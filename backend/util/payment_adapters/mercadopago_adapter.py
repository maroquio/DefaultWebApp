"""
Adapter do Mercado Pago para a interface PaymentProvider.

Encapsula mercadopago_util.py (mantido inalterado) e adapta seus retornos
ao contrato da interface PaymentProvider.

Credenciais lidas do config_cache (banco de dados), com fallback para config.py.
"""

from typing import Optional

from util.logger_config import logger
from util.payment_provider import PaymentProvider


class MercadoPagoAdapter(PaymentProvider):
    """Adapter que integra o Mercado Pago Checkout Pro."""

    @property
    def chave(self) -> str:
        return "mercadopago"

    @property
    def nome(self) -> str:
        return "Mercado Pago"

    def criar_checkout(
        self,
        descricao: str,
        valor: float,
        pagamento_id: int,
        back_urls: dict,
        webhook_url: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Cria preferência no Mercado Pago e retorna reference_id e checkout_url.

        Em desenvolvimento usa sandbox_init_point; em produção usa init_point.

        Returns:
            {"reference_id": preference_id, "checkout_url": init_point} ou None
        """
        from util.config import IS_DEVELOPMENT
        from util.mercadopago_util import criar_preferencia

        resultado = criar_preferencia(
            descricao=descricao,
            valor=valor,
            pagamento_id=pagamento_id,
            back_urls=back_urls,
            webhook_url=webhook_url,
        )

        if not resultado:
            return None

        checkout_url = (
            resultado["sandbox_init_point"] if IS_DEVELOPMENT else resultado["init_point"]
        )

        return {
            "reference_id": resultado["preference_id"],
            "checkout_url": checkout_url,
        }

    def obter_dados_pagamento(self, provider_payment_id: str) -> Optional[dict]:
        """
        Consulta dados do pagamento na API do Mercado Pago.

        Returns:
            Dict normalizado com status, valor_pago, email_pagador, data_aprovacao,
            dados_brutos. Ou None se erro.
        """
        from util.mercadopago_util import obter_pagamento_mp

        dados_mp = obter_pagamento_mp(provider_payment_id)
        if not dados_mp:
            return None

        payer = dados_mp.get("payer") or {}

        return {
            "status": dados_mp.get("status"),
            "valor_pago": dados_mp.get("transaction_amount"),
            "email_pagador": payer.get("email"),
            "data_aprovacao": dados_mp.get("date_approved"),
            "dados_brutos": dados_mp,
        }

    def processar_webhook(
        self, payload: bytes, headers: dict
    ) -> Optional[dict]:
        """
        Processa notificação IPN do Mercado Pago.

        O payload pode ser JSON (IPN v2) ou query string (IPN legacy).

        Returns:
            Dict com provider_payment_id, reference_id, status, pagamento_id.
            Ou None se deve ser ignorado.
        """
        import json

        # Tentar parsear como JSON
        try:
            dados = json.loads(payload)
        except Exception:
            # Fallback: payload como string de query params
            from urllib.parse import parse_qs
            qs = parse_qs(payload.decode("utf-8", errors="replace"))
            dados = {k: v[0] if len(v) == 1 else v for k, v in qs.items()}

        from util.mercadopago_util import processar_webhook as mp_processar_webhook

        resultado_mp = mp_processar_webhook(dados)
        if not resultado_mp:
            return None

        external_ref = resultado_mp.get("external_reference", "")

        return {
            "provider_payment_id": resultado_mp.get("payment_id"),
            "reference_id": None,
            "status": resultado_mp.get("status"),
            "pagamento_id": int(external_ref) if external_ref and external_ref.isdigit() else None,
        }
