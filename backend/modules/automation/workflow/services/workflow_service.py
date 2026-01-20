"""Workflow Service - Gestao de Workflows.

Sprint 33 - Workflow Engine.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Integer, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.automation.workflow.models.workflow import (
    Workflow,
    WorkflowCategory,
    WorkflowStatus,
)
from modules.automation.workflow.models.workflow_execution import (
    ExecutionStatus,
    WorkflowExecution,
)
from modules.automation.workflow.models.workflow_log import WorkflowLog
from modules.automation.workflow.models.workflow_step import StepType, WorkflowStep
from modules.automation.workflow.models.workflow_trigger import (
    TriggerType,
    WorkflowTrigger,
)


@dataclass
class WorkflowStats:
    """Estatisticas de workflow."""

    total_workflows: int = 0
    active_workflows: int = 0
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    avg_execution_time_ms: float = 0.0

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso."""
        if not self.total_executions:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100


@dataclass
class ExecutionSummary:
    """Resumo de execucao."""

    execution_id: UUID
    workflow_name: str
    status: ExecutionStatus
    steps_executed: int
    duration_ms: Optional[int]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class WorkflowService:
    """Servico de gestao de workflows."""

    def __init__(self, session: AsyncSession):
        """Inicializa servico.

        Args:
            session: Sessao do banco.
        """
        self.session = session

    # ==================== CRUD Workflows ====================

    async def create_workflow(
        self,
        tenant_id: UUID,
        name: str,
        slug: str,
        category: WorkflowCategory = WorkflowCategory.CUSTOM,
        description: Optional[str] = None,
        config: Optional[dict] = None,
        context_variables: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        created_by: Optional[UUID] = None,
    ) -> Workflow:
        """Cria novo workflow.

        Args:
            tenant_id: ID do tenant.
            name: Nome.
            slug: Slug unico.
            category: Categoria.
            description: Descricao.
            config: Configuracao.
            context_variables: Variaveis de contexto.
            tags: Tags.
            created_by: Usuario criador.

        Returns:
            Workflow criado.
        """
        workflow = Workflow(
            tenant_id=tenant_id,
            name=name,
            slug=slug,
            category=category,
            description=description,
            config=config or {},
            context_variables=context_variables,
            tags=tags,
            status=WorkflowStatus.DRAFT,
            created_by=created_by,
        )

        self.session.add(workflow)
        await self.session.flush()

        return workflow

    async def get_workflow(
        self,
        workflow_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[Workflow]:
        """Busca workflow por ID.

        Args:
            workflow_id: ID do workflow.
            tenant_id: ID do tenant (opcional).

        Returns:
            Workflow ou None.
        """
        query = select(Workflow).where(Workflow.id == workflow_id)

        if tenant_id:
            query = query.where(Workflow.tenant_id == tenant_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_workflow_by_slug(
        self,
        tenant_id: UUID,
        slug: str,
    ) -> Optional[Workflow]:
        """Busca workflow por slug.

        Args:
            tenant_id: ID do tenant.
            slug: Slug do workflow.

        Returns:
            Workflow ou None.
        """
        query = select(Workflow).where(
            and_(
                Workflow.tenant_id == tenant_id,
                Workflow.slug == slug,
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_workflows(
        self,
        tenant_id: UUID,
        category: Optional[WorkflowCategory] = None,
        status: Optional[WorkflowStatus] = None,
        active_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Workflow]:
        """Lista workflows.

        Args:
            tenant_id: ID do tenant.
            category: Filtro por categoria.
            status: Filtro por status.
            active_only: Apenas ativos.
            limit: Limite.
            offset: Offset.

        Returns:
            Lista de workflows.
        """
        query = select(Workflow).where(Workflow.tenant_id == tenant_id)

        if category:
            query = query.where(Workflow.category == category)

        if status:
            query = query.where(Workflow.status == status)

        if active_only:
            query = query.where(
                and_(
                    Workflow.status == WorkflowStatus.ACTIVE,
                    Workflow.active.is_(True),
                )
            )

        query = query.order_by(Workflow.created_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_workflow(
        self,
        workflow: Workflow,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[dict] = None,
        context_variables: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        updated_by: Optional[UUID] = None,
    ) -> Workflow:
        """Atualiza workflow.

        Args:
            workflow: Workflow a atualizar.
            name: Novo nome.
            description: Nova descricao.
            config: Nova config.
            context_variables: Novas variaveis.
            tags: Novas tags.
            updated_by: Usuario que atualizou.

        Returns:
            Workflow atualizado.
        """
        if name is not None:
            workflow.name = name

        if description is not None:
            workflow.description = description

        if config is not None:
            workflow.config = config

        if context_variables is not None:
            workflow.context_variables = context_variables

        if tags is not None:
            workflow.tags = tags

        if updated_by:
            workflow.updated_by = updated_by

        await self.session.flush()
        return workflow

    async def delete_workflow(self, workflow: Workflow) -> None:
        """Deleta workflow.

        Args:
            workflow: Workflow a deletar.
        """
        await self.session.delete(workflow)
        await self.session.flush()

    # ==================== Workflow Actions ====================

    async def activate_workflow(self, workflow: Workflow) -> Workflow:
        """Ativa workflow.

        Args:
            workflow: Workflow a ativar.

        Returns:
            Workflow atualizado.
        """
        workflow.activate()
        await self.session.flush()
        return workflow

    async def deactivate_workflow(self, workflow: Workflow) -> Workflow:
        """Desativa workflow.

        Args:
            workflow: Workflow a desativar.

        Returns:
            Workflow atualizado.
        """
        workflow.deactivate()
        await self.session.flush()
        return workflow

    async def clone_workflow(
        self,
        workflow: Workflow,
        new_name: str,
        new_slug: str,
    ) -> Workflow:
        """Clona workflow.

        Args:
            workflow: Workflow a clonar.
            new_name: Nome do novo.
            new_slug: Slug do novo.

        Returns:
            Novo workflow.
        """
        # Clona workflow
        new_workflow = workflow.clone(new_name)
        new_workflow.slug = new_slug

        self.session.add(new_workflow)
        await self.session.flush()

        # Clona steps
        for step in workflow.steps:
            new_step = WorkflowStep(
                workflow_id=new_workflow.id,
                name=step.name,
                description=step.description,
                order=step.order,
                step_type=step.step_type,
                config=step.config,
                connections=step.connections,
                position=step.position,
                max_retries=step.max_retries,
                retry_delay_seconds=step.retry_delay_seconds,
                timeout_seconds=step.timeout_seconds,
                entry_condition=step.entry_condition,
                is_start=step.is_start,
                is_end=step.is_end,
                continue_on_error=step.continue_on_error,
            )
            self.session.add(new_step)

        # Clona triggers
        for trigger in workflow.triggers:
            new_trigger = WorkflowTrigger(
                workflow_id=new_workflow.id,
                name=trigger.name,
                description=trigger.description,
                trigger_type=trigger.trigger_type,
                config=trigger.config,
                filters=trigger.filters,
                max_executions=trigger.max_executions,
                cooldown_seconds=trigger.cooldown_seconds,
                priority=trigger.priority,
                once_per_entity=trigger.once_per_entity,
            )
            self.session.add(new_trigger)

        await self.session.flush()
        return new_workflow

    # ==================== CRUD Steps ====================

    async def add_step(
        self,
        workflow: Workflow,
        name: str,
        step_type: StepType,
        config: dict,
        order: Optional[int] = None,
        description: Optional[str] = None,
        is_start: bool = False,
        is_end: bool = False,
    ) -> WorkflowStep:
        """Adiciona step ao workflow.

        Args:
            workflow: Workflow.
            name: Nome do step.
            step_type: Tipo do step.
            config: Configuracao.
            order: Ordem (auto se None).
            description: Descricao.
            is_start: Se e step inicial.
            is_end: Se e step final.

        Returns:
            Step criado.
        """
        # Auto order
        if order is None:
            order = len(workflow.steps) if workflow.steps else 0

        step = WorkflowStep(
            workflow_id=workflow.id,
            name=name,
            description=description,
            order=order,
            step_type=step_type,
            config=config,
            is_start=is_start,
            is_end=is_end,
        )

        self.session.add(step)
        await self.session.flush()

        return step

    async def update_step(
        self,
        step: WorkflowStep,
        name: Optional[str] = None,
        config: Optional[dict] = None,
        order: Optional[int] = None,
        connections: Optional[dict] = None,
        position: Optional[dict] = None,
    ) -> WorkflowStep:
        """Atualiza step.

        Args:
            step: Step a atualizar.
            name: Novo nome.
            config: Nova config.
            order: Nova ordem.
            connections: Novas conexoes.
            position: Nova posicao.

        Returns:
            Step atualizado.
        """
        if name is not None:
            step.name = name

        if config is not None:
            step.config = config

        if order is not None:
            step.order = order

        if connections is not None:
            step.connections = connections

        if position is not None:
            step.position = position

        await self.session.flush()
        return step

    async def delete_step(self, step: WorkflowStep) -> None:
        """Deleta step.

        Args:
            step: Step a deletar.
        """
        await self.session.delete(step)
        await self.session.flush()

    # ==================== CRUD Triggers ====================

    async def add_trigger(
        self,
        workflow: Workflow,
        name: str,
        trigger_type: TriggerType,
        config: dict,
        description: Optional[str] = None,
        filters: Optional[dict] = None,
        max_executions: Optional[int] = None,
    ) -> WorkflowTrigger:
        """Adiciona trigger ao workflow.

        Args:
            workflow: Workflow.
            name: Nome.
            trigger_type: Tipo.
            config: Configuracao.
            description: Descricao.
            filters: Filtros.
            max_executions: Limite de execucoes.

        Returns:
            Trigger criado.
        """
        trigger = WorkflowTrigger(
            workflow_id=workflow.id,
            name=name,
            description=description,
            trigger_type=trigger_type,
            config=config,
            filters=filters,
            max_executions=max_executions,
        )

        self.session.add(trigger)
        await self.session.flush()

        return trigger

    async def delete_trigger(self, trigger: WorkflowTrigger) -> None:
        """Deleta trigger.

        Args:
            trigger: Trigger a deletar.
        """
        await self.session.delete(trigger)
        await self.session.flush()

    # ==================== Estatisticas ====================

    async def get_workflow_stats(
        self,
        tenant_id: UUID,
    ) -> WorkflowStats:
        """Retorna estatisticas de workflows.

        Args:
            tenant_id: ID do tenant.

        Returns:
            Estatisticas.
        """
        # Total workflows
        total_query = select(func.count(Workflow.id)).where(
            Workflow.tenant_id == tenant_id
        )
        total_result = await self.session.execute(total_query)
        total_workflows = total_result.scalar() or 0

        # Ativos
        active_query = select(func.count(Workflow.id)).where(
            and_(
                Workflow.tenant_id == tenant_id,
                Workflow.status == WorkflowStatus.ACTIVE,
            )
        )
        active_result = await self.session.execute(active_query)
        active_workflows = active_result.scalar() or 0

        # Execucoes
        exec_query = select(
            func.count(WorkflowExecution.id),
            func.sum(
                func.cast(
                    WorkflowExecution.status == ExecutionStatus.COMPLETED,
                    Integer,
                )
            ),
            func.sum(
                func.cast(
                    WorkflowExecution.status == ExecutionStatus.FAILED,
                    Integer,
                )
            ),
            func.avg(WorkflowExecution.execution_time_ms),
        ).where(WorkflowExecution.tenant_id == tenant_id)

        exec_result = await self.session.execute(exec_query)
        exec_row = exec_result.one()

        return WorkflowStats(
            total_workflows=total_workflows,
            active_workflows=active_workflows,
            total_executions=exec_row[0] or 0,
            successful_executions=exec_row[1] or 0,
            failed_executions=exec_row[2] or 0,
            avg_execution_time_ms=float(exec_row[3] or 0),
        )

    async def get_execution_history(
        self,
        workflow_id: UUID,
        limit: int = 50,
    ) -> list[ExecutionSummary]:
        """Retorna historico de execucoes.

        Args:
            workflow_id: ID do workflow.
            limit: Limite.

        Returns:
            Lista de resumos.
        """
        query = (
            select(WorkflowExecution)
            .where(WorkflowExecution.workflow_id == workflow_id)
            .order_by(WorkflowExecution.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        executions = list(result.scalars().all())

        return [
            ExecutionSummary(
                execution_id=ex.id,
                workflow_name=ex.workflow.name if ex.workflow else "Unknown",
                status=ex.status,
                steps_executed=ex.steps_executed,
                duration_ms=ex.execution_time_ms,
                error_message=ex.error_message,
                started_at=ex.started_at,
                completed_at=ex.completed_at,
            )
            for ex in executions
        ]

    async def get_execution_logs(
        self,
        execution_id: UUID,
        limit: int = 100,
    ) -> list[WorkflowLog]:
        """Retorna logs de execucao.

        Args:
            execution_id: ID da execucao.
            limit: Limite.

        Returns:
            Lista de logs.
        """
        query = (
            select(WorkflowLog)
            .where(WorkflowLog.execution_id == execution_id)
            .order_by(WorkflowLog.created_at)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ==================== Templates ====================

    async def get_templates(
        self,
        tenant_id: UUID,
        category: Optional[WorkflowCategory] = None,
    ) -> list[Workflow]:
        """Retorna templates de workflow.

        Args:
            tenant_id: ID do tenant.
            category: Filtro por categoria.

        Returns:
            Lista de templates.
        """
        query = select(Workflow).where(
            and_(
                Workflow.tenant_id == tenant_id,
                Workflow.is_template.is_(True),
            )
        )

        if category:
            query = query.where(Workflow.category == category)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_from_template(
        self,
        template: Workflow,
        new_name: str,
        new_slug: str,
    ) -> Workflow:
        """Cria workflow a partir de template.

        Args:
            template: Template.
            new_name: Nome do novo.
            new_slug: Slug do novo.

        Returns:
            Novo workflow.
        """
        return await self.clone_workflow(template, new_name, new_slug)
