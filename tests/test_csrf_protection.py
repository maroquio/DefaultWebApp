"""
Testes para o módulo util/csrf_protection.py

Testa a proteção CSRF incluindo geração de tokens,
validação, paths isentos e contexto de template.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from util.csrf_protection import (
    CSRF_SESSION_KEY,
    CSRF_FORM_FIELD,
    CSRF_HEADER_NAME,
    CSRF_PROTECTED_METHODS,
    CSRF_EXEMPT_PATHS,
    gerar_token_csrf,
    obter_token_csrf,
    validar_token_csrf,
    esta_isento_csrf,
    MiddlewareProtecaoCSRF,
    contexto_token_csrf
)


class TestGerarTokenCSRF:
    """Testes para a função gerar_token_csrf()"""

    def test_gera_token_hex(self):
        """Token gerado deve ser hexadecimal"""
        token = gerar_token_csrf()

        # Deve ser string hexadecimal válida
        int(token, 16)  # Se não for hex, levanta ValueError

    def test_gera_token_tamanho_correto(self):
        """Token deve ter 64 caracteres (32 bytes em hex)"""
        token = gerar_token_csrf()

        assert len(token) == 64

    def test_gera_tokens_unicos(self):
        """Cada chamada deve gerar token diferente"""
        tokens = [gerar_token_csrf() for _ in range(100)]

        # Todos devem ser únicos
        assert len(set(tokens)) == 100


class TestObterTokenCSRF:
    """Testes para a função obter_token_csrf()"""

    def test_cria_novo_token_quando_nao_existe(self):
        """Deve criar novo token se não existe na sessão"""
        request = MagicMock(spec=Request)
        request.session = {}

        with patch('util.csrf_protection.logger'):
            token = obter_token_csrf(request)

            # Deve ter criado um token
            assert token is not None
            assert len(token) == 64
            # Deve ter salvado na sessão
            assert CSRF_SESSION_KEY in request.session
            assert request.session[CSRF_SESSION_KEY] == token

    def test_retorna_token_existente(self):
        """Deve retornar token existente da sessão"""
        token_existente = "token_existente_da_sessao_1234567890abcdef1234567890abcdef"
        request = MagicMock(spec=Request)
        request.session = {CSRF_SESSION_KEY: token_existente}

        token = obter_token_csrf(request)

        assert token == token_existente

    def test_loga_quando_cria_novo_token(self):
        """Deve logar quando cria novo token"""
        request = MagicMock(spec=Request)
        request.session = {}

        with patch('util.csrf_protection.logger') as mock_logger:
            obter_token_csrf(request)

            mock_logger.debug.assert_called_once()
            assert "Novo token CSRF" in str(mock_logger.debug.call_args)


class TestValidarTokenCSRF:
    """Testes para a função validar_token_csrf()"""

    def test_token_valido_retorna_true(self):
        """Token correto deve retornar True"""
        token = "a" * 64  # Token de exemplo
        request = MagicMock(spec=Request)
        request.session = {CSRF_SESSION_KEY: token}

        resultado = validar_token_csrf(request, token)

        assert resultado is True

    def test_token_invalido_retorna_false(self):
        """Token errado deve retornar False"""
        token_correto = "a" * 64
        token_errado = "b" * 64
        request = MagicMock(spec=Request)
        request.session = {CSRF_SESSION_KEY: token_correto}

        resultado = validar_token_csrf(request, token_errado)

        assert resultado is False

    def test_sem_token_sessao_retorna_false(self):
        """Sem token na sessão deve retornar False e logar"""
        request = MagicMock(spec=Request)
        request.session = {}

        with patch('util.csrf_protection.logger') as mock_logger:
            resultado = validar_token_csrf(request, "qualquer_token")

            assert resultado is False
            mock_logger.warning.assert_called_once()
            assert "não encontrado na sessão" in str(mock_logger.warning.call_args)

    def test_token_none_retorna_false(self):
        """Token None do formulário deve retornar False e logar"""
        token_sessao = "a" * 64
        request = MagicMock(spec=Request)
        request.session = {CSRF_SESSION_KEY: token_sessao}

        with patch('util.csrf_protection.logger') as mock_logger:
            resultado = validar_token_csrf(request, None)

            assert resultado is False
            mock_logger.warning.assert_called_once()
            assert "não foi enviado" in str(mock_logger.warning.call_args)

    def test_token_vazio_retorna_false(self):
        """Token vazio do formulário deve retornar False"""
        token_sessao = "a" * 64
        request = MagicMock(spec=Request)
        request.session = {CSRF_SESSION_KEY: token_sessao}

        with patch('util.csrf_protection.logger'):
            resultado = validar_token_csrf(request, "")

            assert resultado is False


class TestEstaIsentoCSRF:
    """Testes para a função esta_isento_csrf()"""

    def test_health_isento(self):
        """Rota /health deve ser isenta"""
        assert esta_isento_csrf("/health") is True

    def test_api_isento(self):
        """Rotas /api/ devem ser isentas"""
        assert esta_isento_csrf("/api/") is True
        assert esta_isento_csrf("/api/users") is True
        assert esta_isento_csrf("/api/users/123") is True

    def test_rotas_normais_nao_isentas(self):
        """Rotas normais não devem ser isentas"""
        rotas_nao_isentas = [
            "/login",
            "/logout",
            "/usuarios",
            "/admin/usuarios",
            "/perfil",
            "/home"
        ]

        for rota in rotas_nao_isentas:
            assert esta_isento_csrf(rota) is False, f"{rota} deveria NÃO ser isenta"

    def test_path_parcial_api(self):
        """Paths que contém 'api' mas não iniciam com /api/ não são isentos"""
        assert esta_isento_csrf("/notapi/endpoint") is False
        assert esta_isento_csrf("/my-api-test") is False


class TestMiddlewareProtecaoCSRF:
    """Testes para o middleware de proteção CSRF"""

    @pytest.fixture
    def app_com_middleware(self):
        """Cria app FastAPI com middleware CSRF"""
        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="test-secret")
        app.add_middleware(MiddlewareProtecaoCSRF)

        @app.get("/test")
        async def test_get():
            return {"status": "ok"}

        @app.post("/test")
        async def test_post():
            return {"status": "created"}

        @app.post("/api/test")
        async def api_test():
            return {"status": "api_created"}

        return app

    def test_get_request_passa(self, app_com_middleware):
        """GET requests devem passar sem validação CSRF"""
        client = TestClient(app_com_middleware)

        response = client.get("/test")

        assert response.status_code == 200

    def test_post_request_passa_middleware(self, app_com_middleware):
        """POST requests passam pelo middleware (validação nos handlers)"""
        client = TestClient(app_com_middleware)

        # Middleware não bloqueia, apenas loga
        response = client.post("/test")

        assert response.status_code == 200

    def test_api_post_request(self, app_com_middleware):
        """POST em /api/ deve passar (isento)"""
        client = TestClient(app_com_middleware)

        response = client.post("/api/test")

        assert response.status_code == 200

    def test_middleware_loga_requisicoes_protegidas(self, app_com_middleware):
        """Middleware deve logar requisições em rotas protegidas"""
        client = TestClient(app_com_middleware)

        with patch('util.csrf_protection.logger') as mock_logger:
            client.post("/test")

            # Deve ter logado (debug level)
            mock_logger.debug.assert_called()


class TestContextoTokenCSRF:
    """Testes para a função contexto_token_csrf()"""

    def test_retorna_dicionario_com_campos(self):
        """Deve retornar dict com csrf_token, csrf_input e csrf_form_field"""
        request = MagicMock(spec=Request)
        request.session = {}

        contexto = contexto_token_csrf(request)

        assert "csrf_token" in contexto
        assert "csrf_input" in contexto
        assert "csrf_form_field" in contexto

    def test_csrf_token_valido(self):
        """csrf_token deve ser o token gerado"""
        request = MagicMock(spec=Request)
        request.session = {}

        contexto = contexto_token_csrf(request)

        assert len(contexto["csrf_token"]) == 64

    def test_csrf_input_gera_html(self):
        """csrf_input() deve gerar HTML do input hidden"""
        token = "test_token_" + "a" * 53  # 64 chars
        request = MagicMock(spec=Request)
        request.session = {CSRF_SESSION_KEY: token}

        contexto = contexto_token_csrf(request)
        html = contexto["csrf_input"]()

        assert '<input type="hidden"' in html
        assert f'name="{CSRF_FORM_FIELD}"' in html
        assert f'value="{token}"' in html

    def test_csrf_form_field_correto(self):
        """csrf_form_field deve ser o nome do campo"""
        request = MagicMock(spec=Request)
        request.session = {}

        contexto = contexto_token_csrf(request)

        assert contexto["csrf_form_field"] == CSRF_FORM_FIELD


class TestConstantes:
    """Testes para constantes do módulo"""

    def test_csrf_session_key(self):
        """CSRF_SESSION_KEY deve existir"""
        assert CSRF_SESSION_KEY == "_csrf_token"

    def test_csrf_form_field(self):
        """CSRF_FORM_FIELD deve existir"""
        assert CSRF_FORM_FIELD == "csrf_token"

    def test_csrf_header_name(self):
        """CSRF_HEADER_NAME deve existir"""
        assert CSRF_HEADER_NAME == "X-CSRF-Token"

    def test_csrf_protected_methods(self):
        """CSRF_PROTECTED_METHODS deve conter métodos corretos"""
        assert "POST" in CSRF_PROTECTED_METHODS
        assert "PUT" in CSRF_PROTECTED_METHODS
        assert "PATCH" in CSRF_PROTECTED_METHODS
        assert "DELETE" in CSRF_PROTECTED_METHODS
        assert "GET" not in CSRF_PROTECTED_METHODS

    def test_csrf_exempt_paths(self):
        """CSRF_EXEMPT_PATHS deve conter paths corretos"""
        assert "/health" in CSRF_EXEMPT_PATHS
        assert "/api/" in CSRF_EXEMPT_PATHS
