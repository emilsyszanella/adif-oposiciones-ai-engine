#!/bin/bash
set -e

# Script de ejecución del agente PDF-to-Markdown
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activar entorno virtual local si existe
if [ -d "$SCRIPT_DIR/.venv" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_BIN="python3"
else
    echo "Error: No se encontró Python 3."
    exit 1
fi

echo "=========================================================="
echo "  Agente de Conversión PDF a Markdown (Lossless Engine)"
echo "=========================================================="
echo "Python interpreter: $PYTHON_BIN"
echo "Directorio de trabajo: $SCRIPT_DIR"
echo ""

$PYTHON_BIN pdf_to_md_agent.py "$@"
