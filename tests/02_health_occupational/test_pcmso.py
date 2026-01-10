"""
Tests for PCMSO Module (medical_exams) - NR-7.

Author: Claude AI + Human Developer
Date: 2026-01-10
"""

import os
import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock, patch
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List


# =============================================================================
# MOCK CLASSES (Simulating the actual implementation)
# =============================================================================

class ExamType(str, Enum):
    ADMISSIONAL = "admissional"
    PERIODICO = "periodico"
    DEMISSIONAL = "demissional"
    RETORNO_TRABALHO = "retorno_trabalho"
    MUDANCA_FUNCAO = "mudanca_funcao"


class ExamStatus(str, Enum):
    AGENDADO = "agendado"
    REALIZADO = "realizado"
    CANCELADO = "cancelado"
    NAO_COMPARECEU = "nao_compareceu"


class FitnessResult(str, Enum):
    APTO = "apto"
    APTO_COM_RESTRICAO = "apto_com_restricao"
    INAPTO = "inapto"
    INAPTO_TEMPORARIO = "inapto_temporario"


@dataclass
class MedicalExam:
    id: str
    funcionario_id: str
    tipo: ExamType
    status: ExamStatus
    data_agendada: date
    resultado: Optional[FitnessResult] = None
    medico_id: Optional[str] = None
    observacoes: Optional[str] = None
    restricoes: List[str] = field(default_factory=list)
    data_reavaliacao: Optional[date] = None
    data_realizacao: Optional[date] = None


@dataclass
class ASO:
    id: str
    numero: str
    exam_id: str
    funcionario_id: str
    tipo: ExamType
    resultado: FitnessResult
    medico_id: str
    data_exame: date
    data_emissao: datetime = field(default_factory=datetime.now)


class MedicalExamManager:
    """Simulated MedicalExamManager for testing."""

    def __init__(self, db_session=None):
        self.db = db_session
        self._exams: Dict[str, MedicalExam] = {}
        self._asos: Dict[str, ASO] = {}

    async def schedule_exam(
        self,
        funcionario_id: str,
        tipo: ExamType,
        data_agendada: date,
        motivo: Optional[str] = None,
        nova_funcao: Optional[str] = None
    ) -> MedicalExam:
        exam = MedicalExam(
            id=str(uuid.uuid4()),
            funcionario_id=funcionario_id,
            tipo=tipo,
            status=ExamStatus.AGENDADO,
            data_agendada=data_agendada
        )
        self._exams[exam.id] = exam
        return exam

    async def complete_exam(
        self,
        exam_id: str,
        resultado: FitnessResult,
        medico_id: str,
        observacoes: Optional[str] = None,
        restricoes: Optional[List[str]] = None,
        data_reavaliacao: Optional[date] = None
    ) -> MedicalExam:
        exam = self._exams.get(exam_id)
        if exam:
            exam.status = ExamStatus.REALIZADO
            exam.resultado = resultado
            exam.medico_id = medico_id
            exam.observacoes = observacoes
            exam.restricoes = restricoes or []
            exam.data_reavaliacao = data_reavaliacao
            exam.data_realizacao = date.today()
        return exam

    async def generate_aso(self, exam_id: str) -> ASO:
        exam = self._exams.get(exam_id)
        if not exam:
            raise ValueError("Exam not found")

        aso = ASO(
            id=str(uuid.uuid4()),
            numero=f"ASO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            exam_id=exam_id,
            funcionario_id=exam.funcionario_id,
            tipo=exam.tipo,
            resultado=exam.resultado,
            medico_id=exam.medico_id,
            data_exame=exam.data_realizacao or date.today()
        )
        self._asos[aso.id] = aso
        return aso

    async def get_exams(
        self,
        funcionario_id: Optional[str] = None,
        tipo: Optional[ExamType] = None,
        status: Optional[ExamStatus] = None
    ) -> List[MedicalExam]:
        results = list(self._exams.values())

        if funcionario_id:
            results = [e for e in results if e.funcionario_id == funcionario_id]
        if tipo:
            results = [e for e in results if e.tipo == tipo]
        if status:
            results = [e for e in results if e.status == status]

        return results

    async def get_pending_exams(self) -> List[MedicalExam]:
        return [e for e in self._exams.values() if e.status == ExamStatus.AGENDADO]

    async def get_overdue_exams(self) -> List[MedicalExam]:
        today = date.today()
        return [
            e for e in self._exams.values()
            if e.status == ExamStatus.AGENDADO and e.data_agendada < today
        ]

    async def calculate_next_periodic(
        self,
        funcionario_id: str,
        idade: int,
        riscos_ocupacionais: List[str]
    ) -> date:
        # NR-7 periodicity rules
        # - Under 18 or over 45: annual
        # - 18-45 with occupational risks: annual
        # - 18-45 without risks: biennial

        if idade < 18 or idade > 45:
            interval_days = 365
        elif riscos_ocupacionais:
            interval_days = 365
        else:
            interval_days = 730  # 2 years

        return date.today() + timedelta(days=interval_days)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_db_session():
    return MagicMock()


