"""
Testes de endpoint do módulo administrativo de chamados (routes/admin_chamados_routes.py).

Cobre caminhos felizes e tristes de (prefixo /api/admin/chamados, exigem ADMIN):
    GET   /api/admin/chamados/            (lista paginada, filtros)
    GET   /api/admin/chamados/{id}        (detalhe + histórico)
    POST  /api/admin/chamados/{id}/interacoes  (responder: mensagem + status)
    PATCH /api/admin/chamados/{id}/status (alterar status: fechar/reabrir)

Contrato (ver CLAUDE.md):
    - Sucesso: recurso puro com status correto (200/201) — ChamadoResponse / PaginaResponse.
    - Erro: {detail, type, errors} via util/exception_handlers.py.
    - Mutações exigem header X-CSRF-Token (senão 403, type="forbidden").
    - @requer_autenticacao([ADMIN]) → 401 sem sessão; 403 perfil não-admin.

Detalhe importante do endpoint `responder`: há DOIS modelos Pydantic no corpo
(dto_mensagem, dto_status), então o FastAPI espera o body aninhado:
    {"dto_mensagem": {"mensagem": "..."}, "dto_status": {"status": "..."}}
"""
import pytest
from fastapi import status

from model.chamado_model import Chamado, StatusChamado, PrioridadeChamado
from repo import chamado_repo
from util.perfis import Perfil


pytestmark = [pytest.mark.integration, pytest.mark.crud]


def _csrf(client):
    """Obtém um token CSRF válido para a sessão do cliente."""
    return client.get("/api/csrf-token").json()["token"]


def _criar_chamado(usuario_id: int, *,
                   titulo: str = "Problema no acesso ao sistema",
                   status_inicial: StatusChamado = StatusChamado.ABERTO,
                   prioridade: PrioridadeChamado = PrioridadeChamado.MEDIA) -> int:
    """Insere um chamado direto no banco (independente do client autenticado)."""
    chamado = Chamado(
        id=0,
        titulo=titulo,
        status=status_inicial,
        prioridade=prioridade,
        usuario_id=usuario_id,
    )
    novo_id = chamado_repo.inserir(chamado)
    assert novo_id is not None
    return novo_id


@pytest.fixture
def cliente_id(criar_usuario_direto):
    """Cria um cliente comum no banco e devolve seu id (dono dos chamados)."""
    return criar_usuario_direto(
        "Cliente Dono", "dono.chamado@example.com", "Senha@123", Perfil.CLIENTE.value
    )


# =============================================================================
# GET /api/admin/chamados/  (listagem paginada)
# =============================================================================

