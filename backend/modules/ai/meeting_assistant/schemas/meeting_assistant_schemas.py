"""
Meeting Assistant Schemas - Sprint 49.

Schemas Pydantic para validação de dados.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator

from modules.ai.meeting_assistant.models import (
    MeetingStatusEnum,
    MeetingTypeEnum,
    ParticipantStatusEnum,
    ParticipantRoleEnum,
    RecurrenceTypeEnum,
    TaskStatusEnum,
    TaskPriorityEnum,
    TaskTypeEnum,
    DependencyTypeEnum,
)


# ============== Meeting Schemas ==============

class MeetingAgendaItem(BaseModel):
    """Item da agenda."""
    title: str = Field(..., min_length=1, max_length=300)
    duration_minutes: Optional[int] = Field(None, ge=1, le=480)
    presenter: Optional[str] = None
    order: Optional[int] = None
    notes: Optional[str] = None


class MeetingActionItem(BaseModel):
    """Item de ação."""
    description: str = Field(..., min_length=1)
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = Field(default="pending")


class ParticipantCreate(BaseModel):
    """Schema para criar participante."""
    user_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., min_length=5, max_length=200)
    phone: Optional[str] = None
    department: Optional[str] = None
    company: Optional[str] = None
    role: ParticipantRoleEnum = ParticipantRoleEnum.REQUIRED


class ParticipantUpdate(BaseModel):
    """Schema para atualizar participante."""
    role: Optional[ParticipantRoleEnum] = None
    status: Optional[ParticipantStatusEnum] = None
    response_note: Optional[str] = None


class ParticipantResponse(BaseModel):
    """Schema de resposta de participante."""
    id: UUID
    user_id: UUID
    name: str
    email: str
    phone: Optional[str]
    department: Optional[str]
    company: Optional[str]
    role: ParticipantRoleEnum
    status: ParticipantStatusEnum
    response_date: Optional[datetime]
    attended: Optional[bool]
    invitation_sent: bool

    class Config:
        from_attributes = True


class MeetingCreate(BaseModel):
    """Schema para criar reunião."""
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    meeting_type: MeetingTypeEnum = MeetingTypeEnum.INTERNAL
    scheduled_start: datetime
    scheduled_end: datetime
    timezone: str = Field(default="America/Sao_Paulo")

    # Localização
    location: Optional[str] = None
    is_virtual: bool = True
    virtual_link: Optional[str] = None
    virtual_platform: Optional[str] = None
    room_id: Optional[str] = None

    # Recorrência
    is_recurring: bool = False
    recurrence_type: RecurrenceTypeEnum = RecurrenceTypeEnum.NONE
    recurrence_pattern: Dict[str, Any] = Field(default_factory=dict)
    recurrence_end_date: Optional[datetime] = None

    # Organização
    organizer_id: UUID
    organizer_name: Optional[str] = None
    organizer_email: Optional[str] = None
    department: Optional[str] = None
    project_id: Optional[UUID] = None

    # Conteúdo
    agenda: List[MeetingAgendaItem] = Field(default_factory=list)
    objectives: List[str] = Field(default_factory=list)
    preparation_notes: Optional[str] = None

    # Participantes
    participants: List[ParticipantCreate] = Field(default_factory=list)

    # Notificações
    reminder_minutes: List[int] = Field(default=[15, 60, 1440])

    # Categorização
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    priority: int = Field(default=50, ge=0, le=100)

    @validator("scheduled_end")
    def end_after_start(cls, v, values):
        if "scheduled_start" in values and v <= values["scheduled_start"]:
            raise ValueError("scheduled_end deve ser após scheduled_start")
        return v


class MeetingUpdate(BaseModel):
    """Schema para atualizar reunião."""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    meeting_type: Optional[MeetingTypeEnum] = None
    status: Optional[MeetingStatusEnum] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    location: Optional[str] = None
    is_virtual: Optional[bool] = None
    virtual_link: Optional[str] = None
    virtual_platform: Optional[str] = None
    agenda: Optional[List[MeetingAgendaItem]] = None
    objectives: Optional[List[str]] = None
    preparation_notes: Optional[str] = None
    meeting_notes: Optional[str] = None
    action_items: Optional[List[MeetingActionItem]] = None
    decisions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0, le=100)


class MeetingResponse(BaseModel):
    """Schema de resposta de reunião."""
    id: UUID
    meeting_code: str
    title: str
    description: Optional[str]
    meeting_type: MeetingTypeEnum
    status: MeetingStatusEnum
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    duration_minutes: int
    timezone: str
    location: Optional[str]
    is_virtual: bool
    virtual_link: Optional[str]
    virtual_platform: Optional[str]
    is_recurring: bool
    recurrence_type: RecurrenceTypeEnum
    organizer_id: UUID
    organizer_name: Optional[str]
    organizer_email: Optional[str]
    agenda: List[Dict[str, Any]]
    objectives: List[str]
    action_items: List[Dict[str, Any]]
    decisions: List[Dict[str, Any]]
    participants: List[ParticipantResponse] = []
    tags: List[str]
    category: Optional[str]
    priority: int
    ai_suggested: bool
    effectiveness_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MeetingListResponse(BaseModel):
    """Schema de lista de reuniões."""
    items: List[MeetingResponse]
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
    description: Optional[str] = None
    task_type: TaskTypeEnum = TaskTypeEnum.TASK
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM

    # Atribuição
    assignee_id: Optional[UUID] = None
    assignee_name: Optional[str] = None
    reporter_id: Optional[UUID] = None
    reporter_name: Optional[str] = None

    # Datas
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None

    # Estimativas
    estimated_hours: Optional[float] = Field(None, ge=0)
    story_points: Optional[int] = Field(None, ge=0, le=100)

    # Organização
    project_id: Optional[UUID] = None
    project_name: Optional[str] = None
    sprint_id: Optional[UUID] = None
    sprint_name: Optional[str] = None
    parent_task_id: Optional[UUID] = None

    # Relacionamento com reunião
    meeting_id: Optional[UUID] = None
    meeting_action_index: Optional[int] = None

    # Categorização
    tags: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    department: Optional[str] = None

    # Conteúdo
    context: Optional[str] = None
    acceptance_criteria: List[str] = Field(default_factory=list)
    checklist: List[TaskChecklistItem] = Field(default_factory=list)

    # Recorrência
    is_recurring: bool = False
    recurrence_pattern: Dict[str, Any] = Field(default_factory=dict)
    recurrence_end_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    """Schema para atualizar tarefa."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    task_type: Optional[TaskTypeEnum] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    assignee_id: Optional[UUID] = None
    assignee_name: Optional[str] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    story_points: Optional[int] = Field(None, ge=0, le=100)
    project_id: Optional[UUID] = None
    sprint_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    category: Optional[str] = None
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    checklist: Optional[List[TaskChecklistItem]] = None
    is_blocked: Optional[bool] = None
    blocked_reason: Optional[str] = None
    context: Optional[str] = None
    acceptance_criteria: Optional[List[str]] = None


