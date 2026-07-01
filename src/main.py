import asyncio
import os
import sys

# Esto asegura que Python encuentre nuestras carpetas internas (src, config, etc.)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importamos las piezas de nuestro motor
from src.scraper.engine import fetch_html
from src.parser.extractor import parse_books
from src.pipeline.cleaner import clean_and_export

from notifier import MockNotifier  # Importamos la clase MockNotifier para usarla en las alertas
from models import inicializar_base_datos, Libro

# Configuración básica
BASE_URL = "https://books.toscrape.com/"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DATABASE_URL = "sqlite:///development.db"  # URL de conexión a la base de datos SQLite
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
        # 1. Conectar a la base de datos y crear la sesión
        session = inicializar_base_datos(DATABASE_URL)

        # 2. Extraer y Parsear
        html = await fetch_html(BASE_URL)
        raw_data = parse_books(html)
        
        # 3. Auditar (El Inspector - Reglas de negocio)
        auditoria_datos(raw_data, alerta_sistema)

        # 4. Persistencia en Base de Datos (Sustituye a clean_and_export)
        print("[Database] Guardando registros en el histórico...")
        for item in raw_data:
            # Creamos un objeto 'Libro' por cada registro parseado
            nuevo_libro = Libro(
                titulo=item.get('titulo'),
                precio=float(item.get('precio', 0)),
                stock=item.get('stock')
            )
            session.add(nuevo_libro) # Lo preparamos en la recámara
            
        session.commit() # Confirmamos la transacción (Se guarda en disco de golpe)
        print(f"✅ Éxito: {len(raw_data)} registros persistidos en la base de datos.")
        session.close()
        
    except Exception as e:
        # Si la web bloquea nuestra IP y el motor falla, enviamos una alerta crítica al sistema
        alerta_sistema.send(f"❌ CAÍDA CRÍTICA DEL SISTEMA: {e}")
        print(f"❌ Error crítico en la ejecución: {e}")

if __name__ == "__main__":
    # Arrancamos el bucle asíncrono
    asyncio.run(main())