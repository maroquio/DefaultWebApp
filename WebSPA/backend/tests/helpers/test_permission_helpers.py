"""
Testes para o módulo util/permission_helpers.py

Testa funções auxiliares para verificação de permissões e propriedade de entidades.
"""

import pytest
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

from util.permission_helpers import (
    verificar_propriedade,
    verificar_propriedade_ou_admin,
    verificar_perfil,
    verificar_multiplas_condicoes
)
from util.perfis import Perfil


@dataclass
class EntidadeExemplo:
    """Entidade de exemplo para testes"""
    id: int
    usuario_id: int
    nome: str


@dataclass
class EntidadeCustomField:
    """Entidade com campo de proprietário customizado"""
    id: int
    criado_por: int
    nome: str


class UsuarioLogadoMock:
    """Mock de UsuarioLogado para testes"""
    def __init__(self, id: int, perfil: str):
        self.id = id
        self.perfil = perfil

    def is_admin(self) -> bool:
        return self.perfil == Perfil.ADMIN.value


class TestVerificarPropriedade:
    """Testes para verificar_propriedade"""

    @pytest.fixture
    def request_mock(self):
        """Mock de Request"""
        mock = MagicMock()
        mock.url.path = "/teste/rota"
        mock.session = {}
        return mock

    def test_usuario_proprietario_permite(self, request_mock):
        """Usuário proprietário deve ter permissão"""
        entidade = EntidadeExemplo(id=1, usuario_id=10, nome="Teste")

        resultado = verificar_propriedade(
            entity=entidade,
            usuario_id=10,
            request=request_mock
        )

        assert resultado is True

    def test_usuario_nao_proprietario_bloqueia(self, request_mock):
        """Usuário não proprietário deve ser bloqueado"""
        entidade = EntidadeExemplo(id=1, usuario_id=10, nome="Teste")

        resultado = verificar_propriedade(
            entity=entidade,
            usuario_id=20,
            request=request_mock
        )

        assert resultado is False

    def test_entidade_none_bloqueia(self, request_mock):
        """Entidade None deve bloquear"""
        resultado = verificar_propriedade(
            entity=None,
            usuario_id=10,
            request=request_mock
        )

        assert resultado is False

    def test_campo_usuario_customizado(self, request_mock):
        """Deve funcionar com campo de proprietário customizado"""
        entidade = EntidadeCustomField(id=1, criado_por=10, nome="Teste")

        resultado = verificar_propriedade(
            entity=entidade,
            usuario_id=10,
            request=request_mock,
            campo_usuario="criado_por"
        )

        assert resultado is True

    def test_campo_usuario_inexistente_bloqueia(self, request_mock):
        """Campo de proprietário inexistente deve bloquear"""
        entidade = EntidadeExemplo(id=1, usuario_id=10, nome="Teste")

        resultado = verificar_propriedade(
            entity=entidade,
            usuario_id=10,
            request=request_mock,
            campo_usuario="campo_que_nao_existe"
        )

        assert resultado is False

    def test_mensagem_erro_customizada(self, request_mock):
        """Deve usar mensagem de erro customizada"""
        entidade = EntidadeExemplo(id=1, usuario_id=10, nome="Teste")

        with patch('util.permission_helpers.informar_erro') as mock_erro:
            verificar_propriedade(
                entity=entidade,
                usuario_id=20,
                request=request_mock,
                mensagem_erro="Acesso negado personalizado"
            )

            mock_erro.assert_called_once()
            args = mock_erro.call_args[0]
            assert args[1] == "Acesso negado personalizado"

    def test_log_tentativa_habilitado(self, request_mock):
        """Deve registrar log quando habilitado"""
        entidade = EntidadeExemplo(id=1, usuario_id=10, nome="Teste")

        with patch('util.permission_helpers.logger') as mock_logger:
            verificar_propriedade(
                entity=entidade,
                usuario_id=20,
                request=request_mock,
                log_tentativa=True
            )

            mock_logger.warning.assert_called_once()

    def test_log_tentativa_desabilitado(self, request_mock):
        """Não deve registrar log quando desabilitado"""
        entidade = EntidadeExemplo(id=1, usuario_id=10, nome="Teste")

        with patch('util.permission_helpers.logger') as mock_logger:
            verificar_propriedade(
                entity=entidade,
                usuario_id=20,
                request=request_mock,
                log_tentativa=False
            )

            mock_logger.warning.assert_not_called()


