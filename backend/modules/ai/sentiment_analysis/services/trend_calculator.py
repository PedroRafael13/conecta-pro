"""
Trend Calculator Service - Sprint 46

Servico para calculo e rastreamento de tendencias de sentimento.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
import statistics

from sqlalchemy.ext.asyncio import AsyncSession

from modules.ai.sentiment_analysis.models import (
    SentimentTrend,
    TrendPeriod,
    TrendDirection,
    SentimentType,
)
from modules.ai.sentiment_analysis.models.sentiment_trend import TrendCategory
from modules.ai.sentiment_analysis.repositories import SentimentRepository

logger = logging.getLogger(__name__)


class TrendCalculator:
    """Servico de calculo de tendencias."""

    # Configuracao de periodos
    PERIOD_CONFIG = {
        TrendPeriod.HOURLY: {
            "delta": timedelta(hours=1),
            "label_format": "%Y-%m-%d %H:00",
        },
        TrendPeriod.DAILY: {
            "delta": timedelta(days=1),
            "label_format": "%Y-%m-%d",
        },
        TrendPeriod.WEEKLY: {
            "delta": timedelta(weeks=1),
            "label_format": "%Y-W%W",
        },
        TrendPeriod.MONTHLY: {
            "delta": timedelta(days=30),
            "label_format": "%Y-%m",
        },
        TrendPeriod.QUARTERLY: {
            "delta": timedelta(days=90),
            "label_format": "%Y-Q%q",
        },
        TrendPeriod.YEARLY: {
            "delta": timedelta(days=365),
            "label_format": "%Y",
        },
    }

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = SentimentRepository(session)

    async def calculate_trend(
        self,
        period_type: TrendPeriod,
        period_start: datetime,
        period_end: datetime,
        category: TrendCategory = TrendCategory.OVERALL,
        category_value: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
    ) -> SentimentTrend:
        """
        Calcula tendencia para um periodo especifico.

        Args:
            period_type: Tipo de periodo (diario, semanal, etc)
            period_start: Inicio do periodo
            period_end: Fim do periodo
            category: Categoria da tendencia
            category_value: Valor especifico da categoria
            entity_type: Tipo de entidade (opcional)
            entity_id: ID da entidade (opcional)

        Returns:
            Tendencia calculada
        """
        logger.info(
            f"Calculando tendencia {period_type.value} "
            f"de {period_start} a {period_end}"
        )

        # Gerar label do periodo
        period_label = self._generate_period_label(period_type, period_start)

        # Verificar se ja existe
        existing = await self.repository.get_trend_by_period(
            period_type=period_type,
            period_label=period_label,
            category=category.value,
            category_value=category_value,
        )

        if existing:
            trend = existing
        else:
            trend = SentimentTrend(
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                period_label=period_label,
                category=category,
                category_value=category_value,
                entity_type=entity_type,
                entity_id=entity_id,
            )

        # Buscar agregacao de dados
        aggregations = await self.repository.aggregate_sentiment_by_period(
            period_start=period_start,
            period_end=period_end,
        )

        if not aggregations or aggregations[0]["count"] == 0:
            logger.warning(f"Sem dados para o periodo {period_label}")
            trend.total_analyses = 0
            if not existing:
                await self.repository.create_trend(trend)
            return trend

        agg = aggregations[0]

        # Preencher metricas basicas
        trend.total_analyses = agg["count"]
        trend.avg_sentiment_score = agg["avg_score"]
        trend.min_sentiment_score = agg["min_score"]
        trend.max_sentiment_score = agg["max_score"]

        # Distribuicao
        trend.very_positive_count = agg["very_positive"]
        trend.positive_count = agg["positive"]
        trend.neutral_count = agg["neutral"]
        trend.negative_count = agg["negative"]
        trend.very_negative_count = agg["very_negative"]

        # Calcular percentuais
        trend.calculate_percentages()

        # Buscar distribuicao de emocoes
        emotion_dist = await self.repository.get_emotion_distribution(
            date_from=period_start,
            date_to=period_end,
        )
        trend.emotion_distribution = emotion_dist
        if emotion_dist:
            trend.primary_emotion = max(emotion_dist, key=emotion_dist.get)

        # Buscar keywords
        keywords = await self.repository.get_top_keywords(
            date_from=period_start,
            date_to=period_end,
            limit=20,
        )
        trend.top_keywords = keywords

        # Buscar estatisticas adicionais
        stats = await self.repository.get_analysis_stats(
            date_from=period_start,
            date_to=period_end,
        )
        trend.complaints_count = stats.get("complaint_count", 0)
        trend.urgency_count = stats.get("urgency_count", 0)
        trend.churn_risk_count = stats.get("churn_risk_count", 0)
        trend.total_with_action = stats.get("action_required_count", 0)

        # Calcular taxa de reclamacoes
        if trend.total_analyses > 0:
            trend.complaints_rate = (
                trend.complaints_count / trend.total_analyses
            ) * 100

        # Comparar com periodo anterior
        previous_trend = await self._get_previous_trend(
            period_type=period_type,
            period_start=period_start,
            category=category.value,
            category_value=category_value,
        )

        if previous_trend:
            trend.calculate_trend(
                previous_score=previous_trend.avg_sentiment_score,
                previous_volume=previous_trend.total_analyses,
            )

        # Calcular desvio padrao (simulado se nao tivermos dados individuais)
        if trend.min_sentiment_score and trend.max_sentiment_score:
            range_val = trend.max_sentiment_score - trend.min_sentiment_score
            trend.std_sentiment_score = range_val / 4  # Estimativa

        # Fazer previsao simples
        trend.predicted_next_score = self._predict_next_score(trend)

        # Gerar insights automaticos
        trend.generate_automatic_insights()

        # Marcar como calculado
        trend.calculated_at = datetime.utcnow()

        # Salvar
        if existing:
            await self.repository.update_trend(trend.id)
        else:
            await self.repository.create_trend(trend)

        logger.info(
            f"Tendencia calculada: {period_label} - "
            f"Score: {trend.avg_sentiment_score} - "
            f"Direcao: {trend.trend_direction.value}"
        )

        return trend

    async def calculate_trends_for_range(
        self,
        period_type: TrendPeriod,
        start_date: datetime,
        end_date: datetime,
        category: TrendCategory = TrendCategory.OVERALL,
        category_value: Optional[str] = None,
    ) -> List[SentimentTrend]:
        """Calcula tendencias para um range de datas."""
        trends = []
        config = self.PERIOD_CONFIG[period_type]
        delta = config["delta"]

        current_start = start_date
        while current_start < end_date:
            current_end = min(current_start + delta, end_date)

            trend = await self.calculate_trend(
                period_type=period_type,
                period_start=current_start,
                period_end=current_end,
                category=category,
                category_value=category_value,
            )
            trends.append(trend)

            current_start = current_end

        return trends

    async def get_trend_comparison(
        self,
        period_type: TrendPeriod,
        current_start: datetime,
        current_end: datetime,
        category: TrendCategory = TrendCategory.OVERALL,
    ) -> Dict[str, Any]:
        """Compara tendencia atual com periodo anterior."""
        # Tendencia atual
        current_trend = await self.calculate_trend(
            period_type=period_type,
            period_start=current_start,
            period_end=current_end,
            category=category,
        )

        # Tendencia anterior
        config = self.PERIOD_CONFIG[period_type]
        delta = config["delta"]
        prev_start = current_start - delta
        prev_end = current_start

        previous_trend = await self.calculate_trend(
            period_type=period_type,
            period_start=prev_start,
            period_end=prev_end,
            category=category,
        )

        # Calcular diferencas
        score_diff = (
            current_trend.avg_sentiment_score - previous_trend.avg_sentiment_score
        )
        volume_diff = current_trend.total_analyses - previous_trend.total_analyses

        satisfaction_diff = (
            current_trend.satisfaction_rate - previous_trend.satisfaction_rate
        )

        # Gerar highlights
        highlights = self._generate_comparison_highlights(
            current_trend, previous_trend
        )

        return {
            "current": current_trend.to_summary(),
            "previous": previous_trend.to_summary(),
            "score_improvement": round(score_diff, 2),
            "volume_change": volume_diff,
            "satisfaction_change": round(satisfaction_diff, 2),
            "trend_direction": current_trend.trend_direction.value,
            "highlights": highlights,
        }

    async def get_trend_timeline(
        self,
        period_type: TrendPeriod,
        periods: int = 12,
        category: TrendCategory = TrendCategory.OVERALL,
        category_value: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retorna timeline de tendencias."""
        trends = await self.repository.list_trends(
            period_type=period_type,
            category=category.value if isinstance(category, TrendCategory) else category,
            limit=periods,
        )

        return [t.to_summary() for t in reversed(trends)]

    async def _get_previous_trend(
        self,
        period_type: TrendPeriod,
        period_start: datetime,
        category: str,
        category_value: Optional[str] = None,
    ) -> Optional[SentimentTrend]:
        """Busca tendencia do periodo anterior."""
        config = self.PERIOD_CONFIG[period_type]
        delta = config["delta"]

        prev_start = period_start - delta
        prev_label = self._generate_period_label(period_type, prev_start)

        return await self.repository.get_trend_by_period(
            period_type=period_type,
            period_label=prev_label,
            category=category,
            category_value=category_value,
        )

    def _generate_period_label(
        self,
        period_type: TrendPeriod,
        date: datetime,
    ) -> str:
        """Gera label para o periodo."""
        config = self.PERIOD_CONFIG[period_type]
        format_str = config["label_format"]

        # Tratar caso especial de trimestre
        if "%q" in format_str:
            quarter = (date.month - 1) // 3 + 1
            return f"{date.year}-Q{quarter}"

        return date.strftime(format_str)

    def _predict_next_score(self, trend: SentimentTrend) -> Optional[float]:
        """Faz previsao simples do proximo score."""
        if trend.prev_avg_score is None:
            return None

        # Modelo simples: continuar na mesma direcao
        change = trend.score_change or 0

        # Aplicar dampening
        dampening = 0.7
        predicted = trend.avg_sentiment_score + (change * dampening)

        # Limitar ao range valido
        return max(-100, min(100, round(predicted, 2)))

    def _generate_comparison_highlights(
        self,
        current: SentimentTrend,
        previous: SentimentTrend,
    ) -> List[str]:
        """Gera highlights da comparacao."""
        highlights = []

        score_diff = current.avg_sentiment_score - previous.avg_sentiment_score

        if score_diff > 10:
            highlights.append(
                f"Sentimento melhorou {abs(score_diff):.1f} pontos"
            )
        elif score_diff < -10:
            highlights.append(
                f"Sentimento piorou {abs(score_diff):.1f} pontos"
            )

        satisfaction_diff = current.satisfaction_rate - previous.satisfaction_rate
        if satisfaction_diff > 5:
            highlights.append(
                f"Satisfacao aumentou {satisfaction_diff:.1f}%"
            )
        elif satisfaction_diff < -5:
            highlights.append(
                f"Satisfacao diminuiu {abs(satisfaction_diff):.1f}%"
            )

        if current.total_analyses > previous.total_analyses * 1.5:
            highlights.append("Volume de feedback aumentou significativamente")
        elif current.total_analyses < previous.total_analyses * 0.5:
            highlights.append("Volume de feedback diminuiu significativamente")

        if current.complaints_rate > previous.complaints_rate + 5:
            highlights.append("Taxa de reclamacoes aumentou")

        if current.churn_risk_count > previous.churn_risk_count:
            diff = current.churn_risk_count - previous.churn_risk_count
            highlights.append(f"+{diff} clientes com risco de churn")

        return highlights

    async def calculate_daily_trends(self) -> List[SentimentTrend]:
        """Calcula tendencias diarias (job agendado)."""
        now = datetime.utcnow()
        yesterday_start = now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=1)
        yesterday_end = yesterday_start + timedelta(days=1)

        trend = await self.calculate_trend(
            period_type=TrendPeriod.DAILY,
            period_start=yesterday_start,
            period_end=yesterday_end,
        )

        return [trend]

    async def calculate_weekly_trends(self) -> List[SentimentTrend]:
        """Calcula tendencias semanais (job agendado)."""
        now = datetime.utcnow()

        # Encontrar inicio da semana anterior (segunda)
        days_since_monday = now.weekday()
        this_monday = now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=days_since_monday)
        last_monday = this_monday - timedelta(weeks=1)
        last_sunday = this_monday

        trend = await self.calculate_trend(
            period_type=TrendPeriod.WEEKLY,
            period_start=last_monday,
            period_end=last_sunday,
        )

        return [trend]

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Retorna resumo para dashboard."""
        now = datetime.utcnow()

        # Ultimas 24h
        daily_start = now - timedelta(hours=24)
        daily_stats = await self.repository.get_analysis_stats(
            date_from=daily_start,
            date_to=now,
        )

        # Ultimos 7 dias
        weekly_start = now - timedelta(days=7)
        weekly_stats = await self.repository.get_analysis_stats(
            date_from=weekly_start,
            date_to=now,
        )

        # Tendencia mais recente
        latest_daily = await self.repository.get_latest_trend(TrendPeriod.DAILY)
        latest_weekly = await self.repository.get_latest_trend(TrendPeriod.WEEKLY)

        # Emocoes do periodo
        emotion_dist = await self.repository.get_emotion_distribution(
            date_from=weekly_start,
            date_to=now,
        )

        # Top keywords
        top_keywords = await self.repository.get_top_keywords(
            date_from=weekly_start,
            date_to=now,
            limit=10,
        )

        return {
            "daily": {
                "total": daily_stats["total"],
                "avg_score": daily_stats["avg_score"],
                "distribution": daily_stats["sentiment_distribution"],
                "complaints": daily_stats["complaint_count"],
                "urgency": daily_stats["urgency_count"],
            },
            "weekly": {
                "total": weekly_stats["total"],
                "avg_score": weekly_stats["avg_score"],
                "distribution": weekly_stats["sentiment_distribution"],
                "complaints": weekly_stats["complaint_count"],
                "churn_risk": weekly_stats["churn_risk_count"],
            },
            "trend_daily": latest_daily.to_summary() if latest_daily else None,
            "trend_weekly": latest_weekly.to_summary() if latest_weekly else None,
            "emotions": emotion_dist,
            "top_keywords": top_keywords,
            "generated_at": now.isoformat(),
        }
