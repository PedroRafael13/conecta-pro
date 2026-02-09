"""Testes para o módulo de integração REP."""

from datetime import date, datetime, time
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.hr.rep_integration.models import (
    AFDRecord,
    AFDRecordType,
    DeviceManufacturer,
    DeviceModel,
    DeviceStatus,
    EventStatus,
    EventType,
    IdentificationMethod,
    REPDevice,
    REPEvent,
    REPSync,
    SyncStatus,
    SyncType,
)


class TestREPDeviceModel:
    """Testes para o modelo REPDevice."""

    def test_create_device(self):
        """Testa criação de dispositivo."""
        device = REPDevice(
            id=uuid4(),
            condominio_id=uuid4(),
            manufacturer=DeviceManufacturer.CONTROL_ID.value,
            model=DeviceModel.IDFLEX.value,
            serial_number="CID123456789",
            device_name="REP Portaria Principal",
            ip_address="192.168.1.100",
            port=80,
            status=DeviceStatus.OFFLINE.value,
        )

        assert device.manufacturer == "control_id"
        assert device.model == "idflex"
        assert device.serial_number == "CID123456789"
        assert device.device_name == "REP Portaria Principal"
        assert device.status == "offline"

    def test_device_connection_url(self):
        """Testa geração de URL de conexão."""
        device = REPDevice(
            id=uuid4(),
            condominio_id=uuid4(),
            manufacturer=DeviceManufacturer.CONTROL_ID.value,
            serial_number="TEST123",
            device_name="Test REP",
            ip_address="192.168.1.100",
            port=80,
            communication_protocol="http_rest",
        )

        assert device.connection_url == "http://192.168.1.100:80"

    def test_device_is_online(self):
        """Testa verificação de status online."""
        device = REPDevice(
            id=uuid4(),
            condominio_id=uuid4(),
            serial_number="TEST123",
            device_name="Test REP",
            status=DeviceStatus.ONLINE.value,
        )

        assert device.is_online is True

        device.status = DeviceStatus.OFFLINE.value
        assert device.is_online is False

    def test_device_needs_sync(self):
        """Testa verificação de necessidade de sync."""
        device = REPDevice(
            id=uuid4(),
            condominio_id=uuid4(),
            serial_number="TEST123",
            device_name="Test REP",
            sync_enabled=True,
            sync_interval_seconds=300,
            is_active=True,
            last_sync=None,
        )

        assert device.needs_sync is True

    def test_device_to_dict(self):
        """Testa conversão para dicionário."""
        device_id = uuid4()
        condo_id = uuid4()

        device = REPDevice(
            id=device_id,
            condominio_id=condo_id,
            manufacturer=DeviceManufacturer.CONTROL_ID.value,
            serial_number="TEST123",
            device_name="Test REP",
            status=DeviceStatus.ONLINE.value,
            is_active=True,
        )

        data = device.to_dict()

        assert data["id"] == str(device_id)
        assert data["condominio_id"] == str(condo_id)
        assert data["manufacturer"] == "control_id"
        assert data["serial_number"] == "TEST123"
        assert data["status"] == "online"


