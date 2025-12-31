"""Modelo WorkSchedule - Jornada de Trabalho.

Define os horários e regras de trabalho para funcionários.
Conformidade com CLT e acordos coletivos.
"""

import uuid
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Date,
    Time,
    Integer,
    String,
    Text,
    Numeric,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base

if TYPE_CHECKING:
    from .time_entry import TimeEntry


class ScheduleType(str, Enum):
    """Tipo de escala/jornada."""

    CLT_44H = "clt_44h"  # 44h semanais padrão
    CLT_40H = "clt_40h"  # 40h semanais (banco/comercial)
    ESCALA_6X1 = "escala_6x1"  # 6 dias trabalhados, 1 folga
    ESCALA_5X2 = "escala_5x2"  # 5 dias trabalhados, 2 folgas
    ESCALA_12X36 = "escala_12x36"  # 12h trabalho, 36h descanso
    ESCALA_24X72 = "escala_24x72"  # 24h trabalho, 72h descanso
    TURNO_REVEZAMENTO = "turno_revezamento"  # Turnos rotativos
    HORARIO_FLEXIVEL = "horario_flexivel"  # Horário flexível
    MEIO_PERIODO = "meio_periodo"  # Part-time
    INTERMITENTE = "intermitente"  # Trabalho intermitente
    TELETRABALHO = "teletrabalho"  # Home office
    HIBRIDO = "hibrido"  # Híbrido
    PERSONALIZADO = "personalizado"  # Customizado


class ScheduleStatus(str, Enum):
    """Status da jornada."""

    ATIVO = "ativo"
    INATIVO = "inativo"
    SUSPENSO = "suspenso"
    FERIAS = "ferias"
    AFASTADO = "afastado"
    DESLIGADO = "desligado"


class DayOfWeek(str, Enum):
    """Dias da semana."""

    SEGUNDA = "segunda"
    TERCA = "terca"
    QUARTA = "quarta"
    QUINTA = "quinta"
    SEXTA = "sexta"
    SABADO = "sabado"
    DOMINGO = "domingo"


