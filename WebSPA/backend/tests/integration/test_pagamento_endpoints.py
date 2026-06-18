"""
Testes de endpoint do módulo de pagamentos (routes/pagamento_routes.py).

Cobre caminhos felizes e tristes de TODOS os endpoints sob /api/pagamentos:
    GET    /api/pagamentos                         → lista do usuário logado
    POST   /api/pagamentos                         → cria checkout → {init_point, pagamento_id}
    GET    /api/pagamentos/{id}                     → status de um pagamento
    POST   /api/pagamentos/{id}/paypal/capturar    → captura order PayPal
    POST   /api/pagamentos/webhook/mercadopago     → IPN MercadoPago (sem auth/CSRF)
    POST   /api/pagamentos/webhook/stripe          → webhook Stripe (sem auth/CSRF)
    POST   /api/pagamentos/webhook/paypal          → webhook PayPal (sem auth/CSRF)

Contrato (ver CLAUDE.md):
    - @requer_autenticacao() sem sessão → 401 (type unauthorized).
    - Mutação sem header X-CSRF-Token → 403 (type forbidden).
    - Webhooks isentos de CSRF e auth (CSRF_EXEMPT_PATHS: /api/pagamentos/webhook).
    - Validação Pydantic falha → 422 (type validation_error).
    - 404 quando o pagamento não existe (ou pertence a outro usuário).

⚠️ NENHUMA chamada real a Mercado Pago / Stripe / PayPal é feita: todas as
funções de provedor são mockadas com unittest.mock.patch no ponto de uso.

⚠️ A tabela `pagamento` NÃO é limpa pelo conftest — fixture autouse abaixo faz
DELETE antes e depois de cada teste para isolar.
"""
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status

from model.pagamento_model import Pagamento, StatusPagamento


pytestmark = [pytest.mark.integration, pytest.mark.crud]


# =============================================================================
# Helpers / Fixtures
# =============================================================================

def _csrf(client):
    """Obtém um token CSRF válido para a sessão do cliente."""
    return client.get("/api/csrf-token").json()["token"]


@pytest.fixture(autouse=True)
def _limpar_pagamentos():  # pyright: ignore
    """A tabela `pagamento` não é limpa pelo conftest — isola cada teste.

    Garante também que a tabela exista no banco temporário do teste (o conftest
    não a cria), criando-a via repo antes de limpar.
    """
    from repo import pagamento_repo
    from util.db_util import obter_conexao

    def limpa():
        pagamento_repo.criar_tabela()
        with obter_conexao() as conn:
            conn.execute("DELETE FROM pagamento")

    limpa()
    yield
    limpa()


def _id_usuario_por_email(email: str) -> int:
    """Retorna o id do usuário cadastrado (para inserir pagamentos direto no banco)."""
    from repo import usuario_repo

    usuario = usuario_repo.obter_por_email(email)
    assert usuario is not None, f"Usuário {email} não encontrado"
    return usuario.id


def _inserir_pagamento(
    usuario_id: int,
    descricao: str = "Plano Premium",
    valor: float = 49.90,
    status_pg: StatusPagamento = StatusPagamento.PENDENTE,
    preference_id=None,
    provider: str = "mercadopago",
) -> int:
    """Insere um pagamento diretamente no banco e devolve o id."""
    from repo import pagamento_repo

    pid = pagamento_repo.inserir(
        Pagamento(
            id=0,
            usuario_id=usuario_id,
            descricao=descricao,
            valor=valor,
            status=status_pg,
            preference_id=preference_id,
            provider=provider,
        )
    )
    assert pid is not None
    return pid


def _provider_fake(checkout_url="https://sandbox.checkout/redirect/abc123"):
    """Cria um provider mockado para PaymentService.obter_provider()."""
    provider = MagicMock()
    provider.chave = "mercadopago"
    provider.nome = "Mercado Pago"
    provider.criar_checkout.return_value = {
        "reference_id": "PREF-XYZ-789",
        "checkout_url": checkout_url,
    }
    return provider


# =============================================================================
# GET /api/pagamentos  (listar)
# =============================================================================

class TestListar:
    def test_lista_vazia_autenticado(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/pagamentos")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_lista_apenas_pagamentos_do_usuario(
        self, cliente_autenticado, usuario_teste, criar_usuario_direto
    ):
        uid = _id_usuario_por_email(usuario_teste["email"])
        _inserir_pagamento(uid, descricao="Assinatura A", valor=10.0)
        _inserir_pagamento(uid, descricao="Assinatura B", valor=20.0)
        # Pagamento de outro usuário não deve aparecer
        outro_id = criar_usuario_direto("Outro", "outro@example.com", "Senha@123")
        _inserir_pagamento(outro_id, descricao="De Outro", valor=99.0)

        resp = cliente_autenticado.get("/api/pagamentos")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert isinstance(corpo, list)
        assert len(corpo) == 2
        ids_usuarios = {item["usuario_id"] for item in corpo}
        assert ids_usuarios == {uid}
        # Shape do item
        item = corpo[0]
        for campo in ("id", "usuario_id", "descricao", "valor", "status", "provider"):
            assert campo in item
        # Enum serializa como string do valor
        assert item["status"] == StatusPagamento.PENDENTE.value

    def test_lista_sem_sessao_401(self, client):
        resp = client.get("/api/pagamentos")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# POST /api/pagamentos  (criar checkout)
