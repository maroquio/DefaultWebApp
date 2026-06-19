"""
Testes para o módulo dtos/validators.py

Testa todas as funções de validação reutilizáveis para DTOs Pydantic.
"""

import pytest
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, field_validator, model_validator

from dtos.validators import (
    validar_string_obrigatoria,
    validar_comprimento,
    validar_texto_minimo_palavras,
    validar_nome_pessoa,
    validar_email,
    validar_cpf,
    validar_cnpj,
    validar_telefone_br,
    validar_cep,
    validar_senha_forte,
    validar_senhas_coincidem,
    validar_rate_limit,
    validar_email_opcional,
    validar_inteiro_range,
    validar_id_positivo,
    validar_slug,
    validar_extensao_arquivo,
    validar_tamanho_arquivo,
    validar_data,
    validar_url,
    validar_tipo,
)


# ===== TESTES DE VALIDAÇÃO DE STRINGS =====


class TestValidarStringObrigatoria:
    """Testes para validar_string_obrigatoria"""

    def test_string_valida(self):
        """String válida deve passar"""
        class Modelo(BaseModel):
            campo: str
            _validar = field_validator('campo')(validar_string_obrigatoria("Titulo"))

        modelo = Modelo(campo="Teste")
        assert modelo.campo == "Teste"

    def test_string_vazia_falha(self):
        """String vazia deve falhar"""
        class Modelo(BaseModel):
            campo: str
            _validar = field_validator('campo')(validar_string_obrigatoria("Titulo"))

        with pytest.raises(ValueError) as exc_info:
            Modelo(campo="")
        assert "obrigatório" in str(exc_info.value).lower()

    def test_string_espacos_apenas_falha(self):
        """String só com espaços deve falhar (com truncar=True)"""
        class Modelo(BaseModel):
            campo: str
            _validar = field_validator('campo')(validar_string_obrigatoria("Titulo"))

        with pytest.raises(ValueError):
            Modelo(campo="   ")

    def test_tamanho_minimo(self):
        """String menor que mínimo deve falhar"""
        class Modelo(BaseModel):
            campo: str
            _validar = field_validator('campo')(validar_string_obrigatoria("Titulo", tamanho_minimo=5))

        with pytest.raises(ValueError) as exc_info:
            Modelo(campo="abc")
        assert "mínimo" in str(exc_info.value).lower()

    def test_tamanho_maximo(self):
        """String maior que máximo deve falhar"""
        class Modelo(BaseModel):
            campo: str
            _validar = field_validator('campo')(validar_string_obrigatoria("Titulo", tamanho_maximo=5))

        with pytest.raises(ValueError) as exc_info:
            Modelo(campo="abcdefgh")
        assert "máximo" in str(exc_info.value).lower()

    def test_truncar_true(self):
        """Com truncar=True, espaços devem ser removidos"""
        class Modelo(BaseModel):
            campo: str
            _validar = field_validator('campo')(validar_string_obrigatoria("Titulo", truncar=True))

        modelo = Modelo(campo="  teste  ")
        assert modelo.campo == "teste"


class TestValidarComprimento:
    """Testes para validar_comprimento (permite vazio)"""

    def test_string_vazia_permitida(self):
        """String vazia deve ser permitida"""
        class Modelo(BaseModel):
            campo: str = ""
            _validar = field_validator('campo')(validar_comprimento(tamanho_maximo=10))

        modelo = Modelo(campo="")
        assert modelo.campo == ""

    def test_tamanho_minimo_com_valor(self):
        """String abaixo do mínimo deve falhar (quando preenchida)"""
        class Modelo(BaseModel):
            campo: str
            _validar = field_validator('campo')(validar_comprimento(tamanho_minimo=5, tamanho_maximo=10))

        with pytest.raises(ValueError):
            Modelo(campo="abc")

    def test_tamanho_maximo_com_valor(self):
        """String acima do máximo deve falhar"""
        class Modelo(BaseModel):
            campo: str
            _validar = field_validator('campo')(validar_comprimento(tamanho_maximo=5))

        with pytest.raises(ValueError):
            Modelo(campo="abcdefghij")


