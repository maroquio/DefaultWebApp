from pydantic import BaseModel, Field, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_tipo,
)
from model.chamado_model import StatusChamado, PrioridadeChamado


class CriarChamadoDTO(BaseModel):
    """DTO para criação de chamado de suporte."""

    titulo: str = Field(..., description="Título resumido do chamado")
    descricao: str = Field(
        ..., description="Descrição detalhada do problema ou solicitação"
    )
    prioridade: str = Field(
        default="Média", description="Nível de prioridade do chamado"
    )

    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria(
            nome_campo="Título", tamanho_minimo=10, tamanho_maximo=200
        )
    )

    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria(
            nome_campo="Descrição", tamanho_minimo=20, tamanho_maximo=2000
        )
    )

    _validar_prioridade = field_validator("prioridade")(
        validar_tipo("Prioridade", PrioridadeChamado)
    )


class AlterarStatusDTO(BaseModel):
    """DTO para alteração de status do chamado."""

    status: str = Field(..., description="Novo status do chamado")

    _validar_status = field_validator("status")(validar_tipo("Status", StatusChamado))
