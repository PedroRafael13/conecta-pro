"""Service de Analytics Financeiro com IA."""

import statistics
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session


class AnalyticsService:
    """Servico de Analytics Financeiro com IA."""

    def __init__(self, db: Session):
        """Inicializa servico."""
        self.db = db

    def detect_anomalies(
        self,
        values: list[Decimal],
        threshold: float = 2.0,
    ) -> list[dict]:
        """Detecta anomalias usando Z-score."""
        if len(values) < 3:
            return []

        float_values = [float(v) for v in values]
        mean = statistics.mean(float_values)
        stdev = statistics.stdev(float_values) if len(float_values) > 1 else 0

        if stdev == 0:
            return []

        anomalies = []
        for i, value in enumerate(float_values):
            z_score = abs((value - mean) / stdev)
            if z_score > threshold:
                deviation = round((value - mean) / mean * 100, 2) if mean != 0 else 0
                anomalies.append(
                    {
                        "index": i,
                        "value": Decimal(str(value)),
                        "z_score": round(z_score, 2),
                        "deviation": deviation,
                        "type": "valor_atipico",
                        "severity": self._get_severity(z_score),
                    }
                )

        return anomalies

    def _get_severity(self, z_score: float) -> str:
        """Retorna severidade baseada no Z-score."""
        if z_score > 3:
            return "critica"
        if z_score > 2.5:
            return "alta"
        return "media"

    def calculate_trend(
        self,
        values: list[Decimal],
        dates: list[datetime] = None,
    ) -> dict:
        """Calcula tendencia dos dados."""
        # dates pode ser usado para analise temporal futura
        _ = dates

        if len(values) < 2:
            return {"direction": "stable", "strength": 0, "change_percent": 0}

        float_values = [float(v) for v in values]
        mid = len(float_values) // 2
        first_half = float_values[:mid]
        second_half = float_values[mid:]

        avg_first = statistics.mean(first_half) if first_half else 0
        avg_second = statistics.mean(second_half) if second_half else 0

        change_percent = self._calc_change_percent(avg_first, avg_second)
        correlation = self._calc_correlation(float_values)
        strength = min(abs(correlation) * 100, 100)

        direction = self._get_direction(change_percent)

        return {
            "direction": direction,
            "strength": round(strength, 2),
            "change_percent": round(change_percent, 2),
            "correlation": round(correlation, 4),
        }

    def _calc_change_percent(self, first: float, second: float) -> float:
        """Calcula percentual de mudanca."""
        if first == 0:
            return 100 if second > 0 else 0
        return ((second - first) / first) * 100

    def _calc_correlation(self, values: list[float]) -> float:
        """Calcula coeficiente de correlacao."""
        n = len(values)
        x_vals = list(range(n))
        x_mean = statistics.mean(x_vals)
        y_mean = statistics.mean(values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, values, strict=False))
        x_var = sum((x - x_mean) ** 2 for x in x_vals)
        y_var = sum((y - y_mean) ** 2 for y in values)

        if x_var == 0 or y_var == 0:
            return 0
        return numerator / (x_var * y_var) ** 0.5

    def _get_direction(self, change_percent: float) -> str:
        """Retorna direcao baseada na mudanca percentual."""
        if change_percent > 5:
            return "up"
        if change_percent < -5:
            return "down"
        return "stable"

    def calculate_seasonality(
        self,
        monthly_values: dict[int, Decimal],
    ) -> dict:
        """Analisa sazonalidade mensal."""
        if not monthly_values or len(monthly_values) < 6:
            return {"has_seasonality": False, "peak_months": [], "low_months": []}

        float_values = {k: float(v) for k, v in monthly_values.items()}
        avg = statistics.mean(float_values.values())

        if avg == 0:
            return {"has_seasonality": False, "peak_months": [], "low_months": []}

        seasonal_indices = {k: v / avg for k, v in float_values.items()}
        peak_months = [m for m, idx in seasonal_indices.items() if idx > 1.15]
        low_months = [m for m, idx in seasonal_indices.items() if idx < 0.85]

        stdev = statistics.stdev(seasonal_indices.values()) if len(seasonal_indices) > 1 else 0
        has_seasonality = stdev > 0.1

        return {
            "has_seasonality": has_seasonality,
            "peak_months": sorted(peak_months),
            "low_months": sorted(low_months),
            "seasonal_indices": {k: round(v, 2) for k, v in seasonal_indices.items()},
            "volatility": round(stdev, 4),
        }

    def analyze_distribution(self, values: list[Decimal]) -> dict:
        """Analisa distribuicao dos dados."""
        if not values:
            return {
                "count": 0,
                "sum": Decimal("0"),
                "mean": Decimal("0"),
                "median": Decimal("0"),
                "stdev": Decimal("0"),
                "min": Decimal("0"),
                "max": Decimal("0"),
            }

        float_values = [float(v) for v in values]
        stdev = statistics.stdev(float_values) if len(float_values) > 1 else 0

        return {
            "count": len(float_values),
            "sum": Decimal(str(sum(float_values))),
            "mean": Decimal(str(statistics.mean(float_values))),
            "median": Decimal(str(statistics.median(float_values))),
            "stdev": Decimal(str(stdev)),
            "min": Decimal(str(min(float_values))),
            "max": Decimal(str(max(float_values))),
            "range": Decimal(str(max(float_values) - min(float_values))),
        }

    def calculate_growth_rate(
        self,
        values: list[Decimal],
        period: str = "monthly",
    ) -> dict:
        """Calcula taxa de crescimento."""
        if len(values) < 2:
            return {"average_growth": Decimal("0"), "cagr": Decimal("0"), "periods": 0}

        float_values = [float(v) for v in values if v > 0]
        if len(float_values) < 2:
            return {"average_growth": Decimal("0"), "cagr": Decimal("0"), "periods": 0}

        growth_rates = []
        for i in range(1, len(float_values)):
            if float_values[i - 1] != 0:
                rate = (float_values[i] - float_values[i - 1]) / float_values[i - 1]
                growth_rates.append(rate)

        avg_growth = statistics.mean(growth_rates) * 100 if growth_rates else 0

        n = len(float_values) - 1
        if float_values[0] != 0 and n > 0:
            cagr = ((float_values[-1] / float_values[0]) ** (1 / n) - 1) * 100
        else:
            cagr = 0

        return {
            "average_growth": Decimal(str(round(avg_growth, 2))),
            "cagr": Decimal(str(round(cagr, 2))),
            "periods": len(float_values),
            "period_type": period,
            "first_value": Decimal(str(float_values[0])),
            "last_value": Decimal(str(float_values[-1])),
        }

    def suggest_targets(
        self,
        historical_values: list[Decimal],
        growth_target: Decimal = None,
    ) -> dict:
        """Sugere metas baseado em historico."""
        if not historical_values:
            return {
                "conservative": Decimal("0"),
                "realistic": Decimal("0"),
                "aggressive": Decimal("0"),
            }

        float_values = [float(v) for v in historical_values]
        current = float_values[-1] if float_values else 0
        avg = statistics.mean(float_values)
        max_val = max(float_values)

        growth = self.calculate_growth_rate(historical_values)
        avg_growth = float(growth["average_growth"]) / 100

        if growth_target:
            target_growth = float(growth_target) / 100
        else:
            target_growth = max(avg_growth, 0.05)

        return {
            "conservative": Decimal(str(round(current * (1 + target_growth * 0.5), 2))),
            "realistic": Decimal(str(round(current * (1 + target_growth), 2))),
            "aggressive": Decimal(str(round(current * (1 + target_growth * 1.5), 2))),
            "based_on": {
                "current_value": Decimal(str(current)),
                "average": Decimal(str(round(avg, 2))),
                "max_historical": Decimal(str(max_val)),
                "growth_rate": growth["average_growth"],
            },
        }

    def calculate_pareto(
        self,
        items: list[dict],
        value_field: str,
        name_field: str,
    ) -> dict:
        """Calcula analise de Pareto (80/20)."""
        empty = {"total": Decimal("0"), "top_20_percent": [], "top_20_contribution": Decimal("0")}
        if not items:
            return empty

        sorted_items = sorted(
            items,
            key=lambda x: float(x.get(value_field, 0)),
            reverse=True,
        )

        total = sum(float(i.get(value_field, 0)) for i in sorted_items)
        if total == 0:
            return empty

        top_items = self._calc_top_items(sorted_items, value_field, name_field, total)

        top_20_count = max(1, len(sorted_items) // 5)
        top_20_value = sum(float(i.get(value_field, 0)) for i in sorted_items[:top_20_count])

        return {
            "total": Decimal(str(round(total, 2))),
            "items_count": len(sorted_items),
            "top_items_for_80": top_items,
            "top_20_percent": [
                {"name": i.get(name_field, "N/A"), "value": Decimal(str(i.get(value_field, 0)))}
                for i in sorted_items[:top_20_count]
            ],
            "top_20_contribution": Decimal(str(round(top_20_value / total * 100, 2))),
        }

    def _calc_top_items(
        self,
        sorted_items: list[dict],
        value_field: str,
        name_field: str,
        total: float,
    ) -> list[dict]:
        """Calcula items top ate 80%."""
        cumulative = 0
        top_items = []
        for item in sorted_items:
            value = float(item.get(value_field, 0))
            cumulative += value
            percentage = (cumulative / total) * 100
            top_items.append(
                {
                    "name": item.get(name_field, "N/A"),
                    "value": Decimal(str(value)),
                    "percentage": Decimal(str(round(value / total * 100, 2))),
                    "cumulative": Decimal(str(round(percentage, 2))),
                }
            )
            if percentage >= 80:
                break
        return top_items

    def analyze_variance(
        self,
        actual: Decimal,
        budget: Decimal,
        description: str = "",
    ) -> dict:
        """Analisa variancia orcamento vs realizado."""
        actual_f = float(actual)
        budget_f = float(budget)

        variance = actual_f - budget_f
        if budget_f != 0:
            variance_percent = (variance / budget_f) * 100
        else:
            variance_percent = 100 if actual_f > 0 else 0

        status, severity = self._get_variance_status(variance_percent)
        favorable = variance > 0

        return {
            "actual": Decimal(str(actual_f)),
            "budget": Decimal(str(budget_f)),
            "variance": Decimal(str(round(variance, 2))),
            "variance_percent": Decimal(str(round(variance_percent, 2))),
            "status": status,
            "severity": severity,
            "favorable": favorable,
            "description": description,
        }

    def _get_variance_status(self, variance_percent: float) -> tuple[str, str]:
        """Retorna status e severidade baseado na variancia."""
        abs_var = abs(variance_percent)
        if abs_var < 5:
            return "on_track", "low"
        if abs_var < 15:
            return "attention", "medium"
        return "off_track", "high"
