"""
Models do Sistema Anti-Procrastinação
=====================================

Define estruturas de dados unificadas para controle de pendências
cross-module no Conecta PRO.

Autor: Conecta PRO Team + Claude AI
Data: 2026-01-10
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum, StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TaskPriority(StrEnum):
    """Prioridade da tarefa pendente."""

    CRITICAL = "critical"  # >7 dias ou compliance
    HIGH = "high"  # 3-7 dias
    MEDIUM = "medium"  # 1-3 dias
    LOW = "low"  # <1 dia
    INFO = "info"  # Informativo


class TaskCategory(StrEnum):
    """Categoria da tarefa por área de impacto."""

    COMPLIANCE = "compliance"  # Compliance/Legal
    FINANCIAL = "financial"  # Financeiro
    OPERATIONAL = "operational"  # Operacional
    HR = "hr"  # Recursos Humanos
    COMMERCIAL = "commercial"  # Comercial
    SECURITY = "security"  # Segurança
    HEALTH_SAFETY = "health_safety"  # Saúde e Segurança


class TaskStatus(StrEnum):
    """Status atual da tarefa."""

    PENDING = "pending"  # Pendente
    IN_PROGRESS = "in_progress"  # Em andamento
    ESCALATED = "escalated"  # Escalada
    BLOCKED = "blocked"  # Bloqueada
    COMPLETED = "completed"  # Concluída
    CANCELLED = "cancelled"  # Cancelada
    OVERDUE = "overdue"  # Atrasada


class EscalationLevel(int, Enum):
    """Níveis de escalation."""

    LEVEL_0 = 0  # Normal
    LEVEL_1 = 1  # Supervisor
    LEVEL_2 = 2  # Manager
    LEVEL_3 = 3  # Diretor
    LEVEL_4 = 4  # CEO/Bloqueio


class Department(StrEnum):
    """Departamentos do sistema."""

    HR = "hr"  # Recursos Humanos
    COMMERCIAL = "commercial"  # Comercial
    FINANCIAL = "financial"  # Financeiro
    FACILITIES = "facilities"  # Facilities
    IT = "it"  # TI
    LEGAL = "legal"  # Jurídico
    OPERATIONS = "operations"  # Operações
    MANAGEMENT = "management"  # Gestão


@dataclass
class PendingTaskData:
    """Estrutura de dados para tarefa pendente."""

    # Identificação
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""

    # Origem
    source_module: str = ""  # Módulo de origem
    source_id: str = ""  # ID na origem

    # Classificação
    category: TaskCategory = TaskCategory.OPERATIONAL
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING

    # Responsabilidade
    department: Department = Department.OPERATIONS
    assigned_to: UUID | None = None
    assigned_to_name: str = ""

    # Datas
    created_at: datetime = field(default_factory=datetime.utcnow)
    due_date: date | None = None
    completed_at: datetime | None = None

    # Escalation
    escalation_level: EscalationLevel = EscalationLevel.LEVEL_0
    escalation_count: int = 0
    last_escalation: datetime | None = None

    # Metadados
    task_metadata: dict[str, Any] = field(default_factory=dict)
    business_impact: str = "medium"  # low, medium, high, critical
    compliance_risk: str = "low"  # low, medium, high, critical

    @property
    def days_pending(self) -> int:
        """Quantidade de dias pendente."""
        return (datetime.utcnow() - self.created_at).days

    @property
    def is_overdue(self) -> bool:
        """Verifica se está atrasada."""
        if self.due_date:
            return date.today() > self.due_date
        return False

    @property
    def urgency_score(self) -> float:
        """Score de urgência (0-100)."""
        score = 0.0

        # Dias pendente (0-40 pontos)
        days = self.days_pending
        if days >= 10:
            score += 40
        else:
            score += days * 4

        # Prioridade (0-25 pontos)
        priority_scores = {
            TaskPriority.CRITICAL: 25,
            TaskPriority.HIGH: 20,
            TaskPriority.MEDIUM: 10,
            TaskPriority.LOW: 5,
            TaskPriority.INFO: 0,
        }
        score += priority_scores[self.priority]

        # Risco de compliance (0-25 pontos)
        risk_scores = {"critical": 25, "high": 20, "medium": 10, "low": 5}
        score += risk_scores.get(self.compliance_risk, 5)

        # Impacto no negócio (0-10 pontos)
        score += risk_scores.get(self.business_impact, 5) / 2

        return min(score, 100.0)


class PendingTask(Base):
    """Modelo de tarefa pendente no banco."""

    __tablename__ = "anti_procrastination_tasks"

    # Identificação
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Dados básicos
    title = Column(String(500), nullable=False)
    description = Column(Text)

    # Origem
    source_module = Column(String(100), nullable=False, index=True)
    source_id = Column(String(100), nullable=False)

    # Classificação
    category = Column(SQLEnum(TaskCategory, create_type=True), nullable=False, index=True)
    priority = Column(SQLEnum(TaskPriority, create_type=True), nullable=False, index=True)
    status = Column(SQLEnum(TaskStatus, create_type=True), nullable=False, default=TaskStatus.PENDING, index=True)

    # Responsabilidade
    department = Column(SQLEnum(Department, create_type=True), nullable=False, index=True)
    assigned_to = Column(PGUUID(as_uuid=True), index=True)
    assigned_to_name = Column(String(200))

    # Datas
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    due_date = Column(DateTime, index=True)
    completed_at = Column(DateTime)

    # Escalation
    escalation_level = Column(SQLEnum(EscalationLevel, create_type=True), default=EscalationLevel.LEVEL_0, index=True)
    escalation_count = Column(Integer, default=0)
    last_escalation = Column(DateTime)

    # Metadados
    task_metadata = Column(JSONB)
    business_impact = Column(String(20), default="medium")
    compliance_risk = Column(String(20), default="low")

    # Índices compostos para performance
    __table_args__ = {"comment": "Tarefas pendentes do sistema anti-procrastinação"}


class DepartmentSummary(BaseModel):
    """Resumo de pendências por departamento."""

    department: Department
    total_tasks: int
    critical_tasks: int
    high_priority_tasks: int
    overdue_tasks: int
    avg_urgency_score: float
    oldest_task_days: int


class SystemSummary(BaseModel):
    """Resumo geral do sistema."""

    total_pending: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    overdue_count: int
    departments: list[DepartmentSummary]
    avg_resolution_time: float
    top_bottlenecks: list[dict[str, Any]]


class TaskFilter(BaseModel):
    """Filtros para busca de tarefas."""

    department: Department | None = None
    category: TaskCategory | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    assigned_to: UUID | None = None

    days_pending_min: int | None = None
    days_pending_max: int | None = None

    escalation_level: EscalationLevel | None = None

    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class TaskActionRequest(BaseModel):
    """Request para ações em tarefas."""

    task_id: UUID
    action: str  # complete, escalate, reassign, block, etc
    comment: str | None = None
    metadata: dict[str, Any] | None = None


class EscalationRule(BaseModel):
    """Regra de escalation por categoria."""

    category: TaskCategory
    level_1_days: int = 1
    level_2_days: int = 3
    level_3_days: int = 7
    level_4_days: int = 10

    enabled: bool = True
    custom_rules: dict[str, Any] | None = None
