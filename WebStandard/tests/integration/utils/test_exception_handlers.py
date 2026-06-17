"""
Testes para o módulo util/exception_handlers.py

Testa os handlers de exceções HTTP e de validação.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import status
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError, BaseModel

from util.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
    form_validation_exception_handler
)
from util.exceptions import ErroValidacaoFormulario


class TestHttpExceptionHandler:
    """Testes para o handler de exceções HTTP"""

    @pytest.mark.asyncio
    async def test_401_redireciona_para_login(self):
        """401 deve redirecionar para login"""
        request = MagicMock()
        request.url.path = "/area-protegida"
        request.client.host = "127.0.0.1"

        exc = StarletteHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )

        response = await http_exception_handler(request, exc)

        assert isinstance(response, RedirectResponse)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    @pytest.mark.asyncio
    async def test_403_redireciona_para_login(self):
        """403 deve redirecionar para login"""
        request = MagicMock()
        request.url.path = "/admin"
        request.client.host = "127.0.0.1"

        exc = StarletteHTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão"
        )

        response = await http_exception_handler(request, exc)

        assert isinstance(response, RedirectResponse)

    @pytest.mark.asyncio
    async def test_404_retorna_pagina_erro(self):
        """404 deve retornar página de erro"""
        request = MagicMock()
        request.url.path = "/pagina-inexistente"
        request.client.host = "127.0.0.1"

        exc = StarletteHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Não encontrado"
        )

        with patch('util.exception_handlers.templates') as mock_templates:
            mock_templates.TemplateResponse.return_value = MagicMock()

            response = await http_exception_handler(request, exc)

            mock_templates.TemplateResponse.assert_called_once()
            call_args = mock_templates.TemplateResponse.call_args
            assert "errors/404.html" in call_args[0]

    @pytest.mark.asyncio
    async def test_404_arquivos_estaticos_loga_debug(self):
        """404 para arquivos estáticos opcionais deve logar como debug"""
        request = MagicMock()
        request.url.path = "/static/file.map"
        request.client.host = "127.0.0.1"

        exc = StarletteHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Não encontrado"
        )

        with patch('util.exception_handlers.templates'):
            with patch('util.exception_handlers.logger') as mock_logger:
                await http_exception_handler(request, exc)

                # Deve usar debug ao invés de warning para .map
                mock_logger.debug.assert_called()

    @pytest.mark.asyncio
    async def test_500_retorna_pagina_erro_generica(self):
        """500 deve retornar página de erro genérica"""
        request = MagicMock()
        request.url.path = "/erro"
        request.client.host = "127.0.0.1"
        request.method = "GET"

        exc = StarletteHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno"
        )

        with patch('util.exception_handlers.templates') as mock_templates:
            mock_templates.TemplateResponse.return_value = MagicMock()

            response = await http_exception_handler(request, exc)

            mock_templates.TemplateResponse.assert_called_once()

    @pytest.mark.asyncio
    async def test_sem_client_host(self):
        """Deve funcionar mesmo sem client.host"""
        request = MagicMock()
        request.url.path = "/test"
        request.client = None

        exc = StarletteHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Não encontrado"
        )

        with patch('util.exception_handlers.templates'):
            # Não deve lançar exceção
            await http_exception_handler(request, exc)


class TestValidationExceptionHandler:
    """Testes para o handler de erros de validação"""

    @pytest.mark.asyncio
    async def test_retorna_422(self):
        """Deve retornar status 422"""
        request = MagicMock()
        request.url.path = "/api/teste"
        request.method = "POST"
        request.client.host = "127.0.0.1"

        exc = MagicMock(spec=RequestValidationError)
        exc.errors.return_value = [
            {"loc": ["body", "campo"], "msg": "valor inválido"}
        ]
        exc.body = {"campo": "valor"}

        with patch('util.exception_handlers.templates') as mock_templates:
            mock_response = MagicMock()
            mock_templates.TemplateResponse.return_value = mock_response

            response = await validation_exception_handler(request, exc)

            call_args = mock_templates.TemplateResponse.call_args
            assert call_args.kwargs['status_code'] == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_exibe_flash_erro(self):
        """Deve exibir flash de erro"""
        request = MagicMock()
        request.url.path = "/api/teste"
        request.method = "POST"
        request.client.host = "127.0.0.1"

        exc = MagicMock(spec=RequestValidationError)
        exc.errors.return_value = [
            {"loc": ["body", "email"], "msg": "email inválido"}
        ]
        exc.body = {}

        with patch('util.exception_handlers.templates'):
            with patch('util.exception_handlers.informar_erro') as mock_flash:
                await validation_exception_handler(request, exc)

                mock_flash.assert_called_once()


class TestGenericExceptionHandler:
    """Testes para o handler genérico de exceções"""

    @pytest.mark.asyncio
    async def test_retorna_500(self):
        """Deve retornar status 500"""
        request = MagicMock()
        request.url.path = "/teste"
        request.method = "GET"
        request.client.host = "127.0.0.1"

        exc = Exception("Erro inesperado")

        with patch('util.exception_handlers.templates') as mock_templates:
            mock_response = MagicMock()
            mock_templates.TemplateResponse.return_value = mock_response

            response = await generic_exception_handler(request, exc)

            call_args = mock_templates.TemplateResponse.call_args
            assert call_args.kwargs['status_code'] == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_loga_erro_completo(self):
        """Deve logar erro completo"""
        request = MagicMock()
        request.url.path = "/teste"
        request.method = "GET"
        request.client.host = "127.0.0.1"

        exc = ValueError("Valor inválido")

        with patch('util.exception_handlers.templates'):
            with patch('util.exception_handlers.logger') as mock_logger:
                await generic_exception_handler(request, exc)

                mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_sem_client(self):
        """Deve funcionar sem client"""
        request = MagicMock()
        request.url.path = "/teste"
        request.method = "GET"
        request.client = None

        exc = Exception("Erro")

        with patch('util.exception_handlers.templates'):
            # Não deve lançar exceção
            await generic_exception_handler(request, exc)


class TestFormValidationExceptionHandler:
    """Testes para o handler de erros de validação de formulário"""

    @pytest.mark.asyncio
    async def test_renderiza_template_com_erros(self):
        """Deve renderizar template com erros"""
        request = MagicMock()
        request.client.host = "127.0.0.1"

        # Criar ValidationError fake
        class FakeModel(BaseModel):
            campo: str

        try:
            FakeModel(campo=None)  # type: ignore
        except ValidationError as e:
            validation_error = e

        exc = ErroValidacaoFormulario(
            validation_error=validation_error,
            template_path="auth/cadastro.html",
            dados_formulario={"campo": ""},
            campo_padrao="campo"
        )

        with patch('util.exception_handlers.templates') as mock_templates:
            mock_templates.TemplateResponse.return_value = MagicMock()

            await form_validation_exception_handler(request, exc)

            mock_templates.TemplateResponse.assert_called_once()
            call_args = mock_templates.TemplateResponse.call_args
            assert call_args[0][0] == "auth/cadastro.html"

    @pytest.mark.asyncio
    async def test_exibe_flash_customizada(self):
        """Deve exibir mensagem flash customizada"""
        request = MagicMock()
        request.client.host = "127.0.0.1"

        class FakeModel(BaseModel):
            campo: str

        try:
            FakeModel(campo=None)  # type: ignore
        except ValidationError as e:
            validation_error = e

        exc = ErroValidacaoFormulario(
            validation_error=validation_error,
            template_path="auth/cadastro.html",
            dados_formulario={},
            mensagem_flash="Mensagem customizada"
        )

        with patch('util.exception_handlers.templates'):
            with patch('util.exception_handlers.informar_erro') as mock_flash:
                await form_validation_exception_handler(request, exc)

                mock_flash.assert_called_once_with(request, "Mensagem customizada")

    @pytest.mark.asyncio
    async def test_contexto_inclui_dados_formulario(self):
        """Contexto deve incluir dados do formulário"""
        request = MagicMock()
        request.client.host = "127.0.0.1"

        class FakeModel(BaseModel):
            nome: str

        try:
            FakeModel(nome=None)  # type: ignore
        except ValidationError as e:
            validation_error = e

        exc = ErroValidacaoFormulario(
            validation_error=validation_error,
            template_path="user/form.html",
            dados_formulario={"nome": "João", "email": "joao@email.com"}
        )

        with patch('util.exception_handlers.templates') as mock_templates:
            await form_validation_exception_handler(request, exc)

            call_args = mock_templates.TemplateResponse.call_args
            context = call_args[0][1]

            assert "dados" in context
            assert context["dados"]["nome"] == "João"
            # Dados também devem estar disponíveis diretamente
            assert context["nome"] == "João"
