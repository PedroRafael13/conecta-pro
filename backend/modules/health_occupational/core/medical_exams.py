"""
Module: MedicalExams
Description: Sistema de gestao de exames medicos ocupacionais (PCMSO)
             conforme NR-7 - Programa de Controle Medico de Saude Ocupacional.
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: NR-7 (Portaria MTb 3.214/78) - PCMSO
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
import logging

from pydantic import BaseModel, Field, validator, EmailStr
from sqlalchemy import Column, String, Boolean, DateTime, Date, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()


class ExamType(str, Enum):
    """Tipos de exames ocupacionais conforme NR-7."""
    ADMISSIONAL = "admissional"           # Antes da contratacao
    PERIODICO = "periodico"               # Durante o vinculo
    RETORNO_TRABALHO = "retorno_trabalho" # Apos afastamento >30 dias
    MUDANCA_FUNCAO = "mudanca_funcao"     # Alteracao de cargo/setor
    DEMISSIONAL = "demissional"           # Desligamento


class ExamStatus(str, Enum):
    """Status de um exame medico."""
    SCHEDULED = "scheduled"       # Agendado
    PENDING = "pending"           # Aguardando resultado
    COMPLETED = "completed"       # Concluido
    CANCELLED = "cancelled"       # Cancelado
    NO_SHOW = "no_show"          # Falta
    RESCHEDULED = "rescheduled"  # Reagendado


class FitnessResult(str, Enum):
    """Resultado de aptidao do ASO."""
    APTO = "apto"                              # Apto para funcao
    APTO_RESTRICOES = "apto_com_restricoes"   # Apto com restricoes
    INAPTO_TEMPORARIO = "inapto_temporario"   # Inapto temporariamente
    INAPTO = "inapto"                         # Inapto para funcao


class ComplementaryExam(str, Enum):
    """Exames complementares comuns."""
    HEMOGRAMA = "hemograma"
    GLICEMIA = "glicemia"
    AUDIOMETRIA = "audiometria"
    ACUIDADE_VISUAL = "acuidade_visual"
    ESPIROMETRIA = "espirometria"
    ECG = "eletrocardiograma"
    RX_TORAX = "raio_x_torax"
    RX_COLUNA = "raio_x_coluna"
    EEG = "eletroencefalograma"
    TOXICOLOGICO = "toxicologico"
    PSA = "psa"
    MAMOGRAFIA = "mamografia"
    PAPANICOLAU = "papanicolau"


class MedicalExamError(Exception):
    """Erro em operacao de exame medico."""

    def __init__(self, message: str, exam_id: Optional[str] = None):
        self.message = message
        self.exam_id = exam_id
        super().__init__(self.message)


@dataclass
class ExamRequirement:
    """Requisito de exame para uma funcao/risco."""
    exam_type: ComplementaryExam
    periodicity_months: int          # Periodicidade em meses
    mandatory: bool = True
    risk_factors: List[str] = field(default_factory=list)
    age_min: Optional[int] = None    # Idade minima para exigir
    age_max: Optional[int] = None    # Idade maxima para exigir
    gender: Optional[str] = None     # M, F ou None para ambos


@dataclass
class OccupationalFunction:
    """Funcao ocupacional com requisitos de exames."""
    id: UUID
    name: str
    cbo_code: str                    # Codigo CBO
    department: str
    risk_factors: List[str]          # Riscos ocupacionais
    exam_requirements: List[ExamRequirement] = field(default_factory=list)


@dataclass
class ClinicPartner:
    """Clinica parceira para realizacao de exames."""
    id: UUID
    name: str
    cnpj: str
    address: str
    phone: str
    email: str
    api_integration: bool = False
    api_endpoint: Optional[str] = None
    available_exams: List[ComplementaryExam] = field(default_factory=list)
    working_hours: Dict[str, str] = field(default_factory=dict)


@dataclass
class MedicalExam:
    """Exame medico ocupacional."""
    id: UUID
    employee_id: str
    employee_name: str
    employee_cpf: str
    exam_type: ExamType
    status: ExamStatus
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[str] = None
    clinic_id: Optional[UUID] = None
    clinic_name: Optional[str] = None
    completed_date: Optional[date] = None
    fitness_result: Optional[FitnessResult] = None
    restrictions: Optional[str] = None
    valid_until: Optional[date] = None
    complementary_exams: List[ComplementaryExam] = field(default_factory=list)
    doctor_name: Optional[str] = None
    doctor_crm: Optional[str] = None
    aso_number: Optional[str] = None
    observations: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Verifica se o exame esta valido."""
        if self.status != ExamStatus.COMPLETED:
            return False
        if not self.valid_until:
            return False
        return date.today() <= self.valid_until

    def days_until_expiry(self) -> Optional[int]:
        """Dias ate vencimento."""
        if not self.valid_until:
            return None
        delta = self.valid_until - date.today()
        return delta.days

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "employee_id": self.employee_id,
            "employee_name": self.employee_name,
            "exam_type": self.exam_type.value,
            "status": self.status.value,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "clinic_name": self.clinic_name,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "fitness_result": self.fitness_result.value if self.fitness_result else None,
            "restrictions": self.restrictions,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "complementary_exams": [e.value for e in self.complementary_exams],
            "doctor_name": self.doctor_name,
            "doctor_crm": self.doctor_crm,
            "aso_number": self.aso_number,
            "is_valid": self.is_valid(),
            "days_until_expiry": self.days_until_expiry(),
        }


