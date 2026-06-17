"""
Adapter do Stripe para a interface PaymentProvider.

Implementa Checkout Sessions do Stripe para criar sessões de pagamento,
processar webhooks com validação de assinatura e consultar dados de pagamentos.

Credenciais lidas do config_cache:
  - STRIPE_SECRET_KEY: chave secreta para autenticar chamadas à API
  - STRIPE_PUBLIC_KEY: chave pública para o frontend (Stripe.js)
  - STRIPE_WEBHOOK_SECRET: secret para validar assinatura dos webhooks

Referência:
  https://stripe.com/docs/checkout/quickstart
  https://stripe.com/docs/webhooks
"""

from typing import Optional

from util.logger_config import logger
from util.payment_provider import PaymentProvider


# Mapeamento de eventos Stripe → StatusPagamento do sistema
# TODO (contribuição do usuário): Revise e ajuste este mapeamento conforme
# a lógica de negócio da sua aplicação. Considere:
#   - checkout.session.completed pode indicar pagamento imediato (APROVADO)
#     ou apenas a conclusão da sessão com pagamento assíncrono (EM_PROCESSAMENTO)
#   - charge.refunded deve gerar REEMBOLSADO
#   - payment_intent.payment_failed deve gerar RECUSADO
MAPA_STATUS_STRIPE = {
    "checkout.session.completed": "Aprovado",
    "checkout.session.async_payment_succeeded": "Aprovado",
    "checkout.session.async_payment_failed": "Recusado",
    "charge.refunded": "Reembolsado",
    "payment_intent.payment_failed": "Recusado",
    "payment_intent.canceled": "Cancelado",
}


