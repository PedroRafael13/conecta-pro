"""
Schemas de Jornada e Adicionais — CCT 2026.
"""

from pydantic import BaseModel, Field


class ScheduleValidationRequest(BaseModel):
    """Request para validacao de jornada."""

    employee_id: str | None = None
    jornada_tipo: str = Field(..., description="Tipo de jornada: 44h_semanais, 36h_corridas, 12x36")
    carga_semanal: int = Field(..., gt=0, le=48)


class ScheduleValidationResponse(BaseModel):
    """Resultado da validacao de jornada."""

    conforme: bool
    jornada_tipo: str
    divisor_mensal: int
    carga_semanal: int
    alertas: list[str]


class OvertimeCalculationRequest(BaseModel):
    """Request para calculo de hora extra."""

    salario_base: float = Field(..., gt=0)
    jornada_tipo: str = Field(default="12x36")
    horas_extras_normais: float = Field(default=0, ge=0)
    horas_extras_feriado: float = Field(default=0, ge=0)
    intrajornada_nao_concedida: bool = Field(default=False)


class OvertimeCalculationResponse(BaseModel):
    """Resultado do calculo de hora extra."""

    salario_base: float
    divisor_mensal: int
    valor_hora_normal: float
    valor_hora_extra_50: float
    valor_hora_extra_100: float
    total_horas_extras_normais: float
    total_horas_extras_feriado: float
    valor_intrajornada: float
    total_extras: float


class NightShiftCalculationRequest(BaseModel):
    """Request para calculo de adicional noturno."""

    salario_base: float = Field(..., gt=0)
    jornada_tipo: str = Field(default="12x36")
    horas_noturnas: float = Field(..., ge=0, description="Horas trabalhadas no periodo noturno (22h-05h)")


class NightShiftCalculationResponse(BaseModel):
    """Resultado do calculo de adicional noturno."""

    salario_base: float
    divisor_mensal: int
    valor_hora_normal: float
    adicional_noturno_percentual: float
    hora_noturna_minutos: float
    horas_noturnas_informadas: float
    horas_noturnas_reduzidas: float
    valor_adicional_noturno: float


class AdicionaisCalculationRequest(BaseModel):
    """Request para calculo de todos os adicionais."""

    salario_base: float = Field(..., gt=0)
    jornada_tipo: str = Field(default="12x36")
    ronda_permanente: bool = Field(default=False)
    ronda_pre_2020: bool = Field(default=False)
    acumulo_funcao: bool = Field(default=False)
    servicos_jardinagem_piscina: bool = Field(default=False)
    insalubridade: bool = Field(default=False)
    periculosidade: bool = Field(default=False)


class AdicionaisCalculationResponse(BaseModel):
    """Resultado do calculo de todos os adicionais."""

    salario_base: float
    adicional_ronda: float
    adicional_acumulo_funcao: float
    adicional_jardinagem_piscina: float
    adicional_insalubridade: float
    adicional_periculosidade: float
    total_adicionais: float
    salario_total: float
