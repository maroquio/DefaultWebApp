"""
Testes de endpoint do módulo de administração: Configurações + Auditoria
(routes/admin_configuracoes_routes.py).

Cobre caminhos felizes e tristes de:
    GET  /api/admin/configuracoes
    PUT  /api/admin/configuracoes
    GET  /api/admin/auditoria/logs
    GET  /api/admin/auditoria/registros   (paginado)

Todos os endpoints exigem perfil ADMIN (@requer_autenticacao([Perfil.ADMIN.value])).

Contrato (ver CLAUDE.md):
    - Sucesso: recurso puro com status correto (200) ou schema de saída.
    - Erro: {detail, type, errors} via util/exception_handlers.py.
    - Mutações exigem header X-CSRF-Token (senão 403, type="forbidden").
    - Sessão por cookie; @requer_autenticacao() → 401 sem sessão; perfil errado → 403.
    - Paginação: PaginaResponse[T] = {items, pagina, por_pagina, total, total_paginas}.

Notas de isolamento:
    - A tabela `configuracao` é LIMPA pelo conftest entre testes (fica vazia).
      Por isso, semeamos configs via configuracao_repo antes de exercer GET/PUT.
    - A tabela `auditoria` NÃO é limpa pelo conftest — este arquivo adiciona um
      fixture autouse que faz DELETE FROM auditoria antes/depois de cada teste.
"""
import pytest
from fastapi import status

from util.perfis import Perfil


pytestmark = [pytest.mark.integration]


def _csrf(client):
    """Obtém um token CSRF válido para a sessão do cliente."""
    return client.get("/api/csrf-token").json()["token"]


# =============================================================================
# Fixtures de isolamento / seed
# =============================================================================

@pytest.fixture(autouse=True)
def _limpar_auditoria():
    """A tabela `auditoria` não está no cleanup do conftest; limpamos aqui."""
    from util.db_util import obter_conexao

    def _limpa():
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='auditoria'"
            )
            if cursor.fetchone():
                cursor.execute("DELETE FROM auditoria")
            conn.commit()

    _limpa()
    yield
    _limpa()


@pytest.fixture
def semear_configs():
    """
    Retorna função que insere configurações no banco (tabela limpa pelo conftest).

    Cada item: (chave, valor, descricao). A categoria sai do prefixo
    "[Categoria]" da descrição (senão "Outras").
    """
    from repo import configuracao_repo

    def _semear(itens):
        for chave, valor, descricao in itens:
            configuracao_repo.inserir_ou_atualizar(chave, valor, descricao)

    return _semear


@pytest.fixture
def registrar_auditoria():
    """Retorna função que insere um registro de auditoria diretamente via repo."""
    from repo import auditoria_repo

    def _registrar(acao="criar", entidade="usuario", usuario_id=None,
                   entidade_id=None, ip="127.0.0.1"):
        return auditoria_repo.registrar(
            acao=acao,
            entidade=entidade,
            usuario_id=usuario_id,
            entidade_id=entidade_id,
            ip=ip,
        )

    return _registrar


# =============================================================================
# GET /api/admin/configuracoes
# =============================================================================

