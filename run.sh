#!/bin/bash

cd "$(dirname "$0")"

# 2. PANEL DE CONTROL DEL CLIENTE
CITY="Prague"
CHECKIN="2026-09-01"
CHECKOUT="2026-09-15"

echo "========================================================="
echo "🚀 INICIANDO RADAR DE PRECIOS"
echo "📍 Destino: $CITY"
echo "📅 Fechas: $CHECKIN -> $CHECKOUT"
echo "========================================================="

.venv/bin/python src/main.py --city "$CITY" --checkin "$CHECKIN" --checkout "$CHECKOUT"

echo "✅ Ejecución finalizada."