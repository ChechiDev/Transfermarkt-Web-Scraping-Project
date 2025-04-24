from scraping.ws_httpClient import HTTPClient
from scraping.ws_engine import ScrapingEngine

class URLManager:
    """
    Gestor principal de URL para scraping en múltiples páginas web.
    """
    def __init__(self, http_client: HTTPClient, scraping_engine: ScrapingEngine):
        pass


class TransfermarktURLManager(URLManager):
    """
    Gestor de URL específico para Transfermarkt.
    """
    def __init__(self, http_client: HTTPClient, scraping_engine: ScrapingEngine):
        self.http_client = http_client
        self.scraping_engine = scraping_engine
        self.url = {
            "EUR1": {
                "region_name": "Europe",
                "url": "https://www.transfermarkt.com/wettbewerbe/europa/wettbewerbe?ajax=yw1&plus=22&page={page}",
                "table_header": None,
                "start_page": 1,
                "end_page": None,
            }
        }
