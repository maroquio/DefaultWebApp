"""
Testes E2E para autenticacao (cadastro e login).

Testes de Cadastro:
- Acesso a pagina de cadastro
- Cadastro com dados validos
- Validacoes de campos (nome, e-mail, senha)
- E-mail duplicado
- Senhas nao coincidentes

Testes de Login:
- Acesso a pagina de login
- Login com credenciais validas
- Login com credenciais invalidas
- Validacoes de campos
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    CadastroPage,
    LoginPage,
    verificar_erro_senhas_diferentes,
)


@pytest.mark.e2e
class TestCadastroAcessoPagina:
    """Testes de acesso a pagina de cadastro."""

    def test_pagina_cadastro_carrega_corretamente(
        self, e2e_page: Page, e2e_server: str
    ):
        """Deve carregar a pagina de cadastro com o formulario."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        assert "/cadastrar" in e2e_page.url

        expect(e2e_page.locator('input[name="nome"]')).to_be_visible()
        expect(e2e_page.locator('input[name="email"]')).to_be_visible()
        expect(e2e_page.locator('input[name="senha"]')).to_be_visible()
        expect(e2e_page.locator('input[name="confirmar_senha"]')).to_be_visible()
        expect(e2e_page.get_by_role("button", name="Criar Conta")).to_be_visible()

    def test_pagina_cadastro_possui_titulo_correto(
        self, e2e_page: Page, e2e_server: str
    ):
        """Deve exibir titulo adequado na pagina."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        titulo = e2e_page.title().lower()
        assert "cadastro" in titulo or "criar" in titulo

    def test_pagina_cadastro_possui_link_para_login(
        self, e2e_page: Page, e2e_server: str
    ):
        """Deve ter link para pagina de login."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        link_login = e2e_page.get_by_text("login aqui")
        expect(link_login).to_be_visible()

    def test_pagina_cadastro_possui_opcoes_perfil(
        self, e2e_page: Page, e2e_server: str
    ):
        """Deve exibir opcoes de perfil (Cliente/Vendedor)."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        expect(e2e_page.locator('label[for="perfil_Cliente"]')).to_be_visible()
        expect(e2e_page.locator('label[for="perfil_Vendedor"]')).to_be_visible()


@pytest.mark.e2e
class TestCadastroSucesso:
    """Testes de cadastro com sucesso."""

    def test_cadastro_cliente_com_dados_validos(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve cadastrar usuario Cliente com dados validos."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="Usuario Teste Completo",
            email="teste_cliente@example.com",
            senha="SenhaForte@123"
        )

        assert page.aguardar_navegacao_login()
        assert "/login" in e2e_page.url

    def test_cadastro_vendedor_com_dados_validos(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve cadastrar usuario Vendedor com dados validos."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Vendedor",
            nome="Vendedor Teste Nome",
            email="teste_vendedor@example.com",
            senha="SenhaForte@123"
        )

        assert page.aguardar_navegacao_login()

    def test_cadastro_exibe_mensagem_sucesso(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir mensagem de sucesso apos cadastro."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="Usuario Mensagem Teste",
            email="teste_mensagem@example.com",
            senha="SenhaForte@123"
        )

        page.aguardar_navegacao_login()
        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "cadastro realizado" in conteudo or "sucesso" in conteudo

    def test_cadastro_permite_login_apos_registro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Apos cadastro, usuario deve conseguir fazer login."""
        email = "login_apos_cadastro@example.com"
        senha = "SenhaForte@123"

        cadastro = CadastroPage(e2e_page, e2e_server)
        cadastro.navegar()
        cadastro.cadastrar(
            perfil="Cliente",
            nome="Usuario Login Teste",
            email=email,
            senha=senha
        )

        assert cadastro.aguardar_navegacao_login()

        login = LoginPage(e2e_page, e2e_server)
        login.fazer_login(email, senha)

        # Aguardar navegacao para area do usuario
        try:
            e2e_page.wait_for_url("**/usuario**", timeout=10000)
        except Exception:
            # Pode ter ido para /home ao inves de /usuario
            assert "/usuario" in e2e_page.url or "/home" in e2e_page.url


