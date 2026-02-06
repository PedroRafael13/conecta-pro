# SKILL: RECURSOS HUMANOS
## ERP CONECTA MAIS - FASE 2

**Modulo:** RH (Recursos Humanos)
**Sprints:** 15-21
**Prioridade:** ALTA

---

## CONTEXTO DO MODULO

Modulo novo na Fase 2. Implementa gestao completa de RH:
- Recrutamento e Selecao (ATS)
- Ponto Eletronico
- Admissao Digital
- Folha de Pagamento
- Ferias e Rescisao

---

## ESTRUTURA DO MODULO

```
modules/hr/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── job_posting.py      # Vagas
│   ├── candidate.py        # Candidatos
│   ├── application.py      # Candidaturas
│   ├── interview.py        # Entrevistas
│   ├── employee.py         # Funcionarios
│   ├── time_entry.py       # Registros de ponto
│   ├── time_sheet.py       # Folha de ponto
│   ├── payroll.py          # Folha de pagamento
│   ├── payroll_item.py     # Rubricas
│   ├── vacation.py         # Ferias
│   └── termination.py      # Rescisao
├── schemas/
│   ├── __init__.py
│   ├── recruitment.py
│   ├── time_tracking.py
│   ├── payroll.py
│   └── employee.py
├── repositories/
│   ├── __init__.py
│   ├── recruitment_repository.py
│   ├── employee_repository.py
│   ├── time_tracking_repository.py
│   └── payroll_repository.py
├── services/
│   ├── __init__.py
│   ├── resume_parser.py     # Parser de curriculo
│   ├── candidate_scoring.py # Scoring de candidatos
│   ├── biometric_service.py # Biometria facial
│   ├── time_calculator.py   # Calculo de horas
│   ├── payroll_engine.py    # Motor de folha
│   └── esocial_service.py   # Integracao eSocial
└── controllers/
    ├── __init__.py
    ├── recruitment_controller.py
    ├── employee_controller.py
    ├── time_tracking_controller.py
    └── payroll_controller.py
```

---

## SPRINT 15-16: RECRUTAMENTO IA

### JobPosting (Vaga)

```python
class JobPosting(Base):
    """Vaga de emprego."""
    __tablename__ = "job_postings"

    id = Column(UUID, primary_key=True, default=uuid4)

    # Identificacao
    code = Column(String(20), unique=True, nullable=False)  # VAG-2026-001
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    # Requisitos
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)

    # Detalhes
    department_id = Column(UUID, ForeignKey("departments.id"))
    location = Column(String(200), nullable=True)
    work_model = Column(Enum(WorkModel))  # ONSITE, REMOTE, HYBRID
    contract_type = Column(Enum(ContractType))  # CLT, PJ, TEMP

    # Salario
    salary_min = Column(Numeric(15, 2), nullable=True)
    salary_max = Column(Numeric(15, 2), nullable=True)
    salary_hidden = Column(Boolean, default=True)

    # Status
    status = Column(Enum(JobStatus), default=JobStatus.DRAFT)
    # DRAFT, OPEN, PAUSED, CLOSED, FILLED

    # Vagas
    positions = Column(Integer, default=1)
    positions_filled = Column(Integer, default=0)

    # Datas
    published_at = Column(DateTime, nullable=True)
    deadline = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Integracao portais
    linkedin_posted = Column(Boolean, default=False)
    indeed_posted = Column(Boolean, default=False)
    catho_posted = Column(Boolean, default=False)
```

### Candidate (Candidato)