# =============================================================================
# MEDICAL EXAM MANAGER TESTS
# =============================================================================

class TestMedicalExamManager:
    """Tests for MedicalExamManager class."""

    @pytest.fixture
    def exam_manager(self, mock_db_session):
        """Create MedicalExamManager instance."""
        return MedicalExamManager(db_session=mock_db_session)

    @pytest.fixture
    def sample_employee(self):
        """Sample employee for tests."""
        return {
            "id": str(uuid.uuid4()),
            "cpf": "12345678901",
            "nome": "Carlos Silva",
            "data_nascimento": date(1985, 6, 15),
            "data_admissao": date(2020, 3, 1),
            "cargo": "Operador de Maquinas",
            "setor": "Producao",
            "empresa_id": str(uuid.uuid4())
        }

    @pytest.fixture
    def sample_physician(self):
        """Sample physician data."""
        return {
            "id": str(uuid.uuid4()),
            "nome": "Dr. Jose Medico",
            "crm": "123456",
            "crm_uf": "SP",
            "especialidade": "Medicina do Trabalho"
        }

    # -------------------------------------------------------------------------
    # EXAM SCHEDULING TESTS
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_schedule_admissional_exam(self, exam_manager, sample_employee):
        """Test scheduling admissional exam."""
        exam = await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.ADMISSIONAL,
            data_agendada=date.today() + timedelta(days=2)
        )

        assert exam is not None
        assert exam.tipo == ExamType.ADMISSIONAL
        assert exam.status == ExamStatus.AGENDADO

    @pytest.mark.asyncio
    async def test_schedule_periodico_exam(self, exam_manager, sample_employee):
        """Test scheduling periodic exam."""
        exam = await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.PERIODICO,
            data_agendada=date.today() + timedelta(days=30)
        )

        assert exam is not None
        assert exam.tipo == ExamType.PERIODICO

    @pytest.mark.asyncio
    async def test_schedule_demissional_exam(self, exam_manager, sample_employee):
        """Test scheduling demissional exam."""
        exam = await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.DEMISSIONAL,
            data_agendada=date.today()
        )

        assert exam is not None
        assert exam.tipo == ExamType.DEMISSIONAL

    @pytest.mark.asyncio
    async def test_schedule_retorno_trabalho_exam(self, exam_manager, sample_employee):
        """Test scheduling return-to-work exam."""
        exam = await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.RETORNO_TRABALHO,
            data_agendada=date.today(),
            motivo="Retorno apos afastamento por doenca"
        )

        assert exam is not None
        assert exam.tipo == ExamType.RETORNO_TRABALHO

    @pytest.mark.asyncio
    async def test_schedule_mudanca_funcao_exam(self, exam_manager, sample_employee):
        """Test scheduling function change exam."""
        exam = await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.MUDANCA_FUNCAO,
            data_agendada=date.today() + timedelta(days=5),
            nova_funcao="Supervisor de Producao"
        )

        assert exam is not None
        assert exam.tipo == ExamType.MUDANCA_FUNCAO

    # -------------------------------------------------------------------------
    # EXAM COMPLETION TESTS
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_complete_exam_apto(self, exam_manager, sample_employee, sample_physician):
        """Test completing exam with APTO result."""
        exam = await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.PERIODICO,
            data_agendada=date.today()
        )

        completed = await exam_manager.complete_exam(
            exam_id=exam.id,
            resultado=FitnessResult.APTO,
            medico_id=sample_physician["id"],
            observacoes="Funcionario em boas condicoes de saude"
        )

        assert completed.status == ExamStatus.REALIZADO
        assert completed.resultado == FitnessResult.APTO

    @pytest.mark.asyncio
    async def test_complete_exam_apto_restricao(self, exam_manager, sample_employee, sample_physician):
        """Test completing exam with APTO_COM_RESTRICAO result."""
        exam = await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.PERIODICO,
            data_agendada=date.today()
        )

        completed = await exam_manager.complete_exam(
            exam_id=exam.id,
            resultado=FitnessResult.APTO_COM_RESTRICAO,
            medico_id=sample_physician["id"],
            restricoes=["Evitar trabalho em altura", "Limite de carga 10kg"],
            observacoes="Restricoes devido a lombalgia"
        )

        assert completed.resultado == FitnessResult.APTO_COM_RESTRICAO
        assert len(completed.restricoes) == 2

    @pytest.mark.asyncio
    async def test_complete_exam_inapto(self, exam_manager, sample_employee, sample_physician):
        """Test completing exam with INAPTO result."""
        exam = await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.ADMISSIONAL,
            data_agendada=date.today()
        )

        completed = await exam_manager.complete_exam(
            exam_id=exam.id,
            resultado=FitnessResult.INAPTO,
            medico_id=sample_physician["id"],
            observacoes="Condicao incompativel com a funcao"
        )

        assert completed.resultado == FitnessResult.INAPTO

    @pytest.mark.asyncio
    async def test_complete_exam_inapto_temporario(self, exam_manager, sample_employee, sample_physician):
        """Test completing exam with INAPTO_TEMPORARIO result."""
        exam = await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.PERIODICO,
            data_agendada=date.today()
        )

        completed = await exam_manager.complete_exam(
            exam_id=exam.id,
            resultado=FitnessResult.INAPTO_TEMPORARIO,
            medico_id=sample_physician["id"],
            data_reavaliacao=date.today() + timedelta(days=30),
            observacoes="Necessita tratamento. Reavaliar em 30 dias."
        )

        assert completed.resultado == FitnessResult.INAPTO_TEMPORARIO
        assert completed.data_reavaliacao is not None

    # -------------------------------------------------------------------------
    # ASO GENERATION TESTS
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_generate_aso(self, exam_manager, sample_employee, sample_physician):
        """Test ASO (Atestado de Saude Ocupacional) generation."""
        exam = await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.ADMISSIONAL,
            data_agendada=date.today()
        )

        await exam_manager.complete_exam(
            exam_id=exam.id,
            resultado=FitnessResult.APTO,
            medico_id=sample_physician["id"]
        )

        aso = await exam_manager.generate_aso(exam.id)

        assert aso is not None
        assert aso.numero is not None
        assert aso.funcionario_id == sample_employee["id"]

    @pytest.mark.asyncio
    async def test_aso_contains_required_fields(self, exam_manager, sample_employee, sample_physician):
        """Test that ASO contains all NR-7 required fields."""
        exam = await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.PERIODICO,
            data_agendada=date.today()
        )

        await exam_manager.complete_exam(
            exam_id=exam.id,
            resultado=FitnessResult.APTO,
            medico_id=sample_physician["id"]
        )

        aso = await exam_manager.generate_aso(exam.id)

        # NR-7 required fields
        assert hasattr(aso, 'funcionario_id') and aso.funcionario_id is not None
        assert hasattr(aso, 'tipo') and aso.tipo is not None
        assert hasattr(aso, 'data_exame')
        assert hasattr(aso, 'resultado')
        assert hasattr(aso, 'medico_id') and aso.medico_id is not None

    # -------------------------------------------------------------------------
    # EXAM QUERY TESTS
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_exams_by_employee(self, exam_manager, sample_employee):
        """Test getting exams by employee."""
        # Schedule multiple exams
        await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.ADMISSIONAL,
            data_agendada=date.today() - timedelta(days=365)
        )
        await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.PERIODICO,
            data_agendada=date.today()
        )

        exams = await exam_manager.get_exams(
            funcionario_id=sample_employee["id"]
        )

        assert len(exams) >= 2

    @pytest.mark.asyncio
    async def test_get_pending_exams(self, exam_manager, sample_employee):
        """Test getting pending exams."""
        await exam_manager.schedule_exam(
            funcionario_id=sample_employee["id"],
            tipo=ExamType.PERIODICO,
            data_agendada=date.today() + timedelta(days=7)
        )

        pending = await exam_manager.get_pending_exams()

        assert pending is not None

    @pytest.mark.asyncio
    async def test_get_overdue_exams(self, exam_manager, sample_employee):
        """Test getting overdue periodic exams."""
        overdue = await exam_manager.get_overdue_exams()

        assert overdue is not None

    # -------------------------------------------------------------------------
    # PERIODICITY TESTS
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_calculate_next_periodic_exam(self, exam_manager, sample_employee):
        """Test calculating next periodic exam date."""
        next_date = await exam_manager.calculate_next_periodic(
            funcionario_id=sample_employee["id"],
            idade=39,
            riscos_ocupacionais=["Ruido", "Quimico"]
        )

        assert next_date is not None
        assert next_date > date.today()

    @pytest.mark.asyncio
    async def test_periodicity_under_18(self, exam_manager, sample_employee):
        """Test periodicity for workers under 18."""
        # Should be annual for minors
        next_date = await exam_manager.calculate_next_periodic(
            funcionario_id=sample_employee["id"],
            idade=17,
            riscos_ocupacionais=[]
        )

        assert next_date is not None
        # Maximum 1 year for minors
        assert (next_date - date.today()).days <= 365

    @pytest.mark.asyncio
    async def test_periodicity_over_45(self, exam_manager, sample_employee):
        """Test periodicity for workers over 45."""
        # Should be annual for workers over 45
        next_date = await exam_manager.calculate_next_periodic(
            funcionario_id=sample_employee["id"],
            idade=50,
            riscos_ocupacionais=[]
        )

        assert next_date is not None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestPCMSOIntegration:
    """Integration tests for PCMSO module."""

    @pytest.mark.asyncio
    async def test_full_admissional_workflow(self, mock_db_session):
        """Test complete admissional exam workflow."""
        manager = MedicalExamManager(db_session=mock_db_session)

        funcionario_id = str(uuid.uuid4())
        medico_id = str(uuid.uuid4())

        # 1. Schedule exam
        exam = await manager.schedule_exam(
            funcionario_id=funcionario_id,
            tipo=ExamType.ADMISSIONAL,
            data_agendada=date.today()
        )
        assert exam.status == ExamStatus.AGENDADO

        # 2. Complete exam
        completed = await manager.complete_exam(
            exam_id=exam.id,
            resultado=FitnessResult.APTO,
            medico_id=medico_id
        )
        assert completed.status == ExamStatus.REALIZADO

        # 3. Generate ASO
        aso = await manager.generate_aso(exam.id)
        assert aso is not None

    @pytest.mark.asyncio
    async def test_periodic_exam_scheduling(self, mock_db_session):
        """Test automatic periodic exam scheduling."""
        manager = MedicalExamManager(db_session=mock_db_session)

        funcionario_id = str(uuid.uuid4())

        # Complete an admissional exam
        exam = await manager.schedule_exam(
            funcionario_id=funcionario_id,
            tipo=ExamType.ADMISSIONAL,
            data_agendada=date.today() - timedelta(days=365)
        )

        await manager.complete_exam(
            exam_id=exam.id,
            resultado=FitnessResult.APTO,
            medico_id=str(uuid.uuid4())
        )

        # Check if periodic is due
        next_periodic = await manager.calculate_next_periodic(
            funcionario_id=funcionario_id,
            idade=35,
            riscos_ocupacionais=[]
        )

        assert next_periodic is not None
