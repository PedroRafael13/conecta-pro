"""Service para projeção de fluxo de caixa."""

import logging
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.payable_account import PayableAccount, PayableStatus
from modules.financial.models.payable_category import PayableCategory
from modules.financial.models.payable_installment import InstallmentStatus, PayableInstallment
from modules.financial.models.supplier import Supplier

logger = logging.getLogger(__name__)


class CashFlowProjection:  # pylint: disable=too-few-public-methods
    """Representa uma projeção de fluxo de caixa."""

    def __init__(
        self,
        date: date,  # pylint: disable=redefined-outer-name
        payables: Decimal = Decimal("0"),
        receivables: Decimal = Decimal("0"),
        balance: Decimal = Decimal("0"),
    ):
        """Inicializa a projeção."""
        self.date = date
        self.payables = payables
        self.receivables = receivables
        self.balance = balance
        self.cumulative_balance = Decimal("0")
        self.details: list[dict] = []

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "date": self.date.isoformat(),
            "payables": float(self.payables),
            "receivables": float(self.receivables),
            "balance": float(self.balance),
            "cumulative_balance": float(self.cumulative_balance),
            "details": self.details,
        }


class CashFlowService:
    """Service para projeção e análise de fluxo de caixa."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session

    async def get_projection(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        include_pending: bool = True,  # pylint: disable=unused-argument
        include_scheduled: bool = True,
        group_by: str = "day",  # day, week, month
    ) -> list[CashFlowProjection]:
        """Gera projeção de fluxo de caixa."""
        if start_date is None:
            start_date = date.today()
        if end_date is None:
            end_date = start_date + timedelta(days=90)

        logger.info(f"Gerando projeção de {start_date} a {end_date} para {condominio_id}")

        # Busca parcelas no período
        statuses = [InstallmentStatus.PENDENTE.value]
        if include_scheduled:
            statuses.append(InstallmentStatus.AGENDADA.value)

        query = (
            select(PayableInstallment)
            .join(PayableAccount)
            .where(
                and_(
                    PayableAccount.condominio_id == condominio_id,
                    PayableAccount.ativo.is_(True),
                    PayableInstallment.status.in_(statuses),
                    PayableInstallment.due_date >= start_date,
                    PayableInstallment.due_date <= end_date,
                )
            )
            .order_by(PayableInstallment.due_date)
        )

        result = await self.session.execute(query)
        installments = list(result.scalars().all())

        # Agrupa por data
        projections_map: dict[date, CashFlowProjection] = {}

        for inst in installments:
            proj_date = self._get_grouped_date(inst.due_date, group_by)

            if proj_date not in projections_map:
                projections_map[proj_date] = CashFlowProjection(date=proj_date)

            proj = projections_map[proj_date]
            amount = inst.calculate_current_value()

            proj.payables += amount
            proj.balance -= amount
            proj.details.append(
                {
                    "type": "payable",
                    "installment_id": str(inst.id),
                    "description": inst.description or f"Parcela {inst.installment_number}",
                    "due_date": inst.due_date.isoformat(),
                    "amount": float(amount),
                }
            )

        # Ordena e calcula saldo acumulado
        projections = sorted(projections_map.values(), key=lambda p: p.date)

        # Integrar com contas a receber para calcular receivables (futuro)
        # Por enquanto, considera apenas saídas

        cumulative = Decimal("0")
        for proj in projections:
            cumulative += proj.balance
            proj.cumulative_balance = cumulative

        return projections

    def _get_grouped_date(self, d: date, group_by: str) -> date:
        """Agrupa data conforme período."""
        if group_by == "week":
            # Início da semana (segunda-feira)
            return d - timedelta(days=d.weekday())
        elif group_by == "month":
            # Primeiro dia do mês
            return d.replace(day=1)
        return d

    async def get_summary(  # pylint: disable=too-many-locals
        self,
        condominio_id: UUID,
        period_days: int = 30,
    ) -> dict:
        """Retorna resumo do fluxo de caixa."""
        today = date.today()
        end_date = today + timedelta(days=period_days)

        # Totais de contas a pagar por status
        status_query = (
            select(
                PayableAccount.status,
                func.sum(PayableAccount.net_value).label("total"),
                func.count(PayableAccount.id).label("count"),
            )
            .where(
                and_(
                    PayableAccount.condominio_id == condominio_id,
                    PayableAccount.ativo.is_(True),
                    PayableAccount.due_date <= end_date,
                )
            )
            .group_by(PayableAccount.status)
        )

        status_result = await self.session.execute(status_query)
        status_data = {row.status: {"total": float(row.total or 0), "count": row.count} for row in status_result}

        # Vencidos
        overdue_query = select(
            func.sum(PayableAccount.net_value).label("total"),
            func.count(PayableAccount.id).label("count"),
        ).where(
            and_(
                PayableAccount.condominio_id == condominio_id,
                PayableAccount.ativo.is_(True),
                PayableAccount.status.in_([PayableStatus.PENDENTE.value, PayableStatus.APROVADA.value]),
                PayableAccount.due_date < today,
            )
        )

        overdue_result = await self.session.execute(overdue_query)
        overdue_row = overdue_result.one()

        # A vencer esta semana
        week_end = today + timedelta(days=7)
        week_query = select(
            func.sum(PayableAccount.net_value).label("total"),
            func.count(PayableAccount.id).label("count"),
        ).where(
            and_(
                PayableAccount.condominio_id == condominio_id,
                PayableAccount.ativo.is_(True),
                PayableAccount.status.in_([PayableStatus.PENDENTE.value, PayableStatus.APROVADA.value]),
                PayableAccount.due_date >= today,
                PayableAccount.due_date <= week_end,
            )
        )

        week_result = await self.session.execute(week_query)
        week_row = week_result.one()

        # A vencer este mês
        month_query = select(
            func.sum(PayableAccount.net_value).label("total"),
            func.count(PayableAccount.id).label("count"),
        ).where(
            and_(
                PayableAccount.condominio_id == condominio_id,
                PayableAccount.ativo.is_(True),
                PayableAccount.status.in_([PayableStatus.PENDENTE.value, PayableStatus.APROVADA.value]),
                PayableAccount.due_date >= today,
                PayableAccount.due_date <= end_date,
            )
        )

        month_result = await self.session.execute(month_query)
        month_row = month_result.one()

        return {
            "period_days": period_days,
            "by_status": status_data,
            "overdue": {
                "total": float(overdue_row.total or 0),
                "count": overdue_row.count or 0,
            },
            "due_this_week": {
                "total": float(week_row.total or 0),
                "count": week_row.count or 0,
            },
            "due_this_month": {
                "total": float(month_row.total or 0),
                "count": month_row.count or 0,
            },
        }

    async def get_category_breakdown(
        self,
        condominio_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict]:
        """Retorna breakdown por categoria."""
        if start_date is None:
            start_date = date.today().replace(day=1)
        if end_date is None:
            end_date = date.today()

        query = (
            select(
                PayableCategory.id,
                PayableCategory.name,
                func.sum(PayableAccount.net_value).label("total"),
                func.count(PayableAccount.id).label("count"),
            )
            .join(PayableAccount, PayableAccount.category_id == PayableCategory.id)
            .where(
                and_(
                    PayableAccount.condominio_id == condominio_id,
                    PayableAccount.ativo.is_(True),
                    PayableAccount.due_date >= start_date,
                    PayableAccount.due_date <= end_date,
                )
            )
            .group_by(PayableCategory.id, PayableCategory.name)
            .order_by(func.sum(PayableAccount.net_value).desc())
        )

        result = await self.session.execute(query)

        return [
            {
                "category_id": str(row.id),
                "name": row.name,
                "full_name": row.name,
                "total": float(row.total or 0),
                "count": row.count,
            }
            for row in result
        ]

    async def get_supplier_breakdown(
        self,
        condominio_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Retorna breakdown por fornecedor."""
        if start_date is None:
            start_date = date.today().replace(day=1)
        if end_date is None:
            end_date = date.today()

        query = (
            select(
                Supplier.id,
                Supplier.name,
                Supplier.trade_name,
                func.sum(PayableAccount.net_value).label("total"),
                func.count(PayableAccount.id).label("count"),
            )
            .join(PayableAccount, PayableAccount.supplier_id == Supplier.id)
            .where(
                and_(
                    PayableAccount.condominio_id == condominio_id,
                    PayableAccount.ativo.is_(True),
                    PayableAccount.due_date >= start_date,
                    PayableAccount.due_date <= end_date,
                )
            )
            .group_by(Supplier.id, Supplier.name, Supplier.trade_name)
            .order_by(func.sum(PayableAccount.net_value).desc())
            .limit(limit)
        )

        result = await self.session.execute(query)

        return [
            {
                "supplier_id": str(row.id),
                "name": row.name,
                "trade_name": row.trade_name,
                "total": float(row.total or 0),
                "count": row.count,
            }
            for row in result
        ]

    async def get_monthly_trend(
        self,
        condominio_id: UUID,
        months: int = 12,
    ) -> list[dict]:
        """Retorna tendência mensal de pagamentos."""
        today = date.today()
        start_date = (today.replace(day=1) - timedelta(days=months * 30)).replace(day=1)

        query = (
            select(
                func.date_trunc(text("'month'"), PayableAccount.due_date).label("month"),
                func.sum(PayableAccount.net_value).label("total"),
                func.sum(PayableAccount.paid_value).label("paid"),
                func.count(PayableAccount.id).label("count"),
            )
            .where(
                and_(
                    PayableAccount.condominio_id == condominio_id,
                    PayableAccount.ativo.is_(True),
                    PayableAccount.due_date >= start_date,
                    PayableAccount.due_date <= today,
                )
            )
            .group_by(text("1"))
            .order_by(text("1"))
        )

        result = await self.session.execute(query)

        return [
            {
                "month": row.month.isoformat() if row.month else None,
                "total": float(row.total or 0),
                "paid": float(row.paid or 0),
                "count": row.count,
            }
            for row in result
        ]
