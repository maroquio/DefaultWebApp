"""
Utilitário de Upload de Arquivos Genérico.

Fornece funções para upload seguro de qualquer tipo de arquivo,
com validação de tamanho, extensão e tipo MIME por assinatura de bytes.

Uso básico:
    from fastapi import UploadFile
    from util.upload_util import salvar_arquivo, validar_arquivo, TIPOS_IMAGEM

    # Validar antes de salvar
    erro = await validar_arquivo(arquivo, tipos_permitidos=TIPOS_IMAGEM, max_bytes=5_000_000)
    if erro:
        raise HTTPException(400, erro)

    # Salvar
    caminho = await salvar_arquivo(arquivo, subdiretorio="produtos")
    # retorna "static/uploads/produtos/uuid_nome.jpg"

    # No template: <img src="/{{ caminho }}">

Configuração via .env:
    UPLOAD_MAX_BYTES=10485760       # 10MB padrão
    UPLOAD_DIRETORIO=static/uploads # Pasta base de uploads
"""

import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

from util.logger_config import logger
from util.config import FOTO_MAX_UPLOAD_BYTES


# --- Configurações de Upload ---

# Diretório base para uploads (dentro de static/ para servir arquivos)
UPLOAD_DIRETORIO = Path("static/uploads")

# Tamanho máximo padrão (lido do .env via FOTO_MAX_UPLOAD_BYTES como referência)
UPLOAD_MAX_BYTES_PADRAO = FOTO_MAX_UPLOAD_BYTES  # padrão: 5MB

# --- Conjuntos de tipos permitidos (para reusar nos routes) ---

#: Imagens comuns (fotos, banners, thumbnails)
TIPOS_IMAGEM = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

#: Documentos de texto e planilhas
TIPOS_DOCUMENTO = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv"}

#: Todos os tipos acima combinados
TIPOS_IMAGEM_E_DOCUMENTO = TIPOS_IMAGEM | TIPOS_DOCUMENTO

# --- Assinaturas de bytes (magic numbers) para validação de conteúdo ---
# Evita que atacantes renomeiem arquivos maliciosos (ex: .exe → .jpg)
_MAGIC_BYTES: dict[str, list[bytes]] = {
    ".jpg":  [b"\xff\xd8\xff"],
    ".jpeg": [b"\xff\xd8\xff"],
    ".png":  [b"\x89PNG"],
    ".gif":  [b"GIF87a", b"GIF89a"],
    ".webp": [b"RIFF"],
    ".pdf":  [b"%PDF"],
}


async def validar_arquivo(
    arquivo: UploadFile,
    tipos_permitidos: Optional[set] = None,
    max_bytes: Optional[int] = None,
    verificar_magic_bytes: bool = True,
) -> Optional[str]:
    """
    Valida um arquivo enviado pelo usuário.

    Realiza validações em ordem:
    1. Arquivo não vazio
    2. Tamanho dentro do limite
    3. Extensão permitida
    4. Magic bytes (tipo MIME real) — detecta arquivos renomeados

    Args:
        arquivo: UploadFile do FastAPI
        tipos_permitidos: Set de extensões permitidas (ex: {'.jpg', '.png'})
                          Se None, aceita qualquer extensão
        max_bytes: Tamanho máximo em bytes. Se None, usa UPLOAD_MAX_BYTES_PADRAO
        verificar_magic_bytes: Se True, verifica assinaturas de bytes (mais seguro)

    Returns:
        None se arquivo válido, string com mensagem de erro caso contrário

    Exemplo:
        erro = await validar_arquivo(arquivo, tipos_permitidos=TIPOS_IMAGEM)
        if erro:
            raise HTTPException(status_code=400, detail=erro)
    """
    if not arquivo or not arquivo.filename:
        return "Nenhum arquivo enviado."

    max_bytes = max_bytes or UPLOAD_MAX_BYTES_PADRAO

    # Verificar tamanho lendo o conteúdo
    conteudo = await arquivo.read()
    await arquivo.seek(0)  # Rebobinar para leitura posterior

    if len(conteudo) == 0:
        return "Arquivo enviado está vazio."

    if len(conteudo) > max_bytes:
        tamanho_mb = max_bytes / (1024 * 1024)
        return f"Arquivo excede o tamanho máximo permitido de {tamanho_mb:.1f}MB."

    # Verificar extensão
    extensao = Path(arquivo.filename).suffix.lower()
    if tipos_permitidos and extensao not in tipos_permitidos:
        tipos_str = ", ".join(sorted(tipos_permitidos))
        return f"Tipo de arquivo não permitido. Use: {tipos_str}"

    # Verificar magic bytes para extensões conhecidas
    if verificar_magic_bytes and extensao in _MAGIC_BYTES:
        assinaturas = _MAGIC_BYTES[extensao]
        if not any(conteudo.startswith(sig) for sig in assinaturas):
            return f"Conteúdo do arquivo não corresponde à extensão '{extensao}'. Arquivo pode estar corrompido ou ser malicioso."

    return None


