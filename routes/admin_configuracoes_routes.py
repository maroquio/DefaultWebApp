# =============================================================================
# Imports
# =============================================================================

# Standard library
import shutil
import sqlite3
from pathlib import Path
from typing import Optional

# Third-party
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

# DTOs
from dtos.configuracao_dto import SalvarConfiguracaoLoteDTO

# Models
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import configuracao_repo

# Utilities
from util.auth_decorator import requer_autenticacao
from util.config_cache import config
from util.datetime_util import agora
from util.flash_messages import informar_sucesso, informar_erro, informar_aviso
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.template_util import criar_templates
from util.validation_util import processar_erros_validacao

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/admin")
templates = criar_templates()

# =============================================================================
# Whitelist de Temas (prevenção de Path Traversal)
# =============================================================================

TEMAS_VALIDOS = frozenset([
    "brite", "cerulean", "cosmo", "cyborg", "darkly", "flatly", "journal",
    "litera", "lumen", "lux", "materia", "minty", "morph", "original",
    "pulse", "quartz", "sandstone", "simplex", "sketchy", "slate", "solar",
    "spacelab", "superhero", "united", "vapor", "yeti", "zephyr"
])

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


# === CRUD de Configurações ===

@router.get("/configuracoes")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_listar_configuracoes(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Lista todas as configurações agrupadas por categoria"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    try:
        # Obter configurações agrupadas por categoria
        configs_por_categoria = configuracao_repo.obter_por_categoria()

        # Calcular total de configurações
        total_configs = sum(len(configs) for configs in configs_por_categoria.values())

        return templates.TemplateResponse(
            "admin/configuracoes/listar.html",
            {
                "request": request,
                "configs_por_categoria": configs_por_categoria,
                "total_configs": total_configs,
                "usuario_logado": usuario_logado,
            }
        )

    except sqlite3.Error as e:
        logger.error(f"Erro de banco de dados ao listar configurações: {e}")
        informar_erro(request, "Erro ao carregar configurações")
        return RedirectResponse("/home", status_code=status.HTTP_303_SEE_OTHER)


# Rotas de edição individual desativadas (substituídas por salvamento em lote)
# Mantidas comentadas para referência histórica
#
# @router.get("/configuracoes/editar/{chave}")
# @router.post("/configuracoes/editar/{chave}")
#
# A edição agora é feita diretamente na tela de listagem com abas,
# salvando múltiplas configurações de uma vez via /configuracoes/salvar-lote


@router.post("/configuracoes/salvar-lote")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_salvar_lote_configuracoes(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Salva múltiplas configurações de uma vez (salvamento em lote).

    Recebe todos os campos do formulário, valida usando SalvarConfiguracaoLoteDTO,
    e atualiza todas as configurações válidas em uma única transação.

    Returns:
        Redirect para listagem com mensagem de sucesso ou erro
    """
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_config_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/configuracoes", status_code=status.HTTP_303_SEE_OTHER)

    try:
        # Obter dados do formulário
        form_data = await request.form()

        # Converter FormData para dict, ignorando campo 'categoria'
        configs = {}
        for key, value in form_data.items():
            if key != "categoria" and value:  # Ignorar categoria e valores vazios
                configs[key] = value

        if not configs:
            informar_aviso(request, "Nenhuma configuração para salvar.")
            return RedirectResponse("/admin/configuracoes", status_code=status.HTTP_303_SEE_OTHER)

        # Validar com DTO
        dto = SalvarConfiguracaoLoteDTO(configs=configs)

        # Atualizar configurações no banco
        quantidade_atualizada, chaves_nao_encontradas = configuracao_repo.atualizar_multiplas(dto.configs)

        # Limpar cache de configurações
        config.limpar()

        # Log de auditoria
        logger.info(
            f"Atualização em lote de configurações por admin {usuario_logado.id} - "
            f"{quantidade_atualizada} atualizadas, {len(chaves_nao_encontradas)} não encontradas"
        )

        # Mensagem de feedback
        if quantidade_atualizada > 0:
            if chaves_nao_encontradas:
                informar_aviso(
                    request,
                    f"{quantidade_atualizada} configurações atualizadas com sucesso! "
                    f"Algumas chaves não foram encontradas: {', '.join(chaves_nao_encontradas)}"
                )
            else:
                informar_sucesso(
                    request,
                    f"{quantidade_atualizada} configurações atualizadas com sucesso! "
                    "Alterações aplicadas imediatamente."
                )
        else:
            informar_erro(request, "Nenhuma configuração foi atualizada.")

        return RedirectResponse("/admin/configuracoes", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Processar erros de validação
        erros = processar_erros_validacao(e)

        # Montar mensagem de erro amigável
        if erros:
            mensagens_erro = []
            for campo, mensagem in erros.items():
                # Remover o prefixo "configs." dos campos se existir
                campo_limpo = campo.replace("configs.", "")
                mensagens_erro.append(f"{campo_limpo}: {mensagem}")

            msg_erro = "Erros de validação: " + "; ".join(mensagens_erro)
        else:
            msg_erro = "Erro ao validar configurações. Verifique os valores informados."

        logger.warning(f"Erro de validação no salvamento em lote: {msg_erro}")
        informar_erro(request, msg_erro)

        # Redirecionar de volta para a listagem
        return RedirectResponse("/admin/configuracoes", status_code=status.HTTP_303_SEE_OTHER)

    except sqlite3.Error as e:
        logger.error(f"Erro de banco de dados ao salvar configurações em lote: {e}")
        informar_erro(request, f"Erro ao salvar configurações: {str(e)}")
        return RedirectResponse("/admin/configuracoes", status_code=status.HTTP_303_SEE_OTHER)


# === Tema Visual ===

@router.get("/tema")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_tema(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe seletor de temas visuais da aplicação"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    # Obter tema atual do banco de dados
    config_tema = configuracao_repo.obter_por_chave("theme")
    tema_atual = config_tema.valor if config_tema else "original"

    # Listar todos os arquivos PNG na pasta de imagens dos temas
    img_dir = Path("static/img/bootswatch")
    temas_disponiveis = []

    if img_dir.exists() and img_dir.is_dir():
        for img_file in sorted(img_dir.glob("*.png")):
            tema_nome = img_file.stem  # Nome do arquivo sem extensão
            # Verificar se existe o arquivo CSS correspondente
            css_file = Path(f"static/css/bootswatch/{tema_nome}.bootstrap.min.css")
            if css_file.exists():
                temas_disponiveis.append({
                    "nome": tema_nome,
                    "nome_exibicao": tema_nome.capitalize(),
                    "imagem": f"/static/img/bootswatch/{img_file.name}",
                    "selecionado": tema_nome == tema_atual
                })

    return templates.TemplateResponse(
        "admin/tema.html",
        {
            "request": request,
            "temas": temas_disponiveis,
            "tema_atual": tema_atual,
            "usuario_logado": usuario_logado,
        }
    )


@router.post("/tema/aplicar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_aplicar_tema(
    request: Request,
    tema: str = Form(...),
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Aplica um tema visual selecionado

    Copia o arquivo CSS do tema para static/css/bootstrap.min.css
    e salva a configuração no banco de dados
    """
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_config_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/tema", status_code=status.HTTP_303_SEE_OTHER)

    try:
        # Obter tema anterior para o log
        config_existente = configuracao_repo.obter_por_chave("theme")

        # Validar tema contra whitelist (prevenção de Path Traversal)
        tema_normalizado = tema.lower().strip()
        if tema_normalizado not in TEMAS_VALIDOS:
            informar_erro(request, f"Tema '{tema}' inválido")
            logger.warning(
                f"Tentativa de aplicar tema inválido por admin {usuario_logado.id}: {tema}"
            )
            return RedirectResponse("/admin/tema", status_code=status.HTTP_303_SEE_OTHER)

        # Construir caminho seguro após validação da whitelist
        css_origem = Path(f"static/css/bootswatch/{tema_normalizado}.bootstrap.min.css")

        if not css_origem.exists():
            informar_erro(request, f"Arquivo do tema '{tema_normalizado}' não encontrado")
            logger.error(f"Arquivo de tema na whitelist não existe: {css_origem}")
            return RedirectResponse("/admin/tema", status_code=status.HTTP_303_SEE_OTHER)

        # Copiar arquivo CSS do tema para bootstrap.min.css
        css_destino = Path("static/css/bootstrap.min.css")
        shutil.copy2(css_origem, css_destino)

        # Atualizar ou inserir configuração no banco (upsert)
        sucesso = configuracao_repo.inserir_ou_atualizar(
            chave="theme",
            valor=tema_normalizado,
            descricao="Tema visual da aplicação (Bootswatch)"
        )

        if sucesso:
            # Limpar cache de configurações
            config.limpar()

            logger.info(
                f"Tema alterado para '{tema_normalizado}' por admin {usuario_logado.id} "
                f"(anterior: {config_existente.valor if config_existente else 'nenhum'})"
            )
            informar_sucesso(
                request,
                f"Tema '{tema_normalizado.capitalize()}' aplicado com sucesso! Recarregue a página para ver as mudanças."
            )
        else:
            logger.error(f"Erro ao salvar configuração de tema '{tema_normalizado}' no banco de dados")
            informar_erro(request, "Erro ao salvar configuração do tema")

    except (sqlite3.Error, OSError) as e:
        # Usa tema original pois tema_normalizado pode não estar definido em caso de exceção precoce
        logger.error(f"Erro ao aplicar tema '{tema}': {str(e)}")
        informar_erro(request, f"Erro ao aplicar tema: {str(e)}")

    return RedirectResponse("/admin/tema", status_code=status.HTTP_303_SEE_OTHER)


def _ler_log_arquivo(data: str, nivel: str) -> tuple[str, int, Optional[str]]:
    """
    Lê arquivo de log e filtra por nível

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

        # Ler arquivo
        with open(arquivo_log, 'r', encoding='utf-8') as f:
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


@router.get("/auditoria")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_auditoria(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe página de auditoria de logs do sistema"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    # Data padrão: hoje
    data_hoje = agora().strftime('%Y-%m-%d')

    return templates.TemplateResponse(
        "admin/auditoria.html",
        {
            "request": request,
            "data_selecionada": data_hoje,
            "nivel_selecionado": "TODOS",
            "usuario_logado": usuario_logado,
        }
    )


@router.post("/auditoria/filtrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_filtrar_auditoria(
    request: Request,
    data: str = Form(...),
    nivel: str = Form(...),
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Filtra logs do sistema por data e nível

    Args:
        data: Data no formato YYYY-MM-DD
        nivel: Nível de log (INFO, WARNING, ERROR, DEBUG, CRITICAL, TODOS)
    """
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_config_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/auditoria", status_code=status.HTTP_303_SEE_OTHER)

    # Ler e filtrar logs
    logs, total_linhas, mensagem_erro = _ler_log_arquivo(data, nivel)

    # Log da ação de auditoria
    logger.info(
        f"Auditoria de logs realizada por admin {usuario_logado.id} - "
        f"Data: {data}, Nível: {nivel}, Linhas encontradas: {total_linhas}"
    )

    return templates.TemplateResponse(
        "admin/auditoria.html",
        {
            "request": request,
            "data_selecionada": data,
            "nivel_selecionado": nivel,
            "logs": logs,
            "total_linhas": total_linhas,
            "mensagem_erro": mensagem_erro,
            "usuario_logado": usuario_logado,
        }
    )
