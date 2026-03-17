"""
Schemas de Oportunidade (Scout Agent) - Licitacoes
===================================================
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ScoutRequest(BaseModel):
    """Parametros de busca do agente Scout."""

    keywords: list[str] = Field(default_factory=list, description="Palavras-chave para busca")
    uf: str = Field(default="AM", max_length=2, description="UF para filtro")
    modalidade: str | None = Field(None, description="Modalidade de licitacao")
    valor_min: Decimal | None = Field(None, ge=0, description="Valor minimo estimado")
    valor_max: Decimal | None = Field(None, ge=0, description="Valor maximo estimado")
    portal: str | None = Field(None, description="Portal especifico (pncp, comprasnet, bec, etc)")
    portais: list[str] = Field(
        default_factory=lambda: ["pncp", "comprasnet", "licitacoes_e", "ecompras_am"],
        description="Lista de portais para busca simultanea",
    )
    dias_retroativos: int = Field(default=30, ge=1, le=180, description="Dias retroativos para busca")
    segmentos: list[str] = Field(
        default_factory=lambda: ["vigilancia", "seguranca_eletronica", "portaria"],
        description="Segmentos de interesse",
    )


class OpportunityCreate(BaseModel):
    """Schema para criacao de oportunidade identificada pelo Scout."""

    tender_id: UUID | None = Field(None, description="ID do edital vinculado, se ja existir")
    portal_origem: str = Field(..., max_length=50, description="Portal de origem")
    portal_id: str | None = Field(None, max_length=100, description="ID no portal de origem")
    titulo: str = Field(..., min_length=5, description="Titulo/objeto da oportunidade")
    orgao_nome: str = Field(..., description="Nome do orgao licitante")
    orgao_uf: str = Field(default="AM", max_length=2)
    modalidade: str | None = Field(None, max_length=50)
    valor_estimado: Decimal | None = Field(None, ge=0)
    data_abertura: datetime | None = None
    url: str | None = Field(None, description="URL do edital no portal")
    score_relevancia: float = Field(default=0.0, ge=0.0, le=1.0, description="Score de relevancia 0-1")
    tags: list[str] = Field(default_factory=list)
    resumo_ia: str | None = Field(None, description="Resumo gerado pelo agente Scout")


class OpportunityResponse(OpportunityCreate):
    """Schema de resposta para oportunidade."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str = Field(default="nova", description="nova, analisando, descartada, convertida")
    created_at: datetime
    updated_at: datetime | None = None


class OpportunityListResponse(BaseModel):
    """Schema de lista de oportunidades com paginacao."""

    items: list[OpportunityResponse]
    total: int
    portais_consultados: list[str] = Field(default_factory=list)
    tempo_busca_ms: float = 0.0
