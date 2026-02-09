"""Schemas Pydantic para solicitações de reembolso."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.reimbursement.schemas.reimbursement_attachment import (
    ReimbursementAttachmentResponse,
)
from modules.reimbursement.schemas.reimbursement_item import (
    ReimbursementItemCreate,
    ReimbursementItemResponse,
)


class ReimbursementRequestBase(BaseModel):
    """Base schema para solicitação de reembolso."""

    title: str = Field(..., min_length=3, max_length=200)
    description: str | None = Field(None, max_length=2000)
    expense_date_start: date
    expense_date_end: date
    cost_center: str | None = Field(None, max_length=50)
    project: str | None = Field(None, max_length=100)
    notes: str | None = None

    # Dados bancários (opcional na criação)
    bank_code: str | None = Field(None, max_length=10)
    bank_agency: str | None = Field(None, max_length=10)
    bank_account: str | None = Field(None, max_length=20)
    pix_key: str | None = Field(None, max_length=100)

    @field_validator("expense_date_end")
    @classmethod
    def validate_date_range(cls, v: date, info) -> date:
        """Valida que data fim é >= data início."""
        start = info.data.get("expense_date_start")
        if start and v < start:
            raise ValueError("Data fim deve ser maior ou igual à data início")
        return v


class ReimbursementRequestCreate(ReimbursementRequestBase):
    """Schema para criação de solicitação de reembolso."""

    items: list[ReimbursementItemCreate] | None = Field(default_factory=list)


class ReimbursementRequestUpdate(BaseModel):
    """Schema para atualização de solicitação de reembolso."""

    title: str | None = Field(None, min_length=3, max_length=200)
    description: str | None = Field(None, max_length=2000)
    expense_date_start: date | None = None
    expense_date_end: date | None = None
    cost_center: str | None = Field(None, max_length=50)
    project: str | None = Field(None, max_length=100)
    notes: str | None = None
    bank_code: str | None = Field(None, max_length=10)
    bank_agency: str | None = Field(None, max_length=10)
    bank_account: str | None = Field(None, max_length=20)
    pix_key: str | None = Field(None, max_length=100)


class ReimbursementRequestResponse(BaseModel):
    """Schema de resposta para solicitação de reembolso."""

    id: UUID
    code: str
    title: str
    description: str | None
    requester_id: UUID
    expense_date_start: date
    expense_date_end: date
    total_amount: Decimal
    approved_amount: Decimal
    paid_amount: Decimal
    status: str
    approval_level: str | None
    submitted_at: datetime | None
    approved_by: UUID | None
    approved_at: datetime | None
    rejection_reason: str | None
    payable_account_id: UUID | None
    processed_at: datetime | None
    processed_by: UUID | None
    bank_code: str | None
    bank_agency: str | None
    bank_account: str | None
    pix_key: str | None
    cost_center: str | None
    project: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    # Itens e anexos
    items: list[ReimbursementItemResponse] = Field(default_factory=list)
    attachments: list[ReimbursementAttachmentResponse] = Field(default_factory=list)

    # Computed fields
    items_count: int = 0
    attachments_count: int = 0
    can_edit: bool = False
    can_submit: bool = False
    can_approve: bool = False
    can_process: bool = False

    model_config = {"from_attributes": True}


class ReimbursementRequestListResponse(BaseModel):
    """Schema de resposta para listagem (sem itens detalhados)."""

    id: UUID
    code: str
    title: str
    requester_id: UUID
    expense_date_start: date
    expense_date_end: date
    total_amount: Decimal
    approved_amount: Decimal
    status: str
    approval_level: str | None
    submitted_at: datetime | None
    approved_at: datetime | None
    items_count: int = 0
    attachments_count: int = 0
    can_edit: bool = False
    can_submit: bool = False
    can_approve: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class ReimbursementRequestFilter(BaseModel):
    """Schema para filtros de listagem."""

    status: str | None = None
    approval_level: str | None = None
    requester_id: UUID | None = None
    expense_date_start: date | None = None
    expense_date_end: date | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    search: str | None = None
    cost_center: str | None = None
    project: str | None = None


class ReimbursementRequestStats(BaseModel):
    """Schema para estatísticas de reembolsos."""

    total: int = 0
    by_status: dict = Field(default_factory=dict)
    by_approval_level: dict = Field(default_factory=dict)
    total_amount: Decimal = Decimal("0.00")
    total_approved: Decimal = Decimal("0.00")
    total_paid: Decimal = Decimal("0.00")
    pending_count: int = 0
    pending_amount: Decimal = Decimal("0.00")
    approved_count: int = 0
    approved_amount: Decimal = Decimal("0.00")


class ReimbursementSubmitRequest(BaseModel):
    """Schema para submissão de solicitação."""

    notes: str | None = None


class ReimbursementApproveRequest(BaseModel):
    """Schema para aprovação de solicitação."""

    comments: str | None = None
    approved_items: list[UUID] | None = None  # IDs dos itens a aprovar
    rejected_items: dict | None = None  # {item_id: reason}


class ReimbursementRejectRequest(BaseModel):
    """Schema para rejeição de solicitação."""

    reason: str = Field(..., min_length=10, max_length=1000)


class ReimbursementReturnRequest(BaseModel):
    """Schema para devolução ao rascunho."""

    reason: str = Field(..., min_length=10, max_length=1000)


class ReimbursementProcessRequest(BaseModel):
    """Schema para processamento (geração de conta a pagar)."""

    due_date: date | None = None  # Data de vencimento da conta a pagar
    notes: str | None = None


class PaginatedReimbursementResponse(BaseModel):
    """Schema para resposta paginada."""

    items: list[ReimbursementRequestListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
