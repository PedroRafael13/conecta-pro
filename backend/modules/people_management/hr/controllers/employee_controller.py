"""
Controller de Funcionários — Departamento Pessoal.

Endpoints CRUD para gestão de funcionários na visão DP.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
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


# =============================================================================
# CONSIGNADOS E PENSÕES (Deduções fixas)
# =============================================================================


class DeductionCreate(BaseModel):
    """Schema para criar dedução do funcionário."""

    tipo: str = Field(..., pattern="^(consignado|pensao_alimenticia|emprestimo|outros)$")
    descricao: str = Field(..., min_length=3, max_length=200)
    valor: float | None = Field(None, ge=0)
    percentual: float | None = Field(None, ge=0, le=100)
    base_calculo: str = Field("fixo", pattern="^(bruto|liquido|fixo)$")
    total_parcelas: int | None = Field(None, ge=1)
    data_inicio: str = Field(...)
    data_fim: str | None = None


@router.get("/{employee_id}/deductions")
async def list_deductions(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    ativo: bool = True,
) -> Any:
    """Lista deduções (consignados, pensões) de um funcionário."""
    result = await db.execute(
        text(
            "SELECT id, tipo, descricao, valor, percentual, base_calculo, "
            "parcela_atual, total_parcelas, data_inicio::text, data_fim::text, ativo "
            "FROM employee_deductions WHERE employee_id = :eid "
            "AND ativo = :ativo ORDER BY tipo, descricao"
        ),
        {"eid": employee_id, "ativo": ativo},
    )
    rows = result.mappings().all()
    return {"employee_id": employee_id, "total": len(rows), "items": [dict(r) for r in rows]}


@router.post("/{employee_id}/deductions", status_code=201)
async def create_deduction(
    employee_id: str,
    data: DeductionCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria nova dedução para um funcionário."""
    result = await db.execute(
        text(
            "INSERT INTO employee_deductions "
            "(employee_id, tipo, descricao, valor, percentual, base_calculo, "
            "total_parcelas, data_inicio, data_fim) "
            "VALUES (:eid, :tipo, :desc, :val, :pct, :base, :parcelas, :inicio, :fim) "
            "RETURNING id"
        ),
        {
            "eid": employee_id,
            "tipo": data.tipo,
            "desc": data.descricao,
            "val": data.valor,
            "pct": data.percentual,
            "base": data.base_calculo,
            "parcelas": data.total_parcelas,
            "inicio": data.data_inicio,
            "fim": data.data_fim,
        },
    )
    new_id = result.scalar_one()
    await db.commit()
    return {"id": str(new_id), "employee_id": employee_id, "tipo": data.tipo, "descricao": data.descricao}
