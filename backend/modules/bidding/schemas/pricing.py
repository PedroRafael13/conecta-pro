"""
Schemas de Precificacao (Pricer Agent) - Licitacoes
====================================================
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PricerRequest(BaseModel):
    """Parametros de entrada para o agente Pricer."""

    tender_id: UUID | None = Field(None, description="ID do edital para precificar")
    regime_tributario: str = Field(
        default="simples",
        description="Regime tributario: simples, lucro_presumido, lucro_real",
    )
    bdi_percentual: float = Field(default=25.0, ge=0.0, le=100.0, description="Percentual de BDI")
    cenario: str = Field(default="base", description="Cenario: conservador, base, agressivo")
    incluir_encargos_sociais: bool = Field(default=True)
    incluir_insumos: bool = Field(default=True)
    incluir_uniformes: bool = Field(default=True)
    incluir_equipamentos: bool = Field(default=True)
    margem_minima: float = Field(default=5.0, ge=0.0, le=50.0, description="Margem minima desejada %")
    quantidade_postos: int | None = Field(None, ge=1, description="Quantidade de postos")
    escala: str | None = Field(None, description="Escala: 12x36, 44h, 24x72, etc")


class PricingCreate(BaseModel):
    """Schema para criacao de precificacao."""

    tender_id: UUID
    cenario: str = Field(default="base")
    regime_tributario: str = Field(default="simples")

    # Custos
    custo_mao_obra: Decimal = Field(default=Decimal("0"), ge=0)
    encargos_sociais: Decimal = Field(default=Decimal("0"), ge=0)
    encargos_percentual: float = Field(default=0.0, ge=0.0)
    insumos: Decimal = Field(default=Decimal("0"), ge=0)
    uniformes: Decimal = Field(default=Decimal("0"), ge=0)
    equipamentos: Decimal = Field(default=Decimal("0"), ge=0)
    custos_administrativos: Decimal = Field(default=Decimal("0"), ge=0)
    custo_total: Decimal = Field(default=Decimal("0"), ge=0)

    # BDI
    bdi_percentual: float = Field(default=25.0)
    bdi_valor: Decimal = Field(default=Decimal("0"), ge=0)

    # Tributos
    tributos_percentual: float = Field(default=0.0)
    tributos_valor: Decimal = Field(default=Decimal("0"), ge=0)
    detalhamento_tributos: dict = Field(default_factory=dict)

    # Preco final
    preco_unitario_mensal: Decimal = Field(default=Decimal("0"), ge=0)
    preco_total_mensal: Decimal = Field(default=Decimal("0"), ge=0)
    preco_total_contrato: Decimal = Field(default=Decimal("0"), ge=0)

    # Margem
    margem_percentual: float = Field(default=0.0)
    margem_valor: Decimal = Field(default=Decimal("0"))

    # Composicao detalhada
    composicao_custos: list[dict] = Field(default_factory=list, description="Planilha detalhada")
    premissas: list[dict] = Field(default_factory=list, description="Premissas utilizadas")

    # Comparativo
    comparativo_cenarios: list[dict] = Field(default_factory=list)
    competitividade_estimada: str | None = Field(None, description="alta, media, baixa")


class PricingResponse(PricingCreate):
    """Schema de resposta para precificacao."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str = Field(default="calculada")
    created_at: datetime
    updated_at: datetime | None = None
    tempo_calculo_ms: float = 0.0
