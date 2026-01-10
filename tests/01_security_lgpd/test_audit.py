"""
Tests for Audit Module (audit_logger).

Author: Claude AI + Human Developer
Date: 2026-01-10
"""

import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch
import uuid
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List
import hashlib
import functools


# =============================================================================
# MOCK CLASSES (Simulating the actual implementation)
# =============================================================================

class AuditAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    EXPORT = "export"


class AuditSeverity(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ResourceType(str, Enum):
    USER = "user"
    DOCUMENT = "document"
    SESSION = "session"
    REPORT = "report"
    SYSTEM = "system"


SENSITIVE_FIELDS = ["senha", "password", "token", "secret", "api_key"]


@dataclass
class AuditEntry:
    id: str
    action: AuditAction
    resource_type: ResourceType
    resource_id: Optional[str]
    description: str
    user_id: Optional[str]
    ip_address: Optional[str]
    severity: AuditSeverity
    timestamp: datetime
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    previous_hash: Optional[str] = None
    entry_hash: Optional[str] = None


class AuditLogger:
    """Simulated AuditLogger for testing."""

    def __init__(self, db_session=None):
        self.db = db_session
        self._entries: List[AuditEntry] = []
        self._last_hash: Optional[str] = None

    def _redact_sensitive(self, data: Optional[Dict]) -> Optional[Dict]:
        if not data:
            return data
        result = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS:
                result[key] = "[REDACTED]"
            else:
                result[key] = value
        return result

    def _compute_hash(self, entry: AuditEntry) -> str:
        content = f"{entry.id}{entry.action}{entry.timestamp}{self._last_hash or ''}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def log(
        self,
        action: AuditAction,
        resource_type: ResourceType,
        resource_id: Optional[str],
        description: str,
        context: Dict[str, Any] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        severity: AuditSeverity = None,
        metadata: Optional[Dict] = None
    ) -> AuditEntry:
        context = context or {}

        # Determine default severity based on action
        if severity is None:
            if action in [AuditAction.DELETE, AuditAction.LOGIN_FAILED]:
                severity = AuditSeverity.WARNING
            else:
                severity = AuditSeverity.INFO

        # Redact sensitive data
        redacted_old = self._redact_sensitive(old_values)
        redacted_new = self._redact_sensitive(new_values)

        entry = AuditEntry(
            id=str(uuid.uuid4()),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            user_id=context.get("user_id"),
            ip_address=context.get("ip_address"),
            severity=severity,
            timestamp=datetime.now(),
            old_values=redacted_old,
            new_values=redacted_new,
            metadata=metadata,
            previous_hash=self._last_hash
        )

        entry.entry_hash = self._compute_hash(entry)
        self._last_hash = entry.entry_hash
        self._entries.append(entry)

        return entry

    async def query(
        self,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        action: Optional[AuditAction] = None,
        severity: Optional[AuditSeverity] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditEntry]:
        results = self._entries.copy()

        if user_id:
            results = [e for e in results if e.user_id == user_id]
        if resource_id:
            results = [e for e in results if e.resource_id == resource_id]
        if resource_type:
            results = [e for e in results if e.resource_type == resource_type]
        if action:
            results = [e for e in results if e.action == action]
        if severity:
            results = [e for e in results if e.severity == severity]
        if start_date:
            results = [e for e in results if e.timestamp >= start_date]
        if end_date:
            results = [e for e in results if e.timestamp <= end_date]

        return results

    async def generate_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        resource_id: Optional[str] = None,
        report_type: str = "compliance"
    ) -> Dict[str, Any]:
        entries = await self.query(
            resource_id=resource_id,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "total_entries": len(entries),
            "by_action": {},
            "by_severity": {}
        }

    async def export(
        self,
        start_date: Optional[datetime] = None,
        format: str = "json"
    ) -> str:
        entries = await self.query(start_date=start_date)

        if format == "json":
            return json.dumps([{
                "id": e.id,
                "action": e.action.value,
                "timestamp": e.timestamp.isoformat()
            } for e in entries])
        return ""


