"""
Models para Treinamento e Desenvolvimento.

Implementa tabelas de cursos, treinamentos, matriculas e certificados
para gestao completa do ciclo de capacitacao dos funcionarios.

Tabelas:
    - training_courses: Catalogo de cursos disponiveis
    - trainings: Instancias/turmas de treinamento
    - training_enrollments: Matriculas de funcionarios
    - training_certificates: Certificados emitidos
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base, TimestampMixin


class TrainingCategoryCourse(StrEnum):
    """Categorias de cursos de treinamento."""

    MANDATORY_SECURITY = "mandatory_security"
    MANDATORY_SAFETY = "mandatory_safety"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    LEADERSHIP = "leadership"
    COMPLIANCE = "compliance"
    ONBOARDING = "onboarding"
    OTHER = "other"


class TrainingStatus(StrEnum):
    """Status de um treinamento/turma."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EnrollmentStatus(StrEnum):
    """Status de matricula em treinamento."""

    ENROLLED = "enrolled"
    CONFIRMED = "confirmed"
    ATTENDED = "attended"
    ABSENT = "absent"
    CANCELLED = "cancelled"


class CertificateStatus(StrEnum):
    """Status de certificado de treinamento."""

    VALID = "valid"
    EXPIRED = "expired"
    REVOKED = "revoked"


class TrainingCourse(Base, TimestampMixin):
    """Catalogo de cursos de treinamento."""

    __tablename__ = "training_courses"
    __table_args__ = (
        Index("idx_training_course_category", "category"),
        Index("idx_training_course_active", "is_active"),
        Index("idx_training_course_mandatory", "is_mandatory"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    category: Mapped[TrainingCategoryCourse] = mapped_column(
        Enum(TrainingCategoryCourse, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=TrainingCategoryCourse.OTHER,
    )
    duration_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        comment="Duracao do curso em horas",
    )
    max_participants: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Maximo de participantes por turma",
    )
    is_mandatory: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    required_for_workplace_types: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Tipos de posto que exigem este curso",
    )
    validity_months: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Meses de validade do certificado (null = sem validade)",
    )
    syllabus: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Ementa do curso em formato estruturado",
    )
    instructor_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    instructor_qualification: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    cost_per_participant: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Custo por participante em BRL",
    )
    provider: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Fornecedor ou empresa de treinamento",
    )

    # Relationships
    trainings: Mapped[list["Training"]] = relationship(
        "Training",
        back_populates="course",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<TrainingCourse(id={self.id}, name={self.name}, category={self.category.value})>"


class Training(Base, TimestampMixin):
    """Instancia/turma de um treinamento."""

    __tablename__ = "trainings"
    __table_args__ = (
        Index("idx_training_course_id", "course_id"),
        Index("idx_training_status", "status"),
        Index("idx_training_start_date", "start_date"),
        Index("idx_training_workplace", "workplace_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("training_courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    location: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )
    status: Mapped[TrainingStatus] = mapped_column(
        Enum(TrainingStatus, name="rh_trainingstatus", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=TrainingStatus.SCHEDULED,
    )
    instructor_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    max_participants: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    current_participants: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    workplace_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Relationships
    course: Mapped["TrainingCourse"] = relationship(
        "TrainingCourse",
        back_populates="trainings",
    )
    enrollments: Mapped[list["TrainingEnrollment"]] = relationship(
        "TrainingEnrollment",
        back_populates="training",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Training(id={self.id}, title={self.title}, status={self.status.value})>"

    @property
    def has_available_slots(self) -> bool:
        """Verifica se ha vagas disponiveis."""
        if self.max_participants is None:
            return True
        return self.current_participants < self.max_participants

    @property
    def is_active(self) -> bool:
        """Verifica se o treinamento esta ativo (nao cancelado/concluido)."""
        return self.status in (TrainingStatus.SCHEDULED, TrainingStatus.IN_PROGRESS)


class TrainingEnrollment(Base, TimestampMixin):
    """Matricula de funcionario em treinamento."""

    __tablename__ = "training_enrollments"
    __table_args__ = (
        UniqueConstraint("training_id", "employee_id", name="uq_enrollment_training_employee"),
        Index("idx_enrollment_training", "training_id"),
        Index("idx_enrollment_employee", "employee_id"),
        Index("idx_enrollment_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    training_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trainings.id", ondelete="CASCADE"),
        nullable=False,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        Enum(EnrollmentStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=EnrollmentStatus.ENROLLED,
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    attended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Nota obtida no treinamento (0-100)",
    )
    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    certificate_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Relationships
    training: Mapped["Training"] = relationship(
        "Training",
        back_populates="enrollments",
    )
    certificate: Mapped["TrainingCertificate | None"] = relationship(
        "TrainingCertificate",
        back_populates="enrollment",
        uselist=False,
        foreign_keys="TrainingCertificate.enrollment_id",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<TrainingEnrollment(id={self.id}, employee={self.employee_id}, status={self.status.value})>"


class TrainingCertificate(Base):
    """Certificado de treinamento emitido para funcionario."""

    __tablename__ = "training_certificates"
    __table_args__ = (
        UniqueConstraint("certificate_number", name="uq_certificate_number"),
        Index("idx_certificate_employee", "employee_id"),
        Index("idx_certificate_course", "course_id"),
        Index("idx_certificate_status", "status"),
        Index("idx_certificate_expires", "expires_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("training_enrollments.id", ondelete="CASCADE"),
        nullable=False,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("training_courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    certificate_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[CertificateStatus] = mapped_column(
        Enum(
            CertificateStatus,
            name="certificatestatus",
            create_type=False,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
        default=CertificateStatus.VALID,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    revocation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    document_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    enrollment: Mapped["TrainingEnrollment"] = relationship(
        "TrainingEnrollment",
        back_populates="certificate",
        foreign_keys=[enrollment_id],
    )

    def __repr__(self) -> str:
        return f"<TrainingCertificate(id={self.id}, number={self.certificate_number}, status={self.status.value})>"

    @property
    def is_valid(self) -> bool:
        """Verifica se o certificado esta valido."""
        if self.status != CertificateStatus.VALID:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
