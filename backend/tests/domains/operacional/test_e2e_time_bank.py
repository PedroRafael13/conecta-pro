"""
Testes E2E para o módulo Time Bank (Banco de Horas) — Operacional.

Cobre os 15 endpoints do time_bank_controller com:
- Happy path (200/201)
- Validação 422
- 404 not found
- Casos de negócio (saldo insuficiente, entrada já aprovada, etc.)
- Fluxos completos (criação → aprovação, criação → rejeição, compensação)
"""

import sys
from datetime import date, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "/opt/conecta-pro/backend")

from core.auth.dependencies import get_current_active_user, get_current_user_id
from core.database import get_db
from modules.operacional.controllers.time_bank_controller import router as time_bank_router

# ===========================================================================
# HELPERS
# ===========================================================================

EMPLOYEE_ID = str(uuid4())
ENTRY_ID = str(uuid4())
USER_ID = str(uuid4())
TODAY = date.today().isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()
EXPIRATION = (date.today() + timedelta(days=180)).isoformat()
NOW = datetime.utcnow()


def _make_entry(
    entry_id: str = ENTRY_ID,
    employee_id: str = EMPLOYEE_ID,
    entry_type: str = "credit",
    status: str = "pending",
    hours: float = 8.0,
    expiration_date: date | None = None,
) -> MagicMock:
    """Cria um objeto TimeBank fake com todas as propriedades necessárias."""
    entry = MagicMock()
    entry.id = entry_id
    entry.employee_id = employee_id
    entry.entry_type = entry_type
    entry.status = status
    entry.hours = hours
    entry.balance_before = 0.0
    entry.balance_after = hours if entry_type == "credit" else -hours
    entry.reference_date = date.today()
    entry.expiration_date = expiration_date or (date.today() + timedelta(days=180))
    entry.shift_id = None
    entry.post_id = None
    entry.description = "Teste"
    entry.reason = "Hora extra turno"
    entry.approved_by = None
    entry.approved_at = None
    entry.rejection_reason = None
    entry.compensated_at = None
    entry.compensation_shift_id = None
    entry.is_active = True
    entry.created_at = NOW
    entry.updated_at = NOW
    # Propriedades calculadas
    entry.is_credit = entry_type == "credit"
    entry.is_debit = entry_type == "debit"
    entry.is_expired = False
    entry.is_pending = status == "pending"
    entry.signed_hours = hours if entry_type == "credit" else -hours
    entry.days_until_expiration = 180
    return entry


def _make_summary(
    employee_id: str = EMPLOYEE_ID,
    current_balance: float = 20.0,
    expiring_soon: float = 0.0,
):
    """Cria um TimeBankSummary fake."""
    summary = MagicMock()
    summary.employee_id = employee_id
    summary.total_credit = 24.0
    summary.total_debit = 4.0
    summary.total_compensated = 0.0
    summary.total_expired = 0.0
    summary.current_balance = current_balance
    summary.pending_approval = 0.0
    summary.expiring_soon = expiring_soon
    summary.entries_count = 3
    return summary


def _make_stats():
    """Cria um TimeBankStats fake."""
    stats = MagicMock()
    stats.total_employees = 10
    stats.total_credit_hours = 80.0
    stats.total_debit_hours = 20.0
    stats.total_compensated_hours = 5.0
    stats.total_expired_hours = 0.0
    stats.total_pending_hours = 8.0
    stats.avg_balance = 5.5
    stats.by_status = {"pending": 2, "approved": 8}
    stats.by_entry_type = {"credit": 80.0, "debit": 20.0}
    return stats


# ===========================================================================
# FAKE DB SESSION
# ===========================================================================


class FakeDB:
    """AsyncSession fake — todas as operações são no-ops."""

    async def execute(self, *args, **kwargs):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        result.scalar.return_value = 0
        result.scalars.return_value = MagicMock(all=lambda: [])
        return result

    async def commit(self):
        pass

    async def rollback(self):
        pass

    async def refresh(self, obj):
        pass

    def add(self, obj):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


async def get_fake_db():
    yield FakeDB()


# ===========================================================================
# FAKE USER (role=admin para ter todas as permissões)
# ===========================================================================


def _make_user():
    user = MagicMock()
    user.id = USER_ID
    user.email = "admin@test.com"
    user.role = "admin"
    user.is_active = True
    return user


