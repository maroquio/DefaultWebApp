"""Schemas de resposta do módulo de chamados (suporte)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from model.chamado_model import Chamado
from model.chamado_interacao_model import ChamadoInteracao


class ChamadoInteracaoResponse(BaseModel):
    """Representação de uma interação (mensagem) de um chamado."""

    id: int
    chamado_id: int
    usuario_id: int
    mensagem: str
    tipo: str = Field(..., description="Tipo da interação")
    data_interacao: Optional[datetime] = None
    status_resultante: Optional[str] = Field(
        default=None, description="Status do chamado após esta interação"
    )
    data_leitura: Optional[datetime] = None
    usuario_nome: Optional[str] = None
    usuario_email: Optional[str] = None

    @classmethod
    def de_interacao(cls, interacao: ChamadoInteracao) -> "ChamadoInteracaoResponse":
        """Constrói o response a partir da entidade de domínio."""
        # status_resultante pode vir como str ou Enum
        status_resultante = interacao.status_resultante
        if status_resultante is not None and hasattr(status_resultante, "value"):
            status_resultante = status_resultante.value

        return cls(
            id=interacao.id,
            chamado_id=interacao.chamado_id,
            usuario_id=interacao.usuario_id,
            mensagem=interacao.mensagem,
            tipo=interacao.tipo.value,
            data_interacao=interacao.data_interacao,
            status_resultante=status_resultante,
            data_leitura=interacao.data_leitura,
            usuario_nome=interacao.usuario_nome,
            usuario_email=interacao.usuario_email,
        )


class ChamadoResponse(BaseModel):
    """Representação de um chamado de suporte."""

    id: int
    titulo: str
    status: str = Field(..., description="Status atual do chamado")
    prioridade: str = Field(..., description="Prioridade do chamado")
    usuario_id: int
    data_abertura: Optional[datetime] = None
    data_fechamento: Optional[datetime] = None
    usuario_nome: Optional[str] = None
    usuario_email: Optional[str] = None
    mensagens_nao_lidas: int = 0
    tem_resposta_admin: bool = False
    interacoes: Optional[list[ChamadoInteracaoResponse]] = Field(
        default=None,
        description="Histórico de interações (presente apenas no detalhe)",
    )

    @classmethod
    def de_chamado(
        cls,
        chamado: Chamado,
        interacoes: Optional[list[ChamadoInteracao]] = None,
    ) -> "ChamadoResponse":
        """Constrói o response a partir da entidade de domínio.

        ``interacoes`` deve ser passado apenas em endpoints de detalhe; nas
        listagens deixe ``None`` para não carregar o histórico completo.
        """
        return cls(
            id=chamado.id,
            titulo=chamado.titulo,
            status=chamado.status.value,
            prioridade=chamado.prioridade.value,
            usuario_id=chamado.usuario_id,
            data_abertura=chamado.data_abertura,
            data_fechamento=chamado.data_fechamento,
            usuario_nome=chamado.usuario_nome,
            usuario_email=chamado.usuario_email,
            mensagens_nao_lidas=chamado.mensagens_nao_lidas,
            tem_resposta_admin=chamado.tem_resposta_admin,
            interacoes=(
                [ChamadoInteracaoResponse.de_interacao(i) for i in interacoes]
                if interacoes is not None
                else None
            ),
        )
