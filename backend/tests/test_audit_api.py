"""
Testes de API para o módulo de Auditoria e Compliance.

Sprint 33: Auditoria e Compliance
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from uuid import uuid4

from modules.audit.models import (
    AuditLog, AuditAction, AuditCategory, AuditSeverity, AuditResult,
    ComplianceRule, ComplianceFramework, RuleCategory, RuleSeverity, RuleStatus,
    ComplianceCheck, CheckType, CheckStatus, CheckResult,
    DataRetention, DataCategory, RetentionPeriod, RetentionAction, RetentionStatus,
    AccessHistory, AccessType, AccessResult, DeviceType, RiskLevel
)
from modules.audit.schemas import (
    AuditLogResponse, AuditLogList, AuditLogStats,
    ComplianceRuleResponse, ComplianceRuleList,
    ComplianceCheckResponse, ComplianceCheckList,
    DataRetentionResponse, DataRetentionList,
    AccessHistoryResponse, AccessHistoryList, AccessHistoryStats
)


# ========================
# Fixtures
# ========================

@pytest.fixture
def mock_audit_service():
    """Fixture para mock do serviço de auditoria."""
    return MagicMock()


@pytest.fixture
def sample_audit_log():
    """Fixture para log de auditoria de exemplo."""
    return AuditLog(
        id=uuid4(),
        tenant_id=uuid4(),
        user_id=uuid4(),
        action=AuditAction.CREATE,
        category=AuditCategory.DATA,
        entity_type="Lead",
        entity_id=str(uuid4()),
        description="Lead criado",
        severity=AuditSeverity.INFO,
        result=AuditResult.SUCCESS,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_compliance_rule():
    """Fixture para regra de compliance de exemplo."""
    return ComplianceRule(
        id=uuid4(),
        tenant_id=uuid4(),
        code="LGPD-001",
        name="Consentimento de Dados",
        description="Verificar consentimento para coleta de dados",
        framework=ComplianceFramework.LGPD,
        category=RuleCategory.DATA_PROTECTION,
        severity=RuleSeverity.HIGH,
        status=RuleStatus.ACTIVE,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_compliance_check():
    """Fixture para verificação de compliance de exemplo."""
    rule_id = uuid4()
    return ComplianceCheck(
        id=uuid4(),
        tenant_id=uuid4(),
        rule_id=rule_id,
        check_type=CheckType.AUTOMATED,
        status=CheckStatus.COMPLETED,
        result=CheckResult.COMPLIANT,
        compliance_score=95.0,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_data_retention():
    """Fixture para política de retenção de exemplo."""
    return DataRetention(
        id=uuid4(),
        tenant_id=uuid4(),
        name="Retenção de Leads",
        entity_type="Lead",
        data_category=DataCategory.CUSTOMER,
        retention_period=RetentionPeriod.YEARS_5,
        retention_action=RetentionAction.ARCHIVE,
        status=RetentionStatus.ACTIVE,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_access_history():
    """Fixture para histórico de acesso de exemplo."""
    return AccessHistory(
        id=uuid4(),
        tenant_id=uuid4(),
        user_id=uuid4(),
        access_type=AccessType.LOGIN,
        result=AccessResult.SUCCESS,
        ip_address="192.168.1.100",
        device_type=DeviceType.DESKTOP,
        risk_level=RiskLevel.LOW,
        created_at=datetime.utcnow()
    )


# ========================
# Testes de Audit Logs
# ========================

class TestAuditLogAPI:
    """Testes dos endpoints de logs de auditoria."""

    @pytest.mark.asyncio
    async def test_list_audit_logs_success(self, mock_audit_service, sample_audit_log):
        """Testa listagem de logs com sucesso."""
        mock_audit_service.list_audit_logs = AsyncMock(return_value={
            "items": [sample_audit_log],
            "total": 1,
            "page": 1,
            "page_size": 20
        })

        with patch('modules.audit.controllers.audit_controller.get_audit_service',
                   return_value=mock_audit_service):
            result = await mock_audit_service.list_audit_logs(
                tenant_id=sample_audit_log.tenant_id,
                page=1,
                page_size=20
            )

        assert result["total"] == 1
        assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_list_audit_logs_with_filters(self, mock_audit_service):
        """Testa listagem de logs com filtros."""
        mock_audit_service.list_audit_logs = AsyncMock(return_value={
            "items": [],
            "total": 0,
            "page": 1,
            "page_size": 20
        })

        filters = {
            "action": AuditAction.CREATE,
            "category": AuditCategory.DATA,
            "severity": AuditSeverity.HIGH
        }

        result = await mock_audit_service.list_audit_logs(
            tenant_id=uuid4(),
            filters=filters,
            page=1,
            page_size=20
        )

        assert result["total"] == 0
        mock_audit_service.list_audit_logs.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_audit_log_success(self, mock_audit_service, sample_audit_log):
        """Testa busca de log por ID."""
        mock_audit_service.get_audit_log = AsyncMock(return_value=sample_audit_log)

        result = await mock_audit_service.get_audit_log(
            tenant_id=sample_audit_log.tenant_id,
            log_id=sample_audit_log.id
        )

        assert result.id == sample_audit_log.id
        assert result.action == AuditAction.CREATE

    @pytest.mark.asyncio
    async def test_get_audit_log_not_found(self, mock_audit_service):
        """Testa busca de log inexistente."""
        mock_audit_service.get_audit_log = AsyncMock(return_value=None)

        result = await mock_audit_service.get_audit_log(
            tenant_id=uuid4(),
            log_id=uuid4()
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_create_audit_log_success(self, mock_audit_service, sample_audit_log):
        """Testa criação de log de auditoria."""
        mock_audit_service.create_audit_log = AsyncMock(return_value=sample_audit_log)

        result = await mock_audit_service.create_audit_log(
            tenant_id=sample_audit_log.tenant_id,
            data={
                "user_id": str(sample_audit_log.user_id),
                "action": "CREATE",
                "category": "DATA",
                "entity_type": "Lead",
                "description": "Lead criado"
            }
        )

        assert result.action == AuditAction.CREATE

    @pytest.mark.asyncio
    async def test_get_audit_stats(self, mock_audit_service):
        """Testa obtenção de estatísticas de auditoria."""
        mock_audit_service.get_audit_stats = AsyncMock(return_value={
            "total_logs": 1000,
            "by_action": {"CREATE": 400, "UPDATE": 300, "DELETE": 100, "READ": 200},
            "by_category": {"DATA": 500, "AUTH": 300, "SYSTEM": 200},
            "by_severity": {"INFO": 700, "WARNING": 200, "ERROR": 80, "CRITICAL": 20}
        })

        result = await mock_audit_service.get_audit_stats(
            tenant_id=uuid4(),
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow()
        )

        assert result["total_logs"] == 1000
        assert "by_action" in result

    @pytest.mark.asyncio
    async def test_mark_audit_log_for_review(self, mock_audit_service, sample_audit_log):
        """Testa marcação de log para revisão."""
        sample_audit_log.mark_for_review("admin", "Verificar ação suspeita")
        mock_audit_service.update_audit_log = AsyncMock(return_value=sample_audit_log)

        assert sample_audit_log.requires_review is True
        assert sample_audit_log.review_notes == "Verificar ação suspeita"


# ========================
# Testes de Compliance Rules
# ========================

class TestComplianceRuleAPI:
    """Testes dos endpoints de regras de compliance."""

    @pytest.mark.asyncio
    async def test_list_compliance_rules_success(self, mock_audit_service, sample_compliance_rule):
        """Testa listagem de regras com sucesso."""
        mock_audit_service.list_compliance_rules = AsyncMock(return_value={
            "items": [sample_compliance_rule],
            "total": 1,
            "page": 1,
            "page_size": 20
        })

        result = await mock_audit_service.list_compliance_rules(
            tenant_id=sample_compliance_rule.tenant_id,
            page=1,
            page_size=20
        )

        assert result["total"] == 1
        assert result["items"][0].framework == ComplianceFramework.LGPD

    @pytest.mark.asyncio
    async def test_create_compliance_rule_success(self, mock_audit_service, sample_compliance_rule):
        """Testa criação de regra de compliance."""
        mock_audit_service.create_compliance_rule = AsyncMock(return_value=sample_compliance_rule)

        result = await mock_audit_service.create_compliance_rule(
            tenant_id=sample_compliance_rule.tenant_id,
            data={
                "code": "LGPD-001",
                "name": "Consentimento de Dados",
                "framework": "LGPD",
                "category": "DATA_PROTECTION",
                "severity": "HIGH"
            }
        )

        assert result.code == "LGPD-001"
        assert result.framework == ComplianceFramework.LGPD

    @pytest.mark.asyncio
    async def test_update_compliance_rule_success(self, mock_audit_service, sample_compliance_rule):
        """Testa atualização de regra."""
        sample_compliance_rule.name = "Consentimento Atualizado"
        mock_audit_service.update_compliance_rule = AsyncMock(return_value=sample_compliance_rule)

        result = await mock_audit_service.update_compliance_rule(
            tenant_id=sample_compliance_rule.tenant_id,
            rule_id=sample_compliance_rule.id,
            data={"name": "Consentimento Atualizado"}
        )

        assert result.name == "Consentimento Atualizado"

    @pytest.mark.asyncio
    async def test_activate_compliance_rule(self, mock_audit_service, sample_compliance_rule):
        """Testa ativação de regra."""
        sample_compliance_rule.status = RuleStatus.DRAFT
        sample_compliance_rule.activate()
        mock_audit_service.update_compliance_rule = AsyncMock(return_value=sample_compliance_rule)

        assert sample_compliance_rule.status == RuleStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_deprecate_compliance_rule(self, mock_audit_service, sample_compliance_rule):
        """Testa depreciação de regra."""
        sample_compliance_rule.deprecate("Nova versão disponível")
        mock_audit_service.update_compliance_rule = AsyncMock(return_value=sample_compliance_rule)

        assert sample_compliance_rule.status == RuleStatus.DEPRECATED


# ========================
# Testes de Compliance Checks
# ========================

class TestComplianceCheckAPI:
    """Testes dos endpoints de verificações de compliance."""

    @pytest.mark.asyncio
    async def test_list_compliance_checks_success(self, mock_audit_service, sample_compliance_check):
        """Testa listagem de verificações."""
        mock_audit_service.list_compliance_checks = AsyncMock(return_value={
            "items": [sample_compliance_check],
            "total": 1,
            "page": 1,
            "page_size": 20
        })

        result = await mock_audit_service.list_compliance_checks(
            tenant_id=sample_compliance_check.tenant_id,
            page=1,
            page_size=20
        )

        assert result["total"] == 1
        assert result["items"][0].result == CheckResult.COMPLIANT

    @pytest.mark.asyncio
    async def test_create_compliance_check_success(self, mock_audit_service, sample_compliance_check):
        """Testa criação de verificação."""
        mock_audit_service.create_compliance_check = AsyncMock(return_value=sample_compliance_check)

        result = await mock_audit_service.create_compliance_check(
            tenant_id=sample_compliance_check.tenant_id,
            data={
                "rule_id": str(sample_compliance_check.rule_id),
                "check_type": "AUTOMATED"
            }
        )

        assert result.check_type == CheckType.AUTOMATED

    @pytest.mark.asyncio
    async def test_complete_compliance_check_compliant(
        self, mock_audit_service, sample_compliance_check
    ):
        """Testa conclusão de verificação como compliant."""
        sample_compliance_check.status = CheckStatus.IN_PROGRESS
        sample_compliance_check.complete_compliant(95.0, {"test": "passed"})
        mock_audit_service.update_compliance_check = AsyncMock(
            return_value=sample_compliance_check
        )

        assert sample_compliance_check.result == CheckResult.COMPLIANT
        assert sample_compliance_check.compliance_score == 95.0

    @pytest.mark.asyncio
    async def test_complete_compliance_check_non_compliant(
        self, mock_audit_service, sample_compliance_check
    ):
        """Testa conclusão de verificação como não compliant."""
        sample_compliance_check.status = CheckStatus.IN_PROGRESS
        sample_compliance_check.complete_non_compliant(
            45.0,
            ["Violação 1", "Violação 2"],
            {"recommendation": "Corrigir"}
        )
        mock_audit_service.update_compliance_check = AsyncMock(
            return_value=sample_compliance_check
        )

        assert sample_compliance_check.result == CheckResult.NON_COMPLIANT
        assert len(sample_compliance_check.violations) == 2

    @pytest.mark.asyncio
    async def test_escalate_compliance_check(self, mock_audit_service, sample_compliance_check):
        """Testa escalonamento de verificação."""
        sample_compliance_check.result = CheckResult.NON_COMPLIANT
        sample_compliance_check.escalate("supervisor", "Múltiplas violações críticas")
        mock_audit_service.update_compliance_check = AsyncMock(
            return_value=sample_compliance_check
        )

        assert sample_compliance_check.escalated is True
        assert sample_compliance_check.escalated_to == "supervisor"


# ========================
# Testes de Data Retention
# ========================

class TestDataRetentionAPI:
    """Testes dos endpoints de retenção de dados."""

    @pytest.mark.asyncio
    async def test_list_data_retention_policies_success(
        self, mock_audit_service, sample_data_retention
    ):
        """Testa listagem de políticas."""
        mock_audit_service.list_data_retention_policies = AsyncMock(return_value={
            "items": [sample_data_retention],
            "total": 1,
            "page": 1,
            "page_size": 20
        })

        result = await mock_audit_service.list_data_retention_policies(
            tenant_id=sample_data_retention.tenant_id,
            page=1,
            page_size=20
        )

        assert result["total"] == 1
        assert result["items"][0].data_category == DataCategory.CUSTOMER

    @pytest.mark.asyncio
    async def test_create_data_retention_policy_success(
        self, mock_audit_service, sample_data_retention
    ):
        """Testa criação de política."""
        mock_audit_service.create_data_retention_policy = AsyncMock(
            return_value=sample_data_retention
        )

        result = await mock_audit_service.create_data_retention_policy(
            tenant_id=sample_data_retention.tenant_id,
            data={
                "name": "Retenção de Leads",
                "entity_type": "Lead",
                "data_category": "CUSTOMER",
                "retention_period": "YEARS_5",
                "retention_action": "ARCHIVE"
            }
        )

        assert result.retention_period == RetentionPeriod.YEARS_5

    @pytest.mark.asyncio
    async def test_enable_legal_hold(self, mock_audit_service, sample_data_retention):
        """Testa ativação de retenção legal."""
        sample_data_retention.enable_legal_hold("Processo judicial", "ADV-001")
        mock_audit_service.update_data_retention_policy = AsyncMock(
            return_value=sample_data_retention
        )

        assert sample_data_retention.legal_hold is True
        assert sample_data_retention.legal_hold_reference == "ADV-001"

    @pytest.mark.asyncio
    async def test_disable_legal_hold(self, mock_audit_service, sample_data_retention):
        """Testa desativação de retenção legal."""
        sample_data_retention.legal_hold = True
        sample_data_retention.disable_legal_hold()
        mock_audit_service.update_data_retention_policy = AsyncMock(
            return_value=sample_data_retention
        )

        assert sample_data_retention.legal_hold is False

    @pytest.mark.asyncio
    async def test_record_execution(self, mock_audit_service, sample_data_retention):
        """Testa registro de execução da política."""
        sample_data_retention.record_execution(100, True)
        mock_audit_service.update_data_retention_policy = AsyncMock(
            return_value=sample_data_retention
        )

        assert sample_data_retention.last_execution is not None
        assert sample_data_retention.records_affected == 100
        assert sample_data_retention.execution_count == 1


# ========================
# Testes de Access History
# ========================

class TestAccessHistoryAPI:
    """Testes dos endpoints de histórico de acesso."""

    @pytest.mark.asyncio
    async def test_list_access_history_success(
        self, mock_audit_service, sample_access_history
    ):
        """Testa listagem de histórico."""
        mock_audit_service.list_access_history = AsyncMock(return_value={
            "items": [sample_access_history],
            "total": 1,
            "page": 1,
            "page_size": 20
        })

        result = await mock_audit_service.list_access_history(
            tenant_id=sample_access_history.tenant_id,
            page=1,
            page_size=20
        )

        assert result["total"] == 1
        assert result["items"][0].access_type == AccessType.LOGIN

    @pytest.mark.asyncio
    async def test_create_login_access(self, mock_audit_service, sample_access_history):
        """Testa criação de registro de login."""
        mock_audit_service.create_access_history = AsyncMock(return_value=sample_access_history)

        result = await mock_audit_service.create_access_history(
            tenant_id=sample_access_history.tenant_id,
            data={
                "user_id": str(sample_access_history.user_id),
                "access_type": "LOGIN",
                "result": "SUCCESS",
                "ip_address": "192.168.1.100"
            }
        )

        assert result.access_type == AccessType.LOGIN
        assert result.result == AccessResult.SUCCESS

    @pytest.mark.asyncio
    async def test_get_access_stats(self, mock_audit_service):
        """Testa obtenção de estatísticas de acesso."""
        mock_audit_service.get_access_stats = AsyncMock(return_value={
            "total_accesses": 5000,
            "successful_logins": 4800,
            "failed_logins": 200,
            "unique_users": 150,
            "by_device_type": {"DESKTOP": 3000, "MOBILE": 1500, "TABLET": 500},
            "by_risk_level": {"LOW": 4500, "MEDIUM": 400, "HIGH": 80, "CRITICAL": 20}
        })

        result = await mock_audit_service.get_access_stats(
            tenant_id=uuid4(),
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow()
        )

        assert result["total_accesses"] == 5000
        assert result["successful_logins"] == 4800

    @pytest.mark.asyncio
    async def test_flag_anomaly(self, mock_audit_service, sample_access_history):
        """Testa flag de anomalia."""
        sample_access_history.flag_anomaly("Login de IP desconhecido")
        mock_audit_service.update_access_history = AsyncMock(return_value=sample_access_history)

        assert sample_access_history.is_anomaly is True
        assert sample_access_history.anomaly_reason == "Login de IP desconhecido"

    @pytest.mark.asyncio
    async def test_trigger_alert(self, mock_audit_service, sample_access_history):
        """Testa disparo de alerta."""
        sample_access_history.trigger_alert("alert-001", "Múltiplas tentativas falhas")
        mock_audit_service.update_access_history = AsyncMock(return_value=sample_access_history)

        assert sample_access_history.alert_triggered is True
        assert sample_access_history.alert_id == "alert-001"

    @pytest.mark.asyncio
    async def test_calculate_risk(self, mock_audit_service, sample_access_history):
        """Testa cálculo de risco."""
        sample_access_history.is_anomaly = True
        sample_access_history.is_new_device = True
        sample_access_history.calculate_risk()
        mock_audit_service.update_access_history = AsyncMock(return_value=sample_access_history)

        # Com anomalia e novo dispositivo, risco deve ser elevado
        assert sample_access_history.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]


# ========================
# Testes de Dashboard
# ========================

class TestDashboardAPI:
    """Testes dos endpoints de dashboard."""

    @pytest.mark.asyncio
    async def test_get_audit_dashboard(self, mock_audit_service):
        """Testa obtenção do dashboard de auditoria."""
        mock_audit_service.get_audit_dashboard = AsyncMock(return_value={
            "total_logs": 10000,
            "logs_today": 500,
            "security_events": 50,
            "requires_review": 10,
            "recent_critical": [],
            "trend": {"day_1": 480, "day_2": 520}
        })

        result = await mock_audit_service.get_audit_dashboard(tenant_id=uuid4())

        assert result["total_logs"] == 10000
        assert "logs_today" in result

    @pytest.mark.asyncio
    async def test_get_compliance_overview(self, mock_audit_service):
        """Testa obtenção do overview de compliance."""
        mock_audit_service.get_compliance_overview = AsyncMock(return_value={
            "total_rules": 50,
            "active_rules": 45,
            "compliance_rate": 92.5,
            "pending_checks": 5,
            "non_compliant_items": 3,
            "by_framework": {
                "LGPD": {"total": 20, "compliant": 18},
                "GDPR": {"total": 15, "compliant": 14}
            }
        })

        result = await mock_audit_service.get_compliance_overview(tenant_id=uuid4())

        assert result["compliance_rate"] == 92.5
        assert "by_framework" in result

    @pytest.mark.asyncio
    async def test_get_security_overview(self, mock_audit_service):
        """Testa obtenção do overview de segurança."""
        mock_audit_service.get_security_overview = AsyncMock(return_value={
            "total_accesses": 5000,
            "failed_logins": 200,
            "anomalies_detected": 15,
            "high_risk_accesses": 8,
            "alerts_triggered": 5,
            "active_sessions": 120
        })

        result = await mock_audit_service.get_security_overview(tenant_id=uuid4())

        assert result["anomalies_detected"] == 15
        assert result["high_risk_accesses"] == 8


# ========================
# Testes de Validação
# ========================

class TestValidation:
    """Testes de validação de entrada."""

    @pytest.mark.asyncio
    async def test_invalid_audit_action(self, mock_audit_service):
        """Testa validação de ação inválida."""
        mock_audit_service.create_audit_log = AsyncMock(
            side_effect=ValueError("Invalid action")
        )

        with pytest.raises(ValueError):
            await mock_audit_service.create_audit_log(
                tenant_id=uuid4(),
                data={"action": "INVALID_ACTION"}
            )

    @pytest.mark.asyncio
    async def test_invalid_compliance_framework(self, mock_audit_service):
        """Testa validação de framework inválido."""
        mock_audit_service.create_compliance_rule = AsyncMock(
            side_effect=ValueError("Invalid framework")
        )

        with pytest.raises(ValueError):
            await mock_audit_service.create_compliance_rule(
                tenant_id=uuid4(),
                data={"framework": "INVALID_FRAMEWORK"}
            )

    @pytest.mark.asyncio
    async def test_invalid_retention_period(self, mock_audit_service):
        """Testa validação de período de retenção inválido."""
        mock_audit_service.create_data_retention_policy = AsyncMock(
            side_effect=ValueError("Invalid retention period")
        )

        with pytest.raises(ValueError):
            await mock_audit_service.create_data_retention_policy(
                tenant_id=uuid4(),
                data={"retention_period": "INVALID_PERIOD"}
            )


# ========================
# Testes de Paginação
# ========================

class TestPagination:
    """Testes de paginação."""

    @pytest.mark.asyncio
    async def test_pagination_first_page(self, mock_audit_service):
        """Testa primeira página."""
        mock_audit_service.list_audit_logs = AsyncMock(return_value={
            "items": [MagicMock() for _ in range(20)],
            "total": 100,
            "page": 1,
            "page_size": 20,
            "total_pages": 5
        })

        result = await mock_audit_service.list_audit_logs(
            tenant_id=uuid4(),
            page=1,
            page_size=20
        )

        assert len(result["items"]) == 20
        assert result["total_pages"] == 5

    @pytest.mark.asyncio
    async def test_pagination_last_page(self, mock_audit_service):
        """Testa última página."""
        mock_audit_service.list_audit_logs = AsyncMock(return_value={
            "items": [MagicMock() for _ in range(5)],
            "total": 45,
            "page": 3,
            "page_size": 20,
            "total_pages": 3
        })

        result = await mock_audit_service.list_audit_logs(
            tenant_id=uuid4(),
            page=3,
            page_size=20
        )

        assert len(result["items"]) == 5
        assert result["page"] == 3


# ========================
# Testes de Erro
# ========================

class TestErrorHandling:
    """Testes de tratamento de erros."""

    @pytest.mark.asyncio
    async def test_database_error(self, mock_audit_service):
        """Testa erro de banco de dados."""
        mock_audit_service.list_audit_logs = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        with pytest.raises(Exception) as exc_info:
            await mock_audit_service.list_audit_logs(
                tenant_id=uuid4(),
                page=1,
                page_size=20
            )

        assert "Database connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_not_found_error(self, mock_audit_service):
        """Testa erro de recurso não encontrado."""
        mock_audit_service.get_audit_log = AsyncMock(return_value=None)

        result = await mock_audit_service.get_audit_log(
            tenant_id=uuid4(),
            log_id=uuid4()
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_permission_denied(self, mock_audit_service):
        """Testa erro de permissão negada."""
        mock_audit_service.delete_audit_log = AsyncMock(
            side_effect=PermissionError("Permission denied")
        )

        with pytest.raises(PermissionError):
            await mock_audit_service.delete_audit_log(
                tenant_id=uuid4(),
                log_id=uuid4()
            )
