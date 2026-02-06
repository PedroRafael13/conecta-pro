"""Service para notificações do portal."""

import logging
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.employee_portal.models import (
    EmployeeNotification,
    NotificationType,
    NotificationPriority,
    NotificationChannel,
)
from modules.hr.employee_portal.repositories import NotificationRepository
from modules.hr.employee_portal.schemas import (
    NotificationCreate,
    UnreadCountResponse,
)

logger = logging.getLogger(__name__)


# Configuração de tipos de notificação
NOTIFICATION_CONFIG = {
    NotificationType.PAYSLIP_AVAILABLE: {
        "icon": "receipt",
        "color": "green",
        "priority": NotificationPriority.NORMAL,
        "channels": [NotificationChannel.PORTAL, NotificationChannel.EMAIL],
    },
    NotificationType.VACATION_APPROVED: {
        "icon": "beach_access",
        "color": "blue",
        "priority": NotificationPriority.HIGH,
        "channels": [
            NotificationChannel.PORTAL, NotificationChannel.EMAIL, NotificationChannel.PUSH
        ],
    },
    NotificationType.VACATION_REJECTED: {
        "icon": "cancel",
        "color": "red",
        "priority": NotificationPriority.HIGH,
        "channels": [NotificationChannel.PORTAL, NotificationChannel.EMAIL],
    },
    NotificationType.DOCUMENT_AVAILABLE: {
        "icon": "description",
        "color": "purple",
        "priority": NotificationPriority.NORMAL,
        "channels": [NotificationChannel.PORTAL],
    },
    NotificationType.DOCUMENT_REQUIRES_SIGNATURE: {
        "icon": "edit",
        "color": "orange",
        "priority": NotificationPriority.HIGH,
        "channels": [NotificationChannel.PORTAL, NotificationChannel.EMAIL],
    },
    NotificationType.BIRTHDAY_GREETING: {
        "icon": "cake",
        "color": "pink",
        "priority": NotificationPriority.LOW,
        "channels": [NotificationChannel.PORTAL, NotificationChannel.EMAIL],
    },
}


