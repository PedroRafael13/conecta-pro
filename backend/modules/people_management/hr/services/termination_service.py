"""
Serviço de Rescisão — Departamento Pessoal.

Gerencia o workflow de desligamento: criação do processo,
cálculos rescisórios (férias, 13o, FGTS 40%) e conclusão.
"""

import logging
from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee
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
        """Calcula verbas rescisórias conforme CLT.

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

        salario = float(employee.salario_base or 0)
        data_admissao = employee.data_admissao
        salario_dia = salario / 30 if salario else 0

        # Meses trabalhados
        if data_admissao:
            delta = last_working_day - data_admissao
            months_worked = max(1, delta.days // 30)
        else:
            months_worked = 1

        # Saldo de salário (dias do mês trabalhados)
        dias_trabalhados_mes = last_working_day.day
        saldo_salario = salario_dia * dias_trabalhados_mes

        # Aviso prévio indenizado (30 dias + 3 dias por ano trabalhado)
        anos_trabalhados = months_worked // 12
        aviso_previo = 0.0
        if termination_type in (
            TerminationType.INVOLUNTARY,
            TerminationType.MUTUAL_AGREEMENT,
        ):
            dias_aviso = min(90, 30 + (anos_trabalhados * 3))
            aviso_previo = salario_dia * dias_aviso
            if termination_type == TerminationType.MUTUAL_AGREEMENT:
                aviso_previo *= 0.5  # Acordo: 50% do aviso

        # Férias proporcionais
        meses_periodo = months_worked % 12 or 12
        ferias_proporcionais = (salario / 12) * meses_periodo

        # Férias vencidas (simplificado: se > 12 meses e não gozou)
        ferias_vencidas = salario if months_worked > 12 else 0.0

        # 1/3 constitucional
        terco = (ferias_proporcionais + ferias_vencidas) / 3

        # 13o proporcional
        meses_13 = last_working_day.month
        decimo_terceiro = (salario / 12) * meses_13

        # FGTS do mês da rescisão
        fgts_mes = saldo_salario * 0.08

        # Multa de 40% do FGTS (estimativa sobre saldo acumulado)
        fgts_acumulado_estimado = salario * 0.08 * months_worked
        multa_fgts = 0.0
        if termination_type == TerminationType.INVOLUNTARY:
            multa_fgts = fgts_acumulado_estimado * 0.40
        elif termination_type == TerminationType.MUTUAL_AGREEMENT:
            multa_fgts = fgts_acumulado_estimado * 0.20

        # Justa causa: perde férias proporcionais, 13o, aviso e multa FGTS
        if termination_type == TerminationType.JUST_CAUSE:
            aviso_previo = 0.0
            ferias_proporcionais = 0.0
            terco = ferias_vencidas / 3 if ferias_vencidas else 0.0
            decimo_terceiro = 0.0
            multa_fgts = 0.0

        total_proventos = (
            saldo_salario
            + aviso_previo
            + ferias_vencidas
            + ferias_proporcionais
            + terco
            + decimo_terceiro
            + fgts_mes
            + multa_fgts
        )

        return {
            "employee_id": str(employee_id),
            "employee_name": employee.nome,
            "termination_type": termination_type,
            "last_working_day": last_working_day,
            "months_worked": months_worked,
            "saldo_salario": round(saldo_salario, 2),
            "aviso_previo_indenizado": round(aviso_previo, 2),
            "ferias_vencidas": round(ferias_vencidas, 2),
            "ferias_proporcionais": round(ferias_proporcionais, 2),
            "terco_constitucional": round(terco, 2),
            "decimo_terceiro_proporcional": round(decimo_terceiro, 2),
            "fgts_mes_rescisao": round(fgts_mes, 2),
            "multa_fgts_40": round(multa_fgts, 2),
            "total_proventos": round(total_proventos, 2),
            "total_descontos": 0.0,
            "total_liquido": round(total_proventos, 2),
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
        return termination
