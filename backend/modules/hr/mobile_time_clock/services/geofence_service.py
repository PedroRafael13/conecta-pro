"""Service para operações de geofencing."""

import logging
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.mobile_time_clock.models import GeofenceZone
from modules.hr.mobile_time_clock.repositories import GeofenceZoneRepository
from modules.hr.mobile_time_clock.schemas import (
    GeofenceCheckRequest,
    GeofenceCheckResponse,
    GeofenceZoneCreate,
    GeofenceZoneUpdate,
)

logger = logging.getLogger(__name__)


class GeofenceService:
    """Service para validação e gerenciamento de geofences."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = GeofenceZoneRepository(db)

    async def check_location(
        self,
        request: GeofenceCheckRequest,
        employee_id: str = None,
    ) -> GeofenceCheckResponse:
        """Verifica se localização está dentro de zona permitida."""
        zones = await self.repository.find_zones_for_location(
            condominio_id=request.condominio_id,
            latitude=request.latitude,
            longitude=request.longitude,
            employee_id=employee_id,
            max_distance_km=10,
        )

        if not zones:
            return GeofenceCheckResponse(
                inside_zone=False,
                zone_id=None,
                zone_name=None,
                distance_meters=None,
                is_time_allowed=False,
                message="Nenhuma zona encontrada na região",
            )

        # Verificar cada zona
        for zone, distance, is_inside in zones:
            if is_inside:
                # Verificar horário
                now = datetime.now()
                time_allowed = zone.is_time_allowed(now.time(), now.weekday())

                return GeofenceCheckResponse(
                    inside_zone=True,
                    zone_id=zone.id,
                    zone_name=zone.name,
                    distance_meters=distance,
                    is_time_allowed=time_allowed,
                    accuracy_required=zone.min_accuracy_meters,
                    wifi_required=zone.require_wifi,
                    beacon_required=zone.require_beacon,
                    message="Localização válida" if time_allowed else "Fora do horário permitido",
                )

        # Nenhuma zona contém o ponto
        nearest_zone, nearest_distance, _ = zones[0]
        return GeofenceCheckResponse(
            inside_zone=False,
            zone_id=nearest_zone.id,
            zone_name=nearest_zone.name,
            distance_meters=nearest_distance,
            is_time_allowed=False,
            message=f"Fora da zona. Distância: {nearest_distance:.0f}m",
        )

    async def validate_checkin_location(  # pylint: disable=too-many-branches
        self,
        condominio_id: UUID,
        latitude: float,
        longitude: float,
        accuracy_meters: float,
        employee_id: str = None,
        wifi_ssid: str = None,
        beacon_uuid: str = None,
    ) -> Tuple[bool, Optional[GeofenceZone], dict]:
        """Valida localização para check-in.

        Retorna:
            - is_valid: bool
            - zone: GeofenceZone ou None
            - details: dict com detalhes da validação
        """
        details = {
            "location_valid": False,
            "accuracy_valid": False,
            "time_valid": False,
            "wifi_valid": True,
            "beacon_valid": True,
            "errors": [],
        }

        # Buscar zona
        zone = await self.repository.find_containing_zone(
            condominio_id=condominio_id,
            latitude=latitude,
            longitude=longitude,
            employee_id=employee_id,
        )

        if not zone:
            details["errors"].append("Localização fora de qualquer zona permitida")
            return False, None, details

        details["location_valid"] = True
        distance = zone.calculate_distance(latitude, longitude)
        details["distance_meters"] = distance

        # Verificar precisão
        if accuracy_meters <= zone.min_accuracy_meters:
            details["accuracy_valid"] = True
        else:
            details["errors"].append(
                f"Precisão insuficiente: {accuracy_meters:.0f}m "
                f"(requerido: {zone.min_accuracy_meters}m)"
            )

        # Verificar horário
        now = datetime.now()
        if zone.is_time_allowed(now.time(), now.weekday()):
            details["time_valid"] = True
        else:
            details["errors"].append("Fora do horário permitido para esta zona")

        # Verificar WiFi
        if zone.require_wifi:
            if wifi_ssid and zone.allowed_wifi_ssids:
                if wifi_ssid in zone.allowed_wifi_ssids:
                    details["wifi_valid"] = True
                else:
                    details["wifi_valid"] = False
                    details["errors"].append(f"WiFi '{wifi_ssid}' não autorizado")
            else:
                details["wifi_valid"] = False
                details["errors"].append("WiFi requerido mas não detectado")

        # Verificar Beacon
        if zone.require_beacon:
            if beacon_uuid and zone.allowed_beacons:
                if beacon_uuid in zone.allowed_beacons:
                    details["beacon_valid"] = True
                else:
                    details["beacon_valid"] = False
                    details["errors"].append("Beacon não reconhecido")
            else:
                details["beacon_valid"] = False
                details["errors"].append("Beacon requerido mas não detectado")

        is_valid = all([
            details["location_valid"],
            details["accuracy_valid"],
            details["time_valid"],
            details["wifi_valid"],
            details["beacon_valid"],
        ])

        return is_valid, zone, details

    async def get_zones_for_employee(
        self,
        condominio_id: UUID,
        employee_id: str,
        latitude: float = None,
        longitude: float = None,
    ) -> List[dict]:
        """Retorna zonas disponíveis para o funcionário."""
        zones = await self.repository.get_by_condominio(condominio_id, active_only=True)

        result = []
        for zone in zones:
            if not zone.is_employee_allowed(employee_id):
                continue

            zone_data = {
                "id": str(zone.id),
                "name": zone.name,
                "category": zone.category,
                "zone_type": zone.zone_type,
                "center_latitude": zone.center_latitude,
                "center_longitude": zone.center_longitude,
                "radius_meters": zone.radius_meters,
                "polygon_coordinates": zone.polygon_coordinates,
                "is_primary": zone.is_primary,
                "priority": zone.priority,
                "allow_all_hours": zone.allow_all_hours,
                "allowed_start_time": (
                    str(zone.allowed_start_time) if zone.allowed_start_time else None
                ),
                "allowed_end_time": (
                    str(zone.allowed_end_time) if zone.allowed_end_time else None
                ),
                "allowed_days": zone.allowed_days,
            }

            if latitude and longitude:
                zone_data["distance_meters"] = zone.calculate_distance(latitude, longitude)
                zone_data["is_inside"] = zone.contains_point(latitude, longitude)

            result.append(zone_data)

        # Ordenar por distância se localização fornecida
        if latitude and longitude:
            result.sort(key=lambda x: x.get("distance_meters", float("inf")))

        return result

    async def create_zone(
        self,
        data: GeofenceZoneCreate,
        condominio_id: UUID,
        created_by: UUID = None,
    ) -> GeofenceZone:
        """Cria nova zona de geofencing."""
        zone = await self.repository.create(data, condominio_id, created_by)
        logger.info(f"Zona criada: {zone.id} - {zone.name}")
        return zone

    async def update_zone(
        self,
        zone_id: UUID,
        data: GeofenceZoneUpdate,
    ) -> Optional[GeofenceZone]:
        """Atualiza zona existente."""
        zone = await self.repository.update(zone_id, data)
        if zone:
            logger.info(f"Zona atualizada: {zone.id}")
        return zone

    async def set_primary_zone(
        self,
        zone_id: UUID,
        condominio_id: UUID,
    ) -> None:
        """Define zona como primária."""
        await self.repository.set_primary(zone_id, condominio_id)
        logger.info(f"Zona {zone_id} definida como primária")

    async def deactivate_zone(self, zone_id: UUID) -> bool:
        """Desativa zona (soft delete)."""
        result = await self.repository.soft_delete(zone_id)
        if result:
            logger.info(f"Zona desativada: {zone_id}")
        return result

    async def get_zone_statistics(
        self,
        condominio_id: UUID = None,
    ) -> dict:
        """Obtém estatísticas das zonas."""
        return await self.repository.get_statistics(condominio_id)

    async def record_checkin_in_zone(self, zone_id: UUID) -> None:
        """Registra check-in na zona (para estatísticas)."""
        await self.repository.increment_checkin_count(zone_id)
