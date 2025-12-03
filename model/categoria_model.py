from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Categoria:
    """
    Representa uma categoria do blog.

    Atributos:
        id: Identificador único da categoria
        nome: Nome da categoria (ex: "Tecnologia")
        descricao: Descrição opcional da categoria
        data_cadastro: Data/hora de criação do registro
        data_atualizacao: Data/hora da última atualização
    """

    id: Optional[int] = None
    nome: str = ""
    descricao: str = ""
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