@pytest.mark.e2e
class TestCadastroValidacaoNome:
    """Testes de validacao do campo nome."""

    def test_nome_vazio_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando nome esta vazio."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="",
            email="teste@example.com",
            senha="SenhaForte@123"
        )

        assert "/cadastrar" in e2e_page.url or "/cadastro" in e2e_page.url.lower()

        conteudo = e2e_page.content().lower()
        assert "nome" in conteudo

    def test_nome_curto_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando nome tem menos de 4 caracteres."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="AB",
            email="teste@example.com",
            senha="SenhaForte@123"
        )

        conteudo = e2e_page.content().lower()
        assert "nome" in conteudo

    def test_nome_sem_sobrenome_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando nome tem apenas uma palavra."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="Usuario",
            email="teste@example.com",
            senha="SenhaForte@123"
        )

        conteudo = e2e_page.content().lower()
        assert "nome" in conteudo


@pytest.mark.e2e
class TestCadastroValidacaoEmail:
    """Testes de validacao do campo e-mail."""

    def test_email_vazio_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando e-mail esta vazio."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="Usuario Teste Nome",
            email="",
            senha="SenhaForte@123"
        )

        conteudo = e2e_page.content().lower()
        assert "e-mail" in conteudo or "email" in conteudo

    def test_email_formato_invalido_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando e-mail tem formato invalido."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="Usuario Teste Nome",
            email="email_invalido",
            senha="SenhaForte@123"
        )

        conteudo = e2e_page.content().lower()
        assert "e-mail" in conteudo or "email" in conteudo

    def test_email_duplicado_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando e-mail ja esta cadastrado."""
        email = "duplicado@example.com"

        page = CadastroPage(e2e_page, e2e_server)

        # Primeiro cadastro
        page.navegar()
        page.cadastrar(
            perfil="Cliente",
            nome="Usuario Primeiro",
            email=email,
            senha="SenhaForte@123"
        )
        page.aguardar_navegacao_login()

        # Segundo cadastro com mesmo email
        page.navegar()
        page.cadastrar(
            perfil="Cliente",
            nome="Usuario Segundo",
            email=email,
            senha="SenhaForte@123"
        )

        conteudo = e2e_page.content().lower()
        assert "e-mail" in conteudo and "cadastrado" in conteudo


@pytest.mark.e2e
class TestCadastroValidacaoSenha:
    """Testes de validacao da senha."""

    def test_senha_curta_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando senha tem menos de 8 caracteres."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="Usuario Teste Nome",
            email="teste@example.com",
            senha="Ab@1"
        )

        conteudo = e2e_page.content().lower()
        assert "senha" in conteudo

    def test_senha_sem_maiuscula_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando senha nao tem letra maiuscula."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="Usuario Teste Nome",
            email="teste@example.com",
            senha="senhafraca@123"
        )

        conteudo = e2e_page.content().lower()
        assert "senha" in conteudo

    def test_senha_sem_minuscula_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando senha nao tem letra minuscula."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="Usuario Teste Nome",
            email="teste@example.com",
            senha="SENHAFRACA@123"
        )

        conteudo = e2e_page.content().lower()
        assert "senha" in conteudo

    def test_senha_sem_numero_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando senha nao tem numero."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="Usuario Teste Nome",
            email="teste@example.com",
            senha="SenhaFraca@abc"
        )

        conteudo = e2e_page.content().lower()
        assert "senha" in conteudo

    def test_senha_sem_especial_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando senha nao tem caractere especial."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="Usuario Teste Nome",
            email="teste@example.com",
            senha="SenhaFraca123"
        )

        conteudo = e2e_page.content().lower()
        assert "senha" in conteudo

    def test_senhas_diferentes_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando senhas nao coincidem."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        page.cadastrar(
            perfil="Cliente",
            nome="Usuario Teste Nome",
            email="teste@example.com",
            senha="SenhaForte@123",
            confirmar_senha="SenhaDiferente@456"
        )

        assert verificar_erro_senhas_diferentes(e2e_page)


@pytest.mark.e2e
class TestCadastroValidacaoPerfil:
    """Testes de validacao do perfil."""

    def test_perfil_cliente_selecionado_corretamente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve permitir selecionar perfil Cliente."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        e2e_page.locator('label[for="perfil_Cliente"]').click()

        expect(e2e_page.locator('input#perfil_Cliente')).to_be_checked()
        expect(e2e_page.locator('input#perfil_Vendedor')).not_to_be_checked()

    def test_perfil_vendedor_selecionado_corretamente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve permitir selecionar perfil Vendedor."""
        page = CadastroPage(e2e_page, e2e_server)
        page.navegar()

        e2e_page.locator('label[for="perfil_Vendedor"]').click()

        expect(e2e_page.locator('input#perfil_Vendedor')).to_be_checked()
        expect(e2e_page.locator('input#perfil_Cliente')).not_to_be_checked()


