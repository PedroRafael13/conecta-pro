"""
Model de Edital (Tender) - Licitacoes Publicas
===============================================
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Date,
    Numeric, Integer, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from core.models import Base


class TenderStatus(str, Enum):
    """Status do edital."""
    DRAFT = "draft"                      # Rascunho
    PUBLISHED = "published"              # Publicado
    OPEN = "open"                        # Aberto para propostas
    SUSPENDED = "suspended"              # Suspenso
    CANCELED = "canceled"                # Cancelado
    UNDER_ANALYSIS = "under_analysis"    # Em analise
    ADJUDICATED = "adjudicated"          # Adjudicado
    HOMOLOGATED = "homologated"          # Homologado
    DESERTED = "deserted"                # Deserto
    FAILED = "failed"                    # Fracassado
    COMPLETED = "completed"              # Concluido


class BiddingModality(str, Enum):
    """Modalidade de licitacao (Lei 8.666/93 e Lei 14.133/21)."""
    CONCORRENCIA = "concorrencia"
    TOMADA_PRECOS = "tomada_precos"
    CONVITE = "convite"
    CONCURSO = "concurso"
    LEILAO = "leilao"
    PREGAO_ELETRONICO = "pregao_eletronico"
    PREGAO_PRESENCIAL = "pregao_presencial"
    DISPENSA = "dispensa"
    INEXIGIBILIDADE = "inexigibilidade"
    DIALOGO_COMPETITIVO = "dialogo_competitivo"
    CONCORRENCIA_INTERNACIONAL = "concorrencia_internacional"


class BiddingCriteria(str, Enum):
    """Criterio de julgamento."""
    MENOR_PRECO = "menor_preco"
    MAIOR_DESCONTO = "maior_desconto"
    MELHOR_TECNICA = "melhor_tecnica"
    TECNICA_E_PRECO = "tecnica_e_preco"
    MAIOR_LANCE = "maior_lance"
    MAIOR_RETORNO_ECONOMICO = "maior_retorno_economico"


class Tender(Base):
    """
    Edital de Licitacao.

    Representa um processo licitatorio completo com todas as informacoes
    necessarias para participacao e acompanhamento.
    """
    __tablename__ = "bidding_tenders"

    # Identificacao
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(50), nullable=False, index=True)
    numero_processo = Column(String(50), nullable=True)
    ano = Column(Integer, nullable=False, index=True)

    # Orgao/Entidade
    orgao_cnpj = Column(String(18), nullable=False, index=True)
    orgao_nome = Column(String(255), nullable=False)
    orgao_uf = Column(String(2), nullable=False, default="AM", index=True)
    orgao_municipio = Column(String(100), nullable=True)
    unidade_gestora = Column(String(100), nullable=True)

    # Modalidade e Tipo
    modalidade = Column(String(50), nullable=False, index=True)
    criterio_julgamento = Column(String(50), nullable=False, default=BiddingCriteria.MENOR_PRECO.value)
    tipo_contratacao = Column(String(50), nullable=True)  # obras, servicos, compras
    regime_execucao = Column(String(50), nullable=True)   # empreitada, tarefa, etc

    # Objeto
    objeto = Column(Text, nullable=False)
    objeto_resumido = Column(String(500), nullable=True)

    # Valores
    valor_estimado = Column(Numeric(15, 2), nullable=True)
    valor_homologado = Column(Numeric(15, 2), nullable=True)

    # Datas importantes
    data_publicacao = Column(DateTime, nullable=True, index=True)
    data_abertura = Column(DateTime, nullable=True, index=True)
    data_encerramento_propostas = Column(DateTime, nullable=True)
    data_impugnacao_limite = Column(DateTime, nullable=True)
    data_esclarecimentos_limite = Column(DateTime, nullable=True)
    data_resultado = Column(DateTime, nullable=True)
    data_homologacao = Column(DateTime, nullable=True)

    # Status e controle
    status = Column(String(30), nullable=False, default=TenderStatus.DRAFT.value, index=True)
    ativo = Column(Boolean, default=True, nullable=False, index=True)

    # Integracao PNCP
    pncp_id = Column(String(100), nullable=True, unique=True, index=True)
    pncp_link = Column(String(500), nullable=True)
    pncp_ultima_sync = Column(DateTime, nullable=True)

    # Participacao da empresa
    participando = Column(Boolean, default=False, index=True)
    interesse = Column(Boolean, default=False)
    motivo_nao_participacao = Column(Text, nullable=True)

    # Segmentacao
    segmento = Column(String(100), nullable=True, index=True)  # seguranca, limpeza, etc
    tags = Column(JSONB, default=list)

    # Requisitos e documentos
    requisitos = Column(JSONB, default=list)           # Lista de requisitos
    documentos_exigidos = Column(JSONB, default=list)  # Documentos necessarios

    # Anexos e arquivos
    anexos = Column(JSONB, default=list)  # URLs dos anexos do edital

    # Informacoes adicionais
    observacoes = Column(Text, nullable=True)
    fonte = Column(String(50), default="manual")  # manual, pncp, ecompras

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    documentos = relationship("TenderDocument", back_populates="tender", cascade="all, delete-orphan")
    propostas = relationship("BiddingProposal", back_populates="tender")
    contratos = relationship("PublicContract", back_populates="tender")

    # Indices compostos
    __table_args__ = (
        Index('idx_tender_orgao_ano', 'orgao_cnpj', 'ano'),
        Index('idx_tender_modalidade_status', 'modalidade', 'status'),
        Index('idx_tender_uf_segmento', 'orgao_uf', 'segmento'),
        Index('idx_tender_participando', 'participando', 'status'),
    )

    def __repr__(self) -> str:
        return f"<Tender {self.numero}/{self.ano} - {self.modalidade}>"

    @property
    def esta_aberto(self) -> bool:
        """Verifica se o edital esta aberto para propostas."""
        if self.status != TenderStatus.OPEN.value:
            return False
        if self.data_encerramento_propostas:
            return datetime.utcnow() < self.data_encerramento_propostas
        return True

    @property
    def prazo_impugnacao_valido(self) -> bool:
        """Verifica se ainda esta no prazo de impugnacao."""
        if not self.data_impugnacao_limite:
            return False
        return datetime.utcnow() < self.data_impugnacao_limite

    @property
    def dias_para_abertura(self) -> Optional[int]:
        """Dias restantes para abertura."""
        if not self.data_abertura:
            return None
        delta = self.data_abertura - datetime.utcnow()
        return max(0, delta.days)


class TenderDocument(Base):
    """
    Documento/Anexo do Edital.

    Armazena os anexos e documentos relacionados ao edital.
    """
    __tablename__ = "bidding_tender_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("bidding_tenders.id"), nullable=False, index=True)

    # Identificacao
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    tipo = Column(String(50), nullable=False)  # edital, anexo, planilha, ata, etc

    # Arquivo
    arquivo_url = Column(String(500), nullable=True)
    arquivo_nome = Column(String(255), nullable=True)
    arquivo_tamanho = Column(Integer, nullable=True)  # bytes
    arquivo_hash = Column(String(64), nullable=True)  # SHA256

    # Controle
    ordem = Column(Integer, default=0)
    obrigatorio = Column(Boolean, default=False)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    tender = relationship("Tender", back_populates="documentos")

    def __repr__(self) -> str:
        return f"<TenderDocument {self.nome}>"
