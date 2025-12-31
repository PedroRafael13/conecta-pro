"""Repository para MobileDevice."""

from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.mobile_time_clock.models import (
    MobileDevice,
    DeviceStatus,
)
from modules.hr.mobile_time_clock.schemas import (
    MobileDeviceRegister,
    MobileDeviceUpdate,
    MobileDeviceFilter,
)


class MobileDeviceRepository:
    """Repository para operações com dispositivos móveis."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: MobileDeviceRegister,
        employee_id: UUID,
        condominio_id: UUID,
    ) -> MobileDevice:
        """Cria novo dispositivo."""
        device = MobileDevice(
            employee_id=employee_id,
            condominio_id=condominio_id,
            device_name=data.device_name,
            device_uuid=data.device_uuid,
            platform=data.platform,
            os_version=data.os_version,
            app_version=data.app_version,
            model=data.model,
            manufacturer=data.manufacturer,
            push_token=data.push_token,
            push_provider=data.push_provider,
            biometric_capability=data.biometric_capability,
            device_info=data.device_info or {},
            status=DeviceStatus.PENDING.value,
            first_seen_at=datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
        )

        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def get_by_id(self, device_id: UUID) -> Optional[MobileDevice]:
        """Busca dispositivo por ID."""
        result = await self.db.execute(
            select(MobileDevice).where(MobileDevice.id == device_id)
        )
        return result.scalar_one_or_none()

    async def get_by_uuid(self, device_uuid: str) -> Optional[MobileDevice]:
        """Busca dispositivo por UUID."""
        result = await self.db.execute(
            select(MobileDevice).where(MobileDevice.device_uuid == device_uuid)
        )
        return result.scalar_one_or_none()

    async def get_by_employee(
        self,
        employee_id: UUID,
        active_only: bool = True,
    ) -> List[MobileDevice]:
        """Busca dispositivos do funcionário."""
        query = select(MobileDevice).where(MobileDevice.employee_id == employee_id)

        if active_only:
            query = query.where(MobileDevice.is_active == True)

        result = await self.db.execute(query.order_by(MobileDevice.last_seen_at.desc()))
        return list(result.scalars().all())

    async def update(
        self,
        device_id: UUID,
        data: MobileDeviceUpdate,
    ) -> Optional[MobileDevice]:
        """Atualiza dispositivo."""
        device = await self.get_by_id(device_id)
        if not device:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(device, key, value)

        device.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def approve(
        self,
        device_id: UUID,
        approved_by: UUID,
        is_trusted: bool = False,
        **kwargs,
    ) -> Optional[MobileDevice]:
        """Aprova dispositivo."""
        device = await self.get_by_id(device_id)
        if not device:
            return None

        device.status = DeviceStatus.ACTIVE.value
        device.approved_by = approved_by
        device.approved_at = datetime.utcnow()
        device.is_trusted = is_trusted
        device.trust_score = 50 if is_trusted else 30

        for key, value in kwargs.items():
            if hasattr(device, key):
                setattr(device, key, value)

        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def block(
        self,
        device_id: UUID,
        blocked_by: UUID,
        reason: str,
    ) -> Optional[MobileDevice]:
        """Bloqueia dispositivo."""
        device = await self.get_by_id(device_id)
        if not device:
            return None

        device.status = DeviceStatus.BLOCKED.value
        device.blocked_by = blocked_by
        device.blocked_at = datetime.utcnow()
        device.blocked_reason = reason
        device.trust_score = 0

        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def unblock(self, device_id: UUID) -> Optional[MobileDevice]:
        """Desbloqueia dispositivo."""
        device = await self.get_by_id(device_id)
        if not device:
            return None

        device.status = DeviceStatus.ACTIVE.value
        device.blocked_reason = None
        device.trust_score = 30

        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def update_heartbeat(
        self,
        device_id: UUID,
        app_version: str = None,
        latitude: float = None,
        longitude: float = None,
    ) -> None:
        """Atualiza heartbeat do dispositivo."""
        update_values = {"last_seen_at": datetime.utcnow()}

        if app_version:
            update_values["app_version"] = app_version
        if latitude and longitude:
            update_values["last_known_lat"] = latitude
            update_values["last_known_lng"] = longitude
            update_values["last_location_at"] = datetime.utcnow()

        await self.db.execute(
            update(MobileDevice)
            .where(MobileDevice.id == device_id)
            .values(**update_values)
        )
        await self.db.commit()

    async def increment_checkin_count(self, device_id: UUID) -> None:
        """Incrementa contador de check-ins."""
        await self.db.execute(
            update(MobileDevice)
            .where(MobileDevice.id == device_id)
            .values(
                checkin_count=MobileDevice.checkin_count + 1,
                last_seen_at=datetime.utcnow(),
            )
        )
        await self.db.commit()

    async def record_failed_attempt(self, device_id: UUID) -> None:
        """Registra tentativa falha."""
        device = await self.get_by_id(device_id)
        if device:
            device.failed_attempts += 1
            device.last_failed_at = datetime.utcnow()

            # Bloquear após 10 tentativas
            if device.failed_attempts >= 10:
                device.status = DeviceStatus.BLOCKED.value
                device.blocked_reason = "Muitas tentativas falhas"
                device.trust_score = 0

            await self.db.commit()

    async def reset_failed_attempts(self, device_id: UUID) -> None:
        """Reseta tentativas falhas."""
        await self.db.execute(
            update(MobileDevice)
            .where(MobileDevice.id == device_id)
            .values(failed_attempts=0, last_failed_at=None)
        )
        await self.db.commit()

    async def update_push_token(
        self,
        device_id: UUID,
        push_token: str,
        push_provider: str,
    ) -> None:
        """Atualiza token de push."""
        await self.db.execute(
            update(MobileDevice)
            .where(MobileDevice.id == device_id)
            .values(push_token=push_token, push_provider=push_provider)
        )
        await self.db.commit()

    async def list_devices(
        self,
        filters: MobileDeviceFilter,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[MobileDevice], int]:
        """Lista dispositivos com filtros."""
        query = select(MobileDevice)

        if filters.employee_id:
            query = query.where(MobileDevice.employee_id == filters.employee_id)
        if filters.condominio_id:
            query = query.where(MobileDevice.condominio_id == filters.condominio_id)
        if filters.platform:
            query = query.where(MobileDevice.platform == filters.platform)
        if filters.status:
            query = query.where(MobileDevice.status == filters.status)
        if filters.is_trusted is not None:
            query = query.where(MobileDevice.is_trusted == filters.is_trusted)
        if filters.is_active is not None:
            query = query.where(MobileDevice.is_active == filters.is_active)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        query = query.order_by(MobileDevice.last_seen_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_pending_approval(
        self,
        condominio_id: UUID,
    ) -> List[MobileDevice]:
        """Lista dispositivos aguardando aprovação."""
        result = await self.db.execute(
            select(MobileDevice)
            .where(MobileDevice.condominio_id == condominio_id)
            .where(MobileDevice.status == DeviceStatus.PENDING.value)
            .order_by(MobileDevice.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_statistics(
        self,
        condominio_id: UUID = None,
    ) -> dict:
        """Obtém estatísticas de dispositivos."""
        query = select(MobileDevice)
        if condominio_id:
            query = query.where(MobileDevice.condominio_id == condominio_id)

        result = await self.db.execute(query)
        devices = list(result.scalars().all())

        by_platform = {}
        by_status = {}
        trust_scores = []
        biometric_count = 0
        offline_count = 0

        for device in devices:
            by_platform[device.platform] = by_platform.get(device.platform, 0) + 1
            by_status[device.status] = by_status.get(device.status, 0) + 1
            trust_scores.append(device.trust_score)
            if device.biometric_enabled:
                biometric_count += 1
            if device.allow_offline_checkin:
                offline_count += 1

        return {
            "total_devices": len(devices),
            "active_devices": by_status.get(DeviceStatus.ACTIVE.value, 0),
            "pending_approval": by_status.get(DeviceStatus.PENDING.value, 0),
            "blocked_devices": by_status.get(DeviceStatus.BLOCKED.value, 0),
            "by_platform": by_platform,
            "by_status": by_status,
            "avg_trust_score": sum(trust_scores) / len(trust_scores) if trust_scores else 0,
            "devices_with_biometric": biometric_count,
            "devices_with_offline": offline_count,
        }

    async def delete(self, device_id: UUID) -> bool:
        """Remove dispositivo."""
        device = await self.get_by_id(device_id)
        if not device:
            return False

        await self.db.delete(device)
        await self.db.commit()
        return True

    async def soft_delete(self, device_id: UUID) -> bool:
        """Desativa dispositivo (soft delete)."""
        device = await self.get_by_id(device_id)
        if not device:
            return False

        device.is_active = False
        device.status = DeviceStatus.REVOKED.value
        await self.db.commit()
        return True
