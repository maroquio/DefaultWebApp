"""
Test helpers e funções auxiliares para assertions.

Fornece funções helper reutilizáveis para simplificar e padronizar
assertions nos testes.
"""
from fastapi import status


def assert_permission_denied(response, expected_redirect: str = "/login"):
    """
    Helper para verificar se permissão foi negada.

    Verifica se resposta é 303 e redireciona para login ou página esperada.
    Permite query strings (ex: /login?redirect=/some/path).

    Args:
        response: Response object do TestClient
        expected_redirect: URL base esperada de redirecionamento (padrão: /login)
    """
    assert response.status_code == status.HTTP_303_SEE_OTHER
    # Verificar se começa com a URL esperada (permite query strings)
    location = response.headers["location"]
    assert location.startswith(expected_redirect), \
        f"Expected redirect to start with '{expected_redirect}', got '{location}'"


def assert_redirects_to(response, expected_url: str, expected_status: int = status.HTTP_303_SEE_OTHER):
    """
    Helper para verificar redirecionamento.

    Args:
        response: Response object do TestClient
        expected_url: URL esperada de redirecionamento
        expected_status: Status code esperado (padrão: 303)
    """
    assert response.status_code == expected_status
    assert response.headers.get("location") == expected_url


def assert_contains_text(response, text: str, case_sensitive: bool = False):
    """
    Helper para verificar se response contém texto.

    Args:
        response: Response object do TestClient
        text: Texto esperado no conteúdo
        case_sensitive: Se deve ser case-sensitive (padrão: False)
    """
    content = response.text
    if not case_sensitive:
        assert text.lower() in content.lower()
    else:
        assert text in content
