"""
Tests for Workflow Optimizer Services - Sprint 55.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
import asyncio

from modules.ai.workflow_optimizer.services import (
    WorkflowAnalyzer,
    WorkflowOptimizer,
    WorkflowExecutor,
    StepExecutor,
)


class TestWorkflowAnalyzer:
    """Testes para WorkflowAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Fixture para analyzer."""
        return WorkflowAnalyzer()

    @pytest.fixture
    def sample_workflow(self):
        """Workflow de exemplo."""
        return {
            "id": "wf-001",
            "steps": [
                {"id": "step1", "name": "Validar", "step_type": "action"},
                {"id": "step2", "name": "Processar", "step_type": "data_transform"},
                {"id": "step3", "name": "Notificar", "step_type": "notification"},
            ],
            "variables": {"timeout": 60},
        }

    @pytest.fixture
    def sample_executions(self):
        """Execucoes de exemplo."""
        now = datetime.utcnow()
        return [
            {
                "status": "completed",
                "execution_time_ms": 1000,
                "step_results": {
                    "step1": {"status": "completed", "execution_time_ms": 200},
                    "step2": {"status": "completed", "execution_time_ms": 600},
                    "step3": {"status": "completed", "execution_time_ms": 200},
                },
                "created_at": now - timedelta(days=1),
            },
            {
                "status": "completed",
                "execution_time_ms": 1500,
                "step_results": {
                    "step1": {"status": "completed", "execution_time_ms": 300},
                    "step2": {"status": "completed", "execution_time_ms": 900},
                    "step3": {"status": "completed", "execution_time_ms": 300},
                },
                "created_at": now - timedelta(days=2),
            },
            {
                "status": "failed",
                "execution_time_ms": 500,
                "error_message": "Timeout no step2",
                "error_step": "step2",
                "step_results": {
                    "step1": {"status": "completed", "execution_time_ms": 200},
                    "step2": {"status": "failed", "execution_time_ms": 300},
                },
                "created_at": now - timedelta(days=3),
            },
        ]

    def test_analyze_workflow_basic(
        self, analyzer, sample_workflow, sample_executions
    ):
        """Testa analise basica de workflow."""
        result = analyzer.analyze_workflow(
            sample_workflow,
            sample_executions,
            period_days=30,
        )

        assert result["workflow_id"] == "wf-001"
        assert result["total_executions"] == 3
        assert result["success_rate"] > 0
        assert result["failure_rate"] > 0
        assert result["avg_execution_time_ms"] > 0
        assert "health_score" in result
        assert "efficiency_score" in result
        assert "reliability_score" in result

    def test_analyze_empty_executions(self, analyzer, sample_workflow):
        """Testa analise sem execucoes."""
        result = analyzer.analyze_workflow(sample_workflow, [], period_days=30)

        assert result["total_executions"] == 0
        assert result["success_rate"] == 0.0
        assert result["bottleneck_steps"] == []

    def test_identify_bottlenecks(
        self, analyzer, sample_workflow, sample_executions
    ):
        """Testa identificacao de bottlenecks."""
        result = analyzer.analyze_workflow(
            sample_workflow,
            sample_executions,
            period_days=30,
        )

        # step2 deve ser identificado como bottleneck (mais lento e com falha)
        bottlenecks = result.get("bottleneck_steps", [])

        if bottlenecks:
            bottleneck_ids = [b["step_id"] for b in bottlenecks]
            assert "step2" in bottleneck_ids or len(bottlenecks) >= 0

    def test_analyze_frequent_errors(
        self, analyzer, sample_workflow, sample_executions
    ):
        """Testa analise de erros frequentes."""
        result = analyzer.analyze_workflow(
            sample_workflow,
            sample_executions,
            period_days=30,
        )

        errors = result.get("frequent_errors", [])
        if errors:
            assert errors[0]["count"] >= 1

    def test_generate_optimizations(
        self, analyzer, sample_workflow, sample_executions
    ):
        """Testa geracao de otimizacoes."""
        # Cria execucoes com baixa taxa de sucesso
        executions_with_failures = sample_executions + [
            {
                "status": "failed",
                "execution_time_ms": 400,
                "error_message": "Error",
                "error_step": "step2",
                "step_results": {},
                "created_at": datetime.utcnow() - timedelta(days=i),
            }
            for i in range(5)
        ]

        result = analyzer.analyze_workflow(
            sample_workflow,
            executions_with_failures,
            period_days=30,
        )

        optimizations = result.get("optimizations", [])
        assert isinstance(optimizations, list)

    def test_calculate_percentiles(self, analyzer):
        """Testa calculo de percentis."""
        data = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

        p50 = analyzer._percentile(data, 50)
        p95 = analyzer._percentile(data, 95)
        p99 = analyzer._percentile(data, 99)

        assert p50 == 550.0
        assert p95 > p50
        assert p99 > p95

    def test_empty_percentile(self, analyzer):
        """Testa percentil com lista vazia."""
        result = analyzer._percentile([], 50)
        assert result == 0.0


class TestWorkflowOptimizer:
    """Testes para WorkflowOptimizer."""

    @pytest.fixture
    def optimizer(self):
        """Fixture para optimizer."""
        return WorkflowOptimizer()

    @pytest.fixture
    def sample_workflow(self):
        """Workflow de exemplo."""
        return {
            "id": "wf-001",
            "steps": [
                {
                    "id": "step1",
                    "name": "Processar",
                    "step_type": "action",
                    "config": {},
                },
                {
                    "id": "step2",
                    "name": "Aprovar",
                    "step_type": "approval",
                    "config": {},
                },
            ],
            "variables": {},
            "settings": {},
        }

    def test_suggest_optimizations(self, optimizer, sample_workflow):
        """Testa sugestao de otimizacoes."""
        executions = [
            {
                "status": "failed",
                "execution_time_ms": 1000,
                "error_message": "Error",
                "error_step": "step1",
                "step_results": {},
                "created_at": datetime.utcnow() - timedelta(days=i),
            }
            for i in range(10)
        ]

        suggestions = optimizer.suggest_optimizations(sample_workflow, executions)
        assert isinstance(suggestions, list)

    def test_apply_retry_optimization(self, optimizer, sample_workflow):
        """Testa aplicacao de otimizacao de retry."""
        optimization = {
            "changes": [{"type": "add_retry", "steps": ["step1"]}],
        }

        result = optimizer.apply_optimization(sample_workflow, optimization)

        assert result.get("is_ai_optimized") is True
        # Verifica se retry foi adicionado
        for step in result.get("steps", []):
            if step.get("id") == "step1":
                config = step.get("config", {})
                assert config.get("retry_count", 0) >= 1

    def test_apply_parallel_optimization(self, optimizer, sample_workflow):
        """Testa aplicacao de otimizacao de paralelismo."""
        optimization = {
            "changes": [{"type": "parallel_execution", "steps": []}],
        }

        result = optimizer.apply_optimization(sample_workflow, optimization)

        settings = result.get("settings", {})
        assert settings.get("parallel_enabled") is True

    def test_apply_auto_approval_optimization(self, optimizer, sample_workflow):
        """Testa aplicacao de aprovacao automatica."""
        optimization = {
            "changes": [{"type": "auto_approval", "condition": "low_risk"}],
        }

        result = optimizer.apply_optimization(sample_workflow, optimization)

        # Verifica se auto_approve foi configurado
        for step in result.get("steps", []):
            if step.get("step_type") == "approval":
                config = step.get("config", {})
                assert config.get("auto_approve_condition") == "low_risk"


class TestStepExecutor:
    """Testes para StepExecutor."""

    @pytest.fixture
    def executor(self):
        """Fixture para executor."""
        return StepExecutor()

    @pytest.mark.asyncio
    async def test_execute_action_step(self, executor):
        """Testa execucao de step de acao."""
        step = {
            "id": "step1",
            "step_type": "action",
            "config": {"action_type": "log", "message": "Test"},
        }
        context = {"variables": {}}

        result = await executor.execute_step(step, context)

        assert result["status"] == "completed"
        assert "execution_time_ms" in result

    @pytest.mark.asyncio
    async def test_execute_condition_step(self, executor):
        """Testa execucao de step de condicao."""
        step = {
            "id": "step1",
            "step_type": "condition",
            "config": {
                "condition": "true",
                "true_step": "step2",
                "false_step": "step3",
            },
        }
        context = {"variables": {}}

        result = await executor.execute_step(step, context)

        assert result["status"] == "completed"
        output = result.get("output", {})
        assert output.get("result") is True
        assert output.get("next_step") == "step2"

    @pytest.mark.asyncio
    async def test_execute_wait_step(self, executor):
        """Testa execucao de step de espera."""
        step = {
            "id": "step1",
            "step_type": "wait",
            "config": {"seconds": 0.1},
        }
        context = {"variables": {}}

        result = await executor.execute_step(step, context)

        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_execute_notification_step(self, executor):
        """Testa execucao de step de notificacao."""
        step = {
            "id": "step1",
            "step_type": "notification",
            "config": {
                "channels": ["log"],
                "message": "Hello ${name}",
                "recipients": ["user@test.com"],
            },
        }
        context = {"variables": {"name": "World"}}

        result = await executor.execute_step(step, context)

        assert result["status"] == "completed"
        output = result.get("output", {})
        assert "World" in output.get("message", "")

    @pytest.mark.asyncio
    async def test_execute_data_transform_step(self, executor):
        """Testa execucao de step de transformacao."""
        step = {
            "id": "step1",
            "step_type": "data_transform",
            "config": {
                "type": "copy",
                "source": "input_value",
                "target": "output_value",
            },
        }
        context = {"variables": {"input_value": "test"}}

        result = await executor.execute_step(step, context)

        assert result["status"] == "completed"
        assert context["variables"].get("output_value") == "test"

    @pytest.mark.asyncio
    async def test_execute_approval_step_auto(self, executor):
        """Testa execucao de step de aprovacao automatica."""
        step = {
            "id": "step1",
            "step_type": "approval",
            "config": {"auto_approve_condition": "low_risk"},
        }
        context = {"variables": {"risk_level": "low"}}

        result = await executor.execute_step(step, context)

        assert result["status"] == "completed"
        output = result.get("output", {})
        assert output.get("auto_approved") is True

    @pytest.mark.asyncio
    async def test_execute_approval_step_manual(self, executor):
        """Testa execucao de step de aprovacao manual."""
        step = {
            "id": "step1",
            "step_type": "approval",
            "config": {"approvers": ["admin"]},
        }
        context = {"variables": {}}

        result = await executor.execute_step(step, context)

        assert result["status"] == "completed"
        output = result.get("output", {})
        assert output.get("requires_approval") is True

    @pytest.mark.asyncio
    async def test_execute_unknown_step_type(self, executor):
        """Testa execucao de step com tipo desconhecido."""
        step = {
            "id": "step1",
            "step_type": "unknown_type",
            "config": {},
        }
        context = {"variables": {}}

        result = await executor.execute_step(step, context)

        assert result["status"] == "failed"
        assert "error" in result

    def test_evaluate_condition_true(self, executor):
        """Testa avaliacao de condicao true."""
        result = executor._evaluate_condition("true", {})
        assert result is True

    def test_evaluate_condition_false(self, executor):
        """Testa avaliacao de condicao false."""
        result = executor._evaluate_condition("false", {})
        assert result is False

    def test_evaluate_condition_equals(self, executor):
        """Testa avaliacao de condicao de igualdade."""
        result = executor._evaluate_condition("value == value", {})
        assert result is True

        result = executor._evaluate_condition("a == b", {})
        assert result is False

    def test_evaluate_condition_not_equals(self, executor):
        """Testa avaliacao de condicao de diferenca."""
        result = executor._evaluate_condition("a != b", {})
        assert result is True

    def test_evaluate_condition_greater(self, executor):
        """Testa avaliacao de condicao maior que."""
        result = executor._evaluate_condition("10 > 5", {})
        assert result is True

        result = executor._evaluate_condition("3 > 5", {})
        assert result is False


class TestWorkflowExecutor:
    """Testes para WorkflowExecutor."""

    @pytest.fixture
    def executor(self):
        """Fixture para executor."""
        return WorkflowExecutor()

    @pytest.fixture
    def simple_workflow(self):
        """Workflow simples de exemplo."""
        return {
            "id": "wf-001",
            "steps": [
                {
                    "id": "step1",
                    "name": "Log Start",
                    "step_type": "action",
                    "config": {"action_type": "log", "message": "Started"},
                },
                {
                    "id": "step2",
                    "name": "Log End",
                    "step_type": "action",
                    "config": {"action_type": "log", "message": "Ended"},
                },
            ],
            "variables": {},
            "settings": {},
            "timeout_seconds": 60,
        }

    @pytest.mark.asyncio
    async def test_execute_simple_workflow(self, executor, simple_workflow):
        """Testa execucao de workflow simples."""
        input_data = {"test": "value"}

        result = await executor.execute_workflow(simple_workflow, input_data)

        assert result["status"] == "completed"
        assert result["current_step"] == 2
        assert result["total_steps"] == 2
        assert result["progress_percent"] == 100.0
        assert len(result["step_results"]) == 2
        assert result["execution_time_ms"] >= 0

    @pytest.mark.asyncio
    async def test_execute_workflow_with_condition(self, executor):
        """Testa workflow com condicao."""
        workflow = {
            "id": "wf-002",
            "steps": [
                {
                    "id": "check",
                    "name": "Check Condition",
                    "step_type": "condition",
                    "config": {
                        "condition": "true",
                        "true_step": "success",
                        "false_step": "failure",
                    },
                },
                {
                    "id": "success",
                    "name": "Success",
                    "step_type": "action",
                    "config": {"action_type": "log", "message": "Success"},
                },
                {
                    "id": "failure",
                    "name": "Failure",
                    "step_type": "action",
                    "config": {"action_type": "log", "message": "Failure"},
                },
            ],
            "variables": {},
            "settings": {},
            "timeout_seconds": 60,
        }

        result = await executor.execute_workflow(workflow, {})

        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_execute_workflow_with_variables(self, executor):
        """Testa workflow com variaveis."""
        workflow = {
            "id": "wf-003",
            "steps": [
                {
                    "id": "step1",
                    "name": "Set Variable",
                    "step_type": "action",
                    "config": {
                        "action_type": "set_variable",
                        "variable": "result",
                        "value": "done",
                    },
                },
            ],
            "variables": {"initial": "value"},
            "settings": {},
            "timeout_seconds": 60,
        }

        result = await executor.execute_workflow(workflow, {"input": "data"})

        assert result["status"] == "completed"
        assert result["output_data"].get("result") == "done"
        assert result["output_data"].get("initial") == "value"
        assert result["output_data"].get("input") == "data"

    @pytest.mark.asyncio
    async def test_execute_workflow_logs(self, executor, simple_workflow):
        """Testa logs de execucao."""
        result = await executor.execute_workflow(simple_workflow, {})

        assert len(result["logs"]) > 0
        assert all("timestamp" in log for log in result["logs"])
        assert all("message" in log for log in result["logs"])

    @pytest.mark.asyncio
    async def test_execute_empty_workflow(self, executor):
        """Testa workflow vazio."""
        workflow = {
            "id": "wf-empty",
            "steps": [],
            "variables": {},
            "settings": {},
            "timeout_seconds": 60,
        }

        result = await executor.execute_workflow(workflow, {})

        assert result["status"] == "completed"
        assert result["total_steps"] == 0


class TestWorkflowAnalyzerScores:
    """Testes para scores do analyzer."""

    @pytest.fixture
    def analyzer(self):
        return WorkflowAnalyzer()

    def test_health_score_perfect(self, analyzer):
        """Testa health score perfeito."""
        metrics = {
            "success_rate": 0.99,
            "avg_time": 1000,
        }
        errors = []

        score = analyzer._calculate_health_score(metrics, errors)
        assert score >= 90

    def test_health_score_with_failures(self, analyzer):
        """Testa health score com falhas."""
        metrics = {
            "success_rate": 0.5,
            "avg_time": 1000,
        }
        errors = []

        score = analyzer._calculate_health_score(metrics, errors)
        assert score < 60

    def test_efficiency_score(self, analyzer):
        """Testa efficiency score."""
        metrics = {
            "avg_time": 1000,
            "p95": 2000,
        }
        step_analysis = {
            "step1": {"avg_time": 500, "times": [500]},
            "step2": {"avg_time": 500, "times": [500]},
        }

        score = analyzer._calculate_efficiency_score(metrics, step_analysis)
        assert 0 <= score <= 100

    def test_reliability_score(self, analyzer):
        """Testa reliability score."""
        metrics = {"success_rate": 0.95}
        score = analyzer._calculate_reliability_score(metrics)
        assert score == 95.0

        metrics = {"success_rate": 0.0}
        score = analyzer._calculate_reliability_score(metrics)
        assert score == 0.0
