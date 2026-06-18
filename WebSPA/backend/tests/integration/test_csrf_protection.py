"""
Testes para o módulo util/csrf_protection.py (contrato da API JSON).

O middleware agora VALIDA o token CSRF em métodos mutantes (POST/PUT/PATCH/
DELETE) via header X-CSRF-Token, exceto em paths isentos (/health e webhooks).
GET nunca exige token.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from util.csrf_protection import (
    CSRF_SESSION_KEY,
    CSRF_HEADER_NAME,
    CSRF_PROTECTED_METHODS,
    CSRF_EXEMPT_PATHS,
    gerar_token_csrf,
    obter_token_csrf,
    validar_token_csrf,
    esta_isento_csrf,
    MiddlewareProtecaoCSRF,
)


class TestGerarTokenCSRF:
    """Testes para a função gerar_token_csrf()"""

    def test_gera_token_hex(self):
        """Token gerado deve ser hexadecimal"""
        token = gerar_token_csrf()
        int(token, 16)  # ValueError se não for hex

    def test_gera_token_tamanho_correto(self):
        """Token deve ter 64 caracteres (32 bytes em hex)"""
        assert len(gerar_token_csrf()) == 64

    def test_gera_tokens_unicos(self):
        """Cada chamada deve gerar token diferente"""
        tokens = [gerar_token_csrf() for _ in range(100)]
        assert len(set(tokens)) == 100


class TestObterTokenCSRF:
    """Testes para a função obter_token_csrf()"""

    def test_cria_novo_token_quando_nao_existe(self):
        """Deve criar e salvar novo token se não existe na sessão"""
        request = MagicMock(spec=Request)
        request.session = {}

        with patch("util.csrf_protection.logger"):
            token = obter_token_csrf(request)

        assert token is not None
        assert len(token) == 64
        assert request.session[CSRF_SESSION_KEY] == token

    def test_retorna_token_existente(self):
        """Deve retornar token já presente na sessão"""
        existente = "a" * 64
        request = MagicMock(spec=Request)
        request.session = {CSRF_SESSION_KEY: existente}

        assert obter_token_csrf(request) == existente


class TestValidarTokenCSRF:
    """Testes para a função validar_token_csrf()"""

    def test_token_valido_retorna_true(self):
        """Token igual ao da sessão deve retornar True"""
        token = "a" * 64
        request = MagicMock(spec=Request)
        request.session = {CSRF_SESSION_KEY: token}
        assert validar_token_csrf(request, token) is True

    def test_token_invalido_retorna_false(self):
        """Token diferente do da sessão deve retornar False"""
        request = MagicMock(spec=Request)
        request.session = {CSRF_SESSION_KEY: "a" * 64}
        assert validar_token_csrf(request, "b" * 64) is False

    def test_sem_token_sessao_retorna_false(self):
        """Sem token na sessão deve retornar False e logar"""
        request = MagicMock(spec=Request)
        request.session = {}
        with patch("util.csrf_protection.logger") as mock_logger:
            assert validar_token_csrf(request, "qualquer") is False
            mock_logger.warning.assert_called_once()

    def test_token_none_retorna_false(self):
        """Token None (não enviado) deve retornar False e logar"""
        request = MagicMock(spec=Request)
        request.session = {CSRF_SESSION_KEY: "a" * 64}
        with patch("util.csrf_protection.logger") as mock_logger:
            assert validar_token_csrf(request, None) is False
            mock_logger.warning.assert_called_once()

    def test_token_vazio_retorna_false(self):
        """Token vazio deve retornar False"""
        request = MagicMock(spec=Request)
        request.session = {CSRF_SESSION_KEY: "a" * 64}
        with patch("util.csrf_protection.logger"):
            assert validar_token_csrf(request, "") is False


class TestEstaIsentoCSRF:
    """Testes para a função esta_isento_csrf()"""

    def test_health_isento(self):
        """/health deve ser isento"""
        assert esta_isento_csrf("/health") is True

    def test_webhook_pagamento_isento(self):
        """Webhook de pagamento (server-to-server) deve ser isento"""
        assert esta_isento_csrf("/api/pagamentos/webhook") is True
        assert esta_isento_csrf("/api/pagamentos/webhook?id=1") is True

    def test_api_geral_nao_isenta(self):
        """Rotas /api/ NÃO são isentas (protegidas via header)"""
        assert esta_isento_csrf("/api/login") is False
        assert esta_isento_csrf("/api/usuario/perfil") is False
        assert esta_isento_csrf("/api/") is False

    def test_rotas_normais_nao_isentas(self):
        """Demais rotas não devem ser isentas"""
        for rota in ["/login", "/logout", "/usuarios", "/perfil"]:
            assert esta_isento_csrf(rota) is False, f"{rota} não deveria ser isenta"


class TestMiddlewareProtecaoCSRF:
    """Testes do comportamento do middleware (validação real)"""

    @pytest.fixture
    def app_com_middleware(self):
        """App FastAPI com SessionMiddleware externo ao CSRF."""
        app = FastAPI()
        # Ordem: CSRF interno, Session externo (igual ao main.py)
        app.add_middleware(MiddlewareProtecaoCSRF)
        app.add_middleware(SessionMiddleware, secret_key="test-secret")

        @app.get("/csrf-token")
        async def get_token(request: Request):
            return {"token": obter_token_csrf(request)}

        @app.get("/test")
        async def test_get():
            return {"status": "ok"}

        @app.post("/test")
        async def test_post():
            return {"status": "created"}

        @app.get("/health")
        async def health():
            return {"status": "healthy"}

        @app.post("/api/pagamentos/webhook")
        async def webhook():
            return {"status": "webhook_ok"}

        return app

    def test_get_nunca_exige_token(self, app_com_middleware):
        """GET deve passar sem token"""
        client = TestClient(app_com_middleware)
        assert client.get("/test").status_code == 200

    def test_post_sem_token_bloqueado(self, app_com_middleware):
        """POST sem header X-CSRF-Token deve ser bloqueado (403)"""
        client = TestClient(app_com_middleware)
        response = client.post("/test")
        assert response.status_code == 403
        corpo = response.json()
        assert corpo["type"] == "forbidden"
        assert corpo["errors"] is None

    def test_post_com_token_valido_passa(self, app_com_middleware):
        """POST com header X-CSRF-Token válido deve passar"""
        client = TestClient(app_com_middleware)
        token = client.get("/csrf-token").json()["token"]
        response = client.post("/test", headers={CSRF_HEADER_NAME: token})
        assert response.status_code == 200
        assert response.json()["status"] == "created"

    def test_post_com_token_invalido_bloqueado(self, app_com_middleware):
        """POST com token errado deve ser bloqueado (403)"""
        client = TestClient(app_com_middleware)
        client.get("/csrf-token")  # cria token na sessão
        response = client.post("/test", headers={CSRF_HEADER_NAME: "b" * 64})
        assert response.status_code == 403

    def test_webhook_isento_passa_sem_token(self, app_com_middleware):
        """Webhook isento deve passar sem token"""
        client = TestClient(app_com_middleware)
        assert client.post("/api/pagamentos/webhook").status_code == 200

    def test_health_isento_get(self, app_com_middleware):
        """/health (GET) deve passar normalmente"""
        client = TestClient(app_com_middleware)
        assert client.get("/health").status_code == 200


class TestConstantes:
    """Testes para constantes do módulo"""

    def test_csrf_session_key(self):
        assert CSRF_SESSION_KEY == "_csrf_token"

    def test_csrf_header_name(self):
        assert CSRF_HEADER_NAME == "X-CSRF-Token"

    def test_csrf_protected_methods(self):
        assert "POST" in CSRF_PROTECTED_METHODS
        assert "PUT" in CSRF_PROTECTED_METHODS
        assert "PATCH" in CSRF_PROTECTED_METHODS
        assert "DELETE" in CSRF_PROTECTED_METHODS
        assert "GET" not in CSRF_PROTECTED_METHODS

    def test_csrf_exempt_paths(self):
        assert "/health" in CSRF_EXEMPT_PATHS
        assert "/api/pagamentos/webhook" in CSRF_EXEMPT_PATHS
        # /api/ inteiro NÃO é mais isento
        assert "/api/" not in CSRF_EXEMPT_PATHS
