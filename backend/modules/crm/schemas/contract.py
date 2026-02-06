"""
Schemas Pydantic para Gestão de Contratos.

Validação e serialização de dados para:
- Contratos recorrentes e pontuais
- Templates e cláusulas
- Aditivos e renovações
- SLA e relatórios
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.crm.models.contract import (
    AddendumType,
    AdjustmentIndex,
    ContractStatus,
    ContractType,
    ServiceType,
)


# ============== Contract Schemas ==============


class ContractBase(BaseModel):
    """Campos base do contrato."""

    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    contract_type: ContractType = ContractType.RECURRING
    monthly_value: Decimal = Field(..., ge=0)
    total_value: Optional[Decimal] = Field(None, ge=0)
    setup_fee: Decimal = Field(default=Decimal("0"), ge=0)
    start_date: date
    end_date: Optional[date] = None
    grace_period_days: int = Field(default=0, ge=0)
    notice_period_days: int = Field(default=30, ge=0)

    # Renovação
    auto_renewal: bool = True
    renewal_period_months: int = Field(default=12, ge=1, le=60)
    renewal_notification_days: int = Field(default=30, ge=0)

    # Reajuste
    adjustment_enabled: bool = True
    adjustment_index: Optional[AdjustmentIndex] = None
    adjustment_fixed_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    adjustment_base_date: Optional[date] = None

    # SLA
    has_sla: bool = False
    sla_config: Optional[dict[str, Any]] = None

    # Assinatura
    signature_required: bool = True
    signature_provider: Optional[str] = Field(None, max_length=50)

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: Optional[date], info) -> Optional[date]:
        """Valida que data fim é posterior à data início."""
        if v is not None and "start_date" in info.data:
            if v <= info.data["start_date"]:
                raise ValueError("Data de término deve ser posterior à data de início")
        return v

    @field_validator("adjustment_fixed_percent")
    @classmethod
    def validate_fixed_percent(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Valida percentual fixo quando índice é FIXED."""
        if info.data.get("adjustment_index") == AdjustmentIndex.FIXED and v is None:
            raise ValueError(
                "Percentual fixo é obrigatório quando índice é FIXED"
            )
        return v


class ContractCreate(ContractBase):
    """Schema para criar contrato."""

    client_id: str = Field(..., min_length=36, max_length=36)
    opportunity_id: Optional[str] = Field(None, min_length=36, max_length=36)
    proposal_id: Optional[str] = Field(None, min_length=36, max_length=36)
    template_id: Optional[str] = Field(None, min_length=36, max_length=36)
    content: Optional[str] = None
    clauses: Optional[list[dict[str, Any]]] = None
    commercial_manager_id: Optional[str] = Field(None, min_length=36, max_length=36)
    account_manager_id: Optional[str] = Field(None, min_length=36, max_length=36)


class ContractCreateFromOpportunity(BaseModel):
    """Schema para criar contrato a partir de opportunity."""

    opportunity_id: str = Field(..., min_length=36, max_length=36)
    template_id: Optional[str] = Field(None, min_length=36, max_length=36)
    start_date: date
    end_date: Optional[date] = None
    monthly_value: Optional[Decimal] = Field(None, ge=0)
    adjustment_index: Optional[AdjustmentIndex] = None


class ContractCreateFromProposal(BaseModel):
    """Schema para criar contrato a partir de proposta aceita."""

    proposal_id: str = Field(..., min_length=36, max_length=36)
    template_id: Optional[str] = Field(None, min_length=36, max_length=36)
    start_date: date
    end_date: Optional[date] = None


class ContractUpdate(BaseModel):
    """Schema para atualizar contrato."""

    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    monthly_value: Optional[Decimal] = Field(None, ge=0)
    total_value: Optional[Decimal] = Field(None, ge=0)
    setup_fee: Optional[Decimal] = Field(None, ge=0)
    end_date: Optional[date] = None
    grace_period_days: Optional[int] = Field(None, ge=0)
    notice_period_days: Optional[int] = Field(None, ge=0)

    # Renovação
    auto_renewal: Optional[bool] = None
    renewal_period_months: Optional[int] = Field(None, ge=1, le=60)
    renewal_notification_days: Optional[int] = Field(None, ge=0)

    # Reajuste
    adjustment_enabled: Optional[bool] = None
    adjustment_index: Optional[AdjustmentIndex] = None
    adjustment_fixed_percent: Optional[Decimal] = Field(None, ge=0, le=100)

    # SLA
    has_sla: Optional[bool] = None
    sla_config: Optional[dict[str, Any]] = None

    # Responsáveis
    commercial_manager_id: Optional[str] = Field(None, min_length=36, max_length=36)
    account_manager_id: Optional[str] = Field(None, min_length=36, max_length=36)


