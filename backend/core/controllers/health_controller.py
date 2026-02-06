"""
Health Check Endpoint - Monitoramento de saúde da aplicação.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.monitoring.health import HealthChecker

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Verifica saúde de todos os componentes críticos da aplicação",
)
async def health_check(
    db: AsyncSession = Depends(get_db),
    detailed: bool = False,
):
    """
    Endpoint de Health Check.

    Verifica:
    - Database (PostgreSQL)
    - Redis (se configurado)
    - Integrações externas (opcional)

    Args:
        db: Sessão do banco de dados
        detailed: Se True, retorna detalhes completos de cada componente

    Returns:
        Status geral e detalhes dos componentes

    Response Codes:
        - 200: Sistema saudável ou com degradação aceitável
        - 503: Sistema não saudável (componentes críticos offline)
    """
    checker = HealthChecker()

    # Tenta obter Redis (opcional)
    redis_client = None
    try:
        from core.cache import get_redis

        redis_client = await get_redis()
    except Exception:
        pass  # Redis é opcional

    # Configurar integrações externas (se necessário)
    external_integrations = None
    # Exemplo: external_integrations = {"solides": "https://employer.tangerino.com.br/test"}

    # Executa health checks
    result = await checker.check_all(
        db=db,
        redis=redis_client,
        external_integrations=external_integrations,
    )

    # Se não detalhado, retorna apenas status geral
    if not detailed:
        return {
            "status": result["status"],
            "healthy_count": result["healthy_count"],
            "total_count": result["total_count"],
            "timestamp": result["timestamp"],
        }

    return result


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Verifica se aplicação está pronta para receber requisições",
)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe para Kubernetes.

    Retorna 200 se a aplicação está pronta, 503 caso contrário.
    """
    checker = HealthChecker()

    # Verifica apenas database (crítico)
    db_health = await checker.check_database(db)

    if db_health.status.value == "unhealthy":
        return {
            "ready": False,
            "reason": db_health.message,
        }, 503

    return {
        "ready": True,
        "timestamp": db_health.checked_at.isoformat(),
    }


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness Check",
    description="Verifica se aplicação está viva",
)
async def liveness_check():
    """
    Liveness probe para Kubernetes.

    Sempre retorna 200 se o processo está rodando.
    """
    return {
        "alive": True,
    }
