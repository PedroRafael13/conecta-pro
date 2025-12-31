"""Schemas para requisições de compra."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.purchase_requisition import (
    RequisitionPriority,
    RequisitionStatus,
    RequisitionType,
)


class RequisitionItemBase(BaseModel):
    """Schema base para item de requisição."""

    description: str = Field(..., min_length=1, max_length=500)
    specifications: Optional[str] = None
    unit_of_measure: str = Field(default="un", max_length=10)
    quantity_requested: Decimal = Field(..., gt=0)
    estimated_unit_price: Optional[Decimal] = Field(None, ge=0)
    product_id: Optional[UUID] = None
    notes: Optional[str] = None


class RequisitionItemCreate(RequisitionItemBase):
    """Schema para criar item de requisição."""

    pass


class RequisitionItemUpdate(BaseModel):
    """Schema para atualizar item de requisição."""

    description: Optional[str] = Field(None, min_length=1, max_length=500)
    specifications: Optional[str] = None
    unit_of_measure: Optional[str] = None
    quantity_requested: Optional[Decimal] = Field(None, gt=0)
    quantity_approved: Optional[Decimal] = Field(None, ge=0)
    estimated_unit_price: Optional[Decimal] = Field(None, ge=0)
    product_id: Optional[UUID] = None
    notes: Optional[str] = None


class RequisitionItemResponse(RequisitionItemBase):
    """Schema de resposta para item de requisição."""

    id: UUID
    requisition_id: UUID
    item_number: int
    quantity_approved: Optional[Decimal] = None
    quantity_ordered: Decimal = Decimal("0")
    quantity_received: Decimal = Decimal("0")
    estimated_total: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseRequisitionBase(BaseModel):
    """Schema base para requisição de compra."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    justification: Optional[str] = None
    requisition_type: RequisitionType = RequisitionType.MATERIAL
    priority: RequisitionPriority = RequisitionPriority.MEDIA
    needed_by_date: Optional[date] = None
    department: Optional[str] = Field(None, max_length=100)
    cost_center: Optional[str] = Field(None, max_length=50)
    min_quotations: int = Field(default=3, ge=1, le=10)
    quotation_deadline: Optional[date] = None
    delivery_address: Optional[str] = None
    delivery_contact: Optional[str] = Field(None, max_length=100)
    delivery_phone: Optional[str] = Field(None, max_length=20)
    delivery_instructions: Optional[str] = None
    suggested_supplier_id: Optional[UUID] = None
    supplier_justification: Optional[str] = None
    notes: Optional[str] = None


class PurchaseRequisitionCreate(PurchaseRequisitionBase):
    """Schema para criar requisição."""

    condominio_id: UUID
    requester_id: UUID
    items: List[RequisitionItemCreate] = Field(default=[], min_length=0)


class PurchaseRequisitionUpdate(BaseModel):
    """Schema para atualizar requisição."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    justification: Optional[str] = None
    requisition_type: Optional[RequisitionType] = None
    priority: Optional[RequisitionPriority] = None
    needed_by_date: Optional[date] = None
    department: Optional[str] = None
    cost_center: Optional[str] = None
    min_quotations: Optional[int] = None
    quotation_deadline: Optional[date] = None
    delivery_address: Optional[str] = None
    delivery_contact: Optional[str] = None
    delivery_phone: Optional[str] = None
    delivery_instructions: Optional[str] = None
    suggested_supplier_id: Optional[UUID] = None
    supplier_justification: Optional[str] = None
    notes: Optional[str] = None


class PurchaseRequisitionResponse(PurchaseRequisitionBase):
    """Schema de resposta para requisição."""

    id: UUID
    condominio_id: UUID
    number: str
    revision: int = 1
    status: RequisitionStatus
    requester_id: UUID
    request_date: date
    estimated_total: Decimal = Decimal("0")
    approved_budget: Optional[Decimal] = None
    actual_total: Decimal = Decimal("0")
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    items: List[RequisitionItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PurchaseRequisitionListResponse(BaseModel):
    """Schema de resposta para lista de requisições."""

    items: List[PurchaseRequisitionResponse]
    total: int
    page: int = 1
    page_size: int = 50


class RequisitionApproveRequest(BaseModel):
    """Request para aprovar requisição."""

    comment: Optional[str] = Field(None, max_length=500)
    approved_budget: Optional[Decimal] = Field(None, ge=0)


class RequisitionRejectRequest(BaseModel):
    """Request para rejeitar requisição."""

    reason: str = Field(..., min_length=5, max_length=500)
    comment: Optional[str] = Field(None, max_length=500)


class RequisitionCancelRequest(BaseModel):
    """Request para cancelar requisição."""

    reason: str = Field(..., min_length=5, max_length=500)


class RequisitionStats(BaseModel):
    """Estatísticas de requisições."""

    total: int = 0
    by_status: Dict[str, int] = {}
    by_priority: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    pending_approval: int = 0
    overdue: int = 0
    total_estimated: Decimal = Decimal("0")
    average_approval_time_hours: Optional[float] = None


class RequisitionFilter(BaseModel):
    """Filtros para busca de requisições."""

    status: Optional[List[RequisitionStatus]] = None
    priority: Optional[List[RequisitionPriority]] = None
    requisition_type: Optional[List[RequisitionType]] = None
    requester_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    needed_by_from: Optional[date] = None
    needed_by_to: Optional[date] = None
    search: Optional[str] = None
