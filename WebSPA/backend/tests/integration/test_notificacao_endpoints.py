"""
Testes de endpoint do módulo de notificações in-app (routes/notificacao_routes.py).

Cobre caminhos felizes e tristes de (todos sob /api/notificacoes):
    GET    /api/notificacoes/            → lista paginada das notificações do usuário
    GET    /api/notificacoes/nao-lidas   → contagem + resumo das não lidas
    PATCH  /api/notificacoes/marcar-todas → marca todas como lidas
    PATCH  /api/notificacoes/{id}/lida   → marca uma como lida
    DELETE /api/notificacoes/lidas       → exclui todas as lidas
    DELETE /api/notificacoes/{id}        → exclui uma específica (204)

Contrato (ver CLAUDE.md):
    - GET → 200; PATCH → 200; DELETE de recurso → 204 sem corpo;
      ação sem recurso (marcar-todas, excluir-lidas) → 200 MensagemResponse.
    - @requer_autenticacao() sem sessão → 401 (type="unauthorized").
    - Mutações sem header X-CSRF-Token → 403 (type="forbidden").
    - Notificação inexistente ou de OUTRO usuário → 404 (isolamento de propriedade).
    - Paginação: PaginaResponse[T] = {items, pagina, por_pagina, total, total_paginas}.

⚠️ A tabela `notificacao` NÃO é limpa pelo conftest — limpamos via fixture autouse.
"""
import pytest
from fastapi import status

from model.notificacao_model import TipoNotificacao
from util.notificacao_util import criar_notificacao
from util.perfis import Perfil


pytestmark = [pytest.mark.integration, pytest.mark.crud]


def _csrf(client):
    """Obtém um token CSRF válido para a sessão do cliente."""
    return client.get("/api/csrf-token").json()["token"]


@pytest.fixture(autouse=True)
def _limpar_notificacoes():
    """A tabela `notificacao` não é limpa pelo conftest; limpamos aqui."""
    from util.db_util import obter_conexao

    def limpa():
        with obter_conexao() as conn:
            # A tabela pode ainda não existir na primeira coleta; protege com try.
            try:
                conn.execute("DELETE FROM notificacao")
            except Exception:
                pass

    limpa()
    yield
    limpa()


@pytest.fixture
def usuario_logado_id(cliente_autenticado):
    """ID do usuário autenticado pelo fixture `cliente_autenticado` (via /api/me)."""
    resp = cliente_autenticado.get("/api/me")
    assert resp.status_code == status.HTTP_200_OK
    return resp.json()["id"]


def _criar(usuario_id, titulo="Aviso", mensagem="Mensagem de teste",
           tipo=TipoNotificacao.INFO, url_acao=None):
    """Cria uma notificação direto via util e retorna o ID."""
    nid = criar_notificacao(
        usuario_id=usuario_id,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo,
        url_acao=url_acao,
    )
    assert nid is not None
    return nid


# =============================================================================
# GET /api/notificacoes/  (listagem paginada)
# =============================================================================

