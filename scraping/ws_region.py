import logging
from scraping.ws_entities import Region, RegionStats, Country, League, LeagueStats
from scraping.ws_engine import ScrapingEngine
from bs4 import BeautifulSoup
from typing import Dict, Any

class RegionManager:
    def __init__(self, http_client, league_manager, team_manager):
        self.http_client = http_client
        self.league_manager = league_manager
        self.team_manager = team_manager

    def create_region(self, region_key: str, region_data: Dict[str, Any]) -> Region:
        logging.info(f"Creando región: {region_key}")

        region_stats = RegionStats(
            fk_region=region_key,
            avg_age=0,
            avg_height=0,
            avg_weight=0,
            avg_salary=0,
            average_market_value=0,
            total_value=0,
        )

        countries = {}

        return Region(
            id_region=region_key,
            region_name=region_data["region_name"],
            url_region=region_data["url_region"][0],
            countries=countries,
            stats=region_stats
        )

    def process_region(self, region: Region, region_data: Dict[str, Any]) -> None:
        for page_number, url in enumerate(region_data["url_region"], start=1):
            response = self.http_client.make_request(url)

            if not response:
                logging.warning(f"No se pudo obtener el HTML de la URL: {url}")
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find("table", {"class": "items"})

            if not table:
                logging.warning(f"No se encontró la tabla de ligas en la URL: {url}")
                continue

            # Extraemos la info de los paises:
            try:
                country_info = self.league_manager.scraping_engine.get_country_info(table)

                for country_id, country_data in country_info.items():
                    country = Country(
                        id_country=country_id,
                        country_name=country_data["country_name"],
                        country_flag=country_data["country_flag"]
                    )
                    region.add_country(country)

            except Exception as e:
                logging.error(f"Error al extraer información de países para la región {region.id_region}: {e}")


            # Obtenemos el diccionario provisional de competition -> tier
            competition_to_tier = self.league_manager.scraping_engine.get_league_tier(table)

            # Usa LeagueManager para extraer las ligas
            try:
                leagues = self.league_manager.get_league_data(
                    table,
                    min_columns=5,
                    region_id=region.id_region,
                    region_countries=region.countries
                )

            except Exception as e:
                logging.error(f"Error al obtener las ligas para la región {region.id_region}: {e}")
                return

            # Validar que leagues sea una lista válida
            if not leagues:
                logging.warning(f"No se encontraron ligas en la tabla para la región {region.id_region}.")
                return

            # Asignar el tier correcto a cada liga y agregarla a la región
            for league in leagues:
                if not isinstance(league, League):
                    raise TypeError(f"Se esperaba una instancia de League, pero se recibió {type(league)}")

                tier = competition_to_tier.get(league.competition, "Unknown Tier")
                region.add_league(tier, league)

                # Procesamos las temporadas y equipos de cada liga
                self.league_manager.process_league_season(league, region, self.team_manager)

            logging.info(f"Página {page_number} de {len(region_data['url_region'])}: {len(leagues)} ligas extraídas.")

        # Calculamos las estadísticas de la región
        if region.leagues:
            stats_to_calculate = ["average_market_value", "total_value"]

            for stat_name in stats_to_calculate:
                logging.debug(f"Calculando estadística: {stat_name} para región: {region.id_region}")

                # Validamos que todas las ligas sean instancias de League
                for tier, leagues_in_tier in region.leagues.items():
                    for league_id, league in leagues_in_tier.items():
                        if not isinstance(league, League):
                            raise TypeError(f"Se esperaba una instancia de League, pero se recibió {type(league)} para la liga {league_id}")

                        if not isinstance(league.stats, LeagueStats):
                            raise TypeError(f"Se esperaba una instancia de LeagueStats, pero se recibió {type(league.stats)} para la liga {league_id}")

                # Llamar al método calculate_avg_value
                try:
                    ScrapingEngine.calculate_avg_value(
                        region.leagues,
                        region.stats,
                        stat_name
                    )

                except Exception as e:
                    logging.error(f"Error al calcular {stat_name} para la región {region.id_region}: {e}")
                    continue

            logging.info(f"Estadísticas calculadas para la región: {region.id_region}")