class TestValidarTextoMinimoPalavras:
    """Testes para validar_texto_minimo_palavras"""

    def test_texto_com_palavras_suficientes(self):
        """Texto com palavras suficientes deve passar"""
        class Modelo(BaseModel):
            descricao: str
            _validar = field_validator('descricao')(validar_texto_minimo_palavras(min_palavras=3))

        modelo = Modelo(descricao="Uma frase completa")
        assert modelo.descricao == "Uma frase completa"

    def test_texto_com_poucas_palavras_falha(self):
        """Texto com poucas palavras deve falhar"""
        class Modelo(BaseModel):
            descricao: str
            _validar = field_validator('descricao')(validar_texto_minimo_palavras(min_palavras=3))

        with pytest.raises(ValueError) as exc_info:
            Modelo(descricao="Uma palavra")
        assert "palavras" in str(exc_info.value).lower()

    def test_texto_vazio_falha(self):
        """Texto vazio deve falhar"""
        class Modelo(BaseModel):
            descricao: str
            _validar = field_validator('descricao')(validar_texto_minimo_palavras())

        with pytest.raises(ValueError):
            Modelo(descricao="")

    def test_texto_tamanho_maximo(self):
        """Texto acima do máximo deve falhar"""
        class Modelo(BaseModel):
            descricao: str
            _validar = field_validator('descricao')(validar_texto_minimo_palavras(tamanho_maximo=20))

        with pytest.raises(ValueError) as exc_info:
            Modelo(descricao="Uma frase muito muito muito longa")
        assert "máximo" in str(exc_info.value).lower()


class TestValidarNomePessoa:
    """Testes para validar_nome_pessoa"""

    def test_nome_completo_valido(self):
        """Nome completo deve passar"""
        class Modelo(BaseModel):
            nome: str
            _validar = field_validator('nome')(validar_nome_pessoa())

        modelo = Modelo(nome="João Silva")
        assert modelo.nome == "João Silva"

    def test_nome_vazio_falha(self):
        """Nome vazio deve falhar"""
        class Modelo(BaseModel):
            nome: str
            _validar = field_validator('nome')(validar_nome_pessoa())

        with pytest.raises(ValueError):
            Modelo(nome="")

    def test_nome_curto_demais_falha(self):
        """Nome muito curto deve falhar"""
        class Modelo(BaseModel):
            nome: str
            _validar = field_validator('nome')(validar_nome_pessoa(tamanho_minimo=5))

        with pytest.raises(ValueError) as exc_info:
            Modelo(nome="Ana")
        assert "mínimo" in str(exc_info.value).lower()

    def test_nome_sem_sobrenome_falha(self):
        """Nome sem sobrenome deve falhar (min_palavras=2)"""
        class Modelo(BaseModel):
            nome: str
            _validar = field_validator('nome')(validar_nome_pessoa(min_palavras=2))

        with pytest.raises(ValueError) as exc_info:
            Modelo(nome="João")
        assert "palavras" in str(exc_info.value).lower()

    def test_nome_muito_longo_falha(self):
        """Nome muito longo deve falhar"""
        class Modelo(BaseModel):
            nome: str
            _validar = field_validator('nome')(validar_nome_pessoa(tamanho_maximo=20))

        with pytest.raises(ValueError) as exc_info:
            Modelo(nome="João da Silva de Souza Pereira")
        assert "máximo" in str(exc_info.value).lower()

    def test_nome_sem_restricoes(self):
        """Nome sem restrições de palavras"""
        class Modelo(BaseModel):
            nome: str
            _validar = field_validator('nome')(validar_nome_pessoa(tamanho_minimo=None, min_palavras=None))

        modelo = Modelo(nome="Ana")
        assert modelo.nome == "Ana"


# ===== TESTES DE VALIDAÇÃO DE IDENTIFICAÇÃO PESSOAL =====


class TestValidarEmail:
    """Testes para validar_email"""

    def test_email_valido(self):
        """Email válido deve passar"""
        class Modelo(BaseModel):
            email: str
            _validar = field_validator('email')(validar_email())

        modelo = Modelo(email="teste@exemplo.com")
        assert modelo.email == "teste@exemplo.com"

    def test_email_convertido_para_lowercase(self):
        """Email deve ser convertido para lowercase"""
        class Modelo(BaseModel):
            email: str
            _validar = field_validator('email')(validar_email())

        modelo = Modelo(email="TESTE@EXEMPLO.COM")
        assert modelo.email == "teste@exemplo.com"

    def test_email_invalido_falha(self):
        """Email inválido deve falhar"""
        class Modelo(BaseModel):
            email: str
            _validar = field_validator('email')(validar_email())

        with pytest.raises(ValueError) as exc_info:
            Modelo(email="email_invalido")
        assert "inválido" in str(exc_info.value).lower()

    def test_email_vazio_falha(self):
        """Email vazio deve falhar"""
        class Modelo(BaseModel):
            email: str
            _validar = field_validator('email')(validar_email())

        with pytest.raises(ValueError):
            Modelo(email="")

    def test_email_muito_curto_falha(self):
        """Email muito curto deve falhar"""
        class Modelo(BaseModel):
            email: str
            _validar = field_validator('email')(validar_email(tamanho_minimo=10))

        with pytest.raises(ValueError) as exc_info:
            Modelo(email="a@b.c")
        assert "mínimo" in str(exc_info.value).lower()

    def test_email_muito_longo_falha(self):
        """Email muito longo deve falhar"""
        class Modelo(BaseModel):
            email: str
            _validar = field_validator('email')(validar_email(tamanho_maximo=20))

        with pytest.raises(ValueError) as exc_info:
            Modelo(email="email_muito_longo_demais@exemplo.com")
        assert "máximo" in str(exc_info.value).lower()


