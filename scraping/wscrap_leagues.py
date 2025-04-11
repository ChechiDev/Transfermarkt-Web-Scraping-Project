from scraping.wscrap_engine import Scraper

class LeagueScraper(Scraper):
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
        self.league_id = None
        self.competition = None
        self.region = None
        self.country = None
        self.num_clubs = None
        self.num_player = None
        self.avg_age = None
        self.foreign_players = None
        self.game_ratio_foreign_players = None
        self.goals_per_match = None
        self.avg_market_value = None
        self.total_value = None
        self.league_url = None

    def parse_row(self, row):
        """
        Procesa una fila de la tabla de ligas.

        Args:
            row (BeautifulSoup.Tag): Fila de la tabla.

        Returns:
            dict: Diccionario con los datos de la liga.
        """
        cells = row.find_all("td")

        if len(cells) > 12: # Filtramos filas vacías o con poca información.
            try:
                self.competition = cells[2].get_text(strip=True)
                self.region = "European"
                self.country = self.get_country_from_row(row)
                self.num_clubs = int(cells[4].get_text(strip=True))
                self.num_player = int(cells[5].get_text(strip=True))
                self.avg_age = self.get_float_conversion(cells[6].get_text(strip=True))
                self.foreign_players = self.get_float_conversion(cells[7].get_text(strip=True))
                self.game_ratio_foreign_players = self.get_float_conversion(cells[8].get_text(strip=True))
                self.goals_per_match = self.get_float_conversion(cells[9].get_text(strip=True))
                self.avg_market_value = self.get_float_conversion(cells[11].get_text(strip=True))
                self.total_value = self.get_float_conversion(cells[12].get_text(strip=True))
                self.league_url =cells[1].find("a")["href"] if cells[1].find("a") else None
                self.league_id = self.league_url.split("/")[-1] if self.league_url else None

                return {
                    "league_id": self.league_id,
                    "competition": self.competition,
                    "region": self.region,
                    "country": self.country,
                    "num_clubs": self.num_clubs,
                    "num_player": self.num_player,
                    "avg_age": self.avg_age,
                    "foreign_players": self.foreign_players,
                    "game_ratio_foreign_players": self.game_ratio_foreign_players,
                    "goals_per_match": self.goals_per_match,
                    "avg_market_value": self.avg_market_value,
                    "total_value": self.total_value,
                    "league_url": f"https://www.transfermarkt.com{self.league_url}" if self.league_url else None,
                }
            except (ValueError, IndexError) as e:
                print(f"Error al procesar la fila: {e}")

        return None

    def get_leagues(self, url_key, page=1):
        """
        Obtiene los datos de las ligas desde la tabla.

        Args:
            url_key (str): Clave de la URL en el archivo .env.
            page (int): Número de página a scrapear.

        Returns:
            list: Lista de diccionarios con los datos de las ligas.
        """
        print(f"Keys disponibles en self.urls: {self.urls.keys()}")
        if url_key not in self.urls:
            raise ValueError(f"la Key '{url_key}' no se encuentra en las URL cargadas: {self.urls.keys()}")

        # url = self.build_url(url_key, page=page)
        return self.get_data(url_key, row_parser=self.parse_row)

    def get_country_from_row(self, row):
        """
        Extrae el país desde una fila de la tabla.

        Args:
            row (BeautifulSoup.Tag): Fila de la tabla.

        Returns:
            str: Nombre del país o None si no se encuentra.
        """
        cells = row.find_all("td")

        if len(cells) >= 11:
            country_img = cells[3].find("img", class_="flaggenrahmen")
            self.country = country_img.get("title") if country_img else None
            return self.country

        return None

    def get_float_conversion(self, value):
        """
        Convierte un valor a float, eliminando el símbolo de porcentaje si es necesario.

        Args:
            value (str): Valor a convertir.

        Returns:
            float: Valor convertido a float o None si no es válido.
        """
        try:
            value = value.strip()
            # Eliminamos el símbolo de porcentaje y convertimos a float
            if "%" in value:
                conv_value = value.split("%")[0].strip()
                return float(conv_value) if conv_value else None

            if "€" in value:
                value = value.replace("€","").strip()
                if value.endswith("bn"):
                    return float(value[:-2]) * 1e9 # Miles de millones
                elif value.endswith("m"):
                    return float(value[:-1]) * 1e6 # Millones
                elif value.endswith("k"):
                    return float(value[:-1]) * 1e3 # Miles
                else:
                    return float(value)
            return float(value)

        except (ValueError, AttributeError):
            return None
