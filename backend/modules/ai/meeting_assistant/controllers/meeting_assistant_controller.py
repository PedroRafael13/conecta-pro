"""
Meeting Assistant Controller - Sprint 49.

Endpoints REST para gestão de reuniões e tarefas.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.auth.dependencies import get_current_user, CurrentActiveUser

from modules.ai.meeting_assistant.models import (
    Meeting,
    Task,
    MeetingStatusEnum,
    TaskStatusEnum,
    TaskPriorityEnum,
    ParticipantStatusEnum,
)
from modules.ai.meeting_assistant.schemas import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingListResponse,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantResponse,
    MeetingNoteCreate,
    MeetingNoteResponse,
    MeetingSummaryResponse,
    ScheduleSuggestionRequest,
    ScheduleSuggestionResponse,
    PrioritizationRequest,
    PrioritizationResponse,
    MeetingAssistantDashboard,
)
from modules.ai.meeting_assistant.repositories import MeetingAssistantRepository
from modules.ai.meeting_assistant.services import (
    ScheduleOptimizer,
    TaskPrioritizer,
    MeetingSummarizer,
    SmartNotifier,
)

router = APIRouter(prefix="/meeting-assistant", tags=["AI Meeting Assistant"])


def get_repository(db: Session = Depends(get_db)) -> MeetingAssistantRepository:
    return MeetingAssistantRepository(db)


# ============== Meeting Endpoints ==============

@router.post("/meetings", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    data: MeetingCreate,
    current_user: CurrentActiveUser = ...,  # Required
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Cria nova reunião."""
    meeting = repo.create_meeting(data, current_user.id)
    return meeting


