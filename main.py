import os
from scraping.ws_httpClient import HTTPClient
from scraping.ws_engine import ScrapingEngine
from scraping.ws_urls import TransfermarktURLManager
from scraping.ws_dataManager import DataManager
from scraping.ws_leagues import LeagueManager
from scraping.ws_teams import TeamManager
from scraping.ws_entities import Region, RegionStats
import logging
from bs4 import BeautifulSoup

def initialize_scraping():
    try:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        logging.info("Inicializando el proceso de scraping...")

        http_client = HTTPClient()
        scraping_engine = ScrapingEngine(http_client)
        url_manager = TransfermarktURLManager(http_client, scraping_engine)
        data_manager = DataManager(http_client)
        league_manager = LeagueManager(scraping_engine, data_manager)
        team_manager = TeamManager(scraping_engine, data_manager)

        # Procesa todas las regiones configuradas en el URL Manager
        for region_key, region_data in url_manager.urls.items():
            logging.info(f"Procesando región: {region_key}")

            # Instancia a la Región:
            region_stats = RegionStats(
                fk_region=region_key,
                avg_age=0,
                avg_height=0,
                avg_weight=0,
                avg_salary=0,
                average_market_value=0,
                total_value=0,
            )

            # Crea la región
            region = Region(
                id_region=region_key,
                region_name=region_data["region_name"],
                url_region=region_data["url_region"][0],
                stats=region_stats
            )

            # Extraer ligas de la región
            for page_number, url in enumerate(region_data["url_region"], start=1):
                response = http_client.make_request(url)
                if not response:
                    logging.warning(f"No se pudo obtener el HTML de la URL: {url}")
                    continue

                soup = BeautifulSoup(response.content, "html.parser")
                table = soup.find("table", {"class": "items"})
                if not table:
                    logging.warning(f"No se encontró la tabla de ligas en la URL: {url}")
                    continue

                # Usa LeagueManager para extraer las ligas
                leagues = league_manager.get_league_data(table, min_columns=5, region_id=region_key)
                for league in leagues:
                    region.add_league(league)

                    # Extraer equipos de cada liga
                    logging.info(f"Procesando equipos para la liga: {league.competition}")
                    team_response = http_client.make_request(league.url_league)
                    if not team_response:
                        logging.warning(f"No se pudo obtener el HTML de la liga: {league.url_league}")
                        continue

                    team_soup = BeautifulSoup(team_response.content, "html.parser")
                    team_table = team_soup.find("table", {"class": "items"})
                    if not team_table:
                        logging.warning(f"No se encontró la tabla de equipos en la liga: {league.url_league}")
                        continue

                    # Usar TeamManager para extraer los equipos
                    teams = team_manager.get_team_data(team_table, min_columns=5, region=region, league=league)
                    for team in teams:
                        logging.info(f"Equipo extraído: {team.team_name}, URL: {team.url_team}, Total Players: {team.stats.total_players}")
                        league.teams[team.team_name] = team

                # os.system('cls' if os.name == 'nt' else 'clear')
                logging.info(f"Página {page_number} de {len(region_data['url_region'])}: {len(leagues)} filas extraídas.")

            # Calculo promedio de las estadísticas de la región
            if region.leagues:
                stats_to_calculate = ["average_market_value", "total_value"]

                for stat_name in stats_to_calculate:
                    ScrapingEngine.calculate_avg_value(
                        region.leagues,
                        region.stats,
                        stat_name
                    )

                # Añade la región a DataManager
                data_manager.add_region(region)

        # Exportamos a JSON
        output_file = "all_regions_with_leagues_and_teams.json"
        data_manager.to_json(output_file)
        logging.info(f"Archivo JSON generado correctamente: {output_file}")

    except Exception as e:
        logging.error(f"Error durante el proceso de scraping: {e}")

if __name__ == "__main__":
    initialize_scraping()