import unittest
from bs4 import BeautifulSoup
from scraping.ws_engine import ScrapingEngine
from scraping.ws_httpClient import HTTPClient
from config.exceptions import HTTPClientError

class TestGetTableHeaders(unittest.TestCase):
    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        self.http_client = HTTPClient()
        self.scraping_engine = ScrapingEngine(self.http_client)

    def test_get_table_headers_real_page(self):
        """
        Prueba el método get_table_headers con una página real de Transfermarkt.
        """
        # URL de ejemplo (puedes reemplazarla con una URL válida de Transfermarkt)
        url = "https://www.transfermarkt.com/wettbewerbe/europa"

        try:
            # Obtener el HTML de la página
            response = self.http_client.make_request(url)
            if not response:
                self.fail(f"No se pudo obtener el HTML de la URL: {url}")

            html = BeautifulSoup(response.content, "html.parser")

            # Buscar la tabla con la clase "items"
            table = html.find("table", {"class": "items"})
            if not table:
                self.fail(f"No se encontró la tabla con la clase 'items' en la URL: {url}")

            # Ejecutar el método get_table_headers
            headers = self.scraping_engine.get_table_headers(table)

            # Verificar que los encabezados sean un diccionario no vacío
            self.assertIsInstance(headers, dict, "Los encabezados no son un diccionario.")
            self.assertGreater(len(headers), 0, "No se encontraron encabezados en la tabla.")

            print(f"Encabezados extraídos: {headers}")

        except HTTPClientError as e:
            self.fail(f"Error al realizar la solicitud HTTP: {e}")

    def test_get_table_headers_mocked_html(self):
        """
        Prueba el método get_table_headers con un HTML simulado.
        """
        # HTML simulado de una tabla
        html = """
        <table class="items">
            <thead>
                <tr>
                    <th>Competition</th>
                    <th>Country</th>
                    <th>Teams</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Premier League</td>
                    <td>England</td>
                    <td>20</td>
                </tr>
            </tbody>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"class": "items"})

        # Ejecutar el método get_table_headers
        headers = self.scraping_engine.get_table_headers(table)

        # Verificar los resultados
        expected_headers = {
            "competition": 0,
            "country": 1,
            "teams": 2
        }
        self.assertEqual(headers, expected_headers, "Los encabezados extraídos no coinciden con los esperados.")

if __name__ == "__main__":
    unittest.main()