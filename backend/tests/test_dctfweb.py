"""
Testes para DCTFWeb.

Testes unitários e de integração para DCTFWeb.
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import Mock, patch

from modules.government_integrations.schemas.dctfweb import (
    CriarDeclaracaoRequest,
    ImportarESocialRequest,
    DadosESocialRequest,
    GerarDarfsRequest,
    TipoDeclaracaoEnum,
)
from modules.government_integrations.services.dctfweb_service import (
    DCTFWebService,
)
from modules.government_integrations.core.dctfweb import (
    DCTFWebManager,
    DCTFWebDeclaracao,
    DebitoContribuicao,
    CreditoVinculavel,
    DARF,
    TipoDeclaracao,
    SituacaoDeclaracao,
    TipoCredito,
)


class TestSchemas:
    """Testes para schemas de validação."""

    def test_criar_declaracao_request_valid(self):
        """Testa criação de request válido."""
        request = CriarDeclaracaoRequest(
            periodo_apuracao="2026-01",
            tipo=TipoDeclaracaoEnum.MENSAL
        )
        assert request.periodo_apuracao == "2026-01"
        assert request.tipo == TipoDeclaracaoEnum.MENSAL

    def test_dados_esocial_request_valid(self):
        """Testa dados eSocial válidos."""
        dados = DadosESocialRequest(
            contribuicao_patronal=Decimal("25000.00"),
            contribuicao_segurado=Decimal("8500.00"),
            rat=Decimal("2500.00"),
            salario_familia=Decimal("150.00"),
        )
        assert dados.contribuicao_patronal == Decimal("25000.00")
        assert dados.salario_familia == Decimal("150.00")

    def test_dados_esocial_com_terceiros(self):
        """Testa dados eSocial com terceiros."""
        dados = DadosESocialRequest(
            contribuicao_patronal=Decimal("25000.00"),
            terceiros={
                "1184": Decimal("1500.00"),
                "1190": Decimal("500.00"),
            }
        )
        assert "1184" in dados.terceiros
        assert dados.terceiros["1184"] == Decimal("1500.00")

    def test_importar_esocial_request_valid(self):
        """Testa request de importação eSocial."""
        request = ImportarESocialRequest(
            periodo_apuracao="2026-01",
            dados_esocial=DadosESocialRequest(
                contribuicao_patronal=Decimal("25000.00")
            )
        )
        assert request.periodo_apuracao == "2026-01"

    def test_gerar_darfs_request_valid(self):
        """Testa request de geração de DARFs."""
        request = GerarDarfsRequest(
            periodo_apuracao="2026-01",
            dados_esocial=DadosESocialRequest(
                contribuicao_patronal=Decimal("25000.00")
            ),
            data_vencimento="2026-02-20"
        )
        assert request.data_vencimento == "2026-02-20"


class TestDCTFWebManager:
    """Testes para DCTFWebManager."""

    @pytest.fixture
    def manager(self):
        """Cria instância do manager."""
        return DCTFWebManager(
            cnpj="35710481000103",
            razao_social="Empresa Teste",
            ambiente="producao",
        )

    def test_criar_declaracao(self, manager):
        """Testa criação de declaração."""
        declaracao = manager.criar_declaracao("2026-01")

        assert declaracao.periodo_apuracao == "2026-01"
        assert declaracao.cnpj == "35710481000103"
        assert declaracao.situacao == SituacaoDeclaracao.EM_ANDAMENTO

    def test_criar_declaracao_anual(self, manager):
        """Testa criação de declaração anual."""
        declaracao = manager.criar_declaracao("2026-12", TipoDeclaracao.ANUAL)

        assert declaracao.tipo == TipoDeclaracao.ANUAL

    def test_importar_esocial(self, manager):
        """Testa importação de dados eSocial."""
        declaracao = manager.criar_declaracao("2026-01")

        dados = {
            "contribuicao_patronal": "25000.00",
            "contribuicao_segurado": "8500.00",
            "rat": "2500.00",
            "salario_familia": "150.00",
        }

        declaracao = manager.importar_esocial(declaracao, dados)

        assert len(declaracao.debitos) == 3
        assert len(declaracao.creditos) == 1
        assert declaracao.total_debitos == Decimal("36000.00")
        assert declaracao.total_creditos == Decimal("150.00")

    def test_importar_esocial_com_terceiros(self, manager):
        """Testa importação com terceiros."""
        declaracao = manager.criar_declaracao("2026-01")

        dados = {
            "contribuicao_patronal": "10000.00",
            "terceiros": {
                "1184": "500.00",
                "1190": "300.00",
            }
        }

        declaracao = manager.importar_esocial(declaracao, dados)

        assert len(declaracao.debitos) == 3

    def test_importar_reinf(self, manager):
        """Testa importação de dados EFD-Reinf."""
        declaracao = manager.criar_declaracao("2026-01")

        dados = {
            "retencoes_tomados": [
                {"cnpj_prestador": "12345678000199", "valor_retencao": "1100.00"},
                {"cnpj_prestador": "98765432000188", "valor_retencao": "550.00"},
            ]
        }

        declaracao = manager.importar_reinf(declaracao, dados)

        assert len(declaracao.creditos) == 2
        assert declaracao.total_creditos == Decimal("1650.00")

    def test_gerar_darfs(self, manager):
        """Testa geração de DARFs."""
        declaracao = manager.criar_declaracao("2026-01")
        declaracao.debitos.append(DebitoContribuicao(
            codigo_receita="1138",
            descricao="CP Patronal",
            valor_principal=Decimal("25000.00"),
            periodo_apuracao="2026-01",
        ))
        declaracao.debitos.append(DebitoContribuicao(
            codigo_receita="1162",
            descricao="CP Segurado",
            valor_principal=Decimal("8500.00"),
            periodo_apuracao="2026-01",
        ))

        darfs = manager.gerar_darfs(declaracao)

        assert len(darfs) == 2
        assert darfs[0].codigo_receita == "1138"
        assert darfs[0].valor_principal == Decimal("25000.00")

    def test_gerar_darfs_com_creditos(self, manager):
        """Testa geração de DARFs com créditos aplicados."""
        declaracao = manager.criar_declaracao("2026-01")
        declaracao.debitos.append(DebitoContribuicao(
            codigo_receita="1138",
            descricao="CP Patronal",
            valor_principal=Decimal("10000.00"),
            periodo_apuracao="2026-01",
        ))
        declaracao.creditos.append(CreditoVinculavel(
            tipo=TipoCredito.SALARIO_FAMILIA,
            descricao="Salário Família",
            valor=Decimal("500.00"),
            periodo_apuracao="2026-01",
        ))

        darfs = manager.gerar_darfs(declaracao)

        # Crédito de 500 aplicado ao débito de 10000
        assert darfs[0].valor_principal == Decimal("9500.00")

    def test_gerar_darfs_data_vencimento(self, manager):
        """Testa data de vencimento dos DARFs."""
        declaracao = manager.criar_declaracao("2026-01")
        declaracao.debitos.append(DebitoContribuicao(
            codigo_receita="1138",
            descricao="CP",
            valor_principal=Decimal("1000.00"),
            periodo_apuracao="2026-01",
        ))

        darfs = manager.gerar_darfs(declaracao)

        # Vencimento padrão: dia 20 do mês seguinte
        assert darfs[0].data_vencimento == date(2026, 2, 20)

    def test_transmitir(self, manager):
        """Testa transmissão de declaração."""
        declaracao = manager.criar_declaracao("2026-01")
        declaracao.debitos.append(DebitoContribuicao(
            codigo_receita="1138",
            descricao="CP",
            valor_principal=Decimal("1000.00"),
            periodo_apuracao="2026-01",
        ))

        resultado = manager.transmitir(declaracao)

        assert resultado["numero_recibo"].startswith("DCTFWeb")
        assert resultado["situacao"] == "ativa"
        assert declaracao.situacao == SituacaoDeclaracao.ATIVA

    def test_consultar(self, manager):
        """Testa consulta de declaração."""
        resultado = manager.consultar("2026-01")

        assert resultado["periodo_apuracao"] == "2026-01"
        assert resultado["cnpj"] == "35710481000103"

    def test_declaracao_saldo_a_pagar(self, manager):
        """Testa cálculo de saldo a pagar."""
        declaracao = manager.criar_declaracao("2026-01")
        declaracao.debitos.append(DebitoContribuicao(
            codigo_receita="1138",
            descricao="CP",
            valor_principal=Decimal("10000.00"),
            periodo_apuracao="2026-01",
        ))
        declaracao.creditos.append(CreditoVinculavel(
            tipo=TipoCredito.SALARIO_FAMILIA,
            descricao="SF",
            valor=Decimal("500.00"),
            periodo_apuracao="2026-01",
        ))

        assert declaracao.total_debitos == Decimal("10000.00")
        assert declaracao.total_creditos == Decimal("500.00")
        assert declaracao.saldo_a_pagar == Decimal("9500.00")


class TestDCTFWebService:
    """Testes para DCTFWebService."""

    @pytest.fixture
    def service(self):
        """Cria instância do service."""
        with patch.dict('os.environ', {
            'DCTFWEB_CNPJ': '35710481000103',
            'EMPRESA_RAZAO_SOCIAL': 'Empresa Teste',
            'DCTFWEB_ENVIRONMENT': 'producao',
        }):
            return DCTFWebService()

    def test_service_init(self, service):
        """Testa inicialização do service."""
        assert service.cnpj == "35710481000103"
        assert service.ambiente == "producao"

    def test_criar_declaracao(self, service):
        """Testa criação de declaração via service."""
        resultado = service.criar_declaracao("2026-01")

        assert resultado["periodo_apuracao"] == "2026-01"
        assert resultado["tipo"] == "1"
        assert resultado["saldo_a_pagar"] == "0"

    def test_importar_esocial(self, service):
        """Testa importação eSocial via service."""
        dados = {
            "contribuicao_patronal": "25000.00",
            "contribuicao_segurado": "8500.00",
        }

        resultado = service.importar_esocial("2026-01", dados)

        assert len(resultado["debitos"]) == 2
        assert resultado["total_debitos"] == "33500.00"

    def test_consolidar_declaracao(self, service):
        """Testa consolidação via service."""
        dados_esocial = {
            "contribuicao_patronal": "25000.00",
            "salario_familia": "150.00",
        }
        dados_reinf = {
            "retencoes_tomados": [
                {"cnpj_prestador": "12345678000199", "valor_retencao": "1100.00"}
            ]
        }

        resultado = service.consolidar_declaracao(
            "2026-01", dados_esocial, dados_reinf
        )

        assert len(resultado["debitos"]) == 1
        assert len(resultado["creditos"]) == 2

    def test_gerar_darfs(self, service):
        """Testa geração de DARFs via service."""
        dados = {
            "contribuicao_patronal": "25000.00",
            "contribuicao_segurado": "8500.00",
        }

        resultado = service.gerar_darfs("2026-01", dados)

        assert resultado["quantidade_darfs"] == 2
        assert len(resultado["darfs"]) == 2

    def test_transmitir(self, service):
        """Testa transmissão via service."""
        dados = {"contribuicao_patronal": "10000.00"}

        resultado = service.transmitir("2026-01", dados)

        assert "numero_recibo" in resultado
        assert resultado["situacao"] == "ativa"

    def test_listar_codigos_receita(self, service):
        """Testa listagem de códigos de receita."""
        codigos = service.listar_codigos_receita()

        assert "codigos" in codigos
        assert len(codigos["codigos"]) > 0

    def test_listar_tipos_declaracao(self, service):
        """Testa listagem de tipos de declaração."""
        tipos = service.listar_tipos_declaracao()

        assert "tipos" in tipos
        assert len(tipos["tipos"]) == 4

    def test_listar_tipos_credito(self, service):
        """Testa listagem de tipos de crédito."""
        tipos = service.listar_tipos_credito()

        assert "tipos" in tipos
        assert len(tipos["tipos"]) > 0

    def test_validar_status(self, service):
        """Testa validação de status."""
        status = service.validar_status()

        assert status["ambiente"] == "producao"
        assert status["cnpj"] == "35710481000103"
        assert "operacoes_disponiveis" in status


class TestDCTFWebEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI

        app = FastAPI()

        from modules.government_integrations.controllers.dctfweb_controller import router
        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_get_status(self, client):
        """Testa endpoint de status."""
        response = client.get("/api/v1/government/dctfweb/status")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "operacoes_disponiveis" in data["data"]

    def test_listar_codigos_receita_endpoint(self, client):
        """Testa endpoint de códigos de receita."""
        response = client.get("/api/v1/government/dctfweb/codigos-receita")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "codigos" in data["data"]

    def test_listar_tipos_declaracao_endpoint(self, client):
        """Testa endpoint de tipos de declaração."""
        response = client.get("/api/v1/government/dctfweb/tipos-declaracao")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_criar_declaracao_endpoint(self, client):
        """Testa endpoint de criação de declaração."""
        payload = {
            "periodo_apuracao": "2026-01",
            "tipo": "1"
        }

        response = client.post(
            "/api/v1/government/dctfweb/criar",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_importar_esocial_endpoint(self, client):
        """Testa endpoint de importação eSocial."""
        payload = {
            "periodo_apuracao": "2026-01",
            "dados_esocial": {
                "contribuicao_patronal": "25000.00",
                "contribuicao_segurado": "8500.00"
            }
        }

        response = client.post(
            "/api/v1/government/dctfweb/importar-esocial",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_gerar_darfs_endpoint(self, client):
        """Testa endpoint de geração de DARFs."""
        payload = {
            "periodo_apuracao": "2026-01",
            "dados_esocial": {
                "contribuicao_patronal": "25000.00"
            }
        }

        response = client.post(
            "/api/v1/government/dctfweb/gerar-darfs",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "darfs" in data["data"]

    def test_transmitir_endpoint(self, client):
        """Testa endpoint de transmissão."""
        payload = {
            "periodo_apuracao": "2026-01",
            "dados_esocial": {
                "contribuicao_patronal": "10000.00"
            }
        }

        response = client.post(
            "/api/v1/government/dctfweb/transmitir",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "numero_recibo" in data["data"]

    def test_consultar_endpoint(self, client):
        """Testa endpoint de consulta."""
        response = client.get("/api/v1/government/dctfweb/consultar/2026-01")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
