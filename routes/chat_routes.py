"""
Rotas para o sistema de chat em tempo real.
"""

# =============================================================================
# Imports
# =============================================================================

# Standard library
import json
import asyncio
from typing import Optional

# Third-party
from fastapi import APIRouter, Request, status, HTTPException, Form
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import ValidationError

# DTOs
from dtos.chat_dto import CriarSalaDTO, EnviarMensagemDTO

# Models
from model.usuario_logado_model import UsuarioLogado

# Repositories
from repo import chat_sala_repo, chat_participante_repo, chat_mensagem_repo, usuario_repo

# Utilities
from util.auth_decorator import requer_autenticacao
from util.chat_manager import gerenciador_chat
from util.datetime_util import agora
from util.foto_util import obter_caminho_foto_usuario
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente

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


@router.get("/stream")
@requer_autenticacao()
async def stream_mensagens(request: Request, usuario_logado: Optional[UsuarioLogado] = None):
    """
    Endpoint SSE para receber mensagens em tempo real.
    Cada usuário mantém UMA conexão que recebe mensagens de TODAS as suas salas.
    """
    if not usuario_logado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
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
        }
    )


@router.post("/salas")
@requer_autenticacao()
async def criar_ou_obter_sala(
    request: Request,
    outro_usuario_id: int = Form(...),
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Cria ou obtém uma sala de chat entre o usuário logado e outro usuário.
    """
    if not usuario_logado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not chat_sala_limiter.verificar(ip):
        logger.warning(f"Rate limit excedido para criação de sala de chat - IP: {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas de criação de salas. Aguarde alguns minutos."
        )

    try:
        # Validar DTO
        dto = CriarSalaDTO(outro_usuario_id=outro_usuario_id)

        # Não pode criar sala consigo mesmo
        if dto.outro_usuario_id == usuario_logado.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível criar chat consigo mesmo."
            )

        # Verificar se outro usuário existe
        outro_usuario = usuario_repo.obter_por_id(dto.outro_usuario_id)
        if not outro_usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )

        # Criar ou obter sala
        sala = chat_sala_repo.criar_ou_obter_sala(usuario_logado.id, dto.outro_usuario_id)

        # Adicionar participantes se sala foi recém-criada
        participante1 = chat_participante_repo.obter_por_sala_e_usuario(sala.id, usuario_logado.id)
        if not participante1:
            chat_participante_repo.adicionar_participante(sala.id, usuario_logado.id)

        participante2 = chat_participante_repo.obter_por_sala_e_usuario(sala.id, dto.outro_usuario_id)
        if not participante2:
            chat_participante_repo.adicionar_participante(sala.id, dto.outro_usuario_id)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"sala_id": sala.id}
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/conversas")
@requer_autenticacao()
async def listar_conversas(
    request: Request,
    limit: int = 12,
    offset: int = 0,
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Lista conversas do usuário (salas com última mensagem e contador de não lidas).
    """
    if not usuario_logado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not chat_listagem_limiter.verificar(ip):
        logger.warning(f"Rate limit excedido para listagem de conversas - IP: {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas requisições de listagem. Aguarde alguns minutos."
        )

    usuario_id = usuario_logado.id

    # Obter todas as participações do usuário
    participacoes = chat_participante_repo.listar_por_usuario(usuario_id)

    conversas = []
    for participacao in participacoes:
        sala = chat_sala_repo.obter_por_id(participacao.sala_id)
        if not sala:
            continue

        # Obter o outro participante da sala
        participantes = chat_participante_repo.listar_por_sala(sala.id)
        outro_participante = next(
            (p for p in participantes if p.usuario_id != usuario_id),
            None
        )

        if not outro_participante:
            continue

        # Obter dados do outro usuário
        outro_usuario = usuario_repo.obter_por_id(outro_participante.usuario_id)
        if not outro_usuario:
            continue

        # Obter última mensagem
        ultima_mensagem = chat_mensagem_repo.obter_ultima_mensagem_sala(sala.id)

        # Contar não lidas
        nao_lidas = chat_participante_repo.contar_mensagens_nao_lidas(sala.id, usuario_id)

        conversa = {
            "sala_id": sala.id,
            "outro_usuario": {
                "id": outro_usuario.id,
                "nome": outro_usuario.nome,
                "email": outro_usuario.email,
                "foto_url": obter_caminho_foto_usuario(outro_usuario.id)
            },
            "ultima_mensagem": {
                "mensagem": ultima_mensagem.mensagem,
                "data_envio": ultima_mensagem.data_envio.isoformat() if ultima_mensagem.data_envio else None,
                "usuario_id": ultima_mensagem.usuario_id
            } if ultima_mensagem else None,
            "nao_lidas": nao_lidas,
            "ultima_atividade": sala.ultima_atividade.isoformat() if sala.ultima_atividade else ""
        }
        conversas.append(conversa)

    # Ordenar por última atividade (mais recente primeiro)
    conversas.sort(key=lambda c: c["ultima_atividade"], reverse=True)

    # Aplicar paginação
    conversas_paginadas = conversas[offset:offset + limit]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=conversas_paginadas
    )


