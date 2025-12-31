"""Model Application - Candidaturas."""

import enum
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    Integer,
    Enum,
    ForeignKey,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.database import Base
from core.models import TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from .job_position import JobPosition
    from .candidate import Candidate
    from .interview import Interview


class ApplicationStatus(str, enum.Enum):
    """Status da candidatura."""

    INSCRITO = "inscrito"
    TRIAGEM = "triagem"
    TRIAGEM_REPROVADO = "triagem_reprovado"
    ENTREVISTA_RH = "entrevista_rh"
    ENTREVISTA_TECNICA = "entrevista_tecnica"
    ENTREVISTA_GESTOR = "entrevista_gestor"
    TESTE = "teste"
    REFERENCIAS = "referencias"
    PROPOSTA = "proposta"
    PROPOSTA_RECUSADA = "proposta_recusada"
    CONTRATADO = "contratado"
    REPROVADO = "reprovado"
    DESISTIU = "desistiu"
    BANCO_TALENTOS = "banco_talentos"


class RejectionReason(str, enum.Enum):
    """Motivo de reprovação."""

    PERFIL_INADEQUADO = "perfil_inadequado"
    EXPERIENCIA_INSUFICIENTE = "experiencia_insuficiente"
    PRETENSAO_ALTA = "pretensao_alta"
    REPROVADO_ENTREVISTA = "reprovado_entrevista"
    REPROVADO_TESTE = "reprovado_teste"
    REFERENCIAS_NEGATIVAS = "referencias_negativas"
    VAGA_CANCELADA = "vaga_cancelada"
    VAGA_PREENCHIDA = "vaga_preenchida"
    DESISTENCIA = "desistencia"
    OUTRO = "outro"