```python
class Candidate(Base):
    """Candidato a vaga."""
    __tablename__ = "candidates"

    id = Column(UUID, primary_key=True, default=uuid4)

    # Dados pessoais
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)
    cpf = Column(String(14), nullable=True, unique=True)

    # Endereco
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)

    # Profissional
    current_position = Column(String(200), nullable=True)
    current_company = Column(String(200), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)

    # Curriculo
    resume_url = Column(String(500), nullable=True)
    resume_text = Column(Text, nullable=True)  # Texto extraido
    resume_parsed = Column(JSONB, nullable=True)  # Dados estruturados

    # Skills extraidas
    skills = Column(ARRAY(String), nullable=True)
    experience_years = Column(Integer, nullable=True)
    education_level = Column(String(50), nullable=True)

    # Scoring
    score = Column(Integer, default=0)  # 0-100
    score_details = Column(JSONB, nullable=True)

    # Status
    source = Column(Enum(CandidateSource))
    # LINKEDIN, INDEED, REFERRAL, WEBSITE, DIRECT

    created_at = Column(DateTime, default=datetime.utcnow)
```

### CandidateScoring (IA)

```python
# modules/hr/services/candidate_scoring.py
"""Scoring de candidatos com IA."""

from decimal import Decimal
from typing import Optional

from modules.hr.models.candidate import Candidate
from modules.hr.models.job_posting import JobPosting


class CandidateScoringEngine:
    """Motor de scoring de candidatos."""

    WEIGHTS = {
        "skill_match": 0.35,
        "experience": 0.25,
        "education": 0.15,
        "location": 0.10,
        "salary_fit": 0.10,
        "recency": 0.05,
    }

    def calculate_score(
        self,
        candidate: Candidate,
        job: JobPosting
    ) -> tuple[int, dict]:
        """
        Calcula score do candidato para a vaga.

        Args:
            candidate: Candidato a avaliar
            job: Vaga para matching

        Returns:
            Tupla (score, detalhes)
        """
        scores = {}

        # 1. Match de skills
        scores["skill_match"] = self._score_skills(candidate, job)

        # 2. Experiencia
        scores["experience"] = self._score_experience(candidate, job)

        # 3. Educacao
        scores["education"] = self._score_education(candidate, job)

        # 4. Localizacao
        scores["location"] = self._score_location(candidate, job)

        # 5. Pretensao salarial
        scores["salary_fit"] = self._score_salary(candidate, job)

        # 6. Recencia da candidatura
        scores["recency"] = self._score_recency(candidate)

        # Calcular score final ponderado
        total = sum(
            scores[key] * weight
            for key, weight in self.WEIGHTS.items()
        )

        return int(total), scores

    def _score_skills(self, candidate: Candidate, job: JobPosting) -> float:
        """Pontua match de skills."""
        if not candidate.skills:
            return 30

        # Extrair skills requeridas do job (do requirements)
        required_skills = self._extract_skills(job.requirements)

        if not required_skills:
            return 50

        matches = sum(
            1 for skill in candidate.skills
            if any(req.lower() in skill.lower() for req in required_skills)
        )

        return min(100, (matches / len(required_skills)) * 100)

    def _score_experience(self, candidate: Candidate, job: JobPosting) -> float:
        """Pontua experiencia."""
        if not candidate.experience_years:
            return 30

        # Ideal: 3-5 anos para maioria das vagas
        if candidate.experience_years < 1:
            return 30
        elif candidate.experience_years <= 3:
            return 60
        elif candidate.experience_years <= 7:
            return 100
        elif candidate.experience_years <= 10:
            return 85
        else:
            return 70  # Overqualified

    def _score_education(self, candidate: Candidate, job: JobPosting) -> float:
        """Pontua educacao."""
        levels = {
            "ensino_medio": 40,
            "tecnico": 60,
            "graduacao": 80,
            "pos_graduacao": 90,
            "mestrado": 95,
            "doutorado": 100
        }
        return levels.get(candidate.education_level, 50)

    def _score_location(self, candidate: Candidate, job: JobPosting) -> float:
        """Pontua localizacao."""
        if job.work_model == "REMOTE":
            return 100

        if not candidate.city or not job.location:
            return 50

        if candidate.city.lower() in job.location.lower():
            return 100
        elif candidate.state and candidate.state in job.location:
            return 70

        return 40

    def _score_salary(self, candidate: Candidate, job: JobPosting) -> float:
        """Pontua fit salarial."""
        # Se nao tem faixa definida, score neutro
        if not job.salary_max:
            return 70

        # Aqui usariamos pretensao do candidato
        return 70

    def _score_recency(self, candidate: Candidate) -> float:
        """Pontua recencia."""
        from datetime import datetime, timedelta

        if not candidate.created_at:
            return 50

        days = (datetime.utcnow() - candidate.created_at).days

        if days <= 7:
            return 100
        elif days <= 30:
            return 80
        elif days <= 90:
            return 60
        else:
            return 40

    def _extract_skills(self, text: str) -> list[str]:
        """Extrai skills de texto."""
        # Lista de skills conhecidas
        known_skills = [
            "python", "javascript", "react", "fastapi", "sql",
            "docker", "kubernetes", "aws", "git", "linux",
            "excel", "powerbi", "sap", "erp", "crm"
        ]

        if not text:
            return []

        text_lower = text.lower()
        return [s for s in known_skills if s in text_lower]
```

