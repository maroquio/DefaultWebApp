"""
Testes de integração das rotas de usuário (API JSON, prefixo /api/usuario).

Cobre dashboard, perfil (GET/PUT), alteração de senha (PUT) e foto (PUT).
"""
from fastapi import status
from util.perfis import Perfil


def _csrf(client):
    """Obtém um token CSRF da sessão atual."""
    return client.get("/api/csrf-token").json()["token"]


class TestDashboard:
    """Testes do dashboard do usuário"""

    def test_dashboard_requer_autenticacao(self, client):
        """Sem sessão deve retornar 401"""
        response = client.get("/api/usuario/dashboard")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_dashboard_cliente_retorna_contadores(self, cliente_autenticado):
        """Cliente autenticado recebe contadores do próprio usuário (200)"""
        response = cliente_autenticado.get("/api/usuario/dashboard")
        assert response.status_code == status.HTTP_200_OK
        corpo = response.json()
        # Visão do cliente expõe chamados em aberto
        assert "chamados_abertos" in corpo

    def test_dashboard_admin_retorna_pendentes(self, admin_autenticado):
        """Admin autenticado recebe contadores de visão administrativa (200)"""
        response = admin_autenticado.get("/api/usuario/dashboard")
        assert response.status_code == status.HTTP_200_OK
        corpo = response.json()
        assert "chamados_pendentes" in corpo


class TestObterPerfil:
    """Testes de GET /api/usuario/perfil"""

    def test_perfil_requer_autenticacao(self, client):
        """Sem sessão deve retornar 401"""
        response = client.get("/api/usuario/perfil")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_perfil_autenticado_retorna_dados(self, cliente_autenticado, usuario_teste):
        """Usuário autenticado obtém os próprios dados (200)"""
        response = cliente_autenticado.get("/api/usuario/perfil")
        assert response.status_code == status.HTTP_200_OK
        corpo = response.json()
        assert corpo["nome"] == usuario_teste["nome"]
        assert corpo["email"] == usuario_teste["email"]
        assert corpo["perfil"] == Perfil.CLIENTE.value
        assert "senha" not in corpo


