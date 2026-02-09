"""
Meeting Assistant Schemas - Sprint 49.
"""

from .meeting_assistant_schemas import (
    MeetingActionItem,
    MeetingAgendaItem,
    # Dashboard
    MeetingAssistantDashboard,
    # Meeting schemas
    MeetingCreate,
    MeetingListResponse,
    # Note/Summary schemas
    MeetingNoteCreate,
    MeetingNoteResponse,
    MeetingResponse,
    MeetingSummaryResponse,
    MeetingUpdate,
    # Participant schemas
    ParticipantCreate,
    ParticipantResponse,
    ParticipantUpdate,
    PrioritizationRequest,
    PrioritizationResponse,
    # Schedule suggestion schemas
    ScheduleSuggestionRequest,
    ScheduleSuggestionResponse,
    TaskChecklistItem,
    # Task schemas
    TaskCreate,
    TaskListResponse,
    # Priority schemas
    TaskPrioritySuggestion,
    TaskResponse,
    TaskUpdate,
    TimeSlot,
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
