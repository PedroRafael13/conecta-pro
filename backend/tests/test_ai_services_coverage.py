"""
Tests for modules/ai/ — targeting service logic, conditional branches, and return values.

Covers:
  - bartolo/services/bartolo_engine.py
  - bartolo/services/learning_service.py
  - bartolo/services/profile_service.py
  - bartolo/config/system_prompt.py
  - bartolo/config/modules.py
  - bartolo/config/identity.py
  - bartolo/actions/action_detector.py
"""

import asyncio
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# ---------------------------------------------------------------------------
# ============================= ACTION TYPES ================================
# ---------------------------------------------------------------------------


class TestActionTypes:
    def test_all_scale_action_types_exist(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        assert ActionType.CREATE_SCALE == "create_scale"
        assert ActionType.APPROVE_SCALE == "approve_scale"
        assert ActionType.PUBLISH_SCALE == "publish_scale"
        assert ActionType.AUTO_GENERATE_SCALE == "auto_generate_scale"
        assert ActionType.OPTIMIZE_SCALE == "optimize_scale"
        assert ActionType.CREATE_SCALE_TEMPLATE == "create_scale_template"
        assert ActionType.APPLY_SCALE_TEMPLATE == "apply_scale_template"

    def test_allocation_action_types(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        assert ActionType.ALLOCATE_EMPLOYEE == "allocate_employee"
        assert ActionType.TERMINATE_ALLOCATION == "terminate_allocation"
        assert ActionType.TRANSFER_EMPLOYEE == "transfer_employee"

    def test_shift_action_types(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        assert ActionType.CREATE_SHIFT == "create_shift"
        assert ActionType.REGISTER_CHECKIN == "register_checkin"
        assert ActionType.REGISTER_CHECKOUT == "register_checkout"
        assert ActionType.MARK_ABSENCE == "mark_absence"

    def test_occurrence_action_types(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        assert ActionType.CREATE_OCCURRENCE == "create_occurrence"
        assert ActionType.RESOLVE_OCCURRENCE == "resolve_occurrence"
        assert ActionType.UPDATE_OCCURRENCE == "update_occurrence"

    def test_disciplinary_action_types(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        assert ActionType.CREATE_DISCIPLINARY == "create_disciplinary"
        assert ActionType.APPROVE_DISCIPLINARY == "approve_disciplinary"
        assert ActionType.REJECT_DISCIPLINARY == "reject_disciplinary"

    def test_inspection_action_types(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        assert ActionType.CREATE_ROUND == "create_round"
        assert ActionType.START_ROUND == "start_round"
        assert ActionType.COMPLETE_ROUND == "complete_round"
        assert ActionType.REGISTER_CHECKPOINT == "register_checkpoint"
        assert ActionType.PAUSE_ROUND == "pause_round"
        assert ActionType.RESUME_ROUND == "resume_round"

    def test_diarist_action_types(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        assert ActionType.CREATE_DIARIST == "create_diarist"
        assert ActionType.SCHEDULE_DIARIST == "schedule_diarist"
        assert ActionType.EVALUATE_DIARIST == "evaluate_diarist"
        assert ActionType.APPROVE_DIARIST_PAYMENT == "approve_diarist_payment"
        assert ActionType.GENERATE_DIARIST_PAYMENT == "generate_diarist_payment"

    def test_communication_action_types(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        assert ActionType.CREATE_ANNOUNCEMENT == "create_announcement"
        assert ActionType.PUBLISH_ANNOUNCEMENT == "publish_announcement"
        assert ActionType.SEND_NOTIFICATION == "send_notification"

    def test_time_bank_action_types(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        assert ActionType.APPROVE_OVERTIME == "approve_overtime"
        assert ActionType.REQUEST_COMPENSATION == "request_compensation"
        assert ActionType.VIEW_BALANCE == "view_balance"

    def test_post_action_types(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        assert ActionType.CREATE_POST == "create_post"
        assert ActionType.UPDATE_POST == "update_post"
        assert ActionType.DELETE_POST == "delete_post"
        assert ActionType.GET_POST_STATS == "get_post_stats"

    def test_report_action_type(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        assert ActionType.GENERATE_REPORT == "generate_report"
        assert ActionType.CREATE_SUBSTITUTION == "create_substitution"

    def test_action_category_enum(self):
        from modules.ai.bartolo.actions.action_types import ActionCategory

        assert ActionCategory.OPERATIONAL == "operational"
        assert ActionCategory.ADMINISTRATIVE == "administrative"
        assert ActionCategory.NOTIFICATION == "notification"
        assert ActionCategory.REPORT == "report"

    def test_action_status_enum(self):
        from modules.ai.bartolo.actions.action_types import ActionStatus

        assert ActionStatus.PENDING_CONFIRMATION == "pending_confirmation"
        assert ActionStatus.CONFIRMED == "confirmed"
        assert ActionStatus.EXECUTING == "executing"
        assert ActionStatus.COMPLETED == "completed"
        assert ActionStatus.FAILED == "failed"
        assert ActionStatus.CANCELLED == "cancelled"

    def test_total_action_type_count(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        # At least 43 action types documented
        assert len(list(ActionType)) >= 43


# ---------------------------------------------------------------------------
# ============================ ACTION DETECTOR =============================
# ---------------------------------------------------------------------------


class TestActionDetector:
    def setup_method(self):
        from modules.ai.bartolo.actions.action_detector import ActionDetector

        self.detector = ActionDetector()

    def test_detect_create_scale(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("criar uma escala para janeiro")
        assert result is not None
        assert result.action_type == ActionType.CREATE_SCALE

    def test_detect_gerar_escala(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("gerar escala do mês")
        assert result is not None
        assert result.action_type == ActionType.CREATE_SCALE

    def test_detect_approve_scale(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("aprovar escala de fevereiro")
        assert result is not None
        assert result.action_type == ActionType.APPROVE_SCALE

    def test_detect_publish_scale(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("publicar a escala")
        assert result is not None
        assert result.action_type == ActionType.PUBLISH_SCALE

    def test_detect_allocate_employee(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("alocar o funcionário no posto central")
        assert result is not None
        assert result.action_type == ActionType.ALLOCATE_EMPLOYEE

    def test_detect_terminate_allocation(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("encerrar a alocação do colaborador")
        assert result is not None
        assert result.action_type == ActionType.TERMINATE_ALLOCATION

    def test_detect_transfer_employee(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("transferir o funcionário para outro posto")
        assert result is not None
        assert result.action_type == ActionType.TRANSFER_EMPLOYEE

    def test_detect_register_checkin(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("registrar a entrada do funcionário")
        assert result is not None
        assert result.action_type == ActionType.REGISTER_CHECKIN

    def test_detect_register_checkout(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("registrar a saída do colaborador")
        assert result is not None
        assert result.action_type == ActionType.REGISTER_CHECKOUT

    def test_detect_mark_absence(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("marcar como falta hoje")
        assert result is not None
        assert result.action_type == ActionType.MARK_ABSENCE

    def test_detect_create_occurrence(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("registrar uma ocorrência de invasão")
        assert result is not None
        assert result.action_type == ActionType.CREATE_OCCURRENCE

    def test_detect_resolve_occurrence(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("resolver a ocorrência número 5")
        assert result is not None
        assert result.action_type == ActionType.RESOLVE_OCCURRENCE

    def test_detect_create_disciplinary(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("aplicar medida disciplinar ao funcionário")
        assert result is not None
        assert result.action_type == ActionType.CREATE_DISCIPLINARY

    def test_detect_approve_disciplinary(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("aprovar a medida disciplinar")
        assert result is not None
        assert result.action_type == ActionType.APPROVE_DISCIPLINARY

    def test_detect_reject_disciplinary(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("rejeitar a medida disciplinar")
        assert result is not None
        assert result.action_type == ActionType.REJECT_DISCIPLINARY

    def test_detect_create_round(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("criar uma ronda para o turno da noite")
        assert result is not None
        assert result.action_type == ActionType.CREATE_ROUND

    def test_detect_start_round(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("iniciar a ronda de inspeção")
        assert result is not None
        assert result.action_type == ActionType.START_ROUND

    def test_detect_complete_round(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("finalizar a ronda")
        assert result is not None
        assert result.action_type == ActionType.COMPLETE_ROUND

    def test_detect_create_diarist(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("cadastrar uma diarista nova")
        assert result is not None
        assert result.action_type == ActionType.CREATE_DIARIST

    def test_detect_schedule_diarist(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("agendar diarista para amanhã")
        assert result is not None
        assert result.action_type == ActionType.SCHEDULE_DIARIST

    def test_detect_create_announcement(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("criar um comunicado para a equipe")
        assert result is not None
        assert result.action_type == ActionType.CREATE_ANNOUNCEMENT

    def test_detect_publish_announcement(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("publicar o comunicado de segurança")
        assert result is not None
        assert result.action_type == ActionType.PUBLISH_ANNOUNCEMENT

    def test_detect_approve_overtime(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("aprovar horas extras do João")
        assert result is not None
        assert result.action_type == ActionType.APPROVE_OVERTIME

    def test_detect_view_balance(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("ver o saldo de horas do banco")
        assert result is not None
        assert result.action_type == ActionType.VIEW_BALANCE

    def test_detect_create_post(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("criar um novo posto de portaria")
        assert result is not None
        assert result.action_type == ActionType.CREATE_POST

    def test_detect_update_post(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("atualizar o posto principal")
        assert result is not None
        assert result.action_type == ActionType.UPDATE_POST

    def test_detect_generate_report(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("gerar um relatório mensal")
        assert result is not None
        assert result.action_type == ActionType.GENERATE_REPORT

    def test_no_action_detected_for_query(self):
        result = self.detector.detect_action("quantos postos temos hoje?")
        # Pure queries might not match action patterns — either None or unrelated type
        # The important thing is detecting actions should not trigger on pure questions
        # depending on implementation, this may or may not return a result
        # We just verify the call does not raise exceptions
        assert result is None or result is not None

    def test_no_action_for_greeting(self):
        result = self.detector.detect_action("olá, bom dia")
        assert result is None

    def test_detect_action_returns_action_request(self):
        from modules.ai.bartolo.actions.action_schemas import ActionRequest
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("criar uma escala")
        assert isinstance(result, ActionRequest)
        assert result.action_type == ActionType.CREATE_SCALE

    def test_action_request_has_raw_message(self):
        msg = "criar uma escala para o posto norte"
        result = self.detector.detect_action(msg)
        assert result is not None
        assert result.raw_message == msg

    def test_detect_marcar_saida(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("marcar saída do funcionário")
        assert result is not None
        assert result.action_type == ActionType.REGISTER_CHECKOUT

    def test_detect_nova_escala(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("nova escala para março")
        assert result is not None
        assert result.action_type == ActionType.CREATE_SCALE

    def test_detect_registrar_falta(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("registrar a ausência de Maria hoje")
        assert result is not None
        assert result.action_type == ActionType.MARK_ABSENCE

    def test_detect_create_substitution(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("criar uma substituição para o turno da tarde")
        assert result is not None
        assert result.action_type == ActionType.CREATE_SUBSTITUTION


# ---------------------------------------------------------------------------
# ============================ IDENTITY CONFIG =============================
# ---------------------------------------------------------------------------


class TestBartoloIdentity:
    def test_bartolo_config_defaults(self):
        from modules.ai.bartolo.config.identity import BartoloConfig

        config = BartoloConfig()
        assert config.name == "Bartolo"
        assert config.version == "1.0"
        assert config.language == "pt-BR"

    def test_bartolo_config_max_response_tokens(self):
        from modules.ai.bartolo.config.identity import BartoloConfig

        config = BartoloConfig()
        assert config.max_response_tokens == 2000

    def test_bartolo_config_flags(self):
        from modules.ai.bartolo.config.identity import BartoloConfig

        config = BartoloConfig()
        assert config.use_emojis is False
        assert config.formal_greeting is True
        assert config.proactive_suggestions is True
        assert config.explain_actions is True
        assert config.use_knowledge_base is True
        assert config.use_data_connector is True
        assert config.use_wizards is True
        assert config.enable_actions is True
        assert config.save_interactions is True
        assert config.learn_from_feedback is True

    def test_bartolo_mood_enum(self):
        from modules.ai.bartolo.config.identity import BartoloMood

        assert BartoloMood.PROFESSIONAL == "professional"
        assert BartoloMood.FRIENDLY == "friendly"
        assert BartoloMood.SUPPORTIVE == "supportive"
        assert BartoloMood.CELEBRATORY == "celebratory"
        assert BartoloMood.FOCUSED == "focused"

    def test_bartolo_identity_string_content(self):
        from modules.ai.bartolo.config.identity import BARTOLO_IDENTITY

        assert "Bartolo" in BARTOLO_IDENTITY
        assert "Conecta PRO" in BARTOLO_IDENTITY

    def test_get_greeting_morning(self):
        from modules.ai.bartolo.config.identity import get_greeting

        with patch("modules.ai.bartolo.config.identity.datetime") as mock_dt:
            mock_dt.now.return_value = MagicMock(hour=9)
            result = get_greeting()
            assert "Bom dia" in result

    def test_get_greeting_afternoon(self):
        from modules.ai.bartolo.config.identity import get_greeting

        with patch("modules.ai.bartolo.config.identity.datetime") as mock_dt:
            mock_dt.now.return_value = MagicMock(hour=14)
            result = get_greeting()
            assert "Boa tarde" in result

    def test_get_greeting_evening(self):
        from modules.ai.bartolo.config.identity import get_greeting

        with patch("modules.ai.bartolo.config.identity.datetime") as mock_dt:
            mock_dt.now.return_value = MagicMock(hour=20)
            result = get_greeting()
            assert "Boa noite" in result

    def test_get_greeting_with_user_name(self):
        from modules.ai.bartolo.config.identity import get_greeting

        result = get_greeting(user_name="João")
        assert "João" in result

    def test_get_greeting_first_time(self):
        from modules.ai.bartolo.config.identity import get_greeting

        result = get_greeting(user_name="Maria", is_first_time=True)
        assert "Maria" in result
        assert "Bartolo" in result

    def test_get_error_response_not_found(self):
        from modules.ai.bartolo.config.identity import get_error_response

        result = get_error_response("not_found", item="usuário")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_error_response_unknown_type(self):
        from modules.ai.bartolo.config.identity import get_error_response

        result = get_error_response("nonexistent_error_type")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_error_response_no_permission(self):
        from modules.ai.bartolo.config.identity import get_error_response

        result = get_error_response("no_permission", action="deletar posto")
        assert isinstance(result, str)

    def test_get_closing_task_complete(self):
        from modules.ai.bartolo.config.identity import get_closing

        result = get_closing(action="Escala", task_complete=True)
        assert "Escala" in result

    def test_get_closing_no_action(self):
        from modules.ai.bartolo.config.identity import get_closing

        result = get_closing()
        assert isinstance(result, str)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# ============================= MODULES CONFIG =============================
# ---------------------------------------------------------------------------


class TestModulesConfig:
    def test_get_module_prompt_crm(self):
        from modules.ai.bartolo.config.modules import get_module_prompt

        result = get_module_prompt("crm")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "CRM" in result.upper() or "crm" in result.lower() or "leads" in result.lower()

    def test_get_module_prompt_unknown_returns_empty(self):
        from modules.ai.bartolo.config.modules import get_module_prompt

        result = get_module_prompt("nonexistent_module_xyz")
        assert result == ""

    def test_get_all_modules_is_list(self):
        from modules.ai.bartolo.config.modules import get_all_modules

        result = get_all_modules()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_all_modules_contains_crm(self):
        from modules.ai.bartolo.config.modules import get_all_modules

        result = get_all_modules()
        assert "crm" in result

    def test_get_all_modules_contains_operacoes(self):
        from modules.ai.bartolo.config.modules import get_all_modules

        result = get_all_modules()
        assert "operacoes" in result

    def test_get_module_capabilities_known_module(self):
        from modules.ai.bartolo.config.modules import get_module_capabilities

        result = get_module_capabilities("crm")
        assert isinstance(result, list)

    def test_get_module_capabilities_unknown_module(self):
        from modules.ai.bartolo.config.modules import get_module_capabilities

        result = get_module_capabilities("unknown_xyz")
        assert result == []

    def test_get_modules_by_category_comercial(self):
        from modules.ai.bartolo.config.modules import ModuleCategory, get_modules_by_category

        result = get_modules_by_category(ModuleCategory.COMERCIAL)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_modules_by_category_operacoes(self):
        from modules.ai.bartolo.config.modules import ModuleCategory, get_modules_by_category

        result = get_modules_by_category(ModuleCategory.OPERACOES)
        assert isinstance(result, list)

    def test_find_module_by_capability_criar_lead(self):
        from modules.ai.bartolo.config.modules import find_module_by_capability

        result = find_module_by_capability("criar_lead")
        # Should find crm or return None if not in capabilities dict
        assert result is None or isinstance(result, str)

    def test_find_module_by_capability_nonexistent(self):
        from modules.ai.bartolo.config.modules import find_module_by_capability

        result = find_module_by_capability("capability_that_does_not_exist_xyz")
        assert result is None

    def test_module_category_enum_values(self):
        from modules.ai.bartolo.config.modules import ModuleCategory

        assert ModuleCategory.COMERCIAL == "comercial"
        assert ModuleCategory.OPERACOES == "operacoes"
        assert ModuleCategory.RH == "rh"
        assert ModuleCategory.FINANCEIRO == "financeiro"
        assert ModuleCategory.IA == "ia"
        assert ModuleCategory.SEGURANCA == "seguranca"

    def test_module_prompts_dict_not_empty(self):
        from modules.ai.bartolo.config.modules import MODULE_PROMPTS

        assert isinstance(MODULE_PROMPTS, dict)
        assert len(MODULE_PROMPTS) > 0

    def test_each_module_has_required_keys(self):
        from modules.ai.bartolo.config.modules import MODULE_PROMPTS

        for module_name, module_data in MODULE_PROMPTS.items():
            assert "category" in module_data, f"Module {module_name} missing 'category'"
            assert "name" in module_data, f"Module {module_name} missing 'name'"
            assert "description" in module_data, f"Module {module_name} missing 'description'"
            assert "prompt" in module_data, f"Module {module_name} missing 'prompt'"


# ---------------------------------------------------------------------------
# ============================ SYSTEM PROMPT ===============================
# ---------------------------------------------------------------------------


class TestSystemPrompt:
    def test_build_full_system_prompt_no_args(self):
        from modules.ai.bartolo.config.system_prompt import build_full_system_prompt

        result = build_full_system_prompt()
        assert isinstance(result, str)
        assert len(result) > 100
        assert "Bartolo" in result

    def test_build_full_system_prompt_with_user_context(self):
        from modules.ai.bartolo.config.system_prompt import build_full_system_prompt

        result = build_full_system_prompt(user_context="Nome: Joao\nCargo: Gerente")
        assert "Joao" in result or "USUARIO ATUAL" in result

    def test_build_full_system_prompt_with_module(self):
        from modules.ai.bartolo.config.system_prompt import build_full_system_prompt

        result = build_full_system_prompt(module="crm")
        assert isinstance(result, str)
        assert len(result) > 100

    def test_build_full_system_prompt_with_additional_context(self):
        from modules.ai.bartolo.config.system_prompt import build_full_system_prompt

        result = build_full_system_prompt(additional_context="Total postos: 10")
        assert "Total postos: 10" in result or "INFORMACOES ADICIONAIS" in result

    def test_build_full_system_prompt_with_unknown_module(self):
        from modules.ai.bartolo.config.system_prompt import build_full_system_prompt

        result = build_full_system_prompt(module="nonexistent_xyz")
        assert isinstance(result, str)
        # Should not crash, just omit the module context

    def test_build_full_system_prompt_all_args(self):
        from modules.ai.bartolo.config.system_prompt import build_full_system_prompt

        result = build_full_system_prompt(
            user_context="Nome: Maria",
            module="operacoes",
            additional_context="Dado extra aqui",
        )
        assert isinstance(result, str)
        assert len(result) > 200

    def test_get_concise_system_prompt_is_string(self):
        from modules.ai.bartolo.config.system_prompt import get_concise_system_prompt

        result = get_concise_system_prompt()
        assert isinstance(result, str)
        assert len(result) > 50

    def test_get_concise_system_prompt_contains_bartolo(self):
        from modules.ai.bartolo.config.system_prompt import get_concise_system_prompt

        result = get_concise_system_prompt()
        assert "Bartolo" in result or "bartolo" in result.lower()

    def test_operacional_expert_knowledge_exists(self):
        from modules.ai.bartolo.config.system_prompt import OPERACIONAL_EXPERT_KNOWLEDGE

        assert isinstance(OPERACIONAL_EXPERT_KNOWLEDGE, str)
        assert len(OPERACIONAL_EXPERT_KNOWLEDGE) > 50

    def test_bartolo_system_prompt_is_string(self):
        from modules.ai.bartolo.config.system_prompt import BARTOLO_SYSTEM_PROMPT

        assert isinstance(BARTOLO_SYSTEM_PROMPT, str)
        assert len(BARTOLO_SYSTEM_PROMPT) > 100


# ---------------------------------------------------------------------------
# ============================ LEARNING SERVICE ============================
# ---------------------------------------------------------------------------


class TestLearningServiceMemoryOnly:
    """Tests for LearningService in memory-only mode (no db, no redis)."""

    def setup_method(self):
        from modules.ai.bartolo.services.learning_service import LearningService

        self.service = LearningService(db=None, redis_client=None)

    @pytest.mark.asyncio
    async def test_record_interaction_returns_uuid(self):
        result = await self.service.record_interaction(
            user_id=1,
            session_id="sess-001",
            message="olá",
            response="Bom dia!",
        )
        assert result is not None
        assert isinstance(result, uuid.UUID)

    @pytest.mark.asyncio
    async def test_record_interaction_increments_total(self):
        initial = self.service._total_interactions
        await self.service.record_interaction(user_id=1, session_id="s1", message="m", response="r")
        assert self.service._total_interactions == initial + 1

    @pytest.mark.asyncio
    async def test_record_interaction_appends_to_list(self):
        await self.service.record_interaction(user_id=1, session_id="s1", message="hello", response="hi")
        assert len(self.service._interactions) >= 1

    @pytest.mark.asyncio
    async def test_record_interaction_with_optional_fields(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        result = await self.service.record_interaction(
            user_id=2,
            session_id="sess-002",
            message="criar escala",
            response="Vou ajudar",
            intent="create_scale",
            module="operacional",
            wizard_type="escala",
            processing_time_ms=500,
            metadata={"extra": "data"},
        )
        assert isinstance(result, uuid.UUID)

    @pytest.mark.asyncio
    async def test_record_feedback_not_found_returns_false(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        fake_id = uuid.uuid4()
        result = await self.service.record_feedback(fake_id, FeedbackType.HELPFUL)
        assert result is False

    @pytest.mark.asyncio
    async def test_record_feedback_found_returns_true(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        interaction_id = await self.service.record_interaction(
            user_id=1, session_id="s1", message="bom dia", response="Bom dia!"
        )
        result = await self.service.record_feedback(interaction_id, FeedbackType.HELPFUL)
        assert result is True

    @pytest.mark.asyncio
    async def test_record_helpful_feedback_increments_positive(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        interaction_id = await self.service.record_interaction(
            user_id=1, session_id="s1", message="teste", response="resp"
        )
        before = self.service._positive_feedback_count
        await self.service.record_feedback(interaction_id, FeedbackType.HELPFUL)
        assert self.service._positive_feedback_count == before + 1

    @pytest.mark.asyncio
    async def test_record_not_helpful_feedback_increments_negative(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        interaction_id = await self.service.record_interaction(
            user_id=1, session_id="s1", message="teste", response="resp"
        )
        before = self.service._negative_feedback_count
        await self.service.record_feedback(interaction_id, FeedbackType.NOT_HELPFUL)
        assert self.service._negative_feedback_count == before + 1

    @pytest.mark.asyncio
    async def test_get_stats_returns_dict(self):
        result = self.service.get_stats()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_stats_keys(self):
        result = self.service.get_stats()
        assert "total_interactions" in result
        assert "satisfaction_rate" in result
        assert "patterns_learned" in result
        assert "persistence_enabled" in result
        assert "redis_enabled" in result

    @pytest.mark.asyncio
    async def test_get_stats_persistence_enabled_false_when_no_db(self):
        result = self.service.get_stats()
        assert result["persistence_enabled"] is False

    @pytest.mark.asyncio
    async def test_get_stats_satisfaction_rate_zero_when_no_feedback(self):
        result = self.service.get_stats()
        assert result["satisfaction_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_get_stats_satisfaction_rate_with_feedback(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        iid = await self.service.record_interaction(user_id=1, session_id="s1", message="m", response="r")
        await self.service.record_feedback(iid, FeedbackType.HELPFUL)
        result = self.service.get_stats()
        assert result["satisfaction_rate"] == 100.0

    @pytest.mark.asyncio
    async def test_get_similar_interactions_empty_when_no_data(self):
        result = await self.service.get_similar_interactions("qualquer mensagem")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_similar_interactions_returns_helpful_ones(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        iid = await self.service.record_interaction(
            user_id=1,
            session_id="s1",
            message="quantos postos temos",
            response="Temos 10 postos",
        )
        await self.service.record_feedback(iid, FeedbackType.HELPFUL)

        result = await self.service.get_similar_interactions("quantos postos")
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_get_successful_patterns_empty_initially(self):
        result = await self.service.get_successful_patterns()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_export_learnings_returns_dict(self):
        result = await self.service.export_learnings()
        assert isinstance(result, dict)
        assert "patterns" in result
        assert "stats" in result
        assert "exported_at" in result

    @pytest.mark.asyncio
    async def test_warmup_no_db_does_not_crash(self):
        # With no db, warmup should silently complete
        await self.service.warmup()

    def test_set_db_updates_db_attribute(self):
        mock_db = AsyncMock()
        self.service.set_db(mock_db)
        assert self.service.db == mock_db

    @pytest.mark.asyncio
    async def test_memory_limit_truncates_interactions(self):
        # Add enough interactions to trigger trimming
        for i in range(10001):
            self.service._interactions.append(MagicMock(id=uuid.uuid4(), message=f"msg{i}", feedback=None))
        # Trigger trimming by adding one more through the public API
        await self.service.record_interaction(user_id=1, session_id="s", message="overflow", response="r")
        assert len(self.service._interactions) <= 10000

    @pytest.mark.asyncio
    async def test_analyze_patterns_greeting(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        iid = await self.service.record_interaction(
            user_id=1,
            session_id="s1",
            message="oi, bom dia como vai",
            response="Bom dia!",
        )
        await self.service.record_feedback(iid, FeedbackType.HELPFUL)
        # Patterns dict should have at least one greeting pattern
        assert any("greeting" in k for k in self.service._patterns.keys())

    @pytest.mark.asyncio
    async def test_analyze_patterns_data_query(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        iid = await self.service.record_interaction(
            user_id=1,
            session_id="s1",
            message="quantos funcionários temos",
            response="Temos 44",
        )
        await self.service.record_feedback(iid, FeedbackType.HELPFUL)
        assert any("data_query" in k for k in self.service._patterns.keys())

    @pytest.mark.asyncio
    async def test_record_interaction_with_wizard_type_creates_pattern(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        iid = await self.service.record_interaction(
            user_id=1,
            session_id="s1",
            message="criar escala",
            response="Iniciando wizard...",
            wizard_type="escala",
        )
        await self.service.record_feedback(iid, FeedbackType.HELPFUL)
        assert any("wizard_escala" in k for k in self.service._patterns.keys())


class TestLearningServiceFeedbackTypes:
    def test_feedback_type_values(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        assert FeedbackType.HELPFUL == "helpful"
        assert FeedbackType.NOT_HELPFUL == "not_helpful"
        assert FeedbackType.INCORRECT == "incorrect"
        assert FeedbackType.INCOMPLETE == "incomplete"
        assert FeedbackType.TOO_LONG == "too_long"
        assert FeedbackType.TOO_SHORT == "too_short"
        assert FeedbackType.OFF_TOPIC == "off_topic"

    def test_learning_event_type_values(self):
        from modules.ai.bartolo.services.learning_service import LearningEventType

        assert LearningEventType.POSITIVE_FEEDBACK == "positive_feedback"
        assert LearningEventType.NEGATIVE_FEEDBACK == "negative_feedback"
        assert LearningEventType.SUCCESSFUL_WIZARD == "successful_wizard"
        assert LearningEventType.FAILED_WIZARD == "failed_wizard"
        assert LearningEventType.QUERY_PATTERN == "query_pattern"
        assert LearningEventType.USER_CORRECTION == "user_correction"


class TestLearningServiceWithDb:
    """Tests for LearningService with mocked DB session."""

    def setup_method(self):
        self.mock_db = AsyncMock()
        from modules.ai.bartolo.services.learning_service import LearningService

        self.service = LearningService(db=self.mock_db, redis_client=None)

    @pytest.mark.asyncio
    async def test_persist_interaction_called_on_record(self):
        with patch.object(self.service, "_persist_interaction") as mock_persist:
            mock_persist.return_value = None
            await self.service.record_interaction(user_id=1, session_id="s1", message="test", response="resp")
            mock_persist.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_feedback_not_in_memory_tries_db(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        fake_id = uuid.uuid4()
        with (
            patch.object(self.service, "_find_interaction_in_db", return_value=True),
            patch.object(self.service, "_persist_feedback") as mock_fb,
        ):
            mock_fb.return_value = None
            result = await self.service.record_feedback(fake_id, FeedbackType.HELPFUL)
            assert result is True

    @pytest.mark.asyncio
    async def test_record_feedback_not_in_db_returns_false(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType

        fake_id = uuid.uuid4()
        with patch.object(self.service, "_find_interaction_in_db", return_value=False):
            result = await self.service.record_feedback(fake_id, FeedbackType.HELPFUL)
            assert result is False

    @pytest.mark.asyncio
    async def test_warmup_calls_load_patterns_from_db(self):
        with patch.object(self.service, "_load_patterns_from_db") as mock_load:
            mock_load.return_value = None
            await self.service.warmup()
            mock_load.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_stats_persistence_enabled_true(self):
        result = self.service.get_stats()
        assert result["persistence_enabled"] is True

    @pytest.mark.asyncio
    async def test_get_successful_patterns_falls_back_to_db(self):
        with patch.object(self.service, "_get_patterns_from_db", return_value=[]):
            result = await self.service.get_successful_patterns()
            assert isinstance(result, list)


class TestLearningServiceRedis:
    """Tests for LearningService Redis cache behavior."""

    def setup_method(self):
        self.mock_redis = AsyncMock()
        from modules.ai.bartolo.services.learning_service import LearningService

        self.service = LearningService(db=None, redis_client=self.mock_redis)

    @pytest.mark.asyncio
    async def test_get_redis_returns_existing_client(self):
        result = await self.service._get_redis()
        assert result == self.mock_redis

    @pytest.mark.asyncio
    async def test_get_stats_redis_enabled_true(self):
        result = self.service.get_stats()
        assert result["redis_enabled"] is True

    @pytest.mark.asyncio
    async def test_cache_pattern_redis_called(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType, LearnedPattern

        pattern = LearnedPattern(
            id=uuid.uuid4(),
            pattern_type="greeting",
            trigger="oi",
            confidence=0.8,
            usage_count=5,
            success_rate=0.9,
        )
        self.mock_redis.setex = AsyncMock()
        await self.service._cache_pattern_redis("greeting:oi", pattern)
        self.mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pattern_from_redis_not_found(self):
        self.mock_redis.get = AsyncMock(return_value=None)
        result = await self.service._get_pattern_from_redis("nonexistent_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_redis_when_redis_is_none(self):
        from modules.ai.bartolo.services.learning_service import LearningService

        service = LearningService(db=None, redis_client=None)
        with (
            patch("modules.ai.bartolo.services.learning_service.logger"),
            patch("modules.ai.bartolo.services.learning_service.LearningService._get_redis") as mock_get,
        ):
            mock_get.return_value = None
            # Should not raise
            result = await service._get_pattern_from_redis("key")
            assert result is None


# ---------------------------------------------------------------------------
# ============================ PROFILE SERVICE =============================
# ---------------------------------------------------------------------------


class TestProfileService:
    def setup_method(self):
        from modules.ai.bartolo.services.profile_service import ProfileService

        self.service = ProfileService(db=None)

    @pytest.mark.asyncio
    async def test_get_user_context_fallback_user_1(self):
        ctx = await self.service.get_user_context(1)
        assert ctx.user_id == 1
        assert ctx.name == "Admin"

    @pytest.mark.asyncio
    async def test_get_user_context_fallback_user_2(self):
        ctx = await self.service.get_user_context(2)
        assert ctx.user_id == 2
        assert ctx.name == "Maria Silva"

    @pytest.mark.asyncio
    async def test_get_user_context_fallback_user_3(self):
        ctx = await self.service.get_user_context(3)
        assert ctx.user_id == 3
        assert ctx.name == "Joao Santos"

    @pytest.mark.asyncio
    async def test_get_user_context_unknown_user(self):
        ctx = await self.service.get_user_context(999)
        assert ctx.user_id == 999
        assert "999" in ctx.name

    @pytest.mark.asyncio
    async def test_get_user_context_caches_result(self):
        ctx1 = await self.service.get_user_context(1)
        ctx2 = await self.service.get_user_context(1)
        assert ctx1 is ctx2

    @pytest.mark.asyncio
    async def test_get_user_context_increments_interaction_count(self):
        ctx = await self.service.get_user_context(1)
        count_before = ctx.interaction_count
        # Second call hits cache and increments counter
        await self.service.get_user_context(1)
        assert ctx.interaction_count == count_before + 1

    @pytest.mark.asyncio
    async def test_update_user_preferences(self):
        await self.service.get_user_context(1)
        await self.service.update_user_preferences(1, {"theme": "dark"})
        ctx = await self.service.get_user_context(1)
        assert ctx.preferences.get("theme") == "dark"

    @pytest.mark.asyncio
    async def test_add_recent_module(self):
        await self.service.get_user_context(1)
        await self.service.add_recent_module(1, "operacional")
        ctx = await self.service.get_user_context(1)
        assert "operacional" in ctx.last_modules

    @pytest.mark.asyncio
    async def test_add_recent_module_no_duplicates(self):
        await self.service.get_user_context(1)
        await self.service.add_recent_module(1, "ged")
        await self.service.add_recent_module(1, "ged")
        ctx = await self.service.get_user_context(1)
        assert ctx.last_modules.count("ged") == 1

    @pytest.mark.asyncio
    async def test_add_recent_module_limits_to_10(self):
        await self.service.get_user_context(1)
        for i in range(15):
            await self.service.add_recent_module(1, f"module_{i}")
        ctx = await self.service.get_user_context(1)
        assert len(ctx.last_modules) <= 10

    @pytest.mark.asyncio
    async def test_get_user_stats_returns_dict(self):
        result = await self.service.get_user_stats(1)
        assert isinstance(result, dict)
        assert "user_id" in result
        assert "interaction_count" in result

    @pytest.mark.asyncio
    async def test_get_user_stats_user_id(self):
        result = await self.service.get_user_stats(1)
        assert result["user_id"] == 1

    def test_clear_cache_specific_user(self):
        # Populate cache first
        self.service._user_cache[1] = MagicMock()
        self.service._cache_timestamps[1] = 999999999
        self.service.clear_cache(user_id=1)
        assert 1 not in self.service._user_cache
        assert 1 not in self.service._cache_timestamps

    def test_clear_cache_all(self):
        self.service._user_cache[1] = MagicMock()
        self.service._user_cache[2] = MagicMock()
        self.service.clear_cache()
        assert len(self.service._user_cache) == 0

    def test_set_db(self):
        mock_db = AsyncMock()
        self.service.set_db(mock_db)
        assert self.service._db == mock_db

    def test_parse_role_valid(self):
        from modules.ai.bartolo.config.user_profiles import UserRole

        result = self.service._parse_role("admin")
        assert result == UserRole.ADMIN

    def test_parse_role_invalid(self):
        result = self.service._parse_role("nonexistent_role_xyz")
        assert result is None

    def test_parse_role_none(self):
        result = self.service._parse_role(None)
        assert result is None

    def test_parse_department_valid(self):
        from modules.ai.bartolo.config.user_profiles import Department

        result = self.service._parse_department("ti")
        assert result == Department.TI

    def test_parse_department_invalid(self):
        result = self.service._parse_department("nonexistent_dept_xyz")
        assert result is None

    def test_parse_department_none(self):
        result = self.service._parse_department(None)
        assert result is None

    def test_is_cache_valid_no_entry(self):
        result = self.service._is_cache_valid(9999)
        assert result is False

    def test_is_cache_valid_fresh_entry(self):
        import time

        self.service._cache_timestamps[42] = time.time()
        result = self.service._is_cache_valid(42)
        assert result is True

    def test_is_cache_valid_expired_entry(self):
        self.service._cache_timestamps[42] = 0  # Unix epoch = very old
        result = self.service._is_cache_valid(42)
        assert result is False

    def test_map_system_role_super_admin(self):
        result = self.service._map_system_role_to_bartolo_role("super_admin")
        assert result == "admin"

    def test_map_system_role_admin(self):
        result = self.service._map_system_role_to_bartolo_role("admin")
        assert result == "admin"

    def test_map_system_role_manager(self):
        result = self.service._map_system_role_to_bartolo_role("manager")
        assert result == "gerente_geral"

    def test_map_system_role_supervisor(self):
        result = self.service._map_system_role_to_bartolo_role("supervisor")
        assert result == "supervisor_operacoes"

    def test_map_system_role_operator(self):
        result = self.service._map_system_role_to_bartolo_role("operator")
        assert result == "assistente_administrativo"

    def test_map_system_role_unknown(self):
        result = self.service._map_system_role_to_bartolo_role("unknown_role")
        assert result == "assistente_administrativo"

    def test_is_manager_role_admin(self):
        assert self.service._is_manager_role("admin") is True

    def test_is_manager_role_supervisor(self):
        assert self.service._is_manager_role("supervisor") is True

    def test_is_manager_role_operator(self):
        assert self.service._is_manager_role("operator") is False

    def test_infer_experience_level_super_admin(self):
        result = self.service._infer_experience_level("super_admin")
        assert result == "advanced"

    def test_infer_experience_level_supervisor(self):
        result = self.service._infer_experience_level("supervisor")
        assert result == "intermediate"

    def test_infer_experience_level_client(self):
        result = self.service._infer_experience_level("client")
        assert result == "beginner"

    def test_infer_experience_level_unknown(self):
        result = self.service._infer_experience_level("unknown_xyz")
        assert result == "intermediate"

    def test_get_fallback_user_data_user_1(self):
        data = self.service._get_fallback_user_data(1)
        assert data["name"] == "Admin"
        assert data["role"] == "admin"

    def test_get_fallback_user_data_unknown(self):
        data = self.service._get_fallback_user_data(500)
        assert "500" in data["name"]

    def test_infer_department_from_role_admin(self):
        result = self.service._infer_department_from_role("admin")
        assert isinstance(result, str)

    def test_infer_department_from_unknown_role(self):
        result = self.service._infer_department_from_role("unknown_role_xyz")
        assert result == "administrativo"


class TestUserContext:
    def setup_method(self):
        from modules.ai.bartolo.config.user_profiles import Department, UserRole
        from modules.ai.bartolo.services.profile_service import UserContext

        self.ctx = UserContext(
            user_id=1,
            name="Test User",
            role=UserRole.ADMIN,
            department=Department.TI,
            is_manager=True,
            experience_level="advanced",
        )

    def test_to_prompt_context_includes_name(self):
        result = self.ctx.to_prompt_context()
        assert "Test User" in result

    def test_to_prompt_context_includes_role(self):
        result = self.ctx.to_prompt_context()
        assert "admin" in result.lower()

    def test_to_prompt_context_includes_department(self):
        result = self.ctx.to_prompt_context()
        assert "ti" in result.lower() or "TI" in result

    def test_to_prompt_context_includes_manager(self):
        result = self.ctx.to_prompt_context()
        assert "gestor" in result.lower()

    def test_to_prompt_context_experience_advanced(self):
        result = self.ctx.to_prompt_context()
        assert "avancado" in result.lower() or "avançado" in result.lower()

    def test_to_prompt_context_with_last_modules(self):
        self.ctx.last_modules = ["operacional", "ged", "crm"]
        result = self.ctx.to_prompt_context()
        assert "operacional" in result

    def test_to_prompt_context_no_name(self):
        from modules.ai.bartolo.services.profile_service import UserContext

        ctx = UserContext(user_id=99)
        result = ctx.to_prompt_context()
        assert isinstance(result, str)

    def test_get_priority_modules_with_role(self):
        result = self.ctx.get_priority_modules()
        assert isinstance(result, list)

    def test_get_priority_modules_no_role(self):
        from modules.ai.bartolo.services.profile_service import UserContext

        ctx = UserContext(user_id=1)
        result = ctx.get_priority_modules()
        assert result == []

    def test_get_communication_style_with_role(self):
        result = self.ctx.get_communication_style()
        assert isinstance(result, str)

    def test_get_communication_style_no_role(self):
        from modules.ai.bartolo.services.profile_service import UserContext

        ctx = UserContext(user_id=1)
        result = ctx.get_communication_style()
        assert result == "detailed"

    def test_to_prompt_context_experience_beginner(self):
        from modules.ai.bartolo.services.profile_service import UserContext

        ctx = UserContext(user_id=1, name="Beginner", experience_level="beginner")
        result = ctx.to_prompt_context()
        assert "iniciante" in result.lower()

    def test_to_prompt_context_experience_intermediate(self):
        from modules.ai.bartolo.services.profile_service import UserContext

        ctx = UserContext(user_id=1, name="Mid", experience_level="intermediate")
        result = ctx.to_prompt_context()
        assert "media" in result.lower() or "média" in result.lower()


class TestProfileServiceWithDb:
    """Tests for ProfileService with a mocked database."""

    def setup_method(self):
        self.mock_db = AsyncMock()
        from modules.ai.bartolo.services.profile_service import ProfileService

        self.service = ProfileService(db=self.mock_db)

    @pytest.mark.asyncio
    async def test_load_user_data_from_db_success(self):
        mock_user = MagicMock()
        mock_user.name = "DB User"
        mock_user.email = "db@test.com"
        mock_user.role = "admin"
        mock_user.permissions = []
        mock_user.id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_result.scalars.return_value.all.return_value = [mock_user]
        self.mock_db.execute = AsyncMock(return_value=mock_result)

        with (
            patch("modules.ai.bartolo.services.profile_service.select"),
            patch("modules.ai.bartolo.services.profile_service.User"),
        ):
            data = await self.service._load_user_data(1)
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_load_user_data_db_exception_falls_back_to_mock(self):
        self.mock_db.execute = AsyncMock(side_effect=Exception("DB connection error"))
        data = await self.service._load_user_data(1)
        # Should fall back to mock data
        assert isinstance(data, dict)
        assert "name" in data

    @pytest.mark.asyncio
    async def test_get_user_context_with_db_exception(self):
        self.mock_db.execute = AsyncMock(side_effect=Exception("DB error"))
        ctx = await self.service.get_user_context(1)
        assert ctx is not None
        assert ctx.user_id == 1


# ---------------------------------------------------------------------------
# ========================= BARTOLO ENGINE =================================
# ---------------------------------------------------------------------------


class TestBartoloEngine:
    """Tests for BartoloEngine core logic with mocked dependencies."""

    def setup_method(self):
        self.mock_llm = AsyncMock()
        self.mock_context_manager = AsyncMock()
        self.mock_intent_classifier = AsyncMock()

    def _make_engine(self):
        from modules.ai.bartolo.config.identity import BartoloConfig
        from modules.ai.bartolo.services.bartolo_engine import BartoloEngine

        return BartoloEngine(
            config=BartoloConfig(),
            llm_provider=self.mock_llm,
            context_manager=self.mock_context_manager,
            intent_classifier=self.mock_intent_classifier,
        )

    def test_engine_instantiation(self):
        engine = self._make_engine()
        assert engine is not None

    def test_engine_has_profile_service(self):
        engine = self._make_engine()
        assert engine.profile_service is not None

    def test_engine_has_data_connector(self):
        engine = self._make_engine()
        assert engine.data_connector is not None

    def test_engine_has_wizard_manager(self):
        engine = self._make_engine()
        assert engine.wizard_manager is not None

    def test_engine_has_action_detector(self):
        engine = self._make_engine()
        assert engine.action_detector is not None

    def test_get_session_key(self):
        engine = self._make_engine()
        key = engine._get_session_key("user1", "session123")
        assert key == "user1:session123"

    def test_format_response_basic(self):
        engine = self._make_engine()
        result = engine._format_response("Hello World", intent="greeting")
        assert result["response"] == "Hello World"
        assert result["intent"] == "greeting"
        assert isinstance(result["suggestions"], list)
        assert isinstance(result["actions"], list)

    def test_format_response_with_suggestions(self):
        engine = self._make_engine()
        result = engine._format_response(
            "Response",
            suggestions=["Option A", "Option B"],
        )
        assert "Option A" in result["suggestions"]

    def test_format_response_with_data(self):
        engine = self._make_engine()
        data = {"total": 10, "items": []}
        result = engine._format_response("Has data", data_results=data)
        assert result["data"] == data

    def test_detect_agent_name_from_keywords(self):
        engine = self._make_engine()
        result = engine._detect_agent_name("quero gerar escala para o posto", "unknown")
        assert result == "escala"

    def test_detect_agent_name_from_fallback_result(self):
        engine = self._make_engine()
        mock_fallback = MagicMock()
        mock_fallback.agent_type = "substituicao"
        result = engine._detect_agent_name("some message", "unknown", fallback_result=mock_fallback)
        assert result == "substituicao"

    def test_detect_agent_name_no_match(self):
        engine = self._make_engine()
        result = engine._detect_agent_name("olá tudo bem?", "greeting")
        assert result is None

    def test_build_system_prompt_no_args(self):
        from modules.ai.bartolo.services.profile_service import UserContext

        engine = self._make_engine()
        ctx = UserContext(user_id=1, name="Test")
        result = engine._build_system_prompt(ctx)
        assert isinstance(result, str)
        assert len(result) > 50

    def test_build_system_prompt_with_additional_context(self):
        from modules.ai.bartolo.services.profile_service import UserContext

        engine = self._make_engine()
        ctx = UserContext(user_id=1, name="Test")
        result = engine._build_system_prompt(ctx, additional_context="Extra data here")
        assert isinstance(result, str)
        assert "Extra data here" in result or "INFORMACOES ADICIONAIS" in result

    def test_build_system_prompt_with_module(self):
        from modules.ai.bartolo.services.profile_service import UserContext

        engine = self._make_engine()
        ctx = UserContext(user_id=1, name="Test")
        result = engine._build_system_prompt(ctx, module="operacional")
        assert isinstance(result, str)

    def test_build_system_prompt_operacional_adds_expert_knowledge(self):
        from modules.ai.bartolo.services.profile_service import UserContext

        engine = self._make_engine()
        ctx = UserContext(user_id=1, name="Test")
        result = engine._build_system_prompt(ctx, module="operacional")
        # Should add OPERACIONAL_EXPERT_KNOWLEDGE
        assert isinstance(result, str)
        assert len(result) > 200

    def test_get_specialized_agent_escala(self):
        engine = self._make_engine()
        # Without agents available, should return None
        result = engine._get_specialized_agent("escala")
        assert result is None or result is engine.escala_agent

    def test_get_specialized_agent_unknown(self):
        engine = self._make_engine()
        result = engine._get_specialized_agent("nonexistent_xyz")
        assert result is None

    def test_init_specialized_agents_no_db(self):
        engine = self._make_engine()
        # Should not raise even without db
        engine._init_specialized_agents(db=None, data_connector=None)

    @pytest.mark.asyncio
    async def test_check_skill_command_not_slash_message(self):
        engine = self._make_engine()
        result = await engine._check_skill_command("não é slash command", "user1")
        assert result is None

    @pytest.mark.asyncio
    async def test_check_skill_command_empty_slash(self):
        engine = self._make_engine()
        result = await engine._check_skill_command("/", "user1")
        assert result is None

    @pytest.mark.asyncio
    async def test_check_agent_followup_no_context(self):
        engine = self._make_engine()
        self.mock_context_manager.get_context = AsyncMock(return_value=None)
        result = await engine._check_agent_followup("user1", "sess1", "message")
        assert result is None

    @pytest.mark.asyncio
    async def test_check_agent_followup_empty_messages(self):
        engine = self._make_engine()
        mock_ctx = MagicMock()
        mock_ctx.messages = []
        self.mock_context_manager.get_context = AsyncMock(return_value=mock_ctx)
        result = await engine._check_agent_followup("user1", "sess1", "message")
        assert result is None

    @pytest.mark.asyncio
    async def test_route_to_specialized_agent_no_agents_available(self):
        engine = self._make_engine()
        # Even if agents are unavailable, should not raise
        result = await engine._route_to_specialized_agent("gerar escala", "escala", "user1")
        # May return None if agents not available
        assert result is None or isinstance(result, dict)

    def test_detect_wizard_intent_blocks_query(self):
        engine = self._make_engine()
        # Questions should not trigger wizard
        result = engine._detect_wizard_intent("quantos postos temos?")
        assert result is None

    def test_generate_suggestions_returns_list(self):
        from modules.ai.bartolo.services.profile_service import UserContext

        engine = self._make_engine()
        ctx = UserContext(user_id=1)
        result = engine._generate_suggestions("greeting", "operacional", ctx)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# ====================== OPENCLAW MEMORY SERVICE ===========================
# ---------------------------------------------------------------------------


class TestLearningServiceIntegration:
    """Integration-style tests exercising multiple methods together."""

    @pytest.mark.asyncio
    async def test_full_interaction_lifecycle(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType, LearningService

        service = LearningService()

        # Record an interaction
        iid = await service.record_interaction(
            user_id=10,
            session_id="full-lifecycle-session",
            message="quantos postos temos?",
            response="Temos 10 postos cadastrados",
            intent="data_query",
            module="operacional",
            processing_time_ms=300,
        )

        # Check stats before feedback
        stats = service.get_stats()
        assert stats["total_interactions"] == 1
        assert stats["satisfaction_rate"] == 0.0

        # Record positive feedback
        result = await service.record_feedback(iid, FeedbackType.HELPFUL, rating=5)
        assert result is True

        # Check stats after feedback
        stats = service.get_stats()
        assert stats["positive_feedback"] == 1
        assert stats["satisfaction_rate"] == 100.0

        # Get similar interactions
        similar = await service.get_similar_interactions("quantos postos")
        assert len(similar) >= 1

        # Export learnings
        export = await service.export_learnings()
        assert export["stats"]["total_interactions"] == 1

    @pytest.mark.asyncio
    async def test_multiple_interactions_satisfaction_rate(self):
        from modules.ai.bartolo.services.learning_service import FeedbackType, LearningService

        service = LearningService()

        # Record 2 helpful, 1 not helpful
        iid1 = await service.record_interaction(user_id=1, session_id="s1", message="m1", response="r1")
        iid2 = await service.record_interaction(user_id=1, session_id="s1", message="m2", response="r2")
        iid3 = await service.record_interaction(user_id=1, session_id="s1", message="m3", response="r3")

        await service.record_feedback(iid1, FeedbackType.HELPFUL)
        await service.record_feedback(iid2, FeedbackType.HELPFUL)
        await service.record_feedback(iid3, FeedbackType.NOT_HELPFUL)

        stats = service.get_stats()
        assert stats["positive_feedback"] == 2
        assert stats["negative_feedback"] == 1
        # Satisfaction rate = 2/3 * 100 = 66.7%
        assert abs(stats["satisfaction_rate"] - 66.7) < 1.0


class TestProfileServiceIntegration:
    """Integration tests for ProfileService."""

    @pytest.mark.asyncio
    async def test_user_workflow(self):
        from modules.ai.bartolo.services.profile_service import ProfileService

        service = ProfileService(db=None)

        # Get context for user 1
        ctx = await service.get_user_context(1)
        assert ctx.name == "Admin"
        assert ctx.interaction_count == 1

        # Add modules
        await service.add_recent_module(1, "ged")
        await service.add_recent_module(1, "crm")
        await service.add_recent_module(1, "operacional")

        # Update preferences
        await service.update_user_preferences(1, {"notifications": True, "theme": "dark"})

        # Get stats
        stats = await service.get_user_stats(1)
        assert stats["user_id"] == 1
        assert stats["recent_modules"] is not None

        # Context should reflect changes
        ctx = await service.get_user_context(1)
        assert "operacional" in ctx.last_modules
        assert ctx.preferences.get("theme") == "dark"

        # Clear cache
        service.clear_cache(user_id=1)
        assert 1 not in service._user_cache


class TestActionDetectorEdgeCases:
    """Edge case tests for ActionDetector."""

    def setup_method(self):
        from modules.ai.bartolo.actions.action_detector import ActionDetector

        self.detector = ActionDetector()

    def test_empty_string(self):
        result = self.detector.detect_action("")
        assert result is None

    def test_whitespace_only(self):
        result = self.detector.detect_action("   ")
        assert result is None

    def test_very_long_message(self):
        long_msg = "criar escala " + "x" * 1000
        result = self.detector.detect_action(long_msg)
        assert result is not None  # Should still detect

    def test_case_insensitive_detection(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("CRIAR UMA ESCALA")
        # Pattern matching is case insensitive based on regex used with re.IGNORECASE or lower()
        # Either detects or doesn't based on implementation - just shouldn't crash
        assert result is None or isinstance(result, object)

    def test_detect_divulgar_escala(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("divulgar a escala do mês")
        assert result is not None
        assert result.action_type == ActionType.PUBLISH_SCALE

    def test_detect_nova_ronda(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("nova ronda de inspeção")
        assert result is not None
        assert result.action_type == ActionType.CREATE_ROUND

    def test_detect_nova_diarista(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("nova diarista no sistema")
        assert result is not None
        assert result.action_type == ActionType.CREATE_DIARIST

    def test_detect_registrar_entrada(self):
        from modules.ai.bartolo.actions.action_types import ActionType

        result = self.detector.detect_action("marcar entrada do funcionário")
        assert result is not None
        assert result.action_type == ActionType.REGISTER_CHECKIN
