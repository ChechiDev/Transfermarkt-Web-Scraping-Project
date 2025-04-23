from scraping.ws_httpClient import HttpClient
from scraping.ws_engine import ScrapingEngine

class TransferMarktURLManager:
    """
    Gestor de URLs específicas de Transfermarkt
    """
    def __init__(self, scraping_engine: ScrapingEngine, http_client: HttpClient):
        self.scraping_engine = scraping_engine
        self.http_client = http_client
        self.urls = {
            "EUR1": {
                "region_name": "Europe",
                "url": "https://www.transfermarkt.com/wettbewerbe/europa/wettbewerbe?ajax=yw1&plus=22&page={page}",
                "start_page": 1,
                "end_page": None,
                "table_header": None,
            },
            "AME1": {
                "region_name": "America",
                "url": "https://transfermarkt.com/wettbewerbe/amerika/wettbewerbe?ajax=yw1&plus=22&page={page}",
                "start_page": 1,
                "end_page": None,
                "table_header": None,
            },
            "AFR1": {
                "region_name": "Africa",
                "url": "https://transfermarkt.com/wettbewerbe/afrika/wettbewerbe?ajax=yw1&plus=22&page={page}",
                "start_page": 1,
                "end_page": None,
                "table_header": None,
            },
            "ASI1": {
                "region_name": "Asia",
                "url": "https://transfermarkt.com/wettbewerbe/asien/wettbewerbe?ajax=yw1&plus=22&page={page}",
                "start_page": 1,
                "end_page": None,
                "table_header": None,
            },
        }

    def get_url(
            self,
            key: str,
            **kwargs
        ) -> str:
        """
        Devuelve la URL formateada para el país especificado.
        :param key: Clave del país (e.g., "europe", "america").
        :param kwargs: Parámetros adicionales para formatear la URL.
        :return: URL formateada.
        """
        # Validamos que la clave exista en el diccionario de URLs
        if key not in self.urls:
            raise KeyError(f"Región '{key}' no registrada en Transfermarkt")

        # Obtenemos la plantilla de URL
        url_template = self.urls[key]
        # Extraemos los campos requeridos de la plantilla (entre llaves {})
        required_fields = [field.strip("{}") for field in url_template.split("{") if "}" in field]

        # Validamos que todos los campos requeridos estén en kwargs:
        for field in required_fields:
            if field not in kwargs:
                raise KeyError(f"Falta el parámetro '{field}' para la URL '{key}'")

        return url_template.format(**kwargs)

    def update_region_data(self, region: str):
        """
        Calcula y actualiza dinámicamente los valores de "end_page" y "table_header" para una región específica.
        """
        if region not in self.urls:
            raise KeyError(f"Región '{region}' no registrada en Transfermarkt")

        # Descargamos el HTML de la primera página:
        url = self.urls[region]["url"].format(page=1)
        html = self.http_client.get_html(url)

        if not html:
            raise ValueError(f"No se pudo descargar el HTML para la región '{region}'")

        # Calculamos total páginas y asignamos automáticamente a "end_page":
        total_pages = self.scraping_engine.get_total_pages(html)
        self.urls[region]["end_page"] = total_pages
        print(f"Total de páginas para la región '{region}': {total_pages}")

        # Extraemos el header de la tabla:
        table = html.find("table")
        if not table:
            raise ValueError(f"No se encontró ninguna tabla en el HTML para la región '{region}'")

        # Extraemos los encabezados de la tabla y los asignamos a `table_header`:
        self.urls[region]["table_header"] = self.scraping_engine.get_table_headers(table)
        print(f"Encabezados de la tabla para la región '{region}': {self.urls[region]['table_header']}")

class URLManager:
    """
    Gestor principal de URLs de scraping para múltiples proveedores (webs).
    """

    def __init__(self, scraping_engine: ScrapingEngine, http_client: HttpClient):
        self.providers = {
            "transfermarkt": TransferMarktURLManager(scraping_engine, http_client),
            # "sofascore": SofascoreURLManager(),  <-  en el futuro
        }

    def get_url(
            self,
            provider: str,
            key: str,
            **kwargs
        ) -> str:
        """
        Devuelve la URL de un proveedor usando su clave interna.

        provider: "transfermarkt" | "sofascore"
        key: "europe" | "top_teams" | etc.
        kwargs: variables como page=1, country="germany"
        """
        if provider not in self.providers:
            raise ValueError(f"Proveedor '{provider}' no está registrado.")

        return self.providers[provider].get_url(key, **kwargs)