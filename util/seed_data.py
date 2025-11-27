from repo import usuario_repo
from model.usuario_model import Usuario
from util.security import criar_hash_senha
from util.logger_config import logger
from util.perfis import Perfil


def carregar_usuarios_seed():
    """
    Carrega usuários padrão gerando automaticamente 1 usuário para cada perfil do enum.

    Só insere usuários se não houver nenhum usuário cadastrado no banco.

    Formato gerado:
    - id: sequencial iniciando em 1
    - nome: {Perfil} Padrão
    - email: {perfil}@email.com
    - senha: 1234aA@#
    - perfil: {Perfil}
    """
    # Verificar se já existem usuários cadastrados
    quantidade_usuarios = usuario_repo.obter_quantidade()
    if quantidade_usuarios > 0:
        logger.info(f"Já existem {quantidade_usuarios} usuários cadastrados. Seed não será executado.")
        return

    usuarios_criados = 0
    usuarios_com_erro = 0

    logger.info("Nenhum usuário encontrado. Iniciando seed de usuários padrão...")

    # Itera sobre todos os perfis definidos no enum
    for perfil_enum in Perfil:
        try:
            perfil_valor = perfil_enum.value

            # Gera dados do usuário baseado no perfil
            nome = f"{perfil_valor} Padrão"
            email = f"padrao@{perfil_valor.lower()}.com"
            senha_plain = "1234aA@#"

            # Criar usuário
            usuario = Usuario(
                id=0,
                nome=nome,
                email=email,
                senha=criar_hash_senha(senha_plain),
                perfil=perfil_valor
            )

            usuario_id = usuario_repo.inserir(usuario)
            if usuario_id:
                logger.info(f"✓ Usuário {email} criado com sucesso (ID: {usuario_id})")
                usuarios_criados += 1
            else:
                logger.error(f"✗ Falha ao inserir usuário {email} no banco")
                usuarios_com_erro += 1

        except Exception as e:
            logger.error(f"✗ Erro ao processar usuário do perfil {perfil_enum.name}: {e}")
            usuarios_com_erro += 1

    # Resumo
    logger.info(f"Resumo do seed de usuários: {usuarios_criados} criados, {usuarios_com_erro} com erro")


def inicializar_dados():
    """Inicializa todos os dados seed"""
    logger.info("=" * 50)
    logger.info("Iniciando carga de dados seed...")
    logger.info("=" * 50)

    try:
        carregar_usuarios_seed()
        logger.info("=" * 50)
        logger.info("Dados seed carregados!")
        logger.info("=" * 50)
    except Exception as e:
        logger.error(f"Erro crítico ao inicializar dados seed: {e}", exc_info=True)