@router.get("/mensagens/{sala_id}")
@requer_autenticacao()
async def listar_mensagens(
    request: Request,
    sala_id: str,
    limit: int = 50,
    offset: int = 0,
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Lista mensagens de uma sala específica com paginação.
    """
    if not usuario_logado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not chat_listagem_limiter.verificar(ip):
        logger.warning(f"Rate limit excedido para listagem de mensagens - IP: {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas requisições de listagem. Aguarde alguns minutos."
        )

    usuario_id = usuario_logado.id

    # Verificar se usuário participa da sala
    participante = chat_participante_repo.obter_por_sala_e_usuario(sala_id, usuario_id)
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a esta sala."
        )

    # Obter mensagens
    mensagens = chat_mensagem_repo.listar_por_sala(sala_id, limit, offset)

    mensagens_json = [
        {
            "id": msg.id,
            "sala_id": msg.sala_id,
            "usuario_id": msg.usuario_id,
            "mensagem": msg.mensagem,
            "data_envio": msg.data_envio.isoformat() if msg.data_envio else None,
            "lida_em": msg.lida_em.isoformat() if msg.lida_em else None
        }
        for msg in mensagens
    ]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=mensagens_json
    )


@router.post("/mensagens")
@requer_autenticacao()
async def enviar_mensagem(
    request: Request,
    sala_id: str = Form(...),
    mensagem: str = Form(...),
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Envia uma mensagem em uma sala.
    """
    if not usuario_logado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not chat_mensagem_limiter.verificar(ip):
        logger.warning(f"Rate limit excedido para envio de mensagem no chat - IP: {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas mensagens enviadas. Aguarde alguns minutos."
        )

    try:
        # Validar DTO
        dto = EnviarMensagemDTO(sala_id=sala_id, mensagem=mensagem)

        usuario_id = usuario_logado.id

        # Verificar se usuário participa da sala
        participante = chat_participante_repo.obter_por_sala_e_usuario(dto.sala_id, usuario_id)
        if not participante:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem acesso a esta sala."
            )

        # Verificar se sala existe
        sala = chat_sala_repo.obter_por_id(dto.sala_id)
        if not sala:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sala não encontrada."
            )

        # Inserir mensagem
        nova_mensagem = chat_mensagem_repo.inserir(dto.sala_id, usuario_id, dto.mensagem)

        # Atualizar última atividade da sala
        chat_sala_repo.atualizar_ultima_atividade(dto.sala_id)

        # Broadcast via SSE para ambos participantes
        mensagem_sse = {
            "tipo": "nova_mensagem",
            "sala_id": nova_mensagem.sala_id,
            "mensagem": {
                "id": nova_mensagem.id,
                "sala_id": nova_mensagem.sala_id,
                "usuario_id": nova_mensagem.usuario_id,
                "mensagem": nova_mensagem.mensagem,
                "data_envio": nova_mensagem.data_envio.isoformat() if nova_mensagem.data_envio else None,
                "lida_em": None
            }
        }
        await gerenciador_chat.broadcast_para_sala(dto.sala_id, mensagem_sse)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "id": nova_mensagem.id,
                "sala_id": nova_mensagem.sala_id,
                "usuario_id": nova_mensagem.usuario_id,
                "mensagem": nova_mensagem.mensagem,
                "data_envio": nova_mensagem.data_envio.isoformat() if nova_mensagem.data_envio else None,
                "lida_em": None
            }
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/mensagens/lidas/{sala_id}")
@requer_autenticacao()
async def marcar_como_lidas(
    request: Request,
    sala_id: str,
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Marca todas as mensagens de uma sala como lidas para o usuário logado.
    """
    if not usuario_logado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
    usuario_id = usuario_logado.id

    # Verificar se usuário participa da sala
    participante = chat_participante_repo.obter_por_sala_e_usuario(sala_id, usuario_id)
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a esta sala."
        )

    # Marcar mensagens como lidas
    chat_mensagem_repo.marcar_como_lidas(sala_id, usuario_id)

    # Atualizar última leitura do participante
    chat_participante_repo.atualizar_ultima_leitura(sala_id, usuario_id)

    # Notificar via SSE para atualizar contador
    await gerenciador_chat.broadcast_para_sala(sala_id, {
        "tipo": "atualizar_contador",
        "sala_id": sala_id
    })

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"sucesso": True}
    )


@router.get("/usuarios/buscar")
@requer_autenticacao()
async def buscar_usuarios(
    request: Request,
    q: str,
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Busca usuários por termo (para autocomplete).
    Exclui o próprio usuário e administradores dos resultados.
    Administradores só podem ser contactados via sistema de chamados.
    """
    if not usuario_logado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not busca_usuarios_limiter.verificar(ip):
        logger.warning(f"Rate limit excedido para busca de usuários - IP: {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas buscas. Aguarde alguns minutos."
        )

    if len(q) < 2:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=[]
        )

    # Buscar usuários
    usuarios = usuario_repo.buscar_por_termo(q, limit=10)

    # Excluir o próprio usuário e administradores dos resultados
    usuarios_filtrados = [
        u for u in usuarios
        if u.id != usuario_logado.id and u.perfil != Perfil.ADMIN.value
    ]

    usuarios_json = [
        {
            "id": u.id,
            "nome": u.nome,
            "email": u.email,
            "foto_url": obter_caminho_foto_usuario(u.id)
        }
        for u in usuarios_filtrados
    ]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=usuarios_json
    )


@router.get("/mensagens/nao-lidas/total")
@requer_autenticacao()
async def contar_nao_lidas_total(
    request: Request,
    usuario_logado: Optional[UsuarioLogado] = None
):
    """
    Conta o total de mensagens não lidas em todas as salas do usuário.
    """
    if not usuario_logado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
    usuario_id = usuario_logado.id

    # Obter todas as participações do usuário
    participacoes = chat_participante_repo.listar_por_usuario(usuario_id)

    total_nao_lidas = 0
    for participacao in participacoes:
        nao_lidas = chat_participante_repo.contar_mensagens_nao_lidas(
            participacao.sala_id,
            usuario_id
        )
        total_nao_lidas += nao_lidas

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"total": total_nao_lidas}
    )


@router.get("/health")
async def chat_health():
    """Health check do sistema de chat."""
    estatisticas = gerenciador_chat.obter_estatisticas()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "conexoes_ativas": estatisticas["total_usuarios_ativos"],
            "timestamp": agora().isoformat()
        }
    )
