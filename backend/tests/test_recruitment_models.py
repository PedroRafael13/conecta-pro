"""Testes para models do modulo Recruitment."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal

import pytest

from modules.recruitment.models.application import (
    Application,
    ApplicationStatus,
    RejectionReason,
)
from modules.recruitment.models.candidate import (
    Candidate,
    CandidateSource,
    CandidateStatus,
    Gender,
)
from modules.recruitment.models.candidate_education import (
    CandidateEducation,
    EducationLevel,
    EducationStatus,
)
from modules.recruitment.models.candidate_experience import (
    CandidateExperience,
    EmploymentType,
)
from modules.recruitment.models.candidate_skill import (
    CandidateSkill,
    SkillCategory,
    SkillLevel,
)
from modules.recruitment.models.interview import (
    Interview,
    InterviewResult,
    InterviewStatus,
    InterviewType,
)
from modules.recruitment.models.job_position import (
    Department,
    JobPosition,
    PositionLevel,
    PositionStatus,
    PositionType,
    WorkModel,
)


class TestJobPosition:
    """Testes para JobPosition model."""

    def test_create_job_position(self):
        """Testa criacao de vaga."""
        position = JobPosition(
            title="Desenvolvedor Python",
            description="Vaga para desenvolvedor Python Senior",
            department=Department.TI,
            position_type=PositionType.CLT,
            position_level=PositionLevel.SENIOR,
            work_model=WorkModel.HIBRIDO,
            status=PositionStatus.RASCUNHO,
            salary_min=Decimal("10000"),
            salary_max=Decimal("15000"),
            vacancies=2,
            filled_count=0,
            city="Sao Paulo",
            state="SP",
        )

        assert position.title == "Desenvolvedor Python"
        assert position.department == Department.TI
        assert position.status == PositionStatus.RASCUNHO
        assert position.vacancies == 2
        assert position.filled_count == 0

    def test_is_open_property(self):
        """Testa propriedade is_open."""
        position = JobPosition(
            title="Teste",
            department=Department.TI,
            position_type=PositionType.CLT,
            status=PositionStatus.ABERTA,
        )
        assert position.is_open is True

        position.status = PositionStatus.RASCUNHO
        assert position.is_open is False

    def test_is_expired_property(self):
        """Testa propriedade is_expired."""
        position = JobPosition(
            title="Teste",
            department=Department.TI,
            position_type=PositionType.CLT,
        )
        # Sem deadline, nao expira
        assert position.is_expired is False

        # Deadline no passado
        position.deadline = date.today() - timedelta(days=1)
        assert position.is_expired is True

        # Deadline no futuro
        position.deadline = date.today() + timedelta(days=7)
        assert position.is_expired is False

    def test_remaining_vacancies_property(self):
        """Testa propriedade remaining_vacancies."""
        position = JobPosition(
            title="Teste",
            department=Department.TI,
            position_type=PositionType.CLT,
            vacancies=3,
            filled_count=1,
        )
        assert position.remaining_vacancies == 2

        position.filled_count = 3
        assert position.remaining_vacancies == 0

        # Nao deve ser negativo
        position.filled_count = 5
        assert position.remaining_vacancies == 0

    def test_salary_range_property(self):
        """Testa propriedade salary_range."""
        # Min e max
        position = JobPosition(
            title="Teste",
            salary_min=Decimal("5000"),
            salary_max=Decimal("10000"),
        )
        assert "5" in position.salary_range
        assert "10" in position.salary_range

        # Somente min
        position.salary_max = None
        assert "A partir de" in position.salary_range

        # Somente max
        position.salary_min = None
        position.salary_max = Decimal("10000")
        assert "Ate" in position.salary_range

        # Sem salario
        position.salary_max = None
        assert position.salary_range == "A combinar"

    def test_remaining_vacancies_none_values(self):
        """Testa remaining_vacancies com valores None."""
        position = JobPosition(
            title="Teste",
            vacancies=None,
            filled_count=None,
        )
        assert position.remaining_vacancies == 0


class TestCandidate:
    """Testes para Candidate model."""

    def test_create_candidate(self):
        """Testa criacao de candidato."""
        candidate = Candidate(
            name="Joao Silva",
            email="joao@example.com",
            phone="11999999999",
            source=CandidateSource.SITE,
            status=CandidateStatus.ATIVO,
            city="Sao Paulo",
            state="SP",
        )

        assert candidate.name == "Joao Silva"
        assert candidate.email == "joao@example.com"
        assert candidate.status == CandidateStatus.ATIVO

    def test_calculate_age(self):
        """Testa calculo de idade."""
        candidate = Candidate(
            name="Teste",
            email="teste@example.com",
            birth_date=date.today().replace(year=date.today().year - 30),
        )

        assert candidate.age == 30

    def test_age_none_without_birth_date(self):
        """Testa que age retorna None sem birth_date."""
        candidate = Candidate(
            name="Teste",
            email="teste@example.com",
        )
        assert candidate.age is None

    def test_candidate_repr(self):
        """Testa representacao do candidato."""
        candidate = Candidate(
            name="Joao Silva",
            email="joao@example.com",
        )
        assert "Joao Silva" in repr(candidate)
        assert "joao@example.com" in repr(candidate)


class TestApplication:
    """Testes para Application model."""

    def test_create_application(self):
        """Testa criacao de candidatura."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
            status=ApplicationStatus.INSCRITO,
            current_stage=1,
            applied_at=datetime.utcnow(),
        )

        assert application.status == ApplicationStatus.INSCRITO
        assert application.current_stage == 1
        assert application.applied_at is not None

    def test_advance_stage(self):
        """Testa avanco de etapa."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
            status=ApplicationStatus.INSCRITO,
            current_stage=1,
            status_history=[],
        )

        application.advance_stage(ApplicationStatus.TRIAGEM, "Aprovado na triagem")

        assert application.status == ApplicationStatus.TRIAGEM
        assert application.current_stage == 2
        assert len(application.status_history) == 1

    def test_reject(self):
        """Testa rejeicao."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
            status=ApplicationStatus.INSCRITO,
            current_stage=1,
            status_history=[],
        )

        application.reject(RejectionReason.PERFIL_INADEQUADO, "Falta experiencia", "recruiter-789")

        assert application.status == ApplicationStatus.REPROVADO
        assert application.rejection_reason == RejectionReason.PERFIL_INADEQUADO
        assert application.rejected_at is not None

    def test_hire(self):
        """Testa contratacao."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
            status=ApplicationStatus.INSCRITO,
            current_stage=1,
            status_history=[],
        )

        start_date = datetime.now() + timedelta(days=30)
        application.hire(start_date)

        assert application.status == ApplicationStatus.CONTRATADO
        assert application.hired_at is not None
        assert application.start_date == start_date

    def test_calculate_final_score(self):
        """Testa calculo de score final."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
            matching_score=80,
            interview_score=85,
            test_score=90,
        )

        application.update_score(matching=80, interview=85, test=90)
        assert application.final_score is not None
        assert 0 <= application.final_score <= 100

    def test_is_active_property(self):
        """Testa propriedade is_active."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
            status=ApplicationStatus.INSCRITO,
        )
        assert application.is_active is True

        application.status = ApplicationStatus.REPROVADO
        assert application.is_active is False

    def test_is_hired_property(self):
        """Testa propriedade is_hired."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
            status=ApplicationStatus.CONTRATADO,
        )
        assert application.is_hired is True

    def test_withdraw(self):
        """Testa desistencia."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
            status=ApplicationStatus.INSCRITO,
            current_stage=1,
            status_history=[],
        )

        application.withdraw("Melhor oferta")
        assert application.status == ApplicationStatus.DESISTIU

    def test_move_to_talent_pool(self):
        """Testa mover para banco de talentos."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
            status=ApplicationStatus.INSCRITO,
            current_stage=1,
            status_history=[],
        )

        application.move_to_talent_pool()
        assert application.status == ApplicationStatus.BANCO_TALENTOS


