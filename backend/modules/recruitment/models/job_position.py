"""Model JobPosition - Vagas de emprego."""

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


class PositionType(str, enum.Enum):
    """Tipo de contratação."""

    CLT = "clt"
    PJ = "pj"
    TEMPORARIO = "temporario"
    ESTAGIO = "estagio"
    TRAINEE = "trainee"
    FREELANCER = "freelancer"
    TERCEIRIZADO = "terceirizado"


class PositionLevel(str, enum.Enum):
    """Nível da vaga."""

    ESTAGIARIO = "estagiario"
    JUNIOR = "junior"
    PLENO = "pleno"
    SENIOR = "senior"
    ESPECIALISTA = "especialista"
    COORDENADOR = "coordenador"
    GERENTE = "gerente"
    DIRETOR = "diretor"


class PositionStatus(str, enum.Enum):
    """Status da vaga."""

    RASCUNHO = "rascunho"
    ABERTA = "aberta"
    PAUSADA = "pausada"
    FECHADA = "fechada"
    CANCELADA = "cancelada"
    PREENCHIDA = "preenchida"


class WorkModel(str, enum.Enum):
    """Modelo de trabalho."""

    PRESENCIAL = "presencial"
    REMOTO = "remoto"
    HIBRIDO = "hibrido"


class Department(str, enum.Enum):
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
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Classificação
    position_type: Mapped[PositionType] = mapped_column(
        Enum(PositionType), default=PositionType.CLT
    )
    position_level: Mapped[PositionLevel] = mapped_column(
        Enum(PositionLevel), default=PositionLevel.PLENO
    )
    department: Mapped[Department] = mapped_column(
        Enum(Department), default=Department.OPERACIONAL
    )
    status: Mapped[PositionStatus] = mapped_column(
        Enum(PositionStatus), default=PositionStatus.RASCUNHO
    )

    # Requisitos
    requirements: Mapped[Optional[str]] = mapped_column(Text)
    responsibilities: Mapped[Optional[str]] = mapped_column(Text)
    required_skills: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), default=list
    )
    desired_skills: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), default=list
    )
    min_experience_years: Mapped[int] = mapped_column(Integer, default=0)
    education_level: Mapped[Optional[str]] = mapped_column(String(100))

    # Remuneração
    salary_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    salary_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    salary_display: Mapped[bool] = mapped_column(Boolean, default=False)
    benefits: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), default=list)

    # Localização
    work_model: Mapped[WorkModel] = mapped_column(
        Enum(WorkModel), default=WorkModel.PRESENCIAL
    )
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(2))
    address: Mapped[Optional[str]] = mapped_column(String(300))

    # Vagas
    vacancies: Mapped[int] = mapped_column(Integer, default=1)
    filled_vacancies: Mapped[int] = mapped_column(Integer, default=0)
    is_urgent: Mapped[bool] = mapped_column(Boolean, default=False)
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=False)

    # Datas
    opening_date: Mapped[Optional[date]] = mapped_column(Date)
    deadline_date: Mapped[Optional[date]] = mapped_column(Date)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Processo seletivo
    selection_stages: Mapped[Optional[List[dict]]] = mapped_column(JSON, default=list)
    expected_start_date: Mapped[Optional[date]] = mapped_column(Date)

    # Contadores
    applications_count: Mapped[int] = mapped_column(Integer, default=0)
    views_count: Mapped[int] = mapped_column(Integer, default=0)

    # Responsável
    recruiter_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))
    hiring_manager_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))

    # Relacionamentos
    condominium_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))
    created_by: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))

    # Relationships
    applications: Mapped[List["Application"]] = relationship(
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
        self, reason: str = None  # pylint: disable=unused-argument
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
