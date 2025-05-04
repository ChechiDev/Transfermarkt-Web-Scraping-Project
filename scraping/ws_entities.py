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
    # fk_team: str
    # fk_league: str
    # fk_region: str
    total_players: int
    # avg_age: float
    # foreigners: int
    # average_market_value: float
    # total_market_value: float


    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Team:
    # id_team: str
    fk_region: str
    fk_league: str
    team_name: str
    url_league: str
    url_team: str
    stats: TeamStats
    players: Dict[str, Player] = field(default_factory=dict)

    def __post_init__(self):
        for player_id, player in self.players.items():
            if isinstance(player, dict):
                self.players[player_id] = Player(**player)

    def to_dict(self) -> Dict:
        return {
            # "id_team": self.id_team,
            "fk_region": self.fk_region,
            "fk_league": self.fk_league,
            "team_name": self.team_name,
            "url_league": self.url_league,
            # "url_team": self.url_team,
            "stats": self.stats.to_dict() if self.stats else None,
            "players": {
                player_id: p.to_dict() for player_id, p in self.players.items()
            }
        }

    def add_player(self, player: Player) -> None:
        self.players[player.id_player] = player


@dataclass
class LeagueStats:
    fk_league: str
    fk_region: str
    total_clubs: float
    total_players: float
    avg_age: float
    foreigners: float
    game_ratio_of_foreign_players: float
    goals_per_match: float
    average_market_value: float
    total_value: float

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class League:
    id_league: str
    competition: str
    country: str
    url_league: str
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
            "url_league": self.url_league,
            "stats": self.stats.to_dict(),
            "teams": {
                key: value.to_dict() if hasattr(value, "to_dict") else value
                for key, value in self.teams.items()
            }
        }


    def add_team(self, team: Team) -> None:
        self.teams[team.id_team] = team


@dataclass
class RegionStats:
    fk_region: str # ID de la región (PK para stats)
    avg_age: float
    avg_height: float
    avg_weight: float
    avg_salary: float
    average_market_value: float
    total_value: float

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Region:
    id_region: str
    region_name: str
    url_region: str
    stats: RegionStats
    leagues: Dict[str, League] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.stats, dict):
            self.stats = RegionStats(**self.stats)

        for league_id, league in self.leagues.items():
            if isinstance(league, dict):
                self.leagues[league_id] = League(**league)

    def to_dict(self) -> Dict:
        region_dict = {
            "id_region":self.id_region,
            "region_name": self.region_name,
            "url_region": self.url_region,
            "stats": self.stats.to_dict(),
            "leagues": {
                league_id: league.to_dict() for league_id, league in self.leagues.items()
            }
        }

        return region_dict

    def add_league(self, league: League) -> None:
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
        return {
            "regions": {
                rkey: r.to_dict() for rkey, r in self.regions.items()
            }
        }

    def add_region(self, region: Region) -> None:
        self.regions[region.id_region] = region