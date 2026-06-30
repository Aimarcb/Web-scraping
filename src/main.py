import asyncio
import os
import sys

# Esto asegura que Python encuentre nuestras carpetas internas (src, config, etc.)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importamos las piezas de nuestro motor
from src.scraper.engine import fetch_html
from src.parser.extractor import parse_books
from src.pipeline.cleaner import clean_and_export

import notifier  # Importamos el módulo de notificación
from notifier import MockNotifier  # Importamos la clase MockNotifier para usarla en las alertas

# Configuración básica
BASE_URL = "https://books.toscrape.com/"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(DATA_PROCESSED_DIR, exist_ok=True) # Crea la carpeta si no existe

def auditoria_datos(raw_data, notifier):
    """
    Evalúa las reglas de negocio del cliente y dispara alertas si es necesario.
    """
    for libro in raw_data:
        # Buscamos si en el texto crudo extraído aparece que no hay stock
        stock_text = str(libro.get('stock', '')).lower()
        if "out of stock" in stock_text:
            mensaje = f"⚠️ ALERTA DE STOCK: El libro '{libro.get('titulo', 'Desconocido')}' se ha agotado."
            notifier.send(mensaje)

async def main():
    print("🚀 INICIANDO PIPELINE DE EXTRACCIÓN AVANZADA...")
    
    # 0. Instanciamos las dependencias (El Notificador)
    # Cuando Telegram funcione, aquí solo cambiaremos MockNotifier() por TelegramNotifier(token, id)
    alerta_sistema = MockNotifier()

    try:
        # 1. Extraer (El Motor)
        html = await fetch_html(BASE_URL)
        
        # 2. Parsear (El Cirujano)
        raw_data = parse_books(html)
        
        # 3. Auditar (El Inspector - Reglas de negocio)
        auditoria_datos(raw_data, alerta_sistema)

        # 4. Limpiar y Guardar (La Refinería)
        output_file = os.path.join(DATA_PROCESSED_DIR, "books_dataset_clean.csv")
        clean_and_export(raw_data, output_file)
        
    except Exception as e:
        # Si la web bloquea nuestra IP y el motor falla, enviamos una alerta crítica al sistema
        alerta_sistema.send(f"❌ CAÍDA CRÍTICA DEL SISTEMA: {e}")
        print(f"❌ Error crítico en la ejecución: {e}")

if __name__ == "__main__":
    # Arrancamos el bucle asíncrono
    asyncio.run(main())