"""
Controller FastAPI para o módulo de Onboarding Digital.

Este módulo define todos os endpoints da API REST para gerenciamento
do processo de onboarding de funcionários.

Routers:
    router: Router principal com todos os endpoints de onboarding
"""

import logging
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth.dependencies import get_current_user

from modules.retention.onboarding.models import StepType, ProgressStatus
from modules.retention.onboarding.schemas import (
    # Checklist
    ChecklistCreate,
    ChecklistUpdate,
    ChecklistResponse,
    ChecklistDetailResponse,
    ChecklistListResponse,
    # Step
    StepCreate,
    StepUpdate,
    StepResponse,
    # Progress
    ProgressComplete,
    ProgressResponse,
    ProgressDetailResponse,
    ProgressListResponse,
    # Funcionário
    FuncionarioOnboardingCreate,
    FuncionarioOnboardingResponse,
    # Dashboard
    OnboardingDashboard,
    OnboardingAlert,
    OnboardingFilter,
    MessageResponse,
)
from modules.retention.onboarding.services import (
    OnboardingService,
    OnboardingException,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/retention/onboarding",
    tags=["Retention - Onboarding Digital"],
)


# =============================================================================
# DEPENDENCY HELPERS
# =============================================================================


def get_service(db: AsyncSession = Depends(get_db)) -> OnboardingService:
    """Obtém instância do service."""
    return OnboardingService(db)


# =============================================================================
# CHECKLIST ENDPOINTS
# =============================================================================


@router.post(
    "/checklists",
    response_model=ChecklistDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar checklist de onboarding",
    description="""
    Cria um novo checklist de onboarding para integração de funcionários.

    O checklist pode ser associado a um cargo específico ou ser genérico.
    É possível criar etapas junto com o checklist enviando a lista de etapas.
    """,
)
async def create_checklist(
    data: ChecklistCreate,
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> ChecklistDetailResponse:
    """Cria um novo checklist de onboarding."""
    try:
        checklist = await service.create_checklist(data)
        return ChecklistDetailResponse.model_validate(checklist)
    except OnboardingException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )
    except Exception as e:
        logger.error(f"Erro ao criar checklist: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar checklist",
        )


