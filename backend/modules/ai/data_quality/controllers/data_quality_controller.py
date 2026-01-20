"""
Data Quality Controller - Sprint 48.

Endpoints REST para qualidade de dados.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from modules.ai.data_quality.models import (
    DataQualityRule,
    DataQualityCheck,
    DataQualityIssue,
    DuplicateRecord,
    DataProfile,
    RuleStatusEnum,
    CheckStatusEnum,
    CheckScopeEnum,
    CheckTriggerEnum,
    IssueStatusEnum,
    DuplicateStatusEnum,
)
from modules.ai.data_quality.schemas import (
    DataQualityRuleCreate,
    DataQualityRuleUpdate,
    DataQualityRuleResponse,
    DataQualityCheckCreate,
    DataQualityCheckResponse,
    DataQualityIssueCreate,
    DataQualityIssueUpdate,
    DataQualityIssueResponse,
    IssueResolutionRequest,
    IssueBulkUpdateRequest,
    DuplicateSearchRequest,
    DuplicateRecordResponse,
    DuplicateMergeRequest,
    DuplicateRejectRequest,
    DataProfileRequest,
    DataProfileResponse,
    DataQualityDashboard,
    ValidationRequest,
    ValidationResponse,
    CleansingRequest,
    CleansingResponse,
)
from modules.ai.data_quality.repositories import DataQualityRepository
from modules.ai.data_quality.services import (
    DataValidator,
    DuplicateDetector,
    DataCleaner,
    DataProfiler,
)

router = APIRouter(prefix="/data-quality", tags=["Data Quality"])


# ============================================================
# Rules Endpoints
# ============================================================

@router.post("/rules", response_model=DataQualityRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_data: DataQualityRuleCreate,
    db: Session = Depends(get_db)
):
    """Cria regra de qualidade."""
    repo = DataQualityRepository(db)

    # Verifica se código já existe
    existing = repo.get_rule_by_code(rule_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Regra com código '{rule_data.code}' já existe"
        )

    rule = DataQualityRule(**rule_data.model_dump())
    return repo.create_rule(rule)


@router.get("/rules", response_model=List[DataQualityRuleResponse])
async def list_rules(
    entity_type: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[RuleStatusEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lista regras de qualidade."""
    repo = DataQualityRepository(db)
    rules, _ = repo.list_rules(
        entity_type=entity_type,
        category=category,
        status=status,
        skip=skip,
        limit=limit
    )
    return rules


@router.get("/rules/{rule_id}", response_model=DataQualityRuleResponse)
async def get_rule(
    rule_id: UUID,
    db: Session = Depends(get_db)
):
    """Busca regra por ID."""
    repo = DataQualityRepository(db)
    rule = repo.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra não encontrada"
        )
    return rule


@router.patch("/rules/{rule_id}", response_model=DataQualityRuleResponse)
async def update_rule(
    rule_id: UUID,
    rule_data: DataQualityRuleUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza regra."""
    repo = DataQualityRepository(db)
    rule = repo.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra não encontrada"
        )

    for field, value in rule_data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)

    return repo.update_rule(rule)


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove regra."""
    repo = DataQualityRepository(db)
    rule = repo.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra não encontrada"
        )
    repo.delete_rule(rule)


# ============================================================
# Checks Endpoints
# ============================================================

@router.post("/checks", response_model=DataQualityCheckResponse, status_code=status.HTTP_201_CREATED)
async def create_check(
    check_data: DataQualityCheckCreate,
    db: Session = Depends(get_db)
):
    """Cria e executa verificação de qualidade."""
    repo = DataQualityRepository(db)

    check = DataQualityCheck(
        entity_type=check_data.entity_type,
        scope=check_data.scope,
        entity_ids=check_data.entity_ids,
        rule_ids=check_data.rule_ids,
        sample_size=check_data.sample_size,
        sample_percentage=check_data.sample_percentage,
        auto_fix_enabled=check_data.auto_fix_enabled,
        parameters=check_data.parameters,
        trigger=CheckTriggerEnum.API
    )

    return repo.create_check(check)


