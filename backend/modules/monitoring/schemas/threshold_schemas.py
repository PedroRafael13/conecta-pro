"""
Schemas para thresholds de metricas.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from ..models.metric_threshold import ThresholdType


class ThresholdBase(BaseModel):
    """Base para schemas de threshold."""

    metric_name: str = Field(..., max_length=100)
    display_name: str = Field(..., max_length=200)
    description: str | None = None
    category: str = Field(default="general", max_length=50)
    threshold_type: ThresholdType = Field(default=ThresholdType.UPPER)
    yellow_threshold: float
    orange_threshold: float
    red_threshold: float
    yellow_lower: float | None = None
    orange_lower: float | None = None
    red_lower: float | None = None
    unit: str = Field(default="", max_length=20)
    enabled: bool = True
    cooldown_seconds: int = Field(default=300, ge=0, le=86400)
    consecutive_breaches: int = Field(default=1, ge=1, le=100)
    notify_channels: dict[str, bool] | None = None
    tags: dict[str, Any] | None = None

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

    display_name: str | None = Field(None, max_length=200)
    description: str | None = None
    category: str | None = Field(None, max_length=50)
    yellow_threshold: float | None = None
    orange_threshold: float | None = None
    red_threshold: float | None = None
    yellow_lower: float | None = None
    orange_lower: float | None = None
    red_lower: float | None = None
    unit: str | None = Field(None, max_length=20)
    enabled: bool | None = None
    cooldown_seconds: int | None = Field(None, ge=0, le=86400)
    consecutive_breaches: int | None = Field(None, ge=1, le=100)
    notify_channels: dict[str, bool] | None = None
    tags: dict[str, Any] | None = None


class ThresholdResponse(ThresholdBase):
    """Schema de resposta de threshold."""

    id: UUID
    is_active: bool
    last_alert_at: datetime | None = None
    last_value: float | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ThresholdListResponse(BaseModel):
    """Resposta de lista de thresholds."""

    total: int
    enabled: int
    thresholds: list[ThresholdResponse]
