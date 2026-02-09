"""
Model de Contrato Publico - Licitacoes
======================================
Gestao de contratos firmados a partir de licitacoes.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class ContractStatus(StrEnum):
    """Status do contrato publico."""

    DRAFT = "draft"  # Rascunho/minuta
    PENDING_SIGNATURE = "pending_signature"  # Aguardando assinatura
    ACTIVE = "active"  # Vigente
    SUSPENDED = "suspended"  # Suspenso
    TERMINATED = "terminated"  # Rescindido
    COMPLETED = "completed"  # Concluido
    EXPIRED = "expired"  # Expirado


class AdjustmentIndex(StrEnum):
    """Indice de reajuste contratual."""

    IGPM = "igpm"  # Indice Geral de Precos de Mercado
    IPCA = "ipca"  # Indice de Precos ao Consumidor Amplo
    INPC = "inpc"  # Indice Nacional de Precos ao Consumidor
    INCC = "incc"  # Indice Nacional de Custo da Construcao
    CCT = "cct"  # Convencao Coletiva de Trabalho
    CUSTOM = "custom"  # Indice customizado


class GuaranteeType(StrEnum):
    """Tipo de garantia contratual."""

    CAUCAO_DINHEIRO = "caucao_dinheiro"  # Caucao em dinheiro
    CAUCAO_TITULO = "caucao_titulo"  # Caucao em titulos da divida publica
    SEGURO_GARANTIA = "seguro_garantia"  # Seguro-garantia
    FIANCA_BANCARIA = "fianca_bancaria"  # Fianca bancaria


class PublicContract(Base):
    """
    Contrato Publico firmado a partir de licitacao.

    Representa um contrato com orgao publico, com controle de
    empenhos, medicoes, aditivos e reajustes.
    """

    __tablename__ = "bidding_public_contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id = Column(UUID(as_uuid=True), ForeignKey("bidding_tenders.id"), nullable=True, index=True)

    # Identificacao do contrato
    numero_contrato = Column(String(50), nullable=False, index=True)
    ano_contrato = Column(Integer, nullable=False, index=True)
    objeto = Column(Text, nullable=False)
    objeto_resumido = Column(String(500), nullable=True)

    # Orgao contratante
    orgao_cnpj = Column(String(18), nullable=False, index=True)
    orgao_nome = Column(String(255), nullable=False)
    orgao_uf = Column(String(2), nullable=False, default="AM")
    unidade_gestora = Column(String(100), nullable=True)
    gestor_contrato = Column(String(255), nullable=True)
    fiscal_contrato = Column(String(255), nullable=True)

    # Valores
    valor_contrato = Column(Numeric(15, 2), nullable=False)
    valor_empenhado = Column(Numeric(15, 2), nullable=True, default=0)
    valor_executado = Column(Numeric(15, 2), nullable=True, default=0)
    valor_pago = Column(Numeric(15, 2), nullable=True, default=0)
    saldo_contrato = Column(Numeric(15, 2), nullable=True)

    # Empenho
    numero_empenho = Column(String(50), nullable=True, index=True)
    data_empenho = Column(Date, nullable=True)
    nota_empenho_url = Column(String(500), nullable=True)

    # Vigencia
    data_assinatura = Column(Date, nullable=True)
    data_publicacao = Column(Date, nullable=True)
    data_vigencia_inicio = Column(Date, nullable=False)
    data_vigencia_fim = Column(Date, nullable=False, index=True)
    prazo_meses = Column(Integer, nullable=True)

    # Reajuste
    indice_reajuste = Column(String(20), nullable=True, default=AdjustmentIndex.IGPM.value)
    data_base_reajuste = Column(Date, nullable=True)
    ultimo_reajuste = Column(Date, nullable=True)
    percentual_ultimo_reajuste = Column(Numeric(5, 2), nullable=True)

    # Garantia
    garantia_tipo = Column(String(30), nullable=True)
    garantia_valor = Column(Numeric(15, 2), nullable=True)
    garantia_percentual = Column(Numeric(5, 2), nullable=True)
    garantia_vencimento = Column(Date, nullable=True)
    garantia_documento_url = Column(String(500), nullable=True)

    # Status e controle
    status = Column(String(30), nullable=False, default=ContractStatus.DRAFT.value, index=True)
    ativo = Column(Boolean, default=True, nullable=False, index=True)

    # Aditivos
    aditivos = Column(JSONB, default=list)  # Lista de Addendum
    quantidade_aditivos = Column(Integer, default=0)

    # Integracao PNCP
    pncp_id = Column(String(100), nullable=True, unique=True, index=True)
    pncp_link = Column(String(500), nullable=True)

    # Arquivos
    arquivo_contrato_url = Column(String(500), nullable=True)
    arquivo_publicacao_url = Column(String(500), nullable=True)

    # Observacoes
    observacoes = Column(Text, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    tender = relationship("Tender", back_populates="contratos")
    medicoes = relationship("Measurement", back_populates="contrato", cascade="all, delete-orphan")

    # Indices compostos
    __table_args__ = (
        Index("idx_contract_orgao_ano", "orgao_cnpj", "ano_contrato"),
        Index("idx_contract_status_vigencia", "status", "data_vigencia_fim"),
        Index("idx_contract_tender", "tender_id"),
    )

    def __repr__(self) -> str:
        return f"<PublicContract {self.numero_contrato}/{self.ano_contrato}>"

    @property
    def esta_vigente(self) -> bool:
        """Verifica se o contrato esta vigente."""
        if self.status != ContractStatus.ACTIVE.value:
            return False
        hoje = date.today()
        return self.data_vigencia_inicio <= hoje <= self.data_vigencia_fim

    @property
    def dias_para_vencer(self) -> int | None:
        """Dias restantes de vigencia."""
        if not self.data_vigencia_fim:
            return None
        delta = self.data_vigencia_fim - date.today()
        return max(0, delta.days)

    @property
    def percentual_executado(self) -> Decimal:
        """Percentual do valor executado."""
        if not self.valor_contrato or self.valor_contrato == 0:
            return Decimal("0")
        return (self.valor_executado or Decimal("0")) / self.valor_contrato * 100

    @property
    def saldo_a_executar(self) -> Decimal:
        """Saldo remanescente do contrato."""
        return self.valor_contrato - (self.valor_executado or Decimal("0"))

    def adicionar_aditivo(
        self,
        tipo: str,
        numero: str,
        objeto: str,
        valor: Decimal = None,
        prazo_dias: int = None,
        data_assinatura: date = None,
    ) -> None:
        """Adiciona um aditivo ao contrato."""
        aditivo = {
            "numero": numero,
            "tipo": tipo,  # valor, prazo, valor_prazo, supressao
            "objeto": objeto,
            "valor": str(valor) if valor else None,
            "prazo_dias": prazo_dias,
            "data_assinatura": data_assinatura.isoformat() if data_assinatura else None,
            "data_registro": datetime.utcnow().isoformat(),
        }

        if not self.aditivos:
            self.aditivos = []

        self.aditivos.append(aditivo)
        self.quantidade_aditivos = len(self.aditivos)

        # Atualiza valores/vigencia se aplicavel
        if valor and tipo in ["valor", "valor_prazo"]:
            self.valor_contrato += valor

        if prazo_dias and tipo in ["prazo", "valor_prazo"]:
            from datetime import timedelta

            self.data_vigencia_fim += timedelta(days=prazo_dias)

    def calcular_reajuste(self, percentual: Decimal, data_aplicacao: date = None) -> Decimal:
        """Calcula o valor reajustado do contrato."""
        valor_reajuste = self.valor_contrato * (percentual / 100)
        self.percentual_ultimo_reajuste = percentual
        self.ultimo_reajuste = data_aplicacao or date.today()
        return valor_reajuste
