"""Serviço de cálculo de horas trabalhadas."""

from datetime import date, time
from decimal import Decimal
from typing import List, Optional, Tuple
import logging

from modules.hr.time_tracking.models import (
    TimeEntry,
    WorkSchedule,
    EntryType,
)

logger = logging.getLogger(__name__)


class TimeCalculationService:
    """Serviço para cálculo de horas trabalhadas conforme CLT."""

    # Constantes CLT
    NIGHT_START = time(22, 0)  # Início do período noturno
    NIGHT_END = time(5, 0)  # Fim do período noturno
    NIGHT_HOUR_REDUCTION = 7 / 60  # 52min30s = 1h noturna
    NIGHT_BONUS_PERCENT = Decimal("0.20")  # 20% adicional noturno

    OVERTIME_50_MULTIPLIER = Decimal("1.50")
    OVERTIME_100_MULTIPLIER = Decimal("2.00")

    MAX_DAILY_HOURS = 10  # Máximo com hora extra
    MAX_WEEKLY_HOURS = 44  # Jornada semanal CLT
    MIN_REST_BETWEEN_SHIFTS = 11  # Horas mínimas de descanso

    def calculate_worked_hours(  # pylint: disable=too-many-locals
        self,
        entries: List[TimeEntry],
        schedule: WorkSchedule = None,
    ) -> dict:
        """Calcula horas trabalhadas a partir dos registros de ponto.

        Args:
            entries: Lista de registros de ponto do dia
            schedule: Jornada de trabalho do funcionário

        Returns:
            Dict com detalhes das horas calculadas
        """
        if not entries:
            return self._empty_result()

        entries_sorted = sorted(entries, key=lambda e: e.entry_time)

        # Separa entradas e saídas
        clock_ins = [e for e in entries_sorted if e.entry_type == EntryType.ENTRADA]
        clock_outs = [e for e in entries_sorted if e.entry_type == EntryType.SAIDA]
        break_starts = [
            e for e in entries_sorted if e.entry_type == EntryType.SAIDA_INTERVALO
        ]
        break_ends = [
            e for e in entries_sorted if e.entry_type == EntryType.RETORNO_INTERVALO
        ]

        if not clock_ins or not clock_outs:
            return self._empty_result()

        # Calcula tempo bruto
        first_in = clock_ins[0].entry_time
        last_out = clock_outs[-1].entry_time

        total_minutes = self._time_diff_minutes(first_in, last_out)

        # Calcula tempo de intervalo
        break_minutes = self._calculate_break_minutes(break_starts, break_ends)

        # Tempo trabalhado líquido
        worked_minutes = total_minutes - break_minutes

        # Horas noturnas
        night_minutes = self._calculate_night_minutes(
            first_in, last_out, break_starts, break_ends
        )

        # Horas esperadas do dia
        expected_minutes = 0
        if schedule:
            entry_date = entries[0].entry_date
            day_schedule = schedule.get_schedule_for_day(entry_date)
            if day_schedule:
                expected_minutes = day_schedule.get("daily_minutes", 0)

        # Diferença (positivo = extra, negativo = débito)
        balance_minutes = worked_minutes - expected_minutes

        # Horas extras
        overtime_minutes = max(0, balance_minutes)
        deficit_minutes = max(0, -balance_minutes)

        # Atraso na entrada
        late_minutes = 0
        if schedule:
            expected_start = self._get_expected_start(schedule, entries[0].entry_date)
            if expected_start and first_in > expected_start:
                late_minutes = self._time_diff_minutes(expected_start, first_in)

        # Saída antecipada
        early_departure_minutes = 0
        if schedule:
            expected_end = self._get_expected_end(schedule, entries[0].entry_date)
            if expected_end and last_out < expected_end:
                early_departure_minutes = self._time_diff_minutes(last_out, expected_end)

        return {
            "worked_minutes": worked_minutes,
            "expected_minutes": expected_minutes,
            "balance_minutes": balance_minutes,
            "overtime_minutes": overtime_minutes,
            "deficit_minutes": deficit_minutes,
            "night_minutes": night_minutes,
            "break_minutes": break_minutes,
            "late_minutes": late_minutes,
            "early_departure_minutes": early_departure_minutes,
            "first_entry": first_in.isoformat(),
            "last_exit": last_out.isoformat(),
            "total_entries": len(entries),
        }

    def calculate_overtime_type(
        self,
        overtime_minutes: int,
        work_date: date,
        schedule: WorkSchedule = None,
    ) -> Tuple[int, int]:
        """Determina tipo de hora extra (50% ou 100%).

        Returns:
            Tuple: (minutos_50, minutos_100)
        """
        if overtime_minutes <= 0:
            return (0, 0)

        is_sunday = work_date.weekday() == 6
        is_holiday = self._is_holiday(work_date)
        is_rest_day = False

        if schedule:
            is_rest_day = not schedule.is_work_day(work_date)

        # Domingo, feriado ou folga = 100%
        if is_sunday or is_holiday or is_rest_day:
            return (0, overtime_minutes)

        # Dias normais = 50% até 2h, depois 100%
        limit_50 = 120  # 2 horas
        if overtime_minutes <= limit_50:
            return (overtime_minutes, 0)
        return (limit_50, overtime_minutes - limit_50)

    def calculate_night_bonus(
        self,
        night_minutes: int,
        hourly_rate: Decimal,
    ) -> Decimal:
        """Calcula adicional noturno.

        A hora noturna é reduzida (52min30s = 1h) e tem adicional de 20%.
        """
        if night_minutes <= 0:
            return Decimal("0")

        # Converte para horas noturnas reduzidas
        night_hours = Decimal(night_minutes) / 60
        reduced_hours = night_hours / Decimal(str(self.NIGHT_HOUR_REDUCTION))

        # Calcula adicional
        bonus = reduced_hours * hourly_rate * self.NIGHT_BONUS_PERCENT

        return round(bonus, 2)

    def calculate_overtime_value(
        self,
        overtime_50_minutes: int,
        overtime_100_minutes: int,
        hourly_rate: Decimal,
    ) -> Tuple[Decimal, Decimal]:
        """Calcula valor das horas extras.

        Returns:
            Tuple: (valor_50, valor_100)
        """
        hours_50 = Decimal(overtime_50_minutes) / 60
        hours_100 = Decimal(overtime_100_minutes) / 60

        value_50 = hours_50 * hourly_rate * self.OVERTIME_50_MULTIPLIER
        value_100 = hours_100 * hourly_rate * self.OVERTIME_100_MULTIPLIER

        return (round(value_50, 2), round(value_100, 2))

    def calculate_dsr(
        self,
        worked_days: int,
        expected_days: int,
        late_count: int,
        absence_count: int,
        max_late_for_dsr: int = 0,
    ) -> Tuple[bool, str]:
        """Verifica direito ao DSR (Descanso Semanal Remunerado).

        Conforme CLT, perde DSR se houver falta injustificada ou
        atrasos que ultrapassem o limite tolerado.

        Returns:
            Tuple: (tem_direito, motivo_perda)
        """
        if absence_count > 0:
            return (False, f"Falta(s) injustificada(s): {absence_count}")

        if max_late_for_dsr > 0 and late_count > max_late_for_dsr:  # pylint: disable=chained-comparison
            return (False, f"Atrasos ({late_count}) excedem limite ({max_late_for_dsr})")

        if worked_days < expected_days:
            return (False, f"Dias trabalhados ({worked_days}) abaixo do esperado ({expected_days})")

        return (True, "")

    def validate_clt_rules(
        self,
        worked_minutes: int,
        break_minutes: int,
        last_exit_yesterday: time = None,
        first_entry_today: time = None,
    ) -> List[str]:
        """Valida regras CLT de jornada.

        Returns:
            Lista de violações encontradas
        """
        violations = []

        # Máximo 10h diárias (8h + 2h extra)
        if worked_minutes > self.MAX_DAILY_HOURS * 60:
            violations.append(
                f"Jornada diária ({worked_minutes // 60}h) excede limite de {self.MAX_DAILY_HOURS}h"
            )

        # Intervalo mínimo para jornada > 6h
        if worked_minutes > 360 and break_minutes < 60:  # 6h
            violations.append(
                f"Intervalo ({break_minutes}min) abaixo do mínimo de 60min para jornada > 6h"
            )

        # Intervalo mínimo para jornada 4-6h
        if 240 < worked_minutes <= 360 and break_minutes < 15:
            violations.append(
                f"Intervalo ({break_minutes}min) abaixo do mínimo de 15min para jornada 4-6h"
            )

        # Descanso entre jornadas (11h)
        if last_exit_yesterday and first_entry_today:
            rest_minutes = self._calculate_rest_between_shifts(
                last_exit_yesterday, first_entry_today
            )
            if rest_minutes < self.MIN_REST_BETWEEN_SHIFTS * 60:
                violations.append(
                    f"Descanso entre jornadas ({rest_minutes // 60}h) "
                    f"abaixo do mínimo de {self.MIN_REST_BETWEEN_SHIFTS}h"
                )

        return violations

    def pair_entries(
        self,
        entries: List[TimeEntry],
    ) -> List[dict]:
        """Agrupa registros em pares (entrada/saída).

        Returns:
            Lista de períodos trabalhados
        """
        periods = []
        entries_sorted = sorted(entries, key=lambda e: e.entry_time)

        pending_in = None
        pending_break_out = None

        for entry in entries_sorted:
            if entry.entry_type == EntryType.ENTRADA:
                if pending_in:
                    # Entrada sem saída anterior - anomalia
                    periods.append({
                        "start": pending_in.entry_time,
                        "end": None,
                        "type": "work",
                        "incomplete": True,
                    })
                pending_in = entry

            elif entry.entry_type == EntryType.SAIDA:
                if pending_in:
                    periods.append({
                        "start": pending_in.entry_time,
                        "end": entry.entry_time,
                        "type": "work",
                        "incomplete": False,
                    })
                    pending_in = None

            elif entry.entry_type == EntryType.SAIDA_INTERVALO:
                pending_break_out = entry

            elif entry.entry_type == EntryType.RETORNO_INTERVALO:
                if pending_break_out:
                    periods.append({
                        "start": pending_break_out.entry_time,
                        "end": entry.entry_time,
                        "type": "break",
                        "incomplete": False,
                    })
                    pending_break_out = None

        # Verifica pendências
        if pending_in:
            periods.append({
                "start": pending_in.entry_time,
                "end": None,
                "type": "work",
                "incomplete": True,
            })

        return periods

    def _time_diff_minutes(self, start: time, end: time) -> int:
        """Calcula diferença em minutos entre dois horários."""
        start_minutes = start.hour * 60 + start.minute
        end_minutes = end.hour * 60 + end.minute

        # Se cruzou meia-noite
        if end_minutes < start_minutes:
            end_minutes += 24 * 60

        return end_minutes - start_minutes

    def _calculate_break_minutes(
        self,
        break_starts: List[TimeEntry],
        break_ends: List[TimeEntry],
    ) -> int:
        """Calcula total de minutos de intervalo."""
        total = 0

        for i, start in enumerate(break_starts):
            if i < len(break_ends):
                total += self._time_diff_minutes(
                    start.entry_time, break_ends[i].entry_time
                )

        return total

    def _calculate_night_minutes(  # pylint: disable=too-many-locals
        self,
        first_in: time,
        last_out: time,
        break_starts: List[TimeEntry],
        break_ends: List[TimeEntry],
    ) -> int:
        """Calcula minutos trabalhados no período noturno (22h-05h)."""
        night_minutes = 0

        # Período noturno: 22:00 - 05:00 (7 horas = 420 minutos)
        # Simplificação: calcula interseção com período noturno

        first_minutes = first_in.hour * 60 + first_in.minute
        last_minutes = last_out.hour * 60 + last_out.minute

        # Ajuste para cruzar meia-noite
        if last_minutes < first_minutes:
            last_minutes += 24 * 60

        # Período noturno em minutos
        night_start_minutes = 22 * 60  # 22:00
        night_end_minutes = 29 * 60  # 05:00 do dia seguinte (24 + 5)

        # Calcula interseção
        work_start = first_minutes
        work_end = last_minutes

        # Primeiro período noturno (22:00 - 24:00 do mesmo dia)
        if work_start < 24 * 60 and work_end > night_start_minutes:
            overlap_start = max(work_start, night_start_minutes)
            overlap_end = min(work_end, 24 * 60)
            if overlap_end > overlap_start:
                night_minutes += overlap_end - overlap_start

        # Segundo período noturno (00:00 - 05:00 do dia seguinte)
        if work_end > 24 * 60:
            adjusted_start = max(work_start, 24 * 60)
            adjusted_end = min(work_end, night_end_minutes)
            if adjusted_end > adjusted_start:
                night_minutes += adjusted_end - adjusted_start

        # Desconta intervalos noturnos
        for i, start in enumerate(break_starts):
            if i < len(break_ends):
                break_night = self._calculate_night_in_period(
                    start.entry_time, break_ends[i].entry_time
                )
                night_minutes -= break_night

        return max(0, night_minutes)

    def _calculate_night_in_period(self, start: time, end: time) -> int:
        """Calcula minutos noturnos em um período específico."""
        # Simplificação para intervalos curtos
        start_minutes = start.hour * 60 + start.minute
        end_minutes = end.hour * 60 + end.minute

        if end_minutes < start_minutes:
            end_minutes += 24 * 60

        night_minutes = 0
        for m in range(start_minutes, end_minutes):
            hour = (m // 60) % 24
            if hour >= 22 or hour < 5:
                night_minutes += 1

        return night_minutes

    def _get_expected_start(
        self,
        schedule: WorkSchedule,
        work_date: date,
    ) -> Optional[time]:
        """Obtém horário esperado de entrada."""
        day_schedule = schedule.get_schedule_for_day(work_date)
        if day_schedule:
            return day_schedule.get("start_time")
        return None

    def _get_expected_end(
        self,
        schedule: WorkSchedule,
        work_date: date,
    ) -> Optional[time]:
        """Obtém horário esperado de saída."""
        day_schedule = schedule.get_schedule_for_day(work_date)
        if day_schedule:
            return day_schedule.get("end_time")
        return None

    def _calculate_rest_between_shifts(
        self,
        last_exit: time,
        first_entry: time,
    ) -> int:
        """Calcula tempo de descanso entre jornadas."""
        exit_minutes = last_exit.hour * 60 + last_exit.minute
        entry_minutes = first_entry.hour * 60 + first_entry.minute

        # Assume que a entrada é no dia seguinte
        rest_minutes = (24 * 60 - exit_minutes) + entry_minutes

        return rest_minutes

    def _is_holiday(self, check_date: date) -> bool:
        """Verifica se é feriado (simplificado).

        TODO: Integrar com tabela de feriados.
        """
        # Feriados nacionais fixos
        fixed_holidays = [
            (1, 1),   # Ano Novo
            (4, 21),  # Tiradentes
            (5, 1),   # Dia do Trabalho
            (9, 7),   # Independência
            (10, 12), # Nossa Senhora
            (11, 2),  # Finados
            (11, 15), # Proclamação da República
            (12, 25), # Natal
        ]

        return (check_date.month, check_date.day) in fixed_holidays

    def _empty_result(self) -> dict:
        """Retorna resultado vazio."""
        return {
            "worked_minutes": 0,
            "expected_minutes": 0,
            "balance_minutes": 0,
            "overtime_minutes": 0,
            "deficit_minutes": 0,
            "night_minutes": 0,
            "break_minutes": 0,
            "late_minutes": 0,
            "early_departure_minutes": 0,
            "first_entry": None,
            "last_exit": None,
            "total_entries": 0,
        }
