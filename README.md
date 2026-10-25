# Blog de robótica

Proyecto para crear un blog en español dedicado a la robótica, pensado para que sus visitantes descubran artículos recientes, los lean con comodidad y conozcan al autor.

## Descripción

El sitio ofrecerá una portada con los artículos publicados, una página para leer cada artículo completo y una sección «Sobre mí». La experiencia priorizará el contenido: navegación sencilla, diseño adaptable a móviles y ordenadores, y una estructura accesible y legible.

El editor podrá mantener los artículos y la presentación del autor desde el panel administrativo estándar de Django, sin modificar manualmente las plantillas. El contenido inicial será de ejemplo y podrá sustituirse o retirarse.

## Funcionalidades previstas

- Listado de artículos publicados en orden cronológico, con título, imagen, fecha y extracto.
- Página individual de cada artículo con su contenido y datos de publicación.
- Página «Sobre mí», editable y accesible desde la navegación principal.
- Navegación básica que funciona sin JavaScript.
- Página 404 propia para artículos inexistentes.
- Gestión de artículos y de la presentación del autor mediante Django Admin, restringida a usuarios autorizados.

## Tecnologías previstas

- Python 3.12 y Django 5.2 LTS para el backend y el renderizado de páginas en el servidor.
- Modelos y migraciones Django para persistir los contenidos.
- Plantillas HTML semánticas y CSS adaptable.
- SQLite para el desarrollo inicial; la base de datos de producción se decidirá según el entorno de despliegue.
- Código Django, dependencias y `manage.py` organizados en `src/`; la documentación y la configuración general del repositorio permanecen en la raíz.

## Puesta en marcha

Activa el entorno virtual, instala las dependencias y prepara la base de datos:

```bash
source .venv/bin/activate
python -m pip install -r src/requirements.txt
python src/manage.py migrate
python src/manage.py load_demo_content
python src/manage.py runserver
```

El servidor de desarrollo estará disponible en <http://127.0.0.1:8000/>.

El panel administrativo se encuentra en `/admin/`; para crear un usuario administrador, ejecuta:

```bash
python src/manage.py createsuperuser
```

No hay un usuario ni una clave predeterminados para el panel. Inicia sesión con las credenciales del superusuario que hayas creado.

En producción, configura `PYTHONPATH=src`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` y `DJANGO_DEBUG=False`, y despliega detrás de HTTPS. No reutilices la clave de desarrollo.

## Fuera del alcance inicial

No se contemplan cuentas para lectores, comentarios, suscripciones, buscador, interacción social ni flujos editoriales avanzados.

## Documentación

- [Briefing](./briefing.md)
- [Requisitos del producto (PRD)](./PRD.md)
- [Visión del producto](./spec/vision.md)
- [Alcance](./spec/scope.md)
- [Criterios de aceptación](./spec/acceptance_criteria.md)

> El proyecto Django y la aplicación `blog` están en `src/`. `load_demo_content` añade artículos de ejemplo y genera imágenes localmente para que puedan editarse o retirarse desde Django Admin.