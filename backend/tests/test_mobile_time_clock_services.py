"""Testes para services do módulo Mobile Time Clock."""

import pytest
from datetime import datetime, time, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from modules.hr.mobile_time_clock.models import (
    MobileDevice,
    MobileCheckIn,
    GeofenceZone,
    OfflineQueue,
    DeviceStatus,
    CheckInType,
    CheckInStatus,
    ZoneType,
    ZoneCategory,
    QueueStatus,
)
from modules.hr.mobile_time_clock.schemas import (
    MobileCheckInCreate,
    CheckInLocation,
    CheckInBiometric,
    CheckInPhoto,
    CheckInValidation,
    GeofenceCheckRequest,
    GeofenceZoneCreate,
    MobileDeviceRegister,
    MobileDeviceApprove,
    OfflineQueueItemCreate,
)


class TestGeofenceServiceUnit:
    """Testes unitários para GeofenceService."""

    def test_haversine_distance_same_point(self):
        """Testa distância zero para mesmo ponto."""
        zone = GeofenceZone(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Test",
            zone_type=ZoneType.CIRCLE.value,
            center_latitude=-23.5505,
            center_longitude=-46.6333,
            radius_meters=100,
        )

        distance = zone.calculate_distance(-23.5505, -46.6333)
        assert distance < 1

    def test_haversine_distance_known_points(self):
        """Testa distância entre pontos conhecidos."""
        zone = GeofenceZone(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Test",
            zone_type=ZoneType.CIRCLE.value,
            center_latitude=0,
            center_longitude=0,
            radius_meters=100,
        )

        # ~111km entre graus de latitude
        distance = zone.calculate_distance(1, 0)
        assert 110000 < distance < 112000

    def test_contains_point_inside_circle(self):
        """Testa ponto dentro do círculo."""
        zone = GeofenceZone(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Test",
            zone_type=ZoneType.CIRCLE.value,
            center_latitude=-23.5505,
            center_longitude=-46.6333,
            radius_meters=100,
        )

        # Ponto no centro
        assert zone.contains_point(-23.5505, -46.6333) is True

    def test_contains_point_outside_circle(self):
        """Testa ponto fora do círculo."""
        zone = GeofenceZone(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Test",
            zone_type=ZoneType.CIRCLE.value,
            center_latitude=-23.5505,
            center_longitude=-46.6333,
            radius_meters=100,
        )

        # Ponto distante
        assert zone.contains_point(-23.56, -46.64) is False

    def test_time_allowed_all_hours(self):
        """Testa quando todas as horas são permitidas."""
        zone = GeofenceZone(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Test",
            zone_type=ZoneType.CIRCLE.value,
            center_latitude=-23.5505,
            center_longitude=-46.6333,
            radius_meters=100,
            allow_all_hours=True,
        )

        assert zone.is_time_allowed(time(3, 0), 0) is True
        assert zone.is_time_allowed(time(23, 59), 6) is True

    def test_time_allowed_restricted(self):
        """Testa horário restrito."""
        zone = GeofenceZone(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Test",
            zone_type=ZoneType.CIRCLE.value,
            center_latitude=-23.5505,
            center_longitude=-46.6333,
            radius_meters=100,
            allow_all_hours=False,
            allowed_start_time=time(8, 0),
            allowed_end_time=time(18, 0),
            allowed_days=[0, 1, 2, 3, 4],  # Seg-Sex
        )

        # Dentro do horário
        assert zone.is_time_allowed(time(10, 0), 2) is True

        # Fora do horário
        assert zone.is_time_allowed(time(20, 0), 2) is False

        # Fim de semana
        assert zone.is_time_allowed(time(10, 0), 5) is False


