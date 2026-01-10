"""
domains/hr/entities/enums.py - HR ENUMS
=======================================
Enterprise HR enumerations for employee management
"""

from enum import Enum
from typing import List
from decimal import Decimal


class EmploymentType(str, Enum):
    """Tipo de contratacao."""

    CLT = "clt"                     # Consolidacao das Leis do Trabalho
    PJ = "pj"                       # Pessoa Juridica
    TEMPORARY = "temporary"         # Temporario
    INTERN = "intern"               # Estagiario
    APPRENTICE = "apprentice"       # Jovem Aprendiz
    OUTSOURCED = "outsourced"       # Terceirizado
    AUTONOMOUS = "autonomous"       # Autonomo

    def requires_esocial(self) -> bool:
        """Verifica se requer registro no eSocial."""
        return self in [self.CLT, self.TEMPORARY, self.INTERN, self.APPRENTICE]

    def has_vacation_rights(self) -> bool:
        """Verifica se tem direito a ferias."""
        return self in [self.CLT, self.TEMPORARY]

    def has_13th_salary(self) -> bool:
        """Verifica se tem direito a 13o salario."""
        return self in [self.CLT, self.TEMPORARY, self.APPRENTICE]


class EmployeeStatus(str, Enum):
    """Status do colaborador."""

    ACTIVE = "active"
    ON_LEAVE = "on_leave"           # Afastado
    VACATION = "vacation"           # Ferias
    MATERNITY_LEAVE = "maternity"   # Licenca maternidade
    PATERNITY_LEAVE = "paternity"   # Licenca paternidade
    SICK_LEAVE = "sick_leave"       # Auxilio doenca
    SUSPENDED = "suspended"         # Suspenso
    NOTICE_PERIOD = "notice_period" # Aviso previo
    TERMINATED = "terminated"       # Desligado
    RETIRED = "retired"             # Aposentado

    @classmethod
    def active_statuses(cls) -> List["EmployeeStatus"]:
        """Retorna status considerados ativos."""
        return [cls.ACTIVE, cls.ON_LEAVE, cls.VACATION,
                cls.MATERNITY_LEAVE, cls.PATERNITY_LEAVE]

    @classmethod
    def inactive_statuses(cls) -> List["EmployeeStatus"]:
        """Retorna status considerados inativos."""
        return [cls.TERMINATED, cls.RETIRED]

    def is_working(self) -> bool:
        """Verifica se esta trabalhando."""
        return self == self.ACTIVE

    def receives_salary(self) -> bool:
        """Verifica se recebe salario."""
        return self not in [self.TERMINATED, self.RETIRED, self.SUSPENDED]


class DepartmentType(str, Enum):
    """Tipo de departamento."""

    ADMINISTRATIVE = "administrative"
    COMMERCIAL = "commercial"
    FINANCIAL = "financial"
    HR = "hr"
    IT = "it"
    LEGAL = "legal"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    PRODUCTION = "production"
    PURCHASING = "purchasing"
    QUALITY = "quality"
    RESEARCH = "research"
    SUPPORT = "support"


class WorkScheduleType(str, Enum):
    """Tipo de jornada de trabalho."""

    FULL_TIME = "full_time"         # Tempo integral
    PART_TIME = "part_time"         # Meio periodo
    SHIFT = "shift"                 # Turno
    FLEXIBLE = "flexible"           # Flexivel
    HOME_OFFICE = "home_office"     # Home office
    HYBRID = "hybrid"               # Hibrido

    def weekly_hours(self) -> int:
        """Horas semanais padrao."""
        hours_map = {
            self.FULL_TIME: 44,
            self.PART_TIME: 22,
            self.SHIFT: 36,
            self.FLEXIBLE: 40,
            self.HOME_OFFICE: 40,
            self.HYBRID: 40
        }
        return hours_map.get(self, 44)


