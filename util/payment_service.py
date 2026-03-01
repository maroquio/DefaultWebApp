"""
Factory de provedores de pagamento.

Lê a configuração PAYMENT_PROVIDER do config_cache (banco de dados) e
retorna a instância correta do adapter. Alterações no painel admin entram
em vigor imediatamente na próxima chamada — sem reiniciar o servidor.

Uso:
    from util.payment_service import PaymentService

    provider = PaymentService.obter_provider()
    resultado = provider.criar_checkout(descricao, valor, pagamento_id, back_urls)
"""

from util.payment_provider import PaymentProvider


class PaymentService:
    """
    Factory que seleciona o PaymentProvider correto com base na configuração ativa.

    Não mantém estado — cada chamada a obter_provider() lê o config_cache,
    garantindo que mudanças no painel admin sejam aplicadas imediatamente.
    """

    @classmethod
    def obter_provider(cls) -> PaymentProvider:
        """
        Retorna o adapter do provedor configurado em PAYMENT_PROVIDER.

        Configuração lida do banco de dados via config_cache. Se não configurado,
        usa 'mercadopago' como padrão para compatibilidade retroativa.

        Returns:
            Instância de MercadoPagoAdapter ou StripeAdapter
        """
        from util.config_cache import config

        chave = config.obter("payment_provider", "mercadopago").lower().strip()

        if chave == "stripe":
            from util.payment_adapters.stripe_adapter import StripeAdapter
            return StripeAdapter()

        if chave == "paypal":
            from util.payment_adapters.paypal_adapter import PayPalAdapter
            return PayPalAdapter()

        # Padrão: Mercado Pago
        from util.payment_adapters.mercadopago_adapter import MercadoPagoAdapter
        return MercadoPagoAdapter()

    @classmethod
    def obter_provider_por_chave(cls, chave: str) -> PaymentProvider:
        """
        Retorna o adapter para uma chave específica de provedor.

        Útil para exibir detalhes de pagamentos antigos com o provedor original,
        independentemente do provedor ativo no momento.

        Args:
            chave: 'mercadopago' ou 'stripe'

        Returns:
            Instância do adapter correspondente
        """
        if chave == "stripe":
            from util.payment_adapters.stripe_adapter import StripeAdapter
            return StripeAdapter()

        if chave == "paypal":
            from util.payment_adapters.paypal_adapter import PayPalAdapter
            return PayPalAdapter()

        from util.payment_adapters.mercadopago_adapter import MercadoPagoAdapter
        return MercadoPagoAdapter()
