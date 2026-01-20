# SKILL: OPERACIONAL
## ERP CONECTA MAIS - FASE 2

**Modulo:** Operacoes
**Sprints:** 30+ (apos financeiro)
**Prioridade:** MEDIA

---

## CONTEXTO DO MODULO

Gestao operacional de contratos e servicos:
- Gestao de Contratos
- Escalas de Trabalho
- Ordens de Servico
- SLA e Medicao
- Gestao de Postos

---

## ESTRUTURA DO MODULO

```
modules/operations/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── contract.py           # Contratos
│   ├── contract_item.py      # Itens do contrato
│   ├── contract_addendum.py  # Aditivos
│   ├── work_post.py          # Postos de trabalho
│   ├── work_schedule.py      # Escalas
│   ├── shift.py              # Turnos
│   ├── service_order.py      # Ordens de servico
│   ├── sla_metric.py         # Metricas SLA
│   └── measurement.py        # Medicoes
├── schemas/
│   ├── __init__.py
│   ├── contract.py
│   ├── schedule.py
│   └── service_order.py
├── repositories/
│   ├── __init__.py
│   ├── contract_repository.py
│   ├── schedule_repository.py
│   └── service_order_repository.py
├── services/
│   ├── __init__.py
│   ├── contract_service.py
│   ├── schedule_optimizer.py  # IA para escalas
│   ├── sla_calculator.py
│   └── measurement_service.py
└── controllers/
    ├── __init__.py
    ├── contract_controller.py
    ├── schedule_controller.py
    └── service_order_controller.py
```

---

## ENTIDADES PRINCIPAIS

### Contract (Contrato)

```python
class Contract(Base):
    """
    Contrato de prestacao de servicos.

    Representa um contrato firmado com cliente,
    incluindo postos, valores e vigencia.
    """

    __tablename__ = "contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identificacao
    number = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)

    # Relacionamentos
    client_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey("proposals.id"), nullable=True)

    # Tipo
    contract_type = Column(Enum(ContractType), nullable=False)
    # CONTINUOUS, PROJECT, TEMPORARY, EMERGENCY

    # Vigencia
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    duration_months = Column(Integer, nullable=True)
    auto_renew = Column(Boolean, default=False)

    # Valores (SEMPRE Decimal)
    monthly_value = Column(Numeric(15, 2), nullable=False)
    total_value = Column(Numeric(15, 2), nullable=False)
    reajustment_index = Column(String(20), default="IPCA")
    reajustment_date = Column(Date, nullable=True)

    # Status
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT)
    # DRAFT, ACTIVE, SUSPENDED, FINISHED, CANCELLED

    # Faturamento
    billing_day = Column(Integer, default=1)
    payment_terms = Column(Integer, default=30)

    # SLA
    sla_target = Column(Numeric(5, 2), default=Decimal("99.00"))

    # Documentos
    signed_document_url = Column(String(500), nullable=True)
    signed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("ContractItem", back_populates="contract")
    posts = relationship("WorkPost", back_populates="contract")
    addendums = relationship("ContractAddendum", back_populates="contract")
    measurements = relationship("Measurement", back_populates="contract")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<Contract(number='{self.number}', client={self.client_id})>"

    def is_active(self) -> bool:
        """Verifica se contrato esta ativo."""
        if self.status != ContractStatus.ACTIVE:
            return False
        today = date.today()
        if self.end_date and today > self.end_date:
            return False
        return True

    def days_to_expire(self) -> Optional[int]:
        """Dias ate expirar."""
        if not self.end_date:
            return None
        return (self.end_date - date.today()).days
```

### WorkPost (Posto de Trabalho)

