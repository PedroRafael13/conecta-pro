"""Model CandidateEducation - Formação acadêmica."""

import enum
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    Date,
    Integer,
    Enum,
    ForeignKey,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.database import Base
from core.models import TimestampMixin

if TYPE_CHECKING:
    from .candidate import Candidate


class EducationLevel(str, enum.Enum):
    """Nível de formação."""

    FUNDAMENTAL = "fundamental"
    MEDIO = "medio"
    TECNICO = "tecnico"
    TECNOLOGICO = "tecnologico"
    GRADUACAO = "graduacao"
    POS_GRADUACAO = "pos_graduacao"
    MBA = "mba"
    MESTRADO = "mestrado"
    DOUTORADO = "doutorado"
    POS_DOUTORADO = "pos_doutorado"
    CURSO_LIVRE = "curso_livre"


class EducationStatus(str, enum.Enum):
    """Status da formação."""

    CURSANDO = "cursando"
    COMPLETO = "completo"
    TRANCADO = "trancado"
    INCOMPLETO = "incompleto"
    PREVISTO = "previsto"


class StudyPeriod(str, enum.Enum):
    """Período de estudo."""

    MATUTINO = "matutino"
    VESPERTINO = "vespertino"
    NOTURNO = "noturno"
    INTEGRAL = "integral"
    EAD = "ead"
    HIBRIDO = "hibrido"


