#!/usr/bin/env python3
"""
CONECTA PRO - Equipment RFID + Lifecycle Management Service
==========================================================
FASE 3 ONDA 2: Excelência Operacional
Target ROI: R$ 100K

Recursos implementados:
- Rastreamento RFID de equipamentos
- Gestão completa do ciclo de vida
- Inventário automatizado
- Depreciação e valoração
- Alertas de substituição
- Otimização de ativos
"""

import asyncio
import logging
import random  # noqa: S311
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EquipmentCategory(Enum):
    ELETRONICO = "electronic"
    MECANICO = "mechanical"
    ELETRICO = "electrical"
    HIDRAULICO = "hydraulic"
    SEGURANCA = "security"
    COMUNICACAO = "communication"


class LifecycleStage(Enum):
    PLANEJAMENTO = "planning"
    AQUISICAO = "acquisition"
    OPERACAO = "operation"
    MANUTENCAO = "maintenance"
    SUBSTITUICAO = "replacement"
    DESCARTE = "disposal"


class EquipmentStatus(Enum):
    NOVO = "new"
    OPERACIONAL = "operational"
    MANUTENCAO = "maintenance"
    INATIVO = "inactive"
    DESCARTADO = "disposed"
    PERDIDO = "lost"


class AlertType(Enum):
    MANUTENCAO_VENCIDA = "maintenance_due"
    SUBSTITUICAO_RECOMENDADA = "replacement_recommended"
    GARANTIA_VENCENDO = "warranty_expiring"
    DEPRECIACAO_COMPLETA = "fully_depreciated"
    EQUIPAMENTO_NAO_LOCALIZADO = "equipment_missing"


@dataclass
class RFIDTag:
    """Tag RFID associada ao equipamento."""

    id: str
    rfid_code: str
    equipment_id: str
    last_scan_location: str
    last_scan_datetime: datetime
    scan_count: int
    is_active: bool = True


@dataclass
class EquipmentLocation:
    """Localização do equipamento."""

    building: str
    floor: str
    room: str
    area: str
    coordinates: tuple[float, float] | None = None
    last_updated: datetime = None


@dataclass
class MaintenanceRecord:
    """Registro de manutenção."""

    id: str
    equipment_id: str
    date: datetime
    type: str  # preventiva, corretiva, preditiva
    description: str
    cost: float
    technician: str
    parts_used: list[str]
    next_maintenance_date: datetime


@dataclass
class DepreciationInfo:
    """Informações de depreciação."""

    method: str  # linear, accelerated, units_of_production
    useful_life_years: float
    salvage_value: float
    annual_depreciation: float
    accumulated_depreciation: float
    book_value: float
    depreciation_rate: float


@dataclass
class Equipment:
    """Equipamento com rastreamento RFID e gestão de ciclo de vida."""

    id: str
    name: str
    category: EquipmentCategory
    manufacturer: str
    model: str
    serial_number: str
    rfid_tag: RFIDTag
    purchase_date: datetime
    purchase_price: float
    warranty_end_date: datetime
    expected_lifespan_years: float
    current_location: EquipmentLocation
    status: EquipmentStatus
    lifecycle_stage: LifecycleStage
    depreciation: DepreciationInfo
    maintenance_records: list[MaintenanceRecord]
    last_maintenance_date: datetime | None
    next_maintenance_date: datetime | None
    usage_hours: float = 0.0
    condition_score: float = 100.0  # 0-100
    replacement_cost_current: float = 0.0


@dataclass
class LifecycleAlert:
    """Alerta do ciclo de vida do equipamento."""

    id: str
    equipment_id: str
    alert_type: AlertType
    severity: str  # low, medium, high, critical
    title: str
    message: str
    created_at: datetime
    due_date: datetime | None
    estimated_cost: float
    recommended_action: str
    is_resolved: bool = False


@dataclass
class InventoryReport:
    """Relatório de inventário."""

    total_equipment: int
    total_value_book: float
    total_value_replacement: float
    by_category: dict[str, dict[str, Any]]
    by_location: dict[str, int]
    by_status: dict[str, int]
    by_lifecycle_stage: dict[str, int]
    maintenance_alerts: int
    replacement_recommendations: int
    generated_at: datetime


