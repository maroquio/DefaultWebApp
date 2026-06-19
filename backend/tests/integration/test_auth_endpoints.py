"""
Testes de endpoint do módulo de autenticação (routes/auth_routes.py).

Cobre caminhos felizes e tristes de:
    GET  /api/csrf-token
    GET  /api/me
    POST /api/login
    POST /api/logout
    POST /api/cadastrar
    POST /api/esqueci-senha
    POST /api/redefinir-senha

Contrato (ver CLAUDE.md):
    - Sucesso: recurso puro com status correto (200/201) ou MensagemResponse.
    - Erro: {detail, type, errors} via util/exception_handlers.py.
    - Mutações exigem header X-CSRF-Token (senão 403, type="forbidden").
    - Sessão por cookie; @requer_autenticacao() → 401 sem sessão.
"""
import pytest
from fastapi import status

from util.perfis import Perfil


pytestmark = [pytest.mark.integration, pytest.mark.auth]


def _csrf(client):
    """Obtém um token CSRF válido para a sessão do cliente."""
    return client.get("/api/csrf-token").json()["token"]


# =============================================================================
# GET /api/csrf-token
# =============================================================================

class TestCsrfToken:
    def test_retorna_token(self, client):
        resp = client.get("/api/csrf-token")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert "token" in corpo
        assert isinstance(corpo["token"], str)
        assert len(corpo["token"]) == 64

    def test_token_estavel_na_mesma_sessao(self, client):
        primeiro = client.get("/api/csrf-token").json()["token"]
        segundo = client.get("/api/csrf-token").json()["token"]
        assert primeiro == segundo


# =============================================================================
# POST /api/cadastrar
# =============================================================================

