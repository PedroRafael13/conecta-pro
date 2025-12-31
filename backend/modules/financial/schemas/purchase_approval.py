"""Schemas para aprovações de compra."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.purchase_approval import (
    ApprovalAction,
    ApprovalLevel,
    ApprovalStatus,
    ApprovalType,
)


class PurchaseApprovalBase(BaseModel):
    """Schema base para aprovação de compra."""

    approval_type: ApprovalType
    document_id: UUID
    document_number: Optional[str] = Field(None, max_length=50)
    approval_level: ApprovalLevel
    document_total: Optional[Decimal] = Field(None, ge=0)
    deadline: Optional[datetime] = None


class PurchaseApprovalCreate(PurchaseApprovalBase):
    """Schema para criar aprovação."""

    condominio_id: UUID
    approver_id: UUID
    approver_role: Optional[str] = Field(None, max_length=50)
    sequence: int = 1


class PurchaseApprovalUpdate(BaseModel):
    """Schema para atualizar aprovação."""

    deadline: Optional[datetime] = None
    approver_id: Optional[UUID] = None


class PurchaseApprovalResponse(PurchaseApprovalBase):
    """Schema de resposta para aprovação."""

    id: UUID
    condominio_id: UUID
    sequence: int = 1
    status: ApprovalStatus
    approver_id: UUID
    approver_role: Optional[str] = None
    original_approver_id: Optional[UUID] = None
    delegated_by: Optional[UUID] = None
    delegation_reason: Optional[str] = None
    delegated_at: Optional[datetime] = None
    requested_at: datetime
    responded_at: Optional[datetime] = None
    response_time_hours: Optional[Decimal] = None
    action: Optional[ApprovalAction] = None
    comments: Optional[str] = None
    rejection_reason: Optional[str] = None
    info_requested: Optional[str] = None
    info_provided: Optional[str] = None
    notification_sent: bool = False
    reminder_count: int = 0
    action_history: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PurchaseApprovalListResponse(BaseModel):
    """Schema de resposta para lista de aprovações."""

    items: List[PurchaseApprovalResponse]
    total: int
    page: int = 1
    page_size: int = 50


class ApprovalApproveRequest(BaseModel):
    """Request para aprovar."""

    comments: Optional[str] = Field(None, max_length=500)


class ApprovalRejectRequest(BaseModel):
    """Request para rejeitar."""

    reason: str = Field(..., min_length=5, max_length=500)
    comments: Optional[str] = Field(None, max_length=500)


class ApprovalDelegateRequest(BaseModel):
    """Request para delegar."""

    new_approver_id: UUID
    reason: str = Field(..., min_length=5, max_length=500)


class ApprovalInfoRequest(BaseModel):
    """Request para solicitar informações."""

    info_request: str = Field(..., min_length=5, max_length=1000)


class ApprovalInfoProvideRequest(BaseModel):
    """Request para fornecer informações."""

    info: str = Field(..., min_length=5, max_length=1000)


class ApprovalStats(BaseModel):
    """Estatísticas de aprovações."""

    total: int = 0
    by_status: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    by_level: Dict[str, int] = {}
    pending: int = 0
    overdue: int = 0
    average_response_hours: Optional[float] = None
    approval_rate: Optional[float] = None


class ApprovalFilter(BaseModel):
    """Filtros para busca de aprovações."""

    status: Optional[List[ApprovalStatus]] = None
    approval_type: Optional[List[ApprovalType]] = None
    approval_level: Optional[List[ApprovalLevel]] = None
    approver_id: Optional[UUID] = None
    document_id: Optional[UUID] = None
    is_overdue: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class MyApprovalsResponse(BaseModel):
    """Minhas aprovações pendentes."""

    pending: List[PurchaseApprovalResponse] = []
    recent: List[PurchaseApprovalResponse] = []
    overdue: List[PurchaseApprovalResponse] = []
    total_pending: int = 0
    total_overdue: int = 0


class ApprovalWorkflowConfig(BaseModel):
    """Configuração de workflow de aprovação."""

    approval_type: ApprovalType
    levels: List[Dict[str, Any]] = []
    # [{level: "operacional", min_value: 0, max_value: 1000, approvers: [uuid1, uuid2]}]
    sequential: bool = True  # Aprovação sequencial ou paralela
    require_all: bool = False  # Requer todos aprovarem (paralelo)
    auto_approve_below: Optional[Decimal] = None  # Auto-aprovar abaixo deste valor
    deadline_hours: int = 48  # Prazo padrão em horas
