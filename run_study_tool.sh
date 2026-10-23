#!/bin/bash
set -e

# Launcher para la Herramienta Didáctica de Oposiciones Adif
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d "$SCRIPT_DIR/.venv" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_BIN="python3"
else
    echo "Error: No se encontró Python 3."
    exit 1
fi

echo "=================================================================="
echo "  ADIF OPOSICIONES PREP - HERRAMIENTA DIDÁCTICA INTERACTIVA"
echo "=================================================================="
echo "Iniciando servidor local y abriendo en tu navegador predeterminado..."
echo ""

$PYTHON_BIN adif_exam_agent.py --serve 8080
