"""
Testes de endpoint do módulo administrativo de pagamentos
(routes/admin_pagamentos_routes.py).

Cobre caminhos felizes e tristes de:
    GET  /api/admin/pagamentos        -> lista paginada (filtro opcional por status)
    GET  /api/admin/pagamentos/{id}   -> detalhes + dados do provedor

Contrato (ver CLAUDE.md):
    - Todos endpoints exigem perfil ADMIN (@requer_autenticacao([Perfil.ADMIN.value])).
    - Sem sessão -> 401 (type unauthorized).
    - Perfil errado (Cliente) -> 403 (type forbidden).
    - Recurso inexistente -> 404 (type not_found).
    - Paginação via PaginaResponse[T] = {items, pagina, por_pagina, total, total_paginas}.

NOTA sobre provedores externos:
    GET /{id} consulta dados no provedor via
    ``PaymentService.obter_provider_por_chave(provider)`` e, em seguida,
    ``adapter.obter_dados_pagamento(payment_id)`` e ``adapter.nome``.
    Para NUNCA fazer chamada externa real, mockamos
    ``routes.admin_pagamentos_routes.PaymentService.obter_provider_por_chave``
    no ponto de uso, retornando um adapter fake.

NOTA sobre isolamento:
    A tabela `pagamento` NÃO é limpa pelo conftest. Fixture autouse abaixo
    faz DELETE FROM pagamento antes e depois de cada teste.
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status

from model.pagamento_model import Pagamento, StatusPagamento
from repo import pagamento_repo


pytestmark = [pytest.mark.integration, pytest.mark.crud]


# =============================================================================
# Isolamento da tabela `pagamento` (não limpa pelo conftest)
# =============================================================================

@pytest.fixture(autouse=True)
def _limpar_pagamentos():  # pyright: ignore
    from util.db_util import obter_conexao

    # Garante que a tabela existe no banco temporário de teste
    pagamento_repo.criar_tabela()

    def limpa():
        with obter_conexao() as conn:
            conn.execute("DELETE FROM pagamento")

    limpa()
    yield
    limpa()


# =============================================================================
# Helpers
# =============================================================================

def _inserir_pagamento(
    usuario_id: int,
    descricao: str = "Plano Pro",
    valor: float = 49.9,
    status_pag: StatusPagamento = StatusPagamento.PENDENTE,
    provider: str = "mercadopago",
    payment_id=None,
    preference_id=None,
    external_reference=None,
    url_checkout=None,
) -> int:
    """Insere um pagamento direto via repo e retorna o id gerado."""
    pagamento = Pagamento(
        id=0,
        usuario_id=usuario_id,
        descricao=descricao,
        valor=valor,
        status=status_pag,
        preference_id=preference_id,
        payment_id=payment_id,
        external_reference=external_reference,
        url_checkout=url_checkout,
        provider=provider,
    )
    novo_id = pagamento_repo.inserir(pagamento)
    assert novo_id is not None
    return novo_id


def _adapter_fake(nome="Mercado Pago", dados=None):
    """Cria um adapter fake (não faz chamada externa)."""
    adapter = MagicMock()
    adapter.nome = nome
    adapter.obter_dados_pagamento.return_value = dados
    return adapter


@pytest.fixture
def dono_pagamento(criar_usuario_direto) -> int:
    """Cria um usuário real e devolve seu id para ser dono dos pagamentos inseridos.

    Evita depender do default mágico `usuario_id=1` (que só funcionava por
    coincidência do autoincrement). Há FK pagamento.usuario_id → usuario.id, então
    todo pagamento inserido precisa referenciar um usuário realmente existente.
    """
    return criar_usuario_direto(
        "Dono Pagamento", "dono.pagamento@example.com", "Senha@123"
    )


# =============================================================================
# GET /api/admin/pagamentos  — autorização
# =============================================================================

class TestListarAutorizacao:
    def test_sem_sessao_401(self, client):
        resp = client.get("/api/admin/pagamentos")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_perfil_cliente_403(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/admin/pagamentos")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_admin_acessa_200(self, admin_autenticado):
        resp = admin_autenticado.get("/api/admin/pagamentos")
        assert resp.status_code == status.HTTP_200_OK


# =============================================================================
# GET /api/admin/pagamentos  — listagem / paginação
# =============================================================================

class TestListar:
    def test_lista_vazia_shape(self, admin_autenticado):
        resp = admin_autenticado.get("/api/admin/pagamentos")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        # Envelope PaginaResponse completo
        assert set(corpo.keys()) == {
            "items", "pagina", "por_pagina", "total", "total_paginas",
        }
        assert corpo["items"] == []
        assert corpo["pagina"] == 1
        assert corpo["por_pagina"] == 10
        assert corpo["total"] == 0
        # total_paginas mínimo é 1 (ver Paginacao.__post_init__)
        assert corpo["total_paginas"] == 1

    def test_item_shape(self, admin_autenticado, dono_pagamento):
        _inserir_pagamento(
            usuario_id=dono_pagamento,
            descricao="Assinatura",
            valor=99.5,
            status_pag=StatusPagamento.APROVADO,
            provider="stripe",
            payment_id="pay_123",
            preference_id="pref_123",
        )
        resp = admin_autenticado.get("/api/admin/pagamentos")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 1
        assert len(corpo["items"]) == 1
        item = corpo["items"][0]
        assert item["descricao"] == "Assinatura"
        assert item["valor"] == 99.5
        # Enum serializa como string do valor
        assert item["status"] == StatusPagamento.APROVADO.value
        assert item["provider"] == "stripe"
        assert item["payment_id"] == "pay_123"
        assert item["preference_id"] == "pref_123"
        assert "id" in item
        assert "usuario_id" in item

    def test_total_e_total_paginas(self, admin_autenticado, dono_pagamento):
        # 25 pagamentos, 10 por página -> 3 páginas
        for i in range(25):
            _inserir_pagamento(usuario_id=dono_pagamento, descricao=f"Pag {i}")
        resp = admin_autenticado.get("/api/admin/pagamentos")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 25
        assert corpo["por_pagina"] == 10
        assert corpo["total_paginas"] == 3
        assert len(corpo["items"]) == 10
        assert corpo["pagina"] == 1

    def test_segunda_pagina(self, admin_autenticado, dono_pagamento):
        for i in range(25):
            _inserir_pagamento(usuario_id=dono_pagamento, descricao=f"Pag {i}")
        resp = admin_autenticado.get("/api/admin/pagamentos?pagina=2")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["pagina"] == 2
        assert len(corpo["items"]) == 10

    def test_ultima_pagina_parcial(self, admin_autenticado, dono_pagamento):
        for i in range(25):
            _inserir_pagamento(usuario_id=dono_pagamento, descricao=f"Pag {i}")
        resp = admin_autenticado.get("/api/admin/pagamentos?pagina=3")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["pagina"] == 3
        assert len(corpo["items"]) == 5

    def test_por_pagina_customizado(self, admin_autenticado, dono_pagamento):
        for i in range(12):
            _inserir_pagamento(usuario_id=dono_pagamento, descricao=f"Pag {i}")
        resp = admin_autenticado.get("/api/admin/pagamentos?por_pagina=5")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["por_pagina"] == 5
        assert corpo["total"] == 12
        assert corpo["total_paginas"] == 3
        assert len(corpo["items"]) == 5


# =============================================================================
# GET /api/admin/pagamentos  — filtro por status
# =============================================================================

class TestListarFiltroStatus:
    def test_filtro_status_valido(self, admin_autenticado, dono_pagamento):
        _inserir_pagamento(usuario_id=dono_pagamento, descricao="A", status_pag=StatusPagamento.APROVADO)
        _inserir_pagamento(usuario_id=dono_pagamento, descricao="B", status_pag=StatusPagamento.APROVADO)
        _inserir_pagamento(usuario_id=dono_pagamento, descricao="C", status_pag=StatusPagamento.PENDENTE)
        _inserir_pagamento(usuario_id=dono_pagamento, descricao="D", status_pag=StatusPagamento.RECUSADO)

        resp = admin_autenticado.get(
            f"/api/admin/pagamentos?status_filtro={StatusPagamento.APROVADO.value}"
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 2
        assert all(
            i["status"] == StatusPagamento.APROVADO.value for i in corpo["items"]
        )

    def test_filtro_status_sem_correspondencia(self, admin_autenticado, dono_pagamento):
        _inserir_pagamento(usuario_id=dono_pagamento, status_pag=StatusPagamento.PENDENTE)
        resp = admin_autenticado.get(
            f"/api/admin/pagamentos?status_filtro={StatusPagamento.CANCELADO.value}"
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 0
        assert corpo["items"] == []

    def test_filtro_status_inexistente_ignorado(self, admin_autenticado, dono_pagamento):
        # status_filtro inválido (não existe no enum) é ignorado -> retorna todos
        _inserir_pagamento(usuario_id=dono_pagamento, status_pag=StatusPagamento.PENDENTE)
        _inserir_pagamento(usuario_id=dono_pagamento, status_pag=StatusPagamento.APROVADO)
        resp = admin_autenticado.get(
            "/api/admin/pagamentos?status_filtro=NaoExisteIsso"
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 2


# =============================================================================
# GET /api/admin/pagamentos/{id}  — autorização
# =============================================================================

class TestDetalhesAutorizacao:
    def test_sem_sessao_401(self, client, criar_usuario_direto, usuario_teste):
        uid = criar_usuario_direto(
            usuario_teste["nome"], usuario_teste["email"],
            usuario_teste["senha"], usuario_teste["perfil"],
        )
        pid = _inserir_pagamento(usuario_id=uid)
        resp = client.get(f"/api/admin/pagamentos/{pid}")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_perfil_cliente_403(self, cliente_autenticado, dono_pagamento):
        pid = _inserir_pagamento(usuario_id=dono_pagamento)
        resp = cliente_autenticado.get(f"/api/admin/pagamentos/{pid}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"


# =============================================================================
# GET /api/admin/pagamentos/{id}  — detalhes
# =============================================================================

class TestDetalhes:
    def test_pagamento_inexistente_404(self, admin_autenticado):
        resp = admin_autenticado.get("/api/admin/pagamentos/999999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_detalhes_sem_payment_id_nao_consulta_provider(self, admin_autenticado, dono_pagamento):
        """payment_id None -> não consulta o provedor; dados_provider fica None."""
        pid = _inserir_pagamento(
            usuario_id=dono_pagamento,
            descricao="Sem pagamento confirmado",
            provider="mercadopago",
            payment_id=None,
        )
        with patch(
            "routes.admin_pagamentos_routes.PaymentService.obter_provider_por_chave"
        ) as mock_obter:
            mock_obter.return_value = _adapter_fake(nome="Mercado Pago")
            resp = admin_autenticado.get(f"/api/admin/pagamentos/{pid}")

        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["pagamento"]["id"] == pid
        assert corpo["pagamento"]["descricao"] == "Sem pagamento confirmado"
        assert corpo["provider_nome"] == "Mercado Pago"
        assert corpo["dados_provider"] is None

    def test_detalhes_com_payment_id_consulta_provider(self, admin_autenticado, dono_pagamento):
        """payment_id presente -> consulta o adapter (mockado) por dados."""
        pid = _inserir_pagamento(
            usuario_id=dono_pagamento,
            descricao="Confirmado",
            provider="stripe",
            payment_id="pay_abc",
            status_pag=StatusPagamento.APROVADO,
        )
        dados_falsos = {"id": "pay_abc", "status": "approved", "amount": 4990}
        adapter = _adapter_fake(nome="Stripe", dados=dados_falsos)

        with patch(
            "routes.admin_pagamentos_routes.PaymentService.obter_provider_por_chave"
        ) as mock_obter:
            mock_obter.return_value = adapter
            resp = admin_autenticado.get(f"/api/admin/pagamentos/{pid}")

        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["pagamento"]["id"] == pid
        assert corpo["provider_nome"] == "Stripe"
        assert corpo["dados_provider"] == dados_falsos
        # Consultou o provedor com a chave correta e o payment_id correto
        mock_obter.assert_called_with("stripe")
        adapter.obter_dados_pagamento.assert_called_once_with("pay_abc")

    def test_detalhes_provider_falha_degrada_para_none(self, admin_autenticado, dono_pagamento):
        """Se a consulta ao provedor lança, a rota engole o erro (dados_provider=None)."""
        pid = _inserir_pagamento(
            usuario_id=dono_pagamento,
            descricao="Provider instável",
            provider="mercadopago",
            payment_id="pay_falha",
        )
        adapter = _adapter_fake(nome="Mercado Pago")
        adapter.obter_dados_pagamento.side_effect = RuntimeError("API fora do ar")

        with patch(
            "routes.admin_pagamentos_routes.PaymentService.obter_provider_por_chave"
        ) as mock_obter:
            mock_obter.return_value = adapter
            resp = admin_autenticado.get(f"/api/admin/pagamentos/{pid}")

        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["pagamento"]["id"] == pid
        assert corpo["dados_provider"] is None
        assert corpo["provider_nome"] == "Mercado Pago"
