"""Repository para contracheques/holerites."""

import logging
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.employee_portal.models import PaySlip, PaySlipStatus, PaySlipType
from modules.hr.employee_portal.schemas import PaySlipCreate, PaySlipUpdate

logger = logging.getLogger(__name__)


class PaySlipRepository:
    """Repository para operações de contracheques."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: PaySlipCreate,
        condominio_id: UUID,
        *,
        created_by: UUID | None = None,
    ) -> PaySlip:
        """Cria novo contracheque."""
        payslip = PaySlip(
            id=uuid4(),
            condominio_id=condominio_id,
            employee_id=data.employee_id,
            period_id=data.period_id,
            payslip_code=self._generate_code(data.reference_year, data.reference_month),
            payslip_type=data.payslip_type.value,
            status=PaySlipStatus.DRAFT.value,
            reference_month=data.reference_month,
            reference_year=data.reference_year,
            payment_date=data.payment_date,
            employee_name=data.employee_name,
            employee_cpf=data.employee_cpf,
            employee_position=data.employee_position,
            employee_department=data.employee_department,
            employee_admission_date=data.employee_admission_date,
            gross_salary=data.gross_salary,
            total_earnings=data.total_earnings,
            total_deductions=data.total_deductions,
            net_salary=data.net_salary,
            inss_base=data.inss_base,
            irrf_base=data.irrf_base,
            fgts_base=data.fgts_base,
            inss_value=data.inss_value,
            irrf_value=data.irrf_value,
            fgts_value=data.fgts_value,
            fgts_deposit=data.fgts_deposit,
            earnings=[e.model_dump() for e in data.earnings],
            deductions=[d.model_dump() for d in data.deductions],
            worked_days=data.worked_days,
            worked_hours=data.worked_hours,
            overtime_hours_50=data.overtime_hours_50,
            overtime_hours_100=data.overtime_hours_100,
            night_hours=data.night_hours,
            absence_days=data.absence_days,
            absence_hours=data.absence_hours,
            dependents_count=data.dependents_count,
            dependents_irrf_deduction=data.dependents_irrf_deduction,
            created_by=created_by,
        )

        self.db.add(payslip)
        await self.db.commit()
        await self.db.refresh(payslip)

        logger.info("Contracheque %s criado para funcionário %s", payslip.id, data.employee_id)
        return payslip

    def _generate_code(self, year: int, month: int) -> str:
        """Gera código único do contracheque."""
        # pylint: disable=import-outside-toplevel
        import random
        import string

        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))  # noqa: S311
        return f"HL{year}{month:02d}{suffix}"

    async def get_by_id(self, payslip_id: UUID) -> PaySlip | None:
        """Busca contracheque por ID."""
        result = await self.db.execute(select(PaySlip).where(PaySlip.id == payslip_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> PaySlip | None:
        """Busca contracheque por código."""
        result = await self.db.execute(select(PaySlip).where(PaySlip.payslip_code == code))
        return result.scalar_one_or_none()

    async def list_by_employee(
        self,
        employee_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        status: PaySlipStatus | None = None,
        payslip_type: PaySlipType | None = None,
        year: int | None = None,
        only_viewable: bool = True,
    ) -> tuple[list[PaySlip], int]:
        """Lista contracheques por funcionário."""
        query = select(PaySlip).where(PaySlip.employee_id == employee_id)

        if only_viewable:
            query = query.where(
                PaySlip.status.in_(
                    [
                        PaySlipStatus.PUBLISHED.value,
                        PaySlipStatus.RECTIFIED.value,
                    ]
                )
            )
        elif status:
            query = query.where(PaySlip.status == status.value)

        if payslip_type:
            query = query.where(PaySlip.payslip_type == payslip_type.value)

        if year:
            query = query.where(PaySlip.reference_year == year)

        # Total
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        # Paginação
        query = query.order_by(
            desc(PaySlip.reference_year),
            desc(PaySlip.reference_month),
            desc(PaySlip.created_at),
        )
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def list_by_condominio(
        self,
        condominio_id: UUID,
        *,
        page: int = 1,
        page_size: int = 50,
        status: PaySlipStatus | None = None,
        year: int | None = None,
        month: int | None = None,
    ) -> tuple[list[PaySlip], int]:
        """Lista contracheques por condomínio."""
        query = select(PaySlip).where(PaySlip.condominio_id == condominio_id)

        if status:
            query = query.where(PaySlip.status == status.value)

        if year:
            query = query.where(PaySlip.reference_year == year)

        if month:
            query = query.where(PaySlip.reference_month == month)

        # Total
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        # Paginação
        query = query.order_by(desc(PaySlip.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def update(
        self,
        payslip_id: UUID,
        data: PaySlipUpdate,
    ) -> PaySlip | None:
        """Atualiza contracheque."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "earnings" and value is not None:
                value = [e.model_dump() for e in value]
            elif field == "deductions" and value is not None:
                value = [d.model_dump() for d in value]
            setattr(payslip, field, value)

        payslip.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(payslip)

        return payslip

    async def publish(
        self,
        payslip_id: UUID,
        *,
        published_by: UUID | None = None,
    ) -> PaySlip | None:
        """Publica contracheque (visível para funcionário)."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        payslip.status = PaySlipStatus.PUBLISHED.value
        payslip.published_at = datetime.utcnow()
        payslip.published_by = published_by

        await self.db.commit()
        await self.db.refresh(payslip)

        logger.info("Contracheque %s publicado", payslip_id)
        return payslip

    async def record_view(self, payslip_id: UUID) -> PaySlip | None:
        """Registra visualização do contracheque."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        payslip.record_view()
        await self.db.commit()
        await self.db.refresh(payslip)

        return payslip

    async def record_download(self, payslip_id: UUID) -> PaySlip | None:
        """Registra download do contracheque."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        payslip.record_download()
        await self.db.commit()
        await self.db.refresh(payslip)

        return payslip

    async def acknowledge(
        self,
        payslip_id: UUID,
    ) -> PaySlip | None:
        """Registra ciência do contracheque."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        if payslip.acknowledged_at:
            return payslip  # Já deu ciência

        payslip.acknowledged_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(payslip)

        logger.info("Ciência registrada para contracheque %s", payslip_id)
        return payslip

    async def contest(
        self,
        payslip_id: UUID,
        reason: str,
    ) -> PaySlip | None:
        """Registra contestação do contracheque."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        if not payslip.can_contest:
            raise ValueError("Contracheque não pode ser contestado")

        payslip.contested = True
        payslip.contest_reason = reason
        payslip.contest_date = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(payslip)

        logger.info("Contestação registrada para contracheque %s", payslip_id)
        return payslip

    async def resolve_contest(
        self,
        payslip_id: UUID,
        resolution: str,
        *,
        resolved_by: UUID | None = None,  # pylint: disable=unused-argument
    ) -> PaySlip | None:
        """Resolve contestação do contracheque."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        payslip.contest_resolved = True
        payslip.contest_resolution = resolution

        await self.db.commit()
        await self.db.refresh(payslip)

        logger.info("Contestação resolvida para contracheque %s", payslip_id)
        return payslip

    async def get_unread_count(self, employee_id: UUID) -> int:
        """Conta contracheques não visualizados."""
        result = await self.db.execute(
            select(func.count(PaySlip.id)).where(
                and_(
                    PaySlip.employee_id == employee_id,
                    PaySlip.status == PaySlipStatus.PUBLISHED.value,
                    PaySlip.first_viewed_at.is_(None),
                )
            )
        )
        return result.scalar() or 0

    async def get_pending_ack_count(self, employee_id: UUID) -> int:
        """Conta contracheques pendentes de ciência."""
        result = await self.db.execute(
            select(func.count(PaySlip.id)).where(
                and_(
                    PaySlip.employee_id == employee_id,
                    PaySlip.status == PaySlipStatus.PUBLISHED.value,
                    PaySlip.acknowledged_at.is_(None),
                )
            )
        )
        return result.scalar() or 0

    async def get_years_available(self, employee_id: UUID) -> list[int]:
        """Retorna anos disponíveis para o funcionário."""
        result = await self.db.execute(
            select(PaySlip.reference_year)
            .where(
                and_(
                    PaySlip.employee_id == employee_id,
                    PaySlip.status == PaySlipStatus.PUBLISHED.value,
                )
            )
            .distinct()
            .order_by(desc(PaySlip.reference_year))
        )
        return list(result.scalars().all())
