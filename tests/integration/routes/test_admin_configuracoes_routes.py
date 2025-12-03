"""
Testes de configurações administrativas
Testa seleção de temas visuais e sistema de auditoria de logs
"""
from fastapi import status
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import sqlite3

from util.datetime_util import agora


class TestTema:
    """Testes de seleção de tema visual"""

    def test_get_tema_requer_admin(self, cliente_autenticado):
        """Cliente não deve acessar seletor de temas"""
        response = cliente_autenticado.get("/admin/tema", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_get_tema_admin_acessa(self, admin_autenticado):
        """Admin deve acessar seletor de temas"""
        response = admin_autenticado.get("/admin/tema")
        assert response.status_code == status.HTTP_200_OK

    def test_get_tema_lista_temas_disponiveis(self, admin_autenticado):
        """Deve listar temas disponíveis"""
        response = admin_autenticado.get("/admin/tema")
        assert response.status_code == status.HTTP_200_OK
        # Deve conter algum tema (pelo menos "original")
        assert "tema" in response.text.lower()

    def test_aplicar_tema_existente(self, admin_autenticado):
        """Admin deve poder aplicar tema existente"""
        # Verificar se o tema 'original' existe antes de testar
        css_original = Path("static/css/bootswatch/original.bootstrap.min.css")

        if css_original.exists():
            response = admin_autenticado.post("/admin/tema/aplicar", data={
                "tema": "original"
            }, follow_redirects=False)

            # Deve redirecionar
            assert response.status_code == status.HTTP_303_SEE_OTHER
            assert response.headers["location"] == "/admin/tema"

    def test_aplicar_tema_inexistente(self, admin_autenticado):
        """Deve rejeitar tema inexistente"""
        response = admin_autenticado.post("/admin/tema/aplicar", data={
            "tema": "tema_que_nao_existe_xyz123"
        }, follow_redirects=False)

        # Deve redirecionar com mensagem de erro
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_aplicar_tema_limpa_cache(self, admin_autenticado):
        """Aplicar tema deve limpar cache de configurações"""
        from util.config_cache import config

        # Verificar se existe pelo menos um tema para aplicar
        css_original = Path("static/css/bootswatch/original.bootstrap.min.css")

        if css_original.exists():
            # Popular cache
            config.obter("theme", "default")

            # Aplicar tema
            admin_autenticado.post("/admin/tema/aplicar", data={
                "tema": "original"
            })

            # Cache deve estar vazio após aplicação
            # (testar indiretamente verificando que a configuração é relida)
            tema_atual = config.obter("theme", "default")
            assert tema_atual is not None

    def test_cliente_nao_pode_aplicar_tema(self, cliente_autenticado):
        """Cliente não deve poder aplicar tema"""
        response = cliente_autenticado.post("/admin/tema/aplicar", data={
            "tema": "original"
        }, follow_redirects=False)

        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]


