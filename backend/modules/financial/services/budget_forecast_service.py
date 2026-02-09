"""Budget Forecast Service - Serviço de Previsão Orçamentária.

Sprint 30 - Orçamento e Previsão.
Responsável por:
- Previsão de despesas
- Alertas de desvio orçamentário
- Projeções de fim de período
- Análise de tendências
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.cost_center import CostCenter, CostCenterStatus
from modules.financial.models.journal_entry import EntryStatus, JournalEntry, JournalEntryLine


class AlertSeverity(StrEnum):
    """Severidade do alerta."""

    INFO = "INFO"  # Informativo
    WARNING = "WARNING"  # Atenção
    CRITICAL = "CRITICAL"  # Crítico


class AlertType(StrEnum):
    """Tipo de alerta orçamentário."""

    OVER_BUDGET = "OVER_BUDGET"  # Acima do orçamento
    NEAR_LIMIT = "NEAR_LIMIT"  # Próximo do limite
    TREND_NEGATIVE = "TREND_NEGATIVE"  # Tendência negativa
    VARIANCE_HIGH = "VARIANCE_HIGH"  # Variação alta
    NO_BUDGET = "NO_BUDGET"  # Sem orçamento definido
    PROJECTION_EXCEEDED = "PROJECTION_EXCEEDED"  # Projeção excede orçamento


class ForecastMethod(StrEnum):
    """Método de previsão."""

    AVERAGE = "AVERAGE"  # Média simples
    WEIGHTED_AVERAGE = "WEIGHTED_AVERAGE"  # Média ponderada
    LINEAR_TREND = "LINEAR_TREND"  # Tendência linear
    SEASONAL = "SEASONAL"  # Sazonal


@dataclass
class BudgetAlert:
    """Alerta orçamentário."""

    alert_type: AlertType
    severity: AlertSeverity
    message: str
    cost_center_id: UUID | None = None
    cost_center_code: str = ""
    cost_center_name: str = ""
    account_id: UUID | None = None
    account_code: str = ""

    budgeted: Decimal = Decimal("0")
    realized: Decimal = Decimal("0")
    variance: Decimal = Decimal("0")
    variance_pct: Decimal = Decimal("0")

    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "cost_center_id": str(self.cost_center_id) if self.cost_center_id else None,
            "cost_center_code": self.cost_center_code,
            "budgeted": float(self.budgeted),
            "realized": float(self.realized),
            "variance": float(self.variance),
            "variance_pct": float(self.variance_pct),
        }


@dataclass
class ExpenseForecast:
    """Previsão de despesa."""

    cost_center_id: UUID | None = None
    cost_center_code: str = ""
    cost_center_name: str = ""

    # Dados históricos
    historical_months: int = 0
    historical_average: Decimal = Decimal("0")
    historical_total: Decimal = Decimal("0")

    # Previsão
    forecast_method: ForecastMethod = ForecastMethod.AVERAGE
    projected_monthly: Decimal = Decimal("0")
    projected_remaining: Decimal = Decimal("0")  # Meses restantes do ano
    projected_annual: Decimal = Decimal("0")

    # Orçamento
    annual_budget: Decimal = Decimal("0")
    budget_remaining: Decimal = Decimal("0")

    # Análise
    will_exceed_budget: bool = False
    excess_amount: Decimal = Decimal("0")
    confidence_level: Decimal = Decimal("0")  # 0-100

    # Tendência
    trend_direction: str = "STABLE"  # UP, DOWN, STABLE
    trend_percentage: Decimal = Decimal("0")


@dataclass
class ForecastReport:
    """Relatório de previsão."""

    condominio_id: UUID
    reference_date: date
    forecast_horizon: int  # Meses à frente
    generated_at: datetime = field(default_factory=datetime.utcnow)

    forecasts: list[ExpenseForecast] = field(default_factory=list)
    alerts: list[BudgetAlert] = field(default_factory=list)

    # Totais
    total_projected: Decimal = Decimal("0")
    total_budget: Decimal = Decimal("0")
    projected_variance: Decimal = Decimal("0")

    # Contadores
    items_exceeding: int = 0
    critical_alerts: int = 0
    warning_alerts: int = 0


class BudgetForecastService:
    """Serviço de Previsão Orçamentária."""

    # Thresholds
    NEAR_LIMIT_THRESHOLD = Decimal("80")  # 80% do orçamento
    WARNING_THRESHOLD = Decimal("90")  # 90% do orçamento
    HIGH_VARIANCE_THRESHOLD = Decimal("15")  # 15% de variação

    def __init__(self, session: AsyncSession):
        """Inicializa o serviço.

        Args:
            session: Sessão assíncrona do banco de dados.
        """
        self.session = session

    async def generate_forecast(
        self,
        condominio_id: UUID,
        reference_date: date,
        forecast_months: int = 3,
        method: ForecastMethod = ForecastMethod.WEIGHTED_AVERAGE,
    ) -> ForecastReport:
        """Gera previsão orçamentária.

        Args:
            condominio_id: ID do condomínio.
            reference_date: Data de referência.
            forecast_months: Meses para projetar.
            method: Método de previsão.

        Returns:
            ForecastReport com previsões e alertas.
        """
        report = ForecastReport(
            condominio_id=condominio_id,
            reference_date=reference_date,
            forecast_horizon=forecast_months,
        )

        # Busca centros de custo ativos
        cost_centers = await self._get_active_cost_centers(condominio_id)

        for cost_center in cost_centers:
            forecast = await self._generate_cost_center_forecast(cost_center, reference_date, forecast_months, method)
            report.forecasts.append(forecast)

            # Gera alertas se necessário
            alerts = self._generate_forecast_alerts(forecast, cost_center)
            report.alerts.extend(alerts)

            # Atualiza totais
            report.total_projected += forecast.projected_annual
            report.total_budget += forecast.annual_budget

            if forecast.will_exceed_budget:
                report.items_exceeding += 1

        # Conta alertas por severidade
        for alert in report.alerts:
            if alert.severity == AlertSeverity.CRITICAL:
                report.critical_alerts += 1
            elif alert.severity == AlertSeverity.WARNING:
                report.warning_alerts += 1

        report.projected_variance = report.total_budget - report.total_projected

        return report

    async def get_budget_alerts(
        self,
        condominio_id: UUID,
        include_info: bool = False,
    ) -> list[BudgetAlert]:
        """Obtém alertas orçamentários ativos.

        Args:
            condominio_id: ID do condomínio.
            include_info: Incluir alertas informativos.

        Returns:
            Lista de alertas.
        """
        alerts = []
        today = date.today()
        current_month = today.month

        cost_centers = await self._get_active_cost_centers(condominio_id)

        for cost_center in cost_centers:
            # Verifica se não tem orçamento
            if cost_center.budget_monthly == Decimal("0"):
                if include_info:
                    alerts.append(
                        BudgetAlert(
                            alert_type=AlertType.NO_BUDGET,
                            severity=AlertSeverity.INFO,
                            message=f"Centro de custo {cost_center.code} sem orçamento definido",
                            cost_center_id=cost_center.id,
                            cost_center_code=cost_center.code,
                            cost_center_name=cost_center.name,
                        )
                    )
                continue

            # Calcula realizado no mês
            realized = await self._get_month_realized(cost_center.id, today.year, current_month)
            budgeted = cost_center.budget_monthly
            usage_pct = (realized / budgeted) * Decimal("100") if budgeted > 0 else Decimal("0")

            # Verifica alertas
            if realized > budgeted:
                alerts.append(
                    BudgetAlert(
                        alert_type=AlertType.OVER_BUDGET,
                        severity=AlertSeverity.CRITICAL,
                        message=f"Centro de custo {cost_center.code} excedeu orçamento mensal",
                        cost_center_id=cost_center.id,
                        cost_center_code=cost_center.code,
                        cost_center_name=cost_center.name,
                        budgeted=budgeted,
                        realized=realized,
                        variance=realized - budgeted,
                        variance_pct=usage_pct - Decimal("100"),
                    )
                )
            elif usage_pct >= self.WARNING_THRESHOLD:
                alerts.append(
                    BudgetAlert(
                        alert_type=AlertType.NEAR_LIMIT,
                        severity=AlertSeverity.WARNING,
                        message=f"Centro de custo {cost_center.code} em {usage_pct:.1f}% do orçamento",
                        cost_center_id=cost_center.id,
                        cost_center_code=cost_center.code,
                        cost_center_name=cost_center.name,
                        budgeted=budgeted,
                        realized=realized,
                        variance=budgeted - realized,
                        variance_pct=usage_pct,
                    )
                )
            elif usage_pct >= self.NEAR_LIMIT_THRESHOLD and include_info:
                alerts.append(
                    BudgetAlert(
                        alert_type=AlertType.NEAR_LIMIT,
                        severity=AlertSeverity.INFO,
                        message=f"Centro de custo {cost_center.code} em {usage_pct:.1f}% do orçamento",
                        cost_center_id=cost_center.id,
                        cost_center_code=cost_center.code,
                        cost_center_name=cost_center.name,
                        budgeted=budgeted,
                        realized=realized,
                        variance=budgeted - realized,
                        variance_pct=usage_pct,
                    )
                )

        # Ordena por severidade
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.INFO: 2,
        }
        alerts.sort(key=lambda x: severity_order[x.severity])

        return alerts

    async def get_trend_analysis(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,  # pylint: disable=unused-argument
        cost_center_id: UUID,
        months_back: int = 6,
    ) -> dict:
        """Analisa tendência de gastos de um centro de custo.

        Args:
            condominio_id: ID do condomínio.
            cost_center_id: ID do centro de custo.
            months_back: Meses para analisar.

        Returns:
            Dict com análise de tendência.
        """
        today = date.today()
        monthly_data = []

        for i in range(months_back, 0, -1):
            # Calcula mês/ano
            month = today.month - i
            year = today.year
            while month <= 0:
                month += 12
                year -= 1

            realized = await self._get_month_realized(cost_center_id, year, month)
            monthly_data.append(
                {
                    "year": year,
                    "month": month,
                    "month_name": self._get_month_name(month),
                    "realized": realized,
                }
            )

        # Calcula tendência
        if len(monthly_data) >= 2:
            first_half = sum(d["realized"] for d in monthly_data[: len(monthly_data) // 2])
            second_half = sum(d["realized"] for d in monthly_data[len(monthly_data) // 2 :])

            if first_half > Decimal("0"):
                trend_pct = ((second_half - first_half) / first_half) * Decimal("100")
            else:
                trend_pct = Decimal("0")

            if trend_pct > Decimal("5"):
                trend_direction = "UP"
            elif trend_pct < Decimal("-5"):
                trend_direction = "DOWN"
            else:
                trend_direction = "STABLE"
        else:
            trend_pct = Decimal("0")
            trend_direction = "STABLE"

        # Calcula média e projeção
        total = sum(d["realized"] for d in monthly_data)
        average = total / Decimal(str(len(monthly_data))) if monthly_data else Decimal("0")

        # Projeção simples (média * meses restantes)
        remaining_months = 12 - today.month
        projected_remaining = average * Decimal(str(remaining_months))

        return {
            "cost_center_id": str(cost_center_id),
            "months_analyzed": months_back,
            "monthly_data": [{**d, "realized": float(d["realized"])} for d in monthly_data],
            "total": float(total),
            "average": float(average),
            "trend_direction": trend_direction,
            "trend_percentage": float(trend_pct),
            "projected_remaining": float(projected_remaining),
            "analysis_date": today.isoformat(),
        }

    async def get_year_end_projection(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        year: int,
    ) -> dict:
        """Projeta gastos até o final do ano.

        Args:
            condominio_id: ID do condomínio.
            year: Ano para projetar.

        Returns:
            Dict com projeção.
        """
        today = date.today()
        current_month = today.month if today.year == year else 12

        cost_centers = await self._get_active_cost_centers(condominio_id)
        projections = []
        total_ytd = Decimal("0")
        total_projected = Decimal("0")
        total_budget = Decimal("0")

        for cost_center in cost_centers:
            # Calcula YTD (Year to Date)
            ytd_realized = Decimal("0")
            for month in range(1, current_month + 1):
                ytd_realized += await self._get_month_realized(cost_center.id, year, month)

            # Projeção: média mensal * 12
            if current_month > 0:
                monthly_avg = ytd_realized / Decimal(str(current_month))
                annual_projection = monthly_avg * Decimal("12")
            else:
                annual_projection = Decimal("0")

            annual_budget = cost_center.budget_annual
            variance = annual_budget - annual_projection

            projections.append(
                {
                    "cost_center_id": str(cost_center.id),
                    "cost_center_code": cost_center.code,
                    "cost_center_name": cost_center.name,
                    "ytd_realized": ytd_realized,
                    "monthly_average": monthly_avg if current_month > 0 else Decimal("0"),
                    "annual_projection": annual_projection,
                    "annual_budget": annual_budget,
                    "projected_variance": variance,
                    "will_exceed": annual_projection > annual_budget,
                }
            )

            total_ytd += ytd_realized
            total_projected += annual_projection
            total_budget += annual_budget

        return {
            "year": year,
            "reference_month": current_month,
            "projections": [
                {
                    **p,
                    "ytd_realized": float(p["ytd_realized"]),
                    "monthly_average": float(p["monthly_average"]),
                    "annual_projection": float(p["annual_projection"]),
                    "annual_budget": float(p["annual_budget"]),
                    "projected_variance": float(p["projected_variance"]),
                }
                for p in projections
            ],
            "summary": {
                "total_ytd": float(total_ytd),
                "total_projected": float(total_projected),
                "total_budget": float(total_budget),
                "projected_variance": float(total_budget - total_projected),
                "items_exceeding": sum(1 for p in projections if p["will_exceed"]),
            },
        }

    # --- Métodos privados ---

    async def _get_active_cost_centers(
        self,
        condominio_id: UUID,
    ) -> list[CostCenter]:
        """Busca centros de custo ativos."""
        query = (
            select(CostCenter)
            .where(
                and_(
                    CostCenter.condominio_id == condominio_id,
                    CostCenter.status == CostCenterStatus.ACTIVE,
                    CostCenter.active.is_(True),
                )
            )
            .order_by(CostCenter.code)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _get_month_realized(
        self,
        cost_center_id: UUID,
        year: int,
        month: int,
    ) -> Decimal:
        """Obtém valor realizado no mês."""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        query = (
            select(func.coalesce(func.sum(JournalEntryLine.debit_amount), 0))
            .join(JournalEntry)
            .where(
                and_(
                    JournalEntryLine.cost_center_id == cost_center_id,
                    JournalEntry.entry_date >= start_date,
                    JournalEntry.entry_date < end_date,
                    JournalEntry.status == EntryStatus.POSTED,
                )
            )
        )

        result = await self.session.execute(query)
        return Decimal(str(result.scalar() or 0))

    async def _generate_cost_center_forecast(  # pylint: disable=too-many-locals
        self,
        cost_center: CostCenter,
        reference_date: date,
        forecast_months: int,  # pylint: disable=unused-argument
        method: ForecastMethod,
    ) -> ExpenseForecast:
        """Gera previsão para um centro de custo."""
        forecast = ExpenseForecast(
            cost_center_id=cost_center.id,
            cost_center_code=cost_center.code,
            cost_center_name=cost_center.name,
            forecast_method=method,
            annual_budget=cost_center.budget_annual,
        )

        # Coleta histórico (últimos 6 meses)
        historical = []
        for i in range(6, 0, -1):
            month = reference_date.month - i
            year = reference_date.year
            while month <= 0:
                month += 12
                year -= 1

            realized = await self._get_month_realized(cost_center.id, year, month)
            historical.append(realized)

        forecast.historical_months = len(historical)
        forecast.historical_total = sum(historical)

        # Calcula projeção conforme método
        if method == ForecastMethod.AVERAGE:
            forecast.historical_average = (
                forecast.historical_total / Decimal(str(len(historical))) if historical else Decimal("0")
            )
            forecast.projected_monthly = forecast.historical_average
        elif method == ForecastMethod.WEIGHTED_AVERAGE:
            # Pesos crescentes para meses mais recentes
            weights = [1, 1, 2, 2, 3, 3]
            weighted_sum = sum(h * w for h, w in zip(historical, weights, strict=False))
            total_weight = sum(weights[: len(historical)])
            forecast.historical_average = (
                weighted_sum / Decimal(str(total_weight)) if total_weight > 0 else Decimal("0")
            )
            forecast.projected_monthly = forecast.historical_average
        else:
            # Fallback para média simples
            forecast.historical_average = (
                forecast.historical_total / Decimal(str(len(historical))) if historical else Decimal("0")
            )
            forecast.projected_monthly = forecast.historical_average

        # Projeção anual
        current_ytd = await self._get_ytd_realized(cost_center.id, reference_date)
        remaining_months = 12 - reference_date.month
        forecast.projected_remaining = forecast.projected_monthly * Decimal(str(remaining_months))
        forecast.projected_annual = current_ytd + forecast.projected_remaining

        # Orçamento restante
        forecast.budget_remaining = forecast.annual_budget - current_ytd

        # Análise
        forecast.will_exceed_budget = forecast.projected_annual > forecast.annual_budget
        if forecast.will_exceed_budget:
            forecast.excess_amount = forecast.projected_annual - forecast.annual_budget

        # Tendência
        if len(historical) >= 2:
            first = sum(historical[:3]) if len(historical) >= 3 else historical[0]
            last = sum(historical[-3:]) if len(historical) >= 3 else historical[-1]
            if first > Decimal("0"):
                trend = ((last - first) / first) * Decimal("100")
                forecast.trend_percentage = trend
                if trend > Decimal("10"):
                    forecast.trend_direction = "UP"
                elif trend < Decimal("-10"):
                    forecast.trend_direction = "DOWN"

        # Confiança baseada em dados históricos
        forecast.confidence_level = min(Decimal("100"), Decimal(str(len(historical) * 15)))

        return forecast

    async def _get_ytd_realized(
        self,
        cost_center_id: UUID,
        reference_date: date,
    ) -> Decimal:
        """Obtém realizado YTD."""
        start_date = date(reference_date.year, 1, 1)

        query = (
            select(func.coalesce(func.sum(JournalEntryLine.debit_amount), 0))
            .join(JournalEntry)
            .where(
                and_(
                    JournalEntryLine.cost_center_id == cost_center_id,
                    JournalEntry.entry_date >= start_date,
                    JournalEntry.entry_date <= reference_date,
                    JournalEntry.status == EntryStatus.POSTED,
                )
            )
        )

        result = await self.session.execute(query)
        return Decimal(str(result.scalar() or 0))

    def _generate_forecast_alerts(
        self,
        forecast: ExpenseForecast,
        cost_center: CostCenter,
    ) -> list[BudgetAlert]:
        """Gera alertas baseados na previsão."""
        alerts = []

        # Alerta de projeção excedendo orçamento
        if forecast.will_exceed_budget:
            alerts.append(
                BudgetAlert(
                    alert_type=AlertType.PROJECTION_EXCEEDED,
                    severity=AlertSeverity.WARNING,
                    message=(f"Projeção de {cost_center.code} excede orçamento em R$ {forecast.excess_amount:,.2f}"),
                    cost_center_id=cost_center.id,
                    cost_center_code=cost_center.code,
                    cost_center_name=cost_center.name,
                    budgeted=forecast.annual_budget,
                    realized=forecast.projected_annual,
                    variance=forecast.excess_amount,
                )
            )

        # Alerta de tendência negativa
        if forecast.trend_direction == "UP" and forecast.trend_percentage > Decimal("20"):
            alerts.append(
                BudgetAlert(
                    alert_type=AlertType.TREND_NEGATIVE,
                    severity=AlertSeverity.WARNING,
                    message=(f"Tendência de aumento de {forecast.trend_percentage:.1f}% em {cost_center.code}"),
                    cost_center_id=cost_center.id,
                    cost_center_code=cost_center.code,
                    cost_center_name=cost_center.name,
                    variance_pct=forecast.trend_percentage,
                )
            )

        return alerts

    @staticmethod
    def _get_month_name(month: int) -> str:
        """Retorna nome do mês."""
        months = [
            "",
            "Jan",
            "Fev",
            "Mar",
            "Abr",
            "Mai",
            "Jun",
            "Jul",
            "Ago",
            "Set",
            "Out",
            "Nov",
            "Dez",
        ]
        return months[month] if 1 <= month <= 12 else ""
