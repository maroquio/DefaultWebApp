"""
Interface abstrata para provedores de pagamento.

Define o contrato que todos os adapters de pagamento devem implementar,
permitindo trocar de provedor (Mercado Pago, Stripe, etc.) sem alterar
a lógica de negócio nas rotas.

Padrão usado: Strategy + Factory
  - PaymentProvider: define a interface (Strategy)
  - PaymentService: seleciona o adapter correto (Factory)
  - MercadoPagoAdapter / StripeAdapter: implementações concretas
"""

from abc import ABC, abstractmethod
from typing import Optional


class PaymentProvider(ABC):
    """
    Interface abstrata para integrações com gateways de pagamento.

    Todos os adapters devem implementar estes métodos para garantir
    que as rotas funcionem independentemente do provedor ativo.
    """

    @property
    @abstractmethod
    def chave(self) -> str:
        """
        Identificador único do provedor (slug).

        Usado para persistir no banco junto ao pagamento.
        Ex: 'mercadopago', 'stripe'
        """

    @property
    @abstractmethod
    def nome(self) -> str:
        """
        Nome legível do provedor para exibição na UI.

        Ex: 'Mercado Pago', 'Stripe'
        """

    @abstractmethod
    def criar_checkout(
        self,
        descricao: str,
        valor: float,
        pagamento_id: int,
        back_urls: dict,
        webhook_url: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Cria uma sessão/preferência de checkout no provedor.

        Args:
            descricao: Descrição do produto/serviço
            valor: Valor em reais (float, ex: 29.90)
            pagamento_id: ID do pagamento no banco local (usado como referência)
            back_urls: Dict com URLs de retorno:
                {"success": "...", "pending": "...", "failure": "..."}
            webhook_url: URL do endpoint de webhook (opcional)

        Returns:
            Dict com:
                - reference_id: ID da sessão/preferência no provedor
                - checkout_url: URL para redirecionar o usuário ao checkout
            Ou None se ocorrer erro.
        """

    @abstractmethod
    def obter_dados_pagamento(self, provider_payment_id: str) -> Optional[dict]:
        """
        Consulta os dados de um pagamento confirmado no provedor.

        Usado na página de detalhes do admin para exibir dados em tempo real.

        Args:
            provider_payment_id: ID do pagamento no provedor (payment_id do banco)

        Returns:
            Dict normalizado com:
                - status: Status atual no provedor
                - valor_pago: Valor efetivamente pago
                - email_pagador: Email de quem pagou
                - data_aprovacao: Data/hora da aprovação
                - dados_brutos: Dict completo retornado pelo provedor
            Ou None se ocorrer erro.
        """

    @abstractmethod
    def processar_webhook(
        self, payload: bytes, headers: dict
    ) -> Optional[dict]:
        """
        Valida e processa uma notificação de webhook do provedor.

        Args:
            payload: Corpo raw da requisição POST (bytes)
            headers: Headers HTTP da requisição

        Returns:
            Dict normalizado com:
                - provider_payment_id: ID do pagamento no provedor
                - reference_id: ID da sessão/preferência no provedor
                - status: Status traduzido para StatusPagamento (ex: 'Aprovado')
                - pagamento_id: ID do pagamento no banco local (se disponível)
            Ou None se o payload deve ser ignorado.
        """
