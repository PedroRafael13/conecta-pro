"""
Testes unitários para models do módulo Remote Gatehouse.
"""

from datetime import datetime, timedelta

import pytest

from modules.remote_gatehouse.models.access_log import AccessLog, AccessLogType
from modules.remote_gatehouse.models.equipment_status import (
    EquipmentStatus,
    EquipmentStatusType,
)
from modules.remote_gatehouse.models.guardian_occurrence import (
    GuardianOccurrence,
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)
from modules.remote_gatehouse.models.guardian_sync import (
    GuardianSync,
    SyncDirection,
    SyncEntityType,
    SyncStatus,
)


class TestGuardianSyncModel:
    """Testes para GuardianSync model."""

    def test_create_guardian_sync(self) -> None:
        """Testa criação de sincronização."""
        sync = GuardianSync(
            sync_code="SYNC-20241230-ABC12345",
            direction=SyncDirection.ERP_TO_GUARDIAN.value,
            entity_type=SyncEntityType.CONTRACT.value,
            entity_id="contract-123",
        )

        assert sync.sync_code == "SYNC-20241230-ABC12345"
        assert sync.direction == SyncDirection.ERP_TO_GUARDIAN.value
        assert sync.entity_type == SyncEntityType.CONTRACT.value
        assert sync.status == SyncStatus.PENDING.value

    def test_sync_is_completed(self) -> None:
        """Testa verificação de sincronização concluída."""
        sync = GuardianSync(
            sync_code="SYNC-001",
            direction=SyncDirection.ERP_TO_GUARDIAN.value,
            entity_type=SyncEntityType.CONTRACT.value,
            entity_id="contract-123",
            status=SyncStatus.COMPLETED.value,
        )

        assert sync.is_completed is True
        assert sync.is_failed is False

    def test_sync_is_failed(self) -> None:
        """Testa verificação de sincronização falha."""
        sync = GuardianSync(
            sync_code="SYNC-002",
            direction=SyncDirection.ERP_TO_GUARDIAN.value,
            entity_type=SyncEntityType.CONTRACT.value,
            entity_id="contract-123",
            status=SyncStatus.FAILED.value,
            retry_count=1,
            max_retries=3,
        )

        assert sync.is_failed is True
        assert sync.can_retry is True

    def test_sync_cannot_retry_max_reached(self) -> None:
        """Testa que não pode tentar após máximo."""
        sync = GuardianSync(
            sync_code="SYNC-003",
            direction=SyncDirection.ERP_TO_GUARDIAN.value,
            entity_type=SyncEntityType.CONTRACT.value,
            entity_id="contract-123",
            status=SyncStatus.FAILED.value,
            retry_count=3,
            max_retries=3,
        )

        assert sync.can_retry is False

    def test_sync_is_outbound(self) -> None:
        """Testa verificação de sincronização de saída."""
        sync = GuardianSync(
            sync_code="SYNC-004",
            direction=SyncDirection.ERP_TO_GUARDIAN.value,
            entity_type=SyncEntityType.CONTRACT.value,
            entity_id="contract-123",
        )

        assert sync.is_outbound is True
        assert sync.is_inbound is False

    def test_sync_is_inbound(self) -> None:
        """Testa verificação de sincronização de entrada."""
        sync = GuardianSync(
            sync_code="SYNC-005",
            direction=SyncDirection.GUARDIAN_TO_ERP.value,
            entity_type=SyncEntityType.OCCURRENCE.value,
            entity_id="occurrence-123",
        )

        assert sync.is_inbound is True
        assert sync.is_outbound is False

    def test_mark_completed(self) -> None:
        """Testa marcar sincronização como concluída."""
        sync = GuardianSync(
            sync_code="SYNC-006",
            direction=SyncDirection.ERP_TO_GUARDIAN.value,
            entity_type=SyncEntityType.CONTRACT.value,
            entity_id="contract-123",
            status=SyncStatus.IN_PROGRESS.value,
        )

        sync.mark_completed({"success": True})

        assert sync.status == SyncStatus.COMPLETED.value
        assert sync.synced_at is not None
        assert sync.response == {"success": True}

    def test_mark_failed(self) -> None:
        """Testa marcar sincronização como falha."""
        sync = GuardianSync(
            sync_code="SYNC-007",
            direction=SyncDirection.ERP_TO_GUARDIAN.value,
            entity_type=SyncEntityType.CONTRACT.value,
            entity_id="contract-123",
            status=SyncStatus.IN_PROGRESS.value,
        )

        sync.mark_failed("Connection timeout", {"code": 504})

        assert sync.status == SyncStatus.FAILED.value
        assert sync.error_message == "Connection timeout"
        assert sync.error_details == {"code": 504}

    def test_increment_retry(self) -> None:
        """Testa incrementar contador de retentativas."""
        sync = GuardianSync(
            sync_code="SYNC-008",
            direction=SyncDirection.ERP_TO_GUARDIAN.value,
            entity_type=SyncEntityType.CONTRACT.value,
            entity_id="contract-123",
            status=SyncStatus.FAILED.value,
            retry_count=0,
        )

        sync.increment_retry()

        assert sync.retry_count == 1
        assert sync.status == SyncStatus.IN_PROGRESS.value
        assert sync.last_retry_at is not None


