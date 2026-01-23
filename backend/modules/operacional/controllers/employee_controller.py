"""
Controller para listar funcionarios do modulo Operacional.
Integração com Solides DP (Tangerino) para dados em tempo real.
"""

import logging
import os
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.operacional.models.employee import Employee
from modules.operacional.permissions import Permission, require_operacional_permission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/employees", tags=["Operations - Employees"])


class EmployeeResponse(BaseModel):
    """Schema de resposta para funcionario."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    email: Optional[str] = None
    matricula: Optional[str] = None
    cargo: Optional[str] = None
    departamento: Optional[str] = None
    status: Optional[str] = None


class EmployeeListResponse(BaseModel):
    """Schema para listagem paginada."""

    items: List[EmployeeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get(
    "/",
    response_model=EmployeeListResponse,
    dependencies=[require_operacional_permission(Permission.EMPLOYEES_VIEW)],
)
async def list_employees(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Pagina atual"),
    page_size: int = Query(100, ge=1, le=500, description="Itens por pagina"),
    search: Optional[str] = Query(None, description="Buscar por nome, email ou matricula"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
) -> EmployeeListResponse:
    """
    Lista funcionarios com paginacao e filtros.
    """
    filters = [Employee.is_active.is_(True)]

    if status:
        filters.append(Employee.status == status)

    if search:
        like_term = f"%{search}%"
        filters.append(
            or_(
                Employee.nome.ilike(like_term),
                Employee.email.ilike(like_term),
                Employee.matricula.ilike(like_term),
            )
        )

    # Count total
    total_result = await db.execute(
        select(func.count(Employee.id)).where(*filters)
    )
    total = total_result.scalar_one() or 0
    total_pages = (total + page_size - 1) // page_size

    # Get items
    items_result = await db.execute(
        select(Employee)
        .where(*filters)
        .order_by(Employee.nome.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = items_result.scalars().all()

    return EmployeeListResponse(
        items=[
            EmployeeResponse(
                id=str(item.id),
                nome=item.nome,
                email=item.email,
                matricula=item.matricula,
                cargo=item.cargo,
                departamento=item.departamento,
                status=item.status,
            )
            for item in items
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ==================== INTEGRAÇÃO SOLIDES DP ====================


class SolidesEmployeeResponse(BaseModel):
    """Schema de resposta para funcionario do Solides."""

    id: str
    nome: str
    email: Optional[str] = None
    matricula: Optional[str] = None
    cargo: Optional[str] = None
    departamento: Optional[str] = None
    status: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    data_admissao: Optional[str] = None
    pis: Optional[str] = None


class SolidesEmployeeListResponse(BaseModel):
    """Schema para listagem de funcionarios do Solides."""

    items: List[SolidesEmployeeResponse]
    total: int
    source: str = "solides"


async def _get_solides_connector():
    """Inicializa o conector Solides com credenciais."""
    from uuid import UUID
    from modules.integrations.connectors.solides.connector import SolidesConnector

    api_token = os.getenv("SOLIDES_API_TOKEN")
    if not api_token:
        raise HTTPException(
            status_code=500,
            detail="Token Solides não configurado. Configure SOLIDES_API_TOKEN."
        )

    # UUID dummy para uso standalone (sem multi-tenant)
    dummy_uuid = UUID("00000000-0000-0000-0000-000000000000")

    connector = SolidesConnector(
        account_id=dummy_uuid,
        tenant_id=dummy_uuid,
        credentials={"api_token": api_token},
        config={"base_url": "https://employer.tangerino.com.br"},
    )

    await connector.setup()
    return connector


def _map_solides_employee(emp: Dict[str, Any], job_roles_map: Dict[int, str]) -> SolidesEmployeeResponse:
    """Mapeia dados do Solides para schema de resposta."""
    # Extrai cargo do jobRole
    job_role_id = None
    job_role_name = None

    if emp.get("jobRole"):
        if isinstance(emp["jobRole"], dict):
            job_role_id = emp["jobRole"].get("id")
            job_role_name = emp["jobRole"].get("name")
        elif isinstance(emp["jobRole"], int):
            job_role_id = emp["jobRole"]

    # Se não tem nome do cargo, busca no mapa
    if not job_role_name and job_role_id and job_role_id in job_roles_map:
        job_role_name = job_roles_map[job_role_id]

    # Extrai departamento
    department_name = None
    if emp.get("department"):
        if isinstance(emp["department"], dict):
            department_name = emp["department"].get("name")

    # Monta nome completo
    nome = emp.get("name", "")
    if not nome:
        nome = f"{emp.get('firstName', '')} {emp.get('lastName', '')}".strip()

    # Mapeia status (pode vir como int ou string)
    status_map = {
        "ACTIVE": "Ativo",
        "INACTIVE": "Inativo",
        "TERMINATED": "Demitido",
        "ON_LEAVE": "Afastado",
        "VACATION": "Férias",
        0: "Ativo",
        1: "Inativo",
        2: "Demitido",
    }
    status_raw = emp.get("status", "ACTIVE")
    status = status_map.get(status_raw, str(status_raw) if status_raw else "Ativo")

    # Converte data_admissao (pode vir como timestamp ou string)
    data_admissao = emp.get("admissionDate")
    if data_admissao:
        if isinstance(data_admissao, int):
            # Timestamp em milliseconds
            from datetime import datetime
            try:
                data_admissao = datetime.fromtimestamp(data_admissao / 1000).strftime("%Y-%m-%d")
            except Exception:
                data_admissao = str(data_admissao)
        else:
            data_admissao = str(data_admissao)

    return SolidesEmployeeResponse(
        id=str(emp.get("id", "")),
        nome=nome,
        email=emp.get("email"),
        matricula=emp.get("registration") or emp.get("employeeCode"),
        cargo=job_role_name,
        departamento=department_name,
        status=status,
        cpf=emp.get("cpf"),
        telefone=emp.get("phone") or emp.get("cellphone"),
        data_admissao=data_admissao,
        pis=emp.get("pis"),
    )


@router.get(
    "/solides",
    response_model=SolidesEmployeeListResponse,
    dependencies=[require_operacional_permission(Permission.EMPLOYEES_VIEW)],
)
async def list_employees_from_solides(
    current_user: CurrentActiveUser,
    search: Optional[str] = Query(None, description="Buscar por nome ou matricula"),
    status: Optional[str] = Query(None, description="Filtrar por status (ACTIVE, INACTIVE, etc)"),
    only_active: bool = Query(True, description="Apenas funcionarios ativos"),
) -> SolidesEmployeeListResponse:
    """
    Lista funcionarios diretamente da API Solides DP (Tangerino).
    Dados em tempo real do sistema de RH/DP.
    """
    try:
        connector = await _get_solides_connector()

        # Busca cargos primeiro para mapear
        job_roles_result = await connector.fetch_entities("job_roles")
        job_roles_map: Dict[int, str] = {}
        if job_roles_result.success and job_roles_result.data:
            for jr in job_roles_result.data:
                if jr.get("id") and jr.get("name"):
                    job_roles_map[jr["id"]] = jr["name"]

        logger.info(f"Carregados {len(job_roles_map)} cargos do Solides")

        # Busca funcionarios
        filters = {}
        if only_active:
            filters["status"] = "ACTIVE"
        elif status:
            filters["status"] = status

        result = await connector.fetch_entities(
            entity_type="employees",
            page_size=500,
            filters=filters if filters else None,
        )

        if not result.success:
            logger.error(f"Erro ao buscar funcionarios do Solides: {result.errors}")
            raise HTTPException(
                status_code=502,
                detail="Erro ao conectar com Solides DP"
            )

        employees = result.data or []
        logger.info(f"Recebidos {len(employees)} funcionarios do Solides")

        # Aplica filtro de busca local (API Solides não tem busca textual)
        if search:
            search_lower = search.lower()
            employees = [
                emp for emp in employees
                if search_lower in (emp.get("name", "") or "").lower()
                or search_lower in (emp.get("firstName", "") or "").lower()
                or search_lower in (emp.get("lastName", "") or "").lower()
                or search_lower in (emp.get("registration", "") or "").lower()
                or search_lower in (emp.get("employeeCode", "") or "").lower()
                or search_lower in (emp.get("email", "") or "").lower()
            ]

        # Mapeia para schema de resposta
        items = [_map_solides_employee(emp, job_roles_map) for emp in employees]

        # Ordena por nome
        items.sort(key=lambda x: x.nome or "")

        await connector.teardown()

        return SolidesEmployeeListResponse(
            items=items,
            total=len(items),
            source="solides",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao buscar funcionarios do Solides: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )
