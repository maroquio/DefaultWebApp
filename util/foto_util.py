"""
Utilitário para gerenciamento de fotos de usuários.

Este módulo fornece funções para:
- Obter caminhos de fotos de usuários (padrão: {id:06d}.jpg)
- Criar foto padrão ao cadastrar usuário
- Salvar foto cropada do upload
"""

import base64
import binascii
import io
from pathlib import Path
from typing import Optional

from PIL import Image, UnidentifiedImageError

from util.logger_config import logger
from util.config import FOTO_PERFIL_TAMANHO_MAX
from util.config_cache import config


# Configurações
PASTA_FOTO_DEFAULT = Path("static/img")
FOTO_DEFAULT = PASTA_FOTO_DEFAULT / "user.jpg"
PASTA_FOTOS = PASTA_FOTO_DEFAULT / "usuarios"
FORMATO_FOTO = "JPEG"
QUALIDADE_FOTO = 90


def obter_caminho_foto_usuario(id: int) -> str:
    """
    Retorna o caminho absoluto da foto do usuário para uso em templates.

    Args:
        id: ID do usuário

    Returns:
        String com caminho absoluto (ex: /static/img/usuarios/000001.jpg)
    """
    return f"/{PASTA_FOTOS}/{id:06d}.jpg"


def obter_path_absoluto_foto(id: int) -> Path:
    """
    Retorna o Path absoluto do arquivo de foto do usuário.

    Args:
        id: ID do usuário

    Returns:
        Path do arquivo de foto
    """
    PASTA_FOTOS.mkdir(parents=True, exist_ok=True)
    return PASTA_FOTOS / f"{id:06d}.jpg"


def criar_foto_padrao_usuario(id: int) -> bool:
    """
    Cria uma cópia da foto padrão para o usuário.

    Copia o arquivo user.jpg para {id:06d}.jpg quando um novo usuário é criado.

    Args:
        id: ID do usuário

    Returns:
        True se criou com sucesso, False caso contrário
    """
    try:
        destino = obter_path_absoluto_foto(id)

        # Verificar se foto padrão existe
        if not FOTO_DEFAULT.exists():
            logger.warning(f"Foto padrão não encontrada em {FOTO_DEFAULT}")
            return False

        # Copiar foto padrão
        with open(FOTO_DEFAULT, "rb") as f_origem:
            with open(destino, "wb") as f_destino:
                f_destino.write(f_origem.read())

        logger.info(f"Foto padrão criada para usuário ID: {id}")
        return True

    except OSError as e:
        logger.error(f"Erro ao criar foto padrão para usuário {id}: {e}")
        return False


def salvar_foto_cropada_usuario(id: int, conteudo_base64: str) -> bool:
    """
    Salva a foto cropada do usuário enviada do frontend.

    Recebe imagem em base64, decodifica, processa e salva como JPG.

    Args:
        id: ID do usuário
        conteudo_base64: String base64 da imagem (pode incluir prefixo data:image/...)

    Returns:
        True se salvou com sucesso, False caso contrário
    """
    try:
        # Remover prefixo data:image/...;base64, se existir
        if "," in conteudo_base64:
            conteudo_base64 = conteudo_base64.split(",", 1)[1]

        # Decodificar base64
        image_data = base64.b64decode(conteudo_base64)

        # Abrir imagem com Pillow
        imagem = Image.open(io.BytesIO(image_data))

        # Converter para RGB se necessário (remove canal alpha)
        if imagem.mode in ("RGBA", "LA", "P"):
            # Criar fundo branco
            fundo: Image.Image = Image.new("RGB", imagem.size, (255, 255, 255))
            if imagem.mode == "P":
                imagem = imagem.convert("RGBA")
            fundo.paste(imagem, mask=imagem.split()[-1] if "A" in imagem.mode else None)
            imagem = fundo
        elif imagem.mode != "RGB":
            imagem = imagem.convert("RGB")

        # Redimensionar se necessário (mantendo aspect ratio)
        # Lê tamanho máximo do cache (database → .env)
        tamanho_max = config.obter_int("foto_perfil_tamanho_max", FOTO_PERFIL_TAMANHO_MAX)
        if imagem.width > tamanho_max or imagem.height > tamanho_max:
            # thumbnail redimensiona mantendo aspect ratio
            imagem.thumbnail((tamanho_max, tamanho_max), Image.Resampling.LANCZOS)
            logger.info(f"Imagem redimensionada para {imagem.width}x{imagem.height}px (max: {tamanho_max}px)")

        # Salvar como JPG
        destino = obter_path_absoluto_foto(id)
        imagem.save(destino, format=FORMATO_FOTO, quality=QUALIDADE_FOTO, optimize=True)

        logger.info(f"Foto cropada salva para usuário ID: {id}")
        return True

    except (OSError, binascii.Error, UnidentifiedImageError, ValueError) as e:
        # OSError: Erro de I/O ao salvar arquivo
        # binascii.Error: Erro ao decodificar base64
        # UnidentifiedImageError: Formato de imagem inválido ou não suportado
        # ValueError: Erro ao processar dados da imagem
        logger.error(f"Erro ao salvar foto cropada para usuário {id}: {e}")
        return False


def foto_existe(id: int) -> bool:
    """
    Verifica se a foto do usuário existe no filesystem.

    Args:
        id: ID do usuário

    Returns:
        True se a foto existe, False caso contrário
    """
    return obter_path_absoluto_foto(id).exists()


def obter_tamanho_foto(id: int) -> Optional[int]:
    """
    Retorna o tamanho da foto do usuário em bytes.

    Args:
        id: ID do usuário

    Returns:
        Tamanho em bytes ou None se foto não existe
    """
    path = obter_path_absoluto_foto(id)
    return path.stat().st_size if path.exists() else None
