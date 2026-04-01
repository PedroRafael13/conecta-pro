"""
Schemas Pydantic para Auditoria e Compliance
Sprint 33: Auditoria e Compliance
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ==================== AuditLog Schemas ====================


class AuditLogCreate(BaseModel):
    """Schema para criar log de auditoria."""

    action: str
    category: str
    description: str
    severity: str = "info"
    result: str = "success"
    user_id: UUID | None = None
    user_email: str | None = None
    entity_type: str | None = None
    entity_id: UUID | None = None
    old_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict[str, Any] | None = None
    tags: list[str] | None = None


class AuditLogResponse(BaseModel):
    """Schema de resposta para log de auditoria."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_id: str
    correlation_id: str | None = None
    action: str
    category: str
    severity: str
    result: str
    description: str
    user_id: UUID | None = None
    user_email: str | None = None
    user_name: str | None = None
    entity_type: str | None = None
    entity_id: UUID | None = None
    entity_name: str | None = None
    old_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    changed_fields: list[str] | None = None
    ip_address: str | None = None
    geo_country: str | None = None
    geo_city: str | None = None
    is_sensitive: bool = False
    is_pii: bool = False
    requires_review: bool = False
    created_at: datetime


class AuditLogList(BaseModel):
    """Lista paginada de logs de auditoria."""

    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AuditLogFilter(BaseModel):
    """Filtros para busca de logs."""

    action: str | None = None
    category: str | None = None
    severity: str | None = None
    result: str | None = None
    user_id: UUID | None = None
    entity_type: str | None = None
    entity_id: UUID | None = None
    ip_address: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    requires_review: bool | None = None
    search: str | None = None


class AuditLogStats(BaseModel):
    """Estatísticas de logs de auditoria."""

    total_events: int = 0
    events_today: int = 0
    events_this_week: int = 0
    by_category: dict[str, int] = Field(default_factory=dict)
    by_severity: dict[str, int] = Field(default_factory=dict)
    by_result: dict[str, int] = Field(default_factory=dict)
    top_users: list[dict[str, Any]] = Field(default_factory=list)
    top_entities: list[dict[str, Any]] = Field(default_factory=list)
    pending_reviews: int = 0


# ==================== ComplianceRule Schemas ====================


class ComplianceRuleCreate(BaseModel):
    """Schema para criar regra de compliance."""

    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=300)
    description: str | None = None
    framework: str
    framework_reference: str | None = None
    category: str
    severity: str = "medium"
    requirement_text: str
    implementation_guidance: str | None = None
    evidence_required: list[str] | None = None
    validation_query: str | None = None
    validation_frequency_hours: int | None = 24
    auto_validate: bool = True
    applies_to_entities: list[str] | None = None
    applies_to_roles: list[str] | None = None
    notify_on_violation: bool = True
    notification_recipients: list[str] | None = None
    remediation_steps: list[str] | None = None
    remediation_deadline_days: int | None = None
    documentation_url: str | None = None
    tags: list[str] | None = None


class ComplianceRuleUpdate(BaseModel):
    """Schema para atualizar regra de compliance."""

    name: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = None
    status: str | None = None
    severity: str | None = None
    requirement_text: str | None = None
    implementation_guidance: str | None = None
    evidence_required: list[str] | None = None
    validation_query: str | None = None
    validation_frequency_hours: int | None = None
    auto_validate: bool | None = None
    applies_to_entities: list[str] | None = None
    notify_on_violation: bool | None = None
    notification_recipients: list[str] | None = None
    remediation_steps: list[str] | None = None
    remediation_deadline_days: int | None = None
    documentation_url: str | None = None
    tags: list[str] | None = None


