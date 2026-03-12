"""
Controller de Benefícios — Departamento Pessoal.

Endpoints CRUD para gestão de benefícios dos colaboradores.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.hr.models.benefits import BenefitStatus
from modules.people_management.hr.schemas.benefits import (
    BenefitCreate,
    BenefitResponse,
    BenefitUpdate,
)
from modules.people_management.hr.services.benefits_service import BenefitsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/benefits", tags=["DP - Benefícios"])


@router.get("/employee/{employee_id}", response_model=list[BenefitResponse])
async def list_employee_benefits(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    status: BenefitStatus | None = Query(None, description="Filtro por status"),
) -> Any:
    """Lista benefícios de um funcionário."""
    service = BenefitsService(db)
    return await service.list_by_employee(employee_id, status=status)


@router.post("/", response_model=BenefitResponse, status_code=201)
async def create_benefit(
    data: BenefitCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria um novo benefício."""
    service = BenefitsService(db)
    benefit = await service.create_benefit(data.model_dump())
    await db.commit()
    return benefit


@router.get("/{benefit_id}", response_model=BenefitResponse)
async def get_benefit(
    benefit_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna detalhes de um benefício."""
    service = BenefitsService(db)
    benefit = await service.get_by_id(benefit_id)
    if not benefit:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")
    return benefit


@router.patch("/{benefit_id}", response_model=BenefitResponse)
async def update_benefit(
    benefit_id: str,
    data: BenefitUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Atualiza um benefício existente."""
    service = BenefitsService(db)
    benefit = await service.update_benefit(benefit_id, data.model_dump(exclude_unset=True))
    if not benefit:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")
    await db.commit()
    return benefit


@router.delete("/{benefit_id}", response_model=BenefitResponse)
async def cancel_benefit(
    benefit_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cancela um benefício (soft delete)."""
    service = BenefitsService(db)
    benefit = await service.cancel_benefit(benefit_id)
    if not benefit:
        raise HTTPException(status_code=404, detail="Benefício não encontrado")
    await db.commit()
    return benefit


@router.get("/employee/{employee_id}/total")
async def get_total_benefits(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Calcula o custo total de benefícios de um funcionário."""
    service = BenefitsService(db)
    return await service.calculate_total_benefits(employee_id)
