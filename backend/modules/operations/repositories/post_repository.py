"""
Repository para operações de banco de dados com Post.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.operations.models.post import Post, PostStatus
from modules.operations.schemas.post import PostCreate, PostFilter, PostStats, PostUpdate


class PostRepository:
    """Repository para operações CRUD de Post."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _generate_code(self) -> str:
        """Gera código único para o posto."""
        result = await self.db.execute(select(func.count(Post.id)))
        count = result.scalar() or 0
        return f"POST-{count + 1:04d}"

    async def create(self, data: PostCreate, created_by: Optional[str] = None) -> Post:
        """
        Cria um novo posto.

        Args:
            data: Dados do posto
            created_by: ID do usuário criador

        Returns:
            Post criado
        """
        code = await self._generate_code()

        post = Post(
            id=str(uuid4()),
            code=code,
            name=data.name,
            description=data.description,
            post_type=data.post_type.value,
            status=PostStatus.ACTIVE.value,
            shift_type=data.shift_type.value,
            contract_id=data.contract_id,
            client_id=data.client_id,
            address=data.address,
            city=data.city,
            state=data.state,
            zip_code=data.zip_code,
            latitude=data.latitude,
            longitude=data.longitude,
            default_start_time=data.default_start_time,
            default_end_time=data.default_end_time,
            break_duration_minutes=data.break_duration_minutes,
            requirements=data.requirements,
            equipment=data.equipment,
            headcount=data.headcount,
            hourly_rate=data.hourly_rate,
            monthly_cost=data.monthly_cost,
            requires_armed=data.requires_armed,
            requires_vehicle=data.requires_vehicle,
            allows_overtime=data.allows_overtime,
            created_by=created_by,
        )

        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)

        logger.info(f"Post criado: {post.id} ({post.code})")
        return post

    async def get_by_id(self, post_id: str) -> Optional[Post]:
        """
        Busca posto por ID.

        Args:
            post_id: ID do posto

        Returns:
            Post ou None
        """
        result = await self.db.execute(
            select(Post).where(Post.id == post_id, Post.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Post]:
        """
        Busca posto por código.

        Args:
            code: Código do posto

        Returns:
            Post ou None
        """
        result = await self.db.execute(
            select(Post).where(Post.code == code, Post.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: Optional[PostFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Post], int]:
        """
        Lista postos com filtros e paginação.

        Args:
            filters: Filtros de busca
            page: Página atual
            page_size: Itens por página

        Returns:
            Tupla (postos, total)
        """
        query = select(Post).where(Post.is_active.is_(True))

        if filters:
            query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(Post.id)).where(Post.is_active.is_(True))
        if filters:
            count_query = self._apply_filters(count_query, filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Post.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        posts = list(result.scalars().all())

        return posts, total

    def _apply_filters(self, query, filters: PostFilter):
        """Aplica filtros à query."""
        if filters.post_type:
            query = query.where(Post.post_type == filters.post_type.value)

        if filters.status:
            query = query.where(Post.status == filters.status.value)

        if filters.shift_type:
            query = query.where(Post.shift_type == filters.shift_type.value)

        if filters.contract_id:
            query = query.where(Post.contract_id == filters.contract_id)

        if filters.client_id:
            query = query.where(Post.client_id == filters.client_id)

        if filters.city:
            query = query.where(Post.city.ilike(f"%{filters.city}%"))

        if filters.state:
            query = query.where(Post.state == filters.state.upper())

        if filters.requires_armed is not None:
            query = query.where(Post.requires_armed == filters.requires_armed)

        if filters.requires_vehicle is not None:
            query = query.where(Post.requires_vehicle == filters.requires_vehicle)

        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Post.name.ilike(search_term),
                    Post.code.ilike(search_term),
                    Post.address.ilike(search_term),
                )
            )

        return query

    async def update(self, post_id: str, data: PostUpdate) -> Optional[Post]:
        """
        Atualiza um posto.

        Args:
            post_id: ID do posto
            data: Dados para atualização

        Returns:
            Post atualizado ou None
        """
        post = await self.get_by_id(post_id)
        if not post:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ("post_type", "status", "shift_type") and value:
                setattr(post, field, value.value)
            else:
                setattr(post, field, value)

        post.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(post)

        logger.info(f"Post atualizado: {post.id}")
        return post

    async def delete(self, post_id: str) -> bool:
        """
        Soft delete de posto.

        Args:
            post_id: ID do posto

        Returns:
            True se deletado
        """
        post = await self.get_by_id(post_id)
        if not post:
            return False

        post.is_active = False
        post.status = PostStatus.INACTIVE.value
        post.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"Post deletado (soft): {post.id}")
        return True

    async def get_by_contract(self, contract_id: str) -> list[Post]:
        """
        Lista postos de um contrato.

        Args:
            contract_id: ID do contrato

        Returns:
            Lista de postos
        """
        result = await self.db.execute(
            select(Post).where(
                Post.contract_id == contract_id,
                Post.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    async def get_by_client(self, client_id: str) -> list[Post]:
        """
        Lista postos de um cliente.

        Args:
            client_id: ID do cliente

        Returns:
            Lista de postos
        """
        result = await self.db.execute(
            select(Post).where(
                Post.client_id == client_id,
                Post.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    async def get_stats(self) -> PostStats:
        """
        Obtém estatísticas de postos.

        Returns:
            Estatísticas
        """
        result = await self.db.execute(select(Post).where(Post.is_active.is_(True)))
        posts = list(result.scalars().all())

        if not posts:
            return PostStats(
                total=0,
                by_status={},
                by_type={},
                by_shift={},
                filled=0,
                with_vacancy=0,
                total_headcount=0,
                total_allocated=0,
                total_monthly_cost=0.0,
            )

        by_status: dict[str, int] = {}
        by_type: dict[str, int] = {}
        by_shift: dict[str, int] = {}
        filled = 0
        with_vacancy = 0
        total_headcount = 0
        total_allocated = 0
        total_monthly_cost = 0.0

        for post in posts:
            by_status[post.status] = by_status.get(post.status, 0) + 1
            by_type[post.post_type] = by_type.get(post.post_type, 0) + 1
            by_shift[post.shift_type] = by_shift.get(post.shift_type, 0) + 1

            total_headcount += post.headcount
            total_monthly_cost += post.monthly_cost

            if post.is_filled:
                filled += 1
            if post.vacancy_count > 0:
                with_vacancy += 1

            active_allocations = [a for a in post.allocations if a.is_active]
            total_allocated += len(active_allocations)

        return PostStats(
            total=len(posts),
            by_status=by_status,
            by_type=by_type,
            by_shift=by_shift,
            filled=filled,
            with_vacancy=with_vacancy,
            total_headcount=total_headcount,
            total_allocated=total_allocated,
            total_monthly_cost=total_monthly_cost,
        )
