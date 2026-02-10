"""
Testes unitários para services do módulo Remote Gatehouse.
"""

from datetime import datetime, timedelta

import pytest
from modules.remote_gatehouse.models.guardian_occurrence import (
    OccurrenceSeverity,
    OccurrenceType,
)
from modules.remote_gatehouse.models.guardian_sync import (
    SyncDirection,
    SyncEntityType,
    SyncStatus,
)
from modules.remote_gatehouse.services.guardian_sync_service import (
    GuardianSyncService,
    guardian_sync_service,
)
from modules.remote_gatehouse.services.occurrence_analyzer import (
    OccurrenceAnalyzer,
    occurrence_analyzer,
)


class TestGuardianSyncService:
    """Testes para GuardianSyncService."""

    def test_singleton_instance(self) -> None:
        """Testa que singleton está inicializado."""
        assert guardian_sync_service is not None

    def test_configure(self) -> None:
        """Testa configuração do serviço."""
        service = GuardianSyncService()
        service.configure("https://guardian.example.com", "api-key-123")

        assert service._guardian_base_url == "https://guardian.example.com"
        assert service._api_key == "api-key-123"

    def test_prepare_contract_payload(self) -> None:
        """Testa preparação de payload de contrato."""
        service = GuardianSyncService()
        payload = service.prepare_contract_payload(
            contract_id="contract-123",
            client_id="client-456",
            client_name="Condomínio Solar",
            address="Rua das Flores, 100",
            services=["remote_gatehouse", "cctv"],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            posts=[{"id": "post-1", "name": "Portaria"}],
            employees=[{"id": "emp-1", "name": "João"}],
        )

        assert payload["contract_id"] == "contract-123"
        assert payload["client_id"] == "client-456"
        assert payload["client_name"] == "Condomínio Solar"
        assert "remote_gatehouse" in payload["services"]
        assert len(payload["posts"]) == 1
        assert len(payload["employees"]) == 1
        assert payload["source"] == "erp_conecta_mais"

    def test_prepare_authorized_person_payload(self) -> None:
        """Testa preparação de payload de pessoa autorizada."""
        service = GuardianSyncService()
        payload = service.prepare_authorized_person_payload(
            person_id="person-123",
            client_id="client-456",
            name="Maria Silva",
            document="12345678900",
            person_type="morador",
            unit_code="101",
            access_type="full",
            photo_url="http://example.com/photo.jpg",
            vehicle_plates=["ABC1234", "XYZ5678"],
        )

        assert payload["person_id"] == "person-123"
        assert payload["name"] == "Maria Silva"
        assert payload["document"] == "12345678900"
        assert payload["person_type"] == "morador"
        assert payload["unit_code"] == "101"
        assert len(payload["vehicle_plates"]) == 2

    def test_prepare_access_config_payload(self) -> None:
        """Testa preparação de payload de configuração de acesso."""
        service = GuardianSyncService()
        payload = service.prepare_access_config_payload(
            client_id="client-123",
            post_id="post-456",
            access_points=[
                {"id": "ap-1", "name": "Portaria Social"},
                {"id": "ap-2", "name": "Garagem"},
            ],
            schedules=[{"weekday": "monday", "start": "08:00", "end": "22:00"}],
        )

        assert payload["client_id"] == "client-123"
        assert payload["post_id"] == "post-456"
        assert len(payload["access_points"]) == 2
        assert len(payload["schedules"]) == 1

    def test_validate_occurrence_payload_valid(self) -> None:
        """Testa validação de payload de ocorrência válido."""
        service = GuardianSyncService()
        payload = {
            "guardian_id": "guardian-123",
            "occurrence_type": "alarm",
            "severity": "high",
            "client_id": "client-123",
            "title": "Alarme disparado",
            "description": "Alarme do setor A",
            "event_timestamp": "2024-12-30T10:00:00Z",
        }

        valid, error = service.validate_occurrence_payload(payload)

        assert valid is True
        assert error is None

    def test_validate_occurrence_payload_missing_field(self) -> None:
        """Testa validação de payload de ocorrência com campo faltando."""
        service = GuardianSyncService()
        payload = {
            "guardian_id": "guardian-123",
            "occurrence_type": "alarm",
            # severity missing
            "client_id": "client-123",
            "title": "Alarme disparado",
            "description": "Alarme do setor A",
            "event_timestamp": "2024-12-30T10:00:00Z",
        }

        valid, error = service.validate_occurrence_payload(payload)

        assert valid is False
        assert "severity" in error

    def test_validate_occurrence_payload_invalid_severity(self) -> None:
        """Testa validação de payload com gravidade inválida."""
        service = GuardianSyncService()
        payload = {
            "guardian_id": "guardian-123",
            "occurrence_type": "alarm",
            "severity": "invalid",
            "client_id": "client-123",
            "title": "Alarme disparado",
            "description": "Alarme do setor A",
            "event_timestamp": "2024-12-30T10:00:00Z",
        }

        valid, error = service.validate_occurrence_payload(payload)

        assert valid is False
        assert "Gravidade inválida" in error

    def test_validate_access_log_payload_valid(self) -> None:
        """Testa validação de payload de log de acesso válido."""
        service = GuardianSyncService()
        payload = {
            "guardian_id": "guardian-123",
            "log_type": "entry",
            "client_id": "client-123",
            "person_name": "João Silva",
            "event_timestamp": "2024-12-30T10:00:00Z",
        }

        valid, error = service.validate_access_log_payload(payload)

        assert valid is True
        assert error is None

    def test_validate_access_log_payload_invalid_type(self) -> None:
        """Testa validação de payload com tipo inválido."""
        service = GuardianSyncService()
        payload = {
            "guardian_id": "guardian-123",
            "log_type": "invalid_type",
            "client_id": "client-123",
            "person_name": "João Silva",
            "event_timestamp": "2024-12-30T10:00:00Z",
        }

        valid, error = service.validate_access_log_payload(payload)

        assert valid is False
        assert "Tipo de log inválido" in error

    def test_validate_equipment_status_payload_valid(self) -> None:
        """Testa validação de payload de status válido."""
        service = GuardianSyncService()
        payload = {
            "guardian_id": "guardian-123",
            "equipment_id": "cam-001",
            "equipment_type": "camera",
            "equipment_name": "Câmera Principal",
            "status": "online",
            "client_id": "client-123",
        }

        valid, error = service.validate_equipment_status_payload(payload)

        assert valid is True
        assert error is None

    def test_calculate_retry_delay(self) -> None:
        """Testa cálculo de delay de retentativa."""
        service = GuardianSyncService()

        # Primeira tentativa: 60 segundos
        delay1 = service.calculate_retry_delay(0)
        assert delay1 == timedelta(seconds=60)

        # Segunda tentativa: 120 segundos
        delay2 = service.calculate_retry_delay(1)
        assert delay2 == timedelta(seconds=120)

        # Terceira tentativa: 240 segundos
        delay3 = service.calculate_retry_delay(2)
        assert delay3 == timedelta(seconds=240)

        # Máximo: 3600 segundos (1 hora)
        delay_max = service.calculate_retry_delay(10)
        assert delay_max == timedelta(seconds=3600)

    def test_get_sync_priority(self) -> None:
        """Testa priorização de sincronização."""
        service = GuardianSyncService()

        # Ocorrências têm maior prioridade (menor número)
        priority_occ = service.get_sync_priority(
            SyncEntityType.OCCURRENCE,
            SyncDirection.GUARDIAN_TO_ERP,
        )

        # Contratos têm prioridade menor
        priority_contract = service.get_sync_priority(
            SyncEntityType.CONTRACT,
            SyncDirection.ERP_TO_GUARDIAN,
        )

        assert priority_occ < priority_contract

    def test_should_retry_failed(self) -> None:
        """Testa verificação de retentativa para falha."""
        service = GuardianSyncService()

        should = service.should_retry(
            SyncStatus.FAILED,
            retry_count=1,
            max_retries=3,
            error_message="Connection timeout",
        )

        assert should is True

    def test_should_retry_max_reached(self) -> None:
        """Testa que não tenta após máximo."""
        service = GuardianSyncService()

        should = service.should_retry(
            SyncStatus.FAILED,
            retry_count=3,
            max_retries=3,
            error_message="Connection timeout",
        )

        assert should is False

    def test_should_retry_permanent_error(self) -> None:
        """Testa que não tenta para erros permanentes."""
        service = GuardianSyncService()

        should = service.should_retry(
            SyncStatus.FAILED,
            retry_count=0,
            max_retries=3,
            error_message="Unauthorized - Invalid API key",
        )

        assert should is False

    def test_format_sync_summary(self) -> None:
        """Testa formatação de resumo."""
        service = GuardianSyncService()

        summary = service.format_sync_summary(
            total=100,
            completed=95,
            failed=3,
            pending=2,
        )

        assert summary["total"] == 100
        assert summary["completed"] == 95
        assert summary["failed"] == 3
        assert summary["pending"] == 2
        assert summary["success_rate"] == 95.0
        assert summary["health"] == "healthy"

    def test_format_sync_summary_warning(self) -> None:
        """Testa formatação com status de alerta."""
        service = GuardianSyncService()

        summary = service.format_sync_summary(
            total=100,
            completed=85,
            failed=10,
            pending=5,
        )

        assert summary["health"] == "warning"

    def test_format_sync_summary_critical(self) -> None:
        """Testa formatação com status crítico."""
        service = GuardianSyncService()

        summary = service.format_sync_summary(
            total=100,
            completed=70,
            failed=25,
            pending=5,
        )

        assert summary["health"] == "critical"


