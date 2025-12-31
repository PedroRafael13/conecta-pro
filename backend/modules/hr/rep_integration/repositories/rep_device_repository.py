"""Repository para REPDevice."""

from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.rep_integration.models import (
    REPDevice,
    DeviceStatus,
)
from modules.hr.rep_integration.schemas import (
    REPDeviceCreate,
    REPDeviceUpdate,
    REPDeviceFilter,
)


class REPDeviceRepository:
    """Repository para operações de REPDevice."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: REPDeviceCreate) -> REPDevice:
        """Cria novo dispositivo."""
        device = REPDevice(
            condominio_id=data.condominio_id,
            manufacturer=data.manufacturer,
            model=data.model,
            firmware_version=data.firmware_version,
            mte_registration=data.mte_registration,
            serial_number=data.serial_number,
            device_name=data.device_name,
            description=data.description,
            location=data.location,
            latitude=data.latitude,
            longitude=data.longitude,
            geofence_radius=data.geofence_radius,
            ip_address=data.ip_address,
            port=data.port,
            mac_address=data.mac_address,
            communication_protocol=data.communication_protocol,
            auth_method=data.auth_method,
            auth_username=data.auth_username,
            sync_enabled=data.sync_enabled,
            sync_interval_seconds=data.sync_interval_seconds,
            sync_mode=data.sync_mode,
            webhook_url=data.webhook_url,
            webhook_secret=data.webhook_secret,
            supports_biometric=data.supports_biometric,
            supports_facial=data.supports_facial,
            supports_rfid=data.supports_rfid,
            supports_password=data.supports_password,
            supports_qrcode=data.supports_qrcode,
            timezone=data.timezone,
            endpoints_config=data.endpoints_config or {},
            vendor_config=data.vendor_config or {},
            status=DeviceStatus.OFFLINE.value,
        )

        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def get_by_id(self, device_id: UUID) -> Optional[REPDevice]:
        """Busca dispositivo por ID."""
        result = await self.db.execute(
            select(REPDevice).where(REPDevice.id == device_id)
        )
        return result.scalar_one_or_none()

    async def get_by_serial(self, serial_number: str) -> Optional[REPDevice]:
        """Busca dispositivo por número de série."""
        result = await self.db.execute(
            select(REPDevice).where(REPDevice.serial_number == serial_number)
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        device_id: UUID,
        data: REPDeviceUpdate,
        updated_by: UUID = None,
    ) -> Optional[REPDevice]:
        """Atualiza dispositivo."""
        device = await self.get_by_id(device_id)
        if not device:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(device, field, value)

        device.updated_at = datetime.utcnow()
        if updated_by:
            device.updated_by = updated_by

        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def delete(self, device_id: UUID) -> bool:
        """Desativa dispositivo (soft delete)."""
        device = await self.get_by_id(device_id)
        if not device:
            return False

        device.is_active = False
        device.updated_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def list_devices(
        self,
        filters: REPDeviceFilter,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[REPDevice], int]:
        """Lista dispositivos com filtros e paginação."""
        query = select(REPDevice).where(REPDevice.is_active.is_(True))

        # Aplicar filtros
        if filters.condominio_id:
            query = query.where(REPDevice.condominio_id == filters.condominio_id)
        if filters.manufacturer:
            query = query.where(REPDevice.manufacturer == filters.manufacturer)
        if filters.model:
            query = query.where(REPDevice.model == filters.model)
        if filters.status:
            query = query.where(REPDevice.status == filters.status)
        if filters.sync_enabled is not None:
            query = query.where(REPDevice.sync_enabled == filters.sync_enabled)
        if filters.location:
            query = query.where(REPDevice.location.ilike(f"%{filters.location}%"))
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    REPDevice.device_name.ilike(search_term),
                    REPDevice.serial_number.ilike(search_term),
                    REPDevice.location.ilike(search_term),
                )
            )

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(REPDevice.device_name)

        result = await self.db.execute(query)
        devices = result.scalars().all()

        return list(devices), total

    async def get_devices_for_sync(
        self,
        condominio_id: UUID = None,
    ) -> List[REPDevice]:
        """Retorna dispositivos que precisam sincronizar."""
        query = select(REPDevice).where(
            REPDevice.is_active.is_(True),
            REPDevice.sync_enabled.is_(True),
            REPDevice.status != DeviceStatus.DISABLED.value,
        )

        if condominio_id:
            query = query.where(REPDevice.condominio_id == condominio_id)

        result = await self.db.execute(query)
        devices = result.scalars().all()

        # Filtrar os que precisam sync
        now = datetime.utcnow()
        return [
            d for d in devices
            if d.last_sync is None or
            (now - d.last_sync).total_seconds() >= d.sync_interval_seconds
        ]

    async def update_status(
        self,
        device_id: UUID,
        status: str,
        error_message: str = None,
    ) -> None:
        """Atualiza status do dispositivo."""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow(),
        }

        if status == DeviceStatus.ONLINE.value:
            update_data["last_online"] = datetime.utcnow()
            update_data["consecutive_errors"] = 0
            update_data["last_error"] = None
        elif status == DeviceStatus.ERROR.value and error_message:
            update_data["last_error"] = error_message
            update_data["last_error_at"] = datetime.utcnow()

        await self.db.execute(
            update(REPDevice)
            .where(REPDevice.id == device_id)
            .values(**update_data)
        )
        await self.db.commit()

    async def increment_error_count(self, device_id: UUID) -> int:
        """Incrementa contador de erros consecutivos."""
        device = await self.get_by_id(device_id)
        if device:
            device.consecutive_errors += 1
            device.updated_at = datetime.utcnow()
            await self.db.commit()
            return device.consecutive_errors
        return 0

    async def update_sync_timestamp(
        self,
        device_id: UUID,
        last_nsr: int = None,
        events_count: int = None,
    ) -> None:
        """Atualiza timestamp de última sincronização."""
        update_data = {
            "last_sync": datetime.utcnow(),
            "status": DeviceStatus.ONLINE.value,
            "updated_at": datetime.utcnow(),
        }

        if events_count is not None:
            update_data["events_count"] = events_count

        await self.db.execute(
            update(REPDevice)
            .where(REPDevice.id == device_id)
            .values(**update_data)
        )
        await self.db.commit()

    async def update_counters(
        self,
        device_id: UUID,
        users: int = None,
        fingerprints: int = None,
        faces: int = None,
        events_pending: int = None,
    ) -> None:
        """Atualiza contadores do dispositivo."""
        update_data = {"updated_at": datetime.utcnow()}

        if users is not None:
            update_data["registered_users"] = users
        if fingerprints is not None:
            update_data["registered_fingerprints"] = fingerprints
        if faces is not None:
            update_data["registered_faces"] = faces
        if events_pending is not None:
            update_data["events_pending_sync"] = events_pending

        await self.db.execute(
            update(REPDevice)
            .where(REPDevice.id == device_id)
            .values(**update_data)
        )
        await self.db.commit()

    async def get_statistics(
        self,
        condominio_id: UUID = None,
    ) -> dict:
        """Retorna estatísticas dos dispositivos."""
        base_query = select(REPDevice).where(REPDevice.is_active.is_(True))

        if condominio_id:
            base_query = base_query.where(REPDevice.condominio_id == condominio_id)

        # Total
        total_result = await self.db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = total_result.scalar() or 0

        # Por status
        status_result = await self.db.execute(
            select(
                REPDevice.status,
                func.count(REPDevice.id)
            )
            .where(REPDevice.is_active.is_(True))
            .group_by(REPDevice.status)
        )
        by_status = {row[0]: row[1] for row in status_result.all()}

        # Por fabricante
        manufacturer_result = await self.db.execute(
            select(
                REPDevice.manufacturer,
                func.count(REPDevice.id)
            )
            .where(REPDevice.is_active.is_(True))
            .group_by(REPDevice.manufacturer)
        )
        by_manufacturer = {row[0]: row[1] for row in manufacturer_result.all()}

        # Contadores
        counters_result = await self.db.execute(
            select(
                func.sum(REPDevice.registered_users),
                func.sum(REPDevice.registered_fingerprints),
                func.sum(REPDevice.registered_faces),
                func.sum(REPDevice.events_count),
                func.sum(REPDevice.events_pending_sync),
            )
            .where(REPDevice.is_active.is_(True))
        )
        counters = counters_result.one()

        return {
            "total_devices": total,
            "devices_by_status": by_status,
            "devices_by_manufacturer": by_manufacturer,
            "total_registered_users": counters[0] or 0,
            "total_fingerprints": counters[1] or 0,
            "total_faces": counters[2] or 0,
            "total_events": counters[3] or 0,
            "pending_sync_events": counters[4] or 0,
            "online_count": by_status.get(DeviceStatus.ONLINE.value, 0),
            "offline_count": by_status.get(DeviceStatus.OFFLINE.value, 0),
            "error_count": by_status.get(DeviceStatus.ERROR.value, 0),
        }
