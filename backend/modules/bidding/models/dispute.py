"""
Model de Disputa/Pregao - Bidding AI Agents
============================================
Gestao de sessoes de disputa em pregoes eletronicos.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
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
    tender_id = Column(
        UUID(as_uuid=True), ForeignKey("bidding_tenders.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Sessao
    portal = Column(String(50), nullable=False, index=True)
    sessao_id = Column(String(100), nullable=True)
    status = Column(String(30), nullable=False, default="configurado", server_default="configurado", index=True)

    # Estrategia e lances
    estrategia = Column(JSONB, nullable=True, server_default="{}")
    lances = Column(JSONB, nullable=True, server_default="[]")

    # Resultado
    posicao_final = Column(Integer, nullable=True)
    resultado = Column(String(30), nullable=True)
    valor_final = Column(String(50), nullable=True)

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    def __repr__(self) -> str:
        return f"<BiddingDispute {self.portal}:{self.sessao_id} - {self.status}>"
