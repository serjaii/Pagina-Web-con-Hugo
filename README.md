# Sitio Hugo — SerjAi

Pequeñas instrucciones para construir y desplegar el sitio Hugo.

Requisitos
- Hugo Extended (para procesado SCSS): https://gohugo.io/getting-started/install/

Build local

```bash
hugo # genera el sitio en ./public
hugo server -D # servidor local con live-reload, incluye drafts
````markdown
# Sitio Hugo — SerjAi

Pequeñas instrucciones para construir y desplegar el sitio Hugo.

Requisitos
- Hugo Extended (para procesado SCSS): https://gohugo.io/getting-started/install/

Build local

```bash
hugo # genera el sitio en ./public (o usa el wrapper ./scripts/hugo para publicar automáticamente)
hugo server -D # servidor local con live-reload, incluye drafts
```

Publicar automáticamente la carpeta public/ en el repo estático

Este repositorio excluye `public/` del control de versiones. Si quieres que la carpeta `public/` se publique automáticamente
en `https://github.com/serjaii/Codigo-html-de-mi-pagina` al ejecutar la build, usa el wrapper incluido:

```bash
# Ejecuta Hugo y luego empuja ./public a https://github.com/serjaii/Codigo-html-de-mi-pagina
./scripts/hugo
```

El wrapper acepta las siguientes variables de entorno (opcional):

- PUBLIC_REPO: repositorio remoto para publicar (por defecto https://github.com/serjaii/Codigo-html-de-mi-pagina)
- PUBLIC_BRANCH: rama en el repo remoto (por defecto main)
- GITHUB_TOKEN: token para autenticación (si el repo es privado)
- GIT_AUTHOR_NAME / GIT_AUTHOR_EMAIL: autor del commit en public/

Despliegue con GitHub Actions
Este repo incluye un workflow que construye el sitio y lo publica automáticamente en GitHub Pages usando la rama `gh-pages` cuando hay cambios en `main`.

Copiar assets del theme (opcional)

```bash
./scripts/copy-assets.sh
```

Contacto
- https://github.com/serjaii

````
