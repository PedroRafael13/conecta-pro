"""Service para Occurrence."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.occurrences.models.occurrence import OccurrenceStatus
from modules.occurrences.repositories.category_repository import CategoryRepository
from modules.occurrences.repositories.occurrence_repository import OccurrenceRepository
from modules.occurrences.schemas.occurrence import (
    OccurrenceAssign,
    OccurrenceCreate,
    OccurrenceEscalate,
    OccurrenceFilter,
    OccurrenceListResponse,
    OccurrenceRate,
    OccurrenceResolve,
    OccurrenceResponse,
    OccurrenceStats,
    OccurrenceUpdate,
)

logger = logging.getLogger(__name__)


class OccurrenceService:
    """Service para operações de Occurrence."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = OccurrenceRepository(session)
        self.category_repository = CategoryRepository(session)

    async def create(self, data: OccurrenceCreate) -> OccurrenceResponse:
        """Cria uma nova ocorrência."""
        # Se tem categoria, aplica SLA padrão
        if data.category_id:
            category_info = await self.category_repository.get_with_sla(data.category_id)
            if category_info:
                if not data.sla_response_hours and category_info.get("sla_response_hours"):
                    data.sla_response_hours = category_info["sla_response_hours"]
                if not data.sla_resolution_hours and category_info.get("sla_resolution_hours"):
                    data.sla_resolution_hours = category_info["sla_resolution_hours"]

        occurrence = await self.repository.create(data)

        # Aplica SLA se definido
        if data.sla_response_hours or data.sla_resolution_hours:
            occurrence.set_sla(
                data.sla_response_hours or 24,
                data.sla_resolution_hours or 72,
            )

        # Incrementa contador da categoria
        if data.category_id:
            await self.category_repository.increment_occurrence_count(data.category_id)

        await self.session.commit()
        await self.session.refresh(occurrence)
        return OccurrenceResponse.model_validate(occurrence)

    async def get_by_id(
        self, occurrence_id: str | UUID, include_relations: bool = False
    ) -> Optional[OccurrenceResponse]:
        """Busca ocorrência por ID."""
        occurrence = await self.repository.get_by_id(occurrence_id, include_relations)
        if not occurrence:
            return None
        return OccurrenceResponse.model_validate(occurrence)

    async def get_by_code(self, code: str) -> Optional[OccurrenceResponse]:
        """Busca ocorrência por código."""
        occurrence = await self.repository.get_by_code(code)
        if not occurrence:
            return None
        return OccurrenceResponse.model_validate(occurrence)

    async def update(
        self, occurrence_id: str | UUID, data: OccurrenceUpdate
    ) -> Optional[OccurrenceResponse]:
        """Atualiza uma ocorrência."""
        occurrence = await self.repository.update(occurrence_id, data)
        if not occurrence:
            return None
        await self.session.commit()
        return OccurrenceResponse.model_validate(occurrence)

    async def delete(self, occurrence_id: str | UUID) -> bool:
        """Deleta uma ocorrência."""
        result = await self.repository.delete(occurrence_id)
        if result:
            await self.session.commit()
        return result

    async def list(
        self,
        filters: Optional[OccurrenceFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> OccurrenceListResponse:
        """Lista ocorrências com filtros."""
        skip = (page - 1) * page_size
        occurrences, total = await self.repository.list_with_filters(
            filters, skip, page_size, order_by, order_desc
        )

        items = [OccurrenceResponse.model_validate(occ) for occ in occurrences]
        pages = (total + page_size - 1) // page_size

        return OccurrenceListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def get_open(self, page: int = 1, page_size: int = 20) -> OccurrenceListResponse:
        """Lista ocorrências abertas."""
        skip = (page - 1) * page_size
        occurrences = await self.repository.get_open(skip, page_size)
        items = [OccurrenceResponse.model_validate(occ) for occ in occurrences]
        return OccurrenceListResponse(items=items, total=len(items), page=page, page_size=page_size)

    async def get_overdue(self, page: int = 1, page_size: int = 20) -> OccurrenceListResponse:
        """Lista ocorrências atrasadas."""
        skip = (page - 1) * page_size
        occurrences = await self.repository.get_overdue(skip, page_size)
        items = [OccurrenceResponse.model_validate(occ) for occ in occurrences]
        return OccurrenceListResponse(items=items, total=len(items), page=page, page_size=page_size)

    async def get_escalated(self, page: int = 1, page_size: int = 20) -> OccurrenceListResponse:
        """Lista ocorrências escalonadas."""
        skip = (page - 1) * page_size
        occurrences = await self.repository.get_escalated(skip, page_size)
        items = [OccurrenceResponse.model_validate(occ) for occ in occurrences]
        return OccurrenceListResponse(items=items, total=len(items), page=page, page_size=page_size)

    async def get_high_priority(self, page: int = 1, page_size: int = 20) -> OccurrenceListResponse:
        """Lista ocorrências de alta prioridade."""
        skip = (page - 1) * page_size
        occurrences = await self.repository.get_high_priority(skip, page_size)
        items = [OccurrenceResponse.model_validate(occ) for occ in occurrences]
        return OccurrenceListResponse(items=items, total=len(items), page=page, page_size=page_size)

    async def get_unassigned(self, page: int = 1, page_size: int = 20) -> OccurrenceListResponse:
        """Lista ocorrências não atribuídas."""
        skip = (page - 1) * page_size
        occurrences = await self.repository.get_unassigned(skip, page_size)
        items = [OccurrenceResponse.model_validate(occ) for occ in occurrences]
        return OccurrenceListResponse(items=items, total=len(items), page=page, page_size=page_size)

    async def get_by_condominium(
        self, condominium_id: str, page: int = 1, page_size: int = 20
    ) -> OccurrenceListResponse:
        """Lista ocorrências por condomínio."""
        skip = (page - 1) * page_size
        occurrences = await self.repository.get_by_condominium(condominium_id, skip, page_size)
        items = [OccurrenceResponse.model_validate(occ) for occ in occurrences]
        return OccurrenceListResponse(items=items, total=len(items), page=page, page_size=page_size)

    async def get_by_reporter(
        self, reporter_id: str, page: int = 1, page_size: int = 20
    ) -> OccurrenceListResponse:
        """Lista ocorrências por reportador."""
        skip = (page - 1) * page_size
        occurrences = await self.repository.get_by_reporter(reporter_id, skip, page_size)
        items = [OccurrenceResponse.model_validate(occ) for occ in occurrences]
        return OccurrenceListResponse(items=items, total=len(items), page=page, page_size=page_size)

    async def get_by_assigned(
        self, assigned_to_id: str, page: int = 1, page_size: int = 20
    ) -> OccurrenceListResponse:
        """Lista ocorrências por responsável."""
        skip = (page - 1) * page_size
        occurrences = await self.repository.get_by_assigned(assigned_to_id, skip, page_size)
        items = [OccurrenceResponse.model_validate(occ) for occ in occurrences]
        return OccurrenceListResponse(items=items, total=len(items), page=page, page_size=page_size)

    async def get_stats(
        self, condominium_id: Optional[str] = None, date_from: Optional[datetime] = None
    ) -> OccurrenceStats:
        """Retorna estatísticas."""
        stats = await self.repository.get_stats(condominium_id, date_from)
        return OccurrenceStats(**stats)

    async def assign(
        self, occurrence_id: str | UUID, data: OccurrenceAssign
    ) -> Optional[OccurrenceResponse]:
        """Atribui responsável."""
        occurrence = await self.repository.assign(
            occurrence_id,
            data.assigned_to_id,
            data.assigned_to_name,
            data.assigned_by_id,
            data.assigned_by_name,
        )
        if not occurrence:
            return None
        await self.session.commit()
        return OccurrenceResponse.model_validate(occurrence)

    async def unassign(self, occurrence_id: str | UUID) -> Optional[OccurrenceResponse]:
        """Remove atribuição."""
        occurrence = await self.repository.get_by_id(occurrence_id)
        if not occurrence:
            return None
        occurrence.unassign()
        await self.session.commit()
        return OccurrenceResponse.model_validate(occurrence)

    async def resolve(
        self, occurrence_id: str | UUID, data: OccurrenceResolve
    ) -> Optional[OccurrenceResponse]:
        """Resolve a ocorrência."""
        occurrence = await self.repository.resolve(
            occurrence_id,
            data.resolved_by_id,
            data.resolved_by_name,
            data.resolution_description,
            data.resolution_type,
        )
        if not occurrence:
            return None

        # Atualiza média de resolução da categoria
        if occurrence.category_id and occurrence.resolution_time_hours:
            await self.category_repository.update_avg_resolution(
                occurrence.category_id, occurrence.resolution_time_hours
            )

        await self.session.commit()
        return OccurrenceResponse.model_validate(occurrence)

    async def escalate(
        self, occurrence_id: str | UUID, data: OccurrenceEscalate
    ) -> Optional[OccurrenceResponse]:
        """Escalona a ocorrência."""
        occurrence = await self.repository.escalate(
            occurrence_id,
            data.escalated_to_id,
            data.escalated_to_name,
            data.reason,
        )
        if not occurrence:
            return None
        await self.session.commit()
        return OccurrenceResponse.model_validate(occurrence)

    async def change_status(
        self, occurrence_id: str | UUID, new_status: OccurrenceStatus, reason: str = None
    ) -> Optional[OccurrenceResponse]:
        """Altera status."""
        occurrence = await self.repository.change_status(occurrence_id, new_status, reason)
        if not occurrence:
            return None
        await self.session.commit()
        return OccurrenceResponse.model_validate(occurrence)

    async def reopen(
        self, occurrence_id: str | UUID, reason: str = None, reopened_by: str = None
    ) -> Optional[OccurrenceResponse]:
        """Reabre a ocorrência."""
        occurrence = await self.repository.get_by_id(occurrence_id)
        if not occurrence:
            return None
        occurrence.reopen(reason, reopened_by)
        await self.session.commit()
        return OccurrenceResponse.model_validate(occurrence)

    async def cancel(
        self, occurrence_id: str | UUID, reason: str = None, cancelled_by: str = None
    ) -> Optional[OccurrenceResponse]:
        """Cancela a ocorrência."""
        occurrence = await self.repository.get_by_id(occurrence_id)
        if not occurrence:
            return None
        occurrence.cancel(reason, cancelled_by)
        await self.session.commit()
        return OccurrenceResponse.model_validate(occurrence)

    async def archive(
        self, occurrence_id: str | UUID, reason: str = None
    ) -> Optional[OccurrenceResponse]:
        """Arquiva a ocorrência."""
        occurrence = await self.repository.get_by_id(occurrence_id)
        if not occurrence:
            return None
        occurrence.archive(reason)
        await self.session.commit()
        return OccurrenceResponse.model_validate(occurrence)

    async def rate(
        self, occurrence_id: str | UUID, data: OccurrenceRate
    ) -> Optional[OccurrenceResponse]:
        """Avalia a ocorrência."""
        occurrence = await self.repository.rate(occurrence_id, data.rating, data.comment)
        if not occurrence:
            return None
        await self.session.commit()
        return OccurrenceResponse.model_validate(occurrence)

    async def increment_views(self, occurrence_id: str | UUID) -> None:
        """Incrementa visualizações."""
        await self.repository.increment_views(occurrence_id)
        await self.session.commit()

    async def register_first_response(self, occurrence_id: str | UUID) -> Optional[OccurrenceResponse]:
        """Registra primeira resposta."""
        occurrence = await self.repository.get_by_id(occurrence_id)
        if not occurrence:
            return None
        occurrence.register_first_response()
        await self.session.commit()
        return OccurrenceResponse.model_validate(occurrence)