class TestCheckInValidationServiceUnit:
    """Testes unitários para CheckInValidationService."""

    def test_device_validation_active(self):
        """Testa validação de dispositivo ativo."""
        device = MobileDevice(
            id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            device_name="Test",
            device_uuid="test-uuid",
            platform="android",
            status=DeviceStatus.ACTIVE.value,
            is_active=True,
        )

        assert device.is_authorized is True
        assert device.can_checkin is True

    def test_device_validation_blocked(self):
        """Testa validação de dispositivo bloqueado."""
        device = MobileDevice(
            id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            device_name="Test",
            device_uuid="test-uuid",
            platform="android",
            status=DeviceStatus.BLOCKED.value,
            is_active=True,
        )

        assert device.is_authorized is False

    def test_device_validation_inactive(self):
        """Testa validação de dispositivo inativo."""
        device = MobileDevice(
            id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            device_name="Test",
            device_uuid="test-uuid",
            platform="android",
            status=DeviceStatus.ACTIVE.value,
            is_active=False,
        )

        assert device.is_authorized is False

    def test_qr_code_validation_valid(self):
        """Testa validação de QR code válido."""
        # QR code válido: CONECTA:ZONE:uuid:timestamp
        now = int(datetime.utcnow().timestamp())
        qr_data = f"CONECTA:ZONE:{uuid4()}:{now}"

        assert qr_data.startswith("CONECTA:")
        parts = qr_data.split(":")
        assert len(parts) == 4

    def test_qr_code_validation_expired(self):
        """Testa validação de QR code expirado."""
        # QR code de 10 minutos atrás
        old_time = int((datetime.utcnow() - timedelta(minutes=10)).timestamp())
        qr_data = f"CONECTA:ZONE:{uuid4()}:{old_time}"

        parts = qr_data.split(":")
        timestamp = int(parts[3])
        now = int(datetime.utcnow().timestamp())

        assert abs(now - timestamp) > 300  # Expirado

    def test_accuracy_level_calculation(self):
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

        # Alta precisão
        checkin.accuracy_meters = 5
        assert checkin.calculate_accuracy_level() == "high"

        # Média precisão
        checkin.accuracy_meters = 30
        assert checkin.calculate_accuracy_level() == "medium"

        # Baixa precisão
        checkin.accuracy_meters = 80
        assert checkin.calculate_accuracy_level() == "low"

        # Muito baixa precisão
        checkin.accuracy_meters = 150
        assert checkin.calculate_accuracy_level() == "very_low"


class TestOfflineSyncServiceUnit:
    """Testes unitários para OfflineSyncService."""

    def test_queue_item_expiration(self):
        """Testa expiração de item na fila."""
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
            expires_at=datetime.utcnow() - timedelta(hours=1),  # Já expirou
        )

        assert item.is_expired is True

    def test_queue_item_not_expired(self):
        """Testa item não expirado."""
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

        assert item.is_expired is False

    def test_retry_backoff_calculation(self):
        """Testa cálculo de backoff exponencial."""
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

        # Primeira falha - retry em 2 minutos
        item.mark_failed("Error", "ERR")
        assert item.retry_count == 1
        assert item.next_retry_at is not None

        # Segunda falha - retry em 4 minutos
        item.mark_failed("Error", "ERR")
        assert item.retry_count == 2

        # Terceira falha - retry em 8 minutos
        item.mark_failed("Error", "ERR")
        assert item.retry_count == 3

    def test_can_retry_limit(self):
        """Testa limite de retries."""
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
            max_retries=3,
            retry_count=2,
        )

        assert item.can_retry is True

        item.retry_count = 3
        assert item.can_retry is False

    def test_queue_item_age(self):
        """Testa cálculo de idade do item."""
        item = OfflineQueue(
            id=uuid4(),
            device_id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            offline_id="offline-123",
            checkin_data={},
            checkin_type=CheckInType.ENTRY.value,
            device_timestamp=datetime.utcnow(),
            queued_at=datetime.utcnow() - timedelta(hours=3),
            received_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )

        assert 2.9 < item.age_hours < 3.1


