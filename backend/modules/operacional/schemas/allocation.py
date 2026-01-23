"""
Schemas Pydantic para Allocation (Alocação Funcionário-Posto).
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from modules.operacional.models.allocation import AllocationStatus


class AllocationBase(BaseModel):
    """Schema base para Allocation."""

    post_id: str = Field(..., description="ID do posto")
    employee_id: str = Field(..., description="ID do funcionário")
    start_date: date = Field(..., description="Data de início")
    end_date: Optional[date] = Field(None, description="Data de fim (null = indeterminado)")
    is_primary: bool = Field(default=True, description="É alocação principal")
    is_temporary: bool = Field(default=False, description="É temporária")
    role: Optional[str] = Field(None, max_length=100, description="Função")
    notes: Optional[str] = Field(None, description="Observações")

    @model_validator(mode="after")
    def validate_dates(self) -> "AllocationBase":
        """Valida range de datas."""
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date deve ser anterior a end_date")
        return self


class AllocationCreate(AllocationBase):
    """Schema para criação de Allocation."""

    hourly_rate: float = Field(default=0.0, ge=0, description="Valor hora")
    monthly_salary: float = Field(default=0.0, ge=0, description="Salário mensal")
    additional_benefits: float = Field(default=0.0, ge=0, description="Benefícios")
    qualifications: Optional[Dict[str, Any]] = Field(None, description="Qualificações")


class AllocationUpdate(BaseModel):
    """Schema para atualização parcial de Allocation."""

    status: Optional[AllocationStatus] = None
    end_date: Optional[date] = None
    is_primary: Optional[bool] = None
    is_temporary: Optional[bool] = None
    hourly_rate: Optional[float] = Field(None, ge=0)
    monthly_salary: Optional[float] = Field(None, ge=0)
    additional_benefits: Optional[float] = Field(None, ge=0)
    role: Optional[str] = Field(None, max_length=100)
    qualifications: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    termination_reason: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class AllocationResponse(BaseModel):
    """Schema de resposta para Allocation."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    post_id: str
    employee_id: str
    status: str
    start_date: date
    end_date: Optional[date]
    is_primary: bool
    is_temporary: bool
    hourly_rate: float
    monthly_salary: float
    additional_benefits: float
    role: Optional[str]
    qualifications: Optional[Dict[str, Any]]
    notes: Optional[str]
    termination_reason: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_current: bool
    days_allocated: int
    total_monthly_cost: float

    # Dados denormalizados do funcionário
    employee_name: Optional[str] = None
    employee_matricula: Optional[str] = None
    employee_cargo: Optional[str] = None

    # Dados denormalizados do posto
    post_name: Optional[str] = None
    post_code: Optional[str] = None


class AllocationListResponse(BaseModel):
    """Schema para listagem paginada de Allocations."""

    items: List[AllocationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AllocationFilter(BaseModel):
    """Schema para filtros de busca de Allocations."""

    post_id: Optional[str] = None
    employee_id: Optional[str] = None
    status: Optional[AllocationStatus] = None
    is_primary: Optional[bool] = None
    is_temporary: Optional[bool] = None
    is_current: Optional[bool] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None


class AllocationTerminate(BaseModel):
    """Schema para encerramento de alocação."""

    end_date: date = Field(..., description="Data de encerramento")
    termination_reason: str = Field(..., max_length=255, description="Motivo")
    notes: Optional[str] = Field(None, description="Observações")
