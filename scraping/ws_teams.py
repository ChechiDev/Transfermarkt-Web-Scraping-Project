import re
import logging
from bs4 import BeautifulSoup
from scraping.ws_engine import ScrapingEngine
from scraping.ws_entities import Team, TeamStats, League, Region
from scraping.ws_dataManager import DataManager
from typing import List


class TeamManager:
    base_url = "https://www.transfermarkt.com"

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
            "key": "name",
            "transform": lambda x: (
                TeamManager.base_url + x.find("a")["href"]
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
            "key": "average_market_value",
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

    def __init__(self, scraping_engine: ScrapingEngine, data_manager: DataManager):
        self.scraping_engine = scraping_engine
        self.data_manager = data_manager

    def extract_cell_value(
            self,
            headers,
            col,
            key,
            offset: int = 1,
            default=None,
            transform=lambda x: x
    ):
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

                teams.append(team)

            except Exception as e:
                logging.warning(f"No se ha podido extraer los campos de la fila: {e}")
                continue

        # logging.info(f"Datos extraídos de la tabla: {len(teams)} filas.")
        return teams