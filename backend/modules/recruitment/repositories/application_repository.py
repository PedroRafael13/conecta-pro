"""Repository para Application."""

import logging
from datetime import datetime
from typing import Optional, List, Tuple

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.recruitment.models.application import (
    Application,
    ApplicationStatus,
    RejectionReason,
)
from modules.recruitment.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationFilter,
)

logger = logging.getLogger(__name__)


class ApplicationRepository:
    """Repository para operações de Application."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: ApplicationCreate) -> Application:
        """Cria uma nova candidatura."""
        application = Application(**data.model_dump())
        self.session.add(application)
        await self.session.flush()
        return application

    async def get_by_id(self, application_id: str) -> Optional[Application]:
        """Busca candidatura por ID."""
        result = await self.session.execute(
            select(Application).where(
                and_(
                    Application.id == application_id,
                    Application.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(
        self, application_id: str
    ) -> Optional[Application]:
        """Busca candidatura por ID com relacionamentos."""
        result = await self.session.execute(
            select(Application)
            .options(
                selectinload(Application.job_position),
                selectinload(Application.candidate),
                selectinload(Application.interviews),
            )
            .where(
                and_(
                    Application.id == application_id,
                    Application.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_candidate_and_position(
        self, candidate_id: str, position_id: str
    ) -> Optional[Application]:
        """Busca candidatura por candidato e vaga."""
        result = await self.session.execute(
            select(Application).where(
                and_(
                    Application.candidate_id == candidate_id,
                    Application.job_position_id == position_id,
                    Application.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self, application_id: str, data: ApplicationUpdate
    ) -> Optional[Application]:
        """Atualiza uma candidatura."""
        application = await self.get_by_id(application_id)
        if not application:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(application, field, value)

        application.last_update_at = datetime.utcnow()
        await self.session.flush()
        return application

    async def soft_delete(self, application_id: str) -> bool:
        """Soft delete de candidatura."""
        application = await self.get_by_id(application_id)
        if not application:
            return False

        application.soft_delete()
        await self.session.flush()
        return True

    async def list_with_filters(
        self,
        filters: Optional[ApplicationFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "applied_at",
        order_desc: bool = True,
    ) -> Tuple[List[Application], int]:
        """Lista candidaturas com filtros e paginação."""
        query = select(Application).where(Application.deleted_at.is_(None))

        if filters:
            if filters.job_position_id:
                query = query.where(
                    Application.job_position_id == filters.job_position_id
                )
            if filters.candidate_id:
                query = query.where(Application.candidate_id == filters.candidate_id)
            if filters.status:
                query = query.where(Application.status == filters.status)
            if filters.is_favorite is not None:
                query = query.where(Application.is_favorite == filters.is_favorite)
            if filters.is_shortlisted is not None:
                query = query.where(Application.is_shortlisted == filters.is_shortlisted)
            if filters.min_score:
                query = query.where(Application.final_score >= filters.min_score)
            if filters.max_score:
                query = query.where(Application.final_score <= filters.max_score)
            if filters.assigned_recruiter_id:
                query = query.where(
                    Application.assigned_recruiter_id == filters.assigned_recruiter_id
                )
            if filters.applied_after:
                query = query.where(Application.applied_at >= filters.applied_after)
            if filters.applied_before:
                query = query.where(Application.applied_at <= filters.applied_before)

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Ordenação
        order_column = getattr(Application, order_by, Application.applied_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Paginação
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        applications = result.scalars().all()

        return list(applications), total

    async def get_by_position(
        self,
        position_id: str,
        status: ApplicationStatus = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Application]:
        """Retorna candidaturas de uma vaga."""
        query = select(Application).where(
            and_(
                Application.job_position_id == position_id,
                Application.deleted_at.is_(None),
            )
        )
        if status:
            query = query.where(Application.status == status)

        query = query.order_by(
            Application.is_favorite.desc(),
            Application.final_score.desc().nulls_last(),
            Application.applied_at.desc(),
        )
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_candidate(
        self, candidate_id: str, skip: int = 0, limit: int = 50
    ) -> List[Application]:
        """Retorna candidaturas de um candidato."""
        query = (
            select(Application)
            .where(
                and_(
                    Application.candidate_id == candidate_id,
                    Application.deleted_at.is_(None),
                )
            )
            .order_by(Application.applied_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active(
        self, position_id: str = None, skip: int = 0, limit: int = 50
    ) -> List[Application]:
        """Retorna candidaturas ativas."""
        inactive_statuses = [
            ApplicationStatus.TRIAGEM_REPROVADO,
            ApplicationStatus.PROPOSTA_RECUSADA,
            ApplicationStatus.CONTRATADO,
            ApplicationStatus.REPROVADO,
            ApplicationStatus.DESISTIU,
        ]

        query = select(Application).where(
            and_(
                Application.status.notin_(inactive_statuses),
                Application.deleted_at.is_(None),
            )
        )
        if position_id:
            query = query.where(Application.job_position_id == position_id)

        query = query.order_by(Application.applied_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_shortlisted(
        self, position_id: str, skip: int = 0, limit: int = 50
    ) -> List[Application]:
        """Retorna candidaturas na lista restrita."""
        query = (
            select(Application)
            .where(
                and_(
                    Application.job_position_id == position_id,
                    Application.is_shortlisted == True,
                    Application.deleted_at.is_(None),
                )
            )
            .order_by(Application.final_score.desc().nulls_last())
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_favorites(
        self, position_id: str = None, skip: int = 0, limit: int = 50
    ) -> List[Application]:
        """Retorna candidaturas favoritas."""
        query = select(Application).where(
            and_(
                Application.is_favorite == True,
                Application.deleted_at.is_(None),
            )
        )
        if position_id:
            query = query.where(Application.job_position_id == position_id)

        query = query.order_by(Application.applied_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def advance_stage(
        self,
        application_id: str,
        new_status: ApplicationStatus,
        notes: str = None,
    ) -> Optional[Application]:
        """Avança candidatura de estágio."""
        application = await self.get_by_id(application_id)
        if application:
            application.advance_stage(new_status, notes)
            await self.session.flush()
        return application

    async def reject(
        self,
        application_id: str,
        reason: RejectionReason,
        details: str = None,
        rejected_by: str = None,
    ) -> Optional[Application]:
        """Rejeita candidatura."""
        application = await self.get_by_id(application_id)
        if application:
            application.reject(reason, details, rejected_by)
            await self.session.flush()
        return application

    async def hire(
        self, application_id: str, start_date: datetime = None
    ) -> Optional[Application]:
        """Contrata candidato."""
        application = await self.get_by_id(application_id)
        if application:
            application.hire(start_date)
            await self.session.flush()
        return application

    async def update_ranking(self, position_id: str) -> None:
        """Atualiza ranking das candidaturas."""
        applications = await self.get_active(position_id)

        # Ordena por score final
        sorted_apps = sorted(
            applications,
            key=lambda a: a.final_score or 0,
            reverse=True,
        )

        for rank, app in enumerate(sorted_apps, 1):
            app.ranking_position = rank

        await self.session.flush()

    async def get_stats(self, position_id: str = None) -> dict:
        """Retorna estatísticas."""
        query = select(Application).where(Application.deleted_at.is_(None))
        if position_id:
            query = query.where(Application.job_position_id == position_id)

        result = await self.session.execute(query)
        applications = result.scalars().all()

        stats = {
            "total_applications": len(applications),
            "active_applications": 0,
            "hired": 0,
            "rejected": 0,
            "in_process": 0,
            "by_status": {},
            "by_stage": {},
            "avg_time_to_hire_days": 0,
            "avg_score": 0,
            "conversion_rate": 0,
        }

        total_score = 0
        score_count = 0
        total_hire_days = 0
        hire_count = 0

        in_process_statuses = [
            ApplicationStatus.TRIAGEM,
            ApplicationStatus.ENTREVISTA_RH,
            ApplicationStatus.ENTREVISTA_TECNICA,
            ApplicationStatus.ENTREVISTA_GESTOR,
            ApplicationStatus.TESTE,
            ApplicationStatus.REFERENCIAS,
            ApplicationStatus.PROPOSTA,
        ]

        rejected_statuses = [
            ApplicationStatus.TRIAGEM_REPROVADO,
            ApplicationStatus.REPROVADO,
            ApplicationStatus.PROPOSTA_RECUSADA,
        ]

        for app in applications:
            if app.status not in rejected_statuses and app.status != ApplicationStatus.CONTRATADO:
                stats["active_applications"] += 1

            if app.status == ApplicationStatus.CONTRATADO:
                stats["hired"] += 1
                if app.hired_at:
                    days = (app.hired_at - app.applied_at).days
                    total_hire_days += days
                    hire_count += 1

            if app.status in rejected_statuses:
                stats["rejected"] += 1

            if app.status in in_process_statuses:
                stats["in_process"] += 1

            status_key = app.status.value
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1

            stage_key = str(app.current_stage)
            stats["by_stage"][stage_key] = stats["by_stage"].get(stage_key, 0) + 1

            if app.final_score:
                total_score += app.final_score
                score_count += 1

        if score_count > 0:
            stats["avg_score"] = round(total_score / score_count, 1)

        if hire_count > 0:
            stats["avg_time_to_hire_days"] = round(total_hire_days / hire_count, 1)

        if applications:
            stats["conversion_rate"] = round(
                (stats["hired"] / len(applications)) * 100, 1
            )

        return stats
