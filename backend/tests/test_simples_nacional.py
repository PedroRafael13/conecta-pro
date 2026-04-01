"""
Testes para Simples Nacional.

Testes unitários e de integração para Simples Nacional.
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from modules.government_integrations.core.simples_nacional import (
    DAS,
    PGDASD,
    AnexoSimples,
    ReceitaCompetencia,
    SimplesNacionalManager,
    TipoReceita,
)
from modules.government_integrations.schemas.simples_nacional import (
    AnexoSimplesEnum,
    CalcularFatorRRequest,
    CalcularPGDASDRequest,
    GerarDASRequest,
    ReceitaRequest,
    SimularCalculoRequest,
    TipoReceitaEnum,
)
from modules.government_integrations.services.simples_nacional_service import (
    SimplesNacionalService,
)


class TestSchemas:
    """Testes para schemas de validação."""

    def test_simular_calculo_request_valid(self):
        """Testa request de simulação válido."""
        request = SimularCalculoRequest(
            receita_mensal=Decimal("50000.00"),
            rbt12=Decimal("600000.00"),
            folha_12_meses=Decimal("180000.00"),
        )
        assert request.receita_mensal == Decimal("50000.00")
        assert request.rbt12 == Decimal("600000.00")

    def test_receita_request_valid(self):
        """Testa request de receita válido."""
        receita = ReceitaRequest(
            valor_bruto=Decimal("50000.00"),
            tipo_receita=TipoReceitaEnum.SERVICOS,
            anexo=AnexoSimplesEnum.ANEXO_III,
        )
        assert receita.valor_bruto == Decimal("50000.00")
        assert receita.tipo_receita == TipoReceitaEnum.SERVICOS

    def test_calcular_pgdasd_request_valid(self):
        """Testa request de PGDAS-D válido."""
        request = CalcularPGDASDRequest(
            competencia="2026-01",
            receitas=[ReceitaRequest(valor_bruto=Decimal("50000.00"))],
            rbt12=Decimal("600000.00"),
        )
        assert request.competencia == "2026-01"
        assert len(request.receitas) == 1

    def test_gerar_das_request_valid(self):
        """Testa request de DAS válido."""
        request = GerarDASRequest(
            competencia="2026-01",
            receitas=[ReceitaRequest(valor_bruto=Decimal("50000.00"))],
            rbt12=Decimal("600000.00"),
            data_vencimento="2026-02-20",
        )
        assert request.data_vencimento == "2026-02-20"

    def test_calcular_fator_r_request_valid(self):
        """Testa request de Fator R válido."""
        request = CalcularFatorRRequest(
            folha_12_meses=Decimal("180000.00"),
            rbt12=Decimal("600000.00"),
        )
        assert request.folha_12_meses == Decimal("180000.00")


class TestSimplesNacionalManager:
    """Testes para SimplesNacionalManager."""

    @pytest.fixture
    def manager(self):
        """Cria instância do manager."""
        return SimplesNacionalManager(
            cnpj="35710481000103",
            razao_social="Empresa Teste",
            anexo_principal=AnexoSimples.ANEXO_III,
        )

    def test_consultar_opcao(self, manager):
        """Testa consulta de opção."""
        resultado = manager.consultar_opcao()

        assert resultado["cnpj"] == "35710481000103"
        assert resultado["situacao"] == "optante"

    def test_calcular_fator_r_anexo_iii(self, manager):
        """Testa cálculo de Fator R >= 28%."""
        fator_r, anexo = manager.calcular_fator_r(
            folha_12_meses=Decimal("180000.00"),
            rbt12=Decimal("600000.00"),
        )

        # 180000/600000 = 0.30 (30%)
        assert fator_r == Decimal("0.3000")
        assert anexo == AnexoSimples.ANEXO_III

    def test_calcular_fator_r_anexo_v(self, manager):
        """Testa cálculo de Fator R < 28%."""
        fator_r, anexo = manager.calcular_fator_r(
            folha_12_meses=Decimal("150000.00"),
            rbt12=Decimal("600000.00"),
        )

        # 150000/600000 = 0.25 (25%)
        assert fator_r == Decimal("0.2500")
        assert anexo == AnexoSimples.ANEXO_V

    def test_obter_faixa_1(self, manager):
        """Testa obtenção de faixa 1."""
        faixa = manager.obter_faixa(Decimal("100000.00"), AnexoSimples.ANEXO_III)

        assert faixa.faixa == 1
        assert faixa.aliquota_nominal == Decimal("0.06")

    def test_obter_faixa_3(self, manager):
        """Testa obtenção de faixa 3."""
        faixa = manager.obter_faixa(Decimal("500000.00"), AnexoSimples.ANEXO_III)

        assert faixa.faixa == 3
        assert faixa.aliquota_nominal == Decimal("0.135")

    def test_calcular_aliquota_efetiva(self, manager):
        """Testa cálculo de alíquota efetiva."""
        faixa = manager.obter_faixa(Decimal("500000.00"), AnexoSimples.ANEXO_III)

        # (500000 * 0.135 - 17640) / 500000 = 0.0997
        aliquota = faixa.calcular_aliquota_efetiva(Decimal("500000.00"))
        assert aliquota == Decimal("0.0997")

    def test_calcular_pgdasd(self, manager):
        """Testa cálculo de PGDAS-D."""
        receitas = [
            ReceitaCompetencia(
                competencia="2026-01",
                tipo_receita=TipoReceita.SERVICOS,
                anexo=AnexoSimples.ANEXO_III,
                valor_bruto=Decimal("50000.00"),
            )
        ]

        pgdasd = manager.calcular_pgdasd(
            competencia="2026-01",
            receitas=receitas,
            rbt12=Decimal("600000.00"),
        )

        assert pgdasd.competencia == "2026-01"
        assert pgdasd.receita_mes == Decimal("50000.00")
        assert pgdasd.valor_devido > 0

    def test_gerar_das(self, manager):
        """Testa geração de DAS."""
        receitas = [
            ReceitaCompetencia(
                competencia="2026-01",
                tipo_receita=TipoReceita.SERVICOS,
                anexo=AnexoSimples.ANEXO_III,
                valor_bruto=Decimal("50000.00"),
            )
        ]

        pgdasd = manager.calcular_pgdasd("2026-01", receitas, Decimal("600000.00"))
        das = manager.gerar_das(pgdasd)

        assert das.competencia == "2026-01"
        assert das.valor_principal == pgdasd.valor_devido
        assert das.codigo_barras is not None

    def test_gerar_das_data_vencimento(self, manager):
        """Testa data de vencimento do DAS."""
        receitas = [
            ReceitaCompetencia(
                competencia="2026-01",
                tipo_receita=TipoReceita.SERVICOS,
                anexo=AnexoSimples.ANEXO_III,
                valor_bruto=Decimal("10000.00"),
            )
        ]

        pgdasd = manager.calcular_pgdasd("2026-01", receitas, Decimal("100000.00"))
        das = manager.gerar_das(pgdasd)

        # Vencimento padrão: dia 20 do mês seguinte
        assert das.data_vencimento == date(2026, 2, 20)

    def test_simular_calculo(self, manager):
        """Testa simulação de cálculo."""
        resultado = manager.simular_calculo(
            receita_mensal=Decimal("50000.00"),
            rbt12=Decimal("600000.00"),
            folha_12_meses=Decimal("180000.00"),
        )

        assert resultado["receita_mensal"] == "50000.00"
        assert resultado["anexo"] in ["III", "V"]
        assert "composicao" in resultado


class TestSimplesNacionalService:
    """Testes para SimplesNacionalService."""

    @pytest.fixture
    def service(self):
        """Cria instância do service."""
        with patch.dict(
            "os.environ",
            {
                "SIMPLES_CNPJ": "35710481000103",
                "EMPRESA_RAZAO_SOCIAL": "Empresa Teste",
                "SIMPLES_ANEXO": "III",
            },
        ):
            return SimplesNacionalService()

    def test_service_init(self, service):
        """Testa inicialização do service."""
        assert service.cnpj == "35710481000103"
        assert service.anexo_principal == AnexoSimples.ANEXO_III

    def test_consultar_opcao(self, service):
        """Testa consulta de opção via service."""
        resultado = service.consultar_opcao()

        assert resultado["cnpj"] == "35710481000103"
        assert resultado["situacao"] == "optante"

    def test_simular_calculo(self, service):
        """Testa simulação via service."""
        resultado = service.simular_calculo(
            receita_mensal="50000.00",
            rbt12="600000.00",
            folha_12_meses="180000.00",
        )

        assert "valor_devido" in resultado
        assert "composicao" in resultado

    def test_calcular_pgdasd(self, service):
        """Testa PGDAS-D via service."""
        receitas = [
            {
                "valor_bruto": "50000.00",
                "tipo_receita": "servicos",
                "anexo": "III",
            }
        ]

        resultado = service.calcular_pgdasd(
            competencia="2026-01",
            receitas=receitas,
            rbt12="600000.00",
        )

        assert resultado["competencia"] == "2026-01"
        assert "valor_devido" in resultado

    def test_gerar_das(self, service):
        """Testa geração de DAS via service."""
        receitas = [{"valor_bruto": "50000.00", "tipo_receita": "servicos"}]

        resultado = service.gerar_das(
            competencia="2026-01",
            receitas=receitas,
            rbt12="600000.00",
        )

        assert "das" in resultado
        assert "pgdasd" in resultado
        assert resultado["das"]["codigo_barras"] is not None

    def test_calcular_fator_r(self, service):
        """Testa Fator R via service."""
        resultado = service.calcular_fator_r(
            folha_12_meses="180000.00",
            rbt12="600000.00",
        )

        assert resultado["fator_r"] == "0.3000"
        assert resultado["anexo_aplicavel"] == "III"

    def test_obter_tabela_aliquotas(self, service):
        """Testa tabela de alíquotas."""
        tabela = service.obter_tabela_aliquotas("III")

        assert tabela["anexo"] == "III"
        assert len(tabela["faixas"]) == 6

    def test_listar_anexos(self, service):
        """Testa listagem de anexos."""
        anexos = service.listar_anexos()

        assert "anexos" in anexos
        assert len(anexos["anexos"]) == 5

    def test_listar_tipos_receita(self, service):
        """Testa listagem de tipos de receita."""
        tipos = service.listar_tipos_receita()

        assert "tipos" in tipos
        assert len(tipos["tipos"]) == 4

    def test_validar_status(self, service):
        """Testa validação de status."""
        status = service.validar_status()

        assert status["cnpj"] == "35710481000103"
        assert status["anexo_principal"] == "III"


class TestSimplesNacionalEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        from modules.government_integrations.controllers.simples_nacional_controller import router

        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_get_status(self, client):
        """Testa endpoint de status."""
        response = client.get("/api/v1/government/simples-nacional/status")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_consultar_opcao_endpoint(self, client):
        """Testa endpoint de opção."""
        response = client.get("/api/v1/government/simples-nacional/opcao")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_listar_anexos_endpoint(self, client):
        """Testa endpoint de anexos."""
        response = client.get("/api/v1/government/simples-nacional/anexos")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "anexos" in data["data"]

    def test_tabela_aliquotas_endpoint(self, client):
        """Testa endpoint de tabela de alíquotas."""
        response = client.get("/api/v1/government/simples-nacional/tabela-aliquotas/III")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "faixas" in data["data"]

    def test_simular_calculo_endpoint(self, client):
        """Testa endpoint de simulação."""
        payload = {"receita_mensal": "50000.00", "rbt12": "600000.00", "folha_12_meses": "180000.00"}

        response = client.post("/api/v1/government/simples-nacional/simular", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "valor_devido" in data["data"]

    def test_fator_r_endpoint(self, client):
        """Testa endpoint de Fator R."""
        payload = {"folha_12_meses": "180000.00", "rbt12": "600000.00"}

        response = client.post("/api/v1/government/simples-nacional/fator-r", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "anexo_aplicavel" in data["data"]

    def test_pgdasd_endpoint(self, client):
        """Testa endpoint de PGDAS-D."""
        payload = {
            "competencia": "2026-01",
            "receitas": [{"valor_bruto": "50000.00", "tipo_receita": "servicos"}],
            "rbt12": "600000.00",
        }

        response = client.post("/api/v1/government/simples-nacional/pgdasd", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_das_endpoint(self, client):
        """Testa endpoint de DAS."""
        payload = {
            "competencia": "2026-01",
            "receitas": [{"valor_bruto": "50000.00", "tipo_receita": "servicos"}],
            "rbt12": "600000.00",
        }

        response = client.post("/api/v1/government/simples-nacional/das", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "das" in data["data"]
