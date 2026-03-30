"""
ClientContract Model - Vínculo Cliente-Contrato
Sprint 30: Cadastro de Clientes/Condomínios

NOTA: Este model foi sincronizado com o banco de dados real em 29/03/2026.
Colunas correspondem EXATAMENTE ao schema da tabela client_contracts.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.clients.models.client import Client


class ContractServiceType(StrEnum):
    """Tipo de serviço do contrato."""

    PORTARIA_REMOTA = "portaria_remota"
    CONTROLE_ACESSO = "controle_acesso"
    CFTV = "cftv"
    ALARME = "alarme"
    CERCA_ELETRICA = "cerca_eletrica"
    MONITORAMENTO_24H = "monitoramento_24h"
    APP_MORADOR = "app_morador"
    ASSEMBLEIA_VIRTUAL = "assembleia_virtual"
    MANUTENCAO = "manutencao"
    LIMPEZA = "limpeza"
    JARDINAGEM = "jardinagem"
    ADMINISTRACAO = "administracao"
    CONSULTORIA = "consultoria"
    INTEGRACAO = "integracao"
    SUPORTE = "suporte"


class ServiceStatus(StrEnum):
    """Status do serviço no contrato."""

    PENDING = "pending"
    IMPLANTATION = "implantation"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    FINISHED = "finished"


class ClientContract(Base):
    """
    Model de Vínculo Cliente-Contrato — sincronizado com banco real.

    Representa os serviços contratados pelo cliente e suas configurações
    específicas para cada contrato.
    """

    __tablename__ = "client_contracts"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    condominium_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    contract_number = Column(String(50), unique=True, nullable=False, index=True)

    # Tipo de serviço e status — strings, não enums SQLAlchemy
    service_type = Column("service_type", String(30), nullable=False)
    status = Column("status", String(30), nullable=False, default="pending")

    # Descrição
    description = Column(Text, nullable=True)

    # Datas
    start_date = Column(Date, nullable=True, index=True)
    end_date = Column(Date, nullable=True, index=True)
    implantation_start_date = Column(Date, nullable=True)
    implantation_end_date = Column(Date, nullable=True)
    activation_date = Column(Date, nullable=True)
    cancellation_date = Column(Date, nullable=True)

    # Valores
    monthly_value = Column(Numeric(15, 2), nullable=True)
    implantation_value = Column(Numeric(15, 2), nullable=True)
    discount_percentage = Column(Float, nullable=True)
    billing_day = Column(Integer, nullable=True)

    # SLA
    sla_response_time = Column(Integer, nullable=True)
    sla_resolution_time = Column(Integer, nullable=True)
    sla_availability = Column(Float, nullable=True)
    sla_config = Column(JSONB, nullable=True)

    # Renovação
    auto_renewal = Column(Boolean, nullable=False, default=False)
    renewal_period_months = Column(Integer, nullable=True)
    notice_period_days = Column(Integer, nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    extra_metadata = Column("metadata", JSONB, nullable=True)

    # Flags — banco usa 'ativo' não 'is_active'
    ativo = Column(Boolean, nullable=False, default=True)

    # Auditoria
    created_at = Column(DateTime, nullable=False, server_default="now()")
    updated_at = Column(DateTime, nullable=False, server_default="now()", onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    client: "Client" = relationship("Client", back_populates="contracts")

    def __repr__(self) -> str:
        return f"<ClientContract(id={self.id}, service={self.service_type}, status={self.status})>"

    # Properties computadas (não são colunas)
    @property
    def is_active(self) -> bool:
        """Alias para ativo."""
        return bool(self.ativo)

    @property
    def contract_duration_days(self) -> int | None:
        """Duração do contrato em dias."""
        if not self.start_date:
            return None
        end = self.end_date or date.today()
        return (end - self.start_date).days

    @property
    def days_active(self) -> int | None:
        """Dias desde a ativação."""
        if not self.activation_date:
            return None
        return (date.today() - self.activation_date).days

    @property
    def days_until_end(self) -> int | None:
        """Dias até o fim do contrato."""
        if not self.end_date:
            return None
        return (self.end_date - date.today()).days

    @property
    def is_expiring_soon(self) -> bool:
        """Verifica se está próximo do vencimento (30 dias)."""
        days = self.days_until_end
        return days is not None and 0 < days <= 30

    @property
    def calculated_final_value(self) -> Decimal:
        """Calcula valor final com desconto."""
        if not self.monthly_value:
            return Decimal("0")
        discount = Decimal(str(self.discount_percentage or 0))
        return self.monthly_value * (1 - discount / 100)

    @property
    def final_value(self) -> Decimal | None:
        """Valor final calculado."""
        if not self.monthly_value:
            return None
        return self.calculated_final_value

    @property
    def is_electronic_security_service(self) -> bool:
        """Verifica se é serviço de segurança eletrônica."""
        electronic_services = {
            "portaria_remota",
            "controle_acesso",
            "cftv",
            "alarme",
            "cerca_eletrica",
            "monitoramento_24h",
        }
        return self.service_type in electronic_services

    @property
    def is_plus_service(self) -> bool:
        """Verifica se é serviço do Conecta Plus."""
        return self.service_type == "administracao"

    @property
    def is_main_service(self) -> bool:
        """Placeholder — determinar via lógica de negócio."""
        return False

    @property
    def auto_renew(self) -> bool:
        """Alias para auto_renewal."""
        return self.auto_renewal

    def start_implantation(self) -> None:
        """Inicia implantação do serviço."""
        self.status = "implantation"
        self.implantation_start_date = date.today()
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Ativa o serviço."""
        self.status = "active"
        self.ativo = True
        self.activation_date = date.today()
        self.updated_at = datetime.utcnow()

    def suspend(self, reason: str | None = None) -> None:
        """Suspende o serviço."""
        self.status = "suspended"
        if reason:
            self.notes = f"{self.notes or ''}\n[SUSPENSO] {datetime.now()}: {reason}".strip()
        self.updated_at = datetime.utcnow()

    def resume(self) -> None:
        """Retoma serviço suspenso."""
        self.status = "active"
        self.updated_at = datetime.utcnow()

    def cancel(self, reason: str | None = None) -> None:
        """Cancela o serviço."""
        self.status = "cancelled"
        self.ativo = False
        self.cancellation_date = date.today()
        if reason:
            self.notes = f"{self.notes or ''}\n[CANCELADO] {datetime.now()}: {reason}".strip()
        self.updated_at = datetime.utcnow()

    def finish(self) -> None:
        """Encerra o serviço."""
        self.status = "finished"
        self.ativo = False
        self.end_date = date.today()
        self.updated_at = datetime.utcnow()
