"""
Serviço de Rescisão — Departamento Pessoal.

Gerencia o workflow de desligamento: criação do processo,
cálculos rescisórios com CLT real (Decimal) e conclusão.
"""

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee
from modules.people_management.common.utils.clt_calculator import (
    calcular_rescisao,
)
from modules.people_management.hr.models.termination import (
    TerminationProcess,
    TerminationStatus,
    TerminationType,
)

logger = logging.getLogger(__name__)


class TerminationService:
    """Serviço para processos de rescisão."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_termination(
        self,
        data: dict,
        created_by_id: str | UUID | None = None,
    ) -> TerminationProcess:
        """Cria um novo processo de rescisão.

        Args:
            data: Dados do processo (schema TerminationCreate).
            created_by_id: ID do usuário que criou.

        Returns:
            Instância de TerminationProcess criada.
        """
        termination = TerminationProcess(
            id=uuid4(),
            employee_id=data["employee_id"],
            type=data["type"],
            reason=data.get("reason"),
            notice_period_days=data.get("notice_period_days"),
            notice_start_date=data.get("notice_start_date"),
            last_working_day=data.get("last_working_day"),
            status=TerminationStatus.INITIATED,
            created_by_id=str(created_by_id) if created_by_id else None,
        )
        self.db.add(termination)
        await self.db.flush()
        await self.db.refresh(termination)
        logger.info("Processo de rescisão criado: %s", termination.id)
        return termination

    async def get_by_id(self, termination_id: str | UUID) -> TerminationProcess | None:
        """Busca processo de rescisão por ID."""
        result = await self.db.execute(select(TerminationProcess).where(TerminationProcess.id == str(termination_id)))
        return result.scalar_one_or_none()

    async def list_terminations(
        self,
        status: TerminationStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Lista processos de rescisão com filtro e paginação."""
        from sqlalchemy import func

        query = select(TerminationProcess)
        count_query = select(func.count()).select_from(TerminationProcess)

        if status:
            query = query.where(TerminationProcess.status == status)
            count_query = count_query.where(TerminationProcess.status == status)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        total_pages = max(1, (total + page_size - 1) // page_size)

        query = query.order_by(TerminationProcess.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return {
            "items": list(items),
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def calculate_severance(
        self,
        employee_id: str | UUID,
        termination_type: TerminationType,
        last_working_day: date,
    ) -> dict:
        """Calcula verbas rescisórias conforme CLT com Decimal preciso.

        Args:
            employee_id: ID do funcionário.
            termination_type: Tipo de rescisão.
            last_working_day: Último dia de trabalho.

        Returns:
            Dicionário com breakdown dos cálculos rescisórios.
        """
        result = await self.db.execute(select(Employee).where(Employee.id == str(employee_id)))
        employee = result.scalar_one_or_none()
        if not employee:
            raise ValueError(f"Funcionário {employee_id} não encontrado")

        salario_base = Decimal(str(employee.salario_base or 0))
        data_admissao = employee.data_admissao

        if not data_admissao:
            data_admissao = last_working_day  # fallback

        # Meses trabalhados
        delta = last_working_day - data_admissao
        months_worked = max(1, delta.days // 30)

        # Mapear tipo de rescisão para clt_calculator
        type_map = {
            TerminationType.INVOLUNTARY: "involuntary",
            TerminationType.VOLUNTARY: "voluntary",
            TerminationType.JUST_CAUSE: "just_cause",
            TerminationType.MUTUAL_AGREEMENT: "mutual_agreement",
        }
        tipo_str = type_map.get(termination_type, str(termination_type.value))

        # Estimar saldo FGTS acumulado
        saldo_fgts = salario_base * Decimal("0.08") * months_worked

        # Férias vencidas (simplificado: 30 dias se > 12 meses)
        ferias_vencidas_dias = 30 if months_worked > 12 else 0

        # Dias trabalhados no mês da rescisão
        dias_trabalhados_mes = last_working_day.day

        # Usar clt_calculator para cálculo completo
        calc = calcular_rescisao(
            salario_base=salario_base,
            tipo_rescisao=tipo_str,
            data_admissao=data_admissao,
            data_demissao=last_working_day,
            saldo_fgts=saldo_fgts,
            ferias_vencidas_dias=ferias_vencidas_dias,
            dias_trabalhados_mes=dias_trabalhados_mes,
        )

        return {
            "employee_id": str(employee_id),
            "employee_name": employee.nome,
            "termination_type": termination_type,
            "last_working_day": last_working_day,
            "months_worked": months_worked,
            "saldo_salario": float(calc["saldo_salario"]),
            "aviso_previo_indenizado": float(calc["aviso_previo_indenizado"]),
            "aviso_previo_dias": calc["aviso_previo_dias"],
            "ferias_vencidas": float(calc["ferias_vencidas"]),
            "ferias_proporcionais": float(calc["ferias_proporcionais"]),
            "terco_constitucional": float(calc["terco_ferias_vencidas"] + calc["terco_ferias_proporcionais"]),
            "decimo_terceiro_proporcional": float(calc["decimo_terceiro_proporcional"]),
            "multa_fgts_40": float(calc["multa_fgts"]),
            "total_proventos": float(calc["total_bruto"]),
            "inss": float(calc["inss"]),
            "irrf": float(calc["irrf"]),
            "total_descontos": float(calc["total_descontos"]),
            "total_liquido": float(calc["total_liquido"]),
        }

    async def complete_termination(
        self,
        termination_id: str | UUID,
    ) -> TerminationProcess | None:
        """Conclui o processo de rescisão.

        Atualiza o status do funcionário para 'Desligado' e marca
        o processo como concluído.

        Args:
            termination_id: ID do processo de rescisão.

        Returns:
            Processo atualizado ou None se não encontrado.
        """
        termination = await self.get_by_id(termination_id)
        if not termination:
            return None

        # Calcular verbas se ainda não calculadas
        if not termination.total_amount and termination.last_working_day:
            calc = await self.calculate_severance(
                termination.employee_id,
                TerminationType(termination.type),
                termination.last_working_day,
            )
            termination.severance_amount = calc.get("aviso_previo_indenizado", 0)
            termination.vacation_balance_amount = calc.get("ferias_vencidas", 0) + calc.get("ferias_proporcionais", 0)
            termination.thirteenth_salary_amount = calc.get("decimo_terceiro_proporcional", 0)
            termination.fgts_amount = calc.get("multa_fgts_40", 0)
            termination.total_amount = calc.get("total_liquido", 0)

        termination.status = TerminationStatus.COMPLETED

        # Atualizar status do funcionário
        emp_result = await self.db.execute(select(Employee).where(Employee.id == str(termination.employee_id)))
        employee = emp_result.scalar_one_or_none()
        if employee:
            employee.status = "Desligado"
            if termination.last_working_day:
                employee.data_demissao = termination.last_working_day

        await self.db.flush()
        await self.db.refresh(termination)
        logger.info("Rescisão %s concluída", termination_id)

        # Publicar evento de funcionário demitido no message bus
        try:
            import asyncio

            from infrastructure.message_bus.events import Event, EventType, publish_event

            event = Event(
                type=EventType.FUNCIONARIO_DEMITIDO,
                source="people_management.termination_service",
                data={
                    "funcionario_id": str(termination.employee_id),
                    "termination_id": str(termination_id),
                    "tipo_rescisao": termination.type,
                    "ultimo_dia": str(termination.last_working_day) if termination.last_working_day else None,
                    "cargo": employee.cargo if employee else None,
                    "departamento": employee.departamento if employee else None,
                },
            )
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(publish_event(event))
            else:
                asyncio.run(publish_event(event))
        except Exception as _pub_err:
            logger.warning("Falha ao publicar FUNCIONARIO_DEMITIDO: %s", _pub_err)

        return termination