class ComplianceRuleResponse(BaseModel):
    """Schema de resposta para regra de compliance."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: str | None = None
    version: str
    framework: str
    framework_reference: str | None = None
    category: str
    status: str
    severity: str
    requirement_text: str
    implementation_guidance: str | None = None
    auto_validate: bool
    validation_frequency_hours: int | None = None
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    compliance_rate: float = 100.0
    last_check_at: datetime | None = None
    last_violation_at: datetime | None = None
    effective_from: datetime | None = None
    effective_until: datetime | None = None
    is_effective: bool = True
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    ativo: bool = True
    created_at: datetime
    updated_at: datetime


class ComplianceRuleList(BaseModel):
    """Lista paginada de regras de compliance."""

    items: list[ComplianceRuleResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ==================== ComplianceCheck Schemas ====================


class ComplianceCheckCreate(BaseModel):
    """Schema para criar verificação de compliance."""

    rule_id: UUID
    check_type: str = "automated"
    scope_description: str | None = None
    scheduled_at: datetime | None = None


class ComplianceCheckUpdate(BaseModel):
    """Schema para atualizar verificação de compliance."""

    status: str | None = None
    result: str | None = None
    analysis_notes: str | None = None
    remediation_plan: list[dict[str, Any]] | None = None
    remediation_deadline: datetime | None = None
    exception_reason: str | None = None


class ComplianceCheckResponse(BaseModel):
    """Schema de resposta para verificação de compliance."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    rule_id: UUID
    check_number: str
    check_type: str
    status: str
    result: str | None = None
    scope_description: str | None = None
    entities_checked: int | None = None
    entities_compliant: int | None = None
    entities_non_compliant: int | None = None
    compliance_percentage: float | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: int | None = None
    violations_count: int = 0
    critical_violations: int = 0
    remediation_required: bool = False
    remediation_deadline: datetime | None = None
    remediation_status: str | None = None
    exception_granted: bool = False
    requires_review: bool = False
    escalated: bool = False
    error_message: str | None = None
    ativo: bool = True
    created_at: datetime
    updated_at: datetime


class ComplianceCheckList(BaseModel):
    """Lista paginada de verificações de compliance."""

    items: list[ComplianceCheckResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ==================== DataRetention Schemas ====================


class DataRetentionCreate(BaseModel):
    """Schema para criar política de retenção."""

    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=300)
    description: str | None = None
    data_category: str
    retention_period: str
    retention_days: int | None = None
    expiration_action: str = "delete"
    secondary_action: str | None = None
    entity_types: list[str] | None = None
    table_names: list[str] | None = None
    compliance_framework: str | None = None
    compliance_reference: str | None = None
    legal_basis: str | None = None
    anonymize_fields: list[str] | None = None
    archive_location: str | None = None
    notify_before_days: int | None = 7
    notify_recipients: list[str] | None = None
    schedule_cron: str | None = None
    tags: list[str] | None = None


class DataRetentionUpdate(BaseModel):
    """Schema para atualizar política de retenção."""

    name: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = None
    status: str | None = None
    retention_period: str | None = None
    retention_days: int | None = None
    expiration_action: str | None = None
    entity_types: list[str] | None = None
    anonymize_fields: list[str] | None = None
    archive_location: str | None = None
    notify_before_days: int | None = None
    notify_recipients: list[str] | None = None
    schedule_enabled: bool | None = None
    schedule_cron: str | None = None
    tags: list[str] | None = None


class DataRetentionResponse(BaseModel):
    """Schema de resposta para política de retenção."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: str | None = None
    version: str
    data_category: str
    status: str
    retention_period: str
    retention_days: int | None = None
    expiration_action: str
    secondary_action: str | None = None
    entity_types: list[str] | None = None
    table_names: list[str] | None = None
    compliance_framework: str | None = None
    legal_hold_enabled: bool = False
    schedule_enabled: bool = True
    last_execution_at: datetime | None = None
    next_execution_at: datetime | None = None
    total_executions: int = 0
    records_processed: int = 0
    records_deleted: int = 0
    records_archived: int = 0
    records_anonymized: int = 0
    storage_freed_bytes: int = 0
    consecutive_errors: int = 0
    is_effective: bool = True
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    ativo: bool = True
    created_at: datetime
    updated_at: datetime


class DataRetentionList(BaseModel):
    """Lista paginada de políticas de retenção."""

    items: list[DataRetentionResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DataRetentionExecution(BaseModel):
    """Resultado de execução de política de retenção."""

    policy_id: UUID
    policy_code: str
    execution_at: datetime
    records_affected: int
    records_deleted: int = 0
    records_archived: int = 0
    records_anonymized: int = 0
    storage_freed_bytes: int = 0
    duration_seconds: int
    success: bool
    error_message: str | None = None


# ==================== AccessHistory Schemas ====================


class AccessHistoryCreate(BaseModel):
    """Schema para criar registro de acesso."""

    access_type: str
    result: str
    user_id: UUID | None = None
    user_email: str | None = None
    resource_path: str | None = None
    http_method: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    session_id: str | None = None
    auth_method: str | None = None
    mfa_used: bool = False
    device_fingerprint: str | None = None
    metadata: dict[str, Any] | None = None


class AccessHistoryResponse(BaseModel):
    """Schema de resposta para registro de acesso."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: str | None = None
    access_type: str
    result: str
    user_id: UUID | None = None
    user_email: str | None = None
    user_name: str | None = None
    user_role: str | None = None
    auth_method: str | None = None
    mfa_used: bool = False
    resource_path: str | None = None
    http_method: str | None = None
    ip_address: str | None = None
    geo_country: str | None = None
    geo_city: str | None = None
    device_type: str | None = None
    browser_name: str | None = None
    os_name: str | None = None
    risk_level: str | None = None
    risk_score: int | None = None
    anomaly_detected: bool = False
    alert_triggered: bool = False
    requires_review: bool = False
    failure_reason: str | None = None
    response_time_ms: int | None = None
    accessed_at: datetime


