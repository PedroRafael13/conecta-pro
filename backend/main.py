"""
ERP Conecta Mais V2.0 - Aplicação Principal
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Gerencia ciclo de vida da aplicação."""
    from core.cache import close_redis, get_redis
    from core.database import close_db

    # Startup
    print(f"Iniciando {settings.app_name} v{settings.app_version}")
    print(f"   Ambiente: {settings.environment}")
    print(f"   Debug: {settings.debug}")

    # Inicializar conexões
    try:
        await get_redis()
        print("   Redis: conectado")
    except Exception as e:
        print(f"   Redis: falha na conexao ({e})")

    yield

    # Shutdown
    print("Encerrando aplicacao...")
    await close_redis()
    await close_db()
    print("   Conexoes fechadas")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema ERP completo para gestão de empresas de segurança",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica saúde da aplicação."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz."""
    return {
        "message": f"Bem-vindo ao {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Desabilitado em produção",
    }


# TODO: Incluir routers
# from api.v1 import router as api_v1_router
# app.include_router(api_v1_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
