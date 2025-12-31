"""Schemas para formas de pagamento."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.payment_method import PaymentMethodStatus, PaymentMethodType


class PaymentMethodBase(BaseModel):
    """Base para forma de pagamento."""

    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    payment_type: PaymentMethodType = PaymentMethodType.BOLETO

    requires_bank_account: bool = False
    requires_authorization: bool = False
    requires_document: bool = False

    bank_account_id: Optional[UUID] = None

    days_to_process: int = Field(default=0, ge=0)
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    daily_limit: Optional[str] = None

    fee_percentage: Optional[str] = None
    fee_fixed: Optional[str] = None

    settings: dict = Field(default_factory=dict)

    display_order: int = Field(default=0, ge=0)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)


class PaymentMethodCreate(PaymentMethodBase):
    """Schema para criação de forma de pagamento."""

    condominio_id: UUID


class PaymentMethodUpdate(BaseModel):
    """Schema para atualização de forma de pagamento."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    payment_type: Optional[PaymentMethodType] = None
    status: Optional[PaymentMethodStatus] = None

    requires_bank_account: Optional[bool] = None
    requires_authorization: Optional[bool] = None
    requires_document: Optional[bool] = None

    bank_account_id: Optional[UUID] = None

    days_to_process: Optional[int] = Field(None, ge=0)
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    daily_limit: Optional[str] = None

    fee_percentage: Optional[str] = None
    fee_fixed: Optional[str] = None

    settings: Optional[dict] = None

    display_order: Optional[int] = Field(None, ge=0)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)

    is_default: Optional[bool] = None


class PaymentMethodResponse(PaymentMethodBase):
    """Schema de resposta para forma de pagamento."""

    id: UUID
    condominio_id: UUID
    code: Optional[str] = None
    status: PaymentMethodStatus
    is_default: bool = False
    is_electronic: bool
    is_instant: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Configuração do schema."""

        from_attributes = True


class PaymentMethodListResponse(BaseModel):
    """Schema de lista de formas de pagamento."""

    id: UUID
    code: Optional[str] = None
    name: str
    payment_type: str
    status: str
    is_electronic: bool
    is_instant: bool
    days_to_process: int
    is_default: bool

    class Config:
        """Configuração do schema."""

        from_attributes = True
