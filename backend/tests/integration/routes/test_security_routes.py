"""
Testes de segurança da API JSON.

Cobre:
- Headers de segurança (util/security_headers.py)
- SQL Injection (prepared statements + validação de path param int)
- Escalação de privilégios (401/403 por perfil)
- Isolamento de sessão
- Segurança de senha (hash bcrypt, não-vazamento)
- Não-divulgação de informações sensíveis
"""
from fastapi import status
from util.perfis import Perfil


def _csrf(client):
    """Obtém um token CSRF da sessão atual."""
    return client.get("/api/csrf-token").json()["token"]


class TestSecurityHeaders:
    """Headers de segurança aplicados pelo middleware"""

    def test_headers_seguranca_presentes(self, client):
        """Respostas devem conter os principais headers de segurança"""
        response = client.get("/health")
        headers = response.headers
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert headers.get("X-Frame-Options") == "DENY"
        assert "Content-Security-Policy" in headers
        assert "Referrer-Policy" in headers
        assert "Permissions-Policy" in headers

    def test_csp_restringe_origens(self, client):
        """CSP deve declarar default-src 'self'"""
        response = client.get("/health")
        csp = response.headers.get("Content-Security-Policy", "")
        assert "default-src 'self'" in csp


class TestSQLInjection:
    """Proteção contra SQL Injection"""

    def test_login_com_sql_injection_no_email_retorna_422(self, client, criar_usuario, usuario_teste):
        """Payload de SQL injection no e-mail não deve autenticar"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"],
        )

        token = _csrf(client)
        response = client.post(
            "/api/login",
            json={"email": "' OR '1'='1' --", "senha": "Senha@123"},
            headers={"X-CSRF-Token": token},
        )

        # E-mail malformado é barrado na validação (não autentica de forma alguma)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_obter_usuario_id_nao_numerico_retorna_422(self, admin_autenticado):
        """ID não numérico no path deve ser rejeitado pela validação (422)"""
        response = admin_autenticado.get("/api/admin/usuarios/1 OR 1=1")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestEscalacaoPrivilegios:
    """Proteção contra escalação de privilégios"""

    def test_nao_autenticado_em_area_admin_retorna_401(self, client):
        """Sem sessão, área admin deve retornar 401"""
        response = client.get("/api/admin/usuarios")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cliente_nao_acessa_admin_usuarios_retorna_403(self, cliente_autenticado):
        """Cliente autenticado em área admin deve receber 403"""
        response = cliente_autenticado.get("/api/admin/usuarios")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cliente_nao_cria_usuario_admin_retorna_403(self, cliente_autenticado):
        """Cliente não deve poder criar usuário via endpoint admin (403)"""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.post(
            "/api/admin/usuarios",
            json={
                "nome": "Hacker Admin",
                "email": "hacker@example.com",
                "senha": "Senha@123",
                "perfil": Perfil.ADMIN.value,
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_vendedor_nao_acessa_backups_retorna_403(self, vendedor_autenticado):
        """Vendedor não deve acessar backups (admin-only)"""
        response = vendedor_autenticado.get("/api/admin/backups")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_acessa_admin_usuarios_retorna_200(self, admin_autenticado):
        """Admin deve acessar a listagem de usuários (200)"""
        response = admin_autenticado.get("/api/admin/usuarios")
        assert response.status_code == status.HTTP_200_OK
        corpo = response.json()
        assert "items" in corpo


class TestSessionSecurity:
    """Segurança de sessão"""

    def test_logout_invalida_sessao(self, cliente_autenticado):
        """Após logout, rota protegida deve retornar 401"""
        # Confirma sessão ativa
        assert cliente_autenticado.get("/api/me").status_code == status.HTTP_200_OK

        token = _csrf(cliente_autenticado)
        cliente_autenticado.post("/api/logout", headers={"X-CSRF-Token": token})

        assert cliente_autenticado.get("/api/me").status_code == status.HTTP_401_UNAUTHORIZED

    def test_sessao_nao_compartilhada_entre_usuarios(self, client, criar_usuario):
        """Login sequencial deve refletir apenas o usuário atual"""
        criar_usuario("Usuario Um", "user1@example.com", "Senha@123")
        criar_usuario("Usuario Dois", "user2@example.com", "Senha@123")

        token = _csrf(client)
        client.post(
            "/api/login",
            json={"email": "user1@example.com", "senha": "Senha@123"},
            headers={"X-CSRF-Token": token},
        )
        assert client.get("/api/me").json()["email"] == "user1@example.com"

        token = _csrf(client)
        client.post("/api/logout", headers={"X-CSRF-Token": token})

        token = _csrf(client)
        client.post(
            "/api/login",
            json={"email": "user2@example.com", "senha": "Senha@123"},
            headers={"X-CSRF-Token": token},
        )
        corpo = client.get("/api/me").json()
        assert corpo["email"] == "user2@example.com"


class TestPasswordSecurity:
    """Segurança de senhas"""

    def test_senha_nao_retornada_em_respostas(self, client, criar_usuario, usuario_teste):
        """A senha não deve aparecer em nenhuma resposta JSON"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"],
        )

        token = _csrf(client)
        client.post(
            "/api/login",
            json={"email": usuario_teste["email"], "senha": usuario_teste["senha"]},
            headers={"X-CSRF-Token": token},
        )

        for endpoint in ["/api/me", "/api/usuario/perfil"]:
            texto = client.get(endpoint).text
            assert usuario_teste["senha"] not in texto
            assert "senha" not in client.get(endpoint).json()

    def test_senha_armazenada_como_hash(self, client, criar_usuario, usuario_teste):
        """A senha deve ser persistida como hash bcrypt"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"],
        )

        from repo import usuario_repo

        usuario = usuario_repo.obter_por_email(usuario_teste["email"])
        assert usuario is not None
        assert usuario.senha.startswith("$2b$")
        assert len(usuario.senha) == 60
        assert usuario_teste["senha"] not in usuario.senha

    def test_senha_fraca_rejeitada_no_cadastro(self, client):
        """Senhas fracas devem ser rejeitadas na validação (422)"""
        senhas_fracas = ["123456", "abcdefgh", "ABCDEFGH", "Abc123", "Senha123"]

        for i, senha in enumerate(senhas_fracas):
            token = _csrf(client)
            response = client.post(
                "/api/cadastrar",
                json={
                    "perfil": Perfil.CLIENTE.value,
                    "nome": "Usuario Teste",
                    "email": f"fraca{i}@example.com",
                    "senha": senha,
                    "confirmar_senha": senha,
                },
                headers={"X-CSRF-Token": token},
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, senha


class TestInformationDisclosure:
    """Prevenção de vazamento de informações"""

    def test_login_email_inexistente_mensagem_generica(self, client):
        """Login com e-mail inexistente não deve revelar a inexistência"""
        token = _csrf(client)
        response = client.post(
            "/api/login",
            json={"email": "naoexiste@example.com", "senha": "Senha@123"},
            headers={"X-CSRF-Token": token},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        detail = response.json()["detail"].lower()
        assert "e-mail ou senha" in detail
        assert "não cadastrado" not in detail

    def test_esqueci_senha_nao_revela_email(self, client):
        """Esqueci-senha deve responder igual para e-mail inexistente"""
        token = _csrf(client)
        response = client.post(
            "/api/esqueci-senha",
            json={"email": "naoexiste@example.com"},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
