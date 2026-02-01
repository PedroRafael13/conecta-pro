"""
Testes automatizados para o BartoloController.

Testa:
- POST /bartolo/send - envio de mensagem
- GET /bartolo/greeting - saudacao
- POST /bartolo/feedback - feedback
- GET /bartolo/modules - listagem de modulos
- GET /bartolo/health - health check
- GET /bartolo/stats - estatisticas
- POST /bartolo/wizard/start - inicio de wizard
- POST /bartolo/wizard/input - input no wizard
- GET /bartolo/wizard/status - status do wizard
- POST /bartolo/wizard/cancel - cancelamento de wizard
"""

import sys

import pytest

sys.path.insert(0, "/app")

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from modules.ai.bartolo.controllers.bartolo_controller import (
    FeedbackRequest,
    SendMessageRequest,
    SendMessageResponse,
    WizardInputRequest,
    WizardStartRequest,
    bartolo_router,
)
from modules.ai.bartolo.wizards.base_wizard import WizardState

# ==========================================================================
# Testes de schemas
# ==========================================================================


class TestControllerSchemas:
    """Testes para os schemas do controller."""

    def test_send_message_request_valid(self):
        """Testa schema de request valido."""
        req = SendMessageRequest(
            message="criar escala",
            session_id="sess-123",
        )
        assert req.message == "criar escala"
        assert req.session_id == "sess-123"
        assert req.module is None
        assert req.metadata is None

    def test_send_message_request_with_optionals(self):
        """Testa schema com campos opcionais."""
        req = SendMessageRequest(
            message="criar escala",
            session_id="sess-123",
            module="escalas",
            metadata={"context": "test"},
        )
        assert req.module == "escalas"
        assert req.metadata == {"context": "test"}

    def test_send_message_request_empty_message_fails(self):
        """Testa que mensagem vazia falha na validacao."""
        with pytest.raises(Exception):
            SendMessageRequest(
                message="",
                session_id="sess-123",
            )

    def test_send_message_response_valid(self):
        """Testa schema de response valido."""
        resp = SendMessageResponse(
            message_id="msg-1",
            session_id="sess-1",
            response="Ola!",
        )
        assert resp.message_id == "msg-1"
        assert resp.response == "Ola!"
        assert resp.suggestions == []
        assert resp.actions == []

    def test_feedback_request_valid(self):
        """Testa schema de feedback valido."""
        req = FeedbackRequest(
            interaction_id=str(uuid4()),
            feedback_type="helpful",
        )
        assert req.feedback_type == "helpful"
        assert req.rating is None
        assert req.feedback_text is None

    def test_feedback_request_with_rating(self):
        """Testa schema de feedback com nota."""
        req = FeedbackRequest(
            interaction_id=str(uuid4()),
            feedback_type="helpful",
            rating=5,
            feedback_text="Resposta excelente",
        )
        assert req.rating == 5
        assert req.feedback_text == "Resposta excelente"

    def test_feedback_request_invalid_rating(self):
        """Testa que rating fora de range falha."""
        with pytest.raises(Exception):
            FeedbackRequest(
                interaction_id=str(uuid4()),
                feedback_type="helpful",
                rating=6,
            )

    def test_wizard_start_request(self):
        """Testa schema de inicio de wizard."""
        req = WizardStartRequest(
            wizard_type="proposta_comercial",
            session_id="sess-1",
        )
        assert req.wizard_type == "proposta_comercial"
        assert req.initial_data is None

    def test_wizard_input_request(self):
        """Testa schema de input no wizard."""
        req = WizardInputRequest(
            session_id="sess-1",
            user_input="Condominio Teste",
        )
        assert req.user_input == "Condominio Teste"


# ==========================================================================
# Testes do Health Check (endpoint mais simples, nao depende de mocks)
# ==========================================================================


class TestHealthEndpoint:
    """Testes para o endpoint /health."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Testa que health check retorna status correto."""
        # Importa e chama diretamente a funcao do endpoint
        from modules.ai.bartolo.controllers.bartolo_controller import health_check

        result = await health_check()
        assert result["status"] == "healthy"
        assert result["name"] == "Bartolo"
        assert result["version"] == "1.0"
        assert "Bartolo" in result["message"]


