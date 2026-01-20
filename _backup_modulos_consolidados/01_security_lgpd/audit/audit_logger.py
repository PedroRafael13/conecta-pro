"""
Module: AuditLogger
Description: Sistema de logging de auditoria para compliance LGPD com
             rastreabilidade completa de acesso a dados pessoais.
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: LGPD Art. 37, 49 - Registro de Operacoes de Tratamento
"""

from typing import Dict, List, Optional, Any, Union, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from contextvars import ContextVar
import json
import hashlib
import logging
import asyncio
import traceback

from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, Text, Integer, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, INET
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()

# Context variable para rastreamento de requisicao
_request_context: ContextVar[Dict[str, Any]] = ContextVar('request_context', default={})


class AuditAction(str, Enum):
    """Acoes auditaveis no sistema."""
    # Operacoes de dados
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    IMPORT = "import"
    # Autenticacao
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    # Autorizacao
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    ACCESS_DENIED = "access_denied"
    # LGPD
    CONSENT_GRANTED = "consent_granted"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    DATA_ACCESS_REQUEST = "data_access_request"
    DATA_ERASURE_REQUEST = "data_erasure_request"
    DATA_PORTABILITY = "data_portability"
    PII_ACCESSED = "pii_accessed"
    PII_MODIFIED = "pii_modified"
    # Sistema
    CONFIG_CHANGE = "config_change"
    SYSTEM_ERROR = "system_error"
    SECURITY_ALERT = "security_alert"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"


class AuditSeverity(str, Enum):
    """Niveis de severidade de eventos."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ResourceType(str, Enum):
    """Tipos de recursos auditados."""
    USER = "user"
    EMPLOYEE = "employee"
    CLIENT = "client"
    CONTRACT = "contract"
    DOCUMENT = "document"
    REPORT = "report"
    CONFIGURATION = "configuration"
    PERMISSION = "permission"
    CONSENT = "consent"
    MEDICAL_RECORD = "medical_record"
    PAYROLL = "payroll"
    SYSTEM = "system"


@dataclass
class AuditContext:
    """Contexto de uma operacao auditada."""
    request_id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "user_role": self.user_role,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "tenant_id": self.tenant_id,
            "correlation_id": self.correlation_id,
        }


@dataclass
class AuditEntry:
    """Entrada de log de auditoria."""
    id: UUID
    timestamp: datetime
    action: AuditAction
    severity: AuditSeverity
    resource_type: ResourceType
    resource_id: Optional[str]
    context: AuditContext
    description: str
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    pii_fields_accessed: List[str] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "severity": self.severity.value,
            "resource_type": self.resource_type.value,
            "resource_id": self.resource_id,
            "context": self.context.to_dict(),
            "description": self.description,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "pii_fields_accessed": self.pii_fields_accessed,
            "success": self.success,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Serializa para JSON."""
        return json.dumps(self.to_dict(), default=str, ensure_ascii=False)


# SQLAlchemy Model
class AuditLogModel(Base):
    """Modelo de banco para logs de auditoria."""
    __tablename__ = "lgpd_audit_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    action = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(100), nullable=True, index=True)

    # Contexto
    request_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    user_role = Column(String(50), nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(100), nullable=True)
    tenant_id = Column(String(100), nullable=True, index=True)
    correlation_id = Column(String(100), nullable=True, index=True)

    # Detalhes
    description = Column(Text, nullable=False)
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    pii_fields_accessed = Column(JSONB, default=[])
    success = Column(String(5), default="true")
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    extra_metadata = Column(JSONB, default={})

    # Indices compostos para queries comuns
    __table_args__ = (
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_resource', 'resource_type', 'resource_id', 'timestamp'),
        Index('idx_audit_action_timestamp', 'action', 'timestamp'),
    )


