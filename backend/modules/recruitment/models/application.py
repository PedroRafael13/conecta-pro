"""Model Application - Candidaturas.

Reescrito para refletir o schema real do banco de dados (15/03/2026).
Corrige mismatch entre model e DB que causava erros nos endpoints.
Colunas fantasma removidas, hybrid_property is_deleted adicionada para
compatibilidade com repository queries existentes.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from .candidate import Candidate
    from .job_position import JobPosition


class ApplicationStatus(StrEnum):
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


class RejectionReason(StrEnum):
    """Motivo de reprovacao."""

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


class Application(Base):
    """Model para candidaturas — reflete schema real do banco."""

    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Tenant
    tenant_id: Mapped[str | None] = mapped_column(String)

    # Relacionamentos principais (FKs)
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

    # Status e etapa
    status: Mapped[str | None] = mapped_column(String)
    current_step: Mapped[str | None] = mapped_column(String)
    step_order: Mapped[int | None] = mapped_column(Integer)

    # Notas e avaliacao
    recruiter_notes: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[int | None] = mapped_column(Integer)

    # AI matching
    ai_match_score: Mapped[Decimal | None] = mapped_column(Numeric)
    ai_match_details: Mapped[dict | None] = mapped_column(JSONB)

    # Historico de etapas
    step_history: Mapped[dict | None] = mapped_column(JSONB)

    # Carta de apresentacao e pretensao
    cover_letter: Mapped[str | None] = mapped_column(Text)
    salary_expectation: Mapped[Decimal | None] = mapped_column(Numeric)
    availability_date: Mapped[date | None] = mapped_column(Date)

    # Datas do pipeline
    applied_at: Mapped[datetime | None] = mapped_column(DateTime)
    screened_at: Mapped[datetime | None] = mapped_column(DateTime)
    interviewed_at: Mapped[datetime | None] = mapped_column(DateTime)
    offered_at: Mapped[datetime | None] = mapped_column(DateTime)
    hired_at: Mapped[datetime | None] = mapped_column(DateTime)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Motivos de rejeicao/desistencia
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    withdrawal_reason: Mapped[str | None] = mapped_column(Text)

    # Responsavel
    assigned_to_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))

    # Flags
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)

    # Timestamps (sem mixin — colunas explicitas)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default="now()")
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------
    job_position: Mapped["JobPosition"] = relationship(
        "JobPosition",
        back_populates="applications",
    )
    candidate: Mapped["Candidate"] = relationship(
        "Candidate",
        back_populates="applications",
    )
    interviews: Mapped[list] = relationship(
        "modules.recruitment.models.interview.Interview",
        back_populates="application",
        lazy="selectin",
    )

    # -------------------------------------------------------------------------
    # Hybrid property: is_deleted (compatibilidade com repository queries)
    # O banco usa is_active (bool). O repository filtra por is_deleted.is_(False).
    # is_deleted == NOT is_active, portanto is_deleted.is_(False) == is_active.is_(True).
    # -------------------------------------------------------------------------
    @hybrid_property
    def is_deleted(self) -> bool:
        """Compatibilidade: mapeia is_deleted para NOT is_active."""
        return not self.is_active

    @is_deleted.expression  # type: ignore[no-redef]
    def is_deleted(cls):  # noqa: N805
        """SQL expression: is_deleted == NOT is_active."""
        return cls.is_active.is_not(True)

    def __repr__(self) -> str:
        return f"<Application {self.id}: {self.status}>"

    # -------------------------------------------------------------------------
    # Convenience properties (compatibilidade com services existentes)
    # -------------------------------------------------------------------------
    @property
    def is_in_process(self) -> bool:
        """Verifica se esta em processo ativo no pipeline."""
        in_process = {
            ApplicationStatus.TRIAGEM,
            ApplicationStatus.ENTREVISTA_RH,
            ApplicationStatus.ENTREVISTA_TECNICA,
            ApplicationStatus.ENTREVISTA_GESTOR,
            ApplicationStatus.TESTE,
            ApplicationStatus.REFERENCIAS,
            ApplicationStatus.PROPOSTA,
        }
        return self.status in in_process

    @property
    def is_hired(self) -> bool:
        """Verifica se foi contratado."""
        return self.status == ApplicationStatus.CONTRATADO

    @property
    def is_rejected(self) -> bool:
        """Verifica se foi reprovado."""
        return self.status in {
            ApplicationStatus.TRIAGEM_REPROVADO,
            ApplicationStatus.REPROVADO,
            ApplicationStatus.PROPOSTA_RECUSADA,
        }

    @property
    def days_in_process(self) -> int | None:
        """Dias em processo desde applied_at."""
        if not self.applied_at:
            return None
        end_date = self.hired_at or self.rejected_at or datetime.utcnow()
        return (end_date - self.applied_at).days

    # -------------------------------------------------------------------------
    # Mutation helpers (compatibilidade com services que chamam esses metodos)
    # Simplificados para trabalhar apenas com colunas reais do banco.
    # -------------------------------------------------------------------------
    def advance_stage(self, new_status: str, notes: str = None) -> None:
        """Avanca para proximo estagio do pipeline."""
        self.status = new_status if isinstance(new_status, str) else new_status.value
        self.current_step = self.status
        if self.step_order is not None:
            self.step_order += 1
        else:
            self.step_order = 1
        if notes:
            self.recruiter_notes = notes
        self._append_step_history(notes)
        self.updated_at = datetime.utcnow()

    def reject(self, reason: str = None, details: str = None, **_kwargs) -> None:
        """Reprova candidatura."""
        self.status = ApplicationStatus.REPROVADO
        self.rejection_reason = reason if isinstance(reason, str) else (reason.value if reason else None)
        self.rejected_at = datetime.utcnow()
        self.current_step = ApplicationStatus.REPROVADO
        self._append_step_history(details or f"Reprovado: {self.rejection_reason}")
        self.updated_at = datetime.utcnow()

    def hire(self, **_kwargs) -> None:
        """Contrata candidato."""
        self.status = ApplicationStatus.CONTRATADO
        self.hired_at = datetime.utcnow()
        self.current_step = ApplicationStatus.CONTRATADO
        self._append_step_history("Contratado")
        self.updated_at = datetime.utcnow()

    def withdraw(self, reason: str = None) -> None:
        """Candidato desiste."""
        self.status = ApplicationStatus.DESISTIU
        self.withdrawal_reason = reason
        self.withdrawn_at = datetime.utcnow()
        self.current_step = ApplicationStatus.DESISTIU
        self._append_step_history(f"Desistiu: {reason or 'Sem motivo'}")
        self.updated_at = datetime.utcnow()

    def move_to_talent_pool(self, notes: str = None) -> None:
        """Move para banco de talentos."""
        self.status = ApplicationStatus.BANCO_TALENTOS
        self.current_step = ApplicationStatus.BANCO_TALENTOS
        self._append_step_history(notes or "Movido para banco de talentos")
        self.updated_at = datetime.utcnow()

    def send_proposal(self, amount: Decimal = None) -> None:
        """Envia proposta."""
        self.status = ApplicationStatus.PROPOSTA
        self.offered_at = datetime.utcnow()
        self.current_step = ApplicationStatus.PROPOSTA
        if amount is not None:
            self.salary_expectation = amount
        self._append_step_history(f"Proposta enviada: R$ {amount}" if amount else "Proposta enviada")
        self.updated_at = datetime.utcnow()

    def accept_proposal(self) -> None:
        """Aceita proposta (avanca para contratado)."""
        self.hire()

    def reject_proposal(self, reason: str = None) -> None:
        """Recusa proposta."""
        self.status = ApplicationStatus.PROPOSTA_RECUSADA
        self.current_step = ApplicationStatus.PROPOSTA_RECUSADA
        self.withdrawal_reason = reason
        self._append_step_history(f"Proposta recusada: {reason or 'Sem motivo'}")
        self.updated_at = datetime.utcnow()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _append_step_history(self, notes: str = None) -> None:
        """Adiciona entrada ao step_history (JSONB)."""
        if not self.step_history:
            self.step_history = []
        if isinstance(self.step_history, list):
            self.step_history = [
                *self.step_history,
                {
                    "status": self.status,
                    "step": self.current_step,
                    "step_order": self.step_order,
                    "timestamp": datetime.utcnow().isoformat(),
                    "notes": notes,
                },
            ]
