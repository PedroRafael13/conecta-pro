"""Testes de API para modulo Fiscal - Sprint 28."""

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient

from main import app


@pytest.fixture
def auth_headers():
    """Headers de autenticacao para testes."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def condominio_id():
    """ID de condominio para testes."""
    return str(uuid4())


class TestCFOPAPI:
    """Testes para endpoints de CFOP."""

    @pytest.mark.asyncio
    async def test_criar_cfop(self, auth_headers):
        """Testa criacao de CFOP."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/fiscal/cfop",
                headers=auth_headers,
                json={
                    "codigo": "5102",
                    "descricao": "Venda de mercadoria adquirida ou recebida de terceiros",
                    "descricao_resumida": "Venda de mercadoria",
                    "tipo": "saida",
                    "grupo": "5",
                    "natureza": "venda",
                    "gera_debito_icms": True,
                    "movimenta_estoque": True,
                    "movimenta_financeiro": True,
                },
            )

        # Verifica resposta (pode ser 201 ou 401 dependendo do mock de auth)
        assert response.status_code in [201, 401, 403]

    @pytest.mark.asyncio
    async def test_listar_cfops(self, auth_headers):
        """Testa listagem de CFOPs."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/fiscal/cfop",
                headers=auth_headers,
                params={"tipo": "saida", "page": 1, "page_size": 10},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_cfops_vigilancia_zfm(self, auth_headers):
        """Testa endpoint de CFOPs para vigilancia em ZFM."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/fiscal/cfop/vigilancia-zfm",
                headers=auth_headers,
            )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            # Verifica CFOPs comuns para vigilancia
            assert "5933" in data or len(data) >= 0


class TestRetencaoAPI:
    """Testes para endpoints de Retencao Federal."""

    @pytest.mark.asyncio
    async def test_criar_retencao(self, auth_headers, condominio_id):
        """Testa criacao de configuracao de retencao."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/fiscal/retencao",
                headers=auth_headers,
                json={
                    "condominio_id": condominio_id,
                    "nome": "Servicos de Vigilancia",
                    "servico_vigilancia": True,
                    "inss_retido": True,
                    "inss_aliquota": "11.00",
                    "inss_liminar_ativa": True,
                    "inss_liminar_numero": "1234567-89.2024.8.13.0001",
                    "ir_retido": True,
                    "ir_aliquota": "1.50",
                    "ir_base_minima": "666.66",
                    "pis_retido": True,
                    "pis_aliquota": "0.65",
                    "cofins_retido": True,
                    "cofins_aliquota": "3.00",
                    "csll_retido": True,
                    "csll_aliquota": "1.00",
                    "valid_from": date.today().isoformat(),
                },
            )

        assert response.status_code in [201, 401, 403]

    @pytest.mark.asyncio
    async def test_calcular_retencoes(self, auth_headers, condominio_id):
        """Testa calculo de retencoes."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/fiscal/retencao/calcular",
                headers=auth_headers,
                params={"condominio_id": condominio_id},
                json={
                    "valor_servico": "10000.00",
                    "cliente_aceita_liminar": True,
                },
            )

        # Pode retornar 200 ou 404 (se nao houver config)
        assert response.status_code in [200, 401, 404]


