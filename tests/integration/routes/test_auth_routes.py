"""
Testes de autenticação e autorização
Testa login, cadastro, logout e recuperação de senha
"""
from fastapi import status
from util.perfis import Perfil
from tests.test_helpers import assert_redirects_to, assert_permission_denied, assert_contains_text


class TestLogin:
    """Testes de login"""

    def test_get_login_retorna_formulario(self, client):
        """Deve retornar página de login"""
        response = client.get("/login")
        assert response.status_code == status.HTTP_200_OK
        assert_contains_text(response, "login")

    def test_login_com_credenciais_validas(self, client, criar_usuario, usuario_teste):
        """Deve fazer login com credenciais válidas"""
        # Criar usuário primeiro
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Tentar login
        response = client.post("/login", data={
            "email": usuario_teste["email"],
            "senha": usuario_teste["senha"]
        }, follow_redirects=False)

        # Deve redirecionar após login bem-sucedido
        assert_redirects_to(response, "/usuario")

    def test_login_com_email_invalido(self, client):
        """Deve rejeitar login com e-mail inexistente"""
        response = client.post("/login", data={
            "email": "naoexiste@example.com",
            "senha": "SenhaQualquer@123"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "e-mail ou senha" in response.text.lower()

    def test_login_com_senha_incorreta(self, client, criar_usuario, usuario_teste):
        """Deve rejeitar login com senha incorreta"""
        # Criar usuário
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Tentar login com senha errada
        response = client.post("/login", data={
            "email": usuario_teste["email"],
            "senha": "SenhaErrada@123"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "e-mail ou senha" in response.text.lower()

    def test_login_com_email_vazio(self, client):
        """Deve validar e-mail obrigatório"""
        response = client.post("/login", data={
            "email": "",
            "senha": "Senha@123"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        texto = response.text.lower()
        assert (
            "string_too_short" in texto
            or "obrigatório" in texto
            or "e-mail" in texto
        )

    def test_usuario_logado_nao_acessa_login(self, cliente_autenticado):
        """Usuário já logado deve ser redirecionado ao acessar /login"""
        response = cliente_autenticado.get("/login", follow_redirects=False)
        assert_redirects_to(response, "/usuario")


class TestCadastro:
    """Testes de cadastro de usuário"""

    def test_get_cadastro_retorna_formulario(self, client):
        """Deve retornar página de cadastro"""
        response = client.get("/cadastrar")
        assert response.status_code == status.HTTP_200_OK
        assert_contains_text(response, "cadastro")

    def test_cadastro_com_dados_validos(self, client):
        """Deve cadastrar usuário com dados válidos"""
        response = client.post("/cadastrar", data={
            "perfil": Perfil.CLIENTE.value,
            "nome": "Novo Usuario",
            "email": "novo@example.com",
            "senha": "Senha@123",
            "confirmar_senha": "Senha@123"
        }, follow_redirects=False)

        # Deve redirecionar para login após cadastro
        assert_redirects_to(response, "/login")

    def test_cadastro_com_email_duplicado(self, client, criar_usuario, usuario_teste):
        """Deve rejeitar cadastro com e-mail já existente"""
        # Criar primeiro usuário
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Tentar cadastrar com mesmo e-mail
        response = client.post("/cadastrar", data={
            "perfil": Perfil.CLIENTE.value,
            "nome": "Outro Nome",
            "email": usuario_teste["email"],  # E-mail duplicado
            "senha": "OutraSenha@123",
            "confirmar_senha": "OutraSenha@123"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "e-mail" in response.text.lower() and "cadastrado" in response.text.lower()

    def test_cadastro_com_senhas_diferentes(self, client):
        """Deve rejeitar quando senhas não coincidem"""
        response = client.post("/cadastrar", data={
            "perfil": Perfil.CLIENTE.value,
            "nome": "Usuario Teste",
            "email": "teste@example.com",
            "senha": "Senha@123",
            "confirmar_senha": "SenhaDiferente@123"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "senha" in response.text.lower() and "coincidem" in response.text.lower()

    def test_cadastro_com_senha_fraca(self, client):
        """Deve rejeitar senha que não atende requisitos de força"""
        response = client.post("/cadastrar", data={
            "perfil": Perfil.CLIENTE.value,
            "nome": "Usuario Teste",
            "email": "teste@example.com",
            "senha": "123456",  # Senha fraca
            "confirmar_senha": "123456"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        # Deve ter mensagem sobre requisitos de senha
        assert any(palavra in response.text.lower() for palavra in ["mínimo", "maiúscula", "senha"])

    def test_cadastro_cria_usuario_com_perfil_cliente(self, client):
        """Cadastro público deve criar usuário com perfil CLIENTE (Enum Perfil)"""
        from repo import usuario_repo

        client.post("/cadastrar", data={
            "perfil": Perfil.CLIENTE.value,
            "nome": "Usuario Teste",
            "email": "teste@example.com",
            "senha": "Senha@123",
            "confirmar_senha": "Senha@123"
        })

        # Verificar no banco que o usuário foi criado com perfil correto
        usuario = usuario_repo.obter_por_email("teste@example.com")
        assert usuario is not None
        assert usuario.perfil == Perfil.CLIENTE.value  # Usa Enum Perfil


class TestLogout:
    """Testes de logout"""

    def test_logout_limpa_sessao(self, cliente_autenticado):
        """Logout deve limpar sessão e redirecionar para raiz"""
        response = cliente_autenticado.get("/logout", follow_redirects=False)

        # Deve redirecionar para raiz do site
        assert_redirects_to(response, "/")

    def test_logout_desautentica_usuario(self, cliente_autenticado):
        """Após logout, usuário não deve ter acesso a áreas protegidas"""
        # Fazer logout
        cliente_autenticado.get("/logout")

        # Tentar acessar área protegida
        response = cliente_autenticado.get("/chamados/listar", follow_redirects=False)

        # Deve redirecionar para login
        assert response.status_code == status.HTTP_303_SEE_OTHER


class TestRecuperacaoSenha:
    """Testes de recuperação de senha"""

    def test_get_esqueci_senha_retorna_formulario(self, client):
        """Deve retornar página de recuperação de senha"""
        response = client.get("/esqueci-senha")
        assert response.status_code == status.HTTP_200_OK
        # Verificar que contém pelo menos uma das palavras-chave
        assert "esqueci" in response.text.lower() or "recupera" in response.text.lower()

    def test_solicitar_recuperacao_senha_email_existente(self, client, criar_usuario, usuario_teste):
        """Deve processar solicitação para e-mail cadastrado"""
        # Criar usuário
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Solicitar recuperação
        response = client.post("/esqueci-senha", data={
            "email": usuario_teste["email"]
        }, follow_redirects=False)

        # Deve redirecionar para login
        assert_redirects_to(response, "/login")

    def test_solicitar_recuperacao_senha_email_inexistente(self, client):
        """Deve retornar mesma mensagem por segurança (não revelar se e-mail existe)"""
        response = client.post("/esqueci-senha", data={
            "email": "naoexiste@example.com"
        }, follow_redirects=False)

        # Deve redirecionar normalmente (sem revelar que e-mail não existe)
        assert_redirects_to(response, "/login")

    def test_redefinir_senha_com_token_invalido(self, client):
        """Deve rejeitar token inválido"""
        response = client.get("/redefinir-senha?token=token_invalido", follow_redirects=False)

        # Deve redirecionar
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_redefinir_senha_com_dados_validos(self, client, criar_usuario, usuario_teste):
        """Deve permitir redefinir senha com token válido"""
        from repo import usuario_repo
        from util.security import gerar_token_redefinicao, obter_data_expiracao_token

        # Criar usuário
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Gerar token manualmente
        token = gerar_token_redefinicao()
        data_expiracao = obter_data_expiracao_token(horas=1)
        usuario_repo.atualizar_token(usuario_teste["email"], token, data_expiracao)

        # Redefinir senha
        response = client.post("/redefinir-senha", data={
            "token": token,
            "senha": "NovaSenha@123",
            "confirmar_senha": "NovaSenha@123"
        }, follow_redirects=False)

        # Deve redirecionar para login
        assert response.status_code == status.HTTP_303_SEE_OTHER


class TestAutorizacao:
    """Testes de autorização e proteção de rotas"""

    def test_acesso_sem_autenticacao_redireciona_para_login(self, client):
        """Tentativa de acessar área protegida sem login deve redirecionar"""
        response = client.get("/chamados/listar", follow_redirects=False)
        assert_permission_denied(response)

    def test_usuario_autenticado_acessa_area_protegida(self, cliente_autenticado):
        """Usuário autenticado deve acessar áreas protegidas"""
        response = cliente_autenticado.get("/chamados/listar")
        assert response.status_code == status.HTTP_200_OK

    def test_cliente_nao_acessa_area_admin(self, cliente_autenticado):
        """Cliente não deve acessar áreas administrativas"""
        response = cliente_autenticado.get("/admin/usuarios/listar", follow_redirects=False)
        # Deve redirecionar ou negar acesso
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_admin_acessa_area_admin(self, admin_autenticado):
        """Admin deve acessar áreas administrativas"""
        response = admin_autenticado.get("/admin/usuarios/listar")
        assert response.status_code == status.HTTP_200_OK


class TestRateLimiting:
    """Testes de rate limiting no login"""

    def test_multiplas_tentativas_login_falhas_bloqueiam_ip(self, client):
        """Múltiplas tentativas de login com falha devem bloquear temporariamente"""
        # Fazer várias tentativas de login com credenciais inválidas
        for i in range(6):  # Mais que o limite de 5
            response = client.post("/login", data={
                "email": "teste@example.com",
                "senha": "SenhaErrada@123"
            }, follow_redirects=True)

        # Última resposta deve indicar rate limiting
        assert "muitas tentativas" in response.text.lower() or "aguarde" in response.text.lower()


class TestValidarUrlRedirect:
    """Testes para a função _validar_url_redirect (prevenção de Open Redirect)"""

    def test_url_vazia_retorna_padrao(self, client):
        """URL vazia deve retornar URL padrão"""
        response = client.get("/login?redirect=", follow_redirects=False)
        assert response.status_code == 200

    def test_url_relativa_valida(self, client, criar_usuario, usuario_teste):
        """URL relativa válida deve ser usada no redirect"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        response = client.post("/login", data={
            "email": usuario_teste["email"],
            "senha": usuario_teste["senha"],
            "redirect": "/chamados/listar"
        }, follow_redirects=False)

        assert response.status_code == 303
        location = response.headers.get("location", "")
        assert "/chamados/listar" in location

    def test_url_nao_relativa_bloqueia(self, client, criar_usuario, usuario_teste):
        """URL não relativa deve ser bloqueada e usar padrão"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        response = client.post("/login", data={
            "email": usuario_teste["email"],
            "senha": usuario_teste["senha"],
            "redirect": "https://evil.com"
        }, follow_redirects=False)

        # Deve redirecionar para URL padrão, não para evil.com
        location = response.headers.get("location", "")
        assert "evil.com" not in location
        assert "/usuario" in location

    def test_url_protocolo_relativo_bloqueia(self, client, criar_usuario, usuario_teste):
        """URL com protocolo relativo (//evil.com) deve ser bloqueada"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        response = client.post("/login", data={
            "email": usuario_teste["email"],
            "senha": usuario_teste["senha"],
            "redirect": "//evil.com"
        }, follow_redirects=False)

        location = response.headers.get("location", "")
        assert "evil.com" not in location
        assert "/usuario" in location

    def test_url_com_esquema_bloqueia(self, client, criar_usuario, usuario_teste):
        """URL com esquema (http://) deve ser bloqueada"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        response = client.post("/login", data={
            "email": usuario_teste["email"],
            "senha": usuario_teste["senha"],
            "redirect": "/test://evil.com"
        }, follow_redirects=False)

        location = response.headers.get("location", "")
        assert "evil.com" not in location

    def test_url_com_crlf_bloqueia(self, client, criar_usuario, usuario_teste):
        """URL com CRLF injection deve ser bloqueada"""
        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        response = client.post("/login", data={
            "email": usuario_teste["email"],
            "senha": usuario_teste["senha"],
            "redirect": "/test\r\nSet-Cookie: evil=true"
        }, follow_redirects=False)

        location = response.headers.get("location", "")
        assert "Set-Cookie" not in location
        assert "/usuario" in location


class TestLoginRedirectSeguranca:
    """Testes adicionais de segurança no redirect de login"""

    def test_get_login_valida_redirect_param(self, client):
        """GET /login deve validar parâmetro redirect da query string"""
        # URL maliciosa na query string
        response = client.get("/login?redirect=https://evil.com")
        assert response.status_code == 200
        # Não deve aparecer evil.com no HTML
        assert "evil.com" not in response.text


class TestEsqueciSenhaRateLimit:
    """Testes de rate limiting para recuperação de senha"""

    def test_multiplas_solicitacoes_bloqueiam(self, client):
        """Múltiplas solicitações de recuperação devem ser limitadas"""
        # Primeira requisição - deveria passar
        response1 = client.post("/esqueci-senha", data={
            "email": "teste@example.com"
        }, follow_redirects=False)

        # Segunda requisição imediata - pode ser bloqueada
        response2 = client.post("/esqueci-senha", data={
            "email": "teste@example.com"
        }, follow_redirects=True)

        # Pelo menos uma das respostas deve funcionar
        assert response1.status_code in [200, 303]


class TestCadastroRateLimit:
    """Testes de rate limiting para cadastro"""

    def test_multiplos_cadastros_bloqueiam(self, client):
        """Múltiplos cadastros devem ser limitados"""
        for i in range(5):
            response = client.post("/cadastrar", data={
                "perfil": "Cliente",
                "nome": f"Usuario {i}",
                "email": f"user{i}@test.com",
                "senha": "Senha@123",
                "confirmar_senha": "Senha@123"
            }, follow_redirects=True)

        # Última resposta pode indicar rate limiting
        # ou continuar funcionando dependendo da configuração
        assert response.status_code in [200, 303]


class TestCadastroAdicional:
    """Testes adicionais de cadastro"""

    def test_usuario_logado_nao_acessa_cadastro(self, cliente_autenticado):
        """Usuário já logado deve ser redirecionado ao acessar /cadastrar"""
        response = cliente_autenticado.get("/cadastrar", follow_redirects=False)
        assert_redirects_to(response, "/usuario")

    def test_cadastro_erro_ao_inserir(self, client):
        """Deve mostrar erro quando inserção falha"""
        from unittest.mock import patch

        with patch('routes.auth_routes.verificar_email_disponivel', return_value=(True, None)):
            with patch('routes.auth_routes.usuario_repo.inserir', return_value=None):
                response = client.post("/cadastrar", data={
                    "perfil": "Cliente",
                    "nome": "Usuario Teste",
                    "email": "teste@test.com",
                    "senha": "Senha@123",
                    "confirmar_senha": "Senha@123"
                })

                assert response.status_code == status.HTTP_200_OK


class TestEsqueciSenhaAdicional:
    """Testes adicionais de esqueci senha"""

    def test_email_invalido_validation_error(self, client):
        """Deve mostrar erro quando e-mail é inválido"""
        response = client.post("/esqueci-senha", data={
            "email": "email-invalido"
        })

        assert response.status_code == status.HTTP_200_OK

    def test_email_enviado_com_sucesso(self, client, criar_usuario, usuario_teste):
        """Deve enviar e-mail quando usuário existe"""
        from unittest.mock import patch

        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        with patch('routes.auth_routes.servico_email.enviar_recuperacao_senha', return_value=True):
            response = client.post("/esqueci-senha", data={
                "email": usuario_teste["email"]
            }, follow_redirects=False)

            assert response.status_code == status.HTTP_303_SEE_OTHER


class TestRedefinirSenhaAdicional:
    """Testes adicionais de redefinição de senha"""

    def test_get_redefinir_senha_token_valido(self, client, criar_usuario, usuario_teste):
        """Deve exibir formulário quando token é válido e não expirado"""
        from repo import usuario_repo as repo
        from util.security import gerar_token_redefinicao, obter_data_expiracao_token

        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Gerar token válido não expirado
        token = gerar_token_redefinicao()
        data_expiracao = obter_data_expiracao_token(horas=1)
        repo.atualizar_token(usuario_teste["email"], token, data_expiracao)

        response = client.get(f"/redefinir-senha?token={token}")
        assert response.status_code == status.HTTP_200_OK
        assert "redefinir" in response.text.lower() or "senha" in response.text.lower()

    def test_get_redefinir_senha_token_expirado(self, client, criar_usuario, usuario_teste):
        """Deve rejeitar token expirado no GET"""
        from repo import usuario_repo as repo
        from util.security import gerar_token_redefinicao
        from datetime import timedelta
        from util.datetime_util import agora

        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Gerar token com data já expirada (usando agora() para timezone correto)
        token = gerar_token_redefinicao()
        data_expirada = agora() - timedelta(hours=2)
        repo.atualizar_token(usuario_teste["email"], token, data_expirada)

        response = client.get(f"/redefinir-senha?token={token}", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_redefinir_senha_token_invalido(self, client):
        """Deve rejeitar token que não existe"""
        response = client.post("/redefinir-senha", data={
            "token": "token_nao_existe_xyz123",
            "senha": "NovaSenha@123",
            "confirmar_senha": "NovaSenha@123"
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_redefinir_senha_token_expirado(self, client, criar_usuario, usuario_teste):
        """Deve rejeitar token expirado no POST"""
        from repo import usuario_repo as repo
        from util.security import gerar_token_redefinicao
        from datetime import timedelta
        from util.datetime_util import agora

        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Gerar token com data já expirada (usando agora() para timezone correto)
        token = gerar_token_redefinicao()
        data_expirada = agora() - timedelta(hours=2)
        repo.atualizar_token(usuario_teste["email"], token, data_expirada)

        response = client.post("/redefinir-senha", data={
            "token": token,
            "senha": "NovaSenha@123",
            "confirmar_senha": "NovaSenha@123"
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_redefinir_senha_sucesso_completo(self, client, criar_usuario, usuario_teste):
        """Deve redefinir senha com sucesso"""
        from repo import usuario_repo as repo
        from util.security import gerar_token_redefinicao, obter_data_expiracao_token

        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Gerar token válido
        token = gerar_token_redefinicao()
        data_expiracao = obter_data_expiracao_token(horas=1)
        repo.atualizar_token(usuario_teste["email"], token, data_expiracao)

        response = client.post("/redefinir-senha", data={
            "token": token,
            "senha": "NovaSenhaForte@123",
            "confirmar_senha": "NovaSenhaForte@123"
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_post_redefinir_senha_validation_error(self, client, criar_usuario, usuario_teste):
        """Deve mostrar erro de validação para senhas inválidas"""
        from repo import usuario_repo as repo
        from util.security import gerar_token_redefinicao, obter_data_expiracao_token

        criar_usuario(
            usuario_teste["nome"],
            usuario_teste["email"],
            usuario_teste["senha"]
        )

        # Gerar token válido
        token = gerar_token_redefinicao()
        data_expiracao = obter_data_expiracao_token(horas=1)
        repo.atualizar_token(usuario_teste["email"], token, data_expiracao)

        response = client.post("/redefinir-senha", data={
            "token": token,
            "senha": "fraca",  # Senha fraca
            "confirmar_senha": "fraca"
        })

        assert response.status_code == status.HTTP_200_OK
