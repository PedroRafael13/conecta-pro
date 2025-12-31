"""Repository para Interview."""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.recruitment.models.interview import (
    Interview,
    InterviewType,
    InterviewStatus,
    InterviewResult,
)
from modules.recruitment.schemas.interview import (
    InterviewCreate,
    InterviewUpdate,
    InterviewFilter,
)

logger = logging.getLogger(__name__)


class InterviewRepository:
    """Repository para operações de Interview."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: InterviewCreate) -> Interview:
        """Cria uma nova entrevista."""
        interview = Interview(**data.model_dump())
        self.session.add(interview)
        await self.session.flush()
        return interview

    async def get_by_id(self, interview_id: str) -> Optional[Interview]:
        """Busca entrevista por ID."""
        result = await self.session.execute(
            select(Interview).where(
                and_(
                    Interview.id == interview_id,
                    Interview.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(
        self, interview_id: str
    ) -> Optional[Interview]:
        """Busca entrevista por ID com relacionamentos."""
        result = await self.session.execute(
            select(Interview)
            .options(selectinload(Interview.application))
            .where(
                and_(
                    Interview.id == interview_id,
                    Interview.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self, interview_id: str, data: InterviewUpdate
    ) -> Optional[Interview]:
        """Atualiza uma entrevista."""
        interview = await self.get_by_id(interview_id)
        if not interview:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(interview, field, value)

        await self.session.flush()
        return interview

    async def soft_delete(self, interview_id: str) -> bool:
        """Soft delete de entrevista."""
        interview = await self.get_by_id(interview_id)
        if not interview:
            return False

        interview.soft_delete()
        await self.session.flush()
        return True

    async def list_with_filters(
        self,
        filters: Optional[InterviewFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "scheduled_date",
        order_desc: bool = False,
    ) -> Tuple[List[Interview], int]:
        """Lista entrevistas com filtros e paginação."""
        query = select(Interview).where(Interview.deleted_at.is_(None))

        if filters:
            if filters.application_id:
                query = query.where(Interview.application_id == filters.application_id)
            if filters.interview_type:
                query = query.where(Interview.interview_type == filters.interview_type)
            if filters.status:
                query = query.where(Interview.status == filters.status)
            if filters.result:
                query = query.where(Interview.result == filters.result)
            if filters.interviewer_id:
                query = query.where(
                    Interview.interviewer_ids.contains([filters.interviewer_id])
                )
            if filters.scheduled_after:
                query = query.where(Interview.scheduled_date >= filters.scheduled_after)
            if filters.scheduled_before:
                query = query.where(Interview.scheduled_date <= filters.scheduled_before)
            if filters.is_today:
                query = query.where(Interview.scheduled_date == date.today())
            if filters.is_upcoming:
                upcoming_limit = date.today() + timedelta(days=7)
                query = query.where(
                    and_(
                        Interview.scheduled_date >= date.today(),
                        Interview.scheduled_date <= upcoming_limit,
                    )
                )

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Ordenação
        order_column = getattr(Interview, order_by, Interview.scheduled_date)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Paginação
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        interviews = result.scalars().all()

        return list(interviews), total

    async def get_by_application(
        self, application_id: str, status: InterviewStatus = None
    ) -> List[Interview]:
        """Retorna entrevistas de uma candidatura."""
        query = select(Interview).where(
            and_(
                Interview.application_id == application_id,
                Interview.deleted_at.is_(None),
            )
        )
        if status:
            query = query.where(Interview.status == status)

        query = query.order_by(Interview.scheduled_date, Interview.scheduled_time)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_today(
        self, interviewer_id: str = None
    ) -> List[Interview]:
        """Retorna entrevistas de hoje."""
        query = select(Interview).where(
            and_(
                Interview.scheduled_date == date.today(),
                Interview.status.in_([
                    InterviewStatus.AGENDADA,
                    InterviewStatus.CONFIRMADA,
                    InterviewStatus.EM_ANDAMENTO,
                ]),
                Interview.deleted_at.is_(None),
            )
        )
        if interviewer_id:
            query = query.where(
                Interview.interviewer_ids.contains([interviewer_id])
            )

        query = query.order_by(Interview.scheduled_time)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_upcoming(
        self, days: int = 7, interviewer_id: str = None
    ) -> List[Interview]:
        """Retorna próximas entrevistas."""
        limit_date = date.today() + timedelta(days=days)

        query = select(Interview).where(
            and_(
                Interview.scheduled_date >= date.today(),
                Interview.scheduled_date <= limit_date,
                Interview.status.in_([
                    InterviewStatus.AGENDADA,
                    InterviewStatus.CONFIRMADA,
                ]),
                Interview.deleted_at.is_(None),
            )
        )
        if interviewer_id:
            query = query.where(
                Interview.interviewer_ids.contains([interviewer_id])
            )

        query = query.order_by(Interview.scheduled_date, Interview.scheduled_time)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending_confirmation(self) -> List[Interview]:
        """Retorna entrevistas pendentes de confirmação."""
        tomorrow = date.today() + timedelta(days=1)

        query = (
            select(Interview)
            .where(
                and_(
                    Interview.scheduled_date <= tomorrow,
                    Interview.status == InterviewStatus.AGENDADA,
                    or_(
                        Interview.candidate_confirmed == False,
                        Interview.interviewer_confirmed == False,
                    ),
                    Interview.deleted_at.is_(None),
                )
            )
            .order_by(Interview.scheduled_date, Interview.scheduled_time)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending_result(self) -> List[Interview]:
        """Retorna entrevistas pendentes de resultado."""
        query = (
            select(Interview)
            .where(
                and_(
                    Interview.status == InterviewStatus.REALIZADA,
                    Interview.result.is_(None),
                    Interview.deleted_at.is_(None),
                )
            )
            .order_by(Interview.scheduled_date.desc())
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_date_range(
        self, start_date: date, end_date: date, interviewer_id: str = None
    ) -> List[Interview]:
        """Retorna entrevistas em um período."""
        query = select(Interview).where(
            and_(
                Interview.scheduled_date >= start_date,
                Interview.scheduled_date <= end_date,
                Interview.deleted_at.is_(None),
            )
        )
        if interviewer_id:
            query = query.where(
                Interview.interviewer_ids.contains([interviewer_id])
            )

        query = query.order_by(Interview.scheduled_date, Interview.scheduled_time)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def complete(
        self,
        interview_id: str,
        result: InterviewResult,
        score: int = None,
        feedback: str = None,
    ) -> Optional[Interview]:
        """Completa entrevista."""
        interview = await self.get_by_id(interview_id)
        if interview:
            interview.complete(result, score, feedback)
            await self.session.flush()
        return interview

    async def cancel(
        self, interview_id: str, reason: str, cancelled_by: str
    ) -> Optional[Interview]:
        """Cancela entrevista."""
        interview = await self.get_by_id(interview_id)
        if interview:
            interview.cancel(reason, cancelled_by)
            await self.session.flush()
        return interview

    async def reschedule(
        self, interview_id: str, new_date: date, new_time
    ) -> Optional[Interview]:
        """Reagenda entrevista."""
        interview = await self.get_by_id(interview_id)
        if interview:
            interview.reschedule(new_date, new_time)
            await self.session.flush()
        return interview

    async def mark_no_show(self, interview_id: str) -> Optional[Interview]:
        """Marca como não compareceu."""
        interview = await self.get_by_id(interview_id)
        if interview:
            interview.mark_no_show()
            await self.session.flush()
        return interview

    async def get_stats(self, application_id: str = None) -> dict:
        """Retorna estatísticas."""
        query = select(Interview).where(Interview.deleted_at.is_(None))
        if application_id:
            query = query.where(Interview.application_id == application_id)

        result = await self.session.execute(query)
        interviews = result.scalars().all()

        stats = {
            "total_interviews": len(interviews),
            "scheduled": 0,
            "completed": 0,
            "cancelled": 0,
            "no_show": 0,
            "by_type": {},
            "by_result": {},
            "avg_score": 0,
            "avg_duration_minutes": 0,
            "approval_rate": 0,
        }

        total_score = 0
        score_count = 0
        total_duration = 0
        duration_count = 0
        approved_count = 0
        completed_count = 0

        for interview in interviews:
            if interview.status in [InterviewStatus.AGENDADA, InterviewStatus.CONFIRMADA]:
                stats["scheduled"] += 1
            elif interview.status == InterviewStatus.REALIZADA:
                stats["completed"] += 1
                completed_count += 1
            elif interview.status == InterviewStatus.CANCELADA:
                stats["cancelled"] += 1
            elif interview.status == InterviewStatus.NO_SHOW:
                stats["no_show"] += 1

            type_key = interview.interview_type.value
            stats["by_type"][type_key] = stats["by_type"].get(type_key, 0) + 1

            if interview.result:
                result_key = interview.result.value
                stats["by_result"][result_key] = stats["by_result"].get(result_key, 0) + 1

                if interview.result in [
                    InterviewResult.APROVADO,
                    InterviewResult.APROVADO_COM_RESSALVAS,
                ]:
                    approved_count += 1

            if interview.score:
                total_score += interview.score
                score_count += 1

            if interview.actual_duration_minutes:
                total_duration += interview.actual_duration_minutes
                duration_count += 1

        if score_count > 0:
            stats["avg_score"] = round(total_score / score_count, 1)

        if duration_count > 0:
            stats["avg_duration_minutes"] = round(total_duration / duration_count, 0)

        if completed_count > 0:
            stats["approval_rate"] = round(
                (approved_count / completed_count) * 100, 1
            )

        return stats
