"""Testes para models do módulo Mobile Time Clock."""

from datetime import datetime, time, timedelta
from uuid import uuid4

import pytest

from modules.hr.mobile_time_clock.models import (
    BiometricCapability,
    CheckInStatus,
    CheckInType,
    DevicePlatform,
    DeviceStatus,
    GeofenceZone,
    LocationAccuracy,
    MobileCheckIn,
    MobileDevice,
    OfflineQueue,
    QueuePriority,
    QueueStatus,
    ValidationMethod,
    ZoneCategory,
    ZoneStatus,
    ZoneType,
)


class TestMobileDevice:
    """Testes para o model MobileDevice."""

    def test_create_device(self):
        """Testa criação de dispositivo."""
        device = MobileDevice(
            id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            device_name="iPhone 15",
            device_uuid="uuid-test-123",
            platform=DevicePlatform.IOS.value,
            os_version="17.0",
            app_version="1.0.0",
            status=DeviceStatus.PENDING.value,
        )

        assert device.device_name == "iPhone 15"
        assert device.platform == "ios"
        assert device.status == "pending"
        assert device.is_active is True
        assert device.trust_score == 0

    def test_device_is_authorized(self):
        """Testa verificação de autorização."""
        device = MobileDevice(
            id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            device_name="Test",
            device_uuid="test-uuid",
            platform=DevicePlatform.ANDROID.value,
            status=DeviceStatus.ACTIVE.value,
            is_active=True,
        )

        assert device.is_authorized is True

        device.status = DeviceStatus.BLOCKED.value
        assert device.is_authorized is False

        device.status = DeviceStatus.ACTIVE.value
        device.is_active = False
        assert device.is_authorized is False

    def test_device_can_checkin(self):
        """Testa se dispositivo pode fazer check-in."""
        device = MobileDevice(
            id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            device_name="Test",
            device_uuid="test-uuid",
            platform=DevicePlatform.ANDROID.value,
            status=DeviceStatus.ACTIVE.value,
            is_active=True,
            biometric_enabled=False,
        )

        assert device.can_checkin is True

        # Requer biometria mas não está enrolled
        device.biometric_enabled = True
        device.biometric_enrolled_at = None
        assert device.can_checkin is False

        device.biometric_enrolled_at = datetime.utcnow()
        assert device.can_checkin is True

    def test_device_needs_biometric(self):
        """Testa verificação de necessidade de biometria."""
        device = MobileDevice(
            id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            device_name="Test",
            device_uuid="test-uuid",
            platform=DevicePlatform.ANDROID.value,
            biometric_enabled=True,
            biometric_enrolled_at=datetime.utcnow(),
        )

        assert device.needs_biometric is False

        device.biometric_enrolled_at = None
        assert device.needs_biometric is True


class TestMobileCheckIn:
    """Testes para o model MobileCheckIn."""

    def test_create_checkin(self):
        """Testa criação de check-in."""
        now = datetime.utcnow()
        checkin = MobileCheckIn(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            checkin_type=CheckInType.ENTRY.value,
            checkin_datetime=now,
            checkin_date=now.date(),
            checkin_time=now.time(),
            device_timestamp=now,
            server_timestamp=now,
        )

        assert checkin.checkin_type == "entry"
        assert checkin.status == "pending"
        assert checkin.is_valid is False

    def test_checkin_is_validated(self):
        """Testa verificação se check-in está validado."""
        checkin = MobileCheckIn(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            checkin_type=CheckInType.ENTRY.value,
            checkin_datetime=datetime.utcnow(),
            checkin_date=datetime.utcnow().date(),
            checkin_time=datetime.utcnow().time(),
            device_timestamp=datetime.utcnow(),
            server_timestamp=datetime.utcnow(),
            status=CheckInStatus.VALIDATED.value,
            is_valid=True,
        )

        assert checkin.is_validated is True

        checkin.status = CheckInStatus.FLAGGED.value
        assert checkin.is_validated is False

    def test_checkin_needs_review(self):
        """Testa verificação se check-in precisa de revisão."""
        checkin = MobileCheckIn(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            checkin_type=CheckInType.ENTRY.value,
            checkin_datetime=datetime.utcnow(),
            checkin_date=datetime.utcnow().date(),
            checkin_time=datetime.utcnow().time(),
            device_timestamp=datetime.utcnow(),
            server_timestamp=datetime.utcnow(),
            status=CheckInStatus.FLAGGED.value,
        )

        assert checkin.needs_review is True

        checkin.status = CheckInStatus.APPROVED.value
        assert checkin.needs_review is False

    def test_calculate_accuracy_level(self):
        """Testa cálculo de nível de precisão."""
        checkin = MobileCheckIn(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            checkin_type=CheckInType.ENTRY.value,
            checkin_datetime=datetime.utcnow(),
            checkin_date=datetime.utcnow().date(),
            checkin_time=datetime.utcnow().time(),
            device_timestamp=datetime.utcnow(),
            server_timestamp=datetime.utcnow(),
        )

        checkin.accuracy_meters = 5
        assert checkin.calculate_accuracy_level() == LocationAccuracy.HIGH.value

        checkin.accuracy_meters = 30
        assert checkin.calculate_accuracy_level() == LocationAccuracy.MEDIUM.value

        checkin.accuracy_meters = 80
        assert checkin.calculate_accuracy_level() == LocationAccuracy.LOW.value

        checkin.accuracy_meters = 150
        assert checkin.calculate_accuracy_level() == LocationAccuracy.VERY_LOW.value

    def test_location_tuple(self):
        """Testa obtenção de tupla de localização."""
        checkin = MobileCheckIn(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            checkin_type=CheckInType.ENTRY.value,
            checkin_datetime=datetime.utcnow(),
            checkin_date=datetime.utcnow().date(),
            checkin_time=datetime.utcnow().time(),
            device_timestamp=datetime.utcnow(),
            server_timestamp=datetime.utcnow(),
            latitude=-23.5505,
            longitude=-46.6333,
        )

        assert checkin.location_tuple == (-23.5505, -46.6333)

        checkin.latitude = None
        assert checkin.location_tuple is None


