"""
Utilitários para processamento de erros de validação Pydantic.

Este módulo fornece funções auxiliares para tratar erros de validação
de forma segura, especialmente quando lidando com @model_validator que
podem retornar erros sem campo específico (loc vazia).
"""

from pydantic import ValidationError


def processar_erros_validacao(
    e: ValidationError, campo_padrao: str = "geral"
) -> dict[str, str]:
    """
    Processa erros de validação Pydantic de forma segura.

    Esta função lida corretamente com erros que têm loc vazia, o que acontece
    quando @model_validator lança ValueError. Nesses casos, o erro não está
    associado a um campo específico.

    Args:
        e: ValidationError do Pydantic contendo os erros de validação
        campo_padrao: Campo a usar quando loc estiver vazia. Útil para
                     erros de @model_validator (ex: "confirmar_senha", "geral")

    Returns:
        Dicionário mapeando nome do campo para mensagem de erro.
    """
    erros = {}
    for erro in e.errors():
        # Se loc estiver vazia (erro de @model_validator), usar campo padrão
        # Converte para str porque loc pode conter int ou str
        campo = str(erro["loc"][-1]) if erro["loc"] else campo_padrao

        # Remover prefixo "Value error, " se presente
        mensagem = erro["msg"].replace("Value error, ", "")

        erros[campo] = mensagem

    return erros
