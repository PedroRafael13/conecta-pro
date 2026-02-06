"""
Testes automatizados para os novos executores do Bartolo:
- SubstitutionActionExecutor
- NotificationActionExecutor
- ReportActionExecutor

Testa:
- create_preview com parametros completos e parciais
- execute com parametros validos e invalidos
- SUPPORTED_ACTIONS corretos
- Warnings e validacoes de preview
- Constantes e tipos de relatorio

Author: Conecta PRO Team
Date: 2026-01-30
"""

import sys
sys.path.insert(0, '/app')

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from modules.ai.bartolo.actions.action_schemas import ActionRequest, ActionPreview, ActionResult
from modules.ai.bartolo.actions.action_types import ActionType, ActionCategory, ActionStatus
from modules.ai.bartolo.actions.executors.substitution_executor import SubstitutionActionExecutor
from modules.ai.bartolo.actions.executors.notification_executor import NotificationActionExecutor
from modules.ai.bartolo.actions.executors.report_executor import (
    ReportActionExecutor,
    REPORT_TYPES,
    EXPORT_FORMATS,
)


# =============================================================================
# Fixtures compartilhadas
# =============================================================================

@pytest.fixture
def mock_db():
    """Fixture para mock do banco de dados (AsyncSession)."""
    db = AsyncMock()
    return db


@pytest.fixture
def substitution_executor(mock_db):
    """Fixture para SubstitutionActionExecutor."""
    return SubstitutionActionExecutor(db=mock_db)


@pytest.fixture
def notification_executor(mock_db):
    """Fixture para NotificationActionExecutor."""
    return NotificationActionExecutor(db=mock_db)


@pytest.fixture
def report_executor(mock_db):
    """Fixture para ReportActionExecutor."""
    return ReportActionExecutor(db=mock_db)


# =============================================================================
# Helpers
# =============================================================================

def _make_request(
    action_type: ActionType,
    category: ActionCategory,
    parameters: dict,
    message: str = "comando teste",
    confidence: float = 0.8,
    user_id: str = "user-1",
    session_id: str = "sess-1",
) -> ActionRequest:
    """Helper para criar ActionRequest."""
    return ActionRequest(
        action_type=action_type,
        category=category,
        parameters=parameters,
        detected_from_message=message,
        confidence=confidence,
        user_id=user_id,
        session_id=session_id,
    )


def _substitution_request(parameters: dict, message: str = "criar substituicao") -> ActionRequest:
    """Helper para criar request de substituicao."""
    return _make_request(
        action_type=ActionType.CREATE_SUBSTITUTION,
        category=ActionCategory.OPERATIONAL,
        parameters=parameters,
        message=message,
    )


def _notification_request(parameters: dict, message: str = "enviar notificacao") -> ActionRequest:
    """Helper para criar request de notificacao."""
    return _make_request(
        action_type=ActionType.SEND_NOTIFICATION,
        category=ActionCategory.NOTIFICATION,
        parameters=parameters,
        message=message,
    )


def _report_request(parameters: dict, message: str = "gerar relatorio") -> ActionRequest:
    """Helper para criar request de relatorio."""
    return _make_request(
        action_type=ActionType.GENERATE_REPORT,
        category=ActionCategory.REPORT,
        parameters=parameters,
        message=message,
    )


# =============================================================================
# TestSubstitutionActionExecutor
# =============================================================================

