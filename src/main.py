import asyncio
import argparse
import logging
import os
from datetime import datetime

from scraper.engine import fetch_html_booking
from parser.extractor import parse_alojamientos

from models import inicializar_base_datos, Alojamiento
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("DB_USER", "postgres")
db_pass = os.getenv("DB_PASSWORD", "postgres")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "postgres")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

async def pipeline_principal(destino: str, entrada_str: str, salida_str: str):
    # 1. Validar y convertir fechas de texto a objetos datetime de Python
    try:
        fecha_in = datetime.strptime(entrada_str, "%Y-%m-%d").date()
        fecha_out = datetime.strptime(salida_str, "%Y-%m-%d").date()
    except ValueError:
        logging.error("❌ Formato de fecha incorrecto. Debe ser YYYY-MM-DD")
        return

    # 2. Construir la URL Maestra para el motor
    url = f"https://www.booking.com/searchresults.html?ss={destino}&checkin={entrada_str}&checkout={salida_str}"
    
    # 3. EJECUCIÓN DEL MOTOR (Fase de Red)
    html_crudo = await fetch_html_booking(url)
    
    if not html_crudo:
        logging.error("❌ El motor no pudo extraer el HTML. Abortando pipeline.")
        return

    # 4. EJECUCIÓN DEL PARSER (Fase de Análisis)
    hoteles_extraidos = parse_alojamientos(html_crudo)
    
    if not hoteles_extraidos:
        logging.warning("⚠️ No se extrajeron alojamientos del HTML.")
        return

    # 5. PERSISTENCIA (Fase de Base de Datos)
    logging.info("💾 Conectando a PostgreSQL para guardar los resultados...")
    
    URL_BD = os.getenv(
        "DATABASE_URL", 
        f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )
    
    # Inicializamos la conexión y obtenemos una sesión limpia
    db = inicializar_base_datos(URL_BD)
    
    try:
        nuevos_registros = []
        for h in hoteles_extraidos:
            # Instanciamos el modelo ORM mapeando los datos limpios
            alojamiento_db = Alojamiento(
                destino=destino,
                titulo=h["titulo"],
                precio=h["precio"],
                fecha_entrada=fecha_in,
                fecha_salida=fecha_out
            )
            nuevos_registros.append(alojamiento_db)
        
        db.add_all(nuevos_registros)
        db.commit()
        logging.info(f"✨ Éxito: Guardados {len(nuevos_registros)} alojamientos en la base de datos.")
        
    except Exception as e:
        db.rollback()
        logging.error(f"❌ Error al guardar en la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orquestador del Scraper de Alojamientos")
    parser.add_argument("-d", "--destino", type=str, required=True, help="Ciudad destino")
    parser.add_argument("-e", "--entrada", type=str, required=True, help="Fecha entrada YYYY-MM-DD")
    parser.add_argument("-s", "--salida", type=str, required=True, help="Fecha salida YYYY-MM-DD")
    
    args = parser.parse_args()
    
    logging.info(f"🏁 Iniciando proceso para {args.destino} ({args.entrada} / {args.salida})")
    asyncio.run(pipeline_principal(args.destino, args.entrada, args.salida))