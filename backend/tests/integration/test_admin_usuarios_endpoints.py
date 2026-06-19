"""
Testes de endpoint do módulo de administração de usuários
(routes/admin_usuarios_routes.py).

Cobre caminhos felizes e tristes de (todos sob /api/admin/usuarios, ADMIN-only):
    GET    /api/admin/usuarios/         (paginado, filtros perfil e q)
    GET    /api/admin/usuarios/{id}
    POST   /api/admin/usuarios/
    PUT    /api/admin/usuarios/{id}
    DELETE /api/admin/usuarios/{id}

Contrato (ver CLAUDE.md):
    - Sucesso: GET único→200, lista→200 PaginaResponse, POST→201, PUT→200, DELETE→204.
    - Erro: {detail, type, errors} via util/exception_handlers.py.
    - Mutações exigem header X-CSRF-Token (senão 403, type="forbidden").
    - Sessão por cookie; @requer_autenticacao([ADMIN]) → 401 sem sessão, 403 perfil errado.
"""
import pytest
from fastapi import status

from util.perfis import Perfil


pytestmark = [pytest.mark.integration, pytest.mark.crud]


def _csrf(client):
    """Obtém um token CSRF válido para a sessão do cliente."""
    return client.get("/api/csrf-token").json()["token"]


def _id_do_admin(admin_autenticado):
    """Descobre o id do admin logado via GET /api/me."""
    return admin_autenticado.get("/api/me").json()["id"]


# =============================================================================
# GET /api/admin/usuarios/  (listagem paginada)
# =============================================================================

