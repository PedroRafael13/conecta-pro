"""
Modulo de Automacao - Conecta PRO
=================================
Workflow engine para automacao de processos de negocio.

Componentes:
- Workflow Designer: Criacao visual de workflows
- Workflow Engine: Execucao de workflows
- Trigger Service: Gatilhos automaticos
- Condition Evaluator: Avaliacao de condicoes
- Action Executor: Execucao de acoes
"""

from modules.automation.workflow.controllers import router as workflow_router
from modules.automation.workflow.models import (
    Workflow,
    WorkflowStep,
    WorkflowTrigger,
    WorkflowCondition,
    WorkflowAction,
    WorkflowExecution,
    WorkflowStepExecution,
    WorkflowLog,
)
from modules.automation.workflow.services import (
    WorkflowService,
    WorkflowEngine,
    WorkflowExecutor,
    WorkflowDesigner,
    TriggerService,
    ConditionEvaluator,
    ActionExecutor,
    WorkflowScheduler,
)

__all__ = [
    # Router
    "workflow_router",
    # Models
    "Workflow",
    "WorkflowStep",
    "WorkflowTrigger",
    "WorkflowCondition",
    "WorkflowAction",
    "WorkflowExecution",
    "WorkflowStepExecution",
    "WorkflowLog",
    # Services
    "WorkflowService",
    "WorkflowEngine",
    "WorkflowExecutor",
    "WorkflowDesigner",
    "TriggerService",
    "ConditionEvaluator",
    "ActionExecutor",
    "WorkflowScheduler",
]