class AuditStoreInterface(ABC):
    """Interface abstrata para armazenamento de logs."""

    @abstractmethod
    async def store(self, entry: AuditEntry) -> bool:
        """Armazena entrada de auditoria."""
        pass

    @abstractmethod
    async def query(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        action: Optional[AuditAction] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """Consulta logs de auditoria."""
        pass


class InMemoryAuditStore(AuditStoreInterface):
    """Armazenamento em memoria para desenvolvimento."""

    def __init__(self, max_entries: int = 10000):
        self._entries: List[AuditEntry] = []
        self._max_entries = max_entries
        self._lock = asyncio.Lock()

    async def store(self, entry: AuditEntry) -> bool:
        async with self._lock:
            self._entries.append(entry)
            # Limpa entradas antigas se exceder limite
            if len(self._entries) > self._max_entries:
                self._entries = self._entries[-self._max_entries:]
            return True

    async def query(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        action: Optional[AuditAction] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        async with self._lock:
            results = self._entries.copy()

            if start_date:
                results = [e for e in results if e.timestamp >= start_date]
            if end_date:
                results = [e for e in results if e.timestamp <= end_date]
            if user_id:
                results = [e for e in results if e.context.user_id == user_id]
            if resource_type:
                results = [e for e in results if e.resource_type == resource_type]
            if action:
                results = [e for e in results if e.action == action]

            # Ordena por timestamp desc e limita
            results.sort(key=lambda x: x.timestamp, reverse=True)
            return results[:limit]


class AuditLogger:
    """
    Logger de auditoria centralizado para compliance LGPD.

    Registra todas as operacoes relevantes com contexto completo
    para rastreabilidade e conformidade legal.

    Example:
        >>> audit = AuditLogger(store)
        >>> await audit.log(
        ...     action=AuditAction.READ,
        ...     resource_type=ResourceType.EMPLOYEE,
        ...     resource_id="emp123",
        ...     description="Visualizacao de dados do funcionario",
        ...     pii_fields=["cpf", "salary"]
        ... )
    """

    def __init__(
        self,
        store: AuditStoreInterface,
        app_name: str = "conecta-pro",
        enable_console_output: bool = False,
        mask_pii_in_logs: bool = True
    ):
        """
        Inicializa o logger de auditoria.

        Args:
            store: Backend de armazenamento.
            app_name: Nome da aplicacao.
            enable_console_output: Se imprime logs no console.
            mask_pii_in_logs: Se mascara PII nos valores logados.
        """
        self.store = store
        self.app_name = app_name
        self.enable_console = enable_console_output
        self.mask_pii = mask_pii_in_logs
        self._pii_fields = {
            "cpf", "cnpj", "rg", "email", "phone", "password",
            "salary", "bank_account", "credit_card", "address",
            "birth_date", "health_data", "biometric"
        }
        logger.info("AuditLogger inicializado para %s", app_name)

    def set_context(self, **kwargs) -> None:
        """
        Define contexto da requisicao atual.

        Args:
            **kwargs: Campos do contexto (user_id, ip_address, etc).
        """
        ctx = _request_context.get().copy()
        ctx.update(kwargs)
        _request_context.set(ctx)

    def get_context(self) -> AuditContext:
        """Recupera contexto da requisicao atual."""
        ctx = _request_context.get()
        return AuditContext(
            request_id=ctx.get("request_id", str(uuid4())),
            user_id=ctx.get("user_id"),
            user_email=ctx.get("user_email"),
            user_role=ctx.get("user_role"),
            ip_address=ctx.get("ip_address"),
            user_agent=ctx.get("user_agent"),
            session_id=ctx.get("session_id"),
            tenant_id=ctx.get("tenant_id"),
            correlation_id=ctx.get("correlation_id"),
        )

    def clear_context(self) -> None:
        """Limpa contexto da requisicao."""
        _request_context.set({})

    def _mask_pii_values(self, data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Mascara valores PII nos dados."""
        if not data or not self.mask_pii:
            return data

        masked = data.copy()
        for key in masked:
            if key.lower() in self._pii_fields:
                value = masked[key]
                if isinstance(value, str) and len(value) > 4:
                    masked[key] = value[:2] + "*" * (len(value) - 4) + value[-2:]
                else:
                    masked[key] = "****"
        return masked

    async def log(
        self,
        action: AuditAction,
        resource_type: ResourceType,
        description: str,
        resource_id: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        pii_fields: Optional[List[str]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """
        Registra evento de auditoria.

        Args:
            action: Acao realizada.
            resource_type: Tipo do recurso.
            description: Descricao do evento.
            resource_id: ID do recurso.
            severity: Severidade do evento.
            old_value: Valor anterior (para updates).
            new_value: Novo valor.
            pii_fields: Campos PII acessados.
            success: Se operacao foi bem sucedida.
            error_message: Mensagem de erro se falhou.
            duration_ms: Duracao da operacao em ms.
            metadata: Metadados adicionais.

        Returns:
            AuditEntry: Entrada criada.
        """
        entry = AuditEntry(
            id=uuid4(),
            timestamp=datetime.utcnow(),
            action=action,
            severity=severity,
            resource_type=resource_type,
            resource_id=resource_id,
            context=self.get_context(),
            description=description,
            old_value=self._mask_pii_values(old_value),
            new_value=self._mask_pii_values(new_value),
            pii_fields_accessed=pii_fields or [],
            success=success,
            error_message=error_message,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )

        await self.store.store(entry)

        if self.enable_console:
            self._console_output(entry)

        return entry

    def _console_output(self, entry: AuditEntry) -> None:
        """Imprime entrada no console."""
        level_map = {
            AuditSeverity.DEBUG: logging.DEBUG,
            AuditSeverity.INFO: logging.INFO,
            AuditSeverity.WARNING: logging.WARNING,
            AuditSeverity.ERROR: logging.ERROR,
            AuditSeverity.CRITICAL: logging.CRITICAL,
        }
        log_level = level_map.get(entry.severity, logging.INFO)
        logger.log(
            log_level,
            "[AUDIT] %s | %s | %s:%s | %s | user=%s",
            entry.action.value,
            entry.severity.value,
            entry.resource_type.value,
            entry.resource_id or "-",
            entry.description,
            entry.context.user_id or "anonymous"
        )

    async def log_login(
        self,
        user_id: str,
        user_email: str,
        success: bool = True,
        failure_reason: Optional[str] = None
    ) -> AuditEntry:
        """Log de tentativa de login."""
        return await self.log(
            action=AuditAction.LOGIN if success else AuditAction.LOGIN_FAILED,
            resource_type=ResourceType.USER,
            resource_id=user_id,
            description=f"Login {'bem sucedido' if success else 'falhou'}: {user_email}",
            severity=AuditSeverity.INFO if success else AuditSeverity.WARNING,
            success=success,
            error_message=failure_reason,
            metadata={"email": user_email}
        )

    async def log_logout(self, user_id: str) -> AuditEntry:
        """Log de logout."""
        return await self.log(
            action=AuditAction.LOGOUT,
            resource_type=ResourceType.USER,
            resource_id=user_id,
            description="Usuario deslogado",
        )

    async def log_data_access(
        self,
        resource_type: ResourceType,
        resource_id: str,
        description: str,
        pii_fields: Optional[List[str]] = None
    ) -> AuditEntry:
        """Log de acesso a dados."""
        action = AuditAction.PII_ACCESSED if pii_fields else AuditAction.READ
        return await self.log(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            pii_fields=pii_fields,
        )

    async def log_data_modification(
        self,
        resource_type: ResourceType,
        resource_id: str,
        description: str,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        pii_fields: Optional[List[str]] = None
    ) -> AuditEntry:
        """Log de modificacao de dados."""
        action = AuditAction.PII_MODIFIED if pii_fields else AuditAction.UPDATE
        return await self.log(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            old_value=old_value,
            new_value=new_value,
            pii_fields=pii_fields,
        )

    async def log_consent_change(
        self,
        subject_id: str,
        action_type: str,
        purposes: List[str]
    ) -> AuditEntry:
        """Log de alteracao de consentimento."""
        action = AuditAction.CONSENT_GRANTED if action_type == "granted" else AuditAction.CONSENT_WITHDRAWN
        return await self.log(
            action=action,
            resource_type=ResourceType.CONSENT,
            resource_id=subject_id,
            description=f"Consentimento {action_type} para: {', '.join(purposes)}",
            metadata={"purposes": purposes}
        )

    async def log_security_event(
        self,
        description: str,
        severity: AuditSeverity = AuditSeverity.WARNING,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """Log de evento de seguranca."""
        return await self.log(
            action=AuditAction.SECURITY_ALERT,
            resource_type=ResourceType.SYSTEM,
            description=description,
            severity=severity,
            metadata=metadata,
        )

    async def query(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        action: Optional[AuditAction] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """Consulta logs de auditoria."""
        return await self.store.query(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            resource_type=resource_type,
            action=action,
            limit=limit
        )

    async def get_user_activity(
        self,
        user_id: str,
        days: int = 30
    ) -> List[AuditEntry]:
        """Recupera atividade de um usuario."""
        start_date = datetime.utcnow() - timedelta(days=days)
        return await self.query(
            start_date=start_date,
            user_id=user_id,
            limit=1000
        )

    async def get_pii_access_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Gera relatorio de acesso a PII."""
        entries = await self.query(
            start_date=start_date,
            end_date=end_date,
            action=AuditAction.PII_ACCESSED,
            limit=10000
        )

        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "total_access_events": len(entries),
            "unique_users": len(set(e.context.user_id for e in entries if e.context.user_id)),
            "by_resource_type": {},
            "by_pii_field": {},
            "by_user": {},
        }

        for entry in entries:
            # Por tipo de recurso
            rt = entry.resource_type.value
            report["by_resource_type"][rt] = report["by_resource_type"].get(rt, 0) + 1

            # Por campo PII
            for field in entry.pii_fields_accessed:
                report["by_pii_field"][field] = report["by_pii_field"].get(field, 0) + 1

            # Por usuario
            user = entry.context.user_id or "anonymous"
            report["by_user"][user] = report["by_user"].get(user, 0) + 1

        return report


# Decorador para auditoria automatica
def audit_action(
    action: AuditAction,
    resource_type: ResourceType,
    description_template: str,
    pii_fields: Optional[List[str]] = None
):
    """
    Decorador para auditoria automatica de funcoes.

    Usage:
        @audit_action(
            AuditAction.UPDATE,
            ResourceType.EMPLOYEE,
            "Atualizacao de funcionario {resource_id}",
            pii_fields=["cpf", "salary"]
        )
        async def update_employee(employee_id: str, data: dict):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            audit = get_audit_logger()
            start_time = datetime.utcnow()
            resource_id = kwargs.get('resource_id') or kwargs.get('id') or (args[0] if args else None)

            try:
                result = await func(*args, **kwargs)
                duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)

                await audit.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=str(resource_id) if resource_id else None,
                    description=description_template.format(resource_id=resource_id),
                    pii_fields=pii_fields,
                    success=True,
                    duration_ms=duration,
                )

                return result

            except Exception as e:
                duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)

                await audit.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=str(resource_id) if resource_id else None,
                    description=description_template.format(resource_id=resource_id),
                    severity=AuditSeverity.ERROR,
                    success=False,
                    error_message=str(e),
                    duration_ms=duration,
                )

                raise

        return wrapper
    return decorator


# Middleware para FastAPI
class AuditMiddleware:
    """Middleware FastAPI para contexto de auditoria."""

    def __init__(self, app, audit_logger: 'AuditLogger'):
        self.app = app
        self.audit = audit_logger

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extrai informacoes da requisicao
        headers = dict(scope.get("headers", []))
        client = scope.get("client", ("", 0))

        self.audit.set_context(
            request_id=headers.get(b"x-request-id", str(uuid4()).encode()).decode(),
            ip_address=client[0] if client else None,
            user_agent=headers.get(b"user-agent", b"").decode(),
            correlation_id=headers.get(b"x-correlation-id", b"").decode() or None,
        )

        try:
            await self.app(scope, receive, send)
        finally:
            self.audit.clear_context()


# Singleton
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Retorna instancia singleton do AuditLogger."""
    global _audit_logger
    if _audit_logger is None:
        raise RuntimeError("AuditLogger nao inicializado. Chame init_audit_logger() primeiro.")
    return _audit_logger


def init_audit_logger(
    store: Optional[AuditStoreInterface] = None,
    app_name: str = "conecta-pro",
    enable_console: bool = False
) -> AuditLogger:
    """
    Inicializa o AuditLogger singleton.

    Args:
        store: Backend de armazenamento.
        app_name: Nome da aplicacao.
        enable_console: Se imprime no console.

    Returns:
        AuditLogger: Instancia inicializada.
    """
    global _audit_logger
    if store is None:
        store = InMemoryAuditStore()
    _audit_logger = AuditLogger(store, app_name, enable_console)
    return _audit_logger
