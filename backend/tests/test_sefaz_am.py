"""
Testes para modulo SEFAZ-AM (Amazonas).

Testa:
- Configuracao de endpoints
- Criacao de envelopes SOAP
- Parse de respostas XML
- Client e Service
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.government_integrations.core.sefaz_am import (
    ENDPOINT_DFE_NACIONAL,
    ENDPOINTS_SEFAZ_AM,
    AmbienteSEFAZ,
    EndpointConfig,
    InformacaoCadastral,
    ResultadoAutorizacao,
    ResultadoConsulta,
    ResultadoEvento,
    SefazAMClient,
    SefazAMService,
    StatusServico,
    TipoEvento,
)

# =============================================================================
# TESTES DE CONFIGURACAO
# =============================================================================


class TestEndpointsConfig:
    """Testes de configuracao de endpoints."""

    def test_todos_endpoints_definidos(self):
        """Verifica se todos os 7 endpoints estao definidos."""
        endpoints_esperados = [
            "NfeStatusServico",
            "NfeAutorizacao",
            "NfeRetAutorizacao",
            "NfeConsulta",
            "NfeInutilizacao",
            "RecepcaoEvento",
            "CadConsultaCadastro",
        ]

        for endpoint in endpoints_esperados:
            assert endpoint in ENDPOINTS_SEFAZ_AM, f"Endpoint {endpoint} nao encontrado"

    def test_endpoint_tem_urls_producao_e_homologacao(self):
        """Cada endpoint deve ter URL de producao e homologacao."""
        for nome, config in ENDPOINTS_SEFAZ_AM.items():
            assert config.producao, f"{nome}: URL producao nao definida"
            assert config.homologacao, f"{nome}: URL homologacao nao definida"
            assert "sefaz.am.gov.br" in config.producao, f"{nome}: URL producao invalida"
            assert "sefaz.am.gov.br" in config.homologacao, f"{nome}: URL homologacao invalida"

    def test_endpoint_tem_soap_action(self):
        """Cada endpoint deve ter SOAP Action definida."""
        for nome, config in ENDPOINTS_SEFAZ_AM.items():
            assert config.soap_action, f"{nome}: SOAP Action nao definida"
            assert "portalfiscal" in config.soap_action, f"{nome}: SOAP Action invalida"

    def test_endpoint_dfe_nacional(self):
        """Verifica endpoint DF-e Nacional para notas destinadas."""
        assert ENDPOINT_DFE_NACIONAL.producao
        assert ENDPOINT_DFE_NACIONAL.homologacao
        assert "nfe.fazenda.gov.br" in ENDPOINT_DFE_NACIONAL.producao
        assert ENDPOINT_DFE_NACIONAL.versao == "1.01"


class TestEnums:
    """Testes de enums."""

    def test_ambiente_sefaz(self):
        """Verifica enum AmbienteSEFAZ."""
        assert AmbienteSEFAZ.PRODUCAO.value == "1"
        assert AmbienteSEFAZ.HOMOLOGACAO.value == "2"

    def test_tipo_evento(self):
        """Verifica enum TipoEvento."""
        assert TipoEvento.CANCELAMENTO.value == "110111"
        assert TipoEvento.CARTA_CORRECAO.value == "110110"
        assert TipoEvento.CIENCIA_OPERACAO.value == "210210"

    def test_status_servico(self):
        """Verifica enum StatusServico."""
        assert StatusServico.OPERANDO.value == "107"
        assert StatusServico.PARALISADO_TEMPORARIAMENTE.value == "108"


# =============================================================================
# TESTES DO CLIENT
# =============================================================================


class TestSefazAMClient:
    """Testes do client SEFAZ-AM."""

    @pytest.fixture
    def mock_cert_manager(self):
        """Mock do CertificateManager."""
        manager = MagicMock()
        manager.get_certificate_for_request.return_value = ("cert.pem", "key.pem")
        return manager

    @pytest.fixture
    def client(self, mock_cert_manager):
        """Cria cliente para testes."""
        return SefazAMClient(
            certificate_manager=mock_cert_manager,
            ambiente=AmbienteSEFAZ.HOMOLOGACAO,
            timeout=10,
        )

    def test_criacao_client(self, client):
        """Testa criacao do client."""
        assert client.ambiente == AmbienteSEFAZ.HOMOLOGACAO
        assert client.timeout == 10
        assert client.UF_CODIGO == "13"
        assert client.UF_SIGLA == "AM"

    def test_get_url_producao(self, mock_cert_manager):
        """Testa obtencao de URL em producao."""
        client = SefazAMClient(mock_cert_manager, AmbienteSEFAZ.PRODUCAO)
        url = client._get_url("NfeStatusServico")
        assert "nfe.sefaz.am.gov.br" in url
        assert "homnfe" not in url

    def test_get_url_homologacao(self, client):
        """Testa obtencao de URL em homologacao."""
        url = client._get_url("NfeStatusServico")
        assert "homnfe.sefaz.am.gov.br" in url

    def test_get_url_servico_invalido(self, client):
        """Testa erro com servico invalido."""
        with pytest.raises(ValueError, match="desconhecido"):
            client._get_url("ServicoInexistente")

    def test_criar_envelope_soap(self, client):
        """Testa criacao de envelope SOAP."""
        body = "<teste>conteudo</teste>"
        envelope = client._criar_envelope_soap(body)

        assert "soap12:Envelope" in envelope
        assert "soap12:Body" in envelope
        assert "<teste>conteudo</teste>" in envelope


class TestClientParsers:
    """Testes dos parsers de resposta."""

    @pytest.fixture
    def client(self):
        """Cria cliente mock."""
        mock_manager = MagicMock()
        return SefazAMClient(mock_manager, AmbienteSEFAZ.HOMOLOGACAO)

    def test_parse_status_servico_ok(self, client):
        """Testa parse de status OK."""
        xml = """<?xml version="1.0"?>
        <root>
            <retConsStatServ>
                <cStat>107</cStat>
                <xMotivo>Servico em Operacao</xMotivo>
                <dhRecbto>2026-01-16T10:00:00</dhRecbto>
                <tMed>1</tMed>
            </retConsStatServ>
        </root>
        """
        resultado = client._parse_status_servico(xml, 100.0)

        assert resultado.sucesso is True
        assert resultado.codigo == "107"
        assert "Operacao" in resultado.mensagem
        assert resultado.tempo_resposta_ms == 100.0

    def test_parse_status_servico_erro(self, client):
        """Testa parse de status com erro."""
        xml = """<?xml version="1.0"?>
        <root>
            <retConsStatServ>
                <cStat>109</cStat>
                <xMotivo>Servico Paralisado</xMotivo>
            </retConsStatServ>
        </root>
        """
        resultado = client._parse_status_servico(xml, 50.0)

        assert resultado.sucesso is False
        assert resultado.codigo == "109"

    def test_parse_consulta_nfe(self, client):
        """Testa parse de consulta NF-e."""
        xml = """<?xml version="1.0"?>
        <root>
            <retConsSitNFe>
                <cStat>100</cStat>
                <xMotivo>Autorizado o uso da NF-e</xMotivo>
                <protNFe>
                    <infProt>
                        <chNFe>13260100000000000190550010000000011000000017</chNFe>
                        <nProt>113260000000001</nProt>
                        <dhRecbto>2026-01-16T10:00:00</dhRecbto>
                        <cStat>100</cStat>
                    </infProt>
                </protNFe>
            </retConsSitNFe>
        </root>
        """
        resultado = client._parse_consulta_nfe(xml, 200.0)

        assert resultado.sucesso is True
        assert resultado.codigo == "100"
        assert resultado.dados["chave_acesso"] == "13260100000000000190550010000000011000000017"
        assert resultado.dados["protocolo"] == "113260000000001"

    def test_parse_inutilizacao(self, client):
        """Testa parse de inutilizacao."""
        xml = """<?xml version="1.0"?>
        <root>
            <retInutNFe>
                <infInut>
                    <cStat>102</cStat>
                    <xMotivo>Inutilizacao homologada</xMotivo>
                    <nProt>113260000000002</nProt>
                    <dhRecbto>2026-01-16T10:00:00</dhRecbto>
                </infInut>
            </retInutNFe>
        </root>
        """
        resultado = client._parse_inutilizacao(xml, 150.0)

        assert resultado.sucesso is True
        assert resultado.codigo == "102"
        assert resultado.dados["protocolo"] == "113260000000002"

    def test_parse_cadastro(self, client):
        """Testa parse de consulta cadastral."""
        xml = """<?xml version="1.0"?>
        <root>
            <retConsCad>
                <infCons>
                    <cStat>111</cStat>
                    <xMotivo>Uma ocorrencia encontrada</xMotivo>
                    <infCad>
                        <CNPJ>12345678000190</CNPJ>
                        <IE>123456789</IE>
                        <xNome>EMPRESA TESTE</xNome>
                        <xFant>TESTE</xFant>
                        <cSit>1</cSit>
                        <ender>
                            <xLgr>RUA TESTE</xLgr>
                            <nro>100</nro>
                            <xBairro>CENTRO</xBairro>
                            <cMun>1302603</cMun>
                            <xMun>MANAUS</xMun>
                            <CEP>69000000</CEP>
                        </ender>
                    </infCad>
                </infCons>
            </retConsCad>
        </root>
        """
        resultado = client._parse_cadastro(xml, 300.0)

        assert resultado.sucesso is True
        assert resultado.codigo == "111"
        assert len(resultado.dados["contribuintes"]) == 1

        contribuinte = resultado.dados["contribuintes"][0]
        assert contribuinte["cnpj"] == "12345678000190"
        assert contribuinte["razao_social"] == "EMPRESA TESTE"
        assert contribuinte["endereco"]["municipio"] == "MANAUS"


# =============================================================================
# TESTES DO SERVICE
# =============================================================================


class TestSefazAMService:
    """Testes do service SEFAZ-AM."""

    @pytest.fixture
    def mock_db(self):
        """Mock da sessao do banco."""
        return MagicMock()

    @pytest.fixture
    def mock_cert_manager(self):
        """Mock do CertificateManager."""
        manager = MagicMock()
        return manager

    @pytest.fixture
    def service(self, mock_db, mock_cert_manager):
        """Cria service para testes."""
        return SefazAMService(mock_db, mock_cert_manager)

    @pytest.mark.asyncio
    async def test_verificar_status(self, service):
        """Testa verificacao de status."""
        with patch.object(
            service,
            "_get_client",
            new_callable=AsyncMock,
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.consultar_status_servico.return_value = ResultadoConsulta(
                sucesso=True,
                codigo="107",
                mensagem="Servico em Operacao",
                tempo_resposta_ms=100.0,
                dados={"ambiente": "2"},
            )
            mock_get_client.return_value = mock_client

            resultado = await service.verificar_status()

            assert resultado["disponivel"] is True
            assert resultado["codigo"] == "107"

    @pytest.mark.asyncio
    async def test_consultar_nfe(self, service):
        """Testa consulta de NF-e."""
        chave = "13260100000000000190550010000000011000000017"

        with patch.object(
            service,
            "_get_client",
            new_callable=AsyncMock,
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_client.consultar_nfe.return_value = ResultadoConsulta(
                sucesso=True,
                codigo="100",
                mensagem="Autorizado",
                dados={"chave_acesso": chave, "protocolo": "123"},
            )
            mock_get_client.return_value = mock_client

            resultado = await service.consultar_nfe(chave)

            assert resultado["sucesso"] is True
            assert resultado["dados"]["chave_acesso"] == chave


# =============================================================================
# TESTES DE DATA CLASSES
# =============================================================================


class TestResultadoConsulta:
    """Testes da dataclass ResultadoConsulta."""

    def test_criacao_sucesso(self):
        """Testa criacao com sucesso."""
        resultado = ResultadoConsulta(
            sucesso=True,
            codigo="107",
            mensagem="OK",
            tempo_resposta_ms=100.0,
        )
        assert resultado.sucesso is True
        assert resultado.dados is None

    def test_criacao_com_dados(self):
        """Testa criacao com dados."""
        resultado = ResultadoConsulta(
            sucesso=True,
            codigo="100",
            mensagem="Autorizado",
            dados={"chave": "123", "protocolo": "456"},
            xml_retorno="<xml>...</xml>",
        )
        assert resultado.dados["chave"] == "123"
        assert resultado.xml_retorno is not None


class TestInformacaoCadastral:
    """Testes da dataclass InformacaoCadastral."""

    def test_criacao_pj(self):
        """Testa criacao para pessoa juridica."""
        info = InformacaoCadastral(
            cnpj="12345678000190",
            inscricao_estadual="123456789",
            razao_social="EMPRESA TESTE",
        )
        assert info.cnpj == "12345678000190"
        assert info.cpf is None

    def test_criacao_pf(self):
        """Testa criacao para pessoa fisica."""
        info = InformacaoCadastral(
            cpf="12345678901",
            inscricao_estadual="987654321",
            razao_social="PESSOA TESTE",
        )
        assert info.cpf == "12345678901"
        assert info.cnpj is None


# =============================================================================
# TESTES DE INTEGRACAO (MOCK)
# =============================================================================


class TestIntegracaoMock:
    """Testes de integracao com mocks."""

    @pytest.fixture
    def client_com_mock_http(self):
        """Client com HTTP mockado."""
        mock_manager = MagicMock()
        mock_manager.get_certificate_for_request.return_value = ("cert", "key")

        client = SefazAMClient(mock_manager, AmbienteSEFAZ.HOMOLOGACAO)
        return client

    @pytest.mark.asyncio
    async def test_fluxo_consulta_status(self, client_com_mock_http):
        """Testa fluxo completo de consulta de status."""
        # XML sem namespace para facilitar parse (namespace é removido pelo parser)
        xml_resposta = """<?xml version="1.0"?>
        <Envelope>
            <Body>
                <nfeResultMsg>
                    <retConsStatServ versao="4.00">
                        <tpAmb>2</tpAmb>
                        <cStat>107</cStat>
                        <xMotivo>Servico em Operacao</xMotivo>
                        <cUF>13</cUF>
                        <dhRecbto>2026-01-16T10:00:00-04:00</dhRecbto>
                        <tMed>1</tMed>
                    </retConsStatServ>
                </nfeResultMsg>
            </Body>
        </Envelope>
        """

        with patch.object(
            client_com_mock_http,
            "_enviar_requisicao",
            new_callable=AsyncMock,
            return_value=(200, xml_resposta, 150.0),
        ):
            resultado = await client_com_mock_http.consultar_status_servico()

            assert resultado.sucesso is True
            assert resultado.codigo == "107"
            assert resultado.tempo_resposta_ms == 150.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
