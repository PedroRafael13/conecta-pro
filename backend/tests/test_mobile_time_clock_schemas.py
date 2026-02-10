"""Testes para schemas do módulo Mobile Time Clock."""

from datetime import datetime, time
from uuid import uuid4

import pytest
from pydantic import ValidationError

from modules.hr.mobile_time_clock.schemas import (
    CheckInBiometric,
    # CheckIn
    CheckInLocation,
    CheckInPhoto,
    CheckInValidation,
    # Geofence
    Coordinate,
    DeviceHeartbeat,
    GeofenceCheckRequest,
    GeofenceZoneCreate,
    GeofenceZoneFilter,
    GeofenceZoneUpdate,
    MobileCheckInCreate,
    MobileCheckInFilter,
    MobileCheckInReview,
    MobileDeviceApprove,
    MobileDeviceBlock,
    MobileDeviceFilter,
    # Device
    MobileDeviceRegister,
    MobileDeviceUpdate,
    OfflineQueueBatch,
    OfflineQueueCleanup,
    OfflineQueueFilter,
    # Offline
    OfflineQueueItemCreate,
)


class TestMobileDeviceSchemas:
    """Testes para schemas de dispositivo."""

    def test_register_valid(self):
        """Testa registro válido de dispositivo."""
        data = MobileDeviceRegister(
            device_name="iPhone 15 Pro",
            device_uuid="uuid-abc-123-def-456",
            platform="ios",
            os_version="17.0",
            app_version="1.0.0",
            model="iPhone15,2",
            manufacturer="Apple",
        )

        assert data.device_name == "iPhone 15 Pro"
        assert data.platform == "ios"

    def test_register_invalid_platform(self):
        """Testa plataforma inválida."""
        with pytest.raises(ValidationError):
            MobileDeviceRegister(
                device_name="Test",
                device_uuid="uuid-123",
                platform="windows",  # Inválido
            )

    def test_register_invalid_uuid_length(self):
        """Testa UUID muito curto."""
        with pytest.raises(ValidationError):
            MobileDeviceRegister(
                device_name="Test",
                device_uuid="abc",  # Muito curto
                platform="android",
            )

    def test_update_partial(self):
        """Testa atualização parcial."""
        data = MobileDeviceUpdate(
            app_version="2.0.0",
        )

        assert data.app_version == "2.0.0"
        assert data.device_name is None

    def test_approve_device(self):
        """Testa aprovação de dispositivo."""
        data = MobileDeviceApprove(
            is_trusted=True,
            biometric_enabled=True,
            allow_offline_checkin=True,
            max_offline_hours=48,
        )

        assert data.is_trusted is True
        assert data.max_offline_hours == 48

    def test_approve_max_offline_hours_limit(self):
        """Testa limite de horas offline."""
        with pytest.raises(ValidationError):
            MobileDeviceApprove(
                max_offline_hours=200,  # Máximo é 168
            )

    def test_block_device(self):
        """Testa bloqueio de dispositivo."""
        data = MobileDeviceBlock(
            reason="Dispositivo comprometido",
        )

        assert data.reason == "Dispositivo comprometido"

    def test_block_reason_required(self):
        """Testa razão obrigatória para bloqueio."""
        with pytest.raises(ValidationError):
            MobileDeviceBlock(
                reason="",  # Muito curto
            )

    def test_heartbeat(self):
        """Testa heartbeat."""
        data = DeviceHeartbeat(
            device_uuid="uuid-123-456",
            app_version="1.0.0",
            latitude=-23.5505,
            longitude=-46.6333,
        )

        assert data.latitude == -23.5505


