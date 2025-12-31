"""Schemas para contas a receber."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.financial.models.billing_rule import (
    BillingFrequency,
    BillingRuleStatus,
    BillingType,
)
from modules.financial.models.customer import CustomerStatus, CustomerType
from modules.financial.models.receivable_account import (
    ReceivablePriority,
    ReceivableStatus,
    ReceivableType,
)
from modules.financial.models.receivable_category import CategoryType
from modules.financial.models.receivable_installment import InstallmentStatus
from modules.financial.models.receivable_payment import PaymentOrigin, PaymentStatus


# ============= Customer =============


class CustomerBase(BaseModel):
    """Base para cliente."""

    cpf_cnpj: str = Field(..., min_length=11, max_length=20)
    name: str = Field(..., min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)
    customer_type: CustomerType = CustomerType.MORADOR

    # Vinculacao
    morador_id: Optional[UUID] = None
    unidade_id: Optional[UUID] = None

    # Contato
    email: Optional[str] = Field(None, max_length=200)
    email_secondary: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)

    # Endereco
    address_street: Optional[str] = Field(None, max_length=200)
    address_number: Optional[str] = Field(None, max_length=20)
    address_complement: Optional[str] = Field(None, max_length=100)
    address_neighborhood: Optional[str] = Field(None, max_length=100)
    address_city: Optional[str] = Field(None, max_length=100)
    address_state: Optional[str] = Field(None, max_length=2)
    address_zipcode: Optional[str] = Field(None, max_length=10)

    # Financeiro
    credit_limit: Decimal = Field(default=Decimal("0"), ge=0)

    # Cobranca
    billing_email: Optional[str] = Field(None, max_length=200)
    billing_day: Optional[str] = Field(None, max_length=2)
    auto_billing: bool = True

    # Notificacoes
    notify_email: bool = True
    notify_sms: bool = False
    notify_whatsapp: bool = True
    notify_push: bool = True

    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Schema para criacao de cliente."""

    condominio_id: UUID


class CustomerUpdate(BaseModel):
    """Schema para atualizacao de cliente."""

    name: Optional[str] = Field(None, min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)
    customer_type: Optional[CustomerType] = None

    morador_id: Optional[UUID] = None
    unidade_id: Optional[UUID] = None

    email: Optional[str] = Field(None, max_length=200)
    email_secondary: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)

    address_street: Optional[str] = Field(None, max_length=200)
    address_number: Optional[str] = Field(None, max_length=20)
    address_complement: Optional[str] = Field(None, max_length=100)
    address_neighborhood: Optional[str] = Field(None, max_length=100)
    address_city: Optional[str] = Field(None, max_length=100)
    address_state: Optional[str] = Field(None, max_length=2)
    address_zipcode: Optional[str] = Field(None, max_length=10)

    credit_limit: Optional[Decimal] = Field(None, ge=0)
    billing_email: Optional[str] = Field(None, max_length=200)
    billing_day: Optional[str] = Field(None, max_length=2)
    auto_billing: Optional[bool] = None

    notify_email: Optional[bool] = None
    notify_sms: Optional[bool] = None
    notify_whatsapp: Optional[bool] = None
    notify_push: Optional[bool] = None

    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Schema de resposta para cliente."""

    id: UUID
    condominio_id: UUID
    status: CustomerStatus

    total_debt: Decimal
    overdue_debt: Decimal
    available_credit: float
    is_inadimplente: bool

    is_blocked: bool
    blocked_reason: Optional[str] = None
    blocked_at: Optional[datetime] = None

    display_name: str
    formatted_cpf_cnpj: str

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Configuracao do schema."""

        from_attributes = True


class CustomerFilter(BaseModel):
    """Filtros para busca de clientes."""

    search: Optional[str] = None
    customer_type: Optional[CustomerType] = None
    status: Optional[CustomerStatus] = None
    is_inadimplente: Optional[bool] = None
    is_blocked: Optional[bool] = None
    unidade_id: Optional[UUID] = None


