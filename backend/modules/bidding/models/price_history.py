"""
Model de Historico de Precos - Bidding AI Agents
=================================================
Base de precos de referencia para composicao de propostas.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class BiddingPriceHistory(Base):
    """
    Historico de Precos de Referencia.

    Armazena precos praticados em licitacoes anteriores para
    servir de referencia na composicao de novas propostas.
    """

    __tablename__ = "bidding_price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    descricao = Column(Text, nullable=False)
    fonte = Column(String(50), nullable=False, default="pncp", index=True)

    # Valores
    valor_unitario = Column(Numeric(15, 4), nullable=False)
    unidade = Column(String(20), nullable=True)

    # Orgao de referencia
    orgao = Column(String(255), nullable=True)
    data_referencia = Column(DateTime, nullable=True, index=True)

    # Metadados adicionais
    metadata_extra = Column(JSONB, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<BiddingPriceHistory {self.descricao[:30]} - R${self.valor_unitario}>"
