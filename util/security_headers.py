"""
Middleware de Security Headers
Adiciona cabeçalhos de segurança HTTP às respostas
"""

from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class MiddlewareSegurancaHeaders(BaseHTTPMiddleware):
    """
    Middleware que adiciona headers de segurança a todas as respostas HTTP

    Headers implementados:
    - X-Content-Type-Options: Previne MIME sniffing
    - X-Frame-Options: Previne clickjacking
    - X-XSS-Protection: Proteção adicional contra XSS (navegadores antigos)
    - Strict-Transport-Security: Força uso de HTTPS
    - Content-Security-Policy: Política de segurança de conteúdo
    - Referrer-Policy: Controla informações de referrer
    - Permissions-Policy: Controla permissões de recursos do navegador
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Processa a requisição e adiciona headers de segurança à resposta

        Args:
            request: Requisição HTTP
            call_next: Próximo middleware na cadeia

        Returns:
            Response com headers de segurança adicionados
        """
        # Processar requisição
        response = await call_next(request)

        # Adicionar headers de segurança

        # Previne MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Previne que a página seja carregada em frames (clickjacking)
        # Usar "SAMEORIGIN" se precisar carregar em frames do mesmo domínio
        response.headers["X-Frame-Options"] = "DENY"

        # Proteção XSS para navegadores antigos
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Força uso de HTTPS (remover em desenvolvimento local sem SSL)
        # Comentar a linha abaixo se estiver em desenvolvimento sem HTTPS
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy - política de segurança
        # NOTA DE SEGURANÇA: 'unsafe-inline' é necessário para:
        # - style-src: Bootstrap e estilos inline do framework
        # - script-src: Scripts inline nos templates (configurações, inicializações)
        #
        # Para remover 'unsafe-inline' de script-src seria necessário:
        # 1. Mover todos os scripts inline para arquivos externos, ou
        # 2. Implementar nonces CSP (gerar nonce por requisição e adicionar aos scripts)
        #
        # TODO: Migrar para nonces quando possível para maior segurança
        csp_directives = [
            "default-src 'self'",
            # AVISO: 'unsafe-inline' em script-src reduz proteção XSS
            # Manter apenas enquanto scripts inline forem necessários
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            # Bootstrap requer 'unsafe-inline' para estilos dinâmicos
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "img-src 'self' data: https:",
            "font-src 'self' https://cdn.jsdelivr.net",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            # Bloquear object e embed para prevenir plugins maliciosos
            "object-src 'none'",
            # Bloquear uso de base href para prevenir hijacking
            "base-uri 'self'",
            # Bloquear submissão de formulários para outros domínios
            "form-action 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Controla o que é enviado no header Referer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Controla permissões de recursos do navegador
        permissions_directives = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_directives)

        return response


class MiddlewareSegurancaCORS(BaseHTTPMiddleware):
    """
    Middleware alternativo para CORS mais restritivo
    Use apenas se precisar de controle fino sobre CORS
    """

    def __init__(self, app, allowed_origins: Optional[list] = None):
        """
        Inicializa middleware CORS

        Args:
            app: Aplicação FastAPI
            allowed_origins: Lista de origens permitidas
        """
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["http://localhost:8000"]

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Processa requisição e adiciona headers CORS

        Args:
            request: Requisição HTTP
            call_next: Próximo middleware

        Returns:
            Response com headers CORS
        """
        origin = request.headers.get("origin")

        response = await call_next(request)

        # Verificar se a origem está na lista de permitidos
        if origin and origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

        return response