class AccessHistoryList(BaseModel):
    """Lista paginada de registros de acesso."""

    items: list[AccessHistoryResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AccessHistoryFilter(BaseModel):
    """Filtros para busca de acessos."""

    access_type: str | None = None
    result: str | None = None
    user_id: UUID | None = None
    ip_address: str | None = None
    geo_country: str | None = None
    device_type: str | None = None
    risk_level: str | None = None
    anomaly_detected: bool | None = None
    requires_review: bool | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    search: str | None = None


class AccessHistoryStats(BaseModel):
    """Estatísticas de acessos."""

    total_accesses: int = 0
    successful_logins: int = 0
    failed_logins: int = 0
    unique_users: int = 0
    unique_ips: int = 0
    by_access_type: dict[str, int] = Field(default_factory=dict)
    by_result: dict[str, int] = Field(default_factory=dict)
    by_country: dict[str, int] = Field(default_factory=dict)
    by_device_type: dict[str, int] = Field(default_factory=dict)
    high_risk_accesses: int = 0
    anomalies_detected: int = 0
    pending_reviews: int = 0


# ==================== Dashboard Schemas ====================


class AuditDashboard(BaseModel):
    """Dashboard de auditoria."""

    audit_stats: AuditLogStats
    access_stats: AccessHistoryStats
    recent_events: list[AuditLogResponse] = Field(default_factory=list)
    recent_accesses: list[AccessHistoryResponse] = Field(default_factory=list)
    alerts: list[dict[str, Any]] = Field(default_factory=list)
    trends: dict[str, Any] = Field(default_factory=dict)


class ComplianceOverview(BaseModel):
    """Visão geral de compliance."""

    total_rules: int = 0
    active_rules: int = 0
    rules_by_framework: dict[str, int] = Field(default_factory=dict)
    rules_by_status: dict[str, int] = Field(default_factory=dict)
    overall_compliance_rate: float = 100.0
    compliance_by_framework: dict[str, float] = Field(default_factory=dict)
    total_checks: int = 0
    checks_this_month: int = 0
    pending_remediations: int = 0
    overdue_remediations: int = 0
    critical_violations: int = 0
    upcoming_checks: list[dict[str, Any]] = Field(default_factory=list)
    recent_violations: list[dict[str, Any]] = Field(default_factory=list)


class SecurityOverview(BaseModel):
    """Visão geral de segurança."""

    total_accesses_today: int = 0
    failed_logins_today: int = 0
    blocked_accesses: int = 0
    suspicious_activities: int = 0
    high_risk_sessions: int = 0
    new_devices_detected: int = 0
    new_locations_detected: int = 0
    mfa_adoption_rate: float = 0.0
    top_risk_users: list[dict[str, Any]] = Field(default_factory=list)
    top_risk_ips: list[dict[str, Any]] = Field(default_factory=list)
    geographic_distribution: dict[str, int] = Field(default_factory=dict)
    alerts_triggered: int = 0
    pending_investigations: int = 0
