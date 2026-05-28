from pydantic import BaseModel, Field, field_validator
from dtos.validators import (
    validar_id_positivo,
    validar_comprimento,
    validar_preco
)


class CriarCargaDTO(BaseModel):
    """DTO para criação de Cargas pelo administrador."""

    titulo: str = Field(..., description="Título descritivo do frete")
    origem: str = Field(..., description="Cidade e Estado de origem")
    destino: str = Field(..., description="Cidade e Estado de destino")
    peso: float = Field(..., description="Peso da carga em toneladas")
    valor: float = Field(..., description="Valor bruto ofertado pelo frete")
    id_categoria: int = Field(..., description="ID da categoria de carroceria exigida")
    id_empresa: int = Field(..., description="ID da empresa embarcadora")
    status: str = Field(..., description="Status atual da carga")

    # Mapeando os validadores exatamente na mesma estrutura base que você definiu:
    _validar_id_categoria = field_validator("id_categoria")(validar_id_positivo("id_categoria"))
    _validar_id_empresa = field_validator("id_empresa")(validar_id_positivo("id_categoria"))
    _validar_titulo = field_validator("titulo")(validar_comprimento("titulo", 2, 100))
    _validar_origem = field_validator("origem")(validar_comprimento("origem", 2, 100))
    _validar_destino = field_validator("destino")(validar_comprimento("destino", 2, 100))
    _validar_status = field_validator("status")(validar_comprimento("status", 2, 100))
    _validar_peso = field_validator("peso")(validar_preco("peso"))
    _validar_valor = field_validator("valor")(validar_preco("valor"))