# ==========================================================================
# Testes do Router Configuration
# ==========================================================================


class TestRouterConfig:
    """Testes para configuracao do router."""

    def test_router_prefix(self):
        """Testa que o router tem o prefix correto."""
        assert bartolo_router.prefix == "/bartolo"

    def test_router_tags(self):
        """Testa que o router tem as tags corretas."""
        assert "Bartolo - Assistente Inteligente" in bartolo_router.tags

    def test_router_has_routes(self):
        """Testa que o router tem rotas definidas."""
        routes = [r.path for r in bartolo_router.routes]
        assert len(routes) > 0

    def test_router_has_send_endpoint(self):
        """Testa que a rota /send existe."""
        routes = [r.path for r in bartolo_router.routes]
        assert "/bartolo/send" in routes

    def test_router_has_greeting_endpoint(self):
        """Testa que a rota /greeting existe."""
        routes = [r.path for r in bartolo_router.routes]
        assert "/bartolo/greeting" in routes

    def test_router_has_feedback_endpoint(self):
        """Testa que a rota /feedback existe."""
        routes = [r.path for r in bartolo_router.routes]
        assert "/bartolo/feedback" in routes

    def test_router_has_health_endpoint(self):
        """Testa que a rota /health existe."""
        routes = [r.path for r in bartolo_router.routes]
        assert "/bartolo/health" in routes

    def test_router_has_stats_endpoint(self):
        """Testa que a rota /stats existe."""
        routes = [r.path for r in bartolo_router.routes]
        assert "/bartolo/stats" in routes

    def test_router_has_modules_endpoint(self):
        """Testa que a rota /modules existe."""
        routes = [r.path for r in bartolo_router.routes]
        assert "/bartolo/modules" in routes

    def test_router_has_wizard_endpoints(self):
        """Testa que as rotas de wizard existem."""
        routes = [r.path for r in bartolo_router.routes]
        assert "/bartolo/wizard/start" in routes
        assert "/bartolo/wizard/input" in routes
        assert "/bartolo/wizard/status" in routes
        assert "/bartolo/wizard/cancel" in routes

    def test_router_has_wizards_list_endpoint(self):
        """Testa que a rota /wizards existe."""
        routes = [r.path for r in bartolo_router.routes]
        assert "/bartolo/wizards" in routes

    def test_router_has_confirm_action_endpoint(self):
        """Testa que a rota /confirm-action existe."""
        routes = [r.path for r in bartolo_router.routes]
        assert "/bartolo/confirm-action" in routes

    def test_router_has_stream_endpoint(self):
        """Testa que a rota /send/stream existe."""
        routes = [r.path for r in bartolo_router.routes]
        assert "/bartolo/send/stream" in routes

    def test_router_has_learning_endpoints(self):
        """Testa que as rotas de learning existem."""
        routes = [r.path for r in bartolo_router.routes]
        assert "/bartolo/learning/stats" in routes
        assert "/bartolo/learning/patterns" in routes


# ==========================================================================
# Testes com Mock do Engine
# ==========================================================================


class TestSendMessageEndpoint:
    """Testes para o endpoint /send com mocks."""

    @pytest.mark.asyncio
    async def test_send_message_calls_engine(self):
        """Testa que send_message chama o engine corretamente."""
        from modules.ai.bartolo.controllers.bartolo_controller import send_message

        mock_response = MagicMock()
        mock_response.message_id = uuid4()
        mock_response.session_id = "sess-1"
        mock_response.response = "Ola! Sou o Bartolo."
        mock_response.response_html = None
        mock_response.intent = "greeting"
        mock_response.confidence = 0.95
        mock_response.suggestions = ["Ver escalas"]
        mock_response.actions = []
        mock_response.wizard_response = None
        mock_response.data_results = None
        mock_response.action_preview = None
        mock_response.processing_time_ms = 50
        mock_response.model_used = "rule_based"

        mock_engine = AsyncMock()
        mock_engine.process_message = AsyncMock(return_value=mock_response)

        mock_learning = AsyncMock()
        mock_learning.record_interaction = AsyncMock()

        mock_db = AsyncMock()

        request = SendMessageRequest(
            message="ola",
            session_id="sess-1",
        )

        # Mock do User autenticado (bug #6: send_message agora usa current_user via JWT)
        mock_user = MagicMock()
        mock_user.id = uuid4()

        result = await send_message(
            request=request,
            current_user=mock_user,
            engine=mock_engine,
            learning=mock_learning,
            db=mock_db,
        )

        assert result.response == "Ola! Sou o Bartolo."
        assert result.session_id == "sess-1"
        mock_engine.process_message.assert_called_once()
        mock_learning.record_interaction.assert_called_once()