class TestInterview:
    """Testes para Interview model."""

    def test_create_interview(self):
        """Testa criacao de entrevista."""
        interview = Interview(
            application_id="app-123",
            interview_type=InterviewType.COMPORTAMENTAL,
            status=InterviewStatus.AGENDADA,
            scheduled_date=date.today() + timedelta(days=7),
            scheduled_time=time(14, 0),
            duration_minutes=60,
            interviewer_ids=["int-001", "int-002"],
            candidate_confirmed=False,
            interviewer_confirmed=False,
            reschedule_count=0,
        )

        assert interview.interview_type == InterviewType.COMPORTAMENTAL
        assert interview.status == InterviewStatus.AGENDADA
        assert interview.duration_minutes == 60

    def test_confirm_candidate(self):
        """Testa confirmacao do candidato."""
        interview = Interview(
            application_id="app-123",
            interview_type=InterviewType.COMPORTAMENTAL,
            status=InterviewStatus.AGENDADA,
            scheduled_date=date.today() + timedelta(days=7),
            scheduled_time=time(14, 0),
            candidate_confirmed=False,
            interviewer_confirmed=False,
            reschedule_count=0,
        )

        interview.confirm_candidate()
        assert interview.candidate_confirmed is True
        assert interview.status == InterviewStatus.AGENDADA

        interview.confirm_interviewer()
        assert interview.interviewer_confirmed is True
        assert interview.status == InterviewStatus.CONFIRMADA

    def test_complete_interview(self):
        """Testa conclusao de entrevista."""
        interview = Interview(
            application_id="app-123",
            interview_type=InterviewType.TECNICA,
            status=InterviewStatus.AGENDADA,
            scheduled_date=date.today(),
            scheduled_time=time(14, 0),
            candidate_confirmed=False,
            interviewer_confirmed=False,
            reschedule_count=0,
        )
        interview.status = InterviewStatus.EM_ANDAMENTO

        interview.complete(InterviewResult.APROVADO, 85, "Excelente candidato")

        assert interview.status == InterviewStatus.REALIZADA
        assert interview.result == InterviewResult.APROVADO
        assert interview.score == 85

    def test_cancel_interview(self):
        """Testa cancelamento de entrevista."""
        interview = Interview(
            application_id="app-123",
            interview_type=InterviewType.COMPORTAMENTAL,
            status=InterviewStatus.AGENDADA,
            scheduled_date=date.today() + timedelta(days=7),
            scheduled_time=time(14, 0),
            candidate_confirmed=False,
            interviewer_confirmed=False,
            reschedule_count=0,
        )

        interview.cancel("Candidato desistiu", "recruiter-001")

        assert interview.status == InterviewStatus.CANCELADA
        assert interview.cancellation_reason == "Candidato desistiu"

    def test_reschedule(self):
        """Testa reagendamento."""
        interview = Interview(
            application_id="app-123",
            interview_type=InterviewType.COMPORTAMENTAL,
            status=InterviewStatus.AGENDADA,
            scheduled_date=date.today() + timedelta(days=7),
            scheduled_time=time(14, 0),
            candidate_confirmed=False,
            interviewer_confirmed=False,
            reschedule_count=0,
        )

        new_date = date.today() + timedelta(days=14)
        new_time = time(10, 0)
        interview.reschedule(new_date, new_time)

        assert interview.status == InterviewStatus.REAGENDADA
        assert interview.scheduled_date == new_date
        assert interview.scheduled_time == new_time

    def test_mark_no_show(self):
        """Testa marcar como nao compareceu."""
        interview = Interview(
            application_id="app-123",
            interview_type=InterviewType.COMPORTAMENTAL,
            status=InterviewStatus.AGENDADA,
            scheduled_date=date.today(),
            scheduled_time=time(14, 0),
            candidate_confirmed=False,
            interviewer_confirmed=False,
            reschedule_count=0,
        )

        interview.mark_no_show()
        assert interview.status == InterviewStatus.NO_SHOW
        assert interview.result == InterviewResult.INCONCLUSIVO