class TestListar:
    def test_lista_sem_sessao_401(self, client):
        resp = client.get("/api/admin/usuarios/")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_lista_perfil_nao_admin_403(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/admin/usuarios/")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_lista_sucesso_shape_pagina(self, admin_autenticado):
        resp = admin_autenticado.get("/api/admin/usuarios/")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        # PaginaResponse[T]
        assert set(corpo.keys()) >= {
            "items", "pagina", "por_pagina", "total", "total_paginas"
        }
        assert isinstance(corpo["items"], list)
        # o próprio admin já existe no banco
        assert corpo["total"] >= 1
        # schema do item nunca expõe senha
        item = corpo["items"][0]
        assert "senha" not in item
        assert {"id", "nome", "email", "perfil", "foto_url"} <= set(item.keys())

    def test_paginacao_multiplos_usuarios(self, admin_autenticado, criar_usuario_direto):
        # admin já no banco (1) + 14 criados = 15; por_pagina=5 → 3 páginas
        for i in range(14):
            criar_usuario_direto(
                f"Usuario {i}", f"user{i}@example.com", "Senha@123",
                Perfil.CLIENTE.value,
            )
        resp = admin_autenticado.get("/api/admin/usuarios/?pagina=1&por_pagina=5")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 15
        assert corpo["por_pagina"] == 5
        assert corpo["pagina"] == 1
        assert corpo["total_paginas"] == 3
        assert len(corpo["items"]) == 5

        # última página tem o resto (15 - 10 = 5)
        ultima = admin_autenticado.get(
            "/api/admin/usuarios/?pagina=3&por_pagina=5"
        ).json()
        assert ultima["pagina"] == 3
        assert len(ultima["items"]) == 5

    def test_filtro_por_perfil(self, admin_autenticado, criar_usuario_direto):
        criar_usuario_direto("Vend A", "venda@example.com", "Senha@123",
                             Perfil.VENDEDOR.value)
        criar_usuario_direto("Vend B", "vendb@example.com", "Senha@123",
                             Perfil.VENDEDOR.value)
        criar_usuario_direto("Cli A", "clia@example.com", "Senha@123",
                             Perfil.CLIENTE.value)
        resp = admin_autenticado.get(
            f"/api/admin/usuarios/?perfil={Perfil.VENDEDOR.value}"
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 2
        assert all(i["perfil"] == Perfil.VENDEDOR.value for i in corpo["items"])

    def test_filtro_por_termo_q(self, admin_autenticado, criar_usuario_direto):
        criar_usuario_direto("Joana Silva", "joana@example.com", "Senha@123",
                             Perfil.CLIENTE.value)
        criar_usuario_direto("Pedro Souza", "pedro@example.com", "Senha@123",
                             Perfil.CLIENTE.value)
        resp = admin_autenticado.get("/api/admin/usuarios/?q=joana")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] >= 1
        assert all("joana" in i["email"].lower() or "joana" in i["nome"].lower()
                   for i in corpo["items"])


# =============================================================================
# GET /api/admin/usuarios/{id}  (detalhe)
# =============================================================================

class TestObter:
    def test_obter_sem_sessao_401(self, client):
        resp = client.get("/api/admin/usuarios/1")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_obter_perfil_nao_admin_403(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/admin/usuarios/1")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_obter_sucesso(self, admin_autenticado, criar_usuario_direto):
        uid = criar_usuario_direto("Alvo", "alvo@example.com", "Senha@123",
                                   Perfil.CLIENTE.value)
        resp = admin_autenticado.get(f"/api/admin/usuarios/{uid}")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["id"] == uid
        assert corpo["email"] == "alvo@example.com"
        assert corpo["perfil"] == Perfil.CLIENTE.value
        assert "senha" not in corpo

    def test_obter_id_inexistente_404(self, admin_autenticado):
        resp = admin_autenticado.get("/api/admin/usuarios/999999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"


# =============================================================================
# POST /api/admin/usuarios/  (criação)
# =============================================================================

class TestCriar:
    def _payload(self, **over):
        base = {
            "nome": "Novo Usuario",
            "email": "novo@example.com",
            "senha": "Senha@123",
            "perfil": Perfil.CLIENTE.value,
        }
        base.update(over)
        return base

    def test_criar_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.post("/api/admin/usuarios/", json=self._payload(),
                           headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_criar_perfil_nao_admin_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.post("/api/admin/usuarios/", json=self._payload(),
                                        headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_criar_sem_csrf_403(self, admin_autenticado):
        resp = admin_autenticado.post("/api/admin/usuarios/", json=self._payload())
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_criar_sucesso_201(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post("/api/admin/usuarios/", json=self._payload(),
                                      headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_201_CREATED
        corpo = resp.json()
        assert corpo["email"] == "novo@example.com"
        assert corpo["nome"] == "Novo Usuario"
        assert corpo["perfil"] == Perfil.CLIENTE.value
        assert "id" in corpo
        assert "senha" not in corpo

    def test_criar_email_duplicado_409(self, admin_autenticado, criar_usuario_direto):
        criar_usuario_direto("Existente", "dup@example.com", "Senha@123",
                             Perfil.CLIENTE.value)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            "/api/admin/usuarios/", json=self._payload(email="dup@example.com"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_409_CONFLICT
        corpo = resp.json()
        assert corpo["type"] == "conflict"
        assert "email" in corpo["errors"]

    def test_criar_email_invalido_422(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            "/api/admin/usuarios/", json=self._payload(email="nao-eh-email"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_criar_senha_fraca_422(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            "/api/admin/usuarios/", json=self._payload(senha="123"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_criar_perfil_invalido_422(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            "/api/admin/usuarios/", json=self._payload(perfil="Inexistente"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_criar_nome_vazio_422(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.post(
            "/api/admin/usuarios/", json=self._payload(nome=""),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"


# =============================================================================
# PUT /api/admin/usuarios/{id}  (alteração)
# =============================================================================

class TestAlterar:
    def _payload(self, uid, **over):
        base = {
            "id": uid,
            "nome": "Nome Alterado",
            "email": "alterado@example.com",
            "perfil": Perfil.VENDEDOR.value,
        }
        base.update(over)
        return base

    def test_alterar_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.put("/api/admin/usuarios/1", json=self._payload(1),
                          headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_alterar_perfil_nao_admin_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put("/api/admin/usuarios/1", json=self._payload(1),
                                       headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_alterar_sem_csrf_403(self, admin_autenticado, criar_usuario_direto):
        uid = criar_usuario_direto("X", "x@example.com", "Senha@123",
                                   Perfil.CLIENTE.value)
        resp = admin_autenticado.put(f"/api/admin/usuarios/{uid}",
                                     json=self._payload(uid))
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_alterar_sucesso_200(self, admin_autenticado, criar_usuario_direto):
        uid = criar_usuario_direto("Antigo", "antigo@example.com", "Senha@123",
                                   Perfil.CLIENTE.value)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            f"/api/admin/usuarios/{uid}", json=self._payload(uid),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["id"] == uid
        assert corpo["nome"] == "Nome Alterado"
        assert corpo["email"] == "alterado@example.com"
        assert corpo["perfil"] == Perfil.VENDEDOR.value

    def test_alterar_id_inexistente_404(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            "/api/admin/usuarios/999999", json=self._payload(999999),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_alterar_id_corpo_diferente_url_400(self, admin_autenticado, criar_usuario_direto):
        uid = criar_usuario_direto("Y", "y@example.com", "Senha@123",
                                   Perfil.CLIENTE.value)
        token = _csrf(admin_autenticado)
        # id no corpo != id na URL
        resp = admin_autenticado.put(
            f"/api/admin/usuarios/{uid}", json=self._payload(uid + 1),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        corpo = resp.json()
        assert corpo["type"] == "bad_request"
        assert "id" in corpo["errors"]

    def test_alterar_email_duplicado_409(self, admin_autenticado, criar_usuario_direto):
        criar_usuario_direto("Ocupa", "ocupado@example.com", "Senha@123",
                             Perfil.CLIENTE.value)
        uid = criar_usuario_direto("Alvo", "alvo2@example.com", "Senha@123",
                                   Perfil.CLIENTE.value)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            f"/api/admin/usuarios/{uid}",
            json=self._payload(uid, email="ocupado@example.com"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_409_CONFLICT
        corpo = resp.json()
        assert corpo["type"] == "conflict"
        assert "email" in corpo["errors"]

    def test_alterar_email_invalido_422(self, admin_autenticado, criar_usuario_direto):
        uid = criar_usuario_direto("Z", "z@example.com", "Senha@123",
                                   Perfil.CLIENTE.value)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            f"/api/admin/usuarios/{uid}",
            json=self._payload(uid, email="nao-eh-email"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_alterar_perfil_invalido_422(self, admin_autenticado, criar_usuario_direto):
        uid = criar_usuario_direto("W", "w@example.com", "Senha@123",
                                   Perfil.CLIENTE.value)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            f"/api/admin/usuarios/{uid}",
            json=self._payload(uid, perfil="Inexistente"),
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"


# =============================================================================
# DELETE /api/admin/usuarios/{id}  (exclusão)
# =============================================================================

class TestExcluir:
    def test_excluir_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.delete("/api/admin/usuarios/1",
                             headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_excluir_perfil_nao_admin_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.delete("/api/admin/usuarios/1",
                                          headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_excluir_sem_csrf_403(self, admin_autenticado, criar_usuario_direto):
        uid = criar_usuario_direto("Del", "del@example.com", "Senha@123",
                                   Perfil.CLIENTE.value)
        resp = admin_autenticado.delete(f"/api/admin/usuarios/{uid}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_excluir_sucesso_204(self, admin_autenticado, criar_usuario_direto):
        uid = criar_usuario_direto("Del2", "del2@example.com", "Senha@123",
                                   Perfil.CLIENTE.value)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.delete(f"/api/admin/usuarios/{uid}",
                                        headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert resp.content == b""  # sem corpo
        # confirmar exclusão
        assert admin_autenticado.get(
            f"/api/admin/usuarios/{uid}"
        ).status_code == status.HTTP_404_NOT_FOUND

    def test_excluir_id_inexistente_404(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.delete("/api/admin/usuarios/999999",
                                        headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.json()["type"] == "not_found"

    def test_excluir_a_si_mesmo_403(self, admin_autenticado):
        meu_id = _id_do_admin(admin_autenticado)
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.delete(f"/api/admin/usuarios/{meu_id}",
                                        headers={"X-CSRF-Token": token})
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"
