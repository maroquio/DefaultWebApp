"""
Testes de integração para Configurações + Auditoria administrativas (API JSON).

Contrato (routes/admin_configuracoes_routes.py, prefixo /admin):
- GET /api/admin/configuracoes          -> 200 ConfigListaResponse
- PUT /api/admin/configuracoes          -> 200 SalvarConfigResultadoResponse
                                           (body {"configs": {chave: valor}}; invalida cache)
- GET /api/admin/auditoria/logs         -> 200 LogArquivoResponse
- GET /api/admin/auditoria/registros    -> 200 PaginaResponse[AuditoriaResponse]

Regras transversais:
- Admin-only: não-admin recebe 403, não-autenticado recebe 401.
- Mutações (PUT) exigem header X-CSRF-Token.

NOTA: As rotas de TEMA (seletor Bootswatch, logo, favicon, cores, cópia de
arquivos CSS em static/css) foram REMOVIDAS na migração para SPA. Todos os
testes de tema/bootswatch e referências a arquivos CSS foram eliminados.
"""
from fastapi import status

from util.datetime_util import agora


def _csrf(client):
    """Obtém um token CSRF válido para a sessão atual."""
    return client.get("/api/csrf-token").json()["token"]


def _seed_config(chave, valor, descricao="[Interface] Config de teste"):
    """
    Insere/atualiza uma configuração diretamente no banco.

    O autouse `limpar_banco_dados` esvazia a tabela `configuracao` por teste,
    então cada teste que depende de configs as semeia explicitamente.
    """
    from repo import configuracao_repo

    configuracao_repo.inserir_ou_atualizar(chave, valor, descricao)


# =============================================================================
# Autorização / Autenticação
# =============================================================================

class TestConfiguracoesAutorizacao:
    """Apenas administradores acessam configurações e auditoria."""

    def test_get_configs_sem_autenticacao_401(self, client):
        """Não autenticado recebe 401 ao listar configurações."""
        response = client.get("/api/admin/configuracoes")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_configs_nao_admin_403(self, cliente_autenticado):
        """Cliente comum recebe 403 ao listar configurações."""
        response = cliente_autenticado.get("/api/admin/configuracoes")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_configs_vendedor_403(self, vendedor_autenticado):
        """Vendedor recebe 403 ao listar configurações."""
        response = vendedor_autenticado.get("/api/admin/configuracoes")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_configs_nao_admin_403(self, cliente_autenticado):
        """Cliente comum recebe 403 ao salvar configurações."""
        token = _csrf(cliente_autenticado)
        response = cliente_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"app_name": "Hack"}},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auditoria_registros_nao_admin_403(self, cliente_autenticado):
        """Cliente comum recebe 403 na trilha de auditoria."""
        response = cliente_autenticado.get("/api/admin/auditoria/registros")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auditoria_logs_sem_autenticacao_401(self, client):
        """Não autenticado recebe 401 no log de arquivo."""
        response = client.get("/api/admin/auditoria/logs")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Listagem de configurações (GET)
# =============================================================================

class TestListarConfiguracoes:
    """GET /admin/configuracoes — ConfigListaResponse."""

    def test_get_configs_200_envelope(self, admin_autenticado):
        """Admin lista configurações agrupadas por categoria."""
        _seed_config("app_name", "Sistema Teste", "[Aplicação] Nome do sistema")

        response = admin_autenticado.get("/api/admin/configuracoes")
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert "total" in corpo
        assert "categorias" in corpo
        assert isinstance(corpo["categorias"], list)
        assert corpo["total"] >= 1

        # Estrutura de cada categoria e item
        categoria = corpo["categorias"][0]
        assert "categoria" in categoria
        assert "itens" in categoria
        item = categoria["itens"][0]
        for campo in ("chave", "valor", "categoria"):
            assert campo in item

    def test_get_configs_reflete_valor_seed(self, admin_autenticado):
        """O valor semeado aparece na listagem."""
        _seed_config("app_name", "Valor Especifico XYZ", "[Aplicação] Nome")

        response = admin_autenticado.get("/api/admin/configuracoes")
        assert response.status_code == status.HTTP_200_OK

        chaves_valores = {
            item["chave"]: item["valor"]
            for cat in response.json()["categorias"]
            for item in cat["itens"]
        }
        assert chaves_valores.get("app_name") == "Valor Especifico XYZ"

    def test_get_configs_erro_banco_500(self, admin_autenticado):
        """Erro de banco ao listar retorna 500 (JSON puro, sem redirect)."""
        import sqlite3
        from unittest.mock import patch

        with patch("routes.admin_configuracoes_routes.configuracao_repo") as mock_repo:
            mock_repo.obter_por_categoria.side_effect = sqlite3.Error("boom")
            response = admin_autenticado.get("/api/admin/configuracoes")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# =============================================================================
