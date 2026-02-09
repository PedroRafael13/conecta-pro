"""
Model de Ronda de Inspecao.

Representa uma ronda realizada por supervisores, inspetores, gerentes ou lideres
para verificar a operacao nos postos de servico.

Author: Conecta PRO Team
Date: 2026-01-23
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from .inspection_checkpoint import InspectionCheckpoint


class InspectionRoundStatus(StrEnum):
    """Status da ronda de inspecao."""

    AGENDADA = "agendada"
    EM_ANDAMENTO = "em_andamento"
    PAUSADA = "pausada"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class InspectorRole(StrEnum):
    """Cargo/funcao do inspetor que realiza a ronda."""

    GERENTE_OPERACIONAL = "gerente_operacional"
    SUPERVISOR_OPERACIONAL = "supervisor_operacional"
    INSPETOR_OPERACIONAL = "inspetor_operacional"
    LIDER_SERVICO = "lider_servico"


class InspectionRound(Base):
    """
    Modelo de Ronda de Inspecao.

    Representa uma visita de inspecao realizada por profissionais autorizados
    (gerentes, supervisores, inspetores, lideres) aos postos de trabalho para
    verificar a operacao, identificar falhas e registrar ocorrencias.

    Attributes:
        id: Identificador unico UUID.
        code: Codigo unico legivel (RON-2026-00001).
        tenant_id: ID do tenant/empresa.
        inspector_id: ID do usuario inspetor.
        inspector_name: Nome do inspetor (snapshot).
        inspector_role: Cargo do inspetor.
        status: Status da ronda.
        scheduled_date: Data agendada para a ronda.
        started_at: Inicio efetivo da ronda.
        completed_at: Conclusao da ronda.
        posts_to_visit: Lista de IDs dos postos a visitar.
        posts_visited: Lista de IDs dos postos ja visitados.
        total_checkpoints: Total de checkpoints realizados.
        total_occurrences: Total de ocorrencias registradas.
        total_disciplinary_actions: Total de medidas disciplinares.
        observations: Observacoes gerais da ronda.
        route_coordinates: Coordenadas GPS do trajeto.
    """

    __tablename__ = "inspection_rounds"
    __table_args__ = (
        Index("ix_inspection_rounds_tenant_status", "tenant_id", "status"),
        Index("ix_inspection_rounds_inspector", "inspector_id"),
        Index("ix_inspection_rounds_scheduled", "scheduled_date"),
        Index("ix_inspection_rounds_created", "created_at"),
    )

    # === Identificacao ===
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )

    # === Inspetor ===
    inspector_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    inspector_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    inspector_role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=InspectorRole.SUPERVISOR_OPERACIONAL.value,
    )

    # === Status e Datas ===
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=InspectionRoundStatus.AGENDADA.value,
        index=True,
    )
    scheduled_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    paused_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # === Postos ===
    posts_to_visit: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
    )
    posts_visited: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
    )

    # === Contadores ===
    total_checkpoints: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_occurrences: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_disciplinary_actions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_employees_checked: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # === Observacoes ===
    observations: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # === Geolocalizacao ===
    start_latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    start_longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    end_latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    end_longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    route_coordinates: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
    )
    total_distance_km: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # === Metadados ===
    extra_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )

    # === Controle ===
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )
    created_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # === Relacionamentos ===
    checkpoints: Mapped[list[InspectionCheckpoint]] = relationship(
        "InspectionCheckpoint",
        back_populates="inspection_round",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="InspectionCheckpoint.created_at",
    )

    def __repr__(self) -> str:
        return f"<InspectionRound {self.code} - {self.status}>"

    # === Properties ===

    @property
    def is_in_progress(self) -> bool:
        """Verifica se a ronda esta em andamento."""
        return self.status == InspectionRoundStatus.EM_ANDAMENTO.value

    @property
    def is_completed(self) -> bool:
        """Verifica se a ronda foi concluida."""
        return self.status == InspectionRoundStatus.CONCLUIDA.value

    @property
    def posts_remaining(self) -> list:
        """Retorna postos ainda nao visitados."""
        visited = set(self.posts_visited or [])
        to_visit = self.posts_to_visit or []
        return [p for p in to_visit if p not in visited]

    @property
    def progress_percentage(self) -> float:
        """Calcula percentual de progresso."""
        if not self.posts_to_visit:
            return 0.0
        total = len(self.posts_to_visit)
        visited = len(self.posts_visited or [])
        return round((visited / total) * 100, 1) if total > 0 else 0.0

    @property
    def inspector_role_display(self) -> str:
        """Retorna nome de exibicao do cargo."""
        display_names = {
            InspectorRole.GERENTE_OPERACIONAL.value: "Gerente Operacional",
            InspectorRole.SUPERVISOR_OPERACIONAL.value: "Supervisor Operacional",
            InspectorRole.INSPETOR_OPERACIONAL.value: "Inspetor Operacional",
            InspectorRole.LIDER_SERVICO.value: "Lider de Servico",
        }
        return display_names.get(self.inspector_role, self.inspector_role)

    @property
    def status_display(self) -> str:
        """Retorna nome de exibicao do status."""
        display_names = {
            InspectionRoundStatus.AGENDADA.value: "Agendada",
            InspectionRoundStatus.EM_ANDAMENTO.value: "Em Andamento",
            InspectionRoundStatus.PAUSADA.value: "Pausada",
            InspectionRoundStatus.CONCLUIDA.value: "Concluida",
            InspectionRoundStatus.CANCELADA.value: "Cancelada",
        }
        return display_names.get(self.status, self.status)

    # === Methods ===

    def start(self, latitude: float | None = None, longitude: float | None = None) -> None:
        """Inicia a ronda."""
        self.status = InspectionRoundStatus.EM_ANDAMENTO.value
        self.started_at = datetime.utcnow()
        if latitude and longitude:
            self.start_latitude = latitude
            self.start_longitude = longitude

    def pause(self) -> None:
        """Pausa a ronda."""
        if self.status == InspectionRoundStatus.EM_ANDAMENTO.value:
            self.status = InspectionRoundStatus.PAUSADA.value
            self.paused_at = datetime.utcnow()

    def resume(self) -> None:
        """Retoma a ronda pausada."""
        if self.status == InspectionRoundStatus.PAUSADA.value:
            self.status = InspectionRoundStatus.EM_ANDAMENTO.value

    def complete(
        self,
        summary: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> None:
        """Conclui a ronda."""
        self.status = InspectionRoundStatus.CONCLUIDA.value
        self.completed_at = datetime.utcnow()
        if summary:
            self.summary = summary
        if latitude and longitude:
            self.end_latitude = latitude
            self.end_longitude = longitude

        # Calcular duracao
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_minutes = int(delta.total_seconds() / 60)

    def cancel(self, reason: str | None = None) -> None:
        """Cancela a ronda."""
        self.status = InspectionRoundStatus.CANCELADA.value
        if reason:
            self.extra_data = self.extra_data or {}
            self.extra_data["cancellation_reason"] = reason
            self.extra_data["cancelled_at"] = datetime.utcnow().isoformat()

    def add_visited_post(self, post_id: str) -> None:
        """Adiciona um posto visitado."""
        if self.posts_visited is None:
            self.posts_visited = []
        if post_id not in self.posts_visited:
            self.posts_visited.append(post_id)

    def add_route_coordinate(self, latitude: float, longitude: float) -> None:
        """Adiciona coordenada ao trajeto."""
        if self.route_coordinates is None:
            self.route_coordinates = []
        self.route_coordinates.append(
            {
                "lat": latitude,
                "lng": longitude,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def increment_occurrences(self) -> None:
        """Incrementa contador de ocorrencias."""
        self.total_occurrences += 1

    def increment_disciplinary_actions(self) -> None:
        """Incrementa contador de medidas disciplinares."""
        self.total_disciplinary_actions += 1

    def increment_employees_checked(self) -> None:
        """Incrementa contador de funcionarios verificados."""
        self.total_employees_checked += 1

    @classmethod
    def generate_code(cls, year: int, sequence: int) -> str:
        """Gera codigo unico para ronda."""
        return f"RON-{year}-{sequence:05d}"