async def salvar_arquivo(
    arquivo: UploadFile,
    subdiretorio: str = "",
    nome_arquivo: Optional[str] = None,
    prefixo: str = "",
) -> str:
    """
    Salva um arquivo enviado pelo usuário no servidor.

    O arquivo é salvo em UPLOAD_DIRETORIO/subdiretorio/ com nome único
    baseado em UUID para evitar colisões e sobrescritas intencionais.

    Args:
        arquivo: UploadFile do FastAPI (já validado com validar_arquivo())
        subdiretorio: Subpasta dentro de UPLOAD_DIRETORIO (ex: 'produtos', 'documentos')
        nome_arquivo: Nome fixo para o arquivo (sem extensão). Se None, usa UUID aleatório
        prefixo: Prefixo opcional no nome do arquivo (ex: str(usuario_id))

    Returns:
        Caminho relativo do arquivo salvo (ex: 'static/uploads/produtos/abc123.jpg')
        Use com barra inicial para templates: f"/{caminho}"

    Raises:
        OSError: Se não for possível criar o diretório ou salvar o arquivo

    Exemplo:
        caminho = await salvar_arquivo(arquivo, subdiretorio="produtos", prefixo=str(produto_id))
        # Template: <img src="/{{ caminho }}">
    """
    # Criar diretório de destino
    pasta_destino = UPLOAD_DIRETORIO / subdiretorio if subdiretorio else UPLOAD_DIRETORIO
    pasta_destino.mkdir(parents=True, exist_ok=True)

    # Gerar nome único
    extensao = Path(arquivo.filename).suffix.lower() if arquivo.filename else ""
    if nome_arquivo:
        nome_final = f"{nome_arquivo}{extensao}"
    else:
        uid = str(uuid.uuid4()).replace("-", "")
        nome_final = f"{prefixo}_{uid}{extensao}" if prefixo else f"{uid}{extensao}"

    caminho_arquivo = pasta_destino / nome_final

    # Salvar arquivo
    await arquivo.seek(0)
    try:
        with open(caminho_arquivo, "wb") as f:
            shutil.copyfileobj(arquivo.file, f)
        logger.info(f"Arquivo salvo: {caminho_arquivo}")
        return str(caminho_arquivo)
    except OSError as e:
        logger.error(f"Erro ao salvar arquivo '{nome_final}': {e}")
        raise


def excluir_arquivo(caminho: str) -> bool:
    """
    Exclui um arquivo do servidor com segurança (path traversal protection).

    Args:
        caminho: Caminho relativo do arquivo (ex: 'static/uploads/produtos/abc.jpg')
                 Deve estar dentro de UPLOAD_DIRETORIO

    Returns:
        True se excluído com sucesso, False se arquivo não existe ou erro

    Exemplo:
        excluir_arquivo(produto.foto_path)
    """
    if not caminho:
        return False

    arquivo = Path(caminho)

    # Proteção contra path traversal: garantir que está dentro de UPLOAD_DIRETORIO
    try:
        arquivo.resolve().relative_to(UPLOAD_DIRETORIO.resolve())
    except ValueError:
        logger.warning(f"Tentativa de exclusão fora de UPLOAD_DIRETORIO: {caminho}")
        return False

    if not arquivo.exists():
        return False

    try:
        arquivo.unlink()
        logger.info(f"Arquivo excluído: {caminho}")
        return True
    except OSError as e:
        logger.error(f"Erro ao excluir arquivo '{caminho}': {e}")
        return False


def obter_url_arquivo(caminho: str) -> str:
    """
    Converte caminho relativo em URL para uso em templates.

    Args:
        caminho: Caminho relativo (ex: 'static/uploads/produtos/abc.jpg')

    Returns:
        URL com barra inicial (ex: '/static/uploads/produtos/abc.jpg')
    """
    return f"/{caminho}" if not caminho.startswith("/") else caminho


def arquivo_existe(caminho: str) -> bool:
    """
    Verifica se um arquivo de upload existe.

    Args:
        caminho: Caminho relativo do arquivo

    Returns:
        True se existe, False caso contrário
    """
    return bool(caminho) and Path(caminho).exists()


def obter_tamanho_arquivo(caminho: str) -> Optional[int]:
    """
    Retorna o tamanho de um arquivo em bytes.

    Args:
        caminho: Caminho relativo do arquivo

    Returns:
        Tamanho em bytes ou None se arquivo não existe
    """
    path = Path(caminho)
    return path.stat().st_size if path.exists() else None
