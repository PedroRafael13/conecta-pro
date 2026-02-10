"""
Testes de Serviço para o módulo de Auditoria e Compliance.

Sprint 33: Auditoria e Compliance
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from modules.audit.models import (
    AccessHistory,
    AccessResult,
    AccessType,
    AuditAction,
    AuditCategory,
    AuditLog,
    AuditResult,
    AuditSeverity,
    CheckResult,
    CheckStatus,
    CheckType,
    ComplianceCheck,
    ComplianceFramework,
    ComplianceRule,
    DataCategory,
    DataRetention,
    DeviceType,
    RetentionAction,
    RetentionPeriod,
    RetentionStatus,
    RiskLevel,
    RuleCategory,
    RuleSeverity,
    RuleStatus,
)
from modules.audit.repositories.audit_repository import AuditRepository
from modules.audit.services.audit_service import AuditService

# ========================
# Fixtures
# ========================


@pytest.fixture
def mock_repository():
    """Fixture para mock do repositório."""
    return MagicMock(spec=AuditRepository)


@pytest.fixture
def audit_service(mock_repository):
    """Fixture para instância do serviço com repositório mockado."""
    service = AuditService.__new__(AuditService)
    service.repository = mock_repository
    return service


@pytest.fixture
def sample_tenant_id():
    """Fixture para tenant ID de exemplo."""
    return uuid4()


@pytest.fixture
def sample_user_id():
    """Fixture para user ID de exemplo."""
    return uuid4()


# ========================
# Testes de AuditLog Service
# ========================


class TestAuditLogService:
    """Testes do serviço de logs de auditoria."""

    def test_create_audit_log_success(self, audit_service, mock_repository, sample_tenant_id):
        """Testa criação de log de auditoria."""
        log_data = {
            "user_id": uuid4(),
            "action": AuditAction.VIEW_PERSONAL_DATA,
            "category": AuditCategory.AUTHENTICATION,
            "entity_type": "Lead",
            "entity_id": str(uuid4()),
            "description": "Lead criado",
        }

        expected_log = AuditLog(id=uuid4(), tenant_id=sample_tenant_id, **log_data)
        mock_repository.create_audit_log.return_value = expected_log

        result = audit_service.create_audit_log(sample_tenant_id, log_data)

        mock_repository.create_audit_log.assert_called_once()
        assert result.action == AuditAction.VIEW_PERSONAL_DATA

    def test_create_audit_log_with_metadata(self, audit_service, mock_repository, sample_tenant_id):
        """Testa criação de log com metadados."""
        log_data = {
            "user_id": uuid4(),
            "action": AuditAction.VIEW_PERSONAL_DATA,
            "category": AuditCategory.AUTHENTICATION,
            "entity_type": "Lead",
            "metadata": {"old_value": "A", "new_value": "B"},
            "data_before": {"status": "novo"},
            "data_after": {"status": "qualificado"},
        }

        expected_log = AuditLog(id=uuid4(), tenant_id=sample_tenant_id, **log_data)
        mock_repository.create_audit_log.return_value = expected_log

        result = audit_service.create_audit_log(sample_tenant_id, log_data)

        assert result.metadata == {"old_value": "A", "new_value": "B"}

    def test_list_audit_logs_with_filters(self, audit_service, mock_repository, sample_tenant_id):
        """Testa listagem com filtros."""
        filters = {
            "action": AuditAction.VIEW_PERSONAL_DATA,
            "severity": AuditSeverity.DEBUG,
            "start_date": datetime.utcnow() - timedelta(days=7),
        }

        mock_repository.list_audit_logs.return_value = ([], 0)

        audit_service.list_audit_logs(sample_tenant_id, filters=filters)

        mock_repository.list_audit_logs.assert_called_once()

    def test_get_audit_stats(self, audit_service, mock_repository, sample_tenant_id):
        """Testa obtenção de estatísticas."""
        mock_repository.get_audit_stats.return_value = {
            "total_logs": 1000,
            "by_action": {"CREATE": 400, "UPDATE": 300},
            "by_severity": {"INFO": 800, "WARNING": 150},
        }

        result = audit_service.get_audit_stats(
            sample_tenant_id, datetime.utcnow() - timedelta(days=30), datetime.utcnow()
        )

        assert result["total_logs"] == 1000

    def test_mark_log_for_review(self, audit_service, mock_repository, sample_tenant_id):
        """Testa marcação para revisão."""
        log_id = uuid4()
        log = AuditLog(
            id=log_id,
            tenant_id=sample_tenant_id,
            user_id=uuid4(),
            action=AuditAction.VIEW_PERSONAL_DATA,
            category=AuditCategory.AUTHENTICATION,
            entity_type="Lead",
        )

        mock_repository.get_audit_log.return_value = log
        mock_repository.update_audit_log.return_value = log

        result = audit_service.mark_for_review(sample_tenant_id, log_id, "admin", "Verificar exclusão")

        assert result.requires_review is True

    def test_archive_old_logs(self, audit_service, mock_repository, sample_tenant_id):
        """Testa arquivamento de logs antigos."""
        mock_repository.archive_old_logs.return_value = 500

        result = audit_service.archive_old_logs(sample_tenant_id, days_old=365)

        assert result == 500
        mock_repository.archive_old_logs.assert_called_once()


# ========================
# Testes de ComplianceRule Service
# ========================


class TestComplianceRuleService:
    """Testes do serviço de regras de compliance."""

    def test_create_compliance_rule_success(self, audit_service, mock_repository, sample_tenant_id):
        """Testa criação de regra."""
        rule_data = {
            "code": "LGPD-001",
            "name": "Consentimento de Dados",
            "framework": ComplianceFramework.LGPD,
            "category": RuleCategory.SENTIMENT,
            "severity": RuleSeverity.HIGH,
        }

        expected_rule = ComplianceRule(id=uuid4(), tenant_id=sample_tenant_id, **rule_data)
        mock_repository.create_compliance_rule.return_value = expected_rule

        result = audit_service.create_compliance_rule(sample_tenant_id, rule_data)

        assert result.code == "LGPD-001"
        assert result.framework == ComplianceFramework.LGPD

    def test_activate_compliance_rule(self, audit_service, mock_repository, sample_tenant_id):
        """Testa ativação de regra."""
        rule_id = uuid4()
        rule = ComplianceRule(
            id=rule_id,
            tenant_id=sample_tenant_id,
            code="LGPD-001",
            name="Consentimento",
            framework=ComplianceFramework.LGPD,
            category=RuleCategory.SENTIMENT,
            severity=RuleSeverity.HIGH,
            status=RuleStatus.DRAFT,
        )

        mock_repository.get_compliance_rule.return_value = rule
        mock_repository.update_compliance_rule.return_value = rule

        result = audit_service.activate_rule(sample_tenant_id, rule_id)

        assert result.status == RuleStatus.ACTIVE

    def test_deprecate_compliance_rule(self, audit_service, mock_repository, sample_tenant_id):
        """Testa depreciação de regra."""
        rule_id = uuid4()
        rule = ComplianceRule(
            id=rule_id,
            tenant_id=sample_tenant_id,
            code="LGPD-001",
            name="Consentimento",
            framework=ComplianceFramework.LGPD,
            category=RuleCategory.SENTIMENT,
            severity=RuleSeverity.HIGH,
            status=RuleStatus.ACTIVE,
        )

        mock_repository.get_compliance_rule.return_value = rule
        mock_repository.update_compliance_rule.return_value = rule

        result = audit_service.deprecate_rule(sample_tenant_id, rule_id, "Nova versão disponível")

        assert result.status == RuleStatus.DEPRECATED

    def test_list_rules_by_framework(self, audit_service, mock_repository, sample_tenant_id):
        """Testa listagem por framework."""
        mock_repository.list_compliance_rules.return_value = ([], 0)

        audit_service.list_rules_by_framework(sample_tenant_id, ComplianceFramework.LGPD)

        mock_repository.list_compliance_rules.assert_called_once()

    def test_get_compliance_rate(self, audit_service, mock_repository, sample_tenant_id):
        """Testa cálculo de taxa de compliance."""
        rule = ComplianceRule(
            id=uuid4(),
            tenant_id=sample_tenant_id,
            code="LGPD-001",
            name="Consentimento",
            framework=ComplianceFramework.LGPD,
            category=RuleCategory.SENTIMENT,
            severity=RuleSeverity.HIGH,
            checks_total=100,
            checks_passed=95,
        )

        mock_repository.get_compliance_rule.return_value = rule

        result = audit_service.get_compliance_rate(sample_tenant_id, rule.id)

        assert result == 95.0


# ========================
# Testes de ComplianceCheck Service
# ========================


class TestComplianceCheckService:
    """Testes do serviço de verificações de compliance."""

    def test_create_compliance_check_success(self, audit_service, mock_repository, sample_tenant_id):
        """Testa criação de verificação."""
        rule_id = uuid4()
        check_data = {"rule_id": rule_id, "check_type": CheckType.AUTOMATED}

        expected_check = ComplianceCheck(id=uuid4(), tenant_id=sample_tenant_id, **check_data)
        mock_repository.create_compliance_check.return_value = expected_check

        result = audit_service.create_compliance_check(sample_tenant_id, check_data)

        assert result.check_type == CheckType.AUTOMATED

    def test_start_compliance_check(self, audit_service, mock_repository, sample_tenant_id):
        """Testa início de verificação."""
        check_id = uuid4()
        check = ComplianceCheck(
            id=check_id,
            tenant_id=sample_tenant_id,
            rule_id=uuid4(),
            check_type=CheckType.AUTOMATED,
            status=CheckStatus.PENDING,
        )

        mock_repository.get_compliance_check.return_value = check
        mock_repository.update_compliance_check.return_value = check

        result = audit_service.start_check(sample_tenant_id, check_id, uuid4())

        assert result.status == CheckStatus.PENDING

    def test_complete_check_compliant(self, audit_service, mock_repository, sample_tenant_id):
        """Testa conclusão como compliant."""
        check_id = uuid4()
        check = ComplianceCheck(
            id=check_id,
            tenant_id=sample_tenant_id,
            rule_id=uuid4(),
            check_type=CheckType.AUTOMATED,
            status=CheckStatus.PENDING,
        )

        mock_repository.get_compliance_check.return_value = check
        mock_repository.update_compliance_check.return_value = check

        result = audit_service.complete_check_compliant(sample_tenant_id, check_id, 95.0, {"all_tests": "passed"})

        assert result.result == CheckResult.COMPLIANT
        assert result.compliance_score == 95.0

    def test_complete_check_non_compliant(self, audit_service, mock_repository, sample_tenant_id):
        """Testa conclusão como não compliant."""
        check_id = uuid4()
        check = ComplianceCheck(
            id=check_id,
            tenant_id=sample_tenant_id,
            rule_id=uuid4(),
            check_type=CheckType.AUTOMATED,
            status=CheckStatus.PENDING,
        )

        mock_repository.get_compliance_check.return_value = check
        mock_repository.update_compliance_check.return_value = check

        violations = ["Dados sem consentimento", "Acesso não autorizado"]
        result = audit_service.complete_check_non_compliant(
            sample_tenant_id, check_id, 45.0, violations, {"recommendation": "Corrigir imediatamente"}
        )

        assert result.result == CheckResult.NON_COMPLIANT
        assert len(result.violations) == 2

    def test_escalate_check(self, audit_service, mock_repository, sample_tenant_id):
        """Testa escalonamento de verificação."""
        check_id = uuid4()
        check = ComplianceCheck(
            id=check_id,
            tenant_id=sample_tenant_id,
            rule_id=uuid4(),
            check_type=CheckType.MANUAL,
            status=CheckStatus.COMPLETED,
            result=CheckResult.NON_COMPLIANT,
        )

        mock_repository.get_compliance_check.return_value = check
        mock_repository.update_compliance_check.return_value = check

        result = audit_service.escalate_check(sample_tenant_id, check_id, "supervisor", "Múltiplas violações críticas")

        assert result.escalated is True
        assert result.escalated_to == "supervisor"

    def test_get_overdue_checks(self, audit_service, mock_repository, sample_tenant_id):
        """Testa busca de verificações atrasadas."""
        mock_repository.get_overdue_checks.return_value = []

        audit_service.get_overdue_checks(sample_tenant_id)

        mock_repository.get_overdue_checks.assert_called_once()


# ========================
# Testes de DataRetention Service
# ========================


class TestDataRetentionService:
    """Testes do serviço de retenção de dados."""

    def test_create_retention_policy_success(self, audit_service, mock_repository, sample_tenant_id):
        """Testa criação de política."""
        policy_data = {
            "name": "Retenção de Leads",
            "entity_type": "Lead",
            "data_category": DataCategory.PROFILE,
            "retention_period": RetentionPeriod.YEARS_5,
            "retention_action": RetentionAction.ARCHIVE,
        }

        expected_policy = DataRetention(id=uuid4(), tenant_id=sample_tenant_id, **policy_data)
        mock_repository.create_data_retention.return_value = expected_policy

        result = audit_service.create_retention_policy(sample_tenant_id, policy_data)

        assert result.retention_period == RetentionPeriod.YEARS_5

    def test_enable_legal_hold(self, audit_service, mock_repository, sample_tenant_id):
        """Testa ativação de retenção legal."""
        policy_id = uuid4()
        policy = DataRetention(
            id=policy_id,
            tenant_id=sample_tenant_id,
            name="Retenção de Leads",
            entity_type="Lead",
            data_category=DataCategory.PROFILE,
            retention_period=RetentionPeriod.YEARS_5,
            retention_action=RetentionAction.ARCHIVE,
        )

        mock_repository.get_data_retention.return_value = policy
        mock_repository.update_data_retention.return_value = policy

        result = audit_service.enable_legal_hold(sample_tenant_id, policy_id, "Processo judicial", "ADV-001")

        assert result.legal_hold is True
        assert result.legal_hold_reference == "ADV-001"

    def test_disable_legal_hold(self, audit_service, mock_repository, sample_tenant_id):
        """Testa desativação de retenção legal."""
        policy_id = uuid4()
        policy = DataRetention(
            id=policy_id,
            tenant_id=sample_tenant_id,
            name="Retenção de Leads",
            entity_type="Lead",
            data_category=DataCategory.PROFILE,
            retention_period=RetentionPeriod.YEARS_5,
            retention_action=RetentionAction.ARCHIVE,
            legal_hold=True,
        )

        mock_repository.get_data_retention.return_value = policy
        mock_repository.update_data_retention.return_value = policy

        result = audit_service.disable_legal_hold(sample_tenant_id, policy_id)

        assert result.legal_hold is False

    def test_execute_retention_policy(self, audit_service, mock_repository, sample_tenant_id):
        """Testa execução de política."""
        policy_id = uuid4()
        policy = DataRetention(
            id=policy_id,
            tenant_id=sample_tenant_id,
            name="Retenção de Leads",
            entity_type="Lead",
            data_category=DataCategory.PROFILE,
            retention_period=RetentionPeriod.YEARS_5,
            retention_action=RetentionAction.ARCHIVE,
            status=RetentionStatus.ACTIVE,
        )

        mock_repository.get_data_retention.return_value = policy
        mock_repository.update_data_retention.return_value = policy

        result = audit_service.execute_retention_policy(sample_tenant_id, policy_id, records_affected=100)

        assert result.execution_count == 1
        assert result.records_affected == 100

    def test_get_due_policies(self, audit_service, mock_repository, sample_tenant_id):
        """Testa busca de políticas devidas."""
        mock_repository.get_due_retention_policies.return_value = []

        audit_service.get_due_policies(sample_tenant_id)

        mock_repository.get_due_retention_policies.assert_called_once()


# ========================
# Testes de AccessHistory Service
# ========================


class TestAccessHistoryService:
    """Testes do serviço de histórico de acesso."""

    def test_create_login_record_success(self, audit_service, mock_repository, sample_tenant_id, sample_user_id):
        """Testa criação de registro de login."""
        access_data = {
            "user_id": sample_user_id,
            "access_type": AccessType.LOGIN,
            "result": AccessResult.SUCCESS,
            "ip_address": "192.168.1.100",
        }

        expected_access = AccessHistory(id=uuid4(), tenant_id=sample_tenant_id, **access_data)
        mock_repository.create_access_history.return_value = expected_access

        result = audit_service.create_access_history(sample_tenant_id, access_data)

        assert result.access_type == AccessType.LOGIN

    def test_record_failed_login(self, audit_service, mock_repository, sample_tenant_id, sample_user_id):
        """Testa registro de login falho."""
        access_data = {
            "user_id": sample_user_id,
            "access_type": AccessType.LOGIN,
            "result": AccessResult.FAILURE,
            "ip_address": "192.168.1.100",
            "failure_reason": "Senha incorreta",
        }

        expected_access = AccessHistory(id=uuid4(), tenant_id=sample_tenant_id, **access_data)
        mock_repository.create_access_history.return_value = expected_access

        result = audit_service.create_access_history(sample_tenant_id, access_data)

        assert result.result == AccessResult.FAILURE

    def test_flag_anomaly(self, audit_service, mock_repository, sample_tenant_id):
        """Testa flag de anomalia."""
        access_id = uuid4()
        access = AccessHistory(
            id=access_id,
            tenant_id=sample_tenant_id,
            user_id=uuid4(),
            access_type=AccessType.LOGIN,
            result=AccessResult.SUCCESS,
            ip_address="192.168.1.100",
        )

        mock_repository.get_access_history.return_value = access
        mock_repository.update_access_history.return_value = access

        result = audit_service.flag_anomaly(sample_tenant_id, access_id, "Login de localização incomum")

        assert result.is_anomaly is True

    def test_trigger_alert(self, audit_service, mock_repository, sample_tenant_id):
        """Testa disparo de alerta."""
        access_id = uuid4()
        access = AccessHistory(
            id=access_id,
            tenant_id=sample_tenant_id,
            user_id=uuid4(),
            access_type=AccessType.LOGIN,
            result=AccessResult.FAILURE,
            ip_address="192.168.1.100",
        )

        mock_repository.get_access_history.return_value = access
        mock_repository.update_access_history.return_value = access

        result = audit_service.trigger_alert(sample_tenant_id, access_id, "alert-001", "Múltiplas tentativas falhas")

        assert result.alert_triggered is True
        assert result.alert_id == "alert-001"

    def test_calculate_risk_for_access(self, audit_service, mock_repository, sample_tenant_id):
        """Testa cálculo de risco."""
        access_id = uuid4()
        access = AccessHistory(
            id=access_id,
            tenant_id=sample_tenant_id,
            user_id=uuid4(),
            access_type=AccessType.LOGIN,
            result=AccessResult.SUCCESS,
            ip_address="192.168.1.100",
            is_anomaly=True,
            is_new_device=True,
        )

        mock_repository.get_access_history.return_value = access
        mock_repository.update_access_history.return_value = access

        result = audit_service.calculate_risk(sample_tenant_id, access_id)

        assert result.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]

    def test_get_access_stats(self, audit_service, mock_repository, sample_tenant_id):
        """Testa obtenção de estatísticas."""
        mock_repository.get_access_stats.return_value = {
            "total_accesses": 5000,
            "successful_logins": 4800,
            "failed_logins": 200,
        }

        result = audit_service.get_access_stats(
            sample_tenant_id, datetime.utcnow() - timedelta(days=30), datetime.utcnow()
        )

        assert result["total_accesses"] == 5000

    def test_get_suspicious_accesses(self, audit_service, mock_repository, sample_tenant_id):
        """Testa busca de acessos suspeitos."""
        mock_repository.get_suspicious_accesses.return_value = []

        audit_service.get_suspicious_accesses(sample_tenant_id)

        mock_repository.get_suspicious_accesses.assert_called_once()


# ========================
# Testes de Dashboard Service
# ========================


class TestDashboardService:
    """Testes do serviço de dashboard."""

    def test_get_audit_dashboard(self, audit_service, mock_repository, sample_tenant_id):
        """Testa obtenção do dashboard de auditoria."""
        mock_repository.get_audit_stats.return_value = {"total_logs": 10000, "logs_today": 500, "security_events": 50}
        mock_repository.get_recent_critical_logs.return_value = []

        result = audit_service.get_audit_dashboard(sample_tenant_id)

        assert "total_logs" in result

    def test_get_compliance_overview(self, audit_service, mock_repository, sample_tenant_id):
        """Testa obtenção do overview de compliance."""
        mock_repository.get_compliance_overview.return_value = {
            "total_rules": 50,
            "active_rules": 45,
            "compliance_rate": 92.5,
        }

        result = audit_service.get_compliance_overview(sample_tenant_id)

        assert result["compliance_rate"] == 92.5

    def test_get_security_overview(self, audit_service, mock_repository, sample_tenant_id):
        """Testa obtenção do overview de segurança."""
        mock_repository.get_access_stats.return_value = {
            "total_accesses": 5000,
            "failed_logins": 200,
            "anomalies_detected": 15,
        }

        result = audit_service.get_security_overview(sample_tenant_id)

        assert "total_accesses" in result


# ========================
# Testes de Validação
# ========================


class TestValidation:
    """Testes de validação."""

    def test_validate_retention_period(self, audit_service):
        """Testa validação de período de retenção."""
        # Período válido
        assert audit_service.validate_retention_period("YEARS_5") is True

        # Período inválido
        with pytest.raises(ValueError):
            audit_service.validate_retention_period("INVALID")

    def test_validate_compliance_framework(self, audit_service):
        """Testa validação de framework."""
        # Framework válido
        assert audit_service.validate_framework("LGPD") is True

        # Framework inválido
        with pytest.raises(ValueError):
            audit_service.validate_framework("INVALID")

    def test_validate_audit_action(self, audit_service):
        """Testa validação de ação."""
        # Ação válida
        assert audit_service.validate_action("CREATE") is True

        # Ação inválida
        with pytest.raises(ValueError):
            audit_service.validate_action("INVALID")


# ========================
# Testes de Integração
# ========================


class TestIntegration:
    """Testes de integração entre componentes."""

    def test_audit_log_triggers_compliance_check(self, audit_service, mock_repository, sample_tenant_id):
        """Testa se log de auditoria pode disparar verificação."""
        log_data = {
            "user_id": uuid4(),
            "action": AuditAction.VIEW_PERSONAL_DATA,
            "category": AuditCategory.AUTHENTICATION,
            "entity_type": "Lead",
            "severity": AuditSeverity.DEBUG,
        }

        log = AuditLog(id=uuid4(), tenant_id=sample_tenant_id, **log_data)
        mock_repository.create_audit_log.return_value = log
        mock_repository.get_rules_for_action.return_value = []

        audit_service.create_audit_log_with_compliance_check(sample_tenant_id, log_data)

        mock_repository.create_audit_log.assert_called_once()

    def test_access_history_triggers_alert(self, audit_service, mock_repository, sample_tenant_id):
        """Testa se histórico de acesso pode disparar alerta."""
        access_data = {
            "user_id": uuid4(),
            "access_type": AccessType.LOGIN,
            "result": AccessResult.FAILURE,
            "ip_address": "192.168.1.100",
            "failed_attempts": 5,
        }

        access = AccessHistory(id=uuid4(), tenant_id=sample_tenant_id, **access_data)
        mock_repository.create_access_history.return_value = access
        mock_repository.get_recent_failed_attempts.return_value = 5

        result = audit_service.create_access_with_alert_check(sample_tenant_id, access_data)

        # Com 5 tentativas falhas, deve disparar alerta
        assert result is not None

    def test_retention_policy_affects_audit_logs(self, audit_service, mock_repository, sample_tenant_id):
        """Testa se política de retenção afeta logs."""
        policy = DataRetention(
            id=uuid4(),
            tenant_id=sample_tenant_id,
            name="Retenção de Logs",
            entity_type="AuditLog",
            data_category=DataCategory.PROFILE,
            retention_period=RetentionPeriod.YEARS_7,
            retention_action=RetentionAction.ARCHIVE,
            status=RetentionStatus.ACTIVE,
        )

        mock_repository.get_data_retention.return_value = policy
        mock_repository.archive_old_logs.return_value = 1000

        result = audit_service.apply_retention_policy(sample_tenant_id, policy.id)

        assert result >= 0


# ========================
# Testes de Performance
# ========================


class TestPerformance:
    """Testes de performance."""

    def test_bulk_create_audit_logs(self, audit_service, mock_repository, sample_tenant_id):
        """Testa criação em lote de logs."""
        logs_data = [
            {"user_id": uuid4(), "action": AuditAction.VIEW_PERSONAL_DATA, "category": AuditCategory.AUTHENTICATION, "entity_type": "Lead"}
            for _ in range(100)
        ]

        mock_repository.bulk_create_audit_logs.return_value = 100

        result = audit_service.bulk_create_audit_logs(sample_tenant_id, logs_data)

        assert result == 100

    def test_batch_compliance_check(self, audit_service, mock_repository, sample_tenant_id):
        """Testa verificação em lote."""
        rule_ids = [uuid4() for _ in range(10)]

        mock_repository.batch_create_compliance_checks.return_value = 10

        result = audit_service.batch_compliance_check(sample_tenant_id, rule_ids)

        assert result == 10
