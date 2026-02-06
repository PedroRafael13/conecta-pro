"""
Forecast Repository - AI Inventory Forecasting

Repository para acesso a dados de previsao de estoque.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session, joinedload

from modules.ai.inventory_forecast.models.forecast import (
    Forecast,
    ForecastResult,
    ForecastStatus,
    ForecastType,
)
from modules.ai.inventory_forecast.models.demand_pattern import (
    DemandPattern,
    PatternType,
    TrendDirection,
)
from modules.ai.inventory_forecast.schemas.forecast_schemas import (
    ForecastCreate,
    ForecastUpdate,
    DemandPatternCreate,
)

logger = logging.getLogger(__name__)


class ForecastRepository:
    """Repository para previsoes de estoque."""

    def __init__(self, db: Session):
        """Inicializa repository."""
        self.db = db

    # ============================================================
    # Forecast CRUD
    # ============================================================

    def create_forecast(self, data: ForecastCreate) -> Forecast:
        """Cria nova previsao."""
        forecast = Forecast(
            product_id=data.product_id,
            product_code=data.product_code,
            product_name=data.product_name,
            forecast_type=data.forecast_type,
            start_date=data.start_date,
            end_date=data.end_date,
            horizon_days=data.horizon_days,
            historical_days=data.historical_days,
            model_type=data.model_type,
            model_params=data.model_params,
            is_automated=data.is_automated,
            notes=data.notes,
            status=ForecastStatus.PENDING,
        )
        self.db.add(forecast)
        self.db.commit()
        self.db.refresh(forecast)
        logger.info(f"Previsao criada: {forecast.id} para produto {data.product_code}")
        return forecast

    def get_forecast(
        self,
        forecast_id: UUID,
        include_results: bool = False
    ) -> Optional[Forecast]:
        """Busca previsao por ID."""
        query = self.db.query(Forecast).filter(Forecast.id == forecast_id)
        if include_results:
            query = query.options(joinedload(Forecast.results))
        return query.first()

    def get_forecasts(
        self,
        product_id: Optional[UUID] = None,
        status: Optional[ForecastStatus] = None,
        forecast_type: Optional[ForecastType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        is_active: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Forecast], int]:
        """Lista previsoes com filtros."""
        query = self.db.query(Forecast)

        if is_active is not None:
            query = query.filter(Forecast.is_active == is_active)

        if product_id:
            query = query.filter(Forecast.product_id == product_id)

        if status:
            query = query.filter(Forecast.status == status)

        if forecast_type:
            query = query.filter(Forecast.forecast_type == forecast_type)

        if start_date:
            query = query.filter(Forecast.start_date >= start_date)

        if end_date:
            query = query.filter(Forecast.end_date <= end_date)

        total = query.count()
        items = (
            query.order_by(desc(Forecast.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def update_forecast(
        self,
        forecast_id: UUID,
        data: ForecastUpdate
    ) -> Optional[Forecast]:
        """Atualiza previsao."""
        forecast = self.get_forecast(forecast_id)
        if not forecast:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(forecast, key, value)

        forecast.updated_at = datetime.utcnow()

        if data.status == ForecastStatus.COMPLETED:
            forecast.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(forecast)
        return forecast

    def delete_forecast(self, forecast_id: UUID) -> bool:
        """Deleta previsao (soft delete)."""
        forecast = self.get_forecast(forecast_id)
        if not forecast:
            return False

        forecast.is_active = False
        forecast.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def get_latest_forecast(
        self,
        product_id: UUID,
        forecast_type: ForecastType = ForecastType.DEMAND
    ) -> Optional[Forecast]:
        """Busca previsao mais recente para produto."""
        return (
            self.db.query(Forecast)
            .filter(
                and_(
                    Forecast.product_id == product_id,
                    Forecast.forecast_type == forecast_type,
                    Forecast.status == ForecastStatus.COMPLETED,
                    Forecast.is_active == True,
                )
            )
            .order_by(desc(Forecast.created_at))
            .first()
        )

    # ============================================================
    # Forecast Results
    # ============================================================

    def add_forecast_results(
        self,
        forecast_id: UUID,
        results: list[dict]
    ) -> list[ForecastResult]:
        """Adiciona resultados a previsao."""
        forecast_results = []
        for result_data in results:
            result = ForecastResult(
                forecast_id=forecast_id,
                **result_data
            )
            self.db.add(result)
            forecast_results.append(result)

        self.db.commit()
        return forecast_results

    def get_forecast_results(
        self,
        forecast_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[ForecastResult]:
        """Busca resultados de previsao."""
        query = self.db.query(ForecastResult).filter(
            ForecastResult.forecast_id == forecast_id
        )

        if start_date:
            query = query.filter(ForecastResult.date >= start_date)

        if end_date:
            query = query.filter(ForecastResult.date <= end_date)

        return query.order_by(ForecastResult.date).all()

    def update_actual_demand(
        self,
        forecast_id: UUID,
        date_value: date,
        actual_demand: float
    ) -> Optional[ForecastResult]:
        """Atualiza demanda real para validacao."""
        result = (
            self.db.query(ForecastResult)
            .filter(
                and_(
                    ForecastResult.forecast_id == forecast_id,
                    ForecastResult.date == date_value,
                )
            )
            .first()
        )

        if result:
            result.actual_demand = actual_demand
            if result.predicted_demand:
                result.variance = actual_demand - result.predicted_demand
                if result.predicted_demand != 0:
                    result.variance_pct = (
                        result.variance / result.predicted_demand
                    ) * 100

            self.db.commit()
            self.db.refresh(result)

        return result

    # ============================================================
    # Demand Patterns
    # ============================================================

    def create_demand_pattern(self, data: DemandPatternCreate) -> DemandPattern:
        """Cria analise de padrao de demanda."""
        pattern = DemandPattern(
            product_id=data.product_id,
            product_code=data.product_code,
            product_name=data.product_name,
            analysis_start_date=data.analysis_start_date,
            analysis_end_date=data.analysis_end_date,
        )
        self.db.add(pattern)
        self.db.commit()
        self.db.refresh(pattern)
        return pattern

    def get_demand_pattern(self, pattern_id: UUID) -> Optional[DemandPattern]:
        """Busca padrao por ID."""
        return self.db.query(DemandPattern).filter(
            DemandPattern.id == pattern_id
        ).first()

    def get_latest_demand_pattern(
        self,
        product_id: UUID
    ) -> Optional[DemandPattern]:
        """Busca padrao mais recente para produto."""
        return (
            self.db.query(DemandPattern)
            .filter(
                and_(
                    DemandPattern.product_id == product_id,
                    DemandPattern.is_active == True,
                )
            )
            .order_by(desc(DemandPattern.created_at))
            .first()
        )

    def get_demand_patterns(
        self,
        pattern_type: Optional[PatternType] = None,
        trend_direction: Optional[TrendDirection] = None,
        min_predictability: Optional[float] = None,
        is_active: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[DemandPattern], int]:
        """Lista padroes de demanda."""
        query = self.db.query(DemandPattern)

        if is_active is not None:
            query = query.filter(DemandPattern.is_active == is_active)

        if pattern_type:
            query = query.filter(DemandPattern.pattern_type == pattern_type)

        if trend_direction:
            query = query.filter(DemandPattern.trend_direction == trend_direction)

        if min_predictability:
            query = query.filter(
                DemandPattern.predictability_score >= min_predictability
            )

        total = query.count()
        items = (
            query.order_by(desc(DemandPattern.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def update_demand_pattern(
        self,
        pattern_id: UUID,
        data: dict
    ) -> Optional[DemandPattern]:
        """Atualiza padrao de demanda."""
        pattern = self.get_demand_pattern(pattern_id)
        if not pattern:
            return None

        for key, value in data.items():
            if hasattr(pattern, key):
                setattr(pattern, key, value)

        pattern.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pattern)
        return pattern

    # ============================================================
    # Analytics
    # ============================================================

    def get_forecasts_needing_update(self, days_old: int = 7) -> list[Forecast]:
        """Busca previsoes que precisam de atualizacao."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        return (
            self.db.query(Forecast)
            .filter(
                and_(
                    Forecast.is_active == True,
                    Forecast.status == ForecastStatus.COMPLETED,
                    or_(
                        Forecast.updated_at < cutoff_date,
                        Forecast.expires_at < datetime.utcnow(),
                    ),
                )
            )
            .all()
        )

    def get_forecast_accuracy_stats(
        self,
        product_id: Optional[UUID] = None,
        days: int = 30
    ) -> dict:
        """Calcula estatisticas de acuracidade das previsoes."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        query = (
            self.db.query(
                func.avg(ForecastResult.variance_pct).label("avg_variance_pct"),
                func.avg(func.abs(ForecastResult.variance_pct)).label("avg_abs_variance"),
                func.count(ForecastResult.id).label("total_predictions"),
                func.count(ForecastResult.actual_demand).label("validated_predictions"),
            )
            .join(Forecast)
            .filter(
                and_(
                    Forecast.is_active == True,
                    ForecastResult.created_at >= cutoff,
                )
            )
        )

        if product_id:
            query = query.filter(Forecast.product_id == product_id)

        result = query.first()

        return {
            "avg_variance_pct": float(result.avg_variance_pct or 0),
            "avg_abs_variance": float(result.avg_abs_variance or 0),
            "total_predictions": result.total_predictions,
            "validated_predictions": result.validated_predictions,
            "accuracy_rate": (
                (1 - abs(result.avg_variance_pct or 0) / 100) * 100
                if result.avg_variance_pct else None
            ),
        }

    def count_products_by_trend(self) -> dict:
        """Conta produtos por direcao de tendencia."""
        results = (
            self.db.query(
                DemandPattern.trend_direction,
                func.count(DemandPattern.id).label("count"),
            )
            .filter(DemandPattern.is_active == True)
            .group_by(DemandPattern.trend_direction)
            .all()
        )

        return {str(r.trend_direction.value): r.count for r in results}