---

## SPRINT 17: PONTO ELETRONICO

### TimeEntry (Registro de Ponto)

```python
class TimeEntry(Base):
    """Registro de ponto."""
    __tablename__ = "time_entries"

    id = Column(UUID, primary_key=True, default=uuid4)
    employee_id = Column(UUID, ForeignKey("employees.id"), nullable=False)

    # Tipo
    entry_type = Column(Enum(EntryType), nullable=False)
    # CLOCK_IN, CLOCK_OUT, BREAK_START, BREAK_END

    # Data/hora
    timestamp = Column(DateTime, nullable=False)
    date = Column(Date, nullable=False)  # Para facilitar queries

    # Localizacao
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    location_address = Column(String(500), nullable=True)

    # Biometria
    photo_url = Column(String(500), nullable=True)
    face_match_score = Column(Numeric(5, 2), nullable=True)  # 0-100
    biometric_validated = Column(Boolean, default=False)

    # Dispositivo
    device_type = Column(Enum(DeviceType))  # APP, WEB, TOTEM
    device_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Justificativa (se manual)
    is_manual = Column(Boolean, default=False)
    justification = Column(Text, nullable=True)
    approved_by = Column(UUID, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
```

### TimeSheet (Folha de Ponto)

```python
class TimeSheet(Base):
    """Folha de ponto mensal."""
    __tablename__ = "time_sheets"

    id = Column(UUID, primary_key=True, default=uuid4)
    employee_id = Column(UUID, ForeignKey("employees.id"), nullable=False)

    # Periodo
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)

    # Horas calculadas
    regular_hours = Column(Numeric(10, 2), default=Decimal("0.00"))
    overtime_50 = Column(Numeric(10, 2), default=Decimal("0.00"))  # 50%
    overtime_100 = Column(Numeric(10, 2), default=Decimal("0.00"))  # 100%
    night_hours = Column(Numeric(10, 2), default=Decimal("0.00"))  # Adicional noturno

    # Faltas e atrasos
    absent_days = Column(Integer, default=0)
    late_minutes = Column(Integer, default=0)

    # Banco de horas
    hour_bank_balance = Column(Numeric(10, 2), default=Decimal("0.00"))

    # Status
    status = Column(Enum(TimeSheetStatus), default=TimeSheetStatus.OPEN)
    # OPEN, PENDING_APPROVAL, APPROVED, CLOSED

    # Aprovacao
    approved_by = Column(UUID, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
```

### BiometricService

