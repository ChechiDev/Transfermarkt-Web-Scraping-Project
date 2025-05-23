import requests
from bs4 import BeautifulSoup
from time import sleep
import validators
from config.headers import get_headers
from config.exceptions import (
    logging,
    HTTPConnectionError,
    HTTPTimeoutError,
    HTTPClientError,
    HTTPResponseError
)

class HTTPClient:
    def __init__(
            self,
            base_headers = None,
            timeout = 10,
            retries = 10,
            delay = 6
        ):

        self.headers = base_headers
        self.timeout = timeout # Tiempo de espera para la conexión
        self.retries = retries # Número de reintentos
        self.delay = delay # Segundos entre reintentos
        self.url_manager = None # Inicializa el gestor de URL (opcional)


    def set_url_manager(self, url_manager):
        """
        Asigna un gestor de URL al cliente HTTP.
        """
        from scraping.ws_urls import URLManager
        from scraping.ws_engine import ScrapingEngine

        if not isinstance(url_manager, URLManager):
            raise ValueError("El gestor de URL debe ser una instancia de URLManager.")

        self.url_manager = url_manager


    def make_request(self, url, method="GET", **kwargs):
        if not validators.url(url):
            raise ValueError(f"URL no válida: {url}")

        for attempt in range(self.retries):
            try:
                # Headers dinámicos para cada solicitud
                self.headers = get_headers()

                # Realizamos la solicitud HTTP
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    timeout=self.timeout,
                    **kwargs,
                )

                if response.status_code == 200:
                    return response
                else:
                    logging.warning(f"HTTP: {response.status_code} para {url}")

            except requests.Timeout:
                # logging.warning(f"Timeout: Fallo en intento {attempt + 1}/{self.retries} para la url: {url}")
                logging.warning(f"Timeout: Fallo en intento {attempt + 1}/{self.retries}")

                if attempt == self.retries - 1:
                    raise HTTPTimeoutError(f"Error: Timeout al acceder a la URL {url} después de {self.retries} intentos.")

            except requests.RequestException as e:
                # logging.warning(f"Error: Fallo en intento {attempt + 1}/{self.retries} para la url: {url}. \nDetalle: {e}")
                logging.warning(f"Timeout: Fallo en intento {attempt + 1}/{self.retries}")

                if attempt == self.retries - 1:
                    raise HTTPConnectionError(f"Error: No se puede acceder a la URL {url} después de {self.retries} intentos.")

            # Pausamos antes de reintento
            sleep(self.delay * 2)

        raise Exception(f"Error: No se puede acceder a la URL {url} después de {self.retries} intentos.")


    def retry_request(self, func, *args, **kwargs):
        """
        Método para realizar una solicitud HTTP con reintentos.
        """
        for attempt in range(self.retries):
            try:
                return func(*args, **kwargs)

            except requests.RequestException as e:
                logging.warning(f"Intento {attempt + 1}/{self.retries} fallido: {e}")
                sleep(self.delay * 2)

        raise Exception(f"Error: No se puede completar la solicitud después de {self.retries} intentos.")


    def get_html(self, url: str, **kwargs):
        """
        Realiza una solicitud GET y devuelve el contenido HTML de la página como un objeto BeautifulSoup.
        """
        if not validators.url(url):
            logging.error(f"URL no válida: {url}")
            return None

        try:
            # Realizar la solicitud HTTP
            response = self.make_request(url, **kwargs)
            return BeautifulSoup(response.content, "html.parser")

        except requests.RequestException as e:
            logging.error(f"Error de conexión al obtener el HTML de la URL: {url}. \nDetalle: {e}")

        except Exception as e:
            logging.error(f"Error al obtener el HTML de la URL: {url}. \nDetalle: {e}")

        return None


    def get_json(self, url, **kwargs):
        try:
            response = self.make_request(url, **kwargs)
            return response.json()

        except Exception as e:
            logging.error(f"Error al obtener el JSON de la URL: {url}: {e}")

        return None