class Application(Base, TimestampMixin, SoftDeleteMixin):
    """Model para candidaturas."""

    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Relacionamentos principais
    job_position_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("job_positions.id"),
        nullable=False,
    )
    candidate_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("candidates.id"),
        nullable=False,
    )

    # Status
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.INSCRITO
    )
    current_stage: Mapped[int] = mapped_column(Integer, default=1)
    current_stage_name: Mapped[Optional[str]] = mapped_column(String(100))

    # Scores
    matching_score: Mapped[int] = mapped_column(Integer, default=0)
    interview_score: Mapped[Optional[int]] = mapped_column(Integer)
    test_score: Mapped[Optional[int]] = mapped_column(Integer)
    final_score: Mapped[Optional[int]] = mapped_column(Integer)

    # Ranking
    ranking_position: Mapped[Optional[int]] = mapped_column(Integer)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    is_shortlisted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Carta de apresentação
    cover_letter: Mapped[Optional[str]] = mapped_column(Text)

    # Respostas a perguntas
    screening_answers: Mapped[Optional[List[dict]]] = mapped_column(JSON, default=list)

    # Histórico de status
    status_history: Mapped[Optional[List[dict]]] = mapped_column(JSON, default=list)

    # Notas e feedback
    recruiter_notes: Mapped[Optional[str]] = mapped_column(Text)
    hiring_manager_notes: Mapped[Optional[str]] = mapped_column(Text)
    feedback: Mapped[Optional[str]] = mapped_column(Text)

    # Reprovação
    rejection_reason: Mapped[Optional[RejectionReason]] = mapped_column(
        Enum(RejectionReason)
    )
    rejection_details: Mapped[Optional[str]] = mapped_column(Text)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rejected_by: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))

    # Proposta
    proposal_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    proposal_amount: Mapped[Optional[int]] = mapped_column(Integer)
    proposal_response_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    proposal_accepted: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Contratação
    hired_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Datas importantes
    applied_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    last_update_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Referência interna
    referral_employee_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))
    referral_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Responsáveis
    assigned_recruiter_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))
    created_by: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))

    # Relationships
    job_position: Mapped["JobPosition"] = relationship(
        "JobPosition", back_populates="applications"
    )
    candidate: Mapped["Candidate"] = relationship(
        "Candidate", back_populates="applications"
    )
    interviews: Mapped[List["Interview"]] = relationship(
        "Interview", back_populates="application", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<Application {self.id}: {self.status.value}>"

    @property
    def is_active(self) -> bool:
        """Verifica se candidatura está ativa."""
        inactive_statuses = [
            ApplicationStatus.TRIAGEM_REPROVADO,
            ApplicationStatus.PROPOSTA_RECUSADA,
            ApplicationStatus.CONTRATADO,
            ApplicationStatus.REPROVADO,
            ApplicationStatus.DESISTIU,
        ]
        return self.status not in inactive_statuses

    @property
    def is_in_process(self) -> bool:
        """Verifica se está em processo."""
        in_process_statuses = [
            ApplicationStatus.TRIAGEM,
            ApplicationStatus.ENTREVISTA_RH,
            ApplicationStatus.ENTREVISTA_TECNICA,
            ApplicationStatus.ENTREVISTA_GESTOR,
            ApplicationStatus.TESTE,
            ApplicationStatus.REFERENCIAS,
            ApplicationStatus.PROPOSTA,
        ]
        return self.status in in_process_statuses

    @property
    def is_hired(self) -> bool:
        """Verifica se foi contratado."""
        return self.status == ApplicationStatus.CONTRATADO

    @property
    def is_rejected(self) -> bool:
        """Verifica se foi reprovado."""
        rejected_statuses = [
            ApplicationStatus.TRIAGEM_REPROVADO,
            ApplicationStatus.REPROVADO,
            ApplicationStatus.PROPOSTA_RECUSADA,
        ]
        return self.status in rejected_statuses

    @property
    def days_in_process(self) -> int:
        """Dias em processo."""
        end_date = self.hired_at or self.rejected_at or datetime.utcnow()
        return (end_date - self.applied_at).days

    def advance_stage(self, new_status: ApplicationStatus, notes: str = None) -> None:
        """Avança para próximo estágio."""
        self._add_status_history(notes)
        self.status = new_status
        self.current_stage += 1
        self.current_stage_name = new_status.value
        self.last_update_at = datetime.utcnow()

    def reject(
        self, reason: RejectionReason, details: str = None, rejected_by: str = None
    ) -> None:
        """Reprova candidatura."""
        self._add_status_history(f"Reprovado: {reason.value}")
        self.status = ApplicationStatus.REPROVADO
        self.rejection_reason = reason
        self.rejection_details = details
        self.rejected_at = datetime.utcnow()
        self.rejected_by = rejected_by
        self.last_update_at = datetime.utcnow()

    def move_to_talent_pool(self, notes: str = None) -> None:
        """Move para banco de talentos."""
        self._add_status_history(notes or "Movido para banco de talentos")
        self.status = ApplicationStatus.BANCO_TALENTOS
        self.last_update_at = datetime.utcnow()

    def send_proposal(self, amount: int) -> None:
        """Envia proposta."""
        self._add_status_history(f"Proposta enviada: R$ {amount:,.2f}")
        self.status = ApplicationStatus.PROPOSTA
        self.proposal_sent_at = datetime.utcnow()
        self.proposal_amount = amount
        self.last_update_at = datetime.utcnow()

    def accept_proposal(self) -> None:
        """Aceita proposta."""
        self._add_status_history("Proposta aceita")
        self.proposal_response_at = datetime.utcnow()
        self.proposal_accepted = True
        self.last_update_at = datetime.utcnow()

    def reject_proposal(self, reason: str = None) -> None:
        """Recusa proposta."""
        self._add_status_history(f"Proposta recusada: {reason or 'Sem motivo'}")
        self.status = ApplicationStatus.PROPOSTA_RECUSADA
        self.proposal_response_at = datetime.utcnow()
        self.proposal_accepted = False
        self.last_update_at = datetime.utcnow()

    def hire(self, start_date: datetime = None) -> None:
        """Contrata candidato."""
        self._add_status_history("Contratado")
        self.status = ApplicationStatus.CONTRATADO
        self.hired_at = datetime.utcnow()
        self.start_date = start_date
        self.last_update_at = datetime.utcnow()

    def withdraw(self, reason: str = None) -> None:
        """Candidato desiste."""
        self._add_status_history(f"Desistiu: {reason or 'Sem motivo'}")
        self.status = ApplicationStatus.DESISTIU
        self.last_update_at = datetime.utcnow()

    def shortlist(self) -> None:
        """Adiciona à lista restrita."""
        self.is_shortlisted = True
        self.last_update_at = datetime.utcnow()

    def favorite(self) -> None:
        """Marca como favorito."""
        self.is_favorite = True
        self.last_update_at = datetime.utcnow()

    def unfavorite(self) -> None:
        """Remove dos favoritos."""
        self.is_favorite = False
        self.last_update_at = datetime.utcnow()

    def mark_viewed(self) -> None:
        """Marca como visualizado."""
        self.viewed_at = datetime.utcnow()

    def update_score(
        self,
        matching: int = None,
        interview: int = None,
        test: int = None,
    ) -> None:
        """Atualiza scores."""
        if matching is not None:
            self.matching_score = matching
        if interview is not None:
            self.interview_score = interview
        if test is not None:
            self.test_score = test

        # Calcula score final (média ponderada)
        scores = []
        weights = []
        if self.matching_score:
            scores.append(self.matching_score)
            weights.append(0.3)
        if self.interview_score:
            scores.append(self.interview_score)
            weights.append(0.4)
        if self.test_score:
            scores.append(self.test_score)
            weights.append(0.3)

        if scores:
            total_weight = sum(weights[: len(scores)])
            self.final_score = int(
                sum(s * w for s, w in zip(scores, weights)) / total_weight
            )

    def _add_status_history(self, notes: str = None) -> None:
        """Adiciona ao histórico de status."""
        if not self.status_history:
            self.status_history = []
        self.status_history.append(
            {
                "status": self.status.value,
                "stage": self.current_stage,
                "timestamp": datetime.utcnow().isoformat(),
                "notes": notes,
            }
        )
