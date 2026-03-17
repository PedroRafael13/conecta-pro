"""
Model de Historico de Precos - Bidding AI Agents
=================================================
Base de precos de referencia para composicao de propostas.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Numeric, String, Text
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
    item_descricao = Column(Text, nullable=False)
    item_catmat = Column(String(20), nullable=True)
    preco = Column(Numeric(15, 2), nullable=True)
    unidade = Column(String(30), nullable=True)
    quantidade = Column(Numeric(15, 4), nullable=True)

    # Orgao de referencia
    orgao_nome = Column(String(255), nullable=True)
    orgao_cnpj = Column(String(14), nullable=True)
    orgao_uf = Column(String(2), nullable=True)

    # Datas
    data_homologacao = Column(Date, nullable=True)

    # Fonte
    fonte = Column(String(50), nullable=True)
    fonte_id = Column(String(100), nullable=True)

    # Metadados adicionais (extra, nao presente na migration original)
    metadata_extra = Column(JSONB, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    def __repr__(self) -> str:
        return f"<BiddingPriceHistory {self.item_descricao[:30]} - R${self.preco}>"
