"""
Controller para Plano de Carreira.

Define endpoints REST para gestao de planos de carreira e milestones.

Prefixo: /human-resources/career
"""

import asyncio
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.people_management.human_resources.models.career import CareerPlanStatus
from modules.people_management.human_resources.publishers import (
    publish_milestone_concluido,
    publish_plano_carreira_criado,
)
from modules.people_management.human_resources.schemas.career import (
    CareerPlanCreate,
    CareerPlanListResponse,
    CareerPlanResponse,
    CareerPlanUpdate,
    MilestoneCreate,
)
from modules.people_management.human_resources.services.career_service import CareerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/career", tags=["RH - Carreira"])


@router.post(
    "/plans",
    response_model=CareerPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar plano de carreira",
)
async def create_plan(
    data: CareerPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CareerPlanResponse:
    """Cria um novo plano de carreira para um funcionario."""
    service = CareerService(db)
    try:
        plan = await service.create_plan(data)
        asyncio.create_task(
            publish_plano_carreira_criado(
                employee_id=str(getattr(data, "employee_id", "") or ""),
                plan_id=str(getattr(plan, "id", "")),
            )
        )
        return CareerPlanResponse.model_validate(plan)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar plano de carreira: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar plano de carreira.",
        )


@router.get(
    "/plans",
    response_model=CareerPlanListResponse,
    summary="Listar planos de carreira",
)
async def list_plans(
    employee_id: UUID | None = None,
    plan_status: CareerPlanStatus | None = Query(None, alias="status"),
    mentor_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CareerPlanListResponse:
    """Lista planos de carreira com filtros e paginacao."""
    service = CareerService(db)
    result = await service.list_plans(
        employee_id=employee_id,
        status=plan_status.value if plan_status else None,
        mentor_id=mentor_id,
        page=page,
        page_size=page_size,
    )
    return CareerPlanListResponse(
        items=[CareerPlanResponse.model_validate(p) for p in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get(
    "/plans/{plan_id}",
    response_model=CareerPlanResponse,
    summary="Buscar plano por ID",
)
async def get_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CareerPlanResponse:
    """Busca um plano de carreira pelo identificador."""
    service = CareerService(db)
    plan = await service.get_plan(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano de carreira nao encontrado.",
        )
    return CareerPlanResponse.model_validate(plan)


@router.put(
    "/plans/{plan_id}",
    response_model=CareerPlanResponse,
    summary="Atualizar plano de carreira",
)
async def update_plan(
    plan_id: UUID,
    data: CareerPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CareerPlanResponse:
    """Atualiza os dados de um plano de carreira."""
    service = CareerService(db)
    plan = await service.update_plan(plan_id, data)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano de carreira nao encontrado.",
        )
    return CareerPlanResponse.model_validate(plan)


@router.delete(
    "/plans/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover plano de carreira",
)
async def delete_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> None:
    """Remove um plano de carreira."""
    service = CareerService(db)
    deleted = await service.delete_plan(plan_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano de carreira nao encontrado.",
        )


@router.put(
    "/plans/{plan_id}/milestones",
    response_model=CareerPlanResponse,
    summary="Atualizar milestones do plano",
)
async def update_milestones(
    plan_id: UUID,
    milestones: list[MilestoneCreate],
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CareerPlanResponse:
    """Substitui os milestones de um plano de carreira."""
    service = CareerService(db)
    plan = await service.update_milestones(plan_id, milestones)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano de carreira nao encontrado.",
        )
    return CareerPlanResponse.model_validate(plan)


@router.post(
    "/plans/{plan_id}/milestones/{milestone_index}/complete",
    response_model=CareerPlanResponse,
    summary="Concluir milestone",
    status_code=201,
)
async def complete_milestone(
    plan_id: UUID,
    milestone_index: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CareerPlanResponse:
    """Marca um milestone como concluido."""
    service = CareerService(db)
    try:
        plan = await service.complete_milestone(plan_id, milestone_index)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plano de carreira nao encontrado.",
            )
        asyncio.create_task(
            publish_milestone_concluido(
                plan_id=str(plan_id),
                milestone_index=milestone_index,
                employee_id=str(getattr(plan, "employee_id", "") or ""),
            )
        )
        return CareerPlanResponse.model_validate(plan)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
