"""Serviço de sincronização com dispositivos REP."""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.rep_integration.models import (
    DeviceStatus,
    REPDevice,
    SyncStatus,
    SyncTrigger,
    SyncType,
)
from modules.hr.rep_integration.repositories import (
    REPDeviceRepository,
    REPEventRepository,
    REPSyncRepository,
)
from modules.hr.rep_integration.schemas import (
    REPEventCreate,
    REPSyncCreate,
)

from .rep_communication_service import REPCommunicationService

logger = logging.getLogger(__name__)


class SyncService:
    """Serviço de sincronização com REPs."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.device_repo = REPDeviceRepository(db)
        self.event_repo = REPEventRepository(db)
        self.sync_repo = REPSyncRepository(db)
        self.comm_service = REPCommunicationService()

    async def sync_device_events(  # pylint: disable=too-many-locals
        self,
        device_id: UUID,
        trigger: str = SyncTrigger.MANUAL.value,
        triggered_by: UUID = None,
        from_nsr: int = None,
        from_datetime: datetime = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Sincroniza eventos de um dispositivo.

        Returns:
            Tuple: (sucesso, resultado)
        """
        # Buscar dispositivo
        device = await self.device_repo.get_by_id(device_id)
        if not device:
            return False, {"error": "Dispositivo não encontrado"}

        if not device.is_active:
            return False, {"error": "Dispositivo inativo"}

        # Verificar se já há sync em andamento
        running = await self.sync_repo.get_running_sync(device_id)
        if running:
            return False, {"error": "Já existe sincronização em andamento"}

        # Criar registro de sync
        sync = await self.sync_repo.create(
            REPSyncCreate(
                device_id=device_id,
                condominio_id=device.condominio_id,
                sync_type=SyncType.EVENTS_PULL.value,
                trigger=trigger,
                triggered_by=triggered_by,
                events_from_datetime=from_datetime,
            )
        )

        try:
            # Iniciar sync
            await self.sync_repo.start_sync(sync.id)

            # Atualizar status do dispositivo
            await self.device_repo.update_status(
                device_id,
                DeviceStatus.SYNCING.value,
            )

            # Obter último NSR se não especificado
            if from_nsr is None:
                from_nsr = await self.event_repo.get_last_nsr(device_id)

            # Buscar eventos do dispositivo
            events = await self.comm_service.get_events(
                device,
                from_nsr=from_nsr,
                from_datetime=from_datetime,
            )

            if not events:
                await self.sync_repo.complete_sync(
                    sync.id,
                    success_items=0,
                    error_items=0,
                    skipped_items=0,
                )
                await self.device_repo.update_sync_timestamp(device_id)
                return True, {"message": "Nenhum evento novo", "sync_id": str(sync.id)}

            # Processar eventos
            created, duplicates, errors = await self._process_events(
                device=device,
                events=events,
                sync_id=sync.id,
            )

            # Obter último NSR
            last_nsr = max(e.get("nsr", 0) for e in events) if events else None

            # Finalizar sync
            await self.sync_repo.complete_sync(
                sync.id,
                success_items=created,
                error_items=errors,
                skipped_items=duplicates,
                last_nsr=last_nsr,
            )

            # Atualizar dispositivo
            await self.device_repo.update_status(device_id, DeviceStatus.ONLINE.value)
            await self.device_repo.update_sync_timestamp(device_id, last_nsr)

            result = {
                "sync_id": str(sync.id),
                "total_events": len(events),
                "created": created,
                "duplicates": duplicates,
                "errors": errors,
                "last_nsr": last_nsr,
            }

            logger.info(f"Sync concluída para dispositivo {device_id}: {result}")
            return True, result

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Erro na sync do dispositivo {device_id}: {e}")

            await self.sync_repo.fail_sync(
                sync.id,
                error_message=str(e),
                error_code="SYNC_ERROR",
            )

            await self.device_repo.update_status(
                device_id,
                DeviceStatus.ERROR.value,
                error_message=str(e),
            )
            await self.device_repo.increment_error_count(device_id)

            return False, {"error": str(e), "sync_id": str(sync.id)}

    async def _process_events(
        self,
        device: REPDevice,
        events: list[dict[str, Any]],
        sync_id: UUID,
    ) -> tuple[int, int, int]:
        """Processa lista de eventos.

        Returns:
            Tuple: (criados, duplicados, erros)
        """
        created = 0
        duplicates = 0
        errors = 0

        for event_data in events:
            try:
                # Verificar duplicado
                existing = await self.event_repo.get_by_device_nsr(
                    device.id,
                    event_data.get("nsr"),
                )

                if existing:
                    duplicates += 1
                    continue

                # Criar evento
                event_datetime = event_data.get("datetime")
                if isinstance(event_datetime, str):
                    event_datetime = datetime.fromisoformat(event_datetime)

                event_create = REPEventCreate(
                    device_id=device.id,
                    condominio_id=device.condominio_id,
                    nsr=event_data.get("nsr"),
                    event_datetime=event_datetime,
                    event_type=event_data.get("event_type", "entry"),
                    pis_number=event_data.get("pis"),
                    employee_code=str(event_data.get("user_id", "")),
                    employee_name=event_data.get("user_name"),
                    identification_method=event_data.get("method", "biometric"),
                    identification_score=event_data.get("score"),
                    raw_data=event_data,
                    sync_id=sync_id,
                )

                await self.event_repo.create(event_create)
                created += 1

            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(f"Erro ao processar evento: {e}")
                errors += 1

        return created, duplicates, errors

    async def sync_all_devices(
        self,
        condominio_id: UUID = None,
    ) -> dict[str, Any]:
        """Sincroniza todos os dispositivos pendentes."""
        devices = await self.device_repo.get_devices_for_sync(condominio_id)

        results = {
            "total_devices": len(devices),
            "success": 0,
            "failed": 0,
            "details": [],
        }

        for device in devices:
            success, result = await self.sync_device_events(
                device.id,
                trigger=SyncTrigger.SCHEDULED.value,
            )

            if success:
                results["success"] += 1
            else:
                results["failed"] += 1

            results["details"].append(
                {
                    "device_id": str(device.id),
                    "device_name": device.device_name,
                    "success": success,
                    "result": result,
                }
            )

        return results

    async def process_webhook_events(
        self,
        device_serial: str,
        events: list[dict[str, Any]],
        signature: str = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Processa eventos recebidos via webhook.

        Returns:
            Tuple: (sucesso, resultado)
        """
        # Buscar dispositivo pelo serial
        device = await self.device_repo.get_by_serial(device_serial)
        if not device:
            return False, {"error": "Dispositivo não encontrado"}

        # Validar signature se configurado
        if device.webhook_secret and signature:
            # TODO: Implementar validação HMAC  # pylint: disable=fixme
            pass

        # Criar registro de sync
        sync = await self.sync_repo.create(
            REPSyncCreate(
                device_id=device.id,
                condominio_id=device.condominio_id,
                sync_type=SyncType.EVENTS_PUSH.value,
                trigger=SyncTrigger.WEBHOOK.value,
            )
        )

        try:
            await self.sync_repo.start_sync(sync.id)

            created, duplicates, errors = await self._process_events(
                device=device,
                events=events,
                sync_id=sync.id,
            )

            await self.sync_repo.complete_sync(
                sync.id,
                success_items=created,
                error_items=errors,
                skipped_items=duplicates,
            )

            await self.device_repo.update_status(device.id, DeviceStatus.ONLINE.value)

            return True, {
                "sync_id": str(sync.id),
                "created": created,
                "duplicates": duplicates,
                "errors": errors,
            }

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Erro no webhook do dispositivo {device_serial}: {e}")

            await self.sync_repo.fail_sync(sync.id, str(e))
            return False, {"error": str(e)}

    async def retry_failed_sync(self, sync_id: UUID) -> tuple[bool, dict[str, Any]]:
        """Retenta uma sincronização que falhou."""
        sync = await self.sync_repo.get_by_id(sync_id)
        if not sync:
            return False, {"error": "Sincronização não encontrada"}

        if sync.status != SyncStatus.FAILED.value:
            return False, {"error": "Sincronização não está em estado de falha"}

        if not sync.can_retry():
            return False, {"error": "Limite de tentativas excedido"}

        return await self.sync_device_events(
            sync.device_id,
            trigger=SyncTrigger.RECOVERY.value,
            from_nsr=sync.last_nsr_before,
        )

    async def get_sync_progress(self, sync_id: UUID) -> dict[str, Any] | None:
        """Obtém progresso de uma sincronização."""
        sync = await self.sync_repo.get_by_id(sync_id)
        if not sync:
            return None

        elapsed = None
        if sync.started_at:
            elapsed = int((datetime.utcnow() - sync.started_at).total_seconds())

        return {
            "sync_id": str(sync.id),
            "status": sync.status,
            "progress_percent": sync.progress_percent,
            "processed_items": sync.processed_items,
            "total_items": sync.total_items,
            "success_items": sync.success_items,
            "error_items": sync.error_items,
            "elapsed_seconds": elapsed,
            "last_error": sync.error_message,
        }
