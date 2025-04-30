import os
import json
from bs4 import BeautifulSoup
from config.exceptions import HTTPClientError, logging
from scraping.ws_engine import ScrapingEngine
from scraping.ws_entities import Region, League, TransferMarket
from typing import Dict

class DataManager:
    """
    Clase para gestionar y centralizar los datos del proyecto.
    Permite generar un JSON con la estructura completa de datos.
    """
    def __init__(self, http_client):
        # Instancia de TransferMarket para almacenar las regiones y sus datos
        self.transfer_market = TransferMarket()
        self.scraping_engine = ScrapingEngine(http_client)


    def extract_league_table_data(self, table: BeautifulSoup, min_columns: int) -> list:
        """
        Extrae todos los datos válidos de una tabla HTML y devuelve una lista de diccionarios.
        Solo incluye filas que tienen al menos `min_columns` columnas.

        Args:
            table (BeautifulSoup): Tabla HTML parseada.
            min_columns (int): Número mínimo de columnas requeridas para procesar una fila.

        Returns:
            list: Lista de diccionarios con los datos de la tabla.
        """
        try:
            # Extraemos los encabezados de la tabla:
            headers = self.scraping_engine.get_table_headers(table)
            if not headers:
                logging.error("No se encontraron encabezados en la tabla.")
                return []

            # Extraemos las filas de la tabla:
            rows = table.find("tbody").find_all("tr")
            if not rows:
                logging.warning("No se encontraron filas en la tabla.")
                return []

            # Procesamos las filas y extraemos los datos:
            table_data = []
            for row in rows:
                col = row.find_all("td")
                if not col:
                    logging.warning("Fila vacía o sin datos.")
                    continue

                # Filtrar filas que tienen menos columnas que `min_columns`
                if len(col) < min_columns:
                    # logging.info(f"Fila omitida porque tiene {len(col)} columnas (menos que {min_columns}).")
                    continue

                try:
                    # Extraer el texto y el enlace del campo 'competition'
                    competition_cell = col[headers["competition"]]
                    competition_name = competition_cell.get_text(strip=True)
                    competition_url = competition_cell.find("a")["href"] if competition_cell.find("a") else None

                    # Extraer el país desde la celda correspondiente
                    country_cell = col[headers["country"]+2]
                    country_name = country_cell.find("img", {"class": "flaggenrahmen"})["title"] if country_cell.find("img", {"class": "flaggenrahmen"}) else None
                    country_flag = country_cell.find("img")["src"] if country_cell.find("img") else None

                    # Extraemos el total de clubes desde la celda correspondiente
                    clubs_cell = col[headers["clubs"]+2]
                    total_clubs = int(clubs_cell.get_text(strip=True) if clubs_cell else 0)

                    # Extraemos el total de players desde la celda correspondiente
                    player_cell = col[headers["player"]+2]
                    total_players = int(player_cell.get_text(strip=True) if player_cell else 0)

                    # Guardar los datos en un diccionario
                    row_data = {
                        "competition": {
                            "competition": competition_name,
                            "url": competition_url
                        },
                        "country": {
                            "country": country_name,
                            "flag_id": None,
                            "flag": country_flag
                        },
                        "clubs": {
                            "total_clubs": total_clubs
                        },
                        "player": {
                            "total_players": total_players
                        },
                    }

                    table_data.append(row_data)

                except IndexError:
                    logging.warning("No se pudo extraer los campos de la fila.")
                    continue

            logging.info(f"Datos extraídos de la tabla: {len(table_data)} filas.")
            return table_data

        except Exception as e:
            logging.error(f"Error al extraer datos de la tabla: {e}")
            return []


    def add_region(self, region: Region) -> None:
        """
        Añade una región a TransferMarket.
        Args:
            region (Region): Objeto de la clase Region.
        Raises:
            ValueError: Si el objeto region no es una instancia de Region.
        """
        if not isinstance(region, Region):
            logging.error("El objeto proporcionado no es una instancia de la clase Region.")
            raise ValueError("El objeto proporcionado no es una instancia de la clase Region.")

        self.transfer_market.regions[region.id_region] = region
        logging.info(f"Región '{region.region_name}' añadida correctamente.")


    def to_dict(self) -> Dict:
        """
        Convierte la instancia de TransferMarket en un diccionario.
        Returns:
            dict: Representación en diccionario de TransferMarket.
        """
        try:
            data = self.transfer_market.to_dict()
            logging.info("Datos convertidos a diccionario correctamente.")
            return data

        except Exception as e:
            logging.error(f"Error al convertir los datos a diccionario: {e}")
            raise HTTPClientError(f"Error al convertir los datos a diccionario: {e}")


    def to_json(self, file_name: str) -> None:
        """
        Guarda los datos en un archivo JSON dentro de la carpeta 'Data Output'.
        Args:
            file_name (str): Nombre del archivo JSON (sin la ruta completa).
        """
        try:
            # Construimos la ruta para guardar el json con la data:
            output_dir = os.path.join(os.getcwd(), "Data output")
            os.makedirs(output_dir, exist_ok=True) # Creamos la carpeta si no existe
            file_path = os.path.join(output_dir, file_name)


            # Convertimos la data a un diccionario:
            data = self.to_dict()

            with open(file_path, "w", encoding = "utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii = False, indent = 4)

            logging.info(f"Datos guardados en el archivo JSON: {file_path}")

        except Exception as e:
            logging.error(f"Error al guardar los datos en el archivo JSON: {e}")
            raise HTTPClientError(f"Error al guardar los datos en el archivo JSON: {e}")
