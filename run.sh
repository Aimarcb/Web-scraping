#!/bin/bash

cd "$(dirname "$0")"

# 2. PANEL DE CONTROL DEL CLIENTE
DESTINO="Praga"
ENTRADA="2026-09-01"
SALIDA="2026-09-15"

echo "========================================================="
echo "🚀 INICIANDO RADAR DE PRECIOS"
echo "📍 Destino: $DESTINO"
echo "📅 Fechas: $ENTRADA -> $SALIDA"
echo "========================================================="

.venv/bin/python src/main.py -d "$DESTINO" -e "$ENTRADA" -s "$SALIDA"

echo "✅ Ejecución finalizada."