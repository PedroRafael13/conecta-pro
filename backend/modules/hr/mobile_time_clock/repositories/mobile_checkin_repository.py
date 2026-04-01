"""Repository para MobileCheckIn."""

from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.mobile_time_clock.models import (
    CheckInStatus,
    MobileCheckIn,
)
from modules.hr.mobile_time_clock.schemas import (
    MobileCheckInCreate,
    MobileCheckInFilter,
)


class MobileCheckInRepository:
    """Repository para operações com check-ins mobile."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: MobileCheckInCreate,
        device_id: UUID,
        employee_id: UUID,
        condominio_id: UUID,
    ) -> MobileCheckIn:
        """Cria novo check-in."""
        checkin = MobileCheckIn(
            device_id=device_id,
            employee_id=employee_id,
            condominio_id=condominio_id,
            checkin_type=data.checkin_type,
            checkin_datetime=data.device_timestamp,
            checkin_date=data.device_timestamp.date(),
            checkin_time=data.device_timestamp.time(),
            device_timestamp=data.device_timestamp,
            server_timestamp=datetime.utcnow(),
            time_drift_seconds=int((datetime.utcnow() - data.device_timestamp).total_seconds()),
            app_version=data.app_version,
            device_info=data.device_info or {},
        )

        # Localização
        if data.location:
            checkin.latitude = data.location.latitude
            checkin.longitude = data.location.longitude
            checkin.accuracy_meters = data.location.accuracy_meters
            checkin.altitude = data.location.altitude
            checkin.location_provider = data.location.provider
            checkin.location_accuracy = checkin.calculate_accuracy_level()

        # Biometria
        if data.biometric:
            checkin.biometric_verified = data.biometric.verified
            checkin.biometric_type = data.biometric.type
            checkin.biometric_score = data.biometric.score

        # Foto
        if data.photo:
            checkin.photo_captured = data.photo.captured
            checkin.photo_path = data.photo.path
            checkin.face_match_score = data.photo.match_score

        # Validação adicional
        if data.validation:
            checkin.wifi_ssid = data.validation.wifi_ssid
            checkin.wifi_bssid = data.validation.wifi_bssid
            checkin.beacon_uuid = data.validation.beacon_uuid
            checkin.nfc_tag_id = data.validation.nfc_tag_id
            checkin.qr_code_data = data.validation.qr_code_data

        self.db.add(checkin)
        await self.db.commit()
        await self.db.refresh(checkin)
        return checkin

    async def get_by_id(self, checkin_id: UUID) -> MobileCheckIn | None:
        """Busca check-in por ID."""
        result = await self.db.execute(select(MobileCheckIn).where(MobileCheckIn.id == checkin_id))
        return result.scalar_one_or_none()

    async def get_employee_today(
        self,
        employee_id: UUID,
        today: date = None,
    ) -> list[MobileCheckIn]:
        """Busca check-ins do funcionário hoje."""
        today = today or date.today()
        result = await self.db.execute(
            select(MobileCheckIn)
            .where(MobileCheckIn.employee_id == employee_id)
            .where(MobileCheckIn.checkin_date == today)
            .order_by(MobileCheckIn.checkin_time.asc())
        )
        return list(result.scalars().all())

    async def get_last_checkin(
        self,
        employee_id: UUID,
    ) -> MobileCheckIn | None:
        """Busca último check-in do funcionário."""
        result = await self.db.execute(
            select(MobileCheckIn)
            .where(MobileCheckIn.employee_id == employee_id)
            .order_by(MobileCheckIn.checkin_datetime.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_geofence(
        self,
        checkin_id: UUID,
        geofence_id: UUID,
        inside_geofence: bool,
        distance_from_center: float,
    ) -> None:
        """Atualiza dados de geofence."""
        await self.db.execute(
            update(MobileCheckIn)
            .where(MobileCheckIn.id == checkin_id)
            .values(
                geofence_id=geofence_id,
                inside_geofence=inside_geofence,
                distance_from_center=distance_from_center,
            )
        )
        await self.db.commit()

    async def update_validation(
        self,
        checkin_id: UUID,
        status: str,
        validation_methods: list[str],
        validation_score: int,
        is_valid: bool,
    ) -> None:
        """Atualiza validação."""
        await self.db.execute(
            update(MobileCheckIn)
            .where(MobileCheckIn.id == checkin_id)
            .values(
                status=status,
                validation_methods=validation_methods,
                validation_score=validation_score,
                is_valid=is_valid,
            )
        )
        await self.db.commit()

    async def mark_processed(
        self,
        checkin_id: UUID,
        time_entry_id: UUID,
    ) -> None:
        """Marca como processado."""
        await self.db.execute(
            update(MobileCheckIn)
            .where(MobileCheckIn.id == checkin_id)
            .values(
                status=CheckInStatus.PROCESSED.value,
                time_entry_id=time_entry_id,
                processed_at=datetime.utcnow(),
            )
        )
        await self.db.commit()

    async def flag_for_review(
        self,
        checkin_id: UUID,
        anomaly_type: str,
        anomaly_details: dict,
    ) -> None:
        """Marca para revisão."""
        await self.db.execute(
            update(MobileCheckIn)
            .where(MobileCheckIn.id == checkin_id)
            .values(
                status=CheckInStatus.FLAGGED.value,
                has_anomaly=True,
                anomaly_type=anomaly_type,
                anomaly_details=anomaly_details,
            )
        )
        await self.db.commit()

    async def review(
        self,
        checkin_id: UUID,
        reviewer_id: UUID,
        approved: bool,
        notes: str = None,
        rejection_reason: str = None,
    ) -> MobileCheckIn | None:
        """Revisa check-in."""
        checkin = await self.get_by_id(checkin_id)
        if not checkin:
            return None

        checkin.reviewed_by = reviewer_id
        checkin.reviewed_at = datetime.utcnow()
        checkin.review_notes = notes

        if approved:
            checkin.status = CheckInStatus.APPROVED.value
        else:
            checkin.status = CheckInStatus.REJECTED.value
            checkin.rejection_reason = rejection_reason
            checkin.is_valid = False

        await self.db.commit()
        await self.db.refresh(checkin)
        return checkin

    async def list_checkins(
        self,
        filters: MobileCheckInFilter,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[MobileCheckIn], int]:
        """Lista check-ins com filtros."""
        query = select(MobileCheckIn)

        if filters.device_id:
            query = query.where(MobileCheckIn.device_id == filters.device_id)
        if filters.employee_id:
            query = query.where(MobileCheckIn.employee_id == filters.employee_id)
        if filters.condominio_id:
            query = query.where(MobileCheckIn.condominio_id == filters.condominio_id)
        if filters.geofence_id:
            query = query.where(MobileCheckIn.geofence_id == filters.geofence_id)
        if filters.checkin_type:
            query = query.where(MobileCheckIn.checkin_type == filters.checkin_type)
        if filters.status:
            query = query.where(MobileCheckIn.status == filters.status)
        if filters.date_from:
            query = query.where(MobileCheckIn.checkin_date >= filters.date_from)
        if filters.date_to:
            query = query.where(MobileCheckIn.checkin_date <= filters.date_to)
        if filters.inside_geofence is not None:
            query = query.where(MobileCheckIn.inside_geofence == filters.inside_geofence)
        if filters.is_offline is not None:
            query = query.where(MobileCheckIn.is_offline == filters.is_offline)
        if filters.has_anomaly is not None:
            query = query.where(MobileCheckIn.has_anomaly == filters.has_anomaly)
        if filters.needs_review:
            query = query.where(MobileCheckIn.status == CheckInStatus.FLAGGED.value)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        query = query.order_by(MobileCheckIn.checkin_datetime.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_pending_review(
        self,
        condominio_id: UUID,
    ) -> list[MobileCheckIn]:
        """Lista check-ins pendentes de revisão."""
        result = await self.db.execute(
            select(MobileCheckIn)
            .where(MobileCheckIn.condominio_id == condominio_id)
            .where(MobileCheckIn.status == CheckInStatus.FLAGGED.value)
            .order_by(MobileCheckIn.checkin_datetime.asc())
        )
        return list(result.scalars().all())

    async def get_statistics(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID = None,
        date_from: date = None,
        date_to: date = None,
    ) -> dict:
        """Obtém estatísticas de check-ins."""
        query = select(MobileCheckIn)

        if condominio_id:
            query = query.where(MobileCheckIn.condominio_id == condominio_id)
        if date_from:
            query = query.where(MobileCheckIn.checkin_date >= date_from)
        if date_to:
            query = query.where(MobileCheckIn.checkin_date <= date_to)

        result = await self.db.execute(query)
        checkins = list(result.scalars().all())

        today = date.today()
        by_type = {}
        by_status = {}
        validation_scores = []
        geofence_inside = 0
        biometric_used = 0

        for checkin in checkins:
            by_type[checkin.checkin_type] = by_type.get(checkin.checkin_type, 0) + 1
            by_status[checkin.status] = by_status.get(checkin.status, 0) + 1
            validation_scores.append(checkin.validation_score)
            if checkin.inside_geofence:
                geofence_inside += 1
            if checkin.biometric_verified:
                biometric_used += 1

        today_count = sum(1 for c in checkins if c.checkin_date == today)
        offline_count = sum(1 for c in checkins if c.is_offline)
        anomaly_count = sum(1 for c in checkins if c.has_anomaly)

        return {
            "total_checkins": len(checkins),
            "today_checkins": today_count,
            "pending_review": by_status.get(CheckInStatus.FLAGGED.value, 0),
            "offline_checkins": offline_count,
            "anomalies_detected": anomaly_count,
            "by_type": by_type,
            "by_status": by_status,
            "avg_validation_score": (sum(validation_scores) / len(validation_scores) if validation_scores else 0),
            "geofence_compliance": (geofence_inside / len(checkins) * 100 if checkins else 0),
            "biometric_usage": (biometric_used / len(checkins) * 100 if checkins else 0),
        }

    async def check_duplicate(
        self,
        employee_id: UUID,
        checkin_type: str,
        device_timestamp: datetime,
        tolerance_minutes: int = 5,
    ) -> bool:
        """Verifica se existe check-in duplicado."""
        min_time = device_timestamp - timedelta(minutes=tolerance_minutes)
        max_time = device_timestamp + timedelta(minutes=tolerance_minutes)

        result = await self.db.execute(
            select(MobileCheckIn)
            .where(MobileCheckIn.employee_id == employee_id)
            .where(MobileCheckIn.checkin_type == checkin_type)
            .where(MobileCheckIn.device_timestamp >= min_time)
            .where(MobileCheckIn.device_timestamp <= max_time)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None