class TestValidarCpf:
    """Testes para validar_cpf"""

    def test_cpf_valido_sem_formatacao(self):
        """CPF válido sem formatação deve passar"""
        class Modelo(BaseModel):
            cpf: str
            _validar = field_validator('cpf')(validar_cpf())

        modelo = Modelo(cpf="52998224725")
        assert modelo.cpf == "52998224725"

    def test_cpf_valido_com_formatacao_entrada(self):
        """CPF válido com formatação na entrada deve passar"""
        class Modelo(BaseModel):
            cpf: str
            _validar = field_validator('cpf')(validar_cpf())

        modelo = Modelo(cpf="529.982.247-25")
        assert modelo.cpf == "52998224725"

    def test_cpf_valido_formatar_saida(self):
        """CPF deve ser formatado na saída se solicitado"""
        class Modelo(BaseModel):
            cpf: str
            _validar = field_validator('cpf')(validar_cpf(formatar=True))

        modelo = Modelo(cpf="52998224725")
        assert modelo.cpf == "529.982.247-25"

    def test_cpf_invalido_digitos_falha(self):
        """CPF com dígitos verificadores inválidos deve falhar"""
        class Modelo(BaseModel):
            cpf: str
            _validar = field_validator('cpf')(validar_cpf())

        with pytest.raises(ValueError) as exc_info:
            Modelo(cpf="52998224726")
        assert "inválido" in str(exc_info.value).lower()

    def test_cpf_repetido_falha(self):
        """CPF com todos os dígitos iguais deve falhar"""
        class Modelo(BaseModel):
            cpf: str
            _validar = field_validator('cpf')(validar_cpf())

        with pytest.raises(ValueError):
            Modelo(cpf="11111111111")

    def test_cpf_tamanho_errado_falha(self):
        """CPF com tamanho errado deve falhar"""
        class Modelo(BaseModel):
            cpf: str
            _validar = field_validator('cpf')(validar_cpf())

        with pytest.raises(ValueError) as exc_info:
            Modelo(cpf="1234567890")  # 10 dígitos
        assert "11 dígitos" in str(exc_info.value).lower()

    def test_cpf_vazio_falha(self):
        """CPF vazio deve falhar"""
        class Modelo(BaseModel):
            cpf: str
            _validar = field_validator('cpf')(validar_cpf())

        with pytest.raises(ValueError):
            Modelo(cpf="")


class TestValidarCnpj:
    """Testes para validar_cnpj"""

    def test_cnpj_valido_sem_formatacao(self):
        """CNPJ válido sem formatação deve passar"""
        class Modelo(BaseModel):
            cnpj: str
            _validar = field_validator('cnpj')(validar_cnpj())

        modelo = Modelo(cnpj="11222333000181")
        assert modelo.cnpj == "11222333000181"

    def test_cnpj_valido_com_formatacao_entrada(self):
        """CNPJ válido com formatação na entrada deve passar"""
        class Modelo(BaseModel):
            cnpj: str
            _validar = field_validator('cnpj')(validar_cnpj())

        modelo = Modelo(cnpj="11.222.333/0001-81")
        assert modelo.cnpj == "11222333000181"

    def test_cnpj_valido_formatar_saida(self):
        """CNPJ deve ser formatado na saída se solicitado"""
        class Modelo(BaseModel):
            cnpj: str
            _validar = field_validator('cnpj')(validar_cnpj(formatar=True))

        modelo = Modelo(cnpj="11222333000181")
        assert modelo.cnpj == "11.222.333/0001-81"

    def test_cnpj_invalido_falha(self):
        """CNPJ com dígitos verificadores inválidos deve falhar"""
        class Modelo(BaseModel):
            cnpj: str
            _validar = field_validator('cnpj')(validar_cnpj())

        with pytest.raises(ValueError) as exc_info:
            Modelo(cnpj="11222333000182")
        assert "inválido" in str(exc_info.value).lower()

    def test_cnpj_repetido_falha(self):
        """CNPJ com todos os dígitos iguais deve falhar"""
        class Modelo(BaseModel):
            cnpj: str
            _validar = field_validator('cnpj')(validar_cnpj())

        with pytest.raises(ValueError):
            Modelo(cnpj="11111111111111")

    def test_cnpj_tamanho_errado_falha(self):
        """CNPJ com tamanho errado deve falhar"""
        class Modelo(BaseModel):
            cnpj: str
            _validar = field_validator('cnpj')(validar_cnpj())

        with pytest.raises(ValueError) as exc_info:
            Modelo(cnpj="1234567890123")  # 13 dígitos
        assert "14 dígitos" in str(exc_info.value).lower()


