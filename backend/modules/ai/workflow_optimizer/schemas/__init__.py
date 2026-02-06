"""
AI Workflow Optimizer Schemas - Sprint 55.
"""

from modules.ai.workflow_optimizer.schemas.workflow_schemas import (
    # Enums
    WorkflowStatusEnum,
    WorkflowTypeEnum,
    TriggerTypeEnum,
    StepTypeEnum,
    ExecutionStatusEnum,
    OptimizationTypeEnum,
    # Step
    WorkflowStep,
    TriggerConfig,
    # Workflow
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowListResponse,
    # Execution
    ExecutionCreate,
    ExecutionResponse,
    ExecutionLog,
    # Template
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    # Optimization
    OptimizationSuggestion,
    OptimizationResponse,
    ApplyOptimizationRequest,
    # Analysis
    WorkflowAnalysisRequest,
    WorkflowAnalysisResult,
    # Dashboard
    WorkflowDashboard,
)

__all__ = [
    # Enums
    "WorkflowStatusEnum",
    "WorkflowTypeEnum",
    "TriggerTypeEnum",
    "StepTypeEnum",
    "ExecutionStatusEnum",
    "OptimizationTypeEnum",
    # Step
    "WorkflowStep",
    "TriggerConfig",
    # Workflow
    "WorkflowCreate",
    "WorkflowUpdate",
    "WorkflowResponse",
    "WorkflowListResponse",
    # Execution
    "ExecutionCreate",
    "ExecutionResponse",
    "ExecutionLog",
    # Template
    "TemplateCreate",
    "TemplateUpdate",
    "TemplateResponse",
    # Optimization
    "OptimizationSuggestion",
    "OptimizationResponse",
    "ApplyOptimizationRequest",
    # Analysis
    "WorkflowAnalysisRequest",
    "WorkflowAnalysisResult",
    # Dashboard
    "WorkflowDashboard",
]
