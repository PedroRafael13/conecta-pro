"""
Insight Extractor - Extração de insights com IA.

Analisa dados e gera insights automaticamente usando técnicas de IA.
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


# Configuração de thresholds para insights
INSIGHT_THRESHOLDS = {
    "growth": {
        "exceptional": 20.0,
        "good": 10.0,
        "warning": -5.0,
        "critical": -15.0,
    },
    "retention": {
        "excellent": 95.0,
        "good": 90.0,
        "warning": 85.0,
        "critical": 80.0,
    },
    "margin": {
        "excellent": 30.0,
        "good": 20.0,
        "warning": 15.0,
        "critical": 10.0,
    },
    "conversion": {
        "excellent": 30.0,
        "good": 20.0,
        "warning": 10.0,
        "critical": 5.0,
    },
}

# Templates de insights
INSIGHT_TEMPLATES = {
    "growth_exceptional": {
        "type": "positive",
        "title": "Crescimento Excepcional",
        "template": "O indicador {metric} cresceu {value}% no período, superando significativamente as expectativas.",
        "impact": "high",
    },
    "growth_good": {
        "type": "positive",
        "title": "Bom Crescimento",
        "template": "{metric} apresentou crescimento de {value}%, dentro das metas estabelecidas.",
        "impact": "medium",
    },
    "growth_warning": {
        "type": "warning",
        "title": "Crescimento Abaixo do Esperado",
        "template": "{metric} apresentou variação de {value}%, abaixo da meta. Atenção necessária.",
        "impact": "medium",
    },
    "growth_critical": {
        "type": "negative",
        "title": "Queda Significativa",
        "template": "{metric} apresentou queda de {value}%. Ação corretiva urgente recomendada.",
        "impact": "high",
    },
    "retention_warning": {
        "type": "warning",
        "title": "Taxa de Retenção em Alerta",
        "template": "Retenção de clientes em {value}% está abaixo do ideal de 90%. Risco de churn elevado.",
        "impact": "high",
    },
    "margin_excellent": {
        "type": "positive",
        "title": "Margem Saudável",
        "template": "Margem de {value}% indica excelente saúde financeira e eficiência operacional.",
        "impact": "medium",
    },
    "margin_warning": {
        "type": "warning",
        "title": "Margem Comprimida",
        "template": "Margem de {value}% está abaixo do ideal. Revisar estrutura de custos.",
        "impact": "high",
    },
    "anomaly_spike": {
        "type": "info",
        "title": "Pico Detectado",
        "template": "Pico incomum detectado em {date}: {value} (esperado: {expected}). Desvio de {deviation}σ.",
        "impact": "medium",
    },
    "anomaly_drop": {
        "type": "warning",
        "title": "Queda Detectada",
        "template": "Queda incomum detectada em {date}: {value} (esperado: {expected}). Desvio de {deviation}σ.",
        "impact": "medium",
    },
    "trend_up": {
        "type": "positive",
        "title": "Tendência de Alta",
        "template": "{metric} apresenta tendência de alta consistente ({change}% no período).",
        "impact": "medium",
    },
    "trend_down": {
        "type": "warning",
        "title": "Tendência de Queda",
        "template": "{metric} apresenta tendência de queda ({change}% no período). Investigar causas.",
        "impact": "medium",
    },
}

# Templates de recomendações
RECOMMENDATION_TEMPLATES = {
    "sales_decline": {
        "title": "Revisar Estratégia de Vendas",
        "description": "Analise os canais e produtos com menor performance. Considere campanhas de reativação e ajustes de pricing.",
        "priority": "high",
        "category": "sales",
        "effort": "medium",
        "expected_impact": "high",
    },
    "retention_low": {
        "title": "Programa de Fidelização",
        "description": "Implemente ou reforce programa de fidelidade. Identifique clientes em risco e ofereça incentivos de permanência.",
        "priority": "high",
        "category": "retention",
        "effort": "medium",
        "expected_impact": "high",
    },
    "margin_low": {
        "title": "Otimização de Custos",
        "description": "Revise contratos de fornecedores, processos operacionais e despesas fixas. Busque oportunidades de automação.",
        "priority": "medium",
        "category": "finance",
        "effort": "high",
        "expected_impact": "high",
    },
    "conversion_low": {
        "title": "Melhorar Taxa de Conversão",
        "description": "Analise o funil de vendas para identificar gargalos. Considere treinamento de vendas e qualificação de leads.",
        "priority": "medium",
        "category": "sales",
        "effort": "medium",
        "expected_impact": "medium",
    },
    "inventory_low": {
        "title": "Ajustar Níveis de Estoque",
        "description": "Revise políticas de estoque mínimo e lead times de reposição para evitar rupturas.",
        "priority": "high",
        "category": "operations",
        "effort": "low",
        "expected_impact": "medium",
    },
    "churn_risk": {
        "title": "Ações Anti-Churn",
        "description": "Identifique clientes com alto risco de churn baseado em comportamento. Inicie contato proativo.",
        "priority": "high",
        "category": "retention",
        "effort": "medium",
        "expected_impact": "high",
    },
}


class InsightExtractor:
    """Serviço de extração de insights com IA."""

    def __init__(self, db: Session = None):
        """Inicializa extrator de insights."""
        self.db = db

    def extract_insights(
        self,
        data: dict[str, Any],
        metrics: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Extrai insights dos dados e métricas.

        Args:
            data: Dados brutos do relatório
            metrics: Métricas calculadas
            context: Contexto adicional (período, tipo de relatório, etc.)

        Returns:
            Lista de insights gerados
        """
        insights = []

        # Analisa crescimento
        growth_insights = self._analyze_growth(metrics)
        insights.extend(growth_insights)

        # Analisa retenção
        retention_insights = self._analyze_retention(metrics)
        insights.extend(retention_insights)

        # Analisa margem
        margin_insights = self._analyze_margin(metrics)
        insights.extend(margin_insights)

        # Analisa conversão
        conversion_insights = self._analyze_conversion(metrics)
        insights.extend(conversion_insights)

        # Detecta anomalias
        if data:
            anomaly_insights = self._detect_anomalies(data)
            insights.extend(anomaly_insights)

        # Analisa tendências
        if data:
            trend_insights = self._analyze_trends(data)
            insights.extend(trend_insights)

        # Ordena por impacto
        impact_order = {"high": 0, "medium": 1, "low": 2}
        insights.sort(key=lambda x: impact_order.get(x.get("impact", "low"), 3))

        return insights

    def generate_recommendations(
        self,
        insights: list[dict[str, Any]],
        data: dict[str, Any],
        metrics: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Gera recomendações baseadas nos insights.

        Args:
            insights: Lista de insights gerados
            data: Dados brutos
            metrics: Métricas calculadas

        Returns:
            Lista de recomendações
        """
        recommendations = []
        added_categories = set()

        for insight in insights:
            insight_type = insight.get("type")
            category = insight.get("category", "")

            # Evita recomendações duplicadas por categoria
            if category in added_categories:
                continue

            # Mapeia insights para recomendações
            if insight_type in ["negative", "warning"]:
                if "sales" in category or "growth" in str(insight.get("title", "")).lower():
                    if "sales_decline" not in added_categories:
                        rec = RECOMMENDATION_TEMPLATES["sales_decline"].copy()
                        recommendations.append(rec)
                        added_categories.add("sales_decline")

                if "retention" in category or "churn" in str(insight.get("title", "")).lower():
                    if "retention_low" not in added_categories:
                        rec = RECOMMENDATION_TEMPLATES["retention_low"].copy()
                        recommendations.append(rec)
                        added_categories.add("retention_low")

                if "margin" in str(insight.get("title", "")).lower():
                    if "margin_low" not in added_categories:
                        rec = RECOMMENDATION_TEMPLATES["margin_low"].copy()
                        recommendations.append(rec)
                        added_categories.add("margin_low")

                if "convers" in str(insight.get("title", "")).lower():
                    if "conversion_low" not in added_categories:
                        rec = RECOMMENDATION_TEMPLATES["conversion_low"].copy()
                        recommendations.append(rec)
                        added_categories.add("conversion_low")

        # Limita quantidade
        return recommendations[:5]

    def detect_anomalies(
        self,
        data: dict[str, Any],
        sensitivity: float = 2.0,
    ) -> list[dict[str, Any]]:
        """
        Detecta anomalias nos dados usando análise estatística.

        Args:
            data: Dados para análise
            sensitivity: Número de desvios padrão para considerar anomalia

        Returns:
            Lista de anomalias detectadas
        """
        return self._detect_anomalies(data, sensitivity)

    def analyze_trends(
        self,
        data: dict[str, Any],
        min_points: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Analisa tendências nos dados.

        Args:
            data: Dados para análise
            min_points: Mínimo de pontos para análise de tendência

        Returns:
            Lista de tendências identificadas
        """
        return self._analyze_trends(data, min_points)

    def _analyze_growth(self, metrics: dict[str, Any]) -> list[dict[str, Any]]:
        """Analisa métricas de crescimento."""
        insights = []

        growth_metrics = [
            ("sales_growth", "Vendas"),
            ("revenue_growth", "Receita"),
            ("customer_growth", "Clientes"),
        ]

        for metric_key, metric_name in growth_metrics:
            if metric_key in metrics:
                value = metrics[metric_key]
                insight = self._create_growth_insight(metric_name, value)
                if insight:
                    insights.append(insight)

        return insights

    def _create_growth_insight(
        self,
        metric_name: str,
        value: float,
    ) -> dict[str, Any] | None:
        """Cria insight de crescimento baseado no valor."""
        thresholds = INSIGHT_THRESHOLDS["growth"]

        if value >= thresholds["exceptional"]:
            template = INSIGHT_TEMPLATES["growth_exceptional"]
        elif value >= thresholds["good"]:
            template = INSIGHT_TEMPLATES["growth_good"]
        elif value <= thresholds["critical"]:
            template = INSIGHT_TEMPLATES["growth_critical"]
        elif value <= thresholds["warning"]:
            template = INSIGHT_TEMPLATES["growth_warning"]
        else:
            return None

        return {
            "type": template["type"],
            "category": "growth",
            "title": template["title"],
            "description": template["template"].format(metric=metric_name, value=abs(value)),
            "impact": template["impact"],
            "confidence": 0.85,
            "value": value,
            "metric": metric_name,
        }

    def _analyze_retention(self, metrics: dict[str, Any]) -> list[dict[str, Any]]:
        """Analisa métricas de retenção."""
        insights = []

        if "retention_rate" in metrics:
            rate = metrics["retention_rate"]
            thresholds = INSIGHT_THRESHOLDS["retention"]

            if rate < thresholds["warning"]:
                template = INSIGHT_TEMPLATES["retention_warning"]
                insights.append(
                    {
                        "type": template["type"],
                        "category": "retention",
                        "title": template["title"],
                        "description": template["template"].format(value=rate),
                        "impact": template["impact"],
                        "confidence": 0.88,
                        "value": rate,
                    }
                )

        return insights

    def _analyze_margin(self, metrics: dict[str, Any]) -> list[dict[str, Any]]:
        """Analisa métricas de margem."""
        insights = []

        margin_metrics = ["profit_margin", "margin", "gross_margin"]
        for metric_key in margin_metrics:
            if metric_key in metrics:
                value = metrics[metric_key]
                thresholds = INSIGHT_THRESHOLDS["margin"]

                if value >= thresholds["excellent"]:
                    template = INSIGHT_TEMPLATES["margin_excellent"]
                elif value < thresholds["warning"]:
                    template = INSIGHT_TEMPLATES["margin_warning"]
                else:
                    continue

                insights.append(
                    {
                        "type": template["type"],
                        "category": "financial",
                        "title": template["title"],
                        "description": template["template"].format(value=value),
                        "impact": template["impact"],
                        "confidence": 0.90,
                        "value": value,
                    }
                )
                break

        return insights

    def _analyze_conversion(self, metrics: dict[str, Any]) -> list[dict[str, Any]]:
        """Analisa métricas de conversão."""
        insights = []

        if "conversion_rate" in metrics:
            rate = metrics["conversion_rate"]
            thresholds = INSIGHT_THRESHOLDS["conversion"]

            if rate >= thresholds["excellent"]:
                insights.append(
                    {
                        "type": "positive",
                        "category": "sales",
                        "title": "Excelente Taxa de Conversão",
                        "description": f"Taxa de conversão de {rate}% está acima da média do mercado.",
                        "impact": "medium",
                        "confidence": 0.82,
                        "value": rate,
                    }
                )
            elif rate < thresholds["warning"]:
                insights.append(
                    {
                        "type": "warning",
                        "category": "sales",
                        "title": "Taxa de Conversão Baixa",
                        "description": f"Taxa de conversão de {rate}% indica necessidade de otimização do funil.",
                        "impact": "high",
                        "confidence": 0.85,
                        "value": rate,
                    }
                )

        return insights

    def _detect_anomalies(
        self,
        data: dict[str, Any],
        sensitivity: float = 2.0,
    ) -> list[dict[str, Any]]:
        """Detecta anomalias usando Z-score."""
        insights = []

        # Procura séries temporais nos dados
        for source, source_data in data.items():
            if not isinstance(source_data, dict):
                continue

            # Busca campos com dados diários/temporais
            for key in ["by_day", "daily", "time_series"]:
                if key in source_data and isinstance(source_data[key], list):
                    series = source_data[key]
                    if len(series) < 5:
                        continue

                    # Extrai valores
                    values = []
                    for item in series:
                        if isinstance(item, dict):
                            for val_key in ["value", "total", "count", "amount"]:
                                if val_key in item:
                                    values.append((item, item[val_key]))
                                    break

                    if len(values) < 5:
                        continue

                    # Calcula estatísticas
                    nums = [v[1] for v in values]
                    avg = sum(nums) / len(nums)
                    variance = sum((x - avg) ** 2 for x in nums) / len(nums)
                    std = variance**0.5

                    if std == 0:
                        continue

                    # Detecta anomalias
                    for item, value in values:
                        z_score = (value - avg) / std
                        if abs(z_score) > sensitivity:
                            date = item.get("date", item.get("period", "N/A"))
                            anomaly_type = "spike" if z_score > 0 else "drop"
                            template = INSIGHT_TEMPLATES[f"anomaly_{anomaly_type}"]

                            insights.append(
                                {
                                    "type": template["type"],
                                    "category": source,
                                    "title": template["title"],
                                    "description": template["template"].format(
                                        date=date, value=value, expected=round(avg, 2), deviation=round(abs(z_score), 1)
                                    ),
                                    "impact": template["impact"],
                                    "confidence": min(0.95, 0.7 + abs(z_score) * 0.1),
                                    "anomaly_type": anomaly_type,
                                    "z_score": round(z_score, 2),
                                }
                            )

        return insights[:5]  # Limita anomalias retornadas

    def _analyze_trends(
        self,
        data: dict[str, Any],
        min_points: int = 5,
    ) -> list[dict[str, Any]]:
        """Analisa tendências nos dados."""
        insights = []

        for source, source_data in data.items():
            if not isinstance(source_data, dict):
                continue

            for key in ["by_day", "daily", "time_series"]:
                if key in source_data and isinstance(source_data[key], list):
                    series = source_data[key]
                    if len(series) < min_points:
                        continue

                    # Extrai valores
                    values = []
                    for item in series:
                        if isinstance(item, dict):
                            for val_key in ["value", "total", "count"]:
                                if val_key in item:
                                    values.append(item[val_key])
                                    break

                    if len(values) < min_points:
                        continue

                    # Analisa tendência (compara primeira e segunda metade)
                    mid = len(values) // 2
                    first_half = sum(values[:mid]) / mid
                    second_half = sum(values[mid:]) / (len(values) - mid)

                    if first_half == 0:
                        continue

                    change = ((second_half - first_half) / first_half) * 100

                    if change > 10:
                        template = INSIGHT_TEMPLATES["trend_up"]
                        direction = "up"
                    elif change < -10:
                        template = INSIGHT_TEMPLATES["trend_down"]
                        direction = "down"
                    else:
                        continue

                    insights.append(
                        {
                            "type": template["type"],
                            "category": source,
                            "title": template["title"],
                            "description": template["template"].format(
                                metric=source.replace("_", " ").title(), change=round(abs(change), 1)
                            ),
                            "impact": template["impact"],
                            "confidence": 0.75,
                            "trend_direction": direction,
                            "change_percent": round(change, 2),
                        }
                    )

        return insights

    def calculate_confidence_score(
        self,
        data_quality: float,
        sample_size: int,
        time_range_days: int,
    ) -> float:
        """
        Calcula score de confiança dos insights.

        Args:
            data_quality: Score de qualidade dos dados (0-100)
            sample_size: Número de registros analisados
            time_range_days: Período de tempo em dias

        Returns:
            Score de confiança (0-1)
        """
        # Normaliza inputs
        quality_factor = data_quality / 100

        # Sample size factor (log scale)
        import math

        sample_factor = min(1.0, math.log10(max(1, sample_size)) / 4)

        # Time range factor
        time_factor = min(1.0, time_range_days / 90)

        # Média ponderada
        confidence = quality_factor * 0.4 + sample_factor * 0.35 + time_factor * 0.25

        return round(min(0.95, max(0.3, confidence)), 2)
