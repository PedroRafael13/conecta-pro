"""
Testes dos Models do Workflow Engine.

Testes para Workflow, Step, Trigger, Action, Condition, Execution.
"""

from datetime import datetime, timedelta

import pytest

from modules.workflows.models.action import (
    Action,
    ActionConfig,
    ActionResult,
    ActionStatus,
    ActionType,
    EmailConfig,
)
from modules.workflows.models.condition import (
    Condition,
    ConditionOperator,
    ConditionType,
    SimpleCondition,
)
from modules.workflows.models.execution import (
    ExecutionLog,
    ExecutionStatus,
    LogLevel,
    StepExecution,
    WorkflowExecution,
)
from modules.workflows.models.trigger import (
    ScheduleConfig,
    ScheduleFrequency,
    Trigger,
    TriggerEvent,
    TriggerType,
    WebhookConfig,
)
from modules.workflows.models.workflow import (
    Workflow,
    WorkflowCategory,
    WorkflowPriority,
    WorkflowStatus,
    WorkflowVariable,
)
from modules.workflows.models.workflow_step import (
    StepConnection,
    StepPosition,
    StepType,
    WorkflowStep,
)


class TestWorkflow:
    """Testes do modelo Workflow."""

    def test_criar_workflow(self):
        """Testa criacao de workflow."""
        workflow = Workflow(
            tenant_id="tenant1",
            name="Meu Workflow",
            description="Descricao do workflow",
            category=WorkflowCategory.FINANCIAL,
        )

        assert workflow.id is not None
        assert workflow.name == "Meu Workflow"
        assert workflow.category == WorkflowCategory.FINANCIAL
        assert workflow.status == WorkflowStatus.DRAFT
        assert workflow.is_enabled is True

    def test_workflow_can_execute(self):
        """Testa verificacao de execucao."""
        workflow = Workflow(name="Test")

        # Draft nao pode executar
        assert workflow.can_execute is False

        # Ativar
        workflow.step_ids = ["step1"]
        workflow.activate()
        assert workflow.status == WorkflowStatus.ACTIVE
        assert workflow.can_execute is True

        # Run once ja executou
        workflow.run_once = True
        workflow.execution_count = 1
        assert workflow.can_execute is False

    def test_workflow_variables(self):
        """Testa variaveis do workflow."""
        workflow = Workflow(name="Test")

        var = WorkflowVariable(
            name="quantidade",
            var_type="number",
            default_value=10,
        )
        workflow.add_variable(var)

        assert len(workflow.variables) == 1
        assert workflow.get_variable("quantidade").default_value == 10
        assert workflow.get_variable("inexistente") is None

    def test_workflow_tags(self):
        """Testa tags do workflow."""
        workflow = Workflow(name="Test")

        workflow.add_tag("Urgente")
        workflow.add_tag("Financeiro")
        workflow.add_tag("urgente")  # Duplicata

        assert len(workflow.tags) == 2
        assert "urgente" in workflow.tags

        workflow.remove_tag("financeiro")
        assert len(workflow.tags) == 1

    def test_workflow_statistics(self):
        """Testa estatisticas do workflow."""
        workflow = Workflow(name="Test")

        workflow.update_statistics(True, 100)
        workflow.update_statistics(True, 200)
        workflow.update_statistics(False, 50)

        assert workflow.execution_count == 3
        assert workflow.success_count == 2
        assert workflow.failure_count == 1
        assert workflow.success_rate == 2 / 3

    def test_workflow_clone(self):
        """Testa clonagem de workflow."""
        original = Workflow(
            name="Original",
            description="Descricao",
            category=WorkflowCategory.OPERATIONAL,
        )
        original.add_tag("test")

        cloned = original.clone("Copia", "tenant2")

        assert cloned.id != original.id
        assert cloned.name == "Copia"
        assert cloned.tenant_id == "tenant2"
        assert cloned.parent_workflow_id == original.id
        assert "test" in cloned.tags

    def test_workflow_to_dict(self):
        """Testa conversao para dicionario."""
        workflow = Workflow(
            name="Test",
            category=WorkflowCategory.COMMUNICATION,
        )

        data = workflow.to_dict()

        assert data["name"] == "Test"
        assert data["category"] == "communication"
        assert "statistics" in data


