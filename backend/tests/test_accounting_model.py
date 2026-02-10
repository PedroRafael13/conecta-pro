"""Tests for Accounting (Contabilidade) models - Sprint 27."""

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.financial.models import (  # ChartOfAccounts; AccountingAccount; CostCenter; AccountingPeriod; JournalEntry; TrialBalance
    AccountClassification,
    AccountingAccount,
    AccountingPeriod,
    AccountNature,
    AccountStatus,
    AccountType,
    AllocationMethod,
    BalancePeriod,
    BalanceStatus,
    BalanceType,
    ChartOfAccounts,
    ChartStandard,
    ChartStatus,
    ChartType,
    ClosingType,
    CostCenter,
    CostCenterStatus,
    CostCenterType,
    EntryOrigin,
    EntryStatus,
    EntryType,
    JournalEntry,
    JournalEntryLine,
    PeriodStatus,
    PeriodType,
    SpedAccountNature,
    TrialBalance,
    TrialBalanceItem,
)


class TestChartOfAccountsModel:
    """Tests for ChartOfAccounts model."""

    def test_chart_creation_basic(self) -> None:
        """Test basic chart of accounts creation."""
        condo_id = uuid4()
        chart = ChartOfAccounts(
            condominio_id=condo_id,
            code="PC-001",
            name="Plano de Contas Principal",
        )
        assert chart.code == "PC-001"
        assert chart.name == "Plano de Contas Principal"
        assert chart.condominio_id == condo_id
        assert chart.chart_type == ChartType.ANALYTICAL
        assert chart.status == ChartStatus.ACTIVE
        assert chart.standard == ChartStandard.CUSTOM
        assert chart.active is True

    def test_chart_type_enum(self) -> None:
        """Test ChartType enum values."""
        assert ChartType.ANALYTICAL.value == "ANALYTICAL"
        assert ChartType.SYNTHETIC.value == "SYNTHETIC"
        assert ChartType.REFERENTIAL.value == "REFERENTIAL"

    def test_chart_status_enum(self) -> None:
        """Test ChartStatus enum values."""
        assert ChartStatus.ACTIVE.value == "ACTIVE"
        assert ChartStatus.INACTIVE.value == "INACTIVE"
        assert ChartStatus.DRAFT.value == "DRAFT"
        assert ChartStatus.BLOCKED.value == "BLOCKED"

    def test_chart_standard_enum(self) -> None:
        """Test ChartStandard enum values."""
        assert ChartStandard.CUSTOM.value == "CUSTOM"
        assert ChartStandard.SPED_ECD.value == "SPED_ECD"
        assert ChartStandard.SPED_ECF.value == "SPED_ECF"
        assert ChartStandard.COSIF.value == "COSIF"
        assert ChartStandard.IFRS.value == "IFRS"
        assert ChartStandard.US_GAAP.value == "US_GAAP"

    def test_chart_with_sped_standard(self) -> None:
        """Test chart with SPED standard."""
        chart = ChartOfAccounts(
            condominio_id=uuid4(),
            code="PC-SPED",
            name="Plano de Contas SPED",
            standard=ChartStandard.SPED_ECD,
            sped_layout_version="9.0",
            sped_compliant=True,
        )
        assert chart.standard == ChartStandard.SPED_ECD
        assert chart.sped_layout_version == "9.0"
        assert chart.sped_compliant is True

    def test_chart_with_fiscal_year(self) -> None:
        """Test chart with fiscal year settings."""
        chart = ChartOfAccounts(
            condominio_id=uuid4(),
            code="PC-FY",
            name="Plano de Contas 2024",
            fiscal_year=2024,
            valid_from=date(2024, 1, 1),
            valid_to=date(2024, 12, 31),
        )
        assert chart.fiscal_year == 2024
        assert chart.valid_from == date(2024, 1, 1)
        assert chart.valid_to == date(2024, 12, 31)


