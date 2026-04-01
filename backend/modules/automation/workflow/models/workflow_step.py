"""Workflow Step Model - Passos do Workflow.

Sprint 33 - Workflow Engine (Unificado).
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class StepType(StrEnum):
    """Tipo de step."""

    # Tipos genericos
    ACTION = "ACTION"  # Acao generica (usa action_id)
    CONDITION = "CONDITION"  # Condicao (usa condition_id)
    START = "START"  # Inicio do workflow
    END = "END"  # Fim do workflow
    ERROR_HANDLER = "ERROR_HANDLER"  # Handler de erro

    # Acoes especificas
    ACTION_EMAIL = "ACTION_EMAIL"  # Enviar email
    ACTION_WHATSAPP = "ACTION_WHATSAPP"  # Enviar WhatsApp
    ACTION_SMS = "ACTION_SMS"  # Enviar SMS
    ACTION_PUSH = "ACTION_PUSH"  # Enviar push notification
    ACTION_NOTIFICATION = "ACTION_NOTIFICATION"  # Enviar notificacao
    ACTION_WEBHOOK = "ACTION_WEBHOOK"  # Chamar webhook
    ACTION_TASK = "ACTION_TASK"  # Criar tarefa
    ACTION_UPDATE = "ACTION_UPDATE"  # Atualizar registro
    ACTION_CREATE = "ACTION_CREATE"  # Criar registro
    ACTION_DELETE = "ACTION_DELETE"  # Deletar registro

    # Controle de fluxo
    SWITCH = "SWITCH"  # Switch/case
    LOOP = "LOOP"  # Loop/iteracao
    PARALLEL = "PARALLEL"  # Execucao paralela
    SUBPROCESS = "SUBPROCESS"  # Sub-workflow

    # Espera
    WAIT_TIME = "WAIT_TIME"  # Aguardar tempo (delay)
    WAIT_EVENT = "WAIT_EVENT"  # Aguardar evento
    WAIT_APPROVAL = "WAIT_APPROVAL"  # Aguardar aprovacao
    DELAY = "DELAY"  # Alias para WAIT_TIME

    # Integracao
    API_CALL = "API_CALL"  # Chamada de API
    SCRIPT = "SCRIPT"  # Executar script

    # Terminadores
    END_SUCCESS = "END_SUCCESS"  # Fim com sucesso
    END_ERROR = "END_ERROR"  # Fim com erro


class StepStatus(StrEnum):
    """Status do step em execucao."""

    PENDING = "PENDING"  # Pendente
    RUNNING = "RUNNING"  # Executando
    COMPLETED = "COMPLETED"  # Completado
    FAILED = "FAILED"  # Falhou
    SKIPPED = "SKIPPED"  # Pulado
    WAITING = "WAITING"  # Aguardando
    CANCELLED = "CANCELLED"  # Cancelado
    RETRYING = "RETRYING"  # Retentando


class OnErrorAction(StrEnum):
    """Acao em caso de erro."""

    FAIL = "FAIL"  # Falhar workflow
    CONTINUE = "CONTINUE"  # Continuar para proximo step
    RETRY = "RETRY"  # Retentar step
    GOTO = "GOTO"  # Ir para step especifico (error_handler)


class WorkflowStep(Base):
    """Passo de um workflow."""

    __tablename__ = "workflow_steps"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Relacionamento com Workflow
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Identificacao
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False, default=0)

    # Tipo
    step_type = Column(
        Enum(StepType, name="steptype", create_type=True),
        nullable=False,
    )

    # Referencias (para tipos genericos ACTION e CONDITION)
    action_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_actions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    condition_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_conditions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    subprocess_workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Configuracao do step
    # Ex para email: {"template_id": "...", "to": "{{lead.email}}"}
    # Ex para condition: {"field": "lead.score", "operator": ">=", "value": 80}
    config = Column(JSONB, nullable=False, default=dict)

    # Conexoes (para designer visual)
    # Ex: {"next": "step-uuid", "on_true": "step-a", "on_false": "step-b"}
    # Ou lista detalhada: [{"to_step_id": "...", "condition": "...", "label": "..."}]
    connections = Column(JSONB, nullable=True)

    # Lista de proximos steps (para acesso rapido)
    next_step_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)

    # Posicao no designer visual
    # Ex: {"x": 100, "y": 200, "width": 200, "height": 80}
    position = Column(JSONB, nullable=True)

    # Loop config
    loop_collection = Column(String(200), nullable=True)  # Ex: "$.items"
    loop_variable = Column(String(50), default="item", nullable=True)
    loop_index_variable = Column(String(50), default="index", nullable=True)
    max_iterations = Column(Integer, default=1000, nullable=True)

    # Parallel config
    parallel_step_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    wait_for_all = Column(Boolean, default=True, nullable=True)

    # Delay config
    delay_seconds = Column(Integer, default=0, nullable=True)
    delay_until = Column(DateTime(timezone=True), nullable=True)
    delay_expression = Column(String(200), nullable=True)

    # Error handling
    on_error = Column(
        Enum(OnErrorAction, name="onerroraction", create_type=True),
        nullable=False,
        default=OnErrorAction.FAIL,
    )
    error_handler_step_id = Column(UUID(as_uuid=True), nullable=True)

    # Retry config
    max_retries = Column(Integer, default=3, nullable=False)
    retry_delay_seconds = Column(Integer, default=60, nullable=False)

    # Timeout
    timeout_seconds = Column(Integer, default=300, nullable=True)

    # Input/Output mapping
    # Ex: {"to_email": "$.lead.email", "name": "$.lead.name"}
    input_mapping = Column(JSONB, nullable=True)
    output_mapping = Column(JSONB, nullable=True)

    # Condicao de entrada (opcional)
    # Ex: {"field": "context.skip_step", "operator": "!=", "value": true}
    entry_condition = Column(JSONB, nullable=True)

    # Visual
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    is_start = Column(Boolean, default=False, nullable=False)
    is_end = Column(Boolean, default=False, nullable=False)
    continue_on_error = Column(Boolean, default=False, nullable=False)

    # Metadados
    extra_metadata = Column("metadata", JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    workflow = relationship("Workflow", back_populates="steps", foreign_keys=[workflow_id])
    action = relationship("WorkflowAction", lazy="joined")
    condition = relationship("WorkflowCondition", lazy="joined")
    subprocess_workflow = relationship("Workflow", foreign_keys=[subprocess_workflow_id], lazy="joined")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<WorkflowStep {self.name} ({self.step_type.value})>"

    @property
    def is_action(self) -> bool:
        """Verifica se e uma acao."""
        return self.step_type.value.startswith("ACTION_")

    @property
    def is_control(self) -> bool:
        """Verifica se e controle de fluxo."""
        return self.step_type in (
            StepType.CONDITION,
            StepType.SWITCH,
            StepType.LOOP,
            StepType.PARALLEL,
            StepType.SUBPROCESS,
        )

    @property
    def is_branching(self) -> bool:
        """Verifica se step cria ramificacao."""
        return self.step_type in (StepType.CONDITION, StepType.SWITCH, StepType.PARALLEL)

    @property
    def is_blocking(self) -> bool:
        """Verifica se step bloqueia execucao."""
        return self.step_type in (StepType.DELAY, StepType.WAIT_TIME, StepType.SUBPROCESS)

    @property
    def is_wait(self) -> bool:
        """Verifica se e espera."""
        return self.step_type.value.startswith("WAIT_")

    @property
    def is_terminator(self) -> bool:
        """Verifica se e terminador."""
        return self.step_type.value.startswith("END_")

    @property
    def next_step_id(self) -> str | None:
        """Retorna ID do proximo step."""
        if self.connections:
            return self.connections.get("next")
        return None

    @property
    def true_step_id(self) -> str | None:
        """Retorna ID do step se condicao for true."""
        if self.connections:
            return self.connections.get("on_true")
        return None

    @property
    def false_step_id(self) -> str | None:
        """Retorna ID do step se condicao for false."""
        if self.connections:
            return self.connections.get("on_false")
        return None

    def get_config_value(self, key: str, default: any = None) -> any:
        """Retorna valor de configuracao.

        Args:
            key: Chave da config.
            default: Valor padrao.

        Returns:
            Valor da config ou default.
        """
        if self.config:
            return self.config.get(key, default)
        return default

    def set_position(self, x: int, y: int) -> None:
        """Define posicao no designer.

        Args:
            x: Posicao X.
            y: Posicao Y.
        """
        self.position = {"x": x, "y": y}

    def connect_to(self, next_step_id: str) -> None:
        """Conecta a outro step.

        Args:
            next_step_id: ID do proximo step.
        """
        if self.connections is None:
            self.connections = {}
        self.connections["next"] = next_step_id

    def set_condition_paths(
        self,
        true_step_id: str,
        false_step_id: str,
    ) -> None:
        """Define caminhos de condicao.

        Args:
            true_step_id: ID do step se true.
            false_step_id: ID do step se false.
        """
        if self.connections is None:
            self.connections = {}
        self.connections["on_true"] = true_step_id
        self.connections["on_false"] = false_step_id

    def add_connection(
        self,
        to_step_id: str,
        condition: str | None = None,
        label: str = "",
        is_default: bool = False,
    ) -> dict:
        """Adiciona conexao detalhada para outro step.

        Args:
            to_step_id: ID do step destino.
            condition: Expressao condicional.
            label: Label da conexao.
            is_default: Se e conexao padrao.

        Returns:
            Dados da conexao.
        """
        if self.connections is None:
            self.connections = {"detailed": []}

        if "detailed" not in self.connections:
            self.connections["detailed"] = []

        connection = {
            "to_step_id": to_step_id,
            "condition": condition,
            "label": label,
            "is_default": is_default,
        }
        self.connections["detailed"].append(connection)

        # Atualiza lista de next_step_ids
        if self.next_step_ids is None:
            self.next_step_ids = []
        if to_step_id not in [str(s) for s in self.next_step_ids]:
            self.next_step_ids.append(to_step_id)

        return connection

    def remove_connection(self, to_step_id: str) -> bool:
        """Remove conexao para step.

        Args:
            to_step_id: ID do step destino.

        Returns:
            True se removeu.
        """
        removed = False

        if self.connections and "detailed" in self.connections:
            initial = len(self.connections["detailed"])
            self.connections["detailed"] = [
                c for c in self.connections["detailed"] if c.get("to_step_id") != to_step_id
            ]
            removed = len(self.connections["detailed"]) < initial

        if self.next_step_ids:
            self.next_step_ids = [s for s in self.next_step_ids if str(s) != to_step_id]

        return removed

    def clone(self, new_workflow_id: str | None = None) -> "WorkflowStep":
        """Clona step.

        Args:
            new_workflow_id: ID do novo workflow.

        Returns:
            Step clonado.
        """
        return WorkflowStep(
            workflow_id=new_workflow_id or self.workflow_id,
            name=f"{self.name} (copia)",
            description=self.description,
            order=self.order,
            step_type=self.step_type,
            action_id=self.action_id,
            condition_id=self.condition_id,
            config=self.config.copy() if self.config else {},
            loop_collection=self.loop_collection,
            loop_variable=self.loop_variable,
            loop_index_variable=self.loop_index_variable,
            max_iterations=self.max_iterations,
            delay_seconds=self.delay_seconds,
            on_error=self.on_error,
            max_retries=self.max_retries,
            retry_delay_seconds=self.retry_delay_seconds,
            timeout_seconds=self.timeout_seconds,
            input_mapping=self.input_mapping.copy() if self.input_mapping else None,
            output_mapping=self.output_mapping.copy() if self.output_mapping else None,
            position={
                "x": (self.position.get("x", 0) if self.position else 0) + 50,
                "y": (self.position.get("y", 0) if self.position else 0) + 50,
            },
            icon=self.icon,
            color=self.color,
            metadata=self.metadata.copy() if self.metadata else None,
        )
