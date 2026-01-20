"""
Sentiment Analysis Repository - Sprint 46

Repository para operacoes de banco de dados do modulo de sentimento.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, update, delete, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.ai.sentiment_analysis.models import (
    SentimentAnalysis,
    SentimentType,
    SourceType,
    AnalysisStatus,
    SentimentRule,
    RuleCategory,
    SentimentTrend,
    TrendPeriod,
    TrendDirection,
    FeedbackInsight,
    InsightType,
    InsightPriority,
)
from modules.ai.sentiment_analysis.models.feedback_insight import InsightStatus

logger = logging.getLogger(__name__)


class SentimentRepository:
    """Repository para operacoes de sentimento."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ============================================================
    # Sentiment Analysis CRUD
    # ============================================================

    async def create_analysis(
        self,
        analysis: SentimentAnalysis,
    ) -> SentimentAnalysis:
        """Cria nova analise."""
        self.session.add(analysis)
        await self.session.commit()
        await self.session.refresh(analysis)
        logger.info(f"Analise criada: {analysis.id}")
        return analysis

    async def get_analysis(
        self,
        analysis_id: UUID,
    ) -> Optional[SentimentAnalysis]:
        """Busca analise por ID."""
        result = await self.session.execute(
            select(SentimentAnalysis).where(SentimentAnalysis.id == analysis_id)
        )
        return result.scalar_one_or_none()

    async def update_analysis(
        self,
        analysis_id: UUID,
        **kwargs,
    ) -> Optional[SentimentAnalysis]:
        """Atualiza analise."""
        analysis = await self.get_analysis(analysis_id)
        if not analysis:
            return None

        for key, value in kwargs.items():
            if hasattr(analysis, key):
                setattr(analysis, key, value)

        await self.session.commit()
        await self.session.refresh(analysis)
        return analysis

    async def delete_analysis(self, analysis_id: UUID) -> bool:
        """Remove analise."""
        result = await self.session.execute(
            delete(SentimentAnalysis).where(SentimentAnalysis.id == analysis_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def list_analyses(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 50,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> Tuple[List[SentimentAnalysis], int]:
        """Lista analises com filtros e paginacao."""
        query = select(SentimentAnalysis)

        if filters:
            conditions = []

            if "sentiment_types" in filters and filters["sentiment_types"]:
                conditions.append(
                    SentimentAnalysis.sentiment_type.in_(filters["sentiment_types"])
                )

            if "source_types" in filters and filters["source_types"]:
                conditions.append(
                    SentimentAnalysis.source_type.in_(filters["source_types"])
                )

            if "customer_id" in filters and filters["customer_id"]:
                conditions.append(
                    SentimentAnalysis.customer_id == filters["customer_id"]
                )

            if "entity_type" in filters and filters["entity_type"]:
                conditions.append(
                    SentimentAnalysis.entity_type == filters["entity_type"]
                )

            if "entity_id" in filters and filters["entity_id"]:
                conditions.append(SentimentAnalysis.entity_id == filters["entity_id"])

            if "min_score" in filters and filters["min_score"] is not None:
                conditions.append(
                    SentimentAnalysis.sentiment_score >= filters["min_score"]
                )

            if "max_score" in filters and filters["max_score"] is not None:
                conditions.append(
                    SentimentAnalysis.sentiment_score <= filters["max_score"]
                )

            if "has_urgency" in filters and filters["has_urgency"] is not None:
                conditions.append(
                    SentimentAnalysis.has_urgency == filters["has_urgency"]
                )

            if "has_complaint" in filters and filters["has_complaint"] is not None:
                conditions.append(
                    SentimentAnalysis.has_complaint == filters["has_complaint"]
                )

            if (
                "has_intent_to_leave" in filters
                and filters["has_intent_to_leave"] is not None
            ):
                conditions.append(
                    SentimentAnalysis.has_intent_to_leave
                    == filters["has_intent_to_leave"]
                )

            if "requires_action" in filters and filters["requires_action"] is not None:
                conditions.append(
                    SentimentAnalysis.requires_action == filters["requires_action"]
                )

            if "is_reviewed" in filters and filters["is_reviewed"] is not None:
                conditions.append(
                    SentimentAnalysis.is_reviewed == filters["is_reviewed"]
                )

            if "date_from" in filters and filters["date_from"]:
                conditions.append(SentimentAnalysis.created_at >= filters["date_from"])

            if "date_to" in filters and filters["date_to"]:
                conditions.append(SentimentAnalysis.created_at <= filters["date_to"])

            if conditions:
                query = query.where(and_(*conditions))

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        # Order
        order_column = getattr(SentimentAnalysis, order_by, SentimentAnalysis.created_at)
        if order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_analyses_by_customer(
        self,
        customer_id: UUID,
        limit: int = 100,
    ) -> List[SentimentAnalysis]:
        """Busca analises de um cliente."""
        result = await self.session.execute(
            select(SentimentAnalysis)
            .where(SentimentAnalysis.customer_id == customer_id)
            .order_by(desc(SentimentAnalysis.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_critical_analyses(
        self,
        hours: int = 24,
        limit: int = 50,
    ) -> List[SentimentAnalysis]:
        """Busca analises criticas recentes."""
        since = datetime.utcnow() - timedelta(hours=hours)

        result = await self.session.execute(
            select(SentimentAnalysis)
            .where(
                and_(
                    SentimentAnalysis.created_at >= since,
                    or_(
                        SentimentAnalysis.sentiment_type == SentimentType.VERY_NEGATIVE,
                        SentimentAnalysis.has_intent_to_leave == True,
                        SentimentAnalysis.urgency_level >= 8,
                    ),
                )
            )
            .order_by(desc(SentimentAnalysis.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_analysis_stats(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Retorna estatisticas de analises."""
        conditions = []
        if date_from:
            conditions.append(SentimentAnalysis.created_at >= date_from)
        if date_to:
            conditions.append(SentimentAnalysis.created_at <= date_to)

        where_clause = and_(*conditions) if conditions else True

        # Total e media
        result = await self.session.execute(
            select(
                func.count(SentimentAnalysis.id).label("total"),
                func.avg(SentimentAnalysis.sentiment_score).label("avg_score"),
                func.avg(SentimentAnalysis.confidence_score).label("avg_confidence"),
            ).where(where_clause)
        )
        row = result.one()

        # Por tipo de sentimento
        sentiment_result = await self.session.execute(
            select(
                SentimentAnalysis.sentiment_type,
                func.count(SentimentAnalysis.id).label("count"),
            )
            .where(where_clause)
            .group_by(SentimentAnalysis.sentiment_type)
        )
        sentiment_counts = {r[0].value: r[1] for r in sentiment_result.all()}

        # Indicadores
        indicators_result = await self.session.execute(
            select(
                func.sum(
                    func.cast(SentimentAnalysis.has_urgency, Integer)
                ).label("urgency_count"),
                func.sum(
                    func.cast(SentimentAnalysis.has_complaint, Integer)
                ).label("complaint_count"),
                func.sum(
                    func.cast(SentimentAnalysis.has_intent_to_leave, Integer)
                ).label("churn_risk_count"),
                func.sum(
                    func.cast(SentimentAnalysis.requires_action, Integer)
                ).label("action_required_count"),
            ).where(where_clause)
        )
        indicators = indicators_result.one()

        return {
            "total": row.total or 0,
            "avg_score": round(row.avg_score or 0, 2),
            "avg_confidence": round(row.avg_confidence or 0, 2),
            "sentiment_distribution": sentiment_counts,
            "urgency_count": indicators.urgency_count or 0,
            "complaint_count": indicators.complaint_count or 0,
            "churn_risk_count": indicators.churn_risk_count or 0,
            "action_required_count": indicators.action_required_count or 0,
        }

    # ============================================================
    # Sentiment Rule CRUD
    # ============================================================

    async def create_rule(self, rule: SentimentRule) -> SentimentRule:
        """Cria nova regra."""
        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        logger.info(f"Regra criada: {rule.code}")
        return rule

    async def get_rule(self, rule_id: UUID) -> Optional[SentimentRule]:
        """Busca regra por ID."""
        result = await self.session.execute(
            select(SentimentRule).where(SentimentRule.id == rule_id)
        )
        return result.scalar_one_or_none()

    async def get_rule_by_code(self, code: str) -> Optional[SentimentRule]:
        """Busca regra por codigo."""
        result = await self.session.execute(
            select(SentimentRule).where(SentimentRule.code == code)
        )
        return result.scalar_one_or_none()

    async def update_rule(
        self,
        rule_id: UUID,
        **kwargs,
    ) -> Optional[SentimentRule]:
        """Atualiza regra."""
        rule = await self.get_rule(rule_id)
        if not rule:
            return None

        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)

        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def delete_rule(self, rule_id: UUID) -> bool:
        """Remove regra."""
        result = await self.session.execute(
            delete(SentimentRule).where(
                and_(
                    SentimentRule.id == rule_id,
                    SentimentRule.is_system == False,
                )
            )
        )
        await self.session.commit()
        return result.rowcount > 0

    async def list_rules(
        self,
        category: Optional[RuleCategory] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[SentimentRule], int]:
        """Lista regras."""
        query = select(SentimentRule)

        conditions = []
        if category:
            conditions.append(SentimentRule.category == category)
        if is_active is not None:
            conditions.append(SentimentRule.is_active == is_active)

        if conditions:
            query = query.where(and_(*conditions))

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        # Order by priority
        query = query.order_by(desc(SentimentRule.priority))

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_active_rules(
        self,
        source_type: Optional[SourceType] = None,
    ) -> List[SentimentRule]:
        """Busca regras ativas."""
        query = select(SentimentRule).where(SentimentRule.is_active == True)

        if source_type:
            # Filtra regras que se aplicam a esta fonte
            query = query.where(
                or_(
                    SentimentRule.source_types == [],
                    func.json_contains(
                        SentimentRule.source_types,
                        f'"{source_type.value}"',
                    ),
                )
            )

        query = query.order_by(desc(SentimentRule.priority))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def increment_rule_trigger(self, rule_id: UUID) -> None:
        """Incrementa contador de trigger."""
        await self.session.execute(
            update(SentimentRule)
            .where(SentimentRule.id == rule_id)
            .values(
                total_triggers=SentimentRule.total_triggers + 1,
                last_triggered_at=datetime.utcnow(),
            )
        )
        await self.session.commit()

    # ============================================================
    # Sentiment Trend CRUD
    # ============================================================

    async def create_trend(self, trend: SentimentTrend) -> SentimentTrend:
        """Cria nova tendencia."""
        self.session.add(trend)
        await self.session.commit()
        await self.session.refresh(trend)
        return trend

    async def get_trend(self, trend_id: UUID) -> Optional[SentimentTrend]:
        """Busca tendencia por ID."""
        result = await self.session.execute(
            select(SentimentTrend).where(SentimentTrend.id == trend_id)
        )
        return result.scalar_one_or_none()

    async def get_trend_by_period(
        self,
        period_type: TrendPeriod,
        period_label: str,
        category: Optional[str] = None,
        category_value: Optional[str] = None,
    ) -> Optional[SentimentTrend]:
        """Busca tendencia por periodo."""
        query = select(SentimentTrend).where(
            and_(
                SentimentTrend.period_type == period_type,
                SentimentTrend.period_label == period_label,
            )
        )

        if category:
            query = query.where(SentimentTrend.category == category)
        if category_value:
            query = query.where(SentimentTrend.category_value == category_value)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_trend(
        self,
        trend_id: UUID,
        **kwargs,
    ) -> Optional[SentimentTrend]:
        """Atualiza tendencia."""
        trend = await self.get_trend(trend_id)
        if not trend:
            return None

        for key, value in kwargs.items():
            if hasattr(trend, key):
                setattr(trend, key, value)

        await self.session.commit()
        await self.session.refresh(trend)
        return trend

    async def list_trends(
        self,
        period_type: Optional[TrendPeriod] = None,
        category: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SentimentTrend]:
        """Lista tendencias."""
        query = select(SentimentTrend)

        conditions = []
        if period_type:
            conditions.append(SentimentTrend.period_type == period_type)
        if category:
            conditions.append(SentimentTrend.category == category)
        if entity_type:
            conditions.append(SentimentTrend.entity_type == entity_type)
        if entity_id:
            conditions.append(SentimentTrend.entity_id == entity_id)
        if date_from:
            conditions.append(SentimentTrend.period_start >= date_from)
        if date_to:
            conditions.append(SentimentTrend.period_end <= date_to)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(desc(SentimentTrend.period_start)).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_latest_trend(
        self,
        period_type: TrendPeriod,
        category: Optional[str] = None,
    ) -> Optional[SentimentTrend]:
        """Busca tendencia mais recente."""
        query = select(SentimentTrend).where(
            SentimentTrend.period_type == period_type
        )

        if category:
            query = query.where(SentimentTrend.category == category)

        query = query.order_by(desc(SentimentTrend.period_start)).limit(1)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    # ============================================================
    # Feedback Insight CRUD
    # ============================================================

    async def create_insight(self, insight: FeedbackInsight) -> FeedbackInsight:
        """Cria novo insight."""
        self.session.add(insight)
        await self.session.commit()
        await self.session.refresh(insight)
        logger.info(f"Insight criado: {insight.insight_number}")
        return insight

    async def get_insight(self, insight_id: UUID) -> Optional[FeedbackInsight]:
        """Busca insight por ID."""
        result = await self.session.execute(
            select(FeedbackInsight).where(FeedbackInsight.id == insight_id)
        )
        return result.scalar_one_or_none()

    async def get_insight_by_number(
        self,
        number: str,
    ) -> Optional[FeedbackInsight]:
        """Busca insight por numero."""
        result = await self.session.execute(
            select(FeedbackInsight).where(FeedbackInsight.insight_number == number)
        )
        return result.scalar_one_or_none()

    async def update_insight(
        self,
        insight_id: UUID,
        **kwargs,
    ) -> Optional[FeedbackInsight]:
        """Atualiza insight."""
        insight = await self.get_insight(insight_id)
        if not insight:
            return None

        for key, value in kwargs.items():
            if hasattr(insight, key):
                setattr(insight, key, value)

        await self.session.commit()
        await self.session.refresh(insight)
        return insight

    async def delete_insight(self, insight_id: UUID) -> bool:
        """Remove insight."""
        result = await self.session.execute(
            delete(FeedbackInsight).where(FeedbackInsight.id == insight_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def list_insights(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 50,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> Tuple[List[FeedbackInsight], int]:
        """Lista insights com filtros."""
        query = select(FeedbackInsight)

        if filters:
            conditions = []

            if "insight_types" in filters and filters["insight_types"]:
                conditions.append(
                    FeedbackInsight.insight_type.in_(filters["insight_types"])
                )

            if "priorities" in filters and filters["priorities"]:
                conditions.append(
                    FeedbackInsight.priority.in_(filters["priorities"])
                )

            if "statuses" in filters and filters["statuses"]:
                conditions.append(FeedbackInsight.status.in_(filters["statuses"]))

            if "category" in filters and filters["category"]:
                conditions.append(FeedbackInsight.category == filters["category"])

            if "entity_type" in filters and filters["entity_type"]:
                conditions.append(
                    FeedbackInsight.entity_type == filters["entity_type"]
                )

            if "entity_id" in filters and filters["entity_id"]:
                conditions.append(FeedbackInsight.entity_id == filters["entity_id"])

            if (
                "min_impact_score" in filters
                and filters["min_impact_score"] is not None
            ):
                conditions.append(
                    FeedbackInsight.impact_score >= filters["min_impact_score"]
                )

            if (
                "min_urgency_score" in filters
                and filters["min_urgency_score"] is not None
            ):
                conditions.append(
                    FeedbackInsight.urgency_score >= filters["min_urgency_score"]
                )

            if "assigned_to" in filters and filters["assigned_to"]:
                conditions.append(
                    FeedbackInsight.assigned_to == filters["assigned_to"]
                )

            if "assigned_team" in filters and filters["assigned_team"]:
                conditions.append(
                    FeedbackInsight.assigned_team == filters["assigned_team"]
                )

            if "date_from" in filters and filters["date_from"]:
                conditions.append(FeedbackInsight.created_at >= filters["date_from"])

            if "date_to" in filters and filters["date_to"]:
                conditions.append(FeedbackInsight.created_at <= filters["date_to"])

            if conditions:
                query = query.where(and_(*conditions))

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        # Order
        order_column = getattr(FeedbackInsight, order_by, FeedbackInsight.created_at)
        if order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_active_insights(
        self,
        limit: int = 50,
    ) -> List[FeedbackInsight]:
        """Busca insights ativos."""
        result = await self.session.execute(
            select(FeedbackInsight)
            .where(
                FeedbackInsight.status.in_([
                    InsightStatus.NEW,
                    InsightStatus.ACKNOWLEDGED,
                    InsightStatus.IN_PROGRESS,
                ])
            )
            .order_by(
                desc(FeedbackInsight.priority),
                desc(FeedbackInsight.urgency_score),
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_critical_insights(self, limit: int = 20) -> List[FeedbackInsight]:
        """Busca insights criticos."""
        result = await self.session.execute(
            select(FeedbackInsight)
            .where(
                and_(
                    FeedbackInsight.priority == InsightPriority.CRITICAL,
                    FeedbackInsight.status.in_([
                        InsightStatus.NEW,
                        InsightStatus.ACKNOWLEDGED,
                    ]),
                )
            )
            .order_by(desc(FeedbackInsight.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_insight_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas de insights."""
        # Por status
        status_result = await self.session.execute(
            select(
                FeedbackInsight.status,
                func.count(FeedbackInsight.id).label("count"),
            ).group_by(FeedbackInsight.status)
        )
        status_counts = {r[0].value: r[1] for r in status_result.all()}

        # Por prioridade (ativos)
        priority_result = await self.session.execute(
            select(
                FeedbackInsight.priority,
                func.count(FeedbackInsight.id).label("count"),
            )
            .where(
                FeedbackInsight.status.in_([
                    InsightStatus.NEW,
                    InsightStatus.ACKNOWLEDGED,
                    InsightStatus.IN_PROGRESS,
                ])
            )
            .group_by(FeedbackInsight.priority)
        )
        priority_counts = {r[0].value: r[1] for r in priority_result.all()}

        # Por tipo (ativos)
        type_result = await self.session.execute(
            select(
                FeedbackInsight.insight_type,
                func.count(FeedbackInsight.id).label("count"),
            )
            .where(
                FeedbackInsight.status.in_([
                    InsightStatus.NEW,
                    InsightStatus.ACKNOWLEDGED,
                    InsightStatus.IN_PROGRESS,
                ])
            )
            .group_by(FeedbackInsight.insight_type)
        )
        type_counts = {r[0].value: r[1] for r in type_result.all()}

        return {
            "by_status": status_counts,
            "by_priority": priority_counts,
            "by_type": type_counts,
            "total_active": sum(
                status_counts.get(s, 0)
                for s in ["new", "acknowledged", "in_progress"]
            ),
            "total_critical": priority_counts.get("critical", 0),
        }

    # ============================================================
    # Aggregation Methods
    # ============================================================

    async def aggregate_sentiment_by_period(
        self,
        period_start: datetime,
        period_end: datetime,
        group_by: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Agrega sentimento por periodo."""
        query = select(
            func.count(SentimentAnalysis.id).label("count"),
            func.avg(SentimentAnalysis.sentiment_score).label("avg_score"),
            func.min(SentimentAnalysis.sentiment_score).label("min_score"),
            func.max(SentimentAnalysis.sentiment_score).label("max_score"),
            func.sum(
                func.cast(
                    SentimentAnalysis.sentiment_type == SentimentType.VERY_POSITIVE,
                    Integer,
                )
            ).label("very_positive"),
            func.sum(
                func.cast(
                    SentimentAnalysis.sentiment_type == SentimentType.POSITIVE,
                    Integer,
                )
            ).label("positive"),
            func.sum(
                func.cast(
                    SentimentAnalysis.sentiment_type == SentimentType.NEUTRAL,
                    Integer,
                )
            ).label("neutral"),
            func.sum(
                func.cast(
                    SentimentAnalysis.sentiment_type == SentimentType.NEGATIVE,
                    Integer,
                )
            ).label("negative"),
            func.sum(
                func.cast(
                    SentimentAnalysis.sentiment_type == SentimentType.VERY_NEGATIVE,
                    Integer,
                )
            ).label("very_negative"),
        ).where(
            and_(
                SentimentAnalysis.created_at >= period_start,
                SentimentAnalysis.created_at <= period_end,
                SentimentAnalysis.status == AnalysisStatus.COMPLETED,
            )
        )

        if group_by:
            group_column = getattr(SentimentAnalysis, group_by, None)
            if group_column:
                query = query.add_columns(group_column.label("group_value"))
                query = query.group_by(group_column)

        result = await self.session.execute(query)
        rows = result.all()

        aggregations = []
        for row in rows:
            agg = {
                "count": row.count or 0,
                "avg_score": round(row.avg_score or 0, 2),
                "min_score": row.min_score,
                "max_score": row.max_score,
                "very_positive": row.very_positive or 0,
                "positive": row.positive or 0,
                "neutral": row.neutral or 0,
                "negative": row.negative or 0,
                "very_negative": row.very_negative or 0,
            }
            if group_by and hasattr(row, "group_value"):
                agg["group_value"] = row.group_value
            aggregations.append(agg)

        return aggregations

    async def get_top_keywords(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Busca keywords mais frequentes."""
        conditions = [SentimentAnalysis.status == AnalysisStatus.COMPLETED]
        if date_from:
            conditions.append(SentimentAnalysis.created_at >= date_from)
        if date_to:
            conditions.append(SentimentAnalysis.created_at <= date_to)

        result = await self.session.execute(
            select(SentimentAnalysis.keywords)
            .where(and_(*conditions))
            .limit(1000)  # Limite de registros para agregar
        )

        keyword_counts: Dict[str, int] = {}
        for row in result.scalars().all():
            if row:
                for kw in row:
                    word = kw.get("word", "")
                    freq = kw.get("frequency", 1)
                    keyword_counts[word] = keyword_counts.get(word, 0) + freq

        # Ordenar e limitar
        sorted_keywords = sorted(
            keyword_counts.items(), key=lambda x: x[1], reverse=True
        )[:limit]

        return [{"word": word, "count": count} for word, count in sorted_keywords]

    async def get_emotion_distribution(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """Retorna distribuicao de emocoes."""
        conditions = [SentimentAnalysis.status == AnalysisStatus.COMPLETED]
        if date_from:
            conditions.append(SentimentAnalysis.created_at >= date_from)
        if date_to:
            conditions.append(SentimentAnalysis.created_at <= date_to)

        result = await self.session.execute(
            select(
                SentimentAnalysis.primary_emotion,
                func.count(SentimentAnalysis.id).label("count"),
            )
            .where(and_(*conditions))
            .group_by(SentimentAnalysis.primary_emotion)
        )

        return {
            r[0].value if r[0] else "unknown": r[1]
            for r in result.all()
        }


# Helper para Integer cast
from sqlalchemy import Integer
