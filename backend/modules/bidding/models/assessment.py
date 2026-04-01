"""
Model de Avaliacao Go/No-Go - Bidding AI Agents
================================================
Avaliacao de viabilidade para participacao em licitacoes.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class BiddingAssessment(Base):
    """
    Avaliacao Go/No-Go.

    Resultado da avaliacao de viabilidade para participacao em um
    processo licitatorio, com score e recomendacao final.
    """

    __tablename__ = "bidding_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("bidding_tenders.id"), nullable=True, index=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("bidding_analyses.id"), nullable=True, index=True)

    # Score e recomendacao
    score = Column(Float, nullable=True)
    recomendacao = Column(String(30), nullable=True)  # GO, NO_GO, CONDICIONAL
    justificativa = Column(Text, nullable=True)

    # Detalhamento
    requisitos_nao_atendidos = Column(JSONB, nullable=True)
    acoes_necessarias = Column(JSONB, nullable=True)

    # Dados brutos da IA
    raw_assessment = Column(JSONB, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<BiddingAssessment {self.id} - {self.recomendacao} ({self.score})>"
