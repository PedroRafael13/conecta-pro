# Dockerfile - ERP Conecta Mais Backend
# Multi-stage build para imagem otimizada

# ===========================================
# Stage 1: Builder
# ===========================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Criar /tmp e instalar dependências de build
RUN mkdir -p /tmp && chmod 1777 /tmp && \
    apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ===========================================
# Stage 2: Runtime
# ===========================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Criar /tmp e instalar dependências runtime
RUN mkdir -p /tmp && chmod 1777 /tmp && \
    apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root e diretórios
RUN groupadd -r erp && useradd -r -g erp erp && \
    mkdir -p /app/logs

# Copiar wheels do builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Instalar Celery separadamente
RUN pip install --no-cache-dir celery[redis]==5.4.0 kombu==5.4.2 flower==2.0.1

# Copiar código
COPY --chown=erp:erp . .

# Ajustar permissões
RUN chown -R erp:erp /app/logs

# Mudar para usuário não-root
USER erp

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expor porta
EXPOSE ${PORT}

# Comando de início - FastAPI com Uvicorn (versao producao)
CMD ["uvicorn", "main_production:app", "--host", "0.0.0.0", "--port", "8080"]