class TestCadastrar:
    def _payload(self, **over):
        base = {
            "perfil": Perfil.CLIENTE.value,
            "nome": "Fulano de Tal",
            "email": "fulano@example.com",
            "senha": "Senha@123",
            "confirmar_senha": "Senha@123",
        }
        base.update(over)
        return base

    def test_cadastro_sucesso_retorna_201(self, client):
        token = _csrf(client)
        resp = client.post("/api/cadastrar", json=self._payload(),
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_201_CREATED
        corpo = resp.json()
        assert corpo["email"] == "fulano@example.com"
        assert corpo["nome"] == "Fulano de Tal"
        assert corpo["perfil"] == Perfil.CLIENTE.value
        assert "id" in corpo
        assert "senha" not in corpo  # nunca expor senha

    def test_cadastro_sem_csrf_bloqueado_403(self, client):
        resp = client.post("/api/cadastrar", json=self._payload())
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_cadastro_email_duplicado_409(self, client):
        token = _csrf(client)
        client.post("/api/cadastrar", json=self._payload(),
                    headers={"X-CSRF-Token": token})
        resp = client.post("/api/cadastrar", json=self._payload(),
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_409_CONFLICT
        corpo = resp.json()
        assert corpo["type"] == "conflict"
        assert "email" in corpo["errors"]

    def test_cadastro_senhas_diferentes_422(self, client):
        token = _csrf(client)
        resp = client.post(
            "/api/cadastrar",
            json=self._payload(confirmar_senha="Outra@123"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_cadastro_email_invalido_422(self, client):
        token = _csrf(client)
        resp = client.post("/api/cadastrar", json=self._payload(email="nao-eh-email"),
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_cadastro_senha_fraca_422(self, client):
        token = _csrf(client)
        resp = client.post("/api/cadastrar",
                           json=self._payload(senha="123", confirmar_senha="123"),
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_cadastro_perfil_invalido_422(self, client):
        token = _csrf(client)
        resp = client.post("/api/cadastrar", json=self._payload(perfil="Inexistente"),
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# =============================================================================
# POST /api/login
# =============================================================================

class TestLogin:
    def test_login_sucesso_retorna_usuario(self, client, criar_usuario, usuario_teste):
        criar_usuario(usuario_teste["nome"], usuario_teste["email"], usuario_teste["senha"])
        token = _csrf(client)
        resp = client.post("/api/login",
                           json={"email": usuario_teste["email"], "senha": usuario_teste["senha"]},
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["email"] == usuario_teste["email"]

    def test_login_senha_errada_401(self, client, criar_usuario, usuario_teste):
        criar_usuario(usuario_teste["nome"], usuario_teste["email"], usuario_teste["senha"])
        token = _csrf(client)
        resp = client.post("/api/login",
                           json={"email": usuario_teste["email"], "senha": "Errada@999"},
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_login_email_inexistente_401(self, client):
        token = _csrf(client)
        resp = client.post("/api/login",
                           json={"email": "ninguem@example.com", "senha": "Senha@123"},
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_sem_csrf_403(self, client):
        resp = client.post("/api/login",
                           json={"email": "x@example.com", "senha": "Senha@123"})
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_login_payload_invalido_422(self, client):
        token = _csrf(client)
        resp = client.post("/api/login", json={"email": "invalido", "senha": ""},
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_excede_rate_limit_429(self, client, bloquear_rate_limiter):
        token = _csrf(client)
        with bloquear_rate_limiter("routes.auth_routes.login_limiter"):
            resp = client.post("/api/login",
                               json={"email": "x@example.com", "senha": "Senha@123"},
                               headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in resp.headers


# =============================================================================
# GET /api/me
# =============================================================================

class TestMe:
    def test_me_autenticado_retorna_usuario(self, cliente_autenticado, usuario_teste):
        resp = cliente_autenticado.get("/api/me")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["email"] == usuario_teste["email"]

    def test_me_sem_sessao_401(self, client):
        resp = client.get("/api/me")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# POST /api/logout
# =============================================================================

class TestLogout:
    def test_logout_sucesso(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post("/api/logout", headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_200_OK
        assert "message" in resp.json()
        # Após logout, /me deve negar
        assert cliente_autenticado.get("/api/me").status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_sem_csrf_403(self, cliente_autenticado):
        resp = cliente_autenticado.post("/api/logout")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# POST /api/esqueci-senha
# =============================================================================

class TestEsqueciSenha:
    def test_email_existente_retorna_mensagem(self, client, criar_usuario, usuario_teste):
        criar_usuario(usuario_teste["nome"], usuario_teste["email"], usuario_teste["senha"])
        token = _csrf(client)
        resp = client.post("/api/esqueci-senha", json={"email": usuario_teste["email"]},
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_200_OK
        assert "message" in resp.json()

    def test_email_inexistente_mesma_mensagem(self, client):
        """Anti-enumeração: mesma resposta para e-mail não cadastrado."""
        token = _csrf(client)
        resp = client.post("/api/esqueci-senha", json={"email": "ninguem@example.com"},
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_200_OK
        assert "message" in resp.json()

    def test_email_invalido_422(self, client):
        token = _csrf(client)
        resp = client.post("/api/esqueci-senha", json={"email": "invalido"},
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_sem_csrf_403(self, client):
        resp = client.post("/api/esqueci-senha", json={"email": "x@example.com"})
        assert resp.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# POST /api/redefinir-senha
# =============================================================================

class TestRedefinirSenha:
    def test_token_invalido_400(self, client):
        token = _csrf(client)
        resp = client.post(
            "/api/redefinir-senha",
            json={"token": "token-inexistente", "senha": "Nova@123", "confirmar_senha": "Nova@123"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_senhas_diferentes_422(self, client):
        token = _csrf(client)
        resp = client.post(
            "/api/redefinir-senha",
            json={"token": "qualquer", "senha": "Nova@123", "confirmar_senha": "Outra@123"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_redefinir_com_token_valido_sucesso(self, client, criar_usuario, usuario_teste):
        """Fluxo completo: gera token no banco e redefine a senha."""
        from repo import usuario_repo
        from util.security import gerar_token_redefinicao, obter_data_expiracao_token

        criar_usuario(usuario_teste["nome"], usuario_teste["email"], usuario_teste["senha"])
        token_reset = gerar_token_redefinicao()
        usuario_repo.atualizar_token(
            usuario_teste["email"], token_reset, obter_data_expiracao_token(horas=1)
        )

        csrf = _csrf(client)
        resp = client.post(
            "/api/redefinir-senha",
            json={"token": token_reset, "senha": "NovaSenha@123", "confirmar_senha": "NovaSenha@123"},
            headers={"X-CSRF-Token": csrf},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert "message" in resp.json()

        # Login com a nova senha deve funcionar
        csrf2 = _csrf(client)
        login = client.post("/api/login",
                            json={"email": usuario_teste["email"], "senha": "NovaSenha@123"},
                            headers={"X-CSRF-Token": csrf2})
        assert login.status_code == status.HTTP_200_OK

    def test_sem_csrf_403(self, client):
        resp = client.post(
            "/api/redefinir-senha",
            json={"token": "x", "senha": "Nova@123", "confirmar_senha": "Nova@123"},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
