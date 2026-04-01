"""
Schemas de Salario — CCT 2026.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SalaryTableEntryResponse(BaseModel):
    """Entrada da tabela salarial."""

    cargo: str
    piso: float
    adicional: str
    adicional_descricao: str


class SalaryTableResponse(BaseModel):
    """Resposta com tabela salarial completa."""

    total_cargos: int
    piso_geral: float
    reajuste_piso: float
    reajuste_acima_piso: float
    vigencia: str
    cargos: list[SalaryTableEntryResponse]


class SalaryValidationRequest(BaseModel):
    """Request para validacao de salario contra piso CCT."""

    cargo: str = Field(..., description="Nome do cargo conforme tabela CCT")
    salario_atual: float = Field(..., gt=0, description="Salario atual do colaborador")
    employee_id: str | None = Field(None, description="ID do colaborador (opcional)")


class SalaryValidationResponse(BaseModel):
    """Resultado da validacao salarial."""

    conforme: bool
    cargo: str
    piso_cct: float
    salario_atual: float
    diferenca: float
    percentual_diferenca: float
    adicional_tipo: str | None = None
    adicional_valor: float | None = None
    alerta: str | None = None


class SalaryAdjustmentRequest(BaseModel):
    """Request para calculo de reajuste salarial CCT."""

    salario_atual: float = Field(..., gt=0)
    cargo: str | None = Field(None, description="Cargo para verificar se esta no piso")


class SalaryAdjustmentResponse(BaseModel):
    """Resultado do calculo de reajuste."""

    salario_atual: float
    percentual_reajuste: float
    salario_reajustado: float
    diferenca: float
    tipo_reajuste: str
    piso_cct: float | None = None


class SalaryAuditResponse(BaseModel):
    """Resposta de auditoria salarial persistida."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    employee_id: str
    cargo_cct: str
    piso_cct: float
    salario_atual: float
    conforme: bool
    diferenca: float
    adicional_tipo: str | None = None
    adicional_valor: float | None = None
    observacoes: str | None = None
    auditado_por: str | None = None
    created_at: datetime
