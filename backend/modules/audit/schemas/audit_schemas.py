"""
Schemas Pydantic para Auditoria e Compliance
Sprint 33: Auditoria e Compliance
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ==================== AuditLog Schemas ====================

class AuditLogCreate(BaseModel):
    """Schema para criar log de auditoria."""
    action: str
    category: str
    description: str
    severity: str = "info"
    result: str = "success"
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class AuditLogResponse(BaseModel):
    """Schema de resposta para log de auditoria."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_id: str
    correlation_id: Optional[str] = None
    action: str
    category: str
    severity: str
    result: str
    description: str
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    entity_name: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changed_fields: Optional[List[str]] = None
    ip_address: Optional[str] = None
    geo_country: Optional[str] = None
    geo_city: Optional[str] = None
    is_sensitive: bool = False
    is_pii: bool = False
    requires_review: bool = False
    created_at: datetime


class AuditLogList(BaseModel):
    """Lista paginada de logs de auditoria."""
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AuditLogFilter(BaseModel):
    """Filtros para busca de logs."""
    action: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    result: Optional[str] = None
    user_id: Optional[UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    requires_review: Optional[bool] = None
    search: Optional[str] = None


class AuditLogStats(BaseModel):
    """Estatísticas de logs de auditoria."""
    total_events: int = 0
    events_today: int = 0
    events_this_week: int = 0
    by_category: Dict[str, int] = Field(default_factory=dict)
    by_severity: Dict[str, int] = Field(default_factory=dict)
    by_result: Dict[str, int] = Field(default_factory=dict)
    top_users: List[Dict[str, Any]] = Field(default_factory=list)
    top_entities: List[Dict[str, Any]] = Field(default_factory=list)
    pending_reviews: int = 0


# ==================== ComplianceRule Schemas ====================

class ComplianceRuleCreate(BaseModel):
    """Schema para criar regra de compliance."""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    framework: str
    framework_reference: Optional[str] = None
    category: str
    severity: str = "medium"
    requirement_text: str
    implementation_guidance: Optional[str] = None
    evidence_required: Optional[List[str]] = None
    validation_query: Optional[str] = None
    validation_frequency_hours: Optional[int] = 24
    auto_validate: bool = True
    applies_to_entities: Optional[List[str]] = None
    applies_to_roles: Optional[List[str]] = None
    notify_on_violation: bool = True
    notification_recipients: Optional[List[str]] = None
    remediation_steps: Optional[List[str]] = None
    remediation_deadline_days: Optional[int] = None
    documentation_url: Optional[str] = None
    tags: Optional[List[str]] = None


class ComplianceRuleUpdate(BaseModel):
    """Schema para atualizar regra de compliance."""
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    requirement_text: Optional[str] = None
    implementation_guidance: Optional[str] = None
    evidence_required: Optional[List[str]] = None
    validation_query: Optional[str] = None
    validation_frequency_hours: Optional[int] = None
    auto_validate: Optional[bool] = None
    applies_to_entities: Optional[List[str]] = None
    notify_on_violation: Optional[bool] = None
    notification_recipients: Optional[List[str]] = None
    remediation_steps: Optional[List[str]] = None
    remediation_deadline_days: Optional[int] = None
    documentation_url: Optional[str] = None
    tags: Optional[List[str]] = None


class ComplianceRuleResponse(BaseModel):
    """Schema de resposta para regra de compliance."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: Optional[str] = None
    version: str
    framework: str
    framework_reference: Optional[str] = None
    category: str
    status: str
    severity: str
    requirement_text: str
    implementation_guidance: Optional[str] = None
    auto_validate: bool
    validation_frequency_hours: Optional[int] = None
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    compliance_rate: float = 100.0
    last_check_at: Optional[datetime] = None
    last_violation_at: Optional[datetime] = None
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None
    is_effective: bool = True
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    ativo: bool = True
    created_at: datetime
    updated_at: datetime


class ComplianceRuleList(BaseModel):
    """Lista paginada de regras de compliance."""
    items: List[ComplianceRuleResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ==================== ComplianceCheck Schemas ====================

class ComplianceCheckCreate(BaseModel):
    """Schema para criar verificação de compliance."""
    rule_id: UUID
    check_type: str = "automated"
    scope_description: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class ComplianceCheckUpdate(BaseModel):
    """Schema para atualizar verificação de compliance."""
    status: Optional[str] = None
    result: Optional[str] = None
    analysis_notes: Optional[str] = None
    remediation_plan: Optional[List[Dict[str, Any]]] = None
    remediation_deadline: Optional[datetime] = None
    exception_reason: Optional[str] = None


class ComplianceCheckResponse(BaseModel):
    """Schema de resposta para verificação de compliance."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    rule_id: UUID
    check_number: str
    check_type: str
    status: str
    result: Optional[str] = None
    scope_description: Optional[str] = None
    entities_checked: Optional[int] = None
    entities_compliant: Optional[int] = None
    entities_non_compliant: Optional[int] = None
    compliance_percentage: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    violations_count: int = 0
    critical_violations: int = 0
    remediation_required: bool = False
    remediation_deadline: Optional[datetime] = None
    remediation_status: Optional[str] = None
    exception_granted: bool = False
    requires_review: bool = False
    escalated: bool = False
    error_message: Optional[str] = None
    ativo: bool = True
    created_at: datetime
    updated_at: datetime


class ComplianceCheckList(BaseModel):
    """Lista paginada de verificações de compliance."""
    items: List[ComplianceCheckResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ==================== DataRetention Schemas ====================

class DataRetentionCreate(BaseModel):
    """Schema para criar política de retenção."""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    data_category: str
    retention_period: str
    retention_days: Optional[int] = None
    expiration_action: str = "delete"
    secondary_action: Optional[str] = None
    entity_types: Optional[List[str]] = None
    table_names: Optional[List[str]] = None
    compliance_framework: Optional[str] = None
    compliance_reference: Optional[str] = None
    legal_basis: Optional[str] = None
    anonymize_fields: Optional[List[str]] = None
    archive_location: Optional[str] = None
    notify_before_days: Optional[int] = 7
    notify_recipients: Optional[List[str]] = None
    schedule_cron: Optional[str] = None
    tags: Optional[List[str]] = None


class DataRetentionUpdate(BaseModel):
    """Schema para atualizar política de retenção."""
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    status: Optional[str] = None
    retention_period: Optional[str] = None
    retention_days: Optional[int] = None
    expiration_action: Optional[str] = None
    entity_types: Optional[List[str]] = None
    anonymize_fields: Optional[List[str]] = None
    archive_location: Optional[str] = None
    notify_before_days: Optional[int] = None
    notify_recipients: Optional[List[str]] = None
    schedule_enabled: Optional[bool] = None
    schedule_cron: Optional[str] = None
    tags: Optional[List[str]] = None


class DataRetentionResponse(BaseModel):
    """Schema de resposta para política de retenção."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: Optional[str] = None
    version: str
    data_category: str
    status: str
    retention_period: str
    retention_days: Optional[int] = None
    expiration_action: str
    secondary_action: Optional[str] = None
    entity_types: Optional[List[str]] = None
    table_names: Optional[List[str]] = None
    compliance_framework: Optional[str] = None
    legal_hold_enabled: bool = False
    schedule_enabled: bool = True
    last_execution_at: Optional[datetime] = None
    next_execution_at: Optional[datetime] = None
    total_executions: int = 0
    records_processed: int = 0
    records_deleted: int = 0
    records_archived: int = 0
    records_anonymized: int = 0
    storage_freed_bytes: int = 0
    consecutive_errors: int = 0
    is_effective: bool = True
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    ativo: bool = True
    created_at: datetime
    updated_at: datetime


class DataRetentionList(BaseModel):
    """Lista paginada de políticas de retenção."""
    items: List[DataRetentionResponse]
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
    error_message: Optional[str] = None


# ==================== AccessHistory Schemas ====================

class AccessHistoryCreate(BaseModel):
    """Schema para criar registro de acesso."""
    access_type: str
    result: str
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    resource_path: Optional[str] = None
    http_method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    auth_method: Optional[str] = None
    mfa_used: bool = False
    device_fingerprint: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AccessHistoryResponse(BaseModel):
    """Schema de resposta para registro de acesso."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: Optional[str] = None
    access_type: str
    result: str
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    user_role: Optional[str] = None
    auth_method: Optional[str] = None
    mfa_used: bool = False
    resource_path: Optional[str] = None
    http_method: Optional[str] = None
    ip_address: Optional[str] = None
    geo_country: Optional[str] = None
    geo_city: Optional[str] = None
    device_type: Optional[str] = None
    browser_name: Optional[str] = None
    os_name: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None
    anomaly_detected: bool = False
    alert_triggered: bool = False
    requires_review: bool = False
    failure_reason: Optional[str] = None
    response_time_ms: Optional[int] = None
    accessed_at: datetime


class AccessHistoryList(BaseModel):
    """Lista paginada de registros de acesso."""
    items: List[AccessHistoryResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AccessHistoryFilter(BaseModel):
    """Filtros para busca de acessos."""
    access_type: Optional[str] = None
    result: Optional[str] = None
    user_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    geo_country: Optional[str] = None
    device_type: Optional[str] = None
    risk_level: Optional[str] = None
    anomaly_detected: Optional[bool] = None
    requires_review: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None


class AccessHistoryStats(BaseModel):
    """Estatísticas de acessos."""
    total_accesses: int = 0
    successful_logins: int = 0
    failed_logins: int = 0
    unique_users: int = 0
    unique_ips: int = 0
    by_access_type: Dict[str, int] = Field(default_factory=dict)
    by_result: Dict[str, int] = Field(default_factory=dict)
    by_country: Dict[str, int] = Field(default_factory=dict)
    by_device_type: Dict[str, int] = Field(default_factory=dict)
    high_risk_accesses: int = 0
    anomalies_detected: int = 0
    pending_reviews: int = 0


# ==================== Dashboard Schemas ====================

class AuditDashboard(BaseModel):
    """Dashboard de auditoria."""
    audit_stats: AuditLogStats
    access_stats: AccessHistoryStats
    recent_events: List[AuditLogResponse] = Field(default_factory=list)
    recent_accesses: List[AccessHistoryResponse] = Field(default_factory=list)
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    trends: Dict[str, Any] = Field(default_factory=dict)


class ComplianceOverview(BaseModel):
    """Visão geral de compliance."""
    total_rules: int = 0
    active_rules: int = 0
    rules_by_framework: Dict[str, int] = Field(default_factory=dict)
    rules_by_status: Dict[str, int] = Field(default_factory=dict)
    overall_compliance_rate: float = 100.0
    compliance_by_framework: Dict[str, float] = Field(default_factory=dict)
    total_checks: int = 0
    checks_this_month: int = 0
    pending_remediations: int = 0
    overdue_remediations: int = 0
    critical_violations: int = 0
    upcoming_checks: List[Dict[str, Any]] = Field(default_factory=list)
    recent_violations: List[Dict[str, Any]] = Field(default_factory=list)


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
    top_risk_users: List[Dict[str, Any]] = Field(default_factory=list)
    top_risk_ips: List[Dict[str, Any]] = Field(default_factory=list)
    geographic_distribution: Dict[str, int] = Field(default_factory=dict)
    alerts_triggered: int = 0
    pending_investigations: int = 0
