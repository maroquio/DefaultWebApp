"""
Testes de integração para o CRUD administrativo de usuários (API JSON).

Contrato (routes/admin_usuarios_routes.py, prefixo /admin/usuarios):
- GET    /api/admin/usuarios/        -> 200 PaginaResponse[UsuarioResponse]
- GET    /api/admin/usuarios/{id}    -> 200 UsuarioResponse | 404
- POST   /api/admin/usuarios/        -> 201 UsuarioResponse | 409 (email duplicado)
- PUT    /api/admin/usuarios/{id}    -> 200 UsuarioResponse | 400 (id divergente) | 409
- DELETE /api/admin/usuarios/{id}    -> 204 | 403 (auto-exclusão)

Regras transversais:
- Admin-only: não-admin recebe 403, não-autenticado recebe 401.
- Mutações exigem header X-CSRF-Token.
"""
from fastapi import status

from util.perfis import Perfil


def _csrf(client):
    """Obtém um token CSRF válido para a sessão atual."""
    return client.get("/api/csrf-token").json()["token"]


def _obter_usuario(email):
    """Carrega a entidade Usuario pelo e-mail (acesso direto ao repo)."""
    from repo import usuario_repo

    return usuario_repo.obter_por_email(email)


# =============================================================================
# Autorização / Autenticação
# =============================================================================

