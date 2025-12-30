"""
Controller FastAPI para GuardianOccurrence.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.logging import logger
from modules.remote_gatehouse.models.guardian_occurrence import (
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)
from modules.remote_gatehouse.repositories.guardian_occurrence_repository import (
    GuardianOccurrenceRepository,
)
from modules.remote_gatehouse.schemas.guardian_occurrence import (
    GuardianOccurrenceAcknowledge,
    GuardianOccurrenceCreate,
    GuardianOccurrenceEscalate,
    GuardianOccurrenceFilter,
    GuardianOccurrenceListResponse,
    GuardianOccurrenceResolve,
    GuardianOccurrenceResponse,
    GuardianOccurrenceStats,
)
from modules.remote_gatehouse.services.occurrence_analyzer import occurrence_analyzer

router = APIRouter(prefix="/guardian/occurrences", tags=["GuardianOccurrences"])


@router.post(
    "/",
    response_model=GuardianOccurrenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_occurrence(
    data: GuardianOccurrenceCreate,
    db: AsyncSession = Depends(get_db),
) -> GuardianOccurrenceResponse:
    """Cria uma nova ocorrência (recebida do Guardian)."""
    repo = GuardianOccurrenceRepository(db)

    # Verificar se já existe
    existing = await repo.get_by_guardian_id(data.guardian_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ocorrência já registrada",
        )

    occurrence = await repo.create(data)
    logger.info(f"Ocorrência criada: {occurrence.occurrence_code}")
    return GuardianOccurrenceResponse.model_validate(occurrence)


@router.get("/", response_model=GuardianOccurrenceListResponse)
async def list_occurrences(
    search: Optional[str] = Query(None),
    occurrence_type: Optional[OccurrenceType] = Query(None),
    severity: Optional[OccurrenceSeverity] = Query(None),
    occurrence_status: Optional[OccurrenceStatus] = Query(None, alias="status"),
    client_id: Optional[str] = Query(None),
    post_id: Optional[str] = Query(None),
    is_open: Optional[bool] = Query(None),
    is_critical: Optional[bool] = Query(None),
    is_false_alarm: Optional[bool] = Query(None),
    requires_followup: Optional[bool] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> GuardianOccurrenceListResponse:
    """Lista ocorrências com filtros e paginação."""
    repo = GuardianOccurrenceRepository(db)
    filters = GuardianOccurrenceFilter(
        search=search,
        occurrence_type=occurrence_type,
        severity=severity,
        status=occurrence_status,
        client_id=client_id,
        post_id=post_id,
        is_open=is_open,
        is_critical=is_critical,
        is_false_alarm=is_false_alarm,
        requires_followup=requires_followup,
        date_from=date_from,
        date_to=date_to,
    )
    occurrences, total = await repo.list(filters, page, page_size)
    total_pages = (total + page_size - 1) // page_size

    return GuardianOccurrenceListResponse(
        items=[GuardianOccurrenceResponse.model_validate(o) for o in occurrences],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=GuardianOccurrenceStats)
async def get_occurrence_stats(
    client_id: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> GuardianOccurrenceStats:
    """Obtém estatísticas de ocorrências."""
    repo = GuardianOccurrenceRepository(db)
    return await repo.get_stats(client_id, date_from, date_to)


@router.get("/open")
async def get_open_occurrences(
    client_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[GuardianOccurrenceResponse]:
    """Obtém ocorrências abertas."""
    repo = GuardianOccurrenceRepository(db)
    occurrences = await repo.get_open(client_id, limit)
    return [GuardianOccurrenceResponse.model_validate(o) for o in occurrences]


@router.get("/critical-open")
async def get_critical_open_occurrences(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[GuardianOccurrenceResponse]:
    """Obtém ocorrências críticas abertas."""
    repo = GuardianOccurrenceRepository(db)
    occurrences = await repo.get_critical_open(limit)
    return [GuardianOccurrenceResponse.model_validate(o) for o in occurrences]


@router.post("/classify")
async def classify_occurrence(
    title: str = Query(..., description="Título da ocorrência"),
    description: str = Query(..., description="Descrição da ocorrência"),
) -> dict:
    """Classifica uma ocorrência usando IA."""
    return occurrence_analyzer.classify_occurrence(title, description)


@router.post("/suggest-actions")
async def suggest_occurrence_actions(
    occurrence_type: OccurrenceType = Query(...),
    severity: OccurrenceSeverity = Query(...),
    location: Optional[str] = Query(None),
) -> list[dict]:
    """Sugere ações para uma ocorrência usando IA."""
    return occurrence_analyzer.suggest_actions(
        occurrence_type.value,
        severity.value,
        location,
    )


@router.post("/check-escalation")
async def check_escalation(
    occurrence_type: OccurrenceType = Query(...),
    severity: OccurrenceSeverity = Query(...),
    elapsed_minutes: int = Query(..., ge=0),
    is_resolved: bool = Query(False),
) -> dict:
    """Verifica necessidade de escalação."""
    return occurrence_analyzer.suggest_escalation(
        occurrence_type.value,
        severity.value,
        elapsed_minutes,
        is_resolved,
    )


@router.get("/{occurrence_id}", response_model=GuardianOccurrenceResponse)
async def get_occurrence(
    occurrence_id: str,
    db: AsyncSession = Depends(get_db),
) -> GuardianOccurrenceResponse:
    """Obtém uma ocorrência por ID."""
    repo = GuardianOccurrenceRepository(db)
    occurrence = await repo.get_by_id(occurrence_id)
    if not occurrence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrência não encontrada",
        )
    return GuardianOccurrenceResponse.model_validate(occurrence)


@router.get("/{occurrence_id}/priority")
async def get_occurrence_priority(
    occurrence_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Calcula prioridade de uma ocorrência."""
    repo = GuardianOccurrenceRepository(db)
    occurrence = await repo.get_by_id(occurrence_id)
    if not occurrence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrência não encontrada",
        )

    return occurrence_analyzer.calculate_priority_score(
        occurrence.occurrence_type,
        occurrence.severity,
        occurrence.event_timestamp,
    )


