"""Workflow Model - Definicao de Workflows.

Sprint 33 - Workflow Engine (Unificado).
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class WorkflowStatus(StrEnum):
    """Status do workflow."""

    DRAFT = "DRAFT"  # Rascunho
    ACTIVE = "ACTIVE"  # Ativo
    INACTIVE = "INACTIVE"  # Inativo
    PAUSED = "PAUSED"  # Pausado
    ARCHIVED = "ARCHIVED"  # Arquivado
    ERROR = "ERROR"  # Em erro


class WorkflowPriority(StrEnum):
    """Prioridade de execucao."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class WorkflowCategory(StrEnum):
    """Categoria do workflow."""

    CRM = "CRM"  # Workflows de CRM
    HR = "HR"  # Recursos Humanos
    FINANCE = "FINANCE"  # Financeiro
    OPERATIONS = "OPERATIONS"  # Operacoes
    ONBOARDING = "ONBOARDING"  # Onboarding
    MARKETING = "MARKETING"  # Marketing
    SUPPORT = "SUPPORT"  # Suporte
    COMMUNICATION = "COMMUNICATION"  # Comunicacao
    DOCUMENT = "DOCUMENT"  # Documentos
    INTEGRATION = "INTEGRATION"  # Integracao
    MAINTENANCE = "MAINTENANCE"  # Manutencao
    SECURITY = "SECURITY"  # Seguranca
    ANALYTICS = "ANALYTICS"  # Analytics
    CUSTOM = "CUSTOM"  # Customizado


