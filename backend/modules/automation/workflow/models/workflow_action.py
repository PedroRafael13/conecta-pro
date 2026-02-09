"""Workflow Action Model - Acoes executaveis.

Sprint 33 - Workflow Engine (Unificado).
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class ActionType(StrEnum):
    """Tipo de acao."""

    # Comunicacao
    SEND_EMAIL = "SEND_EMAIL"
    SEND_SMS = "SEND_SMS"
    SEND_WHATSAPP = "SEND_WHATSAPP"
    SEND_PUSH = "SEND_PUSH"
    SEND_NOTIFICATION = "SEND_NOTIFICATION"

    # Integracao
    HTTP_REQUEST = "HTTP_REQUEST"
    WEBHOOK = "WEBHOOK"
    API_CALL = "API_CALL"

    # Dados
    CREATE_RECORD = "CREATE_RECORD"
    UPDATE_RECORD = "UPDATE_RECORD"
    DELETE_RECORD = "DELETE_RECORD"
    QUERY_DATA = "QUERY_DATA"

    # Documentos
    GENERATE_PDF = "GENERATE_PDF"
    PROCESS_DOCUMENT = "PROCESS_DOCUMENT"
    SEND_DOCUMENT = "SEND_DOCUMENT"

    # Tarefas
    CREATE_TASK = "CREATE_TASK"
    ASSIGN_TASK = "ASSIGN_TASK"
    CREATE_TICKET = "CREATE_TICKET"

    # Sistema
    LOG_MESSAGE = "LOG_MESSAGE"
    SET_VARIABLE = "SET_VARIABLE"
    TRANSFORM_DATA = "TRANSFORM_DATA"
    DELAY = "DELAY"

    # Financeiro
    CREATE_INVOICE = "CREATE_INVOICE"
    PROCESS_PAYMENT = "PROCESS_PAYMENT"
    GENERATE_BOLETO = "GENERATE_BOLETO"

    # Aprovacao
    REQUEST_APPROVAL = "REQUEST_APPROVAL"
    ESCALATE = "ESCALATE"

    # IA
    AI_ANALYSIS = "AI_ANALYSIS"
    CLASSIFY_DOCUMENT = "CLASSIFY_DOCUMENT"
    EXTRACT_DATA = "EXTRACT_DATA"

    # Custom
    CUSTOM_SCRIPT = "CUSTOM_SCRIPT"
    SUBPROCESS = "SUBPROCESS"


class ActionCategory(StrEnum):
    """Categoria da acao."""

    COMMUNICATION = "COMMUNICATION"
    INTEGRATION = "INTEGRATION"
    DATA = "DATA"
    DOCUMENTS = "DOCUMENTS"
    TASKS = "TASKS"
    SYSTEM = "SYSTEM"
    FINANCIAL = "FINANCIAL"
    APPROVAL = "APPROVAL"
    AI = "AI"
    CUSTOM = "CUSTOM"


class WorkflowAction(Base):
    """Acao executavel no workflow."""

    __tablename__ = "workflow_actions"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Tipo e Categoria
    action_type = Column(
        Enum(ActionType, name="actiontype", create_type=True),
        nullable=False,
    )
    category = Column(
        Enum(ActionCategory, name="actioncategory", create_type=True),
        nullable=False,
        default=ActionCategory.CUSTOM,
    )

    # Configuracao base
    # Ex: {"timeout_seconds": 60, "retry_count": 3, "async_execution": false}
    config = Column(JSONB, nullable=False, default=dict)

    # Configuracoes especificas por tipo
    # Ex para email: {"to": [...], "subject": "...", "template_id": "..."}
    # Ex para http: {"url": "...", "method": "POST", "headers": {...}}
    # Ex para whatsapp: {"phone_numbers": [...], "template_name": "..."}
    type_config = Column(JSONB, nullable=True)

    # Input/Output schemas
    # Ex: {"type": "object", "properties": {"email": {"type": "string"}}}
    input_schema = Column(JSONB, nullable=True)
    output_schema = Column(JSONB, nullable=True)

    # Mapeamento de variaveis
    # Ex: {"to_email": "$.lead.email", "name": "$.lead.name"}
    input_mapping = Column(JSONB, nullable=True)
    output_mapping = Column(JSONB, nullable=True)

    # Template de mensagem (para acoes de comunicacao)
    message_template = Column(Text, nullable=True)
    template_engine = Column(String(20), default="jinja2", nullable=False)

    # Script customizado
    custom_script = Column(Text, nullable=True)
    script_language = Column(String(20), default="python", nullable=True)

    # Visual (para designer)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)

    # Flags
    is_enabled = Column(Boolean, default=True, nullable=False)
    is_builtin = Column(Boolean, default=False, nullable=False)

    # Estatisticas
    execution_count = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failure_count = Column(Integer, default=0, nullable=False)
    avg_execution_time_ms = Column(Float, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<WorkflowAction {self.name} ({self.action_type.value})>"

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso."""
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count

    @property
    def is_communication(self) -> bool:
        """Verifica se e acao de comunicacao."""
        return self.action_type.value.startswith("SEND_")

    @property
    def is_data_operation(self) -> bool:
        """Verifica se e operacao de dados."""
        return self.action_type in (
            ActionType.CREATE_RECORD,
            ActionType.UPDATE_RECORD,
            ActionType.DELETE_RECORD,
            ActionType.QUERY_DATA,
        )

    def get_config_value(self, key: str, default: any = None) -> any:
        """Retorna valor de configuracao.

        Args:
            key: Chave da config.
            default: Valor padrao.

        Returns:
            Valor ou default.
        """
        if self.config:
            return self.config.get(key, default)
        return default

    def get_type_config_value(self, key: str, default: any = None) -> any:
        """Retorna valor de configuracao especifica do tipo.

        Args:
            key: Chave da config.
            default: Valor padrao.

        Returns:
            Valor ou default.
        """
        if self.type_config:
            return self.type_config.get(key, default)
        return default

    def update_statistics(self, success: bool, execution_time_ms: float) -> None:
        """Atualiza estatisticas.

        Args:
            success: Se execucao foi sucesso.
            execution_time_ms: Tempo de execucao em ms.
        """
        self.execution_count = (self.execution_count or 0) + 1

        if success:
            self.success_count = (self.success_count or 0) + 1
        else:
            self.failure_count = (self.failure_count or 0) + 1

        # Media movel do tempo de execucao
        if self.avg_execution_time_ms == 0:
            self.avg_execution_time_ms = execution_time_ms
        else:
            self.avg_execution_time_ms = self.avg_execution_time_ms * 0.9 + execution_time_ms * 0.1

    def validate(self) -> list[str]:
        """Valida configuracao da action.

        Returns:
            Lista de erros de validacao.
        """
        errors = []

        if not self.name:
            errors.append("Nome e obrigatorio")

        if self.action_type == ActionType.SEND_EMAIL:
            if not self.type_config:
                errors.append("Configuracao de email obrigatoria")
            elif not self.type_config.get("to") and not self.type_config.get("template_id"):
                errors.append("Destinatario ou template obrigatorio")

        if self.action_type == ActionType.HTTP_REQUEST:
            if not self.type_config:
                errors.append("Configuracao HTTP obrigatoria")
            elif not self.type_config.get("url"):
                errors.append("URL obrigatoria")

        if self.action_type == ActionType.CUSTOM_SCRIPT:
            if not self.custom_script:
                errors.append("Script customizado obrigatorio")

        return errors

    def clone(self, new_name: str) -> "WorkflowAction":
        """Clona action.

        Args:
            new_name: Novo nome.

        Returns:
            Nova action clonada.
        """
        return WorkflowAction(
            tenant_id=self.tenant_id,
            name=new_name,
            description=f"Copia de: {self.name}",
            action_type=self.action_type,
            category=self.category,
            config=self.config.copy() if self.config else {},
            type_config=self.type_config.copy() if self.type_config else {},
            input_schema=self.input_schema.copy() if self.input_schema else {},
            output_schema=self.output_schema.copy() if self.output_schema else {},
            input_mapping=self.input_mapping.copy() if self.input_mapping else {},
            output_mapping=self.output_mapping.copy() if self.output_mapping else {},
            message_template=self.message_template,
            template_engine=self.template_engine,
            custom_script=self.custom_script,
            script_language=self.script_language,
            icon=self.icon,
            color=self.color,
        )


