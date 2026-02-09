"""Service para sincronização de check-ins offline."""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.mobile_time_clock.models import (
    MobileDevice,
    OfflineQueue,
)
from modules.hr.mobile_time_clock.repositories import (
    MobileCheckInRepository,
    MobileDeviceRepository,
    OfflineQueueRepository,
)
from modules.hr.mobile_time_clock.schemas import (
    CheckInBiometric,
    CheckInLocation,
    CheckInPhoto,
    CheckInValidation,
    MobileCheckInCreate,
    OfflineQueueBatch,
    OfflineQueueItemCreate,
    SyncBatchResult,
    SyncResult,
)
from modules.hr.mobile_time_clock.services.checkin_validation_service import (
    CheckInValidationService,
)

logger = logging.getLogger(__name__)


class OfflineSyncService:
    """Service para sincronização de check-ins offline."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.queue_repo = OfflineQueueRepository(db)
        self.device_repo = MobileDeviceRepository(db)
        self.checkin_repo = MobileCheckInRepository(db)
        self.validation_service = CheckInValidationService(db)

    async def queue_item(
        self,
        data: OfflineQueueItemCreate,
        device: MobileDevice,
    ) -> OfflineQueue:
        """Adiciona item à fila de sincronização."""
        # Verificar duplicata
        existing = await self.queue_repo.get_by_offline_id(data.offline_id)
        if existing:
            logger.warning(f"Item duplicado ignorado: {data.offline_id}")
            return existing

        item = await self.queue_repo.create(
            data=data,
            device_id=device.id,
            employee_id=device.employee_id,
            condominio_id=device.condominio_id,
        )

        logger.info(f"Item adicionado à fila: {item.offline_id}")
        return item

    async def queue_batch(
        self,
        batch: OfflineQueueBatch,
        device: MobileDevice,
    ) -> list[OfflineQueue]:
        """Adiciona batch de itens à fila."""
        items = await self.queue_repo.create_batch(
            items=batch.items,
            device_id=device.id,
            employee_id=device.employee_id,
            condominio_id=device.condominio_id,
        )

        logger.info(f"Batch adicionado: {len(items)} itens")
        return items

    async def sync_item(
        self,
        item: OfflineQueue,
        device: MobileDevice,
    ) -> SyncResult:
        """Sincroniza um item da fila."""
        try:
            # Marcar como processando
            await self.queue_repo.mark_processing(item.id)

            # Verificar expiração
            if item.is_expired:
                await self.queue_repo.mark_failed(item.id, "Item expirado", "EXPIRED")
                return SyncResult(
                    offline_id=item.offline_id,
                    success=False,
                    error_message="Item expirado",
                    error_code="EXPIRED",
                )

            # Verificar duplicata de check-in
            is_duplicate = await self.checkin_repo.check_duplicate(
                employee_id=item.employee_id,
                checkin_type=item.checkin_type,
                device_timestamp=item.device_timestamp,
                tolerance_minutes=5,
            )

            if is_duplicate:
                await self.queue_repo.mark_duplicate(item.id)
                return SyncResult(
                    offline_id=item.offline_id,
                    success=False,
                    error_message="Check-in duplicado",
                    error_code="DUPLICATE",
                )

            # Converter para MobileCheckInCreate
            checkin_data = self._convert_to_checkin_create(item)

            # Processar check-in
            checkin, _ = await self.validation_service.process_checkin(
                data=checkin_data,
                device=device,
                employee_id=item.employee_id,
                condominio_id=item.condominio_id,
            )

            # Marcar item como sincronizado
            await self.queue_repo.mark_synced(item.id, checkin.id)

            return SyncResult(
                offline_id=item.offline_id,
                success=True,
                checkin_id=checkin.id,
            )

        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Erro ao sincronizar item {item.offline_id}: {e}")
            await self.queue_repo.mark_failed(
                item_id=item.id,
                error_message=str(e),
                error_code="SYNC_ERROR",
            )
            return SyncResult(
                offline_id=item.offline_id,
                success=False,
                error_message=str(e),
                error_code="SYNC_ERROR",
            )

    async def sync_device_queue(
        self,
        device: MobileDevice,
        limit: int = 20,
    ) -> SyncBatchResult:
        """Sincroniza fila pendente de um dispositivo."""
        results = []
        total_synced = 0
        total_failed = 0
        total_duplicate = 0
        total_expired = 0

        # Buscar itens pendentes
        items = await self.queue_repo.get_pending(device_id=device.id, limit=limit)

        for item in items:
            result = await self.sync_item(item, device)
            results.append(result)

            if result.success:
                total_synced += 1
            elif result.error_code == "DUPLICATE":
                total_duplicate += 1
            elif result.error_code == "EXPIRED":
                total_expired += 1
            else:
                total_failed += 1

        logger.info(
            f"Sincronização do dispositivo {device.id}: "
            f"{total_synced} synced, {total_failed} failed, "
            f"{total_duplicate} duplicates, {total_expired} expired"
        )

        return SyncBatchResult(
            total_submitted=len(items),
            total_synced=total_synced,
            total_failed=total_failed,
            total_duplicate=total_duplicate,
            total_expired=total_expired,
            results=results,
            server_time=datetime.utcnow(),
        )

    async def process_failed_items(
        self,
        limit: int = 20,
    ) -> SyncBatchResult:
        """Processa itens que falharam e estão prontos para retry."""
        results = []
        total_synced = 0
        total_failed = 0

        # Buscar itens para retry
        items = await self.queue_repo.get_failed_for_retry(limit=limit)

        for item in items:
            # Buscar dispositivo
            device = await self.device_repo.get_by_id(item.device_id)
            if not device:
                await self.queue_repo.mark_failed(
                    item_id=item.id,
                    error_message="Dispositivo não encontrado",
                    error_code="DEVICE_NOT_FOUND",
                )
                continue

            result = await self.sync_item(item, device)
            results.append(result)

            if result.success:
                total_synced += 1
            else:
                total_failed += 1

        return SyncBatchResult(
            total_submitted=len(items),
            total_synced=total_synced,
            total_failed=total_failed,
            total_duplicate=0,
            total_expired=0,
            results=results,
            server_time=datetime.utcnow(),
        )

    async def cleanup_queue(
        self,
        older_than_hours: int = 72,
        statuses: list[str] = None,
        dry_run: bool = True,
    ) -> dict:
        """Limpa itens antigos da fila."""
        # Primeiro marcar expirados
        expired_count = await self.queue_repo.mark_expired_items()
        logger.info(f"Marcados {expired_count} itens como expirados")

        # Limpar
        result = await self.queue_repo.cleanup(
            older_than_hours=older_than_hours,
            statuses=statuses,
            dry_run=dry_run,
        )

        return result

    async def get_device_sync_status(
        self,
        device_id: UUID,
    ) -> dict:
        """Retorna status de sincronização do dispositivo."""
        pending_count = await self.queue_repo.get_device_queue_count(device_id)
        stats = await self.queue_repo.get_statistics()

        return {
            "device_id": str(device_id),
            "pending_items": pending_count,
            "total_queue_items": stats["total_items"],
            "queue_health": "healthy" if pending_count < 10 else "backlogged",
        }

    async def retry_items(
        self,
        item_ids: list[UUID],
        force: bool = False,
    ) -> int:
        """Força retry de itens específicos."""
        count = await self.queue_repo.reset_for_retry(item_ids, force)
        logger.info(f"Reset {count} itens para retry")
        return count

    def _convert_to_checkin_create(
        self,
        item: OfflineQueue,
    ) -> MobileCheckInCreate:
        """Converte item da fila para MobileCheckInCreate."""
        checkin_data = item.checkin_data or {}

        # Localização
        location = None
        if item.latitude and item.longitude:
            location = CheckInLocation(
                latitude=item.latitude,
                longitude=item.longitude,
                accuracy_meters=item.accuracy_meters,
                altitude=checkin_data.get("altitude"),
                provider=checkin_data.get("location_provider", "gps"),
            )

        # Biometria
        biometric = None
        if checkin_data.get("biometric"):
            bio_data = checkin_data["biometric"]
            biometric = CheckInBiometric(
                verified=bio_data.get("verified", False),
                type=bio_data.get("type"),
                score=bio_data.get("score"),
            )

        # Foto
        photo = None
        if checkin_data.get("photo"):
            photo_data = checkin_data["photo"]
            photo = CheckInPhoto(
                captured=photo_data.get("captured", False),
                path=photo_data.get("path"),
                match_score=photo_data.get("match_score"),
            )

        # Validação adicional
        validation = None
        if checkin_data.get("validation"):
            val_data = checkin_data["validation"]
            validation = CheckInValidation(
                wifi_ssid=val_data.get("wifi_ssid"),
                wifi_bssid=val_data.get("wifi_bssid"),
                beacon_uuid=val_data.get("beacon_uuid"),
                nfc_tag_id=val_data.get("nfc_tag_id"),
                qr_code_data=val_data.get("qr_code_data"),
            )

        return MobileCheckInCreate(
            checkin_type=item.checkin_type,
            device_timestamp=item.device_timestamp,
            app_version=item.app_version,
            device_info=item.device_info,
            location=location,
            biometric=biometric,
            photo=photo,
            validation=validation,
            is_offline=True,
            offline_id=item.offline_id,
        )
