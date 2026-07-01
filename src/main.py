import asyncio
import os
import sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

env_path = os.path.join(BASE_DIR, ".env")

# Cargamos las variables de entorno desde el archivo .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

if not DB_USER:
    raise ValueError("❌ CRÍTICO: No se encontraron variables de entorno. Revisa el archivo .env")

# Cadena de conexión para PostgreSQL en el servidor Ubuntu
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Importamos las piezas de nuestro motor
from src.scraper.engine import fetch_html
from src.parser.extractor import parse_books
from src.pipeline.cleaner import clean_and_export

from notifier import MockNotifier  # Importamos la clase MockNotifier para usarla en las alertas
from models import inicializar_base_datos, Libro

# Configuración básica
BASE_URL = "https://books.toscrape.com/"

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
        registros_guardados = 0
        for item in raw_data:
            print(f"DEBUG - Diccionario extraído: {item}")

            titulo_extraido = item.get('title')
            precio_limpio = item.get('price', '0').replace('£', '').strip()
            stock_extraido = item.get('stock')

            if not titulo_extraido:
                print("⚠️ [Database] Registro sin título encontrado. Se omite.")
                continue

            libro_existente = session.query(Libro).filter_by(titulo=titulo_extraido).first()
            if libro_existente:
                print(f"[Database] El libro '{titulo_extraido}' ya existe en la base de datos. Se actualiza.")
                libro_existente.precio = precio_limpio if precio_limpio else 0.0
                libro_existente.stock = stock_extraido
            else:
                print(f"[Database] Nuevo libro detectado: '{titulo_extraido}'. Se agrega a la base de datos.")
                nuevo_libro = Libro(
                    titulo=titulo_extraido,
                    precio=float(precio_limpio) if precio_limpio else 0.0,
                    stock=stock_extraido
                )
                session.add(nuevo_libro) # Lo preparamos en la recámara

            registros_guardados += 1
            
        session.commit() # Confirmamos la transacción (Se guarda en disco de golpe)
        print(f"✅ Éxito: {registros_guardados} de {len(raw_data)} registros persistidos en la base de datos.")
        session.close()
        
    except Exception as e:
        # Si la web bloquea nuestra IP y el motor falla, enviamos una alerta crítica al sistema
        alerta_sistema.send(f"❌ CAÍDA CRÍTICA DEL SISTEMA: {e}")
        print(f"❌ Error crítico en la ejecución: {e}")

if __name__ == "__main__":
    # Arrancamos el bucle asíncrono
    asyncio.run(main())