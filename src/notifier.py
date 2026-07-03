import aiohttp
import logging
import os
from datetime import datetime, timezone

async def enviar_alerta_discord(hotel: str, precio_anterior: float, precio_nuevo: float, destino: str, entrada: str, salida: str):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        logging.warning("⚠️ [Notifier] No se encontró DISCORD_WEBHOOK_URL en el archivo .env.")
        return

    ahorro = precio_anterior - precio_nuevo
    
    payload = {
        "username": "Booking Radar Bot",
        "avatar_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=120&h=120&q=80",
        "embeds": [{
            "title": f"📉 ¡BAJADA DE PRECIO EN {destino.upper()}! 🚨",
            "description": f"El sistema ha detectado una reducción de tarifa para tu estancia en **{hotel}**.",
            "color": 3066993,  
            "fields": [
                {"name": "📅 Período de Estancia", "value": f"Del `{entrada}` al `{salida}`", "inline": False},
                {"name": "💰 Precio Anterior", "value": f"{precio_anterior:.2f} €", "inline": True},
                {"name": "🎉 Precio Nuevo", "value": f"**{precio_nuevo:.2f} €**", "inline": True},
                {"name": "📉 Ahorro Directo", "value": f"{ahorro:.2f} €"}
            ]
        }]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status == 204:
                    logging.info(f"✅ [Notifier] Alerta enviada exitosamente a Discord para {hotel}")
                else:
                    logging.error(f"❌ [Notifier] Error al enviar notificación a Discord: {response.status}")
    except Exception as e:
        logging.error(f"❌ [Notifier] Excepción al enviar alerta: {e}")