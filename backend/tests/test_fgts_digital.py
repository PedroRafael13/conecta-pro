"""
Testes para FGTS Digital.

Testes unitários e de integração para FGTS Digital.
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import Mock, patch

from modules.government_integrations.schemas.fgts_digital import (
    TrabalhadorRequest,
    CalcularFolhaRequest,
    ImportarESocialRequest,
    GerarGuiaMensalRequest,
    RescisaoRequest,
    ConsultarDebitosRequest,
    ConsultarExtratoRequest,
    SimularSaqueRequest,
    ModalidadeSaqueEnum,
    CategoriaTrabalhadoEnum,
)
from modules.government_integrations.services.fgts_digital_service import (
    FGTSDigitalService,
)
from modules.government_integrations.core.fgts_digital import (
    FGTSDigitalManager,
    TrabalhadorFGTS,
    DebitoFGTS,
    GRFGTS,
    GuiaRescisoria,
    RecolhimentoRescisorio,
    TipoRecolhimento,
    ModalidadeSaque,
    SituacaoGuia,
)


class TestSchemas:
    """Testes para schemas de validação."""

    def test_trabalhador_request_valid(self):
        """Testa request de trabalhador válido."""
        request = TrabalhadorRequest(
            cpf="12345678901",
            nome="João da Silva",
            pis_pasep="12345678901",
            data_admissao="2020-01-15",
            remuneracao=Decimal("5000.00"),
        )
        assert request.cpf == "12345678901"
        assert request.remuneracao == Decimal("5000.00")

    def test_calcular_folha_request_valid(self):
        """Testa request de cálculo de folha válido."""
        request = CalcularFolhaRequest(
            competencia="2026-01",
            trabalhadores=[
                TrabalhadorRequest(
                    cpf="12345678901",
                    nome="João da Silva",
                    pis_pasep="12345678901",
                    data_admissao="2020-01-15",
                    remuneracao=Decimal("5000.00"),
                )
            ],
        )
        assert request.competencia == "2026-01"
        assert len(request.trabalhadores) == 1

    def test_rescisao_request_valid(self):
        """Testa request de rescisão válido."""
        request = RescisaoRequest(
            cpf="12345678901",
            nome="João da Silva",
            pis_pasep="12345678901",
            data_admissao="2020-01-15",
            data_desligamento="2026-01-31",
            motivo_desligamento="Pedido de demissão",
            aviso_previo="trabalhado",
            remuneracao=Decimal("5000.00"),
            saldo_fgts=Decimal("15000.00"),
        )
        assert request.data_desligamento == "2026-01-31"
        assert request.saldo_fgts == Decimal("15000.00")

    def test_simular_saque_request_valid(self):
        """Testa request de simulação de saque válido."""
        request = SimularSaqueRequest(
            cpf="12345678901",
            modalidade=ModalidadeSaqueEnum.RESCISAO,
            valor_solicitado=Decimal("5000.00"),
        )
        assert request.modalidade == ModalidadeSaqueEnum.RESCISAO


class TestFGTSDigitalManager:
    """Testes para FGTSDigitalManager."""

    @pytest.fixture
    def manager(self):
        """Cria instância do manager."""
        return FGTSDigitalManager(
            cnpj="35710481000103",
            razao_social="Empresa Teste",
            ambiente="homologacao",
        )

    def test_init(self, manager):
        """Testa inicialização do manager."""
        assert manager.cnpj == "35710481000103"
        assert manager.ambiente == "homologacao"
        assert manager.ALIQUOTA_FGTS == Decimal("0.08")

    def test_calcular_fgts_folha(self, manager):
        """Testa cálculo de FGTS da folha."""
        trabalhadores = [
            TrabalhadorFGTS(
                cpf="12345678901",
                nome="João",
                pis_pasep="12345678901",
                data_admissao=date(2020, 1, 15),
                remuneracao=Decimal("5000.00"),
            ),
            TrabalhadorFGTS(
                cpf="98765432101",
                nome="Maria",
                pis_pasep="98765432101",
                data_admissao=date(2021, 3, 1),
                remuneracao=Decimal("3000.00"),
            ),
        ]

        resultado = manager.calcular_fgts_folha(trabalhadores, "2026-01")

        assert resultado["competencia"] == "2026-01"
        assert resultado["quantidade_trabalhadores"] == 2
        # 5000 * 0.08 = 400, 3000 * 0.08 = 240, total = 640
        assert Decimal(resultado["total_fgts"]) == Decimal("640")

    def test_gerar_guia_mensal(self, manager):
        """Testa geração de guia mensal."""
        trabalhadores = [
            TrabalhadorFGTS(
                cpf="12345678901",
                nome="João",
                pis_pasep="12345678901",
                data_admissao=date(2020, 1, 15),
                remuneracao=Decimal("5000.00"),
                valor_fgts=Decimal("400.00"),
            ),
        ]

        guia = manager.gerar_guia_mensal(trabalhadores, "2026-01")

        assert guia.competencia == "2026-01"
        assert guia.valor_principal == Decimal("400.00")
        assert guia.chave_pix == "fgts@caixa.gov.br"
        assert guia.codigo_pix is not None
        assert guia.situacao == SituacaoGuia.GERADA

    def test_gerar_guia_mensal_vencimento_padrao(self, manager):
        """Testa vencimento padrão da guia (dia 20 mês seguinte)."""
        trabalhadores = [
            TrabalhadorFGTS(
                cpf="12345678901",
                nome="João",
                pis_pasep="12345678901",
                data_admissao=date(2020, 1, 15),
                remuneracao=Decimal("5000.00"),
                valor_fgts=Decimal("400.00"),
            ),
        ]

        guia = manager.gerar_guia_mensal(trabalhadores, "2026-01")

        assert guia.data_vencimento == date(2026, 2, 20)

    def test_gerar_guia_rescisoria(self, manager):
        """Testa geração de guia rescisória."""
        trabalhador = TrabalhadorFGTS(
            cpf="12345678901",
            nome="João",
            pis_pasep="12345678901",
            data_admissao=date(2020, 1, 15),
            remuneracao=Decimal("5000.00"),
        )

        rescisao = RecolhimentoRescisorio(
            trabalhador=trabalhador,
            data_desligamento=date(2026, 1, 31),
            motivo_desligamento="Demissão sem justa causa",
            aviso_previo="indenizado",
            saldo_fgts=Decimal("15000.00"),
        )

        guia = manager.gerar_guia_rescisoria(rescisao)

        assert guia.cpf_trabalhador == "12345678901"
        # Multa: 15000 * 0.40 = 6000
        assert guia.valor_multa_rescisoria == Decimal("6000.00")
        assert guia.codigo_pix is not None

    def test_importar_esocial(self, manager):
        """Testa importação de dados do eSocial."""
        dados_esocial = {
            "eventos_s1200": [
                {
                    "cpf": "12345678901",
                    "nome": "João da Silva",
                    "pis_pasep": "12345678901",
                    "data_admissao": "2020-01-15",
                    "categoria": "101",
                    "remuneracao_total": "5000.00",
                    "base_fgts": "5000.00",
                }
            ]
        }

        trabalhadores = manager.importar_esocial(dados_esocial, "2026-01")

        assert len(trabalhadores) == 1
        assert trabalhadores[0].cpf == "12345678901"
        # 5000 * 0.08 = 400
        assert trabalhadores[0].valor_fgts == Decimal("400.00")

    def test_consultar_debitos(self, manager):
        """Testa consulta de débitos."""
        debitos = manager.consultar_debitos("2025-01", "2025-12")

        # Implementação mockada retorna lista vazia
        assert debitos == []

    def test_consultar_extrato_trabalhador(self, manager):
        """Testa consulta de extrato."""
        extrato = manager.consultar_extrato_trabalhador("12345678901", "12345678901")

        assert extrato["cpf"] == "12345678901"
        assert "saldo_total" in extrato

    def test_simular_saque(self, manager):
        """Testa simulação de saque."""
        resultado = manager.simular_saque(
            "12345678901",
            ModalidadeSaque.RESCISAO,
            Decimal("5000.00")
        )

        assert resultado["cpf"] == "12345678901"
        assert resultado["modalidade"] == "01"

    def test_gerar_relatorio_mensal(self, manager):
        """Testa geração de relatório mensal."""
        trabalhadores = [
            TrabalhadorFGTS(
                cpf="12345678901",
                nome="João",
                pis_pasep="12345678901",
                data_admissao=date(2020, 1, 15),
                remuneracao=Decimal("5000.00"),
                valor_fgts=Decimal("400.00"),
            ),
        ]

        relatorio = manager.gerar_relatorio_mensal(trabalhadores, "2026-01")

        assert relatorio["competencia"] == "2026-01"
        assert relatorio["resumo"]["quantidade_trabalhadores"] == 1
        assert relatorio["resumo"]["total_fgts_mensal"] == "400.00"


class TestFGTSDigitalService:
    """Testes para FGTSDigitalService."""

    @pytest.fixture
    def service(self):
        """Cria instância do service."""
        with patch.dict('os.environ', {
            'FGTS_CNPJ': '35710481000103',
            'EMPRESA_RAZAO_SOCIAL': 'Empresa Teste',
            'FGTS_AMBIENTE': 'homologacao',
        }):
            return FGTSDigitalService()

    def test_service_init(self, service):
        """Testa inicialização do service."""
        assert service.cnpj == "35710481000103"
        assert service.ambiente == "homologacao"

    def test_validar_status(self, service):
        """Testa validação de status."""
        status = service.validar_status()

        assert status["cnpj"] == "35710481000103"
        assert status["aliquota_fgts"] == "8%"
        assert "calcular_folha" in status["operacoes_disponiveis"]

    def test_calcular_folha(self, service):
        """Testa cálculo de folha via service."""
        trabalhadores = [
            {
                "cpf": "12345678901",
                "nome": "João da Silva",
                "pis_pasep": "12345678901",
                "data_admissao": "2020-01-15",
                "remuneracao": "5000.00",
            }
        ]

        resultado = service.calcular_folha("2026-01", trabalhadores)

        assert resultado["competencia"] == "2026-01"
        assert resultado["quantidade_trabalhadores"] == 1

    def test_gerar_guia_mensal(self, service):
        """Testa geração de guia via service."""
        trabalhadores = [
            {
                "cpf": "12345678901",
                "nome": "João da Silva",
                "pis_pasep": "12345678901",
                "data_admissao": "2020-01-15",
                "remuneracao": "5000.00",
            }
        ]

        resultado = service.gerar_guia_mensal("2026-01", trabalhadores)

        assert "guia" in resultado
        assert resultado["guia"]["competencia"] == "2026-01"
        assert resultado["guia"]["codigo_pix"] is not None

    def test_gerar_guia_rescisoria(self, service):
        """Testa guia rescisória via service."""
        dados_rescisao = {
            "cpf": "12345678901",
            "nome": "João da Silva",
            "pis_pasep": "12345678901",
            "data_admissao": "2020-01-15",
            "data_desligamento": "2026-01-31",
            "motivo_desligamento": "Demissão sem justa causa",
            "aviso_previo": "indenizado",
            "remuneracao": "5000.00",
            "saldo_fgts": "15000.00",
        }

        resultado = service.gerar_guia_rescisoria(dados_rescisao)

        assert "guia" in resultado
        assert "rescisao" in resultado
        # Compara valores numéricos ignorando formatação
        assert Decimal(resultado["rescisao"]["multa_40_percent"]) == Decimal("6000")

    def test_importar_esocial(self, service):
        """Testa importação eSocial via service."""
        eventos = [
            {
                "cpf": "12345678901",
                "nome": "João da Silva",
                "pis_pasep": "12345678901",
                "data_admissao": "2020-01-15",
                "remuneracao_total": "5000.00",
                "base_fgts": "5000.00",
            }
        ]

        resultado = service.importar_esocial("2026-01", eventos)

        assert resultado["quantidade_importados"] == 1

    def test_listar_categorias(self, service):
        """Testa listagem de categorias."""
        categorias = service.listar_categorias()

        assert "categorias" in categorias
        assert len(categorias["categorias"]) >= 5

    def test_listar_modalidades_saque(self, service):
        """Testa listagem de modalidades."""
        modalidades = service.listar_modalidades_saque()

        assert "modalidades" in modalidades
        assert len(modalidades["modalidades"]) >= 5


class TestFGTSDigitalEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI

        app = FastAPI()

        from modules.government_integrations.controllers.fgts_digital_controller import router
        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_get_status(self, client):
        """Testa endpoint de status."""
        response = client.get("/api/v1/government/fgts-digital/status")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_listar_categorias_endpoint(self, client):
        """Testa endpoint de categorias."""
        response = client.get("/api/v1/government/fgts-digital/categorias")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "categorias" in data["data"]

    def test_listar_modalidades_endpoint(self, client):
        """Testa endpoint de modalidades."""
        response = client.get("/api/v1/government/fgts-digital/modalidades-saque")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "modalidades" in data["data"]

    def test_calcular_folha_endpoint(self, client):
        """Testa endpoint de cálculo de folha."""
        payload = {
            "competencia": "2026-01",
            "trabalhadores": [
                {
                    "cpf": "12345678901",
                    "nome": "João da Silva",
                    "pis_pasep": "12345678901",
                    "data_admissao": "2020-01-15",
                    "remuneracao": "5000.00"
                }
            ]
        }

        response = client.post(
            "/api/v1/government/fgts-digital/calcular-folha",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_guia_mensal_endpoint(self, client):
        """Testa endpoint de guia mensal."""
        payload = {
            "competencia": "2026-01",
            "trabalhadores": [
                {
                    "cpf": "12345678901",
                    "nome": "João da Silva",
                    "pis_pasep": "12345678901",
                    "data_admissao": "2020-01-15",
                    "remuneracao": "5000.00"
                }
            ]
        }

        response = client.post(
            "/api/v1/government/fgts-digital/guia-mensal",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "guia" in data["data"]

    def test_guia_rescisoria_endpoint(self, client):
        """Testa endpoint de guia rescisória."""
        payload = {
            "cpf": "12345678901",
            "nome": "João da Silva",
            "pis_pasep": "12345678901",
            "data_admissao": "2020-01-15",
            "data_desligamento": "2026-01-31",
            "motivo_desligamento": "Demissão sem justa causa",
            "aviso_previo": "indenizado",
            "remuneracao": "5000.00",
            "saldo_fgts": "15000.00"
        }

        response = client.post(
            "/api/v1/government/fgts-digital/guia-rescisoria",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "guia" in data["data"]

    def test_importar_esocial_endpoint(self, client):
        """Testa endpoint de importação eSocial."""
        payload = {
            "competencia": "2026-01",
            "eventos_s1200": [
                {
                    "cpf": "12345678901",
                    "nome": "João da Silva",
                    "pis_pasep": "12345678901",
                    "data_admissao": "2020-01-15",
                    "remuneracao_total": "5000.00",
                    "base_fgts": "5000.00"
                }
            ]
        }

        response = client.post(
            "/api/v1/government/fgts-digital/importar-esocial",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_consultar_debitos_endpoint(self, client):
        """Testa endpoint de consulta de débitos."""
        payload = {
            "competencia_inicio": "2025-01",
            "competencia_fim": "2025-12"
        }

        response = client.post(
            "/api/v1/government/fgts-digital/debitos",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_simular_saque_endpoint(self, client):
        """Testa endpoint de simulação de saque."""
        payload = {
            "cpf": "12345678901",
            "modalidade": "01",
            "valor_solicitado": "5000.00"
        }

        response = client.post(
            "/api/v1/government/fgts-digital/simular-saque",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_relatorio_mensal_endpoint(self, client):
        """Testa endpoint de relatório mensal."""
        payload = {
            "competencia": "2026-01",
            "trabalhadores": [
                {
                    "cpf": "12345678901",
                    "nome": "João da Silva",
                    "pis_pasep": "12345678901",
                    "data_admissao": "2020-01-15",
                    "remuneracao": "5000.00"
                }
            ]
        }

        response = client.post(
            "/api/v1/government/fgts-digital/relatorio-mensal",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "resumo" in data["data"]
