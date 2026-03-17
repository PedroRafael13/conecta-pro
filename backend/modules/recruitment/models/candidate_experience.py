"""Model CandidateExperience - Experiencias profissionais."""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.models import TimestampMixin

if TYPE_CHECKING:
    from .candidate import Candidate


class CandidateExperience(Base, TimestampMixin):
    """Model para experiencias profissionais."""

    __tablename__ = "candidate_experiences"

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
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    achievements: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    employment_type: Mapped[str | None] = mapped_column(String(50))
    industry: Mapped[str | None] = mapped_column(String(100))
    salary: Mapped[float | None] = mapped_column(Numeric)

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="experiences")

    def __repr__(self) -> str:
        return f"<CandidateExperience {self.position} at {self.company}>"

    @property
    def duration_months(self) -> int:
        """Retorna duracao em meses."""
        if not self.start_date:
            return 0
        end = self.end_date or date.today()
        delta = end - self.start_date
        return max(1, delta.days // 30)
