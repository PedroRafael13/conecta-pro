"""
Controller de Contratos — Departamento Pessoal.

Endpoints CRUD para gestão de contratos de trabalho.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.hr.schemas.contract import (
    ContractCreate,
    ContractResponse,
    ContractUpdate,
)
from modules.people_management.hr.services.contract_service import ContractService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contracts", tags=["DP - Contratos"])


@router.get(
    "",
    summary="Listar Contratos",
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def list_contracts(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Any:
    """Lista todos os contratos com paginação."""
    service = ContractService(db)
    result = await service.list_all(page=page, page_size=page_size)
    # Serialize manually to avoid Pydantic errors with raw ORM objects
    if isinstance(result, dict) and "items" in result:
        result["items"] = [ContractResponse.model_validate(c).model_dump(mode="json") for c in result["items"]]
    elif isinstance(result, list):
        result = [ContractResponse.model_validate(c).model_dump(mode="json") for c in result]
    return result


@router.get(
    "/employee/{employee_id}",
    summary="Contratos por Funcionário",
    response_model=list[ContractResponse],
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def list_employee_contracts(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Lista todos os contratos de um funcionário (histórico)."""
    service = ContractService(db)
    return await service.list_by_employee(employee_id)


@router.get(
    "/employee/{employee_id}/current",
    summary="Contrato Vigente",
    response_model=ContractResponse,
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def get_current_contract(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna o contrato vigente de um funcionário."""
    service = ContractService(db)
    contract = await service.get_current_contract(employee_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Nenhum contrato vigente encontrado")
    return contract


@router.post(
    "",
    summary="Criar Contrato",
    response_model=ContractResponse,
    status_code=201,
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def create_contract(
    data: ContractCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria um novo contrato de trabalho.

    Se houver contrato vigente, este será marcado como não atual.
    """
    service = ContractService(db)
    contract = await service.create_contract(data.model_dump())
    await db.commit()
    return contract


@router.get(
    "/{contract_id}",
    summary="Buscar Contrato",
    response_model=ContractResponse,
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def get_contract(
    contract_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna detalhes de um contrato."""
    service = ContractService(db)
    contract = await service.get_by_id(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return contract


@router.patch(
    "/{contract_id}",
    summary="Atualizar Contrato",
    response_model=ContractResponse,
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def update_contract(
    contract_id: str,
    data: ContractUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Atualiza dados de um contrato."""
    service = ContractService(db)
    contract = await service.update_contract(contract_id, data.model_dump(exclude_unset=True))
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    await db.commit()
    return contract


@router.post(
    "/{contract_id}/document",
    summary="Gerar Documento de Contrato",
    status_code=201,
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def generate_contract_document(
    contract_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Gera documento de contrato de trabalho."""
    service = ContractService(db)
    contract = await service.get_by_id(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    # Buscar nome do funcionário
    from modules.people_management.hr.services.employee_service import EmployeeService

    emp_service = EmployeeService(db)
    employee = await emp_service.get_by_id(contract.employee_id)
    employee_name = employee.nome if employee else "N/A"

    document = service.generate_contract_document(contract, employee_name)
    return document
