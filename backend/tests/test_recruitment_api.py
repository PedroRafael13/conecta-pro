"""Testes para API do módulo Recruitment."""

import pytest
from datetime import date, time, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from modules.recruitment.controllers import (
    job_position_router,
    candidate_router,
    application_router,
    interview_router,
)
from modules.recruitment.models.job_position import (
    JobPosition,
    PositionStatus,
    PositionType,
    PositionLevel,
    WorkModel,
    Department,
)
from modules.recruitment.models.candidate import (
    Candidate,
    CandidateStatus,
    CandidateSource,
)
from modules.recruitment.models.application import Application, ApplicationStatus
from modules.recruitment.models.interview import Interview, InterviewType, InterviewStatus


@pytest.fixture
def app():
    """Fixture para app FastAPI de teste."""
    test_app = FastAPI()
    test_app.include_router(job_position_router, prefix="/api/v1/recruitment")
    test_app.include_router(candidate_router, prefix="/api/v1/recruitment")
    test_app.include_router(application_router, prefix="/api/v1/recruitment")
    test_app.include_router(interview_router, prefix="/api/v1/recruitment")
    return test_app


@pytest.fixture
def mock_db():
    """Fixture para mock do banco de dados."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_current_user():
    """Fixture para mock do usuário atual."""
    return {
        "id": "user-123",
        "email": "admin@example.com",
        "role": "admin",
    }


@pytest.fixture
def sample_position_data():
    """Fixture para dados de vaga."""
    return {
        "title": "Desenvolvedor Python Sênior",
        "description": "Vaga para desenvolvedor experiente",
        "department": "ti",
        "position_type": "clt",
        "position_level": "senior",
        "work_model": "hibrido",
        "salary_min": 12000,
        "salary_max": 18000,
        "vacancies": 2,
        "city": "São Paulo",
        "state": "SP",
        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        "desired_skills": ["Docker", "Kubernetes"],
        "experience_min": 5,
    }


@pytest.fixture
def sample_candidate_data():
    """Fixture para dados de candidato."""
    return {
        "name": "João Silva",
        "email": "joao@example.com",
        "phone": "11999999999",
        "source": "linkedin",
        "city": "São Paulo",
        "state": "SP",
        "headline": "Desenvolvedor Python Sênior",
        "salary_expectation": 15000,
    }


class TestJobPositionAPI:
    """Testes para API de vagas."""

    @pytest.mark.asyncio
    async def test_create_position(self, app, sample_position_data):
        """Testa criação de vaga via API."""
        with patch("modules.recruitment.controllers.job_position_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.job_position_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.job_position_controller.JobPositionService"
                ) as mock_service:
                    position = JobPosition(**sample_position_data)
                    position.id = "pos-123"
                    position.code = "VAG-2024-0001"
                    mock_service.return_value.create = AsyncMock(return_value=position)

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.post(
                            "/api/v1/recruitment/job-positions/",
                            json=sample_position_data,
                        )

                    assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_list_positions(self, app):
        """Testa listagem de vagas."""
        with patch("modules.recruitment.controllers.job_position_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.job_position_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.job_position_controller.JobPositionService"
                ) as mock_service:
                    mock_service.return_value.list_with_filters = AsyncMock(
                        return_value=([], 0)
                    )

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.get(
                            "/api/v1/recruitment/job-positions/"
                        )

                    assert response.status_code == 200
                    data = response.json()
                    assert "items" in data
                    assert "total" in data

    @pytest.mark.asyncio
    async def test_get_position_not_found(self, app):
        """Testa busca de vaga inexistente."""
        with patch("modules.recruitment.controllers.job_position_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.job_position_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.job_position_controller.JobPositionService"
                ) as mock_service:
                    mock_service.return_value.get_by_id = AsyncMock(return_value=None)
                    mock_service.return_value.increment_view = AsyncMock()

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.get(
                            "/api/v1/recruitment/job-positions/invalid-id"
                        )

                    assert response.status_code == 404


class TestCandidateAPI:
    """Testes para API de candidatos."""

    @pytest.mark.asyncio
    async def test_create_candidate(self, app, sample_candidate_data):
        """Testa criação de candidato via API."""
        with patch("modules.recruitment.controllers.candidate_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.candidate_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.candidate_controller.CandidateService"
                ) as mock_service:
                    candidate = Candidate(**sample_candidate_data)
                    candidate.id = "cand-123"
                    mock_service.return_value.create = AsyncMock(return_value=candidate)

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.post(
                            "/api/v1/recruitment/candidates/",
                            json=sample_candidate_data,
                        )

                    assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_duplicate_candidate(self, app, sample_candidate_data):
        """Testa criação de candidato duplicado."""
        with patch("modules.recruitment.controllers.candidate_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.candidate_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.candidate_controller.CandidateService"
                ) as mock_service:
                    mock_service.return_value.create = AsyncMock(
                        side_effect=ValueError("Candidato já cadastrado")
                    )

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.post(
                            "/api/v1/recruitment/candidates/",
                            json=sample_candidate_data,
                        )

                    assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_search_by_skills(self, app):
        """Testa busca por habilidades."""
        with patch("modules.recruitment.controllers.candidate_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.candidate_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.candidate_controller.CandidateService"
                ) as mock_service:
                    mock_service.return_value.search_by_skills = AsyncMock(
                        return_value=[]
                    )

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.get(
                            "/api/v1/recruitment/candidates/search-skills",
                            params={"skills": ["python", "fastapi"]},
                        )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_block_candidate(self, app):
        """Testa bloqueio de candidato."""
        with patch("modules.recruitment.controllers.candidate_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.candidate_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.candidate_controller.CandidateService"
                ) as mock_service:
                    candidate = Candidate(
                        name="Teste",
                        email="teste@example.com",
                    )
                    candidate.id = "cand-123"
                    candidate.is_blocked = True
                    mock_service.return_value.block = AsyncMock(return_value=candidate)

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.post(
                            "/api/v1/recruitment/candidates/cand-123/block",
                            json={"reason": "Motivo teste", "blocked_by": "admin"},
                        )

                    assert response.status_code == 200


class TestApplicationAPI:
    """Testes para API de candidaturas."""

    @pytest.mark.asyncio
    async def test_create_application(self, app):
        """Testa criação de candidatura."""
        with patch("modules.recruitment.controllers.application_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.application_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.application_controller.ApplicationService"
                ) as mock_service:
                    application = Application(
                        candidate_id="cand-123",
                        job_position_id="pos-456",
                    )
                    application.id = "app-789"
                    mock_service.return_value.create = AsyncMock(return_value=application)

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.post(
                            "/api/v1/recruitment/applications/",
                            json={
                                "candidate_id": "cand-123",
                                "job_position_id": "pos-456",
                            },
                        )

                    assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_advance_stage(self, app):
        """Testa avanço de etapa."""
        with patch("modules.recruitment.controllers.application_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.application_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.application_controller.ApplicationService"
                ) as mock_service:
                    application = Application(
                        candidate_id="cand-123",
                        job_position_id="pos-456",
                    )
                    application.id = "app-789"
                    application.status = ApplicationStatus.TRIAGEM
                    mock_service.return_value.advance_stage = AsyncMock(
                        return_value=application
                    )

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.post(
                            "/api/v1/recruitment/applications/app-789/advance",
                            json={
                                "new_status": "triagem",
                                "notes": "Aprovado na triagem inicial",
                            },
                        )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_bulk_action(self, app):
        """Testa ação em lote."""
        with patch("modules.recruitment.controllers.application_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.application_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.application_controller.ApplicationService"
                ) as mock_service:
                    mock_service.return_value.bulk_action = AsyncMock(
                        return_value=(3, 0)
                    )

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.post(
                            "/api/v1/recruitment/applications/bulk-action",
                            json={
                                "application_ids": ["app-1", "app-2", "app-3"],
                                "action": "favorite",
                            },
                        )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] == 3
                    assert data["failed"] == 0


class TestInterviewAPI:
    """Testes para API de entrevistas."""

    @pytest.mark.asyncio
    async def test_create_interview(self, app):
        """Testa agendamento de entrevista."""
        interview_data = {
            "application_id": "app-123",
            "interview_type": "entrevista_rh",
            "scheduled_date": str(date.today() + timedelta(days=7)),
            "scheduled_time": "14:00:00",
            "duration_minutes": 60,
            "interviewer_ids": ["int-001"],
            "location": "Sala de reunião 1",
        }

        with patch("modules.recruitment.controllers.interview_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.interview_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.interview_controller.InterviewService"
                ) as mock_service:
                    interview = Interview(
                        application_id="app-123",
                        interview_type=InterviewType.ENTREVISTA_RH,
                        scheduled_date=date.today() + timedelta(days=7),
                        scheduled_time=time(14, 0),
                    )
                    interview.id = "int-456"
                    mock_service.return_value.create = AsyncMock(return_value=interview)

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.post(
                            "/api/v1/recruitment/interviews/",
                            json=interview_data,
                        )

                    assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_get_today_interviews(self, app):
        """Testa busca de entrevistas de hoje."""
        with patch("modules.recruitment.controllers.interview_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.interview_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.interview_controller.InterviewService"
                ) as mock_service:
                    mock_service.return_value.get_today = AsyncMock(return_value=[])

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.get(
                            "/api/v1/recruitment/interviews/today"
                        )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_complete_interview(self, app):
        """Testa conclusão de entrevista."""
        with patch("modules.recruitment.controllers.interview_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.interview_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.interview_controller.InterviewService"
                ) as mock_service:
                    interview = Interview(
                        application_id="app-123",
                        interview_type=InterviewType.ENTREVISTA_RH,
                        scheduled_date=date.today(),
                        scheduled_time=time(14, 0),
                    )
                    interview.id = "int-456"
                    interview.status = InterviewStatus.REALIZADA
                    mock_service.return_value.complete = AsyncMock(
                        return_value=interview
                    )

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.post(
                            "/api/v1/recruitment/interviews/int-456/complete",
                            json={
                                "result": "aprovado",
                                "score": 85,
                                "feedback": "Excelente candidato",
                            },
                        )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_reschedule_interview(self, app):
        """Testa reagendamento de entrevista."""
        with patch("modules.recruitment.controllers.interview_controller.get_db"):
            with patch(
                "modules.recruitment.controllers.interview_controller.get_current_user"
            ) as mock_user:
                mock_user.return_value = {"id": "user-123"}

                with patch(
                    "modules.recruitment.controllers.interview_controller.InterviewService"
                ) as mock_service:
                    interview = Interview(
                        application_id="app-123",
                        interview_type=InterviewType.ENTREVISTA_RH,
                        scheduled_date=date.today() + timedelta(days=14),
                        scheduled_time=time(10, 0),
                    )
                    interview.id = "int-456"
                    interview.status = InterviewStatus.REAGENDADA
                    mock_service.return_value.reschedule = AsyncMock(
                        return_value=interview
                    )

                    transport = ASGITransport(app=app)
                    async with AsyncClient(
                        transport=transport, base_url="http://test"
                    ) as client:
                        response = await client.post(
                            "/api/v1/recruitment/interviews/int-456/reschedule",
                            json={
                                "new_date": str(date.today() + timedelta(days=14)),
                                "new_time": "10:00:00",
                            },
                        )

                    assert response.status_code == 200
