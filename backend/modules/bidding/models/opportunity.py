"""
Model de Oportunidade de Licitacao - Bidding AI Agents
======================================================
Oportunidades capturadas automaticamente de portais publicos.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID

from core.models import Base


class BiddingOpportunity(Base):
    """
    Oportunidade de Licitacao.

    Representa uma oportunidade identificada em portais publicos
    (PNCP, ComprasNet, etc.) para analise e possivel participacao.
    """

    __tablename__ = "bidding_opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portal = Column(String(50), nullable=False, index=True)
    portal_id = Column(String(100), nullable=True, index=True)
    objeto = Column(Text, nullable=False)
    valor_estimado = Column(Numeric(15, 2), nullable=True)

    # Modalidade
    modalidade = Column(String(50), nullable=True)

    # Orgao
    orgao_nome = Column(String(255), nullable=True)
    orgao_cnpj = Column(String(18), nullable=True, index=True)

    # Localizacao
    uf = Column(String(2), nullable=True, index=True)
    municipio = Column(String(100), nullable=True)

    # Datas
    data_publicacao = Column(DateTime, nullable=True, index=True)
    data_abertura = Column(DateTime, nullable=True, index=True)
    data_encerramento = Column(DateTime, nullable=True)

    # Edital
    url_edital = Column(String(500), nullable=True)

    # Classificacao
    status = Column(String(30), nullable=False, default="nova", index=True)
    relevancia_score = Column(Float, nullable=False, default=0)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<BiddingOpportunity {self.portal}:{self.portal_id} - {self.status}>"
