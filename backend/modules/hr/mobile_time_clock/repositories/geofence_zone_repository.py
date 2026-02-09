"""Repository para GeofenceZone."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.mobile_time_clock.models import (
    GeofenceZone,
    ZoneStatus,
)
from modules.hr.mobile_time_clock.schemas import (
    GeofenceZoneCreate,
    GeofenceZoneFilter,
    GeofenceZoneUpdate,
)


class GeofenceZoneRepository:
    """Repository para operações com zonas de geofencing."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: GeofenceZoneCreate,
        condominio_id: UUID,
        created_by: UUID = None,
    ) -> GeofenceZone:
        """Cria nova zona."""
        zone = GeofenceZone(
            condominio_id=condominio_id,
            post_id=data.post_id,
            name=data.name,
            description=data.description,
            zone_type=data.zone_type,
            category=data.category,
            center_latitude=data.center_latitude,
            center_longitude=data.center_longitude,
            radius_meters=data.radius_meters,
            polygon_coordinates=(
                [c.model_dump() for c in data.polygon_coordinates] if data.polygon_coordinates else None
            ),
            address=data.address,
            city=data.city,
            state=data.state,
            postal_code=data.postal_code,
            min_accuracy_meters=data.min_accuracy_meters,
            require_wifi=data.require_wifi,
            allowed_wifi_ssids=data.allowed_wifi_ssids,
            require_beacon=data.require_beacon,
            allowed_beacons=data.allowed_beacons,
            allow_all_hours=data.allow_all_hours,
            allowed_start_time=data.allowed_start_time,
            allowed_end_time=data.allowed_end_time,
            allowed_days=data.allowed_days,
            entry_tolerance_minutes=data.entry_tolerance_minutes,
            exit_tolerance_minutes=data.exit_tolerance_minutes,
            grace_period_meters=data.grace_period_meters,
            allow_all_employees=data.allow_all_employees,
            allowed_employees=([str(e) for e in data.allowed_employees] if data.allowed_employees else None),
            allowed_departments=([str(d) for d in data.allowed_departments] if data.allowed_departments else None),
            is_primary=data.is_primary,
            priority=data.priority,
            created_by=created_by,
        )

        self.db.add(zone)
        await self.db.commit()
        await self.db.refresh(zone)
        return zone

    async def get_by_id(self, zone_id: UUID) -> GeofenceZone | None:
        """Busca zona por ID."""
        result = await self.db.execute(select(GeofenceZone).where(GeofenceZone.id == zone_id))
        return result.scalar_one_or_none()

    async def get_by_condominio(
        self,
        condominio_id: UUID,
        active_only: bool = True,
    ) -> list[GeofenceZone]:
        """Busca zonas do condomínio."""
        query = select(GeofenceZone).where(GeofenceZone.condominio_id == condominio_id)

        if active_only:
            query = query.where(GeofenceZone.is_active.is_(True))
            query = query.where(GeofenceZone.status == ZoneStatus.ACTIVE.value)

        result = await self.db.execute(query.order_by(GeofenceZone.priority.desc(), GeofenceZone.name))
        return list(result.scalars().all())

    async def get_by_post(
        self,
        post_id: UUID,
    ) -> list[GeofenceZone]:
        """Busca zonas do posto."""
        result = await self.db.execute(
            select(GeofenceZone)
            .where(GeofenceZone.post_id == post_id)
            .where(GeofenceZone.is_active.is_(True))
            .order_by(GeofenceZone.priority.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        zone_id: UUID,
        data: GeofenceZoneUpdate,
    ) -> GeofenceZone | None:
        """Atualiza zona."""
        zone = await self.get_by_id(zone_id)
        if not zone:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Converter coordenadas
        if "polygon_coordinates" in update_data and update_data["polygon_coordinates"]:
            update_data["polygon_coordinates"] = [
                c.model_dump() if hasattr(c, "model_dump") else c for c in update_data["polygon_coordinates"]
            ]

        for key, value in update_data.items():
            setattr(zone, key, value)

        zone.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(zone)
        return zone

    async def find_zones_for_location(
        self,
        condominio_id: UUID,
        latitude: float,
        longitude: float,
        employee_id: str = None,
        max_distance_km: float = 10,
    ) -> list[tuple[GeofenceZone, float, bool]]:
        """Encontra zonas próximas à localização.

        Retorna lista de (zona, distância, está_dentro).
        """
        zones = await self.get_by_condominio(condominio_id, active_only=True)
        results = []

        for zone in zones:
            distance = zone.calculate_distance(latitude, longitude)

            # Ignorar zonas muito distantes
            if distance > max_distance_km * 1000:
                continue

            is_inside = zone.contains_point(latitude, longitude)

            # Verificar se funcionário é permitido
            if employee_id and not zone.is_employee_allowed(employee_id):
                continue

            results.append((zone, distance, is_inside))

        # Ordenar por distância
        results.sort(key=lambda x: x[1])
        return results

    async def find_containing_zone(
        self,
        condominio_id: UUID,
        latitude: float,
        longitude: float,
        employee_id: str = None,
    ) -> GeofenceZone | None:
        """Encontra zona que contém o ponto."""
        zones = await self.find_zones_for_location(
            condominio_id,
            latitude,
            longitude,
            employee_id,
        )

        for zone, _distance, is_inside in zones:
            if is_inside:
                return zone

        return None

    async def increment_checkin_count(
        self,
        zone_id: UUID,
    ) -> None:
        """Incrementa contador de check-ins."""
        await self.db.execute(
            update(GeofenceZone)
            .where(GeofenceZone.id == zone_id)
            .values(
                total_checkins=GeofenceZone.total_checkins + 1,
                last_checkin_at=datetime.utcnow(),
            )
        )
        await self.db.commit()

    async def set_primary(
        self,
        zone_id: UUID,
        condominio_id: UUID,
    ) -> None:
        """Define zona como primária (remove de outras)."""
        # Remove primary de outras
        await self.db.execute(
            update(GeofenceZone)
            .where(GeofenceZone.condominio_id == condominio_id)
            .where(GeofenceZone.id != zone_id)
            .values(is_primary=False)
        )

        # Define como primária
        await self.db.execute(update(GeofenceZone).where(GeofenceZone.id == zone_id).values(is_primary=True))

        await self.db.commit()

    async def list_zones(
        self,
        filters: GeofenceZoneFilter,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[GeofenceZone], int]:
        """Lista zonas com filtros."""
        query = select(GeofenceZone)

        if filters.condominio_id:
            query = query.where(GeofenceZone.condominio_id == filters.condominio_id)
        if filters.post_id:
            query = query.where(GeofenceZone.post_id == filters.post_id)
        if filters.category:
            query = query.where(GeofenceZone.category == filters.category)
        if filters.status:
            query = query.where(GeofenceZone.status == filters.status)
        if filters.is_primary is not None:
            query = query.where(GeofenceZone.is_primary == filters.is_primary)
        if filters.is_active is not None:
            query = query.where(GeofenceZone.is_active == filters.is_active)

        # Busca por proximidade
        if filters.near_latitude and filters.near_longitude:
            # Filtro básico por bounding box (aproximação)
            lat_range = (filters.max_distance_km or 10) / 111  # ~111km por grau
            lng_range = lat_range / 0.7  # Aproximação para longitude

            query = query.where(
                GeofenceZone.center_latitude.between(
                    filters.near_latitude - lat_range,
                    filters.near_latitude + lat_range,
                )
            )
            query = query.where(
                GeofenceZone.center_longitude.between(
                    filters.near_longitude - lng_range,
                    filters.near_longitude + lng_range,
                )
            )

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        query = query.order_by(GeofenceZone.priority.desc(), GeofenceZone.name)
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_statistics(
        self,
        condominio_id: UUID = None,
    ) -> dict:
        """Obtém estatísticas de zonas."""
        query = select(GeofenceZone)
        if condominio_id:
            query = query.where(GeofenceZone.condominio_id == condominio_id)

        result = await self.db.execute(query)
        zones = list(result.scalars().all())

        by_category = {}
        by_status = {}
        total_checkins = 0
        radii = []
        most_used = []

        for zone in zones:
            by_category[zone.category] = by_category.get(zone.category, 0) + 1
            by_status[zone.status] = by_status.get(zone.status, 0) + 1
            total_checkins += zone.total_checkins
            radii.append(zone.radius_meters)
            most_used.append(
                {
                    "id": str(zone.id),
                    "name": zone.name,
                    "checkins": zone.total_checkins,
                }
            )

        # Top 5 mais usadas
        most_used.sort(key=lambda x: x["checkins"], reverse=True)
        most_used = most_used[:5]

        return {
            "total_zones": len(zones),
            "active_zones": by_status.get(ZoneStatus.ACTIVE.value, 0),
            "by_category": by_category,
            "by_status": by_status,
            "total_checkins": total_checkins,
            "most_used_zones": most_used,
            "avg_radius_meters": sum(radii) / len(radii) if radii else 0,
        }

    async def delete(self, zone_id: UUID) -> bool:
        """Remove zona."""
        zone = await self.get_by_id(zone_id)
        if not zone:
            return False

        await self.db.delete(zone)
        await self.db.commit()
        return True

    async def soft_delete(self, zone_id: UUID) -> bool:
        """Desativa zona (soft delete)."""
        zone = await self.get_by_id(zone_id)
        if not zone:
            return False

        zone.is_active = False
        zone.status = ZoneStatus.INACTIVE.value
        await self.db.commit()
        return True
