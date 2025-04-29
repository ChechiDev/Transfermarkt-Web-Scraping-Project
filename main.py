from scraping.ws_httpClient import HTTPClient
from scraping.ws_engine import ScrapingEngine
from scraping.ws_urls import TransfermarktURLManager
import logging

def main():
    http_client = HTTPClient()
    scraping_engine = ScrapingEngine(http_client)
    url_manager = TransfermarktURLManager(http_client, scraping_engine)

    # Procesar todas las regiones configuradas
    for region_key, region_data in url_manager.urls.items():
        print(f"\n=== Región: {region_key} ===")
        print(f"Nombre de la región: {region_data.get('region_name', 'No disponible')}")
        print(f"Total de páginas: {region_data.get('end_page', 'No disponible')}")
        print(f"Encabezados de tabla: {region_data.get('table_header', 'No disponible')}")

        # Verificar si hay URLs generadas para esta región
        urls = region_data.get('url', [])
        if urls:
            print(f"URLs generadas ({len(urls)}):")
            for url in urls[:5]:  # Mostrar solo las primeras 5 URLs
                print(f"  - {url}")
            if len(urls) > 5:
                print(f"  ... y {len(urls) - 5} más.")
        else:
            print("No se generaron URLs para esta región.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Error al ejecutar el programa principal: {e}")