"""Service de IA para manutenção preditiva de equipamentos."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.equipment_management.models.equipment import Equipment, EquipmentStatus
from modules.equipment_management.models.maintenance import (
    EquipmentMaintenance,
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
)

logger = logging.getLogger(__name__)


class MaintenanceAIService:
    """Service de IA para análise e previsão de manutenções."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session

    async def analyze_equipment_health(
        self, equipment_id: str | UUID
    ) -> Optional[dict]:
        """Analisa saúde do equipamento e gera score."""
        if isinstance(equipment_id, str):
            equipment_id = UUID(equipment_id)

        # Buscar equipamento
        result = await self.session.execute(
            select(Equipment).where(
                and_(Equipment.id == equipment_id, Equipment.is_active == True)
            )
        )
        equipment = result.scalar_one_or_none()
        if not equipment:
            return None

        # Buscar histórico de manutenções
        maint_result = await self.session.execute(
            select(EquipmentMaintenance)
            .where(
                and_(
                    EquipmentMaintenance.equipment_id == str(equipment_id),
                    EquipmentMaintenance.is_active == True,
                )
            )
            .order_by(EquipmentMaintenance.created_at.desc())
        )
        maintenances = list(maint_result.scalars().all())

        # Calcular score de saúde (0-100)
        health_score = 100.0
        risk_factors = []
        recommendations = []

        now = datetime.utcnow()

        # Fator 1: Idade do equipamento
        if equipment.purchase_date:
            age_months = (now - equipment.purchase_date).days / 30
            age_factor = min(age_months / 60, 1.0) * 15  # Max 15 pontos
            health_score -= age_factor
            if age_months > 36:
                risk_factors.append({
                    "factor": "equipment_age",
                    "severity": "medium",
                    "description": f"Equipamento com {int(age_months)} meses de uso",
                })

        # Fator 2: Status online
        if not equipment.is_online and equipment.status == EquipmentStatus.INSTALADO:
            health_score -= 20
            risk_factors.append({
                "factor": "offline_status",
                "severity": "high",
                "description": "Equipamento está offline",
            })
            recommendations.append({
                "action": "check_connectivity",
                "priority": "high",
                "description": "Verificar conexão e alimentação do equipamento",
            })

        # Fator 3: Uptime
        if equipment.uptime_percent is not None and equipment.uptime_percent < 95:
            uptime_penalty = (95 - equipment.uptime_percent) / 2
            health_score -= uptime_penalty
            if equipment.uptime_percent < 90:
                risk_factors.append({
                    "factor": "low_uptime",
                    "severity": "medium",
                    "description": f"Uptime baixo: {equipment.uptime_percent:.1f}%",
                })

        # Fator 4: Garantia
        if equipment.warranty_end:
            if equipment.warranty_end < now:
                health_score -= 5
                risk_factors.append({
                    "factor": "warranty_expired",
                    "severity": "low",
                    "description": "Garantia expirada",
                })
            elif equipment.warranty_end < now + timedelta(days=30):
                recommendations.append({
                    "action": "check_warranty",
                    "priority": "medium",
                    "description": "Garantia expira em breve - considerar extensão",
                })

        # Fator 5: Manutenção atrasada
        if equipment.next_maintenance_at and equipment.next_maintenance_at < now:
            days_overdue = (now - equipment.next_maintenance_at).days
            overdue_penalty = min(days_overdue / 10, 20)  # Max 20 pontos
            health_score -= overdue_penalty
            risk_factors.append({
                "factor": "maintenance_overdue",
                "severity": "high",
                "description": f"Manutenção atrasada em {days_overdue} dias",
            })
            recommendations.append({
                "action": "schedule_maintenance",
                "priority": "urgent",
                "description": "Agendar manutenção preventiva imediatamente",
            })

        # Fator 6: Histórico de manutenções
        if maintenances:
            # Contagem de manutenções corretivas vs preventivas
            corrective_count = sum(
                1 for m in maintenances
                if m.maintenance_type == MaintenanceType.CORRETIVA
            )
            total_count = len(maintenances)

            if total_count > 0:
                corrective_ratio = corrective_count / total_count
                if corrective_ratio > 0.5:
                    health_score -= corrective_ratio * 10
                    risk_factors.append({
                        "factor": "high_corrective_ratio",
                        "severity": "medium",
                        "description": f"Alto índice de manutenções corretivas: {corrective_ratio:.0%}",
                    })
                    recommendations.append({
                        "action": "increase_preventive",
                        "priority": "medium",
                        "description": "Aumentar frequência de manutenções preventivas",
                    })

            # Verificar problemas não resolvidos
            unresolved = sum(
                1 for m in maintenances
                if m.status == MaintenanceStatus.COMPLETED and not m.problem_resolved
            )
            if unresolved > 0:
                health_score -= unresolved * 5
                risk_factors.append({
                    "factor": "unresolved_issues",
                    "severity": "high",
                    "description": f"{unresolved} manutenções com problemas não resolvidos",
                })

            # Tempo médio entre falhas (MTBF)
            if corrective_count >= 2:
                first_corrective = None
                last_corrective = None
                for m in maintenances:
                    if m.maintenance_type == MaintenanceType.CORRETIVA:
                        if not last_corrective:
                            last_corrective = m.created_at
                        first_corrective = m.created_at

                if first_corrective and last_corrective and first_corrective != last_corrective:
                    days_span = (last_corrective - first_corrective).days
                    mtbf = days_span / (corrective_count - 1)
                    if mtbf < 30:
                        health_score -= 15
                        risk_factors.append({
                            "factor": "low_mtbf",
                            "severity": "high",
                            "description": f"MTBF baixo: {mtbf:.0f} dias entre falhas",
                        })
                        recommendations.append({
                            "action": "consider_replacement",
                            "priority": "high",
                            "description": "Considerar substituição do equipamento",
                        })

        # Garantir score entre 0 e 100
        health_score = max(0, min(100, health_score))

        # Determinar status baseado no score
        if health_score >= 80:
            health_status = "excellent"
        elif health_score >= 60:
            health_status = "good"
        elif health_score >= 40:
            health_status = "fair"
        elif health_score >= 20:
            health_status = "poor"
        else:
            health_status = "critical"

        return {
            "equipment_id": str(equipment.id),
            "equipment_code": equipment.equipment_code,
            "health_score": round(health_score, 1),
            "health_status": health_status,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "analysis_date": now.isoformat(),
            "maintenance_history_count": len(maintenances),
            "next_maintenance_due": equipment.next_maintenance_at.isoformat()
            if equipment.next_maintenance_at
            else None,
        }

    async def predict_failure(
        self, equipment_id: str | UUID
    ) -> Optional[dict]:
        """Prevê probabilidade de falha do equipamento."""
        if isinstance(equipment_id, str):
            equipment_id = UUID(equipment_id)

        health = await self.analyze_equipment_health(equipment_id)
        if not health:
            return None

        # Calcular probabilidade de falha baseado no score de saúde
        # Score baixo = alta probabilidade de falha
        health_score = health["health_score"]
        failure_probability = max(0, 100 - health_score) / 100

        # Ajustar baseado em fatores de risco
        for rf in health["risk_factors"]:
            if rf["severity"] == "high":
                failure_probability = min(1.0, failure_probability + 0.1)
            elif rf["severity"] == "medium":
                failure_probability = min(1.0, failure_probability + 0.05)

        # Estimar tempo até falha
        if failure_probability >= 0.8:
            estimated_days = 7
            urgency = "critical"
        elif failure_probability >= 0.6:
            estimated_days = 30
            urgency = "high"
        elif failure_probability >= 0.4:
            estimated_days = 90
            urgency = "medium"
        elif failure_probability >= 0.2:
            estimated_days = 180
            urgency = "low"
        else:
            estimated_days = 365
            urgency = "minimal"

        return {
            "equipment_id": str(equipment_id),
            "equipment_code": health["equipment_code"],
            "failure_probability": round(failure_probability, 2),
            "urgency": urgency,
            "estimated_days_to_failure": estimated_days,
            "confidence_level": 0.75,  # Nível de confiança do modelo
            "contributing_factors": health["risk_factors"],
            "preventive_actions": health["recommendations"],
            "prediction_date": datetime.utcnow().isoformat(),
        }

    async def recommend_maintenance_schedule(
        self, client_id: Optional[str] = None
    ) -> list[dict]:
        """Recomenda agenda de manutenções preventivas."""
        # Buscar equipamentos que precisam de atenção
        conditions = [
            Equipment.is_active == True,
            Equipment.status == EquipmentStatus.INSTALADO,
        ]

        if client_id:
            conditions.append(Equipment.client_id == client_id)

        result = await self.session.execute(
            select(Equipment).where(and_(*conditions))
        )
        equipments = list(result.scalars().all())

        recommendations = []
        now = datetime.utcnow()

        for equipment in equipments:
            # Analisar saúde
            health = await self.analyze_equipment_health(equipment.id)
            if not health:
                continue

            priority = MaintenancePriority.LOW
            recommended_date = now + timedelta(days=90)
            reason = "Manutenção preventiva de rotina"

            # Ajustar prioridade baseado na análise
            if health["health_status"] == "critical":
                priority = MaintenancePriority.CRITICAL
                recommended_date = now + timedelta(days=1)
                reason = "Equipamento em estado crítico"
            elif health["health_status"] == "poor":
                priority = MaintenancePriority.URGENT
                recommended_date = now + timedelta(days=7)
                reason = "Equipamento com problemas detectados"
            elif health["health_status"] == "fair":
                priority = MaintenancePriority.HIGH
                recommended_date = now + timedelta(days=14)
                reason = "Equipamento requer atenção"
            elif health["health_status"] == "good":
                priority = MaintenancePriority.MEDIUM
                recommended_date = now + timedelta(days=30)
                reason = "Manutenção preventiva recomendada"

            # Verificar se há manutenção programada
            if equipment.next_maintenance_at:
                if equipment.next_maintenance_at < now:
                    priority = MaintenancePriority.URGENT
                    recommended_date = now + timedelta(days=1)
                    reason = "Manutenção atrasada"
                elif equipment.next_maintenance_at < recommended_date:
                    recommended_date = equipment.next_maintenance_at

            recommendations.append({
                "equipment_id": str(equipment.id),
                "equipment_code": equipment.equipment_code,
                "equipment_name": equipment.name,
                "client_id": equipment.client_id,
                "client_name": equipment.client_name,
                "health_score": health["health_score"],
                "health_status": health["health_status"],
                "priority": priority.value,
                "recommended_date": recommended_date.isoformat(),
                "reason": reason,
                "estimated_duration_hours": 2.0,
                "actions": [r["description"] for r in health["recommendations"]],
            })

        # Ordenar por prioridade e data
        priority_order = {
            "critical": 0,
            "urgent": 1,
            "high": 2,
            "medium": 3,
            "low": 4,
        }
        recommendations.sort(
            key=lambda x: (priority_order.get(x["priority"], 5), x["recommended_date"])
        )

        return recommendations

    async def optimize_technician_route(
        self, technician_id: str, date: datetime
    ) -> list[dict]:
        """Otimiza rota de manutenções para técnico."""
        # Buscar manutenções agendadas para o técnico na data
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        result = await self.session.execute(
            select(EquipmentMaintenance).where(
                and_(
                    EquipmentMaintenance.technician_id == technician_id,
                    EquipmentMaintenance.scheduled_date >= start,
                    EquipmentMaintenance.scheduled_date < end,
                    EquipmentMaintenance.status.in_([
                        MaintenanceStatus.SCHEDULED,
                        MaintenanceStatus.PENDING,
                    ]),
                    EquipmentMaintenance.is_active == True,
                )
            )
        )
        maintenances = list(result.scalars().all())

        if not maintenances:
            return []

        # Buscar equipamentos para obter localizações
        equipment_locations = {}
        for m in maintenances:
            eq_result = await self.session.execute(
                select(Equipment).where(Equipment.id == UUID(m.equipment_id))
            )
            equipment = eq_result.scalar_one_or_none()
            if equipment:
                equipment_locations[m.equipment_id] = {
                    "lat": equipment.gps_latitude,
                    "lon": equipment.gps_longitude,
                    "address": equipment.installed_location,
                }

        # Ordenar por prioridade e agrupar por proximidade
        # (Algoritmo simplificado - produção usaria algo mais sofisticado)
        priority_order = {
            MaintenancePriority.CRITICAL: 0,
            MaintenancePriority.URGENT: 1,
            MaintenancePriority.HIGH: 2,
            MaintenancePriority.MEDIUM: 3,
            MaintenancePriority.LOW: 4,
        }

        sorted_maintenances = sorted(
            maintenances,
            key=lambda x: (priority_order.get(x.priority, 5), x.scheduled_date or now),
        )

        route = []
        current_time = start.replace(hour=8, minute=0)  # Início às 8h

        for i, m in enumerate(sorted_maintenances):
            location = equipment_locations.get(m.equipment_id, {})
            duration = m.estimated_duration_hours or 2.0

            route.append({
                "order": i + 1,
                "maintenance_id": str(m.id),
                "maintenance_code": m.maintenance_code,
                "equipment_code": m.equipment_code,
                "equipment_name": m.equipment_name,
                "priority": m.priority.value,
                "scheduled_time": current_time.strftime("%H:%M"),
                "estimated_duration_hours": duration,
                "address": location.get("address"),
                "latitude": location.get("lat"),
                "longitude": location.get("lon"),
            })

            # Adicionar tempo de deslocamento (30 min) + duração
            current_time += timedelta(hours=duration + 0.5)

        return route

    async def analyze_maintenance_patterns(
        self, client_id: Optional[str] = None, months: int = 12
    ) -> dict:
        """Analisa padrões de manutenção para insights."""
        from datetime import timedelta

        now = datetime.utcnow()
        start_date = now - timedelta(days=months * 30)

        conditions = [
            EquipmentMaintenance.created_at >= start_date,
            EquipmentMaintenance.is_active == True,
        ]

        if client_id:
            conditions.append(EquipmentMaintenance.client_id == client_id)

        result = await self.session.execute(
            select(EquipmentMaintenance).where(and_(*conditions))
        )
        maintenances = list(result.scalars().all())

        if not maintenances:
            return {
                "period_months": months,
                "total_maintenances": 0,
                "patterns": [],
                "insights": [],
            }

        # Análise por tipo de equipamento
        by_equipment_type = {}
        for m in maintenances:
            eq_type = m.equipment_type or "unknown"
            if eq_type not in by_equipment_type:
                by_equipment_type[eq_type] = {
                    "total": 0,
                    "corrective": 0,
                    "preventive": 0,
                    "avg_cost": 0.0,
                    "costs": [],
                }
            by_equipment_type[eq_type]["total"] += 1
            if m.maintenance_type == MaintenanceType.CORRETIVA:
                by_equipment_type[eq_type]["corrective"] += 1
            elif m.maintenance_type == MaintenanceType.PREVENTIVA:
                by_equipment_type[eq_type]["preventive"] += 1
            if m.total_cost:
                by_equipment_type[eq_type]["costs"].append(m.total_cost)

        # Calcular médias
        for eq_type in by_equipment_type:
            costs = by_equipment_type[eq_type]["costs"]
            if costs:
                by_equipment_type[eq_type]["avg_cost"] = sum(costs) / len(costs)
            del by_equipment_type[eq_type]["costs"]

        # Análise por mês
        by_month = {}
        for m in maintenances:
            month_key = m.created_at.strftime("%Y-%m")
            if month_key not in by_month:
                by_month[month_key] = {"total": 0, "corrective": 0, "preventive": 0}
            by_month[month_key]["total"] += 1
            if m.maintenance_type == MaintenanceType.CORRETIVA:
                by_month[month_key]["corrective"] += 1
            elif m.maintenance_type == MaintenanceType.PREVENTIVA:
                by_month[month_key]["preventive"] += 1

        # Gerar insights
        insights = []
        total_corrective = sum(1 for m in maintenances if m.maintenance_type == MaintenanceType.CORRETIVA)
        total_preventive = sum(1 for m in maintenances if m.maintenance_type == MaintenanceType.PREVENTIVA)

        corrective_ratio = total_corrective / len(maintenances) if maintenances else 0

        if corrective_ratio > 0.6:
            insights.append({
                "type": "warning",
                "title": "Alto índice de manutenções corretivas",
                "description": f"{corrective_ratio:.0%} das manutenções são corretivas. Considere aumentar preventivas.",
            })

        if corrective_ratio < 0.3:
            insights.append({
                "type": "success",
                "title": "Bom equilíbrio preventivo/corretivo",
                "description": f"Apenas {corrective_ratio:.0%} de manutenções corretivas.",
            })

        # Identificar equipamentos problemáticos
        by_equipment = {}
        for m in maintenances:
            eq_id = m.equipment_id
            if eq_id not in by_equipment:
                by_equipment[eq_id] = {
                    "code": m.equipment_code,
                    "name": m.equipment_name,
                    "count": 0,
                }
            by_equipment[eq_id]["count"] += 1

        problematic = [
            eq for eq in by_equipment.values() if eq["count"] > 3
        ]
        if problematic:
            insights.append({
                "type": "warning",
                "title": "Equipamentos com muitas manutenções",
                "description": f"{len(problematic)} equipamentos tiveram mais de 3 manutenções no período.",
                "equipment": problematic[:5],
            })

        return {
            "period_months": months,
            "total_maintenances": len(maintenances),
            "total_corrective": total_corrective,
            "total_preventive": total_preventive,
            "by_equipment_type": by_equipment_type,
            "by_month": by_month,
            "corrective_ratio": corrective_ratio,
            "insights": insights,
            "analysis_date": now.isoformat(),
        }

    async def estimate_maintenance_cost(
        self, equipment_id: str | UUID, maintenance_type: str = "preventiva"
    ) -> Optional[dict]:
        """Estima custo de manutenção baseado em histórico."""
        if isinstance(equipment_id, str):
            equipment_id = UUID(equipment_id)

        # Buscar histórico do equipamento
        result = await self.session.execute(
            select(EquipmentMaintenance).where(
                and_(
                    EquipmentMaintenance.equipment_id == str(equipment_id),
                    EquipmentMaintenance.status == MaintenanceStatus.COMPLETED,
                    EquipmentMaintenance.is_active.is_(True),
                )
            )
        )
        maintenances = list(result.scalars().all())

        if not maintenances:
            # Retornar estimativa padrão
            return {
                "equipment_id": str(equipment_id),
                "maintenance_type": maintenance_type,
                "estimated_cost": 150.0,  # Custo base
                "labor_cost": 100.0,
                "parts_cost": 50.0,
                "confidence": 0.3,
                "basis": "default_estimate",
            }

        # Calcular médias do histórico
        labor_costs = [m.labor_cost or 0 for m in maintenances]
        parts_costs = [m.parts_cost or 0 for m in maintenances]
        total_costs = [m.total_cost or 0 for m in maintenances]

        avg_labor = sum(labor_costs) / len(labor_costs) if labor_costs else 100.0
        avg_parts = sum(parts_costs) / len(parts_costs) if parts_costs else 50.0
        avg_total = sum(total_costs) / len(total_costs) if total_costs else 150.0

        # Ajustar confiança baseado no volume de dados
        confidence = min(0.9, 0.3 + (len(maintenances) * 0.1))

        return {
            "equipment_id": str(equipment_id),
            "maintenance_type": maintenance_type,
            "estimated_cost": round(avg_total, 2),
            "labor_cost": round(avg_labor, 2),
            "parts_cost": round(avg_parts, 2),
            "confidence": confidence,
            "basis": "historical_average",
            "sample_size": len(maintenances),
        }
