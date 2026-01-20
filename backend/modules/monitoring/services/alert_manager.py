"""
Alert Manager Service.

Gerencia notificacoes e escalacao de alertas.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger

from ..models.alert import Alert, AlertLevel, AlertStatus


class AlertManagerService:
    """
    Servico de gerenciamento de alertas.

    Responsavel por:
    - Notificar sobre novos alertas
    - Escalar alertas nao tratados
    - Gerar estatisticas
    """

    # Tempo para escalacao automatica (em minutos)
    ESCALATION_TIMES = {
        AlertLevel.YELLOW: 60,    # 1 hora
        AlertLevel.ORANGE: 30,    # 30 minutos
        AlertLevel.RED: 10,       # 10 minutos
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self._notification_handlers: List = []

    def register_notification_handler(self, handler) -> None:
        """Registra um handler de notificacao."""
        self._notification_handlers.append(handler)

    async def notify_alert(self, alert: Alert) -> None:
        """
        Envia notificacoes para um alerta.

        Args:
            alert: Alerta a notificar
        """
        for handler in self._notification_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Erro no handler de notificacao: {e}")

        # Log de notificacao
        logger.info(
            f"Notificacao enviada para alerta {alert.id} "
            f"[{alert.level.value}] {alert.metric_name}"
        )

    async def check_escalations(self) -> List[Alert]:
        """
        Verifica alertas que precisam ser escalados.

        Returns:
            Lista de alertas escalados
        """
        escalated = []

        for level, minutes in self.ESCALATION_TIMES.items():
            threshold_time = datetime.utcnow() - timedelta(minutes=minutes)

            stmt = select(Alert).where(
                Alert.level == level,
                Alert.status == AlertStatus.ACTIVE,
                Alert.triggered_at < threshold_time,
                Alert.is_active == True,
            )

            result = await self.db.execute(stmt)
            alerts = result.scalars().all()

            for alert in alerts:
                alert.escalate()
                escalated.append(alert)
                logger.warning(
                    f"Alerta {alert.id} escalado automaticamente "
                    f"(aguardando ha mais de {minutes} minutos)"
                )

        if escalated:
            await self.db.commit()

        return escalated

    async def get_alert_statistics(
        self,
        period_hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Retorna estatisticas de alertas.

        Args:
            period_hours: Periodo em horas para analise

        Returns:
            Dicionario com estatisticas
        """
        threshold = datetime.utcnow() - timedelta(hours=period_hours)

        # Total de alertas no periodo
        stmt = select(func.count(Alert.id)).where(
            Alert.triggered_at >= threshold,
            Alert.is_active == True,
        )
        result = await self.db.execute(stmt)
        total = result.scalar() or 0

        # Por nivel
        by_level = {}
        for level in AlertLevel:
            stmt = select(func.count(Alert.id)).where(
                Alert.triggered_at >= threshold,
                Alert.level == level,
                Alert.is_active == True,
            )
            result = await self.db.execute(stmt)
            by_level[level.value] = result.scalar() or 0

        # Por status
        by_status = {}
        for status in AlertStatus:
            stmt = select(func.count(Alert.id)).where(
                Alert.triggered_at >= threshold,
                Alert.status == status,
                Alert.is_active == True,
            )
            result = await self.db.execute(stmt)
            by_status[status.value] = result.scalar() or 0

        # MTTR (Mean Time To Resolve)
        stmt = select(Alert).where(
            Alert.triggered_at >= threshold,
            Alert.status == AlertStatus.RESOLVED,
            Alert.is_active == True,
        )
        result = await self.db.execute(stmt)
        resolved_alerts = result.scalars().all()

        mttr = 0.0
        if resolved_alerts:
            total_time = sum(
                (a.resolved_at - a.triggered_at).total_seconds()
                for a in resolved_alerts
                if a.resolved_at
            )
            mttr = total_time / len(resolved_alerts)

        # Taxa de escalacao
        stmt = select(func.count(Alert.id)).where(
            Alert.triggered_at >= threshold,
            Alert.status == AlertStatus.ESCALATED,
            Alert.is_active == True,
        )
        result = await self.db.execute(stmt)
        escalated_count = result.scalar() or 0
        escalation_rate = (escalated_count / total * 100) if total > 0 else 0

        # Top metricas com mais alertas
        stmt = (
            select(Alert.metric_name, func.count(Alert.id).label("count"))
            .where(
                Alert.triggered_at >= threshold,
                Alert.is_active == True,
            )
            .group_by(Alert.metric_name)
            .order_by(func.count(Alert.id).desc())
            .limit(10)
        )
        result = await self.db.execute(stmt)
        top_metrics = [{"metric": row[0], "count": row[1]} for row in result.all()]

        return {
            "period_hours": period_hours,
            "total": total,
            "by_level": by_level,
            "by_status": by_status,
            "mttr_seconds": mttr,
            "mttr_formatted": self._format_duration(mttr),
            "escalation_rate": round(escalation_rate, 2),
            "top_metrics": top_metrics,
        }

    def _format_duration(self, seconds: float) -> str:
        """Formata duracao em formato legivel."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds / 60:.1f}min"
        else:
            return f"{seconds / 3600:.1f}h"

    async def get_alerts_timeline(
        self,
        period_hours: int = 24,
        interval_minutes: int = 60,
    ) -> List[Dict[str, Any]]:
        """
        Retorna timeline de alertas agrupados por intervalo.

        Args:
            period_hours: Periodo em horas
            interval_minutes: Intervalo de agrupamento em minutos

        Returns:
            Lista de pontos na timeline
        """
        threshold = datetime.utcnow() - timedelta(hours=period_hours)

        # Buscar todos os alertas no periodo
        stmt = select(Alert).where(
            Alert.triggered_at >= threshold,
            Alert.is_active == True,
        ).order_by(Alert.triggered_at)

        result = await self.db.execute(stmt)
        alerts = result.scalars().all()

        # Agrupar por intervalo
        timeline = []
        current_time = threshold.replace(minute=0, second=0, microsecond=0)
        end_time = datetime.utcnow()
        interval = timedelta(minutes=interval_minutes)

        while current_time < end_time:
            next_time = current_time + interval

            # Contar alertas no intervalo
            interval_alerts = [
                a for a in alerts
                if current_time <= a.triggered_at < next_time
            ]

            timeline.append({
                "timestamp": current_time.isoformat(),
                "total": len(interval_alerts),
                "yellow": sum(1 for a in interval_alerts if a.level == AlertLevel.YELLOW),
                "orange": sum(1 for a in interval_alerts if a.level == AlertLevel.ORANGE),
                "red": sum(1 for a in interval_alerts if a.level == AlertLevel.RED),
            })

            current_time = next_time

        return timeline

    async def cleanup_old_alerts(self, days: int = 90) -> int:
        """
        Remove alertas antigos resolvidos.

        Args:
            days: Idade maxima em dias

        Returns:
            Numero de alertas removidos
        """
        threshold = datetime.utcnow() - timedelta(days=days)

        stmt = select(Alert).where(
            Alert.status == AlertStatus.RESOLVED,
            Alert.resolved_at < threshold,
        )

        result = await self.db.execute(stmt)
        old_alerts = result.scalars().all()

        for alert in old_alerts:
            alert.is_active = False

        await self.db.commit()

        logger.info(f"Cleanup: {len(old_alerts)} alertas antigos desativados")
        return len(old_alerts)

    async def suppress_alert(
        self,
        alert_id: UUID,
        duration_minutes: int = 60,
    ) -> Optional[Alert]:
        """
        Suprime um alerta temporariamente.

        Args:
            alert_id: ID do alerta
            duration_minutes: Duracao da supressao em minutos

        Returns:
            Alerta atualizado ou None
        """
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await self.db.execute(stmt)
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        alert.suppress()
        alert.details = alert.details or {}
        alert.details["suppressed_until"] = (
            datetime.utcnow() + timedelta(minutes=duration_minutes)
        ).isoformat()

        await self.db.commit()
        await self.db.refresh(alert)

        logger.info(f"Alerta {alert_id} suprimido por {duration_minutes} minutos")
        return alert
