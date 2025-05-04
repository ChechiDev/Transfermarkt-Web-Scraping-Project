import re
import logging
from typing import Dict
from bs4 import BeautifulSoup
from scraping.ws_httpClient import HTTPClient
from config.exceptions import HTTPClientError
from scraping.ws_entities import League, LeagueStats, RegionStats, TransferMarket

class ScrapingEngine:
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client


    def expand_collpased_cells(self, table: BeautifulSoup):
        """
        Expande las celdas colapsadas en una tabla HTML.
        """

        try:
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
        """

        # Realizamos la solicitud HTTP para obtener el HTML de la página:
        try:
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


    def get_table_headers(self, table: BeautifulSoup, header_type: str = "default") -> dict:
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
                if text:  # Ignorar columnas vacías
                    formatted_text = text.replace(" ", "_").replace(".", "").replace("ø", "avg").lower()

                    # Personalizar encabezados según el tipo de tabla
                    if header_type == "region":
                        formatted_text = f"region_{formatted_text}"

                    elif header_type == "league":
                        formatted_text = f"league_{formatted_text}"

                    headers[formatted_text] = idx

            return headers

        except Exception as e:
            logging.error(f"Error al extraer encabezados de la tabla: {e}")
            return {}


    def measure_row_lengths(self, table: BeautifulSoup) -> tuple:
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

            return length_summary, max_length

        except Exception as e:
            logging.error(f"Error al medir las longitudes de las filas: {e}")
            return {}, 0


    def get_seasons(self, url: str) -> list[int]:
        try:
            respponse = self.http_client.make_request(url)
            if not respponse:
                logging.error(f"No se pudo obtener el HTML de la URL: '{url}'.")
                raise HTTPClientError(f"No se pudo obtener el HTML de la URL: {url}")

            # Parseamos:
            soup = BeautifulSoup(respponse.content, "html.parser")

            select_element = soup.find("select", {"name": "saison_id"})
            if not select_element:
                logging.error(f"No se encontró el elemento select para las temporadas en la URL: {url}")
                return []

            # Extraemos las seasons:
            seasons = [
                int(option.get("value"))
                for option in select_element.find_all("option")
                if option.get("value")
            ]

            logging.info(f"Seasons extraídas: {seasons}")
            return seasons

        except Exception as e:
            logging.error(f"Error al obtener las temporadas de la URL: {url}. \nDetalle: {e}")
            raise HTTPClientError(f"Error al obtener las temporadas de la URL: {url}. \nDetalle: {e}")

    @staticmethod
    def int_validation(value, default) -> int:
        try:
            return int(value)

        except (ValueError, TypeError):
            return default

    @staticmethod
    def float_validation(value: str) -> float:
        try:
            return float(value.replace(",", ".").replace(" %", ""))

        except ValueError:
            return 0.0

    @staticmethod
    def parse_currency_to_float(value: str) -> float:
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
            logging.warning(f"No se pudo convertir el valor: {value}")
            return 0.0

    @staticmethod
    def calculate_avg_value(
        leagues: Dict[str, League],
        region_stats: RegionStats,
        stat_name: str

    ) -> float:

        if not leagues:
            setattr(region_stats, stat_name, 0.0)
            return 0.0

        valid_values = [
            getattr(league.stats, stat_name, 0.0) for league in leagues.values()
            if league.stats and getattr(league.stats, stat_name, None) is not None
        ]

        if not valid_values:
            setattr(region_stats, stat_name, 0.0)
            return 0.0

        total_stat_value = sum(valid_values)
        avg_stat_value = round(total_stat_value / len(valid_values), 2)

        setattr(region_stats, stat_name, avg_stat_value)
        return avg_stat_value