"""Cost AI Service - Inteligência Artificial para Análise de Custos."""

import statistics
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.costing.models import (
    AnalysisType,
    CostAnalysis,
    ProfitabilityLevel,
    ValueAddedType,
)
from modules.financial.costing.repositories import (
    CostActivityRepository,
    CostAllocationRepository,
    CostAnalysisRepository,
    CostObjectRepository,
    CostPoolRepository,
)


class CostAIService:
    """Serviço de IA para análises de custo."""

    def __init__(self, db: AsyncSession):
        """Inicializa o serviço."""
        self.db = db
        self.pool_repo = CostPoolRepository(db)
        self.activity_repo = CostActivityRepository(db)
        self.object_repo = CostObjectRepository(db)
        self.allocation_repo = CostAllocationRepository(db)
        self.analysis_repo = CostAnalysisRepository(db)

    async def analyze_profitability(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        object_ids: list[UUID] = None,
    ) -> dict:
        """Analisa rentabilidade dos objetos de custo."""
        objects, _ = await self.object_repo.list_all(
            condominio_id=condominio_id,
            active=True,
            limit=1000,
        )

        if object_ids:
            objects = [o for o in objects if o.id in object_ids]

        if not objects:
            return {"error": "Nenhum objeto de custo encontrado"}

        # Classificar por rentabilidade
        profitable = []
        marginal = []
        unprofitable = []

        for obj in objects:
            if obj.net_margin_percent >= 10:
                profitable.append(obj)
            elif obj.net_margin_percent >= 0:
                marginal.append(obj)
            else:
                unprofitable.append(obj)

        # Calcular totais
        total_revenue = sum(o.revenue for o in objects)
        total_cost = sum(o.total_cost for o in objects)
        total_margin = total_revenue - total_cost

        # Top 5 mais rentáveis
        top_profitable = sorted(objects, key=lambda x: x.net_margin_percent, reverse=True)[:5]

        # Top 5 menos rentáveis
        bottom_profitable = sorted(objects, key=lambda x: x.net_margin_percent)[:5]

        # Insights
        insights = []

        if len(unprofitable) > len(profitable):
            insights.append(
                {
                    "type": "critical",
                    "message": f"{len(unprofitable)} objetos não rentáveis vs {len(profitable)} rentáveis",
                    "priority": "high",
                }
            )

        if total_margin < 0:
            insights.append(
                {
                    "type": "critical",
                    "message": f"Margem total negativa: R$ {total_margin:,.2f}",
                    "priority": "critical",
                }
            )

        # Concentração de receita
        if profitable:
            top_revenue = max(o.revenue for o in profitable)
            revenue_concentration = (top_revenue / total_revenue * 100) if total_revenue > 0 else 0
            if revenue_concentration > 50:
                insights.append(
                    {
                        "type": "warning",
                        "message": f"Alta concentração de receita: {revenue_concentration:.1f}% em um objeto",
                        "priority": "medium",
                    }
                )

        # Recomendações
        recommendations = []

        for obj in unprofitable[:3]:
            recommendations.append(
                {
                    "action": f"Revisar custos de {obj.name}",
                    "impact": abs(obj.net_margin),
                    "priority": "high" if obj.net_margin < Decimal("-1000") else "medium",
                    "details": f"Margem: {obj.net_margin_percent:.1f}%",
                }
            )

        return {
            "summary": {
                "total_objects": len(objects),
                "profitable_count": len(profitable),
                "marginal_count": len(marginal),
                "unprofitable_count": len(unprofitable),
                "total_revenue": total_revenue,
                "total_cost": total_cost,
                "total_margin": total_margin,
                "avg_margin_percent": (
                    sum(o.net_margin_percent for o in objects) / len(objects) if objects else Decimal("0")
                ),
            },
            "top_profitable": [
                {
                    "id": str(o.id),
                    "name": o.name,
                    "revenue": o.revenue,
                    "margin": o.net_margin,
                    "margin_percent": o.net_margin_percent,
                }
                for o in top_profitable
            ],
            "bottom_profitable": [
                {
                    "id": str(o.id),
                    "name": o.name,
                    "revenue": o.revenue,
                    "margin": o.net_margin,
                    "margin_percent": o.net_margin_percent,
                }
                for o in bottom_profitable
            ],
            "insights": insights,
            "recommendations": recommendations,
        }

    async def analyze_idle_capacity(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
    ) -> dict:
        """Analisa capacidade ociosa."""
        activities, _ = await self.activity_repo.list_all(
            condominio_id=condominio_id,
            active=True,
            limit=1000,
        )

        activities_with_capacity = [a for a in activities if a.practical_capacity and a.practical_capacity > 0]

        if not activities_with_capacity:
            return {"error": "Nenhuma atividade com capacidade definida"}

        # Calcular ociosidade
        total_capacity = sum(a.practical_capacity for a in activities_with_capacity)
        total_used = sum(a.used_capacity for a in activities_with_capacity)
        total_idle = total_capacity - total_used

        idle_cost = Decimal("0")
        high_idle = []  # >50% ociosidade
        low_utilization = []  # <30% utilização

        for activity in activities_with_capacity:
            idle = activity.practical_capacity - activity.used_capacity
            usage_percent = (
                (activity.used_capacity / activity.practical_capacity) * 100
                if activity.practical_capacity > 0
                else Decimal("0")
            )

            if activity.activity_rate:
                cost = idle * activity.activity_rate
                idle_cost += cost

            if usage_percent < 50:
                high_idle.append(
                    {
                        "id": str(activity.id),
                        "name": activity.name,
                        "capacity": activity.practical_capacity,
                        "used": activity.used_capacity,
                        "idle": idle,
                        "usage_percent": usage_percent,
                        "idle_cost": idle * activity.activity_rate if activity.activity_rate else 0,
                    }
                )

            if usage_percent < 30:
                low_utilization.append(activity)

        # Insights
        insights = []
        overall_usage = (total_used / total_capacity * 100) if total_capacity > 0 else 0

        if overall_usage < 60:
            insights.append(
                {
                    "type": "warning",
                    "message": f"Utilização geral baixa: {overall_usage:.1f}%",
                    "priority": "high",
                }
            )

        if idle_cost > Decimal("10000"):
            insights.append(
                {
                    "type": "critical",
                    "message": f"Custo de ociosidade significativo: R$ {idle_cost:,.2f}",
                    "priority": "critical",
                }
            )

        # Recomendações
        recommendations = []

        for activity in sorted(high_idle, key=lambda x: x["idle_cost"], reverse=True)[:3]:
            recommendations.append(
                {
                    "action": f"Otimizar capacidade de {activity['name']}",
                    "impact": activity["idle_cost"],
                    "priority": "high",
                    "details": f"Ociosidade: {100 - activity['usage_percent']:.1f}%",
                }
            )

        return {
            "summary": {
                "total_activities": len(activities_with_capacity),
                "total_capacity": total_capacity,
                "total_used": total_used,
                "total_idle": total_idle,
                "usage_percent": overall_usage,
                "idle_cost": idle_cost,
            },
            "high_idle_activities": high_idle[:10],
            "low_utilization_count": len(low_utilization),
            "insights": insights,
            "recommendations": recommendations,
        }

    async def detect_cost_anomalies(
        self,
        condominio_id: UUID,
        period: str = None,
        z_score_threshold: float = 2.0,
    ) -> dict:
        """Detecta anomalias em custos usando Z-score."""
        allocations, _ = await self.allocation_repo.list_all(
            condominio_id=condominio_id,
            reference_period=period,
            is_reversed=False,
            limit=5000,
        )

        if len(allocations) < 10:
            return {"error": "Dados insuficientes para análise de anomalias"}

        # Calcular estatísticas
        amounts = [float(a.allocated_amount) for a in allocations]
        mean = statistics.mean(amounts)
        stdev = statistics.stdev(amounts) if len(amounts) > 1 else 0

        anomalies = []

        if stdev > 0:
            for allocation in allocations:
                z_score = (float(allocation.allocated_amount) - mean) / stdev
                if abs(z_score) > z_score_threshold:
                    severity = "high" if abs(z_score) > 3 else "medium"
                    anomalies.append(
                        {
                            "id": str(allocation.id),
                            "allocation_number": allocation.allocation_number,
                            "amount": allocation.allocated_amount,
                            "z_score": round(z_score, 2),
                            "severity": severity,
                            "type": "high_value" if z_score > 0 else "low_value",
                            "date": (allocation.allocation_date.isoformat() if allocation.allocation_date else None),
                        }
                    )

        # Ordenar por z_score absoluto
        anomalies.sort(key=lambda x: abs(x["z_score"]), reverse=True)

        # Insights
        insights = []
        if len(anomalies) > len(allocations) * 0.1:
            insights.append(
                {
                    "type": "warning",
                    "message": f"Alto número de anomalias: {len(anomalies)} "
                    f"({len(anomalies) / len(allocations) * 100:.1f}%)",
                    "priority": "medium",
                }
            )

        high_value_anomalies = [a for a in anomalies if a["type"] == "high_value"]
        if high_value_anomalies:
            total_excess = sum(float(a["amount"]) - mean for a in high_value_anomalies)
            insights.append(
                {
                    "type": "info",
                    "message": f"Alocações acima da média representam R$ {total_excess:,.2f} extras",
                    "priority": "low",
                }
            )

        return {
            "summary": {
                "total_allocations": len(allocations),
                "anomalies_count": len(anomalies),
                "anomaly_rate": len(anomalies) / len(allocations) * 100 if allocations else 0,
                "mean_amount": mean,
                "std_deviation": stdev,
                "threshold_used": z_score_threshold,
            },
            "anomalies": anomalies[:20],
            "insights": insights,
        }

    async def suggest_cost_optimization(
        self,
        condominio_id: UUID,
    ) -> dict:
        """Sugere otimizações de custo."""
        # Buscar dados
        activities, _ = await self.activity_repo.list_all(
            condominio_id=condominio_id,
            active=True,
            limit=1000,
        )
        objects, _ = await self.object_repo.list_all(
            condominio_id=condominio_id,
            active=True,
            limit=1000,
        )

        suggestions = []

        # 1. Atividades que não agregam valor
        non_value_activities = [a for a in activities if a.value_added_type == ValueAddedType.NON_VALUE_ADDED]
        if non_value_activities:
            total_non_value_cost = sum(a.total_cost for a in non_value_activities)
            suggestions.append(
                {
                    "category": "value_analysis",
                    "title": "Eliminar atividades sem valor agregado",
                    "description": f"{len(non_value_activities)} atividades identificadas "
                    f"como não agregando valor ao cliente",
                    "potential_savings": total_non_value_cost,
                    "priority": "high",
                    "activities": [
                        {"id": str(a.id), "name": a.name, "cost": a.total_cost} for a in non_value_activities[:5]
                    ],
                }
            )

        # 2. Atividades terceirizáveis
        outsourceable = [a for a in activities if a.is_outsourceable and a.total_cost > 0]
        if outsourceable:
            # Estimativa: terceirização pode economizar 15-25%
            potential = sum(a.total_cost for a in outsourceable) * Decimal("0.20")
            suggestions.append(
                {
                    "category": "outsourcing",
                    "title": "Avaliar terceirização de atividades",
                    "description": f"{len(outsourceable)} atividades candidatas à terceirização",
                    "potential_savings": potential,
                    "priority": "medium",
                    "activities": [{"id": str(a.id), "name": a.name, "cost": a.total_cost} for a in outsourceable[:5]],
                }
            )

        # 3. Atividades automatizáveis
        automatable = [a for a in activities if a.is_automatable and a.total_cost > 0]
        if automatable:
            # Estimativa: automação pode economizar 30-50%
            potential = sum(a.total_cost for a in automatable) * Decimal("0.40")
            suggestions.append(
                {
                    "category": "automation",
                    "title": "Automatizar atividades repetitivas",
                    "description": f"{len(automatable)} atividades candidatas à automação",
                    "potential_savings": potential,
                    "priority": "high",
                    "activities": [{"id": str(a.id), "name": a.name, "cost": a.total_cost} for a in automatable[:5]],
                }
            )

        # 4. Objetos não rentáveis
        unprofitable = [o for o in objects if o.profitability_level == ProfitabilityLevel.UNPROFITABLE]
        if unprofitable:
            total_loss = abs(sum(o.net_margin for o in unprofitable))
            suggestions.append(
                {
                    "category": "profitability",
                    "title": "Revisar produtos/serviços não rentáveis",
                    "description": f"{len(unprofitable)} objetos com margem negativa",
                    "potential_savings": total_loss,
                    "priority": "critical",
                    "objects": [
                        {
                            "id": str(o.id),
                            "name": o.name,
                            "margin": o.net_margin,
                            "margin_percent": o.net_margin_percent,
                        }
                        for o in unprofitable[:5]
                    ],
                }
            )

        # 5. Capacidade ociosa
        high_idle = [
            a for a in activities if a.practical_capacity and a.practical_capacity > 0 and a.capacity_usage_percent < 50
        ]
        if high_idle:
            idle_cost = sum(a.idle_capacity * a.activity_rate for a in high_idle if a.activity_rate)
            suggestions.append(
                {
                    "category": "capacity",
                    "title": "Otimizar capacidade ociosa",
                    "description": f"{len(high_idle)} atividades com utilização < 50%",
                    "potential_savings": idle_cost,
                    "priority": "medium",
                }
            )

        # Ordenar por potencial de economia
        suggestions.sort(key=lambda x: x["potential_savings"], reverse=True)

        # Total de economia potencial
        total_potential = sum(s["potential_savings"] for s in suggestions)

        return {
            "summary": {
                "suggestions_count": len(suggestions),
                "total_potential_savings": total_potential,
            },
            "suggestions": suggestions,
        }

    async def forecast_costs(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        periods_ahead: int = 3,
    ) -> dict:
        """Previsão de custos futuros."""
        # Buscar histórico de alocações
        allocations, _ = await self.allocation_repo.list_all(
            condominio_id=condominio_id,
            is_reversed=False,
            limit=5000,
        )

        if len(allocations) < 30:
            return {"error": "Histórico insuficiente para previsão"}

        # Agrupar por período
        by_period: dict[str, Decimal] = {}
        for alloc in allocations:
            period = alloc.reference_period
            if period not in by_period:
                by_period[period] = Decimal("0")
            by_period[period] += alloc.allocated_amount

        if len(by_period) < 3:
            return {"error": "Necessário pelo menos 3 períodos para previsão"}

        # Ordenar períodos
        periods_sorted = sorted(by_period.keys())
        values = [float(by_period[p]) for p in periods_sorted]

        # Calcular tendência (média móvel simples)
        recent_values = values[-6:] if len(values) >= 6 else values
        avg = statistics.mean(recent_values)

        # Calcular variação mensal
        if len(recent_values) >= 2:
            changes = [
                (recent_values[i] - recent_values[i - 1]) / recent_values[i - 1] if recent_values[i - 1] != 0 else 0
                for i in range(1, len(recent_values))
            ]
            avg_change = statistics.mean(changes) if changes else 0
        else:
            avg_change = 0

        # Gerar previsões
        forecasts = []
        last_period = periods_sorted[-1]
        last_value = values[-1]

        for i in range(1, periods_ahead + 1):
            # Calcular próximo período
            year = int(last_period[:4])
            month = int(last_period[5:7])
            month += i
            while month > 12:
                month -= 12
                year += 1
            next_period = f"{year}-{month:02d}"

            # Projetar valor
            projected = last_value * (1 + avg_change) ** i

            # Cenários
            pessimist = projected * Decimal("1.10")  # +10%
            optimist = projected * Decimal("0.90")  # -10%

            forecasts.append(
                {
                    "period": next_period,
                    "pessimist": round(pessimist, 2),
                    "realistic": round(projected, 2),
                    "optimist": round(optimist, 2),
                    "confidence": max(0, min(100, 80 - i * 10)),  # Diminui com distância
                }
            )

        return {
            "historical_summary": {
                "periods_analyzed": len(periods_sorted),
                "avg_monthly_cost": avg,
                "avg_monthly_change_percent": avg_change * 100,
                "last_period": last_period,
                "last_value": last_value,
            },
            "forecasts": forecasts,
            "methodology": "Moving average with trend extrapolation",
        }

    async def run_analysis(
        self,
        analysis: CostAnalysis,
        condominio_id: UUID,
    ) -> CostAnalysis:
        """Executa uma análise de custo."""
        analysis.start()
        await self.analysis_repo.update(analysis)

        try:
            results = {}

            if analysis.analysis_type == AnalysisType.PROFITABILITY:
                results = await self.analyze_profitability(
                    condominio_id=condominio_id,
                    object_ids=analysis.object_ids,
                )

            elif analysis.analysis_type == AnalysisType.IDLE_CAPACITY:
                results = await self.analyze_idle_capacity(
                    condominio_id=condominio_id,
                )

            elif analysis.analysis_type == AnalysisType.VARIANCE:
                results = await self.detect_cost_anomalies(
                    condominio_id=condominio_id,
                    period=analysis.reference_period,
                )

            elif analysis.analysis_type == AnalysisType.TREND:
                results = await self.forecast_costs(
                    condominio_id=condominio_id,
                )

            elif analysis.analysis_type == AnalysisType.ABC_COSTING:
                # Combinar várias análises
                profitability = await self.analyze_profitability(condominio_id)
                capacity = await self.analyze_idle_capacity(condominio_id)
                optimization = await self.suggest_cost_optimization(condominio_id)

                results = {
                    "profitability": profitability.get("summary", {}),
                    "capacity": capacity.get("summary", {}),
                    "optimization": optimization.get("summary", {}),
                    "all_insights": (profitability.get("insights", []) + capacity.get("insights", [])),
                    "all_recommendations": (
                        profitability.get("recommendations", []) + optimization.get("suggestions", [])
                    ),
                }

            # Atualizar análise com resultados
            analysis.results = results
            if "summary" in results:
                summary = results["summary"]
                analysis.total_cost = Decimal(str(summary.get("total_cost", 0)))
                analysis.total_revenue = Decimal(str(summary.get("total_revenue", 0)))
                analysis.total_margin = Decimal(str(summary.get("total_margin", 0)))

            if "insights" in results:
                analysis.insights = results["insights"]
            if "recommendations" in results:
                analysis.recommendations = results["recommendations"]

            analysis.complete(results)

        except (ValueError, TypeError, RuntimeError) as e:
            analysis.fail(str(e))

        await self.analysis_repo.update(analysis)
        return analysis
