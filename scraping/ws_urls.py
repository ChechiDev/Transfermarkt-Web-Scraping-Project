from scraping.ws_httpClient import HTTPClient
from scraping.ws_engine import ScrapingEngine
from config.exceptions import logging, HTTPClientError
from bs4 import BeautifulSoup
import validators


class URLManager:
    """
    Clase base para gestionar y almacenar URLs de scraping.
    Permite agregar y validar URLs asociadas a diferentes regiones o entidades.
    """

    def __init__(self, http_client: HTTPClient, scraping_engine: ScrapingEngine):
        """
        Inicializa el URLManager con un cliente HTTP y un motor de scraping.

        Args:
            http_client (HTTPClient): Cliente HTTP para las peticiones web.
            scraping_engine (ScrapingEngine): Motor de scraping.
        """
        if not isinstance(http_client, HTTPClient):
            raise ValueError("El cliente HTTP debe ser una instancia de HTTPClient.")

        self.http_client = http_client
        self.scraping_engine = scraping_engine
        self.urls = {}  # Diccionario para almacenar las URLs de diferentes regiones.

    def add_url(self, key: str, url_data: dict):
        """
        Agrega una URL al diccionario de URLs, validando su formato.

        Args:
            key (str): Clave identificadora de la URL.
            url_data (dict): Diccionario con la información de la URL.

        Raises:
            ValueError: Si la URL no es válida.
        """
        if "url" not in url_data or not validators.url(url_data["url"].replace("{page}", "1")):
            raise ValueError(f"La URL proporcionada no es válida: {url_data}")

        self.urls[key] = url_data


class TransfermarktURLManager(URLManager):
    """
    Gestor especializado para las URLs de Transfermarkt.
    Genera y valida URLs para regiones, maneja paginación y encabezados de tablas.
    """
    def __init__(self, http_client: HTTPClient, scraping_engine: ScrapingEngine):
        """
        Inicializa el TransfermarktURLManager con cliente HTTP y motor de scraping.

        Args:
            http_client (HTTPClient): Cliente HTTP para las peticiones web.
            scraping_engine (ScrapingEngine): Motor de scraping.
        """
        super().__init__(http_client, scraping_engine)
        self.base_url = "https://www.transfermarkt.com/wettbewerbe/{region}/wettbewerbe?ajax=yw1&plus=22&page={page}"
        self.regions = {
            "EUR1": "europa",
            "AME1": "amerika",
            "ASI1": "asien",
            "AFR1": "afrika",
        }
        self.initialize_urls()


    def initialize_urls(self):
        """
        Inicializa las URLs de todas las regiones configuradas.
        Extrae encabezados de tabla y páginas totales para cada región.
        """
        for key, region in self.regions.items():
            region_name = self.format_region_name(region)
            url_region = self.build_url(region, page=1)
            response = self.fetch_html(url_region)

            if not response:
                self.handle_failed_region(key)

            else:
                self.process_region_response(key, region, region_name, response)


    def format_region_name(self, region: str) -> str:
        """
        Formatea el nombre de la región para mostrarlo correctamente.

        Args:
            region (str): Nombre de la región en minúsculas.

        Return:
            str: Nombre de la región formateado.
        """
        return region.capitalize().replace("k", "c")


    def build_url(self, region: str, page: int) -> str:
        """
        Construye la URL para una región y página específica.

        Args:
            region (str): Nombre de la región.
            page (int): Número de página.

        Return:
            str: URL construida.
        """
        return self.base_url.format(region=region, page=page)


    def fetch_html(self, url: str) -> BeautifulSoup:
        """
        Realiza una petición HTTP y devuelve el HTML parseado con BeautifulSoup.

        Args:
            url (str): URL a solicitar.

        Return:
            BeautifulSoup | None: Objeto BeautifulSoup o None si falla.
        """
        response = self.http_client.make_request(url)
        if not response:
            logging.warning(f"No se pudo obtener el HTML de la URL: {url}")
            return None

        return BeautifulSoup(response.content, "html.parser")


    def region_warnings(self, key: str):
        """
        Maneja el caso en que no se puede obtener el HTML de una región.

        Args:
            key (str): Clave de la región.
        """
        logging.warning(f"No se pudo obtener el HTML de la región: '{key}'.")
        self.urls[key] = {
            "region_name": None,
            "url_region": [],
            "region": None,
            "table_header": None,
            "start_page": 1,
            "end_page": 1,
        }


    def process_region_response(self, key: str, region: str, region_name: str, html: BeautifulSoup):
        """
        Procesa la respuesta HTML de una región, extrayendo encabezados y URLs de todas las páginas.

        Args:
            key (str): Clave de la región.
            region (str): Nombre de la región.
            region_name (str): Nombre formateado de la región.
            html (BeautifulSoup): HTML de la página de la región.
        """
        table_header = self.extract_table_header(html)
        end_page = self.extract_total_pages(html, region)
        urls = self.generate_urls(region, end_page)

        self.urls[key] = {
            "region_name": region_name,
            "url_region": urls,
            "region": region,
            "table_header": table_header,
            "start_page": 1,
            "end_page": end_page,
        }


    def extract_table_header(self, html: BeautifulSoup):
        """
        Extrae los encabezados de la tabla principal de la página HTML.

        Args:
            html (BeautifulSoup): HTML de la página.

        Return:
            dict | None: Diccionario de encabezados o None si no se encuentra la tabla.
        """
        table = html.find("table", {"class": "items"})
        if not table:
            logging.warning("No se encontró ninguna tabla en la página.")
            return None

        return self.scraping_engine.get_table_headers(table)


    def extract_total_pages(self, html: BeautifulSoup, region: str) -> int:
        """
        Extrae el número total de páginas para una región.

        Args:
            html (BeautifulSoup): HTML de la página.
            region (str): Nombre de la región.

        Return:
            int: Número total de páginas.
        """
        return self.scraping_engine.get_total_pages(self.build_url(region, page=1))


    def generate_urls(self, region: str, end_page: int) -> list:
        """
        Genera una lista de URLs para todas las páginas de una región.

        Args:
            region (str): Nombre de la región.
            end_page (int): Número total de páginas.

        Return:
            list: Lista de URLs generadas.
        """
        return [self.build_url(region, page) for page in range(1, end_page + 1)]