class ContractStatusUpdate(BaseModel):
    """Schema para atualizar status do contrato."""

    status: ContractStatus
    reason: Optional[str] = None


class ContractRenewal(BaseModel):
    """Schema para renovação de contrato."""

    new_end_date: date
    adjustment_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    new_monthly_value: Optional[Decimal] = Field(None, ge=0)


class ContractItemResponse(BaseModel):
    """Resposta de item do contrato."""

    id: str
    service_type: ServiceType
    service_name: str
    description: Optional[str] = None
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContractResponse(BaseModel):
    """Resposta resumida do contrato."""

    id: str
    contract_number: str
    name: str
    contract_type: ContractType
    status: ContractStatus
    client_id: str
    monthly_value: Decimal
    total_value: Decimal
    start_date: date
    end_date: Optional[date] = None
    auto_renewal: bool
    adjustment_enabled: bool
    has_sla: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Propriedades calculadas
    is_active_contract: bool
    is_expiring_soon: bool
    days_until_end: Optional[int] = None
    needs_adjustment: bool

    model_config = ConfigDict(from_attributes=True)


class ContractDetailResponse(ContractResponse):
    """Resposta detalhada do contrato."""

    description: Optional[str] = None
    opportunity_id: Optional[str] = None
    proposal_id: Optional[str] = None
    template_id: Optional[str] = None
    setup_fee: Decimal
    grace_period_days: int
    notice_period_days: int
    renewal_period_months: int
    renewal_notification_days: int
    adjustment_index: Optional[AdjustmentIndex] = None
    adjustment_fixed_percent: Optional[Decimal] = None
    adjustment_base_date: Optional[date] = None
    last_adjustment_date: Optional[date] = None
    next_adjustment_date: Optional[date] = None
    sla_config: Optional[dict[str, Any]] = None
    content: Optional[str] = None
    clauses: Optional[list[dict[str, Any]]] = None
    signature_required: bool
    signature_provider: Optional[str] = None
    signed_at: Optional[datetime] = None
    signed_by_client: Optional[str] = None
    signed_by_company: Optional[str] = None
    pdf_file_path: Optional[str] = None
    commercial_manager_id: Optional[str] = None
    account_manager_id: Optional[str] = None
    created_by: Optional[str] = None

    # Itens do contrato
    items: list[ContractItemResponse] = []


class ContractFilter(BaseModel):
    """Filtros para listagem de contratos."""

    status: Optional[ContractStatus] = None
    contract_type: Optional[ContractType] = None
    client_id: Optional[str] = None
    commercial_manager_id: Optional[str] = None
    account_manager_id: Optional[str] = None
    is_expiring_soon: Optional[bool] = None
    needs_adjustment: Optional[bool] = None
    has_sla: Optional[bool] = None
    min_value: Optional[Decimal] = Field(None, ge=0)
    max_value: Optional[Decimal] = Field(None, ge=0)
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    end_date_from: Optional[date] = None
    end_date_to: Optional[date] = None
    search: Optional[str] = None


class ContractListResponse(BaseModel):
    """Resposta paginada de contratos."""

    items: list[ContractResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ContractStats(BaseModel):
    """Estatísticas de contratos."""

    total_contracts: int
    active_contracts: int
    total_monthly_revenue: Decimal
    average_contract_value: Decimal
    expiring_soon: int
    needs_adjustment: int
    by_status: dict[str, int]
    by_type: dict[str, int]


# ============== Contract Item Schemas ==============


class ContractItemCreate(BaseModel):
    """Schema para criar item do contrato."""

    service_type: ServiceType
    service_name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    unit_price: Decimal = Field(..., ge=0)
    notes: Optional[str] = None


class ContractItemUpdate(BaseModel):
    """Schema para atualizar item do contrato."""

    service_type: Optional[ServiceType] = None
    service_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=1)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


