import unittest
from scraping.ws_entities import Region, Transfermarkt
from scraping.ws_urls import TransfermarktURLManager

class TestEntities(unittest.TestCase):
    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        # Inicializar el gestor de URLs
        self.url_manager = TransfermarktURLManager(None, None)

    def test_url_manager_data(self):
        """
        Prueba que el gestor de URLs contenga datos válidos.
        """
        print("\n=== Probando datos del gestor de URLs ===")
        for region_id, region_data in self.url_manager.url.items():
            print(f"ID: {region_id}, Datos: {region_data}")
        self.assertIn("EUR1", self.url_manager.url, "La región 'EUR1' no está en el gestor de URLs.")
        self.assertIn("region_name", self.url_manager.url["EUR1"], "Falta 'region_name' en los datos de 'EUR1'.")
        self.assertIn("url", self.url_manager.url["EUR1"], "Falta 'url' en los datos de 'EUR1'.")

    def test_region_instance(self):
        """
        Prueba que se puedan crear instancias de la clase Region correctamente.
        """
        print("\n=== Probando creación de instancia de Region ===")
        region_data = self.url_manager.url["EUR1"]
        region = Region(
            id_region="EUR1",
            region_name=region_data["region_name"],
            url=region_data["url"]
        )
        print(region)
        self.assertEqual(region.id_region, "EUR1", "El ID de la región no coincide.")
        self.assertEqual(region.region_name, "Europe", "El nombre de la región no coincide.")
        self.assertTrue(region.url.startswith("https://"), "La URL de la región no es válida.")

    def test_transfermarkt_instance(self):
        """
        Prueba que se pueda crear una instancia de Transfermarkt con los datos del gestor de URLs.
        """
        print("\n=== Probando creación de instancia de Transfermarkt ===")
        # Crear un diccionario de regiones basado en los datos del gestor de URLs
        regions = {
            region_id: Region(
                id_region=region_id,
                region_name=region_data["region_name"],
                url=region_data["url"]
            )
            for region_id, region_data in self.url_manager.url.items()
        }

        # Crear una instancia de Transfermarkt
        transfermarkt = Transfermarkt(regions=regions)

        # Verificar que las regiones se cargaron correctamente
        for region_id, region in transfermarkt.regions.items():
            print(f"ID: {region_id}, Region: {region}")
        self.assertIn("EUR1", transfermarkt.regions, "La región 'EUR1' no está en Transfermarkt.")
        self.assertIsInstance(transfermarkt.regions["EUR1"], Region, "La región 'EUR1' no es una instancia de Region.")
        self.assertEqual(
            transfermarkt.regions["EUR1"].region_name,
            "Europe",
            "El nombre de la región 'EUR1' no coincide en Transfermarkt."
        )

if __name__ == "__main__":
    unittest.main()