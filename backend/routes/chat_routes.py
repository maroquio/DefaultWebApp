"""
Rotas do sistema de chat em tempo real (API JSON + stream SSE).

Todos os endpoints retornam JSON, exceto ``GET /chat/stream``, que mantém
uma conexão SSE (Server-Sent Events) viva — esse é o único endpoint que
não usa ``response_model`` nem retorna JSON estruturado.
"""

# =============================================================================
# Imports
# =============================================================================

# Standard library
import asyncio
import json
from datetime import datetime, timezone
from typing import List, Optional

# Third-party
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

# DTOs (entrada)
from dtos.chat_dto import CriarSalaDTO, EnviarMensagemDTO

# Schemas (saída)
from dtos.responses.chat_response import (
    ChatHealthResponse,
    ChatMensagemResponse,
    ChatSalaResponse,
    ConversaResponse,
    EventoAtualizarContadorSSE,
    EventoNovaMensagemSSE,
    TotalNaoLidasResponse,
    UsuarioBuscaResponse,
)
from dtos.responses.comum import MensagemResponse

# Models
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import (
    chat_mensagem_repo,
    chat_participante_repo,
    chat_sala_repo,
    usuario_repo,
)

# Utilities
from util.api_helpers import checar_rate_limit
from util.auth_decorator import requer_autenticacao
from util.chat_manager import gerenciador_chat
from util.datetime_util import agora
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import DynamicRateLimiter

# =============================================================================
# Configuração do Router
# =============================================================================

router = APIRouter(prefix="/chat", tags=["Chat"])

# =============================================================================
# Rate Limiters
# =============================================================================

chat_mensagem_limiter = DynamicRateLimiter(
    chave_max="rate_limit_chat_message_max",
    chave_minutos="rate_limit_chat_message_minutos",
    padrao_max=30,
    padrao_minutos=1,
    nome="chat_mensagem",
)
chat_sala_limiter = DynamicRateLimiter(
    chave_max="rate_limit_chat_sala_max",
    chave_minutos="rate_limit_chat_sala_minutos",
    padrao_max=10,
    padrao_minutos=10,
    nome="chat_sala",
)
busca_usuarios_limiter = DynamicRateLimiter(
    chave_max="rate_limit_busca_usuarios_max",
    chave_minutos="rate_limit_busca_usuarios_minutos",
    padrao_max=30,
    padrao_minutos=1,
    nome="busca_usuarios",
)
chat_listagem_limiter = DynamicRateLimiter(
    chave_max="rate_limit_chat_listagem_max",
    chave_minutos="rate_limit_chat_listagem_minutos",
    padrao_max=60,
    padrao_minutos=1,
    nome="chat_listagem",
)


# =============================================================================
# Stream SSE (mantido como stream — NÃO é JSON estruturado)
# =============================================================================

