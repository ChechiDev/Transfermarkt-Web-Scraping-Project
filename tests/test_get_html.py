from scraping.wscrap_engine import HttpClient
from dotenv import load_dotenv
import os

def test_get_html():
    """
    Prueba que el método get_html descargue correctamente el HTML desde una URL válida definida en .env.
    """
    # Cargamos las variables de entorno desde el archivo .env
    load_dotenv()

    # Obtenemos la URL desde el archivo .env
    url = os.getenv("URL_TMKT_EUR_LEAGUES").format(page=1)
    assert url is not None, "La URL no se encontró en el archivo .env."

    # Creamos una instancia de HttpClient
    http_client = HttpClient()

    # Llamamos al método get_html
    html = http_client.get_html(url)

    # Verificamos si se descargó el HTML
    if html:
        print("HTML descargado correctamente.")
        print(f"Título de la página: {html.title.text}")
    else:
        print("No se pudo descargar el HTML. Verifica los encabezados o las restricciones del servidor.")

if __name__ == "__main__":
    print("Ejecutando test_get_html...")
    test_get_html()
    print("Prueba completada.")