class TestGeofenceZone:
    """Testes para o model GeofenceZone."""

    def test_create_zone(self):
        """Testa criação de zona."""
        zone = GeofenceZone(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Sede Principal",
            zone_type=ZoneType.CIRCLE.value,
            category=ZoneCategory.WORK.value,
            center_latitude=-23.5505,
            center_longitude=-46.6333,
            radius_meters=100,
        )

        assert zone.name == "Sede Principal"
        assert zone.zone_type == "circle"
        assert zone.radius_meters == 100
        assert zone.is_active is True

    def test_contains_point_circle(self):
        """Testa verificação de ponto dentro de zona circular."""
        zone = GeofenceZone(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Test Zone",
            zone_type=ZoneType.CIRCLE.value,
            center_latitude=-23.5505,
            center_longitude=-46.6333,
            radius_meters=100,
        )

        # Ponto no centro
        assert zone.contains_point(-23.5505, -46.6333) is True

        # Ponto próximo (dentro dos 100m)
        assert zone.contains_point(-23.5506, -46.6334) is True

        # Ponto distante
        assert zone.contains_point(-23.56, -46.64) is False

    def test_calculate_distance(self):
        """Testa cálculo de distância (Haversine)."""
        zone = GeofenceZone(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Test Zone",
            zone_type=ZoneType.CIRCLE.value,
            center_latitude=-23.5505,
            center_longitude=-46.6333,
            radius_meters=100,
        )

        # Distância para o mesmo ponto
        distance = zone.calculate_distance(-23.5505, -46.6333)
        assert distance < 1  # Menos de 1 metro

        # Distância para ponto conhecido (~1km)
        distance = zone.calculate_distance(-23.5595, -46.6333)
        assert 900 < distance < 1100

    def test_is_time_allowed(self):
        """Testa verificação de horário permitido."""
        zone = GeofenceZone(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Test Zone",
            zone_type=ZoneType.CIRCLE.value,
            center_latitude=-23.5505,
            center_longitude=-46.6333,
            radius_meters=100,
            allow_all_hours=True,
        )

        # Permite todas as horas
        assert zone.is_time_allowed(time(10, 0), 1) is True

        # Restringir horário
        zone.allow_all_hours = False
        zone.allowed_start_time = time(8, 0)
        zone.allowed_end_time = time(18, 0)
        zone.allowed_days = [0, 1, 2, 3, 4]  # Seg-Sex

        assert zone.is_time_allowed(time(10, 0), 1) is True  # Terça 10h
        assert zone.is_time_allowed(time(20, 0), 1) is False  # Terça 20h
        assert zone.is_time_allowed(time(10, 0), 5) is False  # Sábado 10h

    def test_is_employee_allowed(self):
        """Testa verificação de funcionário permitido."""
        zone = GeofenceZone(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Test Zone",
            zone_type=ZoneType.CIRCLE.value,
            center_latitude=-23.5505,
            center_longitude=-46.6333,
            radius_meters=100,
            allow_all_employees=True,
        )

        assert zone.is_employee_allowed("any-employee-id") is True

        zone.allow_all_employees = False
        zone.allowed_employees = ["emp-1", "emp-2"]

        assert zone.is_employee_allowed("emp-1") is True
        assert zone.is_employee_allowed("emp-3") is False


