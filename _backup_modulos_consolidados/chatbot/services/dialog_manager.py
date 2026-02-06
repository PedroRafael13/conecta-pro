"""Dialog Manager - Gerenciador de Dialogo do Chatbot.

Sprint 38 - Chatbot IA.

Responsavel por:
- Gerenciamento de contexto
- Fluxo de dialogo
- Slot filling
- Selecao de resposta
"""

import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from modules.ai.chatbot.models import (
    Conversation,
    ConversationContext,
    ConversationMessage,
    ConversationStatus,
    Intent,
    MessageSender,
    MessageType,
)
from modules.ai.chatbot.services.nlu_service import DetectedIntent, ExtractedEntity, NLUResult


@dataclass
class DialogContext:
    """Contexto do dialogo."""

    conversation_id: str
    active_contexts: List[str] = field(default_factory=list)
    slots: Dict[str, Any] = field(default_factory=dict)
    state: str = "idle"
    last_intent: Optional[str] = None
    pending_slots: List[Dict[str, Any]] = field(default_factory=list)
    turn_count: int = 0
    consecutive_fallbacks: int = 0


@dataclass
class DialogAction:
    """Acao a ser executada."""

    action_type: str  # response, api_call, handoff, slot_filling, confirmation
    response_text: Optional[str] = None
    response_buttons: List[Dict[str, Any]] = field(default_factory=list)
    quick_replies: List[Dict[str, Any]] = field(default_factory=list)
    api_config: Optional[Dict[str, Any]] = None
    handoff_reason: Optional[str] = None
    slot_prompt: Optional[str] = None
    confirmation_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DialogResponse:
    """Resposta do gerenciador de dialogo."""

    message_id: str
    text: str
    message_type: MessageType
    buttons: List[Dict[str, Any]]
    quick_replies: List[Dict[str, Any]]
    attachments: List[Dict[str, Any]]
    action_triggered: Optional[str]
    action_result: Optional[Dict[str, Any]]
    context_updates: Dict[str, Any]
    should_handoff: bool
    handoff_reason: Optional[str]
    is_fallback: bool