class TestAccountingAccountModel:
    """Tests for AccountingAccount model."""

    def test_account_creation_basic(self) -> None:
        """Test basic accounting account creation."""
        condo_id = uuid4()
        chart_id = uuid4()
        account = AccountingAccount(
            condominio_id=condo_id,
            chart_id=chart_id,
            code="1",
            name="Ativo",
        )
        assert account.code == "1"
        assert account.name == "Ativo"
        assert account.account_type == AccountType.SYNTHETIC
        assert account.nature == AccountNature.DEBIT
        assert account.classification == AccountClassification.PATRIMONIAL
        assert account.status == AccountStatus.ACTIVE
        assert account.level == 1
        assert account.allow_entries is False

    def test_account_type_enum(self) -> None:
        """Test AccountType enum values."""
        assert AccountType.SYNTHETIC.value == "SYNTHETIC"
        assert AccountType.ANALYTICAL.value == "ANALYTICAL"

    def test_account_nature_enum(self) -> None:
        """Test AccountNature enum values."""
        assert AccountNature.DEBIT.value == "DEBIT"
        assert AccountNature.CREDIT.value == "CREDIT"
        assert AccountNature.MIXED.value == "MIXED"

    def test_account_classification_enum(self) -> None:
        """Test AccountClassification enum values."""
        assert AccountClassification.PATRIMONIAL.value == "PATRIMONIAL"
        assert AccountClassification.RESULT.value == "RESULT"
        assert AccountClassification.COMPENSATION.value == "COMPENSATION"
        assert AccountClassification.ANALYTICAL.value == "ANALYTICAL"

    def test_account_status_enum(self) -> None:
        """Test AccountStatus enum values."""
        assert AccountStatus.ACTIVE.value == "ACTIVE"
        assert AccountStatus.INACTIVE.value == "INACTIVE"
        assert AccountStatus.BLOCKED.value == "BLOCKED"
        assert AccountStatus.PENDING.value == "PENDING"

    def test_sped_account_nature_enum(self) -> None:
        """Test SpedAccountNature enum values."""
        assert SpedAccountNature.DEBIT.value == "D"
        assert SpedAccountNature.CREDIT.value == "C"

    def test_account_analytical(self) -> None:
        """Test analytical account creation."""
        parent_id = uuid4()
        account = AccountingAccount(
            condominio_id=uuid4(),
            chart_id=uuid4(),
            code="1.1.1.01",
            name="Caixa Geral",
            account_type=AccountType.ANALYTICAL,
            parent_id=parent_id,
            level=4,
            allow_entries=True,
        )
        assert account.account_type == AccountType.ANALYTICAL
        assert account.parent_id == parent_id
        assert account.level == 4
        assert account.allow_entries is True

    def test_account_with_sped_info(self) -> None:
        """Test account with SPED information."""
        account = AccountingAccount(
            condominio_id=uuid4(),
            chart_id=uuid4(),
            code="1.1.1.01",
            name="Caixa",
            sped_account_code="1.1.1.01.0001",
            sped_account_nature=SpedAccountNature.DEBIT,
            sped_reference_date=date(2024, 1, 1),
        )
        assert account.sped_account_code == "1.1.1.01.0001"
        assert account.sped_account_nature == SpedAccountNature.DEBIT
        assert account.sped_reference_date == date(2024, 1, 1)

    def test_account_with_balances(self) -> None:
        """Test account with balance tracking."""
        account = AccountingAccount(
            condominio_id=uuid4(),
            chart_id=uuid4(),
            code="1.1.1.01",
            name="Caixa",
            account_type=AccountType.ANALYTICAL,
            allow_entries=True,
            initial_balance=Decimal("10000.00"),
            current_balance=Decimal("15500.00"),
            debit_balance=Decimal("20000.00"),
            credit_balance=Decimal("14500.00"),
        )
        assert account.initial_balance == Decimal("10000.00")
        assert account.current_balance == Decimal("15500.00")
        assert account.debit_balance == Decimal("20000.00")
        assert account.credit_balance == Decimal("14500.00")

    def test_account_with_cost_center(self) -> None:
        """Test account with cost center requirement."""
        cost_center_id = uuid4()
        account = AccountingAccount(
            condominio_id=uuid4(),
            chart_id=uuid4(),
            code="4.1.1.01",
            name="Despesas com Pessoal",
            classification=AccountClassification.RESULT,
            requires_cost_center=True,
            default_cost_center_id=cost_center_id,
        )
        assert account.requires_cost_center is True
        assert account.default_cost_center_id == cost_center_id


