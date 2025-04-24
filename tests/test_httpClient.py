import unittest
from scraping.ws_httpClient import HTTPClient
from scraping.ws_urls import TransfermarktURLManager
from scraping.ws_engine import ScrapingEngine

class TestHTTPClient(unittest.TestCase):
    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        self.http_client = HTTPClient()
        self.scraping_engine = ScrapingEngine(self.http_client)
        self.url_manager = TransfermarktURLManager(self.http_client, self.scraping_engine)

    def test_get_html_from_url_manager(self):
        """
        Prueba que el cliente HTTP pueda obtener HTML desde una URL del gestor de URLs.
        """
        # Obtener la URL de la región 'EUR1' desde el gestor de URLs
        region_id = "EUR1"
        test_url = self.url_manager.url[region_id]["url"].format(page=1)

        # Realizar la solicitud HTTP
        html = self.http_client.get_html(test_url)
        if html:
            print(f"Conexión exitosa a la URL: {test_url}")
            print(f"Título de la página: {html.title.string if html.title else 'No disponible'}")
        else:
            print(f"No se pudo obtener el HTML de la URL: {test_url}")

        # Verificar que el HTML no sea None
        self.assertIsNotNone(html, "El cliente HTTP no devolvió contenido HTML.")
        # Verificar que el contenido descargado contiene la etiqueta <html>
        self.assertIn("<html", str(html), "El contenido descargado no parece ser HTML.")

if __name__ == "__main__":
    unittest.main()