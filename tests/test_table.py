import unittest
from scraping.ws_httpClient import HTTPClient
from scraping.ws_engine import ScrapingEngine
from scraping.ws_urls import TransfermarktURLManager
from scraping.ws_entities import League
from config.exceptions import HTTPClientError

class TestLeagueExtraction(unittest.TestCase):
    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        self.http_client = HTTPClient()
        self.scraping_engine = ScrapingEngine(self.http_client)
        self.url_manager = TransfermarktURLManager(self.http_client, self.scraping_engine)

    def test_extract_leagues_from_regions(self):
        """
        Prueba la extracción de ligas desde las tablas de todas las regiones configuradas.
        """
        for region_key, region_data in self.url_manager.urls.items():
            print(f"\n=== Probando región: {region_key} ===")
            try:
                # Obtener las URLs de la región
                urls = region_data["url"]
                print(f"URLs: {urls}")

                # Extraer ligas de la región
                leagues = self.scraping_engine.extract_leagues_from_region(urls, region_key)

                # Verificar que se extrajeron ligas
                self.assertIsInstance(leagues, list, "Los datos extraídos no son una lista.")
                self.assertGreater(len(leagues), 0, f"No se extrajeron ligas para la región {region_key}.")

                # Mostrar las primeras ligas extraídas
                print(f"Ligas extraídas ({len(leagues)}):")
                for league in leagues[:5]:  # Mostrar solo las primeras 5 ligas
                    print(f"- {league.competition} ({league.id_league}) - {league.country}")

            except HTTPClientError as e:
                self.fail(f"Error al realizar la solicitud HTTP para la región {region_key}: {e}")
            except Exception as e:
                self.fail(f"Error inesperado al procesar la región {region_key}: {e}")

if __name__ == "__main__":
    unittest.main()