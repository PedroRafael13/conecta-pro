"""Schemas para contas a pagar."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.financial.models.payable_account import (
    PayablePriority,
    PayableStatus,
    PayableType,
    RecurrenceType,
)
from modules.financial.models.payable_installment import InstallmentStatus
from modules.financial.models.payable_payment import PaymentOrigin, PaymentStatus

# ============= PayableAccount =============


class PayableAccountBase(BaseModel):
    """Base para conta a pagar."""

    description: str = Field(..., min_length=3, max_length=500)
    document_number: Optional[str] = Field(None, max_length=50)
    payable_type: PayableType = PayableType.AVULSA
    priority: PayablePriority = PayablePriority.MEDIA

    supplier_id: Optional[UUID] = None
    category_id: Optional[UUID] = None

    gross_value: Decimal = Field(..., gt=0)
    discount_value: Decimal = Field(default=Decimal("0"), ge=0)
    addition_value: Decimal = Field(default=Decimal("0"), ge=0)

    # Retenções
    withhold_iss: Decimal = Field(default=Decimal("0"), ge=0)
    withhold_ir: Decimal = Field(default=Decimal("0"), ge=0)
    withhold_pis: Decimal = Field(default=Decimal("0"), ge=0)
    withhold_cofins: Decimal = Field(default=Decimal("0"), ge=0)
    withhold_csll: Decimal = Field(default=Decimal("0"), ge=0)
    withhold_inss: Decimal = Field(default=Decimal("0"), ge=0)

    # Datas
    issue_date: Optional[date] = None
    due_date: date
    competence_date: Optional[date] = None

    # Parcelamento
    total_installments: int = Field(default=1, ge=1, le=360)

    # Recorrência
    is_recurring: bool = False
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_end_date: Optional[date] = None

    # Centro de custo
    cost_center: Optional[str] = Field(None, max_length=50)
    project: Optional[str] = Field(None, max_length=50)

    # Documento fiscal
    fiscal_document_type: Optional[str] = Field(None, max_length=30)
    fiscal_document_key: Optional[str] = Field(None, max_length=50)
    fiscal_document_url: Optional[str] = Field(None, max_length=500)

    # Contrato
    contract_id: Optional[UUID] = None

    # Forma de pagamento
    payment_method_id: Optional[UUID] = None
    bank_account_id: Optional[UUID] = None

    # Aprovação
    requires_approval: bool = False

    # Tags e notas
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class PayableAccountCreate(PayableAccountBase):
    """Schema para criação de conta a pagar."""

    condominio_id: UUID

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: date) -> date:
        """Valida data de vencimento."""
        # Permite datas no passado (para lançamentos retroativos)
        return v


class PayableAccountUpdate(BaseModel):
    """Schema para atualização de conta a pagar."""

    description: Optional[str] = Field(None, min_length=3, max_length=500)
    document_number: Optional[str] = Field(None, max_length=50)
    priority: Optional[PayablePriority] = None

    supplier_id: Optional[UUID] = None
    category_id: Optional[UUID] = None

    gross_value: Optional[Decimal] = Field(None, gt=0)
    discount_value: Optional[Decimal] = Field(None, ge=0)
    addition_value: Optional[Decimal] = Field(None, ge=0)

    # Retenções
    withhold_iss: Optional[Decimal] = Field(None, ge=0)
    withhold_ir: Optional[Decimal] = Field(None, ge=0)
    withhold_pis: Optional[Decimal] = Field(None, ge=0)
    withhold_cofins: Optional[Decimal] = Field(None, ge=0)
    withhold_csll: Optional[Decimal] = Field(None, ge=0)
    withhold_inss: Optional[Decimal] = Field(None, ge=0)

    # Datas
    due_date: Optional[date] = None
    competence_date: Optional[date] = None

    # Centro de custo
    cost_center: Optional[str] = Field(None, max_length=50)
    project: Optional[str] = Field(None, max_length=50)

    # Forma de pagamento
    payment_method_id: Optional[UUID] = None
    bank_account_id: Optional[UUID] = None

    # Tags e notas
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class PayableAccountResponse(PayableAccountBase):
    """Schema de resposta para conta a pagar."""

    id: UUID
    condominio_id: UUID
    code: Optional[str] = None
    status: PayableStatus
    net_value: Decimal
    paid_value: Decimal
    remaining_value: Optional[Decimal] = None
    total_withholdings: Decimal

    entry_date: date
    payment_date: Optional[date] = None

    current_installment: int
    parent_id: Optional[UUID] = None

    approval_status: Optional[str] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None

    scheduled_payment_date: Optional[date] = None

    is_overdue: bool
    days_overdue: int
    days_until_due: int
    payment_percentage: float
    balance: Decimal

    attachments: List[dict] = Field(default_factory=list)

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Configuração do schema."""

        from_attributes = True


