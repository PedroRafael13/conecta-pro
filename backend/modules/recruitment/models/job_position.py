"""Model JobPosition - Vagas de emprego."""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from core.models import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from .application import Application


class PositionType(StrEnum):
    """Tipo de contratação."""

    CLT = "clt"
    PJ = "pj"
    TEMPORARIO = "temporario"
    ESTAGIO = "estagio"
    TRAINEE = "trainee"
    FREELANCER = "freelancer"
    TERCEIRIZADO = "terceirizado"


class PositionLevel(StrEnum):
    """Nível da vaga."""

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


class JobPosition(Base, TimestampMixin, SoftDeleteMixin):
    """Model para vagas de emprego."""

    __tablename__ = "job_positions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Identificação
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Classificação
    position_type: Mapped[PositionType] = mapped_column(Enum(PositionType), default=PositionType.CLT)
    position_level: Mapped[PositionLevel] = mapped_column(Enum(PositionLevel), default=PositionLevel.PLENO)
    department: Mapped[Department] = mapped_column(Enum(Department), default=Department.OPERACIONAL)
    status: Mapped[PositionStatus] = mapped_column(Enum(PositionStatus), default=PositionStatus.RASCUNHO)

    # Requisitos
    requirements: Mapped[str | None] = mapped_column(Text)
    responsibilities: Mapped[str | None] = mapped_column(Text)
    required_skills: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)
    desired_skills: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)
    min_experience_years: Mapped[int] = mapped_column(Integer, default=0)
    education_level: Mapped[str | None] = mapped_column(String(100))

    # Remuneração
    salary_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    salary_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    salary_display: Mapped[bool] = mapped_column(Boolean, default=False)
    benefits: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)

    # Localização
    work_model: Mapped[WorkModel] = mapped_column(Enum(WorkModel), default=WorkModel.PRESENCIAL)
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(2))
    address: Mapped[str | None] = mapped_column(String(300))

    # Vagas
    vacancies: Mapped[int] = mapped_column(Integer, default=1)
    filled_vacancies: Mapped[int] = mapped_column(Integer, default=0)
    is_urgent: Mapped[bool] = mapped_column(Boolean, default=False)
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=False)

    # Datas
    opening_date: Mapped[date | None] = mapped_column(Date)
    deadline_date: Mapped[date | None] = mapped_column(Date)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Processo seletivo
    selection_stages: Mapped[list[dict] | None] = mapped_column(JSON, default=list)
    expected_start_date: Mapped[date | None] = mapped_column(Date)

    # Contadores
    applications_count: Mapped[int] = mapped_column(Integer, default=0)
    views_count: Mapped[int] = mapped_column(Integer, default=0)

    # Responsável
    recruiter_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    hiring_manager_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))

    # Relacionamentos
    condominium_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    created_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False))

    # Relationships
    applications: Mapped[list["Application"]] = relationship(
        "Application", back_populates="job_position", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<JobPosition {self.code}: {self.title}>"

    @property
    def is_open(self) -> bool:
        """Verifica se vaga está aberta."""
        return self.status == PositionStatus.ABERTA

    @property
    def is_expired(self) -> bool:
        """Verifica se vaga expirou."""
        if not self.deadline_date:
            return False
        return date.today() > self.deadline_date

    @property
    def remaining_vacancies(self) -> int:
        """Retorna vagas restantes."""
        return max(0, self.vacancies - self.filled_vacancies)

    @property
    def is_fully_filled(self) -> bool:
        """Verifica se todas as vagas foram preenchidas."""
        return self.filled_vacancies >= self.vacancies

    @property
    def salary_range(self) -> str:
        """Retorna faixa salarial formatada."""
        if self.salary_min and self.salary_max:
            return f"R$ {self.salary_min:,.2f} - R$ {self.salary_max:,.2f}"
        if self.salary_min:
            return f"A partir de R$ {self.salary_min:,.2f}"
        if self.salary_max:
            return f"Até R$ {self.salary_max:,.2f}"
        return "A combinar"

    def open(self) -> None:
        """Abre a vaga."""
        self.status = PositionStatus.ABERTA
        self.opening_date = date.today()

    def pause(self) -> None:
        """Pausa a vaga."""
        self.status = PositionStatus.PAUSADA

    def close(
        self,
        reason: str = None,  # pylint: disable=unused-argument
    ) -> None:
        """Fecha a vaga."""
        self.status = PositionStatus.FECHADA
        self.closed_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancela a vaga."""
        self.status = PositionStatus.CANCELADA
        self.closed_at = datetime.utcnow()

    def mark_as_filled(self) -> None:
        """Marca como preenchida."""
        self.status = PositionStatus.PREENCHIDA
        self.closed_at = datetime.utcnow()

    def fill_vacancy(self) -> None:
        """Preenche uma vaga."""
        self.filled_vacancies += 1
        if self.is_fully_filled:
            self.mark_as_filled()

    def increment_view(self) -> None:
        """Incrementa visualização."""
        self.views_count += 1

    def increment_application(self) -> None:
        """Incrementa candidaturas."""
        self.applications_count += 1

    @staticmethod
    def generate_code(sequence: int) -> str:
        """Gera código da vaga."""
        year = date.today().year
        return f"VAG-{year}-{sequence:05d}"
