from scraping.ws_engine import ScrapingEngine
from src.ws_urls import TransferMarktURLManager
from src.ws_entities import League, LeagueStats, Region


class LeagueScraper(ScrapingEngine):
    """
    Scraper específico para obtener información de ligas de futbol.
    """
    def __init__(self, http_client):
        """
        Constructor de la clase LeagueScraper.

        Args:
            http_client (HttpClient): Instancia de HttpClient para manejar solicitudes HTTP.
        """
        super().__init__(http_client)
        self.id_league = None

    def set_table_headers(self, headers: dict):
        """
        Asigna los encabezados de la tabla como atributos de la clase.

        Args:
            headers (dict): Diccionario con encabezados como claves y sus índices como valores.
        """
        for header, index in headers.items():
            setattr(self, header, index)

    def extract_headers_from_table(self, table):
        """
        Extrae los encabezados de la tabla y los asigna como atributos.

        Args:
            table (BeautifulSoup): Tabla HTML parseada.
        """
        headers = self.get_table_headers(table)
        self.set_table_headers(headers)

    def create_league_instance(
        self,
        id_league: str,
        competition: str,
        country: str,
        region_entity: Region
    ) -> None:
        """
        Crea una instancia de League y la agrega a la entidad Region.

        Args:
            id_league (str): ID de la liga.
            competition (str): Nombre de la competición.
            country (str): País de la liga.
            region_entity (Region): Entidad Region donde se agregará la liga.
        """
        if id_league not in region_entity.leagues:
            league = League(
                id_league=id_league,
                competition=competition,
                country=country,
                url=f"https://www.transfermarkt.com/startseite/wettbewerb/{id_league}",
                stats=LeagueStats(
                    fk_league=id_league,
                    fk_region=region_entity.id_region
                )
            )
            region_entity.add_league(league)

    def process_table_rows(
        self,
        url_template: str,
        start_page: int,
        end_page: int,
        row_selector: str,
        headers: dict,
        row_processor: callable,
        region_entity: Region
    ) -> None:
        """
        Extrae filas de la tabla y aplica una función de procesamiento a cada fila.

        Args:
            url_template (str): Plantilla de la URL para las páginas.
            start_page (int): Número de la página inicial.
            end_page (int): Número de la página final.
            row_selector (str): Selector CSS para las filas de la tabla.
            headers (dict): Diccionario de encabezados con sus índices.
            row_processor (callable): Función que define cómo procesar cada fila.
            region_entity (Region): Entidad Region donde se guardarán las ligas.
        """
        for page in range(start_page, end_page + 1):
            html = self.http_client.get_html(url_template.format(page=page))
            if not html:
                print(f"Advertencia: No se pudo obtener el HTML para la página {page}.")
                continue

            table = html.find("table")
            if not table:
                print(f"Advertencia: No se encontró ninguna tabla en la página {page}.")
                continue

            rows = table.select(row_selector)
            for row in rows:
                row_processor(row, headers, region_entity)


