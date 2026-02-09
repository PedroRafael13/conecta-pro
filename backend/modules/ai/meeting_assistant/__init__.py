"""
AI Meeting/Task Assistant Module - Sprint 49.

Módulo de assistente inteligente para reuniões e tarefas:
- Agendamento inteligente de reuniões
- Priorização automática de tarefas
- Geração de resumos automáticos
- Sugestões de horários
- Notificações inteligentes
"""

from .models import (
    Meeting,
    MeetingNote,
    MeetingParticipant,
    MeetingSummary,
    Task,
    TaskDependency,
)
from .schemas import (
    MeetingCreate,
    MeetingResponse,
    MeetingUpdate,
    ScheduleSuggestionRequest,
    ScheduleSuggestionResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)

__all__ = [
    # Models
    "Meeting",
    "MeetingParticipant",
    "Task",
    "TaskDependency",
    "MeetingNote",
    "MeetingSummary",
    # Schemas
    "MeetingCreate",
    "MeetingUpdate",
    "MeetingResponse",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "ScheduleSuggestionRequest",
    "ScheduleSuggestionResponse",
]
