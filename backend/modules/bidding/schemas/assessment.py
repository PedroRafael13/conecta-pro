"""
Schemas de Avaliacao Go/No-Go (Assessor Agent) - Licitacoes
============================================================
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AssessorRequest(BaseModel):
    """Parametros de entrada para o agente Assessor (Go/No-Go)."""

    tender_id: UUID | None = Field(None, description="ID do edital para avaliar")
    analysis_id: UUID | None = Field(None, description="ID de uma analise ja existente")
    considerar_capacidade_operacional: bool = Field(default=True)
    considerar_distancia: bool = Field(default=True)
    considerar_historico: bool = Field(default=True)
    peso_financeiro: float = Field(default=0.3, ge=0.0, le=1.0)
    peso_tecnico: float = Field(default=0.3, ge=0.0, le=1.0)
    peso_estrategico: float = Field(default=0.2, ge=0.0, le=1.0)
    peso_risco: float = Field(default=0.2, ge=0.0, le=1.0)


class AssessmentCreate(BaseModel):
    """Schema para criacao de avaliacao Go/No-Go."""

    tender_id: UUID | None = None
    analysis_id: UUID | None = None

    # Decisao
    recomendacao: str = Field(..., description="go, no_go, condicional")
    score_geral: float = Field(default=0.0, ge=0.0, le=10.0, description="Score geral 0-10")
    justificativa: str = Field(..., description="Justificativa da recomendacao")

    # Dimensoes de avaliacao
    score_financeiro: float = Field(default=0.0, ge=0.0, le=10.0)
    score_tecnico: float = Field(default=0.0, ge=0.0, le=10.0)
    score_estrategico: float = Field(default=0.0, ge=0.0, le=10.0)
    score_risco: float = Field(default=0.0, ge=0.0, le=10.0)

    # Detalhes por dimensao
    analise_financeira: dict = Field(default_factory=dict)
    analise_tecnica: dict = Field(default_factory=dict)
    analise_estrategica: dict = Field(default_factory=dict)
    analise_risco: dict = Field(default_factory=dict)

    # Requisitos atendidos
    requisitos_atendidos: list[dict] = Field(default_factory=list)
    requisitos_nao_atendidos: list[dict] = Field(default_factory=list)
    requisitos_parciais: list[dict] = Field(default_factory=list)

    # Capacidade
    possui_atestados: bool = False
    possui_equipe: bool = False
    possui_equipamentos: bool = False
    capacidade_financeira_suficiente: bool = False

    # Concorrencia
    concorrentes_provaveis: list[dict] = Field(default_factory=list)
    vantagem_competitiva: str | None = None

    # Valor estimado de participacao
    custo_participacao_estimado: Decimal | None = None


class AssessmentResponse(AssessmentCreate):
    """Schema de resposta para avaliacao Go/No-Go."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str = Field(default="concluida")
    created_at: datetime
    updated_at: datetime | None = None
    tempo_avaliacao_ms: float = 0.0
