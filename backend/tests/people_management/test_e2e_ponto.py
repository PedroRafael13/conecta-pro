"""Testes E2E do Ponto Eletronico - endpoints FastAPI."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from modules.people_management.ponto.controllers.punch_controller import router as ponto_router


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(ponto_router, prefix="/api/v1")
    return app


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestPontoE2E:
    """Testes E2E das rotas de Ponto Eletronico."""

    @pytest.mark.asyncio
    async def test_registrar_batida_entrada(self, client):
        response = await client.post(
            "/api/v1/ponto/batida",
            json={
                "employee_id": 1,
                "punch_type": "entrada",
                "device_type": "web",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["punch_type"] == "entrada"
        assert data["status"] == "normal"
        assert "punch_id" in data

    @pytest.mark.asyncio
    async def test_registrar_batida_com_geo(self, client):
        response = await client.post(
            "/api/v1/ponto/batida",
            json={
                "employee_id": 1,
                "punch_type": "entrada",
                "location": {"latitude": -3.1, "longitude": -60.0, "accuracy": 10.0},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["dentro_geofence"] is True

    @pytest.mark.asyncio
    async def test_registrar_batida_com_facial(self, client):
        response = await client.post(
            "/api/v1/ponto/batida",
            json={
                "employee_id": 1,
                "punch_type": "entrada",
                "facial": {"match": True, "confidence": 0.95, "liveness_check": True},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["facial_match"] is True
        assert data["facial_confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_registrar_batida_offline(self, client):
        response = await client.post(
            "/api/v1/ponto/batida",
            json={
                "employee_id": 2,
                "punch_type": "entrada",
                "is_offline": True,
                "timestamp": "2026-03-13T08:00:00",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["is_offline"] is True
        assert data["status"] == "offline"

    @pytest.mark.asyncio
    async def test_sync_offline_punches(self, client):
        response = await client.post(
            "/api/v1/ponto/sync",
            json={
                "punches": [
                    {"employee_id": 3, "punch_type": "entrada", "timestamp": "2026-03-13T08:00:00"},
                    {"employee_id": 3, "punch_type": "saida_almoco", "timestamp": "2026-03-13T12:00:00"},
                    {"employee_id": 3, "punch_type": "retorno_almoco", "timestamp": "2026-03-13T13:00:00"},
                    {"employee_id": 3, "punch_type": "saida", "timestamp": "2026-03-13T17:00:00"},
                ]
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_received"] == 4
        assert data["total_synced"] == 4
        assert data["total_errors"] == 0

    @pytest.mark.asyncio
    async def test_sync_detecta_duplicatas(self, client):
        punch = {"employee_id": 4, "punch_type": "entrada", "timestamp": "2026-03-13T08:00:00"}
        # Primeira vez
        await client.post("/api/v1/ponto/batida", json=punch)
        # Sync com mesma batida
        response = await client.post("/api/v1/ponto/sync", json={"punches": [punch]})
        data = response.json()
        assert data["total_duplicates"] == 1

    @pytest.mark.asyncio
    async def test_get_batidas_dia(self, client):
        await client.post(
            "/api/v1/ponto/batida",
            json={
                "employee_id": 5,
                "punch_type": "entrada",
                "timestamp": "2026-03-13T08:00:00",
            },
        )
        response = await client.get("/api/v1/ponto/batidas/5?data=2026-03-13")
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == 5
        assert len(data["punches"]) >= 1

    @pytest.mark.asyncio
    async def test_get_espelho_mensal(self, client):
        response = await client.get("/api/v1/ponto/espelho/1?month=3&year=2026")
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == 1
        assert data["month"] == 3

    @pytest.mark.asyncio
    async def test_criar_justificativa(self, client):
        response = await client.post(
            "/api/v1/ponto/justificativa",
            json={
                "employee_id": 1,
                "punch_id": "punch-123",
                "justification_type": "atraso",
                "reason": "Transito muito intenso na AM-010",
                "category": "transito",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pendente"
        assert data["category"] == "transito"

    @pytest.mark.asyncio
    async def test_revisar_justificativa_aprovar(self, client):
        # Criar
        resp = await client.post(
            "/api/v1/ponto/justificativa",
            json={
                "employee_id": 1,
                "justification_type": "atraso",
                "reason": "Onibus atrasou",
                "category": "transporte_publico",
            },
        )
        jid = resp.json()["justification_id"]

        # Aprovar
        response = await client.put(
            f"/api/v1/ponto/justificativa/{jid}/revisar",
            json={
                "action": "aprovar",
                "reviewer_id": "sup-1",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "aprovada"

    @pytest.mark.asyncio
    async def test_revisar_justificativa_rejeitar(self, client):
        resp = await client.post(
            "/api/v1/ponto/justificativa",
            json={
                "employee_id": 2,
                "justification_type": "falta",
                "reason": "Motivo pessoal bastante relevante",
                "category": "outro",
            },
        )
        jid = resp.json()["justification_id"]

        response = await client.put(
            f"/api/v1/ponto/justificativa/{jid}/revisar",
            json={
                "action": "rejeitar",
                "reviewer_id": "sup-1",
                "notes": "Sem comprovante",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejeitada"

    @pytest.mark.asyncio
    async def test_justificativas_pendentes(self, client):
        response = await client.get("/api/v1/ponto/justificativas/pendentes")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_fechar_mes(self, client):
        response = await client.post("/api/v1/ponto/fechamento?employee_id=1&month=3&year=2026&fechado_por=admin-1")
        assert response.status_code == 200
        data = response.json()
        assert data["fechado"] is True
        assert data["employee_id"] == 1

    @pytest.mark.asyncio
    async def test_batida_todos_tipos(self, client):
        for tipo in ["entrada", "saida_almoco", "retorno_almoco", "saida"]:
            response = await client.post(
                "/api/v1/ponto/batida",
                json={
                    "employee_id": 10,
                    "punch_type": tipo,
                },
            )
            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_justificativa_com_anexo(self, client):
        response = await client.post(
            "/api/v1/ponto/justificativa",
            json={
                "employee_id": 1,
                "justification_type": "falta",
                "reason": "Atestado medico de 1 dia",
                "category": "saude",
                "attachments": [{"type": "documento", "file_name": "atestado.pdf", "file_size": 150000}],
            },
        )
        assert response.status_code == 201