class TestListar:
    def test_lista_vazia_retorna_pagina_vazia(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/notificacoes/")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["items"] == []
        assert corpo["total"] == 0
        assert corpo["pagina"] == 1
        assert corpo["por_pagina"] == 15
        assert corpo["total_paginas"] in (0, 1)

    def test_lista_com_notificacoes(self, cliente_autenticado, usuario_logado_id):
        _criar(usuario_logado_id, titulo="Primeira")
        _criar(usuario_logado_id, titulo="Segunda", tipo=TipoNotificacao.SUCESSO,
               url_acao="/destino")

        resp = cliente_autenticado.get("/api/notificacoes/")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 2
        assert len(corpo["items"]) == 2
        item = corpo["items"][0]
        # Shape do NotificacaoResponse
        for campo in ("id", "usuario_id", "titulo", "mensagem", "tipo", "lida"):
            assert campo in item
        assert item["usuario_id"] == usuario_logado_id
        assert item["lida"] is False
        # Enum serializado como string do valor
        tipos = {i["tipo"] for i in corpo["items"]}
        assert tipos <= {"info", "sucesso", "aviso", "erro"}
        assert "sucesso" in tipos

    def test_paginacao_segunda_pagina(self, cliente_autenticado, usuario_logado_id):
        # 15 por página → criar 16 para forçar 2 páginas
        for i in range(16):
            _criar(usuario_logado_id, titulo=f"N{i}")
        resp = cliente_autenticado.get("/api/notificacoes/?pagina=2")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["pagina"] == 2
        assert corpo["total"] == 16
        assert corpo["total_paginas"] == 2
        assert len(corpo["items"]) == 1

    def test_isolamento_nao_ve_notificacao_de_outro(
        self, cliente_autenticado, usuario_logado_id, criar_usuario_direto
    ):
        outro_id = criar_usuario_direto("Outro", "outro@example.com", "Senha@123")
        _criar(outro_id, titulo="Do outro usuário")

        resp = cliente_autenticado.get("/api/notificacoes/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["total"] == 0

    def test_sem_sessao_401(self, client):
        resp = client.get("/api/notificacoes/")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# GET /api/notificacoes/nao-lidas
# =============================================================================

class TestNaoLidas:
    def test_zero_quando_vazio(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/notificacoes/nao-lidas")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 0
        assert corpo["items"] == []

    def test_conta_e_resume_nao_lidas(self, cliente_autenticado, usuario_logado_id):
        for i in range(3):
            _criar(usuario_logado_id, titulo=f"N{i}")
        resp = cliente_autenticado.get("/api/notificacoes/nao-lidas")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 3
        assert len(corpo["items"]) == 3
        # Shape do NotificacaoResumoResponse (sem 'lida' nem 'usuario_id')
        item = corpo["items"][0]
        for campo in ("id", "titulo", "mensagem", "tipo"):
            assert campo in item
        assert "lida" not in item

    def test_resumo_limitado_a_cinco(self, cliente_autenticado, usuario_logado_id):
        for i in range(7):
            _criar(usuario_logado_id, titulo=f"N{i}")
        resp = cliente_autenticado.get("/api/notificacoes/nao-lidas")
        corpo = resp.json()
        assert corpo["total"] == 7  # contador total
        assert len(corpo["items"]) == 5  # resumo limitado a 5

    def test_isolamento(self, cliente_autenticado, usuario_logado_id, criar_usuario_direto):
        outro_id = criar_usuario_direto("Outro", "outro@example.com", "Senha@123")
        _criar(outro_id, titulo="Do outro")
        resp = cliente_autenticado.get("/api/notificacoes/nao-lidas")
        assert resp.json()["total"] == 0

    def test_sem_sessao_401(self, client):
        resp = client.get("/api/notificacoes/nao-lidas")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# PATCH /api/notificacoes/{id}/lida
# =============================================================================

class TestMarcarLida:
    def test_marca_como_lida_muda_estado(self, cliente_autenticado, usuario_logado_id):
        nid = _criar(usuario_logado_id, titulo="Para ler")
        # Confirma que está como não lida
        assert cliente_autenticado.get("/api/notificacoes/nao-lidas").json()["total"] == 1

        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.patch(
            f"/api/notificacoes/{nid}/lida", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["id"] == nid
        assert corpo["lida"] is True

        # Contador de não lidas deve ter zerado
        assert cliente_autenticado.get("/api/notificacoes/nao-lidas").json()["total"] == 0

    def test_sem_sessao_401(self, client):
        # Com CSRF válido mas sem sessão → 401 (CSRF passa, auth falha).
        token = _csrf(client)
        resp = client.patch("/api/notificacoes/1/lida", headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_sem_csrf_403(self, cliente_autenticado, usuario_logado_id):
        nid = _criar(usuario_logado_id)
        resp = cliente_autenticado.patch(f"/api/notificacoes/{nid}/lida")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_inexistente_404(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.patch(
            "/api/notificacoes/999999/lida", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_de_outro_usuario_404(
        self, cliente_autenticado, criar_usuario_direto
    ):
        outro_id = criar_usuario_direto("Outro", "outro@example.com", "Senha@123")
        nid = _criar(outro_id, titulo="Do outro")
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.patch(
            f"/api/notificacoes/{nid}/lida", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"


# =============================================================================
# PATCH /api/notificacoes/marcar-todas
# =============================================================================

class TestMarcarTodas:
    def test_marca_todas_lidas(self, cliente_autenticado, usuario_logado_id):
        for i in range(3):
            _criar(usuario_logado_id, titulo=f"N{i}")
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.patch(
            "/api/notificacoes/marcar-todas", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert "message" in resp.json()
        assert "3" in resp.json()["message"]
        # Nenhuma não lida restante
        assert cliente_autenticado.get("/api/notificacoes/nao-lidas").json()["total"] == 0

    def test_sem_nada_para_marcar_mensagem(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.patch(
            "/api/notificacoes/marcar-todas", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert "message" in resp.json()

    def test_nao_afeta_outro_usuario(
        self, cliente_autenticado, usuario_logado_id, criar_usuario_direto
    ):
        outro_id = criar_usuario_direto("Outro", "outro@example.com", "Senha@123")
        _criar(outro_id, titulo="Do outro")
        _criar(usuario_logado_id, titulo="Minha")

        token = _csrf(cliente_autenticado)
        cliente_autenticado.patch(
            "/api/notificacoes/marcar-todas", headers={"X-CSRF-Token": token}
        )
        # A notificação do outro usuário permanece não lida
        assert _nao_lidas_do_usuario(outro_id) == 1

    def test_sem_csrf_403(self, cliente_autenticado):
        resp = cliente_autenticado.patch("/api/notificacoes/marcar-todas")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.patch(
            "/api/notificacoes/marcar-todas", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# DELETE /api/notificacoes/lidas
# =============================================================================

class TestExcluirLidas:
    def test_exclui_apenas_lidas(self, cliente_autenticado, usuario_logado_id):
        lida = _criar(usuario_logado_id, titulo="Lida")
        _criar(usuario_logado_id, titulo="Nao lida")

        token = _csrf(cliente_autenticado)
        # Marca a primeira como lida
        cliente_autenticado.patch(
            f"/api/notificacoes/{lida}/lida", headers={"X-CSRF-Token": token}
        )

        resp = cliente_autenticado.delete(
            "/api/notificacoes/lidas", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert "message" in resp.json()
        assert "1" in resp.json()["message"]

        # Sobra apenas a não lida
        corpo = cliente_autenticado.get("/api/notificacoes/").json()
        assert corpo["total"] == 1
        assert corpo["items"][0]["titulo"] == "Nao lida"

    def test_sem_lidas_mensagem(self, cliente_autenticado, usuario_logado_id):
        _criar(usuario_logado_id, titulo="Nao lida")
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.delete(
            "/api/notificacoes/lidas", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_200_OK
        assert "message" in resp.json()
        # Notificação não lida permanece
        assert cliente_autenticado.get("/api/notificacoes/").json()["total"] == 1

    def test_nao_afeta_outro_usuario(
        self, cliente_autenticado, criar_usuario_direto
    ):
        outro_id = criar_usuario_direto("Outro", "outro@example.com", "Senha@123")
        # Cria e marca como lida no banco diretamente para o outro usuário
        nid = _criar(outro_id, titulo="Do outro")
        from repo import notificacao_repo
        notificacao_repo.marcar_como_lida(nid, outro_id)

        token = _csrf(cliente_autenticado)
        cliente_autenticado.delete(
            "/api/notificacoes/lidas", headers={"X-CSRF-Token": token}
        )
        # A do outro usuário continua existindo
        assert len(notificacao_repo.obter_por_usuario(outro_id)) == 1

    def test_sem_csrf_403(self, cliente_autenticado):
        resp = cliente_autenticado.delete("/api/notificacoes/lidas")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.delete(
            "/api/notificacoes/lidas", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# DELETE /api/notificacoes/{id}
# =============================================================================

class TestExcluir:
    def test_exclui_retorna_204(self, cliente_autenticado, usuario_logado_id):
        nid = _criar(usuario_logado_id, titulo="Excluir")
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.delete(
            f"/api/notificacoes/{nid}", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert resp.content == b""  # 204 sem corpo
        # Some da listagem
        assert cliente_autenticado.get("/api/notificacoes/").json()["total"] == 0

    def test_inexistente_404(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.delete(
            "/api/notificacoes/999999", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_de_outro_usuario_404(
        self, cliente_autenticado, criar_usuario_direto
    ):
        outro_id = criar_usuario_direto("Outro", "outro@example.com", "Senha@123")
        nid = _criar(outro_id, titulo="Do outro")
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.delete(
            f"/api/notificacoes/{nid}", headers={"X-CSRF-Token": token}
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"
        # E a notificação do outro continua existindo
        from repo import notificacao_repo
        assert len(notificacao_repo.obter_por_usuario(outro_id)) == 1

    def test_sem_csrf_403(self, cliente_autenticado, usuario_logado_id):
        nid = _criar(usuario_logado_id)
        resp = cliente_autenticado.delete(f"/api/notificacoes/{nid}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.delete("/api/notificacoes/1", headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# Helper de verificação direta no banco (isolamento entre usuários)
# =============================================================================

def _nao_lidas_do_usuario(usuario_id: int) -> int:
    from repo import notificacao_repo
    return notificacao_repo.contar_nao_lidas(usuario_id)