# ============== Contract Addendum Schemas ==============


class ContractAddendumCreate(BaseModel):
    """Schema para criar aditivo."""

    addendum_type: AddendumType
    effective_date: date
    description: str = Field(..., min_length=10)
    reason: Optional[str] = None

    # Valores (para reajuste)
    new_value: Optional[Decimal] = Field(None, ge=0)
    adjustment_percent: Optional[Decimal] = Field(None, ge=-100, le=100)
    adjustment_index: Optional[AdjustmentIndex] = None

    @field_validator("new_value", "adjustment_percent")
    @classmethod
    def validate_adjustment_values(cls, v, info):
        """Valida valores de reajuste."""
        if info.data.get("addendum_type") == AddendumType.ADJUSTMENT:
            if info.field_name == "new_value" and v is None:
                if info.data.get("adjustment_percent") is None:
                    raise ValueError(
                        "Reajuste requer novo_valor ou percentual_reajuste"
                    )
        return v


class ContractAddendumResponse(BaseModel):
    """Resposta de aditivo."""

    id: str
    contract_id: str
    addendum_number: str
    addendum_type: AddendumType
    previous_value: Optional[Decimal] = None
    new_value: Optional[Decimal] = None
    adjustment_percent: Optional[Decimal] = None
    adjustment_index: Optional[AdjustmentIndex] = None
    effective_date: date
    description: str
    reason: Optional[str] = None
    signed: bool
    signed_at: Optional[datetime] = None
    pdf_file_path: Optional[str] = None
    created_at: datetime
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ContractAddendumSign(BaseModel):
    """Schema para assinar aditivo."""

    signature_document_id: str = Field(..., min_length=1, max_length=100)


# ============== Contract Template Schemas ==============


class ContractTemplateCreate(BaseModel):
    """Schema para criar template."""

    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    service_type: Optional[ServiceType] = None
    content_template: str = Field(..., min_length=100)
    clauses: Optional[list[dict[str, Any]]] = None
    variables: Optional[list[str]] = None


class ContractTemplateUpdate(BaseModel):
    """Schema para atualizar template."""

    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    service_type: Optional[ServiceType] = None
    content_template: Optional[str] = Field(None, min_length=100)
    clauses: Optional[list[dict[str, Any]]] = None
    variables: Optional[list[str]] = None


class ContractTemplateApprove(BaseModel):
    """Schema para aprovar template."""

    notes: Optional[str] = None


class ContractTemplateResponse(BaseModel):
    """Resposta de template."""

    id: str
    name: str
    description: Optional[str] = None
    service_type: Optional[ServiceType] = None
    content_template: str
    clauses: Optional[list[dict[str, Any]]] = None
    variables: Optional[list[str]] = None
    version: int
    approved_by_legal: bool
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ContractTemplateListResponse(BaseModel):
    """Resposta de lista de templates."""

    items: list[ContractTemplateResponse]
    total: int


# ============== Contract SLA Report Schemas ==============


class SLAIndicatorResult(BaseModel):
    """Resultado de um indicador de SLA."""

    name: str
    target: Decimal
    actual: Decimal
    achieved: bool
    weight: Decimal = Field(default=Decimal("1"))


class ContractSLAReportCreate(BaseModel):
    """Schema para criar relatório de SLA."""

    year: int = Field(..., ge=2020, le=2100)
    month: int = Field(..., ge=1, le=12)
    indicators: list[SLAIndicatorResult]
    overall_score: Decimal = Field(..., ge=0, le=150)
    penalty_applied: bool = False
    penalty_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    penalty_amount: Optional[Decimal] = Field(None, ge=0)


class ContractSLAReportResponse(BaseModel):
    """Resposta de relatório de SLA."""

    id: str
    contract_id: str
    year: int
    month: int
    indicators: list[dict[str, Any]]
    overall_score: Decimal
    penalty_applied: bool
    penalty_percent: Decimal
    penalty_amount: Decimal
    status: str
    period_label: str
    is_target_met: bool
    generated_at: datetime
    generated_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ContractSLAReportApprove(BaseModel):
    """Schema para aprovar relatório de SLA."""

    disputed: bool = False
    dispute_reason: Optional[str] = None
