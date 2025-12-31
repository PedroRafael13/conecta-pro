"""Service para envio de push notifications."""

import logging
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.mobile_time_clock.models import MobileDevice, DeviceStatus
from modules.hr.mobile_time_clock.repositories import MobileDeviceRepository

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Tipos de notificação."""
    CHECKIN_REMINDER = "checkin_reminder"
    CHECKIN_CONFIRMED = "checkin_confirmed"
    CHECKIN_REJECTED = "checkin_rejected"
    DEVICE_APPROVED = "device_approved"
    DEVICE_BLOCKED = "device_blocked"
    GEOFENCE_ENTER = "geofence_enter"
    GEOFENCE_EXIT = "geofence_exit"
    SHIFT_START = "shift_start"
    SHIFT_END = "shift_end"
    OVERTIME_WARNING = "overtime_warning"
    BREAK_REMINDER = "break_reminder"
    SYNC_REQUIRED = "sync_required"


class PushNotificationService:
    """Service para envio de notificações push."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.device_repo = MobileDeviceRepository(db)
        # Configurações dos providers seriam injetadas via config
        self._fcm_enabled = True
        self._apns_enabled = True

    async def send_to_device(
        self,
        device: MobileDevice,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Dict[str, Any] = None,
    ) -> bool:
        """Envia notificação para um dispositivo."""
        if not device.push_token:
            logger.warning(f"Dispositivo {device.id} sem push token")
            return False

        if device.status != DeviceStatus.ACTIVE.value:
            logger.warning(f"Dispositivo {device.id} não está ativo")
            return False

        payload = self._build_payload(
            notification_type=notification_type,
            title=title,
            body=body,
            data=data,
        )

        try:
            if device.push_provider == "fcm":
                return await self._send_fcm(device.push_token, payload)
            elif device.push_provider == "apns":
                return await self._send_apns(device.push_token, payload)
            else:
                logger.error(f"Provider desconhecido: {device.push_provider}")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar push para {device.id}: {e}")
            return False

    async def send_to_employee(
        self,
        employee_id: UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Dict[str, Any] = None,
    ) -> int:
        """Envia notificação para todos os dispositivos de um funcionário."""
        devices = await self.device_repo.get_by_employee(
            employee_id=employee_id,
            active_only=True,
        )

        sent_count = 0
        for device in devices:
            if await self.send_to_device(device, notification_type, title, body, data):
                sent_count += 1

        return sent_count

    async def send_to_condominio(
        self,
        condominio_id: UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Dict[str, Any] = None,
        employee_ids: List[UUID] = None,
    ) -> int:
        """Envia notificação para dispositivos do condomínio."""
        from modules.hr.mobile_time_clock.schemas import MobileDeviceFilter

        filters = MobileDeviceFilter(
            condominio_id=condominio_id,
            is_active=True,
        )

        devices, _ = await self.device_repo.list_devices(filters, page_size=1000)

        if employee_ids:
            devices = [d for d in devices if d.employee_id in employee_ids]

        sent_count = 0
        for device in devices:
            if await self.send_to_device(device, notification_type, title, body, data):
                sent_count += 1

        logger.info(f"Enviadas {sent_count}/{len(devices)} notificações para condomínio {condominio_id}")
        return sent_count

    async def notify_checkin_confirmed(
        self,
        device: MobileDevice,
        checkin_type: str,
        checkin_time: datetime,
    ) -> bool:
        """Notifica confirmação de check-in."""
        type_names = {
            "entry": "entrada",
            "exit": "saída",
            "break_start": "início de intervalo",
            "break_end": "fim de intervalo",
        }

        type_name = type_names.get(checkin_type, checkin_type)

        return await self.send_to_device(
            device=device,
            notification_type=NotificationType.CHECKIN_CONFIRMED,
            title="Check-in Confirmado",
            body=f"Sua {type_name} foi registrada às {checkin_time.strftime('%H:%M')}",
            data={
                "checkin_type": checkin_type,
                "checkin_time": checkin_time.isoformat(),
            },
        )

    async def notify_checkin_rejected(
        self,
        device: MobileDevice,
        reason: str,
    ) -> bool:
        """Notifica rejeição de check-in."""
        return await self.send_to_device(
            device=device,
            notification_type=NotificationType.CHECKIN_REJECTED,
            title="Check-in Rejeitado",
            body=f"Seu registro foi rejeitado: {reason}",
            data={"reason": reason},
        )

    async def notify_device_approved(
        self,
        device: MobileDevice,
    ) -> bool:
        """Notifica aprovação de dispositivo."""
        return await self.send_to_device(
            device=device,
            notification_type=NotificationType.DEVICE_APPROVED,
            title="Dispositivo Aprovado",
            body="Seu dispositivo foi aprovado para registro de ponto",
        )

    async def notify_device_blocked(
        self,
        device: MobileDevice,
        reason: str,
    ) -> bool:
        """Notifica bloqueio de dispositivo."""
        return await self.send_to_device(
            device=device,
            notification_type=NotificationType.DEVICE_BLOCKED,
            title="Dispositivo Bloqueado",
            body=f"Seu dispositivo foi bloqueado: {reason}",
            data={"reason": reason},
        )

    async def notify_checkin_reminder(
        self,
        employee_id: UUID,
        shift_time: datetime,
    ) -> int:
        """Envia lembrete de check-in."""
        return await self.send_to_employee(
            employee_id=employee_id,
            notification_type=NotificationType.CHECKIN_REMINDER,
            title="Lembrete de Ponto",
            body=f"Seu turno começa às {shift_time.strftime('%H:%M')}. Não esqueça de registrar!",
            data={"shift_time": shift_time.isoformat()},
        )

    async def notify_overtime_warning(
        self,
        employee_id: UUID,
        hours_worked: float,
        max_hours: float,
    ) -> int:
        """Avisa sobre hora extra."""
        return await self.send_to_employee(
            employee_id=employee_id,
            notification_type=NotificationType.OVERTIME_WARNING,
            title="Aviso de Hora Extra",
            body=f"Você trabalhou {hours_worked:.1f}h. Limite: {max_hours:.1f}h",
            data={
                "hours_worked": hours_worked,
                "max_hours": max_hours,
            },
        )

    async def notify_break_reminder(
        self,
        employee_id: UUID,
        hours_since_last_break: float,
    ) -> int:
        """Lembra de fazer intervalo."""
        return await self.send_to_employee(
            employee_id=employee_id,
            notification_type=NotificationType.BREAK_REMINDER,
            title="Hora do Intervalo",
            body=f"Você está trabalhando há {hours_since_last_break:.1f}h. Faça uma pausa!",
        )

    async def notify_sync_required(
        self,
        device: MobileDevice,
        pending_count: int,
    ) -> bool:
        """Avisa que há itens para sincronizar."""
        return await self.send_to_device(
            device=device,
            notification_type=NotificationType.SYNC_REQUIRED,
            title="Sincronização Pendente",
            body=f"Você tem {pending_count} registros para sincronizar",
            data={"pending_count": pending_count},
        )

    def _build_payload(
        self,
        notification_type: NotificationType,
        title: str,
        body: str,
        data: Dict[str, Any] = None,
    ) -> dict:
        """Constrói payload da notificação."""
        return {
            "notification": {
                "title": title,
                "body": body,
            },
            "data": {
                "type": notification_type.value,
                "timestamp": datetime.utcnow().isoformat(),
                **(data or {}),
            },
        }

    async def _send_fcm(
        self,
        token: str,
        payload: dict,
    ) -> bool:
        """Envia via Firebase Cloud Messaging."""
        if not self._fcm_enabled:
            logger.warning("FCM desabilitado")
            return False

        # Implementação real usaria firebase-admin SDK
        # from firebase_admin import messaging
        #
        # message = messaging.Message(
        #     notification=messaging.Notification(
        #         title=payload["notification"]["title"],
        #         body=payload["notification"]["body"],
        #     ),
        #     data=payload["data"],
        #     token=token,
        # )
        # response = messaging.send(message)

        logger.info(f"FCM: Enviando para {token[:20]}...")
        # Simular envio bem-sucedido
        return True

    async def _send_apns(
        self,
        token: str,
        payload: dict,
    ) -> bool:
        """Envia via Apple Push Notification Service."""
        if not self._apns_enabled:
            logger.warning("APNS desabilitado")
            return False

        # Implementação real usaria httpx ou aioapns
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"https://api.push.apple.com/3/device/{token}",
        #         json=payload,
        #         headers={"authorization": f"bearer {jwt_token}"},
        #     )

        logger.info(f"APNS: Enviando para {token[:20]}...")
        # Simular envio bem-sucedido
        return True
