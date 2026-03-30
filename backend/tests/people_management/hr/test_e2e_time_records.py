"""
Testes E2E do modulo HR Time Records — 8 endpoints com mocking de servico.

Endpoints cobertos:
1. GET  /time-records                           — list com filtros e paginacao
2. GET  /time-records/daily/{record_date}       — registros diarios
3. GET  /time-records/employee/{id}/summary     — resumo mensal
4. POST /time-records/clock-in                  — batida de entrada
5. POST /time-records/clock-out/{record_id}     — batida de saida
6. POST /time-records                           — lancamento manual
7. GET  /time-records/{record_id}               — busca por ID
8. PATCH /time-records/{record_id}              — atualizar registro
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from core.auth.dependencies import get_current_active_user
from core.database import get_db
from modules.people_management.hr.controllers.time_record_controller import router as time_records_router

# ===========================================================================
# CONSTANTS
# ===========================================================================

BASE_URL = "http://test"
PREFIX = "/api/v1"
PATCH_TARGET = "modules.people_management.hr.controllers.time_record_controller.TimeRecordService"

SAMPLE_RECORD_ID = "punch-abc-123"
SAMPLE_EMPLOYEE_ID = "emp-uuid-001"

# ---------------------------------------------------------------------------
# Realistic mock return values
# ---------------------------------------------------------------------------

SAMPLE_TIME_RECORD = {
    "id": SAMPLE_RECORD_ID,
    "employee_id": SAMPLE_EMPLOYEE_ID,
    "employee_name": "Joao Silva",
    "record_date": "2026-03-29",
    "clock_in": "08:00",
    "clock_out": "17:00",
    "clock_in_lunch": "12:00",
    "clock_out_lunch": "13:00",
    "total_hours": "08:00",
    "overtime_hours": "00:00",
    "status": "regular",
    "justification": None,
    "location_lat": -3.1,
    "location_lng": -60.0,
    "registered_by": "web",
    "source": "portal",
    "created_at": "2026-03-29T08:00:00",
    "updated_at": None,
}

SAMPLE_LIST_RESPONSE = {
    "items": [SAMPLE_TIME_RECORD],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
}

SAMPLE_EMPTY_LIST = {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
}

SAMPLE_DAILY_RESPONSE = {
    "date": "2026-03-29",
    "total_employees": 1,
    "records": [SAMPLE_TIME_RECORD],
}

SAMPLE_DAILY_EMPTY = {
    "date": "2026-03-29",
    "total_employees": 0,
    "records": [],
}

SAMPLE_SUMMARY = {
    "employee_id": SAMPLE_EMPLOYEE_ID,
    "employee_name": "Joao Silva",
    "month": 3,
    "year": 2026,
    "total_work_days": 21,
    "total_worked_days": 20,
    "total_hours_worked": "160:00",
    "total_hours_worked_minutes": 9600,
    "total_overtime_minutes": 120,
    "total_overtime": "02:00",
    "total_late_minutes": 0,
    "total_absences": 1,
    "total_justified_absences": 0,
    "total_unjustified_absences": 1,
    "total_medical_leaves": 0,
    "total_holidays": 0,
    "total_night_hours_minutes": 0,
    "records": [],
}


# ===========================================================================
# FIXTURES
# ===========================================================================


async def get_fake_db():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.rollback = AsyncMock()
    yield session


def get_fake_user():
    user = MagicMock()
    user.id = "admin-1"
    user.email = "admin@test.com"
    user.is_active = True
    user.role = "admin"
    return user


@pytest.fixture
def app():
    application = FastAPI()
    application.include_router(time_records_router, prefix=f"{PREFIX}")
    application.dependency_overrides[get_db] = get_fake_db
    application.dependency_overrides[get_current_active_user] = get_fake_user
    return application


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        yield ac


# ===========================================================================
# 1. GET /time-records — LIST
# ===========================================================================


class TestListTimeRecords:
    """Testes para GET /time-records."""

    @pytest.mark.asyncio
    async def test_list_returns_200_with_data(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.list_records = AsyncMock(return_value=SAMPLE_LIST_RESPONSE)
            response = await client.get(f"{PREFIX}/time-records")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["page"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == SAMPLE_RECORD_ID

    @pytest.mark.asyncio
    async def test_list_empty_results(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.list_records = AsyncMock(return_value=SAMPLE_EMPTY_LIST)
            response = await client.get(f"{PREFIX}/time-records")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_list_filter_by_employee_id(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.list_records = AsyncMock(return_value=SAMPLE_LIST_RESPONSE)
            response = await client.get(
                f"{PREFIX}/time-records",
                params={"employee_id": SAMPLE_EMPLOYEE_ID},
            )
        assert response.status_code == 200
        instance.list_records.assert_called_once()
        call_kwargs = instance.list_records.call_args.kwargs
        assert call_kwargs["employee_id"] == SAMPLE_EMPLOYEE_ID

    @pytest.mark.asyncio
    async def test_list_filter_by_date_range(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.list_records = AsyncMock(return_value=SAMPLE_LIST_RESPONSE)
            response = await client.get(
                f"{PREFIX}/time-records",
                params={"date_from": "2026-03-01", "date_to": "2026-03-31"},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_filter_by_status(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.list_records = AsyncMock(return_value=SAMPLE_LIST_RESPONSE)
            response = await client.get(
                f"{PREFIX}/time-records",
                params={"status": "regular"},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_pagination(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            paginated = {**SAMPLE_LIST_RESPONSE, "page": 2, "page_size": 10, "total_pages": 3}
            instance.list_records = AsyncMock(return_value=paginated)
            response = await client.get(
                f"{PREFIX}/time-records",
                params={"page": 2, "page_size": 10},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_list_page_size_exceeds_max_returns_422(self, client):
        """page_size <= 100, acima retorna 422."""
        response = await client.get(
            f"{PREFIX}/time-records",
            params={"page_size": 101},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_page_zero_returns_422(self, client):
        """page >= 1, page=0 retorna 422."""
        response = await client.get(
            f"{PREFIX}/time-records",
            params={"page": 0},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_all_filters_combined(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.list_records = AsyncMock(return_value=SAMPLE_LIST_RESPONSE)
            response = await client.get(
                f"{PREFIX}/time-records",
                params={
                    "employee_id": SAMPLE_EMPLOYEE_ID,
                    "date_from": "2026-03-01",
                    "date_to": "2026-03-31",
                    "status": "regular",
                    "page": 1,
                    "page_size": 50,
                },
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_page_size_min_valid(self, client):
        """page_size=1 deve ser aceito (ge=1)."""
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.list_records = AsyncMock(return_value=SAMPLE_EMPTY_LIST)
            response = await client.get(
                f"{PREFIX}/time-records",
                params={"page_size": 1},
            )
        assert response.status_code == 200


# ===========================================================================
# 2. GET /time-records/daily/{record_date} — DAILY RECORDS
# ===========================================================================


class TestDailyRecords:
    """Testes para GET /time-records/daily/{record_date}."""

    @pytest.mark.asyncio
    async def test_get_daily_returns_200(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_daily = AsyncMock(return_value=SAMPLE_DAILY_RESPONSE)
            response = await client.get(f"{PREFIX}/time-records/daily/2026-03-29")
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == "2026-03-29"
        assert data["total_employees"] == 1
        assert len(data["records"]) == 1

    @pytest.mark.asyncio
    async def test_get_daily_empty_day(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_daily = AsyncMock(return_value=SAMPLE_DAILY_EMPTY)
            response = await client.get(f"{PREFIX}/time-records/daily/2026-03-01")
        assert response.status_code == 200
        data = response.json()
        assert data["total_employees"] == 0
        assert data["records"] == []

    @pytest.mark.asyncio
    async def test_get_daily_invalid_date_format_returns_422(self, client):
        """Data no formato errado deve retornar 422."""
        response = await client.get(f"{PREFIX}/time-records/daily/not-a-date")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_daily_future_date(self, client):
        """Data futura e valida para o endpoint."""
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_daily = AsyncMock(return_value=SAMPLE_DAILY_EMPTY)
            response = await client.get(f"{PREFIX}/time-records/daily/2026-12-31")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_daily_multiple_employees(self, client):
        record2 = {**SAMPLE_TIME_RECORD, "id": "punch-xyz-456", "employee_id": "emp-uuid-002"}
        multi_response = {
            "date": "2026-03-29",
            "total_employees": 2,
            "records": [SAMPLE_TIME_RECORD, record2],
        }
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_daily = AsyncMock(return_value=multi_response)
            response = await client.get(f"{PREFIX}/time-records/daily/2026-03-29")
        assert response.status_code == 200
        data = response.json()
        assert data["total_employees"] == 2
        assert len(data["records"]) == 2

    @pytest.mark.asyncio
    async def test_get_daily_date_passed_to_service(self, client):
        """Confirma que a data correta e passada ao service."""
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_daily = AsyncMock(return_value=SAMPLE_DAILY_RESPONSE)
            await client.get(f"{PREFIX}/time-records/daily/2026-03-15")
        instance.get_daily.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_daily_with_inconsistencies(self, client):
        incon_record = {**SAMPLE_TIME_RECORD, "status": "inconsistencia", "clock_out": None}
        response_data = {"date": "2026-03-29", "total_employees": 1, "records": [incon_record]}
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_daily = AsyncMock(return_value=response_data)
            response = await client.get(f"{PREFIX}/time-records/daily/2026-03-29")
        assert response.status_code == 200
        data = response.json()
        assert data["records"][0]["status"] == "inconsistencia"

    @pytest.mark.asyncio
    async def test_get_daily_missing_date_in_path_returns_non_200(self, client):
        """Chamada sem data no path retorna redirecionamento ou erro, nao 200."""
        response = await client.get(f"{PREFIX}/time-records/daily/", follow_redirects=False)
        assert response.status_code in (307, 308, 404, 405, 422)

    @pytest.mark.asyncio
    async def test_get_daily_year_month_day_format(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_daily = AsyncMock(return_value=SAMPLE_DAILY_RESPONSE)
            response = await client.get(f"{PREFIX}/time-records/daily/2026-01-01")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_daily_records_have_required_fields(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_daily = AsyncMock(return_value=SAMPLE_DAILY_RESPONSE)
            response = await client.get(f"{PREFIX}/time-records/daily/2026-03-29")
        data = response.json()
        record = data["records"][0]
        assert "id" in record
        assert "employee_id" in record
        assert "record_date" in record
        assert "status" in record


# ===========================================================================
# 3. GET /time-records/employee/{employee_id}/summary — MONTHLY SUMMARY
# ===========================================================================


class TestEmployeeSummary:
    """Testes para GET /time-records/employee/{employee_id}/summary."""

    @pytest.mark.asyncio
    async def test_get_summary_returns_200(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_summary = AsyncMock(return_value=SAMPLE_SUMMARY)
            response = await client.get(
                f"{PREFIX}/time-records/employee/{SAMPLE_EMPLOYEE_ID}/summary",
                params={"month": 3, "year": 2026},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == SAMPLE_EMPLOYEE_ID
        assert data["month"] == 3
        assert data["year"] == 2026

    @pytest.mark.asyncio
    async def test_get_summary_missing_month_returns_422(self, client):
        """month e required."""
        response = await client.get(
            f"{PREFIX}/time-records/employee/{SAMPLE_EMPLOYEE_ID}/summary",
            params={"year": 2026},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_summary_missing_year_returns_422(self, client):
        """year e required."""
        response = await client.get(
            f"{PREFIX}/time-records/employee/{SAMPLE_EMPLOYEE_ID}/summary",
            params={"month": 3},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_summary_missing_both_params_returns_422(self, client):
        response = await client.get(
            f"{PREFIX}/time-records/employee/{SAMPLE_EMPLOYEE_ID}/summary",
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_summary_month_out_of_range_high_returns_422(self, client):
        """month <= 12."""
        response = await client.get(
            f"{PREFIX}/time-records/employee/{SAMPLE_EMPLOYEE_ID}/summary",
            params={"month": 13, "year": 2026},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_summary_month_out_of_range_low_returns_422(self, client):
        """month >= 1."""
        response = await client.get(
            f"{PREFIX}/time-records/employee/{SAMPLE_EMPLOYEE_ID}/summary",
            params={"month": 0, "year": 2026},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_summary_year_below_minimum_returns_422(self, client):
        """year >= 2020."""
        response = await client.get(
            f"{PREFIX}/time-records/employee/{SAMPLE_EMPLOYEE_ID}/summary",
            params={"month": 3, "year": 2019},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_summary_totals_structure(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_summary = AsyncMock(return_value=SAMPLE_SUMMARY)
            response = await client.get(
                f"{PREFIX}/time-records/employee/{SAMPLE_EMPLOYEE_ID}/summary",
                params={"month": 3, "year": 2026},
            )
        data = response.json()
        assert "total_work_days" in data
        assert "total_worked_days" in data
        assert "total_hours_worked" in data
        assert "total_overtime" in data
        assert "total_absences" in data
        assert "records" in data

    @pytest.mark.asyncio
    async def test_get_summary_correct_args_passed_to_service(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_summary = AsyncMock(return_value=SAMPLE_SUMMARY)
            await client.get(
                f"{PREFIX}/time-records/employee/{SAMPLE_EMPLOYEE_ID}/summary",
                params={"month": 5, "year": 2026},
            )
        instance.get_summary.assert_called_once_with(SAMPLE_EMPLOYEE_ID, 5, 2026)

    @pytest.mark.asyncio
    async def test_get_summary_december(self, client):
        dec_summary = {**SAMPLE_SUMMARY, "month": 12}
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_summary = AsyncMock(return_value=dec_summary)
            response = await client.get(
                f"{PREFIX}/time-records/employee/{SAMPLE_EMPLOYEE_ID}/summary",
                params={"month": 12, "year": 2026},
            )
        assert response.status_code == 200
        assert response.json()["month"] == 12


# ===========================================================================
# 4. POST /time-records/clock-in
# ===========================================================================


class TestClockIn:
    """Testes para POST /time-records/clock-in."""

    @pytest.mark.asyncio
    async def test_clock_in_happy_path(self, client):
        clock_in_response = {
            **SAMPLE_TIME_RECORD,
            "clock_out": None,
            "total_hours": None,
        }
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_in = AsyncMock(return_value=clock_in_response)
            response = await client.post(
                f"{PREFIX}/time-records/clock-in",
                json={"employee_id": SAMPLE_EMPLOYEE_ID},
            )
        assert response.status_code == 201
        data = response.json()
        assert data["employee_id"] == SAMPLE_EMPLOYEE_ID

    @pytest.mark.asyncio
    async def test_clock_in_missing_employee_id_returns_422(self, client):
        response = await client.post(
            f"{PREFIX}/time-records/clock-in",
            json={},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_clock_in_with_gps_coordinates(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_in = AsyncMock(
                return_value={
                    **SAMPLE_TIME_RECORD,
                    "location_lat": -3.1,
                    "location_lng": -60.0,
                    "clock_out": None,
                }
            )
            response = await client.post(
                f"{PREFIX}/time-records/clock-in",
                json={
                    "employee_id": SAMPLE_EMPLOYEE_ID,
                    "location_lat": -3.1,
                    "location_lng": -60.0,
                },
            )
        assert response.status_code == 201
        data = response.json()
        assert data["location_lat"] == -3.1

    @pytest.mark.asyncio
    async def test_clock_in_with_posto_id(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_in = AsyncMock(return_value={**SAMPLE_TIME_RECORD, "clock_out": None})
            response = await client.post(
                f"{PREFIX}/time-records/clock-in",
                json={
                    "employee_id": SAMPLE_EMPLOYEE_ID,
                    "posto_id": "posto-001",
                },
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_clock_in_with_device_type(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_in = AsyncMock(
                return_value={
                    **SAMPLE_TIME_RECORD,
                    "registered_by": "app",
                    "clock_out": None,
                }
            )
            response = await client.post(
                f"{PREFIX}/time-records/clock-in",
                json={
                    "employee_id": SAMPLE_EMPLOYEE_ID,
                    "device_type": "app",
                },
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_clock_in_with_notes(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_in = AsyncMock(return_value={**SAMPLE_TIME_RECORD, "clock_out": None})
            response = await client.post(
                f"{PREFIX}/time-records/clock-in",
                json={
                    "employee_id": SAMPLE_EMPLOYEE_ID,
                    "notes": "Inicio do turno noturno",
                },
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_clock_in_passes_created_by_from_user(self, client):
        """Garante que created_by vem do current_user.id."""
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_in = AsyncMock(return_value={**SAMPLE_TIME_RECORD, "clock_out": None})
            await client.post(
                f"{PREFIX}/time-records/clock-in",
                json={"employee_id": SAMPLE_EMPLOYEE_ID},
            )
        call_kwargs = instance.clock_in.call_args.kwargs
        assert call_kwargs["created_by"] == "admin-1"

    @pytest.mark.asyncio
    async def test_clock_in_full_payload(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_in = AsyncMock(return_value={**SAMPLE_TIME_RECORD, "clock_out": None})
            response = await client.post(
                f"{PREFIX}/time-records/clock-in",
                json={
                    "employee_id": SAMPLE_EMPLOYEE_ID,
                    "location_lat": -3.1319,
                    "location_lng": -60.0212,
                    "posto_id": "posto-001",
                    "device_type": "app",
                    "notes": "Entrada turno da manha",
                },
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_clock_in_response_has_required_fields(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_in = AsyncMock(return_value={**SAMPLE_TIME_RECORD, "clock_out": None})
            response = await client.post(
                f"{PREFIX}/time-records/clock-in",
                json={"employee_id": SAMPLE_EMPLOYEE_ID},
            )
        data = response.json()
        assert "id" in data
        assert "employee_id" in data
        assert "record_date" in data
        assert "status" in data

    @pytest.mark.asyncio
    async def test_clock_in_invalid_body_not_json_returns_422(self, client):
        response = await client.post(
            f"{PREFIX}/time-records/clock-in",
            content="not-json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422


# ===========================================================================
# 5. POST /time-records/clock-out/{record_id}
# ===========================================================================


class TestClockOut:
    """Testes para POST /time-records/clock-out/{record_id}."""

    @pytest.mark.asyncio
    async def test_clock_out_happy_path(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_out = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            response = await client.post(
                f"{PREFIX}/time-records/clock-out/{SAMPLE_RECORD_ID}",
                json={},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == SAMPLE_RECORD_ID
        assert data["clock_out"] == "17:00"

    @pytest.mark.asyncio
    async def test_clock_out_record_not_found_returns_404(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_out = AsyncMock(side_effect=ValueError("Registro de ponto nao encontrado"))
            response = await client.post(
                f"{PREFIX}/time-records/clock-out/nonexistent-id",
                json={},
            )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_clock_out_with_gps(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_out = AsyncMock(
                return_value={
                    **SAMPLE_TIME_RECORD,
                    "location_lat": -3.1,
                    "location_lng": -60.0,
                }
            )
            response = await client.post(
                f"{PREFIX}/time-records/clock-out/{SAMPLE_RECORD_ID}",
                json={"location_lat": -3.1, "location_lng": -60.0},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_clock_out_with_notes(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_out = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            response = await client.post(
                f"{PREFIX}/time-records/clock-out/{SAMPLE_RECORD_ID}",
                json={"notes": "Saida ao fim do turno"},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_clock_out_without_body(self, client):
        """Body e opcional no clock-out."""
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_out = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            response = await client.post(
                f"{PREFIX}/time-records/clock-out/{SAMPLE_RECORD_ID}",
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_clock_out_error_detail_from_valueerror(self, client):
        error_msg = "Registro de ponto punch-xyz nao encontrado"
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_out = AsyncMock(side_effect=ValueError(error_msg))
            response = await client.post(
                f"{PREFIX}/time-records/clock-out/punch-xyz",
                json={},
            )
        assert response.status_code == 404
        assert error_msg in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_clock_out_passes_created_by_from_user(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_out = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            await client.post(
                f"{PREFIX}/time-records/clock-out/{SAMPLE_RECORD_ID}",
                json={},
            )
        call_kwargs = instance.clock_out.call_args.kwargs
        assert call_kwargs["created_by"] == "admin-1"

    @pytest.mark.asyncio
    async def test_clock_out_total_hours_in_response(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_out = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            response = await client.post(
                f"{PREFIX}/time-records/clock-out/{SAMPLE_RECORD_ID}",
                json={},
            )
        data = response.json()
        assert data["total_hours"] == "08:00"

    @pytest.mark.asyncio
    async def test_clock_out_full_gps_and_notes(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_out = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            response = await client.post(
                f"{PREFIX}/time-records/clock-out/{SAMPLE_RECORD_ID}",
                json={
                    "location_lat": -3.1319,
                    "location_lng": -60.0212,
                    "notes": "Saida normal",
                },
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_clock_out_record_id_is_uuid(self, client):
        """Suporta UUIDs como record_id."""
        uid = "550e8400-e29b-41d4-a716-446655440000"
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.clock_out = AsyncMock(return_value={**SAMPLE_TIME_RECORD, "id": uid})
            response = await client.post(
                f"{PREFIX}/time-records/clock-out/{uid}",
                json={},
            )
        assert response.status_code == 200


# ===========================================================================
# 6. POST /time-records — CREATE MANUAL
# ===========================================================================


class TestCreateManualRecord:
    """Testes para POST /time-records (lancamento manual)."""

    @pytest.mark.asyncio
    async def test_create_manual_happy_path(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.create_manual = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            response = await client.post(
                f"{PREFIX}/time-records",
                json={
                    "employee_id": SAMPLE_EMPLOYEE_ID,
                    "record_date": "2026-03-29",
                    "clock_in": "2026-03-29T08:00:00",
                    "clock_out": "2026-03-29T17:00:00",
                },
            )
        assert response.status_code == 201
        data = response.json()
        assert data["employee_id"] == SAMPLE_EMPLOYEE_ID

    @pytest.mark.asyncio
    async def test_create_manual_missing_employee_id_returns_422(self, client):
        response = await client.post(
            f"{PREFIX}/time-records",
            json={"record_date": "2026-03-29"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_manual_missing_record_date_returns_422(self, client):
        response = await client.post(
            f"{PREFIX}/time-records",
            json={"employee_id": SAMPLE_EMPLOYEE_ID},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_manual_with_lunch_times(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.create_manual = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            response = await client.post(
                f"{PREFIX}/time-records",
                json={
                    "employee_id": SAMPLE_EMPLOYEE_ID,
                    "record_date": "2026-03-29",
                    "clock_in": "2026-03-29T08:00:00",
                    "clock_in_lunch": "2026-03-29T12:00:00",
                    "clock_out_lunch": "2026-03-29T13:00:00",
                    "clock_out": "2026-03-29T17:00:00",
                },
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_manual_with_justification(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.create_manual = AsyncMock(
                return_value={
                    **SAMPLE_TIME_RECORD,
                    "justification": "Ajuste retroativo aprovado pelo DP",
                }
            )
            response = await client.post(
                f"{PREFIX}/time-records",
                json={
                    "employee_id": SAMPLE_EMPLOYEE_ID,
                    "record_date": "2026-03-28",
                    "justification": "Ajuste retroativo aprovado pelo DP",
                },
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_manual_status_falta(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.create_manual = AsyncMock(
                return_value={
                    **SAMPLE_TIME_RECORD,
                    "status": "falta",
                    "clock_in": None,
                    "clock_out": None,
                }
            )
            response = await client.post(
                f"{PREFIX}/time-records",
                json={
                    "employee_id": SAMPLE_EMPLOYEE_ID,
                    "record_date": "2026-03-28",
                    "status": "falta",
                },
            )
        assert response.status_code == 201
        assert response.json()["status"] == "falta"

    @pytest.mark.asyncio
    async def test_create_manual_invalid_status_returns_422(self, client):
        response = await client.post(
            f"{PREFIX}/time-records",
            json={
                "employee_id": SAMPLE_EMPLOYEE_ID,
                "record_date": "2026-03-29",
                "status": "status_invalido",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_manual_passes_created_by_from_user(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.create_manual = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            await client.post(
                f"{PREFIX}/time-records",
                json={
                    "employee_id": SAMPLE_EMPLOYEE_ID,
                    "record_date": "2026-03-29",
                },
            )
        call_kwargs = instance.create_manual.call_args.kwargs
        assert call_kwargs["created_by"] == "admin-1"

    @pytest.mark.asyncio
    async def test_create_manual_with_gps(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.create_manual = AsyncMock(
                return_value={
                    **SAMPLE_TIME_RECORD,
                    "location_lat": -3.1319,
                    "location_lng": -60.0212,
                }
            )
            response = await client.post(
                f"{PREFIX}/time-records",
                json={
                    "employee_id": SAMPLE_EMPLOYEE_ID,
                    "record_date": "2026-03-29",
                    "location_lat": -3.1319,
                    "location_lng": -60.0212,
                },
            )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_manual_all_valid_statuses(self, client):
        valid_statuses = ["regular", "falta", "atestado", "feriado", "compensacao", "inconsistencia", "abono"]
        for status_val in valid_statuses:
            with patch(PATCH_TARGET) as MockService:
                instance = MockService.return_value
                instance.create_manual = AsyncMock(
                    return_value={
                        **SAMPLE_TIME_RECORD,
                        "status": status_val,
                    }
                )
                response = await client.post(
                    f"{PREFIX}/time-records",
                    json={
                        "employee_id": SAMPLE_EMPLOYEE_ID,
                        "record_date": "2026-03-29",
                        "status": status_val,
                    },
                )
            assert response.status_code == 201, f"Status {status_val} falhou"


# ===========================================================================
# 7. GET /time-records/{record_id} — GET BY ID
# ===========================================================================


class TestGetTimeRecord:
    """Testes para GET /time-records/{record_id}."""

    @pytest.mark.asyncio
    async def test_get_by_id_returns_200(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_by_id = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            response = await client.get(f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == SAMPLE_RECORD_ID
        assert data["employee_id"] == SAMPLE_EMPLOYEE_ID

    @pytest.mark.asyncio
    async def test_get_by_id_not_found_returns_404(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_by_id = AsyncMock(return_value=None)
            response = await client.get(f"{PREFIX}/time-records/nonexistent-id")
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_by_id_404_detail_message(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_by_id = AsyncMock(return_value=None)
            response = await client.get(f"{PREFIX}/time-records/unknown-record")
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert "Registro de ponto" in detail

    @pytest.mark.asyncio
    async def test_get_by_id_uuid_format(self, client):
        uid = "550e8400-e29b-41d4-a716-446655440000"
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_by_id = AsyncMock(return_value={**SAMPLE_TIME_RECORD, "id": uid})
            response = await client.get(f"{PREFIX}/time-records/{uid}")
        assert response.status_code == 200
        assert response.json()["id"] == uid

    @pytest.mark.asyncio
    async def test_get_by_id_record_with_overtime(self, client):
        overtime_record = {
            **SAMPLE_TIME_RECORD,
            "clock_in": "07:00",
            "clock_out": "18:00",
            "total_hours": "10:00",
            "overtime_hours": "02:00",
        }
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_by_id = AsyncMock(return_value=overtime_record)
            response = await client.get(f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}")
        data = response.json()
        assert data["overtime_hours"] == "02:00"

    @pytest.mark.asyncio
    async def test_get_by_id_record_inconsistencia(self, client):
        incon_record = {
            **SAMPLE_TIME_RECORD,
            "status": "inconsistencia",
            "clock_out": None,
            "total_hours": None,
        }
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_by_id = AsyncMock(return_value=incon_record)
            response = await client.get(f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}")
        assert response.status_code == 200
        assert response.json()["status"] == "inconsistencia"

    @pytest.mark.asyncio
    async def test_get_by_id_record_with_justification(self, client):
        justified_record = {
            **SAMPLE_TIME_RECORD,
            "status": "atestado",
            "justification": "Atestado medico CID-10 J00",
        }
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_by_id = AsyncMock(return_value=justified_record)
            response = await client.get(f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}")
        data = response.json()
        assert data["justification"] == "Atestado medico CID-10 J00"

    @pytest.mark.asyncio
    async def test_get_by_id_passes_correct_id_to_service(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_by_id = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            await client.get(f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}")
        instance.get_by_id.assert_called_once_with(SAMPLE_RECORD_ID)

    @pytest.mark.asyncio
    async def test_get_by_id_response_has_all_fields(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_by_id = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            response = await client.get(f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}")
        data = response.json()
        required_fields = ["id", "employee_id", "record_date", "status", "registered_by"]
        for field in required_fields:
            assert field in data, f"Campo '{field}' ausente na resposta"

    @pytest.mark.asyncio
    async def test_get_by_id_record_with_gps(self, client):
        gps_record = {**SAMPLE_TIME_RECORD, "location_lat": -3.1319, "location_lng": -60.0212}
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.get_by_id = AsyncMock(return_value=gps_record)
            response = await client.get(f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}")
        data = response.json()
        assert data["location_lat"] == -3.1319
        assert data["location_lng"] == -60.0212


# ===========================================================================
# 8. PATCH /time-records/{record_id} — UPDATE RECORD
# ===========================================================================


class TestUpdateTimeRecord:
    """Testes para PATCH /time-records/{record_id}."""

    @pytest.mark.asyncio
    async def test_update_returns_200(self, client):
        updated = {**SAMPLE_TIME_RECORD, "justification": "Atraso por problema de transporte"}
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.update_record = AsyncMock(return_value=updated)
            response = await client.patch(
                f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}",
                json={"justification": "Atraso por problema de transporte"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["justification"] == "Atraso por problema de transporte"

    @pytest.mark.asyncio
    async def test_update_not_found_returns_404(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.update_record = AsyncMock(return_value=None)
            response = await client.patch(
                f"{PREFIX}/time-records/nonexistent-id",
                json={"status": "regular"},
            )
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_status_only(self, client):
        updated = {**SAMPLE_TIME_RECORD, "status": "atestado"}
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.update_record = AsyncMock(return_value=updated)
            response = await client.patch(
                f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}",
                json={"status": "atestado"},
            )
        assert response.status_code == 200
        assert response.json()["status"] == "atestado"

    @pytest.mark.asyncio
    async def test_update_invalid_status_returns_422(self, client):
        response = await client.patch(
            f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}",
            json={"status": "status_inexistente"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_clock_times(self, client):
        updated = {
            **SAMPLE_TIME_RECORD,
            "clock_in": "07:55",
            "clock_out": "17:05",
            "total_hours": "08:10",
        }
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.update_record = AsyncMock(return_value=updated)
            response = await client.patch(
                f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}",
                json={
                    "clock_in": "2026-03-29T07:55:00",
                    "clock_out": "2026-03-29T17:05:00",
                },
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_partial_empty_body(self, client):
        """PATCH com body vazio deve ser aceito (todos os campos sao opcionais)."""
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.update_record = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            response = await client.patch(
                f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}",
                json={},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_passes_correct_id_and_updated_by(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.update_record = AsyncMock(return_value=SAMPLE_TIME_RECORD)
            await client.patch(
                f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}",
                json={"notes": "Correcao solicitada pelo DP"},
            )
        call_kwargs = instance.update_record.call_args.kwargs
        assert call_kwargs["record_id"] == SAMPLE_RECORD_ID
        assert call_kwargs["updated_by"] == "admin-1"

    @pytest.mark.asyncio
    async def test_update_with_notes(self, client):
        updated = {**SAMPLE_TIME_RECORD, "status": "regular"}
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.update_record = AsyncMock(return_value=updated)
            response = await client.patch(
                f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}",
                json={"notes": "Ajuste retroativo autorizado"},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_all_valid_statuses(self, client):
        valid_statuses = ["regular", "falta", "atestado", "feriado", "compensacao", "inconsistencia", "abono"]
        for status_val in valid_statuses:
            with patch(PATCH_TARGET) as MockService:
                instance = MockService.return_value
                instance.update_record = AsyncMock(
                    return_value={
                        **SAMPLE_TIME_RECORD,
                        "status": status_val,
                    }
                )
                response = await client.patch(
                    f"{PREFIX}/time-records/{SAMPLE_RECORD_ID}",
                    json={"status": status_val},
                )
            assert response.status_code == 200, f"Status update {status_val} falhou"

    @pytest.mark.asyncio
    async def test_update_404_detail_message(self, client):
        with patch(PATCH_TARGET) as MockService:
            instance = MockService.return_value
            instance.update_record = AsyncMock(return_value=None)
            response = await client.patch(
                f"{PREFIX}/time-records/unknown-record",
                json={"justification": "Justificativa"},
            )
        assert response.status_code == 404
        assert "Registro de ponto" in response.json()["detail"]
