# =============================================================================
# Rotas de Administração: Configurações + Auditoria (API JSON)
# =============================================================================

# Standard library
import sqlite3
from pathlib import Path
from typing import Optional

# Third-party
from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

# DTOs (entrada)
from dtos.configuracao_dto import SalvarConfiguracaoLoteDTO

# Schemas (saída)
from dtos.responses.comum import PaginaResponse
from dtos.responses.config_response import (
    ConfigListaResponse,
    SalvarConfigResultadoResponse,
)
from dtos.responses.auditoria_response import AuditoriaResponse

# Models
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import configuracao_repo, auditoria_repo

# Pagination
from util.paginacao_util import Paginacao

# Utilities
from util.api_helpers import checar_rate_limit
from util.auth_decorator import requer_autenticacao
from util.config_cache import config
from util.datetime_util import agora
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import DynamicRateLimiter

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/admin")

# =============================================================================
# Rate Limiters
# =============================================================================

admin_config_limiter = DynamicRateLimiter(
    chave_max="rate_limit_admin_config_max",
    chave_minutos="rate_limit_admin_config_minutos",
    padrao_max=10,
    padrao_minutos=1,
    nome="admin_config",
)


# =============================================================================
# Configurações do Sistema
# =============================================================================

@router.get("/configuracoes", response_model=ConfigListaResponse)
@requer_autenticacao([Perfil.ADMIN.value])
async def get_listar_configuracoes(
    request: Request, usuario_logado: Optional[UsuarioLogado] = None
):
    """Lista todas as configurações do sistema agrupadas por categoria."""
    assert usuario_logado is not None
    try:
        agrupado = configuracao_repo.obter_por_categoria()
    except sqlite3.Error as e:
        logger.error(f"Erro de banco de dados ao listar configurações: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao carregar configurações.",
        )
    return ConfigListaResponse.de_agrupado(agrupado)


