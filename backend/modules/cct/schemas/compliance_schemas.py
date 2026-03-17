"""
Schemas de Compliance — CCT 2026.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ComplianceCheckRequest(BaseModel):
    """Request para verificacao de conformidade CCT."""

    empresa_id: str | None = None
    tipo_verificacao: str = Field(
        default="geral",
        description="Tipo: geral, salarios, beneficios, jornadas",
    )
    periodo_referencia: str = Field(..., description="Periodo no formato YYYY-MM", pattern=r"^\d{4}-\d{2}$")


class ComplianceItemResponse(BaseModel):
    """Item individual de compliance."""

    employee_id: str
    employee_nome: str | None = None
    cargo: str | None = None
    categoria: str
    conforme: bool
    detalhes: str


class ComplianceCheckResponse(BaseModel):
    """Resultado de verificacao de compliance."""

    model_config = ConfigDict(from_attributes=True)

    tipo_verificacao: str
    periodo_referencia: str
    total_funcionarios: int
    conformes: int
    nao_conformes: int
    percentual_conformidade: float
    itens: list[ComplianceItemResponse]
    alertas: list[str]
    created_at: datetime | None = None


class ComplianceSummaryResponse(BaseModel):
    """Resumo geral de compliance CCT."""

    empresa_id: str | None = None
    periodo: str
    cct_vigente: str
    registro_mte: str
    salarios_conformes: int
    salarios_total: int
    beneficios_conformes: int
    beneficios_total: int
    jornadas_conformes: int
    jornadas_total: int
    percentual_geral: float
    status: str
    recomendacoes: list[str]


class StabilityCheckRequest(BaseModel):
    """Request para verificacao de estabilidade."""

    employee_id: str
    data_admissao: str = Field(..., description="Data de admissao YYYY-MM-DD")
    data_nascimento: str | None = Field(None, description="Data de nascimento YYYY-MM-DD")
    acidente_trabalho: bool = Field(default=False)
    data_alta_inss: str | None = Field(None, description="Data da alta INSS YYYY-MM-DD")
    gestante: bool = Field(default=False)
    data_parto: str | None = Field(None, description="Data do parto YYYY-MM-DD")


class StabilityCheckResponse(BaseModel):
    """Resultado da verificacao de estabilidade."""

    employee_id: str
    estavel: bool
    motivos: list[str]
    data_fim_estabilidade: str | None = None
    alertas: list[str]
