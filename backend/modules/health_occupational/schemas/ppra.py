"""
Schemas PPRA/PGR (NR-9) - Mapeamento de Riscos
==============================================

Schemas Pydantic para endpoints PPRA.
"""

from datetime import datetime, date
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator

from modules.health_occupational.models.ppra import RiskCategory, RiskLevel, ControlType


# ==============================================================================
# Risk Mapping Schemas
# ==============================================================================

class OccupationalRiskRequest(BaseModel):
    """Request para risco ocupacional."""

    categoria: str = Field(
        ...,
        description="Categoria do risco",
        pattern=r"^(fisico|quimico|biologico|ergonomico|acidente)$",
    )
    agente: str = Field(..., min_length=2, max_length=50, description="Agente de risco")
    descricao: Optional[str] = Field(None, description="Descricao do risco")
    fonte_geradora: str = Field(..., min_length=2, max_length=200)
    meio_propagacao: Optional[str] = Field(None, max_length=200)
    funcoes_expostas: List[str] = Field(default_factory=list)
    numero_expostos: Optional[int] = Field(None, ge=0)
    tempo_exposicao: Optional[str] = Field(None, max_length=50)
    probabilidade: Optional[int] = Field(None, ge=1, le=5)
    severidade: Optional[int] = Field(None, ge=1, le=5)
    valor_medido: Optional[float] = None
    unidade_medida: Optional[str] = None
    limite_tolerancia: Optional[float] = None
    medidas_existentes: List[str] = Field(default_factory=list)
    epis_recomendados: List[str] = Field(default_factory=list)
    exames_requeridos: List[str] = Field(default_factory=list)
    prioridade: int = Field(default=3, ge=1, le=5)


class RiskMappingRequest(BaseModel):
    """Request para mapeamento de riscos."""

    setor: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Setor a mapear",
    )
    descricao_setor: Optional[str] = Field(None, description="Descricao do setor")
    localizacao: Optional[str] = Field(None, max_length=200)
    funcoes: List[str] = Field(
        ...,
        min_length=1,
        description="Funcoes do setor",
    )
    numero_trabalhadores: Optional[int] = Field(None, ge=0)
    avaliador: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nome do avaliador",
    )
    cargo_avaliador: Optional[str] = Field(None, max_length=100)
    riscos: List[OccupationalRiskRequest] = Field(
        default_factory=list,
        description="Riscos identificados",
    )
    medidas_controle: List[str] = Field(
        default_factory=list,
        description="Medidas de controle existentes",
    )
    data_proxima_revisao: Optional[date] = None

    @field_validator('funcoes')
    @classmethod
    def validar_funcoes(cls, v):
        if len(v) > 50:
            raise ValueError("Maximo de 50 funcoes por setor")
        return v


class RiskMappingUpdateRequest(BaseModel):
    """Request para atualizacao de mapeamento."""

    descricao_setor: Optional[str] = None
    localizacao: Optional[str] = None
    funcoes: Optional[List[str]] = None
    numero_trabalhadores: Optional[int] = None
    nivel_risco_geral: Optional[str] = None
    data_proxima_revisao: Optional[date] = None
    ativo: Optional[bool] = None


class OccupationalRiskResponse(BaseModel):
    """Response de risco ocupacional."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mapeamento_id: UUID
    categoria: str
    agente: str
    descricao: Optional[str] = None
    fonte_geradora: str
    meio_propagacao: Optional[str] = None
    funcoes_expostas: List[str]
    numero_expostos: Optional[int] = None
    tempo_exposicao: Optional[str] = None
    probabilidade: Optional[int] = None
    severidade: Optional[int] = None
    nivel_risco: Optional[str] = None
    valor_medido: Optional[float] = None
    unidade_medida: Optional[str] = None
    limite_tolerancia: Optional[float] = None
    medidas_existentes: List[str]
    epis_recomendados: List[str]
    exames_requeridos: List[str]
    prioridade: int
    created_at: datetime


class RiskMappingResponse(BaseModel):
    """Response de mapeamento de riscos."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    setor: str
    descricao_setor: Optional[str] = None
    localizacao: Optional[str] = None
    funcoes: List[str]
    numero_trabalhadores: Optional[int] = None
    data_avaliacao: date
    avaliador: str
    cargo_avaliador: Optional[str] = None
    nivel_risco_geral: Optional[str] = None
    data_proxima_revisao: Optional[date] = None
    ativo: bool
    versao: int
    riscos: List[OccupationalRiskResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None


class RiskMappingListResponse(BaseModel):
    """Response de lista de mapeamentos."""
    items: List[RiskMappingResponse]
    total: int
    page: int = 1
    size: int = 20


class RiskMappingSummary(BaseModel):
    """Resumo de mapeamento para listagens."""
    id: UUID
    setor: str
    data_avaliacao: date
    nivel_risco_geral: Optional[str] = None
    total_riscos: int
    total_funcoes: int
    ativo: bool


# ==============================================================================
# Control Measure Schemas
# ==============================================================================

class ControlMeasureRequest(BaseModel):
    """Request para medida de controle."""

    mapeamento_id: UUID = Field(..., description="ID do mapeamento")
    tipo: str = Field(
        ...,
        description="Tipo da medida",
        pattern=r"^(eliminacao|substituicao|controle_engenharia|sinalizacao|controle_administrativo|epi|epc)$",
    )
    descricao: str = Field(..., min_length=10, description="Descricao da medida")
    riscos_controlados: List[UUID] = Field(
        default_factory=list,
        description="IDs dos riscos controlados",
    )
    responsavel: Optional[str] = Field(None, max_length=100)
    data_prevista: Optional[date] = None
    custo_estimado: Optional[float] = Field(None, ge=0)


class ControlMeasureUpdateRequest(BaseModel):
    """Request para atualizacao de medida de controle."""

    descricao: Optional[str] = None
    status: Optional[str] = Field(
        None,
        pattern=r"^(pendente|em_andamento|implementada|cancelada)$",
    )
    responsavel: Optional[str] = None
    data_prevista: Optional[date] = None
    data_implementacao: Optional[date] = None
    eficaz: Optional[bool] = None
    data_verificacao: Optional[date] = None
    observacoes: Optional[str] = None
    custo_estimado: Optional[float] = None


class ControlMeasureResponse(BaseModel):
    """Response de medida de controle."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mapeamento_id: UUID
    tipo: str
    descricao: str
    riscos_controlados: List[UUID]
    status: str
    responsavel: Optional[str] = None
    data_prevista: Optional[date] = None
    data_implementacao: Optional[date] = None
    eficaz: Optional[bool] = None
    data_verificacao: Optional[date] = None
    observacoes: Optional[str] = None
    custo_estimado: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# ==============================================================================
# Risk Category Info
# ==============================================================================

class RiskCategoryInfo(BaseModel):
    """Informacoes de categoria de risco."""
    id: str
    nome: str
    exemplos: List[str]
    cor_mapa: str


class RiskCategoriesResponse(BaseModel):
    """Response com categorias de risco."""
    categorias: List[RiskCategoryInfo]
    niveis_risco: List[str]
