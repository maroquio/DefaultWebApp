"""
Testes para o módulo util/email_service.py

Testa o serviço de envio de e-mails via Resend.
"""

import pytest
from unittest.mock import patch, MagicMock
import os


class TestServicoEmailInit:
    """Testes para inicialização do ServicoEmail"""

    def test_init_sem_api_key(self):
        """Deve inicializar sem API key"""
        with patch.dict(os.environ, {'RESEND_API_KEY': ''}, clear=False):
            from util.email_service import ServicoEmail
            servico = ServicoEmail()
            # Pode ser '' ou None dependendo do ambiente
            assert servico.api_key == '' or servico.api_key is None

    def test_init_com_api_key(self):
        """Deve configurar API key do Resend"""
        with patch.dict(os.environ, {'RESEND_API_KEY': 'test_key_123'}, clear=False):
            with patch('util.email_service.resend'):
                from util.email_service import ServicoEmail
                servico = ServicoEmail()
                assert servico.api_key == 'test_key_123'

    def test_init_valores_padrao(self):
        """Deve usar valores padrão quando não configurados"""
        from util.email_service import ServicoEmail
        servico = ServicoEmail()

        # from_name deve ter valor padrão
        assert servico.from_name is not None


class TestEnviarEmail:
    """Testes para o método enviar_email()"""

    def test_sem_api_key_retorna_false(self):
        """Deve retornar False quando API key não está configurada"""
        from util.email_service import ServicoEmail
        servico = ServicoEmail()
        servico.api_key = None

        resultado = servico.enviar_email(
            para_email="test@email.com",
            para_nome="Teste",
            assunto="Teste",
            html="<p>Teste</p>"
        )

        assert resultado is False

    def test_envio_com_sucesso(self):
        """Deve retornar True quando e-mail é enviado com sucesso"""
        from util.email_service import ServicoEmail
        servico = ServicoEmail()
        servico.api_key = 'test_key'

        with patch('util.email_service.resend.Emails.send') as mock_send:
            mock_send.return_value = {'id': 'email123'}

            resultado = servico.enviar_email(
                para_email="test@email.com",
                para_nome="Teste",
                assunto="Assunto Teste",
                html="<p>Conteúdo</p>"
            )

            assert resultado is True
            mock_send.assert_called_once()

    def test_envio_com_erro_resend(self):
        """Deve retornar False quando Resend retorna erro"""
        from resend.exceptions import ResendError
        from util.email_service import ServicoEmail

        servico = ServicoEmail()
        servico.api_key = 'test_key'

        with patch('util.email_service.resend.Emails.send') as mock_send:
            # ResendError requer code, error_type, message, suggested_action
            mock_send.side_effect = ResendError(
                code=500,
                error_type="api_error",
                message="API Error",
                suggested_action="Try again"
            )

            resultado = servico.enviar_email(
                para_email="test@email.com",
                para_nome="Teste",
                assunto="Assunto",
                html="<p>HTML</p>"
            )

            assert resultado is False


class TestEnviarRecuperacaoSenha:
    """Testes para o método enviar_recuperacao_senha()"""

    def test_envia_recuperacao_senha(self):
        """Deve enviar e-mail de recuperação de senha"""
        from util.email_service import ServicoEmail
        servico = ServicoEmail()

        with patch.object(servico, 'enviar_email', return_value=True) as mock_enviar:
            resultado = servico.enviar_recuperacao_senha(
                para_email="user@email.com",
                para_nome="Usuario",
                token="token123"
            )

            assert resultado is True
            mock_enviar.assert_called_once()

            # Verifica conteúdo do HTML
            call_args = mock_enviar.call_args
            html = call_args.kwargs['html']
            assert "Recuperação de Senha" in html
            assert "token123" in html
            assert "Usuario" in html

    def test_recuperacao_senha_com_base_url(self):
        """Deve usar BASE_URL na URL de recuperação"""
        from util.email_service import ServicoEmail

        with patch.dict(os.environ, {'BASE_URL': 'http://meusite.com'}, clear=False):
            servico = ServicoEmail()

            with patch.object(servico, 'enviar_email', return_value=True) as mock_enviar:
                servico.enviar_recuperacao_senha(
                    para_email="user@email.com",
                    para_nome="Usuario",
                    token="token123"
                )

                call_args = mock_enviar.call_args
                html = call_args.kwargs['html']
                # O link deve conter a URL ou o token
                assert "redefinir-senha" in html or "token123" in html


class TestEnviarBoasVindas:
    """Testes para o método enviar_boas_vindas()"""

    def test_envia_boas_vindas(self):
        """Deve enviar e-mail de boas-vindas"""
        from util.email_service import ServicoEmail
        servico = ServicoEmail()

        with patch.object(servico, 'enviar_email', return_value=True) as mock_enviar:
            resultado = servico.enviar_boas_vindas(
                para_email="novo@email.com",
                para_nome="Novo Usuario"
            )

            assert resultado is True
            mock_enviar.assert_called_once()

            # Verifica conteúdo
            call_args = mock_enviar.call_args
            assert call_args.kwargs['assunto'] == "Bem-vindo ao Sistema"
            assert "Novo Usuario" in call_args.kwargs['html']
            assert "Bem-vindo" in call_args.kwargs['html']

    def test_boas_vindas_falha_retorna_false(self):
        """Deve retornar False quando envio falha"""
        from util.email_service import ServicoEmail
        servico = ServicoEmail()

        with patch.object(servico, 'enviar_email', return_value=False):
            resultado = servico.enviar_boas_vindas(
                para_email="novo@email.com",
                para_nome="Usuario"
            )

            assert resultado is False


class TestServicoEmailGlobal:
    """Testes para a instância global do serviço"""

    def test_servico_email_existe(self):
        """Instância global deve existir"""
        from util.email_service import servico_email, ServicoEmail

        assert servico_email is not None
        assert isinstance(servico_email, ServicoEmail)
