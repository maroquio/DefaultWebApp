"""
Testes para o módulo util/rate_limit_decorator.py

Testa o decorator de rate limiting e funções auxiliares.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient
from starlette.responses import PlainTextResponse
from starlette.middleware.sessions import SessionMiddleware

from util.rate_limit_decorator import (
    obter_identificador_cliente,
    aplicar_rate_limit,
    aplicar_rate_limit_async
)
from util.rate_limiter import RateLimiter


class TestObterIdentificadorCliente:
    """Testes para a função obter_identificador_cliente"""

    def test_ip_via_x_forwarded_for(self):
        """Deve extrair IP do header X-Forwarded-For"""
        request = MagicMock(spec=Request)
        request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1, 172.16.0.1"}
        request.client = MagicMock(host="127.0.0.1")

        ip = obter_identificador_cliente(request)
        assert ip == "192.168.1.1"

    def test_ip_via_x_forwarded_for_unico(self):
        """Deve extrair IP único do header X-Forwarded-For"""
        request = MagicMock(spec=Request)
        request.headers = {"X-Forwarded-For": "10.20.30.40"}
        request.client = MagicMock(host="127.0.0.1")

        ip = obter_identificador_cliente(request)
        assert ip == "10.20.30.40"

    def test_ip_via_x_real_ip(self):
        """Deve usar X-Real-IP se X-Forwarded-For não estiver presente"""
        request = MagicMock(spec=Request)
        request.headers = {"X-Real-IP": "192.168.2.2"}
        request.client = MagicMock(host="127.0.0.1")

        ip = obter_identificador_cliente(request)
        assert ip == "192.168.2.2"

    def test_ip_via_x_real_ip_com_espacos(self):
        """Deve remover espaços do X-Real-IP"""
        request = MagicMock(spec=Request)
        request.headers = {"X-Real-IP": "  192.168.2.2  "}
        request.client = MagicMock(host="127.0.0.1")

        ip = obter_identificador_cliente(request)
        assert ip == "192.168.2.2"

    def test_ip_via_client_host(self):
        """Deve usar client.host se headers não estiverem presentes"""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = MagicMock(host="192.168.3.3")

        ip = obter_identificador_cliente(request)
        assert ip == "192.168.3.3"

    def test_ip_fallback_unknown(self):
        """Deve retornar 'unknown' se nenhum identificador for encontrado"""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = None

        ip = obter_identificador_cliente(request)
        assert ip == "unknown"

    def test_ip_fallback_client_sem_host(self):
        """Deve retornar 'unknown' se client existir mas host for None"""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = MagicMock(host=None)

        ip = obter_identificador_cliente(request)
        assert ip == "unknown"

    def test_prioridade_x_forwarded_for_sobre_x_real_ip(self):
        """X-Forwarded-For deve ter prioridade sobre X-Real-IP"""
        request = MagicMock(spec=Request)
        request.headers = {
            "X-Forwarded-For": "10.0.0.1",
            "X-Real-IP": "20.0.0.2"
        }
        request.client = MagicMock(host="127.0.0.1")

        ip = obter_identificador_cliente(request)
        assert ip == "10.0.0.1"


class TestAplicarRateLimit:
    """Testes para o decorator aplicar_rate_limit"""

    @pytest.fixture
    def limiter_permissivo(self):
        """Cria rate limiter que sempre permite"""
        limiter = MagicMock(spec=RateLimiter)
        limiter.verificar.return_value = True
        limiter.nome = "test_limiter"
        limiter.janela_minutos = 5
        return limiter

    @pytest.fixture
    def limiter_bloqueador(self):
        """Cria rate limiter que sempre bloqueia"""
        limiter = MagicMock(spec=RateLimiter)
        limiter.verificar.return_value = False
        limiter.nome = "test_limiter"
        limiter.janela_minutos = 5
        return limiter

    def test_decorator_requer_rate_limiter(self):
        """Deve levantar TypeError se limiter não for RateLimiter"""
        with pytest.raises(TypeError) as exc_info:
            aplicar_rate_limit("não é um limiter")

        assert "RateLimiter" in str(exc_info.value)

    def test_rate_limit_permitido_executa_funcao(self, limiter_permissivo):
        """Quando rate limit não é excedido, função deve ser executada"""
        app = FastAPI()

        @app.get("/test")
        @aplicar_rate_limit(limiter_permissivo)
        async def test_endpoint(request: Request):
            return PlainTextResponse("Sucesso")

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        assert response.text == "Sucesso"

    def test_rate_limit_bloqueado_retorna_json(self, limiter_bloqueador):
        """Quando rate limit é excedido sem redirect, retorna JSON 429"""
        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="test-secret")

        @app.get("/test")
        @aplicar_rate_limit(limiter_bloqueador)
        async def test_endpoint(request: Request):
            return PlainTextResponse("Sucesso")

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 429
        assert "retry_after" in response.json()

    def test_rate_limit_bloqueado_redireciona(self, limiter_bloqueador):
        """Quando rate limit é excedido com redirect_url, redireciona"""
        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="test-secret")

        @app.get("/blocked")
        async def blocked_endpoint(request: Request):
            return PlainTextResponse("Bloqueado")

        @app.get("/test")
        @aplicar_rate_limit(limiter_bloqueador, redirect_url="/blocked")
        async def test_endpoint(request: Request):
            return PlainTextResponse("Sucesso")

        client = TestClient(app, follow_redirects=False)
        response = client.get("/test")

        assert response.status_code == 303
        assert response.headers.get("location") == "/blocked"

    def test_rate_limit_mensagem_customizada(self, limiter_bloqueador):
        """Deve usar mensagem de erro customizada"""
        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="test-secret")

        @app.get("/test")
        @aplicar_rate_limit(limiter_bloqueador, mensagem_erro="Limite personalizado!")
        async def test_endpoint(request: Request):
            return PlainTextResponse("Sucesso")

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 429
        assert response.json()["detail"] == "Limite personalizado!"

    def test_rate_limit_retry_after_correto(self, limiter_bloqueador):
        """retry_after deve ser baseado na janela do limiter"""
        limiter_bloqueador.janela_minutos = 10
        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="test-secret")

        @app.get("/test")
        @aplicar_rate_limit(limiter_bloqueador)
        async def test_endpoint(request: Request):
            return PlainTextResponse("Sucesso")

        client = TestClient(app)
        response = client.get("/test")

        assert response.json()["retry_after"] == 600  # 10 * 60 segundos

    def test_rate_limit_com_log_detalhes(self, limiter_bloqueador):
        """Deve chamar função de log_detalhes quando bloqueado"""
        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="test-secret")
        log_chamado = []

        def log_callback(ip):
            log_chamado.append(ip)
            return f"IP capturado: {ip}"

        @app.get("/test")
        @aplicar_rate_limit(limiter_bloqueador, log_detalhes=log_callback)
        async def test_endpoint(request: Request):
            return PlainTextResponse("Sucesso")

        client = TestClient(app)
        client.get("/test")

        assert len(log_chamado) == 1

    def test_rate_limit_log_detalhes_com_erro(self, limiter_bloqueador):
        """Deve continuar funcionando mesmo se log_detalhes falhar"""
        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="test-secret")

        def log_callback_com_erro(ip):
            raise ValueError("Erro no callback")

        @app.get("/test")
        @aplicar_rate_limit(limiter_bloqueador, log_detalhes=log_callback_com_erro)
        async def test_endpoint(request: Request):
            return PlainTextResponse("Sucesso")

        client = TestClient(app)
        response = client.get("/test")

        # Mesmo com erro no callback, deve continuar bloqueando
        assert response.status_code == 429


class TestAplicarRateLimitAsync:
    """Testes para o decorator aplicar_rate_limit_async"""

    @pytest.fixture
    def limiter_bloqueador(self):
        """Cria rate limiter que sempre bloqueia"""
        limiter = MagicMock(spec=RateLimiter)
        limiter.verificar.return_value = False
        limiter.nome = "test_limiter"
        limiter.janela_minutos = 5
        return limiter

    def test_async_retorna_json(self, limiter_bloqueador):
        """aplicar_rate_limit_async deve sempre retornar JSON"""
        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="test-secret")

        @app.get("/test")
        @aplicar_rate_limit_async(limiter_bloqueador)
        async def test_endpoint(request: Request):
            return PlainTextResponse("Sucesso")

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 429
        assert "detail" in response.json()

    def test_async_mensagem_customizada(self, limiter_bloqueador):
        """Deve usar mensagem customizada na versão async"""
        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="test-secret")

        @app.get("/test")
        @aplicar_rate_limit_async(limiter_bloqueador, mensagem_erro="API bloqueada")
        async def test_endpoint(request: Request):
            return PlainTextResponse("Sucesso")

        client = TestClient(app)
        response = client.get("/test")

        assert response.json()["detail"] == "API bloqueada"
