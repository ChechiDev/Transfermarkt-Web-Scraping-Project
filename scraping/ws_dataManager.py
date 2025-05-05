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
        # Instancia de TransferMarket para almacenar las regiones y sus datos
        self.transfer_market = TransferMarket()
        self.scraping_engine = ScrapingEngine(http_client)


    def add_region(self, region: Region) -> None:
        logging.debug(f"Añadiendo región: {region}, tipo: {type(region)}")

        if not isinstance(region, Region):
            logging.error("El objeto proporcionado no es una instancia de la clase Region.")
            raise ValueError("El objeto proporcionado no es una instancia de la clase Region.")

        self.transfer_market.regions[region.id_region] = region
        logging.info(f"Región '{region.region_name}' añadida correctamente.")


    def to_dict(self) -> Dict:
        try:
            data = self.transfer_market.to_dict()
            logging.info("Datos convertidos a diccionario correctamente.")
            return data

        except Exception as e:
            logging.error(f"Error al convertir los datos a diccionario: {e}")
            raise HTTPClientError(f"Error al convertir los datos a diccionario: {e}")


    def to_json(self, file_name: str) -> None:
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
