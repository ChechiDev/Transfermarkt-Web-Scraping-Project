import os
import re
import logging
from typing import Dict
from datetime import datetime, date
from bs4 import BeautifulSoup, Tag
from scraping.ws_httpClient import HTTPClient
from config.exceptions import HTTPClientError
from scraping.ws_entities import League, LeagueStats, RegionStats, TransferMarket, Player
from pprint import pprint

def clear_terminal():
    """
    Limpia la terminal según el sistema operativo.
    """
    os.system("cls" if os.name == "nt" else "clear")


class ScrapingEngine:
    """
    Motor principal para realizar operaciones de scraping sobre Transfermarkt.
    Proporciona utilidades para procesar tablas, extraer datos y limpiar HTML.
    """
    def __init__(self, http_client: HTTPClient):
        """
        Inicializa el motor de scraping con un cliente HTTP.

        Args:
            http_client (HTTPClient): Cliente HTTP para realizar peticiones web.
        """
        self.http_client = http_client


    def expand_collpased_cells(self, table: BeautifulSoup):
        """
        Expande las celdas colapsadas de una tabla HTML, reemplazando su contenido por el expandido.

        Args:
            table (BeautifulSoup): Tabla HTML a procesar.
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
        Obtiene el número total de páginas de una tabla paginada en Transfermarkt.

        Args:
            url (str): URL de la página a analizar.

        Return:
            int: Número total de páginas.
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
        """
        Extrae los encabezados de una tabla HTML y los formatea según el tipo de tabla.

        Args:
            table (BeautifulSoup): Tabla HTML a analizar.
            header_type (str): Tipo de encabezado para personalizar el nombre.

        Return:
            dict: Diccionario con los encabezados y su índice.
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
        """
        Calcula la frecuencia de longitudes de filas en una tabla y la longitud máxima.

        Args:
            table (BeautifulSoup): Tabla HTML a analizar.

        Return:
            tuple: (dict con frecuencias, int longitud máxima)
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

            return length_summary, max_length

        except Exception as e:
            logging.error(f"Error al medir las longitudes de las filas: {e}")
            return {}, 0


    def get_country_info(self, table: BeautifulSoup) -> dict:
        """
        Extrae información de países (id, nombre, bandera) de una tabla HTML.

        Args:
            table (BeautifulSoup): Tabla HTML a analizar.

        Return:
            dict: Diccionario con información de países.
        """
        try:
            country_info = {}
            rows = table.find("tbody").find_all("tr")

            if not rows:
                logging.warning("No se encontraron filas en la tabla.")
                return country_info

            for row in rows:
                country_cell = row.find("td", {"class": "zentriert"})
                if not country_cell:
                    continue

                country_flag = country_cell.find("img", {"class": "flaggenrahmen"})
                if not country_flag:
                    logging.debug("No se encontró la imagen con clase 'flaggenrahmen'.")
                    continue

                # URL de la bandera
                country_flag_url = country_flag.get("src", "").strip()
                if not country_flag_url:
                    logging.warning("No se encontró la URL de la bandera.")
                    continue

                # Extraemos el ID del país de la URL de la bandera
                match = re.search(r"tiny/(\d+)\.png", country_flag_url)
                country_id = match.group(1) if match else None

                country_name = country_flag.get("title", "").strip()
                if not country_name:
                    logging.warning(f"No se encontró el nombre del país para la bandera con URL: {country_flag_url}")
                    continue

                country_info[country_id] = {
                    "id_country": country_id,
                    "country_name": country_name,
                    "country_flag": country_flag_url,
                }

            return country_info

        except Exception as e:
            logging.error(f"Error al obtener la información del país: {e}")
            raise ValueError(f"Error al obtener la información del país: {e}")


    def get_player_img_info(self, table: BeautifulSoup) -> dict:
        """
        Extrae información de imágenes de jugadores de una tabla HTML.

        Args:
            table (BeautifulSoup): Tabla HTML a analizar.

        Return:
            dict: Diccionario con información de imágenes de jugadores.
        """
        try:
            player_info = {}
            rows = table.find("tbody").find_all("tr")

            if not rows:
                logging.warning("No se encontraron filas en la tabla.")
                return player_info

            for row in rows:
                player_cell = row.find("td", {"class": "posrela"})
                if not player_cell:
                    continue

                inline_table = player_cell.find("table", class_="inline-table")
                if not inline_table:
                    continue

                first_tr = inline_table.find("tr")
                if not first_tr:
                    continue

                first_td = first_tr.find("td")
                if not first_td:
                    continue

                img_tag = first_td.find("img")
                img_player = img_tag.get("data-src") or img_tag.get("src") or None

                id_img = None
                if img_player:
                    match = re.search(r"/medium/(\d+-\d+)", img_player)
                    id_img = match.group(1) if match else None

                id_cell = row.find("td", {"class": "hauptlink"})
                if id_cell:
                    player_url = id_cell.find("a")["href"]
                    player_id_match = re.search(r"spieler/(\d+)", player_url)

                    if player_id_match:
                        player_id = player_id_match.group(1)
                        player_info[player_id] = {
                            "id_img": id_img,
                            "img_player": img_player
                        }

            return player_info

        except Exception as e:
            logging.error(f"Error al obtener la información de imágenes de los jugadores: {e}")
            raise ValueError(f"Error al obtener la información de imágenes de los jugadores: {e}")


    def get_date(self, element: Tag) -> str:
        """
        Extrae y formatea una fecha desde un elemento HTML.

        Args:
            element (Tag): Elemento HTML con la fecha.

        Return:
            str: Fecha en formato SQL o None.
        """
        if element:
            text = element.get_text(strip=True)

            # Extraemos solo la fecha antes del paréntesis
            match = re.search(r"([A-Za-z]+\s\d{1,2},\s\d{4})|(\d{1,2}\s[A-Za-z]+\s\d{4})", text)

            if match:
                raw_date = match.group(0)
                return self.format_date_to_sql(raw_date)

        return None


    def get_nationality_id(self, cell: Tag) -> str | None:
        """
        Extrae el ID de nacionalidad de un elemento de celda HTML.

        Args:
            cell (Tag): Celda HTML con la bandera.

        Return:
            str | None: ID de nacionalidad o None.
        """
        if cell:
            img = cell.find("img", {"class": "flaggenrahmen"})

            if img:
                src = img.get("src", "")
                match = re.search(r"verysmall/(\d+)", src)

                if match:
                    return match.group(1)
        return None


    def get_team_signed_from_id(self, cell: Tag) -> str | None:
        """
        Extrae el ID del equipo de procedencia de un jugador desde una celda HTML.

        Args:
            cell (Tag): Celda HTML con la imagen del equipo.

        Return:
            str | None: ID del equipo o None.
        """
        if cell:
            img = cell.find("img")

            if img:
                src = img.get("src", "")
                match = re.search(r"verysmall/(\d+)", src)

                if match:
                    return match.group(1)

        return None


    def get_player_height(self, cell: Tag) -> float:
        """
        Extrae la altura de un jugador desde una celda HTML.

        Args:
            cell (Tag): Celda HTML con la altura.

        Return:
            float: Altura del jugador en metros.
        """
        if isinstance(cell, str):
            text = cell
        else:
            text = cell.get_text(strip=True)

        match = re.search(r"(\d{1,2},\d{1,2})\s*m", text)
        if match:
            return self.float_validation(match.group(1))

        return 0.0


    def get_league_tier(self, table: BeautifulSoup) -> Dict[str, str]:
        """
        Extrae el nivel (tier) de cada liga de una tabla HTML.

        Args:
            table (BeautifulSoup): Tabla HTML a analizar.

        Return:
            dict: Diccionario con el nombre de la liga y su tier.
        """
        try:
            competition_to_tier = {}
            rows = table.find("tbody").find_all("tr")

            if not rows:
                logging.warning("No se encontraron filas en la tabla.")
                return competition_to_tier

            current_tier = None
            for row in rows:
                # Comprobamos si la fila es un encabezado de tier
                tier_cell = row.find("td", {"class": "extrarow bg_blau_20 hauptlink"})
                if tier_cell:
                    current_tier = tier_cell.get_text(strip=True)
                    continue

                # Comprobamos si la fila es una liga
                competition_cell = row.find("td", {"class": "hauptlink"})
                if competition_cell and current_tier:
                    competition_name = competition_cell.get_text(strip=True)
                    competition_to_tier[competition_name] = current_tier

            return competition_to_tier

        except Exception as e:
            logging.error(f"Error al obtener el nivel de la liga: {e}")
            raise ValueError(f"Error al obtener el nivel de la liga: {e}")


    def get_seasons(self, url: str) -> list[int]:
        """
        Extrae la lista de temporadas disponibles desde una URL de Transfermarkt.

        Args:
            url (str): URL de la página a analizar.

        Return:
            list[int]: Lista de temporadas disponibles.
        """
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

            # logging.info(f"Seasons extraídas: {seasons}")
            return seasons

        except Exception as e:
            logging.error(f"Error al obtener las temporadas de la URL: {url}. \nDetalle: {e}")
            raise HTTPClientError(f"Error al obtener las temporadas de la URL: {url}. \nDetalle: {e}")

    @staticmethod
    def int_validation(value, default) -> int:
        """
        Convierte un valor a entero, devolviendo un valor por defecto si falla.

        Args:
            value: Valor a convertir.
            default: Valor por defecto si la conversión falla.

        Return:
            int: Valor convertido o valor por defecto.
        """
        try:
            return int(value)

        except (ValueError, TypeError):
            return default

    @staticmethod
    def float_validation(value: str) -> float:
        """
        Convierte un string a float, adaptando formatos europeos y eliminando caracteres no numéricos.

        Args:
            value (str): Valor a convertir.

        Return:
            float: Valor convertido o 0.0 si falla.
        """
        try:
            return float(
                value
                .replace(",", ".")
                .replace("m", "")
                .replace(" %", "")
            )

        except ValueError:
            return 0.0

    @staticmethod
    def parse_currency_to_float(value: str) -> float:
        """
        Convierte un string de moneda de Transfermarkt a float.

        Args:
            value (str): Valor de moneda a convertir.

        Return:
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
            logging.warning(f"No se pudo convertir el valor: {value}")
            return 0.0

    @staticmethod
    def calculate_avg_value(
        leagues: Dict[str, League],
        region_stats: RegionStats,
        stat_name: str

    ) -> float:
        """
        Calcula el valor promedio de una estadística para todas las ligas de una región.

        Args:
            leagues (Dict[str, League]): Diccionario de ligas.
            region_stats (RegionStats): Objeto de estadísticas de la región.
            stat_name (str): Nombre de la estadística a promediar.

        Return:
            float: Valor promedio calculado.
        """

        # Validamos que region_stats sea una instancia de RegionStats
        if not isinstance(region_stats, RegionStats):
            raise TypeError(f"Se esperaba una instancia de RegionStats, pero se recibió {type(region_stats)}")

        valid_values = []

        for tier, leagues_in_tier in leagues.items():
            for league_id, league in leagues_in_tier.items():
                # Validamos que league sea una instancia de League
                if not isinstance(league, League):
                    logging.warning(f"La liga {league_id} no es una instancia de League. Tipo recibido: {type(league)}")
                    continue

                # Validamos que league.stats sea una instancia de LeagueStats
                if not isinstance(league.stats, LeagueStats):
                    logging.warning(f"La liga {league_id} tiene un atributo 'stats' inválido. Tipo recibido: {type(league.stats)}")
                    continue

                # Obtener el valor de la estadística
                value = getattr(league.stats, stat_name, None)
                if value is not None:
                    valid_values.append(value)

        # Calcula el promedio
        if not valid_values:
            setattr(region_stats, stat_name, 0.0)
            return 0.0

        total_stat_value = sum(valid_values)
        avg_stat_value = round(total_stat_value / len(valid_values), 2)

        setattr(region_stats, stat_name, avg_stat_value)
        return avg_stat_value

    @staticmethod
    def format_date_to_sql(date_str: str) -> date | None:
        """
        Convierte un string de fecha a formato date compatible con SQL.

        Args:
            date_str (str): Fecha en formato string.

        Return:
            date | None: Fecha en formato date o None si falla.
        """
        try:
            # Detectamos el formato de fecha:
            date_formats = ["%b %d, %Y", "%d %b %Y", "%Y-%m-%d"]
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt).date() # Formateamos a SQL

                except ValueError:
                    continue

            return None

        except Exception as e:
            logging.error(f"Error al formatear la fecha '{date_str}' al formato SQL: {e}")
            return None
