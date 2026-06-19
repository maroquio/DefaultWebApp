# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# Build multi-stage:
#   Stage 1 (frontend) : Node compila o SPA React (Vite) -> /fe/dist
#   Stage 2 (backend)  : Python/FastAPI serve a API + o SPA buildado
#
# IMPORTANTE: o contexto de build DEVE ser a RAIZ do repositório (não backend/),
# pois copiamos tanto frontend/ quanto backend/. Use:
#   docker build -f deploy/Dockerfile .
# ou o docker-compose.yml deste diretório (que já aponta o contexto para "..").
# ---------------------------------------------------------------------------

# === Stage 1: build do frontend (Bun) ======================================
FROM oven/bun:1 AS frontend

WORKDIR /fe

# Instala dependências primeiro (cache de camada enquanto o lockfile não muda).
# --frozen-lockfile falha o build se bun.lock estiver dessincronizado do package.json.
COPY frontend/package.json frontend/bun.lock ./
RUN bun install --frozen-lockfile

# Copia o restante do frontend e gera o build de produção em /fe/dist
COPY frontend/ ./
RUN bun run build


# === Stage 2: backend FastAPI ==============================================
FROM python:3.12-slim AS backend

# Evita geração de .pyc e buffer no stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Dependências do sistema (curl para o health check)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instala dependências Python (cache enquanto requirements.txt não muda)
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código do backend
COPY backend/ ./

# Copia o SPA buildado do stage anterior e aponta o backend para ele.
# main.py serve o SPA quando IS_DEVELOPMENT=False e SPA_DIST_PATH existir.
COPY --from=frontend /fe/dist /app/frontend_dist
ENV SPA_DIST_PATH=/app/frontend_dist
ENV RUNNING_MODE=Production

# Porta interna onde o Uvicorn escutará
ENV PORT=8000
EXPOSE 8000

# --proxy-headers + --forwarded-allow-ips: roda atrás de proxy reverso que
# termina TLS. Faz o Uvicorn honrar X-Forwarded-Proto/-For, para que redirects
# (ex: redirect_slashes 307) e url_for usem o scheme https correto em vez de
# http. Sem isso o browser bloqueia o redirect http via CSP connect-src 'self'.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
