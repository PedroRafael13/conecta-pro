"""
Health Check Controller - Fase C Type Hints
"""

from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """
    Health check básico da aplicação.

    Returns:
        Status da aplicação
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Readiness probe - verifica se a aplicação está pronta para receber tráfego.

    Args:
        db: Sessão do banco de dados

    Returns:
        Status detalhado dos componentes
    """
    checks: dict[str, Any] = {
        "status": "ready",
        "checks": {},
    }

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["checks"]["database"] = {"status": "up"}
    except Exception as e:
        checks["checks"]["database"] = {"status": "down", "error": str(e)}
        checks["status"] = "not_ready"

    return checks


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> dict[str, str]:
    """
    Liveness probe - verifica se a aplicação está viva.

    Returns:
        Status de liveness
    """
    return {"status": "alive"}
