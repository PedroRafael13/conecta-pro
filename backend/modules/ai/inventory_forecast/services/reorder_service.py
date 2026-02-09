"""
Reorder Service - AI Inventory Forecasting

Servico para geracao de sugestoes de reposicao de estoque
baseado em previsoes de demanda.
"""

import logging
import math
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from modules.ai.inventory_forecast.models.forecast import (
    Forecast,
    ForecastType,
)
from modules.ai.inventory_forecast.repositories.forecast_repository import (
    ForecastRepository,
)
from modules.ai.inventory_forecast.schemas.forecast_schemas import (
    ReorderListResponse,
    ReorderSuggestion,
)

logger = logging.getLogger(__name__)


class ReorderService:
    """
    Servico de sugestoes de reposicao.

    Analisa previsoes e estoque atual para gerar
    recomendacoes de compra.
    """

    # Niveis de urgencia
    URGENCY_CRITICAL = "CRITICAL"  # < 3 dias de estoque
    URGENCY_HIGH = "HIGH"  # 3-7 dias de estoque
    URGENCY_MEDIUM = "MEDIUM"  # 7-14 dias de estoque
    URGENCY_LOW = "LOW"  # > 14 dias de estoque

    def __init__(self, db: Session):
        """Inicializa service."""
        self.db = db
        self.repository = ForecastRepository(db)

    def generate_reorder_suggestions(
        self,
        products_stock: list[dict],
        default_lead_time: int = 7,
        service_level: float = 0.95,
    ) -> ReorderListResponse:
        """
        Gera sugestoes de reposicao para lista de produtos.

        Args:
            products_stock: Lista de {product_id, current_stock, lead_time_days}
            default_lead_time: Lead time padrao se nao especificado
            service_level: Nivel de servico desejado (0.90-0.99)

        Returns:
            ReorderListResponse: Lista de sugestoes
        """
        logger.info(f"Gerando sugestoes para {len(products_stock)} produtos")

        suggestions = []
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for product in products_stock:
            product_id = product["product_id"]
            current_stock = product.get("current_stock", 0)
            lead_time = product.get("lead_time_days", default_lead_time)

            try:
                suggestion = self._generate_product_suggestion(
                    product_id=product_id,
                    current_stock=current_stock,
                    lead_time_days=lead_time,
                    service_level=service_level,
                    product_info=product,
                )

                if suggestion:
                    suggestions.append(suggestion)

                    # Contar urgencias
                    urgency_key = suggestion.urgency.lower()
                    if urgency_key in counts:
                        counts[urgency_key] += 1

            except Exception as e:
                logger.error(f"Erro ao gerar sugestao para {product_id}: {e}")

        # Ordenar por urgencia
        urgency_order = {
            self.URGENCY_CRITICAL: 0,
            self.URGENCY_HIGH: 1,
            self.URGENCY_MEDIUM: 2,
            self.URGENCY_LOW: 3,
        }
        suggestions.sort(key=lambda x: urgency_order.get(x.urgency, 99))

        return ReorderListResponse(
            items=suggestions,
            total=len(suggestions),
            critical_count=counts["critical"],
            high_count=counts["high"],
            medium_count=counts["medium"],
            low_count=counts["low"],
        )

    def _generate_product_suggestion(
        self,
        product_id: UUID,
        current_stock: float,
        lead_time_days: int,
        service_level: float,
        product_info: dict,
    ) -> ReorderSuggestion | None:
        """Gera sugestao para um produto."""
        # Buscar previsao mais recente
        forecast = self.repository.get_latest_forecast(product_id, ForecastType.DEMAND)

        if not forecast:
            logger.warning(f"Sem previsao para produto {product_id}")
            return None

        # Usar valores da previsao
        avg_daily_demand = forecast.avg_daily_demand
        if avg_daily_demand <= 0:
            return None

        # Calcular safety stock
        safety_stock = forecast.suggested_safety_stock or 0
        if safety_stock == 0:
            # Calcular se nao disponivel
            safety_stock = self._calculate_safety_stock(
                avg_daily_demand,
                lead_time_days,
                service_level,
            )

        # Calcular ponto de reposicao
        reorder_point = forecast.suggested_reorder_point or ((avg_daily_demand * lead_time_days) + safety_stock)

        # Calcular dias de estoque restante
        days_remaining = int(current_stock / avg_daily_demand) if avg_daily_demand > 0 else 999

        # Determinar urgencia
        urgency = self._determine_urgency(days_remaining, lead_time_days)

        # Calcular data estimada de stockout
        stockout_date = None
        if days_remaining < 365:
            stockout_date = date.today() + timedelta(days=days_remaining)

        # Calcular quantidade sugerida
        suggested_quantity = forecast.suggested_reorder_quantity or (
            avg_daily_demand * 30  # 30 dias de cobertura
        )

        # Ajustar quantidade se estoque muito baixo
        if current_stock < reorder_point:
            # Adicionar deficit atual
            deficit = reorder_point - current_stock
            suggested_quantity = max(suggested_quantity, deficit + (avg_daily_demand * 14))

        # Gerar nota baseada na urgencia
        notes = self._generate_notes(urgency, days_remaining, lead_time_days, forecast)

        return ReorderSuggestion(
            product_id=product_id,
            product_code=product_info.get("code", forecast.product_code),
            product_name=product_info.get("name", forecast.product_name),
            current_stock=round(current_stock, 2),
            reorder_point=round(reorder_point, 2),
            safety_stock=round(safety_stock, 2),
            suggested_quantity=round(suggested_quantity, 2),
            avg_daily_demand=round(avg_daily_demand, 2),
            days_of_stock_remaining=days_remaining,
            lead_time_days=lead_time_days,
            urgency=urgency,
            estimated_stockout_date=stockout_date,
            confidence_score=forecast.confidence_score or 0,
            notes=notes,
        )

    def _calculate_safety_stock(
        self,
        avg_daily_demand: float,
        lead_time_days: int,
        service_level: float,
    ) -> float:
        """Calcula safety stock."""
        # Z-score para nivel de servico
        z_scores = {
            0.90: 1.28,
            0.95: 1.65,
            0.98: 2.05,
            0.99: 2.33,
        }

        # Encontrar z-score mais proximo
        z = 1.65  # Default para 95%
        for level, score in sorted(z_scores.items()):
            if service_level <= level:
                z = score
                break

        # Assumir desvio padrao de 30% da media
        std_demand = avg_daily_demand * 0.3

        # Safety stock = z * std * sqrt(lead_time)
        return z * std_demand * math.sqrt(lead_time_days)

    def _determine_urgency(self, days_remaining: int, lead_time_days: int) -> str:
        """Determina nivel de urgencia."""
        # Considerar lead time na analise
        buffer_days = days_remaining - lead_time_days

        if buffer_days < 0:
            return self.URGENCY_CRITICAL
        elif buffer_days < 3:
            return self.URGENCY_HIGH
        elif buffer_days < 7:
            return self.URGENCY_MEDIUM
        else:
            return self.URGENCY_LOW

    def _generate_notes(self, urgency: str, days_remaining: int, lead_time_days: int, forecast: Forecast) -> str:
        """Gera notas explicativas."""
        notes = []

        if urgency == self.URGENCY_CRITICAL:
            notes.append("ACAO URGENTE: Estoque insuficiente para cobrir lead time!")
        elif urgency == self.URGENCY_HIGH:
            notes.append("Iniciar reposicao imediatamente.")
        elif urgency == self.URGENCY_MEDIUM:
            notes.append("Planejar reposicao em breve.")

        # Adicionar info de confianca
        if forecast.confidence_score:
            if forecast.confidence_score >= 80:
                notes.append(f"Previsao confiavel ({forecast.confidence_score:.0f}%).")
            elif forecast.confidence_score >= 60:
                notes.append(f"Previsao moderada ({forecast.confidence_score:.0f}%).")
            else:
                notes.append(f"Previsao incerta ({forecast.confidence_score:.0f}%), considerar margem extra.")

        return " ".join(notes)

    def get_critical_products(
        self,
        products_stock: list[dict],
        default_lead_time: int = 7,
    ) -> list[ReorderSuggestion]:
        """
        Retorna apenas produtos com urgencia CRITICAL ou HIGH.

        Util para alertas automaticos.
        """
        all_suggestions = self.generate_reorder_suggestions(
            products_stock,
            default_lead_time,
        )

        return [s for s in all_suggestions.items if s.urgency in (self.URGENCY_CRITICAL, self.URGENCY_HIGH)]

    def calculate_optimal_order(
        self,
        product_id: UUID,
        current_stock: float,
        lead_time_days: int = 7,
        ordering_cost: float = 50.0,
        holding_cost_pct: float = 0.25,
        unit_cost: float = 10.0,
    ) -> dict:
        """
        Calcula quantidade otima de pedido (EOQ).

        Args:
            product_id: ID do produto
            current_stock: Estoque atual
            lead_time_days: Tempo de reposicao
            ordering_cost: Custo por pedido
            holding_cost_pct: % do custo unitario para armazenagem
            unit_cost: Custo unitario do produto

        Returns:
            Dict com EOQ, custo total estimado e frequencia de pedidos
        """
        forecast = self.repository.get_latest_forecast(product_id, ForecastType.DEMAND)

        if not forecast:
            return {"error": "Sem previsao disponivel"}

        # Demanda anual estimada
        annual_demand = forecast.avg_daily_demand * 365

        # Custo de armazenagem por unidade por ano
        holding_cost = unit_cost * holding_cost_pct

        if holding_cost == 0 or annual_demand == 0:
            return {"error": "Dados insuficientes para calculo"}

        # EOQ = sqrt(2 * D * S / H)
        # D = demanda anual
        # S = custo por pedido
        # H = custo de armazenagem por unidade por ano
        eoq = math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)

        # Numero de pedidos por ano
        orders_per_year = annual_demand / eoq if eoq > 0 else 0

        # Dias entre pedidos
        days_between_orders = 365 / orders_per_year if orders_per_year > 0 else 0

        # Custo total anual
        ordering_total = orders_per_year * ordering_cost
        holding_total = (eoq / 2) * holding_cost
        total_cost = ordering_total + holding_total

        return {
            "eoq": round(eoq, 2),
            "orders_per_year": round(orders_per_year, 1),
            "days_between_orders": round(days_between_orders, 0),
            "annual_ordering_cost": round(ordering_total, 2),
            "annual_holding_cost": round(holding_total, 2),
            "total_annual_cost": round(total_cost, 2),
            "avg_daily_demand": forecast.avg_daily_demand,
            "annual_demand": round(annual_demand, 2),
        }

    def simulate_stock_levels(
        self,
        product_id: UUID,
        current_stock: float,
        reorder_point: float,
        reorder_quantity: float,
        lead_time_days: int,
        simulation_days: int = 90,
    ) -> list[dict]:
        """
        Simula niveis de estoque futuros.

        Returns:
            Lista de {date, stock_level, reorder_triggered, delivery_received}
        """
        forecast = self.repository.get_latest_forecast(product_id, ForecastType.DEMAND)

        if not forecast:
            return []

        # Buscar previsoes diarias
        results = self.repository.get_forecast_results(
            forecast.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=simulation_days),
        )

        if not results:
            # Usar demanda media se nao houver previsao detalhada
            avg_demand = forecast.avg_daily_demand
            results = [
                {"date": date.today() + timedelta(days=i), "predicted_demand": avg_demand}
                for i in range(simulation_days)
            ]

        simulation = []
        stock = current_stock
        pending_orders = []  # Lista de {arrival_date, quantity}

        for i, result in enumerate(results):
            sim_date = result.date if hasattr(result, "date") else result["date"]
            demand = result.predicted_demand if hasattr(result, "predicted_demand") else result["predicted_demand"]

            # Verificar entregas
            delivery_received = 0
            for order in pending_orders[:]:
                if order["arrival_date"] <= sim_date:
                    delivery_received += order["quantity"]
                    pending_orders.remove(order)

            stock += delivery_received

            # Consumir demanda
            stock = max(0, stock - demand)

            # Verificar necessidade de pedido
            reorder_triggered = False
            if stock <= reorder_point and not any(o["arrival_date"] > sim_date for o in pending_orders):
                reorder_triggered = True
                pending_orders.append(
                    {
                        "arrival_date": sim_date + timedelta(days=lead_time_days),
                        "quantity": reorder_quantity,
                    }
                )

            simulation.append(
                {
                    "date": sim_date.isoformat() if hasattr(sim_date, "isoformat") else str(sim_date),
                    "day": i + 1,
                    "stock_level": round(stock, 2),
                    "demand": round(demand, 2),
                    "reorder_triggered": reorder_triggered,
                    "delivery_received": round(delivery_received, 2),
                    "pending_orders": len(pending_orders),
                }
            )

        return simulation
