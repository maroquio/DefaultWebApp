import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path

# Configurações
from util.config import APP_NAME, SECRET_KEY, HOST, PORT, RELOAD, VERSION

# Logger
from util.logger_config import logger

# Exception Handlers
from util.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
    form_validation_exception_handler,
)
from util.exceptions import FormValidationError

# Repositórios
from repo import usuario_repo, configuracao_repo, chamado_repo, chamado_interacao_repo, indices_repo
from repo import chat_sala_repo, chat_participante_repo, chat_mensagem_repo

# Rotas
from routes.auth_routes import router as auth_router
from routes.chamados_routes import router as chamados_router
from routes.admin_usuarios_routes import router as admin_usuarios_router
from routes.admin_configuracoes_routes import router as admin_config_router
from routes.admin_backups_routes import router as admin_backups_router
from routes.admin_chamados_routes import router as admin_chamados_router
from routes.usuario_routes import router as usuario_router
from routes.chat_routes import router as chat_router
from routes.public_routes import router as public_router
from routes.examples_routes import router as examples_router

# Seeds
from util.seed_data import inicializar_dados

# Criar aplicação FastAPI
app = FastAPI(title=APP_NAME, version=VERSION)

# Configurar SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Configurar CSRF Protection Middleware
from util.csrf_protection import CSRFProtectionMiddleware
app.add_middleware(CSRFProtectionMiddleware)
logger.info("CSRF Protection habilitado")

# Registrar Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(FormValidationError, form_validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, generic_exception_handler)
logger.info("Exception handlers registrados")

# Montar arquivos estáticos
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Arquivos estáticos montados em /static")

# Criar tabelas do banco de dados
logger.info("Criando tabelas do banco de dados...")
try:
    usuario_repo.criar_tabela()
    logger.info("Tabela 'usuario' criada/verificada")

    configuracao_repo.criar_tabela()
    logger.info("Tabela 'configuracao' criada/verificada")

    chamado_repo.criar_tabela()
    logger.info("Tabela 'chamado' criada/verificada")

    chamado_interacao_repo.criar_tabela()
    logger.info("Tabela 'chamado_interacao' criada/verificada")

    chat_sala_repo.criar_tabela()
    logger.info("Tabela 'chat_sala' criada/verificada")

    chat_participante_repo.criar_tabela()
    logger.info("Tabela 'chat_participante' criada/verificada")

    chat_mensagem_repo.criar_tabela()
    logger.info("Tabela 'chat_mensagem' criada/verificada")

    # Criar índices para otimização de performance
    indices_repo.criar_indices()

except Exception as e:
    logger.error(f"Erro ao criar tabelas: {e}")
    raise

# Inicializar dados seed
try:
    inicializar_dados()
except Exception as e:
    logger.error(f"Erro ao inicializar dados seed: {e}", exc_info=True)

# Migrar configurações do .env para o banco de dados
try:
    from util.migrar_config import migrar_configs_para_banco
    migrar_configs_para_banco()
except Exception as e:
    logger.error(f"Erro ao migrar configurações para banco: {e}", exc_info=True)

# Incluir routers
# IMPORTANTE: public_router deve ser incluído por último para que a rota "/" funcione corretamente
app.include_router(auth_router, tags=["Autenticação"])
logger.info("Router de autenticação incluído")

app.include_router(chamados_router, tags=["Chamados"])
logger.info("Router de chamados incluído")

app.include_router(admin_usuarios_router, tags=["Admin - Usuários"])
logger.info("Router admin de usuários incluído")

app.include_router(admin_config_router, tags=["Admin - Configurações"])
logger.info("Router admin de configurações incluído")

app.include_router(admin_backups_router, tags=["Admin - Backups"])
logger.info("Router admin de backups incluído")

app.include_router(admin_chamados_router, tags=["Admin - Chamados"])
logger.info("Router admin de chamados incluído")

app.include_router(usuario_router, tags=["Usuário"])
logger.info("Router de usuário incluído")

app.include_router(chat_router, tags=["Chat"])
logger.info("Router de chat incluído")

# Rotas públicas (deve ser por último para não sobrescrever outras rotas)
app.include_router(public_router, tags=["Público"])
logger.info("Router público incluído")

# Rotas públicas (deve ser por último para não sobrescrever outras rotas)
app.include_router(examples_router, tags=["Exemplos"])
logger.info("Router de exemplos incluído")

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info(f"Iniciando {APP_NAME} v{VERSION}")
    logger.info("=" * 60)

    logger.info(f"Servidor rodando em http://{HOST}:{PORT}")
    logger.info(f"Hot reload: {'Ativado' if RELOAD else 'Desativado'}")
    logger.info(f"Documentação API: http://{HOST}:{PORT}/docs")
    logger.info("=" * 60)

    try:
        uvicorn.run(
            "main:app",
            host=HOST,
            port=PORT,
            reload=RELOAD,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        raise