class TestCheckInSchemas:
    """Testes para schemas de check-in."""

    def test_location_valid(self):
        """Testa localização válida."""
        data = CheckInLocation(
            latitude=-23.5505,
            longitude=-46.6333,
            accuracy_meters=10.0,
            altitude=750.0,
            provider="gps",
        )

        assert data.latitude == -23.5505
        assert data.provider == "gps"

    def test_location_invalid_latitude(self):
        """Testa latitude inválida."""
        with pytest.raises(ValidationError):
            CheckInLocation(
                latitude=100,  # Máximo é 90
                longitude=-46.6333,
            )

    def test_location_invalid_longitude(self):
        """Testa longitude inválida."""
        with pytest.raises(ValidationError):
            CheckInLocation(
                latitude=-23.5505,
                longitude=200,  # Máximo é 180
            )

    def test_biometric_valid(self):
        """Testa biometria válida."""
        data = CheckInBiometric(
            verified=True,
            type="fingerprint",
            score=95,
        )

        assert data.verified is True
        assert data.score == 95

    def test_biometric_invalid_type(self):
        """Testa tipo biométrico inválido."""
        with pytest.raises(ValidationError):
            CheckInBiometric(
                verified=True,
                type="voice",  # Não suportado
            )

    def test_photo_valid(self):
        """Testa foto válida."""
        data = CheckInPhoto(
            captured=True,
            path="/photos/selfie_123.jpg",
            match_score=0.85,
        )

        assert data.captured is True
        assert data.match_score == 0.85

    def test_photo_match_score_range(self):
        """Testa range de score de foto."""
        with pytest.raises(ValidationError):
            CheckInPhoto(
                captured=True,
                match_score=150.0,  # Máximo é 100
            )

    def test_checkin_create_valid(self):
        """Testa criação de check-in válido."""
        data = MobileCheckInCreate(
            checkin_type="entry",
            device_timestamp=datetime.utcnow(),
            app_version="1.0.0",
            location=CheckInLocation(
                latitude=-23.5505,
                longitude=-46.6333,
                accuracy_meters=10,
            ),
        )

        assert data.checkin_type == "entry"
        assert data.location is not None

    def test_checkin_create_invalid_type(self):
        """Testa tipo de check-in inválido."""
        with pytest.raises(ValidationError):
            MobileCheckInCreate(
                checkin_type="lunch",  # Inválido
                device_timestamp=datetime.utcnow(),
            )

    def test_checkin_review(self):
        """Testa revisão de check-in."""
        data = MobileCheckInReview(
            approved=False,
            notes="Localização inconsistente",
            rejection_reason="Fora da área permitida",
        )

        assert data.approved is False
        assert data.rejection_reason is not None


class TestGeofenceSchemas:
    """Testes para schemas de geofence."""

    def test_coordinate_valid(self):
        """Testa coordenada válida."""
        data = Coordinate(
            lat=-23.5505,
            lng=-46.6333,
        )

        assert data.lat == -23.5505

    def test_zone_create_circle(self):
        """Testa criação de zona circular."""
        data = GeofenceZoneCreate(
            name="Sede Principal",
            zone_type="circle",
            category="headquarters",
            center_latitude=-23.5505,
            center_longitude=-46.6333,
            radius_meters=100,
        )

        assert data.name == "Sede Principal"
        assert data.zone_type == "circle"
        assert data.radius_meters == 100

    def test_zone_create_polygon(self):
        """Testa criação de zona poligonal."""
        data = GeofenceZoneCreate(
            name="Área de Trabalho",
            zone_type="polygon",
            category="branch",
            center_latitude=-23.5505,
            center_longitude=-46.6333,
            radius_meters=100,
            polygon_coordinates=[
                Coordinate(lat=-23.55, lng=-46.63),
                Coordinate(lat=-23.55, lng=-46.64),
                Coordinate(lat=-23.56, lng=-46.64),
                Coordinate(lat=-23.56, lng=-46.63),
            ],
        )

        assert data.zone_type == "polygon"
        assert len(data.polygon_coordinates) == 4

    def test_zone_create_invalid_radius(self):
        """Testa raio inválido."""
        with pytest.raises(ValidationError):
            GeofenceZoneCreate(
                name="Test",
                zone_type="circle",
                category="headquarters",
                center_latitude=-23.5505,
                center_longitude=-46.6333,
                radius_meters=5,  # Mínimo é 10
            )

    def test_zone_update_partial(self):
        """Testa atualização parcial de zona."""
        data = GeofenceZoneUpdate(
            name="Novo Nome",
            radius_meters=150,
        )

        assert data.name == "Novo Nome"
        assert data.category is None

    def test_geofence_check_request(self):
        """Testa request de verificação de geofence."""
        data = GeofenceCheckRequest(
            condominio_id=uuid4(),
            latitude=-23.5505,
            longitude=-46.6333,
            accuracy_meters=10,
        )

        assert data.latitude == -23.5505


