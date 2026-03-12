"""
Serviço de Férias — Departamento Pessoal.

Re-exporta funcionalidades do employee_portal e módulo operacional de férias,
adicionando cálculo de saldo de férias e aprovação com notificação.
"""

import contextlib
import logging
from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee

logger = logging.getLogger(__name__)

# Re-export do serviço existente de férias
try:
    from modules.hr.employee_portal.services import VacationService as PortalVacationService
except ImportError:
    PortalVacationService = None  # type: ignore[assignment, misc]

try:
    from modules.operacional.vacations.models import VacationRequest
except ImportError:
    VacationRequest = None  # type: ignore[assignment, misc]


class VacationService:
    """Serviço de Férias — visão DP."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._portal_service = None
        if PortalVacationService:
            with contextlib.suppress(Exception):
                self._portal_service = PortalVacationService(db)

    async def calculate_vacation_balance(self, employee_id: str | UUID) -> dict:
        """Calcula o saldo de férias do funcionário.

        Considera data de admissão, períodos aquisitivos e férias já gozadas.

        Args:
            employee_id: ID do funcionário.

        Returns:
            Dicionário com dados do saldo de férias.
        """
        result = await self.db.execute(select(Employee).where(Employee.id == str(employee_id)))
        employee = result.scalar_one_or_none()
        if not employee:
            raise ValueError(f"Funcionário {employee_id} não encontrado")

        data_admissao = employee.data_admissao
        if not data_admissao:
            return {
                "employee_id": str(employee_id),
                "employee_name": employee.nome,
                "dias_direito": 0,
                "dias_gozados": 0,
                "dias_saldo": 0,
                "periodos_aquisitivos": [],
                "message": "Data de admissão não informada",
            }

        today = date.today()
        delta = today - data_admissao
        meses_trabalhados = delta.days // 30

        # Dias de direito: 30 dias a cada 12 meses
        periodos_completos = meses_trabalhados // 12
        meses_periodo_atual = meses_trabalhados % 12
        dias_proporcional = int((30 / 12) * meses_periodo_atual)
        dias_direito_total = (periodos_completos * 30) + dias_proporcional

        # Buscar férias gozadas
        dias_gozados = 0
        if VacationRequest:
            try:
                vac_result = await self.db.execute(
                    select(VacationRequest).where(
                        VacationRequest.employee_id == str(employee_id),
                        VacationRequest.status == "approved",
                    )
                )
                vacations = vac_result.scalars().all()
                for v in vacations:
                    if hasattr(v, "days_count") and v.days_count:
                        dias_gozados += v.days_count
                    elif hasattr(v, "start_date") and hasattr(v, "end_date"):
                        if v.start_date and v.end_date:
                            dias_gozados += (v.end_date - v.start_date).days
            except Exception as e:
                logger.warning("Erro ao buscar férias gozadas: %s", e)

        dias_saldo = max(0, dias_direito_total - dias_gozados)

        return {
            "employee_id": str(employee_id),
            "employee_name": employee.nome,
            "data_admissao": data_admissao.isoformat(),
            "meses_trabalhados": meses_trabalhados,
            "periodos_completos": periodos_completos,
            "dias_direito": dias_direito_total,
            "dias_gozados": dias_gozados,
            "dias_saldo": dias_saldo,
            "dias_proporcional_periodo_atual": dias_proporcional,
        }

    async def approve_vacation(
        self,
        vacation_id: str | UUID,
        approved_by_id: str | UUID | None = None,
    ) -> dict:
        """Aprova uma solicitação de férias e notifica operações.

        Args:
            vacation_id: ID da solicitação de férias.
            approved_by_id: ID do usuário que aprovou.

        Returns:
            Dicionário com resultado da aprovação.
        """
        if not VacationRequest:
            raise ValueError("Módulo de férias não disponível")

        result = await self.db.execute(select(VacationRequest).where(VacationRequest.id == str(vacation_id)))
        vacation = result.scalar_one_or_none()
        if not vacation:
            raise ValueError(f"Solicitação de férias {vacation_id} não encontrada")

        vacation.status = "approved"
        if hasattr(vacation, "approved_by_id"):
            vacation.approved_by_id = str(approved_by_id) if approved_by_id else None

        await self.db.flush()
        await self.db.refresh(vacation)

        # Notificar operações (async, não bloqueia)
        try:
            from modules.operacional.services import notify_vacation_approved

            await notify_vacation_approved(vacation)
        except (ImportError, Exception) as e:
            logger.info("Notificação de férias não enviada: %s", e)

        logger.info("Férias %s aprovadas", vacation_id)
        return {
            "vacation_id": str(vacation_id),
            "status": "approved",
            "message": "Férias aprovadas com sucesso",
        }
