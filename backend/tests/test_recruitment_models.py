"""Testes para models do módulo Recruitment."""

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
        """Testa criação de vaga."""
        position = JobPosition(
            title="Desenvolvedor Python",
            description="Vaga para desenvolvedor Python Sênior",
            department=Department.TI,
            position_type=PositionType.CLT,
            position_level=PositionLevel.SENIOR,
            work_model=WorkModel.HIBRIDO,
            salary_min=Decimal("10000"),
            salary_max=Decimal("15000"),
            vacancies=2,
            city="São Paulo",
            state="SP",
        )

        assert position.title == "Desenvolvedor Python"
        assert position.department == Department.TI
        assert position.status == PositionStatus.RASCUNHO
        assert position.vacancies == 2
        assert position.filled_vacancies == 0

    def test_generate_code(self):
        """Testa geração de código."""
        code = JobPosition.generate_code(42)
        year = date.today().year
        assert code == f"VAG-{year}-0042"

    def test_open_position(self):
        """Testa abertura de vaga."""
        position = JobPosition(
            title="Teste",
            department=Department.TI,
            position_type=PositionType.CLT,
            position_level=PositionLevel.JUNIOR,
            work_model=WorkModel.PRESENCIAL,
        )
        position.open()

        assert position.status == PositionStatus.ABERTA
        assert position.published_at is not None

    def test_fill_vacancy(self):
        """Testa preenchimento de vaga."""
        position = JobPosition(
            title="Teste",
            department=Department.TI,
            position_type=PositionType.CLT,
            position_level=PositionLevel.JUNIOR,
            work_model=WorkModel.PRESENCIAL,
            vacancies=2,
        )
        position.status = PositionStatus.ABERTA

        position.fill_vacancy()
        assert position.filled_vacancies == 1
        assert position.status == PositionStatus.ABERTA

        position.fill_vacancy()
        assert position.filled_vacancies == 2
        assert position.status == PositionStatus.PREENCHIDA

    def test_increment_counters(self):
        """Testa incremento de contadores."""
        position = JobPosition(
            title="Teste",
            department=Department.TI,
            position_type=PositionType.CLT,
            position_level=PositionLevel.JUNIOR,
            work_model=WorkModel.PRESENCIAL,
        )

        position.increment_view()
        assert position.views_count == 1

        position.increment_application()
        assert position.applications_count == 1


class TestCandidate:
    """Testes para Candidate model."""

    def test_create_candidate(self):
        """Testa criação de candidato."""
        candidate = Candidate(
            name="João Silva",
            email="joao@example.com",
            phone="11999999999",
            source=CandidateSource.SITE_CARREIRAS,
            city="São Paulo",
            state="SP",
        )

        assert candidate.name == "João Silva"
        assert candidate.email == "joao@example.com"
        assert candidate.status == CandidateStatus.ATIVO
        assert candidate.is_blocked is False

    def test_calculate_age(self):
        """Testa cálculo de idade."""
        candidate = Candidate(
            name="Teste",
            email="teste@example.com",
            birth_date=date.today() - timedelta(days=365 * 30),
        )

        assert candidate.age == 30

    def test_full_address(self):
        """Testa endereço completo."""
        candidate = Candidate(
            name="Teste",
            email="teste@example.com",
            address="Rua Teste, 123",
            city="São Paulo",
            state="SP",
            zip_code="01234-567",
        )

        assert "Rua Teste" in candidate.full_address
        assert "São Paulo" in candidate.full_address

    def test_block_unblock(self):
        """Testa bloqueio e desbloqueio."""
        candidate = Candidate(
            name="Teste",
            email="teste@example.com",
        )

        candidate.block("Motivo teste", "admin")
        assert candidate.is_blocked is True
        assert candidate.blocked_reason == "Motivo teste"
        assert candidate.blocked_by == "admin"
        assert candidate.blocked_at is not None

        candidate.unblock()
        assert candidate.is_blocked is False
        assert candidate.blocked_at is None

    def test_profile_score(self):
        """Testa cálculo de score do perfil."""
        candidate = Candidate(
            name="Teste",
            email="teste@example.com",
            phone="11999999999",
            resume_text="Currículo completo...",
            headline="Desenvolvedor Sênior",
        )
        candidate.update_profile_score()

        assert candidate.profile_score > 0
        assert candidate.profile_score <= 100


