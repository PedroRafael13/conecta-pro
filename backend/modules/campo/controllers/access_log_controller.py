"""
Controller FastAPI para AccessLog.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.logging import logger
from modules.campo.models.access_log import AccessLogType
from modules.campo.repositories.access_log_repository import (
    AccessLogRepository,
)
from modules.campo.schemas.access_log import (
    AccessLogCreate,
    AccessLogFilter,
    AccessLogListResponse,
    AccessLogResponse,
    AccessLogStats,
)

router = APIRouter(prefix="/campo/access-logs", tags=["Campo Access Logs"])


@router.post(
    "/",
    response_model=AccessLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_access_log(
    data: AccessLogCreate,
    db: AsyncSession = Depends(get_db),
) -> AccessLogResponse:
    """Cria um novo log de acesso."""
    repo = AccessLogRepository(db)

    # Verificar se já existe
    existing = await repo.get_by_external_id(data.guardian_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Log de acesso já registrado",
        )

    log = await repo.create(data)
    logger.info(f"Log de acesso criado: {log.id}")
    return AccessLogResponse.model_validate(log)


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def create_access_logs_batch(
    data: list[AccessLogCreate],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Cria múltiplos logs de acesso em lote."""
    repo = AccessLogRepository(db)
    logs = await repo.create_batch(data)
    logger.info(f"Criados {len(logs)} logs de acesso em lote")
    return {
        "created": len(logs),
        "ids": [log.id for log in logs],
    }


@router.get("/", response_model=AccessLogListResponse)
async def list_access_logs(  # pylint: disable=too-many-locals
    search: str | None = Query(None),
    log_type: AccessLogType | None = Query(None),
    client_id: str | None = Query(None),
    post_id: str | None = Query(None),
    person_type: str | None = Query(None),
    access_method: str | None = Query(None),
    unit_code: str | None = Query(None),
    vehicle_plate: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    is_denied: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> AccessLogListResponse:
    """Lista logs de acesso com filtros e paginação."""
    repo = AccessLogRepository(db)
    filters = AccessLogFilter(
        search=search,
        log_type=log_type,
        client_id=client_id,
        post_id=post_id,
        person_type=person_type,
        access_method=access_method,
        unit_code=unit_code,
        vehicle_plate=vehicle_plate,
        date_from=date_from,
        date_to=date_to,
        is_denied=is_denied,
    )
    logs, total = await repo.list(filters, page, page_size)
    total_pages = (total + page_size - 1) // page_size

    return AccessLogListResponse(
        items=[AccessLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=AccessLogStats)
async def get_access_log_stats(
    client_id: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> AccessLogStats:
    """Obtém estatísticas de logs de acesso."""
    repo = AccessLogRepository(db)
    return await repo.get_stats(client_id, date_from, date_to)


@router.get("/by-person/{person_document}")
async def get_logs_by_person(
    person_document: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[AccessLogResponse]:
    """Obtém logs de acesso de uma pessoa específica."""
    repo = AccessLogRepository(db)
    # Limpar documento
    clean_doc = person_document.replace(".", "").replace("-", "").strip()
    logs = await repo.get_by_person(clean_doc, limit)
    return [AccessLogResponse.model_validate(log) for log in logs]


@router.get("/by-vehicle/{vehicle_plate}")
async def get_logs_by_vehicle(
    vehicle_plate: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[AccessLogResponse]:
    """Obtém logs de acesso de um veículo específico."""
    repo = AccessLogRepository(db)
    # Normalizar placa
    clean_plate = vehicle_plate.upper().replace("-", "").replace(" ", "").strip()
    logs = await repo.get_by_vehicle(clean_plate, limit)
    return [AccessLogResponse.model_validate(log) for log in logs]


@router.get("/{log_id}", response_model=AccessLogResponse)
async def get_access_log(
    log_id: str,
    db: AsyncSession = Depends(get_db),
) -> AccessLogResponse:
    """Obtém um log de acesso por ID."""
    repo = AccessLogRepository(db)
    log = await repo.get_by_id(log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log de acesso não encontrado",
        )
    return AccessLogResponse.model_validate(log)


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_access_log(
    log_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove um log de acesso (soft delete)."""
    repo = AccessLogRepository(db)
    deleted = await repo.delete(log_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log de acesso não encontrado",
        )