@router.get("/checks", response_model=List[DataQualityCheckResponse])
async def list_checks(
    entity_type: Optional[str] = None,
    status: Optional[CheckStatusEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lista verificações."""
    repo = DataQualityRepository(db)
    checks, _ = repo.list_checks(
        entity_type=entity_type,
        status=status,
        skip=skip,
        limit=limit
    )
    return checks


@router.get("/checks/{check_id}", response_model=DataQualityCheckResponse)
async def get_check(
    check_id: UUID,
    db: Session = Depends(get_db)
):
    """Busca verificação por ID."""
    repo = DataQualityRepository(db)
    check = repo.get_check(check_id)
    if not check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verificação não encontrada"
        )
    return check


# ============================================================
# Issues Endpoints
# ============================================================

@router.get("/issues", response_model=List[DataQualityIssueResponse])
async def list_issues(
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    status: Optional[IssueStatusEnum] = None,
    severity: Optional[str] = None,
    check_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lista issues de qualidade."""
    repo = DataQualityRepository(db)
    issues, _ = repo.list_issues(
        entity_type=entity_type,
        entity_id=entity_id,
        status=status,
        check_id=check_id,
        skip=skip,
        limit=limit
    )
    return issues


@router.get("/issues/{issue_id}", response_model=DataQualityIssueResponse)
async def get_issue(
    issue_id: UUID,
    db: Session = Depends(get_db)
):
    """Busca issue por ID."""
    repo = DataQualityRepository(db)
    issue = repo.get_issue(issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue não encontrado"
        )
    return issue


@router.patch("/issues/{issue_id}", response_model=DataQualityIssueResponse)
async def update_issue(
    issue_id: UUID,
    issue_data: DataQualityIssueUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza issue."""
    repo = DataQualityRepository(db)
    issue = repo.get_issue(issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue não encontrado"
        )

    for field, value in issue_data.model_dump(exclude_unset=True).items():
        setattr(issue, field, value)

    return repo.update_issue(issue)


@router.post("/issues/{issue_id}/resolve", response_model=DataQualityIssueResponse)
async def resolve_issue(
    issue_id: UUID,
    resolution: IssueResolutionRequest,
    db: Session = Depends(get_db)
):
    """Resolve issue."""
    repo = DataQualityRepository(db)
    issue = repo.get_issue(issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue não encontrado"
        )

    if resolution.resolution_type == "fixed":
        issue.mark_fixed(notes=resolution.notes)
    elif resolution.resolution_type == "ignored":
        issue.mark_ignored(notes=resolution.notes)
    elif resolution.resolution_type == "false_positive":
        issue.mark_false_positive(notes=resolution.notes)

    return repo.update_issue(issue)


@router.post("/issues/bulk-update")
async def bulk_update_issues(
    request: IssueBulkUpdateRequest,
    db: Session = Depends(get_db)
):
    """Atualiza issues em lote."""
    repo = DataQualityRepository(db)
    updates = {}
    if request.status:
        updates["status"] = request.status
    if request.assigned_to:
        updates["assigned_to"] = request.assigned_to
    if request.severity:
        updates["severity"] = request.severity

    count = repo.bulk_update_issues(request.issue_ids, updates)
    return {"updated": count}


# ============================================================
# Duplicates Endpoints
# ============================================================

@router.get("/duplicates", response_model=List[DuplicateRecordResponse])
async def list_duplicates(
    entity_type: Optional[str] = None,
    status: Optional[DuplicateStatusEnum] = None,
    min_score: Optional[float] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lista duplicatas detectadas."""
    repo = DataQualityRepository(db)
    duplicates, _ = repo.list_duplicates(
        entity_type=entity_type,
        status=status,
        min_score=min_score,
        skip=skip,
        limit=limit
    )
    return duplicates


@router.get("/duplicates/{duplicate_id}", response_model=DuplicateRecordResponse)
async def get_duplicate(
    duplicate_id: UUID,
    db: Session = Depends(get_db)
):
    """Busca duplicata por ID."""
    repo = DataQualityRepository(db)
    duplicate = repo.get_duplicate(duplicate_id)
    if not duplicate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Duplicata não encontrada"
        )
    return duplicate


@router.post("/duplicates/{duplicate_id}/merge", response_model=DuplicateRecordResponse)
async def merge_duplicates(
    duplicate_id: UUID,
    merge_request: DuplicateMergeRequest,
    db: Session = Depends(get_db)
):
    """Realiza merge de duplicatas."""
    repo = DataQualityRepository(db)
    duplicate = repo.get_duplicate(duplicate_id)
    if not duplicate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Duplicata não encontrada"
        )

    # Simula merge (implementação real dependeria do tipo de entidade)
    import uuid as uuid_lib
    duplicate.merge(
        master_id=merge_request.master_record_id,
        merged_id=uuid_lib.uuid4(),
        strategy=merge_request.strategy
    )

    return repo.update_duplicate(duplicate)


@router.post("/duplicates/{duplicate_id}/reject", response_model=DuplicateRecordResponse)
async def reject_duplicate(
    duplicate_id: UUID,
    reject_request: DuplicateRejectRequest,
    db: Session = Depends(get_db)
):
    """Rejeita duplicata como falso positivo."""
    repo = DataQualityRepository(db)
    duplicate = repo.get_duplicate(duplicate_id)
    if not duplicate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Duplicata não encontrada"
        )

    duplicate.reject(reason=reject_request.reason)
    return repo.update_duplicate(duplicate)


# ============================================================
# Profiles Endpoints
# ============================================================

