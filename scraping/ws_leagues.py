import logging
from bs4 import BeautifulSoup
from scraping.ws_engine import ScrapingEngine
from scraping.ws_entities import League, LeagueStats, Team, Region
from scraping.ws_teams import TeamManager
from scraping.ws_dataManager import DataManager
from typing import List

class LeagueManager:
    base_url = "https://www.transfermarkt.com"

    # Diccionario base para configuraciones comunes
    base_config = {
        "offset": 2,
        "default": None,
        "transform": lambda x: x
    }

    # Configuración de campos para extraer datos de la tabla
    league_field_config = {
        "competition_name": {
            **base_config,
            "key": "competition",
            "transform": lambda x: x.get_text(strip=True) if x else None
        },
        "competition_url": {
            **base_config,
            "key": "competition",
            "transform": lambda x: (
                LeagueManager.base_url + x.find("a")["href"]
                if x and x.find("a") and "href" in x.find("a").attrs
                else None
            )
        },
        "country_name": {
            **base_config,
            "key": "country",
            "transform": lambda x: (
                x.find("img", {"class": "flaggenrahmen"})["title"]
                if x and x.find("img", {"class": "flaggenrahmen"})
                else None
            )
        },
        "total_clubs": {
            **base_config,
            "key": "clubs",
            "transform": lambda x: ScrapingEngine.int_validation(
                x.get_text(strip=True)
                .replace(".", "")
                .replace("-", ""),
                default=0
                )
                if x else 0
        },
        "total_players": {
            **base_config,
            "key": "player",
            "transform": lambda x: ScrapingEngine.int_validation(
                x.get_text(strip=True)
                .replace(".", "")
                .replace("-", ""),
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
            "transform": lambda x: ScrapingEngine.float_validation(
                x.get_text(strip=True)
                .replace(",", ".")
                .replace(" %", "")
                )
                if x else 0.0
        },
        "game_ratio_of_foreign_players": {
            **base_config,
            "key": "game_ratio_of_foreign_players",
            "transform": lambda x: ScrapingEngine.float_validation(
                x.get_text(strip=True)
                .replace(",", ".")
                .replace(" %", "")
                )
                if x else 0.0
        },
        "goals_per_match": {
            **base_config,
            "key": "goals_per_match",
            "transform": lambda x: ScrapingEngine.float_validation(
                x.get_text(strip=True)
                .replace(",", ".")
                )
                if x else 0.0
        },
        "average_market_value": {
            **base_config,
            "key": "average_market_value",
            "transform": lambda x: ScrapingEngine.parse_currency_to_float(
                x.get_text(strip=True)
                )
                if x else 0.0
        },
        "total_value": {
            **base_config,
            "key": "total_value",
            "transform": lambda x: ScrapingEngine.parse_currency_to_float(
                x.get_text(strip=True)
                )
                if x else 0.0
        }
    }

    def __init__(self, scraping_engine: ScrapingEngine, data_manager: DataManager):
        self.scraping_engine = scraping_engine
        self.data_manager = DataManager(http_client=scraping_engine.http_client)


    def process_league_season(self, league: League, region: Region, team_manager: TeamManager) -> None:
        # logging.info(f"Iniciando el procesamiento de temporadas para la liga: {league.competition}")
        seasons = self.scraping_engine.get_seasons(league.url_league)
        if not seasons:
            logging.warning(f"No se encontraron temporadas para la liga: {league.competition}")
            return

        # Filtro TEMPORAL para solo procesar la temporada 2024
        seasons = [season for season in seasons if season == 2024]

        for season in seasons:
            season_key = f"{season}/{season + 1}"
            # logging.info(f"Procesando temporada: {season_key} para la liga: {league.competition}")

            try:
                league.season = season

                # Construimos la URL dinámica para la temporada
                season_url = f"{league.url_league}/plus/?saison_id={season}"
                team_response = self.scraping_engine.http_client.make_request(season_url)

                if not team_response:
                    logging.warning(f"No se pudo obtener el HTML de la liga: {season_url}")
                    continue

                team_soup = BeautifulSoup(team_response.content, "html.parser")
                team_table = team_soup.find("table", {"class": "items"})

                if not team_table:
                    logging.warning(f"No se encontró la tabla de equipos en la liga: {season_url}")
                    continue

                # Llamamos a get_team_data en el objeto correcto (TeamManager)
                teams = team_manager.get_team_data(
                    table=team_table,
                    min_columns=5,
                    region=region,
                    league=league
                )

                # Agregamos los equipos a la temporada correspondiente
                for team in teams:
                    league.add_team_to_season(
                        season_key=season_key,
                        team=team
                    )
                    # logging.info(f"Equipo '{team.team_name}' añadido a la temporada '{season_key}'.")

                logging.info(f"Se procesaron {len(teams)} equipos para la temporada: {season_key}")

            except Exception as e:
                logging.error(f"Error al procesar la temporada {season_key} para la liga {league.competition}: {e}")


    def extract_cell_value(
            self,
            headers,
            col,
            key,
            offset: int = 2,
            default=None,
            transform=lambda x: x
    ):
        """
        Extrae el valor de una celda de la tabla según el encabezado y aplica una transformación opcional.

        Args:
            headers (dict): Diccionario de encabezados.
            col (list): Lista de celdas de la fila.
            key (str): Clave del encabezado.
            offset (int): Desplazamiento opcional para la columna.
            default: Valor predeterminado si no se encuentra la celda.
            transform (callable): Función para transformar el valor extraído.

        Returns:
            El valor transformado o el valor predeterminado.
        """
        try:
            cell = col[headers[key] + offset] if headers.get(key) is not None else None
            return transform(cell) if cell else default

        except (IndexError, AttributeError) as e:
            logging.warning(f"Error al extraer el valor de la celda: {e}")
            return default


    def get_league_data(
            self,
            table: BeautifulSoup,
            min_columns: int,
            region_id: str

    ) -> List[League]:
        """
        Extrae todos los datos válidos de una tabla HTML y devuelve una lista de objetos League.
        Solo incluye filas que tienen al menos `min_columns` columnas.

        Args:
            table (BeautifulSoup): Tabla HTML parseada.
            min_columns (int): Número mínimo de columnas requeridas para procesar una fila.
            region_id (str): ID de la región a la que pertenece la liga.

        Returns:
            List[League]: Lista de objetos League con los datos extraídos.
        """
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

        leagues = []
        for row in rows:
            col = row.find_all("td")
            if not col or len(col) < min_columns:
                continue

            try:
                # Extraer valores dinámicamente usando el diccionario de configuración
                extracted_values = {
                    field: self.extract_cell_value(
                        headers=headers,
                        col=col,
                        key=config["key"],
                        offset=config.get("offset", 0),
                        default=config.get("default", None),
                        transform=config["transform"]
                    )
                    for field, config in self.league_field_config.items()
                }

                # Instancia de LeagueStats
                league_stats = LeagueStats(
                    fk_league=extracted_values["competition_url"].split("/")[-1] if extracted_values["competition_url"] else None,
                    fk_region=region_id,
                    total_clubs=extracted_values["total_clubs"],
                    total_players=extracted_values["total_players"],
                    avg_age=extracted_values["avg_age"],
                    foreigners=extracted_values["foreigners"],
                    game_ratio_of_foreign_players=extracted_values["game_ratio_of_foreign_players"],
                    goals_per_match=extracted_values["goals_per_match"],
                    average_market_value=extracted_values["average_market_value"],
                    total_value=extracted_values["total_value"]
                )

                # Instancia de League
                league = League(
                    id_league=league_stats.fk_league,
                    competition=extracted_values["competition_name"],
                    season=0,
                    country=extracted_values["country_name"],
                    url_league=extracted_values["competition_url"],
                    stats=league_stats,
                    teams={
                        "fk_region": region_id,
                        "fk_league": extracted_values["competition_url"].split("/")[-1] if extracted_values["competition_url"] else None,
                        "url_league": extracted_values["competition_url"]
                    }
                )

                leagues.append(league)

            except Exception as e:
                logging.warning(f"No se ha podido extraer los campos de la fila: {e}")
                continue

        # logging.info(f"Datos extraídos de la tabla: {len(leagues)} filas.")
        return leagues