class TestListarConfiguracoes:
    def test_lista_agrupada_por_categoria(self, admin_autenticado, semear_configs):
        # A app pode semear configs no startup; usamos chaves próprias e
        # uma categoria singular ("CatTesteXYZ") para asserts determinísticos.
        semear_configs([
            ("config_teste_xyz_app", "Meu Sistema", "[CatTesteXYZ] Nome teste"),
            ("config_teste_xyz_cor", "#1a73e8", "[CatTesteXYZ] Cor teste"),
        ])
        resp = admin_autenticado.get("/api/admin/configuracoes")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert isinstance(corpo["categorias"], list)
        # total deve contar todas as configs (inclui nossas 2 + seed da app)
        assert corpo["total"] == sum(len(c["itens"]) for c in corpo["categorias"])
        assert corpo["total"] >= 2

        # Mapa categoria -> itens
        cats = {c["categoria"]: c["itens"] for c in corpo["categorias"]}
        assert "CatTesteXYZ" in cats
        itens_cat = cats["CatTesteXYZ"]
        assert len(itens_cat) == 2

        # Shape do item
        item = itens_cat[0]
        assert {"chave", "valor", "descricao", "categoria"} <= set(item.keys())
        assert item["categoria"] == "CatTesteXYZ"

        por_chave = {i["chave"]: i for i in itens_cat}
        assert por_chave["config_teste_xyz_app"]["valor"] == "Meu Sistema"

    def test_categoria_outras_para_sem_prefixo(self, admin_autenticado, semear_configs):
        """Config com descrição sem '[Categoria]' cai em 'Outras'."""
        semear_configs([
            ("config_sem_categoria_xyz", "valor", "Descrição sem prefixo"),
        ])
        resp = admin_autenticado.get("/api/admin/configuracoes")
        assert resp.status_code == status.HTTP_200_OK
        cats = {c["categoria"]: c["itens"] for c in resp.json()["categorias"]}
        assert "Outras" in cats
        chaves_outras = {i["chave"] for i in cats["Outras"]}
        assert "config_sem_categoria_xyz" in chaves_outras

    def test_sem_sessao_401(self, client):
        resp = client.get("/api/admin/configuracoes")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_perfil_nao_admin_403(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/admin/configuracoes")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_vendedor_403(self, vendedor_autenticado):
        resp = vendedor_autenticado.get("/api/admin/configuracoes")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"


# =============================================================================
# PUT /api/admin/configuracoes
# =============================================================================

class TestSalvarConfiguracoes:
    def test_atualiza_multiplas_sucesso(self, admin_autenticado, semear_configs):
        semear_configs([
            ("app_name", "Antigo", "Nome da aplicação"),
            ("resend_from_name", "Antigo Remetente", "Nome remetente"),
        ])
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"app_name": "Novo Nome", "resend_from_name": "Novo Remetente"}},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["atualizadas"] == 2
        assert corpo["chaves_nao_encontradas"] == []
        assert "2 configurações atualizadas" in corpo["message"]

        # Persistiu de fato
        from repo import configuracao_repo
        assert configuracao_repo.obter_por_chave("app_name").valor == "Novo Nome"

    def test_chave_nao_encontrada_mensagem_parcial(self, admin_autenticado, semear_configs):
        """Chave existente é atualizada; chave inexistente vira não-encontrada."""
        semear_configs([("app_name", "Antigo", "Nome da aplicação")])
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"app_name": "Novo", "chave_inexistente": "x"}},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["atualizadas"] == 1
        assert corpo["chaves_nao_encontradas"] == ["chave_inexistente"]
        assert "Chaves não encontradas: chave_inexistente" in corpo["message"]

    def test_nenhuma_atualizada_quando_todas_inexistentes(self, admin_autenticado):
        """Banco vazio: nenhuma chave existe, nada é atualizado."""
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"nao_existe": "valor"}},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["atualizadas"] == 0
        assert corpo["chaves_nao_encontradas"] == ["nao_existe"]
        assert corpo["message"] == "Nenhuma configuração foi atualizada."

    def test_sem_sessao_401(self, client):
        token = _csrf(client)
        resp = client.put(
            "/api/admin/configuracoes",
            json={"configs": {"app_name": "X"}},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_perfil_nao_admin_403(self, cliente_autenticado):
        token = _csrf(cliente_autenticado)
        resp = cliente_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"app_name": "X"}},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_sem_csrf_403(self, admin_autenticado):
        resp = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"app_name": "X"}},
        )
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_configs_vazio_422(self, admin_autenticado):
        """O validador exige pelo menos uma configuração."""
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {}},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_payload_sem_campo_configs_422(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_valor_max_invalido_422(self, admin_autenticado):
        """Chave terminando em _max com valor fora do range falha na validação do DTO."""
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"rate_limit_login_max": "99999"}},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_email_invalido_422(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"resend_from_email": "nao-eh-email"}},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_valor_vazio_422(self, admin_autenticado):
        token = _csrf(admin_autenticado)
        resp = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"app_name": "   "}},
            headers={"X-CSRF-Token": token},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_excede_rate_limit_429(self, admin_autenticado, semear_configs,
                                   bloquear_rate_limiter):
        semear_configs([("app_name", "X", "Nome da aplicação")])
        token = _csrf(admin_autenticado)
        with bloquear_rate_limiter(
            "routes.admin_configuracoes_routes.admin_config_limiter"
        ):
            resp = admin_autenticado.put(
                "/api/admin/configuracoes",
                json={"configs": {"app_name": "Novo"}},
                headers={"X-CSRF-Token": token},
            )
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in resp.headers


# =============================================================================
# GET /api/admin/auditoria/logs
# =============================================================================