class TestApplication:
    """Testes para Application model."""

    def test_create_application(self):
        """Testa criação de candidatura."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
        )

        assert application.status == ApplicationStatus.INSCRITO
        assert application.current_stage == 1
        assert application.applied_at is not None

    def test_advance_stage(self):
        """Testa avanço de etapa."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
        )

        application.advance_stage(ApplicationStatus.TRIAGEM, "Aprovado na triagem")

        assert application.status == ApplicationStatus.TRIAGEM
        assert application.current_stage == 2
        assert len(application.stage_history) == 1

    def test_reject(self):
        """Testa rejeição."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
        )

        application.reject(RejectionReason.PERFIL_NAO_ADEQUADO, "Falta experiência", "recruiter-789")

        assert application.status == ApplicationStatus.REPROVADO
        assert application.rejection_reason == RejectionReason.PERFIL_NAO_ADEQUADO
        assert application.rejected_at is not None

    def test_hire(self):
        """Testa contratação."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
        )

        start_date = datetime.now() + timedelta(days=30)
        application.hire(start_date)

        assert application.status == ApplicationStatus.CONTRATADO
        assert application.hired_at is not None
        assert application.expected_start_date == start_date

    def test_calculate_final_score(self):
        """Testa cálculo de score final."""
        application = Application(
            candidate_id="cand-123",
            job_position_id="pos-456",
            matching_score=80,
            interview_score=85,
            test_score=90,
        )

        application.calculate_final_score()
        assert application.final_score is not None
        assert 0 <= application.final_score <= 100


class TestInterview:
    """Testes para Interview model."""

    def test_create_interview(self):
        """Testa criação de entrevista."""
        interview = Interview(
            application_id="app-123",
            interview_type=InterviewType.ENTREVISTA_RH,
            scheduled_date=date.today() + timedelta(days=7),
            scheduled_time=time(14, 0),
            duration_minutes=60,
            interviewer_ids=["int-001", "int-002"],
        )

        assert interview.interview_type == InterviewType.ENTREVISTA_RH
        assert interview.status == InterviewStatus.AGENDADA
        assert interview.duration_minutes == 60

    def test_confirm_candidate(self):
        """Testa confirmação do candidato."""
        interview = Interview(
            application_id="app-123",
            interview_type=InterviewType.ENTREVISTA_RH,
            scheduled_date=date.today() + timedelta(days=7),
            scheduled_time=time(14, 0),
        )

        interview.confirm_candidate()
        assert interview.candidate_confirmed is True
        assert interview.status == InterviewStatus.AGENDADA

        interview.confirm_interviewer()
        assert interview.interviewer_confirmed is True
        assert interview.status == InterviewStatus.CONFIRMADA

    def test_complete_interview(self):
        """Testa conclusão de entrevista."""
        interview = Interview(
            application_id="app-123",
            interview_type=InterviewType.ENTREVISTA_TECNICA,
            scheduled_date=date.today(),
            scheduled_time=time(14, 0),
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
            interview_type=InterviewType.ENTREVISTA_RH,
            scheduled_date=date.today() + timedelta(days=7),
            scheduled_time=time(14, 0),
        )

        interview.cancel("Candidato desistiu", "recruiter-001")

        assert interview.status == InterviewStatus.CANCELADA
        assert interview.cancellation_reason == "Candidato desistiu"

    def test_reschedule(self):
        """Testa reagendamento."""
        interview = Interview(
            application_id="app-123",
            interview_type=InterviewType.ENTREVISTA_RH,
            scheduled_date=date.today() + timedelta(days=7),
            scheduled_time=time(14, 0),
        )

        new_date = date.today() + timedelta(days=14)
        new_time = time(10, 0)
        interview.reschedule(new_date, new_time)

        assert interview.status == InterviewStatus.REAGENDADA
        assert interview.scheduled_date == new_date
        assert interview.scheduled_time == new_time


