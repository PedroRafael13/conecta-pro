"""Period Closing Service - Serviço de Fechamento Contábil.

Sprint 29 - Balancete e Fechamento.
Responsável por:
- Fechamento mensal automático
- Provisões automáticas
- Conciliação contábil
- Auditoria de lançamentos
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.accounting_account import (
    AccountingAccount,
    AccountNature,
    AccountType,
)
from modules.financial.models.accounting_period import (
    AccountingPeriod,
    ClosingType,
    PeriodStatus,
    PeriodType,
)
from modules.financial.models.journal_entry import (
    EntryOrigin,
    EntryStatus,
    EntryType,
    JournalEntry,
    JournalEntryLine,
)


class ClosingStepType(StrEnum):
    """Tipos de etapas do fechamento."""

    VALIDATE_ENTRIES = "VALIDATE_ENTRIES"  # Validar lançamentos
    CHECK_BALANCE = "CHECK_BALANCE"  # Verificar balanceamento
    GENERATE_PROVISIONS = "GENERATE_PROVISIONS"  # Gerar provisões
    CLOSE_RESULT_ACCOUNTS = "CLOSE_RESULT_ACCOUNTS"  # Encerrar contas de resultado
    TRANSFER_RESULT = "TRANSFER_RESULT"  # Transferir resultado para PL
    GENERATE_TRIAL_BALANCE = "GENERATE_TRIAL_BALANCE"  # Gerar balancete
    FINALIZE = "FINALIZE"  # Finalizar fechamento


class ProvisionType(StrEnum):
    """Tipos de provisões."""

    DEPRECIATION = "DEPRECIATION"  # Depreciação
    VACATION = "VACATION"  # Férias
    THIRTEENTH = "THIRTEENTH"  # 13º salário
    TAX = "TAX"  # Impostos
    BAD_DEBT = "BAD_DEBT"  # Perdas estimadas
    OTHER = "OTHER"  # Outras


class AuditIssueType(StrEnum):
    """Tipos de problemas de auditoria."""

    UNBALANCED_ENTRY = "UNBALANCED_ENTRY"  # Lançamento não balanceado
    MISSING_DOCUMENT = "MISSING_DOCUMENT"  # Documento faltante
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"  # Lançamento duplicado
    INVALID_ACCOUNT = "INVALID_ACCOUNT"  # Conta inválida
    PERIOD_MISMATCH = "PERIOD_MISMATCH"  # Data fora do período
    UNAUTHORIZED = "UNAUTHORIZED"  # Lançamento não autorizado
    RECONCILIATION_PENDING = "RECONCILIATION_PENDING"  # Conciliação pendente


@dataclass
class ClosingStep:
    """Etapa do processo de fechamento."""

    step_type: ClosingStepType
    name: str
    status: str = "pending"  # pending, running, completed, failed
    message: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None
    details: dict = field(default_factory=dict)


@dataclass
class ProvisionEntry:
    """Entrada de provisão."""

    provision_type: ProvisionType
    description: str
    debit_account_id: UUID
    credit_account_id: UUID
    amount: Decimal
    reference_date: date


@dataclass
class AuditIssue:
    """Problema identificado na auditoria."""

    issue_type: AuditIssueType
    severity: str  # ERROR, WARNING, INFO
    message: str
    entry_id: UUID | None = None
    account_id: UUID | None = None
    amount: Decimal = Decimal("0")
    details: dict = field(default_factory=dict)


@dataclass
class ClosingResult:
    """Resultado do fechamento."""

    condominio_id: UUID
    period_id: UUID
    year: int
    month: int
    started_at: datetime
    completed_at: datetime | None = None
    status: str = "in_progress"  # in_progress, completed, failed

    # Etapas
    steps: list[ClosingStep] = field(default_factory=list)

    # Resultado
    total_revenue: Decimal = Decimal("0")
    total_expenses: Decimal = Decimal("0")
    period_result: Decimal = Decimal("0")  # Lucro/Prejuízo

    # Lançamentos gerados
    closing_entry_id: UUID | None = None
    provisions_generated: int = 0

    # Problemas
    issues: list[AuditIssue] = field(default_factory=list)

    def add_step(self, step: ClosingStep) -> None:
        """Adiciona etapa ao processo."""
        self.steps.append(step)

    def add_issue(self, issue: AuditIssue) -> None:
        """Adiciona problema identificado."""
        self.issues.append(issue)

    @property
    def has_errors(self) -> bool:
        """Verifica se há erros críticos."""
        return any(issue.severity == "ERROR" for issue in self.issues)


class PeriodClosingService:
    """Serviço de Fechamento de Período Contábil."""

    def __init__(self, session: AsyncSession):
        """Inicializa o serviço.

        Args:
            session: Sessão assíncrona do banco de dados.
        """
        self.session = session

    async def close_period(
        self,
        condominio_id: UUID,
        year: int,
        month: int,
        closing_type: ClosingType = ClosingType.PROVISIONAL,
        generate_provisions: bool = True,
        user_id: UUID | None = None,
    ) -> ClosingResult:
        """Executa fechamento do período contábil.

        Args:
            condominio_id: ID do condomínio.
            year: Ano do período.
            month: Mês do período.
            closing_type: Tipo de fechamento.
            generate_provisions: Gerar provisões automáticas.
            user_id: ID do usuário executando.

        Returns:
            ClosingResult com resultado do fechamento.
        """
        # Busca ou cria período
        period = await self._get_or_create_period(condominio_id, year, month)

        result = ClosingResult(
            condominio_id=condominio_id,
            period_id=period.id,
            year=year,
            month=month,
            started_at=datetime.utcnow(),
        )

        # Etapa 1: Validar lançamentos
        await self._execute_step(
            result,
            ClosingStepType.VALIDATE_ENTRIES,
            "Validando lançamentos",
            self._validate_entries,
            period,
        )

        # Etapa 2: Verificar balanceamento
        await self._execute_step(
            result,
            ClosingStepType.CHECK_BALANCE,
            "Verificando balanceamento",
            self._check_balance,
            period,
        )

        # Verificar erros antes de continuar
        if result.has_errors:
            result.status = "failed"
            return result

        # Etapa 3: Gerar provisões (se habilitado)
        if generate_provisions:
            await self._execute_step(
                result,
                ClosingStepType.GENERATE_PROVISIONS,
                "Gerando provisões",
                self._generate_provisions,
                period,
                user_id,
            )

        # Etapa 4: Encerrar contas de resultado
        await self._execute_step(
            result,
            ClosingStepType.CLOSE_RESULT_ACCOUNTS,
            "Encerrando contas de resultado",
            self._close_result_accounts,
            period,
            user_id,
        )

        # Etapa 5: Transferir resultado para PL
        await self._execute_step(
            result,
            ClosingStepType.TRANSFER_RESULT,
            "Transferindo resultado",
            self._transfer_result_to_equity,
            period,
            result,
            user_id,
        )

        # Etapa 6: Finalizar fechamento
        await self._execute_step(
            result,
            ClosingStepType.FINALIZE,
            "Finalizando fechamento",
            self._finalize_closing,
            period,
            closing_type,
            user_id,
        )

        result.completed_at = datetime.utcnow()
        result.status = "completed" if not result.has_errors else "failed"

        return result

    async def reopen_period(
        self,
        condominio_id: UUID,
        year: int,
        month: int,
        reason: str,
        user_id: UUID | None = None,
    ) -> dict:
        """Reabre um período fechado.

        Args:
            condominio_id: ID do condomínio.
            year: Ano do período.
            month: Mês do período.
            reason: Motivo da reabertura.
            user_id: ID do usuário.

        Returns:
            Dict com resultado da reabertura.
        """
        period = await self._get_period(condominio_id, year, month)

        if not period:
            return {"success": False, "error": "Período não encontrado"}

        if not period.can_reopen:
            return {
                "success": False,
                "error": "Período não pode ser reaberto (SPED transmitido ou bloqueado)",
            }

        # Atualiza status
        period.status = PeriodStatus.REOPENED
        period.reopened_by = user_id
        period.reopened_at = datetime.utcnow()
        period.reopen_reason = reason
        period.reopen_count += 1

        await self.session.commit()

        return {
            "success": True,
            "period_id": str(period.id),
            "status": period.status.value,
            "reopen_count": period.reopen_count,
        }

    async def audit_entries(
        self,
        condominio_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[AuditIssue]:
        """Audita lançamentos do período.

        Args:
            condominio_id: ID do condomínio.
            start_date: Data inicial.
            end_date: Data final.

        Returns:
            Lista de problemas encontrados.
        """
        issues: list[AuditIssue] = []

        # Busca lançamentos do período
        entries_query = select(JournalEntry).where(
            and_(
                JournalEntry.condominio_id == condominio_id,
                JournalEntry.entry_date >= start_date,
                JournalEntry.entry_date <= end_date,
            )
        )

        result = await self.session.execute(entries_query)
        entries = result.scalars().all()

        for entry in entries:
            # Verifica balanceamento
            if not entry.is_balanced:
                issues.append(
                    AuditIssue(
                        issue_type=AuditIssueType.UNBALANCED_ENTRY,
                        severity="ERROR",
                        message=f"Lançamento {entry.entry_number} não balanceado",
                        entry_id=entry.id,
                        amount=abs(entry.total_debit - entry.total_credit),
                    )
                )

            # Verifica documento
            if entry.status == EntryStatus.POSTED and not entry.source_number:
                issues.append(
                    AuditIssue(
                        issue_type=AuditIssueType.MISSING_DOCUMENT,
                        severity="WARNING",
                        message=f"Lançamento {entry.entry_number} sem documento de origem",
                        entry_id=entry.id,
                    )
                )

        # Verifica duplicados
        duplicates = await self._find_duplicate_entries(condominio_id, start_date, end_date)
        issues.extend(duplicates)

        # Verifica conciliação pendente
        pending = await self._find_pending_reconciliation(condominio_id, end_date)
        issues.extend(pending)

        return issues

    async def generate_provision(
        self,
        condominio_id: UUID,
        provision: ProvisionEntry,
        user_id: UUID | None = None,
    ) -> UUID | None:
        """Gera lançamento de provisão.

        Args:
            condominio_id: ID do condomínio.
            provision: Dados da provisão.
            user_id: ID do usuário.

        Returns:
            ID do lançamento gerado ou None.
        """
        # Busca período
        period = await self._get_period(
            condominio_id,
            provision.reference_date.year,
            provision.reference_date.month,
        )

        if not period or not period.can_receive_entries:
            return None

        # Cria lançamento de provisão
        entry_number = await self._generate_entry_number(condominio_id)

        journal_entry = JournalEntry(
            condominio_id=condominio_id,
            period_id=period.id,
            entry_number=entry_number,
            description=provision.description,
            entry_type=EntryType.PROVISION,
            status=EntryStatus.DRAFT,
            origin=EntryOrigin.OTHER,
            entry_date=provision.reference_date,
            competence_date=provision.reference_date,
            total_debit=provision.amount,
            total_credit=provision.amount,
            line_count=2,
            created_by=user_id,
        )

        self.session.add(journal_entry)
        await self.session.flush()

        # Linhas do lançamento
        debit_line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=provision.debit_account_id,
            line_number=1,
            debit_amount=provision.amount,
            credit_amount=Decimal("0"),
            description=provision.description,
        )

        credit_line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=provision.credit_account_id,
            line_number=2,
            debit_amount=Decimal("0"),
            credit_amount=provision.amount,
            description=provision.description,
        )

        self.session.add_all([debit_line, credit_line])
        await self.session.commit()

        return journal_entry.id

    async def get_period_summary(
        self,
        condominio_id: UUID,
        year: int,
        month: int,
    ) -> dict:
        """Obtém resumo do período.

        Args:
            condominio_id: ID do condomínio.
            year: Ano.
            month: Mês.

        Returns:
            Dict com resumo do período.
        """
        period = await self._get_period(condominio_id, year, month)

        if not period:
            return {"error": "Período não encontrado"}

        # Calcula totais
        totals = await self._calculate_period_totals(period)

        return {
            "period_id": str(period.id),
            "code": period.code,
            "status": period.status.value,
            "start_date": period.start_date.isoformat(),
            "end_date": period.end_date.isoformat(),
            "total_entries": period.total_entries,
            "total_debit": totals["total_debit"],
            "total_credit": totals["total_credit"],
            "total_revenue": totals["total_revenue"],
            "total_expenses": totals["total_expenses"],
            "period_result": totals["total_revenue"] - totals["total_expenses"],
            "can_close": period.can_close,
            "can_reopen": period.can_reopen,
            "is_balanced": totals["total_debit"] == totals["total_credit"],
        }

    # --- Métodos privados ---

    async def _get_or_create_period(
        self,
        condominio_id: UUID,
        year: int,
        month: int,
    ) -> AccountingPeriod:
        """Obtém ou cria período contábil."""
        period = await self._get_period(condominio_id, year, month)

        if period:
            return period

        # Cria novo período
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - __import__("datetime").timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - __import__("datetime").timedelta(days=1)

        period = AccountingPeriod(
            condominio_id=condominio_id,
            code=f"{year}-{month:02d}",
            name=f"{self._get_month_name(month)} {year}",
            year=year,
            month=month,
            period_type=PeriodType.MONTHLY,
            status=PeriodStatus.OPEN,
            start_date=start_date,
            end_date=end_date,
            opening_date=datetime.utcnow(),
        )

        self.session.add(period)
        await self.session.flush()

        return period

    async def _get_period(
        self,
        condominio_id: UUID,
        year: int,
        month: int,
    ) -> AccountingPeriod | None:
        """Busca período existente."""
        query = select(AccountingPeriod).where(
            and_(
                AccountingPeriod.condominio_id == condominio_id,
                AccountingPeriod.year == year,
                AccountingPeriod.month == month,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _execute_step(
        self,
        result: ClosingResult,
        step_type: ClosingStepType,
        name: str,
        step_func,
        *args,
    ) -> None:
        """Executa uma etapa do fechamento."""
        step = ClosingStep(
            step_type=step_type,
            name=name,
            status="running",
            started_at=datetime.utcnow(),
        )
        result.add_step(step)

        try:
            step.details = await step_func(*args) or {}
            step.status = "completed"
        except Exception as exc:  # pylint: disable=broad-exception-caught
            step.status = "failed"
            step.message = str(exc)
            result.add_issue(
                AuditIssue(
                    issue_type=AuditIssueType.UNAUTHORIZED,
                    severity="ERROR",
                    message=f"Erro na etapa {name}: {exc}",
                )
            )
        finally:
            step.completed_at = datetime.utcnow()

    async def _validate_entries(self, period: AccountingPeriod) -> dict:
        """Valida lançamentos do período."""
        # Conta lançamentos por status
        count_query = (
            select(
                JournalEntry.status,
                func.count(JournalEntry.id).label("count"),
            )
            .where(JournalEntry.period_id == period.id)
            .group_by(JournalEntry.status)
        )

        result = await self.session.execute(count_query)
        counts = {row.status.value: row.count for row in result.fetchall()}

        return {
            "total_entries": sum(counts.values()),
            "posted": counts.get("POSTED", 0),
            "draft": counts.get("DRAFT", 0),
            "pending": counts.get("PENDING", 0),
        }

    async def _check_balance(self, period: AccountingPeriod) -> dict:
        """Verifica balanceamento do período."""
        totals_query = select(
            func.sum(JournalEntry.total_debit).label("total_debit"),
            func.sum(JournalEntry.total_credit).label("total_credit"),
        ).where(
            and_(
                JournalEntry.period_id == period.id,
                JournalEntry.status == EntryStatus.POSTED,
            )
        )

        result = await self.session.execute(totals_query)
        row = result.one()

        total_debit = Decimal(str(row.total_debit or 0))
        total_credit = Decimal(str(row.total_credit or 0))
        difference = total_debit - total_credit

        return {
            "total_debit": total_debit,
            "total_credit": total_credit,
            "difference": difference,
            "is_balanced": abs(difference) < Decimal("0.01"),
        }

    async def _generate_provisions(
        self,
        period: AccountingPeriod,  # pylint: disable=unused-argument
        user_id: UUID | None,  # pylint: disable=unused-argument
    ) -> dict:
        """Gera provisões automáticas."""
        # Placeholder - em produção, geraria provisões reais
        return {
            "depreciation_generated": False,
            "vacation_generated": False,
            "thirteenth_generated": False,
            "total_provisions": 0,
        }

    async def _close_result_accounts(
        self,
        period: AccountingPeriod,
        user_id: UUID | None,  # pylint: disable=unused-argument
    ) -> dict:
        """Encerra contas de resultado (receitas e despesas)."""
        # Busca contas de resultado com saldo
        accounts_query = select(AccountingAccount).where(
            and_(
                AccountingAccount.condominio_id == period.condominio_id,
                AccountingAccount.account_type.in_(
                    [
                        AccountType.REVENUE,
                        AccountType.EXPENSE,
                        AccountType.COST,
                    ]
                ),
                AccountingAccount.active.is_(True),
            )
        )

        result = await self.session.execute(accounts_query)
        accounts = result.scalars().all()

        total_revenue = Decimal("0")
        total_expenses = Decimal("0")

        for account in accounts:
            balance = await self._get_account_period_balance(account.id, period)

            if account.account_type == AccountType.REVENUE:
                total_revenue += balance
            else:
                total_expenses += balance

        return {
            "accounts_processed": len(accounts),
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "period_result": total_revenue - total_expenses,
        }

    async def _transfer_result_to_equity(
        self,
        period: AccountingPeriod,
        result: ClosingResult,
        user_id: UUID | None,  # pylint: disable=unused-argument
    ) -> dict:
        """Transfere resultado do período para o PL."""
        # Calcula resultado
        closing_data = await self._close_result_accounts(period, user_id)

        result.total_revenue = closing_data["total_revenue"]
        result.total_expenses = closing_data["total_expenses"]
        result.period_result = closing_data["period_result"]

        return {
            "result_transferred": result.period_result,
            "is_profit": result.period_result > Decimal("0"),
        }

    async def _finalize_closing(
        self,
        period: AccountingPeriod,
        closing_type: ClosingType,
        user_id: UUID | None,
    ) -> dict:
        """Finaliza o fechamento do período."""
        # Atualiza status do período
        period.status = PeriodStatus.CLOSED
        period.closing_type = closing_type
        period.closing_date = datetime.utcnow()
        period.closed_by = user_id
        period.allows_entries = False

        await self.session.commit()

        return {
            "period_closed": True,
            "closing_type": closing_type.value,
            "closed_at": period.closing_date.isoformat(),
        }

    async def _get_account_period_balance(
        self,
        account_id: UUID,
        period: AccountingPeriod,
    ) -> Decimal:
        """Obtém saldo de uma conta no período."""
        query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), 0).label("debit"),
                func.coalesce(func.sum(JournalEntryLine.credit_amount), 0).label("credit"),
            )
            .join(JournalEntry)
            .where(
                and_(
                    JournalEntryLine.account_id == account_id,
                    JournalEntry.period_id == period.id,
                    JournalEntry.status == EntryStatus.POSTED,
                )
            )
        )

        result = await self.session.execute(query)
        row = result.one()

        debit = Decimal(str(row.debit))
        credit = Decimal(str(row.credit))

        # Busca natureza da conta
        account_query = select(AccountingAccount.nature).where(AccountingAccount.id == account_id)
        account_result = await self.session.execute(account_query)
        nature = account_result.scalar_one_or_none()

        if nature == AccountNature.DEBIT:
            return debit - credit
        return credit - debit

    async def _calculate_period_totals(self, period: AccountingPeriod) -> dict:
        """Calcula totais do período."""
        # Totais de lançamentos
        entries_query = select(
            func.sum(JournalEntry.total_debit).label("total_debit"),
            func.sum(JournalEntry.total_credit).label("total_credit"),
        ).where(
            and_(
                JournalEntry.period_id == period.id,
                JournalEntry.status == EntryStatus.POSTED,
            )
        )

        result = await self.session.execute(entries_query)
        row = result.one()

        total_debit = Decimal(str(row.total_debit or 0))
        total_credit = Decimal(str(row.total_credit or 0))

        # Receitas e despesas
        closing_data = await self._close_result_accounts(period, None)

        return {
            "total_debit": total_debit,
            "total_credit": total_credit,
            "total_revenue": closing_data["total_revenue"],
            "total_expenses": closing_data["total_expenses"],
        }

    async def _find_duplicate_entries(
        self,
        condominio_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[AuditIssue]:
        """Encontra lançamentos duplicados."""
        issues = []

        # Busca possíveis duplicados por valor e data
        duplicates_query = (
            select(
                JournalEntry.entry_date,
                JournalEntry.total_debit,
                func.count(JournalEntry.id).label("count"),
            )
            .where(
                and_(
                    JournalEntry.condominio_id == condominio_id,
                    JournalEntry.entry_date >= start_date,
                    JournalEntry.entry_date <= end_date,
                    JournalEntry.status == EntryStatus.POSTED,
                )
            )
            .group_by(JournalEntry.entry_date, JournalEntry.total_debit)
            .having(func.count(JournalEntry.id) > 1)
        )

        result = await self.session.execute(duplicates_query)
        duplicates = result.fetchall()

        for dup in duplicates:
            issues.append(
                AuditIssue(
                    issue_type=AuditIssueType.DUPLICATE_ENTRY,
                    severity="WARNING",
                    message=(
                        f"Possível duplicidade: {dup.count} lançamentos de R$ {dup.total_debit} em {dup.entry_date}"
                    ),
                    amount=dup.total_debit,
                )
            )

        return issues

    async def _find_pending_reconciliation(
        self,
        condominio_id: UUID,
        end_date: date,
    ) -> list[AuditIssue]:
        """Encontra lançamentos pendentes de conciliação."""
        issues = []

        # Busca linhas não conciliadas
        pending_query = (
            select(func.count(JournalEntryLine.id))
            .join(JournalEntry)
            .where(
                and_(
                    JournalEntry.condominio_id == condominio_id,
                    JournalEntry.entry_date <= end_date,
                    JournalEntry.status == EntryStatus.POSTED,
                    JournalEntryLine.is_reconciled.is_(False),
                )
            )
        )

        result = await self.session.execute(pending_query)
        count = result.scalar() or 0

        if count > 0:
            issues.append(
                AuditIssue(
                    issue_type=AuditIssueType.RECONCILIATION_PENDING,
                    severity="INFO",
                    message=f"{count} partidas pendentes de conciliação",
                )
            )

        return issues

    async def _generate_entry_number(self, condominio_id: UUID) -> str:
        """Gera número sequencial de lançamento."""
        max_query = select(func.max(JournalEntry.entry_number)).where(JournalEntry.condominio_id == condominio_id)

        result = await self.session.execute(max_query)
        max_number = result.scalar()

        if max_number:
            # Extrai número e incrementa
            try:
                num = int(max_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                num = 1
        else:
            num = 1

        return f"LC-{num:08d}"

    @staticmethod
    def _get_month_name(month: int) -> str:
        """Retorna nome do mês em português."""
        months = [
            "",
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
        ]
        return months[month] if 1 <= month <= 12 else ""
