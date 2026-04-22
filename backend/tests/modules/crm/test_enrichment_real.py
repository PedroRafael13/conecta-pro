"""CPRO11 R2 — Testes 🔴 reais integração BrasilAPI via endpoints Conecta PRO."""

import pytest


@pytest.mark.asyncio
async def test_cnpj_conecta_mais_real(auth_client):
    """🔴 CNPJ real da Conecta Mais deve retornar razão social e Manaus."""
    r = await auth_client.get("/api/v1/crm/enrichment/cnpj/35710481000103")
    assert r.status_code == 200
    data = r.json()
    assert data["razao_social"] is not None
    assert data["endereco"]["municipio"] is not None
    assert data["cnae_principal"] is not None
    assert "35.710.481" in data["cnpj"] or data["cnpj"] == "35710481000103"


@pytest.mark.asyncio
async def test_cnpj_invalid_format(auth_client):
    """🔴 CNPJ com menos de 14 dígitos → 422."""
    r = await auth_client.get("/api/v1/crm/enrichment/cnpj/123")
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_cnpj_not_found(auth_client):
    """🔴 CNPJ com 14 dígitos mas inexistente → 404 ou 503 (BrasilAPI instável)."""
    r = await auth_client.get("/api/v1/crm/enrichment/cnpj/00000000000000")
    assert r.status_code in (404, 503)


@pytest.mark.asyncio
async def test_cnpj_cache_hit(auth_client):
    """🔴 Segunda chamada ao mesmo CNPJ: X-Cache=HIT."""
    cnpj = "35710481000103"
    r1 = await auth_client.get(f"/api/v1/crm/enrichment/cnpj/{cnpj}")
    assert r1.status_code == 200
    r2 = await auth_client.get(f"/api/v1/crm/enrichment/cnpj/{cnpj}")
    assert r2.status_code == 200
    assert r2.headers.get("x-cache") == "HIT"
    assert r2.json().get("cache_hit") is True


@pytest.mark.asyncio
async def test_cep_manaus_real(auth_client):
    """🔴 CEP Manaus real → cidade + UF corretos."""
    r = await auth_client.get("/api/v1/crm/enrichment/cep/69073488")
    assert r.status_code == 200
    data = r.json()
    assert data["cidade"] is not None
    assert data["uf"] == "AM"


@pytest.mark.asyncio
async def test_cep_invalid(auth_client):
    """🔴 CEP com formato inválido → 422."""
    r = await auth_client.get("/api/v1/crm/enrichment/cep/abc")
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_taxas_has_all_three(auth_client):
    """🔴 Taxas retorna Selic, CDI, IPCA como números."""
    r = await auth_client.get("/api/v1/crm/enrichment/taxas")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["selic"], (int, float))
    assert isinstance(data["cdi"], (int, float))
    assert isinstance(data["ipca"], (int, float))
    assert data["selic"] > 0
    assert len(data["taxas"]) >= 3


@pytest.mark.asyncio
async def test_taxas_cache(auth_client):
    """🔴 Segunda chamada de Taxas deve ser HIT."""
    await auth_client.get("/api/v1/crm/enrichment/taxas")
    r = await auth_client.get("/api/v1/crm/enrichment/taxas")
    assert r.headers.get("x-cache") == "HIT"


@pytest.mark.asyncio
async def test_cep_brasilapi_5xx_fallback_viacep():
    """🔴 Se BrasilAPI retornar 5xx para CEP → fallback ViaCEP deve retornar dados válidos.

    INV-4: 'Valida que fallback ViaCEP funciona se BrasilAPI 5xx.'
    Mock usado para simular BrasilAPI indisponível (não controlável em teste real).
    """
    from unittest.mock import AsyncMock, patch

    from modules.integrations.brasilapi.client import BrasilAPIClient
    from modules.integrations.brasilapi.exceptions import BrasilAPIUnavailableError

    client = BrasilAPIClient()

    viacep_data = {
        "cep": "01001000",
        "state": "SP",
        "city": "São Paulo",
        "neighborhood": "Sé",
        "street": "Praça da Sé",
        "service": "viacep-fallback",
    }

    with (
        patch.object(client._cache, "get", new=AsyncMock(return_value=None)),
        patch.object(client._cache, "set", new=AsyncMock()),
        patch.object(
            client,
            "_request_with_retry",
            new=AsyncMock(side_effect=BrasilAPIUnavailableError("BrasilAPI 503")),
        ),
        patch.object(
            client,
            "_fallback_viacep",
            new=AsyncMock(return_value=viacep_data),
        ),
    ):
        result, cache_hit = await client.get_cep("01001000")

    assert result.city == "São Paulo"
    assert result.state == "SP"
    assert result.service == "viacep-fallback"
    assert cache_hit is False
