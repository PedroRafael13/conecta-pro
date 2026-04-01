"""
Schemas de Rescisao e Ferias — CCT 2026.
"""

from pydantic import BaseModel, Field


class TerminationValidationRequest(BaseModel):
    """Request para validacao de rescisao conforme CCT."""

    employee_id: str
    data_admissao: str = Field(..., description="Data admissao YYYY-MM-DD")
    data_demissao: str = Field(..., description="Data demissao YYYY-MM-DD")
    salario_base: float = Field(..., gt=0)
    motivo: str = Field(..., description="Motivo: sem_justa_causa, justa_causa, pedido_demissao, acordo")
    aviso_previo_cumprido: bool = Field(default=False)
    dias_aviso_previo: int = Field(default=30, ge=0)


class TerminationValidationResponse(BaseModel):
    """Resultado da validacao de rescisao."""

    employee_id: str
    conforme: bool
    tempo_servico_anos: float
    homologacao_obrigatoria: bool
    sindicato_homologacao: str | None = None
    prazo_pagamento_dias: int
    data_limite_pagamento: str
    multa_atraso: float | None = None
    multa_demissao_pre_database: float | None = None
    alertas: list[str]


class VacationProportionalRequest(BaseModel):
    """Request para calculo de ferias proporcionais conforme CCT."""

    salario_base: float = Field(..., gt=0)
    faltas_periodo: int = Field(default=0, ge=0)
    meses_trabalhados: int = Field(..., ge=1, le=12)
    abono_pecuniario: bool = Field(default=False)


class VacationProportionalResponse(BaseModel):
    """Resultado do calculo de ferias proporcionais."""

    salario_base: float
    faltas_periodo: int
    dias_direito: int
    meses_trabalhados: int
    dias_proporcionais: float
    valor_ferias: float
    terco_constitucional: float
    abono_pecuniario: float
    total: float
    tabela_faltas: dict[str, int]


class ThirteenthSalaryRequest(BaseModel):
    """Request para calculo de 13o salario."""

    salario_base: float = Field(..., gt=0)
    meses_trabalhados: int = Field(..., ge=1, le=12)
    adicionais_mensais: float = Field(default=0, ge=0)


class ThirteenthSalaryResponse(BaseModel):
    """Resultado do calculo de 13o salario."""

    salario_base: float
    adicionais_mensais: float
    meses_trabalhados: int
    valor_integral: float
    valor_proporcional: float
    primeira_parcela: float
    segunda_parcela: float
    prazo_segunda_parcela: str
