"""Model Interview - Entrevistas."""

from datetime import date, datetime, time
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.models import SoftDeleteMixin, TimestampMixin

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


class Interview(Base, TimestampMixin, SoftDeleteMixin):
    """Model para entrevistas."""

    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Relacionamento
    application_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("applications.id"),
        nullable=False,
    )

    # Tipo e status
    interview_type: Mapped[InterviewType] = mapped_column(Enum(InterviewType), default=InterviewType.VIDEO)
    status: Mapped[InterviewStatus] = mapped_column(Enum(InterviewStatus), default=InterviewStatus.AGENDADA)
    result: Mapped[InterviewResult | None] = mapped_column(Enum(InterviewResult))

    # Agendamento
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    scheduled_time: Mapped[time] = mapped_column(Time, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    timezone: Mapped[str] = mapped_column(String(50), default="America/Sao_Paulo")

    # Local/Link
    location: Mapped[str | None] = mapped_column(String(300))
    meeting_link: Mapped[str | None] = mapped_column(String(500))
    meeting_platform: Mapped[str | None] = mapped_column(String(50))
    meeting_id: Mapped[str | None] = mapped_column(String(100))
    meeting_password: Mapped[str | None] = mapped_column(String(50))

    # Entrevistadores
    interviewer_ids: Mapped[list[str] | None] = mapped_column(ARRAY(UUID(as_uuid=False)), default=list)
    interviewer_names: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)
    lead_interviewer_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))

    # Roteiro
    script: Mapped[str | None] = mapped_column(Text)
    questions: Mapped[list[dict] | None] = mapped_column(JSON, default=list)
    competencies_to_assess: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)

    # Realização
    actual_start_time: Mapped[datetime | None] = mapped_column(DateTime)
    actual_end_time: Mapped[datetime | None] = mapped_column(DateTime)
    actual_duration_minutes: Mapped[int | None] = mapped_column(Integer)

    # Avaliação
    score: Mapped[int | None] = mapped_column(Integer)
    evaluation: Mapped[dict | None] = mapped_column(JSON)
    strengths: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)
    weaknesses: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)
    competency_scores: Mapped[dict | None] = mapped_column(JSON)

    # Feedback
    feedback: Mapped[str | None] = mapped_column(Text)
    recommendation: Mapped[str | None] = mapped_column(Text)
    internal_notes: Mapped[str | None] = mapped_column(Text)

    # Candidato
    candidate_feedback: Mapped[str | None] = mapped_column(Text)
    candidate_questions: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)

    # Confirmações
    candidate_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    candidate_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime)
    interviewer_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Lembretes
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_sent_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Cancelamento/Reagendamento
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancelled_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    rescheduled_from: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    reschedule_count: Mapped[int] = mapped_column(Integer, default=0)

    # Gravação
    is_recorded: Mapped[bool] = mapped_column(Boolean, default=False)
    recording_url: Mapped[str | None] = mapped_column(String(500))
    recording_consent: Mapped[bool] = mapped_column(Boolean, default=False)

    # Responsável
    created_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False))

    # Relationship
    application: Mapped["Application"] = relationship("Application", back_populates="interviews")

    def __repr__(self) -> str:
        return f"<Interview {self.id}: {self.interview_type.value} - {self.status.value}>"

    @property
    def scheduled_datetime(self) -> datetime:
        """Retorna data/hora agendada."""
        return datetime.combine(self.scheduled_date, self.scheduled_time)

    @property
    def is_past(self) -> bool:
        """Verifica se já passou."""
        return datetime.now() > self.scheduled_datetime

    @property
    def is_today(self) -> bool:
        """Verifica se é hoje."""
        return self.scheduled_date == date.today()

    @property
    def is_upcoming(self) -> bool:
        """Verifica se está próxima (até 7 dias)."""
        days_until = (self.scheduled_date - date.today()).days
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

    def confirm_candidate(self) -> None:
        """Confirma participação do candidato."""
        self.candidate_confirmed = True
        self.candidate_confirmed_at = datetime.utcnow()
        if self.interviewer_confirmed:
            self.status = InterviewStatus.CONFIRMADA

    def confirm_interviewer(self) -> None:
        """Confirma participação do entrevistador."""
        self.interviewer_confirmed = True
        if self.candidate_confirmed:
            self.status = InterviewStatus.CONFIRMADA

    def start(self) -> None:
        """Inicia entrevista."""
        self.status = InterviewStatus.EM_ANDAMENTO
        self.actual_start_time = datetime.utcnow()

    def complete(
        self,
        result: InterviewResult,
        score: int = None,
        feedback: str = None,
    ) -> None:
        """Finaliza entrevista."""
        self.status = InterviewStatus.REALIZADA
        self.result = result
        self.actual_end_time = datetime.utcnow()
        if self.actual_start_time:
            self.actual_duration_minutes = int((self.actual_end_time - self.actual_start_time).total_seconds() / 60)
        if score is not None:
            self.score = score
        if feedback:
            self.feedback = feedback

    def cancel(self, reason: str, cancelled_by: str) -> None:
        """Cancela entrevista."""
        self.status = InterviewStatus.CANCELADA
        self.cancelled_at = datetime.utcnow()
        self.cancelled_by = cancelled_by
        self.cancellation_reason = reason

    def reschedule(self, new_date: date, new_time: time) -> None:
        """Reagenda entrevista."""
        self.status = InterviewStatus.REAGENDADA
        self.scheduled_date = new_date
        self.scheduled_time = new_time
        self.reschedule_count += 1
        self.candidate_confirmed = False
        self.interviewer_confirmed = False

    def mark_no_show(self) -> None:
        """Marca como não compareceu."""
        self.status = InterviewStatus.NO_SHOW
        self.result = InterviewResult.INCONCLUSIVO

    def send_reminder(self) -> None:
        """Marca lembrete como enviado."""
        self.reminder_sent = True
        self.reminder_sent_at = datetime.utcnow()

    def add_evaluation(
        self,
        competency_scores: dict,
        strengths: list[str] = None,
        weaknesses: list[str] = None,
        recommendation: str = None,
    ) -> None:
        """Adiciona avaliação detalhada."""
        self.competency_scores = competency_scores
        if strengths:
            self.strengths = strengths
        if weaknesses:
            self.weaknesses = weaknesses
        if recommendation:
            self.recommendation = recommendation

        # Calcula score médio das competências
        if competency_scores:
            scores = [v for v in competency_scores.values() if isinstance(v, (int, float))]
            if scores:
                self.score = int(sum(scores) / len(scores))

    def set_recording(self, url: str, consent: bool = True) -> None:
        """Define gravação."""
        self.is_recorded = True
        self.recording_url = url
        self.recording_consent = consent
