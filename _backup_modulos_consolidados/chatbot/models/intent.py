"""Intent e Entity Models - NLU do Chatbot.

Sprint 38 - Chatbot IA.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.models.base import Base


class IntentCategory(str, enum.Enum):
    """Categoria da intencao."""

    GREETING = "greeting"
    FAREWELL = "farewell"
    THANKS = "thanks"
    HELP = "help"
    INFORMATION = "information"
    ACTION = "action"
    COMPLAINT = "complaint"
    FEEDBACK = "feedback"
    SALES = "sales"
    SUPPORT = "support"
    BILLING = "billing"
    SCHEDULING = "scheduling"
    FAQ = "faq"
    CHITCHAT = "chitchat"
    FALLBACK = "fallback"
    CUSTOM = "custom"


class EntityType(str, enum.Enum):
    """Tipo de entidade."""

    # Basicos
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    DURATION = "duration"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"

    # Contato
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"

    # Documentos BR
    CPF = "cpf"
    CNPJ = "cnpj"
    CEP = "cep"

    # Localizacao
    ADDRESS = "address"
    CITY = "city"
    STATE = "state"
    COUNTRY = "country"
    LOCATION = "location"

    # Negocio
    PRODUCT = "product"
    SERVICE = "service"
    ORDER_ID = "order_id"
    TICKET_ID = "ticket_id"
    CONTRACT_ID = "contract_id"

    # Pessoa
    PERSON_NAME = "person_name"
    COMPANY_NAME = "company_name"

    # Custom
    CUSTOM = "custom"
    LIST = "list"
    REGEX = "regex"


class Intent(Base):
    """Modelo de intencao do chatbot."""

    __tablename__ = "chatbot_intents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    chatbot_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    name = Column(String(100), nullable=False, index=True)
    display_name = Column(String(200))
    description = Column(Text)
    category = Column(Enum(IntentCategory), default=IntentCategory.CUSTOM, index=True)

    # Exemplos de treinamento
    training_phrases = Column(ARRAY(String), default=[])
    # Ex: ["qual o horario de funcionamento", "que horas vocês abrem", "horario de atendimento"]

    # Sinonimos e variacoes
    synonyms = Column(JSONB, default={})
    # Ex: {"horario": ["hora", "horário", "horas"], "funcionamento": ["atendimento", "abertura"]}

    # Entidades esperadas
    required_entities = Column(ARRAY(String), default=[])
    optional_entities = Column(ARRAY(String), default=[])

    # Resposta padrao
    responses = Column(ARRAY(String), default=[])
    # Ex: ["Nosso horario é de 8h às 18h", "Funcionamos de segunda a sexta, das 8h às 18h"]

    # Resposta rica
    rich_responses = Column(JSONB, default=[])
    # Estrutura: [
    #   {"type": "text", "content": "Nosso horário..."},
    #   {"type": "image", "url": "...", "alt": "..."},
    #   {"type": "buttons", "buttons": [{"text": "Ver mais", "action": "..."}]},
    #   {"type": "card", "title": "...", "subtitle": "...", "image": "...", "buttons": []}
    # ]

    # Acao
    action = Column(String(100))  # Nome da acao a executar
    action_config = Column(JSONB, default={})
    # Ex: {"type": "api_call", "endpoint": "/api/horarios", "method": "GET"}

    # Webhook
    webhook_url = Column(String(500))
    webhook_headers = Column(JSONB, default={})

    # Contexto
    input_contexts = Column(ARRAY(String), default=[])
    output_contexts = Column(ARRAY(String), default=[])
    context_lifespan = Column(Integer, default=5)  # Turnos

    # Follow-up intents
    parent_intent_id = Column(UUID(as_uuid=True), index=True)
    followup_intents = Column(ARRAY(UUID(as_uuid=True)), default=[])

    # Prioridade
    priority = Column(Integer, default=50)  # 0-100, maior = mais prioritario

    # Confirmacao
    requires_confirmation = Column(Boolean, default=False)
    confirmation_message = Column(String(500))

    # Slots/Parametros
    slots = Column(JSONB, default=[])
    # Estrutura: [
    #   {"name": "data", "entity": "date", "required": True, "prompt": "Qual data?"},
    #   {"name": "horario", "entity": "time", "required": True, "prompt": "Qual horário?"}
    # ]

    # Metricas
    total_matches = Column(Integer, default=0)
    avg_confidence = Column(Float)
    last_matched_at = Column(DateTime)

    # Treinamento
    is_trained = Column(Boolean, default=False)
    trained_at = Column(DateTime)
    training_samples = Column(Integer, default=0)

    # Controle
    is_system = Column(Boolean, default=False)  # Intent do sistema (nao editavel)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Intent {self.name}>"


class Entity(Base):
    """Modelo de entidade do chatbot."""

    __tablename__ = "chatbot_entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    chatbot_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    name = Column(String(100), nullable=False, index=True)
    display_name = Column(String(200))
    description = Column(Text)
    entity_type = Column(Enum(EntityType), default=EntityType.CUSTOM, index=True)

    # Valores predefinidos (para LIST)
    values = Column(JSONB, default=[])
    # Estrutura: [
    #   {"value": "visa", "synonyms": ["cartao visa", "visa card"]},
    #   {"value": "mastercard", "synonyms": ["master", "master card"]}
    # ]

    # Regex pattern (para REGEX)
    regex_pattern = Column(String(500))
    regex_flags = Column(String(20))

    # Validacao
    validation_regex = Column(String(500))
    validation_message = Column(String(500))

    # Normalizacao
    normalize = Column(Boolean, default=True)
    normalization_rules = Column(JSONB, default={})
    # Ex: {"lowercase": true, "strip": true, "remove_accents": false}

    # Extracao
    extraction_patterns = Column(ARRAY(String), default=[])
    # Patterns para ajudar na extracao

    # Fuzzy matching
    enable_fuzzy = Column(Boolean, default=True)
    fuzzy_threshold = Column(Float, default=0.8)

    # Metricas
    total_extractions = Column(Integer, default=0)
    avg_confidence = Column(Float)
    last_extracted_at = Column(DateTime)

    # Treinamento
    is_trained = Column(Boolean, default=False)
    trained_at = Column(DateTime)

    # Controle
    is_system = Column(Boolean, default=False)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Entity {self.name} ({self.entity_type.value})>"


class IntentExample(Base):
    """Modelo de exemplo de treinamento para intent."""

    __tablename__ = "chatbot_intent_examples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    intent_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Texto do exemplo
    text = Column(Text, nullable=False)
    language = Column(String(10), default="pt_BR")

    # Entidades anotadas
    entities = Column(JSONB, default=[])
    # Estrutura: [
    #   {"entity": "date", "value": "amanha", "start": 10, "end": 16},
    #   {"entity": "time", "value": "14h", "start": 20, "end": 23}
    # ]

    # Origem
    source = Column(String(50), default="manual")  # manual, imported, generated, user_feedback
    source_id = Column(String(200))  # ID da origem (ex: conversation_id)

    # Validacao
    is_validated = Column(Boolean, default=False)
    validated_by = Column(UUID(as_uuid=True))
    validated_at = Column(DateTime)

    # Qualidade
    quality_score = Column(Float)  # 0-1
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(UUID(as_uuid=True))

    # Controle
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<IntentExample {self.text[:30]}...>"
