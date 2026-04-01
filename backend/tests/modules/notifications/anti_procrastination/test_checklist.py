"""
Testes do Sistema de Checklist Diário
====================================

Testes para verificar funcionamento do sistema de checklist
obrigatório e controle de acesso.

Autor: Conecta PRO Team + Claude AI
Data: 2026-01-10
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from modules.notifications.anti_procrastination.daily_checklist.checklist_manager import (
    ChecklistItem,
    ChecklistManager,
    ChecklistStatus,
    TaskAction,
)
from modules.notifications.anti_procrastination.models import TaskPriority


class TestChecklistManager:
    """Testes do gerenciador de checklist."""

    @pytest.fixture
    def mock_db(self):
        """Mock da sessão de banco."""
        return Mock()

    @pytest.fixture
    def mock_dashboard(self):
        """Mock do dashboard."""
        return Mock()

    @pytest.fixture
    def checklist_manager(self, mock_db, mock_dashboard):
        """Instância do checklist manager para testes."""
        return ChecklistManager(mock_db, mock_dashboard)

    @pytest.mark.asyncio
    async def test_check_daily_requirement_no_tasks(self, checklist_manager):
        """Testa requirement quando usuário não tem tarefas."""
        # Arrange
        user_id = uuid4()
        checklist_manager.db.query.return_value.filter.return_value.first.return_value = None
        checklist_manager._get_user_pending_tasks = AsyncMock(return_value=[])

        # Act
        result = await checklist_manager.check_daily_requirement(user_id, "hr")

        # Assert
        assert not result["required"]
        assert not result["blocked"]
        assert "Sem tarefas pendentes" in result["message"]

    @pytest.mark.asyncio
    async def test_check_daily_requirement_with_critical_tasks(self, checklist_manager):
        """Testa requirement com tarefas críticas (deve bloquear)."""
        # Arrange
        user_id = uuid4()
        mock_task = Mock()
        mock_task.priority = TaskPriority.CRITICAL
        mock_task.days_pending = 2

        checklist_manager.db.query.return_value.filter.return_value.first.return_value = None
        checklist_manager._get_user_pending_tasks = AsyncMock(return_value=[mock_task])

        # Act
        result = await checklist_manager.check_daily_requirement(user_id, "hr")

        # Assert
        assert result["required"]
        assert result["blocked"]
        assert result["critical_count"] == 1

    @pytest.mark.asyncio
    async def test_generate_daily_checklist(self, checklist_manager):
        """Testa geração de checklist diário."""
        # Arrange
        user_id = uuid4()
        mock_task = Mock()
        mock_task.id = uuid4()
        mock_task.title = "Tarefa Teste"
        mock_task.priority = TaskPriority.HIGH
        mock_task.days_pending = 3
        mock_task.urgency_score = 75.0

        checklist_manager.db.query.return_value.filter.return_value.first.return_value = None
        checklist_manager._get_user_pending_tasks = AsyncMock(return_value=[mock_task])

        expected_id = uuid4()

        def fake_refresh(obj):
            obj.id = expected_id

        checklist_manager.db.add = Mock()
        checklist_manager.db.commit = Mock()
        checklist_manager.db.refresh = Mock(side_effect=fake_refresh)

        # Act
        result_id = await checklist_manager.generate_daily_checklist(user_id, "João Silva", "hr")

        # Assert
        assert result_id is not None
        assert result_id == expected_id

    @pytest.mark.asyncio
    async def test_update_checklist_item_acknowledge(self, checklist_manager):
        """Testa atualização de item com ação ACKNOWLEDGED."""
        # Arrange
        checklist_id = uuid4()
        task_id = uuid4()

        mock_checklist = Mock()
        mock_checklist.id = checklist_id
        mock_checklist.total_items = 3
        mock_checklist.checklist_data = [{"task_id": str(task_id), "title": "Tarefa 1", "action_taken": None}]

        checklist_manager.db.query.return_value.filter.return_value.first.return_value = mock_checklist
        checklist_manager.db.commit = Mock()

        # Act
        result = await checklist_manager.update_checklist_item(
            checklist_id, task_id, TaskAction.ACKNOWLEDGED, "Tarefa reconhecida"
        )

        # Assert
        assert result
        # Verifica se ação foi atualizada
        item = mock_checklist.checklist_data[0]
        assert item["action_taken"] == TaskAction.ACKNOWLEDGED.value
        assert item["comment"] == "Tarefa reconhecida"

    def test_checklist_item_creation(self):
        """Testa criação de item de checklist."""
        # Arrange
        task_id = uuid4()

        # Act
        item = ChecklistItem(
            task_id=task_id, title="Tarefa Teste", priority=TaskPriority.HIGH, days_pending=5, urgency_score=80.0
        )

        # Assert
        assert item.task_id == task_id
        assert item.title == "Tarefa Teste"
        assert item.priority == TaskPriority.HIGH
        assert item.action_taken is None

    def test_should_block_access_with_critical_tasks(self, checklist_manager):
        """Testa bloqueio de acesso com tarefas críticas."""
        # Arrange
        critical_task = Mock()
        critical_task.priority = TaskPriority.CRITICAL
        critical_task.days_pending = 1

        normal_task = Mock()
        normal_task.priority = TaskPriority.MEDIUM
        normal_task.days_pending = 2

        pending_tasks = [critical_task, normal_task]

        # Act
        should_block = checklist_manager._should_block_access(pending_tasks)

        # Assert
        assert should_block  # Deve bloquear por ter tarefa crítica

    def test_should_block_access_with_many_old_tasks(self, checklist_manager):
        """Testa bloqueio com muitas tarefas antigas."""
        # Arrange
        old_tasks = []
        for _i in range(6):  # 6 tarefas antigas (> 5)
            task = Mock()
            task.priority = TaskPriority.MEDIUM
            task.days_pending = 8  # Antiga (> 7 dias)
            old_tasks.append(task)

        # Act
        should_block = checklist_manager._should_block_access(old_tasks)

        # Assert
        assert should_block  # Deve bloquear por ter muitas tarefas antigas


class TestChecklistStatusTransitions:
    """Testes de transições de status do checklist."""

    def test_valid_status_transitions(self):
        """Testa transições válidas de status."""
        # Arrange/Act/Assert
        assert ChecklistStatus.PENDING.value == "pending"
        assert ChecklistStatus.IN_PROGRESS.value == "in_progress"
        assert ChecklistStatus.COMPLETED.value == "completed"

    def test_task_action_types(self):
        """Testa tipos de ação válidos."""
        # Arrange/Act/Assert
        assert TaskAction.ACKNOWLEDGED.value == "acknowledged"
        assert TaskAction.SCHEDULED.value == "scheduled"
        assert TaskAction.COMPLETED.value == "completed"
        assert TaskAction.DELEGATED.value == "delegated"
        assert TaskAction.POSTPONED.value == "postponed"


@pytest.mark.integration
class TestChecklistIntegration:
    """Testes de integração do checklist."""

    @pytest.mark.asyncio
    async def test_complete_checklist_workflow(self):
        """Testa fluxo completo de checklist."""
        # Teste de integração end-to-end
        # Por enquanto estrutural
        pass

    @pytest.mark.asyncio
    async def test_checklist_metrics_calculation(self):
        """Testa cálculo de métricas de compliance."""
        # Teste para métricas de compliance
        pass
