import os
from typing import Optional

import resend
from resend.exceptions import ResendError

from util.logger_config import logger


class ServicoEmail:
    def __init__(self):
        self.api_key = os.getenv('RESEND_API_KEY')
        self.from_email = os.getenv('RESEND_FROM_EMAIL', 'noreply@seudominio.com')
        self.from_name = os.getenv('RESEND_FROM_NAME', 'Sistema')

        # Configura a API key do Resend
        if self.api_key:
            resend.api_key = self.api_key

    def enviar_email(
        self,
        para_email: str,
        para_nome: str,
        assunto: str,
        html: str,
        texto: Optional[str] = None
    ) -> bool:
        """Envia e-mail via Resend.com"""
        if not self.api_key:
            logger.warning("RESEND_API_KEY não configurada")
            return False

        params = {
            "from": f"{self.from_name} <{self.from_email}>",
            "to": [para_email],
            "subject": assunto,
            "html": html
        }

        try:
            email = resend.Emails.send(params)
            logger.info(f"E-mail enviado para {para_email} - ID: {email.get('id', 'N/A')}")
            return True
        except ResendError as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
            return False

    def enviar_recuperacao_senha(self, para_email: str, para_nome: str, token: str) -> bool:
        """Envia e-mail de recuperação de senha"""
        url_recuperacao = f"{os.getenv('BASE_URL', 'http://localhost:8000')}/redefinir-senha?token={token}"

        html = f"""
        <html>
        <body>
            <h2>Recuperação de Senha</h2>
            <p>Olá {para_nome},</p>
            <p>Você solicitou a recuperação de senha.</p>
            <p>Clique no link abaixo para redefinir sua senha:</p>
            <a href="{url_recuperacao}">Redefinir Senha</a>
            <p>Este link expira em 1 hora.</p>
            <p>Se você não solicitou esta recuperação, ignore este e-mail.</p>
        </body>
        </html>
        """

        return self.enviar_email(
            para_email=para_email,
            para_nome=para_nome,
            assunto="Recuperação de Senha",
            html=html
        )

    def enviar_boas_vindas(self, para_email: str, para_nome: str) -> bool:
        """Envia e-mail de boas-vindas"""
        html = f"""
        <html>
        <body>
            <h2>Bem-vindo(a)!</h2>
            <p>Olá {para_nome},</p>
            <p>Seu cadastro foi realizado com sucesso!</p>
            <p>Agora você pode acessar o sistema com seu e-mail e senha.</p>
        </body>
        </html>
        """

        return self.enviar_email(
            para_email=para_email,
            para_nome=para_nome,
            assunto="Bem-vindo ao Sistema",
            html=html
        )


# Instância global
servico_email = ServicoEmail()
