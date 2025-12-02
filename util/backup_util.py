"""
Módulo de gerenciamento de backups do banco de dados SQLite.

Fornece funções para criar, listar, restaurar e excluir backups do banco de dados.
Os backups são armazenados no diretório 'backups/' com nomenclatura padronizada.
"""
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

from util.config import DATABASE_PATH
from util.logger_config import logger
from util.datetime_util import agora


# Diretório onde os backups são armazenados
BACKUP_DIR = Path("backups")

# Formato do nome do arquivo de backup
BACKUP_FILENAME_FORMAT = "backup_%Y-%m-%d_%H-%M-%S.db"
BACKUP_AUTO_FILENAME_FORMAT = "backup_auto_%Y-%m-%d_%H-%M-%S.db"

# Padrão para validação de nomes de arquivo de backup
BACKUP_FILENAME_PATTERN = "backup_"


@dataclass
class BackupInfo:
    """Informações sobre um arquivo de backup"""
    nome_arquivo: str
    caminho_completo: str
    data_criacao: datetime
    tamanho_bytes: int
    tamanho_formatado: str
    tipo: str  # "manual" ou "automático"


def _formatar_tamanho(bytes: int) -> str:
    """
    Formata tamanho em bytes para formato legível

    Args:
        bytes: Tamanho em bytes

    Returns:
        String formatada (ex: "2.5 MB", "150 KB")
    """
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024 * 1024 * 1024:
        return f"{bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes / (1024 * 1024 * 1024):.2f} GB"


def _validar_nome_arquivo(nome_arquivo: str) -> bool:
    """
    Valida nome de arquivo de backup para evitar path traversal

    Args:
        nome_arquivo: Nome do arquivo a validar

    Returns:
        True se o nome é válido, False caso contrário
    """
    # Verificar se contém caracteres perigosos
    if ".." in nome_arquivo or "/" in nome_arquivo or "\\" in nome_arquivo:
        logger.warning(f"Tentativa de path traversal detectada: {nome_arquivo}")
        return False

    # Verificar se segue o padrão esperado
    if not nome_arquivo.startswith(BACKUP_FILENAME_PATTERN):
        logger.warning(f"Nome de arquivo de backup inválido: {nome_arquivo}")
        return False

    # Verificar extensão
    if not nome_arquivo.endswith(".db"):
        logger.warning(f"Extensão de arquivo de backup inválida: {nome_arquivo}")
        return False

    return True


def _garantir_diretorio_backup() -> None:
    """Garante que o diretório de backups existe"""
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Diretório de backups criado: {BACKUP_DIR}")


def _detectar_tipo_backup(nome_arquivo: str) -> str:
    """
    Detecta se um backup é manual ou automático pelo nome

    Args:
        nome_arquivo: Nome do arquivo de backup

    Returns:
        "automático" se contém "_auto_", "manual" caso contrário
    """
    return "automático" if "_auto_" in nome_arquivo else "manual"


