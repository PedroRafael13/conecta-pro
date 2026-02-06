"""
Data Quality Schemas - Sprint 48.

Schemas Pydantic para validação de dados na API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.ai.data_quality.models import (
    RuleTypeEnum,
    RuleSeverityEnum,
    RuleStatusEnum,
    RuleCategoryEnum,
    CheckStatusEnum,
    CheckScopeEnum,
    CheckTriggerEnum,
    IssueSeverityEnum,
    IssueStatusEnum,
    IssueTypeEnum,
    DuplicateStatusEnum,
    DuplicateTypeEnum,
    MergeStrategyEnum,
    ProfileStatusEnum,
    DataTypeEnum,
)


# ============================================================
# Rule Schemas
# ============================================================

class DataQualityRuleBase(BaseModel):
    """Schema base para regra de qualidade."""

    code: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    rule_type: RuleTypeEnum
    category: RuleCategoryEnum = RuleCategoryEnum.VALIDITY
    severity: RuleSeverityEnum = RuleSeverityEnum.MEDIUM
    entity_type: str = Field(..., min_length=1, max_length=100)
    field_name: Optional[str] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Valida código da regra."""
        import re
        if not re.match(r"^[a-z][a-z0-9_]*$", v):
            raise ValueError("Código deve conter apenas letras minúsculas, números e underscore")
        return v


class DataQualityRuleCreate(DataQualityRuleBase):
    """Schema para criar regra."""

    condition: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    threshold: Optional[float] = None
    regex_pattern: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: List[str] = Field(default_factory=list)
    action_on_violation: str = "flag"
    auto_fix_enabled: bool = False
    fix_function: Optional[str] = None
    error_message: Optional[str] = None
    priority: int = Field(default=50, ge=1, le=100)
    tags: List[str] = Field(default_factory=list)


class DataQualityRuleUpdate(BaseModel):
    """Schema para atualizar regra."""

    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[RuleCategoryEnum] = None
    severity: Optional[RuleSeverityEnum] = None
    status: Optional[RuleStatusEnum] = None
    condition: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    threshold: Optional[float] = None
    auto_fix_enabled: Optional[bool] = None
    error_message: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=1, le=100)
    is_active: Optional[bool] = None


class DataQualityRuleResponse(DataQualityRuleBase):
    """Schema de resposta para regra."""

    id: UUID
    status: RuleStatusEnum
    total_checks: int
    total_violations: int
    violation_rate: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# Check Schemas
# ============================================================

class DataQualityCheckCreate(BaseModel):
    """Schema para criar verificação."""

    name: Optional[str] = None
    entity_type: str = Field(..., min_length=1, max_length=100)
    scope: CheckScopeEnum = CheckScopeEnum.FULL
    entity_ids: List[UUID] = Field(default_factory=list)
    rule_ids: List[UUID] = Field(default_factory=list)
    sample_size: Optional[int] = Field(default=None, ge=1)
    sample_percentage: Optional[float] = Field(default=None, ge=0.1, le=100)
    auto_fix_enabled: bool = False
    parameters: Dict[str, Any] = Field(default_factory=dict)


class DataQualityCheckResponse(BaseModel):
    """Schema de resposta para verificação."""

    id: UUID
    check_number: int
    name: Optional[str] = None
    status: CheckStatusEnum
    scope: CheckScopeEnum
    entity_type: str
    progress: float
    records_checked: int
    records_valid: int
    records_invalid: int
    records_fixed: int
    issues_found: int
    issues_critical: int
    issues_high: int
    overall_score: Optional[float] = None
    completeness_score: Optional[float] = None
    accuracy_score: Optional[float] = None
    consistency_score: Optional[float] = None
    validity_score: Optional[float] = None
    uniqueness_score: Optional[float] = None
    pass_rate: float
    duration_ms: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DataQualityCheckSummary(BaseModel):
    """Schema resumido de verificação."""

    id: UUID
    status: CheckStatusEnum
    overall_score: Optional[float] = None
    issues_found: int
    pass_rate: float
    duration_ms: int

    class Config:
        from_attributes = True


# ============================================================
# Issue Schemas
# ============================================================

class DataQualityIssueCreate(BaseModel):
    """Schema para criar issue manualmente."""

    issue_type: IssueTypeEnum
    severity: IssueSeverityEnum = IssueSeverityEnum.MEDIUM
    entity_type: str = Field(..., min_length=1, max_length=100)
    entity_id: Optional[UUID] = None
    field_name: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    current_value: Optional[str] = None
    expected_value: Optional[str] = None
    suggested_value: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class DataQualityIssueUpdate(BaseModel):
    """Schema para atualizar issue."""

    status: Optional[IssueStatusEnum] = None
    severity: Optional[IssueSeverityEnum] = None
    assigned_to: Optional[UUID] = None
    resolution_notes: Optional[str] = None
    tags: Optional[List[str]] = None


