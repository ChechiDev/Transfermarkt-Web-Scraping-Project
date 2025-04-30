from scraping.ws_httpClient import HTTPClient
from scraping.ws_engine import ScrapingEngine
from config.exceptions import logging, HTTPClientError
from bs4 import BeautifulSoup
import validators

class URLManager:
    """
    Gestor principal de URL para scraping en múltiples páginas web.
    """
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
        self.urls = {} # Diccionario para almacenar las URLs de diferentes regiones.


    def add_url(self, key: str, url_data: dict):
        """
        Agrega una URL al gestor.
        Args:
            key (str): Clave para identificar la URL.
            url_data (dict): Diccionario con los datos de la URL (estructura JSON).
        """
        if "url" not in url_data or not validators.url(url_data["url"].replace("{page}", "1")):
            raise ValueError(f"La URL proporcionada no es válida: {url_data}")

        self.urls[key] = url_data



class TransfermarktURLManager(URLManager):
    """
    Gestor de URL específico para Transfermarkt.
    """
    def __init__(self, http_client: HTTPClient, scraping_engine: ScrapingEngine):
        super().__init__(http_client, scraping_engine)

        # Configuración inicial de las URLs para Transfermarkt:
        self.base_url = "https://www.transfermarkt.com/wettbewerbe/{region}/wettbewerbe?ajax=yw1&plus=22&page={page}"
        self.regions = {
            # "EUR1": "europa",
            "AME1": "amerika",
            # "ASI1": "asien",
            # "AFR1": "afrika",
        }


        # Generamos dinámicamente las entidades de de las regiones:
        for key, region in self.regions.items():
            region_name = region.capitalize().replace("k","c")

            url = self.base_url.format(region=region, page=1)

            response = self.http_client.make_request(url)
            if not response:
                logging.warning(f"No se pudo obtener el HTML de la región: '{key}'.")
                table_header = None
                end_page = 1
                urls = [] # Si no hay respuesta no hay urls

            else:
                # Parseamos el HTML y extramos los encabezados de la tabla:
                html = BeautifulSoup(response.content, "html.parser")
                table = html.find("table")
                if table:
                    table_header = self.scraping_engine.get_table_headers(table)
                else:
                    logging.warning(f"No se ha encontrado ninguna tabla en la página inicial de la región '{key}'.")
                    table_header = None

                # Extraemos el número total de páginas:
                end_page = self.scraping_engine.get_total_pages(url)

                # Construimos la lista de URLs para todas las páginas:
                urls = [
                    self.base_url.format(region=region, page=page)
                    for page in range(1, end_page + 1)
                ]

            self.urls[key] = {
                "region_name": region_name,
                "url": urls,
                "region": region,
                "table_header": table_header,
                "start_page": 1,
                "end_page": end_page,
            }