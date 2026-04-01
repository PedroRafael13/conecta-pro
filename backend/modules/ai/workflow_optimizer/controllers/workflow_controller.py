"""
Workflow Controller - Sprint 55.

Endpoints REST para o otimizador de workflows com IA.
"""

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_async_session
from modules.ai.workflow_optimizer.repositories import WorkflowRepository
from modules.ai.workflow_optimizer.schemas import (
    ExecutionCreate,
    ExecutionResponse,
    ExecutionStatusEnum,
    OptimizationResponse,
    TemplateCreate,
    TemplateResponse,
    WorkflowAnalysisResult,
    WorkflowCreate,
    WorkflowDashboard,
    WorkflowListResponse,
    WorkflowResponse,
    WorkflowStatusEnum,
    WorkflowTypeEnum,
    WorkflowUpdate,
)
from modules.ai.workflow_optimizer.services import (
    WorkflowAnalyzer,
    WorkflowExecutor,
    WorkflowOptimizer,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflow-optimizer", tags=["AI Workflow Optimizer"])

# Services
_analyzer = WorkflowAnalyzer()
_optimizer = WorkflowOptimizer()
_executor = WorkflowExecutor()


def get_repository(
    session: AsyncSession = Depends(get_async_session),
) -> WorkflowRepository:
    """Obtem instancia do repositorio."""
    return WorkflowRepository(session)


# =============================================================================
# Workflow Endpoints
# =============================================================================


@router.post(
    "/workflows",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar workflow",
)
async def create_workflow(
    data: WorkflowCreate,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Cria novo workflow."""
    try:
        existing = await repo.get_workflow_by_code(data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Workflow com este codigo ja existe",
            )

        workflow_data = data.model_dump()
        workflow_data["status"] = "draft"

        workflow = await repo.create_workflow(workflow_data)
        logger.info(f"Workflow criado: {workflow.id}")
        return workflow

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar workflow",
        )


@router.get(
    "/workflows",
    response_model=list[WorkflowListResponse],
    summary="Listar workflows",
)
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: WorkflowStatusEnum | None = None,
    workflow_type: WorkflowTypeEnum | None = None,
    condominio_id: UUID | None = None,
    search: str | None = None,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Lista workflows com filtros."""
    workflows, _ = await repo.list_workflows(
        skip=skip,
        limit=limit,
        status=status,
        workflow_type=workflow_type,
        condominio_id=condominio_id,
        search=search,
    )
    return workflows


@router.get(
    "/workflows/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Obter workflow",
)
async def get_workflow(
    workflow_id: UUID,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Obtem workflow por ID."""
    workflow = await repo.get_workflow_by_id(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow nao encontrado",
        )
    return workflow


@router.patch(
    "/workflows/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Atualizar workflow",
)
async def update_workflow(
    workflow_id: UUID,
    data: WorkflowUpdate,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Atualiza workflow."""
    update_data = data.model_dump(exclude_unset=True)
    workflow = await repo.update_workflow(workflow_id, update_data)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow nao encontrado",
        )
    return workflow


@router.post(
    "/workflows/{workflow_id}/activate",
    response_model=WorkflowResponse,
    summary="Ativar workflow",
)
async def activate_workflow(
    workflow_id: UUID,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Ativa workflow."""
    workflow = await repo.update_workflow(workflow_id, {"status": "active"})
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow nao encontrado",
        )
    return workflow


@router.post(
    "/workflows/{workflow_id}/pause",
    response_model=WorkflowResponse,
    summary="Pausar workflow",
)
async def pause_workflow(
    workflow_id: UUID,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Pausa workflow."""
    workflow = await repo.update_workflow(workflow_id, {"status": "paused"})
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow nao encontrado",
        )
    return workflow


@router.delete(
    "/workflows/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar workflow",
)
async def delete_workflow(
    workflow_id: UUID,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Deleta workflow."""
    success = await repo.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow nao encontrado",
        )


# =============================================================================
# Execution Endpoints
# =============================================================================


@router.post(
    "/executions",
    response_model=ExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Executar workflow",
)
async def execute_workflow(
    data: ExecutionCreate,
    background_tasks: BackgroundTasks,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Inicia execucao de workflow."""
    workflow = await repo.get_workflow_by_id(data.workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow nao encontrado",
        )

    if workflow.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow nao esta ativo",
        )

    # Cria registro de execucao
    execution_data = {
        "workflow_id": data.workflow_id,
        "status": "pending",
        "input_data": data.input_data,
        "trigger_type": data.trigger_type,
        "trigger_data": data.trigger_data,
        "total_steps": len(workflow.steps or []),
    }

    execution = await repo.create_execution(execution_data)

    # Executa em background
    async def run_execution():
        workflow_dict = {
            "id": str(workflow.id),
            "steps": workflow.steps,
            "variables": workflow.variables,
            "settings": workflow.settings,
            "timeout_seconds": workflow.timeout_seconds,
        }

        result = await _executor.execute_workflow(
            workflow_dict,
            data.input_data,
            execution.id,
        )

        # Atualiza execucao
        await repo.update_execution(
            execution.id,
            {
                "status": result["status"],
                "current_step": result["current_step"],
                "progress_percent": result["progress_percent"],
                "output_data": result["output_data"],
                "step_results": result["step_results"],
                "logs": result["logs"],
                "error_message": result.get("error_message"),
                "error_step": result.get("error_step"),
                "started_at": datetime.fromisoformat(result["started_at"]),
                "completed_at": datetime.fromisoformat(result["completed_at"]) if result.get("completed_at") else None,
                "execution_time_ms": result["execution_time_ms"],
            },
        )

        # Atualiza stats do workflow
        await repo.update_workflow_stats(
            workflow.id,
            result["execution_time_ms"] / 1000,
            result["status"] == "completed",
        )

    background_tasks.add_task(run_execution)

    return execution


@router.get(
    "/executions",
    response_model=list[ExecutionResponse],
    summary="Listar execucoes",
)
async def list_executions(
    workflow_id: UUID | None = None,
    status: ExecutionStatusEnum | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Lista execucoes."""
    executions, _ = await repo.list_executions(
        workflow_id=workflow_id,
        status=status,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit,
    )
    return executions


@router.get(
    "/executions/{execution_id}",
    response_model=ExecutionResponse,
    summary="Obter execucao",
)
async def get_execution(
    execution_id: UUID,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Obtem execucao por ID."""
    execution = await repo.get_execution_by_id(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execucao nao encontrada",
        )
    return execution


@router.post(
    "/executions/{execution_id}/cancel",
    response_model=ExecutionResponse,
    summary="Cancelar execucao",
)
async def cancel_execution(
    execution_id: UUID,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Cancela execucao."""
    execution = await repo.update_execution(
        execution_id,
        {
            "status": "cancelled",
            "completed_at": datetime.utcnow(),
        },
    )
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execucao nao encontrada",
        )
    return execution


# =============================================================================
# Template Endpoints
# =============================================================================


@router.post(
    "/templates",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar template",
)
async def create_template(
    data: TemplateCreate,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Cria template de workflow."""
    existing = await repo.get_template_by_code(data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Template com este codigo ja existe",
        )

    template_data = data.model_dump()
    template = await repo.create_template(template_data)
    return template


@router.get(
    "/templates",
    response_model=list[TemplateResponse],
    summary="Listar templates",
)
async def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    workflow_type: WorkflowTypeEnum | None = None,
    is_active: bool | None = None,
    ai_recommended: bool | None = None,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Lista templates."""
    templates, _ = await repo.list_templates(
        skip=skip,
        limit=limit,
        workflow_type=workflow_type,
        is_active=is_active,
        ai_recommended=ai_recommended,
    )
    return templates


@router.get(
    "/templates/{template_id}",
    response_model=TemplateResponse,
    summary="Obter template",
)
async def get_template(
    template_id: UUID,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Obtem template por ID."""
    template = await repo.get_template_by_id(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template nao encontrado",
        )
    return template


@router.post(
    "/templates/{template_id}/create-workflow",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar workflow a partir de template",
)
async def create_workflow_from_template(
    template_id: UUID,
    name: str,
    code: str,
    params: dict = None,
    condominio_id: UUID | None = None,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Cria workflow a partir de template."""
    if params is None:
        params = {}
    template = await repo.get_template_by_id(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template nao encontrado",
        )

    existing = await repo.get_workflow_by_code(code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Workflow com este codigo ja existe",
        )

    workflow_data = {
        "name": name,
        "code": code,
        "description": template.description,
        "workflow_type": template.workflow_type,
        "category": template.category,
        "tags": template.tags,
        "trigger_config": template.trigger_template,
        "steps": template.steps_template,
        "variables": {**template.variables_template, **params},
        "status": "draft",
        "condominio_id": condominio_id,
    }

    workflow = await repo.create_workflow(workflow_data)
    await repo.increment_template_usage(template_id)

    return workflow


# =============================================================================
# Analysis & Optimization Endpoints
# =============================================================================


@router.post(
    "/workflows/{workflow_id}/analyze",
    response_model=WorkflowAnalysisResult,
    summary="Analisar workflow",
)
async def analyze_workflow(
    workflow_id: UUID,
    period_days: int = Query(30, ge=1, le=365),
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Analisa performance do workflow."""
    workflow = await repo.get_workflow_by_id(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow nao encontrado",
        )

    executions = await repo.get_recent_executions(workflow_id, limit=500)

    workflow_dict = {
        "id": str(workflow.id),
        "steps": workflow.steps,
        "variables": workflow.variables,
    }

    executions_dict = [
        {
            "status": e.status.value if e.status else "unknown",
            "execution_time_ms": e.execution_time_ms,
            "step_results": e.step_results or {},
            "error_message": e.error_message,
            "error_step": e.error_step,
            "created_at": e.created_at,
        }
        for e in executions
    ]

    result = _analyzer.analyze_workflow(workflow_dict, executions_dict, period_days)
    return WorkflowAnalysisResult(**result)


@router.get(
    "/workflows/{workflow_id}/optimizations",
    response_model=list[OptimizationResponse],
    summary="Listar otimizacoes",
)
async def list_workflow_optimizations(
    workflow_id: UUID,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Lista otimizacoes sugeridas para workflow."""
    optimizations, _ = await repo.list_optimizations(
        workflow_id=workflow_id,
        status=status,
        skip=skip,
        limit=limit,
    )
    return optimizations


@router.post(
    "/workflows/{workflow_id}/suggest-optimizations",
    response_model=list[OptimizationResponse],
    summary="Sugerir otimizacoes",
)
async def suggest_optimizations(
    workflow_id: UUID,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Gera novas sugestoes de otimizacao."""
    workflow = await repo.get_workflow_by_id(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow nao encontrado",
        )

    executions = await repo.get_recent_executions(workflow_id, limit=500)

    workflow_dict = {
        "id": str(workflow.id),
        "steps": workflow.steps,
        "variables": workflow.variables,
    }

    executions_dict = [
        {
            "status": e.status.value if e.status else "unknown",
            "execution_time_ms": e.execution_time_ms,
            "step_results": e.step_results or {},
            "error_message": e.error_message,
            "error_step": e.error_step,
            "created_at": e.created_at,
        }
        for e in executions
    ]

    suggestions = _optimizer.suggest_optimizations(workflow_dict, executions_dict)

    # Salva sugestoes
    created = []
    for suggestion in suggestions:
        opt_data = {
            "workflow_id": workflow_id,
            "optimization_type": suggestion["optimization_type"],
            "title": suggestion["title"],
            "description": suggestion.get("description", ""),
            "suggestion": suggestion["suggestion"],
            "estimated_improvement": suggestion["estimated_improvement"],
            "confidence": suggestion["confidence"],
            "priority": suggestion["priority"],
            "current_state": suggestion.get("current_state", {}),
            "proposed_state": suggestion.get("proposed_state", {}),
            "changes": suggestion.get("changes", []),
        }
        opt = await repo.create_optimization(opt_data)
        created.append(opt)

    return created


@router.post(
    "/optimizations/{optimization_id}/apply",
    response_model=WorkflowResponse,
    summary="Aplicar otimizacao",
)
async def apply_optimization(
    optimization_id: UUID,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Aplica otimizacao ao workflow."""
    optimization = await repo.get_optimization_by_id(optimization_id)
    if not optimization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Otimizacao nao encontrada",
        )

    if optimization.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Otimizacao nao pode ser aplicada (status: {optimization.status})",
        )

    workflow = await repo.get_workflow_by_id(optimization.workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow nao encontrado",
        )

    # Aplica otimizacao
    workflow_dict = {
        "steps": workflow.steps,
        "variables": workflow.variables,
        "settings": workflow.settings,
    }

    optimization_dict = {
        "changes": optimization.changes,
    }

    updated_workflow = _optimizer.apply_optimization(workflow_dict, optimization_dict)

    # Atualiza workflow
    await repo.update_workflow(
        workflow.id,
        {
            "steps": updated_workflow.get("steps"),
            "variables": updated_workflow.get("variables"),
            "settings": updated_workflow.get("settings"),
            "is_ai_optimized": True,
            "last_optimization": datetime.utcnow(),
        },
    )

    # Marca otimizacao como aplicada
    await repo.update_optimization_status(optimization_id, "applied")

    workflow = await repo.get_workflow_by_id(workflow.id)
    return workflow


# =============================================================================
# Dashboard Endpoint
# =============================================================================


@router.get(
    "/dashboard",
    response_model=WorkflowDashboard,
    summary="Dashboard do otimizador",
)
async def get_dashboard(
    condominio_id: UUID | None = None,
    repo: WorkflowRepository = Depends(get_repository),
    current_user: CurrentActiveUser = None,  # pylint: disable=unused-argument
):
    """Obtem dashboard do otimizador de workflows."""
    stats = await repo.get_dashboard_stats(condominio_id)

    # Busca execucoes hoje
    executions, _ = await repo.list_executions(limit=100)
    exec_by_status = {}
    for e in executions:
        status = e.status.value if e.status else "unknown"
        exec_by_status[status] = exec_by_status.get(status, 0) + 1

    return WorkflowDashboard(
        total_workflows=stats["total_workflows"],
        active_workflows=stats["active_workflows"],
        total_executions=len(executions),
        executions_today=stats["executions_today"],
        workflows_by_status=stats["workflows_by_status"],
        executions_by_status=exec_by_status,
        workflows_by_type=stats["workflows_by_type"],
        avg_success_rate=stats["avg_success_rate"],
        avg_execution_time=0.0,
        total_failures_today=exec_by_status.get("failed", 0),
        top_executed=[],
        top_failing=[],
        recently_optimized=[],
        executions_trend=[],
        success_rate_trend=[],
        pending_optimizations=stats["pending_optimizations"],
        applied_optimizations=0,
        estimated_savings=0.0,
    )
