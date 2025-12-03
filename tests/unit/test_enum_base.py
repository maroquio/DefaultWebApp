"""
Testes para o módulo util/enum_base.py

Testa a classe base EnumEntidade para Enums de entidades do sistema.
"""

import pytest
from util.enum_base import EnumEntidade


class TipoTeste(EnumEntidade):
    """Enum de teste"""
    TIPO_A = "Tipo A"
    TIPO_B = "Tipo B"
    TIPO_C = "Tipo C"


class StatusTeste(EnumEntidade):
    """Outro enum de teste"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    PENDENTE = "pendente"


class TestEnumEntidade:
    """Testes para a classe EnumEntidade"""

    def test_str_retorna_valor(self):
        """__str__ deve retornar o valor do enum"""
        assert str(TipoTeste.TIPO_A) == "Tipo A"
        assert str(StatusTeste.ATIVO) == "ativo"

    def test_valores_retorna_lista_valores(self):
        """valores() deve retornar lista com todos os valores"""
        valores = TipoTeste.valores()

        assert isinstance(valores, list)
        assert len(valores) == 3
        assert "Tipo A" in valores
        assert "Tipo B" in valores
        assert "Tipo C" in valores

    def test_nomes_retorna_lista_nomes(self):
        """nomes() deve retornar lista com todos os nomes (keys)"""
        nomes = TipoTeste.nomes()

        assert isinstance(nomes, list)
        assert len(nomes) == 3
        assert "TIPO_A" in nomes
        assert "TIPO_B" in nomes
        assert "TIPO_C" in nomes

    def test_existe_valor_existente(self):
        """existe() deve retornar True para valor existente"""
        assert TipoTeste.existe("Tipo A") is True
        assert StatusTeste.existe("ativo") is True

    def test_existe_valor_inexistente(self):
        """existe() deve retornar False para valor inexistente"""
        assert TipoTeste.existe("Tipo D") is False
        assert StatusTeste.existe("cancelado") is False

    def test_from_valor_valor_existente(self):
        """from_valor() deve retornar enum para valor existente"""
        resultado = TipoTeste.from_valor("Tipo A")

        assert resultado == TipoTeste.TIPO_A
        assert isinstance(resultado, TipoTeste)

    def test_from_valor_valor_inexistente(self):
        """from_valor() deve retornar None para valor inexistente"""
        resultado = TipoTeste.from_valor("Tipo X")

        assert resultado is None

    def test_validar_valor_valido(self):
        """validar() deve retornar valor para valor válido"""
        resultado = TipoTeste.validar("Tipo A")

        assert resultado == "Tipo A"

    def test_validar_valor_invalido_levanta_erro(self):
        """validar() deve levantar ValueError para valor inválido"""
        with pytest.raises(ValueError) as exc_info:
            TipoTeste.validar("Tipo Invalido")

        assert "inválido" in str(exc_info.value).lower()
        assert "TipoTeste" in str(exc_info.value)

    def test_obter_por_nome_nome_existente(self):
        """obter_por_nome() deve retornar enum para nome existente"""
        resultado = TipoTeste.obter_por_nome("TIPO_A")

        assert resultado == TipoTeste.TIPO_A

    def test_obter_por_nome_nome_inexistente(self):
        """obter_por_nome() deve retornar None para nome inexistente"""
        resultado = TipoTeste.obter_por_nome("TIPO_X")

        assert resultado is None

    def test_para_opcoes_select(self):
        """para_opcoes_select() deve retornar lista de tuplas"""
        opcoes = StatusTeste.para_opcoes_select()

        assert isinstance(opcoes, list)
        assert len(opcoes) == 3
        assert ("ativo", "ativo") in opcoes
        assert ("inativo", "inativo") in opcoes
        assert ("pendente", "pendente") in opcoes

    def test_comparacao_com_string(self):
        """Enum deve ser comparável com string por herdar de str"""
        assert TipoTeste.TIPO_A == "Tipo A"
        assert StatusTeste.ATIVO == "ativo"

    def test_comparacao_entre_enums(self):
        """Enums do mesmo tipo devem ser comparáveis"""
        assert TipoTeste.TIPO_A == TipoTeste.TIPO_A
        assert TipoTeste.TIPO_A != TipoTeste.TIPO_B

    def test_iteracao(self):
        """Deve ser iterável"""
        tipos = list(TipoTeste)

        assert len(tipos) == 3
        assert TipoTeste.TIPO_A in tipos

    def test_uso_em_condicional(self):
        """Deve funcionar em condicionais"""
        tipo = TipoTeste.TIPO_A

        if tipo == "Tipo A":
            resultado = True
        else:
            resultado = False

        assert resultado is True

    def test_hash_para_uso_em_dict(self):
        """Deve ser hashable para uso como chave de dicionário"""
        mapeamento = {
            TipoTeste.TIPO_A: "Primeiro tipo",
            TipoTeste.TIPO_B: "Segundo tipo",
        }

        assert mapeamento[TipoTeste.TIPO_A] == "Primeiro tipo"

    def test_validar_mensagem_erro_inclui_valores_aceitos(self):
        """Mensagem de erro do validar() deve incluir valores aceitos"""
        with pytest.raises(ValueError) as exc_info:
            StatusTeste.validar("invalido")

        mensagem = str(exc_info.value)
        assert "ativo" in mensagem
        assert "inativo" in mensagem
        assert "pendente" in mensagem
