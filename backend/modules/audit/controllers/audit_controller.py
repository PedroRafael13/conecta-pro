"""
Controller para o módulo de Auditoria e Compliance
Sprint 33: Auditoria e Compliance
"""
# pylint: disable=unused-argument,too-many-locals

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.audit.schemas import (
    # AccessHistory
    AccessHistoryCreate,
    AccessHistoryList,
    AccessHistoryResponse,
    AccessHistoryStats,
    # Dashboard
    AuditDashboard,
    # AuditLog
    AuditLogCreate,
    AuditLogList,
    AuditLogResponse,
    AuditLogStats,
    # ComplianceCheck
    ComplianceCheckCreate,
    ComplianceCheckList,
    ComplianceCheckResponse,
    ComplianceOverview,
    # ComplianceRule
    ComplianceRuleCreate,
    ComplianceRuleList,
    ComplianceRuleResponse,
    ComplianceRuleUpdate,
    # DataRetention
    DataRetentionCreate,
    DataRetentionExecution,
    DataRetentionList,
    DataRetentionResponse,
    DataRetentionUpdate,
    SecurityOverview,
)
from modules.audit.services import AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["Auditoria e Compliance"])


# ==================== Dependências ====================


async def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    """Obtém serviço de auditoria."""
    return AuditService(db)


# ==================== AuditLog Endpoints ====================


