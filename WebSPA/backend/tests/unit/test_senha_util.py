"""
Testes para o módulo util/senha_util.py

Testa funções de validação de força de senha e cálculo de nível de senha.
"""

import pytest
from util.senha_util import validar_forca_senha, calcular_nivel_senha


class TestValidarForcaSenha:
    """Testes para a função validar_forca_senha"""

    def test_senha_valida_completa(self):
        """Senha com todos os requisitos deve ser válida"""
        valida, mensagem = validar_forca_senha("Teste@123")
        assert valida is True
        assert mensagem == "Senha válida"

    def test_senha_muito_curta(self):
        """Senha menor que 8 caracteres deve ser rejeitada"""
        valida, mensagem = validar_forca_senha("Te@1")
        assert valida is False
        assert "mínimo" in mensagem.lower()

    def test_senha_muito_longa(self):
        """Senha maior que 128 caracteres deve ser rejeitada"""
        senha_longa = "A" * 60 + "a" * 60 + "@1" + "b" * 20  # > 128 caracteres
        valida, mensagem = validar_forca_senha(senha_longa)
        assert valida is False
        assert "máximo" in mensagem.lower()

    def test_senha_sem_maiuscula(self):
        """Senha sem letra maiúscula deve ser rejeitada"""
        valida, mensagem = validar_forca_senha("teste@123")
        assert valida is False
        assert "maiúscula" in mensagem.lower()

    def test_senha_sem_minuscula(self):
        """Senha sem letra minúscula deve ser rejeitada"""
        valida, mensagem = validar_forca_senha("TESTE@123")
        assert valida is False
        assert "minúscula" in mensagem.lower()

    def test_senha_sem_numero(self):
        """Senha sem número deve ser rejeitada"""
        valida, mensagem = validar_forca_senha("Teste@abc")
        assert valida is False
        assert "número" in mensagem.lower()

    def test_senha_sem_caractere_especial(self):
        """Senha sem caractere especial deve ser rejeitada"""
        valida, mensagem = validar_forca_senha("Teste1234")
        assert valida is False
        assert "especial" in mensagem.lower()

    def test_senha_com_todos_caracteres_especiais_aceitos(self):
        """Testa diferentes caracteres especiais aceitos"""
        caracteres_especiais = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", ",", ".", "?", '"', ":", "{", "}", "|", "<", ">"]
        for char in caracteres_especiais:
            senha = f"Teste123{char}"
            valida, _ = validar_forca_senha(senha)
            assert valida is True, f"Caractere especial '{char}' deveria ser aceito"

    def test_senha_exatamente_8_caracteres(self):
        """Senha com exatamente 8 caracteres válidos deve ser aceita"""
        valida, mensagem = validar_forca_senha("Te@1abcd")
        assert valida is True

    def test_senha_exatamente_128_caracteres(self):
        """Senha com exatamente 128 caracteres válidos deve ser aceita"""
        senha = "A" * 60 + "a" * 60 + "@1" + "b" * 6  # Exatamente 128 caracteres
        valida, _ = validar_forca_senha(senha)
        assert valida is True


class TestCalcularNivelSenha:
    """Testes para a função calcular_nivel_senha"""

    def test_senha_fraca_muito_curta(self):
        """Senha muito curta deve ser classificada como fraca"""
        nivel = calcular_nivel_senha("abc")
        assert nivel == "fraca"

    def test_senha_fraca_apenas_minusculas(self):
        """Senha apenas com minúsculas deve ser fraca"""
        nivel = calcular_nivel_senha("abcdefgh")
        assert nivel == "fraca"

    def test_senha_media_com_minusculas_e_maiusculas(self):
        """Senha com minúsculas e maiúsculas deve ser média"""
        nivel = calcular_nivel_senha("AbcdEfgh")
        assert nivel == "média"

    def test_senha_media_com_numero(self):
        """Senha com minúsculas, maiúsculas e número deve ser média"""
        nivel = calcular_nivel_senha("Abcdefg1")
        assert nivel == "média"

    def test_senha_forte_completa(self):
        """Senha com todos os critérios deve ser forte"""
        nivel = calcular_nivel_senha("Teste@123456")  # 12+ chars, maiúscula, minúscula, número, especial
        assert nivel == "forte"

    def test_senha_forte_longa_com_todos_requisitos(self):
        """Senha longa com todos os requisitos é forte"""
        nivel = calcular_nivel_senha("MinhaSenha@Forte1234")
        assert nivel == "forte"

    def test_senha_media_sem_especial(self):
        """Senha sem caractere especial mas com outros requisitos"""
        nivel = calcular_nivel_senha("Teste12345")
        assert nivel == "média"

    def test_senha_limite_fraca_para_media(self):
        """Teste do limite entre fraca e média (2 pontos -> 3 pontos)"""
        # Fraca: apenas 8 chars + minúscula = 2 pontos
        nivel_fraca = calcular_nivel_senha("abcdefgh")
        assert nivel_fraca == "fraca"

        # Média: 8 chars + maiúscula + minúscula = 3 pontos
        nivel_media = calcular_nivel_senha("Abcdefgh")
        assert nivel_media == "média"

    def test_senha_limite_media_para_forte(self):
        """Teste do limite entre média e forte (4 pontos -> 5 pontos)"""
        # Média: 8 chars + maiúscula + minúscula + numero = 4 pontos
        nivel_media = calcular_nivel_senha("Abcdefg1")
        assert nivel_media == "média"

        # Forte: 12 chars + maiúscula + minúscula + numero = 5 pontos
        nivel_forte = calcular_nivel_senha("Abcdefghijk1")
        assert nivel_forte == "forte"

    def test_senha_forte_todos_os_pontos(self):
        """Senha com todos os 6 pontos possíveis"""
        # 8+ chars, 12+ chars, maiúscula, minúscula, número, especial = 6 pontos
        nivel = calcular_nivel_senha("SenhaForte@123")
        assert nivel == "forte"

    def test_senha_vazia(self):
        """Senha vazia deve ser classificada como fraca"""
        nivel = calcular_nivel_senha("")
        assert nivel == "fraca"

    def test_senha_apenas_numeros(self):
        """Senha apenas com números"""
        nivel = calcular_nivel_senha("12345678")
        assert nivel == "fraca"

    def test_senha_apenas_especiais(self):
        """Senha apenas com caracteres especiais"""
        nivel = calcular_nivel_senha("@#$%^&*(")
        assert nivel == "fraca"
