from pydantic import BaseModel, Field, field_validator

from dtos.validators import validar_string_obrigatoria


class CriarCategoriaDTO(BaseModel):
    """DTO para criação de categoria."""

    nome: str = Field(..., description="Nome da categoria")

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria(nome_campo="Nome", tamanho_minimo=3, tamanho_maximo=100)
    )


class AlterarCategoriaDTO(CriarCategoriaDTO):
    """DTO para alteração de categoria — mesmos campos da criação."""
    pass
