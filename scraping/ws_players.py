import re
import json
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from scraping.ws_engine import ScrapingEngine
from scraping.ws_entities import Team, TeamStats, League, Region, Player, PlayerStats
from scraping.ws_dataManager import DataManager
from typing import List
from pprint import pprint


class PlayerManager:
    """
    Clase para gestionar la extracción y procesamiento de datos de jugadores desde Transfermarkt.
    Permite obtener información de jugadores y extraer valores de celdas.
    """
    base_url = "https://www.transfermarkt.com"

    base_config = {
        "offset": 0,
        "default": None,
        "transform": lambda x: x
    }

    def __init__(self, scraping_engine: ScrapingEngine):
        """
        Inicializa el PlayerManager con el motor de scraping.

        Args:
            scraping_engine (ScrapingEngine): Motor de scraping.
        """

        self.scraping_engine = scraping_engine

        self.player_field_config = {
            "player_name": {
                **self.base_config,
                "key": "player",
                "transform": lambda x: x.find("a").get_text(strip=True)
                if x and x.find("a") else None
            },
            "general_position": {
                **self.base_config,
                "key": "position",
                "transform": lambda x: x.parent["title"]
                if x and x.parent
                and "title" in x.parent.attrs else None
            },
            "player_position": {
                **self.base_config,
                "key": "player",
                "transform": lambda x: (
                    x.find("table").find_all("tr")[1].find_all("td")[0].get_text(strip=True)

                    if x
                    and x.find("table")
                    and len(x.find("table").find_all("tr")) > 1
                    and len(x.find("table").find_all("tr")[1].find_all("td")) > 0
                    else None
                ),
            },
            "birth_date": {
                **self.base_config,
                "key": "date_of_birth/age",
                "offset": 3,
                "transform": lambda x: (
                    self.scraping_engine.get_date(x).strftime("%Y-%m-%d")
                    if x and self.scraping_engine.get_date(x) else None
                )
            },
            "player_age": {
                **self.base_config,
                "key": "date_of_birth/age",
                "offset": 3,
                "transform": lambda x: (
                    (datetime.now().year - self.scraping_engine.get_date(x).year) -
                    (
                        (datetime.now().month, datetime.now().day) <
                        (self.scraping_engine.get_date(x).month, self.scraping_engine.get_date(x).day)
                    )
                    if x and self.scraping_engine.get_date(x) else None
                )
            },
            "fk_country": {
                **self.base_config,
                "key": "nat",
                "offset": 3,
                "transform": lambda x: (
                    self.scraping_engine.get_nationality_id(x) if x else None
                )
            },
            "player_height": {
                **self.base_config,
                "key": "height",
                "offset": 3,
                "transform": lambda x: (
                    self.scraping_engine.get_player_height(x) if x else None
                )
            },
            "player_foot": {
                **self.base_config,
                "key": "foot",
                "offset": 3,
                "transform": lambda x: x.get_text(strip=True)
                if x and x.get_text(strip=True) else None,
            },
            "player_joined": {
                **self.base_config,
                "key": "joined",
                "offset": 3,
                "transform": lambda x: (
                    self.scraping_engine.get_date(x).strftime("%Y-%m-%d")
                    if x and self.scraping_engine.get_date(x) else None
                )
            },
            "player_contract": {
                **self.base_config,
                "key": "contract",
                "offset": 3,
                "transform": lambda x: (
                    self.scraping_engine.get_date(x).strftime("%Y-%m-%d")
                    if x and self.scraping_engine.get_date(x) else None
                )
            },
            "fk_team_signed_from": {
                **self.base_config,
                "key": "signed_from",
                "offset": 3,
                "transform": lambda x: (
                    self.scraping_engine.get_team_signed_from_id(x) if x else None
                )
            },
            "market_value": {
                **self.base_config,
                "key": "market_value",
                "offset": 3,
                "transform": lambda x: ScrapingEngine.parse_currency_to_float(
                    x.get_text(strip=True)
                    )
                    if x else 0.0
            },
            "url_player": {
                **self.base_config,
                "key": "player",
                "transform": lambda x: (
                    PlayerManager.base_url + x.find("a")["href"].replace("startseite", "kader")
                    if x and x.find("a") and "href" in x.find("a").attrs
                    else None
                )
            },
        }


    def extract_cell_value(
            self,
            headers,
            col,
            key,
            offset: int = 0,
            default=None,
            transform=lambda x: x
        ):
        """
        Extrae y transforma el valor de una celda de la tabla según la configuración.

        Args:
            headers (dict): Diccionario de encabezados de la tabla.
            col (list): Lista de celdas de la fila.
            key (str): Clave del encabezado.
            offset (int): Desplazamiento para la columna.
            default: Valor por defecto si falla la extracción.
            transform (callable): Función de transformación para el valor.

        Return:
            Valor extraído y transformado, o el valor por defecto.
        """

        try:
            index = headers[key] + offset if headers.get(key) is not None else None
            cell = col[index] if index is not None and index < len(col) else None

            return transform(cell) if cell else default

        except (IndexError, AttributeError) as e:
            logging.warning(f"Error al extraer el valor de la celda: {e}")
            return default

    def get_player_data(
            self,
            table: BeautifulSoup,
            min_columns: int,
            fk_region: str,
            fk_league: str,
            team: Team,

    ) -> List[Player]:
        """
        Extrae los datos de los jugadores de una tabla HTML y devuelve una lista de objetos Player.

        Args:
            table (BeautifulSoup): Tabla HTML con los datos de los jugadores.
            min_columns (int): Número mínimo de columnas requeridas por fila.
            fk_region (str): ID de la región.
            fk_league (str): ID de la liga.
            team (Team): Equipo al que pertenecen los jugadores.

        Return:
            List[Player]: Lista de objetos Player extraídos de la tabla.
        """

        player_img_info_dict = self.scraping_engine.get_player_img_info(table)

        headers = self.scraping_engine.get_table_headers(table)
        if not headers:
            logging.error("No se encontraron encabezados en la tabla.")
            return []

        rows = table.find("tbody").find_all("tr")
        if not rows:
            logging.warning("No se encontraron filas en la tabla.")
            return []

        players = []
        for row in rows:
            col = row.find_all("td")

            if not col or len(col) < min_columns:
                continue

            try:
                extracted_values = {
                    field: self.extract_cell_value(
                        headers=headers,
                        col=col,
                        key=config["key"],
                        offset=config.get("offset", 0),
                        default=config.get("default", None),
                        transform=config["transform"]
                    )
                    for field, config in self.player_field_config.items()
                }

                general_position = row.find("td", {"title": True})
                extracted_values["general_position"] = general_position["title"] if general_position else None

                player_url_cell = row.find("td", {"class": "hauptlink"})
                extracted_values["url_player"] = (
                    self.base_url + player_url_cell.find("a")["href"]
                    if player_url_cell and player_url_cell.find("a")
                    else None
                )

                extracted_values["player_name"] = (
                    player_url_cell.find("a").get_text(strip=True)
                    if player_url_cell and player_url_cell.find("a")
                    else None
                )

                id_player = (
                    re.search(r"spieler/(\d+)", extracted_values["url_player"]).group(1)
                    if extracted_values["url_player"] and re.search(r"spieler/(\d+)", extracted_values["url_player"])
                    else None
                )

                player_stats = PlayerStats(
                    player_position=extracted_values["player_position"],
                    player_foot=extracted_values["player_foot"],
                    player_age=extracted_values["player_age"],
                    player_height=extracted_values["player_height"],
                    general_position=extracted_values["general_position"],
                    birth_date=extracted_values["birth_date"],
                    market_value=extracted_values["market_value"],

                )

                player = Player(
                    id_player=id_player,
                    url_player=extracted_values["url_player"],
                    player_name=extracted_values["player_name"],
                    season=team.season,
                    player_img_info={},
                    fk_country=extracted_values["fk_country"],
                    player_joined=extracted_values["player_joined"],
                    player_contract=extracted_values["player_contract"],
                    fk_team_signed_from=extracted_values["fk_team_signed_from"],
                    fk_region=fk_region,
                    fk_league=fk_league,
                    stats=player_stats,
                )

                img_info = self.scraping_engine.get_player_img_info(table)

                if id_player in player_img_info_dict:
                    img_info = player_img_info_dict[id_player]
                    player.add_player_img_info(img_info=img_info)

                else:
                    logging.warning(f"No se encontró información de imagen para el jugador con ID: {id_player}")

                logging.info(f"Jugador agregado: {json.dumps(player.__dict__, default=str, ensure_ascii=False, indent=4)}")
                players.append(player)

            except Exception as e:
                logging.warning(f"No se ha podido extraer los campos de la fila: {e}")
                continue

        # pprint(players, indent=4)
        return players
