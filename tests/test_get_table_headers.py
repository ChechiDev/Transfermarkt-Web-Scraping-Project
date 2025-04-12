from scraping.wscrap_engine import Scraper, HttpClient
from config.headers import headers  # Mantener la importación de los encabezados HTTP

def test_get_table_headers():
    """
    Prueba la extracción de encabezados de una tabla desde una URL configurada.
    """
    # Crear una instancia de HttpClient
    http_client = HttpClient(headers=headers)

    # Crear una instancia del Scraper
    scraper = Scraper(http_client)

    # Cargar las URLs desde el archivo .env
    scraper.get_url_from_env()

    # Clave de la URL en el archivo .env
    url_key = "url_tmkt_eur_leagues"

    # Obtener la tabla desde la URL y extraer los encabezados
    table_class = "items"  # Clase CSS de la tabla
    url = scraper.build_url(url_key)
    print(f"Probando extracción de encabezados desde la URL: {url}")

    table = scraper.get_table(url, table_class)
    if not table:
        print("No se encontró la tabla en la página.")
        return

    # Renombrar la variable para evitar conflictos
    table_headers = scraper.get_table_headers(table)
    print(f"Encabezados extraídos: {table_headers}")

    # Validar que los encabezados no estén vacíos
    assert table_headers, "No se extrajeron encabezados de la tabla."
    print("Prueba completada con éxito.")

# Ejecutar la prueba si se llama directamente
if __name__ == "__main__":
    test_get_table_headers()