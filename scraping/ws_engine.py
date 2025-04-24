import re
from bs4 import BeautifulSoup
from scraping.ws_httpClient import HTTPClient

class ScrapingEngine:
    """
    Motor reutilizable que contiene métodos genéricos reutilizables para el scraping.
    """
    def __init__(self, http_client: HTTPClient):
        # Instancia a HTTPClient para manejar las peticiones HTTP:
        self.http_client = http_client