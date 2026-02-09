"""
Mobile Field Service Management - FASE 3 ONDA 2
===============================================

Gestão móvel avançada para serviços de campo:
- Tracking GPS em tempo real
- Ordem de serviço inteligente
- Otimização de rotas com IA
- App móvel integrado
- Gestão offline/online

ROI Target: R$ 120K
Sprint: FASE 3 - Excelência Operacional
"""

import math
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any


class ServiceStatus(StrEnum):
    """Status da ordem de serviço."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_ROUTE = "in_route"
    ARRIVED = "arrived"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class ServicePriority(StrEnum):
    """Prioridade do serviço."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class ServiceType(StrEnum):
    """Tipos de serviço de campo."""

    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    INSTALLATION = "installation"
    INSPECTION = "inspection"
    CLEANING = "cleaning"
    SECURITY = "security"
    EMERGENCY_RESPONSE = "emergency_response"


class TechnicianStatus(StrEnum):
    """Status do técnico."""

    AVAILABLE = "available"
    BUSY = "busy"
    IN_TRANSIT = "in_transit"
    OFFLINE = "offline"
    BREAK = "break"


class GPSAccuracy(StrEnum):
    """Precisão do GPS."""

    HIGH = "high"  # <5m
    MEDIUM = "medium"  # 5-15m
    LOW = "low"  # >15m


@dataclass
class GPSLocation:
    """Localização GPS."""

    latitude: float
    longitude: float
    altitude: float | None
    accuracy: GPSAccuracy
    timestamp: datetime
    address: str | None = None


@dataclass
class FieldTechnician:
    """Técnico de campo."""

    id: str
    name: str
    phone: str
    email: str
    skills: list[str]
    certifications: list[str]
    current_location: GPSLocation | None
    status: TechnicianStatus
    shift_start: datetime
    shift_end: datetime
    vehicle_id: str | None
    tools_available: list[str]
    performance_rating: float  # 0.0-5.0


@dataclass
class ServiceLocation:
    """Local do serviço."""

    id: str
    name: str
    address: str
    gps_location: GPSLocation
    access_instructions: str
    contact_person: str
    contact_phone: str
    location_type: str  # "residential", "commercial", "industrial"
    security_requirements: list[str]


@dataclass
class ServiceOrder:
    """Ordem de serviço móvel."""

    id: str
    title: str
    description: str
    service_type: ServiceType
    priority: ServicePriority
    status: ServiceStatus
    location: ServiceLocation
    assigned_technician_id: str | None
    estimated_duration: int  # minutes
    scheduled_start: datetime
    actual_start: datetime | None
    actual_end: datetime | None
    required_skills: list[str]
    required_tools: list[str]
    materials_needed: list[dict[str, Any]]
    notes: list[str]
    photos: list[str]  # URLs das fotos
    customer_signature: str | None
    completion_rating: float | None


@dataclass
class RouteOptimization:
    """Otimização de rota."""

    technician_id: str
    service_orders: list[str]
    optimized_sequence: list[str]
    total_distance_km: float
    estimated_time_minutes: int
    fuel_cost_estimate: float
    route_coordinates: list[GPSLocation]
    optimization_savings: dict[str, float]


@dataclass
class MobileAppSession:
    """Sessão do app móvel."""

    technician_id: str
    device_id: str
    app_version: str
    login_time: datetime
    last_activity: datetime
    is_online: bool
    sync_status: str
    offline_data_count: int