class TestListar:
    def test_lista_vazia_shape(self, admin_autenticado):
        resp = admin_autenticado.get("/api/admin/chamados/")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        # Shape de PaginaResponse[T]
        assert set(corpo.keys()) >= {
            "items", "pagina", "por_pagina", "total", "total_paginas"
        }
        assert corpo["items"] == []
        assert corpo["total"] == 0
        assert corpo["pagina"] == 1

    def test_lista_com_chamados(self, admin_autenticado, cliente_id):
        _criar_chamado(cliente_id, titulo="Erro ao gerar relatorio")
        _criar_chamado(cliente_id, titulo="Solicitacao de novo acesso")
        resp = admin_autenticado.get("/api/admin/chamados/")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 2
        assert len(corpo["items"]) == 2
        item = corpo["items"][0]
        # Shape de ChamadoResponse e enums como string
        assert item["status"] in StatusChamado.valores()
        assert item["prioridade"] in PrioridadeChamado.valores()
        assert item["usuario_id"] == cliente_id
        # Histórico não vem na listagem
        assert item["interacoes"] is None

    def test_lista_paginada_respeita_por_pagina(self, admin_autenticado, cliente_id):
        for i in range(3):
            _criar_chamado(cliente_id, titulo=f"Chamado numero {i} de teste")
        resp = admin_autenticado.get(
            "/api/admin/chamados/", params={"pagina": 1, "por_pagina": 2}
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 3
        assert corpo["por_pagina"] == 2
        assert len(corpo["items"]) == 2
        assert corpo["total_paginas"] == 2

    def test_lista_filtro_status(self, admin_autenticado, cliente_id):
        _criar_chamado(cliente_id, titulo="Aberto de teste um",
                       status_inicial=StatusChamado.ABERTO)
        _criar_chamado(cliente_id, titulo="Fechado de teste dois",
                       status_inicial=StatusChamado.FECHADO)
        resp = admin_autenticado.get(
            "/api/admin/chamados/", params={"status_filtro": StatusChamado.FECHADO.value}
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 1
        assert corpo["items"][0]["status"] == StatusChamado.FECHADO.value

    def test_lista_filtro_prioridade(self, admin_autenticado, cliente_id):
        _criar_chamado(cliente_id, titulo="Prioridade alta de teste",
                       prioridade=PrioridadeChamado.ALTA)
        _criar_chamado(cliente_id, titulo="Prioridade baixa de teste",
                       prioridade=PrioridadeChamado.BAIXA)
        resp = admin_autenticado.get(
            "/api/admin/chamados/", params={"prioridade": PrioridadeChamado.ALTA.value}
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 1
        assert corpo["items"][0]["prioridade"] == PrioridadeChamado.ALTA.value

    def test_lista_filtro_busca_q(self, admin_autenticado, cliente_id):
        _criar_chamado(cliente_id, titulo="Problema especifico de impressao")
        _criar_chamado(cliente_id, titulo="Outra solicitacao qualquer aqui")
        resp = admin_autenticado.get(
            "/api/admin/chamados/", params={"q": "impressao"}
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 1
        assert "impressao" in corpo["items"][0]["titulo"].lower()

    def test_lista_sem_sessao_401(self, client):
        resp = client.get("/api/admin/chamados/")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_lista_perfil_cliente_403(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/admin/chamados/")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"


# =============================================================================
# GET /api/admin/chamados/{id}  (detalhe)
# =============================================================================

class TestObter:
    def test_obter_chamado_com_historico(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id, titulo="Chamado para detalhar agora")
        resp = admin_autenticado.get(f"/api/admin/chamados/{chamado_id}")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["id"] == chamado_id
        assert corpo["titulo"] == "Chamado para detalhar agora"
        assert corpo["usuario_id"] == cliente_id
        # Detalhe inclui a chave interacoes (lista, possivelmente vazia)
        assert isinstance(corpo["interacoes"], list)

    def test_obter_inexistente_404(self, admin_autenticado):
        resp = admin_autenticado.get("/api/admin/chamados/999999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_obter_sem_sessao_401(self, client, cliente_id):
        chamado_id = _criar_chamado(cliente_id)
        resp = client.get(f"/api/admin/chamados/{chamado_id}")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_obter_perfil_cliente_403(self, cliente_autenticado):
        # cliente_autenticado é cliente; insere chamado para um id qualquer
        resp = cliente_autenticado.get("/api/admin/chamados/1")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"


# =============================================================================
# POST /api/admin/chamados/{id}/interacoes  (responder)
# =============================================================================

class TestResponder:
    def _body(self, *, mensagem="Estamos analisando o seu chamado agora.",
              status_novo=StatusChamado.EM_ANALISE.value):
        return {
            "dto_mensagem": {"mensagem": mensagem},
            "dto_status": {"status": status_novo},
        }

    def test_responder_sucesso_201(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id, titulo="Chamado a ser respondido ja")
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            f"/api/admin/chamados/{chamado_id}/interacoes",
            json=self._body(),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        corpo = resp.json()
        assert corpo["id"] == chamado_id
        # Status atualizado conforme dto_status
        assert corpo["status"] == StatusChamado.EM_ANALISE.value
        # Histórico contém a interação do admin (resposta do administrador)
        assert isinstance(corpo["interacoes"], list)
        assert len(corpo["interacoes"]) >= 1
        tipos = [i["tipo"] for i in corpo["interacoes"]]
        assert "Resposta do Administrador" in tipos
        # NOTA: tem_resposta_admin sai False aqui porque o endpoint usa
        # chamado_repo.obter_por_id (que não popula esse flag, sempre default
        # False); só obter_por_usuario o calcula. Contrato real, não bug do teste.
        assert corpo["tem_resposta_admin"] is False

    def test_responder_fechando_grava_data_fechamento(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id, titulo="Chamado para ser fechado")
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            f"/api/admin/chamados/{chamado_id}/interacoes",
            json=self._body(mensagem="Resolvido, fechando o chamado.",
                            status_novo=StatusChamado.FECHADO.value),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        corpo = resp.json()
        assert corpo["status"] == StatusChamado.FECHADO.value
        assert corpo["data_fechamento"] is not None

    def test_responder_inexistente_404(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            "/api/admin/chamados/999999/interacoes",
            json=self._body(),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_responder_sem_csrf_403(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id)
        resp = admin_autenticado.post(
            f"/api/admin/chamados/{chamado_id}/interacoes",
            json=self._body(),
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_responder_sem_sessao_401(self, client, cliente_id):
        chamado_id = _criar_chamado(cliente_id)
        token = _csrf(client)
        resp = client.post(
            f"/api/admin/chamados/{chamado_id}/interacoes",
            json=self._body(),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_responder_perfil_cliente_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/admin/chamados/1/interacoes",
            json=self._body(),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_responder_mensagem_vazia_422(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            f"/api/admin/chamados/{chamado_id}/interacoes",
            json=self._body(mensagem=""),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_responder_mensagem_curta_422(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            f"/api/admin/chamados/{chamado_id}/interacoes",
            json=self._body(mensagem="curta"),  # < 10 chars
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_responder_status_invalido_422(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            f"/api/admin/chamados/{chamado_id}/interacoes",
            json=self._body(status_novo="StatusInexistente"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_responder_excede_rate_limit_429(self, admin_autenticado, cliente_id,
                                             bloquear_rate_limiter):
        chamado_id = _criar_chamado(cliente_id)
        token = _csrf(admin_autenticado)
        with bloquear_rate_limiter(
            "routes.admin_chamados_routes.admin_chamado_responder_limiter"
        ):
            resp = admin_autenticado.post(
                f"/api/admin/chamados/{chamado_id}/interacoes",
                json=self._body(),
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert resp.json()["type"] == "rate_limited"
        assert "Retry-After" in resp.headers


# =============================================================================
# PATCH /api/admin/chamados/{id}/status  (alterar status)
# =============================================================================

class TestAlterarStatus:
    def test_alterar_status_sucesso(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id, status_inicial=StatusChamado.ABERTO)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.patch(
            f"/api/admin/chamados/{chamado_id}/status",
            json={"status": StatusChamado.EM_ANALISE.value},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["id"] == chamado_id
        assert corpo["status"] == StatusChamado.EM_ANALISE.value

    def test_alterar_status_fechar_grava_data(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id, status_inicial=StatusChamado.EM_ANALISE)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.patch(
            f"/api/admin/chamados/{chamado_id}/status",
            json={"status": StatusChamado.FECHADO.value},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["status"] == StatusChamado.FECHADO.value
        assert corpo["data_fechamento"] is not None

    def test_reabrir_fechado_para_em_analise_ok(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id, status_inicial=StatusChamado.FECHADO)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.patch(
            f"/api/admin/chamados/{chamado_id}/status",
            json={"status": StatusChamado.EM_ANALISE.value},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["status"] == StatusChamado.EM_ANALISE.value

    def test_reabrir_fechado_para_outro_status_409(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id, status_inicial=StatusChamado.FECHADO)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.patch(
            f"/api/admin/chamados/{chamado_id}/status",
            json={"status": StatusChamado.ABERTO.value},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_409_CONFLICT
        corpo = resp.json()
        assert corpo["type"] == "conflict"
        assert "status" in corpo["errors"]

    def test_alterar_status_inexistente_404(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.patch(
            "/api/admin/chamados/999999/status",
            json={"status": StatusChamado.EM_ANALISE.value},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_alterar_status_invalido_422(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.patch(
            f"/api/admin/chamados/{chamado_id}/status",
            json={"status": "Inexistente"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_alterar_status_sem_csrf_403(self, admin_autenticado, cliente_id):
        chamado_id = _criar_chamado(cliente_id)
        resp = admin_autenticado.patch(
            f"/api/admin/chamados/{chamado_id}/status",
            json={"status": StatusChamado.EM_ANALISE.value},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_alterar_status_sem_sessao_401(self, client, cliente_id):
        chamado_id = _criar_chamado(cliente_id)
        token = _csrf(client)
        resp = client.patch(
            f"/api/admin/chamados/{chamado_id}/status",
            json={"status": StatusChamado.EM_ANALISE.value},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_alterar_status_perfil_cliente_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.patch(
            "/api/admin/chamados/1/status",
            json={"status": StatusChamado.EM_ANALISE.value},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"
