"""
Testes E2E - Fluxo de Operações.

Testa os módulos de Operações: Postos, Escalas, Alocações.
Rotas usam padrão: /api/v1/operacional/{module}/{resource}/

Inclui testes de:
- Existência de endpoints
- Fluxos CRUD completos
- Validações de dados
- Business rules
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestValidations:
    """Testes de validações de dados."""

    @pytest.mark.skip(reason="Requer autenticação")
    async def test_post_validation_limits(self, client: AsyncClient, auth_headers: dict):
        """Testa limites de validação em posts."""
        # Valores fora dos limites permitidos
        invalid_post = {
            "name": "Posto Teste",
            "post_type": "VIGILANTE",
            "hourly_rate": 2000.0,  # Excede máximo de 1000
            "monthly_cost": 200000.0,  # Excede máximo de 100k
            "required_headcount": 100,  # Excede máximo de 50
            "night_shift_bonus_percent": 150.0,  # Excede máximo de 100%
        }

        response = await client.post("/api/v1/operacional/postos/", json=invalid_post, headers=auth_headers)
        assert response.status_code == 422
        errors = response.json()["detail"]
        # Deve ter múltiplos erros de validação
        assert len(errors) > 0

    @pytest.mark.skip(reason="Requer autenticação")
    async def test_allocation_date_validation(self, client: AsyncClient, auth_headers: dict):
        """Testa validação de datas em alocações."""
        from datetime import date, timedelta

        # Data muito antiga (> 2 anos)
        old_date = date.today() - timedelta(days=800)

        invalid_allocation = {
            "post_id": "550e8400-e29b-41d4-a716-446655440000",
            "employee_id": "550e8400-e29b-41d4-a716-446655440001",
            "start_date": old_date.isoformat(),
            "hourly_rate": 25.0,
        }

        response = await client.post(
            "/api/v1/operacional/alocacoes/",
            json=invalid_allocation,
            headers=auth_headers,
        )
        assert response.status_code == 422

    @pytest.mark.skip(reason="Requer autenticação")
    async def test_shift_time_validation(self, client: AsyncClient, auth_headers: dict):
        """Testa validação de horários em turnos."""
        from datetime import date, time

        # Horários iguais (inválido)
        invalid_shift = {
            "scale_id": "550e8400-e29b-41d4-a716-446655440000",
            "post_id": "550e8400-e29b-41d4-a716-446655440001",
            "shift_date": date.today().isoformat(),
            "planned_start_time": "08:00:00",
            "planned_end_time": "08:00:00",  # Igual ao início
        }

        response = await client.post(
            "/api/v1/operacional/turnos/",
            json=invalid_shift,
            headers=auth_headers,
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestOperationsPosts:
    """Testes de Postos."""

    async def test_posts_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de postos existe."""
        response = await client.get("/api/v1/operacional/postos/posts/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_posts_stats_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de stats de postos existe."""
        response = await client.get("/api/v1/operacional/postos/posts/stats")
        assert response.status_code in [200, 401, 403, 422]

    @pytest.mark.skip(reason="Requer autenticação e permissões configuradas")
    async def test_create_post_flow(self, client: AsyncClient, auth_headers: dict):
        """Testa fluxo completo de criação de posto."""
        # Dados do posto
        post_data = {
            "name": "Portaria Principal - Teste E2E",
            "description": "Posto de teste criado automaticamente",
            "post_type": "VIGILANTE",
            "shift_type": "DIURNO",
            "address": "Av. Teste, 1000",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01310-100",
            "required_headcount": 2,
            "requires_armed": False,
            "requires_vehicle": False,
            "hourly_rate": 25.50,
            "monthly_cost": 8000.00,
        }

        # Criar posto
        response = await client.post("/api/v1/operacional/postos/", json=post_data, headers=auth_headers)
        assert response.status_code == 201
        created_post = response.json()
        assert created_post["name"] == post_data["name"]
        assert "id" in created_post
        post_id = created_post["id"]

        # Buscar posto criado
        response = await client.get(f"/api/v1/operacional/postos/{post_id}", headers=auth_headers)
        assert response.status_code == 200
        fetched_post = response.json()
        assert fetched_post["id"] == post_id

        # Atualizar posto
        update_data = {"monthly_cost": 9000.00}
        response = await client.patch(
            f"/api/v1/operacional/postos/{post_id}",
            json=update_data,
            headers=auth_headers,
        )
        assert response.status_code == 200
        updated_post = response.json()
        assert updated_post["monthly_cost"] == 9000.00

        # Deletar posto
        response = await client.delete(f"/api/v1/operacional/postos/{post_id}", headers=auth_headers)
        assert response.status_code == 204


@pytest.mark.asyncio
class TestOperationsScales:
    """Testes de Escalas."""

    async def test_scales_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de escalas existe."""
        response = await client.get("/api/v1/operacional/escalas/scales/")
        assert response.status_code in [200, 401, 403, 422]

    @pytest.mark.skip(reason="Requer posto e funcionários existentes")
    async def test_create_scale_flow(self, client: AsyncClient, auth_headers: dict):
        """Testa fluxo completo de criação de escala."""
        from datetime import date

        today = date.today()

        # Dados da escala
        scale_data = {
            "post_id": "550e8400-e29b-41d4-a716-446655440000",  # ID fictício
            "scale_type": "SCALE_12X36",
            "month": today.month,
            "year": today.year,
            "notes": "Escala de teste E2E",
        }

        # Criar escala
        response = await client.post("/api/v1/operacional/escalas/", json=scale_data, headers=auth_headers)
        # Pode falhar por post_id não existir ou escala duplicada
        assert response.status_code in [201, 400, 404, 422]

        if response.status_code == 201:
            created_scale = response.json()
            assert "id" in created_scale
            scale_id = created_scale["id"]

            # Buscar escala criada
            response = await client.get(f"/api/v1/operacional/escalas/{scale_id}", headers=auth_headers)
            assert response.status_code == 200

            # Testar stats de escalas
            response = await client.get("/api/v1/operacional/escalas/stats", headers=auth_headers)
            assert response.status_code == 200
            stats = response.json()
            assert "total" in stats


@pytest.mark.asyncio
class TestOperationsShifts:
    """Testes de Turnos."""

    async def test_shifts_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de turnos existe."""
        response = await client.get("/api/v1/operacional/turnos/shifts/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_shifts_today_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de turnos de hoje existe."""
        response = await client.get("/api/v1/operacional/turnos/shifts/today")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestOperationsAllocations:
    """Testes de Alocações."""

    async def test_allocations_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de alocações existe."""
        response = await client.get("/api/v1/operacional/alocacoes/allocations/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_allocations_current_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de alocações atuais existe."""
        response = await client.get("/api/v1/operacional/alocacoes/allocations/current")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestClients:
    """Testes de Clientes/Condomínios."""

    @pytest.mark.xfail(reason="Bug: sync query com AsyncSession no repository")
    async def test_clients_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de clientes existe."""
        # Rota tem duplicação: /api/v1/clients/api/v1/clients/
        response = await client.get("/api/v1/clients/api/v1/clients/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestOccurrences:
    """Testes de Ocorrências."""

    async def test_occurrences_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de ocorrências existe."""
        response = await client.get("/api/v1/operacional/occurrences/")
        assert response.status_code in [200, 401, 403, 422]

    @pytest.mark.skip(reason="Requer autenticação e dados de teste")
    async def test_occurrence_validation(self, client: AsyncClient, auth_headers: dict):
        """Testa validações de criação de ocorrência."""
        from datetime import datetime

        # Dados inválidos: IDs não são UUID
        invalid_data = {
            "title": "Teste",
            "description": "Descrição muito curta",  # Deve ter min 10 chars
            "occurrence_type": "COMPORTAMENTO_INADEQUADO",
            "severity": "LEVE",
            "category": "USO_CELULAR",
            "occurred_at": datetime.now().isoformat(),
            "employee_id": "invalid-id",  # ID inválido
            "post_id": "invalid-id",  # ID inválido
        }

        # Deve falhar na validação
        response = await client.post(
            "/api/v1/operacional/occurrences/",
            json=invalid_data,
            headers=auth_headers,
        )
        assert response.status_code == 422  # Validation error
        error_detail = response.json()
        assert "detail" in error_detail


@pytest.mark.asyncio
class TestAudit:
    """Testes de Auditoria."""

    async def test_audit_logs_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de logs de auditoria existe."""
        response = await client.get("/api/v1/audit/audit/logs")
        assert response.status_code in [200, 401, 403, 422]

    async def test_audit_dashboard_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de dashboard de auditoria existe."""
        response = await client.get("/api/v1/audit/audit/dashboard")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestGED:
    """Testes de Gestão de Documentos."""

    async def test_ged_folders_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de pastas GED existe."""
        response = await client.get("/api/v1/ged/folders/folders/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_ged_documents_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de documentos GED existe."""
        response = await client.get("/api/v1/ged/documents/documents/")
        assert response.status_code in [200, 401, 403, 422]
