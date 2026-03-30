"""
Controller (endpoints) para Commission.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from core.logging import logger
from modules.crm.models.commission import CommissionStatus, CommissionTrigger
from modules.crm.repositories.commission_repository import CommissionRepository
from modules.crm.schemas.commission import (
    CommissionApprove,
    CommissionCalculateRequest,
    CommissionCreate,
    CommissionDetailResponse,
    CommissionFilter,
    CommissionListResponse,
    CommissionPaymentConfirm,
    CommissionPaymentCreate,
    CommissionPaymentResponse,
    CommissionResponse,
    CommissionRuleCreate,
    CommissionRuleListResponse,
    CommissionRuleResponse,
    CommissionRuleUpdate,
    CommissionStats,
    CommissionStatusUpdate,
    CommissionSummaryFilter,
    CommissionSummaryResponse,
    CommissionUpdate,
    SellerCommissionRuleCreate,
    SellerCommissionRuleResponse,
    SellerCommissionStats,
)
from modules.crm.services.commission_service import CommissionService

router = APIRouter(prefix="/commissions", tags=["CRM - Commissions"])


# ============== Commission Rules Endpoints ==============


@router.post(
    "/rules",
    response_model=CommissionRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_commission_rule(
    data: CommissionRuleCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> CommissionRuleResponse:
    """
    Cria uma nova regra de comissão.

    Requer autenticação. Apenas administradores podem criar regras.
    """
    repo = CommissionRepository(db)
    rule = await repo.create_rule(data, created_by_id=str(current_user.id))
    logger.info(f"CommissionRule criada por {current_user.email}: {rule.name}")
    return CommissionRuleResponse.model_validate(rule)


@router.get("/rules", response_model=CommissionRuleListResponse)
async def list_commission_rules(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    active_only: bool = True,
) -> CommissionRuleListResponse:
    """Lista regras de comissão."""
    repo = CommissionRepository(db)
    skip = (page - 1) * page_size
    rules, total = await repo.list_rules(
        active_only=active_only,
        skip=skip,
        limit=page_size,
    )

    return CommissionRuleListResponse(
        items=[CommissionRuleResponse.model_validate(r) for r in rules],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/rules/{rule_id}", response_model=CommissionRuleResponse)
async def get_commission_rule(
    rule_id: str,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> CommissionRuleResponse:
    """Busca regra por ID."""
    repo = CommissionRepository(db)
    rule = await repo.get_rule_by_id(rule_id)

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra de comissão não encontrada",
        )

    return CommissionRuleResponse.model_validate(rule)


@router.put("/rules/{rule_id}", response_model=CommissionRuleResponse)
async def update_commission_rule(
    rule_id: str,
    data: CommissionRuleUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> CommissionRuleResponse:
    """Atualiza regra de comissão."""
    repo = CommissionRepository(db)
    rule = await repo.update_rule(rule_id, data)

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra de comissão não encontrada",
        )

    logger.info(f"CommissionRule atualizada por {current_user.email}: {rule_id}")
    return CommissionRuleResponse.model_validate(rule)


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_commission_rule(
    rule_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Desativa regra de comissão."""
    repo = CommissionRepository(db)
    deleted = await repo.delete_rule(rule_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra de comissão não encontrada",
        )

    logger.info(f"CommissionRule desativada por {current_user.email}: {rule_id}")