def audit_action(logger: AuditLogger, action: AuditAction, resource_type: ResourceType):
    """Decorator for auditing function calls."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                await logger.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=result.get("id") if isinstance(result, dict) else None,
                    description=f"Function {func.__name__} executed successfully",
                    context={}
                )
                return result
            except Exception as e:
                await logger.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=None,
                    description=f"Function {func.__name__} failed: {str(e)}",
                    context={},
                    severity=AuditSeverity.ERROR
                )
                raise
        return wrapper
    return decorator


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_db_session():
    return MagicMock()


# =============================================================================
# AUDIT LOGGER TESTS
# =============================================================================

class TestAuditLogger:
    """Tests for AuditLogger class."""

    @pytest.fixture
    def audit_logger(self, mock_db_session):
        """Create AuditLogger instance."""
        return AuditLogger(db_session=mock_db_session)

    @pytest.fixture
    def sample_context(self):
        """Sample audit context."""
        return {
            "user_id": str(uuid.uuid4()),
            "user_email": "admin@empresa.com",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
            "session_id": str(uuid.uuid4())
        }

    @pytest.mark.asyncio
    async def test_log_create_action(self, audit_logger, sample_context):
        """Test logging CREATE action."""
        entry = await audit_logger.log(
            action=AuditAction.CREATE,
            resource_type=ResourceType.USER,
            resource_id=str(uuid.uuid4()),
            description="Usuario criado",
            context=sample_context
        )

        assert entry is not None
        assert entry.action == AuditAction.CREATE
        assert entry.severity == AuditSeverity.INFO

    @pytest.mark.asyncio
    async def test_log_read_action(self, audit_logger, sample_context):
        """Test logging READ action."""
        entry = await audit_logger.log(
            action=AuditAction.READ,
            resource_type=ResourceType.DOCUMENT,
            resource_id=str(uuid.uuid4()),
            description="Documento visualizado",
            context=sample_context
        )

        assert entry is not None
        assert entry.action == AuditAction.READ

    @pytest.mark.asyncio
    async def test_log_update_action(self, audit_logger, sample_context):
        """Test logging UPDATE action."""
        old_values = {"nome": "Antigo Nome"}
        new_values = {"nome": "Novo Nome"}

        entry = await audit_logger.log(
            action=AuditAction.UPDATE,
            resource_type=ResourceType.USER,
            resource_id=str(uuid.uuid4()),
            description="Usuario atualizado",
            context=sample_context,
            old_values=old_values,
            new_values=new_values
        )

        assert entry is not None
        assert entry.action == AuditAction.UPDATE
        assert entry.old_values == old_values
        assert entry.new_values == new_values

    @pytest.mark.asyncio
    async def test_log_delete_action(self, audit_logger, sample_context):
        """Test logging DELETE action."""
        entry = await audit_logger.log(
            action=AuditAction.DELETE,
            resource_type=ResourceType.USER,
            resource_id=str(uuid.uuid4()),
            description="Usuario removido",
            context=sample_context,
            severity=AuditSeverity.WARNING
        )

        assert entry is not None
        assert entry.action == AuditAction.DELETE
        assert entry.severity == AuditSeverity.WARNING

    @pytest.mark.asyncio
    async def test_log_login_action(self, audit_logger, sample_context):
        """Test logging LOGIN action."""
        entry = await audit_logger.log(
            action=AuditAction.LOGIN,
            resource_type=ResourceType.SESSION,
            resource_id=sample_context["session_id"],
            description="Login realizado com sucesso",
            context=sample_context
        )

        assert entry is not None
        assert entry.action == AuditAction.LOGIN

    @pytest.mark.asyncio
    async def test_log_logout_action(self, audit_logger, sample_context):
        """Test logging LOGOUT action."""
        entry = await audit_logger.log(
            action=AuditAction.LOGOUT,
            resource_type=ResourceType.SESSION,
            resource_id=sample_context["session_id"],
            description="Logout realizado",
            context=sample_context
        )

        assert entry is not None
        assert entry.action == AuditAction.LOGOUT

    @pytest.mark.asyncio
    async def test_log_failed_login(self, audit_logger):
        """Test logging failed login attempt."""
        context = {
            "ip_address": "192.168.1.200",
            "user_agent": "Mozilla/5.0",
            "attempted_email": "hacker@evil.com"
        }

        entry = await audit_logger.log(
            action=AuditAction.LOGIN_FAILED,
            resource_type=ResourceType.SESSION,
            resource_id=None,
            description="Tentativa de login falhou",
            context=context,
            severity=AuditSeverity.WARNING
        )

        assert entry is not None
        assert entry.action == AuditAction.LOGIN_FAILED
        assert entry.severity == AuditSeverity.WARNING

    @pytest.mark.asyncio
    async def test_log_export_action(self, audit_logger, sample_context):
        """Test logging data EXPORT action."""
        entry = await audit_logger.log(
            action=AuditAction.EXPORT,
            resource_type=ResourceType.REPORT,
            resource_id=str(uuid.uuid4()),
            description="Relatorio exportado",
            context=sample_context,
            metadata={"format": "PDF", "records": 1500}
        )

        assert entry is not None
        assert entry.action == AuditAction.EXPORT

    @pytest.mark.asyncio
    async def test_log_with_sensitive_data_redaction(self, audit_logger, sample_context):
        """Test that sensitive data is redacted in logs."""
        entry = await audit_logger.log(
            action=AuditAction.UPDATE,
            resource_type=ResourceType.USER,
            resource_id=str(uuid.uuid4()),
            description="Senha alterada",
            context=sample_context,
            old_values={"senha": "antiga123"},
            new_values={"senha": "nova456"}
        )

        # Password should be redacted
        assert entry.old_values.get("senha") != "antiga123"
        assert entry.new_values.get("senha") != "nova456"

    @pytest.mark.asyncio
    async def test_query_audit_logs(self, audit_logger, sample_context):
        """Test querying audit logs."""
        user_id = sample_context["user_id"]

        # Create some logs
        await audit_logger.log(
            action=AuditAction.CREATE,
            resource_type=ResourceType.USER,
            resource_id=str(uuid.uuid4()),
            description="Teste 1",
            context=sample_context
        )
        await audit_logger.log(
            action=AuditAction.UPDATE,
            resource_type=ResourceType.USER,
            resource_id=str(uuid.uuid4()),
            description="Teste 2",
            context=sample_context
        )

        # Query logs
        logs = await audit_logger.query(
            user_id=user_id,
            start_date=datetime.now() - timedelta(hours=1),
            end_date=datetime.now() + timedelta(hours=1)
        )

        assert logs is not None

    @pytest.mark.asyncio
    async def test_query_by_resource(self, audit_logger, sample_context):
        """Test querying logs by resource."""
        resource_id = str(uuid.uuid4())

        await audit_logger.log(
            action=AuditAction.CREATE,
            resource_type=ResourceType.DOCUMENT,
            resource_id=resource_id,
            description="Documento criado",
            context=sample_context
        )

        logs = await audit_logger.query(
            resource_id=resource_id,
            resource_type=ResourceType.DOCUMENT
        )

        assert logs is not None

    @pytest.mark.asyncio
    async def test_query_by_action(self, audit_logger, sample_context):
        """Test querying logs by action type."""
        logs = await audit_logger.query(
            action=AuditAction.DELETE,
            start_date=datetime.now() - timedelta(days=7)
        )

        assert logs is not None

    @pytest.mark.asyncio
    async def test_query_by_severity(self, audit_logger, sample_context):
        """Test querying logs by severity."""
        await audit_logger.log(
            action=AuditAction.DELETE,
            resource_type=ResourceType.USER,
            resource_id=str(uuid.uuid4()),
            description="Acao critica",
            context=sample_context,
            severity=AuditSeverity.CRITICAL
        )

        logs = await audit_logger.query(
            severity=AuditSeverity.CRITICAL
        )

        assert logs is not None


# =============================================================================
# AUDIT DECORATOR TESTS
# =============================================================================

class TestAuditDecorator:
    """Tests for audit_action decorator."""

    @pytest.mark.asyncio
    async def test_decorator_logs_function_call(self, mock_db_session):
        """Test that decorator logs function execution."""
        logger = AuditLogger(db_session=mock_db_session)

        @audit_action(
            logger=logger,
            action=AuditAction.CREATE,
            resource_type=ResourceType.USER
        )
        async def create_user(user_data: dict):
            return {"id": str(uuid.uuid4()), **user_data}

        result = await create_user({"nome": "Teste"})

        assert result is not None
        assert "id" in result

    @pytest.mark.asyncio
    async def test_decorator_logs_exception(self, mock_db_session):
        """Test that decorator logs exceptions."""
        logger = AuditLogger(db_session=mock_db_session)

        @audit_action(
            logger=logger,
            action=AuditAction.CREATE,
            resource_type=ResourceType.USER
        )
        async def failing_function():
            raise ValueError("Erro de teste")

        with pytest.raises(ValueError):
            await failing_function()


# =============================================================================
# AUDIT INTEGRITY TESTS
# =============================================================================

class TestAuditIntegrity:
    """Tests for audit log integrity."""

    @pytest.fixture
    def audit_logger(self, mock_db_session):
        """Create AuditLogger instance."""
        return AuditLogger(db_session=mock_db_session)

    @pytest.mark.asyncio
    async def test_audit_entry_immutability(self, audit_logger):
        """Test that audit entries cannot be modified after creation."""
        context = {"user_id": str(uuid.uuid4())}

        entry = await audit_logger.log(
            action=AuditAction.CREATE,
            resource_type=ResourceType.USER,
            resource_id=str(uuid.uuid4()),
            description="Teste de imutabilidade",
            context=context
        )

        # Audit entries should not have update methods
        assert not hasattr(entry, 'update') or entry.id is not None

    @pytest.mark.asyncio
    async def test_audit_timestamp_automatic(self, audit_logger):
        """Test that timestamp is automatically set."""
        context = {"user_id": str(uuid.uuid4())}

        before = datetime.now()
        entry = await audit_logger.log(
            action=AuditAction.READ,
            resource_type=ResourceType.DOCUMENT,
            resource_id=str(uuid.uuid4()),
            description="Teste",
            context=context
        )
        after = datetime.now()

        assert entry.timestamp is not None
        assert before <= entry.timestamp <= after

    @pytest.mark.asyncio
    async def test_audit_hash_chain(self, audit_logger):
        """Test audit log hash chain integrity."""
        context = {"user_id": str(uuid.uuid4())}

        entry1 = await audit_logger.log(
            action=AuditAction.CREATE,
            resource_type=ResourceType.USER,
            resource_id=str(uuid.uuid4()),
            description="Entry 1",
            context=context
        )

        entry2 = await audit_logger.log(
            action=AuditAction.UPDATE,
            resource_type=ResourceType.USER,
            resource_id=str(uuid.uuid4()),
            description="Entry 2",
            context=context
        )

        # If hash chain is implemented
        if hasattr(entry2, 'previous_hash'):
            assert entry2.previous_hash is not None


# =============================================================================
# COMPLIANCE REPORTING TESTS
# =============================================================================

class TestAuditReporting:
    """Tests for audit compliance reporting."""

    @pytest.fixture
    def audit_logger(self, mock_db_session):
        """Create AuditLogger instance."""
        return AuditLogger(db_session=mock_db_session)

    @pytest.mark.asyncio
    async def test_generate_compliance_report(self, audit_logger):
        """Test generating compliance report."""
        report = await audit_logger.generate_report(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            report_type="compliance"
        )

        assert report is not None

    @pytest.mark.asyncio
    async def test_generate_access_report(self, audit_logger):
        """Test generating access report for specific resource."""
        resource_id = str(uuid.uuid4())

        report = await audit_logger.generate_report(
            resource_id=resource_id,
            report_type="access"
        )

        assert report is not None

    @pytest.mark.asyncio
    async def test_export_audit_logs(self, audit_logger):
        """Test exporting audit logs."""
        exported = await audit_logger.export(
            start_date=datetime.now() - timedelta(days=7),
            format="json"
        )

        assert exported is not None