class TestREPEventModel:
    """Testes para o modelo REPEvent."""

    def test_create_event(self):
        """Testa criação de evento."""
        now = datetime.utcnow()

        event = REPEvent(
            id=uuid4(),
            device_id=uuid4(),
            condominio_id=uuid4(),
            nsr=12345,
            event_datetime=now,
            event_date=now.date(),
            event_time=now.time(),
            event_type=EventType.ENTRY.value,
            pis_number="12345678901",
            identification_method=IdentificationMethod.BIOMETRIC.value,
            status=EventStatus.RECEIVED.value,
        )

        assert event.nsr == 12345
        assert event.event_type == "entry"
        assert event.pis_number == "12345678901"
        assert event.status == "received"

    def test_generate_afd_line(self):
        """Testa geração de linha AFD."""
        event = REPEvent(
            id=uuid4(),
            device_id=uuid4(),
            condominio_id=uuid4(),
            nsr=123,
            event_datetime=datetime(2025, 12, 31, 8, 30),
            event_date=date(2025, 12, 31),
            event_time=time(8, 30),
            event_type=EventType.ENTRY.value,
            pis_number="12345678901",
        )

        afd_line = event.generate_afd_line()

        # NSR (9 dígitos) + tipo (1) + data (8) + hora (4) + PIS (12)
        assert len(afd_line) == 34
        assert afd_line[:9] == "000000123"  # NSR
        assert afd_line[9] == "3"  # Tipo
        assert afd_line[10:18] == "31122025"  # Data
        assert afd_line[18:22] == "0830"  # Hora

    def test_event_is_processed(self):
        """Testa verificação de processamento."""
        event = REPEvent(
            id=uuid4(),
            device_id=uuid4(),
            condominio_id=uuid4(),
            nsr=1,
            event_datetime=datetime.utcnow(),
            event_date=date.today(),
            event_time=time(8, 0),
            status=EventStatus.PROCESSED.value,
        )

        assert event.is_processed is True

    def test_event_can_retry(self):
        """Testa verificação de retry."""
        event = REPEvent(
            id=uuid4(),
            device_id=uuid4(),
            condominio_id=uuid4(),
            nsr=1,
            event_datetime=datetime.utcnow(),
            event_date=date.today(),
            event_time=time(8, 0),
            status=EventStatus.ERROR.value,
            retry_count=1,
            max_retries=3,
        )

        assert event.can_retry is True

        event.retry_count = 3
        assert event.can_retry is False


class TestREPSyncModel:
    """Testes para o modelo REPSync."""

    def test_create_sync(self):
        """Testa criação de sync."""
        sync = REPSync(
            id=uuid4(),
            device_id=uuid4(),
            condominio_id=uuid4(),
            sync_type=SyncType.EVENTS_PULL.value,
            status=SyncStatus.PENDING.value,
        )

        assert sync.sync_type == "events_pull"
        assert sync.status == "pending"

    def test_sync_progress(self):
        """Testa cálculo de progresso."""
        sync = REPSync(
            id=uuid4(),
            device_id=uuid4(),
            condominio_id=uuid4(),
            sync_type=SyncType.EVENTS_PULL.value,
            total_items=100,
            processed_items=50,
            success_items=45,
            error_items=5,
        )

        assert sync.progress_percent == 50.0
        assert sync.success_rate == 90.0

    def test_sync_lifecycle(self):
        """Testa ciclo de vida da sync."""
        sync = REPSync(
            id=uuid4(),
            device_id=uuid4(),
            condominio_id=uuid4(),
            sync_type=SyncType.EVENTS_PULL.value,
            status=SyncStatus.PENDING.value,
        )

        # Start
        sync.start()
        assert sync.status == SyncStatus.IN_PROGRESS.value
        assert sync.started_at is not None
        assert sync.is_running is True

        # Complete
        sync.complete()
        assert sync.status == SyncStatus.COMPLETED.value
        assert sync.completed_at is not None
        assert sync.is_finished is True

    def test_sync_fail(self):
        """Testa falha de sync."""
        sync = REPSync(
            id=uuid4(),
            device_id=uuid4(),
            condominio_id=uuid4(),
            sync_type=SyncType.EVENTS_PULL.value,
        )

        sync.start()
        sync.fail("Connection timeout", "TIMEOUT")

        assert sync.status == SyncStatus.FAILED.value
        assert sync.error_message == "Connection timeout"
        assert sync.error_code == "TIMEOUT"


