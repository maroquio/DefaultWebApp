from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria, validar_comprimento

class CriarCategoriaDTO(BaseModel):
    """
    DTO para validar dados ao criar uma nova categoria.

    Regras:
    - nome: obrigatório, entre 3 e 50 caracteres
    - descricao: opcional, máximo 200 caracteres
    """
    nome: str
    descricao: str = ""

    # Validador do campo 'nome'
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria(
            nome_campo="Nome",
            tamanho_minimo=3,
            tamanho_maximo=50
        )
    )

    # Validador do campo 'descricao'
    _validar_descricao = field_validator("descricao")(
        validar_comprimento(tamanho_maximo=200)
    )


class AlterarCategoriaDTO(BaseModel):
    """
    DTO para validar dados ao editar uma categoria existente.

    Regras: mesmas do CriarCategoriaDTO
    """
    nome: str
    descricao: str = ""

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria(
            nome_campo="Nome",
            tamanho_minimo=3,
            tamanho_maximo=50
        )
    )

    _validar_descricao = field_validator("descricao")(
        validar_comprimento(tamanho_maximo=200)
    )