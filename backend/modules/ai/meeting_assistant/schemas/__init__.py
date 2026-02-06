"""
Meeting Assistant Schemas - Sprint 49.
"""

from .meeting_assistant_schemas import (
    # Meeting schemas
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingListResponse,
    MeetingAgendaItem,
    MeetingActionItem,
    # Participant schemas
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantResponse,
    # Task schemas
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskChecklistItem,
    # Note/Summary schemas
    MeetingNoteCreate,
    MeetingNoteResponse,
    MeetingSummaryResponse,
    # Schedule suggestion schemas
    ScheduleSuggestionRequest,
    ScheduleSuggestionResponse,
    TimeSlot,
    # Priority schemas
    TaskPrioritySuggestion,
    PrioritizationRequest,
    PrioritizationResponse,
    # Dashboard
    MeetingAssistantDashboard,
)

__all__ = [
    "MeetingCreate",
    "MeetingUpdate",
    "MeetingResponse",
    "MeetingListResponse",
    "MeetingAgendaItem",
    "MeetingActionItem",
    "ParticipantCreate",
    "ParticipantUpdate",
    "ParticipantResponse",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "TaskChecklistItem",
    "MeetingNoteCreate",
    "MeetingNoteResponse",
    "MeetingSummaryResponse",
    "ScheduleSuggestionRequest",
    "ScheduleSuggestionResponse",
    "TimeSlot",
    "TaskPrioritySuggestion",
    "PrioritizationRequest",
    "PrioritizationResponse",
    "MeetingAssistantDashboard",
]