```python
class WorkPost(Base):
    """
    Posto de trabalho em um contrato.

    Representa um local/funcao onde funcionarios
    serao alocados.
    """

    __tablename__ = "work_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False)

    # Identificacao
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)

    # Localizacao
    address = Column(String(300), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)

    # Tipo de servico
    service_type = Column(Enum(ServiceType), nullable=False)
    # VIGILANCE, CLEANING, RECEPTION, MAINTENANCE, OTHER

    # Cobertura
    coverage_type = Column(Enum(CoverageType), default=CoverageType.FULL_TIME)
    # FULL_TIME (24x7), BUSINESS_HOURS, CUSTOM

    # Headcount
    required_headcount = Column(Integer, default=1)
    current_headcount = Column(Integer, default=0)

    # Valores
    post_value = Column(Numeric(15, 2), default=Decimal("0.00"))

    # Status
    is_active = Column(Boolean, default=True)

    # Relationships
    contract = relationship("Contract", back_populates="posts")
    schedules = relationship("WorkSchedule", back_populates="post")
    employees = relationship("PostEmployee", back_populates="post")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<WorkPost(code='{self.code}', name='{self.name}')>"

    def coverage_percentage(self) -> Decimal:
        """Calcula percentual de cobertura."""
        if self.required_headcount == 0:
            return Decimal("100.00")
        return Decimal(str(self.current_headcount / self.required_headcount * 100))
```

### WorkSchedule (Escala de Trabalho)

```python
class WorkSchedule(Base):
    """
    Escala de trabalho.

    Define horarios e funcionarios alocados
    em um posto.
    """

    __tablename__ = "work_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("work_posts.id"), nullable=False)

    # Periodo
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    # Tipo de escala
    schedule_type = Column(Enum(ScheduleType), nullable=False)
    # FIXED_5X2, FIXED_6X1, ROTATING_12X36, ROTATING_24X48, CUSTOM

    # Status
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.DRAFT)
    # DRAFT, PUBLISHED, LOCKED

    # Dados da escala (JSON com dias e funcionarios)
    schedule_data = Column(JSONB, nullable=False, default={})
    # Exemplo:
    # {
    #   "2026-01-01": [{"employee_id": "xxx", "shift_id": "yyy", "start": "06:00", "end": "18:00"}],
    #   "2026-01-02": [...]
    # }

    # Metricas
    total_hours = Column(Numeric(10, 2), default=Decimal("0.00"))
    overtime_hours = Column(Numeric(10, 2), default=Decimal("0.00"))
    coverage_rate = Column(Numeric(5, 2), default=Decimal("0.00"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    post = relationship("WorkPost", back_populates="schedules")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<WorkSchedule(post={self.post_id}, month={self.month}/{self.year})>"
```

### ServiceOrder (Ordem de Servico)

```python
class ServiceOrder(Base):
    """
    Ordem de servico.

    Representa uma demanda de trabalho
    a ser executada.
    """

    __tablename__ = "service_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identificacao
    number = Column(String(20), unique=True, nullable=False, index=True)

    # Relacionamentos
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("work_posts.id"), nullable=True)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)

    # Tipo e prioridade
    order_type = Column(Enum(OrderType), nullable=False)
    # CORRECTIVE, PREVENTIVE, INSPECTION, EMERGENCY
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    # LOW, MEDIUM, HIGH, CRITICAL

    # Descricao
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    resolution = Column(Text, nullable=True)

    # Status
    status = Column(Enum(OrderStatus), default=OrderStatus.OPEN)
    # OPEN, IN_PROGRESS, ON_HOLD, COMPLETED, CANCELLED

    # Datas
    scheduled_date = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)

    # SLA
    sla_deadline = Column(DateTime, nullable=True)
    sla_met = Column(Boolean, nullable=True)

    # Checklist (JSON)
    checklist = Column(JSONB, default=[])
    # [{"item": "Verificar X", "done": true}, ...]

    # Anexos
    attachments = Column(JSONB, default=[])

    # Assinatura
    signature_url = Column(String(500), nullable=True)
    signed_by = Column(String(200), nullable=True)
    signed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<ServiceOrder(number='{self.number}', status={self.status})>"

    def is_overdue(self) -> bool:
        """Verifica se esta atrasada."""
        if not self.due_date:
            return False
        if self.status in (OrderStatus.COMPLETED, OrderStatus.CANCELLED):
            return False
        return datetime.now() > self.due_date
```

---

## SERVICES ESPECIALIZADOS

### ScheduleOptimizer (IA para Escalas)