class PayableAccountListResponse(BaseModel):
    """Schema de lista de contas a pagar."""

    id: UUID
    code: Optional[str] = None
    document_number: Optional[str] = None
    description: str
    payable_type: str
    status: str
    priority: str
    supplier_name: Optional[str] = None
    category_name: Optional[str] = None
    net_value: Decimal
    paid_value: Decimal
    balance: Decimal
    due_date: date
    payment_date: Optional[date] = None
    is_overdue: bool
    days_overdue: int
    total_installments: int

    class Config:
        """Configuração do schema."""

        from_attributes = True


class PayableAccountFilter(BaseModel):
    """Filtros para busca de contas a pagar."""

    search: Optional[str] = None
    supplier_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    status: Optional[PayableStatus] = None
    payable_type: Optional[PayableType] = None
    priority: Optional[PayablePriority] = None
    due_date_start: Optional[date] = None
    due_date_end: Optional[date] = None
    payment_date_start: Optional[date] = None
    payment_date_end: Optional[date] = None
    is_overdue: Optional[bool] = None
    cost_center: Optional[str] = None
    project: Optional[str] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    tags: Optional[List[str]] = None


class PayableAccountStats(BaseModel):
    """Estatísticas de contas a pagar."""

    total_count: int = 0
    total_value: Decimal = Decimal("0")
    total_paid: Decimal = Decimal("0")
    total_pending: Decimal = Decimal("0")
    total_overdue: Decimal = Decimal("0")
    overdue_count: int = 0

    by_status: dict = Field(default_factory=dict)
    by_category: dict = Field(default_factory=dict)
    by_supplier: dict = Field(default_factory=dict)
    by_priority: dict = Field(default_factory=dict)


# ============= PayableInstallment =============


class PayableInstallmentCreate(BaseModel):
    """Schema para criação de parcela."""

    installment_number: int = Field(..., ge=1)
    total_installments: int = Field(..., ge=1)
    original_value: Decimal = Field(..., gt=0)
    due_date: date

    discount_value: Decimal = Field(default=Decimal("0"), ge=0)
    interest_rate: Decimal = Field(default=Decimal("0"), ge=0)
    penalty_rate: Decimal = Field(default=Decimal("0"), ge=0)

    payment_method_id: Optional[UUID] = None
    barcode: Optional[str] = Field(None, max_length=100)
    pix_copy_paste: Optional[str] = Field(None, max_length=500)

    notes: Optional[str] = None


class PayableInstallmentUpdate(BaseModel):
    """Schema para atualização de parcela."""

    due_date: Optional[date] = None
    discount_value: Optional[Decimal] = Field(None, ge=0)
    addition_value: Optional[Decimal] = Field(None, ge=0)
    interest_rate: Optional[Decimal] = Field(None, ge=0)
    penalty_rate: Optional[Decimal] = Field(None, ge=0)

    payment_method_id: Optional[UUID] = None
    barcode: Optional[str] = Field(None, max_length=100)
    digitable_line: Optional[str] = Field(None, max_length=100)
    pix_qrcode: Optional[str] = None
    pix_copy_paste: Optional[str] = Field(None, max_length=500)
    boleto_url: Optional[str] = Field(None, max_length=500)

    scheduled_payment_date: Optional[date] = None
    notes: Optional[str] = None


