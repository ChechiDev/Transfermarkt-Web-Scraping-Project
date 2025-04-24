import requests
from bs4 import BeautifulSoup
from config import headers


class HTTPClient:
    """
    Client HTTP reutilizable para descargar y parsear HTML de forma segura.
    """
    def __init__(self, base_headers = None, timeout = 5, retries = 3, delay = 1):
        self.headers = base_headers or headers
        self.timeout = timeout # Tiempo de espera para la conexión
        self.retries = retries # Número de reintentos
        self.delay = delay # Segundos entre reintentos
        self.url_manager = None
