import requests
from bs4 import BeautifulSoup
from time import sleep
from typing import Dict, Optional
from config.headers import headers
from scraping.ws_engine import ScrapingEngine

class HttpClient:
    """
    Cliente HTTP reutilizable para descargar y parsear HTML de forma segura.
    """
    def __init__(
            self,
            base_headers = None,
            timeout = 5,
            retries = 3,
            delay = 1

        ):
        self.headers = base_headers or headers
        self.timeout = timeout
        self.retries = retries
        self.delay = delay # Segundos entre reintentos
        self.url_manager = None

    def initialize_url_manager(self):
        """
        Inicializa el gestor de URLs con la configuración de scraping.
        """
        from src.ws_urls import URLManager
        scraping_engine = ScrapingEngine(self)
        self.url_manager = URLManager(self, scraping_engine)

    def get_html(
            self,
            url: str

        ) -> str:
        """
        Realiza una solicitud GET y devuelve el contenido HTML como objeto BeautifulSoup.

        Args:
            url (str): URL a descargar

        Returns:
            BeautifulSoup: HTML parseado o None si falla.
        """
        for attempt in range(self.retries):
            try:
                respone = requests.get(url, headers = self.headers, timeout = self.timeout)

                if respone.status_code == 200:
                    return BeautifulSoup(respone.text, 'html.parser')
                else:
                    print(f"HTTP: {respone.status_code} para {url}")

            except requests.RequestException as e:
                print(f"Error: Fallo en intento {attempt + 1}/{self.retries} para {url}: {e}")

            sleep(self.delay)

        print(f"Error: No se pudo acceder a la URL: {url}")
        return None

    def get_html_from_regions(
            self,
            provider: Optional[str] = None,
            region: Optional[str] = None,
            page: int = 1

        ) -> Dict[str, Dict[str, Optional[BeautifulSoup]]]:
        """
        Recorre todos los providers (o uno específico) y descarga el HTML
        de cada clave de región/recurso.

        Returns:
            Dict[provider][region] = BeautifulSoup | None
        """
        html_by_provider = {}

        providers_to_scrape = (
            [provider] if provider else list(self.url_manager.providers.keys())
        )

        for prov in providers_to_scrape:
            html_by_provider[prov] = {}
            region_keys = region or list(self.url_manager.providers[prov].urls.keys())

            for rkey in region_keys:
                try:
                    url = self.url_manager.get_url(prov, rkey, page = page)
                    html = self.get_html(url)
                    html_by_provider[prov][rkey] = html

                except Exception as e:
                    print(f"Error: {prov.upper()} - {rkey}: {e}")
                    html_by_provider[prov][rkey] = None

            return html_by_provider
