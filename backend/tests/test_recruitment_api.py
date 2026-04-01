"""Testes para API do modulo Recruitment."""

from datetime import date, datetime, time, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.recruitment.controllers import (
    application_router,
    candidate_router,
    interview_router,
    job_position_router,
)
from modules.recruitment.models.application import ApplicationStatus
from modules.recruitment.models.candidate import CandidateStatus
from modules.recruitment.models.interview import InterviewStatus, InterviewType
from modules.recruitment.models.job_position import (
    Department,
    PositionLevel,
    PositionStatus,
    PositionType,
    WorkModel,
)
from modules.recruitment.schemas.application import ApplicationResponse
from modules.recruitment.schemas.candidate import CandidateResponse
from modules.recruitment.schemas.interview import InterviewResponse
from modules.recruitment.schemas.job_position import JobPositionResponse

# ---------------------------------------------------------------------------
# Helpers para construir response schemas validos
# ---------------------------------------------------------------------------


def _make_position_response(**overrides):
    """Cria um JobPositionResponse valido para testes."""
    defaults = {
        "id": "pos-123",
        "code": "VAG-2024-0001",
        "title": "Dev Python",
        "description": None,
        "position_type": PositionType.CLT,
        "position_level": PositionLevel.SENIOR,
        "department": Department.TI,
        "requirements": None,
        "responsibilities": None,
        "required_skills": ["Python"],
        "desired_skills": [],
        "min_experience_years": 5,
        "education_level": None,
        "salary_min": None,
        "salary_max": None,
        "salary_display": False,
        "benefits": [],
        "work_model": WorkModel.HIBRIDO,
        "city": "Sao Paulo",
        "state": "SP",
        "address": None,
        "vacancies": 2,
        "is_urgent": False,
        "is_confidential": False,
        "deadline_date": None,
        "expected_start_date": None,
        "selection_stages": None,
        "status": PositionStatus.RASCUNHO,
        "opening_date": None,
        "closed_at": None,
        "filled_vacancies": 0,
        "applications_count": 0,
        "views_count": 0,
        "recruiter_id": None,
        "hiring_manager_id": None,
        "condominium_id": None,
        "created_by": None,
        "created_at": datetime.now(),
        "updated_at": None,
        "is_open": False,
        "is_expired": False,
        "remaining_vacancies": 2,
        "is_fully_filled": False,
        "salary_range": "A combinar",
    }
    defaults.update(overrides)
    return JobPositionResponse(**defaults)


def _make_candidate_response(**overrides):
    """Cria um CandidateResponse valido para testes."""
    defaults = {
        "id": "cand-123",
        "name": "Joao Silva",
        "email": "joao@example.com",
        "status": CandidateStatus.ATIVO,
        "created_at": datetime.now(),
        "is_available": True,
        "full_address": "",
        "profile_completeness": 50,
    }
    defaults.update(overrides)
    return CandidateResponse(**defaults)


def _make_application_response(**overrides):
    """Cria um ApplicationResponse valido para testes."""
    defaults = {
        "id": "app-789",
        "job_position_id": "pos-456",
        "candidate_id": "cand-123",
        "status": ApplicationStatus.INSCRITO,
        "current_stage": 0,
        "applied_at": datetime.now(),
        "created_at": datetime.now(),
        "is_active": True,
        "is_in_process": True,
        "is_hired": False,
        "is_rejected": False,
        "days_in_process": 0,
    }
    defaults.update(overrides)
    return ApplicationResponse(**defaults)


def _make_interview_response(**overrides):
    """Cria um InterviewResponse valido para testes."""
    defaults = {
        "id": "int-456",
        "application_id": "app-123",
        "scheduled_date": date.today(),
        "scheduled_time": time(14, 0),
        "status": InterviewStatus.AGENDADA,
        "created_at": datetime.now(),
        "scheduled_datetime": datetime.now(),
        "is_past": False,
        "is_today": True,
        "is_upcoming": False,
        "is_pending_result": False,
        "was_successful": False,
    }
    defaults.update(overrides)
    return InterviewResponse(**defaults)