class TestCandidateSkill:
    """Testes para CandidateSkill model."""

    def test_create_skill(self):
        """Testa criacao de habilidade."""
        skill = CandidateSkill(
            candidate_id="cand-123",
            name="Python",
            category=SkillCategory.TECNICA,
            level=SkillLevel.AVANCADO,
            years_experience=5,
        )

        assert skill.name == "Python"
        assert skill.level == SkillLevel.AVANCADO
        assert skill.years_experience == 5

    def test_add_certification(self):
        """Testa adicao de certificacao."""
        skill = CandidateSkill(
            candidate_id="cand-123",
            name="AWS",
            category=SkillCategory.FERRAMENTA,
        )

        skill.add_certification(
            name="AWS Solutions Architect",
            issuer="Amazon",
            cert_date=datetime.now(),
            expiry=datetime.now() + timedelta(days=365 * 3),
            url="https://aws.amazon.com/verify/AWS-123456",
        )

        assert skill.is_certified is True
        assert skill.certification_name == "AWS Solutions Architect"

    def test_level_score(self):
        """Testa score do nivel."""
        skill = CandidateSkill(
            candidate_id="cand-123",
            name="Python",
            level=SkillLevel.AVANCADO,
        )
        assert skill.level_score == 3

        skill.level = SkillLevel.EXPERT
        assert skill.level_score == 4

    def test_total_experience_months(self):
        """Testa experiencia total em meses."""
        skill = CandidateSkill(
            candidate_id="cand-123",
            name="Python",
            years_experience=2,
            months_experience=6,
        )
        assert skill.total_experience_months == 30


