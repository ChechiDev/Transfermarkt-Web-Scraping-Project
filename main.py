from scraping.ws_httpClient import HTTPClient
from scraping.ws_urls import TransfermarktURLManager
from scraping.ws_engine import ScrapingEngine
from scraping.ws_region import RegionManager
from scraping.ws_dataManager import DataManager
from scraping.ws_leagues import LeagueManager
from scraping.ws_teams import TeamManager
from config.exceptions import logging

def initialize_scraping():
    try:
        logging.info("Inicializando el proceso de scraping...")

        # Inicialización de componentes
        http_client = HTTPClient()
        scraping_engine = ScrapingEngine(http_client)
        url_manager = TransfermarktURLManager(http_client, scraping_engine)
        data_manager = DataManager(http_client)
        league_manager = LeagueManager(scraping_engine, data_manager)
        team_manager = TeamManager(scraping_engine, data_manager)
        region_manager = RegionManager(http_client, league_manager, team_manager)

        logging.info("Componentes inicializados correctamente.")

        # Procesa todas las regiones configuradas en el URL Manager
        for region_key, region_data in url_manager.urls.items():
            logging.info(f"Procesando región: {region_key}")

            region = region_manager.create_region(region_key, region_data)
            logging.debug(f"Región creada: {region}, tipo: {type(region)}")

            region_manager.process_region(region, region_data)

            data_manager.add_region(region)
            logging.info(f"Región añadida a DataManager: {region_key}")

        # Exportamos a JSON
        output_file = "all_regions_with_leagues_and_teams.json"
        data_manager.to_json(output_file)

        logging.info(f"Archivo JSON generado correctamente: {output_file}")

    except Exception as e:
        logging.error(f"Error durante el proceso de scraping: {e}")

if __name__ == "__main__":
    initialize_scraping()