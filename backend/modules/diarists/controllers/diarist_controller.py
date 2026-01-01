"""Controller para endpoints de Diaristas."""

import logging
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user, require_roles
from core.database import get_db
from modules.diarists.models.diarist import (
    DiaristStatus,
    DiaristType,
    AssignmentStatus,
    ScheduleStatus,
    PaymentStatus,
)
from modules.diarists.schemas.diarist_schemas import (
    DiaristCreate,
    DiaristUpdate,
    DiaristResponse,
    DiaristListResponse,
    DiaristAssignmentCreate,
    DiaristAssignmentResponse,
    DiaristScheduleCreate,
    DiaristScheduleResponse,
    DiaristPaymentCreate,
    DiaristPaymentResponse,
    DiaristEvaluationCreate,
    DiaristEvaluationResponse,
    CheckinRequest,
    CheckoutRequest,
    DiaristSuggestionResponse,
    DiaristAvailabilityResponse,
    DiaristPerformanceResponse,
    ScheduleOptimizationResponse,
)
from modules.diarists.services.diarist_service import DiaristService
from modules.diarists.services.diarist_ai_service import DiaristAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diarists", tags=["Diaristas"])


def get_diarist_service(db: Session = Depends(get_db)) -> DiaristService:
    """Dependency para DiaristService."""
    return DiaristService(db)


def get_ai_service(db: Session = Depends(get_db)) -> DiaristAIService:
    """Dependency para DiaristAIService."""
    return DiaristAIService(db)


# ==================== DIARIST ENDPOINTS ====================


@router.post(
    "/",
    response_model=DiaristResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(["admin", "sindico"]))],
)
async def create_diarist(
    data: DiaristCreate,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristResponse:
    """Cria uma nova diarista."""
    try:
        diarist = service.create_diarist(data)
        return DiaristResponse.model_validate(diarist)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=DiaristListResponse)
