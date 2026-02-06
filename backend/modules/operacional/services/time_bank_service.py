"""
TimeBankService - Serviço para gestão de banco de horas.

Este serviço implementa regras de negócio para:
- Cálculo de saldo de banco de horas
- Regras de compensação (CLT)
- Alertas de expiração
- Relatórios e estatísticas
"""

from datetime import date, timedelta
from typing import Any, Dict, List

from core.logging import logger


class TimeBankService:
    """
    Serviço de gestão do banco de horas.

    Implementa regras da CLT para banco de horas:
    - Limite de 2h extras por dia
    - Compensação em até 6 meses (acordo individual)
    - Compensação em até 1 ano (acordo coletivo)
    """

    # Configurações padrão
    MAX_DAILY_OVERTIME_HOURS = 2.0  # CLT
    DEFAULT_EXPIRATION_DAYS = 180  # 6 meses
    COLLECTIVE_AGREEMENT_EXPIRATION_DAYS = 365  # 1 ano
    WARN_EXPIRATION_DAYS = 30  # Alertar 30 dias antes

    def __init__(self) -> None:
        """Inicializa o serviço."""

    def calculate_overtime_hours(
        self,
        actual_hours: float,
        planned_hours: float,
        is_night_shift: bool = False,
        break_minutes: int = 0,
    ) -> Dict[str, float]:
        """
        Calcula horas extras de um turno.

        Args:
            actual_hours: Horas trabalhadas
            planned_hours: Horas previstas
            is_night_shift: Se é turno noturno
            break_minutes: Minutos de intervalo

        Returns:
            Dicionário com horas normais, extras e noturnas
        """
        # Descontar intervalo
        worked_hours = actual_hours - (break_minutes / 60)

        # Horas normais vs extras
        if worked_hours <= planned_hours:
            normal_hours = worked_hours
            overtime_hours = 0.0
            negative_hours = planned_hours - worked_hours
        else:
            normal_hours = planned_hours
            overtime_hours = min(
                worked_hours - planned_hours,
                self.MAX_DAILY_OVERTIME_HOURS,
            )
            negative_hours = 0.0

            # Alertar se ultrapassou limite diário
            if worked_hours - planned_hours > self.MAX_DAILY_OVERTIME_HOURS:
                logger.warning(
                    f"Horas extras ({worked_hours - planned_hours:.1f}h) "
                    f"excedem limite diário ({self.MAX_DAILY_OVERTIME_HOURS}h)"
                )

        # Adicional noturno (20% CLT)
        night_hours = 0.0
        if is_night_shift:
            night_hours = worked_hours  # Todas as horas são noturnas

        return {
            "worked_hours": round(worked_hours, 2),
            "normal_hours": round(normal_hours, 2),
            "overtime_hours": round(overtime_hours, 2),
            "negative_hours": round(negative_hours, 2),
            "night_hours": round(night_hours, 2),
        }

    def calculate_compensation_value(
        self,
        hours: float,
        hourly_rate: float,
        is_overtime: bool = False,
        is_night: bool = False,
        is_sunday: bool = False,
        is_holiday: bool = False,
    ) -> Dict[str, float]:
        """
        Calcula valor monetário das horas.

        Args:
            hours: Quantidade de horas
            hourly_rate: Valor hora base
            is_overtime: Se é hora extra
            is_night: Se é adicional noturno
            is_sunday: Se é domingo
            is_holiday: Se é feriado

        Returns:
            Dicionário com valores
        """
        base_value = hours * hourly_rate

        # Adicional noturno: 20% (CLT)
        night_bonus = base_value * 0.20 if is_night else 0

        # Hora extra: 50% (CLT)
        overtime_bonus = base_value * 0.50 if is_overtime else 0

        # Domingo: 100% (CLT)
        sunday_bonus = base_value * 1.00 if is_sunday else 0

        # Feriado: 100% (CLT)
        holiday_bonus = base_value * 1.00 if is_holiday else 0

        total_value = base_value + night_bonus + overtime_bonus + sunday_bonus + holiday_bonus

        return {
            "base_value": round(base_value, 2),
            "night_bonus": round(night_bonus, 2),
            "overtime_bonus": round(overtime_bonus, 2),
            "sunday_bonus": round(sunday_bonus, 2),
            "holiday_bonus": round(holiday_bonus, 2),
            "total_value": round(total_value, 2),
        }

    def get_expiration_date(
        self,
        reference_date: date,
        has_collective_agreement: bool = False,
    ) -> date:
        """
        Calcula data de expiração das horas.

        Args:
            reference_date: Data de referência
            has_collective_agreement: Se tem acordo coletivo

        Returns:
            Data de expiração
        """
        if has_collective_agreement:
            expiration_days = self.COLLECTIVE_AGREEMENT_EXPIRATION_DAYS
        else:
            expiration_days = self.DEFAULT_EXPIRATION_DAYS

        return reference_date + timedelta(days=expiration_days)

    def check_expiration_alerts(
        self,
        entries: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Verifica entradas próximas da expiração.

        Args:
            entries: Lista de entradas do banco

        Returns:
            Lista de alertas
        """
        alerts = []
        today = date.today()
        warn_date = today + timedelta(days=self.WARN_EXPIRATION_DAYS)

        for entry in entries:
            expiration = entry.get("expiration_date")
            if not expiration:
                continue

            if isinstance(expiration, str):
                expiration = date.fromisoformat(expiration)

            if expiration <= today:
                # Já expirou
                alerts.append(
                    {
                        "entry_id": entry.get("id"),
                        "employee_id": entry.get("employee_id"),
                        "hours": entry.get("hours", 0),
                        "expiration_date": expiration,
                        "status": "expired",
                        "severity": "critical",
                        "message": f"Banco de horas expirou em {expiration}",
                    }
                )
            elif expiration <= warn_date:
                # Vai expirar em breve
                days_left = (expiration - today).days
                alerts.append(
                    {
                        "entry_id": entry.get("id"),
                        "employee_id": entry.get("employee_id"),
                        "hours": entry.get("hours", 0),
                        "expiration_date": expiration,
                        "status": "expiring_soon",
                        "severity": "high" if days_left <= 7 else "medium",
                        "message": f"Banco de horas expira em {days_left} dias",
                        "days_left": days_left,
                    }
                )

        return alerts

    def validate_compensation_request(
        self,
        employee_balance: float,
        requested_hours: float,
        compensation_date: date,
    ) -> Dict[str, Any]:
        """
        Valida solicitação de compensação.

        Args:
            employee_balance: Saldo atual do funcionário
            requested_hours: Horas solicitadas
            compensation_date: Data da compensação

        Returns:
            Resultado da validação
        """
        is_valid = True
        errors = []
        warnings = []

        # Verificar saldo suficiente
        if requested_hours > employee_balance:
            is_valid = False
            errors.append(
                f"Saldo insuficiente: {employee_balance:.1f}h disponíveis, "
                f"{requested_hours:.1f}h solicitadas"
            )

        # Verificar data
        today = date.today()
        if compensation_date < today:
            is_valid = False
            errors.append("Data de compensação não pode ser no passado")

        # Verificar fim de semana
        if compensation_date.weekday() >= 5:
            warnings.append("Compensação em fim de semana")

        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "balance_after": max(0, employee_balance - requested_hours),
        }

    def calculate_monthly_summary(
        self,
        entries: List[Dict[str, Any]],
        month: int,
        year: int,
    ) -> Dict[str, Any]:
        """
        Calcula resumo mensal do banco de horas.

        Args:
            entries: Lista de entradas
            month: Mês
            year: Ano

        Returns:
            Resumo mensal
        """
        monthly_entries = [
            e
            for e in entries
            if e.get("reference_date")
            and date.fromisoformat(str(e["reference_date"])).month == month
            and date.fromisoformat(str(e["reference_date"])).year == year
        ]

        credit_total = sum(
            e.get("hours", 0) for e in monthly_entries if e.get("entry_type") == "credit"
        )
        debit_total = sum(
            e.get("hours", 0) for e in monthly_entries if e.get("entry_type") == "debit"
        )
        compensation_total = sum(
            e.get("hours", 0) for e in monthly_entries if e.get("entry_type") == "compensation"
        )

        return {
            "month": month,
            "year": year,
            "entries_count": len(monthly_entries),
            "total_credits": round(credit_total, 2),
            "total_debits": round(debit_total, 2),
            "total_compensations": round(compensation_total, 2),
            "net_balance": round(credit_total - debit_total - compensation_total, 2),
        }

    def get_recommendations(
        self,
        employee_balance: float,
        expiring_soon: float,
        monthly_avg_overtime: float,
    ) -> List[str]:
        """
        Gera recomendações baseadas no saldo.

        Args:
            employee_balance: Saldo atual
            expiring_soon: Horas expirando em breve
            monthly_avg_overtime: Média mensal de horas extras

        Returns:
            Lista de recomendações
        """
        recommendations = []

        if expiring_soon > 0:
            recommendations.append(
                f"Agendar compensação de {expiring_soon:.1f}h " "que expiram em breve"
            )

        if employee_balance > 40:
            recommendations.append("Considerar folga compensatória para reduzir saldo elevado")

        if employee_balance < -10:
            recommendations.append("Saldo negativo - considerar horas extras para compensar")

        if monthly_avg_overtime > 30:
            recommendations.append(
                "Média de horas extras alta - avaliar necessidade de contratação"
            )

        return recommendations


# Singleton
time_bank_service = TimeBankService()
