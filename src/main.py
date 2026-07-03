import asyncio
import argparse
import logging
import os
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

# Importaciones de la arquitectura modular
from scraper.engine import fetch_html_booking
from parser.extractor import parse_alojamientos
from models import inicializar_base_datos, Alojamiento
from notifier import enviar_alerta_discord

# Logs configurados para volcar información estructurada tanto en consola como en ficheros log de Linux
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

async def pipeline_principal(destino: str, entrada_str: str, salida_str: str):
    # 1. Validar y transformar cadenas de texto de la CLI a tipos Date nativos de Python
    try:
        fecha_in = datetime.strptime(entrada_str, "%Y-%m-%d").date()
        fecha_out = datetime.strptime(salida_str, "%Y-%m-%d").date()
    except ValueError:
        logging.error("❌ Formato de fecha incorrecto en los argumentos. Debe ser YYYY-MM-DD")
        return

    # 2. Inyección dinámica de parámetros en la URL Maestra
    url = f"https://www.booking.com/searchresults.html?ss={destino}&checkin={entrada_str}&checkout={salida_str}"
    
    # 3. Fase de Extracción (Navegador Stealth Headless)
    html_crudo = await fetch_html_booking(url)
    if not html_crudo:
        logging.error("❌ El motor no pudo extraer el HTML. Abortando flujo.")
        return

    # 4. Fase de Análisis (Parser con BeautifulSoup)
    hoteles_extraidos = parse_alojamientos(html_crudo)
    if not hoteles_extraidos:
        logging.warning("⚠️ No se extrajeron estructuras de alojamiento válidas del HTML.")
        return

    # 5. Fase de Persistencia y Alertas (PostgreSQL con patrón UPSERT)
    logging.info("💾 Conectando a PostgreSQL para procesar transacciones...")
    load_dotenv()
    
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "postgres")
    
    # Protegemos caracteres especiales en la contraseña (como el símbolo "!") antes de armar la URI
    db_pass_segura = urllib.parse.quote_plus(db_pass)
    URL_BD = f"postgresql://{db_user}:{db_pass_segura}@{db_host}:{db_port}/{db_name}"
    
    db = inicializar_base_datos(URL_BD)
    
    try:
        alertas_a_disparar = []
        nuevos_insertados = 0
        actualizados = 0

        for h in hoteles_extraidos:
            # Buscamos si el hotel ya existe para el mismo destino y rango de fechas exacto
            registro_existente = db.query(Alojamiento).filter(
                Alojamiento.titulo == h["titulo"],
                Alojamiento.destino == destino,
                Alojamiento.fecha_entrada == fecha_in,
                Alojamiento.fecha_salida == fecha_out
            ).first()

            if registro_existente:
                # Si existe, evaluamos si el precio actual es menor que el almacenado previamente
                if 0 < h["precio"] < registro_existente.precio:
                    logging.info(f"📉 Oportunidad de mercado detectada: {h['titulo']} bajó de {registro_existente.precio}€ a {h['precio']}€")
                    alertas_a_disparar.append(
                        enviar_alerta_discord(
                            hotel=h["titulo"],
                            precio_anterior=registro_existente.precio,
                            precio_nuevo=h["precio"],
                            destino=destino,
                            entrada=entrada_str,
                            salida=salida_str
                        )
                    )
                
                # Actualizamos los campos de la fila existente (Operación UPDATE implícita del ORM)
                registro_existente.precio = h["precio"]
                registro_existente.fecha_captura = datetime.utcnow()
                actualizados += 1
            else:
                # Si no existe en los registros, creamos la nueva instancia (Operación INSERT)
                alojamiento_db = Alojamiento(
                    destino=destino,
                    titulo=h["titulo"],
                    precio=h["precio"],
                    fecha_entrada=fecha_in,
                    fecha_salida=fecha_out
                )
                db.add(alojamiento_db)
                nuevos_insertados += 1
        
        # Consolidamos la transacción en la base de datos de manera masiva
        db.commit()
        logging.info(f"✨ Transacción completada: {nuevos_insertados} insertados, {actualizados} actualizados.")

        # Si se han encolado alertas de bajadas de precio, las disparamos concurrentemente
        if alertas_a_disparar:
            logging.info(f"📣 Ejecutando concurrencia asíncrona para {len(alertas_a_disparar)} notificaciones...")
            await asyncio.gather(*alertas_a_disparar)
        
    except Exception as e:
        db.rollback()
        logging.error(f"❌ Fallo crítico en el bloque de persistencia: {e}")
    finally:
        # Liberamos la conexión al grupo (pool) obligatoriamente para producción
        db.close()

if __name__ == "__main__":
    # Configuración de argumentos de consola con banderas cortas y descripción explícita
    parser = argparse.ArgumentParser(description="Orquestador táctico de Scraping y Alertas")
    parser.add_argument("-d", "--destino", type=str, required=True, help="Ciudad de destino para el análisis")
    parser.add_argument("-e", "--entrada", type=str, required=True, help="Fecha de check-in (YYYY-MM-DD)")
    parser.add_argument("-s", "--salida", type=str, required=True, help="Fecha de check-out (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    logging.info(f"🏁 Ejecutando pipeline automatizado para {args.destino} ({args.entrada} -> {args.salida})")
    asyncio.run(pipeline_principal(args.destino, args.entrada, args.salida))