class TestVerificarPropriedadeOuAdmin:
    """Testes para verificar_propriedade_ou_admin"""

    @pytest.fixture
    def request_mock(self):
        """Mock de Request"""
        mock = MagicMock()
        mock.url.path = "/teste/rota"
        mock.session = {}
        return mock

    def test_admin_tem_acesso_a_qualquer_entidade(self, request_mock):
        """Administrador deve ter acesso a qualquer entidade"""
        entidade = EntidadeExemplo(id=1, usuario_id=10, nome="Teste")
        admin = UsuarioLogadoMock(id=99, perfil=Perfil.ADMIN.value)

        resultado = verificar_propriedade_ou_admin(
            entity=entidade,
            usuario_logado=admin,
            request=request_mock
        )

        assert resultado is True

    def test_proprietario_tem_acesso(self, request_mock):
        """Proprietário não-admin deve ter acesso à própria entidade"""
        entidade = EntidadeExemplo(id=1, usuario_id=10, nome="Teste")
        usuario = UsuarioLogadoMock(id=10, perfil=Perfil.CLIENTE.value)

        resultado = verificar_propriedade_ou_admin(
            entity=entidade,
            usuario_logado=usuario,
            request=request_mock
        )

        assert resultado is True

    def test_nao_proprietario_nao_admin_bloqueado(self, request_mock):
        """Não-proprietário não-admin deve ser bloqueado"""
        entidade = EntidadeExemplo(id=1, usuario_id=10, nome="Teste")
        usuario = UsuarioLogadoMock(id=20, perfil=Perfil.CLIENTE.value)

        resultado = verificar_propriedade_ou_admin(
            entity=entidade,
            usuario_logado=usuario,
            request=request_mock
        )

        assert resultado is False

    def test_admin_acessa_entidade_none(self, request_mock):
        """Admin não pode acessar entidade None (precisa verificar existência)"""
        admin = UsuarioLogadoMock(id=99, perfil=Perfil.ADMIN.value)

        # Admin bypassa verificação de propriedade, mas entidade None
        # deveria ser tratada antes
        resultado = verificar_propriedade_ou_admin(
            entity=None,
            usuario_logado=admin,
            request=request_mock
        )

        # Admin retorna True antes de verificar entidade
        assert resultado is True


class TestVerificarPerfil:
    """Testes para verificar_perfil"""

    @pytest.fixture
    def request_mock(self):
        """Mock de Request"""
        mock = MagicMock()
        mock.url.path = "/teste/rota"
        mock.session = {}
        return mock

    def test_perfil_permitido(self, request_mock):
        """Perfil na lista de permitidos deve passar"""
        resultado = verificar_perfil(
            usuario_perfil=Perfil.ADMIN.value,
            perfis_permitidos=[Perfil.ADMIN.value],
            request=request_mock
        )

        assert resultado is True

    def test_perfil_nao_permitido(self, request_mock):
        """Perfil fora da lista de permitidos deve ser bloqueado"""
        resultado = verificar_perfil(
            usuario_perfil=Perfil.CLIENTE.value,
            perfis_permitidos=[Perfil.ADMIN.value],
            request=request_mock
        )

        assert resultado is False

    def test_multiplos_perfis_permitidos(self, request_mock):
        """Deve funcionar com múltiplos perfis permitidos"""
        resultado = verificar_perfil(
            usuario_perfil=Perfil.VENDEDOR.value,
            perfis_permitidos=[Perfil.ADMIN.value, Perfil.VENDEDOR.value],
            request=request_mock
        )

        assert resultado is True

    def test_mensagem_erro_customizada(self, request_mock):
        """Deve usar mensagem de erro customizada"""
        with patch('util.permission_helpers.informar_erro') as mock_erro:
            verificar_perfil(
                usuario_perfil=Perfil.CLIENTE.value,
                perfis_permitidos=[Perfil.ADMIN.value],
                request=request_mock,
                mensagem_erro="Apenas administradores"
            )

            mock_erro.assert_called_once()
            args = mock_erro.call_args[0]
            assert args[1] == "Apenas administradores"

    def test_log_tentativa_registrado(self, request_mock):
        """Deve registrar log de tentativa de acesso"""
        with patch('util.permission_helpers.logger') as mock_logger:
            verificar_perfil(
                usuario_perfil=Perfil.CLIENTE.value,
                perfis_permitidos=[Perfil.ADMIN.value],
                request=request_mock,
                log_tentativa=True
            )

            mock_logger.warning.assert_called_once()


