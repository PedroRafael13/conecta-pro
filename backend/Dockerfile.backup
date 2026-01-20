# Dockerfile - ERP Conecta Mais Backend
# Multi-stage build para imagem otimizada

# ===========================================
# Stage 1: Builder
# ===========================================
FROM python:3.12-slim as builder

WORKDIR /app

# Instalar dependências de build
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ===========================================
# Stage 2: Runtime
# ===========================================
FROM python:3.12-slim as runtime

WORKDIR /app

# Criar usuário não-root
RUN groupadd -r erp && useradd -r -g erp erp

# Instalar dependências runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar wheels do builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copiar código
COPY --chown=erp:erp . .

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

# Comando de início
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