class TestAccessLogModel:
    """Testes para AccessLog model."""

    def test_create_access_log(self) -> None:
        """Testa criação de log de acesso."""
        log = AccessLog(
            guardian_id="guardian-log-001",
            log_type=AccessLogType.ENTRY.value,
            client_id="client-123",
            person_name="João Silva",
            event_timestamp=datetime.utcnow(),
        )

        assert log.guardian_id == "guardian-log-001"
        assert log.log_type == AccessLogType.ENTRY.value
        assert log.person_name == "João Silva"

    def test_access_log_is_entry(self) -> None:
        """Testa verificação de entrada."""
        log = AccessLog(
            guardian_id="guardian-log-002",
            log_type=AccessLogType.ENTRY.value,
            client_id="client-123",
            person_name="João Silva",
            event_timestamp=datetime.utcnow(),
        )

        assert log.is_entry is True
        assert log.is_exit is False
        assert log.is_denied is False

    def test_access_log_is_exit(self) -> None:
        """Testa verificação de saída."""
        log = AccessLog(
            guardian_id="guardian-log-003",
            log_type=AccessLogType.EXIT.value,
            client_id="client-123",
            person_name="João Silva",
            event_timestamp=datetime.utcnow(),
        )

        assert log.is_exit is True
        assert log.is_entry is False

    def test_access_log_is_denied(self) -> None:
        """Testa verificação de acesso negado."""
        log = AccessLog(
            guardian_id="guardian-log-004",
            log_type=AccessLogType.DENIED.value,
            client_id="client-123",
            person_name="Desconhecido",
            denial_reason="Documento não autorizado",
            event_timestamp=datetime.utcnow(),
        )

        assert log.is_denied is True

    def test_access_log_has_vehicle(self) -> None:
        """Testa verificação de veículo."""
        log = AccessLog(
            guardian_id="guardian-log-005",
            log_type=AccessLogType.ENTRY.value,
            client_id="client-123",
            person_name="João Silva",
            vehicle_plate="ABC1234",
            event_timestamp=datetime.utcnow(),
        )

        assert log.has_vehicle is True

    def test_access_log_has_media(self) -> None:
        """Testa verificação de mídia."""
        log = AccessLog(
            guardian_id="guardian-log-006",
            log_type=AccessLogType.ENTRY.value,
            client_id="client-123",
            person_name="João Silva",
            photos=["http://example.com/photo1.jpg"],
            event_timestamp=datetime.utcnow(),
        )

        assert log.has_media is True


