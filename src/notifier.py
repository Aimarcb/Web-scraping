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
        logging.info(f"🚨 ALERTA: {message}")

class TelegramNotifier(NotifierInterface):
    """Plantilla para el futuro."""
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        
    def send(self, message: str):
        # Aquí irá el código de Telegram cuando meta el bot
        pass