class TestValidarTelefoneBr:
    """Testes para validar_telefone_br"""

    def test_celular_valido(self):
        """Celular válido deve passar"""
        class Modelo(BaseModel):
            telefone: str
            _validar = field_validator('telefone')(validar_telefone_br())

        modelo = Modelo(telefone="11912345678")
        assert modelo.telefone == "11912345678"

    def test_celular_formatado_entrada(self):
        """Celular formatado deve passar"""
        class Modelo(BaseModel):
            telefone: str
            _validar = field_validator('telefone')(validar_telefone_br())

        modelo = Modelo(telefone="(11) 91234-5678")
        assert modelo.telefone == "11912345678"

    def test_celular_formatar_saida(self):
        """Celular deve ser formatado na saída se solicitado"""
        class Modelo(BaseModel):
            telefone: str
            _validar = field_validator('telefone')(validar_telefone_br(formatar=True))

        modelo = Modelo(telefone="11912345678")
        assert modelo.telefone == "(11) 91234-5678"

    def test_fixo_valido(self):
        """Telefone fixo válido deve passar"""
        class Modelo(BaseModel):
            telefone: str
            _validar = field_validator('telefone')(validar_telefone_br())

        modelo = Modelo(telefone="1112345678")
        assert modelo.telefone == "1112345678"

    def test_fixo_formatar_saida(self):
        """Telefone fixo deve ser formatado na saída se solicitado"""
        class Modelo(BaseModel):
            telefone: str
            _validar = field_validator('telefone')(validar_telefone_br(formatar=True))

        modelo = Modelo(telefone="1112345678")
        assert modelo.telefone == "(11) 1234-5678"

    def test_telefone_ddd_invalido(self):
        """Telefone com DDD inválido deve falhar"""
        class Modelo(BaseModel):
            telefone: str
            _validar = field_validator('telefone')(validar_telefone_br())

        with pytest.raises(ValueError) as exc_info:
            Modelo(telefone="01912345678")
        assert "ddd" in str(exc_info.value).lower()

    def test_celular_sem_nove_falha(self):
        """Celular de 11 dígitos sem 9 inicial deve falhar"""
        class Modelo(BaseModel):
            telefone: str
            _validar = field_validator('telefone')(validar_telefone_br())

        with pytest.raises(ValueError) as exc_info:
            Modelo(telefone="11812345678")
        assert "9" in str(exc_info.value).lower()

    def test_telefone_tamanho_invalido(self):
        """Telefone com tamanho inválido deve falhar"""
        class Modelo(BaseModel):
            telefone: str
            _validar = field_validator('telefone')(validar_telefone_br())

        with pytest.raises(ValueError):
            Modelo(telefone="119123456")  # 9 dígitos


class TestValidarCep:
    """Testes para validar_cep"""

    def test_cep_valido(self):
        """CEP válido deve passar"""
        class Modelo(BaseModel):
            cep: str
            _validar = field_validator('cep')(validar_cep())

        modelo = Modelo(cep="12345678")
        assert modelo.cep == "12345-678"

    def test_cep_formatado_entrada(self):
        """CEP formatado deve passar"""
        class Modelo(BaseModel):
            cep: str
            _validar = field_validator('cep')(validar_cep())

        modelo = Modelo(cep="12345-678")
        assert modelo.cep == "12345-678"

    def test_cep_sem_formatacao_saida(self):
        """CEP sem formatação na saída"""
        class Modelo(BaseModel):
            cep: str
            _validar = field_validator('cep')(validar_cep(formatar=False))

        modelo = Modelo(cep="12345678")
        assert modelo.cep == "12345678"

    def test_cep_tamanho_errado_falha(self):
        """CEP com tamanho errado deve falhar"""
        class Modelo(BaseModel):
            cep: str
            _validar = field_validator('cep')(validar_cep())

        with pytest.raises(ValueError) as exc_info:
            Modelo(cep="1234567")
        assert "8 dígitos" in str(exc_info.value).lower()


# ===== TESTES DE VALIDAÇÃO DE SEGURANÇA =====


