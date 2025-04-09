from config.headers import headers
import requests
from bs4 import BeautifulSoup
import time
import os

# Clase para manejar las solicitudes HTTP.
class HttpClient:
    def __init__(self, headers, sleep_time=1):
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.sleep_time = sleep_time

    # Realiza una solicitud HTTP y devuelve el contenido HTML.
    def get_html(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            time.sleep(self.sleep_time)
            return BeautifulSoup(response.content, "html.parser")
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error HTTP {response.status_code} al solicitar {url}: {e}")
            return None
        except requests.RequestException as e:
            print(f"❌ Error al solicitar {url}: {e}")
            return None

# Clase base para manejar el scraping.
# Esta clase se encarga de construir las URLs y realizar el scraping.
class ScrapeBase:
    def __init__(self, http_client):
        self.http_client = http_client
        self.base_url = {}

    # Añader una URL al diccionario base_url.
    # Las URLs se pueden definir en un archivo .env o directamente en el código.
    def add_url(self, name, url):
        self.base_url[name] = url

    # Carga automáticamente todas las URLs desde el archivo .env.
    # Las URLs deben estar definidas con el prefijo "URL_".
    def get_url_from_env(self):
        for key, value in os.environ.items():
            if key.startswith("URL_"):
                self.add_url(key.lower(), value)

    # Construye una URL dinámica, reemplazando variables dinámicas.
    # Las variables deben estar definidas en la URL con el formato {variable}.
    def build_url(self, name, **kwargs):
        url = self.base_url.get(name)
        if not url:
            raise ValueError(f"No existe la URL para '{name}'")
        try:
            final_url = url.format(**kwargs)
            return final_url  # Eliminamos el print para no mostrar la URL generada
        except KeyError as e:
            raise ValueError(f"Falta variable para construir la URL: {e}")

    # Realiza el scraping para una URL específica.
    # Esta función utiliza el cliente HTTP para obtener el HTML de la URL construida.
    def scrape(self, name, **kwargs):
        url = self.build_url(name, **kwargs)
        return self.http_client.get_html(url)
