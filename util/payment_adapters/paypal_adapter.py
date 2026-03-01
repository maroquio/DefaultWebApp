"""
Adapter do PayPal para a interface PaymentProvider.

Usa a Orders API v2 do PayPal diretamente via HTTP com `requests`
(já presente nas dependências do projeto — sem SDK externo adicional).

Fluxo do Checkout:
    1. criar_checkout() → cria Order (CAPTURE intent), retorna approval_url
    2. Usuário aprova no PayPal
    3. PayPal redireciona para /pagamentos/paypal/capturar?pagamento_id=X&token=ORDER_ID
    4. capturar_ordem() confirma e captura o pagamento na API
    5. Usuário é redirecionado para /pagamentos/sucesso ou /pagamentos/falha

Credenciais no banco/config_cache:
    - paypal_client_id:     Client ID do app PayPal Developer
    - paypal_client_secret: Client Secret do app PayPal Developer
    - paypal_webhook_id:    ID do webhook cadastrado (para verificação de assinatura)

Ambientes:
    - IS_DEVELOPMENT=True  → sandbox (api-m.sandbox.paypal.com)
    - IS_DEVELOPMENT=False → produção (api-m.paypal.com)

Referência:
    https://developer.paypal.com/docs/api/orders/v2/
    https://developer.paypal.com/docs/api/webhooks/v1/
"""

from typing import Optional

from util.logger_config import logger
from util.payment_provider import PaymentProvider


