"""Schemas para cotações de compra."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.purchase_quotation import (
    DeliveryType,
    PaymentCondition,
    QuotationStatus,
)


class QuotationItemBase(BaseModel):
    """Schema base para item de cotação."""

    description: str = Field(..., min_length=1, max_length=500)
    unit_of_measure: str = Field(default="un", max_length=10)
    quantity_requested: Decimal = Field(..., gt=0)
    quantity_offered: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Decimal = Decimal("0")
    ipi_percentage: Decimal = Decimal("0")
    icms_percentage: Decimal = Decimal("0")
    delivery_days: Optional[int] = Field(None, ge=0)
    availability: Optional[str] = Field(None, max_length=50)
    supplier_code: Optional[str] = Field(None, max_length=50)
    supplier_description: Optional[str] = Field(None, max_length=500)
    technical_specs: Optional[str] = None
    notes: Optional[str] = None
    requisition_item_id: Optional[UUID] = None
    product_id: Optional[UUID] = None


class QuotationItemCreate(QuotationItemBase):
    """Schema para criar item de cotacao."""


class QuotationItemUpdate(BaseModel):
    """Schema para atualizar item de cotação."""

    description: Optional[str] = Field(None, min_length=1, max_length=500)
    quantity_offered: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = None
    ipi_percentage: Optional[Decimal] = None
    icms_percentage: Optional[Decimal] = None
    delivery_days: Optional[int] = None
    availability: Optional[str] = None
    supplier_code: Optional[str] = None
    supplier_description: Optional[str] = None
    technical_specs: Optional[str] = None
    notes: Optional[str] = None
    meets_specs: Optional[bool] = None
    evaluation_notes: Optional[str] = None


class QuotationItemResponse(QuotationItemBase):
    """Schema de resposta para item de cotação."""

    id: UUID
    quotation_id: UUID
    item_number: int
    discount_amount: Decimal = Decimal("0")
    total: Optional[Decimal] = None
    min_quantity: Optional[Decimal] = None
    meets_specs: Optional[bool] = None
    evaluation_notes: Optional[str] = None
    created_at: datetime

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


class PurchaseQuotationBase(BaseModel):
    """Schema base para cotação de compra."""

    reference: Optional[str] = Field(None, max_length=50)
    validity_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    payment_condition: PaymentCondition = PaymentCondition.DIAS_30
    payment_installments: Optional[int] = Field(None, ge=1)
    delivery_type: DeliveryType = DeliveryType.CIF
    delivery_days: Optional[int] = Field(None, ge=0)
    discount_percentage: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    freight_amount: Decimal = Decimal("0")
    insurance_amount: Decimal = Decimal("0")
    other_costs: Decimal = Decimal("0")
    ipi_amount: Decimal = Decimal("0")
    icms_amount: Decimal = Decimal("0")
    notes: Optional[str] = None
    supplier_notes: Optional[str] = None


class PurchaseQuotationCreate(PurchaseQuotationBase):
    """Schema para criar cotação."""

    condominio_id: UUID
    requisition_id: UUID
    supplier_id: UUID
    items: List[QuotationItemCreate] = Field(default=[], min_length=0)


class PurchaseQuotationUpdate(BaseModel):
    """Schema para atualizar cotação."""

    reference: Optional[str] = None
    validity_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    payment_condition: Optional[PaymentCondition] = None
    payment_installments: Optional[int] = None
    delivery_type: Optional[DeliveryType] = None
    delivery_days: Optional[int] = None
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    freight_amount: Optional[Decimal] = None
    insurance_amount: Optional[Decimal] = None
    other_costs: Optional[Decimal] = None
    ipi_amount: Optional[Decimal] = None
    icms_amount: Optional[Decimal] = None
    notes: Optional[str] = None
    supplier_notes: Optional[str] = None
    technical_score: Optional[Decimal] = Field(None, ge=0, le=100)
    commercial_score: Optional[Decimal] = Field(None, ge=0, le=100)
    delivery_score: Optional[Decimal] = Field(None, ge=0, le=100)


class PurchaseQuotationResponse(PurchaseQuotationBase):
    """Schema de resposta para cotação."""

    id: UUID
    condominio_id: UUID
    number: str
    requisition_id: UUID
    supplier_id: UUID
    status: QuotationStatus
    request_date: date
    sent_date: Optional[datetime] = None
    received_date: Optional[datetime] = None
    subtotal: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    pis_amount: Decimal = Decimal("0")
    cofins_amount: Decimal = Decimal("0")
    technical_score: Optional[Decimal] = None
    commercial_score: Optional[Decimal] = None
    delivery_score: Optional[Decimal] = None
    overall_score: Optional[Decimal] = None
    is_best_price: bool = False
    is_best_delivery: bool = False
    is_best_overall: bool = False
    selected_at: Optional[datetime] = None
    selected_by: Optional[UUID] = None
    selection_justification: Optional[str] = None
    rejection_reason: Optional[str] = None
    items: List[QuotationItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


class PurchaseQuotationListResponse(BaseModel):
    """Schema de resposta para lista de cotações."""

    items: List[PurchaseQuotationResponse]
    total: int
    page: int = 1
    page_size: int = 50


class QuotationSelectRequest(BaseModel):
    """Request para selecionar cotação vencedora."""

    justification: Optional[str] = Field(None, max_length=500)


class QuotationRejectRequest(BaseModel):
    """Request para rejeitar cotação."""

    reason: str = Field(..., min_length=5, max_length=500)


class QuotationScoreRequest(BaseModel):
    """Request para avaliar cotação."""

    technical_score: Optional[Decimal] = Field(None, ge=0, le=100)
    commercial_score: Optional[Decimal] = Field(None, ge=0, le=100)
    delivery_score: Optional[Decimal] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class QuotationComparisonResponse(BaseModel):
    """Comparação entre cotações."""

    requisition_id: UUID
    requisition_number: str
    quotations: List[Dict[str, Any]] = []
    best_price: Optional[UUID] = None
    best_delivery: Optional[UUID] = None
    best_overall: Optional[UUID] = None
    recommendation: Optional[str] = None


class QuotationStats(BaseModel):
    """Estatísticas de cotações."""

    total: int = 0
    by_status: Dict[str, int] = {}
    pending_response: int = 0
    expired: int = 0
    average_response_days: Optional[float] = None
    average_discount_percentage: Optional[float] = None
