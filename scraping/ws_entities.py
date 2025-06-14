from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict
from config.exceptions import logging
from bs4 import BeautifulSoup
import logging

@dataclass
class PlayerStats:
    """
    Representa las estadísticas individuales de un jugador.
    """
    birth_date: str
    player_age: int
    player_height: float
    general_position: str
    player_position: str
    player_foot: str
    market_value: float

    def to_dict(self) -> Dict:
        """
        Convierte el objeto PlayerStats a un diccionario.

        Return:
            dict: Representación en diccionario de las estadísticas del jugador.
        """
        return asdict(self)


@dataclass
class PlayerImgInfo:
    """
    Contiene información de la imagen de un jugador.
    """
    fk_player: str
    id_img: str
    img_player: str

    def to_dict(self) -> Dict:
        """
        Convierte el objeto PlayerImgInfo a un diccionario.

        Return:
            dict: Representación en diccionario de la información de imagen.
        """
        return asdict(self)


@dataclass
class Player:
    """
    Representa un jugador, incluyendo sus datos, imagen y estadísticas.
    """
    fk_region: str
    fk_league: str
    id_player: str
    fk_country: str
    player_name: str
    season: int
    player_joined: str
    player_contract: str
    fk_team_signed_from: str
    url_player: str
    player_img_info: Dict[str, PlayerImgInfo] = field(default_factory=dict)
    stats: PlayerStats = None


    def add_player_img_info(self, img_info: Dict[str, str]) -> None:
        """
        Añade información de imagen al jugador.

        Args:
            img_info (dict): Diccionario con información de imagen.
        """
        if not img_info:
            logging.warning(f"No se proporcionó información de imagen para el jugador {self.player_name}.")
            return

        self.player_img_info = {
            "fk_player": self.id_player,
            "id_img": img_info.get("id_img"),
            "img_player": img_info.get("img_player")
        }


    def to_dict(self) -> Dict:
        """
        Convierte el objeto Player a un diccionario.

        Return:
            dict: Representación en diccionario del jugador.
        """
        return {
            "fk_region": self.fk_region,
            "fk_league": self.fk_league,
            "id_player": self.id_player,
            "player_name": self.player_name,

            "player_img_info": self.player_img_info.to_dict()
                if isinstance(self.player_img_info, PlayerImgInfo) else self.player_img_info,

            "fk_country": self.fk_country,
            "player_joined": self.player_joined,
            "player_contract": self.player_contract,
            "fk_team_signed_from": self.fk_team_signed_from,
            "url_player": self.url_player,
            "stats": self.stats.to_dict() if self.stats else None,
        }


@dataclass
class TeamStats:
    """
    Estadísticas agregadas de un equipo.
    """
    fk_team: str
    fk_league: str
    fk_region: str
    season: int
    total_players: int
    avg_age: float
    foreigners: int
    avg_market_value: float
    total_market_value: float


    def to_dict(self) -> Dict:
        """
        Convierte el objeto TeamStats a un diccionario.

        Return:
            dict: Representación en diccionario de las estadísticas del equipo.
        """
        return asdict(self)


@dataclass
class Team:
    """
    Representa un equipo, incluyendo sus estadísticas y jugadores.
    """
    id_team: str
    fk_region: str
    fk_league: str
    season: int
    team_name: str
    url_team: str
    stats: TeamStats
    players: Dict[str, Player] = field(default_factory=dict)

    def __post_init__(self):
        """
        Inicializa los jugadores del equipo a partir de diccionarios si es necesario.
        """
        for player_id, player in self.players.items():
            if isinstance(player, dict):
                self.players[player_id] = Player(**player)

    def to_dict(self) -> Dict:
        """
        Convierte el objeto Team a un diccionario.

        Return:
            dict: Representación en diccionario del equipo.
        """
        return {
            "id_team": self.id_team,
            "fk_region": self.fk_region,
            "fk_league": self.fk_league,
            "season": self.season,
            "team_name": self.team_name,
            "url_team": self.url_team,
            "stats": self.stats.to_dict() if self.stats else None,
            "players": {
                player_id: p.to_dict() for player_id, p in self.players.items()
            }
        }

    def add_player(self, player: Player) -> None:
        """
        Añade un jugador al equipo y le asigna la temporada actual.

        Args:
            player (Player): Jugador a añadir.
        """
        player.season = self.season
        self.players[player.id_player] = player


