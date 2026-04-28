"""Testes D5.3 — CNDTTrabalhistaClient fallback semântico.

Principio (D5.3/INV-4): portal TST usa captcha de imagem customizado
(tokenDesafio via JS). ROTA-FALLBACK adotada. Quando fallback BrasilAPI
e acionado, regular=None e o unico retorno honesto (§42.4).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from modules.bidding.integrations.receita_federal.cndt_client import CNDTTrabalhistaClient
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


def test_cndt_url_aponta_para_tst_jus_br():
    """CONSULTA_URL aponta para portal TST (tst.jus.br)."""
    client = CNDTTrabalhistaClient()
    assert "tst.jus.br" in client.CONSULTA_URL, "CONSULTA_URL deve apontar para cndt-certidao.tst.jus.br"
    assert "cndt-certidao" in client.CONSULTA_URL, "CONSULTA_URL deve referenciar o portal CNDT do TST"


@pytest.mark.asyncio
async def test_cndt_fallback_brasilapi_regular_none(cnpj_conecta, cnpj_response_ativa):
    """Fallback BrasilAPI retorna regular=None mesmo quando CNPJ esta ATIVO na RFB."""
    client = CNDTTrabalhistaClient()

    with patch(
        "modules.bidding.integrations.receita_federal.cndt_client.BrasilAPIClient",
        autospec=True,
    ) as MockBrasilAPI:
        mock_instance = AsyncMock()
        mock_instance.get_cnpj.return_value = (cnpj_response_ativa, False)
        MockBrasilAPI.return_value = mock_instance

        resultado = await client.consultar_cndt(cnpj_conecta)

    assert resultado["regular"] is None, (
        f"❌ §42.4 VIOLADO: fallback afirmou regular={resultado['regular']} — deve ser None"
    )
    assert resultado["situacao"] == "indeterminado_portal_indisponivel"
    assert resultado["fonte"] == "BrasilAPI (fallback)"
    assert resultado["cnpj_ativo_rfb"] is True
    assert "NÃO confirmado" in resultado["nota"]


@pytest.mark.asyncio
async def test_cndt_fallback_total_retorna_regular_none(cnpj_conecta):
    """Quando TST + BrasilAPI ambos falham, regular=None (nao False)."""
    client = CNDTTrabalhistaClient()

    with patch(
        "modules.bidding.integrations.receita_federal.cndt_client.BrasilAPIClient",
        autospec=True,
    ) as MockBrasilAPI:
        from modules.integrations.brasilapi.exceptions import BrasilAPIUnavailableError

        mock_instance = AsyncMock()
        mock_instance.get_cnpj.side_effect = BrasilAPIUnavailableError("BrasilAPI offline")
        MockBrasilAPI.return_value = mock_instance

        resultado = await client.consultar_cndt(cnpj_conecta)

    assert resultado["regular"] is None, f"❌ regular deve ser None quando tudo falha, got {resultado['regular']}"
    assert resultado["situacao"] == "erro_consulta"


@pytest.mark.asyncio
async def test_verificar_regularidade_tripartite_none(cnpj_conecta, cnpj_response_ativa):
    """verificar_regularidade: apto_licitar=None quando regular=None."""
    client = CNDTTrabalhistaClient()

    with patch(
        "modules.bidding.integrations.receita_federal.cndt_client.BrasilAPIClient",
        autospec=True,
    ) as MockBrasilAPI:
        mock_instance = AsyncMock()
        mock_instance.get_cnpj.return_value = (cnpj_response_ativa, False)
        MockBrasilAPI.return_value = mock_instance

        resultado = await client.verificar_regularidade(cnpj_conecta)

    assert resultado["regular"] is None
    assert resultado["apto_licitar"] is None
    assert "indeterminado" in resultado["observacao"].lower()


@pytest.mark.asyncio
async def test_cndt_fallback_cnpj_baixado_cnpj_ativo_rfb_false(cnpj_conecta, cnpj_response_baixada):
    """Fallback BrasilAPI: cnpj_ativo_rfb=False quando CNPJ esta BAIXADO na RFB."""
    client = CNDTTrabalhistaClient()

    with patch(
        "modules.bidding.integrations.receita_federal.cndt_client.BrasilAPIClient",
        autospec=True,
    ) as MockBrasilAPI:
        mock_instance = AsyncMock()
        mock_instance.get_cnpj.return_value = (cnpj_response_baixada, False)
        MockBrasilAPI.return_value = mock_instance

        resultado = await client.consultar_cndt(cnpj_conecta)

    assert resultado["regular"] is None
    assert resultado["cnpj_ativo_rfb"] is False
    assert resultado["fonte"] == "BrasilAPI (fallback)"
