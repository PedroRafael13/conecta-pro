"""
Contract Schemas - AI Contract Analysis

DTOs para entrada e saida da API de analise de contratos.
"""

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.ai.contract_analysis.models.contract_analysis import (
    AnalysisStatus,
    ContractType,
    RiskLevel,
)
from modules.ai.contract_analysis.models.extracted_clause import (
    ClauseType,
    ClauseImportance,
)
from modules.ai.contract_analysis.models.contract_alert import (
    AlertType,
    AlertStatus,
    AlertPriority,
)


# ============================================================
# Analysis Schemas
# ============================================================


class ContractAnalysisRequest(BaseModel):
    """Request para analisar contrato."""

    contract_id: UUID = Field(..., description="ID do contrato")
    document_id: Optional[UUID] = Field(None, description="ID do documento no GED")
    document_content: Optional[str] = Field(None, description="Conteudo do documento")
    contract_number: Optional[str] = Field(None, max_length=50)
    contract_title: Optional[str] = Field(None, max_length=300)
    template_id: Optional[UUID] = Field(None, description="Template para comparacao")
    extract_clauses: bool = Field(default=True, description="Extrair clausulas")
    analyze_risk: bool = Field(default=True, description="Analisar riscos")
    check_compliance: bool = Field(default=True, description="Verificar conformidade")
    generate_alerts: bool = Field(default=True, description="Gerar alertas")


class ExtractedClauseResponse(BaseModel):
    """Response para clausula extraida."""

    id: UUID
    analysis_id: UUID
    clause_number: Optional[str] = None
    clause_title: Optional[str] = None
    clause_type: ClauseType
    clause_type_confidence: float = 0
    original_text: str
    normalized_text: Optional[str] = None
    summary: Optional[str] = None
    page_number: Optional[int] = None
    importance: ClauseImportance
    is_standard: bool = True
    is_custom: bool = False
    is_risky: bool = False
    entities: Optional[list[dict]] = None
    dates_found: Optional[list[dict]] = None
    values_found: Optional[list[dict]] = None
    risk_score: float = 0
    risk_reasons: Optional[list[str]] = None
    obligations: Optional[list[dict]] = None
    has_deadline: bool = False
    has_monetary_value: bool = False
    requires_action: bool = False
    manually_reviewed: bool = False
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ContractAlertResponse(BaseModel):
    """Response para alerta de contrato."""

    id: UUID
    analysis_id: UUID
    contract_id: UUID
    contract_number: Optional[str] = None
    alert_type: AlertType
    status: AlertStatus
    priority: AlertPriority
    title: str
    description: Optional[str] = None
    recommendation: Optional[str] = None
    trigger_date: date
    due_date: Optional[date] = None
    reference_date: Optional[date] = None
    days_before: int = 30
    days_remaining: Optional[int] = None
    clause_id: Optional[UUID] = None
    clause_number: Optional[str] = None
    monetary_value: Optional[str] = None
    assigned_to: Optional[UUID] = None
    notification_sent: bool = False
    confidence: int = 100
    is_active: bool = True
    is_read: bool = False
    is_overdue: bool = False
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class ContractAnalysisResponse(BaseModel):
    """Response para analise de contrato."""

    id: UUID
    contract_id: UUID
    contract_number: Optional[str] = None
    contract_title: Optional[str] = None
    document_id: Optional[UUID] = None
    document_name: Optional[str] = None
    status: AnalysisStatus
    contract_type: ContractType
    contract_type_confidence: float = 0

    # Partes
    contractor_name: Optional[str] = None
    contractor_document: Optional[str] = None
    contracted_name: Optional[str] = None
    contracted_document: Optional[str] = None

    # Datas
    signature_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    renewal_date: Optional[date] = None
    notice_period_days: Optional[int] = None

    # Valores
    total_value: Optional[float] = None
    monthly_value: Optional[float] = None
    currency: str = "BRL"
    payment_terms: Optional[str] = None
    adjustment_index: Optional[str] = None

    # Risco
    risk_level: RiskLevel
    risk_score: float = 50
    risk_factors: Optional[list[dict]] = None

    # Conformidade
    compliance_score: float = 0
    compliance_issues: Optional[list[dict]] = None
    missing_clauses: Optional[list[str]] = None

    # Estatisticas
    total_pages: int = 0
    total_words: int = 0
    total_clauses_found: int = 0
    processing_time_seconds: Optional[float] = None

    # Resumo
    summary: Optional[str] = None
    key_terms: Optional[list[str]] = None
    obligations_summary: Optional[str] = None

    # Flags
    has_auto_renewal: bool = False
    has_penalty_clause: bool = False
    has_exclusivity: bool = False
    has_confidentiality: bool = False
    has_non_compete: bool = False
    requires_review: bool = False

    # Metadados
    created_at: datetime
    completed_at: Optional[datetime] = None
    is_active: bool = True

    # Relacionamentos (opcionais)
    clauses: Optional[list[ExtractedClauseResponse]] = None
    alerts: Optional[list[ContractAlertResponse]] = None

    # Propriedades calculadas
    days_until_expiry: Optional[int] = None
    is_expiring_soon: bool = False
    is_expired: bool = False

    class Config:
        """Pydantic config."""

        from_attributes = True


