"""Service de Previsao Financeira com IA."""

from decimal import Decimal
import statistics

from sqlalchemy.orm import Session


class ForecastService:
    """Servico de Previsao Financeira com IA."""

    def __init__(self, db: Session):
        """Inicializa servico."""
        self.db = db

    def generate_forecast(
        self,
        historical_values: list[Decimal],
        periods: int = 12,
    ) -> dict:
        """Gera previsao com cenarios usando regressao linear."""
        if len(historical_values) < 3:
            return self._empty_forecast()

        float_values = [float(v) for v in historical_values]
        model = self._calc_linear_model(float_values)
        n = len(float_values)

        forecasts, scenarios = self._generate_predictions(n, periods, model)
        confidence = self._calc_confidence(model["r_squared"])

        return {
            "forecasts": forecasts,
            "scenarios": scenarios,
            "model": {
                "type": "linear_regression",
                "slope": round(model["slope"], 4),
                "intercept": round(model["intercept"], 2),
                "r_squared": round(model["r_squared"], 4),
            },
            "confidence": round(confidence, 2),
            "periods": periods,
        }

    def _empty_forecast(self) -> dict:
        """Retorna previsao vazia."""
        return {
            "forecasts": [],
            "scenarios": {"pessimistic": [], "realistic": [], "optimistic": []},
            "confidence": 0,
        }

    def _calc_linear_model(self, values: list[float]) -> dict:
        """Calcula modelo de regressao linear."""
        n = len(values)
        x_vals = list(range(n))
        x_mean = statistics.mean(x_vals)
        y_mean = statistics.mean(values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, values))
        denominator = sum((x - x_mean) ** 2 for x in x_vals)

        if denominator == 0:
            slope, intercept = 0, y_mean
        else:
            slope = numerator / denominator
            intercept = y_mean - slope * x_mean

        predictions = [slope * x + intercept for x in x_vals]
        residuals = [a - p for a, p in zip(values, predictions)]
        std_error = (sum(r ** 2 for r in residuals) / (n - 2)) ** 0.5 if n > 2 else 0

        ss_res = sum(r ** 2 for r in residuals)
        ss_tot = sum((y - y_mean) ** 2 for y in values)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        return {
            "slope": slope,
            "intercept": intercept,
            "std_error": std_error,
            "r_squared": r_squared,
        }

    def _generate_predictions(
        self,
        n: int,
        periods: int,
        model: dict,
    ) -> tuple[list[dict], dict]:
        """Gera previsoes e cenarios."""
        forecasts = []
        pessimistic, realistic, optimistic = [], [], []

        slope = model["slope"]
        intercept = model["intercept"]
        margin = 1.96 * model["std_error"]

        for i in range(periods):
            x = n + i
            predicted = slope * x + intercept

            forecasts.append({
                "period": i + 1,
                "value": Decimal(str(round(predicted, 2))),
                "lower_bound": Decimal(str(round(predicted - margin, 2))),
                "upper_bound": Decimal(str(round(predicted + margin, 2))),
            })

            pessimistic.append(Decimal(str(round(predicted * 0.85, 2))))
            realistic.append(Decimal(str(round(predicted, 2))))
            optimistic.append(Decimal(str(round(predicted * 1.15, 2))))

        return forecasts, {
            "pessimistic": pessimistic,
            "realistic": realistic,
            "optimistic": optimistic,
        }

    def _calc_confidence(self, r_squared: float) -> float:
        """Calcula confianca baseada em R-squared."""
        return max(0, min(100, r_squared * 100))

    def moving_average_forecast(
        self,
        values: list[Decimal],
        window: int = 3,
        periods: int = 6,
    ) -> list[Decimal]:
        """Previsao por media movel."""
        if len(values) < window:
            return []

        float_values = [float(v) for v in values]
        forecasts = []
        current_values = float_values.copy()

        for _ in range(periods):
            ma = statistics.mean(current_values[-window:])
            forecasts.append(Decimal(str(round(ma, 2))))
            current_values.append(ma)

        return forecasts

    def exponential_smoothing(
        self,
        values: list[Decimal],
        alpha: float = 0.3,
        periods: int = 6,
    ) -> list[Decimal]:
        """Previsao por suavizacao exponencial."""
        if not values:
            return []

        float_values = [float(v) for v in values]
        smoothed = [float_values[0]]

        for i in range(1, len(float_values)):
            s = alpha * float_values[i] + (1 - alpha) * smoothed[-1]
            smoothed.append(s)

        return [Decimal(str(round(smoothed[-1], 2))) for _ in range(periods)]

    def calculate_break_even(
        self,
        fixed_costs: Decimal,
        variable_cost_per_unit: Decimal,
        price_per_unit: Decimal,
    ) -> dict:
        """Calcula ponto de equilibrio."""
        fixed = float(fixed_costs)
        variable = float(variable_cost_per_unit)
        price = float(price_per_unit)

        if price <= variable:
            return {
                "units": None,
                "revenue": None,
                "margin_contribution": Decimal("0"),
                "error": "Preco deve ser maior que custo variavel",
            }

        margin = price - variable
        units = fixed / margin
        revenue = units * price

        return {
            "units": Decimal(str(round(units, 0))),
            "revenue": Decimal(str(round(revenue, 2))),
            "margin_contribution": Decimal(str(round(margin, 2))),
            "margin_contribution_percent": Decimal(str(round((margin / price) * 100, 2))),
            "fixed_costs": fixed_costs,
            "variable_cost_per_unit": variable_cost_per_unit,
            "price_per_unit": price_per_unit,
        }

    def scenario_analysis(
        self,
        base_value: Decimal,
        growth_rates: list[Decimal],
        periods: int = 12,
    ) -> dict:
        """Analise de cenarios com diferentes taxas de crescimento."""
        if not growth_rates:
            growth_rates = [Decimal("-0.1"), Decimal("0"), Decimal("0.1")]

        scenarios = {}
        base = float(base_value)

        for rate in growth_rates:
            rate_f = float(rate)
            name = "pessimistic" if rate_f < 0 else "optimistic" if rate_f > 0 else "base"
            values = self._project_values(base, rate_f, periods)

            final = float(values[-1]) if values else base
            total_growth = ((final - base) / base) * 100 if base != 0 else 0

            scenarios[name] = {
                "growth_rate": rate,
                "values": values,
                "final_value": values[-1] if values else base_value,
                "total_growth": Decimal(str(round(total_growth, 2))),
            }

        return {"base_value": base_value, "periods": periods, "scenarios": scenarios}

    def _project_values(
        self,
        base: float,
        rate: float,
        periods: int,
    ) -> list[Decimal]:
        """Projeta valores com taxa de crescimento."""
        values = []
        current = base
        for _ in range(periods):
            current = current * (1 + rate)
            values.append(Decimal(str(round(current, 2))))
        return values

    def cash_flow_projection(
        self,
        opening_balance: Decimal,
        expected_inflows: list[Decimal],
        expected_outflows: list[Decimal],
    ) -> dict:
        """Projeta fluxo de caixa."""
        periods = max(len(expected_inflows), len(expected_outflows))
        inflows = self._pad_list(expected_inflows, periods)
        outflows = self._pad_list(expected_outflows, periods)

        projections = self._calc_projections(opening_balance, inflows, outflows)
        summary = self._calc_summary(opening_balance, inflows, outflows, projections)
        alerts = self._calc_alerts(projections, periods)

        return {
            "opening_balance": opening_balance,
            "projections": projections,
            "summary": summary,
            "alerts": alerts,
        }

    def _pad_list(self, values: list[Decimal], length: int) -> list[Decimal]:
        """Preenche lista com zeros."""
        return list(values) + [Decimal("0")] * (length - len(values))

    def _calc_projections(
        self,
        opening: Decimal,
        inflows: list[Decimal],
        outflows: list[Decimal],
    ) -> list[dict]:
        """Calcula projecoes de fluxo."""
        projections = []
        balance = float(opening)

        for i, (inf, out) in enumerate(zip(inflows, outflows)):
            inflow, outflow = float(inf), float(out)
            net_flow = inflow - outflow
            balance += net_flow

            projections.append({
                "period": i + 1,
                "inflow": Decimal(str(round(inflow, 2))),
                "outflow": Decimal(str(round(outflow, 2))),
                "net_flow": Decimal(str(round(net_flow, 2))),
                "closing_balance": Decimal(str(round(balance, 2))),
                "is_negative": balance < 0,
            })

        return projections

    def _calc_summary(
        self,
        opening: Decimal,
        inflows: list[Decimal],
        outflows: list[Decimal],
        projections: list[dict],
    ) -> dict:
        """Calcula resumo do fluxo."""
        total_in = sum(float(i) for i in inflows)
        total_out = sum(float(o) for o in outflows)
        min_bal = min(float(p["closing_balance"]) for p in projections)

        return {
            "total_inflows": Decimal(str(round(total_in, 2))),
            "total_outflows": Decimal(str(round(total_out, 2))),
            "net_change": Decimal(str(round(total_in - total_out, 2))),
            "final_balance": projections[-1]["closing_balance"] if projections else opening,
            "min_balance": Decimal(str(round(min_bal, 2))),
        }

    def _calc_alerts(self, projections: list[dict], periods: int) -> dict:
        """Calcula alertas de fluxo."""
        critical = [p for p in projections if p["is_negative"]]
        count = len(critical)

        if count > periods * 0.3:
            risk = "high"
        elif count > 0:
            risk = "medium"
        else:
            risk = "low"

        return {
            "has_negative_periods": count > 0,
            "critical_periods": [p["period"] for p in critical],
            "risk_level": risk,
        }

    def what_if_analysis(
        self,
        base_scenario: dict,
        variable_changes: dict,
    ) -> list[dict]:
        """Analise what-if com variacoes de variaveis."""
        results = []

        for var_name, changes in variable_changes.items():
            for change in changes:
                original = float(base_scenario.get(var_name, 0))
                modified = original * (1 + float(change) / 100)
                impact = modified - original

                results.append({
                    "variable": var_name,
                    "change_percent": change,
                    "original_value": Decimal(str(original)),
                    "modified_value": Decimal(str(round(modified, 2))),
                    "impact": Decimal(str(round(impact, 2))),
                })

        return results

    def calculate_npv(
        self,
        initial_investment: Decimal,
        cash_flows: list[Decimal],
        discount_rate: Decimal,
    ) -> dict:
        """Calcula Valor Presente Liquido (VPL)."""
        rate = float(discount_rate)
        investment = float(initial_investment)

        present_values = []
        for i, cf in enumerate(cash_flows, start=1):
            pv = float(cf) / ((1 + rate) ** i)
            present_values.append(Decimal(str(round(pv, 2))))

        total_pv = sum(float(pv) for pv in present_values)
        npv = total_pv - investment

        return {
            "initial_investment": initial_investment,
            "discount_rate": discount_rate,
            "present_values": present_values,
            "total_present_value": Decimal(str(round(total_pv, 2))),
            "npv": Decimal(str(round(npv, 2))),
            "is_viable": npv > 0,
            "periods": len(cash_flows),
        }

    def calculate_payback(
        self,
        initial_investment: Decimal,
        cash_flows: list[Decimal],
    ) -> dict:
        """Calcula Payback simples."""
        investment = float(initial_investment)
        cumulative = 0
        payback_period = None

        for i, cf in enumerate(cash_flows):
            cf_float = float(cf)
            cumulative += cf_float
            if cumulative >= investment and payback_period is None:
                previous = cumulative - cf_float
                remaining = investment - previous
                fraction = remaining / cf_float if cf_float != 0 else 0
                payback_period = i + fraction

        return {
            "initial_investment": initial_investment,
            "payback_period": (
                Decimal(str(round(payback_period, 2))) if payback_period is not None else None
            ),
            "recovered": payback_period is not None,
            "total_cash_flows": sum(cash_flows),
            "periods_analyzed": len(cash_flows),
        }
