"""
Testes para o módulo util/repository_helpers.py

Testa as funções auxiliares para operações comuns em repositórios.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import Request, status
from fastapi.responses import RedirectResponse

from util.repository_helpers import (
    obter_ou_404,
    obter_lista_ou_vazia,
    validar_inteiro_positivo,
    executar_operacao_repo
)


class TestObterOu404:
    """Testes para a função obter_ou_404"""

    @pytest.fixture
    def mock_request(self):
        """Cria mock de Request"""
        request = MagicMock(spec=Request)
        request.url.path = "/test/path"
        request.session = {}
        return request

    def test_entity_existe_retorna_entity(self, mock_request):
        """Quando entidade existe, deve retorná-la"""
        entity = {"id": 1, "nome": "Teste"}

        resultado = obter_ou_404(entity, mock_request)

        assert resultado == entity
        assert not isinstance(resultado, RedirectResponse)

    def test_entity_none_retorna_redirect(self, mock_request):
        """Quando entidade é None, deve retornar RedirectResponse"""
        with patch('util.repository_helpers.informar_erro') as mock_informar:
            resultado = obter_ou_404(None, mock_request)

            assert isinstance(resultado, RedirectResponse)
            assert resultado.status_code == status.HTTP_303_SEE_OTHER
            mock_informar.assert_called_once()

    def test_entity_none_usa_mensagem_custom(self, mock_request):
        """Deve usar mensagem customizada quando fornecida"""
        mensagem = "Usuário não encontrado"

        with patch('util.repository_helpers.informar_erro') as mock_informar:
            obter_ou_404(None, mock_request, mensagem=mensagem)

            mock_informar.assert_called_once_with(mock_request, mensagem)

    def test_entity_none_usa_redirect_url_custom(self, mock_request):
        """Deve redirecionar para URL customizada"""
        redirect_url = "/usuarios"

        with patch('util.repository_helpers.informar_erro'):
            resultado = obter_ou_404(None, mock_request, redirect_url=redirect_url)

            assert resultado.headers.get("location") == redirect_url

    def test_entity_none_loga_erro_por_padrao(self, mock_request):
        """Deve logar erro por padrão quando entidade não existe"""
        with patch('util.repository_helpers.informar_erro'):
            with patch('util.repository_helpers.logger') as mock_logger:
                obter_ou_404(None, mock_request)

                mock_logger.warning.assert_called_once()

    def test_entity_none_nao_loga_quando_desabilitado(self, mock_request):
        """Não deve logar quando log_erro=False"""
        with patch('util.repository_helpers.informar_erro'):
            with patch('util.repository_helpers.logger') as mock_logger:
                obter_ou_404(None, mock_request, log_erro=False)

                mock_logger.warning.assert_not_called()

    def test_entity_com_diferentes_tipos(self, mock_request):
        """Deve funcionar com diferentes tipos de entidade"""
        # String
        assert obter_ou_404("teste", mock_request) == "teste"

        # Int
        assert obter_ou_404(42, mock_request) == 42

        # List
        assert obter_ou_404([1, 2, 3], mock_request) == [1, 2, 3]

        # Object
        obj = MagicMock()
        assert obter_ou_404(obj, mock_request) == obj


class TestObterListaOuVazia:
    """Testes para a função obter_lista_ou_vazia"""

    @pytest.fixture
    def mock_request(self):
        """Cria mock de Request com sessão funcional (sem spec para ser truthy)"""
        request = MagicMock()  # Sem spec para que bool() retorne True
        # Sessão real (dict) para permitir flash messages
        request.session = {}
        return request

    def test_lista_valida_retorna_mesma_lista(self):
        """Quando lista é válida, deve retorná-la"""
        lista = [1, 2, 3]

        resultado = obter_lista_ou_vazia(lista)

        assert resultado == lista

    def test_lista_none_retorna_lista_vazia(self):
        """Quando lista é None, deve retornar lista vazia"""
        resultado = obter_lista_ou_vazia(None)

        assert resultado == []

    def test_valor_nao_lista_retorna_lista_vazia(self):
        """Quando valor não é lista, deve retornar lista vazia"""
        resultado = obter_lista_ou_vazia("não é lista")

        assert resultado == []

    def test_lista_vazia_com_mensagem_aviso(self, mock_request):
        """Deve informar aviso quando lista vazia e mensagem fornecida"""
        # A função importa dinamicamente informar_info
        # Vamos verificar que não levanta exceção e retorna lista vazia
        resultado = obter_lista_ou_vazia(
            [],
            request=mock_request,
            mensagem_aviso="Nenhum registro encontrado"
        )

        assert resultado == []
        # A mensagem flash será adicionada à sessão do request

    def test_lista_vazia_sem_request_nao_informa(self):
        """Não deve informar aviso se request não fornecido"""
        # Sem request, não deve tentar chamar informar_info
        resultado = obter_lista_ou_vazia([], mensagem_aviso="Teste")

        assert resultado == []

    def test_lista_vazia_com_log_aviso(self, mock_request):
        """Deve logar aviso quando log_aviso=True"""
        with patch('util.repository_helpers.logger') as mock_logger:
            obter_lista_ou_vazia(
                [],
                request=mock_request,
                mensagem_aviso="Lista vazia",
                log_aviso=True
            )

            mock_logger.info.assert_called_once()

    def test_lista_populada_nao_informa_aviso(self, mock_request):
        """Não deve informar aviso se lista tem itens"""
        # Com lista populada, não deve chamar informar_info
        resultado = obter_lista_ou_vazia(
            [1, 2, 3],
            request=mock_request,
            mensagem_aviso="Nenhum registro"
        )

        assert resultado == [1, 2, 3]


class TestValidarInteiroPositivo:
    """Testes para a função validar_inteiro_positivo"""

    @pytest.fixture
    def mock_request(self):
        """Cria mock de Request"""
        request = MagicMock(spec=Request)
        request.session = {}
        return request

    def test_inteiro_positivo_retorna_valor(self, mock_request):
        """Inteiro positivo deve ser retornado"""
        resultado = validar_inteiro_positivo(42, mock_request)

        assert resultado == 42

    def test_string_numerica_retorna_inteiro(self, mock_request):
        """String numérica deve ser convertida para inteiro"""
        resultado = validar_inteiro_positivo("123", mock_request)

        assert resultado == 123

    def test_zero_retorna_redirect(self, mock_request):
        """Zero deve retornar RedirectResponse"""
        with patch('util.repository_helpers.informar_erro'):
            resultado = validar_inteiro_positivo(0, mock_request)

            assert isinstance(resultado, RedirectResponse)

    def test_negativo_retorna_redirect(self, mock_request):
        """Número negativo deve retornar RedirectResponse"""
        with patch('util.repository_helpers.informar_erro'):
            resultado = validar_inteiro_positivo(-5, mock_request)

            assert isinstance(resultado, RedirectResponse)

    def test_string_invalida_retorna_redirect(self, mock_request):
        """String não numérica deve retornar RedirectResponse"""
        with patch('util.repository_helpers.informar_erro'):
            resultado = validar_inteiro_positivo("abc", mock_request)

            assert isinstance(resultado, RedirectResponse)

    def test_none_retorna_redirect(self, mock_request):
        """None deve retornar RedirectResponse"""
        with patch('util.repository_helpers.informar_erro'):
            resultado = validar_inteiro_positivo(None, mock_request)

            assert isinstance(resultado, RedirectResponse)

    def test_usa_nome_campo_custom(self, mock_request):
        """Deve usar nome do campo customizado na mensagem"""
        with patch('util.repository_helpers.informar_erro') as mock_informar:
            validar_inteiro_positivo("abc", mock_request, nome_campo="Código")

            mock_informar.assert_called_once_with(mock_request, "Código inválido")

    def test_usa_redirect_url_custom(self, mock_request):
        """Deve redirecionar para URL customizada"""
        with patch('util.repository_helpers.informar_erro'):
            resultado = validar_inteiro_positivo(
                "abc",
                mock_request,
                redirect_url="/usuarios"
            )

            assert resultado.headers.get("location") == "/usuarios"

    def test_loga_warning_em_erro(self, mock_request):
        """Deve logar warning quando validação falha"""
        with patch('util.repository_helpers.informar_erro'):
            with patch('util.repository_helpers.logger') as mock_logger:
                validar_inteiro_positivo("abc", mock_request)

                mock_logger.warning.assert_called_once()


class TestExecutarOperacaoRepo:
    """Testes para a função executar_operacao_repo"""

    @pytest.fixture
    def mock_request(self):
        """Cria mock de Request"""
        request = MagicMock(spec=Request)
        request.session = {}
        return request

    def test_operacao_sucesso_retorna_resultado(self, mock_request):
        """Operação bem-sucedida deve retornar resultado"""
        operacao = lambda: {"id": 1, "nome": "Criado"}

        resultado = executar_operacao_repo(operacao, mock_request)

        assert resultado == {"id": 1, "nome": "Criado"}

    def test_operacao_retorna_none_com_sucesso(self, mock_request):
        """Operação que retorna None deve funcionar"""
        operacao = lambda: None

        resultado = executar_operacao_repo(operacao, mock_request)

        assert resultado is None
        assert not isinstance(resultado, RedirectResponse)

    def test_operacao_exception_retorna_redirect(self, mock_request):
        """Operação com exceção deve retornar RedirectResponse"""
        def operacao_com_erro():
            raise ValueError("Erro de teste")

        with patch('util.repository_helpers.informar_erro'):
            resultado = executar_operacao_repo(operacao_com_erro, mock_request)

            assert isinstance(resultado, RedirectResponse)
            assert resultado.status_code == status.HTTP_303_SEE_OTHER

    def test_operacao_exception_informa_erro(self, mock_request):
        """Deve informar erro quando operação falha"""
        def operacao_com_erro():
            raise Exception("Erro")

        mensagem = "Falha ao criar usuário"

        with patch('util.repository_helpers.informar_erro') as mock_informar:
            executar_operacao_repo(
                operacao_com_erro,
                mock_request,
                mensagem_erro=mensagem
            )

            mock_informar.assert_called_once_with(mock_request, mensagem)

    def test_operacao_exception_loga_com_exc_info(self, mock_request):
        """Deve logar exceção completa por padrão"""
        def operacao_com_erro():
            raise Exception("Erro detalhado")

        with patch('util.repository_helpers.informar_erro'):
            with patch('util.repository_helpers.logger') as mock_logger:
                executar_operacao_repo(operacao_com_erro, mock_request)

                mock_logger.error.assert_called_once()
                # Verifica que exc_info=True foi passado
                call_kwargs = mock_logger.error.call_args[1]
                assert call_kwargs.get('exc_info') is True

    def test_operacao_exception_loga_sem_exc_info(self, mock_request):
        """Não deve logar exc_info quando desabilitado"""
        def operacao_com_erro():
            raise Exception("Erro simples")

        with patch('util.repository_helpers.informar_erro'):
            with patch('util.repository_helpers.logger') as mock_logger:
                executar_operacao_repo(
                    operacao_com_erro,
                    mock_request,
                    log_exception=False
                )

                mock_logger.error.assert_called_once()
                # Verifica que não passou exc_info
                call_kwargs = mock_logger.error.call_args[1]
                assert 'exc_info' not in call_kwargs

    def test_operacao_usa_redirect_url_custom(self, mock_request):
        """Deve redirecionar para URL customizada em erro"""
        def operacao_com_erro():
            raise Exception("Erro")

        with patch('util.repository_helpers.informar_erro'):
            resultado = executar_operacao_repo(
                operacao_com_erro,
                mock_request,
                redirect_url="/admin/usuarios"
            )

            assert resultado.headers.get("location") == "/admin/usuarios"

    def test_operacao_com_diferentes_excecoes(self, mock_request):
        """Deve capturar diferentes tipos de exceção"""
        excecoes = [
            ValueError("Valor inválido"),
            TypeError("Tipo errado"),
            KeyError("Chave não encontrada"),
            RuntimeError("Erro de runtime")
        ]

        with patch('util.repository_helpers.informar_erro'):
            for exc in excecoes:
                def operacao():
                    raise exc

                resultado = executar_operacao_repo(operacao, mock_request)
                assert isinstance(resultado, RedirectResponse)