class TestCostCenterModel:
    """Tests for CostCenter model."""

    def test_cost_center_creation_basic(self) -> None:
        """Test basic cost center creation."""
        condo_id = uuid4()
        cost_center = CostCenter(
            condominio_id=condo_id,
            code="CC-001",
            name="Administracao",
        )
        assert cost_center.code == "CC-001"
        assert cost_center.name == "Administracao"
        assert cost_center.condominio_id == condo_id
        assert cost_center.cost_center_type == CostCenterType.ADMINISTRATIVE
        assert cost_center.status == CostCenterStatus.ACTIVE
        assert cost_center.allocation_method == AllocationMethod.DIRECT
        assert cost_center.level == 1
        assert cost_center.active is True

    def test_cost_center_type_enum(self) -> None:
        """Test CostCenterType enum values."""
        assert CostCenterType.ADMINISTRATIVE.value == "ADMINISTRATIVE"
        assert CostCenterType.OPERATIONAL.value == "OPERATIONAL"
        assert CostCenterType.COMMERCIAL.value == "COMMERCIAL"
        assert CostCenterType.PRODUCTION.value == "PRODUCTION"
        assert CostCenterType.PROJECT.value == "PROJECT"
        assert CostCenterType.SUPPORT.value == "SUPPORT"
        assert CostCenterType.SHARED.value == "SHARED"

    def test_cost_center_status_enum(self) -> None:
        """Test CostCenterStatus enum values."""
        assert CostCenterStatus.ACTIVE.value == "ACTIVE"
        assert CostCenterStatus.INACTIVE.value == "INACTIVE"
        assert CostCenterStatus.BLOCKED.value == "BLOCKED"
        assert CostCenterStatus.PENDING.value == "PENDING"

    def test_allocation_method_enum(self) -> None:
        """Test AllocationMethod enum values."""
        assert AllocationMethod.DIRECT.value == "DIRECT"
        assert AllocationMethod.PROPORTIONAL.value == "PROPORTIONAL"
        assert AllocationMethod.HEADCOUNT.value == "HEADCOUNT"
        assert AllocationMethod.AREA.value == "AREA"
        assert AllocationMethod.REVENUE.value == "REVENUE"
        assert AllocationMethod.PRODUCTION.value == "PRODUCTION"
        assert AllocationMethod.CUSTOM.value == "CUSTOM"

    def test_cost_center_hierarchical(self) -> None:
        """Test cost center with hierarchy."""
        parent_id = uuid4()
        cost_center = CostCenter(
            condominio_id=uuid4(),
            code="CC-001-01",
            name="Contabilidade",
            parent_id=parent_id,
            level=2,
            path="CC-001/CC-001-01",
        )
        assert cost_center.parent_id == parent_id
        assert cost_center.level == 2
        assert cost_center.path == "CC-001/CC-001-01"

    def test_cost_center_with_budget(self) -> None:
        """Test cost center with budget."""
        cost_center = CostCenter(
            condominio_id=uuid4(),
            code="CC-002",
            name="Marketing",
            cost_center_type=CostCenterType.COMMERCIAL,
            budget_amount=Decimal("50000.00"),
            actual_amount=Decimal("35000.00"),
            variance_amount=Decimal("15000.00"),
            variance_percent=Decimal("30.00"),
        )
        assert cost_center.budget_amount == Decimal("50000.00")
        assert cost_center.actual_amount == Decimal("35000.00")
        assert cost_center.variance_amount == Decimal("15000.00")
        assert cost_center.variance_percent == Decimal("30.00")

    def test_cost_center_with_allocation(self) -> None:
        """Test cost center with allocation settings."""
        cost_center = CostCenter(
            condominio_id=uuid4(),
            code="CC-003",
            name="TI",
            cost_center_type=CostCenterType.SUPPORT,
            allocation_method=AllocationMethod.HEADCOUNT,
            allocation_percent=Decimal("100.00"),
            accepts_allocation=True,
            distributes_costs=True,
        )
        assert cost_center.allocation_method == AllocationMethod.HEADCOUNT
        assert cost_center.allocation_percent == Decimal("100.00")
        assert cost_center.accepts_allocation is True
        assert cost_center.distributes_costs is True