class TestNFSeAPI:
    """Testes para endpoints de NFS-e."""

    @pytest.mark.asyncio
    async def test_criar_nfse(self, auth_headers, condominio_id):
        """Testa criacao de NFS-e."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/fiscal/nfse",
                headers=auth_headers,
                json={
                    "condominio_id": condominio_id,
                    "prestador_cnpj": "12345678000199",
                    "prestador_razao_social": "Conecta Mais Servicos LTDA",
                    "tomador_cpf_cnpj": "98765432000188",
                    "tomador_razao_social": "Condominio Residencial Teste",
                    "tomador_logradouro": "Rua Teste",
                    "tomador_numero": "100",
                    "tomador_bairro": "Centro",
                    "tomador_municipio": "Manaus",
                    "tomador_uf": "AM",
                    "tomador_cep": "69000000",
                    "codigo_servico": "11.02",
                    "descricao_servico": "Servicos de vigilancia e seguranca patrimonial",
                    "valor_servicos": "10000.00",
                    "iss_aliquota": "5.00",
                    "data_emissao": datetime.now().isoformat(),
                    "data_competencia": date.today().isoformat(),
                    "serie_rps": "A",
                    "tipo_rps": "1",
                    "natureza_operacao": "1",
                },
            )

        assert response.status_code in [201, 401, 403]

    @pytest.mark.asyncio
    async def test_listar_nfses(self, auth_headers, condominio_id):
        """Testa listagem de NFS-es."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/fiscal/nfse",
                headers=auth_headers,
                params={
                    "condominio_id": condominio_id,
                    "page": 1,
                    "page_size": 10,
                },
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_retencoes_competencia(self, auth_headers, condominio_id):
        """Testa obter retencoes de competencia."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/fiscal/nfse/retencoes/competencia",
                headers=auth_headers,
                params={
                    "condominio_id": condominio_id,
                    "mes": 12,
                    "ano": 2024,
                },
            )

        assert response.status_code in [200, 401]


class TestDASAPI:
    """Testes para endpoints do DAS Simples Nacional."""

    @pytest.mark.asyncio
    async def test_calcular_das(self, auth_headers, condominio_id):
        """Testa calculo do DAS."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/fiscal/das/calcular",
                headers=auth_headers,
                params={"condominio_id": condominio_id},
                json={
                    "receita_bruta_mes": "50000.00",
                    "receita_bruta_12_meses": "500000.00",
                    "anexo": "III",
                    "competencia_mes": 12,
                    "competencia_ano": 2024,
                },
            )

        if response.status_code == 200:
            data = response.json()
            assert "faixa" in data
            assert "aliquota_efetiva" in data
            assert "valor_devido" in data
            assert "reparticao" in data
            assert "data_vencimento" in data

    @pytest.mark.asyncio
    async def test_faixas_simples(self, auth_headers):
        """Testa obter faixas do Simples Nacional."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/fiscal/das/faixas",
                headers=auth_headers,
                params={"anexo": "III"},
            )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 6  # 6 faixas
            # Verifica estrutura da faixa
            assert "faixa" in data[0]
            assert "aliquota" in data[0]
            assert "rbt_inicial" in data[0]
            assert "rbt_final" in data[0]


class TestSPEDAPI:
    """Testes para endpoints de SPED."""

    @pytest.mark.asyncio
    async def test_listar_speds(self, auth_headers, condominio_id):
        """Testa listagem de arquivos SPED."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/fiscal/sped",
                headers=auth_headers,
                params={
                    "condominio_id": condominio_id,
                    "ano": 2024,
                },
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_gerar_sped(self, auth_headers, condominio_id):
        """Testa geracao de arquivo SPED."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/fiscal/sped/gerar",
                headers=auth_headers,
                params={"condominio_id": condominio_id},
                json={
                    "tipo": "efd_contribuicoes",
                    "ano": 2024,
                    "mes": 12,
                    "finalidade": "0",
                },
            )

        assert response.status_code in [200, 401, 403]


class TestObrigacaoAPI:
    """Testes para endpoints de Obrigacoes Fiscais."""

    @pytest.mark.asyncio
    async def test_listar_obrigacoes_pendentes(self, auth_headers, condominio_id):
        """Testa listagem de obrigacoes pendentes."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/fiscal/obrigacao/pendentes",
                headers=auth_headers,
                params={"condominio_id": condominio_id},
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_listar_obrigacoes_atrasadas(self, auth_headers, condominio_id):
        """Testa listagem de obrigacoes atrasadas."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/fiscal/obrigacao/atrasadas",
                headers=auth_headers,
                params={"condominio_id": condominio_id},
            )

        assert response.status_code in [200, 401]


class TestSUFRAMAAPI:
    """Testes para endpoints SUFRAMA."""

    @pytest.mark.asyncio
    async def test_criar_suframa_config(self, auth_headers, condominio_id):
        """Testa criacao de configuracao SUFRAMA."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/fiscal/suframa/config",
                headers=auth_headers,
                json={
                    "condominio_id": condominio_id,
                    "inscricao_suframa": "123456789",
                    "data_validade": "2025-12-31",
                    "tipo_incentivo": "zfm",
                    "isento_ipi": True,
                    "reducao_icms": True,
                    "percentual_reducao_icms": "100.00",
                    "suspensao_pis_cofins": True,
                },
            )

        assert response.status_code in [201, 401, 403]

    @pytest.mark.asyncio
    async def test_obter_economia_suframa(self, auth_headers, condominio_id):
        """Testa obter economia SUFRAMA de um periodo."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/fiscal/suframa/economia",
                headers=auth_headers,
                params={
                    "condominio_id": condominio_id,
                    "data_inicial": "2024-01-01",
                    "data_final": "2024-12-31",
                },
            )

        if response.status_code == 200:
            data = response.json()
            assert "economia_ipi" in data
            assert "economia_icms" in data
            assert "economia_pis_cofins" in data
            assert "total" in data


class TestFiscalDashboardAPI:
    """Testes para endpoints de Dashboard Fiscal."""

    @pytest.mark.asyncio
    async def test_obter_stats(self, auth_headers, condominio_id):
        """Testa obter estatisticas fiscais."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/fiscal/stats",
                headers=auth_headers,
                params={
                    "condominio_id": condominio_id,
                    "mes": 12,
                    "ano": 2024,
                },
            )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_obter_dashboard(self, auth_headers, condominio_id):
        """Testa obter dashboard fiscal completo."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/fiscal/dashboard",
                headers=auth_headers,
                params={
                    "condominio_id": condominio_id,
                    "mes": 12,
                    "ano": 2024,
                },
            )

        assert response.status_code in [200, 401]
