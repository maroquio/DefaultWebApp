"""
Testes de integração das rotas de autenticação (API JSON).

Cobre login, cadastro, logout, recuperação/redefinição de senha,
/me e /csrf-token sob o prefixo /api.
"""
from fastapi import status
from util.perfis import Perfil


def _csrf(client):
    """Obtém um token CSRF da sessão atual."""
    return client.get("/api/csrf-token").json()["token"]


class TestCsrfToken:
    """Testes do endpoint de handshake CSRF"""

    def test_csrf_token_retorna_token(self, client):
        """GET /api/csrf-token deve retornar um token na sessão"""
        response = client.get("/api/csrf-token")
        assert response.status_code == status.HTTP_200_OK
        corpo = response.json()
        assert "token" in corpo
        assert isinstance(corpo["token"], str)
        assert len(corpo["token"]) == 64


class TestLogin:
    """Testes de login"""

    def test_login_com_credenciais_validas(self, client, criar_usuario, usuario_teste):
        """Deve autenticar e retornar UsuarioResponse (200)"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"],
        )

        token = _csrf(client)
        response = client.post(
            "/api/login",
            json={"email": usuario_teste["email"], "senha": usuario_teste["senha"]},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_200_OK
        corpo = response.json()
        assert corpo["email"] == usuario_teste["email"]
        assert corpo["nome"] == usuario_teste["nome"]
        assert corpo["perfil"] == Perfil.CLIENTE.value
        assert "foto_url" in corpo
        # Senha nunca deve ser exposta
        assert "senha" not in corpo

    def test_login_sem_csrf_retorna_403(self, client, criar_usuario, usuario_teste):
        """POST de login sem header X-CSRF-Token deve ser bloqueado (403)"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"],
        )
        # Garante sessão com token, mas NÃO envia o header
        _csrf(client)

        response = client.post(
            "/api/login",
            json={"email": usuario_teste["email"], "senha": usuario_teste["senha"]},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        corpo = response.json()
        assert corpo["type"] == "forbidden"

    def test_login_com_email_inexistente_retorna_401(self, client):
        """E-mail inexistente deve retornar 401 com mensagem genérica"""
        token = _csrf(client)
        response = client.post(
            "/api/login",
            json={"email": "naoexiste@example.com", "senha": "SenhaQualquer@123"},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        detail = response.json()["detail"]
        assert "e-mail ou senha" in detail.lower()
        # Não deve revelar que o e-mail não existe
        assert "não cadastrado" not in detail.lower()

    def test_login_com_senha_incorreta_retorna_401(self, client, criar_usuario, usuario_teste):
        """Senha incorreta deve retornar 401"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"],
        )

        token = _csrf(client)
        response = client.post(
            "/api/login",
            json={"email": usuario_teste["email"], "senha": "SenhaErrada@123"},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "e-mail ou senha" in response.json()["detail"].lower()

    def test_login_com_email_invalido_retorna_422(self, client):
        """E-mail malformado deve falhar na validação (422)"""
        token = _csrf(client)
        response = client.post(
            "/api/login",
            json={"email": "email-invalido", "senha": "Senha@123"},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        corpo = response.json()
        assert corpo["errors"] is not None
        assert "email" in corpo["errors"]

    def test_login_com_senha_vazia_retorna_422(self, client):
        """Senha vazia/inválida deve falhar na validação (422)"""
        token = _csrf(client)
        response = client.post(
            "/api/login",
            json={"email": "teste@example.com", "senha": ""},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        corpo = response.json()
        assert corpo["errors"] is not None
        assert "senha" in corpo["errors"]


class TestCadastro:
    """Testes de cadastro de usuário"""

    def test_cadastro_com_dados_validos_retorna_201(self, client):
        """Deve cadastrar usuário e retornar UsuarioResponse (201)"""
        token = _csrf(client)
        response = client.post(
            "/api/cadastrar",
            json={
                "perfil": Perfil.CLIENTE.value,
                "nome": "Novo Usuario",
                "email": "novo@example.com",
                "senha": "Senha@123",
                "confirmar_senha": "Senha@123",
            },
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_201_CREATED
        corpo = response.json()
        assert corpo["email"] == "novo@example.com"
        assert corpo["nome"] == "Novo Usuario"
        assert corpo["perfil"] == Perfil.CLIENTE.value
        assert corpo["id"] > 0
        assert "senha" not in corpo

    def test_cadastro_cria_usuario_com_perfil_cliente(self, client):
        """Cadastro deve persistir o usuário com perfil CLIENTE"""
        from repo import usuario_repo

        token = _csrf(client)
        client.post(
            "/api/cadastrar",
            json={
                "perfil": Perfil.CLIENTE.value,
                "nome": "Usuario Teste",
                "email": "persist@example.com",
                "senha": "Senha@123",
                "confirmar_senha": "Senha@123",
            },
            headers={"X-CSRF-Token": token},
        )

        usuario = usuario_repo.obter_por_email("persist@example.com")
        assert usuario is not None
        assert usuario.perfil == Perfil.CLIENTE.value

    def test_cadastro_com_email_duplicado_retorna_409(self, client, criar_usuario, usuario_teste):
        """E-mail já cadastrado deve retornar 409 (conflito)"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"],
        )

        token = _csrf(client)
        response = client.post(
            "/api/cadastrar",
            json={
                "perfil": Perfil.CLIENTE.value,
                "nome": "Outro Nome",
                "email": usuario_teste["email"],
                "senha": "OutraSenha@123",
                "confirmar_senha": "OutraSenha@123",
            },
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        detail = response.json()["detail"]
        # O handler pode aninhar o contrato de erro dentro de detail
        texto = str(detail).lower()
        assert "mail" in texto

    def test_cadastro_com_senhas_diferentes_retorna_422(self, client):
        """Senhas que não coincidem devem falhar na validação (422)"""
        token = _csrf(client)
        response = client.post(
            "/api/cadastrar",
            json={
                "perfil": Perfil.CLIENTE.value,
                "nome": "Usuario Teste",
                "email": "diff@example.com",
                "senha": "Senha@123",
                "confirmar_senha": "SenhaDiferente@123",
            },
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["errors"] is not None

    def test_cadastro_com_senha_fraca_retorna_422(self, client):
        """Senha fraca deve falhar na validação (422)"""
        token = _csrf(client)
        response = client.post(
            "/api/cadastrar",
            json={
                "perfil": Perfil.CLIENTE.value,
                "nome": "Usuario Teste",
                "email": "fraca@example.com",
                "senha": "123456",
                "confirmar_senha": "123456",
            },
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        corpo = response.json()
        assert corpo["errors"] is not None
        assert "senha" in corpo["errors"]


class TestLogout:
    """Testes de logout"""

    def test_logout_retorna_200(self, cliente_autenticado):
        """Logout deve retornar 200 com mensagem"""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.post(
            "/api/logout", headers={"X-CSRF-Token": token}
        )

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

    def test_logout_desautentica_usuario(self, cliente_autenticado):
        """Após logout, /me deve retornar 401"""
        token = _csrf(cliente_autenticado)
        cliente_autenticado.post("/api/logout", headers={"X-CSRF-Token": token})

        response = cliente_autenticado.get("/api/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMe:
    """Testes do endpoint /me"""

    def test_me_autenticado_retorna_usuario(self, cliente_autenticado, usuario_teste):
        """Usuário autenticado deve obter seus próprios dados (200)"""
        response = cliente_autenticado.get("/api/me")
        assert response.status_code == status.HTTP_200_OK
        corpo = response.json()
        assert corpo["email"] == usuario_teste["email"]
        assert corpo["nome"] == usuario_teste["nome"]
        assert "senha" not in corpo

    def test_me_sem_sessao_retorna_401(self, client):
        """Sem sessão, /me deve retornar 401"""
        response = client.get("/api/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRecuperacaoSenha:
    """Testes de recuperação de senha (esqueci-senha)"""

    def test_esqueci_senha_email_existente_retorna_200(self, client, criar_usuario, usuario_teste):
        """E-mail cadastrado deve retornar mensagem genérica (200)"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"],
        )

        token = _csrf(client)
        response = client.post(
            "/api/esqueci-senha",
            json={"email": usuario_teste["email"]},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

    def test_esqueci_senha_email_inexistente_retorna_200(self, client):
        """E-mail inexistente deve retornar a mesma mensagem (anti-enumeração)"""
        token = _csrf(client)
        response = client.post(
            "/api/esqueci-senha",
            json={"email": "naoexiste@example.com"},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_200_OK
        # Mensagem genérica que não revela existência do e-mail
        mensagem = response.json()["message"].lower()
        assert "cadastrado" in mensagem or "recupera" in mensagem

    def test_esqueci_senha_email_invalido_retorna_422(self, client):
        """E-mail malformado deve falhar na validação (422)"""
        token = _csrf(client)
        response = client.post(
            "/api/esqueci-senha",
            json={"email": "email-invalido"},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRedefinirSenha:
    """Testes de redefinição de senha por token"""

    def test_redefinir_senha_com_token_invalido_retorna_400(self, client):
        """Token inexistente deve retornar 400"""
        token = _csrf(client)
        response = client.post(
            "/api/redefinir-senha",
            json={
                "token": "token_nao_existe_xyz123",
                "senha": "NovaSenha@123",
                "confirmar_senha": "NovaSenha@123",
            },
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" in response.json()["detail"].lower()

    def test_redefinir_senha_com_token_expirado_retorna_400(self, client, criar_usuario, usuario_teste):
        """Token expirado deve retornar 400"""
        from repo import usuario_repo
        from util.security import gerar_token_redefinicao
        from datetime import timedelta
        from util.datetime_util import agora

        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"],
        )

        token_reset = gerar_token_redefinicao()
        data_expirada = agora() - timedelta(hours=2)
        usuario_repo.atualizar_token(usuario_teste["email"], token_reset, data_expirada)

        token = _csrf(client)
        response = client.post(
            "/api/redefinir-senha",
            json={
                "token": token_reset,
                "senha": "NovaSenha@123",
                "confirmar_senha": "NovaSenha@123",
            },
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_redefinir_senha_com_dados_validos_retorna_200(self, client, criar_usuario, usuario_teste):
        """Token válido deve permitir redefinir a senha (200)"""
        from repo import usuario_repo
        from util.security import gerar_token_redefinicao, obter_data_expiracao_token

        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"],
        )

        token_reset = gerar_token_redefinicao()
        data_expiracao = obter_data_expiracao_token(horas=1)
        usuario_repo.atualizar_token(usuario_teste["email"], token_reset, data_expiracao)

        token = _csrf(client)
        response = client.post(
            "/api/redefinir-senha",
            json={
                "token": token_reset,
                "senha": "NovaSenhaForte@123",
                "confirmar_senha": "NovaSenhaForte@123",
            },
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

        # A nova senha deve funcionar para login
        token2 = _csrf(client)
        login = client.post(
            "/api/login",
            json={"email": usuario_teste["email"], "senha": "NovaSenhaForte@123"},
            headers={"X-CSRF-Token": token2},
        )
        assert login.status_code == status.HTTP_200_OK

    def test_redefinir_senha_validation_error_retorna_422(self, client, criar_usuario, usuario_teste):
        """Senha nova fraca deve falhar na validação (422)"""
        from repo import usuario_repo
        from util.security import gerar_token_redefinicao, obter_data_expiracao_token

        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"],
        )

        token_reset = gerar_token_redefinicao()
        data_expiracao = obter_data_expiracao_token(horas=1)
        usuario_repo.atualizar_token(usuario_teste["email"], token_reset, data_expiracao)

        token = _csrf(client)
        response = client.post(
            "/api/redefinir-senha",
            json={
                "token": token_reset,
                "senha": "fraca",
                "confirmar_senha": "fraca",
            },
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRateLimiting:
    """Testes de rate limiting no login"""

    def test_multiplas_tentativas_login_retornam_429(self, client):
        """Excedido o limite de tentativas, deve retornar 429"""
        ultimo = None
        for _ in range(8):  # limite padrão é 5
            token = _csrf(client)
            ultimo = client.post(
                "/api/login",
                json={"email": "teste@example.com", "senha": "SenhaErrada@123"},
                headers={"X-CSRF-Token": token},
            )

        # Em algum momento deve bloquear por rate limit
        assert ultimo.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "aguarde" in ultimo.json()["detail"].lower()
