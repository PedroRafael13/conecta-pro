"""
Controller de Monitoramento - Guardian Unified v3.0.0
====================================================

Endpoints para health checks, métricas e status do sistema.
"""

import logging
from datetime import datetime
from typing import Dict
import psutil
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.database import get_db

# Configurar logging
logger = logging.getLogger(__name__)

# Router para monitoramento
router = APIRouter(prefix="/monitoring", tags=["System Monitoring"])

# Timestamp de quando o sistema iniciou
STARTUP_TIME = datetime.utcnow()

class HealthStatus(BaseModel):
    """Status de saúde do sistema."""
    status: str
    timestamp: datetime
    uptime: str
    version: str
    database: str
    memory_usage: float
    cpu_usage: float

class ReadinessStatus(BaseModel):
    """Status de prontidão do sistema."""
    ready: bool
    timestamp: datetime
    services: Dict[str, str]
    checks_passed: int
    checks_total: int

class SystemMetrics(BaseModel):
    """Métricas do sistema."""
    timestamp: datetime
    uptime_seconds: int
    memory_usage_mb: float
    memory_percent: float
    cpu_percent: float
    disk_usage_percent: float
    active_connections: int


async def check_database_health(session: AsyncSession) -> bool:
    """Verifica se o database está respondendo."""
    try:
        result = await session.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(f"Database health check failed: {e}")
        return False


async def check_guardian_tables(session: AsyncSession) -> Dict[str, bool]:
    """Verifica se as tabelas principais do Guardian existem."""
    tables_to_check = [
        "guardian.access_logs",
        "guardian.guardian_occurrences",
        "guardian.guardian_syncs",
        "guardian.equipment_status",
        "guardian.campo_tecnicos"
    ]

    results = {}
    for table in tables_to_check:
        try:
            schema, table_name = table.split('.')
            query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = :schema
                    AND table_name = :table_name
                )
            """)
            result = await session.execute(query, {"schema": schema, "table_name": table_name})
            results[table] = result.scalar()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Table check failed for {table}: {e}")
            results[table] = False

    return results


def get_uptime() -> str:
    """Calcula tempo de atividade do sistema."""
    uptime = datetime.utcnow() - STARTUP_TIME
    total_seconds = int(uptime.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


@router.get("/health", response_model=HealthStatus)
async def health_check(session: AsyncSession = Depends(get_db)):
    """
    Health check básico do sistema.

    Verifica:
    - Conectividade com database
    - Uso de memória e CPU
    - Tempo de atividade

    Returns:
        Status geral de saúde do sistema
    """
    try:
        # Verificar database
        db_healthy = await check_database_health(session)
        db_status = "connected" if db_healthy else "disconnected"

        # Métricas do sistema
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)

        # Determinar status geral
        overall_status = "healthy" if db_healthy else "unhealthy"

        return HealthStatus(
            status=overall_status,
            timestamp=datetime.utcnow(),
            uptime=get_uptime(),
            version="3.0.0",
            database=db_status,
            memory_usage=memory.percent,
            cpu_usage=cpu_percent
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/ready", response_model=ReadinessStatus)
async def readiness_check(session: AsyncSession = Depends(get_db)):
    """
    Readiness check detalhado do sistema.

    Verifica se o sistema está pronto para receber traffic:
    - Database conectado
    - Tabelas existem
    - Serviços respondendo

    Returns:
        Status detalhado de prontidão
    """
    try:
        services = {}
        checks_passed = 0
        checks_total = 0

        # Check 1: Database connectivity
        checks_total += 1
        db_healthy = await check_database_health(session)
        services["database"] = "ok" if db_healthy else "failed"
        if db_healthy:
            checks_passed += 1

        # Check 2: Guardian tables
        checks_total += 1
        tables_status = await check_guardian_tables(session)
        all_tables_exist = all(tables_status.values())
        services["guardian_tables"] = "ok" if all_tables_exist else "missing"
        if all_tables_exist:
            checks_passed += 1

        # Check 3: CAMPO service
        checks_total += 1
        campo_ready = (
            "campo_tecnicos" in tables_status
            and tables_status.get("guardian.campo_tecnicos", False)
        )
        services["campo_service"] = "ok" if campo_ready else "not_ready"
        if campo_ready:
            checks_passed += 1

        # Sistema está pronto se todos os checks passaram
        system_ready = checks_passed == checks_total

        return ReadinessStatus(
            ready=system_ready,
            timestamp=datetime.utcnow(),
            services=services,
            checks_passed=checks_passed,
            checks_total=checks_total
        )

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Readiness check failed: {str(e)}"
        )


@router.get("/metrics", response_model=SystemMetrics)
async def get_metrics(
    session: AsyncSession = Depends(get_db),  # pylint: disable=unused-argument
):
    """
    Métricas detalhadas do sistema.

    Returns:
        Métricas de performance e uso de recursos
    """
    try:
        # Métricas de sistema
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        disk_usage = psutil.disk_usage('/')

        # Calcular uptime em segundos
        uptime_seconds = int((datetime.utcnow() - STARTUP_TIME).total_seconds())

        # Contar conexões ativas (estimativa)
        connections = len(psutil.net_connections())

        return SystemMetrics(
            timestamp=datetime.utcnow(),
            uptime_seconds=uptime_seconds,
            memory_usage_mb=memory.used / (1024 * 1024),
            memory_percent=memory.percent,
            cpu_percent=cpu_percent,
            disk_usage_percent=(disk_usage.used / disk_usage.total) * 100,
            active_connections=connections
        )

    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics collection failed: {str(e)}"
        )


@router.get("/ping")
async def ping():
    """
    Ping simples para verificar se o serviço responde.

    Returns:
        Pong com timestamp
    """
    return {
        "message": "pong",
        "timestamp": datetime.utcnow(),
        "service": "Guardian Unified v3.0.0"
    }


@router.get("/status")
async def system_status(session: AsyncSession = Depends(get_db)):
    """
    Status resumido do sistema.

    Returns:
        Status consolidado em formato simples
    """
    try:
        # Verificações básicas
        db_healthy = await check_database_health(session)

        # Status geral
        if db_healthy:
            status_code = "UP"
            message = "All systems operational"
        else:
            status_code = "DOWN"
            message = "Database connectivity issues"

        return {
            "status": status_code,
            "message": message,
            "timestamp": datetime.utcnow(),
            "uptime": get_uptime(),
            "version": "Guardian Unified v3.0.0"
        }

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(f"Status check failed: {e}")
        return {
            "status": "ERROR",
            "message": f"Status check failed: {str(e)}",
            "timestamp": datetime.utcnow()
        }
