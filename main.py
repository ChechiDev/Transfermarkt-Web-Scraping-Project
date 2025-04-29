from scraping.ws_httpClient import HTTPClient
from scraping.ws_urls import TransfermarktURLManager
from scraping.ws_engine import ScrapingEngine

def main():
    # Inicializar el cliente HTTP
    http_client = HTTPClient()
    # Inicializar el motor de scraping
    scraping_engine = ScrapingEngine(http_client)
    # Inicializar el gestor de URLs
    url_manager = TransfermarktURLManager(http_client, scraping_engine)

    # Obtener la URL de la región 'EUR1' desde el gestor de URLs
    region_id = "EUR1"
    test_url = url_manager.url[region_id]["url"].format(page=1)

    print(f"Conectando a la URL: {test_url}")

    # Realizar la solicitud HTTP
    html = http_client.get_html(test_url)

    # Verificar si se obtuvo el HTML
    if html:
        print("Conexión exitosa. HTML obtenido.")
        # Mostrar el título de la página si está disponible
        title = html.title.string if html.title else "No disponible"
        print(f"Título de la página: {title}")
    else:
        print("No se pudo obtener el HTML de la URL.")

if __name__ == "__main__":
    main()