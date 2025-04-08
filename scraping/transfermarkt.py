from config.headers import headers
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# Creamos una clase para la configuración de las ligas
class Leagues:
    def __init__(self, id_league, league_name, league_url):
        self.id_league = id_league
        self.league_name = league_name
        self.league_url = league_url

    def __repr__(self):
        return f"League(id_league='{self.id_league}', league_name='{self.league_name}, league_url='{self.league_url}')"


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


    def get_all_leagues(self, soup):
        leagues_list = []

        # Encontrar todos los <a> dentro de la tabla que contengan las ligas
        league_links = soup.select('table.items a')

        for link in league_links:
            league_name = link.get_text(strip=True)

            league_url = link.get('href')
            # Extraemos el ID de la URL:
            id_league = league_url.split("/")[-1]

            # Filtramos para evitar información innecesaria:
            if(
                not league_name or
                re.match(r"[\d%]", league_name) or
                league_name in ["Player", "Avg. age", "Foreigners", "Goals per match", "Average market value", "Total value"]

            ): continue

            # Creamos el objeto League:
            league = Leagues(
                id_league=id_league,
                league_name=league_name,
                league_url=f"https://www.transfermarkt.com{league_url}" # <- URL completa
            )

            # Creamos un diccionario con las ligas:
            league_dict = {
                "id_league": league.id_league,
                "league_name": league.league_name,
                "league_url": league.league_url
            }
            # Añadimos el diccionario a la lista:
            leagues_list.append(league_dict)

        # Convertimos a df:
        df_leagues = pd.DataFrame(leagues_list)

        return df_leagues





# Comprobamos:
# ----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    scraper = TransfermarktScraper()
    url = "https://www.transfermarkt.com/wettbewerbe/europa/wettbewerbe?plus=1"
    soup = scraper.get_req_to_soup(url)

    if soup:
        print("✅ Página cargada correctamente.")
        leagues = scraper.get_all_leagues(soup)

        # Mostramos con pandas:
        df = pd.DataFrame(leagues)
        print(df)

    else:
        print("❌ Error al cargar la página.")