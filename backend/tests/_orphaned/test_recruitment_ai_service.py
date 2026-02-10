"""Testes para RecruitmentAIService."""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from modules.recruitment.models.candidate import (
    Candidate,
    CandidateSource,
)
from modules.recruitment.models.candidate_skill import (
    CandidateSkill,
    SkillCategory,
    SkillLevel,
)
from modules.recruitment.models.job_position import (
    Department,
    JobPosition,
    PositionLevel,
    PositionType,
    WorkModel,
)
from modules.recruitment.services.recruitment_ai_service import RecruitmentAIService


@pytest.fixture
def ai_service():
    """Fixture para serviço de IA."""
    return RecruitmentAIService()


@pytest.fixture
def sample_position():
    """Fixture para vaga de exemplo."""
    position = JobPosition(
        title="Desenvolvedor Python Sênior",
        description="Buscamos desenvolvedor Python experiente",
        department=Department.TI,
        position_type=PositionType.CLT,
        position_level=PositionLevel.SENIOR,
        work_model=WorkModel.HIBRIDO,
        salary_min=Decimal("12000"),
        salary_max=Decimal("18000"),
        city="São Paulo",
        state="SP",
        required_skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
        desired_skills=["Kubernetes", "AWS", "Redis"],
        experience_min=5,
    )
    return position


@pytest.fixture
def sample_candidate():
    """Fixture para candidato de exemplo."""
    candidate = Candidate(
        name="João Silva",
        email="joao@example.com",
        phone="11999999999",
        source=CandidateSource.LINKEDIN,
        city="São Paulo",
        state="SP",
        headline="Desenvolvedor Python Sênior | FastAPI | Django",
        salary_expectation=Decimal("15000"),
        years_experience=6,
        tags=["python", "fastapi", "postgresql", "docker", "aws"],
        available_immediately=True,
    )
    return candidate


@pytest.fixture
def sample_skills():
    """Fixture para habilidades de exemplo."""
    return [
        CandidateSkill(
            candidate_id="cand-123",
            name="Python",
            category=SkillCategory.TECNICA,
            level=SkillLevel.ESPECIALISTA,
            years_experience=6,
        ),
        CandidateSkill(
            candidate_id="cand-123",
            name="FastAPI",
            category=SkillCategory.TECNICA,
            level=SkillLevel.AVANCADO,
            years_experience=3,
        ),
        CandidateSkill(
            candidate_id="cand-123",
            name="PostgreSQL",
            category=SkillCategory.TECNICA,
            level=SkillLevel.AVANCADO,
            years_experience=5,
        ),
        CandidateSkill(
            candidate_id="cand-123",
            name="Docker",
            category=SkillCategory.FERRAMENTA,
            level=SkillLevel.INTERMEDIARIO,
            years_experience=2,
        ),
    ]