class TestOccurrenceAnalyzer:
    """Testes para OccurrenceAnalyzer."""

    def test_singleton_instance(self) -> None:
        """Testa que singleton está inicializado."""
        assert occurrence_analyzer is not None

    def test_classify_occurrence_fire(self) -> None:
        """Testa classificação de incêndio."""
        analyzer = OccurrenceAnalyzer()
        result = analyzer.classify_occurrence(
            "Incêndio no setor B",
            "Foi detectada fumaça e chamas no setor B da garagem",
        )

        assert result["suggested_type"] == OccurrenceType.FIRE.value
        assert result["suggested_severity"] == OccurrenceSeverity.CRITICAL.value
        assert result["confidence"] > 0.5

    def test_classify_occurrence_intrusion(self) -> None:
        """Testa classificação de invasão."""
        analyzer = OccurrenceAnalyzer()
        result = analyzer.classify_occurrence(
            "Invasão detectada",
            "Pessoa pulou muro e entrou na área de lazer",
        )

        assert result["suggested_type"] == OccurrenceType.INTRUSION.value
        assert result["suggested_severity"] == OccurrenceSeverity.CRITICAL.value

    def test_classify_occurrence_alarm(self) -> None:
        """Testa classificação de alarme."""
        analyzer = OccurrenceAnalyzer()
        result = analyzer.classify_occurrence(
            "Alarme disparado",
            "Sensor de movimento acionou o alarme na recepção",
        )

        assert result["suggested_type"] == OccurrenceType.ALARM.value
        assert result["suggested_severity"] == OccurrenceSeverity.HIGH.value

    def test_classify_occurrence_with_urgency(self) -> None:
        """Testa classificação com indicadores de urgência."""
        analyzer = OccurrenceAnalyzer()
        result = analyzer.classify_occurrence(
            "Situação urgente - alarme",
            "Alarme disparado - situação grave, precisa de atendimento imediato",
        )

        assert result["has_urgency_indicators"] is True

    def test_calculate_priority_score_critical(self) -> None:
        """Testa cálculo de prioridade para ocorrência crítica."""
        analyzer = OccurrenceAnalyzer()
        result = analyzer.calculate_priority_score(
            occurrence_type=OccurrenceType.FIRE.value,
            severity=OccurrenceSeverity.CRITICAL.value,
            event_timestamp=datetime.utcnow() - timedelta(minutes=2),
            is_recurring=True,
            affected_people_count=5,
        )

        assert result["total_score"] >= 80
        assert result["priority_level"] == "immediate"

    def test_calculate_priority_score_low(self) -> None:
        """Testa cálculo de prioridade para ocorrência baixa."""
        analyzer = OccurrenceAnalyzer()
        result = analyzer.calculate_priority_score(
            occurrence_type=OccurrenceType.VISITOR_INCIDENT.value,
            severity=OccurrenceSeverity.LOW.value,
            event_timestamp=datetime.utcnow() - timedelta(hours=2),
            is_recurring=False,
            affected_people_count=0,
        )

        assert result["total_score"] < 40
        assert result["priority_level"] == "low"

    def test_suggest_actions_fire(self) -> None:
        """Testa sugestão de ações para incêndio."""
        analyzer = OccurrenceAnalyzer()
        actions = analyzer.suggest_actions(
            OccurrenceType.FIRE.value,
            OccurrenceSeverity.CRITICAL.value,
        )

        assert len(actions) > 0
        action_names = [a["action"] for a in actions]
        assert any("Bombeiros" in a for a in action_names)

    def test_suggest_actions_intrusion(self) -> None:
        """Testa sugestão de ações para invasão."""
        analyzer = OccurrenceAnalyzer()
        actions = analyzer.suggest_actions(
            OccurrenceType.INTRUSION.value,
            OccurrenceSeverity.CRITICAL.value,
        )

        assert len(actions) > 0
        action_names = [a["action"] for a in actions]
        assert any("Polícia" in a for a in action_names)

    def test_suggest_actions_medical(self) -> None:
        """Testa sugestão de ações para emergência médica."""
        analyzer = OccurrenceAnalyzer()
        actions = analyzer.suggest_actions(
            OccurrenceType.MEDICAL.value,
            OccurrenceSeverity.HIGH.value,
        )

        assert len(actions) > 0
        action_names = [a["action"] for a in actions]
        assert any("SAMU" in a or "Ambulância" in a for a in action_names)

    def test_suggest_escalation_within_sla(self) -> None:
        """Testa sugestão de escalação dentro do SLA."""
        analyzer = OccurrenceAnalyzer()
        result = analyzer.suggest_escalation(
            OccurrenceType.ALARM.value,
            OccurrenceSeverity.HIGH.value,
            elapsed_minutes=10,
            is_resolved=False,
        )

        assert result["should_escalate"] is False
        assert result["current_sla_status"] == "within_limits"

    def test_suggest_escalation_sla_violated(self) -> None:
        """Testa sugestão de escalação com SLA violado."""
        analyzer = OccurrenceAnalyzer()
        result = analyzer.suggest_escalation(
            OccurrenceType.ALARM.value,
            OccurrenceSeverity.CRITICAL.value,
            elapsed_minutes=30,  # Crítico tem limite de 5 min
            is_resolved=False,
        )

        assert result["should_escalate"] is True
        assert result["current_sla_status"] == "violated"
        assert len(result["escalation_path"]) > 0

    def test_suggest_escalation_resolved(self) -> None:
        """Testa que não escala ocorrência resolvida."""
        analyzer = OccurrenceAnalyzer()
        result = analyzer.suggest_escalation(
            OccurrenceType.ALARM.value,
            OccurrenceSeverity.CRITICAL.value,
            elapsed_minutes=120,
            is_resolved=True,
        )

        assert result["should_escalate"] is False

    def test_detect_patterns_no_occurrences(self) -> None:
        """Testa detecção de padrões sem ocorrências."""
        analyzer = OccurrenceAnalyzer()
        result = analyzer.detect_patterns([])

        assert result["patterns_found"] is False

    def test_detect_patterns_recurring_type(self) -> None:
        """Testa detecção de tipo recorrente."""
        analyzer = OccurrenceAnalyzer()
        occurrences = [
            {"occurrence_type": "alarm", "location": "Portaria"},
            {"occurrence_type": "alarm", "location": "Garagem"},
            {"occurrence_type": "alarm", "location": "Hall"},
            {"occurrence_type": "alarm", "location": "Portaria"},
        ]

        result = analyzer.detect_patterns(occurrences)

        assert result["patterns_found"] is True
        assert "alarm" in result["recurring_types"]

    def test_detect_patterns_hot_spot(self) -> None:
        """Testa detecção de local problemático."""
        analyzer = OccurrenceAnalyzer()
        occurrences = [
            {"occurrence_type": "alarm", "location": "Portaria"},
            {"occurrence_type": "intrusion", "location": "Portaria"},
            {"occurrence_type": "suspicious_activity", "location": "Portaria"},
        ]

        result = analyzer.detect_patterns(occurrences)

        assert result["patterns_found"] is True
        assert "Portaria" in result["hot_spots"]
