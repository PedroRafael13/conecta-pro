"""
Data Quality Schemas - Sprint 48.

Schemas Pydantic para validação de dados na API.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.ai.data_quality.models import (
    CheckScopeEnum,
    CheckStatusEnum,
    DataTypeEnum,
    DuplicateStatusEnum,
    DuplicateTypeEnum,
    IssueSeverityEnum,
    IssueStatusEnum,
    IssueTypeEnum,
    MergeStrategyEnum,
    ProfileStatusEnum,
    RuleCategoryEnum,
    RuleSeverityEnum,
    RuleStatusEnum,
    RuleTypeEnum,
)

# ============================================================
# Rule Schemas
# ============================================================


class DataQualityRuleBase(BaseModel):
    """Schema base para regra de qualidade."""

    code: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    rule_type: RuleTypeEnum
    category: RuleCategoryEnum = RuleCategoryEnum.VALIDITY
    severity: RuleSeverityEnum = RuleSeverityEnum.MEDIUM
    entity_type: str = Field(..., min_length=1, max_length=100)
    field_name: str | None = None

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

    condition: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    threshold: float | None = None
    regex_pattern: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    allowed_values: list[str] = Field(default_factory=list)
    action_on_violation: str = "flag"
    auto_fix_enabled: bool = False
    fix_function: str | None = None
    error_message: str | None = None
    priority: int = Field(default=50, ge=1, le=100)
    tags: list[str] = Field(default_factory=list)


class DataQualityRuleUpdate(BaseModel):
    """Schema para atualizar regra."""

    name: str | None = None
    description: str | None = None
    category: RuleCategoryEnum | None = None
    severity: RuleSeverityEnum | None = None
    status: RuleStatusEnum | None = None
    condition: str | None = None
    parameters: dict[str, Any] | None = None
    threshold: float | None = None
    auto_fix_enabled: bool | None = None
    error_message: str | None = None
    priority: int | None = Field(default=None, ge=1, le=100)
    is_active: bool | None = None


class DataQualityRuleResponse(DataQualityRuleBase):
    """Schema de resposta para regra."""

    id: UUID
    status: RuleStatusEnum
    total_checks: int
    total_violations: int
    violation_rate: float
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


# ============================================================
# Check Schemas
# ============================================================


class DataQualityCheckCreate(BaseModel):
    """Schema para criar verificação."""

    name: str | None = None
    entity_type: str = Field(..., min_length=1, max_length=100)
    scope: CheckScopeEnum = CheckScopeEnum.FULL
    entity_ids: list[UUID] = Field(default_factory=list)
    rule_ids: list[UUID] = Field(default_factory=list)
    sample_size: int | None = Field(default=None, ge=1)
    sample_percentage: float | None = Field(default=None, ge=0.1, le=100)
    auto_fix_enabled: bool = False
    parameters: dict[str, Any] = Field(default_factory=dict)


class DataQualityCheckResponse(BaseModel):
    """Schema de resposta para verificação."""

    id: UUID
    check_number: int
    name: str | None = None
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
    overall_score: float | None = None
    completeness_score: float | None = None
    accuracy_score: float | None = None
    consistency_score: float | None = None
    validity_score: float | None = None
    uniqueness_score: float | None = None
    pass_rate: float
    duration_ms: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class DataQualityCheckSummary(BaseModel):
    """Schema resumido de verificação."""

    id: UUID
    status: CheckStatusEnum
    overall_score: float | None = None
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
    entity_id: UUID | None = None
    field_name: str | None = None
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    current_value: str | None = None
    expected_value: str | None = None
    suggested_value: str | None = None
    tags: list[str] = Field(default_factory=list)


class DataQualityIssueUpdate(BaseModel):
    """Schema para atualizar issue."""

    status: IssueStatusEnum | None = None
    severity: IssueSeverityEnum | None = None
    assigned_to: UUID | None = None
    resolution_notes: str | None = None
    tags: list[str] | None = None


class DataQualityIssueResponse(BaseModel):
    """Schema de resposta para issue."""

    id: UUID
    issue_code: str
    issue_type: IssueTypeEnum
    severity: IssueSeverityEnum
    status: IssueStatusEnum
    entity_type: str
    entity_id: UUID | None = None
    field_name: str | None = None
    title: str
    description: str | None = None
    current_value: str | None = None
    suggested_value: str | None = None
    can_auto_fix: bool
    occurrence_count: int
    is_open: bool
    is_resolved: bool
    assigned_to: UUID | None = None
    resolved_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class IssueResolutionRequest(BaseModel):
    """Schema para resolver issue."""

    resolution_type: str = Field(..., pattern="^(fixed|ignored|false_positive|wont_fix)$")
    notes: str | None = None


class IssueBulkUpdateRequest(BaseModel):
    """Schema para atualização em lote."""

    issue_ids: list[UUID] = Field(..., min_items=1)
    status: IssueStatusEnum | None = None
    assigned_to: UUID | None = None
    severity: IssueSeverityEnum | None = None


# ============================================================
# Duplicate Schemas
# ============================================================


class DuplicateSearchRequest(BaseModel):
    """Schema para buscar duplicatas."""

    entity_type: str = Field(..., min_length=1, max_length=100)
    fields: list[str] = Field(..., min_items=1)
    threshold: float = Field(default=80.0, ge=50, le=100)
    limit: int = Field(default=100, ge=1, le=1000)
    entity_ids: list[UUID] | None = None


class DuplicateRecordResponse(BaseModel):
    """Schema de resposta para duplicata."""

    id: UUID
    group_id: UUID
    status: DuplicateStatusEnum
    duplicate_type: DuplicateTypeEnum
    entity_type: str
    record_ids: list[str]
    record_count: int
    master_record_id: UUID | None = None
    similarity_score: float
    confidence_score: float
    matching_fields: list[str]
    conflicting_fields: list[str]
    can_auto_merge: bool
    is_pending: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DuplicateMergeRequest(BaseModel):
    """Schema para merge de duplicatas."""

    master_record_id: UUID
    strategy: MergeStrategyEnum = MergeStrategyEnum.KEEP_MOST_COMPLETE
    field_resolutions: dict[str, str] = Field(default_factory=dict)


class DuplicateRejectRequest(BaseModel):
    """Schema para rejeitar duplicata."""

    reason: str = Field(..., min_length=1, max_length=255)


# ============================================================
# Profile Schemas
# ============================================================


class DataProfileRequest(BaseModel):
    """Schema para solicitar profiling."""

    entity_type: str = Field(..., min_length=1, max_length=100)
    field_name: str | None = None
    sample_size: int | None = Field(default=None, ge=100)


class DataProfileResponse(BaseModel):
    """Schema de resposta para perfil."""

    id: UUID
    profile_code: str
    status: ProfileStatusEnum
    entity_type: str
    field_name: str | None = None
    detected_type: DataTypeEnum | None = None
    total_records: int
    null_count: int
    null_percentage: float
    distinct_count: int
    distinct_percentage: float
    completeness_score: float | None = None
    quality_score: float | None = None
    outlier_count: int
    has_quality_issues: bool
    is_outdated: bool
    duration_ms: int
    completed_at: datetime | None = None
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
    min_value: float | None = None
    max_value: float | None = None
    mean_value: float | None = None
    median_value: float | None = None
    std_deviation: float | None = None
    percentiles: dict[str, float] = Field(default_factory=dict)
    # String
    min_length: int | None = None
    max_length: int | None = None
    avg_length: float | None = None
    common_patterns: list[str] = Field(default_factory=list)
    # Distribuição
    value_distribution: dict[str, int] = Field(default_factory=dict)


# ============================================================
# Dashboard/Analytics Schemas
# ============================================================


class DataQualityDashboard(BaseModel):
    """Schema do dashboard de qualidade."""

    overall_score: float
    total_records: int
    total_issues: int
    issues_by_severity: dict[str, int]
    issues_by_type: dict[str, int]
    top_problematic_fields: list[dict[str, Any]]
    quality_trend: list[dict[str, Any]]
    recent_checks: list[DataQualityCheckSummary]
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
    last_check_at: datetime | None = None


class ValidationRequest(BaseModel):
    """Schema para validação de dados."""

    entity_type: str = Field(..., min_length=1, max_length=100)
    data: dict[str, Any] = Field(..., min_items=1)
    rule_ids: list[UUID] | None = None
    auto_fix: bool = False


class ValidationResponse(BaseModel):
    """Schema de resposta de validação."""

    is_valid: bool
    errors: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    fixed_data: dict[str, Any] | None = None
    fixes_applied: int = 0


class CleansingRequest(BaseModel):
    """Schema para limpeza de dados."""

    entity_type: str = Field(..., min_length=1, max_length=100)
    data: dict[str, Any] = Field(..., min_items=1)
    operations: list[str] = Field(default_factory=list)


class CleansingResponse(BaseModel):
    """Schema de resposta de limpeza."""

    original_data: dict[str, Any]
    cleaned_data: dict[str, Any]
    changes: list[dict[str, Any]]
    changes_count: int
