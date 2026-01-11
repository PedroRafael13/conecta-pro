"""
Model de Documento da Empresa - Licitacoes
==========================================
Gestao de documentos necessarios para participacao em licitacoes.
"""

import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Date,
    Integer, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from core.models import Base


class DocumentType(str, Enum):
    """Tipo de documento."""
    # Certidoes
    CND_FEDERAL = "cnd_federal"                    # Certidao Negativa de Debitos Federais
    CND_ESTADUAL = "cnd_estadual"                  # Certidao Negativa de Debitos Estaduais
    CND_MUNICIPAL = "cnd_municipal"                # Certidao Negativa de Debitos Municipais
    CND_TRABALHISTA = "cnd_trabalhista"            # Certidao Negativa de Debitos Trabalhistas
    CRF_FGTS = "crf_fgts"                          # Certificado de Regularidade do FGTS
    CND_INSS = "cnd_inss"                          # Certidao Negativa de Debitos INSS

    # Documentos Juridicos
    CONTRATO_SOCIAL = "contrato_social"            # Contrato Social e alteracoes
    CNPJ = "cnpj"                                  # Cartao CNPJ
    PROCURACAO = "procuracao"                      # Procuracao
    ESTATUTO = "estatuto"                          # Estatuto Social
    ATA_ASSEMBLEIA = "ata_assembleia"              # Ata de Assembleia

    # Documentos Tecnicos
    ATESTADO_CAPACIDADE = "atestado_capacidade"    # Atestado de Capacidade Tecnica
    REGISTRO_CREA = "registro_crea"                # Registro no CREA
    REGISTRO_CRA = "registro_cra"                  # Registro no CRA
    ALVARA_FUNCIONAMENTO = "alvara_funcionamento"  # Alvara de Funcionamento
    LICENCA_AMBIENTAL = "licenca_ambiental"        # Licenca Ambiental

    # Documentos Financeiros
    BALANCO_PATRIMONIAL = "balanco_patrimonial"    # Balanco Patrimonial
    DRE = "dre"                                    # Demonstracao de Resultado
    CERTIDAO_FALENCIA = "certidao_falencia"        # Certidao Negativa de Falencia

    # Outros
    DECLARACAO = "declaracao"                      # Declaracoes diversas
    OUTROS = "outros"


class DocumentStatus(str, Enum):
    """Status do documento."""
    VALID = "valid"              # Valido
    EXPIRING = "expiring"        # Vencendo em breve (< 30 dias)
    EXPIRED = "expired"          # Vencido
    PENDING = "pending"          # Pendente de obtencao
    RENEWING = "renewing"        # Em renovacao


class CompanyDocument(Base):
    """
    Documento da Empresa para Licitacoes.

    Gerencia todos os documentos necessarios para participacao
    em processos licitatorios, com controle de validade e alertas.
    """
    __tablename__ = "bidding_company_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao
    tipo = Column(String(50), nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    numero = Column(String(100), nullable=True)

    # Datas
    data_emissao = Column(Date, nullable=True)
    data_validade = Column(Date, nullable=True, index=True)

    # Arquivo
    arquivo_url = Column(String(500), nullable=True)
    arquivo_nome = Column(String(255), nullable=True)
    arquivo_tamanho = Column(Integer, nullable=True)

    # Status e controle
    status = Column(String(30), nullable=False, default=DocumentStatus.PENDING.value, index=True)
    ativo = Column(Boolean, default=True, nullable=False, index=True)

    # Renovacao automatica
    certidao_automatica = Column(Boolean, default=False)
    ultima_verificacao = Column(DateTime, nullable=True)
    ultima_renovacao = Column(DateTime, nullable=True)
    erro_renovacao = Column(Text, nullable=True)

    # Orgao emissor
    orgao_emissor = Column(String(255), nullable=True)

    # Metadados
    metadados = Column(JSONB, default=dict)

    # Observacoes
    observacoes = Column(Text, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Indices
    __table_args__ = (
        Index('idx_company_doc_tipo_status', 'tipo', 'status'),
        Index('idx_company_doc_validade', 'data_validade'),
    )

    def __repr__(self) -> str:
        return f"<CompanyDocument {self.tipo} - {self.nome}>"

    @property
    def esta_valido(self) -> bool:
        """Verifica se o documento esta valido."""
        if not self.data_validade:
            return True  # Documentos sem validade sao considerados validos
        return date.today() <= self.data_validade

    @property
    def dias_para_vencer(self) -> Optional[int]:
        """Dias restantes ate o vencimento."""
        if not self.data_validade:
            return None
        delta = self.data_validade - date.today()
        return delta.days

    @property
    def esta_vencendo(self) -> bool:
        """Verifica se esta vencendo em menos de 30 dias."""
        dias = self.dias_para_vencer
        if dias is None:
            return False
        return 0 < dias <= 30

    def atualizar_status(self) -> None:
        """Atualiza o status baseado na validade."""
        if not self.data_validade:
            self.status = DocumentStatus.VALID.value
        elif date.today() > self.data_validade:
            self.status = DocumentStatus.EXPIRED.value
        elif self.dias_para_vencer <= 30:
            self.status = DocumentStatus.EXPIRING.value
        else:
            self.status = DocumentStatus.VALID.value
