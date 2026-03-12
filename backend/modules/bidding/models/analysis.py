"""
Model de Analise de Edital - Bidding AI Agents
===============================================
Analise automatizada de editais por agentes de IA.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class BiddingAnalysis(Base):
    """
    Analise de Edital.

    Resultado da analise automatizada de um edital por agente de IA,
    incluindo resumo do objeto, requisitos e recomendacoes.
    """

    __tablename__ = "bidding_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("bidding_tenders.id"), nullable=True, index=True)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("bidding_opportunities.id"), nullable=True, index=True)

    # Analise do objeto
    objeto_resumido = Column(Text, nullable=True)
    modalidade_identificada = Column(String(50), nullable=True)
    criterio_julgamento = Column(String(50), nullable=True)

    # Requisitos e documentos
    requisitos_habilitacao = Column(JSONB, nullable=True)
    red_flags = Column(JSONB, nullable=True)
    documentos_necessarios = Column(JSONB, nullable=True)

    # Recomendacao
    recomendacao_participacao = Column(String(30), nullable=True)

    # Dados brutos da IA
    raw_analysis = Column(JSONB, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<BiddingAnalysis {self.id} - {self.recomendacao_participacao}>"
