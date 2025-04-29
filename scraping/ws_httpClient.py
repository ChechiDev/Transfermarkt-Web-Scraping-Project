import requests
from bs4 import BeautifulSoup
from time import sleep
import validators
from config.headers import headers
from config.exceptions import (
    logging,
    HTTPClientError,
    HTTPConnectionError,
    HTTPTimeoutError,
    HTTPResponseError
)

class HTTPClient:
    """
    Client HTTP reutilizable para descargar y parsear HTML de forma segura.
    """
    def __init__(self, base_headers = None, timeout = 5, retries = 3, delay = 1):
        """
        Constructor del cliente HTTP.
        Args:
            base_headers (dict, opcional): Headers HTTP predeterminados para las solicitudes.
            timeout (int, opcional): Tiempo máximo de espera para una solicitud (en segundos).
            retries (int, opcional): Número de intentos en caso de fallo.
            delay (int, opcional): Tiempo de espera entre intentos (en segundos).
        """

        self.headers = base_headers or headers
        self.timeout = timeout # Tiempo de espera para la conexión
        self.retries = retries # Número de reintentos
        self.delay = delay # Segundos entre reintentos
        self.url_manager = None # Inicializa el gestor de URL (opcional)


    def set_url_manager(self, url_manager):
        """
        Asigna un gestor de URL al cliente HTTP.
        Args:
            url_manager (URLManager): Instancia del gestor de URL.
        """
        from scraping.ws_urls import URLManager
        from scraping.ws_engine import ScrapingEngine

        if not isinstance(url_manager, URLManager):
            raise ValueError("El gestor de URL debe ser una instancia de URLManager.")

        self.url_manager = url_manager


    def make_request(self, url, method = "GET", **kwargs):
        """
        Método para realizar una solicitud HTTP con reintentos.
        Args:
            method (str): Método HTTP a utilizar (GET, POST, etc.).
            url (str): URL a la que se desea acceder.
            **Kwargs: Parámetros adicionales para la solicitud.
        Returns:
            request.Response: Respuesta de la solicitud HTTP, si es exitosa.
        """
        if not validators.url(url):
            raise ValueError(f"URL no válida: {url}")

        for attempt in range(self.retries):
            try:
                # Realizamos la solicitud GET a la URL con el método especificado:
                response = requests.request(
                    method = method, # Agregamos method para más flexibilidad.
                    url = url,
                    headers = self.headers,
                    timeout = self.timeout,
                    **kwargs, # Pasamos los parámetros adicionales
                )
                # Verificamos si la respuesta es exitosa (código 200):
                if response.status_code == 200:
                    return response
                else:
                    logging.warning(f"HTTP: {response.status_code} para {url}")

            except requests.Timeout:
                logging.warning(f"Timeout: Fallo en intento {attempt + 1}/{self.retries} para la url: {url}")
                if attempt == self.retries - 1:
                    raise HTTPTimeoutError(f"Error: Timeout al acceder a la URL {url} después de {self.retries} intentos.")

            except requests.RequestException as e:
                logging.warning(f"Error: Fallo en intento {attempt + 1}/{self.retries} para la url: {url}. \nDetalle: {e}")
                if attempt == self.retries - 1:
                    raise HTTPConnectionError(f"Error: No se puede acceder a la URL {url} después de {self.retries} intentos.")

            # Pausamos antes de reintento:
            sleep(self.delay)

        # Si todos los intentos fallan, lanzamos una excepción:
        raise Exception(f"Error: No se puede acceder a la URL {url} después de {self.retries} intentos.")


    def retry_request(self, func, *args, **kwargs):
        """
        Método para realizar una solicitud HTTP con reintentos.
        Args:
            func (callable): Función a ejecutar (por ejemplo, make_request).
            *args: Argumentos posicionales para la función.
            **kwargs: Argumentos de palabra clave para la función.
        Returns:
            request.Response: Respuesta de la solicitud HTTP, si es exitosa.
        """
        for attempt in range(self.retries):
            try:
                return func(*args, **kwargs)

            except requests.RequestException as e:
                logging.warning(f"Intento {attempt + 1}/{self.retries} fallido: {e}")
                sleep(self.delay)  # Espera antes de reintentar

        raise Exception(f"Error: No se puede completar la solicitud después de {self.retries} intentos.")


    def get_html(self, url: str, **kwargs):
        """
        Realiza una solicitud GET y devuelve el contenido HTML de la página como un objeto BeautifulSoup.

        Args:
            url (str): URL de la página a descargar.
            **kwargs: Parámetros adicionales para la solicitud GET.

        Returns:
            BeautifulSoup: Objeto BeautifulSoup con el contenido HTML si la solicitud es exitosa.
            None: Si la solicitud falla o la URL es inválida.
        """

        # Validamos la URL antes de realizar la solicitud:
        if not validators.url(url):
            logging.error(f"URL no válida: {url}")
            return None

        # Controlamos el tiempo de espera y los reintentos:
        # Si la URL no es válida, lanzamos una excepción:
        try:
            response = self.make_request(url, **kwargs)
            return BeautifulSoup(response.content, "html.parser")

        # Manejo de excepciones para errores de conexión o tiempo de espera:
        except requests.RequestException as e:
            logging.error(f"Error de conexión al obtener el HTML de la URL: {url}. \nDetalle: {e}")

        except Exception as e:
            logging.error(f"Error al obtener el HTML de la URL: {url}. \nDetalle: {e}")

        return None


    def get_json(self, url, **kwargs):
        """
        Realiza una solicitud GET y devuelve el contenido JSON de la página.
        Args:
            url (str): URL de la página a descargar.
            **kwargs: Parámetros adicionales para la solicitud GET.
        Returns:
            dict: Objeto JSON con el contenido de la respuesta.
        """
        try:
            response = self.make_request(url, **kwargs)
            return response.json()

        # Manejo de excepciones para errores de conexión o tiempo de espera:
        except Exception as e:
            logging.error(f"Error al obtener el JSON de la URL: {url}: {e}")

        return None