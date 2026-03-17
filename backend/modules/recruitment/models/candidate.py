"""Model Candidate - Candidatos.

Reescrito para refletir o schema real do banco de dados (15/03/2026).
Corrige mismatch que causava 500 em todos os endpoints de recruitment.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class CandidateStatus(StrEnum):
    """Status do candidato."""

    ATIVO = "ativo"
    INATIVO = "inativo"
    CONTRATADO = "contratado"
    BLOQUEADO = "bloqueado"
    ARQUIVADO = "arquivado"


class CandidateSource(StrEnum):
    """Origem do candidato."""

    SITE = "site"
    LINKEDIN = "linkedin"
    INDICACAO = "indicacao"
    BANCO_TALENTOS = "banco_talentos"
    FEIRA_EMPREGO = "feira_emprego"
    AGENCIA = "agencia"
    HEADHUNTER = "headhunter"
    REDE_SOCIAL = "rede_social"
    EMAIL = "email"
    PRESENCIAL = "presencial"
    OUTRO = "outro"


class Gender(StrEnum):
    """Genero."""

    MASCULINO = "masculino"
    FEMININO = "feminino"
    NAO_BINARIO = "nao_binario"
    PREFIRO_NAO_DIZER = "prefiro_nao_dizer"


class MaritalStatus(StrEnum):
    """Estado civil."""

    SOLTEIRO = "solteiro"
    CASADO = "casado"
    DIVORCIADO = "divorciado"
    VIUVO = "viuvo"
    UNIAO_ESTAVEL = "uniao_estavel"


if TYPE_CHECKING:
    from .application import Application
    from .candidate_education import CandidateEducation
    from .candidate_experience import CandidateExperience
    from .candidate_skill import CandidateSkill


class Candidate(Base):
    """Model para candidatos — reflete schema real do banco."""

    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Tenant
    tenant_id: Mapped[str | None] = mapped_column(String(50))

    # Dados pessoais
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    whatsapp: Mapped[str | None] = mapped_column(String(20))
    cpf: Mapped[str | None] = mapped_column(String(14), unique=True)
    rg: Mapped[str | None] = mapped_column(String(20))
    birth_date: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(30))
    marital_status: Mapped[str | None] = mapped_column(String(30))

    # Endereco
    address: Mapped[str | None] = mapped_column(String(300))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(2))
    zip_code: Mapped[str | None] = mapped_column(String(10))
    country: Mapped[str | None] = mapped_column(String(50))

    # Profissional
    headline: Mapped[str | None] = mapped_column(String(200))
    summary: Mapped[str | None] = mapped_column(Text)
    current_company: Mapped[str | None] = mapped_column(String(200))
    current_position: Mapped[str | None] = mapped_column(String(200))
    linkedin_url: Mapped[str | None] = mapped_column(String(300))
    linkedin_id: Mapped[str | None] = mapped_column(String(100))
    github_url: Mapped[str | None] = mapped_column(String(300))
    portfolio_url: Mapped[str | None] = mapped_column(String(300))

    # Curriculo
    resume_url: Mapped[str | None] = mapped_column(String(500))
    resume_text: Mapped[str | None] = mapped_column(Text)
    resume_parsed: Mapped[dict | None] = mapped_column(JSONB)
    photo_url: Mapped[str | None] = mapped_column(String(500))

    # Pretensao
    salary_expectation: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    # Disponibilidade
    availability: Mapped[str | None] = mapped_column(String(50))

    # Status e origem
    status: Mapped[str | None] = mapped_column(String(30))
    source: Mapped[str | None] = mapped_column(String(50))

    # AI
    ai_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ai_analysis: Mapped[dict | None] = mapped_column(JSONB)

    # Tags
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))

    # Flags
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool | None] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default="now()")
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    applications: Mapped[list["Application"]] = relationship(
        "Application",
        back_populates="candidate",
        lazy="selectin",
    )
    skills: Mapped[list["CandidateSkill"]] = relationship(
        "CandidateSkill",
        back_populates="candidate",
        lazy="selectin",
    )
    experiences: Mapped[list["CandidateExperience"]] = relationship(
        "CandidateExperience",
        back_populates="candidate",
        lazy="selectin",
    )
    educations: Mapped[list["CandidateEducation"]] = relationship(
        "CandidateEducation",
        back_populates="candidate",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Candidate {self.name} ({self.email})>"

    @property
    def age(self) -> int | None:
        """Calcula idade."""
        if not self.birth_date:
            return None
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )
