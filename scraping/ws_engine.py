from bs4 import BeautifulSoup
import re

class ScrapingEngine:
    """
    Motor reutilizable de scraping para todas las entidades (ligas, equipos, jugadores...).
    Contiene funciones genéricas como obtener el número total de páginas.
    """
    def __init__(self, http_client):
        """
        Constructor de la clase ScrapingEngine.

        Args:
            http_client (HttpClient): Instancia de HttpClient para manejar solicitudes HTTP.
        """
        self.http_client = http_client

    @staticmethod
    def expand_cells(cells):
        """
        Expande las celdas combinadas (colspan y rowspan) en una fila de la tabla.

        Args:
            cells (list): Lista de celdas (td) de una fila.

        Returns:
            list: Lista de celdas expandidas.
        """
        expanded_cells = []
        for cell in cells:
            colspan = int(cell.get("colspan", 1))
            rowspan = int(cell.get("rowspan", 1))
            for _ in range(colspan):
                expanded_cells.append(cell)

        print(f"Celdas expandidas: {len(expanded_cells)}")
        return expanded_cells

    def get_total_pages(html: BeautifulSoup) -> int:
        try:
            # Buscamos el contenedor de paginación
            pagination = html.select_one(
                "ul.tm-pagination, div.pagination, ul.pagination, nav[role='navigation'] ul"
            )
            if not pagination:
                return 1

            page_numbers = set()

            # Recorremos todos los enlaces dentro del contenedor
            for a in pagination.find_all("a"):
                # Números visibles (1‑10, 22…)
                page_numbers.update(
                    int(n) for n in re.findall(r"\d+", a.get_text(strip=True))
                )

                # Números escondidos en ?page=X
                href = a.get("href", "")
                page_numbers.update(
                    int(n) for n in re.findall(r"page=(\d+)", href)
                )

            return max(page_numbers) if page_numbers else 1

        except Exception as e:
            print(f"Error: No se pudo determinar el número de páginas: {e}")
            return 1

    def get_table_headers(self, table: BeautifulSoup) -> dict:
        """
        Extrae los encabezados de una tabla HTML y los convierte en un diccionario.

        Args:
            table (BeautifulSoup): Tabla HTML parseada.

        Returns:
            dict: Diccionario con encabezados como claves y sus índices como valores.
        """
        try:
            headers = {}

            # Buscamos encabezado en thead o en la primera fila de la tabla:
            header_row = (
                table.find("thead").find("tr")
                if table.find("thead")
                else table.find_all("tr")[0]
            )

            if not header_row:
                print("No se encontró encabezado en la tabla.")
                return {}

            th_elements = header_row.find_all(["th", "td"])
            for idx, th in enumerate(th_elements):
                text = th.get_text(strip=True)
                if text:  # ignorar columnas vacías
                    formattted_text = text.replace(" ", "_").replace(".", "").lower()
                    headers[formattted_text] = idx

            return headers

        except Exception as e:
            print(f"Error al extraer encabezados de la tabla: {e}")
            return {}

    def get_table_data(
        self,
        url_template: str,
        start_page: int,
        end_page: int,
        row_selector: str
    ):
        """
        Método genérico para recorrer páginas y devolver las filas de una tabla.

        Args:
            url_template (str): Plantilla de URL con un marcador `{page}` para la paginación.
            start_page (int): Número de página inicial.
            end_page (int): Número de página final.
            row_selector (str): Selector CSS para las filas de la tabla.

        Returns:
            list: Lista de filas de la tabla como objetos BeautifulSoup.
        """
        rows = []  # Lista para almacenar las filas extraídas

        for page in range(start_page, end_page + 1):
            # Formatear la URL para la página actual
            url = url_template.format(page=page)
            html = self.http_client.get_html(url)

            if not html:
                print(f"No se pudo obtener el HTML de la página {page}.")
                continue

            # Buscar la tabla en el HTML
            table = html.find("table")
            if not table:
                print(f"No se encontró ninguna tabla en la página {page}.")
                continue

            # Extraer las filas de la tabla
            rows.extend(table.select(row_selector))

        return rows