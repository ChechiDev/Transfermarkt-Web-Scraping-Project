import unittest
from scraping.ws_httpClient import HttpClient
from scraping.ws_engine import ScrapingEngine
from scraping.ws_leagues import LeagueScraper
from src.ws_urls import TransferMarktURLManager
from src.ws_entities import Region

class TestProcessRowWithRealHTML(unittest.TestCase):
    def setUp(self):
        # Inicializar HttpClient y URL Manager
        self.http_client = HttpClient()
        self.scraping_engine = ScrapingEngine(self.http_client)
        self.url_manager = TransferMarktURLManager(self.scraping_engine, self.http_client)

        # Inicializar LeagueScraper
        self.scraper = LeagueScraper(self.http_client)

        # Configurar región de prueba
        self.region_id = "AFR1"  # Región de África
        self.region_entity = Region(
            id_region=self.region_id,
            region_name="Africa",
            url=self.url_manager.urls[self.region_id]["url"],
            stats=None
        )

    def test_process_row_with_real_html(self):
        # Obtener la URL de la primera página de la región
        url = self.url_manager.urls[self.region_id]["url"].format(page=1)

        # Descargar el HTML de la página
        html = self.http_client.get_html(url)
        self.assertIsNotNone(html, "No se pudo descargar el HTML de la página.")

        # Buscar la tabla en el HTML
        table = html.find("table")
        self.assertIsNotNone(table, "No se encontró ninguna tabla en el HTML.")

        # Extraer encabezados de la tabla
        headers = self.scraper.get_table_headers(table)
        self.assertIn("competition", headers, "El encabezado 'competition' no está en la tabla.")

        # Obtener la primera fila de la tabla
        rows = table.select("tbody tr")
        self.assertGreater(len(rows), 0, "No se encontraron filas en la tabla.")
        first_row = rows[0]

        # Método a probar
        def process_row(row, headers, region_entity):
            # Obtener todas las celdas de la fila
            cells = row.find_all("td")

            # Expandir celdas combinadas (colspan y rowspan)
            cells = ScrapingEngine.expand_cells(cells)

            # Validar que la cantidad de celdas coincida con la cantidad de encabezados
            if len(cells) <= 2:
                return  # Ignorar esta fila

            competition_name = self.scraper.get_competition(row, headers)
            country_name = self.scraper.get_country(row, headers)

            # Procesar el ID de la liga
            competition_index = headers["competition"] - 1
            if competition_index < len(cells):
                link = cells[competition_index].find("a", href=True)
                if link:
                    league_id = link["href"].split("/")[-1]
                    self.scraper.create_league_instance(
                        league_id,
                        competition_name,
                        country_name,
                        region_entity
                    )
                else:
                    print(f"Advertencia: No se encontró enlace en la celda de competición. HTML: {cells[competition_index]}")
            else:
                print(f"Advertencia: Índice 'competition' fuera de rango. Total celdas: {len(cells)}")

        # Ejecutar el método
        process_row(first_row, headers, self.region_entity)

        # Validar que la liga se haya agregado correctamente a la región
        self.assertGreater(len(self.region_entity.leagues), 0, "No se agregó ninguna liga a la región.")
        for league_id, league in self.region_entity.leagues.items():
            print(f"Liga ID: {league_id}, Competición: {league.competition}, País: {league.country}")

if __name__ == "__main__":
    unittest.main()