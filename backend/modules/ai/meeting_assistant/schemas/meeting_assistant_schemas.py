"""
Meeting Assistant Schemas - Sprint 49.

Schemas Pydantic para validação de dados.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.ai.meeting_assistant.models import (
    MeetingStatusEnum,
    MeetingTypeEnum,
    ParticipantRoleEnum,
    ParticipantStatusEnum,
    RecurrenceTypeEnum,
    TaskPriorityEnum,
    TaskStatusEnum,
    TaskTypeEnum,
)

# ============== Meeting Schemas ==============


class MeetingAgendaItem(BaseModel):
    """Item da agenda."""

    title: str = Field(..., min_length=1, max_length=300)
    duration_minutes: int | None = Field(None, ge=1, le=480)
    presenter: str | None = None
    order: int | None = None
    notes: str | None = None


class MeetingActionItem(BaseModel):
    """Item de ação."""

    description: str = Field(..., min_length=1)
    assignee_id: str | None = None
    assignee_name: str | None = None
    due_date: datetime | None = None
    status: str = Field(default="pending")


class ParticipantCreate(BaseModel):
    """Schema para criar participante."""

    user_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., min_length=5, max_length=200)
    phone: str | None = None
    department: str | None = None
    company: str | None = None
    role: ParticipantRoleEnum = ParticipantRoleEnum.REQUIRED


class ParticipantUpdate(BaseModel):
    """Schema para atualizar participante."""

    role: ParticipantRoleEnum | None = None
    status: ParticipantStatusEnum | None = None
    response_note: str | None = None


class ParticipantResponse(BaseModel):
    """Schema de resposta de participante."""

    id: UUID
    user_id: UUID
    name: str
    email: str
    phone: str | None
    department: str | None
    company: str | None
    role: ParticipantRoleEnum
    status: ParticipantStatusEnum
    response_date: datetime | None
    attended: bool | None
    invitation_sent: bool

    class Config:
        from_attributes = True


class MeetingCreate(BaseModel):
    """Schema para criar reunião."""

    title: str = Field(..., min_length=1, max_length=300)
    description: str | None = None
    meeting_type: MeetingTypeEnum = MeetingTypeEnum.INTERNAL
    scheduled_start: datetime
    scheduled_end: datetime
    timezone: str = Field(default="America/Sao_Paulo")

    # Localização
    location: str | None = None
    is_virtual: bool = True
    virtual_link: str | None = None
    virtual_platform: str | None = None
    room_id: str | None = None

    # Recorrência
    is_recurring: bool = False
    recurrence_type: RecurrenceTypeEnum = RecurrenceTypeEnum.NONE
    recurrence_pattern: dict[str, Any] = Field(default_factory=dict)
    recurrence_end_date: datetime | None = None

    # Organização
    organizer_id: UUID
    organizer_name: str | None = None
    organizer_email: str | None = None
    department: str | None = None
    project_id: UUID | None = None

    # Conteúdo
    agenda: list[MeetingAgendaItem] = Field(default_factory=list)
    objectives: list[str] = Field(default_factory=list)
    preparation_notes: str | None = None

    # Participantes
    participants: list[ParticipantCreate] = Field(default_factory=list)

    # Notificações
    reminder_minutes: list[int] = Field(default=[15, 60, 1440])

    # Categorização
    tags: list[str] = Field(default_factory=list)
    category: str | None = None
    priority: int = Field(default=50, ge=0, le=100)

    @field_validator("scheduled_end")
    @classmethod
    def end_after_start(cls, v: Any, info) -> Any:
        values = info.data
        if "scheduled_start" in values and v <= values["scheduled_start"]:
            raise ValueError("scheduled_end deve ser após scheduled_start")
        return v


class MeetingUpdate(BaseModel):
    """Schema para atualizar reunião."""

    title: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = None
    meeting_type: MeetingTypeEnum | None = None
    status: MeetingStatusEnum | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    location: str | None = None
    is_virtual: bool | None = None
    virtual_link: str | None = None
    virtual_platform: str | None = None
    agenda: list[MeetingAgendaItem] | None = None
    objectives: list[str] | None = None
    preparation_notes: str | None = None
    meeting_notes: str | None = None
    action_items: list[MeetingActionItem] | None = None
    decisions: list[str] | None = None
    tags: list[str] | None = None
    category: str | None = None
    priority: int | None = Field(None, ge=0, le=100)


class MeetingResponse(BaseModel):
    """Schema de resposta de reunião."""

    id: UUID
    meeting_code: str
    title: str
    description: str | None
    meeting_type: MeetingTypeEnum
    status: MeetingStatusEnum
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: datetime | None
    actual_end: datetime | None
    duration_minutes: int
    timezone: str
    location: str | None
    is_virtual: bool
    virtual_link: str | None
    virtual_platform: str | None
    is_recurring: bool
    recurrence_type: RecurrenceTypeEnum
    organizer_id: UUID
    organizer_name: str | None
    organizer_email: str | None
    agenda: list[dict[str, Any]]
    objectives: list[str]
    action_items: list[dict[str, Any]]
    decisions: list[dict[str, Any]]
    participants: list[ParticipantResponse] = []
    tags: list[str]
    category: str | None
    priority: int
    ai_suggested: bool
    effectiveness_score: float | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MeetingListResponse(BaseModel):
    """Schema de lista de reuniões."""

    items: list[MeetingResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============== Task Schemas ==============


class TaskChecklistItem(BaseModel):
    """Item do checklist."""

    item: str = Field(..., min_length=1)
    completed: bool = False


class TaskCreate(BaseModel):
    """Schema para criar tarefa."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    task_type: TaskTypeEnum = TaskTypeEnum.TASK
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM

    # Atribuição
    assignee_id: UUID | None = None
    assignee_name: str | None = None
    reporter_id: UUID | None = None
    reporter_name: str | None = None

    # Datas
    due_date: datetime | None = None
    start_date: datetime | None = None

    # Estimativas
    estimated_hours: float | None = Field(None, ge=0)
    story_points: int | None = Field(None, ge=0, le=100)

    # Organização
    project_id: UUID | None = None
    project_name: str | None = None
    sprint_id: UUID | None = None
    sprint_name: str | None = None
    parent_task_id: UUID | None = None

    # Relacionamento com reunião
    meeting_id: UUID | None = None
    meeting_action_index: int | None = None

    # Categorização
    tags: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    category: str | None = None
    department: str | None = None

    # Conteúdo
    context: str | None = None
    acceptance_criteria: list[str] = Field(default_factory=list)
    checklist: list[TaskChecklistItem] = Field(default_factory=list)

    # Recorrência
    is_recurring: bool = False
    recurrence_pattern: dict[str, Any] = Field(default_factory=dict)
    recurrence_end_date: datetime | None = None


