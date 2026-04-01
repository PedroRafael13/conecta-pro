"""
AuditService - Serviço principal de auditoria e compliance
Sprint 33: Auditoria e Compliance
"""
# pylint: disable=too-many-locals,too-many-public-methods

import logging
from datetime import datetime, timedelta
from uuid import UUID

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
    CheckType,
    ComplianceCheck,
    ComplianceRule,
    DataCategory,
    DataRetention,
    RetentionAction,
    RetentionPeriod,
    RetentionStatus,
    RiskLevel,
    RuleSeverity,
    RuleStatus,
)
from modules.audit.models import (
    AccessResult as AccessResultEnum,
)
from modules.audit.repositories import AuditRepository
from modules.audit.schemas import (
    AccessHistoryCreate,
    AccessHistoryStats,
    AuditDashboard,
    AuditLogCreate,
    AuditLogStats,
    ComplianceCheckCreate,
    ComplianceOverview,
    ComplianceRuleCreate,
    ComplianceRuleUpdate,
    DataRetentionCreate,
    DataRetentionExecution,
    DataRetentionUpdate,
    SecurityOverview,
)

logger = logging.getLogger(__name__)


class AuditService:
    """Serviço para auditoria e compliance."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = AuditRepository(db)

    # ==================== AuditLog ====================

    async def create_audit_log(self, data: AuditLogCreate, correlation_id: str | None = None) -> AuditLog:
        """Cria um log de auditoria."""
        log = AuditLog.create_event(
            action=AuditAction(data.action),
            category=AuditCategory(data.category),
            description=data.description,
            user_id=str(data.user_id) if data.user_id else None,
            user_email=data.user_email,
            entity_type=data.entity_type,
            entity_id=str(data.entity_id) if data.entity_id else None,
            severity=AuditSeverity(data.severity),
            result=AuditResult(data.result),
            ip_address=data.ip_address,
            user_agent=data.user_agent,
            old_values=data.old_values,
            new_values=data.new_values,
            metadata=data.metadata,
            tags=data.tags,
            correlation_id=correlation_id,
        )

        # Detecta campos alterados
        if data.old_values and data.new_values:
            changed = []
            for key in set(data.old_values.keys()) | set(data.new_values.keys()):
                if data.old_values.get(key) != data.new_values.get(key):
                    changed.append(key)
            log.changed_fields = changed

        # Marca como sensível se necessário
        if data.entity_type in ["user", "password", "financial", "document"]:
            log.is_sensitive = True
        if data.entity_type in ["user", "personal_data"]:
            log.is_pii = True

        # Marca para revisão se severidade alta
        if log.severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
            log.requires_review = True

        created = await self.repository.create_audit_log(log)
        await self.db.commit()

        logger.info("Audit log created: %s - %s by %s", created.event_id, data.action, data.user_email)
        return created

    async def log_action(
        self,
        action: str,
        category: str,
        description: str,
        user_id: str | None = None,
        user_email: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        ip_address: str | None = None,
        **kwargs,
    ) -> AuditLog:
        """Helper para logar ações rapidamente."""
        data = AuditLogCreate(
            action=action,
            category=category,
            description=description,
            user_id=UUID(user_id) if user_id else None,
            user_email=user_email,
            entity_type=entity_type,
            entity_id=UUID(entity_id) if entity_id else None,
            ip_address=ip_address,
            **kwargs,
        )
        return await self.create_audit_log(data)

    async def get_audit_log(self, log_id: UUID) -> AuditLog | None:
        """Busca log por ID."""
        return await self.repository.get_audit_log(log_id)

    async def list_audit_logs(
        self,
        action: str | None = None,
        category: str | None = None,
        severity: str | None = None,
        result: str | None = None,
        user_id: UUID | None = None,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        requires_review: bool | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AuditLog], int]:
        """Lista logs de auditoria."""
        skip = (page - 1) * page_size
        return await self.repository.list_audit_logs(
            action=AuditAction(action) if action else None,
            category=AuditCategory(category) if category else None,
            severity=AuditSeverity(severity) if severity else None,
            result=AuditResult(result) if result else None,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            start_date=start_date,
            end_date=end_date,
            requires_review=requires_review,
            search=search,
            skip=skip,
            limit=page_size,
        )

    async def get_audit_stats(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> AuditLogStats:
        """Retorna estatísticas de auditoria."""
        stats = await self.repository.get_audit_stats(start_date, end_date)
        return AuditLogStats(**stats)

    async def complete_review(self, log_id: UUID, reviewer_id: str, notes: str | None = None) -> AuditLog:
        """Completa revisão de um log."""
        log = await self.repository.get_audit_log(log_id)
        if not log:
            raise ValueError(f"Log {log_id} não encontrado")

        log.complete_review(reviewer_id, notes)
        await self.db.commit()
        return log

    # ==================== ComplianceRule ====================

    async def create_compliance_rule(self, data: ComplianceRuleCreate, user_id: str | None = None) -> ComplianceRule:
        """Cria uma regra de compliance."""
        # Verifica se código já existe
        existing = await self.repository.get_compliance_rule_by_code(data.code)
        if existing:
            raise ValueError(f"Regra com código {data.code} já existe")

        rule = ComplianceRule(
            code=data.code,
            name=data.name,
            description=data.description,
            framework=data.framework,
            framework_reference=data.framework_reference,
            category=data.category,
            severity=RuleSeverity(data.severity),
            requirement_text=data.requirement_text,
            implementation_guidance=data.implementation_guidance,
            evidence_required=data.evidence_required,
            validation_query=data.validation_query,
            validation_frequency_hours=data.validation_frequency_hours,
            auto_validate=data.auto_validate,
            applies_to_entities=data.applies_to_entities,
            applies_to_roles=data.applies_to_roles,
            notify_on_violation=data.notify_on_violation,
            notification_recipients=data.notification_recipients,
            remediation_steps=data.remediation_steps,
            remediation_deadline_days=data.remediation_deadline_days,
            documentation_url=data.documentation_url,
            tags=data.tags,
            created_by=user_id,
        )

        created = await self.repository.create_compliance_rule(rule)
        await self.db.commit()

        logger.info("Compliance rule created: %s", created.code)
        return created

    async def get_compliance_rule(self, rule_id: UUID) -> ComplianceRule | None:
        """Busca regra por ID."""
        return await self.repository.get_compliance_rule(rule_id)

    async def list_compliance_rules(
        self,
        framework: str | None = None,
        category: str | None = None,
        status: str | None = None,
        severity: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[ComplianceRule], int]:
        """Lista regras de compliance."""
        skip = (page - 1) * page_size
        return await self.repository.list_compliance_rules(
            framework=framework,
            category=category,
            status=RuleStatus(status) if status else None,
            severity=RuleSeverity(severity) if severity else None,
            skip=skip,
            limit=page_size,
        )

    async def update_compliance_rule(
        self, rule_id: UUID, data: ComplianceRuleUpdate, user_id: str | None = None
    ) -> ComplianceRule:
        """Atualiza uma regra de compliance."""
        rule = await self.repository.get_compliance_rule(rule_id)
        if not rule:
            raise ValueError(f"Regra {rule_id} não encontrada")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value:
                setattr(rule, field, RuleStatus(value))
            elif field == "severity" and value:
                setattr(rule, field, RuleSeverity(value))
            else:
                setattr(rule, field, value)

        rule.updated_by = user_id
        rule.updated_at = datetime.utcnow()

        updated = await self.repository.update_compliance_rule(rule)
        await self.db.commit()
        return updated

    async def activate_rule(self, rule_id: UUID) -> ComplianceRule:
        """Ativa uma regra de compliance."""
        rule = await self.repository.get_compliance_rule(rule_id)
        if not rule:
            raise ValueError(f"Regra {rule_id} não encontrada")

        rule.activate()
        await self.db.commit()
        return rule

    async def delete_compliance_rule(self, rule_id: UUID) -> None:
        """Remove uma regra de compliance."""
        rule = await self.repository.get_compliance_rule(rule_id)
        if not rule:
            raise ValueError(f"Regra {rule_id} não encontrada")

        await self.repository.delete_compliance_rule(rule)
        await self.db.commit()

    # ==================== ComplianceCheck ====================

    async def create_compliance_check(self, data: ComplianceCheckCreate, user_id: str | None = None) -> ComplianceCheck:
        """Cria uma verificação de compliance."""
        rule = await self.repository.get_compliance_rule(data.rule_id)
        if not rule:
            raise ValueError(f"Regra {data.rule_id} não encontrada")

        check = ComplianceCheck.create_check(
            rule_id=str(data.rule_id), check_type=CheckType(data.check_type), executed_by=user_id
        )
        check.scope_description = data.scope_description
        check.scheduled_at = data.scheduled_at
        check.created_by = user_id

        created = await self.repository.create_compliance_check(check)
        await self.db.commit()

        logger.info("Compliance check created: %s for rule %s", created.check_number, rule.code)
        return created

    async def get_compliance_check(self, check_id: UUID) -> ComplianceCheck | None:
        """Busca verificação por ID."""
        return await self.repository.get_compliance_check(check_id)

    async def list_compliance_checks(
        self,
        rule_id: UUID | None = None,
        status: str | None = None,
        result: str | None = None,
        requires_review: bool | None = None,
        remediation_required: bool | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[ComplianceCheck], int]:
        """Lista verificações de compliance."""
        skip = (page - 1) * page_size
        return await self.repository.list_compliance_checks(
            rule_id=rule_id,
            status=CheckStatus(status) if status else None,
            result=CheckResult(result) if result else None,
            requires_review=requires_review,
            remediation_required=remediation_required,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=page_size,
        )

    async def start_check(self, check_id: UUID, executor_id: str) -> ComplianceCheck:
        """Inicia uma verificação."""
        check = await self.repository.get_compliance_check(check_id)
        if not check:
            raise ValueError(f"Verificação {check_id} não encontrada")

        check.start(executor_id)
        await self.db.commit()
        return check

    async def complete_check_compliant(
        self, check_id: UUID, evidence: dict | None = None, notes: str | None = None
    ) -> ComplianceCheck:
        """Marca verificação como conforme."""
        check = await self.repository.get_compliance_check(check_id)
        if not check:
            raise ValueError(f"Verificação {check_id} não encontrada")

        check.complete_compliant(evidence, notes)

        # Atualiza métricas da regra
        rule = await self.repository.get_compliance_rule(check.rule_id)
        if rule:
            rule.record_check(passed=True)

        await self.db.commit()
        return check

    async def complete_check_non_compliant(
        self, check_id: UUID, violations: list, remediation_deadline_days: int | None = None
    ) -> ComplianceCheck:
        """Marca verificação como não conforme."""
        check = await self.repository.get_compliance_check(check_id)
        if not check:
            raise ValueError(f"Verificação {check_id} não encontrada")

        deadline = None
        if remediation_deadline_days:
            deadline = datetime.utcnow() + timedelta(days=remediation_deadline_days)

        check.complete_non_compliant(violations=violations, remediation_required=True, remediation_deadline=deadline)

        # Atualiza métricas da regra
        rule = await self.repository.get_compliance_rule(check.rule_id)
        if rule:
            rule.record_check(passed=False)

        await self.db.commit()
        return check

    # ==================== DataRetention ====================

    async def create_data_retention(self, data: DataRetentionCreate, user_id: str | None = None) -> DataRetention:
        """Cria uma política de retenção."""
        existing = await self.repository.get_data_retention_by_code(data.code)
        if existing:
            raise ValueError(f"Política com código {data.code} já existe")

        policy = DataRetention(
            code=data.code,
            name=data.name,
            description=data.description,
            data_category=DataCategory(data.data_category),
            retention_period=RetentionPeriod(data.retention_period),
            retention_days=data.retention_days,
            expiration_action=RetentionAction(data.expiration_action),
            secondary_action=(RetentionAction(data.secondary_action) if data.secondary_action else None),
            entity_types=data.entity_types,
            table_names=data.table_names,
            compliance_framework=data.compliance_framework,
            compliance_reference=data.compliance_reference,
            legal_basis=data.legal_basis,
            anonymize_fields=data.anonymize_fields,
            archive_location=data.archive_location,
            notify_before_days=data.notify_before_days,
            notify_recipients=data.notify_recipients,
            schedule_cron=data.schedule_cron,
            tags=data.tags,
            created_by=user_id,
        )

        created = await self.repository.create_data_retention(policy)
        await self.db.commit()

        logger.info("Data retention policy created: %s", created.code)
        return created

    async def get_data_retention(self, policy_id: UUID) -> DataRetention | None:
        """Busca política por ID."""
        return await self.repository.get_data_retention(policy_id)

    async def list_data_retention_policies(
        self,
        data_category: str | None = None,
        status: str | None = None,
        schedule_enabled: bool | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[DataRetention], int]:
        """Lista políticas de retenção."""
        skip = (page - 1) * page_size
        return await self.repository.list_data_retention_policies(
            data_category=data_category,
            status=RetentionStatus(status) if status else None,
            schedule_enabled=schedule_enabled,
            skip=skip,
            limit=page_size,
        )

    async def update_data_retention(
        self, policy_id: UUID, data: DataRetentionUpdate, user_id: str | None = None
    ) -> DataRetention:
        """Atualiza uma política de retenção."""
        policy = await self.repository.get_data_retention(policy_id)
        if not policy:
            raise ValueError(f"Política {policy_id} não encontrada")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value:
                setattr(policy, field, RetentionStatus(value))
            elif field == "retention_period" and value:
                setattr(policy, field, RetentionPeriod(value))
            elif field == "expiration_action" and value:
                setattr(policy, field, RetentionAction(value))
            else:
                setattr(policy, field, value)

        policy.updated_by = user_id
        policy.updated_at = datetime.utcnow()

        updated = await self.repository.update_data_retention(policy)
        await self.db.commit()
        return updated

    async def execute_retention_policy(self, policy_id: UUID) -> DataRetentionExecution:
        """Executa uma política de retenção."""
        policy = await self.repository.get_data_retention(policy_id)
        if not policy:
            raise ValueError(f"Política {policy_id} não encontrada")

        if policy.legal_hold_enabled:
            raise ValueError("Política está em legal hold")

        start_time = datetime.utcnow()

        # Simula execução - em produção, executaria queries reais
        records_affected = 0
        deleted = 0
        archived = 0
        anonymized = 0
        storage_freed = 0

        try:
            # Aqui executaria a lógica real de retenção
            # Por enquanto, apenas registra a execução
            policy.record_execution(
                records_affected=records_affected,
                deleted=deleted,
                archived=archived,
                anonymized=anonymized,
                storage_freed=storage_freed,
            )
            await self.db.commit()

            duration = int((datetime.utcnow() - start_time).total_seconds())

            return DataRetentionExecution(
                policy_id=policy.id,
                policy_code=policy.code,
                execution_at=start_time,
                records_affected=records_affected,
                records_deleted=deleted,
                records_archived=archived,
                records_anonymized=anonymized,
                storage_freed_bytes=storage_freed,
                duration_seconds=duration,
                success=True,
            )

        except Exception as e:
            policy.record_error(str(e))
            await self.db.commit()
            raise

    async def delete_data_retention(self, policy_id: UUID) -> None:
        """Remove uma política de retenção."""
        policy = await self.repository.get_data_retention(policy_id)
        if not policy:
            raise ValueError(f"Política {policy_id} não encontrada")

        await self.repository.delete_data_retention(policy)
        await self.db.commit()

    # ==================== AccessHistory ====================

    async def record_access(self, data: AccessHistoryCreate) -> AccessHistory:
        """Registra um acesso."""
        access = AccessHistory(
            access_type=AccessType(data.access_type),
            result=AccessResultEnum(data.result),
            user_id=data.user_id,
            user_email=data.user_email,
            resource_path=data.resource_path,
            http_method=data.http_method,
            ip_address=data.ip_address,
            user_agent=data.user_agent,
            session_id=data.session_id,
            auth_method=data.auth_method,
            mfa_used=data.mfa_used,
            device_fingerprint=data.device_fingerprint,
            metadata=data.metadata,
        )

        # Calcula risco
        access.calculate_risk()

        created = await self.repository.create_access_history(access)
        await self.db.commit()

        logger.debug("Access recorded: %s - %s from %s", data.access_type, data.result, data.ip_address)
        return created

    async def record_login(
        self, user_id: str, user_email: str, ip_address: str, success: bool, **kwargs
    ) -> AccessHistory:
        """Helper para registrar login."""
        data = AccessHistoryCreate(
            access_type="login",
            result="success" if success else "failure",
            user_id=UUID(user_id),
            user_email=user_email,
            ip_address=ip_address,
            **kwargs,
        )
        return await self.record_access(data)

    async def get_access_history(self, access_id: UUID) -> AccessHistory | None:
        """Busca registro por ID."""
        return await self.repository.get_access_history(access_id)

    async def list_access_history(
        self,
        access_type: str | None = None,
        result: str | None = None,
        user_id: UUID | None = None,
        ip_address: str | None = None,
        risk_level: str | None = None,
        anomaly_detected: bool | None = None,
        requires_review: bool | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AccessHistory], int]:
        """Lista registros de acesso."""
        skip = (page - 1) * page_size
        return await self.repository.list_access_history(
            access_type=AccessType(access_type) if access_type else None,
            result=AccessResultEnum(result) if result else None,
            user_id=user_id,
            ip_address=ip_address,
            risk_level=RiskLevel(risk_level) if risk_level else None,
            anomaly_detected=anomaly_detected,
            requires_review=requires_review,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=page_size,
        )

    async def get_access_stats(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> AccessHistoryStats:
        """Retorna estatísticas de acessos."""
        stats = await self.repository.get_access_stats(start_date, end_date)
        return AccessHistoryStats(**stats)

    async def get_user_access_history(self, user_id: UUID, limit: int = 50) -> list[AccessHistory]:
        """Busca histórico de acessos de um usuário."""
        return await self.repository.get_user_access_history(user_id, limit)

    # ==================== Dashboard ====================

    async def get_audit_dashboard(self) -> AuditDashboard:
        """Retorna dashboard de auditoria."""
        audit_stats = await self.get_audit_stats()
        access_stats = await self.get_access_stats()

        _logs, _ = await self.list_audit_logs(page_size=10)
        _accesses, _ = await self.list_access_history(page_size=10)

        return AuditDashboard(
            audit_stats=audit_stats,
            access_stats=access_stats,
            recent_events=[],  # Converteria para response
            recent_accesses=[],
            alerts=[],
            trends={},
        )

    async def get_compliance_overview(self) -> ComplianceOverview:
        """Retorna visão geral de compliance."""
        overview = await self.repository.get_compliance_overview()
        return ComplianceOverview(**overview)

    async def get_security_overview(self) -> SecurityOverview:
        """Retorna visão geral de segurança."""
        stats = await self.get_access_stats()

        return SecurityOverview(
            total_accesses_today=stats.total_accesses,
            failed_logins_today=stats.failed_logins,
            blocked_accesses=stats.by_result.get("denied", 0),
            suspicious_activities=stats.by_result.get("suspicious", 0),
            high_risk_sessions=stats.high_risk_accesses,
            mfa_adoption_rate=0.0,
            alerts_triggered=0,
            pending_investigations=stats.pending_reviews,
        )
