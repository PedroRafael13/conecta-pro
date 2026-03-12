"""
Controller de Funcionários — Departamento Pessoal.

Endpoints CRUD para gestão de funcionários na visão DP.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.hr.schemas.employee import (
    DPEmployeeList,
    DPEmployeeRead,
    DPEmployeeUpdate,
)
from modules.people_management.hr.services.employee_service import EmployeeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/employees", tags=["DP - Funcionários"])


@router.get("/", response_model=DPEmployeeList)
async def list_employees(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Página"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    search: str | None = Query(None, description="Busca por nome, CPF ou matrícula"),
) -> Any:
    """Lista funcionários ativos com paginação e busca."""
    service = EmployeeService(db)
    return await service.get_active_employees(page=page, page_size=page_size, search=search)


@router.get("/{employee_id}", response_model=DPEmployeeRead)
async def get_employee(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna dados DP de um funcionário."""
    service = EmployeeService(db)
    employee = await service.get_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employee


@router.get("/{employee_id}/profile")
async def get_employee_full_profile(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna perfil completo do funcionário (dados + benefícios + contrato)."""
    service = EmployeeService(db)
    profile = await service.get_employee_full_profile(employee_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return profile


@router.get("/cpf/{cpf}", response_model=DPEmployeeRead)
async def get_employee_by_cpf(
    cpf: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Busca funcionário por CPF."""
    service = EmployeeService(db)
    employee = await service.get_by_cpf(cpf)
    if not employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employee


@router.patch("/{employee_id}", response_model=DPEmployeeRead)
async def update_employee(
    employee_id: str,
    data: DPEmployeeUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Atualiza dados DP de um funcionário."""
    service = EmployeeService(db)
    employee = await service.update_employee(employee_id, data.model_dump(exclude_unset=True))
    if not employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    await db.commit()
    return employee
