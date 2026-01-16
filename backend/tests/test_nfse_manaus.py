"""
Testes para NFS-e Manaus.

Testes de integração para emissão, consulta e cancelamento de NFS-e.
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock

from modules.government_integrations.schemas.nfse_manaus import (
    EmitirNFSeRequest,
    TomadorRequest,
    ServicoRequest,
    CancelarNFSeRequest,
    NaturezaOperacaoEnum,
    CodigoCancelamentoEnum,
)
from modules.government_integrations.services.nfse_manaus_service import (
    NFSeManausService,
)
from modules.government_integrations.core.nfse_manaus import (
    NFSeManausManager,
    NFSeManaus,
    Tomador,
    Servico,
    NFSeStatus,
)


class TestSchemas:
    """Testes para schemas de validação."""

    def test_tomador_request_valid(self):
        """Testa criação de TomadorRequest válido."""
        tomador = TomadorRequest(
            cpf_cnpj="12345678901234",
            razao_social="Empresa Teste LTDA",
            endereco="Rua Teste",
            numero="100",
            bairro="Centro",
            cidade="Manaus",
            uf="AM",
            cep="69000000",
        )
        assert tomador.cpf_cnpj == "12345678901234"
        assert tomador.cidade == "Manaus"

    def test_tomador_request_cpf(self):
        """Testa TomadorRequest com CPF."""
        tomador = TomadorRequest(
            cpf_cnpj="12345678901",
            razao_social="Pessoa Física",
            endereco="Rua Teste",
            bairro="Centro",
            cep="69000000",
        )
        assert len(tomador.cpf_cnpj) == 11

    def test_tomador_request_cnpj_formatado(self):
        """Testa limpeza de formatação do CNPJ."""
        tomador = TomadorRequest(
            cpf_cnpj="12.345.678/0001-34",
            razao_social="Empresa Teste",
            endereco="Rua Teste",
            bairro="Centro",
            cep="69000-000",
        )
        assert tomador.cpf_cnpj == "12345678000134"
        assert tomador.cep == "69000000"

    def test_tomador_request_cpf_cnpj_invalido(self):
        """Testa rejeição de CPF/CNPJ inválido."""
        with pytest.raises(ValueError):
            TomadorRequest(
                cpf_cnpj="123456",  # Inválido
                razao_social="Teste",
                endereco="Rua",
                bairro="Bairro",
                cep="69000000",
            )

    def test_servico_request_valid(self):
        """Testa criação de ServicoRequest válido."""
        servico = ServicoRequest(
            codigo_servico="11.02",
            discriminacao="Serviços de vigilância patrimonial",
            valor_servicos=Decimal("15000.00"),
            aliquota_iss=Decimal("0.05"),
        )
        assert servico.codigo_servico == "11.02"
        assert servico.valor_servicos == Decimal("15000.00")

    def test_servico_request_valor_negativo(self):
        """Testa rejeição de valor negativo."""
        with pytest.raises(ValueError):
            ServicoRequest(
                codigo_servico="11.02",
                discriminacao="Serviços de teste",
                valor_servicos=Decimal("-100.00"),
            )

    def test_emitir_nfse_request_completo(self):
        """Testa criação de EmitirNFSeRequest completo."""
        request = EmitirNFSeRequest(
            tomador=TomadorRequest(
                cpf_cnpj="12345678901234",
                razao_social="Empresa Cliente",
                endereco="Av. Eduardo Ribeiro",
                numero="1000",
                bairro="Centro",
                cep="69010001",
            ),
            servico=ServicoRequest(
                codigo_servico="11.02",
                discriminacao="Vigilância patrimonial janeiro/2026",
                valor_servicos=Decimal("15000.00"),
            ),
            competencia="2026-01",
            natureza_operacao=NaturezaOperacaoEnum.TRIBUTACAO_MUNICIPIO,
            optante_simples=True,
        )
        assert request.competencia == "2026-01"
        assert request.optante_simples is True


class TestNFSeManausManager:
    """Testes para NFSeManausManager."""

    @pytest.fixture
    def mock_cert_manager(self):
        """Mock do CertificateManager."""
        mock = Mock()
        mock._loaded = True
        mock.get_cert_path.return_value = "/path/to/cert.pem"
        mock.get_key_path.return_value = "/path/to/key.pem"
        mock.get_certificate_base64.return_value = "BASE64CERT"
        mock.sign_data.return_value = b"SIGNATURE"
        return mock

    @pytest.fixture
    def manager(self, mock_cert_manager):
        """Cria instância do manager para testes."""
        return NFSeManausManager(
            certificate_manager=mock_cert_manager,
            ambiente="homologacao",
            cnpj="35710481000103",
            inscricao_municipal="12345",
            usuario="35710481000103",
            senha="senha123",
        )

    def test_gerar_rps(self, manager):
        """Testa geração de XML do RPS."""
        tomador = Tomador(
            cpf_cnpj="12345678901234",
            razao_social="Empresa Cliente",
            endereco="Rua Teste",
            numero="100",
            bairro="Centro",
            cidade="Manaus",
            uf="AM",
            cep="69000000",
        )

        servico = Servico(
            codigo_servico="11.02",
            discriminacao="Serviços de vigilância",
            valor_servicos=Decimal("1000.00"),
        )

        nfse = NFSeManaus(
            prestador_cnpj="35710481000103",
            prestador_inscricao_municipal="12345",
            tomador=tomador,
            servico=servico,
        )

        xml = manager.gerar_rps(nfse)

        assert "<Rps>" in xml
        assert "<InfDeclaracaoPrestacaoServico>" in xml
        assert "<ValorServicos>1000.00</ValorServicos>" in xml
        assert "<ItemListaServico>11.02</ItemListaServico>" in xml
        assert "<Cnpj>35710481000103</Cnpj>" in xml

    def test_enviar_lote_rps(self, manager):
        """Testa envio de lote de RPS."""
        tomador = Tomador(
            cpf_cnpj="12345678901234",
            razao_social="Cliente",
            endereco="Rua",
            numero="1",
            bairro="Centro",
            cidade="Manaus",
            uf="AM",
            cep="69000000",
        )

        servico = Servico(
            codigo_servico="11.02",
            discriminacao="Serviço",
            valor_servicos=Decimal("500.00"),
        )

        nfse = NFSeManaus(
            prestador_cnpj="35710481000103",
            prestador_inscricao_municipal="12345",
            tomador=tomador,
            servico=servico,
        )

        resultado = manager.enviar_lote_rps([nfse])

        assert "xml_envio" in resultado
        assert resultado["quantidade"] == 1
        assert resultado["status"] == "pendente"

    def test_consultar_nfse_por_rps(self, manager):
        """Testa consulta de NFS-e por RPS."""
        resultado = manager.consultar_nfse_por_rps("123456")

        assert "xml_consulta" in resultado
        assert resultado["numero_rps"] == "123456"
        assert "<ConsultarNfseRpsEnvio" in resultado["xml_consulta"]

    def test_cancelar_nfse(self, manager):
        """Testa cancelamento de NFS-e."""
        resultado = manager.cancelar_nfse("789012", "1")

        assert "xml_cancelamento" in resultado
        assert resultado["numero_nfse"] == "789012"
        assert resultado["codigo_cancelamento"] == "1"

    def test_montar_envelope_soap(self, manager):
        """Testa montagem de envelope SOAP."""
        envelope = manager._montar_envelope_soap(
            "RecepcionarLoteRps",
            "<cabecalho>test</cabecalho>",
            "<dados>test</dados>"
        )

        assert "soap:Envelope" in envelope
        assert "soap:Body" in envelope
        assert "RecepcionarLoteRps.Execute" in envelope
        assert "<![CDATA[<cabecalho>test</cabecalho>]]>" in envelope

    def test_get_url_producao(self, mock_cert_manager):
        """Testa URL de produção."""
        manager = NFSeManausManager(
            certificate_manager=mock_cert_manager,
            ambiente="producao",
            cnpj="35710481000103",
        )
        assert "nfse-prd.manaus.am.gov.br" in manager.url_base

    def test_get_url_homologacao(self, mock_cert_manager):
        """Testa URL de homologação."""
        manager = NFSeManausManager(
            certificate_manager=mock_cert_manager,
            ambiente="homologacao",
            cnpj="35710481000103",
        )
        assert "nfse-hml.manaus.am.gov.br" in manager.url_base


class TestNFSeManausService:
    """Testes para NFSeManausService."""

    @pytest.fixture
    def service(self):
        """Cria instância do service para testes."""
        with patch.dict('os.environ', {
            'NFSE_MANAUS_CNPJ': '35710481000103',
            'NFSE_MANAUS_USUARIO': '35710481000103',
            'NFSE_MANAUS_SENHA': 'senha123',
            'NFSE_MANAUS_ENVIRONMENT': 'homologacao',
            'CERTIFICATE_PATH': '/nonexistent/cert.pfx',
            'CERTIFICATE_PASSWORD': '',
        }):
            return NFSeManausService()

    def test_service_init(self, service):
        """Testa inicialização do service."""
        assert service.cnpj == "35710481000103"
        assert service.ambiente == "homologacao"

    def test_emitir_nfse_simulado(self, service):
        """Testa emissão de NFS-e em modo simulado."""
        tomador_data = {
            "cpf_cnpj": "12345678901234",
            "razao_social": "Empresa Teste",
            "endereco": "Rua Teste",
            "numero": "100",
            "bairro": "Centro",
            "cidade": "Manaus",
            "uf": "AM",
            "cep": "69000000",
        }

        servico_data = {
            "codigo_servico": "11.02",
            "discriminacao": "Serviços de vigilância",
            "valor_servicos": "1000.00",
            "aliquota_iss": "0.05",
        }

        resultado = service.emitir_nfse(tomador_data, servico_data)

        assert resultado["status"] == "simulado"
        assert "xml_envio" in resultado

    def test_validar_conexao(self, service):
        """Testa validação de conexão."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            resultado = service.validar_conexao()

            assert resultado["ambiente"] == "homologacao"
            assert resultado["cnpj"] == "35710481000103"
            assert resultado["conexao_http"] is True


class TestNFSeEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI

        # Criar app de teste
        app = FastAPI()

        # Importar e incluir router
        from modules.government_integrations.controllers.nfse_manaus_controller import router
        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_listar_codigos_servico(self, client):
        """Testa endpoint de listagem de códigos de serviço."""
        response = client.get("/api/v1/government/nfse-manaus/codigos-servico")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "codigos" in data["data"]
        assert len(data["data"]["codigos"]) > 0

        # Verificar código 11.02 (vigilância)
        codigos = {c["codigo"]: c for c in data["data"]["codigos"]}
        assert "11.02" in codigos
        assert "vigilância" in codigos["11.02"]["descricao"].lower()

    def test_validar_conexao_endpoint(self, client):
        """Testa endpoint de validação de conexão."""
        with patch('modules.government_integrations.services.nfse_manaus_service.NFSeManausService.validar_conexao') as mock:
            mock.return_value = {
                "ambiente": "homologacao",
                "cnpj": "35710481000103",
                "url_base": "https://nfse-hml.manaus.am.gov.br",
                "conexao_http": True,
                "http_status": 200,
                "certificado_configurado": False,
            }

            response = client.get("/api/v1/government/nfse-manaus/status")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["ambiente"] == "homologacao"

    def test_emitir_nfse_endpoint(self, client):
        """Testa endpoint de emissão de NFS-e."""
        with patch('modules.government_integrations.services.nfse_manaus_service.NFSeManausService.emitir_nfse') as mock:
            mock.return_value = {
                "numero_rps": "123456",
                "numero_lote": "789012",
                "status": "simulado",
                "xml_envio": "<xml>test</xml>",
            }

            payload = {
                "tomador": {
                    "cpf_cnpj": "12345678901234",
                    "razao_social": "Empresa Teste LTDA",
                    "endereco": "Av. Eduardo Ribeiro",
                    "numero": "1000",
                    "bairro": "Centro",
                    "cidade": "Manaus",
                    "uf": "AM",
                    "cep": "69010001",
                },
                "servico": {
                    "codigo_servico": "11.02",
                    "discriminacao": "Serviços de vigilância patrimonial conforme contrato",
                    "valor_servicos": "15000.00",
                    "aliquota_iss": "0.05",
                },
                "competencia": "2026-01",
                "optante_simples": True,
            }

            response = client.post(
                "/api/v1/government/nfse-manaus/emitir",
                json=payload
            )

            assert response.status_code == 202
            data = response.json()
            assert data["success"] is True
            assert "NFS-e" in data["message"]

    def test_cancelar_nfse_endpoint(self, client):
        """Testa endpoint de cancelamento de NFS-e."""
        with patch('modules.government_integrations.services.nfse_manaus_service.NFSeManausService.cancelar_nfse') as mock:
            mock.return_value = {
                "status": "simulado",
                "numero_nfse": "123456",
            }

            payload = {
                "numero_nfse": "123456",
                "codigo_cancelamento": "1",
                "motivo": "Erro no valor",
            }

            response = client.post(
                "/api/v1/government/nfse-manaus/cancelar",
                json=payload
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


class TestIntegracaoReal:
    """
    Testes de integração real com WebService.

    ATENÇÃO: Estes testes fazem requisições reais ao WebService.
    Usar apenas em ambiente de homologação.
    """

    @pytest.mark.skip(reason="Requer certificado digital configurado")
    def test_conexao_webservice_producao(self):
        """Testa conexão real com WebService de produção."""
        import requests

        url = "https://nfse-prd.manaus.am.gov.br/nfse/servlet/arecepcionarloterps?wsdl"
        response = requests.get(url, timeout=10)

        assert response.status_code == 200
        assert "wsdl" in response.text.lower()

    @pytest.mark.skip(reason="Requer certificado digital configurado")
    def test_conexao_webservice_homologacao(self):
        """Testa conexão real com WebService de homologação."""
        import requests

        url = "https://nfse-hml.manaus.am.gov.br/nfse/servlet/arecepcionarloterps?wsdl"
        response = requests.get(url, timeout=10)

        assert response.status_code == 200
