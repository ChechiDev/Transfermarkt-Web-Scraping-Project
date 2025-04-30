from scraping.ws_httpClient import HTTPClient
from scraping.ws_engine import ScrapingEngine
from scraping.ws_urls import TransfermarktURLManager
from scraping.ws_dataManager import DataManager
from scraping.ws_entities import Region, RegionStats

def generate_json_with_all_regions_and_leagues():
    # Inicializar las clases principales del proyecto
    http_client = HTTPClient()
    scraping_engine = ScrapingEngine(http_client)
    url_manager = TransfermarktURLManager(http_client, scraping_engine)
    data_manager = DataManager()

    # Procesar todas las regiones configuradas en el URL Manager
    for region_key, region_data in url_manager.urls.items():
        print(f"\n=== Procesando región: {region_key} ===")

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
            url=region_data["url"][0],  # Usar la primera URL como referencia
            stats=region_stats
        )

        # Extraer ligas de la región
        leagues = scraping_engine.extract_leagues_from_region(region_data["url"], region_key)
        for league in leagues:
            region.add_league(league)

        # Añadir la región al DataManager
        data_manager.add_region(region)

    # Exportar los datos generados a un archivo JSON
    output_file = "all_regions_with_leagues.json"
    data_manager.to_json(output_file)

    print(f"Archivo JSON generado correctamente: {output_file}")

if __name__ == "__main__":
    generate_json_with_all_regions_and_leagues()