# ============= ReceivableCategory =============


class ReceivableCategoryCreate(BaseModel):
    """Schema para criacao de categoria."""

    condominio_id: UUID
    code: Optional[str] = Field(None, max_length=20)
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    category_type: CategoryType = CategoryType.OUTROS
    parent_id: Optional[UUID] = None

    accounting_code: Optional[str] = Field(None, max_length=30)
    cost_center: Optional[str] = Field(None, max_length=30)

    apply_interest: bool = True
    interest_rate: str = "1.00"
    apply_penalty: bool = True
    penalty_rate: str = "2.00"
    grace_days: int = Field(default=0, ge=0)

    display_order: int = 0


class ReceivableCategoryUpdate(BaseModel):
    """Schema para atualizacao de categoria."""

    code: Optional[str] = Field(None, max_length=20)
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    category_type: Optional[CategoryType] = None
    parent_id: Optional[UUID] = None

    accounting_code: Optional[str] = Field(None, max_length=30)
    cost_center: Optional[str] = Field(None, max_length=30)

    apply_interest: Optional[bool] = None
    interest_rate: Optional[str] = None
    apply_penalty: Optional[bool] = None
    penalty_rate: Optional[str] = None
    grace_days: Optional[int] = Field(None, ge=0)

    display_order: Optional[int] = None


class ReceivableCategoryResponse(BaseModel):
    """Schema de resposta para categoria."""

    id: UUID
    condominio_id: UUID
    code: Optional[str] = None
    name: str
    description: Optional[str] = None
    category_type: str
    parent_id: Optional[UUID] = None
    full_name: str

    accounting_code: Optional[str] = None
    cost_center: Optional[str] = None

    apply_interest: bool
    interest_rate: str
    apply_penalty: bool
    penalty_rate: str
    grace_days: int

    display_order: int
    has_children: bool
    ativo: bool

    created_at: datetime

    class Config:
        """Configuracao do schema."""

        from_attributes = True


# ============= ReceivableAccount =============


class ReceivableAccountBase(BaseModel):
    """Base para conta a receber."""

    description: str = Field(..., min_length=3, max_length=500)
    document_number: Optional[str] = Field(None, max_length=50)
    receivable_type: ReceivableType = ReceivableType.AVULSA
    priority: ReceivablePriority = ReceivablePriority.MEDIA

    customer_id: Optional[UUID] = None
    unidade_id: Optional[UUID] = None
    morador_id: Optional[UUID] = None
    category_id: Optional[UUID] = None

    gross_value: Decimal = Field(..., gt=0)
    discount_value: Decimal = Field(default=Decimal("0"), ge=0)
    addition_value: Decimal = Field(default=Decimal("0"), ge=0)

    # Juros e multa
    interest_rate: Decimal = Field(default=Decimal("1"), ge=0)
    penalty_rate: Decimal = Field(default=Decimal("2"), ge=0)
    grace_days: int = Field(default=0, ge=0)

    # Datas
    issue_date: Optional[date] = None
    due_date: date
    competence_date: Optional[date] = None

    # Parcelamento
    total_installments: int = Field(default=1, ge=1, le=360)

    # Recorrencia
    is_recurring: bool = False
    recurrence_type: Optional[str] = None
    recurrence_end_date: Optional[date] = None

    # Centro de custo
    cost_center: Optional[str] = Field(None, max_length=50)

    # Tags e notas
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class ReceivableAccountCreate(ReceivableAccountBase):
    """Schema para criacao de conta a receber."""

    condominio_id: UUID

    # Boleto/PIX automatico
    generate_boleto: bool = False
    generate_pix: bool = False


