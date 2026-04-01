"""
Model de Proposta - Licitacoes
==============================
Gestao de propostas para editais de licitacao.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class ProposalStatus(StrEnum):
    """Status da proposta."""

    DRAFT = "draft"  # Rascunho
    READY = "ready"  # Pronta para envio
    SUBMITTED = "submitted"  # Enviada
    UNDER_ANALYSIS = "under_analysis"  # Em analise
    CLASSIFIED = "classified"  # Classificada
    DISQUALIFIED = "disqualified"  # Desclassificada
    WINNER = "winner"  # Vencedora
    SECOND_PLACE = "second_place"  # Segundo lugar
    NEGOTIATING = "negotiating"  # Em negociacao
    CANCELED = "canceled"  # Cancelada


class BiddingProposal(Base):
    """
    Proposta para Licitacao.

    Representa uma proposta comercial para um edital especifico,
    com controle de itens, valores, BDI e versionamento.
    """

    __tablename__ = "bidding_proposals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("bidding_tenders.id"), nullable=False, index=True)

    # Identificacao
    numero = Column(String(50), nullable=False)
    versao = Column(Integer, default=1, nullable=False)

    # Valores
    valor_total = Column(Numeric(15, 2), nullable=False)
    valor_unitario = Column(Numeric(15, 4), nullable=True)  # Para itens unicos
    desconto_percentual = Column(Numeric(5, 2), nullable=True)

    # BDI e composicao
    bdi_percentual = Column(Numeric(5, 2), nullable=True)
    bdi_detalhamento = Column(JSONB, default=dict)  # Composicao do BDI

    # Encargos
    encargos_sociais = Column(Numeric(5, 2), nullable=True)
    encargos_detalhamento = Column(JSONB, default=dict)

    # Itens da proposta
    itens = Column(JSONB, default=list)  # Lista de ProposalItem

    # Status e controle
    status = Column(String(30), nullable=False, default=ProposalStatus.DRAFT.value, index=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Classificacao
    posicao_classificacao = Column(Integer, nullable=True)
    valor_lance_final = Column(Numeric(15, 2), nullable=True)

    # Arquivo gerado
    arquivo_pdf_url = Column(String(500), nullable=True)
    arquivo_planilha_url = Column(String(500), nullable=True)

    # Datas
    data_envio = Column(DateTime, nullable=True)
    data_resultado = Column(DateTime, nullable=True)

    # Observacoes
    observacoes = Column(Text, nullable=True)
    justificativa_preco = Column(Text, nullable=True)

    # Historico de lances (pregao)
    historico_lances = Column(JSONB, default=list)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    tender = relationship("Tender", back_populates="propostas")

    # Indices
    __table_args__ = (
        Index("idx_proposal_tender_status", "tender_id", "status"),
        Index("idx_proposal_versao", "tender_id", "versao"),
    )

    def __repr__(self) -> str:
        return f"<BiddingProposal {self.numero} v{self.versao} - {self.status}>"

    @property
    def valor_com_bdi(self) -> Decimal:
        """Calcula valor total com BDI aplicado."""
        if not self.bdi_percentual:
            return self.valor_total
        fator_bdi = 1 + (self.bdi_percentual / 100)
        return self.valor_total * fator_bdi

    def adicionar_lance(self, valor: Decimal, data: datetime = None) -> None:
        """Adiciona lance ao historico (pregao)."""
        lance = {
            "valor": str(valor),
            "data": (data or datetime.utcnow()).isoformat(),
            "posicao": len(self.historico_lances) + 1,
        }
        if not self.historico_lances:
            self.historico_lances = []
        self.historico_lances.append(lance)
        self.valor_lance_final = valor


class BiddingProposalItem(Base):
    """
    Item da Proposta de Licitacao.

    Detalha cada item/servico da proposta com valores unitarios e totais.
    """

    __tablename__ = "bidding_proposal_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey("bidding_proposals.id"), nullable=False, index=True)

    # Identificacao do item
    numero_item = Column(Integer, nullable=False)
    codigo = Column(String(50), nullable=True)
    descricao = Column(Text, nullable=False)
    unidade = Column(String(20), nullable=False)  # UN, M2, H, etc

    # Quantidades e valores
    quantidade = Column(Numeric(15, 4), nullable=False)
    valor_unitario = Column(Numeric(15, 4), nullable=False)
    valor_total = Column(Numeric(15, 2), nullable=False)

    # Composicao de custo
    custo_direto = Column(Numeric(15, 2), nullable=True)
    custo_indireto = Column(Numeric(15, 2), nullable=True)
    margem = Column(Numeric(15, 2), nullable=True)

    # Detalhamento
    composicao = Column(JSONB, default=dict)  # Detalhamento do custo

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<BiddingProposalItem {self.numero_item} - {self.descricao[:30]}>"