class TestCandidateExperience:
    """Testes para CandidateExperience model."""

    def test_create_experience(self):
        """Testa criacao de experiencia."""
        experience = CandidateExperience(
            candidate_id="cand-123",
            company_name="Tech Corp",
            job_title="Desenvolvedor Senior",
            employment_type=EmploymentType.CLT,
            start_date=date(2020, 1, 1),
            is_current=True,
            responsibilities=["Desenvolvimento", "Code review"],
        )

        assert experience.company_name == "Tech Corp"
        assert experience.is_current is True
        assert experience.duration_months > 0

    def test_duration_calculation(self):
        """Testa calculo de duracao."""
        experience = CandidateExperience(
            candidate_id="cand-123",
            company_name="Tech Corp",
            job_title="Dev",
            start_date=date(2022, 1, 1),
            end_date=date(2023, 1, 1),
        )

        assert experience.duration_months == 12

    def test_has_reference(self):
        """Testa verificacao de referencia."""
        experience = CandidateExperience(
            candidate_id="cand-123",
            company_name="Tech Corp",
            job_title="Dev",
            start_date=date(2022, 1, 1),
        )
        assert experience.has_reference is False

        experience.reference_name = "Fulano"
        experience.reference_phone = "11999999999"
        assert experience.has_reference is True


class TestCandidateEducation:
    """Testes para CandidateEducation model."""

    def test_create_education(self):
        """Testa criacao de formacao."""
        education = CandidateEducation(
            candidate_id="cand-123",
            institution_name="USP",
            course_name="Ciencia da Computacao",
            level=EducationLevel.GRADUACAO,
            status=EducationStatus.COMPLETO,
            start_date=date(2015, 2, 1),
            end_date=date(2019, 12, 1),
        )

        assert education.institution_name == "USP"
        assert education.level == EducationLevel.GRADUACAO
        assert education.is_completed is True

    def test_education_level_check(self):
        """Testa verificacao de nivel educacional."""
        education = CandidateEducation(
            candidate_id="cand-123",
            institution_name="ETEC",
            course_name="Tecnico em Informatica",
            level=EducationLevel.TECNICO,
        )
        assert education.level == EducationLevel.TECNICO

        education.level = EducationLevel.GRADUACAO
        assert education.level == EducationLevel.GRADUACAO

    def test_is_in_progress(self):
        """Testa verificacao de em andamento."""
        education = CandidateEducation(
            candidate_id="cand-123",
            institution_name="USP",
            course_name="Mestrado",
            level=EducationLevel.MESTRADO,
            status=EducationStatus.CURSANDO,
        )
        assert education.is_in_progress is True
        assert education.is_completed is False

    def test_level_weight(self):
        """Testa peso do nivel."""
        education = CandidateEducation(
            candidate_id="cand-123",
            institution_name="USP",
            course_name="Doutorado",
            level=EducationLevel.DOUTORADO,
        )
        assert education.level_weight == 9


class TestEnums:
    """Testes para Enums."""

    def test_position_status_values(self):
        """Testa valores de PositionStatus."""
        assert PositionStatus.RASCUNHO.value == "rascunho"
        assert PositionStatus.ABERTA.value == "aberta"
        assert PositionStatus.PREENCHIDA.value == "preenchida"

    def test_candidate_source_values(self):
        """Testa valores de CandidateSource."""
        assert CandidateSource.SITE.value == "site"
        assert CandidateSource.LINKEDIN.value == "linkedin"
        assert CandidateSource.INDICACAO.value == "indicacao"

    def test_application_status_values(self):
        """Testa valores de ApplicationStatus."""
        assert ApplicationStatus.INSCRITO.value == "inscrito"
        assert ApplicationStatus.CONTRATADO.value == "contratado"
        assert len(ApplicationStatus) == 14

    def test_interview_type_values(self):
        """Testa valores de InterviewType."""
        assert InterviewType.COMPORTAMENTAL.value == "comportamental"
        assert InterviewType.TECNICA.value == "tecnica"
        assert len(InterviewType) == 8
