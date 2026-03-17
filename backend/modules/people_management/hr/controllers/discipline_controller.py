"""
Controller de Medidas Disciplinares — Departamento Pessoal.

Re-exporta endpoints disciplinares do operacional e adiciona endpoints DP:
histórico por funcionário e criação a partir de ocorrência.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.hr.services.discipline_service import DisciplineService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/discipline", tags=["DP - Disciplinar"])

# Re-export do router existente de disciplinares
# IMPORTANTE: usar include_router (NÃO append) para preservar prefixos
try:
    from modules.operacional.disciplinary.controllers import disciplinary_router

    router.include_router(disciplinary_router)
except ImportError:
    logger.info("Router disciplinar operacional não disponível para re-export")


@router.get("/employee/{employee_id}/history")
async def get_employee_discipline_history(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Any:
    """Retorna histórico disciplinar completo de um funcionário."""
    service = DisciplineService(db)
    return await service.get_employee_history(employee_id, page=page, page_size=page_size)


@router.post("/from-occurrence/{occurrence_id}")
async def create_from_occurrence(
    occurrence_id: str,
    current_user: CurrentActiveUser,
    action_type: str = Query(..., description="Tipo de ação disciplinar"),
    description: str | None = Query(None, description="Descrição/justificativa"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria medida disciplinar a partir de uma ocorrência operacional."""
    service = DisciplineService(db)
    try:
        result = await service.create_from_occurrence(
            occurrence_id=occurrence_id,
            action_type=action_type,
            description=description,
            created_by_id=current_user.id,
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
