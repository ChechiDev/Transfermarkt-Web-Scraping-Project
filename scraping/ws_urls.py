from scraping.ws_httpClient import HTTPClient
from scraping.ws_engine import ScrapingEngine
from config.exceptions import logging, HTTPClientError
from bs4 import BeautifulSoup
import validators


class URLManager:
    def __init__(self, http_client: HTTPClient, scraping_engine: ScrapingEngine):
        """
        Constructor del gestor de URL.
        Args:
            http_client(HTTPClient): Instancia del cliente HTTP para realizar solicitudes.
            scraping_engine(ScrapingEngine): Instancia del motor de scraping para procesar el HTML.
        """
        if not isinstance(http_client, HTTPClient):
            raise ValueError("El cliente HTTP debe ser una instancia de HTTPClient.")

        self.http_client = http_client
        self.scraping_engine = scraping_engine
        self.urls = {}  # Diccionario para almacenar las URLs de diferentes regiones.

    def add_url(self, key: str, url_data: dict):
        if "url" not in url_data or not validators.url(url_data["url"].replace("{page}", "1")):
            raise ValueError(f"La URL proporcionada no es válida: {url_data}")

        self.urls[key] = url_data


class TransfermarktURLManager(URLManager):
    def __init__(self, http_client: HTTPClient, scraping_engine: ScrapingEngine):
        super().__init__(http_client, scraping_engine)
        self.base_url = "https://www.transfermarkt.com/wettbewerbe/{region}/wettbewerbe?ajax=yw1&plus=22&page={page}"
        self.regions = {
            # "EUR1": "europa",
            # "AME1": "amerika",
            # "ASI1": "asien",
            "AFR1": "afrika",
        }
        self.initialize_urls()


    def initialize_urls(self):
        for key, region in self.regions.items():
            region_name = self.format_region_name(region)
            url = self.build_url(region, page=1)
            response = self.fetch_html(url)

            if not response:
                self.handle_failed_region(key)
            else:
                self.process_region_response(key, region, region_name, response)


    def format_region_name(self, region: str) -> str:
        return region.capitalize().replace("k", "c")


    def build_url(self, region: str, page: int) -> str:
        """
        Construye una URL para una región y una página específica.
        Returns:
            str: URL construida.
        """
        return self.base_url.format(region=region, page=page)


    def fetch_html(self, url: str) -> BeautifulSoup:
        """
        Realiza una solicitud HTTP y devuelve el HTML parseado.
        """
        response = self.http_client.make_request(url)
        if not response:
            logging.warning(f"No se pudo obtener el HTML de la URL: {url}")
            return None
        return BeautifulSoup(response.content, "html.parser")


    def region_warnings(self, key: str):
        logging.warning(f"No se pudo obtener el HTML de la región: '{key}'.")
        self.urls[key] = {
            "region_name": None,
            "url": [],
            "region": None,
            "table_header": None,
            "start_page": 1,
            "end_page": 1,
        }


    def process_region_response(self, key: str, region: str, region_name: str, html: BeautifulSoup):
        """
        Procesa la respuesta HTML de una región y genera las URLs.
        """
        table_header = self.extract_table_header(html)
        end_page = self.extract_total_pages(html, region)
        urls = self.generate_urls(region, end_page)

        self.urls[key] = {
            "region_name": region_name,
            "url": urls,
            "region": region,
            "table_header": table_header,
            "start_page": 1,
            "end_page": end_page,
        }


    def extract_table_header(self, html: BeautifulSoup):
        table = html.find("table")
        if not table:
            logging.warning("No se encontró ninguna tabla en la página.")
            return None
        return self.scraping_engine.get_table_headers(table)


    def extract_total_pages(self, html: BeautifulSoup, region: str) -> int:
        return self.scraping_engine.get_total_pages(self.build_url(region, page=1))


    def generate_urls(self, region: str, end_page: int) -> list:
        return [self.build_url(region, page) for page in range(1, end_page + 1)]