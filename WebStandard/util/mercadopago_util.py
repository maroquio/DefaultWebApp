"""
Utilitário de integração com o Mercado Pago.

Encapsula o SDK do Mercado Pago e expõe funções de alto nível para:
- Criar preferências de pagamento (Checkout Pro)
- Consultar dados de pagamentos pelo ID
- Processar notificações IPN (webhook)

Fluxo do Checkout Pro:
    1. criar_preferencia() → retorna preference_id e init_point (URL de checkout)
    2. Usuário é redirecionado para init_point
    3. Usuário paga no site do Mercado Pago
    4. MP redireciona para back_url com payment_id e status
    5. MP envia webhook IPN → processar_webhook() atualiza o status no BD

Referência:
    https://www.mercadopago.com.br/developers/pt/docs/checkout-pro/landing
"""

from typing import Optional

from util.config import MERCADOPAGO_ACCESS_TOKEN
from util.logger_config import logger


def obter_sdk():
    """
    Retorna uma instância autenticada do SDK do Mercado Pago.

    O SDK é criado com o access token configurado em .env.
    Usar credenciais TEST-xxx para ambiente sandbox.

    Returns:
        Instância do mercadopago.SDK
    """
    import mercadopago
    return mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)


def criar_preferencia(
    descricao: str,
    valor: float,
    pagamento_id: int,
    back_urls: dict,
    webhook_url: Optional[str] = None,
) -> Optional[dict]:
    """
    Cria uma preferência de pagamento no Mercado Pago (Checkout Pro).

    Uma "preferência" define o que está sendo pago (item, valor, URLs de retorno).
    O MP retorna um `init_point` — a URL para onde o usuário deve ser redirecionado.

    Args:
        descricao: Descrição do produto/serviço (aparece na tela do MP)
        valor: Valor em reais (float, ex: 29.90)
        pagamento_id: ID do pagamento no nosso banco (usado como external_reference)
        back_urls: Dict com URLs de retorno:
            {
                "success": "https://app.com/pagamentos/sucesso",
                "pending": "https://app.com/pagamentos/pendente",
                "failure": "https://app.com/pagamentos/falha",
            }
        webhook_url: URL do endpoint IPN para notificações (opcional)

    Returns:
        Dict com:
            - preference_id: ID da preferência no MP
            - init_point: URL de checkout (ambiente produção)
            - sandbox_init_point: URL de checkout (ambiente sandbox/teste)
        Ou None se ocorrer erro.

    Exemplo:
        resultado = criar_preferencia(
            descricao="Plano Premium",
            valor=99.90,
            pagamento_id=42,
            back_urls={
                "success": f"{BASE_URL}/pagamentos/sucesso",
                "pending": f"{BASE_URL}/pagamentos/pendente",
                "failure": f"{BASE_URL}/pagamentos/falha",
            },
            webhook_url=f"{BASE_URL}/pagamentos/webhook",
        )
        if resultado:
            redirect_url = resultado["init_point"]  # ou sandbox_init_point para testes
    """
    sdk = obter_sdk()

    preference_data = {
        "items": [
            {
                "title": descricao,
                "quantity": 1,
                "unit_price": valor,
                "currency_id": "BRL",
            }
        ],
        "back_urls": back_urls,
        "auto_return": "approved",
        "external_reference": str(pagamento_id),
    }

    if webhook_url:
        preference_data["notification_url"] = webhook_url

    try:
        preference_response = sdk.preference().create(preference_data)
        response_data = preference_response.get("response", {})

        if preference_response.get("status") not in (200, 201):
            logger.error(
                f"Erro ao criar preferência no MP: status={preference_response.get('status')}, "
                f"response={response_data}"
            )
            return None

        preference_id = response_data.get("id")
        init_point = response_data.get("init_point")
        sandbox_init_point = response_data.get("sandbox_init_point")

        logger.info(
            f"Preferência MP criada: id={preference_id}, pagamento_id={pagamento_id}"
        )

        return {
            "preference_id": preference_id,
            "init_point": init_point,
            "sandbox_init_point": sandbox_init_point,
        }

    except Exception as e:
        logger.error(f"Exceção ao criar preferência no MP: {e}", exc_info=True)
        return None


