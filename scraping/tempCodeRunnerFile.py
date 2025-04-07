from config.headers import headers
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Creamos una clase que defina a Transfermarkt:
class TransfermarktScraper:
    def __init__(self):
        self.header = headers
        self.sleep_time = 3 # <- Configuramos 3 segundos de espera para no saturar al servidor.

    def get_req_to_soup(self, url):
        try:
            response = requests.get(url, headers = self.header)
            soup = BeautifulSoup(response.content, 'html.parser')

            return soup

        except requests.exceptions.RequestException as e:
            print(f"Error al solicitar la url: \n{e}")
            return None



# -------------------------------------------------------------------------------------------
# Comprobamos
if __name__== "__main__":
    # Creamos instancia del Scraper:
    scraper = TransfermarktScraper()

    # URL de prueba
    url = "https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1"

    # Hacemos una petición
    soup = scraper.get_req_to_soup(url)

    if soup:
        print("Página cargada!")
    else:
        print("Error al cargar la página")