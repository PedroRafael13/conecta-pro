"""
Repository para relatorios operacionais.
"""

from datetime import date
from typing import Dict, List, Optional

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.allocation import Allocation, AllocationStatus
from modules.operacional.models.post import Post
from modules.operacional.models.shift import Shift


class ReportsRepository:
    """Repository de relatorios para o modulo operacional."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_coverage(
        self,
        start_date: date,
        end_date: date,
        post_id: Optional[str] = None,
    ) -> List[Dict]:
        """Retorna cobertura por posto (alocacoes)."""
        posts_query = select(Post.id, Post.name).where(Post.is_active.is_(True))
        if post_id:
            posts_query = posts_query.where(Post.id == post_id)

        posts_result = await self.db.execute(posts_query)
        posts = list(posts_result.all())

        alloc_query = (
            select(
                Allocation.post_id,
                func.count(Allocation.id).label("total_allocations"),
                func.sum(
                    case(
                        (Allocation.status == AllocationStatus.ACTIVE.value, 1),
                        else_=0,
                    )
                ).label("active_allocations"),
            )
            .where(Allocation.is_active.is_(True))
            .where(Allocation.start_date <= end_date)
            .where(or_(Allocation.end_date.is_(None), Allocation.end_date >= start_date))
            .group_by(Allocation.post_id)
        )

        if post_id:
            alloc_query = alloc_query.where(Allocation.post_id == post_id)

        alloc_result = await self.db.execute(alloc_query)
        alloc_map = {
            row.post_id: {
                "total_allocations": int(row.total_allocations or 0),
                "active_allocations": int(row.active_allocations or 0),
            }
            for row in alloc_result.all()
        }

        items: List[Dict] = []
        for post in posts:
            counts = alloc_map.get(post.id, {"total_allocations": 0, "active_allocations": 0})
            total_allocations = counts["total_allocations"]
            active_allocations = counts["active_allocations"]
            coverage_rate = (active_allocations / total_allocations * 100) if total_allocations else 0.0
            items.append(
                {
                    "post_id": str(post.id),
                    "post_name": post.name,
                    "total_allocations": total_allocations,
                    "active_allocations": active_allocations,
                    "coverage_rate": round(coverage_rate, 2),
                }
            )

        return items

    async def get_hours(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[str] = None,
    ) -> List[Dict]:
        """Retorna horas trabalhadas por funcionario."""
        query = (
            select(
                Shift.employee_id,
                func.count(Shift.id).label("total_shifts"),
                func.sum(Shift.actual_hours).label("total_hours"),
                func.sum(Shift.overtime_hours).label("overtime_hours"),
            )
            .where(Shift.is_active.is_(True))
            .where(Shift.employee_id.isnot(None))
            .where(Shift.shift_date >= start_date)
            .where(Shift.shift_date <= end_date)
            .group_by(Shift.employee_id)
        )

        if employee_id:
            query = query.where(Shift.employee_id == employee_id)

        result = await self.db.execute(query)
        items = []
        for row in result.all():
            items.append(
                {
                    "employee_id": str(row.employee_id),
                    "total_shifts": int(row.total_shifts or 0),
                    "total_hours": float(row.total_hours or 0.0),
                    "overtime_hours": float(row.overtime_hours or 0.0),
                }
            )
        return items

    async def get_costs(
        self,
        start_date: date,
        end_date: date,
        post_id: Optional[str] = None,
    ) -> List[Dict]:
        """Retorna custos estimados por posto."""
        query = (
            select(
                Shift.post_id,
                func.count(Shift.id).label("total_shifts"),
                func.sum(Shift.total_pay).label("total_cost"),
            )
            .where(Shift.is_active.is_(True))
            .where(Shift.shift_date >= start_date)
            .where(Shift.shift_date <= end_date)
            .group_by(Shift.post_id)
        )

        if post_id:
            query = query.where(Shift.post_id == post_id)

        result = await self.db.execute(query)
        raw_items = list(result.all())

        post_ids = [row.post_id for row in raw_items]
        post_names: Dict[str, str] = {}
        if post_ids:
            posts_result = await self.db.execute(
                select(Post.id, Post.name).where(Post.id.in_(post_ids))
            )
            post_names = {str(row.id): row.name for row in posts_result.all()}

        items: List[Dict] = []
        for row in raw_items:
            items.append(
                {
                    "post_id": str(row.post_id),
                    "post_name": post_names.get(str(row.post_id), "Posto"),
                    "total_shifts": int(row.total_shifts or 0),
                    "total_cost": float(row.total_cost or 0.0),
                }
            )
        return items
