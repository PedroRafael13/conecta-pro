"""
Smart Notifier Service - Sprint 49.

Serviço de notificações inteligentes para reuniões e tarefas.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid

from modules.ai.meeting_assistant.models import (
    Meeting,
    Task,
    MeetingParticipant,
    MeetingStatusEnum,
    TaskStatusEnum,
    TaskPriorityEnum,
    ParticipantStatusEnum,
)


class NotificationType(str, Enum):
    """Tipos de notificação."""
    MEETING_REMINDER = "meeting_reminder"
    MEETING_STARTING = "meeting_starting"
    MEETING_INVITATION = "meeting_invitation"
    MEETING_RESCHEDULED = "meeting_rescheduled"
    MEETING_CANCELLED = "meeting_cancelled"
    MEETING_SUMMARY = "meeting_summary"
    TASK_ASSIGNED = "task_assigned"
    TASK_DUE_SOON = "task_due_soon"
    TASK_OVERDUE = "task_overdue"
    TASK_COMPLETED = "task_completed"
    TASK_BLOCKED = "task_blocked"
    TASK_PRIORITY_CHANGED = "task_priority_changed"
    ACTION_ITEM_CREATED = "action_item_created"
    DAILY_DIGEST = "daily_digest"
    WEEKLY_SUMMARY = "weekly_summary"


class NotificationPriority(str, Enum):
    """Prioridade da notificação."""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class SmartNotifier:
    """Serviço de notificações inteligentes."""

    def __init__(self):
        self.notification_rules = {
            NotificationType.MEETING_STARTING: {
                "priority": NotificationPriority.URGENT,
                "channels": ["push", "email"],
                "timing_minutes": [5, 1]
            },
            NotificationType.MEETING_REMINDER: {
                "priority": NotificationPriority.NORMAL,
                "channels": ["push"],
                "timing_minutes": [15, 60, 1440]  # 15min, 1h, 1 dia
            },
            NotificationType.TASK_OVERDUE: {
                "priority": NotificationPriority.HIGH,
                "channels": ["push", "email"],
                "timing_minutes": [0]
            },
            NotificationType.TASK_DUE_SOON: {
                "priority": NotificationPriority.NORMAL,
                "channels": ["push"],
                "timing_minutes": [1440]  # 1 dia antes
            }
        }

    def generate_meeting_notifications(
        self,
        meeting: Meeting,
        participants: List[MeetingParticipant] = None
    ) -> List[Dict[str, Any]]:
        """
        Gera notificações para uma reunião.

        Returns:
            Lista de notificações a serem enviadas
        """
        notifications = []
        now = datetime.utcnow()

        if meeting.status in [MeetingStatusEnum.SCHEDULED, MeetingStatusEnum.CONFIRMED]:
            time_until = (meeting.scheduled_start - now).total_seconds() / 60

            # Reunião começando
            if 0 <= time_until <= 5:
                notifications.append(self._create_notification(
                    notification_type=NotificationType.MEETING_STARTING,
                    recipients=self._get_meeting_recipients(meeting, participants),
                    context={
                        "meeting_id": str(meeting.id),
                        "meeting_title": meeting.title,
                        "start_time": meeting.scheduled_start.isoformat(),
                        "virtual_link": meeting.virtual_link
                    },
                    message=f"Reunião '{meeting.title}' começa em {int(time_until)} minutos"
                ))

            # Lembretes configurados
            elif meeting.reminder_minutes:
                for reminder_min in meeting.reminder_minutes:
                    if reminder_min - 1 <= time_until <= reminder_min + 1:
                        notifications.append(self._create_notification(
                            notification_type=NotificationType.MEETING_REMINDER,
                            recipients=self._get_meeting_recipients(meeting, participants),
                            context={
                                "meeting_id": str(meeting.id),
                                "meeting_title": meeting.title,
                                "start_time": meeting.scheduled_start.isoformat(),
                                "reminder_minutes": reminder_min
                            },
                            message=self._format_reminder_message(meeting.title, reminder_min)
                        ))

        return notifications

    def generate_task_notifications(self, task: Task) -> List[Dict[str, Any]]:
        """
        Gera notificações para uma tarefa.

        Returns:
            Lista de notificações
        """
        notifications = []
        now = datetime.utcnow()

        if task.status == TaskStatusEnum.COMPLETED:
            return notifications  # Não notifica tarefas completas

        recipients = []
        if task.assignee_id:
            recipients.append(str(task.assignee_id))
        if task.watchers:
            recipients.extend([str(w) for w in task.watchers])

        # Tarefa atrasada
        if task.due_date and task.due_date < now:
            notifications.append(self._create_notification(
                notification_type=NotificationType.TASK_OVERDUE,
                recipients=recipients,
                context={
                    "task_id": str(task.id),
                    "task_code": task.task_code,
                    "task_title": task.title,
                    "due_date": task.due_date.isoformat(),
                    "days_overdue": (now - task.due_date).days
                },
                message=f"Tarefa '{task.task_code}' está atrasada há {(now - task.due_date).days} dia(s)"
            ))

        # Tarefa vence em breve
        elif task.due_date:
            hours_until = (task.due_date - now).total_seconds() / 3600
            if 0 < hours_until <= 24:
                notifications.append(self._create_notification(
                    notification_type=NotificationType.TASK_DUE_SOON,
                    recipients=recipients,
                    context={
                        "task_id": str(task.id),
                        "task_code": task.task_code,
                        "task_title": task.title,
                        "due_date": task.due_date.isoformat(),
                        "hours_until": int(hours_until)
                    },
                    message=f"Tarefa '{task.task_code}' vence em {int(hours_until)} hora(s)"
                ))

        # Tarefa bloqueada
        if task.is_blocked:
            notifications.append(self._create_notification(
                notification_type=NotificationType.TASK_BLOCKED,
                recipients=recipients,
                context={
                    "task_id": str(task.id),
                    "task_code": task.task_code,
                    "task_title": task.title,
                    "blocked_reason": task.blocked_reason
                },
                message=f"Tarefa '{task.task_code}' está bloqueada: {task.blocked_reason}"
            ))

        return notifications

    def generate_daily_digest(
        self,
        user_id: uuid.UUID,
        meetings_today: List[Meeting],
        tasks_due_today: List[Task],
        overdue_tasks: List[Task]
    ) -> Dict[str, Any]:
        """
        Gera digest diário para um usuário.

        Returns:
            Notificação de digest
        """
        sections = []

        # Seção de reuniões
        if meetings_today:
            meeting_items = []
            for meeting in meetings_today[:5]:
                meeting_items.append({
                    "title": meeting.title,
                    "time": meeting.scheduled_start.strftime("%H:%M"),
                    "virtual_link": meeting.virtual_link
                })
            sections.append({
                "title": "Reuniões de Hoje",
                "count": len(meetings_today),
                "items": meeting_items
            })

        # Seção de tarefas
        if tasks_due_today:
            task_items = []
            for task in tasks_due_today[:5]:
                task_items.append({
                    "code": task.task_code,
                    "title": task.title,
                    "priority": task.priority.value
                })
            sections.append({
                "title": "Tarefas para Hoje",
                "count": len(tasks_due_today),
                "items": task_items
            })

        # Seção de atrasadas
        if overdue_tasks:
            overdue_items = []
            for task in overdue_tasks[:5]:
                overdue_items.append({
                    "code": task.task_code,
                    "title": task.title,
                    "days_overdue": (datetime.utcnow() - task.due_date).days
                })
            sections.append({
                "title": "Tarefas Atrasadas",
                "count": len(overdue_tasks),
                "items": overdue_items,
                "alert": True
            })

        return self._create_notification(
            notification_type=NotificationType.DAILY_DIGEST,
            recipients=[str(user_id)],
            context={
                "date": datetime.utcnow().strftime("%d/%m/%Y"),
                "sections": sections,
                "total_meetings": len(meetings_today),
                "total_tasks_due": len(tasks_due_today),
                "total_overdue": len(overdue_tasks)
            },
            message=self._format_digest_summary(meetings_today, tasks_due_today, overdue_tasks)
        )

    def generate_weekly_summary(
        self,
        user_id: uuid.UUID,
        meetings_completed: int,
        tasks_completed: int,
        tasks_created: int,
        productivity_score: float = None
    ) -> Dict[str, Any]:
        """
        Gera resumo semanal.

        Returns:
            Notificação de resumo semanal
        """
        return self._create_notification(
            notification_type=NotificationType.WEEKLY_SUMMARY,
            recipients=[str(user_id)],
            context={
                "week_start": (datetime.utcnow() - timedelta(days=7)).strftime("%d/%m"),
                "week_end": datetime.utcnow().strftime("%d/%m"),
                "meetings_completed": meetings_completed,
                "tasks_completed": tasks_completed,
                "tasks_created": tasks_created,
                "productivity_score": productivity_score
            },
            message=f"Semana: {meetings_completed} reuniões, {tasks_completed} tarefas concluídas"
        )

    def notify_meeting_invitation(
        self,
        meeting: Meeting,
        participant: MeetingParticipant
    ) -> Dict[str, Any]:
        """Gera notificação de convite de reunião."""
        return self._create_notification(
            notification_type=NotificationType.MEETING_INVITATION,
            recipients=[str(participant.user_id)],
            context={
                "meeting_id": str(meeting.id),
                "meeting_title": meeting.title,
                "organizer_name": meeting.organizer_name,
                "scheduled_start": meeting.scheduled_start.isoformat(),
                "scheduled_end": meeting.scheduled_end.isoformat(),
                "location": meeting.location or meeting.virtual_link,
                "is_virtual": meeting.is_virtual
            },
            message=f"Convite: {meeting.title} - {meeting.scheduled_start.strftime('%d/%m %H:%M')}"
        )

    def notify_task_assignment(
        self,
        task: Task,
        assigned_by: str = None
    ) -> Dict[str, Any]:
        """Gera notificação de atribuição de tarefa."""
        return self._create_notification(
            notification_type=NotificationType.TASK_ASSIGNED,
            recipients=[str(task.assignee_id)] if task.assignee_id else [],
            context={
                "task_id": str(task.id),
                "task_code": task.task_code,
                "task_title": task.title,
                "assigned_by": assigned_by,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority.value
            },
            message=f"Nova tarefa atribuída: {task.task_code} - {task.title}"
        )

    def notify_action_item_from_meeting(
        self,
        meeting: Meeting,
        action_item: Dict[str, Any],
        assignee_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Gera notificação de action item de reunião."""
        return self._create_notification(
            notification_type=NotificationType.ACTION_ITEM_CREATED,
            recipients=[str(assignee_id)],
            context={
                "meeting_id": str(meeting.id),
                "meeting_title": meeting.title,
                "action_description": action_item.get("description"),
                "due_date": action_item.get("due_date")
            },
            message=f"Novo item de ação da reunião '{meeting.title}': {action_item.get('description', '')[:50]}"
        )

    def should_notify(
        self,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        context: Dict[str, Any],
        user_preferences: Dict[str, Any] = None
    ) -> bool:
        """
        Verifica se deve enviar notificação.

        Considera preferências do usuário e regras de negócio.
        """
        # Regras padrão
        rules = self.notification_rules.get(notification_type, {})

        # Verifica preferências do usuário
        if user_preferences:
            # Usuário desativou este tipo
            disabled_types = user_preferences.get("disabled_notifications", [])
            if notification_type.value in disabled_types:
                return False

            # Horário silencioso
            quiet_hours = user_preferences.get("quiet_hours")
            if quiet_hours:
                now = datetime.utcnow().time()
                quiet_start = datetime.strptime(quiet_hours.get("start", "22:00"), "%H:%M").time()
                quiet_end = datetime.strptime(quiet_hours.get("end", "08:00"), "%H:%M").time()

                if quiet_start <= now or now <= quiet_end:
                    # Em horário silencioso, só notifica urgentes
                    if rules.get("priority") != NotificationPriority.URGENT:
                        return False

        return True

    def _create_notification(
        self,
        notification_type: NotificationType,
        recipients: List[str],
        context: Dict[str, Any],
        message: str
    ) -> Dict[str, Any]:
        """Cria estrutura de notificação."""
        rules = self.notification_rules.get(notification_type, {})

        return {
            "id": str(uuid.uuid4()),
            "type": notification_type.value,
            "priority": rules.get("priority", NotificationPriority.NORMAL).value,
            "channels": rules.get("channels", ["push"]),
            "recipients": recipients,
            "message": message,
            "context": context,
            "created_at": datetime.utcnow().isoformat(),
            "scheduled_for": None,
            "sent": False
        }

    def _get_meeting_recipients(
        self,
        meeting: Meeting,
        participants: List[MeetingParticipant] = None
    ) -> List[str]:
        """Obtém destinatários de notificação da reunião."""
        recipients = [str(meeting.organizer_id)]

        if participants:
            for p in participants:
                if p.status != ParticipantStatusEnum.DECLINED:
                    recipients.append(str(p.user_id))

        return list(set(recipients))

    def _format_reminder_message(self, title: str, minutes: int) -> str:
        """Formata mensagem de lembrete."""
        if minutes >= 1440:
            time_str = f"{minutes // 1440} dia(s)"
        elif minutes >= 60:
            time_str = f"{minutes // 60} hora(s)"
        else:
            time_str = f"{minutes} minuto(s)"

        return f"Lembrete: '{title}' em {time_str}"

    def _format_digest_summary(
        self,
        meetings: List[Meeting],
        tasks_due: List[Task],
        overdue: List[Task]
    ) -> str:
        """Formata resumo do digest."""
        parts = []

        if meetings:
            parts.append(f"{len(meetings)} reunião(ões)")
        if tasks_due:
            parts.append(f"{len(tasks_due)} tarefa(s) para hoje")
        if overdue:
            parts.append(f"⚠️ {len(overdue)} atrasada(s)")

        return "Hoje: " + ", ".join(parts) if parts else "Dia livre!"
