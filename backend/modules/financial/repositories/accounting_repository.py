"""Repositories para o modulo de Contabilidade."""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from modules.financial.models.accounting_account import (
    AccountClassification,
    AccountingAccount,
    AccountNature,
    AccountStatus,
    AccountType,
)
from modules.financial.models.accounting_period import (
    AccountingPeriod,
    ClosingType,
    PeriodStatus,
    PeriodType,
)
from modules.financial.models.chart_of_accounts import ChartOfAccounts, ChartStatus, ChartType
from modules.financial.models.cost_center import CostCenter, CostCenterStatus, CostCenterType
from modules.financial.models.journal_entry import (
    EntryOrigin,
    EntryStatus,
    EntryType,
    JournalEntry,
    JournalEntryLine,
)
from modules.financial.models.trial_balance import (
    BalanceStatus,
    BalanceType,
    TrialBalance,
    TrialBalanceItem,
)

# =============================================================================
# ChartOfAccounts Repository
# =============================================================================


class ChartOfAccountsRepository:
    """Repository para operacoes de Plano de Contas."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, chart: ChartOfAccounts) -> ChartOfAccounts:
        """Cria um novo plano de contas."""
        self.db.add(chart)
        self.db.flush()
        return chart

    def get_by_id(self, chart_id: uuid.UUID) -> Optional[ChartOfAccounts]:
        """Busca plano de contas por ID."""
        return self.db.query(ChartOfAccounts).filter(ChartOfAccounts.id == chart_id).first()

    def get_by_code(self, code: str, condominio_id: uuid.UUID) -> Optional[ChartOfAccounts]:
        """Busca plano de contas por codigo."""
        return (
            self.db.query(ChartOfAccounts)
            .filter(
                and_(
                    ChartOfAccounts.code == code,
                    ChartOfAccounts.condominio_id == condominio_id,
                    ChartOfAccounts.active.is_(True),  # noqa: E712
                )
            )
            .first()
        )

    def get_active(self, condominio_id: uuid.UUID) -> Optional[ChartOfAccounts]:
        """Busca plano de contas ativo do condominio."""
        return (
            self.db.query(ChartOfAccounts)
            .filter(
                and_(
                    ChartOfAccounts.condominio_id == condominio_id,
                    ChartOfAccounts.status == ChartStatus.ACTIVE,
                    ChartOfAccounts.active.is_(True),  # noqa: E712
                )
            )
            .first()
        )

    def list_all(
        self,
        condominio_id: uuid.UUID,
        chart_type: Optional[ChartType] = None,
        status: Optional[ChartStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ChartOfAccounts]:
        """Lista planos de contas com filtros."""
        query = self.db.query(ChartOfAccounts).filter(
            and_(
                ChartOfAccounts.condominio_id == condominio_id,
                ChartOfAccounts.active.is_(True),  # noqa: E712
            )
        )

        if chart_type:
            query = query.filter(ChartOfAccounts.chart_type == chart_type)
        if status:
            query = query.filter(ChartOfAccounts.status == status)

        return query.order_by(ChartOfAccounts.code).offset(skip).limit(limit).all()

    def count(
        self,
        condominio_id: uuid.UUID,
        status: Optional[ChartStatus] = None,
    ) -> int:
        """Conta planos de contas."""
        query = self.db.query(func.count(ChartOfAccounts.id)).filter(
            and_(
                ChartOfAccounts.condominio_id == condominio_id,
                ChartOfAccounts.active.is_(True),  # noqa: E712
            )
        )

        if status:
            query = query.filter(ChartOfAccounts.status == status)

        return query.scalar() or 0

    def update(self, chart: ChartOfAccounts) -> ChartOfAccounts:
        """Atualiza plano de contas."""
        chart.updated_at = datetime.utcnow()
        self.db.flush()
        return chart

    def delete(self, chart: ChartOfAccounts) -> None:
        """Soft delete de plano de contas."""
        chart.active = False
        chart.updated_at = datetime.utcnow()
        self.db.flush()

    def get_stats(self, condominio_id: uuid.UUID) -> dict:
        """Retorna estatisticas dos planos de contas."""
        total = self.count(condominio_id)
        active = self.count(condominio_id, ChartStatus.ACTIVE)

        # Contagem de contas no plano ativo
        active_chart = self.get_active(condominio_id)
        total_accounts = 0
        if active_chart:
            total_accounts = active_chart.total_accounts or 0

        return {
            "total_charts": total,
            "active_charts": active,
            "total_accounts": total_accounts,
        }

    def generate_next_code(self, condominio_id: uuid.UUID) -> str:
        """Gera proximo codigo de plano de contas."""
        year = datetime.utcnow().year
        prefix = f"PC-{year}-"

        last = (
            self.db.query(ChartOfAccounts)
            .filter(
                and_(
                    ChartOfAccounts.condominio_id == condominio_id,
                    ChartOfAccounts.code.like(f"{prefix}%"),
                )
            )
            .order_by(ChartOfAccounts.code.desc())
            .first()
        )

        if last and last.code:
            try:
                num = int(last.code.split("-")[-1]) + 1
            except (IndexError, ValueError):
                num = 1
        else:
            num = 1

        return f"{prefix}{num:03d}"


# =============================================================================
# AccountingAccount Repository
# =============================================================================


class AccountingAccountRepository:
    """Repository para operacoes de Contas Contabeis."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, account: AccountingAccount) -> AccountingAccount:
        """Cria uma nova conta contabil."""
        self.db.add(account)
        self.db.flush()
        return account

    def get_by_id(self, account_id: uuid.UUID) -> Optional[AccountingAccount]:
        """Busca conta por ID."""
        return self.db.query(AccountingAccount).filter(AccountingAccount.id == account_id).first()

    def get_by_code(self, code: str, chart_id: uuid.UUID) -> Optional[AccountingAccount]:
        """Busca conta por codigo no plano."""
        return (
            self.db.query(AccountingAccount)
            .filter(
                and_(
                    AccountingAccount.code == code,
                    AccountingAccount.chart_id == chart_id,
                    AccountingAccount.active.is_(True),  # noqa: E712
                )
            )
            .first()
        )

    def list_all(
        self,
        chart_id: uuid.UUID,
        account_type: Optional[AccountType] = None,
        nature: Optional[AccountNature] = None,
        classification: Optional[AccountClassification] = None,
        status: Optional[AccountStatus] = None,
        parent_id: Optional[uuid.UUID] = None,
        level: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AccountingAccount]:
        """Lista contas contabeis com filtros."""
        query = self.db.query(AccountingAccount).filter(
            and_(
                AccountingAccount.chart_id == chart_id,
                AccountingAccount.active.is_(True),  # noqa: E712
            )
        )

        if account_type:
            query = query.filter(AccountingAccount.account_type == account_type)
        if nature:
            query = query.filter(AccountingAccount.nature == nature)
        if classification:
            query = query.filter(AccountingAccount.classification == classification)
        if status:
            query = query.filter(AccountingAccount.status == status)
        if parent_id:
            query = query.filter(AccountingAccount.parent_id == parent_id)
        if level:
            query = query.filter(AccountingAccount.level == level)

        return query.order_by(AccountingAccount.code).offset(skip).limit(limit).all()

    def list_analytical(self, chart_id: uuid.UUID) -> list[AccountingAccount]:
        """Lista apenas contas analiticas."""
        return (
            self.db.query(AccountingAccount)
            .filter(
                and_(
                    AccountingAccount.chart_id == chart_id,
                    AccountingAccount.classification == AccountClassification.ANALYTICAL,
                    AccountingAccount.status == AccountStatus.ACTIVE,
                    AccountingAccount.active.is_(True),  # noqa: E712
                )
            )
            .order_by(AccountingAccount.code)
            .all()
        )

    def list_synthetic(self, chart_id: uuid.UUID) -> list[AccountingAccount]:
        """Lista apenas contas sinteticas."""
        return (
            self.db.query(AccountingAccount)
            .filter(
                and_(
                    AccountingAccount.chart_id == chart_id,
                    AccountingAccount.classification == AccountClassification.SYNTHETIC,
                    AccountingAccount.status == AccountStatus.ACTIVE,
                    AccountingAccount.active.is_(True),  # noqa: E712
                )
            )
            .order_by(AccountingAccount.code)
            .all()
        )

    def list_by_type(
        self, chart_id: uuid.UUID, account_type: AccountType
    ) -> list[AccountingAccount]:
        """Lista contas por tipo."""
        return (
            self.db.query(AccountingAccount)
            .filter(
                and_(
                    AccountingAccount.chart_id == chart_id,
                    AccountingAccount.account_type == account_type,
                    AccountingAccount.active.is_(True),  # noqa: E712
                )
            )
            .order_by(AccountingAccount.code)
            .all()
        )

    def list_children(self, parent_id: uuid.UUID) -> list[AccountingAccount]:
        """Lista contas filhas."""
        return (
            self.db.query(AccountingAccount)
            .filter(
                and_(
                    AccountingAccount.parent_id == parent_id,
                    AccountingAccount.active.is_(True),  # noqa: E712
                )
            )
            .order_by(AccountingAccount.code)
            .all()
        )

    def list_root_accounts(self, chart_id: uuid.UUID) -> list[AccountingAccount]:
        """Lista contas raiz (nivel 1)."""
        return (
            self.db.query(AccountingAccount)
            .filter(
                and_(
                    AccountingAccount.chart_id == chart_id,
                    AccountingAccount.level == 1,
                    AccountingAccount.active.is_(True),  # noqa: E712
                )
            )
            .order_by(AccountingAccount.code)
            .all()
        )

    def count(
        self,
        chart_id: uuid.UUID,
        account_type: Optional[AccountType] = None,
        classification: Optional[AccountClassification] = None,
    ) -> int:
        """Conta contas contabeis."""
        query = self.db.query(func.count(AccountingAccount.id)).filter(
            and_(
                AccountingAccount.chart_id == chart_id,
                AccountingAccount.active.is_(True),  # noqa: E712
            )
        )

        if account_type:
            query = query.filter(AccountingAccount.account_type == account_type)
        if classification:
            query = query.filter(AccountingAccount.classification == classification)

        return query.scalar() or 0

    def update(self, account: AccountingAccount) -> AccountingAccount:
        """Atualiza conta contabil."""
        account.updated_at = datetime.utcnow()
        self.db.flush()
        return account

    def delete(self, account: AccountingAccount) -> None:
        """Soft delete de conta."""
        account.active = False
        account.updated_at = datetime.utcnow()
        self.db.flush()

    def get_stats(self, chart_id: uuid.UUID) -> dict:
        """Retorna estatisticas das contas."""
        total = self.count(chart_id)
        analytical = self.count(chart_id, classification=AccountClassification.ANALYTICAL)
        synthetic = self.count(chart_id, classification=AccountClassification.SYNTHETIC)

        # Contagem por tipo
        assets = self.count(chart_id, AccountType.ASSET)
        liabilities = self.count(chart_id, AccountType.LIABILITY)
        equity = self.count(chart_id, AccountType.EQUITY)
        revenue = self.count(chart_id, AccountType.REVENUE)
        expense = self.count(chart_id, AccountType.EXPENSE)
        costs = self.count(chart_id, AccountType.COST)

        return {
            "total_accounts": total,
            "analytical_accounts": analytical,
            "synthetic_accounts": synthetic,
            "assets": assets,
            "liabilities": liabilities,
            "equity": equity,
            "revenue": revenue,
            "expenses": expense,
            "costs": costs,
        }

    def get_account_tree(self, chart_id: uuid.UUID) -> list[AccountingAccount]:
        """Retorna arvore hierarquica de contas."""
        return (
            self.db.query(AccountingAccount)
            .filter(
                and_(
                    AccountingAccount.chart_id == chart_id,
                    AccountingAccount.active.is_(True),  # noqa: E712
                )
            )
            .order_by(AccountingAccount.code)
            .all()
        )

    def generate_next_code(self, chart_id: uuid.UUID, parent_code: Optional[str] = None) -> str:
        """Gera proximo codigo de conta."""
        if parent_code:
            prefix = f"{parent_code}."
            last = (
                self.db.query(AccountingAccount)
                .filter(
                    and_(
                        AccountingAccount.chart_id == chart_id,
                        AccountingAccount.code.like(f"{prefix}%"),
                    )
                )
                .order_by(AccountingAccount.code.desc())
                .first()
            )

            if last and last.code:
                try:
                    suffix = last.code.replace(prefix, "").split(".")[0]
                    num = int(suffix) + 1
                except (IndexError, ValueError):
                    num = 1
            else:
                num = 1

            return f"{prefix}{num:02d}"

        # Conta raiz
        last = (
            self.db.query(AccountingAccount)
            .filter(
                and_(
                    AccountingAccount.chart_id == chart_id,
                    AccountingAccount.level == 1,
                )
            )
            .order_by(AccountingAccount.code.desc())
            .first()
        )

        if last and last.code:
            try:
                num = int(last.code) + 1
            except ValueError:
                num = 1
        else:
            num = 1

        return f"{num}"


