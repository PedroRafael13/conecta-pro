"""Balance Sheet Service - Serviço de Balancete e Balanço Patrimonial.

Sprint 29 - Balancete e Fechamento.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.accounting_account import (
    AccountClassification,
    AccountingAccount,
    AccountNature,
    AccountStatus,
    AccountType,
)
from modules.financial.models.journal_entry import EntryStatus, JournalEntry, JournalEntryLine


class BalanceSheetGroupType(StrEnum):
    """Grupos do Balanço Patrimonial."""

    # Ativo
    ATIVO_CIRCULANTE = "ATIVO_CIRCULANTE"
    ATIVO_NAO_CIRCULANTE = "ATIVO_NAO_CIRCULANTE"
    # Passivo
    PASSIVO_CIRCULANTE = "PASSIVO_CIRCULANTE"
    PASSIVO_NAO_CIRCULANTE = "PASSIVO_NAO_CIRCULANTE"
    # Patrimônio Líquido
    PATRIMONIO_LIQUIDO = "PATRIMONIO_LIQUIDO"


class TrialBalanceType(StrEnum):
    """Tipos de balancete."""

    VERIFICATION = "VERIFICATION"  # Balancete de verificação
    ANALYTICAL = "ANALYTICAL"  # Analítico (todas as contas)
    SYNTHETIC = "SYNTHETIC"  # Sintético (apenas sintéticas)


@dataclass
class AccountBalance:
    """Saldo de uma conta contábil."""

    account_id: UUID
    account_code: str
    account_name: str
    account_type: AccountType
    account_nature: AccountNature
    level: int
    is_analytical: bool
    parent_id: UUID | None = None

    # Saldos
    previous_debit: Decimal = Decimal("0")
    previous_credit: Decimal = Decimal("0")
    previous_balance: Decimal = Decimal("0")

    period_debit: Decimal = Decimal("0")
    period_credit: Decimal = Decimal("0")

    current_debit: Decimal = Decimal("0")
    current_credit: Decimal = Decimal("0")
    current_balance: Decimal = Decimal("0")

    # Análise
    variation_absolute: Decimal = Decimal("0")
    variation_percentage: Decimal = Decimal("0")

    # Hierarquia
    children: list["AccountBalance"] = field(default_factory=list)

    def calculate_balance(self) -> None:
        """Calcula saldos baseado na natureza da conta."""
        # Saldo anterior
        if self.account_nature == AccountNature.DEBIT:
            self.previous_balance = self.previous_debit - self.previous_credit
        else:
            self.previous_balance = self.previous_credit - self.previous_debit

        # Saldo atual
        total_debit = self.previous_debit + self.period_debit
        total_credit = self.previous_credit + self.period_credit

        self.current_debit = total_debit
        self.current_credit = total_credit

        if self.account_nature == AccountNature.DEBIT:
            self.current_balance = total_debit - total_credit
        else:
            self.current_balance = total_credit - total_debit

        # Variação
        if self.previous_balance != Decimal("0"):
            self.variation_absolute = self.current_balance - self.previous_balance
            self.variation_percentage = (self.variation_absolute / abs(self.previous_balance)) * Decimal("100")


@dataclass
class TrialBalanceReport:
    """Relatório de Balancete de Verificação."""

    condominio_id: UUID
    report_date: date
    start_date: date
    end_date: date
    balance_type: TrialBalanceType
    generated_at: datetime = field(default_factory=datetime.utcnow)

    # Itens do balancete
    items: list[AccountBalance] = field(default_factory=list)

    # Totais
    total_accounts: int = 0
    total_analytical: int = 0

    # Saldos anteriores
    total_previous_debit: Decimal = Decimal("0")
    total_previous_credit: Decimal = Decimal("0")

    # Movimentos do período
    total_period_debit: Decimal = Decimal("0")
    total_period_credit: Decimal = Decimal("0")

    # Saldos atuais
    total_current_debit: Decimal = Decimal("0")
    total_current_credit: Decimal = Decimal("0")

    # Verificação
    is_balanced: bool = True
    difference: Decimal = Decimal("0")

    def calculate_totals(self) -> None:
        """Calcula totais do balancete."""
        self.total_accounts = len(self.items)
        self.total_analytical = sum(1 for item in self.items if item.is_analytical)

        # Soma apenas contas analíticas
        for item in self.items:
            if item.is_analytical:
                self.total_previous_debit += item.previous_debit
                self.total_previous_credit += item.previous_credit
                self.total_period_debit += item.period_debit
                self.total_period_credit += item.period_credit
                self.total_current_debit += item.current_debit
                self.total_current_credit += item.current_credit

        # Verificação
        self.difference = self.total_current_debit - self.total_current_credit
        self.is_balanced = abs(self.difference) < Decimal("0.01")


@dataclass
class BalanceSheetGroup:
    """Grupo do Balanço Patrimonial."""

    group_type: BalanceSheetGroupType
    name: str
    total: Decimal = Decimal("0")
    items: list[AccountBalance] = field(default_factory=list)
    percentage: Decimal = Decimal("0")  # Análise vertical

    def calculate_total(self) -> None:
        """Calcula total do grupo."""
        self.total = sum((item.current_balance for item in self.items), Decimal("0"))


@dataclass
class BalanceSheetReport:
    """Relatório de Balanço Patrimonial."""

    condominio_id: UUID
    reference_date: date
    generated_at: datetime = field(default_factory=datetime.utcnow)

    # Grupos do Ativo
    ativo_circulante: BalanceSheetGroup = field(
        default_factory=lambda: BalanceSheetGroup(
            group_type=BalanceSheetGroupType.ATIVO_CIRCULANTE, name="Ativo Circulante"
        )
    )
    ativo_nao_circulante: BalanceSheetGroup = field(
        default_factory=lambda: BalanceSheetGroup(
            group_type=BalanceSheetGroupType.ATIVO_NAO_CIRCULANTE, name="Ativo Não Circulante"
        )
    )

    # Grupos do Passivo
    passivo_circulante: BalanceSheetGroup = field(
        default_factory=lambda: BalanceSheetGroup(
            group_type=BalanceSheetGroupType.PASSIVO_CIRCULANTE, name="Passivo Circulante"
        )
    )
    passivo_nao_circulante: BalanceSheetGroup = field(
        default_factory=lambda: BalanceSheetGroup(
            group_type=BalanceSheetGroupType.PASSIVO_NAO_CIRCULANTE, name="Passivo Não Circulante"
        )
    )

    # Patrimônio Líquido
    patrimonio_liquido: BalanceSheetGroup = field(
        default_factory=lambda: BalanceSheetGroup(
            group_type=BalanceSheetGroupType.PATRIMONIO_LIQUIDO, name="Patrimônio Líquido"
        )
    )

    # Totais
    total_ativo: Decimal = Decimal("0")
    total_passivo: Decimal = Decimal("0")
    total_patrimonio: Decimal = Decimal("0")
    total_passivo_patrimonio: Decimal = Decimal("0")

    # Verificação
    is_balanced: bool = True
    difference: Decimal = Decimal("0")

    # Comparativo (período anterior)
    previous_total_ativo: Decimal = Decimal("0")
    previous_total_passivo_patrimonio: Decimal = Decimal("0")
    variation_ativo: Decimal = Decimal("0")
    variation_passivo_patrimonio: Decimal = Decimal("0")

    def calculate_totals(self) -> None:
        """Calcula totais do balanço."""
        # Calcula totais dos grupos
        self.ativo_circulante.calculate_total()
        self.ativo_nao_circulante.calculate_total()
        self.passivo_circulante.calculate_total()
        self.passivo_nao_circulante.calculate_total()
        self.patrimonio_liquido.calculate_total()

        # Totais gerais
        self.total_ativo = self.ativo_circulante.total + self.ativo_nao_circulante.total
        self.total_passivo = self.passivo_circulante.total + self.passivo_nao_circulante.total
        self.total_patrimonio = self.patrimonio_liquido.total
        self.total_passivo_patrimonio = self.total_passivo + self.total_patrimonio

        # Verificação (Ativo = Passivo + PL)
        self.difference = self.total_ativo - self.total_passivo_patrimonio
        self.is_balanced = abs(self.difference) < Decimal("0.01")

        # Análise vertical
        if self.total_ativo > Decimal("0"):
            self.ativo_circulante.percentage = (self.ativo_circulante.total / self.total_ativo) * Decimal("100")
            self.ativo_nao_circulante.percentage = (self.ativo_nao_circulante.total / self.total_ativo) * Decimal("100")

        if self.total_passivo_patrimonio > Decimal("0"):
            self.passivo_circulante.percentage = (
                self.passivo_circulante.total / self.total_passivo_patrimonio
            ) * Decimal("100")
            self.passivo_nao_circulante.percentage = (
                self.passivo_nao_circulante.total / self.total_passivo_patrimonio
            ) * Decimal("100")
            self.patrimonio_liquido.percentage = (
                self.patrimonio_liquido.total / self.total_passivo_patrimonio
            ) * Decimal("100")


class BalanceSheetService:
    """Serviço de Balancete e Balanço Patrimonial."""

    def __init__(self, session: AsyncSession):
        """Inicializa o serviço.

        Args:
            session: Sessão assíncrona do banco de dados.
        """
        self.session = session

    async def generate_trial_balance(
        self,
        condominio_id: UUID,
        start_date: date,
        end_date: date,
        balance_type: TrialBalanceType = TrialBalanceType.VERIFICATION,
        include_zero_balance: bool = False,
        cost_center_id: UUID | None = None,
    ) -> TrialBalanceReport:
        """Gera balancete de verificação.

        Args:
            condominio_id: ID do condomínio.
            start_date: Data inicial do período.
            end_date: Data final do período.
            balance_type: Tipo de balancete.
            include_zero_balance: Incluir contas com saldo zero.
            cost_center_id: Filtrar por centro de custo.

        Returns:
            TrialBalanceReport com os dados do balancete.
        """
        report = TrialBalanceReport(
            condominio_id=condominio_id,
            report_date=end_date,
            start_date=start_date,
            end_date=end_date,
            balance_type=balance_type,
        )

        # Busca contas
        accounts = await self._get_accounts(condominio_id, balance_type)

        # Calcula saldos para cada conta
        for account in accounts:
            balance = await self._calculate_account_balance(
                account=account,
                start_date=start_date,
                end_date=end_date,
                cost_center_id=cost_center_id,
            )

            if include_zero_balance or balance.current_balance != Decimal("0"):
                report.items.append(balance)

        # Ordena por código da conta
        report.items.sort(key=lambda x: x.account_code)

        # Calcula totais
        report.calculate_totals()

        return report

    async def generate_balance_sheet(
        self,
        condominio_id: UUID,
        reference_date: date,
        include_comparison: bool = True,
    ) -> BalanceSheetReport:
        """Gera balanço patrimonial.

        Args:
            condominio_id: ID do condomínio.
            reference_date: Data de referência do balanço.
            include_comparison: Incluir comparação com período anterior.

        Returns:
            BalanceSheetReport com os dados do balanço.
        """
        report = BalanceSheetReport(
            condominio_id=condominio_id,
            reference_date=reference_date,
        )

        # Busca contas patrimoniais
        accounts = await self._get_accounts(condominio_id, TrialBalanceType.ANALYTICAL)

        # Data inicial (início do exercício)
        start_of_year = date(reference_date.year, 1, 1)

        # Classifica contas por grupo
        for account in accounts:
            balance = await self._calculate_account_balance(
                account=account,
                start_date=start_of_year,
                end_date=reference_date,
            )

            # Apenas contas com saldo
            if balance.current_balance == Decimal("0"):
                continue

            # Classifica no grupo apropriado
            self._classify_account_in_balance_sheet(report, balance)

        # Calcula totais
        report.calculate_totals()

        # Comparação com período anterior
        if include_comparison:
            await self._add_previous_period_comparison(report, condominio_id, reference_date)

        return report

    async def get_account_statement(
        self,
        condominio_id: UUID,
        account_id: UUID,
        start_date: date,
        end_date: date,
    ) -> dict:
        """Obtém extrato de uma conta.

        Args:
            condominio_id: ID do condomínio.
            account_id: ID da conta.
            start_date: Data inicial.
            end_date: Data final.

        Returns:
            Dict com extrato da conta.
        """
        # Busca a conta
        account_query = select(AccountingAccount).where(
            and_(
                AccountingAccount.condominio_id == condominio_id,
                AccountingAccount.id == account_id,
            )
        )
        result = await self.session.execute(account_query)
        account = result.scalar_one_or_none()

        if not account:
            return {"error": "Conta não encontrada"}

        # Saldo anterior
        previous_balance = await self._get_account_balance_at_date(account_id, start_date - timedelta(days=1))

        # Lançamentos do período
        entries_query = (
            select(
                JournalEntry.entry_date,
                JournalEntry.entry_number,
                JournalEntry.description,
                JournalEntryLine.debit_amount,
                JournalEntryLine.credit_amount,
                JournalEntryLine.description.label("line_description"),
            )
            .join(JournalEntryLine)
            .where(
                and_(
                    JournalEntryLine.account_id == account_id,
                    JournalEntry.entry_date >= start_date,
                    JournalEntry.entry_date <= end_date,
                    JournalEntry.status == EntryStatus.POSTED,
                )
            )
            .order_by(JournalEntry.entry_date, JournalEntry.entry_number)
        )

        result = await self.session.execute(entries_query)
        entries = result.fetchall()

        # Monta extrato
        statement_entries = []
        running_balance = previous_balance

        for entry in entries:
            if account.nature == AccountNature.DEBIT:
                running_balance += entry.debit_amount - entry.credit_amount
            else:
                running_balance += entry.credit_amount - entry.debit_amount

            statement_entries.append(
                {
                    "date": entry.entry_date,
                    "entry_number": entry.entry_number,
                    "description": entry.line_description or entry.description,
                    "debit": entry.debit_amount,
                    "credit": entry.credit_amount,
                    "balance": running_balance,
                }
            )

        return {
            "account_id": str(account_id),
            "account_code": account.code,
            "account_name": account.name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "opening_balance": previous_balance,
            "closing_balance": running_balance,
            "entries": statement_entries,
            "total_entries": len(statement_entries),
        }

    async def get_comparison_report(
        self,
        condominio_id: UUID,
        current_end_date: date,
        previous_end_date: date,
    ) -> dict:
        """Gera relatório comparativo entre dois períodos.

        Args:
            condominio_id: ID do condomínio.
            current_end_date: Data final do período atual.
            previous_end_date: Data final do período anterior.

        Returns:
            Dict com análise comparativa.
        """
        # Balanços dos dois períodos
        current_balance = await self.generate_balance_sheet(condominio_id, current_end_date, include_comparison=False)
        previous_balance = await self.generate_balance_sheet(condominio_id, previous_end_date, include_comparison=False)

        # Análise comparativa
        comparison = {
            "current_period": current_end_date.isoformat(),
            "previous_period": previous_end_date.isoformat(),
            "ativo": {
                "current": current_balance.total_ativo,
                "previous": previous_balance.total_ativo,
                "variation": current_balance.total_ativo - previous_balance.total_ativo,
                "variation_pct": self._calc_variation_pct(current_balance.total_ativo, previous_balance.total_ativo),
            },
            "passivo": {
                "current": current_balance.total_passivo,
                "previous": previous_balance.total_passivo,
                "variation": current_balance.total_passivo - previous_balance.total_passivo,
                "variation_pct": self._calc_variation_pct(
                    current_balance.total_passivo, previous_balance.total_passivo
                ),
            },
            "patrimonio": {
                "current": current_balance.total_patrimonio,
                "previous": previous_balance.total_patrimonio,
                "variation": (current_balance.total_patrimonio - previous_balance.total_patrimonio),
                "variation_pct": self._calc_variation_pct(
                    current_balance.total_patrimonio, previous_balance.total_patrimonio
                ),
            },
            "is_balanced": current_balance.is_balanced and previous_balance.is_balanced,
        }

        return comparison

    async def validate_balance(self, condominio_id: UUID, reference_date: date) -> dict:
        """Valida consistência do balancete.

        Args:
            condominio_id: ID do condomínio.
            reference_date: Data de referência.

        Returns:
            Dict com resultado da validação.
        """
        start_of_year = date(reference_date.year, 1, 1)

        trial_balance = await self.generate_trial_balance(
            condominio_id=condominio_id,
            start_date=start_of_year,
            end_date=reference_date,
            include_zero_balance=True,
        )

        issues = []

        # Verifica se está balanceado
        if not trial_balance.is_balanced:
            issues.append(
                {
                    "type": "UNBALANCED",
                    "message": f"Balancete não balanceado. Diferença: {trial_balance.difference}",
                    "severity": "ERROR",
                }
            )

        # Verifica contas sem movimento há muito tempo
        for item in trial_balance.items:
            if item.is_analytical and item.period_debit == 0 and item.period_credit == 0:
                if item.current_balance != Decimal("0"):
                    issues.append(
                        {
                            "type": "NO_MOVEMENT",
                            "message": f"Conta {item.account_code} sem movimento no período",
                            "severity": "WARNING",
                            "account_id": str(item.account_id),
                        }
                    )

        return {
            "reference_date": reference_date.isoformat(),
            "is_valid": len([i for i in issues if i["severity"] == "ERROR"]) == 0,
            "is_balanced": trial_balance.is_balanced,
            "total_debit": trial_balance.total_current_debit,
            "total_credit": trial_balance.total_current_credit,
            "difference": trial_balance.difference,
            "issues": issues,
            "issues_count": len(issues),
        }

    # --- Métodos privados ---

    async def _get_accounts(
        self,
        condominio_id: UUID,
        balance_type: TrialBalanceType,
    ) -> list[AccountingAccount]:
        """Busca contas conforme o tipo de balancete."""
        query = select(AccountingAccount).where(
            and_(
                AccountingAccount.condominio_id == condominio_id,
                AccountingAccount.status == AccountStatus.ACTIVE,
                AccountingAccount.active.is_(True),
            )
        )

        if balance_type == TrialBalanceType.ANALYTICAL:
            query = query.where(AccountingAccount.classification == AccountClassification.ANALYTICAL)
        elif balance_type == TrialBalanceType.SYNTHETIC:
            query = query.where(AccountingAccount.classification == AccountClassification.SYNTHETIC)

        query = query.order_by(AccountingAccount.code)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _calculate_account_balance(
        self,
        account: AccountingAccount,
        start_date: date,
        end_date: date,
        cost_center_id: UUID | None = None,
    ) -> AccountBalance:
        """Calcula saldo de uma conta no período."""
        balance = AccountBalance(
            account_id=account.id,
            account_code=account.code,
            account_name=account.name,
            account_type=account.account_type,
            account_nature=account.nature,
            level=account.level,
            is_analytical=account.is_analytical,
            parent_id=account.parent_id,
        )

        # Saldo anterior ao período
        balance.previous_debit, balance.previous_credit = await self._get_movements_until(
            account.id,
            start_date - timedelta(days=1),
            cost_center_id,
        )

        # Movimentos do período
        balance.period_debit, balance.period_credit = await self._get_movements_in_period(
            account.id,
            start_date,
            end_date,
            cost_center_id,
        )

        # Calcula saldos
        balance.calculate_balance()

        return balance

    async def _get_movements_until(
        self,
        account_id: UUID,
        until_date: date,
        cost_center_id: UUID | None = None,
    ) -> tuple[Decimal, Decimal]:
        """Obtém movimentos até uma data."""
        query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), 0),
                func.coalesce(func.sum(JournalEntryLine.credit_amount), 0),
            )
            .join(JournalEntry)
            .where(
                and_(
                    JournalEntryLine.account_id == account_id,
                    JournalEntry.entry_date <= until_date,
                    JournalEntry.status == EntryStatus.POSTED,
                )
            )
        )

        if cost_center_id:
            query = query.where(JournalEntryLine.cost_center_id == cost_center_id)

        result = await self.session.execute(query)
        row = result.one()

        return Decimal(str(row[0])), Decimal(str(row[1]))

    async def _get_movements_in_period(
        self,
        account_id: UUID,
        start_date: date,
        end_date: date,
        cost_center_id: UUID | None = None,
    ) -> tuple[Decimal, Decimal]:
        """Obtém movimentos de um período."""
        query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), 0),
                func.coalesce(func.sum(JournalEntryLine.credit_amount), 0),
            )
            .join(JournalEntry)
            .where(
                and_(
                    JournalEntryLine.account_id == account_id,
                    JournalEntry.entry_date >= start_date,
                    JournalEntry.entry_date <= end_date,
                    JournalEntry.status == EntryStatus.POSTED,
                )
            )
        )

        if cost_center_id:
            query = query.where(JournalEntryLine.cost_center_id == cost_center_id)

        result = await self.session.execute(query)
        row = result.one()

        return Decimal(str(row[0])), Decimal(str(row[1]))

    async def _get_account_balance_at_date(
        self,
        account_id: UUID,
        reference_date: date,
    ) -> Decimal:
        """Obtém saldo de uma conta em uma data."""
        # Busca a conta para saber a natureza
        account_query = select(AccountingAccount).where(AccountingAccount.id == account_id)
        result = await self.session.execute(account_query)
        account = result.scalar_one_or_none()

        if not account:
            return Decimal("0")

        debit, credit = await self._get_movements_until(account_id, reference_date)

        if account.nature == AccountNature.DEBIT:
            return debit - credit
        return credit - debit

    def _classify_account_in_balance_sheet(
        self,
        report: BalanceSheetReport,
        balance: AccountBalance,
    ) -> None:
        """Classifica conta no grupo apropriado do balanço."""
        account_type = balance.account_type

        if account_type == AccountType.ASSET:
            # Ativo - verifica se é circulante pelo código ou classificação
            if balance.account_code.startswith("1.1"):
                report.ativo_circulante.items.append(balance)
            else:
                report.ativo_nao_circulante.items.append(balance)

        elif account_type == AccountType.LIABILITY:
            # Passivo
            if balance.account_code.startswith("2.1"):
                report.passivo_circulante.items.append(balance)
            else:
                report.passivo_nao_circulante.items.append(balance)

        elif account_type == AccountType.EQUITY:
            report.patrimonio_liquido.items.append(balance)

    async def _add_previous_period_comparison(
        self,
        report: BalanceSheetReport,
        condominio_id: UUID,
        reference_date: date,
    ) -> None:
        """Adiciona comparação com período anterior."""
        # Período anterior (ano anterior na mesma data)
        previous_date = date(reference_date.year - 1, reference_date.month, reference_date.day)

        previous_balance = await self.generate_balance_sheet(
            condominio_id,
            previous_date,
            include_comparison=False,
        )

        report.previous_total_ativo = previous_balance.total_ativo
        report.previous_total_passivo_patrimonio = previous_balance.total_passivo_patrimonio

        # Variações
        report.variation_ativo = report.total_ativo - report.previous_total_ativo
        report.variation_passivo_patrimonio = report.total_passivo_patrimonio - report.previous_total_passivo_patrimonio

    def _calc_variation_pct(
        self,
        current: Decimal,
        previous: Decimal,
    ) -> Decimal:
        """Calcula variação percentual."""
        if previous == Decimal("0"):
            return Decimal("0")
        return ((current - previous) / abs(previous)) * Decimal("100")
