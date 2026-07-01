import os
import httpx
import logging

logging.basicConfig(level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

class NotifierInterface:
    """Clase base. Obliga a todos los hijos a tener un método send()"""
    def send(self, message: str):
        raise NotImplementedError("Debe implementarse en la clase hija")

class MockNotifier(NotifierInterface):
    """El Simulador. Imprime en terminal."""
    def send(self, message: str):
        logging.info(f"🚨 [MOCK ALERTA]: {message}")

class DiscordNotifier(NotifierInterface):
    """Integración real con Webhooks de Discord para producción."""
    def __init__(self):
        # Leemos el secreto directamente aquí para no ensuciar el main
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        
        if not self.webhook_url:
            logging.error("❌ CRÍTICO: No se encontró DISCORD_WEBHOOK_URL en el .env")

    def send(self, message: str):
        if not self.webhook_url:
            return
            
        try:
            # Petición POST síncrona a la API de Discord
            response = httpx.post(
                self.webhook_url, 
                json={"content": f"🚨 **ALERTA SCRAPER:**\n{message}"}
            )
            response.raise_for_status() # Lanza excepción si Discord rechaza la petición
            logging.info("👾 Alerta de sistema enviada a Discord con éxito.")
        except Exception as e:
            logging.error(f"Fallo al comunicarse con los servidores de Discord: {e}")