class TestGreetingEndpoint:
    """Testes para o endpoint /greeting com mocks."""

    @pytest.mark.asyncio
    async def test_greeting(self):
        """Testa que greeting retorna saudacao."""
        from modules.ai.bartolo.controllers.bartolo_controller import get_greeting

        mock_user = MagicMock()
        mock_user.id = uuid4()

        mock_engine = AsyncMock()
        mock_engine.get_greeting = AsyncMock(return_value="Bom dia! Sou o Bartolo.")

        result = await get_greeting(
            session_id="sess-1",
            current_user=mock_user,
            engine=mock_engine,
        )

        assert result["greeting"] == "Bom dia! Sou o Bartolo."
        mock_engine.get_greeting.assert_called_once_with(str(mock_user.id), "sess-1")


class TestStatsEndpoint:
    """Testes para o endpoint /stats com mocks."""

    @pytest.mark.asyncio
    async def test_stats(self):
        """Testa que stats retorna dados."""
        from modules.ai.bartolo.controllers.bartolo_controller import get_stats

        mock_engine = MagicMock()
        mock_engine.get_stats = MagicMock(return_value={"total_messages": 100})

        mock_learning = MagicMock()
        mock_learning.get_stats = MagicMock(return_value={"total_feedback": 10})

        result = await get_stats(engine=mock_engine, learning=mock_learning)

        assert result["bartolo"]["total_messages"] == 100
        assert result["learning"]["total_feedback"] == 10


class TestModulesEndpoint:
    """Testes para o endpoint /modules com mocks."""

    @pytest.mark.asyncio
    async def test_list_modules(self):
        """Testa listagem de modulos."""
        from modules.ai.bartolo.controllers.bartolo_controller import list_modules

        mock_engine = AsyncMock()
        mock_engine.get_available_modules = AsyncMock(
            return_value=[
                {"id": "escalas", "name": "Escalas"},
                {"id": "cobertura", "name": "Cobertura"},
            ]
        )

        result = await list_modules(engine=mock_engine)

        assert result["total"] == 2
        assert len(result["modules"]) == 2


class TestModuleInfoEndpoint:
    """Testes para o endpoint /modules/{module_id}."""

    @pytest.mark.asyncio
    async def test_module_info_not_found(self):
        """Testa que modulo inexistente retorna 404."""
        from fastapi import HTTPException

        from modules.ai.bartolo.controllers.bartolo_controller import get_module_info

        with pytest.raises(HTTPException) as exc_info:
            await get_module_info("modulo_inexistente_xyz")
        assert exc_info.value.status_code == 404


