"""ChatbotConfig Model - Configuracao do Chatbot por Tenant.

Sprint 38 - Chatbot IA.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from core.models.base import Base


class ChatbotStatus(str, enum.Enum):
    """Status do chatbot."""

    DRAFT = "draft"
    TRAINING = "training"
    ACTIVE = "active"
    PAUSED = "paused"
    MAINTENANCE = "maintenance"
    DISABLED = "disabled"


class ChatbotPersonality(str, enum.Enum):
    """Personalidade do chatbot."""

    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    SUPPORTIVE = "supportive"


class ChatbotProvider(str, enum.Enum):
    """Provedor de NLU/LLM."""

    INTERNAL = "internal"  # Motor interno
    OPENAI = "openai"  # GPT-4, GPT-3.5
    ANTHROPIC = "anthropic"  # Claude
    GOOGLE = "google"  # Dialogflow, Gemini
    AWS = "aws"  # Lex, Bedrock
    AZURE = "azure"  # LUIS, Azure OpenAI
    RASA = "rasa"  # Rasa Open Source
    CUSTOM = "custom"  # Modelo customizado


class ChatbotConfig(Base):
    """Modelo de configuracao do chatbot."""

    __tablename__ = "chatbot_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    name = Column(String(200), nullable=False)
    slug = Column(String(200), index=True)
    description = Column(Text)
    avatar_url = Column(String(500))

    # Status
    status = Column(Enum(ChatbotStatus), default=ChatbotStatus.DRAFT, index=True)
    status_reason = Column(String(200))
    status_changed_at = Column(DateTime)

    # Personalidade
    personality = Column(Enum(ChatbotPersonality), default=ChatbotPersonality.PROFESSIONAL)
    greeting_message = Column(Text, default="Ola! Como posso ajudar?")
    fallback_message = Column(Text, default="Desculpe, nao entendi. Pode reformular?")
    goodbye_message = Column(Text, default="Obrigado pelo contato! Ate logo!")
    offline_message = Column(Text, default="Nosso atendimento esta offline no momento.")
    transfer_message = Column(Text, default="Vou transferir voce para um atendente.")

    # Provedor NLU/LLM
    provider = Column(Enum(ChatbotProvider), default=ChatbotProvider.INTERNAL)
    provider_config = Column(JSONB, default={})
    # Estrutura: {
    #   "api_key": "...",
    #   "model": "gpt-4",
    #   "temperature": 0.7,
    #   "max_tokens": 500,
    #   "endpoint": "..."
    # }

    # Modelo interno
    model_version = Column(String(50))
    model_trained_at = Column(DateTime)
    model_accuracy = Column(Float)

    # Configuracoes de NLU
    confidence_threshold = Column(Float, default=0.7)  # Minimo para aceitar intent
    ambiguity_threshold = Column(Float, default=0.15)  # Diferenca para considerar ambiguo
    max_context_turns = Column(Integer, default=10)  # Turnos de contexto
    enable_spell_check = Column(Boolean, default=True)
    enable_sentiment = Column(Boolean, default=True)
    enable_entity_extraction = Column(Boolean, default=True)

    # Idiomas
    primary_language = Column(String(10), default="pt_BR")
    supported_languages = Column(ARRAY(String), default=["pt_BR", "en_US", "es_ES"])
    auto_detect_language = Column(Boolean, default=True)

    # Canais habilitados
    enabled_channels = Column(ARRAY(String), default=["web", "whatsapp", "telegram"])
    channel_configs = Column(JSONB, default={})
    # Estrutura: {
    #   "web": {"widget_color": "#007bff", "position": "bottom-right"},
    #   "whatsapp": {"phone_number": "+55..."},
    #   "telegram": {"bot_token": "..."}
    # }

    # Horario de funcionamento
    business_hours = Column(JSONB, default={})
    # Estrutura: {
    #   "monday": {"start": "08:00", "end": "18:00"},
    #   "tuesday": {"start": "08:00", "end": "18:00"},
    #   ...
    # }
    timezone = Column(String(50), default="America/Sao_Paulo")
    enforce_business_hours = Column(Boolean, default=False)

    # Handoff para humano
    enable_handoff = Column(Boolean, default=True)
    handoff_triggers = Column(ARRAY(String), default=["falar com atendente", "humano", "pessoa real"])
    handoff_after_failures = Column(Integer, default=3)  # Transferir apos N falhas
    handoff_queue_id = Column(UUID(as_uuid=True))  # Fila de atendimento

    # Rate limiting
    rate_limit_per_user = Column(Integer, default=60)  # Mensagens por minuto
    rate_limit_window = Column(Integer, default=60)  # Janela em segundos
    block_after_limit = Column(Boolean, default=False)

    # Respostas rapidas
    quick_replies = Column(JSONB, default=[])
    # Estrutura: [
    #   {"id": "qr1", "text": "Horario de funcionamento", "intent": "business_hours"},
    #   {"id": "qr2", "text": "Falar com atendente", "action": "handoff"}
    # ]

    # Menus persistentes
    persistent_menu = Column(JSONB, default=[])
    # Estrutura: [
    #   {"type": "postback", "title": "Menu", "payload": "SHOW_MENU"},
    #   {"type": "web_url", "title": "Site", "url": "https://..."}
    # ]

    # Intencoes especiais
    welcome_intent = Column(String(100), default="greeting")
    fallback_intent = Column(String(100), default="fallback")
    goodbye_intent = Column(String(100), default="goodbye")
    help_intent = Column(String(100), default="help")

    # Analytics
    track_conversations = Column(Boolean, default=True)
    track_messages = Column(Boolean, default=True)
    track_intents = Column(Boolean, default=True)
    track_entities = Column(Boolean, default=True)
    track_sentiment = Column(Boolean, default=True)

    # Metricas
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    avg_response_time_ms = Column(Integer)
    avg_conversation_duration_seconds = Column(Integer)
    handoff_rate = Column(Float)
    resolution_rate = Column(Float)
    satisfaction_score = Column(Float)

    # Integracao com sistemas
    crm_integration = Column(Boolean, default=False)
    crm_config = Column(JSONB, default={})
    ticket_integration = Column(Boolean, default=False)
    ticket_config = Column(JSONB, default={})
    knowledge_base_id = Column(UUID(as_uuid=True))

    # Metadata
    extra_data = Column(JSONB, default={})
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    # Controle
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ChatbotConfig {self.name} ({self.status.value})>"

    def is_available(self) -> bool:
        """Verifica se o chatbot esta disponivel."""
        return self.active and self.status == ChatbotStatus.ACTIVE

    def is_within_business_hours(self, current_time: Optional[datetime] = None) -> bool:
        """Verifica se esta dentro do horario de funcionamento."""
        if not self.enforce_business_hours:
            return True

        if not self.business_hours:
            return True

        from datetime import datetime as dt

        now = current_time or dt.now()
        day_name = now.strftime("%A").lower()

        if day_name not in self.business_hours:
            return False

        hours = self.business_hours[day_name]
        if not hours.get("start") or not hours.get("end"):
            return False

        start = dt.strptime(hours["start"], "%H:%M").time()
        end = dt.strptime(hours["end"], "%H:%M").time()
        current = now.time()

        return start <= current <= end
