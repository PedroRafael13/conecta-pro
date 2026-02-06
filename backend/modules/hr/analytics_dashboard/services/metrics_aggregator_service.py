"""Service para agregação de métricas."""

import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import UUID
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.analytics_dashboard.models import (
    AnalyticsCache,
    CacheType,
    DataSource,
    AggregationType,
)
from modules.hr.analytics_dashboard.repositories import CacheRepository

logger = logging.getLogger(__name__)


class TimeGranularity(str, Enum):
    """Granularidade temporal."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class MetricsAggregatorService:
    """Service para agregação de métricas de RH."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache_repo = CacheRepository(db)

    async def aggregate_data(
        self,
        data_source: DataSource,
        aggregation: AggregationType,
        condominio_id: UUID,
        period_start: datetime = None,
        period_end: datetime = None,
        group_by: str = None,
        filters: dict = None,
        limit: int = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Agrega dados de uma fonte."""
        # Período padrão
        if not period_end:
            period_end = datetime.utcnow()
        if not period_start:
            period_start = period_end - timedelta(days=30)

        # Cache key
        cache_key = AnalyticsCache.generate_cache_key(
            cache_type=CacheType.AGGREGATION.value,
            identifier=f"{data_source.value}_{aggregation.value}",
            params={
                "condominio_id": str(condominio_id),
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "group_by": group_by,
                "filters": filters,
                "limit": limit,
            },
        )

        if use_cache:
            cached = await self.cache_repo.get_valid_cache(cache_key, condominio_id)
            if cached:
                await self.cache_repo.record_hit(cached.id)
                return cached.data

        # Calcular
        start_time = datetime.utcnow()
        result = await self._aggregate(
            data_source=data_source,
            aggregation=aggregation,
            condominio_id=condominio_id,
            period_start=period_start,
            period_end=period_end,
            group_by=group_by,
            filters=filters,
            limit=limit,
        )
        computation_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Salvar cache
        await self.cache_repo.set_cache(
            condominio_id=condominio_id,
            cache_key=cache_key,
            cache_type=CacheType.AGGREGATION,
            data=result,
            ttl_seconds=300,
            computation_time_ms=computation_time,
        )

        return result

    async def _aggregate(
        self,
        data_source: DataSource,
        aggregation: AggregationType,
        condominio_id: UUID,
        period_start: datetime,
        period_end: datetime,
        group_by: str = None,
        filters: dict = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """Executa agregação."""
        aggregators = {
            DataSource.TIME_ENTRIES: self._aggregate_time_entries,
            DataSource.CHECKINS: self._aggregate_checkins,
            DataSource.EMPLOYEES: self._aggregate_employees,
            DataSource.DEPARTMENTS: self._aggregate_departments,
            DataSource.OVERTIME: self._aggregate_overtime,
            DataSource.ABSENCES: self._aggregate_absences,
        }

        aggregator = aggregators.get(data_source)
        if aggregator:
            return await aggregator(
                aggregation=aggregation,
                condominio_id=condominio_id,
                period_start=period_start,
                period_end=period_end,
                group_by=group_by,
                filters=filters,
                limit=limit,
            )

        return {"error": f"Data source not implemented: {data_source.value}"}

    async def _aggregate_time_entries(  # pylint: disable=unused-argument
        self,
        aggregation: AggregationType,
        condominio_id: UUID,
        period_start: datetime,
        period_end: datetime,
        group_by: str = None,
        filters: dict = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """Agrega registros de ponto."""

        # Simular dados para demonstração
        if group_by == "date":
            data = []
            current = period_start.date()
            while current <= period_end.date():
                data.append({
                    "date": current.isoformat(),
                    "value": random.randint(50, 200),
                })
                current += timedelta(days=1)
        elif group_by == "department":
            departments = ["TI", "RH", "Financeiro", "Operações", "Comercial"]
            data = [
                {"department": dept, "value": random.randint(20, 100)}
                for dept in departments
            ]
        elif group_by == "employee":
            data = [
                {
                    "employee_id": f"emp_{i}",
                    "employee_name": f"Funcionário {i}",
                    "value": random.randint(160, 200)
                }
                for i in range(1, min((limit or 10) + 1, 11))
            ]
        else:
            data = {"total": random.randint(5000, 10000)}

        return {
            "data_source": "time_entries",
            "aggregation": aggregation.value,
            "group_by": group_by,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "data": data,
            "computed_at": datetime.utcnow().isoformat(),
        }

    async def _aggregate_checkins(  # pylint: disable=unused-argument
        self,
        aggregation: AggregationType,
        condominio_id: UUID,
        period_start: datetime,
        period_end: datetime,
        group_by: str = None,
        filters: dict = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """Agrega check-ins."""

        if group_by == "type":
            data = [
                {"type": "entry", "count": random.randint(500, 1000)},
                {"type": "exit", "count": random.randint(500, 1000)},
                {"type": "break_start", "count": random.randint(200, 500)},
                {"type": "break_end", "count": random.randint(200, 500)},
            ]
        elif group_by == "hour":
            data = [
                {"hour": h, "count": random.randint(10, 100)}
                for h in range(6, 23)
            ]
        else:
            data = {"total": random.randint(2000, 5000)}

        return {
            "data_source": "checkins",
            "aggregation": aggregation.value,
            "group_by": group_by,
            "data": data,
            "computed_at": datetime.utcnow().isoformat(),
        }

    async def _aggregate_employees(  # pylint: disable=unused-argument
        self,
        aggregation: AggregationType,
        condominio_id: UUID,
        period_start: datetime,
        period_end: datetime,
        group_by: str = None,
        filters: dict = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """Agrega funcionários."""

        if group_by == "department":
            data = [
                {"department": "TI", "count": random.randint(10, 30)},
                {"department": "RH", "count": random.randint(5, 15)},
                {"department": "Financeiro", "count": random.randint(5, 20)},
                {"department": "Operações", "count": random.randint(20, 50)},
                {"department": "Comercial", "count": random.randint(10, 25)},
            ]
        elif group_by == "status":
            data = [
                {"status": "active", "count": random.randint(80, 120)},
                {"status": "inactive", "count": random.randint(5, 15)},
                {"status": "vacation", "count": random.randint(3, 10)},
            ]
        else:
            data = {"total": random.randint(80, 150)}

        return {
            "data_source": "employees",
            "aggregation": aggregation.value,
            "group_by": group_by,
            "data": data,
            "computed_at": datetime.utcnow().isoformat(),
        }

    async def _aggregate_departments(  # pylint: disable=unused-argument
        self,
        aggregation: AggregationType,
        condominio_id: UUID,
        period_start: datetime,
        period_end: datetime,
        group_by: str = None,
        filters: dict = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """Agrega departamentos."""

        data = [
            {
                "name": "TI",
                "employee_count": random.randint(10, 30),
                "avg_hours": round(random.uniform(7.5, 9.0), 1),
                "overtime_hours": round(random.uniform(10, 50), 1),
            },
            {
                "name": "RH",
                "employee_count": random.randint(5, 15),
                "avg_hours": round(random.uniform(7.8, 8.5), 1),
                "overtime_hours": round(random.uniform(5, 20), 1),
            },
            {
                "name": "Financeiro",
                "employee_count": random.randint(5, 20),
                "avg_hours": round(random.uniform(8.0, 9.0), 1),
                "overtime_hours": round(random.uniform(15, 40), 1),
            },
        ]

        return {
            "data_source": "departments",
            "aggregation": aggregation.value,
            "data": data,
            "computed_at": datetime.utcnow().isoformat(),
        }

    async def _aggregate_overtime(  # pylint: disable=unused-argument
        self,
        aggregation: AggregationType,
        condominio_id: UUID,
        period_start: datetime,
        period_end: datetime,
        group_by: str = None,
        filters: dict = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """Agrega horas extras."""

        if group_by == "date":
            data = []
            current = period_start.date()
            while current <= period_end.date():
                data.append({
                    "date": current.isoformat(),
                    "hours": round(random.uniform(5, 30), 1),
                    "cost": round(random.uniform(500, 3000), 2),
                })
                current += timedelta(days=1)
        elif group_by == "department":
            data = [
                {"department": "TI", "hours": round(random.uniform(50, 150), 1)},
                {"department": "Operações", "hours": round(random.uniform(100, 200), 1)},
                {"department": "Comercial", "hours": round(random.uniform(30, 80), 1)},
            ]
        else:
            data = {
                "total_hours": round(random.uniform(200, 500), 1),
                "total_cost": round(random.uniform(10000, 30000), 2),
                "avg_per_employee": round(random.uniform(5, 15), 1),
            }

        return {
            "data_source": "overtime",
            "aggregation": aggregation.value,
            "group_by": group_by,
            "data": data,
            "computed_at": datetime.utcnow().isoformat(),
        }

    async def _aggregate_absences(  # pylint: disable=unused-argument
        self,
        aggregation: AggregationType,
        condominio_id: UUID,
        period_start: datetime,
        period_end: datetime,
        group_by: str = None,
        filters: dict = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """Agrega faltas."""

        if group_by == "reason":
            data = [
                {"reason": "medical", "count": random.randint(10, 30)},
                {"reason": "personal", "count": random.randint(5, 15)},
                {"reason": "vacation", "count": random.randint(20, 40)},
                {"reason": "unjustified", "count": random.randint(2, 8)},
            ]
        elif group_by == "department":
            data = [
                {"department": "TI", "days": random.randint(5, 20)},
                {"department": "RH", "days": random.randint(3, 10)},
                {"department": "Operações", "days": random.randint(10, 30)},
            ]
        else:
            data = {
                "total_days": random.randint(30, 80),
                "justified": random.randint(20, 60),
                "unjustified": random.randint(5, 15),
            }

        return {
            "data_source": "absences",
            "aggregation": aggregation.value,
            "group_by": group_by,
            "data": data,
            "computed_at": datetime.utcnow().isoformat(),
        }

    async def get_time_series(  # pylint: disable=unused-argument
        self,
        data_source: DataSource,
        condominio_id: UUID,
        *,
        period_start: datetime,
        period_end: datetime,
        granularity: TimeGranularity = TimeGranularity.DAY,
        metric: str = "count",
    ) -> List[Dict[str, Any]]:
        """Retorna série temporal de uma métrica."""

        result = []

        if granularity == TimeGranularity.HOUR:
            delta = timedelta(hours=1)
        elif granularity == TimeGranularity.WEEK:
            delta = timedelta(weeks=1)
        elif granularity == TimeGranularity.MONTH:
            delta = timedelta(days=30)
        else:
            delta = timedelta(days=1)

        current = period_start
        while current < period_end:
            result.append({
                "timestamp": current.isoformat(),
                "value": random.randint(50, 200),
            })
            current += delta

        return result

    async def compare_periods(
        self,
        data_source: DataSource,
        aggregation: AggregationType,
        condominio_id: UUID,
        *,
        current_start: datetime,
        current_end: datetime,
        previous_start: datetime,
        previous_end: datetime,
    ) -> Dict[str, Any]:
        """Compara métricas entre dois períodos."""
        current = await self.aggregate_data(
            data_source=data_source,
            aggregation=aggregation,
            condominio_id=condominio_id,
            period_start=current_start,
            period_end=current_end,
            use_cache=True,
        )

        previous = await self.aggregate_data(
            data_source=data_source,
            aggregation=aggregation,
            condominio_id=condominio_id,
            period_start=previous_start,
            period_end=previous_end,
            use_cache=True,
        )

        # Calcular variação
        current_value = self._extract_total(current.get("data", {}))
        previous_value = self._extract_total(previous.get("data", {}))

        if previous_value > 0:
            change_percentage = ((current_value - previous_value) / previous_value) * 100
        else:
            change_percentage = 0

        return {
            "current": current,
            "previous": previous,
            "change_absolute": current_value - previous_value,
            "change_percentage": round(change_percentage, 2),
            "trend": (
                "up" if change_percentage > 0 else "down" if change_percentage < 0 else "stable"
            ),
        }

    def _extract_total(self, data) -> float:
        """Extrai valor total dos dados agregados."""
        if isinstance(data, dict):
            return data.get("total", 0)
        if isinstance(data, list):
            return sum(item.get("value", item.get("count", 0)) for item in data)
        return 0
