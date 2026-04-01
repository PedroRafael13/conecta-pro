"""
Model EquipmentMaintenance - Manutenções de Equipamentos.
"""

from datetime import datetime, timedelta
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class MaintenanceType(StrEnum):
    """Tipos de manutenção."""

    PREVENTIVA = "preventiva"  # Agendada periodicamente
    CORRETIVA = "corretiva"  # Chamado por defeito
    PREDITIVA = "preditiva"  # Baseada em análise de dados
    INSTALACAO = "instalacao"  # Pós-instalação
    ATUALIZACAO = "atualizacao"  # Atualização de firmware/software
    CALIBRACAO = "calibracao"  # Calibração de sensores


class MaintenanceStatus(StrEnum):
    """Status da manutenção."""

    SCHEDULED = "scheduled"  # Agendada
    PENDING = "pending"  # Pendente de execução
    IN_PROGRESS = "in_progress"  # Em andamento
    WAITING_PARTS = "waiting_parts"  # Aguardando peças
    COMPLETED = "completed"  # Concluída
    CANCELLED = "cancelled"  # Cancelada
    FAILED = "failed"  # Falha na manutenção


class MaintenancePriority(StrEnum):
    """Prioridades de manutenção."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class EquipmentMaintenance(Base):
    """
    Model para manutenções de equipamentos.

    Gerencia manutenções preventivas e corretivas,
    incluindo checklist, peças, custos e relatórios.
    """

    __tablename__ = "equipment_maintenances"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    maintenance_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    # Tipo e status
    maintenance_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default=MaintenanceStatus.SCHEDULED.value,
        nullable=False,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        default=MaintenancePriority.MEDIUM.value,
        nullable=False,
    )

    # Equipamento
    equipment_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )
    equipment_code: Mapped[str] = mapped_column(String(30), nullable=False)
    equipment_name: Mapped[str] = mapped_column(String(200), nullable=False)
    equipment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Cliente (onde o equipamento está instalado)
    client_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    client_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contract_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Descrição do problema/serviço
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    symptoms: Mapped[str | None] = mapped_column(Text, nullable=True)
    reported_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reported_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Agendamento
    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    scheduled_time: Mapped[str | None] = mapped_column(
        String(5),
        nullable=True,
    )  # HH:MM
    estimated_duration_hours: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    sla_deadline: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )  # Prazo SLA

    # Execução
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_duration_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Técnico
    technician_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    technician_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    team_members: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Checklist de manutenção
    checklist_template_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    checklist_items: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )  # [{item, checked, notes}]
    checklist_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )  # 0-100%

    # Diagnóstico
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_warranty_repair: Mapped[bool] = mapped_column(Boolean, default=False)

    # Ações realizadas
    actions_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    firmware_updated: Mapped[bool] = mapped_column(Boolean, default=False)
    firmware_version_before: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    firmware_version_after: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    settings_changed: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Peças substituídas
    parts_replaced: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )  # [{part_id, name, qty, unit_cost}]
    parts_requested: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )  # Peças solicitadas mas não entregues

    # Custos
    labor_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    parts_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    transport_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    other_costs: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_billable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )  # Cobrável do cliente?
    invoice_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Resultado
    equipment_status_after: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )  # Status do equipamento após manutenção
    problem_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    needs_followup: Mapped[bool] = mapped_column(Boolean, default=False)
    followup_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    followup_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Fotos
    photos_before: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    photos_after: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    photos_parts: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Relatório técnico
    technical_report: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Assinatura do cliente
    client_signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    signed_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Métricas
    response_time_hours: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )  # Tempo até iniciar
    resolution_time_hours: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )  # Tempo até concluir
    sla_met: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Recorrência (para preventivas)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_interval_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    next_maintenance_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    parent_maintenance_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Metadados
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    metadata_extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

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
    created_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Properties
    @property
    def is_completed(self) -> bool:
        """Verifica se a manutenção foi concluída."""
        return self.status == MaintenanceStatus.COMPLETED.value

    @property
    def is_overdue(self) -> bool:
        """Verifica se está atrasada (SLA)."""
        if not self.sla_deadline or self.is_completed:
            return False
        return datetime.utcnow() > self.sla_deadline

    @property
    def is_preventive(self) -> bool:
        """Verifica se é manutenção preventiva."""
        return self.maintenance_type == MaintenanceType.PREVENTIVA.value

    @property
    def is_corrective(self) -> bool:
        """Verifica se é manutenção corretiva."""
        return self.maintenance_type == MaintenanceType.CORRETIVA.value

    # Methods
    def start(self, technician_id: str, technician_name: str) -> None:
        """Inicia a manutenção."""
        self.status = MaintenanceStatus.IN_PROGRESS.value
        self.started_at = datetime.utcnow()
        self.technician_id = technician_id
        self.technician_name = technician_name

        # Calcular tempo de resposta
        if self.reported_at:
            delta = self.started_at - self.reported_at
            self.response_time_hours = round(delta.total_seconds() / 3600, 2)

    def complete(
        self,
        problem_resolved: bool = True,
        diagnosis: str | None = None,
        actions_taken: str | None = None,
    ) -> None:
        """Conclui a manutenção."""
        self.status = MaintenanceStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        self.problem_resolved = problem_resolved
        if diagnosis:
            self.diagnosis = diagnosis
        if actions_taken:
            self.actions_taken = actions_taken

        # Calcular duração
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.actual_duration_hours = round(delta.total_seconds() / 3600, 2)

        # Calcular tempo de resolução
        if self.reported_at:
            delta = self.completed_at - self.reported_at
            self.resolution_time_hours = round(delta.total_seconds() / 3600, 2)

        # Verificar SLA
        if self.sla_deadline:
            self.sla_met = self.completed_at <= self.sla_deadline

        # Programar próxima manutenção (se preventiva recorrente)
        if self.is_recurring and self.recurrence_interval_days:
            self.next_maintenance_date = self.completed_at + timedelta(days=self.recurrence_interval_days)

    def cancel(self, reason: str) -> None:
        """Cancela a manutenção."""
        self.status = MaintenanceStatus.CANCELLED.value
        self.notes = f"Cancelada: {reason}"

    def mark_waiting_parts(self, parts_requested: list) -> None:
        """Marca como aguardando peças."""
        self.status = MaintenanceStatus.WAITING_PARTS.value
        self.parts_requested = parts_requested

    def mark_failed(self, reason: str) -> None:
        """Marca como falha."""
        self.status = MaintenanceStatus.FAILED.value
        self.problem_resolved = False
        self.notes = f"Falha: {reason}"

    def add_part_replaced(
        self,
        part_id: str,
        name: str,
        quantity: int,
        unit_cost: float,
    ) -> None:
        """Adiciona peça substituída."""
        if not self.parts_replaced:
            self.parts_replaced = []
        self.parts_replaced.append(
            {
                "part_id": part_id,
                "name": name,
                "quantity": quantity,
                "unit_cost": unit_cost,
                "total_cost": quantity * unit_cost,
                "added_at": datetime.utcnow().isoformat(),
            }
        )

    def calculate_total_cost(self) -> float:
        """Calcula custo total da manutenção."""
        total = 0.0
        if self.labor_cost:
            total += self.labor_cost
        if self.parts_cost:
            total += self.parts_cost
        if self.transport_cost:
            total += self.transport_cost
        if self.other_costs:
            total += self.other_costs

        # Somar custos das peças substituídas
        if self.parts_replaced:
            for part in self.parts_replaced:
                total += part.get("total_cost", 0)

        self.total_cost = total
        return total

    def sign_by_client(self, signed_by: str, signature: str) -> None:
        """Registra assinatura do cliente."""
        self.signed_by = signed_by
        self.client_signature = signature
        self.signed_at = datetime.utcnow()

    def schedule_followup(self, followup_date: datetime, notes: str) -> None:
        """Agenda follow-up."""
        self.needs_followup = True
        self.followup_date = followup_date
        self.followup_notes = notes
