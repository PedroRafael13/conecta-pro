"""
AIWorkflow Repository - Sprint 55.

Repositorio para persistencia de workflows e entidades relacionadas.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.ai.workflow_optimizer.models import (
    AIWorkflow,
    AIWorkflowExecution,
    ExecutionStatusEnum,
    WorkflowMetrics,
    WorkflowOptimization,
    WorkflowStatusEnum,
    WorkflowTemplate,
    WorkflowTypeEnum,
)


class WorkflowRepository:
    """Repositorio para operacoes com workflows."""

    def __init__(self, session: AsyncSession):
        """Inicializa repositorio."""
        self.session = session

    # =========================================================================
    # AIWorkflow CRUD
    # =========================================================================

    async def create_workflow(self, workflow_data: dict[str, Any]) -> AIWorkflow:
        """Cria novo workflow."""
        workflow = AIWorkflow(**workflow_data)
        self.session.add(workflow)
        await self.session.commit()
        await self.session.refresh(workflow)
        return workflow

    async def get_workflow_by_id(
        self,
        workflow_id: UUID,
        include_executions: bool = False,
    ) -> AIWorkflow | None:
        """Busca workflow por ID."""
        query = select(AIWorkflow).where(and_(AIWorkflow.id == workflow_id, AIWorkflow.ativo))

        if include_executions:
            query = query.options(selectinload(AIWorkflow.executions))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_workflow_by_code(self, code: str) -> AIWorkflow | None:
        """Busca workflow por codigo."""
        query = select(AIWorkflow).where(and_(AIWorkflow.code == code, AIWorkflow.ativo))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_workflows(
        self,
        skip: int = 0,
        limit: int = 100,
        status: WorkflowStatusEnum | None = None,
        workflow_type: WorkflowTypeEnum | None = None,
        condominio_id: UUID | None = None,
        search: str | None = None,
    ) -> tuple[list[AIWorkflow], int]:
        """Lista workflows com filtros."""
        query = select(AIWorkflow).where(AIWorkflow.ativo)

        if status:
            query = query.where(AIWorkflow.status == status)
        if workflow_type:
            query = query.where(AIWorkflow.workflow_type == workflow_type)
        if condominio_id:
            query = query.where(AIWorkflow.condominio_id == condominio_id)
        if search:
            search_filter = or_(
                AIWorkflow.name.ilike(f"%{search}%"),
                AIWorkflow.code.ilike(f"%{search}%"),
                AIWorkflow.description.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        query = query.order_by(desc(AIWorkflow.updated_at)).offset(skip).limit(limit)

        result = await self.session.execute(query)
        workflows = result.scalars().all()

        return list(workflows), total

    async def update_workflow(
        self,
        workflow_id: UUID,
        update_data: dict[str, Any],
    ) -> AIWorkflow | None:
        """Atualiza workflow."""
        workflow = await self.get_workflow_by_id(workflow_id)
        if not workflow:
            return None

        for key, value in update_data.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)

        workflow.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(workflow)
        return workflow

    async def update_workflow_stats(
        self,
        workflow_id: UUID,
        execution_time: float,
        success: bool,
    ) -> None:
        """Atualiza estatisticas do workflow."""
        workflow = await self.get_workflow_by_id(workflow_id)
        if not workflow:
            return

        workflow.execution_count += 1
        workflow.total_execution_time += execution_time

        if success:
            workflow.success_count += 1
        else:
            workflow.failure_count += 1

        workflow.avg_execution_time = workflow.total_execution_time / workflow.execution_count
        workflow.success_rate = workflow.success_count / workflow.execution_count
        workflow.last_run_at = datetime.utcnow()

        await self.session.commit()

    async def delete_workflow(self, workflow_id: UUID, soft: bool = True) -> bool:
        """Deleta workflow."""
        if soft:
            workflow = await self.update_workflow(
                workflow_id,
                {
                    "ativo": False,
                    "status": WorkflowStatusEnum.DISABLED,
                },
            )
            return workflow is not None
        else:
            workflow = await self.get_workflow_by_id(workflow_id)
            if workflow:
                await self.session.delete(workflow)
                await self.session.commit()
                return True
            return False

    # =========================================================================
    # Execution CRUD
    # =========================================================================

    async def create_execution(
        self,
        execution_data: dict[str, Any],
    ) -> AIWorkflowExecution:
        """Cria execucao."""
        execution = AIWorkflowExecution(**execution_data)
        self.session.add(execution)
        await self.session.commit()
        await self.session.refresh(execution)
        return execution

    async def get_execution_by_id(
        self,
        execution_id: UUID,
    ) -> AIWorkflowExecution | None:
        """Busca execucao por ID."""
        query = select(AIWorkflowExecution).where(AIWorkflowExecution.id == execution_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_executions(
        self,
        workflow_id: UUID | None = None,
        status: ExecutionStatusEnum | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[AIWorkflowExecution], int]:
        """Lista execucoes."""
        query = select(AIWorkflowExecution)

        if workflow_id:
            query = query.where(AIWorkflowExecution.workflow_id == workflow_id)
        if status:
            query = query.where(AIWorkflowExecution.status == status)
        if from_date:
            query = query.where(AIWorkflowExecution.created_at >= from_date)
        if to_date:
            query = query.where(AIWorkflowExecution.created_at <= to_date)

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        query = query.order_by(desc(AIWorkflowExecution.created_at)).offset(skip).limit(limit)

        result = await self.session.execute(query)
        executions = result.scalars().all()

        return list(executions), total

    async def update_execution(
        self,
        execution_id: UUID,
        update_data: dict[str, Any],
    ) -> AIWorkflowExecution | None:
        """Atualiza execucao."""
        execution = await self.get_execution_by_id(execution_id)
        if not execution:
            return None

        for key, value in update_data.items():
            if hasattr(execution, key):
                setattr(execution, key, value)

        execution.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(execution)
        return execution

    async def get_recent_executions(
        self,
        workflow_id: UUID,
        limit: int = 100,
    ) -> list[AIWorkflowExecution]:
        """Busca execucoes recentes."""
        query = (
            select(AIWorkflowExecution)
            .where(AIWorkflowExecution.workflow_id == workflow_id)
            .order_by(desc(AIWorkflowExecution.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # =========================================================================
    # Template CRUD
    # =========================================================================

    async def create_template(
        self,
        template_data: dict[str, Any],
    ) -> WorkflowTemplate:
        """Cria template."""
        template = WorkflowTemplate(**template_data)
        self.session.add(template)
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def get_template_by_id(
        self,
        template_id: UUID,
    ) -> WorkflowTemplate | None:
        """Busca template por ID."""
        query = select(WorkflowTemplate).where(and_(WorkflowTemplate.id == template_id, WorkflowTemplate.ativo))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_template_by_code(self, code: str) -> WorkflowTemplate | None:
        """Busca template por codigo."""
        query = select(WorkflowTemplate).where(and_(WorkflowTemplate.code == code, WorkflowTemplate.ativo))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_templates(
        self,
        skip: int = 0,
        limit: int = 100,
        workflow_type: WorkflowTypeEnum | None = None,
        is_active: bool | None = None,
        ai_recommended: bool | None = None,
    ) -> tuple[list[WorkflowTemplate], int]:
        """Lista templates."""
        query = select(WorkflowTemplate).where(WorkflowTemplate.ativo)

        if workflow_type:
            query = query.where(WorkflowTemplate.workflow_type == workflow_type)
        if is_active is not None:
            query = query.where(WorkflowTemplate.is_active == is_active)
        if ai_recommended is not None:
            query = query.where(WorkflowTemplate.ai_recommended == ai_recommended)

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        query = query.order_by(desc(WorkflowTemplate.usage_count)).offset(skip).limit(limit)

        result = await self.session.execute(query)
        templates = result.scalars().all()

        return list(templates), total

    async def update_template(
        self,
        template_id: UUID,
        update_data: dict[str, Any],
    ) -> WorkflowTemplate | None:
        """Atualiza template."""
        template = await self.get_template_by_id(template_id)
        if not template:
            return None

        for key, value in update_data.items():
            if hasattr(template, key):
                setattr(template, key, value)

        template.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def increment_template_usage(self, template_id: UUID) -> None:
        """Incrementa uso do template."""
        template = await self.get_template_by_id(template_id)
        if template:
            template.usage_count += 1
            await self.session.commit()

    # =========================================================================
    # Optimization CRUD
    # =========================================================================

    async def create_optimization(
        self,
        optimization_data: dict[str, Any],
    ) -> WorkflowOptimization:
        """Cria otimizacao."""
        optimization = WorkflowOptimization(**optimization_data)
        self.session.add(optimization)
        await self.session.commit()
        await self.session.refresh(optimization)
        return optimization

    async def get_optimization_by_id(
        self,
        optimization_id: UUID,
    ) -> WorkflowOptimization | None:
        """Busca otimizacao por ID."""
        query = select(WorkflowOptimization).where(WorkflowOptimization.id == optimization_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_optimizations(
        self,
        workflow_id: UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[WorkflowOptimization], int]:
        """Lista otimizacoes."""
        query = select(WorkflowOptimization)

        if workflow_id:
            query = query.where(WorkflowOptimization.workflow_id == workflow_id)
        if status:
            query = query.where(WorkflowOptimization.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        query = query.order_by(desc(WorkflowOptimization.priority)).offset(skip).limit(limit)

        result = await self.session.execute(query)
        optimizations = result.scalars().all()

        return list(optimizations), total

    async def update_optimization_status(
        self,
        optimization_id: UUID,
        status: str,
        applied_by: UUID | None = None,
        actual_improvement: float | None = None,
    ) -> WorkflowOptimization | None:
        """Atualiza status de otimizacao."""
        optimization = await self.get_optimization_by_id(optimization_id)
        if not optimization:
            return None

        optimization.status = status
        if status == "applied":
            optimization.applied_at = datetime.utcnow()
            optimization.applied_by = applied_by
        if actual_improvement is not None:
            optimization.actual_improvement = actual_improvement

        await self.session.commit()
        await self.session.refresh(optimization)
        return optimization

    # =========================================================================
    # Metrics
    # =========================================================================

    async def save_metrics(
        self,
        metrics_data: dict[str, Any],
    ) -> WorkflowMetrics:
        """Salva metricas."""
        metrics = WorkflowMetrics(**metrics_data)
        self.session.add(metrics)
        await self.session.commit()
        await self.session.refresh(metrics)
        return metrics

    async def get_metrics(
        self,
        workflow_id: UUID,
        period_type: str = "daily",
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[WorkflowMetrics]:
        """Busca metricas."""
        query = select(WorkflowMetrics).where(
            and_(
                WorkflowMetrics.workflow_id == workflow_id,
                WorkflowMetrics.period_type == period_type,
            )
        )

        if from_date:
            query = query.where(WorkflowMetrics.period_start >= from_date)
        if to_date:
            query = query.where(WorkflowMetrics.period_end <= to_date)

        query = query.order_by(desc(WorkflowMetrics.period_start))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    # =========================================================================
    # Dashboard
    # =========================================================================

    async def get_dashboard_stats(
        self,
        condominio_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Obtem estatisticas para dashboard."""
        # Total de workflows
        wf_query = select(func.count()).where(AIWorkflow.ativo)
        if condominio_id:
            wf_query = wf_query.where(AIWorkflow.condominio_id == condominio_id)
        total_wf = (await self.session.execute(wf_query)).scalar()

        # Workflows ativos
        active_query = select(func.count()).where(
            and_(AIWorkflow.ativo, AIWorkflow.status == WorkflowStatusEnum.ACTIVE)
        )
        if condominio_id:
            active_query = active_query.where(AIWorkflow.condominio_id == condominio_id)
        active_wf = (await self.session.execute(active_query)).scalar()

        # Por status
        status_query = select(AIWorkflow.status, func.count()).where(AIWorkflow.ativo).group_by(AIWorkflow.status)
        if condominio_id:
            status_query = status_query.where(AIWorkflow.condominio_id == condominio_id)
        status_result = await self.session.execute(status_query)
        by_status = {str(row[0].value): row[1] for row in status_result}

        # Por tipo
        type_query = (
            select(AIWorkflow.workflow_type, func.count()).where(AIWorkflow.ativo).group_by(AIWorkflow.workflow_type)
        )
        if condominio_id:
            type_query = type_query.where(AIWorkflow.condominio_id == condominio_id)
        type_result = await self.session.execute(type_query)
        by_type = {str(row[0].value): row[1] for row in type_result}

        # Execucoes hoje
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        exec_today_query = select(func.count()).where(AIWorkflowExecution.created_at >= today_start)
        exec_today = (await self.session.execute(exec_today_query)).scalar()

        # Media de sucesso
        avg_success_query = select(func.avg(AIWorkflow.success_rate)).where(
            and_(AIWorkflow.ativo, AIWorkflow.execution_count > 0)
        )
        if condominio_id:
            avg_success_query = avg_success_query.where(AIWorkflow.condominio_id == condominio_id)
        avg_success = (await self.session.execute(avg_success_query)).scalar() or 0

        # Otimizacoes pendentes
        pending_opt = (
            await self.session.execute(select(func.count()).where(WorkflowOptimization.status == "pending"))
        ).scalar()

        return {
            "total_workflows": total_wf,
            "active_workflows": active_wf,
            "workflows_by_status": by_status,
            "workflows_by_type": by_type,
            "executions_today": exec_today,
            "avg_success_rate": float(avg_success),
            "pending_optimizations": pending_opt,
        }
