import os
from typing import Optional

import resend
from resend.exceptions import ResendError

from util.logger_config import logger

# Fallback alinhado ao default de DEV (.env PORT=8400). Em produção o BASE_URL
# é sempre o domínio público HTTPS, definido no deploy (ver docs/FORKING.md §2b).
BASE_URL_PADRAO = "http://localhost:8400"


class ServicoEmail:
    def __init__(self):
        self.api_key = os.getenv('RESEND_API_KEY')
        self.from_email = os.getenv('RESEND_FROM_EMAIL', 'noreply@seudominio.com')
        self.from_name = os.getenv('RESEND_FROM_NAME', 'Sistema')
        # Nome do produto exibido em assuntos/corpos (fonte: APP_NAME; cai no
        # from_name se ausente). Evita textos genéricos como "Bem-vindo ao Sistema".
        self.app_name = os.getenv('APP_NAME', self.from_name)

    def _rodape_html(self) -> str:
        """Rodapé de compliance (anti-spam / LGPD), CSS inline."""
        return (
            '<hr style="border:none;border-top:1px solid #eee;margin:24px 0">'
            '<p style="font-size:12px;color:#888">'
            f'Você recebeu este e-mail porque possui um cadastro em {self.app_name}. '
            'Este é um e-mail automático, por favor não responda.'
            '</p>'
        )

    def _rodape_texto(self) -> str:
        return (
            f'\n\n---\nVocê recebeu este e-mail porque possui um cadastro em '
            f'{self.app_name}. Este é um e-mail automático, por favor não responda.'
        )

    def enviar_email(
        self,
        para_email: str,
        para_nome: str,
        assunto: str,
        html: str,
        texto: Optional[str] = None
    ) -> bool:
        """Envia e-mail via Resend.com.

        Sempre passe `texto` com um corpo plaintext equivalente ao HTML:
        e-mail só-HTML pontua mais alto como spam. NÃO há derivação automática
        do texto a partir do HTML.
        """
        if not self.api_key:
            logger.warning("RESEND_API_KEY não configurada")
            return False

        params = {
            "from": f"{self.from_name} <{self.from_email}>",
            "to": [para_email],
            "subject": assunto,
            "html": html,
        }
        if texto:
            params["text"] = texto

        try:
            # params satisfaz SendParams em runtime; o TypedDict do resend é
            # estrito demais para o dict montado dinamicamente.
            email = resend.Emails.send(params)  # type: ignore[arg-type]
            logger.info(f"E-mail enviado para {para_email} - ID: {email.get('id', 'N/A')}")
            return True
        except ResendError as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
            return False

    def enviar_recuperacao_senha(self, para_email: str, para_nome: str, token: str) -> bool:
        """Envia e-mail de recuperação de senha"""
        url_recuperacao = f"{os.getenv('BASE_URL', BASE_URL_PADRAO)}/redefinir-senha?token={token}"

        html = f"""
        <html>
        <body>
            <h2>Recuperação de Senha</h2>
            <p>Olá {para_nome},</p>
            <p>Você solicitou a recuperação de senha em {self.app_name}.</p>
            <p>Clique no link abaixo para redefinir sua senha:</p>
            <a href="{url_recuperacao}">Redefinir Senha</a>
            <p>Ou copie e cole este endereço no navegador:<br>{url_recuperacao}</p>
            <p>Este link expira em 1 hora.</p>
            <p>Se você não solicitou esta recuperação, ignore este e-mail.</p>
            {self._rodape_html()}
        </body>
        </html>
        """

        texto = (
            f"Olá {para_nome},\n\n"
            f"Você solicitou a recuperação de senha em {self.app_name}.\n"
            f"Acesse o endereço abaixo para redefinir sua senha:\n{url_recuperacao}\n\n"
            "Este link expira em 1 hora.\n"
            "Se você não solicitou esta recuperação, ignore este e-mail."
            f"{self._rodape_texto()}"
        )

        return self.enviar_email(
            para_email=para_email,
            para_nome=para_nome,
            assunto="Recuperação de Senha",
            html=html,
            texto=texto,
        )

    def enviar_boas_vindas(self, para_email: str, para_nome: str) -> bool:
        """Envia e-mail de boas-vindas"""
        url_app = os.getenv('BASE_URL', BASE_URL_PADRAO)

        html = f"""
        <html>
        <body>
            <h2>Bem-vindo(a) ao {self.app_name}!</h2>
            <p>Olá {para_nome},</p>
            <p>Seu cadastro foi realizado com sucesso!</p>
            <p>Agora você pode acessar o sistema com seu e-mail e senha:</p>
            <a href="{url_app}">Acessar o {self.app_name}</a>
            <p>Ou copie e cole este endereço no navegador:<br>{url_app}</p>
            {self._rodape_html()}
        </body>
        </html>
        """

        texto = (
            f"Olá {para_nome},\n\n"
            f"Bem-vindo(a) ao {self.app_name}! Seu cadastro foi realizado com sucesso.\n"
            f"Acesse o sistema com seu e-mail e senha em:\n{url_app}"
            f"{self._rodape_texto()}"
        )

        return self.enviar_email(
            para_email=para_email,
            para_nome=para_nome,
            assunto=f"Bem-vindo ao {self.app_name}",
            html=html,
            texto=texto,
        )


# Instância global
servico_email = ServicoEmail()
