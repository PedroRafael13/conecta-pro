"""
Employee Controller - Com Type Hints Completos
Exemplo para Fase C - Excelência
"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.auth.dependencies import get_current_active_user
from core.database import get_db
from core.models import User
from core.rate_limit import limiter

# Schemas (simplificado - usar schemas reais do projeto)
# from modules.operacional.schemas.employee import (
#     EmployeeResponse, EmployeeCreate, EmployeeUpdate, EmployeeListResponse
# )

router = APIRouter(prefix="/employees", tags=["Employees"])

# Type aliases
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_active_user)]


@router.get(
    "/",
    response_model=dict,  # Replace with EmployeeListResponse
    summary="Listar funcionários",
    description="Lista todos os funcionários com paginação e filtros opcionais",
)
@limiter.limit("100/minute")
async def list_employees(
    request: Any,  # Required by slowapi
    db: DbSession,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0, description="Número de registros para pular")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Limite de registros por página")] = 20,
    department_id: Annotated[UUID | None, Query(description="Filtrar por departamento")] = None,
    is_active: Annotated[bool | None, Query(description="Filtrar por status ativo")] = None,
    search: Annotated[str | None, Query(description="Busca por nome ou email")] = None,
) -> dict[str, Any]:
    """
    Lista funcionários com suporte a paginação e filtros.

    Args:
        request: Request object (requerido pelo rate limiter)
        db: Sessão do banco de dados
        current_user: Usuário autenticado atual
        skip: Offset para paginação
        limit: Limite de registros
        department_id: Filtro por departamento
        is_active: Filtro por status
        search: Termo de busca

    Returns:
        Lista paginada de funcionários
    """
    # Query base com eager loading
    query = select(Employee).options(
        joinedload(Employee.department),
        joinedload(Employee.manager),
        selectinload(Employee.certifications),
    )

    # Aplicar filtros
    if department_id:
        query = query.where(Employee.department_id == department_id)
    if is_active is not None:
        query = query.where(Employee.is_active == is_active)
    if search:
        query = query.where((Employee.name.ilike(f"%{search}%")) | (Employee.email.ilike(f"%{search}%")))

    # Contar total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Aplicar paginação
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    employees = result.scalars().all()

    return {
        "items": [emp.to_dict() for emp in employees],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get(
    "/{employee_id}",
    response_model=dict,  # Replace with EmployeeResponse
    summary="Obter funcionário por ID",
    description="Retorna os detalhes completos de um funcionário específico",
    responses={
        200: {"description": "Funcionário encontrado"},
        404: {"description": "Funcionário não encontrado"},
    },
)
@limiter.limit("100/minute")
async def get_employee(
    request: Any,
    employee_id: Annotated[UUID, ...],
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Obtém um funcionário pelo ID com todos os relacionamentos."""
    query = (
        select(Employee)
        .options(
            joinedload(Employee.department),
            joinedload(Employee.manager),
            selectinload(Employee.certifications),
            selectinload(Employee.projects),
            selectinload(Employee.time_records),
        )
        .where(Employee.id == employee_id)
    )

    result = await db.execute(query)
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")

    return employee.to_dict()


@router.post(
    "/",
    response_model=dict,  # Replace with EmployeeResponse
    status_code=status.HTTP_201_CREATED,
    summary="Criar funcionário",
    description="Cria um novo funcionário no sistema",
)
@limiter.limit("10/minute")
async def create_employee(
    request: Any,
    # employee_data: EmployeeCreate,
    employee_data: dict[str, Any],
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Cria um novo funcionário."""
    # Verificar se email já existe
    existing = await db.execute(select(Employee).where(Employee.email == employee_data.get("email")))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")

    employee = Employee(**employee_data)
    db.add(employee)
    await db.commit()
    await db.refresh(employee)

    return employee.to_dict()


@router.put(
    "/{employee_id}",
    response_model=dict,  # Replace with EmployeeResponse
    summary="Atualizar funcionário",
    description="Atualiza os dados de um funcionário existente",
)
@limiter.limit("20/minute")
async def update_employee(
    request: Any,
    employee_id: Annotated[UUID, ...],
    # employee_data: EmployeeUpdate,
    employee_data: dict[str, Any],
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Atualiza um funcionário existente."""
    query = select(Employee).where(Employee.id == employee_id)
    result = await db.execute(query)
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")

    # Atualizar apenas campos fornecidos
    for field, value in employee_data.items():
        if value is not None and hasattr(employee, field):
            setattr(employee, field, value)

    await db.commit()
    await db.refresh(employee)
    return employee.to_dict()


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover funcionário",
    description="Remove um funcionário do sistema (soft delete)",
)
@limiter.limit("5/minute")
async def delete_employee(
    request: Any,
    employee_id: Annotated[UUID, ...],
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Remove um funcionário (soft delete)."""
    query = select(Employee).where(Employee.id == employee_id)
    result = await db.execute(query)
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")

    # Soft delete
    employee.is_active = False
    await db.commit()


# Placeholder para Employee model
class Employee:
    """Placeholder - usar o modelo real do projeto."""

    def to_dict(self) -> dict[str, Any]:
        return {}
