"""Service para gerenciamento de eventos de folha."""

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.payroll_integration.models import EventCategory, EventType, PayrollEvent
from modules.hr.payroll_integration.repositories import (
    PayrollEventRepository,
    PayrollPeriodRepository,
)
from modules.hr.payroll_integration.schemas import (
    EmployeePayrollSummary,
    EventAdjustmentRequest,
    PayrollEventBulkCreate,
    PayrollEventCreate,
    PayrollEventUpdate,
)

logger = logging.getLogger(__name__)


class PayrollEventService:
    """Service para operações de eventos de folha."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.period_repo = PayrollPeriodRepository(db)
        self.event_repo = PayrollEventRepository(db)

    async def create_event(
        self,
        data: PayrollEventCreate,
        condominio_id: UUID,
        *,
        user_id: UUID = None,
    ) -> PayrollEvent:
        """Cria novo evento."""
        # Validar período
        period = await self.period_repo.get_by_id(data.period_id)
        if not period:
            raise ValueError("Período não encontrado")
        if not period.is_editable:
            raise ValueError("Período não permite edição")

        # Verificar duplicidade
        exists = await self.event_repo.exists_for_employee(
            data.employee_id,
            data.period_id,
            data.event_code,
        )
        if exists:
            raise ValueError(f"Evento {data.event_code} já existe para este funcionário no período")

        event = await self.event_repo.create(data, condominio_id, created_by=user_id)
        logger.info("Evento criado: %s para funcionário %s", data.event_code, data.employee_id)

        return event

    async def create_bulk(
        self,
        data: PayrollEventBulkCreate,
        condominio_id: UUID,
        *,
        user_id: UUID = None,
    ) -> Dict[str, Any]:
        """Cria eventos em lote."""
        period = await self.period_repo.get_by_id(data.period_id)
        if not period:
            raise ValueError("Período não encontrado")
        if not period.is_editable:
            raise ValueError("Período não permite edição")

        results = {
            "created": 0,
            "failed": 0,
            "errors": [],
        }

        for event_data in data.events:
            try:
                await self.event_repo.create(
                    event_data,
                    condominio_id,
                    created_by=user_id,
                )
                results["created"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(
                    {
                        "event_code": event_data.event_code,
                        "employee_id": str(event_data.employee_id),
                        "error": str(e),
                    }
                )

        logger.info(
            "Bulk create: %d criados, %d falhas",
            results["created"],
            results["failed"],
        )
        return results

    async def get_event(self, event_id: UUID) -> Optional[PayrollEvent]:
        """Busca evento por ID."""
        return await self.event_repo.get_by_id(event_id)

    async def list_period_events(
        self,
        period_id: UUID,
        *,
        employee_id: UUID = None,
        event_type: EventType = None,
        event_category: EventCategory = None,
        page: int = 1,
        page_size: int = 100,
    ) -> tuple:
        """Lista eventos de um período."""
        return await self.event_repo.list_by_period(
            period_id,
            employee_id=employee_id,
            event_type=event_type,
            event_category=event_category,
            page=page,
            page_size=page_size,
        )

    async def get_employee_events(
        self,
        employee_id: UUID,
        period_id: UUID,
    ) -> List[PayrollEvent]:
        """Retorna todos eventos de um funcionário no período."""
        return await self.event_repo.list_by_employee(employee_id, period_id)

    async def get_employee_summary(
        self,
        employee_id: UUID,
        period_id: UUID,
    ) -> EmployeePayrollSummary:
        """Retorna resumo da folha do funcionário."""
        events = await self.event_repo.list_by_employee(employee_id, period_id)
        totals = await self.event_repo.get_employee_totals(employee_id, period_id)

        # Separar por tipo
        earnings = [e for e in events if e.event_type == EventType.EARNING.value]
        deductions = [e for e in events if e.event_type == EventType.DEDUCTION.value]

        # Buscar INSS/IRRF
        inss = next(
            (e.value for e in deductions if e.event_category == EventCategory.INSS.value),
            Decimal("0"),
        )
        irrf = next(
            (e.value for e in deductions if e.event_category == EventCategory.IRRF.value),
            Decimal("0"),
        )

        # Calcular FGTS (informativo)
        fgts_base = sum(e.value for e in earnings if e.esocial_incidences.get("fgts", False))
        fgts = fgts_base * Decimal("0.08")

        return EmployeePayrollSummary(
            employee_id=employee_id,
            employee_name="",  # Preenchido pelo controller
            employee_cpf=None,
            department=None,
            position=None,
            admission_date=None,
            base_salary=Decimal("0"),
            total_earnings=totals["total_earnings"],
            total_deductions=totals["total_deductions"],
            net_salary=totals["net_salary"],
            total_hours=None,
            overtime_hours=None,
            absence_hours=None,
            events=[
                {
                    "event_code": e.event_code,
                    "event_name": e.event_name,
                    "event_type": e.event_type,
                    "value": e.value,
                }
                for e in events
            ],
            inss=inss,
            irrf=irrf,
            fgts=fgts.quantize(Decimal("0.01")),
        )

    async def update_event(
        self,
        event_id: UUID,
        data: PayrollEventUpdate,
    ) -> Optional[PayrollEvent]:
        """Atualiza evento."""
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            return None

        period = await self.period_repo.get_by_id(event.period_id)
        if not period or not period.is_editable:
            raise ValueError("Período não permite edição")

        return await self.event_repo.update(event_id, data)

    async def adjust_event(
        self,
        event_id: UUID,
        data: EventAdjustmentRequest,
        user_id: UUID,
    ) -> Optional[PayrollEvent]:
        """Ajusta valor do evento."""
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            return None

        period = await self.period_repo.get_by_id(event.period_id)
        if not period or not period.is_editable:
            raise ValueError("Período não permite edição")

        return await self.event_repo.adjust_value(
            event_id,
            data.new_value,
            data.reason,
            user_id,
        )

    async def cancel_event(
        self,
        event_id: UUID,
        reason: str,
        user_id: UUID,
    ) -> Optional[PayrollEvent]:
        """Cancela evento."""
        event = await self.event_repo.get_by_id(event_id)
        if not event:
            return None

        period = await self.period_repo.get_by_id(event.period_id)
        if not period or not period.is_editable:
            raise ValueError("Período não permite edição")

        return await self.event_repo.cancel(event_id, reason, user_id)

    async def get_events_by_category(
        self,
        period_id: UUID,
    ) -> Dict[str, List[PayrollEvent]]:
        """Retorna eventos agrupados por categoria."""
        return await self.event_repo.get_events_by_category(period_id)

    async def get_period_totals(
        self,
        period_id: UUID,
    ) -> Dict[str, Decimal]:
        """Retorna totais do período."""
        return await self.event_repo.get_period_totals(period_id)

    async def recalculate_employee(
        self,
        employee_id: UUID,
        period_id: UUID,
        condominio_id: UUID,
        *,
        user_id: UUID = None,
    ) -> Dict[str, Any]:
        """Recalcula folha de um funcionário."""
        # Importar aqui para evitar circular import
        from modules.hr.payroll_integration.repositories import EmployeePayrollConfigRepository
        from modules.hr.payroll_integration.services.payroll_calculation_service import (
            PayrollCalculationService,
        )

        # Buscar configuração do funcionário
        config_repo = EmployeePayrollConfigRepository(self.db)
        config = await config_repo.get_by_employee(employee_id, condominio_id)
        if not config:
            raise ValueError("Configuração de folha não encontrada")

        # Buscar período
        period = await self.period_repo.get_by_id(period_id)
        if not period:
            raise ValueError("Período não encontrado")

        # Deletar eventos existentes
        deleted = await self.event_repo.delete_by_period(
            period_id,
            employee_id=employee_id,
        )

        # Recalcular
        calc_service = PayrollCalculationService(self.db)
        events = await calc_service._calculate_employee_payroll(
            employee=config,
            period=period,
            condominio_id=condominio_id,
        )

        # Criar novos eventos
        created = 0
        for event_data in events:
            await self.event_repo.create(event_data, condominio_id, created_by=user_id)
            created += 1

        # Atualizar totais do período
        totals = await self.event_repo.get_period_totals(period_id)
        await self.period_repo.update_totals(
            period_id,
            {
                "total_employees": totals["total_employees"],
                "total_earnings": totals["total_earnings"],
                "total_deductions": totals["total_deductions"],
                "total_net": totals["total_net"],
            },
        )

        return {
            "employee_id": str(employee_id),
            "deleted_events": deleted,
            "created_events": created,
            "totals": {
                "earnings": float(totals["total_earnings"]),
                "deductions": float(totals["total_deductions"]),
                "net": float(totals["total_net"]),
            },
        }

    async def import_events_from_file(
        self,
        period_id: UUID,
        file_content: bytes,
        file_format: str,
        condominio_id: UUID,
        *,
        user_id: UUID = None,
    ) -> Dict[str, Any]:
        """Importa eventos de arquivo."""
        # Validar período
        period = await self.period_repo.get_by_id(period_id)
        if not period:
            raise ValueError("Período não encontrado")
        if not period.is_editable:
            raise ValueError("Período não permite edição")

        results = {
            "imported": 0,
            "failed": 0,
            "errors": [],
        }

        # Implementação simplificada - em produção parsearia o arquivo
        logger.info(
            "Importação de %d bytes em formato %s para período %s",
            len(file_content),
            file_format,
            period_id,
        )

        return results
