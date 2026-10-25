from datetime import timedelta
from io import BytesIO
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from PIL import Image

from .models import AboutPage, Article


def make_test_image(name="robot.png"):
    image_content = BytesIO()
    Image.new("RGB", (8, 8), color="teal").save(image_content, format="PNG")
    return SimpleUploadedFile(
        name,
        image_content.getvalue(),
        content_type="image/png",
    )


class BlogPageTests(TestCase):
    def setUp(self):
        temporary_media = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_media.cleanup)
        self.enterContext(override_settings(MEDIA_ROOT=temporary_media.name))
        AboutPage.objects.update_or_create(
            pk=1,
            defaults={"content": "Presentación de prueba del autor."},
        )

    def create_article(self, **overrides):
        article_data = {
            "title": "Robótica educativa",
            "slug": "robotica-educativa",
            "image": make_test_image(),
            "publication_date": timezone.now(),
            "excerpt": "Un extracto sobre robótica.",
            "content": "## Primeros pasos\n\nContenido del artículo.",
            "author": "Ada",
            "published": True,
        }
        article_data.update(overrides)
        return Article.objects.create(**article_data)

    def test_home_lists_published_articles_newest_first_with_image_and_link(self):
        older = self.create_article(
            title="Primeros pasos",
            slug="primeros-pasos",
            publication_date=timezone.now() - timedelta(days=2),
        )
        newer = self.create_article(
            title="Robots actuales",
            slug="robots-actuales",
            publication_date=timezone.now() - timedelta(days=1),
        )
        draft = self.create_article(
            title="Borrador secreto",
            slug="borrador-secreto",
            published=False,
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Blog de robótica")
        self.assertEqual(list(response.context["articles"]), [newer, older])
        self.assertContains(response, newer.image.url)
        self.assertContains(response, 'alt="Robots actuales"')
        self.assertContains(response, reverse("article-detail", args=[newer.slug]))
        self.assertNotContains(response, draft.title)

    def test_home_shows_informative_empty_state_when_there_are_no_published_articles(self):
        self.create_article(published=False)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Todavía no hay artículos publicados")
        self.assertNotContains(response, "article-grid")
        self.assertNotContains(response, "Robótica educativa")

    def test_article_detail_shows_metadata_image_and_safe_structured_content(self):
        article = self.create_article(
            content="## El primer movimiento\n\nUn párrafo.\n\n<script>alert('x')</script>"
        )

        response = self.client.get(article.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.title)
        self.assertContains(response, article.image.url)
        self.assertContains(response, article.author)
        self.assertContains(response, '<h2>El primer movimiento</h2>', html=True)
        self.assertContains(response, "<p>Un párrafo.</p>", html=True)
        self.assertNotContains(response, "<script>alert")

    def test_unpublished_article_is_not_publicly_accessible(self):
        article = self.create_article(published=False)

        with override_settings(DEBUG=False):
            response = self.client.get(article.get_absolute_url())

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Este robot se ha perdido", status_code=404)

    def test_unknown_article_uses_custom_not_found_page(self):
        with override_settings(DEBUG=False):
            response = self.client.get("/articulos/no-existe/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Este robot se ha perdido", status_code=404)
        self.assertContains(response, reverse("home"), status_code=404)

    def test_about_page_is_editable_and_has_main_navigation(self):
        response = self.client.get(reverse("about"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1 id=\"page-title\">Sobre mí</h1>", html=True)
        self.assertContains(response, "Presentación de prueba del autor.")
        self.assertContains(response, reverse("home"))
        self.assertContains(response, reverse("about"))

    def test_navigation_is_available_from_home_and_article(self):
        article = self.create_article()

        for url in (reverse("home"), article.get_absolute_url()):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, 'aria-label="Navegación principal"')
                self.assertContains(response, reverse("about"))
                self.assertContains(response, reverse("home"))


class EditorialAdminTests(TestCase):
    def setUp(self):
        temporary_media = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_media.cleanup)
        self.enterContext(override_settings(MEDIA_ROOT=temporary_media.name))
        from django.contrib.auth import get_user_model

        self.user = get_user_model().objects.create_superuser(
            username="editor",
            email="editor@example.com",
            password="secure-test-password",
        )
        AboutPage.objects.get_or_create(pk=1, defaults={"content": "Texto inicial."})

    def test_anonymous_visitors_cannot_access_editorial_admin(self):
        response = self.client.get(reverse("admin:blog_article_add"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response.url)
        self.assertEqual(self.client.get("/registro/").status_code, 404)

    def test_editor_can_create_and_update_an_article_with_its_image(self):
        self.client.force_login(self.user)
        add_url = reverse("admin:blog_article_add")
        response = self.client.post(
            add_url,
            {
                "title": "Brazo robótico",
                "slug": "brazo-robotico",
                "image": make_test_image("brazo.png"),
                "publication_date_0": timezone.localtime().strftime("%d/%m/%Y"),
                "publication_date_1": timezone.localtime().strftime("%H:%M:%S"),
                "excerpt": "Un brazo aprende a manipular objetos.",
                "content": "## Precisión\n\nContenido del artículo.",
                "author": "Ada",
                "published": "on",
                "_save": "Guardar",
            },
        )

        self.assertEqual(response.status_code, 302)
        article = Article.objects.get(slug="brazo-robotico")
        self.assertTrue(article.image.storage.exists(article.image.name))
        self.assertContains(
            self.client.get(reverse("home")),
            article.image.url,
        )

        change_url = reverse("admin:blog_article_change", args=[article.pk])
        response = self.client.post(
            change_url,
            {
                "title": "Brazo robótico actualizado",
                "slug": article.slug,
                "publication_date_0": timezone.localtime(
                    article.publication_date
                ).strftime("%d/%m/%Y"),
                "publication_date_1": timezone.localtime(
                    article.publication_date
                ).strftime("%H:%M:%S"),
                "excerpt": article.excerpt,
                "content": article.content,
                "author": article.author,
                "published": "on",
                "_save": "Guardar",
            },
        )

        self.assertEqual(response.status_code, 302)
        article.refresh_from_db()
        self.assertEqual(article.title, "Brazo robótico actualizado")
        self.assertContains(
            self.client.get(article.get_absolute_url()),
            article.image.url,
        )

    def test_editor_can_update_about_page_and_changes_are_public(self):
        self.client.force_login(self.user)
        about_page = AboutPage.objects.get(pk=1)
        response = self.client.post(
            reverse("admin:blog_aboutpage_change", args=[about_page.pk]),
            {"content": "Una presentación actualizada del autor.", "_save": "Guardar"},
        )

        self.assertEqual(response.status_code, 302)
        about_page.refresh_from_db()
        self.assertEqual(about_page.content, "Una presentación actualizada del autor.")
        self.assertContains(
            self.client.get(reverse("about")),
            about_page.content,
        )

    def test_editor_can_unpublish_an_article_and_it_disappears_from_public_pages(self):
        article = Article.objects.create(
            title="Artículo visible",
            slug="articulo-visible",
            image=make_test_image(),
            publication_date=timezone.now(),
            excerpt="Extracto visible.",
            content="Contenido.",
            author="Ada",
            published=True,
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("admin:blog_article_change", args=[article.pk]),
            {
                "title": article.title,
                "slug": article.slug,
                "publication_date_0": timezone.localtime(
                    article.publication_date
                ).strftime("%d/%m/%Y"),
                "publication_date_1": timezone.localtime(
                    article.publication_date
                ).strftime("%H:%M:%S"),
                "excerpt": article.excerpt,
                "content": article.content,
                "author": article.author,
                "_save": "Guardar",
            },
        )

        self.assertEqual(response.status_code, 302)
        article.refresh_from_db()
        self.assertFalse(article.published)
        self.assertNotContains(self.client.get(reverse("home")), article.title)


class DemoContentCommandTests(TestCase):
    def test_demo_command_creates_editable_profile_and_three_articles(self):
        temporary_media = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_media.cleanup)
        with override_settings(MEDIA_ROOT=temporary_media.name):
            from django.core.management import call_command

            call_command("load_demo_content", verbosity=0)

            self.assertEqual(Article.objects.filter(published=True).count(), 3)
            self.assertEqual(AboutPage.objects.count(), 1)
            self.assertEqual(Article.objects.filter(image="").count(), 0)
            for article in Article.objects.filter(published=True):
                self.assertTrue(article.image.storage.exists(article.image.name))
