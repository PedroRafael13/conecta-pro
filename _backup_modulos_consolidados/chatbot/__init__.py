"""Módulo Chatbot IA.

Sprint 38 - Sistema de Chatbot com NLU.

Features:
- Natural Language Understanding (NLU)
- Intent detection e entity extraction
- Dialog management com contexto
- Slot filling e confirmação
- Análise de sentimento
- Suporte multi-canal (web, whatsapp, telegram, etc.)
- Treinamento de modelo
- Analytics e feedback
- Handoff para atendente humano
"""

# Lazy import para evitar dependências circulares em testes
# Use: from modules.ai.chatbot.controllers import router


def get_router():
    """Retorna o router do chatbot (lazy import)."""
    from modules.ai.chatbot.controllers import router
    return router


__all__ = ["get_router"]
