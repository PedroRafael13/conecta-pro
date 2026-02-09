"""ForecastService - Servico de Previsao de Valores.

Sprint 34 - AI Predictions.
"""

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class ForecastResult:
    """Resultado de forecast."""

    value: float  # Valor previsto
    lower_bound: float  # Limite inferior (intervalo confianca)
    upper_bound: float  # Limite superior
    confidence: float  # Nivel de confianca (0-1)
    trend: str  # up, down, stable
    trend_percent: float  # % mudanca
    seasonality_factor: float  # Fator sazonal aplicado
    date: datetime  # Data da previsao


@dataclass
class ForecastSummary:
    """Resumo de forecast para periodo."""

    period_start: datetime
    period_end: datetime
    total_value: float
    avg_value: float
    min_value: float
    max_value: float
    trend: str
    confidence: float
    scenarios: dict  # pessimist, base, optimist
    forecasts: list  # Lista de ForecastResult


class ForecastService:
    """Servico de previsao de valores (receita, despesa, demanda)."""

    # Fatores sazonais por mes (1.0 = normal)
    DEFAULT_SEASONALITY = {
        1: 0.85,  # Janeiro - ferias, inicio de ano lento
        2: 0.90,  # Fevereiro - carnaval
        3: 1.00,  # Marco - normal
        4: 1.00,  # Abril - normal
        5: 1.05,  # Maio - aquecimento
        6: 1.00,  # Junho - normal
        7: 0.95,  # Julho - ferias
        8: 1.00,  # Agosto - normal
        9: 1.05,  # Setembro - aquecimento
        10: 1.10,  # Outubro - alta
        11: 1.15,  # Novembro - Black Friday
        12: 1.20,  # Dezembro - fim de ano
    }

    def __init__(self, db_session: Any):
        """Inicializa o servico.

        Args:
            db_session: Sessao do banco de dados.
        """
        self.db = db_session

    async def forecast_revenue(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID | None = None,
        historical_data: list[dict] | None = None,
        periods: int = 6,
        period_type: str = "month",  # day, week, month, quarter
        confidence_level: float = 0.95,
    ) -> ForecastSummary:
        """Preve receita futura.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade (condominio, contrato, etc).
            entity_id: ID especifico (None = todos).
            historical_data: Dados historicos (opcional).
            periods: Numero de periodos a prever.
            period_type: Tipo de periodo.
            confidence_level: Nivel de confianca.

        Returns:
            Resumo do forecast.
        """
        # Coleta dados historicos se nao fornecidos
        if historical_data is None:
            historical_data = await self._get_historical_revenue(tenant_id, entity_type, entity_id, periods * 3)

        # Calcula forecast
        forecasts = self._calculate_forecast(
            historical_data,
            periods,
            period_type,
            confidence_level,
            forecast_type="revenue",
        )

        # Gera resumo
        return self._create_summary(forecasts, period_type)

    async def forecast_expense(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID | None = None,
        historical_data: list[dict] | None = None,
        periods: int = 6,
        period_type: str = "month",
        confidence_level: float = 0.95,
    ) -> ForecastSummary:
        """Preve despesas futuras.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade.
            entity_id: ID especifico.
            historical_data: Dados historicos.
            periods: Numero de periodos.
            period_type: Tipo de periodo.
            confidence_level: Nivel de confianca.

        Returns:
            Resumo do forecast.
        """
        if historical_data is None:
            historical_data = await self._get_historical_expense(tenant_id, entity_type, entity_id, periods * 3)

        forecasts = self._calculate_forecast(
            historical_data,
            periods,
            period_type,
            confidence_level,
            forecast_type="expense",
        )

        return self._create_summary(forecasts, period_type)

    async def forecast_demand(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID | None = None,
        historical_data: list[dict] | None = None,
        periods: int = 6,
        period_type: str = "month",
        confidence_level: float = 0.95,
    ) -> ForecastSummary:
        """Preve demanda futura.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade.
            entity_id: ID especifico.
            historical_data: Dados historicos.
            periods: Numero de periodos.
            period_type: Tipo de periodo.
            confidence_level: Nivel de confianca.

        Returns:
            Resumo do forecast.
        """
        if historical_data is None:
            historical_data = await self._get_historical_demand(tenant_id, entity_type, entity_id, periods * 3)

        forecasts = self._calculate_forecast(
            historical_data,
            periods,
            period_type,
            confidence_level,
            forecast_type="demand",
        )

        return self._create_summary(forecasts, period_type)

    def _calculate_forecast(
        self,
        historical_data: list[dict],
        periods: int,
        period_type: str,
        confidence_level: float,
        forecast_type: str,
    ) -> list[ForecastResult]:
        """Calcula forecast usando media movel + tendencia + sazonalidade.

        Args:
            historical_data: Dados historicos.
            periods: Numero de periodos.
            period_type: Tipo de periodo.
            confidence_level: Nivel de confianca.
            forecast_type: Tipo de forecast.

        Returns:
            Lista de previsoes.
        """
        if not historical_data:
            # Retorna forecast vazio se nao tem dados
            return self._generate_empty_forecast(periods, period_type)

        # Extrai valores
        values = [d.get("value", 0) for d in historical_data]
        dates = [d.get("date", datetime.utcnow()) for d in historical_data]

        # Calcula estatisticas basicas
        avg_value = sum(values) / len(values) if values else 0
        std_dev = self._calculate_std_dev(values, avg_value)

        # Calcula tendencia (regressao linear simples)
        trend_slope = self._calculate_trend(values)
        trend_direction = "up" if trend_slope > 0.01 else "down" if trend_slope < -0.01 else "stable"

        # Gera forecasts
        forecasts = []
        last_date = dates[-1] if dates else datetime.utcnow()
        last_value = values[-1] if values else avg_value

        for i in range(1, periods + 1):
            # Calcula data do periodo
            forecast_date = self._get_next_period_date(last_date, period_type, i)

            # Aplica tendencia
            base_value = last_value + (trend_slope * avg_value * i)

            # Aplica sazonalidade
            month = forecast_date.month
            seasonality = self.DEFAULT_SEASONALITY.get(month, 1.0)
            forecast_value = base_value * seasonality

            # Calcula intervalo de confianca
            z_score = self._get_z_score(confidence_level)
            margin = z_score * std_dev * math.sqrt(i)  # Incerteza aumenta com tempo

            lower_bound = max(0, forecast_value - margin)
            upper_bound = forecast_value + margin

            # Confianca diminui com distancia
            confidence = confidence_level * (1 - (i / (periods * 2)))

            forecasts.append(
                ForecastResult(
                    value=round(forecast_value, 2),
                    lower_bound=round(lower_bound, 2),
                    upper_bound=round(upper_bound, 2),
                    confidence=round(confidence, 4),
                    trend=trend_direction,
                    trend_percent=round(trend_slope * 100, 2),
                    seasonality_factor=seasonality,
                    date=forecast_date,
                )
            )

        logger.info(
            "Forecast calculated",
            extra={
                "type": forecast_type,
                "periods": periods,
                "avg_value": avg_value,
                "trend": trend_direction,
            },
        )

        return forecasts

    def _create_summary(
        self,
        forecasts: list[ForecastResult],
        period_type: str,
    ) -> ForecastSummary:
        """Cria resumo do forecast.

        Args:
            forecasts: Lista de previsoes.
            period_type: Tipo de periodo.

        Returns:
            Resumo do forecast.
        """
        if not forecasts:
            return ForecastSummary(
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow(),
                total_value=0,
                avg_value=0,
                min_value=0,
                max_value=0,
                trend="stable",
                confidence=0,
                scenarios={},
                forecasts=[],
            )

        values = [f.value for f in forecasts]
        total_value = sum(values)
        avg_value = total_value / len(values)

        # Calcula cenarios
        scenarios = {
            "pessimist": {
                "total": round(sum(f.lower_bound for f in forecasts), 2),
                "avg": round(sum(f.lower_bound for f in forecasts) / len(forecasts), 2),
            },
            "base": {
                "total": round(total_value, 2),
                "avg": round(avg_value, 2),
            },
            "optimist": {
                "total": round(sum(f.upper_bound for f in forecasts), 2),
                "avg": round(sum(f.upper_bound for f in forecasts) / len(forecasts), 2),
            },
        }

        return ForecastSummary(
            period_start=forecasts[0].date,
            period_end=forecasts[-1].date,
            total_value=round(total_value, 2),
            avg_value=round(avg_value, 2),
            min_value=round(min(values), 2),
            max_value=round(max(values), 2),
            trend=forecasts[0].trend,
            confidence=round(sum(f.confidence for f in forecasts) / len(forecasts), 4),
            scenarios=scenarios,
            forecasts=forecasts,
        )

    def _calculate_std_dev(self, values: list[float], mean: float) -> float:
        """Calcula desvio padrao.

        Args:
            values: Lista de valores.
            mean: Media.

        Returns:
            Desvio padrao.
        """
        if len(values) < 2:
            return mean * 0.1  # Default 10% da media

        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    def _calculate_trend(self, values: list[float]) -> float:
        """Calcula tendencia (slope da regressao linear).

        Args:
            values: Lista de valores.

        Returns:
            Slope normalizado.
        """
        if len(values) < 3:
            return 0.0

        n = len(values)
        x = list(range(n))
        mean_x = sum(x) / n
        mean_y = sum(values) / n

        # Calcula slope
        numerator = sum((x[i] - mean_x) * (values[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Normaliza pela media
        if mean_y != 0:
            return slope / mean_y
        return 0.0

    def _get_next_period_date(
        self,
        base_date: datetime,
        period_type: str,
        periods_ahead: int,
    ) -> datetime:
        """Calcula data do proximo periodo.

        Args:
            base_date: Data base.
            period_type: Tipo de periodo.
            periods_ahead: Quantos periodos a frente.

        Returns:
            Data do periodo.
        """
        if period_type == "day":
            return base_date + timedelta(days=periods_ahead)
        if period_type == "week":
            return base_date + timedelta(weeks=periods_ahead)
        if period_type == "month":
            # Adiciona meses
            month = base_date.month + periods_ahead
            year = base_date.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            day = min(base_date.day, 28)  # Evita problemas com dias
            return base_date.replace(year=year, month=month, day=day)
        if period_type == "quarter":
            months = periods_ahead * 3
            month = base_date.month + months
            year = base_date.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            return base_date.replace(year=year, month=month, day=1)

        return base_date + timedelta(days=periods_ahead * 30)

    def _get_z_score(self, confidence_level: float) -> float:
        """Retorna z-score para nivel de confianca.

        Args:
            confidence_level: Nivel de confianca (0-1).

        Returns:
            Z-score.
        """
        z_scores = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576,
        }
        return z_scores.get(confidence_level, 1.96)

    def _generate_empty_forecast(
        self,
        periods: int,
        period_type: str,
    ) -> list[ForecastResult]:
        """Gera forecast vazio quando nao ha dados.

        Args:
            periods: Numero de periodos.
            period_type: Tipo de periodo.

        Returns:
            Lista de previsoes vazias.
        """
        forecasts = []
        base_date = datetime.utcnow()

        for i in range(1, periods + 1):
            forecast_date = self._get_next_period_date(base_date, period_type, i)
            forecasts.append(
                ForecastResult(
                    value=0,
                    lower_bound=0,
                    upper_bound=0,
                    confidence=0,
                    trend="stable",
                    trend_percent=0,
                    seasonality_factor=1.0,
                    date=forecast_date,
                )
            )

        return forecasts

    async def _get_historical_revenue(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID | None,
        periods: int,
    ) -> list[dict]:
        """Busca dados historicos de receita.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade.
            entity_id: ID da entidade.
            periods: Numero de periodos.

        Returns:
            Lista de dados historicos.
        """
        # Em producao, buscaria do banco de dados
        # Aqui retorna dados simulados para demonstracao
        data = []
        base_date = datetime.utcnow()
        base_value = 50000.0

        for i in range(periods, 0, -1):
            date = self._get_next_period_date(base_date, "month", -i)
            seasonality = self.DEFAULT_SEASONALITY.get(date.month, 1.0)
            # Adiciona variacao aleatoria
            variation = 1 + ((hash(str(date)) % 20) - 10) / 100
            value = base_value * seasonality * variation
            data.append({"date": date, "value": value})

        return data

    async def _get_historical_expense(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID | None,
        periods: int,
    ) -> list[dict]:
        """Busca dados historicos de despesa.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade.
            entity_id: ID da entidade.
            periods: Numero de periodos.

        Returns:
            Lista de dados historicos.
        """
        data = []
        base_date = datetime.utcnow()
        base_value = 35000.0

        for i in range(periods, 0, -1):
            date = self._get_next_period_date(base_date, "month", -i)
            variation = 1 + ((hash(str(date)) % 15) - 7) / 100
            value = base_value * variation
            data.append({"date": date, "value": value})

        return data

    async def _get_historical_demand(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID | None,
        periods: int,
    ) -> list[dict]:
        """Busca dados historicos de demanda.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade.
            entity_id: ID da entidade.
            periods: Numero de periodos.

        Returns:
            Lista de dados historicos.
        """
        data = []
        base_date = datetime.utcnow()
        base_value = 100.0  # unidades de demanda

        for i in range(periods, 0, -1):
            date = self._get_next_period_date(base_date, "month", -i)
            seasonality = self.DEFAULT_SEASONALITY.get(date.month, 1.0)
            variation = 1 + ((hash(str(date)) % 25) - 12) / 100
            value = base_value * seasonality * variation
            data.append({"date": date, "value": int(value)})

        return data