async def fake_get_current_user_id():
    return USER_ID


async def fake_get_current_active_user():
    return _make_user()


# ===========================================================================
# APP FIXTURE
# ===========================================================================


@pytest.fixture
def app():
    application = FastAPI()
    application.include_router(time_bank_router, prefix="/api/v1")
    application.dependency_overrides[get_db] = get_fake_db
    application.dependency_overrides[get_current_user_id] = fake_get_current_user_id
    application.dependency_overrides[get_current_active_user] = fake_get_current_active_user
    return application


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


REPO_PATH = "modules.operacional.controllers.time_bank_controller.TimeBankRepository"


# ===========================================================================
# 1. POST /time-bank/ — criar entrada
# ===========================================================================


class TestCreateEntry:
    """Testes para POST /time-bank/"""

    @pytest.mark.asyncio
    async def test_create_entry_happy_path(self, client, app):
        """201 — cria entrada com dados válidos."""
        entry = _make_entry()

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.create = AsyncMock(return_value=entry)

            app.dependency_overrides[get_db] = get_fake_db

            response = await client.post(
                "/api/v1/time-bank/",
                json={
                    "employee_id": EMPLOYEE_ID,
                    "entry_type": "credit",
                    "hours": 8.0,
                    "reference_date": TODAY,
                    "description": "Hora extra plantão",
                },
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["employee_id"] == EMPLOYEE_ID
        assert data["entry_type"] == "credit"
        assert data["hours"] == 8.0

    @pytest.mark.asyncio
    async def test_create_entry_with_all_fields(self, client, app):
        """201 — cria entrada com todos os campos opcionais."""
        entry = _make_entry()
        shift_id = str(uuid4())
        post_id = str(uuid4())
        entry.shift_id = shift_id
        entry.post_id = post_id

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.create = AsyncMock(return_value=entry)

            response = await client.post(
                "/api/v1/time-bank/",
                json={
                    "employee_id": EMPLOYEE_ID,
                    "entry_type": "credit",
                    "hours": 4.0,
                    "reference_date": TODAY,
                    "description": "Descricao completa",
                    "reason": "Motivo X",
                    "shift_id": shift_id,
                    "post_id": post_id,
                    "expiration_date": EXPIRATION,
                },
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_entry_missing_required_fields_422(self, client, app):
        """422 — faltam campos obrigatórios."""
        response = await client.post(
            "/api/v1/time-bank/",
            json={"hours": 8.0},
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_entry_zero_hours_422(self, client, app):
        """422 — horas zero não são permitidas."""
        response = await client.post(
            "/api/v1/time-bank/",
            json={
                "employee_id": EMPLOYEE_ID,
                "entry_type": "credit",
                "hours": 0,
                "reference_date": TODAY,
            },
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_entry_invalid_type_422(self, client, app):
        """422 — tipo de entrada inválido."""
        response = await client.post(
            "/api/v1/time-bank/",
            json={
                "employee_id": EMPLOYEE_ID,
                "entry_type": "invalido",
                "hours": 8.0,
                "reference_date": TODAY,
            },
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_entry_debit_type(self, client, app):
        """201 — cria entrada do tipo débito."""
        entry = _make_entry(entry_type="debit")

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.create = AsyncMock(return_value=entry)

            response = await client.post(
                "/api/v1/time-bank/",
                json={
                    "employee_id": EMPLOYEE_ID,
                    "entry_type": "debit",
                    "hours": 2.0,
                    "reference_date": TODAY,
                },
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 201
        assert response.json()["entry_type"] == "debit"


# ===========================================================================
# 2. GET /time-bank/ — listar com filtros e paginação
# ===========================================================================


class TestListEntries:
    """Testes para GET /time-bank/"""

    @pytest.mark.asyncio
    async def test_list_entries_empty(self, client, app):
        """200 — lista vazia."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([], 0))

            response = await client.get(
                "/api/v1/time-bank/",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20

    @pytest.mark.asyncio
    async def test_list_entries_with_results(self, client, app):
        """200 — retorna lista de entradas."""
        entry1 = _make_entry(entry_id=str(uuid4()))
        entry2 = _make_entry(entry_id=str(uuid4()))

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([entry1, entry2], 2))

            response = await client.get(
                "/api/v1/time-bank/",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2
        assert data["total_pages"] == 1

    @pytest.mark.asyncio
    async def test_list_entries_pagination(self, client, app):
        """200 — paginação funciona corretamente."""
        entry = _make_entry()

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([entry], 50))

            response = await client.get(
                "/api/v1/time-bank/?page=2&page_size=10",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total"] == 50
        assert data["total_pages"] == 5

    @pytest.mark.asyncio
    async def test_list_entries_with_employee_filter(self, client, app):
        """200 — filtro por employee_id."""
        entry = _make_entry()

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([entry], 1))

            response = await client.get(
                f"/api/v1/time-bank/?employee_id={EMPLOYEE_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        assert len(response.json()["items"]) == 1

    @pytest.mark.asyncio
    async def test_list_entries_invalid_page_422(self, client, app):
        """422 — page deve ser >= 1."""
        response = await client.get(
            "/api/v1/time-bank/?page=0",
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_entries_page_size_too_large_422(self, client, app):
        """422 — page_size máximo é 100."""
        response = await client.get(
            "/api/v1/time-bank/?page_size=101",
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_entries_with_status_filter(self, client, app):
        """200 — filtro por status."""
        entry = _make_entry(status="approved")

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([entry], 1))

            response = await client.get(
                "/api/v1/time-bank/?status=approved",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200


# ===========================================================================
# 3. GET /time-bank/pending — entradas pendentes
# ===========================================================================


class TestGetPendingEntries:
    """Testes para GET /time-bank/pending"""

    @pytest.mark.asyncio
    async def test_get_pending_entries(self, client, app):
        """200 — lista entradas pendentes."""
        entry = _make_entry(status="pending")

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([entry], 1))

            response = await client.get(
                "/api/v1/time-bank/pending",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_pending_entries_empty(self, client, app):
        """200 — nenhuma pendente."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([], 0))

            response = await client.get(
                "/api/v1/time-bank/pending",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_pending_entries_with_employee_filter(self, client, app):
        """200 — filtro por funcionário."""
        entry = _make_entry(status="pending")

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([entry], 1))

            response = await client.get(
                f"/api/v1/time-bank/pending?employee_id={EMPLOYEE_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        assert len(response.json()) == 1


# ===========================================================================
# 4. GET /time-bank/expiring — entradas expirando
# ===========================================================================


class TestGetExpiringEntries:
    """Testes para GET /time-bank/expiring"""

    @pytest.mark.asyncio
    async def test_get_expiring_entries_none(self, client, app):
        """200 — sem entradas expirando em breve."""
        # Entrada com expiração em 60 dias (fora do filtro padrão de 30 dias)
        entry = _make_entry(
            status="approved",
            expiration_date=date.today() + timedelta(days=60),
        )

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([entry], 1))

            response = await client.get(
                "/api/v1/time-bank/expiring",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        # Entrada com 60 dias de expiração NÃO deve aparecer com days=30
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_expiring_entries_has_results(self, client, app):
        """200 — retorna entradas expirando dentro do prazo."""
        entry = _make_entry(
            status="approved",
            expiration_date=date.today() + timedelta(days=10),
        )

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([entry], 1))

            response = await client.get(
                "/api/v1/time-bank/expiring?days=30",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_get_expiring_entries_invalid_days_422(self, client, app):
        """422 — days deve ser entre 1 e 90."""
        response = await client.get(
            "/api/v1/time-bank/expiring?days=0",
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_expiring_entries_days_too_large_422(self, client, app):
        """422 — days máximo é 90."""
        response = await client.get(
            "/api/v1/time-bank/expiring?days=91",
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422


# ===========================================================================
# 5. GET /time-bank/summary/{employee_id} — resumo do funcionário
# ===========================================================================


class TestGetEmployeeSummary:
    """Testes para GET /time-bank/summary/{employee_id}"""

    @pytest.mark.asyncio
    async def test_get_summary_happy_path(self, client, app):
        """200 — retorna resumo do funcionário."""
        summary = _make_summary()

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_summary = AsyncMock(return_value=summary)

            response = await client.get(
                f"/api/v1/time-bank/summary/{EMPLOYEE_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == EMPLOYEE_ID
        assert data["current_balance"] == 20.0

    @pytest.mark.asyncio
    async def test_get_summary_not_found_404(self, client, app):
        """404 — funcionário sem entradas."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_summary = AsyncMock(return_value=None)

            response = await client.get(
                f"/api/v1/time-bank/summary/{EMPLOYEE_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"].lower()


# ===========================================================================
# 6. GET /time-bank/stats — estatísticas gerais
# ===========================================================================


class TestGetStats:
    """Testes para GET /time-bank/stats"""

    @pytest.mark.asyncio
    async def test_get_stats_happy_path(self, client, app):
        """200 — retorna estatísticas."""
        stats = _make_stats()

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_stats = AsyncMock(return_value=stats)

            # Cache deve ser ignorado/contornado
            with (
                patch("core.cache.cache_get", return_value=None),
                patch("core.cache.cache_set", return_value=True),
            ):
                response = await client.get(
                    "/api/v1/time-bank/stats",
                    headers={"Authorization": "Bearer fake-token"},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["total_employees"] == 10
        assert data["total_credit_hours"] == 80.0

    @pytest.mark.asyncio
    async def test_get_stats_cache_miss_calls_repo(self, client, app):
        """200 — cache miss executa query ao repositório."""
        stats = _make_stats()

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_stats = AsyncMock(return_value=stats)

            with (
                patch("core.cache.cache_get", return_value=None),
                patch("core.cache.cache_set", return_value=True),
            ):
                response = await client.get(
                    "/api/v1/time-bank/stats",
                    headers={"Authorization": "Bearer fake-token"},
                )

        assert response.status_code == 200
        instance.get_stats.assert_called_once()


# ===========================================================================
# 7. GET /time-bank/alerts — alertas de expiração
# ===========================================================================


class TestGetExpirationAlerts:
    """Testes para GET /time-bank/alerts"""

    @pytest.mark.asyncio
    async def test_get_alerts_no_expiring(self, client, app):
        """200 — sem alertas quando não há entradas expirando."""
        entry = _make_entry(
            status="approved",
            expiration_date=date.today() + timedelta(days=90),
        )

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([entry], 1))

            response = await client.get(
                "/api/v1/time-bank/alerts",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_alerts_expired_entry(self, client, app):
        """200 — retorna alerta crítico para entrada já expirada."""
        entry = _make_entry(
            status="approved",
            expiration_date=date.today() - timedelta(days=5),
        )
        entry.expiration_date = date.today() - timedelta(days=5)

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([entry], 1))

            response = await client.get(
                "/api/v1/time-bank/alerts",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        alerts = response.json()
        # Deve ter pelo menos um alerta crítico
        assert len(alerts) >= 1
        statuses = [a["status"] for a in alerts]
        assert "expired" in statuses

    @pytest.mark.asyncio
    async def test_get_alerts_expiring_soon(self, client, app):
        """200 — retorna alerta de aviso para entrada expirando em breve."""
        entry = _make_entry(
            status="approved",
            expiration_date=date.today() + timedelta(days=15),
        )
        entry.expiration_date = date.today() + timedelta(days=15)

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([entry], 1))

            response = await client.get(
                "/api/v1/time-bank/alerts",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        alerts = response.json()
        assert len(alerts) >= 1
        statuses = [a["status"] for a in alerts]
        assert "expiring_soon" in statuses

    @pytest.mark.asyncio
    async def test_get_alerts_empty_list(self, client, app):
        """200 — sem entradas = sem alertas."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([], 0))

            response = await client.get(
                "/api/v1/time-bank/alerts",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        assert response.json() == []


# ===========================================================================
# 8. GET /time-bank/{entry_id} — busca por ID
# ===========================================================================


class TestGetEntry:
    """Testes para GET /time-bank/{entry_id}"""

    @pytest.mark.asyncio
    async def test_get_entry_happy_path(self, client, app):
        """200 — retorna entrada existente."""
        entry = _make_entry()

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=entry)

            response = await client.get(
                f"/api/v1/time-bank/{ENTRY_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ENTRY_ID
        assert data["employee_id"] == EMPLOYEE_ID

    @pytest.mark.asyncio
    async def test_get_entry_not_found_404(self, client, app):
        """404 — entrada não existe."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_by_id = AsyncMock(return_value=None)

            response = await client.get(
                f"/api/v1/time-bank/{ENTRY_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"].lower()


# ===========================================================================
# 9. PATCH /time-bank/{entry_id} — atualizar entrada
# ===========================================================================


class TestUpdateEntry:
    """Testes para PATCH /time-bank/{entry_id}"""

    @pytest.mark.asyncio
    async def test_update_entry_happy_path(self, client, app):
        """200 — atualiza entrada pendente."""
        entry = _make_entry()
        entry.hours = 6.0

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.update = AsyncMock(return_value=entry)

            response = await client.patch(
                f"/api/v1/time-bank/{ENTRY_ID}",
                json={"hours": 6.0, "description": "Atualizado"},
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_entry_not_found_404(self, client, app):
        """404 — entrada não encontrada ou já processada."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.update = AsyncMock(return_value=None)

            response = await client.patch(
                f"/api/v1/time-bank/{ENTRY_ID}",
                json={"hours": 6.0},
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_entry_partial_fields(self, client, app):
        """200 — atualização parcial funciona."""
        entry = _make_entry()
        entry.description = "Nova descricao"

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.update = AsyncMock(return_value=entry)

            response = await client.patch(
                f"/api/v1/time-bank/{ENTRY_ID}",
                json={"description": "Nova descricao"},
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200


# ===========================================================================
# 10. POST /time-bank/{entry_id}/approve — aprovar
# ===========================================================================


class TestApproveEntry:
    """Testes para POST /time-bank/{entry_id}/approve"""

    @pytest.mark.asyncio
    async def test_approve_entry_happy_path(self, client, app):
        """200 — aprova entrada pendente."""
        entry = _make_entry(status="approved")
        entry.approved_by = USER_ID
        entry.approved_at = NOW

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.approve = AsyncMock(return_value=entry)

            response = await client.post(
                f"/api/v1/time-bank/{ENTRY_ID}/approve",
                json={"notes": "Aprovado pelo supervisor"},
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"

    @pytest.mark.asyncio
    async def test_approve_entry_without_notes(self, client, app):
        """200 — aprova sem notas (campo opcional)."""
        entry = _make_entry(status="approved")

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.approve = AsyncMock(return_value=entry)

            response = await client.post(
                f"/api/v1/time-bank/{ENTRY_ID}/approve",
                json={},
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_approve_entry_not_found_404(self, client, app):
        """404 — entrada não encontrada ou já processada."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.approve = AsyncMock(return_value=None)

            response = await client.post(
                f"/api/v1/time-bank/{ENTRY_ID}/approve",
                json={},
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_approve_already_approved_returns_404(self, client, app):
        """404 — repositório retorna None para entrada já aprovada."""
        # O repositório retorna None quando status != PENDING

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.approve = AsyncMock(return_value=None)

            response = await client.post(
                f"/api/v1/time-bank/{ENTRY_ID}/approve",
                json={"notes": "Tentativa dupla"},
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 404


# ===========================================================================
# 11. POST /time-bank/{entry_id}/reject — rejeitar
# ===========================================================================


class TestRejectEntry:
    """Testes para POST /time-bank/{entry_id}/reject"""

    @pytest.mark.asyncio
    async def test_reject_entry_happy_path(self, client, app):
        """200 — rejeita entrada com motivo."""
        entry = _make_entry(status="rejected")
        entry.rejection_reason = "Documentacao insuficiente"

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.reject = AsyncMock(return_value=entry)

            response = await client.post(
                f"/api/v1/time-bank/{ENTRY_ID}/reject",
                json={"rejection_reason": "Documentacao insuficiente"},
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"

    @pytest.mark.asyncio
    async def test_reject_entry_missing_reason_422(self, client, app):
        """422 — motivo de rejeição é obrigatório."""
        response = await client.post(
            f"/api/v1/time-bank/{ENTRY_ID}/reject",
            json={},
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_reject_entry_not_found_404(self, client, app):
        """404 — entrada não encontrada."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.reject = AsyncMock(return_value=None)

            response = await client.post(
                f"/api/v1/time-bank/{ENTRY_ID}/reject",
                json={"rejection_reason": "Entrada invalida"},
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_reject_reason_too_long_422(self, client, app):
        """422 — motivo de rejeição maior que 255 caracteres."""
        response = await client.post(
            f"/api/v1/time-bank/{ENTRY_ID}/reject",
            json={"rejection_reason": "x" * 256},
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422


# ===========================================================================
# 12. POST /time-bank/compensate/{employee_id} — compensar horas
# ===========================================================================


class TestCompensateHours:
    """Testes para POST /time-bank/compensate/{employee_id}"""

    @pytest.mark.asyncio
    async def test_compensate_hours_happy_path(self, client, app):
        """200 — compensação válida com saldo suficiente."""
        entry = _make_entry(entry_type="compensation", status="approved")
        summary = _make_summary(current_balance=20.0)

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_summary = AsyncMock(return_value=summary)
            instance.compensate = AsyncMock(return_value=entry)

            response = await client.post(
                f"/api/v1/time-bank/compensate/{EMPLOYEE_ID}",
                json={
                    "hours": 8.0,
                    "compensation_date": TOMORROW,
                    "notes": "Folga compensatoria",
                },
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_compensate_insufficient_balance_400(self, client, app):
        """400 — saldo insuficiente."""
        summary = _make_summary(current_balance=4.0)  # Tem apenas 4h

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_summary = AsyncMock(return_value=summary)

            response = await client.post(
                f"/api/v1/time-bank/compensate/{EMPLOYEE_ID}",
                json={
                    "hours": 8.0,  # Pede 8h mas tem apenas 4h
                    "compensation_date": TOMORROW,
                },
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 400
        assert "saldo insuficiente" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_compensate_past_date_400(self, client, app):
        """400 — data de compensação no passado."""
        summary = _make_summary(current_balance=20.0)
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_summary = AsyncMock(return_value=summary)

            response = await client.post(
                f"/api/v1/time-bank/compensate/{EMPLOYEE_ID}",
                json={
                    "hours": 8.0,
                    "compensation_date": yesterday,
                },
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 400
        assert "passado" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_compensate_employee_not_found_404(self, client, app):
        """404 — funcionário não encontrado."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_summary = AsyncMock(return_value=None)

            response = await client.post(
                f"/api/v1/time-bank/compensate/{EMPLOYEE_ID}",
                json={
                    "hours": 8.0,
                    "compensation_date": TOMORROW,
                },
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_compensate_missing_fields_422(self, client, app):
        """422 — campos obrigatórios ausentes."""
        response = await client.post(
            f"/api/v1/time-bank/compensate/{EMPLOYEE_ID}",
            json={"hours": 4.0},  # falta compensation_date
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_compensate_zero_hours_422(self, client, app):
        """422 — horas devem ser > 0."""
        response = await client.post(
            f"/api/v1/time-bank/compensate/{EMPLOYEE_ID}",
            json={"hours": 0, "compensation_date": TOMORROW},
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422


# ===========================================================================
# 13. GET /time-bank/monthly-summary/{employee_id} — resumo mensal
# ===========================================================================


class TestGetMonthlySummary:
    """Testes para GET /time-bank/monthly-summary/{employee_id}"""

    @pytest.mark.asyncio
    async def test_get_monthly_summary_happy_path(self, client, app):
        """200 — retorna resumo mensal."""
        entry = _make_entry()
        entry.entry_type = "credit"
        entry.reference_date = date(2026, 3, 15)

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([entry], 1))

            response = await client.get(
                f"/api/v1/time-bank/monthly-summary/{EMPLOYEE_ID}?month=3&year=2026",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["month"] == 3
        assert data["year"] == 2026
        assert "entries_count" in data
        assert "total_credits" in data
        assert "net_balance" in data

    @pytest.mark.asyncio
    async def test_get_monthly_summary_empty(self, client, app):
        """200 — retorna resumo zerado para mês sem entradas."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([], 0))

            response = await client.get(
                f"/api/v1/time-bank/monthly-summary/{EMPLOYEE_ID}?month=1&year=2026",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["entries_count"] == 0
        assert data["total_credits"] == 0.0

    @pytest.mark.asyncio
    async def test_get_monthly_summary_missing_month_422(self, client, app):
        """422 — parâmetro month é obrigatório."""
        response = await client.get(
            f"/api/v1/time-bank/monthly-summary/{EMPLOYEE_ID}?year=2026",
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_monthly_summary_invalid_month_422(self, client, app):
        """422 — mês deve ser entre 1 e 12."""
        response = await client.get(
            f"/api/v1/time-bank/monthly-summary/{EMPLOYEE_ID}?month=13&year=2026",
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_monthly_summary_invalid_year_422(self, client, app):
        """422 — ano deve estar no range válido."""
        response = await client.get(
            f"/api/v1/time-bank/monthly-summary/{EMPLOYEE_ID}?month=3&year=2019",
            headers={"Authorization": "Bearer fake-token"},
        )
        assert response.status_code == 422


# ===========================================================================
# 14. GET /time-bank/recommendations/{employee_id} — recomendações
# ===========================================================================


class TestGetRecommendations:
    """Testes para GET /time-bank/recommendations/{employee_id}"""

    @pytest.mark.asyncio
    async def test_get_recommendations_high_balance(self, client, app):
        """200 — retorna recomendação para saldo alto."""
        summary = _make_summary(current_balance=50.0)  # > 40 horas

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_summary = AsyncMock(return_value=summary)

            response = await client.get(
                f"/api/v1/time-bank/recommendations/{EMPLOYEE_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Saldo alto (>40h) deve gerar recomendação
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_get_recommendations_expiring_hours(self, client, app):
        """200 — retorna recomendação de compensação para horas expirando."""
        summary = _make_summary(current_balance=10.0, expiring_soon=5.0)

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_summary = AsyncMock(return_value=summary)

            response = await client.get(
                f"/api/v1/time-bank/recommendations/{EMPLOYEE_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        data = response.json()
        # Deve recomendar compensar horas que expiram
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_get_recommendations_no_entries_returns_empty(self, client, app):
        """200 — retorna lista vazia quando não há entradas."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_summary = AsyncMock(return_value=None)

            response = await client.get(
                f"/api/v1/time-bank/recommendations/{EMPLOYEE_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_recommendations_balanced_employee(self, client, app):
        """200 — nenhuma recomendação para funcionário com saldo equilibrado."""
        summary = _make_summary(current_balance=5.0, expiring_soon=0.0)

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_summary = AsyncMock(return_value=summary)

            response = await client.get(
                f"/api/v1/time-bank/recommendations/{EMPLOYEE_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ===========================================================================
# 15. DELETE /time-bank/{entry_id} — soft delete
# ===========================================================================


class TestDeleteEntry:
    """Testes para DELETE /time-bank/{entry_id}"""

    @pytest.mark.asyncio
    async def test_delete_entry_happy_path(self, client, app):
        """204 — deleta entrada pendente com sucesso."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.delete = AsyncMock(return_value=True)

            response = await client.delete(
                f"/api/v1/time-bank/{ENTRY_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_entry_not_found_404(self, client, app):
        """404 — entrada não encontrada ou não pode ser deletada."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.delete = AsyncMock(return_value=False)

            response = await client.delete(
                f"/api/v1/time-bank/{ENTRY_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_returns_no_body(self, client, app):
        """204 — body vazio após deleção."""

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.delete = AsyncMock(return_value=True)

            response = await client.delete(
                f"/api/v1/time-bank/{ENTRY_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )

        assert response.status_code == 204
        assert response.content == b""


# ===========================================================================
# FLUXOS DE NEGÓCIO COMPLETOS
# ===========================================================================


class TestBusinessFlows:
    """Fluxos E2E completos de negócio."""

    @pytest.mark.asyncio
    async def test_full_approval_flow(self, client, app):
        """
        Fluxo completo: criar → verificar pendente → aprovar.
        Verifica que status muda de pending para approved.
        """
        entry_pending = _make_entry(status="pending")
        entry_approved = _make_entry(status="approved")
        entry_approved.approved_by = USER_ID
        entry_approved.approved_at = NOW

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.create = AsyncMock(return_value=entry_pending)
            instance.list = AsyncMock(return_value=([entry_pending], 1))
            instance.approve = AsyncMock(return_value=entry_approved)

            # 1. Criar entrada
            resp_create = await client.post(
                "/api/v1/time-bank/",
                json={
                    "employee_id": EMPLOYEE_ID,
                    "entry_type": "credit",
                    "hours": 8.0,
                    "reference_date": TODAY,
                },
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp_create.status_code == 201
            assert resp_create.json()["status"] == "pending"

            # 2. Verificar que aparece nas pendentes
            resp_pending = await client.get(
                "/api/v1/time-bank/pending",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp_pending.status_code == 200
            assert len(resp_pending.json()) == 1

            # 3. Aprovar
            resp_approve = await client.post(
                f"/api/v1/time-bank/{ENTRY_ID}/approve",
                json={"notes": "Aprovado"},
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp_approve.status_code == 200
            assert resp_approve.json()["status"] == "approved"

    @pytest.mark.asyncio
    async def test_rejection_flow(self, client, app):
        """
        Fluxo de rejeição: criar → rejeitar com motivo.
        """
        entry_pending = _make_entry(status="pending")
        entry_rejected = _make_entry(status="rejected")
        entry_rejected.rejection_reason = "Documentacao insuficiente"

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.create = AsyncMock(return_value=entry_pending)
            instance.reject = AsyncMock(return_value=entry_rejected)

            # 1. Criar
            resp_create = await client.post(
                "/api/v1/time-bank/",
                json={
                    "employee_id": EMPLOYEE_ID,
                    "entry_type": "credit",
                    "hours": 4.0,
                    "reference_date": TODAY,
                },
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp_create.status_code == 201

            # 2. Rejeitar
            resp_reject = await client.post(
                f"/api/v1/time-bank/{ENTRY_ID}/reject",
                json={"rejection_reason": "Documentacao insuficiente"},
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp_reject.status_code == 200
            assert resp_reject.json()["status"] == "rejected"

    @pytest.mark.asyncio
    async def test_compensation_flow(self, client, app):
        """
        Fluxo de compensação: verificar saldo → compensar → entrada de débito criada.
        """
        summary = _make_summary(current_balance=16.0)
        entry_compensation = _make_entry(entry_type="compensation", status="approved")

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.get_summary = AsyncMock(return_value=summary)
            instance.compensate = AsyncMock(return_value=entry_compensation)

            # 1. Verificar saldo
            resp_summary = await client.get(
                f"/api/v1/time-bank/summary/{EMPLOYEE_ID}",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp_summary.status_code == 200
            assert resp_summary.json()["current_balance"] == 16.0

            # 2. Compensar
            resp_compensate = await client.post(
                f"/api/v1/time-bank/compensate/{EMPLOYEE_ID}",
                json={"hours": 8.0, "compensation_date": TOMORROW},
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp_compensate.status_code == 200
            assert resp_compensate.json()["entry_type"] == "compensation"

    @pytest.mark.asyncio
    async def test_expiration_detection_flow(self, client, app):
        """
        Fluxo de detecção de expiração: verificar expiring + alerts.
        """
        expiring_entry = _make_entry(
            status="approved",
            expiration_date=date.today() + timedelta(days=5),
        )
        expiring_entry.expiration_date = date.today() + timedelta(days=5)

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            instance.list = AsyncMock(return_value=([expiring_entry], 1))

            # 1. Verificar expiração
            resp_expiring = await client.get(
                "/api/v1/time-bank/expiring?days=30",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp_expiring.status_code == 200
            assert len(resp_expiring.json()) >= 1

            # 2. Verificar alertas
            resp_alerts = await client.get(
                "/api/v1/time-bank/alerts",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp_alerts.status_code == 200
            alerts = resp_alerts.json()
            assert len(alerts) >= 1
            assert alerts[0]["status"] in ("expired", "expiring_soon")

    @pytest.mark.asyncio
    async def test_pagination_flow(self, client, app):
        """
        Verifica paginação correta com múltiplas páginas.
        """
        entries = [_make_entry(entry_id=str(uuid4())) for _ in range(5)]

        with patch(REPO_PATH) as MockRepo:
            instance = MockRepo.return_value
            # Total 50, retornando página 1 com 5 itens
            instance.list = AsyncMock(return_value=(entries, 50))

            # Página 1
            resp_p1 = await client.get(
                "/api/v1/time-bank/?page=1&page_size=5",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp_p1.status_code == 200
            data = resp_p1.json()
            assert data["page"] == 1
            assert data["page_size"] == 5
            assert data["total"] == 50
            assert data["total_pages"] == 10
            assert len(data["items"]) == 5

            # Página 2
            resp_p2 = await client.get(
                "/api/v1/time-bank/?page=2&page_size=5",
                headers={"Authorization": "Bearer fake-token"},
            )
            assert resp_p2.status_code == 200
            assert resp_p2.json()["page"] == 2
