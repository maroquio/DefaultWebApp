"""
Testes de endpoint do módulo de chamados de usuário (routes/chamados_routes.py).

Cobre caminhos felizes e tristes de (prefixo /api/chamados):
    GET    /api/chamados/                 -> lista paginada (PaginaResponse)
    POST   /api/chamados/                 -> abre chamado (201)
    GET    /api/chamados/{id}             -> detalhe com interações
    POST   /api/chamados/{id}/interacoes  -> responder ao chamado (201)
    DELETE /api/chamados/{id}             -> excluir (204)

Contrato (ver CLAUDE.md / contexto compartilhado):
    - Sucesso: recurso puro com status correto (200/201) ou 204 sem corpo.
    - Erro: {detail, type, errors}.
    - @requer_autenticacao() sem sessão -> 401 (type unauthorized).
    - Mutação sem header X-CSRF-Token -> 403 (type forbidden).
    - Recurso inexistente -> 404 (type not_found).
    - Acesso a chamado de OUTRO usuário (não-admin) -> 403 (type forbidden)
      [regra real: chamado.usuario_id != usuario.id and not is_admin()].
    - Validação Pydantic -> 422 (type validation_error).
    - Conflito (excluir não-aberto / com resposta admin) -> 409 (type conflict).
    - Rate limit -> 429 (chamado_criar_limiter / chamado_responder_limiter).
"""
import pytest
from fastapi import status

from util.perfis import Perfil


pytestmark = [pytest.mark.integration, pytest.mark.crud]


def _csrf(client):
    """Obtém um token CSRF válido para a sessão do cliente."""
    return client.get("/api/csrf-token").json()["token"]


def _criar_chamado(client, titulo="Titulo de chamado valido",
                   descricao="Descricao detalhada do problema relatado.",
                   prioridade="Média"):
    """Cria um chamado via endpoint (caminho feliz) e retorna a Response."""
    token = _csrf(client)
    return client.post(
        "/api/chamados/",
        json={"titulo": titulo, "descricao": descricao, "prioridade": prioridade},
        headers={"X-CSRF-Token": token},
    )


def _login(client, email, senha):
    token = _csrf(client)
    return client.post("/api/login", json={"email": email, "senha": senha},
                       headers={"X-CSRF-Token": token})


# =============================================================================
# POST /api/chamados/  (criação)
# =============================================================================

