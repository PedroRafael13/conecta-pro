"""Service para geracao de DRE (Demonstracao do Resultado do Exercicio).

Implementa calculo e geracao de DRE mensal/anual com:
- Agrupamento por contas contabeis
- Comparativo com periodo anterior
- Rateio por centro de custo
- Exportacao para Excel/PDF
"""

import calendar
import logging
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.accounting_account import (
    AccountingAccount,
    AccountType,
)
from modules.financial.models.cost_center import CostCenter
from modules.financial.models.journal_entry import (
    EntryStatus,
    JournalEntry,
    JournalEntryLine,
)

logger = logging.getLogger(__name__)


class DREPeriodType(StrEnum):
    """Tipo de periodo do DRE."""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMIANNUAL = "semiannual"
    ANNUAL = "annual"
    CUSTOM = "custom"


class DREGroupType(StrEnum):
    """Tipos de grupos do DRE."""

    RECEITA_BRUTA = "receita_bruta"
    DEDUCOES = "deducoes"
    RECEITA_LIQUIDA = "receita_liquida"
    CUSTO_PRODUTOS = "custo_produtos"
    CUSTO_SERVICOS = "custo_servicos"
    LUCRO_BRUTO = "lucro_bruto"
    DESPESAS_OPERACIONAIS = "despesas_operacionais"
    DESPESAS_ADMINISTRATIVAS = "despesas_administrativas"
    DESPESAS_COMERCIAIS = "despesas_comerciais"
    DESPESAS_FINANCEIRAS = "despesas_financeiras"
    RECEITAS_FINANCEIRAS = "receitas_financeiras"
    OUTRAS_RECEITAS = "outras_receitas"
    OUTRAS_DESPESAS = "outras_despesas"
    LUCRO_OPERACIONAL = "lucro_operacional"
    RESULTADO_ANTES_IR = "resultado_antes_ir"
    IR_CSLL = "ir_csll"
    LUCRO_LIQUIDO = "lucro_liquido"