def _make_paginated_response(items, total, skip=0, limit=20):
    """Cria dict compativel com *ListResponse."""
    page_size = max(limit, 1)
    pages = max((total + page_size - 1) // page_size, 1) if total else 1
    return {
        "items": items,
        "total": total,
        "page": (skip // page_size) + 1 if page_size else 1,
        "page_size": page_size,
        "pages": pages,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """Fixture para app FastAPI de teste."""
    test_app = FastAPI()
    test_app.include_router(job_position_router, prefix="/api/v1/recruitment")
    test_app.include_router(candidate_router, prefix="/api/v1/recruitment")
    test_app.include_router(application_router, prefix="/api/v1/recruitment")
    test_app.include_router(interview_router, prefix="/api/v1/recruitment")

    # Dependency overrides para auth e db
    async def _mock_get_current_user():
        return {"id": "user-123", "email": "admin@example.com", "role": "admin"}

    async def _mock_get_db():
        yield AsyncMock()

    test_app.dependency_overrides[get_current_user] = _mock_get_current_user
    test_app.dependency_overrides[get_db] = _mock_get_db

    return test_app


@pytest.fixture
def sample_position_data():
    """Fixture para dados de vaga."""
    return {
        "title": "Desenvolvedor Python Senior",
        "description": "Vaga para desenvolvedor experiente",
        "department": "ti",
        "position_type": "clt",
        "position_level": "senior",
        "work_model": "hibrido",
        "salary_min": 12000,
        "salary_max": 18000,
        "vacancies": 2,
        "city": "Sao Paulo",
        "state": "SP",
        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        "desired_skills": ["Docker", "Kubernetes"],
        "min_experience_years": 5,
    }


@pytest.fixture
def sample_candidate_data():
    """Fixture para dados de candidato."""
    return {
        "name": "Joao Silva",
        "email": "joao@example.com",
        "phone": "11999999999",
        "source": "linkedin",
        "city": "Sao Paulo",
        "state": "SP",
        "headline": "Desenvolvedor Python Senior",
        "salary_expectation": 15000,
    }


# ---------------------------------------------------------------------------
# Tests - JobPosition
# ---------------------------------------------------------------------------


class TestJobPositionAPI:
    """Testes para API de vagas."""

    @pytest.mark.asyncio
    async def test_create_position(self, app, sample_position_data):
        """Testa criacao de vaga via API."""
        resp_obj = _make_position_response()

        with patch("modules.recruitment.controllers.job_position_controller.JobPositionService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.create = AsyncMock(return_value=MagicMock())

            with patch.object(JobPositionResponse, "model_validate", return_value=resp_obj):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/recruitment/job-positions/",
                        json=sample_position_data,
                    )

                assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_list_positions(self, app):
        """Testa listagem de vagas."""
        with patch("modules.recruitment.controllers.job_position_controller.JobPositionService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.list_with_filters = AsyncMock(return_value=([], 0))

            paginated = _make_paginated_response([], 0)
            with patch(
                "modules.recruitment.controllers.job_position_controller.JobPositionListResponse",
                return_value=MagicMock(**paginated),
            ):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/api/v1/recruitment/job-positions/")

                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_position_not_found(self, app):
        """Testa busca de vaga inexistente."""
        with patch("modules.recruitment.controllers.job_position_controller.JobPositionService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.get_by_id = AsyncMock(return_value=None)

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/recruitment/job-positions/invalid-id")

            assert response.status_code == 404


# ---------------------------------------------------------------------------
# Tests - Candidate
# ---------------------------------------------------------------------------


class TestCandidateAPI:
    """Testes para API de candidatos."""

    @pytest.mark.asyncio
    async def test_create_candidate(self, app, sample_candidate_data):
        """Testa criacao de candidato via API."""
        resp_obj = _make_candidate_response()

        with patch("modules.recruitment.controllers.candidate_controller.CandidateService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.create = AsyncMock(return_value=MagicMock())

            with patch.object(CandidateResponse, "model_validate", return_value=resp_obj):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/recruitment/candidates/",
                        json=sample_candidate_data,
                    )

                assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_duplicate_candidate(self, app, sample_candidate_data):
        """Testa criacao de candidato duplicado."""
        with patch("modules.recruitment.controllers.candidate_controller.CandidateService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.create = AsyncMock(side_effect=ValueError("Candidato ja cadastrado"))

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/recruitment/candidates/",
                    json=sample_candidate_data,
                )

            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_search_by_skills(self, app):
        """Testa busca por habilidades."""
        with patch("modules.recruitment.controllers.candidate_controller.CandidateService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.search_by_skills = AsyncMock(return_value=[])

            paginated = _make_paginated_response([], 0, limit=50)
            with patch(
                "modules.recruitment.controllers.candidate_controller.CandidateListResponse",
                return_value=MagicMock(**paginated),
            ):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get(
                        "/api/v1/recruitment/candidates/search-skills",
                        params={"skills": ["python", "fastapi"]},
                    )

                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_block_candidate(self, app):
        """Testa bloqueio de candidato."""
        resp_obj = _make_candidate_response(
            is_blocked=True,
            block_reason="Motivo teste",
        )

        with patch("modules.recruitment.controllers.candidate_controller.CandidateService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.block = AsyncMock(return_value=MagicMock())

            with patch.object(CandidateResponse, "model_validate", return_value=resp_obj):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/recruitment/candidates/cand-123/block",
                        json={"reason": "Motivo teste"},
                    )

                assert response.status_code == 200


# ---------------------------------------------------------------------------
# Tests - Application
# ---------------------------------------------------------------------------


class TestApplicationAPI:
    """Testes para API de candidaturas."""

    @pytest.mark.asyncio
    async def test_create_application(self, app):
        """Testa criacao de candidatura."""
        resp_obj = _make_application_response()

        with patch("modules.recruitment.controllers.application_controller.ApplicationService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.create = AsyncMock(return_value=MagicMock())

            with patch.object(ApplicationResponse, "model_validate", return_value=resp_obj):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
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
        """Testa avanco de etapa."""
        resp_obj = _make_application_response(
            status=ApplicationStatus.TRIAGEM,
        )

        with patch("modules.recruitment.controllers.application_controller.ApplicationService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.advance_stage = AsyncMock(return_value=MagicMock())

            with patch.object(ApplicationResponse, "model_validate", return_value=resp_obj):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
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
        """Testa acao em lote."""
        with patch("modules.recruitment.controllers.application_controller.ApplicationService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.bulk_action = AsyncMock(return_value=(3, 0))

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
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


# ---------------------------------------------------------------------------
# Tests - Interview
# ---------------------------------------------------------------------------


class TestInterviewAPI:
    """Testes para API de entrevistas."""

    @pytest.mark.asyncio
    async def test_create_interview(self, app):
        """Testa agendamento de entrevista."""
        interview_data = {
            "application_id": "app-123",
            "interview_type": "tecnica",
            "scheduled_date": str(date.today() + timedelta(days=7)),
            "scheduled_time": "14:00:00",
            "duration_minutes": 60,
            "interviewer_ids": ["int-001"],
            "location": "Sala de reuniao 1",
        }

        resp_obj = _make_interview_response(
            interview_type=InterviewType.TECNICA,
            scheduled_date=date.today() + timedelta(days=7),
        )

        with patch("modules.recruitment.controllers.interview_controller.InterviewService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.create = AsyncMock(return_value=MagicMock())

            with patch.object(InterviewResponse, "model_validate", return_value=resp_obj):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/recruitment/interviews/",
                        json=interview_data,
                    )

                assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_get_today_interviews(self, app):
        """Testa busca de entrevistas de hoje."""
        with patch("modules.recruitment.controllers.interview_controller.InterviewService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.get_today = AsyncMock(return_value=[])

            paginated = _make_paginated_response([], 0, limit=0)
            with patch(
                "modules.recruitment.controllers.interview_controller.InterviewListResponse",
                return_value=MagicMock(**paginated),
            ):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get("/api/v1/recruitment/interviews/today")

                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_complete_interview(self, app):
        """Testa conclusao de entrevista."""
        resp_obj = _make_interview_response(
            status=InterviewStatus.REALIZADA,
        )

        with patch("modules.recruitment.controllers.interview_controller.InterviewService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.complete = AsyncMock(return_value=MagicMock())

            with patch.object(InterviewResponse, "model_validate", return_value=resp_obj):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
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
        resp_obj = _make_interview_response(
            status=InterviewStatus.REAGENDADA,
            scheduled_date=date.today() + timedelta(days=14),
            scheduled_time=time(10, 0),
        )

        with patch("modules.recruitment.controllers.interview_controller.InterviewService") as mock_svc_cls:
            svc = mock_svc_cls.return_value
            svc.reschedule = AsyncMock(return_value=MagicMock())

            with patch.object(InterviewResponse, "model_validate", return_value=resp_obj):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/recruitment/interviews/int-456/reschedule",
                        json={
                            "new_date": str(date.today() + timedelta(days=14)),
                            "new_time": "10:00:00",
                        },
                    )

                assert response.status_code == 200
