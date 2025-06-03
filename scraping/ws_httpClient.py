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
    """
    Cliente HTTP para gestionar solicitudes web con reintentos, validación y manejo de errores.
    Permite obtener HTML y JSON de páginas web, así como asignar un gestor de URLs.
    """
    def __init__(
            self,
            base_headers = None,
            timeout = 10,
            retries = 10,
            delay = 6
        ):
        """
        Inicializa el cliente HTTP con parámetros de conexión y reintentos.

        Args:
            base_headers (dict, opcional): Cabeceras base para las solicitudes.
            timeout (int, opcional): Tiempo de espera para la conexión.
            retries (int, opcional): Número de reintentos.
            delay (int, opcional): Segundos entre reintentos.
        """
        self.headers = base_headers
        self.timeout = timeout # Tiempo de espera para la conexión
        self.retries = retries # Número de reintentos
        self.delay = delay # Segundos entre reintentos
        self.url_manager = None # Inicializa el gestor de URL (opcional)


    def set_url_manager(self, url_manager):
        """
        Asigna un gestor de URL al cliente HTTP.

        Args:
            url_manager: Instancia de URLManager.
        """
        from scraping.ws_urls import URLManager
        from scraping.ws_engine import ScrapingEngine

        if not isinstance(url_manager, URLManager):
            raise ValueError("El gestor de URL debe ser una instancia de URLManager.")

        self.url_manager = url_manager


    def make_request(self, url, method="GET", **kwargs):
        """
        Realiza una solicitud HTTP con reintentos y manejo de errores.

        Args:
            url (str): URL a la que se realiza la solicitud.
            method (str): Método HTTP (por defecto "GET").
            **kwargs: Argumentos adicionales para requests.

        Return:
            Response: Objeto de respuesta de requests si es exitosa.
        """
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
                logging.warning(f"Timeout: Fallo en intento {attempt + 1}/{self.retries}")

                if attempt == self.retries - 1:
                    raise HTTPTimeoutError(f"Error: Timeout al acceder a la URL {url} después de {self.retries} intentos.")

            except requests.RequestException as e:
                logging.warning(f"Timeout: Fallo en intento {attempt + 1}/{self.retries}")

                if attempt == self.retries - 1:
                    raise HTTPConnectionError(f"Error: No se puede acceder a la URL {url} después de {self.retries} intentos.")

            # Pausamos antes de reintento
            sleep(self.delay * 2)

        raise Exception(f"Error: No se puede acceder a la URL {url} después de {self.retries} intentos.")


    def retry_request(self, func, *args, **kwargs):
        """
        Método para realizar una solicitud HTTP con reintentos.

        Args:
            func: Función a ejecutar.
            *args: Argumentos posicionales para la función.
            **kwargs: Argumentos adicionales para la función.

        Return:
            Resultado de la función si es exitosa.
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

        Args:
            url (str): URL de la página a obtener.

        Return:
            BeautifulSoup | None: Objeto BeautifulSoup con el HTML o None si falla.
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
        """
        Realiza una solicitud GET y devuelve la respuesta en formato JSON.

        Args:
            url (str): URL de la API o recurso JSON.

        Return:
            dict | None: Diccionario con la respuesta JSON o None si falla.
        """
        try:
            response = self.make_request(url, **kwargs)
            return response.json()

        except Exception as e:
            logging.error(f"Error al obtener el JSON de la URL: {url}: {e}")

        return None