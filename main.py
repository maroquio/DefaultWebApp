import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
from pathlib import Path

# Logger
from util.logger_config import logger

# Repositórios
from repo import usuario_repo, configuracao_repo, tarefa_repo

# Rotas
from routes.auth_routes import router as auth_router
from routes.tarefas_routes import router as tarefas_router
from routes.admin_usuarios_routes import router as admin_usuarios_router
from routes.admin_configuracoes_routes import router as admin_config_router
from routes.perfil_routes import router as perfil_router
from routes.public_routes import router as public_router

# Seeds
from util.seed_data import inicializar_dados

# Criar aplicação FastAPI
app = FastAPI(title="Biblix", version="1.0.0")

# Configurar SessionMiddleware
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-super-segura-mude-isso-em-producao")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

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

    tarefa_repo.criar_tabela()
    logger.info("Tabela 'tarefa' criada/verificada")

except Exception as e:
    logger.error(f"Erro ao criar tabelas: {e}")
    raise

# Inicializar dados seed
logger.info("Inicializando dados seed...")
try:
    inicializar_dados()
    logger.info("Dados seed inicializados com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar dados seed: {e}")

# Incluir routers
# IMPORTANTE: public_router deve ser incluído por último para que a rota "/" funcione corretamente
app.include_router(auth_router, tags=["Autenticação"])
logger.info("Router de autenticação incluído")

app.include_router(perfil_router, tags=["Perfil"])
logger.info("Router de perfil incluído")

app.include_router(tarefas_router, tags=["Tarefas"])
logger.info("Router de tarefas incluído")

app.include_router(admin_usuarios_router, tags=["Admin - Usuários"])
logger.info("Router admin de usuários incluído")

app.include_router(admin_config_router, tags=["Admin - Configurações"])
logger.info("Router admin de configurações incluído")

# Rotas públicas (deve ser por último para não sobrescrever outras rotas)
app.include_router(public_router, tags=["Público"])
logger.info("Router público incluído")

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Iniciando Biblix...")
    logger.info("=" * 60)

    # Configurações do servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "True").lower() == "true"

    logger.info(f"Servidor rodando em http://{host}:{port}")
    logger.info(f"Hot reload: {'Ativado' if reload else 'Desativado'}")
    logger.info(f"Documentação API: http://{host}:{port}/docs")
    logger.info("=" * 60)

    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        raise
