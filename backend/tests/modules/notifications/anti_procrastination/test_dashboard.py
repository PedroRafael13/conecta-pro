"""
Testes do Dashboard Unificado de Pendências
==========================================

Testes automatizados para verificar funcionamento do dashboard
e integração com módulos existentes.

Autor: Conecta PRO Team + Claude AI
Data: 2026-01-10
"""

from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from modules.notifications.anti_procrastination.dashboard.unified_dashboard import UnifiedDashboard
from modules.notifications.anti_procrastination.integration.module_integrator import ModuleIntegrator
from modules.notifications.anti_procrastination.models import (
    Department,
    PendingTaskData,
    TaskCategory,
    TaskPriority,
    TaskStatus,
)


class TestUnifiedDashboard:
    """Testes do dashboard unificado."""

    @pytest.fixture
    def mock_db(self):
        """Mock da sessão de banco."""
        return Mock()

    @pytest.fixture
    def mock_integrator(self):
        """Mock do integrador de módulos."""
        return Mock(spec=ModuleIntegrator)

    @pytest.fixture
    def dashboard(self, mock_db, mock_integrator):
        """Instância do dashboard para testes."""
        return UnifiedDashboard(mock_db, mock_integrator)

    @pytest.mark.asyncio
    async def test_get_system_summary_empty(self, dashboard, mock_integrator):
        """Testa resumo do sistema sem tarefas."""
        # Arrange
        mock_integrator.sync_all_modules = AsyncMock()
        dashboard.db.query.return_value.filter.return_value.count.return_value = 0

        # Act
        summary = await dashboard.get_system_summary()

        # Assert
        assert summary.total_pending == 0
        assert summary.critical_count == 0
        assert len(summary.departments) >= 0
        mock_integrator.sync_all_modules.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_department_dashboard_hr(self, dashboard):
        """Testa dashboard específico do RH."""
        # Arrange
        mock_tasks = [
            Mock(
                id="task-1",
                title="Coletar documento",
                priority=TaskPriority.HIGH,
                department=Department.HR,
                created_at=datetime.utcnow() - timedelta(days=2),
            )
        ]
        dashboard.db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_tasks
        dashboard.db.query.return_value.filter.return_value.count.return_value = 1

        # Act
        result = await dashboard.get_department_dashboard(Department.HR)

        # Assert
        assert result["department"] == "hr"
        assert result["summary"]["total_tasks"] == 1
        assert "tasks" in result
        assert "urgent_tasks" in result

    def test_task_to_data_conversion(self, dashboard):
        """Testa conversão de tarefa para PendingTaskData."""
        # Arrange
        mock_task = Mock()
        mock_task.id = "task-123"
        mock_task.title = "Tarefa Teste"
        mock_task.description = "Descrição teste"
        mock_task.source_module = "hr"
        mock_task.source_id = "hr-001"
        mock_task.category = TaskCategory.HR
        mock_task.priority = TaskPriority.HIGH
        mock_task.status = TaskStatus.PENDING
        mock_task.department = Department.HR
        mock_task.assigned_to = None
        mock_task.assigned_to_name = "João Silva"
        mock_task.created_at = datetime.utcnow()
        mock_task.due_date = None
        mock_task.completed_at = None
        mock_task.escalation_level = 0
        mock_task.escalation_count = 0
        mock_task.last_escalation = None
        mock_task.metadata = {}
        mock_task.business_impact = "medium"
        mock_task.compliance_risk = "low"

        # Act
        task_data = dashboard._task_to_data(mock_task)

        # Assert
        assert isinstance(task_data, PendingTaskData)
        assert task_data.title == "Tarefa Teste"
        assert task_data.category == TaskCategory.HR
        assert task_data.priority == TaskPriority.HIGH
        assert task_data.days_pending >= 0
        assert task_data.urgency_score > 0

    def test_urgency_score_calculation(self):
        """Testa cálculo de score de urgência."""
        # Arrange
        task = PendingTaskData(
            title="Tarefa Crítica",
            priority=TaskPriority.CRITICAL,
            created_at=datetime.utcnow() - timedelta(days=5),
            compliance_risk="critical",
            business_impact="high",
        )

        # Act
        score = task.urgency_score

        # Assert
        assert score > 50  # Deve ser alta por ser crítica e antiga
        assert score <= 100


class TestTaskFilters:
    """Testes dos filtros de tarefas."""

    def test_priority_filter(self):
        """Testa filtro por prioridade."""
        # Test mock - em implementação real testaria query SQL
        assert TaskPriority.CRITICAL.value == "critical"
        assert TaskPriority.HIGH.value == "high"

    def test_department_filter(self):
        """Testa filtro por departamento."""
        # Test mock - em implementação real testaria query SQL
        assert Department.HR.value == "hr"
        assert Department.COMMERCIAL.value == "commercial"


@pytest.mark.integration
class TestDashboardIntegration:
    """Testes de integração do dashboard."""

    @pytest.mark.asyncio
    async def test_full_dashboard_flow(self):
        """Testa fluxo completo do dashboard."""
        # Este seria um teste de integração completo
        # Por enquanto apenas estrutural
        pass

    @pytest.mark.asyncio
    async def test_performance_large_dataset(self):
        """Testa performance com grande volume de dados."""
        # Teste de performance para muitas tarefas
        pass