@router.get("/meetings", response_model=MeetingListResponse)
async def list_meetings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[MeetingStatusEnum] = None,
    organizer_id: Optional[uuid.UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    meeting_type: Optional[str] = None,
    current_user: CurrentActiveUser = None,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Lista reuniões com filtros."""
    skip = (page - 1) * page_size
    meetings, total = repo.list_meetings(
        skip=skip,
        limit=page_size,
        status=status,
        organizer_id=organizer_id,
        start_date=start_date,
        end_date=end_date,
        meeting_type=meeting_type
    )

    return MeetingListResponse(
        items=meetings,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/meetings/my", response_model=List[MeetingResponse])
async def get_my_meetings(
    upcoming_only: bool = True,
    limit: int = Query(10, ge=1, le=50),
    current_user: CurrentActiveUser = None,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Busca reuniões do usuário atual."""
    if upcoming_only:
        return repo.get_upcoming_meetings(current_user.id, limit)
    meetings, _ = repo.list_meetings(
        participant_id=current_user.id,
        limit=limit
    )
    return meetings


@router.get("/meetings/today", response_model=List[MeetingResponse])
async def get_meetings_today(
    current_user: CurrentActiveUser = None,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Busca reuniões de hoje."""
    return repo.get_meetings_today(current_user.id)


@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Busca reunião por ID."""
    meeting = repo.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    return meeting


@router.put("/meetings/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: uuid.UUID,
    data: MeetingUpdate,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Atualiza reunião."""
    meeting = repo.update_meeting(meeting_id, data)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    return meeting


@router.delete("/meetings/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Deleta reunião."""
    if not repo.delete_meeting(meeting_id):
        raise HTTPException(status_code=404, detail="Reunião não encontrada")


@router.post("/meetings/{meeting_id}/start", response_model=MeetingResponse)
async def start_meeting(
    meeting_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Inicia reunião."""
    meeting = repo.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")

    meeting.start_meeting()
    repo.db.commit()
    return meeting


@router.post("/meetings/{meeting_id}/end", response_model=MeetingResponse)
async def end_meeting(
    meeting_id: uuid.UUID,
    notes: Optional[str] = None,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Finaliza reunião."""
    meeting = repo.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")

    meeting.end_meeting(notes)
    repo.db.commit()
    return meeting


@router.post("/meetings/{meeting_id}/cancel", response_model=MeetingResponse)
async def cancel_meeting(
    meeting_id: uuid.UUID,
    reason: Optional[str] = None,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Cancela reunião."""
    meeting = repo.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")

    meeting.cancel_meeting(reason)
    repo.db.commit()
    return meeting


# ============== Participant Endpoints ==============

@router.post("/meetings/{meeting_id}/participants", response_model=ParticipantResponse)
async def add_participant(
    meeting_id: uuid.UUID,
    data: ParticipantCreate,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Adiciona participante à reunião."""
    meeting = repo.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")

    participant = repo.add_participant(meeting_id, data.dict())
    return participant


@router.put("/meetings/{meeting_id}/participants/{participant_id}/respond")
async def respond_to_meeting(
    meeting_id: uuid.UUID,
    participant_id: uuid.UUID,
    response: str,
    note: Optional[str] = None,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Responde ao convite de reunião."""
    if response not in ["accept", "decline", "tentative"]:
        raise HTTPException(status_code=400, detail="Resposta inválida")

    status_map = {
        "accept": ParticipantStatusEnum.ACCEPTED,
        "decline": ParticipantStatusEnum.DECLINED,
        "tentative": ParticipantStatusEnum.TENTATIVE
    }

    participant = repo.update_participant_status(
        participant_id,
        status_map[response],
        note
    )

    if not participant:
        raise HTTPException(status_code=404, detail="Participante não encontrado")

    return {"status": "ok", "response": response}


@router.delete("/meetings/{meeting_id}/participants/{user_id}")
async def remove_participant(
    meeting_id: uuid.UUID,
    user_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Remove participante da reunião."""
    if not repo.remove_participant(meeting_id, user_id):
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return {"status": "removed"}


# ============== Notes & Summary Endpoints ==============

@router.post("/meetings/{meeting_id}/notes", response_model=MeetingNoteResponse)
async def create_note(
    meeting_id: uuid.UUID,
    data: MeetingNoteCreate,
    current_user: CurrentActiveUser = ...,  # Required
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Cria nota na reunião."""
    meeting = repo.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")

    note = repo.create_note(meeting_id, data, current_user.id, current_user.nome)
    return note


@router.get("/meetings/{meeting_id}/notes", response_model=List[MeetingNoteResponse])
async def get_notes(
    meeting_id: uuid.UUID,
    include_private: bool = False,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Busca notas da reunião."""
    return repo.get_meeting_notes(meeting_id, include_private)


@router.post("/meetings/{meeting_id}/generate-summary", response_model=MeetingSummaryResponse)
async def generate_summary(
    meeting_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Gera resumo da reunião usando IA."""
    meeting = repo.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")

    notes = repo.get_meeting_notes(meeting_id)
    summarizer = MeetingSummarizer()
    summary_data = summarizer.generate_summary(meeting, notes)

    summary = repo.create_summary(meeting_id, summary_data)
    return summary


@router.get("/meetings/{meeting_id}/summary", response_model=MeetingSummaryResponse)
async def get_summary(
    meeting_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Busca resumo da reunião."""
    summary = repo.get_meeting_summary(meeting_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Resumo não encontrado")
    return summary


# ============== Schedule Optimization Endpoints ==============

@router.post("/schedule/suggest", response_model=ScheduleSuggestionResponse)
async def suggest_schedule(
    request: ScheduleSuggestionRequest,
    current_user: CurrentActiveUser = ...,  # Required
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Sugere horários para reunião."""
    # Busca reuniões existentes dos participantes
    existing_meetings = []
    for participant_id in request.participant_ids:
        meetings, _ = repo.list_meetings(
            participant_id=participant_id,
            start_date=request.preferred_start_date or datetime.utcnow(),
            end_date=request.preferred_end_date or (datetime.utcnow() + timedelta(days=14))
        )
        existing_meetings.extend(meetings)

    optimizer = ScheduleOptimizer()
    suggestions = optimizer.find_optimal_slots(request, existing_meetings)

    return ScheduleSuggestionResponse(
        suggestions=suggestions,
        participants_analyzed=len(request.participant_ids),
        conflicts_found=sum(len(s.conflicts) for s in suggestions),
        best_slot=suggestions[0] if suggestions else None,
        analysis_notes=f"Analisadas {len(existing_meetings)} reuniões existentes"
    )


@router.post("/schedule/check-availability")
async def check_availability(
    participant_ids: List[uuid.UUID],
    start: datetime,
    end: datetime,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Verifica disponibilidade para horário específico."""
    existing_meetings = []
    for participant_id in participant_ids:
        meetings, _ = repo.list_meetings(
            participant_id=participant_id,
            start_date=start - timedelta(hours=2),
            end_date=end + timedelta(hours=2)
        )
        existing_meetings.extend(meetings)

    optimizer = ScheduleOptimizer()
    result = optimizer.check_availability(participant_ids, start, end, existing_meetings)
    return result


# ============== Task Endpoints ==============

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    current_user: CurrentActiveUser = ...,  # Required
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Cria nova tarefa."""
    task = repo.create_task(data, current_user.id)
    return task


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[TaskStatusEnum] = None,
    priority: Optional[TaskPriorityEnum] = None,
    assignee_id: Optional[uuid.UUID] = None,
    project_id: Optional[uuid.UUID] = None,
    is_overdue: Optional[bool] = None,
    is_blocked: Optional[bool] = None,
    current_user: CurrentActiveUser = None,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Lista tarefas com filtros."""
    skip = (page - 1) * page_size
    tasks, total = repo.list_tasks(
        skip=skip,
        limit=page_size,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        project_id=project_id,
        is_overdue=is_overdue,
        is_blocked=is_blocked
    )

    return TaskListResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/tasks/my", response_model=List[TaskResponse])
async def get_my_tasks(
    status: Optional[TaskStatusEnum] = None,
    limit: int = Query(20, ge=1, le=100),
    current_user: CurrentActiveUser = None,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Busca tarefas do usuário atual."""
    tasks, _ = repo.list_tasks(
        assignee_id=current_user.id,
        status=status,
        limit=limit
    )
    return tasks


@router.get("/tasks/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(
    current_user: CurrentActiveUser = None,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Busca tarefas atrasadas."""
    return repo.get_overdue_tasks(current_user.id)


@router.get("/tasks/blocked", response_model=List[TaskResponse])
async def get_blocked_tasks(
    current_user: CurrentActiveUser = None,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Busca tarefas bloqueadas."""
    return repo.get_blocked_tasks(current_user.id)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Busca tarefa por ID."""
    task = repo.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Atualiza tarefa."""
    task = repo.update_task(task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Deleta tarefa."""
    if not repo.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")


@router.post("/tasks/{task_id}/start", response_model=TaskResponse)
async def start_task(
    task_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Inicia tarefa."""
    task = repo.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    task.start_task()
    repo.db.commit()
    return task


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Completa tarefa."""
    task = repo.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    task.complete_task()
    repo.db.commit()
    return task


@router.post("/tasks/{task_id}/block", response_model=TaskResponse)
async def block_task(
    task_id: uuid.UUID,
    reason: str,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Bloqueia tarefa."""
    task = repo.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    task.block_task(reason)
    repo.db.commit()
    return task


@router.post("/tasks/{task_id}/unblock", response_model=TaskResponse)
async def unblock_task(
    task_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Desbloqueia tarefa."""
    task = repo.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    task.unblock_task()
    repo.db.commit()
    return task


# ============== Task Prioritization Endpoints ==============

@router.post("/tasks/prioritize", response_model=PrioritizationResponse)
async def prioritize_tasks(
    request: PrioritizationRequest,
    current_user: CurrentActiveUser = ...,  # Required
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Prioriza tarefas usando IA."""
    # Busca tarefas
    if request.task_ids:
        tasks = [repo.get_task(tid) for tid in request.task_ids]
        tasks = [t for t in tasks if t is not None]
    else:
        tasks, _ = repo.list_tasks(
            assignee_id=request.assignee_id or current_user.id,
            project_id=request.project_id
        )

    if not request.include_completed:
        tasks = [t for t in tasks if t.status != TaskStatusEnum.COMPLETED]

    # Busca dependências
    dependencies_map = {}
    for task in tasks:
        dependencies_map[task.id] = repo.get_task_dependencies(task.id)

    # Prioriza
    prioritizer = TaskPrioritizer()
    suggestions = prioritizer.prioritize_tasks(tasks, dependencies_map)

    # Conta métricas
    high_priority = sum(1 for s in suggestions if s.suggested_priority in [TaskPriorityEnum.CRITICAL, TaskPriorityEnum.HIGH])
    overdue = sum(1 for t in tasks if t.due_date and t.due_date < datetime.utcnow())
    blocked = sum(1 for t in tasks if t.is_blocked)

    return PrioritizationResponse(
        tasks=suggestions,
        total_analyzed=len(tasks),
        high_priority_count=high_priority,
        overdue_count=overdue,
        blocked_count=blocked,
        recommendations=[
            f"{high_priority} tarefas requerem atenção prioritária",
            f"{overdue} tarefas estão atrasadas" if overdue > 0 else "Nenhuma tarefa atrasada",
            f"{blocked} tarefas bloqueadas" if blocked > 0 else "Nenhum bloqueio identificado"
        ]
    )


@router.get("/tasks/{task_id}/priority-analysis")
async def analyze_task_priority(
    task_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Analisa prioridade de uma tarefa."""
    task = repo.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    dependencies = repo.get_task_dependencies(task_id)
    prioritizer = TaskPrioritizer()
    analysis = prioritizer.calculate_priority(task, dependencies)

    return {
        "task_id": str(task_id),
        "task_code": task.task_code,
        "current_priority": task.priority.value,
        "analysis": analysis
    }


# ============== Meeting-Task Integration ==============

@router.get("/meetings/{meeting_id}/tasks", response_model=List[TaskResponse])
async def get_meeting_tasks(
    meeting_id: uuid.UUID,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Busca tarefas originadas de uma reunião."""
    meeting = repo.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")

    return repo.get_tasks_from_meeting(meeting_id)


@router.post("/meetings/{meeting_id}/create-task", response_model=TaskResponse)
async def create_task_from_meeting(
    meeting_id: uuid.UUID,
    data: TaskCreate,
    action_index: Optional[int] = None,
    current_user: CurrentActiveUser = None,
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Cria tarefa a partir de reunião."""
    meeting = repo.get_meeting(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")

    # Associa à reunião
    data_dict = data.dict()
    data_dict["meeting_id"] = meeting_id
    data_dict["meeting_action_index"] = action_index

    task_data = TaskCreate(**data_dict)
    task = repo.create_task(task_data, current_user.id)
    task.ai_generated = True
    task.ai_generation_source = "meeting"
    repo.db.commit()

    return task


# ============== Dashboard ==============

@router.get("/dashboard", response_model=MeetingAssistantDashboard)
async def get_dashboard(
    current_user: CurrentActiveUser = ...,  # Required
    repo: MeetingAssistantRepository = Depends(get_repository)
):
    """Obtém dashboard do assistente."""
    stats = repo.get_dashboard_stats(current_user.id)

    # Próximas reuniões
    upcoming = repo.get_upcoming_meetings(current_user.id, 5)

    # Distribuições
    meetings_by_status = {}
    meetings_by_type = {}
    tasks_by_priority = {}
    tasks_by_status = {}

    # Busca todas as reuniões para estatísticas
    all_meetings, _ = repo.list_meetings(participant_id=current_user.id, limit=100)
    for m in all_meetings:
        status_key = m.status.value
        type_key = m.meeting_type.value
        meetings_by_status[status_key] = meetings_by_status.get(status_key, 0) + 1
        meetings_by_type[type_key] = meetings_by_type.get(type_key, 0) + 1

    # Busca todas as tarefas para estatísticas
    all_tasks, _ = repo.list_tasks(assignee_id=current_user.id, limit=100)
    for t in all_tasks:
        priority_key = t.priority.value
        status_key = t.status.value
        tasks_by_priority[priority_key] = tasks_by_priority.get(priority_key, 0) + 1
        tasks_by_status[status_key] = tasks_by_status.get(status_key, 0) + 1

    return MeetingAssistantDashboard(
        total_meetings=stats["total_meetings"],
        meetings_today=stats["meetings_today"],
        meetings_this_week=stats["meetings_this_week"],
        upcoming_meetings=upcoming,
        meetings_by_status=meetings_by_status,
        meetings_by_type=meetings_by_type,
        total_tasks=stats["total_tasks"],
        tasks_todo=stats["tasks_todo"],
        tasks_in_progress=stats["tasks_in_progress"],
        tasks_completed_this_week=stats["tasks_completed_this_week"],
        overdue_tasks=stats["overdue_tasks"],
        blocked_tasks=stats["blocked_tasks"],
        tasks_by_priority=tasks_by_priority,
        tasks_by_status=tasks_by_status,
        ai_suggestions_pending=0,
        auto_scheduled_meetings=0,
        tasks_from_meetings=len([t for t in all_tasks if t.meeting_id]),
        avg_meeting_duration_minutes=sum(m.duration_minutes for m in all_meetings) / len(all_meetings) if all_meetings else 0,
        avg_task_completion_time_hours=0,
        meeting_effectiveness_avg=None,
        recent_activity=[]
    )