# SQLAlchemy Models
class MedicalExamModel(Base):
    """Modelo de banco para exames medicos."""
    __tablename__ = "health_medical_exams"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id = Column(String(100), nullable=False, index=True)
    employee_name = Column(String(255), nullable=False)
    employee_cpf = Column(String(14), nullable=False)
    exam_type = Column(String(30), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="scheduled", index=True)
    scheduled_date = Column(Date, nullable=True, index=True)
    scheduled_time = Column(String(5), nullable=True)
    clinic_id = Column(PGUUID(as_uuid=True), nullable=True)
    clinic_name = Column(String(255), nullable=True)
    completed_date = Column(Date, nullable=True)
    fitness_result = Column(String(30), nullable=True)
    restrictions = Column(Text, nullable=True)
    valid_until = Column(Date, nullable=True, index=True)
    complementary_exams = Column(JSONB, default=[])
    doctor_name = Column(String(255), nullable=True)
    doctor_crm = Column(String(20), nullable=True)
    aso_number = Column(String(50), nullable=True)
    observations = Column(Text, nullable=True)
    extra_metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ClinicPartnerModel(Base):
    """Modelo de banco para clinicas parceiras."""
    __tablename__ = "health_clinic_partners"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    cnpj = Column(String(18), nullable=False, unique=True)
    address = Column(Text, nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    api_integration = Column(Boolean, default=False)
    api_endpoint = Column(String(500), nullable=True)
    available_exams = Column(JSONB, default=[])
    working_hours = Column(JSONB, default={})
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PCMSOConfig(BaseModel):
    """Configuracao do sistema PCMSO."""
    default_validity_months: int = Field(default=12, ge=6, le=24)
    alert_days_before_expiry: int = Field(default=30, ge=7)
    auto_schedule_enabled: bool = True
    require_complementary_exams: bool = True
    allow_online_scheduling: bool = True


class MedicalExamManager:
    """
    Gerenciador de exames medicos ocupacionais (PCMSO).

    Coordena agendamento, controle de validade e integracao
    com clinicas parceiras conforme NR-7.

    Example:
        >>> manager = MedicalExamManager(config)
        >>> exam = await manager.schedule_exam(
        ...     employee_id="emp123",
        ...     exam_type=ExamType.PERIODICO
        ... )
    """

    def __init__(self, config: Optional[PCMSOConfig] = None):
        """
        Inicializa o gerenciador PCMSO.

        Args:
            config: Configuracao do sistema.
        """
        self.config = config or PCMSOConfig()
        self._exams: Dict[UUID, MedicalExam] = {}
        self._clinics: Dict[UUID, ClinicPartner] = {}
        self._functions: Dict[UUID, OccupationalFunction] = {}
        logger.info("MedicalExamManager inicializado")

    async def schedule_exam(
        self,
        employee_id: str,
        employee_name: str,
        employee_cpf: str,
        exam_type: ExamType,
        scheduled_date: date,
        scheduled_time: str = "08:00",
        clinic_id: Optional[UUID] = None,
        complementary_exams: Optional[List[ComplementaryExam]] = None,
        created_by: Optional[str] = None
    ) -> MedicalExam:
        """
        Agenda exame medico ocupacional.

        Args:
            employee_id: ID do funcionario.
            employee_name: Nome do funcionario.
            employee_cpf: CPF do funcionario.
            exam_type: Tipo do exame.
            scheduled_date: Data agendada.
            scheduled_time: Horario agendado.
            clinic_id: ID da clinica.
            complementary_exams: Exames complementares.
            created_by: ID de quem agendou.

        Returns:
            MedicalExam: Exame agendado.
        """
        clinic = self._clinics.get(clinic_id) if clinic_id else None

        exam = MedicalExam(
            id=uuid4(),
            employee_id=employee_id,
            employee_name=employee_name,
            employee_cpf=employee_cpf,
            exam_type=exam_type,
            status=ExamStatus.SCHEDULED,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            clinic_id=clinic_id,
            clinic_name=clinic.name if clinic else None,
            complementary_exams=complementary_exams or [],
            created_by=created_by,
        )

        self._exams[exam.id] = exam

        logger.info(
            "Exame agendado: id=%s, employee=%s, type=%s, date=%s",
            exam.id, employee_id, exam_type.value, scheduled_date
        )

        return exam

    async def complete_exam(
        self,
        exam_id: UUID,
        fitness_result: FitnessResult,
        doctor_name: str,
        doctor_crm: str,
        valid_until: date,
        aso_number: Optional[str] = None,
        restrictions: Optional[str] = None,
        observations: Optional[str] = None
    ) -> MedicalExam:
        """
        Registra conclusao de exame.

        Args:
            exam_id: ID do exame.
            fitness_result: Resultado de aptidao.
            doctor_name: Nome do medico.
            doctor_crm: CRM do medico.
            valid_until: Validade do ASO.
            aso_number: Numero do ASO.
            restrictions: Restricoes (se houver).
            observations: Observacoes.

        Returns:
            MedicalExam: Exame atualizado.
        """
        exam = self._exams.get(exam_id)
        if not exam:
            raise MedicalExamError("Exame nao encontrado", str(exam_id))

        exam.status = ExamStatus.COMPLETED
        exam.completed_date = date.today()
        exam.fitness_result = fitness_result
        exam.doctor_name = doctor_name
        exam.doctor_crm = doctor_crm
        exam.valid_until = valid_until
        exam.aso_number = aso_number
        exam.restrictions = restrictions
        exam.observations = observations

        logger.info(
            "Exame concluido: id=%s, result=%s, valid_until=%s",
            exam_id, fitness_result.value, valid_until
        )

        return exam

    async def reschedule_exam(
        self,
        exam_id: UUID,
        new_date: date,
        new_time: str = "08:00",
        reason: Optional[str] = None
    ) -> MedicalExam:
        """
        Reagenda exame medico.

        Args:
            exam_id: ID do exame.
            new_date: Nova data.
            new_time: Novo horario.
            reason: Motivo do reagendamento.

        Returns:
            MedicalExam: Exame reagendado.
        """
        exam = self._exams.get(exam_id)
        if not exam:
            raise MedicalExamError("Exame nao encontrado", str(exam_id))

        old_date = exam.scheduled_date
        exam.scheduled_date = new_date
        exam.scheduled_time = new_time
        exam.status = ExamStatus.RESCHEDULED
        exam.metadata["reschedule_history"] = exam.metadata.get("reschedule_history", [])
        exam.metadata["reschedule_history"].append({
            "old_date": old_date.isoformat() if old_date else None,
            "new_date": new_date.isoformat(),
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        })

        logger.info("Exame reagendado: id=%s, new_date=%s", exam_id, new_date)
        return exam

    async def cancel_exam(
        self,
        exam_id: UUID,
        reason: Optional[str] = None,
        cancelled_by: Optional[str] = None
    ) -> MedicalExam:
        """
        Cancela exame medico.

        Args:
            exam_id: ID do exame.
            reason: Motivo do cancelamento.
            cancelled_by: ID de quem cancelou.

        Returns:
            MedicalExam: Exame cancelado.
        """
        exam = self._exams.get(exam_id)
        if not exam:
            raise MedicalExamError("Exame nao encontrado", str(exam_id))

        exam.status = ExamStatus.CANCELLED
        exam.metadata["cancellation"] = {
            "reason": reason,
            "cancelled_by": cancelled_by,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info("Exame cancelado: id=%s, reason=%s", exam_id, reason)
        return exam

    async def get_exam(self, exam_id: UUID) -> Optional[MedicalExam]:
        """Recupera exame por ID."""
        return self._exams.get(exam_id)

    async def get_employee_exams(
        self,
        employee_id: str,
        include_expired: bool = False
    ) -> List[MedicalExam]:
        """
        Recupera exames de um funcionario.

        Args:
            employee_id: ID do funcionario.
            include_expired: Se inclui exames expirados.

        Returns:
            List[MedicalExam]: Lista de exames.
        """
        exams = [e for e in self._exams.values() if e.employee_id == employee_id]

        if not include_expired:
            exams = [e for e in exams if e.is_valid() or e.status == ExamStatus.SCHEDULED]

        return sorted(exams, key=lambda x: x.created_at, reverse=True)

    async def get_expiring_exams(
        self,
        days: Optional[int] = None
    ) -> List[MedicalExam]:
        """
        Lista exames proximos de vencer.

        Args:
            days: Dias ate vencimento (usa config se None).

        Returns:
            List[MedicalExam]: Exames proximos de vencer.
        """
        days = days or self.config.alert_days_before_expiry
        cutoff_date = date.today() + timedelta(days=days)

        expiring = []
        for exam in self._exams.values():
            if exam.status == ExamStatus.COMPLETED and exam.valid_until:
                if date.today() <= exam.valid_until <= cutoff_date:
                    expiring.append(exam)

        return sorted(expiring, key=lambda x: x.valid_until)

    async def get_expired_exams(self) -> List[MedicalExam]:
        """Lista exames vencidos."""
        today = date.today()
        return [
            e for e in self._exams.values()
            if e.status == ExamStatus.COMPLETED and e.valid_until and e.valid_until < today
        ]

    async def get_pending_exams(self) -> List[MedicalExam]:
        """Lista exames pendentes (agendados)."""
        return [
            e for e in self._exams.values()
            if e.status in [ExamStatus.SCHEDULED, ExamStatus.RESCHEDULED]
        ]

    async def check_employee_compliance(
        self,
        employee_id: str,
        function_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Verifica compliance de exames de um funcionario.

        Args:
            employee_id: ID do funcionario.
            function_id: ID da funcao (para requisitos especificos).

        Returns:
            Dict: Status de compliance.
        """
        exams = await self.get_employee_exams(employee_id)
        valid_exams = [e for e in exams if e.is_valid()]

        compliance = {
            "employee_id": employee_id,
            "is_compliant": False,
            "has_valid_aso": False,
            "valid_exams_count": len(valid_exams),
            "expiring_soon": [],
            "missing_exams": [],
            "last_exam_date": None,
            "next_exam_due": None,
        }

        # Verifica ASO valido
        completed = [e for e in valid_exams if e.fitness_result]
        if completed:
            compliance["has_valid_aso"] = True
            compliance["last_exam_date"] = max(e.completed_date for e in completed).isoformat()

        # Verifica exames proximos de vencer
        for exam in valid_exams:
            days_left = exam.days_until_expiry()
            if days_left and days_left <= self.config.alert_days_before_expiry:
                compliance["expiring_soon"].append({
                    "exam_type": exam.exam_type.value,
                    "valid_until": exam.valid_until.isoformat(),
                    "days_remaining": days_left,
                })

        # Verifica requisitos da funcao
        if function_id:
            function = self._functions.get(function_id)
            if function:
                completed_types = {e.exam_type for e in valid_exams}
                # Verificar exames complementares obrigatorios
                # (simplificado - em producao seria mais completo)

        compliance["is_compliant"] = compliance["has_valid_aso"] and not compliance["missing_exams"]

        return compliance

    async def generate_aso_report(self, exam_id: UUID) -> Dict[str, Any]:
        """
        Gera relatorio ASO (Atestado de Saude Ocupacional).

        Args:
            exam_id: ID do exame.

        Returns:
            Dict: Dados do ASO.
        """
        exam = self._exams.get(exam_id)
        if not exam:
            raise MedicalExamError("Exame nao encontrado", str(exam_id))

        if exam.status != ExamStatus.COMPLETED:
            raise MedicalExamError("Exame nao concluido", str(exam_id))

        aso = {
            "aso_number": exam.aso_number or f"ASO-{exam.id.hex[:8].upper()}",
            "exam_type": exam.exam_type.value,
            "issue_date": exam.completed_date.isoformat() if exam.completed_date else None,
            "valid_until": exam.valid_until.isoformat() if exam.valid_until else None,
            "employee": {
                "name": exam.employee_name,
                "cpf": exam.employee_cpf,
            },
            "result": {
                "fitness": exam.fitness_result.value if exam.fitness_result else None,
                "restrictions": exam.restrictions,
            },
            "complementary_exams": [e.value for e in exam.complementary_exams],
            "physician": {
                "name": exam.doctor_name,
                "crm": exam.doctor_crm,
            },
            "observations": exam.observations,
            "clinic": exam.clinic_name,
        }

        return aso

    async def register_clinic(self, clinic: ClinicPartner) -> ClinicPartner:
        """Registra clinica parceira."""
        self._clinics[clinic.id] = clinic
        logger.info("Clinica registrada: %s", clinic.name)
        return clinic

    async def list_clinics(self, only_active: bool = True) -> List[ClinicPartner]:
        """Lista clinicas parceiras."""
        clinics = list(self._clinics.values())
        # Aqui seria filtrado por active se fosse do banco
        return clinics

    async def register_function(self, function: OccupationalFunction) -> OccupationalFunction:
        """Registra funcao ocupacional."""
        self._functions[function.id] = function
        logger.info("Funcao registrada: %s (CBO: %s)", function.name, function.cbo_code)
        return function

    async def get_compliance_summary(self) -> Dict[str, Any]:
        """
        Gera resumo de compliance PCMSO.

        Returns:
            Dict: Metricas de compliance.
        """
        all_exams = list(self._exams.values())
        valid_exams = [e for e in all_exams if e.is_valid()]
        expired = await self.get_expired_exams()
        expiring = await self.get_expiring_exams()

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "total_exams": len(all_exams),
            "valid_exams": len(valid_exams),
            "expired_exams": len(expired),
            "expiring_soon": len(expiring),
            "pending_scheduling": len([e for e in all_exams if e.status == ExamStatus.SCHEDULED]),
            "compliance_rate": round(len(valid_exams) / len(all_exams) * 100, 2) if all_exams else 0,
            "by_exam_type": self._count_by_type(all_exams),
            "by_result": self._count_by_result(valid_exams),
        }

    def _count_by_type(self, exams: List[MedicalExam]) -> Dict[str, int]:
        """Conta exames por tipo."""
        counts = {}
        for exam in exams:
            t = exam.exam_type.value
            counts[t] = counts.get(t, 0) + 1
        return counts

    def _count_by_result(self, exams: List[MedicalExam]) -> Dict[str, int]:
        """Conta exames por resultado."""
        counts = {}
        for exam in exams:
            if exam.fitness_result:
                r = exam.fitness_result.value
                counts[r] = counts.get(r, 0) + 1
        return counts


# Singleton
_exam_manager: Optional[MedicalExamManager] = None


def get_exam_manager() -> MedicalExamManager:
    """Retorna instancia singleton do MedicalExamManager."""
    global _exam_manager
    if _exam_manager is None:
        _exam_manager = MedicalExamManager()
    return _exam_manager


def init_exam_manager(config: Optional[PCMSOConfig] = None) -> MedicalExamManager:
    """Inicializa o MedicalExamManager singleton."""
    global _exam_manager
    _exam_manager = MedicalExamManager(config)
    return _exam_manager
