"""
Exemplo de Controller com Type Hints Completos - Fase C

Este exemplo demonstra as melhores práticas para type hints em controllers FastAPI.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.auth.dependencies import get_current_active_user
from core.database import get_db
from core.models import User

# Modelo fictício para exemplo
try:
    from modules.operacional.models.employee import Employee
except ImportError:

    class Employee:
        """Modelo fictício para exemplo"""

        id: UUID
        department_id: UUID | None
        department: object | None
        manager: object | None
        certifications: list[object]
        projects: list[object]

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def to_dict(self) -> dict:
            return {"id": str(self.id)}

# Importar schemas específicos
# from modules.operacional.schemas.employee import EmployeeResponse, EmployeeCreate, EmployeeUpdate
# from modules.operacional.models.employee import Employee


router = APIRouter(prefix="/employees", tags=["Employees"])

# Type aliases para dependências comuns
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_active_user)]


@router.get("/", response_model=list[dict])  # Replace with actual response model
async def list_employees(
    db: DbSession,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0, description="Número de registros para pular")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Limite de registros")] = 20,
    department_id: Annotated[UUID | None, Query(description="Filtrar por departamento")] = None,
) -> list[dict]:
    """
    Lista funcionários com paginação e filtros.

    Args:
        db: Sessão do banco de dados
        current_user: Usuário autenticado
        skip: Offset para paginação
        limit: Limite de registros
        department_id: Filtro opcional por departamento

    Returns:
        Lista de funcionários

    Raises:
        HTTPException: Se houver erro de permissão
    """
    # Query com eager loading para evitar N+1
    query = (
        select(Employee)
        .options(
            joinedload(Employee.department),
            selectinload(Employee.certifications),
        )
        .offset(skip)
        .limit(limit)
    )

    if department_id:
        query = query.where(Employee.department_id == department_id)

    result = await db.execute(query)
    employees = result.scalars().all()

    return [emp.to_dict() for emp in employees]


@router.get("/{employee_id}", response_model=dict)
async def get_employee(
    employee_id: Annotated[UUID, ...],
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    """Obtém um funcionário pelo ID."""
    query = (
        select(Employee)
        .options(
            joinedload(Employee.department),
            joinedload(Employee.manager),
            selectinload(Employee.certifications),
            selectinload(Employee.projects),
        )
        .where(Employee.id == employee_id)
    )

    result = await db.execute(query)
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")

    return employee.to_dict()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_employee(
    # employee_data: EmployeeCreate,
    employee_data: dict,
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    """Cria um novo funcionário."""
    employee = Employee(**employee_data)
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return employee.to_dict()


@router.put("/{employee_id}", response_model=dict)
async def update_employee(
    employee_id: Annotated[UUID, ...],
    # employee_data: EmployeeUpdate,
    employee_data: dict,
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    """Atualiza um funcionário existente."""
    query = select(Employee).where(Employee.id == employee_id)
    result = await db.execute(query)
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")

    for field, value in employee_data.items():
        setattr(employee, field, value)

    await db.commit()
    await db.refresh(employee)
    return employee.to_dict()


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: Annotated[UUID, ...],
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Remove um funcionário."""
    query = select(Employee).where(Employee.id == employee_id)
    result = await db.execute(query)
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionário não encontrado")

    await db.delete(employee)
    await db.commit()
