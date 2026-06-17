"""
Testes de integração para rotas de usuário (/usuario)
Testa dashboard, perfil, edição, alteração de senha e upload de foto
"""
from fastapi import status
from unittest.mock import patch
from tests.test_helpers import assert_redirects_to, assert_permission_denied, assert_contains_text


class TestDashboard:
    """Testes do dashboard do usuário"""

    def test_dashboard_requer_autenticacao(self, client):
        """Usuário não autenticado não pode acessar dashboard"""
        response = client.get("/usuario", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_dashboard_usuario_cliente(self, cliente_autenticado):
        """Cliente autenticado pode acessar dashboard"""
        response = cliente_autenticado.get("/usuario")
        assert response.status_code == status.HTTP_200_OK

    def test_dashboard_exibe_dados_usuario(self, cliente_autenticado, usuario_teste):
        """Dashboard deve exibir informações do usuário logado"""
        response = cliente_autenticado.get("/usuario")
        assert response.status_code == status.HTTP_200_OK
        assert usuario_teste["nome"] in response.text

    def test_dashboard_admin(self, admin_autenticado, admin_teste):
        """Admin autenticado pode acessar dashboard"""
        response = admin_autenticado.get("/usuario")
        assert response.status_code == status.HTTP_200_OK
        assert admin_teste["nome"] in response.text

    def test_dashboard_vendedor(self, vendedor_autenticado, vendedor_teste):
        """Vendedor autenticado pode acessar dashboard"""
        response = vendedor_autenticado.get("/usuario")
        assert response.status_code == status.HTTP_200_OK
        assert vendedor_teste["nome"] in response.text


class TestVisualizarPerfil:
    """Testes de visualização de perfil"""

    def test_visualizar_perfil_requer_autenticacao(self, client):
        """Deve exigir autenticação para visualizar perfil"""
        response = client.get("/usuario/perfil/visualizar", follow_redirects=False)
        assert_permission_denied(response)

    def test_visualizar_perfil_usuario_autenticado(self, cliente_autenticado, usuario_teste):
        """Usuário autenticado deve ver seu perfil"""
        response = cliente_autenticado.get("/usuario/perfil/visualizar")
        assert response.status_code == status.HTTP_200_OK
        assert usuario_teste["nome"] in response.text
        assert usuario_teste["email"] in response.text

    def test_visualizar_perfil_usuario_nao_encontrado(self, cliente_autenticado):
        """Redireciona para logout se usuário não for encontrado no banco"""
        with patch('routes.usuario_routes.usuario_repo') as mock_repo:
            mock_repo.obter_por_id.return_value = None

            response = cliente_autenticado.get(
                "/usuario/perfil/visualizar",
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER


class TestEditarPerfil:
    """Testes de edição de perfil"""

    def test_get_formulario_edicao_requer_autenticacao(self, client):
        """Deve exigir autenticação para acessar formulário de edição"""
        response = client.get("/usuario/perfil/editar", follow_redirects=False)
        assert_permission_denied(response)

    def test_get_formulario_edicao_usuario_autenticado(self, cliente_autenticado):
        """Usuário autenticado deve acessar formulário de edição"""
        response = cliente_autenticado.get("/usuario/perfil/editar")
        assert response.status_code == status.HTTP_200_OK
        assert "editar" in response.text.lower() or "perfil" in response.text.lower()

    def test_editar_perfil_com_dados_validos(self, cliente_autenticado, usuario_teste):
        """Deve permitir editar perfil com dados válidos"""
        response = cliente_autenticado.post("/usuario/perfil/editar", data={
            "nome": "Nome Atualizado",
            "email": usuario_teste["email"]
        }, follow_redirects=False)

        assert_redirects_to(response, "/usuario/perfil/visualizar")

        # Verificar que dados foram atualizados
        response_visualizar = cliente_autenticado.get("/usuario/perfil/visualizar")
        assert "Nome Atualizado" in response_visualizar.text

    def test_editar_perfil_com_email_duplicado(self, client, criar_usuario, usuario_teste):
        """Deve rejeitar edição com email já usado por outro usuário"""
        criar_usuario(usuario_teste["nome"], usuario_teste["email"], usuario_teste["senha"])
        criar_usuario("Outro Usuario", "outro@example.com", "Senha@123")

        # Login como segundo usuário
        client.post("/login", data={
            "email": "outro@example.com",
            "senha": "Senha@123"
        })

        # Tentar alterar email para o do primeiro usuário
        response = client.post("/usuario/perfil/editar", data={
            "nome": "Outro Usuario",
            "email": usuario_teste["email"]
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "e-mail" in response.text.lower()

    def test_editar_perfil_com_nome_vazio(self, cliente_autenticado, usuario_teste):
        """Deve rejeitar nome vazio"""
        response = cliente_autenticado.post("/usuario/perfil/editar", data={
            "nome": "",
            "email": usuario_teste["email"]
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "erro" in response.text.lower() or "obrigatório" in response.text.lower()

    def test_editar_perfil_com_email_invalido(self, cliente_autenticado):
        """Deve rejeitar email inválido"""
        response = cliente_autenticado.post("/usuario/perfil/editar", data={
            "nome": "Nome Válido",
            "email": "email-invalido"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "e-mail" in response.text.lower() or "válido" in response.text.lower()

    def test_editar_perfil_atualiza_sessao(self, cliente_autenticado, usuario_teste):
        """Editar perfil deve atualizar dados na sessão"""
        cliente_autenticado.post("/usuario/perfil/editar", data={
            "nome": "Nome Atualizado",
            "email": "novoemail@example.com"
        })

        response = cliente_autenticado.get("/usuario")
        assert "Nome Atualizado" in response.text

    def test_get_editar_perfil_rate_limit(self, cliente_autenticado):
        """Rate limit deve bloquear acesso ao formulário"""
        with patch('routes.usuario_routes.form_get_limiter.verificar', return_value=False):
            response = cliente_autenticado.get(
                "/usuario/perfil/editar",
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER
            assert response.headers["location"] == "/usuario"


class TestAlterarSenha:
    """Testes de alteração de senha"""

    def test_get_formulario_alterar_senha_requer_autenticacao(self, client):
        """Deve exigir autenticação para acessar formulário"""
        response = client.get("/usuario/perfil/alterar-senha", follow_redirects=False)
        assert_permission_denied(response)

    def test_get_formulario_alterar_senha_usuario_autenticado(self, cliente_autenticado):
        """Usuário autenticado deve acessar formulário de alteração de senha"""
        response = cliente_autenticado.get("/usuario/perfil/alterar-senha")
        assert response.status_code == status.HTTP_200_OK
        assert_contains_text(response, "senha")

    def test_alterar_senha_com_dados_validos(self, cliente_autenticado, usuario_teste):
        """Deve permitir alterar senha com dados válidos"""
        response = cliente_autenticado.post("/usuario/perfil/alterar-senha", data={
            "senha_atual": usuario_teste["senha"],
            "senha_nova": "NovaSenha@123",
            "confirmar_senha": "NovaSenha@123"
        }, follow_redirects=False)

        assert_redirects_to(response, "/usuario/perfil/visualizar")

        # Fazer logout e tentar login com nova senha
        cliente_autenticado.get("/logout")
        response_login = cliente_autenticado.post("/login", data={
            "email": usuario_teste["email"],
            "senha": "NovaSenha@123"
        }, follow_redirects=False)

        assert response_login.status_code == status.HTTP_303_SEE_OTHER

    def test_alterar_senha_com_senha_atual_incorreta(self, cliente_autenticado):
        """Deve rejeitar se senha atual estiver incorreta"""
        response = cliente_autenticado.post("/usuario/perfil/alterar-senha", data={
            "senha_atual": "SenhaErrada@123",
            "senha_nova": "NovaSenha@123",
            "confirmar_senha": "NovaSenha@123"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "incorreta" in response.text.lower()

    def test_alterar_senha_nova_igual_atual(self, cliente_autenticado, usuario_teste):
        """Deve rejeitar se nova senha for igual à atual"""
        response = cliente_autenticado.post("/usuario/perfil/alterar-senha", data={
            "senha_atual": usuario_teste["senha"],
            "senha_nova": usuario_teste["senha"],
            "confirmar_senha": usuario_teste["senha"]
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "diferente" in response.text.lower()

    def test_alterar_senha_senhas_nao_coincidem(self, cliente_autenticado, usuario_teste):
        """Deve rejeitar se senhas não coincidem"""
        response = cliente_autenticado.post("/usuario/perfil/alterar-senha", data={
            "senha_atual": usuario_teste["senha"],
            "senha_nova": "NovaSenha@123",
            "confirmar_senha": "SenhaDiferente@123"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "coincidem" in response.text.lower()

    def test_alterar_senha_nova_fraca(self, cliente_autenticado, usuario_teste):
        """Deve rejeitar senha fraca"""
        response = cliente_autenticado.post("/usuario/perfil/alterar-senha", data={
            "senha_atual": usuario_teste["senha"],
            "senha_nova": "123456",
            "confirmar_senha": "123456"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert any(palavra in response.text.lower() for palavra in ["mínimo", "maiúscula", "senha"])

    def test_get_alterar_senha_rate_limit(self, cliente_autenticado):
        """Rate limit deve bloquear acesso ao formulário"""
        with patch('routes.usuario_routes.form_get_limiter.verificar', return_value=False):
            response = cliente_autenticado.get(
                "/usuario/perfil/alterar-senha",
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER
            assert response.headers["location"] == "/usuario"

    def test_post_alterar_senha_rate_limit(self, cliente_autenticado):
        """Rate limit deve bloquear alteração de senha"""
        with patch('routes.usuario_routes.alterar_senha_limiter.verificar', return_value=False):
            response = cliente_autenticado.post(
                "/usuario/perfil/alterar-senha",
                data={
                    "senha_atual": "SenhaAtual@123",
                    "senha_nova": "NovaSenha@123",
                    "confirmar_senha": "NovaSenha@123"
                }
            )

            assert response.status_code == status.HTTP_200_OK
            assert "muitas tentativas" in response.text.lower() or "aguarde" in response.text.lower()


class TestAtualizarFoto:
    """Testes de upload de foto de perfil"""

    def test_atualizar_foto_requer_autenticacao(self, client, foto_teste_base64):
        """Deve exigir autenticação para atualizar foto"""
        response = client.post("/usuario/perfil/atualizar-foto", data={
            "foto_base64": foto_teste_base64
        }, follow_redirects=False)
        assert_permission_denied(response)

    def test_atualizar_foto_com_dados_validos(self, cliente_autenticado, foto_teste_base64):
        """Deve permitir atualizar foto com dados válidos"""
        response = cliente_autenticado.post("/usuario/perfil/atualizar-foto", data={
            "foto_base64": foto_teste_base64
        }, follow_redirects=False)

        assert_redirects_to(response, "/usuario/perfil/visualizar")

    def test_atualizar_foto_com_dados_invalidos(self, cliente_autenticado):
        """Deve rejeitar dados inválidos"""
        response = cliente_autenticado.post("/usuario/perfil/atualizar-foto", data={
            "foto_base64": "dados-invalidos"
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_atualizar_foto_muito_grande(self, cliente_autenticado):
        """Deve rejeitar foto muito grande (>10MB)"""
        foto_grande = "data:image/png;base64," + ("A" * 15 * 1024 * 1024)

        response = cliente_autenticado.post("/usuario/perfil/atualizar-foto", data={
            "foto_base64": foto_grande
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_atualizar_foto_vazia(self, cliente_autenticado):
        """Deve rejeitar foto vazia"""
        response = cliente_autenticado.post("/usuario/perfil/atualizar-foto", data={
            "foto_base64": ""
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_atualizar_foto_rate_limit(self, cliente_autenticado):
        """Rate limit deve bloquear upload de foto"""
        with patch('routes.usuario_routes.upload_foto_limiter.verificar', return_value=False):
            response = cliente_autenticado.post(
                "/usuario/perfil/atualizar-foto",
                data={"foto_base64": "data:image/png;base64," + "A" * 100},
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_atualizar_foto_erro_io(self, cliente_autenticado):
        """Deve tratar erro de I/O ao salvar foto"""
        with patch('routes.usuario_routes.salvar_foto_cropada_usuario', side_effect=IOError("Disk full")):
            response = cliente_autenticado.post(
                "/usuario/perfil/atualizar-foto",
                data={"foto_base64": "data:image/png;base64," + "A" * 200},
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_atualizar_foto_erro_os(self, cliente_autenticado):
        """Deve tratar OSError ao salvar foto"""
        with patch('routes.usuario_routes.salvar_foto_cropada_usuario', side_effect=OSError("Permission denied")):
            response = cliente_autenticado.post(
                "/usuario/perfil/atualizar-foto",
                data={"foto_base64": "data:image/png;base64," + "A" * 200},
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER
