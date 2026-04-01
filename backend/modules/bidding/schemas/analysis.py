"""
Schemas de Analise (Analyst Agent) - Licitacoes
================================================
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnalystRequest(BaseModel):
    """Parametros de entrada para o agente Analyst."""

    tender_id: UUID | None = Field(None, description="ID do edital para analisar")
    edital_text: str | None = Field(None, description="Texto completo do edital (alternativa a tender_id)")
    extrair_requisitos: bool = Field(default=True, description="Extrair requisitos de habilitacao")
    extrair_itens: bool = Field(default=True, description="Extrair itens/lotes")
    extrair_prazos: bool = Field(default=True, description="Extrair prazos importantes")
    extrair_penalidades: bool = Field(default=True, description="Extrair clausulas de penalidades")


class AnalysisCreate(BaseModel):
    """Schema para criacao de analise de edital."""

    tender_id: UUID | None = None
    # Resumo geral
    resumo: str = Field(..., description="Resumo da analise do edital")
    objeto_detalhado: str | None = Field(None, description="Descricao detalhada do objeto")

    # Requisitos
    requisitos_habilitacao: list[dict] = Field(default_factory=list, description="Lista de requisitos")
    requisitos_tecnicos: list[dict] = Field(default_factory=list)
    requisitos_financeiros: list[dict] = Field(default_factory=list)

    # Itens / Lotes
    itens: list[dict] = Field(default_factory=list, description="Itens ou lotes identificados")
    valor_estimado_total: Decimal | None = None

    # Prazos
    prazos: list[dict] = Field(default_factory=list, description="Prazos criticos")

    # Riscos e oportunidades
    riscos_identificados: list[dict] = Field(default_factory=list)
    oportunidades: list[dict] = Field(default_factory=list)

    # Penalidades
    penalidades: list[dict] = Field(default_factory=list)

    # Clausulas importantes
    clausulas_destaque: list[dict] = Field(default_factory=list, description="Clausulas que merecem atencao")

    # Metricas
    complexidade_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Complexidade do edital 0-1")
    confianca_analise: float = Field(default=0.0, ge=0.0, le=1.0, description="Confianca na analise 0-1")


class AnalysisResponse(AnalysisCreate):
    """Schema de resposta para analise de edital."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str = Field(default="concluida", description="concluida, parcial, erro")
    created_at: datetime
    updated_at: datetime | None = None
    tempo_analise_ms: float = 0.0
