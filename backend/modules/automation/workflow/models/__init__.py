"""Workflow Models - Sprint 33 (Unificado).

Modelos do Workflow Engine para automacao.
Inclui Action, Condition, Step, Trigger, Execution e Log.
"""

from modules.automation.workflow.models.workflow import (
    Workflow,
    WorkflowCategory,
    WorkflowPriority,
    WorkflowStatus,
)
from modules.automation.workflow.models.workflow_action import (
    BUILTIN_ACTIONS,
    ActionCategory,
    ActionType,
    WorkflowAction,
)
from modules.automation.workflow.models.workflow_condition import (
    BUILTIN_CONDITIONS,
    ConditionOperator,
    ConditionType,
    LogicalOperator,
    WorkflowCondition,
)
from modules.automation.workflow.models.workflow_execution import (
    ExecutionPriority,
    ExecutionStatus,
    WorkflowExecution,
)
from modules.automation.workflow.models.workflow_log import (
    LogLevel,
    LogType,
    WorkflowLog,
)
from modules.automation.workflow.models.workflow_step import (
    OnErrorAction,
    StepStatus,
    StepType,
    WorkflowStep,
)
from modules.automation.workflow.models.workflow_step_execution import (
    StepExecutionStatus,
    WorkflowStepExecution,
)
from modules.automation.workflow.models.workflow_trigger import (
    TriggerEvent,
    TriggerStatus,
    TriggerType,
    WorkflowTrigger,
)

__all__ = [
    # Workflow
    "Workflow",
    "WorkflowStatus",
    "WorkflowCategory",
    "WorkflowPriority",
    # Action
    "WorkflowAction",
    "ActionType",
    "ActionCategory",
    "BUILTIN_ACTIONS",
    # Condition
    "WorkflowCondition",
    "ConditionType",
    "ConditionOperator",
    "LogicalOperator",
    "BUILTIN_CONDITIONS",
    # Step
    "WorkflowStep",
    "StepType",
    "StepStatus",
    "OnErrorAction",
    # Step Execution
    "WorkflowStepExecution",
    "StepExecutionStatus",
    # Trigger
    "WorkflowTrigger",
    "TriggerType",
    "TriggerEvent",
    "TriggerStatus",
    # Execution
    "WorkflowExecution",
    "ExecutionStatus",
    "ExecutionPriority",
    # Log
    "WorkflowLog",
    "LogLevel",
    "LogType",
]
