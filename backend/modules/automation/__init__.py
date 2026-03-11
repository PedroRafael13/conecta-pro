"""
Modulo de Automacao - Conecta PRO

DEPRECATED: Use 'modules.gestao' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.automation' is deprecated. "
    "Use 'modules.gestao' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from modules.automation.workflow.controllers import router as workflow_router  # noqa: E402
from modules.automation.workflow.models import (  # noqa: E402
    Workflow,
    WorkflowAction,
    WorkflowCondition,
    WorkflowExecution,
    WorkflowLog,
    WorkflowStep,
    WorkflowStepExecution,
    WorkflowTrigger,
)
from modules.automation.workflow.services import (  # noqa: E402
    ActionExecutor,
    ConditionEvaluator,
    TriggerService,
    WorkflowDesigner,
    WorkflowEngine,
    WorkflowExecutor,
    WorkflowScheduler,
    WorkflowService,
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
