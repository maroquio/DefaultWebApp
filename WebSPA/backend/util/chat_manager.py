"""
Gerenciador de conexões SSE do chat.
Mantém conexões ativas e faz broadcast de mensagens para usuários conectados.
"""
import asyncio
from typing import Dict, Set
from util.logger_config import logger


class GerenciadorChat:
    """
    Gerencia conexões SSE para o sistema de chat.

    Cada usuário tem UMA conexão SSE que recebe mensagens de TODAS as suas salas.
    Quando uma mensagem é enviada em uma sala, o GerenciadorChat faz broadcast
    para ambos os participantes da sala (se estiverem conectados).
    """

    def __init__(self):
        # Dicionário de filas: usuario_id -> asyncio.Queue
        self._connections: Dict[int, asyncio.Queue] = {}
        # Set de usuários com conexão ativa
        self._active_connections: Set[int] = set()

    async def conectar(self, usuario_id: int) -> asyncio.Queue:
        """
        Registra nova conexão SSE para um usuário.

        Args:
            usuario_id: ID do usuário conectando

        Returns:
            Queue para envio de mensagens SSE
        """
        queue = asyncio.Queue()
        self._connections[usuario_id] = queue
        self._active_connections.add(usuario_id)

        logger.info(
            f"[GerenciadorChat] Usuário {usuario_id} conectado. "
            f"Total conexões: {len(self._active_connections)}"
        )

        return queue

    async def desconectar(self, usuario_id: int):
        """
        Remove conexão SSE de um usuário.

        Args:
            usuario_id: ID do usuário desconectando
        """
        if usuario_id in self._connections:
            del self._connections[usuario_id]

        if usuario_id in self._active_connections:
            self._active_connections.remove(usuario_id)

        logger.info(
            f"[GerenciadorChat] Usuário {usuario_id} desconectado. "
            f"Total conexões: {len(self._active_connections)}"
        )

    async def broadcast_para_sala(self, sala_id: str, mensagem_dict: dict):
        """
        Envia mensagem SSE para ambos os participantes de uma sala.

        Args:
            sala_id: ID da sala (formato: "menor_id_maior_id")
            mensagem_dict: Dicionário com dados da mensagem a enviar
        """
        # Extrair IDs dos usuários do sala_id
        partes = sala_id.split("_")
        if len(partes) != 2:
            logger.error(f"[ChatManager] sala_id inválido: {sala_id}")
            return

        try:
            usuario1_id = int(partes[0])
            usuario2_id = int(partes[1])
        except ValueError:
            logger.error(f"[ChatManager] Erro ao parsear IDs do sala_id: {sala_id}")
            return

        # Enviar para cada participante se estiver conectado
        for usuario_id in [usuario1_id, usuario2_id]:
            if usuario_id in self._connections:
                await self._connections[usuario_id].put(mensagem_dict)
                logger.debug(f"[ChatManager] Mensagem enviada para usuário {usuario_id} via SSE")
            else:
                logger.debug(f"[ChatManager] Usuário {usuario_id} não está conectado (não receberá via SSE)")

    def esta_conectado(self, usuario_id: int) -> bool:
        """
        Verifica se um usuário está conectado.

        Args:
            usuario_id: ID do usuário

        Returns:
            True se conectado, False caso contrário
        """
        return usuario_id in self._active_connections

    def obter_estatisticas(self) -> dict:
        """
        Retorna estatísticas do chat manager.

        Returns:
            Dicionário com estatísticas
        """
        return {
            "total_conexoes": len(self._connections),
            "usuarios_ativos": list(self._active_connections),
            "total_usuarios_ativos": len(self._active_connections)
        }


# Instância singleton global
gerenciador_chat = GerenciadorChat()