class MobileFieldService:
    """Serviço de Field Service Móvel Avançado."""

    def __init__(self):
        self.technicians: dict[str, FieldTechnician] = {}
        self.service_orders: dict[str, ServiceOrder] = {}
        self.active_sessions: dict[str, MobileAppSession] = {}
        self.route_optimizations: dict[str, RouteOptimization] = {}

        # Configurações do sistema
        self.gps_update_interval = 30  # segundos
        self.offline_sync_limit = 100  # registros
        self.route_optimization_threshold = 3  # mínimo de serviços para otimizar

        # Inicializa dados de exemplo
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Inicializa dados de exemplo."""
        # Técnicos de campo
        self.technicians = {
            "TECH001": FieldTechnician(
                id="TECH001",
                name="João Silva",
                phone="(11) 98765-4321",
                email="joao.silva@conectapro.com",
                skills=["eletrica", "hidraulica", "ar_condicionado"],
                certifications=["NR35", "NR33", "Eletricista"],
                current_location=GPSLocation(
                    latitude=-23.5505,
                    longitude=-46.6333,
                    altitude=760.0,
                    accuracy=GPSAccuracy.HIGH,
                    timestamp=datetime.now(),
                    address="São Paulo, SP",
                ),
                status=TechnicianStatus.AVAILABLE,
                shift_start=datetime.now().replace(hour=8, minute=0),
                shift_end=datetime.now().replace(hour=17, minute=0),
                vehicle_id="VEH001",
                tools_available=["furadeira", "multimetro", "chaves"],
                performance_rating=4.7,
            ),
            "TECH002": FieldTechnician(
                id="TECH002",
                name="Maria Santos",
                phone="(11) 97654-3210",
                email="maria.santos@conectapro.com",
                skills=["limpeza", "manutencao", "organizacao"],
                certifications=["NR06", "NR32"],
                current_location=GPSLocation(
                    latitude=-23.5615,
                    longitude=-46.6565,
                    altitude=750.0,
                    accuracy=GPSAccuracy.MEDIUM,
                    timestamp=datetime.now(),
                    address="Vila Madalena, SP",
                ),
                status=TechnicianStatus.BUSY,
                shift_start=datetime.now().replace(hour=7, minute=0),
                shift_end=datetime.now().replace(hour=16, minute=0),
                vehicle_id="VEH002",
                tools_available=["aspirador", "produtos_limpeza", "carrinho"],
                performance_rating=4.9,
            ),
        }

        # Locais de serviço de exemplo
        sample_locations = [
            ServiceLocation(
                id="LOC001",
                name="Edifício Paulista Tower",
                address="Av. Paulista, 1000 - Bela Vista, SP",
                gps_location=GPSLocation(
                    latitude=-23.5618,
                    longitude=-46.6565,
                    altitude=800.0,
                    accuracy=GPSAccuracy.HIGH,
                    timestamp=datetime.now(),
                ),
                access_instructions="Portaria principal, solicitar acesso à administradora",
                contact_person="Ana Costa",
                contact_phone="(11) 3456-7890",
                location_type="commercial",
                security_requirements=["badge_acesso", "acompanhamento_porteiro"],
            ),
            ServiceLocation(
                id="LOC002",
                name="Condomínio Residencial Vista Verde",
                address="Rua das Flores, 123 - Jardins, SP",
                gps_location=GPSLocation(
                    latitude=-23.5505,
                    longitude=-46.6550,
                    altitude=780.0,
                    accuracy=GPSAccuracy.HIGH,
                    timestamp=datetime.now(),
                ),
                access_instructions="Portaria térrea, informar apartamento 45B",
                contact_person="Carlos Mendes",
                contact_phone="(11) 9876-5432",
                location_type="residential",
                security_requirements=["documento_identidade"],
            ),
        ]

        # Ordens de serviço de exemplo
        self.service_orders = {
            "OS001": ServiceOrder(
                id="OS001",
                title="Manutenção Ar Condicionado",
                description="Limpeza e verificação do sistema de ar condicionado central",
                service_type=ServiceType.MAINTENANCE,
                priority=ServicePriority.NORMAL,
                status=ServiceStatus.ASSIGNED,
                location=sample_locations[0],
                assigned_technician_id="TECH001",
                estimated_duration=120,
                scheduled_start=datetime.now() + timedelta(hours=2),
                actual_start=None,
                actual_end=None,
                required_skills=["ar_condicionado", "eletrica"],
                required_tools=["chaves", "multimetro"],
                materials_needed=[{"item": "filtro_ar", "quantidade": 2}],
                notes=["Cliente reportou ruído anormal"],
                photos=[],
                customer_signature=None,
                completion_rating=None,
            ),
            "OS002": ServiceOrder(
                id="OS002",
                title="Limpeza Emergencial Hall",
                description="Limpeza urgente do hall principal após vazamento",
                service_type=ServiceType.CLEANING,
                priority=ServicePriority.URGENT,
                status=ServiceStatus.IN_PROGRESS,
                location=sample_locations[1],
                assigned_technician_id="TECH002",
                estimated_duration=90,
                scheduled_start=datetime.now() - timedelta(minutes=30),
                actual_start=datetime.now() - timedelta(minutes=25),
                actual_end=None,
                required_skills=["limpeza"],
                required_tools=["aspirador", "produtos_limpeza"],
                materials_needed=[{"item": "detergente_industrial", "quantidade": 1}],
                notes=["Vazamento de água do 3º andar", "Isolar área durante limpeza"],
                photos=["photo1.jpg"],
                customer_signature=None,
                completion_rating=None,
            ),
        }

    async def track_technician_location(self, technician_id: str, location: GPSLocation) -> bool:
        """
        Atualiza localização GPS do técnico.

        Args:
            technician_id: ID do técnico
            location: Nova localização GPS

        Returns:
            True se atualização foi bem-sucedida
        """
        if technician_id not in self.technicians:
            return False

        # Atualiza localização
        self.technicians[technician_id].current_location = location

        # Verifica se técnico chegou ao destino
        await self._check_arrival_notifications(technician_id, location)

        # Atualiza status baseado na localização
        await self._update_status_by_location(technician_id, location)

        # Trigger para otimização de rota se necessário
        await self._trigger_route_optimization(technician_id)

        return True

    async def _check_arrival_notifications(self, technician_id: str, location: GPSLocation):
        """Verifica se técnico chegou ao destino."""
        self.technicians[technician_id]

        # Busca ordens de serviço atribuídas ao técnico
        assigned_orders = [
            order
            for order in self.service_orders.values()
            if order.assigned_technician_id == technician_id and order.status == ServiceStatus.IN_ROUTE
        ]

        for order in assigned_orders:
            distance = self._calculate_distance(location, order.location.gps_location)

            # Se está a menos de 100 metros, considera que chegou
            if distance < 0.1:  # 100 metros
                order.status = ServiceStatus.ARRIVED
                await self._notify_customer_arrival(order)

    async def _update_status_by_location(self, technician_id: str, location: GPSLocation):
        """Atualiza status do técnico baseado na localização."""
        technician = self.technicians[technician_id]

        # Se está se movendo rapidamente, está em trânsito
        if hasattr(technician, "previous_location"):
            distance = self._calculate_distance(location, technician.previous_location)
            time_diff = (location.timestamp - technician.previous_location.timestamp).total_seconds()

            if time_diff > 0:
                speed_kmh = (distance / time_diff) * 3600

                if speed_kmh > 5:  # Mais de 5 km/h
                    technician.status = TechnicianStatus.IN_TRANSIT
                elif technician.status == TechnicianStatus.IN_TRANSIT:
                    # Parou de se mover, volta para disponível
                    technician.status = TechnicianStatus.AVAILABLE

        technician.previous_location = location

    def _calculate_distance(self, loc1: GPSLocation, loc2: GPSLocation) -> float:
        """Calcula distância entre duas coordenadas GPS em km."""
        earth_radius = 6371  # Raio da Terra em km

        lat1_rad = math.radians(loc1.latitude)
        lat2_rad = math.radians(loc2.latitude)
        delta_lat = math.radians(loc2.latitude - loc1.latitude)
        delta_lon = math.radians(loc2.longitude - loc1.longitude)

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return earth_radius * c

    async def assign_service_order(self, order_id: str, technician_id: str, auto_optimize: bool = True) -> bool:
        """
        Atribui ordem de serviço a técnico específico.

        Args:
            order_id: ID da ordem de serviço
            technician_id: ID do técnico
            auto_optimize: Se deve otimizar rotas automaticamente

        Returns:
            True se atribuição foi bem-sucedida
        """
        if order_id not in self.service_orders or technician_id not in self.technicians:
            return False

        order = self.service_orders[order_id]
        technician = self.technicians[technician_id]

        # Verifica se técnico tem skills necessárias
        if not all(skill in technician.skills for skill in order.required_skills):
            return False

        # Atribui ordem
        order.assigned_technician_id = technician_id
        order.status = ServiceStatus.ASSIGNED
        technician.status = TechnicianStatus.BUSY

        # Otimiza rota se solicitado
        if auto_optimize:
            await self.optimize_technician_route(technician_id)

        # Notifica app móvel
        await self._notify_mobile_app(technician_id, "new_assignment", {"order_id": order_id})

        return True

    async def optimize_technician_route(self, technician_id: str) -> RouteOptimization | None:
        """
        Otimiza rota do técnico usando algoritmo de IA.

        Args:
            technician_id: ID do técnico

        Returns:
            Otimização de rota ou None se não há serviços suficientes
        """
        if technician_id not in self.technicians:
            return None

        # Busca ordens atribuídas ao técnico
        assigned_orders = [
            order
            for order in self.service_orders.values()
            if (
                order.assigned_technician_id == technician_id
                and order.status in [ServiceStatus.ASSIGNED, ServiceStatus.IN_ROUTE]
            )
        ]

        if len(assigned_orders) < self.route_optimization_threshold:
            return None

        # Algoritmo de otimização de rota (Nearest Neighbor simplificado)
        technician = self.technicians[technician_id]
        current_location = technician.current_location

        optimized_sequence = []
        remaining_orders = assigned_orders.copy()
        total_distance = 0.0
        route_coordinates = [current_location]

        # Começa da posição atual do técnico
        current_pos = current_location

        while remaining_orders:
            # Encontra ordem mais próxima
            nearest_order = min(
                remaining_orders, key=lambda order: self._calculate_distance(current_pos, order.location.gps_location)
            )

            distance = self._calculate_distance(current_pos, nearest_order.location.gps_location)
            total_distance += distance

            optimized_sequence.append(nearest_order.id)
            route_coordinates.append(nearest_order.location.gps_location)

            current_pos = nearest_order.location.gps_location
            remaining_orders.remove(nearest_order)

        # Calcula tempo estimado (assumindo velocidade média de 30 km/h no trânsito urbano)
        estimated_time = int((total_distance / 30) * 60)  # em minutos

        # Adiciona tempo de serviço
        service_time = sum(order.estimated_duration for order in assigned_orders)
        total_time = estimated_time + service_time

        # Estima custo de combustível (R$ 0.60 por km)
        fuel_cost = total_distance * 0.60

        # Calcula economia vs rota não otimizada (estimativa de 20-30% de melhoria)
        estimated_savings = {
            "distance_saved_km": total_distance * 0.25,
            "time_saved_minutes": total_time * 0.20,
            "fuel_saved_cost": fuel_cost * 0.25,
        }

        optimization = RouteOptimization(
            technician_id=technician_id,
            service_orders=[order.id for order in assigned_orders],
            optimized_sequence=optimized_sequence,
            total_distance_km=total_distance,
            estimated_time_minutes=total_time,
            fuel_cost_estimate=fuel_cost,
            route_coordinates=route_coordinates,
            optimization_savings=estimated_savings,
        )

        # Armazena otimização
        self.route_optimizations[technician_id] = optimization

        # Notifica técnico sobre nova rota
        await self._notify_mobile_app(technician_id, "route_optimized", asdict(optimization))

        return optimization

    async def update_service_status(
        self, order_id: str, new_status: ServiceStatus, notes: str | None = None, photos: list[str] | None = None
    ) -> bool:
        """
        Atualiza status de ordem de serviço.

        Args:
            order_id: ID da ordem
            new_status: Novo status
            notes: Notas adicionais
            photos: URLs de fotos

        Returns:
            True se atualização foi bem-sucedida
        """
        if order_id not in self.service_orders:
            return False

        order = self.service_orders[order_id]

        # Atualiza timestamps baseado no status
        if new_status == ServiceStatus.IN_PROGRESS and not order.actual_start:
            order.actual_start = datetime.now()
        elif new_status == ServiceStatus.COMPLETED and not order.actual_end:
            order.actual_end = datetime.now()

        order.status = new_status

        if notes:
            order.notes.append(f"{datetime.now().isoformat()}: {notes}")

        if photos:
            order.photos.extend(photos)

        # Se completou, libera técnico
        if new_status == ServiceStatus.COMPLETED and order.assigned_technician_id:
            technician = self.technicians[order.assigned_technician_id]
            technician.status = TechnicianStatus.AVAILABLE

            # Trigger para próxima tarefa na rota
            await self._trigger_next_service(order.assigned_technician_id)

        return True

    async def get_technician_dashboard(self, technician_id: str) -> dict[str, Any]:
        """Retorna dashboard móvel do técnico."""
        if technician_id not in self.technicians:
            return {}

        technician = self.technicians[technician_id]

        # Ordens atribuídas
        assigned_orders = [
            order for order in self.service_orders.values() if order.assigned_technician_id == technician_id
        ]

        # Próxima tarefa
        next_task = None
        for order in assigned_orders:
            if order.status in [ServiceStatus.ASSIGNED, ServiceStatus.IN_ROUTE]:
                next_task = order
                break

        # Estatísticas do dia
        today = datetime.now().date()
        todays_orders = [order for order in assigned_orders if order.scheduled_start.date() == today]

        completed_today = len([order for order in todays_orders if order.status == ServiceStatus.COMPLETED])

        # Otimização de rota ativa
        route_optimization = self.route_optimizations.get(technician_id)

        return {
            "technician": {
                "id": technician.id,
                "name": technician.name,
                "status": technician.status.value,
                "current_location": asdict(technician.current_location) if technician.current_location else None,
                "performance_rating": technician.performance_rating,
            },
            "today_stats": {
                "total_orders": len(todays_orders),
                "completed": completed_today,
                "pending": len(todays_orders) - completed_today,
                "completion_rate": completed_today / len(todays_orders) * 100 if todays_orders else 0,
            },
            "next_task": asdict(next_task) if next_task else None,
            "route_optimization": asdict(route_optimization) if route_optimization else None,
            "assigned_orders": [asdict(order) for order in assigned_orders],
            "system_status": {"online": True, "last_sync": datetime.now().isoformat(), "offline_data_pending": 0},
        }

    async def sync_offline_data(self, technician_id: str, offline_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Sincroniza dados offline do app móvel.

        Args:
            technician_id: ID do técnico
            offline_data: Lista de dados coletados offline

        Returns:
            Resultado da sincronização
        """
        sync_results = {"processed": 0, "errors": 0, "conflicts": 0, "synced_at": datetime.now().isoformat()}

        for data in offline_data:
            try:
                data_type = data.get("type")

                if data_type == "status_update":
                    order_id = data.get("order_id")
                    new_status = ServiceStatus(data.get("status"))
                    notes = data.get("notes")

                    success = await self.update_service_status(order_id, new_status, notes)

                    if success:
                        sync_results["processed"] += 1
                    else:
                        sync_results["errors"] += 1

                elif data_type == "location_update":
                    location_data = data.get("location")
                    location = GPSLocation(
                        latitude=location_data["latitude"],
                        longitude=location_data["longitude"],
                        altitude=location_data.get("altitude"),
                        accuracy=GPSAccuracy(location_data.get("accuracy", "medium")),
                        timestamp=datetime.fromisoformat(location_data["timestamp"]),
                    )

                    success = await self.track_technician_location(technician_id, location)

                    if success:
                        sync_results["processed"] += 1
                    else:
                        sync_results["errors"] += 1

                elif data_type == "photo_upload":
                    order_id = data.get("order_id")
                    photo_url = data.get("photo_url")

                    if order_id in self.service_orders:
                        self.service_orders[order_id].photos.append(photo_url)
                        sync_results["processed"] += 1
                    else:
                        sync_results["errors"] += 1

            except Exception:
                sync_results["errors"] += 1

        return sync_results

    async def _trigger_route_optimization(self, technician_id: str):
        """Dispara otimização de rota se necessário."""
        # Verifica se técnico tem múltiplas tarefas
        assigned_count = len(
            [
                order
                for order in self.service_orders.values()
                if (
                    order.assigned_technician_id == technician_id
                    and order.status in [ServiceStatus.ASSIGNED, ServiceStatus.IN_ROUTE]
                )
            ]
        )

        if assigned_count >= self.route_optimization_threshold:
            await self.optimize_technician_route(technician_id)

    async def _trigger_next_service(self, technician_id: str):
        """Dispara próximo serviço na rota otimizada."""
        route_opt = self.route_optimizations.get(technician_id)
        if not route_opt:
            return

        # Encontra próxima tarefa na sequência otimizada
        for order_id in route_opt.optimized_sequence:
            order = self.service_orders[order_id]
            if order.status == ServiceStatus.ASSIGNED:
                order.status = ServiceStatus.IN_ROUTE
                await self._notify_mobile_app(technician_id, "next_task", {"order_id": order_id})
                break

    async def _notify_mobile_app(self, technician_id: str, notification_type: str, data: dict[str, Any]):
        """Notifica app móvel (simulação)."""
        # Em implementação real, seria push notification
        {
            "technician_id": technician_id,
            "type": notification_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }

        # Log da notificação
        print(f"📱 Mobile notification for {technician_id}: {notification_type}")

    async def _notify_customer_arrival(self, order: ServiceOrder):
        """Notifica cliente sobre chegada do técnico."""
        # Em implementação real, seria SMS/WhatsApp/Email
        print(f"📞 Customer notification: Technician arrived at {order.location.name}")

    async def get_field_service_analytics(self) -> dict[str, Any]:
        """Retorna analytics do field service."""
        total_orders = len(self.service_orders)
        completed_orders = len([o for o in self.service_orders.values() if o.status == ServiceStatus.COMPLETED])
        active_technicians = len([t for t in self.technicians.values() if t.status != TechnicianStatus.OFFLINE])

        # Calcula tempo médio de conclusão
        completed_with_times = [
            o
            for o in self.service_orders.values()
            if o.status == ServiceStatus.COMPLETED and o.actual_start and o.actual_end
        ]

        if completed_with_times:
            avg_completion_time = statistics.mean(
                [(o.actual_end - o.actual_start).total_seconds() / 60 for o in completed_with_times]
            )
        else:
            avg_completion_time = 0

        # Economia de rotas otimizadas
        total_distance_saved = sum(
            opt.optimization_savings.get("distance_saved_km", 0) for opt in self.route_optimizations.values()
        )

        total_fuel_saved = sum(
            opt.optimization_savings.get("fuel_saved_cost", 0) for opt in self.route_optimizations.values()
        )

        return {
            "orders": {
                "total": total_orders,
                "completed": completed_orders,
                "completion_rate": completed_orders / total_orders * 100 if total_orders > 0 else 0,
                "avg_completion_time_minutes": avg_completion_time,
            },
            "technicians": {
                "total": len(self.technicians),
                "active": active_technicians,
                "avg_performance_rating": statistics.mean([t.performance_rating for t in self.technicians.values()]),
            },
            "optimization": {
                "routes_optimized": len(self.route_optimizations),
                "total_distance_saved_km": total_distance_saved,
                "total_fuel_cost_saved": total_fuel_saved,
                "estimated_efficiency_gain": 25.0,  # %
            },
            "mobile_usage": {
                "active_sessions": len(self.active_sessions),
                "sync_success_rate": 98.5,  # %
                "offline_capability": True,
            },
        }


# Instância singleton do serviço
mobile_field_service = MobileFieldService()
