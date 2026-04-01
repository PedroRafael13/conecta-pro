"""
Schemas de Pipeline completo - Licitacoes
==========================================
Orquestra todos os agentes em sequencia.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.bidding.schemas.analysis import AnalysisResponse
from modules.bidding.schemas.assessment import AssessmentResponse
from modules.bidding.schemas.pricing import PricingResponse


class PipelineRequest(BaseModel):
    """Parametros para execucao do pipeline completo."""

    tender_id: UUID | None = Field(None, description="ID do edital existente")
    edital_text: str | None = Field(None, description="Texto do edital (alternativa a tender_id)")
    run_pricing: bool = Field(default=True, description="Executar precificacao")
    regime_tributario: str = Field(
        default="simples",
        description="Regime tributario para precificacao",
    )
    bdi_percentual: float = Field(default=25.0, ge=0.0, le=100.0)
    cenario: str = Field(default="base", description="Cenario de precificacao")
    gerar_documentos: bool = Field(default=False, description="Gerar documentos de proposta")


class PipelineStepResult(BaseModel):
    """Resultado de um passo do pipeline."""

    agent_name: str
    status: str = Field(description="success, failed, skipped")
    duration_ms: float = 0.0
    error: str | None = None


class PipelineResult(BaseModel):
    """Resultado completo do pipeline."""

    model_config = ConfigDict(from_attributes=True)

    pipeline_id: UUID
    tender_id: UUID | None = None

    # Resultados dos agentes
    analysis: AnalysisResponse | None = None
    assessment: AssessmentResponse | None = None
    pricing: PricingResponse | None = None

    # Documentos gerados
    documents_generated: list[dict] = Field(default_factory=list)

    # Recomendacao final
    overall_recommendation: str = Field(
        default="pendente",
        description="go, no_go, condicional, pendente",
    )
    recommendation_summary: str | None = Field(None, description="Resumo da recomendacao")

    # Metricas do pipeline
    steps: list[PipelineStepResult] = Field(default_factory=list)
    total_duration_ms: float = 0.0
    created_at: datetime | None = None