# =============================================================================

class TestCriar:
    def _payload(self, **over):
        base = {"descricao": "Plano Premium Anual", "valor": 99.90}
        base.update(over)
        return base

    def test_criar_sucesso_retorna_init_point(self, cliente_autenticado, usuario_teste):
        token = _csrf(cliente_autenticado)
        provider = _provider_fake(checkout_url="https://sandbox.mp/checkout/INIT-POINT")
        with patch(
            "routes.pagamento_routes.PaymentService.obter_provider",
            return_value=provider,
        ):
            resp = cliente_autenticado.post(
                "/api/pagamentos",
                json=self._payload(),
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_201_CREATED
        corpo = resp.json()
        assert corpo["init_point"] == "https://sandbox.mp/checkout/INIT-POINT"
        assert isinstance(corpo["pagamento_id"], int)
        assert corpo["pagamento_id"] > 0

        # provider.criar_checkout foi de fato chamado (sem rede real)
        provider.criar_checkout.assert_called_once()

        # O pagamento foi persistido como Pendente com url_checkout e preference_id
        uid = _id_usuario_por_email(usuario_teste["email"])
        lista = cliente_autenticado.get("/api/pagamentos").json()
        assert len(lista) == 1
        pg = lista[0]
        assert pg["usuario_id"] == uid
        assert pg["status"] == StatusPagamento.PENDENTE.value
        assert pg["preference_id"] == "PREF-XYZ-789"
        assert pg["url_checkout"] == "https://sandbox.mp/checkout/INIT-POINT"

    def test_criar_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.post(
            "/api/pagamentos",
            json=self._payload(),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_criar_sem_csrf_403(self, cliente_autenticado):
        resp = cliente_autenticado.post("/api/pagamentos", json=self._payload())
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_criar_valor_zero_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/pagamentos",
            json=self._payload(valor=0),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_criar_valor_negativo_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/pagamentos",
            json=self._payload(valor=-5),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_criar_descricao_curta_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/pagamentos",
            json=self._payload(descricao="ab"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_criar_valor_acima_do_maximo_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/pagamentos",
            json=self._payload(valor=1_000_000),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_criar_falha_checkout_provedor_502(self, cliente_autenticado):
        """Provider retorna None (falha ao conectar) → 502 Bad Gateway."""
        token = _csrf(cliente_autenticado)
        provider = MagicMock()
        provider.chave = "mercadopago"
        provider.nome = "Mercado Pago"
        provider.criar_checkout.return_value = None
        with patch(
            "routes.pagamento_routes.PaymentService.obter_provider",
            return_value=provider,
        ):
            resp = cliente_autenticado.post(
                "/api/pagamentos",
                json=self._payload(),
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_502_BAD_GATEWAY

    def test_criar_excede_rate_limit_429(self, cliente_autenticado, bloquear_rate_limiter):
        token = _csrf(cliente_autenticado)
        provider = _provider_fake()
        with bloquear_rate_limiter("routes.pagamento_routes.pagamento_criar_limiter"):
            with patch(
                "routes.pagamento_routes.PaymentService.obter_provider",
                return_value=provider,
            ):
                resp = cliente_autenticado.post(
                    "/api/pagamentos",
                    json=self._payload(),
                    headers={"X-CSRF-Token": token},
                )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in resp.headers


# =============================================================================
# GET /api/pagamentos/{id}  (obter)
# =============================================================================

class TestObter:
    def test_obter_proprio_pagamento(self, cliente_autenticado, usuario_teste):
        uid = _id_usuario_por_email(usuario_teste["email"])
        pid = _inserir_pagamento(uid, descricao="Curso de Python", valor=149.90)

        resp = cliente_autenticado.get(f"/api/pagamentos/{pid}")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["id"] == pid
        assert corpo["usuario_id"] == uid
        assert corpo["descricao"] == "Curso de Python"
        assert corpo["status"] == StatusPagamento.PENDENTE.value

    def test_obter_inexistente_404(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/pagamentos/999999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_obter_de_outro_usuario_404(self, cliente_autenticado, criar_usuario_direto):
        """Não-dono não-admin recebe 404 (não revela existência do recurso)."""
        outro_id = criar_usuario_direto("Outro", "outro@example.com", "Senha@123")
        pid = _inserir_pagamento(outro_id, descricao="De Outro", valor=10.0)
        resp = cliente_autenticado.get(f"/api/pagamentos/{pid}")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_obter_admin_ve_qualquer_pagamento(self, admin_autenticado, criar_usuario_direto):
        """Admin pode consultar pagamento de qualquer usuário."""
        outro_id = criar_usuario_direto("Outro", "outro@example.com", "Senha@123")
        pid = _inserir_pagamento(outro_id, descricao="De Outro", valor=33.0)
        resp = admin_autenticado.get(f"/api/pagamentos/{pid}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["id"] == pid

    def test_obter_sem_sessao_401(self, client):
        resp = client.get("/api/pagamentos/1")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# POST /api/pagamentos/{id}/paypal/capturar
# =============================================================================

class TestPaypalCapturar:
    def test_capturar_sucesso_aprova_pagamento(self, cliente_autenticado, usuario_teste):
        uid = _id_usuario_por_email(usuario_teste["email"])
        pid = _inserir_pagamento(
            uid, descricao="Doação", valor=25.0, provider="paypal"
        )
        token = _csrf(cliente_autenticado)

        adapter = MagicMock()
        adapter.capturar_ordem.return_value = {
            "status": "COMPLETED",
            "capture_id": "CAP-123",
        }
        with patch(
            "util.payment_adapters.paypal_adapter.PayPalAdapter",
            return_value=adapter,
        ):
            resp = cliente_autenticado.post(
                f"/api/pagamentos/{pid}/paypal/capturar?token=ORDER-ABC",
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["id"] == pid
        assert corpo["status"] == StatusPagamento.APROVADO.value
        adapter.capturar_ordem.assert_called_once_with("ORDER-ABC")

    def test_capturar_falha_paypal_402(self, cliente_autenticado, usuario_teste):
        uid = _id_usuario_por_email(usuario_teste["email"])
        pid = _inserir_pagamento(uid, descricao="Doação", valor=25.0, provider="paypal")
        token = _csrf(cliente_autenticado)

        adapter = MagicMock()
        adapter.capturar_ordem.return_value = {"status": "DECLINED"}
        with patch(
            "util.payment_adapters.paypal_adapter.PayPalAdapter",
            return_value=adapter,
        ):
            resp = cliente_autenticado.post(
                f"/api/pagamentos/{pid}/paypal/capturar?token=ORDER-ABC",
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_402_PAYMENT_REQUIRED
        # Pagamento marcado como Recusado
        pg = cliente_autenticado.get(f"/api/pagamentos/{pid}").json()
        assert pg["status"] == StatusPagamento.RECUSADO.value

    def test_capturar_pagamento_inexistente_404(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/pagamentos/999999/paypal/capturar?token=ORDER-ABC",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_capturar_de_outro_usuario_404(self, cliente_autenticado, criar_usuario_direto):
        outro_id = criar_usuario_direto("Outro", "outro@example.com", "Senha@123")
        pid = _inserir_pagamento(outro_id, descricao="De Outro", valor=10.0, provider="paypal")
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            f"/api/pagamentos/{pid}/paypal/capturar?token=ORDER-ABC",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_capturar_sem_token_query_422(self, cliente_autenticado, usuario_teste):
        """O parâmetro de query `token` é obrigatório → 422 se ausente."""
        uid = _id_usuario_por_email(usuario_teste["email"])
        pid = _inserir_pagamento(uid, descricao="Doação", valor=25.0, provider="paypal")
        csrf = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            f"/api/pagamentos/{pid}/paypal/capturar",
            headers={"X-CSRF-Token": csrf},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_capturar_sem_csrf_403(self, cliente_autenticado, usuario_teste):
        uid = _id_usuario_por_email(usuario_teste["email"])
        pid = _inserir_pagamento(uid, descricao="Doação", valor=25.0, provider="paypal")
        resp = cliente_autenticado.post(
            f"/api/pagamentos/{pid}/paypal/capturar?token=ORDER-ABC"
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_capturar_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.post(
            "/api/pagamentos/1/paypal/capturar?token=ORDER-ABC",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# POST /api/pagamentos/webhook/{provedor}  (sem auth, sem CSRF)
# =============================================================================

class TestWebhookMercadoPago:
    def test_webhook_sem_csrf_e_sem_sessao_aceito(self, client, usuario_teste, criar_usuario):
        """Webhook é isento de CSRF e de auth; payload válido atualiza o status."""
        criar_usuario(usuario_teste["nome"], usuario_teste["email"], usuario_teste["senha"])
        uid = _id_usuario_por_email(usuario_teste["email"])
        pid = _inserir_pagamento(uid, descricao="Item", valor=50.0, provider="mercadopago")

        adapter = MagicMock()
        adapter.processar_webhook.return_value = {
            "pagamento_id": pid,
            "provider_payment_id": "MP-PAY-1",
            "reference_id": None,
            "status": StatusPagamento.APROVADO.value,
        }
        body = json.dumps(
            {"action": "payment.updated", "data": {"id": "1"}, "type": "payment"}
        )
        with patch(
            "util.payment_adapters.mercadopago_adapter.MercadoPagoAdapter",
            return_value=adapter,
        ):
            # SEM header X-CSRF-Token e SEM sessão
            resp = client.post("/api/pagamentos/webhook/mercadopago", content=body)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"status": "ok"}

        # Status efetivamente atualizado no banco
        from repo import pagamento_repo
        pagamento_atualizado = pagamento_repo.obter_por_id(pid)
        assert pagamento_atualizado is not None
        assert pagamento_atualizado.status == StatusPagamento.APROVADO

    def test_webhook_payload_ignorado(self, client):
        """Adapter retorna None → resposta 'ignored' (HTTP 200)."""
        adapter = MagicMock()
        adapter.processar_webhook.return_value = None
        with patch(
            "util.payment_adapters.mercadopago_adapter.MercadoPagoAdapter",
            return_value=adapter,
        ):
            resp = client.post("/api/pagamentos/webhook/mercadopago", content=b"lixo")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"status": "ignored"}

    def test_webhook_pagamento_nao_encontrado(self, client):
        """Resultado válido mas pagamento inexistente → 'not_found' (HTTP 200)."""
        adapter = MagicMock()
        adapter.processar_webhook.return_value = {
            "pagamento_id": 888888,
            "provider_payment_id": "MP-PAY-X",
            "reference_id": None,
            "status": StatusPagamento.APROVADO.value,
        }
        with patch(
            "util.payment_adapters.mercadopago_adapter.MercadoPagoAdapter",
            return_value=adapter,
        ):
            resp = client.post("/api/pagamentos/webhook/mercadopago", content=b"{}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"status": "not_found"}


class TestWebhookStripe:
    def test_webhook_stripe_aprova(self, client, usuario_teste, criar_usuario):
        criar_usuario(usuario_teste["nome"], usuario_teste["email"], usuario_teste["senha"])
        uid = _id_usuario_por_email(usuario_teste["email"])
        pid = _inserir_pagamento(uid, descricao="Item Stripe", valor=70.0, provider="stripe")

        adapter = MagicMock()
        adapter.processar_webhook.return_value = {
            "pagamento_id": pid,
            "provider_payment_id": "pi_123",
            "reference_id": None,
            "status": StatusPagamento.APROVADO.value,
        }
        with patch(
            "util.payment_adapters.stripe_adapter.StripeAdapter",
            return_value=adapter,
        ):
            resp = client.post("/api/pagamentos/webhook/stripe", content=b"{}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"status": "ok"}

    def test_webhook_stripe_ignorado(self, client):
        adapter = MagicMock()
        adapter.processar_webhook.return_value = None
        with patch(
            "util.payment_adapters.stripe_adapter.StripeAdapter",
            return_value=adapter,
        ):
            resp = client.post("/api/pagamentos/webhook/stripe", content=b"invalido")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"status": "ignored"}


class TestWebhookPaypal:
    def test_webhook_paypal_localiza_por_reference_id(self, client, usuario_teste, criar_usuario):
        criar_usuario(usuario_teste["nome"], usuario_teste["email"], usuario_teste["senha"])
        uid = _id_usuario_por_email(usuario_teste["email"])
        pid = _inserir_pagamento(
            uid,
            descricao="Item PayPal",
            valor=80.0,
            provider="paypal",
            preference_id="REF-PP-1",
        )

        adapter = MagicMock()
        adapter.processar_webhook.return_value = {
            "pagamento_id": None,
            "provider_payment_id": "PP-PAY-1",
            "reference_id": "REF-PP-1",
            "status": StatusPagamento.APROVADO.value,
        }
        with patch(
            "util.payment_adapters.paypal_adapter.PayPalAdapter",
            return_value=adapter,
        ):
            resp = client.post("/api/pagamentos/webhook/paypal", content=b"{}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"status": "ok"}

        from repo import pagamento_repo
        pagamento_atualizado = pagamento_repo.obter_por_id(pid)
        assert pagamento_atualizado is not None
        assert pagamento_atualizado.status == StatusPagamento.APROVADO

    def test_webhook_paypal_ignorado(self, client):
        adapter = MagicMock()
        adapter.processar_webhook.return_value = None
        with patch(
            "util.payment_adapters.paypal_adapter.PayPalAdapter",
            return_value=adapter,
        ):
            resp = client.post("/api/pagamentos/webhook/paypal", content=b"x")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"status": "ignored"}