@dataclass
class LifecycleAnalytics:
    """Analytics do ciclo de vida dos equipamentos."""

    avg_equipment_age_years: float
    avg_condition_score: float
    total_depreciation: float
    maintenance_cost_monthly: float
    replacement_pipeline_value: float
    inventory_turnover_ratio: float
    rfid_scan_accuracy: float
    equipment_utilization: float


class RFIDLifecycleService:
    """Serviço de RFID + Gestão do Ciclo de Vida de Equipamentos."""

    def __init__(self):
        self.equipment: dict[str, Equipment] = {}
        self.rfid_tags: dict[str, RFIDTag] = {}
        self.alerts: dict[str, LifecycleAlert] = {}
        self.scan_history: list[dict[str, Any]] = []

        # Inicializar com dados de demonstração
        self._initialize_demo_data()

    def _initialize_demo_data(self):
        """Inicializar com equipamentos de demonstração."""

        demo_equipment = [
            {
                "name": "Bomba Centrífuga 15CV",
                "category": EquipmentCategory.HIDRAULICO,
                "manufacturer": "Schneider",
                "model": "BCF-15",
                "serial_number": "SCH-2023-001",
                "purchase_price": 8500.0,
                "lifespan": 12.0,
                "location": {"building": "Torre A", "floor": "Subsolo", "room": "Casa Máquinas", "area": "Hidráulica"},
            },
            {
                "name": "Central CFTV 32 Canais",
                "category": EquipmentCategory.SEGURANCA,
                "manufacturer": "Hikvision",
                "model": "DS-7732NI-I4",
                "serial_number": "HIK-2023-002",
                "purchase_price": 3200.0,
                "lifespan": 8.0,
                "location": {"building": "Torre A", "floor": "Térreo", "room": "Portaria", "area": "Segurança"},
            },
            {
                "name": "Motor Portão Eletrônico",
                "category": EquipmentCategory.ELETRICO,
                "manufacturer": "Garen",
                "model": "GTX-3000",
                "serial_number": "GAR-2023-003",
                "purchase_price": 1800.0,
                "lifespan": 10.0,
                "location": {"building": "Entrada", "floor": "Térreo", "room": "Portaria", "area": "Acesso"},
            },
            {
                "name": "Painel Elevador 8 Andares",
                "category": EquipmentCategory.ELETRONICO,
                "manufacturer": "Otis",
                "model": "OT-8F-2023",
                "serial_number": "OTI-2023-004",
                "purchase_price": 12000.0,
                "lifespan": 15.0,
                "location": {"building": "Torre A", "floor": "Térreo", "room": "Casa Máquinas", "area": "Elevadores"},
            },
            {
                "name": "Switch Gigabit 48 Portas",
                "category": EquipmentCategory.COMUNICACAO,
                "manufacturer": "Cisco",
                "model": "SF300-48",
                "serial_number": "CIS-2023-005",
                "purchase_price": 2500.0,
                "lifespan": 7.0,
                "location": {"building": "Torre A", "floor": "Térreo", "room": "TI", "area": "Rede"},
            },
        ]

        for i, eq_data in enumerate(demo_equipment, 1):
            equipment_id = f"EQ_{i:04d}"
            rfid_code = f"RFID_{random.randint(100000, 999999):06d}"  # noqa: S311

            # Criar tag RFID
            rfid_tag = RFIDTag(
                id=f"TAG_{i:04d}",
                rfid_code=rfid_code,
                equipment_id=equipment_id,
                last_scan_location=f"{eq_data['location']['building']} - {eq_data['location']['room']}",
                last_scan_datetime=datetime.now() - timedelta(hours=random.randint(1, 72)),  # noqa: S311
                scan_count=random.randint(50, 200),  # noqa: S311
            )

            # Criar localização
            location = EquipmentLocation(
                building=eq_data["location"]["building"],
                floor=eq_data["location"]["floor"],
                room=eq_data["location"]["room"],
                area=eq_data["location"]["area"],
                coordinates=(random.uniform(-23.0, -22.0), random.uniform(-46.0, -45.0)),  # noqa: S311
                last_updated=datetime.now(),
            )

            # Calcular depreciação
            purchase_date = datetime.now() - timedelta(days=random.randint(365, 1095))  # 1-3 anos  # noqa: S311
            age_years = (datetime.now() - purchase_date).days / 365.25
            annual_depreciation = eq_data["purchase_price"] / eq_data["lifespan"]
            accumulated_depreciation = min(annual_depreciation * age_years, eq_data["purchase_price"])
            book_value = eq_data["purchase_price"] - accumulated_depreciation

            depreciation = DepreciationInfo(
                method="linear",
                useful_life_years=eq_data["lifespan"],
                salvage_value=eq_data["purchase_price"] * 0.1,  # 10% valor residual
                annual_depreciation=annual_depreciation,
                accumulated_depreciation=accumulated_depreciation,
                book_value=book_value,
                depreciation_rate=1 / eq_data["lifespan"],
            )

            # Criar equipamento
            equipment = Equipment(
                id=equipment_id,
                name=eq_data["name"],
                category=eq_data["category"],
                manufacturer=eq_data["manufacturer"],
                model=eq_data["model"],
                serial_number=eq_data["serial_number"],
                rfid_tag=rfid_tag,
                purchase_date=purchase_date,
                purchase_price=eq_data["purchase_price"],
                warranty_end_date=purchase_date + timedelta(days=365 * 2),  # 2 anos garantia
                expected_lifespan_years=eq_data["lifespan"],
                current_location=location,
                status=EquipmentStatus.OPERACIONAL,
                lifecycle_stage=LifecycleStage.OPERACAO,
                depreciation=depreciation,
                maintenance_records=[],
                last_maintenance_date=datetime.now() - timedelta(days=random.randint(30, 180)),  # noqa: S311
                next_maintenance_date=datetime.now() + timedelta(days=random.randint(30, 120)),  # noqa: S311
                usage_hours=random.uniform(5000, 15000),  # noqa: S311
                condition_score=random.uniform(70, 95),  # noqa: S311
                replacement_cost_current=eq_data["purchase_price"]
                * random.uniform(1.05, 1.25),  # inflação  # noqa: S311
            )

            self.equipment[equipment_id] = equipment
            self.rfid_tags[rfid_code] = rfid_tag

        # Gerar alertas automáticos
        asyncio.create_task(self._generate_lifecycle_alerts())

    async def scan_rfid_tag(self, rfid_code: str, location: str, scanner_id: str = "default") -> bool:
        """Registrar scan de tag RFID."""
        if rfid_code not in self.rfid_tags:
            return False

        rfid_tag = self.rfid_tags[rfid_code]
        equipment = self.equipment.get(rfid_tag.equipment_id)

        if not equipment:
            return False

        # Atualizar informações do scan
        rfid_tag.last_scan_location = location
        rfid_tag.last_scan_datetime = datetime.now()
        rfid_tag.scan_count += 1

        # Atualizar localização do equipamento se mudou
        if location != f"{equipment.current_location.building} - {equipment.current_location.room}":
            # Parsear localização (formato: "Building - Room")
            parts = location.split(" - ")
            if len(parts) >= 2:
                equipment.current_location.building = parts[0]
                equipment.current_location.room = parts[1]
                equipment.current_location.last_updated = datetime.now()

        # Registrar no histórico
        scan_record = {
            "rfid_code": rfid_code,
            "equipment_id": rfid_tag.equipment_id,
            "location": location,
            "scanner_id": scanner_id,
            "timestamp": datetime.now(),
            "equipment_name": equipment.name,
        }
        self.scan_history.append(scan_record)

        # Manter apenas últimos 1000 scans
        if len(self.scan_history) > 1000:
            self.scan_history = self.scan_history[-1000:]

        logger.info(f"RFID scan registrado: {equipment.name} em {location}")
        return True

    async def get_equipment_by_rfid(self, rfid_code: str) -> Equipment | None:
        """Obter equipamento por código RFID."""
        rfid_tag = self.rfid_tags.get(rfid_code)
        if not rfid_tag:
            return None

        return self.equipment.get(rfid_tag.equipment_id)

    async def get_equipment_location(self, equipment_id: str) -> EquipmentLocation | None:
        """Obter localização atual de um equipamento."""
        equipment = self.equipment.get(equipment_id)
        return equipment.current_location if equipment else None

    async def update_equipment_condition(self, equipment_id: str, condition_score: float, notes: str = "") -> bool:
        """Atualizar condição do equipamento."""
        equipment = self.equipment.get(equipment_id)
        if not equipment:
            return False

        equipment.condition_score = max(0, min(100, condition_score))

        # Ajustar lifecycle stage baseado na condição
        if condition_score < 30:
            equipment.lifecycle_stage = LifecycleStage.SUBSTITUICAO
            equipment.status = EquipmentStatus.INATIVO
        elif condition_score < 50:
            equipment.lifecycle_stage = LifecycleStage.MANUTENCAO
        else:
            equipment.lifecycle_stage = LifecycleStage.OPERACAO
            if equipment.status == EquipmentStatus.INATIVO:
                equipment.status = EquipmentStatus.OPERACIONAL

        # Criar alerta se condição está ruim
        if condition_score < 60:
            await self._create_condition_alert(equipment, condition_score)

        return True

    async def _create_condition_alert(self, equipment: Equipment, condition_score: float):
        """Criar alerta baseado na condição do equipamento."""
        severity = "high" if condition_score < 40 else "medium" if condition_score < 60 else "low"
        alert_type = AlertType.SUBSTITUICAO_RECOMENDADA if condition_score < 40 else AlertType.MANUTENCAO_VENCIDA

        alert = LifecycleAlert(
            id=f"ALERT_{len(self.alerts) + 1:04d}",
            equipment_id=equipment.id,
            alert_type=alert_type,
            severity=severity,
            title=f"Condição {equipment.name} Degradada",
            message=f"Equipamento {equipment.name} com condição {condition_score:.1f}% requer atenção",
            created_at=datetime.now(),
            due_date=datetime.now() + timedelta(days=7 if severity == "high" else 30),
            estimated_cost=equipment.replacement_cost_current
            if alert_type == AlertType.SUBSTITUICAO_RECOMENDADA
            else equipment.replacement_cost_current * 0.2,
            recommended_action="Substituir equipamento" if condition_score < 40 else "Agendar manutenção corretiva",
        )

        self.alerts[alert.id] = alert

    async def calculate_depreciation(self, equipment_id: str) -> bool:
        """Recalcular depreciação do equipamento."""
        equipment = self.equipment.get(equipment_id)
        if not equipment:
            return False

        # Calcular idade atual
        age_years = (datetime.now() - equipment.purchase_date).days / 365.25

        # Método linear de depreciação
        if equipment.depreciation.method == "linear":
            annual_depreciation = (
                equipment.purchase_price - equipment.depreciation.salvage_value
            ) / equipment.depreciation.useful_life_years
            accumulated_depreciation = min(
                annual_depreciation * age_years, equipment.purchase_price - equipment.depreciation.salvage_value
            )
        else:
            # Implementar outros métodos se necessário
            accumulated_depreciation = equipment.depreciation.accumulated_depreciation

        equipment.depreciation.accumulated_depreciation = accumulated_depreciation
        equipment.depreciation.book_value = equipment.purchase_price - accumulated_depreciation

        # Criar alerta se completamente depreciado
        if equipment.depreciation.book_value <= equipment.depreciation.salvage_value:
            await self._create_depreciation_alert(equipment)

        return True

    async def _create_depreciation_alert(self, equipment: Equipment):
        """Criar alerta de depreciação completa."""
        alert = LifecycleAlert(
            id=f"ALERT_{len(self.alerts) + 1:04d}",
            equipment_id=equipment.id,
            alert_type=AlertType.DEPRECIACAO_COMPLETA,
            severity="medium",
            title=f"Depreciação Completa - {equipment.name}",
            message=f"Equipamento {equipment.name} totalmente depreciado. Considere substituição.",
            created_at=datetime.now(),
            due_date=datetime.now() + timedelta(days=90),
            estimated_cost=equipment.replacement_cost_current,
            recommended_action="Avaliar substituição ou extensão da vida útil",
        )

        self.alerts[alert.id] = alert

    async def add_maintenance_record(
        self,
        equipment_id: str,
        maintenance_type: str,
        description: str,
        cost: float,
        technician: str,
        parts_used: list[str] = None,
    ) -> bool:
        """Adicionar registro de manutenção."""
        equipment = self.equipment.get(equipment_id)
        if not equipment:
            return False

        parts_used = parts_used or []
        maintenance_record = MaintenanceRecord(
            id=f"MAINT_{len([r for eq in self.equipment.values() for r in eq.maintenance_records]) + 1:04d}",
            equipment_id=equipment_id,
            date=datetime.now(),
            type=maintenance_type,
            description=description,
            cost=cost,
            technician=technician,
            parts_used=parts_used,
            next_maintenance_date=datetime.now() + timedelta(days=90),  # 3 meses
        )

        equipment.maintenance_records.append(maintenance_record)
        equipment.last_maintenance_date = datetime.now()
        equipment.next_maintenance_date = maintenance_record.next_maintenance_date

        # Melhorar condition score após manutenção
        if maintenance_type in ["preventiva", "corretiva"]:
            improvement = 15 if maintenance_type == "corretiva" else 10
            equipment.condition_score = min(95, equipment.condition_score + improvement)

        return True

    async def _generate_lifecycle_alerts(self):
        """Gerar alertas automáticos baseados no ciclo de vida."""
        for equipment in self.equipment.values():
            # Alerta de manutenção vencida
            if equipment.next_maintenance_date and equipment.next_maintenance_date <= datetime.now():
                alert = LifecycleAlert(
                    id=f"ALERT_{len(self.alerts) + 1:04d}",
                    equipment_id=equipment.id,
                    alert_type=AlertType.MANUTENCAO_VENCIDA,
                    severity="medium",
                    title=f"Manutenção Vencida - {equipment.name}",
                    message=f"Equipamento {equipment.name} com manutenção vencida",
                    created_at=datetime.now(),
                    due_date=datetime.now() + timedelta(days=15),
                    estimated_cost=equipment.replacement_cost_current * 0.1,
                    recommended_action="Agendar manutenção preventiva",
                )
                self.alerts[alert.id] = alert

            # Alerta de garantia vencendo
            if equipment.warranty_end_date <= datetime.now() + timedelta(days=30):
                alert = LifecycleAlert(
                    id=f"ALERT_{len(self.alerts) + 1:04d}",
                    equipment_id=equipment.id,
                    alert_type=AlertType.GARANTIA_VENCENDO,
                    severity="low",
                    title=f"Garantia Vencendo - {equipment.name}",
                    message=f"Garantia do equipamento {equipment.name} vence em breve",
                    created_at=datetime.now(),
                    due_date=equipment.warranty_end_date,
                    estimated_cost=0.0,
                    recommended_action="Revisar cobertura de garantia e considerar extensão",
                )
                self.alerts[alert.id] = alert

    async def get_active_alerts(self, severity_filter: str | None = None) -> list[LifecycleAlert]:
        """Obter alertas ativos."""
        alerts = [alert for alert in self.alerts.values() if not alert.is_resolved]

        if severity_filter:
            alerts = [alert for alert in alerts if alert.severity == severity_filter]

        return sorted(alerts, key=lambda x: x.created_at, reverse=True)

    async def generate_inventory_report(self) -> InventoryReport:
        """Gerar relatório completo de inventário."""
        total_equipment = len(self.equipment)
        total_value_book = sum(eq.depreciation.book_value for eq in self.equipment.values())
        total_value_replacement = sum(eq.replacement_cost_current for eq in self.equipment.values())

        # Por categoria
        by_category = {}
        for eq in self.equipment.values():
            cat = eq.category.value
            if cat not in by_category:
                by_category[cat] = {"count": 0, "book_value": 0, "replacement_value": 0}

            by_category[cat]["count"] += 1
            by_category[cat]["book_value"] += eq.depreciation.book_value
            by_category[cat]["replacement_value"] += eq.replacement_cost_current

        # Por localização
        by_location = {}
        for eq in self.equipment.values():
            location = f"{eq.current_location.building} - {eq.current_location.room}"
            by_location[location] = by_location.get(location, 0) + 1

        # Por status
        by_status = {}
        for eq in self.equipment.values():
            status = eq.status.value
            by_status[status] = by_status.get(status, 0) + 1

        # Por estágio do ciclo de vida
        by_lifecycle_stage = {}
        for eq in self.equipment.values():
            stage = eq.lifecycle_stage.value
            by_lifecycle_stage[stage] = by_lifecycle_stage.get(stage, 0) + 1

        # Contar alertas
        active_alerts = await self.get_active_alerts()
        maintenance_alerts = len([a for a in active_alerts if a.alert_type == AlertType.MANUTENCAO_VENCIDA])
        replacement_recommendations = len(
            [a for a in active_alerts if a.alert_type == AlertType.SUBSTITUICAO_RECOMENDADA]
        )

        return InventoryReport(
            total_equipment=total_equipment,
            total_value_book=total_value_book,
            total_value_replacement=total_value_replacement,
            by_category=by_category,
            by_location=by_location,
            by_status=by_status,
            by_lifecycle_stage=by_lifecycle_stage,
            maintenance_alerts=maintenance_alerts,
            replacement_recommendations=replacement_recommendations,
            generated_at=datetime.now(),
        )

    async def get_lifecycle_analytics(self) -> LifecycleAnalytics:
        """Obter analytics do ciclo de vida."""
        if not self.equipment:
            return LifecycleAnalytics(
                avg_equipment_age_years=0,
                avg_condition_score=0,
                total_depreciation=0,
                maintenance_cost_monthly=0,
                replacement_pipeline_value=0,
                inventory_turnover_ratio=0,
                rfid_scan_accuracy=0,
                equipment_utilization=0,
            )

        # Idade média
        total_age = sum((datetime.now() - eq.purchase_date).days / 365.25 for eq in self.equipment.values())
        avg_age = total_age / len(self.equipment)

        # Condição média
        avg_condition = sum(eq.condition_score for eq in self.equipment.values()) / len(self.equipment)

        # Depreciação total
        total_depreciation = sum(eq.depreciation.accumulated_depreciation for eq in self.equipment.values())

        # Custo de manutenção mensal (últimos 6 meses)
        six_months_ago = datetime.now() - timedelta(days=180)
        maintenance_costs = []
        for eq in self.equipment.values():
            for record in eq.maintenance_records:
                if record.date >= six_months_ago:
                    maintenance_costs.append(record.cost)

        maintenance_cost_monthly = sum(maintenance_costs) / 6 if maintenance_costs else 0

        # Pipeline de substituição
        replacement_alerts = [a for a in self.alerts.values() if a.alert_type == AlertType.SUBSTITUICAO_RECOMENDADA]
        replacement_pipeline_value = sum(a.estimated_cost for a in replacement_alerts)

        # Taxa de rotatividade do inventário (simulada)
        inventory_turnover_ratio = random.uniform(0.8, 1.2)  # noqa: S311

        # Precisão de scan RFID
        total_scans = sum(tag.scan_count for tag in self.rfid_tags.values())
        successful_scans = total_scans  # Assumindo 100% de sucesso para demonstração
        rfid_scan_accuracy = (successful_scans / total_scans * 100) if total_scans > 0 else 100

        # Utilização dos equipamentos
        avg_utilization = sum(min(100, eq.usage_hours / (8760 * 3)) * 100 for eq in self.equipment.values()) / len(
            self.equipment
        )  # 3 anos = 8760*3 horas

        return LifecycleAnalytics(
            avg_equipment_age_years=avg_age,
            avg_condition_score=avg_condition,
            total_depreciation=total_depreciation,
            maintenance_cost_monthly=maintenance_cost_monthly,
            replacement_pipeline_value=replacement_pipeline_value,
            inventory_turnover_ratio=inventory_turnover_ratio,
            rfid_scan_accuracy=rfid_scan_accuracy,
            equipment_utilization=avg_utilization,
        )

    async def get_scan_history(self, equipment_id: str | None = None, last_n_records: int = 50) -> list[dict[str, Any]]:
        """Obter histórico de scans RFID."""
        history = self.scan_history

        if equipment_id:
            history = [record for record in history if record["equipment_id"] == equipment_id]

        return sorted(history, key=lambda x: x["timestamp"], reverse=True)[:last_n_records]

    async def find_equipment(self, search_term: str) -> list[Equipment]:
        """Buscar equipamentos por nome, modelo, local, etc."""
        results = []
        search_term = search_term.lower()

        for equipment in self.equipment.values():
            if (
                search_term in equipment.name.lower()
                or search_term in equipment.model.lower()
                or search_term in equipment.manufacturer.lower()
                or search_term in equipment.current_location.room.lower()
                or search_term in equipment.current_location.building.lower()
                or search_term in equipment.serial_number.lower()
            ):
                results.append(equipment)

        return results

    async def get_replacement_recommendations(self) -> list[dict[str, Any]]:
        """Obter recomendações de substituição baseadas em múltiplos fatores."""
        recommendations = []

        for equipment in self.equipment.values():
            # Calcular score de substituição baseado em múltiplos fatores
            age_factor = min(
                1.0, (datetime.now() - equipment.purchase_date).days / (equipment.expected_lifespan_years * 365)
            )
            condition_factor = (100 - equipment.condition_score) / 100
            depreciation_factor = equipment.depreciation.accumulated_depreciation / equipment.purchase_price

            # Score composto (0-1)
            replacement_score = age_factor * 0.4 + condition_factor * 0.4 + depreciation_factor * 0.2

            if replacement_score > 0.6:  # Limiar para recomendação
                priority = "alta" if replacement_score > 0.8 else "média" if replacement_score > 0.7 else "baixa"

                recommendation = {
                    "equipment_id": equipment.id,
                    "equipment_name": equipment.name,
                    "replacement_score": replacement_score,
                    "priority": priority,
                    "reasons": [],
                    "estimated_cost": equipment.replacement_cost_current,
                    "roi_potential": 0.0,
                }

                # Adicionar razões específicas
                if age_factor > 0.8:
                    recommendation["reasons"].append(
                        f"Idade avançada ({(datetime.now() - equipment.purchase_date).days / 365:.1f} anos)"
                    )

                if condition_factor > 0.5:
                    recommendation["reasons"].append(f"Condição degradada ({equipment.condition_score:.1f}%)")

                if depreciation_factor > 0.9:
                    recommendation["reasons"].append("Totalmente depreciado")

                # Simular ROI potencial da substituição
                maintenance_savings = equipment.replacement_cost_current * 0.15  # 15% economia em manutenção
                efficiency_gains = equipment.replacement_cost_current * 0.20  # 20% ganho em eficiência
                recommendation["roi_potential"] = maintenance_savings + efficiency_gains

                recommendations.append(recommendation)

        return sorted(recommendations, key=lambda x: x["replacement_score"], reverse=True)


# Instância singleton do serviço
rfid_lifecycle_service = RFIDLifecycleService()


if __name__ == "__main__":
    # Teste básico
    async def test_rfid_lifecycle():
        service = RFIDLifecycleService()

        # Simular scan RFID
        rfid_code = list(service.rfid_tags.keys())[0]
        await service.scan_rfid_tag(rfid_code, "Torre A - Portaria", "SCANNER_001")

        # Obter analytics
        analytics = await service.get_lifecycle_analytics()
        print(f"Average Equipment Age: {analytics.avg_equipment_age_years:.1f} years")
        print(f"RFID Scan Accuracy: {analytics.rfid_scan_accuracy:.1f}%")

    asyncio.run(test_rfid_lifecycle())