class PayPalAdapter(PaymentProvider):
    """Adapter que integra o PayPal Checkout via Orders API v2."""

    SANDBOX_URL = "https://api-m.sandbox.paypal.com"
    LIVE_URL = "https://api-m.paypal.com"

    @property
    def chave(self) -> str:
        return "paypal"

    @property
    def nome(self) -> str:
        return "PayPal"

    def _base_url(self) -> str:
        """Retorna a URL base da API conforme o modo de execução."""
        from util.config import IS_DEVELOPMENT
        return self.SANDBOX_URL if IS_DEVELOPMENT else self.LIVE_URL

    def _obter_access_token(self) -> str:
        """
        Obtém access token via OAuth2 client_credentials.

        Returns:
            Access token válido para autenticar chamadas à API.

        Raises:
            ValueError: Se as credenciais não estiverem configuradas.
            requests.HTTPError: Se a API retornar erro.
        """
        import requests
        from util.config_cache import config

        client_id = config.obter("paypal_client_id", "")
        client_secret = config.obter("paypal_client_secret", "")

        if not client_id or not client_secret:
            raise ValueError("Credenciais PayPal não configuradas (paypal_client_id / paypal_client_secret)")

        response = requests.post(
            f"{self._base_url()}/v1/oauth2/token",
            headers={"Accept": "application/json", "Accept-Language": "en_US"},
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def _headers(self) -> dict:
        """Retorna headers autenticados para chamadas à API."""
        return {
            "Authorization": f"Bearer {self._obter_access_token()}",
            "Content-Type": "application/json",
        }

    def criar_checkout(
        self,
        descricao: str,
        valor: float,
        pagamento_id: int,
        back_urls: dict,
        webhook_url: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Cria uma Order no PayPal com CAPTURE intent e retorna a approval_url.

        O usuário é redirecionado para a approval_url onde aprova o pagamento.
        Após aprovação, o PayPal redireciona para /pagamentos/paypal/capturar.

        Args:
            descricao: Descrição exibida no checkout (máx 127 chars no PayPal)
            valor: Valor em reais
            pagamento_id: ID local usado como reference_id da purchase_unit
            back_urls: Dict com "success"/"failure" — PayPal usa application_context
            webhook_url: Não usado diretamente (PayPal usa webhooks cadastrados)

        Returns:
            {"reference_id": order_id, "checkout_url": approval_url} ou None
        """
        import requests
        from util.config import BASE_URL
        from util.config_cache import config

        try:
            response = requests.post(
                f"{self._base_url()}/v2/checkout/orders",
                headers=self._headers(),
                json={
                    "intent": "CAPTURE",
                    "purchase_units": [
                        {
                            "reference_id": str(pagamento_id),
                            "amount": {
                                "currency_code": "BRL",
                                "value": f"{valor:.2f}",
                            },
                            "description": descricao[:127],
                        }
                    ],
                    "application_context": {
                        "brand_name": config.obter("app_name", "Sistema"),
                        "locale": "pt-BR",
                        "landing_page": "LOGIN",
                        "user_action": "PAY_NOW",
                        "return_url": (
                            f"{BASE_URL}/pagamentos/paypal/capturar"
                            f"?pagamento_id={pagamento_id}"
                        ),
                        "cancel_url": f"{BASE_URL}/pagamentos/falha?pagamento_id={pagamento_id}",
                    },
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            order_id = data["id"]
            approval_url = next(
                (link["href"] for link in data.get("links", []) if link["rel"] == "approve"),
                None,
            )

            if not approval_url:
                logger.error(f"PayPal: approval_url não encontrada na resposta: {data}")
                return None

            logger.info(f"PayPal Order criado: id={order_id}, pagamento_id={pagamento_id}")

            return {
                "reference_id": order_id,
                "checkout_url": approval_url,
            }

        except Exception as e:
            logger.error(f"Erro ao criar PayPal Order: {e}", exc_info=True)
            return None

    def capturar_ordem(self, order_id: str) -> Optional[dict]:
        """
        Captura uma Order aprovada pelo usuário.

        Deve ser chamado APÓS o usuário aprovar o pagamento no PayPal.
        Sem esta chamada, o dinheiro não é transferido — a aprovação apenas
        autoriza, a captura efetiva a cobrança.

        Args:
            order_id: ID da Order PayPal (recebido como `token` na return URL)

        Returns:
            Dict com order_id, capture_id, status, valor_pago. Ou None se erro.
        """
        import requests

        try:
            response = requests.post(
                f"{self._base_url()}/v2/checkout/orders/{order_id}/capture",
                headers=self._headers(),
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            status_paypal = data.get("status")
            purchase_unit = (data.get("purchase_units") or [{}])[0]
            captures = purchase_unit.get("payments", {}).get("captures") or [{}]
            capture = captures[0]

            logger.info(f"PayPal Order capturado: id={order_id}, status={status_paypal}")

            return {
                "order_id": order_id,
                "capture_id": capture.get("id"),
                "status": status_paypal,
                "valor_pago": float(capture.get("amount", {}).get("value", 0) or 0),
                "dados_brutos": data,
            }

        except Exception as e:
            logger.error(f"Erro ao capturar PayPal Order {order_id}: {e}", exc_info=True)
            return None

    def obter_dados_pagamento(self, provider_payment_id: str) -> Optional[dict]:
        """
        Consulta dados de uma Order PayPal pelo order_id.

        Args:
            provider_payment_id: ID da Order PayPal (armazenado em payment_id)

        Returns:
            Dict normalizado com status, valor_pago, email_pagador, data_aprovacao.
        """
        import requests

        try:
            response = requests.get(
                f"{self._base_url()}/v2/checkout/orders/{provider_payment_id}",
                headers=self._headers(),
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            purchase_unit = (data.get("purchase_units") or [{}])[0]
            captures = purchase_unit.get("payments", {}).get("captures") or [{}]
            capture = captures[0]
            payer = data.get("payer") or {}

            valor_pago = None
            if capture.get("amount"):
                valor_pago = float(capture["amount"].get("value", 0) or 0)

            data_aprovacao = capture.get("create_time") or data.get("create_time")

            return {
                "status": data.get("status"),
                "valor_pago": valor_pago,
                "email_pagador": payer.get("email_address"),
                "data_aprovacao": data_aprovacao,
                "dados_brutos": data,
            }

        except Exception as e:
            logger.error(
                f"Erro ao consultar PayPal Order {provider_payment_id}: {e}", exc_info=True
            )
            return None

    def processar_webhook(
        self, payload: bytes, headers: dict
    ) -> Optional[dict]:
        """
        Valida assinatura e processa evento de webhook do PayPal.

        Se PAYPAL_WEBHOOK_ID estiver configurado, verifica a assinatura
        chamando o endpoint de verificação da API do PayPal.

        Mapeamento de eventos:
            PAYMENT.CAPTURE.COMPLETED → Aprovado
            PAYMENT.CAPTURE.DENIED    → Recusado
            PAYMENT.CAPTURE.REFUNDED  → Reembolsado
            CHECKOUT.ORDER.COMPLETED  → Aprovado

        Args:
            payload: Corpo raw da requisição POST
            headers: Headers HTTP — devem conter paypal-transmission-* para verificação

        Returns:
            Dict com provider_payment_id, reference_id, status, pagamento_id.
            Ou None se deve ser ignorado.
        """
        import json
        import requests
        from util.config_cache import config

        try:
            event_data = json.loads(payload)
        except Exception as e:
            logger.error(f"PayPal webhook: payload JSON inválido: {e}")
            return None

        # Verificar assinatura se webhook_id configurado
        webhook_id = config.obter("paypal_webhook_id", "")
        if webhook_id:
            try:
                verify_response = requests.post(
                    f"{self._base_url()}/v1/notifications/verify-webhook-signature",
                    headers=self._headers(),
                    json={
                        "auth_algo": headers.get("paypal-auth-algo", ""),
                        "cert_url": headers.get("paypal-cert-url", ""),
                        "transmission_id": headers.get("paypal-transmission-id", ""),
                        "transmission_sig": headers.get("paypal-transmission-sig", ""),
                        "transmission_time": headers.get("paypal-transmission-time", ""),
                        "webhook_id": webhook_id,
                        "webhook_event": event_data,
                    },
                    timeout=10,
                )
                result = verify_response.json()
                if result.get("verification_status") != "SUCCESS":
                    logger.warning(f"PayPal webhook: assinatura inválida: {result}")
                    return None
            except Exception as e:
                logger.warning(f"PayPal webhook: falha na verificação de assinatura: {e}")
                from util.config import IS_DEVELOPMENT
                if not IS_DEVELOPMENT:
                    return None

        event_type = event_data.get("event_type", "")
        logger.info(f"PayPal webhook recebido: event_type={event_type}")

        # Mapeamento de eventos PayPal → StatusPagamento
        mapa_status = {
            "PAYMENT.CAPTURE.COMPLETED": "Aprovado",
            "PAYMENT.CAPTURE.DENIED": "Recusado",
            "PAYMENT.CAPTURE.REFUNDED": "Reembolsado",
            "PAYMENT.CAPTURE.REVERSED": "Reembolsado",
            "CHECKOUT.ORDER.COMPLETED": "Aprovado",
            "PAYMENT.SALE.COMPLETED": "Aprovado",
            "PAYMENT.SALE.REFUNDED": "Reembolsado",
        }

        if event_type not in mapa_status:
            logger.debug(f"PayPal webhook ignorado: event_type={event_type} não mapeado")
            return None

        status_sistema = mapa_status[event_type]
        resource = event_data.get("resource", {})

        # Extrair IDs do recurso
        capture_id = resource.get("id") if "CAPTURE" in event_type else None
        order_id = (
            resource.get("supplementary_data", {}).get("related_ids", {}).get("order_id")
            or (resource.get("id") if "ORDER" in event_type else None)
        )

        # Extrair pagamento_id via reference_id da purchase_unit (se disponível)
        pagamento_id = None
        for unit in resource.get("purchase_units", []):
            ref = unit.get("reference_id", "")
            if ref and str(ref).isdigit():
                pagamento_id = int(ref)
                break

        logger.info(
            f"PayPal webhook processado: event={event_type}, "
            f"order_id={order_id}, capture_id={capture_id}, pagamento_id={pagamento_id}"
        )

        return {
            "provider_payment_id": capture_id or order_id,
            "reference_id": order_id,
            "status": status_sistema,
            "pagamento_id": pagamento_id,
        }
