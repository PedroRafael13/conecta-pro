"""
domains/hr/entities/employee.py - EMPLOYEE ENTITY
=================================================
Enterprise employee entity with Brazilian labor law compliance
"""

from typing import Dict, List, Optional, Any, NewType
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from .enums import (
    EmploymentType,
    EmployeeStatus,
    WorkScheduleType,
    LeaveType,
    TerminationType
)

# Strong typing for domain identifiers
EmployeeId = NewType('EmployeeId', UUID)
DepartmentId = NewType('DepartmentId', UUID)
PositionId = NewType('PositionId', UUID)


class Address(BaseModel):
    """Endereco - Value Object."""

    model_config = ConfigDict(frozen=True)

    street: str = Field(..., min_length=3, max_length=200)
    number: str = Field(..., max_length=20)
    complement: Optional[str] = Field(None, max_length=100)
    neighborhood: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., pattern=r"^[A-Z]{2}$")
    postal_code: str = Field(..., pattern=r"^\d{5}-?\d{3}$")
    country: str = Field(default="BR", pattern=r"^[A-Z]{2}$")


class BankAccount(BaseModel):
    """Conta bancaria - Value Object."""

    model_config = ConfigDict(frozen=True)

    bank_code: str = Field(..., pattern=r"^\d{3}$")
    bank_name: str = Field(..., min_length=2, max_length=100)
    agency: str = Field(..., pattern=r"^\d{4}-?\d?$")
    account_number: str = Field(..., pattern=r"^\d{5,12}-?\d?$")
    account_type: str = Field(..., pattern=r"^(corrente|poupanca)$")
    pix_key: Optional[str] = None


