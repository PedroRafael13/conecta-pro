"""
Audit Logger - Sistema de auditoria completo para Gestao de Pessoas.
Registra: QUEM fez O QUE, QUANDO e DE ONDE.
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class AuditAction(StrEnum):
    """Tipos de acoes que podem ser auditadas."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SIGN = "sign"
    EXPORT = "export"
    IMPORT = "import"
    LOGIN = "login"
    LOGOUT = "logout"
    CLOCK_PUNCH = "clock_punch"
    APPROVE = "approve"
    REJECT = "reject"
    SYNC = "sync"
    SEND = "send"


@dataclass
class AuditActor:
    """Quem realizou a acao."""

    user_id: str
    user_name: str
    user_role: str
    user_module: str


@dataclass
class AuditContext:
    """Contexto da acao."""

    ip_address: str
    user_agent: str
    device_type: str
    session_id: str
    geolocation: dict[str, float] | None = None


@dataclass
class AuditChange:
    """Mudanca em um campo."""

    field: str
    old_value: Any
    new_value: Any


@dataclass
class AuditLog:
    """Registro de auditoria."""

    action: AuditAction
    entity: str
    entity_id: str
    description: str
    source_module: str
    actor: AuditActor
    context: AuditContext
    id: str = None
    timestamp: datetime = None
    changes: list[AuditChange] = None
    related_funcionario_id: str | None = None
    related_documento_id: str | None = None
    affected_modules: list[str] = None
    extra_data: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.id is None:
            self.id = str(uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.changes is None:
            self.changes = []
        if self.affected_modules is None:
            self.affected_modules = []
        if self.extra_data is None:
            self.extra_data = {}

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "entity": self.entity,
            "entity_id": self.entity_id,
            "description": self.description,
            "source_module": self.source_module,
            "actor": asdict(self.actor),
            "context": asdict(self.context),
            "changes": [asdict(c) for c in self.changes],
            "related_funcionario_id": self.related_funcionario_id,
            "related_documento_id": self.related_documento_id,
            "affected_modules": self.affected_modules,
            "extra_data": self.extra_data,
        }


class AuditLogger:
    """
    Logger de auditoria para Gestao de Pessoas.

    Uso:
        audit = get_audit_logger()
        await audit.log(
            action=AuditAction.CREATE,
            entity="documento",
            entity_id="123",
            description="Criou documento de suspensao",
            source_module="OPS",
            actor=AuditActor(...),
            context=AuditContext(...),
        )
    """

    def __init__(self) -> None:
        self._buffer: list[AuditLog] = []

    async def log(
        self,
        action: AuditAction,
        entity: str,
        entity_id: str,
        description: str,
        source_module: str,
        actor: AuditActor,
        context: AuditContext,
        changes: list[AuditChange] | None = None,
        related_funcionario_id: str | None = None,
        related_documento_id: str | None = None,
        affected_modules: list[str] | None = None,
        extra_data: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Registra uma acao no log de auditoria."""
        audit_log = AuditLog(
            action=action,
            entity=entity,
            entity_id=entity_id,
            description=description,
            source_module=source_module,
            actor=actor,
            context=context,
            changes=changes,
            related_funcionario_id=related_funcionario_id,
            related_documento_id=related_documento_id,
            affected_modules=affected_modules,
            extra_data=extra_data,
        )

        logger.info(
            f"AUDIT: [{audit_log.action.value}] {audit_log.entity}/{audit_log.entity_id} "
            f"by {audit_log.actor.user_name} ({audit_log.actor.user_module}) - "
            f"{audit_log.description}"
        )

        self._buffer.append(audit_log)
        return audit_log

    async def query(
        self,
        entity: str | None = None,
        entity_id: str | None = None,
        actor_user_id: str | None = None,
        action: AuditAction | None = None,
        source_module: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        """Consulta logs de auditoria."""
        results = self._buffer.copy()

        if entity:
            results = [r for r in results if r.entity == entity]
        if entity_id:
            results = [r for r in results if r.entity_id == entity_id]
        if actor_user_id:
            results = [r for r in results if r.actor.user_id == actor_user_id]
        if action:
            results = [r for r in results if r.action == action]
        if source_module:
            results = [r for r in results if r.source_module == source_module]

        return results[offset : offset + limit]

    @property
    def buffer_size(self) -> int:
        return len(self._buffer)


# Singleton
_audit_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Retorna instancia singleton do Audit Logger."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
