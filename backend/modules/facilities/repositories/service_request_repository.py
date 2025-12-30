"""
Repository para operações de banco de dados com ServiceRequest.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.facilities.models.service_request import (
    ServiceRequest,
    ServiceRequestCategory,
    ServiceRequestPriority,
    ServiceRequestStatus,
)
from modules.facilities.schemas.service_request import (
    ServiceRequestCreate,
    ServiceRequestFilter,
    ServiceRequestStats,
    ServiceRequestUpdate,
)


class ServiceRequestRepository:
    """Repository para operações CRUD de ServiceRequest."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _generate_code(self) -> str:
        """Gera código único para solicitação."""
        result = await self.db.execute(
            select(func.count(ServiceRequest.id)).where(
                ServiceRequest.is_active.is_(True)
            )
        )
        count = result.scalar() or 0
        return f"SR-{count + 1:06d}"

    async def create(
        self,
        data: ServiceRequestCreate,
        created_by: Optional[str] = None,
    ) -> ServiceRequest:
        """Cria uma nova solicitação de serviço."""
        code = data.code or await self._generate_code()

        service_request = ServiceRequest(
            id=str(uuid4()),
            code=code,
            title=data.title,
            description=data.description,
            category=data.category.value,
            status=ServiceRequestStatus.OPEN.value,
            priority=data.priority.value,
            area_id=data.area_id,
            client_id=data.client_id,
            condominium_id=data.condominium_id,
            requester_id=data.requester_id,
            requester_name=data.requester_name,
            requester_unit=data.requester_unit,
            requester_contact=data.requester_contact,
            requester_email=data.requester_email,
            location_details=data.location_details,
            floor=data.floor,
            building=data.building,
            scheduled_date=data.scheduled_date,
            photos=data.photos,
            notes=data.notes,
            status_history=[
                {
                    "status": ServiceRequestStatus.OPEN.value,
                    "timestamp": datetime.now().isoformat(),
                    "user_id": created_by,
                }
            ],
            created_by=created_by,
        )

        self.db.add(service_request)
        await self.db.commit()
        await self.db.refresh(service_request)

        logger.info(f"ServiceRequest criada: {service_request.id} - {service_request.code}")
        return service_request

    async def get_by_id(self, request_id: str) -> Optional[ServiceRequest]:
        """Busca solicitação por ID."""
        result = await self.db.execute(
            select(ServiceRequest).where(
                ServiceRequest.id == request_id,
                ServiceRequest.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[ServiceRequest]:
        """Busca solicitação por código."""
        result = await self.db.execute(
            select(ServiceRequest).where(
                ServiceRequest.code == code.upper(),
                ServiceRequest.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: Optional[ServiceRequestFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[ServiceRequest], int]:
        """Lista solicitações com filtros e paginação."""
        query = select(ServiceRequest).where(ServiceRequest.is_active.is_(True))

        if filters:
            query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(ServiceRequest.id)).where(
            ServiceRequest.is_active.is_(True)
        )
        if filters:
            count_query = self._apply_filters(count_query, filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(ServiceRequest.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        requests = list(result.scalars().all())

        return requests, total

    def _apply_filters(self, query, filters: ServiceRequestFilter):
        """Aplica filtros à query."""
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    ServiceRequest.title.ilike(search_term),
                    ServiceRequest.code.ilike(search_term),
                    ServiceRequest.description.ilike(search_term),
                )
            )

        if filters.category:
            query = query.where(ServiceRequest.category == filters.category.value)

        if filters.status:
            query = query.where(ServiceRequest.status == filters.status.value)

        if filters.priority:
            query = query.where(ServiceRequest.priority == filters.priority.value)

        if filters.area_id:
            query = query.where(ServiceRequest.area_id == filters.area_id)

        if filters.client_id:
            query = query.where(ServiceRequest.client_id == filters.client_id)

        if filters.condominium_id:
            query = query.where(ServiceRequest.condominium_id == filters.condominium_id)

        if filters.requester_id:
            query = query.where(ServiceRequest.requester_id == filters.requester_id)

        if filters.assigned_to:
            query = query.where(ServiceRequest.assigned_to == filters.assigned_to)

        if filters.created_start:
            query = query.where(
                ServiceRequest.created_at >= datetime.combine(
                    filters.created_start,
                    datetime.min.time(),
                )
            )

        if filters.created_end:
            query = query.where(
                ServiceRequest.created_at <= datetime.combine(
                    filters.created_end,
                    datetime.max.time(),
                )
            )

        if filters.deadline_start:
            query = query.where(ServiceRequest.deadline >= filters.deadline_start)

        if filters.deadline_end:
            query = query.where(ServiceRequest.deadline <= filters.deadline_end)

        if filters.is_overdue:
            today = date.today()
            query = query.where(
                and_(
                    ServiceRequest.deadline.isnot(None),
                    ServiceRequest.deadline < today,
                    ServiceRequest.status.notin_(
                        [
                            ServiceRequestStatus.COMPLETED.value,
                            ServiceRequestStatus.CLOSED.value,
                            ServiceRequestStatus.CANCELLED.value,
                        ]
                    ),
                )
            )

        if filters.has_sla_breach is not None:
            query = query.where(ServiceRequest.sla_breached == filters.has_sla_breach)

        if filters.has_feedback:
            query = query.where(ServiceRequest.satisfaction_rating.isnot(None))

        if filters.min_rating is not None:
            query = query.where(ServiceRequest.satisfaction_rating >= filters.min_rating)

        return query

    async def update(
        self,
        request_id: str,
        data: ServiceRequestUpdate,
    ) -> Optional[ServiceRequest]:
        """Atualiza uma solicitação."""
        service_request = await self.get_by_id(request_id)
        if not service_request:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ("category", "status", "priority") and value:
                setattr(service_request, field, value.value)
            else:
                setattr(service_request, field, value)

        service_request.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(service_request)

        logger.info(f"ServiceRequest atualizada: {service_request.id}")
        return service_request

    async def acknowledge(
        self,
        request_id: str,
        acknowledged_by: str,
        notes: Optional[str] = None,
    ) -> Optional[ServiceRequest]:
        """Reconhece/recebe uma solicitação."""
        service_request = await self.get_by_id(request_id)
        if not service_request:
            return None

        service_request.status = ServiceRequestStatus.ACKNOWLEDGED.value
        service_request.acknowledged_by = acknowledged_by
        service_request.acknowledged_at = datetime.utcnow()
        service_request.response_time_hours = service_request.calculate_response_time()
        if notes:
            current_notes = service_request.internal_notes or ""
            service_request.internal_notes = f"{current_notes}\n[Reconhecimento] {notes}".strip()

        service_request.add_status_history(
            ServiceRequestStatus.ACKNOWLEDGED.value,
            acknowledged_by,
        )
        service_request.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(service_request)

        logger.info(f"ServiceRequest reconhecida: {service_request.id}")
        return service_request

    async def assign(
        self,
        request_id: str,
        assigned_to: str,
        assigned_by: str,
        **kwargs,
    ) -> Optional[ServiceRequest]:
        """Atribui responsável a uma solicitação."""
        service_request = await self.get_by_id(request_id)
        if not service_request:
            return None

        service_request.assigned_to = assigned_to
        service_request.status = ServiceRequestStatus.IN_ANALYSIS.value

        for field, value in kwargs.items():
            if hasattr(service_request, field):
                setattr(service_request, field, value)

        service_request.add_status_history(
            ServiceRequestStatus.IN_ANALYSIS.value,
            assigned_by,
        )
        service_request.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(service_request)

        logger.info(f"ServiceRequest atribuída: {service_request.id} -> {assigned_to}")
        return service_request

    async def start(
        self,
        request_id: str,
        started_by: str,
    ) -> Optional[ServiceRequest]:
        """Inicia o atendimento de uma solicitação."""
        service_request = await self.get_by_id(request_id)
        if not service_request:
            return None

        service_request.status = ServiceRequestStatus.IN_PROGRESS.value
        service_request.started_at = datetime.utcnow()

        service_request.add_status_history(
            ServiceRequestStatus.IN_PROGRESS.value,
            started_by,
        )
        service_request.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(service_request)

        logger.info(f"ServiceRequest iniciada: {service_request.id}")
        return service_request

    async def complete(
        self,
        request_id: str,
        completed_by: str,
        resolution: str,
        **kwargs,
    ) -> Optional[ServiceRequest]:
        """Conclui uma solicitação."""
        service_request = await self.get_by_id(request_id)
        if not service_request:
            return None

        service_request.status = ServiceRequestStatus.COMPLETED.value
        service_request.completed_at = datetime.utcnow()
        service_request.resolution = resolution
        service_request.resolution_time_hours = service_request.calculate_resolution_time()

        for field, value in kwargs.items():
            if hasattr(service_request, field):
                setattr(service_request, field, value)

        service_request.add_status_history(
            ServiceRequestStatus.COMPLETED.value,
            completed_by,
        )
        service_request.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(service_request)

        logger.info(f"ServiceRequest concluída: {service_request.id}")
        return service_request

    async def reject(
        self,
        request_id: str,
        rejected_by: str,
        rejection_reason: str,
    ) -> Optional[ServiceRequest]:
        """Rejeita uma solicitação."""
        service_request = await self.get_by_id(request_id)
        if not service_request:
            return None

        service_request.status = ServiceRequestStatus.REJECTED.value
        service_request.rejection_reason = rejection_reason

        service_request.add_status_history(
            ServiceRequestStatus.REJECTED.value,
            rejected_by,
        )
        service_request.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(service_request)

        logger.info(f"ServiceRequest rejeitada: {service_request.id}")
        return service_request

    async def cancel(
        self,
        request_id: str,
        cancelled_by: str,
        cancellation_reason: str,
    ) -> Optional[ServiceRequest]:
        """Cancela uma solicitação."""
        service_request = await self.get_by_id(request_id)
        if not service_request:
            return None

        service_request.status = ServiceRequestStatus.CANCELLED.value
        service_request.cancellation_reason = cancellation_reason

        service_request.add_status_history(
            ServiceRequestStatus.CANCELLED.value,
            cancelled_by,
        )
        service_request.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(service_request)

        logger.info(f"ServiceRequest cancelada: {service_request.id}")
        return service_request

    async def add_feedback(
        self,
        request_id: str,
        rating: int,
        feedback: Optional[str] = None,
    ) -> Optional[ServiceRequest]:
        """Adiciona avaliação do solicitante."""
        service_request = await self.get_by_id(request_id)
        if not service_request:
            return None

        service_request.satisfaction_rating = rating
        service_request.feedback = feedback
        service_request.feedback_at = datetime.utcnow()
        service_request.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(service_request)

        logger.info(f"Feedback adicionado: {service_request.id} - {rating}/5")
        return service_request

    async def delete(self, request_id: str) -> bool:
        """Soft delete de solicitação."""
        service_request = await self.get_by_id(request_id)
        if not service_request:
            return False

        service_request.is_active = False
        service_request.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"ServiceRequest deletada (soft): {service_request.id}")
        return True

    async def get_stats(
        self,
        client_id: Optional[str] = None,
        condominium_id: Optional[str] = None,
    ) -> ServiceRequestStats:
        """Obtém estatísticas de solicitações."""
        base_filter = [ServiceRequest.is_active.is_(True)]
        if client_id:
            base_filter.append(ServiceRequest.client_id == client_id)
        if condominium_id:
            base_filter.append(ServiceRequest.condominium_id == condominium_id)

        # Total
        total_result = await self.db.execute(
            select(func.count(ServiceRequest.id)).where(and_(*base_filter))
        )
        total = total_result.scalar() or 0

        # Por categoria
        by_category: Dict[str, int] = {}
        for cat in ServiceRequestCategory:
            cat_result = await self.db.execute(
                select(func.count(ServiceRequest.id)).where(
                    and_(*base_filter, ServiceRequest.category == cat.value)
                )
            )
            count = cat_result.scalar() or 0
            if count > 0:
                by_category[cat.value] = count

        # Por status
        by_status: Dict[str, int] = {}
        for status in ServiceRequestStatus:
            status_result = await self.db.execute(
                select(func.count(ServiceRequest.id)).where(
                    and_(*base_filter, ServiceRequest.status == status.value)
                )
            )
            count = status_result.scalar() or 0
            if count > 0:
                by_status[status.value] = count

        # Por prioridade
        by_priority: Dict[str, int] = {}
        for priority in ServiceRequestPriority:
            priority_result = await self.db.execute(
                select(func.count(ServiceRequest.id)).where(
                    and_(*base_filter, ServiceRequest.priority == priority.value)
                )
            )
            count = priority_result.scalar() or 0
            if count > 0:
                by_priority[priority.value] = count

        # Em aberto
        open_statuses = [
            ServiceRequestStatus.OPEN.value,
            ServiceRequestStatus.ACKNOWLEDGED.value,
            ServiceRequestStatus.IN_ANALYSIS.value,
            ServiceRequestStatus.IN_PROGRESS.value,
        ]
        open_result = await self.db.execute(
            select(func.count(ServiceRequest.id)).where(
                and_(*base_filter, ServiceRequest.status.in_(open_statuses))
            )
        )
        open_count = open_result.scalar() or 0

        # Atrasadas
        today = date.today()
        overdue_result = await self.db.execute(
            select(func.count(ServiceRequest.id)).where(
                and_(
                    *base_filter,
                    ServiceRequest.deadline.isnot(None),
                    ServiceRequest.deadline < today,
                    ServiceRequest.status.in_(open_statuses),
                )
            )
        )
        overdue_count = overdue_result.scalar() or 0

        # SLA violado
        sla_result = await self.db.execute(
            select(func.count(ServiceRequest.id)).where(
                and_(*base_filter, ServiceRequest.sla_breached.is_(True))
            )
        )
        sla_breach_count = sla_result.scalar() or 0

        # Médias
        avg_response_result = await self.db.execute(
            select(func.avg(ServiceRequest.response_time_hours)).where(
                and_(*base_filter, ServiceRequest.response_time_hours.isnot(None))
            )
        )
        avg_response = avg_response_result.scalar()

        avg_resolution_result = await self.db.execute(
            select(func.avg(ServiceRequest.resolution_time_hours)).where(
                and_(*base_filter, ServiceRequest.resolution_time_hours.isnot(None))
            )
        )
        avg_resolution = avg_resolution_result.scalar()

        avg_satisfaction_result = await self.db.execute(
            select(func.avg(ServiceRequest.satisfaction_rating)).where(
                and_(*base_filter, ServiceRequest.satisfaction_rating.isnot(None))
            )
        )
        avg_satisfaction = avg_satisfaction_result.scalar()

        # Custo total
        cost_result = await self.db.execute(
            select(func.sum(ServiceRequest.actual_cost)).where(and_(*base_filter))
        )
        total_cost = cost_result.scalar() or 0.0

        # Este mês
        first_day = today.replace(day=1)

        created_result = await self.db.execute(
            select(func.count(ServiceRequest.id)).where(
                and_(
                    *base_filter,
                    ServiceRequest.created_at >= datetime.combine(
                        first_day,
                        datetime.min.time(),
                    ),
                )
            )
        )
        created_this_month = created_result.scalar() or 0

        completed_result = await self.db.execute(
            select(func.count(ServiceRequest.id)).where(
                and_(
                    *base_filter,
                    ServiceRequest.completed_at >= datetime.combine(
                        first_day,
                        datetime.min.time(),
                    ),
                )
            )
        )
        completed_this_month = completed_result.scalar() or 0

        return ServiceRequestStats(
            total=total,
            by_category=by_category,
            by_status=by_status,
            by_priority=by_priority,
            open_count=open_count,
            overdue_count=overdue_count,
            sla_breach_count=sla_breach_count,
            avg_response_time_hours=float(avg_response) if avg_response else None,
            avg_resolution_time_hours=float(avg_resolution) if avg_resolution else None,
            avg_satisfaction=float(avg_satisfaction) if avg_satisfaction else None,
            total_cost=float(total_cost),
            created_this_month=created_this_month,
            completed_this_month=completed_this_month,
        )
