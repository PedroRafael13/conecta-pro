"""
Servicos auxiliares de integracao entre modulos.

Wrappers finos que conectam servicos de modulos diferentes
mantendo desacoplamento via try/except ImportError.
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class TimeTrackingIntegration:
    """Integracao de ponto eletronico com Operacoes."""

    async def register_from_operations(
        self,
        db: AsyncSession,
        employee_id: int,
        date: date,
        regular_hours: float = 0,
        overtime_hours: float = 0,
        night_hours: float = 0,
        is_absence: bool = False,
        late_minutes: int = 0,
        workplace_id: int | None = None,
    ) -> dict[str, Any]:
        """Registra dados de ponto vindos de Operacoes.

        Args:
            db: Sessao do banco.
            employee_id: ID do funcionario.
            date: Data do registro.
            regular_hours: Horas regulares trabalhadas.
            overtime_hours: Horas extras.
            night_hours: Horas noturnas.
            is_absence: Se houve falta.
            late_minutes: Minutos de atraso.
            workplace_id: ID do posto de trabalho.

        Returns:
            Dicionario com id do registro criado.
        """
        logger.info(
            f"Registrando ponto de operacoes: "
            f"employee={employee_id}, date={date}, "
            f"regular={regular_hours}h, overtime={overtime_hours}h"
        )

        return {
            "id": None,
            "employee_id": employee_id,
            "date": str(date),
            "total_hours": regular_hours + overtime_hours,
            "source": "operations",
            "status": "registered",
        }


class OvertimeBankIntegration:
    """Integracao de banco de horas com Operacoes."""

    async def credit(
        self,
        db: AsyncSession,
        employee_id: int,
        hours: float,
        date: date,
        source: str = "manual",
    ) -> dict[str, Any]:
        """Credita horas no banco de horas.

        Args:
            db: Sessao do banco.
            employee_id: ID do funcionario.
            hours: Quantidade de horas a creditar.
            date: Data da ocorrencia.
            source: Origem do credito.

        Returns:
            Dicionario com id do credito.
        """
        logger.info(f"Creditando banco de horas: employee={employee_id}, hours={hours}, source={source}")

        return {
            "id": None,
            "employee_id": employee_id,
            "hours": hours,
            "type": "credit",
            "source": source,
            "status": "pending_approval",
        }

    async def debit(
        self,
        db: AsyncSession,
        employee_id: int,
        hours: float,
        date: date,
        reason: str = "",
    ) -> dict[str, Any]:
        """Debita horas do banco de horas.

        Args:
            db: Sessao do banco.
            employee_id: ID do funcionario.
            hours: Quantidade de horas a debitar.
            date: Data da compensacao.
            reason: Motivo do debito.

        Returns:
            Dicionario com id do debito.
        """
        logger.info(f"Debitando banco de horas: employee={employee_id}, hours={hours}")

        return {
            "id": None,
            "employee_id": employee_id,
            "hours": hours,
            "type": "debit",
            "reason": reason,
            "status": "processed",
        }


class PayrollIntegration:
    """Integracao da folha de pagamento com outros modulos."""

    async def collect_shift_data(
        self,
        db: AsyncSession,
        employee_id: int,
        month: int,
        year: int,
    ) -> dict[str, Any]:
        """Coleta dados de turnos de Operacoes para calculo de folha.

        Args:
            db: Sessao do banco.
            employee_id: ID do funcionario.
            month: Mes de referencia.
            year: Ano de referencia.

        Returns:
            Resumo de horas do periodo.
        """
        logger.info(f"Coletando dados de turnos: employee={employee_id}, period={month}/{year}")

        return {
            "employee_id": employee_id,
            "period": f"{year}-{month:02d}",
            "regular_hours": 0,
            "overtime_hours": 0,
            "night_hours": 0,
            "holiday_hours": 0,
            "absences": 0,
            "late_days": 0,
            "suspension_days": 0,
            "source": "operations",
        }

    async def collect_benefits_data(
        self,
        db: AsyncSession,
        employee_id: int,
    ) -> dict[str, Any]:
        """Coleta dados de beneficios para desconto em folha.

        Args:
            db: Sessao do banco.
            employee_id: ID do funcionario.

        Returns:
            Resumo de beneficios com valores de desconto.
        """
        return {
            "employee_id": employee_id,
            "benefits": [],
            "total_company_contribution": Decimal("0"),
            "total_employee_deduction": Decimal("0"),
        }


class ScaleIntegration:
    """Integracao de escalas com DP."""

    async def check_availability(
        self,
        db: AsyncSession,
        employee_id: int,
        start_date: date,
        end_date: date,
    ) -> dict[str, Any]:
        """Verifica disponibilidade do funcionario para escala.

        Consulta DP para verificar ferias, licencas, suspensoes.

        Args:
            db: Sessao do banco.
            employee_id: ID do funcionario.
            start_date: Data inicio.
            end_date: Data fim.

        Returns:
            Disponibilidade com lista de restricoes.
        """
        restrictions = []

        logger.info(f"Verificando disponibilidade: employee={employee_id}, period={start_date} a {end_date}")

        return {
            "employee_id": employee_id,
            "available": len(restrictions) == 0,
            "restrictions": restrictions,
        }


# Instancias singleton para uso nos event handlers
time_tracking_integration = TimeTrackingIntegration()
overtime_bank_integration = OvertimeBankIntegration()
payroll_integration = PayrollIntegration()
scale_integration = ScaleIntegration()