@router.get("/stream")
@requer_autenticacao()
async def stream_mensagens(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """
    Endpoint SSE para receber mensagens em tempo real.

    Cada usuário mantém UMA conexão que recebe mensagens de TODAS as suas salas.

    Observação: o ``EventSource`` do browser envia automaticamente o cookie de
    sessão e GET é isento de CSRF, portanto não há header CSRF exigido aqui.
    Este endpoint NÃO declara ``response_model`` por ser um stream contínuo.
    """
    assert usuario_logado is not None
    usuario_id = usuario_logado.id

    async def event_generator():
        # Conectar usuário ao GerenciadorChat
        queue = await gerenciador_chat.conectar(usuario_id)
        try:
            while True:
                # Aguardar mensagem na fila
                evento = await queue.get()

                # Formatar como SSE
                sse_data = f"data: {json.dumps(evento)}\n\n"
                yield sse_data

                # Pequeno delay para não sobrecarregar
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info(f"[SSE] Conexão cancelada para usuário {usuario_id}")
        finally:
            # Desconectar ao fechar stream
            await gerenciador_chat.desconectar(usuario_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# =============================================================================
# Salas
# =============================================================================

@router.post("/salas", response_model=ChatSalaResponse, status_code=status.HTTP_201_CREATED)
@requer_autenticacao()
async def criar_ou_obter_sala(
    request: Request,
    dto: CriarSalaDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Cria ou obtém a sala de chat entre o usuário logado e outro usuário."""
    assert usuario_logado is not None
    checar_rate_limit(chat_sala_limiter, request)

    # Não pode criar sala consigo mesmo
    if dto.outro_usuario_id == usuario_logado.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível criar chat consigo mesmo.",
        )

    # Verificar se outro usuário existe
    outro_usuario = usuario_repo.obter_por_id(dto.outro_usuario_id)
    if not outro_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    # Criar ou obter sala
    sala = chat_sala_repo.criar_ou_obter_sala(usuario_logado.id, dto.outro_usuario_id)

    # Adicionar participantes se ainda não existirem
    if not chat_participante_repo.obter_por_sala_e_usuario(sala.id, usuario_logado.id):
        chat_participante_repo.adicionar_participante(sala.id, usuario_logado.id)

    if not chat_participante_repo.obter_por_sala_e_usuario(sala.id, dto.outro_usuario_id):
        chat_participante_repo.adicionar_participante(sala.id, dto.outro_usuario_id)

    return ChatSalaResponse.de_sala(sala)


# =============================================================================
# Conversas e mensagens
# =============================================================================

@router.get("/conversas", response_model=List[ConversaResponse])
@requer_autenticacao()
async def listar_conversas(
    request: Request,
    limit: int = 12,
    offset: int = 0,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Lista conversas do usuário (sala, outro participante, última mensagem e não lidas)."""
    assert usuario_logado is not None
    checar_rate_limit(chat_listagem_limiter, request)

    usuario_id = usuario_logado.id

    # Obter todas as participações do usuário
    participacoes = chat_participante_repo.listar_por_usuario(usuario_id)

    conversas: List[ConversaResponse] = []
    for participacao in participacoes:
        sala = chat_sala_repo.obter_por_id(participacao.sala_id)
        if not sala:
            continue

        # Obter o outro participante da sala
        participantes = chat_participante_repo.listar_por_sala(sala.id)
        outro_participante = next(
            (p for p in participantes if p.usuario_id != usuario_id),
            None,
        )
        if not outro_participante:
            continue

        # Obter dados do outro usuário
        outro_usuario = usuario_repo.obter_por_id(outro_participante.usuario_id)
        if not outro_usuario:
            continue

        ultima_mensagem = chat_mensagem_repo.obter_ultima_mensagem_sala(sala.id)
        nao_lidas = chat_participante_repo.contar_mensagens_nao_lidas(sala.id, usuario_id)

        conversas.append(
            ConversaResponse.de_dados(sala, outro_usuario, ultima_mensagem, nao_lidas)
        )

    # Ordenar por última atividade (mais recente primeiro)
    _epoch_min = datetime.min.replace(tzinfo=timezone.utc)
    conversas.sort(
        key=lambda c: c.ultima_atividade or _epoch_min,
        reverse=True,
    )

    # Aplicar paginação
    return conversas[offset:offset + limit]


@router.get("/mensagens/{sala_id}", response_model=List[ChatMensagemResponse])
@requer_autenticacao()
async def listar_mensagens(
    request: Request,
    sala_id: str,
    limit: int = 50,
    offset: int = 0,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Lista mensagens de uma sala específica com paginação."""
    assert usuario_logado is not None
    checar_rate_limit(chat_listagem_limiter, request)

    usuario_id = usuario_logado.id

    # Verificar se usuário participa da sala
    if not chat_participante_repo.obter_por_sala_e_usuario(sala_id, usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a esta sala.",
        )

    mensagens = chat_mensagem_repo.listar_por_sala(sala_id, limit, offset)
    return [ChatMensagemResponse.de_mensagem(msg) for msg in mensagens]


@router.post(
    "/mensagens",
    response_model=ChatMensagemResponse,
    status_code=status.HTTP_201_CREATED,
)
@requer_autenticacao()
async def enviar_mensagem(
    request: Request,
    dto: EnviarMensagemDTO,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Envia uma mensagem em uma sala e faz broadcast via SSE para os participantes."""
    assert usuario_logado is not None
    checar_rate_limit(chat_mensagem_limiter, request)

    usuario_id = usuario_logado.id

    # Verificar se usuário participa da sala
    if not chat_participante_repo.obter_por_sala_e_usuario(dto.sala_id, usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a esta sala.",
        )

    # Verificar se sala existe
    if not chat_sala_repo.obter_por_id(dto.sala_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada.",
        )

    # Inserir mensagem
    nova_mensagem = chat_mensagem_repo.inserir(dto.sala_id, usuario_id, dto.mensagem)

    # Atualizar última atividade da sala
    chat_sala_repo.atualizar_ultima_atividade(dto.sala_id)

    resposta = ChatMensagemResponse.de_mensagem(nova_mensagem)

    # Broadcast via SSE para ambos os participantes (payload tipado: ver
    # EventoNovaMensagemSSE; reusa `resposta`, que já tem lida_em=None por ser
    # mensagem recém-inserida).
    evento_sse = EventoNovaMensagemSSE(sala_id=nova_mensagem.sala_id, mensagem=resposta)
    await gerenciador_chat.broadcast_para_sala(
        dto.sala_id, evento_sse.model_dump(mode="json")
    )

    return resposta


@router.post("/mensagens/lidas/{sala_id}", response_model=MensagemResponse)
@requer_autenticacao()
async def marcar_como_lidas(
    request: Request,
    sala_id: str,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Marca todas as mensagens de uma sala como lidas para o usuário logado."""
    assert usuario_logado is not None
    usuario_id = usuario_logado.id

    # Verificar se usuário participa da sala
    if not chat_participante_repo.obter_por_sala_e_usuario(sala_id, usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a esta sala.",
        )

    chat_mensagem_repo.marcar_como_lidas(sala_id, usuario_id)
    chat_participante_repo.atualizar_ultima_leitura(sala_id, usuario_id)

    # Notificar via SSE para atualizar contador (payload tipado)
    evento_sse = EventoAtualizarContadorSSE(sala_id=sala_id)
    await gerenciador_chat.broadcast_para_sala(
        sala_id, evento_sse.model_dump(mode="json")
    )

    return MensagemResponse(message="Mensagens marcadas como lidas.")


@router.get("/mensagens/nao-lidas/total", response_model=TotalNaoLidasResponse)
@requer_autenticacao()
async def contar_nao_lidas_total(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """Conta o total de mensagens não lidas em todas as salas do usuário."""
    assert usuario_logado is not None
    usuario_id = usuario_logado.id

    participacoes = chat_participante_repo.listar_por_usuario(usuario_id)

    total_nao_lidas = 0
    for participacao in participacoes:
        total_nao_lidas += chat_participante_repo.contar_mensagens_nao_lidas(
            participacao.sala_id, usuario_id
        )

    return TotalNaoLidasResponse(total=total_nao_lidas)


# =============================================================================
# Busca de usuários
# =============================================================================

@router.get("/usuarios/buscar", response_model=List[UsuarioBuscaResponse])
@requer_autenticacao()
async def buscar_usuarios(
    request: Request,
    q: str,
    usuario_logado: Optional[UsuarioLogado] = None,
):
    """
    Busca usuários por termo (autocomplete).

    Exclui o próprio usuário e administradores dos resultados — admins só são
    contactados via sistema de chamados.
    """
    assert usuario_logado is not None
    checar_rate_limit(busca_usuarios_limiter, request)

    if len(q) < 2:
        return []

    usuarios = usuario_repo.buscar_por_termo(q, limit=10)

    usuarios_filtrados = [
        u
        for u in usuarios
        if u.id != usuario_logado.id and u.perfil != Perfil.ADMIN.value
    ]

    return [UsuarioBuscaResponse.de_usuario(u) for u in usuarios_filtrados]


# =============================================================================
# Health
# =============================================================================

@router.get("/health", response_model=ChatHealthResponse)
async def chat_health():
    """Health check do sistema de chat (conexões SSE ativas)."""
    estatisticas = gerenciador_chat.obter_estatisticas()
    return ChatHealthResponse(
        status="healthy",
        conexoes_ativas=estatisticas["total_usuarios_ativos"],
        timestamp=agora(),
    )
