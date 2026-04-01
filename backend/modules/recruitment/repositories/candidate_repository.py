"""Repository para Candidate."""

import logging
from datetime import datetime, timedelta

from sqlalchemy import and_, func, or_, select
from sqlalchemy import inspect as sa_inspect
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
        self.session.add(candidate)
        await self.session.flush()
        return candidate

    async def get_by_id(self, candidate_id: str) -> Candidate | None:
        """Busca candidato por ID."""
        result = await self.session.execute(
            select(Candidate).where(
                and_(
                    Candidate.id == candidate_id,
                    Candidate.is_deleted.is_(False),
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
                    Candidate.is_deleted.is_(False),
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
                    Candidate.is_deleted.is_(False),
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
                    Candidate.is_deleted.is_(False),
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
            if hasattr(candidate, field):
                setattr(candidate, field, value)

        candidate.updated_at = datetime.utcnow()
        await self.session.flush()
        return candidate

    async def soft_delete(self, candidate_id: str) -> bool:
        """Soft delete de candidato."""
        candidate = await self.get_by_id(candidate_id)
        if not candidate:
            return False

        candidate.is_deleted = True
        candidate.is_active = False
        candidate.updated_at = datetime.utcnow()
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
        query = select(Candidate).where(Candidate.is_deleted.is_(False))

        if filters:
            if filters.status:
                query = query.where(Candidate.status == filters.status)
            if filters.source:
                query = query.where(Candidate.source == filters.source)
            if filters.city:
                query = query.where(Candidate.city.ilike(f"%{filters.city}%"))
            if filters.state:
                query = query.where(Candidate.state == filters.state)
            # available_immediately, has_cnh, is_pcd, is_blocked, condominium_id
            # don't exist as DB columns — skip these filters silently
            if filters.salary_min:
                query = query.where(Candidate.salary_expectation >= filters.salary_min)
            if filters.salary_max:
                query = query.where(Candidate.salary_expectation <= filters.salary_max)
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
        _valid_order_column_cols = {c.key for c in sa_inspect(Candidate).mapper.column_attrs}
        order_column = getattr(Candidate, order_by if order_by in _valid_order_column_cols else "created_at")
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Paginação
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        candidates = result.scalars().all()

        return list(candidates), total

    async def get_active(self, skip: int = 0, limit: int = 50) -> list[Candidate]:
        """Retorna candidatos ativos."""
        query = select(Candidate).where(
            and_(
                Candidate.status == CandidateStatus.ATIVO,
                Candidate.status != CandidateStatus.BLOQUEADO,
                Candidate.is_deleted.is_(False),
            )
        )

        query = query.order_by(Candidate.ai_score.desc().nulls_last())
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
                    Candidate.is_deleted.is_(False),
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
                    Candidate.status == CandidateStatus.BLOQUEADO,
                    Candidate.is_deleted.is_(False),
                )
            )
            .order_by(Candidate.updated_at.desc().nulls_last())
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
                    Candidate.is_deleted.is_(False),
                )
            )
            .order_by(Candidate.ai_score.desc().nulls_last())
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
                    Candidate.updated_at >= cutoff,
                    Candidate.status == CandidateStatus.ATIVO,
                    Candidate.is_deleted.is_(False),
                )
            )
            .order_by(Candidate.updated_at.desc().nulls_last())
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def block(self, candidate_id: str, reason: str, blocked_by: str) -> Candidate | None:
        """Bloqueia candidato."""
        candidate = await self.get_by_id(candidate_id)
        if candidate:
            candidate.status = CandidateStatus.BLOQUEADO
            candidate.updated_at = datetime.utcnow()
            await self.session.flush()
        return candidate

    async def unblock(self, candidate_id: str) -> Candidate | None:
        """Desbloqueia candidato."""
        candidate = await self.get_by_id(candidate_id)
        if candidate:
            candidate.status = CandidateStatus.ATIVO
            candidate.updated_at = datetime.utcnow()
            await self.session.flush()
        return candidate

    async def mark_as_hired(self, candidate_id: str) -> Candidate | None:
        """Marca como contratado."""
        candidate = await self.get_by_id(candidate_id)
        if candidate:
            candidate.status = CandidateStatus.CONTRATADO
            candidate.updated_at = datetime.utcnow()
            await self.session.flush()
        return candidate

    async def get_stats(self) -> dict:
        """Retorna estatísticas."""
        query = select(Candidate).where(Candidate.is_deleted.is_(False))

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
        score_count = 0

        for cand in candidates:
            if cand.status == CandidateStatus.ATIVO:
                stats["active_candidates"] += 1
            if cand.status == CandidateStatus.BLOQUEADO:
                stats["blocked_candidates"] += 1
            if cand.status == CandidateStatus.CONTRATADO:
                stats["hired_candidates"] += 1

            status_key = cand.status or "unknown"
            if hasattr(status_key, "value"):
                status_key = status_key.value
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1

            source_key = cand.source or "unknown"
            if hasattr(source_key, "value"):
                source_key = source_key.value
            stats["by_source"][source_key] = stats["by_source"].get(source_key, 0) + 1

            if cand.city:
                stats["by_city"][cand.city] = stats["by_city"].get(cand.city, 0) + 1

            if cand.ai_score is not None:
                total_score += float(cand.ai_score)
                score_count += 1

            if cand.created_at and cand.created_at >= month_ago:
                stats["new_this_month"] += 1
            if cand.created_at and cand.created_at >= week_ago:
                stats["new_this_week"] += 1

        if score_count > 0:
            stats["avg_profile_score"] = round(total_score / score_count, 1)

        return stats
