"""Schemas Pydantic para itens de reembolso."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ReimbursementItemBase(BaseModel):
    """Base schema para item de reembolso."""

    category_type: str = Field(..., max_length=30)
    description: str = Field(..., min_length=3, max_length=500)
    merchant: Optional[str] = Field(None, max_length=200)
    expense_date: date
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    document_type: Optional[str] = Field(None, max_length=30)
    document_number: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Valida que o valor é positivo."""
        if v <= 0:
            raise ValueError("Valor deve ser maior que zero")
        return v


class ReimbursementItemCreate(ReimbursementItemBase):
    """Schema para criação de item de reembolso."""

    category_id: Optional[UUID] = None


class ReimbursementItemUpdate(BaseModel):
    """Schema para atualização de item de reembolso."""

    category_type: Optional[str] = Field(None, max_length=30)
    category_id: Optional[UUID] = None
    description: Optional[str] = Field(None, min_length=3, max_length=500)
    merchant: Optional[str] = Field(None, max_length=200)
    expense_date: Optional[date] = None
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    document_type: Optional[str] = Field(None, max_length=30)
    document_number: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class ReimbursementItemApprove(BaseModel):
    """Schema para aprovação individual de item."""

    approved_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)


class ReimbursementItemReject(BaseModel):
    """Schema para rejeição individual de item."""

    reason: str = Field(..., min_length=5, max_length=500)


class ReimbursementItemResponse(BaseModel):
    """Schema de resposta para item de reembolso."""

    id: UUID
    request_id: UUID
    category_id: Optional[UUID]
    category_type: str
    category_label: str = ""
    description: str
    merchant: Optional[str]
    expense_date: date
    amount: Decimal
    approved_amount: Optional[Decimal]
    document_type: Optional[str]
    document_number: Optional[str]
    is_approved: bool
    rejection_reason: Optional[str]
    has_attachment: bool = False
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}


class ReimbursementItemBulkCreate(BaseModel):
    """Schema para criação em lote de itens."""

    items: List[ReimbursementItemCreate] = Field(..., min_length=1)
