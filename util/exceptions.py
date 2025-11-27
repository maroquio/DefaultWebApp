"""
Exceções customizadas para tratamento de erros no sistema.

Este módulo define exceções personalizadas usadas em conjunto com
exception handlers globais para centralizar o tratamento de erros.
"""

from pydantic import ValidationError


class ErroValidacaoFormulario(Exception):
    """
    Exceção customizada para erros de validação de formulários DTO.

    Esta exceção encapsula um ValidationError do Pydantic junto com
    todas as informações necessárias para renderizar a página de erro
    de forma consistente.

    É capturada por um exception handler global que:
    1. Processa os erros de validação
    2. Exibe mensagem flash
    3. Renderiza o template com dados e erros

    Attributes:
        validation_error: O ValidationError original do Pydantic
        template_path: Caminho do template a renderizar (ex: "auth/login.html")
        dados_formulario: Dicionário com dados do formulário para reexibição
        campo_padrao: Campo a usar quando erro não tem campo específico (erros de @model_validator)
        mensagem_flash: Mensagem a exibir no toast de erro
    """

    def __init__(
        self,
        validation_error: ValidationError,
        template_path: str,
        dados_formulario: dict,
        campo_padrao: str = "geral",
        mensagem_flash: str = "Há campos com erros de validação.",
    ):
        """
        Inicializa a exceção com todas as informações necessárias.

        Args:
            validation_error: O ValidationError original do Pydantic
            template_path: Caminho do template Jinja2 (relativo a templates/)
            dados_formulario: Dados do formulário para reexibir ao usuário
            campo_padrao: Campo padrão para erros sem loc específico (default: "geral")
            mensagem_flash: Mensagem de erro a exibir no toast (default: mensagem genérica)
        """
        self.validation_error = validation_error
        self.template_path = template_path
        self.dados_formulario = dados_formulario
        self.campo_padrao = campo_padrao
        self.mensagem_flash = mensagem_flash

        # Mensagem da exceção para logging
        super().__init__(
            f"Erro de validação em '{template_path}': {len(validation_error.errors())} erro(s)"
        )