@router.post("/profiles", response_model=DataProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_request: DataProfileRequest,
    db: Session = Depends(get_db)
):
    """Cria perfil de dados."""
    repo = DataQualityRepository(db)
    profiler = DataProfiler()

    # Por enquanto, cria perfil vazio (dados reais viriam de consulta)
    import uuid as uuid_lib
    profile_code = f"PROF-{profile_request.entity_type}-{uuid_lib.uuid4().hex[:8]}"

    profile = DataProfile(
        profile_code=profile_code,
        entity_type=profile_request.entity_type,
        field_name=profile_request.field_name,
        is_entity_profile=profile_request.field_name is None
    )
    profile.start_profiling()
    profile.total_records = 0
    profile.complete_profiling()

    return repo.create_profile(profile)


@router.get("/profiles", response_model=List[DataProfileResponse])
async def list_profiles(
    entity_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lista perfis de dados."""
    repo = DataQualityRepository(db)
    profiles, _ = repo.list_profiles(entity_type=entity_type, skip=skip, limit=limit)
    return profiles


@router.get("/profiles/{profile_id}", response_model=DataProfileResponse)
async def get_profile(
    profile_id: UUID,
    db: Session = Depends(get_db)
):
    """Busca perfil por ID."""
    repo = DataQualityRepository(db)
    profile = repo.get_profile(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil não encontrado"
        )
    return profile


# ============================================================
# Validation Endpoints
# ============================================================

@router.post("/validate", response_model=ValidationResponse)
async def validate_data(
    request: ValidationRequest,
    db: Session = Depends(get_db)
):
    """Valida dados contra regras."""
    repo = DataQualityRepository(db)
    validator = DataValidator()

    # Busca regras aplicáveis
    if request.rule_ids:
        rules = [repo.get_rule(rid) for rid in request.rule_ids if repo.get_rule(rid)]
    else:
        rules = repo.get_active_rules_for_entity(request.entity_type)

    # Executa validação
    is_valid, issues, fixed_data = validator.validate_record(
        data=request.data,
        rules=rules,
        entity_type=request.entity_type
    )

    return ValidationResponse(
        is_valid=is_valid,
        errors=[i.to_dict() for i in issues if i.severity.value in ["critical", "high"]],
        warnings=[i.to_dict() for i in issues if i.severity.value in ["medium", "low", "info"]],
        fixed_data=fixed_data if request.auto_fix else None,
        fixes_applied=len([i for i in issues if i.can_auto_fix]) if request.auto_fix else 0
    )


@router.post("/cleanse", response_model=CleansingResponse)
async def cleanse_data(request: CleansingRequest):
    """Limpa e padroniza dados."""
    cleaner = DataCleaner()

    cleaned_data, changes = cleaner.clean_record(
        data=request.data,
        default_operations=request.operations if request.operations else None
    )

    return CleansingResponse(
        original_data=request.data,
        cleaned_data=cleaned_data,
        changes=changes,
        changes_count=len(changes)
    )


# ============================================================
# Dashboard Endpoints
# ============================================================

@router.get("/dashboard", response_model=DataQualityDashboard)
async def get_dashboard(db: Session = Depends(get_db)):
    """Retorna dashboard de qualidade de dados."""
    repo = DataQualityRepository(db)
    stats = repo.get_quality_stats()

    # Busca últimas verificações
    checks, _ = repo.list_checks(status=CheckStatusEnum.COMPLETED, limit=5)

    # Calcula score geral
    overall_score = 0.0
    if checks:
        scores = [c.overall_score for c in checks if c.overall_score]
        overall_score = sum(scores) / len(scores) if scores else 0

    return DataQualityDashboard(
        overall_score=overall_score,
        total_records=0,  # Seria calculado agregando de todas as entidades
        total_issues=stats["total_open_issues"],
        issues_by_severity=stats["issues_by_severity"],
        issues_by_type=stats["issues_by_type"],
        top_problematic_fields=[],  # Requer análise mais profunda
        quality_trend=[],  # Requer dados históricos
        recent_checks=[c.to_summary_dict() for c in checks],
        duplicate_groups_pending=stats["pending_duplicates"],
        profiles_outdated=stats["outdated_profiles"]
    )


@router.get("/stats/{entity_type}")
async def get_entity_stats(
    entity_type: str,
    db: Session = Depends(get_db)
):
    """Retorna estatísticas para entidade específica."""
    repo = DataQualityRepository(db)

    # Última verificação
    latest_check = repo.get_latest_check(entity_type)

    # Contagem de issues
    issues, total_issues = repo.list_issues(entity_type=entity_type, limit=0)

    # Perfil mais recente
    profile = repo.get_profile_for_field(entity_type)

    return {
        "entity_type": entity_type,
        "latest_check": latest_check.to_summary_dict() if latest_check else None,
        "total_open_issues": repo.get_open_issues_count(entity_type),
        "quality_score": latest_check.overall_score if latest_check else None,
        "profile": profile.to_summary_dict() if profile else None
    }
