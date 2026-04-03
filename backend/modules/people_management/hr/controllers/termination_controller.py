"""
Controller de Rescisão — Departamento Pessoal.

Endpoints para o workflow de desligamento de colaboradores.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.hr.models.termination import (
    TerminationStatus,
    TerminationType,
)
from modules.people_management.hr.schemas.termination import (
    TerminationCalculation,
    TerminationCreate,
    TerminationResponse,
    TerminationUpdate,
)
from modules.people_management.hr.services.termination_service import (
    TerminationService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/terminations", tags=["DP - Rescisões"])


@router.get(
    "",
    summary="Listar Rescisões",
    description="Retorna lista paginada de processos de rescisão com filtro por status.",
)
async def list_terminations(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    status: TerminationStatus | None = Query(None, description="Filtro por status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Any:
    """Lista processos de rescisão com filtro e paginação."""
    service = TerminationService(db)
    return await service.list_terminations(status=status, page=page, page_size=page_size)


@router.post(
    "",
    summary="Iniciar Processo de Rescisão",
    response_model=TerminationResponse,
    status_code=201,
    description="Retorna lista paginada de processos de rescisão com filtro por status.",
)
async def create_termination(
    data: TerminationCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria um novo processo de rescisão."""
    service = TerminationService(db)
    termination = await service.create_termination(data.model_dump(), created_by_id=current_user.id)
    await db.commit()
    return termination


@router.get(
    "/{termination_id}",
    summary="Buscar Rescisão",
    response_model=TerminationResponse,
    description="Retorna lista paginada de processos de rescisão com filtro por status.",
)
async def get_termination(
    termination_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna detalhes de um processo de rescisão."""
    service = TerminationService(db)
    termination = await service.get_by_id(termination_id)
    if not termination:
        raise HTTPException(status_code=404, detail="Rescisão não encontrada")
    return termination


@router.patch(
    "/{termination_id}",
    summary="Atualizar Rescisão",
    response_model=TerminationResponse,
    description="Retorna lista paginada de processos de rescisão com filtro por status.",
)
async def update_termination(
    termination_id: str,
    data: TerminationUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Atualiza dados de um processo de rescisão."""
    service = TerminationService(db)
    termination = await service.get_by_id(termination_id)
    if not termination:
        raise HTTPException(status_code=404, detail="Rescisão não encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(termination, key) and value is not None:
            setattr(termination, key, value)

    await db.flush()
    await db.refresh(termination)
    await db.commit()
    return termination


@router.post(
    "/{termination_id}/calculate",
    summary="Calcular Verbas Rescisórias",
    response_model=TerminationCalculation,
    status_code=201,
    description="Retorna lista paginada de processos de rescisão com filtro por status.",
)
async def calculate_severance(
    termination_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Calcula verbas rescisórias para um processo de rescisão."""
    service = TerminationService(db)
    termination = await service.get_by_id(termination_id)
    if not termination:
        raise HTTPException(status_code=404, detail="Rescisão não encontrada")

    if not termination.last_working_day:
        raise HTTPException(
            status_code=400,
            detail="Último dia de trabalho não informado",
        )

    try:
        calculation = await service.calculate_severance(
            termination.employee_id,
            TerminationType(termination.type),
            termination.last_working_day,
        )
        return calculation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{termination_id}/complete",
    summary="Concluir Rescisão",
    response_model=TerminationResponse,
    status_code=201,
    description="Retorna lista paginada de processos de rescisão com filtro por status.",
)
async def complete_termination(
    termination_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Conclui o processo de rescisão e desativa o funcionário."""
    service = TerminationService(db)
    termination = await service.complete_termination(termination_id)
    if not termination:
        raise HTTPException(status_code=404, detail="Rescisão não encontrada")
    await db.commit()
    return termination