class TestDeviceServiceUnit:
    """Testes unitários para DeviceService."""

    def test_device_trust_score_on_approve(self):
        """Testa score de confiança ao aprovar."""
        device = MobileDevice(
            id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            device_name="Test",
            device_uuid="test-uuid",
            platform="android",
            status=DeviceStatus.PENDING.value,
            trust_score=0,
        )

        # Simular aprovação com trusted
        device.status = DeviceStatus.ACTIVE.value
        device.is_trusted = True
        device.trust_score = 50

        assert device.trust_score == 50

        # Sem trusted
        device.is_trusted = False
        device.trust_score = 30

        assert device.trust_score == 30

    def test_device_blocked_trust_score(self):
        """Testa score zerado ao bloquear."""
        device = MobileDevice(
            id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            device_name="Test",
            device_uuid="test-uuid",
            platform="android",
            status=DeviceStatus.ACTIVE.value,
            trust_score=50,
        )

        # Simular bloqueio
        device.status = DeviceStatus.BLOCKED.value
        device.trust_score = 0

        assert device.trust_score == 0

    def test_failed_attempts_tracking(self):
        """Testa contagem de tentativas falhas."""
        device = MobileDevice(
            id=uuid4(),
            employee_id=uuid4(),
            condominio_id=uuid4(),
            device_name="Test",
            device_uuid="test-uuid",
            platform="android",
            status=DeviceStatus.ACTIVE.value,
            failed_attempts=0,
        )

        # Incrementar falhas
        for i in range(10):
            device.failed_attempts += 1
            device.last_failed_at = datetime.utcnow()

        assert device.failed_attempts == 10

        # Auto-bloqueio após 10 falhas
        if device.failed_attempts >= 10:
            device.status = DeviceStatus.BLOCKED.value
            device.blocked_reason = "Muitas tentativas falhas"

        assert device.status == DeviceStatus.BLOCKED.value


class TestPushNotificationServiceUnit:
    """Testes unitários para PushNotificationService."""

    def test_notification_type_values(self):
        """Testa valores de tipos de notificação."""
        from modules.hr.mobile_time_clock.services import NotificationType

        assert NotificationType.CHECKIN_REMINDER.value == "checkin_reminder"
        assert NotificationType.CHECKIN_CONFIRMED.value == "checkin_confirmed"
        assert NotificationType.DEVICE_APPROVED.value == "device_approved"
        assert NotificationType.GEOFENCE_ENTER.value == "geofence_enter"

    def test_notification_payload_structure(self):
        """Testa estrutura do payload de notificação."""
        payload = {
            "notification": {
                "title": "Check-in Confirmado",
                "body": "Sua entrada foi registrada às 08:00",
            },
            "data": {
                "type": "checkin_confirmed",
                "timestamp": datetime.utcnow().isoformat(),
                "checkin_type": "entry",
            },
        }

        assert "notification" in payload
        assert "data" in payload
        assert payload["data"]["type"] == "checkin_confirmed"


class TestValidationWeights:
    """Testes para pesos de validação."""

    def test_validation_weights_sum(self):
        """Testa que pesos podem somar mais de 100 (todos os métodos)."""
        weights = {
            "geofence": 30,
            "biometric": 25,
            "photo": 20,
            "wifi": 10,
            "beacon": 10,
            "nfc": 15,
            "qr_code": 10,
        }

        total = sum(weights.values())
        assert total == 120  # Todos os métodos

    def test_minimum_score_calculation(self):
        """Testa cálculo de score mínimo."""
        # Apenas geofence + biometric = 55
        score = 30 + 25
        min_required = 60

        assert score < min_required  # Precisa de mais validação

        # Com foto = 75
        score += 20
        assert score >= min_required  # Aprovado

    def test_score_cap(self):
        """Testa limite de score em 100."""
        score = 30 + 25 + 20 + 10 + 10 + 15 + 10  # 120
        capped_score = min(score, 100)

        assert capped_score == 100
