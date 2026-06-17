"""
Decorator de Auditoria para Routes FastAPI.

Registra automaticamente ações realizadas em routes na trilha de auditoria,
capturando usuário logado, IP do cliente e a ação realizada.

Uso:
    from util.auditoria_decorator import auditar
    from model.auditoria_model import AcaoAuditoria

    @router.post("/produto/excluir/{produto_id}")
    @requer_autenticacao()
    @auditar(acao=AcaoAuditoria.EXCLUIR, entidade="produto")
    async def excluir_produto(request: Request, produto_id: int, ...):
        ...
        # A auditoria é registrada automaticamente

    # Para passar o ID da entidade:
    @router.post("/usuario/editar/{usuario_id}")
    @requer_autenticacao()
    @auditar(acao=AcaoAuditoria.ATUALIZAR, entidade="usuario", id_param="usuario_id")
    async def editar_usuario(request: Request, usuario_id: int, ...):
        ...

IMPORTANTE: O decorator @auditar deve vir APÓS @requer_autenticacao() na pilha.
            A ordem de aplicação em Python é de baixo para cima, então:
                @requer_autenticacao()  <- executado primeiro
                @auditar(...)           <- executado depois
"""

import json
import functools
from typing import Optional, Callable, Any

from fastapi import Request

from model.auditoria_model import AcaoAuditoria
from repo import auditoria_repo
from util.rate_limiter import obter_identificador_cliente
from util.logger_config import logger


def auditar(
    acao: str | AcaoAuditoria,
    entidade: str,
    id_param: Optional[str] = None,
    registrar_em_erro: bool = False,
) -> Callable:
    """
    Decorator que registra ações de auditoria automaticamente.

    Captura automaticamente:
    - Usuário logado (via request.session)
    - IP do cliente (suporta proxies via X-Forwarded-For)
    - Ação e entidade fornecidos nos parâmetros

    Args:
        acao: Tipo da ação. Use AcaoAuditoria.CRIAR, .ATUALIZAR, .EXCLUIR, etc.
              ou string direta: 'criar', 'atualizar', 'excluir', 'exportar'
        entidade: Nome da entidade afetada (ex: 'usuario', 'produto', 'pedido')
        id_param: Nome do parâmetro da route que contém o ID da entidade
                  (ex: id_param='produto_id' para capturar o ID do produto)
        registrar_em_erro: Se True, registra auditoria mesmo quando a route lança exceção

    Returns:
        Decorator que envolve a função da route

    Exemplos:
        # Criação (sem ID ainda)
        @auditar(acao=AcaoAuditoria.CRIAR, entidade="produto")
        async def criar_produto(request: Request, ...): ...

        # Exclusão com ID
        @auditar(acao=AcaoAuditoria.EXCLUIR, entidade="produto", id_param="produto_id")
        async def excluir_produto(request: Request, produto_id: int, ...): ...

        # Exportação
        @auditar(acao=AcaoAuditoria.EXPORTAR, entidade="usuarios")
        async def exportar_csv(request: Request, ...): ...
    """
    acao_valor = acao.value if isinstance(acao, AcaoAuditoria) else str(acao)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extrair request dos argumentos
            request: Optional[Request] = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            # Extrair informações para auditoria
            usuario_id = None
            ip = None

            if request:
                try:
                    usuario_logado = request.session.get("usuario_logado")
                    if usuario_logado:
                        usuario_id = usuario_logado.get("id")
                except Exception:
                    pass
                ip = obter_identificador_cliente(request)

            # Extrair ID da entidade se especificado
            entidade_id = kwargs.get(id_param) if id_param else None

            try:
                resultado = await func(*args, **kwargs)

                # Registrar auditoria após execução bem-sucedida
                auditoria_repo.registrar(
                    acao=acao_valor,
                    entidade=entidade,
                    usuario_id=usuario_id,
                    entidade_id=entidade_id,
                    ip=ip,
                )
                logger.debug(f"Auditoria: [{acao_valor}] {entidade} (user={usuario_id}, ip={ip})")

                return resultado

            except Exception as e:
                if registrar_em_erro:
                    auditoria_repo.registrar(
                        acao=acao_valor,
                        entidade=entidade,
                        usuario_id=usuario_id,
                        entidade_id=entidade_id,
                        dados_antes=json.dumps({"erro": str(e)}),
                        ip=ip,
                    )
                raise

        return wrapper
    return decorator