class GetDataLeagues:
    """
    Clase para extraer datos específicos de las ligas desde el HTML.
    """

    def __init__(self, url_manager: TransferMarktURLManager, region: str):
        """
        Inicializa la clase con los datos de la región.

        Args:
            url_manager (TransferMarktURLManager): Gestor de URLs.
            region (str): Región para obtener las URLs.
        """
        if region not in url_manager.urls:
            raise ValueError(f"La región '{region}' no está configurada en el URL Manager.")

        self.url_template = url_manager.urls[region]["url"]
        self.start_page = url_manager.urls[region]["start_page"]
        self.end_page = url_manager.urls[region]["end_page"]

        if self.end_page is None:
            raise ValueError(f"No se ha configurado el número de páginas para la región '{region}'.")

    def get_id_league(
        self,
        scraper: LeagueScraper,
        region_entity: Region
    ) -> list:
        """
        Extrae todos los IDs de liga desde las páginas de una región y los asigna al atributo `id_league` del scraper.
        Además, guarda las ligas extraídas en la entidad `Region`.

        Args:
            scraper (LeagueScraper): Instancia de LeagueScraper para manejar el scraping.
            region_entity (Region): Entidad Region donde se guardarán las ligas.

        Returns:
            list: Lista de IDs de liga extraídos.
        """
        # Obtener el HTML de la primera página para extraer encabezados
        html = scraper.http_client.get_html(self.url_template.format(page=self.start_page))
        if not html:
            raise ValueError(f"No se pudo obtener el HTML para la región.")

        table = html.find("table")
        if not table:
            raise ValueError(f"No se encontró ninguna tabla en el HTML para la región.")

        # Extraer encabezados de la tabla
        headers = scraper.get_table_headers(table)
        if "competition" not in headers:
            raise ValueError("El encabezado 'competition' no se encontró en la tabla.")

        # Extraer IDs de liga desde las filas
        ids = set()  # Usaremos set() para evitar duplicados

        def process_row(row, headers, region_entity):
            """
            Procesa una fila de la tabla para extraer el ID de la liga y crear una instancia.

            Args:
                row (BeautifulSoup): Fila de la tabla.
                headers (dict): Diccionario de encabezados con sus índices.
                region_entity (Region): Entidad Region donde se guardarán las ligas.
            """
            # Obtener todas las celdas de la fila
            cells = row.find_all("td")

            # Expandir celdas combinadas (colspan y rowspan)
            cells = ScrapingEngine.expand_cells(cells)

            # Validar que la cantidad de celdas coincida con la cantidad de encabezados
            if len(cells) <= 2:
                return  # Ignorar esta fila

            competition_name = self.get_competition(row, headers)
            country_name = self.get_country(row, headers)

            # Procesar el ID de la liga
            competition_index = headers["competition"] - 1
            if competition_index < len(cells):
                link = cells[competition_index].find("a", href=True)
                if link:
                    league_id = link["href"].split("/")[-1]
                    scraper.create_league_instance(
                        league_id,
                        competition_name,
                        country_name,
                        region_entity
                    )
                    ids.add(league_id)
                else:
                    print(f"Advertencia: No se encontró enlace en la celda de competición. HTML: {cells[competition_index]}")
            else:
                print(f"Advertencia: Índice 'competition' fuera de rango. Total celdas: {len(cells)}")

        scraper.process_table_rows(
            url_template=self.url_template,
            start_page=self.start_page,
            end_page=self.end_page,
            row_selector="tbody tr",
            headers=headers,
            row_processor=process_row,
            region_entity=region_entity
        )

        # Asignar los IDs extraídos al atributo del scraper
        scraper.id_league = list(ids)  # Convertir el conjunto a lista
        return scraper.id_league

    def get_competition(self, row, headers) -> str:
        """
        Extrae el nombre de la competición desde una fila de la tabla.

        Args:
            row (BeautifulSoup): Fila de la tabla.
            headers (dict): Diccionario con encabezados y sus índices.

        Returns:
            str: Nombre de la competición o 'Unknown' si no se encuentra.
        """
        if "competition" not in headers:
            raise ValueError("El encabezado 'competition' no se encontró en la tabla.")

        competition_index = headers["competition"] - 1
        cells = row.find_all("td")

        if competition_index < len(cells):
            link = cells[competition_index].find("a", href=True)
            if link:
                return link.get("title", link.get_text(strip=True)) or "Unknown"

        print(f"Advertencia: No se encontró la competición en la fila. HTML: {row}")
        return "Unknown"

    def get_country(self, row, headers) -> str:
        """
        Extrae el nombre del país desde una fila de la tabla.

        Args:
            row (BeautifulSoup): Fila de la tabla.
            headers (dict): Diccionario con encabezados y sus índices.

        Returns:
            str: Nombre del país o 'Unknown' si no se encuentra.
        """
        if "country" not in headers:
            raise ValueError("El encabezado 'country' no se encontró en la tabla.")

        # Obtener el índice de la columna 'country'
        country_index = headers["country"] - 1
        cells = row.find_all("td")

        # Verificar si la celda correspondiente al país existe
        if country_index < len(cells):
            cell = cells[country_index]
            print(f"HTML de la celda del país: {cell}")

            # Buscar la imagen dentro de la celda correspondiente
            img = cell.find("img", class_="flaggenrahmen")
            if img:
                # Extraer el nombre del país desde el atributo 'title'
                country_name = img.get("title", "").strip()
                if country_name:
                    return country_name
                else:
                    print(f"Advertencia: La imagen no tiene el atributo 'title'. HTML: {img}")
            else:
                print(f"Advertencia: No se encontró una imagen con clase 'flaggenrahmen'. HTML: {cell}")
        else:
            print(f"Advertencia: Índice 'country_index' fuera de rango. Total celdas: {len(cells)}")

        # Si no se encuentra el país, devolver 'Unknown'
        print(f"Advertencia: No se encontró el país en la fila. HTML: {row}")
        return "Unknown"