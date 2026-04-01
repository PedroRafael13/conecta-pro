"""
Testes para EFD-Reinf.

Testes unitários e de integração para eventos EFD-Reinf.
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest

from modules.government_integrations.core.efd_reinf import (
    ClassificacaoTributaria,
    EFDReinfManager,
    IndRetificacao,
    InfoContribuinte,
    PagamentoBeneficiarioPF,
    PagamentoBeneficiarioPJ,
    RetencaoServico,
    TipoAmbiente,
)
from modules.government_integrations.schemas.efd_reinf import (
    ClassificacaoTributariaEnum,
    GerarR1000Request,
    GerarR2010Request,
    GerarR2099Request,
    GerarR4010Request,
    GerarR4020Request,
    PagamentoPFRequest,
    PagamentoPJRequest,
    RetencaoServicoRequest,
)
from modules.government_integrations.services.efd_reinf_service import (
    EFDReinfService,
)


class TestSchemas:
    """Testes para schemas de validação."""

    def test_r1000_request_valid(self):
        """Testa criação de GerarR1000Request válido."""
        request = GerarR1000Request(
            razao_social="Empresa Teste LTDA",
            classificacao_tributaria=ClassificacaoTributariaEnum.EMPRESA_SIMPLES,
            inicio_validade="2026-01",
            email="contato@empresa.com.br",
        )
        assert request.razao_social == "Empresa Teste LTDA"
        assert request.classificacao_tributaria == ClassificacaoTributariaEnum.EMPRESA_SIMPLES

    def test_r1000_request_com_fim_validade(self):
        """Testa R-1000 com fim de validade."""
        request = GerarR1000Request(
            razao_social="Empresa",
            classificacao_tributaria=ClassificacaoTributariaEnum.MEI,
            inicio_validade="2026-01",
            fim_validade="2026-12",
        )
        assert request.fim_validade == "2026-12"

    def test_retencao_servico_valid(self):
        """Testa RetencaoServicoRequest válido."""
        retencao = RetencaoServicoRequest(
            cnpj_prestador="12345678000199",
            valor_bruto=Decimal("10000.00"),
            valor_retencao=Decimal("1100.00"),
            numero_nf="123456",
            data_emissao_nf="2026-01-15",
        )
        assert retencao.cnpj_prestador == "12345678000199"
        assert retencao.valor_retencao == Decimal("1100.00")

    def test_retencao_servico_cnpj_formatado(self):
        """Testa limpeza de formatação do CNPJ."""
        retencao = RetencaoServicoRequest(
            cnpj_prestador="12.345.678/0001-99",
            valor_bruto=Decimal("5000.00"),
            valor_retencao=Decimal("550.00"),
            numero_nf="789",
        )
        assert retencao.cnpj_prestador == "12345678000199"

    def test_r2010_request_valid(self):
        """Testa GerarR2010Request válido."""
        request = GerarR2010Request(
            periodo_apuracao="2026-01",
            retencoes=[
                RetencaoServicoRequest(
                    cnpj_prestador="12345678000199",
                    valor_bruto=Decimal("10000.00"),
                    valor_retencao=Decimal("1100.00"),
                    numero_nf="123",
                )
            ],
        )
        assert request.periodo_apuracao == "2026-01"
        assert len(request.retencoes) == 1

    def test_pagamento_pf_valid(self):
        """Testa PagamentoPFRequest válido."""
        pagamento = PagamentoPFRequest(
            cpf_beneficiario="12345678901",
            nome_beneficiario="João da Silva",
            natureza_rendimento="10008",
            valor_bruto=Decimal("5000.00"),
            valor_irrf=Decimal("750.00"),
            data_pagamento="2026-01-20",
        )
        assert pagamento.cpf_beneficiario == "12345678901"
        assert pagamento.valor_irrf == Decimal("750.00")

    def test_pagamento_pf_cpf_formatado(self):
        """Testa limpeza de CPF formatado."""
        pagamento = PagamentoPFRequest(
            cpf_beneficiario="123.456.789-01",
            nome_beneficiario="Maria",
            natureza_rendimento="10001",
            valor_bruto=Decimal("1000.00"),
        )
        assert pagamento.cpf_beneficiario == "12345678901"

    def test_r4010_request_valid(self):
        """Testa GerarR4010Request válido."""
        request = GerarR4010Request(
            periodo_apuracao="2026-01",
            pagamentos=[
                PagamentoPFRequest(
                    cpf_beneficiario="12345678901",
                    nome_beneficiario="Beneficiário",
                    natureza_rendimento="10008",
                    valor_bruto=Decimal("3000.00"),
                )
            ],
        )
        assert len(request.pagamentos) == 1

    def test_pagamento_pj_valid(self):
        """Testa PagamentoPJRequest válido."""
        pagamento = PagamentoPJRequest(
            cnpj_beneficiario="98765432000188",
            razao_social="Empresa Prestadora LTDA",
            natureza_rendimento="15004",
            valor_bruto=Decimal("25000.00"),
            valor_irrf=Decimal("375.00"),
            valor_csll=Decimal("250.00"),
            valor_cofins=Decimal("750.00"),
            valor_pis=Decimal("162.50"),
        )
        assert pagamento.valor_irrf == Decimal("375.00")

    def test_r4020_request_valid(self):
        """Testa GerarR4020Request válido."""
        request = GerarR4020Request(
            periodo_apuracao="2026-01",
            pagamentos=[
                PagamentoPJRequest(
                    cnpj_beneficiario="98765432000188",
                    razao_social="Empresa",
                    natureza_rendimento="15004",
                    valor_bruto=Decimal("10000.00"),
                )
            ],
        )
        assert len(request.pagamentos) == 1

    def test_r2099_request_valid(self):
        """Testa GerarR2099Request válido."""
        request = GerarR2099Request(periodo_apuracao="2026-01", retificacao=False)
        assert request.periodo_apuracao == "2026-01"


class TestEFDReinfManager:
    """Testes para EFDReinfManager."""

    @pytest.fixture
    def manager(self):
        """Cria instância do manager para testes."""
        return EFDReinfManager(
            certificate_manager=None,
            ambiente=TipoAmbiente.PRODUCAO_RESTRITA,
            cnpj="35710481000103",
        )

    def test_gerar_id_evento(self, manager):
        """Testa geração de ID de evento."""
        id_evento = manager._gerar_id_evento("1000")
        assert id_evento.startswith("ID1000")
        assert "35710481" in id_evento

    def test_gerar_r1000(self, manager):
        """Testa geração de evento R-1000."""
        info = InfoContribuinte(
            cnpj="35710481000103",
            razao_social="Empresa Teste",
            classificacao_tributaria=ClassificacaoTributaria.EMPRESA_SIMPLES,
            inicio_validade="2026-01",
        )

        xml = manager.gerar_r1000(info)

        assert "<Reinf" in xml
        assert "<evtInfoContri" in xml
        assert "<classTrib>02</classTrib>" in xml
        assert "<iniValid>2026-01</iniValid>" in xml

    def test_gerar_r2010(self, manager):
        """Testa geração de evento R-2010."""
        retencoes = [
            RetencaoServico(
                cnpj_prestador="12345678000199",
                valor_bruto=Decimal("10000.00"),
                valor_base_retencao=Decimal("10000.00"),
                valor_retencao=Decimal("1100.00"),
                numero_nf="123456",
            )
        ]

        xml = manager.gerar_r2010("2026-01", retencoes)

        assert "<Reinf" in xml
        assert "<evtServTom" in xml
        assert "<perApur>2026-01</perApur>" in xml
        assert "<vlrBruto>10000.00</vlrBruto>" in xml

    def test_gerar_r4010(self, manager):
        """Testa geração de evento R-4010."""
        pagamentos = [
            PagamentoBeneficiarioPF(
                cpf_beneficiario="12345678901",
                nome_beneficiario="João da Silva",
                natureza_rendimento="10008",
                valor_bruto=Decimal("5000.00"),
                valor_irrf=Decimal("750.00"),
            )
        ]

        xml = manager.gerar_r4010("2026-01", pagamentos)

        assert "<Reinf" in xml
        assert "<evt4010" in xml
        assert "<cpfBenef>12345678901</cpfBenef>" in xml
        assert "<vlrRendBruto>5000.00</vlrRendBruto>" in xml

    def test_gerar_r4020(self, manager):
        """Testa geração de evento R-4020."""
        pagamentos = [
            PagamentoBeneficiarioPJ(
                cnpj_beneficiario="98765432000188",
                razao_social="Empresa LTDA",
                natureza_rendimento="15004",
                valor_bruto=Decimal("25000.00"),
                valor_irrf=Decimal("375.00"),
            )
        ]

        xml = manager.gerar_r4020("2026-01", pagamentos)

        assert "<Reinf" in xml
        assert "<evt4020" in xml
        assert "<cnpjBenef>98765432000188</cnpjBenef>" in xml
        assert "<vlrIR>375.00</vlrIR>" in xml

    def test_gerar_r2099(self, manager):
        """Testa geração de evento R-2099."""
        xml = manager.gerar_r2099("2026-01")

        assert "<Reinf" in xml
        assert "<evtFechaEvPer" in xml
        assert "<perApur>2026-01</perApur>" in xml

    def test_enviar_lote(self, manager):
        """Testa preparação de lote para envio."""
        eventos = [
            "<Reinf><evento1/></Reinf>",
            "<Reinf><evento2/></Reinf>",
        ]

        resultado = manager.enviar_lote(eventos)

        assert resultado["quantidade_eventos"] == 2
        assert resultado["status"] == "pendente"
        assert "xml_envio" in resultado

    def test_url_producao(self):
        """Testa URL de produção."""
        manager = EFDReinfManager(
            certificate_manager=None,
            ambiente=TipoAmbiente.PRODUCAO,
            cnpj="35710481000103",
        )
        assert "reinf.receita.fazenda.gov.br" in manager.url

    def test_url_producao_restrita(self):
        """Testa URL de produção restrita."""
        manager = EFDReinfManager(
            certificate_manager=None,
            ambiente=TipoAmbiente.PRODUCAO_RESTRITA,
            cnpj="35710481000103",
        )
        assert "preproducao.reinf" in manager.url


class TestEFDReinfService:
    """Testes para EFDReinfService."""

    @pytest.fixture
    def service(self):
        """Cria instância do service para testes."""
        with patch.dict(
            "os.environ",
            {
                "EFD_REINF_CNPJ": "35710481000103",
                "EFD_REINF_ENVIRONMENT": "producao_restrita",
                "CERTIFICATE_PATH": "",
            },
        ):
            return EFDReinfService()

    def test_service_init(self, service):
        """Testa inicialização do service."""
        assert service.cnpj == "35710481000103"
        assert service.ambiente_str == "producao_restrita"

    def test_gerar_r1000(self, service):
        """Testa geração de R-1000 via service."""
        resultado = service.gerar_r1000(
            razao_social="Empresa Teste",
            classificacao_tributaria="02",
            inicio_validade="2026-01",
        )

        assert resultado["evento"] == "R-1000"
        assert resultado["status"] == "gerado"
        assert "xml" in resultado

    def test_gerar_r2010(self, service):
        """Testa geração de R-2010 via service."""
        retencoes = [
            {
                "cnpj_prestador": "12345678000199",
                "valor_bruto": "10000.00",
                "valor_retencao": "1100.00",
                "numero_nf": "123",
            }
        ]

        resultado = service.gerar_r2010("2026-01", retencoes)

        assert resultado["evento"] == "R-2010"
        assert resultado["quantidade_retencoes"] == 1
        assert resultado["valor_total_bruto"] == "10000.00"

    def test_gerar_r4010(self, service):
        """Testa geração de R-4010 via service."""
        pagamentos = [
            {
                "cpf_beneficiario": "12345678901",
                "nome_beneficiario": "João",
                "natureza_rendimento": "10008",
                "valor_bruto": "5000.00",
                "valor_irrf": "750.00",
            }
        ]

        resultado = service.gerar_r4010("2026-01", pagamentos)

        assert resultado["evento"] == "R-4010"
        assert resultado["quantidade_pagamentos"] == 1
        assert resultado["valor_total_irrf"] == "750.00"

    def test_gerar_r4020(self, service):
        """Testa geração de R-4020 via service."""
        pagamentos = [
            {
                "cnpj_beneficiario": "98765432000188",
                "razao_social": "Empresa",
                "natureza_rendimento": "15004",
                "valor_bruto": "25000.00",
                "valor_irrf": "375.00",
                "valor_csll": "250.00",
            }
        ]

        resultado = service.gerar_r4020("2026-01", pagamentos)

        assert resultado["evento"] == "R-4020"
        assert resultado["quantidade_pagamentos"] == 1

    def test_gerar_r2099(self, service):
        """Testa geração de R-2099 via service."""
        resultado = service.gerar_r2099("2026-01")

        assert resultado["evento"] == "R-2099"
        assert resultado["periodo_apuracao"] == "2026-01"

    def test_enviar_lote(self, service):
        """Testa envio de lote via service."""
        eventos = ["<xml>teste1</xml>", "<xml>teste2</xml>"]

        resultado = service.enviar_lote(eventos)

        assert resultado["quantidade_eventos"] == 2
        assert "Modo simulado" in resultado["mensagem"]

    def test_listar_naturezas(self, service):
        """Testa listagem de naturezas de rendimento."""
        naturezas = service.listar_naturezas_rendimento()

        assert "pessoa_fisica" in naturezas
        assert "pessoa_juridica" in naturezas
        assert len(naturezas["pessoa_fisica"]) > 0

    def test_listar_classificacoes(self, service):
        """Testa listagem de classificações tributárias."""
        classificacoes = service.listar_classificacoes_tributarias()

        assert "classificacoes" in classificacoes
        assert len(classificacoes["classificacoes"]) > 0

    def test_validar_status(self, service):
        """Testa validação de status."""
        status = service.validar_status()

        assert status["ambiente"] == "producao_restrita"
        assert status["cnpj"] == "35710481000103"
        assert status["certificado_configurado"] is False


class TestEFDReinfEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        from modules.government_integrations.controllers.efd_reinf_controller import router

        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_get_status(self, client):
        """Testa endpoint de status."""
        response = client.get("/api/v1/government/efd-reinf/status")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "eventos_disponiveis" in data["data"]

    def test_listar_naturezas_endpoint(self, client):
        """Testa endpoint de naturezas de rendimento."""
        response = client.get("/api/v1/government/efd-reinf/naturezas-rendimento")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "pessoa_fisica" in data["data"]

    def test_listar_classificacoes_endpoint(self, client):
        """Testa endpoint de classificações tributárias."""
        response = client.get("/api/v1/government/efd-reinf/classificacoes-tributarias")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "classificacoes" in data["data"]

    def test_gerar_r1000_endpoint(self, client):
        """Testa endpoint de geração R-1000."""
        payload = {
            "razao_social": "Empresa Teste LTDA",
            "classificacao_tributaria": "02",
            "inicio_validade": "2026-01",
            "email": "teste@empresa.com.br",
        }

        response = client.post("/api/v1/government/efd-reinf/r1000", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["evento"] == "R-1000"

    def test_gerar_r2010_endpoint(self, client):
        """Testa endpoint de geração R-2010."""
        payload = {
            "periodo_apuracao": "2026-01",
            "retencoes": [
                {
                    "cnpj_prestador": "12345678000199",
                    "valor_bruto": "10000.00",
                    "valor_base_retencao": "10000.00",
                    "valor_retencao": "1100.00",
                    "numero_nf": "123456",
                }
            ],
        }

        response = client.post("/api/v1/government/efd-reinf/r2010", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["evento"] == "R-2010"

    def test_gerar_r4010_endpoint(self, client):
        """Testa endpoint de geração R-4010."""
        payload = {
            "periodo_apuracao": "2026-01",
            "pagamentos": [
                {
                    "cpf_beneficiario": "12345678901",
                    "nome_beneficiario": "João da Silva",
                    "natureza_rendimento": "10008",
                    "valor_bruto": "5000.00",
                    "valor_irrf": "750.00",
                }
            ],
        }

        response = client.post("/api/v1/government/efd-reinf/r4010", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["evento"] == "R-4010"

    def test_gerar_r4020_endpoint(self, client):
        """Testa endpoint de geração R-4020."""
        payload = {
            "periodo_apuracao": "2026-01",
            "pagamentos": [
                {
                    "cnpj_beneficiario": "98765432000188",
                    "razao_social": "Empresa Prestadora",
                    "natureza_rendimento": "15004",
                    "valor_bruto": "25000.00",
                    "valor_irrf": "375.00",
                    "valor_csll": "250.00",
                }
            ],
        }

        response = client.post("/api/v1/government/efd-reinf/r4020", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["evento"] == "R-4020"

    def test_gerar_r2099_endpoint(self, client):
        """Testa endpoint de geração R-2099."""
        payload = {"periodo_apuracao": "2026-01", "retificacao": False}

        response = client.post("/api/v1/government/efd-reinf/r2099", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["evento"] == "R-2099"