class TestCandidateSkill:
    """Testes para CandidateSkill model."""

    def test_create_skill(self):
        """Testa criação de habilidade."""
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
        """Testa adição de certificação."""
        skill = CandidateSkill(
            candidate_id="cand-123",
            name="AWS",
            category=SkillCategory.FERRAMENTA,
        )

        skill.add_certification(
            name="AWS Solutions Architect",
            issuer="Amazon",
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365 * 3),
            credential_id="AWS-123456",
        )

        assert len(skill.certifications) == 1
        assert skill.certifications[0]["name"] == "AWS Solutions Architect"


class TestCandidateExperience:
    """Testes para CandidateExperience model."""

    def test_create_experience(self):
        """Testa criação de experiência."""
        experience = CandidateExperience(
            candidate_id="cand-123",
            company_name="Tech Corp",
            position="Desenvolvedor Sênior",
            employment_type=EmploymentType.CLT,
            start_date=date(2020, 1, 1),
            is_current=True,
            responsibilities=["Desenvolvimento", "Code review"],
        )

        assert experience.company_name == "Tech Corp"
        assert experience.is_current is True
        assert experience.duration_months > 0

    def test_duration_calculation(self):
        """Testa cálculo de duração."""
        experience = CandidateExperience(
            candidate_id="cand-123",
            company_name="Tech Corp",
            position="Dev",
            start_date=date(2022, 1, 1),
            end_date=date(2023, 1, 1),
        )

        assert experience.duration_months == 12


class TestCandidateEducation:
    """Testes para CandidateEducation model."""

    def test_create_education(self):
        """Testa criação de formação."""
        education = CandidateEducation(
            candidate_id="cand-123",
            institution="USP",
            course="Ciência da Computação",
            level=EducationLevel.GRADUACAO,
            status=EducationStatus.CONCLUIDO,
            start_date=date(2015, 2, 1),
            end_date=date(2019, 12, 1),
        )

        assert education.institution == "USP"
        assert education.level == EducationLevel.GRADUACAO
        assert education.is_completed is True

    def test_is_higher_education(self):
        """Testa verificação de ensino superior."""
        education = CandidateEducation(
            candidate_id="cand-123",
            institution="ETEC",
            course="Técnico em Informática",
            level=EducationLevel.TECNICO,
        )
        assert education.is_higher_education is False

        education.level = EducationLevel.GRADUACAO
        assert education.is_higher_education is True


class TestEnums:
    """Testes para Enums."""

    def test_position_status_values(self):
        """Testa valores de PositionStatus."""
        assert PositionStatus.RASCUNHO.value == "rascunho"
        assert PositionStatus.ABERTA.value == "aberta"
        assert PositionStatus.PREENCHIDA.value == "preenchida"

    def test_candidate_source_values(self):
        """Testa valores de CandidateSource."""
        assert CandidateSource.SITE_CARREIRAS.value == "site_carreiras"
        assert CandidateSource.LINKEDIN.value == "linkedin"
        assert CandidateSource.INDICACAO.value == "indicacao"

    def test_application_status_values(self):
        """Testa valores de ApplicationStatus."""
        assert ApplicationStatus.INSCRITO.value == "inscrito"
        assert ApplicationStatus.CONTRATADO.value == "contratado"
        assert len(ApplicationStatus) == 14

    def test_interview_type_values(self):
        """Testa valores de InterviewType."""
        assert InterviewType.ENTREVISTA_RH.value == "entrevista_rh"
        assert InterviewType.ENTREVISTA_TECNICA.value == "entrevista_tecnica"
        assert len(InterviewType) == 8
