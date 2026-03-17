"""Model Interview - Entrevistas.

Reescrito para refletir o schema real do banco de dados (15/03/2026).
Corrige mismatch que causava erros nos endpoints de entrevistas.
"""

from datetime import date, datetime, time
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from .application import Application


class InterviewType(StrEnum):
    """Tipo de entrevista."""

    TELEFONE = "telefone"
    VIDEO = "video"
    PRESENCIAL = "presencial"
    TECNICA = "tecnica"
    COMPORTAMENTAL = "comportamental"
    CASE = "case"
    PAINEL = "painel"
    DINAMICA = "dinamica"


class InterviewStatus(StrEnum):
    """Status da entrevista."""

    AGENDADA = "agendada"
    CONFIRMADA = "confirmada"
    EM_ANDAMENTO = "em_andamento"
    REALIZADA = "realizada"
    CANCELADA = "cancelada"
    REAGENDADA = "reagendada"
    NO_SHOW = "no_show"
    ADIADA = "adiada"


class InterviewResult(StrEnum):
    """Resultado da entrevista."""

    APROVADO = "aprovado"
    REPROVADO = "reprovado"
    APROVADO_COM_RESSALVAS = "aprovado_com_ressalvas"
    PENDENTE_AVALIACAO = "pendente_avaliacao"
    INCONCLUSIVO = "inconclusivo"


class Interview(Base):
    """Model para entrevistas — reflete schema real do banco."""

    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Tenant
    tenant_id: Mapped[str | None] = mapped_column(String)

    # Relacionamento
    application_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("applications.id"),
        nullable=False,
    )

    # Tipo, formato e status
    interview_type: Mapped[str] = mapped_column(String, nullable=False)
    format: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str | None] = mapped_column(String)
    result: Mapped[str | None] = mapped_column(String)

    # Agendamento
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)

    # Local/Link
    location: Mapped[str | None] = mapped_column(String)
    meeting_url: Mapped[str | None] = mapped_column(String)

    # Entrevistadores
    interviewer_ids: Mapped[list[str] | None] = mapped_column(ARRAY(UUID(as_uuid=False)))
    interviewer_notes: Mapped[dict | None] = mapped_column(JSONB)

    # Feedback e avaliacao
    feedback: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[int | None] = mapped_column(Integer)
    transcript: Mapped[str | None] = mapped_column(Text)

    # Realizacao
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Cancelamento
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancellation_reason: Mapped[str | None] = mapped_column(Text)

    # Gravacao
    recording_url: Mapped[str | None] = mapped_column(String)

    # Timestamps
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default="now()")
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationship
    application: Mapped["Application"] = relationship("Application", back_populates="interviews")

    # -------------------------------------------------------------------------
    # Compatibility: is_deleted (DB nao tem coluna — repositorio filtra por ela)
    # -------------------------------------------------------------------------
    @hybrid_property
    def is_deleted(self) -> bool:
        """Sempre False — tabela interviews nao possui soft delete."""
        return False

    @is_deleted.expression  # type: ignore[no-redef]
    def is_deleted(cls):  # noqa: N805
        """Expressao SQL: sempre False para queries com .is_(False)."""
        from sqlalchemy import literal

        return literal(False)

    # -------------------------------------------------------------------------
    # Compatibility properties (codigo legado usa esses nomes)
    # -------------------------------------------------------------------------
    @property
    def scheduled_date(self) -> date | None:
        """Extrai date de scheduled_at (compatibilidade)."""
        if self.scheduled_at is None:
            return None
        return self.scheduled_at.date()

    @property
    def scheduled_time(self) -> time | None:
        """Extrai time de scheduled_at (compatibilidade)."""
        if self.scheduled_at is None:
            return None
        return self.scheduled_at.time()

    @property
    def score(self) -> int | None:
        """Alias para rating (compatibilidade)."""
        return self.rating

    @score.setter
    def score(self, value: int | None) -> None:
        """Setter para score → rating."""
        self.rating = value

    @property
    def scheduled_datetime(self) -> datetime | None:
        """Retorna data/hora agendada (alias direto para scheduled_at)."""
        return self.scheduled_at

    def __repr__(self) -> str:
        return f"<Interview {self.id}: {self.interview_type} - {self.status}>"

    # -------------------------------------------------------------------------
    # Convenience properties
    # -------------------------------------------------------------------------
    @property
    def is_past(self) -> bool:
        """Verifica se ja passou."""
        if self.scheduled_at is None:
            return False
        return datetime.utcnow() > self.scheduled_at

    @property
    def is_today(self) -> bool:
        """Verifica se e hoje."""
        if self.scheduled_at is None:
            return False
        return self.scheduled_at.date() == date.today()

    @property
    def is_upcoming(self) -> bool:
        """Verifica se esta proxima (ate 7 dias)."""
        if self.scheduled_at is None:
            return False
        days_until = (self.scheduled_at.date() - date.today()).days
        return 0 <= days_until <= 7

    @property
    def is_pending_result(self) -> bool:
        """Verifica se aguarda resultado."""
        return self.status == InterviewStatus.REALIZADA and self.result == InterviewResult.PENDENTE_AVALIACAO

    @property
    def was_successful(self) -> bool:
        """Verifica se foi bem-sucedida."""
        return self.result in [
            InterviewResult.APROVADO,
            InterviewResult.APROVADO_COM_RESSALVAS,
        ]

    # -------------------------------------------------------------------------
    # Action methods
    # -------------------------------------------------------------------------
    def start(self) -> None:
        """Inicia entrevista."""
        self.status = InterviewStatus.EM_ANDAMENTO
        self.started_at = datetime.utcnow()

    def complete(
        self,
        result: InterviewResult,
        rating: int | None = None,
        feedback: str | None = None,
    ) -> None:
        """Finaliza entrevista."""
        self.status = InterviewStatus.REALIZADA
        self.result = result
        self.ended_at = datetime.utcnow()
        if rating is not None:
            self.rating = rating
        if feedback:
            self.feedback = feedback

    def cancel(self, reason: str, cancelled_by: str | None = None) -> None:
        """Cancela entrevista.

        cancelled_by aceito por compatibilidade mas nao persiste (coluna nao existe).
        """
        self.status = InterviewStatus.CANCELADA
        self.cancelled_at = datetime.utcnow()
        self.cancellation_reason = reason

    def reschedule(self, new_datetime: datetime) -> None:
        """Reagenda entrevista.

        Aceita datetime completo (scheduled_at e timestamp, nao date+time separados).
        """
        self.status = InterviewStatus.REAGENDADA
        self.scheduled_at = new_datetime

    def mark_no_show(self) -> None:
        """Marca como nao compareceu."""
        self.status = InterviewStatus.NO_SHOW
        self.result = InterviewResult.INCONCLUSIVO

    def set_recording(self, url: str) -> None:
        """Define URL da gravacao."""
        self.recording_url = url