class Workflow(Base):
    """Definicao de workflow automatizado."""

    __tablename__ = "workflows"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)

    # Categoria, Status e Prioridade
    category = Column(
        Enum(WorkflowCategory, name="workflowcategory", create_type=True),
        nullable=False,
        default=WorkflowCategory.CUSTOM,
    )
    status = Column(
        Enum(WorkflowStatus, name="workflowstatus", create_type=True),
        nullable=False,
        default=WorkflowStatus.DRAFT,
    )
    priority = Column(
        Enum(WorkflowPriority, name="workflowpriority", create_type=True),
        nullable=False,
        default=WorkflowPriority.NORMAL,
    )

    # Configuracao
    # Ex: {"max_executions": 100, "timeout_minutes": 60}
    config = Column(JSONB, nullable=True)

    # Variaveis de contexto disponiveis (nomes)
    # Ex: ["lead", "opportunity", "user", "contract"]
    context_variables = Column(ARRAY(String), nullable=True)

    # Variaveis detalhadas com tipo, default, required
    # Ex: [{"name": "amount", "type": "number", "default": 0, "required": true}]
    variables = Column(JSONB, nullable=True)

    # Schemas de input/output
    input_schema = Column(JSONB, nullable=True)
    output_schema = Column(JSONB, nullable=True)

    # Tags
    tags = Column(ARRAY(String), nullable=True)

    # Execucao
    run_once = Column(Boolean, default=False, nullable=False)
    max_executions = Column(Integer, nullable=True)
    timeout_seconds = Column(Integer, default=3600, nullable=False)
    retry_count = Column(Integer, default=3, nullable=False)
    retry_delay_seconds = Column(Integer, default=60, nullable=False)

    # Visual Designer
    # Ex: {"nodes": [...], "edges": [...], "viewport": {...}}
    canvas_data = Column(JSONB, nullable=True)

    # Versionamento
    # Ex: [{"version": 1, "created_at": "...", "changes": "..."}]
    versions_history = Column(JSONB, nullable=True)

    # Parent workflow (para clones)
    parent_workflow_id = Column(UUID(as_uuid=True), nullable=True)

    # Metricas
    total_executions = Column(Integer, default=0, nullable=False)
    successful_executions = Column(Integer, default=0, nullable=False)
    failed_executions = Column(Integer, default=0, nullable=False)
    avg_execution_time_ms = Column(Integer, default=0, nullable=True)

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    last_executed_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_failure_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Metadados extras
    extra_metadata = Column("metadata", JSONB, nullable=True)

    # Relationships
    steps = relationship(
        "WorkflowStep",
        back_populates="workflow",
        lazy="selectin",
        order_by="WorkflowStep.order",
        foreign_keys="[WorkflowStep.workflow_id]",
    )
    triggers = relationship(
        "WorkflowTrigger",
        back_populates="workflow",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<Workflow {self.name} ({self.status.value})>"

    @property
    def is_active(self) -> bool:
        """Verifica se esta ativo."""
        return self.status == WorkflowStatus.ACTIVE and self.active

    @property
    def success_rate(self) -> float:
        """Calcula taxa de sucesso."""
        if not self.total_executions:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100

    @property
    def failure_rate(self) -> float:
        """Calcula taxa de falha."""
        if not self.total_executions:
            return 0.0
        return (self.failed_executions / self.total_executions) * 100

    @property
    def step_count(self) -> int:
        """Retorna quantidade de steps."""
        return len(self.steps) if self.steps else 0

    @property
    def trigger_count(self) -> int:
        """Retorna quantidade de triggers."""
        return len(self.triggers) if self.triggers else 0

    def activate(self) -> None:
        """Ativa o workflow."""
        self.status = WorkflowStatus.ACTIVE
        self.active = True
        self.published_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Desativa o workflow."""
        self.status = WorkflowStatus.INACTIVE
        self.active = False

    def archive(self) -> None:
        """Arquiva o workflow."""
        self.status = WorkflowStatus.ARCHIVED
        self.active = False

    def increment_version(self) -> None:
        """Incrementa versao."""
        self.version = (self.version or 0) + 1

    @property
    def can_execute(self) -> bool:
        """Verifica se pode executar."""
        if not self.is_active:
            return False
        if self.run_once and self.total_executions and self.total_executions > 0:
            return False
        if self.max_executions and self.total_executions and self.total_executions >= self.max_executions:
            return False
        return True

    def record_execution(
        self,
        success: bool,
        execution_time_ms: int | None = None,
    ) -> None:
        """Registra execucao.

        Args:
            success: Se foi sucesso.
            execution_time_ms: Tempo de execucao em ms.
        """
        self.total_executions = (self.total_executions or 0) + 1
        self.last_executed_at = datetime.utcnow()

        if success:
            self.successful_executions = (self.successful_executions or 0) + 1
            self.last_success_at = datetime.utcnow()
        else:
            self.failed_executions = (self.failed_executions or 0) + 1
            self.last_failure_at = datetime.utcnow()

        # Atualiza media de tempo (media movel)
        if execution_time_ms is not None:
            current_avg = self.avg_execution_time_ms or 0
            if current_avg == 0:
                self.avg_execution_time_ms = execution_time_ms
            else:
                self.avg_execution_time_ms = int(current_avg * 0.9 + execution_time_ms * 0.1)

    def pause(self) -> None:
        """Pausa o workflow."""
        self.status = WorkflowStatus.PAUSED

    def resume(self) -> None:
        """Resume o workflow."""
        if self.status == WorkflowStatus.PAUSED:
            self.status = WorkflowStatus.ACTIVE

    def add_variable(self, name: str, var_type: str = "string", default: any = None, required: bool = False) -> None:
        """Adiciona variavel ao workflow.

        Args:
            name: Nome da variavel.
            var_type: Tipo (string, number, boolean, date, array, object).
            default: Valor padrao.
            required: Se e obrigatoria.
        """
        if self.variables is None:
            self.variables = []

        # Verifica se ja existe
        for var in self.variables:
            if var.get("name") == name:
                return

        self.variables.append(
            {
                "name": name,
                "type": var_type,
                "default": default,
                "required": required,
            }
        )

    def get_variable(self, name: str) -> dict | None:
        """Obtem variavel por nome.

        Args:
            name: Nome da variavel.

        Returns:
            Variavel ou None.
        """
        if not self.variables:
            return None
        for var in self.variables:
            if var.get("name") == name:
                return var
        return None

    def add_tag(self, tag: str) -> None:
        """Adiciona tag.

        Args:
            tag: Tag a adicionar.
        """
        tag = tag.lower().strip()
        if not tag:
            return
        if self.tags is None:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove tag.

        Args:
            tag: Tag a remover.
        """
        tag = tag.lower().strip()
        if self.tags and tag in self.tags:
            self.tags.remove(tag)

    def create_version_snapshot(self, user_id: str, changes: str = "") -> dict:
        """Cria snapshot da versao atual.

        Args:
            user_id: ID do usuario.
            changes: Descricao das mudancas.

        Returns:
            Dados do snapshot.
        """
        if self.versions_history is None:
            self.versions_history = []

        snapshot = {
            "version": self.version,
            "created_at": datetime.utcnow().isoformat(),
            "created_by": user_id,
            "changes": changes,
        }

        self.versions_history.append(snapshot)
        self.increment_version()
        self.updated_by = user_id

        return snapshot

    def clone(self, new_name: str, tenant_id: str | None = None) -> "Workflow":
        """Clona o workflow.

        Args:
            new_name: Nome do novo workflow.
            tenant_id: ID do tenant (opcional, usa o atual).

        Returns:
            Novo workflow clonado.
        """
        return Workflow(
            tenant_id=tenant_id or self.tenant_id,
            name=new_name,
            slug=f"{self.slug}-copy",
            description=f"Copia de: {self.name}",
            category=self.category,
            status=WorkflowStatus.DRAFT,
            priority=self.priority,
            config=self.config.copy() if self.config else None,
            context_variables=self.context_variables.copy() if self.context_variables else None,
            variables=self.variables.copy() if self.variables else None,
            input_schema=self.input_schema.copy() if self.input_schema else None,
            output_schema=self.output_schema.copy() if self.output_schema else None,
            tags=self.tags.copy() if self.tags else None,
            timeout_seconds=self.timeout_seconds,
            retry_count=self.retry_count,
            retry_delay_seconds=self.retry_delay_seconds,
            canvas_data=self.canvas_data.copy() if self.canvas_data else None,
            parent_workflow_id=self.id,
            is_template=False,
            extra_metadata=self.extra_metadata.copy() if self.extra_metadata else None,
            created_by=self.created_by,
        )