class DialogManager:
    """Gerenciador de dialogo do chatbot."""

    # Acoes especiais
    HANDOFF_TRIGGERS = {"falar com atendente", "falar com humano", "pessoa real", "atendente"}
    CANCEL_TRIGGERS = {"cancelar", "sair", "voltar", "desistir"}
    HELP_TRIGGERS = {"ajuda", "help", "como funciona", "o que voce faz"}

    def __init__(
        self,
        max_context_turns: int = 10,
        max_consecutive_fallbacks: int = 3,
        enable_slot_filling: bool = True,
        enable_confirmation: bool = True,
    ):
        """Inicializa o gerenciador de dialogo."""
        self.max_context_turns = max_context_turns
        self.max_consecutive_fallbacks = max_consecutive_fallbacks
        self.enable_slot_filling = enable_slot_filling
        self.enable_confirmation = enable_confirmation

    def process_turn(
        self,
        nlu_result: NLUResult,
        context: DialogContext,
        intents: Dict[str, Intent],
        greeting_message: str = "Ola! Como posso ajudar?",
        fallback_message: str = "Desculpe, nao entendi. Pode reformular?",
        goodbye_message: str = "Obrigado pelo contato!",
    ) -> DialogResponse:
        """Processa um turno de dialogo."""
        context.turn_count += 1

        # Verificar triggers especiais
        special_response = self._check_special_triggers(nlu_result.normalized_text, context)
        if special_response:
            return special_response

        # Verificar se ha intent detectado
        if not nlu_result.top_intent:
            return self._handle_no_intent(context, fallback_message)

        intent = intents.get(nlu_result.top_intent.name)
        if not intent:
            return self._handle_no_intent(context, fallback_message)

        # Resetar contador de fallbacks
        context.consecutive_fallbacks = 0
        context.last_intent = intent.name

        # Preencher slots com entidades extraidas
        self._fill_slots_from_entities(context, nlu_result.entities, intent)

        # Verificar se precisa de mais slots
        if self.enable_slot_filling:
            missing_slot = self._get_missing_required_slot(context, intent)
            if missing_slot:
                return self._request_slot(context, missing_slot)

        # Verificar se precisa confirmacao
        if self.enable_confirmation and intent.requires_confirmation:
            if context.state != "awaiting_confirmation":
                return self._request_confirmation(context, intent)

        # Executar acao se houver
        action_result = None
        if intent.action:
            action_result = self._execute_action(intent, context)

        # Gerar resposta
        response_text = self._select_response(intent, context)

        # Atualizar contexto
        self._update_context(context, intent)

        return DialogResponse(
            message_id=str(uuid.uuid4()),
            text=response_text,
            message_type=MessageType.TEXT,
            buttons=self._get_response_buttons(intent),
            quick_replies=self._get_quick_replies(intent, context),
            attachments=[],
            action_triggered=intent.action,
            action_result=action_result,
            context_updates={"slots": context.slots, "active_contexts": context.active_contexts},
            should_handoff=False,
            handoff_reason=None,
            is_fallback=False,
        )

    def _check_special_triggers(
        self,
        text: str,
        context: DialogContext,
    ) -> Optional[DialogResponse]:
        """Verifica triggers especiais."""
        text_lower = text.lower()

        # Handoff
        if any(trigger in text_lower for trigger in self.HANDOFF_TRIGGERS):
            return DialogResponse(
                message_id=str(uuid.uuid4()),
                text="Vou transferir voce para um atendente. Aguarde um momento.",
                message_type=MessageType.TEXT,
                buttons=[],
                quick_replies=[],
                attachments=[],
                action_triggered="handoff",
                action_result=None,
                context_updates={},
                should_handoff=True,
                handoff_reason="user_request",
                is_fallback=False,
            )

        # Cancelar
        if any(trigger in text_lower for trigger in self.CANCEL_TRIGGERS):
            context.state = "idle"
            context.pending_slots = []
            return DialogResponse(
                message_id=str(uuid.uuid4()),
                text="Ok, cancelado. Como posso ajudar?",
                message_type=MessageType.TEXT,
                buttons=[],
                quick_replies=[],
                attachments=[],
                action_triggered="cancel",
                action_result=None,
                context_updates={"state": "idle"},
                should_handoff=False,
                handoff_reason=None,
                is_fallback=False,
            )

        # Confirmacao
        if context.state == "awaiting_confirmation":
            if text_lower in ["sim", "confirmar", "ok", "yes", "isso", "correto"]:
                context.state = "confirmed"
                return None  # Continuar processamento normal

            elif text_lower in ["nao", "no", "cancelar", "errado", "incorreto"]:
                context.state = "idle"
                context.pending_slots = []
                return DialogResponse(
                    message_id=str(uuid.uuid4()),
                    text="Ok, vamos comecar de novo. O que voce precisa?",
                    message_type=MessageType.TEXT,
                    buttons=[],
                    quick_replies=[],
                    attachments=[],
                    action_triggered="cancel_confirmation",
                    action_result=None,
                    context_updates={"state": "idle"},
                    should_handoff=False,
                    handoff_reason=None,
                    is_fallback=False,
                )

        return None

    def _handle_no_intent(
        self,
        context: DialogContext,
        fallback_message: str,
    ) -> DialogResponse:
        """Trata caso de nenhum intent detectado."""
        context.consecutive_fallbacks += 1

        # Verificar se deve transferir para humano
        should_handoff = context.consecutive_fallbacks >= self.max_consecutive_fallbacks

        if should_handoff:
            text = "Parece que estou tendo dificuldades em entender. Vou transferir para um atendente."
        else:
            text = fallback_message

        return DialogResponse(
            message_id=str(uuid.uuid4()),
            text=text,
            message_type=MessageType.TEXT,
            buttons=[],
            quick_replies=[{"text": "Falar com atendente", "action": "handoff"}],
            attachments=[],
            action_triggered="fallback",
            action_result=None,
            context_updates={},
            should_handoff=should_handoff,
            handoff_reason="consecutive_fallbacks" if should_handoff else None,
            is_fallback=True,
        )

    def _fill_slots_from_entities(
        self,
        context: DialogContext,
        entities: List[ExtractedEntity],
        intent: Intent,
    ) -> None:
        """Preenche slots a partir de entidades extraidas."""
        if not intent.slots:
            return

        for slot in intent.slots:
            slot_name = slot.get("name")
            slot_entity = slot.get("entity")

            if slot_name and slot_entity:
                for entity in entities:
                    if entity.entity == slot_entity:
                        context.slots[slot_name] = entity.value
                        break

    def _get_missing_required_slot(
        self,
        context: DialogContext,
        intent: Intent,
    ) -> Optional[Dict[str, Any]]:
        """Retorna proximo slot obrigatorio faltando."""
        if not intent.slots:
            return None

        for slot in intent.slots:
            if slot.get("required", False):
                slot_name = slot.get("name")
                if slot_name and slot_name not in context.slots:
                    return slot

        return None

    def _request_slot(
        self,
        context: DialogContext,
        slot: Dict[str, Any],
    ) -> DialogResponse:
        """Solicita preenchimento de slot."""
        context.state = "slot_filling"
        context.pending_slots.append(slot)

        prompt = slot.get("prompt", f"Por favor, informe {slot.get('name')}:")

        return DialogResponse(
            message_id=str(uuid.uuid4()),
            text=prompt,
            message_type=MessageType.TEXT,
            buttons=[],
            quick_replies=[{"text": "Cancelar", "action": "cancel"}],
            attachments=[],
            action_triggered="slot_request",
            action_result={"slot": slot.get("name")},
            context_updates={"state": "slot_filling"},
            should_handoff=False,
            handoff_reason=None,
            is_fallback=False,
        )

    def _request_confirmation(
        self,
        context: DialogContext,
        intent: Intent,
    ) -> DialogResponse:
        """Solicita confirmacao antes de executar."""
        context.state = "awaiting_confirmation"

        # Construir mensagem de confirmacao
        confirmation_msg = intent.confirmation_message or "Confirma a operacao?"

        # Adicionar slots preenchidos
        if context.slots:
            slots_text = "\n".join(f"- {k}: {v}" for k, v in context.slots.items())
            confirmation_msg = f"{slots_text}\n\n{confirmation_msg}"

        return DialogResponse(
            message_id=str(uuid.uuid4()),
            text=confirmation_msg,
            message_type=MessageType.TEXT,
            buttons=[
                {"text": "Sim", "action": "confirm"},
                {"text": "Nao", "action": "cancel"},
            ],
            quick_replies=[],
            attachments=[],
            action_triggered="confirmation_request",
            action_result=None,
            context_updates={"state": "awaiting_confirmation"},
            should_handoff=False,
            handoff_reason=None,
            is_fallback=False,
        )

    def _execute_action(
        self,
        intent: Intent,
        context: DialogContext,
    ) -> Optional[Dict[str, Any]]:
        """Executa acao do intent."""
        action_config = intent.action_config or {}
        action_type = action_config.get("type", "none")

        # Simulacao de execucao de acao
        result = {
            "action": intent.action,
            "type": action_type,
            "status": "success",
            "executed_at": datetime.utcnow().isoformat(),
            "slots_used": context.slots.copy(),
        }

        # Aqui integraria com APIs externas, banco de dados, etc.
        # Por enquanto, apenas retorna resultado simulado

        return result

    def _select_response(
        self,
        intent: Intent,
        context: DialogContext,
    ) -> str:
        """Seleciona resposta do intent."""
        if not intent.responses:
            return "Entendido."

        # Selecionar resposta aleatoria
        response = random.choice(intent.responses)

        # Substituir variaveis de slot
        for slot_name, slot_value in context.slots.items():
            response = response.replace(f"{{{slot_name}}}", str(slot_value))

        return response

    def _update_context(
        self,
        context: DialogContext,
        intent: Intent,
    ) -> None:
        """Atualiza contexto apos processamento."""
        # Adicionar contextos de saida
        if intent.output_contexts:
            for ctx in intent.output_contexts:
                if ctx not in context.active_contexts:
                    context.active_contexts.append(ctx)

        # Remover contextos expirados (simplificado)
        if len(context.active_contexts) > 5:
            context.active_contexts = context.active_contexts[-5:]

        # Resetar estado
        context.state = "idle"
        context.pending_slots = []

    def _get_response_buttons(
        self,
        intent: Intent,
    ) -> List[Dict[str, Any]]:
        """Retorna botoes de resposta."""
        if intent.rich_responses:
            for response in intent.rich_responses:
                if response.get("type") == "buttons":
                    return response.get("buttons", [])
        return []

    def _get_quick_replies(
        self,
        intent: Intent,
        context: DialogContext,
    ) -> List[Dict[str, Any]]:
        """Retorna quick replies."""
        # Followup intents
        quick_replies = []

        if intent.followup_intents:
            # Simplificado - idealmente buscaria os intents followup
            pass

        return quick_replies

    def create_context(self, conversation_id: str) -> DialogContext:
        """Cria novo contexto de dialogo."""
        return DialogContext(conversation_id=conversation_id)

    def restore_context(
        self,
        conversation_id: str,
        saved_context: Dict[str, Any],
    ) -> DialogContext:
        """Restaura contexto de dialogo."""
        return DialogContext(
            conversation_id=conversation_id,
            active_contexts=saved_context.get("active_contexts", []),
            slots=saved_context.get("slots", {}),
            state=saved_context.get("state", "idle"),
            last_intent=saved_context.get("last_intent"),
            turn_count=saved_context.get("turn_count", 0),
            consecutive_fallbacks=saved_context.get("consecutive_fallbacks", 0),
        )

    def save_context(self, context: DialogContext) -> Dict[str, Any]:
        """Salva contexto de dialogo."""
        return {
            "active_contexts": context.active_contexts,
            "slots": context.slots,
            "state": context.state,
            "last_intent": context.last_intent,
            "turn_count": context.turn_count,
            "consecutive_fallbacks": context.consecutive_fallbacks,
        }
