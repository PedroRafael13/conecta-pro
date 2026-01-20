"""
Controller FastAPI para ServiceRequest.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.logging import logger
from modules.facilities.models.service_request import (
    ServiceRequestCategory,
    ServiceRequestPriority,
    ServiceRequestStatus,
)
from modules.facilities.repositories.service_request_repository import (
    ServiceRequestRepository,
)
from modules.facilities.schemas.service_request import (
    ServiceRequestAcknowledge,
    ServiceRequestAssign,
    ServiceRequestCancel,
    ServiceRequestComplete,
    ServiceRequestCreate,
    ServiceRequestFeedback,
    ServiceRequestFilter,
    ServiceRequestListResponse,
    ServiceRequestReject,
    ServiceRequestResponse,
    ServiceRequestStats,
    ServiceRequestUpdate,
)
from modules.facilities.services.request_classifier import request_classifier

router = APIRouter(prefix="/service-requests", tags=["ServiceRequests"])


@router.post("/", response_model=ServiceRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_service_request(
    data: ServiceRequestCreate,
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestResponse:
    """Cria uma nova solicitação de serviço."""
    repo = ServiceRequestRepository(db)
    request = await repo.create(data)
    logger.info(f"Solicitação de serviço criada: {request.id}")
    return ServiceRequestResponse.model_validate(request)


@router.get("/", response_model=ServiceRequestListResponse)
async def list_service_requests(  # pylint: disable=too-many-locals
    search: Optional[str] = Query(None),
    request_status: Optional[ServiceRequestStatus] = Query(None, alias="status"),
    priority: Optional[ServiceRequestPriority] = Query(None),
    category: Optional[ServiceRequestCategory] = Query(None),
    area_id: Optional[str] = Query(None),
    requester_id: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    is_overdue: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestListResponse:
    """Lista solicitações de serviço com filtros e paginação."""
    repo = ServiceRequestRepository(db)
    filters = ServiceRequestFilter(
        search=search,
        status=request_status,
        priority=priority,
        category=category,
        area_id=area_id,
        requester_id=requester_id,
        assigned_to=assigned_to,
        is_overdue=is_overdue,
    )
    requests, total = await repo.list(filters, page, page_size)
    total_pages = (total + page_size - 1) // page_size

    return ServiceRequestListResponse(
        items=[ServiceRequestResponse.model_validate(r) for r in requests],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=ServiceRequestStats)
async def get_service_request_stats(
    client_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestStats:
    """Obtém estatísticas de solicitações de serviço."""
    repo = ServiceRequestRepository(db)
    return await repo.get_stats(client_id, area_id)


@router.post("/classify")
async def classify_request(
    title: str = Query(..., description="Título da solicitação"),
    description: str = Query(..., description="Descrição da solicitação"),
) -> dict:
    """Classifica uma solicitação usando IA."""
    return request_classifier.classify(title, description)


@router.post("/suggest-assignee")
async def suggest_assignee(
    category: ServiceRequestCategory = Query(...),
    priority: ServiceRequestPriority = Query(...),
) -> dict:
    """Sugere responsável para uma solicitação usando IA."""
    # Retorna sugestões baseadas em categoria e prioridade
    team_mapping = {
        ServiceRequestCategory.ELETRICA: "Equipe Elétrica",
        ServiceRequestCategory.HIDRAULICA: "Equipe Hidráulica",
        ServiceRequestCategory.CLIMATIZACAO: "Equipe Climatização",
        ServiceRequestCategory.LIMPEZA: "Equipe Limpeza",
        ServiceRequestCategory.SEGURANCA: "Equipe Segurança",
        ServiceRequestCategory.JARDINAGEM: "Equipe Jardinagem",
        ServiceRequestCategory.MANUTENCAO: "Equipe Manutenção Geral",
        ServiceRequestCategory.OUTROS: "Equipe Manutenção Geral",
    }
    return {
        "suggested_team": team_mapping.get(category, "Equipe Manutenção Geral"),
        "suggested_skills": [category.value],
        "escalation_path": ["Coordenador", "Gerente de Facilities"],
        "priority_level": priority.value,
    }


@router.get("/{request_id}", response_model=ServiceRequestResponse)
async def get_service_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestResponse:
    """Obtém uma solicitação de serviço por ID."""
    repo = ServiceRequestRepository(db)
    request = await repo.get_by_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada",
        )
    return ServiceRequestResponse.model_validate(request)


@router.patch("/{request_id}", response_model=ServiceRequestResponse)
async def update_service_request(
    request_id: str,
    data: ServiceRequestUpdate,
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestResponse:
    """Atualiza uma solicitação de serviço."""
    repo = ServiceRequestRepository(db)
    request = await repo.update(request_id, data)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada",
        )
    return ServiceRequestResponse.model_validate(request)


@router.post("/{request_id}/acknowledge", response_model=ServiceRequestResponse)
async def acknowledge_service_request(
    request_id: str,
    data: ServiceRequestAcknowledge,
    acknowledged_by: str = Query(..., description="ID de quem reconheceu"),
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestResponse:
    """Reconhece uma solicitação de serviço."""
    repo = ServiceRequestRepository(db)
    request = await repo.acknowledge(
        request_id,
        acknowledged_by=acknowledged_by,
        notes=data.notes,
    )
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada",
        )
    return ServiceRequestResponse.model_validate(request)


@router.post("/{request_id}/assign", response_model=ServiceRequestResponse)
async def assign_service_request(
    request_id: str,
    data: ServiceRequestAssign,
    assigned_by: str = Query(..., description="ID de quem está atribuindo"),
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestResponse:
    """Atribui uma solicitação a um responsável."""
    repo = ServiceRequestRepository(db)
    request = await repo.assign(
        request_id,
        assigned_to=data.assigned_to,
        assigned_by=assigned_by,
        assigned_team=data.assigned_team,
        scheduled_date=data.scheduled_date,
        estimated_hours=data.estimated_hours,
    )
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada",
        )
    return ServiceRequestResponse.model_validate(request)


@router.post("/{request_id}/start", response_model=ServiceRequestResponse)
async def start_service_request(
    request_id: str,
    started_by: str = Query(..., description="ID de quem está iniciando"),
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestResponse:
    """Inicia o atendimento de uma solicitação."""
    repo = ServiceRequestRepository(db)
    request = await repo.start(request_id, started_by=started_by)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada",
        )
    return ServiceRequestResponse.model_validate(request)


@router.post("/{request_id}/complete", response_model=ServiceRequestResponse)
async def complete_service_request(
    request_id: str,
    data: ServiceRequestComplete,
    completed_by: str = Query(..., description="ID de quem está concluindo"),
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestResponse:
    """Conclui uma solicitação de serviço."""
    repo = ServiceRequestRepository(db)
    request = await repo.complete(
        request_id,
        completed_by=completed_by,
        resolution=data.resolution,
        actual_hours=data.actual_hours,
        cost=data.cost,
        photos=data.photos,
    )
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada",
        )
    return ServiceRequestResponse.model_validate(request)


@router.post("/{request_id}/reject", response_model=ServiceRequestResponse)
async def reject_service_request(
    request_id: str,
    data: ServiceRequestReject,
    rejected_by: str = Query(..., description="ID de quem rejeitou"),
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestResponse:
    """Rejeita uma solicitação de serviço."""
    repo = ServiceRequestRepository(db)
    request = await repo.reject(
        request_id,
        rejection_reason=data.rejection_reason,
        rejected_by=rejected_by,
    )
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada",
        )
    return ServiceRequestResponse.model_validate(request)


@router.post("/{request_id}/cancel", response_model=ServiceRequestResponse)
async def cancel_service_request(
    request_id: str,
    data: ServiceRequestCancel,
    cancelled_by: str = Query(..., description="ID de quem cancelou"),
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestResponse:
    """Cancela uma solicitação de serviço."""
    repo = ServiceRequestRepository(db)
    request = await repo.cancel(
        request_id,
        cancellation_reason=data.cancellation_reason,
        cancelled_by=cancelled_by,
    )
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada",
        )
    return ServiceRequestResponse.model_validate(request)


@router.post("/{request_id}/feedback", response_model=ServiceRequestResponse)
async def add_feedback(
    request_id: str,
    data: ServiceRequestFeedback,
    db: AsyncSession = Depends(get_db),
) -> ServiceRequestResponse:
    """Adiciona feedback do solicitante."""
    repo = ServiceRequestRepository(db)
    request = await repo.add_feedback(
        request_id,
        rating=data.rating,
        feedback=data.feedback,
    )
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada",
        )
    return ServiceRequestResponse.model_validate(request)


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove uma solicitação de serviço (soft delete)."""
    repo = ServiceRequestRepository(db)
    deleted = await repo.delete(request_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada",
        )