async def list_diarists(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: Optional[DiaristStatus] = Query(None, alias="status"),
    tipo: Optional[DiaristType] = None,
    search: Optional[str] = None,
    condominio_id: Optional[UUID] = None,
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> DiaristListResponse:
    """Lista diaristas com filtros."""
    diarists = service.list_diarists(
        skip=skip,
        limit=limit,
        status=status_filter,
        tipo=tipo,
        search=search,
        condominio_id=condominio_id,
    )
    return DiaristListResponse(
        items=[DiaristResponse.model_validate(d) for d in diarists],
        total=len(diarists),
        skip=skip,
        limit=limit,
    )


@router.get("/{diarist_id}", response_model=DiaristResponse)
async def get_diarist(
    diarist_id: UUID,
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> DiaristResponse:
    """Busca diarista por ID."""
    diarist = service.get_diarist(diarist_id)
    if not diarist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diarista não encontrada",
        )
    return DiaristResponse.model_validate(diarist)


@router.put(
    "/{diarist_id}",
    response_model=DiaristResponse,
    dependencies=[Depends(require_roles(["admin", "sindico"]))],
)
async def update_diarist(
    diarist_id: UUID,
    data: DiaristUpdate,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristResponse:
    """Atualiza diarista."""
    diarist = service.update_diarist(diarist_id, data)
    if not diarist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diarista não encontrada",
        )
    return DiaristResponse.model_validate(diarist)


@router.post(
    "/{diarist_id}/activate",
    response_model=DiaristResponse,
    dependencies=[Depends(require_roles(["admin", "sindico"]))],
)
async def activate_diarist(
    diarist_id: UUID,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristResponse:
    """Ativa uma diarista."""
    diarist = service.activate_diarist(diarist_id)
    if not diarist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diarista não encontrada",
        )
    return DiaristResponse.model_validate(diarist)


@router.post(
    "/{diarist_id}/deactivate",
    response_model=DiaristResponse,
    dependencies=[Depends(require_roles(["admin", "sindico"]))],
)
async def deactivate_diarist(
    diarist_id: UUID,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristResponse:
    """Desativa uma diarista."""
    diarist = service.deactivate_diarist(diarist_id)
    if not diarist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diarista não encontrada",
        )
    return DiaristResponse.model_validate(diarist)


@router.delete(
    "/{diarist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(["admin"]))],
)
async def delete_diarist(
    diarist_id: UUID,
    service: DiaristService = Depends(get_diarist_service),
) -> None:
    """Remove diarista (soft delete)."""
    if not service.delete_diarist(diarist_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diarista não encontrada",
        )


@router.get("/{diarist_id}/metrics")
async def get_diarist_metrics(
    diarist_id: UUID,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> dict:
    """Retorna métricas da diarista."""
    return service.get_diarist_metrics(
        diarist_id=diarist_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


# ==================== ASSIGNMENT ENDPOINTS ====================


@router.post(
    "/assignments",
    response_model=DiaristAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(["admin", "sindico"]))],
)
async def create_assignment(
    data: DiaristAssignmentCreate,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristAssignmentResponse:
    """Cria uma alocação de diarista."""
    try:
        assignment = service.create_assignment(data)
        return DiaristAssignmentResponse.model_validate(assignment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/assignments", response_model=list[DiaristAssignmentResponse])
async def list_assignments(
    diarist_id: Optional[UUID] = None,
    condominio_id: Optional[UUID] = None,
    status_filter: Optional[AssignmentStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> list[DiaristAssignmentResponse]:
    """Lista alocações."""
    assignments = service.list_assignments(
        diarist_id=diarist_id,
        condominio_id=condominio_id,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return [DiaristAssignmentResponse.model_validate(a) for a in assignments]


@router.get(
    "/assignments/{assignment_id}",
    response_model=DiaristAssignmentResponse,
)
async def get_assignment(
    assignment_id: UUID,
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> DiaristAssignmentResponse:
    """Busca alocação por ID."""
    assignment = service.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alocação não encontrada",
        )
    return DiaristAssignmentResponse.model_validate(assignment)


@router.post(
    "/assignments/{assignment_id}/cancel",
    dependencies=[Depends(require_roles(["admin", "sindico"]))],
)
async def cancel_assignment(
    assignment_id: UUID,
    service: DiaristService = Depends(get_diarist_service),
) -> dict:
    """Cancela uma alocação."""
    if not service.cancel_assignment(assignment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alocação não encontrada",
        )
    return {"message": "Alocação cancelada com sucesso"}


# ==================== SCHEDULE ENDPOINTS ====================


@router.post(
    "/schedules",
    response_model=DiaristScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(["admin", "sindico", "porteiro"]))],
)
async def create_schedule(
    data: DiaristScheduleCreate,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristScheduleResponse:
    """Cria um agendamento avulso."""
    try:
        schedule = service.create_schedule(data)
        return DiaristScheduleResponse.model_validate(schedule)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/schedules", response_model=list[DiaristScheduleResponse])
async def list_schedules(
    diarist_id: Optional[UUID] = None,
    condominio_id: Optional[UUID] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    status_filter: Optional[ScheduleStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> list[DiaristScheduleResponse]:
    """Lista agendamentos."""
    schedules = service.list_schedules(
        diarist_id=diarist_id,
        condominio_id=condominio_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return [DiaristScheduleResponse.model_validate(s) for s in schedules]


@router.get("/schedules/today", response_model=list[DiaristScheduleResponse])
async def get_today_schedules(
    condominio_id: Optional[UUID] = None,
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> list[DiaristScheduleResponse]:
    """Busca agendamentos de hoje."""
    schedules = service.get_today_schedules(condominio_id)
    return [DiaristScheduleResponse.model_validate(s) for s in schedules]


@router.get(
    "/schedules/{schedule_id}",
    response_model=DiaristScheduleResponse,
)
async def get_schedule(
    schedule_id: UUID,
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> DiaristScheduleResponse:
    """Busca agendamento por ID."""
    schedule = service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    return DiaristScheduleResponse.model_validate(schedule)


@router.post(
    "/schedules/{schedule_id}/confirm",
    response_model=DiaristScheduleResponse,
    dependencies=[Depends(require_roles(["admin", "sindico", "porteiro"]))],
)
async def confirm_schedule(
    schedule_id: UUID,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristScheduleResponse:
    """Confirma um agendamento."""
    schedule = service.confirm_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agendamento não pode ser confirmado",
        )
    return DiaristScheduleResponse.model_validate(schedule)


@router.post(
    "/schedules/{schedule_id}/cancel",
    response_model=DiaristScheduleResponse,
    dependencies=[Depends(require_roles(["admin", "sindico"]))],
)
async def cancel_schedule(
    schedule_id: UUID,
    motivo: Optional[str] = None,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristScheduleResponse:
    """Cancela um agendamento."""
    try:
        schedule = service.cancel_schedule(schedule_id, motivo)
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agendamento não encontrado",
            )
        return DiaristScheduleResponse.model_validate(schedule)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/schedules/checkin",
    response_model=DiaristScheduleResponse,
    dependencies=[Depends(require_roles(["admin", "sindico", "porteiro"]))],
)
async def register_checkin(
    data: CheckinRequest,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristScheduleResponse:
    """Registra check-in."""
    schedule = service.register_checkin(data)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in não pode ser registrado",
        )
    return DiaristScheduleResponse.model_validate(schedule)


@router.post(
    "/schedules/checkout",
    response_model=DiaristScheduleResponse,
    dependencies=[Depends(require_roles(["admin", "sindico", "porteiro"]))],
)
async def register_checkout(
    data: CheckoutRequest,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristScheduleResponse:
    """Registra check-out."""
    schedule = service.register_checkout(data)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out não pode ser registrado",
        )
    return DiaristScheduleResponse.model_validate(schedule)


# ==================== PAYMENT ENDPOINTS ====================


@router.post(
    "/payments",
    response_model=DiaristPaymentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(["admin", "sindico"]))],
)
async def create_payment(
    data: DiaristPaymentCreate,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristPaymentResponse:
    """Cria um pagamento."""
    try:
        payment = service.create_payment(data)
        return DiaristPaymentResponse.model_validate(payment)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/payments", response_model=list[DiaristPaymentResponse])
async def list_payments(
    diarist_id: Optional[UUID] = None,
    condominio_id: Optional[UUID] = None,
    status_filter: Optional[PaymentStatus] = Query(None, alias="status"),
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> list[DiaristPaymentResponse]:
    """Lista pagamentos."""
    payments = service.list_payments(
        diarist_id=diarist_id,
        condominio_id=condominio_id,
        status=status_filter,
        data_inicio=data_inicio,
        data_fim=data_fim,
        skip=skip,
        limit=limit,
    )
    return [DiaristPaymentResponse.model_validate(p) for p in payments]


@router.get("/payments/pending", response_model=list[DiaristPaymentResponse])
async def get_pending_payments(
    condominio_id: Optional[UUID] = None,
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> list[DiaristPaymentResponse]:
    """Lista pagamentos pendentes."""
    payments = service.get_pending_payments(condominio_id)
    return [DiaristPaymentResponse.model_validate(p) for p in payments]


@router.get(
    "/payments/{payment_id}",
    response_model=DiaristPaymentResponse,
)
async def get_payment(
    payment_id: UUID,
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> DiaristPaymentResponse:
    """Busca pagamento por ID."""
    payment = service.get_payment(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado",
        )
    return DiaristPaymentResponse.model_validate(payment)


@router.post(
    "/payments/{payment_id}/process",
    response_model=DiaristPaymentResponse,
    dependencies=[Depends(require_roles(["admin", "sindico"]))],
)
async def process_payment(
    payment_id: UUID,
    data_pagamento: date,
    comprovante: Optional[str] = None,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristPaymentResponse:
    """Processa pagamento."""
    payment = service.process_payment(
        payment_id=payment_id,
        data_pagamento=data_pagamento,
        comprovante=comprovante,
    )
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pagamento não pode ser processado",
        )
    return DiaristPaymentResponse.model_validate(payment)


@router.post(
    "/payments/generate",
    response_model=DiaristPaymentResponse,
    dependencies=[Depends(require_roles(["admin", "sindico"]))],
)
async def generate_payment(
    diarist_id: UUID,
    condominio_id: UUID,
    data_inicio: date,
    data_fim: date,
    service: DiaristService = Depends(get_diarist_service),
) -> DiaristPaymentResponse:
    """Gera pagamento a partir de agendamentos concluídos."""
    payment = service.generate_payment_from_schedules(
        diarist_id=diarist_id,
        condominio_id=condominio_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum agendamento concluído no período",
        )
    return DiaristPaymentResponse.model_validate(payment)


# ==================== EVALUATION ENDPOINTS ====================


@router.post(
    "/evaluations",
    response_model=DiaristEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_evaluation(
    data: DiaristEvaluationCreate,
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> DiaristEvaluationResponse:
    """Cria uma avaliação."""
    try:
        evaluation = service.create_evaluation(data)
        return DiaristEvaluationResponse.model_validate(evaluation)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/evaluations", response_model=list[DiaristEvaluationResponse])
async def list_evaluations(
    diarist_id: Optional[UUID] = None,
    nota_minima: Optional[int] = Query(None, ge=1, le=5),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> list[DiaristEvaluationResponse]:
    """Lista avaliações."""
    evaluations = service.list_evaluations(
        diarist_id=diarist_id,
        nota_minima=nota_minima,
        skip=skip,
        limit=limit,
    )
    return [DiaristEvaluationResponse.model_validate(e) for e in evaluations]


@router.get(
    "/evaluations/{evaluation_id}",
    response_model=DiaristEvaluationResponse,
)
async def get_evaluation(
    evaluation_id: UUID,
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> DiaristEvaluationResponse:
    """Busca avaliação por ID."""
    evaluation = service.get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliação não encontrada",
        )
    return DiaristEvaluationResponse.model_validate(evaluation)


# ==================== AI ENDPOINTS ====================


@router.get("/ai/suggest", response_model=DiaristSuggestionResponse)
async def suggest_diarists(
    condominio_id: UUID,
    data: date,
    tipo: Optional[DiaristType] = None,
    duracao_horas: int = Query(8, ge=1, le=12),
    priorizar_conhecidas: bool = True,
    ai_service: DiaristAIService = Depends(get_ai_service),
    _: dict = Depends(get_current_user),
) -> DiaristSuggestionResponse:
    """Sugere diaristas para uma data usando IA."""
    return ai_service.suggest_diarists(
        condominio_id=condominio_id,
        data=data,
        tipo=tipo,
        duracao_horas=duracao_horas,
        priorizar_conhecidas=priorizar_conhecidas,
    )


@router.get("/ai/availability", response_model=DiaristAvailabilityResponse)
async def analyze_availability(
    condominio_id: UUID,
    data_inicio: date,
    data_fim: date,
    tipo: Optional[DiaristType] = None,
    ai_service: DiaristAIService = Depends(get_ai_service),
    _: dict = Depends(get_current_user),
) -> DiaristAvailabilityResponse:
    """Analisa disponibilidade de diaristas em um período."""
    return ai_service.analyze_availability(
        condominio_id=condominio_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        tipo=tipo,
    )


@router.get(
    "/ai/performance/{diarist_id}",
    response_model=DiaristPerformanceResponse,
)
async def analyze_performance(
    diarist_id: UUID,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    ai_service: DiaristAIService = Depends(get_ai_service),
    _: dict = Depends(get_current_user),
) -> DiaristPerformanceResponse:
    """Analisa performance de uma diarista usando IA."""
    try:
        return ai_service.analyze_performance(
            diarist_id=diarist_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/ai/optimize", response_model=ScheduleOptimizationResponse)
async def optimize_schedule(
    condominio_id: UUID,
    data_inicio: date,
    data_fim: date,
    budget: Optional[Decimal] = None,
    ai_service: DiaristAIService = Depends(get_ai_service),
    _: dict = Depends(get_current_user),
) -> ScheduleOptimizationResponse:
    """Otimiza agendamentos do condomínio usando IA."""
    return ai_service.optimize_schedule(
        condominio_id=condominio_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        budget=budget,
    )


# ==================== STATISTICS ENDPOINTS ====================


@router.get("/statistics/condominio/{condominio_id}")
async def get_condominio_statistics(
    condominio_id: UUID,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> dict:
    """Retorna estatísticas de diaristas do condomínio."""
    return service.get_condominio_statistics(
        condominio_id=condominio_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get("/statistics/ranking")
async def get_top_diarists(
    condominio_id: Optional[UUID] = None,
    limit: int = Query(10, ge=1, le=50),
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> list[dict]:
    """Retorna ranking das melhores diaristas."""
    return service.get_top_diarists(
        condominio_id=condominio_id,
        limit=limit,
    )


@router.get("/available")
async def get_available_diarists(
    data: date,
    tipo: Optional[DiaristType] = None,
    condominio_id: Optional[UUID] = None,
    service: DiaristService = Depends(get_diarist_service),
    _: dict = Depends(get_current_user),
) -> list[DiaristResponse]:
    """Busca diaristas disponíveis para uma data."""
    diarists = service.get_available_diarists(
        data=data,
        tipo=tipo,
        condominio_id=condominio_id,
    )
    return [DiaristResponse.model_validate(d) for d in diarists]
