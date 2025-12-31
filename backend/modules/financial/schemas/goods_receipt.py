"""Schemas para recebimento de mercadorias."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.goods_receipt import InspectionResult, ReceiptStatus, ReceiptType


class ReceiptItemBase(BaseModel):
    """Schema base para item de recebimento."""

    description: str = Field(..., min_length=1, max_length=500)
    unit_of_measure: str = Field(default="un", max_length=10)
    quantity_expected: Decimal = Field(..., gt=0)
    quantity_received: Decimal = Field(default=Decimal("0"), ge=0)
    quantity_accepted: Decimal = Field(default=Decimal("0"), ge=0)
    quantity_rejected: Decimal = Field(default=Decimal("0"), ge=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    batch_number: Optional[str] = Field(None, max_length=50)
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    serial_numbers: List[str] = []
    storage_location: Optional[str] = Field(None, max_length=100)
    storage_position: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    order_item_id: Optional[UUID] = None
    product_id: Optional[UUID] = None


class ReceiptItemCreate(ReceiptItemBase):
    """Schema para criar item de recebimento."""

    pass


class ReceiptItemUpdate(BaseModel):
    """Schema para atualizar item de recebimento."""

    quantity_received: Optional[Decimal] = Field(None, ge=0)
    quantity_accepted: Optional[Decimal] = Field(None, ge=0)
    quantity_rejected: Optional[Decimal] = Field(None, ge=0)
    batch_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    serial_numbers: Optional[List[str]] = None
    storage_location: Optional[str] = None
    storage_position: Optional[str] = None
    inspection_result: Optional[InspectionResult] = None
    inspection_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None


class ReceiptItemResponse(ReceiptItemBase):
    """Schema de resposta para item de recebimento."""

    id: UUID
    receipt_id: UUID
    item_number: int
    quantity_difference: Decimal = Decimal("0")
    expected_total: Optional[Decimal] = None
    received_total: Optional[Decimal] = None
    accepted_total: Optional[Decimal] = None
    rejected_total: Optional[Decimal] = None
    inspection_result: Optional[InspectionResult] = None
    inspection_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GoodsReceiptBase(BaseModel):
    """Schema base para recebimento de mercadorias."""

    receipt_type: ReceiptType = ReceiptType.NORMAL
    expected_date: Optional[date] = None
    invoice_number: Optional[str] = Field(None, max_length=50)
    invoice_series: Optional[str] = Field(None, max_length=10)
    invoice_date: Optional[date] = None
    invoice_key: Optional[str] = Field(None, max_length=50)
    invoice_total: Optional[Decimal] = Field(None, ge=0)
    carrier: Optional[str] = Field(None, max_length=200)
    carrier_cnpj: Optional[str] = Field(None, max_length=18)
    vehicle_plate: Optional[str] = Field(None, max_length=10)
    driver_name: Optional[str] = Field(None, max_length=100)
    driver_document: Optional[str] = Field(None, max_length=20)
    seal_number: Optional[str] = Field(None, max_length=50)
    volumes: Optional[int] = Field(None, ge=0)
    gross_weight: Optional[Decimal] = Field(None, ge=0)
    net_weight: Optional[Decimal] = Field(None, ge=0)
    storage_location: Optional[str] = Field(None, max_length=100)
    storage_notes: Optional[str] = None
    notes: Optional[str] = None


class GoodsReceiptCreate(GoodsReceiptBase):
    """Schema para criar recebimento."""

    condominio_id: UUID
    order_id: UUID
    supplier_id: UUID
    items: List[ReceiptItemCreate] = Field(..., min_length=1)


class GoodsReceiptUpdate(BaseModel):
    """Schema para atualizar recebimento."""

    receipt_type: Optional[ReceiptType] = None
    invoice_number: Optional[str] = None
    invoice_series: Optional[str] = None
    invoice_date: Optional[date] = None
    invoice_key: Optional[str] = None
    invoice_total: Optional[Decimal] = None
    carrier: Optional[str] = None
    carrier_cnpj: Optional[str] = None
    vehicle_plate: Optional[str] = None
    driver_name: Optional[str] = None
    driver_document: Optional[str] = None
    seal_number: Optional[str] = None
    volumes: Optional[int] = None
    gross_weight: Optional[Decimal] = None
    net_weight: Optional[Decimal] = None
    storage_location: Optional[str] = None
    storage_notes: Optional[str] = None
    notes: Optional[str] = None


class GoodsReceiptResponse(GoodsReceiptBase):
    """Schema de resposta para recebimento."""

    id: UUID
    condominio_id: UUID
    number: str
    order_id: UUID
    supplier_id: UUID
    status: ReceiptStatus
    receipt_date: date
    inspection_date: Optional[datetime] = None
    approval_date: Optional[datetime] = None
    total_expected: Decimal = Decimal("0")
    total_received: Decimal = Decimal("0")
    total_accepted: Decimal = Decimal("0")
    total_rejected: Decimal = Decimal("0")
    total_difference: Decimal = Decimal("0")
    inspection_result: Optional[InspectionResult] = None
    inspection_notes: Optional[str] = None
    inspected_by: Optional[UUID] = None
    has_divergence: bool = False
    divergence_type: Optional[str] = None
    divergence_description: Optional[str] = None
    divergence_action: Optional[str] = None
    approved_by: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_document: Optional[str] = None
    received_at: Optional[datetime] = None
    items: List[ReceiptItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GoodsReceiptListResponse(BaseModel):
    """Schema de resposta para lista de recebimentos."""

    items: List[GoodsReceiptResponse]
    total: int
    page: int = 1
    page_size: int = 50


class ReceiptInspectionRequest(BaseModel):
    """Request para iniciar/concluir inspeção."""

    result: InspectionResult
    notes: Optional[str] = Field(None, max_length=1000)


class ReceiptApproveRequest(BaseModel):
    """Request para aprovar recebimento."""

    notes: Optional[str] = Field(None, max_length=500)


class ReceiptRejectRequest(BaseModel):
    """Request para recusar recebimento."""

    reason: str = Field(..., min_length=5, max_length=500)


class ReceiptDivergenceRequest(BaseModel):
    """Request para registrar divergência."""

    divergence_type: str = Field(..., max_length=50)
    description: str = Field(..., min_length=5, max_length=1000)
    action: Optional[str] = Field(None, max_length=50)


class ReceiptSignRequest(BaseModel):
    """Request para assinar recebimento."""

    receiver_name: str = Field(..., min_length=2, max_length=100)
    receiver_document: str = Field(..., min_length=5, max_length=20)
    signature: Optional[str] = None


class ReceiptStats(BaseModel):
    """Estatísticas de recebimentos."""

    total: int = 0
    by_status: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    pending_inspection: int = 0
    with_divergence: int = 0
    total_received_value: Decimal = Decimal("0")
    acceptance_rate: Optional[float] = None
    average_inspection_hours: Optional[float] = None


class ReceiptFilter(BaseModel):
    """Filtros para busca de recebimentos."""

    status: Optional[List[ReceiptStatus]] = None
    receipt_type: Optional[List[ReceiptType]] = None
    order_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    has_divergence: Optional[bool] = None
    search: Optional[str] = None
