from scraping.ws_httpClient import HttpClient
from scraping.ws_engine import ScrapingEngine
from scraping.ws_leagues import LeagueScraper
from scraping.ws_urls import TransferMarktURLManager

def main():
    # Inicializar HttpClient
    http_client = HttpClient()
    print("HttpClient inicializado.")

    # Inicializar ScrapingEngine
    scraping_engine = ScrapingEngine(http_client)
    print("ScrapingEngine inicializado.")

    # Inicializar TransferMarktURLManager
    url_manager = TransferMarktURLManager(scraping_engine, http_client)
    print("TransferMarktURLManager inicializado.")

    # Inicializar LeagueScraper
    league_scraper = LeagueScraper(http_client)
    print("LeagueScraper inicializado.")

    # Configurar la región para scraping
    region = "europe"  # Cambiar a "america", "africa", "asia" según sea necesario
    try:
        # Actualizar los datos de la región (end_page y table_header)
        print(f"Actualizando datos para la región: {region}")
        url_manager.update_region_data(region)
        print(f"Datos actualizados para la región '{region}':")
        print(f"Total de páginas: {url_manager.urls[region]['end_page']}")
        print(f"Encabezados de la tabla: {url_manager.urls[region]['table_header']}")

        # Obtener HTML de la primera página
        url = url_manager.urls[region]["url"].format(page=1)
        html = http_client.get_html(url)

        if html:
            # Extraer tabla y encabezados
            table = html.find("table")
            league_scraper.extract_headers_from_table(table)

            # Verificar los atributos asignados
            print("Atributos asignados en LeagueScraper:")
            print(f"Competition index: {league_scraper.competition}")
            print(f"Country index: {league_scraper.country}")
            print(f"Clubs index: {league_scraper.clubs}")
            print(f"Players index: {league_scraper.player}")
            print(f"Avg Age index: {league_scraper.avg_age}")
            print(f"Foreigners index: {league_scraper.foreigners}")
            print(f"Goals per Match index: {league_scraper.goals_per_match}")
            print(f"Average Market Value index: {league_scraper.average_market_value}")
            print(f"Total Value index: {league_scraper.total_value}")
        else:
            print(f"No se pudo obtener el HTML para la región '{region}'.")

    except Exception as e:
        print(f"Error durante el scraping de la región '{region}': {e}")

if __name__ == "__main__":
    main()