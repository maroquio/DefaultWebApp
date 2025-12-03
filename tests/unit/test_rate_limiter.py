"""
Testes para o módulo util/rate_limiter.py

Testa RateLimiter, DynamicRateLimiter, RegistroLimiters e decorator @com_rate_limit.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient

from util.rate_limiter import (
    RateLimiter,
    DynamicRateLimiter,
    RegistroLimiters,
    registro_limiters,
    obter_identificador_cliente,
    com_rate_limit
)


class TestRateLimiter:
    """Testes para a classe RateLimiter"""

    def test_inicializacao_valida(self):
        """Deve inicializar com valores válidos"""
        limiter = RateLimiter(max_tentativas=10, janela_minutos=5, nome="teste")

        assert limiter.max_tentativas == 10
        assert limiter.janela_minutos == 5
        assert limiter.nome == "teste"
        assert limiter.janela == timedelta(minutes=5)

    def test_inicializacao_max_tentativas_zero_falha(self):
        """Deve falhar se max_tentativas for zero"""
        with pytest.raises(ValueError) as exc_info:
            RateLimiter(max_tentativas=0, janela_minutos=5)

        assert "max_tentativas deve ser positivo" in str(exc_info.value)

    def test_inicializacao_max_tentativas_negativo_falha(self):
        """Deve falhar se max_tentativas for negativo"""
        with pytest.raises(ValueError) as exc_info:
            RateLimiter(max_tentativas=-1, janela_minutos=5)

        assert "max_tentativas deve ser positivo" in str(exc_info.value)

    def test_inicializacao_janela_zero_falha(self):
        """Deve falhar se janela_minutos for zero"""
        with pytest.raises(ValueError) as exc_info:
            RateLimiter(max_tentativas=5, janela_minutos=0)

        assert "janela_minutos deve ser positivo" in str(exc_info.value)

    def test_inicializacao_janela_negativo_falha(self):
        """Deve falhar se janela_minutos for negativo"""
        with pytest.raises(ValueError) as exc_info:
            RateLimiter(max_tentativas=5, janela_minutos=-1)

        assert "janela_minutos deve ser positivo" in str(exc_info.value)

    def test_verificar_primeira_tentativa_permitida(self):
        """Primeira tentativa deve ser permitida"""
        limiter = RateLimiter(max_tentativas=5, janela_minutos=5, nome="teste")

        resultado = limiter.verificar("192.168.1.1")

        assert resultado is True

    def test_verificar_dentro_do_limite(self):
        """Tentativas dentro do limite devem ser permitidas"""
        limiter = RateLimiter(max_tentativas=5, janela_minutos=5, nome="teste")

        for i in range(5):
            resultado = limiter.verificar("192.168.1.1")
            assert resultado is True

    def test_verificar_excede_limite(self):
        """Tentativas além do limite devem ser bloqueadas"""
        limiter = RateLimiter(max_tentativas=3, janela_minutos=5, nome="teste")

        # Primeiras 3 permitidas
        for _ in range(3):
            limiter.verificar("192.168.1.1")

        # Quarta bloqueada
        with patch('util.rate_limiter.logger'):
            resultado = limiter.verificar("192.168.1.1")

        assert resultado is False

    def test_verificar_loga_warning_ao_exceder(self):
        """Deve logar warning quando limite é excedido"""
        limiter = RateLimiter(max_tentativas=2, janela_minutos=5, nome="teste")

        limiter.verificar("192.168.1.1")
        limiter.verificar("192.168.1.1")

        with patch('util.rate_limiter.logger') as mock_logger:
            limiter.verificar("192.168.1.1")
            mock_logger.warning.assert_called_once()

    def test_verificar_identificadores_isolados(self):
        """Cada identificador deve ter contagem separada"""
        limiter = RateLimiter(max_tentativas=2, janela_minutos=5, nome="teste")

        # IP 1 - 2 tentativas
        limiter.verificar("192.168.1.1")
        limiter.verificar("192.168.1.1")

        # IP 2 deve estar livre
        resultado = limiter.verificar("192.168.1.2")
        assert resultado is True

    def test_limpar_identificador_especifico(self):
        """Deve limpar apenas identificador especificado"""
        limiter = RateLimiter(max_tentativas=2, janela_minutos=5, nome="teste")

        limiter.verificar("192.168.1.1")
        limiter.verificar("192.168.1.2")

        limiter.limpar("192.168.1.1")

        assert "192.168.1.1" not in limiter.tentativas
        assert "192.168.1.2" in limiter.tentativas

    def test_limpar_todos(self):
        """Deve limpar todos os identificadores"""
        limiter = RateLimiter(max_tentativas=5, janela_minutos=5, nome="teste")

        limiter.verificar("192.168.1.1")
        limiter.verificar("192.168.1.2")
        limiter.verificar("192.168.1.3")

        limiter.limpar()

        assert len(limiter.tentativas) == 0

    def test_limpar_identificador_inexistente(self):
        """Limpar identificador inexistente não deve causar erro"""
        limiter = RateLimiter(max_tentativas=5, janela_minutos=5, nome="teste")

        # Não deve levantar exceção
        limiter.limpar("192.168.1.1")

    def test_obter_tentativas_restantes(self):
        """Deve retornar número correto de tentativas restantes"""
        limiter = RateLimiter(max_tentativas=5, janela_minutos=5, nome="teste")

        assert limiter.obter_tentativas_restantes("192.168.1.1") == 5

        limiter.verificar("192.168.1.1")
        assert limiter.obter_tentativas_restantes("192.168.1.1") == 4

        limiter.verificar("192.168.1.1")
        limiter.verificar("192.168.1.1")
        assert limiter.obter_tentativas_restantes("192.168.1.1") == 2

    def test_obter_tentativas_restantes_zero_quando_bloqueado(self):
        """Deve retornar 0 quando está bloqueado"""
        limiter = RateLimiter(max_tentativas=2, janela_minutos=5, nome="teste")

        limiter.verificar("192.168.1.1")
        limiter.verificar("192.168.1.1")

        assert limiter.obter_tentativas_restantes("192.168.1.1") == 0

    def test_obter_tempo_reset_sem_tentativas(self):
        """Deve retornar None se não há tentativas"""
        limiter = RateLimiter(max_tentativas=5, janela_minutos=5, nome="teste")

        tempo = limiter.obter_tempo_reset("192.168.1.1")

        assert tempo is None

    def test_obter_tempo_reset_bloqueado(self):
        """Deve retornar tempo até reset quando bloqueado"""
        limiter = RateLimiter(max_tentativas=2, janela_minutos=5, nome="teste")

        limiter.verificar("192.168.1.1")
        limiter.verificar("192.168.1.1")

        tempo = limiter.obter_tempo_reset("192.168.1.1")

        # Deve retornar um timedelta positivo
        assert tempo is not None
        assert tempo.total_seconds() > 0
        assert tempo.total_seconds() <= 300  # 5 minutos

    def test_obter_tempo_reset_nao_bloqueado(self):
        """Deve retornar None se não está bloqueado"""
        limiter = RateLimiter(max_tentativas=5, janela_minutos=5, nome="teste")

        limiter.verificar("192.168.1.1")

        tempo = limiter.obter_tempo_reset("192.168.1.1")

        assert tempo is None

    def test_repr(self):
        """Deve ter representação string correta"""
        limiter = RateLimiter(max_tentativas=10, janela_minutos=5, nome="meu_limiter")

        repr_str = repr(limiter)

        assert "RateLimiter" in repr_str
        assert "meu_limiter" in repr_str
        assert "10" in repr_str
        assert "5" in repr_str


class TestDynamicRateLimiter:
    """Testes para a classe DynamicRateLimiter"""

    def test_inicializacao_com_valores_padrao(self):
        """Deve inicializar com valores padrão se config não existir"""
        with patch('util.rate_limiter.config') as mock_config:
            mock_config.obter_int.side_effect = lambda k, d: d

            limiter = DynamicRateLimiter(
                chave_max="rate_limit_teste_max",
                chave_minutos="rate_limit_teste_minutos",
                padrao_max=10,
                padrao_minutos=5,
                nome="teste_dynamic"
            )

            assert limiter.max_tentativas == 10
            assert limiter.janela_minutos == 5

    def test_inicializacao_padrao_max_zero_falha(self):
        """Deve falhar se padrao_max for zero"""
        with pytest.raises(ValueError) as exc_info:
            DynamicRateLimiter(
                chave_max="teste_max",
                chave_minutos="teste_minutos",
                padrao_max=0
            )

        assert "padrao_max deve ser positivo" in str(exc_info.value)

    def test_inicializacao_padrao_minutos_zero_falha(self):
        """Deve falhar se padrao_minutos for zero"""
        with pytest.raises(ValueError) as exc_info:
            DynamicRateLimiter(
                chave_max="teste_max",
                chave_minutos="teste_minutos",
                padrao_minutos=0
            )

        assert "padrao_minutos deve ser positivo" in str(exc_info.value)

    def test_atualizar_valores_quando_mudou(self):
        """Deve atualizar valores quando config muda"""
        with patch('util.rate_limiter.config') as mock_config:
            # Valores iniciais
            mock_config.obter_int.side_effect = lambda k, d: {
                "rate_test_max": 5,
                "rate_test_minutos": 3
            }.get(k, d)

            limiter = DynamicRateLimiter(
                chave_max="rate_test_max",
                chave_minutos="rate_test_minutos",
                padrao_max=10,
                padrao_minutos=5,
                nome="teste"
            )

            assert limiter.max_tentativas == 5
            assert limiter.janela_minutos == 3

            # Simular mudança de config
            mock_config.obter_int.side_effect = lambda k, d: {
                "rate_test_max": 20,
                "rate_test_minutos": 10
            }.get(k, d)

            # Forçar atualização
            limiter._atualizar_valores()

            assert limiter.max_tentativas == 20
            assert limiter.janela_minutos == 10

    def test_verificar_atualiza_valores(self):
        """verificar() deve atualizar valores antes de verificar"""
        with patch('util.rate_limiter.config') as mock_config:
            mock_config.obter_int.side_effect = lambda k, d: d

            limiter = DynamicRateLimiter(
                chave_max="teste_max",
                chave_minutos="teste_minutos",
                padrao_max=5,
                padrao_minutos=5,
                nome="teste"
            )

            with patch.object(limiter, '_atualizar_valores') as mock_atualizar:
                limiter.verificar("192.168.1.1")
                mock_atualizar.assert_called_once()

    def test_obter_tentativas_restantes_atualiza_valores(self):
        """obter_tentativas_restantes() deve atualizar valores"""
        with patch('util.rate_limiter.config') as mock_config:
            mock_config.obter_int.side_effect = lambda k, d: d

            limiter = DynamicRateLimiter(
                chave_max="teste_max",
                chave_minutos="teste_minutos",
                padrao_max=5,
                padrao_minutos=5,
                nome="teste"
            )

            with patch.object(limiter, '_atualizar_valores') as mock_atualizar:
                limiter.obter_tentativas_restantes("192.168.1.1")
                mock_atualizar.assert_called_once()

    def test_obter_tempo_reset_atualiza_valores(self):
        """obter_tempo_reset() deve atualizar valores"""
        with patch('util.rate_limiter.config') as mock_config:
            mock_config.obter_int.side_effect = lambda k, d: d

            limiter = DynamicRateLimiter(
                chave_max="teste_max",
                chave_minutos="teste_minutos",
                padrao_max=5,
                padrao_minutos=5,
                nome="teste"
            )

            with patch.object(limiter, '_atualizar_valores') as mock_atualizar:
                limiter.obter_tempo_reset("192.168.1.1")
                mock_atualizar.assert_called_once()

    def test_repr(self):
        """Deve ter representação string correta"""
        with patch('util.rate_limiter.config') as mock_config:
            mock_config.obter_int.side_effect = lambda k, d: d

            limiter = DynamicRateLimiter(
                chave_max="minha_chave_max",
                chave_minutos="minha_chave_minutos",
                padrao_max=10,
                padrao_minutos=5,
                nome="meu_dynamic"
            )

            repr_str = repr(limiter)

            assert "DynamicRateLimiter" in repr_str
            assert "meu_dynamic" in repr_str
            assert "minha_chave_max" in repr_str


class TestObterIdentificadorCliente:
    """Testes para a função obter_identificador_cliente"""

    def test_com_client_host(self):
        """Deve retornar IP do client.host"""
        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "192.168.1.100"

        resultado = obter_identificador_cliente(request)

        assert resultado == "192.168.1.100"

    def test_sem_client(self):
        """Deve retornar 'unknown' se client não existir"""
        request = MagicMock()
        request.client = None

        resultado = obter_identificador_cliente(request)

        assert resultado == "unknown"

    def test_sem_atributo_client(self):
        """Deve retornar 'unknown' se atributo client não existir"""
        request = MagicMock(spec=[])

        resultado = obter_identificador_cliente(request)

        assert resultado == "unknown"


class TestRegistroLimiters:
    """Testes para a classe RegistroLimiters"""

    def test_registrar_limiter(self):
        """Deve registrar um limiter"""
        registro = RegistroLimiters()
        limiter = RateLimiter(max_tentativas=5, janela_minutos=5, nome="teste_registro")

        registro.registrar(limiter)

        assert "teste_registro" in registro.listar()

    def test_obter_limiter_existente(self):
        """Deve retornar limiter pelo nome"""
        registro = RegistroLimiters()
        limiter = RateLimiter(max_tentativas=5, janela_minutos=5, nome="meu_limiter")
        registro.registrar(limiter)

        resultado = registro.obter("meu_limiter")

        assert resultado is limiter

    def test_obter_limiter_inexistente(self):
        """Deve retornar None para limiter inexistente"""
        registro = RegistroLimiters()

        resultado = registro.obter("nao_existe")

        assert resultado is None

    def test_listar_limiters(self):
        """Deve listar todos os nomes de limiters"""
        registro = RegistroLimiters()
        registro.registrar(RateLimiter(max_tentativas=5, janela_minutos=5, nome="limiter_a"))
        registro.registrar(RateLimiter(max_tentativas=5, janela_minutos=5, nome="limiter_b"))

        nomes = registro.listar()

        assert "limiter_a" in nomes
        assert "limiter_b" in nomes

    def test_obter_estatisticas(self):
        """Deve retornar estatísticas dos limiters"""
        registro = RegistroLimiters()
        limiter1 = RateLimiter(max_tentativas=10, janela_minutos=5, nome="estatistica_a")
        limiter2 = RateLimiter(max_tentativas=20, janela_minutos=10, nome="estatistica_b")
        registro.registrar(limiter1)
        registro.registrar(limiter2)

        # Adicionar tentativas
        limiter1.verificar("192.168.1.1")

        stats = registro.obter_estatisticas()

        assert stats["total_limiters"] == 2
        assert "estatistica_a" in stats["limiters"]
        assert stats["limiters"]["estatistica_a"]["max_tentativas"] == 10
        assert stats["limiters"]["estatistica_a"]["tipo"] == "estatico"

    def test_obter_estatisticas_tipo_dinamico(self):
        """Deve identificar tipo 'dinamico' para DynamicRateLimiter"""
        with patch('util.rate_limiter.config') as mock_config:
            mock_config.obter_int.side_effect = lambda k, d: d

            registro = RegistroLimiters()
            limiter = DynamicRateLimiter(
                chave_max="teste_max",
                chave_minutos="teste_minutos",
                padrao_max=5,
                padrao_minutos=5,
                nome="dinamico_test"
            )
            registro.registrar(limiter)

            stats = registro.obter_estatisticas()

            assert stats["limiters"]["dinamico_test"]["tipo"] == "dinamico"

    def test_limpar_todos(self):
        """Deve limpar tentativas de todos os limiters"""
        registro = RegistroLimiters()
        limiter1 = RateLimiter(max_tentativas=10, janela_minutos=5, nome="limpar_a")
        limiter2 = RateLimiter(max_tentativas=10, janela_minutos=5, nome="limpar_b")
        registro.registrar(limiter1)
        registro.registrar(limiter2)

        limiter1.verificar("192.168.1.1")
        limiter2.verificar("192.168.1.2")

        assert len(limiter1.tentativas) > 0
        assert len(limiter2.tentativas) > 0

        registro.limpar_todos()

        assert len(limiter1.tentativas) == 0
        assert len(limiter2.tentativas) == 0


class TestDecoratorComRateLimit:
    """Testes para o decorator @com_rate_limit"""

    @pytest.fixture
    def limiter(self):
        """Cria rate limiter para testes"""
        return RateLimiter(max_tentativas=3, janela_minutos=5, nome="decorator_test")

    def test_decorator_permite_requisicao_valida(self, limiter):
        """Deve permitir requisição quando dentro do limite"""
        app = FastAPI()

        @app.get("/test")
        @com_rate_limit(limiter, registrar=False)
        async def test_endpoint(request: Request):
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_decorator_bloqueia_excesso(self, limiter):
        """Deve bloquear quando exceder limite"""
        app = FastAPI()

        @app.get("/test")
        @com_rate_limit(limiter, registrar=False)
        async def test_endpoint(request: Request):
            return {"status": "ok"}

        client = TestClient(app)

        # Primeiras 3 requisições OK
        for _ in range(3):
            response = client.get("/test")
            assert response.status_code == 200

        # Quarta deve ser bloqueada
        response = client.get("/test")
        assert response.status_code == 429

    def test_decorator_mensagem_customizada(self, limiter):
        """Deve usar mensagem de erro customizada"""
        limiter.limpar()
        # Esgota o limite
        for _ in range(3):
            limiter.verificar("testclient")

        app = FastAPI()

        @app.get("/test")
        @com_rate_limit(limiter, mensagem_erro="Minha mensagem", registrar=False)
        async def test_endpoint(request: Request):
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 429
        assert "Minha mensagem" in response.json()["detail"]

    def test_decorator_registra_no_registry(self):
        """Deve registrar limiter no registry global"""
        limiter = RateLimiter(max_tentativas=5, janela_minutos=5, nome="registrar_test_unique")

        app = FastAPI()

        @app.get("/test")
        @com_rate_limit(limiter, registrar=True)
        async def test_endpoint(request: Request):
            return {"status": "ok"}

        # O decorator deve registrar o limiter
        assert "registrar_test_unique" in registro_limiters.listar()

    def test_decorator_sem_request_continua(self):
        """Deve continuar sem rate limiting se Request não for encontrado"""
        limiter = RateLimiter(max_tentativas=1, janela_minutos=5, nome="sem_request_test")

        app = FastAPI()

        # Endpoint sem parâmetro request
        @app.get("/test")
        @com_rate_limit(limiter, registrar=False)
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # Deve funcionar mesmo excedendo o limite normal
        # porque não conseguiu encontrar o request
        with patch('util.rate_limiter.logger'):
            for _ in range(5):
                response = client.get("/test")
                assert response.status_code == 200

    def test_decorator_encontra_request_em_args(self, limiter):
        """Deve encontrar request em args (não só kwargs)"""
        limiter.limpar()

        app = FastAPI()

        @app.get("/test")
        @com_rate_limit(limiter, registrar=False)
        async def test_endpoint(request: Request):
            return {"status": "ok"}

        client = TestClient(app)

        # Deve funcionar normalmente
        response = client.get("/test")
        assert response.status_code == 200
