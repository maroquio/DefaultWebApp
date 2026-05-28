from dataclasses import dataclass
from typing import Optional

@dataclass
class Carga:
    id: Optional[int]
    titulo: str
    origem: str
    destino: str
    peso: float
    valor: float
    id_categoria: int
    id_empresa: int
    status: str