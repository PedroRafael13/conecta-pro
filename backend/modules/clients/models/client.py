"""
Client Model - Cadastro de Clientes
Sprint 30: Cadastro de Clientes/Condomínios
"""

import re
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, Enum, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.clients.models.client_contract import ClientContract
    from modules.clients.models.condominium import Condominium
    from modules.clients.models.integration_settings import IntegrationSettings


class ClientType(StrEnum):
    """Tipo de cliente."""

    CONDOMINIO = "condominio"
    EMPRESA = "empresa"
    RESIDENCIAL = "residencial"
    COMERCIAL = "comercial"
    INDUSTRIAL = "industrial"
    PUBLICO = "publico"
    OUTRO = "outro"


class ClientStatus(StrEnum):
    """Status do cliente."""

    PROSPECT = "prospect"
    ATIVO = "ativo"
    INATIVO = "inativo"
    SUSPENSO = "suspenso"
    BLOQUEADO = "bloqueado"
    CANCELADO = "cancelado"
    INADIMPLENTE = "inadimplente"


class ClientSegment(StrEnum):
    """Segmento do cliente."""

    PEQUENO = "pequeno"
    MEDIO = "medio"
    GRANDE = "grande"
    ENTERPRISE = "enterprise"
    GOVERNO = "governo"
    ONG = "ong"


class DocumentType(StrEnum):
    """Tipo de documento."""

    CPF = "cpf"
    CNPJ = "cnpj"
    RG = "rg"
    INSCRICAO_ESTADUAL = "inscricao_estadual"
    INSCRICAO_MUNICIPAL = "inscricao_municipal"


