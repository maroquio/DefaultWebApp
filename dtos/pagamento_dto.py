from typing import Any

from pydantic import BaseModel, Field, field_validator

from dtos.validators import validar_string_obrigatoria


class CriarPagamentoDTO(BaseModel):
    """DTO para criação de um novo pagamento via Checkout Pro do Mercado Pago."""

    descricao: str = Field(..., description="Descrição do item/serviço a ser pago")
    valor: float = Field(..., gt=0, description="Valor do pagamento em reais")

    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria(
            nome_campo="Descrição",
            tamanho_minimo=5,
            tamanho_maximo=255,
        )
    )

    @field_validator("valor")
    @classmethod
    def validar_valor(cls, v: Any) -> Any:
        """Valida que o valor é um número positivo com no máximo 2 casas decimais."""
        try:
            v = float(v)
        except (TypeError, ValueError):
            raise ValueError("Valor deve ser um número válido")
        if v <= 0:
            raise ValueError("Valor deve ser maior que zero")
        if v > 999_999.99:
            raise ValueError("Valor máximo permitido é R$ 999.999,99")
        return round(v, 2)
