"""Chatbot Service - Servico de Chatbot WhatsApp.

Sprint 31 - Automacoes WhatsApp.
Responsavel por:
- Processamento de mensagens recebidas
- Respostas automaticas
- Menu interativo
- Intencoes e acoes
"""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.integrations.whatsapp.models.message_log import MessageLog


class Intent(StrEnum):
    """Intencoes reconhecidas pelo chatbot."""

    GREETING = "GREETING"  # Saudacao
    BILLING = "BILLING"  # Consulta boleto/financeiro
    SECOND_COPY = "SECOND_COPY"  # Segunda via de boleto
    PAYMENT_STATUS = "PAYMENT_STATUS"  # Status de pagamento
    SUPPORT = "SUPPORT"  # Suporte tecnico
    SCHEDULE = "SCHEDULE"  # Agendamento
    COMPLAINT = "COMPLAINT"  # Reclamacao
    INFORMATION = "INFORMATION"  # Informacoes gerais
    MENU = "MENU"  # Ver menu
    HUMAN = "HUMAN"  # Falar com atendente
    GOODBYE = "GOODBYE"  # Despedida
    UNKNOWN = "UNKNOWN"  # Nao reconhecido


class ConversationState(StrEnum):
    """Estado da conversa."""

    NEW = "NEW"  # Nova conversa
    MENU = "MENU"  # Exibindo menu
    AWAITING_CPF = "AWAITING_CPF"  # Aguardando CPF
    AWAITING_UNIT = "AWAITING_UNIT"  # Aguardando unidade
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"  # Aguardando confirmacao
    HUMAN_TRANSFER = "HUMAN_TRANSFER"  # Transferido para humano
    COMPLETED = "COMPLETED"  # Conversa finalizada


@dataclass
class ConversationContext:
    """Contexto da conversa."""

    tenant_id: UUID
    phone: str
    state: ConversationState = ConversationState.NEW
    intent: Intent | None = None
    data: dict = field(default_factory=dict)
    last_message_at: datetime = field(default_factory=datetime.utcnow)
    message_count: int = 0

    def update_state(self, new_state: ConversationState) -> None:
        """Atualiza estado."""
        self.state = new_state
        self.last_message_at = datetime.utcnow()

    def set_data(self, key: str, value) -> None:
        """Define dado no contexto."""
        self.data[key] = value

    def get_data(self, key: str, default=None):
        """Obtem dado do contexto."""
        return self.data.get(key, default)

    def increment_messages(self) -> None:
        """Incrementa contador de mensagens."""
        self.message_count += 1
        self.last_message_at = datetime.utcnow()


@dataclass
class ChatbotResponse:
    """Resposta do chatbot."""

    message: str
    buttons: list = field(default_factory=list)
    quick_replies: list = field(default_factory=list)
    transfer_to_human: bool = False
    end_conversation: bool = False
    context: ConversationContext | None = None


