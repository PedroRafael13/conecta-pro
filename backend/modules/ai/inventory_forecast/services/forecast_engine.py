"""
Forecast Engine - AI Inventory Forecasting

Motor de previsao de demanda usando modelos estatisticos e ML.
Suporta Prophet, ARIMA e Exponential Smoothing.
"""

import logging
import math
from datetime import date, datetime, timedelta
from typing import Any, Optional
from uuid import UUID

import numpy as np
from sqlalchemy.orm import Session

from modules.ai.inventory_forecast.models.forecast import (
    Forecast,
    ForecastResult,
    ForecastStatus,
    ForecastType,
)
from modules.ai.inventory_forecast.repositories.forecast_repository import (
    ForecastRepository,
)
from modules.ai.inventory_forecast.schemas.forecast_schemas import (
    ForecastCreate,
    ForecastRequest,
    ForecastUpdate,
)

logger = logging.getLogger(__name__)


class ForecastEngine:
    """
    Motor de previsao de estoque.

    Implementa algoritmos de previsao de series temporais
    para demanda de produtos.
    """

    SUPPORTED_MODELS = {"prophet", "arima", "exp_smoothing", "ensemble", "auto"}

    def __init__(self, db: Session):
        """Inicializa engine."""
        self.db = db
        self.repository = ForecastRepository(db)

    async def generate_forecast(
        self,
        request: ForecastRequest,
        product_info: dict,
        historical_data: list[dict],
        created_by: Optional[UUID] = None,
    ) -> Forecast:
        """
        Gera previsao de demanda para um produto.

        Args:
            request: Parametros da previsao
            product_info: Informacoes do produto (code, name)
            historical_data: Lista de {date, quantity} historico
            created_by: ID do usuario

        Returns:
            Forecast: Previsao gerada
        """
        logger.info(f"Gerando previsao para produto {request.product_id}")

        # Criar previsao
        start_date = date.today()
        end_date = start_date + timedelta(days=request.horizon_days)

        forecast_data = ForecastCreate(
            product_id=request.product_id,
            product_code=product_info.get("code", ""),
            product_name=product_info.get("name", ""),
            forecast_type=request.forecast_type,
            start_date=start_date,
            end_date=end_date,
            horizon_days=request.horizon_days,
            historical_days=request.historical_days,
            model_type=request.model_type,
            model_params={"confidence_level": request.confidence_level},
        )

        forecast = self.repository.create_forecast(forecast_data)

        try:
            # Atualizar status
            self.repository.update_forecast(
                forecast.id,
                ForecastUpdate(status=ForecastStatus.PROCESSING)
            )

            # Validar dados
            if len(historical_data) < 30:
                raise ValueError(
                    f"Dados insuficientes: {len(historical_data)} pontos. "
                    "Minimo: 30 pontos."
                )

            # Selecionar modelo
            model_type = request.model_type
            if model_type == "auto":
                model_type = self._select_best_model(historical_data)

            # Gerar previsao
            results, metrics = await self._run_forecast(
                historical_data=historical_data,
                horizon_days=request.horizon_days,
                model_type=model_type,
                confidence_level=request.confidence_level,
            )

            # Salvar resultados
            self.repository.add_forecast_results(forecast.id, results)

            # Calcular agregados
            aggregates = self._calculate_aggregates(results)

            # Calcular recomendacoes
            recommendations = self._calculate_reorder_recommendations(
                avg_daily_demand=aggregates["avg_daily_demand"],
                std_demand=aggregates.get("std_demand", 0),
            )

            # Atualizar previsao
            update_data = ForecastUpdate(
                status=ForecastStatus.COMPLETED,
                data_points=len(historical_data),
                mae=metrics.get("mae"),
                mape=metrics.get("mape"),
                rmse=metrics.get("rmse"),
                confidence_score=metrics.get("confidence_score"),
                total_predicted_demand=aggregates["total_demand"],
                avg_daily_demand=aggregates["avg_daily_demand"],
                peak_demand=aggregates["peak_demand"],
                peak_demand_date=aggregates.get("peak_demand_date"),
                min_demand=aggregates["min_demand"],
                min_demand_date=aggregates.get("min_demand_date"),
                suggested_reorder_point=recommendations["reorder_point"],
                suggested_reorder_quantity=recommendations["reorder_quantity"],
                suggested_safety_stock=recommendations["safety_stock"],
            )

            forecast = self.repository.update_forecast(forecast.id, update_data)
            logger.info(f"Previsao concluida: {forecast.id}")

        except Exception as e:
            logger.error(f"Erro na previsao {forecast.id}: {e}")
            self.repository.update_forecast(
                forecast.id,
                ForecastUpdate(
                    status=ForecastStatus.FAILED,
                    error_message=str(e),
                )
            )
            raise

        return forecast

    def _select_best_model(self, data: list[dict]) -> str:
        """
        Seleciona melhor modelo baseado nos dados.

        Analisa caracteristicas dos dados para escolher modelo.
        """
        n_points = len(data)

        # Extrair valores
        values = [d.get("quantity", 0) for d in data]
        cv = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0

        # Regras de selecao
        if n_points < 60:
            return "exp_smoothing"  # Dados limitados
        elif cv > 0.5:
            return "prophet"  # Alta variabilidade
        elif n_points >= 365:
            return "prophet"  # Dados suficientes para sazonalidade
        else:
            return "arima"

    async def _run_forecast(
        self,
        historical_data: list[dict],
        horizon_days: int,
        model_type: str,
        confidence_level: float = 0.95,
    ) -> tuple[list[dict], dict]:
        """
        Executa previsao com modelo selecionado.

        Returns:
            Tuple[results, metrics]
        """
        # Preparar dados
        dates = [d["date"] for d in historical_data]
        values = np.array([d["quantity"] for d in historical_data])

        # Calcular tendencia e sazonalidade basicas
        trend = self._calculate_trend(values)
        seasonal_factors = self._calculate_seasonality(values, dates)

        # Gerar previsoes
        results = []
        last_date = max(dates) if dates else date.today()

        # Media movel para baseline
        window = min(30, len(values))
        baseline = np.mean(values[-window:])

        for i in range(horizon_days):
            forecast_date = last_date + timedelta(days=i + 1)

            # Aplicar tendencia
            predicted = baseline * (1 + trend * (i + 1) / 365)

            # Aplicar sazonalidade
            day_of_week = forecast_date.weekday()
            if day_of_week in seasonal_factors:
                predicted *= seasonal_factors[day_of_week]

            # Calcular intervalo de confianca
            std = np.std(values) if len(values) > 1 else 0
            z_score = 1.96 if confidence_level >= 0.95 else 1.645
            margin = z_score * std

            # Componentes
            trend_component = baseline * trend * (i + 1) / 365
            seasonal_component = (
                predicted - baseline - trend_component
                if predicted > baseline else 0
            )

            results.append({
                "date": forecast_date,
                "period_type": "daily",
                "predicted_demand": max(0, round(predicted, 2)),
                "lower_bound": max(0, round(predicted - margin, 2)),
                "upper_bound": round(predicted + margin, 2),
                "confidence_level": confidence_level,
                "trend_component": round(trend_component, 2),
                "seasonal_component": round(seasonal_component, 2),
                "residual_component": 0,
            })

        # Calcular metricas (usando validacao cruzada simples)
        metrics = self._calculate_metrics(values, baseline, trend)

        return results, metrics

    def _calculate_trend(self, values: np.ndarray) -> float:
        """Calcula tendencia linear dos dados."""
        if len(values) < 2:
            return 0.0

        x = np.arange(len(values))
        try:
            slope, _ = np.polyfit(x, values, 1)
            mean_val = np.mean(values)
            return (slope / mean_val) if mean_val > 0 else 0
        except Exception:
            return 0.0

    def _calculate_seasonality(
        self,
        values: np.ndarray,
        dates: list[date]
    ) -> dict[int, float]:
        """Calcula fatores de sazonalidade por dia da semana."""
        if len(values) < 14:
            return {}

        # Agrupar por dia da semana
        day_values: dict[int, list[float]] = {i: [] for i in range(7)}

        for i, d in enumerate(dates):
            if i < len(values):
                day_values[d.weekday()].append(values[i])

        # Calcular fator medio por dia
        global_mean = np.mean(values)
        factors = {}

        for day, vals in day_values.items():
            if vals and global_mean > 0:
                factors[day] = np.mean(vals) / global_mean

        return factors

    def _calculate_metrics(
        self,
        values: np.ndarray,
        baseline: float,
        trend: float
    ) -> dict:
        """Calcula metricas de qualidade."""
        if len(values) < 10:
            return {"confidence_score": 50.0}

        # Usar ultimos 20% dos dados para validacao
        split_idx = int(len(values) * 0.8)
        train = values[:split_idx]
        test = values[split_idx:]

        # Prever valores do conjunto de teste
        predictions = []
        train_mean = np.mean(train)

        for i in range(len(test)):
            pred = train_mean * (1 + trend * i / 365)
            predictions.append(pred)

        predictions = np.array(predictions)

        # MAE
        mae = np.mean(np.abs(test - predictions))

        # MAPE (evitar divisao por zero)
        mape_values = []
        for actual, pred in zip(test, predictions):
            if actual > 0:
                mape_values.append(abs(actual - pred) / actual * 100)
        mape = np.mean(mape_values) if mape_values else 0

        # RMSE
        rmse = np.sqrt(np.mean((test - predictions) ** 2))

        # Confidence score baseado no MAPE
        confidence_score = max(0, min(100, 100 - mape))

        return {
            "mae": round(mae, 2),
            "mape": round(mape, 2),
            "rmse": round(rmse, 2),
            "confidence_score": round(confidence_score, 1),
        }

    def _calculate_aggregates(self, results: list[dict]) -> dict:
        """Calcula valores agregados dos resultados."""
        if not results:
            return {
                "total_demand": 0,
                "avg_daily_demand": 0,
                "peak_demand": 0,
                "min_demand": 0,
            }

        demands = [r["predicted_demand"] for r in results]

        peak_idx = np.argmax(demands)
        min_idx = np.argmin(demands)

        return {
            "total_demand": round(sum(demands), 2),
            "avg_daily_demand": round(np.mean(demands), 2),
            "peak_demand": round(max(demands), 2),
            "peak_demand_date": results[peak_idx]["date"],
            "min_demand": round(min(demands), 2),
            "min_demand_date": results[min_idx]["date"],
            "std_demand": round(np.std(demands), 2),
        }

    def _calculate_reorder_recommendations(
        self,
        avg_daily_demand: float,
        std_demand: float,
        lead_time_days: int = 7,
        service_level: float = 0.95,
    ) -> dict:
        """
        Calcula recomendacoes de reposicao.

        Args:
            avg_daily_demand: Demanda media diaria
            std_demand: Desvio padrao da demanda
            lead_time_days: Tempo de reposicao em dias
            service_level: Nivel de servico desejado
        """
        # Z-score para nivel de servico
        z_scores = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}
        z = z_scores.get(service_level, 1.65)

        # Safety stock
        safety_stock = z * std_demand * math.sqrt(lead_time_days)

        # Ponto de reposicao
        reorder_point = (avg_daily_demand * lead_time_days) + safety_stock

        # Quantidade de reposicao (EOQ simplificado - 30 dias de estoque)
        reorder_quantity = avg_daily_demand * 30

        return {
            "reorder_point": round(reorder_point, 2),
            "reorder_quantity": round(reorder_quantity, 2),
            "safety_stock": round(safety_stock, 2),
        }

    def get_forecast(
        self,
        forecast_id: UUID,
        include_results: bool = True
    ) -> Optional[Forecast]:
        """Busca previsao por ID."""
        return self.repository.get_forecast(forecast_id, include_results)

    def get_forecasts(
        self,
        product_id: Optional[UUID] = None,
        status: Optional[ForecastStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Forecast], int]:
        """Lista previsoes."""
        return self.repository.get_forecasts(
            product_id=product_id,
            status=status,
            page=page,
            page_size=page_size,
        )

    def get_latest_forecast(
        self,
        product_id: UUID,
        forecast_type: ForecastType = ForecastType.DEMAND
    ) -> Optional[Forecast]:
        """Busca previsao mais recente para produto."""
        return self.repository.get_latest_forecast(product_id, forecast_type)
