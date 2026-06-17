from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from util.enum_base import EnumEntidade


class AcaoAuditoria(EnumEntidade):
    """
    Tipos de ação registrados na trilha de auditoria.

    Para adicionar novos tipos: adicione apenas nesta classe.
    Use no decorator @auditar(acao=AcaoAuditoria.CRIAR, entidade='produto')
    """

    CRIAR = "criar"
    ATUALIZAR = "atualizar"
    EXCLUIR = "excluir"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORTAR = "exportar"
    RESTAURAR = "restaurar"


@dataclass
class RegistroAuditoria:
    """
    Registro de uma ação realizada na aplicação.

    Campos:
        id: ID do registro
        usuario_id: ID do usuário que realizou a ação (None se sistema)
        usuario_nome: Nome do usuário (JOIN com tabela usuario)
        acao: Tipo da ação (AcaoAuditoria)
        entidade: Nome da entidade afetada (ex: 'usuario', 'produto')
        entidade_id: ID da entidade afetada (None se não aplicável)
        dados_antes: JSON com estado anterior (para ATUALIZAR/EXCLUIR)
        dados_depois: JSON com estado posterior (para CRIAR/ATUALIZAR)
        ip: Endereço IP do cliente
        data: Quando a ação ocorreu

    Exemplo de criação via decorator:
        from util.auditoria_decorator import auditar

        @router.post("/produto/excluir/{id}")
        @auditar(acao=AcaoAuditoria.EXCLUIR, entidade="produto")
        async def excluir(request: Request, id: int, ...):
            ...
    """

    id: int
    acao: AcaoAuditoria
    entidade: str
    usuario_id: Optional[int] = None
    usuario_nome: Optional[str] = None
    entidade_id: Optional[int] = None
    dados_antes: Optional[str] = None
    dados_depois: Optional[str] = None
    ip: Optional[str] = None
    data: Optional[datetime] = None
