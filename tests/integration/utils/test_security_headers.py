"""
Testes para o módulo util/security_headers.py

Testa os middlewares de segurança HTTP headers e CORS.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import PlainTextResponse

from util.security_headers import MiddlewareSegurancaHeaders, MiddlewareSegurancaCORS


class TestMiddlewareSegurancaHeaders:
    """Testes para o middleware de security headers"""

    @pytest.fixture
    def app_com_middleware(self):
        """Cria aplicação FastAPI com middleware de segurança"""
        app = FastAPI()
        app.add_middleware(MiddlewareSegurancaHeaders)

        @app.get("/test")
        async def test_endpoint():
            return PlainTextResponse("OK")

        return app

    @pytest.fixture
    def client(self, app_com_middleware):
        """Cliente de teste"""
        return TestClient(app_com_middleware)

    def test_header_x_content_type_options(self, client):
        """Deve adicionar X-Content-Type-Options: nosniff"""
        response = client.get("/test")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_header_x_frame_options(self, client):
        """Deve adicionar X-Frame-Options: DENY"""
        response = client.get("/test")
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_header_x_xss_protection(self, client):
        """Deve adicionar X-XSS-Protection: 1; mode=block"""
        response = client.get("/test")
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"

    def test_header_content_security_policy(self, client):
        """Deve adicionar Content-Security-Policy com diretivas corretas"""
        response = client.get("/test")
        csp = response.headers.get("Content-Security-Policy")

        assert csp is not None
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp
        assert "style-src 'self'" in csp
        assert "img-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
        assert "object-src 'none'" in csp
        assert "base-uri 'self'" in csp
        assert "form-action 'self'" in csp

    def test_header_referrer_policy(self, client):
        """Deve adicionar Referrer-Policy: strict-origin-when-cross-origin"""
        response = client.get("/test")
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    def test_header_permissions_policy(self, client):
        """Deve adicionar Permissions-Policy com restrições"""
        response = client.get("/test")
        permissions = response.headers.get("Permissions-Policy")

        assert permissions is not None
        assert "geolocation=()" in permissions
        assert "microphone=()" in permissions
        assert "camera=()" in permissions
        assert "payment=()" in permissions
        assert "usb=()" in permissions

    def test_response_status_ok(self, client):
        """Middleware não deve alterar o status code da resposta"""
        response = client.get("/test")
        assert response.status_code == 200

    def test_response_body_preservado(self, client):
        """Middleware não deve alterar o corpo da resposta"""
        response = client.get("/test")
        assert response.text == "OK"


class TestMiddlewareSegurancaCORS:
    """Testes para o middleware de CORS restritivo"""

    @pytest.fixture
    def app_cors_default(self):
        """Cria aplicação com CORS usando origens padrão"""
        app = FastAPI()
        app.add_middleware(MiddlewareSegurancaCORS)

        @app.get("/test")
        async def test_endpoint():
            return PlainTextResponse("OK")

        return app

    @pytest.fixture
    def app_cors_custom(self):
        """Cria aplicação com CORS usando origens customizadas"""
        app = FastAPI()
        app.add_middleware(
            MiddlewareSegurancaCORS,
            allowed_origins=["http://example.com", "https://trusted.com"]
        )

        @app.get("/test")
        async def test_endpoint():
            return PlainTextResponse("OK")

        return app

    def test_cors_origem_permitida_default(self, app_cors_default):
        """Requisição de origem permitida deve ter headers CORS"""
        client = TestClient(app_cors_default)
        response = client.get("/test", headers={"Origin": "http://localhost:8000"})

        assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:8000"
        assert response.headers.get("Access-Control-Allow-Credentials") == "true"
        assert "GET" in response.headers.get("Access-Control-Allow-Methods", "")
        assert "POST" in response.headers.get("Access-Control-Allow-Methods", "")

    def test_cors_origem_nao_permitida(self, app_cors_default):
        """Requisição de origem não permitida não deve ter headers CORS"""
        client = TestClient(app_cors_default)
        response = client.get("/test", headers={"Origin": "http://malicious.com"})

        assert response.headers.get("Access-Control-Allow-Origin") is None

    def test_cors_sem_header_origin(self, app_cors_default):
        """Requisição sem header Origin não deve ter headers CORS"""
        client = TestClient(app_cors_default)
        response = client.get("/test")

        assert response.headers.get("Access-Control-Allow-Origin") is None

    def test_cors_origem_customizada_permitida(self, app_cors_custom):
        """Origem customizada permitida deve ter headers CORS"""
        client = TestClient(app_cors_custom)
        response = client.get("/test", headers={"Origin": "http://example.com"})

        assert response.headers.get("Access-Control-Allow-Origin") == "http://example.com"

    def test_cors_origem_customizada_https(self, app_cors_custom):
        """Origem HTTPS customizada permitida deve ter headers CORS"""
        client = TestClient(app_cors_custom)
        response = client.get("/test", headers={"Origin": "https://trusted.com"})

        assert response.headers.get("Access-Control-Allow-Origin") == "https://trusted.com"

    def test_cors_origem_customizada_nao_permitida(self, app_cors_custom):
        """Origem não na lista customizada não deve ter headers CORS"""
        client = TestClient(app_cors_custom)
        response = client.get("/test", headers={"Origin": "http://localhost:8000"})

        assert response.headers.get("Access-Control-Allow-Origin") is None

    def test_cors_headers_methods(self, app_cors_default):
        """Deve incluir métodos permitidos no header"""
        client = TestClient(app_cors_default)
        response = client.get("/test", headers={"Origin": "http://localhost:8000"})

        methods = response.headers.get("Access-Control-Allow-Methods", "")
        assert "GET" in methods
        assert "POST" in methods
        assert "PUT" in methods
        assert "DELETE" in methods
        assert "OPTIONS" in methods

    def test_cors_headers_allowed_headers(self, app_cors_default):
        """Deve incluir headers permitidos"""
        client = TestClient(app_cors_default)
        response = client.get("/test", headers={"Origin": "http://localhost:8000"})

        headers_permitidos = response.headers.get("Access-Control-Allow-Headers", "")
        assert "Content-Type" in headers_permitidos
        assert "Authorization" in headers_permitidos

    def test_response_preservada_com_cors(self, app_cors_default):
        """Resposta deve ser preservada mesmo com headers CORS"""
        client = TestClient(app_cors_default)
        response = client.get("/test", headers={"Origin": "http://localhost:8000"})

        assert response.status_code == 200
        assert response.text == "OK"
