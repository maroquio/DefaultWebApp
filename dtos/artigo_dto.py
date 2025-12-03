from pydantic import BaseModel, field_validator
from model.artigo_model import StatusArtigo
from dtos.validators import (
    validar_id_positivo,
    validar_string_obrigatoria,
    validar_comprimento,
    validar_tipo,
)


class CriarArtigoDTO(BaseModel):
    titulo: str
    resumo: str = ""
    conteudo: str
    status: str = "Rascunho"
    categoria_id: int

    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria(
            nome_campo="Título",
            tamanho_minimo=5,
            tamanho_maximo=200
        )
    )
    _validar_resumo = field_validator("resumo")(
        validar_comprimento(tamanho_maximo=500)
    )
    _validar_conteudo = field_validator("conteudo")(
        validar_string_obrigatoria(
            nome_campo="Conteúdo",
            tamanho_minimo=50,
            tamanho_maximo=50000
        )
    )
    _validar_status = field_validator("status")(validar_tipo("Status", StatusArtigo))
    _validar_id_categoria = field_validator("categoria_id")(validar_id_positivo("Categoria"))


class AlterarArtigoDTO(BaseModel):
    id: int
    titulo: str
    resumo: str = ""
    conteudo: str
    status: str
    categoria_id: int

    _validar_id = field_validator("id")(validar_id_positivo("ID"))
    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria(
            nome_campo="Título",
            tamanho_minimo=5,
            tamanho_maximo=200
        )
    )
    _validar_resumo = field_validator("resumo")(
        validar_comprimento(tamanho_maximo=500)
    )
    _validar_conteudo = field_validator("conteudo")(
        validar_string_obrigatoria(
            nome_campo="Conteúdo",
            tamanho_minimo=50,
            tamanho_maximo=50000
        )
    )
    _validar_status = field_validator("status")(validar_tipo("Status", StatusArtigo))
    _validar_id_categoria = field_validator("categoria_id")(validar_id_positivo("Categoria"))