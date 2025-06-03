import os
import json
from bs4 import BeautifulSoup
from config.exceptions import HTTPClientError, logging
from scraping.ws_engine import ScrapingEngine
from scraping.ws_entities import Region, League, LeagueStats, TransferMarket
from typing import Dict

class DataManager:
    """
    Clase para gestionar y centralizar los datos del proyecto.
    Permite generar un JSON con la estructura completa de datos.
    """
    def __init__(self, http_client):
        """
        Inicializa el DataManager con un cliente HTTP y el motor de scraping.

        Args:
            http_client: Cliente HTTP para las peticiones web.
        """
        self.transfer_market = TransferMarket()
        self.scraping_engine = ScrapingEngine(http_client)


    def add_region(self, region: Region) -> None:
        """
        Añade una región al objeto TransferMarket.

        Args:
            region (Region): Instancia de la clase Region a añadir.
        """

        # Validamos que la región sea una instancia de la clase Region:
        logging.debug(f"Añadiendo región: {region}, tipo: {type(region)}")

        if not isinstance(region, Region):
            logging.error("El objeto proporcionado no es una instancia de la clase Region.")
            raise ValueError("El objeto proporcionado no es una instancia de la clase Region.")

        self.transfer_market.regions[region.id_region] = region
        logging.info(f"Región '{region.region_name}' añadida correctamente.")


    def to_dict(self) -> Dict:
        """
        Convierte los datos de TransferMarket a un diccionario.

        Return:
            dict: Estructura de datos en formato diccionario.
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
        Guarda los datos de TransferMarket en un archivo JSON.

        Args:
            file_name (str): Nombre del archivo JSON a crear.
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
