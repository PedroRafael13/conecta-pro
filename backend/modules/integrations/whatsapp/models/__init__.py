"""Models do modulo WhatsApp.

Sprint 31 - Automacoes WhatsApp.
"""

from modules.integrations.whatsapp.models.message_log import (
    ConversationType,
    MessageDirection,
    MessageLog,
)
from modules.integrations.whatsapp.models.message_queue import (
    MessagePriority,
    MessagePurpose,
    MessageQueue,
    MessageStatus,
    MessageType,
)
from modules.integrations.whatsapp.models.message_template import (
    MessageTemplate,
    TemplateCategory,
    TemplateStatus,
    TemplateType,
)
from modules.integrations.whatsapp.models.whatsapp_config import (
    WhatsAppConfig,
    WhatsAppProvider,
    WhatsAppStatus,
)

__all__ = [
    # WhatsApp Config
    "WhatsAppConfig",
    "WhatsAppStatus",
    "WhatsAppProvider",
    # Message Template
    "MessageTemplate",
    "TemplateCategory",
    "TemplateStatus",
    "TemplateType",
    # Message Queue
    "MessageQueue",
    "MessageStatus",
    "MessagePriority",
    "MessageType",
    "MessagePurpose",
    # Message Log
    "MessageLog",
    "MessageDirection",
    "ConversationType",
]