```python
# modules/operations/services/schedule_optimizer.py
"""Otimizador de Escalas com IA."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

from core.logging import logger


@dataclass
class EmployeeAvailability:
    """Disponibilidade do funcionario."""
    employee_id: str
    available_days: list[date]
    max_hours_week: int
    preferred_shift: str
    restrictions: list[str]


@dataclass
class ScheduleConstraints:
    """Restricoes da escala."""
    min_rest_hours: int = 11  # DSR
    max_consecutive_days: int = 6
    max_hours_day: int = 12
    max_hours_week: int = 44
    require_lunch_break: bool = True


@dataclass
class OptimizedSchedule:
    """Escala otimizada."""
    schedule_data: dict
    total_hours: Decimal
    overtime_hours: Decimal
    coverage_rate: Decimal
    warnings: list[str]


class ScheduleOptimizer:
    """
    Otimizador de escalas de trabalho.

    Usa algoritmos de otimizacao para gerar
    escalas que minimizam custos e maximizam
    cobertura respeitando restricoes legais.
    """

    def __init__(self, constraints: Optional[ScheduleConstraints] = None) -> None:
        """Inicializa otimizador."""
        self.constraints = constraints or ScheduleConstraints()

    def optimize(
        self,
        post_id: str,
        month: int,
        year: int,
        employees: list[EmployeeAvailability],
        required_coverage: dict[str, int]
    ) -> OptimizedSchedule:
        """
        Gera escala otimizada.

        Args:
            post_id: ID do posto
            month: Mes
            year: Ano
            employees: Funcionarios disponiveis
            required_coverage: Cobertura necessaria por dia

        Returns:
            Escala otimizada
        """
        logger.info(
            "Iniciando otimizacao de escala",
            extra={
                "post_id": post_id,
                "month": month,
                "year": year,
                "employees": len(employees)
            }
        )

        schedule_data = {}
        warnings = []
        total_hours = Decimal("0")

        # Gerar dias do mes
        days = self._get_month_days(month, year)

        # Para cada dia, alocar funcionarios
        for day in days:
            day_str = day.isoformat()
            required = required_coverage.get(day_str, required_coverage.get("default", 1))

            # Encontrar funcionarios disponiveis
            available = self._get_available_employees(
                employees,
                day,
                schedule_data
            )

            if len(available) < required:
                warnings.append(
                    f"Cobertura insuficiente em {day_str}: "
                    f"{len(available)}/{required}"
                )

            # Alocar funcionarios
            allocations = []
            for i, emp in enumerate(available[:required]):
                shift = self._select_shift(emp, day)
                allocations.append({
                    "employee_id": emp.employee_id,
                    "shift": shift,
                    "start": self._get_shift_start(shift),
                    "end": self._get_shift_end(shift)
                })
                total_hours += Decimal("8")  # Simplificado

            schedule_data[day_str] = allocations

        # Calcular metricas
        coverage_rate = self._calculate_coverage(schedule_data, required_coverage)
        overtime = self._calculate_overtime(schedule_data, employees)

        logger.info(
            "Escala otimizada gerada",
            extra={
                "coverage_rate": str(coverage_rate),
                "warnings": len(warnings)
            }
        )

        return OptimizedSchedule(
            schedule_data=schedule_data,
            total_hours=total_hours,
            overtime_hours=overtime,
            coverage_rate=coverage_rate,
            warnings=warnings
        )

    def _get_month_days(self, month: int, year: int) -> list[date]:
        """Retorna dias do mes."""
        first_day = date(year, month, 1)
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)

        days = []
        current = first_day
        while current < next_month:
            days.append(current)
            current += timedelta(days=1)

        return days

    def _get_available_employees(
        self,
        employees: list[EmployeeAvailability],
        day: date,
        current_schedule: dict
    ) -> list[EmployeeAvailability]:
        """Filtra funcionarios disponiveis."""
        available = []

        for emp in employees:
            # Verificar disponibilidade
            if day not in emp.available_days:
                continue

            # Verificar descanso minimo
            if not self._has_minimum_rest(emp.employee_id, day, current_schedule):
                continue

            # Verificar dias consecutivos
            if self._exceeds_consecutive_days(emp.employee_id, day, current_schedule):
                continue

            available.append(emp)

        return available

    def _has_minimum_rest(
        self,
        employee_id: str,
        day: date,
        schedule: dict
    ) -> bool:
        """Verifica descanso minimo (DSR)."""
        yesterday = (day - timedelta(days=1)).isoformat()

        if yesterday not in schedule:
            return True

        for allocation in schedule[yesterday]:
            if allocation["employee_id"] == employee_id:
                # Verificar horario de termino vs inicio
                # Simplificado: sempre True por enquanto
                return True

        return True

    def _exceeds_consecutive_days(
        self,
        employee_id: str,
        day: date,
        schedule: dict
    ) -> bool:
        """Verifica se excede dias consecutivos."""
        consecutive = 0

        for i in range(1, self.constraints.max_consecutive_days + 1):
            prev_day = (day - timedelta(days=i)).isoformat()
            if prev_day not in schedule:
                break

            worked = any(
                a["employee_id"] == employee_id
                for a in schedule[prev_day]
            )

            if worked:
                consecutive += 1
            else:
                break

        return consecutive >= self.constraints.max_consecutive_days

    def _select_shift(self, employee: EmployeeAvailability, day: date) -> str:
        """Seleciona turno para o funcionario."""
        # Preferencia do funcionario
        if employee.preferred_shift:
            return employee.preferred_shift

        # Dia da semana determina turno padrao
        weekday = day.weekday()
        if weekday < 5:  # Seg-Sex
            return "MORNING"
        else:  # Sab-Dom
            return "FULL"

    def _get_shift_start(self, shift: str) -> str:
        """Retorna horario de inicio do turno."""
        shifts = {
            "MORNING": "06:00",
            "AFTERNOON": "14:00",
            "NIGHT": "22:00",
            "FULL": "07:00"
        }
        return shifts.get(shift, "08:00")

    def _get_shift_end(self, shift: str) -> str:
        """Retorna horario de fim do turno."""
        shifts = {
            "MORNING": "14:00",
            "AFTERNOON": "22:00",
            "NIGHT": "06:00",
            "FULL": "19:00"
        }
        return shifts.get(shift, "17:00")

    def _calculate_coverage(
        self,
        schedule: dict,
        required: dict
    ) -> Decimal:
        """Calcula taxa de cobertura."""
        total_required = 0
        total_covered = 0

        for day, allocations in schedule.items():
            req = required.get(day, required.get("default", 1))
            total_required += req
            total_covered += min(len(allocations), req)

        if total_required == 0:
            return Decimal("100.00")

        rate = Decimal(str(total_covered / total_required * 100))
        return rate.quantize(Decimal("0.01"))

    def _calculate_overtime(
        self,
        schedule: dict,
        employees: list[EmployeeAvailability]
    ) -> Decimal:
        """Calcula horas extras."""
        # Simplificado: considerar horas acima de 44/semana
        overtime = Decimal("0")
        # Implementar calculo real
        return overtime
```