class TaskUpdate(BaseModel):
    """Schema para atualizar tarefa."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    task_type: TaskTypeEnum | None = None
    status: TaskStatusEnum | None = None
    priority: TaskPriorityEnum | None = None
    assignee_id: UUID | None = None
    assignee_name: str | None = None
    due_date: datetime | None = None
    start_date: datetime | None = None
    estimated_hours: float | None = Field(None, ge=0)
    actual_hours: float | None = Field(None, ge=0)
    story_points: int | None = Field(None, ge=0, le=100)
    project_id: UUID | None = None
    sprint_id: UUID | None = None
    tags: list[str] | None = None
    labels: list[str] | None = None
    category: str | None = None
    progress_percentage: float | None = Field(None, ge=0, le=100)
    checklist: list[TaskChecklistItem] | None = None
    is_blocked: bool | None = None
    blocked_reason: str | None = None
    context: str | None = None
    acceptance_criteria: list[str] | None = None


class TaskResponse(BaseModel):
    """Schema de resposta de tarefa."""

    id: UUID
    task_code: str
    title: str
    description: str | None
    task_type: TaskTypeEnum
    status: TaskStatusEnum
    priority: TaskPriorityEnum
    ai_priority_score: float | None
    ai_suggested_priority: TaskPriorityEnum | None
    assignee_id: UUID | None
    assignee_name: str | None
    reporter_id: UUID | None
    reporter_name: str | None
    due_date: datetime | None
    start_date: datetime | None
    completed_at: datetime | None
    ai_suggested_due_date: datetime | None
    estimated_hours: float | None
    actual_hours: float | None
    ai_estimated_hours: float | None
    story_points: int | None
    project_id: UUID | None
    project_name: str | None
    sprint_id: UUID | None
    sprint_name: str | None
    parent_task_id: UUID | None
    meeting_id: UUID | None
    tags: list[str]
    labels: list[str]
    category: str | None
    progress_percentage: float
    checklist: list[dict[str, Any]]
    checklist_completed: int
    checklist_total: int
    is_blocked: bool
    blocked_reason: str | None
    ai_generated: bool
    ai_suggestions: list[dict[str, Any]]
    cycle_time_hours: float | None
    lead_time_hours: float | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema de lista de tarefas."""

    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============== Note/Summary Schemas ==============


