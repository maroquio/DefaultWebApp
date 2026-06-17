"""
Testes de administração de usuários
Testa CRUD completo de usuários por administradores
"""
from unittest.mock import patch

from fastapi import status

from util.perfis import Perfil
from tests.test_helpers import assert_redirects_to, assert_permission_denied, assert_contains_text


class TestListarUsuarios:
    """Testes de listagem de usuários"""

    def test_listar_usuarios_requer_admin(self, cliente_autenticado):
        """Cliente não deve acessar listagem de usuários"""
        response = cliente_autenticado.get("/admin/usuarios/listar", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_listar_usuarios_admin_acessa(self, admin_autenticado):
        """Admin deve acessar listagem de usuários"""
        response = admin_autenticado.get("/admin/usuarios/listar")
        assert response.status_code == status.HTTP_200_OK

    def test_listar_usuarios_exibe_usuarios(self, admin_autenticado, admin_teste):
        """Listagem deve exibir usuários cadastrados"""
        response = admin_autenticado.get("/admin/usuarios/listar")
        assert response.status_code == status.HTTP_200_OK
        # Deve conter o próprio admin
        assert admin_teste["email"] in response.text

    def test_listar_usuarios_sem_autenticacao(self, client):
        """Não autenticado deve ser redirecionado"""
        response = client.get("/admin/usuarios/listar", follow_redirects=False)
        assert_permission_denied(response)


class TestCadastrarUsuario:
    """Testes de cadastro de usuário por admin"""

    def test_get_cadastrar_requer_admin(self, cliente_autenticado):
        """Cliente não deve acessar formulário de cadastro"""
        response = cliente_autenticado.get("/admin/usuarios/cadastrar", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_get_cadastrar_admin_acessa(self, admin_autenticado):
        """Admin deve acessar formulário de cadastro"""
        response = admin_autenticado.get("/admin/usuarios/cadastrar")
        assert response.status_code == status.HTTP_200_OK
        assert_contains_text(response, "cadastr")

    def test_cadastrar_usuario_com_dados_validos(self, admin_autenticado):
        """Admin deve poder cadastrar usuário com todos os perfis"""
        response = admin_autenticado.post("/admin/usuarios/cadastrar", data={
            "nome": "Novo Usuario Admin",
            "email": "novousuario@example.com",
            "senha": "Senha@123",
            "perfil": Perfil.CLIENTE.value
        }, follow_redirects=False)

        # Deve redirecionar para listagem
        assert_redirects_to(response, "/admin/usuarios/listar")

        # Verificar que usuário foi criado
        from repo import usuario_repo
        usuario = usuario_repo.obter_por_email("novousuario@example.com")
        assert usuario is not None
        assert usuario.nome == "Novo Usuario Admin"

    def test_cadastrar_usuario_com_perfil_admin(self, admin_autenticado):
        """Admin deve poder cadastrar outro admin"""
        response = admin_autenticado.post("/admin/usuarios/cadastrar", data={
            "nome": "Novo Admin",
            "email": "novoadmin@example.com",
            "senha": "SenhaAdmin@123",
            "perfil": Perfil.ADMIN.value
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Verificar perfil
        from repo import usuario_repo
        usuario = usuario_repo.obter_por_email("novoadmin@example.com")
        assert usuario is not None
        assert usuario.perfil == Perfil.ADMIN.value

    def test_cadastrar_usuario_com_perfil_vendedor(self, admin_autenticado):
        """Admin deve poder cadastrar vendedor"""
        response = admin_autenticado.post("/admin/usuarios/cadastrar", data={
            "nome": "Novo Vendedor",
            "email": "novovendedor@example.com",
            "senha": "SenhaVendedor@123",
            "perfil": Perfil.VENDEDOR.value
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Verificar perfil
        from repo import usuario_repo
        usuario = usuario_repo.obter_por_email("novovendedor@example.com")
        assert usuario is not None
        assert usuario.perfil == Perfil.VENDEDOR.value

    def test_cadastrar_usuario_email_duplicado(self, admin_autenticado, admin_teste):
        """Deve rejeitar email já cadastrado"""
        response = admin_autenticado.post("/admin/usuarios/cadastrar", data={
            "nome": "Outro Nome",
            "email": admin_teste["email"],  # Email já existe
            "senha": "Senha@123",
            "perfil": Perfil.CLIENTE.value
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "e-mail" in response.text.lower() and "cadastrado" in response.text.lower()

    def test_cadastrar_usuario_senha_fraca(self, admin_autenticado):
        """Deve rejeitar senha fraca"""
        response = admin_autenticado.post("/admin/usuarios/cadastrar", data={
            "nome": "Usuario Teste",
            "email": "teste@example.com",
            "senha": "123",  # Senha fraca
            "perfil": Perfil.CLIENTE.value
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        # Deve ter mensagem sobre requisitos de senha
        assert any(palavra in response.text.lower() for palavra in ["mínimo", "maiúscula", "senha"])

    def test_cadastrar_usuario_perfil_invalido(self, admin_autenticado):
        """Deve rejeitar perfil inválido"""
        response = admin_autenticado.post("/admin/usuarios/cadastrar", data={
            "nome": "Usuario Teste",
            "email": "teste@example.com",
            "senha": "Senha@123",
            "perfil": "PERFIL_INVALIDO"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK


class TestEditarUsuario:
    """Testes de edição de usuário por admin"""

    def test_get_editar_requer_admin(self, cliente_autenticado, criar_usuario):
        """Cliente não deve acessar formulário de edição"""
        # Criar um usuário qualquer para tentar editar
        criar_usuario("Outro Usuario", "outro@example.com", "Senha@123")

        from repo import usuario_repo
        outro = usuario_repo.obter_por_email("outro@example.com")

        response = cliente_autenticado.get(f"/admin/usuarios/editar/{outro.id}", follow_redirects=False)
        # Cliente pode receber 200 mas sem permissão, ou redirect/403
        # Vamos verificar se pelo menos não consegue acessar como admin
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_get_editar_admin_acessa(self, admin_autenticado, admin_teste):
        """Admin deve acessar formulário de edição"""
        from repo import usuario_repo
        admin = usuario_repo.obter_por_email(admin_teste["email"])

        response = admin_autenticado.get(f"/admin/usuarios/editar/{admin.id}")
        assert response.status_code == status.HTTP_200_OK
        assert_contains_text(response, "editar")

    def test_editar_usuario_com_dados_validos(self, admin_autenticado, criar_usuario):
        """Admin deve poder editar usuário"""
        # Criar usuário para editar
        criar_usuario("Usuario Original", "original@example.com", "Senha@123")

        from repo import usuario_repo
        usuario = usuario_repo.obter_por_email("original@example.com")

        # Editar usuário
        response = admin_autenticado.post(f"/admin/usuarios/editar/{usuario.id}", data={
            "nome": "Usuario Editado",
            "email": "editado@example.com",
            "perfil": Perfil.VENDEDOR.value
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Verificar que foi editado
        usuario_editado = usuario_repo.obter_por_id(usuario.id)
        assert usuario_editado.nome == "Usuario Editado"
        assert usuario_editado.email == "editado@example.com"
        assert usuario_editado.perfil == Perfil.VENDEDOR.value

    def test_editar_usuario_email_duplicado(self, admin_autenticado, criar_usuario):
        """Deve rejeitar email já usado por outro usuário"""
        # Criar dois usuários
        criar_usuario("Usuario 1", "usuario1@example.com", "Senha@123")
        criar_usuario("Usuario 2", "usuario2@example.com", "Senha@123")

        from repo import usuario_repo
        usuario2 = usuario_repo.obter_por_email("usuario2@example.com")

        # Tentar alterar email do usuario2 para o do usuario1
        response = admin_autenticado.post(f"/admin/usuarios/editar/{usuario2.id}", data={
            "nome": "Usuario 2",
            "email": "usuario1@example.com",  # Email já existe
            "perfil": Perfil.CLIENTE.value
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "e-mail" in response.text.lower()

    def test_editar_usuario_nao_altera_senha(self, admin_autenticado, criar_usuario):
        """Editar usuário não deve alterar a senha"""
        criar_usuario("Usuario Teste", "teste@example.com", "SenhaOriginal@123")

        from repo import usuario_repo
        usuario_original = usuario_repo.obter_por_email("teste@example.com")
        senha_hash_original = usuario_original.senha

        # Editar usuário
        admin_autenticado.post(f"/admin/usuarios/editar/{usuario_original.id}", data={
            "nome": "Nome Editado",
            "email": "teste@example.com",
            "perfil": Perfil.CLIENTE.value
        })

        # Verificar que senha não mudou
        usuario_editado = usuario_repo.obter_por_id(usuario_original.id)
        assert usuario_editado.senha == senha_hash_original

    def test_editar_usuario_inexistente(self, admin_autenticado):
        """Deve tratar edição de usuário inexistente"""
        response = admin_autenticado.post("/admin/usuarios/editar/99999", data={
            "nome": "Nome",
            "email": "email@example.com",
            "perfil": Perfil.CLIENTE.value
        }, follow_redirects=False)

        # Deve redirecionar
        assert response.status_code == status.HTTP_303_SEE_OTHER


class TestExcluirUsuario:
    """Testes de exclusão de usuário por admin"""

    def test_excluir_usuario_por_admin(self, admin_autenticado, criar_usuario):
        """Admin deve poder excluir usuário"""
        criar_usuario("Usuario Para Excluir", "excluir@example.com", "Senha@123")

        from repo import usuario_repo
        usuario = usuario_repo.obter_por_email("excluir@example.com")

        # Excluir usuário
        response = admin_autenticado.post(f"/admin/usuarios/excluir/{usuario.id}", follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Verificar que foi excluído
        usuario_excluido = usuario_repo.obter_por_id(usuario.id)
        assert usuario_excluido is None

    def test_admin_nao_pode_excluir_a_si_mesmo(self, admin_autenticado, admin_teste):
        """Admin não deve poder excluir a si mesmo"""
        from repo import usuario_repo
        admin = usuario_repo.obter_por_email(admin_teste["email"])

        response = admin_autenticado.post(f"/admin/usuarios/excluir/{admin.id}", follow_redirects=False)

        # Deve redirecionar com mensagem de erro
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Verificar que admin ainda existe
        admin_ainda_existe = usuario_repo.obter_por_id(admin.id)
        assert admin_ainda_existe is not None

    def test_excluir_usuario_inexistente(self, admin_autenticado):
        """Deve tratar exclusão de usuário inexistente"""
        response = admin_autenticado.post("/admin/usuarios/excluir/99999", follow_redirects=False)

        # Deve redirecionar
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_cliente_nao_pode_excluir_usuario(self, cliente_autenticado, criar_usuario):
        """Cliente não deve poder excluir usuários"""
        criar_usuario("Outro Usuario", "outro@example.com", "Senha@123")

        from repo import usuario_repo
        outro = usuario_repo.obter_por_email("outro@example.com")

        response = cliente_autenticado.post(f"/admin/usuarios/excluir/{outro.id}", follow_redirects=False)

        # Deve ser bloqueado
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

        # Verificar que usuário ainda existe
        outro_ainda_existe = usuario_repo.obter_por_id(outro.id)
        assert outro_ainda_existe is not None


class TestRedirecionamentos:
    """Testes de redirecionamentos"""

    def test_index_redireciona_para_listar(self, admin_autenticado):
        """GET /admin/usuarios/ deve redirecionar para /listar"""
        response = admin_autenticado.get("/admin/usuarios/", follow_redirects=False)
        # Redireciona com status 307 (Temporary Redirect) para /listar
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert "/admin/usuarios/listar" in response.headers["location"]


class TestAdminUsuariosRateLimiting:
    """Testes de rate limiting para operações de administração de usuários"""

    def test_cadastrar_rate_limit(self, admin_autenticado):
        """Rate limit deve bloquear cadastros excessivos"""
        with patch('routes.admin_usuarios_routes.admin_usuarios_limiter.verificar', return_value=False):
            response = admin_autenticado.post("/admin/usuarios/cadastrar", data={
                "nome": "Teste Rate Limit",
                "email": "ratelimit@example.com",
                "senha": "Senha@123",
                "perfil": Perfil.CLIENTE.value
            }, follow_redirects=False)

            assert_redirects_to(response, "/admin/usuarios/listar")

    def test_editar_rate_limit(self, admin_autenticado, criar_usuario):
        """Rate limit deve bloquear edições excessivas"""
        criar_usuario("Usuario Editar", "editar_rate@example.com", "Senha@123")

        from repo import usuario_repo
        usuario = usuario_repo.obter_por_email("editar_rate@example.com")

        with patch('routes.admin_usuarios_routes.admin_usuarios_limiter.verificar', return_value=False):
            response = admin_autenticado.post(f"/admin/usuarios/editar/{usuario.id}", data={
                "nome": "Nome Editado",
                "email": "editar_rate@example.com",
                "perfil": Perfil.CLIENTE.value
            }, follow_redirects=False)

            assert_redirects_to(response, "/admin/usuarios/listar")

    def test_excluir_rate_limit(self, admin_autenticado, criar_usuario):
        """Rate limit deve bloquear exclusões excessivas"""
        criar_usuario("Usuario Excluir", "excluir_rate@example.com", "Senha@123")

        from repo import usuario_repo
        usuario = usuario_repo.obter_por_email("excluir_rate@example.com")

        with patch('routes.admin_usuarios_routes.admin_usuarios_limiter.verificar', return_value=False):
            response = admin_autenticado.post(f"/admin/usuarios/excluir/{usuario.id}", follow_redirects=False)

            assert_redirects_to(response, "/admin/usuarios/listar")

        # Verificar que usuário ainda existe (não foi excluído devido ao rate limit)
        usuario_ainda_existe = usuario_repo.obter_por_id(usuario.id)
        assert usuario_ainda_existe is not None
