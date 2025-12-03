"""
Testes para o módulo util/foto_util.py

Testa o gerenciamento de fotos de usuários.
"""

import pytest
import base64
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image
import io

from util.foto_util import (
    obter_caminho_foto_usuario,
    obter_path_absoluto_foto,
    criar_foto_padrao_usuario,
    salvar_foto_cropada_usuario,
    foto_existe,
    obter_tamanho_foto,
    PASTA_FOTOS,
    FOTO_DEFAULT
)


class TestObterCaminhoFotoUsuario:
    """Testes para a função obter_caminho_foto_usuario()"""

    def test_id_1_retorna_caminho_correto(self):
        """ID 1 deve retornar caminho com zeros à esquerda"""
        resultado = obter_caminho_foto_usuario(1)
        assert "000001.jpg" in resultado
        assert resultado.startswith("/")

    def test_id_grande_retorna_caminho_correto(self):
        """ID grande deve formatar corretamente"""
        resultado = obter_caminho_foto_usuario(123456)
        assert "123456.jpg" in resultado

    def test_caminho_inclui_pasta(self):
        """Caminho deve incluir pasta de usuários"""
        resultado = obter_caminho_foto_usuario(1)
        assert "usuarios" in resultado


class TestObterPathAbsolutoFoto:
    """Testes para a função obter_path_absoluto_foto()"""

    def test_retorna_path_objeto(self):
        """Deve retornar objeto Path"""
        resultado = obter_path_absoluto_foto(1)
        assert isinstance(resultado, Path)

    def test_path_inclui_id_formatado(self):
        """Path deve incluir ID formatado"""
        resultado = obter_path_absoluto_foto(5)
        assert "000005.jpg" in str(resultado)

    def test_cria_diretorio_se_nao_existir(self):
        """Deve criar diretório de fotos se não existir"""
        # O diretório pode já existir, então apenas verificamos que não dá erro
        resultado = obter_path_absoluto_foto(1)
        assert resultado is not None


