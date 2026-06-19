"""
Testes de endpoint do módulo de usuário (routes/usuario_routes.py).

Cobre caminhos felizes e tristes de:
    GET  /api/usuario/dashboard
    GET  /api/usuario/perfil
    PUT  /api/usuario/perfil
    PUT  /api/usuario/senha
    PUT  /api/usuario/foto   (base64)

Contrato (ver CLAUDE.md):
    - Todos sob /api/usuario; @requer_autenticacao() → 401 sem sessão.
    - Sucesso: GET→200 (recurso/contadores); PUT→200 (recurso ou MensagemResponse).
    - Erro: {detail, type, errors} via util/exception_handlers.py.
    - Mutações exigem header X-CSRF-Token (senão 403, type="forbidden").
    - 409 e-mail duplicado no PUT /perfil; 400 senha atual incorreta / nova == atual;
      413 foto grande; 400 foto inválida; 429 rate limit.
"""
import pytest
from fastapi import status

from util.perfis import Perfil


pytestmark = [pytest.mark.integration, pytest.mark.auth]


def _csrf(client):
    """Obtém um token CSRF válido para a sessão do cliente."""
    return client.get("/api/csrf-token").json()["token"]


# =============================================================================
# GET /api/usuario/dashboard
# =============================================================================

class TestDashboard:
    def test_dashboard_cliente_retorna_chamados_abertos(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/usuario/dashboard")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        # Visão de usuário comum: chamados_abertos preenchido, pendentes None
        assert corpo["chamados_abertos"] == 0
        assert corpo["chamados_pendentes"] is None

    def test_dashboard_admin_retorna_chamados_pendentes(self, admin_autenticado):
        resp = admin_autenticado.get("/api/usuario/dashboard")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        # Visão admin: chamados_pendentes preenchido, abertos None
        assert corpo["chamados_pendentes"] == 0
        assert corpo["chamados_abertos"] is None

    def test_dashboard_sem_sessao_401(self, client):
        resp = client.get("/api/usuario/dashboard")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# GET /api/usuario/perfil
# =============================================================================

class TestGetPerfil:
    def test_perfil_autenticado_retorna_usuario(self, cliente_autenticado, usuario_teste):
        resp = cliente_autenticado.get("/api/usuario/perfil")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["email"] == usuario_teste["email"]
        assert corpo["nome"] == usuario_teste["nome"]
        assert corpo["perfil"] == Perfil.CLIENTE.value
        assert "id" in corpo
        assert "foto_url" in corpo
        assert "senha" not in corpo  # nunca expor senha

    def test_perfil_sem_sessao_401(self, client):
        resp = client.get("/api/usuario/perfil")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# PUT /api/usuario/perfil
# =============================================================================

class TestPutPerfil:
    def test_atualizar_perfil_sucesso(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/usuario/perfil",
            json={"nome": "Novo Nome", "email": "novo@example.com"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["nome"] == "Novo Nome"
        assert corpo["email"] == "novo@example.com"
        # Sessão sincronizada: /me deve refletir o novo e-mail
        me = cliente_autenticado.get("/api/me")
        assert me.json()["email"] == "novo@example.com"

    def test_atualizar_perfil_mantem_proprio_email(self, cliente_autenticado, usuario_teste):
        """Reusar o próprio e-mail não deve conflitar (409)."""
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/usuario/perfil",
            json={"nome": "Outro Nome", "email": usuario_teste["email"]},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["email"] == usuario_teste["email"]

    def test_atualizar_perfil_sem_csrf_403(self, cliente_autenticado):
        resp = cliente_autenticado.put(
            "/api/usuario/perfil",
            json={"nome": "Novo Nome", "email": "novo@example.com"},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_atualizar_perfil_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.put(
            "/api/usuario/perfil",
            json={"nome": "Novo Nome", "email": "novo@example.com"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_atualizar_perfil_email_duplicado_409(
        self, cliente_autenticado, criar_usuario
    ):
        """E-mail de outro usuário já existente → 409 conflict."""
        criar_usuario("Outro Usuario", "ocupado@example.com", "Senha@123")
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/usuario/perfil",
            json={"nome": "Novo Nome", "email": "ocupado@example.com"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_409_CONFLICT
        corpo = resp.json()
        assert corpo["type"] == "conflict"
        assert "email" in corpo["errors"]

    def test_atualizar_perfil_nome_uma_palavra_422(self, cliente_autenticado):
        """validar_nome_pessoa(min_palavras=2) exige nome completo."""
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/usuario/perfil",
            json={"nome": "Solo", "email": "valido@example.com"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_atualizar_perfil_email_invalido_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/usuario/perfil",
            json={"nome": "Nome Valido", "email": "nao-eh-email"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"


# =============================================================================
# PUT /api/usuario/senha
# =============================================================================

class TestPutSenha:
    def _payload(self, **over):
        base = {
            "senha_atual": "Senha@123",
            "senha_nova": "NovaSenha@123",
            "confirmar_senha": "NovaSenha@123",
        }
        base.update(over)
        return base

    def test_alterar_senha_sucesso(self, cliente_autenticado, usuario_teste):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/usuario/senha",
            json=self._payload(),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert "message" in resp.json()
        # Nova senha deve permitir novo login
        cliente_autenticado.post("/api/logout", headers={"X-CSRF-Token": _csrf(cliente_autenticado)})
        csrf = _csrf(cliente_autenticado)
        login = cliente_autenticado.post(
            "/api/login",
            json={"email": usuario_teste["email"], "senha": "NovaSenha@123"},
            headers={"X-CSRF-Token": csrf},
        )
        assert login.status_code == status.HTTP_200_OK

    def test_alterar_senha_sem_csrf_403(self, cliente_autenticado):
        resp = cliente_autenticado.put("/api/usuario/senha", json=self._payload())
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_alterar_senha_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.put(
            "/api/usuario/senha", json=self._payload(), headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_alterar_senha_atual_incorreta_400(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/usuario/senha",
            json=self._payload(senha_atual="Errada@999"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        corpo = resp.json()
        assert corpo["type"] == "bad_request"
        assert "senha_atual" in corpo["errors"]

    def test_alterar_senha_nova_igual_atual_400(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/usuario/senha",
            json=self._payload(senha_nova="Senha@123", confirmar_senha="Senha@123"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        corpo = resp.json()
        assert corpo["type"] == "bad_request"
        assert "senha_nova" in corpo["errors"]

    def test_alterar_senha_nova_fraca_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/usuario/senha",
            json=self._payload(senha_nova="123", confirmar_senha="123"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_alterar_senha_confirmacao_diferente_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/usuario/senha",
            json=self._payload(confirmar_senha="Diferente@123"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_alterar_senha_excede_rate_limit_429(
        self, cliente_autenticado, bloquear_rate_limiter
    ):
        token = _csrf(cliente_autenticado)
        with bloquear_rate_limiter("routes.usuario_routes.alterar_senha_limiter"):
            resp = cliente_autenticado.put(
                "/api/usuario/senha",
                json=self._payload(),
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert resp.json()["type"] == "rate_limited"
        assert "Retry-After" in resp.headers


# =============================================================================
# PUT /api/usuario/foto
# =============================================================================

class TestPutFoto:
    def test_atualizar_foto_sucesso(self, cliente_autenticado, foto_teste_base64):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/usuario/foto",
            json={"foto_base64": foto_teste_base64},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert "foto_url" in corpo
        assert "id" in corpo

    def test_atualizar_foto_sem_csrf_403(self, cliente_autenticado, foto_teste_base64):
        resp = cliente_autenticado.put(
            "/api/usuario/foto",
            json={"foto_base64": foto_teste_base64},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_atualizar_foto_sem_sessao_401(self, client, foto_teste_base64):
        token = _csrf(client)
        resp = client.put(
            "/api/usuario/foto",
            json={"foto_base64": foto_teste_base64},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_atualizar_foto_base64_curto_422(self, cliente_autenticado):
        """validar_string_obrigatoria(min=100) reprova base64 < 100 chars."""
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/usuario/foto",
            json={"foto_base64": "abc"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_atualizar_foto_invalida_400(self, cliente_autenticado):
        """Base64 com >100 chars mas conteúdo não-imagem → 400 bad_request."""
        token = _csrf(cliente_autenticado)
        lixo = "x" * 200  # passa o min_length=100 mas não é imagem válida
        resp = cliente_autenticado.put(
            "/api/usuario/foto",
            json={"foto_base64": lixo},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json()["type"] == "bad_request"

    def test_atualizar_foto_muito_grande_413(self, cliente_autenticado):
        """Base64 grande (>10MB binário aproximado) → 413."""
        token = _csrf(cliente_autenticado)
        # 10MB binário ~= 14MB de base64; geramos > limiar para forçar 413
        foto_grande = "A" * (15 * 1024 * 1024)
        resp = cliente_autenticado.put(
            "/api/usuario/foto",
            json={"foto_base64": foto_grande},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

    def test_atualizar_foto_excede_rate_limit_429(
        self, cliente_autenticado, foto_teste_base64, bloquear_rate_limiter
    ):
        token = _csrf(cliente_autenticado)
        with bloquear_rate_limiter("routes.usuario_routes.upload_foto_limiter"):
            resp = cliente_autenticado.put(
                "/api/usuario/foto",
                json={"foto_base64": foto_teste_base64},
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert resp.json()["type"] == "rate_limited"
        assert "Retry-After" in resp.headers
