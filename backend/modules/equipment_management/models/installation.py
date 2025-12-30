"""
Model EquipmentInstallation - Ordens de Instalação de Equipamentos.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class InstallationStatus(str, Enum):
    """Status da instalação."""

    SCHEDULED = "scheduled"  # Agendada
    IN_PROGRESS = "in_progress"  # Em andamento
    COMPLETED = "completed"  # Concluída
    CANCELLED = "cancelled"  # Cancelada
    RESCHEDULED = "rescheduled"  # Reagendada
    PENDING_APPROVAL = "pending_approval"  # Aguardando aprovação do cliente
    PARTIAL = "partial"  # Parcialmente concluída


class EquipmentInstallation(Base):
    """
    Model para ordens de instalação de equipamentos.

    Gerencia o processo de instalação desde o agendamento
    até a conclusão e aceite do cliente.
    """

    __tablename__ = "equipment_installations"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    installation_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(30),
        default=InstallationStatus.SCHEDULED.value,
        nullable=False,
        index=True,
    )

    # Cliente/Contrato
    client_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )
    client_name: Mapped[str] = mapped_column(String(200), nullable=False)
    contract_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    post_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), nullable=True)

    # Local de instalação
    address: Mapped[str] = mapped_column(Text, nullable=False)
    address_complement: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    gps_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gps_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Agendamento
    scheduled_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    scheduled_time_start: Mapped[Optional[str]] = mapped_column(
        String(5),
        nullable=True,
    )  # HH:MM
    scheduled_time_end: Mapped[Optional[str]] = mapped_column(
        String(5),
        nullable=True,
    )  # HH:MM
    estimated_duration_hours: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # Execução
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_duration_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Técnico responsável
    technician_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    technician_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    team_members: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # [{id, name}]

    # Equipamentos a instalar
    equipment_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    equipment_count: Mapped[int] = mapped_column(Integer, default=0)
    equipment_details: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # Detalhes de cada equipamento

    # Configurações técnicas aplicadas
    configurations: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    network_config: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )  # IPs, portas, etc.

    # Fotos e documentos
    photos_before: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # Fotos antes
    photos_after: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # Fotos depois
    photos_equipment: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # Fotos dos equipamentos
    documents: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # Manuais, certificados

    # Materiais utilizados
    materials_used: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )  # [{item, qty, value}]
    total_materials_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Aceite do cliente
    client_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    client_accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    client_accepted_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    client_signature: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )  # Base64 da assinatura
    acceptance_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relatório técnico
    technical_report: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issues_found: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Custos
    labor_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    transport_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Reagendamento
    rescheduled_count: Mapped[int] = mapped_column(Integer, default=0)
    rescheduled_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    original_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Cancelamento
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadados
    priority: Mapped[str] = mapped_column(
        String(20),
        default="normal",
    )  # low, normal, high, urgent
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    metadata_extra: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Auditoria
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Properties
    @property
    def is_completed(self) -> bool:
        """Verifica se a instalação foi concluída."""
        return self.status == InstallationStatus.COMPLETED.value

    @property
    def is_overdue(self) -> bool:
        """Verifica se está atrasada."""
        if self.status in [
            InstallationStatus.COMPLETED.value,
            InstallationStatus.CANCELLED.value,
        ]:
            return False
        return datetime.utcnow() > self.scheduled_date

    @property
    def days_overdue(self) -> int:
        """Dias de atraso."""
        if not self.is_overdue:
            return 0
        delta = datetime.utcnow() - self.scheduled_date
        return delta.days

    @property
    def has_client_acceptance(self) -> bool:
        """Verifica se tem aceite do cliente."""
        return self.client_accepted and self.client_accepted_at is not None

    # Methods
    def start(self, technician_id: str, technician_name: str) -> None:
        """Inicia a instalação."""
        self.status = InstallationStatus.IN_PROGRESS.value
        self.started_at = datetime.utcnow()
        self.technician_id = technician_id
        self.technician_name = technician_name

    def complete(self, technical_report: Optional[str] = None) -> None:
        """Conclui a instalação."""
        self.status = InstallationStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds() / 3600
            self.actual_duration_hours = round(duration, 2)
        if technical_report:
            self.technical_report = technical_report

    def cancel(self, reason: str, cancelled_by: str) -> None:
        """Cancela a instalação."""
        self.status = InstallationStatus.CANCELLED.value
        self.cancelled_at = datetime.utcnow()
        self.cancelled_by = cancelled_by
        self.cancellation_reason = reason

    def reschedule(self, new_date: datetime, reason: str) -> None:
        """Reagenda a instalação."""
        if self.rescheduled_count == 0:
            self.original_date = self.scheduled_date
        self.status = InstallationStatus.RESCHEDULED.value
        self.scheduled_date = new_date
        self.rescheduled_count += 1
        self.rescheduled_reason = reason

    def accept_by_client(
        self,
        accepted_by: str,
        signature: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Registra aceite do cliente."""
        self.client_accepted = True
        self.client_accepted_at = datetime.utcnow()
        self.client_accepted_by = accepted_by
        self.client_signature = signature
        self.acceptance_notes = notes

    def add_photo(self, photo_type: str, photo_url: str) -> None:
        """Adiciona foto à instalação."""
        if photo_type == "before":
            if not self.photos_before:
                self.photos_before = []
            self.photos_before.append({
                "url": photo_url,
                "uploaded_at": datetime.utcnow().isoformat(),
            })
        elif photo_type == "after":
            if not self.photos_after:
                self.photos_after = []
            self.photos_after.append({
                "url": photo_url,
                "uploaded_at": datetime.utcnow().isoformat(),
            })
        elif photo_type == "equipment":
            if not self.photos_equipment:
                self.photos_equipment = []
            self.photos_equipment.append({
                "url": photo_url,
                "uploaded_at": datetime.utcnow().isoformat(),
            })

    def calculate_total_cost(self) -> float:
        """Calcula custo total da instalação."""
        total = 0.0
        if self.labor_cost:
            total += self.labor_cost
        if self.transport_cost:
            total += self.transport_cost
        if self.total_materials_value:
            total += self.total_materials_value
        self.total_cost = total
        return total
