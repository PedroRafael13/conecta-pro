"""Repository para contracheques/holerites.

Acessa a tabela hr_payslips (migration sprint21_001).
"""

import logging
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.employee_portal.models import PaySlip, PaySlipStatus

logger = logging.getLogger(__name__)


class PaySlipRepository:
    """Repository para operações de contracheques."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    async def get_by_id(self, payslip_id: UUID) -> PaySlip | None:
        """Busca contracheque por ID."""
        result = await self.db.execute(select(PaySlip).where(PaySlip.id == payslip_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> PaySlip | None:
        """Busca contracheque por código."""
        result = await self.db.execute(select(PaySlip).where(PaySlip.payslip_code == code))
        return result.scalar_one_or_none()

    async def get_by_employee_month_year(
        self,
        employee_id: UUID,
        month: int,
        year: int,
    ) -> PaySlip | None:
        """Busca contracheque específico por funcionário/mês/ano (apenas publicados)."""
        result = await self.db.execute(
            select(PaySlip).where(
                and_(
                    PaySlip.employee_id == employee_id,
                    PaySlip.reference_month == month,
                    PaySlip.reference_year == year,
                    PaySlip.status.in_([PaySlipStatus.PUBLISHED.value, PaySlipStatus.RECTIFIED.value]),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_latest(self, employee_id: UUID) -> PaySlip | None:
        """Retorna o contracheque mais recente publicado."""
        result = await self.db.execute(
            select(PaySlip)
            .where(
                and_(
                    PaySlip.employee_id == employee_id,
                    PaySlip.status.in_([PaySlipStatus.PUBLISHED.value, PaySlipStatus.RECTIFIED.value]),
                )
            )
            .order_by(
                desc(PaySlip.reference_year),
                desc(PaySlip.reference_month),
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_by_employee(
        self,
        employee_id: UUID,
        *,
        year: int | None = None,
        page: int = 1,
        page_size: int = 24,
        only_viewable: bool = True,
    ) -> tuple[list[PaySlip], int]:
        """Lista contracheques por funcionário.

        Args:
            employee_id: UUID do funcionário.
            year: Filtrar por ano (opcional).
            page: Página (começa em 1).
            page_size: Tamanho da página.
            only_viewable: Se True, retorna apenas publicados/retificados.

        Returns:
            Tupla (lista de contracheques, total).
        """
        query = select(PaySlip).where(PaySlip.employee_id == employee_id)

        if only_viewable:
            query = query.where(PaySlip.status.in_([PaySlipStatus.PUBLISHED.value, PaySlipStatus.RECTIFIED.value]))

        if year:
            query = query.where(PaySlip.reference_year == year)

        # Total
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        # Paginação
        query = query.order_by(
            desc(PaySlip.reference_year),
            desc(PaySlip.reference_month),
        )
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def list_by_condominio(
        self,
        condominio_id: UUID,
        *,
        employee_id: UUID | None = None,
        year: int | None = None,
        month: int | None = None,
        status: PaySlipStatus | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[PaySlip], int]:
        """Lista contracheques por condomínio (uso administrativo DP)."""
        query = select(PaySlip).where(PaySlip.condominio_id == condominio_id)

        if employee_id:
            query = query.where(PaySlip.employee_id == employee_id)

        if year:
            query = query.where(PaySlip.reference_year == year)

        if month:
            query = query.where(PaySlip.reference_month == month)

        if status:
            query = query.where(PaySlip.status == status.value)

        # Total
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        # Paginação
        query = query.order_by(desc(PaySlip.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def get_years_available(self, employee_id: UUID) -> list[int]:
        """Retorna anos com contracheques disponíveis para o funcionário."""
        result = await self.db.execute(
            select(PaySlip.reference_year)
            .where(
                and_(
                    PaySlip.employee_id == employee_id,
                    PaySlip.status.in_([PaySlipStatus.PUBLISHED.value, PaySlipStatus.RECTIFIED.value]),
                )
            )
            .distinct()
            .order_by(desc(PaySlip.reference_year))
        )
        return list(result.scalars().all())

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

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    async def create(
        self,
        *,
        condominio_id: UUID,
        employee_id: UUID,
        payslip_type: str = "monthly",
        reference_month: int,
        reference_year: int,
        base_salary: float,
        total_earnings: float,
        total_deductions: float,
        net_salary: float,
        earnings: list[dict],
        deductions: list[dict],
        payment_date: datetime | None = None,
        inss_base: float | None = None,
        inss_value: float | None = None,
        irrf_base: float | None = None,
        irrf_value: float | None = None,
        fgts_base: float | None = None,
        fgts_value: float | None = None,
        employee_notes: str | None = None,
        external_id: str | None = None,
        source_system: str | None = None,
        import_batch_id: UUID | None = None,
        created_by: UUID | None = None,
    ) -> PaySlip:
        """Cria novo contracheque."""
        code = self._generate_code(reference_year, reference_month)
        payslip = PaySlip(
            id=uuid4(),
            condominio_id=condominio_id,
            employee_id=employee_id,
            payslip_code=code,
            payslip_type=payslip_type,
            status=PaySlipStatus.DRAFT.value,
            reference_month=reference_month,
            reference_year=reference_year,
            reference_period=f"{reference_year}-{reference_month:02d}",
            payment_date=payment_date,
            base_salary=base_salary,
            total_earnings=total_earnings,
            total_deductions=total_deductions,
            net_salary=net_salary,
            earnings=earnings,
            deductions=deductions,
            inss_base=inss_base,
            inss_value=inss_value,
            irrf_base=irrf_base,
            irrf_value=irrf_value,
            fgts_base=fgts_base,
            fgts_value=fgts_value,
            external_id=external_id,
            source_system=source_system,
            import_batch_id=import_batch_id,
            created_by=created_by,
        )

        self.db.add(payslip)
        await self.db.commit()
        await self.db.refresh(payslip)

        logger.info(
            "Contracheque %s criado para funcionário %s (ref: %02d/%d)",
            payslip.payslip_code,
            employee_id,
            reference_month,
            reference_year,
        )
        return payslip

    async def publish(
        self,
        payslip_id: UUID,
        *,
        published_by: UUID | None = None,
    ) -> PaySlip | None:
        """Publica contracheque (status → published, visível para funcionário)."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        payslip.status = PaySlipStatus.PUBLISHED.value
        payslip.published_at = datetime.utcnow()
        payslip.published_by = published_by

        await self.db.commit()
        await self.db.refresh(payslip)

        logger.info("Contracheque %s publicado por %s", payslip_id, published_by)
        return payslip

    async def revert_to_draft(self, payslip_id: UUID) -> PaySlip | None:
        """Reverte para rascunho."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        payslip.status = PaySlipStatus.DRAFT.value
        payslip.published_at = None
        payslip.published_by = None

        await self.db.commit()
        await self.db.refresh(payslip)
        return payslip

    async def soft_delete(self, payslip_id: UUID) -> bool:
        """Marca como cancelado (soft delete)."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return False

        payslip.status = PaySlipStatus.CANCELLED.value
        await self.db.commit()
        return True

    async def record_view(self, payslip_id: UUID) -> PaySlip | None:
        """Registra visualização."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        payslip.record_view()
        await self.db.commit()
        await self.db.refresh(payslip)
        return payslip

    async def record_download(self, payslip_id: UUID) -> PaySlip | None:
        """Registra download."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        payslip.record_download()
        await self.db.commit()
        await self.db.refresh(payslip)
        return payslip

    async def acknowledge(self, payslip_id: UUID, *, ip: str | None = None) -> PaySlip | None:
        """Registra ciência do funcionário."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip or payslip.acknowledged_at:
            return payslip

        payslip.acknowledged_at = datetime.utcnow()
        payslip.acknowledged_by_ip = ip

        await self.db.commit()
        await self.db.refresh(payslip)
        return payslip

    async def contest(self, payslip_id: UUID, *, reason: str) -> PaySlip | None:
        """Registra contestação."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        if not payslip.can_contest:
            raise ValueError("Contracheque não pode ser contestado no estado atual.")

        payslip.contested_at = datetime.utcnow()
        payslip.contest_reason = reason

        await self.db.commit()
        await self.db.refresh(payslip)
        return payslip

    async def save_pdf_path(self, payslip_id: UUID, pdf_path: str) -> PaySlip | None:
        """Salva caminho do PDF gerado."""
        payslip = await self.get_by_id(payslip_id)
        if not payslip:
            return None

        payslip.pdf_path = pdf_path
        payslip.pdf_generated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(payslip)
        return payslip

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    def _generate_code(self, year: int, month: int) -> str:
        """Gera código único do contracheque."""
        import random
        import string

        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))  # noqa: S311
        return f"HL{year}{month:02d}{suffix}"
