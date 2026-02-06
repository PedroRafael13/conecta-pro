"""Testes para o sistema de auditoria."""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from core.audit.audit_log import (
    AuditAction,
    AuditLog,
    audit_sensitive_access,
    get_audit_logs,
    log_audit,
)


class TestAuditAction:
    """Testes para enum AuditAction."""

    def test_view_personal_data(self):
        """Testa valor VIEW_PERSONAL_DATA."""
        assert AuditAction.VIEW_PERSONAL_DATA.value == "view_personal_data"

    def test_edit_personal_data(self):
        """Testa valor EDIT_PERSONAL_DATA."""
        assert AuditAction.EDIT_PERSONAL_DATA.value == "edit_personal_data"

    def test_delete_personal_data(self):
        """Testa valor DELETE_PERSONAL_DATA."""
        assert AuditAction.DELETE_PERSONAL_DATA.value == "delete_personal_data"

    def test_login_success(self):
        """Testa valor LOGIN_SUCCESS."""
        assert AuditAction.LOGIN_SUCCESS.value == "login_success"

    def test_login_failure(self):
        """Testa valor LOGIN_FAILURE."""
        assert AuditAction.LOGIN_FAILURE.value == "login_failure"

    def test_view_salary(self):
        """Testa valor VIEW_SALARY."""
        assert AuditAction.VIEW_SALARY.value == "view_salary"

    def test_role_change(self):
        """Testa valor ROLE_CHANGE."""
        assert AuditAction.ROLE_CHANGE.value == "role_change"


class TestAuditLog:
    """Testes para modelo AuditLog."""

    def test_create_audit_log(self):
        """Testa criação de AuditLog."""
        log = AuditLog(
            action=AuditAction.LOGIN_SUCCESS,
            resource_type="user",
            user_id="123",
        )

        assert log.action == AuditAction.LOGIN_SUCCESS
        assert log.resource_type == "user"
        assert log.user_id == "123"
        assert log.id is not None
        assert log.timestamp is not None

    def test_audit_log_defaults(self):
        """Testa valores default do AuditLog."""
        log = AuditLog(
            action=AuditAction.VIEW_PERSONAL_DATA,
            resource_type="employee",
        )

        assert log.user_id is None
        assert log.user_email is None
        assert log.ip_address is None
        assert log.resource_id is None
        assert log.details is None
        assert log.success is True
        assert log.error_message is None

    def test_audit_log_full(self):
        """Testa AuditLog com todos os campos."""
        log = AuditLog(
            action=AuditAction.EDIT_SALARY,
            resource_type="employee",
            resource_id="emp-001",
            user_id="user-123",
            user_email="admin@test.com",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={"old_salary": 5000, "new_salary": 6000},
            success=True,
        )

        assert log.resource_id == "emp-001"
        assert log.user_email == "admin@test.com"
        assert log.ip_address == "192.168.1.1"
        assert log.details["old_salary"] == 5000


class TestLogAudit:
    """Testes para função log_audit."""

    @pytest.mark.asyncio
    async def test_log_audit_success(self):
        """Testa log de auditoria com sucesso."""
        # Limpar logs anteriores
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        log = await log_audit(
            action=AuditAction.LOGIN_SUCCESS,
            resource_type="auth",
            user_id="user-123",
            user_email="test@test.com",
            ip_address="127.0.0.1",
        )

        assert log.action == AuditAction.LOGIN_SUCCESS
        assert log.user_id == "user-123"
        assert log.success is True
        assert len(audit_module._audit_logs) == 1

    @pytest.mark.asyncio
    async def test_log_audit_failure(self):
        """Testa log de auditoria com falha."""
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        log = await log_audit(
            action=AuditAction.LOGIN_FAILURE,
            resource_type="auth",
            user_email="invalid@test.com",
            success=False,
            error_message="Credenciais inválidas",
        )

        assert log.action == AuditAction.LOGIN_FAILURE
        assert log.success is False
        assert log.error_message == "Credenciais inválidas"

    @pytest.mark.asyncio
    async def test_log_audit_with_details(self):
        """Testa log de auditoria com detalhes."""
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        log = await log_audit(
            action=AuditAction.EDIT_PERSONAL_DATA,
            resource_type="user",
            resource_id="user-456",
            details={"field": "email", "action": "update"},
        )

        assert log.details is not None
        assert log.details["field"] == "email"


