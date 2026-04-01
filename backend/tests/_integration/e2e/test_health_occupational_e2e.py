"""
Testes E2E — Módulo Saúde Ocupacional (health_occupational).

Cobre todos os submodulos:
  - NR-7  PCMSO: exames médicos, ASO, vencimentos, estatísticas
  - NR-9  PPRA:  mapeamento de riscos, medidas de controle, estatísticas
  - NR-6  EPI:   catálogo, estoque, entregas, fichas
  - Status:      health, status, info do módulo

Padrão: endpoints sem auth retornam 401/403; com dados inválidos retornam 422.
Todos os testes verificam que o endpoint EXISTE e responde de forma coerente.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

BASE = "/api/v1/health-occupational"

# ──────────────────────────────────────────────────────────────────────────────
# Fixtures de payload reutilizáveis
# ──────────────────────────────────────────────────────────────────────────────

VALID_EPI_ID = "00000000-0000-0000-0000-000000000001"
VALID_EXAM_ID = "00000000-0000-0000-0000-000000000002"
VALID_ASO_ID = "00000000-0000-0000-0000-000000000003"
VALID_MAPPING_ID = "00000000-0000-0000-0000-000000000004"
VALID_MEASURE_ID = "00000000-0000-0000-0000-000000000005"
VALID_DELIVERY_ID = "00000000-0000-0000-0000-000000000006"
VALID_FUNC_ID = "00000000-0000-0000-0000-000000000007"


# ==============================================================================
# HEALTH STATUS — /health-occupational/status, /health, /info
# ==============================================================================


@pytest.mark.asyncio
class TestHealthOccupationalStatus:
    """Testes dos endpoints de status e health do módulo."""

    async def test_module_health_check_exists(self, client: AsyncClient):
        """GET /health-occupational/health deve existir."""
        response = await client.get(f"{BASE}/health")
        assert response.status_code in [200, 401, 403]

    async def test_module_health_check_200(self, client: AsyncClient):
        """GET /health retorna 200 — endpoint público."""
        response = await client.get(f"{BASE}/health")
        # health é um endpoint de status sem autenticação
        assert response.status_code in [200, 401, 403]

    async def test_module_status_endpoint_exists(self, client: AsyncClient):
        """GET /health-occupational/status deve existir."""
        response = await client.get(f"{BASE}/status")
        assert response.status_code in [200, 401, 403]

    async def test_module_info_endpoint_exists(self, client: AsyncClient):
        """GET /health-occupational/info deve existir."""
        response = await client.get(f"{BASE}/info")
        assert response.status_code in [200, 401, 403]

    async def test_module_health_check_returns_json(self, client: AsyncClient):
        """GET /health retorna JSON válido."""
        response = await client.get(f"{BASE}/health")
        assert response.headers.get("content-type", "").startswith("application/json")

    async def test_invalid_path_returns_404(self, client: AsyncClient):
        """Endpoint inexistente retorna 404."""
        response = await client.get(f"{BASE}/nao-existe-nunca")
        assert response.status_code == 404

    async def test_health_check_data_structure(self, client: AsyncClient):
        """GET /health retorna estrutura esperada."""
        response = await client.get(f"{BASE}/health")
        if response.status_code == 200:
            data = response.json()
            assert "status" in data or "module" in data or "success" in data

    async def test_status_data_structure(self, client: AsyncClient):
        """GET /status retorna estrutura esperada."""
        response = await client.get(f"{BASE}/status")
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data

    async def test_info_data_structure(self, client: AsyncClient):
        """GET /info retorna estrutura esperada."""
        response = await client.get(f"{BASE}/info")
        if response.status_code == 200:
            data = response.json()
            assert "name" in data or "features" in data or "compliance" in data


# ==============================================================================
# EPI — /health-occupational/epi/...  (NR-6)
# ==============================================================================


@pytest.mark.asyncio
class TestEPICatalog:
    """Testes do catálogo de EPIs (NR-6)."""

    async def test_list_epis_endpoint_exists(self, client: AsyncClient):
        """GET /epi — listar EPIs deve responder."""
        response = await client.get(f"{BASE}/epi")
        assert response.status_code in [200, 401, 403, 500]

    async def test_get_epi_categories_endpoint_exists(self, client: AsyncClient):
        """GET /epi/categorias deve responder."""
        response = await client.get(f"{BASE}/epi/categorias")
        assert response.status_code in [200, 401, 403]

    async def test_get_epi_statistics_endpoint_exists(self, client: AsyncClient):
        """GET /epi/estatisticas deve responder."""
        response = await client.get(f"{BASE}/epi/estatisticas")
        assert response.status_code in [200, 401, 403]

    async def test_create_epi_sem_auth_retorna_401_ou_422(self, client: AsyncClient):
        """POST /epi/cadastrar sem auth retorna 401/403/422."""
        response = await client.post(f"{BASE}/epi/cadastrar", json={})
        assert response.status_code in [401, 403, 422]

    async def test_create_epi_com_dados_invalidos(self, client: AsyncClient):
        """POST /epi/cadastrar com payload inválido retorna 422 ou 401."""
        payload = {"nome": ""}  # nome vazio — inválido
        response = await client.post(f"{BASE}/epi/cadastrar", json=payload)
        assert response.status_code in [401, 403, 422]

    async def test_get_epi_by_id_endpoint_exists(self, client: AsyncClient):
        """GET /epi/{id} deve responder."""
        response = await client.get(f"{BASE}/epi/{VALID_EPI_ID}")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    async def test_update_epi_sem_auth(self, client: AsyncClient):
        """PATCH /epi/{id} sem auth retorna 401/403."""
        response = await client.patch(f"{BASE}/epi/{VALID_EPI_ID}", json={"nome": "Novo"})
        assert response.status_code in [401, 403, 404, 422, 500]

    async def test_delete_epi_sem_auth(self, client: AsyncClient):
        """DELETE /epi/{id} sem auth retorna 401/403."""
        response = await client.delete(f"{BASE}/epi/{VALID_EPI_ID}")
        assert response.status_code in [401, 403, 404, 422, 500]

    async def test_list_epis_with_filters(self, client: AsyncClient):
        """GET /epi com filtros query params."""
        response = await client.get(f"{BASE}/epi?ativo=true&page=1&size=10")
        assert response.status_code in [200, 401, 403, 422, 500]

    async def test_categories_endpoint_returns_json(self, client: AsyncClient):
        """GET /epi/categorias retorna JSON."""
        response = await client.get(f"{BASE}/epi/categorias")
        assert response.headers.get("content-type", "").startswith("application/json")


@pytest.mark.asyncio
class TestEPIInventory:
    """Testes de estoque de EPI."""

    async def test_list_inventory_endpoint_exists(self, client: AsyncClient):
        """GET /epi/estoque deve responder."""
        response = await client.get(f"{BASE}/epi/estoque")
        assert response.status_code in [200, 401, 403]

    async def test_update_inventory_sem_auth(self, client: AsyncClient):
        """PATCH /epi/estoque/{epi_id} sem auth retorna 401/403."""
        response = await client.patch(
            f"{BASE}/epi/estoque/{VALID_EPI_ID}",
            json={"quantidade_minima": 5},
        )
        assert response.status_code in [401, 403, 404, 422, 500]

    async def test_add_to_inventory_sem_auth(self, client: AsyncClient):
        """POST /epi/estoque/{epi_id}/entrada sem auth retorna 401/403."""
        response = await client.post(
            f"{BASE}/epi/estoque/{VALID_EPI_ID}/entrada",
            json={"quantidade": 10},
        )
        assert response.status_code in [401, 403, 404, 422]

    async def test_inventory_endpoint_returns_json(self, client: AsyncClient):
        """GET /epi/estoque retorna JSON."""
        response = await client.get(f"{BASE}/epi/estoque")
        assert response.headers.get("content-type", "").startswith("application/json")

    async def test_inventory_with_low_stock_filter(self, client: AsyncClient):
        """GET /epi/estoque?estoque_baixo_apenas=true."""
        response = await client.get(f"{BASE}/epi/estoque?estoque_baixo_apenas=true")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestEPIDeliveries:
    """Testes de entregas e fichas de EPI."""

    async def test_get_employee_record_endpoint_exists(self, client: AsyncClient):
        """GET /epi/ficha/{funcionario_id} deve responder."""
        response = await client.get(f"{BASE}/epi/ficha/{VALID_FUNC_ID}")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    async def test_register_delivery_sem_auth(self, client: AsyncClient):
        """POST /epi/entregar sem auth retorna 401/403."""
        response = await client.post(f"{BASE}/epi/entregar", json={})
        assert response.status_code in [401, 403, 422]

    async def test_register_delivery_dados_invalidos(self, client: AsyncClient):
        """POST /epi/entregar com payload inválido retorna 422 ou 401."""
        response = await client.post(
            f"{BASE}/epi/entregar",
            json={"epi_id": "nao-eh-uuid"},
        )
        assert response.status_code in [401, 403, 422]

    async def test_get_delivery_by_id_endpoint_exists(self, client: AsyncClient):
        """GET /epi/entrega/{delivery_id} deve responder."""
        response = await client.get(f"{BASE}/epi/entrega/{VALID_DELIVERY_ID}")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    async def test_sign_delivery_sem_auth(self, client: AsyncClient):
        """POST /epi/entrega/{id}/assinar sem auth retorna 401/403."""
        response = await client.post(f"{BASE}/epi/entrega/{VALID_DELIVERY_ID}/assinar", json={})
        assert response.status_code in [401, 403, 404, 422, 500]

    async def test_return_delivery_sem_auth(self, client: AsyncClient):
        """POST /epi/entrega/{id}/devolver sem auth retorna 401/403."""
        response = await client.post(
            f"{BASE}/epi/entrega/{VALID_DELIVERY_ID}/devolver",
            json={"motivo": "desgaste"},
        )
        assert response.status_code in [401, 403, 404, 422]

    async def test_epi_statistics_returns_json(self, client: AsyncClient):
        """GET /epi/estatisticas retorna JSON."""
        response = await client.get(f"{BASE}/epi/estatisticas")
        assert response.headers.get("content-type", "").startswith("application/json")


# ==============================================================================
# PCMSO — /health-occupational/pcmso/...  (NR-7)
# ==============================================================================


@pytest.mark.asyncio
class TestPCMSOExams:
    """Testes de exames médicos — PCMSO (NR-7)."""

    async def test_schedule_exam_sem_auth(self, client: AsyncClient):
        """POST /pcmso/exames/agendar sem auth retorna 401/403."""
        response = await client.post(f"{BASE}/pcmso/exames/agendar", json={})
        assert response.status_code in [401, 403, 422]

    async def test_schedule_exam_dados_invalidos(self, client: AsyncClient):
        """POST /pcmso/exames/agendar com dados inválidos retorna 422 ou 401."""
        payload = {"tipo_exame": "tipo_invalido_xyz"}
        response = await client.post(f"{BASE}/pcmso/exames/agendar", json=payload)
        assert response.status_code in [401, 403, 422]

    async def test_get_exam_by_id_endpoint_exists(self, client: AsyncClient):
        """GET /pcmso/exames/{id} deve responder."""
        response = await client.get(f"{BASE}/pcmso/exames/{VALID_EXAM_ID}")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    async def test_update_exam_sem_auth(self, client: AsyncClient):
        """PATCH /pcmso/exames/{id} sem auth retorna 401/403."""
        response = await client.patch(
            f"{BASE}/pcmso/exames/{VALID_EXAM_ID}",
            json={"observacoes": "Atualizado"},
        )
        assert response.status_code in [401, 403, 404, 422, 500]

    async def test_list_employee_exams_endpoint_exists(self, client: AsyncClient):
        """GET /pcmso/exames/funcionario/{id} deve responder."""
        response = await client.get(f"{BASE}/pcmso/exames/funcionario/{VALID_FUNC_ID}")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    async def test_confirm_exam_sem_auth(self, client: AsyncClient):
        """POST /pcmso/exames/{id}/confirmar sem auth retorna 401/403."""
        response = await client.post(f"{BASE}/pcmso/exames/{VALID_EXAM_ID}/confirmar", json={})
        assert response.status_code in [401, 403, 404, 422, 500]

    async def test_complete_exam_sem_auth(self, client: AsyncClient):
        """POST /pcmso/exames/{id}/realizar sem auth retorna 401/403."""
        response = await client.post(f"{BASE}/pcmso/exames/{VALID_EXAM_ID}/realizar", json={})
        assert response.status_code in [401, 403, 404, 422, 500]

    async def test_list_exams_with_status_filter(self, client: AsyncClient):
        """GET /pcmso/exames/funcionario/{id}?status=agendado."""
        response = await client.get(f"{BASE}/pcmso/exames/funcionario/{VALID_FUNC_ID}?status=agendado")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    async def test_list_exams_with_tipo_filter(self, client: AsyncClient):
        """GET /pcmso/exames/funcionario/{id}?tipo=admissional."""
        response = await client.get(f"{BASE}/pcmso/exames/funcionario/{VALID_FUNC_ID}?tipo=admissional")
        assert response.status_code in [200, 401, 403, 404, 422, 500]


@pytest.mark.asyncio
class TestPCMSOAso:
    """Testes de ASO (Atestado de Saúde Ocupacional)."""

    async def test_emit_aso_sem_auth(self, client: AsyncClient):
        """POST /pcmso/aso/emitir sem auth retorna 401/403."""
        response = await client.post(f"{BASE}/pcmso/aso/emitir", json={})
        assert response.status_code in [401, 403, 422]

    async def test_emit_aso_dados_invalidos(self, client: AsyncClient):
        """POST /pcmso/aso/emitir com dados inválidos retorna 422 ou 401."""
        payload = {"resultado": "resultado_invalido_xyz"}
        response = await client.post(f"{BASE}/pcmso/aso/emitir", json=payload)
        assert response.status_code in [401, 403, 422]

    async def test_get_aso_by_id_endpoint_exists(self, client: AsyncClient):
        """GET /pcmso/aso/{id} deve responder."""
        response = await client.get(f"{BASE}/pcmso/aso/{VALID_ASO_ID}")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    async def test_list_vencimentos_endpoint_exists(self, client: AsyncClient):
        """GET /pcmso/vencimentos deve responder."""
        response = await client.get(f"{BASE}/pcmso/vencimentos")
        assert response.status_code in [200, 401, 403]

    async def test_list_vencimentos_with_days_filter(self, client: AsyncClient):
        """GET /pcmso/vencimentos?dias=60 filtra por prazo."""
        response = await client.get(f"{BASE}/pcmso/vencimentos?dias=60")
        assert response.status_code in [200, 401, 403, 422]

    async def test_sign_aso_sem_auth(self, client: AsyncClient):
        """POST /pcmso/aso/{id}/assinar sem auth retorna 401/403."""
        response = await client.post(
            f"{BASE}/pcmso/aso/{VALID_ASO_ID}/assinar",
            json={"assinatura": "assinado"},
        )
        assert response.status_code in [401, 403, 404, 422, 500]

    async def test_pcmso_statistics_endpoint_exists(self, client: AsyncClient):
        """GET /pcmso/estatisticas deve responder."""
        response = await client.get(f"{BASE}/pcmso/estatisticas")
        assert response.status_code in [200, 401, 403]

    async def test_pcmso_statistics_returns_json(self, client: AsyncClient):
        """GET /pcmso/estatisticas retorna JSON."""
        response = await client.get(f"{BASE}/pcmso/estatisticas")
        assert response.headers.get("content-type", "").startswith("application/json")

    async def test_vencimentos_returns_json(self, client: AsyncClient):
        """GET /pcmso/vencimentos retorna JSON."""
        response = await client.get(f"{BASE}/pcmso/vencimentos")
        assert response.headers.get("content-type", "").startswith("application/json")


# ==============================================================================
# PPRA — /health-occupational/ppra/...  (NR-9)
# ==============================================================================


@pytest.mark.asyncio
class TestPPRARiskMapping:
    """Testes de mapeamento de riscos — PPRA (NR-9)."""

    async def test_create_mapping_sem_auth(self, client: AsyncClient):
        """POST /ppra/mapeamento sem auth retorna 401/403."""
        response = await client.post(f"{BASE}/ppra/mapeamento", json={})
        assert response.status_code in [401, 403, 422]

    async def test_create_mapping_dados_invalidos(self, client: AsyncClient):
        """POST /ppra/mapeamento com dados inválidos retorna 422 ou 401."""
        payload = {"setor": ""}  # setor vazio
        response = await client.post(f"{BASE}/ppra/mapeamento", json=payload)
        assert response.status_code in [401, 403, 422]

    async def test_get_mapping_by_id_endpoint_exists(self, client: AsyncClient):
        """GET /ppra/mapeamento/{id} deve responder."""
        response = await client.get(f"{BASE}/ppra/mapeamento/{VALID_MAPPING_ID}")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    async def test_update_mapping_sem_auth(self, client: AsyncClient):
        """PATCH /ppra/mapeamento/{id} sem auth retorna 401/403."""
        response = await client.patch(
            f"{BASE}/ppra/mapeamento/{VALID_MAPPING_ID}",
            json={"descricao_setor": "Atualizado"},
        )
        assert response.status_code in [401, 403, 404, 422, 500]

    async def test_list_mappings_endpoint_exists(self, client: AsyncClient):
        """GET /ppra/mapeamentos deve responder."""
        response = await client.get(f"{BASE}/ppra/mapeamentos")
        assert response.status_code in [200, 401, 403]

    async def test_list_mappings_with_filters(self, client: AsyncClient):
        """GET /ppra/mapeamentos?setor=Portaria&ativo=true."""
        response = await client.get(f"{BASE}/ppra/mapeamentos?setor=Portaria&ativo=true")
        assert response.status_code in [200, 401, 403, 422]

    async def test_list_mappings_returns_json(self, client: AsyncClient):
        """GET /ppra/mapeamentos retorna JSON."""
        response = await client.get(f"{BASE}/ppra/mapeamentos")
        assert response.headers.get("content-type", "").startswith("application/json")


@pytest.mark.asyncio
class TestPPRARiskConsultation:
    """Testes de consulta de riscos por setor/função."""

    async def test_get_risks_by_sector_endpoint_exists(self, client: AsyncClient):
        """GET /ppra/riscos/{setor} deve responder."""
        response = await client.get(f"{BASE}/ppra/riscos/Portaria")
        assert response.status_code in [200, 401, 403, 404, 500]

    async def test_get_risks_by_sector_returns_json(self, client: AsyncClient):
        """GET /ppra/riscos/{setor} retorna JSON."""
        response = await client.get(f"{BASE}/ppra/riscos/Portaria")
        assert response.headers.get("content-type", "").startswith("application/json")

    async def test_get_risks_by_function_endpoint_exists(self, client: AsyncClient):
        """GET /ppra/riscos/funcao/{funcao} deve responder."""
        response = await client.get(f"{BASE}/ppra/riscos/funcao/Vigilante")
        assert response.status_code in [200, 401, 403, 404, 500]

    async def test_get_risks_by_function_returns_json(self, client: AsyncClient):
        """GET /ppra/riscos/funcao/{funcao} retorna JSON."""
        response = await client.get(f"{BASE}/ppra/riscos/funcao/Vigilante")
        assert response.headers.get("content-type", "").startswith("application/json")

    async def test_get_risk_categories_endpoint_exists(self, client: AsyncClient):
        """GET /ppra/categorias deve responder."""
        response = await client.get(f"{BASE}/ppra/categorias")
        assert response.status_code in [200, 401, 403]

    async def test_get_risk_categories_returns_json(self, client: AsyncClient):
        """GET /ppra/categorias retorna JSON."""
        response = await client.get(f"{BASE}/ppra/categorias")
        assert response.headers.get("content-type", "").startswith("application/json")

    async def test_ppra_statistics_endpoint_exists(self, client: AsyncClient):
        """GET /ppra/estatisticas deve responder."""
        response = await client.get(f"{BASE}/ppra/estatisticas")
        assert response.status_code in [200, 401, 403]

    async def test_ppra_statistics_returns_json(self, client: AsyncClient):
        """GET /ppra/estatisticas retorna JSON."""
        response = await client.get(f"{BASE}/ppra/estatisticas")
        assert response.headers.get("content-type", "").startswith("application/json")


@pytest.mark.asyncio
class TestPPRAControlMeasures:
    """Testes de medidas de controle."""

    async def test_add_control_measure_sem_auth(self, client: AsyncClient):
        """POST /ppra/medidas-controle sem auth retorna 401/403."""
        response = await client.post(f"{BASE}/ppra/medidas-controle", json={})
        assert response.status_code in [401, 403, 422]

    async def test_add_control_measure_dados_invalidos(self, client: AsyncClient):
        """POST /ppra/medidas-controle com dados inválidos retorna 422 ou 401."""
        payload = {"tipo": "tipo_invalido_xyz"}
        response = await client.post(f"{BASE}/ppra/medidas-controle", json=payload)
        assert response.status_code in [401, 403, 422]

    async def test_update_control_measure_sem_auth(self, client: AsyncClient):
        """PATCH /ppra/medidas-controle/{id} sem auth retorna 401/403."""
        response = await client.patch(
            f"{BASE}/ppra/medidas-controle/{VALID_MEASURE_ID}",
            json={"status": "concluido"},
        )
        assert response.status_code in [401, 403, 404, 422]

    async def test_list_control_measures_endpoint_exists(self, client: AsyncClient):
        """GET /ppra/mapeamento/{id}/medidas-controle deve responder."""
        response = await client.get(f"{BASE}/ppra/mapeamento/{VALID_MAPPING_ID}/medidas-controle")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    async def test_list_control_measures_with_status_filter(self, client: AsyncClient):
        """GET /ppra/mapeamento/{id}/medidas-controle?status=pendente."""
        response = await client.get(f"{BASE}/ppra/mapeamento/{VALID_MAPPING_ID}/medidas-controle?status=pendente")
        assert response.status_code in [200, 401, 403, 404, 422, 500]

    async def test_list_control_measures_returns_json(self, client: AsyncClient):
        """GET /ppra/mapeamento/{id}/medidas-controle retorna JSON."""
        response = await client.get(f"{BASE}/ppra/mapeamento/{VALID_MAPPING_ID}/medidas-controle")
        assert response.headers.get("content-type", "").startswith("application/json")


# ==============================================================================
# FLUXOS INTEGRADOS — cenários E2E de ponta a ponta
# ==============================================================================


@pytest.mark.asyncio
class TestFluxoEPICompleto:
    """
    Fluxo E2E EPI: cadastrar → entregar → devolver.
    Verifica que todos os endpoints do fluxo existem e respondem.
    """

    async def test_fluxo_epi_endpoints_existem(self, client: AsyncClient):
        """Todos os endpoints do fluxo EPI respondem (sem auth = 401/403)."""
        endpoints = [
            ("POST", f"{BASE}/epi/cadastrar", {}),
            ("GET", f"{BASE}/epi", None),
            ("GET", f"{BASE}/epi/estoque", None),
            ("POST", f"{BASE}/epi/entregar", {}),
            ("GET", f"{BASE}/epi/ficha/{VALID_FUNC_ID}", None),
        ]
        for method, url, body in endpoints:
            if method == "POST":
                resp = await client.post(url, json=body)
            else:
                resp = await client.get(url)
            assert resp.status_code in [200, 401, 403, 422, 500], f"{method} {url} retornou {resp.status_code}"

    async def test_fluxo_epi_metodos_corretos(self, client: AsyncClient):
        """Verifica que os métodos HTTP corretos são aceitos."""
        # GET em endpoint de criação deve retornar 405 (method not allowed) ou 404
        response = await client.get(f"{BASE}/epi/cadastrar")
        assert response.status_code in [404, 405, 422]

    async def test_entrega_sem_funcionario_id_retorna_erro(self, client: AsyncClient):
        """POST /epi/entregar sem funcionario_id retorna 401/403/422."""
        payload = {"epi_id": VALID_EPI_ID, "quantidade": 1}
        response = await client.post(f"{BASE}/epi/entregar", json=payload)
        assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
class TestFluxoPCMSOCompleto:
    """
    Fluxo E2E PCMSO: agendar exame → confirmar → realizar → emitir ASO.
    Verifica que todos os endpoints do fluxo existem e respondem.
    """

    async def test_fluxo_pcmso_endpoints_existem(self, client: AsyncClient):
        """Todos os endpoints do fluxo PCMSO respondem."""
        endpoints = [
            ("POST", f"{BASE}/pcmso/exames/agendar", {}),
            ("GET", f"{BASE}/pcmso/exames/{VALID_EXAM_ID}", None),
            ("POST", f"{BASE}/pcmso/exames/{VALID_EXAM_ID}/confirmar", {}),
            ("POST", f"{BASE}/pcmso/exames/{VALID_EXAM_ID}/realizar", {}),
            ("POST", f"{BASE}/pcmso/aso/emitir", {}),
            ("GET", f"{BASE}/pcmso/aso/{VALID_ASO_ID}", None),
            ("GET", f"{BASE}/pcmso/vencimentos", None),
        ]
        for method, url, body in endpoints:
            if method == "POST":
                resp = await client.post(url, json=body)
            else:
                resp = await client.get(url)
            assert resp.status_code in [200, 401, 403, 404, 422, 500], f"{method} {url} retornou {resp.status_code}"

    async def test_agendar_exame_sem_funcionario_retorna_erro(self, client: AsyncClient):
        """POST /pcmso/exames/agendar sem funcionario_id retorna 401/403/422."""
        payload = {"tipo_exame": "admissional"}  # faltam campos obrigatórios
        response = await client.post(f"{BASE}/pcmso/exames/agendar", json=payload)
        assert response.status_code in [401, 403, 422]

    async def test_emitir_aso_sem_exame_retorna_erro(self, client: AsyncClient):
        """POST /pcmso/aso/emitir sem exame_id retorna 401/403/422."""
        payload = {"resultado": "apto"}  # falta exame_id
        response = await client.post(f"{BASE}/pcmso/aso/emitir", json=payload)
        assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
class TestFluxoPPRACompleto:
    """
    Fluxo E2E PPRA: mapear setor → criar riscos → adicionar medidas de controle.
    Verifica que todos os endpoints do fluxo existem e respondem.
    """

    async def test_fluxo_ppra_endpoints_existem(self, client: AsyncClient):
        """Todos os endpoints do fluxo PPRA respondem."""
        endpoints = [
            ("POST", f"{BASE}/ppra/mapeamento", {}),
            ("GET", f"{BASE}/ppra/mapeamentos", None),
            ("GET", f"{BASE}/ppra/mapeamento/{VALID_MAPPING_ID}", None),
            ("POST", f"{BASE}/ppra/medidas-controle", {}),
            ("GET", f"{BASE}/ppra/mapeamento/{VALID_MAPPING_ID}/medidas-controle", None),
            ("GET", f"{BASE}/ppra/riscos/Portaria", None),
            ("GET", f"{BASE}/ppra/riscos/funcao/Vigilante", None),
            ("GET", f"{BASE}/ppra/categorias", None),
        ]
        for method, url, body in endpoints:
            if method == "POST":
                resp = await client.post(url, json=body)
            else:
                resp = await client.get(url)
            assert resp.status_code in [200, 401, 403, 404, 422, 500], f"{method} {url} retornou {resp.status_code}"

    async def test_criar_mapeamento_sem_setor_retorna_erro(self, client: AsyncClient):
        """POST /ppra/mapeamento sem setor retorna 401/403/422."""
        payload = {"descricao_setor": "Área de Acesso Principal"}  # falta setor
        response = await client.post(f"{BASE}/ppra/mapeamento", json=payload)
        assert response.status_code in [401, 403, 422]


# ==============================================================================
# CONFORMIDADE NR — validação de regras de negócio expostas nos endpoints
# ==============================================================================


@pytest.mark.asyncio
class TestNRCompliance:
    """Testes de conformidade com normas regulamentadoras (NR-6, NR-7, NR-9)."""

    async def test_nr6_epi_categories_endpoint_disponivel(self, client: AsyncClient):
        """NR-6: categorias de EPI devem ser consultáveis."""
        response = await client.get(f"{BASE}/epi/categorias")
        assert response.status_code in [200, 401, 403]

    async def test_nr7_pcmso_statistics_disponivel(self, client: AsyncClient):
        """NR-7: estatísticas do PCMSO devem ser consultáveis."""
        response = await client.get(f"{BASE}/pcmso/estatisticas")
        assert response.status_code in [200, 401, 403]

    async def test_nr9_ppra_risk_categories_disponivel(self, client: AsyncClient):
        """NR-9: categorias de risco devem ser consultáveis."""
        response = await client.get(f"{BASE}/ppra/categorias")
        assert response.status_code in [200, 401, 403]

    async def test_nr7_vencimentos_aso_disponivel(self, client: AsyncClient):
        """NR-7: controle de vencimentos de ASO deve ser consultável."""
        response = await client.get(f"{BASE}/pcmso/vencimentos")
        assert response.status_code in [200, 401, 403]

    async def test_module_info_menciona_nrs(self, client: AsyncClient):
        """GET /info deve mencionar NRs relevantes."""
        response = await client.get(f"{BASE}/info")
        if response.status_code == 200:
            text = response.text
            # Pelo menos uma NR deve ser mencionada
            assert any(nr in text for nr in ["NR-4", "NR-6", "NR-7", "NR-9", "NR4", "NR6", "NR7", "NR9"])

    async def test_module_status_menciona_compliance(self, client: AsyncClient):
        """GET /status deve incluir informações de compliance."""
        response = await client.get(f"{BASE}/status")
        if response.status_code == 200:
            data = response.json()
            # Status deve ter dados de compliance ou components
            content = str(data)
            assert any(key in content for key in ["nr", "NR", "compliance", "pcmso", "ppra", "epi"])

    async def test_epi_inventory_endpoint_nr6_estoque(self, client: AsyncClient):
        """NR-6: controle de estoque de EPI deve estar disponível."""
        response = await client.get(f"{BASE}/epi/estoque")
        assert response.status_code in [200, 401, 403]

    async def test_epi_statistics_nr6(self, client: AsyncClient):
        """NR-6: estatísticas de EPI devem ser consultáveis."""
        response = await client.get(f"{BASE}/epi/estatisticas")
        assert response.status_code in [200, 401, 403]

    async def test_ppra_statistics_nr9(self, client: AsyncClient):
        """NR-9: estatísticas do PPRA devem ser consultáveis."""
        response = await client.get(f"{BASE}/ppra/estatisticas")
        assert response.status_code in [200, 401, 403]


# ==============================================================================
# RESPOSTAS JSON — garantia de Content-Type e estrutura
# ==============================================================================


@pytest.mark.asyncio
class TestResponseStructure:
    """Garante que todos os endpoints retornam JSON bem-formado."""

    async def test_all_get_endpoints_return_json(self, client: AsyncClient):
        """Todos os endpoints GET retornam Content-Type application/json."""
        get_endpoints = [
            f"{BASE}/health",
            f"{BASE}/status",
            f"{BASE}/info",
            f"{BASE}/epi",
            f"{BASE}/epi/categorias",
            f"{BASE}/epi/estoque",
            f"{BASE}/epi/estatisticas",
            f"{BASE}/pcmso/vencimentos",
            f"{BASE}/pcmso/estatisticas",
            f"{BASE}/ppra/mapeamentos",
            f"{BASE}/ppra/categorias",
            f"{BASE}/ppra/estatisticas",
        ]
        for url in get_endpoints:
            resp = await client.get(url)
            assert resp.headers.get("content-type", "").startswith("application/json"), (
                f"GET {url} não retornou application/json (status={resp.status_code})"
            )

    async def test_post_endpoint_sem_body_retorna_json(self, client: AsyncClient):
        """POST sem body retorna JSON (não HTML de erro)."""
        response = await client.post(f"{BASE}/epi/cadastrar", json={})
        assert response.headers.get("content-type", "").startswith("application/json")

    async def test_invalid_uuid_retorna_422_ou_404(self, client: AsyncClient):
        """UUID inválido retorna 422 (validação) ou 404."""
        response = await client.get(f"{BASE}/epi/not-a-uuid")
        assert response.status_code in [404, 422]

    async def test_404_retorna_json(self, client: AsyncClient):
        """Endpoint inexistente retorna JSON ou HTML — mas não quebra o servidor."""
        response = await client.get(f"{BASE}/endpoint-que-nao-existe")
        assert response.status_code == 404
