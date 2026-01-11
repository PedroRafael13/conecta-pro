"""
Model de Medicao - Licitacoes
=============================
Gestao de medicoes de contratos publicos.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Date,
    Numeric, Integer, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from sqlalchemy.orm import relationship

from core.models import Base


class MeasurementStatus(str, Enum):
    """Status da medicao."""
    DRAFT = "draft"                          # Rascunho
    SUBMITTED = "submitted"                  # Enviada para aprovacao
    UNDER_REVIEW = "under_review"            # Em analise pelo fiscal
    APPROVED = "approved"                    # Aprovada
    REJECTED = "rejected"                    # Rejeitada
    PARTIALLY_APPROVED = "partially_approved"  # Aprovada parcialmente
    PAID = "paid"                            # Paga
    CANCELED = "canceled"                    # Cancelada


class MeasurementType(str, Enum):
    """Tipo de medicao."""
    MENSAL = "mensal"                # Medicao mensal
    EVENTUAL = "eventual"            # Medicao eventual
    FINAL = "final"                  # Medicao final
    REAJUSTE = "reajuste"            # Medicao de reajuste
    ADICIONAL = "adicional"          # Servicos adicionais


class Measurement(Base):
    """
    Medicao de Contrato Publico.

    Representa uma medicao de servicos/obras executados
    em um contrato publico, com aprovacao e pagamento.
    """
    __tablename__ = "bidding_measurements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contrato_id = Column(UUID(as_uuid=True), ForeignKey("bidding_public_contracts.id"), nullable=False, index=True)

    # Identificacao
    numero_medicao = Column(Integer, nullable=False)
    competencia = Column(String(7), nullable=False)  # YYYY-MM
    tipo = Column(String(30), nullable=False, default=MeasurementType.MENSAL.value)

    # Periodo de referencia
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)

    # Valores
    valor_bruto = Column(Numeric(15, 2), nullable=False)
    valor_retencoes = Column(Numeric(15, 2), nullable=True, default=0)
    valor_glosas = Column(Numeric(15, 2), nullable=True, default=0)
    valor_liquido = Column(Numeric(15, 2), nullable=False)

    # Retencoes detalhadas
    retencao_iss = Column(Numeric(15, 2), nullable=True, default=0)
    retencao_inss = Column(Numeric(15, 2), nullable=True, default=0)
    retencao_irrf = Column(Numeric(15, 2), nullable=True, default=0)
    retencao_pis_cofins_csll = Column(Numeric(15, 2), nullable=True, default=0)
    outras_retencoes = Column(Numeric(15, 2), nullable=True, default=0)

    # Glosas
    glosas_detalhamento = Column(JSONB, default=list)

    # Itens medidos
    itens_medidos = Column(JSONB, default=list)  # Lista de itens/servicos

    # Status e controle
    status = Column(String(30), nullable=False, default=MeasurementStatus.DRAFT.value, index=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Datas do processo
    data_envio = Column(Date, nullable=True)
    data_ateste = Column(Date, nullable=True)
    data_aprovacao = Column(Date, nullable=True)
    data_pagamento = Column(Date, nullable=True)

    # Aprovacao
    aprovador_nome = Column(String(255), nullable=True)
    aprovador_cargo = Column(String(100), nullable=True)
    observacoes_aprovador = Column(Text, nullable=True)

    # Nota Fiscal
    nota_fiscal_numero = Column(String(50), nullable=True)
    nota_fiscal_data = Column(Date, nullable=True)
    nota_fiscal_url = Column(String(500), nullable=True)

    # Arquivos
    relatorio_url = Column(String(500), nullable=True)       # Relatorio de medicao
    planilha_url = Column(String(500), nullable=True)        # Planilha de medicao
    fotos_url = Column(JSONB, default=list)                  # Registro fotografico

    # Observacoes
    descricao_servicos = Column(Text, nullable=True)
    observacoes = Column(Text, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    contrato = relationship("PublicContract", back_populates="medicoes")

    # Indices compostos
    __table_args__ = (
        Index('idx_measurement_contrato_numero', 'contrato_id', 'numero_medicao'),
        Index('idx_measurement_competencia', 'competencia'),
        Index('idx_measurement_status', 'status'),
    )

    def __repr__(self) -> str:
        return f"<Measurement {self.numero_medicao} - {self.competencia}>"

    @property
    def valor_total_retencoes(self) -> Decimal:
        """Calcula o total de retencoes."""
        return (
            (self.retencao_iss or Decimal("0")) +
            (self.retencao_inss or Decimal("0")) +
            (self.retencao_irrf or Decimal("0")) +
            (self.retencao_pis_cofins_csll or Decimal("0")) +
            (self.outras_retencoes or Decimal("0"))
        )

    @property
    def valor_a_receber(self) -> Decimal:
        """Valor liquido a receber apos retencoes e glosas."""
        return (
            self.valor_bruto -
            self.valor_total_retencoes -
            (self.valor_glosas or Decimal("0"))
        )

    @property
    def esta_aprovada(self) -> bool:
        """Verifica se a medicao foi aprovada."""
        return self.status in [
            MeasurementStatus.APPROVED.value,
            MeasurementStatus.PARTIALLY_APPROVED.value,
            MeasurementStatus.PAID.value
        ]

    def calcular_retencoes(
        self,
        aliquota_iss: Decimal = Decimal("5.0"),
        aliquota_inss: Decimal = Decimal("11.0"),
        aliquota_irrf: Decimal = Decimal("1.5"),
        aliquota_pcc: Decimal = Decimal("4.65")
    ) -> None:
        """Calcula as retencoes sobre o valor bruto."""
        self.retencao_iss = self.valor_bruto * (aliquota_iss / 100)
        self.retencao_inss = self.valor_bruto * (aliquota_inss / 100)
        self.retencao_irrf = self.valor_bruto * (aliquota_irrf / 100)
        self.retencao_pis_cofins_csll = self.valor_bruto * (aliquota_pcc / 100)

        self.valor_retencoes = self.valor_total_retencoes
        self.valor_liquido = self.valor_a_receber

    def adicionar_glosa(
        self,
        descricao: str,
        valor: Decimal,
        motivo: str = None
    ) -> None:
        """Adiciona uma glosa a medicao."""
        glosa = {
            "descricao": descricao,
            "valor": str(valor),
            "motivo": motivo,
            "data": datetime.utcnow().isoformat()
        }

        if not self.glosas_detalhamento:
            self.glosas_detalhamento = []

        self.glosas_detalhamento.append(glosa)
        self.valor_glosas = sum(
            Decimal(g["valor"]) for g in self.glosas_detalhamento
        )
        self.valor_liquido = self.valor_a_receber

    def adicionar_item_medido(
        self,
        descricao: str,
        unidade: str,
        quantidade: Decimal,
        valor_unitario: Decimal
    ) -> None:
        """Adiciona um item a medicao."""
        item = {
            "descricao": descricao,
            "unidade": unidade,
            "quantidade": str(quantidade),
            "valor_unitario": str(valor_unitario),
            "valor_total": str(quantidade * valor_unitario)
        }

        if not self.itens_medidos:
            self.itens_medidos = []

        self.itens_medidos.append(item)
