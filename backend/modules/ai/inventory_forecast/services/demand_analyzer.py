"""
Demand Analyzer - AI Inventory Forecasting

Analisa padroes de demanda para identificar sazonalidade,
tendencias e anomalias.
"""

import logging
from collections import defaultdict
from datetime import date
from uuid import UUID

import numpy as np
from sqlalchemy.orm import Session

from modules.ai.inventory_forecast.models.demand_pattern import (
    DemandPattern,
    PatternType,
    SeasonalityType,
    TrendDirection,
)
from modules.ai.inventory_forecast.repositories.forecast_repository import (
    ForecastRepository,
)
from modules.ai.inventory_forecast.schemas.forecast_schemas import (
    DemandPatternCreate,
)

logger = logging.getLogger(__name__)


class DemandAnalyzer:
    """
    Analisador de padroes de demanda.

    Identifica padroes, sazonalidade, tendencias e anomalias
    nos dados historicos de demanda.
    """

    # Nomes dos dias da semana
    WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    # Nomes dos meses
    MONTHS = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]

    def __init__(self, db: Session):
        """Inicializa analyzer."""
        self.db = db
        self.repository = ForecastRepository(db)

    async def analyze_demand_pattern(
        self,
        product_id: UUID,
        product_info: dict,
        historical_data: list[dict],
        analyzed_by: UUID | None = None,
    ) -> DemandPattern:
        """
        Analisa padrao de demanda de um produto.

        Args:
            product_id: ID do produto
            product_info: Informacoes do produto
            historical_data: Lista de {date, quantity}
            analyzed_by: ID do usuario

        Returns:
            DemandPattern: Padrao identificado
        """
        logger.info(f"Analisando padrao de demanda: {product_id}")

        if len(historical_data) < 14:
            raise ValueError(f"Dados insuficientes: {len(historical_data)} pontos. Minimo: 14 pontos para analise.")

        # Ordenar dados por data
        sorted_data = sorted(historical_data, key=lambda x: x["date"])
        dates = [d["date"] for d in sorted_data]
        values = np.array([d["quantity"] for d in sorted_data])

        # Criar registro de padrao
        pattern_data = DemandPatternCreate(
            product_id=product_id,
            product_code=product_info.get("code", ""),
            product_name=product_info.get("name", ""),
            analysis_start_date=min(dates),
            analysis_end_date=max(dates),
        )
        pattern = self.repository.create_demand_pattern(pattern_data)

        try:
            # Estatisticas basicas
            stats = self._calculate_statistics(values)

            # Analise de tendencia
            trend_info = self._analyze_trend(values)

            # Analise de sazonalidade
            seasonality_info = self._analyze_seasonality(dates, values)

            # Classificar padrao
            pattern_type, confidence = self._classify_pattern(values, trend_info, seasonality_info)

            # Detectar anomalias
            anomaly_info = self._detect_anomalies(dates, values, stats)

            # Calcular distribuicoes
            weekday_dist = self._calculate_weekday_distribution(dates, values)
            monthly_dist = self._calculate_monthly_distribution(dates, values)

            # Calcular previsibilidade
            predictability = self._calculate_predictability(stats, trend_info, seasonality_info)

            # Gerar recomendacoes
            recommendations = self._generate_recommendations(pattern_type, trend_info, seasonality_info, stats)

            # Gerar insights
            insights = self._generate_insights(pattern_type, trend_info, seasonality_info, anomaly_info)

            # Atualizar padrao
            update_data = {
                "total_data_points": len(values),
                "pattern_type": pattern_type,
                "pattern_confidence": confidence,
                "seasonality_type": seasonality_info["type"],
                "seasonality_strength": seasonality_info["strength"],
                "seasonal_periods": seasonality_info.get("periods"),
                "peak_periods": seasonality_info.get("peaks", []),
                "trend_direction": trend_info["direction"],
                "trend_slope": trend_info["slope"],
                "trend_strength": trend_info["strength"],
                "avg_demand": stats["mean"],
                "std_demand": stats["std"],
                "cv_demand": stats["cv"],
                "median_demand": stats["median"],
                "min_demand": stats["min"],
                "max_demand": stats["max"],
                "volatility_index": stats["volatility"],
                "predictability_score": predictability,
                "anomalies_detected": anomaly_info["count"],
                "anomaly_dates": anomaly_info["dates"],
                "anomaly_impact": anomaly_info["impact"],
                "weekday_distribution": weekday_dist,
                "monthly_distribution": monthly_dist,
                "recommended_model": recommendations["model"],
                "recommended_safety_stock_days": recommendations["safety_days"],
                "recommended_review_period_days": recommendations["review_days"],
                "insights": insights,
                "analyzed_by": analyzed_by,
            }

            pattern = self.repository.update_demand_pattern(pattern.id, update_data)
            logger.info(f"Padrao analisado: {pattern.id} - {pattern_type.value}")

        except Exception as e:
            logger.error(f"Erro na analise {pattern.id}: {e}")
            raise

        return pattern

    def _calculate_statistics(self, values: np.ndarray) -> dict:
        """Calcula estatisticas basicas."""
        mean = np.mean(values)
        std = np.std(values)
        cv = (std / mean * 100) if mean > 0 else 0

        # Volatilidade (0-100)
        volatility = min(100, cv)

        return {
            "mean": round(float(mean), 2),
            "std": round(float(std), 2),
            "cv": round(float(cv), 2),
            "median": round(float(np.median(values)), 2),
            "min": round(float(np.min(values)), 2),
            "max": round(float(np.max(values)), 2),
            "volatility": round(volatility, 1),
        }

    def _analyze_trend(self, values: np.ndarray) -> dict:
        """Analisa tendencia dos dados."""
        if len(values) < 7:
            return {
                "direction": TrendDirection.STABLE,
                "slope": 0.0,
                "strength": 0.0,
            }

        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)

        # Calcular R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((values - y_pred) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Determinar direcao
        mean_val = np.mean(values)
        relative_slope = (slope / mean_val) if mean_val > 0 else 0

        if abs(relative_slope) < 0.001:
            direction = TrendDirection.STABLE
        elif relative_slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING

        # Se R-squared baixo, considerar volatil
        if r_squared < 0.3 and abs(relative_slope) > 0.001:
            direction = TrendDirection.VOLATILE

        return {
            "direction": direction,
            "slope": round(float(relative_slope), 4),
            "strength": round(float(max(0, r_squared)), 2),
        }

    def _analyze_seasonality(self, dates: list[date], values: np.ndarray) -> dict:
        """Analisa sazonalidade dos dados."""
        n = len(values)

        if n < 14:
            return {
                "type": SeasonalityType.NONE,
                "strength": 0.0,
                "periods": [],
                "peaks": [],
            }

        # Verificar sazonalidade semanal (7 dias)
        weekly_strength = self._check_periodicity(values, 7)

        # Verificar sazonalidade mensal (30 dias)
        monthly_strength = 0.0
        if n >= 60:
            monthly_strength = self._check_periodicity(values, 30)

        # Verificar sazonalidade anual (365 dias)
        yearly_strength = 0.0
        if n >= 400:
            yearly_strength = self._check_periodicity(values, 365)

        # Identificar periodos de pico
        peaks = self._identify_peak_periods(dates, values)

        # Determinar tipo principal
        strengths = {
            SeasonalityType.WEEKLY: weekly_strength,
            SeasonalityType.MONTHLY: monthly_strength,
            SeasonalityType.YEARLY: yearly_strength,
        }

        max_strength = max(strengths.values())
        if max_strength < 0.2:
            return {
                "type": SeasonalityType.NONE,
                "strength": 0.0,
                "periods": [],
                "peaks": peaks,
            }

        # Encontrar tipo dominante
        dominant_type = max(strengths.items(), key=lambda x: x[1])[0]
        periods = []
        if weekly_strength >= 0.2:
            periods.append(7)
        if monthly_strength >= 0.2:
            periods.append(30)
        if yearly_strength >= 0.2:
            periods.append(365)

        return {
            "type": dominant_type,
            "strength": round(max_strength, 2),
            "periods": periods,
            "peaks": peaks,
        }

    def _check_periodicity(self, values: np.ndarray, period: int) -> float:
        """Verifica forca de periodicidade."""
        n = len(values)
        if n < period * 2:
            return 0.0

        # Autocorrelacao no lag = period
        mean = np.mean(values)
        var = np.var(values)

        if var == 0:
            return 0.0

        # Calcular autocorrelacao
        n_valid = n - period
        autocorr = 0.0

        for i in range(n_valid):
            autocorr += (values[i] - mean) * (values[i + period] - mean)

        autocorr = autocorr / (n_valid * var)

        return max(0, min(1, autocorr))

    def _identify_peak_periods(self, dates: list[date], values: np.ndarray) -> list[dict]:
        """Identifica periodos de pico."""
        if len(values) < 30:
            return []

        peaks = []
        mean = np.mean(values)
        std = np.std(values)
        threshold = mean + std

        # Agrupar por mes
        monthly_data = defaultdict(list)
        for d, v in zip(dates, values, strict=False):
            key = f"{d.year}-{d.month:02d}"
            monthly_data[key].append(v)

        # Identificar meses de pico
        for month_key, month_values in monthly_data.items():
            month_mean = np.mean(month_values)
            if month_mean > threshold:
                year, month = month_key.split("-")
                peaks.append(
                    {
                        "period": month_key,
                        "month": int(month),
                        "avg_demand": round(float(month_mean), 2),
                        "above_mean_pct": round((month_mean / mean - 1) * 100, 1),
                    }
                )

        return sorted(peaks, key=lambda x: x["avg_demand"], reverse=True)[:5]

    def _classify_pattern(
        self, values: np.ndarray, trend_info: dict, seasonality_info: dict
    ) -> tuple[PatternType, float]:
        """Classifica tipo de padrao."""
        cv = (np.std(values) / np.mean(values)) if np.mean(values) > 0 else 0

        # Verificar zeros (demanda intermitente)
        zero_pct = np.sum(values == 0) / len(values)
        if zero_pct > 0.3:
            return PatternType.INTERMITTENT, 80.0

        # Verificar irregularidade
        if cv > 0.8:
            return PatternType.IRREGULAR, 70.0

        # Verificar sazonalidade
        if seasonality_info["strength"] >= 0.4:
            return PatternType.SEASONAL, 85.0

        # Verificar tendencia
        if trend_info["strength"] >= 0.5:
            return PatternType.TRENDING, 80.0

        # Verificar ciclos longos
        if len(values) >= 365:
            cycle_strength = self._check_periodicity(values, 90)
            if cycle_strength >= 0.3:
                return PatternType.CYCLICAL, 75.0

        # Demanda constante
        if cv < 0.3:
            return PatternType.CONSTANT, 85.0

        return PatternType.CONSTANT, 60.0

    def _detect_anomalies(self, dates: list[date], values: np.ndarray, stats: dict) -> dict:
        """Detecta anomalias nos dados."""
        mean = stats["mean"]
        std = stats["std"]

        # Usar 2.5 desvios padrao como threshold
        threshold = 2.5

        anomaly_dates = []
        total_impact = 0.0

        for _i, (d, v) in enumerate(zip(dates, values, strict=False)):
            if std > 0:
                z_score = abs(v - mean) / std
                if z_score > threshold:
                    anomaly_dates.append(
                        {
                            "date": d.isoformat(),
                            "value": float(v),
                            "z_score": round(z_score, 2),
                            "type": "spike" if v > mean else "drop",
                        }
                    )
                    total_impact += abs(v - mean)

        # Calcular impacto percentual
        total_sum = np.sum(values)
        impact_pct = (total_impact / total_sum * 100) if total_sum > 0 else 0

        return {
            "count": len(anomaly_dates),
            "dates": anomaly_dates[:20],  # Limitar a 20
            "impact": round(impact_pct, 2),
        }

    def _calculate_weekday_distribution(self, dates: list[date], values: np.ndarray) -> dict:
        """Calcula distribuicao por dia da semana."""
        day_totals = defaultdict(float)
        day_counts = defaultdict(int)

        for d, v in zip(dates, values, strict=False):
            day = self.WEEKDAYS[d.weekday()]
            day_totals[day] += v
            day_counts[day] += 1

        total = sum(day_totals.values())
        if total == 0:
            return {}

        return {day: round(day_totals[day] / total, 4) for day in self.WEEKDAYS if day_counts[day] > 0}

    def _calculate_monthly_distribution(self, dates: list[date], values: np.ndarray) -> dict:
        """Calcula distribuicao por mes."""
        month_totals = defaultdict(float)
        month_counts = defaultdict(int)

        for d, v in zip(dates, values, strict=False):
            month = self.MONTHS[d.month - 1]
            month_totals[month] += v
            month_counts[month] += 1

        total = sum(month_totals.values())
        if total == 0:
            return {}

        return {month: round(month_totals[month] / total, 4) for month in self.MONTHS if month_counts[month] > 0}

    def _calculate_predictability(self, stats: dict, trend_info: dict, seasonality_info: dict) -> float:
        """Calcula score de previsibilidade (0-100)."""
        # Fatores que aumentam previsibilidade
        score = 50.0  # Base

        # CV baixo aumenta previsibilidade
        cv = stats["cv"]
        if cv < 20:
            score += 25
        elif cv < 40:
            score += 15
        elif cv < 60:
            score += 5
        else:
            score -= 10

        # Tendencia forte aumenta
        if trend_info["strength"] >= 0.5:
            score += 15
        elif trend_info["strength"] >= 0.3:
            score += 10

        # Sazonalidade clara aumenta
        if seasonality_info["strength"] >= 0.4:
            score += 15
        elif seasonality_info["strength"] >= 0.2:
            score += 10

        # Volatilidade penaliza
        if stats["volatility"] > 60:
            score -= 15
        elif stats["volatility"] > 40:
            score -= 10

        return max(0, min(100, round(score, 1)))

    def _generate_recommendations(
        self, pattern_type: PatternType, trend_info: dict, seasonality_info: dict, stats: dict
    ) -> dict:
        """Gera recomendacoes baseadas no padrao."""
        # Modelo recomendado
        if pattern_type == PatternType.SEASONAL:
            model = "prophet"
        elif pattern_type == PatternType.TRENDING:
            model = "arima"
        elif pattern_type == PatternType.INTERMITTENT:
            model = "croston"
        elif pattern_type == PatternType.IRREGULAR:
            model = "ensemble"
        else:
            model = "exp_smoothing"

        # Dias de safety stock
        cv = stats["cv"]
        if cv > 60:
            safety_days = 14
        elif cv > 40:
            safety_days = 10
        elif cv > 20:
            safety_days = 7
        else:
            safety_days = 5

        # Periodo de revisao
        if pattern_type == PatternType.INTERMITTENT:
            review_days = 30
        elif pattern_type in (PatternType.TRENDING, PatternType.VOLATILE):
            review_days = 7
        else:
            review_days = 14

        return {
            "model": model,
            "safety_days": safety_days,
            "review_days": review_days,
        }

    def _generate_insights(
        self, pattern_type: PatternType, trend_info: dict, seasonality_info: dict, anomaly_info: dict
    ) -> list[dict]:
        """Gera insights sobre o padrao."""
        insights = []

        # Insight sobre tipo de padrao
        insights.append(
            {
                "type": "pattern",
                "title": f"Padrao {pattern_type.value}",
                "description": self._get_pattern_description(pattern_type),
                "importance": "high",
            }
        )

        # Insight sobre tendencia
        if trend_info["direction"] != TrendDirection.STABLE:
            direction = "crescente" if trend_info["direction"] == TrendDirection.INCREASING else "decrescente"
            insights.append(
                {
                    "type": "trend",
                    "title": f"Tendencia {direction}",
                    "description": f"Demanda com tendencia {direction} ({trend_info['slope'] * 100:.1f}% ao ano)",
                    "importance": "high" if trend_info["strength"] >= 0.5 else "medium",
                }
            )

        # Insight sobre sazonalidade
        if seasonality_info["type"] != SeasonalityType.NONE:
            insights.append(
                {
                    "type": "seasonality",
                    "title": f"Sazonalidade {seasonality_info['type'].value}",
                    "description": f"Padrao sazonal identificado com forca de {seasonality_info['strength'] * 100:.0f}%",
                    "importance": "medium",
                }
            )

        # Insight sobre anomalias
        if anomaly_info["count"] > 0:
            insights.append(
                {
                    "type": "anomaly",
                    "title": f"{anomaly_info['count']} anomalias detectadas",
                    "description": f"Impacto de {anomaly_info['impact']:.1f}% no total",
                    "importance": "low" if anomaly_info["count"] < 5 else "medium",
                }
            )

        return insights

    def _get_pattern_description(self, pattern_type: PatternType) -> str:
        """Retorna descricao do tipo de padrao."""
        descriptions = {
            PatternType.CONSTANT: "Demanda estavel e previsivel, ideal para modelos simples.",
            PatternType.TRENDING: "Demanda com tendencia clara, requer ajuste de previsoes.",
            PatternType.SEASONAL: "Demanda com padroes sazonais, considerar ciclos nas previsoes.",
            PatternType.CYCLICAL: "Demanda com ciclos longos, monitorar tendencias macro.",
            PatternType.IRREGULAR: "Demanda volatil, usar modelos robustos e safety stock maior.",
            PatternType.INTERMITTENT: "Demanda esporadica, usar modelos especificos (Croston).",
        }
        return descriptions.get(pattern_type, "Padrao identificado.")

    def get_pattern(self, pattern_id: UUID) -> DemandPattern | None:
        """Busca padrao por ID."""
        return self.repository.get_demand_pattern(pattern_id)

    def get_latest_pattern(self, product_id: UUID) -> DemandPattern | None:
        """Busca padrao mais recente para produto."""
        return self.repository.get_latest_demand_pattern(product_id)