class TestAFDRecordModel:
    """Testes para o modelo AFDRecord."""

    def test_generate_type1_header(self):
        """Testa geração de cabeçalho AFD."""
        line = AFDRecord.generate_type1_header(
            nsr=1,
            rep_serial="CID123456789012345",
            manufacturer="Control iD",
            model="iDFlex",
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 31),
        )

        assert line[:9] == "000000001"  # NSR
        assert line[9] == "1"  # Tipo

    def test_generate_type2_company(self):
        """Testa geração de dados do empregador."""
        line = AFDRecord.generate_type2_company(
            nsr=2,
            cnpj="12345678000190",
            cei="123456789012",
            company_name="Empresa Teste LTDA",
        )

        assert line[:9] == "000000002"  # NSR
        assert line[9] == "2"  # Tipo
        assert line[10] == "1"  # CNPJ

    def test_generate_type3_record(self):
        """Testa geração de marcação de ponto."""
        line = AFDRecord.generate_type3_record(
            nsr=100,
            record_date=date(2025, 12, 31),
            record_time=time(8, 30),
            pis="12345678901",
        )

        assert line[:9] == "000000100"  # NSR
        assert line[9] == "3"  # Tipo
        assert line[10:18] == "31122025"  # Data
        assert line[18:22] == "0830"  # Hora
        assert "12345678901" in line  # PIS

    def test_generate_type9_trailer(self):
        """Testa geração de trailer."""
        line = AFDRecord.generate_type9_trailer(
            nsr=1000,
            total_records=998,
        )

        assert line[:9] == "000001000"  # NSR
        assert line[9] == "9"  # Tipo
        assert "000000998" in line  # Total

    def test_parse_afd_line_type3(self):
        """Testa parsing de linha AFD tipo 3."""
        line = "0000001003311220250830123456789012"

        parsed = AFDRecord.parse_afd_line(line)

        assert parsed["nsr"] == 100
        assert parsed["record_type"] == "3"
        assert parsed["record_date"] == date(2025, 12, 31)
        assert parsed["record_time"] == time(8, 30)
        assert parsed["pis_number"] == "123456789012"


class TestEnums:
    """Testes para enums do módulo."""

    def test_device_manufacturer_values(self):
        """Testa valores de fabricantes."""
        assert DeviceManufacturer.CONTROL_ID.value == "control_id"
        assert DeviceManufacturer.INTELBRAS.value == "intelbras"
        assert DeviceManufacturer.HENRY.value == "henry"

    def test_device_status_values(self):
        """Testa valores de status."""
        assert DeviceStatus.ONLINE.value == "online"
        assert DeviceStatus.OFFLINE.value == "offline"
        assert DeviceStatus.SYNCING.value == "syncing"
        assert DeviceStatus.ERROR.value == "error"

    def test_event_type_values(self):
        """Testa valores de tipos de evento."""
        assert EventType.ENTRY.value == "entry"
        assert EventType.EXIT.value == "exit"
        assert EventType.BREAK_START.value == "break_start"
        assert EventType.BREAK_END.value == "break_end"

    def test_sync_type_values(self):
        """Testa valores de tipos de sync."""
        assert SyncType.EVENTS_PULL.value == "events_pull"
        assert SyncType.EVENTS_PUSH.value == "events_push"
        assert SyncType.USERS_PUSH.value == "users_push"


class TestAFDCompliance:
    """Testes de conformidade com Portaria 671."""

    def test_afd_line_format_type3(self):
        """Verifica formato de linha tipo 3."""
        # Formato: NSR(9) + Tipo(1) + Data(8) + Hora(4) + PIS(12)
        # Total: 34 caracteres

        line = AFDRecord.generate_type3_record(
            nsr=1,
            record_date=date(2025, 1, 15),
            record_time=time(14, 30),
            pis="12345678901",
        )

        # Verificar tamanho
        assert len(line) == 34

        # Verificar NSR (posição 1-9)
        assert line[0:9] == "000000001"

        # Verificar tipo (posição 10)
        assert line[9] == "3"

        # Verificar data (posição 11-18, formato ddmmaaaa)
        assert line[10:18] == "15012025"

        # Verificar hora (posição 19-22, formato hhmm)
        assert line[18:22] == "1430"

    def test_nsr_sequential(self):
        """Verifica que NSR é sequencial."""
        lines = []
        for i in range(1, 11):
            line = AFDRecord.generate_type3_record(
                nsr=i,
                record_date=date(2025, 1, 15),
                record_time=time(8, 0),
                pis="12345678901",
            )
            lines.append(line)

        # Verificar sequência
        for i, line in enumerate(lines, 1):
            nsr_str = line[0:9]
            assert int(nsr_str) == i

    def test_pis_format(self):
        """Verifica formato do PIS."""
        line = AFDRecord.generate_type3_record(
            nsr=1,
            record_date=date(2025, 1, 15),
            record_time=time(8, 0),
            pis="12345678901",  # 11 dígitos
        )

        # PIS deve ter 12 dígitos (com padding)
        pis_in_line = line[22:34]
        assert len(pis_in_line) == 12
