"""Service para contracheques/holerites."""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.employee_portal.models import PaySlip, PaySlipStatus, PaySlipType
from modules.hr.employee_portal.repositories import PaySlipRepository
from modules.hr.employee_portal.schemas import (
    PaySlipCreate,
    PaySlipDeductionItem,
    PaySlipEarningItem,
)

logger = logging.getLogger(__name__)


class PaySlipService:
    """Service para operações de contracheques."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PaySlipRepository(db)

    async def create_payslip(
        self,
        data: PaySlipCreate,
        condominio_id: UUID,
        *,
        created_by: UUID | None = None,
    ) -> PaySlip:
        """Cria novo contracheque."""
        return await self.repo.create(data, condominio_id, created_by=created_by)

    async def get_payslip(self, payslip_id: UUID) -> PaySlip | None:
        """Busca contracheque por ID."""
        return await self.repo.get_by_id(payslip_id)

    async def list_employee_payslips(
        self,
        employee_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        year: int | None = None,
        payslip_type: PaySlipType | None = None,
    ) -> tuple[list[PaySlip], int]:
        """Lista contracheques do funcionário."""
        return await self.repo.list_by_employee(
            employee_id,
            page=page,
            page_size=page_size,
            year=year,
            payslip_type=payslip_type,
            only_viewable=True,
        )

    async def view_payslip(
        self,
        payslip_id: UUID,
        employee_id: UUID,
    ) -> PaySlip | None:
        """Visualiza contracheque (registra view)."""
        payslip = await self.repo.get_by_id(payslip_id)
        if not payslip or payslip.employee_id != employee_id:
            return None

        if not payslip.is_viewable:
            raise ValueError("Contracheque não disponível para visualização")

        return await self.repo.record_view(payslip_id)

    async def download_payslip(
        self,
        payslip_id: UUID,
        employee_id: UUID,
    ) -> PaySlip | None:
        """Download do contracheque (registra download)."""
        payslip = await self.repo.get_by_id(payslip_id)
        if not payslip or payslip.employee_id != employee_id:
            return None

        if not payslip.is_viewable:
            raise ValueError("Contracheque não disponível para download")

        return await self.repo.record_download(payslip_id)

    async def acknowledge_payslip(
        self,
        payslip_id: UUID,
        employee_id: UUID,
    ) -> PaySlip | None:
        """Registra ciência no contracheque."""
        payslip = await self.repo.get_by_id(payslip_id)
        if not payslip or payslip.employee_id != employee_id:
            return None

        return await self.repo.acknowledge(payslip_id)

    async def contest_payslip(
        self,
        payslip_id: UUID,
        employee_id: UUID,
        reason: str,
    ) -> PaySlip | None:
        """Contesta contracheque."""
        payslip = await self.repo.get_by_id(payslip_id)
        if not payslip or payslip.employee_id != employee_id:
            return None

        return await self.repo.contest(payslip_id, reason)

    async def get_employee_summary(
        self,
        employee_id: UUID,
    ) -> dict:
        """Retorna resumo de contracheques do funcionário."""
        unread_count = await self.repo.get_unread_count(employee_id)
        pending_ack = await self.repo.get_pending_ack_count(employee_id)
        years = await self.repo.get_years_available(employee_id)

        # Buscar último contracheque
        payslips, _ = await self.repo.list_by_employee(
            employee_id,
            page=1,
            page_size=1,
            only_viewable=True,
        )

        last_payslip = None
        if payslips:
            ps = payslips[0]
            last_payslip = {
                "id": str(ps.id),
                "reference_period": ps.reference_period,
                "net_salary": float(ps.net_salary),
                "payment_date": ps.payment_date.isoformat() if ps.payment_date else None,
            }

        return {
            "unread_count": unread_count,
            "pending_acknowledgement": pending_ack,
            "available_years": years,
            "last_payslip": last_payslip,
        }

    async def generate_pdf(
        self,
        payslip_id: UUID,
    ) -> str | None:
        """Gera PDF do contracheque."""
        payslip = await self.repo.get_by_id(payslip_id)
        if not payslip:
            return None

        # Simular geração de PDF
        # Em produção, usaria biblioteca como ReportLab ou WeasyPrint
        pdf_path = f"/payslips/{payslip.condominio_id}/{payslip.payslip_code}.pdf"

        payslip.pdf_path = pdf_path
        payslip.pdf_generated_at = datetime.utcnow()
        await self.db.commit()

        logger.info("PDF gerado para contracheque %s", payslip_id)
        return pdf_path

    async def publish_payslip(
        self,
        payslip_id: UUID,
        *,
        published_by: UUID | None = None,
    ) -> PaySlip | None:
        """Publica contracheque (visível para funcionário)."""
        return await self.repo.publish(payslip_id, published_by=published_by)

    async def bulk_publish(
        self,
        condominio_id: UUID,
        year: int,
        month: int,
        *,
        published_by: UUID | None = None,
    ) -> int:
        """Publica contracheques em lote."""
        payslips, _ = await self.repo.list_by_condominio(
            condominio_id,
            status=PaySlipStatus.GENERATED,
            year=year,
            month=month,
            page_size=1000,
        )

        count = 0
        for payslip in payslips:
            if payslip.status == PaySlipStatus.GENERATED.value:
                await self.repo.publish(payslip.id, published_by=published_by)
                count += 1

        logger.info("Publicados %d contracheques de %02d/%d", count, month, year)
        return count

    def calculate_totals(
        self,
        earnings: list[PaySlipEarningItem],
        deductions: list[PaySlipDeductionItem],
    ) -> dict:
        """Calcula totais do contracheque."""
        total_earnings = sum(e.value for e in earnings)
        total_deductions = sum(d.value for d in deductions)
        net_salary = total_earnings - total_deductions

        return {
            "total_earnings": total_earnings,
            "total_deductions": total_deductions,
            "net_salary": net_salary,
        }
