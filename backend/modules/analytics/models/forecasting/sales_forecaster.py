"""Modelo de previsão de vendas com séries temporais."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sqlalchemy.ext.asyncio import AsyncSession

from modules.analytics.ml.registry.model_registry import (
    ModelFramework,
    ModelRegistry,
    ModelStage,
    ModelType,
)

logger = logging.getLogger(__name__)


class ForecastGranularity(Enum):
    """Granularidade da previsão."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class SeasonalityType(Enum):
    """Tipos de sazonalidade."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class TrendType(Enum):
    """Tipos de tendência."""

    FLAT = "flat"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    POLYNOMIAL = "polynomial"


@dataclass
class ForecastPoint:
    """Ponto individual de previsão."""

    date: datetime
    value: float
    lower_bound: float
    upper_bound: float
    confidence: float


@dataclass
class SeasonalComponent:
    """Componente sazonal identificado."""

    type: SeasonalityType
    period: int
    strength: float
    pattern: list[float]


@dataclass
class TrendComponent:
    """Componente de tendência identificado."""

    type: TrendType
    slope: float
    intercept: float
    r_squared: float


@dataclass
class SalesForecast:
    """Resultado da previsão de vendas."""

    id: UUID
    forecast_type: str
    granularity: ForecastGranularity
    start_date: datetime
    end_date: datetime
    predictions: list[ForecastPoint]
    total_forecast: float
    trend: TrendComponent
    seasonality: list[SeasonalComponent]
    accuracy_metrics: dict[str, float]
    insights: list[str]
    model_version: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ForecastComparison:
    """Comparação entre previsão e realizado."""

    period: str
    forecasted: float
    actual: float
    variance: float
    variance_pct: float
    accuracy: float


class SalesForecaster:
    """
    Sistema de previsão de vendas.

    Funcionalidades:
    - Previsão de receita/vendas
    - Decomposição de séries temporais
    - Identificação de sazonalidade
    - Análise de tendência
    - Cenários what-if
    - Comparação forecast vs realizado
    """

    def __init__(
        self,
        model_registry: Optional[ModelRegistry] = None,
    ) -> None:
        """
        Inicializa o forecaster.

        Args:
            model_registry: Registry de modelos
        """
        self.model_registry = model_registry or ModelRegistry()
        self._model = None
        self._scaler = StandardScaler()

    async def forecast(
        self,
        db: AsyncSession,
        periods: int = 30,
        granularity: ForecastGranularity = ForecastGranularity.DAILY,
        entity_type: str = "revenue",
        entity_id: Optional[str] = None,
        confidence_level: float = 0.95,
    ) -> SalesForecast:
        """
        Gera previsão de vendas.

        Args:
            db: Sessão do banco
            periods: Número de períodos a prever
            granularity: Granularidade da previsão
            entity_type: Tipo de entidade (revenue, units, etc.)
            entity_id: ID específico (condomínio, produto, etc.)
            confidence_level: Nível de confiança para intervalos

        Returns:
            SalesForecast com previsões
        """
        logger.info(f"Gerando forecast: {entity_type}, {periods} {granularity.value}")

        # Obter dados históricos
        historical_data = await self._get_historical_data(
            db, entity_type, entity_id, granularity
        )

        if len(historical_data) < 10:
            logger.warning("Dados insuficientes, usando previsão simplificada")
            return self._simple_forecast(periods, granularity, entity_type)

        # Decompor série temporal
        trend = self._detect_trend(historical_data)
        seasonality = self._detect_seasonality(historical_data, granularity)

        # Preparar features
        X, y = self._prepare_features(historical_data, granularity)

        # Treinar ou carregar modelo
        model = self._get_or_train_model(X, y)

        # Gerar previsões
        predictions = self._generate_predictions(
            model, historical_data, periods, granularity, confidence_level
        )

        # Calcular métricas de acurácia
        accuracy_metrics = self._calculate_accuracy_metrics(
            historical_data, model, X, y
        )

        # Gerar insights
        insights = self._generate_insights(
            trend, seasonality, predictions, historical_data
        )

        return SalesForecast(
            id=uuid4(),
            forecast_type=entity_type,
            granularity=granularity,
            start_date=predictions[0].date if predictions else datetime.utcnow(),
            end_date=predictions[-1].date if predictions else datetime.utcnow(),
            predictions=predictions,
            total_forecast=sum(p.value for p in predictions),
            trend=trend,
            seasonality=seasonality,
            accuracy_metrics=accuracy_metrics,
            insights=insights,
            model_version="1.0.0",
        )

    async def forecast_scenarios(
        self,
        db: AsyncSession,
        periods: int = 30,
        scenarios: list[dict[str, Any]] = None,
    ) -> dict[str, SalesForecast]:
        """
        Gera múltiplos cenários de previsão.

        Args:
            db: Sessão do banco
            periods: Períodos a prever
            scenarios: Lista de cenários com ajustes

        Returns:
            Dict com forecasts por cenário
        """
        if scenarios is None:
            scenarios = [
                {"name": "pessimistic", "growth_adj": -0.2},
                {"name": "baseline", "growth_adj": 0.0},
                {"name": "optimistic", "growth_adj": 0.2},
            ]

        results = {}
        base_forecast = await self.forecast(db, periods)

        for scenario in scenarios:
            name = scenario.get("name", "custom")
            growth_adj = scenario.get("growth_adj", 0.0)

            # Ajustar previsões
            adjusted_predictions = []
            for pred in base_forecast.predictions:
                adj_value = pred.value * (1 + growth_adj)
                adj_lower = pred.lower_bound * (1 + growth_adj)
                adj_upper = pred.upper_bound * (1 + growth_adj)

                adjusted_predictions.append(ForecastPoint(
                    date=pred.date,
                    value=adj_value,
                    lower_bound=adj_lower,
                    upper_bound=adj_upper,
                    confidence=pred.confidence,
                ))

            results[name] = SalesForecast(
                id=uuid4(),
                forecast_type=base_forecast.forecast_type,
                granularity=base_forecast.granularity,
                start_date=base_forecast.start_date,
                end_date=base_forecast.end_date,
                predictions=adjusted_predictions,
                total_forecast=sum(p.value for p in adjusted_predictions),
                trend=base_forecast.trend,
                seasonality=base_forecast.seasonality,
                accuracy_metrics=base_forecast.accuracy_metrics,
                insights=[f"Cenário {name}: ajuste de {growth_adj*100:+.0f}%"],
                model_version=base_forecast.model_version,
            )

        return results

    async def compare_forecast_vs_actual(
        self,
        db: AsyncSession,
        forecast_id: UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> list[ForecastComparison]:
        """
        Compara previsão com valores realizados.

        Args:
            db: Sessão do banco
            forecast_id: ID da previsão
            start_date: Data inicial
            end_date: Data final

        Returns:
            Lista de comparações
        """
        # Simulação - em produção buscaria do banco
        comparisons = []
        current = start_date

        while current <= end_date:
            forecasted = np.random.uniform(8000, 12000)
            actual = forecasted * np.random.uniform(0.85, 1.15)
            variance = actual - forecasted
            variance_pct = (variance / forecasted) * 100

            comparisons.append(ForecastComparison(
                period=current.strftime("%Y-%m-%d"),
                forecasted=round(forecasted, 2),
                actual=round(actual, 2),
                variance=round(variance, 2),
                variance_pct=round(variance_pct, 2),
                accuracy=round(100 - abs(variance_pct), 2),
            ))

            current += timedelta(days=1)

        return comparisons

    async def get_forecast_accuracy_report(
        self,
        db: AsyncSession,
        lookback_days: int = 90,
    ) -> dict[str, Any]:
        """
        Gera relatório de acurácia das previsões.

        Args:
            db: Sessão do banco
            lookback_days: Dias para análise

        Returns:
            Relatório de acurácia
        """
        # Em produção, buscaria comparações históricas
        # Simulação para desenvolvimento

        return {
            "period_start": (datetime.utcnow() - timedelta(days=lookback_days)).isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "total_forecasts": 90,
            "overall_accuracy": 87.5,
            "mape": 12.5,  # Mean Absolute Percentage Error
            "rmse": 1250.0,  # Root Mean Square Error
            "bias": 2.3,  # Tendency to over/under forecast
            "accuracy_by_granularity": {
                "daily": 82.3,
                "weekly": 88.5,
                "monthly": 92.1,
            },
            "best_performing_period": "weekly",
            "worst_performing_period": "daily",
            "recommendations": [
                "Previsões semanais têm melhor acurácia",
                "Considere fatores externos para previsões diárias",
                "Modelo tende a subestimar fins de semana",
            ],
        }

    async def _get_historical_data(
        self,
        db: AsyncSession,
        entity_type: str,
        entity_id: Optional[str],
        granularity: ForecastGranularity,
    ) -> pd.DataFrame:
        """Obtém dados históricos para treinamento."""
        # Em produção, query ao banco
        # Simulação de 365 dias de dados

        np.random.seed(42)
        days = 365
        dates = pd.date_range(
            end=datetime.utcnow(),
            periods=days,
            freq="D",
        )

        # Base value
        base = 10000

        # Tendência
        trend = np.linspace(0, 2000, days)

        # Sazonalidade semanal
        weekly_pattern = np.array([0.8, 0.9, 1.0, 1.0, 1.1, 1.2, 0.9])
        weekly = np.tile(weekly_pattern, days // 7 + 1)[:days] * 1000

        # Sazonalidade mensal
        monthly_pattern = np.sin(np.linspace(0, 12 * np.pi, days)) * 1500

        # Ruído
        noise = np.random.normal(0, 500, days)

        values = base + trend + weekly + monthly_pattern + noise
        values = np.maximum(values, 0)

        return pd.DataFrame({
            "date": dates,
            "value": values,
        })

    def _detect_trend(self, data: pd.DataFrame) -> TrendComponent:
        """Detecta componente de tendência."""
        X = np.arange(len(data)).reshape(-1, 1)
        y = data["value"].values

        model = LinearRegression()
        model.fit(X, y)

        r_squared = model.score(X, y)
        slope = model.coef_[0]

        # Classificar tipo de tendência
        if abs(slope) < 1:
            trend_type = TrendType.FLAT
        elif slope > 0:
            trend_type = TrendType.LINEAR
        else:
            trend_type = TrendType.LINEAR

        return TrendComponent(
            type=trend_type,
            slope=round(slope, 4),
            intercept=round(model.intercept_, 2),
            r_squared=round(r_squared, 4),
        )

    def _detect_seasonality(
        self,
        data: pd.DataFrame,
        granularity: ForecastGranularity,
    ) -> list[SeasonalComponent]:
        """Detecta componentes sazonais."""
        seasonality = []
        values = data["value"].values

        # Sazonalidade semanal (para dados diários)
        if granularity == ForecastGranularity.DAILY and len(values) >= 14:
            weekly_pattern = []
            for i in range(7):
                day_values = values[i::7]
                weekly_pattern.append(np.mean(day_values))

            # Normalizar
            mean_val = np.mean(weekly_pattern)
            weekly_pattern = [v / mean_val for v in weekly_pattern]

            # Calcular força
            strength = np.std(weekly_pattern) / np.mean(weekly_pattern)

            if strength > 0.05:
                seasonality.append(SeasonalComponent(
                    type=SeasonalityType.WEEKLY,
                    period=7,
                    strength=round(strength, 4),
                    pattern=weekly_pattern,
                ))

        # Sazonalidade mensal
        if len(values) >= 60:
            monthly_pattern = []
            days_per_month = 30
            for i in range(12):
                start = i * days_per_month
                end = start + days_per_month
                if end <= len(values):
                    monthly_pattern.append(np.mean(values[start:end]))

            if len(monthly_pattern) >= 6:
                mean_val = np.mean(monthly_pattern)
                monthly_pattern = [v / mean_val for v in monthly_pattern]
                strength = np.std(monthly_pattern) / np.mean(monthly_pattern)

                if strength > 0.05:
                    seasonality.append(SeasonalComponent(
                        type=SeasonalityType.MONTHLY,
                        period=30,
                        strength=round(strength, 4),
                        pattern=monthly_pattern,
                    ))

        return seasonality

    def _prepare_features(
        self,
        data: pd.DataFrame,
        granularity: ForecastGranularity,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Prepara features para o modelo."""
        df = data.copy()
        df["date"] = pd.to_datetime(df["date"])

        # Features temporais
        df["day_of_week"] = df["date"].dt.dayofweek
        df["day_of_month"] = df["date"].dt.day
        df["month"] = df["date"].dt.month
        df["quarter"] = df["date"].dt.quarter
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

        # Features de lag
        for lag in [1, 7, 14, 30]:
            df[f"lag_{lag}"] = df["value"].shift(lag)

        # Features de rolling
        for window in [7, 14, 30]:
            df[f"rolling_mean_{window}"] = df["value"].rolling(window).mean()
            df[f"rolling_std_{window}"] = df["value"].rolling(window).std()

        # Remover NaN
        df = df.dropna()

        feature_cols = [
            "day_of_week", "day_of_month", "month", "quarter", "is_weekend",
            "lag_1", "lag_7", "lag_14", "lag_30",
            "rolling_mean_7", "rolling_mean_14", "rolling_mean_30",
            "rolling_std_7", "rolling_std_14", "rolling_std_30",
        ]

        X = df[feature_cols].values
        y = df["value"].values

        return X, y

    def _get_or_train_model(
        self,
        X: np.ndarray,
        y: np.ndarray,
    ) -> Any:
        """Obtém ou treina modelo de previsão."""
        # Tentar carregar modelo existente
        model = self.model_registry.get_production_model("sales_forecaster")

        if model is None:
            # Treinar novo modelo
            model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42,
            )

            # Escalar features
            X_scaled = self._scaler.fit_transform(X)
            model.fit(X_scaled, y)

            logger.info("Modelo de forecast treinado")

        return model

    def _generate_predictions(
        self,
        model: Any,
        historical_data: pd.DataFrame,
        periods: int,
        granularity: ForecastGranularity,
        confidence_level: float,
    ) -> list[ForecastPoint]:
        """Gera pontos de previsão."""
        predictions = []
        last_date = historical_data["date"].max()
        last_values = historical_data["value"].tail(30).values

        # Parâmetros para intervalo de confiança
        z_score = 1.96 if confidence_level == 0.95 else 1.645
        historical_std = np.std(historical_data["value"])

        for i in range(periods):
            # Determinar próxima data
            if granularity == ForecastGranularity.DAILY:
                next_date = last_date + timedelta(days=i + 1)
            elif granularity == ForecastGranularity.WEEKLY:
                next_date = last_date + timedelta(weeks=i + 1)
            elif granularity == ForecastGranularity.MONTHLY:
                next_date = last_date + timedelta(days=30 * (i + 1))
            else:
                next_date = last_date + timedelta(days=i + 1)

            # Criar features para previsão
            features = self._create_forecast_features(
                next_date, last_values, i
            )

            # Predizer
            X_scaled = self._scaler.transform([features])
            pred_value = model.predict(X_scaled)[0]

            # Intervalo de confiança (aumenta com distância)
            uncertainty = historical_std * (1 + 0.1 * i) * z_score

            predictions.append(ForecastPoint(
                date=next_date,
                value=round(max(0, pred_value), 2),
                lower_bound=round(max(0, pred_value - uncertainty), 2),
                upper_bound=round(pred_value + uncertainty, 2),
                confidence=round(confidence_level - 0.01 * i, 4),
            ))

            # Atualizar últimos valores
            last_values = np.append(last_values[1:], pred_value)

        return predictions

    def _create_forecast_features(
        self,
        date: datetime,
        last_values: np.ndarray,
        step: int,
    ) -> list[float]:
        """Cria features para um ponto de previsão."""
        return [
            date.weekday(),  # day_of_week
            date.day,  # day_of_month
            date.month,  # month
            (date.month - 1) // 3 + 1,  # quarter
            1 if date.weekday() in [5, 6] else 0,  # is_weekend
            last_values[-1] if len(last_values) > 0 else 0,  # lag_1
            last_values[-7] if len(last_values) >= 7 else last_values[-1],  # lag_7
            last_values[-14] if len(last_values) >= 14 else last_values[-1],  # lag_14
            last_values[-min(30, len(last_values))],  # lag_30
            np.mean(last_values[-7:]) if len(last_values) >= 7 else np.mean(last_values),
            np.mean(last_values[-14:]) if len(last_values) >= 14 else np.mean(last_values),
            np.mean(last_values),  # rolling_mean_30
            np.std(last_values[-7:]) if len(last_values) >= 7 else np.std(last_values),
            np.std(last_values[-14:]) if len(last_values) >= 14 else np.std(last_values),
            np.std(last_values),  # rolling_std_30
        ]

    def _calculate_accuracy_metrics(
        self,
        data: pd.DataFrame,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
    ) -> dict[str, float]:
        """Calcula métricas de acurácia do modelo."""
        # Holdout validation
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        X_test_scaled = self._scaler.transform(X_test)
        y_pred = model.predict(X_test_scaled)

        # Métricas
        mse = np.mean((y_test - y_pred) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y_test - y_pred))
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

        # R²
        ss_res = np.sum((y_test - y_pred) ** 2)
        ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
        r2 = 1 - (ss_res / ss_tot)

        return {
            "mse": round(mse, 2),
            "rmse": round(rmse, 2),
            "mae": round(mae, 2),
            "mape": round(mape, 2),
            "r2": round(r2, 4),
            "accuracy": round(100 - mape, 2),
        }

    def _generate_insights(
        self,
        trend: TrendComponent,
        seasonality: list[SeasonalComponent],
        predictions: list[ForecastPoint],
        historical_data: pd.DataFrame,
    ) -> list[str]:
        """Gera insights sobre a previsão."""
        insights = []

        # Insight sobre tendência
        if trend.type == TrendType.LINEAR and trend.slope > 0:
            daily_growth = trend.slope
            monthly_growth = daily_growth * 30
            insights.append(
                f"Tendência de crescimento de R$ {monthly_growth:,.0f}/mês"
            )
        elif trend.type == TrendType.LINEAR and trend.slope < 0:
            insights.append("Tendência de queda identificada - avaliar ações")

        # Insight sobre sazonalidade
        for season in seasonality:
            if season.type == SeasonalityType.WEEKLY:
                max_day = np.argmax(season.pattern)
                days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
                insights.append(f"Pico de vendas: {days[max_day]}")

        # Insight sobre previsão total
        if predictions:
            total = sum(p.value for p in predictions)
            avg = total / len(predictions)
            historical_avg = historical_data["value"].mean()

            if avg > historical_avg * 1.1:
                insights.append(
                    f"Previsão {((avg/historical_avg)-1)*100:.0f}% acima da média histórica"
                )
            elif avg < historical_avg * 0.9:
                insights.append("Previsão abaixo da média - revisar estratégias")

        # Insight sobre confiança
        avg_confidence = np.mean([p.confidence for p in predictions])
        if avg_confidence < 0.8:
            insights.append("Incerteza alta - recomenda-se cenários alternativos")

        return insights

    def _simple_forecast(
        self,
        periods: int,
        granularity: ForecastGranularity,
        entity_type: str,
    ) -> SalesForecast:
        """Previsão simplificada quando dados são insuficientes."""
        base_value = 10000
        predictions = []
        start_date = datetime.utcnow()

        for i in range(periods):
            if granularity == ForecastGranularity.DAILY:
                date = start_date + timedelta(days=i)
            else:
                date = start_date + timedelta(days=i * 7)

            value = base_value * (1 + np.random.uniform(-0.1, 0.1))

            predictions.append(ForecastPoint(
                date=date,
                value=round(value, 2),
                lower_bound=round(value * 0.8, 2),
                upper_bound=round(value * 1.2, 2),
                confidence=0.6,
            ))

        return SalesForecast(
            id=uuid4(),
            forecast_type=entity_type,
            granularity=granularity,
            start_date=predictions[0].date,
            end_date=predictions[-1].date,
            predictions=predictions,
            total_forecast=sum(p.value for p in predictions),
            trend=TrendComponent(
                type=TrendType.FLAT,
                slope=0,
                intercept=base_value,
                r_squared=0,
            ),
            seasonality=[],
            accuracy_metrics={"accuracy": 60.0, "confidence": "low"},
            insights=["Dados insuficientes para previsão precisa"],
            model_version="simple_v1",
        )