### SLACalculator

```python
# modules/operations/services/sla_calculator.py
"""Calculador de SLA."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from core.logging import logger


@dataclass
class SLAResult:
    """Resultado do calculo de SLA."""
    period_start: datetime
    period_end: datetime
    target_percent: Decimal
    achieved_percent: Decimal
    met: bool
    details: dict


class SLACalculator:
    """
    Calculador de metricas de SLA.

    Calcula cumprimento de SLA baseado em
    diferentes metricas operacionais.
    """

    def calculate_coverage_sla(
        self,
        contract_id: str,
        start_date: datetime,
        end_date: datetime,
        target: Decimal = Decimal("99.00")
    ) -> SLAResult:
        """
        Calcula SLA de cobertura de postos.

        Args:
            contract_id: ID do contrato
            start_date: Inicio do periodo
            end_date: Fim do periodo
            target: Meta de SLA

        Returns:
            Resultado do SLA
        """
        # Buscar dados de cobertura
        total_hours_required = self._get_required_hours(contract_id, start_date, end_date)
        total_hours_covered = self._get_covered_hours(contract_id, start_date, end_date)

        if total_hours_required == 0:
            achieved = Decimal("100.00")
        else:
            achieved = Decimal(str(
                total_hours_covered / total_hours_required * 100
            )).quantize(Decimal("0.01"))

        met = achieved >= target

        logger.info(
            "SLA de cobertura calculado",
            extra={
                "contract_id": contract_id,
                "target": str(target),
                "achieved": str(achieved),
                "met": met
            }
        )

        return SLAResult(
            period_start=start_date,
            period_end=end_date,
            target_percent=target,
            achieved_percent=achieved,
            met=met,
            details={
                "required_hours": total_hours_required,
                "covered_hours": total_hours_covered,
                "gap_hours": total_hours_required - total_hours_covered
            }
        )

    def calculate_response_sla(
        self,
        service_orders: list,
        target: Decimal = Decimal("95.00")
    ) -> SLAResult:
        """
        Calcula SLA de tempo de resposta de OS.

        Args:
            service_orders: Lista de ordens de servico
            target: Meta de SLA

        Returns:
            Resultado do SLA
        """
        if not service_orders:
            return SLAResult(
                period_start=datetime.now(),
                period_end=datetime.now(),
                target_percent=target,
                achieved_percent=Decimal("100.00"),
                met=True,
                details={"total_orders": 0}
            )

        total = len(service_orders)
        within_sla = sum(1 for os in service_orders if os.sla_met)

        achieved = Decimal(str(within_sla / total * 100)).quantize(Decimal("0.01"))
        met = achieved >= target

        return SLAResult(
            period_start=min(os.created_at for os in service_orders),
            period_end=max(os.created_at for os in service_orders),
            target_percent=target,
            achieved_percent=achieved,
            met=met,
            details={
                "total_orders": total,
                "within_sla": within_sla,
                "outside_sla": total - within_sla
            }
        )

    def _get_required_hours(
        self,
        contract_id: str,
        start: datetime,
        end: datetime
    ) -> int:
        """Calcula horas requeridas no periodo."""
        # Implementar: buscar postos e calcular horas
        days = (end - start).days + 1
        return days * 24  # Simplificado: 24h/dia

    def _get_covered_hours(
        self,
        contract_id: str,
        start: datetime,
        end: datetime
    ) -> int:
        """Calcula horas cobertas no periodo."""
        # Implementar: buscar registros de ponto
        return int(self._get_required_hours(contract_id, start, end) * 0.98)
```

