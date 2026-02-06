"""Workflow Services - Sprint 33 (Unificado).

Servicos do Workflow Engine.

NOTA: Os services action_executor, condition_evaluator, scheduler, trigger_service,
workflow_designer e workflow_executor foram migrados do modulo workflows/.
Eles ainda usam os Dataclasses internamente para processamento, mas a persistencia
usa os models SQLAlchemy.
"""

from modules.automation.workflow.services.workflow_engine import (
    ExecutionContext,
    StepResult,
    WorkflowEngine,
)
from modules.automation.workflow.services.workflow_service import (
    ExecutionSummary,
    WorkflowService,
    WorkflowStats,
)

# Services migrados do modulo workflows/
# Nota: Estes services usam Dataclasses internamente para processamento
try:
    from modules.automation.workflow.services.action_executor import (
        ActionExecutor,
        ActionExecutorRegistry,
    )
except ImportError:
    ActionExecutor = None
    ActionExecutorRegistry = None

try:
    from modules.automation.workflow.services.condition_evaluator import (
        ConditionEvaluator,
    )
except ImportError:
    ConditionEvaluator = None

try:
    from modules.automation.workflow.services.scheduler import (
        WorkflowScheduler,
    )
except ImportError:
    WorkflowScheduler = None

try:
    from modules.automation.workflow.services.trigger_service import (
        TriggerService,
    )
except ImportError:
    TriggerService = None

try:
    from modules.automation.workflow.services.workflow_designer import (
        WorkflowDesigner,
    )
except ImportError:
    WorkflowDesigner = None

try:
    from modules.automation.workflow.services.workflow_executor import (
        WorkflowExecutor,
    )
except ImportError:
    WorkflowExecutor = None

__all__ = [
    # Service principal
    "WorkflowService",
    "WorkflowStats",
    "ExecutionSummary",
    # Engine
    "WorkflowEngine",
    "ExecutionContext",
    "StepResult",
    # Services migrados
    "ActionExecutor",
    "ActionExecutorRegistry",
    "ConditionEvaluator",
    "WorkflowScheduler",
    "TriggerService",
    "WorkflowDesigner",
    "WorkflowExecutor",
]
