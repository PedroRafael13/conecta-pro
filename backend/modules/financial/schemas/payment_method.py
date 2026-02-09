"""Schemas para formas de pagamento."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.payment_method import PaymentMethodStatus, PaymentMethodType


class PaymentMethodBase(BaseModel):
    """Base para forma de pagamento."""

    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None
    payment_type: PaymentMethodType = PaymentMethodType.BOLETO

    requires_bank_account: bool = False
    requires_authorization: bool = False
    requires_document: bool = False

    bank_account_id: UUID | None = None

    days_to_process: int = Field(default=0, ge=0)
    min_value: str | None = None
    max_value: str | None = None
    daily_limit: str | None = None

    fee_percentage: str | None = None
    fee_fixed: str | None = None

    settings: dict = Field(default_factory=dict)

    display_order: int = Field(default=0, ge=0)
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=20)


class PaymentMethodCreate(PaymentMethodBase):
    """Schema para criação de forma de pagamento."""

    condominio_id: UUID


class PaymentMethodUpdate(BaseModel):
    """Schema para atualização de forma de pagamento."""

    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = None
    payment_type: PaymentMethodType | None = None
    status: PaymentMethodStatus | None = None

    requires_bank_account: bool | None = None
    requires_authorization: bool | None = None
    requires_document: bool | None = None

    bank_account_id: UUID | None = None

    days_to_process: int | None = Field(None, ge=0)
    min_value: str | None = None
    max_value: str | None = None
    daily_limit: str | None = None

    fee_percentage: str | None = None
    fee_fixed: str | None = None

    settings: dict | None = None

    display_order: int | None = Field(None, ge=0)
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=20)

    is_default: bool | None = None


class PaymentMethodResponse(PaymentMethodBase):
    """Schema de resposta para forma de pagamento."""

    id: UUID
    condominio_id: UUID
    code: str | None = None
    status: PaymentMethodStatus
    is_default: bool = False
    is_electronic: bool
    is_instant: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:  # pylint: disable=too-few-public-methods
        """Configuração do schema."""

        from_attributes = True


class PaymentMethodListResponse(BaseModel):
    """Schema de lista de formas de pagamento."""

    id: UUID
    code: str | None = None
    name: str
    payment_type: str
    status: str
    is_electronic: bool
    is_instant: bool
    days_to_process: int
    is_default: bool

    class Config:  # pylint: disable=too-few-public-methods
        """Configuração do schema."""

        from_attributes = True
