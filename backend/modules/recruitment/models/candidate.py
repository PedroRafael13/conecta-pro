"""Model Candidate - Candidatos."""

import enum
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import (
    String,
    Text,
    Boolean,
    DateTime,
    Date,
    Integer,
    Numeric,
    Enum,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.database import Base
from core.models import TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from .application import Application
    from .candidate_skill import CandidateSkill
    from .candidate_experience import CandidateExperience
    from .candidate_education import CandidateEducation


class CandidateStatus(str, enum.Enum):
    """Status do candidato."""

    ATIVO = "ativo"
    INATIVO = "inativo"
    CONTRATADO = "contratado"
    BLOQUEADO = "bloqueado"
    ARQUIVADO = "arquivado"


class CandidateSource(str, enum.Enum):
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


class Gender(str, enum.Enum):
    """Gênero."""

    MASCULINO = "masculino"
    FEMININO = "feminino"
    NAO_BINARIO = "nao_binario"
    PREFIRO_NAO_DIZER = "prefiro_nao_dizer"


class MaritalStatus(str, enum.Enum):
    """Estado civil."""

    SOLTEIRO = "solteiro"
    CASADO = "casado"
    DIVORCIADO = "divorciado"
    VIUVO = "viuvo"
    UNIAO_ESTAVEL = "uniao_estavel"


class Candidate(Base, TimestampMixin, SoftDeleteMixin):
    """Model para candidatos."""

    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Dados pessoais
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    whatsapp: Mapped[Optional[str]] = mapped_column(String(20))
    cpf: Mapped[Optional[str]] = mapped_column(String(14), unique=True)
    rg: Mapped[Optional[str]] = mapped_column(String(20))
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[Gender]] = mapped_column(Enum(Gender))
    marital_status: Mapped[Optional[MaritalStatus]] = mapped_column(Enum(MaritalStatus))

    # Endereço
    address: Mapped[Optional[str]] = mapped_column(String(300))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(2))
    zip_code: Mapped[Optional[str]] = mapped_column(String(10))
    neighborhood: Mapped[Optional[str]] = mapped_column(String(100))

    # Profissional
    headline: Mapped[Optional[str]] = mapped_column(String(200))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(300))
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(300))
    github_url: Mapped[Optional[str]] = mapped_column(String(300))

    # Currículo
    resume_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    resume_text: Mapped[Optional[str]] = mapped_column(Text)
    resume_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Pretensão
    salary_expectation: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    salary_expectation_pj: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))

    # Disponibilidade
    available_immediately: Mapped[bool] = mapped_column(Boolean, default=True)
    notice_period_days: Mapped[int] = mapped_column(Integer, default=0)
    available_date: Mapped[Optional[date]] = mapped_column(Date)
    available_for_travel: Mapped[bool] = mapped_column(Boolean, default=False)
    available_for_relocation: Mapped[bool] = mapped_column(Boolean, default=False)
    preferred_work_model: Mapped[Optional[str]] = mapped_column(String(50))

    # CNH
    has_cnh: Mapped[bool] = mapped_column(Boolean, default=False)
    cnh_category: Mapped[Optional[str]] = mapped_column(String(5))
    has_vehicle: Mapped[bool] = mapped_column(Boolean, default=False)

    # Idiomas
    languages: Mapped[Optional[List[dict]]] = mapped_column(JSON, default=list)

    # Status e origem
    status: Mapped[CandidateStatus] = mapped_column(
        Enum(CandidateStatus), default=CandidateStatus.ATIVO
    )
    source: Mapped[CandidateSource] = mapped_column(
        Enum(CandidateSource), default=CandidateSource.SITE
    )
    source_detail: Mapped[Optional[str]] = mapped_column(String(200))

    # Bloqueio
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    block_reason: Mapped[Optional[str]] = mapped_column(Text)
    blocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    blocked_by: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))

    # Scores e métricas
    profile_score: Mapped[int] = mapped_column(Integer, default=0)
    applications_count: Mapped[int] = mapped_column(Integer, default=0)
    interviews_count: Mapped[int] = mapped_column(Integer, default=0)
    hired_count: Mapped[int] = mapped_column(Integer, default=0)

    # Tags e notas
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Última atividade
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_application_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # PCD
    is_pcd: Mapped[bool] = mapped_column(Boolean, default=False)
    pcd_type: Mapped[Optional[str]] = mapped_column(String(100))
    pcd_cid: Mapped[Optional[str]] = mapped_column(String(20))
    needs_accommodation: Mapped[bool] = mapped_column(Boolean, default=False)
    accommodation_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relacionamentos
    condominium_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))
    created_by: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))

    # Relationships
    applications: Mapped[List["Application"]] = relationship(
        "Application", back_populates="candidate", lazy="dynamic"
    )
    skills: Mapped[List["CandidateSkill"]] = relationship(
        "CandidateSkill", back_populates="candidate", lazy="dynamic"
    )
    experiences: Mapped[List["CandidateExperience"]] = relationship(
        "CandidateExperience", back_populates="candidate", lazy="dynamic"
    )
    educations: Mapped[List["CandidateEducation"]] = relationship(
        "CandidateEducation", back_populates="candidate", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<Candidate {self.name} ({self.email})>"

    @property
    def age(self) -> Optional[int]:
        """Calcula idade."""
        if not self.birth_date:
            return None
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @property
    def is_available(self) -> bool:
        """Verifica se está disponível."""
        if self.available_immediately:
            return True
        if self.available_date and self.available_date <= date.today():
            return True
        return False

    @property
    def full_address(self) -> str:
        """Retorna endereço completo."""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.neighborhood:
            parts.append(self.neighborhood)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.zip_code:
            parts.append(f"CEP: {self.zip_code}")
        return ", ".join(parts) if parts else ""

    @property
    def profile_completeness(self) -> int:  # pylint: disable=too-many-branches
        """Calcula completude do perfil (0-100)."""
        score = 0
        total = 0

        # Dados obrigatórios (40 pontos)
        total += 10
        if self.name:
            score += 10
        total += 10
        if self.email:
            score += 10
        total += 10
        if self.phone:
            score += 10
        total += 10
        if self.resume_file_path or self.resume_text:
            score += 10

        # Dados importantes (35 pontos)
        total += 7
        if self.headline:
            score += 7
        total += 7
        if self.summary:
            score += 7
        total += 7
        if self.city and self.state:
            score += 7
        total += 7
        if self.salary_expectation:
            score += 7
        total += 7
        if self.birth_date:
            score += 7

        # Dados complementares (25 pontos)
        total += 5
        if self.linkedin_url:
            score += 5
        total += 5
        if self.photo_url:
            score += 5
        total += 5
        if self.cpf:
            score += 5
        total += 5
        if self.languages:
            score += 5
        total += 5
        if self.has_cnh:
            score += 5

        return int((score / total) * 100) if total > 0 else 0

    def block(self, reason: str, blocked_by: str) -> None:
        """Bloqueia candidato."""
        self.is_blocked = True
        self.block_reason = reason
        self.blocked_at = datetime.utcnow()
        self.blocked_by = blocked_by
        self.status = CandidateStatus.BLOQUEADO

    def unblock(self) -> None:
        """Desbloqueia candidato."""
        self.is_blocked = False
        self.block_reason = None
        self.blocked_at = None
        self.blocked_by = None
        self.status = CandidateStatus.ATIVO

    def archive(self) -> None:
        """Arquiva candidato."""
        self.status = CandidateStatus.ARQUIVADO

    def activate(self) -> None:
        """Ativa candidato."""
        self.status = CandidateStatus.ATIVO

    def mark_as_hired(self) -> None:
        """Marca como contratado."""
        self.status = CandidateStatus.CONTRATADO
        self.hired_count += 1

    def record_activity(self) -> None:
        """Registra atividade."""
        self.last_activity_at = datetime.utcnow()

    def record_application(self) -> None:
        """Registra candidatura."""
        self.applications_count += 1
        self.last_application_at = datetime.utcnow()
        self.record_activity()

    def record_interview(self) -> None:
        """Registra entrevista."""
        self.interviews_count += 1
        self.record_activity()

    def update_profile_score(self) -> None:
        """Atualiza score do perfil."""
        self.profile_score = self.profile_completeness

    def add_tag(self, tag: str) -> None:
        """Adiciona tag."""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove tag."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
