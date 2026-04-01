"""
Meeting Assistant Repository - Sprint 49.

Repositório para operações de banco de dados.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, desc, or_
from sqlalchemy.orm import Session, joinedload

from modules.ai.meeting_assistant.models import (
    Meeting,
    MeetingNote,
    MeetingParticipant,
    MeetingStatusEnum,
    MeetingSummary,
    Task,
    TaskDependency,
    TaskPriorityEnum,
    TaskStatusEnum,
)
from modules.ai.meeting_assistant.schemas import (
    MeetingCreate,
    MeetingNoteCreate,
    MeetingUpdate,
    TaskCreate,
    TaskUpdate,
)


class MeetingAssistantRepository:
    """Repositório para Meeting Assistant."""

    def __init__(self, db: Session):
        self.db = db

    # ============== Meeting Operations ==============

    def create_meeting(self, data: MeetingCreate, user_id: uuid.UUID) -> Meeting:
        """Cria nova reunião."""
        meeting_code = f"MTG-{uuid.uuid4().hex[:8].upper()}"

        duration = int((data.scheduled_end - data.scheduled_start).total_seconds() / 60)

        meeting = Meeting(
            meeting_code=meeting_code,
            title=data.title,
            description=data.description,
            meeting_type=data.meeting_type,
            scheduled_start=data.scheduled_start,
            scheduled_end=data.scheduled_end,
            duration_minutes=duration,
            timezone=data.timezone,
            location=data.location,
            is_virtual=data.is_virtual,
            virtual_link=data.virtual_link,
            virtual_platform=data.virtual_platform,
            room_id=data.room_id,
            is_recurring=data.is_recurring,
            recurrence_type=data.recurrence_type,
            recurrence_pattern=data.recurrence_pattern,
            recurrence_end_date=data.recurrence_end_date,
            organizer_id=data.organizer_id,
            organizer_name=data.organizer_name,
            organizer_email=data.organizer_email,
            department=data.department,
            project_id=data.project_id,
            agenda=[item.dict() for item in data.agenda],
            objectives=data.objectives,
            preparation_notes=data.preparation_notes,
            reminder_minutes=data.reminder_minutes,
            tags=data.tags,
            category=data.category,
            priority=data.priority,
            created_by=user_id,
        )

        self.db.add(meeting)
        self.db.flush()

        # Adiciona participantes
        for participant_data in data.participants:
            participant = MeetingParticipant(
                meeting_id=meeting.id,
                user_id=participant_data.user_id,
                name=participant_data.name,
                email=participant_data.email,
                phone=participant_data.phone,
                department=participant_data.department,
                company=participant_data.company,
                role=participant_data.role,
            )
            self.db.add(participant)

        self.db.commit()
        self.db.refresh(meeting)
        return meeting

    def get_meeting(self, meeting_id: uuid.UUID) -> Meeting | None:
        """Busca reunião por ID."""
        return (
            self.db.query(Meeting)
            .options(joinedload(Meeting.participants), joinedload(Meeting.notes), joinedload(Meeting.summaries))
            .filter(Meeting.id == meeting_id, Meeting.ativo)
            .first()
        )

    def get_meeting_by_code(self, meeting_code: str) -> Meeting | None:
        """Busca reunião por código."""
        return (
            self.db.query(Meeting)
            .options(joinedload(Meeting.participants))
            .filter(Meeting.meeting_code == meeting_code, Meeting.ativo)
            .first()
        )

    def list_meetings(
        self,
        skip: int = 0,
        limit: int = 100,
        status: MeetingStatusEnum = None,
        organizer_id: uuid.UUID = None,
        participant_id: uuid.UUID = None,
        start_date: datetime = None,
        end_date: datetime = None,
        meeting_type: str = None,
    ) -> tuple[list[Meeting], int]:
        """Lista reuniões com filtros."""
        query = self.db.query(Meeting).filter(Meeting.ativo)

        if status:
            query = query.filter(Meeting.status == status)
        if organizer_id:
            query = query.filter(Meeting.organizer_id == organizer_id)
        if start_date:
            query = query.filter(Meeting.scheduled_start >= start_date)
        if end_date:
            query = query.filter(Meeting.scheduled_end <= end_date)
        if meeting_type:
            query = query.filter(Meeting.meeting_type == meeting_type)
        if participant_id:
            query = query.join(MeetingParticipant).filter(MeetingParticipant.user_id == participant_id)

        total = query.count()
        meetings = (
            query.options(joinedload(Meeting.participants))
            .order_by(Meeting.scheduled_start)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return meetings, total

    def update_meeting(self, meeting_id: uuid.UUID, data: MeetingUpdate) -> Meeting | None:
        """Atualiza reunião."""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return None

        update_data = data.dict(exclude_unset=True)

        # Processa agenda se fornecida
        if "agenda" in update_data and update_data["agenda"]:
            update_data["agenda"] = [item.dict() if hasattr(item, "dict") else item for item in update_data["agenda"]]

        # Processa action_items se fornecidos
        if "action_items" in update_data and update_data["action_items"]:
            update_data["action_items"] = [
                item.dict() if hasattr(item, "dict") else item for item in update_data["action_items"]
            ]

        for field, value in update_data.items():
            setattr(meeting, field, value)

        # Recalcula duração se datas mudaram
        if data.scheduled_start or data.scheduled_end:
            if meeting.scheduled_start and meeting.scheduled_end:
                meeting.duration_minutes = int((meeting.scheduled_end - meeting.scheduled_start).total_seconds() / 60)

        self.db.commit()
        self.db.refresh(meeting)
        return meeting

    def delete_meeting(self, meeting_id: uuid.UUID) -> bool:
        """Deleta reunião (soft delete)."""
        meeting = self.get_meeting(meeting_id)
        if meeting:
            meeting.ativo = False
            self.db.commit()
            return True
        return False

    def get_upcoming_meetings(self, user_id: uuid.UUID, limit: int = 10) -> list[Meeting]:
        """Busca próximas reuniões do usuário."""
        now = datetime.utcnow()
        return (
            self.db.query(Meeting)
            .join(MeetingParticipant)
            .filter(
                and_(
                    Meeting.ativo,
                    Meeting.scheduled_start >= now,
                    Meeting.status.in_([MeetingStatusEnum.SCHEDULED, MeetingStatusEnum.CONFIRMED]),
                    or_(Meeting.organizer_id == user_id, MeetingParticipant.user_id == user_id),
                )
            )
            .order_by(Meeting.scheduled_start)
            .limit(limit)
            .all()
        )

    def get_meetings_today(self, user_id: uuid.UUID = None) -> list[Meeting]:
        """Busca reuniões de hoje."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        query = self.db.query(Meeting).filter(
            and_(Meeting.ativo, Meeting.scheduled_start >= today_start, Meeting.scheduled_start < today_end)
        )

        if user_id:
            query = query.join(MeetingParticipant).filter(
                or_(Meeting.organizer_id == user_id, MeetingParticipant.user_id == user_id)
            )

        return query.order_by(Meeting.scheduled_start).all()

    # ============== Participant Operations ==============

    def add_participant(self, meeting_id: uuid.UUID, participant_data: dict[str, Any]) -> MeetingParticipant:
        """Adiciona participante à reunião."""
        participant = MeetingParticipant(meeting_id=meeting_id, **participant_data)
        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def update_participant_status(
        self, participant_id: uuid.UUID, status: str, note: str = None
    ) -> MeetingParticipant | None:
        """Atualiza status do participante."""
        participant = self.db.query(MeetingParticipant).filter(MeetingParticipant.id == participant_id).first()

        if participant:
            participant.status = status
            participant.response_date = datetime.utcnow()
            if note:
                participant.response_note = note
            self.db.commit()
            self.db.refresh(participant)

        return participant

    def remove_participant(self, meeting_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Remove participante da reunião."""
        result = (
            self.db.query(MeetingParticipant)
            .filter(and_(MeetingParticipant.meeting_id == meeting_id, MeetingParticipant.user_id == user_id))
            .delete()
        )
        self.db.commit()
        return result > 0

    # ============== Note Operations ==============

    def create_note(
        self, meeting_id: uuid.UUID, data: MeetingNoteCreate, author_id: uuid.UUID, author_name: str = None
    ) -> MeetingNote:
        """Cria nota de reunião."""
        note = MeetingNote(
            meeting_id=meeting_id,
            author_id=author_id,
            author_name=author_name,
            content=data.content,
            content_type=data.content_type,
            is_private=data.is_private,
            note_type=data.note_type,
            agenda_item_index=data.agenda_item_index,
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def get_meeting_notes(self, meeting_id: uuid.UUID, include_private: bool = False) -> list[MeetingNote]:
        """Busca notas da reunião."""
        query = self.db.query(MeetingNote).filter(MeetingNote.meeting_id == meeting_id)
        if not include_private:
            query = query.filter(not MeetingNote.is_private)
        return query.order_by(MeetingNote.created_at).all()

    # ============== Summary Operations ==============

    def create_summary(self, meeting_id: uuid.UUID, summary_data: dict[str, Any]) -> MeetingSummary:
        """Cria resumo de reunião."""
        summary = MeetingSummary(meeting_id=meeting_id, **summary_data)
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        return summary

    def get_meeting_summary(self, meeting_id: uuid.UUID) -> MeetingSummary | None:
        """Busca resumo da reunião."""
        return (
            self.db.query(MeetingSummary)
            .filter(MeetingSummary.meeting_id == meeting_id)
            .order_by(desc(MeetingSummary.created_at))
            .first()
        )

    # ============== Task Operations ==============

    def create_task(self, data: TaskCreate, user_id: uuid.UUID) -> Task:
        """Cria nova tarefa."""
        task_code = f"TASK-{uuid.uuid4().hex[:8].upper()}"

        task = Task(
            task_code=task_code,
            title=data.title,
            description=data.description,
            task_type=data.task_type,
            priority=data.priority,
            assignee_id=data.assignee_id,
            assignee_name=data.assignee_name,
            reporter_id=data.reporter_id or user_id,
            reporter_name=data.reporter_name,
            due_date=data.due_date,
            start_date=data.start_date,
            estimated_hours=data.estimated_hours,
            story_points=data.story_points,
            project_id=data.project_id,
            project_name=data.project_name,
            sprint_id=data.sprint_id,
            sprint_name=data.sprint_name,
            parent_task_id=data.parent_task_id,
            meeting_id=data.meeting_id,
            meeting_action_index=data.meeting_action_index,
            tags=data.tags,
            labels=data.labels,
            category=data.category,
            department=data.department,
            context=data.context,
            acceptance_criteria=data.acceptance_criteria,
            checklist=[item.dict() for item in data.checklist],
            checklist_total=len(data.checklist),
            is_recurring=data.is_recurring,
            recurrence_pattern=data.recurrence_pattern,
            recurrence_end_date=data.recurrence_end_date,
            created_by=user_id,
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_task(self, task_id: uuid.UUID) -> Task | None:
        """Busca tarefa por ID."""
        return self.db.query(Task).filter(Task.id == task_id, Task.ativo).first()

    def get_task_by_code(self, task_code: str) -> Task | None:
        """Busca tarefa por código."""
        return self.db.query(Task).filter(Task.task_code == task_code, Task.ativo).first()

    def list_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TaskStatusEnum = None,
        priority: TaskPriorityEnum = None,
        assignee_id: uuid.UUID = None,
        project_id: uuid.UUID = None,
        meeting_id: uuid.UUID = None,
        is_overdue: bool = None,
        is_blocked: bool = None,
    ) -> tuple[list[Task], int]:
        """Lista tarefas com filtros."""
        query = self.db.query(Task).filter(Task.ativo)

        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if meeting_id:
            query = query.filter(Task.meeting_id == meeting_id)
        if is_blocked is not None:
            query = query.filter(Task.is_blocked == is_blocked)
        if is_overdue:
            now = datetime.utcnow()
            query = query.filter(and_(Task.due_date < now, Task.status != TaskStatusEnum.COMPLETED))

        total = query.count()
        tasks = query.order_by(Task.priority.desc(), Task.due_date.asc().nullslast()).offset(skip).limit(limit).all()

        return tasks, total

    def update_task(self, task_id: uuid.UUID, data: TaskUpdate) -> Task | None:
        """Atualiza tarefa."""
        task = self.get_task(task_id)
        if not task:
            return None

        update_data = data.dict(exclude_unset=True)

        # Processa checklist se fornecido
        if "checklist" in update_data and update_data["checklist"]:
            update_data["checklist"] = [
                item.dict() if hasattr(item, "dict") else item for item in update_data["checklist"]
            ]
            update_data["checklist_total"] = len(update_data["checklist"])
            update_data["checklist_completed"] = sum(1 for item in update_data["checklist"] if item.get("completed"))

        for field, value in update_data.items():
            setattr(task, field, value)

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: uuid.UUID) -> bool:
        """Deleta tarefa (soft delete)."""
        task = self.get_task(task_id)
        if task:
            task.ativo = False
            self.db.commit()
            return True
        return False

    def get_overdue_tasks(self, assignee_id: uuid.UUID = None) -> list[Task]:
        """Busca tarefas atrasadas."""
        now = datetime.utcnow()
        query = self.db.query(Task).filter(
            and_(
                Task.ativo,
                Task.due_date < now,
                Task.status != TaskStatusEnum.COMPLETED,
                Task.status != TaskStatusEnum.CANCELLED,
            )
        )

        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)

        return query.order_by(Task.due_date).all()

    def get_blocked_tasks(self, assignee_id: uuid.UUID = None) -> list[Task]:
        """Busca tarefas bloqueadas."""
        query = self.db.query(Task).filter(and_(Task.ativo, Task.is_blocked))

        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)

        return query.order_by(Task.blocked_since).all()

    def get_tasks_from_meeting(self, meeting_id: uuid.UUID) -> list[Task]:
        """Busca tarefas originadas de uma reunião."""
        return (
            self.db.query(Task)
            .filter(and_(Task.ativo, Task.meeting_id == meeting_id))
            .order_by(Task.meeting_action_index)
            .all()
        )

    # ============== Dependency Operations ==============

    def create_dependency(
        self, task_id: uuid.UUID, related_task_id: uuid.UUID, dependency_type: str, user_id: uuid.UUID
    ) -> TaskDependency:
        """Cria dependência entre tarefas."""
        dependency = TaskDependency(
            task_id=task_id, related_task_id=related_task_id, dependency_type=dependency_type, created_by=user_id
        )
        self.db.add(dependency)
        self.db.commit()
        self.db.refresh(dependency)
        return dependency

    def get_task_dependencies(self, task_id: uuid.UUID) -> list[TaskDependency]:
        """Busca dependências de uma tarefa."""
        return (
            self.db.query(TaskDependency)
            .filter(or_(TaskDependency.task_id == task_id, TaskDependency.related_task_id == task_id))
            .all()
        )

    def remove_dependency(self, dependency_id: uuid.UUID) -> bool:
        """Remove dependência."""
        result = self.db.query(TaskDependency).filter(TaskDependency.id == dependency_id).delete()
        self.db.commit()
        return result > 0

    # ============== Statistics ==============

    def get_dashboard_stats(self, user_id: uuid.UUID = None) -> dict[str, Any]:
        """Obtém estatísticas para dashboard."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        week_end = week_start + timedelta(days=7)

        # Meetings stats
        meeting_query = self.db.query(Meeting).filter(Meeting.ativo)
        if user_id:
            meeting_query = meeting_query.join(MeetingParticipant).filter(
                or_(Meeting.organizer_id == user_id, MeetingParticipant.user_id == user_id)
            )

        total_meetings = meeting_query.count()
        meetings_today = meeting_query.filter(
            and_(Meeting.scheduled_start >= today_start, Meeting.scheduled_start < today_start + timedelta(days=1))
        ).count()
        meetings_this_week = meeting_query.filter(
            and_(Meeting.scheduled_start >= week_start, Meeting.scheduled_start < week_end)
        ).count()

        # Task stats
        task_query = self.db.query(Task).filter(Task.ativo)
        if user_id:
            task_query = task_query.filter(Task.assignee_id == user_id)

        total_tasks = task_query.count()
        tasks_todo = task_query.filter(Task.status == TaskStatusEnum.TODO).count()
        tasks_in_progress = task_query.filter(Task.status == TaskStatusEnum.IN_PROGRESS).count()
        tasks_completed_week = task_query.filter(
            and_(Task.status == TaskStatusEnum.COMPLETED, Task.completed_at >= week_start)
        ).count()
        overdue_tasks = task_query.filter(
            and_(Task.due_date < now, Task.status != TaskStatusEnum.COMPLETED, Task.status != TaskStatusEnum.CANCELLED)
        ).count()
        blocked_tasks = task_query.filter(Task.is_blocked).count()

        return {
            "total_meetings": total_meetings,
            "meetings_today": meetings_today,
            "meetings_this_week": meetings_this_week,
            "total_tasks": total_tasks,
            "tasks_todo": tasks_todo,
            "tasks_in_progress": tasks_in_progress,
            "tasks_completed_this_week": tasks_completed_week,
            "overdue_tasks": overdue_tasks,
            "blocked_tasks": blocked_tasks,
        }
