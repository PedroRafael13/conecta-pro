"""Analytics avançado para notificações."""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class TimeGranularity(Enum):
    """Granularidade temporal."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TrendDirection(Enum):
    """Direção da tendência."""

    UP = "up"
    DOWN = "down"
    STABLE = "stable"


@dataclass
class MetricPoint:
    """Ponto de métrica no tempo."""

    timestamp: datetime
    value: float
    count: int = 0


@dataclass
class ChannelPerformance:
    """Performance de um canal."""

    channel: str
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_converted: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    conversion_rate: float
    avg_delivery_time_seconds: float
    cost_total: float
    cost_per_conversion: float
    trend: TrendDirection


@dataclass
class CampaignMetrics:
    """Métricas de uma campanha."""

    campaign_id: str
    name: str
    start_date: datetime
    end_date: datetime | None
    total_recipients: int
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_converted: int
    total_unsubscribed: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    conversion_rate: float
    unsubscribe_rate: float
    revenue_attributed: float
    roi: float


@dataclass
class TrendAnalysis:
    """Análise de tendência."""

    metric_name: str
    direction: TrendDirection
    change_percentage: float
    current_value: float
    previous_value: float
    period: str
    data_points: list[MetricPoint]
    forecast: list[MetricPoint]
    confidence: float


@dataclass
class MetricReport:
    """Relatório de métricas."""

    period_start: datetime
    period_end: datetime
    total_notifications: int
    total_unique_users: int
    channels_performance: list[ChannelPerformance]
    top_campaigns: list[CampaignMetrics]
    trends: list[TrendAnalysis]
    insights: list[str]
    recommendations: list[str]


@dataclass
class AnalyticsDashboard:
    """Dashboard de analytics."""

    generated_at: datetime
    summary: dict[str, Any]
    realtime_metrics: dict[str, float]
    channel_breakdown: list[ChannelPerformance]
    recent_campaigns: list[CampaignMetrics]
    alerts: list[str]
    health_score: float


class NotificationAnalytics:
    """
    Sistema de analytics para notificações.

    Features:
    - Métricas em tempo real
    - Análise de tendências
    - Performance por canal
    - ROI de campanhas
    - Forecasting simples
    - Alertas automáticos
    """

    # Thresholds para alertas
    ALERT_THRESHOLDS = {
        "delivery_rate": 0.90,  # Alerta se < 90%
        "open_rate_drop": 0.20,  # Alerta se cair > 20%
        "unsubscribe_spike": 0.05,  # Alerta se > 5%
        "cost_spike": 1.5,  # Alerta se custo > 150% da média
    }

    def __init__(
        self,
        default_lookback_days: int = 30,
        enable_forecasting: bool = True,
    ) -> None:
        """
        Inicializa o analytics.

        Args:
            default_lookback_days: Dias padrão para análise
            enable_forecasting: Habilitar previsões
        """
        self.lookback_days = default_lookback_days
        self.enable_forecasting = enable_forecasting

    async def get_dashboard(
        self,
        db: AsyncSession,
        tenant_id: str | None = None,
    ) -> AnalyticsDashboard:
        """
        Gera dashboard de analytics.

        Args:
            db: Sessão do banco
            tenant_id: ID do tenant (opcional)

        Returns:
            AnalyticsDashboard com visão geral
        """
        now = datetime.utcnow()

        # Métricas em tempo real
        realtime = await self._get_realtime_metrics(db, tenant_id)

        # Performance por canal
        channels = await self._get_channel_performance(db, tenant_id, days=7)

        # Campanhas recentes
        campaigns = await self._get_recent_campaigns(db, tenant_id, limit=5)

        # Gerar alertas
        alerts = await self._generate_alerts(db, tenant_id, realtime, channels)

        # Calcular health score
        health = self._calculate_health_score(realtime, channels, alerts)

        # Summary
        summary = {
            "total_sent_today": realtime.get("sent_today", 0),
            "total_delivered_today": realtime.get("delivered_today", 0),
            "avg_delivery_rate": realtime.get("delivery_rate", 0),
            "avg_open_rate": realtime.get("open_rate", 0),
            "active_campaigns": len([c for c in campaigns if not c.end_date]),
        }

        return AnalyticsDashboard(
            generated_at=now,
            summary=summary,
            realtime_metrics=realtime,
            channel_breakdown=channels,
            recent_campaigns=campaigns,
            alerts=alerts,
            health_score=health,
        )

    async def generate_report(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        tenant_id: str | None = None,
        granularity: TimeGranularity = TimeGranularity.DAILY,
    ) -> MetricReport:
        """
        Gera relatório detalhado.

        Args:
            db: Sessão do banco
            start_date: Data inicial
            end_date: Data final
            tenant_id: ID do tenant
            granularity: Granularidade temporal

        Returns:
            MetricReport completo
        """
        # Obter dados agregados
        totals = await self._get_period_totals(db, start_date, end_date, tenant_id)

        # Performance por canal
        channels = await self._get_channel_performance(
            db,
            tenant_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Top campanhas
        campaigns = await self._get_top_campaigns(
            db,
            tenant_id,
            start_date=start_date,
            end_date=end_date,
            limit=10,
        )

        # Análise de tendências
        trends = await self._analyze_trends(
            db,
            tenant_id,
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
        )

        # Gerar insights
        insights = self._generate_insights(channels, campaigns, trends)

        # Gerar recomendações
        recommendations = self._generate_recommendations(channels, campaigns, trends)

        return MetricReport(
            period_start=start_date,
            period_end=end_date,
            total_notifications=totals.get("total_sent", 0),
            total_unique_users=totals.get("unique_users", 0),
            channels_performance=channels,
            top_campaigns=campaigns,
            trends=trends,
            insights=insights,
            recommendations=recommendations,
        )

    async def get_channel_analytics(
        self,
        db: AsyncSession,
        channel: str,
        days: int = 30,
        tenant_id: str | None = None,
    ) -> ChannelPerformance:
        """
        Obtém analytics de um canal específico.

        Args:
            db: Sessão do banco
            channel: Nome do canal
            days: Dias para análise
            tenant_id: ID do tenant

        Returns:
            ChannelPerformance detalhado
        """
        # TODO: Implementar query real
        return await self._get_channel_metrics(db, channel, days, tenant_id)

    async def get_campaign_analytics(
        self,
        db: AsyncSession,
        campaign_id: str,
    ) -> CampaignMetrics:
        """
        Obtém analytics de uma campanha.

        Args:
            db: Sessão do banco
            campaign_id: ID da campanha

        Returns:
            CampaignMetrics detalhado
        """
        # TODO: Implementar query real
        return await self._get_campaign_metrics(db, campaign_id)

    async def get_user_analytics(
        self,
        db: AsyncSession,
        user_id: int,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Obtém analytics de um usuário.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            days: Dias para análise

        Returns:
            Dict com métricas do usuário
        """
        # TODO: Implementar query real
        return {
            "user_id": user_id,
            "total_received": 45,
            "total_opened": 30,
            "total_clicked": 10,
            "open_rate": 0.67,
            "click_rate": 0.22,
            "preferred_channel": "push",
            "preferred_time": "10:00",
            "engagement_score": 0.75,
            "last_engagement": datetime.utcnow() - timedelta(days=2),
        }

    async def forecast_metrics(
        self,
        db: AsyncSession,
        metric: str,
        days_ahead: int = 7,
        tenant_id: str | None = None,
    ) -> list[MetricPoint]:
        """
        Prevê métricas futuras.

        Args:
            db: Sessão do banco
            metric: Nome da métrica
            days_ahead: Dias para previsão
            tenant_id: ID do tenant

        Returns:
            Lista de MetricPoint previstos
        """
        if not self.enable_forecasting:
            return []

        # Obter dados históricos
        historical = await self._get_historical_data(db, metric, days=30, tenant_id=tenant_id)

        # Calcular tendência simples (média móvel)
        forecast = self._simple_forecast(historical, days_ahead)

        return forecast

    async def _get_realtime_metrics(
        self,
        db: AsyncSession,
        tenant_id: str | None,
    ) -> dict[str, float]:
        """Obtém métricas em tempo real."""
        # TODO: Implementar query real com dados de hoje

        return {
            "sent_today": 1250,
            "delivered_today": 1200,
            "opened_today": 450,
            "clicked_today": 120,
            "delivery_rate": 0.96,
            "open_rate": 0.375,
            "click_rate": 0.10,
            "active_users": 350,
            "queue_size": 50,
            "avg_delivery_time_ms": 250,
        }

    async def _get_channel_performance(
        self,
        db: AsyncSession,
        tenant_id: str | None,
        days: int = 30,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[ChannelPerformance]:
        """Obtém performance por canal."""
        # TODO: Implementar query real

        channels = ["push", "email", "sms", "whatsapp", "in_app"]
        results = []

        for channel in channels:
            perf = await self._get_channel_metrics(db, channel, days, tenant_id)
            results.append(perf)

        return results

    async def _get_channel_metrics(
        self,
        db: AsyncSession,
        channel: str,
        days: int,
        tenant_id: str | None,
    ) -> ChannelPerformance:
        """Obtém métricas de um canal."""
        # TODO: Implementar query real

        # Dados simulados
        base_metrics = {
            "push": {"sent": 5000, "opened": 3500, "clicked": 1000, "cost": 0},
            "email": {"sent": 3000, "opened": 1200, "clicked": 300, "cost": 3.0},
            "sms": {"sent": 500, "opened": 475, "clicked": 50, "cost": 25.0},
            "whatsapp": {"sent": 800, "opened": 720, "clicked": 200, "cost": 24.0},
            "in_app": {"sent": 4000, "opened": 3400, "clicked": 1500, "cost": 0},
        }

        metrics = base_metrics.get(channel, {"sent": 0, "opened": 0, "clicked": 0, "cost": 0})

        sent = metrics["sent"]
        delivered = int(sent * 0.98)
        opened = metrics["opened"]
        clicked = metrics["clicked"]
        converted = int(clicked * 0.15)

        return ChannelPerformance(
            channel=channel,
            total_sent=sent,
            total_delivered=delivered,
            total_opened=opened,
            total_clicked=clicked,
            total_converted=converted,
            delivery_rate=delivered / max(sent, 1),
            open_rate=opened / max(delivered, 1),
            click_rate=clicked / max(opened, 1),
            conversion_rate=converted / max(clicked, 1),
            avg_delivery_time_seconds=5 if channel in ["push", "in_app"] else 30,
            cost_total=metrics["cost"],
            cost_per_conversion=metrics["cost"] / max(converted, 1),
            trend=TrendDirection.UP if channel in ["push", "whatsapp"] else TrendDirection.STABLE,
        )

    async def _get_recent_campaigns(
        self,
        db: AsyncSession,
        tenant_id: str | None,
        limit: int = 5,
    ) -> list[CampaignMetrics]:
        """Obtém campanhas recentes."""
        # TODO: Implementar query real

        return [
            CampaignMetrics(
                campaign_id="camp_001",
                name="Boas-vindas Novos Moradores",
                start_date=datetime.utcnow() - timedelta(days=7),
                end_date=None,
                total_recipients=150,
                total_sent=150,
                total_delivered=148,
                total_opened=95,
                total_clicked=35,
                total_converted=12,
                total_unsubscribed=2,
                delivery_rate=0.987,
                open_rate=0.642,
                click_rate=0.368,
                conversion_rate=0.343,
                unsubscribe_rate=0.013,
                revenue_attributed=0,
                roi=0,
            ),
            CampaignMetrics(
                campaign_id="camp_002",
                name="Lembrete Assembleia",
                start_date=datetime.utcnow() - timedelta(days=3),
                end_date=datetime.utcnow() - timedelta(days=1),
                total_recipients=200,
                total_sent=200,
                total_delivered=198,
                total_opened=165,
                total_clicked=80,
                total_converted=45,
                total_unsubscribed=0,
                delivery_rate=0.99,
                open_rate=0.833,
                click_rate=0.485,
                conversion_rate=0.563,
                unsubscribe_rate=0,
                revenue_attributed=0,
                roi=0,
            ),
        ]

    async def _get_top_campaigns(
        self,
        db: AsyncSession,
        tenant_id: str | None,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10,
    ) -> list[CampaignMetrics]:
        """Obtém top campanhas por performance."""
        campaigns = await self._get_recent_campaigns(db, tenant_id, limit=limit)
        # Ordenar por open_rate
        return sorted(campaigns, key=lambda c: c.open_rate, reverse=True)

    async def _get_period_totals(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        tenant_id: str | None,
    ) -> dict[str, int]:
        """Obtém totais do período."""
        # TODO: Implementar query real

        return {
            "total_sent": 15000,
            "total_delivered": 14700,
            "total_opened": 8500,
            "total_clicked": 2500,
            "total_converted": 800,
            "unique_users": 2500,
        }

    async def _analyze_trends(
        self,
        db: AsyncSession,
        tenant_id: str | None,
        start_date: datetime,
        end_date: datetime,
        granularity: TimeGranularity,
    ) -> list[TrendAnalysis]:
        """Analisa tendências de métricas."""
        metrics = ["open_rate", "click_rate", "delivery_rate"]
        trends = []

        for metric in metrics:
            historical = await self._get_historical_data(
                db,
                metric,
                days=(end_date - start_date).days,
                tenant_id=tenant_id,
            )

            if len(historical) < 2:
                continue

            # Calcular tendência
            current = historical[-1].value
            previous = historical[0].value

            if previous > 0:
                change = (current - previous) / previous
            else:
                change = 0

            direction = TrendDirection.STABLE
            if change > 0.05:
                direction = TrendDirection.UP
            elif change < -0.05:
                direction = TrendDirection.DOWN

            # Forecast
            forecast = []
            if self.enable_forecasting:
                forecast = self._simple_forecast(historical, days_ahead=7)

            trends.append(
                TrendAnalysis(
                    metric_name=metric,
                    direction=direction,
                    change_percentage=change * 100,
                    current_value=current,
                    previous_value=previous,
                    period=f"{start_date.date()} - {end_date.date()}",
                    data_points=historical,
                    forecast=forecast,
                    confidence=0.75 if len(historical) >= 14 else 0.5,
                )
            )

        return trends

    async def _get_historical_data(
        self,
        db: AsyncSession,
        metric: str,
        days: int,
        tenant_id: str | None,
    ) -> list[MetricPoint]:
        """Obtém dados históricos de uma métrica."""
        # TODO: Implementar query real

        # Simular dados
        data = []
        base_value = {"open_rate": 0.35, "click_rate": 0.10, "delivery_rate": 0.96}.get(metric, 0.5)

        for i in range(days):
            timestamp = datetime.utcnow() - timedelta(days=days - i)
            # Adicionar variação
            variation = (hash(f"{metric}_{i}") % 20 - 10) / 100
            value = base_value + variation

            data.append(
                MetricPoint(
                    timestamp=timestamp,
                    value=max(0, min(1, value)),
                    count=100 + (i * 5),
                )
            )

        return data

    def _simple_forecast(
        self,
        historical: list[MetricPoint],
        days_ahead: int,
    ) -> list[MetricPoint]:
        """Faz previsão simples usando média móvel."""
        if len(historical) < 7:
            return []

        # Média dos últimos 7 dias
        recent = [p.value for p in historical[-7:]]
        avg = sum(recent) / len(recent)

        # Calcular tendência
        if len(historical) >= 14:
            older = [p.value for p in historical[-14:-7]]
            older_avg = sum(older) / len(older)
            trend = (avg - older_avg) / 7
        else:
            trend = 0

        # Gerar previsões
        forecast = []
        last_timestamp = historical[-1].timestamp

        for i in range(days_ahead):
            timestamp = last_timestamp + timedelta(days=i + 1)
            predicted_value = avg + (trend * (i + 1))
            # Limitar entre 0 e 1 para taxas
            predicted_value = max(0, min(1, predicted_value))

            forecast.append(
                MetricPoint(
                    timestamp=timestamp,
                    value=predicted_value,
                    count=0,
                )
            )

        return forecast

    async def _generate_alerts(
        self,
        db: AsyncSession,
        tenant_id: str | None,
        realtime: dict[str, float],
        channels: list[ChannelPerformance],
    ) -> list[str]:
        """Gera alertas automáticos."""
        alerts = []

        # Alerta de delivery rate baixo
        delivery_rate = realtime.get("delivery_rate", 1.0)
        if delivery_rate < self.ALERT_THRESHOLDS["delivery_rate"]:
            alerts.append(f"⚠️ Taxa de entrega baixa: {delivery_rate:.1%}")

        # Alerta por canal
        for channel in channels:
            if channel.delivery_rate < self.ALERT_THRESHOLDS["delivery_rate"]:
                alerts.append(f"⚠️ {channel.channel}: delivery rate baixo ({channel.delivery_rate:.1%})")

            if channel.trend == TrendDirection.DOWN:
                alerts.append(f"📉 {channel.channel}: tendência de queda detectada")

        # Alerta de fila
        queue_size = realtime.get("queue_size", 0)
        if queue_size > 1000:
            alerts.append(f"⚠️ Fila de notificações alta: {queue_size}")

        return alerts

    def _calculate_health_score(
        self,
        realtime: dict[str, float],
        channels: list[ChannelPerformance],
        alerts: list[str],
    ) -> float:
        """Calcula score de saúde do sistema."""
        score = 1.0

        # Penalidade por alertas
        score -= len(alerts) * 0.1

        # Penalidade por delivery rate baixo
        delivery_rate = realtime.get("delivery_rate", 1.0)
        if delivery_rate < 0.95:
            score -= 0.95 - delivery_rate

        # Penalidade por canais com problemas
        for channel in channels:
            if channel.delivery_rate < 0.90:
                score -= 0.05

        return max(0, min(1, score))

    def _generate_insights(
        self,
        channels: list[ChannelPerformance],
        campaigns: list[CampaignMetrics],
        trends: list[TrendAnalysis],
    ) -> list[str]:
        """Gera insights dos dados."""
        insights = []

        # Insight de melhor canal
        best_channel = max(channels, key=lambda c: c.open_rate)
        insights.append(f"Melhor canal por open rate: {best_channel.channel} ({best_channel.open_rate:.1%})")

        # Insight de custo-benefício
        cost_channels = [c for c in channels if c.cost_total > 0]
        if cost_channels:
            best_roi = min(cost_channels, key=lambda c: c.cost_per_conversion)
            insights.append(
                f"Melhor custo-benefício: {best_roi.channel} (R${best_roi.cost_per_conversion:.2f}/conversão)"
            )

        # Insight de tendências
        for trend in trends:
            if trend.direction == TrendDirection.UP and trend.change_percentage > 10:
                insights.append(f"📈 {trend.metric_name} crescendo {trend.change_percentage:.1f}%")
            elif trend.direction == TrendDirection.DOWN and trend.change_percentage < -10:
                insights.append(f"📉 {trend.metric_name} caindo {abs(trend.change_percentage):.1f}%")

        # Insight de campanhas
        if campaigns:
            best_campaign = max(campaigns, key=lambda c: c.conversion_rate)
            insights.append(f"Melhor campanha: {best_campaign.name} ({best_campaign.conversion_rate:.1%} conversão)")

        return insights

    def _generate_recommendations(
        self,
        channels: list[ChannelPerformance],
        campaigns: list[CampaignMetrics],
        trends: list[TrendAnalysis],
    ) -> list[str]:
        """Gera recomendações baseadas nos dados."""
        recommendations = []

        # Recomendação de canal
        underperforming = [c for c in channels if c.open_rate < 0.20]
        if underperforming:
            channels_names = ", ".join(c.channel for c in underperforming)
            recommendations.append(f"Revisar estratégia de {channels_names} - baixo engajamento")

        # Recomendação de timing
        for trend in trends:
            if trend.metric_name == "open_rate" and trend.direction == TrendDirection.DOWN:
                recommendations.append("Considerar otimização de timing de envio")

        # Recomendação de custo
        high_cost = [c for c in channels if c.cost_per_conversion > 1.0]
        if high_cost:
            recommendations.append(f"Avaliar ROI de {', '.join(c.channel for c in high_cost)}")

        # Recomendação de A/B testing
        if len(campaigns) > 0:
            avg_conversion = sum(c.conversion_rate for c in campaigns) / len(campaigns)
            if avg_conversion < 0.30:
                recommendations.append("Implementar A/B testing para melhorar conversão")

        return recommendations

    async def export_report(
        self,
        db: AsyncSession,
        report: MetricReport,
        export_format: str = "json",
    ) -> str:
        """
        Exporta relatório em formato específico.

        Args:
            db: Sessão do banco
            report: Relatório a exportar
            export_format: Formato (json, csv)

        Returns:
            String com dados exportados
        """
        if export_format == "json":
            import json

            return json.dumps(
                {
                    "period": f"{report.period_start} - {report.period_end}",
                    "total_notifications": report.total_notifications,
                    "total_users": report.total_unique_users,
                    "insights": report.insights,
                    "recommendations": report.recommendations,
                },
                default=str,
                indent=2,
            )

        elif export_format == "csv":
            lines = ["metric,value"]
            lines.append(f"total_notifications,{report.total_notifications}")
            lines.append(f"total_users,{report.total_unique_users}")
            for channel in report.channels_performance:
                lines.append(f"{channel.channel}_open_rate,{channel.open_rate}")
            return "\n".join(lines)

        return ""
