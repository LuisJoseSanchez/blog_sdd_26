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

- Django para el backend y el renderizado de páginas en el servidor.
- Modelos y migraciones Django para persistir los contenidos.
- Plantillas HTML semánticas y CSS adaptable.
- SQLite para el desarrollo inicial; la base de datos de producción se decidirá según el entorno de despliegue.

## Fuera del alcance inicial

No se contemplan cuentas para lectores, comentarios, suscripciones, buscador, interacción social ni flujos editoriales avanzados.

## Documentación

- [Briefing](./briefing.md)
- [Requisitos del producto (PRD)](./PRD.md)
- [Visión del producto](./spec/vision.md)
- [Alcance](./spec/scope.md)
- [Criterios de aceptación](./spec/acceptance_criteria.md)

> El repositorio recoge la documentación y definición del producto. La estructura técnica y la implementación de la aplicación se concretarán durante el desarrollo.