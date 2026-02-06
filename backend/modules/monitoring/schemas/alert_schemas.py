"""
Schemas para alertas do Early Warning System.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..models.alert import AlertLevel, AlertStatus


class AlertBase(BaseModel):
    """Base para schemas de alerta."""

    metric_name: str = Field(..., max_length=100)
    source: str = Field(default="system", max_length=100)
    level: AlertLevel = Field(default=AlertLevel.YELLOW)
    current_value: float
    threshold_value: float
    title: str = Field(..., max_length=200)
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class AlertCreate(AlertBase):
    """Schema para criacao de alerta."""

    threshold_id: Optional[UUID] = None


class AlertResponse(AlertBase):
    """Schema de resposta de alerta."""

    id: UUID
    status: AlertStatus
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[UUID] = None
    resolved_by: Optional[UUID] = None
    resolution_notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertAcknowledge(BaseModel):
    """Schema para reconhecer alerta."""

    notes: Optional[str] = Field(None, max_length=1000)


class AlertResolve(BaseModel):
    """Schema para resolver alerta."""

    notes: Optional[str] = Field(None, max_length=2000)


class AlertsListResponse(BaseModel):
    """Resposta de lista de alertas."""

    total: int
    active: int
    critical: int
    alerts: List[AlertResponse]


class AlertStats(BaseModel):
    """Estatisticas de alertas."""

    total_24h: int = 0
    total_7d: int = 0
    by_level: Dict[str, int] = Field(default_factory=dict)
    by_status: Dict[str, int] = Field(default_factory=dict)
    by_metric: Dict[str, int] = Field(default_factory=dict)
    mttr_seconds: float = 0  # Mean Time To Resolve
    escalation_rate: float = 0