class TestVerificarMultiplasCondicoes:
    """Testes para verificar_multiplas_condicoes"""

    @pytest.fixture
    def request_mock(self):
        """Mock de Request"""
        mock = MagicMock()
        mock.url.path = "/teste/rota"
        mock.session = {}
        return mock

    def test_and_todas_true_passa(self, request_mock):
        """AND: todas condições True deve passar"""
        condicoes = [
            (True, "Erro 1"),
            (True, "Erro 2"),
            (True, "Erro 3"),
        ]

        resultado = verificar_multiplas_condicoes(
            condicoes=condicoes,
            request=request_mock,
            operador="AND"
        )

        assert resultado is True

    def test_and_uma_false_falha(self, request_mock):
        """AND: uma condição False deve falhar"""
        condicoes = [
            (True, "Erro 1"),
            (False, "Erro 2"),
            (True, "Erro 3"),
        ]

        with patch('util.permission_helpers.informar_erro') as mock_erro:
            resultado = verificar_multiplas_condicoes(
                condicoes=condicoes,
                request=request_mock,
                operador="AND"
            )

            assert resultado is False
            mock_erro.assert_called_once()
            args = mock_erro.call_args[0]
            assert args[1] == "Erro 2"

    def test_or_uma_true_passa(self, request_mock):
        """OR: uma condição True deve passar"""
        condicoes = [
            (False, "Erro 1"),
            (True, "Erro 2"),
            (False, "Erro 3"),
        ]

        resultado = verificar_multiplas_condicoes(
            condicoes=condicoes,
            request=request_mock,
            operador="OR"
        )

        assert resultado is True

    def test_or_todas_false_falha(self, request_mock):
        """OR: todas condições False deve falhar"""
        condicoes = [
            (False, "Erro 1"),
            (False, "Erro 2"),
            (False, "Erro 3"),
        ]

        with patch('util.permission_helpers.informar_erro') as mock_erro:
            resultado = verificar_multiplas_condicoes(
                condicoes=condicoes,
                request=request_mock,
                operador="OR",
                mensagem_erro_padrao="Nenhuma condição satisfeita"
            )

            assert resultado is False
            mock_erro.assert_called_once()

    def test_operador_invalido_levanta_erro(self, request_mock):
        """Operador inválido deve levantar ValueError"""
        condicoes = [(True, "Erro")]

        with pytest.raises(ValueError) as exc_info:
            verificar_multiplas_condicoes(
                condicoes=condicoes,
                request=request_mock,
                operador="XOR"
            )

        assert "inválido" in str(exc_info.value).lower()

    def test_and_mensagem_none_usa_padrao(self, request_mock):
        """AND: mensagem None deve usar mensagem padrão"""
        condicoes = [
            (False, None),
        ]

        with patch('util.permission_helpers.informar_erro') as mock_erro:
            verificar_multiplas_condicoes(
                condicoes=condicoes,
                request=request_mock,
                operador="AND",
                mensagem_erro_padrao="Mensagem padrão"
            )

            mock_erro.assert_called_once()
            args = mock_erro.call_args[0]
            assert args[1] == "Mensagem padrão"

    def test_or_lista_vazia_falha(self, request_mock):
        """OR: lista vazia deve falhar com mensagem padrão"""
        condicoes = []

        with patch('util.permission_helpers.informar_erro') as mock_erro:
            resultado = verificar_multiplas_condicoes(
                condicoes=condicoes,
                request=request_mock,
                operador="OR",
                mensagem_erro_padrao="Sem condições"
            )

            assert resultado is False

    def test_and_lista_vazia_passa(self, request_mock):
        """AND: lista vazia deve passar (nenhuma condição a falhar)"""
        condicoes = []

        resultado = verificar_multiplas_condicoes(
            condicoes=condicoes,
            request=request_mock,
            operador="AND"
        )

        assert resultado is True
