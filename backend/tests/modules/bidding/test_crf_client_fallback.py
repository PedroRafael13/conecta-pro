"""Testes D5.1 — CRFFGTSClient fallback semântico.

Princípio (D5.1/INV-4): quando portal Caixa cai e o fallback BrasilAPI é
acionado, o retorno NUNCA deve afirmar regular=True. BrasilAPI retorna
situacao_cadastral da RFB, que é independente da regularidade FGTS.
`regular=None` é o único valor honesto nesse cenário.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.bidding.integrations.receita_federal.crf_client import CRFFGTSClient
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


@pytest.mark.asyncio
async def test_crf_fallback_brasilapi_nao_afirma_regular_true(cnpj_conecta, cnpj_response_ativa):
    """Fallback BrasilAPI retorna regular=None mesmo quando CNPJ está ATIVO na RFB."""
    client = CRFFGTSClient()

    # Simular portal Caixa indisponível (tentativas 1 e 2 falham)
    with (
        patch.object(client, "_request_with_retry", side_effect=Exception("Portal Caixa offline")),
        patch(
            "modules.bidding.integrations.receita_federal.crf_client.BrasilAPIClient",
            autospec=True,
        ) as MockBrasilAPI,
    ):
        mock_instance = AsyncMock()
        mock_instance.get_cnpj.return_value = (cnpj_response_ativa, False)
        MockBrasilAPI.return_value = mock_instance

        resultado = await client.consultar_crf(cnpj_conecta)

    assert resultado["regular"] is None, (
        f"❌ BUG: fallback BrasilAPI afirmou regular={resultado['regular']} — deve ser None quando portal Caixa cai"
    )
    assert resultado["situacao"] == "indeterminado_portal_indisponivel"
    assert resultado["fonte"] == "BrasilAPI (fallback)"
    assert resultado["cnpj_ativo_rfb"] is True
    assert "NÃO confirmado" in resultado["nota"]


@pytest.mark.asyncio
async def test_crf_fallback_cnpj_baixado_regular_none(cnpj_conecta, cnpj_response_baixada):
    """Fallback BrasilAPI retorna regular=None mesmo quando CNPJ está BAIXADO na RFB."""
    client = CRFFGTSClient()

    with (
        patch.object(client, "_request_with_retry", side_effect=Exception("Portal Caixa offline")),
        patch(
            "modules.bidding.integrations.receita_federal.crf_client.BrasilAPIClient",
            autospec=True,
        ) as MockBrasilAPI,
    ):
        mock_instance = AsyncMock()
        mock_instance.get_cnpj.return_value = (cnpj_response_baixada, False)
        MockBrasilAPI.return_value = mock_instance

        resultado = await client.consultar_crf(cnpj_conecta)

    assert resultado["regular"] is None
    assert resultado["cnpj_ativo_rfb"] is False


@pytest.mark.asyncio
async def test_crf_fallback_total_retorna_regular_none(cnpj_conecta):
    """Quando Caixa + BrasilAPI ambos falham, regular=None (não False)."""
    client = CRFFGTSClient()

    with (
        patch.object(client, "_request_with_retry", side_effect=Exception("Caixa offline")),
        patch(
            "modules.bidding.integrations.receita_federal.crf_client.BrasilAPIClient",
            autospec=True,
        ) as MockBrasilAPI,
    ):
        mock_instance = AsyncMock()
        mock_instance.get_cnpj.side_effect = Exception("BrasilAPI também offline")
        MockBrasilAPI.return_value = mock_instance

        resultado = await client.consultar_crf(cnpj_conecta)

    assert resultado["regular"] is None, f"❌ regular deve ser None quando tudo falha, got {resultado['regular']}"
    assert resultado["situacao"] == "erro_consulta"


@pytest.mark.asyncio
async def test_verificar_regularidade_apto_licitar_none_quando_indeterminado(cnpj_conecta, cnpj_response_ativa):
    """verificar_regularidade: apto_licitar=None quando regular=None."""
    client = CRFFGTSClient()

    with (
        patch.object(client, "_request_with_retry", side_effect=Exception("Caixa offline")),
        patch(
            "modules.bidding.integrations.receita_federal.crf_client.BrasilAPIClient",
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
