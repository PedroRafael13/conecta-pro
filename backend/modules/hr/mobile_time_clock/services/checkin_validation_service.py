"""Service para validação de check-ins mobile."""

import logging
from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.mobile_time_clock.models import (
    MobileCheckIn,
    MobileDevice,
    CheckInStatus,
    CheckInType,
    ValidationMethod,
    DeviceStatus,
)
from modules.hr.mobile_time_clock.repositories import (
    MobileCheckInRepository,
    MobileDeviceRepository,
    GeofenceZoneRepository,
)
from modules.hr.mobile_time_clock.schemas import (
    MobileCheckInCreate,
    CheckInValidationResult,
)
from modules.hr.mobile_time_clock.services.geofence_service import GeofenceService

logger = logging.getLogger(__name__)


class CheckInValidationService:
    """Service para validação completa de check-ins."""

    # Pesos para cálculo de score
    VALIDATION_WEIGHTS = {
        ValidationMethod.GEOFENCE.value: 30,
        ValidationMethod.BIOMETRIC.value: 25,
        ValidationMethod.PHOTO.value: 20,
        ValidationMethod.WIFI.value: 10,
        ValidationMethod.BEACON.value: 10,
        ValidationMethod.NFC.value: 15,
        ValidationMethod.QR_CODE.value: 10,
    }

    # Score mínimo para aprovação automática
    MIN_SCORE_AUTO_APPROVE = 60

    # Tolerância de drift de tempo (segundos)
    MAX_TIME_DRIFT = 300  # 5 minutos

    def __init__(self, db: AsyncSession):
        self.db = db
        self.checkin_repo = MobileCheckInRepository(db)
        self.device_repo = MobileDeviceRepository(db)
        self.geofence_repo = GeofenceZoneRepository(db)
        self.geofence_service = GeofenceService(db)

    async def validate_checkin(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        self,
        data: MobileCheckInCreate,
        device: MobileDevice,
        employee_id: UUID,
        condominio_id: UUID,
    ) -> CheckInValidationResult:
        """Valida check-in completo."""
        validation_methods = []
        errors = []
        warnings = []
        score = 0

        # 1. Validar dispositivo
        device_valid, device_error = self._validate_device(device)
        if not device_valid:
            errors.append(device_error)
            return CheckInValidationResult(
                is_valid=False,
                score=0,
                validation_methods=[],
                errors=errors,
                warnings=warnings,
            )

        # 2. Validar drift de tempo
        time_drift = abs((datetime.utcnow() - data.device_timestamp).total_seconds())
        if time_drift > self.MAX_TIME_DRIFT:
            warnings.append(
                f"Diferença de horário detectada: {time_drift:.0f}s"
            )

        # 3. Verificar duplicata
        is_duplicate = await self.checkin_repo.check_duplicate(
            employee_id=employee_id,
            checkin_type=data.checkin_type,
            device_timestamp=data.device_timestamp,
            tolerance_minutes=5,
        )
        if is_duplicate:
            errors.append("Check-in duplicado detectado")
            return CheckInValidationResult(
                is_valid=False,
                score=0,
                validation_methods=[],
                errors=errors,
                warnings=warnings,
            )

        # 4. Validar localização (geofence)
        geofence_zone = None
        if data.location:
            geo_valid, zone, geo_details = await self.geofence_service.validate_checkin_location(
                condominio_id=condominio_id,
                latitude=data.location.latitude,
                longitude=data.location.longitude,
                accuracy_meters=data.location.accuracy_meters or 100,
                employee_id=str(employee_id),
                wifi_ssid=data.validation.wifi_ssid if data.validation else None,
                beacon_uuid=data.validation.beacon_uuid if data.validation else None,
            )

            if geo_valid:
                geofence_zone = zone
                validation_methods.append(ValidationMethod.GEOFENCE.value)
                score += self.VALIDATION_WEIGHTS[ValidationMethod.GEOFENCE.value]
            else:
                for error in geo_details.get("errors", []):
                    warnings.append(error)

            # WiFi validation
            if geo_details.get("wifi_valid") and data.validation and data.validation.wifi_ssid:
                validation_methods.append(ValidationMethod.WIFI.value)
                score += self.VALIDATION_WEIGHTS[ValidationMethod.WIFI.value]

            # Beacon validation
            if geo_details.get("beacon_valid") and data.validation and data.validation.beacon_uuid:
                validation_methods.append(ValidationMethod.BEACON.value)
                score += self.VALIDATION_WEIGHTS[ValidationMethod.BEACON.value]
        else:
            errors.append("Localização não fornecida")

        # 5. Validar biometria
        if data.biometric and data.biometric.verified:
            if data.biometric.score >= 0.8:
                validation_methods.append(ValidationMethod.BIOMETRIC.value)
                score += self.VALIDATION_WEIGHTS[ValidationMethod.BIOMETRIC.value]
            else:
                warnings.append(
                    f"Score biométrico baixo: {data.biometric.score:.2f}"
                )

        # 6. Validar foto/selfie
        if data.photo and data.photo.captured:
            if data.photo.match_score and data.photo.match_score >= 0.75:
                validation_methods.append(ValidationMethod.PHOTO.value)
                score += self.VALIDATION_WEIGHTS[ValidationMethod.PHOTO.value]
            elif data.photo.match_score:
                warnings.append(
                    f"Match de foto baixo: {data.photo.match_score:.2f}"
                )
            else:
                # Foto capturada mas sem match score (revisão manual)
                validation_methods.append(ValidationMethod.PHOTO.value)
                score += self.VALIDATION_WEIGHTS[ValidationMethod.PHOTO.value] // 2

        # 7. Validar NFC
        if data.validation and data.validation.nfc_tag_id:
            validation_methods.append(ValidationMethod.NFC.value)
            score += self.VALIDATION_WEIGHTS[ValidationMethod.NFC.value]

        # 8. Validar QR Code
        if data.validation and data.validation.qr_code_data:
            # Verificar se QR code é válido
            if self._validate_qr_code(data.validation.qr_code_data):
                validation_methods.append(ValidationMethod.QR_CODE.value)
                score += self.VALIDATION_WEIGHTS[ValidationMethod.QR_CODE.value]
            else:
                warnings.append("QR Code inválido ou expirado")

        # 9. Determinar validade
        is_valid = score >= self.MIN_SCORE_AUTO_APPROVE and not errors

        # 10. Determinar status
        if is_valid:
            status = CheckInStatus.VALIDATED.value
        elif errors:
            status = CheckInStatus.REJECTED.value
        else:
            status = CheckInStatus.FLAGGED.value

        return CheckInValidationResult(
            is_valid=is_valid,
            score=min(score, 100),
            validation_methods=validation_methods,
            status=status,
            geofence_zone_id=geofence_zone.id if geofence_zone else None,
            geofence_zone_name=geofence_zone.name if geofence_zone else None,
            errors=errors,
            warnings=warnings,
            requires_review=status == CheckInStatus.FLAGGED.value,
        )

    def _validate_device(self, device: MobileDevice) -> Tuple[bool, Optional[str]]:
        """Valida se dispositivo pode fazer check-in."""
        if not device.is_active:
            return False, "Dispositivo inativo"

        if device.status != DeviceStatus.ACTIVE.value:
            return False, f"Dispositivo não autorizado: {device.status}"

        if not device.can_checkin:
            return False, "Dispositivo não pode realizar check-in"

        return True, None

    def _validate_qr_code(self, qr_data: str) -> bool:
        """Valida QR code."""
        # Formato esperado: CONECTA:ZONE:uuid:timestamp
        if not qr_data or not qr_data.startswith("CONECTA:"):
            return False

        parts = qr_data.split(":")
        if len(parts) < 4:
            return False

        try:
            # Verificar timestamp (válido por 5 minutos)
            timestamp = int(parts[3])
            now = int(datetime.utcnow().timestamp())
            if abs(now - timestamp) > 300:
                return False
            return True
        except (ValueError, IndexError):
            return False

    async def detect_anomalies(
        self,
        checkin: MobileCheckIn,
        employee_id: UUID,
    ) -> Tuple[bool, Optional[str], Optional[dict]]:
        """Detecta anomalias no check-in."""
        anomaly_type = None
        anomaly_details = {}

        # Buscar último check-in
        last_checkin = await self.checkin_repo.get_last_checkin(employee_id)

        if last_checkin:
            # 1. Verificar velocidade impossível
            if checkin.latitude and last_checkin.latitude:
                time_diff = (
                    checkin.checkin_datetime - last_checkin.checkin_datetime
                ).total_seconds()
                if time_diff > 0:
                    # Calcular distância aproximada
                    # pylint: disable=import-outside-toplevel
                    from modules.hr.mobile_time_clock.models import GeofenceZone
                    temp_zone = GeofenceZone(
                        center_latitude=last_checkin.latitude,
                        center_longitude=last_checkin.longitude,
                    )
                    distance = temp_zone.calculate_distance(
                        checkin.latitude,
                        checkin.longitude,
                    )

                    # Velocidade em km/h
                    speed_kmh = (distance / 1000) / (time_diff / 3600)

                    # Velocidade impossível (> 200 km/h)
                    if speed_kmh > 200:
                        anomaly_type = "impossible_speed"
                        anomaly_details = {
                            "speed_kmh": round(speed_kmh, 2),
                            "distance_m": round(distance, 2),
                            "time_diff_s": round(time_diff, 2),
                            "last_checkin_id": str(last_checkin.id),
                        }
                        return True, anomaly_type, anomaly_details

            # 2. Verificar sequência incorreta
            if last_checkin.checkin_type == checkin.checkin_type:
                if checkin.checkin_type in [CheckInType.ENTRY.value, CheckInType.BREAK_END.value]:
                    anomaly_type = "duplicate_entry"
                    anomaly_details = {
                        "last_checkin_type": last_checkin.checkin_type,
                        "last_checkin_time": last_checkin.checkin_datetime.isoformat(),
                    }
                    return True, anomaly_type, anomaly_details

            # 3. Verificar exit sem entry
            if checkin.checkin_type == CheckInType.EXIT.value:
                today_checkins = await self.checkin_repo.get_employee_today(employee_id)
                has_entry = any(c.checkin_type == CheckInType.ENTRY.value for c in today_checkins)
                if not has_entry:
                    anomaly_type = "exit_without_entry"
                    anomaly_details = {"checkins_today": len(today_checkins)}
                    return True, anomaly_type, anomaly_details

        # 4. Verificar horário suspeito
        hour = checkin.checkin_datetime.hour
        if hour < 4 or hour > 23:
            anomaly_type = "unusual_time"
            anomaly_details = {"hour": hour}
            return True, anomaly_type, anomaly_details

        return False, None, None

    async def process_checkin(
        self,
        data: MobileCheckInCreate,
        device: MobileDevice,
        employee_id: UUID,
        condominio_id: UUID,
    ) -> Tuple[MobileCheckIn, CheckInValidationResult]:
        """Processa check-in completo com validação."""
        # Validar
        validation = await self.validate_checkin(data, device, employee_id, condominio_id)

        # Criar check-in
        checkin = await self.checkin_repo.create(
            data=data,
            device_id=device.id,
            employee_id=employee_id,
            condominio_id=condominio_id,
        )

        # Atualizar com dados de geofence
        if validation.geofence_zone_id:
            zone = await self.geofence_repo.get_by_id(validation.geofence_zone_id)
            if zone:
                distance = zone.calculate_distance(
                    data.location.latitude,
                    data.location.longitude,
                ) if data.location else None

                await self.checkin_repo.update_geofence(
                    checkin_id=checkin.id,
                    geofence_id=validation.geofence_zone_id,
                    inside_geofence=True,
                    distance_from_center=distance or 0,
                )

        # Atualizar validação
        await self.checkin_repo.update_validation(
            checkin_id=checkin.id,
            status=validation.status,
            validation_methods=validation.validation_methods,
            validation_score=validation.score,
            is_valid=validation.is_valid,
        )

        # Detectar anomalias
        has_anomaly, anomaly_type, anomaly_details = await self.detect_anomalies(
            checkin,
            employee_id,
        )

        if has_anomaly:
            await self.checkin_repo.flag_for_review(
                checkin_id=checkin.id,
                anomaly_type=anomaly_type,
                anomaly_details=anomaly_details,
            )
            validation.requires_review = True
            validation.warnings.append(f"Anomalia detectada: {anomaly_type}")

        # Atualizar contadores
        await self.device_repo.increment_checkin_count(device.id)
        if validation.geofence_zone_id:
            await self.geofence_repo.increment_checkin_count(validation.geofence_zone_id)

        # Recarregar check-in
        checkin = await self.checkin_repo.get_by_id(checkin.id)

        logger.info(
            f"Check-in processado: {checkin.id} - "
            f"Score: {validation.score} - Valid: {validation.is_valid}"
        )

        return checkin, validation