```python
# modules/hr/services/biometric_service.py
"""Servico de biometria facial."""

from decimal import Decimal
from typing import Optional
import base64

from core.logging import logger


class BiometricService:
    """Validacao biometrica facial."""

    MATCH_THRESHOLD = Decimal("80.00")  # 80% de similaridade

    def __init__(self) -> None:
        """Inicializa o servico."""
        # Aqui integraria com API de reconhecimento facial
        # Ex: AWS Rekognition, Azure Face, Google Vision
        pass

    def validate_face(
        self,
        employee_id: str,
        photo_base64: str
    ) -> tuple[bool, Decimal]:
        """
        Valida foto contra cadastro do funcionario.

        Args:
            employee_id: ID do funcionario
            photo_base64: Foto em base64

        Returns:
            Tupla (validado, score)
        """
        # Buscar foto cadastrada do funcionario
        reference_photo = self._get_reference_photo(employee_id)

        if not reference_photo:
            logger.warning(
                "Foto de referencia nao encontrada",
                extra={"employee_id": employee_id}
            )
            return False, Decimal("0.00")

        # Comparar faces
        match_score = self._compare_faces(reference_photo, photo_base64)

        is_valid = match_score >= self.MATCH_THRESHOLD

        logger.info(
            "Validacao biometrica",
            extra={
                "employee_id": employee_id,
                "score": str(match_score),
                "valid": is_valid
            }
        )

        return is_valid, match_score

    def _get_reference_photo(self, employee_id: str) -> Optional[str]:
        """Busca foto cadastrada."""
        # Implementar busca no banco
        pass

    def _compare_faces(self, ref: str, photo: str) -> Decimal:
        """Compara duas fotos."""
        # Implementar comparacao via API
        # Retorna score de 0 a 100
        return Decimal("95.00")  # Mock

    def register_face(
        self,
        employee_id: str,
        photo_base64: str
    ) -> bool:
        """Cadastra foto de referencia."""
        # Validar qualidade da foto
        if not self._validate_photo_quality(photo_base64):
            return False

        # Salvar foto
        # ...

        return True

    def _validate_photo_quality(self, photo: str) -> bool:
        """Valida qualidade da foto."""
        # Verificar:
        # - Tamanho minimo
        # - Rosto detectado
        # - Iluminacao adequada
        # - Foco
        return True
```

---

## SPRINT 18-21: FOLHA DE PAGAMENTO

### PayrollEngine

