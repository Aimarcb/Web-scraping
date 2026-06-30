import asyncio
import os
import sys

# Esto asegura que Python encuentre nuestras carpetas internas (src, config, etc.)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importamos las piezas de nuestro motor
from src.scraper.engine import fetch_html
from src.parser.extractor import parse_books
from src.pipeline.cleaner import clean_and_export

# Configuración básica (En un proyecto más grande esto iría en config/settings.py)
BASE_URL = "https://books.toscrape.com/"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(DATA_PROCESSED_DIR, exist_ok=True) # Crea la carpeta si no existe

async def main():
    print("🚀 INICIANDO PIPELINE DE EXTRACCIÓN AVANZADA...")
    
    try:
        # 1. Extraer (El Motor)
        html = await fetch_html(BASE_URL)
        
        # 2. Parsear (El Cirujano)
        raw_data = parse_books(html)
        
        # 3. Limpiar y Guardar (La Refinería)
        output_file = os.path.join(DATA_PROCESSED_DIR, "books_dataset_clean.csv")
        clean_and_export(raw_data, output_file)
        
    except Exception as e:
        print(f"❌ Error crítico en la ejecución: {e}")

if __name__ == "__main__":
    # Arrancamos el bucle asíncrono
    asyncio.run(main())