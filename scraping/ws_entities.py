from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

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
    def __init__(self):
        pass