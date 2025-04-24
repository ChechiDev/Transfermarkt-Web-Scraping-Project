from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict

@dataclass
class Region:
    """
    Clase que representa una región.
    Contiene información sobre la región y sus ligas.
    """
    id_region: str
    region_name: str
    url: str

@dataclass
class Transfermarkt:
    """
    Clase raíz del proyecto.
    Contiene toda la información de las regiones.
    """
    # Creamos el diccionario con las regiones:
    regions: Dict[str, Region] = field(default_factory=dict)


    def __post_init__(self):
        for region_id, region in self.regions.items():
            if isinstance(region, Dict):
                self.regions[region_id] = Region(**region)
