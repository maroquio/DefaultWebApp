"""
Rotas administrativas para gerenciamento de backups do banco de dados.

Permite ao administrador criar, listar, restaurar e excluir backups do banco SQLite.
"""
from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse, FileResponse

from model.usuario_logado_model import UsuarioLogado
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util import backup_util
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente


router = APIRouter(prefix="/admin/backups")
templates = criar_templates()

# Rate limiter para operações de backup (MUITO restritivo - operações perigosas)
admin_backups_limiter = DynamicRateLimiter(
    chave_max="rate_limit_admin_backups_max",
    chave_minutos="rate_limit_admin_backups_minutos",
    padrao_max=5,
    padrao_minutos=5,
    nome="admin_backups",
)

# Rate limiter específico para download de backups
backup_download_limiter = DynamicRateLimiter(
    chave_max="rate_limit_backup_download_max",
    chave_minutos="rate_limit_backup_download_minutos",
    padrao_max=5,
    padrao_minutos=10,
    nome="backup_download",
)


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_listar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """
    Exibe lista de backups disponíveis

    Lista todos os backups existentes com informações de data/hora e tamanho.
    """
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Obter lista de backups
    backups = backup_util.listar_backups()

    logger.debug(f"Admin {usuario_logado.id} acessou página de backups - {len(backups)} backup(s) encontrado(s)")

    return templates.TemplateResponse(
        "admin/backups/listar.html",
        {
            "request": request,
            "backups": backups,
            "usuario_logado": usuario_logado,
        }
    )


@router.post("/criar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_criar(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """
    Cria um novo backup do banco de dados

    Copia o arquivo database.db para backups/ com timestamp no nome.
    """
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_backups_limiter.verificar(ip):
        informar_erro(request, "Muitas operações de backup. Aguarde alguns minutos e tente novamente.")
        return RedirectResponse("/admin/backups/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Criar backup
    sucesso, mensagem = backup_util.criar_backup()

    if sucesso:
        logger.info(f"Backup criado por admin {usuario_logado.id}: {mensagem}")
        informar_sucesso(request, mensagem)
    else:
        logger.error(f"Erro ao criar backup por admin {usuario_logado.id}: {mensagem}")
        informar_erro(request, mensagem)

    return RedirectResponse(
        "/admin/backups/listar",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/restaurar/{nome_arquivo}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_restaurar(
    request: Request,
    nome_arquivo: str,
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Restaura um backup do banco de dados

    IMPORTANTE: Esta operação sobrescreve o banco de dados atual!
    Um backup automático do estado atual é criado antes da restauração.

    Args:
        nome_arquivo: Nome do arquivo de backup a restaurar
    """
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_backups_limiter.verificar(ip):
        informar_erro(request, "Muitas operações de backup. Aguarde alguns minutos e tente novamente.")
        return RedirectResponse("/admin/backups/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Log da tentativa de restauração
    logger.warning(
        f"Admin {usuario_logado.id} iniciou restauração de backup: {nome_arquivo}"
    )

    # Restaurar backup (com backup automático do estado atual)
    sucesso, mensagem, nome_backup_automatico = backup_util.restaurar_backup(
        nome_arquivo,
        criar_backup_antes=True
    )

    if sucesso:
        logger.info(
            f"Backup restaurado com sucesso por admin {usuario_logado.id}: {nome_arquivo}"
        )

        # Mensagem com informação sobre o backup automático criado
        if nome_backup_automatico:
            mensagem_completa = (
                f"{mensagem}. "
                f"✓ Backup de segurança criado automaticamente: {nome_backup_automatico}"
            )
        else:
            mensagem_completa = f"{mensagem} (Aviso: Não foi possível criar backup de segurança)"

        informar_sucesso(request, mensagem_completa)
    else:
        logger.error(
            f"Erro ao restaurar backup por admin {usuario_logado.id}: {mensagem}"
        )
        informar_erro(request, mensagem)

    return RedirectResponse(
        "/admin/backups/listar",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/excluir/{nome_arquivo}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(
    request: Request,
    nome_arquivo: str,
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Exclui um arquivo de backup

    Args:
        nome_arquivo: Nome do arquivo de backup a excluir
    """
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_backups_limiter.verificar(ip):
        informar_erro(request, "Muitas operações de backup. Aguarde alguns minutos e tente novamente.")
        return RedirectResponse("/admin/backups/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Excluir backup
    sucesso, mensagem = backup_util.excluir_backup(nome_arquivo)

    if sucesso:
        logger.info(f"Backup excluído por admin {usuario_logado.id}: {nome_arquivo}")
        informar_sucesso(request, mensagem)
    else:
        logger.error(f"Erro ao excluir backup por admin {usuario_logado.id}: {mensagem}")
        informar_erro(request, mensagem)

    return RedirectResponse(
        "/admin/backups/listar",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/download/{nome_arquivo}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_download(
    request: Request,
    nome_arquivo: str,
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Faz download de um arquivo de backup

    Args:
        nome_arquivo: Nome do arquivo de backup para download

    Returns:
        FileResponse com o arquivo de backup
    """
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not backup_download_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas tentativas de download. Aguarde alguns minutos.",
        )
        logger.warning(f"Rate limit excedido para download de backup - IP: {ip}")
        return RedirectResponse(
            "/admin/backups/listar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Obter caminho do backup
    caminho_backup = backup_util.obter_caminho_backup(nome_arquivo)

    if caminho_backup is None or not caminho_backup.exists():
        logger.error(
            f"Tentativa de download de backup inexistente por admin {usuario_logado.id}: {nome_arquivo}"
        )
        # Não é possível usar flash message aqui pois é um download
        # Retornar 404 ou redirecionar
        return RedirectResponse(
            "/admin/backups/listar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    logger.info(f"Download de backup por admin {usuario_logado.id}: {nome_arquivo}")

    return FileResponse(
        path=str(caminho_backup),
        filename=nome_arquivo,
        media_type="application/octet-stream"
    )