class TestValidarSenhaForte:
    """Testes para validar_senha_forte"""

    def test_senha_forte_completa(self):
        """Senha com todos os requisitos deve passar"""
        class Modelo(BaseModel):
            senha: str
            _validar = field_validator('senha')(validar_senha_forte())

        modelo = Modelo(senha="Teste@123")
        assert modelo.senha == "Teste@123"

    def test_senha_sem_maiuscula_falha(self):
        """Senha sem maiúscula deve falhar"""
        class Modelo(BaseModel):
            senha: str
            _validar = field_validator('senha')(validar_senha_forte())

        with pytest.raises(ValueError) as exc_info:
            Modelo(senha="teste@123")
        assert "maiúscula" in str(exc_info.value).lower()

    def test_senha_sem_minuscula_falha(self):
        """Senha sem minúscula deve falhar"""
        class Modelo(BaseModel):
            senha: str
            _validar = field_validator('senha')(validar_senha_forte())

        with pytest.raises(ValueError) as exc_info:
            Modelo(senha="TESTE@123")
        assert "minúscula" in str(exc_info.value).lower()

    def test_senha_sem_numero_falha(self):
        """Senha sem número deve falhar"""
        class Modelo(BaseModel):
            senha: str
            _validar = field_validator('senha')(validar_senha_forte())

        with pytest.raises(ValueError) as exc_info:
            Modelo(senha="Teste@abc")
        assert "número" in str(exc_info.value).lower()

    def test_senha_sem_especial_falha(self):
        """Senha sem caractere especial deve falhar"""
        class Modelo(BaseModel):
            senha: str
            _validar = field_validator('senha')(validar_senha_forte())

        with pytest.raises(ValueError) as exc_info:
            Modelo(senha="Teste1234")
        assert "especial" in str(exc_info.value).lower()

    def test_senha_muito_curta_falha(self):
        """Senha muito curta deve falhar"""
        class Modelo(BaseModel):
            senha: str
            _validar = field_validator('senha')(validar_senha_forte(tamanho_minimo=8))

        with pytest.raises(ValueError) as exc_info:
            Modelo(senha="Te@1")
        assert "mínimo" in str(exc_info.value).lower()

    def test_senha_muito_longa_falha(self):
        """Senha muito longa deve falhar"""
        class Modelo(BaseModel):
            senha: str
            _validar = field_validator('senha')(validar_senha_forte(tamanho_maximo=10))

        with pytest.raises(ValueError) as exc_info:
            Modelo(senha="TesteForte@123456")
        assert "máximo" in str(exc_info.value).lower()


class TestValidarSenhasCoincidem:
    """Testes para validar_senhas_coincidem"""

    def test_senhas_iguais(self):
        """Senhas iguais devem passar"""
        class Modelo(BaseModel):
            senha: str
            confirmar_senha: str

            @model_validator(mode="after")
            def validar(self):
                return validar_senhas_coincidem()(self)

        modelo = Modelo(senha="Teste@123", confirmar_senha="Teste@123")
        assert modelo.senha == modelo.confirmar_senha

    def test_senhas_diferentes_falha(self):
        """Senhas diferentes devem falhar"""
        class Modelo(BaseModel):
            senha: str
            confirmar_senha: str

            @model_validator(mode="after")
            def validar(self):
                return validar_senhas_coincidem()(self)

        with pytest.raises(ValueError) as exc_info:
            Modelo(senha="Teste@123", confirmar_senha="Teste@456")
        assert "coincidem" in str(exc_info.value).lower()

    def test_senhas_campos_customizados(self):
        """Usar campos customizados"""
        class Modelo(BaseModel):
            nova_senha: str
            repetir_senha: str

            @model_validator(mode="after")
            def validar(self):
                return validar_senhas_coincidem(
                    campo_senha="nova_senha",
                    campo_confirmacao="repetir_senha"
                )(self)

        modelo = Modelo(nova_senha="Teste@123", repetir_senha="Teste@123")
        assert modelo.nova_senha == modelo.repetir_senha


# ===== TESTES DE VALIDAÇÃO DE RATE LIMITING =====