class TestGetAuditLogs:
    """Testes para função get_audit_logs."""

    @pytest.mark.asyncio
    async def test_get_all_logs(self):
        """Testa obtenção de todos os logs."""
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        await log_audit(AuditAction.LOGIN_SUCCESS, "auth", user_id="user-1")
        await log_audit(AuditAction.LOGIN_SUCCESS, "auth", user_id="user-2")
        await log_audit(AuditAction.VIEW_PERSONAL_DATA, "user", user_id="user-1")

        logs = await get_audit_logs()

        assert len(logs) == 3

    @pytest.mark.asyncio
    async def test_get_logs_by_user(self):
        """Testa filtro por usuário."""
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        await log_audit(AuditAction.LOGIN_SUCCESS, "auth", user_id="user-1")
        await log_audit(AuditAction.LOGIN_SUCCESS, "auth", user_id="user-2")
        await log_audit(AuditAction.VIEW_PERSONAL_DATA, "user", user_id="user-1")

        logs = await get_audit_logs(user_id="user-1")

        assert len(logs) == 2
        assert all(log.user_id == "user-1" for log in logs)

    @pytest.mark.asyncio
    async def test_get_logs_by_action(self):
        """Testa filtro por ação."""
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        await log_audit(AuditAction.LOGIN_SUCCESS, "auth", user_id="user-1")
        await log_audit(AuditAction.LOGIN_FAILURE, "auth", user_id="user-2")
        await log_audit(AuditAction.LOGIN_SUCCESS, "auth", user_id="user-3")

        logs = await get_audit_logs(action=AuditAction.LOGIN_SUCCESS)

        assert len(logs) == 2
        assert all(log.action == AuditAction.LOGIN_SUCCESS for log in logs)

    @pytest.mark.asyncio
    async def test_get_logs_by_resource_type(self):
        """Testa filtro por tipo de recurso."""
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        await log_audit(AuditAction.LOGIN_SUCCESS, "auth")
        await log_audit(AuditAction.VIEW_PERSONAL_DATA, "user")
        await log_audit(AuditAction.EDIT_SALARY, "employee")

        logs = await get_audit_logs(resource_type="user")

        assert len(logs) == 1
        assert logs[0].resource_type == "user"

    @pytest.mark.asyncio
    async def test_get_logs_with_limit(self):
        """Testa limite de resultados."""
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        for i in range(10):
            await log_audit(AuditAction.LOGIN_SUCCESS, "auth", user_id=f"user-{i}")

        logs = await get_audit_logs(limit=5)

        assert len(logs) == 5

    @pytest.mark.asyncio
    async def test_get_logs_sorted_by_timestamp(self):
        """Testa ordenação por timestamp."""
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        await log_audit(AuditAction.LOGIN_SUCCESS, "auth", user_id="first")
        await log_audit(AuditAction.LOGIN_SUCCESS, "auth", user_id="second")
        await log_audit(AuditAction.LOGIN_SUCCESS, "auth", user_id="third")

        logs = await get_audit_logs()

        # Mais recente primeiro
        assert logs[0].user_id == "third"
        assert logs[2].user_id == "first"


class TestAuditSensitiveAccessDecorator:
    """Testes para decorator audit_sensitive_access."""

    @pytest.mark.asyncio
    async def test_decorator_logs_success(self):
        """Testa que decorator loga sucesso."""
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        @audit_sensitive_access(AuditAction.VIEW_SALARY, "employee", "employee_id")
        async def get_salary(employee_id: str):
            return {"salary": 5000}

        result = await get_salary(employee_id="emp-123")

        assert result == {"salary": 5000}
        assert len(audit_module._audit_logs) == 1
        assert audit_module._audit_logs[0].action == AuditAction.VIEW_SALARY
        assert audit_module._audit_logs[0].success is True

    @pytest.mark.asyncio
    async def test_decorator_logs_failure(self):
        """Testa que decorator loga falha."""
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        @audit_sensitive_access(AuditAction.VIEW_SALARY, "employee", "employee_id")
        async def get_salary(employee_id: str):
            raise ValueError("Employee not found")

        with pytest.raises(ValueError):
            await get_salary(employee_id="emp-999")

        assert len(audit_module._audit_logs) == 1
        assert audit_module._audit_logs[0].success is False
        assert "Employee not found" in audit_module._audit_logs[0].error_message

    @pytest.mark.asyncio
    async def test_decorator_extracts_resource_id(self):
        """Testa extração do resource_id."""
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        @audit_sensitive_access(AuditAction.EDIT_PERSONAL_DATA, "user", "user_id")
        async def update_user(user_id: str, data: dict):
            return {"updated": True}

        await update_user(user_id="user-456", data={"name": "Test"})

        assert audit_module._audit_logs[0].resource_id == "user-456"

    @pytest.mark.asyncio
    async def test_decorator_no_resource_id_param(self):
        """Testa decorator sem parâmetro de resource_id."""
        import core.audit.audit_log as audit_module

        audit_module._audit_logs = []

        @audit_sensitive_access(AuditAction.EXPORT_PERSONAL_DATA, "report")
        async def export_all():
            return {"data": []}

        await export_all()

        assert audit_module._audit_logs[0].resource_id is None
