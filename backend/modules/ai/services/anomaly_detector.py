"""AnomalyDetector - Servico de Deteccao de Anomalias.

Sprint 34 - AI Predictions.
"""

import logging
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from modules.ai.models.anomaly_log import AnomalyLog, AnomalySeverity, AnomalyStatus, AnomalyType

logger = logging.getLogger(__name__)


@dataclass
class AnomalyResult:
    """Resultado de deteccao de anomalia."""

    is_anomaly: bool
    anomaly_type: AnomalyType | None
    severity: AnomalySeverity
    anomaly_score: float  # 0-1
    confidence: float  # 0-1
    observed_value: float
    expected_value: float
    expected_range: tuple[float, float]
    deviation_score: float  # Z-score
    explanation: str
    contributing_factors: list[dict]


@dataclass
class TimeSeriesAnomaly:
    """Anomalia em serie temporal."""

    timestamp: datetime
    value: float
    is_anomaly: bool
    anomaly_type: AnomalyType | None
    expected_value: float
    deviation: float


class AnomalyDetector:
    """Detector de anomalias em dados."""

    # Thresholds para deteccao
    Z_SCORE_THRESHOLD = 3.0  # Desvios padrao para considerar anomalia
    IQR_FACTOR = 1.5  # Fator IQR para outliers
    SPIKE_THRESHOLD = 0.5  # 50% de variacao para spike
    DROP_THRESHOLD = 0.3  # 30% de queda para drop

    # Severidade por z-score
    SEVERITY_THRESHOLDS = {
        AnomalySeverity.LOW: 2.0,
        AnomalySeverity.MEDIUM: 3.0,
        AnomalySeverity.HIGH: 4.0,
        AnomalySeverity.CRITICAL: 5.0,
    }

    def __init__(self, db_session: Any):
        """Inicializa o detector.

        Args:
            db_session: Sessao do banco de dados.
        """
        self.db = db_session

    async def detect_anomaly(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
        field: str,
        value: float,
        historical_values: list[float] | None = None,
        context: dict | None = None,
    ) -> AnomalyResult:
        """Detecta anomalia em um valor.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade.
            entity_id: ID da entidade.
            field: Campo sendo analisado.
            value: Valor a verificar.
            historical_values: Valores historicos para comparacao.
            context: Contexto adicional.

        Returns:
            Resultado da deteccao.
        """
        # Coleta dados historicos se nao fornecidos
        if historical_values is None:
            historical_values = await self._get_historical_values(tenant_id, entity_type, entity_id, field)

        if len(historical_values) < 5:
            # Dados insuficientes para deteccao
            return AnomalyResult(
                is_anomaly=False,
                anomaly_type=None,
                severity=AnomalySeverity.LOW,
                anomaly_score=0.0,
                confidence=0.0,
                observed_value=value,
                expected_value=value,
                expected_range=(value, value),
                deviation_score=0.0,
                explanation="Dados historicos insuficientes para deteccao",
                contributing_factors=[],
            )

        # Calcula estatisticas
        stats = self._calculate_statistics(historical_values)

        # Calcula z-score
        z_score = self._calculate_z_score(value, stats["mean"], stats["std"])

        # Verifica se e anomalia
        is_anomaly = abs(z_score) >= self.Z_SCORE_THRESHOLD

        # Determina tipo de anomalia
        anomaly_type = self._determine_anomaly_type(value, historical_values, stats, z_score)

        # Calcula severidade
        severity = self._calculate_severity(abs(z_score))

        # Calcula score de anomalia (0-1)
        anomaly_score = min(abs(z_score) / 5.0, 1.0)

        # Calcula confianca baseada na quantidade de dados
        confidence = min(len(historical_values) / 30, 1.0)

        # Gera explicacao
        explanation = self._generate_explanation(value, stats, z_score, anomaly_type, is_anomaly)

        # Identifica fatores contribuintes
        contributing_factors = self._identify_contributing_factors(value, historical_values, stats, context)

        result = AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type if is_anomaly else None,
            severity=severity,
            anomaly_score=round(anomaly_score, 4),
            confidence=round(confidence, 4),
            observed_value=value,
            expected_value=round(stats["mean"], 2),
            expected_range=(
                round(stats["mean"] - 2 * stats["std"], 2),
                round(stats["mean"] + 2 * stats["std"], 2),
            ),
            deviation_score=round(z_score, 2),
            explanation=explanation,
            contributing_factors=contributing_factors,
        )

        # Registra anomalia se detectada
        if is_anomaly:
            await self._log_anomaly(tenant_id, entity_type, entity_id, field, result)

        return result

    async def detect_time_series_anomalies(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
        field: str,
        time_series: list[dict],  # [{"timestamp": datetime, "value": float}]
        window_size: int = 7,
    ) -> list[TimeSeriesAnomaly]:
        """Detecta anomalias em serie temporal.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade.
            entity_id: ID da entidade.
            field: Campo sendo analisado.
            time_series: Serie temporal.
            window_size: Tamanho da janela para media movel.

        Returns:
            Lista de anomalias detectadas.
        """
        if len(time_series) < window_size + 1:
            return []

        results = []
        values = [ts["value"] for ts in time_series]

        for i, ts in enumerate(time_series):
            if i < window_size:
                # Dados insuficientes para janela
                results.append(
                    TimeSeriesAnomaly(
                        timestamp=ts["timestamp"],
                        value=ts["value"],
                        is_anomaly=False,
                        anomaly_type=None,
                        expected_value=ts["value"],
                        deviation=0.0,
                    )
                )
                continue

            # Calcula estatisticas da janela
            window = values[i - window_size : i]
            stats = self._calculate_statistics(window)

            # Calcula z-score
            z_score = self._calculate_z_score(ts["value"], stats["mean"], stats["std"])

            # Verifica anomalia
            is_anomaly = abs(z_score) >= self.Z_SCORE_THRESHOLD

            # Determina tipo
            anomaly_type = None
            if is_anomaly:
                if ts["value"] > stats["mean"]:
                    anomaly_type = AnomalyType.SPIKE
                else:
                    anomaly_type = AnomalyType.DROP

            results.append(
                TimeSeriesAnomaly(
                    timestamp=ts["timestamp"],
                    value=ts["value"],
                    is_anomaly=is_anomaly,
                    anomaly_type=anomaly_type,
                    expected_value=round(stats["mean"], 2),
                    deviation=round(z_score, 2),
                )
            )

        # Log anomalias encontradas
        anomaly_count = sum(1 for r in results if r.is_anomaly)
        if anomaly_count > 0:
            logger.info(
                "Time series anomalies detected",
                extra={
                    "entity": f"{entity_type}:{entity_id}",
                    "field": field,
                    "anomaly_count": anomaly_count,
                    "total_points": len(time_series),
                },
            )

        return results

    async def detect_batch_anomalies(
        self,
        tenant_id: UUID,
        entity_type: str,
        data: list[dict],  # [{"entity_id": UUID, "field": str, "value": float}]
    ) -> list[AnomalyResult]:
        """Detecta anomalias em lote.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo das entidades.
            data: Lista de dados a verificar.

        Returns:
            Lista de resultados.
        """
        # Agrupa por field para calcular estatisticas do grupo
        field_values = {}
        for item in data:
            field = item["field"]
            if field not in field_values:
                field_values[field] = []
            field_values[field].append(item["value"])

        # Calcula estatisticas por field
        field_stats = {}
        for field, values in field_values.items():
            field_stats[field] = self._calculate_statistics(values)

        # Detecta anomalias
        results = []
        for item in data:
            field = item["field"]
            value = item["value"]
            stats = field_stats[field]

            z_score = self._calculate_z_score(value, stats["mean"], stats["std"])
            is_anomaly = abs(z_score) >= self.Z_SCORE_THRESHOLD

            anomaly_type = None
            if is_anomaly:
                anomaly_type = AnomalyType.OUTLIER

            severity = self._calculate_severity(abs(z_score))
            anomaly_score = min(abs(z_score) / 5.0, 1.0)

            results.append(
                AnomalyResult(
                    is_anomaly=is_anomaly,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    anomaly_score=round(anomaly_score, 4),
                    confidence=0.8,
                    observed_value=value,
                    expected_value=round(stats["mean"], 2),
                    expected_range=(
                        round(stats["mean"] - 2 * stats["std"], 2),
                        round(stats["mean"] + 2 * stats["std"], 2),
                    ),
                    deviation_score=round(z_score, 2),
                    explanation=f"Valor {value} desvia {abs(z_score):.1f} desvios padrao da media do grupo",
                    contributing_factors=[],
                )
            )

        return results

    def _calculate_statistics(self, values: list[float]) -> dict:
        """Calcula estatisticas basicas.

        Args:
            values: Lista de valores.

        Returns:
            Dicionario com estatisticas.
        """
        if not values:
            return {"mean": 0, "std": 0, "min": 0, "max": 0, "median": 0, "iqr": 0}

        n = len(values)
        sorted_values = sorted(values)

        # Media
        mean = sum(values) / n

        # Desvio padrao
        if n > 1:
            variance = sum((x - mean) ** 2 for x in values) / (n - 1)
            std = math.sqrt(variance)
        else:
            std = 0

        # Mediana
        if n % 2 == 0:
            median = (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        else:
            median = sorted_values[n // 2]

        # Quartis e IQR
        q1_idx = n // 4
        q3_idx = (3 * n) // 4
        q1 = sorted_values[q1_idx]
        q3 = sorted_values[q3_idx]
        iqr = q3 - q1

        return {
            "mean": mean,
            "std": std if std > 0 else mean * 0.1,  # Default 10% da media
            "min": min(values),
            "max": max(values),
            "median": median,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "count": n,
        }

    def _calculate_z_score(self, value: float, mean: float, std: float) -> float:
        """Calcula z-score.

        Args:
            value: Valor observado.
            mean: Media.
            std: Desvio padrao.

        Returns:
            Z-score.
        """
        if std == 0:
            return 0.0
        return (value - mean) / std

    def _determine_anomaly_type(
        self,
        value: float,
        historical_values: list[float],
        stats: dict,
        z_score: float,
    ) -> AnomalyType | None:
        """Determina o tipo de anomalia.

        Args:
            value: Valor observado.
            historical_values: Valores historicos.
            stats: Estatisticas.
            z_score: Z-score calculado.

        Returns:
            Tipo de anomalia ou None.
        """
        if abs(z_score) < self.Z_SCORE_THRESHOLD:
            return None

        # Verifica spike/drop
        last_value = historical_values[-1] if historical_values else stats["mean"]
        if last_value != 0:
            change_rate = (value - last_value) / abs(last_value)
            if change_rate > self.SPIKE_THRESHOLD:
                return AnomalyType.SPIKE
            if change_rate < -self.DROP_THRESHOLD:
                return AnomalyType.DROP

        # Verifica outlier simples
        if value > stats["mean"]:
            return AnomalyType.OUTLIER
        return AnomalyType.OUTLIER

    def _calculate_severity(self, abs_z_score: float) -> AnomalySeverity:
        """Calcula severidade baseada no z-score.

        Args:
            abs_z_score: Valor absoluto do z-score.

        Returns:
            Severidade.
        """
        if abs_z_score >= self.SEVERITY_THRESHOLDS[AnomalySeverity.CRITICAL]:
            return AnomalySeverity.CRITICAL
        if abs_z_score >= self.SEVERITY_THRESHOLDS[AnomalySeverity.HIGH]:
            return AnomalySeverity.HIGH
        if abs_z_score >= self.SEVERITY_THRESHOLDS[AnomalySeverity.MEDIUM]:
            return AnomalySeverity.MEDIUM
        return AnomalySeverity.LOW

    def _generate_explanation(
        self,
        value: float,
        stats: dict,
        z_score: float,
        anomaly_type: AnomalyType | None,
        is_anomaly: bool,
    ) -> str:
        """Gera explicacao da anomalia.

        Args:
            value: Valor observado.
            stats: Estatisticas.
            z_score: Z-score.
            anomaly_type: Tipo de anomalia.
            is_anomaly: Se e anomalia.

        Returns:
            Explicacao em texto.
        """
        if not is_anomaly:
            return f"Valor {value:.2f} esta dentro do esperado (media: {stats['mean']:.2f})"

        direction = "acima" if z_score > 0 else "abaixo"
        type_desc = {
            AnomalyType.SPIKE: "pico subito",
            AnomalyType.DROP: "queda abrupta",
            AnomalyType.OUTLIER: "valor atipico",
        }.get(anomaly_type, "anomalia")

        return (
            f"Detectado {type_desc}: valor {value:.2f} esta {abs(z_score):.1f} "
            f"desvios padrao {direction} da media ({stats['mean']:.2f}). "
            f"Faixa esperada: {stats['mean'] - 2 * stats['std']:.2f} a {stats['mean'] + 2 * stats['std']:.2f}"
        )

    def _identify_contributing_factors(
        self,
        value: float,
        historical_values: list[float],
        stats: dict,
        context: dict | None,
    ) -> list[dict]:
        """Identifica fatores contribuintes.

        Args:
            value: Valor observado.
            historical_values: Valores historicos.
            stats: Estatisticas.
            context: Contexto adicional.

        Returns:
            Lista de fatores.
        """
        factors = []

        # Fator: Desvio da media
        deviation_pct = abs(value - stats["mean"]) / stats["mean"] * 100 if stats["mean"] else 0
        factors.append(
            {
                "factor": "deviation_from_mean",
                "contribution": min(deviation_pct / 100, 0.5),
                "description": f"Desvio de {deviation_pct:.1f}% da media",
            }
        )

        # Fator: Tendencia recente
        if len(historical_values) >= 3:
            recent = historical_values[-3:]
            trend = (recent[-1] - recent[0]) / recent[0] * 100 if recent[0] else 0
            factors.append(
                {
                    "factor": "recent_trend",
                    "contribution": min(abs(trend) / 100, 0.3),
                    "description": f"Tendencia recente de {trend:+.1f}%",
                }
            )

        # Fator: Volatilidade
        cv = stats["std"] / stats["mean"] * 100 if stats["mean"] else 0
        factors.append(
            {
                "factor": "volatility",
                "contribution": min(cv / 100, 0.2),
                "description": f"Coeficiente de variacao: {cv:.1f}%",
            }
        )

        return sorted(factors, key=lambda x: x["contribution"], reverse=True)

    async def _get_historical_values(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
        field: str,
        days: int = 90,
    ) -> list[float]:
        """Busca valores historicos.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade.
            entity_id: ID da entidade.
            field: Campo.
            days: Dias de historico.

        Returns:
            Lista de valores.
        """
        # Em producao, buscaria do banco de dados
        # Aqui retorna valores simulados
        import random

        base = 1000
        values = []
        for _i in range(days):
            # Gera valor com variacao normal
            variation = random.gauss(0, 0.1)
            values.append(base * (1 + variation))

        return values

    async def _log_anomaly(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
        field: str,
        result: AnomalyResult,
    ) -> AnomalyLog:
        """Registra anomalia no banco.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade.
            entity_id: ID da entidade.
            field: Campo.
            result: Resultado da deteccao.

        Returns:
            Log criado.
        """
        anomaly_log = AnomalyLog(
            tenant_id=tenant_id,
            anomaly_type=result.anomaly_type or AnomalyType.OTHER,
            severity=result.severity,
            status=AnomalyStatus.DETECTED,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_field=field,
            detector_name="statistical_detector",
            observed_value=result.observed_value,
            expected_value=result.expected_value,
            expected_range_min=result.expected_range[0],
            expected_range_max=result.expected_range[1],
            anomaly_score=result.anomaly_score,
            confidence_score=result.confidence,
            deviation_score=result.deviation_score,
            detected_at=datetime.utcnow(),
            title=f"Anomalia em {entity_type}.{field}",
            description=result.explanation,
            contributing_factors={f["factor"]: f["contribution"] for f in result.contributing_factors},
        )

        self.db.add(anomaly_log)
        await self.db.commit()
        await self.db.refresh(anomaly_log)

        logger.info(
            "Anomaly logged",
            extra={
                "anomaly_id": str(anomaly_log.id),
                "type": result.anomaly_type.value if result.anomaly_type else "unknown",
                "severity": result.severity.value,
            },
        )

        return anomaly_log