class TestWizardEndpoints:
    """Testes para os endpoints de wizard."""

    @pytest.mark.asyncio
    async def test_start_wizard(self):
        """Testa inicio de wizard via endpoint."""
        from modules.ai.bartolo.controllers.bartolo_controller import start_wizard

        mock_engine = MagicMock()
        mock_response = MagicMock()
        mock_response.wizard_id = uuid4()
        mock_response.step_id = "cliente"
        mock_response.step_number = 1
        mock_response.total_steps = 9
        mock_response.state = WizardState.WAITING_INPUT
        mock_response.message = "Vamos comecar!"
        mock_response.question = "Qual o nome do cliente?"
        mock_response.options = []
        mock_response.help_text = "Informe o nome"
        mock_response.progress_percent = 0.0

        mock_engine.wizard_manager = MagicMock()
        mock_engine.wizard_manager.start_wizard = MagicMock(return_value=mock_response)

        request = WizardStartRequest(
            wizard_type="proposta_comercial",
            session_id="sess-1",
        )

        mock_user = MagicMock()
        mock_user.id = uuid4()

        result = await start_wizard(request=request, current_user=mock_user, engine=mock_engine)

        assert result["step_number"] == 1
        assert result["total_steps"] == 9
        assert result["state"] == WizardState.WAITING_INPUT.value

    @pytest.mark.asyncio
    async def test_wizard_input(self):
        """Testa input no wizard via endpoint."""
        from modules.ai.bartolo.controllers.bartolo_controller import wizard_input

        mock_engine = MagicMock()
        mock_response = MagicMock()
        mock_response.wizard_id = uuid4()
        mock_response.step_id = "tipo_servico"
        mock_response.step_number = 2
        mock_response.total_steps = 9
        mock_response.state = WizardState.WAITING_INPUT
        mock_response.message = "Otimo!"
        mock_response.question = "Qual o tipo?"
        mock_response.options = ["Portaria", "Vigilancia"]
        mock_response.help_text = None
        mock_response.collected_data = {"cliente": "Teste"}
        mock_response.progress_percent = 11.1
        mock_response.can_go_back = True

        mock_engine.wizard_manager = MagicMock()
        mock_engine.wizard_manager.process_input = MagicMock(return_value=mock_response)

        request = WizardInputRequest(
            session_id="sess-1",
            user_input="Condominio Teste",
        )

        mock_user = MagicMock()
        mock_user.id = uuid4()

        result = await wizard_input(request=request, current_user=mock_user, engine=mock_engine)

        assert result["step_number"] == 2
        assert result["collected_data"]["cliente"] == "Teste"
        assert result["can_go_back"] is True

    @pytest.mark.asyncio
    async def test_wizard_input_no_active_wizard(self):
        """Testa input sem wizard ativo."""
        from fastapi import HTTPException

        from modules.ai.bartolo.controllers.bartolo_controller import wizard_input

        mock_engine = MagicMock()
        mock_engine.wizard_manager = MagicMock()
        mock_engine.wizard_manager.process_input = MagicMock(return_value=None)

        request = WizardInputRequest(
            session_id="sess-1",
            user_input="texto",
        )

        mock_user = MagicMock()
        mock_user.id = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            await wizard_input(request=request, current_user=mock_user, engine=mock_engine)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_wizard_cancel(self):
        """Testa cancelamento de wizard."""
        from modules.ai.bartolo.controllers.bartolo_controller import cancel_wizard

        mock_engine = MagicMock()
        mock_response = MagicMock()
        mock_response.message = "Wizard cancelado."

        mock_engine.wizard_manager = MagicMock()
        mock_engine.wizard_manager.cancel_wizard = MagicMock(return_value=mock_response)

        mock_user = MagicMock()
        mock_user.id = uuid4()

        result = await cancel_wizard(session_id="sess-1", current_user=mock_user, engine=mock_engine)

        assert result["success"] is True
        assert "cancelado" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_wizard_cancel_no_active(self):
        """Testa cancelamento sem wizard ativo."""
        from fastapi import HTTPException

        from modules.ai.bartolo.controllers.bartolo_controller import cancel_wizard

        mock_engine = MagicMock()
        mock_engine.wizard_manager = MagicMock()
        mock_engine.wizard_manager.cancel_wizard = MagicMock(return_value=None)

        mock_user = MagicMock()
        mock_user.id = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            await cancel_wizard(session_id="sess-1", current_user=mock_user, engine=mock_engine)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_wizard_status_no_active(self):
        """Testa status sem wizard ativo."""
        from modules.ai.bartolo.controllers.bartolo_controller import wizard_status

        mock_engine = MagicMock()
        mock_engine.wizard_manager = MagicMock()
        mock_engine.wizard_manager.get_wizard_status = MagicMock(return_value=None)

        mock_user = MagicMock()
        mock_user.id = uuid4()

        result = await wizard_status(session_id="sess-1", current_user=mock_user, engine=mock_engine)

        assert result["active"] is False
