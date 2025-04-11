from scraping.wscrap_engine import HttpClient, Scraper
from scraping.wscrap_league import LeagueScraper
from config.headers import headers

# Crear instancia del cliente HTTP
http_client = HttpClient(headers=headers)

# Probar el motor (Scraper)
def test_engine():
    print("Testing (Scraper):")
    scraper = Scraper(http_client)

    # Cargar las URLs desde el archivo .env
    scraper.get_url_from_env()

    # Probar la construcción de una URL
    try:
        url = scraper.build_url("url_tmkt_eur_leagues", page=1)
        print(f"URL construida correctamente: {url}")
    except ValueError as e:
        print(f"Error al construir la URL: {e}")

    # Probar la descarga de HTML
    html = http_client.get_html(url)
    if html:
        print("HTML descargado correctamente.")
        print(f"Título de la página: {html.title.text}")
    else:
        print("Error al descargar el HTML.")

    # Probar la detección del número total de páginas
    try:
        total_pages = scraper.get_total_pages(url)
        print(f"Número total de páginas detectado: {total_pages}")
    except Exception as e:
        print(f"Error al detectar el número total de páginas: {e}")

# Probar el scraper específico (LeagueScraper)
def test_league_scraper():
    print("\nTesting  (LeagueScraper)")
    league_scraper = LeagueScraper(http_client)

    # Cargar las URLs desde el archivo .env
    league_scraper = LeagueScraper(http_client)

    # Cargar las URLs desde el archivo .env
    league_scraper.get_url_from_env()

    # Depuración: Imprimir las claves cargadas
    print(f"Claves cargadas desde .env: {league_scraper.urls}")

    # Depuración: Imprimir la clave que se pasa
    url_key = "url_tmkt_eur_leagues"
    print(f"Clave pasada a get_leagues: '{url_key}'")

    # Obtener las ligas desde múltiples páginas
    try:
        leagues = league_scraper.get_leagues(url_key)
        if leagues:
            print(f"{len(leagues)} ligas encontradas:")
            for league in leagues[:25]:
                print(league)
        else:
            print("No se encontraron ligas.")
    except Exception as e:
        print(f"Error al obtener las ligas: {e}")

# Llamar a las funciones de prueba
if __name__ == "__main__":
    test_engine()
    test_league_scraper()