class TestAccountingPeriodModel:
    """Tests for AccountingPeriod model."""

    def test_period_creation_basic(self) -> None:
        """Test basic accounting period creation."""
        condo_id = uuid4()
        period = AccountingPeriod(
            condominio_id=condo_id,
            code="2024-01",
            name="Janeiro 2024",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert period.code == "2024-01"
        assert period.name == "Janeiro 2024"
        assert period.start_date == date(2024, 1, 1)
        assert period.end_date == date(2024, 1, 31)
        assert period.period_type == PeriodType.MONTHLY
        assert period.status == PeriodStatus.OPEN
        assert period.active is True

    def test_period_type_enum(self) -> None:
        """Test PeriodType enum values."""
        assert PeriodType.MONTHLY.value == "MONTHLY"
        assert PeriodType.QUARTERLY.value == "QUARTERLY"
        assert PeriodType.SEMIANNUAL.value == "SEMIANNUAL"
        assert PeriodType.ANNUAL.value == "ANNUAL"
        assert PeriodType.SPECIAL.value == "SPECIAL"

    def test_period_status_enum(self) -> None:
        """Test PeriodStatus enum values."""
        assert PeriodStatus.OPEN.value == "OPEN"
        assert PeriodStatus.FROZEN.value == "FROZEN"
        assert PeriodStatus.CLOSED.value == "CLOSED"
        assert PeriodStatus.LOCKED.value == "LOCKED"
        assert PeriodStatus.REOPENED.value == "REOPENED"

    def test_closing_type_enum(self) -> None:
        """Test ClosingType enum values."""
        assert ClosingType.TEMPORARY.value == "TEMPORARY"
        assert ClosingType.DEFINITIVE.value == "DEFINITIVE"
        assert ClosingType.FISCAL.value == "FISCAL"

    def test_period_quarterly(self) -> None:
        """Test quarterly period creation."""
        period = AccountingPeriod(
            condominio_id=uuid4(),
            code="2024-Q1",
            name="1o Trimestre 2024",
            period_type=PeriodType.QUARTERLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            fiscal_year=2024,
            quarter=1,
        )
        assert period.period_type == PeriodType.QUARTERLY
        assert period.fiscal_year == 2024
        assert period.quarter == 1

    def test_period_closed(self) -> None:
        """Test closed period."""
        closed_by = uuid4()
        period = AccountingPeriod(
            condominio_id=uuid4(),
            code="2023-12",
            name="Dezembro 2023",
            start_date=date(2023, 12, 1),
            end_date=date(2023, 12, 31),
            status=PeriodStatus.CLOSED,
            closing_type=ClosingType.DEFINITIVE,
            closed_at=datetime(2024, 1, 5, 18, 30, 0),
            closed_by_id=closed_by,
        )
        assert period.status == PeriodStatus.CLOSED
        assert period.closing_type == ClosingType.DEFINITIVE
        assert period.closed_by_id == closed_by

    def test_period_with_balances(self) -> None:
        """Test period with balance tracking."""
        period = AccountingPeriod(
            condominio_id=uuid4(),
            code="2024-02",
            name="Fevereiro 2024",
            start_date=date(2024, 2, 1),
            end_date=date(2024, 2, 29),
            opening_balance=Decimal("100000.00"),
            closing_balance=Decimal("125000.00"),
            total_debits=Decimal("50000.00"),
            total_credits=Decimal("50000.00"),
            entries_count=150,
        )
        assert period.opening_balance == Decimal("100000.00")
        assert period.closing_balance == Decimal("125000.00")
        assert period.total_debits == Decimal("50000.00")
        assert period.total_credits == Decimal("50000.00")
        assert period.entries_count == 150


class TestJournalEntryModel:
    """Tests for JournalEntry model."""

    def test_entry_creation_basic(self) -> None:
        """Test basic journal entry creation."""
        condo_id = uuid4()
        period_id = uuid4()
        entry = JournalEntry(
            condominio_id=condo_id,
            entry_number="LC-2024-00001",
            entry_date=date(2024, 1, 15),
            period_id=period_id,
            description="Pagamento de fornecedor",
        )
        assert entry.entry_number == "LC-2024-00001"
        assert entry.entry_date == date(2024, 1, 15)
        assert entry.entry_type == EntryType.STANDARD
        assert entry.status == EntryStatus.DRAFT
        assert entry.origin == EntryOrigin.MANUAL
        assert entry.active is True

    def test_entry_type_enum(self) -> None:
        """Test EntryType enum values."""
        assert EntryType.STANDARD.value == "STANDARD"
        assert EntryType.OPENING.value == "OPENING"
        assert EntryType.CLOSING.value == "CLOSING"
        assert EntryType.ADJUSTMENT.value == "ADJUSTMENT"
        assert EntryType.REVERSAL.value == "REVERSAL"
        assert EntryType.TRANSFER.value == "TRANSFER"

    def test_entry_status_enum(self) -> None:
        """Test EntryStatus enum values."""
        assert EntryStatus.DRAFT.value == "DRAFT"
        assert EntryStatus.PENDING.value == "PENDING"
        assert EntryStatus.APPROVED.value == "APPROVED"
        assert EntryStatus.POSTED.value == "POSTED"
        assert EntryStatus.REVERSED.value == "REVERSED"
        assert EntryStatus.CANCELLED.value == "CANCELLED"

    def test_entry_origin_enum(self) -> None:
        """Test EntryOrigin enum values."""
        assert EntryOrigin.MANUAL.value == "MANUAL"
        assert EntryOrigin.AUTOMATIC.value == "AUTOMATIC"
        assert EntryOrigin.IMPORT.value == "IMPORT"
        assert EntryOrigin.INTEGRATION.value == "INTEGRATION"
        assert EntryOrigin.SYSTEM.value == "SYSTEM"

    def test_entry_with_amounts(self) -> None:
        """Test entry with amounts."""
        entry = JournalEntry(
            condominio_id=uuid4(),
            entry_number="LC-2024-00002",
            entry_date=date(2024, 1, 20),
            period_id=uuid4(),
            description="Recebimento de cliente",
            total_debit=Decimal("5000.00"),
            total_credit=Decimal("5000.00"),
            is_balanced=True,
        )
        assert entry.total_debit == Decimal("5000.00")
        assert entry.total_credit == Decimal("5000.00")
        assert entry.is_balanced is True

    def test_entry_posted(self) -> None:
        """Test posted entry."""
        posted_by = uuid4()
        approved_by = uuid4()
        entry = JournalEntry(
            condominio_id=uuid4(),
            entry_number="LC-2024-00003",
            entry_date=date(2024, 1, 25),
            period_id=uuid4(),
            description="Despesa operacional",
            status=EntryStatus.POSTED,
            approved_at=datetime(2024, 1, 25, 10, 0, 0),
            approved_by_id=approved_by,
            posted_at=datetime(2024, 1, 25, 14, 0, 0),
            posted_by_id=posted_by,
        )
        assert entry.status == EntryStatus.POSTED
        assert entry.approved_by_id == approved_by
        assert entry.posted_by_id == posted_by

    def test_entry_with_reversal(self) -> None:
        """Test entry with reversal info."""
        original_entry = uuid4()
        entry = JournalEntry(
            condominio_id=uuid4(),
            entry_number="LC-2024-00004",
            entry_date=date(2024, 1, 30),
            period_id=uuid4(),
            description="Estorno de lancamento",
            entry_type=EntryType.REVERSAL,
            reversed_entry_id=original_entry,
            reversal_reason="Lancamento incorreto",
        )
        assert entry.entry_type == EntryType.REVERSAL
        assert entry.reversed_entry_id == original_entry
        assert entry.reversal_reason == "Lancamento incorreto"


class TestJournalEntryLineModel:
    """Tests for JournalEntryLine model."""

    def test_line_creation_basic(self) -> None:
        """Test basic journal entry line creation."""
        entry_id = uuid4()
        account_id = uuid4()
        line = JournalEntryLine(
            entry_id=entry_id,
            account_id=account_id,
            line_number=1,
            debit_amount=Decimal("1000.00"),
            credit_amount=Decimal("0.00"),
            description="Debito em caixa",
        )
        assert line.entry_id == entry_id
        assert line.account_id == account_id
        assert line.line_number == 1
        assert line.debit_amount == Decimal("1000.00")
        assert line.credit_amount == Decimal("0.00")

    def test_line_with_cost_center(self) -> None:
        """Test line with cost center."""
        cost_center_id = uuid4()
        line = JournalEntryLine(
            entry_id=uuid4(),
            account_id=uuid4(),
            line_number=1,
            debit_amount=Decimal("0.00"),
            credit_amount=Decimal("500.00"),
            cost_center_id=cost_center_id,
            description="Receita de servicos",
        )
        assert line.cost_center_id == cost_center_id
        assert line.credit_amount == Decimal("500.00")

    def test_line_with_document(self) -> None:
        """Test line with document reference."""
        line = JournalEntryLine(
            entry_id=uuid4(),
            account_id=uuid4(),
            line_number=2,
            debit_amount=Decimal("2500.00"),
            credit_amount=Decimal("0.00"),
            description="Pagamento NF 12345",
            document_type="NF",
            document_number="12345",
            document_date=date(2024, 1, 10),
        )
        assert line.document_type == "NF"
        assert line.document_number == "12345"
        assert line.document_date == date(2024, 1, 10)

    def test_line_with_historical(self) -> None:
        """Test line with historical info."""
        line = JournalEntryLine(
            entry_id=uuid4(),
            account_id=uuid4(),
            line_number=1,
            debit_amount=Decimal("3000.00"),
            credit_amount=Decimal("0.00"),
            description="Compra de material",
            historical="Material de escritorio - Papelaria ABC",
        )
        assert line.historical == "Material de escritorio - Papelaria ABC"


class TestTrialBalanceModel:
    """Tests for TrialBalance model."""

    def test_balance_creation_basic(self) -> None:
        """Test basic trial balance creation."""
        condo_id = uuid4()
        chart_id = uuid4()
        period_id = uuid4()
        balance = TrialBalance(
            condominio_id=condo_id,
            chart_id=chart_id,
            period_id=period_id,
            reference_date=date(2024, 1, 31),
            name="Balancete Janeiro 2024",
        )
        assert balance.reference_date == date(2024, 1, 31)
        assert balance.name == "Balancete Janeiro 2024"
        assert balance.balance_type == BalanceType.VERIFICATION
        assert balance.status == BalanceStatus.DRAFT
        assert balance.balance_period == BalancePeriod.MONTHLY
        assert balance.active is True

    def test_balance_type_enum(self) -> None:
        """Test BalanceType enum values."""
        assert BalanceType.VERIFICATION.value == "VERIFICATION"
        assert BalanceType.OPENING.value == "OPENING"
        assert BalanceType.CLOSING.value == "CLOSING"
        assert BalanceType.ADJUSTED.value == "ADJUSTED"
        assert BalanceType.CONSOLIDATED.value == "CONSOLIDATED"

    def test_balance_status_enum(self) -> None:
        """Test BalanceStatus enum values."""
        assert BalanceStatus.DRAFT.value == "DRAFT"
        assert BalanceStatus.GENERATED.value == "GENERATED"
        assert BalanceStatus.VERIFIED.value == "VERIFIED"
        assert BalanceStatus.APPROVED.value == "APPROVED"
        assert BalanceStatus.CLOSED.value == "CLOSED"

    def test_balance_period_enum(self) -> None:
        """Test BalancePeriod enum values."""
        assert BalancePeriod.MONTHLY.value == "MONTHLY"
        assert BalancePeriod.QUARTERLY.value == "QUARTERLY"
        assert BalancePeriod.SEMIANNUAL.value == "SEMIANNUAL"
        assert BalancePeriod.ANNUAL.value == "ANNUAL"
        assert BalancePeriod.CUSTOM.value == "CUSTOM"

    def test_balance_with_totals(self) -> None:
        """Test balance with totals."""
        balance = TrialBalance(
            condominio_id=uuid4(),
            chart_id=uuid4(),
            period_id=uuid4(),
            reference_date=date(2024, 2, 29),
            name="Balancete Fevereiro 2024",
            total_debit=Decimal("150000.00"),
            total_credit=Decimal("150000.00"),
            total_debit_balance=Decimal("85000.00"),
            total_credit_balance=Decimal("65000.00"),
            is_balanced=True,
            accounts_count=45,
        )
        assert balance.total_debit == Decimal("150000.00")
        assert balance.total_credit == Decimal("150000.00")
        assert balance.is_balanced is True
        assert balance.accounts_count == 45

    def test_balance_approved(self) -> None:
        """Test approved balance."""
        approved_by = uuid4()
        generated_by = uuid4()
        balance = TrialBalance(
            condominio_id=uuid4(),
            chart_id=uuid4(),
            period_id=uuid4(),
            reference_date=date(2024, 3, 31),
            name="Balancete Março 2024",
            status=BalanceStatus.APPROVED,
            generated_at=datetime(2024, 4, 1, 9, 0, 0),
            generated_by_id=generated_by,
            approved_at=datetime(2024, 4, 2, 15, 30, 0),
            approved_by_id=approved_by,
        )
        assert balance.status == BalanceStatus.APPROVED
        assert balance.generated_by_id == generated_by
        assert balance.approved_by_id == approved_by

    def test_balance_with_date_range(self) -> None:
        """Test balance with custom date range."""
        balance = TrialBalance(
            condominio_id=uuid4(),
            chart_id=uuid4(),
            period_id=uuid4(),
            reference_date=date(2024, 6, 30),
            name="Balancete 1o Semestre 2024",
            balance_period=BalancePeriod.SEMIANNUAL,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
        )
        assert balance.balance_period == BalancePeriod.SEMIANNUAL
        assert balance.start_date == date(2024, 1, 1)
        assert balance.end_date == date(2024, 6, 30)


class TestTrialBalanceItemModel:
    """Tests for TrialBalanceItem model."""

    def test_balance_item_creation_basic(self) -> None:
        """Test basic trial balance item creation."""
        trial_balance_id = uuid4()
        account_id = uuid4()
        item = TrialBalanceItem(
            trial_balance_id=trial_balance_id,
            account_id=account_id,
            account_code="1.1.1.01",
            account_name="Caixa",
        )
        assert item.trial_balance_id == trial_balance_id
        assert item.account_id == account_id
        assert item.account_code == "1.1.1.01"
        assert item.account_name == "Caixa"

    def test_balance_item_with_balances(self) -> None:
        """Test balance item with balances."""
        item = TrialBalanceItem(
            trial_balance_id=uuid4(),
            account_id=uuid4(),
            account_code="1.1.1.01",
            account_name="Caixa",
            previous_debit_balance=Decimal("10000.00"),
            previous_credit_balance=Decimal("0.00"),
            period_debit=Decimal("5000.00"),
            period_credit=Decimal("3000.00"),
            current_debit_balance=Decimal("12000.00"),
            current_credit_balance=Decimal("0.00"),
        )
        assert item.previous_debit_balance == Decimal("10000.00")
        assert item.period_debit == Decimal("5000.00")
        assert item.period_credit == Decimal("3000.00")
        assert item.current_debit_balance == Decimal("12000.00")

    def test_balance_item_with_level(self) -> None:
        """Test balance item with hierarchy level."""
        parent_id = uuid4()
        item = TrialBalanceItem(
            trial_balance_id=uuid4(),
            account_id=uuid4(),
            account_code="1.1",
            account_name="Ativo Circulante",
            level=2,
            parent_id=parent_id,
            is_synthetic=True,
        )
        assert item.level == 2
        assert item.parent_id == parent_id
        assert item.is_synthetic is True

    def test_balance_item_with_variance(self) -> None:
        """Test balance item with variance calculation."""
        item = TrialBalanceItem(
            trial_balance_id=uuid4(),
            account_id=uuid4(),
            account_code="4.1.1.01",
            account_name="Despesas com Pessoal",
            current_debit_balance=Decimal("45000.00"),
            budget_amount=Decimal("50000.00"),
            variance_amount=Decimal("-5000.00"),
            variance_percent=Decimal("-10.00"),
        )
        assert item.budget_amount == Decimal("50000.00")
        assert item.variance_amount == Decimal("-5000.00")
        assert item.variance_percent == Decimal("-10.00")
