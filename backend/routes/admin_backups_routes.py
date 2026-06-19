# =============================================================================
# Rotas administrativas de Backups (API JSON) — gerenciamento de backups do banco
# =============================================================================

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import FileResponse

# Schemas (saída)
from dtos.responses.backup_response import BackupInfoResponse
from dtos.responses.comum import MensagemResponse

# Models
from model.usuario_logado_model import UsuarioLogado

# Utilities
from util import backup_util
from util.api_helpers import checar_rate_limit
from util.auth_decorator import requer_autenticacao
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import DynamicRateLimiter

router = APIRouter(prefix="/admin/backups")

# =============================================================================
# Rate Limiters
# =============================================================================

# Operações de backup (MUITO restritivo - operações perigosas)
admin_backups_limiter = DynamicRateLimiter(
    chave_max="rate_limit_admin_backups_max",
    chave_minutos="rate_limit_admin_backups_minutos",
    padrao_max=5,
    padrao_minutos=5,
    nome="admin_backups",
)

# Download de backups
backup_download_limiter = DynamicRateLimiter(
    chave_max="rate_limit_backup_download_max",
    chave_minutos="rate_limit_backup_download_minutos",
    padrao_max=5,
    padrao_minutos=10,
    nome="backup_download",
)


# =============================================================================
# Listagem
# =============================================================================

@router.get("", response_model=List[BackupInfoResponse])
@requer_autenticacao([Perfil.ADMIN.value])
async def listar_backups(
    request: Request, usuario_logado: Optional[UsuarioLogado] = None
):
    """Lista todos os backups disponíveis (mais recentes primeiro)."""
    assert usuario_logado is not None
    backups = backup_util.listar_backups()
    logger.debug(
        f"Admin {usuario_logado.id} listou backups - "
        f"{len(backups)} backup(s) encontrado(s)"
    )
    return [BackupInfoResponse.de_backup_info(b) for b in backups]


# =============================================================================
# Criação
# =============================================================================

@router.post(
    "", response_model=BackupInfoResponse, status_code=status.HTTP_201_CREATED
)
@requer_autenticacao([Perfil.ADMIN.value])
async def criar_backup(
    request: Request, usuario_logado: Optional[UsuarioLogado] = None
):
    """Cria um novo backup manual do banco de dados."""
    assert usuario_logado is not None
    checar_rate_limit(admin_backups_limiter, request)

    sucesso, mensagem = backup_util.criar_backup()
    if not sucesso:
        logger.error(
            f"Erro ao criar backup por admin {usuario_logado.id}: {mensagem}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=mensagem
        )

    logger.info(f"Backup criado por admin {usuario_logado.id}: {mensagem}")

    # Recuperar o backup recém-criado (o mais recente do tipo manual)
    backups = backup_util.listar_backups()
    criado = next((b for b in backups if b.tipo == "manual"), None)
    if criado is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backup criado, mas não foi possível recuperar suas informações.",
        )

    return BackupInfoResponse.de_backup_info(criado)


# =============================================================================
# Download
# =============================================================================

@router.get("/{nome_arquivo}/download")
@requer_autenticacao([Perfil.ADMIN.value])
async def download_backup(
    request: Request,
    nome_arquivo: str,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Faz o download binário de um arquivo de backup."""
    assert usuario_logado is not None
    checar_rate_limit(backup_download_limiter, request)

    # O util valida o nome (proteção contra path traversal) e a existência
    caminho_backup = backup_util.obter_caminho_backup(nome_arquivo)
    if caminho_backup is None or not caminho_backup.exists():
        logger.error(
            f"Tentativa de download de backup inexistente por admin "
            f"{usuario_logado.id}: {nome_arquivo}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup não encontrado.",
        )

    logger.info(
        f"Download de backup por admin {usuario_logado.id}: {nome_arquivo}"
    )
    return FileResponse(
        path=str(caminho_backup),
        filename=nome_arquivo,
        media_type="application/octet-stream",
    )


# =============================================================================
# Restauração
# =============================================================================

@router.post("/{nome_arquivo}/restaurar", response_model=MensagemResponse)
@requer_autenticacao([Perfil.ADMIN.value])
async def restaurar_backup(
    request: Request,
    nome_arquivo: str,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Restaura o banco de dados a partir de um backup.

    A operação sobrescreve o banco atual. Um backup automático de segurança é
    criado antes da restauração e o util valida integridade com rollback.
    """
    assert usuario_logado is not None
    checar_rate_limit(admin_backups_limiter, request)

    logger.warning(
        f"Admin {usuario_logado.id} iniciou restauração de backup: {nome_arquivo}"
    )

    sucesso, mensagem, nome_backup_automatico = backup_util.restaurar_backup(
        nome_arquivo, criar_backup_antes=True
    )

    if not sucesso:
        logger.error(
            f"Erro ao restaurar backup por admin {usuario_logado.id}: {mensagem}"
        )
        # Nome inválido / backup inexistente vs. falha de integridade/rollback
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "não encontrado" in mensagem or "inválido" in mensagem
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(status_code=status_code, detail=mensagem)

    logger.info(
        f"Backup restaurado com sucesso por admin {usuario_logado.id}: {nome_arquivo}"
    )

    if nome_backup_automatico:
        mensagem_completa = (
            f"{mensagem}. Backup de segurança criado automaticamente: "
            f"{nome_backup_automatico}"
        )
    else:
        mensagem_completa = (
            f"{mensagem} (Aviso: não foi possível criar backup de segurança)"
        )

    return MensagemResponse(message=mensagem_completa)


# =============================================================================
# Exclusão
# =============================================================================

@router.delete("/{nome_arquivo}", status_code=status.HTTP_204_NO_CONTENT)
@requer_autenticacao([Perfil.ADMIN.value])
async def excluir_backup(
    request: Request,
    nome_arquivo: str,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Exclui um arquivo de backup."""
    assert usuario_logado is not None
    checar_rate_limit(admin_backups_limiter, request)

    sucesso, mensagem = backup_util.excluir_backup(nome_arquivo)
    if not sucesso:
        logger.error(
            f"Erro ao excluir backup por admin {usuario_logado.id}: {mensagem}"
        )
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "não encontrado" in mensagem or "inválido" in mensagem
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(status_code=status_code, detail=mensagem)

    logger.info(f"Backup excluído por admin {usuario_logado.id}: {nome_arquivo}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
