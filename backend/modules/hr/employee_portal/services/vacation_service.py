"""Service para férias."""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.employee_portal.models import (
    VacationRequest,
    VacationStatus,
)
from modules.hr.employee_portal.repositories import (
    VacationPeriodRepository,
    VacationRequestRepository,
)
from modules.hr.employee_portal.schemas import (
    VacationRequestCreate,
    VacationCalculationRequest,
    VacationCalculationResponse,
    VacationBalanceResponse,
    VacationPeriodSummary,
)

logger = logging.getLogger(__name__)


class VacationService:
    """Service para operações de férias."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.period_repo = VacationPeriodRepository(db)
        self.request_repo = VacationRequestRepository(db)

    async def get_vacation_balance(  # pylint: disable=too-many-locals
        self,
        employee_id: UUID,
    ) -> VacationBalanceResponse:
        """Retorna saldo de férias do funcionário."""
        periods = await self.period_repo.list_by_employee(
            employee_id,
            include_expired=False,
            include_fully_used=False,
        )

        total_available = sum(p.days_remaining for p in periods)
        total_used = sum(p.days_used for p in periods)
        total_sold = sum(p.days_sold for p in periods)
        total_remaining = sum(p.days_remaining for p in periods)

        # Buscar solicitações pendentes
        requests, _ = await self.request_repo.list_by_employee(
            employee_id,
            status=VacationStatus.PENDING,
        )

        period_summaries = [
            VacationPeriodSummary(
                id=p.id,
                start_date=p.start_date,
                end_date=p.end_date,
                days_remaining=p.days_remaining,
                days_until_expiration=p.days_until_expiration,
                is_expired=p.is_expired,
            )
            for p in periods
        ]

        # Verificar período expirando
        has_expiring = any(p.days_until_expiration <= 60 for p in periods)
        next_expiration = min(
            (p.days_until_expiration for p in periods if p.days_until_expiration > 0),
            default=None,
        )

        return VacationBalanceResponse(
            employee_id=employee_id,
            periods=period_summaries,
            total_days_available=total_available,
            total_days_used=total_used,
            total_days_sold=total_sold,
            total_days_remaining=total_remaining,
            pending_requests_count=len(requests),
            next_period_start=None,  # Calculado baseado em admissão
            has_expiring_period=has_expiring,
            days_until_next_expiration=next_expiration,
        )

    async def create_vacation_request(
        self,
        data: VacationRequestCreate,
        condominio_id: UUID,
        employee_id: UUID,
    ) -> VacationRequest:
        """Cria solicitação de férias."""
        # Verificar conflito de datas
        has_conflict = await self.request_repo.check_date_conflict(
            employee_id,
            data.start_date,
            data.end_date,
        )

        if has_conflict:
            raise ValueError("Já existe solicitação para este período")

        # Verificar saldo
        total_days = data.days_requested + data.sell_days
        available = await self.period_repo.get_available_days(employee_id)

        if total_days > available:
            raise ValueError(
                f"Dias solicitados ({total_days}) excedem saldo ({available})"
            )

        # Verificar prazo mínimo (30 dias antes)
        days_until = (data.start_date - date.today()).days
        if days_until < 30:
            logger.warning(
                "Solicitação com menos de 30 dias de antecedência: %d dias",
                days_until,
            )

        request = await self.request_repo.create(
            data,
            condominio_id,
            created_by=employee_id,
        )

        # Atualizar employee_id corretamente
        request.employee_id = employee_id
        await self.db.commit()
        await self.db.refresh(request)

        return request

    async def submit_request(
        self,
        request_id: UUID,
        employee_id: UUID,
    ) -> VacationRequest:
        """Submete solicitação para aprovação."""
        request = await self.request_repo.get_by_id(request_id)
        if not request or request.employee_id != employee_id:
            raise ValueError("Solicitação não encontrada")

        return await self.request_repo.submit(request_id)

    async def calculate_vacation(  # pylint: disable=too-many-locals
        self,
        data: VacationCalculationRequest,
        base_salary: Decimal,
    ) -> VacationCalculationResponse:
        """Calcula valores de férias."""
        # Valor diário
        daily_rate = base_salary / Decimal("30")

        # Valor dos dias de férias
        vacation_days_value = daily_rate * data.days_requested

        # 1/3 constitucional
        vacation_bonus = vacation_days_value / Decimal("3")

        # Abono pecuniário (venda)
        sell_value = daily_rate * data.sell_days
        sell_bonus = sell_value / Decimal("3")
        total_sell = sell_value + sell_bonus

        # Adiantamento 13º (50% do salário)
        advance_13th = (base_salary / Decimal("2")) if data.advance_13th else Decimal("0")

        # Total bruto
        gross_total = vacation_days_value + vacation_bonus + total_sell + advance_13th

        # INSS (simplificado - usar tabela real em produção)
        inss_base = vacation_days_value + vacation_bonus
        inss_value = self._calculate_inss(inss_base)

        # IRRF (simplificado)
        irrf_base = inss_base - inss_value
        irrf_value = self._calculate_irrf(irrf_base)

        # Líquido
        net_total = gross_total - inss_value - irrf_value

        # Datas
        payment_date = data.start_date - timedelta(days=2)
        return_date = data.start_date + timedelta(days=data.days_requested)

        return VacationCalculationResponse(
            base_salary=base_salary,
            daily_rate=daily_rate,
            vacation_days_value=vacation_days_value,
            vacation_bonus=vacation_bonus,
            sell_value=total_sell,
            advance_13th_value=advance_13th,
            gross_total=gross_total,
            inss_base=inss_base,
            inss_value=inss_value,
            irrf_base=irrf_base,
            irrf_value=irrf_value,
            other_deductions=Decimal("0"),
            net_total=net_total,
            payment_date=payment_date,
            return_date=return_date,
            calculation_details={
                "days_requested": data.days_requested,
                "sell_days": data.sell_days,
                "advance_13th": data.advance_13th,
            },
        )

    def _calculate_inss(self, base: Decimal) -> Decimal:  # pylint: disable=too-many-return-statements
        """Calcula INSS progressivo (simplificado)."""
        # Tabela 2024 simplificada
        if base <= Decimal("1412"):
            return base * Decimal("0.075")
        if base <= Decimal("2666.68"):
            return base * Decimal("0.09") - Decimal("21.18")
        if base <= Decimal("4000.03"):
            return base * Decimal("0.12") - Decimal("101.18")
        if base <= Decimal("7786.02"):
            return base * Decimal("0.14") - Decimal("181.18")
        return Decimal("908.85")

    def _calculate_irrf(self, base: Decimal) -> Decimal:  # pylint: disable=too-many-return-statements
        """Calcula IRRF (simplificado)."""
        if base <= Decimal("2259.20"):
            return Decimal("0")
        if base <= Decimal("2826.65"):
            return base * Decimal("0.075") - Decimal("169.44")
        if base <= Decimal("3751.05"):
            return base * Decimal("0.15") - Decimal("381.44")
        if base <= Decimal("4664.68"):
            return base * Decimal("0.225") - Decimal("662.77")
        return base * Decimal("0.275") - Decimal("896.00")

    async def approve_vacation(
        self,
        request_id: UUID,
        approved_by: UUID,
        *,
        level: str = "manager",
        approved: bool = True,
        notes: Optional[str] = None,
        rejection_reason: Optional[str] = None,
    ) -> VacationRequest:
        """Aprova ou rejeita férias."""
        if level == "manager":
            return await self.request_repo.approve_manager(
                request_id,
                approved,
                approved_by=approved_by,
                notes=notes,
                rejection_reason=rejection_reason,
            )
        return await self.request_repo.approve_hr(
            request_id,
            approved,
            approved_by=approved_by,
            notes=notes,
            rejection_reason=rejection_reason,
        )

    async def cancel_vacation(
        self,
        request_id: UUID,
        employee_id: UUID,
        reason: str,
    ) -> VacationRequest:
        """Cancela solicitação de férias."""
        request = await self.request_repo.get_by_id(request_id)
        if not request or request.employee_id != employee_id:
            raise ValueError("Solicitação não encontrada")

        return await self.request_repo.cancel(
            request_id,
            reason,
            cancelled_by=employee_id,
        )

    async def get_pending_approvals(
        self,
        condominio_id: UUID,
        *,
        manager_level: bool = True,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[VacationRequest], int]:
        """Lista solicitações pendentes de aprovação."""
        return await self.request_repo.list_pending_approval(
            condominio_id,
            manager_level=manager_level,
            page=page,
            page_size=page_size,
        )

    async def get_upcoming_vacations(
        self,
        condominio_id: UUID,
        days_ahead: int = 30,
    ) -> List[VacationRequest]:
        """Retorna férias programadas."""
        return await self.request_repo.get_upcoming(condominio_id, days_ahead)