@router.post("/{occurrence_id}/acknowledge", response_model=GuardianOccurrenceResponse)
async def acknowledge_occurrence(
    occurrence_id: str,
    data: GuardianOccurrenceAcknowledge,
    operator_id: str = Query(..., description="ID do operador"),
    operator_name: str = Query(..., description="Nome do operador"),
    db: AsyncSession = Depends(get_db),
) -> GuardianOccurrenceResponse:
    """Reconhece uma ocorrência."""
    repo = GuardianOccurrenceRepository(db)
    occurrence = await repo.acknowledge(
        occurrence_id,
        operator_id,
        operator_name,
        data.notes,
    )
    if not occurrence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrência não encontrada",
        )
    logger.info(f"Ocorrência reconhecida: {occurrence.occurrence_code}")
    return GuardianOccurrenceResponse.model_validate(occurrence)


@router.post("/{occurrence_id}/start", response_model=GuardianOccurrenceResponse)
async def start_occurrence(
    occurrence_id: str,
    db: AsyncSession = Depends(get_db),
) -> GuardianOccurrenceResponse:
    """Inicia atendimento de uma ocorrência."""
    repo = GuardianOccurrenceRepository(db)
    occurrence = await repo.start_progress(occurrence_id)
    if not occurrence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrência não encontrada",
        )
    logger.info(f"Atendimento iniciado: {occurrence.occurrence_code}")
    return GuardianOccurrenceResponse.model_validate(occurrence)


@router.post("/{occurrence_id}/resolve", response_model=GuardianOccurrenceResponse)
async def resolve_occurrence(
    occurrence_id: str,
    data: GuardianOccurrenceResolve,
    db: AsyncSession = Depends(get_db),
) -> GuardianOccurrenceResponse:
    """Resolve uma ocorrência."""
    repo = GuardianOccurrenceRepository(db)
    occurrence = await repo.resolve(
        occurrence_id,
        data.resolution,
        data.is_false_alarm,
        data.requires_followup,
        data.followup_notes,
    )
    if not occurrence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrência não encontrada",
        )
    logger.info(f"Ocorrência resolvida: {occurrence.occurrence_code}")
    return GuardianOccurrenceResponse.model_validate(occurrence)


@router.post("/{occurrence_id}/escalate", response_model=GuardianOccurrenceResponse)
async def escalate_occurrence(
    occurrence_id: str,
    data: GuardianOccurrenceEscalate,
    db: AsyncSession = Depends(get_db),
) -> GuardianOccurrenceResponse:
    """Escala uma ocorrência."""
    repo = GuardianOccurrenceRepository(db)
    occurrence = await repo.escalate(
        occurrence_id,
        data.escalated_to,
        data.reason,
    )
    if not occurrence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrência não encontrada",
        )
    logger.info(f"Ocorrência escalada: {occurrence.occurrence_code}")
    return GuardianOccurrenceResponse.model_validate(occurrence)


@router.post("/{occurrence_id}/close", response_model=GuardianOccurrenceResponse)
async def close_occurrence(
    occurrence_id: str,
    db: AsyncSession = Depends(get_db),
) -> GuardianOccurrenceResponse:
    """Fecha uma ocorrência."""
    repo = GuardianOccurrenceRepository(db)
    occurrence = await repo.close(occurrence_id)
    if not occurrence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrência não encontrada",
        )
    logger.info(f"Ocorrência fechada: {occurrence.occurrence_code}")
    return GuardianOccurrenceResponse.model_validate(occurrence)


@router.delete("/{occurrence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_occurrence(
    occurrence_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove uma ocorrência (soft delete)."""
    repo = GuardianOccurrenceRepository(db)
    deleted = await repo.delete(occurrence_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrência não encontrada",
        )