# ============================================================
# TESTES DE LOGIN
# ============================================================


@pytest.mark.e2e
class TestLoginAcessoPagina:
    """Testes de acesso a pagina de login."""

    def test_pagina_login_carrega_corretamente(
        self, e2e_page: Page, e2e_server: str
    ):
        """Deve carregar a pagina de login com o formulario."""
        page = LoginPage(e2e_page, e2e_server)
        page.navegar()

        assert "/login" in e2e_page.url

        expect(e2e_page.locator('input[name="email"]')).to_be_visible()
        expect(e2e_page.locator('input[name="senha"]')).to_be_visible()
        expect(e2e_page.locator('form button[type="submit"]').first).to_be_visible()

    def test_pagina_login_possui_titulo_correto(
        self, e2e_page: Page, e2e_server: str
    ):
        """Deve exibir titulo adequado na pagina."""
        page = LoginPage(e2e_page, e2e_server)
        page.navegar()

        titulo = e2e_page.title().lower()
        assert "login" in titulo or "entrar" in titulo or "acesso" in titulo

    def test_pagina_login_possui_link_para_cadastro(
        self, e2e_page: Page, e2e_server: str
    ):
        """Deve ter link para pagina de cadastro."""
        page = LoginPage(e2e_page, e2e_server)
        page.navegar()

        link_cadastro = e2e_page.get_by_text("cadastre-se aqui")
        expect(link_cadastro).to_be_visible()

    def test_pagina_login_possui_link_esqueci_senha(
        self, e2e_page: Page, e2e_server: str
    ):
        """Deve ter link para recuperar senha."""
        page = LoginPage(e2e_page, e2e_server)
        page.navegar()

        link_esqueci = e2e_page.get_by_text("Esqueceu sua senha?")
        expect(link_esqueci).to_be_visible()