@router.put("/configuracoes", response_model=SalvarConfigResultadoResponse)
@requer_autenticacao([Perfil.ADMIN.value])
async def put_salvar_configuracoes(
    request: Request,
    dto: SalvarConfiguracaoLoteDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Atualiza múltiplas configurações de uma vez (salvamento em lote).

    Após salvar, invalida o cache de configurações e regenera o CSS de toast,
    preservando o comportamento da versão original.
    """
    assert usuario_logado is not None
    checar_rate_limit(admin_config_limiter, request)

    try:
        quantidade_atualizada, chaves_nao_encontradas = (
            configuracao_repo.atualizar_multiplas(dto.configs)
        )

        # Invalidar cache de configurações (alterações aplicadas imediatamente)
        config.limpar()

        # Regenerar CSS de toast caso configurações de posição/margem tenham mudado
        from util.toast_css_util import aplicar_css_toast
        aplicar_css_toast()

        logger.info(
            f"Atualização em lote de configurações por admin {usuario_logado.id} - "
            f"{quantidade_atualizada} atualizadas, "
            f"{len(chaves_nao_encontradas)} não encontradas"
        )
    except sqlite3.Error as e:
        logger.error(f"Erro de banco de dados ao salvar configurações em lote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar configurações.",
        )

    if quantidade_atualizada > 0 and chaves_nao_encontradas:
        message = (
            f"{quantidade_atualizada} configurações atualizadas. "
            f"Chaves não encontradas: {', '.join(chaves_nao_encontradas)}."
        )
    elif quantidade_atualizada > 0:
        message = f"{quantidade_atualizada} configurações atualizadas com sucesso."
    else:
        message = "Nenhuma configuração foi atualizada."

    return SalvarConfigResultadoResponse(
        atualizadas=quantidade_atualizada,
        chaves_nao_encontradas=chaves_nao_encontradas,
        message=message,
    )


# =============================================================================
# Auditoria — Log de Arquivo (texto técnico)
# =============================================================================

class LogArquivoResponse(BaseModel):
    """Resultado da leitura do log de arquivo, filtrado por data e nível."""

    data: str = Field(..., description="Data consultada (YYYY-MM-DD)")
    nivel: str = Field(..., description="Nível filtrado (INFO, ERROR, TODOS, ...)")
    total_linhas: int = Field(..., description="Quantidade de linhas retornadas")
    conteudo: str = Field(..., description="Conteúdo do log filtrado (texto puro)")
    erro: Optional[str] = Field(
        default=None, description="Mensagem de erro quando a leitura falha"
    )


def _ler_log_arquivo(data: str, nivel: str) -> tuple[str, int, Optional[str]]:
    """
    Lê arquivo de log e filtra por nível.

    Args:
        data: Data no formato YYYY-MM-DD
        nivel: Nível de log (INFO, WARNING, ERROR, DEBUG, CRITICAL, TODOS)

    Returns:
        Tupla (conteúdo_filtrado, total_linhas, mensagem_erro)
    """
    try:
        # Converter data para formato do arquivo (YYYY.MM.DD)
        data_formatada = data.replace('-', '.')
        arquivo_log = Path(f"logs/app.{data_formatada}.log")

        # Verificar se arquivo existe
        if not arquivo_log.exists():
            return "", 0, f"Nenhum arquivo de log encontrado para a data {data}."

        # Verificar tamanho do arquivo (limite de 10MB para performance)
        tamanho_mb = arquivo_log.stat().st_size / (1024 * 1024)
        if tamanho_mb > 10:
            logger.warning(f"Arquivo de log muito grande ({tamanho_mb:.2f} MB): {arquivo_log}")
            msg = f"Arquivo de log muito grande ({tamanho_mb:.2f} MB). Use ferramentas externas."
            return "", 0, msg

        # Ler arquivo (errors='replace' evita falhar em logs legados gravados
        # em encoding diferente de UTF-8, ex.: cp1252 no Windows)
        with open(arquivo_log, 'r', encoding='utf-8', errors='replace') as f:
            linhas = f.readlines()

        # Filtrar por nível se não for "TODOS"
        if nivel != "TODOS":
            linhas_filtradas = [
                linha for linha in linhas
                if f" - {nivel} - " in linha
            ]
        else:
            linhas_filtradas = linhas

        conteudo = ''.join(linhas_filtradas)
        total = len(linhas_filtradas)

        return conteudo, total, None

    except OSError as e:
        logger.error(f"Erro ao ler arquivo de log: {str(e)}")
        return "", 0, f"Erro ao ler arquivo de log: {str(e)}"


@router.get("/auditoria/logs", response_model=LogArquivoResponse)
@requer_autenticacao([Perfil.ADMIN.value])
async def get_auditoria_logs(
    request: Request,
    data: Optional[str] = Query(
        default=None, description="Data no formato YYYY-MM-DD (padrão: hoje)"
    ),
    nivel: str = Query(
        default="TODOS",
        description="Nível de log (INFO, WARNING, ERROR, DEBUG, CRITICAL, TODOS)",
    ),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Lê o log de arquivo do sistema filtrado por data e nível.

    Substitui as antigas rotas Jinja `GET /auditoria` e `POST /auditoria/filtrar`,
    unificando-as em um único endpoint JSON parametrizado por query string.
    """
    assert usuario_logado is not None
    checar_rate_limit(admin_config_limiter, request)

    data_consulta = data or agora().strftime('%Y-%m-%d')

    conteudo, total_linhas, mensagem_erro = _ler_log_arquivo(data_consulta, nivel)

    logger.info(
        f"Auditoria de logs realizada por admin {usuario_logado.id} - "
        f"Data: {data_consulta}, Nível: {nivel}, Linhas encontradas: {total_linhas}"
    )

    return LogArquivoResponse(
        data=data_consulta,
        nivel=nivel,
        total_linhas=total_linhas,
        conteudo=conteudo,
        erro=mensagem_erro,
    )


# =============================================================================
# Auditoria — Trilha Estruturada (ações de negócio)
# =============================================================================

@router.get("/auditoria/registros", response_model=PaginaResponse[AuditoriaResponse])
@requer_autenticacao([Perfil.ADMIN.value])
async def get_auditoria_registros(
    request: Request,
    pagina: int = Query(default=1, ge=1, description="Número da página (1-based)"),
    acao: str = Query(default="", description="Filtrar por tipo de ação"),
    entidade: str = Query(default="", description="Filtrar por entidade"),
    data_inicio: str = Query(default="", description="Data início (YYYY-MM-DD)"),
    data_fim: str = Query(default="", description="Data fim (YYYY-MM-DD)"),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Lista a trilha de auditoria estruturada com filtros e paginação.

    Diferente do log de arquivo (texto técnico), esta trilha registra
    ações de negócio: quem fez o quê, quando, em qual entidade.
    """
    assert usuario_logado is not None

    por_pagina = 20
    registros, total = auditoria_repo.obter_com_filtros(
        acao=acao or None,
        entidade=entidade or None,
        data_inicio=data_inicio or None,
        data_fim=data_fim or None,
        pagina=pagina,
        por_pagina=por_pagina,
    )

    paginacao = Paginacao(
        items=registros, total=total, pagina_atual=pagina, por_pagina=por_pagina
    )
    items = [AuditoriaResponse.de_registro(r) for r in registros]
    return PaginaResponse.de_paginacao(paginacao, items)