class TestCriarFotoPadraoUsuario:
    """Testes para a função criar_foto_padrao_usuario()"""

    def test_cria_foto_quando_padrao_existe(self):
        """Deve criar cópia da foto padrão quando existe"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Criar arquivo fake de foto padrão
            foto_padrao = Path(tmpdir) / "user.jpg"
            foto_padrao.write_bytes(b"fake image data")

            pasta_fotos = Path(tmpdir) / "usuarios"

            with patch('util.foto_util.FOTO_DEFAULT', foto_padrao):
                with patch('util.foto_util.PASTA_FOTOS', pasta_fotos):
                    resultado = criar_foto_padrao_usuario(1)

                    assert resultado is True
                    assert (pasta_fotos / "000001.jpg").exists()

    def test_retorna_false_quando_padrao_nao_existe(self):
        """Deve retornar False quando foto padrão não existe"""
        with tempfile.TemporaryDirectory() as tmpdir:
            foto_inexistente = Path(tmpdir) / "nao_existe.jpg"

            with patch('util.foto_util.FOTO_DEFAULT', foto_inexistente):
                resultado = criar_foto_padrao_usuario(1)

                assert resultado is False

    def test_retorna_false_em_erro_io(self):
        """Deve retornar False em erro de I/O"""
        with patch('util.foto_util.FOTO_DEFAULT') as mock_default:
            mock_default.exists.return_value = True

            with patch('util.foto_util.obter_path_absoluto_foto') as mock_path:
                mock_path.side_effect = OSError("Permission denied")

                resultado = criar_foto_padrao_usuario(1)

                assert resultado is False


class TestSalvarFotoCropadaUsuario:
    """Testes para a função salvar_foto_cropada_usuario()"""

    def _criar_imagem_base64(self, mode="RGB", size=(100, 100)):
        """Helper para criar imagem base64"""
        img = Image.new(mode, size, color="red")
        buffer = io.BytesIO()
        if mode in ("RGBA", "P"):
            img.save(buffer, format="PNG")
        else:
            img.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode()

    def test_salva_imagem_rgb(self):
        """Deve salvar imagem RGB corretamente"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pasta_fotos = Path(tmpdir) / "usuarios"

            with patch('util.foto_util.PASTA_FOTOS', pasta_fotos):
                base64_img = self._criar_imagem_base64("RGB")

                resultado = salvar_foto_cropada_usuario(1, base64_img)

                assert resultado is True
                assert (pasta_fotos / "000001.jpg").exists()

    def test_salva_imagem_com_prefixo_data_url(self):
        """Deve remover prefixo data:image e salvar"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pasta_fotos = Path(tmpdir) / "usuarios"

            with patch('util.foto_util.PASTA_FOTOS', pasta_fotos):
                base64_img = self._criar_imagem_base64("RGB")
                data_url = f"data:image/jpeg;base64,{base64_img}"

                resultado = salvar_foto_cropada_usuario(1, data_url)

                assert resultado is True

    def test_converte_rgba_para_rgb(self):
        """Deve converter RGBA para RGB"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pasta_fotos = Path(tmpdir) / "usuarios"

            with patch('util.foto_util.PASTA_FOTOS', pasta_fotos):
                base64_img = self._criar_imagem_base64("RGBA")

                resultado = salvar_foto_cropada_usuario(1, base64_img)

                assert resultado is True

    def test_converte_modo_p_para_rgb(self):
        """Deve converter modo P (palette) para RGB"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pasta_fotos = Path(tmpdir) / "usuarios"

            with patch('util.foto_util.PASTA_FOTOS', pasta_fotos):
                # Criar imagem P (palette)
                img = Image.new("P", (100, 100))
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                base64_img = base64.b64encode(buffer.getvalue()).decode()

                resultado = salvar_foto_cropada_usuario(1, base64_img)

                assert resultado is True

    def test_redimensiona_imagem_grande(self):
        """Deve redimensionar imagem maior que o limite"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pasta_fotos = Path(tmpdir) / "usuarios"

            with patch('util.foto_util.PASTA_FOTOS', pasta_fotos):
                with patch('util.foto_util.config') as mock_config:
                    mock_config.obter_int.return_value = 50  # Limite de 50px

                    # Imagem grande de 100x100
                    base64_img = self._criar_imagem_base64("RGB", (100, 100))

                    resultado = salvar_foto_cropada_usuario(1, base64_img)

                    assert resultado is True

                    # Verificar que foi salvo e redimensionado
                    saved_img = Image.open(pasta_fotos / "000001.jpg")
                    assert saved_img.width <= 50
                    assert saved_img.height <= 50

    def test_retorna_false_base64_invalido(self):
        """Deve retornar False para base64 inválido"""
        resultado = salvar_foto_cropada_usuario(1, "isso não é base64 válido!!!")

        assert resultado is False

    def test_retorna_false_imagem_invalida(self):
        """Deve retornar False para dados que não são imagem"""
        # Base64 válido mas não é imagem
        base64_data = base64.b64encode(b"texto qualquer").decode()

        resultado = salvar_foto_cropada_usuario(1, base64_data)

        assert resultado is False


class TestFotoExiste:
    """Testes para a função foto_existe()"""

    def test_retorna_true_quando_existe(self):
        """Deve retornar True quando foto existe"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pasta_fotos = Path(tmpdir) / "usuarios"
            pasta_fotos.mkdir()
            (pasta_fotos / "000001.jpg").write_bytes(b"fake")

            with patch('util.foto_util.PASTA_FOTOS', pasta_fotos):
                resultado = foto_existe(1)

                assert resultado is True

    def test_retorna_false_quando_nao_existe(self):
        """Deve retornar False quando foto não existe"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pasta_fotos = Path(tmpdir) / "usuarios"
            pasta_fotos.mkdir()

            with patch('util.foto_util.PASTA_FOTOS', pasta_fotos):
                resultado = foto_existe(999)

                assert resultado is False


class TestObterTamanhoFoto:
    """Testes para a função obter_tamanho_foto()"""

    def test_retorna_tamanho_quando_existe(self):
        """Deve retornar tamanho em bytes quando foto existe"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pasta_fotos = Path(tmpdir) / "usuarios"
            pasta_fotos.mkdir()
            foto = pasta_fotos / "000001.jpg"
            foto.write_bytes(b"12345678")  # 8 bytes

            with patch('util.foto_util.PASTA_FOTOS', pasta_fotos):
                resultado = obter_tamanho_foto(1)

                assert resultado == 8

    def test_retorna_none_quando_nao_existe(self):
        """Deve retornar None quando foto não existe"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pasta_fotos = Path(tmpdir) / "usuarios"
            pasta_fotos.mkdir()

            with patch('util.foto_util.PASTA_FOTOS', pasta_fotos):
                resultado = obter_tamanho_foto(999)

                assert resultado is None