# =============================================================================
# CostCenter Repository
# =============================================================================


class CostCenterRepository:
    """Repository para operacoes de Centro de Custo."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, cost_center: CostCenter) -> CostCenter:
        """Cria um novo centro de custo."""
        self.db.add(cost_center)
        self.db.flush()
        return cost_center

    def get_by_id(self, cost_center_id: uuid.UUID) -> Optional[CostCenter]:
        """Busca centro de custo por ID."""
        return self.db.query(CostCenter).filter(CostCenter.id == cost_center_id).first()

    def get_by_code(self, code: str, condominio_id: uuid.UUID) -> Optional[CostCenter]:
        """Busca centro de custo por codigo."""
        return (
            self.db.query(CostCenter)
            .filter(
                and_(
                    CostCenter.code == code,
                    CostCenter.condominio_id == condominio_id,
                    CostCenter.active.is_(True),  # noqa: E712
                )
            )
            .first()
        )

    def list_all(
        self,
        condominio_id: uuid.UUID,
        center_type: Optional[CostCenterType] = None,
        status: Optional[CostCenterStatus] = None,
        parent_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CostCenter]:
        """Lista centros de custo com filtros."""
        query = self.db.query(CostCenter).filter(
            and_(
                CostCenter.condominio_id == condominio_id,
                CostCenter.active.is_(True),  # noqa: E712
            )
        )

        if center_type:
            query = query.filter(CostCenter.center_type == center_type)
        if status:
            query = query.filter(CostCenter.status == status)
        if parent_id:
            query = query.filter(CostCenter.parent_id == parent_id)

        return query.order_by(CostCenter.code).offset(skip).limit(limit).all()

    def list_active(self, condominio_id: uuid.UUID) -> list[CostCenter]:
        """Lista centros de custo ativos."""
        return (
            self.db.query(CostCenter)
            .filter(
                and_(
                    CostCenter.condominio_id == condominio_id,
                    CostCenter.status == CostCenterStatus.ACTIVE,
                    CostCenter.active.is_(True),  # noqa: E712
                )
            )
            .order_by(CostCenter.code)
            .all()
        )

    def list_children(self, parent_id: uuid.UUID) -> list[CostCenter]:
        """Lista centros de custo filhos."""
        return (
            self.db.query(CostCenter)
            .filter(
                and_(
                    CostCenter.parent_id == parent_id,
                    CostCenter.active.is_(True),  # noqa: E712
                )
            )
            .order_by(CostCenter.code)
            .all()
        )

    def count(
        self,
        condominio_id: uuid.UUID,
        status: Optional[CostCenterStatus] = None,
    ) -> int:
        """Conta centros de custo."""
        query = self.db.query(func.count(CostCenter.id)).filter(
            and_(
                CostCenter.condominio_id == condominio_id,
                CostCenter.active.is_(True),  # noqa: E712
            )
        )

        if status:
            query = query.filter(CostCenter.status == status)

        return query.scalar() or 0

    def update(self, cost_center: CostCenter) -> CostCenter:
        """Atualiza centro de custo."""
        cost_center.updated_at = datetime.utcnow()
        self.db.flush()
        return cost_center

    def delete(self, cost_center: CostCenter) -> None:
        """Soft delete de centro de custo."""
        cost_center.active = False
        cost_center.updated_at = datetime.utcnow()
        self.db.flush()

    def get_stats(self, condominio_id: uuid.UUID) -> dict:
        """Retorna estatisticas dos centros de custo."""
        total = self.count(condominio_id)
        active = self.count(condominio_id, CostCenterStatus.ACTIVE)

        # Total orcado e realizado
        budget_total = (
            self.db.query(func.coalesce(func.sum(CostCenter.budget_amount), 0))
            .filter(
                and_(
                    CostCenter.condominio_id == condominio_id,
                    CostCenter.active.is_(True),  # noqa: E712
                )
            )
            .scalar()
        )

        actual_total = (
            self.db.query(func.coalesce(func.sum(CostCenter.actual_amount), 0))
            .filter(
                and_(
                    CostCenter.condominio_id == condominio_id,
                    CostCenter.active.is_(True),  # noqa: E712
                )
            )
            .scalar()
        )

        return {
            "total_cost_centers": total,
            "active_cost_centers": active,
            "total_budget": float(budget_total or 0),
            "total_actual": float(actual_total or 0),
        }

    def generate_next_code(self, condominio_id: uuid.UUID) -> str:
        """Gera proximo codigo de centro de custo."""
        last = (
            self.db.query(CostCenter)
            .filter(
                and_(
                    CostCenter.condominio_id == condominio_id,
                    CostCenter.code.like("CC-%"),
                )
            )
            .order_by(CostCenter.code.desc())
            .first()
        )

        if last and last.code:
            try:
                num = int(last.code.split("-")[1]) + 1
            except (IndexError, ValueError):
                num = 1
        else:
            num = 1

        return f"CC-{num:04d}"


# =============================================================================
# AccountingPeriod Repository
# =============================================================================


class AccountingPeriodRepository:
    """Repository para operacoes de Periodo Contabil."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, period: AccountingPeriod) -> AccountingPeriod:
        """Cria um novo periodo contabil."""
        self.db.add(period)
        self.db.flush()
        return period

    def get_by_id(self, period_id: uuid.UUID) -> Optional[AccountingPeriod]:
        """Busca periodo por ID."""
        return self.db.query(AccountingPeriod).filter(AccountingPeriod.id == period_id).first()

    def get_by_code(self, code: str, condominio_id: uuid.UUID) -> Optional[AccountingPeriod]:
        """Busca periodo por codigo."""
        return (
            self.db.query(AccountingPeriod)
            .filter(
                and_(
                    AccountingPeriod.code == code,
                    AccountingPeriod.condominio_id == condominio_id,
                    AccountingPeriod.active.is_(True),  # noqa: E712
                )
            )
            .first()
        )

    def get_current(self, condominio_id: uuid.UUID) -> Optional[AccountingPeriod]:
        """Busca periodo contabil atual (aberto)."""
        today = date.today()
        return (
            self.db.query(AccountingPeriod)
            .filter(
                and_(
                    AccountingPeriod.condominio_id == condominio_id,
                    AccountingPeriod.status == PeriodStatus.OPEN,
                    AccountingPeriod.start_date <= today,
                    AccountingPeriod.end_date >= today,
                    AccountingPeriod.active.is_(True),  # noqa: E712
                )
            )
            .first()
        )

    def get_by_date(
        self, reference_date: date, condominio_id: uuid.UUID
    ) -> Optional[AccountingPeriod]:
        """Busca periodo por data de referencia."""
        return (
            self.db.query(AccountingPeriod)
            .filter(
                and_(
                    AccountingPeriod.condominio_id == condominio_id,
                    AccountingPeriod.start_date <= reference_date,
                    AccountingPeriod.end_date >= reference_date,
                    AccountingPeriod.active.is_(True),  # noqa: E712
                )
            )
            .first()
        )

    def list_all(
        self,
        condominio_id: uuid.UUID,
        year: Optional[int] = None,
        period_type: Optional[PeriodType] = None,
        status: Optional[PeriodStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AccountingPeriod]:
        """Lista periodos contabeis com filtros."""
        query = self.db.query(AccountingPeriod).filter(
            and_(
                AccountingPeriod.condominio_id == condominio_id,
                AccountingPeriod.active.is_(True),  # noqa: E712
            )
        )

        if year:
            query = query.filter(AccountingPeriod.year == year)
        if period_type:
            query = query.filter(AccountingPeriod.period_type == period_type)
        if status:
            query = query.filter(AccountingPeriod.status == status)

        return query.order_by(AccountingPeriod.start_date.desc()).offset(skip).limit(limit).all()

    def list_open(self, condominio_id: uuid.UUID) -> list[AccountingPeriod]:
        """Lista periodos abertos."""
        return (
            self.db.query(AccountingPeriod)
            .filter(
                and_(
                    AccountingPeriod.condominio_id == condominio_id,
                    AccountingPeriod.status == PeriodStatus.OPEN,
                    AccountingPeriod.active.is_(True),  # noqa: E712
                )
            )
            .order_by(AccountingPeriod.start_date)
            .all()
        )

    def list_by_year(self, condominio_id: uuid.UUID, year: int) -> list[AccountingPeriod]:
        """Lista periodos de um ano."""
        return (
            self.db.query(AccountingPeriod)
            .filter(
                and_(
                    AccountingPeriod.condominio_id == condominio_id,
                    AccountingPeriod.year == year,
                    AccountingPeriod.active.is_(True),  # noqa: E712
                )
            )
            .order_by(AccountingPeriod.start_date)
            .all()
        )

    def count(
        self,
        condominio_id: uuid.UUID,
        status: Optional[PeriodStatus] = None,
    ) -> int:
        """Conta periodos contabeis."""
        query = self.db.query(func.count(AccountingPeriod.id)).filter(
            and_(
                AccountingPeriod.condominio_id == condominio_id,
                AccountingPeriod.active.is_(True),  # noqa: E712
            )
        )

        if status:
            query = query.filter(AccountingPeriod.status == status)

        return query.scalar() or 0

    def update(self, period: AccountingPeriod) -> AccountingPeriod:
        """Atualiza periodo contabil."""
        period.updated_at = datetime.utcnow()
        self.db.flush()
        return period

    def delete(self, period: AccountingPeriod) -> None:
        """Soft delete de periodo."""
        period.active = False
        period.updated_at = datetime.utcnow()
        self.db.flush()

    def close_period(
        self,
        period: AccountingPeriod,
        closed_by: uuid.UUID,
        closing_type: ClosingType = ClosingType.PROVISIONAL,
        notes: Optional[str] = None,
    ) -> AccountingPeriod:
        """Fecha um periodo contabil."""
        period.status = PeriodStatus.CLOSED
        period.closed_by = closed_by
        period.closed_at = datetime.utcnow()
        period.closing_type = closing_type
        period.closing_notes = notes
        period.updated_at = datetime.utcnow()
        self.db.flush()
        return period

    def reopen_period(
        self,
        period: AccountingPeriod,
        reopened_by: uuid.UUID,
        reason: str,
    ) -> AccountingPeriod:
        """Reabre um periodo contabil."""
        period.status = PeriodStatus.REOPENED
        period.reopened_by = reopened_by
        period.reopened_at = datetime.utcnow()
        period.reopen_reason = reason
        period.reopen_count = (period.reopen_count or 0) + 1
        period.updated_at = datetime.utcnow()
        self.db.flush()
        return period

    def get_stats(self, condominio_id: uuid.UUID, year: Optional[int] = None) -> dict:
        """Retorna estatisticas dos periodos."""
        if not year:
            year = datetime.utcnow().year

        total = self.count(condominio_id)
        open_count = self.count(condominio_id, PeriodStatus.OPEN)
        closed = self.count(condominio_id, PeriodStatus.CLOSED)

        # Total de lancamentos
        current = self.get_current(condominio_id)
        total_entries = 0
        if current:
            total_entries = current.total_entries or 0

        return {
            "total_periods": total,
            "open_periods": open_count,
            "closed_periods": closed,
            "current_period_entries": total_entries,
            "year": year,
        }

    def generate_next_code(self, _condominio_id: uuid.UUID, year: int, month: int) -> str:
        """Gera proximo codigo de periodo."""
        return f"PER-{year}-{month:02d}"


# =============================================================================
# JournalEntry Repository
# =============================================================================


class JournalEntryRepository:
    """Repository para operacoes de Lancamento Contabil."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, entry: JournalEntry) -> JournalEntry:
        """Cria um novo lancamento contabil."""
        self.db.add(entry)
        self.db.flush()
        return entry

    def create_with_lines(self, entry: JournalEntry, lines: list[JournalEntryLine]) -> JournalEntry:
        """Cria lancamento com partidas."""
        self.db.add(entry)
        self.db.flush()

        for i, line in enumerate(lines):
            line.journal_entry_id = entry.id
            line.line_number = i + 1
            self.db.add(line)

        entry.line_count = len(lines)
        entry.total_debit = sum(line.debit_amount for line in lines)
        entry.total_credit = sum(line.credit_amount for line in lines)

        self.db.flush()
        return entry

    def get_by_id(self, entry_id: uuid.UUID, include_lines: bool = True) -> Optional[JournalEntry]:
        """Busca lancamento por ID."""
        query = self.db.query(JournalEntry).filter(JournalEntry.id == entry_id)

        if include_lines:
            query = query.options(joinedload(JournalEntry.lines))

        return query.first()

    def get_by_number(self, entry_number: str, condominio_id: uuid.UUID) -> Optional[JournalEntry]:
        """Busca lancamento por numero."""
        return (
            self.db.query(JournalEntry)
            .filter(
                and_(
                    JournalEntry.entry_number == entry_number,
                    JournalEntry.condominio_id == condominio_id,
                    JournalEntry.active.is_(True),  # noqa: E712
                )
            )
            .first()
        )

    def list_all(
        self,
        condominio_id: uuid.UUID,
        period_id: Optional[uuid.UUID] = None,
        entry_type: Optional[EntryType] = None,
        status: Optional[EntryStatus] = None,
        origin: Optional[EntryOrigin] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JournalEntry]:
        """Lista lancamentos com filtros."""
        query = self.db.query(JournalEntry).filter(
            and_(
                JournalEntry.condominio_id == condominio_id,
                JournalEntry.active.is_(True),  # noqa: E712
            )
        )

        if period_id:
            query = query.filter(JournalEntry.period_id == period_id)
        if entry_type:
            query = query.filter(JournalEntry.entry_type == entry_type)
        if status:
            query = query.filter(JournalEntry.status == status)
        if origin:
            query = query.filter(JournalEntry.origin == origin)
        if date_from:
            query = query.filter(JournalEntry.entry_date >= date_from)
        if date_to:
            query = query.filter(JournalEntry.entry_date <= date_to)

        return (
            query.order_by(JournalEntry.entry_date.desc(), JournalEntry.entry_number.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_period(self, period_id: uuid.UUID) -> list[JournalEntry]:
        """Lista lancamentos de um periodo."""
        return (
            self.db.query(JournalEntry)
            .filter(
                and_(
                    JournalEntry.period_id == period_id,
                    JournalEntry.active.is_(True),  # noqa: E712
                )
            )
            .order_by(JournalEntry.entry_date, JournalEntry.entry_number)
            .all()
        )

    def list_pending_approval(self, condominio_id: uuid.UUID) -> list[JournalEntry]:
        """Lista lancamentos pendentes de aprovacao."""
        return (
            self.db.query(JournalEntry)
            .filter(
                and_(
                    JournalEntry.condominio_id == condominio_id,
                    JournalEntry.status == EntryStatus.PENDING,
                    JournalEntry.requires_approval.is_(True),  # noqa: E712
                    JournalEntry.active.is_(True),  # noqa: E712
                )
            )
            .order_by(JournalEntry.entry_date)
            .all()
        )

    def list_by_source(self, source_type: str, source_id: uuid.UUID) -> list[JournalEntry]:
        """Lista lancamentos por origem."""
        return (
            self.db.query(JournalEntry)
            .filter(
                and_(
                    JournalEntry.source_type == source_type,
                    JournalEntry.source_id == source_id,
                    JournalEntry.active.is_(True),  # noqa: E712
                )
            )
            .order_by(JournalEntry.entry_date)
            .all()
        )

    def count(
        self,
        condominio_id: uuid.UUID,
        status: Optional[EntryStatus] = None,
        period_id: Optional[uuid.UUID] = None,
    ) -> int:
        """Conta lancamentos."""
        query = self.db.query(func.count(JournalEntry.id)).filter(
            and_(
                JournalEntry.condominio_id == condominio_id,
                JournalEntry.active.is_(True),  # noqa: E712
            )
        )

        if status:
            query = query.filter(JournalEntry.status == status)
        if period_id:
            query = query.filter(JournalEntry.period_id == period_id)

        return query.scalar() or 0

    def update(self, entry: JournalEntry) -> JournalEntry:
        """Atualiza lancamento."""
        entry.updated_at = datetime.utcnow()
        self.db.flush()
        return entry

    def delete(self, entry: JournalEntry) -> None:
        """Soft delete de lancamento."""
        entry.active = False
        entry.updated_at = datetime.utcnow()
        self.db.flush()

    def post_entry(self, entry: JournalEntry, posted_by: uuid.UUID) -> JournalEntry:
        """Contabiliza o lancamento."""
        entry.status = EntryStatus.POSTED
        entry.posted_by = posted_by
        entry.posting_date = datetime.utcnow()
        entry.updated_at = datetime.utcnow()
        self.db.flush()
        return entry

    def approve_entry(
        self, entry: JournalEntry, approved_by: uuid.UUID, notes: Optional[str] = None
    ) -> JournalEntry:
        """Aprova o lancamento."""
        entry.status = EntryStatus.APPROVED
        entry.approved_by = approved_by
        entry.approved_at = datetime.utcnow()
        entry.approval_notes = notes
        entry.updated_at = datetime.utcnow()
        self.db.flush()
        return entry

    def reject_entry(
        self, entry: JournalEntry, rejected_by: uuid.UUID, reason: str
    ) -> JournalEntry:
        """Rejeita o lancamento."""
        entry.status = EntryStatus.DRAFT
        entry.rejected_by = rejected_by
        entry.rejected_at = datetime.utcnow()
        entry.rejection_reason = reason
        entry.updated_at = datetime.utcnow()
        self.db.flush()
        return entry

    def reverse_entry(
        self,
        entry: JournalEntry,
        reversal_entry: JournalEntry,
        reason: str,
    ) -> tuple[JournalEntry, JournalEntry]:
        """Estorna o lancamento."""
        entry.status = EntryStatus.REVERSED
        entry.reversal_entry_id = reversal_entry.id
        entry.reversal_reason = reason
        entry.reversal_date = datetime.utcnow()
        entry.updated_at = datetime.utcnow()

        reversal_entry.is_reversal = True
        reversal_entry.reversed_entry_id = entry.id

        self.db.flush()
        return entry, reversal_entry

    def get_stats(
        self,
        condominio_id: uuid.UUID,
        period_id: Optional[uuid.UUID] = None,
    ) -> dict:
        """Retorna estatisticas dos lancamentos."""
        total = self.count(condominio_id, period_id=period_id)
        posted = self.count(condominio_id, EntryStatus.POSTED, period_id)
        draft = self.count(condominio_id, EntryStatus.DRAFT, period_id)
        pending = self.count(condominio_id, EntryStatus.PENDING, period_id)

        # Totais
        query = self.db.query(JournalEntry).filter(
            and_(
                JournalEntry.condominio_id == condominio_id,
                JournalEntry.status == EntryStatus.POSTED,
                JournalEntry.active.is_(True),  # noqa: E712
            )
        )
        if period_id:
            query = query.filter(JournalEntry.period_id == period_id)

        total_debit = (
            self.db.query(func.coalesce(func.sum(JournalEntry.total_debit), 0))
            .filter(
                and_(
                    JournalEntry.condominio_id == condominio_id,
                    JournalEntry.status == EntryStatus.POSTED,
                    JournalEntry.active.is_(True),  # noqa: E712
                )
            )
            .scalar()
        )

        total_credit = (
            self.db.query(func.coalesce(func.sum(JournalEntry.total_credit), 0))
            .filter(
                and_(
                    JournalEntry.condominio_id == condominio_id,
                    JournalEntry.status == EntryStatus.POSTED,
                    JournalEntry.active.is_(True),  # noqa: E712
                )
            )
            .scalar()
        )

        return {
            "total_entries": total,
            "posted_entries": posted,
            "draft_entries": draft,
            "pending_entries": pending,
            "total_debit": float(total_debit or 0),
            "total_credit": float(total_credit or 0),
        }

    def generate_next_number(self, condominio_id: uuid.UUID) -> str:
        """Gera proximo numero de lancamento."""
        year = datetime.utcnow().year
        prefix = f"LC-{year}-"

        last = (
            self.db.query(JournalEntry)
            .filter(
                and_(
                    JournalEntry.condominio_id == condominio_id,
                    JournalEntry.entry_number.like(f"{prefix}%"),
                )
            )
            .order_by(JournalEntry.entry_number.desc())
            .first()
        )

        if last and last.entry_number:
            try:
                num = int(last.entry_number.split("-")[-1]) + 1
            except (IndexError, ValueError):
                num = 1
        else:
            num = 1

        return f"{prefix}{num:06d}"


# =============================================================================
# JournalEntryLine Repository
# =============================================================================


class JournalEntryLineRepository:
    """Repository para operacoes de Partidas do Lancamento."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, line: JournalEntryLine) -> JournalEntryLine:
        """Cria uma nova partida."""
        self.db.add(line)
        self.db.flush()
        return line

    def create_batch(self, lines: list[JournalEntryLine]) -> list[JournalEntryLine]:
        """Cria multiplas partidas."""
        self.db.add_all(lines)
        self.db.flush()
        return lines

    def get_by_id(self, line_id: uuid.UUID) -> Optional[JournalEntryLine]:
        """Busca partida por ID."""
        return self.db.query(JournalEntryLine).filter(JournalEntryLine.id == line_id).first()

    def list_by_entry(self, entry_id: uuid.UUID) -> list[JournalEntryLine]:
        """Lista partidas de um lancamento."""
        return (
            self.db.query(JournalEntryLine)
            .filter(JournalEntryLine.journal_entry_id == entry_id)
            .order_by(JournalEntryLine.line_number)
            .all()
        )

    def list_by_account(
        self,
        account_id: uuid.UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JournalEntryLine]:
        """Lista partidas de uma conta."""
        query = (
            self.db.query(JournalEntryLine)
            .join(JournalEntry)
            .filter(
                and_(
                    JournalEntryLine.account_id == account_id,
                    JournalEntry.status == EntryStatus.POSTED,
                    JournalEntry.active.is_(True),  # noqa: E712
                )
            )
        )

        if date_from:
            query = query.filter(JournalEntry.entry_date >= date_from)
        if date_to:
            query = query.filter(JournalEntry.entry_date <= date_to)

        return (
            query.order_by(JournalEntry.entry_date, JournalEntryLine.line_number)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_cost_center(
        self,
        cost_center_id: uuid.UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[JournalEntryLine]:
        """Lista partidas de um centro de custo."""
        query = (
            self.db.query(JournalEntryLine)
            .join(JournalEntry)
            .filter(
                and_(
                    JournalEntryLine.cost_center_id == cost_center_id,
                    JournalEntry.status == EntryStatus.POSTED,
                    JournalEntry.active.is_(True),  # noqa: E712
                )
            )
        )

        if date_from:
            query = query.filter(JournalEntry.entry_date >= date_from)
        if date_to:
            query = query.filter(JournalEntry.entry_date <= date_to)

        return query.order_by(JournalEntry.entry_date).all()

    def update(self, line: JournalEntryLine) -> JournalEntryLine:
        """Atualiza partida."""
        line.updated_at = datetime.utcnow()
        self.db.flush()
        return line

    def delete(self, line: JournalEntryLine) -> None:
        """Deleta partida."""
        self.db.delete(line)
        self.db.flush()

    def get_account_balance(
        self,
        account_id: uuid.UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> dict:
        """Retorna saldo de uma conta."""
        query = (
            self.db.query(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), 0).label("debit"),
                func.coalesce(func.sum(JournalEntryLine.credit_amount), 0).label("credit"),
            )
            .join(JournalEntry)
            .filter(
                and_(
                    JournalEntryLine.account_id == account_id,
                    JournalEntry.status == EntryStatus.POSTED,
                    JournalEntry.active.is_(True),  # noqa: E712
                )
            )
        )

        if date_from:
            query = query.filter(JournalEntry.entry_date >= date_from)
        if date_to:
            query = query.filter(JournalEntry.entry_date <= date_to)

        result = query.first()

        return {
            "total_debit": float(result.debit if result else 0),
            "total_credit": float(result.credit if result else 0),
            "balance": float((result.debit - result.credit) if result else 0),
        }


# =============================================================================
# TrialBalance Repository
# =============================================================================


class TrialBalanceRepository:
    """Repository para operacoes de Balancete."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, balance: TrialBalance) -> TrialBalance:
        """Cria um novo balancete."""
        self.db.add(balance)
        self.db.flush()
        return balance

    def create_with_items(
        self, balance: TrialBalance, items: list[TrialBalanceItem]
    ) -> TrialBalance:
        """Cria balancete com itens."""
        self.db.add(balance)
        self.db.flush()

        for i, item in enumerate(items):
            item.trial_balance_id = balance.id
            item.display_order = i + 1
            self.db.add(item)

        balance.total_accounts = len(items)
        balance.total_analytical = len([item for item in items if item.is_analytical])

        self.db.flush()
        return balance

    def get_by_id(
        self, balance_id: uuid.UUID, include_items: bool = False
    ) -> Optional[TrialBalance]:
        """Busca balancete por ID."""
        query = self.db.query(TrialBalance).filter(TrialBalance.id == balance_id)

        if include_items:
            query = query.options(joinedload(TrialBalance.items))

        return query.first()

    def get_by_code(self, code: str, condominio_id: uuid.UUID) -> Optional[TrialBalance]:
        """Busca balancete por codigo."""
        return (
            self.db.query(TrialBalance)
            .filter(
                and_(
                    TrialBalance.code == code,
                    TrialBalance.condominio_id == condominio_id,
                    TrialBalance.active.is_(True),  # noqa: E712
                )
            )
            .first()
        )

    def list_all(
        self,
        condominio_id: uuid.UUID,
        chart_id: Optional[uuid.UUID] = None,
        balance_type: Optional[BalanceType] = None,
        status: Optional[BalanceStatus] = None,
        year: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TrialBalance]:
        """Lista balancetes com filtros."""
        query = self.db.query(TrialBalance).filter(
            and_(
                TrialBalance.condominio_id == condominio_id,
                TrialBalance.active.is_(True),  # noqa: E712
            )
        )

        if chart_id:
            query = query.filter(TrialBalance.chart_id == chart_id)
        if balance_type:
            query = query.filter(TrialBalance.balance_type == balance_type)
        if status:
            query = query.filter(TrialBalance.status == status)
        if year:
            query = query.filter(TrialBalance.year == year)

        return query.order_by(TrialBalance.reference_date.desc()).offset(skip).limit(limit).all()

    def list_by_year(self, condominio_id: uuid.UUID, year: int) -> list[TrialBalance]:
        """Lista balancetes de um ano."""
        return (
            self.db.query(TrialBalance)
            .filter(
                and_(
                    TrialBalance.condominio_id == condominio_id,
                    TrialBalance.year == year,
                    TrialBalance.active.is_(True),  # noqa: E712
                )
            )
            .order_by(TrialBalance.reference_date)
            .all()
        )

    def get_latest(self, condominio_id: uuid.UUID) -> Optional[TrialBalance]:
        """Busca ultimo balancete."""
        return (
            self.db.query(TrialBalance)
            .filter(
                and_(
                    TrialBalance.condominio_id == condominio_id,
                    TrialBalance.status.in_([BalanceStatus.APPROVED, BalanceStatus.PUBLISHED]),
                    TrialBalance.active.is_(True),  # noqa: E712
                )
            )
            .order_by(TrialBalance.reference_date.desc())
            .first()
        )

    def count(
        self,
        condominio_id: uuid.UUID,
        status: Optional[BalanceStatus] = None,
    ) -> int:
        """Conta balancetes."""
        query = self.db.query(func.count(TrialBalance.id)).filter(
            and_(
                TrialBalance.condominio_id == condominio_id,
                TrialBalance.active.is_(True),  # noqa: E712
            )
        )

        if status:
            query = query.filter(TrialBalance.status == status)

        return query.scalar() or 0

    def update(self, balance: TrialBalance) -> TrialBalance:
        """Atualiza balancete."""
        balance.updated_at = datetime.utcnow()
        self.db.flush()
        return balance

    def delete(self, balance: TrialBalance) -> None:
        """Soft delete de balancete."""
        balance.active = False
        balance.updated_at = datetime.utcnow()
        self.db.flush()

    def approve(
        self, balance: TrialBalance, approved_by: uuid.UUID, notes: Optional[str] = None
    ) -> TrialBalance:
        """Aprova o balancete."""
        balance.status = BalanceStatus.APPROVED
        balance.approved_by = approved_by
        balance.approved_at = datetime.utcnow()
        balance.approval_notes = notes
        balance.updated_at = datetime.utcnow()
        self.db.flush()
        return balance

    def publish(self, balance: TrialBalance, published_by: uuid.UUID) -> TrialBalance:
        """Publica o balancete."""
        balance.status = BalanceStatus.PUBLISHED
        balance.published_by = published_by
        balance.published_at = datetime.utcnow()
        balance.updated_at = datetime.utcnow()
        self.db.flush()
        return balance

    def get_stats(self, condominio_id: uuid.UUID, year: Optional[int] = None) -> dict:
        """Retorna estatisticas dos balancetes."""
        if not year:
            year = datetime.utcnow().year

        total = self.count(condominio_id)
        approved = self.count(condominio_id, BalanceStatus.APPROVED)
        published = self.count(condominio_id, BalanceStatus.PUBLISHED)

        latest = self.get_latest(condominio_id)
        latest_date = latest.reference_date.isoformat() if latest else None
        is_balanced = latest.is_balanced if latest else True

        return {
            "total_balances": total,
            "approved_balances": approved,
            "published_balances": published,
            "latest_balance_date": latest_date,
            "is_balanced": is_balanced,
            "year": year,
        }

    def generate_next_code(self, _condominio_id: uuid.UUID, year: int, month: int) -> str:
        """Gera proximo codigo de balancete."""
        return f"BAL-{year}-{month:02d}"


# =============================================================================
# TrialBalanceItem Repository
# =============================================================================


class TrialBalanceItemRepository:
    """Repository para operacoes de Itens do Balancete."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, item: TrialBalanceItem) -> TrialBalanceItem:
        """Cria um novo item de balancete."""
        self.db.add(item)
        self.db.flush()
        return item

    def create_batch(self, items: list[TrialBalanceItem]) -> list[TrialBalanceItem]:
        """Cria multiplos itens."""
        self.db.add_all(items)
        self.db.flush()
        return items

    def get_by_id(self, item_id: uuid.UUID) -> Optional[TrialBalanceItem]:
        """Busca item por ID."""
        return self.db.query(TrialBalanceItem).filter(TrialBalanceItem.id == item_id).first()

    def list_by_balance(
        self,
        balance_id: uuid.UUID,
        account_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TrialBalanceItem]:
        """Lista itens de um balancete."""
        query = self.db.query(TrialBalanceItem).filter(
            TrialBalanceItem.trial_balance_id == balance_id
        )

        if account_type:
            query = query.filter(TrialBalanceItem.account_type == account_type)

        return query.order_by(TrialBalanceItem.account_code).offset(skip).limit(limit).all()

    def list_analytical(self, balance_id: uuid.UUID) -> list[TrialBalanceItem]:
        """Lista apenas itens analiticos."""
        return (
            self.db.query(TrialBalanceItem)
            .filter(
                and_(
                    TrialBalanceItem.trial_balance_id == balance_id,
                    TrialBalanceItem.is_analytical.is_(True),  # noqa: E712
                )
            )
            .order_by(TrialBalanceItem.account_code)
            .all()
        )

    def list_with_movement(self, balance_id: uuid.UUID) -> list[TrialBalanceItem]:
        """Lista itens com movimento no periodo."""
        return (
            self.db.query(TrialBalanceItem)
            .filter(
                and_(
                    TrialBalanceItem.trial_balance_id == balance_id,
                    or_(
                        TrialBalanceItem.period_debit > 0,
                        TrialBalanceItem.period_credit > 0,
                    ),
                )
            )
            .order_by(TrialBalanceItem.account_code)
            .all()
        )

    def update(self, item: TrialBalanceItem) -> TrialBalanceItem:
        """Atualiza item de balancete."""
        self.db.flush()
        return item

    def delete(self, item: TrialBalanceItem) -> None:
        """Deleta item de balancete."""
        self.db.delete(item)
        self.db.flush()

    def delete_by_balance(self, balance_id: uuid.UUID) -> int:
        """Deleta todos os itens de um balancete."""
        count = (
            self.db.query(TrialBalanceItem)
            .filter(TrialBalanceItem.trial_balance_id == balance_id)
            .delete()
        )
        self.db.flush()
        return count