class ContractAnalysisListResponse(BaseModel):
    """Response para lista de analises."""

    items: list[ContractAnalysisResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AlertListResponse(BaseModel):
    """Response para lista de alertas."""

    items: list[ContractAlertResponse]
    total: int
    pending_count: int
    urgent_count: int
    overdue_count: int


# ============================================================
# Alert Management Schemas
# ============================================================


class ContractAlertCreate(BaseModel):
    """Schema para criar alerta manualmente."""

    contract_id: UUID
    alert_type: AlertType
    priority: AlertPriority = AlertPriority.MEDIUM
    title: str = Field(..., min_length=5, max_length=300)
    description: Optional[str] = None
    recommendation: Optional[str] = None
    trigger_date: date
    due_date: Optional[date] = None
    reference_date: Optional[date] = None
    days_before: int = Field(default=30, ge=0, le=365)
    assigned_to: Optional[UUID] = None
    notify_users: Optional[list[UUID]] = None


class ContractAlertUpdate(BaseModel):
    """Schema para atualizar alerta."""

    status: Optional[AlertStatus] = None
    priority: Optional[AlertPriority] = None
    assigned_to: Optional[UUID] = None
    due_date: Optional[date] = None
    resolution_notes: Optional[str] = None
    is_read: Optional[bool] = None
    snooze_until: Optional[datetime] = None


# ============================================================
# Report Schemas
# ============================================================


class ContractSummary(BaseModel):
    """Resumo de contrato para dashboard."""

    contract_id: UUID
    contract_number: Optional[str] = None
    contract_title: Optional[str] = None
    contract_type: ContractType
    risk_level: RiskLevel
    risk_score: float
    compliance_score: float
    end_date: Optional[date] = None
    days_until_expiry: Optional[int] = None
    pending_alerts: int = 0
    status: str  # "active", "expiring", "expired", "review_required"


class RiskAssessment(BaseModel):
    """Avaliacao de risco detalhada."""

    contract_id: UUID
    overall_risk_level: RiskLevel
    overall_risk_score: float
    risk_factors: list[dict]
    # Ex: [{"factor": "no_penalty_clause", "impact": "medium", "description": "..."}]
    risky_clauses: list[dict]
    # Ex: [{"clause_number": "5.1", "type": "penalty", "risk_score": 75}]
    recommendations: list[str]
    comparison_with_template: Optional[dict] = None


class ComplianceReport(BaseModel):
    """Relatorio de conformidade."""

    contract_id: UUID
    compliance_score: float
    status: str  # "compliant", "partially_compliant", "non_compliant"
    required_clauses: list[dict]
    # Ex: [{"type": "confidentiality", "status": "present", "compliant": true}]
    missing_clauses: list[str]
    issues: list[dict]
    # Ex: [{"severity": "high", "description": "...", "clause": "5.1"}]
    recommendations: list[str]


# ============================================================
# Bulk Operations Schemas
# ============================================================


class BulkAnalysisRequest(BaseModel):
    """Request para analise em lote."""

    contract_ids: list[UUID] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Lista de IDs de contratos (max 50)"
    )
    extract_clauses: bool = True
    analyze_risk: bool = True
    check_compliance: bool = True
    generate_alerts: bool = True


class BulkAlertActionRequest(BaseModel):
    """Request para acao em lote em alertas."""

    alert_ids: list[UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Lista de IDs de alertas"
    )
    action: str = Field(
        ...,
        pattern="^(acknowledge|resolve|dismiss|snooze)$"
    )
    notes: Optional[str] = None
    snooze_days: Optional[int] = Field(None, ge=1, le=90)


# ============================================================
# Dashboard Schemas
# ============================================================


class ContractsDashboard(BaseModel):
    """Dashboard de contratos."""

    total_contracts_analyzed: int
    contracts_by_risk: dict[str, int]
    # Ex: {"low": 10, "medium": 25, "high": 5, "critical": 2}
    contracts_by_type: dict[str, int]
    expiring_soon: int  # Proximos 30 dias
    expired: int
    pending_alerts: int
    urgent_alerts: int
    average_compliance_score: float
    average_risk_score: float
    recent_analyses: list[ContractSummary]
