#!/bin/bash
echo "Iniciando el script de scraping..."

# Comprobamos si el entorno virtual existe antes de intentar activarlo
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "[*] Entorno virtual activado."
else
    echo "❌ Error: No se encontró el entorno virtual (.venv)."
    exit 1
fi

echo "[*] Ejecutando el motor de extracción..."
python src/main.py

echo "Proceso de scraping finalizado."