# Salvamento em lote de configurações (PUT)
# =============================================================================

class TestSalvarConfiguracoes:
    """PUT /admin/configuracoes — SalvarConfigResultadoResponse + efeito."""

    def test_put_configs_200_e_efeito(self, admin_autenticado):
        """Admin salva configs; valor persiste e cache é invalidado."""
        from util.config_cache import config
        from repo import configuracao_repo

        _seed_config("app_name", "Nome Antigo", "[Aplicação] Nome do sistema")

        # Popular o cache com o valor antigo (para provar invalidação)
        valor_em_cache = config.obter("app_name", "fallback")
        assert valor_em_cache == "Nome Antigo"

        token = _csrf(admin_autenticado)
        response = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"app_name": "Nome Novo"}},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["atualizadas"] == 1
        assert corpo["chaves_nao_encontradas"] == []
        assert "message" in corpo

        # Efeito no banco
        assert configuracao_repo.obter_por_chave("app_name").valor == "Nome Novo"
        # Cache invalidado: nova leitura reflete o valor atualizado
        assert config.obter("app_name", "fallback") == "Nome Novo"

    def test_put_configs_chave_inexistente(self, admin_autenticado):
        """Chaves inexistentes são reportadas em chaves_nao_encontradas."""
        _seed_config("app_name", "Existe", "[Aplicação] Nome")

        token = _csrf(admin_autenticado)
        response = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"app_name": "Novo", "chave_fantasma": "x"}},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["atualizadas"] == 1
        assert "chave_fantasma" in corpo["chaves_nao_encontradas"]

    def test_put_configs_sem_csrf_falha(self, admin_autenticado):
        """PUT sem header X-CSRF-Token é rejeitado (403)."""
        response = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"app_name": "Sem CSRF"}},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_configs_valor_vazio_422(self, admin_autenticado):
        """Valor vazio é barrado pela validação do DTO (422)."""
        token = _csrf(admin_autenticado)
        response = admin_autenticado.put(
            "/api/admin/configuracoes",
            json={"configs": {"app_name": ""}},
            headers={"X-CSRF-Token": token},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# =============================================================================
# Auditoria — Log de arquivo (GET /admin/auditoria/logs)
# =============================================================================

class TestAuditoriaLogs:
    """GET /admin/auditoria/logs — LogArquivoResponse."""

    def test_logs_200_padrao(self, admin_autenticado):
        """Admin lê o log do dia (nível TODOS por padrão)."""
        response = admin_autenticado.get("/api/admin/auditoria/logs")
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        for campo in ("data", "nivel", "total_linhas", "conteudo"):
            assert campo in corpo
        assert corpo["nivel"] == "TODOS"

    def test_logs_filtra_por_data_e_nivel(self, admin_autenticado):
        """Parâmetros de query data/nível são refletidos na resposta."""
        data_hoje = agora().strftime("%Y-%m-%d")
        response = admin_autenticado.get(
            f"/api/admin/auditoria/logs?data={data_hoje}&nivel=INFO"
        )
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["data"] == data_hoje
        assert corpo["nivel"] == "INFO"

    def test_logs_data_sem_arquivo_reporta_erro(self, admin_autenticado):
        """Data sem arquivo de log retorna 200 com campo erro preenchido."""
        response = admin_autenticado.get(
            "/api/admin/auditoria/logs?data=2000-01-01&nivel=TODOS"
        )
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        assert corpo["total_linhas"] == 0
        assert corpo["erro"] is not None


# =============================================================================
# Auditoria — Trilha estruturada (GET /admin/auditoria/registros)
# =============================================================================

class TestAuditoriaRegistros:
    """GET /admin/auditoria/registros — PaginaResponse[AuditoriaResponse]."""

    def test_registros_200_paginado(self, admin_autenticado):
        """Admin lista a trilha estruturada num envelope paginado."""
        response = admin_autenticado.get("/api/admin/auditoria/registros")
        assert response.status_code == status.HTTP_200_OK

        corpo = response.json()
        for campo in ("items", "pagina", "por_pagina", "total", "total_paginas"):
            assert campo in corpo
        assert isinstance(corpo["items"], list)
        assert corpo["pagina"] == 1
        # por_pagina é fixo em 20 na rota
        assert corpo["por_pagina"] == 20

    def test_registros_aceita_filtros(self, admin_autenticado):
        """Filtros por ação/entidade/página são aceitos sem erro."""
        response = admin_autenticado.get(
            "/api/admin/auditoria/registros?pagina=1&acao=criar&entidade=usuario"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pagina"] == 1