class TaskResponse(BaseModel):
    """Schema de resposta de tarefa."""
    id: UUID
    task_code: str
    title: str
    description: Optional[str]
    task_type: TaskTypeEnum
    status: TaskStatusEnum
    priority: TaskPriorityEnum
    ai_priority_score: Optional[float]
    ai_suggested_priority: Optional[TaskPriorityEnum]
    assignee_id: Optional[UUID]
    assignee_name: Optional[str]
    reporter_id: Optional[UUID]
    reporter_name: Optional[str]
    due_date: Optional[datetime]
    start_date: Optional[datetime]
    completed_at: Optional[datetime]
    ai_suggested_due_date: Optional[datetime]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    ai_estimated_hours: Optional[float]
    story_points: Optional[int]
    project_id: Optional[UUID]
    project_name: Optional[str]
    sprint_id: Optional[UUID]
    sprint_name: Optional[str]
    parent_task_id: Optional[UUID]
    meeting_id: Optional[UUID]
    tags: List[str]
    labels: List[str]
    category: Optional[str]
    progress_percentage: float
    checklist: List[Dict[str, Any]]
    checklist_completed: int
    checklist_total: int
    is_blocked: bool
    blocked_reason: Optional[str]
    ai_generated: bool
    ai_suggestions: List[Dict[str, Any]]
    cycle_time_hours: Optional[float]
    lead_time_hours: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema de lista de tarefas."""
    items: List[TaskResponse]
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
    note_type: Optional[str] = None
    agenda_item_index: Optional[int] = None


class MeetingNoteResponse(BaseModel):
    """Schema de resposta de nota."""
    id: UUID
    meeting_id: UUID
    author_id: UUID
    author_name: Optional[str]
    content: str
    content_type: str
    is_private: bool
    note_type: Optional[str]
    agenda_item_index: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MeetingSummaryResponse(BaseModel):
    """Schema de resposta de resumo."""
    id: UUID
    meeting_id: UUID
    summary: str
    key_points: List[str]
    action_items: List[Dict[str, Any]]
    decisions: List[str]
    next_steps: List[str]
    topics_discussed: List[str]
    keywords: List[str]
    sentiment_analysis: Dict[str, Any]
    ai_model: Optional[str]
    ai_confidence: Optional[float]
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
    reason: Optional[str] = None
    conflicts: List[str] = Field(default_factory=list)


class ScheduleSuggestionRequest(BaseModel):
    """Request para sugestão de agendamento."""
    participant_ids: List[UUID]
    duration_minutes: int = Field(ge=15, le=480)
    preferred_start_date: Optional[datetime] = None
    preferred_end_date: Optional[datetime] = None
    preferred_times: Optional[List[str]] = None  # ["09:00-12:00", "14:00-18:00"]
    avoid_times: Optional[List[str]] = None  # Horários a evitar
    meeting_type: MeetingTypeEnum = MeetingTypeEnum.INTERNAL
    priority: int = Field(default=50, ge=0, le=100)
    max_suggestions: int = Field(default=5, ge=1, le=20)


class ScheduleSuggestionResponse(BaseModel):
    """Response de sugestão de agendamento."""
    suggestions: List[TimeSlot]
    participants_analyzed: int
    conflicts_found: int
    best_slot: Optional[TimeSlot]
    analysis_notes: Optional[str]


# ============== Priority Schemas ==============

class TaskPrioritySuggestion(BaseModel):
    """Sugestão de prioridade para tarefa."""
    task_id: UUID
    task_code: str
    current_priority: TaskPriorityEnum
    suggested_priority: TaskPriorityEnum
    priority_score: float
    factors: Dict[str, Any]
    recommendation: str


class PrioritizationRequest(BaseModel):
    """Request para priorização de tarefas."""
    task_ids: Optional[List[UUID]] = None
    project_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None
    include_completed: bool = False
    recalculate: bool = True


class PrioritizationResponse(BaseModel):
    """Response de priorização."""
    tasks: List[TaskPrioritySuggestion]
    total_analyzed: int
    high_priority_count: int
    overdue_count: int
    blocked_count: int
    recommendations: List[str]


# ============== Dashboard Schemas ==============

class MeetingAssistantDashboard(BaseModel):
    """Dashboard do assistente de reuniões/tarefas."""
    # Reuniões
    total_meetings: int
    meetings_today: int
    meetings_this_week: int
    upcoming_meetings: List[MeetingResponse]
    meetings_by_status: Dict[str, int]
    meetings_by_type: Dict[str, int]

    # Tarefas
    total_tasks: int
    tasks_todo: int
    tasks_in_progress: int
    tasks_completed_this_week: int
    overdue_tasks: int
    blocked_tasks: int
    tasks_by_priority: Dict[str, int]
    tasks_by_status: Dict[str, int]

    # IA
    ai_suggestions_pending: int
    auto_scheduled_meetings: int
    tasks_from_meetings: int

    # Métricas
    avg_meeting_duration_minutes: float
    avg_task_completion_time_hours: float
    meeting_effectiveness_avg: Optional[float]

    # Timeline
    recent_activity: List[Dict[str, Any]]