class TestGuardianOccurrenceModel:
    """Testes para GuardianOccurrence model."""

    def test_create_occurrence(self) -> None:
        """Testa criação de ocorrência."""
        occurrence = GuardianOccurrence(
            guardian_id="guardian-occ-001",
            occurrence_code="OC-20241230-ABC123",
            occurrence_type=OccurrenceType.ALARM.value,
            severity=OccurrenceSeverity.HIGH.value,
            client_id="client-123",
            title="Alarme disparado",
            description="Alarme do setor A disparado às 22h",
            event_timestamp=datetime.utcnow(),
        )

        assert occurrence.occurrence_code == "OC-20241230-ABC123"
        assert occurrence.occurrence_type == OccurrenceType.ALARM.value
        assert occurrence.severity == OccurrenceSeverity.HIGH.value
        assert occurrence.status == OccurrenceStatus.OPEN.value

    def test_occurrence_is_open(self) -> None:
        """Testa verificação de ocorrência aberta."""
        occurrence = GuardianOccurrence(
            guardian_id="guardian-occ-002",
            occurrence_code="OC-002",
            occurrence_type=OccurrenceType.ALARM.value,
            severity=OccurrenceSeverity.MEDIUM.value,
            client_id="client-123",
            title="Teste",
            description="Teste",
            status=OccurrenceStatus.IN_PROGRESS.value,
            event_timestamp=datetime.utcnow(),
        )

        assert occurrence.is_open is True
        assert occurrence.is_resolved is False

    def test_occurrence_is_critical(self) -> None:
        """Testa verificação de ocorrência crítica."""
        occurrence = GuardianOccurrence(
            guardian_id="guardian-occ-003",
            occurrence_code="OC-003",
            occurrence_type=OccurrenceType.FIRE.value,
            severity=OccurrenceSeverity.CRITICAL.value,
            client_id="client-123",
            title="Incêndio",
            description="Incêndio detectado",
            event_timestamp=datetime.utcnow(),
        )

        assert occurrence.is_critical is True
        assert occurrence.is_high_severity is True

    def test_occurrence_acknowledge(self) -> None:
        """Testa reconhecimento de ocorrência."""
        occurrence = GuardianOccurrence(
            guardian_id="guardian-occ-004",
            occurrence_code="OC-004",
            occurrence_type=OccurrenceType.ALARM.value,
            severity=OccurrenceSeverity.HIGH.value,
            client_id="client-123",
            title="Alarme",
            description="Alarme disparado",
            event_timestamp=datetime.utcnow() - timedelta(minutes=5),
        )

        occurrence.acknowledge("operator-123", "João Operador")

        assert occurrence.status == OccurrenceStatus.ACKNOWLEDGED.value
        assert occurrence.operator_id == "operator-123"
        assert occurrence.operator_name == "João Operador"
        assert occurrence.acknowledged_at is not None
        assert occurrence.response_time_seconds is not None

    def test_occurrence_resolve(self) -> None:
        """Testa resolução de ocorrência."""
        occurrence = GuardianOccurrence(
            guardian_id="guardian-occ-005",
            occurrence_code="OC-005",
            occurrence_type=OccurrenceType.ALARM.value,
            severity=OccurrenceSeverity.MEDIUM.value,
            client_id="client-123",
            title="Alarme",
            description="Alarme disparado",
            status=OccurrenceStatus.IN_PROGRESS.value,
            acknowledged_at=datetime.utcnow() - timedelta(minutes=10),
            event_timestamp=datetime.utcnow() - timedelta(minutes=15),
        )

        occurrence.resolve("Falso alarme - sensor com defeito")

        assert occurrence.status == OccurrenceStatus.RESOLVED.value
        assert occurrence.resolution == "Falso alarme - sensor com defeito"
        assert occurrence.resolved_at is not None

    def test_occurrence_escalate(self) -> None:
        """Testa escalação de ocorrência."""
        occurrence = GuardianOccurrence(
            guardian_id="guardian-occ-006",
            occurrence_code="OC-006",
            occurrence_type=OccurrenceType.INTRUSION.value,
            severity=OccurrenceSeverity.CRITICAL.value,
            client_id="client-123",
            title="Invasão",
            description="Invasão detectada",
            status=OccurrenceStatus.IN_PROGRESS.value,
            event_timestamp=datetime.utcnow(),
        )

        occurrence.escalate("Gerente Operacional", "Situação crítica")

        assert occurrence.status == OccurrenceStatus.ESCALATED.value
        assert occurrence.escalated_to == "Gerente Operacional"
        assert occurrence.escalation_reason == "Situação crítica"
        assert occurrence.escalated_at is not None

    def test_occurrence_mark_false_alarm(self) -> None:
        """Testa marcação de falso alarme."""
        occurrence = GuardianOccurrence(
            guardian_id="guardian-occ-007",
            occurrence_code="OC-007",
            occurrence_type=OccurrenceType.ALARM.value,
            severity=OccurrenceSeverity.HIGH.value,
            client_id="client-123",
            title="Alarme",
            description="Alarme disparado",
            event_timestamp=datetime.utcnow(),
        )

        occurrence.mark_as_false_alarm()

        assert occurrence.is_false_alarm is True
        assert occurrence.status == OccurrenceStatus.CANCELLED.value


