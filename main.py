from scraping.ws_httpClient import HTTPClient
from scraping.ws_engine import ScrapingEngine
from scraping.ws_urls import TransfermarktURLManager
from scraping.ws_dataManager import DataManager
from scraping.ws_leagues import LeagueManager
from scraping.ws_entities import Region, RegionStats
import logging
from bs4 import BeautifulSoup

def initialize_scraping():
    """
    Inicializa el proceso de scraping y descarga de datos.
    """
    try:
        # Configurar logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        logging.info("Inicializando el proceso de scraping...")

        # Inicializar las clases principales del proyecto
        http_client = HTTPClient()
        scraping_engine = ScrapingEngine(http_client)
        url_manager = TransfermarktURLManager(http_client, scraping_engine)
        data_manager = DataManager(http_client)
        league_manager = LeagueManager(scraping_engine, data_manager)

        # Procesar todas las regiones configuradas en el URL Manager
        for region_key, region_data in url_manager.urls.items():
            logging.info(f"Procesando región: {region_key}")

            # Crear estadísticas ficticias para la región
            region_stats = RegionStats(
                fk_region=region_key,
                avg_age=0,  # Valor ficticio
                avg_height=0,  # Valor ficticio
                avg_weight=0,  # Valor ficticio
                avg_salary=0,  # Valor ficticio
                avg_market_value=0  # Valor ficticio
            )

            # Crear la región
            region = Region(
                id_region=region_key,
                region_name=region_data["region_name"],
                url=region_data["url"][0],
                stats=region_stats
            )

            # Extraer ligas de la región
            for url in region_data["url"]:
                response = http_client.make_request(url)
                if not response:
                    logging.warning(f"No se pudo obtener el HTML de la URL: {url}")
                    continue

                soup = BeautifulSoup(response.content, "html.parser")
                table = soup.find("table", {"class": "items"})
                if not table:
                    logging.warning(f"No se encontró la tabla de ligas en la URL: {url}")
                    continue

                # Usar LeagueManager para extraer las ligas
                leagues = league_manager.get_league_data(table, min_columns=5, region_id=region_key)
                for league in leagues:
                    region.add_league(league)

            # Añadir la región al DataManager
            data_manager.add_region(region)

        # Exportar los datos generados a un archivo JSON
        output_file = "all_regions_with_leagues.json"
        data_manager.to_json(output_file)
        logging.info(f"Archivo JSON generado correctamente: {output_file}")

    except Exception as e:
        logging.error(f"Error durante el proceso de scraping: {e}")

if __name__ == "__main__":
    initialize_scraping()