def _extrair_data_do_nome(nome_arquivo: str) -> Optional[datetime]:
    """
    Extrai data/hora do nome do arquivo de backup

    Args:
        nome_arquivo: Nome do arquivo (ex: "backup_2025-10-20_14-30-45.db" ou "backup_auto_2025-10-20_14-30-45.db")

    Returns:
        Objeto datetime ou None se não conseguir extrair
    """
    try:
        # Remover prefixo "backup_" ou "backup_auto_" e sufixo ".db"
        data_str = nome_arquivo.replace("backup_auto_", "").replace("backup_", "").replace(".db", "")
        # Converter para datetime
        return datetime.strptime(data_str, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        logger.warning(f"Não foi possível extrair data do nome do arquivo: {nome_arquivo}")
        return None


def _validar_integridade_backup(caminho: Path) -> tuple[bool, str]:
    """
    Valida a integridade de um arquivo de backup SQLite

    Executa PRAGMA integrity_check para verificar se o banco está corrompido.

    Args:
        caminho: Path para o arquivo de backup a validar

    Returns:
        Tupla (valido: bool, mensagem: str)
    """
    try:
        # Verificar se arquivo existe
        if not caminho.exists():
            return False, f"Arquivo não encontrado: {caminho}"

        # Verificar se arquivo tem tamanho > 0
        if caminho.stat().st_size == 0:
            return False, "Arquivo de backup está vazio"

        # Tentar abrir e validar integridade do banco
        conn = sqlite3.connect(str(caminho))
        cursor = conn.cursor()

        # PRAGMA integrity_check retorna "ok" se banco está íntegro
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()

        conn.close()

        if result and result[0] == "ok":
            logger.debug(f"Validação de integridade OK: {caminho.name}")
            return True, "Backup válido"
        else:
            mensagem = f"Falha na verificação de integridade: {result[0] if result else 'unknown'}"
            logger.error(mensagem)
            return False, mensagem

    except sqlite3.DatabaseError as e:
        mensagem = f"Banco corrompido ou inválido: {str(e)}"
        logger.error(f"Erro de integridade em {caminho.name}: {mensagem}")
        return False, mensagem

    except OSError as e:
        mensagem = f"Erro ao validar backup: {str(e)}"
        logger.error(f"Erro ao validar {caminho.name}: {mensagem}")
        return False, mensagem


def _verificar_database_pos_restauracao() -> bool:
    """
    Verifica se o banco de dados atual está válido após restauração

    Returns:
        True se banco está válido, False caso contrário
    """
    db_path = Path(DATABASE_PATH)
    valido, _ = _validar_integridade_backup(db_path)
    return valido


def criar_backup(automatico: bool = False) -> tuple[bool, str]:
    """
    Cria um novo backup do banco de dados

    Args:
        automatico: Se True, cria backup automático (prefixo "backup_auto_"),
                   se False, cria backup manual (prefixo "backup_")

    Returns:
        Tupla (sucesso: bool, mensagem: str)
    """
    try:
        # Garantir que o diretório de backups existe
        _garantir_diretorio_backup()

        # Verificar se o banco de dados existe
        db_path = Path(DATABASE_PATH)
        if not db_path.exists():
            mensagem = f"Banco de dados não encontrado: {DATABASE_PATH}"
            logger.error(mensagem)
            return False, mensagem

        # Gerar nome do arquivo de backup com timestamp
        formato = BACKUP_AUTO_FILENAME_FORMAT if automatico else BACKUP_FILENAME_FORMAT
        nome_backup = agora().strftime(formato)
        caminho_backup = BACKUP_DIR / nome_backup

        # Copiar arquivo do banco de dados
        shutil.copy2(db_path, caminho_backup)

        # Obter tamanho do backup
        tamanho = caminho_backup.stat().st_size
        tamanho_formatado = _formatar_tamanho(tamanho)

        tipo = "automático" if automatico else "manual"
        mensagem = f"Backup {tipo} criado com sucesso: {nome_backup} ({tamanho_formatado})"
        logger.info(mensagem)

        return True, mensagem

    except OSError as e:
        mensagem = f"Erro ao criar backup: {str(e)}"
        logger.error(mensagem)
        return False, mensagem


def listar_backups() -> List[BackupInfo]:
    """
    Lista todos os backups disponíveis

    Returns:
        Lista de objetos BackupInfo ordenados por data (mais recente primeiro)
    """
    try:
        # Garantir que o diretório existe
        _garantir_diretorio_backup()

        backups = []

        # Listar todos os arquivos .db no diretório de backups
        for arquivo in BACKUP_DIR.glob("backup_*.db"):
            try:
                # Obter informações do arquivo
                stat = arquivo.stat()
                tamanho = stat.st_size
                data_criacao = _extrair_data_do_nome(arquivo.name)

                # Se não conseguiu extrair data do nome, usar data de modificação do arquivo
                if data_criacao is None:
                    data_criacao = datetime.fromtimestamp(stat.st_mtime)

                # Detectar tipo do backup
                tipo = _detectar_tipo_backup(arquivo.name)

                backups.append(BackupInfo(
                    nome_arquivo=arquivo.name,
                    caminho_completo=str(arquivo),
                    data_criacao=data_criacao,
                    tamanho_bytes=tamanho,
                    tamanho_formatado=_formatar_tamanho(tamanho),
                    tipo=tipo
                ))
            except OSError as e:
                logger.warning(f"Erro ao processar arquivo de backup {arquivo.name}: {str(e)}")
                continue

        # Ordenar por data (mais recente primeiro)
        backups.sort(key=lambda x: x.data_criacao, reverse=True)

        logger.debug(f"{len(backups)} backup(s) encontrado(s)")
        return backups

    except OSError as e:
        logger.error(f"Erro ao listar backups: {str(e)}")
        return []


def restaurar_backup(nome_arquivo: str, criar_backup_antes: bool = True) -> tuple[bool, str, Optional[str]]:
    """
    Restaura um backup do banco de dados com validação de integridade

    IMPORTANTE: Esta operação sobrescreve o banco de dados atual!
    Por padrão, cria um backup automático antes de restaurar e valida
    a integridade do backup antes de aplicar.

    Args:
        nome_arquivo: Nome do arquivo de backup a restaurar
        criar_backup_antes: Se True, cria backup do estado atual antes de restaurar

    Returns:
        Tupla (sucesso: bool, mensagem: str, nome_backup_automatico: Optional[str])
    """
    caminho_backup_seguranca = None

    try:
        # Validar nome do arquivo
        if not _validar_nome_arquivo(nome_arquivo):
            mensagem = "Nome de arquivo de backup inválido"
            logger.error(f"{mensagem}: {nome_arquivo}")
            return False, mensagem, None

        # Verificar se o arquivo de backup existe
        caminho_backup = BACKUP_DIR / nome_arquivo
        if not caminho_backup.exists():
            mensagem = f"Arquivo de backup não encontrado: {nome_arquivo}"
            logger.error(mensagem)
            return False, mensagem, None

        # VALIDAÇÃO DE INTEGRIDADE: Verificar se backup está íntegro
        logger.info(f"Validando integridade do backup: {nome_arquivo}")
        valido, msg_validacao = _validar_integridade_backup(caminho_backup)
        if not valido:
            mensagem = f"Backup corrompido ou inválido! {msg_validacao}. Restauração abortada."
            logger.error(mensagem)
            return False, mensagem, None

        logger.info(f"Validação de integridade OK: {nome_arquivo}")

        # Criar backup de segurança do estado atual antes de restaurar
        nome_backup_automatico = None
        if criar_backup_antes:
            sucesso, msg = criar_backup(automatico=True)
            if sucesso:
                # Obter o último backup criado (que acabamos de criar)
                backups = listar_backups()
                if backups and backups[0].tipo == "automático":
                    nome_backup_automatico = backups[0].nome_arquivo
                    caminho_backup_seguranca = BACKUP_DIR / nome_backup_automatico
                    logger.info(f"Backup de segurança criado: {nome_backup_automatico}")
            else:
                logger.warning(f"Falha ao criar backup de segurança: {msg}")
                # Continua mesmo se falhar o backup automático

        # Restaurar backup (copiar sobre o arquivo atual)
        db_path = Path(DATABASE_PATH)
        shutil.copy2(caminho_backup, db_path)

        # VALIDAÇÃO PÓS-RESTAURAÇÃO: Verificar se banco restaurado está válido
        logger.info("Verificando integridade do banco após restauração...")
        if not _verificar_database_pos_restauracao():
            # ROLLBACK: Restaurar o backup de segurança
            logger.error("Banco corrompido após restauração! Executando rollback...")

            if caminho_backup_seguranca and caminho_backup_seguranca.exists():
                shutil.copy2(caminho_backup_seguranca, db_path)
                mensagem = (
                    f"Restauração falhou! Banco revertido para estado anterior. "
                    f"Backup '{nome_arquivo}' pode estar corrompido."
                )
                logger.error(mensagem)
                return False, mensagem, nome_backup_automatico
            else:
                mensagem = (
                    "ERRO CRÍTICO: Restauração falhou e não foi possível reverter! "
                    "Banco pode estar inconsistente."
                )
                logger.critical(mensagem)
                return False, mensagem, None

        mensagem = f"Backup restaurado com sucesso: {nome_arquivo}"
        logger.info(mensagem)

        return True, mensagem, nome_backup_automatico

    except OSError as e:
        mensagem = f"Erro ao restaurar backup: {str(e)}"
        logger.error(mensagem)

        # Tentar rollback em caso de exceção
        if caminho_backup_seguranca and caminho_backup_seguranca.exists():
            try:
                db_path = Path(DATABASE_PATH)
                shutil.copy2(caminho_backup_seguranca, db_path)
                logger.info("Rollback executado com sucesso após exceção")
                mensagem += " (Banco revertido para estado anterior)"
            except OSError as rollback_error:
                logger.critical(f"Falha no rollback: {rollback_error}")
                mensagem += " (CRÍTICO: Falha no rollback!)"

        return False, mensagem, None


def excluir_backup(nome_arquivo: str) -> tuple[bool, str]:
    """
    Exclui um arquivo de backup

    Args:
        nome_arquivo: Nome do arquivo de backup a excluir

    Returns:
        Tupla (sucesso: bool, mensagem: str)
    """
    try:
        # Validar nome do arquivo
        if not _validar_nome_arquivo(nome_arquivo):
            mensagem = "Nome de arquivo de backup inválido"
            logger.error(f"{mensagem}: {nome_arquivo}")
            return False, mensagem

        # Verificar se o arquivo existe
        caminho_backup = BACKUP_DIR / nome_arquivo
        if not caminho_backup.exists():
            mensagem = f"Arquivo de backup não encontrado: {nome_arquivo}"
            logger.error(mensagem)
            return False, mensagem

        # Excluir arquivo
        caminho_backup.unlink()

        mensagem = f"Backup excluído com sucesso: {nome_arquivo}"
        logger.info(mensagem)

        return True, mensagem

    except OSError as e:
        mensagem = f"Erro ao excluir backup: {str(e)}"
        logger.error(mensagem)
        return False, mensagem


def obter_info_backup(nome_arquivo: str) -> Optional[BackupInfo]:
    """
    Obtém informações detalhadas sobre um arquivo de backup

    Args:
        nome_arquivo: Nome do arquivo de backup

    Returns:
        Objeto BackupInfo ou None se não encontrado
    """
    try:
        # Validar nome do arquivo
        if not _validar_nome_arquivo(nome_arquivo):
            return None

        # Verificar se o arquivo existe
        caminho_backup = BACKUP_DIR / nome_arquivo
        if not caminho_backup.exists():
            return None

        # Obter informações do arquivo
        stat = caminho_backup.stat()
        tamanho = stat.st_size
        data_criacao = _extrair_data_do_nome(nome_arquivo)

        if data_criacao is None:
            data_criacao = datetime.fromtimestamp(stat.st_mtime)

        # Detectar tipo do backup
        tipo = _detectar_tipo_backup(nome_arquivo)

        return BackupInfo(
            nome_arquivo=nome_arquivo,
            caminho_completo=str(caminho_backup),
            data_criacao=data_criacao,
            tamanho_bytes=tamanho,
            tamanho_formatado=_formatar_tamanho(tamanho),
            tipo=tipo
        )

    except OSError as e:
        logger.error(f"Erro ao obter informações do backup {nome_arquivo}: {str(e)}")
        return None


def obter_caminho_backup(nome_arquivo: str) -> Optional[Path]:
    """
    Obtém o caminho completo de um arquivo de backup

    Args:
        nome_arquivo: Nome do arquivo de backup

    Returns:
        Path do arquivo ou None se inválido
    """
    if not _validar_nome_arquivo(nome_arquivo):
        return None

    caminho = BACKUP_DIR / nome_arquivo

    if not caminho.exists():
        return None

    return caminho