class TestWorkflowStep:
    """Testes do modelo WorkflowStep."""

    def test_criar_step(self):
        """Testa criacao de step."""
        step = WorkflowStep(
            workflow_id="wf1",
            name="Enviar Email",
            step_type=StepType.ACTION,
            action_id="action1",
        )

        assert step.id is not None
        assert step.name == "Enviar Email"
        assert step.step_type == StepType.ACTION
        assert step.is_enabled is True

    def test_step_connections(self):
        """Testa conexoes entre steps."""
        step = WorkflowStep(name="Step 1")

        conn = step.add_connection(
            to_step_id="step2",
            condition="$.amount > 1000",
            label="Valor alto",
        )

        assert len(step.connections) == 1
        assert conn.to_step_id == "step2"
        assert "step2" in step.next_step_ids

        step.remove_connection("step2")
        assert len(step.connections) == 0

    def test_step_position(self):
        """Testa posicao no canvas."""
        step = WorkflowStep(name="Test")
        step.set_position(100, 200)

        assert step.position.x == 100
        assert step.position.y == 200

    def test_step_clone(self):
        """Testa clonagem de step."""
        original = WorkflowStep(
            name="Original",
            step_type=StepType.ACTION,
            action_id="act1",
        )

        cloned = original.clone("wf2")

        assert cloned.id != original.id
        assert cloned.workflow_id == "wf2"
        assert cloned.action_id == "act1"


class TestTrigger:
    """Testes do modelo Trigger."""

    def test_criar_trigger_evento(self):
        """Testa criacao de trigger de evento."""
        trigger = Trigger(
            workflow_id="wf1",
            name="Documento Uploaded",
            trigger_type=TriggerType.EVENT,
            event=TriggerEvent.DOCUMENT_UPLOADED,
        )

        assert trigger.trigger_type == TriggerType.EVENT
        assert trigger.event == TriggerEvent.DOCUMENT_UPLOADED
        assert trigger.is_enabled is True

    def test_criar_trigger_schedule(self):
        """Testa criacao de trigger agendado."""
        config = ScheduleConfig(
            frequency=ScheduleFrequency.DAILY,
            time_of_day=datetime.strptime("08:00", "%H:%M").time(),
        )

        trigger = Trigger(
            name="Relatorio Diario",
            trigger_type=TriggerType.SCHEDULE,
            schedule_config=config,
        )

        assert trigger.trigger_type == TriggerType.SCHEDULE
        assert trigger.schedule_config.frequency == ScheduleFrequency.DAILY

    def test_trigger_matches_event(self):
        """Testa match de evento."""
        trigger = Trigger(
            trigger_type=TriggerType.EVENT,
            event=TriggerEvent.PAYMENT_RECEIVED,
            filter_conditions={"amount": 100},
        )

        # Match exato
        assert (
            trigger.matches_event(
                "payment.received",
                {"amount": 100},
            )
            is True
        )

        # Evento diferente
        assert (
            trigger.matches_event(
                "payment.overdue",
                {"amount": 100},
            )
            is False
        )

        # Filtro nao corresponde
        assert (
            trigger.matches_event(
                "payment.received",
                {"amount": 50},
            )
            is False
        )

    def test_trigger_cooldown(self):
        """Testa cooldown do trigger."""
        trigger = Trigger(
            name="Test",
            trigger_type=TriggerType.EVENT,
            cooldown_seconds=60,
        )

        assert trigger.can_trigger is True

        trigger.record_trigger()
        assert trigger.trigger_count == 1

        # Com cooldown ativo
        assert trigger.can_trigger is False


class TestAction:
    """Testes do modelo Action."""

    def test_criar_action(self):
        """Testa criacao de action."""
        action = Action(
            name="Enviar Email",
            action_type=ActionType.SEND_EMAIL,
            email_config=EmailConfig(
                to=["user@example.com"],
                subject="Assunto",
                body="Corpo do email",
            ),
        )

        assert action.action_type == ActionType.SEND_EMAIL
        assert action.email_config is not None
        assert "user@example.com" in action.email_config.to

    def test_action_validate(self):
        """Testa validacao de action."""
        # Action sem configuracao
        action = Action(
            name="",
            action_type=ActionType.SEND_EMAIL,
        )

        errors = action.validate()
        assert len(errors) > 0
        assert any("Nome" in e for e in errors)

    def test_action_statistics(self):
        """Testa estatisticas de action."""
        action = Action(name="Test")

        action.update_statistics(True, 100)
        action.update_statistics(False, 50)

        assert action.execution_count == 2
        assert action.success_count == 1
        assert action.success_rate == 0.5


