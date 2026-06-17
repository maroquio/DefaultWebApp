"""
Utilitário de Notificações In-App.

Fornece funções helper para criar notificações de forma simples e consistente
a partir de qualquer módulo da aplicação.

Uso básico:
    from util.notificacao_util import criar_notificacao
    from model.notificacao_model import TipoNotificacao

    # Notificação simples (tipo INFO por padrão)
    criar_notificacao(
        usuario_id=usuario_id,
        titulo="Bem-vindo!",
        mensagem="Sua conta foi criada com sucesso.",
    )

    # Com tipo e URL de ação
    criar_notificacao(
        usuario_id=usuario_id,
        titulo="Chamado respondido",
        mensagem="O administrador respondeu ao seu chamado #42.",
        tipo=TipoNotificacao.SUCESSO,
        url_acao="/chamados/42",
    )

    # Notificação de aviso
    criar_notificacao(
        usuario_id=usuario_id,
        titulo="Perfil incompleto",
        mensagem="Complete seu perfil para aproveitar todos os recursos.",
        tipo=TipoNotificacao.AVISO,
        url_acao="/usuario/perfil/editar",
    )
"""

from typing import Optional

from model.notificacao_model import TipoNotificacao
from repo import notificacao_repo
from util.logger_config import logger


def criar_notificacao(
    usuario_id: int,
    titulo: str,
    mensagem: str,
    tipo: TipoNotificacao = TipoNotificacao.INFO,
    url_acao: Optional[str] = None,
) -> Optional[int]:
    """
    Cria uma notificação in-app para um usuário.

    Esta é a função principal para criar notificações em qualquer parte
    da aplicação. Use-a nos routes sempre que uma ação importante ocorrer
    e o usuário precisar ser notificado.

    Args:
        usuario_id: ID do usuário que receberá a notificação
        titulo: Título curto da notificação (ex: 'Chamado respondido')
        mensagem: Texto descritivo (ex: 'Seu chamado #42 foi respondido.')
        tipo: Tipo visual da notificação (INFO, SUCESSO, AVISO, ERRO)
              Importar de model.notificacao_model.TipoNotificacao
        url_acao: URL para redirecionar quando o usuário clicar na notificação
                  (ex: '/chamados/42', '/pedidos/123')

    Returns:
        ID da notificação criada ou None em caso de erro

    Exemplos comuns:
        # Ao responder um chamado, notificar o dono:
        criar_notificacao(
            usuario_id=chamado.usuario_id,
            titulo="Chamado respondido",
            mensagem=f"Seu chamado '{chamado.titulo}' recebeu uma resposta.",
            tipo=TipoNotificacao.SUCESSO,
            url_acao=f"/chamados/{chamado.id}",
        )

        # Ao cadastrar novo usuário:
        criar_notificacao(
            usuario_id=novo_usuario.id,
            titulo="Bem-vindo!",
            mensagem=f"Olá {novo_usuario.nome}, sua conta foi criada com sucesso!",
        )
    """
    notificacao_id = notificacao_repo.inserir(
        usuario_id=usuario_id,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo,
        url_acao=url_acao,
    )

    if notificacao_id:
        logger.debug(f"Notificação criada (ID={notificacao_id}) para usuário {usuario_id}: {titulo}")
    else:
        logger.warning(f"Falha ao criar notificação para usuário {usuario_id}: {titulo}")

    return notificacao_id


def criar_notificacao_sucesso(usuario_id: int, titulo: str, mensagem: str, url_acao: Optional[str] = None) -> Optional[int]:
    """Atalho para criar notificação de sucesso."""
    return criar_notificacao(usuario_id, titulo, mensagem, TipoNotificacao.SUCESSO, url_acao)


def criar_notificacao_aviso(usuario_id: int, titulo: str, mensagem: str, url_acao: Optional[str] = None) -> Optional[int]:
    """Atalho para criar notificação de aviso."""
    return criar_notificacao(usuario_id, titulo, mensagem, TipoNotificacao.AVISO, url_acao)


def criar_notificacao_erro(usuario_id: int, titulo: str, mensagem: str, url_acao: Optional[str] = None) -> Optional[int]:
    """Atalho para criar notificação de erro."""
    return criar_notificacao(usuario_id, titulo, mensagem, TipoNotificacao.ERRO, url_acao)
