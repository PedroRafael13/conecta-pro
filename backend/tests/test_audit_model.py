"""
Testes para os Models do módulo de Auditoria
Sprint 33: Auditoria e Compliance
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from modules.audit.models import (
    AuditLog,
    ComplianceRule,
    ComplianceCheck,
    DataRetention,
    AccessHistory,
    AuditAction,
    AuditCategory,
    AuditSeverity,
    AuditResult,
    ComplianceFramework,
    RuleCategory,
    RuleSeverity,
    RuleStatus,
    CheckType,
    CheckStatus,
    CheckResult,
    DataCategory,
    RetentionPeriod,
    RetentionAction,
    RetentionStatus,
    AccessType,
    AccessResult,
    DeviceType,
    RiskLevel,
)


class TestAuditLog:
    """Testes para AuditLog model."""

    def test_create_audit_log(self):
        """Testa criação de log de auditoria."""
        log = AuditLog(
            event_id="EVT-001",
            action=AuditAction.CREATE,
            category=AuditCategory.DATA_MODIFICATION,
            severity=AuditSeverity.INFO,
            result=AuditResult.SUCCESS,
            description="Registro criado",
            user_email="user@test.com"
        )

        assert log.event_id == "EVT-001"
        assert log.action == AuditAction.CREATE
        assert log.category == AuditCategory.DATA_MODIFICATION
        assert log.severity == AuditSeverity.INFO
        assert log.result == AuditResult.SUCCESS

    def test_create_event_factory(self):
        """Testa factory method para criar evento."""
        log = AuditLog.create_event(
            action=AuditAction.LOGIN,
            category=AuditCategory.AUTHENTICATION,
            description="Login realizado",
            user_email="user@test.com",
            ip_address="192.168.1.1"
        )

        assert log.event_id.startswith("EVT-")
        assert log.action == AuditAction.LOGIN
        assert log.category == AuditCategory.AUTHENTICATION

    def test_mark_for_review(self):
        """Testa marcação para revisão."""
        log = AuditLog(
            event_id="EVT-002",
            action=AuditAction.DELETE,
            category=AuditCategory.DATA_MODIFICATION,
            severity=AuditSeverity.WARNING,
            result=AuditResult.SUCCESS,
            description="Registro deletado"
        )

        log.mark_for_review("Ação sensível")

        assert log.requires_review is True
        assert log.metadata["review_reason"] == "Ação sensível"

    def test_complete_review(self):
        """Testa conclusão de revisão."""
        log = AuditLog(
            event_id="EVT-003",
            action=AuditAction.UPDATE,
            category=AuditCategory.DATA_MODIFICATION,
            severity=AuditSeverity.INFO,
            result=AuditResult.SUCCESS,
            description="Registro atualizado",
            requires_review=True
        )

        reviewer_id = str(uuid4())
        log.complete_review(reviewer_id, "Aprovado")

        assert log.requires_review is False
        assert log.reviewed_by == reviewer_id
        assert log.reviewed_at is not None
        assert log.review_notes == "Aprovado"

    def test_is_security_event(self):
        """Testa verificação de evento de segurança."""
        security_log = AuditLog(
            event_id="EVT-004",
            action=AuditAction.LOGIN_FAILED,
            category=AuditCategory.AUTHENTICATION,
            severity=AuditSeverity.WARNING,
            result=AuditResult.FAILURE,
            description="Login falhou"
        )

        data_log = AuditLog(
            event_id="EVT-005",
            action=AuditAction.CREATE,
            category=AuditCategory.DATA_MODIFICATION,
            severity=AuditSeverity.INFO,
            result=AuditResult.SUCCESS,
            description="Dado criado"
        )

        assert security_log.is_security_event is True
        assert data_log.is_security_event is False

    def test_is_high_severity(self):
        """Testa verificação de alta severidade."""
        error_log = AuditLog(
            event_id="EVT-006",
            action=AuditAction.DELETE,
            category=AuditCategory.DATA_MODIFICATION,
            severity=AuditSeverity.ERROR,
            result=AuditResult.FAILURE,
            description="Erro ao deletar"
        )

        info_log = AuditLog(
            event_id="EVT-007",
            action=AuditAction.READ,
            category=AuditCategory.DATA_ACCESS,
            severity=AuditSeverity.INFO,
            result=AuditResult.SUCCESS,
            description="Dados lidos"
        )

        assert error_log.is_high_severity is True
        assert info_log.is_high_severity is False

    def test_archive(self):
        """Testa arquivamento."""
        log = AuditLog(
            event_id="EVT-008",
            action=AuditAction.CREATE,
            category=AuditCategory.DATA_MODIFICATION,
            severity=AuditSeverity.INFO,
            result=AuditResult.SUCCESS,
            description="Teste"
        )

        log.archive()

        assert log.archived is True
        assert log.archived_at is not None


class TestComplianceRule:
    """Testes para ComplianceRule model."""

    def test_create_compliance_rule(self):
        """Testa criação de regra de compliance."""
        rule = ComplianceRule(
            code="LGPD-001",
            name="Consentimento de Dados",
            framework=ComplianceFramework.LGPD,
            category=RuleCategory.DATA_PRIVACY,
            severity=RuleSeverity.HIGH,
            requirement_text="Obter consentimento explícito"
        )

        assert rule.code == "LGPD-001"
        assert rule.framework == ComplianceFramework.LGPD
        assert rule.category == RuleCategory.DATA_PRIVACY
        assert rule.severity == RuleSeverity.HIGH

    def test_activate_rule(self):
        """Testa ativação de regra."""
        rule = ComplianceRule(
            code="LGPD-002",
            name="Direito ao Esquecimento",
            framework=ComplianceFramework.LGPD,
            category=RuleCategory.DATA_PRIVACY,
            severity=RuleSeverity.CRITICAL,
            requirement_text="Permitir exclusão de dados",
            status=RuleStatus.DRAFT
        )

        rule.activate()

        assert rule.status == RuleStatus.ACTIVE
        assert rule.effective_from is not None

    def test_deprecate_rule(self):
        """Testa depreciação de regra."""
        rule = ComplianceRule(
            code="LGPD-003",
            name="Regra Antiga",
            framework=ComplianceFramework.LGPD,
            category=RuleCategory.DATA_PROTECTION,
            severity=RuleSeverity.MEDIUM,
            requirement_text="Teste",
            status=RuleStatus.ACTIVE
        )

        rule.deprecate("LGPD-004")

        assert rule.status == RuleStatus.DEPRECATED
        assert rule.metadata["replaced_by"] == "LGPD-004"

    def test_record_check(self):
        """Testa registro de verificação."""
        rule = ComplianceRule(
            code="LGPD-004",
            name="Teste Check",
            framework=ComplianceFramework.LGPD,
            category=RuleCategory.DATA_PRIVACY,
            severity=RuleSeverity.MEDIUM,
            requirement_text="Teste"
        )

        rule.record_check(passed=True)
        rule.record_check(passed=False)
        rule.record_check(passed=True)

        assert rule.total_checks == 3
        assert rule.passed_checks == 2
        assert rule.failed_checks == 1
        assert rule.last_violation_at is not None

    def test_compliance_rate(self):
        """Testa taxa de conformidade."""
        rule = ComplianceRule(
            code="LGPD-005",
            name="Taxa Teste",
            framework=ComplianceFramework.LGPD,
            category=RuleCategory.DATA_PRIVACY,
            severity=RuleSeverity.LOW,
            requirement_text="Teste",
            total_checks=10,
            passed_checks=8,
            failed_checks=2
        )

        assert rule.compliance_rate == 80.0

    def test_is_effective(self):
        """Testa verificação se regra está em vigor."""
        now = datetime.utcnow()

        active_rule = ComplianceRule(
            code="LGPD-006",
            name="Regra Ativa",
            framework=ComplianceFramework.LGPD,
            category=RuleCategory.DATA_PRIVACY,
            severity=RuleSeverity.MEDIUM,
            requirement_text="Teste",
            status=RuleStatus.ACTIVE,
            effective_from=now - timedelta(days=30)
        )

        future_rule = ComplianceRule(
            code="LGPD-007",
            name="Regra Futura",
            framework=ComplianceFramework.LGPD,
            category=RuleCategory.DATA_PRIVACY,
            severity=RuleSeverity.MEDIUM,
            requirement_text="Teste",
            status=RuleStatus.ACTIVE,
            effective_from=now + timedelta(days=30)
        )

        assert active_rule.is_effective is True
        assert future_rule.is_effective is False


class TestComplianceCheck:
    """Testes para ComplianceCheck model."""

    def test_create_check_factory(self):
        """Testa factory method para criar verificação."""
        rule_id = str(uuid4())
        check = ComplianceCheck.create_check(
            rule_id=rule_id,
            check_type=CheckType.AUTOMATED
        )

        assert check.check_number.startswith("CHK-")
        assert check.status == CheckStatus.PENDING
        assert str(check.rule_id) == rule_id

    def test_start_check(self):
        """Testa início de verificação."""
        check = ComplianceCheck(
            rule_id=uuid4(),
            check_number="CHK-001",
            check_type=CheckType.MANUAL,
            status=CheckStatus.PENDING
        )

        executor_id = str(uuid4())
        check.start(executor_id)

        assert check.status == CheckStatus.RUNNING
        assert check.started_at is not None
        assert check.executed_by == executor_id

    def test_complete_compliant(self):
        """Testa conclusão como conforme."""
        check = ComplianceCheck(
            rule_id=uuid4(),
            check_number="CHK-002",
            check_type=CheckType.AUTOMATED,
            status=CheckStatus.RUNNING,
            started_at=datetime.utcnow()
        )

        check.complete_compliant(
            evidence={"test": "data"},
            notes="Tudo OK"
        )

        assert check.status == CheckStatus.COMPLETED
        assert check.result == CheckResult.COMPLIANT
        assert check.completed_at is not None
        assert check.duration_seconds is not None
        assert check.evidence_collected == {"test": "data"}

    def test_complete_non_compliant(self):
        """Testa conclusão como não conforme."""
        check = ComplianceCheck(
            rule_id=uuid4(),
            check_number="CHK-003",
            check_type=CheckType.AUTOMATED,
            status=CheckStatus.RUNNING,
            started_at=datetime.utcnow()
        )

        violations = [
            {"field": "email", "severity": "critical"},
            {"field": "phone", "severity": "medium"}
        ]

        deadline = datetime.utcnow() + timedelta(days=7)
        check.complete_non_compliant(
            violations=violations,
            remediation_required=True,
            remediation_deadline=deadline
        )

        assert check.status == CheckStatus.COMPLETED
        assert check.result == CheckResult.NON_COMPLIANT
        assert check.violations_count == 2
        assert check.critical_violations == 1
        assert check.remediation_required is True

    def test_grant_exception(self):
        """Testa concessão de exceção."""
        check = ComplianceCheck(
            rule_id=uuid4(),
            check_number="CHK-004",
            check_type=CheckType.MANUAL,
            status=CheckStatus.COMPLETED,
            result=CheckResult.NON_COMPLIANT
        )

        approver_id = str(uuid4())
        expires = datetime.utcnow() + timedelta(days=30)
        check.grant_exception("Motivo válido", approver_id, expires)

        assert check.exception_granted is True
        assert check.exception_reason == "Motivo válido"
        assert check.exception_approved_by == approver_id

    def test_is_overdue(self):
        """Testa verificação de atraso."""
        overdue_check = ComplianceCheck(
            rule_id=uuid4(),
            check_number="CHK-005",
            check_type=CheckType.AUTOMATED,
            status=CheckStatus.COMPLETED,
            result=CheckResult.NON_COMPLIANT,
            remediation_required=True,
            remediation_deadline=datetime.utcnow() - timedelta(days=1)
        )

        pending_check = ComplianceCheck(
            rule_id=uuid4(),
            check_number="CHK-006",
            check_type=CheckType.AUTOMATED,
            status=CheckStatus.COMPLETED,
            result=CheckResult.NON_COMPLIANT,
            remediation_required=True,
            remediation_deadline=datetime.utcnow() + timedelta(days=1)
        )

        assert overdue_check.is_overdue is True
        assert pending_check.is_overdue is False


class TestDataRetention:
    """Testes para DataRetention model."""

    def test_create_data_retention(self):
        """Testa criação de política de retenção."""
        policy = DataRetention(
            code="RET-001",
            name="Logs de Auditoria",
            data_category=DataCategory.LOGS,
            retention_period=RetentionPeriod.YEARS_5,
            expiration_action=RetentionAction.ARCHIVE
        )

        assert policy.code == "RET-001"
        assert policy.data_category == DataCategory.LOGS
        assert policy.retention_period == RetentionPeriod.YEARS_5
        assert policy.expiration_action == RetentionAction.ARCHIVE

    def test_get_retention_days(self):
        """Testa obtenção de dias de retenção."""
        policy_5y = DataRetention(
            code="RET-002",
            name="5 Anos",
            data_category=DataCategory.FINANCIAL,
            retention_period=RetentionPeriod.YEARS_5,
            expiration_action=RetentionAction.DELETE
        )

        policy_custom = DataRetention(
            code="RET-003",
            name="Custom",
            data_category=DataCategory.TEMPORARY,
            retention_period=RetentionPeriod.CUSTOM,
            retention_days=45,
            expiration_action=RetentionAction.DELETE
        )

        assert policy_5y.get_retention_days() == 1825
        assert policy_custom.get_retention_days() == 45

    def test_activate_policy(self):
        """Testa ativação de política."""
        policy = DataRetention(
            code="RET-004",
            name="Teste Ativação",
            data_category=DataCategory.PERSONAL,
            retention_period=RetentionPeriod.YEARS_2,
            expiration_action=RetentionAction.ANONYMIZE,
            status=RetentionStatus.DRAFT
        )

        policy.activate()

        assert policy.status == RetentionStatus.ACTIVE
        assert policy.effective_from is not None

    def test_record_execution(self):
        """Testa registro de execução."""
        policy = DataRetention(
            code="RET-005",
            name="Teste Execução",
            data_category=DataCategory.LOGS,
            retention_period=RetentionPeriod.DAYS_90,
            expiration_action=RetentionAction.DELETE,
            status=RetentionStatus.ACTIVE,
            schedule_enabled=True
        )

        policy.record_execution(
            records_affected=100,
            deleted=80,
            archived=20,
            storage_freed=1024000
        )

        assert policy.total_executions == 1
        assert policy.records_processed == 100
        assert policy.records_deleted == 80
        assert policy.records_archived == 20
        assert policy.storage_freed_bytes == 1024000
        assert policy.last_execution_at is not None

    def test_legal_hold(self):
        """Testa legal hold."""
        policy = DataRetention(
            code="RET-006",
            name="Legal Hold Test",
            data_category=DataCategory.LEGAL,
            retention_period=RetentionPeriod.YEARS_7,
            expiration_action=RetentionAction.ARCHIVE,
            status=RetentionStatus.ACTIVE
        )

        policy.enable_legal_hold("Investigação em andamento")

        assert policy.legal_hold_enabled is True
        assert "legal_hold_reason" in policy.metadata

        policy.disable_legal_hold("admin@test.com")

        assert policy.legal_hold_enabled is False
        assert "legal_hold_released_by" in policy.metadata

    def test_is_permanent(self):
        """Testa verificação de permanente."""
        permanent = DataRetention(
            code="RET-007",
            name="Permanente",
            data_category=DataCategory.LEGAL,
            retention_period=RetentionPeriod.PERMANENT,
            expiration_action=RetentionAction.REVIEW
        )

        temporary = DataRetention(
            code="RET-008",
            name="Temporário",
            data_category=DataCategory.TEMPORARY,
            retention_period=RetentionPeriod.DAYS_30,
            expiration_action=RetentionAction.DELETE
        )

        assert permanent.is_permanent is True
        assert temporary.is_permanent is False


class TestAccessHistory:
    """Testes para AccessHistory model."""

    def test_create_access_history(self):
        """Testa criação de registro de acesso."""
        access = AccessHistory(
            access_type=AccessType.LOGIN,
            result=AccessResult.SUCCESS,
            user_email="user@test.com",
            ip_address="192.168.1.1"
        )

        assert access.access_type == AccessType.LOGIN
        assert access.result == AccessResult.SUCCESS

    def test_create_login_factory(self):
        """Testa factory method para login."""
        user_id = str(uuid4())
        access = AccessHistory.create_login(
            user_id=user_id,
            user_email="user@test.com",
            ip_address="10.0.0.1",
            result=AccessResult.SUCCESS
        )

        assert access.access_type == AccessType.LOGIN
        assert access.result == AccessResult.SUCCESS
        assert access.user_email == "user@test.com"

    def test_create_api_access_factory(self):
        """Testa factory method para acesso API."""
        access = AccessHistory.create_api_access(
            user_id=None,
            resource_path="/api/v1/users",
            http_method="GET",
            ip_address="192.168.1.100",
            result=AccessResult.SUCCESS,
            response_time_ms=150
        )

        assert access.access_type == AccessType.API_ACCESS
        assert access.resource_path == "/api/v1/users"
        assert access.response_time_ms == 150

    def test_calculate_risk(self):
        """Testa cálculo de risco."""
        low_risk = AccessHistory(
            access_type=AccessType.LOGIN,
            result=AccessResult.SUCCESS,
            ip_address="192.168.1.1",
            device_trusted=True
        )

        high_risk = AccessHistory(
            access_type=AccessType.LOGIN,
            result=AccessResult.FAILURE,
            ip_address="192.168.1.2",
            tor_detected=True,
            vpn_detected=True,
            attempts_count=5,
            anomaly_detected=True
        )

        low_risk.calculate_risk()
        high_risk.calculate_risk()

        assert low_risk.risk_level == RiskLevel.LOW
        assert high_risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert len(high_risk.risk_factors) > 0

    def test_flag_anomaly(self):
        """Testa marcação de anomalia."""
        access = AccessHistory(
            access_type=AccessType.LOGIN,
            result=AccessResult.SUCCESS,
            ip_address="192.168.1.1"
        )

        access.flag_anomaly("impossible_travel")

        assert access.anomaly_detected is True
        assert access.anomaly_type == "impossible_travel"
        assert access.requires_review is True

    def test_trigger_alert(self):
        """Testa disparo de alerta."""
        access = AccessHistory(
            access_type=AccessType.LOGIN_FAILED,
            result=AccessResult.FAILURE,
            ip_address="192.168.1.1"
        )

        access.trigger_alert(["ALERT-001", "ALERT-002"])

        assert access.alert_triggered is True
        assert len(access.alert_ids) == 2
        assert access.requires_review is True

    def test_is_suspicious(self):
        """Testa verificação de suspeito."""
        normal = AccessHistory(
            access_type=AccessType.LOGIN,
            result=AccessResult.SUCCESS,
            ip_address="192.168.1.1",
            risk_level=RiskLevel.LOW
        )

        suspicious = AccessHistory(
            access_type=AccessType.LOGIN,
            result=AccessResult.SUSPICIOUS,
            ip_address="192.168.1.2"
        )

        assert normal.is_suspicious is False
        assert suspicious.is_suspicious is True

    def test_needs_attention(self):
        """Testa verificação de atenção necessária."""
        attention = AccessHistory(
            access_type=AccessType.LOGIN,
            result=AccessResult.FAILURE,
            ip_address="192.168.1.1",
            requires_review=True
        )

        normal = AccessHistory(
            access_type=AccessType.LOGIN,
            result=AccessResult.SUCCESS,
            ip_address="192.168.1.2"
        )

        assert attention.needs_attention is True
        assert normal.needs_attention is False


class TestEnums:
    """Testes para Enums."""

    def test_audit_action_values(self):
        """Testa valores de AuditAction."""
        assert AuditAction.CREATE.value == "create"
        assert AuditAction.LOGIN.value == "login"
        assert AuditAction.BULK_OPERATION.value == "bulk_operation"

    def test_compliance_framework_values(self):
        """Testa valores de ComplianceFramework."""
        assert ComplianceFramework.LGPD.value == "lgpd"
        assert ComplianceFramework.GDPR.value == "gdpr"
        assert ComplianceFramework.SOX.value == "sox"
        assert ComplianceFramework.ISO_27001.value == "iso_27001"

    def test_retention_period_values(self):
        """Testa valores de RetentionPeriod."""
        assert RetentionPeriod.DAYS_30.value == "30_days"
        assert RetentionPeriod.YEARS_5.value == "5_years"
        assert RetentionPeriod.PERMANENT.value == "permanent"

    def test_risk_level_values(self):
        """Testa valores de RiskLevel."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"
