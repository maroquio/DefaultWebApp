"""Schemas de resposta do módulo de pagamentos (Checkout Pro / multi-provedor)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from model.pagamento_model import Pagamento


class PagamentoResponse(BaseModel):
    """Representação pública de um pagamento."""

    id: int
    usuario_id: int
    descricao: str
    valor: float
    status: str = Field(..., description="Status atual do pagamento")
    provider: str = Field(..., description="Provedor usado na criação (ex: mercadopago)")
    preference_id: Optional[str] = Field(
        default=None, description="ID da preferência/sessão no provedor"
    )
    payment_id: Optional[str] = Field(
        default=None, description="ID do pagamento confirmado no provedor"
    )
    external_reference: Optional[str] = None
    url_checkout: Optional[str] = Field(
        default=None, description="URL de checkout (init_point) do provedor"
    )
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    usuario_nome: Optional[str] = Field(
        default=None, description="Nome do dono do pagamento (visão admin)"
    )

    @classmethod
    def de_pagamento(cls, pagamento: Pagamento) -> "PagamentoResponse":
        """Constrói o response a partir da entidade de domínio."""
        return cls(
            id=pagamento.id,
            usuario_id=pagamento.usuario_id,
            descricao=pagamento.descricao,
            valor=pagamento.valor,
            status=pagamento.status.value,
            provider=pagamento.provider,
            preference_id=pagamento.preference_id,
            payment_id=pagamento.payment_id,
            external_reference=pagamento.external_reference,
            url_checkout=pagamento.url_checkout,
            data_criacao=pagamento.data_criacao,
            data_atualizacao=pagamento.data_atualizacao,
            usuario_nome=pagamento.usuario_nome,
        )


class CriarPagamentoResultadoResponse(BaseModel):
    """
    Resultado da criação de um pagamento.

    O backend NÃO redireciona — o SPA usa ``init_point`` para fazer
    ``window.location`` em direção ao checkout do provedor.
    """

    init_point: str = Field(..., description="URL de checkout para redirecionar o usuário")
    pagamento_id: int = Field(..., description="ID do pagamento criado no sistema")


class DadosProviderResponse(BaseModel):
    """Dados detalhados consultados diretamente no provedor (visão admin)."""

    pagamento: PagamentoResponse
    provider_nome: str = Field(..., description="Nome amigável do provedor")
    dados_provider: Optional[dict] = Field(
        default=None, description="Payload bruto retornado pela API do provedor"
    )
