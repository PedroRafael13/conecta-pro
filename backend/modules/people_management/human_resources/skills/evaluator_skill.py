"""Skill IA: Performance Evaluator — Avaliação de desempenho inteligente."""

import logging
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.people_management.human_resources.models.performance import PerformanceReview

logger = logging.getLogger(__name__)


class EvaluatorSkill:
    """Skill IA para análise de avaliações de desempenho."""

    SKILL_NAME = "performance_evaluator"
    DESCRIPTION = "Análise de desempenho com insights e recomendações"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def performance_dashboard(self) -> dict:
        """Dashboard geral de avaliações de desempenho."""
        result = await self.db.execute(
            select(
                PerformanceReview.status,
                func.count(PerformanceReview.id),
                func.avg(PerformanceReview.overall_score),
            ).group_by(PerformanceReview.status)
        )
        rows = result.all()

        by_status = {}
        total_reviews = 0
        scores = []
        for status, count, avg_score in rows:
            by_status[str(status)] = {"count": count, "avg_score": round(float(avg_score or 0), 2)}
            total_reviews += count
            if avg_score:
                scores.append(float(avg_score))

        overall_avg = round(sum(scores) / len(scores), 2) if scores else 0

        return {
            "total_reviews": total_reviews,
            "by_status": by_status,
            "overall_average_score": overall_avg,
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def employee_performance_history(self, employee_id: str) -> dict:
        """Histórico de desempenho de um funcionário."""
        result = await self.db.execute(
            select(PerformanceReview)
            .where(PerformanceReview.employee_id == employee_id)
            .order_by(PerformanceReview.review_date.desc())
        )
        reviews = result.scalars().all()

        history = []
        for r in reviews:
            history.append(
                {
                    "id": str(r.id),
                    "period": r.review_period,
                    "score": float(r.overall_score) if r.overall_score else None,
                    "status": str(r.status),
                    "date": r.review_date.isoformat() if r.review_date else None,
                }
            )

        scores = [h["score"] for h in history if h["score"]]
        trend = "stable"
        if len(scores) >= 2:
            trend = "improving" if scores[0] > scores[-1] else "declining" if scores[0] < scores[-1] else "stable"

        return {
            "employee_id": employee_id,
            "total_reviews": len(history),
            "history": history,
            "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
            "trend": trend,
        }