class TestMatchingScore:
    """Testes para cálculo de matching score."""

    @pytest.mark.asyncio
    async def test_calculate_matching_score_high_match(
        self, ai_service, sample_position, sample_candidate, sample_skills
    ):
        """Testa matching alto entre candidato e vaga."""
        result = await ai_service.calculate_matching_score(sample_candidate, sample_position, sample_skills)

        assert "final_score" in result
        assert result["final_score"] >= 70  # Alto match
        assert "scores" in result
        assert "recommendation" in result
        assert result["recommendation"]["level"] in ["bom", "excelente"]

    @pytest.mark.asyncio
    async def test_calculate_matching_score_low_match(self, ai_service, sample_position):
        """Testa matching baixo."""
        # Candidato sem skills relevantes
        candidate = Candidate(
            name="Maria Teste",
            email="maria@example.com",
            source=CandidateSource.SITE_CARREIRAS,
            city="Recife",
            state="PE",
            years_experience=1,
            salary_expectation=Decimal("25000"),  # Muito acima
            tags=["java", "spring"],
        )

        result = await ai_service.calculate_matching_score(candidate, sample_position, [])

        assert result["final_score"] < 50  # Baixo match
        assert result["recommendation"]["level"] in ["baixo", "incompatível", "moderado"]

    @pytest.mark.asyncio
    async def test_skills_match_calculation(self, ai_service, sample_position, sample_candidate, sample_skills):
        """Testa cálculo específico de match de skills."""
        result = await ai_service._calculate_skills_match(sample_candidate, sample_position, sample_skills)

        assert "score" in result
        assert "matched_required" in result
        assert "missing_required" in result
        assert result["score"] > 0.5  # Maioria das skills match

    @pytest.mark.asyncio
    async def test_experience_match_meets_requirement(self, ai_service, sample_position, sample_candidate):
        """Testa match de experiência quando atende requisito."""
        result = await ai_service._calculate_experience_match(sample_candidate, sample_position)

        assert result["meets_requirement"] is True
        assert result["score"] >= 0.9

    @pytest.mark.asyncio
    async def test_experience_match_below_requirement(self, ai_service, sample_position):
        """Testa match de experiência abaixo do requisito."""
        candidate = Candidate(
            name="Junior",
            email="junior@example.com",
            years_experience=2,  # Requisito é 5
        )

        result = await ai_service._calculate_experience_match(candidate, sample_position)

        assert result["meets_requirement"] is False
        assert result["score"] < 0.8

    def test_salary_match_within_range(self, ai_service, sample_position, sample_candidate):
        """Testa match de salário dentro da faixa."""
        result = ai_service._calculate_salary_match(sample_candidate, sample_position)

        assert result["compatible"] is True
        assert result["score"] >= 0.9

    def test_salary_match_above_range(self, ai_service, sample_position):
        """Testa match de salário acima da faixa."""
        candidate = Candidate(
            name="Teste",
            email="teste@example.com",
            salary_expectation=Decimal("25000"),  # Max é 18000
        )

        result = ai_service._calculate_salary_match(candidate, sample_position)

        assert result["compatible"] is False
        assert result["score"] < 0.7

    def test_location_match_same_city(self, ai_service, sample_position, sample_candidate):
        """Testa match de localização mesma cidade."""
        result = ai_service._calculate_location_match(sample_candidate, sample_position)

        assert result["score"] >= 0.9
        assert "Mesma cidade" in result["reason"]

    def test_location_match_remote(self, ai_service, sample_position):
        """Testa match de localização para vaga remota."""
        sample_position.work_model = WorkModel.REMOTO

        candidate = Candidate(
            name="Teste",
            email="teste@example.com",
            city="Manaus",
            state="AM",
        )

        result = ai_service._calculate_location_match(candidate, sample_position)

        assert result["score"] == 1.0
        assert "remota" in result["reason"].lower()


class TestResumeParser:
    """Testes para parsing de currículo."""

    @pytest.mark.asyncio
    async def test_parse_resume_skills(self, ai_service):
        """Testa extração de skills do currículo."""
        resume = """
        Desenvolvedor Python com 5 anos de experiência.
        Conhecimentos em FastAPI, Django, PostgreSQL, Docker.
        Fluente em inglês e espanhol.
        """

        result = await ai_service.parse_resume(resume)

        assert "skills" in result
        assert "python" in result["skills"]
        assert "fastapi" in result["skills"]
        assert "postgresql" in result["skills"]

    @pytest.mark.asyncio
    async def test_parse_resume_experience(self, ai_service):
        """Testa extração de experiência."""
        resume = "Profissional com 8 anos de experiência em TI."

        result = await ai_service.parse_resume(resume)

        assert result["experience_years"] == 8

    @pytest.mark.asyncio
    async def test_parse_resume_education(self, ai_service):
        """Testa extração de formação."""
        resume = "Mestrado em Ciência da Computação pela USP."

        result = await ai_service.parse_resume(resume)

        assert result["education_level"] == "mestrado"

    @pytest.mark.asyncio
    async def test_parse_resume_languages(self, ai_service):
        """Testa extração de idiomas."""
        resume = "Fluente em inglês e espanhol. Conhecimento básico de francês."

        result = await ai_service.parse_resume(resume)

        assert "inglês" in result["languages"]
        assert "espanhol" in result["languages"]
        assert "francês" in result["languages"]

    @pytest.mark.asyncio
    async def test_parse_resume_contact(self, ai_service):
        """Testa extração de contato."""
        resume = """
        João Silva
        Email: joao@email.com
        Telefone: (11) 99999-8888
        """

        result = await ai_service.parse_resume(resume)

        assert result["contact"]["email"] == "joao@email.com"
        assert "99999-8888" in result["contact"]["phone"]


