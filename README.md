# Sitio Hugo — Serj AI

Pequeñas instrucciones para construir y desplegar el sitio Hugo.

Requisitos
- Hugo Extended (para procesado SCSS): https://gohugo.io/getting-started/install/

Build local

```bash
hugo # genera el sitio en ./public
hugo server -D # servidor local con live-reload, incluye drafts
```

Despliegue
- Para GitHub Pages: este repo incluye un workflow de GitHub Actions que construye y publica en la rama `gh-pages`.
- Para Netlify: incluir `netlify.toml` y configurar el build command `hugo` y publish directory `public`.

Copiar assets del theme (opcional)

```bash
./scripts/copy-assets.sh
```

Contacto
- https://github.com/serjaii