class TestOfflineQueue:
    """Testes para o model OfflineQueue."""

    def test_create_queue_item(self):
        """Testa criação de item na fila."""
        now = datetime.utcnow()
        item = OfflineQueue(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            offline_id="offline-123",
            checkin_data={"type": "entry"},
            checkin_type=CheckInType.ENTRY.value,
            device_timestamp=now,
            queued_at=now,
            received_at=now,
            expires_at=now + timedelta(hours=24),
        )

        assert item.offline_id == "offline-123"
        assert item.status == "pending"
        assert item.retry_count == 0

    def test_can_retry(self):
        """Testa verificação se pode fazer retry."""
        item = OfflineQueue(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            offline_id="offline-123",
            checkin_data={},
            checkin_type=CheckInType.ENTRY.value,
            device_timestamp=datetime.utcnow(),
            queued_at=datetime.utcnow(),
            received_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            max_retries=5,
            retry_count=3,
        )

        assert item.can_retry is True

        item.retry_count = 5
        assert item.can_retry is False

    def test_age_hours(self):
        """Testa cálculo de idade em horas."""
        item = OfflineQueue(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            offline_id="offline-123",
            checkin_data={},
            checkin_type=CheckInType.ENTRY.value,
            device_timestamp=datetime.utcnow(),
            queued_at=datetime.utcnow() - timedelta(hours=2),
            received_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )

        assert 1.9 < item.age_hours < 2.1

    def test_mark_processing(self):
        """Testa marcação como em processamento."""
        item = OfflineQueue(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            offline_id="offline-123",
            checkin_data={},
            checkin_type=CheckInType.ENTRY.value,
            device_timestamp=datetime.utcnow(),
            queued_at=datetime.utcnow(),
            received_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )

        item.mark_processing()
        assert item.status == QueueStatus.PROCESSING.value

    def test_mark_synced(self):
        """Testa marcação como sincronizado."""
        item = OfflineQueue(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            offline_id="offline-123",
            checkin_data={},
            checkin_type=CheckInType.ENTRY.value,
            device_timestamp=datetime.utcnow(),
            queued_at=datetime.utcnow(),
            received_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )

        checkin_id = uuid4()
        item.mark_synced(checkin_id)

        assert item.status == QueueStatus.SYNCED.value
        assert item.checkin_id == checkin_id
        assert item.synced_at is not None

    def test_mark_failed_with_retry(self):
        """Testa marcação como falho com retry."""
        item = OfflineQueue(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            offline_id="offline-123",
            checkin_data={},
            checkin_type=CheckInType.ENTRY.value,
            device_timestamp=datetime.utcnow(),
            queued_at=datetime.utcnow(),
            received_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            max_retries=5,
            retry_count=0,
        )

        item.mark_failed("Connection error", "CONN_ERROR")

        assert item.status == QueueStatus.FAILED.value
        assert item.retry_count == 1
        assert item.error_message == "Connection error"
        assert item.next_retry_at is not None

    def test_mark_expired(self):
        """Testa marcação como expirado."""
        item = OfflineQueue(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            offline_id="offline-123",
            checkin_data={},
            checkin_type=CheckInType.ENTRY.value,
            device_timestamp=datetime.utcnow(),
            queued_at=datetime.utcnow(),
            received_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )

        item.mark_expired()

        assert item.status == QueueStatus.EXPIRED.value
        assert item.is_expired is True


class TestEnums:
    """Testes para os Enums."""

    def test_device_platform_values(self):
        """Testa valores de DevicePlatform."""
        assert DevicePlatform.ANDROID.value == "android"
        assert DevicePlatform.IOS.value == "ios"
        assert DevicePlatform.WEB.value == "web"

    def test_device_status_values(self):
        """Testa valores de DeviceStatus."""
        assert DeviceStatus.PENDING.value == "pending"
        assert DeviceStatus.ACTIVE.value == "active"
        assert DeviceStatus.BLOCKED.value == "blocked"
        assert DeviceStatus.REVOKED.value == "revoked"
        assert DeviceStatus.LOST.value == "lost"

    def test_checkin_type_values(self):
        """Testa valores de CheckInType."""
        assert CheckInType.ENTRY.value == "entry"
        assert CheckInType.EXIT.value == "exit"
        assert CheckInType.BREAK_START.value == "break_start"
        assert CheckInType.BREAK_END.value == "break_end"

    def test_validation_method_values(self):
        """Testa valores de ValidationMethod."""
        assert ValidationMethod.GEOFENCE.value == "geofence"
        assert ValidationMethod.BIOMETRIC.value == "biometric"
        assert ValidationMethod.PHOTO.value == "photo"
        assert ValidationMethod.WIFI.value == "wifi"
        assert ValidationMethod.BEACON.value == "beacon"
        assert ValidationMethod.NFC.value == "nfc"
        assert ValidationMethod.QR_CODE.value == "qr_code"

    def test_queue_status_values(self):
        """Testa valores de QueueStatus."""
        assert QueueStatus.PENDING.value == "pending"
        assert QueueStatus.PROCESSING.value == "processing"
        assert QueueStatus.SYNCED.value == "synced"
        assert QueueStatus.FAILED.value == "failed"
        assert QueueStatus.EXPIRED.value == "expired"
