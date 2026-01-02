"""Serviço de processamento de eventos REP.

Converte eventos brutos em registros de ponto (TimeEntry).
"""

import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.rep_integration.models import (
    REPEvent,
    EventStatus,
    EventType,
)
from modules.hr.rep_integration.repositories import (
    REPEventRepository,
    AFDRecordRepository,
)

logger = logging.getLogger(__name__)


class EventProcessorService:
    """Serviço para processar eventos REP."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_repo = REPEventRepository(db)
        self.afd_repo = AFDRecordRepository(db)

    async def process_pending_events(
        self,
        device_id: UUID = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Processa eventos pendentes.

        Returns:
            Estatísticas do processamento.
        """
        events = await self.event_repo.get_pending_processing(
            device_id=device_id,
            limit=limit,
        )

        results = {
            "total": len(events),
            "processed": 0,
            "errors": 0,
            "skipped": 0,
        }

        for event in events:
            try:
                success = await self.process_event(event)
                if success:
                    results["processed"] += 1
                else:
                    results["skipped"] += 1
            except (ValueError, KeyError, TypeError, RuntimeError) as e:
                logger.error(f"Erro ao processar evento {event.id}: {e}")
                results["errors"] += 1
                await self.event_repo.mark_as_error(
                    event.id,
                    str(e),
                    "PROCESS_ERROR",
                )

        return results

    async def process_event(self, event: REPEvent) -> bool:
        """Processa um evento individual.

        1. Valida evento
        2. Identifica funcionário (se não identificado)
        3. Cria TimeEntry
        4. Cria registro AFD
        5. Atualiza status do evento

        Returns:
            True se processado com sucesso.
        """
        # Validar evento
        validation = await self._validate_event(event)
        if not validation["is_valid"]:
            await self.event_repo.update(
                event.id,
                {"is_valid": False, "validation_errors": validation["errors"]},
            )
            return False

        # Identificar funcionário se necessário
        if not event.employee_id and event.pis_number:
            employee_id = await self._identify_employee(
                event.pis_number,
                event.condominio_id,
            )
            if employee_id:
                event.employee_id = employee_id

        # Se ainda não identificado, marcar para revisão
        if not event.employee_id:
            await self.event_repo.update(
                event.id,
                {"status": EventStatus.VALIDATED.value},
            )
            return False

        # Criar TimeEntry
        time_entry_id = await self._create_time_entry(event)
        if not time_entry_id:
            await self.event_repo.mark_as_error(
                event.id,
                "Falha ao criar registro de ponto",
                "TIME_ENTRY_ERROR",
            )
            return False

        # Criar registro AFD
        await self.afd_repo.create_from_event(
            device_id=event.device_id,
            condominio_id=event.condominio_id,
            nsr=event.nsr,
            record_date=event.event_date,
            record_time=event.event_time,
            pis_number=event.pis_number,
            event_id=event.id,
        )

        # Marcar como processado
        await self.event_repo.mark_as_processed(event.id, time_entry_id)

        logger.info(f"Evento {event.id} processado -> TimeEntry {time_entry_id}")
        return True

    async def _validate_event(self, event: REPEvent) -> Dict[str, Any]:
        """Valida um evento."""
        errors = []

        # Data/hora válida
        if not event.event_datetime:
            errors.append("Data/hora do evento é obrigatória")

        # Data não pode ser futura
        if event.event_datetime and event.event_datetime > datetime.utcnow():
            errors.append("Data do evento não pode ser futura")

        # NSR válido
        if not event.nsr or event.nsr <= 0:
            errors.append("NSR inválido")

        # PIS ou código do funcionário
        if not event.pis_number and not event.employee_code:
            errors.append("PIS ou código do funcionário é obrigatório")

        # Verificar duplicado no mesmo dia
        if event.pis_number and event.event_datetime:
            # TODO: Implementar verificação de duplicados  # pylint: disable=fixme
            pass

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
        }

    async def _identify_employee(
        self,
        pis_number: str,  # pylint: disable=unused-argument
        condominio_id: UUID,  # pylint: disable=unused-argument
    ) -> Optional[UUID]:
        """Identifica funcionário pelo PIS.

        Returns:
            ID do funcionário ou None.
        """
        # TODO: Implementar busca no cadastro de funcionários  # pylint: disable=fixme
        # Por enquanto, retorna None para marcar como não identificado
        return None

    async def _create_time_entry(self, event: REPEvent) -> Optional[UUID]:
        """Cria registro de ponto a partir do evento.

        Returns:
            ID do TimeEntry criado ou None.
        """
        # TODO: Integrar com módulo time_tracking  # pylint: disable=fixme
        # Por enquanto, simula criação
        try:
            # Importar TimeEntry do módulo time_tracking
            # from modules.hr.time_tracking.repositories import TimeEntryRepository
            # from modules.hr.time_tracking.schemas import TimeEntryCreate

            # Mapear tipo de evento (usado quando integrar com time_tracking)
            _entry_type = self._map_event_type(event.event_type)

            # Criar TimeEntry
            # time_entry = await time_entry_repo.create(TimeEntryCreate(...))
            # return time_entry.id

            # Por enquanto, retorna UUID simulado (remover quando integrar)
            import uuid  # pylint: disable=import-outside-toplevel
            _ = _entry_type  # Usado na integração com time_tracking
            return uuid.uuid4()

        except (ValueError, KeyError, TypeError, AttributeError) as e:
            logger.error(f"Erro ao criar TimeEntry: {e}")
            return None

    def _map_event_type(self, rep_event_type: str) -> str:
        """Mapeia tipo de evento REP para tipo de TimeEntry."""
        mapping = {
            EventType.ENTRY.value: "entry",
            EventType.EXIT.value: "exit",
            EventType.BREAK_START.value: "break_start",
            EventType.BREAK_END.value: "break_end",
            EventType.EXTRA_ENTRY.value: "extra_entry",
            EventType.EXTRA_EXIT.value: "extra_exit",
        }
        return mapping.get(rep_event_type, "entry")

    async def link_event_to_employee(
        self,
        event_id: UUID,
        employee_id: UUID,
    ) -> bool:
        """Vincula evento a um funcionário manualmente."""
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            return False

        if event.status == EventStatus.PROCESSED.value:
            return False  # Já processado

        await self.event_repo.update(
            event_id,
            {"employee_id": employee_id, "status": EventStatus.VALIDATED.value},
        )

        # Tentar processar novamente
        return await self.process_event(event)

    async def get_unidentified_events(
        self,
        device_id: UUID = None,
        date_from: date = None,
        date_to: date = None,
        limit: int = 100,
    ) -> List[REPEvent]:
        """Retorna eventos sem funcionário identificado."""
        return await self.event_repo.get_unidentified_events(
            device_id=device_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
        )

    async def bulk_link_events(
        self,
        mappings: List[Dict[str, UUID]],
    ) -> Dict[str, int]:
        """Vincula múltiplos eventos a funcionários.

        Args:
            mappings: Lista de {"event_id": UUID, "employee_id": UUID}

        Returns:
            Estatísticas do processamento.
        """
        results = {"success": 0, "failed": 0}

        for mapping in mappings:
            try:
                success = await self.link_event_to_employee(
                    mapping["event_id"],
                    mapping["employee_id"],
                )
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
            except (ValueError, KeyError, TypeError, RuntimeError):
                results["failed"] += 1

        return results

    async def reprocess_failed_events(
        self,
        device_id: UUID = None,
        limit: int = 50,
    ) -> Dict[str, int]:
        """Reprocessa eventos que falharam."""
        # Buscar eventos com erro que podem ser reprocessados
        # pylint: disable=import-outside-toplevel
        from modules.hr.rep_integration.schemas import REPEventFilter

        filters = REPEventFilter(
            device_id=device_id,
            status=EventStatus.ERROR.value,
        )

        events, _ = await self.event_repo.list_events(filters, page_size=limit)

        results = {"reprocessed": 0, "failed": 0, "skipped": 0}

        for event in events:
            if not event.can_retry:
                results["skipped"] += 1
                continue

            try:
                # Resetar status
                await self.event_repo.update(
                    event.id,
                    {"status": EventStatus.RECEIVED.value},
                )

                success = await self.process_event(event)
                if success:
                    results["reprocessed"] += 1
                else:
                    results["failed"] += 1
            except (ValueError, KeyError, TypeError, RuntimeError):
                results["failed"] += 1

        return results
