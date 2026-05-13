from dataclasses import dataclass

@dataclass
class Carga:
    id: int
    nome: str
    email: str
    senha: str
    perfil: str
    