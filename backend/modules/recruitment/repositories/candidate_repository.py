"""Repository para Candidate."""

import logging
from datetime import datetime, timedelta

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.recruitment.models.candidate import (
    Candidate,
    CandidateSource,
    CandidateStatus,
)
from modules.recruitment.schemas.candidate import (
    CandidateCreate,
    CandidateFilter,
    CandidateUpdate,
)

logger = logging.getLogger(__name__)


class CandidateRepository:
    """Repository para operações de Candidate."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: CandidateCreate) -> Candidate:
        """Cria um novo candidato."""
        candidate = Candidate(**data.model_dump())
        candidate.update_profile_score()
        self.session.add(candidate)
        await self.session.flush()
        return candidate

    async def get_by_id(self, candidate_id: str) -> Candidate | None:
        """Busca candidato por ID."""
        result = await self.session.execute(
            select(Candidate).where(
                and_(
                    Candidate.id == candidate_id,
                    Candidate.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(self, candidate_id: str) -> Candidate | None:
        """Busca candidato por ID com relacionamentos."""
        result = await self.session.execute(
            select(Candidate)
            .options(
                selectinload(Candidate.skills),
                selectinload(Candidate.experiences),
                selectinload(Candidate.educations),
            )
            .where(
                and_(
                    Candidate.id == candidate_id,
                    Candidate.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Candidate | None:
        """Busca candidato por email."""
        result = await self.session.execute(
            select(Candidate).where(
                and_(
                    Candidate.email == email,
                    Candidate.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> Candidate | None:
        """Busca candidato por CPF."""
        result = await self.session.execute(
            select(Candidate).where(
                and_(
                    Candidate.cpf == cpf,
                    Candidate.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(self, candidate_id: str, data: CandidateUpdate) -> Candidate | None:
        """Atualiza um candidato."""
        candidate = await self.get_by_id(candidate_id)
        if not candidate:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(candidate, field, value)

        candidate.update_profile_score()
        candidate.record_activity()
        await self.session.flush()
        return candidate

    async def soft_delete(self, candidate_id: str) -> bool:
        """Soft delete de candidato."""
        candidate = await self.get_by_id(candidate_id)
        if not candidate:
            return False

        candidate.soft_delete()
        await self.session.flush()
        return True

    async def list_with_filters(  # pylint: disable=too-many-branches
        self,
        filters: CandidateFilter | None = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[Candidate], int]:
        """Lista candidatos com filtros e paginação."""
        query = select(Candidate).where(Candidate.deleted_at.is_(None))

        if filters:
            if filters.status:
                query = query.where(Candidate.status == filters.status)
            if filters.source:
                query = query.where(Candidate.source == filters.source)
            if filters.city:
                query = query.where(Candidate.city.ilike(f"%{filters.city}%"))
            if filters.state:
                query = query.where(Candidate.state == filters.state)
            if filters.available_immediately is not None:
                query = query.where(Candidate.available_immediately == filters.available_immediately)
            if filters.has_cnh is not None:
                query = query.where(Candidate.has_cnh == filters.has_cnh)
            if filters.is_pcd is not None:
                query = query.where(Candidate.is_pcd == filters.is_pcd)
            if filters.is_blocked is not None:
                query = query.where(Candidate.is_blocked == filters.is_blocked)
            if filters.salary_min:
                query = query.where(Candidate.salary_expectation >= filters.salary_min)
            if filters.salary_max:
                query = query.where(Candidate.salary_expectation <= filters.salary_max)
            if filters.condominium_id:
                query = query.where(Candidate.condominium_id == filters.condominium_id)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(
                    or_(
                        Candidate.name.ilike(search_term),
                        Candidate.email.ilike(search_term),
                        Candidate.headline.ilike(search_term),
                        Candidate.phone.ilike(search_term),
                    )
                )

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Ordenação
        order_column = getattr(Candidate, order_by, Candidate.created_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Paginação
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        candidates = result.scalars().all()

        return list(candidates), total

    async def get_active(self, condominium_id: str = None, skip: int = 0, limit: int = 50) -> list[Candidate]:
        """Retorna candidatos ativos."""
        query = select(Candidate).where(
            and_(
                Candidate.status == CandidateStatus.ATIVO,
                Candidate.is_blocked.is_(False),
                Candidate.deleted_at.is_(None),
            )
        )
        if condominium_id:
            query = query.where(Candidate.condominium_id == condominium_id)

        query = query.order_by(Candidate.profile_score.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_source(self, source: CandidateSource, skip: int = 0, limit: int = 50) -> list[Candidate]:
        """Retorna candidatos por fonte."""
        query = (
            select(Candidate)
            .where(
                and_(
                    Candidate.source == source,
                    Candidate.deleted_at.is_(None),
                )
            )
            .order_by(Candidate.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_blocked(self, skip: int = 0, limit: int = 50) -> list[Candidate]:
        """Retorna candidatos bloqueados."""
        query = (
            select(Candidate)
            .where(
                and_(
                    Candidate.is_blocked.is_(True),
                    Candidate.deleted_at.is_(None),
                )
            )
            .order_by(Candidate.blocked_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search_by_skills(self, skills: list[str], limit: int = 50) -> list[Candidate]:
        """Busca candidatos por habilidades."""
        # Busca simples por tags
        query = (
            select(Candidate)
            .where(
                and_(
                    Candidate.status == CandidateStatus.ATIVO,
                    Candidate.deleted_at.is_(None),
                )
            )
            .order_by(Candidate.profile_score.desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        candidates = result.scalars().all()

        # Filtra por skills nas tags ou resume
        filtered = []
        for candidate in candidates:
            candidate_skills = set(candidate.tags or [])
            resume_lower = (candidate.resume_text or "").lower()

            for skill in skills:
                skill_lower = skill.lower()
                if skill_lower in candidate_skills or skill_lower in resume_lower:
                    filtered.append(candidate)
                    break

        return filtered

    async def get_recently_active(self, days: int = 30, limit: int = 50) -> list[Candidate]:
        """Retorna candidatos ativos recentemente."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        query = (
            select(Candidate)
            .where(
                and_(
                    Candidate.last_activity_at >= cutoff,
                    Candidate.status == CandidateStatus.ATIVO,
                    Candidate.deleted_at.is_(None),
                )
            )
            .order_by(Candidate.last_activity_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def block(self, candidate_id: str, reason: str, blocked_by: str) -> Candidate | None:
        """Bloqueia candidato."""
        candidate = await self.get_by_id(candidate_id)
        if candidate:
            candidate.block(reason, blocked_by)
            await self.session.flush()
        return candidate

    async def unblock(self, candidate_id: str) -> Candidate | None:
        """Desbloqueia candidato."""
        candidate = await self.get_by_id(candidate_id)
        if candidate:
            candidate.unblock()
            await self.session.flush()
        return candidate

    async def mark_as_hired(self, candidate_id: str) -> Candidate | None:
        """Marca como contratado."""
        candidate = await self.get_by_id(candidate_id)
        if candidate:
            candidate.mark_as_hired()
            await self.session.flush()
        return candidate

    async def get_stats(self, condominium_id: str = None) -> dict:
        """Retorna estatísticas."""
        query = select(Candidate).where(Candidate.deleted_at.is_(None))
        if condominium_id:
            query = query.where(Candidate.condominium_id == condominium_id)

        result = await self.session.execute(query)
        candidates = result.scalars().all()

        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        stats = {
            "total_candidates": len(candidates),
            "active_candidates": 0,
            "blocked_candidates": 0,
            "hired_candidates": 0,
            "by_status": {},
            "by_source": {},
            "by_city": {},
            "avg_profile_score": 0,
            "avg_applications": 0,
            "new_this_month": 0,
            "new_this_week": 0,
        }

        total_score = 0
        total_apps = 0

        for cand in candidates:
            if cand.status == CandidateStatus.ATIVO:
                stats["active_candidates"] += 1
            if cand.is_blocked:
                stats["blocked_candidates"] += 1
            if cand.status == CandidateStatus.CONTRATADO:
                stats["hired_candidates"] += 1

            status_key = cand.status.value
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1

            source_key = cand.source.value
            stats["by_source"][source_key] = stats["by_source"].get(source_key, 0) + 1

            if cand.city:
                stats["by_city"][cand.city] = stats["by_city"].get(cand.city, 0) + 1

            total_score += cand.profile_score
            total_apps += cand.applications_count

            if cand.created_at >= month_ago:
                stats["new_this_month"] += 1
            if cand.created_at >= week_ago:
                stats["new_this_week"] += 1

        if candidates:
            stats["avg_profile_score"] = round(total_score / len(candidates), 1)
            stats["avg_applications"] = round(total_apps / len(candidates), 1)

        return stats