class TestCondition:
    """Testes do modelo Condition."""

    def test_simple_condition_equals(self):
        """Testa condicao simples de igualdade."""
        condition = SimpleCondition(
            field="status",
            operator=ConditionOperator.EQUALS,
            value="active",
        )

        context = {"status": "active"}
        assert condition.evaluate(context) is True

        context = {"status": "inactive"}
        assert condition.evaluate(context) is False

    def test_simple_condition_greater_than(self):
        """Testa condicao de maior que."""
        condition = SimpleCondition(
            field="amount",
            operator=ConditionOperator.GREATER_THAN,
            value=100,
        )

        assert condition.evaluate({"amount": 150}) is True
        assert condition.evaluate({"amount": 50}) is False

    def test_simple_condition_contains(self):
        """Testa condicao contains."""
        condition = SimpleCondition(
            field="message",
            operator=ConditionOperator.CONTAINS,
            value="urgente",
        )

        assert condition.evaluate({"message": "Isso e urgente!"}) is True
        assert condition.evaluate({"message": "Normal"}) is False

    def test_simple_condition_is_null(self):
        """Testa condicao de nulidade."""
        condition = SimpleCondition(
            field="optional_field",
            operator=ConditionOperator.IS_NULL,
        )

        assert condition.evaluate({"optional_field": None}) is True
        assert condition.evaluate({"other": "value"}) is True
        assert condition.evaluate({"optional_field": "value"}) is False

    def test_condition_nested_field(self):
        """Testa acesso a campo aninhado."""
        condition = SimpleCondition(
            field="$.user.role",
            operator=ConditionOperator.EQUALS,
            value="admin",
        )

        context = {"user": {"role": "admin"}}
        assert condition.evaluate(context) is True


class TestExecution:
    """Testes do modelo Execution."""

    def test_criar_execution(self):
        """Testa criacao de execution."""
        execution = WorkflowExecution(
            workflow_id="wf1",
            workflow_name="Meu Workflow",
            input_data={"key": "value"},
        )

        assert execution.id is not None
        assert execution.status == ExecutionStatus.PENDING
        assert execution.success is False

    def test_execution_lifecycle(self):
        """Testa ciclo de vida da execution."""
        execution = WorkflowExecution(
            workflow_id="wf1",
            steps_total=5,
        )

        # Iniciar
        execution.start()
        assert execution.status == ExecutionStatus.RUNNING
        assert execution.started_at is not None

        # Completar
        execution.complete({"result": "ok"})
        assert execution.status == ExecutionStatus.COMPLETED
        assert execution.success is True
        assert execution.output_data["result"] == "ok"

    def test_execution_failure(self):
        """Testa falha na execution."""
        execution = WorkflowExecution(workflow_id="wf1")
        execution.start()

        execution.fail("Erro no step", "step123")

        assert execution.status == ExecutionStatus.FAILED
        assert execution.success is False
        assert execution.error == "Erro no step"
        assert execution.error_step_id == "step123"

    def test_execution_variables(self):
        """Testa variaveis da execution."""
        execution = WorkflowExecution(workflow_id="wf1")

        execution.set_variable("count", 10)
        assert execution.get_variable("count") == 10
        assert execution.get_variable("undefined", 0) == 0

    def test_execution_progress(self):
        """Testa progresso da execution."""
        execution = WorkflowExecution(
            workflow_id="wf1",
            steps_total=10,
            steps_completed=3,
        )

        assert execution.progress_percent == 30.0

    def test_step_execution(self):
        """Testa execution de step."""
        step_exec = StepExecution(
            execution_id="exec1",
            step_id="step1",
            step_name="Meu Step",
        )

        step_exec.start()
        assert step_exec.status == ExecutionStatus.RUNNING

        step_exec.complete({"output": "data"})
        assert step_exec.status == ExecutionStatus.COMPLETED
        assert step_exec.success is True

    def test_execution_logs(self):
        """Testa logs da execution."""
        execution = WorkflowExecution(workflow_id="wf1")

        log = execution.add_log(
            "Processando dados",
            LogLevel.INFO,
            {"count": 100},
        )

        assert len(execution.logs) == 1
        assert log.message == "Processando dados"
        assert log.level == LogLevel.INFO