@dataclass
class LeagueStats:
    """
    Estadísticas agregadas de una liga.
    """
    fk_league: str
    fk_region: str
    season: int
    total_clubs: float
    total_players: float
    avg_age: float
    foreigners: float
    game_ratio_of_foreign_players: float
    goals_per_match: float
    avg_market_value: float
    total_value: float

    def to_dict(self) -> Dict:
        """
        Convierte el objeto LeagueStats a un diccionario.

        Return:
            dict: Representación en diccionario de las estadísticas de la liga.
        """
        return asdict(self)


@dataclass
class League:
    """
    Representa una liga, incluyendo sus equipos, estadísticas y temporadas.
    """
    id_league: str
    competition: str
    season: int
    fk_country: str
    country: str
    url_league: str
    stats: LeagueStats
    teams: Dict[str, Team] = field(default_factory=dict)
    seasons: Dict[str, Dict] = field(default_factory=dict)

    def __post_init__(self):
        """
        Inicializa los equipos y estadísticas de la liga a partir de diccionarios si es necesario.
        """
        if isinstance(self.stats, dict):
            self.stats = LeagueStats(**self.stats)

        for id_team, team in self.teams.items():
            if isinstance(team, dict):
                self.teams[id_team] = Team(**team)

    def to_dict(self) -> Dict:
        """
        Convierte el objeto League a un diccionario, incluyendo temporadas y equipos.

        Return:
            dict: Representación en diccionario de la liga.
        """
        seasons_dict = {
            season_key: {
                "teams": {
                    team_id: team.to_dict() for team_id, team in season_data["teams"].items()
                }
            }
            for season_key, season_data in self.seasons.items()
        }

        # Registro detallado
        logging.debug(f"Generando JSON para la liga '{self.competition}'. Temporadas incluidas: {list(self.seasons.keys())}")

        return {
            "id_league": self.id_league,
            "competition": self.competition,
            "season": self.season,
            "fk_country": self.fk_country,
            "country": self.country,
            "url_league": self.url_league,
            "stats": self.stats.to_dict(),
            **seasons_dict
        }

    def add_country(self, region_countries: Dict[str, "Country"]) -> None:
        """
        Asigna el id de país a la liga si coincide el nombre.

        Args:
            region_countries (dict): Diccionario de países de la región.
        """
        for country_id, country in region_countries.items():
            if country.country_name.strip().lower() == self.country.strip().lower():
                self.fk_country = country_id
                break

    def add_team_to_season(self, season_key: str, team: Team) -> None:
        """
        Añade un equipo a una temporada específica de la liga.

        Args:
            season_key (str): Clave de la temporada.
            team (Team): Equipo a añadir.
        """
        if season_key not in self.seasons:
            self.seasons[season_key] = {"teams": {}}

        self.seasons[season_key]["teams"][team.id_team] = team
        # # Registro detallado
        # logging.info(f"Equipo '{team.team_name}' añadido a la temporada '{season_key}' en la liga '{self.competition}'.")
        # logging.debug(f"Estado actual de la temporada '{season_key}': {self.seasons[season_key]}")


@dataclass
class RegionStats:
    """
    Estadísticas agregadas de una región.
    """
    fk_region: str
    avg_age: float
    avg_height: float
    avg_weight: float
    avg_salary: float
    average_market_value: float
    total_value: float

    def to_dict(self) -> Dict:
        """
        Convierte el objeto RegionStats a un diccionario.

        Return:
            dict: Representación en diccionario de las estadísticas de la región.
        """
        return asdict(self)