class StripeAdapter(PaymentProvider):
    """Adapter que integra o Stripe Checkout Sessions."""

    @property
    def chave(self) -> str:
        return "stripe"

    @property
    def nome(self) -> str:
        return "Stripe"

    def _obter_stripe(self):
        """Retorna módulo stripe configurado com a chave secreta do config_cache."""
        import stripe
        from util.config_cache import config

        stripe.api_key = config.obter("stripe_secret_key", "")
        return stripe

    def criar_checkout(
        self,
        descricao: str,
        valor: float,
        pagamento_id: int,
        back_urls: dict,
        webhook_url: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Cria uma Checkout Session no Stripe.

        O valor é convertido de reais (float) para centavos (int) — o Stripe
        trabalha sempre com a menor unidade monetária.

        Args:
            descricao: Nome do produto exibido no checkout
            valor: Valor em reais (ex: 29.90 → 2990 centavos)
            pagamento_id: ID local usado como client_reference_id
            back_urls: {"success": "...", "failure": "..."} — "pending" ignorado
            webhook_url: Não usado diretamente (Stripe usa dashboard/CLI)

        Returns:
            {"reference_id": session.id, "checkout_url": session.url} ou None
        """
        stripe = self._obter_stripe()
        from util.config import BASE_URL

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "brl",
                            "unit_amount": int(round(valor * 100)),
                            "product_data": {"name": descricao},
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                client_reference_id=str(pagamento_id),
                success_url=(
                    f"{BASE_URL}/pagamentos/sucesso"
                    f"?pagamento_id={pagamento_id}&session_id={{CHECKOUT_SESSION_ID}}"
                ),
                cancel_url=f"{BASE_URL}/pagamentos/falha?pagamento_id={pagamento_id}",
            )

            logger.info(
                f"Stripe Checkout Session criada: id={session.id}, "
                f"pagamento_id={pagamento_id}"
            )

            return {
                "reference_id": session.id,
                "checkout_url": session.url,
            }

        except Exception as e:
            logger.error(f"Erro ao criar Stripe Checkout Session: {e}", exc_info=True)
            return None

    def obter_dados_pagamento(self, provider_payment_id: str) -> Optional[dict]:
        """
        Consulta dados de uma Checkout Session ou PaymentIntent no Stripe.

        O provider_payment_id pode ser um session.id (cs_...) ou payment_intent.id (pi_...).

        Returns:
            Dict normalizado com status, valor_pago, email_pagador, data_aprovacao,
            dados_brutos. Ou None se erro.
        """
        stripe = self._obter_stripe()

        try:
            if provider_payment_id.startswith("cs_"):
                # Checkout Session
                session = stripe.checkout.Session.retrieve(
                    provider_payment_id,
                    expand=["payment_intent", "payment_intent.latest_charge"],
                )
                payment_intent = session.payment_intent
                email_pagador = session.customer_details.email if session.customer_details else None
                valor_pago = session.amount_total / 100.0 if session.amount_total else None

                # Data de aprovação via charge
                data_aprovacao = None
                if payment_intent and hasattr(payment_intent, "latest_charge"):
                    charge = payment_intent.latest_charge
                    if charge and charge.created:
                        from datetime import datetime, timezone
                        data_aprovacao = datetime.fromtimestamp(
                            charge.created, tz=timezone.utc
                        ).isoformat()

                return {
                    "status": session.payment_status,
                    "valor_pago": valor_pago,
                    "email_pagador": email_pagador,
                    "data_aprovacao": data_aprovacao,
                    "dados_brutos": dict(session),
                }

            elif provider_payment_id.startswith("pi_"):
                # PaymentIntent direto
                pi = stripe.PaymentIntent.retrieve(
                    provider_payment_id,
                    expand=["latest_charge"],
                )
                charge = pi.latest_charge if hasattr(pi, "latest_charge") else None
                email_pagador = charge.billing_details.email if charge and charge.billing_details else None
                valor_pago = pi.amount / 100.0 if pi.amount else None

                data_aprovacao = None
                if charge and charge.created:
                    from datetime import datetime, timezone
                    data_aprovacao = datetime.fromtimestamp(
                        charge.created, tz=timezone.utc
                    ).isoformat()

                return {
                    "status": pi.status,
                    "valor_pago": valor_pago,
                    "email_pagador": email_pagador,
                    "data_aprovacao": data_aprovacao,
                    "dados_brutos": dict(pi),
                }

            else:
                logger.warning(f"Stripe: provider_payment_id com formato desconhecido: {provider_payment_id}")
                return None

        except Exception as e:
            logger.error(
                f"Erro ao consultar Stripe id={provider_payment_id}: {e}", exc_info=True
            )
            return None

    def processar_webhook(
        self, payload: bytes, headers: dict
    ) -> Optional[dict]:
        """
        Valida assinatura e processa evento do webhook Stripe.

        A assinatura é validada com STRIPE_WEBHOOK_SECRET para garantir
        que a requisição veio realmente do Stripe (não de terceiros).

        TODO (contribuição do usuário): Implemente aqui a lógica de mapeamento
        de eventos Stripe → StatusPagamento conforme sua regra de negócio.
        O esqueleto abaixo processa os eventos mais comuns, mas você pode
        adicionar/remover eventos em MAPA_STATUS_STRIPE no topo do arquivo.

        Considere:
          - checkout.session.completed: indica sessão finalizada. Para pagamentos
            síncronos (cartão), significa aprovação imediata. Para PIX/boleto,
            pode precisar aguardar checkout.session.async_payment_succeeded.
          - Para pagamentos com 3D Secure, o fluxo pode ter mais etapas.

        Args:
            payload: Corpo raw da requisição (bytes)
            headers: Headers HTTP — deve conter "stripe-signature"

        Returns:
            Dict com provider_payment_id, reference_id, status, pagamento_id.
            Ou None se deve ser ignorado.
        """
        stripe = self._obter_stripe()
        from util.config_cache import config

        webhook_secret = config.obter("stripe_webhook_secret", "")
        if not webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET não configurado — pulando validação de assinatura")

        # Validar assinatura do webhook
        try:
            sig_header = headers.get("stripe-signature", "")
            if webhook_secret:
                event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            else:
                import json
                event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)

        except Exception as e:
            logger.error(f"Stripe webhook: assinatura inválida ou payload malformado: {e}")
            return None

        event_type = event.get("type", "")
        logger.info(f"Stripe webhook recebido: type={event_type}")

        # Verificar se é um evento que nos interessa
        if event_type not in MAPA_STATUS_STRIPE:
            logger.debug(f"Stripe webhook ignorado: type={event_type} não mapeado")
            return None

        status_sistema = MAPA_STATUS_STRIPE[event_type]

        # Extrair dados do objeto do evento
        data_object = event.get("data", {}).get("object", {})

        # Identificar o pagamento local via client_reference_id (Checkout Sessions)
        pagamento_id = None
        reference_id = None
        provider_payment_id = None

        if event_type.startswith("checkout.session"):
            reference_id = data_object.get("id")
            provider_payment_id = data_object.get("payment_intent") or reference_id
            client_ref = data_object.get("client_reference_id", "")
            if client_ref and client_ref.isdigit():
                pagamento_id = int(client_ref)

        elif event_type.startswith("charge"):
            provider_payment_id = data_object.get("payment_intent") or data_object.get("id")
            # Para charges, o pagamento_id pode estar nos metadados
            metadata = data_object.get("metadata") or {}
            ref = metadata.get("pagamento_id", "")
            if ref and str(ref).isdigit():
                pagamento_id = int(ref)

        elif event_type.startswith("payment_intent"):
            provider_payment_id = data_object.get("id")
            metadata = data_object.get("metadata") or {}
            ref = metadata.get("pagamento_id", "")
            if ref and str(ref).isdigit():
                pagamento_id = int(ref)

        logger.info(
            f"Stripe webhook processado: event={event_type}, "
            f"provider_payment_id={provider_payment_id}, "
            f"pagamento_id={pagamento_id}, status={status_sistema}"
        )

        return {
            "provider_payment_id": provider_payment_id,
            "reference_id": reference_id,
            "status": status_sistema,
            "pagamento_id": pagamento_id,
        }
