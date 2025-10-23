#!/usr/bin/env bash
set -euo pipefail

# Copia imágenes y assets necesarios desde el theme a static/
SRC_THEME="themes/stack/assets/img/mi-logo.jpg"
DEST="static/img/mi-logo.jpg"

mkdir -p "$(dirname "$DEST")"
if [ -f "$SRC_THEME" ]; then
  cp "$SRC_THEME" "$DEST"
  echo "Copiado $SRC_THEME -> $DEST"
else
  echo "Aviso: $SRC_THEME no existe. Verifica la ruta del theme." >&2
  exit 1
fi
