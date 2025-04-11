from config.headers import headers
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
import time
import os

class HttpClient:
    """
    Clase para manejar solicitudes HTTP con lógica de reintentos.
    """
    def __init__(self, max_retries=5, delay=1, headers=None):
        """
        Constructor de la clase HttpClient.

        Args:
            max_retries (int): Número máximo de reintentos en caso de error.
            delay (int): Tiempo de espera entre reintentos (en segundos).
            headers (dict): Headers HTTP para las solicitudes.
        """
        self.headers = headers or {}
        self.max_retries = 5
        self.delay = delay

    def get_html(self, url):
        """
        Realiza una solicitud HTTP GET y devuelve el contenido HTML parseado con BeautifulSoup.

        Args:
            url (str): URL de la página a descargar.

        Returns:
            BeautifulSoup: Objeto BeautifulSoup con el contenido HTML.
            None: Si no se pudo descargar el HTML después de los reintentos.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()  # Lanza un error si la respuesta no es 200
                return BeautifulSoup(response.text, 'html.parser')

            except requests.exceptions.RequestException as e:
                print(f"Error al descagar {url} (intento {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    time.sleep(self.delay)
                else:
                    print("Se agotaron los intentos.")
            return None

class Scraper:
    """
    Clase abstracta base para todos los scrapers específicos.
    Define los métodos que deben ser implementados por los scrapers.
    """
    def __init__(self, http_client):
        """
        Constructor de la clase AbstractScraper.

        Args:
            http_client (HttpClient): Instancia de HttpClient para manejar solicitudes HTTP.
        """
        self.http_client = http_client
        self.urls = {}

    def get_url_from_env(self):
        """
        Carga las URLs desde el archivo .env y las almacena en el atributo `urls`.

        Raises:
            FileNotFoundError: Si el archivo .env no existe.
        """
        try:
            load_dotenv()
            for k, v in os.environ.items():
                if k.startswith('URL_'):
                    self.urls[k.lower().strip()] = v.strip()
            print(f"Claves cargadas desde .env: {self.urls}")

            if not self.urls:
                raise ValueError("No se encontraron URLs en el archivo .env.")

        except FileNotFoundError:
            raise FileNotFoundError("El archivo .env no fue encontrado. Asegúrate de que exista en la raíz del proyecto.")

    def build_url(self, url_key, page=1):
        """
        Construye una URL dinámica reemplazando las variables en la plantilla.

        Args:
            url_key (str): Clave de la URL en el diccionario `urls`.
            kwargs: Variables a reemplazar en la plantilla de la URL.

        Returns:
            str: URL construida.

        Raises:
            ValueError: Si la clave `url_key` no existe en el diccionario `urls`.
        """
        print(f"Clave recibida en build_url: '{url_key}'")
        print(f"Claves disponibles en self.urls: {self.urls.keys()}")

        if url_key not in self.urls:
            raise ValueError(f"URL '{url_key}' no encontrada en las URL cargadas: {list(self.urls.keys())}")

        url_temp = self.urls[url_key]

        try:
            return url_temp.format(page=page)

        except KeyError as e:
            raise ValueError(f"Falta la variable '{e.args[0]}' en los argumentos para construir la URL.")

    def get_table(self, url, table_class = "items"):
        """
        Busca una tabla en el HTML de la URL especificada.

        Args:
            url (str): URL de la página donde se buscará la tabla.
            table_class (str): Clase CSS de la tabla a buscar.

        Returns:
            BeautifulSoup.Tag: Tabla HTML encontrada o None si no se encuentra.
        """
        html = self.http_client.get_html(url)
        if not html:
            print(f"No se ha podido descargar el HTML.")
            return None

        try:
            table = html.find("table", {"class": table_class})
            if not table:
                print(f"No se ha encontrado una tabla con la clase '{table_class}'.")
                return None
            return table

        except Exception as e:
            print(f"Error al buscar la tabla: {e}")
            return None

    def get_data(self, url_key, table_class = "items", row_parser = None, start_page=1, end_page=None):
        """
        Extrae los datos de una tabla desde múltiples páginas y los devuelve como una lista de diccionarios.

        Args:
            url_template (str): Plantilla de la URL con un marcador {page} para las páginas.
            table_class (str): Clase CSS de la tabla a buscar.
            row_parser (callable): Función para procesar cada fila de la tabla.
            start_page (int): Número de la primera página a scrapear.
            end_page (int): Número de la última página a scrapear.

        Returns:
            list: Lista de diccionarios con los datos extraídos.
        """
        url = self.build_url(url_key, page=start_page)
        if end_page is None:
            end_page = self.get_total_pages(url)

        data = []

        for page in range(start_page, end_page + 1):
            print(f"Scrapeando página {page}...")

            # Construimos la URL para la página actual:
            try:
                url = self.build_url(url_key, page=page)

            except ValueError as e:
                print(f"Error al construir la URL: {e}")
                continue


            table = self.get_table(url, table_class)
            if not table:
                print(f"No se encontró una tabla en la página {page}.")
                continue

            try:
                rows = table.find_all("tr")
                for row in rows:
                    # Validamos que haya información:
                    cells = row.find_all("td")
                    if not cells:
                        continue

                    if row_parser:
                        parsed_row = row_parser(row)
                        if parsed_row:
                            data.append(parsed_row)

            except Exception as e:
                print(f"Error al extraer datos de la tabla en la página: {page}:{e}")

        return data

    def get_total_pages(self, url, pagination_class = "tm-pagination"):
        """
        Obtiene el número total de páginas desde el elemento de paginación.

        Args:
            url (str): URL de la página inicial.
            pagination_class (str): Clase CSS del contenedor de paginación.

        Returns:
            int: Número total de páginas, o 1 si no se encuentra el elemento de paginación.
        """
        html = self.http_client.get_html(url)
        if not html:
            print(f"No se ha podido descargar el HTML.")
            return 1 # Retornamos siempre 1, para tener un end page.

        # print(html.prettify()) # Para depurar el HTML descargado.

        try:
            # Buscamos el contenedor de paginación en el html:
            pagination = html.find("ul", {"class": pagination_class})
            if not pagination:
                print(f"No se ha encontrado el contenedor de paginación con la clase '{pagination_class}'.")
                return 1

            # Buscamos el enlace de la última página:
            last_page_link = pagination.find("li", {"class": "tm-pagination__list-item--icon-last-page"})
            if not last_page_link:
                print(f"No se ha encontrado el enlace de la última página.")
                return 1

            # extraemos el número de la última página:
            last_page_href = last_page_link.find("a")
            if not last_page_href or "href" not in last_page_href.attrs:
                print(f"No se ha encontrado el atributo 'href' en el enlace de la última página.")
                return 1

            total_pages = int(last_page_href["href"].split("page=")[-1])
            return total_pages

        except Exception as e:
            print(f"Error al buscar el contenedor de paginación: {e}")
            return 1