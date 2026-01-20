"""
AI AIWorkflow Optimizer Module - Sprint 55.

Otimizador inteligente de workflows com:
- Execucao automatizada de workflows
- Analise de performance com IA
- Sugestoes de otimizacao
- Templates pre-definidos
- Metricas e dashboard
"""

from modules.ai.workflow_optimizer.models import (
    AIWorkflow,
    AIWorkflowExecution,
    WorkflowTemplate,
    WorkflowOptimization,
    WorkflowMetrics,
    WorkflowStatusEnum,
    WorkflowTypeEnum,
    TriggerTypeEnum,
    StepTypeEnum,
    ExecutionStatusEnum,
    OptimizationTypeEnum,
)
from modules.ai.workflow_optimizer.services import (
    WorkflowAnalyzer,
    WorkflowOptimizer,
    WorkflowExecutor,
    StepExecutor,
)
from modules.ai.workflow_optimizer.repositories import WorkflowRepository
from modules.ai.workflow_optimizer.controllers import router

__all__ = [
    # Models
    "AIWorkflow",
    "AIWorkflowExecution",
    "WorkflowTemplate",
    "WorkflowOptimization",
    "WorkflowMetrics",
    # Enums
    "WorkflowStatusEnum",
    "WorkflowTypeEnum",
    "TriggerTypeEnum",
    "StepTypeEnum",
    "ExecutionStatusEnum",
    "OptimizationTypeEnum",
    # Services
    "WorkflowAnalyzer",
    "WorkflowOptimizer",
    "WorkflowExecutor",
    "StepExecutor",
    # Repository
    "WorkflowRepository",
    # Router
    "router",
]
