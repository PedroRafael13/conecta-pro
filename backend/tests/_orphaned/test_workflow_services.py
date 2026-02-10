"""
Testes dos Services do Workflow Engine.

Testes para ConditionEvaluator, ActionExecutor, WorkflowDesigner.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from modules.workflows.models.action import (
    Action,
    ActionType,
    EmailConfig,
    HTTPConfig,
)
from modules.workflows.models.condition import (
    Condition,
    ConditionGroup,
    ConditionOperator,
    ConditionType,
    LogicalOperator,
    SimpleCondition,
)
from modules.workflows.models.trigger import (
    ScheduleConfig,
    ScheduleFrequency,
    Trigger,
    TriggerType,
)
from modules.workflows.models.workflow import Workflow, WorkflowCategory
from modules.workflows.models.workflow_step import StepType, WorkflowStep
from modules.workflows.services.action_executor import ActionExecutor
from modules.workflows.services.condition_evaluator import ConditionEvaluator
from modules.workflows.services.workflow_designer import WorkflowDesigner


class TestConditionEvaluator:
    """Testes do avaliador de condicoes."""

    @pytest.fixture
    def evaluator(self):
        """Cria instancia do evaluator."""
        return ConditionEvaluator()

    def test_evaluate_simple_equals(self, evaluator):
        """Testa avaliacao de igualdade."""
        condition = Condition(
            condition_type=ConditionType.SIMPLE,
            simple_condition=SimpleCondition(
                field="status",
                operator=ConditionOperator.EQUALS,
                value="active",
            ),
        )

        assert evaluator.evaluate(condition, {"status": "active"}) is True
        assert evaluator.evaluate(condition, {"status": "inactive"}) is False

    def test_evaluate_expression(self, evaluator):
        """Testa avaliacao de expressao."""
        condition = Condition(
            condition_type=ConditionType.EXPRESSION,
            expression="amount > 1000",
        )

        context = {"amount": 1500}
        assert evaluator.evaluate(condition, context) is True

        context = {"amount": 500}
        assert evaluator.evaluate(condition, context) is False

    def test_evaluate_function_business_hours(self, evaluator):
        """Testa funcao de horario comercial."""
        condition = Condition(
            condition_type=ConditionType.FUNCTION,
            function_name="is_business_hours",
            function_params={"start_hour": 9, "end_hour": 18},
        )

        # O resultado depende do horario atual
        result = evaluator.evaluate(condition, {})
        assert isinstance(result, bool)

    def test_evaluate_compound_and(self, evaluator):
        """Testa grupo AND de condicoes."""
        group = ConditionGroup(
            operator=LogicalOperator.AND,
            conditions=[
                SimpleCondition(
                    field="status",
                    operator=ConditionOperator.EQUALS,
                    value="active",
                ),
                SimpleCondition(
                    field="amount",
                    operator=ConditionOperator.GREATER_THAN,
                    value=100,
                ),
            ],
        )

        condition = Condition(
            condition_type=ConditionType.COMPOUND,
            condition_group=group,
        )

        # Ambas verdadeiras
        assert evaluator.evaluate(condition, {"status": "active", "amount": 200}) is True

        # Uma falsa
        assert evaluator.evaluate(condition, {"status": "active", "amount": 50}) is False

    def test_evaluate_compound_or(self, evaluator):
        """Testa grupo OR de condicoes."""
        group = ConditionGroup(
            operator=LogicalOperator.OR,
            conditions=[
                SimpleCondition(
                    field="role",
                    operator=ConditionOperator.EQUALS,
                    value="admin",
                ),
                SimpleCondition(
                    field="role",
                    operator=ConditionOperator.EQUALS,
                    value="manager",
                ),
            ],
        )

        condition = Condition(
            condition_type=ConditionType.COMPOUND,
            condition_group=group,
        )

        assert evaluator.evaluate(condition, {"role": "admin"}) is True
        assert evaluator.evaluate(condition, {"role": "manager"}) is True
        assert evaluator.evaluate(condition, {"role": "user"}) is False

    def test_get_next_step(self, evaluator):
        """Testa obtencao de proximo step."""
        condition = Condition(
            condition_type=ConditionType.SIMPLE,
            simple_condition=SimpleCondition(
                field="approved",
                operator=ConditionOperator.EQUALS,
                value=True,
            ),
            true_step_id="step_approved",
            false_step_id="step_rejected",
        )

        assert evaluator.get_next_step(condition, {"approved": True}) == "step_approved"
        assert evaluator.get_next_step(condition, {"approved": False}) == "step_rejected"


class TestActionExecutor:
    """Testes do executor de acoes."""

    @pytest.fixture
    def executor(self):
        """Cria instancia do executor."""
        return ActionExecutor()

    @pytest.mark.asyncio
    async def test_execute_log_message(self, executor):
        """Testa action de log."""
        action = Action(
            name="Log",
            action_type=ActionType.CREATE_SCALE,
            message_template="Processando {{item_id}}",
        )

        result = await executor.execute(action, {"item_id": "123"})

        assert result.success is True
        assert result.output["message"] == "Processando 123"

    @pytest.mark.asyncio
    async def test_execute_set_variable(self, executor):
        """Testa action de set variable."""
        action = Action(
            name="Set Var",
            action_type=ActionType.CREATE_SCALE,
            input_mapping={
                "total": "{{amount * 1.1}}",
            },
        )

        result = await executor.execute(action, {"amount": 100})
        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_invalid_action(self, executor):
        """Testa action invalida."""
        action = Action(
            name="",  # Nome vazio
            action_type=ActionType.CREATE_SCALE,
            # Sem email_config
        )

        result = await executor.execute(action, {})

        assert result.success is False
        assert "Nome" in result.error or "email" in result.error.lower()


class TestWorkflowDesigner:
    """Testes do designer de workflows."""

    @pytest.fixture
    def designer(self):
        """Cria instancia do designer."""
        return WorkflowDesigner()

    def test_create_workflow(self, designer):
        """Testa criacao de workflow."""
        workflow = designer.create_workflow(
            name="Novo Workflow",
            description="Descricao",
            category=WorkflowCategory.CRM,
            tenant_id="tenant1",
        )

        assert workflow.id is not None
        assert workflow.name == "Novo Workflow"
        assert len(workflow.step_ids) == 2  # START e END

    def test_add_step(self, designer):
        """Testa adicao de step."""
        workflow = designer.create_workflow("Test")
        initial_count = len(workflow.step_ids)

        step = designer.add_step(
            workflow=workflow,
            name="Novo Step",
            step_type=StepType.TEXT_INPUT,
        )

        assert step.id is not None
        assert len(workflow.step_ids) == initial_count + 1

    def test_remove_step(self, designer):
        """Testa remocao de step."""
        workflow = designer.create_workflow("Test")

        step = designer.add_step(
            workflow=workflow,
            name="Step Removivel",
            step_type=StepType.TEXT_INPUT,
        )

        # Pode remover step de action
        assert designer.remove_step(workflow.id, step.id) is True

        # Nao pode remover START
        start_id = workflow.step_ids[0]
        assert designer.remove_step(workflow.id, start_id) is False

    def test_connect_steps(self, designer):
        """Testa conexao entre steps."""
        workflow = designer.create_workflow("Test")

        step1 = designer.add_step(workflow, "Step 1", StepType.TEXT_INPUT)
        step2 = designer.add_step(workflow, "Step 2", StepType.TEXT_INPUT)

        connection = designer.connect_steps(
            workflow.id,
            step1.id,
            step2.id,
            label="Proximo",
        )

        assert connection is not None
        assert step2.id in step1.next_step_ids

    def test_validate_workflow(self, designer):
        """Testa validacao de workflow."""
        workflow = designer.create_workflow("Test")

        # Workflow inicial e valido (tem START, END e conexao)
        errors = designer.validate_workflow(workflow)
        assert len(errors) == 0

    def test_export_import_workflow(self, designer):
        """Testa exportacao e importacao."""
        workflow = designer.create_workflow("Original")
        designer.add_step(workflow, "Action Step", StepType.TEXT_INPUT)

        # Exportar
        data = designer.export_workflow(workflow)
        assert "workflow" in data
        assert "steps" in data

        # Importar
        imported = designer.import_workflow(
            data,
            tenant_id="new_tenant",
            new_name="Importado",
        )

        assert imported.id != workflow.id
        assert imported.name == "Importado"
        assert imported.tenant_id == "new_tenant"

    def test_auto_layout(self, designer):
        """Testa layout automatico."""
        workflow = designer.create_workflow("Test")

        # Adiciona alguns steps
        designer.add_step(workflow, "Step 1", StepType.TEXT_INPUT)
        designer.add_step(workflow, "Step 2", StepType.TEXT_INPUT)

        layout = designer.auto_layout(workflow)

        assert len(layout.nodes) >= 2

    def test_add_action_step(self, designer):
        """Testa adicao de step de action."""
        workflow = designer.create_workflow("Test")

        step, action = designer.add_action_step(
            workflow=workflow,
            action_type=ActionType.CREATE_SCALE,
            name="Enviar Notificacao",
        )

        assert step.step_type == StepType.TEXT_INPUT
        assert step.action_id == action.id
        assert action.action_type == ActionType.CREATE_SCALE

    def test_add_condition_step(self, designer):
        """Testa adicao de step de condicao."""
        workflow = designer.create_workflow("Test")

        step, condition = designer.add_condition_step(
            workflow=workflow,
            expression="amount > 1000",
            name="Valor Alto?",
        )

        assert step.step_type == StepType.TEXT_INPUT
        assert step.condition_id == condition.id
        assert condition.expression == "amount > 1000"

    def test_add_trigger(self, designer):
        """Testa adicao de trigger."""
        workflow = designer.create_workflow("Test")

        trigger = designer.add_trigger(
            workflow=workflow,
            trigger_type=TriggerType.EVENT,
            name="Documento Criado",
            config={"event": "document.uploaded"},
        )

        assert trigger.id in workflow.trigger_ids
        assert trigger.trigger_type == TriggerType.EVENT


class TestTriggerService:
    """Testes do servico de triggers."""

    @pytest.fixture
    def trigger_service(self):
        """Cria instancia do trigger service."""
        from modules.workflows.services.trigger_service import TriggerService

        return TriggerService()

    @pytest.mark.asyncio
    async def test_register_trigger(self, trigger_service):
        """Testa registro de trigger."""
        workflow = Workflow(name="Test")
        trigger = Trigger(
            name="Test Trigger",
            trigger_type=TriggerType.MANUAL,
        )

        result = await trigger_service.register_trigger(trigger, workflow)

        assert result is True
        assert trigger_service.registry.get_trigger(trigger.id) is not None

    @pytest.mark.asyncio
    async def test_unregister_trigger(self, trigger_service):
        """Testa remocao de trigger."""
        workflow = Workflow(name="Test")
        trigger = Trigger(name="Test", trigger_type=TriggerType.MANUAL)

        await trigger_service.register_trigger(trigger, workflow)
        await trigger_service.unregister_trigger(trigger.id)

        assert trigger_service.registry.get_trigger(trigger.id) is None

    def test_get_next_run_time_daily(self, trigger_service):
        """Testa calculo de proxima execucao diaria."""
        trigger = Trigger(
            name="Daily",
            trigger_type=TriggerType.SCHEDULE,
            schedule_config=ScheduleConfig(
                frequency=ScheduleFrequency.DAILY,
            ),
        )

        next_run = trigger_service.get_next_run_time(trigger)

        assert next_run is not None
        assert next_run > datetime.utcnow()


class TestScheduler:
    """Testes do scheduler."""

    @pytest.fixture
    def scheduler(self):
        """Cria instancia do scheduler."""
        from modules.workflows.services.scheduler import WorkflowScheduler

        return WorkflowScheduler()

    def test_schedule_job(self, scheduler):
        """Testa agendamento de job."""
        workflow = Workflow(name="Test")
        trigger = Trigger(
            name="Test",
            trigger_type=TriggerType.SCHEDULE,
            schedule_config=ScheduleConfig(
                frequency=ScheduleFrequency.ONCE,
                run_at=datetime.utcnow(),
            ),
        )

        job_id = scheduler.schedule(
            trigger=trigger,
            workflow=workflow,
            run_at=datetime.utcnow(),
        )

        assert job_id is not None
        assert scheduler.get_job(job_id) is not None

    def test_cancel_job(self, scheduler):
        """Testa cancelamento de job."""
        workflow = Workflow(name="Test")
        trigger = Trigger(name="Test", trigger_type=TriggerType.SCHEDULE)
        trigger.schedule_config = ScheduleConfig(frequency=ScheduleFrequency.ONCE)

        job_id = scheduler.schedule(trigger, workflow, datetime.utcnow())

        assert scheduler.cancel_job(job_id) is True
        assert scheduler.get_job(job_id) is None

    def test_get_stats(self, scheduler):
        """Testa estatisticas."""
        stats = scheduler.get_stats()

        assert "pending_jobs" in stats
        assert "running" in stats
        assert "max_concurrent" in stats
