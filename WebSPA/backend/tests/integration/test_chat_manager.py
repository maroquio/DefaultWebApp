"""
Testes para o módulo util/chat_manager.py

Testa o gerenciador de conexões SSE para o sistema de chat.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from util.chat_manager import GerenciadorChat, gerenciador_chat


class TestGerenciadorChat:
    """Testes para a classe GerenciadorChat"""

    @pytest.fixture
    def gerenciador(self):
        """Cria instância nova do gerenciador para cada teste"""
        g = GerenciadorChat()
        yield g
        # Cleanup: limpar conexões e queues para evitar interferência
        g._connections.clear()
        g._active_connections.clear()

    @pytest.mark.asyncio
    async def test_conectar_usuario(self, gerenciador):
        """Deve conectar usuário e retornar queue"""
        queue = await gerenciador.conectar(1)

        assert isinstance(queue, asyncio.Queue)
        assert gerenciador.esta_conectado(1)
        assert 1 in gerenciador._active_connections

    @pytest.mark.asyncio
    async def test_conectar_multiplos_usuarios(self, gerenciador):
        """Deve gerenciar múltiplas conexões"""
        await gerenciador.conectar(1)
        await gerenciador.conectar(2)
        await gerenciador.conectar(3)

        assert gerenciador.esta_conectado(1)
        assert gerenciador.esta_conectado(2)
        assert gerenciador.esta_conectado(3)

    @pytest.mark.asyncio
    async def test_desconectar_usuario(self, gerenciador):
        """Deve desconectar usuário corretamente"""
        await gerenciador.conectar(1)
        assert gerenciador.esta_conectado(1)

        await gerenciador.desconectar(1)
        assert not gerenciador.esta_conectado(1)
        assert 1 not in gerenciador._connections

    @pytest.mark.asyncio
    async def test_desconectar_usuario_nao_conectado(self, gerenciador):
        """Desconectar usuário não conectado não deve gerar erro"""
        # Não deve levantar exceção
        await gerenciador.desconectar(999)

    @pytest.mark.asyncio
    async def test_esta_conectado_usuario_conectado(self, gerenciador):
        """Deve retornar True para usuário conectado"""
        await gerenciador.conectar(1)
        assert gerenciador.esta_conectado(1) is True

    @pytest.mark.asyncio
    async def test_esta_conectado_usuario_nao_conectado(self, gerenciador):
        """Deve retornar False para usuário não conectado"""
        assert gerenciador.esta_conectado(999) is False

    @pytest.mark.asyncio
    async def test_broadcast_para_sala_usuarios_conectados(self, gerenciador):
        """Deve enviar mensagem para ambos usuários conectados"""
        queue1 = await gerenciador.conectar(1)
        queue2 = await gerenciador.conectar(2)

        mensagem = {"texto": "Olá!", "remetente_id": 1}
        await gerenciador.broadcast_para_sala("1_2", mensagem)

        # Verificar que ambas queues receberam a mensagem
        assert not queue1.empty()
        assert not queue2.empty()

        msg1 = await queue1.get()
        msg2 = await queue2.get()

        assert msg1 == mensagem
        assert msg2 == mensagem

    @pytest.mark.asyncio
    async def test_broadcast_para_sala_um_usuario_conectado(self, gerenciador):
        """Deve enviar apenas para usuário conectado"""
        queue1 = await gerenciador.conectar(1)
        # Usuário 2 não conectado

        mensagem = {"texto": "Olá!", "remetente_id": 1}
        await gerenciador.broadcast_para_sala("1_2", mensagem)

        # Apenas queue1 deve receber
        assert not queue1.empty()
        msg1 = await queue1.get()
        assert msg1 == mensagem

    @pytest.mark.asyncio
    async def test_broadcast_para_sala_nenhum_conectado(self, gerenciador):
        """Broadcast para sala sem usuários conectados não deve gerar erro"""
        mensagem = {"texto": "Olá!", "remetente_id": 1}
        # Não deve levantar exceção
        await gerenciador.broadcast_para_sala("1_2", mensagem)

    @pytest.mark.asyncio
    async def test_broadcast_para_sala_id_invalido(self, gerenciador):
        """Broadcast com sala_id inválido não deve gerar erro"""
        await gerenciador.conectar(1)

        # Formato inválido - sem underscore
        await gerenciador.broadcast_para_sala("invalido", {"texto": "teste"})

        # Formato inválido - mais de 2 partes
        await gerenciador.broadcast_para_sala("1_2_3", {"texto": "teste"})

    @pytest.mark.asyncio
    async def test_broadcast_para_sala_id_nao_numerico(self, gerenciador):
        """Broadcast com IDs não numéricos não deve gerar erro"""
        await gerenciador.conectar(1)

        # IDs não numéricos
        await gerenciador.broadcast_para_sala("abc_def", {"texto": "teste"})

    @pytest.mark.asyncio
    async def test_obter_estatisticas_inicial(self, gerenciador):
        """Estatísticas iniciais devem estar zeradas"""
        stats = gerenciador.obter_estatisticas()

        assert stats["total_conexoes"] == 0
        assert stats["usuarios_ativos"] == []
        assert stats["total_usuarios_ativos"] == 0

    @pytest.mark.asyncio
    async def test_obter_estatisticas_com_usuarios(self, gerenciador):
        """Estatísticas devem refletir conexões ativas"""
        await gerenciador.conectar(1)
        await gerenciador.conectar(5)
        await gerenciador.conectar(10)

        stats = gerenciador.obter_estatisticas()

        assert stats["total_conexoes"] == 3
        assert stats["total_usuarios_ativos"] == 3
        assert 1 in stats["usuarios_ativos"]
        assert 5 in stats["usuarios_ativos"]
        assert 10 in stats["usuarios_ativos"]

    @pytest.mark.asyncio
    async def test_obter_estatisticas_apos_desconexao(self, gerenciador):
        """Estatísticas devem atualizar após desconexão"""
        await gerenciador.conectar(1)
        await gerenciador.conectar(2)

        await gerenciador.desconectar(1)

        stats = gerenciador.obter_estatisticas()

        assert stats["total_conexoes"] == 1
        assert stats["total_usuarios_ativos"] == 1
        assert 1 not in stats["usuarios_ativos"]
        assert 2 in stats["usuarios_ativos"]

    @pytest.mark.asyncio
    async def test_reconectar_usuario(self, gerenciador):
        """Reconectar usuário deve criar nova queue"""
        queue1 = await gerenciador.conectar(1)
        await gerenciador.desconectar(1)
        queue2 = await gerenciador.conectar(1)

        # Deve ser uma nova queue
        assert queue1 is not queue2
        assert gerenciador.esta_conectado(1)


class TestGerenciadorChatSingleton:
    """Testes para a instância singleton"""

    def test_singleton_existe(self):
        """Instância singleton deve existir"""
        assert gerenciador_chat is not None
        assert isinstance(gerenciador_chat, GerenciadorChat)

    @pytest.mark.asyncio
    async def test_singleton_funcional(self):
        """Singleton deve ser funcional"""
        # Garantir estado limpo
        gerenciador_chat._connections.clear()
        gerenciador_chat._active_connections.clear()

        queue = await gerenciador_chat.conectar(999)
        assert gerenciador_chat.esta_conectado(999)

        await gerenciador_chat.desconectar(999)
        assert not gerenciador_chat.esta_conectado(999)