class ChatbotService:
    """Servico de Chatbot para WhatsApp."""

    # Padroes de intencao
    INTENT_PATTERNS = {
        Intent.GREETING: [
            r"\b(oi|ola|bom dia|boa tarde|boa noite|hey|hello|hi)\b",
        ],
        Intent.BILLING: [
            r"\b(boleto|fatura|conta|pagar|pagamento|cobran[cç]a|d[eé]bito)\b",
        ],
        Intent.SECOND_COPY: [
            r"\b(segunda via|2[aª]?\s*via|copiar?|reemitir|novo boleto)\b",
        ],
        Intent.PAYMENT_STATUS: [
            r"\b(status|situa[cç][aã]o|paguei|pagou|baixa|quitado)\b",
        ],
        Intent.SUPPORT: [
            r"\b(suporte|ajuda|problema|erro|n[aã]o funciona|bug)\b",
        ],
        Intent.SCHEDULE: [
            r"\b(agendar|marcar|horario|visita|t[eé]cnico)\b",
        ],
        Intent.COMPLAINT: [
            r"\b(reclama[cç][aã]o|reclamar|insatisfeito|p[eé]ssimo|ruim)\b",
        ],
        Intent.MENU: [
            r"\b(menu|op[cç][oõ]es|comandos|ajuda|o que voc[eê])\b",
        ],
        Intent.HUMAN: [
            r"\b(atendente|humano|pessoa|falar com|operador)\b",
        ],
        Intent.GOODBYE: [
            r"\b(tchau|at[eé]|obrigad[oa]|valeu|fui)\b",
        ],
    }

    # Respostas padrao
    DEFAULT_RESPONSES = {
        Intent.GREETING: (
            "Ola! Bem-vindo ao atendimento automatico. "
            "Como posso ajudar voce hoje?\n\n"
            "Digite *MENU* para ver as opcoes disponiveis."
        ),
        Intent.GOODBYE: ("Obrigado pelo contato! Se precisar de mais alguma coisa, e so chamar. Ate logo!"),
        Intent.UNKNOWN: (
            "Desculpe, nao entendi sua mensagem. "
            "Digite *MENU* para ver as opcoes disponiveis ou "
            "*ATENDENTE* para falar com uma pessoa."
        ),
    }

    MENU_MESSAGE = (
        "*MENU DE OPCOES*\n\n"
        "1. Consultar boleto\n"
        "2. Segunda via de boleto\n"
        "3. Status de pagamento\n"
        "4. Suporte tecnico\n"
        "5. Agendar visita\n"
        "6. Falar com atendente\n\n"
        "Digite o numero da opcao desejada."
    )

    def __init__(self, session: AsyncSession):
        """Inicializa o servico.

        Args:
            session: Sessao assincrona do banco de dados.
        """
        self.session = session
        self._conversations: dict[str, ConversationContext] = {}
        self._action_handlers: dict[Intent, Callable] = {}

    def register_handler(self, intent: Intent, handler: Callable) -> None:
        """Registra handler para intencao.

        Args:
            intent: Intencao.
            handler: Funcao handler.
        """
        self._action_handlers[intent] = handler

    async def process_message(
        self,
        tenant_id: UUID,
        phone: str,
        message: str,
        contact_name: str | None = None,
    ) -> ChatbotResponse:
        """Processa mensagem recebida.

        Args:
            tenant_id: ID do tenant.
            phone: Telefone do remetente.
            message: Texto da mensagem.
            contact_name: Nome do contato.

        Returns:
            ChatbotResponse.
        """
        # Obtem ou cria contexto
        context = self._get_or_create_context(tenant_id, phone)
        context.increment_messages()

        # Normaliza mensagem
        normalized = self._normalize_message(message)

        # Verifica menu numerico
        if context.state == ConversationState.MENU:
            return await self._handle_menu_selection(context, normalized)

        # Detecta intencao
        intent = self._detect_intent(normalized)
        context.intent = intent

        # Processa conforme intencao
        response = await self._process_intent(context, intent, normalized, contact_name)

        return response

    async def get_conversation_history(
        self,
        tenant_id: UUID,
        phone: str,
        limit: int = 50,
    ) -> list[dict]:
        """Obtem historico de conversa.

        Args:
            tenant_id: ID do tenant.
            phone: Telefone.
            limit: Limite de mensagens.

        Returns:
            Lista de mensagens.
        """
        query = (
            select(MessageLog)
            .where(
                and_(
                    MessageLog.tenant_id == tenant_id,
                    (MessageLog.from_phone == phone) | (MessageLog.to_phone == phone),
                )
            )
            .order_by(MessageLog.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        messages = list(result.scalars().all())

        return [
            {
                "id": str(msg.id),
                "direction": msg.direction.value,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
                "status": msg.status,
            }
            for msg in reversed(messages)
        ]

    async def transfer_to_human(
        self,
        tenant_id: UUID,
        phone: str,
        reason: str | None = None,
    ) -> ChatbotResponse:
        """Transfere conversa para atendente humano.

        Args:
            tenant_id: ID do tenant.
            phone: Telefone.
            reason: Motivo da transferencia.

        Returns:
            ChatbotResponse.
        """
        context = self._get_or_create_context(tenant_id, phone)
        context.update_state(ConversationState.HUMAN_TRANSFER)
        context.set_data("transfer_reason", reason)

        return ChatbotResponse(
            message=(
                "Voce sera transferido para um atendente humano. "
                "Aguarde um momento, por favor.\n\n"
                "Horario de atendimento: Segunda a Sexta, 8h as 18h."
            ),
            transfer_to_human=True,
            context=context,
        )

    def clear_context(self, tenant_id: UUID, phone: str) -> None:
        """Limpa contexto da conversa.

        Args:
            tenant_id: ID do tenant.
            phone: Telefone.
        """
        key = f"{tenant_id}:{phone}"
        if key in self._conversations:
            del self._conversations[key]

    # --- Metodos privados ---

    def _get_or_create_context(
        self,
        tenant_id: UUID,
        phone: str,
    ) -> ConversationContext:
        """Obtem ou cria contexto de conversa."""
        key = f"{tenant_id}:{phone}"

        if key not in self._conversations:
            self._conversations[key] = ConversationContext(
                tenant_id=tenant_id,
                phone=phone,
            )

        return self._conversations[key]

    def _normalize_message(self, message: str) -> str:
        """Normaliza mensagem para processamento."""
        # Remove espacos extras
        normalized = " ".join(message.split())
        # Lowercase
        normalized = normalized.lower()
        # Remove acentos comuns
        replacements = {
            "á": "a",
            "à": "a",
            "ã": "a",
            "â": "a",
            "é": "e",
            "ê": "e",
            "í": "i",
            "ó": "o",
            "ô": "o",
            "õ": "o",
            "ú": "u",
            "ç": "c",
        }
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        return normalized

    def _detect_intent(self, message: str) -> Intent:
        """Detecta intencao da mensagem."""
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return intent

        return Intent.UNKNOWN

    async def _process_intent(  # pylint: disable=too-many-return-statements
        self,
        context: ConversationContext,
        intent: Intent,
        message: str,
        contact_name: str | None = None,
    ) -> ChatbotResponse:
        """Processa intencao detectada."""
        # Handlers customizados
        if intent in self._action_handlers:
            handler = self._action_handlers[intent]
            return await handler(context, message, contact_name)

        # Respostas padrao
        if intent == Intent.GREETING:
            name_part = f", {contact_name}" if contact_name else ""
            return ChatbotResponse(
                message=f"Ola{name_part}! Bem-vindo ao atendimento automatico.\n\n"
                "Como posso ajudar voce hoje?\n"
                "Digite *MENU* para ver as opcoes disponiveis.",
                context=context,
            )

        if intent == Intent.MENU:
            context.update_state(ConversationState.MENU)
            return ChatbotResponse(
                message=self.MENU_MESSAGE,
                context=context,
            )

        if intent == Intent.HUMAN:
            return await self.transfer_to_human(
                context.tenant_id,
                context.phone,
                "Solicitado pelo usuario",
            )

        if intent == Intent.GOODBYE:
            context.update_state(ConversationState.COMPLETED)
            return ChatbotResponse(
                message=self.DEFAULT_RESPONSES[Intent.GOODBYE],
                end_conversation=True,
                context=context,
            )

        if intent == Intent.BILLING:
            context.update_state(ConversationState.AWAITING_CPF)
            return ChatbotResponse(
                message=(
                    "Para consultar seus boletos, preciso do seu CPF.\nPor favor, digite apenas os numeros do CPF:"
                ),
                context=context,
            )

        if intent == Intent.SECOND_COPY:
            context.update_state(ConversationState.AWAITING_CPF)
            context.set_data("action", "second_copy")
            return ChatbotResponse(
                message=(
                    "Para emitir a segunda via do boleto, preciso do seu CPF.\n"
                    "Por favor, digite apenas os numeros do CPF:"
                ),
                context=context,
            )

        if intent == Intent.SUPPORT:
            return ChatbotResponse(
                message=(
                    "Para suporte tecnico, voce pode:\n\n"
                    "1. Descrever seu problema aqui\n"
                    "2. Falar com um atendente\n\n"
                    "O que prefere?"
                ),
                context=context,
            )

        # Intencao desconhecida
        return ChatbotResponse(
            message=self.DEFAULT_RESPONSES[Intent.UNKNOWN],
            context=context,
        )

    async def _handle_menu_selection(
        self,
        context: ConversationContext,
        message: str,
    ) -> ChatbotResponse:
        """Processa selecao de menu."""
        # Mapa de opcoes
        menu_map = {
            "1": Intent.BILLING,
            "2": Intent.SECOND_COPY,
            "3": Intent.PAYMENT_STATUS,
            "4": Intent.SUPPORT,
            "5": Intent.SCHEDULE,
            "6": Intent.HUMAN,
        }

        # Verifica se e numero valido
        if message in menu_map:
            intent = menu_map[message]
            context.update_state(ConversationState.NEW)
            return await self._process_intent(context, intent, message, None)

        # Opcao invalida
        return ChatbotResponse(
            message="Opcao invalida. Por favor, digite um numero de 1 a 6:\n\n" + self.MENU_MESSAGE,
            context=context,
        )

    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Valida CPF.

        Args:
            cpf: CPF a validar.

        Returns:
            True se valido.
        """
        # Remove nao-digitos
        digits = "".join(c for c in cpf if c.isdigit())

        if len(digits) != 11:
            return False

        # Verifica sequencias invalidas
        if digits == digits[0] * 11:
            return False

        # Calcula digitos verificadores
        def calc_digit(partial: str, weights: list) -> int:
            total = sum(int(d) * w for d, w in zip(partial, weights, strict=False))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder

        weights1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
        weights2 = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]

        digit1 = calc_digit(digits[:9], weights1)
        digit2 = calc_digit(digits[:9] + str(digit1), weights2)

        return digits[-2:] == f"{digit1}{digit2}"
