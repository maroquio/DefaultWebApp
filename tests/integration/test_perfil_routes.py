"""
Testes de gerenciamento de perfil do usuário
Testa visualização, edição de dados, alteração de senha e upload de foto
"""
from fastapi import status
from tests.test_helpers import assert_redirects_to, assert_permission_denied, assert_contains_text


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
        # Verificar que contém pelo menos uma das palavras-chave
        assert "editar" in response.text.lower() or "perfil" in response.text.lower()

    def test_editar_perfil_com_dados_validos(self, cliente_autenticado, usuario_teste):
        """Deve permitir editar perfil com dados válidos"""
        response = cliente_autenticado.post("/usuario/perfil/editar", data={
            "nome": "Nome Atualizado",
            "email": usuario_teste["email"]  # Mantém o mesmo email
        }, follow_redirects=False)

        # Deve redirecionar para visualizar
        assert_redirects_to(response, "/usuario/perfil/visualizar")

        # Verificar que dados foram atualizados
        response_visualizar = cliente_autenticado.get("/usuario/perfil/visualizar")
        assert "Nome Atualizado" in response_visualizar.text

    def test_editar_perfil_com_email_duplicado(self, client, criar_usuario, usuario_teste):
        """Deve rejeitar edição com email já usado por outro usuário"""
        # Criar dois usuários
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
            "email": usuario_teste["email"]  # Email já usado
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
        # Deve ter mensagem de erro
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
        # Editar perfil
        cliente_autenticado.post("/usuario/perfil/editar", data={
            "nome": "Nome Atualizado",
            "email": "novoemail@example.com"
        })

        # Acessar dashboard e verificar que sessão foi atualizada
        response = cliente_autenticado.get("/usuario")
        assert "Nome Atualizado" in response.text


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

        # Deve redirecionar para visualizar
        assert_redirects_to(response, "/usuario/perfil/visualizar")

        # Fazer logout e tentar login com nova senha
        cliente_autenticado.get("/logout")
        response_login = cliente_autenticado.post("/login", data={
            "email": usuario_teste["email"],
            "senha": "NovaSenha@123"
        }, follow_redirects=False)

        # Deve fazer login com sucesso
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
            "senha_nova": usuario_teste["senha"],  # Mesma senha
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
            "senha_nova": "123456",  # Senha fraca
            "confirmar_senha": "123456"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        # Deve ter mensagem sobre requisitos de senha
        assert any(palavra in response.text.lower() for palavra in ["mínimo", "maiúscula", "senha"])


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

        # Deve redirecionar para visualizar
        assert_redirects_to(response, "/usuario/perfil/visualizar")

    def test_atualizar_foto_com_dados_invalidos(self, cliente_autenticado):
        """Deve rejeitar dados inválidos"""
        response = cliente_autenticado.post("/usuario/perfil/atualizar-foto", data={
            "foto_base64": "dados-invalidos"
        }, follow_redirects=False)

        # Deve redirecionar para visualizar (com mensagem de erro)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_atualizar_foto_muito_grande(self, cliente_autenticado):
        """Deve rejeitar foto muito grande (>10MB)"""
        # Criar string muito grande (simulando foto >10MB)
        foto_grande = "data:image/png;base64," + ("A" * 15 * 1024 * 1024)  # 15MB

        response = cliente_autenticado.post("/usuario/perfil/atualizar-foto", data={
            "foto_base64": foto_grande
        }, follow_redirects=False)

        # Deve redirecionar para visualizar (com mensagem de erro)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_atualizar_foto_vazia(self, cliente_autenticado):
        """Deve rejeitar foto vazia"""
        response = cliente_autenticado.post("/usuario/perfil/atualizar-foto", data={
            "foto_base64": ""
        }, follow_redirects=False)

        # Deve redirecionar para visualizar (com mensagem de erro)
        assert response.status_code == status.HTTP_303_SEE_OTHER
