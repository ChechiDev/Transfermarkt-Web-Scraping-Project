import re
import json
import logging
from bs4 import BeautifulSoup
from scraping.ws_engine import ScrapingEngine
from scraping.ws_entities import Team, TeamStats, League, Region, Player
from scraping.ws_players import PlayerManager
from scraping.ws_dataManager import DataManager
from typing import List


class TeamManager:
    """
    Clase para gestionar la extracción y procesamiento de datos de equipos desde Transfermarkt.
    Permite obtener información de equipos, procesar jugadores y extraer valores de celdas.
    """
    base_url = "https://www.transfermarkt.com"
    url_plus = "/plus/1"

    base_config = {
        "offset": 0,
        "default": None,
        "transform": lambda x: x
    }

    team_field_config = {
        "name": {
            **base_config,
            "key": "name",
            "transform": lambda x: x.get_text(strip=True) if x else None
        },
        "url_team": {
            **base_config,
            "key": "squad",
            "transform": lambda x: (
                TeamManager.base_url + x.find("a")["href"] + TeamManager.url_plus
                if x and x.find("a") and "href" in x.find("a").attrs
                else None
            )
        },
        "squad": {
            **base_config,
            "key": "squad",
            "transform": lambda x: ScrapingEngine.int_validation(
                x.get_text(strip=True).replace(".", ""),
                default=0
                )
                if x else 0
        },
        "avg_age": {
            **base_config,
            "key": "avg_age",
            "transform": lambda x: ScrapingEngine.float_validation(
                x.get_text(strip=True)
                .replace(",", ".")
                )
                if x else 0.0
        },
        "foreigners": {
            **base_config,
            "key": "foreigners",
            "transform": lambda x: ScrapingEngine.int_validation(
                x.get_text(strip=True).replace(".", ""),
                default=0
                )
                if x else 0.0
        },
        "avg_market_value": {
            **base_config,
            "key": "avg_market_value",
            "transform": lambda x: ScrapingEngine.parse_currency_to_float(
                x.get_text(strip=True)
                )
                if x else 0.0
        },
        "total_market_value": {
            **base_config,
            "key": "total_market_value",
            "transform": lambda x: ScrapingEngine.parse_currency_to_float(
                x.get_text(strip=True)
                )
                if x else 0.0
        }
    }

    def __init__(
            self,
            scraping_engine: ScrapingEngine,
            data_manager: DataManager,

        ):
        """
        Inicializa el TeamManager con el motor de scraping y el gestor de datos.

        Args:
            scraping_engine (ScrapingEngine): Motor de scraping.
            data_manager (DataManager): Gestor de datos.
        """
        self.scraping_engine = scraping_engine
        self.data_manager = data_manager
        self.player_manager = PlayerManager(scraping_engine)


    def process_team_players(self, team: Team) -> None:
        """
        Procesa los jugadores de un equipo, extrayendo su información y agregándolos al equipo.

        Args:
            team (Team): Instancia del equipo a procesar.
        """

        response = self.scraping_engine.http_client.make_request(team.url_team)
        if not response:
            logging.error(f"No se pudo obtener el HTML del equipo: {team.url_team}")
            return

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "items"})
        if not table:
            logging.warning(f"No se encontró la tabla de jugadores en el equipo: {team.url_team}")
            return

        players = self.player_manager.get_player_data(
            table,
            min_columns=5,
            fk_region=team.fk_region,
            fk_league=team.fk_league,
            team=team,
        )

        for player in players:
            team.add_player(player)


    def extract_cell_value(
            self,
            headers,
            col,
            key,
            offset: int = 1,
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
            cell = col[headers[key] + offset] if headers.get(key) is not None else None
            return transform(cell) if cell else default

        except (IndexError, AttributeError) as e:
            logging.warning(f"Error al extraer el valor de la celda: {e}")
            return default


    def get_team_data(
            self,
            table: BeautifulSoup,
            min_columns: int,
            region: Region,
            league: League

        ) -> List[Team]:
        """
        Extrae los datos de los equipos de una tabla HTML y devuelve una lista de objetos Team.

        Args:
            table (BeautifulSoup): Tabla HTML con los datos de los equipos.
            min_columns (int): Número mínimo de columnas requeridas por fila.
            region (Region): Región a la que pertenece el equipo.
            league (League): Liga a la que pertenece el equipo.

        Return:
            List[Team]: Lista de objetos Team extraídos de la tabla.
        """

        headers = self.scraping_engine.get_table_headers(table)
        if not headers:
            logging.error("No se encontraron encabezados en la tabla.")
            return []

        rows = table.find("tbody").find_all("tr")
        if not rows:
            logging.warning("No se encontraron filas en la tabla.")
            return []

        teams = []
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
                    for field, config in self.team_field_config.items()
                }

                # Propagar valores desde la liga
                extracted_values["fk_region"] = region.id_region
                extracted_values["fk_league"] = league.id_league
                extracted_values["season"] = league.season

                team_stats = TeamStats(
                    # Extraemos el ID del equipo de la URL
                    fk_team=re.search(r"verein/(\d+)", extracted_values["url_team"]).group(1)
                    if extracted_values["url_team"] else None,

                    fk_region=extracted_values["fk_region"],
                    fk_league=extracted_values["fk_league"],
                    season=extracted_values["season"],
                    total_players=extracted_values["squad"],
                    avg_age=extracted_values["avg_age"],
                    foreigners=extracted_values["foreigners"],
                    avg_market_value=extracted_values["avg_market_value"],
                    total_market_value=extracted_values["total_market_value"]
                )

                team = Team(
                    id_team=team_stats.fk_team,
                    fk_region=extracted_values["fk_region"],
                    fk_league=extracted_values["fk_league"],
                    season=extracted_values["season"],
                    team_name=extracted_values["name"],
                    url_team=extracted_values.get("url_team"),
                    stats=team_stats
                )

                # Log del nombre del equipo creada
                logging.info(f"Equipo agregado: {json.dumps(team.__dict__, default=str, ensure_ascii=False, indent=4)}")

                teams.append(team)

            except Exception as e:
                logging.warning(f"No se ha podido extraer los campos de la fila: {e}")
                continue

        # logging.info(f"Datos extraídos de la tabla: {len(teams)} filas.")
        return teams