class PayrollEventType(str, Enum):
    """Tipo de evento de folha."""

    # Proventos
    SALARY = "salary"               # Salario base
    OVERTIME_50 = "overtime_50"     # Hora extra 50%
    OVERTIME_100 = "overtime_100"   # Hora extra 100%
    NIGHT_SHIFT = "night_shift"     # Adicional noturno
    HAZARD_PAY = "hazard_pay"       # Periculosidade
    UNHEALTHY_PAY = "unhealthy"     # Insalubridade
    COMMISSION = "commission"       # Comissao
    BONUS = "bonus"                 # Bonus
    VACATION_PAY = "vacation_pay"   # Ferias
    THIRTEENTH = "thirteenth"       # 13o salario
    PROFIT_SHARING = "profit_share" # PLR

    # Descontos
    INSS = "inss"                   # INSS
    IRRF = "irrf"                   # IRRF
    FGTS = "fgts"                   # FGTS
    UNION_FEE = "union_fee"         # Contribuicao sindical
    MEAL_DISCOUNT = "meal_discount" # Desconto refeicao
    TRANSPORT = "transport"         # Vale transporte (6%)
    HEALTH_PLAN = "health_plan"     # Plano de saude
    ABSENCE = "absence"             # Falta
    ADVANCE = "advance"             # Adiantamento
    LOAN = "loan"                   # Emprestimo consignado

    def is_earning(self) -> bool:
        """Verifica se e provento."""
        earnings = [
            self.SALARY, self.OVERTIME_50, self.OVERTIME_100,
            self.NIGHT_SHIFT, self.HAZARD_PAY, self.UNHEALTHY_PAY,
            self.COMMISSION, self.BONUS, self.VACATION_PAY,
            self.THIRTEENTH, self.PROFIT_SHARING
        ]
        return self in earnings

    def is_deduction(self) -> bool:
        """Verifica se e desconto."""
        return not self.is_earning()

    def is_mandatory(self) -> bool:
        """Verifica se e obrigatorio por lei."""
        return self in [self.INSS, self.IRRF, self.FGTS]


class TimeClockEventType(str, Enum):
    """Tipo de registro de ponto."""

    CLOCK_IN = "clock_in"           # Entrada
    CLOCK_OUT = "clock_out"         # Saida
    BREAK_START = "break_start"     # Inicio intervalo
    BREAK_END = "break_end"         # Fim intervalo
    OVERTIME_START = "overtime_in"  # Inicio hora extra
    OVERTIME_END = "overtime_out"   # Fim hora extra


class LeaveType(str, Enum):
    """Tipo de afastamento."""

    VACATION = "vacation"
    SICK_LEAVE = "sick_leave"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    BEREAVEMENT = "bereavement"     # Luto
    WEDDING = "wedding"             # Casamento
    BLOOD_DONATION = "blood"        # Doacao de sangue
    MILITARY = "military"           # Servico militar
    JURY_DUTY = "jury_duty"         # Juri
    STUDY = "study"                 # Licenca estudo
    UNPAID = "unpaid"               # Licenca sem vencimentos

    def max_days(self) -> int:
        """Dias maximos permitidos por lei."""
        days_map = {
            self.VACATION: 30,
            self.SICK_LEAVE: 15,  # Apos 15 dias, INSS assume
            self.MATERNITY: 120,
            self.PATERNITY: 20,  # Com cidadania empresarial
            self.BEREAVEMENT: 2,
            self.WEDDING: 3,
            self.BLOOD_DONATION: 1,
            self.MILITARY: 0,  # Indeterminado
            self.JURY_DUTY: 0,  # Indeterminado
            self.STUDY: 0,
            self.UNPAID: 0
        }
        return days_map.get(self, 0)

    def is_paid(self) -> bool:
        """Verifica se e remunerado."""
        return self != self.UNPAID


class TerminationType(str, Enum):
    """Tipo de desligamento."""

    RESIGNATION = "resignation"           # Pedido de demissao
    DISMISSAL_CAUSE = "dismissal_cause"   # Demissao por justa causa
    DISMISSAL_NO_CAUSE = "dismissal"      # Demissao sem justa causa
    MUTUAL_AGREEMENT = "mutual"           # Acordo mutuo (reforma trabalhista)
    CONTRACT_END = "contract_end"         # Termino de contrato
    RETIREMENT = "retirement"             # Aposentadoria
    DEATH = "death"                       # Falecimento

    def has_notice_period(self) -> bool:
        """Verifica se tem aviso previo."""
        return self in [
            self.RESIGNATION, self.DISMISSAL_NO_CAUSE, self.MUTUAL_AGREEMENT
        ]

    def receives_fgts_penalty(self) -> bool:
        """Verifica se recebe multa FGTS 40%."""
        return self in [self.DISMISSAL_NO_CAUSE]

    def fgts_penalty_percent(self) -> Decimal:
        """Percentual da multa FGTS."""
        if self == self.DISMISSAL_NO_CAUSE:
            return Decimal("40")
        if self == self.MUTUAL_AGREEMENT:
            return Decimal("20")
        return Decimal("0")
