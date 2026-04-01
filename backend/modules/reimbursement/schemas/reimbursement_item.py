"""Schemas Pydantic para itens de reembolso."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ReimbursementItemBase(BaseModel):
    """Base schema para item de reembolso."""

    category_type: str = Field(..., max_length=30)
    description: str = Field(..., min_length=3, max_length=500)
    merchant: str | None = Field(None, max_length=200)
    expense_date: date
    amount: Decimal = Field(..., gt=0)
    document_type: str | None = Field(None, max_length=30)
    document_number: str | None = Field(None, max_length=50)
    notes: str | None = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Valida que o valor é positivo."""
        if v <= 0:
            raise ValueError("Valor deve ser maior que zero")
        return v


class ReimbursementItemCreate(ReimbursementItemBase):
    """Schema para criação de item de reembolso."""

    category_id: UUID | None = None


class ReimbursementItemUpdate(BaseModel):
    """Schema para atualização de item de reembolso."""

    category_type: str | None = Field(None, max_length=30)
    category_id: UUID | None = None
    description: str | None = Field(None, min_length=3, max_length=500)
    merchant: str | None = Field(None, max_length=200)
    expense_date: date | None = None
    amount: Decimal | None = Field(None, gt=0)
    document_type: str | None = Field(None, max_length=30)
    document_number: str | None = Field(None, max_length=50)
    notes: str | None = None


class ReimbursementItemApprove(BaseModel):
    """Schema para aprovação individual de item."""

    approved_amount: Decimal | None = Field(None, ge=0)


class ReimbursementItemReject(BaseModel):
    """Schema para rejeição individual de item."""

    reason: str = Field(..., min_length=5, max_length=500)


class ReimbursementItemResponse(BaseModel):
    """Schema de resposta para item de reembolso."""

    id: UUID
    request_id: UUID
    category_id: UUID | None
    category_type: str
    category_label: str = ""
    description: str
    merchant: str | None
    expense_date: date
    amount: Decimal
    approved_amount: Decimal | None
    document_type: str | None
    document_number: str | None
    is_approved: bool
    rejection_reason: str | None
    has_attachment: bool = False
    notes: str | None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}


class ReimbursementItemBulkCreate(BaseModel):
    """Schema para criação em lote de itens."""

    items: list[ReimbursementItemCreate] = Field(..., min_length=1)
