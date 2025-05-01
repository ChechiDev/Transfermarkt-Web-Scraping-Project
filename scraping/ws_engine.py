import re
import logging
from bs4 import BeautifulSoup
from scraping.ws_httpClient import HTTPClient
from config.exceptions import HTTPClientError
from scraping.ws_entities import League, LeagueStats, RegionStats, TransferMarket

class ScrapingEngine:
    """
    Motor reutilizable que contiene métodos genéricos reutilizables para el scraping.
    """
    def __init__(self, http_client: HTTPClient):
        # Instancia a HTTPClient para manejar las peticiones HTTP:
        self.http_client = http_client


    def expand_collpased_cells(self, table: BeautifulSoup):
        """
        Expande las celdas colapsadas en una tabla HTML.

        Args:
            table (BeautifulSoup): Objeto BeautifulSoup que contiene la tabla HTML.
        """

        try:
            # Recorremos todas las celdas de la tabla:
            for cell in table.find_all("td", {"class": "collapsed-cell"}):
                expanded_content = cell.get("data-content")

                if expanded_content:
                    cell.string = expanded_content.strip()
                    logging.info(f"Celda expandida: {cell.string}")

        except Exception as e:
            logging.error(f"Error al expandir las celdas colapsadas en la tabla. \nDetalle: {e}")
            raise ValueError(f"Error al expandir celdas colapsadas en la tabla. \nDetalle: {e}")



    def get_total_pages(self, url: str) -> int:
        """
        Obtiene el número total de páginas (end_page) para una región específica.

        Args:
            url (str): URL de la primera página de la región.

        Returns:
            int: Número total de páginas.
        """

        # Realizamos la solicitud HTTP para obtener el HTML de la página:
        try:
            # Realizamos la solicitud HTTP para obtener el HTML de la página:
            response = self.http_client.make_request(url)

            if not response:
                logging.error(f"No se pudo obtener el HTML de la URL: '{url}'.")
                raise HTTPClientError(f"No se pudo obtener el HTML de la URL: {url}")

            # Convertimos el contenido del Response en un objeto BeautifulSoup:
            html = BeautifulSoup(response.content, "html.parser")

            # Extraemos el número total de páginas del HTML:
            pagination = html.select_one(
                "ul.tm-pagination," \
                "div.pagination," \
                "ul.pagination," \
                "nav[role='navigation']"
            )

            if not pagination:
                logging.warning(f"No se encontró el elemento de paginación en el HTML de la URL: {url}")
                return 1  # Asignamos 1 página por defecto

            page_numbers = set()

            # Recorremos todos los enlaces dentro del contenedor:
            for a in pagination.find_all("a"):
                page_numbers.update(
                    int(n) for n in re.findall(r"\d+", a.get_text(strip=True))
                )

                # Buscamos los números de página en el texto del enlace:
                href = a.get("href", "")
                page_numbers.update(
                    int(n) for n in re.findall(r"page=(\d+)", href)
                )

            return max(page_numbers) if page_numbers else 1

        except Exception as e:
            logging.error(f"Error al calcular el número de páginas para la URL: {url}. \nDetalle: {e}")
            raise HTTPClientError(f"Error al calcular el número de páginas para la URL: {url}. \nDetalle: {e}")



    def get_table_headers(self, table: BeautifulSoup) -> dict:
        """
        Extrae los encabezados de una tabla HTML y los convierte en un diccionario.

        Args:
            table (BeautifulSoup): Tabla HTML parseada.

        Returns:
            dict: Diccionario con encabezados como claves y sus índices como valores.
        """
        try:
            headers = {}

            # Buscamos encabezado en thead o en la primera fila de la tabla:
            header_row = (
                table.find("thead").find("tr")
                if table.find("thead")
                else table.find_all("tr")[0]
            )

            if not header_row:
                logging.error("No se encontró encabezado en la tabla.")
                return {}

            th_elements = header_row.find_all(["th", "td"])
            for idx, th in enumerate(th_elements):
                text = th.get_text(strip=True)
                if text:  # ignorar columnas vacías
                    formattted_text = text.replace(" ", "_").replace(".", "").lower()
                    headers[formattted_text] = idx

            return headers

        except Exception as e:
            logging.error(f"Error al extraer encabezados de la tabla: {e}")
            return {}



    def measure_row_lengths(self, table: BeautifulSoup) -> tuple:
        """
        Mide la longitud de cada fila en una tabla HTML y devuelve un resumen y el valor más alto.

        Args:
            table (BeautifulSoup): Tabla HTML parseada.

        Returns:
            tuple: Un diccionario con las longitudes de las filas y su frecuencia, y el valor más alto.
        """
        try:
            # Extraer las filas de la tabla
            rows = table.find("tbody").find_all("tr")
            if not rows:
                logging.warning("No se encontraron filas en la tabla.")
                return {}, 0

            # Calculamos la longitud de cada fila
            row_lengths = [len(row.find_all("td")) for row in rows]

            # Count de la frecuencia de cada longitud
            length_summary = {}
            for length in row_lengths:
                length_summary[length] = length_summary.get(length, 0) + 1

            # Obtener el valor más alto
            max_length = max(row_lengths) if row_lengths else 0

            logging.info(f"Resumen de longitudes de filas: {length_summary}")
            logging.info(f"Valor más alto de longitud de fila: {max_length}")
            return length_summary, max_length

        except Exception as e:
            logging.error(f"Error al medir las longitudes de las filas: {e}")
            return {}, 0


    @staticmethod
    def float_validation(value: str) -> float:
        """
        Convierte un valor de texto a un número flotante.
        Args:
            value (str): El valor en formato de texto.
        Returns:
            float: El valor convertido a flotante, o 0.0 si no es válido.
        """
        try:
            return float(value.replace(",", ".").replace(" %", ""))

        except ValueError:
            return 0.0


    @staticmethod
    def parse_currency_to_float(value: str) -> float:
        """
        Convierte un texto de moneda como '592,92 mill. €' o '11,86 mil mill. €' a float.

        Args:
            value (str): Texto de moneda a convertir.

        Returns:
            float: Valor numérico convertido.
        """
        try:
            value = value.replace("€", "").replace(" ", "").strip().lower()

            if value.endswith("bn"):
                value = value.replace("bn", "")
                multiplier = 1e9  # Un billón

            elif value.endswith("m"):
                value = value.replace("m", "")
                multiplier = 1e6  # Un millón

            elif value.endswith("k"):
                value = value.replace("k", "")
                multiplier = 1e3  # Mil

            elif value == "-":
                return 0.0

            # Si no hay unidades, el multiplicador es 1
            else:
                multiplier = 1

            value = value.replace(".", "").replace(",", ".")

            return float(value) * multiplier

        except ValueError:
            # Si no se puede convertir, devolver 0.0 como valor predeterminado
            logging.warning(f"No se pudo convertir el valor: {value}")
            return 0.0