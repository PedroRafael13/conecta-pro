"""Schemas Pydantic para solicitações de reembolso."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.reimbursement.models.reimbursement_request import (
    ApprovalLevel,
    ReimbursementStatus,
)
from modules.reimbursement.schemas.reimbursement_item import (
    ReimbursementItemCreate,
    ReimbursementItemResponse,
)
from modules.reimbursement.schemas.reimbursement_attachment import (
    ReimbursementAttachmentResponse,
)


class ReimbursementRequestBase(BaseModel):
    """Base schema para solicitação de reembolso."""

    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    expense_date_start: date
    expense_date_end: date
    cost_center: Optional[str] = Field(None, max_length=50)
    project: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

    # Dados bancários (opcional na criação)
    bank_code: Optional[str] = Field(None, max_length=10)
    bank_agency: Optional[str] = Field(None, max_length=10)
    bank_account: Optional[str] = Field(None, max_length=20)
    pix_key: Optional[str] = Field(None, max_length=100)

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

    items: Optional[List[ReimbursementItemCreate]] = Field(default_factory=list)


class ReimbursementRequestUpdate(BaseModel):
    """Schema para atualização de solicitação de reembolso."""

    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    expense_date_start: Optional[date] = None
    expense_date_end: Optional[date] = None
    cost_center: Optional[str] = Field(None, max_length=50)
    project: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    bank_code: Optional[str] = Field(None, max_length=10)
    bank_agency: Optional[str] = Field(None, max_length=10)
    bank_account: Optional[str] = Field(None, max_length=20)
    pix_key: Optional[str] = Field(None, max_length=100)


class ReimbursementRequestResponse(BaseModel):
    """Schema de resposta para solicitação de reembolso."""

    id: UUID
    code: str
    title: str
    description: Optional[str]
    requester_id: UUID
    expense_date_start: date
    expense_date_end: date
    total_amount: Decimal
    approved_amount: Decimal
    paid_amount: Decimal
    status: str
    approval_level: Optional[str]
    submitted_at: Optional[datetime]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    payable_account_id: Optional[UUID]
    processed_at: Optional[datetime]
    processed_by: Optional[UUID]
    bank_code: Optional[str]
    bank_agency: Optional[str]
    bank_account: Optional[str]
    pix_key: Optional[str]
    cost_center: Optional[str]
    project: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool

    # Itens e anexos
    items: List[ReimbursementItemResponse] = Field(default_factory=list)
    attachments: List[ReimbursementAttachmentResponse] = Field(default_factory=list)

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
    approval_level: Optional[str]
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    items_count: int = 0
    attachments_count: int = 0
    can_edit: bool = False
    can_submit: bool = False
    can_approve: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class ReimbursementRequestFilter(BaseModel):
    """Schema para filtros de listagem."""

    status: Optional[str] = None
    approval_level: Optional[str] = None
    requester_id: Optional[UUID] = None
    expense_date_start: Optional[date] = None
    expense_date_end: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    search: Optional[str] = None
    cost_center: Optional[str] = None
    project: Optional[str] = None


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

    notes: Optional[str] = None


class ReimbursementApproveRequest(BaseModel):
    """Schema para aprovação de solicitação."""

    comments: Optional[str] = None
    approved_items: Optional[List[UUID]] = None  # IDs dos itens a aprovar
    rejected_items: Optional[dict] = None  # {item_id: reason}


class ReimbursementRejectRequest(BaseModel):
    """Schema para rejeição de solicitação."""

    reason: str = Field(..., min_length=10, max_length=1000)


class ReimbursementReturnRequest(BaseModel):
    """Schema para devolução ao rascunho."""

    reason: str = Field(..., min_length=10, max_length=1000)


class ReimbursementProcessRequest(BaseModel):
    """Schema para processamento (geração de conta a pagar)."""

    due_date: Optional[date] = None  # Data de vencimento da conta a pagar
    notes: Optional[str] = None


class PaginatedReimbursementResponse(BaseModel):
    """Schema para resposta paginada."""

    items: List[ReimbursementRequestListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
