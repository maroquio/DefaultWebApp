"""Schemas de resposta do módulo de auditoria estruturada."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from model.auditoria_model import RegistroAuditoria


class AuditoriaResponse(BaseModel):
    """Representação de um registro da trilha de auditoria estruturada."""

    id: int
    usuario_id: Optional[int] = Field(
        default=None, description="ID do usuário que realizou a ação (None se sistema)"
    )
    usuario_nome: Optional[str] = Field(
        default=None, description="Nome do usuário (quando disponível)"
    )
    acao: str = Field(..., description="Tipo da ação realizada")
    entidade: str = Field(..., description="Entidade afetada pela ação")
    entidade_id: Optional[int] = Field(
        default=None, description="ID da entidade afetada (quando aplicável)"
    )
    dados_antes: Optional[str] = Field(
        default=None, description="JSON com estado anterior (atualizar/excluir)"
    )
    dados_depois: Optional[str] = Field(
        default=None, description="JSON com estado posterior (criar/atualizar)"
    )
    ip: Optional[str] = Field(default=None, description="Endereço IP do cliente")
    data: Optional[datetime] = Field(default=None, description="Quando a ação ocorreu")

    @classmethod
    def de_registro(cls, registro: RegistroAuditoria) -> "AuditoriaResponse":
        """Constrói o response a partir da entidade de domínio."""
        return cls(
            id=registro.id,
            usuario_id=registro.usuario_id,
            usuario_nome=registro.usuario_nome,
            acao=str(registro.acao.value if hasattr(registro.acao, "value") else registro.acao),
            entidade=registro.entidade,
            entidade_id=registro.entidade_id,
            dados_antes=registro.dados_antes,
            dados_depois=registro.dados_depois,
            ip=registro.ip,
            data=registro.data,
        )
