"""Model JobPosition - Vagas de emprego.

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
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from .application import Application


class PositionType(StrEnum):
    """Tipo de contratacao."""

    CLT = "clt"
    PJ = "pj"
    TEMPORARIO = "temporario"
    ESTAGIO = "estagio"
    TRAINEE = "trainee"
    FREELANCER = "freelancer"
    TERCEIRIZADO = "terceirizado"


class PositionLevel(StrEnum):
    """Nivel da vaga."""

    ESTAGIARIO = "estagiario"
    JUNIOR = "junior"
    PLENO = "pleno"
    SENIOR = "senior"
    ESPECIALISTA = "especialista"
    COORDENADOR = "coordenador"
    GERENTE = "gerente"
    DIRETOR = "diretor"


class PositionStatus(StrEnum):
    """Status da vaga."""

    RASCUNHO = "rascunho"
    ABERTA = "aberta"
    PAUSADA = "pausada"
    FECHADA = "fechada"
    CANCELADA = "cancelada"
    PREENCHIDA = "preenchida"


class WorkModel(StrEnum):
    """Modelo de trabalho."""

    PRESENCIAL = "presencial"
    REMOTO = "remoto"
    HIBRIDO = "hibrido"


class Department(StrEnum):
    """Departamento."""

    OPERACIONAL = "operacional"
    ADMINISTRATIVO = "administrativo"
    FINANCEIRO = "financeiro"
    RH = "rh"
    COMERCIAL = "comercial"
    TI = "ti"
    JURIDICO = "juridico"
    MARKETING = "marketing"
    LOGISTICA = "logistica"
    SEGURANCA = "seguranca"
    FACILITIES = "facilities"
    OUTRO = "outro"


class JobPosition(Base):
    """Model para vagas de emprego — reflete schema real do banco."""

    __tablename__ = "job_positions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Tenant e condominio
    tenant_id: Mapped[str | None] = mapped_column(String(50))
    condominio_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))

    # Identificacao
    code: Mapped[str | None] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Classificacao
    position_type: Mapped[str] = mapped_column(String(30), nullable=False, default="clt")
    position_level: Mapped[str | None] = mapped_column(String(30))
    department: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="rascunho")

    # Requisitos
    requirements: Mapped[str | None] = mapped_column(Text)
    responsibilities: Mapped[str | None] = mapped_column(Text)
    benefits: Mapped[str | None] = mapped_column(Text)
    required_skills: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    desired_skills: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    min_experience_years: Mapped[int | None] = mapped_column(Integer)
    education_level: Mapped[str | None] = mapped_column(String(100))
    languages: Mapped[dict | None] = mapped_column(JSONB)

    # Remuneracao
    salary_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    salary_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    show_salary: Mapped[bool | None] = mapped_column(Boolean, default=False)
    additional_benefits: Mapped[dict | None] = mapped_column(JSONB)

    # Localizacao
    work_model: Mapped[str | None] = mapped_column(String(30))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(2))
    country: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(300))

    # Vagas
    vacancies: Mapped[int | None] = mapped_column(Integer, default=1)
    filled_count: Mapped[int | None] = mapped_column(Integer, default=0)

    # Datas
    published_at: Mapped[datetime | None] = mapped_column(DateTime)
    deadline: Mapped[date | None] = mapped_column(Date)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Processo seletivo
    selection_steps: Mapped[dict | None] = mapped_column(JSONB)

    # Responsavel
    responsible_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))

    # Integracao
    linkedin_job_id: Mapped[str | None] = mapped_column(String(100))
    indeed_job_id: Mapped[str | None] = mapped_column(String(100))
    external_url: Mapped[str | None] = mapped_column(String(500))

    # Flags
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool | None] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default="now()")
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.utcnow)
    created_by_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))

    # Relationships
    applications: Mapped[list["Application"]] = relationship(
        "Application",
        back_populates="job_position",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<JobPosition {self.code}: {self.title}>"

    @property
    def is_open(self) -> bool:
        """Verifica se vaga esta aberta."""
        return self.status == "aberta"

    @property
    def is_expired(self) -> bool:
        """Verifica se vaga expirou."""
        if not self.deadline:
            return False
        return date.today() > self.deadline

    @property
    def remaining_vacancies(self) -> int:
        """Retorna vagas restantes."""
        return max(0, (self.vacancies or 0) - (self.filled_count or 0))

    @property
    def salary_range(self) -> str:
        """Retorna faixa salarial formatada."""
        if self.salary_min and self.salary_max:
            return f"R$ {self.salary_min:,.2f} - R$ {self.salary_max:,.2f}"
        if self.salary_min:
            return f"A partir de R$ {self.salary_min:,.2f}"
        if self.salary_max:
            return f"Ate R$ {self.salary_max:,.2f}"
        return "A combinar"
