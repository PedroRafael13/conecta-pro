"""Schemas para ordens de compra."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.purchase_order import OrderPriority, OrderStatus


class OrderItemBase(BaseModel):
    """Schema base para item de ordem de compra."""

    description: str = Field(..., min_length=1, max_length=500)
    unit_of_measure: str = Field(default="un", max_length=10)
    quantity_ordered: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount_percentage: Decimal = Decimal("0")
    ipi_percentage: Decimal = Decimal("0")
    icms_percentage: Decimal = Decimal("0")
    expected_delivery_date: date | None = None
    supplier_code: str | None = Field(None, max_length=50)
    notes: str | None = None
    quotation_item_id: UUID | None = None
    requisition_item_id: UUID | None = None
    product_id: UUID | None = None


class OrderItemCreate(OrderItemBase):
    """Schema para criar item de ordem."""


class OrderItemUpdate(BaseModel):
    """Schema para atualizar item de ordem."""

    description: str | None = Field(None, min_length=1, max_length=500)
    quantity_ordered: Decimal | None = Field(None, gt=0)
    unit_price: Decimal | None = Field(None, ge=0)
    discount_percentage: Decimal | None = None
    ipi_percentage: Decimal | None = None
    icms_percentage: Decimal | None = None
    expected_delivery_date: date | None = None
    supplier_code: str | None = None
    notes: str | None = None


class OrderItemResponse(OrderItemBase):
    """Schema de resposta para item de ordem."""

    id: UUID
    order_id: UUID
    item_number: int
    discount_amount: Decimal = Decimal("0")
    total: Decimal
    ipi_amount: Decimal = Decimal("0")
    icms_amount: Decimal = Decimal("0")
    quantity_received: Decimal = Decimal("0")
    quantity_invoiced: Decimal = Decimal("0")
    quantity_returned: Decimal = Decimal("0")
    actual_delivery_date: date | None = None
    created_at: datetime

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


class PurchaseOrderBase(BaseModel):
    """Schema base para ordem de compra."""

    priority: OrderPriority = OrderPriority.NORMAL
    expected_delivery_date: date | None = None
    payment_condition: str | None = Field(None, max_length=20)
    payment_installments: int | None = Field(None, ge=1)
    delivery_type: str | None = Field(None, max_length=20)
    discount_percentage: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    freight_amount: Decimal = Decimal("0")
    insurance_amount: Decimal = Decimal("0")
    other_costs: Decimal = Decimal("0")
    delivery_address: str | None = None
    delivery_contact: str | None = Field(None, max_length=100)
    delivery_phone: str | None = Field(None, max_length=20)
    delivery_instructions: str | None = None
    billing_address: str | None = None
    billing_contact: str | None = Field(None, max_length=100)
    notes: str | None = None


class PurchaseOrderCreate(PurchaseOrderBase):
    """Schema para criar ordem de compra."""

    condominio_id: UUID
    supplier_id: UUID
    quotation_id: UUID | None = None
    requisition_id: UUID | None = None
    items: list[OrderItemCreate] = Field(..., min_length=1)


class PurchaseOrderUpdate(BaseModel):
    """Schema para atualizar ordem de compra."""

    priority: OrderPriority | None = None
    expected_delivery_date: date | None = None
    payment_condition: str | None = None
    payment_installments: int | None = None
    delivery_type: str | None = None
    discount_percentage: Decimal | None = None
    discount_amount: Decimal | None = None
    freight_amount: Decimal | None = None
    insurance_amount: Decimal | None = None
    other_costs: Decimal | None = None
    delivery_address: str | None = None
    delivery_contact: str | None = None
    delivery_phone: str | None = None
    delivery_instructions: str | None = None
    notes: str | None = None
    supplier_notes: str | None = None


class PurchaseOrderResponse(PurchaseOrderBase):
    """Schema de resposta para ordem de compra."""

    id: UUID
    condominio_id: UUID
    number: str
    revision: int = 1
    status: OrderStatus
    supplier_id: UUID
    quotation_id: UUID | None = None
    requisition_id: UUID | None = None
    order_date: date
    approval_date: datetime | None = None
    sent_date: datetime | None = None
    confirmed_date: datetime | None = None
    actual_delivery_date: date | None = None
    subtotal: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    ipi_amount: Decimal = Decimal("0")
    icms_amount: Decimal = Decimal("0")
    icms_st_amount: Decimal = Decimal("0")
    pis_amount: Decimal = Decimal("0")
    cofins_amount: Decimal = Decimal("0")
    received_total: Decimal = Decimal("0")
    invoiced_total: Decimal = Decimal("0")
    paid_total: Decimal = Decimal("0")
    approved_by: UUID | None = None
    supplier_notes: str | None = None
    rejection_reason: str | None = None
    cancellation_reason: str | None = None
    payable_account_id: UUID | None = None
    items: list[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime | None = None

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


class PurchaseOrderListResponse(BaseModel):
    """Schema de resposta para lista de ordens."""

    items: list[PurchaseOrderResponse]
    total: int
    page: int = 1
    page_size: int = 50


class OrderApproveRequest(BaseModel):
    """Request para aprovar ordem."""

    notes: str | None = Field(None, max_length=500)


class OrderRejectRequest(BaseModel):
    """Request para rejeitar ordem."""

    reason: str = Field(..., min_length=5, max_length=500)


class OrderCancelRequest(BaseModel):
    """Request para cancelar ordem."""

    reason: str = Field(..., min_length=5, max_length=500)


class OrderReceiveRequest(BaseModel):
    """Request para registrar recebimento parcial."""

    amount: Decimal = Field(..., gt=0)
    notes: str | None = None


class OrderInvoiceRequest(BaseModel):
    """Request para registrar fatura."""

    invoice_total: Decimal = Field(..., gt=0)
    invoice_number: str | None = None
    invoice_date: date | None = None


class OrderPaymentRequest(BaseModel):
    """Request para registrar pagamento."""

    paid_amount: Decimal = Field(..., gt=0)
    payment_date: date | None = None
    notes: str | None = None


class OrderStats(BaseModel):
    """Estatísticas de ordens de compra."""

    total: int = 0
    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    pending_approval: int = 0
    pending_delivery: int = 0
    overdue: int = 0
    total_amount: Decimal = Decimal("0")
    total_pending: Decimal = Decimal("0")
    average_delivery_days: float | None = None


class OrderFilter(BaseModel):
    """Filtros para busca de ordens."""

    status: list[OrderStatus] | None = None
    priority: list[OrderPriority] | None = None
    supplier_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    delivery_from: date | None = None
    delivery_to: date | None = None
    search: str | None = None
