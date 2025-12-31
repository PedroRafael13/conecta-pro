"""Schemas para ordens de compra."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
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
    expected_delivery_date: Optional[date] = None
    supplier_code: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    quotation_item_id: Optional[UUID] = None
    requisition_item_id: Optional[UUID] = None
    product_id: Optional[UUID] = None


class OrderItemCreate(OrderItemBase):
    """Schema para criar item de ordem."""

    pass


class OrderItemUpdate(BaseModel):
    """Schema para atualizar item de ordem."""

    description: Optional[str] = Field(None, min_length=1, max_length=500)
    quantity_ordered: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = None
    ipi_percentage: Optional[Decimal] = None
    icms_percentage: Optional[Decimal] = None
    expected_delivery_date: Optional[date] = None
    supplier_code: Optional[str] = None
    notes: Optional[str] = None


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
    actual_delivery_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseOrderBase(BaseModel):
    """Schema base para ordem de compra."""

    priority: OrderPriority = OrderPriority.NORMAL
    expected_delivery_date: Optional[date] = None
    payment_condition: Optional[str] = Field(None, max_length=20)
    payment_installments: Optional[int] = Field(None, ge=1)
    delivery_type: Optional[str] = Field(None, max_length=20)
    discount_percentage: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    freight_amount: Decimal = Decimal("0")
    insurance_amount: Decimal = Decimal("0")
    other_costs: Decimal = Decimal("0")
    delivery_address: Optional[str] = None
    delivery_contact: Optional[str] = Field(None, max_length=100)
    delivery_phone: Optional[str] = Field(None, max_length=20)
    delivery_instructions: Optional[str] = None
    billing_address: Optional[str] = None
    billing_contact: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    """Schema para criar ordem de compra."""

    condominio_id: UUID
    supplier_id: UUID
    quotation_id: Optional[UUID] = None
    requisition_id: Optional[UUID] = None
    items: List[OrderItemCreate] = Field(..., min_length=1)


class PurchaseOrderUpdate(BaseModel):
    """Schema para atualizar ordem de compra."""

    priority: Optional[OrderPriority] = None
    expected_delivery_date: Optional[date] = None
    payment_condition: Optional[str] = None
    payment_installments: Optional[int] = None
    delivery_type: Optional[str] = None
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    freight_amount: Optional[Decimal] = None
    insurance_amount: Optional[Decimal] = None
    other_costs: Optional[Decimal] = None
    delivery_address: Optional[str] = None
    delivery_contact: Optional[str] = None
    delivery_phone: Optional[str] = None
    delivery_instructions: Optional[str] = None
    notes: Optional[str] = None
    supplier_notes: Optional[str] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    """Schema de resposta para ordem de compra."""

    id: UUID
    condominio_id: UUID
    number: str
    revision: int = 1
    status: OrderStatus
    supplier_id: UUID
    quotation_id: Optional[UUID] = None
    requisition_id: Optional[UUID] = None
    order_date: date
    approval_date: Optional[datetime] = None
    sent_date: Optional[datetime] = None
    confirmed_date: Optional[datetime] = None
    actual_delivery_date: Optional[date] = None
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
    approved_by: Optional[UUID] = None
    supplier_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    payable_account_id: Optional[UUID] = None
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PurchaseOrderListResponse(BaseModel):
    """Schema de resposta para lista de ordens."""

    items: List[PurchaseOrderResponse]
    total: int
    page: int = 1
    page_size: int = 50


class OrderApproveRequest(BaseModel):
    """Request para aprovar ordem."""

    notes: Optional[str] = Field(None, max_length=500)


class OrderRejectRequest(BaseModel):
    """Request para rejeitar ordem."""

    reason: str = Field(..., min_length=5, max_length=500)


class OrderCancelRequest(BaseModel):
    """Request para cancelar ordem."""

    reason: str = Field(..., min_length=5, max_length=500)


class OrderReceiveRequest(BaseModel):
    """Request para registrar recebimento parcial."""

    amount: Decimal = Field(..., gt=0)
    notes: Optional[str] = None


class OrderInvoiceRequest(BaseModel):
    """Request para registrar fatura."""

    invoice_total: Decimal = Field(..., gt=0)
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None


class OrderPaymentRequest(BaseModel):
    """Request para registrar pagamento."""

    paid_amount: Decimal = Field(..., gt=0)
    payment_date: Optional[date] = None
    notes: Optional[str] = None


class OrderStats(BaseModel):
    """Estatísticas de ordens de compra."""

    total: int = 0
    by_status: Dict[str, int] = {}
    by_priority: Dict[str, int] = {}
    pending_approval: int = 0
    pending_delivery: int = 0
    overdue: int = 0
    total_amount: Decimal = Decimal("0")
    total_pending: Decimal = Decimal("0")
    average_delivery_days: Optional[float] = None


class OrderFilter(BaseModel):
    """Filtros para busca de ordens."""

    status: Optional[List[OrderStatus]] = None
    priority: Optional[List[OrderPriority]] = None
    supplier_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    delivery_from: Optional[date] = None
    delivery_to: Optional[date] = None
    search: Optional[str] = None