class CandidateEducation(Base, TimestampMixin):
    """Model para formação acadêmica."""

    __tablename__ = "candidate_educations"

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

    # Instituição
    institution_name: Mapped[str] = mapped_column(String(200), nullable=False)
    institution_type: Mapped[Optional[str]] = mapped_column(String(50))
    institution_location: Mapped[Optional[str]] = mapped_column(String(200))
    institution_country: Mapped[str] = mapped_column(String(100), default="Brasil")

    # Curso
    course_name: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[EducationLevel] = mapped_column(
        Enum(EducationLevel), default=EducationLevel.GRADUACAO
    )
    area: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[EducationStatus] = mapped_column(
        Enum(EducationStatus), default=EducationStatus.COMPLETO
    )

    # Período
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    expected_end_date: Mapped[Optional[date]] = mapped_column(Date)
    study_period: Mapped[Optional[StudyPeriod]] = mapped_column(Enum(StudyPeriod))

    # Desempenho
    gpa: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    gpa_max: Mapped[float] = mapped_column(Numeric(4, 2), default=10.0)
    class_rank: Mapped[Optional[int]] = mapped_column(Integer)
    class_size: Mapped[Optional[int]] = mapped_column(Integer)

    # TCC/Tese
    thesis_title: Mapped[Optional[str]] = mapped_column(String(500))
    thesis_advisor: Mapped[Optional[str]] = mapped_column(String(200))
    thesis_abstract: Mapped[Optional[str]] = mapped_column(Text)

    # Atividades
    activities: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    honors: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    scholarships: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), default=list
    )

    # Intercâmbio
    has_exchange: Mapped[bool] = mapped_column(Boolean, default=False)
    exchange_institution: Mapped[Optional[str]] = mapped_column(String(200))
    exchange_country: Mapped[Optional[str]] = mapped_column(String(100))
    exchange_duration_months: Mapped[Optional[int]] = mapped_column(Integer)

    # Diploma
    diploma_number: Mapped[Optional[str]] = mapped_column(String(100))
    diploma_date: Mapped[Optional[date]] = mapped_column(Date)
    diploma_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Verificação
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    verified_by: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship
    candidate: Mapped["Candidate"] = relationship(
        "Candidate", back_populates="educations"
    )

    def __repr__(self) -> str:
        return f"<CandidateEducation {self.course_name} at {self.institution_name}>"

    @property
    def is_completed(self) -> bool:
        """Verifica se está completo."""
        return self.status == EducationStatus.COMPLETO

    @property
    def is_in_progress(self) -> bool:
        """Verifica se está cursando."""
        return self.status == EducationStatus.CURSANDO

    @property
    def duration_months(self) -> Optional[int]:
        """Retorna duração em meses."""
        if not self.start_date:
            return None
        end = self.end_date or self.expected_end_date or date.today()
        delta = end - self.start_date
        return max(1, delta.days // 30)

    @property
    def period_display(self) -> str:
        """Retorna período formatado."""
        if not self.start_date:
            return "Data não informada"

        start = self.start_date.strftime("%Y")
        if self.status == EducationStatus.CURSANDO:
            if self.expected_end_date:
                return f"{start} - Previsão: {self.expected_end_date.strftime('%Y')}"
            return f"{start} - Cursando"
        if self.end_date:
            return f"{start} - {self.end_date.strftime('%Y')}"
        return start

    @property
    def gpa_normalized(self) -> Optional[float]:
        """Retorna GPA normalizado (0-10)."""
        if self.gpa is None:
            return None
        return round((float(self.gpa) / float(self.gpa_max)) * 10, 2)

    @property
    def level_display(self) -> str:
        """Retorna nível formatado."""
        level_names = {
            EducationLevel.FUNDAMENTAL: "Ensino Fundamental",
            EducationLevel.MEDIO: "Ensino Médio",
            EducationLevel.TECNICO: "Curso Técnico",
            EducationLevel.TECNOLOGICO: "Tecnólogo",
            EducationLevel.GRADUACAO: "Graduação",
            EducationLevel.POS_GRADUACAO: "Pós-Graduação",
            EducationLevel.MBA: "MBA",
            EducationLevel.MESTRADO: "Mestrado",
            EducationLevel.DOUTORADO: "Doutorado",
            EducationLevel.POS_DOUTORADO: "Pós-Doutorado",
            EducationLevel.CURSO_LIVRE: "Curso Livre",
        }
        return level_names.get(self.level, self.level.value)

    @property
    def level_weight(self) -> int:
        """Retorna peso do nível (1-10)."""
        weights = {
            EducationLevel.FUNDAMENTAL: 1,
            EducationLevel.MEDIO: 2,
            EducationLevel.TECNICO: 3,
            EducationLevel.TECNOLOGICO: 4,
            EducationLevel.GRADUACAO: 5,
            EducationLevel.POS_GRADUACAO: 6,
            EducationLevel.MBA: 7,
            EducationLevel.MESTRADO: 8,
            EducationLevel.DOUTORADO: 9,
            EducationLevel.POS_DOUTORADO: 10,
            EducationLevel.CURSO_LIVRE: 2,
        }
        return weights.get(self.level, 1)

    def complete(self, end_date: date = None, gpa: float = None) -> None:
        """Marca como completo."""
        self.status = EducationStatus.COMPLETO
        self.end_date = end_date or date.today()
        if gpa is not None:
            self.gpa = gpa

    def set_in_progress(self, expected_end: date = None) -> None:
        """Marca como cursando."""
        self.status = EducationStatus.CURSANDO
        self.end_date = None
        if expected_end:
            self.expected_end_date = expected_end

    def lock(self) -> None:
        """Tranca curso."""
        self.status = EducationStatus.TRANCADO

    def verify(self, verified_by: str) -> None:
        """Verifica formação."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verified_by = verified_by

    def set_as_primary(self) -> None:
        """Define como formação principal."""
        self.is_primary = True

    def add_honor(self, honor: str) -> None:
        """Adiciona honraria."""
        if not self.honors:
            self.honors = []
        if honor not in self.honors:
            self.honors.append(honor)

    def add_activity(self, activity: str) -> None:
        """Adiciona atividade."""
        if not self.activities:
            self.activities = []
        if activity not in self.activities:
            self.activities.append(activity)

    def add_scholarship(self, scholarship: str) -> None:
        """Adiciona bolsa."""
        if not self.scholarships:
            self.scholarships = []
        if scholarship not in self.scholarships:
            self.scholarships.append(scholarship)

    def set_exchange(
        self,
        institution: str,
        country: str,
        duration_months: int,
    ) -> None:
        """Define intercâmbio."""
        self.has_exchange = True
        self.exchange_institution = institution
        self.exchange_country = country
        self.exchange_duration_months = duration_months

    def set_thesis(
        self,
        title: str,
        advisor: str = None,
        abstract: str = None,
    ) -> None:
        """Define TCC/Tese."""
        self.thesis_title = title
        self.thesis_advisor = advisor
        self.thesis_abstract = abstract

    def set_diploma(self, number: str, diploma_date: date = None) -> None:
        """Define diploma."""
        self.diploma_number = number
        self.diploma_date = diploma_date or date.today()
