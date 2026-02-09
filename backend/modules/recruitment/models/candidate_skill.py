"""Model CandidateSkill - Habilidades do candidato."""

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.models import TimestampMixin

if TYPE_CHECKING:
    from .candidate import Candidate


class SkillCategory(StrEnum):
    """Categoria da habilidade."""

    TECNICA = "tecnica"
    COMPORTAMENTAL = "comportamental"
    IDIOMA = "idioma"
    FERRAMENTA = "ferramenta"
    CERTIFICACAO = "certificacao"
    METODOLOGIA = "metodologia"
    GESTAO = "gestao"
    OUTRO = "outro"


class SkillLevel(StrEnum):
    """Nível da habilidade."""

    BASICO = "basico"
    INTERMEDIARIO = "intermediario"
    AVANCADO = "avancado"
    EXPERT = "expert"


class CandidateSkill(Base, TimestampMixin):
    """Model para habilidades do candidato."""

    __tablename__ = "candidate_skills"

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

    # Habilidade
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[SkillCategory] = mapped_column(Enum(SkillCategory), default=SkillCategory.TECNICA)
    level: Mapped[SkillLevel] = mapped_column(Enum(SkillLevel), default=SkillLevel.INTERMEDIARIO)

    # Experiência
    years_experience: Mapped[int | None] = mapped_column(Integer)
    months_experience: Mapped[int | None] = mapped_column(Integer)
    last_used_year: Mapped[int | None] = mapped_column(Integer)

    # Certificação
    is_certified: Mapped[bool] = mapped_column(Boolean, default=False)
    certification_name: Mapped[str | None] = mapped_column(String(200))
    certification_issuer: Mapped[str | None] = mapped_column(String(200))
    certification_date: Mapped[datetime | None] = mapped_column(DateTime)
    certification_expiry: Mapped[datetime | None] = mapped_column(DateTime)
    certification_url: Mapped[str | None] = mapped_column(String(500))

    # Validação
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    verified_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False))

    # Notas
    notes: Mapped[str | None] = mapped_column(Text)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationship
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="skills")

    def __repr__(self) -> str:
        return f"<CandidateSkill {self.name}: {self.level.value}>"

    @property
    def total_experience_months(self) -> int:
        """Retorna experiência total em meses."""
        years = self.years_experience or 0
        months = self.months_experience or 0
        return (years * 12) + months

    @property
    def experience_display(self) -> str:
        """Retorna experiência formatada."""
        years = self.years_experience or 0
        months = self.months_experience or 0
        if years and months:
            return f"{years} anos e {months} meses"
        if years:
            return f"{years} {'ano' if years == 1 else 'anos'}"
        if months:
            return f"{months} {'mês' if months == 1 else 'meses'}"
        return "Sem experiência"

    @property
    def is_certification_valid(self) -> bool:
        """Verifica se certificação é válida."""
        if not self.is_certified:
            return False
        if not self.certification_expiry:
            return True
        return self.certification_expiry > datetime.utcnow()

    @property
    def level_score(self) -> int:
        """Retorna score do nível (1-4)."""
        level_scores = {
            SkillLevel.BASICO: 1,
            SkillLevel.INTERMEDIARIO: 2,
            SkillLevel.AVANCADO: 3,
            SkillLevel.EXPERT: 4,
        }
        return level_scores.get(self.level, 1)

    def verify(self, verified_by: str) -> None:
        """Marca como verificado."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verified_by = verified_by

    def set_as_primary(self) -> None:
        """Define como habilidade principal."""
        self.is_primary = True

    def update_level(self, level: SkillLevel) -> None:
        """Atualiza nível."""
        self.level = level

    def add_certification(
        self,
        name: str,
        issuer: str,
        cert_date: datetime = None,
        expiry: datetime = None,
        url: str = None,
    ) -> None:
        """Adiciona certificação."""
        self.is_certified = True
        self.certification_name = name
        self.certification_issuer = issuer
        self.certification_date = cert_date
        self.certification_expiry = expiry
        self.certification_url = url