class TestValidarRateLimit:
    """Testes para validar_rate_limit"""

    def test_valores_validos(self):
        """Valores dentro dos limites devem passar"""
        validar_tentativas, validar_minutos = validar_rate_limit()

        class Modelo(BaseModel):
            tentativas: int
            minutos: int
            _val_tentativas = field_validator('tentativas')(validar_tentativas)
            _val_minutos = field_validator('minutos')(validar_minutos)

        modelo = Modelo(tentativas=10, minutos=5)
        assert modelo.tentativas == 10
        assert modelo.minutos == 5

    def test_tentativas_abaixo_minimo_falha(self):
        """Tentativas abaixo do mínimo deve falhar"""
        validar_tentativas, _ = validar_rate_limit(min_tentativas=5)

        class Modelo(BaseModel):
            tentativas: int
            _val = field_validator('tentativas')(validar_tentativas)

        with pytest.raises(ValueError) as exc_info:
            Modelo(tentativas=2)
        assert "tentativa" in str(exc_info.value).lower()

    def test_tentativas_acima_maximo_falha(self):
        """Tentativas acima do máximo deve falhar"""
        validar_tentativas, _ = validar_rate_limit(max_tentativas=100)

        class Modelo(BaseModel):
            tentativas: int
            _val = field_validator('tentativas')(validar_tentativas)

        with pytest.raises(ValueError) as exc_info:
            Modelo(tentativas=150)
        assert "máximo" in str(exc_info.value).lower()

    def test_minutos_abaixo_minimo_falha(self):
        """Minutos abaixo do mínimo deve falhar"""
        _, validar_minutos = validar_rate_limit(min_minutos=5)

        class Modelo(BaseModel):
            minutos: int
            _val = field_validator('minutos')(validar_minutos)

        with pytest.raises(ValueError) as exc_info:
            Modelo(minutos=2)
        assert "minuto" in str(exc_info.value).lower()

    def test_minutos_acima_maximo_24h(self):
        """Minutos acima de 24h (1440) deve falhar com mensagem específica"""
        _, validar_minutos = validar_rate_limit(max_minutos=1440)

        class Modelo(BaseModel):
            minutos: int
            _val = field_validator('minutos')(validar_minutos)

        with pytest.raises(ValueError) as exc_info:
            Modelo(minutos=1500)
        assert "24 horas" in str(exc_info.value).lower()

    def test_minutos_acima_maximo_customizado(self):
        """Minutos acima de máximo customizado deve falhar"""
        _, validar_minutos = validar_rate_limit(max_minutos=60)

        class Modelo(BaseModel):
            minutos: int
            _val = field_validator('minutos')(validar_minutos)

        with pytest.raises(ValueError) as exc_info:
            Modelo(minutos=90)
        assert "60" in str(exc_info.value)


class TestValidarEmailOpcional:
    """Testes para validar_email_opcional"""

    def test_email_valido(self):
        """Email válido deve passar"""
        class Modelo(BaseModel):
            email: str | None = None
            _validar = field_validator('email')(validar_email_opcional())

        modelo = Modelo(email="teste@exemplo.com")
        assert modelo.email == "teste@exemplo.com"

    def test_email_none_permitido(self):
        """None deve ser permitido"""
        class Modelo(BaseModel):
            email: str | None = None
            _validar = field_validator('email')(validar_email_opcional())

        modelo = Modelo(email=None)
        assert modelo.email is None

    def test_email_vazio_retorna_none(self):
        """String vazia deve retornar None"""
        class Modelo(BaseModel):
            email: str | None = None
            _validar = field_validator('email')(validar_email_opcional())

        modelo = Modelo(email="")
        assert modelo.email is None

    def test_email_invalido_falha(self):
        """Email inválido deve falhar"""
        class Modelo(BaseModel):
            email: str | None = None
            _validar = field_validator('email')(validar_email_opcional())

        with pytest.raises(ValueError):
            Modelo(email="email_invalido")


class TestValidarInteiroRange:
    """Testes para validar_inteiro_range"""

    def test_valor_no_range(self):
        """Valor dentro do range deve passar"""
        class Modelo(BaseModel):
            valor: int
            _validar = field_validator('valor')(validar_inteiro_range(1, 100))

        modelo = Modelo(valor=50)
        assert modelo.valor == 50

    def test_valor_abaixo_minimo(self):
        """Valor abaixo do mínimo deve falhar"""
        class Modelo(BaseModel):
            valor: int
            _validar = field_validator('valor')(validar_inteiro_range(10, 100, "Quantidade"))

        with pytest.raises(ValueError) as exc_info:
            Modelo(valor=5)
        assert "mínimo" in str(exc_info.value).lower()

    def test_valor_acima_maximo(self):
        """Valor acima do máximo deve falhar"""
        class Modelo(BaseModel):
            valor: int
            _validar = field_validator('valor')(validar_inteiro_range(1, 50, "Quantidade"))

        with pytest.raises(ValueError) as exc_info:
            Modelo(valor=60)
        assert "máximo" in str(exc_info.value).lower()

    def test_valor_none_permitido(self):
        """None deve ser permitido"""
        class Modelo(BaseModel):
            valor: int | None = None
            _validar = field_validator('valor')(validar_inteiro_range(1, 100))

        modelo = Modelo(valor=None)
        assert modelo.valor is None


# ===== TESTES DE VALIDAÇÃO DE IDENTIFICADORES =====


