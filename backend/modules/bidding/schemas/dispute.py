"""
Schemas de Disputa (Warrior Agent) - Licitacoes
================================================
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DisputeCreate(BaseModel):
    """Schema para criacao de registro de disputa/pregao."""

    tender_id: UUID = Field(..., description="ID do edital em disputa")
    portal: str = Field(..., max_length=50, description="Portal da disputa")
    portal_sessao_id: str | None = Field(None, description="ID da sessao no portal")

    # Configuracao
    valor_referencia: Decimal = Field(..., ge=0, description="Valor de referencia")
    valor_lance_inicial: Decimal | None = Field(None, ge=0)
    valor_lance_minimo: Decimal | None = Field(None, ge=0, description="Piso para lances automaticos")
    decremento_minimo: Decimal | None = Field(None, ge=0)
    estrategia: str = Field(default="moderada", description="agressiva, moderada, conservadora")

    # Lances realizados
    lances: list[dict] = Field(default_factory=list, description="Historico de lances")
    total_lances: int = Field(default=0, ge=0)

    # Resultado
    valor_final: Decimal | None = Field(None, ge=0)
    posicao_final: int | None = Field(None, ge=1)
    vencedor: bool = False

    # Observacoes
    observacoes: str | None = None


class DisputeResponse(DisputeCreate):
    """Schema de resposta para registro de disputa."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str = Field(default="aguardando", description="aguardando, em_disputa, encerrada, suspensa")
    created_at: datetime
    updated_at: datetime | None = None