class TestEditarPerfil:
    """Testes de PUT /api/usuario/perfil"""

    def test_editar_perfil_requer_autenticacao(self, client, usuario_teste):
        """Sem sessão deve retornar 401"""
        # Sem header CSRF e sem sessão: mutação é bloqueada antes (403).
        # Com header válido mas sem sessão de usuário, deve dar 401.
        token = _csrf(client)
        response = client.put(
            "/api/usuario/perfil",
            json={"nome": "Nome Qualquer", "email": usuario_teste["email"]},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_editar_perfil_sem_csrf_retorna_403(self, cliente_autenticado, usuario_teste):
        """Mutação sem header X-CSRF-Token deve ser bloqueada (403)"""
        response = cliente_autenticado.put(
            "/api/usuario/perfil",
            json={"nome": "Nome Atualizado", "email": usuario_teste["email"]},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_editar_perfil_com_dados_validos_retorna_200(self, cliente_autenticado, usuario_teste):
        """Deve atualizar nome/e-mail e refletir no GET (200)"""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.put(
            "/api/usuario/perfil",
            json={"nome": "Nome Atualizado", "email": usuario_teste["email"]},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nome"] == "Nome Atualizado"

        # Confirma persistência via GET
        get_resp = cliente_autenticado.get("/api/usuario/perfil")
        assert get_resp.json()["nome"] == "Nome Atualizado"

    def test_editar_perfil_com_email_duplicado_retorna_409(self, client, criar_usuario, usuario_teste):
        """Alterar o e-mail para o de outro usuário deve retornar 409"""
        criar_usuario(usuario_teste["nome"], usuario_teste["email"], usuario_teste["senha"])
        criar_usuario("Outro Usuario", "outro@example.com", "Senha@123")

        # Login como o segundo usuário
        token = _csrf(client)
        client.post(
            "/api/login",
            json={"email": "outro@example.com", "senha": "Senha@123"},
            headers={"X-CSRF-Token": token},
        )

        token = _csrf(client)
        response = client.put(
            "/api/usuario/perfil",
            json={"nome": "Outro Usuario", "email": usuario_teste["email"]},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "mail" in str(response.json()["detail"]).lower()

    def test_editar_perfil_com_email_invalido_retorna_422(self, cliente_autenticado):
        """E-mail malformado deve falhar na validação (422)"""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.put(
            "/api/usuario/perfil",
            json={"nome": "Nome Válido Sobrenome", "email": "email-invalido"},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["errors"] is not None


class TestAlterarSenha:
    """Testes de PUT /api/usuario/senha"""

    def test_alterar_senha_requer_autenticacao(self, client):
        """Sem sessão deve retornar 401"""
        token = _csrf(client)
        response = client.put(
            "/api/usuario/senha",
            json={
                "senha_atual": "Senha@123",
                "senha_nova": "NovaSenha@123",
                "confirmar_senha": "NovaSenha@123",
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_alterar_senha_com_dados_validos_retorna_200(self, cliente_autenticado, usuario_teste):
        """Deve alterar a senha e permitir login com a nova (200)"""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.put(
            "/api/usuario/senha",
            json={
                "senha_atual": usuario_teste["senha"],
                "senha_nova": "NovaSenha@123",
                "confirmar_senha": "NovaSenha@123",
            },
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

        # Logout e login com a nova senha
        token = _csrf(cliente_autenticado)
        cliente_autenticado.post("/api/logout", headers={"X-CSRF-Token": token})

        token = _csrf(cliente_autenticado)
        login = cliente_autenticado.post(
            "/api/login",
            json={"email": usuario_teste["email"], "senha": "NovaSenha@123"},
            headers={"X-CSRF-Token": token},
        )
        assert login.status_code == status.HTTP_200_OK

    def test_alterar_senha_com_senha_atual_incorreta_retorna_400(self, cliente_autenticado):
        """Senha atual errada deve retornar 400"""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.put(
            "/api/usuario/senha",
            json={
                "senha_atual": "SenhaErrada@123",
                "senha_nova": "NovaSenha@123",
                "confirmar_senha": "NovaSenha@123",
            },
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "incorreta" in str(response.json()["detail"]).lower()

    def test_alterar_senha_nova_igual_atual_retorna_400(self, cliente_autenticado, usuario_teste):
        """Nova senha igual à atual deve retornar 400"""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.put(
            "/api/usuario/senha",
            json={
                "senha_atual": usuario_teste["senha"],
                "senha_nova": usuario_teste["senha"],
                "confirmar_senha": usuario_teste["senha"],
            },
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "diferente" in str(response.json()["detail"]).lower()

    def test_alterar_senha_nao_coincidem_retorna_422(self, cliente_autenticado, usuario_teste):
        """Confirmação divergente deve falhar na validação (422)"""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.put(
            "/api/usuario/senha",
            json={
                "senha_atual": usuario_teste["senha"],
                "senha_nova": "NovaSenha@123",
                "confirmar_senha": "SenhaDiferente@123",
            },
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAtualizarFoto:
    """Testes de PUT /api/usuario/foto"""

    def test_atualizar_foto_requer_autenticacao(self, client, foto_teste_base64):
        """Sem sessão deve retornar 401"""
        token = _csrf(client)
        response = client.put(
            "/api/usuario/foto",
            json={"foto_base64": foto_teste_base64},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_atualizar_foto_com_dados_validos_retorna_200(self, cliente_autenticado, foto_teste_base64):
        """Deve atualizar a foto e retornar UsuarioResponse (200)"""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.put(
            "/api/usuario/foto",
            json={"foto_base64": foto_teste_base64},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_200_OK
        corpo = response.json()
        assert "foto_url" in corpo
        assert "id" in corpo

    def test_atualizar_foto_invalida_retorna_400(self, cliente_autenticado):
        """Base64 inválido (mas comprido o suficiente) deve retornar 400"""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.put(
            "/api/usuario/foto",
            json={"foto_base64": "dados-invalidos-" + "x" * 200},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_atualizar_foto_curta_demais_retorna_422(self, cliente_autenticado):
        """Base64 muito curto deve falhar na validação do DTO (422)"""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.put(
            "/api/usuario/foto",
            json={"foto_base64": "abc"},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
