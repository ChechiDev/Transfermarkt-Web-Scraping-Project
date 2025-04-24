import requests
from bs4 import BeautifulSoup
from time import sleep
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

    def get_html(self, url: str) -> BeautifulSoup:
        """
        Realiza una solicitud GET y devuelve el contenido HTML cómo un objeto BeautifulSoup.
        Args:
            url (str): URL a la que se desea acceder.
        Returns:
            BeautifulSoup: HTML parsed o None si falla.
        """
        for attempt in range(self.retries):
            try:
                response = requests.get(
                    headers=self.headers,
                    timeout=self.timeout,
                )
                if response.status_code == 200:
                    return BeautifulSoup(response.content, 'html.parser')
                else:
                    print(f"HTTP: {response.status_code} para {url}")
            except requests.RequestException as e:
                print(f"Error: Fallo en intento {attempt + 1}/{self.retries} para la url: {url}")

            sleep(self.delay) # Espera 1 segundo entre el siguiente reintento.

        print(f"Error: No se puede acceder a la URL: {url}")
        return None