class TestAdminUsuariosAutorizacao:
    """Apenas administradores acessam o CRUD de usuários."""

    def test_listar_sem_autenticacao_401(self, client):
        """Não autenticado recebe 401 ao listar."""
        response = client.get("/api/admin/usuarios")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_listar_nao_admin_403(self, cliente_autenticado):
        """Cliente comum recebe 403 ao listar."""
        response = cliente_autenticado.get("/api/admin/usuarios")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_obter_nao_admin_403(self, cliente_autenticado):
        """Cliente comum recebe 403 ao obter um usuário."""
        response = cliente_autenticado.get("/api/admin/usuarios/1")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_criar_nao_admin_403(self, cliente_autenticado):
        """Cliente comum recebe 403 ao tentar criar usuário."""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.post(
            "/api/admin/usuarios",
            json={
                "nome": "Qualquer Um",
                "email": "qualquer@example.com",
                "senha": "Senha@123",
                "perfil": Perfil.CLIENTE.value,
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_criar_sem_autenticacao_401(self, client):
        """Não autenticado recebe 401 ao tentar criar usuário."""
        token = _csrf(client)
        response = client.post(
            "/api/admin/usuarios",
            json={
                "nome": "Qualquer Um",
                "email": "qualquer@example.com",
                "senha": "Senha@123",
                "perfil": Perfil.CLIENTE.value,
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_excluir_nao_admin_403(self, cliente_autenticado):
        """Cliente comum recebe 403 ao tentar excluir usuário."""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.request(
            "DELETE", "/api/admin/usuarios/1", headers={"X-CSRF-Token": token}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# Listagem
# =============================================================================

class TestListarUsuarios:
    """GET /admin/usuarios/ — listagem paginada."""

    def test_listar_200_envelope_paginado(self, admin_autenticado, admin_teste):
        """Admin lista usuários e recebe um PaginaResponse."""
        response = admin_autenticado.get("/api/admin/usuarios")
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        # Campos do envelope PaginaResponse
        assert "items" in corpo
        assert "pagina" in corpo
        assert "por_pagina" in corpo
        assert "total" in corpo
        assert "total_paginas" in corpo
        assert isinstance(corpo["items"], list)

        # O próprio admin deve constar na listagem
        emails = [u["email"] for u in corpo["items"]]
        assert admin_teste["email"] in emails
        assert corpo["total"] >= 1

    def test_listar_item_tem_campos_response(self, admin_autenticado):
        """Cada item segue o contrato de UsuarioResponse (sem senha)."""
        response = admin_autenticado.get("/api/admin/usuarios")
        assert response.status_code == status.HTTP_200_OK

        item = response.json()["items"][0]
        for campo in ("id", "nome", "email", "perfil", "foto_url"):
            assert campo in item
        # Dados sensíveis nunca devem vazar
        assert "senha" not in item

    def test_listar_paginacao_respeita_por_pagina(
        self, admin_autenticado, criar_usuario
    ):
        """O parâmetro por_pagina limita a quantidade de itens da página."""
        criar_usuario("Usuario A", "lista_a@example.com", "Senha@123")
        criar_usuario("Usuario B", "lista_b@example.com", "Senha@123")

        response = admin_autenticado.get("/api/admin/usuarios/?pagina=1&por_pagina=1")
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["por_pagina"] == 1
        assert len(corpo["items"]) == 1
        assert corpo["total"] >= 3
        assert corpo["total_paginas"] >= 3


# =============================================================================
# Detalhe
# =============================================================================

class TestObterUsuario:
    """GET /admin/usuarios/{id} — detalhe."""

    def test_obter_existente_200(self, admin_autenticado, admin_teste):
        """Admin obtém os dados de um usuário existente."""
        admin = _obter_usuario(admin_teste["email"])

        response = admin_autenticado.get(f"/api/admin/usuarios/{admin.id}")
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["id"] == admin.id
        assert corpo["email"] == admin_teste["email"]
        assert "senha" not in corpo

    def test_obter_inexistente_404(self, admin_autenticado):
        """Usuário inexistente retorna 404."""
        response = admin_autenticado.get("/api/admin/usuarios/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# Criação
# =============================================================================

class TestCriarUsuario:
    """POST /admin/usuarios/ — criação."""

    def test_criar_201(self, admin_autenticado):
        """Admin cria usuário e recebe 201 com o recurso criado."""
        token = _csrf(admin_autenticado)
        response = admin_autenticado.post(
            "/api/admin/usuarios",
            json={
                "nome": "Novo Usuario Admin",
                "email": "novousuario@example.com",
                "senha": "Senha@123",
                "perfil": Perfil.CLIENTE.value,
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_201_CREATED

        corpo = response.json()
        assert corpo["nome"] == "Novo Usuario Admin"
        assert corpo["email"] == "novousuario@example.com"
        assert corpo["perfil"] == Perfil.CLIENTE.value
        assert corpo["id"] > 0
        assert "senha" not in corpo

        # Efeito colateral: usuário realmente persistido
        criado = _obter_usuario("novousuario@example.com")
        assert criado is not None
        assert criado.perfil == Perfil.CLIENTE.value

    def test_criar_perfil_admin_201(self, admin_autenticado):
        """Admin pode criar outro admin."""
        token = _csrf(admin_autenticado)
        response = admin_autenticado.post(
            "/api/admin/usuarios",
            json={
                "nome": "Novo Admin",
                "email": "novoadmin@example.com",
                "senha": "SenhaAdmin@123",
                "perfil": Perfil.ADMIN.value,
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["perfil"] == Perfil.ADMIN.value

    def test_criar_email_duplicado_409(self, admin_autenticado, admin_teste):
        """E-mail já cadastrado retorna 409 com contrato de erro."""
        token = _csrf(admin_autenticado)
        response = admin_autenticado.post(
            "/api/admin/usuarios",
            json={
                "nome": "Outro Nome",
                "email": admin_teste["email"],  # já existe
                "senha": "Senha@123",
                "perfil": Perfil.CLIENTE.value,
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_409_CONFLICT

        corpo = response.json()
        # O handler achata o dict padronizado no topo {detail, type, errors}
        assert corpo["type"] == "conflict"
        assert "email" in corpo["errors"]

    def test_criar_senha_fraca_422(self, admin_autenticado):
        """Senha fraca é barrada pela validação do DTO (422)."""
        token = _csrf(admin_autenticado)
        response = admin_autenticado.post(
            "/api/admin/usuarios",
            json={
                "nome": "Usuario Teste",
                "email": "fraco@example.com",
                "senha": "123",
                "perfil": Perfil.CLIENTE.value,
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_criar_perfil_invalido_422(self, admin_autenticado):
        """Perfil inexistente é barrado pela validação do DTO (422)."""
        token = _csrf(admin_autenticado)
        response = admin_autenticado.post(
            "/api/admin/usuarios",
            json={
                "nome": "Usuario Teste",
                "email": "perfilinvalido@example.com",
                "senha": "Senha@123",
                "perfil": "PERFIL_INVALIDO",
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# =============================================================================
# Alteração
# =============================================================================

class TestAlterarUsuario:
    """PUT /admin/usuarios/{id} — alteração."""

    def test_alterar_200(self, admin_autenticado, criar_usuario):
        """Admin altera nome, e-mail e perfil de um usuário."""
        criar_usuario("Usuario Original", "original@example.com", "Senha@123")
        usuario = _obter_usuario("original@example.com")

        token = _csrf(admin_autenticado)
        response = admin_autenticado.put(
            f"/api/admin/usuarios/{usuario.id}",
            json={
                "id": usuario.id,  # id do corpo deve bater com o da URL
                "nome": "Usuario Editado",
                "email": "editado@example.com",
                "perfil": Perfil.VENDEDOR.value,
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["nome"] == "Usuario Editado"
        assert corpo["email"] == "editado@example.com"
        assert corpo["perfil"] == Perfil.VENDEDOR.value

        # Efeito colateral persistido
        editado = _obter_usuario("editado@example.com")
        assert editado is not None
        assert editado.id == usuario.id

    def test_alterar_nao_altera_senha(self, admin_autenticado, criar_usuario):
        """Alteração preserva o hash de senha existente."""
        criar_usuario("Usuario Senha", "senha@example.com", "SenhaOriginal@123")
        usuario = _obter_usuario("senha@example.com")
        senha_hash_original = usuario.senha

        token = _csrf(admin_autenticado)
        admin_autenticado.put(
            f"/api/admin/usuarios/{usuario.id}",
            json={
                "id": usuario.id,
                "nome": "Nome Editado",
                "email": "senha@example.com",
                "perfil": Perfil.CLIENTE.value,
            },
            headers={"X-CSRF-Token": token},
        )

        from repo import usuario_repo

        editado = usuario_repo.obter_por_id(usuario.id)
        assert editado.senha == senha_hash_original

    def test_alterar_id_divergente_400(self, admin_autenticado, criar_usuario):
        """id do corpo divergente do id da URL retorna 400."""
        criar_usuario("Usuario Div", "div@example.com", "Senha@123")
        usuario = _obter_usuario("div@example.com")

        token = _csrf(admin_autenticado)
        response = admin_autenticado.put(
            f"/api/admin/usuarios/{usuario.id}",
            json={
                "id": usuario.id + 1000,  # divergente
                "nome": "Nome Alterado",
                "email": "div@example.com",
                "perfil": Perfil.CLIENTE.value,
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["type"] == "bad_request"

    def test_alterar_email_duplicado_409(self, admin_autenticado, criar_usuario):
        """E-mail já usado por outro usuário retorna 409."""
        criar_usuario("Usuario 1", "usuario1@example.com", "Senha@123")
        criar_usuario("Usuario 2", "usuario2@example.com", "Senha@123")
        usuario2 = _obter_usuario("usuario2@example.com")

        token = _csrf(admin_autenticado)
        response = admin_autenticado.put(
            f"/api/admin/usuarios/{usuario2.id}",
            json={
                "id": usuario2.id,
                "nome": "Usuario 2",
                "email": "usuario1@example.com",  # pertence ao usuario1
                "perfil": Perfil.CLIENTE.value,
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["type"] == "conflict"

    def test_alterar_inexistente_404(self, admin_autenticado):
        """Alterar usuário inexistente retorna 404."""
        token = _csrf(admin_autenticado)
        response = admin_autenticado.put(
            "/api/admin/usuarios/99999",
            json={
                "id": 99999,
                "nome": "Nome Alterado",
                "email": "inexistente@example.com",
                "perfil": Perfil.CLIENTE.value,
            },
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# Exclusão
# =============================================================================

class TestExcluirUsuario:
    """DELETE /admin/usuarios/{id} — exclusão."""

    def test_excluir_204(self, admin_autenticado, criar_usuario):
        """Admin exclui usuário e recebe 204 (sem corpo)."""
        criar_usuario("Usuario Para Excluir", "excluir@example.com", "Senha@123")
        usuario = _obter_usuario("excluir@example.com")

        token = _csrf(admin_autenticado)
        response = admin_autenticado.request(
            "DELETE",
            f"/api/admin/usuarios/{usuario.id}",
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        from repo import usuario_repo

        assert usuario_repo.obter_por_id(usuario.id) is None

    def test_excluir_a_si_mesmo_403(self, admin_autenticado, admin_teste):
        """Admin não pode excluir o próprio usuário (403)."""
        admin = _obter_usuario(admin_teste["email"])

        token = _csrf(admin_autenticado)
        response = admin_autenticado.request(
            "DELETE",
            f"/api/admin/usuarios/{admin.id}",
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        from repo import usuario_repo

        # O admin continua existindo
        assert usuario_repo.obter_por_id(admin.id) is not None

    def test_excluir_inexistente_404(self, admin_autenticado):
        """Excluir usuário inexistente retorna 404."""
        token = _csrf(admin_autenticado)
        response = admin_autenticado.request(
            "DELETE", "/api/admin/usuarios/99999", headers={"X-CSRF-Token": token}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