class TestRanking:
    """Testes para ranking de candidatos."""

    @pytest.mark.asyncio
    async def test_rank_candidates(self, ai_service, sample_position):
        """Testa ranking de candidatos."""
        candidates = [
            (
                Candidate(
                    name="Candidato A",
                    email="a@example.com",
                    years_experience=6,
                    tags=["python", "fastapi", "docker"],
                    salary_expectation=Decimal("14000"),
                    city="São Paulo",
                    state="SP",
                ),
                [],
            ),
            (
                Candidate(
                    name="Candidato B",
                    email="b@example.com",
                    years_experience=2,
                    tags=["java"],
                    salary_expectation=Decimal("20000"),
                ),
                [],
            ),
            (
                Candidate(
                    name="Candidato C",
                    email="c@example.com",
                    years_experience=4,
                    tags=["python", "postgresql"],
                    salary_expectation=Decimal("15000"),
                    city="São Paulo",
                    state="SP",
                ),
                [],
            ),
        ]

        rankings = await ai_service.rank_candidates(candidates, sample_position)

        assert len(rankings) == 3
        assert rankings[0]["rank"] == 1
        assert rankings[0]["final_score"] >= rankings[1]["final_score"]
        assert rankings[1]["final_score"] >= rankings[2]["final_score"]


class TestPositionSuggestions:
    """Testes para sugestões de vagas."""

    @pytest.mark.asyncio
    async def test_suggest_positions(self, ai_service, sample_candidate, sample_skills):
        """Testa sugestões de vagas para candidato."""
        positions = [
            JobPosition(
                title="Dev Python",
                department=Department.TI,
                position_type=PositionType.CLT,
                position_level=PositionLevel.SENIOR,
                work_model=WorkModel.REMOTO,
                required_skills=["Python", "FastAPI"],
                salary_min=Decimal("12000"),
                salary_max=Decimal("18000"),
            ),
            JobPosition(
                title="Dev Java",
                department=Department.TI,
                position_type=PositionType.CLT,
                position_level=PositionLevel.PLENO,
                work_model=WorkModel.PRESENCIAL,
                required_skills=["Java", "Spring"],
            ),
        ]
        positions[0].code = "VAG-2024-0001"
        positions[1].code = "VAG-2024-0002"

        suggestions = await ai_service.suggest_positions(sample_candidate, positions, sample_skills, limit=5)

        assert len(suggestions) >= 1
        # Python deveria estar primeiro
        if len(suggestions) > 0:
            assert "Python" in suggestions[0]["position_title"]


class TestInterviewQuestions:
    """Testes para geração de perguntas."""

    @pytest.mark.asyncio
    async def test_generate_interview_questions(self, ai_service, sample_position, sample_candidate):
        """Testa geração de perguntas para entrevista."""
        questions = await ai_service.generate_interview_questions(sample_candidate, sample_position)

        assert len(questions) > 0

        # Verifica categorias
        categories = {q["category"] for q in questions}
        assert "tecnica" in categories
        assert "comportamental" in categories
        assert "motivacao" in categories

        # Verifica perguntas técnicas sobre skills requeridas
        tech_questions = [q for q in questions if q["category"] == "tecnica"]
        assert len(tech_questions) > 0


class TestRecommendations:
    """Testes para recomendações."""

    def test_get_recommendation_excellent(self, ai_service):
        """Testa recomendação para score excelente."""
        result = ai_service._get_recommendation(0.90)

        assert result["level"] == "excelente"
        assert "Priorizar" in result["action"]

    def test_get_recommendation_good(self, ai_service):
        """Testa recomendação para score bom."""
        result = ai_service._get_recommendation(0.75)

        assert result["level"] == "bom"
        assert "entrevista" in result["action"].lower()

    def test_get_recommendation_moderate(self, ai_service):
        """Testa recomendação para score moderado."""
        result = ai_service._get_recommendation(0.60)

        assert result["level"] == "moderado"

    def test_get_recommendation_low(self, ai_service):
        """Testa recomendação para score baixo."""
        result = ai_service._get_recommendation(0.45)

        assert result["level"] == "baixo"
        assert "banco" in result["action"].lower()

    def test_get_recommendation_incompatible(self, ai_service):
        """Testa recomendação para score incompatível."""
        result = ai_service._get_recommendation(0.25)

        assert result["level"] == "incompatível"
        assert "Não prosseguir" in result["action"]