class TestOfflineSchemas:
    """Testes para schemas de fila offline."""

    def test_queue_item_create(self):
        """Testa criação de item na fila."""
        data = OfflineQueueItemCreate(
            offline_id="offline-12345-67890",
            checkin_data={"type": "entry", "location": {}},
            checkin_type="entry",
            device_timestamp=datetime.utcnow(),
            latitude=-23.5505,
            longitude=-46.6333,
            accuracy_meters=10,
            expires_hours=24,
        )

        assert data.offline_id == "offline-12345-67890"
        assert data.expires_hours == 24

    def test_queue_item_invalid_offline_id(self):
        """Testa offline_id muito curto."""
        with pytest.raises(ValidationError):
            OfflineQueueItemCreate(
                offline_id="short",  # Mínimo é 10
                checkin_data={},
                checkin_type="entry",
                device_timestamp=datetime.utcnow(),
            )

    def test_queue_item_expires_hours_range(self):
        """Testa range de horas de expiração."""
        with pytest.raises(ValidationError):
            OfflineQueueItemCreate(
                offline_id="offline-12345",
                checkin_data={},
                checkin_type="entry",
                device_timestamp=datetime.utcnow(),
                expires_hours=200,  # Máximo é 168
            )

    def test_queue_batch(self):
        """Testa batch de itens."""
        items = [
            OfflineQueueItemCreate(
                offline_id=f"offline-{i:05d}",
                checkin_data={},
                checkin_type="entry",
                device_timestamp=datetime.utcnow(),
            )
            for i in range(3)
        ]

        data = OfflineQueueBatch(items=items)
        assert len(data.items) == 3

    def test_queue_batch_max_items(self):
        """Testa limite de itens no batch."""
        items = [
            OfflineQueueItemCreate(
                offline_id=f"offline-{i:05d}-extra",
                checkin_data={},
                checkin_type="entry",
                device_timestamp=datetime.utcnow(),
            )
            for i in range(101)  # Máximo é 100
        ]

        with pytest.raises(ValidationError):
            OfflineQueueBatch(items=items)

    def test_queue_cleanup(self):
        """Testa configuração de limpeza."""
        data = OfflineQueueCleanup(
            older_than_hours=72,
            statuses=["synced", "expired"],
            dry_run=True,
        )

        assert data.older_than_hours == 72
        assert data.dry_run is True

    def test_queue_cleanup_hours_range(self):
        """Testa range de horas para limpeza."""
        with pytest.raises(ValidationError):
            OfflineQueueCleanup(
                older_than_hours=12,  # Mínimo é 24
            )


class TestFilters:
    """Testes para schemas de filtros."""

    def test_device_filter(self):
        """Testa filtro de dispositivos."""
        data = MobileDeviceFilter(
            employee_id=uuid4(),
            platform="android",
            status="active",
            is_trusted=True,
        )

        assert data.platform == "android"
        assert data.is_trusted is True

    def test_checkin_filter(self):
        """Testa filtro de check-ins."""
        data = MobileCheckInFilter(
            employee_id=uuid4(),
            checkin_type="entry",
            status="validated",
            has_anomaly=False,
            needs_review=False,
        )

        assert data.checkin_type == "entry"
        assert data.has_anomaly is False

    def test_geofence_filter(self):
        """Testa filtro de zonas."""
        data = GeofenceZoneFilter(
            condominio_id=uuid4(),
            category="headquarters",
            is_primary=True,
            near_latitude=-23.5505,
            near_longitude=-46.6333,
            max_distance_km=5,
        )

        assert data.category == "headquarters"
        assert data.max_distance_km == 5

    def test_offline_queue_filter(self):
        """Testa filtro de fila offline."""
        data = OfflineQueueFilter(
            device_id=uuid4(),
            status="pending",
            priority="high",
            is_expired=False,
        )

        assert data.status == "pending"
        assert data.is_expired is False
