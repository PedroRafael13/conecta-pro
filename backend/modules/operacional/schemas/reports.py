"""
Schemas Pydantic para Relatorios Operacionais.
"""

from datetime import date

from pydantic import BaseModel, Field


class CoverageReportItem(BaseModel):
    """Item de cobertura por posto."""

    post_id: str
    post_name: str
    total_allocations: int
    active_allocations: int
    coverage_rate: float = Field(..., description="Percentual de cobertura")


class CoverageReportResponse(BaseModel):
    """Resposta do relatorio de cobertura."""

    start_date: date
    end_date: date
    total_posts: int
    total_allocations: int
    active_allocations: int
    coverage_rate: float
    items: list[CoverageReportItem]


class HoursReportItem(BaseModel):
    """Item de horas por funcionario."""

    employee_id: str
    total_shifts: int
    total_hours: float
    overtime_hours: float


class HoursReportResponse(BaseModel):
    """Resposta do relatorio de horas trabalhadas."""

    start_date: date
    end_date: date
    total_employees: int
    total_hours: float
    total_overtime: float
    items: list[HoursReportItem]


class CostsReportItem(BaseModel):
    """Item de custos por posto."""

    post_id: str
    post_name: str
    total_shifts: int
    total_cost: float


class CostsReportResponse(BaseModel):
    """Resposta do relatorio de custos estimados."""

    start_date: date
    end_date: date
    total_posts: int
    total_cost: float
    items: list[CostsReportItem]
