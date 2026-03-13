#!/bin/bash
# Script para poder ejecutar los notebooks en WSL cuando el Python del sistema
# no permite instalar paquetes. Crea un venv y registra el kernel Jupyter.

set -e
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV_DIR="$REPO_ROOT/.venv_wsl"

echo "1. Instalando python3.12-venv (necesita sudo)..."
sudo apt update -qq && sudo apt install -y python3.12-venv

echo "2. Creando entorno virtual en $VENV_DIR..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install ipykernel pandas==2.2.3 numpy==1.26.4 -q

echo "3. Registrando kernel Jupyter 'Python 3.12 (fdd_p26)'..."
"$VENV_DIR/bin/python" -m ipykernel install --user --name fdd_p26 --display-name "Python 3.12 (fdd_p26)"

echo ""
echo "Listo. En el notebook:"
echo "  - Pulsa en el selector de kernel (arriba a la derecha, donde pone 'Python 3.12.3')"
echo "  - Elige 'Python 3.12 (fdd_p26)'"
echo "  - Vuelve a ejecutar la celda."
