from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict

@dataclass
class PlayerStats:
    pass


@dataclass
class Player:
    pass


@dataclass
class TeamStats:
    pass


@dataclass
class Team:
    pass


@dataclass
class LeagueStats:
    """
    Estadísticas de una liga.
    """
    fk_league: str
    fk_region: str
    total_clubs: float
    total_players: float

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class League:
    """
    Clase que representa una liga nacional/regional con todos sus equipos y estadísticas.
    """
    id_league: str
    competition: str
    country: str
    url: str
    stats: LeagueStats
    teams: Dict[str, Team] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.stats, dict):
            self.stats = LeagueStats(**self.stats)

        for team_id, team in self.teams.items():
            if isinstance(team, dict):
                self.teams[team_id] = Team(**team)

    def to_dict(self) -> Dict:
        return {
            "id_league": self.id_league,
            "competition": self.competition,
            "country": self.country,
            "url": self.url,
            "stats": self.stats.to_dict(), # Objeto con las estadísticas de la liga.
            "teams": {
                id_team : t.to_dict() for id_team, t in self.teams.items()
            }
        }


    def add_team(self, team: Team) -> None:
        """
        Añade un equipo a la liga.
        """
        self.teams[team.id_team] = team


@dataclass
class RegionStats:
    """
    Estadísticas globales de una región.
    """
    fk_region: str # ID de la región (PK para stats)
    avg_age: float
    avg_height: float
    avg_weight: float
    avg_salary: float
    avg_market_value: float

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Region:
    """
    Clase que representa una región que agrupa multiples ligas.
    """
    id_region: str
    region_name: str
    url: str
    stats: RegionStats
    leagues: Dict[str, League] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.stats, dict):
            self.stats = RegionStats(**self.stats)

        for league_id, league in self.leagues.items():
            if isinstance(league, dict):
                self.leagues[league_id] = League(**league)

    def to_dict(self) -> Dict: # Convertimos atributos Region en dict:
        return {
            "id_region":self.id_region,
            "region_name": self.region_name,
            "url": self.url,
            "stats": self.stats.to_dict(), # Obj con las estadísticas
            "leagues": {
                league_id: l.to_dict() for league_id, l in self.leagues.items() # Diccionario con las ligas de la región.
            }
        }

    def add_league(self, league: League) -> None:
        """
        Añade una liga a la región.
        """
        self.leagues[league.id_league] = league


@dataclass
class TransferMarket:
    """
    Clase raíz del proyecto.
    Contiene toda la información de las regiones
    """
    # Creamos el diccionario de regiones.
    regions:  Dict[str, Region] = field(default_factory=dict)

    def __post_init__(self):
        for region_id, region in self.regions.items():
            if isinstance(region, dict):
                self.regions[region_id] = Region(**region)

    def to_dict(self) -> Dict:
        """
        Convierte la clase en un diccionario.
        """
        return {
            "regions": {
                rkey: r.to_dict() for rkey, r in self.regions.items()
            }
        }

    def add_region(self, region: Region) -> None:
        """
        Añade una región al mercado de transferencias.
        """
        self.regions[region.id_region] = region