```python
# modules/hr/services/payroll_engine.py
"""Motor de calculo de folha de pagamento."""

from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import Optional
from dataclasses import dataclass

from core.logging import logger


@dataclass
class PayrollInput:
    """Dados de entrada para calculo."""
    employee_id: str
    base_salary: Decimal
    month: int
    year: int
    regular_hours: Decimal
    overtime_50: Decimal
    overtime_100: Decimal
    night_hours: Decimal
    absent_days: int
    advances: Decimal
    benefits_discount: Decimal


@dataclass
class PayrollResult:
    """Resultado do calculo de folha."""
    gross_salary: Decimal
    overtime_value: Decimal
    night_bonus: Decimal
    total_earnings: Decimal
    inss: Decimal
    irrf: Decimal
    other_discounts: Decimal
    total_discounts: Decimal
    net_salary: Decimal
    fgts: Decimal


class PayrollEngine:
    """Motor de folha de pagamento."""

    # Tabela INSS 2026 (atualizar anualmente)
    INSS_TABLE = [
        (Decimal("1412.00"), Decimal("0.075")),
        (Decimal("2666.68"), Decimal("0.09")),
        (Decimal("4000.03"), Decimal("0.12")),
        (Decimal("7786.02"), Decimal("0.14")),
    ]
    INSS_CEILING = Decimal("908.85")

    # Tabela IRRF 2026 (atualizar anualmente)
    IRRF_TABLE = [
        (Decimal("2259.20"), Decimal("0"), Decimal("0")),
        (Decimal("2826.65"), Decimal("0.075"), Decimal("169.44")),
        (Decimal("3751.05"), Decimal("0.15"), Decimal("381.44")),
        (Decimal("4664.68"), Decimal("0.225"), Decimal("662.77")),
        (Decimal("999999999"), Decimal("0.275"), Decimal("896.00")),
    ]
    DEPENDENT_DEDUCTION = Decimal("189.59")

    def calculate(self, payroll_input: PayrollInput) -> PayrollResult:
        """
        Calcula folha de pagamento.

        Args:
            payroll_input: Dados de entrada

        Returns:
            PayrollResult com todos os valores
        """
        # 1. Salario base proporcional
        base = payroll_input.base_salary

        # 2. Calcular horas extras
        hourly_rate = base / Decimal("220")  # 220h mensais CLT
        overtime_50 = payroll_input.overtime_50 * hourly_rate * Decimal("1.5")
        overtime_100 = payroll_input.overtime_100 * hourly_rate * Decimal("2.0")
        overtime_value = overtime_50 + overtime_100

        # 3. Adicional noturno (20% das horas noturnas)
        night_bonus = payroll_input.night_hours * hourly_rate * Decimal("0.2")

        # 4. Desconto de faltas
        daily_rate = base / Decimal("30")
        absence_discount = daily_rate * payroll_input.absent_days

        # 5. Total de proventos
        gross = base + overtime_value + night_bonus
        total_earnings = gross - absence_discount

        # 6. INSS
        inss = self._calculate_inss(total_earnings)

        # 7. IRRF (base = salario - INSS - dependentes)
        irrf_base = total_earnings - inss
        irrf = self._calculate_irrf(irrf_base)

        # 8. Outros descontos
        other_discounts = (
            payroll_input.advances +
            payroll_input.benefits_discount
        )

        # 9. Total de descontos
        total_discounts = inss + irrf + other_discounts

        # 10. Salario liquido
        net_salary = total_earnings - total_discounts

        # 11. FGTS (8% sobre bruto)
        fgts = total_earnings * Decimal("0.08")

        return PayrollResult(
            gross_salary=self._round(base),
            overtime_value=self._round(overtime_value),
            night_bonus=self._round(night_bonus),
            total_earnings=self._round(total_earnings),
            inss=self._round(inss),
            irrf=self._round(irrf),
            other_discounts=self._round(other_discounts),
            total_discounts=self._round(total_discounts),
            net_salary=self._round(net_salary),
            fgts=self._round(fgts)
        )

    def _calculate_inss(self, salary: Decimal) -> Decimal:
        """Calcula INSS progressivo."""
        inss = Decimal("0")
        remaining = salary
        previous_limit = Decimal("0")

        for limit, rate in self.INSS_TABLE:
            if salary > limit:
                inss += (limit - previous_limit) * rate
            else:
                inss += (salary - previous_limit) * rate
                break
            previous_limit = limit

        return min(inss, self.INSS_CEILING)

    def _calculate_irrf(
        self,
        base: Decimal,
        dependents: int = 0
    ) -> Decimal:
        """Calcula IRRF."""
        # Deduzir dependentes
        base -= self.DEPENDENT_DEDUCTION * dependents

        if base <= Decimal("0"):
            return Decimal("0")

        for limit, rate, deduction in self.IRRF_TABLE:
            if base <= limit:
                irrf = (base * rate) - deduction
                return max(Decimal("0"), irrf)

        return Decimal("0")

    def _round(self, value: Decimal) -> Decimal:
        """Arredonda para 2 casas."""
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

---

## INTEGRACAO ESOCIAL

```python
# modules/hr/services/esocial_service.py
"""Integracao com eSocial."""

from typing import Any
from datetime import date

from core.logging import logger