@dataclass
class Country:
    """
    Representa un país con su información básica.
    """
    id_country: str
    country_name: str
    country_flag: str

    def to_dict(self) -> Dict:
        """
        Convierte el objeto Country a un diccionario.

        Return:
            dict: Representación en diccionario del país.
        """
        return {
            "id_country": self.id_country,
            "country_name": self.country_name,
            "country_flag": self.country_flag
        }


@dataclass
class Region:
    """
    Representa una región, incluyendo países, ligas y estadísticas.
    """
    id_region: str
    region_name: str
    url_region: str
    stats: RegionStats
    countries: Dict[str, Country] = field(default_factory=dict)
    leagues: Dict[str, Dict[str, League]] = field(default_factory=dict)

    def __post_init__(self):
        """
        Inicializa países, estadísticas y ligas a partir de diccionarios si es necesario.
        """
        if not isinstance(self.stats, RegionStats):
            if isinstance(self.stats, dict):
                self.stats = RegionStats(**self.stats)

        for country_id, country in self.countries.items():
            if isinstance(country, dict):
                self.country[country_id] = Country(**country)

        for tier, leagues in self.leagues.items():
            for league_id, league in leagues.items():
                if isinstance(league, dict):
                    self.leagues[tier][league_id] = League(**league)

    def to_dict(self) -> Dict:
        """
        Convierte el objeto Region a un diccionario, incluyendo países y ligas.

        Return:
            dict: Representación en diccionario de la región.
        """
        region_dict = {
            "id_region":self.id_region,
            "region_name": self.region_name,
            "url_region": self.url_region,
            "countries": {
                country_id: country.to_dict() for country_id, country in self.countries.items()
            },

            "stats": self.stats.to_dict() if isinstance(self.stats, RegionStats) else self.stats,
            "leagues": {
                tier: {
                    league_id: league.to_dict() for league_id, league in leagues.items()
                }

                for tier, leagues in self.leagues.items()
            }
        }

        return region_dict

    def add_country(self, country: Country) -> None:
        """
        Añade un país a la región si no existe previamente.

        Args:
            country (Country): País a añadir.
        """
        if not isinstance(country, Country):
            raise TypeError(f"Se esperaba una instancia de Country, pero se recibió {type(country)}")

        # Evitamos duplicados:
        if country.id_country in self.countries:
            return

        self.countries[country.id_country] = country

    def add_league(self, tier: str, league: League) -> None:
        """
        Añade una liga a un tier específico de la región.

        Args:
            tier (str): Nivel o división.
            league (League): Liga a añadir.
        """
        if tier not in self.leagues:
            self.leagues[tier] = {}

        self.leagues[tier][league.id_league] = league


@dataclass
class TransferMarket:
    """
    Clase raíz del proyecto.
    Contiene toda la información de las regiones
    """
    regions:  Dict[str, Region] = field(default_factory=dict)

    def __post_init__(self):
        """
        Inicializa las regiones a partir de diccionarios si es necesario.
        """
        for region_id, region in self.regions.items():
            if isinstance(region, dict):
                self.regions[region_id] = Region(**region)

    def to_dict(self) -> Dict:
        """
        Convierte el objeto TransferMarket a un diccionario.

        Return:
            dict: Representación en diccionario de todas las regiones.
        """
        return {
            "regions": {
                rkey: r.to_dict() for rkey, r in self.regions.items()
            }
        }

    def add_region(self, region: Region) -> None:
        """
        Añade una región al objeto TransferMarket.

        Args:
            region (Region): Región a añadir.
        """
        if not isinstance(region, Region):
            raise TypeError(f"Se esperaba una instancia de Region, pero se recibió {type(region)}")

        self.regions[region.id_region] = region