class MeetingNoteCreate(BaseModel):
    """Schema para criar nota."""

    content: str = Field(..., min_length=1)
    content_type: str = Field(default="text")
    is_private: bool = False
    note_type: str | None = None
    agenda_item_index: int | None = None


class MeetingNoteResponse(BaseModel):
    """Schema de resposta de nota."""

    id: UUID
    meeting_id: UUID
    author_id: UUID
    author_name: str | None
    content: str
    content_type: str
    is_private: bool
    note_type: str | None
    agenda_item_index: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MeetingSummaryResponse(BaseModel):
    """Schema de resposta de resumo."""

    id: UUID
    meeting_id: UUID
    summary: str
    key_points: list[str]
    action_items: list[dict[str, Any]]
    decisions: list[str]
    next_steps: list[str]
    topics_discussed: list[str]
    keywords: list[str]
    sentiment_analysis: dict[str, Any]
    ai_model: str | None
    ai_confidence: float | None
    is_reviewed: bool
    is_published: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Schedule Suggestion Schemas ==============


class TimeSlot(BaseModel):
    """Slot de tempo disponível."""

    start: datetime
    end: datetime
    score: float = Field(ge=0, le=100)
    reason: str | None = None
    conflicts: list[str] = Field(default_factory=list)


class ScheduleSuggestionRequest(BaseModel):
    """Request para sugestão de agendamento."""

    participant_ids: list[UUID]
    duration_minutes: int = Field(ge=15, le=480)
    preferred_start_date: datetime | None = None
    preferred_end_date: datetime | None = None
    preferred_times: list[str] | None = None  # ["09:00-12:00", "14:00-18:00"]
    avoid_times: list[str] | None = None  # Horários a evitar
    meeting_type: MeetingTypeEnum = MeetingTypeEnum.INTERNAL
    priority: int = Field(default=50, ge=0, le=100)
    max_suggestions: int = Field(default=5, ge=1, le=20)


class ScheduleSuggestionResponse(BaseModel):
    """Response de sugestão de agendamento."""

    suggestions: list[TimeSlot]
    participants_analyzed: int
    conflicts_found: int
    best_slot: TimeSlot | None
    analysis_notes: str | None


# ============== Priority Schemas ==============


class TaskPrioritySuggestion(BaseModel):
    """Sugestão de prioridade para tarefa."""

    task_id: UUID
    task_code: str
    current_priority: TaskPriorityEnum
    suggested_priority: TaskPriorityEnum
    priority_score: float
    factors: dict[str, Any]
    recommendation: str


class PrioritizationRequest(BaseModel):
    """Request para priorização de tarefas."""

    task_ids: list[UUID] | None = None
    project_id: UUID | None = None
    assignee_id: UUID | None = None
    include_completed: bool = False
    recalculate: bool = True


class PrioritizationResponse(BaseModel):
    """Response de priorização."""

    tasks: list[TaskPrioritySuggestion]
    total_analyzed: int
    high_priority_count: int
    overdue_count: int
    blocked_count: int
    recommendations: list[str]


# ============== Dashboard Schemas ==============


class MeetingAssistantDashboard(BaseModel):
    """Dashboard do assistente de reuniões/tarefas."""

    # Reuniões
    total_meetings: int
    meetings_today: int
    meetings_this_week: int
    upcoming_meetings: list[MeetingResponse]
    meetings_by_status: dict[str, int]
    meetings_by_type: dict[str, int]

    # Tarefas
    total_tasks: int
    tasks_todo: int
    tasks_in_progress: int
    tasks_completed_this_week: int
    overdue_tasks: int
    blocked_tasks: int
    tasks_by_priority: dict[str, int]
    tasks_by_status: dict[str, int]

    # IA
    ai_suggestions_pending: int
    auto_scheduled_meetings: int
    tasks_from_meetings: int

    # Métricas
    avg_meeting_duration_minutes: float
    avg_task_completion_time_hours: float
    meeting_effectiveness_avg: float | None

    # Timeline
    recent_activity: list[dict[str, Any]]
