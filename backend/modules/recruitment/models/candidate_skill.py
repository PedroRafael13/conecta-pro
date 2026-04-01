"""Model CandidateSkill - Habilidades do candidato."""

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from .candidate import Candidate


class SkillCategory(StrEnum):
    """Categoria da habilidade."""

    TECNICA = "tecnica"
    COMPORTAMENTAL = "comportamental"
    SEGURANCA = "seguranca"
    LIDERANCA = "lideranca"
    OUTRO = "outro"


class SkillLevel(StrEnum):
    """Nivel da habilidade."""

    BASICO = "basico"
    INTERMEDIARIO = "intermediario"
    AVANCADO = "avancado"
    EXPERT = "expert"


class CandidateSkill(Base):
    """Model para habilidades do candidato."""

    __tablename__ = "candidate_skills"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    candidate_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("candidates.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))
    level: Mapped[str | None] = mapped_column(String(50))
    years_of_experience: Mapped[int | None] = mapped_column(Integer)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    endorsements_count: Mapped[int | None] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="skills")

    def __repr__(self) -> str:
        return f"<CandidateSkill {self.name}: {self.level}>"

    @property
    def level_score(self) -> int:
        """Retorna score do nivel (1-4)."""
        scores = {"basico": 1, "intermediario": 2, "avancado": 3, "expert": 4}
        return scores.get(self.level or "", 1)
