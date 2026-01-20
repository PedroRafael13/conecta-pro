"""
Schemas para thresholds de metricas.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from ..models.metric_threshold import ThresholdType


class ThresholdBase(BaseModel):
    """Base para schemas de threshold."""

    metric_name: str = Field(..., max_length=100)
    display_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: str = Field(default="general", max_length=50)
    threshold_type: ThresholdType = Field(default=ThresholdType.UPPER)
    yellow_threshold: float
    orange_threshold: float
    red_threshold: float
    yellow_lower: Optional[float] = None
    orange_lower: Optional[float] = None
    red_lower: Optional[float] = None
    unit: str = Field(default="", max_length=20)
    enabled: bool = True
    cooldown_seconds: int = Field(default=300, ge=0, le=86400)
    consecutive_breaches: int = Field(default=1, ge=1, le=100)
    notify_channels: Optional[Dict[str, bool]] = None
    tags: Optional[Dict[str, Any]] = None

    @field_validator("orange_threshold")
    @classmethod
    def orange_greater_than_yellow(cls, v: float, info) -> float:
        """Valida que orange >= yellow para UPPER type."""
        if info.data.get("threshold_type") == ThresholdType.UPPER:
            yellow = info.data.get("yellow_threshold", 0)
            if v < yellow:
                raise ValueError("orange_threshold deve ser >= yellow_threshold para tipo UPPER")
        return v

    @field_validator("red_threshold")
    @classmethod
    def red_greater_than_orange(cls, v: float, info) -> float:
        """Valida que red >= orange para UPPER type."""
        if info.data.get("threshold_type") == ThresholdType.UPPER:
            orange = info.data.get("orange_threshold", 0)
            if v < orange:
                raise ValueError("red_threshold deve ser >= orange_threshold para tipo UPPER")
        return v


class ThresholdCreate(ThresholdBase):
    """Schema para criacao de threshold."""

    pass


class ThresholdUpdate(BaseModel):
    """Schema para atualizacao de threshold."""

    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    yellow_threshold: Optional[float] = None
    orange_threshold: Optional[float] = None
    red_threshold: Optional[float] = None
    yellow_lower: Optional[float] = None
    orange_lower: Optional[float] = None
    red_lower: Optional[float] = None
    unit: Optional[str] = Field(None, max_length=20)
    enabled: Optional[bool] = None
    cooldown_seconds: Optional[int] = Field(None, ge=0, le=86400)
    consecutive_breaches: Optional[int] = Field(None, ge=1, le=100)
    notify_channels: Optional[Dict[str, bool]] = None
    tags: Optional[Dict[str, Any]] = None


class ThresholdResponse(ThresholdBase):
    """Schema de resposta de threshold."""

    id: UUID
    is_active: bool
    last_alert_at: Optional[datetime] = None
    last_value: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ThresholdListResponse(BaseModel):
    """Resposta de lista de thresholds."""

    total: int
    enabled: int
    thresholds: List[ThresholdResponse]