class TestCriarChamado:
    def test_criar_sucesso_201(self, cliente_autenticado):
        resp = _criar_chamado(cliente_autenticado)
        assert resp.status_code == status.HTTP_201_CREATED
        corpo = resp.json()
        assert corpo["titulo"] == "Titulo de chamado valido"
        assert corpo["status"] == "Aberto"
        assert corpo["prioridade"] == "Média"
        assert "id" in corpo
        # A criação retorna o detalhe com a interação inicial (Abertura).
        assert corpo["interacoes"] is not None
        assert len(corpo["interacoes"]) == 1
        assert corpo["interacoes"][0]["tipo"] == "Abertura"
        assert corpo["interacoes"][0]["mensagem"] == (
            "Descricao detalhada do problema relatado."
        )

    def test_prioridade_default_media(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chamados/",
            json={
                "titulo": "Chamado sem prioridade",
                "descricao": "Descricao detalhada o suficiente aqui.",
            },
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.json()["prioridade"] == "Média"

    def test_criar_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.post(
            "/api/chamados/",
            json={"titulo": "Titulo qualquer valido", "descricao": "Descricao com tamanho ok aqui."},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_criar_sem_csrf_403(self, cliente_autenticado):
        resp = cliente_autenticado.post(
            "/api/chamados/",
            json={"titulo": "Titulo qualquer valido", "descricao": "Descricao com tamanho ok aqui."},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_titulo_curto_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chamados/",
            json={"titulo": "curto", "descricao": "Descricao com tamanho suficiente aqui."},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_descricao_curta_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chamados/",
            json={"titulo": "Titulo valido aqui", "descricao": "curta"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_prioridade_invalida_422(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chamados/",
            json={
                "titulo": "Titulo valido aqui",
                "descricao": "Descricao detalhada o suficiente aqui.",
                "prioridade": "Inexistente",
            },
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_excede_rate_limit_429(self, cliente_autenticado, bloquear_rate_limiter):
        token = _csrf(cliente_autenticado)
        with bloquear_rate_limiter("routes.chamados_routes.chamado_criar_limiter"):
            resp = cliente_autenticado.post(
                "/api/chamados/",
                json={
                    "titulo": "Titulo valido aqui",
                    "descricao": "Descricao detalhada o suficiente aqui.",
                },
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert resp.json()["type"] == "rate_limited"
        assert "Retry-After" in resp.headers


# =============================================================================
# GET /api/chamados/  (listagem paginada)
# =============================================================================

class TestListarChamados:
    def test_lista_vazia_shape_pagina(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/chamados/")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert set(corpo.keys()) >= {
            "items", "pagina", "por_pagina", "total", "total_paginas"
        }
        assert corpo["items"] == []
        assert corpo["total"] == 0
        assert corpo["pagina"] == 1

    def test_lista_apos_criar(self, cliente_autenticado):
        _criar_chamado(cliente_autenticado, titulo="Primeiro chamado teste")
        _criar_chamado(cliente_autenticado, titulo="Segundo chamado teste")
        resp = cliente_autenticado.get("/api/chamados/")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 2
        assert len(corpo["items"]) == 2
        # Listagem não carrega o histórico de interações.
        assert corpo["items"][0]["interacoes"] is None

    def test_paginacao_por_pagina(self, cliente_autenticado):
        for i in range(3):
            _criar_chamado(cliente_autenticado, titulo=f"Chamado numero {i} aqui")
        resp = cliente_autenticado.get("/api/chamados/?pagina=1&por_pagina=2")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 3
        assert corpo["por_pagina"] == 2
        assert len(corpo["items"]) == 2
        assert corpo["total_paginas"] == 2

    def test_filtro_status(self, cliente_autenticado):
        _criar_chamado(cliente_autenticado, titulo="Chamado aberto filtro")
        resp = cliente_autenticado.get("/api/chamados/?status_filtro=Aberto")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["total"] == 1
        resp2 = cliente_autenticado.get("/api/chamados/?status_filtro=Fechado")
        assert resp2.json()["total"] == 0

    def test_filtro_prioridade(self, cliente_autenticado):
        _criar_chamado(cliente_autenticado, titulo="Chamado prioridade alta", prioridade="Alta")
        resp = cliente_autenticado.get("/api/chamados/?prioridade=Alta")
        assert resp.json()["total"] == 1
        assert resp.json()["items"][0]["prioridade"] == "Alta"

    def test_filtro_busca_titulo(self, cliente_autenticado):
        _criar_chamado(cliente_autenticado, titulo="Problema com login aqui")
        _criar_chamado(cliente_autenticado, titulo="Outro assunto qualquer aqui")
        resp = cliente_autenticado.get("/api/chamados/?q=login")
        assert resp.json()["total"] == 1

    def test_lista_isola_por_usuario(self, cliente_autenticado, dois_usuarios):
        """Cada usuário só vê os próprios chamados."""
        # cliente_autenticado é usuario_teste (sessão ativa); cria 1 chamado.
        _criar_chamado(cliente_autenticado, titulo="Chamado do dono aqui")
        # Loga como outro usuário no MESMO client (substitui a sessão).
        u1, _ = dois_usuarios
        _login(cliente_autenticado, u1["email"], u1["senha"])
        resp = cliente_autenticado.get("/api/chamados/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["total"] == 0

    def test_lista_sem_sessao_401(self, client):
        resp = client.get("/api/chamados/")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# GET /api/chamados/{id}  (detalhe)
# =============================================================================

class TestObterChamado:
    def test_obter_proprio_sucesso(self, cliente_autenticado):
        criado = _criar_chamado(cliente_autenticado).json()
        resp = cliente_autenticado.get(f"/api/chamados/{criado['id']}")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["id"] == criado["id"]
        assert corpo["interacoes"] is not None
        assert len(corpo["interacoes"]) == 1

    def test_obter_inexistente_404(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/chamados/999999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_obter_de_outro_usuario_403(self, cliente_autenticado, dois_usuarios):
        """Acesso a chamado de outro usuário (não-admin) -> 403."""
        criado = _criar_chamado(cliente_autenticado).json()
        u1, _ = dois_usuarios
        _login(cliente_autenticado, u1["email"], u1["senha"])
        resp = cliente_autenticado.get(f"/api/chamados/{criado['id']}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_obter_de_outro_usuario_admin_pode(self, cliente_autenticado, admin_teste):
        """Admin acessa chamado de qualquer usuário (regra: not is_admin())."""
        from repo import usuario_repo
        from model.usuario_model import Usuario
        from util.security import criar_hash_senha

        criado = _criar_chamado(cliente_autenticado).json()
        # Cria admin direto no banco e loga no mesmo client.
        usuario_repo.inserir(Usuario(
            id=0, nome=admin_teste["nome"], email=admin_teste["email"],
            senha=criar_hash_senha(admin_teste["senha"]), perfil=Perfil.ADMIN.value,
        ))
        _login(cliente_autenticado, admin_teste["email"], admin_teste["senha"])
        resp = cliente_autenticado.get(f"/api/chamados/{criado['id']}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["id"] == criado["id"]

    def test_obter_sem_sessao_401(self, client):
        resp = client.get("/api/chamados/1")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"


# =============================================================================
# POST /api/chamados/{id}/interacoes  (responder)
# =============================================================================

class TestResponderChamado:
    def test_responder_proprio_sucesso_201(self, cliente_autenticado):
        criado = _criar_chamado(cliente_autenticado).json()
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            f"/api/chamados/{criado['id']}/interacoes",
            json={"mensagem": "Esta e a minha resposta ao chamado."},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        corpo = resp.json()
        # Abertura + resposta.
        assert len(corpo["interacoes"]) == 2
        ultima = corpo["interacoes"][-1]
        assert ultima["tipo"] == "Resposta do Usuário"
        assert ultima["mensagem"] == "Esta e a minha resposta ao chamado."

    def test_responder_inexistente_404(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            "/api/chamados/999999/interacoes",
            json={"mensagem": "Mensagem de resposta valida aqui."},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_responder_de_outro_usuario_403(self, cliente_autenticado, dois_usuarios):
        criado = _criar_chamado(cliente_autenticado).json()
        u1, _ = dois_usuarios
        _login(cliente_autenticado, u1["email"], u1["senha"])
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            f"/api/chamados/{criado['id']}/interacoes",
            json={"mensagem": "Tentando responder chamado alheio."},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_responder_sem_csrf_403(self, cliente_autenticado):
        criado = _criar_chamado(cliente_autenticado).json()
        resp = cliente_autenticado.post(
            f"/api/chamados/{criado['id']}/interacoes",
            json={"mensagem": "Resposta sem token csrf aqui."},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_responder_mensagem_curta_422(self, cliente_autenticado):
        criado = _criar_chamado(cliente_autenticado).json()
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post(
            f"/api/chamados/{criado['id']}/interacoes",
            json={"mensagem": "curta"},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_responder_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.post(
            "/api/chamados/1/interacoes",
            json={"mensagem": "Mensagem de resposta valida aqui."},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_responder_excede_rate_limit_429(self, cliente_autenticado, bloquear_rate_limiter):
        criado = _criar_chamado(cliente_autenticado).json()
        token = _csrf(cliente_autenticado)
        with bloquear_rate_limiter("routes.chamados_routes.chamado_responder_limiter"):
            resp = cliente_autenticado.post(
                f"/api/chamados/{criado['id']}/interacoes",
                json={"mensagem": "Resposta valida com tamanho ok."},
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert resp.json()["type"] == "rate_limited"
        assert "Retry-After" in resp.headers


# =============================================================================
# DELETE /api/chamados/{id}  (exclusão)
# =============================================================================

class TestExcluirChamado:
    def test_excluir_aberto_sucesso_204(self, cliente_autenticado):
        criado = _criar_chamado(cliente_autenticado).json()
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.delete(
            f"/api/chamados/{criado['id']}",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert resp.content == b""
        # Confirma que sumiu.
        assert cliente_autenticado.get(
            f"/api/chamados/{criado['id']}"
        ).status_code == status.HTTP_404_NOT_FOUND

    def test_excluir_inexistente_404(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.delete(
            "/api/chamados/999999",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_excluir_de_outro_usuario_403(self, cliente_autenticado, dois_usuarios):
        criado = _criar_chamado(cliente_autenticado).json()
        u1, _ = dois_usuarios
        _login(cliente_autenticado, u1["email"], u1["senha"])
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.delete(
            f"/api/chamados/{criado['id']}",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_excluir_sem_csrf_403(self, cliente_autenticado):
        criado = _criar_chamado(cliente_autenticado).json()
        resp = cliente_autenticado.delete(f"/api/chamados/{criado['id']}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_excluir_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.delete("/api/chamados/1", headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_excluir_status_nao_aberto_409(self, cliente_autenticado):
        """Apenas chamados abertos podem ser excluídos -> 409 conflict."""
        from repo import chamado_repo
        from model.chamado_model import StatusChamado

        criado = _criar_chamado(cliente_autenticado).json()
        # Altera status direto no banco para um valor != Aberto.
        chamado_repo.atualizar_status(criado["id"], StatusChamado.EM_ANALISE.value)

        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.delete(
            f"/api/chamados/{criado['id']}",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_409_CONFLICT
        assert resp.json()["type"] == "conflict"

    def test_excluir_com_resposta_admin_409(self, cliente_autenticado):
        """Chamado aberto mas com resposta de admin não pode ser excluído -> 409."""
        from repo import chamado_interacao_repo
        from model.chamado_interacao_model import ChamadoInteracao, TipoInteracao
        from model.chamado_model import StatusChamado
        from util.datetime_util import agora

        criado = _criar_chamado(cliente_autenticado).json()
        # Insere uma interação do tipo Resposta do Administrador direto no banco
        # (mantendo o status Aberto para exercitar especificamente esta regra).
        chamado_interacao_repo.inserir(ChamadoInteracao(
            id=0,
            chamado_id=criado["id"],
            usuario_id=criado["usuario_id"],
            mensagem="Resposta do administrador ao chamado.",
            tipo=TipoInteracao.RESPOSTA_ADMIN,
            data_interacao=agora(),
            status_resultante=StatusChamado.ABERTO.value,
        ))

        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.delete(
            f"/api/chamados/{criado['id']}",
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_409_CONFLICT
        assert resp.json()["type"] == "conflict"
