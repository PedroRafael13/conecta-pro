"""
ERP Conecta Mais V2.0 - Aplicação Principal
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from core.logging import configure_logging, logger
from core.monitoring import MetricsMiddleware, get_metrics
from core.rate_limit import limiter, rate_limit_handler


# =============================================================================
# SECURITY HEADERS MIDDLEWARE
# =============================================================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adiciona headers de segurança em todas as respostas."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Headers de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self'; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none'"
        )
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        # Cache control para APIs
        if "/api/" in request.url.path:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        # Forçar SameSite=Strict em todos os cookies
        if "set-cookie" in response.headers:
            cookie = response.headers["set-cookie"]
            if "SameSite" not in cookie:
                response.headers["set-cookie"] = f"{cookie}; SameSite=Strict; Secure"
        return response


# =============================================================================
# RATE LIMITER
# =============================================================================
# Importado de core.rate_limit com configuração customizada
# Usa Redis para storage distribuído e identifica por user_id + IP
# Limite padrão: 1000/hour (definido no módulo)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Gerencia ciclo de vida da aplicação."""
    from core.cache import close_redis, get_redis
    from core.database import close_db

    # Configurar logging
    configure_logging()

    # Startup
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    logger.info(f"Ambiente: {settings.environment}")
    logger.debug(f"Debug: {settings.debug}")

    # Inicializar conexões
    try:
        await get_redis()
        logger.info("Redis: conectado")
    except Exception as e:
        logger.warning(f"Redis: falha na conexao ({e})")

    yield

    # Shutdown
    logger.info("Encerrando aplicacao...")
    await close_redis()
    await close_db()
    logger.info("Conexoes fechadas")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema ERP completo para gestão de empresas de segurança",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Rate Limiter state (necessário para slowapi funcionar)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# =============================================================================
# MIDDLEWARES (ordem importa: último adicionado = primeiro executado)
# =============================================================================

# 1. CORS (primeiro a processar)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# 2. Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 3. GZIP Compression (respostas > 500 bytes)
app.add_middleware(GZipMiddleware, minimum_size=500)

# 4. Metrics
app.add_middleware(MetricsMiddleware, app_name=settings.app_name)


@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica saúde da aplicação."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/metrics", tags=["Monitoring"], include_in_schema=False)
async def metrics_endpoint():
    """Endpoint Prometheus para metricas."""
    return Response(content=get_metrics(), media_type="text/plain")


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz."""
    return {
        "message": f"Bem-vindo ao {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Desabilitado em produção",
    }


# Incluir routers
from api.v1 import router as api_v1_router  # noqa: E402

app.include_router(api_v1_router)

# PATCH 03: LGPD - Endpoint de direitos do titular
from modules.lgpd.routes.delete_me import router as lgpd_router  # noqa: E402

app.include_router(lgpd_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
