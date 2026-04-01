"""
Schemas de Beneficios — CCT 2026.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class BeneficioEntryResponse(BaseModel):
    """Entrada de beneficio CCT."""

    tipo: str
    obrigatorio: bool
    valor_total: float | None = None
    valor_empresa: float | None = None
    desconto_maximo_empregado: float | None = None
    desconto_percentual: float | None = None
    observacao: str


class BenefitsCCTResponse(BaseModel):
    """Lista completa de beneficios CCT."""

    total_beneficios: int
    obrigatorios: int
    opcionais: int
    beneficios: list[BeneficioEntryResponse]


class BenefitsValidationRequest(BaseModel):
    """Request para validacao de beneficios de um colaborador."""

    employee_id: str
    salario_base: float = Field(..., gt=0)
    beneficios_ativos: list[str] = Field(..., description="Lista de tipos de beneficio ativos")
    valor_vr_dia: float | None = Field(None, description="Valor do VR por dia")
    desconto_vt_percentual: float | None = Field(None, description="Percentual de desconto VT")


class BenefitValidationItem(BaseModel):
    """Resultado de validacao de um beneficio individual."""

    tipo: str
    obrigatorio: bool
    presente: bool
    conforme: bool
    alerta: str | None = None


class BenefitsValidationResponse(BaseModel):
    """Resultado da validacao de beneficios."""

    employee_id: str
    total_obrigatorios: int
    presentes: int
    faltantes: int
    conforme: bool
    itens: list[BenefitValidationItem]


class TaxaNegocialResponse(BaseModel):
    """Informacoes da taxa negocial sindical."""

    valor: float
    meses: list[int]
    prazo_oposicao_dia: int
    observacao: str
    mes_atual_aplicavel: bool
    proximo_desconto: str | None = None


class BenefitConfigCreate(BaseModel):
    """Schema para configurar beneficio por empresa."""

    empresa_id: str | None = None
    tipo_beneficio: str
    valor_empresa: float = Field(..., ge=0)
    desconto_empregado: float = Field(..., ge=0)
    operadora: str | None = None
    vigencia_inicio: date | None = None
    vigencia_fim: date | None = None
    observacoes: str | None = None


class BenefitConfigResponse(BaseModel):
    """Resposta de configuracao de beneficio."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    empresa_id: str | None = None
    tipo_beneficio: str
    valor_empresa: float
    desconto_empregado: float
    operadora: str | None = None
    vigencia_inicio: date | None = None
    vigencia_fim: date | None = None
    ativo: bool
    observacoes: str | None = None
    created_at: datetime
    updated_at: datetime