class TestSubstitutionActionExecutor:
    """Testes para SubstitutionActionExecutor."""

    # -------------------------------------------------------------------------
    # SUPPORTED_ACTIONS
    # -------------------------------------------------------------------------

    def test_supported_actions_contains_create_substitution(self):
        """Testa que SUPPORTED_ACTIONS contem CREATE_SUBSTITUTION."""
        assert ActionType.CREATE_SUBSTITUTION in SubstitutionActionExecutor.SUPPORTED_ACTIONS

    def test_supported_actions_length(self):
        """Testa que SUPPORTED_ACTIONS tem exatamente 1 acao."""
        assert len(SubstitutionActionExecutor.SUPPORTED_ACTIONS) == 1

    # -------------------------------------------------------------------------
    # create_preview
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_preview_all_parameters(self, substitution_executor):
        """Testa create_preview com todos os parametros preenchidos."""
        request = _substitution_request({
            "employee_id": "EMP-001",
            "substitute_id": "EMP-002",
            "post_code": "POST-101",
            "start_date": "2026-02-01",
            "end_date": "2026-02-15",
            "reason": "Ferias do titular",
        })

        preview = await substitution_executor.create_preview(request)

        assert isinstance(preview, ActionPreview)
        assert preview.action_type == ActionType.CREATE_SUBSTITUTION
        assert "EMP-001" in preview.title
        assert preview.required_permission == "substitutions:create"
        assert preview.user_has_permission is True
        assert preview.can_be_undone is True
        assert preview.requires_confirmation is True
        assert any("EMP-001" in s for s in preview.changes_summary)
        assert any("EMP-002" in s for s in preview.changes_summary)
        assert any("POST-101" in s for s in preview.changes_summary)
        assert any("2026-02-01" in s for s in preview.changes_summary)
        assert any("2026-02-15" in s for s in preview.changes_summary)
        assert any("Ferias do titular" in s for s in preview.changes_summary)

    @pytest.mark.asyncio
    async def test_create_preview_missing_employee_id_warning(self, substitution_executor):
        """Testa que preview gera warning quando employee_id esta ausente."""
        request = _substitution_request({
            "substitute_id": "EMP-002",
            "post_code": "POST-101",
        })

        preview = await substitution_executor.create_preview(request)

        assert isinstance(preview, ActionPreview)
        assert any("titular" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_missing_substitute_id_warning(self, substitution_executor):
        """Testa que preview gera warning quando substitute_id esta ausente."""
        request = _substitution_request({
            "employee_id": "EMP-001",
            "post_code": "POST-101",
        })

        preview = await substitution_executor.create_preview(request)

        assert isinstance(preview, ActionPreview)
        assert any("substituto" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_missing_start_date_warning(self, substitution_executor):
        """Testa que preview gera warning quando start_date esta ausente."""
        request = _substitution_request({
            "employee_id": "EMP-001",
            "substitute_id": "EMP-002",
        })

        preview = await substitution_executor.create_preview(request)

        assert any("inicio" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_missing_end_date_warning(self, substitution_executor):
        """Testa que preview gera warning quando end_date esta ausente."""
        request = _substitution_request({
            "employee_id": "EMP-001",
            "substitute_id": "EMP-002",
            "start_date": "2026-02-01",
        })

        preview = await substitution_executor.create_preview(request)

        assert any("termino" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_affected_entities(self, substitution_executor):
        """Testa que affected_entities inclui titular e substituto."""
        request = _substitution_request({
            "employee_id": "EMP-001",
            "substitute_id": "EMP-002",
            "post_code": "POST-101",
        })

        preview = await substitution_executor.create_preview(request)

        employee_entities = [e for e in preview.affected_entities if e.get("type") == "employee"]
        post_entities = [e for e in preview.affected_entities if e.get("type") == "post"]
        assert len(employee_entities) == 2
        assert len(post_entities) == 1
        assert any(e.get("role") == "titular" for e in employee_entities)
        assert any(e.get("role") == "substituto" for e in employee_entities)

    @pytest.mark.asyncio
    async def test_create_preview_qualification_warning(self, substitution_executor):
        """Testa que preview gera warning de qualificacao quando ambos IDs presentes."""
        request = _substitution_request({
            "employee_id": "EMP-001",
            "substitute_id": "EMP-002",
        })

        preview = await substitution_executor.create_preview(request)

        assert any("qualificacoes" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_empty_params(self, substitution_executor):
        """Testa create_preview com parametros vazios gera multiplos warnings."""
        request = _substitution_request({})

        preview = await substitution_executor.create_preview(request)

        assert isinstance(preview, ActionPreview)
        assert len(preview.warnings) >= 2  # titular + substituto no minimo
        assert preview.title == "Criar Substituicao"

    @pytest.mark.asyncio
    async def test_create_preview_title_with_employee(self, substitution_executor):
        """Testa que titulo inclui employee_id quando presente."""
        request = _substitution_request({"employee_id": "EMP-001"})

        preview = await substitution_executor.create_preview(request)

        assert "EMP-001" in preview.title

    @pytest.mark.asyncio
    async def test_create_preview_title_without_employee(self, substitution_executor):
        """Testa que titulo padrao e usado quando employee_id ausente."""
        request = _substitution_request({})

        preview = await substitution_executor.create_preview(request)

        assert preview.title == "Criar Substituicao"

    @pytest.mark.asyncio
    async def test_create_preview_description_with_post(self, substitution_executor):
        """Testa que descricao menciona posto quando informado."""
        request = _substitution_request({"post_code": "POST-101"})

        preview = await substitution_executor.create_preview(request)

        assert "POST-101" in preview.description

    @pytest.mark.asyncio
    async def test_create_preview_description_without_post(self, substitution_executor):
        """Testa descricao padrao quando posto nao informado."""
        request = _substitution_request({})

        preview = await substitution_executor.create_preview(request)

        assert "temporaria" in preview.description.lower()

    # -------------------------------------------------------------------------
    # execute
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.substitution_executor._HAS_SUBSTITUICAO_REPO", False)
    async def test_execute_valid_parameters(self, substitution_executor):
        """Testa execute com parametros validos retorna COMPLETED."""
        request = _substitution_request({
            "employee_id": "EMP-001",
            "substitute_id": "EMP-002",
            "post_code": "POST-101",
            "start_date": "2026-02-01",
            "end_date": "2026-02-15",
            "reason": "Ferias",
        })

        result = await substitution_executor.execute(request, "action-001")

        assert isinstance(result, ActionResult)
        assert result.status == ActionStatus.COMPLETED
        assert result.success is True
        assert result.action_id == "action-001"
        assert "sucesso" in result.message.lower()
        assert result.details["employee_id"] == "EMP-001"
        assert result.details["substitute_id"] == "EMP-002"
        assert result.details["post_code"] == "POST-101"

    @pytest.mark.asyncio
    async def test_execute_missing_employee_id_raises(self, substitution_executor):
        """Testa que execute sem employee_id retorna FAILED (ValueError capturada)."""
        request = _substitution_request({
            "substitute_id": "EMP-002",
        })

        result = await substitution_executor.execute(request, "action-002")

        assert isinstance(result, ActionResult)
        assert result.status == ActionStatus.FAILED
        assert result.success is False
        assert "obrigatorio" in (result.error_message or "").lower()

    @pytest.mark.asyncio
    async def test_execute_missing_substitute_id_raises(self, substitution_executor):
        """Testa que execute sem substitute_id retorna FAILED (ValueError capturada)."""
        request = _substitution_request({
            "employee_id": "EMP-001",
        })

        result = await substitution_executor.execute(request, "action-003")

        assert isinstance(result, ActionResult)
        assert result.status == ActionStatus.FAILED
        assert result.success is False
        assert "obrigatorio" in (result.error_message or "").lower()

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.substitution_executor._HAS_SUBSTITUICAO_REPO", False)
    async def test_execute_result_has_affected_entities(self, substitution_executor):
        """Testa que resultado de execute inclui affected_entities."""
        request = _substitution_request({
            "employee_id": "EMP-001",
            "substitute_id": "EMP-002",
        })

        result = await substitution_executor.execute(request, "action-004")

        assert len(result.affected_entities) == 3
        types = [e["type"] for e in result.affected_entities]
        assert "substitution" in types
        assert "employee" in types

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.substitution_executor._HAS_SUBSTITUICAO_REPO", False)
    async def test_execute_result_timing(self, substitution_executor):
        """Testa que resultado tem timestamps e duracao."""
        request = _substitution_request({
            "employee_id": "EMP-001",
            "substitute_id": "EMP-002",
        })

        result = await substitution_executor.execute(request, "action-005")

        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.duration_seconds is not None
        assert result.duration_seconds >= 0

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.substitution_executor._HAS_SUBSTITUICAO_REPO", False)
    async def test_execute_default_reason(self, substitution_executor):
        """Testa que reason padrao e aplicado quando nao fornecido."""
        request = _substitution_request({
            "employee_id": "EMP-001",
            "substitute_id": "EMP-002",
        })

        result = await substitution_executor.execute(request, "action-006")

        assert result.details["reason"] == "Substituicao via Bartolo"


# =============================================================================
# TestNotificationActionExecutor
# =============================================================================

class TestNotificationActionExecutor:
    """Testes para NotificationActionExecutor."""

    # -------------------------------------------------------------------------
    # SUPPORTED_ACTIONS
    # -------------------------------------------------------------------------

    def test_supported_actions_contains_send_notification(self):
        """Testa que SUPPORTED_ACTIONS contem SEND_NOTIFICATION."""
        assert ActionType.SEND_NOTIFICATION in NotificationActionExecutor.SUPPORTED_ACTIONS

    def test_supported_actions_length(self):
        """Testa que SUPPORTED_ACTIONS tem exatamente 1 acao."""
        assert len(NotificationActionExecutor.SUPPORTED_ACTIONS) == 1

    # -------------------------------------------------------------------------
    # create_preview
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_preview_all_parameters(self, notification_executor):
        """Testa create_preview com todos os parametros preenchidos."""
        request = _notification_request({
            "title": "Alerta de Seguranca",
            "message": "Verificar posto central imediatamente",
            "channel": "push",
            "target_type": "user",
            "target_ids": ["user-1", "user-2"],
            "priority": "normal",
        })

        preview = await notification_executor.create_preview(request)

        assert isinstance(preview, ActionPreview)
        assert preview.action_type == ActionType.SEND_NOTIFICATION
        assert "Alerta de Seguranca" in preview.title
        assert preview.required_permission == "notifications:send"
        assert preview.user_has_permission is True
        assert preview.can_be_undone is False
        assert preview.requires_confirmation is True
        assert any("Alerta de Seguranca" in s for s in preview.changes_summary)
        assert any("push" in s.lower() for s in preview.changes_summary)

    @pytest.mark.asyncio
    async def test_create_preview_missing_title_warning(self, notification_executor):
        """Testa que preview gera warning quando titulo ausente."""
        request = _notification_request({
            "message": "Corpo da mensagem",
            "channel": "push",
        })

        preview = await notification_executor.create_preview(request)

        assert any("titulo" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_missing_message_warning(self, notification_executor):
        """Testa que preview gera warning quando mensagem ausente."""
        request = _notification_request({
            "title": "Alerta",
            "channel": "push",
        })

        preview = await notification_executor.create_preview(request)

        assert any("mensagem" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_target_type_all_warning(self, notification_executor):
        """Testa que preview gera warning para target_type 'all'."""
        request = _notification_request({
            "title": "Aviso Geral",
            "message": "Reuniao amanha",
            "channel": "push",
            "target_type": "all",
        })

        preview = await notification_executor.create_preview(request)

        assert any("todos" in w.lower() for w in preview.warnings)
        assert any("alcance" in s.lower() or "todos" in s.lower() for s in preview.changes_summary)

    @pytest.mark.asyncio
    async def test_create_preview_sms_channel_cost_warning(self, notification_executor):
        """Testa que preview gera warning de custo para canal SMS."""
        request = _notification_request({
            "title": "Alerta SMS",
            "message": "Verificar posto",
            "channel": "sms",
            "target_type": "user",
            "target_ids": ["user-1"],
        })

        preview = await notification_executor.create_preview(request)

        assert any("custo" in w.lower() or "sms" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_all_channel_cost_warning(self, notification_executor):
        """Testa que preview gera warning de custo para canal 'all' (inclui SMS)."""
        request = _notification_request({
            "title": "Alerta",
            "message": "Mensagem urgente",
            "channel": "all",
            "target_type": "user",
            "target_ids": ["user-1"],
        })

        preview = await notification_executor.create_preview(request)

        assert any("custo" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_invalid_channel_warning(self, notification_executor):
        """Testa que preview gera warning para canal invalido."""
        request = _notification_request({
            "title": "Alerta",
            "message": "Mensagem",
            "channel": "telegram",
        })

        preview = await notification_executor.create_preview(request)

        assert any("invalido" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_high_priority_warning(self, notification_executor):
        """Testa que preview gera warning para prioridade alta."""
        request = _notification_request({
            "title": "Emergencia",
            "message": "Evacuacao imediata",
            "channel": "push",
            "priority": "urgente",
        })

        preview = await notification_executor.create_preview(request)

        assert any("urgente" in w.lower() or "prioridade" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_target_ids_count(self, notification_executor):
        """Testa que preview mostra contagem de destinatarios."""
        target_ids = [f"user-{i}" for i in range(10)]
        request = _notification_request({
            "title": "Aviso",
            "message": "Corpo",
            "channel": "push",
            "target_type": "user",
            "target_ids": target_ids,
        })

        preview = await notification_executor.create_preview(request)

        assert any("10" in s for s in preview.changes_summary)
        # Apenas 5 primeiros devem estar nos affected_entities
        user_entities = [e for e in preview.affected_entities if e.get("type") == "user"]
        assert len(user_entities) == 5

    @pytest.mark.asyncio
    async def test_create_preview_role_target(self, notification_executor):
        """Testa preview com target_type 'role'."""
        request = _notification_request({
            "title": "Aviso Supervisores",
            "message": "Reuniao amanha",
            "channel": "email",
            "target_type": "role",
            "target_roles": ["supervisor", "gerente"],
        })

        preview = await notification_executor.create_preview(request)

        assert any("supervisor" in s.lower() or "gerente" in s.lower() for s in preview.changes_summary)

    @pytest.mark.asyncio
    async def test_create_preview_long_message_truncated(self, notification_executor):
        """Testa que mensagem longa e truncada no preview."""
        long_msg = "A" * 200
        request = _notification_request({
            "title": "Aviso",
            "message": long_msg,
            "channel": "push",
        })

        preview = await notification_executor.create_preview(request)

        msg_summaries = [s for s in preview.changes_summary if "Mensagem:" in s]
        assert len(msg_summaries) == 1
        assert "..." in msg_summaries[0]

    @pytest.mark.asyncio
    async def test_create_preview_title_format_with_title(self, notification_executor):
        """Testa formato do titulo do preview quando titulo da notificacao presente."""
        request = _notification_request({
            "title": "Alerta Seguranca",
            "message": "Corpo",
        })

        preview = await notification_executor.create_preview(request)

        assert "Alerta Seguranca" in preview.title
        assert "Enviar Notificacao" in preview.title

    @pytest.mark.asyncio
    async def test_create_preview_title_format_without_title(self, notification_executor):
        """Testa formato do titulo do preview quando titulo ausente."""
        request = _notification_request({
            "message": "Corpo",
        })

        preview = await notification_executor.create_preview(request)

        assert preview.title == "Enviar Notificacao"

    @pytest.mark.asyncio
    async def test_create_preview_empty_params(self, notification_executor):
        """Testa create_preview com parametros vazios."""
        request = _notification_request({})

        preview = await notification_executor.create_preview(request)

        assert isinstance(preview, ActionPreview)
        # Deve ter warnings para titulo e mensagem
        assert len(preview.warnings) >= 2

    # -------------------------------------------------------------------------
    # execute
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.notification_executor._HAS_NOTIFICATION_SERVICE", False)
    @patch("modules.ai.bartolo.actions.executors.notification_executor._HAS_PUSH_SERVICE", False)
    async def test_execute_valid_parameters(self, notification_executor):
        """Testa execute com parametros validos retorna COMPLETED."""
        request = _notification_request({
            "title": "Alerta",
            "message": "Verificar posto central",
            "channel": "push",
            "target_type": "user",
            "target_ids": ["user-1", "user-2"],
            "priority": "normal",
        })

        result = await notification_executor.execute(request, "action-101")

        assert isinstance(result, ActionResult)
        assert result.status == ActionStatus.COMPLETED
        assert result.success is True
        assert result.action_id == "action-101"
        assert result.details["title"] == "Alerta"
        assert result.details["channel"] == "push"
        assert result.details["sent_count"] == 2

    @pytest.mark.asyncio
    async def test_execute_missing_title_raises(self, notification_executor):
        """Testa que execute sem titulo retorna FAILED (ValueError capturada)."""
        request = _notification_request({
            "message": "Corpo da mensagem",
            "channel": "push",
        })

        result = await notification_executor.execute(request, "action-102")

        assert isinstance(result, ActionResult)
        assert result.status == ActionStatus.FAILED
        assert result.success is False
        assert "titulo" in (result.error_message or "").lower()

    @pytest.mark.asyncio
    async def test_execute_missing_message_raises(self, notification_executor):
        """Testa que execute sem mensagem retorna FAILED (ValueError capturada)."""
        request = _notification_request({
            "title": "Alerta",
            "channel": "push",
        })

        result = await notification_executor.execute(request, "action-103")

        assert isinstance(result, ActionResult)
        assert result.status == ActionStatus.FAILED
        assert result.success is False
        assert "mensagem" in (result.error_message or "").lower()

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.notification_executor._HAS_NOTIFICATION_SERVICE", False)
    @patch("modules.ai.bartolo.actions.executors.notification_executor._HAS_PUSH_SERVICE", False)
    async def test_execute_result_timing(self, notification_executor):
        """Testa que resultado tem timestamps e duracao."""
        request = _notification_request({
            "title": "Alerta",
            "message": "Mensagem",
            "channel": "push",
        })

        result = await notification_executor.execute(request, "action-104")

        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.duration_seconds is not None
        assert result.duration_seconds >= 0

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.notification_executor._HAS_NOTIFICATION_SERVICE", False)
    @patch("modules.ai.bartolo.actions.executors.notification_executor._HAS_PUSH_SERVICE", False)
    async def test_execute_fallback_creates_notification_id(self, notification_executor):
        """Testa que fallback cria notification_id."""
        request = _notification_request({
            "title": "Alerta",
            "message": "Mensagem",
            "channel": "push",
            "target_ids": ["user-1"],
        })

        result = await notification_executor.execute(request, "action-105")

        assert len(result.details["notification_ids"]) > 0

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.notification_executor._HAS_NOTIFICATION_SERVICE", False)
    @patch("modules.ai.bartolo.actions.executors.notification_executor._HAS_PUSH_SERVICE", False)
    async def test_execute_affected_entities(self, notification_executor):
        """Testa que affected_entities inclui notificacoes."""
        request = _notification_request({
            "title": "Alerta",
            "message": "Mensagem",
            "channel": "push",
        })

        result = await notification_executor.execute(request, "action-106")

        assert len(result.affected_entities) > 0
        assert result.affected_entities[0]["type"] == "notification"

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.notification_executor._HAS_NOTIFICATION_SERVICE", False)
    @patch("modules.ai.bartolo.actions.executors.notification_executor._HAS_PUSH_SERVICE", False)
    async def test_execute_no_target_ids_still_succeeds(self, notification_executor):
        """Testa que execute sem target_ids (fallback) ainda retorna sucesso."""
        request = _notification_request({
            "title": "Aviso Geral",
            "message": "Corpo",
            "channel": "push",
            "target_type": "all",
        })

        result = await notification_executor.execute(request, "action-107")

        assert result.success is True
        assert result.details["sent_count"] == 1  # fallback default


# =============================================================================
# TestReportActionExecutor
# =============================================================================

class TestReportActionExecutor:
    """Testes para ReportActionExecutor."""

    # -------------------------------------------------------------------------
    # SUPPORTED_ACTIONS
    # -------------------------------------------------------------------------

    def test_supported_actions_contains_generate_report(self):
        """Testa que SUPPORTED_ACTIONS contem GENERATE_REPORT."""
        assert ActionType.GENERATE_REPORT in ReportActionExecutor.SUPPORTED_ACTIONS

    def test_supported_actions_length(self):
        """Testa que SUPPORTED_ACTIONS tem exatamente 1 acao."""
        assert len(ReportActionExecutor.SUPPORTED_ACTIONS) == 1

    # -------------------------------------------------------------------------
    # REPORT_TYPES e EXPORT_FORMATS
    # -------------------------------------------------------------------------

    def test_report_types_has_all_expected_types(self):
        """Testa que REPORT_TYPES contem todos os tipos esperados."""
        expected = [
            "horas_extras", "custos", "banco_horas", "substituicoes",
            "disciplinar", "ocorrencias", "diaristas", "rondas",
            "postos", "escalas", "geral",
        ]
        for report_type in expected:
            assert report_type in REPORT_TYPES, f"Tipo '{report_type}' ausente em REPORT_TYPES"

    def test_report_types_count(self):
        """Testa quantidade de tipos de relatorio."""
        assert len(REPORT_TYPES) == 11

    def test_report_types_structure(self):
        """Testa que cada tipo tem name, description e required_params."""
        for key, info in REPORT_TYPES.items():
            assert "name" in info, f"Tipo '{key}' sem 'name'"
            assert "description" in info, f"Tipo '{key}' sem 'description'"
            assert "required_params" in info, f"Tipo '{key}' sem 'required_params'"
            assert isinstance(info["required_params"], list)

    def test_export_formats_has_pdf(self):
        """Testa que EXPORT_FORMATS contem pdf."""
        assert "pdf" in EXPORT_FORMATS

    def test_export_formats_has_xlsx(self):
        """Testa que EXPORT_FORMATS contem xlsx."""
        assert "xlsx" in EXPORT_FORMATS

    def test_export_formats_has_csv(self):
        """Testa que EXPORT_FORMATS contem csv."""
        assert "csv" in EXPORT_FORMATS

    def test_export_formats_has_json(self):
        """Testa que EXPORT_FORMATS contem json."""
        assert "json" in EXPORT_FORMATS

    def test_export_formats_count(self):
        """Testa que EXPORT_FORMATS tem 4 formatos."""
        assert len(EXPORT_FORMATS) == 4

    # -------------------------------------------------------------------------
    # create_preview
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_preview_valid_report_type(self, report_executor):
        """Testa create_preview com tipo de relatorio valido."""
        request = _report_request({
            "report_type": "horas_extras",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
            "format": "pdf",
        })

        preview = await report_executor.create_preview(request)

        assert isinstance(preview, ActionPreview)
        assert preview.action_type == ActionType.GENERATE_REPORT
        assert "Horas Extras" in preview.title
        assert preview.required_permission == "reports:generate"
        assert preview.can_be_undone is False
        assert preview.requires_confirmation is True
        assert any("Horas Extras" in s for s in preview.changes_summary)
        assert any("PDF" in s for s in preview.changes_summary)

    @pytest.mark.asyncio
    async def test_create_preview_unknown_report_type_warning(self, report_executor):
        """Testa que preview gera warning para tipo desconhecido."""
        request = _report_request({
            "report_type": "tipo_inexistente",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
        })

        preview = await report_executor.create_preview(request)

        assert any("nao reconhecido" in w.lower() for w in preview.warnings)
        # Deve fazer fallback para "geral"
        assert any("Geral" in s for s in preview.changes_summary)

    @pytest.mark.asyncio
    async def test_create_preview_missing_period_start_warning(self, report_executor):
        """Testa que preview gera warning quando period_start ausente (tipo que requer)."""
        request = _report_request({
            "report_type": "horas_extras",
            "period_end": "2026-01-31",
        })

        preview = await report_executor.create_preview(request)

        assert any("inicio" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_missing_period_end_warning(self, report_executor):
        """Testa que preview gera warning quando period_end ausente (tipo que requer)."""
        request = _report_request({
            "report_type": "custos",
            "period_start": "2026-01-01",
        })

        preview = await report_executor.create_preview(request)

        assert any("fim" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_postos_no_period_warning(self, report_executor):
        """Testa que tipo 'postos' nao requer periodo (sem warning)."""
        request = _report_request({
            "report_type": "postos",
        })

        preview = await report_executor.create_preview(request)

        # "postos" tem required_params vazio, nao deve ter warning de periodo
        period_warnings = [w for w in preview.warnings if "periodo" in w.lower() or "inicio" in w.lower() or "fim" in w.lower()]
        assert len(period_warnings) == 0

    @pytest.mark.asyncio
    async def test_create_preview_with_post_filter(self, report_executor):
        """Testa preview com filtro por posto."""
        request = _report_request({
            "report_type": "geral",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
            "post_code": "POST-101",
        })

        preview = await report_executor.create_preview(request)

        assert any("POST-101" in s for s in preview.changes_summary)
        post_entities = [e for e in preview.affected_entities if e.get("type") == "post"]
        assert len(post_entities) == 1

    @pytest.mark.asyncio
    async def test_create_preview_with_employee_filter(self, report_executor):
        """Testa preview com filtro por funcionario."""
        request = _report_request({
            "report_type": "horas_extras",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
            "employee_id": "EMP-001",
        })

        preview = await report_executor.create_preview(request)

        assert any("EMP-001" in s for s in preview.changes_summary)
        employee_entities = [e for e in preview.affected_entities if e.get("type") == "employee"]
        assert len(employee_entities) == 1

    @pytest.mark.asyncio
    async def test_create_preview_invalid_format_warning(self, report_executor):
        """Testa que preview gera warning para formato invalido."""
        request = _report_request({
            "report_type": "geral",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
            "format": "docx",
        })

        preview = await report_executor.create_preview(request)

        assert any("nao suportado" in w.lower() or "formato" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_geral_no_filter_warning(self, report_executor):
        """Testa que relatorio geral sem filtros gera warning de demora."""
        request = _report_request({
            "report_type": "geral",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
        })

        preview = await report_executor.create_preview(request)

        assert any("demorar" in w.lower() for w in preview.warnings)

    @pytest.mark.asyncio
    async def test_create_preview_geral_with_filter_no_delay_warning(self, report_executor):
        """Testa que relatorio geral com filtro nao gera warning de demora."""
        request = _report_request({
            "report_type": "geral",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
            "post_code": "POST-101",
        })

        preview = await report_executor.create_preview(request)

        delay_warnings = [w for w in preview.warnings if "demorar" in w.lower()]
        assert len(delay_warnings) == 0

    @pytest.mark.asyncio
    async def test_create_preview_empty_params(self, report_executor):
        """Testa create_preview com parametros vazios (usa defaults)."""
        request = _report_request({})

        preview = await report_executor.create_preview(request)

        assert isinstance(preview, ActionPreview)
        # Default e "geral" que requer periodo
        assert any("Geral" in s for s in preview.changes_summary)

    # -------------------------------------------------------------------------
    # execute
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.report_executor._HAS_RELATORIO_SERVICE", False)
    @patch("modules.ai.bartolo.actions.executors.report_executor._HAS_EXPORT_SERVICE", False)
    async def test_execute_valid_parameters(self, report_executor):
        """Testa execute com parametros validos retorna COMPLETED."""
        request = _report_request({
            "report_type": "horas_extras",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
            "format": "pdf",
        })

        result = await report_executor.execute(request, "action-201")

        assert isinstance(result, ActionResult)
        assert result.status == ActionStatus.COMPLETED
        assert result.success is True
        assert result.action_id == "action-201"
        assert "sucesso" in result.message.lower()
        assert result.details["report_type"] == "horas_extras"
        assert result.details["format"] == "pdf"

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.report_executor._HAS_RELATORIO_SERVICE", False)
    @patch("modules.ai.bartolo.actions.executors.report_executor._HAS_EXPORT_SERVICE", False)
    async def test_execute_fallback_generates_data(self, report_executor):
        """Testa que fallback gera dados de demonstracao."""
        request = _report_request({
            "report_type": "custos",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
        })

        result = await report_executor.execute(request, "action-202")

        assert result.success is True
        data = result.details.get("data", {})
        assert data.get("report_type") == "custos"
        assert "summary" in data
        assert data["summary"].get("custo_total") is not None

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.report_executor._HAS_RELATORIO_SERVICE", False)
    @patch("modules.ai.bartolo.actions.executors.report_executor._HAS_EXPORT_SERVICE", False)
    async def test_execute_result_timing(self, report_executor):
        """Testa que resultado tem timestamps e duracao."""
        request = _report_request({
            "report_type": "geral",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
        })

        result = await report_executor.execute(request, "action-203")

        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.duration_seconds is not None
        assert result.duration_seconds >= 0

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.report_executor._HAS_RELATORIO_SERVICE", False)
    @patch("modules.ai.bartolo.actions.executors.report_executor._HAS_EXPORT_SERVICE", False)
    async def test_execute_affected_entities(self, report_executor):
        """Testa que resultado inclui affected_entities com report."""
        request = _report_request({
            "report_type": "ocorrencias",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
        })

        result = await report_executor.execute(request, "action-204")

        assert len(result.affected_entities) == 1
        assert result.affected_entities[0]["type"] == "report"

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.report_executor._HAS_RELATORIO_SERVICE", False)
    @patch("modules.ai.bartolo.actions.executors.report_executor._HAS_EXPORT_SERVICE", False)
    async def test_execute_unknown_type_fallback_to_geral(self, report_executor):
        """Testa que tipo desconhecido faz fallback para geral no execute."""
        request = _report_request({
            "report_type": "desconhecido",
        })

        result = await report_executor.execute(request, "action-205")

        assert result.success is True
        # Fallback vai para "geral" via REPORT_TYPES.get(...)
        assert "Geral" in result.message or result.details["report_type"] == "desconhecido"

    @pytest.mark.asyncio
    @patch("modules.ai.bartolo.actions.executors.report_executor._HAS_RELATORIO_SERVICE", False)
    @patch("modules.ai.bartolo.actions.executors.report_executor._HAS_EXPORT_SERVICE", False)
    async def test_execute_result_details_structure(self, report_executor):
        """Testa estrutura completa dos details no resultado."""
        request = _report_request({
            "report_type": "banco_horas",
            "period_start": "2026-01-01",
            "period_end": "2026-01-31",
            "post_code": "POST-101",
            "employee_id": "EMP-001",
            "format": "xlsx",
        })

        result = await report_executor.execute(request, "action-206")

        details = result.details
        assert "report_id" in details
        assert details["report_type"] == "banco_horas"
        assert details["report_name"] == "Relatorio de Banco de Horas"
        assert details["format"] == "xlsx"
        assert "period" in details
        assert details["period"]["start"] == "2026-01-01"
        assert details["period"]["end"] == "2026-01-31"
        assert "filters" in details
        assert details["filters"]["post_code"] == "POST-101"
        assert details["filters"]["employee_id"] == "EMP-001"

    # -------------------------------------------------------------------------
    # _generate_fallback_summary
    # -------------------------------------------------------------------------

    def test_generate_fallback_summary_horas_extras(self, report_executor):
        """Testa fallback summary para horas_extras."""
        summary = report_executor._generate_fallback_summary("horas_extras")
        assert "total_horas" in summary
        assert "total_funcionarios" in summary
        assert "custo_estimado" in summary

    def test_generate_fallback_summary_custos(self, report_executor):
        """Testa fallback summary para custos."""
        summary = report_executor._generate_fallback_summary("custos")
        assert "custo_total" in summary
        assert "custo_pessoal" in summary

    def test_generate_fallback_summary_banco_horas(self, report_executor):
        """Testa fallback summary para banco_horas."""
        summary = report_executor._generate_fallback_summary("banco_horas")
        assert "saldo_total" in summary
        assert "creditos" in summary
        assert "debitos" in summary

    def test_generate_fallback_summary_substituicoes(self, report_executor):
        """Testa fallback summary para substituicoes."""
        summary = report_executor._generate_fallback_summary("substituicoes")
        assert "total" in summary
        assert "concluidas" in summary
        assert "ativas" in summary

    def test_generate_fallback_summary_disciplinar(self, report_executor):
        """Testa fallback summary para disciplinar."""
        summary = report_executor._generate_fallback_summary("disciplinar")
        assert "total" in summary
        assert "advertencias" in summary

    def test_generate_fallback_summary_ocorrencias(self, report_executor):
        """Testa fallback summary para ocorrencias."""
        summary = report_executor._generate_fallback_summary("ocorrencias")
        assert "total" in summary
        assert "resolvidas" in summary
        assert "pendentes" in summary

    def test_generate_fallback_summary_diaristas(self, report_executor):
        """Testa fallback summary para diaristas."""
        summary = report_executor._generate_fallback_summary("diaristas")
        assert "total_escalados" in summary
        assert "media_avaliacao" in summary

    def test_generate_fallback_summary_rondas(self, report_executor):
        """Testa fallback summary para rondas."""
        summary = report_executor._generate_fallback_summary("rondas")
        assert "total" in summary
        assert "conformidade" in summary

    def test_generate_fallback_summary_postos(self, report_executor):
        """Testa fallback summary para postos."""
        summary = report_executor._generate_fallback_summary("postos")
        assert "total_postos" in summary
        assert "cobertura" in summary

    def test_generate_fallback_summary_escalas(self, report_executor):
        """Testa fallback summary para escalas."""
        summary = report_executor._generate_fallback_summary("escalas")
        assert "total_geradas" in summary
        assert "cumprimento" in summary

    def test_generate_fallback_summary_geral(self, report_executor):
        """Testa fallback summary para geral."""
        summary = report_executor._generate_fallback_summary("geral")
        assert "total_funcionarios" in summary
        assert "total_postos" in summary
        assert "cobertura_media" in summary

    def test_generate_fallback_summary_unknown_type(self, report_executor):
        """Testa que tipo desconhecido retorna summary do geral."""
        summary = report_executor._generate_fallback_summary("tipo_inexistente")
        geral_summary = report_executor._generate_fallback_summary("geral")
        assert summary == geral_summary

    def test_generate_fallback_summary_returns_dict(self, report_executor):
        """Testa que fallback summary sempre retorna dict."""
        for report_type in REPORT_TYPES.keys():
            summary = report_executor._generate_fallback_summary(report_type)
            assert isinstance(summary, dict), f"Tipo '{report_type}' nao retornou dict"
            assert len(summary) > 0, f"Tipo '{report_type}' retornou dict vazio"
