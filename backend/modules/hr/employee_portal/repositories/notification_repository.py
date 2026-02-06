"""Repository para notificações do funcionário."""

import logging
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, func, and_, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.employee_portal.models import (
    EmployeeNotification,
    NotificationType,
    NotificationPriority,
)
from modules.hr.employee_portal.schemas import NotificationCreate

logger = logging.getLogger(__name__)


class NotificationRepository:
    """Repository para operações de notificações."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: NotificationCreate,
        condominio_id: UUID,
        *,
        created_by: Optional[UUID] = None,
    ) -> EmployeeNotification:
        """Cria nova notificação."""
        notification = EmployeeNotification(
            id=uuid4(),
            condominio_id=condominio_id,
            employee_id=data.employee_id,
            notification_type=data.notification_type.value,
            priority=data.priority.value,
            title=data.title,
            message=data.message,
            short_message=data.short_message or data.message[:200],
            icon=data.icon,
            color=data.color,
            image_url=data.image_url,
            action_url=data.action_url,
            action_label=data.action_label,
            action_type=data.action_type,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            channels=[c.value for c in data.channels],
            scheduled_at=data.scheduled_at,
            expires_at=data.expires_at,
            is_recurring=data.is_recurring,
            recurrence_pattern=data.recurrence_pattern,
            extra_data=data.extra_data,
            created_by=created_by,
        )

        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)

        logger.info(
            "Notificação %s criada para funcionário %s",
            notification.id,
            data.employee_id,
        )
        return notification

    async def create_bulk(
        self,
        employee_ids: List[UUID],
        data: dict,
        condominio_id: UUID,
        *,
        created_by: Optional[UUID] = None,
    ) -> List[EmployeeNotification]:
        """Cria notificações em lote."""
        notifications = []

        for employee_id in employee_ids:
            notification = EmployeeNotification(
                id=uuid4(),
                condominio_id=condominio_id,
                employee_id=employee_id,
                notification_type=data["notification_type"],
                priority=data.get("priority", NotificationPriority.NORMAL.value),
                title=data["title"],
                message=data["message"],
                short_message=data.get("short_message", data["message"][:200]),
                icon=data.get("icon"),
                color=data.get("color"),
                action_url=data.get("action_url"),
                action_label=data.get("action_label"),
                channels=data.get("channels", ["portal"]),
                scheduled_at=data.get("scheduled_at"),
                expires_at=data.get("expires_at"),
                extra_data=data.get("extra_data", {}),
                created_by=created_by,
            )
            notifications.append(notification)
            self.db.add(notification)

        await self.db.commit()

        for n in notifications:
            await self.db.refresh(n)

        logger.info("Criadas %d notificações em lote", len(notifications))
        return notifications

    async def get_by_id(self, notification_id: UUID) -> Optional[EmployeeNotification]:
        """Busca notificação por ID."""
        result = await self.db.execute(
            select(EmployeeNotification).where(
                EmployeeNotification.id == notification_id
            )
        )
        return result.scalar_one_or_none()

    async def list_by_employee(
        self,
        employee_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        notification_type: Optional[NotificationType] = None,
        priority: Optional[NotificationPriority] = None,
        is_read: Optional[bool] = None,
        is_active: bool = True,
    ) -> Tuple[List[EmployeeNotification], int]:
        """Lista notificações do funcionário."""
        query = select(EmployeeNotification).where(
            EmployeeNotification.employee_id == employee_id
        )

        if is_active:
            query = query.where(EmployeeNotification.is_active.is_(True))
            query = query.where(EmployeeNotification.is_archived.is_(False))

        if notification_type:
            query = query.where(
                EmployeeNotification.notification_type == notification_type.value
            )

        if priority:
            query = query.where(EmployeeNotification.priority == priority.value)

        if is_read is not None:
            query = query.where(EmployeeNotification.is_read == is_read)

        # Total
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Paginação
        query = query.order_by(desc(EmployeeNotification.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def mark_as_read(
        self,
        notification_id: UUID,
    ) -> Optional[EmployeeNotification]:
        """Marca notificação como lida."""
        notification = await self.get_by_id(notification_id)
        if not notification:
            return None

        notification.mark_as_read()
        await self.db.commit()
        await self.db.refresh(notification)

        return notification

    async def mark_multiple_as_read(
        self,
        notification_ids: List[UUID],
    ) -> int:
        """Marca múltiplas notificações como lidas."""
        now = datetime.utcnow()
        result = await self.db.execute(
            update(EmployeeNotification)
            .where(
                and_(
                    EmployeeNotification.id.in_(notification_ids),
                    EmployeeNotification.is_read.is_(False),
                )
            )
            .values(is_read=True, read_at=now)
        )
        await self.db.commit()
        return result.rowcount

    async def mark_all_as_read(self, employee_id: UUID) -> int:
        """Marca todas as notificações como lidas."""
        now = datetime.utcnow()
        result = await self.db.execute(
            update(EmployeeNotification)
            .where(
                and_(
                    EmployeeNotification.employee_id == employee_id,
                    EmployeeNotification.is_read.is_(False),
                    EmployeeNotification.is_active.is_(True),
                )
            )
            .values(is_read=True, read_at=now)
        )
        await self.db.commit()
        return result.rowcount

    async def dismiss(
        self,
        notification_id: UUID,
    ) -> Optional[EmployeeNotification]:
        """Descarta notificação."""
        notification = await self.get_by_id(notification_id)
        if not notification:
            return None

        notification.dismiss()
        await self.db.commit()
        await self.db.refresh(notification)

        return notification

    async def dismiss_multiple(
        self,
        notification_ids: List[UUID],
    ) -> int:
        """Descarta múltiplas notificações."""
        now = datetime.utcnow()
        result = await self.db.execute(
            update(EmployeeNotification)
            .where(EmployeeNotification.id.in_(notification_ids))
            .values(dismissed_at=now, is_active=False)
        )
        await self.db.commit()
        return result.rowcount

    async def get_unread_count(self, employee_id: UUID) -> int:
        """Conta notificações não lidas."""
        result = await self.db.execute(
            select(func.count(EmployeeNotification.id)).where(
                and_(
                    EmployeeNotification.employee_id == employee_id,
                    EmployeeNotification.is_read.is_(False),
                    EmployeeNotification.is_active.is_(True),
                    EmployeeNotification.is_archived.is_(False),
                )
            )
        )
        return result.scalar() or 0

    async def get_unread_count_by_type(self, employee_id: UUID) -> dict:
        """Conta notificações não lidas por tipo."""
        result = await self.db.execute(
            select(
                EmployeeNotification.notification_type,
                func.count(EmployeeNotification.id),
            )
            .where(
                and_(
                    EmployeeNotification.employee_id == employee_id,
                    EmployeeNotification.is_read.is_(False),
                    EmployeeNotification.is_active.is_(True),
                )
            )
            .group_by(EmployeeNotification.notification_type)
        )
        return dict(result.all())

    async def get_unread_count_by_priority(self, employee_id: UUID) -> dict:
        """Conta notificações não lidas por prioridade."""
        result = await self.db.execute(
            select(
                EmployeeNotification.priority,
                func.count(EmployeeNotification.id),
            )
            .where(
                and_(
                    EmployeeNotification.employee_id == employee_id,
                    EmployeeNotification.is_read.is_(False),
                    EmployeeNotification.is_active.is_(True),
                )
            )
            .group_by(EmployeeNotification.priority)
        )
        return dict(result.all())

    async def record_email_sent(
        self,
        notification_id: UUID,
    ) -> Optional[EmployeeNotification]:
        """Registra envio de email."""
        notification = await self.get_by_id(notification_id)
        if not notification:
            return None

        notification.email_sent = True
        notification.email_sent_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(notification)

        return notification

    async def record_push_sent(
        self,
        notification_id: UUID,
    ) -> Optional[EmployeeNotification]:
        """Registra envio de push."""
        notification = await self.get_by_id(notification_id)
        if not notification:
            return None

        notification.push_sent = True
        notification.push_sent_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(notification)

        return notification

    async def get_pending_delivery(
        self,
        channel: str,
        *,
        limit: int = 100,
    ) -> List[EmployeeNotification]:
        """Busca notificações pendentes de entrega."""
        query = select(EmployeeNotification).where(
            and_(
                EmployeeNotification.is_active.is_(True),
                EmployeeNotification.channels.contains([channel]),
            )
        )

        if channel == "email":
            query = query.where(EmployeeNotification.email_sent.is_(False))
        elif channel == "push":
            query = query.where(EmployeeNotification.push_sent.is_(False))
        elif channel == "sms":
            query = query.where(EmployeeNotification.sms_sent.is_(False))

        query = query.order_by(EmployeeNotification.created_at).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def archive_old_notifications(
        self,
        days_old: int = 90,
    ) -> int:
        """Arquiva notificações antigas."""
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=days_old)
        result = await self.db.execute(
            update(EmployeeNotification)
            .where(
                and_(
                    EmployeeNotification.created_at < cutoff,
                    EmployeeNotification.is_archived.is_(False),
                )
            )
            .values(is_archived=True)
        )
        await self.db.commit()
        return result.rowcount