class TestAuditoriaLogs:
    def test_data_inexistente_preenche_erro(self, admin_autenticado):
        """Sem arquivo de log para a data, o campo `erro` é preenchido."""
        resp = admin_autenticado.get(
            "/api/admin/auditoria/logs", params={"data": "1999-01-01"}
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["data"] == "1999-01-01"
        assert corpo["nivel"] == "TODOS"
        assert corpo["total_linhas"] == 0
        assert corpo["conteudo"] == ""
        assert corpo["erro"] is not None
        assert "1999-01-01" in corpo["erro"]

    def test_nivel_personalizado_refletido(self, admin_autenticado):
        resp = admin_autenticado.get(
            "/api/admin/auditoria/logs",
            params={"data": "1999-01-01", "nivel": "ERROR"},
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["nivel"] == "ERROR"
        assert corpo["erro"] is not None

    def test_sem_parametros_usa_hoje(self, admin_autenticado):
        """Sem `data`, usa a data de hoje; shape do response deve estar completo."""
        resp = admin_autenticado.get("/api/admin/auditoria/logs")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert {"data", "nivel", "total_linhas", "conteudo", "erro"} == set(corpo.keys())
        assert corpo["nivel"] == "TODOS"
        assert len(corpo["data"]) == 10  # YYYY-MM-DD

    def test_sem_sessao_401(self, client):
        resp = client.get("/api/admin/auditoria/logs")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_perfil_nao_admin_403(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/admin/auditoria/logs")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"

    def test_excede_rate_limit_429(self, admin_autenticado, bloquear_rate_limiter):
        with bloquear_rate_limiter(
            "routes.admin_configuracoes_routes.admin_config_limiter"
        ):
            resp = admin_autenticado.get("/api/admin/auditoria/logs")
        assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in resp.headers


# =============================================================================
# GET /api/admin/auditoria/registros (paginado)
# =============================================================================

class TestAuditoriaRegistros:
    def test_lista_vazia_paginada(self, admin_autenticado):
        resp = admin_autenticado.get("/api/admin/auditoria/registros")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["items"] == []
        assert corpo["pagina"] == 1
        assert corpo["por_pagina"] == 20
        assert corpo["total"] == 0
        # Paginacao.__post_init__ usa max(1, ...): página vazia => 1 página
        assert corpo["total_paginas"] == 1

    def test_lista_com_registros(self, admin_autenticado, registrar_auditoria):
        registrar_auditoria(acao="criar", entidade="usuario", entidade_id=1)
        registrar_auditoria(acao="excluir", entidade="produto", entidade_id=2)
        resp = admin_autenticado.get("/api/admin/auditoria/registros")
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 2
        assert len(corpo["items"]) == 2
        assert corpo["total_paginas"] == 1

        item = corpo["items"][0]
        assert {"id", "acao", "entidade", "data"} <= set(item.keys())
        acoes = {i["acao"] for i in corpo["items"]}
        assert acoes == {"criar", "excluir"}

    def test_filtro_por_acao(self, admin_autenticado, registrar_auditoria):
        registrar_auditoria(acao="criar", entidade="usuario")
        registrar_auditoria(acao="excluir", entidade="usuario")
        resp = admin_autenticado.get(
            "/api/admin/auditoria/registros", params={"acao": "excluir"}
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 1
        assert corpo["items"][0]["acao"] == "excluir"

    def test_filtro_por_entidade(self, admin_autenticado, registrar_auditoria):
        registrar_auditoria(acao="criar", entidade="usuario")
        registrar_auditoria(acao="criar", entidade="produto")
        resp = admin_autenticado.get(
            "/api/admin/auditoria/registros", params={"entidade": "produto"}
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["total"] == 1
        assert corpo["items"][0]["entidade"] == "produto"

    def test_paginacao_segunda_pagina(self, admin_autenticado, registrar_auditoria):
        # 21 registros -> 2 páginas (20 por página)
        for i in range(21):
            registrar_auditoria(acao="criar", entidade="usuario", entidade_id=i)
        resp = admin_autenticado.get(
            "/api/admin/auditoria/registros", params={"pagina": 2}
        )
        assert resp.status_code == status.HTTP_200_OK
        corpo = resp.json()
        assert corpo["pagina"] == 2
        assert corpo["total"] == 21
        assert corpo["total_paginas"] == 2
        assert len(corpo["items"]) == 1

    def test_pagina_invalida_zero_422(self, admin_autenticado):
        """pagina tem ge=1; valor 0 falha validação de query."""
        resp = admin_autenticado.get(
            "/api/admin/auditoria/registros", params={"pagina": 0}
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.json()["type"] == "validation_error"

    def test_sem_sessao_401(self, client):
        resp = client.get("/api/admin/auditoria/registros")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()["type"] == "unauthorized"

    def test_perfil_nao_admin_403(self, cliente_autenticado):
        resp = cliente_autenticado.get("/api/admin/auditoria/registros")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp.json()["type"] == "forbidden"
