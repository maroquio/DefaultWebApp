"""
Schemas de resposta genéricos e transversais da API.

- ErroResponse: documenta o contrato de erro padronizado no OpenAPI.
- MensagemResponse: respostas de ações sem recurso (ex: logout).
- PaginaResponse[T]: envelope único de listagens paginadas.
- TokenCsrfResponse: token CSRF para o handshake do SPA.
"""
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErroResponse(BaseModel):
    """Contrato de erro padronizado da API."""

    detail: str = Field(..., description="Mensagem legível do erro")
    type: str = Field(..., description="Categoria do erro (ex: validation_error)")
    errors: Optional[dict[str, list[str]]] = Field(
        default=None, description="Erros por campo, quando aplicável"
    )


class MensagemResponse(BaseModel):
    """Resposta simples de ação sem recurso associado."""

    message: str = Field(..., description="Mensagem de resultado da operação")


class TokenCsrfResponse(BaseModel):
    """Token CSRF a ser enviado em X-CSRF-Token nas mutações."""

    token: str = Field(..., description="Token CSRF da sessão atual")


class PaginaResponse(BaseModel, Generic[T]):
    """Envelope padronizado de listagens paginadas."""

    items: list[T] = Field(..., description="Itens da página atual")
    pagina: int = Field(..., description="Número da página atual (1-based)")
    por_pagina: int = Field(..., description="Quantidade de itens por página")
    total: int = Field(..., description="Total de itens em todas as páginas")
    total_paginas: int = Field(..., description="Quantidade total de páginas")

    @classmethod
    def de_paginacao(cls, paginacao, items: list) -> "PaginaResponse":
        """
        Constrói o envelope a partir de um ``util.paginacao_util.Paginacao``.

        ``items`` deve ser a lista já convertida para os schemas de resposta
        (não as entidades de domínio cruas), permitindo controlar a serialização.
        """
        return cls(
            items=items,
            pagina=paginacao.pagina_atual,
            por_pagina=paginacao.por_pagina,
            total=paginacao.total,
            total_paginas=paginacao.total_paginas,
        )