class TestValidarIdPositivo:
    """Testes para validar_id_positivo"""

    def test_id_valido(self):
        """ID positivo deve passar"""
        class Modelo(BaseModel):
            id: int
            _validar = field_validator('id')(validar_id_positivo())

        modelo = Modelo(id=1)
        assert modelo.id == 1

    def test_id_zero_falha(self):
        """ID zero deve falhar"""
        class Modelo(BaseModel):
            id: int
            _validar = field_validator('id')(validar_id_positivo())

        with pytest.raises(ValueError):
            Modelo(id=0)

    def test_id_negativo_falha(self):
        """ID negativo deve falhar"""
        class Modelo(BaseModel):
            id: int
            _validar = field_validator('id')(validar_id_positivo())

        with pytest.raises(ValueError):
            Modelo(id=-1)


class TestValidarSlug:
    """Testes para validar_slug"""

    def test_slug_valido(self):
        """Slug válido deve passar"""
        class Modelo(BaseModel):
            slug: str
            _validar = field_validator('slug')(validar_slug())

        modelo = Modelo(slug="meu-slug-valido")
        assert modelo.slug == "meu-slug-valido"

    def test_slug_convertido_para_lowercase(self):
        """Slug deve ser convertido para lowercase"""
        class Modelo(BaseModel):
            slug: str
            _validar = field_validator('slug')(validar_slug())

        modelo = Modelo(slug="MEU-SLUG")
        assert modelo.slug == "meu-slug"

    def test_slug_com_caracteres_invalidos_falha(self):
        """Slug com caracteres inválidos deve falhar"""
        class Modelo(BaseModel):
            slug: str
            _validar = field_validator('slug')(validar_slug())

        with pytest.raises(ValueError):
            Modelo(slug="slug_com_underline")

    def test_slug_muito_longo_falha(self):
        """Slug muito longo deve falhar"""
        class Modelo(BaseModel):
            slug: str
            _validar = field_validator('slug')(validar_slug(tamanho_maximo=10))

        with pytest.raises(ValueError):
            Modelo(slug="slug-muito-longo-demais")

    def test_slug_vazio_falha(self):
        """Slug vazio deve falhar"""
        class Modelo(BaseModel):
            slug: str
            _validar = field_validator('slug')(validar_slug())

        with pytest.raises(ValueError):
            Modelo(slug="")


# ===== TESTES DE VALIDAÇÃO DE ARQUIVOS =====


class TestValidarExtensaoArquivo:
    """Testes para validar_extensao_arquivo"""

    def test_extensao_permitida(self):
        """Extensão permitida deve passar"""
        class Modelo(BaseModel):
            arquivo: str
            _validar = field_validator('arquivo')(validar_extensao_arquivo({'.jpg', '.png', '.gif'}))

        modelo = Modelo(arquivo="foto.jpg")
        assert modelo.arquivo == "foto.jpg"

    def test_extensao_maiuscula_permitida(self):
        """Extensão maiúscula deve passar"""
        class Modelo(BaseModel):
            arquivo: str
            _validar = field_validator('arquivo')(validar_extensao_arquivo({'.jpg', '.png'}))

        modelo = Modelo(arquivo="foto.JPG")
        assert modelo.arquivo == "foto.JPG"

    def test_extensao_nao_permitida_falha(self):
        """Extensão não permitida deve falhar"""
        class Modelo(BaseModel):
            arquivo: str
            _validar = field_validator('arquivo')(validar_extensao_arquivo({'.jpg', '.png'}))

        with pytest.raises(ValueError) as exc_info:
            Modelo(arquivo="documento.pdf")
        assert "formato" in str(exc_info.value).lower()

    def test_arquivo_vazio_falha(self):
        """Arquivo vazio deve falhar"""
        class Modelo(BaseModel):
            arquivo: str
            _validar = field_validator('arquivo')(validar_extensao_arquivo({'.jpg'}))

        with pytest.raises(ValueError):
            Modelo(arquivo="")


class TestValidarTamanhoArquivo:
    """Testes para validar_tamanho_arquivo"""

    def test_tamanho_valido(self):
        """Tamanho dentro do limite deve passar"""
        class Modelo(BaseModel):
            tamanho: int
            _validar = field_validator('tamanho')(validar_tamanho_arquivo(5 * 1024 * 1024))

        modelo = Modelo(tamanho=1024)
        assert modelo.tamanho == 1024

    def test_tamanho_zero_falha(self):
        """Arquivo vazio deve falhar"""
        class Modelo(BaseModel):
            tamanho: int
            _validar = field_validator('tamanho')(validar_tamanho_arquivo(5 * 1024 * 1024))

        with pytest.raises(ValueError) as exc_info:
            Modelo(tamanho=0)
        assert "vazio" in str(exc_info.value).lower()

    def test_tamanho_acima_limite_falha(self):
        """Arquivo acima do limite deve falhar"""
        class Modelo(BaseModel):
            tamanho: int
            _validar = field_validator('tamanho')(validar_tamanho_arquivo(1024 * 1024))

        with pytest.raises(ValueError) as exc_info:
            Modelo(tamanho=2 * 1024 * 1024)
        assert "grande" in str(exc_info.value).lower()