class WorkSchedule(Base):
    """Modelo de Jornada de Trabalho.

    Define os horários, intervalos e regras de trabalho
    de cada funcionário. Segue as normas da CLT.
    """

    __tablename__ = "work_schedules"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Tipo e status
    schedule_type: Mapped[ScheduleType] = mapped_column(
        String(30), default=ScheduleType.CLT_44H
    )
    status: Mapped[ScheduleStatus] = mapped_column(
        String(20), default=ScheduleStatus.ATIVO
    )

    # Funcionário (pode ser template sem funcionário)
    employee_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    employee_name: Mapped[Optional[str]] = mapped_column(String(200))
    employee_registration: Mapped[Optional[str]] = mapped_column(String(50))
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)

    # Departamento
    department_id: Mapped[Optional[str]] = mapped_column(String(50))
    department_name: Mapped[Optional[str]] = mapped_column(String(100))

    # Carga horária semanal (em minutos)
    weekly_hours_minutes: Mapped[int] = mapped_column(Integer, default=2640)  # 44h
    daily_hours_minutes: Mapped[int] = mapped_column(Integer, default=528)  # 8h48min
    max_daily_hours_minutes: Mapped[int] = mapped_column(Integer, default=600)  # 10h

    # Horário padrão (segunda a sexta)
    default_entry_time: Mapped[Optional[time]] = mapped_column(Time)
    default_exit_time: Mapped[Optional[time]] = mapped_column(Time)
    default_break_start: Mapped[Optional[time]] = mapped_column(Time)
    default_break_end: Mapped[Optional[time]] = mapped_column(Time)
    break_duration_minutes: Mapped[int] = mapped_column(Integer, default=60)

    # Horários por dia da semana (JSON)
    # Formato: {"segunda": {"entry": "08:00", "exit": "17:48", "break_start": "12:00", "break_end": "13:00"}}
    daily_schedule: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Dias trabalhados
    work_days: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), default=list
    )
    days_off: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), default=list
    )

    # Tolerâncias (em minutos)
    entry_tolerance_minutes: Mapped[int] = mapped_column(Integer, default=10)
    exit_tolerance_minutes: Mapped[int] = mapped_column(Integer, default=10)
    break_tolerance_minutes: Mapped[int] = mapped_column(Integer, default=5)

    # Regras de hora extra
    overtime_requires_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    max_overtime_daily_minutes: Mapped[int] = mapped_column(Integer, default=120)
    max_overtime_weekly_minutes: Mapped[int] = mapped_column(Integer, default=600)
    overtime_multiplier_50: Mapped[Decimal] = mapped_column(
        Numeric(4, 2), default=Decimal("1.50")
    )
    overtime_multiplier_100: Mapped[Decimal] = mapped_column(
        Numeric(4, 2), default=Decimal("2.00")
    )
    use_time_bank: Mapped[bool] = mapped_column(Boolean, default=False)

    # Adicional noturno (22h às 05h)
    night_shift_start: Mapped[time] = mapped_column(Time, default=time(22, 0))
    night_shift_end: Mapped[time] = mapped_column(Time, default=time(5, 0))
    night_shift_multiplier: Mapped[Decimal] = mapped_column(
        Numeric(4, 2), default=Decimal("1.20")
    )
    night_hour_reduction: Mapped[bool] = mapped_column(Boolean, default=True)

    # Intervalos obrigatórios (CLT)
    min_break_4h_minutes: Mapped[int] = mapped_column(Integer, default=15)
    min_break_6h_minutes: Mapped[int] = mapped_column(Integer, default=60)
    min_rest_between_shifts_hours: Mapped[int] = mapped_column(Integer, default=11)

    # Banco de horas
    time_bank_balance_minutes: Mapped[int] = mapped_column(Integer, default=0)
    time_bank_expiry_months: Mapped[int] = mapped_column(Integer, default=6)
    time_bank_max_positive_hours: Mapped[int] = mapped_column(Integer, default=40)
    time_bank_max_negative_hours: Mapped[int] = mapped_column(Integer, default=20)

    # Geolocalização obrigatória
    require_geolocation: Mapped[bool] = mapped_column(Boolean, default=False)
    allowed_locations: Mapped[Optional[List[dict]]] = mapped_column(
        JSONB, default=list
    )
    max_distance_meters: Mapped[int] = mapped_column(Integer, default=100)

    # Biometria
    require_biometric: Mapped[bool] = mapped_column(Boolean, default=True)
    min_biometric_score: Mapped[int] = mapped_column(Integer, default=80)
    require_face_match: Mapped[bool] = mapped_column(Boolean, default=False)
    require_liveness: Mapped[bool] = mapped_column(Boolean, default=True)

    # Feriados
    consider_holidays: Mapped[bool] = mapped_column(Boolean, default=True)
    holiday_calendar_id: Mapped[Optional[str]] = mapped_column(String(50))

    # Acordo coletivo
    collective_agreement_id: Mapped[Optional[str]] = mapped_column(String(50))
    collective_agreement_name: Mapped[Optional[str]] = mapped_column(String(200))

    # Validade
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_until: Mapped[Optional[date]] = mapped_column(Date)

    # Condomínio/Local
    condominium_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    condominium_name: Mapped[Optional[str]] = mapped_column(String(200))

    # Observações e metadados
    notes: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Controle
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(String(50))

    # Índices
    __table_args__ = (
        Index("ix_work_schedules_employee_status", "employee_id", "status"),
        Index("ix_work_schedules_type_status", "schedule_type", "status"),
    )

    def __init__(self, **kwargs) -> None:
        """Inicializa a jornada de trabalho."""
        super().__init__(**kwargs)
        if not self.code:
            self.code = self._generate_code()
        if not self.work_days:
            self._set_default_work_days()

    def _generate_code(self) -> str:
        """Gera código único da jornada."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"JOR-{timestamp}"

    def _set_default_work_days(self) -> None:
        """Define dias de trabalho padrão baseado no tipo."""
        if self.schedule_type in [
            ScheduleType.CLT_44H,
            ScheduleType.CLT_40H,
            ScheduleType.ESCALA_5X2,
        ]:
            self.work_days = [
                DayOfWeek.SEGUNDA.value,
                DayOfWeek.TERCA.value,
                DayOfWeek.QUARTA.value,
                DayOfWeek.QUINTA.value,
                DayOfWeek.SEXTA.value,
            ]
            self.days_off = [DayOfWeek.SABADO.value, DayOfWeek.DOMINGO.value]
        elif self.schedule_type == ScheduleType.ESCALA_6X1:
            self.work_days = [
                DayOfWeek.SEGUNDA.value,
                DayOfWeek.TERCA.value,
                DayOfWeek.QUARTA.value,
                DayOfWeek.QUINTA.value,
                DayOfWeek.SEXTA.value,
                DayOfWeek.SABADO.value,
            ]
            self.days_off = [DayOfWeek.DOMINGO.value]

    def get_schedule_for_day(self, day: DayOfWeek) -> Optional[dict]:
        """Retorna o horário para um dia específico.

        Args:
            day: Dia da semana

        Returns:
            dict: Horários do dia ou None se folga
        """
        if not self.daily_schedule:
            if day.value not in (self.work_days or []):
                return None
            return {
                "entry": self.default_entry_time.strftime("%H:%M")
                if self.default_entry_time
                else None,
                "exit": self.default_exit_time.strftime("%H:%M")
                if self.default_exit_time
                else None,
                "break_start": self.default_break_start.strftime("%H:%M")
                if self.default_break_start
                else None,
                "break_end": self.default_break_end.strftime("%H:%M")
                if self.default_break_end
                else None,
            }
        return self.daily_schedule.get(day.value)

    def is_work_day(self, check_date: date) -> bool:
        """Verifica se é dia de trabalho.

        Args:
            check_date: Data a verificar

        Returns:
            bool: True se é dia de trabalho
        """
        weekday = check_date.weekday()
        day_map = {
            0: DayOfWeek.SEGUNDA,
            1: DayOfWeek.TERCA,
            2: DayOfWeek.QUARTA,
            3: DayOfWeek.QUINTA,
            4: DayOfWeek.SEXTA,
            5: DayOfWeek.SABADO,
            6: DayOfWeek.DOMINGO,
        }
        day = day_map[weekday]
        return day.value in (self.work_days or [])

    def get_expected_times(self, check_date: date) -> Optional[dict]:
        """Retorna horários esperados para uma data.

        Args:
            check_date: Data a verificar

        Returns:
            dict: Horários esperados ou None
        """
        if not self.is_work_day(check_date):
            return None

        weekday = check_date.weekday()
        day_map = {
            0: DayOfWeek.SEGUNDA,
            1: DayOfWeek.TERCA,
            2: DayOfWeek.QUARTA,
            3: DayOfWeek.QUINTA,
            4: DayOfWeek.SEXTA,
            5: DayOfWeek.SABADO,
            6: DayOfWeek.DOMINGO,
        }
        day = day_map[weekday]
        return self.get_schedule_for_day(day)

    def calculate_expected_hours(self, check_date: date) -> int:
        """Calcula horas esperadas para uma data (em minutos).

        Args:
            check_date: Data a verificar

        Returns:
            int: Minutos esperados
        """
        schedule = self.get_expected_times(check_date)
        if not schedule:
            return 0

        entry = schedule.get("entry")
        exit_time = schedule.get("exit")
        break_start = schedule.get("break_start")
        break_end = schedule.get("break_end")

        if not entry or not exit_time:
            return self.daily_hours_minutes

        # Calcula diferença
        entry_dt = datetime.strptime(entry, "%H:%M")
        exit_dt = datetime.strptime(exit_time, "%H:%M")
        total_minutes = int((exit_dt - entry_dt).total_seconds() / 60)

        # Desconta intervalo
        if break_start and break_end:
            break_start_dt = datetime.strptime(break_start, "%H:%M")
            break_end_dt = datetime.strptime(break_end, "%H:%M")
            break_minutes = int((break_end_dt - break_start_dt).total_seconds() / 60)
            total_minutes -= break_minutes

        return total_minutes

    def validate_clt_rules(self) -> List[str]:
        """Valida regras da CLT.

        Returns:
            List[str]: Lista de violações encontradas
        """
        violations = []

        # Limite semanal (44h normais + até 10h extras)
        if self.weekly_hours_minutes > 3240:  # 54h
            violations.append(
                "Carga horária semanal excede o limite legal de 54h (44h + 10h extras)"
            )

        # Limite diário (8h normais + até 2h extras)
        if self.max_daily_hours_minutes > 600:  # 10h
            violations.append(
                "Carga horária diária máxima excede o limite legal de 10h"
            )

        # Descanso entre jornadas (11h)
        if self.min_rest_between_shifts_hours < 11:
            violations.append(
                "Descanso entre jornadas inferior ao mínimo de 11h"
            )

        # Intervalo obrigatório (>6h = 1h de intervalo)
        if self.daily_hours_minutes > 360 and self.break_duration_minutes < 60:
            violations.append(
                "Jornada superior a 6h requer intervalo mínimo de 1h"
            )

        return violations

    def update_time_bank(self, minutes: int) -> None:
        """Atualiza saldo do banco de horas.

        Args:
            minutes: Minutos a adicionar (positivo) ou subtrair (negativo)
        """
        self.time_bank_balance_minutes += minutes

        # Limites
        max_positive = self.time_bank_max_positive_hours * 60
        max_negative = -self.time_bank_max_negative_hours * 60

        if self.time_bank_balance_minutes > max_positive:
            self.time_bank_balance_minutes = max_positive
        elif self.time_bank_balance_minutes < max_negative:
            self.time_bank_balance_minutes = max_negative

    def is_within_allowed_location(
        self, latitude: float, longitude: float
    ) -> bool:
        """Verifica se coordenadas estão em área permitida.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            bool: True se dentro da área permitida
        """
        if not self.require_geolocation:
            return True

        if not self.allowed_locations:
            return True

        from math import radians, sin, cos, sqrt, atan2

        for location in self.allowed_locations:
            loc_lat = location.get("latitude", 0)
            loc_lon = location.get("longitude", 0)
            max_dist = location.get("max_distance", self.max_distance_meters)

            # Haversine
            r = 6371000  # Raio da Terra em metros
            lat1, lat2 = radians(latitude), radians(loc_lat)
            dlat = radians(loc_lat - latitude)
            dlon = radians(loc_lon - longitude)

            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = r * c

            if distance <= max_dist:
                return True

        return False

    def deactivate(self) -> None:
        """Desativa a jornada."""
        self.status = ScheduleStatus.INATIVO

    def activate(self) -> None:
        """Ativa a jornada."""
        self.status = ScheduleStatus.ATIVO

    def suspend(self, reason: str = None) -> None:
        """Suspende a jornada.

        Args:
            reason: Motivo da suspensão
        """
        self.status = ScheduleStatus.SUSPENSO
        if reason:
            self.notes = f"Suspenso: {reason}"

    def set_vacation(self) -> None:
        """Define como férias."""
        self.status = ScheduleStatus.FERIAS

    def soft_delete(self) -> None:
        """Soft delete da jornada."""
        self.is_deleted = True
        self.status = ScheduleStatus.INATIVO

    @property
    def weekly_hours(self) -> float:
        """Retorna carga horária semanal em horas."""
        return self.weekly_hours_minutes / 60

    @property
    def daily_hours(self) -> float:
        """Retorna carga horária diária em horas."""
        return self.daily_hours_minutes / 60

    @property
    def time_bank_hours(self) -> float:
        """Retorna saldo do banco de horas."""
        return self.time_bank_balance_minutes / 60

    @property
    def is_valid(self) -> bool:
        """Verifica se jornada está válida."""
        today = date.today()
        if self.valid_from and self.valid_from > today:
            return False
        if self.valid_until and self.valid_until < today:
            return False
        return self.status == ScheduleStatus.ATIVO and not self.is_deleted

    @property
    def schedule_type_display(self) -> str:
        """Retorna tipo para exibição."""
        display_map = {
            ScheduleType.CLT_44H: "CLT 44h semanais",
            ScheduleType.CLT_40H: "CLT 40h semanais",
            ScheduleType.ESCALA_6X1: "Escala 6x1",
            ScheduleType.ESCALA_5X2: "Escala 5x2",
            ScheduleType.ESCALA_12X36: "Escala 12x36",
            ScheduleType.ESCALA_24X72: "Escala 24x72",
            ScheduleType.TURNO_REVEZAMENTO: "Turno de Revezamento",
            ScheduleType.HORARIO_FLEXIVEL: "Horário Flexível",
            ScheduleType.MEIO_PERIODO: "Meio Período",
            ScheduleType.INTERMITENTE: "Intermitente",
            ScheduleType.TELETRABALHO: "Teletrabalho",
            ScheduleType.HIBRIDO: "Híbrido",
            ScheduleType.PERSONALIZADO: "Personalizado",
        }
        return display_map.get(self.schedule_type, self.schedule_type.value)

    def __repr__(self) -> str:
        """Representação do objeto."""
        return f"<WorkSchedule {self.code}: {self.name} ({self.schedule_type_display})>"