class TestEquipmentStatusModel:
    """Testes para EquipmentStatus model."""

    def test_create_equipment_status(self) -> None:
        """Testa criação de status de equipamento."""
        equipment = EquipmentStatus(
            guardian_id="guardian-equip-001",
            equipment_id="cam-001",
            equipment_type="camera",
            equipment_name="Câmera Entrada Principal",
            status=EquipmentStatusType.ONLINE.value,
            client_id="client-123",
        )

        assert equipment.equipment_name == "Câmera Entrada Principal"
        assert equipment.equipment_type == "camera"
        assert equipment.status == EquipmentStatusType.ONLINE.value

    def test_equipment_is_online(self) -> None:
        """Testa verificação de equipamento online."""
        equipment = EquipmentStatus(
            guardian_id="guardian-equip-002",
            equipment_id="cam-002",
            equipment_type="camera",
            equipment_name="Câmera Garagem",
            status=EquipmentStatusType.ONLINE.value,
            client_id="client-123",
        )

        assert equipment.is_online is True
        assert equipment.is_offline is False

    def test_equipment_has_issues(self) -> None:
        """Testa verificação de equipamento com problemas."""
        equipment = EquipmentStatus(
            guardian_id="guardian-equip-003",
            equipment_id="cam-003",
            equipment_type="camera",
            equipment_name="Câmera Hall",
            status=EquipmentStatusType.WARNING.value,
            client_id="client-123",
        )

        assert equipment.has_issues is True

    def test_equipment_is_camera(self) -> None:
        """Testa verificação de tipo câmera."""
        equipment = EquipmentStatus(
            guardian_id="guardian-equip-004",
            equipment_id="dvr-001",
            equipment_type="dvr",
            equipment_name="DVR Principal",
            status=EquipmentStatusType.ONLINE.value,
            client_id="client-123",
        )

        assert equipment.is_camera is True

    def test_equipment_set_online(self) -> None:
        """Testa marcar equipamento como online."""
        equipment = EquipmentStatus(
            guardian_id="guardian-equip-005",
            equipment_id="cam-005",
            equipment_type="camera",
            equipment_name="Câmera Piscina",
            status=EquipmentStatusType.OFFLINE.value,
            client_id="client-123",
        )

        equipment.set_online(50)

        assert equipment.status == EquipmentStatusType.ONLINE.value
        assert equipment.ping_latency_ms == 50
        assert equipment.last_online_at is not None

    def test_equipment_set_offline(self) -> None:
        """Testa marcar equipamento como offline."""
        equipment = EquipmentStatus(
            guardian_id="guardian-equip-006",
            equipment_id="cam-006",
            equipment_type="camera",
            equipment_name="Câmera Portão",
            status=EquipmentStatusType.ONLINE.value,
            client_id="client-123",
        )

        equipment.set_offline("Falha de conexão")

        assert equipment.status == EquipmentStatusType.OFFLINE.value
        assert equipment.status_message == "Falha de conexão"
        assert equipment.last_offline_at is not None

    def test_equipment_add_alert(self) -> None:
        """Testa adicionar alerta ao equipamento."""
        equipment = EquipmentStatus(
            guardian_id="guardian-equip-007",
            equipment_id="cam-007",
            equipment_type="camera",
            equipment_name="Câmera Estacionamento",
            status=EquipmentStatusType.WARNING.value,
            client_id="client-123",
        )

        equipment.add_alert({"type": "storage_full", "message": "HD cheio"})

        assert equipment.has_alerts is True
        assert equipment.alert_count == 1
        assert len(equipment.active_alerts) == 1

    def test_equipment_clear_alerts(self) -> None:
        """Testa limpar alertas do equipamento."""
        equipment = EquipmentStatus(
            guardian_id="guardian-equip-008",
            equipment_id="cam-008",
            equipment_type="camera",
            equipment_name="Câmera Academia",
            status=EquipmentStatusType.WARNING.value,
            client_id="client-123",
            has_alerts=True,
            active_alerts=[{"type": "test"}],
            alert_count=1,
        )

        equipment.clear_alerts()

        assert equipment.has_alerts is False
        assert equipment.alert_count == 0
        assert equipment.active_alerts == []


class TestEnums:
    """Testes para enums do módulo."""

    def test_sync_status_values(self) -> None:
        """Testa valores de SyncStatus."""
        assert SyncStatus.PENDING.value == "pending"
        assert SyncStatus.IN_PROGRESS.value == "in_progress"
        assert SyncStatus.COMPLETED.value == "completed"
        assert SyncStatus.FAILED.value == "failed"

    def test_sync_direction_values(self) -> None:
        """Testa valores de SyncDirection."""
        assert SyncDirection.ERP_TO_GUARDIAN.value == "erp_to_guardian"
        assert SyncDirection.GUARDIAN_TO_ERP.value == "guardian_to_erp"

    def test_access_log_type_values(self) -> None:
        """Testa valores de AccessLogType."""
        assert AccessLogType.ENTRY.value == "entry"
        assert AccessLogType.EXIT.value == "exit"
        assert AccessLogType.DENIED.value == "denied"
        assert AccessLogType.VISITOR.value == "visitor"

    def test_occurrence_type_values(self) -> None:
        """Testa valores de OccurrenceType."""
        assert OccurrenceType.ALARM.value == "alarm"
        assert OccurrenceType.FIRE.value == "fire"
        assert OccurrenceType.INTRUSION.value == "intrusion"
        assert OccurrenceType.PANIC.value == "panic"

    def test_occurrence_severity_values(self) -> None:
        """Testa valores de OccurrenceSeverity."""
        assert OccurrenceSeverity.LOW.value == "low"
        assert OccurrenceSeverity.MEDIUM.value == "medium"
        assert OccurrenceSeverity.HIGH.value == "high"
        assert OccurrenceSeverity.CRITICAL.value == "critical"

    def test_equipment_status_type_values(self) -> None:
        """Testa valores de EquipmentStatusType."""
        assert EquipmentStatusType.ONLINE.value == "online"
        assert EquipmentStatusType.OFFLINE.value == "offline"
        assert EquipmentStatusType.WARNING.value == "warning"
        assert EquipmentStatusType.ERROR.value == "error"
