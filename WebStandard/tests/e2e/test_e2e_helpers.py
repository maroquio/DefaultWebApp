"""
Funcoes auxiliares e Page Objects para testes E2E.

Fornece helpers para interacoes comuns com a UI.
"""
from typing import Optional

from playwright.sync_api import Page, expect


class CadastroPage:
    """Page Object para a pagina de cadastro."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/cadastrar"

    def navegar(self) -> None:
        """Navega para a pagina de cadastro."""
        self.page.goto(self.url)

    def preencher_formulario(
        self,
        perfil: str,
        nome: str,
        email: str,
        senha: str,
        confirmar_senha: Optional[str] = None
    ) -> None:
        """
        Preenche o formulario de cadastro.

        Args:
            perfil: "Cliente" ou "Vendedor"
            nome: Nome completo
            email: E-mail
            senha: Senha
            confirmar_senha: Confirmacao de senha (usa senha se nao informado)
        """
        if confirmar_senha is None:
            confirmar_senha = senha

        # Selecionar perfil (radio button com estilo de botao Bootstrap)
        # Precisamos clicar no label pois o input esta escondido
        self.page.locator(f'label[for="perfil_{perfil}"]').click()

        # Preencher campos
        self.page.fill('input[name="nome"]', nome)
        self.page.fill('input[name="email"]', email)
        self.page.fill('input[name="senha"]', senha)
        self.page.fill('input[name="confirmar_senha"]', confirmar_senha)

    def submeter(self) -> None:
        """Submete o formulario."""
        self.page.get_by_role("button", name="Criar Conta").click()

    def cadastrar(
        self,
        perfil: str,
        nome: str,
        email: str,
        senha: str,
        confirmar_senha: Optional[str] = None
    ) -> None:
        """
        Realiza cadastro completo: preenche e submete.
        """
        self.preencher_formulario(perfil, nome, email, senha, confirmar_senha)
        self.submeter()

    def obter_mensagem_erro_campo(self, campo: str) -> Optional[str]:
        """
        Obtem mensagem de erro de um campo especifico.

        Args:
            campo: Nome do campo (nome, email, senha, confirmar_senha)

        Returns:
            Texto da mensagem de erro ou None
        """
        seletor = f'input[name="{campo}"] ~ .invalid-feedback'
        elemento = self.page.locator(seletor).first

        if elemento.is_visible():
            return elemento.text_content()
        return None

    def obter_mensagem_flash(self) -> Optional[str]:
        """
        Obtem mensagem flash (toast ou alert).

        Returns:
            Texto da mensagem ou None
        """
        toast = self.page.locator('.toast-body').first
        if toast.is_visible():
            return toast.text_content()

        alert = self.page.locator('.alert').first
        if alert.is_visible():
            return alert.text_content()

        return None

    def aguardar_navegacao_login(self, timeout: int = 5000) -> bool:
        """
        Aguarda redirecionamento para pagina de login.

        Args:
            timeout: Tempo maximo em ms

        Returns:
            True se redirecionou, False caso contrario
        """
        try:
            self.page.wait_for_url("**/login**", timeout=timeout)
            return True
        except Exception:
            return False


class LoginPage:
    """Page Object para a pagina de login."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.url = f"{base_url}/login"

    def navegar(self) -> None:
        """Navega para a pagina de login."""
        self.page.goto(self.url)

    def preencher_formulario(self, email: str, senha: str) -> None:
        """Preenche o formulario de login sem submeter."""
        self.page.wait_for_selector('input[name="email"]')
        self.page.fill('input[name="email"]', email)
        self.page.fill('input[name="senha"]', senha)

    def submeter(self) -> None:
        """Submete o formulario de login."""
        self.page.locator('form button[type="submit"]').first.click()

    def fazer_login(self, email: str, senha: str) -> None:
        """Preenche e submete formulario de login."""
        self.preencher_formulario(email, senha)
        self.submeter()

    def esta_na_pagina_login(self) -> bool:
        """Verifica se esta na pagina de login."""
        return "/login" in self.page.url

    def aguardar_navegacao_usuario(self, timeout: int = 10000) -> bool:
        """
        Aguarda redirecionamento para area do usuario.

        Args:
            timeout: Tempo maximo em ms

        Returns:
            True se redirecionou, False caso contrario
        """
        try:
            self.page.wait_for_url("**/usuario**", timeout=timeout)
            return True
        except Exception:
            # Pode ter ido para /home
            return "/usuario" in self.page.url or "/home" in self.page.url

    def obter_mensagem_flash(self) -> Optional[str]:
        """
        Obtem mensagem flash (toast ou alert).

        Returns:
            Texto da mensagem ou None
        """
        toast = self.page.locator('.toast-body').first
        if toast.is_visible():
            return toast.text_content()

        alert = self.page.locator('.alert').first
        if alert.is_visible():
            return alert.text_content()

        return None


def verificar_mensagem_sucesso_cadastro(page: Page) -> bool:
    """
    Verifica se a mensagem de sucesso do cadastro foi exibida.

    A mensagem esperada e: "Cadastro realizado com sucesso!"
    """
    try:
        toast = page.locator('.toast-body')
        if toast.is_visible():
            texto = toast.text_content() or ""
            return "cadastro realizado com sucesso" in texto.lower()

        alert = page.locator('.alert-success')
        if alert.is_visible():
            texto = alert.text_content() or ""
            return "cadastro realizado com sucesso" in texto.lower()
    except Exception:
        pass

    return False


def verificar_erro_email_duplicado(page: Page) -> bool:
    """
    Verifica se apareceu erro de e-mail duplicado.

    A mensagem esperada contem: "e-mail ja esta cadastrado"
    """
    try:
        conteudo = page.content().lower()
        return "e-mail" in conteudo and "cadastrado" in conteudo
    except Exception:
        return False


def verificar_erro_senhas_diferentes(page: Page) -> bool:
    """
    Verifica se apareceu erro de senhas nao coincidentes.

    A mensagem esperada: "As senhas nao coincidem."
    """
    try:
        conteudo = page.content().lower()
        return "senhas" in conteudo and "coincidem" in conteudo
    except Exception:
        return False
