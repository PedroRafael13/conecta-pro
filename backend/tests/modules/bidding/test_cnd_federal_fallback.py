"""Testes D5.2 — CNDFederalClient URL atualizada + fallback semântico.

Princípio (D5.2/INV-4): quando portal RFB indisponível ou exige auth gov.br,
o retorno NUNCA deve afirmar regular=True. BrasilAPI retorna situacao_cadastral
da RFB, que é independente da regularidade CND/PGFN.
`regular=None` é o único valor honesto nesse cenário (princípio §42.4).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from modules.bidding.integrations.receita_federal.cnd_client import CNDFederalClient
from modules.integrations.brasilapi.schemas import CNPJResponse


@pytest.fixture
def cnpj_conecta():
    return "35710481000103"


@pytest.fixture
def cnpj_response_ativa():
    return CNPJResponse(
        cnpj="35710481000103",
        razao_social="CONECTAMAIS ELETRONICA LTDA",
        descricao_situacao_cadastral="ATIVA",
    )


@pytest.fixture
def cnpj_response_baixada():
    return CNPJResponse(
        cnpj="35710481000103",
        razao_social="EMPRESA BAIXADA LTDA",
        descricao_situacao_cadastral="BAIXADA",
    )


def test_cnd_federal_url_atualizada():
    """CONSULTA_URL aponta para portal novo (não o 404 antigo)."""
    client = CNDFederalClient()
    assert "solucoes.receita.fazenda.gov.br" not in client.CONSULTA_URL, (
        "URL antiga (solucoes.receita.fazenda.gov.br) ainda em uso — deve ser atualizada"
    )
    assert "receitafederal.gov.br" in client.CONSULTA_URL, (
        "URL nova (servicos.receitafederal.gov.br) deve estar em CONSULTA_URL"
    )


@pytest.mark.asyncio
async def test_cnd_federal_fallback_brasilapi_regular_none(cnpj_conecta, cnpj_response_ativa):
    """Fallback BrasilAPI retorna regular=None mesmo quando CNPJ está ATIVO na RFB."""
    client = CNDFederalClient()

    with (
        patch.object(client, "_request_with_retry", side_effect=Exception("Portal RFB offline")),
        patch(
            "modules.bidding.integrations.receita_federal.cnd_client.BrasilAPIClient",
            autospec=True,
        ) as MockBrasilAPI,
    ):
        mock_instance = AsyncMock()
        mock_instance.get_cnpj.return_value = (cnpj_response_ativa, False)
        MockBrasilAPI.return_value = mock_instance

        resultado = await client.consultar_cnd(cnpj_conecta)

    assert resultado["regular"] is None, (
        f"❌ §42.4 VIOLADO: fallback afirmou regular={resultado['regular']} — deve ser None"
    )
    assert resultado["situacao"] == "indeterminado_portal_indisponivel"
    assert resultado["fonte"] == "BrasilAPI (fallback)"
    assert resultado["cnpj_ativo_rfb"] is True
    assert "NÃO confirmado" in resultado["nota"]


@pytest.mark.asyncio
async def test_cnd_federal_fallback_total_retorna_regular_none(cnpj_conecta):
    """Quando RFB + BrasilAPI ambos falham, regular=None (não False)."""
    client = CNDFederalClient()

    with (
        patch.object(client, "_request_with_retry", side_effect=Exception("RFB offline")),
        patch(
            "modules.bidding.integrations.receita_federal.cnd_client.BrasilAPIClient",
            autospec=True,
        ) as MockBrasilAPI,
    ):
        from modules.integrations.brasilapi.exceptions import BrasilAPIUnavailableError

        mock_instance = AsyncMock()
        mock_instance.get_cnpj.side_effect = BrasilAPIUnavailableError("BrasilAPI também offline")
        MockBrasilAPI.return_value = mock_instance

        resultado = await client.consultar_cnd(cnpj_conecta)

    assert resultado["regular"] is None, f"❌ regular deve ser None quando tudo falha, got {resultado['regular']}"
    assert resultado["situacao"] == "erro_consulta"


@pytest.mark.asyncio
async def test_verificar_regularidade_apto_licitar_none_quando_indeterminado(cnpj_conecta, cnpj_response_ativa):
    """verificar_regularidade: apto_licitar=None quando regular=None."""
    client = CNDFederalClient()

    with (
        patch.object(client, "_request_with_retry", side_effect=Exception("RFB offline")),
        patch(
            "modules.bidding.integrations.receita_federal.cnd_client.BrasilAPIClient",
            autospec=True,
        ) as MockBrasilAPI,
    ):
        mock_instance = AsyncMock()
        mock_instance.get_cnpj.return_value = (cnpj_response_ativa, False)
        MockBrasilAPI.return_value = mock_instance

        resultado = await client.verificar_regularidade(cnpj_conecta)

    assert resultado["regular"] is None
    assert resultado["apto_licitar"] is None
    assert "indeterminado" in resultado["observacao"].lower()