class EmergencyContact(BaseModel):
    """Contato de emergencia - Value Object."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=3, max_length=100)
    relationship: str = Field(..., min_length=2, max_length=50)
    phone: str = Field(..., pattern=r"^\(\d{2}\)\s?\d{4,5}-?\d{4}$")
    secondary_phone: Optional[str] = None


class Dependent(BaseModel):
    """Dependente - Value Object."""

    model_config = ConfigDict(frozen=True)

    dependent_id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=3, max_length=100)
    relationship: str = Field(..., min_length=2, max_length=50)
    cpf: str = Field(..., pattern=r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$")
    birth_date: date
    is_ir_dependent: bool = Field(default=False)  # Dependente para IR
    is_health_plan: bool = Field(default=False)   # Incluso no plano de saude

    @property
    def age(self) -> int:
        """Calcula idade do dependente."""
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


class LeaveRecord(BaseModel):
    """Registro de afastamento."""

    leave_id: UUID = Field(default_factory=uuid4)
    leave_type: LeaveType
    start_date: date
    end_date: date
    days: int = Field(..., ge=1)
    reason: str = Field(..., min_length=5, max_length=500)
    medical_certificate: Optional[str] = None  # CID
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    status: str = Field(default="pending")  # pending, approved, rejected


class EmployeeEntity(BaseModel):
    """
    Entidade de colaborador.

    Implementa regras trabalhistas brasileiras e
    gestao completa do ciclo de vida do funcionario.
    """

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True
    )

    # Identity
    employee_id: UUID = Field(default_factory=uuid4)
    employee_code: str = Field(..., pattern=r"^EMP-\d{6}$")
    registration_number: Optional[str] = None  # Matricula eSocial

    # Personal Data
    full_name: str = Field(..., min_length=5, max_length=150)
    social_name: Optional[str] = Field(None, max_length=150)  # Nome social
    cpf: str = Field(..., pattern=r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$")
    rg: Optional[str] = Field(None, max_length=20)
    birth_date: date
    gender: str = Field(..., pattern=r"^(M|F|O|NI)$")  # M, F, Outro, Nao Informado
    marital_status: str = Field(..., pattern=r"^(single|married|divorced|widowed|stable_union)$")
    nationality: str = Field(default="Brasileiro", max_length=50)

    # Contact
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    personal_email: Optional[str] = None
    phone: str = Field(..., pattern=r"^\(\d{2}\)\s?\d{4,5}-?\d{4}$")
    address: Address

    # Employment
    employment_type: EmploymentType
    status: EmployeeStatus = Field(default=EmployeeStatus.ACTIVE)
    hire_date: date
    termination_date: Optional[date] = None
    termination_type: Optional[TerminationType] = None

    # Position
    department_id: UUID
    department_name: str
    position_id: UUID
    position_name: str
    manager_id: Optional[UUID] = None
    work_schedule: WorkScheduleType

    # Compensation
    base_salary: Decimal = Field(..., gt=Decimal("0"))
    currency: str = Field(default="BRL", pattern=r"^[A-Z]{3}$")
    salary_type: str = Field(default="monthly", pattern=r"^(hourly|monthly)$")
    payment_day: int = Field(default=5, ge=1, le=31)

    # Benefits
    has_meal_voucher: bool = Field(default=False)
    meal_voucher_value: Decimal = Field(default=Decimal("0"))
    has_transport_voucher: bool = Field(default=False)
    has_health_plan: bool = Field(default=False)
    has_dental_plan: bool = Field(default=False)
    has_life_insurance: bool = Field(default=False)

    # Banking
    bank_account: BankAccount

    # Dependents
    dependents: List[Dependent] = Field(default_factory=list)
    emergency_contacts: List[EmergencyContact] = Field(default_factory=list)

    # Leave History
    leave_records: List[LeaveRecord] = Field(default_factory=list)
    vacation_balance_days: int = Field(default=0, ge=0)
    last_vacation_period: Optional[str] = None  # Ex: "2023/2024"

    # Documents
    ctps_number: Optional[str] = None  # Carteira de trabalho
    ctps_series: Optional[str] = None
    pis_number: Optional[str] = Field(None, pattern=r"^\d{3}\.?\d{5}\.?\d{2}-?\d$")
    voter_id: Optional[str] = None
    military_certificate: Optional[str] = None

    # Multi-tenant
    tenant_id: UUID
    condominium_id: Optional[UUID] = None

    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: Optional[str] = None

    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v: str) -> str:
        """Valida CPF."""
        # Remove formatacao
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError("CPF deve ter 11 digitos")
        # Valida digitos repetidos
        if cpf == cpf[0] * 11:
            raise ValueError("CPF invalido")
        return v

    @model_validator(mode='after')
    def validate_employee(self) -> 'EmployeeEntity':
        """Valida regras de negocio do colaborador."""
        # Valida idade minima (16 anos para aprendiz, 18 para CLT)
        age = self._calculate_age()
        if self.employment_type == EmploymentType.CLT and age < 18:
            raise ValueError("Idade minima para CLT e 18 anos")
        if self.employment_type == EmploymentType.APPRENTICE and age < 14:
            raise ValueError("Idade minima para aprendiz e 14 anos")
        if self.employment_type == EmploymentType.INTERN and age < 16:
            raise ValueError("Idade minima para estagiario e 16 anos")

        # Valida data de contratacao
        if self.hire_date > date.today():
            raise ValueError("Data de contratacao nao pode ser futura")

        # Valida desligamento
        if self.termination_date:
            if self.termination_date < self.hire_date:
                raise ValueError("Data de desligamento deve ser posterior a contratacao")
            if not self.termination_type:
                raise ValueError("Tipo de desligamento e obrigatorio")

        return self

    def _calculate_age(self) -> int:
        """Calcula idade do colaborador."""
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    # ==========================================================================
    # Business Methods
    # ==========================================================================

    @property
    def age(self) -> int:
        """Retorna idade atual."""
        return self._calculate_age()

    @property
    def tenure_days(self) -> int:
        """Retorna tempo de casa em dias."""
        end = self.termination_date or date.today()
        return (end - self.hire_date).days

    @property
    def tenure_years(self) -> float:
        """Retorna tempo de casa em anos."""
        return self.tenure_days / 365.25

    @property
    def display_name(self) -> str:
        """Retorna nome de exibicao (social se disponivel)."""
        return self.social_name or self.full_name

    @property
    def is_active(self) -> bool:
        """Verifica se esta ativo."""
        return self.status in EmployeeStatus.active_statuses()

    @property
    def can_work(self) -> bool:
        """Verifica se pode trabalhar."""
        return EmployeeStatus(self.status).is_working()

    @property
    def ir_dependents_count(self) -> int:
        """Conta dependentes para IR."""
        return sum(1 for d in self.dependents if d.is_ir_dependent)

    def calculate_vacation_days(self) -> int:
        """Calcula dias de ferias disponiveis."""
        if not EmploymentType(self.employment_type).has_vacation_rights():
            return 0

        # Apos 12 meses, tem direito a 30 dias
        if self.tenure_days >= 365:
            return 30
        return 0

    def calculate_13th_salary(self, reference_month: int = 12) -> Decimal:
        """Calcula 13o salario proporcional."""
        if not EmploymentType(self.employment_type).has_13th_salary():
            return Decimal("0")

        # Calcula meses trabalhados no ano
        current_year = date.today().year
        start_of_year = date(current_year, 1, 1)
        work_start = max(self.hire_date, start_of_year)

        months_worked = min(reference_month, (date.today() - work_start).days // 30)
        months_worked = max(0, min(12, months_worked))

        return (self.base_salary * Decimal(months_worked) / Decimal("12")).quantize(Decimal("0.01"))

    def calculate_overtime(
        self,
        hours: Decimal,
        is_holiday: bool = False
    ) -> Decimal:
        """Calcula valor de hora extra."""
        hourly_rate = self.base_salary / Decimal("220")  # 220 horas mensais

        if is_holiday:
            multiplier = Decimal("2.0")  # 100%
        else:
            multiplier = Decimal("1.5")  # 50%

        return (hourly_rate * hours * multiplier).quantize(Decimal("0.01"))

    def calculate_night_shift_bonus(self, hours: Decimal) -> Decimal:
        """Calcula adicional noturno (20%)."""
        hourly_rate = self.base_salary / Decimal("220")
        return (hourly_rate * hours * Decimal("0.2")).quantize(Decimal("0.01"))

    def request_leave(
        self,
        leave_type: LeaveType,
        start_date: date,
        end_date: date,
        reason: str
    ) -> LeaveRecord:
        """Solicita afastamento."""
        if not self.is_active:
            raise ValueError("Colaborador inativo nao pode solicitar afastamento")

        days = (end_date - start_date).days + 1
        max_days = leave_type.max_days()

        if max_days > 0 and days > max_days:
            raise ValueError(
                f"Afastamento de {leave_type.value} nao pode exceder {max_days} dias"
            )

        leave = LeaveRecord(
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days=days,
            reason=reason
        )

        self.leave_records.append(leave)
        self.updated_at = datetime.utcnow()

        return leave

    def terminate(
        self,
        termination_date: date,
        termination_type: TerminationType,
        user_id: str
    ) -> Dict[str, Any]:
        """Processa desligamento do colaborador."""
        if self.status == EmployeeStatus.TERMINATED:
            raise ValueError("Colaborador ja esta desligado")

        self.status = EmployeeStatus.TERMINATED
        self.termination_date = termination_date
        self.termination_type = termination_type
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

        # Calcula verbas rescisorias
        severance = self._calculate_severance(termination_type)

        return severance

    def _calculate_severance(self, term_type: TerminationType) -> Dict[str, Any]:
        """Calcula verbas rescisorias."""
        severance = {
            "salary_balance": Decimal("0"),
            "vacation_balance": Decimal("0"),
            "vacation_bonus": Decimal("0"),
            "13th_proportional": Decimal("0"),
            "notice_period": Decimal("0"),
            "fgts_penalty": Decimal("0"),
            "total": Decimal("0")
        }

        # Saldo de salario (dias trabalhados no mes)
        today = date.today()
        days_worked = today.day
        severance["salary_balance"] = (self.base_salary / 30 * days_worked).quantize(Decimal("0.01"))

        # Ferias proporcionais
        vacation_months = (today.month - self.hire_date.month) % 12 or 12
        severance["vacation_balance"] = (self.base_salary / 12 * vacation_months).quantize(Decimal("0.01"))

        # 1/3 de ferias
        severance["vacation_bonus"] = (severance["vacation_balance"] / 3).quantize(Decimal("0.01"))

        # 13o proporcional
        severance["13th_proportional"] = self.calculate_13th_salary(today.month)

        # Aviso previo (se aplicavel)
        if term_type.has_notice_period():
            # 30 dias + 3 dias por ano trabalhado
            notice_days = 30 + min(60, int(self.tenure_years) * 3)
            severance["notice_period"] = (self.base_salary / 30 * notice_days).quantize(Decimal("0.01"))

        # Multa FGTS
        fgts_penalty_percent = term_type.fgts_penalty_percent()
        if fgts_penalty_percent > 0:
            # Estimativa: 8% do salario por mes trabalhado
            fgts_balance = self.base_salary * Decimal("0.08") * Decimal(str(int(self.tenure_years * 12)))
            severance["fgts_penalty"] = (fgts_balance * fgts_penalty_percent / 100).quantize(Decimal("0.01"))

        severance["total"] = sum(v for v in severance.values() if isinstance(v, Decimal))

        return severance

    def promote(
        self,
        new_position_id: UUID,
        new_position_name: str,
        new_salary: Decimal,
        effective_date: date,
        user_id: str
    ) -> None:
        """Promove o colaborador."""
        if new_salary <= self.base_salary:
            raise ValueError("Novo salario deve ser maior que atual em promocao")

        self.position_id = new_position_id
        self.position_name = new_position_name
        self.base_salary = new_salary
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

    def transfer(
        self,
        new_department_id: UUID,
        new_department_name: str,
        user_id: str
    ) -> None:
        """Transfere o colaborador de departamento."""
        self.department_id = new_department_id
        self.department_name = new_department_name
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

    def add_dependent(self, dependent: Dependent) -> None:
        """Adiciona dependente."""
        # Verifica duplicidade por CPF
        for d in self.dependents:
            if d.cpf == dependent.cpf:
                raise ValueError("Dependente ja cadastrado")

        self.dependents.append(dependent)
        self.updated_at = datetime.utcnow()

    def remove_dependent(self, dependent_id: UUID) -> bool:
        """Remove dependente."""
        original_count = len(self.dependents)
        self.dependents = [d for d in self.dependents if d.dependent_id != dependent_id]

        if len(self.dependents) < original_count:
            self.updated_at = datetime.utcnow()
            return True
        return False

    @staticmethod
    def generate_employee_code(sequence: int) -> str:
        """Gera codigo do colaborador."""
        return f"EMP-{sequence:06d}"

    def to_summary(self) -> Dict[str, Any]:
        """Retorna resumo do colaborador."""
        return {
            "employee_id": str(self.employee_id),
            "employee_code": self.employee_code,
            "name": self.display_name,
            "department": self.department_name,
            "position": self.position_name,
            "status": self.status,
            "hire_date": self.hire_date.isoformat(),
            "tenure_years": round(self.tenure_years, 1),
            "employment_type": self.employment_type
        }
