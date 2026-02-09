"""
Data Quality Repository - Sprint 48.

Repositório para operações de banco de dados.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from modules.ai.data_quality.models import (
    CheckStatusEnum,
    DataProfile,
    DataQualityCheck,
    DataQualityIssue,
    DataQualityRule,
    DuplicateRecord,
    DuplicateStatusEnum,
    IssueSeverityEnum,
    IssueStatusEnum,
    ProfileStatusEnum,
    RuleStatusEnum,
)


class DataQualityRepository:
    """Repositório de Data Quality."""

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # Rules
    # ============================================================

    def create_rule(self, rule: DataQualityRule) -> DataQualityRule:
        """Cria regra."""
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def get_rule(self, rule_id: UUID) -> DataQualityRule | None:
        """Busca regra por ID."""
        return self.db.query(DataQualityRule).filter(DataQualityRule.id == rule_id, DataQualityRule.is_active).first()

    def get_rule_by_code(self, code: str) -> DataQualityRule | None:
        """Busca regra por código."""
        return self.db.query(DataQualityRule).filter(DataQualityRule.code == code, DataQualityRule.is_active).first()

    def list_rules(
        self,
        entity_type: str = None,
        category: str = None,
        status: RuleStatusEnum = None,
        skip: int = 0,
        limit: int = 100,
        organization_id: UUID = None,
    ) -> tuple[list[DataQualityRule], int]:
        """Lista regras com filtros."""
        query = self.db.query(DataQualityRule).filter(DataQualityRule.is_active)

        if entity_type:
            query = query.filter(or_(DataQualityRule.entity_type == entity_type, DataQualityRule.applies_to_all))
        if category:
            query = query.filter(DataQualityRule.category == category)
        if status:
            query = query.filter(DataQualityRule.status == status)
        if organization_id:
            query = query.filter(or_(DataQualityRule.organization_id == organization_id, DataQualityRule.is_system))

        total = query.count()
        rules = (
            query.order_by(DataQualityRule.priority.desc(), DataQualityRule.execution_order)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return rules, total

    def get_active_rules_for_entity(self, entity_type: str) -> list[DataQualityRule]:
        """Busca regras ativas para entidade."""
        return (
            self.db.query(DataQualityRule)
            .filter(
                DataQualityRule.is_active,
                DataQualityRule.status == RuleStatusEnum.ACTIVE,
                or_(DataQualityRule.entity_type == entity_type, DataQualityRule.applies_to_all),
            )
            .order_by(DataQualityRule.execution_order)
            .all()
        )

    def update_rule(self, rule: DataQualityRule) -> DataQualityRule:
        """Atualiza regra."""
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete_rule(self, rule: DataQualityRule) -> None:
        """Soft delete de regra."""
        rule.is_active = False
        self.db.commit()

    # ============================================================
    # Checks
    # ============================================================

    def create_check(self, check: DataQualityCheck) -> DataQualityCheck:
        """Cria verificação."""
        # Gera número sequencial
        last_check = (
            self.db.query(DataQualityCheck)
            .filter(DataQualityCheck.entity_type == check.entity_type)
            .order_by(desc(DataQualityCheck.check_number))
            .first()
        )

        check.check_number = (last_check.check_number + 1) if last_check else 1

        self.db.add(check)
        self.db.commit()
        self.db.refresh(check)
        return check

    def get_check(self, check_id: UUID) -> DataQualityCheck | None:
        """Busca verificação por ID."""
        return self.db.query(DataQualityCheck).filter(DataQualityCheck.id == check_id).first()

    def list_checks(
        self,
        entity_type: str = None,
        status: CheckStatusEnum = None,
        skip: int = 0,
        limit: int = 100,
        organization_id: UUID = None,
    ) -> tuple[list[DataQualityCheck], int]:
        """Lista verificações."""
        query = self.db.query(DataQualityCheck)

        if entity_type:
            query = query.filter(DataQualityCheck.entity_type == entity_type)
        if status:
            query = query.filter(DataQualityCheck.status == status)
        if organization_id:
            query = query.filter(DataQualityCheck.organization_id == organization_id)

        total = query.count()
        checks = query.order_by(desc(DataQualityCheck.created_at)).offset(skip).limit(limit).all()

        return checks, total

    def get_latest_check(self, entity_type: str) -> DataQualityCheck | None:
        """Busca última verificação para entidade."""
        return (
            self.db.query(DataQualityCheck)
            .filter(DataQualityCheck.entity_type == entity_type, DataQualityCheck.status == CheckStatusEnum.COMPLETED)
            .order_by(desc(DataQualityCheck.completed_at))
            .first()
        )

    def update_check(self, check: DataQualityCheck) -> DataQualityCheck:
        """Atualiza verificação."""
        self.db.commit()
        self.db.refresh(check)
        return check

    # ============================================================
    # Issues
    # ============================================================

    def create_issue(self, issue: DataQualityIssue) -> DataQualityIssue:
        """Cria issue."""
        self.db.add(issue)
        self.db.commit()
        self.db.refresh(issue)
        return issue

    def get_issue(self, issue_id: UUID) -> DataQualityIssue | None:
        """Busca issue por ID."""
        return (
            self.db.query(DataQualityIssue).filter(DataQualityIssue.id == issue_id, DataQualityIssue.is_active).first()
        )

    def list_issues(
        self,
        entity_type: str = None,
        entity_id: UUID = None,
        status: IssueStatusEnum = None,
        severity: IssueSeverityEnum = None,
        issue_type: str = None,
        check_id: UUID = None,
        skip: int = 0,
        limit: int = 100,
        organization_id: UUID = None,
    ) -> tuple[list[DataQualityIssue], int]:
        """Lista issues."""
        query = self.db.query(DataQualityIssue).filter(DataQualityIssue.is_active)

        if entity_type:
            query = query.filter(DataQualityIssue.entity_type == entity_type)
        if entity_id:
            query = query.filter(DataQualityIssue.entity_id == entity_id)
        if status:
            query = query.filter(DataQualityIssue.status == status)
        if severity:
            query = query.filter(DataQualityIssue.severity == severity)
        if issue_type:
            query = query.filter(DataQualityIssue.issue_type == issue_type)
        if check_id:
            query = query.filter(DataQualityIssue.check_id == check_id)
        if organization_id:
            query = query.filter(DataQualityIssue.organization_id == organization_id)

        total = query.count()
        issues = (
            query.order_by(DataQualityIssue.severity.desc(), desc(DataQualityIssue.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return issues, total

    def get_open_issues_count(self, entity_type: str = None) -> int:
        """Conta issues abertos."""
        query = self.db.query(DataQualityIssue).filter(
            DataQualityIssue.is_active,
            DataQualityIssue.status.in_(
                [IssueStatusEnum.OPEN, IssueStatusEnum.ACKNOWLEDGED, IssueStatusEnum.IN_PROGRESS]
            ),
        )
        if entity_type:
            query = query.filter(DataQualityIssue.entity_type == entity_type)
        return query.count()

    def get_issues_by_severity(self) -> dict[str, int]:
        """Conta issues por severidade."""
        result = (
            self.db.query(DataQualityIssue.severity, func.count(DataQualityIssue.id))
            .filter(
                DataQualityIssue.is_active,
                DataQualityIssue.status.in_(
                    [IssueStatusEnum.OPEN, IssueStatusEnum.ACKNOWLEDGED, IssueStatusEnum.IN_PROGRESS]
                ),
            )
            .group_by(DataQualityIssue.severity)
            .all()
        )

        return {r[0].value: r[1] for r in result}

    def update_issue(self, issue: DataQualityIssue) -> DataQualityIssue:
        """Atualiza issue."""
        self.db.commit()
        self.db.refresh(issue)
        return issue

    def bulk_update_issues(self, issue_ids: list[UUID], updates: dict[str, Any]) -> int:
        """Atualiza issues em lote."""
        count = (
            self.db.query(DataQualityIssue)
            .filter(DataQualityIssue.id.in_(issue_ids))
            .update(updates, synchronize_session=False)
        )
        self.db.commit()
        return count

    # ============================================================
    # Duplicates
    # ============================================================

    def create_duplicate(self, duplicate: DuplicateRecord) -> DuplicateRecord:
        """Cria registro de duplicata."""
        self.db.add(duplicate)
        self.db.commit()
        self.db.refresh(duplicate)
        return duplicate

    def get_duplicate(self, duplicate_id: UUID) -> DuplicateRecord | None:
        """Busca duplicata por ID."""
        return (
            self.db.query(DuplicateRecord).filter(DuplicateRecord.id == duplicate_id, DuplicateRecord.is_active).first()
        )

    def list_duplicates(
        self,
        entity_type: str = None,
        status: DuplicateStatusEnum = None,
        min_score: float = None,
        skip: int = 0,
        limit: int = 100,
        organization_id: UUID = None,
    ) -> tuple[list[DuplicateRecord], int]:
        """Lista duplicatas."""
        query = self.db.query(DuplicateRecord).filter(DuplicateRecord.is_active)

        if entity_type:
            query = query.filter(DuplicateRecord.entity_type == entity_type)
        if status:
            query = query.filter(DuplicateRecord.status == status)
        if min_score:
            query = query.filter(DuplicateRecord.similarity_score >= min_score)
        if organization_id:
            query = query.filter(DuplicateRecord.organization_id == organization_id)

        total = query.count()
        duplicates = (
            query.order_by(desc(DuplicateRecord.similarity_score), desc(DuplicateRecord.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return duplicates, total

    def get_pending_duplicates_count(self) -> int:
        """Conta duplicatas pendentes."""
        return (
            self.db.query(DuplicateRecord)
            .filter(
                DuplicateRecord.is_active,
                DuplicateRecord.status.in_(
                    [DuplicateStatusEnum.DETECTED, DuplicateStatusEnum.REVIEWING, DuplicateStatusEnum.CONFIRMED]
                ),
            )
            .count()
        )

    def update_duplicate(self, duplicate: DuplicateRecord) -> DuplicateRecord:
        """Atualiza duplicata."""
        self.db.commit()
        self.db.refresh(duplicate)
        return duplicate

    # ============================================================
    # Profiles
    # ============================================================

    def create_profile(self, profile: DataProfile) -> DataProfile:
        """Cria perfil."""
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_profile(self, profile_id: UUID) -> DataProfile | None:
        """Busca perfil por ID."""
        return self.db.query(DataProfile).filter(DataProfile.id == profile_id, DataProfile.is_active).first()

    def get_profile_for_field(self, entity_type: str, field_name: str = None) -> DataProfile | None:
        """Busca perfil mais recente para campo."""
        query = self.db.query(DataProfile).filter(
            DataProfile.entity_type == entity_type,
            DataProfile.is_active,
            DataProfile.status == ProfileStatusEnum.COMPLETED,
        )
        if field_name:
            query = query.filter(DataProfile.field_name == field_name)
        else:
            query = query.filter(DataProfile.is_entity_profile)

        return query.order_by(desc(DataProfile.completed_at)).first()

    def list_profiles(
        self,
        entity_type: str = None,
        status: ProfileStatusEnum = None,
        skip: int = 0,
        limit: int = 100,
        organization_id: UUID = None,
    ) -> tuple[list[DataProfile], int]:
        """Lista perfis."""
        query = self.db.query(DataProfile).filter(DataProfile.is_active)

        if entity_type:
            query = query.filter(DataProfile.entity_type == entity_type)
        if status:
            query = query.filter(DataProfile.status == status)
        if organization_id:
            query = query.filter(DataProfile.organization_id == organization_id)

        total = query.count()
        profiles = query.order_by(desc(DataProfile.created_at)).offset(skip).limit(limit).all()

        return profiles, total

    def get_outdated_profiles_count(self, days: int = 7) -> int:
        """Conta perfis desatualizados."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return (
            self.db.query(DataProfile)
            .filter(
                DataProfile.is_active,
                DataProfile.status == ProfileStatusEnum.COMPLETED,
                DataProfile.completed_at < cutoff,
            )
            .count()
        )

    def update_profile(self, profile: DataProfile) -> DataProfile:
        """Atualiza perfil."""
        self.db.commit()
        self.db.refresh(profile)
        return profile

    # ============================================================
    # Analytics
    # ============================================================

    def get_quality_stats(self, organization_id: UUID = None) -> dict[str, Any]:
        """Obtém estatísticas de qualidade."""
        base_filter = []
        if organization_id:
            base_filter.append(DataQualityIssue.organization_id == organization_id)

        # Issues por severidade
        issues_by_severity = self.get_issues_by_severity()

        # Issues por tipo
        issues_by_type = (
            self.db.query(DataQualityIssue.issue_type, func.count(DataQualityIssue.id))
            .filter(DataQualityIssue.is_active, *base_filter)
            .group_by(DataQualityIssue.issue_type)
            .all()
        )

        # Última verificação por entidade
        recent_checks = (
            self.db.query(DataQualityCheck)
            .filter(DataQualityCheck.status == CheckStatusEnum.COMPLETED)
            .order_by(desc(DataQualityCheck.completed_at))
            .limit(5)
            .all()
        )

        return {
            "total_open_issues": self.get_open_issues_count(),
            "issues_by_severity": issues_by_severity,
            "issues_by_type": {r[0].value: r[1] for r in issues_by_type},
            "pending_duplicates": self.get_pending_duplicates_count(),
            "outdated_profiles": self.get_outdated_profiles_count(),
            "recent_checks": [c.to_summary_dict() for c in recent_checks],
        }
