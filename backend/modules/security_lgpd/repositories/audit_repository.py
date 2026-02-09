"""
Repository de Auditoria LGPD.
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from modules.security_lgpd.models.audit_log import (
    AuditAction,
    AuditLog,
    AuditSeverity,
    ResourceType,
)

logger = logging.getLogger(__name__)


class AuditRepository:
    """Repository para operacoes de persistencia de logs de auditoria.

    Encapsula o acesso ao banco de dados para a entidade AuditLog.
    """

    def __init__(self, db: Session):
        """Inicializa o repository.

        Args:
            db: Sessao do banco de dados.
        """
        self.db = db

    def create(self, log: AuditLog) -> AuditLog:
        """Cria um novo log de auditoria.

        Args:
            log: Instancia do log.

        Returns:
            Log criado.
        """
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_by_id(self, log_id: UUID) -> AuditLog | None:
        """Busca log por ID.

        Args:
            log_id: UUID do log.

        Returns:
            Log ou None.
        """
        return self.db.query(AuditLog).filter(AuditLog.id == log_id).first()

    def query(
        self,
        action: AuditAction | None = None,
        resource_type: ResourceType | None = None,
        resource_id: str | None = None,
        user_id: str | None = None,
        severity: AuditSeverity | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        """Consulta logs de auditoria com filtros.

        Args:
            action: Filtro por acao.
            resource_type: Filtro por tipo de recurso.
            resource_id: Filtro por ID do recurso.
            user_id: Filtro por usuario.
            severity: Filtro por severidade.
            start_date: Data inicial.
            end_date: Data final.
            limit: Limite de resultados.
            offset: Offset para paginacao.

        Returns:
            Lista de logs.
        """
        query = self.db.query(AuditLog)

        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if severity:
            query = query.filter(AuditLog.severity == severity)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    def get_by_resource(
        self,
        resource_type: ResourceType,
        resource_id: str,
        limit: int = 50,
    ) -> list[AuditLog]:
        """Busca logs de um recurso especifico.

        Args:
            resource_type: Tipo do recurso.
            resource_id: ID do recurso.
            limit: Limite de resultados.

        Returns:
            Lista de logs.
        """
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.resource_type == resource_type)
            .filter(AuditLog.resource_id == resource_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_user(
        self,
        user_id: str,
        start_date: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Busca logs de um usuario especifico.

        Args:
            user_id: ID do usuario.
            start_date: Data inicial.
            limit: Limite de resultados.

        Returns:
            Lista de logs.
        """
        query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)

        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)

        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    def get_last_hash(self) -> str | None:
        """Retorna o hash do ultimo log para hash chain.

        Returns:
            Hash do ultimo log ou None.
        """
        last_log = self.db.query(AuditLog).order_by(AuditLog.created_at.desc()).first()
        return last_log.event_hash if last_log else None

    def count_by_action(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict:
        """Conta logs por acao.

        Args:
            start_date: Data inicial.
            end_date: Data final.

        Returns:
            Dict com contagens por acao.
        """
        from sqlalchemy import func

        query = self.db.query(AuditLog.action, func.count(AuditLog.id))

        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        result = query.group_by(AuditLog.action).all()
        return {action.value: count for action, count in result}