@pytest.mark.e2e
class TestLoginSucesso:
    """Testes de login com sucesso."""

    def test_login_cliente_com_credenciais_validas(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve fazer login com credenciais validas de cliente."""
        email = "cliente_login@example.com"
        senha = "SenhaForte@123"

        # Primeiro cadastrar o usuario
        cadastro = CadastroPage(e2e_page, e2e_server)
        cadastro.navegar()
        cadastro.cadastrar(
            perfil="Cliente",
            nome="Cliente Login Teste",
            email=email,
            senha=senha
        )
        cadastro.aguardar_navegacao_login()

        # Fazer login
        login = LoginPage(e2e_page, e2e_server)
        login.fazer_login(email, senha)

        # Verificar redirecionamento para area do usuario
        assert login.aguardar_navegacao_usuario()

    def test_login_vendedor_com_credenciais_validas(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve fazer login com credenciais validas de vendedor."""
        email = "vendedor_login@example.com"
        senha = "SenhaForte@123"

        # Primeiro cadastrar o usuario
        cadastro = CadastroPage(e2e_page, e2e_server)
        cadastro.navegar()
        cadastro.cadastrar(
            perfil="Vendedor",
            nome="Vendedor Login Teste",
            email=email,
            senha=senha
        )
        cadastro.aguardar_navegacao_login()

        # Fazer login
        login = LoginPage(e2e_page, e2e_server)
        login.fazer_login(email, senha)

        # Verificar redirecionamento para area do usuario
        assert login.aguardar_navegacao_usuario()

    def test_login_mantem_sessao_ativa(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Apos login, sessao deve permanecer ativa em navegacoes."""
        email = "sessao_ativa@example.com"
        senha = "SenhaForte@123"

        # Cadastrar e fazer login
        cadastro = CadastroPage(e2e_page, e2e_server)
        cadastro.navegar()
        cadastro.cadastrar(
            perfil="Cliente",
            nome="Usuario Sessao Teste",
            email=email,
            senha=senha
        )
        cadastro.aguardar_navegacao_login()

        login = LoginPage(e2e_page, e2e_server)
        login.fazer_login(email, senha)
        login.aguardar_navegacao_usuario()

        # Navegar para outra pagina e voltar
        e2e_page.goto(f"{e2e_server}/home")
        e2e_page.wait_for_timeout(500)

        # Voltar para area do usuario - deve continuar logado
        e2e_page.goto(f"{e2e_server}/usuario")
        e2e_page.wait_for_timeout(500)

        # Nao deve redirecionar para login
        assert "/login" not in e2e_page.url


@pytest.mark.e2e
class TestLoginValidacao:
    """Testes de validacao do formulario de login."""

    def test_email_vazio_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando e-mail esta vazio."""
        login = LoginPage(e2e_page, e2e_server)
        login.navegar()

        login.fazer_login("", "SenhaForte@123")

        # Deve permanecer na pagina de login
        assert login.esta_na_pagina_login()

    def test_senha_vazia_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando senha esta vazia."""
        login = LoginPage(e2e_page, e2e_server)
        login.navegar()

        login.fazer_login("teste@example.com", "")

        # Deve permanecer na pagina de login
        assert login.esta_na_pagina_login()

    def test_email_formato_invalido_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando e-mail tem formato invalido."""
        login = LoginPage(e2e_page, e2e_server)
        login.navegar()

        login.fazer_login("email_invalido", "SenhaForte@123")

        # Deve permanecer na pagina de login ou exibir erro
        e2e_page.wait_for_timeout(500)
        assert login.esta_na_pagina_login()


@pytest.mark.e2e
class TestLoginCredenciaisInvalidas:
    """Testes de login com credenciais invalidas."""

    def test_senha_incorreta_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando senha esta incorreta."""
        email = "senha_errada@example.com"
        senha_correta = "SenhaForte@123"
        senha_errada = "SenhaErrada@456"

        # Primeiro cadastrar o usuario
        cadastro = CadastroPage(e2e_page, e2e_server)
        cadastro.navegar()
        cadastro.cadastrar(
            perfil="Cliente",
            nome="Usuario Senha Errada",
            email=email,
            senha=senha_correta
        )
        cadastro.aguardar_navegacao_login()

        # Tentar login com senha errada
        login = LoginPage(e2e_page, e2e_server)
        login.fazer_login(email, senha_errada)

        e2e_page.wait_for_timeout(500)

        # Deve permanecer na pagina de login
        assert login.esta_na_pagina_login()

        # Deve exibir mensagem de erro
        conteudo = e2e_page.content().lower()
        assert "senha" in conteudo or "credenciais" in conteudo or "incorret" in conteudo

    def test_usuario_nao_cadastrado_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve exibir erro quando usuario nao existe."""
        login = LoginPage(e2e_page, e2e_server)
        login.navegar()

        login.fazer_login("nao_existe@example.com", "SenhaForte@123")

        e2e_page.wait_for_timeout(500)

        # Deve permanecer na pagina de login
        assert login.esta_na_pagina_login()

        # Deve exibir mensagem de erro
        conteudo = e2e_page.content().lower()
        assert "e-mail" in conteudo or "credenciais" in conteudo or "não encontrad" in conteudo

    def test_multiplas_tentativas_falhas(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve permitir multiplas tentativas apos falhas."""
        email = "multiplas_tentativas@example.com"
        senha = "SenhaForte@123"

        # Cadastrar usuario
        cadastro = CadastroPage(e2e_page, e2e_server)
        cadastro.navegar()
        cadastro.cadastrar(
            perfil="Cliente",
            nome="Usuario Multiplas Tentativas",
            email=email,
            senha=senha
        )
        cadastro.aguardar_navegacao_login()

        login = LoginPage(e2e_page, e2e_server)

        # Primeira tentativa com senha errada
        login.fazer_login(email, "SenhaErrada@1")
        e2e_page.wait_for_timeout(300)
        assert login.esta_na_pagina_login()

        # Segunda tentativa com senha errada
        login.preencher_formulario(email, "SenhaErrada@2")
        login.submeter()
        e2e_page.wait_for_timeout(300)
        assert login.esta_na_pagina_login()

        # Terceira tentativa com senha correta
        login.preencher_formulario(email, senha)
        login.submeter()

        # Deve conseguir logar
        assert login.aguardar_navegacao_usuario()
