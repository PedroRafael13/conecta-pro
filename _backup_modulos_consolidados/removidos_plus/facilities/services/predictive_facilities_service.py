#!/usr/bin/env python3
"""
CONECTA PRO - Facilities IoT + Manutenção Preditiva Service
=========================================================
FASE 3 ONDA 2: Excelência Operacional
Target ROI: R$ 100K

Recursos implementados:
- Monitoramento IoT de equipamentos
- Manutenção preditiva com ML
- Gestão de ativos automatizada
- Alertas inteligentes de falhas
- Otimização de recursos
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EquipmentType(Enum):
    ELEVADOR = "elevator"
    BOMBA_AGUA = "water_pump"
    PORTAO = "gate"
    ILUMINACAO = "lighting"
    CAMERA = "camera"
    CLIMATIZACAO = "hvac"
    GERADOR = "generator"
    INTERFONE = "intercom"


class MaintenanceType(Enum):
    PREVENTIVA = "preventive"
    CORRETIVA = "corrective"
    PREDITIVA = "predictive"
    EMERGENCIAL = "emergency"


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EquipmentStatus(Enum):
    OPERACIONAL = "operational"
    MANUTENCAO = "maintenance"
    FALHA = "failure"
    DESLIGADO = "offline"


@dataclass
class IoTSensor:
    """Sensor IoT conectado ao equipamento."""
    id: str
    equipment_id: str
    type: str  # temperature, vibration, current, pressure, etc.
    location: str
    last_reading: float
    unit: str
    threshold_min: float
    threshold_max: float
    last_update: datetime
    is_active: bool = True


@dataclass
class Equipment:
    """Equipamento monitorado pelo sistema IoT."""
    id: str
    name: str
    type: EquipmentType
    location: str
    installation_date: datetime
    last_maintenance: datetime
    maintenance_interval_days: int
    status: EquipmentStatus
    sensors: List[IoTSensor]
    health_score: float  # 0-100
    failure_probability: float  # 0-1
    maintenance_cost: float
    replacement_cost: float


@dataclass
class MaintenanceTask:
    """Tarefa de manutenção."""
    id: str
    equipment_id: str
    type: MaintenanceType
    title: str
    description: str
    scheduled_date: datetime
    estimated_duration_hours: float
    priority: int  # 1-10
    cost_estimate: float
    technician_required: str
    parts_needed: List[str]
    is_completed: bool = False
    completion_date: Optional[datetime] = None


@dataclass
class MaintenanceAlert:
    """Alerta de manutenção."""
    id: str
    equipment_id: str
    severity: AlertSeverity
    message: str
    alert_type: str
    created_at: datetime
    sensor_readings: Dict[str, float]
    recommended_action: str
    estimated_cost_impact: float
    is_acknowledged: bool = False


@dataclass
class PredictiveAnalysis:
    """Análise preditiva de equipamento."""
    equipment_id: str
    failure_probability: float
    predicted_failure_date: Optional[datetime]
    confidence_level: float
    contributing_factors: List[str]
    recommended_actions: List[str]
    cost_savings_potential: float
    generated_at: datetime


@dataclass
class FacilitiesAnalytics:
    """Analytics completo do sistema de facilities."""
    total_equipment: int
    equipment_health_avg: float
    maintenance_tasks_pending: int
    alerts_active: int
    cost_savings_month: float
    uptime_percentage: float
    predictive_accuracy: float
    response_time_avg_minutes: float


class PredictiveFacilitiesService:
    """Serviço de Facilities com IoT e Manutenção Preditiva."""
    
    def __init__(self):
        self.equipment: Dict[str, Equipment] = {}
        self.maintenance_tasks: Dict[str, MaintenanceTask] = {}
        self.alerts: Dict[str, MaintenanceAlert] = {}
        self.predictive_analyses: Dict[str, PredictiveAnalysis] = {}
        
        # Inicializar com dados de demonstração
        self._initialize_demo_data()
    
    def _initialize_demo_data(self):
        """Inicializar com equipamentos e sensores de demonstração."""
        
        # Equipamentos de exemplo
        demo_equipment = [
            {
                "id": "ELEV_001",
                "name": "Elevador Social",
                "type": EquipmentType.ELEVADOR,
                "location": "Torre A",
                "maintenance_interval_days": 90,
                "maintenance_cost": 1200.0,
                "replacement_cost": 80000.0
            },
            {
                "id": "PUMP_001", 
                "name": "Bomba Recalque Principal",
                "type": EquipmentType.BOMBA_AGUA,
                "location": "Casa de Máquinas",
                "maintenance_interval_days": 60,
                "maintenance_cost": 800.0,
                "replacement_cost": 15000.0
            },
            {
                "id": "GATE_001",
                "name": "Portão Principal",
                "type": EquipmentType.PORTAO,
                "location": "Entrada Principal",
                "maintenance_interval_days": 180,
                "maintenance_cost": 400.0,
                "replacement_cost": 8000.0
            }
        ]
        
        for eq_data in demo_equipment:
            # Criar sensores para cada equipamento
            sensors = self._create_sensors_for_equipment(eq_data["id"], eq_data["type"])
            
            equipment = Equipment(
                id=eq_data["id"],
                name=eq_data["name"],
                type=eq_data["type"],
                location=eq_data["location"],
                installation_date=datetime.now() - timedelta(days=random.randint(365, 1825)),
                last_maintenance=datetime.now() - timedelta(days=random.randint(10, 90)),
                maintenance_interval_days=eq_data["maintenance_interval_days"],
                status=EquipmentStatus.OPERACIONAL,
                sensors=sensors,
                health_score=random.uniform(70, 95),
                failure_probability=random.uniform(0.05, 0.25),
                maintenance_cost=eq_data["maintenance_cost"],
                replacement_cost=eq_data["replacement_cost"]
            )
            
            self.equipment[equipment.id] = equipment
    
    def _create_sensors_for_equipment(self, equipment_id: str, eq_type: EquipmentType) -> List[IoTSensor]:
        """Criar sensores específicos por tipo de equipamento."""
        sensors = []
        base_time = datetime.now()
        
        if eq_type == EquipmentType.ELEVADOR:
            sensors = [
                IoTSensor(
                    id=f"{equipment_id}_VIBRATION",
                    equipment_id=equipment_id,
                    type="vibration",
                    location="Motor",
                    last_reading=random.uniform(0.1, 2.5),
                    unit="mm/s",
                    threshold_min=0.0,
                    threshold_max=3.0,
                    last_update=base_time
                ),
                IoTSensor(
                    id=f"{equipment_id}_CURRENT",
                    equipment_id=equipment_id,
                    type="current",
                    location="Painel Elétrico",
                    last_reading=random.uniform(8, 15),
                    unit="A",
                    threshold_min=5.0,
                    threshold_max=20.0,
                    last_update=base_time
                ),
                IoTSensor(
                    id=f"{equipment_id}_TEMP",
                    equipment_id=equipment_id,
                    type="temperature",
                    location="Casa de Máquinas",
                    last_reading=random.uniform(25, 45),
                    unit="°C",
                    threshold_min=10.0,
                    threshold_max=60.0,
                    last_update=base_time
                )
            ]
        
        elif eq_type == EquipmentType.BOMBA_AGUA:
            sensors = [
                IoTSensor(
                    id=f"{equipment_id}_PRESSURE",
                    equipment_id=equipment_id,
                    type="pressure",
                    location="Saída",
                    last_reading=random.uniform(3.0, 4.5),
                    unit="bar",
                    threshold_min=2.5,
                    threshold_max=6.0,
                    last_update=base_time
                ),
                IoTSensor(
                    id=f"{equipment_id}_FLOW",
                    equipment_id=equipment_id,
                    type="flow",
                    location="Tubulação Principal",
                    last_reading=random.uniform(800, 1200),
                    unit="L/min",
                    threshold_min=500.0,
                    threshold_max=1500.0,
                    last_update=base_time
                ),
                IoTSensor(
                    id=f"{equipment_id}_VIBRATION",
                    equipment_id=equipment_id,
                    type="vibration",
                    location="Motor",
                    last_reading=random.uniform(0.5, 3.0),
                    unit="mm/s",
                    threshold_min=0.0,
                    threshold_max=5.0,
                    last_update=base_time
                )
            ]
        
        elif eq_type == EquipmentType.PORTAO:
            sensors = [
                IoTSensor(
                    id=f"{equipment_id}_CURRENT",
                    equipment_id=equipment_id,
                    type="current",
                    location="Motor",
                    last_reading=random.uniform(2.0, 8.0),
                    unit="A",
                    threshold_min=1.0,
                    threshold_max=12.0,
                    last_update=base_time
                ),
                IoTSensor(
                    id=f"{equipment_id}_CYCLES",
                    equipment_id=equipment_id,
                    type="cycles",
                    location="Contador",
                    last_reading=random.uniform(50, 200),
                    unit="cycles/day",
                    threshold_min=0.0,
                    threshold_max=500.0,
                    last_update=base_time
                )
            ]
        
        return sensors
    
    async def get_equipment_status(self, equipment_id: str) -> Optional[Equipment]:
        """Obter status atual de um equipamento."""
        return self.equipment.get(equipment_id)
    
    async def get_all_equipment(self) -> List[Equipment]:
        """Obter todos os equipamentos."""
        return list(self.equipment.values())
    
    async def update_sensor_reading(self, sensor_id: str, value: float) -> bool:
        """Atualizar leitura de um sensor IoT."""
        for equipment in self.equipment.values():
            for sensor in equipment.sensors:
                if sensor.id == sensor_id:
                    sensor.last_reading = value
                    sensor.last_update = datetime.now()
                    
                    # Verificar se leitura está fora dos limites
                    if value < sensor.threshold_min or value > sensor.threshold_max:
                        await self._create_sensor_alert(sensor, equipment)
                    
                    # Atualizar análise preditiva
                    await self._update_predictive_analysis(equipment.id)
                    
                    return True
        return False
    
    async def _create_sensor_alert(self, sensor: IoTSensor, equipment: Equipment):
        """Criar alerta baseado na leitura do sensor."""
        severity = AlertSeverity.LOW
        
        # Determinar severidade baseada no desvio dos limites
        deviation_min = abs(sensor.last_reading - sensor.threshold_min) / sensor.threshold_min if sensor.threshold_min > 0 else 0
        deviation_max = abs(sensor.last_reading - sensor.threshold_max) / sensor.threshold_max if sensor.threshold_max > 0 else 0
        max_deviation = max(deviation_min, deviation_max)
        
        if max_deviation > 0.5:
            severity = AlertSeverity.CRITICAL
        elif max_deviation > 0.3:
            severity = AlertSeverity.HIGH
        elif max_deviation > 0.1:
            severity = AlertSeverity.MEDIUM
        
        alert = MaintenanceAlert(
            id=f"ALERT_{len(self.alerts) + 1:04d}",
            equipment_id=equipment.id,
            severity=severity,
            message=f"Sensor {sensor.type} fora dos limites: {sensor.last_reading:.2f} {sensor.unit}",
            alert_type=f"sensor_{sensor.type}",
            created_at=datetime.now(),
            sensor_readings={sensor.id: sensor.last_reading},
            recommended_action=self._get_recommended_action(sensor, severity),
            estimated_cost_impact=self._calculate_cost_impact(equipment, severity),
            is_acknowledged=False
        )
        
        self.alerts[alert.id] = alert
        logger.warning(f"Alert criado: {alert.message}")
    
    def _get_recommended_action(self, sensor: IoTSensor, severity: AlertSeverity) -> str:
        """Gerar recomendação baseada no sensor e severidade."""
        actions = {
            ("vibration", AlertSeverity.CRITICAL): "Parar equipamento imediatamente - risco de dano severo",
            ("vibration", AlertSeverity.HIGH): "Agendar inspeção técnica em 24h",
            ("temperature", AlertSeverity.CRITICAL): "Verificar sistema de ventilação urgente",
            ("pressure", AlertSeverity.HIGH): "Verificar vazamentos e ajustar pressão",
            ("current", AlertSeverity.CRITICAL): "Inspeção elétrica imediata necessária"
        }
        
        return actions.get((sensor.type, severity), "Monitorar de perto e agendar manutenção preventiva")
    
    def _calculate_cost_impact(self, equipment: Equipment, severity: AlertSeverity) -> float:
        """Calcular impacto financeiro potencial do problema."""
        base_cost = equipment.maintenance_cost
        
        multipliers = {
            AlertSeverity.LOW: 0.1,
            AlertSeverity.MEDIUM: 0.3,
            AlertSeverity.HIGH: 0.7,
            AlertSeverity.CRITICAL: 2.0
        }
        
        return base_cost * multipliers.get(severity, 0.5)
    
    async def _update_predictive_analysis(self, equipment_id: str):
        """Atualizar análise preditiva do equipamento."""
        equipment = self.equipment.get(equipment_id)
        if not equipment:
            return
        
        # Simular análise ML baseada nas leituras dos sensores
        sensor_scores = []
        contributing_factors = []
        
        for sensor in equipment.sensors:
            # Calcular score baseado na proximidade dos limites
            range_size = sensor.threshold_max - sensor.threshold_min
            if range_size > 0:
                deviation = abs(sensor.last_reading - (sensor.threshold_min + range_size/2))
                score = 1.0 - (deviation / (range_size/2))
                sensor_scores.append(max(0, score))
                
                if score < 0.7:
                    contributing_factors.append(f"Sensor {sensor.type} degradado")
        
        # Calcular probabilidade de falha
        avg_sensor_health = sum(sensor_scores) / len(sensor_scores) if sensor_scores else 0.8
        
        # Considerar idade do equipamento
        age_days = (datetime.now() - equipment.installation_date).days
        age_factor = min(1.0, age_days / 3650)  # 10 anos = fator 1.0
        
        # Considerar tempo desde última manutenção
        days_since_maintenance = (datetime.now() - equipment.last_maintenance).days
        maintenance_factor = min(1.0, days_since_maintenance / equipment.maintenance_interval_days)
        
        failure_probability = (1 - avg_sensor_health) * 0.4 + age_factor * 0.3 + maintenance_factor * 0.3
        
        # Atualizar health score
        equipment.health_score = (1 - failure_probability) * 100
        equipment.failure_probability = failure_probability
        
        # Prever data de falha se probabilidade for alta
        predicted_failure_date = None
        if failure_probability > 0.7:
            days_to_failure = int((1 - failure_probability) * 365)
            predicted_failure_date = datetime.now() + timedelta(days=days_to_failure)
        
        # Calcular potencial de economia
        cost_savings = 0.0
        if failure_probability > 0.5:
            # Economia = custo de manutenção corretiva - custo preventiva
            corrective_cost = equipment.maintenance_cost * 3  # Manutenção corretiva é mais cara
            preventive_cost = equipment.maintenance_cost
            cost_savings = corrective_cost - preventive_cost
        
        analysis = PredictiveAnalysis(
            equipment_id=equipment_id,
            failure_probability=failure_probability,
            predicted_failure_date=predicted_failure_date,
            confidence_level=min(0.95, avg_sensor_health + 0.1),
            contributing_factors=contributing_factors,
            recommended_actions=self._get_predictive_recommendations(failure_probability),
            cost_savings_potential=cost_savings,
            generated_at=datetime.now()
        )
        
        self.predictive_analyses[equipment_id] = analysis
    
    def _get_predictive_recommendations(self, failure_probability: float) -> List[str]:
        """Gerar recomendações baseadas na probabilidade de falha."""
        recommendations = []
        
        if failure_probability > 0.8:
            recommendations.extend([
                "Agendar manutenção corretiva imediata",
                "Preparar peças de reposição",
                "Considerar substituição do equipamento"
            ])
        elif failure_probability > 0.6:
            recommendations.extend([
                "Agendar manutenção preventiva urgente",
                "Aumentar frequência de monitoramento",
                "Verificar fornecedores de peças"
            ])
        elif failure_probability > 0.4:
            recommendations.extend([
                "Incluir na próxima manutenção preventiva",
                "Monitorar tendências dos sensores"
            ])
        else:
            recommendations.append("Manter programa de manutenção atual")
        
        return recommendations
    
    async def schedule_maintenance(self, equipment_id: str, maintenance_type: MaintenanceType, 
                                 scheduled_date: datetime, description: str) -> MaintenanceTask:
        """Agendar tarefa de manutenção."""
        equipment = self.equipment.get(equipment_id)
        if not equipment:
            raise ValueError(f"Equipamento {equipment_id} não encontrado")
        
        # Calcular prioridade baseada no health score
        priority = 10 - int(equipment.health_score / 10)
        
        # Estimar duração baseada no tipo de manutenção
        duration_hours = {
            MaintenanceType.PREVENTIVA: equipment.maintenance_cost / 100,  # R/hora
            MaintenanceType.CORRETIVA: equipment.maintenance_cost / 80,    # R/hora (mais demorado)
            MaintenanceType.PREDITIVA: equipment.maintenance_cost / 120,   # R/hora (mais eficiente)
            MaintenanceType.EMERGENCIAL: equipment.maintenance_cost / 150  # R/hora (mais rápido)
        }.get(maintenance_type, 4.0)
        
        task = MaintenanceTask(
            id=f"MAINT_{len(self.maintenance_tasks) + 1:04d}",
            equipment_id=equipment_id,
            type=maintenance_type,
            title=f"Manutenção {maintenance_type.value} - {equipment.name}",
            description=description,
            scheduled_date=scheduled_date,
            estimated_duration_hours=duration_hours,
            priority=priority,
            cost_estimate=equipment.maintenance_cost,
            technician_required=self._get_required_technician(equipment.type),
            parts_needed=self._get_required_parts(equipment.type, maintenance_type),
            is_completed=False
        )
        
        self.maintenance_tasks[task.id] = task
        return task
    
    def _get_required_technician(self, equipment_type: EquipmentType) -> str:
        """Determinar tipo de técnico necessário."""
        technician_map = {
            EquipmentType.ELEVADOR: "Técnico em Elevadores",
            EquipmentType.BOMBA_AGUA: "Técnico Hidráulico",
            EquipmentType.PORTAO: "Técnico Eletroeletrônico",
            EquipmentType.ILUMINACAO: "Eletricista",
            EquipmentType.CAMERA: "Técnico CFTV",
            EquipmentType.CLIMATIZACAO: "Técnico Refrigeração",
            EquipmentType.GERADOR: "Técnico Eletromecânico"
        }
        return technician_map.get(equipment_type, "Técnico Geral")
    
    def _get_required_parts(self, equipment_type: EquipmentType, maintenance_type: MaintenanceType) -> List[str]:
        """Determinar peças necessárias."""
        parts_map = {
            EquipmentType.ELEVADOR: ["Cabos de aço", "Pastilhas de freio", "Óleo hidráulico"],
            EquipmentType.BOMBA_AGUA: ["Selo mecânico", "Rolamentos", "Impelidor"],
            EquipmentType.PORTAO: ["Correia dentada", "Sensor infravermelho", "Relé"]
        }
        
        base_parts = parts_map.get(equipment_type, ["Peças diversas"])
        
        if maintenance_type == MaintenanceType.CORRETIVA:
            base_parts.extend(["Peça de emergência", "Componente sobressalente"])
        
        return base_parts
    
    async def get_active_alerts(self, severity_filter: Optional[AlertSeverity] = None) -> List[MaintenanceAlert]:
        """Obter alertas ativos, opcionalmente filtrados por severidade."""
        alerts = [alert for alert in self.alerts.values() if not alert.is_acknowledged]
        
        if severity_filter:
            alerts = [alert for alert in alerts if alert.severity == severity_filter]
        
        return sorted(alerts, key=lambda x: x.created_at, reverse=True)
    
    async def get_pending_maintenance(self) -> List[MaintenanceTask]:
        """Obter tarefas de manutenção pendentes."""
        pending = [task for task in self.maintenance_tasks.values() if not task.is_completed]
        return sorted(pending, key=lambda x: (x.priority, x.scheduled_date), reverse=True)
    
    async def get_predictive_analysis(self, equipment_id: str) -> Optional[PredictiveAnalysis]:
        """Obter análise preditiva de um equipamento."""
        return self.predictive_analyses.get(equipment_id)
    
    async def get_all_predictive_analyses(self) -> List[PredictiveAnalysis]:
        """Obter todas as análises preditivas."""
        return list(self.predictive_analyses.values())
    
    async def complete_maintenance_task(self, task_id: str, completion_notes: str = "") -> bool:
        """Marcar tarefa de manutenção como concluída."""
        task = self.maintenance_tasks.get(task_id)
        if not task:
            return False
        
        task.is_completed = True
        task.completion_date = datetime.now()
        
        # Atualizar último período de manutenção do equipamento
        equipment = self.equipment.get(task.equipment_id)
        if equipment:
            equipment.last_maintenance = datetime.now()
            equipment.health_score = min(95, equipment.health_score + 10)  # Melhora health score
            equipment.failure_probability = max(0.05, equipment.failure_probability * 0.7)
        
        logger.info(f"Manutenção concluída: {task.title}")
        return True
    
    async def simulate_iot_readings(self):
        """Simular leituras IoT para demonstração."""
        for equipment in self.equipment.values():
            for sensor in equipment.sensors:
                # Simular variação natural das leituras
                current_value = sensor.last_reading
                range_size = sensor.threshold_max - sensor.threshold_min
                variation = random.uniform(-0.1, 0.1) * range_size
                new_value = max(sensor.threshold_min - range_size * 0.1, 
                              min(sensor.threshold_max + range_size * 0.1, 
                                  current_value + variation))
                
                await self.update_sensor_reading(sensor.id, new_value)
    
    async def get_facilities_analytics(self) -> FacilitiesAnalytics:
        """Obter analytics completo do sistema de facilities."""
        total_equipment = len(self.equipment)
        equipment_health_avg = sum(eq.health_score for eq in self.equipment.values()) / total_equipment if total_equipment > 0 else 0
        
        pending_maintenance = len([task for task in self.maintenance_tasks.values() if not task.is_completed])
        active_alerts = len([alert for alert in self.alerts.values() if not alert.is_acknowledged])
        
        # Calcular economia mensal baseada em manutenção preditiva
        cost_savings_month = sum(analysis.cost_savings_potential for analysis in self.predictive_analyses.values()) / 12
        
        # Calcular uptime (baseado em health scores)
        uptime_percentage = equipment_health_avg
        
        # Simular precisão preditiva
        predictive_accuracy = 89.5
        
        # Simular tempo de resposta médio
        response_time_avg_minutes = 12.3
        
        return FacilitiesAnalytics(
            total_equipment=total_equipment,
            equipment_health_avg=equipment_health_avg,
            maintenance_tasks_pending=pending_maintenance,
            alerts_active=active_alerts,
            cost_savings_month=cost_savings_month,
            uptime_percentage=uptime_percentage,
            predictive_accuracy=predictive_accuracy,
            response_time_avg_minutes=response_time_avg_minutes
        )
    
    async def generate_maintenance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Gerar relatório de manutenção para período."""
        # Filtrar tarefas no período
        period_tasks = [
            task for task in self.maintenance_tasks.values()
            if start_date <= task.scheduled_date <= end_date
        ]
        
        completed_tasks = [task for task in period_tasks if task.is_completed]
        total_cost = sum(task.cost_estimate for task in completed_tasks)
        
        # Calcular métricas por tipo de manutenção
        type_stats = {}
        for task in period_tasks:
            task_type = task.type.value
            if task_type not in type_stats:
                type_stats[task_type] = {"count": 0, "cost": 0, "completed": 0}
            
            type_stats[task_type]["count"] += 1
            type_stats[task_type]["cost"] += task.cost_estimate
            if task.is_completed:
                type_stats[task_type]["completed"] += 1
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_tasks": len(period_tasks),
                "completed_tasks": len(completed_tasks),
                "completion_rate": len(completed_tasks) / len(period_tasks) * 100 if period_tasks else 0,
                "total_cost": total_cost,
                "avg_cost_per_task": total_cost / len(completed_tasks) if completed_tasks else 0
            },
            "by_type": type_stats,
            "equipment_performance": [
                {
                    "equipment_id": eq.id,
                    "equipment_name": eq.name,
                    "health_score": eq.health_score,
                    "maintenance_count": len([t for t in period_tasks if t.equipment_id == eq.id])
                }
                for eq in self.equipment.values()
            ]
        }


# Instância singleton do serviço
predictive_facilities_service = PredictiveFacilitiesService()


if __name__ == "__main__":
    # Teste básico
    async def test_facilities():
        service = PredictiveFacilitiesService()
        
        # Simular algumas leituras IoT
        await service.simulate_iot_readings()
        
        # Obter analytics
        analytics = await service.get_facilities_analytics()
        print(f"Equipment Health Average: {analytics.equipment_health_avg:.1f}%")
        print(f"Cost Savings per Month: R$ {analytics.cost_savings_month:.2f}")
        
    asyncio.run(test_facilities())
