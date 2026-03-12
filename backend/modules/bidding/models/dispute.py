"""
Model de Disputa/Pregao - Bidding AI Agents
============================================
Gestao de sessoes de disputa em pregoes eletronicos.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class BiddingDispute(Base):
    """
    Disputa de Pregao Eletronico.

    Representa uma sessao de disputa em pregao eletronico,
    com estrategia de lances e resultado final.
    """

    __tablename__ = "bidding_disputes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("bidding_tenders.id"), nullable=True, index=True)

    # Sessao
    portal = Column(String(50), nullable=False, index=True)
    session_id = Column(String(100), nullable=True)
    status = Column(String(30), nullable=False, default="pending", index=True)

    # Estrategia e lances
    estrategia = Column(JSONB, nullable=True)
    lances = Column(JSONB, nullable=True)

    # Resultado
    posicao_final = Column(Integer, nullable=True)
    resultado = Column(String(30), nullable=True)
    valor_final = Column(Numeric(15, 2), nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<BiddingDispute {self.portal}:{self.session_id} - {self.status}>"
