"""
Testes do modulo PCMSO (NR-7) - Programa de Controle Medico de Saude Ocupacional.

Cobre: models, schemas, repository, service e controller.
Usa mocks para evitar dependencia de banco de dados real.
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest

# ==============================================================================
# Testes dos Models
# ==============================================================================


class TestPCMSOModels:
    """Testes dos modelos SQLAlchemy do PCMSO."""

    def test_exam_type_enum(self):
        from modules.health_occupational.models.pcmso import ExamType

        assert ExamType.ADMISSIONAL == "admissional"
        assert ExamType.PERIODICO == "periodico"
        assert ExamType.RETORNO_TRABALHO == "retorno_trabalho"
        assert ExamType.MUDANCA_FUNCAO == "mudanca_funcao"
        assert ExamType.DEMISSIONAL == "demissional"

    def test_exam_status_enum(self):
        from modules.health_occupational.models.pcmso import ExamStatus

        assert ExamStatus.AGENDADO == "agendado"
        assert ExamStatus.CONFIRMADO == "confirmado"
        assert ExamStatus.REALIZADO == "realizado"
        assert ExamStatus.CANCELADO == "cancelado"
        assert ExamStatus.NAO_COMPARECEU == "nao_compareceu"

    def test_fitness_result_enum(self):
        from modules.health_occupational.models.pcmso import FitnessResult

        assert FitnessResult.APTO == "apto"
        assert FitnessResult.INAPTO == "inapto"
        assert FitnessResult.APTO_COM_RESTRICOES == "apto_com_restricoes"

    def test_medical_exam_tablename(self):
        from modules.health_occupational.models.pcmso import MedicalExam

        assert MedicalExam.__tablename__ == "health_medical_exams"

    def test_aso_tablename(self):
        from modules.health_occupational.models.pcmso import ASO

        assert ASO.__tablename__ == "health_asos"

    def test_complementary_exam_tablename(self):
        from modules.health_occupational.models.pcmso import ComplementaryExam

        assert ComplementaryExam.__tablename__ == "health_complementary_exams"

    def test_medical_exam_esta_pendente_agendado(self):
        from modules.health_occupational.models.pcmso import ExamStatus, MedicalExam

        exam = MedicalExam()
        exam.status = ExamStatus.AGENDADO.value
        assert exam.esta_pendente is True

    def test_medical_exam_esta_pendente_confirmado(self):
        from modules.health_occupational.models.pcmso import ExamStatus, MedicalExam

        exam = MedicalExam()
        exam.status = ExamStatus.CONFIRMADO.value
        assert exam.esta_pendente is True

    def test_medical_exam_esta_pendente_realizado(self):
        from modules.health_occupational.models.pcmso import ExamStatus, MedicalExam

        exam = MedicalExam()
        exam.status = ExamStatus.REALIZADO.value
        assert exam.esta_pendente is False

    def test_medical_exam_repr(self):
        from modules.health_occupational.models.pcmso import MedicalExam

        exam = MedicalExam()
        exam.tipo_exame = "admissional"
        exam.data_agendamento = date(2026, 4, 1)
        r = repr(exam)
        assert "admissional" in r
        assert "2026-04-01" in r

    def test_aso_esta_vencido_false(self):
        from modules.health_occupational.models.pcmso import ASO

        aso = ASO()
        aso.data_vencimento = date.today() + timedelta(days=30)
        assert aso.esta_vencido is False

    def test_aso_esta_vencido_true(self):
        from modules.health_occupational.models.pcmso import ASO

        aso = ASO()
        aso.data_vencimento = date.today() - timedelta(days=1)
        assert aso.esta_vencido is True

    def test_aso_dias_para_vencer(self):
        from modules.health_occupational.models.pcmso import ASO

        aso = ASO()
        aso.data_vencimento = date.today() + timedelta(days=10)
        assert aso.dias_para_vencer == 10

    def test_aso_dias_para_vencer_vencido(self):
        from modules.health_occupational.models.pcmso import ASO

        aso = ASO()
        aso.data_vencimento = date.today() - timedelta(days=5)
        assert aso.dias_para_vencer == 0

    def test_aso_repr(self):
        from modules.health_occupational.models.pcmso import ASO

        aso = ASO()
        aso.numero_aso = "ASO-2026-000001"
        aso.resultado = "apto"
        r = repr(aso)
        assert "ASO-2026-000001" in r
        assert "apto" in r

    def test_complementary_exam_repr(self):
        from modules.health_occupational.models.pcmso import ComplementaryExam

        exam = ComplementaryExam()
        exam.nome = "Audiometria"
        r = repr(exam)
        assert "Audiometria" in r


# ==============================================================================
# Testes dos Schemas
# ==============================================================================


class TestPCMSOSchemas:
    """Testes dos schemas Pydantic do PCMSO."""

    def test_medical_exam_request_valid(self):
        from modules.health_occupational.schemas.pcmso import MedicalExamRequest

        req = MedicalExamRequest(
            funcionario_id=uuid4(),
            tipo_exame="admissional",
            data_agendamento=date.today() + timedelta(days=1),
            funcao="Vigilante",
            setor="Operacional",
        )
        assert req.tipo_exame == "admissional"
        assert req.funcao == "Vigilante"
        assert req.riscos == []
        assert req.exames_complementares == []

    def test_medical_exam_request_data_passado_invalida(self):
        from pydantic import ValidationError

        from modules.health_occupational.schemas.pcmso import MedicalExamRequest

        with pytest.raises(ValidationError):
            MedicalExamRequest(
                funcionario_id=uuid4(),
                tipo_exame="admissional",
                data_agendamento=date.today() - timedelta(days=1),
                funcao="Vigilante",
                setor="Operacional",
            )

    def test_medical_exam_request_tipo_invalido(self):
        from pydantic import ValidationError

        from modules.health_occupational.schemas.pcmso import MedicalExamRequest

        with pytest.raises(ValidationError):
            MedicalExamRequest(
                funcionario_id=uuid4(),
                tipo_exame="tipo_invalido",
                data_agendamento=date.today() + timedelta(days=1),
                funcao="Vigilante",
                setor="Operacional",
            )

    def test_medical_exam_request_com_riscos_e_complementares(self):
        from modules.health_occupational.schemas.pcmso import MedicalExamRequest

        req = MedicalExamRequest(
            funcionario_id=uuid4(),
            tipo_exame="periodico",
            data_agendamento=date.today() + timedelta(days=5),
            funcao="Supervisor",
            setor="Seguranca",
            riscos=["quimico", "fisico"],
            exames_complementares=["hemograma", "audiometria"],
            hora_agendamento="09:00",
            local_realizacao="Clinica Central",
        )
        assert "quimico" in req.riscos
        assert "hemograma" in req.exames_complementares
        assert req.hora_agendamento == "09:00"

    def test_medical_exam_update_request(self):
        from modules.health_occupational.schemas.pcmso import MedicalExamUpdateRequest

        req = MedicalExamUpdateRequest(
            status="realizado",
            data_realizacao=datetime.utcnow(),
        )
        assert req.status == "realizado"

    def test_medical_exam_update_request_status_invalido(self):
        from pydantic import ValidationError

        from modules.health_occupational.schemas.pcmso import MedicalExamUpdateRequest

        with pytest.raises(ValidationError):
            MedicalExamUpdateRequest(status="status_invalido")

    def test_aso_request_valid(self):
        from modules.health_occupational.schemas.pcmso import ASORequest

        req = ASORequest(
            exame_id=uuid4(),
            resultado="apto",
            validade_dias=365,
            medico_responsavel="Dr. Silva",
            crm="12345",
            uf_crm="AM",
        )
        assert req.resultado == "apto"
        assert req.validade_dias == 365

    def test_aso_request_resultado_invalido(self):
        from pydantic import ValidationError

        from modules.health_occupational.schemas.pcmso import ASORequest

        with pytest.raises(ValidationError):
            ASORequest(
                exame_id=uuid4(),
                resultado="resultado_invalido",
                medico_responsavel="Dr. Silva",
                crm="12345",
            )

    def test_aso_request_apto_com_restricoes_sem_restricoes(self):
        from pydantic import ValidationError

        from modules.health_occupational.schemas.pcmso import ASORequest

        with pytest.raises(ValidationError):
            ASORequest(
                exame_id=uuid4(),
                resultado="apto_com_restricoes",
                restricoes=None,
                medico_responsavel="Dr. Silva",
                crm="12345",
            )

    def test_aso_request_apto_com_restricoes_com_restricoes(self):
        from modules.health_occupational.schemas.pcmso import ASORequest

        req = ASORequest(
            exame_id=uuid4(),
            resultado="apto_com_restricoes",
            restricoes=["Sem trabalho em altura"],
            medico_responsavel="Dr. Costa",
            crm="67890",
        )
        assert req.restricoes == ["Sem trabalho em altura"]

    def test_aso_update_request(self):
        from modules.health_occupational.schemas.pcmso import ASOUpdateRequest

        req = ASOUpdateRequest(assinatura_funcionario=True)
        assert req.assinatura_funcionario is True

    def test_standard_response_import(self):
        from modules.health_occupational.schemas.common import StandardResponse

        resp = StandardResponse(success=True, message="OK", data={"key": "value"})
        assert resp.success is True
        assert resp.message == "OK"

    def test_complementary_exam_request(self):
        from modules.health_occupational.schemas.pcmso import ComplementaryExamRequest

        req = ComplementaryExamRequest(
            exame_principal_id=uuid4(),
            nome="Hemograma",
            codigo="TUSS-123",
            laboratorio="Lab Central",
        )
        assert req.nome == "Hemograma"

    def test_complementary_exam_update_request(self):
        from modules.health_occupational.schemas.pcmso import ComplementaryExamUpdateRequest

        req = ComplementaryExamUpdateRequest(
            resultado="Normal",
            normal=True,
            status="realizado",
        )
        assert req.normal is True


# ==============================================================================
# Testes do Repository
# ==============================================================================


class TestPCMSORepository:
    """Testes do PCMSORepository com DB mockado."""

    def _make_db(self):
        db = MagicMock()
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        db.delete = MagicMock()
        return db

    def _make_exam(self, status="agendado"):
        from modules.health_occupational.models.pcmso import MedicalExam

        exam = MedicalExam()
        exam.id = uuid4()
        exam.funcionario_id = uuid4()
        exam.tipo_exame = "admissional"
        exam.status = status
        exam.funcao = "Vigilante"
        exam.setor = "Operacional"
        exam.riscos = []
        exam.exames_complementares = []
        exam.data_agendamento = date.today() + timedelta(days=1)
        exam.created_at = datetime.utcnow()
        exam.updated_at = datetime.utcnow()
        return exam

    def _make_aso(self):
        from modules.health_occupational.models.pcmso import ASO

        aso = ASO()
        aso.id = uuid4()
        aso.exame_id = uuid4()
        aso.resultado = "apto"
        aso.restricoes = []
        aso.data_emissao = datetime.utcnow()
        aso.validade_dias = 365
        aso.data_vencimento = date.today() + timedelta(days=365)
        aso.medico_responsavel = "Dr. Silva"
        aso.crm = "12345"
        aso.uf_crm = "AM"
        aso.numero_aso = "ASO-2026-000001"
        aso.assinatura_medico = True
        aso.assinatura_funcionario = False
        aso.ativo = True
        aso.cancelado = False
        aso.created_at = datetime.utcnow()
        return aso

    def test_repository_import(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        assert PCMSORepository is not None

    def test_create_exam(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        repo = PCMSORepository(db=db)
        exam = self._make_exam()

        result = repo.create_exam(exam)

        db.add.assert_called_once_with(exam)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(exam)
        assert result is exam

    def test_get_exam_by_id_found(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        exam = self._make_exam()
        db.query.return_value.filter.return_value.first.return_value = exam

        repo = PCMSORepository(db=db)
        result = repo.get_exam_by_id(exam.id)
        assert result is exam

    def test_get_exam_by_id_not_found(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        repo = PCMSORepository(db=db)
        result = repo.get_exam_by_id(uuid4())
        assert result is None

    def test_get_exams_by_funcionario(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        exams = [self._make_exam(), self._make_exam()]
        db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = exams

        repo = PCMSORepository(db=db)
        result = repo.get_exams_by_funcionario(uuid4())
        assert result is exams

    def test_get_exams_by_funcionario_com_filtros(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        db.query.return_value.filter.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        repo = PCMSORepository(db=db)
        result = repo.get_exams_by_funcionario(uuid4(), status="agendado", tipo="periodico")
        assert result == []

    def test_count_exams_by_funcionario(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        db.query.return_value.filter.return_value.count.return_value = 5

        repo = PCMSORepository(db=db)
        result = repo.count_exams_by_funcionario(uuid4())
        assert result == 5

    def test_get_pending_exams(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        exams = [self._make_exam("agendado"), self._make_exam("confirmado")]
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = exams

        repo = PCMSORepository(db=db)
        result = repo.get_pending_exams(days_ahead=30)
        assert len(result) == 2

    def test_update_exam(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        exam = self._make_exam()

        repo = PCMSORepository(db=db)
        result = repo.update_exam(exam)

        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(exam)
        assert result is exam

    def test_delete_exam_found(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        exam = self._make_exam()
        db.query.return_value.filter.return_value.first.return_value = exam

        repo = PCMSORepository(db=db)
        result = repo.delete_exam(exam.id)

        db.delete.assert_called_once_with(exam)
        db.commit.assert_called_once()
        assert result is True

    def test_delete_exam_not_found(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        repo = PCMSORepository(db=db)
        result = repo.delete_exam(uuid4())
        assert result is False

    def test_create_aso(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        aso = self._make_aso()

        repo = PCMSORepository(db=db)
        result = repo.create_aso(aso)

        db.add.assert_called_once_with(aso)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(aso)
        assert result is aso

    def test_get_aso_by_id_found(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        aso = self._make_aso()
        db.query.return_value.filter.return_value.first.return_value = aso

        repo = PCMSORepository(db=db)
        result = repo.get_aso_by_id(aso.id)
        assert result is aso

    def test_get_aso_by_exam(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        aso = self._make_aso()
        db.query.return_value.filter.return_value.first.return_value = aso

        repo = PCMSORepository(db=db)
        result = repo.get_aso_by_exam(aso.exame_id)
        assert result is aso

    def test_get_aso_by_numero(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        aso = self._make_aso()
        db.query.return_value.filter.return_value.first.return_value = aso

        repo = PCMSORepository(db=db)
        result = repo.get_aso_by_numero("ASO-2026-000001")
        assert result is aso

    def test_get_expiring_asos(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        asos = [self._make_aso()]
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = asos

        repo = PCMSORepository(db=db)
        result = repo.get_expiring_asos(days=30)
        assert result is asos

    def test_count_asos_by_year(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        # count_asos_by_year usa .filter().filter().count() (duas chamadas filter)
        db.query.return_value.filter.return_value.count.return_value = 12
        db.query.return_value.filter.return_value.filter.return_value.count.return_value = 12

        repo = PCMSORepository(db=db)
        result = repo.count_asos_by_year(2026)
        assert result == 12

    def test_get_exam_statistics(self):
        from modules.health_occupational.repositories.pcmso_repository import PCMSORepository

        db = self._make_db()
        db.query.return_value.filter.return_value.count.return_value = 0
        db.query.return_value.filter.return_value.filter.return_value.count.return_value = 0

        repo = PCMSORepository(db=db)
        result = repo.get_exam_statistics(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )
        assert "total" in result
        assert "by_type" in result
        assert "by_status" in result
        assert "period" in result


# ==============================================================================
# Testes do Service
# ==============================================================================


class TestPCMSOService:
    """Testes do PCMSOService com DB mockado."""

    def _make_db(self):
        db = MagicMock()
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        return db

    def _make_exam_mock(self, status="agendado"):
        exam = MagicMock()
        exam.id = uuid4()
        exam.funcionario_id = uuid4()
        exam.tipo_exame = "admissional"
        exam.status = status
        exam.funcao = "Vigilante"
        exam.setor = "Operacional"
        exam.data_agendamento = date.today() + timedelta(days=1)
        exam.data_realizacao = None
        exam.observacoes = None
        return exam

    def _make_aso_mock(self):
        aso = MagicMock()
        aso.id = uuid4()
        aso.exame_id = uuid4()
        aso.resultado = "apto"
        aso.restricoes = []
        aso.numero_aso = "ASO-2026-000001"
        aso.data_emissao = datetime.utcnow()
        aso.data_vencimento = date.today() + timedelta(days=365)
        aso.assinatura_funcionario = False
        aso.data_assinatura_funcionario = None
        aso.ativo = True
        aso.cancelado = False
        return aso

    def test_service_import(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        assert PCMSOService is not None

    def test_service_instantiation(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        service = PCMSOService(db=db)
        assert service.db is db

    def test_schedule_exam(self):
        from modules.health_occupational.schemas.pcmso import MedicalExamRequest
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        service = PCMSOService(db=db)

        request = MedicalExamRequest(
            funcionario_id=uuid4(),
            tipo_exame="admissional",
            data_agendamento=date.today() + timedelta(days=1),
            funcao="Vigilante",
            setor="Operacional",
        )

        # Simula o refresh definindo o id no objeto
        def set_id(obj):
            if not hasattr(obj, "_id_set"):
                obj.id = uuid4()
                obj._id_set = True
            return None

        db.refresh.side_effect = set_id

        result = service.schedule_exam(request)

        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    def test_get_exam_found(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        exam = self._make_exam_mock()
        db.query.return_value.filter.return_value.first.return_value = exam

        service = PCMSOService(db=db)
        result = service.get_exam(exam.id)
        assert result is exam

    def test_get_exam_not_found(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        service = PCMSOService(db=db)
        result = service.get_exam(uuid4())
        assert result is None

    def test_update_exam_found(self):
        from modules.health_occupational.schemas.pcmso import MedicalExamUpdateRequest
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        exam = self._make_exam_mock()
        db.query.return_value.filter.return_value.first.return_value = exam

        service = PCMSOService(db=db)
        request = MedicalExamUpdateRequest(status="confirmado")
        result = service.update_exam(exam.id, request)

        db.commit.assert_called_once()
        db.refresh.assert_called_once()
        assert result is exam

    def test_update_exam_not_found(self):
        from modules.health_occupational.schemas.pcmso import MedicalExamUpdateRequest
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        service = PCMSOService(db=db)
        request = MedicalExamUpdateRequest(status="confirmado")
        result = service.update_exam(uuid4(), request)
        assert result is None

    def test_list_employee_exams(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        exams = [self._make_exam_mock(), self._make_exam_mock()]
        query_mock = db.query.return_value.filter.return_value
        query_mock.count.return_value = 2
        query_mock.order_by.return_value.offset.return_value.limit.return_value.all.return_value = exams

        service = PCMSOService(db=db)
        result = service.list_employee_exams(funcionario_id=uuid4(), page=1, size=20)

        assert result["total"] == 2
        assert result["page"] == 1
        assert result["size"] == 20
        assert len(result["items"]) == 2

    def test_list_employee_exams_com_filtros(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        query_base = db.query.return_value.filter.return_value
        query_status = query_base.filter.return_value
        query_tipo = query_status.filter.return_value
        query_tipo.count.return_value = 0
        query_tipo.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        service = PCMSOService(db=db)
        result = service.list_employee_exams(
            funcionario_id=uuid4(),
            status_filter="agendado",
            tipo_filter="periodico",
        )
        assert result["total"] == 0

    def test_confirm_exam(self):
        from modules.health_occupational.models.pcmso import ExamStatus
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        exam = self._make_exam_mock("agendado")
        db.query.return_value.filter.return_value.first.return_value = exam

        service = PCMSOService(db=db)
        result = service.confirm_exam(exam.id)

        assert exam.status == ExamStatus.CONFIRMADO.value
        db.commit.assert_called_once()
        assert result is exam

    def test_confirm_exam_not_found(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        service = PCMSOService(db=db)
        result = service.confirm_exam(uuid4())
        assert result is None

    def test_complete_exam(self):
        from modules.health_occupational.models.pcmso import ExamStatus
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        exam = self._make_exam_mock("confirmado")
        db.query.return_value.filter.return_value.first.return_value = exam

        service = PCMSOService(db=db)
        result = service.complete_exam(exam.id)

        assert exam.status == ExamStatus.REALIZADO.value
        assert exam.data_realizacao is not None
        db.commit.assert_called_once()
        assert result is exam

    def test_complete_exam_not_found(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        service = PCMSOService(db=db)
        result = service.complete_exam(uuid4())
        assert result is None

    def test_cancel_exam(self):
        from modules.health_occupational.models.pcmso import ExamStatus
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        exam = self._make_exam_mock("agendado")
        db.query.return_value.filter.return_value.first.return_value = exam

        service = PCMSOService(db=db)
        result = service.cancel_exam(exam.id, motivo="Paciente desistiu")

        assert exam.status == ExamStatus.CANCELADO.value
        db.commit.assert_called_once()
        assert result is exam

    def test_cancel_exam_not_found(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        service = PCMSOService(db=db)
        result = service.cancel_exam(uuid4())
        assert result is None

    def test_list_pending_exams(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        exams = [self._make_exam_mock("agendado")]
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = exams

        service = PCMSOService(db=db)
        result = service.list_pending_exams(days_ahead=30)
        assert result is exams

    def test_emit_aso_exame_nao_encontrado(self):
        from modules.health_occupational.schemas.pcmso import ASORequest
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        service = PCMSOService(db=db)
        request = ASORequest(
            exame_id=uuid4(),
            resultado="apto",
            medico_responsavel="Dr. Silva",
            crm="12345",
        )

        with pytest.raises(ValueError, match="nao encontrado"):
            service.emit_aso(request)

    def test_emit_aso_exame_nao_realizado(self):
        from modules.health_occupational.schemas.pcmso import ASORequest
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        exam = self._make_exam_mock("agendado")
        db.query.return_value.filter.return_value.first.return_value = exam

        service = PCMSOService(db=db)
        request = ASORequest(
            exame_id=exam.id,
            resultado="apto",
            medico_responsavel="Dr. Silva",
            crm="12345",
        )

        with pytest.raises(ValueError, match="Exame deve estar realizado"):
            service.emit_aso(request)

    def test_emit_aso_sucesso(self):
        from modules.health_occupational.schemas.pcmso import ASORequest
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        exam = self._make_exam_mock("realizado")

        call_count = [0]

        def first_side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                return exam  # get_exam
            return None  # check ASO existente

        db.query.return_value.filter.return_value.first.side_effect = first_side_effect
        db.query.return_value.filter.return_value.count.return_value = 0  # _generate_aso_number

        def set_aso_id(obj):
            obj.id = uuid4()
            obj.numero_aso = "ASO-2026-000001"
            obj.data_emissao = datetime.utcnow()
            obj.data_vencimento = date.today() + timedelta(days=365)

        db.refresh.side_effect = set_aso_id

        service = PCMSOService(db=db)
        request = ASORequest(
            exame_id=exam.id,
            resultado="apto",
            medico_responsavel="Dr. Silva",
            crm="12345",
        )

        result = service.emit_aso(request)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_emit_aso_ja_existente(self):
        from modules.health_occupational.schemas.pcmso import ASORequest
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        exam = self._make_exam_mock("realizado")
        aso_existente = self._make_aso_mock()

        call_count = [0]

        def first_side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                return exam
            return aso_existente

        db.query.return_value.filter.return_value.first.side_effect = first_side_effect

        service = PCMSOService(db=db)
        request = ASORequest(
            exame_id=exam.id,
            resultado="apto",
            medico_responsavel="Dr. Silva",
            crm="12345",
        )

        with pytest.raises(ValueError, match="ASO ja emitido"):
            service.emit_aso(request)

    def test_get_aso_found(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        aso = self._make_aso_mock()
        db.query.return_value.filter.return_value.first.return_value = aso

        service = PCMSOService(db=db)
        result = service.get_aso(aso.id)
        assert result is aso

    def test_get_aso_not_found(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        service = PCMSOService(db=db)
        result = service.get_aso(uuid4())
        assert result is None

    def test_get_aso_by_exam(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        aso = self._make_aso_mock()
        db.query.return_value.filter.return_value.first.return_value = aso

        service = PCMSOService(db=db)
        result = service.get_aso_by_exam(uuid4())
        assert result is aso

    def test_update_aso_found(self):
        from modules.health_occupational.schemas.pcmso import ASOUpdateRequest
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        aso = self._make_aso_mock()
        db.query.return_value.filter.return_value.first.return_value = aso

        service = PCMSOService(db=db)
        request = ASOUpdateRequest(assinatura_funcionario=True)
        result = service.update_aso(aso.id, request)

        db.commit.assert_called_once()
        assert result is aso

    def test_update_aso_not_found(self):
        from modules.health_occupational.schemas.pcmso import ASOUpdateRequest
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        service = PCMSOService(db=db)
        request = ASOUpdateRequest(assinatura_funcionario=True)
        result = service.update_aso(uuid4(), request)
        assert result is None

    def test_cancel_aso(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        aso = self._make_aso_mock()
        db.query.return_value.filter.return_value.first.return_value = aso

        service = PCMSOService(db=db)
        result = service.cancel_aso(aso.id, motivo="Exame invalidado")

        assert aso.cancelado is True
        assert aso.ativo is False
        assert aso.motivo_cancelamento == "Exame invalidado"
        db.commit.assert_called_once()
        assert result is aso

    def test_cancel_aso_not_found(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        service = PCMSOService(db=db)
        result = service.cancel_aso(uuid4(), motivo="Motivo")
        assert result is None

    def test_add_complementary_exam(self):
        from modules.health_occupational.schemas.pcmso import ComplementaryExamRequest
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()

        def set_comp_id(obj):
            obj.id = uuid4()

        db.refresh.side_effect = set_comp_id

        service = PCMSOService(db=db)
        request = ComplementaryExamRequest(
            exame_principal_id=uuid4(),
            nome="Hemograma Completo",
        )
        result = service.add_complementary_exam(request)

        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_list_complementary_exams(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        comp_exams = [MagicMock(), MagicMock()]
        db.query.return_value.filter.return_value.all.return_value = comp_exams

        service = PCMSOService(db=db)
        result = service.list_complementary_exams(uuid4())
        assert result is comp_exams

    def test_list_expiring_asos_sem_db(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        service = PCMSOService(db=None)
        result = service.list_expiring_asos(days=30)
        assert result == []

    def test_list_expiring_asos_com_db_erro(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        db.execute.side_effect = Exception("DB error")

        service = PCMSOService(db=db)
        result = service.list_expiring_asos(days=30)
        assert result == []

    def test_get_statistics_sem_db(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        service = PCMSOService(db=None)
        result = service.get_statistics()

        assert result["total_exames_ano"] == 0
        assert result["exames_pendentes"] == 0
        assert result["exames_realizados"] == 0
        assert result["asos_vencendo_30_dias"] == 0

    def test_get_statistics_com_db_erro(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        db.execute.side_effect = Exception("DB error")

        service = PCMSOService(db=db)
        result = service.get_statistics()

        assert result["total_exames_ano"] == 0

    def test_generate_aso_number(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        db = self._make_db()
        db.query.return_value.filter.return_value.count.return_value = 5

        service = PCMSOService(db=db)
        numero = service._generate_aso_number()

        year = date.today().year
        assert str(year) in numero
        assert "ASO-" in numero
        assert "000006" in numero


# ==============================================================================
# Testes do Controller (imports e dependencias)
# ==============================================================================


class TestPCMSOController:
    """Testes do controller PCMSO — verifica imports e estrutura de rotas."""

    def test_controller_import(self):
        from modules.health_occupational.controllers.pcmso_controller import router

        assert router is not None

    def test_router_prefix(self):
        from modules.health_occupational.controllers.pcmso_controller import router

        assert router.prefix == "/pcmso"

    def test_router_tags(self):
        from modules.health_occupational.controllers.pcmso_controller import router

        assert "PCMSO" in router.tags[0]

    def test_router_has_routes(self):
        from modules.health_occupational.controllers.pcmso_controller import router

        routes = [r.path for r in router.routes]
        assert len(routes) > 0

    def test_router_has_schedule_exam_route(self):
        from modules.health_occupational.controllers.pcmso_controller import router

        paths = [r.path for r in router.routes]
        assert any("agendar" in p for p in paths)

    def test_router_has_emit_aso_route(self):
        from modules.health_occupational.controllers.pcmso_controller import router

        paths = [r.path for r in router.routes]
        assert any("emitir" in p for p in paths)

    def test_router_has_vencimentos_route(self):
        from modules.health_occupational.controllers.pcmso_controller import router

        paths = [r.path for r in router.routes]
        assert any("vencimentos" in p for p in paths)

    def test_router_has_estatisticas_route(self):
        from modules.health_occupational.controllers.pcmso_controller import router

        paths = [r.path for r in router.routes]
        assert any("estatisticas" in p for p in paths)

    def test_get_pcmso_service_dependency(self):
        from modules.health_occupational.controllers.pcmso_controller import get_pcmso_service

        assert callable(get_pcmso_service)

    def test_schedule_exam_endpoint_direct(self):
        """Testa o endpoint schedule_medical_exam diretamente via mock do service."""
        import asyncio

        from modules.health_occupational.controllers.pcmso_controller import schedule_medical_exam
        from modules.health_occupational.schemas.pcmso import MedicalExamRequest

        exam_mock = MagicMock()
        exam_mock.id = uuid4()
        exam_mock.status = "agendado"

        service_mock = MagicMock()
        service_mock.schedule_exam.return_value = exam_mock

        request = MedicalExamRequest(
            funcionario_id=uuid4(),
            tipo_exame="admissional",
            data_agendamento=date.today() + timedelta(days=1),
            funcao="Vigilante",
            setor="Operacional",
        )

        response = asyncio.get_event_loop().run_until_complete(
            schedule_medical_exam(request=request, service=service_mock)
        )

        assert response.success is True
        assert "agendado" in response.message.lower()
        service_mock.schedule_exam.assert_called_once_with(request)

    def test_schedule_exam_endpoint_value_error(self):
        """Testa tratamento de ValueError no agendamento."""
        import asyncio

        from fastapi import HTTPException

        from modules.health_occupational.controllers.pcmso_controller import schedule_medical_exam
        from modules.health_occupational.schemas.pcmso import MedicalExamRequest

        service_mock = MagicMock()
        service_mock.schedule_exam.side_effect = ValueError("Data invalida")

        request = MedicalExamRequest(
            funcionario_id=uuid4(),
            tipo_exame="admissional",
            data_agendamento=date.today() + timedelta(days=1),
            funcao="Vigilante",
            setor="Operacional",
        )

        with pytest.raises(HTTPException) as exc_info:
            asyncio.get_event_loop().run_until_complete(schedule_medical_exam(request=request, service=service_mock))

        assert exc_info.value.status_code == 400

    def test_get_exam_endpoint_not_found(self):
        """Testa 404 quando exame nao encontrado."""
        import asyncio

        from fastapi import HTTPException

        from modules.health_occupational.controllers.pcmso_controller import get_exam

        service_mock = MagicMock()
        service_mock.get_exam.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.get_event_loop().run_until_complete(get_exam(exame_id=uuid4(), service=service_mock))

        assert exc_info.value.status_code == 404

    def test_emit_aso_endpoint_direct(self):
        """Testa emissao de ASO via endpoint direto."""
        import asyncio

        from modules.health_occupational.controllers.pcmso_controller import emit_aso
        from modules.health_occupational.schemas.pcmso import ASORequest

        aso_mock = MagicMock()
        aso_mock.id = uuid4()
        aso_mock.numero_aso = "ASO-2026-000001"
        aso_mock.data_vencimento = date.today() + timedelta(days=365)
        aso_mock.data_emissao = datetime.utcnow()

        service_mock = MagicMock()
        service_mock.emit_aso.return_value = aso_mock

        request = ASORequest(
            exame_id=uuid4(),
            resultado="apto",
            medico_responsavel="Dr. Silva",
            crm="12345",
        )

        response = asyncio.get_event_loop().run_until_complete(emit_aso(request=request, service=service_mock))

        assert response.success is True
        assert "ASO" in response.message

    def test_emit_aso_endpoint_value_error(self):
        """Testa 400 em ValueError na emissao de ASO."""
        import asyncio

        from fastapi import HTTPException

        from modules.health_occupational.controllers.pcmso_controller import emit_aso
        from modules.health_occupational.schemas.pcmso import ASORequest

        service_mock = MagicMock()
        service_mock.emit_aso.side_effect = ValueError("ASO ja emitido")

        request = ASORequest(
            exame_id=uuid4(),
            resultado="apto",
            medico_responsavel="Dr. Silva",
            crm="12345",
        )

        with pytest.raises(HTTPException) as exc_info:
            asyncio.get_event_loop().run_until_complete(emit_aso(request=request, service=service_mock))

        assert exc_info.value.status_code == 400

    def test_get_aso_endpoint_not_found(self):
        """Testa 404 quando ASO nao encontrado."""
        import asyncio

        from fastapi import HTTPException

        from modules.health_occupational.controllers.pcmso_controller import get_aso

        service_mock = MagicMock()
        service_mock.get_aso.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.get_event_loop().run_until_complete(get_aso(aso_id=uuid4(), service=service_mock))

        assert exc_info.value.status_code == 404

    def test_confirm_exam_endpoint_not_found(self):
        """Testa 404 ao confirmar exame inexistente."""
        import asyncio

        from fastapi import HTTPException

        from modules.health_occupational.controllers.pcmso_controller import confirm_exam

        service_mock = MagicMock()
        service_mock.confirm_exam.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.get_event_loop().run_until_complete(confirm_exam(exame_id=uuid4(), service=service_mock))

        assert exc_info.value.status_code == 404

    def test_complete_exam_endpoint_not_found(self):
        """Testa 404 ao completar exame inexistente."""
        import asyncio

        from fastapi import HTTPException

        from modules.health_occupational.controllers.pcmso_controller import complete_exam

        service_mock = MagicMock()
        service_mock.complete_exam.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.get_event_loop().run_until_complete(complete_exam(exame_id=uuid4(), service=service_mock))

        assert exc_info.value.status_code == 404

    def test_list_expiring_asos_endpoint(self):
        """Testa listagem de ASOs a vencer."""
        import asyncio

        from modules.health_occupational.controllers.pcmso_controller import list_expiring_asos

        service_mock = MagicMock()
        service_mock.list_expiring_asos.return_value = []

        response = asyncio.get_event_loop().run_until_complete(list_expiring_asos(dias=30, service=service_mock))

        assert response.success is True
        assert "0" in response.message

    def test_get_statistics_endpoint(self):
        """Testa endpoint de estatisticas."""
        import asyncio

        from modules.health_occupational.controllers.pcmso_controller import get_statistics

        service_mock = MagicMock()
        service_mock.get_statistics.return_value = {
            "total_exames_ano": 10,
            "exames_pendentes": 3,
            "exames_realizados": 7,
            "asos_vencendo_30_dias": 2,
        }

        response = asyncio.get_event_loop().run_until_complete(get_statistics(service=service_mock))

        assert response.success is True

    def test_sign_aso_endpoint_not_found(self):
        """Testa 404 ao assinar ASO inexistente."""
        import asyncio

        from fastapi import HTTPException

        from modules.health_occupational.controllers.pcmso_controller import sign_aso

        service_mock = MagicMock()
        service_mock.update_aso.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.get_event_loop().run_until_complete(sign_aso(aso_id=uuid4(), service=service_mock))

        assert exc_info.value.status_code == 404

    def test_update_exam_endpoint_not_found(self):
        """Testa 404 ao atualizar exame inexistente."""
        import asyncio

        from fastapi import HTTPException

        from modules.health_occupational.controllers.pcmso_controller import update_exam
        from modules.health_occupational.schemas.pcmso import MedicalExamUpdateRequest

        service_mock = MagicMock()
        service_mock.update_exam.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            asyncio.get_event_loop().run_until_complete(
                update_exam(
                    exame_id=uuid4(),
                    request=MedicalExamUpdateRequest(status="confirmado"),
                    service=service_mock,
                )
            )

        assert exc_info.value.status_code == 404


# ==============================================================================
# Testes das Schemas Auxiliares (Common)
# ==============================================================================


class TestCommonSchemas:
    """Testes das schemas comuns do modulo de saude ocupacional."""

    def test_standard_response_fields(self):
        from modules.health_occupational.schemas.common import StandardResponse

        resp = StandardResponse(success=True, message="Operacao realizada")
        assert resp.success is True
        assert resp.message == "Operacao realizada"
        assert resp.data is None
        assert resp.timestamp is not None

    def test_standard_response_com_data(self):
        from modules.health_occupational.schemas.common import StandardResponse

        resp = StandardResponse(
            success=True,
            message="Dados retornados",
            data={"id": "123", "nome": "Teste"},
        )
        assert resp.data["id"] == "123"

    def test_pagination_params(self):
        from modules.health_occupational.schemas.common import PaginationParams

        params = PaginationParams(page=2, size=50)
        assert params.page == 2
        assert params.size == 50

    def test_pagination_params_defaults(self):
        from modules.health_occupational.schemas.common import PaginationParams

        params = PaginationParams()
        assert params.page == 1
        assert params.size == 20

    def test_paginated_response(self):
        from modules.health_occupational.schemas.common import PaginatedResponse

        resp = PaginatedResponse(items=[], total=0, page=1, size=20, pages=0)
        assert resp.has_next is False
        assert resp.has_prev is False

    def test_paginated_response_has_next(self):
        from modules.health_occupational.schemas.common import PaginatedResponse

        resp = PaginatedResponse(items=[], total=60, page=1, size=20, pages=3)
        assert resp.has_next is True
        assert resp.has_prev is False

    def test_paginated_response_has_prev(self):
        from modules.health_occupational.schemas.common import PaginatedResponse

        resp = PaginatedResponse(items=[], total=60, page=2, size=20, pages=3)
        assert resp.has_prev is True
        assert resp.has_next is True

    def test_error_response(self):
        from modules.health_occupational.schemas.common import ErrorResponse

        err = ErrorResponse(message="Recurso nao encontrado", error_code="NOT_FOUND")
        assert err.success is False
        assert err.message == "Recurso nao encontrado"
        assert err.error_code == "NOT_FOUND"
