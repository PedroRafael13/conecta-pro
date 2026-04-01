"""
Model de Precificacao - Bidding AI Agents
==========================================
Calculo de precos e cenarios para propostas de licitacao.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class BiddingPricing(Base):
    """
    Precificacao de Proposta.

    Calculo detalhado de custos e precos para uma proposta,
    incluindo cenarios e composicao tributaria.
    """

    __tablename__ = "bidding_pricing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(
        UUID(as_uuid=True), ForeignKey("bidding_tenders.id", ondelete="CASCADE"), nullable=True, index=True
    )
    proposal_id = Column(UUID(as_uuid=True), ForeignKey("bidding_proposals.id", ondelete="SET NULL"), nullable=True)
    assessment_id = Column(
        UUID(as_uuid=True), ForeignKey("bidding_assessments.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Itens
    itens = Column(JSONB, nullable=True, server_default="[]")

    # Custos
    custos_diretos = Column(Numeric(15, 2), nullable=True)
    custos_indiretos = Column(Numeric(15, 2), nullable=True)
    impostos = Column(Numeric(15, 2), nullable=True)
    margem_lucro = Column(Float, nullable=True)
    valor_total = Column(Numeric(15, 2), nullable=True)

    # Cenarios
    cenario = Column(String(20), nullable=True)
    cenarios_completos = Column(JSONB, nullable=True, server_default="{}")
    comparativo_mercado = Column(JSONB, nullable=True, server_default="{}")

    # Tributacao
    regime_tributario = Column(String(30), nullable=True)
    bdi_percentual = Column(Float, nullable=True)

    # Dados brutos da IA
    raw_pricing = Column(JSONB, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    def __repr__(self) -> str:
        return f"<BiddingPricing {self.id} - {self.cenario} R${self.valor_total}>"
