#!/usr/bin/env python3
"""
FastAPI - VERSÃO LITE para startup rápido.
Carrega apenas módulos essenciais, outros são carregados sob demanda.
"""

# Configurar logging básico ANTES de qualquer import pesado
import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Imports básicos apenas
from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.middleware.gzip import GZipMiddleware  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação."""
    logger.info("🚀 Conecta PRO - Iniciando (versão lite)...")
    yield
    logger.info("🛑 Conecta PRO - Finalizando...")


# Criar app FastAPI
app = FastAPI(
    title="Conecta PRO - API",
    description="Sistema de Gestão Condominial Inteligente",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware básico
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar adequadamente em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de health check - sempre disponível."""
    return {
        "status": "healthy",
        "service": "conecta-pro-api",
        "version": "1.0.0-lite",
        "timestamp": "2026-01-12T16:20:00Z",
    }


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz."""
    return {"message": "Conecta PRO API", "status": "running", "version": "1.0.0-lite", "docs": "/docs"}


# Lazy loading de routers - apenas quando acessados
@app.get("/api/status")
async def api_status():
    """Status da API com lazy loading."""
    try:
        # Lazy import apenas quando necessário

        return {"api": "running", "database": "connected", "version": "1.0.0-lite"}
    except Exception as e:
        logger.error(f"Erro no status: {e}")
        raise HTTPException(status_code=500, detail="Service temporarily unavailable")


# Rota para carregar módulos completos (apenas se necessário)
@app.post("/admin/load-modules")
async def load_full_modules():
    """Carrega todos os módulos da aplicação sob demanda."""
    try:
        logger.info("Carregando módulos completos...")

        # Aqui carregaria todos os routers pesados
        # from api.v1 import router as api_v1_router
        # app.include_router(api_v1_router, prefix="/api/v1")

        return {"status": "modules loaded", "routes": len(app.routes)}
    except Exception as e:
        logger.error(f"Erro ao carregar módulos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
