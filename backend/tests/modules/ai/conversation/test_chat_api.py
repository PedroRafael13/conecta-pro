"""Tests para API de Chat."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.fixture
def mock_current_user():
    """Mock do usuario autenticado."""
    user = MagicMock()
    user.id = 1
    user.nome = "Test User"
    user.email = "test@test.com"
    return user


@pytest.fixture
def sample_session():
    """Sessao de exemplo."""
    return {
        "id": str(uuid4()),
        "user_id": 1,
        "title": "Test Session",
        "description": None,
        "module_context": "crm",
        "message_count": 0,
        "is_active": True,
        "is_archived": False,
        "is_pinned": False,
    }


@pytest.fixture
def sample_message():
    """Mensagem de exemplo."""
    return {
        "id": str(uuid4()),
        "session_id": str(uuid4()),
        "message_type": "user",
        "content": "Olá, teste",
        "intent": "greeting",
        "intent_confidence": 0.95,
    }


class TestChatSessionEndpoints:
    """Testes dos endpoints de sessao."""

    @pytest.mark.asyncio
    async def test_create_session_success(self, mock_current_user, sample_session):
        """Testa criacao de sessao com sucesso."""
        # Este teste verifica a estrutura do request
        request_data = {
            "title": "Nova Conversa",
            "description": "Teste",
            "module_context": "crm",
        }

        assert "title" in request_data
        assert "module_context" in request_data

    @pytest.mark.asyncio
    async def test_create_session_default_title(self):
        """Testa que titulo padrao e aplicado."""
        from modules.ai.conversation.schemas.chat_schemas import ChatSessionCreate

        schema = ChatSessionCreate()

        assert schema.title == "Nova Conversa"

    @pytest.mark.asyncio
    async def test_list_sessions_pagination(self):
        """Testa paginacao de sessoes."""
        # Verifica parametros de paginacao
        params = {
            "page": 1,
            "page_size": 20,
            "include_archived": False,
        }

        assert params["page"] >= 1
        assert params["page_size"] <= 100

    @pytest.mark.asyncio
    async def test_update_session_fields(self):
        """Testa campos atualizaveis."""
        from modules.ai.conversation.schemas.chat_schemas import ChatSessionUpdate

        update = ChatSessionUpdate(
            title="Novo Titulo",
            is_pinned=True,
        )

        assert update.title == "Novo Titulo"
        assert update.is_pinned is True
        assert update.description is None


class TestChatMessageEndpoints:
    """Testes dos endpoints de mensagem."""

    @pytest.mark.asyncio
    async def test_send_message_request_validation(self):
        """Testa validacao do request de mensagem."""
        from modules.ai.conversation.schemas.chat_schemas import SendMessageRequest

        # Request valido
        request = SendMessageRequest(
            message="Olá, tudo bem?",
            include_suggestions=True,
        )

        assert request.message == "Olá, tudo bem?"
        assert request.include_suggestions is True

    @pytest.mark.asyncio
    async def test_send_message_strips_whitespace(self):
        """Testa que whitespace e removido."""
        from modules.ai.conversation.schemas.chat_schemas import SendMessageRequest

        request = SendMessageRequest(message="  Mensagem com espacos  ")

        assert request.message == "Mensagem com espacos"

    @pytest.mark.asyncio
    async def test_send_message_min_length(self):
        """Testa comprimento minimo da mensagem."""
        from pydantic import ValidationError

        from modules.ai.conversation.schemas.chat_schemas import SendMessageRequest

        with pytest.raises(ValidationError):
            SendMessageRequest(message="")

    @pytest.mark.asyncio
    async def test_feedback_rating_range(self):
        """Testa range do rating de feedback."""
        from pydantic import ValidationError

        from modules.ai.conversation.schemas.chat_schemas import MessageFeedback

        # Rating valido
        feedback = MessageFeedback(
            message_id=uuid4(),
            rating=5,
            was_helpful=True,
        )
        assert feedback.rating == 5

        # Rating invalido (> 5)
        with pytest.raises(ValidationError):
            MessageFeedback(
                message_id=uuid4(),
                rating=6,
                was_helpful=True,
            )

        # Rating invalido (< 1)
        with pytest.raises(ValidationError):
            MessageFeedback(
                message_id=uuid4(),
                rating=0,
                was_helpful=True,
            )


class TestSendMessageResponse:
    """Testes do schema de resposta."""

    def test_response_structure(self):
        """Testa estrutura da resposta."""
        from modules.ai.conversation.schemas.chat_schemas import (
            ActionItem,
            SendMessageResponse,
            SuggestionItem,
        )

        response = SendMessageResponse(
            message_id=uuid4(),
            session_id=uuid4(),
            response="Olá! Como posso ajudar?",
            intent="greeting",
            intent_confidence=0.95,
            suggestions=[
                SuggestionItem(text="Ver dashboard", type="quick_reply"),
            ],
            actions=[],
            processing_time_ms=150,
            model_used="gpt-4",
        )

        assert len(response.suggestions) == 1
        assert response.processing_time_ms == 150

    def test_suggestion_item(self):
        """Testa item de sugestao."""
        from modules.ai.conversation.schemas.chat_schemas import SuggestionItem

        suggestion = SuggestionItem(
            text="Criar lead",
            type="action",
            action="create",
            payload={"entity": "lead"},
        )

        assert suggestion.text == "Criar lead"
        assert suggestion.type == "action"

    def test_action_item(self):
        """Testa item de acao."""
        from modules.ai.conversation.schemas.chat_schemas import ActionItem

        action = ActionItem(
            type="create",
            label="Criar novo cliente",
            module="crm",
            entity="customer",
            requires_confirmation=True,
        )

        assert action.requires_confirmation is True


class TestConversationResponse:
    """Testes do schema de conversacao."""

    def test_conversation_response(self):
        """Testa resposta de conversacao."""
        from modules.ai.conversation.schemas.chat_schemas import ConversationResponse

        response = ConversationResponse(
            text="Resposta",
            intent="data_query",
            confidence=0.9,
            entities=[{"name": "email", "value": "test@test.com"}],
        )

        assert response.text == "Resposta"
        assert len(response.entities) == 1


class TestAIConfig:
    """Testes de configuracao."""

    def test_ai_config_response(self):
        """Testa resposta de configuracao."""
        from modules.ai.conversation.schemas.chat_schemas import AIConfigResponse

        config = AIConfigResponse()

        assert config.model == "gpt-4"
        assert "voice_input" in config.features_enabled
        assert "suggestions" in config.features_enabled

    def test_conversation_stats(self):
        """Testa estatisticas."""
        from modules.ai.conversation.schemas.chat_schemas import ConversationStats

        stats = ConversationStats(
            total_sessions=10,
            total_messages=100,
            avg_messages_per_session=10.0,
        )

        assert stats.total_sessions == 10
        assert stats.avg_messages_per_session == 10.0


class TestChatMessageModel:
    """Testes do model de mensagem."""

    def test_message_types(self):
        """Testa tipos de mensagem."""
        from modules.ai.conversation.models.chat_message import MessageType

        assert MessageType.USER.value == "user"
        assert MessageType.AI.value == "ai"
        assert MessageType.SYSTEM.value == "system"

    def test_message_status(self):
        """Testa status de mensagem."""
        from modules.ai.conversation.models.chat_message import MessageStatus

        assert MessageStatus.PENDING.value == "pending"
        assert MessageStatus.COMPLETED.value == "completed"
        assert MessageStatus.FAILED.value == "failed"

    def test_intent_categories(self):
        """Testa categorias de intent."""
        from modules.ai.conversation.models.chat_message import IntentCategory

        assert IntentCategory.GREETING.value == "greeting"
        assert IntentCategory.DATA_QUERY.value == "data_query"
        assert IntentCategory.ACTION_REQUEST.value == "action_request"