class ESocialService:
    """Servico de integracao eSocial."""

    def __init__(self, ambiente: str = "producao") -> None:
        """
        Inicializa servico.

        Args:
            ambiente: "producao" ou "homologacao"
        """
        self.ambiente = ambiente
        self.base_url = self._get_base_url()

    def send_event(
        self,
        event_type: str,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Envia evento para o eSocial.

        Args:
            event_type: Tipo do evento (S-2200, S-1200, etc)
            data: Dados do evento

        Returns:
            Resposta do eSocial
        """
        # Gerar XML do evento
        xml = self._generate_xml(event_type, data)

        # Assinar XML
        signed_xml = self._sign_xml(xml)

        # Enviar para eSocial
        response = self._send_to_esocial(signed_xml)

        logger.info(
            "Evento eSocial enviado",
            extra={
                "event_type": event_type,
                "response": response
            }
        )

        return response

    def send_admission(self, employee_data: dict) -> dict:
        """Envia evento S-2200 (admissao)."""
        return self.send_event("S-2200", employee_data)

    def send_payroll(self, payroll_data: dict) -> dict:
        """Envia evento S-1200 (remuneracao)."""
        return self.send_event("S-1200", payroll_data)

    def send_termination(self, termination_data: dict) -> dict:
        """Envia evento S-2299 (desligamento)."""
        return self.send_event("S-2299", termination_data)

    def _get_base_url(self) -> str:
        """Retorna URL do ambiente."""
        urls = {
            "producao": "https://webservices.producaorestrita.esocial.gov.br",
            "homologacao": "https://webservices.homologacao.esocial.gov.br"
        }
        return urls[self.ambiente]

    def _generate_xml(self, event_type: str, data: dict) -> str:
        """Gera XML do evento."""
        # Usar template XML do evento
        # Implementar geracao
        pass

    def _sign_xml(self, xml: str) -> str:
        """Assina XML com certificado A1."""
        # Implementar assinatura
        pass

    def _send_to_esocial(self, xml: str) -> dict:
        """Envia XML para webservice."""
        # Implementar envio SOAP
        pass
```

---

## ENDPOINTS POR SPRINT

### Sprint 15-16 (Recrutamento)
```
POST   /api/v1/jobs/                    - Criar vaga
GET    /api/v1/jobs/                    - Listar vagas
POST   /api/v1/candidates/              - Cadastrar candidato
POST   /api/v1/candidates/import-resume - Importar curriculo
GET    /api/v1/jobs/{id}/candidates     - Candidatos da vaga
POST   /api/v1/jobs/{id}/match          - Matching IA
POST   /api/v1/interviews/              - Agendar entrevista
```

### Sprint 17 (Ponto)
```
POST   /api/v1/time-entries/            - Registrar ponto
GET    /api/v1/time-entries/            - Listar registros
GET    /api/v1/time-sheets/{employee_id}/{month}/{year}
POST   /api/v1/time-sheets/{id}/approve - Aprovar folha
GET    /api/v1/time-sheets/{id}/report  - Relatorio MTE
```

### Sprint 18-21 (Folha)
```
POST   /api/v1/employees/               - Admitir funcionario
GET    /api/v1/employees/               - Listar funcionarios
POST   /api/v1/payroll/calculate        - Calcular folha
GET    /api/v1/payroll/{month}/{year}   - Folha do mes
GET    /api/v1/payroll/{id}/payslip     - Holerite PDF
POST   /api/v1/payroll/{id}/esocial     - Enviar eSocial
```

---

## CHECKLIST MODULO RH

- [ ] Sprint 15-16: Recrutamento
  - [ ] Models de vagas e candidatos
  - [ ] Parser de curriculo
  - [ ] Scoring IA
  - [ ] Pipeline Kanban

- [ ] Sprint 17: Ponto
  - [ ] Registro com biometria
  - [ ] Geolocalizacao
  - [ ] Banco de horas
  - [ ] Relatorio MTE

- [ ] Sprint 18-21: Folha
  - [ ] Calculo completo
  - [ ] INSS progressivo
  - [ ] IRRF
  - [ ] eSocial
  - [ ] Holerite digital

---

*Skill RH - ERP Conecta Mais Fase 2*