class DataQualityIssueResponse(BaseModel):
    """Schema de resposta para issue."""

    id: UUID
    issue_code: str
    issue_type: IssueTypeEnum
    severity: IssueSeverityEnum
    status: IssueStatusEnum
    entity_type: str
    entity_id: Optional[UUID] = None
    field_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    current_value: Optional[str] = None
    suggested_value: Optional[str] = None
    can_auto_fix: bool
    occurrence_count: int
    is_open: bool
    is_resolved: bool
    assigned_to: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class IssueResolutionRequest(BaseModel):
    """Schema para resolver issue."""

    resolution_type: str = Field(..., pattern="^(fixed|ignored|false_positive|wont_fix)$")
    notes: Optional[str] = None


class IssueBulkUpdateRequest(BaseModel):
    """Schema para atualização em lote."""

    issue_ids: List[UUID] = Field(..., min_items=1)
    status: Optional[IssueStatusEnum] = None
    assigned_to: Optional[UUID] = None
    severity: Optional[IssueSeverityEnum] = None


# ============================================================
# Duplicate Schemas
# ============================================================

class DuplicateSearchRequest(BaseModel):
    """Schema para buscar duplicatas."""

    entity_type: str = Field(..., min_length=1, max_length=100)
    fields: List[str] = Field(..., min_items=1)
    threshold: float = Field(default=80.0, ge=50, le=100)
    limit: int = Field(default=100, ge=1, le=1000)
    entity_ids: Optional[List[UUID]] = None


class DuplicateRecordResponse(BaseModel):
    """Schema de resposta para duplicata."""

    id: UUID
    group_id: UUID
    status: DuplicateStatusEnum
    duplicate_type: DuplicateTypeEnum
    entity_type: str
    record_ids: List[str]
    record_count: int
    master_record_id: Optional[UUID] = None
    similarity_score: float
    confidence_score: float
    matching_fields: List[str]
    conflicting_fields: List[str]
    can_auto_merge: bool
    is_pending: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DuplicateMergeRequest(BaseModel):
    """Schema para merge de duplicatas."""

    master_record_id: UUID
    strategy: MergeStrategyEnum = MergeStrategyEnum.KEEP_MOST_COMPLETE
    field_resolutions: Dict[str, str] = Field(default_factory=dict)


class DuplicateRejectRequest(BaseModel):
    """Schema para rejeitar duplicata."""

    reason: str = Field(..., min_length=1, max_length=255)


# ============================================================
# Profile Schemas
# ============================================================

class DataProfileRequest(BaseModel):
    """Schema para solicitar profiling."""

    entity_type: str = Field(..., min_length=1, max_length=100)
    field_name: Optional[str] = None
    sample_size: Optional[int] = Field(default=None, ge=100)


class DataProfileResponse(BaseModel):
    """Schema de resposta para perfil."""

    id: UUID
    profile_code: str
    status: ProfileStatusEnum
    entity_type: str
    field_name: Optional[str] = None
    detected_type: Optional[DataTypeEnum] = None
    total_records: int
    null_count: int
    null_percentage: float
    distinct_count: int
    distinct_percentage: float
    completeness_score: Optional[float] = None
    quality_score: Optional[float] = None
    outlier_count: int
    has_quality_issues: bool
    is_outdated: bool
    duration_ms: int
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DataProfileStats(BaseModel):
    """Schema de estatísticas do perfil."""

    total_records: int
    null_count: int
    null_percentage: float
    distinct_count: int
    distinct_percentage: float
    duplicate_count: int
    # Numéricas
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_deviation: Optional[float] = None
    percentiles: Dict[str, float] = Field(default_factory=dict)
    # String
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None
    common_patterns: List[str] = Field(default_factory=list)
    # Distribuição
    value_distribution: Dict[str, int] = Field(default_factory=dict)


# ============================================================
# Dashboard/Analytics Schemas
# ============================================================

class DataQualityDashboard(BaseModel):
    """Schema do dashboard de qualidade."""

    overall_score: float
    total_records: int
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_type: Dict[str, int]
    top_problematic_fields: List[Dict[str, Any]]
    quality_trend: List[Dict[str, Any]]
    recent_checks: List[DataQualityCheckSummary]
    duplicate_groups_pending: int
    profiles_outdated: int


class QualityScoreByEntity(BaseModel):
    """Schema de score por entidade."""

    entity_type: str
    total_records: int
    overall_score: float
    completeness_score: float
    validity_score: float
    issues_count: int
    last_check_at: Optional[datetime] = None


class ValidationRequest(BaseModel):
    """Schema para validação de dados."""

    entity_type: str = Field(..., min_length=1, max_length=100)
    data: Dict[str, Any] = Field(..., min_items=1)
    rule_ids: Optional[List[UUID]] = None
    auto_fix: bool = False


class ValidationResponse(BaseModel):
    """Schema de resposta de validação."""

    is_valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    fixed_data: Optional[Dict[str, Any]] = None
    fixes_applied: int = 0


class CleansingRequest(BaseModel):
    """Schema para limpeza de dados."""

    entity_type: str = Field(..., min_length=1, max_length=100)
    data: Dict[str, Any] = Field(..., min_items=1)
    operations: List[str] = Field(default_factory=list)


class CleansingResponse(BaseModel):
    """Schema de resposta de limpeza."""

    original_data: Dict[str, Any]
    cleaned_data: Dict[str, Any]
    changes: List[Dict[str, Any]]
    changes_count: int
