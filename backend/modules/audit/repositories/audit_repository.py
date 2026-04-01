"""
Repository para o módulo de Auditoria e Compliance
Sprint 33: Auditoria e Compliance
"""
# pylint: disable=too-many-locals,too-many-public-methods,singleton-comparison

import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.audit.models import (
    AccessHistory,
    AccessType,
    AuditAction,
    AuditCategory,
    AuditLog,
    AuditResult,
    AuditSeverity,
    CheckResult,
    CheckStatus,
    ComplianceCheck,
    ComplianceRule,
    DataRetention,
    RetentionStatus,
    RiskLevel,
    RuleSeverity,
    RuleStatus,
)
from modules.audit.models import (
    AccessResult as AccessResultEnum,
)

logger = logging.getLogger(__name__)


class AuditRepository:
    """Repository para operações de auditoria e compliance."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== AuditLog ====================

    async def create_audit_log(self, log: AuditLog) -> AuditLog:
        """Cria um log de auditoria."""
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return log

    async def get_audit_log(self, log_id: UUID) -> AuditLog | None:
        """Busca log por ID."""
        result = await self.db.execute(select(AuditLog).where(AuditLog.id == log_id))
        return result.scalar_one_or_none()

    async def get_audit_log_by_event_id(self, event_id: str) -> AuditLog | None:
        """Busca log por event_id."""
        result = await self.db.execute(select(AuditLog).where(AuditLog.event_id == event_id))
        return result.scalar_one_or_none()

    async def list_audit_logs(
        self,
        action: AuditAction | None = None,
        category: AuditCategory | None = None,
        severity: AuditSeverity | None = None,
        result: AuditResult | None = None,
        user_id: UUID | None = None,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        requires_review: bool | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[AuditLog], int]:
        """Lista logs de auditoria com filtros."""
        query = select(AuditLog)
        count_query = select(func.count(AuditLog.id))

        conditions = []

        if action:
            conditions.append(AuditLog.action == action)
        if category:
            conditions.append(AuditLog.category == category)
        if severity:
            conditions.append(AuditLog.severity == severity)
        if result:
            conditions.append(AuditLog.result == result)
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if entity_type:
            conditions.append(AuditLog.entity_type == entity_type)
        if entity_id:
            conditions.append(AuditLog.entity_id == entity_id)
        if start_date:
            conditions.append(AuditLog.created_at >= start_date)
        if end_date:
            conditions.append(AuditLog.created_at <= end_date)
        if requires_review is not None:
            conditions.append(AuditLog.requires_review == requires_review)
        if search:
            conditions.append(
                or_(
                    AuditLog.description.ilike(f"%{search}%"),
                    AuditLog.user_email.ilike(f"%{search}%"),
                    AuditLog.entity_name.ilike(f"%{search}%"),
                )
            )

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    async def get_audit_stats(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> dict[str, Any]:
        """Retorna estatísticas de auditoria."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())

        if not start_date:
            start_date = today_start - timedelta(days=30)
        if not end_date:
            end_date = now

        # Total de eventos
        total_result = await self.db.execute(
            select(func.count(AuditLog.id)).where(AuditLog.created_at.between(start_date, end_date))
        )
        total = total_result.scalar() or 0

        # Eventos hoje
        today_result = await self.db.execute(select(func.count(AuditLog.id)).where(AuditLog.created_at >= today_start))
        today_count = today_result.scalar() or 0

        # Eventos esta semana
        week_result = await self.db.execute(select(func.count(AuditLog.id)).where(AuditLog.created_at >= week_start))
        week_count = week_result.scalar() or 0

        # Por categoria
        cat_result = await self.db.execute(
            select(AuditLog.category, func.count(AuditLog.id))
            .where(AuditLog.created_at.between(start_date, end_date))
            .group_by(AuditLog.category)
        )
        by_category = {str(row[0].value): row[1] for row in cat_result.all()}

        # Por severidade
        sev_result = await self.db.execute(
            select(AuditLog.severity, func.count(AuditLog.id))
            .where(AuditLog.created_at.between(start_date, end_date))
            .group_by(AuditLog.severity)
        )
        by_severity = {str(row[0].value): row[1] for row in sev_result.all()}

        # Por resultado
        res_result = await self.db.execute(
            select(AuditLog.result, func.count(AuditLog.id))
            .where(AuditLog.created_at.between(start_date, end_date))
            .group_by(AuditLog.result)
        )
        by_result = {str(row[0].value): row[1] for row in res_result.all()}

        # Pendentes de revisão
        review_result = await self.db.execute(
            select(func.count(AuditLog.id)).where(
                AuditLog.requires_review == True  # noqa: E712
            )
        )
        pending_reviews = review_result.scalar() or 0

        return {
            "total_events": total,
            "events_today": today_count,
            "events_this_week": week_count,
            "by_category": by_category,
            "by_severity": by_severity,
            "by_result": by_result,
            "pending_reviews": pending_reviews,
        }

    # ==================== ComplianceRule ====================

    async def create_compliance_rule(self, rule: ComplianceRule) -> ComplianceRule:
        """Cria uma regra de compliance."""
        self.db.add(rule)
        await self.db.flush()
        await self.db.refresh(rule)
        return rule

    async def get_compliance_rule(self, rule_id: UUID) -> ComplianceRule | None:
        """Busca regra por ID."""
        result = await self.db.execute(
            select(ComplianceRule).where(
                and_(
                    ComplianceRule.id == rule_id,
                    ComplianceRule.ativo == True,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_compliance_rule_by_code(self, code: str) -> ComplianceRule | None:
        """Busca regra por código."""
        result = await self.db.execute(
            select(ComplianceRule).where(
                and_(
                    ComplianceRule.code == code,
                    ComplianceRule.ativo == True,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_compliance_rules(
        self,
        framework: str | None = None,
        category: str | None = None,
        status: RuleStatus | None = None,
        severity: RuleSeverity | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[ComplianceRule], int]:
        """Lista regras de compliance."""
        query = select(ComplianceRule).where(
            ComplianceRule.ativo == True  # noqa: E712
        )
        count_query = select(func.count(ComplianceRule.id)).where(
            ComplianceRule.ativo == True  # noqa: E712
        )

        conditions = []
        if framework:
            conditions.append(ComplianceRule.framework == framework)
        if category:
            conditions.append(ComplianceRule.category == category)
        if status:
            conditions.append(ComplianceRule.status == status)
        if severity:
            conditions.append(ComplianceRule.severity == severity)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(ComplianceRule.code).offset(skip).limit(limit)
        result = await self.db.execute(query)
        rules = list(result.scalars().all())

        return rules, total

    async def update_compliance_rule(self, rule: ComplianceRule) -> ComplianceRule:
        """Atualiza uma regra de compliance."""
        await self.db.flush()
        await self.db.refresh(rule)
        return rule

    async def delete_compliance_rule(self, rule: ComplianceRule) -> None:
        """Remove uma regra (soft delete)."""
        rule.ativo = False
        rule.updated_at = datetime.utcnow()
        await self.db.flush()

    # ==================== ComplianceCheck ====================

    async def create_compliance_check(self, check: ComplianceCheck) -> ComplianceCheck:
        """Cria uma verificação de compliance."""
        self.db.add(check)
        await self.db.flush()
        await self.db.refresh(check)
        return check

    async def get_compliance_check(self, check_id: UUID) -> ComplianceCheck | None:
        """Busca verificação por ID."""
        result = await self.db.execute(
            select(ComplianceCheck).where(
                and_(
                    ComplianceCheck.id == check_id,
                    ComplianceCheck.ativo == True,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_compliance_checks(
        self,
        rule_id: UUID | None = None,
        status: CheckStatus | None = None,
        result: CheckResult | None = None,
        requires_review: bool | None = None,
        remediation_required: bool | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[ComplianceCheck], int]:
        """Lista verificações de compliance."""
        query = select(ComplianceCheck).where(
            ComplianceCheck.ativo == True  # noqa: E712
        )
        count_query = select(func.count(ComplianceCheck.id)).where(
            ComplianceCheck.ativo == True  # noqa: E712
        )

        conditions = []
        if rule_id:
            conditions.append(ComplianceCheck.rule_id == rule_id)
        if status:
            conditions.append(ComplianceCheck.status == status)
        if result:
            conditions.append(ComplianceCheck.result == result)
        if requires_review is not None:
            conditions.append(ComplianceCheck.requires_review == requires_review)
        if remediation_required is not None:
            conditions.append(ComplianceCheck.remediation_required == remediation_required)
        if start_date:
            conditions.append(ComplianceCheck.created_at >= start_date)
        if end_date:
            conditions.append(ComplianceCheck.created_at <= end_date)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(desc(ComplianceCheck.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        checks = list(result.scalars().all())

        return checks, total

    async def update_compliance_check(self, check: ComplianceCheck) -> ComplianceCheck:
        """Atualiza uma verificação de compliance."""
        await self.db.flush()
        await self.db.refresh(check)
        return check

    # ==================== DataRetention ====================

    async def create_data_retention(self, policy: DataRetention) -> DataRetention:
        """Cria uma política de retenção."""
        self.db.add(policy)
        await self.db.flush()
        await self.db.refresh(policy)
        return policy

    async def get_data_retention(self, policy_id: UUID) -> DataRetention | None:
        """Busca política por ID."""
        result = await self.db.execute(
            select(DataRetention).where(
                and_(
                    DataRetention.id == policy_id,
                    DataRetention.ativo == True,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_data_retention_by_code(self, code: str) -> DataRetention | None:
        """Busca política por código."""
        result = await self.db.execute(
            select(DataRetention).where(
                and_(
                    DataRetention.code == code,
                    DataRetention.ativo == True,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_data_retention_policies(
        self,
        data_category: str | None = None,
        status: RetentionStatus | None = None,
        schedule_enabled: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[DataRetention], int]:
        """Lista políticas de retenção."""
        query = select(DataRetention).where(
            DataRetention.ativo == True  # noqa: E712
        )
        count_query = select(func.count(DataRetention.id)).where(
            DataRetention.ativo == True  # noqa: E712
        )

        conditions = []
        if data_category:
            conditions.append(DataRetention.data_category == data_category)
        if status:
            conditions.append(DataRetention.status == status)
        if schedule_enabled is not None:
            conditions.append(DataRetention.schedule_enabled == schedule_enabled)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(DataRetention.code).offset(skip).limit(limit)
        result = await self.db.execute(query)
        policies = list(result.scalars().all())

        return policies, total

    async def update_data_retention(self, policy: DataRetention) -> DataRetention:
        """Atualiza uma política de retenção."""
        await self.db.flush()
        await self.db.refresh(policy)
        return policy

    async def delete_data_retention(self, policy: DataRetention) -> None:
        """Remove uma política (soft delete)."""
        policy.ativo = False
        policy.updated_at = datetime.utcnow()
        await self.db.flush()

    async def get_due_retention_policies(self) -> list[DataRetention]:
        """Busca políticas que devem ser executadas."""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(DataRetention).where(
                and_(
                    DataRetention.ativo == True,  # noqa: E712
                    DataRetention.status == RetentionStatus.ACTIVE,
                    DataRetention.schedule_enabled == True,  # noqa: E712
                    DataRetention.legal_hold_enabled == False,  # noqa: E712
                    or_(
                        DataRetention.next_execution_at == None,  # noqa: E711
                        DataRetention.next_execution_at <= now,
                    ),
                )
            )
        )
        return list(result.scalars().all())

    # ==================== AccessHistory ====================

    async def create_access_history(self, access: AccessHistory) -> AccessHistory:
        """Cria um registro de acesso."""
        self.db.add(access)
        await self.db.flush()
        await self.db.refresh(access)
        return access

    async def get_access_history(self, access_id: UUID) -> AccessHistory | None:
        """Busca registro por ID."""
        result = await self.db.execute(select(AccessHistory).where(AccessHistory.id == access_id))
        return result.scalar_one_or_none()

    async def list_access_history(
        self,
        access_type: AccessType | None = None,
        result: AccessResultEnum | None = None,
        user_id: UUID | None = None,
        ip_address: str | None = None,
        risk_level: RiskLevel | None = None,
        anomaly_detected: bool | None = None,
        requires_review: bool | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[AccessHistory], int]:
        """Lista registros de acesso."""
        query = select(AccessHistory)
        count_query = select(func.count(AccessHistory.id))

        conditions = []
        if access_type:
            conditions.append(AccessHistory.access_type == access_type)
        if result:
            conditions.append(AccessHistory.result == result)
        if user_id:
            conditions.append(AccessHistory.user_id == user_id)
        if ip_address:
            conditions.append(AccessHistory.ip_address == ip_address)
        if risk_level:
            conditions.append(AccessHistory.risk_level == risk_level)
        if anomaly_detected is not None:
            conditions.append(AccessHistory.anomaly_detected == anomaly_detected)
        if requires_review is not None:
            conditions.append(AccessHistory.requires_review == requires_review)
        if start_date:
            conditions.append(AccessHistory.accessed_at >= start_date)
        if end_date:
            conditions.append(AccessHistory.accessed_at <= end_date)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(desc(AccessHistory.accessed_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        accesses = list(result.scalars().all())

        return accesses, total

    async def get_access_stats(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> dict[str, Any]:
        """Retorna estatísticas de acessos."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if not start_date:
            start_date = today_start
        if not end_date:
            end_date = now

        # Total de acessos
        total_result = await self.db.execute(
            select(func.count(AccessHistory.id)).where(AccessHistory.accessed_at.between(start_date, end_date))
        )
        total = total_result.scalar() or 0

        # Logins bem-sucedidos
        success_result = await self.db.execute(
            select(func.count(AccessHistory.id)).where(
                and_(
                    AccessHistory.accessed_at.between(start_date, end_date),
                    AccessHistory.access_type == AccessType.LOGIN,
                    AccessHistory.result == AccessResultEnum.SUCCESS,
                )
            )
        )
        successful_logins = success_result.scalar() or 0

        # Logins com falha
        failed_result = await self.db.execute(
            select(func.count(AccessHistory.id)).where(
                and_(
                    AccessHistory.accessed_at.between(start_date, end_date),
                    AccessHistory.access_type == AccessType.LOGIN,
                    AccessHistory.result == AccessResultEnum.FAILURE,
                )
            )
        )
        failed_logins = failed_result.scalar() or 0

        # Usuários únicos
        users_result = await self.db.execute(
            select(func.count(func.distinct(AccessHistory.user_id))).where(
                AccessHistory.accessed_at.between(start_date, end_date)
            )
        )
        unique_users = users_result.scalar() or 0

        # IPs únicos
        ips_result = await self.db.execute(
            select(func.count(func.distinct(AccessHistory.ip_address))).where(
                AccessHistory.accessed_at.between(start_date, end_date)
            )
        )
        unique_ips = ips_result.scalar() or 0

        # Por tipo de acesso
        type_result = await self.db.execute(
            select(AccessHistory.access_type, func.count(AccessHistory.id))
            .where(AccessHistory.accessed_at.between(start_date, end_date))
            .group_by(AccessHistory.access_type)
        )
        by_type = {str(row[0].value): row[1] for row in type_result.all()}

        # Por resultado
        res_result = await self.db.execute(
            select(AccessHistory.result, func.count(AccessHistory.id))
            .where(AccessHistory.accessed_at.between(start_date, end_date))
            .group_by(AccessHistory.result)
        )
        by_result = {str(row[0].value): row[1] for row in res_result.all()}

        # Acessos de alto risco
        high_risk_result = await self.db.execute(
            select(func.count(AccessHistory.id)).where(
                and_(
                    AccessHistory.accessed_at.between(start_date, end_date),
                    AccessHistory.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]),
                )
            )
        )
        high_risk = high_risk_result.scalar() or 0

        # Anomalias detectadas
        anomaly_result = await self.db.execute(
            select(func.count(AccessHistory.id)).where(
                and_(
                    AccessHistory.accessed_at.between(start_date, end_date),
                    AccessHistory.anomaly_detected == True,  # noqa: E712
                )
            )
        )
        anomalies = anomaly_result.scalar() or 0

        # Pendentes de revisão
        review_result = await self.db.execute(
            select(func.count(AccessHistory.id)).where(
                AccessHistory.requires_review == True  # noqa: E712
            )
        )
        pending_reviews = review_result.scalar() or 0

        return {
            "total_accesses": total,
            "successful_logins": successful_logins,
            "failed_logins": failed_logins,
            "unique_users": unique_users,
            "unique_ips": unique_ips,
            "by_access_type": by_type,
            "by_result": by_result,
            "high_risk_accesses": high_risk,
            "anomalies_detected": anomalies,
            "pending_reviews": pending_reviews,
        }

    async def get_user_access_history(self, user_id: UUID, limit: int = 50) -> list[AccessHistory]:
        """Busca histórico de acessos de um usuário."""
        result = await self.db.execute(
            select(AccessHistory)
            .where(AccessHistory.user_id == user_id)
            .order_by(desc(AccessHistory.accessed_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_ip_access_history(self, ip_address: str, limit: int = 50) -> list[AccessHistory]:
        """Busca histórico de acessos de um IP."""
        result = await self.db.execute(
            select(AccessHistory)
            .where(AccessHistory.ip_address == ip_address)
            .order_by(desc(AccessHistory.accessed_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    # ==================== Compliance Overview ====================

    async def get_compliance_overview(self) -> dict[str, Any]:
        """Retorna visão geral de compliance."""
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Total de regras
        total_result = await self.db.execute(
            select(func.count(ComplianceRule.id)).where(
                ComplianceRule.ativo == True  # noqa: E712
            )
        )
        total_rules = total_result.scalar() or 0

        # Regras ativas
        active_result = await self.db.execute(
            select(func.count(ComplianceRule.id)).where(
                and_(
                    ComplianceRule.ativo == True,  # noqa: E712
                    ComplianceRule.status == RuleStatus.ACTIVE,
                )
            )
        )
        active_rules = active_result.scalar() or 0

        # Por framework
        framework_result = await self.db.execute(
            select(ComplianceRule.framework, func.count(ComplianceRule.id))
            .where(ComplianceRule.ativo == True)  # noqa: E712
            .group_by(ComplianceRule.framework)
        )
        by_framework = {str(row[0].value): row[1] for row in framework_result.all()}

        # Por status
        status_result = await self.db.execute(
            select(ComplianceRule.status, func.count(ComplianceRule.id))
            .where(ComplianceRule.ativo == True)  # noqa: E712
            .group_by(ComplianceRule.status)
        )
        by_status = {str(row[0].value): row[1] for row in status_result.all()}

        # Total de verificações
        checks_result = await self.db.execute(
            select(func.count(ComplianceCheck.id)).where(
                ComplianceCheck.ativo == True  # noqa: E712
            )
        )
        total_checks = checks_result.scalar() or 0

        # Verificações este mês
        month_checks_result = await self.db.execute(
            select(func.count(ComplianceCheck.id)).where(
                and_(
                    ComplianceCheck.ativo == True,  # noqa: E712
                    ComplianceCheck.created_at >= month_start,
                )
            )
        )
        checks_this_month = month_checks_result.scalar() or 0

        # Remediações pendentes
        pending_result = await self.db.execute(
            select(func.count(ComplianceCheck.id)).where(
                and_(
                    ComplianceCheck.ativo == True,  # noqa: E712
                    ComplianceCheck.remediation_required == True,  # noqa: E712
                    ComplianceCheck.remediation_completed_at == None,  # noqa: E711
                )
            )
        )
        pending_remediations = pending_result.scalar() or 0

        # Remediações atrasadas
        overdue_result = await self.db.execute(
            select(func.count(ComplianceCheck.id)).where(
                and_(
                    ComplianceCheck.ativo == True,  # noqa: E712
                    ComplianceCheck.remediation_required == True,  # noqa: E712
                    ComplianceCheck.remediation_completed_at == None,  # noqa: E711
                    ComplianceCheck.remediation_deadline < now,
                )
            )
        )
        overdue_remediations = overdue_result.scalar() or 0

        # Violações críticas
        critical_result = await self.db.execute(
            select(func.count(ComplianceCheck.id)).where(
                and_(
                    ComplianceCheck.ativo == True,  # noqa: E712
                    ComplianceCheck.critical_violations > 0,
                )
            )
        )
        critical_violations = critical_result.scalar() or 0

        return {
            "total_rules": total_rules,
            "active_rules": active_rules,
            "rules_by_framework": by_framework,
            "rules_by_status": by_status,
            "total_checks": total_checks,
            "checks_this_month": checks_this_month,
            "pending_remediations": pending_remediations,
            "overdue_remediations": overdue_remediations,
            "critical_violations": critical_violations,
        }
