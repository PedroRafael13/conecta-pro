"""Model CandidateExperience - Experiências profissionais."""

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.models import TimestampMixin

if TYPE_CHECKING:
    from .candidate import Candidate


class EmploymentType(StrEnum):
    """Tipo de contratação."""

    CLT = "clt"
    PJ = "pj"
    ESTAGIO = "estagio"
    TRAINEE = "trainee"
    FREELANCER = "freelancer"
    TEMPORARIO = "temporario"
    TERCEIRIZADO = "terceirizado"
    AUTONOMO = "autonomo"
    VOLUNTARIO = "voluntario"


class ExperienceLevel(StrEnum):
    """Nível da experiência."""

    ESTAGIARIO = "estagiario"
    JUNIOR = "junior"
    PLENO = "pleno"
    SENIOR = "senior"
    ESPECIALISTA = "especialista"
    COORDENADOR = "coordenador"
    GERENTE = "gerente"
    DIRETOR = "diretor"
    C_LEVEL = "c_level"


class CandidateExperience(Base, TimestampMixin):
    """Model para experiências profissionais."""

    __tablename__ = "candidate_experiences"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Relacionamento
    candidate_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("candidates.id"),
        nullable=False,
    )

    # Empresa
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    company_industry: Mapped[str | None] = mapped_column(String(100))
    company_size: Mapped[str | None] = mapped_column(String(50))
    company_location: Mapped[str | None] = mapped_column(String(200))
    company_linkedin: Mapped[str | None] = mapped_column(String(300))

    # Cargo
    job_title: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100))
    level: Mapped[ExperienceLevel | None] = mapped_column(Enum(ExperienceLevel))
    employment_type: Mapped[EmploymentType] = mapped_column(Enum(EmploymentType), default=EmploymentType.CLT)

    # Período
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)

    # Descrição
    description: Mapped[str | None] = mapped_column(Text)
    responsibilities: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)
    achievements: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)
    technologies: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)

    # Métricas
    team_size: Mapped[int | None] = mapped_column(Integer)
    direct_reports: Mapped[int | None] = mapped_column(Integer)
    budget_managed: Mapped[str | None] = mapped_column(String(100))

    # Motivo da saída
    leaving_reason: Mapped[str | None] = mapped_column(String(200))
    exit_type: Mapped[str | None] = mapped_column(String(50))

    # Referência
    reference_name: Mapped[str | None] = mapped_column(String(200))
    reference_title: Mapped[str | None] = mapped_column(String(200))
    reference_phone: Mapped[str | None] = mapped_column(String(20))
    reference_email: Mapped[str | None] = mapped_column(String(255))
    can_contact_reference: Mapped[bool] = mapped_column(Boolean, default=True)

    # Verificação
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    verified_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    verification_notes: Mapped[str | None] = mapped_column(Text)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="experiences")

    def __repr__(self) -> str:
        return f"<CandidateExperience {self.job_title} at {self.company_name}>"

    @property
    def duration_months(self) -> int:
        """Retorna duração em meses."""
        end = self.end_date or date.today()
        delta = end - self.start_date
        return max(1, delta.days // 30)

    @property
    def duration_years(self) -> float:
        """Retorna duração em anos."""
        return round(self.duration_months / 12, 1)

    @property
    def duration_display(self) -> str:
        """Retorna duração formatada."""
        months = self.duration_months
        years = months // 12
        remaining_months = months % 12

        if years and remaining_months:
            year_label = "ano" if years == 1 else "anos"
            month_label = "mês" if remaining_months == 1 else "meses"
            return f"{years} {year_label} e {remaining_months} {month_label}"
        if years:
            return f"{years} {'ano' if years == 1 else 'anos'}"
        return f"{remaining_months} {'mês' if remaining_months == 1 else 'meses'}"

    @property
    def period_display(self) -> str:
        """Retorna período formatado."""
        start = self.start_date.strftime("%b/%Y")
        if self.is_current:
            return f"{start} - Atual"
        end = self.end_date.strftime("%b/%Y") if self.end_date else "Atual"
        return f"{start} - {end}"

    @property
    def has_reference(self) -> bool:
        """Verifica se tem referência."""
        return bool(self.reference_name and (self.reference_phone or self.reference_email))

    def set_as_current(self) -> None:
        """Define como emprego atual."""
        self.is_current = True
        self.end_date = None

    def end_employment(self, end_date: date = None, reason: str = None) -> None:
        """Encerra emprego."""
        self.is_current = False
        self.end_date = end_date or date.today()
        if reason:
            self.leaving_reason = reason

    def verify(self, verified_by: str, notes: str = None) -> None:
        """Verifica experiência."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verified_by = verified_by
        if notes:
            self.verification_notes = notes

    def add_achievement(self, achievement: str) -> None:
        """Adiciona conquista."""
        if not self.achievements:
            self.achievements = []
        if achievement not in self.achievements:
            self.achievements.append(achievement)

    def add_responsibility(self, responsibility: str) -> None:
        """Adiciona responsabilidade."""
        if not self.responsibilities:
            self.responsibilities = []
        if responsibility not in self.responsibilities:
            self.responsibilities.append(responsibility)

    def add_technology(self, technology: str) -> None:
        """Adiciona tecnologia."""
        if not self.technologies:
            self.technologies = []
        if technology not in self.technologies:
            self.technologies.append(technology)

    def set_reference(
        self,
        name: str,
        title: str = None,
        phone: str = None,
        email: str = None,
        can_contact: bool = True,
    ) -> None:
        """Define referência."""
        self.reference_name = name
        self.reference_title = title
        self.reference_phone = phone
        self.reference_email = email
        self.can_contact_reference = can_contact