class Client(Base):
    """
    Model de Cliente.

    Representa uma empresa, condomínio ou pessoa física que contrata
    serviços da Conecta Mais.
    """

    __tablename__ = "clients"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String(20), unique=True, nullable=False, index=True)

    # Dados cadastrais
    type = Column(Enum(ClientType), nullable=False, default=ClientType.CONDOMINIO)
    status = Column(Enum(ClientStatus), nullable=False, default=ClientStatus.PROSPECT)
    segment = Column(Enum(ClientSegment), nullable=True)

    # Razão social / Nome
    legal_name = Column(String(200), nullable=False)
    trade_name = Column(String(200), nullable=True)

    # Documentos
    document_type = Column(Enum(DocumentType), nullable=False, default=DocumentType.CNPJ)
    document_number = Column(String(20), nullable=False, index=True)
    state_registration = Column(String(20), nullable=True)
    municipal_registration = Column(String(20), nullable=True)

    # Endereço
    address_street = Column(String(200), nullable=True)
    address_number = Column(String(20), nullable=True)
    address_complement = Column(String(100), nullable=True)
    address_neighborhood = Column(String(100), nullable=True)
    address_city = Column(String(100), nullable=True)
    address_state = Column(String(2), nullable=True)
    address_zipcode = Column(String(10), nullable=True)
    address_country = Column(String(50), nullable=True, default="Brasil")
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)

    # Contatos
    phone = Column(String(20), nullable=True)
    phone_secondary = Column(String(20), nullable=True)
    whatsapp = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    email_billing = Column(String(200), nullable=True)
    website = Column(String(200), nullable=True)

    # Contato principal
    contact_name = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(200), nullable=True)
    contact_role = Column(String(50), nullable=True)

    # Dados financeiros
    payment_terms = Column(Integer, nullable=True, default=30)
    credit_limit = Column(Numeric(15, 2), nullable=True, default=0)
    current_balance = Column(Numeric(15, 2), nullable=True, default=0)
    is_defaulter = Column(Boolean, nullable=False, default=False)
    default_since = Column(Date, nullable=True)
    total_debt = Column(Numeric(15, 2), nullable=True, default=0)

    # Dados comerciais
    sales_rep_id = Column(UUID(as_uuid=True), nullable=True)
    sales_rep_name = Column(String(100), nullable=True)
    acquisition_source = Column(String(50), nullable=True)
    acquisition_date = Column(Date, nullable=True)
    first_contract_date = Column(Date, nullable=True)

    # Métricas
    total_contracts = Column(Integer, nullable=False, default=0)
    active_contracts = Column(Integer, nullable=False, default=0)
    total_revenue = Column(Numeric(15, 2), nullable=True, default=0)
    average_ticket = Column(Numeric(15, 2), nullable=True, default=0)
    satisfaction_score = Column(Numeric(3, 2), nullable=True)
    nps_score = Column(Integer, nullable=True)

    # Integrações
    plus_enabled = Column(Boolean, nullable=False, default=False)
    plus_client_id = Column(String(50), nullable=True)
    external_id = Column(String(50), nullable=True)

    # Configurações
    settings = Column(JSONB, nullable=True, default=dict)
    tags = Column(ARRAY(String), nullable=True, default=list)
    notes = Column(Text, nullable=True)

    # Flags
    is_active = Column(Boolean, nullable=False, default=True)
    is_vip = Column(Boolean, nullable=False, default=False)
    requires_approval = Column(Boolean, nullable=False, default=False)

    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    condominiums: list["Condominium"] = relationship(
        "Condominium", back_populates="client", cascade="all, delete-orphan"
    )
    contracts: list["ClientContract"] = relationship(
        "ClientContract", back_populates="client", cascade="all, delete-orphan"
    )
    integration_settings: list["IntegrationSettings"] = relationship(
        "IntegrationSettings", back_populates="client", cascade="all, delete-orphan"
    )

    # Índices
    __table_args__ = (
        Index("ix_clients_document", "document_type", "document_number"),
        Index("ix_clients_status_type", "status", "type"),
        Index("ix_clients_segment", "segment"),
        Index("ix_clients_sales_rep", "sales_rep_id"),
        Index("ix_clients_defaulter", "is_defaulter"),
        CheckConstraint("credit_limit >= 0", name="ck_clients_credit_limit_positive"),
    )

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, code={self.code}, legal_name={self.legal_name})>"

    @property
    def display_name(self) -> str:
        """Nome para exibição."""
        return self.trade_name or self.legal_name

    @property
    def formatted_document(self) -> str:
        """Documento formatado."""
        doc = self.document_number
        if not doc:
            return ""

        doc = re.sub(r"\D", "", doc)

        if self.document_type == DocumentType.CPF and len(doc) == 11:
            return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
        elif self.document_type == DocumentType.CNPJ and len(doc) == 14:
            return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"

        return doc

    @property
    def full_address(self) -> str:
        """Endereço completo."""
        parts = []
        if self.address_street:
            addr = self.address_street
            if self.address_number:
                addr += f", {self.address_number}"
            if self.address_complement:
                addr += f" - {self.address_complement}"
            parts.append(addr)

        if self.address_neighborhood:
            parts.append(self.address_neighborhood)

        if self.address_city and self.address_state:
            parts.append(f"{self.address_city}/{self.address_state}")

        if self.address_zipcode:
            parts.append(f"CEP: {self.address_zipcode}")

        return ", ".join(parts)

    @property
    def is_company(self) -> bool:
        """Verifica se é pessoa jurídica."""
        return self.document_type == DocumentType.CNPJ

    @property
    def days_as_defaulter(self) -> int | None:
        """Dias como inadimplente."""
        if not self.is_defaulter or not self.default_since:
            return None
        return (date.today() - self.default_since).days

    @property
    def health_score(self) -> int:
        """Score de saúde do cliente (0-100)."""
        score = 100

        # Penalidades
        if self.status == ClientStatus.INADIMPLENTE:
            score -= 40
        elif self.status == ClientStatus.SUSPENSO:
            score -= 30
        elif self.status == ClientStatus.BLOQUEADO:
            score -= 50
        elif self.status != ClientStatus.ATIVO:
            score -= 20

        if self.is_defaulter:
            days = self.days_as_defaulter or 0
            if days > 90:
                score -= 30
            elif days > 60:
                score -= 20
            elif days > 30:
                score -= 10

        # Bônus
        if self.is_vip:
            score += 10

        if self.satisfaction_score and self.satisfaction_score >= 4.5:
            score += 5

        if self.active_contracts >= 3:
            score += 5

        return max(0, min(100, score))

    def activate(self) -> None:
        """Ativa o cliente."""
        self.status = ClientStatus.ATIVO
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Desativa o cliente."""
        self.status = ClientStatus.INATIVO
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def suspend(self, reason: str | None = None) -> None:
        """Suspende o cliente."""
        self.status = ClientStatus.SUSPENSO
        if reason:
            self.notes = f"{self.notes or ''}\n[SUSPENSO] {datetime.now()}: {reason}".strip()
        self.updated_at = datetime.utcnow()

    def block(self, reason: str | None = None) -> None:
        """Bloqueia o cliente."""
        self.status = ClientStatus.BLOQUEADO
        self.is_active = False
        if reason:
            self.notes = f"{self.notes or ''}\n[BLOQUEADO] {datetime.now()}: {reason}".strip()
        self.updated_at = datetime.utcnow()

    def set_defaulter(self, debt_amount: Decimal) -> None:
        """Marca como inadimplente."""
        self.is_defaulter = True
        self.default_since = date.today()
        self.total_debt = debt_amount
        self.status = ClientStatus.INADIMPLENTE
        self.updated_at = datetime.utcnow()

    def clear_default(self) -> None:
        """Remove status de inadimplente."""
        self.is_defaulter = False
        self.default_since = None
        self.total_debt = Decimal("0")
        if self.status == ClientStatus.INADIMPLENTE:
            self.status = ClientStatus.ATIVO
        self.updated_at = datetime.utcnow()

    def update_metrics(self, total_contracts: int, active_contracts: int, total_revenue: Decimal) -> None:
        """Atualiza métricas do cliente."""
        self.total_contracts = total_contracts
        self.active_contracts = active_contracts
        self.total_revenue = total_revenue
        if total_contracts > 0:
            self.average_ticket = total_revenue / total_contracts
        self.updated_at = datetime.utcnow()

    def enable_plus(self, client_id: str) -> None:
        """Habilita integração com Conecta Plus."""
        self.plus_enabled = True
        self.plus_client_id = client_id
        self.updated_at = datetime.utcnow()

    @staticmethod
    def generate_code(sequence: int) -> str:
        """Gera código do cliente."""
        year = datetime.now().year
        return f"CLI-{year}-{sequence:05d}"

    @staticmethod
    def validate_cnpj(cnpj: str) -> bool:
        """Valida CNPJ."""
        cnpj = re.sub(r"\D", "", cnpj)

        if len(cnpj) != 14:
            return False

        if cnpj == cnpj[0] * 14:
            return False

        # Validação dos dígitos verificadores
        def calc_digit(cnpj_part: str, weights: list[int]) -> int:
            total = sum(int(d) * w for d, w in zip(cnpj_part, weights, strict=False))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder

        weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        digit1 = calc_digit(cnpj[:12], weights1)
        digit2 = calc_digit(cnpj[:12] + str(digit1), weights2)

        return cnpj[-2:] == f"{digit1}{digit2}"

    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Valida CPF."""
        cpf = re.sub(r"\D", "", cpf)

        if len(cpf) != 11:
            return False

        if cpf == cpf[0] * 11:
            return False

        # Validação dos dígitos verificadores
        def calc_digit(cpf_part: str, factor: int) -> int:
            total = sum(int(d) * (factor - i) for i, d in enumerate(cpf_part))
            remainder = (total * 10) % 11
            return 0 if remainder >= 10 else remainder

        digit1 = calc_digit(cpf[:9], 10)
        digit2 = calc_digit(cpf[:9] + str(digit1), 11)

        return cpf[-2:] == f"{digit1}{digit2}"