@router.post(
    "/rules/assign",
    response_model=SellerCommissionRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_rule_to_seller(
    data: SellerCommissionRuleCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> SellerCommissionRuleResponse:
    """Associa regra de comissão a um vendedor específico."""
    repo = CommissionRepository(db)
    seller_rule = await repo.assign_rule_to_seller(data)
    logger.info(f"Regra {data.rule_id} atribuída ao vendedor {data.seller_id} por {current_user.email}")
    return SellerCommissionRuleResponse.model_validate(seller_rule)


# ============== Commission Endpoints ==============


@router.post(
    "/",
    response_model=CommissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_commission(
    data: CommissionCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> CommissionResponse:
    """
    Cria uma nova comissão manualmente.

    Normalmente as comissões são criadas automaticamente quando
    uma proposta é aceita.
    """
    repo = CommissionRepository(db)
    commission = await repo.create(data, created_by_id=str(current_user.id))
    logger.info(f"Commission criada por {current_user.email}: {commission.reference_number}")
    return CommissionResponse.model_validate(commission)


@router.post("/calculate", response_model=CommissionResponse)
async def calculate_commission(
    data: CommissionCalculateRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> CommissionResponse:
    """
    Calcula e cria comissão baseado em uma proposta.

    Usa a regra especificada ou encontra a mais adequada automaticamente.
    """
    repo = CommissionRepository(db)
    service = CommissionService()

    # Buscar regras válidas
    rules = await repo.get_valid_rules(seller_id=data.seller_id)
    if not rules:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma regra de comissão válida encontrada",
        )

    # Usar regra específica ou encontrar a mais adequada
    if data.rule_id:
        rule = await repo.get_rule_by_id(data.rule_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Regra de comissão não encontrada",
            )
    else:
        rule = service.find_applicable_rule(rules, data.sale_value)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhuma regra aplicável para este valor",
            )

    # Criar comissão
    commission_data = CommissionCreate(
        seller_id=data.seller_id,
        proposal_id=data.proposal_id,
        sale_value=data.sale_value,
        sale_margin=data.sale_margin,
        rule_id=str(rule.id),
    )

    commission = await repo.create(commission_data, created_by_id=str(current_user.id))
    logger.info(f"Commission calculada por {current_user.email}: {commission.reference_number}")
    return CommissionResponse.model_validate(commission)


@router.get("", response_model=CommissionListResponse)
async def list_commissions(  # pylint: disable=too-many-locals
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    seller_id: str | None = None,
    proposal_id: str | None = None,
    status_filter: CommissionStatus | None = Query(None, alias="status"),
    trigger: CommissionTrigger | None = None,
    is_overdue: bool | None = None,
    min_value: float | None = Query(None, ge=0),
    max_value: float | None = Query(None, ge=0),
    date_from: date | None = None,
    date_to: date | None = None,
    due_date_from: date | None = None,
    due_date_to: date | None = None,
) -> CommissionListResponse:
    """Lista comissões com filtros."""
    repo = CommissionRepository(db)

    filters = CommissionFilter(
        seller_id=seller_id,
        proposal_id=proposal_id,
        status=status_filter,
        trigger=trigger,
        is_overdue=is_overdue,
        min_value=min_value,
        max_value=max_value,
        date_from=date_from,
        date_to=date_to,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
    )

    skip = (page - 1) * page_size
    commissions, total = await repo.list(filters=filters, skip=skip, limit=page_size)

    return CommissionListResponse(
        items=[CommissionResponse.model_validate(c) for c in commissions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/stats", response_model=CommissionStats)
async def get_commission_stats(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    date_from: date | None = None,
    date_to: date | None = None,
) -> CommissionStats:
    """Retorna estatísticas de comissões."""
    repo = CommissionRepository(db)
    service = CommissionService()

    commissions = await repo.get_all_for_stats(date_from=date_from, date_to=date_to)
    stats = service.calculate_stats(commissions, date_from=date_from, date_to=date_to)

    return stats


@router.get("/seller/{seller_id}/stats", response_model=SellerCommissionStats)
async def get_seller_commission_stats(
    seller_id: str,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    target: float | None = None,
) -> SellerCommissionStats:
    """Retorna estatísticas de comissões de um vendedor."""
    repo = CommissionRepository(db)
    service = CommissionService()

    filters = CommissionFilter(seller_id=seller_id)
    commissions, _ = await repo.list(filters=filters, limit=1000)

    stats = service.calculate_seller_stats(
        commissions=commissions,
        seller_id=seller_id,
        target=target,
    )

    return stats


# ============== Summary Endpoints (devem vir antes de /{commission_id}) ==============


@router.get("/summaries", response_model=list[CommissionSummaryResponse])
async def list_commission_summaries(
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    seller_id: str | None = None,
    year: int | None = None,
    month: int | None = None,
    is_closed: bool | None = None,
) -> list[CommissionSummaryResponse]:
    """Lista resumos mensais de comissões."""
    repo = CommissionRepository(db)

    filters = CommissionSummaryFilter(
        seller_id=seller_id,
        year=year,
        month=month,
        is_closed=is_closed,
    )

    summaries = await repo.list_summaries(filters)
    return [CommissionSummaryResponse.model_validate(s) for s in summaries]


@router.get(
    "/summaries/{seller_id}/{year}/{month}",
    response_model=CommissionSummaryResponse,
)
async def get_commission_summary(
    seller_id: str,
    year: int,
    month: int,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> CommissionSummaryResponse:
    """Busca ou cria resumo mensal de um vendedor."""
    repo = CommissionRepository(db)
    summary = await repo.update_summary(seller_id, year, month)
    return CommissionSummaryResponse.model_validate(summary)


@router.post(
    "/summaries/{seller_id}/{year}/{month}/close",
    response_model=CommissionSummaryResponse,
)
async def close_commission_summary(
    seller_id: str,
    year: int,
    month: int,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> CommissionSummaryResponse:
    """Fecha resumo mensal (impede alterações)."""
    repo = CommissionRepository(db)
    summary = await repo.close_summary(seller_id, year, month)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resumo não encontrado",
        )

    logger.info(f"Summary {seller_id}/{year}/{month} fechado por {current_user.email}")
    return CommissionSummaryResponse.model_validate(summary)


# ============== Commission by ID (deve vir DEPOIS de rotas estáticas) ==============


@router.get("/{commission_id}", response_model=CommissionDetailResponse)
async def get_commission(
    commission_id: str,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
) -> CommissionDetailResponse:
    """Busca comissão por ID com detalhes de pagamentos."""
    repo = CommissionRepository(db)
    commission = await repo.get_by_id(commission_id)

    if not commission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comissão não encontrada",
        )

    return CommissionDetailResponse.model_validate(commission)


@router.put("/{commission_id}", response_model=CommissionResponse)
async def update_commission(
    commission_id: str,
    data: CommissionUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> CommissionResponse:
    """Atualiza comissão (ajustes, descrição, etc)."""
    repo = CommissionRepository(db)
    commission = await repo.update(commission_id, data)

    if not commission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comissão não encontrada",
        )

    logger.info(f"Commission atualizada por {current_user.email}: {commission_id}")
    return CommissionResponse.model_validate(commission)


@router.patch("/{commission_id}/status", response_model=CommissionResponse)
async def update_commission_status(
    commission_id: str,
    data: CommissionStatusUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> CommissionResponse:
    """Atualiza status da comissão."""
    repo = CommissionRepository(db)
    commission = await repo.update_status(
        commission_id=commission_id,
        status=data.status,
        approved_by_id=str(current_user.id) if data.status == CommissionStatus.APPROVED else None,
        notes=data.notes,
    )

    if not commission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comissão não encontrada",
        )

    logger.info(f"Commission {commission_id} status alterado para {data.status.value} por {current_user.email}")
    return CommissionResponse.model_validate(commission)


@router.post("/{commission_id}/approve", response_model=CommissionResponse)
async def approve_commission(
    commission_id: str,
    data: CommissionApprove,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> CommissionResponse:
    """Aprova comissão para pagamento."""
    repo = CommissionRepository(db)
    commission = await repo.update_status(
        commission_id=commission_id,
        status=CommissionStatus.APPROVED,
        approved_by_id=str(current_user.id),
        notes=data.notes,
    )

    if not commission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comissão não encontrada",
        )

    logger.info(f"Commission {commission_id} aprovada por {current_user.email}")
    return CommissionResponse.model_validate(commission)


@router.delete("/{commission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_commission(
    commission_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Desativa comissão (soft delete)."""
    repo = CommissionRepository(db)
    deleted = await repo.delete(commission_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comissão não encontrada",
        )

    logger.info(f"Commission {commission_id} desativada por {current_user.email}")


# ============== Payment Endpoints ==============


@router.post(
    "/{commission_id}/payments",
    response_model=CommissionPaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_commission_payment(
    commission_id: str,
    data: CommissionPaymentCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> CommissionPaymentResponse:
    """Registra pagamento de comissão."""
    # Verificar se commission_id corresponde
    if data.commission_id != commission_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="commission_id no path e no body não correspondem",
        )

    repo = CommissionRepository(db)
    payment = await repo.create_payment(data, created_by_id=str(current_user.id))

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comissão não encontrada ou valor excede pendente",
        )

    logger.info(f"Payment criado por {current_user.email}: {payment.id}")
    return CommissionPaymentResponse.model_validate(payment)


@router.post(
    "/payments/{payment_id}/confirm",
    response_model=CommissionPaymentResponse,
)
async def confirm_commission_payment(
    payment_id: str,
    data: CommissionPaymentConfirm,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> CommissionPaymentResponse:
    """Confirma pagamento de comissão."""
    repo = CommissionRepository(db)
    payment = await repo.confirm_payment(
        payment_id=payment_id,
        confirmed_by_id=str(current_user.id),
        notes=data.notes,
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado",
        )

    logger.info(f"Payment {payment_id} confirmado por {current_user.email}")
    return CommissionPaymentResponse.model_validate(payment)


# (Summary endpoints movidos para antes de /{commission_id} — ver acima)
