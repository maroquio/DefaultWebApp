FROM python:3.12-slim

# Evita geração de .pyc e buffer no stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Instala dependências do sistema (curl para health check)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instala dependências do projeto
# Garanta que seu projeto tenha um requirements.txt no diretório raiz
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Porta interna onde o Uvicorn escutará
ENV PORT=8000
EXPOSE 8000

# Ajuste "main:app" para o módulo ASGI do seu projeto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
