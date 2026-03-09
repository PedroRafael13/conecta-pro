"""Schemas Pydantic para Férias e Afastamentos."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class VacationRequestCreate(BaseModel):
    """Schema para criar solicitação."""

    employee_id: str
    employee_name: str | None = None
    type: str = "ferias"
    start_date: date
    end_date: date
    reason: str | None = None
    notes: str | None = None


class VacationRequestUpdate(BaseModel):
    """Schema para atualizar solicitação."""

    type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    reason: str | None = None
    notes: str | None = None
    status: str | None = None


class VacationRequestResponse(BaseModel):
    """Schema de resposta."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    employee_id: str
    employee_name: str | None = None
    type: str
    status: str
    start_date: date
    end_date: date
    days: str | None = None
    reason: str | None = None
    notes: str | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None
    rejected_reason: str | None = None
    created_at: datetime
    updated_at: datetime


class VacationRequestListResponse(BaseModel):
    """Schema de resposta lista."""

    items: list[VacationRequestResponse]
    total: int
    pendente: int
    aprovado: int
    rejeitado: int