@dataclass
class DRELineItem:
    """Representa uma linha do DRE."""

    account_id: UUID | None = None
    account_code: str = ""
    account_name: str = ""
    group_type: DREGroupType | None = None
    level: int = 0
    is_total: bool = False
    current_value: Decimal = Decimal("0")
    previous_value: Decimal = Decimal("0")
    budget_value: Decimal = Decimal("0")
    variation_value: Decimal = Decimal("0")
    variation_percent: Decimal = Decimal("0")
    av_percent: Decimal = Decimal("0")  # Analise Vertical
    ah_percent: Decimal = Decimal("0")  # Analise Horizontal
    cost_center_breakdown: dict[str, Decimal] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Converte para dicionario."""
        return {
            "account_id": str(self.account_id) if self.account_id else None,
            "account_code": self.account_code,
            "account_name": self.account_name,
            "group_type": self.group_type.value if self.group_type else None,
            "level": self.level,
            "is_total": self.is_total,
            "current_value": float(self.current_value),
            "previous_value": float(self.previous_value),
            "budget_value": float(self.budget_value),
            "variation_value": float(self.variation_value),
            "variation_percent": float(self.variation_percent),
            "av_percent": float(self.av_percent),
            "ah_percent": float(self.ah_percent),
            "cost_center_breakdown": {k: float(v) for k, v in self.cost_center_breakdown.items()},
        }


@dataclass
class DREReport:
    """Representa um relatorio DRE completo."""

    condominio_id: UUID
    period_type: DREPeriodType
    start_date: date
    end_date: date
    previous_start_date: date | None = None
    previous_end_date: date | None = None
    lines: list[DRELineItem] = field(default_factory=list)
    totals: dict[str, Decimal] = field(default_factory=dict)
    cost_centers: list[dict] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        """Converte para dicionario."""
        return {
            "condominio_id": str(self.condominio_id),
            "period_type": self.period_type.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "previous_start_date": (self.previous_start_date.isoformat() if self.previous_start_date else None),
            "previous_end_date": (self.previous_end_date.isoformat() if self.previous_end_date else None),
            "lines": [line.to_dict() for line in self.lines],
            "totals": {k: float(v) for k, v in self.totals.items()},
            "cost_centers": self.cost_centers,
            "generated_at": self.generated_at.isoformat(),
        }


# Mapeamento de tipos de conta para grupos DRE
ACCOUNT_TYPE_TO_DRE_GROUP: dict[AccountType, DREGroupType] = {
    AccountType.REVENUE: DREGroupType.RECEITA_BRUTA,
    AccountType.COST: DREGroupType.CUSTO_PRODUTOS,
    AccountType.EXPENSE: DREGroupType.DESPESAS_OPERACIONAIS,
}


class DREService:
    """Service para geracao de DRE.

    Calcula e gera Demonstracao do Resultado do Exercicio
    com comparativos, analises vertical/horizontal e
    rateio por centro de custo.
    """

    def __init__(self, session: AsyncSession):
        """Inicializa o service.

        Args:
            session: Sessao do banco de dados.
        """
        self.session = session

    async def generate_dre(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        start_date: date,
        end_date: date,
        include_previous: bool = True,
        _include_budget: bool = False,  # pylint: disable=unused-argument
        cost_center_ids: list[UUID] | None = None,
    ) -> DREReport:
        """Gera DRE para o periodo especificado.

        Args:
            condominio_id: ID do condominio.
            start_date: Data inicial do periodo.
            end_date: Data final do periodo.
            include_previous: Incluir periodo anterior para comparativo.
            include_budget: Incluir valores orcados.
            cost_center_ids: Filtrar por centros de custo especificos.

        Returns:
            Relatorio DRE completo.
        """
        logger.info(
            "Gerando DRE",
            extra={
                "condominio_id": str(condominio_id),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )

        # Calcula periodo anterior
        previous_start = None
        previous_end = None
        if include_previous:
            days_diff = (end_date - start_date).days + 1
            previous_end = start_date - timedelta(days=1)
            previous_start = previous_end - timedelta(days=days_diff - 1)

        # Determina tipo de periodo
        period_type = self._determine_period_type(start_date, end_date)

        # Busca contas de resultado
        accounts = await self._get_result_accounts(condominio_id)

        # Busca lancamentos do periodo atual
        current_balances = await self._get_period_balances(
            condominio_id=condominio_id,
            start_date=start_date,
            end_date=end_date,
            cost_center_ids=cost_center_ids,
        )

        # Busca lancamentos do periodo anterior
        previous_balances: dict[UUID, Decimal] = {}
        if include_previous and previous_start and previous_end:
            previous_balances = await self._get_period_balances(
                condominio_id=condominio_id,
                start_date=previous_start,
                end_date=previous_end,
                cost_center_ids=cost_center_ids,
            )

        # Busca breakdown por centro de custo
        cost_center_breakdown = await self._get_cost_center_breakdown(
            condominio_id=condominio_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Monta linhas do DRE
        lines = self._build_dre_lines(
            accounts=accounts,
            current_balances=current_balances,
            previous_balances=previous_balances,
            cost_center_breakdown=cost_center_breakdown,
        )

        # Calcula totais
        totals = self._calculate_totals(lines)

        # Calcula analises vertical e horizontal
        self._calculate_analysis(lines, totals)

        # Busca lista de centros de custo
        cost_centers = await self._get_cost_centers(condominio_id)

        return DREReport(
            condominio_id=condominio_id,
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
            previous_start_date=previous_start,
            previous_end_date=previous_end,
            lines=lines,
            totals=totals,
            cost_centers=cost_centers,
        )

    def _determine_period_type(self, start_date: date, end_date: date) -> DREPeriodType:
        """Determina o tipo de periodo baseado nas datas."""
        days = (end_date - start_date).days + 1

        if days <= 31:
            return DREPeriodType.MONTHLY
        if days <= 92:
            return DREPeriodType.QUARTERLY
        if days <= 184:
            return DREPeriodType.SEMIANNUAL
        if days <= 366:
            return DREPeriodType.ANNUAL
        return DREPeriodType.CUSTOM

    async def _get_result_accounts(
        self,
        condominio_id: UUID,
    ) -> list[AccountingAccount]:
        """Busca contas de resultado (Receita, Custo, Despesa)."""
        query = (
            select(AccountingAccount)
            .where(
                and_(
                    AccountingAccount.condominio_id == condominio_id,
                    AccountingAccount.active.is_(True),
                    AccountingAccount.account_type.in_(
                        [
                            AccountType.REVENUE,
                            AccountType.COST,
                            AccountType.EXPENSE,
                        ]
                    ),
                )
            )
            .order_by(AccountingAccount.code)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _get_period_balances(
        self,
        condominio_id: UUID,
        start_date: date,
        end_date: date,
        cost_center_ids: list[UUID] | None = None,
    ) -> dict[UUID, Decimal]:
        """Busca saldos das contas no periodo."""
        query = (
            select(
                JournalEntryLine.account_id,
                func.sum(JournalEntryLine.debit_amount).label("total_debit"),
                func.sum(JournalEntryLine.credit_amount).label("total_credit"),
            )
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
            .where(
                and_(
                    JournalEntry.condominio_id == condominio_id,
                    JournalEntry.status == EntryStatus.POSTED,
                    JournalEntry.entry_date >= start_date,
                    JournalEntry.entry_date <= end_date,
                )
            )
            .group_by(JournalEntryLine.account_id)
        )

        if cost_center_ids:
            query = query.where(JournalEntryLine.cost_center_id.in_(cost_center_ids))

        result = await self.session.execute(query)

        balances: dict[UUID, Decimal] = {}
        for row in result:
            debit = Decimal(str(row.total_debit or 0))
            credit = Decimal(str(row.total_credit or 0))
            # Para contas de resultado: Receita = Credito, Despesa/Custo = Debito
            balances[row.account_id] = credit - debit

        return balances

    async def _get_cost_center_breakdown(
        self,
        condominio_id: UUID,
        start_date: date,
        end_date: date,
    ) -> dict[UUID, dict[str, Decimal]]:
        """Busca breakdown por centro de custo."""
        query = (
            select(
                JournalEntryLine.account_id,
                CostCenter.code.label("cc_code"),
                func.sum(JournalEntryLine.debit_amount).label("total_debit"),
                func.sum(JournalEntryLine.credit_amount).label("total_credit"),
            )
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
            .join(CostCenter, CostCenter.id == JournalEntryLine.cost_center_id, isouter=True)
            .where(
                and_(
                    JournalEntry.condominio_id == condominio_id,
                    JournalEntry.status == EntryStatus.POSTED,
                    JournalEntry.entry_date >= start_date,
                    JournalEntry.entry_date <= end_date,
                )
            )
            .group_by(JournalEntryLine.account_id, CostCenter.code)
        )

        result = await self.session.execute(query)

        breakdown: dict[UUID, dict[str, Decimal]] = {}
        for row in result:
            if row.account_id not in breakdown:
                breakdown[row.account_id] = {}

            cc_code = row.cc_code or "SEM_CC"
            debit = Decimal(str(row.total_debit or 0))
            credit = Decimal(str(row.total_credit or 0))
            breakdown[row.account_id][cc_code] = credit - debit

        return breakdown

    async def _get_cost_centers(self, condominio_id: UUID) -> list[dict]:
        """Busca centros de custo do condominio."""
        query = (
            select(CostCenter.id, CostCenter.code, CostCenter.name)
            .where(
                and_(
                    CostCenter.condominio_id == condominio_id,
                    CostCenter.active.is_(True),
                )
            )
            .order_by(CostCenter.code)
        )

        result = await self.session.execute(query)

        return [{"id": str(row.id), "code": row.code, "name": row.name} for row in result]

    def _build_dre_lines(
        self,
        accounts: list[AccountingAccount],
        current_balances: dict[UUID, Decimal],
        previous_balances: dict[UUID, Decimal],
        cost_center_breakdown: dict[UUID, dict[str, Decimal]],
    ) -> list[DRELineItem]:
        """Monta as linhas do DRE."""
        lines: list[DRELineItem] = []

        # Agrupa contas por tipo
        revenue_accounts = [a for a in accounts if a.account_type == AccountType.REVENUE]
        cost_accounts = [a for a in accounts if a.account_type == AccountType.COST]
        expense_accounts = [a for a in accounts if a.account_type == AccountType.EXPENSE]

        # Receita Bruta
        lines.append(
            DRELineItem(
                account_name="RECEITA BRUTA",
                group_type=DREGroupType.RECEITA_BRUTA,
                level=0,
                is_total=True,
            )
        )

        for account in revenue_accounts:
            if account.dre_group == "deducoes":
                continue
            current = current_balances.get(account.id, Decimal("0"))
            previous = previous_balances.get(account.id, Decimal("0"))
            cc_breakdown = cost_center_breakdown.get(account.id, {})

            lines.append(
                DRELineItem(
                    account_id=account.id,
                    account_code=account.code,
                    account_name=account.name,
                    group_type=DREGroupType.RECEITA_BRUTA,
                    level=1,
                    current_value=current,
                    previous_value=previous,
                    cost_center_breakdown=cc_breakdown,
                )
            )

        # Deducoes da Receita
        lines.append(
            DRELineItem(
                account_name="(-) DEDUCOES DA RECEITA",
                group_type=DREGroupType.DEDUCOES,
                level=0,
                is_total=True,
            )
        )

        for account in revenue_accounts:
            if account.dre_group != "deducoes":
                continue
            current = current_balances.get(account.id, Decimal("0"))
            previous = previous_balances.get(account.id, Decimal("0"))

            lines.append(
                DRELineItem(
                    account_id=account.id,
                    account_code=account.code,
                    account_name=account.name,
                    group_type=DREGroupType.DEDUCOES,
                    level=1,
                    current_value=current,
                    previous_value=previous,
                )
            )

        # Custos
        lines.append(
            DRELineItem(
                account_name="(-) CUSTOS DOS PRODUTOS/SERVICOS",
                group_type=DREGroupType.CUSTO_PRODUTOS,
                level=0,
                is_total=True,
            )
        )

        for account in cost_accounts:
            current = current_balances.get(account.id, Decimal("0"))
            previous = previous_balances.get(account.id, Decimal("0"))
            cc_breakdown = cost_center_breakdown.get(account.id, {})

            lines.append(
                DRELineItem(
                    account_id=account.id,
                    account_code=account.code,
                    account_name=account.name,
                    group_type=DREGroupType.CUSTO_PRODUTOS,
                    level=1,
                    current_value=abs(current),  # Custo e positivo no DRE
                    previous_value=abs(previous),
                    cost_center_breakdown=cc_breakdown,
                )
            )

        # Lucro Bruto (calculado)
        lines.append(
            DRELineItem(
                account_name="LUCRO BRUTO",
                group_type=DREGroupType.LUCRO_BRUTO,
                level=0,
                is_total=True,
            )
        )

        # Despesas Operacionais
        lines.append(
            DRELineItem(
                account_name="(-) DESPESAS OPERACIONAIS",
                group_type=DREGroupType.DESPESAS_OPERACIONAIS,
                level=0,
                is_total=True,
            )
        )

        for account in expense_accounts:
            current = current_balances.get(account.id, Decimal("0"))
            previous = previous_balances.get(account.id, Decimal("0"))
            cc_breakdown = cost_center_breakdown.get(account.id, {})

            lines.append(
                DRELineItem(
                    account_id=account.id,
                    account_code=account.code,
                    account_name=account.name,
                    group_type=DREGroupType.DESPESAS_OPERACIONAIS,
                    level=1,
                    current_value=abs(current),
                    previous_value=abs(previous),
                    cost_center_breakdown=cc_breakdown,
                )
            )

        # Lucro Liquido (calculado)
        lines.append(
            DRELineItem(
                account_name="LUCRO/PREJUIZO LIQUIDO",
                group_type=DREGroupType.LUCRO_LIQUIDO,
                level=0,
                is_total=True,
            )
        )

        return lines

    def _calculate_totals(  # pylint: disable=too-many-branches
        self,
        lines: list[DRELineItem],
    ) -> dict[str, Decimal]:
        """Calcula os totais do DRE."""
        totals: dict[str, Decimal] = {
            "receita_bruta": Decimal("0"),
            "deducoes": Decimal("0"),
            "receita_liquida": Decimal("0"),
            "custos": Decimal("0"),
            "lucro_bruto": Decimal("0"),
            "despesas": Decimal("0"),
            "lucro_liquido": Decimal("0"),
        }

        for line in lines:
            if line.is_total or not line.group_type:
                continue

            if line.group_type == DREGroupType.RECEITA_BRUTA:
                totals["receita_bruta"] += line.current_value
            elif line.group_type == DREGroupType.DEDUCOES:
                totals["deducoes"] += line.current_value
            elif line.group_type == DREGroupType.CUSTO_PRODUTOS:
                totals["custos"] += line.current_value
            elif line.group_type == DREGroupType.DESPESAS_OPERACIONAIS:
                totals["despesas"] += line.current_value

        # Calcula totais derivados
        totals["receita_liquida"] = totals["receita_bruta"] - totals["deducoes"]
        totals["lucro_bruto"] = totals["receita_liquida"] - totals["custos"]
        totals["lucro_liquido"] = totals["lucro_bruto"] - totals["despesas"]

        # Atualiza linhas de total
        for line in lines:
            if not line.is_total:
                continue

            if line.group_type == DREGroupType.RECEITA_BRUTA:
                line.current_value = totals["receita_bruta"]
            elif line.group_type == DREGroupType.DEDUCOES:
                line.current_value = totals["deducoes"]
            elif line.group_type == DREGroupType.CUSTO_PRODUTOS:
                line.current_value = totals["custos"]
            elif line.group_type == DREGroupType.LUCRO_BRUTO:
                line.current_value = totals["lucro_bruto"]
            elif line.group_type == DREGroupType.DESPESAS_OPERACIONAIS:
                line.current_value = totals["despesas"]
            elif line.group_type == DREGroupType.LUCRO_LIQUIDO:
                line.current_value = totals["lucro_liquido"]

        return totals

    def _calculate_analysis(
        self,
        lines: list[DRELineItem],
        totals: dict[str, Decimal],
    ) -> None:
        """Calcula analises vertical e horizontal."""
        receita_liquida = totals.get("receita_liquida", Decimal("0"))

        for line in lines:
            # Analise Vertical (% sobre receita liquida)
            if receita_liquida != Decimal("0"):
                line.av_percent = (line.current_value / receita_liquida) * Decimal("100")

            # Variacao absoluta e percentual
            line.variation_value = line.current_value - line.previous_value

            if line.previous_value != Decimal("0"):
                line.variation_percent = (line.variation_value / abs(line.previous_value)) * Decimal("100")

            # Analise Horizontal (igual a variacao percentual)
            line.ah_percent = line.variation_percent

    async def get_monthly_comparison(
        self,
        condominio_id: UUID,
        year: int,
        months: int = 12,
    ) -> dict:
        """Gera comparativo mensal do DRE.

        Args:
            condominio_id: ID do condominio.
            year: Ano de referencia.
            months: Quantidade de meses a comparar.

        Returns:
            Dados do comparativo mensal.
        """
        comparison_data: dict[str, list] = {
            "months": [],
            "receita_bruta": [],
            "custos": [],
            "lucro_bruto": [],
            "despesas": [],
            "lucro_liquido": [],
        }

        for month in range(1, min(months + 1, 13)):
            _, last_day = calendar.monthrange(year, month)
            start = date(year, month, 1)
            end = date(year, month, last_day)

            # Gera DRE do mes
            dre = await self.generate_dre(
                condominio_id=condominio_id,
                start_date=start,
                end_date=end,
                include_previous=False,
            )

            comparison_data["months"].append(f"{year}-{month:02d}")
            comparison_data["receita_bruta"].append(float(dre.totals.get("receita_bruta", 0)))
            comparison_data["custos"].append(float(dre.totals.get("custos", 0)))
            comparison_data["lucro_bruto"].append(float(dre.totals.get("lucro_bruto", 0)))
            comparison_data["despesas"].append(float(dre.totals.get("despesas", 0)))
            comparison_data["lucro_liquido"].append(float(dre.totals.get("lucro_liquido", 0)))

        return comparison_data

    async def get_cost_center_dre(
        self,
        condominio_id: UUID,
        cost_center_id: UUID,
        start_date: date,
        end_date: date,
    ) -> DREReport:
        """Gera DRE filtrado por centro de custo.

        Args:
            condominio_id: ID do condominio.
            cost_center_id: ID do centro de custo.
            start_date: Data inicial.
            end_date: Data final.

        Returns:
            Relatorio DRE do centro de custo.
        """
        return await self.generate_dre(
            condominio_id=condominio_id,
            start_date=start_date,
            end_date=end_date,
            cost_center_ids=[cost_center_id],
        )
