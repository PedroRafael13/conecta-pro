"""
ClientContract Model - Vínculo Cliente-Contrato
Sprint 30: Cadastro de Clientes/Condomínios
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.clients.models.client import Client


class ContractServiceType(StrEnum):
    """Tipo de serviço contratado."""

    PORTARIA_REMOTA = "portaria_remota"
    CONTROLE_ACESSO = "controle_acesso"
    CFTV = "cftv"
    ALARME = "alarme"
    CERCA_ELETRICA = "cerca_eletrica"
    MONITORAMENTO_24H = "monitoramento_24h"
    RONDA_VIRTUAL = "ronda_virtual"
    INTERFONIA = "interfonia"
    MANUTENCAO = "manutencao"
    GESTAO_CONDOMINIAL = "gestao_condominial"
    PORTARIA_FISICA = "portaria_fisica"
    LIMPEZA = "limpeza"
    JARDINAGEM = "jardinagem"
    PISCINA = "piscina"
    OUTRO = "outro"


class ServiceStatus(StrEnum):
    """Status do serviço."""

    PENDENTE = "pendente"
    EM_IMPLANTACAO = "em_implantacao"
    ATIVO = "ativo"
    SUSPENSO = "suspenso"
    CANCELADO = "cancelado"
    ENCERRADO = "encerrado"


class ClientContract(Base):
    """
    Model de Vínculo Cliente-Contrato.

    Representa os serviços contratados pelo cliente e suas configurações
    específicas para cada contrato.
    """

    __tablename__ = "client_contracts"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    contract_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    condominium_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Tipo de serviço
    service_type = Column(Enum(ContractServiceType), nullable=False, default=ContractServiceType.PORTARIA_REMOTA)
    status = Column(Enum(ServiceStatus), nullable=False, default=ServiceStatus.PENDENTE)

    # Descrição
    description = Column(String(500), nullable=True)
    scope = Column(Text, nullable=True)

    # Valores
    monthly_value = Column(Numeric(12, 2), nullable=True)
    setup_fee = Column(Numeric(12, 2), nullable=True, default=0)
    discount_percentage = Column(Numeric(5, 2), nullable=True, default=0)
    final_value = Column(Numeric(12, 2), nullable=True)

    # Datas
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    implantation_date = Column(Date, nullable=True)
    activation_date = Column(Date, nullable=True)
    suspension_date = Column(Date, nullable=True)
    cancellation_date = Column(Date, nullable=True)

    # SLA
    sla_response_time_minutes = Column(Integer, nullable=True)
    sla_resolution_time_hours = Column(Integer, nullable=True)
    sla_availability_percentage = Column(Numeric(5, 2), nullable=True, default=99.0)

    # Recursos
    total_cameras = Column(Integer, nullable=True, default=0)
    total_access_points = Column(Integer, nullable=True, default=0)
    total_alarm_zones = Column(Integer, nullable=True, default=0)
    total_intercoms = Column(Integer, nullable=True, default=0)
    total_employees = Column(Integer, nullable=True, default=0)

    # Horários
    operating_hours = Column(JSONB, nullable=True)
    is_24h = Column(Boolean, nullable=False, default=False)

    # Integrações
    guardian_service_id = Column(String(50), nullable=True)
    plus_service_id = Column(String(50), nullable=True)

    # Configurações específicas do serviço
    settings = Column(JSONB, nullable=True, default=dict)
    features = Column(ARRAY(String), nullable=True, default=list)
    restrictions = Column(ARRAY(String), nullable=True, default=list)

    # Responsáveis
    technical_contact_name = Column(String(100), nullable=True)
    technical_contact_phone = Column(String(20), nullable=True)
    technical_contact_email = Column(String(200), nullable=True)
    commercial_contact_name = Column(String(100), nullable=True)
    commercial_contact_phone = Column(String(20), nullable=True)

    # Notas
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    suspension_reason = Column(Text, nullable=True)

    # Flags
    is_active = Column(Boolean, nullable=False, default=True)
    is_main_service = Column(Boolean, nullable=False, default=False)
    auto_renew = Column(Boolean, nullable=False, default=True)
    requires_equipment = Column(Boolean, nullable=False, default=False)

    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    client: "Client" = relationship("Client", back_populates="contracts")

    # Índices
    __table_args__ = (
        Index("ix_client_contracts_client_service", "client_id", "service_type"),
        Index("ix_client_contracts_status", "status"),
        Index("ix_client_contracts_contract", "contract_id"),
        Index("ix_client_contracts_condominium", "condominium_id"),
    )

    def __repr__(self) -> str:
        return f"<ClientContract(id={self.id}, service={self.service_type}, status={self.status})>"

    @property
    def is_guardian_service(self) -> bool:
        """Verifica se é serviço do Guardian."""
        guardian_services = {
            ContractServiceType.PORTARIA_REMOTA,
            ContractServiceType.CONTROLE_ACESSO,
            ContractServiceType.CFTV,
            ContractServiceType.ALARME,
            ContractServiceType.CERCA_ELETRICA,
            ContractServiceType.MONITORAMENTO_24H,
            ContractServiceType.RONDA_VIRTUAL,
        }
        return self.service_type in guardian_services

    @property
    def is_plus_service(self) -> bool:
        """Verifica se é serviço do Conecta Plus."""
        return self.service_type == ContractServiceType.GESTAO_CONDOMINIAL

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
        discount = self.discount_percentage or Decimal("0")
        return self.monthly_value * (1 - discount / 100)

    def start_implantation(self) -> None:
        """Inicia implantação do serviço."""
        self.status = ServiceStatus.EM_IMPLANTACAO
        self.implantation_date = date.today()
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Ativa o serviço."""
        self.status = ServiceStatus.ATIVO
        self.is_active = True
        self.activation_date = date.today()
        self.updated_at = datetime.utcnow()

    def suspend(self, reason: str | None = None) -> None:
        """Suspende o serviço."""
        self.status = ServiceStatus.SUSPENSO
        self.suspension_date = date.today()
        self.suspension_reason = reason
        self.updated_at = datetime.utcnow()

    def resume(self) -> None:
        """Retoma serviço suspenso."""
        self.status = ServiceStatus.ATIVO
        self.suspension_date = None
        self.suspension_reason = None
        self.updated_at = datetime.utcnow()

    def cancel(self, reason: str | None = None) -> None:
        """Cancela o serviço."""
        self.status = ServiceStatus.CANCELADO
        self.is_active = False
        self.cancellation_date = date.today()
        self.cancellation_reason = reason
        self.updated_at = datetime.utcnow()

    def finish(self) -> None:
        """Encerra o serviço."""
        self.status = ServiceStatus.ENCERRADO
        self.is_active = False
        self.end_date = date.today()
        self.updated_at = datetime.utcnow()

    def update_sla(
        self, response_time: int | None = None, resolution_time: int | None = None, availability: Decimal | None = None
    ) -> None:
        """Atualiza configurações de SLA."""
        if response_time is not None:
            self.sla_response_time_minutes = response_time
        if resolution_time is not None:
            self.sla_resolution_time_hours = resolution_time
        if availability is not None:
            self.sla_availability_percentage = availability
        self.updated_at = datetime.utcnow()

    def update_resources(
        self,
        cameras: int | None = None,
        access_points: int | None = None,
        alarm_zones: int | None = None,
        intercoms: int | None = None,
        employees: int | None = None,
    ) -> None:
        """Atualiza recursos do serviço."""
        if cameras is not None:
            self.total_cameras = cameras
        if access_points is not None:
            self.total_access_points = access_points
        if alarm_zones is not None:
            self.total_alarm_zones = alarm_zones
        if intercoms is not None:
            self.total_intercoms = intercoms
        if employees is not None:
            self.total_employees = employees
        self.updated_at = datetime.utcnow()

    def set_technical_contact(self, name: str, phone: str | None = None, email: str | None = None) -> None:
        """Define contato técnico."""
        self.technical_contact_name = name
        self.technical_contact_phone = phone
        self.technical_contact_email = email
        self.updated_at = datetime.utcnow()

    def calculate_value(self) -> None:
        """Calcula e atualiza valor final."""
        self.final_value = self.calculated_final_value
        self.updated_at = datetime.utcnow()