class ReceivableAccountUpdate(BaseModel):
    """Schema para atualizacao de conta a receber."""

    description: Optional[str] = Field(None, min_length=3, max_length=500)
    document_number: Optional[str] = Field(None, max_length=50)
    priority: Optional[ReceivablePriority] = None

    customer_id: Optional[UUID] = None
    category_id: Optional[UUID] = None

    gross_value: Optional[Decimal] = Field(None, gt=0)
    discount_value: Optional[Decimal] = Field(None, ge=0)
    addition_value: Optional[Decimal] = Field(None, ge=0)

    interest_rate: Optional[Decimal] = Field(None, ge=0)
    penalty_rate: Optional[Decimal] = Field(None, ge=0)
    grace_days: Optional[int] = Field(None, ge=0)

    due_date: Optional[date] = None
    competence_date: Optional[date] = None

    cost_center: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class ReceivableAccountResponse(ReceivableAccountBase):
    """Schema de resposta para conta a receber."""

    id: UUID
    condominio_id: UUID
    code: Optional[str] = None
    status: ReceivableStatus
    net_value: Decimal
    paid_value: Decimal
    remaining_value: Optional[Decimal] = None
    interest_value: Decimal
    penalty_value: Decimal

    entry_date: date
    payment_date: Optional[date] = None

    current_installment: int
    parent_id: Optional[UUID] = None

    boleto_generated: bool
    boleto_number: Optional[str] = None
    boleto_url: Optional[str] = None
    pix_generated: bool
    pix_copy_paste: Optional[str] = None

    collection_attempts: int
    last_collection_date: Optional[datetime] = None

    is_protested: bool
    is_in_agreement: bool
    is_written_off: bool

    is_overdue: bool
    days_overdue: int
    days_until_due: int
    payment_percentage: float
    balance: Decimal
    current_total_value: Decimal

    attachments: List[dict] = Field(default_factory=list)

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Configuracao do schema."""

        from_attributes = True


class ReceivableAccountListResponse(BaseModel):
    """Schema de lista de contas a receber."""

    id: UUID
    code: Optional[str] = None
    document_number: Optional[str] = None
    description: str
    receivable_type: str
    status: str
    priority: str
    customer_name: Optional[str] = None
    unidade_codigo: Optional[str] = None
    category_name: Optional[str] = None
    net_value: Decimal
    paid_value: Decimal
    balance: Decimal
    due_date: date
    payment_date: Optional[date] = None
    is_overdue: bool
    days_overdue: int
    total_installments: int
    boleto_generated: bool
    pix_generated: bool

    class Config:
        """Configuracao do schema."""

        from_attributes = True


class ReceivableAccountFilter(BaseModel):
    """Filtros para busca de contas a receber."""

    search: Optional[str] = None
    customer_id: Optional[UUID] = None
    unidade_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    status: Optional[ReceivableStatus] = None
    receivable_type: Optional[ReceivableType] = None
    priority: Optional[ReceivablePriority] = None
    due_date_start: Optional[date] = None
    due_date_end: Optional[date] = None
    payment_date_start: Optional[date] = None
    payment_date_end: Optional[date] = None
    is_overdue: Optional[bool] = None
    has_boleto: Optional[bool] = None
    has_pix: Optional[bool] = None
    cost_center: Optional[str] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    tags: Optional[List[str]] = None


class ReceivableAccountStats(BaseModel):
    """Estatisticas de contas a receber."""

    total_count: int = 0
    total_value: Decimal = Decimal("0")
    total_received: Decimal = Decimal("0")
    total_pending: Decimal = Decimal("0")
    total_overdue: Decimal = Decimal("0")
    overdue_count: int = 0

    by_status: dict = Field(default_factory=dict)
    by_category: dict = Field(default_factory=dict)
    by_unit: dict = Field(default_factory=dict)
    by_priority: dict = Field(default_factory=dict)


# ============= ReceivableInstallment =============


class ReceivableInstallmentCreate(BaseModel):
    """Schema para criacao de parcela."""

    installment_number: int = Field(..., ge=1)
    total_installments: int = Field(..., ge=1)
    original_value: Decimal = Field(..., gt=0)
    due_date: date

    discount_value: Decimal = Field(default=Decimal("0"), ge=0)
    interest_rate: Decimal = Field(default=Decimal("1"), ge=0)
    penalty_rate: Decimal = Field(default=Decimal("2"), ge=0)
    grace_days: int = Field(default=0, ge=0)

    notes: Optional[str] = None


class ReceivableInstallmentUpdate(BaseModel):
    """Schema para atualizacao de parcela."""

    due_date: Optional[date] = None
    discount_value: Optional[Decimal] = Field(None, ge=0)
    addition_value: Optional[Decimal] = Field(None, ge=0)
    interest_rate: Optional[Decimal] = Field(None, ge=0)
    penalty_rate: Optional[Decimal] = Field(None, ge=0)
    grace_days: Optional[int] = Field(None, ge=0)

    notes: Optional[str] = None


class ReceivableInstallmentResponse(BaseModel):
    """Schema de resposta para parcela."""

    id: UUID
    receivable_account_id: UUID
    condominio_id: UUID
    installment_number: int
    total_installments: int
    display_number: str
    status: InstallmentStatus

    original_value: Decimal
    discount_value: Decimal
    interest_value: Decimal
    penalty_value: Decimal
    addition_value: Decimal
    current_value: Decimal
    paid_value: Decimal
    balance: Decimal

    due_date: date
    original_due_date: Optional[date] = None
    payment_date: Optional[date] = None

    interest_rate: Decimal
    penalty_rate: Decimal
    grace_days: int

    boleto_generated: bool
    boleto_number: Optional[str] = None
    boleto_barcode: Optional[str] = None
    boleto_digitable_line: Optional[str] = None
    boleto_url: Optional[str] = None
    boleto_expires_at: Optional[date] = None

    pix_generated: bool
    pix_qrcode: Optional[str] = None
    pix_copy_paste: Optional[str] = None
    pix_expires_at: Optional[datetime] = None

    collection_attempts: int
    last_collection_date: Optional[datetime] = None

    is_overdue: bool
    days_overdue: int
    days_until_due: int
    is_paid: bool
    is_partially_paid: bool
    is_renegotiated: bool
    can_generate_boleto: bool

    notes: Optional[str] = None
    created_at: datetime

    class Config:
        """Configuracao do schema."""

        from_attributes = True


class ReceivableInstallmentRenegotiateRequest(BaseModel):
    """Request para renegociar parcela."""

    new_due_date: date
    new_value: Optional[Decimal] = Field(None, gt=0)
    reason: str = Field(..., min_length=5, max_length=500)


class ReceivableInstallmentBoletoRequest(BaseModel):
    """Request para gerar boleto."""

    expiration_days: int = Field(default=30, ge=1, le=365)


class ReceivableInstallmentPixRequest(BaseModel):
    """Request para gerar PIX."""

    expiration_hours: int = Field(default=24, ge=1, le=168)


# ============= ReceivablePayment =============


class ReceivablePaymentCreate(BaseModel):
    """Schema para criacao de recebimento."""

    installment_id: UUID
    paid_value: Decimal = Field(..., gt=0)
    payment_date: date
    origin: PaymentOrigin = PaymentOrigin.MANUAL

    discount_value: Decimal = Field(default=Decimal("0"), ge=0)
    interest_value: Decimal = Field(default=Decimal("0"), ge=0)
    penalty_value: Decimal = Field(default=Decimal("0"), ge=0)
    fee_value: Decimal = Field(default=Decimal("0"), ge=0)

    payment_method_id: Optional[UUID] = None
    bank_account_id: Optional[UUID] = None

    receipt_number: Optional[str] = Field(None, max_length=50)
    receipt_url: Optional[str] = Field(None, max_length=500)
    authentication_code: Optional[str] = Field(None, max_length=100)

    notes: Optional[str] = None


class ReceivablePaymentUpdate(BaseModel):
    """Schema para atualizacao de recebimento."""

    payment_date: Optional[date] = None
    discount_value: Optional[Decimal] = Field(None, ge=0)
    interest_value: Optional[Decimal] = Field(None, ge=0)
    penalty_value: Optional[Decimal] = Field(None, ge=0)
    fee_value: Optional[Decimal] = Field(None, ge=0)

    receipt_number: Optional[str] = Field(None, max_length=50)
    receipt_url: Optional[str] = Field(None, max_length=500)
    authentication_code: Optional[str] = Field(None, max_length=100)

    notes: Optional[str] = None


class ReceivablePaymentResponse(BaseModel):
    """Schema de resposta para recebimento."""

    id: UUID
    installment_id: UUID
    condominio_id: UUID
    code: Optional[str] = None
    status: PaymentStatus
    origin: PaymentOrigin

    paid_value: Decimal
    discount_value: Decimal
    interest_value: Decimal
    penalty_value: Decimal
    fee_value: Decimal
    net_value: Decimal
    total_additions: Decimal
    total_deductions: Decimal

    payment_date: date
    processing_date: Optional[date] = None
    confirmation_date: Optional[date] = None
    credit_date: Optional[date] = None

    payment_method_name: Optional[str] = None
    bank_account_name: Optional[str] = None

    receipt_number: Optional[str] = None
    receipt_url: Optional[str] = None
    authentication_code: Optional[str] = None

    bank_transaction_id: Optional[str] = None
    bank_return_code: Optional[str] = None
    bank_return_message: Optional[str] = None

    boleto_nosso_numero: Optional[str] = None
    pix_txid: Optional[str] = None
    pix_end_to_end_id: Optional[str] = None

    is_confirmed: bool
    is_reversed: bool
    is_reconciled: bool

    reversed_at: Optional[datetime] = None
    reversal_reason: Optional[str] = None

    notes: Optional[str] = None
    created_at: datetime

    class Config:
        """Configuracao do schema."""

        from_attributes = True


class ReceivablePaymentReverseRequest(BaseModel):
    """Request para estornar recebimento."""

    reason: str = Field(..., min_length=5, max_length=500)
    receipt: Optional[str] = Field(None, max_length=500)


class ReceivablePaymentReconcileRequest(BaseModel):
    """Request para conciliar recebimento."""

    notes: Optional[str] = Field(None, max_length=500)


# ============= BillingRule =============


class BillingRuleBase(BaseModel):
    """Base para regra de cobranca."""

    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    billing_type: BillingType = BillingType.TAXA_CONDOMINIAL
    category_id: Optional[UUID] = None

    base_value: Decimal = Field(..., gt=0)
    value_type: str = Field(default="fixo")  # fixo, percentual, por_m2
    reference_field: Optional[str] = Field(None, max_length=50)

    frequency: BillingFrequency = BillingFrequency.MENSAL
    due_day: int = Field(default=10, ge=1, le=28)
    generation_day: int = Field(default=1, ge=1, le=28)

    start_date: date
    end_date: Optional[date] = None

    apply_interest: bool = True
    interest_rate: Decimal = Field(default=Decimal("1"), ge=0)
    apply_penalty: bool = True
    penalty_rate: Decimal = Field(default=Decimal("2"), ge=0)
    grace_days: int = Field(default=0, ge=0)

    apply_discount: bool = False
    discount_rate: Decimal = Field(default=Decimal("0"), ge=0)
    discount_days: int = Field(default=0, ge=0)

    auto_generate_boleto: bool = True
    boleto_days_before: int = Field(default=5, ge=1, le=30)
    boleto_expiration_days: int = Field(default=30, ge=1, le=365)

    auto_generate_pix: bool = True
    pix_expiration_hours: int = Field(default=24, ge=1, le=168)

    notifications_enabled: bool = True
    notification_channels: List[str] = Field(default_factory=lambda: ["email", "push"])
    notify_before_days: List[int] = Field(default_factory=lambda: [7, 3, 1])
    notify_after_days: List[int] = Field(default_factory=lambda: [1, 3, 7, 15, 30])
    notification_time: time = Field(default=time(9, 0))

    apply_to_all: bool = True
    unit_filter: dict = Field(default_factory=dict)

    notes: Optional[str] = None


class BillingRuleCreate(BillingRuleBase):
    """Schema para criacao de regra."""

    condominio_id: UUID

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, v: date) -> date:
        """Valida data de inicio."""
        return v


class BillingRuleUpdate(BaseModel):
    """Schema para atualizacao de regra."""

    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    category_id: Optional[UUID] = None

    base_value: Optional[Decimal] = Field(None, gt=0)
    value_type: Optional[str] = None
    reference_field: Optional[str] = Field(None, max_length=50)

    due_day: Optional[int] = Field(None, ge=1, le=28)
    generation_day: Optional[int] = Field(None, ge=1, le=28)

    end_date: Optional[date] = None

    apply_interest: Optional[bool] = None
    interest_rate: Optional[Decimal] = Field(None, ge=0)
    apply_penalty: Optional[bool] = None
    penalty_rate: Optional[Decimal] = Field(None, ge=0)
    grace_days: Optional[int] = Field(None, ge=0)

    apply_discount: Optional[bool] = None
    discount_rate: Optional[Decimal] = Field(None, ge=0)
    discount_days: Optional[int] = Field(None, ge=0)

    auto_generate_boleto: Optional[bool] = None
    boleto_days_before: Optional[int] = Field(None, ge=1, le=30)
    boleto_expiration_days: Optional[int] = Field(None, ge=1, le=365)

    auto_generate_pix: Optional[bool] = None
    pix_expiration_hours: Optional[int] = Field(None, ge=1, le=168)

    notifications_enabled: Optional[bool] = None
    notification_channels: Optional[List[str]] = None
    notify_before_days: Optional[List[int]] = None
    notify_after_days: Optional[List[int]] = None
    notification_time: Optional[time] = None

    apply_to_all: Optional[bool] = None
    unit_filter: Optional[dict] = None

    notes: Optional[str] = None


class BillingRuleResponse(BillingRuleBase):
    """Schema de resposta para regra."""

    id: UUID
    condominio_id: UUID
    status: BillingRuleStatus
    is_active: bool
    should_run_today: bool

    total_generated: int
    total_collected: Decimal
    collection_rate: Decimal

    last_run_at: Optional[datetime] = None
    last_run_result: dict = Field(default_factory=dict)
    next_run_at: Optional[datetime] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Configuracao do schema."""

        from_attributes = True


