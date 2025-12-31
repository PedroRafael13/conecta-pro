"""Service para gerenciamento de dispositivos mobile."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.mobile_time_clock.models import (
    MobileDevice,
    DeviceStatus,
)
from modules.hr.mobile_time_clock.repositories import MobileDeviceRepository
from modules.hr.mobile_time_clock.schemas import (
    MobileDeviceRegister,
    MobileDeviceUpdate,
    MobileDeviceApprove,
    MobileDeviceBlock,
    MobileDeviceFilter,
    DeviceHeartbeat,
)
from modules.hr.mobile_time_clock.services.push_notification_service import (
    PushNotificationService,
)

logger = logging.getLogger(__name__)


class DeviceService:
    """Service para gerenciamento de dispositivos mobile."""

    # Limite de dispositivos por funcionário
    MAX_DEVICES_PER_EMPLOYEE = 3

    # Tempo máximo sem heartbeat para considerar offline
    OFFLINE_THRESHOLD_MINUTES = 30

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = MobileDeviceRepository(db)
        self.push_service = PushNotificationService(db)

    async def register_device(
        self,
        data: MobileDeviceRegister,
        employee_id: UUID,
        condominio_id: UUID,
    ) -> Tuple[MobileDevice, bool]:
        """Registra novo dispositivo.

        Retorna:
            - device: MobileDevice
            - is_new: True se criado, False se já existia
        """
        # Verificar se dispositivo já existe
        existing = await self.repository.get_by_uuid(data.device_uuid)
        if existing:
            # Atualizar informações
            update_data = MobileDeviceUpdate(
                device_name=data.device_name,
                os_version=data.os_version,
                app_version=data.app_version,
                push_token=data.push_token,
                push_provider=data.push_provider,
                biometric_capability=data.biometric_capability,
            )
            await self.repository.update(existing.id, update_data)
            await self.repository.update_heartbeat(existing.id, data.app_version)

            logger.info(f"Dispositivo atualizado: {existing.id}")
            return existing, False

        # Verificar limite de dispositivos
        employee_devices = await self.repository.get_by_employee(
            employee_id=employee_id,
            active_only=True,
        )

        if len(employee_devices) >= self.MAX_DEVICES_PER_EMPLOYEE:
            logger.warning(
                f"Funcionário {employee_id} atingiu limite de dispositivos"
            )
            # Poderia desativar o mais antigo ou retornar erro
            oldest = min(employee_devices, key=lambda d: d.last_seen_at)
            await self.repository.soft_delete(oldest.id)
            logger.info(f"Dispositivo antigo desativado: {oldest.id}")

        # Criar novo
        device = await self.repository.create(data, employee_id, condominio_id)
        logger.info(f"Novo dispositivo registrado: {device.id}")

        return device, True

    async def approve_device(
        self,
        device_id: UUID,
        data: MobileDeviceApprove,
        approved_by: UUID,
    ) -> Optional[MobileDevice]:
        """Aprova dispositivo para uso."""
        device = await self.repository.approve(
            device_id=device_id,
            approved_by=approved_by,
            is_trusted=data.is_trusted,
            biometric_enabled=data.biometric_enabled,
            allow_offline_checkin=data.allow_offline_checkin,
            max_offline_hours=data.max_offline_hours,
        )

        if device:
            # Notificar usuário
            await self.push_service.notify_device_approved(device)
            logger.info(f"Dispositivo aprovado: {device_id}")

        return device

    async def block_device(
        self,
        device_id: UUID,
        data: MobileDeviceBlock,
        blocked_by: UUID,
    ) -> Optional[MobileDevice]:
        """Bloqueia dispositivo."""
        device = await self.repository.block(
            device_id=device_id,
            blocked_by=blocked_by,
            reason=data.reason,
        )

        if device:
            # Notificar usuário
            await self.push_service.notify_device_blocked(device, data.reason)
            logger.info(f"Dispositivo bloqueado: {device_id} - {data.reason}")

        return device

    async def unblock_device(self, device_id: UUID) -> Optional[MobileDevice]:
        """Desbloqueia dispositivo."""
        device = await self.repository.unblock(device_id)
        if device:
            logger.info(f"Dispositivo desbloqueado: {device_id}")
        return device

    async def process_heartbeat(
        self,
        device_id: UUID,
        data: DeviceHeartbeat,
    ) -> None:
        """Processa heartbeat do dispositivo."""
        await self.repository.update_heartbeat(
            device_id=device_id,
            app_version=data.app_version,
            latitude=data.latitude,
            longitude=data.longitude,
        )

        # Reset tentativas falhas em heartbeat bem-sucedido
        await self.repository.reset_failed_attempts(device_id)

    async def record_failed_attempt(self, device_id: UUID) -> None:
        """Registra tentativa falha (biometria, foto, etc)."""
        await self.repository.record_failed_attempt(device_id)

    async def update_push_token(
        self,
        device_id: UUID,
        push_token: str,
        push_provider: str,
    ) -> None:
        """Atualiza token de push notification."""
        await self.repository.update_push_token(
            device_id=device_id,
            push_token=push_token,
            push_provider=push_provider,
        )

    async def get_pending_approval(
        self,
        condominio_id: UUID,
    ) -> List[MobileDevice]:
        """Lista dispositivos pendentes de aprovação."""
        return await self.repository.get_pending_approval(condominio_id)

    async def get_employee_devices(
        self,
        employee_id: UUID,
        include_inactive: bool = False,
    ) -> List[MobileDevice]:
        """Lista dispositivos do funcionário."""
        return await self.repository.get_by_employee(
            employee_id=employee_id,
            active_only=not include_inactive,
        )

    async def validate_device_for_checkin(
        self,
        device_uuid: str,
    ) -> Tuple[bool, Optional[MobileDevice], Optional[str]]:
        """Valida se dispositivo pode fazer check-in.

        Retorna:
            - is_valid: bool
            - device: MobileDevice ou None
            - error: mensagem de erro ou None
        """
        device = await self.repository.get_by_uuid(device_uuid)

        if not device:
            return False, None, "Dispositivo não registrado"

        if not device.is_active:
            return False, device, "Dispositivo inativo"

        if device.status == DeviceStatus.PENDING.value:
            return False, device, "Dispositivo aguardando aprovação"

        if device.status == DeviceStatus.BLOCKED.value:
            return False, device, f"Dispositivo bloqueado: {device.blocked_reason}"

        if device.status == DeviceStatus.REVOKED.value:
            return False, device, "Dispositivo revogado"

        if not device.can_checkin:
            return False, device, "Dispositivo sem permissão para check-in"

        return True, device, None

    async def get_offline_devices(
        self,
        condominio_id: UUID = None,
    ) -> List[MobileDevice]:
        """Lista dispositivos que estão offline."""
        threshold = datetime.utcnow() - timedelta(minutes=self.OFFLINE_THRESHOLD_MINUTES)

        filters = MobileDeviceFilter(
            condominio_id=condominio_id,
            is_active=True,
        )

        devices, _ = await self.repository.list_devices(filters, page_size=1000)

        # Filtrar offline
        offline = [d for d in devices if d.last_seen_at < threshold]
        return offline

    async def get_device_statistics(
        self,
        condominio_id: UUID = None,
    ) -> dict:
        """Obtém estatísticas de dispositivos."""
        stats = await self.repository.get_statistics(condominio_id)

        # Adicionar contagem de offline
        offline_devices = await self.get_offline_devices(condominio_id)
        stats["offline_devices"] = len(offline_devices)

        return stats

    async def revoke_device(self, device_id: UUID) -> bool:
        """Revoga dispositivo permanentemente."""
        result = await self.repository.soft_delete(device_id)
        if result:
            logger.info(f"Dispositivo revogado: {device_id}")
        return result

    async def cleanup_inactive_devices(
        self,
        inactive_days: int = 90,
        dry_run: bool = True,
    ) -> dict:
        """Limpa dispositivos inativos."""
        threshold = datetime.utcnow() - timedelta(days=inactive_days)

        filters = MobileDeviceFilter(is_active=True)
        devices, _ = await self.repository.list_devices(filters, page_size=10000)

        to_cleanup = [d for d in devices if d.last_seen_at < threshold]

        if not dry_run:
            for device in to_cleanup:
                await self.repository.soft_delete(device.id)

        return {
            "total_checked": len(devices),
            "to_cleanup": len(to_cleanup),
            "cleaned": len(to_cleanup) if not dry_run else 0,
            "dry_run": dry_run,
        }
