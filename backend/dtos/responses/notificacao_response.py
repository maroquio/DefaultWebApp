"""Schemas de resposta do módulo de notificações in-app."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from model.notificacao_model import Notificacao


class NotificacaoResponse(BaseModel):
    """Representação pública de uma notificação."""

    id: int
    usuario_id: int
    titulo: str
    mensagem: str
    tipo: str = Field(..., description="Tipo visual: info, sucesso, aviso, erro")
    lida: bool
    url_acao: Optional[str] = None
    data_criacao: Optional[datetime] = None

    @classmethod
    def de_notificacao(cls, notificacao: Notificacao) -> "NotificacaoResponse":
        """Constrói o response a partir da entidade de domínio."""
        return cls(
            id=notificacao.id,
            usuario_id=notificacao.usuario_id,
            titulo=notificacao.titulo,
            mensagem=notificacao.mensagem,
            tipo=notificacao.tipo.value,
            lida=notificacao.lida,
            url_acao=notificacao.url_acao,
            data_criacao=notificacao.data_criacao,
        )


class NotificacaoResumoResponse(BaseModel):
    """Resumo enxuto de uma notificação, usado no polling de não lidas."""

    id: int
    titulo: str
    mensagem: str
    tipo: str = Field(..., description="Tipo visual: info, sucesso, aviso, erro")
    url_acao: Optional[str] = None
    data_criacao: Optional[datetime] = None

    @classmethod
    def de_notificacao(cls, notificacao: Notificacao) -> "NotificacaoResumoResponse":
        """Constrói o resumo a partir da entidade de domínio."""
        return cls(
            id=notificacao.id,
            titulo=notificacao.titulo,
            mensagem=notificacao.mensagem,
            tipo=notificacao.tipo.value,
            url_acao=notificacao.url_acao,
            data_criacao=notificacao.data_criacao,
        )


class NaoLidasResponse(BaseModel):
    """Contagem e lista resumida de notificações não lidas (para polling)."""

    total: int = Field(..., description="Total de notificações não lidas")
    items: list[NotificacaoResumoResponse] = Field(
        default_factory=list, description="Últimas notificações não lidas (resumo)"
    )
