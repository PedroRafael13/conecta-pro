"""
Controller (endpoints) para Allocation (Alocação Funcionário-Posto).
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from core.logging import logger
from modules.operations.models.allocation import AllocationStatus
from modules.operations.repositories.allocation_repository import AllocationRepository
from modules.operations.schemas.allocation import (
    AllocationCreate,
    AllocationFilter,
    AllocationListResponse,
    AllocationResponse,
    AllocationTerminate,
    AllocationUpdate,
)

router = APIRouter(prefix="/allocations", tags=["Operations - Allocations"])


@router.post("/", response_model=AllocationResponse, status_code=status.HTTP_201_CREATED)
async def create_allocation(
    data: AllocationCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> AllocationResponse:
    """
    Cria uma nova alocação de funcionário em posto.

    Requer autenticação.
    """
    repo = AllocationRepository(db)
    allocation = await repo.create(data)

    logger.info(
        f"Allocation criada por {current_user.email}: "
        f"funcionário {data.employee_id} -> posto {data.post_id}"
    )
    return AllocationResponse.model_validate(allocation)


@router.get("/", response_model=AllocationListResponse)
async def list_allocations(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    post_id: Optional[str] = None,
    employee_id: Optional[str] = None,
    status_filter: Optional[AllocationStatus] = Query(None, alias="status"),
    is_primary: Optional[bool] = None,
    is_temporary: Optional[bool] = None,
    is_current: Optional[bool] = None,
    start_date_from: Optional[date] = None,
    start_date_to: Optional[date] = None,
) -> AllocationListResponse:
    """
    Lista alocações com filtros e paginação.
    """
    repo = AllocationRepository(db)

    filters = AllocationFilter(
        post_id=post_id,
        employee_id=employee_id,
        status=status_filter,
        is_primary=is_primary,
        is_temporary=is_temporary,
        is_current=is_current,
        start_date_from=start_date_from,
        start_date_to=start_date_to,
    )

    allocations, total = await repo.list(filters=filters, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size

    return AllocationListResponse(
        items=[AllocationResponse.model_validate(a) for a in allocations],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/current", response_model=list[AllocationResponse])
async def get_current_allocations(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    post_id: Optional[str] = None,
) -> list[AllocationResponse]:
    """
    Lista alocações vigentes (ativas no momento).
    """
    repo = AllocationRepository(db)

    filters = AllocationFilter(
        post_id=post_id,
        is_current=True,
        status=AllocationStatus.ACTIVE,
    )

    allocations, _ = await repo.list(filters=filters, page=1, page_size=500)

    return [AllocationResponse.model_validate(a) for a in allocations]


@router.get("/available-employees")
async def get_available_employees(
    post_id: str,
    target_date: date,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """
    Lista funcionários disponíveis para alocação em um posto na data.
    """
    repo = AllocationRepository(db)
    employees = await repo.get_available_employees(post_id, target_date)

    return employees


@router.get("/post/{post_id}", response_model=list[AllocationResponse])
async def get_allocations_by_post(
    post_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = Query(False, description="Incluir inativos"),
) -> list[AllocationResponse]:
    """
    Lista todas as alocações de um posto.
    """
    repo = AllocationRepository(db)

    filters = AllocationFilter(
        post_id=post_id,
        is_current=None if include_inactive else True,
    )

    allocations, _ = await repo.list(filters=filters, page=1, page_size=500)

    return [AllocationResponse.model_validate(a) for a in allocations]


@router.get("/employee/{employee_id}", response_model=list[AllocationResponse])
async def get_allocations_by_employee(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = Query(False, description="Incluir inativos"),
) -> list[AllocationResponse]:
    """
    Lista todas as alocações de um funcionário.
    """
    repo = AllocationRepository(db)

    filters = AllocationFilter(
        employee_id=employee_id,
        is_current=None if include_inactive else True,
    )

    allocations, _ = await repo.list(filters=filters, page=1, page_size=500)

    return [AllocationResponse.model_validate(a) for a in allocations]


@router.get("/{allocation_id}", response_model=AllocationResponse)
async def get_allocation(
    allocation_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> AllocationResponse:
    """
    Busca alocação por ID.
    """
    repo = AllocationRepository(db)
    allocation = await repo.get_by_id(allocation_id)

    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alocação não encontrada",
        )

    return AllocationResponse.model_validate(allocation)


@router.patch("/{allocation_id}", response_model=AllocationResponse)
async def update_allocation(
    allocation_id: str,
    data: AllocationUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> AllocationResponse:
    """
    Atualiza uma alocação.
    """
    repo = AllocationRepository(db)
    allocation = await repo.update(allocation_id, data)

    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alocação não encontrada",
        )

    logger.info(f"Allocation atualizada por {current_user.email}: {allocation.id}")
    return AllocationResponse.model_validate(allocation)


@router.post("/{allocation_id}/terminate", response_model=AllocationResponse)
async def terminate_allocation(
    allocation_id: str,
    data: AllocationTerminate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> AllocationResponse:
    """
    Encerra uma alocação.
    """
    repo = AllocationRepository(db)
    allocation = await repo.terminate(
        allocation_id,
        data.end_date,
        data.termination_reason,
        data.notes,
    )

    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alocação não encontrada ou já encerrada",
        )

    logger.info(f"Allocation encerrada por {current_user.email}: {allocation.id}")
    return AllocationResponse.model_validate(allocation)


@router.delete("/{allocation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_allocation(
    allocation_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Remove uma alocação (soft delete).
    """
    repo = AllocationRepository(db)
    deleted = await repo.delete(allocation_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alocação não encontrada",
        )

    logger.info(f"Allocation deletada por {current_user.email}: {allocation_id}")
