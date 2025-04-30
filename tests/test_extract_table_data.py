import unittest
from scraping.ws_httpClient import HTTPClient
from scraping.ws_engine import ScrapingEngine
from scraping.ws_dataManager import DataManager
from scraping.ws_urls import TransfermarktURLManager
from config.exceptions import HTTPClientError

class TestExtractTableData(unittest.TestCase):
    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        self.http_client = HTTPClient()
        self.scraping_engine = ScrapingEngine(self.http_client)
        self.data_manager = DataManager(self.http_client)
        self.url_manager = TransfermarktURLManager(self.http_client, self.scraping_engine)

    def test_extract_table_data_from_real_urls(self):
        """
        Prueba la función extract_table_data con HTML real desde las URLs configuradas.
        """
        for region_key, region_data in self.url_manager.urls.items():
            print(f"\n=== Probando región: {region_key} ===")
            try:
                # Obtener la primera URL de la región
                url = region_data["url"][0]
                print(f"URL: {url}")

                # Descargar el HTML de la página
                html = self.http_client.get_html(url)
                if not html:
                    self.fail(f"No se pudo obtener el HTML de la URL: {url}")

                # Buscar la tabla con la clase "items"
                table = html.find("table", {"class": "items"})
                if not table:
                    self.fail(f"No se encontró la tabla con la clase 'items' en la URL: {url}")

                # Calcular el valor de min_columns usando measure_row_lengths
                _, max_length = self.scraping_engine.measure_row_lengths(table)
                if max_length == 0:
                    self.fail(f"No se pudo calcular el valor de min_columns para la tabla en la URL: {url}")

                # Extraer los datos de la tabla usando el valor de min_columns
                table_data = self.data_manager.extract_league_table_data(table, min_columns=max_length)

                # Verificar que se extrajeron datos
                self.assertIsInstance(table_data, list, "Los datos extraídos no son una lista.")
                self.assertGreater(len(table_data), 0, f"No se extrajeron filas de la tabla para la región {region_key}.")

                # Mostrar las primeras filas extraídas
                print(f"Datos extraídos ({len(table_data)} filas):")
                for row in table_data[:5]:  # Mostrar solo las primeras 5 filas
                    print(row)

            except HTTPClientError as e:
                self.fail(f"Error al realizar la solicitud HTTP para la región {region_key}: {e}")
            except Exception as e:
                self.fail(f"Error inesperado al procesar la región {region_key}: {e}")

if __name__ == "__main__":
    unittest.main()