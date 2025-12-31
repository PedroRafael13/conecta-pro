"""Serviço de IA para Compras."""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class PurchaseAIService:
    """Serviço de IA para análises e sugestões em compras."""

    def __init__(self):
        """Inicializa o serviço de IA."""
        pass

    def analyze_supplier_performance(
        self,
        supplier_id: UUID,
        orders: List[Dict[str, Any]],
        receipts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analisa performance do fornecedor.

        Args:
            supplier_id: ID do fornecedor
            orders: Lista de ordens de compra do fornecedor
            receipts: Lista de recebimentos do fornecedor

        Returns:
            Análise de performance com scores e recomendações
        """
        if not orders:
            return {
                "supplier_id": str(supplier_id),
                "score": 0,
                "level": "sem_historico",
                "metrics": {},
                "recommendations": ["Não há histórico suficiente para análise"],
            }

        # Métricas de entrega
        on_time_deliveries = 0
        late_deliveries = 0
        total_delay_days = 0

        for order in orders:
            expected = order.get("expected_delivery_date")
            actual = order.get("actual_delivery_date")
            if expected and actual:
                if actual <= expected:
                    on_time_deliveries += 1
                else:
                    late_deliveries += 1
                    delay = (actual - expected).days
                    total_delay_days += delay

        delivery_rate = (
            on_time_deliveries / len(orders) * 100 if orders else 0
        )

        # Métricas de qualidade (baseado em recebimentos)
        total_accepted = Decimal("0")
        total_rejected = Decimal("0")
        divergence_count = 0

        for receipt in receipts:
            total_accepted += Decimal(str(receipt.get("total_accepted", 0)))
            total_rejected += Decimal(str(receipt.get("total_rejected", 0)))
            if receipt.get("has_divergence"):
                divergence_count += 1

        total_received = total_accepted + total_rejected
        quality_rate = (
            float(total_accepted / total_received * 100)
            if total_received > 0
            else 100
        )

        # Métricas de preço
        price_variations = []
        for order in orders:
            items = order.get("items", [])
            for item in items:
                if item.get("unit_price") and item.get("product_id"):
                    price_variations.append(float(item.get("unit_price")))

        avg_price_score = 70  # Score base
        if price_variations:
            avg_price = sum(price_variations) / len(price_variations)
            # Ajuste baseado em variação (menor variação = melhor)
            variance = sum((p - avg_price) ** 2 for p in price_variations) / len(
                price_variations
            )
            if variance < 100:
                avg_price_score = 90
            elif variance < 500:
                avg_price_score = 75
            else:
                avg_price_score = 60

        # Score geral ponderado
        # Entrega: 40%, Qualidade: 35%, Preço: 25%
        overall_score = (
            delivery_rate * 0.40 + quality_rate * 0.35 + avg_price_score * 0.25
        )

        # Determinar nível
        if overall_score >= 85:
            level = "excelente"
        elif overall_score >= 70:
            level = "bom"
        elif overall_score >= 55:
            level = "regular"
        else:
            level = "ruim"

        # Recomendações
        recommendations = []
        if delivery_rate < 80:
            recommendations.append(
                f"Taxa de entrega no prazo ({delivery_rate:.1f}%) está abaixo do ideal. "
                "Considere negociar prazos mais realistas ou penalidades."
            )
        if quality_rate < 95:
            recommendations.append(
                f"Taxa de aceitação ({quality_rate:.1f}%) indica problemas de qualidade. "
                "Revise especificações técnicas com o fornecedor."
            )
        if divergence_count > len(receipts) * 0.1:
            recommendations.append(
                f"{divergence_count} recebimentos com divergência. "
                "Alinhe processo de conferência e documentação."
            )
        if not recommendations:
            recommendations.append(
                "Fornecedor com bom desempenho. Considere para parcerias estratégicas."
            )

        return {
            "supplier_id": str(supplier_id),
            "score": round(overall_score, 1),
            "level": level,
            "metrics": {
                "delivery_rate": round(delivery_rate, 1),
                "quality_rate": round(quality_rate, 1),
                "price_score": avg_price_score,
                "total_orders": len(orders),
                "on_time_deliveries": on_time_deliveries,
                "late_deliveries": late_deliveries,
                "average_delay_days": (
                    total_delay_days / late_deliveries if late_deliveries > 0 else 0
                ),
                "divergence_count": divergence_count,
            },
            "recommendations": recommendations,
        }

    def suggest_suppliers(
        self,
        product_id: UUID,
        quantity: Decimal,
        historical_purchases: List[Dict[str, Any]],
        supplier_performances: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Sugere fornecedores para um produto.

        Args:
            product_id: ID do produto
            quantity: Quantidade desejada
            historical_purchases: Histórico de compras do produto
            supplier_performances: Performances dos fornecedores

        Returns:
            Lista de fornecedores sugeridos com scores
        """
        suggestions = []

        # Agrupa por fornecedor
        supplier_history = {}
        for purchase in historical_purchases:
            supplier_id = purchase.get("supplier_id")
            if supplier_id:
                if supplier_id not in supplier_history:
                    supplier_history[supplier_id] = {
                        "purchases": [],
                        "total_quantity": Decimal("0"),
                        "total_value": Decimal("0"),
                        "prices": [],
                    }
                supplier_history[supplier_id]["purchases"].append(purchase)
                supplier_history[supplier_id]["total_quantity"] += Decimal(
                    str(purchase.get("quantity", 0))
                )
                supplier_history[supplier_id]["total_value"] += Decimal(
                    str(purchase.get("total", 0))
                )
                if purchase.get("unit_price"):
                    supplier_history[supplier_id]["prices"].append(
                        float(purchase.get("unit_price"))
                    )

        for supplier_id, history in supplier_history.items():
            performance = supplier_performances.get(supplier_id, {})

            # Calcular score de preço (menor preço = maior score)
            if history["prices"]:
                avg_price = sum(history["prices"]) / len(history["prices"])
                min_price = min(history["prices"])
                price_score = min(100, (min_price / avg_price) * 100) if avg_price > 0 else 50
            else:
                price_score = 50

            # Score de experiência (mais compras = maior score)
            experience_score = min(100, len(history["purchases"]) * 10)

            # Score de performance do fornecedor
            performance_score = performance.get("score", 50)

            # Score geral
            # Performance: 40%, Preço: 35%, Experiência: 25%
            overall_score = (
                performance_score * 0.40 + price_score * 0.35 + experience_score * 0.25
            )

            suggestions.append(
                {
                    "supplier_id": supplier_id,
                    "score": round(overall_score, 1),
                    "last_price": history["prices"][-1] if history["prices"] else None,
                    "average_price": (
                        round(sum(history["prices"]) / len(history["prices"]), 2)
                        if history["prices"]
                        else None
                    ),
                    "purchase_count": len(history["purchases"]),
                    "total_quantity": float(history["total_quantity"]),
                    "performance_level": performance.get("level", "desconhecido"),
                    "reasons": [],
                }
            )

        # Ordena por score
        suggestions.sort(key=lambda x: x["score"], reverse=True)

        # Adiciona razões
        for i, suggestion in enumerate(suggestions):
            reasons = []
            if i == 0:
                reasons.append("Melhor score geral")
            if suggestion.get("performance_level") == "excelente":
                reasons.append("Excelente performance histórica")
            if suggestion["purchase_count"] >= 5:
                reasons.append(f"Fornecedor frequente ({suggestion['purchase_count']} compras)")
            if suggestion.get("last_price") and suggestion.get("average_price"):
                if suggestion["last_price"] <= suggestion["average_price"]:
                    reasons.append("Último preço abaixo ou igual à média")
            suggestion["reasons"] = reasons

        return suggestions[:5]  # Top 5

    def optimize_quotation_selection(
        self,
        quotations: List[Dict[str, Any]],
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Otimiza seleção de cotação.

        Args:
            quotations: Lista de cotações para comparar
            weights: Pesos customizados (price, delivery, quality)

        Returns:
            Análise comparativa e recomendação
        """
        if not quotations:
            return {
                "recommendation": None,
                "analysis": [],
                "message": "Nenhuma cotação para análise",
            }

        # Pesos padrão
        if not weights:
            weights = {"price": 0.40, "delivery": 0.35, "quality": 0.25}

        analysis = []

        # Encontrar min/max para normalização
        prices = [float(q.get("total", 0)) for q in quotations if q.get("total")]
        deliveries = [
            q.get("delivery_days", 30) for q in quotations if q.get("delivery_days")
        ]

        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 1
        min_delivery = min(deliveries) if deliveries else 0
        max_delivery = max(deliveries) if deliveries else 30

        for quotation in quotations:
            total = float(quotation.get("total", 0))
            delivery_days = quotation.get("delivery_days", 30)
            technical_score = float(quotation.get("technical_score", 50) or 50)
            commercial_score = float(quotation.get("commercial_score", 50) or 50)
            delivery_score = float(quotation.get("delivery_score", 50) or 50)

            # Normalizar preço (menor = melhor, então invertemos)
            if max_price > min_price:
                price_normalized = 100 - (
                    (total - min_price) / (max_price - min_price) * 100
                )
            else:
                price_normalized = 100

            # Normalizar prazo (menor = melhor, então invertemos)
            if max_delivery > min_delivery:
                delivery_normalized = 100 - (
                    (delivery_days - min_delivery) / (max_delivery - min_delivery) * 100
                )
            else:
                delivery_normalized = 100

            # Score de qualidade (média dos scores técnico e comercial)
            quality_normalized = (technical_score + commercial_score) / 2

            # Score final ponderado
            final_score = (
                price_normalized * weights["price"]
                + delivery_normalized * weights["delivery"]
                + quality_normalized * weights["quality"]
            )

            analysis.append(
                {
                    "quotation_id": quotation.get("id"),
                    "quotation_number": quotation.get("number"),
                    "supplier_id": quotation.get("supplier_id"),
                    "total": total,
                    "delivery_days": delivery_days,
                    "scores": {
                        "price": round(price_normalized, 1),
                        "delivery": round(delivery_normalized, 1),
                        "quality": round(quality_normalized, 1),
                        "final": round(final_score, 1),
                    },
                    "pros": [],
                    "cons": [],
                }
            )

        # Ordenar por score final
        analysis.sort(key=lambda x: x["scores"]["final"], reverse=True)

        # Identificar pros/cons
        best_price_id = min(analysis, key=lambda x: x["total"])["quotation_id"]
        best_delivery_id = min(analysis, key=lambda x: x["delivery_days"])["quotation_id"]

        for item in analysis:
            if item["quotation_id"] == best_price_id:
                item["pros"].append("Melhor preço")
            if item["quotation_id"] == best_delivery_id:
                item["pros"].append("Menor prazo de entrega")
            if item["scores"]["quality"] >= 80:
                item["pros"].append("Alta qualidade técnica")
            if item["scores"]["price"] < 50:
                item["cons"].append("Preço acima da média")
            if item["scores"]["delivery"] < 50:
                item["cons"].append("Prazo acima da média")

        # Recomendação
        recommended = analysis[0] if analysis else None

        return {
            "recommendation": recommended,
            "analysis": analysis,
            "message": (
                f"Recomendamos a cotação {recommended['quotation_number']} "
                f"com score final de {recommended['scores']['final']}"
                if recommended
                else "Sem recomendação"
            ),
            "criteria": weights,
        }

    def predict_demand(
        self,
        product_id: UUID,
        historical_consumption: List[Dict[str, Any]],
        forecast_months: int = 3,
    ) -> Dict[str, Any]:
        """
        Prevê demanda de um produto.

        Args:
            product_id: ID do produto
            historical_consumption: Histórico de consumo mensal
            forecast_months: Meses para prever

        Returns:
            Previsão de demanda com cenários
        """
        if len(historical_consumption) < 3:
            return {
                "product_id": str(product_id),
                "forecast": [],
                "confidence": "baixa",
                "message": "Histórico insuficiente para previsão (mínimo 3 meses)",
            }

        # Ordenar por data
        sorted_data = sorted(
            historical_consumption, key=lambda x: x.get("month", "")
        )

        # Extrair quantidades
        quantities = [float(d.get("quantity", 0)) for d in sorted_data]

        # Média móvel simples (últimos 3 meses)
        recent = quantities[-3:]
        avg = sum(recent) / len(recent)

        # Tendência (variação percentual)
        if len(quantities) >= 6:
            old_avg = sum(quantities[-6:-3]) / 3
            trend = (avg - old_avg) / old_avg if old_avg > 0 else 0
        else:
            trend = 0

        # Sazonalidade (simplificada)
        seasonality = {}
        for data in sorted_data:
            month = data.get("month", "")[-2:]  # Último 2 caracteres = mês
            if month:
                if month not in seasonality:
                    seasonality[month] = []
                seasonality[month].append(float(data.get("quantity", 0)))

        seasonal_factors = {}
        overall_avg = sum(quantities) / len(quantities) if quantities else 1
        for month, values in seasonality.items():
            month_avg = sum(values) / len(values)
            seasonal_factors[month] = month_avg / overall_avg if overall_avg > 0 else 1

        # Gerar previsões
        forecast = []
        current_date = datetime.utcnow()

        for i in range(1, forecast_months + 1):
            future_date = current_date + timedelta(days=30 * i)
            month_key = future_date.strftime("%m")
            seasonal_factor = seasonal_factors.get(month_key, 1.0)

            # Previsão base com tendência e sazonalidade
            base = avg * (1 + trend * i) * seasonal_factor

            forecast.append(
                {
                    "period": future_date.strftime("%Y-%m"),
                    "pessimistic": round(base * 0.8, 0),
                    "realistic": round(base, 0),
                    "optimistic": round(base * 1.2, 0),
                    "seasonal_factor": round(seasonal_factor, 2),
                }
            )

        # Determinar confiança
        if len(quantities) >= 12:
            confidence = "alta"
        elif len(quantities) >= 6:
            confidence = "media"
        else:
            confidence = "baixa"

        return {
            "product_id": str(product_id),
            "forecast": forecast,
            "confidence": confidence,
            "metrics": {
                "average_consumption": round(avg, 2),
                "trend_percentage": round(trend * 100, 1),
                "data_points": len(quantities),
            },
            "recommendations": self._generate_demand_recommendations(
                avg, trend, forecast
            ),
        }

    def _generate_demand_recommendations(
        self,
        avg: float,
        trend: float,
        forecast: List[Dict[str, Any]],
    ) -> List[str]:
        """Gera recomendações baseadas na previsão de demanda."""
        recommendations = []

        if trend > 0.1:
            recommendations.append(
                f"Demanda crescente ({trend*100:.1f}%). "
                "Considere aumentar estoque de segurança."
            )
        elif trend < -0.1:
            recommendations.append(
                f"Demanda decrescente ({trend*100:.1f}%). "
                "Revise níveis de estoque para evitar excesso."
            )

        if forecast:
            max_forecast = max(f["realistic"] for f in forecast)
            if max_forecast > avg * 1.5:
                recommendations.append(
                    "Pico de demanda previsto. Antecipe compras para garantir estoque."
                )

        if not recommendations:
            recommendations.append(
                "Demanda estável. Mantenha política atual de reposição."
            )

        return recommendations

    def calculate_reorder_point(
        self,
        average_daily_consumption: Decimal,
        lead_time_days: int,
        safety_stock_days: int = 7,
        service_level: float = 0.95,
    ) -> Dict[str, Any]:
        """
        Calcula ponto de pedido.

        Args:
            average_daily_consumption: Consumo médio diário
            lead_time_days: Prazo de entrega em dias
            safety_stock_days: Dias de estoque de segurança
            service_level: Nível de serviço desejado (0-1)

        Returns:
            Ponto de pedido e estoque de segurança
        """
        # Estoque de segurança
        safety_stock = average_daily_consumption * Decimal(str(safety_stock_days))

        # Ponto de pedido
        reorder_point = (
            average_daily_consumption * Decimal(str(lead_time_days)) + safety_stock
        )

        # Quantidade econômica de pedido (EOQ simplificado)
        # Assumindo custo de pedido = 50 e custo de manutenção = 20% do valor
        annual_demand = average_daily_consumption * 365
        order_cost = Decimal("50")
        holding_cost_rate = Decimal("0.2")

        # EOQ = sqrt(2 * D * S / H)
        # Simplificado para evitar complexidade
        eoq = (
            annual_demand * 2 * order_cost / (annual_demand * holding_cost_rate)
        ) ** Decimal("0.5")

        return {
            "reorder_point": round(float(reorder_point), 0),
            "safety_stock": round(float(safety_stock), 0),
            "economic_order_quantity": round(float(eoq), 0),
            "lead_time_days": lead_time_days,
            "service_level": service_level,
            "recommendations": [
                f"Faça pedido quando estoque atingir {round(float(reorder_point), 0)} unidades",
                f"Mantenha estoque de segurança de {round(float(safety_stock), 0)} unidades",
                f"Quantidade ideal por pedido: {round(float(eoq), 0)} unidades",
            ],
        }

    def analyze_purchase_risks(
        self,
        requisition: Dict[str, Any],
        supplier_performances: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analisa riscos de uma compra.

        Args:
            requisition: Dados da requisição
            supplier_performances: Performances dos fornecedores

        Returns:
            Análise de riscos
        """
        risks = []

        # Risco de prazo
        needed_by = requisition.get("needed_by_date")
        if needed_by:
            days_until = (needed_by - datetime.utcnow().date()).days
            if days_until < 7:
                risks.append(
                    {
                        "type": "prazo",
                        "level": "alto",
                        "description": f"Apenas {days_until} dias até a data necessária",
                        "mitigation": "Priorize fornecedores com entrega rápida",
                    }
                )
            elif days_until < 14:
                risks.append(
                    {
                        "type": "prazo",
                        "level": "medio",
                        "description": f"{days_until} dias até a data necessária",
                        "mitigation": "Monitore de perto o processo de cotação",
                    }
                )

        # Risco de fornecedor único
        suggested_supplier = requisition.get("suggested_supplier_id")
        if suggested_supplier and not requisition.get("supplier_justification"):
            risks.append(
                {
                    "type": "fornecedor_unico",
                    "level": "medio",
                    "description": "Fornecedor único sugerido sem justificativa",
                    "mitigation": "Solicite justificativa ou obtenha múltiplas cotações",
                }
            )

        # Risco de valor
        estimated_total = requisition.get("estimated_total", 0)
        if float(estimated_total) > 50000:
            risks.append(
                {
                    "type": "valor_alto",
                    "level": "alto",
                    "description": f"Valor estimado alto (R$ {float(estimated_total):,.2f})",
                    "mitigation": "Requer aprovação de níveis superiores",
                }
            )
        elif float(estimated_total) > 10000:
            risks.append(
                {
                    "type": "valor_alto",
                    "level": "medio",
                    "description": f"Valor estimado considerável (R$ {float(estimated_total):,.2f})",
                    "mitigation": "Obtenha pelo menos 3 cotações",
                }
            )

        # Risco de qualidade do fornecedor
        if suggested_supplier and supplier_performances:
            performance = supplier_performances.get(str(suggested_supplier), {})
            if performance.get("level") == "ruim":
                risks.append(
                    {
                        "type": "qualidade_fornecedor",
                        "level": "alto",
                        "description": "Fornecedor sugerido tem histórico ruim",
                        "mitigation": "Considere outros fornecedores ou exija garantias",
                    }
                )

        # Determinar risco geral
        high_risks = sum(1 for r in risks if r["level"] == "alto")
        medium_risks = sum(1 for r in risks if r["level"] == "medio")

        if high_risks >= 2:
            overall_level = "critico"
        elif high_risks >= 1:
            overall_level = "alto"
        elif medium_risks >= 2:
            overall_level = "medio"
        elif medium_risks >= 1 or risks:
            overall_level = "baixo"
        else:
            overall_level = "minimo"

        return {
            "requisition_id": requisition.get("id"),
            "overall_level": overall_level,
            "risk_count": len(risks),
            "high_risk_count": high_risks,
            "risks": risks,
            "recommendations": [r["mitigation"] for r in risks],
        }
