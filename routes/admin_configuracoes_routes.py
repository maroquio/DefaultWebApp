# =============================================================================
# Imports
# =============================================================================

# Standard library
import re
import shutil
import sqlite3
from pathlib import Path
from typing import Optional

# Third-party
from fastapi import APIRouter, File, Form, Request, UploadFile, status
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import ValidationError

# DTOs
from dtos.configuracao_dto import SalvarConfiguracaoLoteDTO

# Models
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import configuracao_repo, auditoria_repo

# Pagination
from util.paginacao_util import Paginacao

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

        # Dados da aba Tema
        from util.tema_css_util import _obter_config_tema
        config_tema_db = configuracao_repo.obter_por_chave("theme")
        tema_atual_nome = config_tema_db.valor if config_tema_db else "original"
        img_dir = Path("static/img/bootswatch")
        temas_disponiveis = []
        if img_dir.exists() and img_dir.is_dir():
            for img_file in sorted(img_dir.glob("*.png")):
                tema_nome = img_file.stem
                css_file = Path(f"static/css/bootswatch/{tema_nome}.bootstrap.min.css")
                if css_file.exists():
                    temas_disponiveis.append({
                        "nome": tema_nome,
                        "nome_exibicao": tema_nome.capitalize(),
                        "imagem": f"/static/img/bootswatch/{img_file.name}",
                        "selecionado": tema_nome == tema_atual_nome,
                    })
        _CHAVES_COR = [
            "tema_cor_primary", "tema_cor_secondary", "tema_cor_success",
            "tema_cor_danger", "tema_cor_warning", "tema_cor_info",
            "tema_cor_light", "tema_cor_dark", "tema_cor_custom",
        ]
        tema_config_cores = {chave: config.obter(chave, "") for chave in _CHAVES_COR}
        tema_identidade = _obter_config_tema()
        tema_fonte_titulos = config.obter("tema_fonte_titulos", "")
        tema_fonte_corpo = config.obter("tema_fonte_corpo", "")
        tema_logo_configurado = bool(config.obter("tema_logo", "").strip())
        tema_favicon_configurado = bool(config.obter("tema_favicon", "").strip())

        return templates.TemplateResponse(
            "admin/configuracoes/listar.html",
            {
                "request": request,
                "configs_por_categoria": configs_por_categoria,
                "total_configs": total_configs,
                "temas": temas_disponiveis,
                "tema_atual_nome": tema_atual_nome,
                "tema_config_cores": tema_config_cores,
                "tema_fonte_titulos": tema_fonte_titulos,
                "tema_fonte_corpo": tema_fonte_corpo,
                "tema_identidade": tema_identidade,
                "tema_logo_configurado": tema_logo_configurado,
                "tema_favicon_configurado": tema_favicon_configurado,
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
    categoria: str = Form(...),
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

        # Regenerar CSS de toast se configurações de posição foram alteradas
        from util.toast_css_util import aplicar_css_toast
        aplicar_css_toast()

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
    """Redireciona para a aba de tema na página de configurações"""
    return RedirectResponse("/admin/configuracoes", status_code=status.HTTP_302_FOUND)


@router.get("/tema-legado")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_tema_legado(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """Exibe seletor de temas visuais da aplicação com abas de personalização"""
    if not usuario_logado:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Tema base atual
    config_tema = configuracao_repo.obter_por_chave("theme")
    tema_atual_nome = config_tema.valor if config_tema else "original"

    # Listar temas disponíveis
    img_dir = Path("static/img/bootswatch")
    temas_disponiveis = []
    if img_dir.exists() and img_dir.is_dir():
        for img_file in sorted(img_dir.glob("*.png")):
            tema_nome = img_file.stem
            css_file = Path(f"static/css/bootswatch/{tema_nome}.bootstrap.min.css")
            if css_file.exists():
                temas_disponiveis.append({
                    "nome": tema_nome,
                    "nome_exibicao": tema_nome.capitalize(),
                    "imagem": f"/static/img/bootswatch/{img_file.name}",
                    "selecionado": tema_nome == tema_atual_nome,
                })

    # Configurações de cores atuais para preencher os campos
    CHAVES_COR = [
        "tema_cor_primary", "tema_cor_secondary", "tema_cor_success",
        "tema_cor_danger", "tema_cor_warning", "tema_cor_info",
        "tema_cor_light", "tema_cor_dark", "tema_cor_custom",
    ]
    config_cores = {chave: config.obter(chave, "") for chave in CHAVES_COR}

    # Configurações de fontes atuais
    from util.tema_css_util import _obter_config_tema

    class _FontesConfig:
        tema_fonte_titulos = config.obter("tema_fonte_titulos", "")
        tema_fonte_corpo = config.obter("tema_fonte_corpo", "")

    # Dados de identidade visual
    tema_atual = _obter_config_tema()
    logo_configurado = bool(config.obter("tema_logo", "").strip())
    favicon_configurado = bool(config.obter("tema_favicon", "").strip())

    return templates.TemplateResponse(
        "admin/tema.html",
        {
            "request": request,
            "temas": temas_disponiveis,
            "tema_atual_nome": tema_atual_nome,
            "config_cores": config_cores,
            "config_fontes": _FontesConfig(),
            "tema_atual": tema_atual,
            "logo_configurado": logo_configurado,
            "favicon_configurado": favicon_configurado,
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
            config.limpar()
            logger.info(
                f"Tema alterado para '{tema_normalizado}' por admin {usuario_logado.id} "
                f"(anterior: {config_existente.valor if config_existente else 'nenhum'})"
            )
            informar_sucesso(
                request,
                f"Tema '{tema_normalizado.capitalize()}' aplicado com sucesso!"
            )
        else:
            logger.error(f"Erro ao salvar configuração de tema '{tema_normalizado}' no banco de dados")
            informar_erro(request, "Erro ao salvar configuração do tema")

    except (sqlite3.Error, OSError) as e:
        logger.error(f"Erro ao aplicar tema '{tema}': {str(e)}")
        informar_erro(request, f"Erro ao aplicar tema: {str(e)}")

    return RedirectResponse("/admin/tema", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/tema/personalizar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_personalizar_tema(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Salva personalização de cores e fontes do tema (AJAX ou form normal).

    Aceita JSON ou form-data com campos:
      tema_cor_primary, tema_cor_secondary, ... (hex #rrggbb ou vazio)
      tema_fonte_titulos, tema_fonte_corpo (nome de fonte ou vazio)
    """
    assert usuario_logado is not None

    ip = obter_identificador_cliente(request)
    if not admin_config_limiter.verificar(ip):
        return JSONResponse(
            {"sucesso": False, "mensagem": "Muitas operações. Aguarde um momento."},
            status_code=429,
        )

    _RE_HEX = re.compile(r'^#[0-9a-fA-F]{6}$')
    _RE_FONTE = re.compile(r'^[a-zA-Z0-9 ]{0,60}$')

    CHAVES_COR = [
        "tema_cor_primary", "tema_cor_secondary", "tema_cor_success",
        "tema_cor_danger", "tema_cor_warning", "tema_cor_info",
        "tema_cor_light", "tema_cor_dark", "tema_cor_custom",
    ]
    CHAVES_FONTE = ["tema_fonte_titulos", "tema_fonte_corpo"]

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
    else:
        form = await request.form()
        body = dict(form)

    configs: dict[str, str] = {}
    erros: list[str] = []

    for chave in CHAVES_COR:
        valor = str(body.get(chave, "")).strip()
        if valor and not _RE_HEX.match(valor):
            erros.append(f"Cor inválida para '{chave}': deve ser #rrggbb")
        else:
            configs[chave] = valor

    for chave in CHAVES_FONTE:
        valor = str(body.get(chave, "")).strip()
        if valor and not _RE_FONTE.match(valor):
            erros.append(f"Nome de fonte inválido para '{chave}'")
        else:
            configs[chave] = valor

    if erros:
        return JSONResponse({"sucesso": False, "mensagem": "; ".join(erros)}, status_code=400)

    try:
        configuracao_repo.atualizar_multiplas(configs)
        config.limpar()
        logger.info(f"Personalização de tema salva por admin {usuario_logado.id}")
        return JSONResponse({"sucesso": True, "mensagem": "Personalização salva com sucesso!"})
    except sqlite3.Error as e:
        logger.error(f"Erro ao salvar personalização de tema: {e}")
        return JSONResponse({"sucesso": False, "mensagem": "Erro ao salvar no banco de dados."}, status_code=500)


@router.post("/tema/logo")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_logo_tema(
    request: Request,
    logo: UploadFile = File(...),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Upload de logo personalizado para o sistema."""
    assert usuario_logado is not None

    from util.upload_util import validar_arquivo, TIPOS_IMAGEM

    TIPOS_LOGO = TIPOS_IMAGEM | {".svg"}
    erro = await validar_arquivo(logo, tipos_permitidos=TIPOS_LOGO, max_bytes=2 * 1024 * 1024)
    if erro:
        return JSONResponse({"sucesso": False, "mensagem": erro}, status_code=400)

    try:
        # Remover logo anterior se existir
        logo_anterior = config.obter("tema_logo", "").strip()
        if logo_anterior:
            Path(f"static/{logo_anterior}").unlink(missing_ok=True)

        # Salvar novo logo com nome fixo (sobrescreve versão anterior)
        extensao = Path(logo.filename).suffix.lower() if logo.filename else ".png"
        pasta = Path("static/img/tema")
        pasta.mkdir(parents=True, exist_ok=True)
        caminho_arquivo = pasta / f"logo{extensao}"

        await logo.seek(0)
        with open(caminho_arquivo, "wb") as f:
            import shutil as _shutil
            _shutil.copyfileobj(logo.file, f)

        caminho_relativo = f"img/tema/logo{extensao}"
        configuracao_repo.inserir_ou_atualizar("tema_logo", caminho_relativo, "[Tema] Caminho do logo personalizado")
        config.limpar()

        logger.info(f"Logo personalizado salvo por admin {usuario_logado.id}: {caminho_relativo}")
        return JSONResponse({
            "sucesso": True,
            "mensagem": "Logo salvo com sucesso!",
            "logo_url": f"/static/{caminho_relativo}",
        })
    except OSError as e:
        logger.error(f"Erro ao salvar logo: {e}")
        return JSONResponse({"sucesso": False, "mensagem": "Erro ao salvar logo."}, status_code=500)


@router.post("/tema/logo/remover")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_remover_logo_tema(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Remove logo personalizado e volta ao padrão."""
    assert usuario_logado is not None

    logo_anterior = config.obter("tema_logo", "").strip()
    if logo_anterior:
        Path(f"static/{logo_anterior}").unlink(missing_ok=True)

    configuracao_repo.inserir_ou_atualizar("tema_logo", "", "[Tema] Caminho do logo personalizado")
    config.limpar()

    logger.info(f"Logo personalizado removido por admin {usuario_logado.id}")
    return JSONResponse({"sucesso": True, "mensagem": "Logo removido. Usando logo padrão."})


@router.post("/tema/favicon")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_favicon_tema(
    request: Request,
    favicon: UploadFile = File(...),
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Upload de favicon personalizado para o sistema."""
    assert usuario_logado is not None

    TIPOS_FAVICON = {".ico", ".png", ".svg"}
    extensao = Path(favicon.filename).suffix.lower() if favicon.filename else ""
    if extensao not in TIPOS_FAVICON:
        return JSONResponse(
            {"sucesso": False, "mensagem": "Favicon deve ser .ico, .png ou .svg"},
            status_code=400,
        )

    conteudo = await favicon.read()
    if len(conteudo) > 512 * 1024:
        return JSONResponse(
            {"sucesso": False, "mensagem": "Favicon não pode exceder 512KB"},
            status_code=400,
        )
    if len(conteudo) == 0:
        return JSONResponse({"sucesso": False, "mensagem": "Arquivo vazio"}, status_code=400)

    try:
        favicon_anterior = config.obter("tema_favicon", "").strip()
        if favicon_anterior:
            Path(f"static/{favicon_anterior}").unlink(missing_ok=True)

        pasta = Path("static/img/tema")
        pasta.mkdir(parents=True, exist_ok=True)
        caminho_arquivo = pasta / f"favicon{extensao}"

        with open(caminho_arquivo, "wb") as f:
            f.write(conteudo)

        caminho_relativo = f"img/tema/favicon{extensao}"
        configuracao_repo.inserir_ou_atualizar("tema_favicon", caminho_relativo, "[Tema] Caminho do favicon personalizado")
        config.limpar()

        logger.info(f"Favicon personalizado salvo por admin {usuario_logado.id}")
        return JSONResponse({
            "sucesso": True,
            "mensagem": "Favicon salvo com sucesso!",
            "favicon_url": f"/static/{caminho_relativo}",
        })
    except OSError as e:
        logger.error(f"Erro ao salvar favicon: {e}")
        return JSONResponse({"sucesso": False, "mensagem": "Erro ao salvar favicon."}, status_code=500)


@router.post("/tema/favicon/remover")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_remover_favicon_tema(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Remove favicon personalizado e volta ao padrão do browser."""
    assert usuario_logado is not None

    favicon_anterior = config.obter("tema_favicon", "").strip()
    if favicon_anterior:
        Path(f"static/{favicon_anterior}").unlink(missing_ok=True)

    configuracao_repo.inserir_ou_atualizar("tema_favicon", "", "[Tema] Caminho do favicon personalizado")
    config.limpar()

    logger.info(f"Favicon personalizado removido por admin {usuario_logado.id}")
    return JSONResponse({"sucesso": True, "mensagem": "Favicon removido."})


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


@router.get("/auditoria/registros")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_auditoria_registros(
    request: Request,
    pagina: int = 1,
    acao: str = "",
    entidade: str = "",
    data_inicio: str = "",
    data_fim: str = "",
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Exibe a trilha de auditoria estruturada com filtros.

    Diferente do log de arquivo (que exibe texto puro),
    esta página exibe registros estruturados de ações de negócio:
    quem fez o quê, quando, em qual entidade.
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

    # Criar objeto Paginacao manualmente para o template
    from util.paginacao_util import Paginacao
    paginacao = Paginacao(items=registros, total=total, pagina_atual=pagina, por_pagina=por_pagina)

    return templates.TemplateResponse(
        "admin/auditoria_registros.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "paginacao": paginacao,
            "registros": registros,
            "filtro_acao": acao,
            "filtro_entidade": entidade,
            "filtro_data_inicio": data_inicio,
            "filtro_data_fim": data_fim,
        }
    )