class BillingRuleFilter(BaseModel):
    """Filtros para busca de regras."""

    search: Optional[str] = None
    billing_type: Optional[BillingType] = None
    status: Optional[BillingRuleStatus] = None
    frequency: Optional[BillingFrequency] = None
    is_active: Optional[bool] = None


# ============= Bulk Operations =============


class ReceivableBulkPaymentRequest(BaseModel):
    """Request para recebimento em lote."""

    installment_ids: List[UUID] = Field(..., min_length=1)
    payment_date: date
    payment_method_id: Optional[UUID] = None
    bank_account_id: Optional[UUID] = None


class ReceivableBulkBoletoRequest(BaseModel):
    """Request para geracao de boletos em lote."""

    installment_ids: List[UUID] = Field(..., min_length=1)
    expiration_days: int = Field(default=30, ge=1, le=365)


class ReceivableBulkNotifyRequest(BaseModel):
    """Request para envio de notificacoes em lote."""

    installment_ids: List[UUID] = Field(..., min_length=1)
    channels: List[str] = Field(default_factory=lambda: ["email"])
    template: str = Field(default="cobranca")


class ReceivableWriteOffRequest(BaseModel):
    """Request para baixa de conta."""

    reason: str = Field(..., min_length=5, max_length=500)


class ReceivableProtestRequest(BaseModel):
    """Request para protesto de conta."""

    protest_number: str = Field(..., min_length=1, max_length=50)


class ReceivableAgreementRequest(BaseModel):
    """Request para acordo de conta."""

    agreement_id: UUID
    new_due_date: date
    new_value: Optional[Decimal] = Field(None, gt=0)
    installments: int = Field(default=1, ge=1, le=60)