def obter_pagamento_mp(payment_id: str) -> Optional[dict]:
    """
    Consulta os dados de um pagamento no Mercado Pago pelo payment_id.

    Usado para verificar o status atual de um pagamento diretamente na API do MP,
    especialmente útil nas páginas de retorno e para validar webhooks.

    Args:
        payment_id: ID do pagamento no Mercado Pago (recebido nas back_urls ou no webhook)

    Returns:
        Dict com os dados completos do pagamento (conforme API do MP), ou None se erro.

    Campos relevantes no retorno:
        - id: ID do pagamento
        - status: "approved" | "pending" | "rejected" | "cancelled" | "refunded"
        - status_detail: Detalhe do status (ex: "accredited", "cc_rejected_bad_filled_cvv")
        - transaction_amount: Valor pago
        - external_reference: Referência externa que definimos (nosso pagamento_id)
        - payer.email: Email do pagador
    """
    sdk = obter_sdk()

    try:
        payment_response = sdk.payment().get(payment_id)
        response_data = payment_response.get("response", {})

        if payment_response.get("status") != 200:
            logger.error(
                f"Erro ao consultar pagamento MP id={payment_id}: "
                f"status={payment_response.get('status')}"
            )
            return None

        logger.debug(
            f"Pagamento MP consultado: id={payment_id}, "
            f"status={response_data.get('status')}"
        )
        return response_data

    except Exception as e:
        logger.error(f"Exceção ao consultar pagamento MP id={payment_id}: {e}", exc_info=True)
        return None


def processar_webhook(dados: dict) -> Optional[dict]:
    """
    Processa uma notificação IPN (webhook) recebida do Mercado Pago.

    O MP envia notificações POST para o endpoint /pagamentos/webhook quando
    o status de um pagamento muda. Este utilitário normaliza os dados recebidos
    e consulta o status atual na API do MP.

    Tipos de notificação que chegam via IPN:
        - type="payment": Notificação de pagamento (aprovado, recusado, etc.)
        - type="merchant_order": Ordem de compra (ignoramos neste fluxo)

    Args:
        dados: Corpo da requisição POST do webhook (dict JSON)

    Returns:
        Dict com dados do pagamento normalizado:
            - payment_id: ID do pagamento no MP
            - status: Status traduzido para português ("Aprovado", "Recusado", etc.)
            - status_mp: Status original do MP ("approved", "rejected", etc.)
            - external_reference: Nosso ID interno (string)
        Ou None se não for uma notificação de pagamento válida.

    Mapeamento de status:
        approved   → Aprovado
        in_process → Em Processamento
        pending    → Pendente
        rejected   → Recusado
        cancelled  → Cancelado
        refunded   → Reembolsado
    """
    tipo = dados.get("type") or dados.get("topic")

    if tipo not in ("payment", "merchant_order"):
        logger.debug(f"Webhook MP ignorado: tipo='{tipo}'")
        return None

    # Extrair o payment_id da notificação
    payment_id = None

    # Formato IPN v2 (mais comum): {"type": "payment", "data": {"id": "123456"}}
    data_obj = dados.get("data", {})
    if data_obj:
        payment_id = str(data_obj.get("id", ""))

    # Formato IPN legacy: {"id": "123456", "topic": "payment"}
    if not payment_id:
        payment_id = str(dados.get("id", ""))

    if not payment_id or payment_id == "0":
        logger.warning(f"Webhook MP sem payment_id válido: {dados}")
        return None

    # Consultar dados atuais na API do MP
    dados_mp = obter_pagamento_mp(payment_id)
    if not dados_mp:
        return None

    status_mp = dados_mp.get("status", "")
    external_reference = dados_mp.get("external_reference", "")

    # Mapear status do MP para StatusPagamento do sistema
    mapa_status = {
        "approved": "Aprovado",
        "in_process": "Em Processamento",
        "pending": "Pendente",
        "rejected": "Recusado",
        "cancelled": "Cancelado",
        "refunded": "Reembolsado",
        "charged_back": "Reembolsado",
    }
    status_sistema = mapa_status.get(status_mp, "Pendente")

    logger.info(
        f"Webhook MP processado: payment_id={payment_id}, "
        f"status_mp={status_mp}, external_reference={external_reference}"
    )

    return {
        "payment_id": payment_id,
        "status": status_sistema,
        "status_mp": status_mp,
        "external_reference": external_reference,
    }