# Actions builtin
BUILTIN_ACTIONS = {
    "send_email": {
        "name": "Enviar Email",
        "action_type": ActionType.SEND_EMAIL,
        "category": ActionCategory.COMMUNICATION,
        "icon": "mail",
        "color": "#3B82F6",
    },
    "send_whatsapp": {
        "name": "Enviar WhatsApp",
        "action_type": ActionType.SEND_WHATSAPP,
        "category": ActionCategory.COMMUNICATION,
        "icon": "message-circle",
        "color": "#25D366",
    },
    "create_task": {
        "name": "Criar Tarefa",
        "action_type": ActionType.CREATE_TASK,
        "category": ActionCategory.TASKS,
        "icon": "check-square",
        "color": "#8B5CF6",
    },
    "http_request": {
        "name": "Requisicao HTTP",
        "action_type": ActionType.HTTP_REQUEST,
        "category": ActionCategory.INTEGRATION,
        "icon": "globe",
        "color": "#F59E0B",
    },
    "process_document": {
        "name": "Processar Documento",
        "action_type": ActionType.PROCESS_DOCUMENT,
        "category": ActionCategory.DOCUMENTS,
        "icon": "file-text",
        "color": "#10B981",
    },
    "generate_boleto": {
        "name": "Gerar Boleto",
        "action_type": ActionType.GENERATE_BOLETO,
        "category": ActionCategory.FINANCIAL,
        "icon": "file-invoice",
        "color": "#EF4444",
    },
    "ai_analysis": {
        "name": "Analise IA",
        "action_type": ActionType.AI_ANALYSIS,
        "category": ActionCategory.AI,
        "icon": "brain",
        "color": "#6366F1",
    },
}