class PayableInstallmentResponse(BaseModel):
    """Schema de resposta para parcela."""

    id: UUID
    payable_account_id: UUID
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

    barcode: Optional[str] = None
    digitable_line: Optional[str] = None
    pix_copy_paste: Optional[str] = None
    boleto_url: Optional[str] = None

    scheduled_payment_date: Optional[date] = None

    is_overdue: bool
    days_overdue: int
    days_until_due: int
    is_paid: bool
    is_partially_paid: bool
    is_renegotiated: bool

    notes: Optional[str] = None
    created_at: datetime

    class Config:
        """Configuração do schema."""

        from_attributes = True


class PayableInstallmentRenegotiateRequest(BaseModel):
    """Request para renegociar parcela."""

    new_due_date: date
    new_value: Optional[Decimal] = Field(None, gt=0)
    reason: str = Field(..., min_length=5, max_length=500)


# ============= PayablePayment =============


class PayablePaymentCreate(BaseModel):
    """Schema para criação de pagamento."""

    installment_id: UUID
    paid_value: Decimal = Field(..., gt=0)
    payment_date: date

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


class PayablePaymentUpdate(BaseModel):
    """Schema para atualização de pagamento."""

    payment_date: Optional[date] = None
    discount_value: Optional[Decimal] = Field(None, ge=0)
    interest_value: Optional[Decimal] = Field(None, ge=0)
    penalty_value: Optional[Decimal] = Field(None, ge=0)
    fee_value: Optional[Decimal] = Field(None, ge=0)

    receipt_number: Optional[str] = Field(None, max_length=50)
    receipt_url: Optional[str] = Field(None, max_length=500)
    authentication_code: Optional[str] = Field(None, max_length=100)

    notes: Optional[str] = None


class PayablePaymentResponse(BaseModel):
    """Schema de resposta para pagamento."""

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

    payment_date: date
    processing_date: Optional[date] = None
    confirmation_date: Optional[date] = None

    payment_method_name: Optional[str] = None
    bank_account_name: Optional[str] = None

    receipt_number: Optional[str] = None
    receipt_url: Optional[str] = None
    authentication_code: Optional[str] = None

    bank_transaction_id: Optional[str] = None
    bank_return_code: Optional[str] = None
    bank_return_message: Optional[str] = None

    is_confirmed: bool
    is_reversed: bool
    is_reconciled: bool

    reversed_at: Optional[datetime] = None
    reversal_reason: Optional[str] = None

    notes: Optional[str] = None
    created_at: datetime

    class Config:
        """Configuração do schema."""

        from_attributes = True


class PayablePaymentReverseRequest(BaseModel):
    """Request para estornar pagamento."""

    reason: str = Field(..., min_length=5, max_length=500)
    receipt: Optional[str] = Field(None, max_length=500)


class PayablePaymentReconcileRequest(BaseModel):
    """Request para conciliar pagamento."""

    notes: Optional[str] = Field(None, max_length=500)


# ============= Bulk Operations =============


class PayableBulkPaymentRequest(BaseModel):
    """Request para pagamento em lote."""

    installment_ids: List[UUID] = Field(..., min_length=1)
    payment_date: date
    payment_method_id: Optional[UUID] = None
    bank_account_id: Optional[UUID] = None


class PayableBulkApproveRequest(BaseModel):
    """Request para aprovação em lote."""

    payable_ids: List[UUID] = Field(..., min_length=1)
    notes: Optional[str] = Field(None, max_length=500)


class PayableScheduleRequest(BaseModel):
    """Request para agendar pagamento."""

    scheduled_date: date

    @field_validator("scheduled_date")
    @classmethod
    def validate_scheduled_date(cls, v: date) -> date:
        """Valida data de agendamento."""
        if v < date.today():
            raise ValueError("Data de agendamento não pode ser no passado")
        return v