---

## ENDPOINTS

### Contratos

```
POST   /api/v1/contracts/                    - Criar contrato
GET    /api/v1/contracts/                    - Listar contratos
GET    /api/v1/contracts/{id}                - Obter contrato
PATCH  /api/v1/contracts/{id}                - Atualizar contrato
DELETE /api/v1/contracts/{id}                - Cancelar contrato
POST   /api/v1/contracts/{id}/activate       - Ativar contrato
POST   /api/v1/contracts/{id}/renew          - Renovar contrato
POST   /api/v1/contracts/{id}/addendum       - Criar aditivo
GET    /api/v1/contracts/{id}/sla            - Obter SLA
```

### Postos

```
POST   /api/v1/posts/                        - Criar posto
GET    /api/v1/contracts/{id}/posts          - Listar postos do contrato
PATCH  /api/v1/posts/{id}                    - Atualizar posto
DELETE /api/v1/posts/{id}                    - Desativar posto
GET    /api/v1/posts/{id}/coverage           - Cobertura do posto
```

### Escalas

```
POST   /api/v1/schedules/                    - Criar escala
GET    /api/v1/posts/{id}/schedules          - Listar escalas do posto
GET    /api/v1/schedules/{id}                - Obter escala
PATCH  /api/v1/schedules/{id}                - Atualizar escala
POST   /api/v1/schedules/{id}/publish        - Publicar escala
POST   /api/v1/schedules/optimize            - Gerar escala otimizada
```

### Ordens de Servico

```
POST   /api/v1/service-orders/               - Criar OS
GET    /api/v1/service-orders/               - Listar OS
GET    /api/v1/service-orders/{id}           - Obter OS
PATCH  /api/v1/service-orders/{id}           - Atualizar OS
POST   /api/v1/service-orders/{id}/assign    - Atribuir OS
POST   /api/v1/service-orders/{id}/start     - Iniciar OS
POST   /api/v1/service-orders/{id}/complete  - Concluir OS
POST   /api/v1/service-orders/{id}/cancel    - Cancelar OS
```

---

## CHECKLIST MODULO OPERACIONAL

- [ ] Models de Contratos
  - [ ] Contract
  - [ ] ContractItem
  - [ ] ContractAddendum

- [ ] Models de Postos
  - [ ] WorkPost
  - [ ] PostEmployee

- [ ] Models de Escalas
  - [ ] WorkSchedule
  - [ ] Shift

- [ ] Models de OS
  - [ ] ServiceOrder
  - [ ] Checklist

- [ ] Services
  - [ ] ScheduleOptimizer
  - [ ] SLACalculator
  - [ ] MeasurementService

- [ ] Testes >= 85%
- [ ] Pylint 100/100

---

*Skill Operacional - ERP Conecta Mais Fase 2*