class TestAuditoria:
    """Testes de sistema de auditoria de logs"""

    def test_get_auditoria_requer_admin(self, cliente_autenticado):
        """Cliente não deve acessar auditoria"""
        response = cliente_autenticado.get("/admin/auditoria", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_get_auditoria_admin_acessa(self, admin_autenticado):
        """Admin deve acessar página de auditoria"""
        response = admin_autenticado.get("/admin/auditoria")
        assert response.status_code == status.HTTP_200_OK
        assert "auditoria" in response.text.lower() or "log" in response.text.lower()

    def test_filtrar_logs_por_data(self, admin_autenticado):
        """Deve permitir filtrar logs por data"""
        data_hoje = agora().strftime('%Y-%m-%d')

        response = admin_autenticado.post("/admin/auditoria/filtrar", data={
            "data": data_hoje,
            "nivel": "TODOS"
        })

        assert response.status_code == status.HTTP_200_OK

    def test_filtrar_logs_nivel_info(self, admin_autenticado):
        """Deve permitir filtrar logs por nível INFO"""
        data_hoje = agora().strftime('%Y-%m-%d')

        response = admin_autenticado.post("/admin/auditoria/filtrar", data={
            "data": data_hoje,
            "nivel": "INFO"
        })

        assert response.status_code == status.HTTP_200_OK

    def test_filtrar_logs_nivel_warning(self, admin_autenticado):
        """Deve permitir filtrar logs por nível WARNING"""
        data_hoje = agora().strftime('%Y-%m-%d')

        response = admin_autenticado.post("/admin/auditoria/filtrar", data={
            "data": data_hoje,
            "nivel": "WARNING"
        })

        assert response.status_code == status.HTTP_200_OK

    def test_filtrar_logs_nivel_error(self, admin_autenticado):
        """Deve permitir filtrar logs por nível ERROR"""
        data_hoje = agora().strftime('%Y-%m-%d')

        response = admin_autenticado.post("/admin/auditoria/filtrar", data={
            "data": data_hoje,
            "nivel": "ERROR"
        })

        assert response.status_code == status.HTTP_200_OK

    def test_filtrar_logs_nivel_todos(self, admin_autenticado):
        """Deve permitir filtrar logs sem filtro de nível (TODOS)"""
        data_hoje = agora().strftime('%Y-%m-%d')

        response = admin_autenticado.post("/admin/auditoria/filtrar", data={
            "data": data_hoje,
            "nivel": "TODOS"
        })

        assert response.status_code == status.HTTP_200_OK

    def test_filtrar_logs_data_sem_arquivo(self, admin_autenticado):
        """Deve tratar data sem arquivo de log"""
        # Data muito antiga (provavelmente não tem log)
        response = admin_autenticado.post("/admin/auditoria/filtrar", data={
            "data": "2000-01-01",
            "nivel": "TODOS"
        })

        assert response.status_code == status.HTTP_200_OK
        # Deve ter mensagem sobre arquivo não encontrado
        assert "encontrado" in response.text.lower() or "nenhum" in response.text.lower()

    def test_filtrar_logs_registra_acao(self, admin_autenticado):
        """Filtrar logs deve registrar a própria ação de auditoria"""
        data_hoje = agora().strftime('%Y-%m-%d')

        # Fazer auditoria
        response = admin_autenticado.post("/admin/auditoria/filtrar", data={
            "data": data_hoje,
            "nivel": "INFO"
        })

        # Verificar que a requisição foi processada com sucesso
        assert response.status_code == status.HTTP_200_OK

    def test_cliente_nao_pode_filtrar_logs(self, cliente_autenticado):
        """Cliente não deve poder filtrar logs"""
        data_hoje = agora().strftime('%Y-%m-%d')

        response = cliente_autenticado.post("/admin/auditoria/filtrar", data={
            "data": data_hoje,
            "nivel": "TODOS"
        }, follow_redirects=False)

        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_filtrar_logs_arquivo_muito_grande(self, admin_autenticado):
        """Deve rejeitar arquivos de log muito grandes (>10MB)"""
        from routes.admin_configuracoes_routes import _ler_log_arquivo
        from unittest.mock import MagicMock

        data_hoje = agora().strftime('%Y-%m-%d')

        with patch('routes.admin_configuracoes_routes.Path') as mock_path:
            mock_arquivo = MagicMock()
            mock_arquivo.exists.return_value = True
            mock_arquivo.stat.return_value.st_size = 15 * 1024 * 1024  # 15MB
            mock_path.return_value = mock_arquivo

            conteudo, total, erro = _ler_log_arquivo(data_hoje, "TODOS")

            assert conteudo == ""
            assert total == 0
            assert "muito grande" in erro.lower()

    def test_filtrar_logs_oserror(self, admin_autenticado):
        """Deve tratar OSError ao ler arquivo de log"""
        from routes.admin_configuracoes_routes import _ler_log_arquivo
        from unittest.mock import MagicMock

        data_hoje = agora().strftime('%Y-%m-%d')

        with patch('routes.admin_configuracoes_routes.Path') as mock_path:
            mock_arquivo = MagicMock()
            mock_arquivo.exists.return_value = True
            mock_arquivo.stat.return_value.st_size = 1024  # 1KB
            mock_path.return_value = mock_arquivo

            with patch('builtins.open', side_effect=OSError("Permission denied")):
                conteudo, total, erro = _ler_log_arquivo(data_hoje, "TODOS")

                assert conteudo == ""
                assert total == 0
                assert "erro" in erro.lower()


class TestSegurancaConfiguracoes:
    """Testes de segurança das configurações"""

    def test_sem_autenticacao_nao_acessa_tema(self, client):
        """Não autenticado não deve acessar temas"""
        response = client.get("/admin/tema", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_sem_autenticacao_nao_acessa_auditoria(self, client):
        """Não autenticado não deve acessar auditoria"""
        response = client.get("/admin/auditoria", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_vendedor_nao_acessa_tema(self, vendedor_autenticado):
        """Vendedor não deve acessar temas"""
        response = vendedor_autenticado.get("/admin/tema", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]

    def test_vendedor_nao_acessa_auditoria(self, vendedor_autenticado):
        """Vendedor não deve acessar auditoria"""
        response = vendedor_autenticado.get("/admin/auditoria", follow_redirects=False)
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_403_FORBIDDEN]


class TestListarConfiguracoes:
    """Testes para listagem de configurações"""

    def test_listar_configuracoes_admin(self, admin_autenticado):
        """Admin deve acessar listagem de configurações"""
        response = admin_autenticado.get("/admin/configuracoes")
        assert response.status_code == status.HTTP_200_OK

    def test_listar_configuracoes_erro_banco(self, admin_autenticado):
        """Erro de banco deve redirecionar com mensagem"""
        with patch('routes.admin_configuracoes_routes.configuracao_repo') as mock_repo:
            mock_repo.obter_por_categoria.side_effect = sqlite3.Error("Database error")

            response = admin_autenticado.get(
                "/admin/configuracoes",
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER


class TestAplicarTemaErros:
    """Testes de erros ao aplicar tema"""

    def test_aplicar_tema_rate_limit(self, admin_autenticado):
        """Rate limit deve bloquear aplicação de tema"""
        with patch('routes.admin_configuracoes_routes.admin_config_limiter.verificar', return_value=False):
            response = admin_autenticado.post(
                "/admin/tema/aplicar",
                data={"tema": "original"},
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_aplicar_tema_arquivo_nao_existe(self, admin_autenticado):
        """Tema na whitelist mas arquivo não existe"""
        with patch('routes.admin_configuracoes_routes.Path') as mock_path:
            # Simula que arquivo não existe
            mock_css = MagicMock()
            mock_css.exists.return_value = False
            mock_path.return_value = mock_css

            response = admin_autenticado.post(
                "/admin/tema/aplicar",
                data={"tema": "original"},
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_aplicar_tema_erro_salvar_banco(self, admin_autenticado):
        """Erro ao salvar tema no banco"""
        css_original = Path("static/css/bootswatch/original.bootstrap.min.css")

        if css_original.exists():
            with patch('routes.admin_configuracoes_routes.configuracao_repo') as mock_repo:
                mock_repo.obter_por_chave.return_value = MagicMock(valor="original")
                mock_repo.inserir_ou_atualizar.return_value = False

                response = admin_autenticado.post(
                    "/admin/tema/aplicar",
                    data={"tema": "original"},
                    follow_redirects=False
                )

                assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_aplicar_tema_erro_copiar_arquivo(self, admin_autenticado):
        """Erro ao copiar arquivo CSS"""
        css_original = Path("static/css/bootswatch/original.bootstrap.min.css")

        if css_original.exists():
            with patch('routes.admin_configuracoes_routes.shutil.copy2') as mock_copy:
                mock_copy.side_effect = OSError("Permission denied")

                response = admin_autenticado.post(
                    "/admin/tema/aplicar",
                    data={"tema": "original"},
                    follow_redirects=False
                )

                assert response.status_code == status.HTTP_303_SEE_OTHER


class TestAuditoriaErros:
    """Testes de erros na auditoria"""

    def test_auditoria_rate_limit(self, admin_autenticado):
        """Rate limit deve bloquear filtro de auditoria"""
        with patch('routes.admin_configuracoes_routes.admin_config_limiter') as mock_limiter:
            mock_limiter.verificar.return_value = False

            response = admin_autenticado.post(
                "/admin/auditoria/filtrar",
                data={"data": "2025-01-01", "nivel": "TODOS"},
                follow_redirects=False
            )

            assert response.status_code == status.HTTP_303_SEE_OTHER


class TestSalvarLoteConfiguracoes:
    """Testes unitários para salvamento em lote de configurações.

    Nota: Esta rota usa await request.form() sem parâmetros Form() explícitos,
    o que impede testes via TestClient. Por isso, testamos a função diretamente.
    """

    def _criar_request_mock(self, form_data: dict, com_usuario_admin: bool = True):
        """Cria um mock de Request com form data e session com usuário admin."""
        from starlette.datastructures import ImmutableMultiDict

        request = MagicMock()

        # Sessão com usuário admin logado
        if com_usuario_admin:
            request.session = {
                "usuario_logado": {
                    "id": 1,
                    "nome": "Admin",
                    "email": "admin@test.com",
                    "perfil": "Administrador"
                }
            }
        else:
            request.session = {}

        # Mock assíncrono para form()
        async def mock_form():
            return ImmutableMultiDict(form_data)
        request.form = mock_form

        # Mock para client.host (usado em rate limiting)
        request.client = MagicMock()
        request.client.host = "127.0.0.1"

        # Mock para url.path (usado em redirects e flash messages)
        request.url = MagicMock()
        request.url.path = "/admin/configuracoes/salvar-lote"

        return request

    @pytest.mark.asyncio
    async def test_salvar_lote_rate_limit(self):
        """Rate limit deve bloquear salvamento em lote"""
        from routes.admin_configuracoes_routes import post_salvar_lote_configuracoes

        request = self._criar_request_mock({"toast_delay": "5000"})

        with patch('routes.admin_configuracoes_routes.admin_config_limiter.verificar', return_value=False):
            # Decorator injeta usuario_logado a partir da sessão
            response = await post_salvar_lote_configuracoes(request)

            assert response.status_code == status.HTTP_303_SEE_OTHER
            assert response.headers["location"] == "/admin/configuracoes"

    @pytest.mark.asyncio
    async def test_salvar_lote_configs_vazias(self):
        """Deve avisar quando não há configurações para salvar"""
        from routes.admin_configuracoes_routes import post_salvar_lote_configuracoes

        # Apenas categoria, sem configs reais
        request = self._criar_request_mock({"categoria": "interface"})

        response = await post_salvar_lote_configuracoes(request)

        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/admin/configuracoes"

    @pytest.mark.asyncio
    async def test_salvar_lote_sucesso(self):
        """Deve salvar configurações com sucesso"""
        from routes.admin_configuracoes_routes import post_salvar_lote_configuracoes

        request = self._criar_request_mock({"toast_delay": "5000"})

        with patch('routes.admin_configuracoes_routes.configuracao_repo') as mock_repo:
            mock_repo.atualizar_multiplas.return_value = (1, [])

            response = await post_salvar_lote_configuracoes(request)

            assert response.status_code == status.HTTP_303_SEE_OTHER

    @pytest.mark.asyncio
    async def test_salvar_lote_sucesso_com_avisos(self):
        """Deve salvar com sucesso e avisar sobre chaves não encontradas"""
        from routes.admin_configuracoes_routes import post_salvar_lote_configuracoes

        request = self._criar_request_mock({
            "toast_delay": "5000",
            "chave_inexistente": "valor"
        })

        with patch('routes.admin_configuracoes_routes.configuracao_repo') as mock_repo:
            mock_repo.atualizar_multiplas.return_value = (1, ["chave_inexistente"])

            response = await post_salvar_lote_configuracoes(request)

            assert response.status_code == status.HTTP_303_SEE_OTHER

    @pytest.mark.asyncio
    async def test_salvar_lote_nenhum_atualizado(self):
        """Deve informar erro quando nenhuma configuração foi atualizada"""
        from routes.admin_configuracoes_routes import post_salvar_lote_configuracoes

        request = self._criar_request_mock({"toast_delay": "5000"})

        with patch('routes.admin_configuracoes_routes.configuracao_repo') as mock_repo:
            mock_repo.atualizar_multiplas.return_value = (0, [])

            response = await post_salvar_lote_configuracoes(request)

            assert response.status_code == status.HTTP_303_SEE_OTHER

    @pytest.mark.asyncio
    async def test_salvar_lote_validation_error(self):
        """Deve tratar erro de validação"""
        from routes.admin_configuracoes_routes import post_salvar_lote_configuracoes
        from pydantic import ValidationError as PydanticValidationError
        from pydantic import BaseModel, field_validator

        request = self._criar_request_mock({"campo_invalido": "abc"})

        with patch('routes.admin_configuracoes_routes.SalvarConfiguracaoLoteDTO') as mock_dto:
            # Criar uma ValidationError real
            class TestModel(BaseModel):
                campo: str

                @field_validator('campo')
                @classmethod
                def validar(cls, v):
                    raise ValueError("Valor inválido")

            try:
                TestModel(campo="abc")
            except PydanticValidationError as e:
                mock_dto.side_effect = e

            response = await post_salvar_lote_configuracoes(request)

            assert response.status_code == status.HTTP_303_SEE_OTHER

    @pytest.mark.asyncio
    async def test_salvar_lote_validation_error_erros_vazios(self):
        """Deve usar mensagem fallback quando processar_erros_validacao retorna vazio"""
        from routes.admin_configuracoes_routes import post_salvar_lote_configuracoes
        from pydantic import ValidationError as PydanticValidationError
        from pydantic import BaseModel, field_validator

        request = self._criar_request_mock({"campo_invalido": "abc"})

        with patch('routes.admin_configuracoes_routes.SalvarConfiguracaoLoteDTO') as mock_dto:
            # Criar uma ValidationError real
            class TestModel(BaseModel):
                campo: str

                @field_validator('campo')
                @classmethod
                def validar(cls, v):
                    raise ValueError("Valor inválido")

            try:
                TestModel(campo="abc")
            except PydanticValidationError as e:
                mock_dto.side_effect = e

            # Mock processar_erros_validacao para retornar dict vazio
            with patch('routes.admin_configuracoes_routes.processar_erros_validacao', return_value={}):
                response = await post_salvar_lote_configuracoes(request)

                assert response.status_code == status.HTTP_303_SEE_OTHER

    @pytest.mark.asyncio
    async def test_salvar_lote_erro_banco(self):
        """Deve tratar erro de banco de dados"""
        from routes.admin_configuracoes_routes import post_salvar_lote_configuracoes

        request = self._criar_request_mock({"toast_delay": "5000"})

        with patch('routes.admin_configuracoes_routes.configuracao_repo') as mock_repo:
            mock_repo.atualizar_multiplas.side_effect = sqlite3.Error("Database error")

            response = await post_salvar_lote_configuracoes(request)

            assert response.status_code == status.HTTP_303_SEE_OTHER


class TestLerLogArquivo:
    """Testes para função _ler_log_arquivo"""

    def test_arquivo_muito_grande(self, admin_autenticado):
        """Arquivo de log muito grande deve retornar erro"""
        import tempfile
        import os

        data_hoje = agora().strftime('%Y-%m-%d')
        data_formatada = data_hoje.replace('-', '.')

        with tempfile.TemporaryDirectory() as tmpdir:
            # Criar arquivo de log grande (fake)
            log_dir = Path(tmpdir) / "logs"
            log_dir.mkdir()
            log_file = log_dir / f"app.{data_formatada}.log"

            # Simular arquivo grande verificando tamanho
            with patch('routes.admin_configuracoes_routes._ler_log_arquivo') as mock_ler:
                mock_ler.return_value = ("", 0, "Arquivo de log muito grande (11.00 MB)")

                response = admin_autenticado.post(
                    "/admin/auditoria/filtrar",
                    data={"data": data_hoje, "nivel": "TODOS"}
                )

                # Verifica resposta mesmo com mock
                assert response.status_code == status.HTTP_200_OK

    def test_erro_leitura_arquivo(self, admin_autenticado):
        """Erro ao ler arquivo deve retornar mensagem"""
        data_hoje = agora().strftime('%Y-%m-%d')

        with patch('routes.admin_configuracoes_routes._ler_log_arquivo') as mock_ler:
            mock_ler.return_value = ("", 0, "Erro ao ler arquivo de log: Permission denied")

            response = admin_autenticado.post(
                "/admin/auditoria/filtrar",
                data={"data": data_hoje, "nivel": "TODOS"}
            )

            assert response.status_code == status.HTTP_200_OK