# ===== TESTES DE VALIDAÇÃO DE TIPOS ESPECÍFICOS =====


class TestValidarData:
    """Testes para validar_data"""

    def test_data_valida(self):
        """Data válida deve passar"""
        class Modelo(BaseModel):
            data: str
            _validar = field_validator('data')(validar_data())

        modelo = Modelo(data="2024-01-15")
        assert modelo.data == "2024-01-15"

    def test_data_formato_invalido_falha(self):
        """Data com formato inválido deve falhar"""
        class Modelo(BaseModel):
            data: str
            _validar = field_validator('data')(validar_data())

        with pytest.raises(ValueError) as exc_info:
            Modelo(data="15/01/2024")
        assert "formato" in str(exc_info.value).lower()

    def test_data_formato_customizado(self):
        """Data com formato customizado deve passar"""
        class Modelo(BaseModel):
            data: str
            _validar = field_validator('data')(validar_data(formato="%d/%m/%Y"))

        modelo = Modelo(data="15/01/2024")
        assert modelo.data == "15/01/2024"

    def test_data_anterior_minima_falha(self):
        """Data anterior à mínima deve falhar"""
        class Modelo(BaseModel):
            data: str
            _validar = field_validator('data')(validar_data(data_minima=datetime(2024, 1, 1)))

        with pytest.raises(ValueError) as exc_info:
            Modelo(data="2023-12-31")
        assert "posterior" in str(exc_info.value).lower()

    def test_data_posterior_maxima_falha(self):
        """Data posterior à máxima deve falhar"""
        class Modelo(BaseModel):
            data: str
            _validar = field_validator('data')(validar_data(data_maxima=datetime(2024, 12, 31)))

        with pytest.raises(ValueError) as exc_info:
            Modelo(data="2025-01-01")
        assert "anterior" in str(exc_info.value).lower()


class TestValidarUrl:
    """Testes para validar_url"""

    def test_url_https_valida(self):
        """URL HTTPS válida deve passar"""
        class Modelo(BaseModel):
            url: str
            _validar = field_validator('url')(validar_url())

        modelo = Modelo(url="https://exemplo.com")
        assert modelo.url == "https://exemplo.com"

    def test_url_http_valida(self):
        """URL HTTP válida deve passar"""
        class Modelo(BaseModel):
            url: str
            _validar = field_validator('url')(validar_url())

        modelo = Modelo(url="http://exemplo.com")
        assert modelo.url == "http://exemplo.com"

    def test_url_sem_protocolo_falha_com_requer(self):
        """URL sem protocolo deve falhar quando requer_protocolo=True"""
        class Modelo(BaseModel):
            url: str
            _validar = field_validator('url')(validar_url(requer_protocolo=True))

        with pytest.raises(ValueError) as exc_info:
            Modelo(url="exemplo.com")
        assert "http" in str(exc_info.value).lower()

    def test_url_sem_protocolo_passa_sem_requer(self):
        """URL sem protocolo deve passar quando requer_protocolo=False"""
        class Modelo(BaseModel):
            url: str
            _validar = field_validator('url')(validar_url(requer_protocolo=False))

        modelo = Modelo(url="exemplo.com")
        assert modelo.url == "exemplo.com"

    def test_url_invalida_falha(self):
        """URL inválida deve falhar - começa com caractere especial proibido"""
        class Modelo(BaseModel):
            url: str
            _validar = field_validator('url')(validar_url(requer_protocolo=False))

        with pytest.raises(ValueError):
            Modelo(url="?invalido")


class TestValidarTipo:
    """Testes para validar_tipo com Enum"""

    def test_tipo_valido(self):
        """Tipo válido do enum deve passar"""
        class TipoEnum(Enum):
            TIPO_A = "tipo_a"
            TIPO_B = "tipo_b"

        class Modelo(BaseModel):
            tipo: str
            _validar = field_validator('tipo')(validar_tipo("Tipo", TipoEnum))

        modelo = Modelo(tipo="tipo_a")
        assert modelo.tipo == "tipo_a"

    def test_tipo_invalido_falha(self):
        """Tipo inválido deve falhar"""
        class TipoEnum(Enum):
            TIPO_A = "tipo_a"
            TIPO_B = "tipo_b"

        class Modelo(BaseModel):
            tipo: str
            _validar = field_validator('tipo')(validar_tipo("Tipo", TipoEnum))

        with pytest.raises(ValueError) as exc_info:
            Modelo(tipo="tipo_c")
        assert "valor válido" in str(exc_info.value).lower()