@router.get(
    "/checklists",
    response_model=ChecklistListResponse,
    summary="Listar checklists",
    description="Lista todos os checklists de onboarding com filtros e paginação.",
)
async def list_checklists(
    condominium_id: UUID = Query(..., description="ID do condomínio"),
    skip: int = Query(0, ge=0, description="Registros para pular"),
    limit: int = Query(20, ge=1, le=100, description="Limite por página"),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    search: Optional[str] = Query(None, max_length=100, description="Termo de busca"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> ChecklistListResponse:
    """Lista checklists com filtros."""
    filters = OnboardingFilter(
        condominium_id=condominium_id,
        departamento=departamento,
        search=search,
    )

    checklists, total = await service.list_checklists(
        condominium_id=condominium_id,
        skip=skip,
        limit=limit,
        filters=filters,
    )

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return ChecklistListResponse(
        items=[ChecklistResponse.model_validate(c) for c in checklists],
        total=total,
        skip=skip,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/checklists/{checklist_id}",
    response_model=ChecklistDetailResponse,
    summary="Buscar checklist",
    description="Busca um checklist por ID com todas as suas etapas.",
)
async def get_checklist(
    checklist_id: UUID = Path(..., description="ID do checklist"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> ChecklistDetailResponse:
    """Busca checklist por ID."""
    checklist = await service.get_checklist(checklist_id, include_etapas=True)

    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist não encontrado",
        )

    return ChecklistDetailResponse.model_validate(checklist)


@router.put(
    "/checklists/{checklist_id}",
    response_model=ChecklistResponse,
    summary="Atualizar checklist",
    description="Atualiza um checklist existente.",
)
async def update_checklist(
    checklist_id: UUID = Path(..., description="ID do checklist"),
    data: ChecklistUpdate = Body(...),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> ChecklistResponse:
    """Atualiza um checklist."""
    try:
        checklist = await service.update_checklist(checklist_id, data)

        if not checklist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist não encontrado",
            )

        return ChecklistResponse.model_validate(checklist)
    except OnboardingException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@router.delete(
    "/checklists/{checklist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover checklist",
    description="Remove um checklist (soft delete).",
)
async def delete_checklist(
    checklist_id: UUID = Path(..., description="ID do checklist"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> None:
    """Remove um checklist."""
    try:
        result = await service.delete_checklist(checklist_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist não encontrado",
            )
    except OnboardingException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@router.post(
    "/checklists/{checklist_id}/duplicate",
    response_model=ChecklistDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicar checklist",
    description="Cria uma cópia de um checklist existente com todas as etapas.",
)
async def duplicate_checklist(
    checklist_id: UUID = Path(..., description="ID do checklist original"),
    novo_nome: str = Query(..., min_length=3, max_length=200, description="Nome do novo checklist"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> ChecklistDetailResponse:
    """Duplica um checklist."""
    try:
        checklist = await service.duplicate_checklist(checklist_id, novo_nome)
        return ChecklistDetailResponse.model_validate(checklist)
    except OnboardingException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


# =============================================================================
# STEP ENDPOINTS
# =============================================================================


@router.post(
    "/checklists/{checklist_id}/steps",
    response_model=StepResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar etapa",
    description="Adiciona uma nova etapa a um checklist.",
)
async def create_step(
    checklist_id: UUID = Path(..., description="ID do checklist"),
    data: StepCreate = Body(...),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> StepResponse:
    """Cria uma nova etapa."""
    # Garante que checklist_id do path é usado
    data.checklist_id = checklist_id

    try:
        step = await service.create_step(data)
        return StepResponse.model_validate(step)
    except OnboardingException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@router.get(
    "/steps/{step_id}",
    response_model=StepResponse,
    summary="Buscar etapa",
    description="Busca uma etapa por ID.",
)
async def get_step(
    step_id: UUID = Path(..., description="ID da etapa"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> StepResponse:
    """Busca etapa por ID."""
    step = await service.get_step(step_id)

    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etapa não encontrada",
        )

    return StepResponse.model_validate(step)


@router.put(
    "/steps/{step_id}",
    response_model=StepResponse,
    summary="Atualizar etapa",
    description="Atualiza uma etapa existente.",
)
async def update_step(
    step_id: UUID = Path(..., description="ID da etapa"),
    data: StepUpdate = Body(...),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> StepResponse:
    """Atualiza uma etapa."""
    step = await service.update_step(step_id, data)

    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etapa não encontrada",
        )

    return StepResponse.model_validate(step)


@router.delete(
    "/steps/{step_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover etapa",
    description="Remove uma etapa do checklist.",
)
async def delete_step(
    step_id: UUID = Path(..., description="ID da etapa"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> None:
    """Remove uma etapa."""
    try:
        result = await service.delete_step(step_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Etapa não encontrada",
            )
    except OnboardingException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@router.post(
    "/checklists/{checklist_id}/steps/reorder",
    response_model=List[StepResponse],
    summary="Reordenar etapas",
    description="Reordena as etapas de um checklist.",
)
async def reorder_steps(
    checklist_id: UUID = Path(..., description="ID do checklist"),
    step_orders: List[dict] = Body(
        ...,
        description="Lista com {step_id: UUID, ordem: int}",
        example=[
            {"step_id": "uuid-1", "ordem": 1},
            {"step_id": "uuid-2", "ordem": 2},
        ],
    ),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> List[StepResponse]:
    """Reordena etapas."""
    steps = await service.reorder_steps(checklist_id, step_orders)
    return [StepResponse.model_validate(s) for s in steps]


# =============================================================================
# FUNCIONÁRIO ONBOARDING ENDPOINTS
# =============================================================================


@router.post(
    "/funcionario/{funcionario_id}/iniciar",
    response_model=FuncionarioOnboardingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar onboarding",
    description="""
    Inicia o processo de onboarding para um funcionário.

    Cria registros de progresso para todas as etapas do checklist,
    calculando as datas previstas baseadas na data de admissão.
    """,
)
async def iniciar_onboarding(
    funcionario_id: UUID = Path(..., description="ID do funcionário"),
    data: FuncionarioOnboardingCreate = Body(...),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> FuncionarioOnboardingResponse:
    """Inicia onboarding de funcionário."""
    # Garante que funcionario_id do path é usado
    data.funcionario_id = funcionario_id

    try:
        result = await service.iniciar_onboarding(data)
        return result
    except OnboardingException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@router.get(
    "/funcionario/{funcionario_id}/progress",
    response_model=FuncionarioOnboardingResponse,
    summary="Status do onboarding",
    description="Obtém o status completo do onboarding de um funcionário.",
)
async def get_funcionario_progress(
    funcionario_id: UUID = Path(..., description="ID do funcionário"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> FuncionarioOnboardingResponse:
    """Obtém status do onboarding."""
    result = await service.get_funcionario_onboarding(funcionario_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding não encontrado para este funcionário",
        )

    return result


@router.post(
    "/progress/{progress_id}/iniciar",
    response_model=ProgressResponse,
    summary="Iniciar etapa",
    description="Marca uma etapa como em andamento.",
)
async def iniciar_etapa(
    progress_id: UUID = Path(..., description="ID do progresso"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> ProgressResponse:
    """Inicia uma etapa."""
    try:
        progress = await service.iniciar_etapa(progress_id)
        return ProgressResponse.model_validate(progress)
    except OnboardingException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@router.post(
    "/progress/{progress_id}/completar",
    response_model=ProgressResponse,
    summary="Completar etapa",
    description="""
    Marca uma etapa como concluída.

    Permite adicionar observações, evidências e avaliação.
    Verifica se etapas de dependência foram concluídas.
    """,
)
async def completar_etapa(
    progress_id: UUID = Path(..., description="ID do progresso"),
    data: ProgressComplete = Body(...),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> ProgressResponse:
    """Completa uma etapa."""
    try:
        progress = await service.completar_etapa(progress_id, data)
        return ProgressResponse.model_validate(progress)
    except OnboardingException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


@router.post(
    "/progress/{progress_id}/cancelar",
    response_model=ProgressResponse,
    summary="Cancelar etapa",
    description="Cancela uma etapa não obrigatória.",
)
async def cancelar_etapa(
    progress_id: UUID = Path(..., description="ID do progresso"),
    motivo: str = Query(..., min_length=10, max_length=500, description="Motivo do cancelamento"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> ProgressResponse:
    """Cancela uma etapa."""
    try:
        progress = await service.cancelar_etapa(progress_id, motivo)
        return ProgressResponse.model_validate(progress)
    except OnboardingException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code, "details": e.details},
        )


# =============================================================================
# DASHBOARD E ALERTAS
# =============================================================================


@router.get(
    "/dashboard",
    response_model=OnboardingDashboard,
    summary="Dashboard de onboarding",
    description="Obtém métricas e indicadores do processo de onboarding.",
)
async def get_dashboard(
    condominium_id: UUID = Query(..., description="ID do condomínio"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> OnboardingDashboard:
    """Obtém dashboard de onboarding."""
    return await service.get_dashboard(condominium_id)


@router.get(
    "/alerts",
    response_model=List[OnboardingAlert],
    summary="Alertas de onboarding",
    description="Lista alertas de etapas atrasadas e próximas a vencer.",
)
async def get_alerts(
    condominium_id: UUID = Query(..., description="ID do condomínio"),
    limit: int = Query(50, ge=1, le=200, description="Limite de alertas"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> List[OnboardingAlert]:
    """Lista alertas de onboarding."""
    return await service.get_alertas(condominium_id, limit)


@router.get(
    "/pendentes",
    response_model=ProgressListResponse,
    summary="Etapas pendentes",
    description="Lista todas as etapas pendentes de um condomínio.",
)
async def list_pendentes(
    condominium_id: UUID = Query(..., description="ID do condomínio"),
    skip: int = Query(0, ge=0, description="Registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Limite por página"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> ProgressListResponse:
    """Lista etapas pendentes."""
    progressos, total = await service.list_pendentes(condominium_id, skip, limit)

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return ProgressListResponse(
        items=[ProgressResponse.model_validate(p) for p in progressos],
        total=total,
        skip=skip,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/atrasados",
    response_model=ProgressListResponse,
    summary="Etapas atrasadas",
    description="Lista todas as etapas atrasadas de um condomínio.",
)
async def list_atrasados(
    condominium_id: UUID = Query(..., description="ID do condomínio"),
    skip: int = Query(0, ge=0, description="Registros para pular"),
    limit: int = Query(50, ge=1, le=100, description="Limite por página"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> ProgressListResponse:
    """Lista etapas atrasadas."""
    progressos, total = await service.list_atrasados(condominium_id, skip, limit)

    pages = (total + limit - 1) // limit if limit > 0 else 0

    return ProgressListResponse(
        items=[ProgressResponse.model_validate(p) for p in progressos],
        total=total,
        skip=skip,
        limit=limit,
        pages=pages,
    )


@router.post(
    "/verificar-atrasos",
    response_model=MessageResponse,
    summary="Verificar atrasos",
    description="""
    Executa verificação de etapas atrasadas.

    Este endpoint pode ser chamado periodicamente via scheduler
    para marcar etapas que passaram da data prevista.
    """,
)
async def verificar_atrasos(
    condominium_id: UUID = Query(..., description="ID do condomínio"),
    service: OnboardingService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
) -> MessageResponse:
    """Verifica e marca etapas atrasadas."""
    result = await service.verificar_atrasos(condominium_id)

    return MessageResponse(
        message=f"Verificação concluída. {result['atrasados_marcados']} etapa(s) marcada(s) como atrasada(s).",
        success=True,
    )