@router.post(
    "/logs", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED, summary="Cria log de auditoria"
)
async def create_audit_log(
    data: AuditLogCreate,
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> AuditLogResponse:
    """Cria um novo log de auditoria."""
    log = await service.create_audit_log(data)
    return AuditLogResponse.model_validate(log)


@router.get("/logs", response_model=AuditLogList, summary="Lista logs de auditoria")
async def list_audit_logs(
    action: str | None = None,
    category: str | None = None,
    severity: str | None = None,
    result: str | None = None,
    user_id: UUID | None = None,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    requires_review: bool | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> AuditLogList:
    """Lista logs de auditoria com filtros."""
    logs, total = await service.list_audit_logs(
        action=action,
        category=category,
        severity=severity,
        result=result,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        requires_review=requires_review,
        search=search,
        page=page,
        page_size=page_size,
    )

    pages = (total + page_size - 1) // page_size

    return AuditLogList(
        items=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/logs/stats", response_model=AuditLogStats, summary="Estatísticas de auditoria")
async def get_audit_stats(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> AuditLogStats:
    """Retorna estatísticas de auditoria."""
    return await service.get_audit_stats(start_date, end_date)


@router.get("/logs/{log_id}", response_model=AuditLogResponse, summary="Busca log por ID")
async def get_audit_log(
    log_id: UUID, service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> AuditLogResponse:
    """Busca um log de auditoria por ID."""
    log = await service.get_audit_log(log_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log não encontrado")
    return AuditLogResponse.model_validate(log)


@router.post("/logs/{log_id}/review", response_model=AuditLogResponse, summary="Completa revisão de log")
async def complete_log_review(
    log_id: UUID,
    notes: str | None = None,
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> AuditLogResponse:
    """Completa a revisão de um log de auditoria."""
    try:
        log = await service.complete_review(log_id=log_id, reviewer_id=current_user.get("id"), notes=notes)
        return AuditLogResponse.model_validate(log)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


# ==================== ComplianceRule Endpoints ====================


@router.post(
    "/rules",
    response_model=ComplianceRuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria regra de compliance",
)
async def create_compliance_rule(
    data: ComplianceRuleCreate,
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> ComplianceRuleResponse:
    """Cria uma nova regra de compliance."""
    try:
        rule = await service.create_compliance_rule(data=data, user_id=current_user.get("id"))
        return ComplianceRuleResponse.model_validate(rule)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/rules", response_model=ComplianceRuleList, summary="Lista regras de compliance")
async def list_compliance_rules(
    framework: str | None = None,
    category: str | None = None,
    rule_status: str | None = Query(None, alias="status"),
    severity: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> ComplianceRuleList:
    """Lista regras de compliance."""
    rules, total = await service.list_compliance_rules(
        framework=framework, category=category, status=rule_status, severity=severity, page=page, page_size=page_size
    )

    pages = (total + page_size - 1) // page_size

    return ComplianceRuleList(
        items=[ComplianceRuleResponse.model_validate(rule) for rule in rules],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/rules/{rule_id}", response_model=ComplianceRuleResponse, summary="Busca regra por ID")
async def get_compliance_rule(
    rule_id: UUID, service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> ComplianceRuleResponse:
    """Busca uma regra de compliance por ID."""
    rule = await service.get_compliance_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regra não encontrada")
    return ComplianceRuleResponse.model_validate(rule)


@router.put("/rules/{rule_id}", response_model=ComplianceRuleResponse, summary="Atualiza regra")
async def update_compliance_rule(
    rule_id: UUID,
    data: ComplianceRuleUpdate,
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> ComplianceRuleResponse:
    """Atualiza uma regra de compliance."""
    try:
        rule = await service.update_compliance_rule(rule_id=rule_id, data=data, user_id=current_user.get("id"))
        return ComplianceRuleResponse.model_validate(rule)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/rules/{rule_id}/activate", response_model=ComplianceRuleResponse, summary="Ativa regra")
async def activate_compliance_rule(
    rule_id: UUID, service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> ComplianceRuleResponse:
    """Ativa uma regra de compliance."""
    try:
        rule = await service.activate_rule(rule_id)
        return ComplianceRuleResponse.model_validate(rule)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove regra")
async def delete_compliance_rule(
    rule_id: UUID, service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> None:
    """Remove uma regra de compliance."""
    try:
        await service.delete_compliance_rule(rule_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


# ==================== ComplianceCheck Endpoints ====================


@router.post(
    "/checks",
    response_model=ComplianceCheckResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria verificação de compliance",
)
async def create_compliance_check(
    data: ComplianceCheckCreate,
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> ComplianceCheckResponse:
    """Cria uma nova verificação de compliance."""
    try:
        check = await service.create_compliance_check(data=data, user_id=current_user.get("id"))
        return ComplianceCheckResponse.model_validate(check)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/checks", response_model=ComplianceCheckList, summary="Lista verificações")
async def list_compliance_checks(
    rule_id: UUID | None = None,
    check_status: str | None = Query(None, alias="status"),
    result: str | None = None,
    requires_review: bool | None = None,
    remediation_required: bool | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> ComplianceCheckList:
    """Lista verificações de compliance."""
    checks, total = await service.list_compliance_checks(
        rule_id=rule_id,
        status=check_status,
        result=result,
        requires_review=requires_review,
        remediation_required=remediation_required,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )

    pages = (total + page_size - 1) // page_size

    return ComplianceCheckList(
        items=[ComplianceCheckResponse.model_validate(check) for check in checks],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/checks/{check_id}", response_model=ComplianceCheckResponse, summary="Busca verificação por ID")
async def get_compliance_check(
    check_id: UUID, service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> ComplianceCheckResponse:
    """Busca uma verificação de compliance por ID."""
    check = await service.get_compliance_check(check_id)
    if not check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verificação não encontrada")
    return ComplianceCheckResponse.model_validate(check)


@router.post("/checks/{check_id}/start", response_model=ComplianceCheckResponse, summary="Inicia verificação")
async def start_compliance_check(
    check_id: UUID, service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> ComplianceCheckResponse:
    """Inicia uma verificação de compliance."""
    try:
        check = await service.start_check(check_id=check_id, executor_id=current_user.get("id"))
        return ComplianceCheckResponse.model_validate(check)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post(
    "/checks/{check_id}/complete/compliant", response_model=ComplianceCheckResponse, summary="Marca como conforme"
)
async def complete_check_compliant(
    check_id: UUID,
    evidence: dict | None = None,
    notes: str | None = None,
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> ComplianceCheckResponse:
    """Marca verificação como conforme."""
    try:
        check = await service.complete_check_compliant(check_id=check_id, evidence=evidence, notes=notes)
        return ComplianceCheckResponse.model_validate(check)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post(
    "/checks/{check_id}/complete/non-compliant",
    response_model=ComplianceCheckResponse,
    summary="Marca como não conforme",
)
async def complete_check_non_compliant(
    check_id: UUID,
    violations: list[dict],
    remediation_deadline_days: int | None = None,
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> ComplianceCheckResponse:
    """Marca verificação como não conforme."""
    try:
        check = await service.complete_check_non_compliant(
            check_id=check_id, violations=violations, remediation_deadline_days=remediation_deadline_days
        )
        return ComplianceCheckResponse.model_validate(check)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


# ==================== DataRetention Endpoints ====================


@router.post(
    "/retention",
    response_model=DataRetentionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria política de retenção",
)
async def create_data_retention(
    data: DataRetentionCreate,
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> DataRetentionResponse:
    """Cria uma nova política de retenção de dados."""
    try:
        policy = await service.create_data_retention(data=data, user_id=current_user.get("id"))
        return DataRetentionResponse.model_validate(policy)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/retention", response_model=DataRetentionList, summary="Lista políticas de retenção")
async def list_data_retention_policies(
    data_category: str | None = None,
    retention_status: str | None = Query(None, alias="status"),
    schedule_enabled: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> DataRetentionList:
    """Lista políticas de retenção de dados."""
    policies, total = await service.list_data_retention_policies(
        data_category=data_category,
        status=retention_status,
        schedule_enabled=schedule_enabled,
        page=page,
        page_size=page_size,
    )

    pages = (total + page_size - 1) // page_size

    return DataRetentionList(
        items=[DataRetentionResponse.model_validate(p) for p in policies],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/retention/{policy_id}", response_model=DataRetentionResponse, summary="Busca política por ID")
async def get_data_retention(
    policy_id: UUID, service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> DataRetentionResponse:
    """Busca uma política de retenção por ID."""
    policy = await service.get_data_retention(policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Política não encontrada")
    return DataRetentionResponse.model_validate(policy)


@router.put("/retention/{policy_id}", response_model=DataRetentionResponse, summary="Atualiza política")
async def update_data_retention(
    policy_id: UUID,
    data: DataRetentionUpdate,
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> DataRetentionResponse:
    """Atualiza uma política de retenção."""
    try:
        policy = await service.update_data_retention(policy_id=policy_id, data=data, user_id=current_user.get("id"))
        return DataRetentionResponse.model_validate(policy)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/retention/{policy_id}/execute", response_model=DataRetentionExecution, summary="Executa política")
async def execute_retention_policy(
    policy_id: UUID, service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> DataRetentionExecution:
    """Executa uma política de retenção manualmente."""
    try:
        result = await service.execute_retention_policy(policy_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/retention/{policy_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove política")
async def delete_data_retention(
    policy_id: UUID, service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> None:
    """Remove uma política de retenção."""
    try:
        await service.delete_data_retention(policy_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


# ==================== AccessHistory Endpoints ====================


@router.post(
    "/access", response_model=AccessHistoryResponse, status_code=status.HTTP_201_CREATED, summary="Registra acesso"
)
async def record_access(
    data: AccessHistoryCreate, service: AuditService = Depends(get_audit_service)
) -> AccessHistoryResponse:
    """Registra um acesso ao sistema."""
    access = await service.record_access(data)
    return AccessHistoryResponse.model_validate(access)


@router.get("/access", response_model=AccessHistoryList, summary="Lista histórico de acessos")
async def list_access_history(
    access_type: str | None = None,
    result: str | None = None,
    user_id: UUID | None = None,
    ip_address: str | None = None,
    risk_level: str | None = None,
    anomaly_detected: bool | None = None,
    requires_review: bool | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> AccessHistoryList:
    """Lista histórico de acessos."""
    accesses, total = await service.list_access_history(
        access_type=access_type,
        result=result,
        user_id=user_id,
        ip_address=ip_address,
        risk_level=risk_level,
        anomaly_detected=anomaly_detected,
        requires_review=requires_review,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )

    pages = (total + page_size - 1) // page_size

    return AccessHistoryList(
        items=[AccessHistoryResponse.model_validate(a) for a in accesses],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/access/stats", response_model=AccessHistoryStats, summary="Estatísticas de acessos")
async def get_access_stats(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> AccessHistoryStats:
    """Retorna estatísticas de acessos."""
    return await service.get_access_stats(start_date, end_date)


@router.get("/access/{access_id}", response_model=AccessHistoryResponse, summary="Busca acesso por ID")
async def get_access_history_item(
    access_id: UUID, service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> AccessHistoryResponse:
    """Busca um registro de acesso por ID."""
    access = await service.get_access_history(access_id)
    if not access:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de acesso não encontrado")
    return AccessHistoryResponse.model_validate(access)


@router.get(
    "/access/user/{user_id}", response_model=list[AccessHistoryResponse], summary="Histórico de acessos do usuário"
)
async def get_user_access_history(
    user_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    service: AuditService = Depends(get_audit_service),
    current_user: dict = Depends(get_current_user),
) -> list[AccessHistoryResponse]:
    """Busca histórico de acessos de um usuário."""
    accesses = await service.get_user_access_history(user_id, limit)
    return [AccessHistoryResponse.model_validate(a) for a in accesses]


# ==================== Dashboard Endpoints ====================


@router.get("/dashboard", response_model=AuditDashboard, summary="Dashboard de auditoria")
async def get_audit_dashboard(
    service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> AuditDashboard:
    """Retorna dashboard de auditoria."""
    return await service.get_audit_dashboard()


@router.get("/compliance/overview", response_model=ComplianceOverview, summary="Visão geral de compliance")
async def get_compliance_overview(
    service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> ComplianceOverview:
    """Retorna visão geral de compliance."""
    return await service.get_compliance_overview()


@router.get("/security/overview", response_model=SecurityOverview, summary="Visão geral de segurança")
async def get_security_overview(
    service: AuditService = Depends(get_audit_service), current_user: dict = Depends(get_current_user)
) -> SecurityOverview:
    """Retorna visão geral de segurança."""
    return await service.get_security_overview()
