import os
import uvicorn
import sqlite3
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path

# Configurações
from util.config import APP_NAME, SECRET_KEY, HOST, PORT, RELOAD, VERSION, IS_DEVELOPMENT

# Logger
from util.logger_config import logger

# Exception Handlers (JSON)
from util.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

# Repositórios (criação das tabelas)
from repo import (
    usuario_repo,
    configuracao_repo,
    chamado_repo,
    chamado_interacao_repo,
    indices_repo,
    notificacao_repo,
    auditoria_repo,
    pagamento_repo,
)
from repo import chat_sala_repo, chat_participante_repo, chat_mensagem_repo

# Rotas (API JSON)
from routes.auth_routes import router as auth_router
from routes.usuario_routes import router as usuario_router
from routes.chamados_routes import router as chamados_router
from routes.admin_chamados_routes import router as admin_chamados_router
from routes.chat_routes import router as chat_router
from routes.notificacao_routes import router as notificacao_router
from routes.admin_configuracoes_routes import router as admin_config_router
from routes.pagamento_routes import router as pagamento_router
from routes.admin_pagamentos_routes import router as admin_pagamentos_router
from routes.admin_backups_routes import router as admin_backups_router
from routes.admin_usuarios_routes import router as admin_usuarios_router

# Seeds
from util.seed_data import inicializar_dados

# CSRF Protection
from util.csrf_protection import MiddlewareProtecaoCSRF

# Security headers
from util.security_headers import MiddlewareSegurancaHeaders

# Prefixo único da API
API_PREFIX = "/api"

# Criar aplicação FastAPI
app = FastAPI(title=APP_NAME, version=VERSION)

# ---------------------------------------------------------------------------
# Middlewares
# Ordem importa: o último add_middleware é o mais externo. SessionMiddleware
# precisa ser externo ao CSRF para que request.session já exista na validação.
# ---------------------------------------------------------------------------
app.add_middleware(MiddlewareProtecaoCSRF)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, same_site="lax")
# Headers de segurança: mais externo, aplica a todas as respostas (inclusive erros)
app.add_middleware(MiddlewareSegurancaHeaders)
logger.info("Middlewares (Segurança + Session + CSRF) habilitados")

# ---------------------------------------------------------------------------
# Exception Handlers (todos retornam JSON no contrato padronizado)
# ---------------------------------------------------------------------------
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
logger.info("Exception handlers JSON registrados")

# ---------------------------------------------------------------------------
# Arquivos estáticos (uploads e mídia). Mantido para servir fotos de perfil.
# ---------------------------------------------------------------------------
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Arquivos estáticos montados em /static")

# ---------------------------------------------------------------------------
# Criação de tabelas e seed
# ---------------------------------------------------------------------------
TABELAS = [
    (usuario_repo, "usuario"),
    (configuracao_repo, "configuracao"),
    (chamado_repo, "chamado"),
    (chamado_interacao_repo, "chamado_interacao"),
    (chat_sala_repo, "chat_sala"),
    (chat_participante_repo, "chat_participante"),
    (chat_mensagem_repo, "chat_mensagem"),
    (notificacao_repo, "notificacao"),
    (auditoria_repo, "auditoria"),
    (pagamento_repo, "pagamento"),
]

logger.info("Criando tabelas do banco de dados...")
try:
    for repo, nome in TABELAS:
        repo.criar_tabela()
        logger.info(f"Tabela '{nome}' criada/verificada")
    indices_repo.criar_indices()
except sqlite3.Error as e:
    logger.error(f"Erro ao criar tabelas: {e}")
    raise

try:
    inicializar_dados()
except sqlite3.Error as e:
    logger.error(f"Erro ao inicializar dados seed: {e}", exc_info=True)

# Migrar configurações do .env para o banco (config híbrida)
try:
    from util.migrar_config import (
        migrar_configs_para_banco,
        garantir_configs_pagamento,
    )

    migrar_configs_para_banco()
    garantir_configs_pagamento()
except sqlite3.Error as e:
    logger.error(f"Erro ao migrar configurações: {e}", exc_info=True)

# ---------------------------------------------------------------------------
# Routers (todos sob /api)
# ---------------------------------------------------------------------------
ROUTERS = [
    (auth_router, ["Autenticação"], "autenticação"),
    (usuario_router, ["Usuário"], "usuário"),
    (chamados_router, ["Chamados"], "chamados"),
    (admin_chamados_router, ["Admin - Chamados"], "admin de chamados"),
    (chat_router, ["Chat"], "chat"),
    (notificacao_router, ["Notificações"], "notificações"),
    (admin_config_router, ["Admin - Configurações"], "admin de configurações"),
    (pagamento_router, ["Pagamentos"], "pagamentos"),
    (admin_pagamentos_router, ["Admin - Pagamentos"], "admin de pagamentos"),
    (admin_backups_router, ["Admin - Backups"], "admin de backups"),
    (admin_usuarios_router, ["Admin - Usuários"], "admin de usuários"),
]

for router, tags, nome in ROUTERS:
    app.include_router(router, prefix=API_PREFIX, tags=tags)
    logger.info(f"Router de {nome} incluído em {API_PREFIX}")


@app.get("/health", tags=["Infra"])
async def health_check():
    """Endpoint de health check."""
    return {"status": "healthy"}


# ---------------------------------------------------------------------------
# Catch-all SPA (apenas em produção, quando o build do React existir).
# Registrado por ÚLTIMO para não capturar /api nem /static.
# ---------------------------------------------------------------------------
SPA_DIST_PATH = Path(os.getenv("SPA_DIST_PATH", "../frontend/dist"))
if not IS_DEVELOPMENT and SPA_DIST_PATH.exists():
    index_html = SPA_DIST_PATH / "index.html"
    app.mount(
        "/assets",
        StaticFiles(directory=str(SPA_DIST_PATH / "assets")),
        name="spa-assets",
    )

    # Fallback do SPA via handler de 404 (em vez de uma rota catch-all).
    # Uma rota "/{path:path}" sombrearia as URLs de API sem barra final
    # (ex: GET /api/admin/usuarios), devolvendo o index.html no lugar de
    # acionar o redirect 307 para a versão com barra (/api/admin/usuarios/).
    # Com o fallback de 404, apenas requisições de NAVEGAÇÃO (GET de páginas
    # que não casam nenhuma rota) recebem o index.html; /api segue retornando
    # JSON (inclusive o redirect de barra final das coleções).
    async def spa_fallback_handler(request, exc):
        if (
            exc.status_code == 404
            and request.method in ("GET", "HEAD")
            and not request.url.path.startswith(("/api", "/static", "/assets"))
        ):
            return FileResponse(index_html)
        return await http_exception_handler(request, exc)

    app.add_exception_handler(StarletteHTTPException, spa_fallback_handler)

    logger.info(f"SPA servido a partir de {SPA_DIST_PATH} (fallback 404)")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info(f"Iniciando {APP_NAME} v{VERSION} (API JSON)")
    logger.info("=" * 60)
    logger.info(f"Servidor: http://{HOST}:{PORT}")
    logger.info(f"Documentação: http://{HOST}:{PORT}/docs")
    logger.info("=" * 60)

    try:
        uvicorn.run(
            "main:app",
            host=HOST,
            port=PORT,
            reload=RELOAD,
            log_level="info",
            # Honra X-Forwarded-Proto/-For quando atrás de proxy reverso (TLS),
            # garantindo scheme https em redirects e url_for.
            proxy_headers=True,
            forwarded_allow_ips="*",
        )
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        raise
