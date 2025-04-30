import os
import json
from bs4 import BeautifulSoup
from config.exceptions import HTTPClientError, logging
from scraping.ws_engine import ScrapingEngine
from scraping.ws_entities import Region, League, LeagueStats, TransferMarket
from typing import Dict

class DataManager:
    """
    Clase para gestionar y centralizar los datos del proyecto.
    Permite generar un JSON con la estructura completa de datos.
    """
    def __init__(self, http_client):
        # Instancia de TransferMarket para almacenar las regiones y sus datos
        self.transfer_market = TransferMarket()
        self.scraping_engine = ScrapingEngine(http_client)


    def extract_league_table_data(self, table: BeautifulSoup, min_columns: int, region_id: str) -> list:
        """
        Extrae todos los datos válidos de una tabla HTML y devuelve una lista de diccionarios.
        Solo incluye filas que tienen al menos `min_columns` columnas.

        Args:
            table (BeautifulSoup): Tabla HTML parseada.
            min_columns (int): Número mínimo de columnas requeridas para procesar una fila.

        Returns:
            list: Lista de diccionarios con los datos de la tabla.
        """
        try:
            # Extraemos los encabezados de la tabla:
            headers = self.scraping_engine.get_table_headers(table)
            if not headers:
                logging.error("No se encontraron encabezados en la tabla.")
                return []

            # Extraemos las filas de la tabla:
            rows = table.find("tbody").find_all("tr")
            if not rows:
                logging.warning("No se encontraron filas en la tabla.")
                return []

            # Procesamos las filas y extraemos los datos:
            leagues = []
            base_url = "https://www.transfermarkt.com"
            for row in rows:
                col = row.find_all("td")
                if not col:
                    logging.warning("Fila vacía o sin datos.")
                    continue

                # Filtrar filas que tienen menos columnas
                if len(col) < min_columns:
                    continue

                try:
                    # Extraer el texto y el enlace del campo 'competition'
                    competition_cell = col[headers["competition"]]
                    competition_name = competition_cell.get_text(strip=True)
                    competition_url = competition_cell.find("a")["href"] if competition_cell.find("a") else None

                    # Completamos URL:
                    if competition_url and not competition_url.startswith("http"):
                        competition_url = base_url + competition_url

                    # Extraemos el id_league de la URL:
                    id_league = None
                    if competition_url:
                        id_league = competition_url.split("/")[-1]


                    # Creamos un método para validar los valores númericos/float:
                    def float_validation(value: str) -> float:
                        try:
                            return float(value.replace(",", ".").replace(" %", ""))

                        except ValueError:
                            return 0.0


                    # Extraer el país desde la celda correspondiente
                    country_cell = col[headers["country"] + 2]
                    country_name = country_cell.find("img", {"class": "flaggenrahmen"})["title"] if country_cell.find("img", {"class": "flaggenrahmen"}) else None
                    country_flag = country_cell.find("img")["src"] if country_cell.find("img") else None

                    # Extraemos el total de clubes desde la celda correspondiente
                    clubs_cell = col[headers["clubs"] + 2]
                    total_clubs = int(clubs_cell.get_text(strip=True).replace(".", "").replace("-", "")) if clubs_cell else 0

                    # Extraemos el total de players desde la celda correspondiente
                    player_cell = col[headers["player"] + 2]
                    total_players = int(player_cell.get_text(strip=True).replace(".", "").replace("-", "")) if player_cell else 0

                    # Extraemos la media de edad jugadores:
                    avg_cell = col[headers["avg_age"] + 2]
                    avg_age = float_validation(avg_cell.get_text(strip=True).replace(",", ".")) if avg_cell else 0.0

                    # Extraemos los jugadores extranjeros
                    foreign_cell = col[headers["foreigners"] + 2] if headers.get("foreigners") is not None else 0.0
                    foreigners = float_validation(foreign_cell.get_text(strip=True).replace(",", ".").replace(" %", "")) if foreign_cell else 0.0

                    # Extraemos el average de partidos de jugadores extrangeros
                    game_ratio_of_foreign_players_cell = col[headers["game_ratio_of_foreign_players"] + 2] if headers.get("game_ratio_of_foreign_players") is not None else 0.0
                    game_ratio_of_foreign_players = float_validation(game_ratio_of_foreign_players_cell.get_text(strip=True).replace(",", ".").replace(" %", "")) if game_ratio_of_foreign_players_cell else 0.0

                    # Extraemos el average de goles por encuentro
                    goals_per_match_cell = col[headers["goals_per_match"] + 2] if headers.get("goals_per_match") is not None else 0.0
                    goals_per_match = float_validation(goals_per_match_cell.get_text(strip=True).replace(",", ".")) if goals_per_match_cell else 0.0

                    # Extraemos el average de mercado
                    average_market_value_cell = col[headers["average_market_value"] + 2] if headers.get("average_market_value") is not None else 0.0
                    # Convertimos el texto a float:
                    if average_market_value_cell:
                        avg_mrkt_text = average_market_value_cell.get_text(strip=True)
                        average_market_value = self.scraping_engine.parse_currency_to_float(avg_mrkt_text)
                    else:
                        average_market_value = 0.0


                    # Creamos instancia con LeagueStats:
                    league_stats = LeagueStats(
                        fk_league = id_league,
                        fk_region = region_id,
                        total_clubs = total_clubs,
                        total_players = total_players,
                        avg_age = avg_age,
                        foreigners = foreigners,
                        game_ratio_of_foreign_players = game_ratio_of_foreign_players,
                        goals_per_match = goals_per_match,
                        average_market_value = average_market_value
                    )

                    # Creamos instancia con League:
                    league = League(
                        id_league = id_league,
                        competition= competition_name,
                        country= country_name,
                        url= competition_url,
                        stats= league_stats,
                        teams= {} # Equipos vacío por ahora.
                    )

                    leagues.append(league)

                except IndexError:
                    logging.warning("No se pudo extraer los campos de la fila.")
                    continue

            logging.info(f"Datos extraídos de la tabla: {len(leagues)} filas.")
            return leagues

        except Exception as e:
            logging.error(f"Error al extraer datos de la tabla: {e}")
            return []


    def add_region(self, region: Region) -> None:
        """
        Añade una región a TransferMarket.
        Args:
            region (Region): Objeto de la clase Region.
        Raises:
            ValueError: Si el objeto region no es una instancia de Region.
        """
        if not isinstance(region, Region):
            logging.error("El objeto proporcionado no es una instancia de la clase Region.")
            raise ValueError("El objeto proporcionado no es una instancia de la clase Region.")

        self.transfer_market.regions[region.id_region] = region
        logging.info(f"Región '{region.region_name}' añadida correctamente.")


    def to_dict(self) -> Dict:
        """
        Convierte la instancia de TransferMarket en un diccionario.
        Returns:
            dict: Representación en diccionario de TransferMarket.
        """
        try:
            data = self.transfer_market.to_dict()
            logging.info("Datos convertidos a diccionario correctamente.")
            return data

        except Exception as e:
            logging.error(f"Error al convertir los datos a diccionario: {e}")
            raise HTTPClientError(f"Error al convertir los datos a diccionario: {e}")


    def to_json(self, file_name: str) -> None:
        """
        Guarda los datos en un archivo JSON dentro de la carpeta 'Data Output'.
        Args:
            file_name (str): Nombre del archivo JSON (sin la ruta completa).
        """
        try:
            # Construimos la ruta para guardar el json con la data:
            output_dir = os.path.join(os.getcwd(), "Data output")
            os.makedirs(output_dir, exist_ok=True) # Creamos la carpeta si no existe
            file_path = os.path.join(output_dir, file_name)


            # Convertimos la data a un diccionario:
            data = self.to_dict()

            with open(file_path, "w", encoding = "utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii = False, indent = 4)

            logging.info(f"Datos guardados en el archivo JSON: {file_path}")

        except Exception as e:
            logging.error(f"Error al guardar los datos en el archivo JSON: {e}")
            raise HTTPClientError(f"Error al guardar los datos en el archivo JSON: {e}")