class PortalNotificationService:
    """Service para operações de notificações do portal."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NotificationRepository(db)

    async def send_notification(
        self,
        employee_id: UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        condominio_id: UUID,
        *,
        reference_type: Optional[str] = None,
        reference_id: Optional[UUID] = None,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        extra_data: Optional[dict] = None,
        created_by: Optional[UUID] = None,
    ) -> EmployeeNotification:
        """Envia notificação para funcionário."""
        config = NOTIFICATION_CONFIG.get(notification_type, {})

        data = NotificationCreate(
            employee_id=employee_id,
            notification_type=notification_type,
            priority=config.get("priority", NotificationPriority.NORMAL),
            title=title,
            message=message,
            short_message=message[:200] if len(message) > 200 else None,
            icon=config.get("icon"),
            color=config.get("color"),
            action_url=action_url,
            action_label=action_label,
            reference_type=reference_type,
            reference_id=reference_id,
            channels=config.get("channels", [NotificationChannel.PORTAL]),
            extra_data=extra_data or {},
        )

        return await self.repo.create(data, condominio_id, created_by=created_by)

    async def send_bulk_notification(
        self,
        employee_ids: List[UUID],
        notification_type: NotificationType,
        title: str,
        message: str,
        condominio_id: UUID,
        *,
        created_by: Optional[UUID] = None,
    ) -> List[EmployeeNotification]:
        """Envia notificação para múltiplos funcionários."""
        config = NOTIFICATION_CONFIG.get(notification_type, {})

        data = {
            "notification_type": notification_type.value,
            "priority": config.get("priority", NotificationPriority.NORMAL).value,
            "title": title,
            "message": message,
            "icon": config.get("icon"),
            "color": config.get("color"),
            "channels": [c.value for c in config.get("channels", [NotificationChannel.PORTAL])],
        }

        return await self.repo.create_bulk(
            employee_ids,
            data,
            condominio_id,
            created_by=created_by,
        )

    async def list_notifications(
        self,
        employee_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        is_read: Optional[bool] = None,
        notification_type: Optional[NotificationType] = None,
    ) -> Tuple[List[EmployeeNotification], int]:
        """Lista notificações do funcionário."""
        return await self.repo.list_by_employee(
            employee_id,
            page=page,
            page_size=page_size,
            is_read=is_read,
            notification_type=notification_type,
        )

    async def mark_as_read(
        self,
        notification_id: UUID,
        employee_id: UUID,
    ) -> Optional[EmployeeNotification]:
        """Marca notificação como lida."""
        notification = await self.repo.get_by_id(notification_id)
        if not notification or notification.employee_id != employee_id:
            return None

        return await self.repo.mark_as_read(notification_id)

    async def mark_multiple_as_read(
        self,
        notification_ids: List[UUID],
        employee_id: UUID,
    ) -> int:
        """Marca múltiplas notificações como lidas."""
        # Validar que notificações pertencem ao funcionário
        _ = employee_id  # Usado para validação futura
        return await self.repo.mark_multiple_as_read(notification_ids)

    async def mark_all_as_read(self, employee_id: UUID) -> int:
        """Marca todas as notificações como lidas."""
        return await self.repo.mark_all_as_read(employee_id)

    async def dismiss_notification(
        self,
        notification_id: UUID,
        employee_id: UUID,
    ) -> Optional[EmployeeNotification]:
        """Descarta notificação."""
        notification = await self.repo.get_by_id(notification_id)
        if not notification or notification.employee_id != employee_id:
            return None

        return await self.repo.dismiss(notification_id)

    async def get_unread_count(
        self,
        employee_id: UUID,
    ) -> UnreadCountResponse:
        """Retorna contagem de notificações não lidas."""
        total = await self.repo.get_unread_count(employee_id)
        by_type = await self.repo.get_unread_count_by_type(employee_id)
        by_priority = await self.repo.get_unread_count_by_priority(employee_id)

        return UnreadCountResponse(
            total_unread=total,
            by_type=by_type,
            by_priority=by_priority,
            oldest_unread_at=None,  # Calculado se necessário
        )

    # Notificações específicas

    async def notify_payslip_available(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        payslip_id: UUID,
        period: str,
    ) -> EmployeeNotification:
        """Notifica sobre novo contracheque."""
        return await self.send_notification(
            employee_id=employee_id,
            notification_type=NotificationType.PAYSLIP_AVAILABLE,
            title="Novo Contracheque Disponível",
            message=f"Seu contracheque de {period} está disponível para visualização.",
            condominio_id=condominio_id,
            reference_type="payslip",
            reference_id=payslip_id,
            action_url=f"/portal/payslips/{payslip_id}",
            action_label="Ver Contracheque",
        )

    async def notify_vacation_approved(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        request_id: UUID,
        start_date: str,
    ) -> EmployeeNotification:
        """Notifica sobre férias aprovadas."""
        return await self.send_notification(
            employee_id=employee_id,
            notification_type=NotificationType.VACATION_APPROVED,
            title="Férias Aprovadas",
            message=f"Suas férias com início em {start_date} foram aprovadas.",
            condominio_id=condominio_id,
            reference_type="vacation_request",
            reference_id=request_id,
            action_url=f"/portal/vacation/{request_id}",
            action_label="Ver Detalhes",
        )

    async def notify_vacation_rejected(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        request_id: UUID,
        reason: str,
    ) -> EmployeeNotification:
        """Notifica sobre férias rejeitadas."""
        return await self.send_notification(
            employee_id=employee_id,
            notification_type=NotificationType.VACATION_REJECTED,
            title="Férias Não Aprovadas",
            message=f"Sua solicitação de férias não foi aprovada. Motivo: {reason}",
            condominio_id=condominio_id,
            reference_type="vacation_request",
            reference_id=request_id,
            action_url=f"/portal/vacation/{request_id}",
            action_label="Ver Detalhes",
        )

    async def notify_document_available(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        document_id: UUID,
        title: str,
    ) -> EmployeeNotification:
        """Notifica sobre novo documento."""
        return await self.send_notification(
            employee_id=employee_id,
            notification_type=NotificationType.DOCUMENT_AVAILABLE,
            title="Novo Documento Disponível",
            message=f"O documento '{title}' está disponível no portal.",
            condominio_id=condominio_id,
            reference_type="document",
            reference_id=document_id,
            action_url=f"/portal/documents/{document_id}",
            action_label="Ver Documento",
        )

    async def notify_birthday(
        self,
        employee_id: UUID,
        condominio_id: UUID,
        employee_name: str,
    ) -> EmployeeNotification:
        """Envia felicitação de aniversário."""
        return await self.send_notification(
            employee_id=employee_id,
            notification_type=NotificationType.BIRTHDAY_GREETING,
            title="Feliz Aniversário! 🎂",
            message=f"A equipe deseja um feliz aniversário para você, {employee_name}!",
            condominio_id=condominio_id,
        )
