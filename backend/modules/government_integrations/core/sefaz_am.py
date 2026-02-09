"""
Module: SEFAZ-AM (Amazonas)
Description: Integracao especifica com SEFAZ do Amazonas para NF-e/NFC-e.
             Implementa todos os 7 webservices oficiais.

Endpoints SEFAZ-AM (Producao):
- NfeStatusServico4: https://nfe.sefaz.am.gov.br/services2/services/NfeStatusServico4
- NfeAutorizacao4: https://nfe.sefaz.am.gov.br/services2/services/NfeAutorizacao4
- NfeRetAutorizacao4: https://nfe.sefaz.am.gov.br/services2/services/NfeRetAutorizacao4
- NfeConsulta4: https://nfe.sefaz.am.gov.br/services2/services/NfeConsulta4
- NfeInutilizacao4: https://nfe.sefaz.am.gov.br/services2/services/NfeInutilizacao4
- RecepcaoEvento4: https://nfe.sefaz.am.gov.br/services2/services/RecepcaoEvento4
- CadConsultaCadastro4: https://nfe.sefaz.am.gov.br/services2/services/CadConsultaCadastro4

Author: Claude AI + Human Developer
Date: 2026-01-16
"""

import logging
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from typing import Any

import defusedxml.ElementTree as ET  # noqa: N817
import httpx

from .certificate_manager import CertificateManager
from .xml_signer import NFEXMLSigner, SignatureType

logger = logging.getLogger(__name__)


class AmbienteSEFAZ(StrEnum):
    """Ambiente SEFAZ."""

    PRODUCAO = "1"
    HOMOLOGACAO = "2"


class TipoEvento(StrEnum):
    """Tipos de eventos NF-e."""

    CANCELAMENTO = "110111"
    CARTA_CORRECAO = "110110"
    CIENCIA_OPERACAO = "210210"
    CONFIRMACAO_OPERACAO = "210200"
    DESCONHECIMENTO_OPERACAO = "210220"
    OPERACAO_NAO_REALIZADA = "210240"


class StatusServico(StrEnum):
    """Status do servico SEFAZ."""

    OPERANDO = "107"
    PARALISADO_TEMPORARIAMENTE = "108"
    PARALISADO_SEM_PREVISAO = "109"


@dataclass
class EndpointConfig:
    """Configuracao de endpoint SEFAZ-AM."""

    producao: str
    homologacao: str
    versao: str = "4.00"
    metodo: str = "POST"
    soap_action: str | None = None


# Endpoints oficiais SEFAZ-AM conforme documentacao
ENDPOINTS_SEFAZ_AM: dict[str, EndpointConfig] = {
    "NfeStatusServico": EndpointConfig(
        producao="https://nfe.sefaz.am.gov.br/services2/services/NfeStatusServico4",
        homologacao="https://homnfe.sefaz.am.gov.br/services2/services/NfeStatusServico4",
        soap_action="http://www.portalfiscal.inf.br/nfe/wsdl/NFeStatusServico4/nfeStatusServicoNF",
    ),
    "NfeAutorizacao": EndpointConfig(
        producao="https://nfe.sefaz.am.gov.br/services2/services/NfeAutorizacao4",
        homologacao="https://homnfe.sefaz.am.gov.br/services2/services/NfeAutorizacao4",
        soap_action="http://www.portalfiscal.inf.br/nfe/wsdl/NFeAutorizacao4/nfeAutorizacaoLote",
    ),
    "NfeRetAutorizacao": EndpointConfig(
        producao="https://nfe.sefaz.am.gov.br/services2/services/NfeRetAutorizacao4",
        homologacao="https://homnfe.sefaz.am.gov.br/services2/services/NfeRetAutorizacao4",
        soap_action="http://www.portalfiscal.inf.br/nfe/wsdl/NFeRetAutorizacao4/nfeRetAutorizacaoLote",
    ),
    "NfeConsulta": EndpointConfig(
        producao="https://nfe.sefaz.am.gov.br/services2/services/NfeConsulta4",
        homologacao="https://homnfe.sefaz.am.gov.br/services2/services/NfeConsulta4",
        soap_action="http://www.portalfiscal.inf.br/nfe/wsdl/NFeConsultaProtocolo4/nfeConsultaNF",
    ),
    "NfeInutilizacao": EndpointConfig(
        producao="https://nfe.sefaz.am.gov.br/services2/services/NfeInutilizacao4",
        homologacao="https://homnfe.sefaz.am.gov.br/services2/services/NfeInutilizacao4",
        soap_action="http://www.portalfiscal.inf.br/nfe/wsdl/NFeInutilizacao4/nfeInutilizacaoNF",
    ),
    "RecepcaoEvento": EndpointConfig(
        producao="https://nfe.sefaz.am.gov.br/services2/services/RecepcaoEvento4",
        homologacao="https://homnfe.sefaz.am.gov.br/services2/services/RecepcaoEvento4",
        soap_action="http://www.portalfiscal.inf.br/nfe/wsdl/NFeRecepcaoEvento4/nfeRecepcaoEvento",
    ),
    "CadConsultaCadastro": EndpointConfig(
        producao="https://nfe.sefaz.am.gov.br/services2/services/CadConsultaCadastro4",
        homologacao="https://homnfe.sefaz.am.gov.br/services2/services/CadConsultaCadastro4",
        soap_action="http://www.portalfiscal.inf.br/nfe/wsdl/CadConsultaCadastro4/consultaCadastro",
    ),
}

# Endpoint Nacional para DF-e (notas destinadas)
ENDPOINT_DFE_NACIONAL = EndpointConfig(
    producao="https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx",
    homologacao="https://hom1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx",
    versao="1.01",
    soap_action="http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe/nfeDistDFeInteresse",
)

# Namespaces XML
NS_NFE = "http://www.portalfiscal.inf.br/nfe"
NS_SOAP = "http://www.w3.org/2003/05/soap-envelope"
NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS_XSD = "http://www.w3.org/2001/XMLSchema"


@dataclass
class ResultadoConsulta:
    """Resultado de consulta SEFAZ."""

    sucesso: bool
    codigo: str
    mensagem: str
    dados: dict[str, Any] | None = None
    xml_retorno: str | None = None
    tempo_resposta_ms: float = 0


@dataclass
class ResultadoAutorizacao:
    """Resultado de autorizacao NF-e."""

    sucesso: bool
    codigo: str
    mensagem: str
    protocolo: str | None = None
    chave_acesso: str | None = None
    data_autorizacao: datetime | None = None
    xml_protocolo: str | None = None
    numero_recibo: str | None = None


@dataclass
class ResultadoEvento:
    """Resultado de evento NF-e."""

    sucesso: bool
    codigo: str
    mensagem: str
    protocolo: str | None = None
    tipo_evento: str | None = None
    sequencia: int | None = None
    data_registro: datetime | None = None
    xml_evento: str | None = None


@dataclass
class InformacaoCadastral:
    """Informacoes cadastrais de contribuinte."""

    cnpj: str | None = None
    cpf: str | None = None
    inscricao_estadual: str = ""
    razao_social: str = ""
    nome_fantasia: str | None = None
    situacao: str = ""
    data_situacao: date | None = None
    regime_tributario: str | None = None
    cnae_principal: str | None = None
    endereco: dict[str, Any] | None = None


class SefazAMClient:
    """Cliente para comunicacao com SEFAZ-AM."""

    UF_CODIGO = "13"  # Codigo IBGE do Amazonas
    UF_SIGLA = "AM"

    def __init__(
        self,
        certificate_manager: CertificateManager,
        ambiente: AmbienteSEFAZ = AmbienteSEFAZ.PRODUCAO,
        timeout: int = 30,
    ):
        """
        Inicializa o cliente SEFAZ-AM.

        Args:
            certificate_manager: Gerenciador de certificados
            ambiente: Ambiente (producao/homologacao)
            timeout: Timeout em segundos
        """
        self.certificate_manager = certificate_manager
        self.ambiente = ambiente
        self.timeout = timeout
        self.xml_signer = NFEXMLSigner(certificate_manager)
        self._http_client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Obtem cliente HTTP com certificado."""
        if self._http_client is None or self._http_client.is_closed:
            cert_info = self.certificate_manager.get_certificate_for_request()
            # SEFAZ usa certificados ICP-Brasil que podem não estar no bundle padrão
            # Em produção, configurar CA bundle ICP-Brasil específico
            self._http_client = httpx.AsyncClient(
                cert=cert_info,
                timeout=httpx.Timeout(self.timeout),
                verify=False,  # noqa: S501 # TODO: Configurar CA bundle ICP-Brasil
            )
        return self._http_client

    async def close(self):
        """Fecha o cliente HTTP."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    def _get_url(self, servico: str) -> str:
        """Obtem URL do servico baseado no ambiente."""
        config = ENDPOINTS_SEFAZ_AM.get(servico)
        if not config:
            raise ValueError(f"Servico desconhecido: {servico}")

        return config.producao if self.ambiente == AmbienteSEFAZ.PRODUCAO else config.homologacao

    def _get_soap_action(self, servico: str) -> str:
        """Obtem SOAP Action do servico."""
        config = ENDPOINTS_SEFAZ_AM.get(servico)
        return config.soap_action if config else ""

    def _criar_envelope_soap(self, body_content: str) -> str:
        """Cria envelope SOAP para requisicao."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:soap12="{NS_SOAP}"
                 xmlns:xsi="{NS_XSI}"
                 xmlns:xsd="{NS_XSD}">
    <soap12:Body>
        {body_content}
    </soap12:Body>
</soap12:Envelope>'''

    async def _enviar_requisicao(
        self,
        servico: str,
        xml_body: str,
    ) -> tuple[int, str, float]:
        """
        Envia requisicao SOAP para SEFAZ.

        Returns:
            Tuple com (status_code, response_text, tempo_ms)
        """
        url = self._get_url(servico)
        soap_action = self._get_soap_action(servico)

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": soap_action,
        }

        envelope = self._criar_envelope_soap(xml_body)

        inicio = datetime.now()
        try:
            client = await self._get_client()
            response = await client.post(url, content=envelope, headers=headers)
            tempo_ms = (datetime.now() - inicio).total_seconds() * 1000

            logger.info(f"[SEFAZ-AM] {servico} - Status: {response.status_code}, Tempo: {tempo_ms:.0f}ms")

            return response.status_code, response.text, tempo_ms

        except httpx.TimeoutException as e:
            tempo_ms = (datetime.now() - inicio).total_seconds() * 1000
            logger.error(f"[SEFAZ-AM] Timeout {servico}: {e}")
            raise TimeoutError(f"Timeout na comunicacao com SEFAZ-AM: {servico}")

        except Exception as e:
            tempo_ms = (datetime.now() - inicio).total_seconds() * 1000
            logger.error(f"[SEFAZ-AM] Erro {servico}: {e}")
            raise

    # =========================================================================
    # 1. CONSULTA STATUS DO SERVICO
    # =========================================================================

    async def consultar_status_servico(self) -> ResultadoConsulta:
        """
        Consulta status do servico SEFAZ-AM.

        Endpoint: NfeStatusServico4
        Versao: 4.00

        Returns:
            ResultadoConsulta com status do servico
        """
        xml_body = f'''<nfeDadosMsg xmlns="{NS_NFE}">
            <consStatServ xmlns="{NS_NFE}" versao="4.00">
                <tpAmb>{self.ambiente.value}</tpAmb>
                <cUF>{self.UF_CODIGO}</cUF>
                <xServ>STATUS</xServ>
            </consStatServ>
        </nfeDadosMsg>'''

        try:
            status_code, response_text, tempo_ms = await self._enviar_requisicao("NfeStatusServico", xml_body)

            if status_code == 200:
                return self._parse_status_servico(response_text, tempo_ms)
            else:
                return ResultadoConsulta(
                    sucesso=False,
                    codigo=str(status_code),
                    mensagem=f"Erro HTTP: {status_code}",
                    tempo_resposta_ms=tempo_ms,
                )

        except Exception as e:
            logger.error(f"[SEFAZ-AM] Erro consulta status: {e}")
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem=str(e),
            )

    def _parse_status_servico(self, xml_response: str, tempo_ms: float) -> ResultadoConsulta:
        """Parse da resposta de status do servico."""
        try:
            # Remover todos os namespaces para facilitar parse
            import re

            xml_clean = re.sub(r'\sxmlns[^"]*"[^"]*"', "", xml_response)
            xml_clean = re.sub(r"<(\w+):", r"<", xml_clean)
            xml_clean = re.sub(r"</(\w+):", r"</", xml_clean)
            root = ET.fromstring(xml_clean)

            # Buscar retConsStatServ
            ret = root.find(".//retConsStatServ")
            if ret is None:
                return ResultadoConsulta(
                    sucesso=False,
                    codigo="999",
                    mensagem="Resposta invalida - retConsStatServ nao encontrado",
                    xml_retorno=xml_response,
                    tempo_resposta_ms=tempo_ms,
                )

            cstat = ret.findtext("cStat", "")
            xmotivo = ret.findtext("xMotivo", "")
            dhrecbto = ret.findtext("dhRecbto", "")
            tmed = ret.findtext("tMed", "")

            sucesso = cstat == StatusServico.OPERANDO.value

            return ResultadoConsulta(
                sucesso=sucesso,
                codigo=cstat,
                mensagem=xmotivo,
                dados={
                    "data_hora_recebimento": dhrecbto,
                    "tempo_medio_resposta": tmed,
                    "ambiente": self.ambiente.value,
                    "uf": self.UF_SIGLA,
                },
                xml_retorno=xml_response,
                tempo_resposta_ms=tempo_ms,
            )

        except ET.ParseError as e:
            logger.error(f"[SEFAZ-AM] Erro parse XML status: {e}")
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem=f"Erro parse XML: {e}",
                xml_retorno=xml_response,
                tempo_resposta_ms=tempo_ms,
            )

    # =========================================================================
    # 2. AUTORIZACAO DE NF-e (LOTE)
    # =========================================================================

    async def autorizar_nfe(
        self,
        xml_nfe_assinado: str,
        id_lote: str,
        sincrono: bool = True,
    ) -> ResultadoAutorizacao:
        """
        Envia NF-e para autorizacao.

        Endpoint: NfeAutorizacao4
        Versao: 4.00

        Args:
            xml_nfe_assinado: XML da NF-e ja assinado
            id_lote: Identificador do lote
            sincrono: Se True, aguarda processamento sincrono

        Returns:
            ResultadoAutorizacao com protocolo
        """
        ind_sinc = "1" if sincrono else "0"

        xml_body = f'''<nfeDadosMsg xmlns="{NS_NFE}">
            <enviNFe xmlns="{NS_NFE}" versao="4.00">
                <idLote>{id_lote}</idLote>
                <indSinc>{ind_sinc}</indSinc>
                {xml_nfe_assinado}
            </enviNFe>
        </nfeDadosMsg>'''

        try:
            status_code, response_text, tempo_ms = await self._enviar_requisicao("NfeAutorizacao", xml_body)

            if status_code == 200:
                return self._parse_autorizacao(response_text)
            else:
                return ResultadoAutorizacao(
                    sucesso=False,
                    codigo=str(status_code),
                    mensagem=f"Erro HTTP: {status_code}",
                )

        except Exception as e:
            logger.error(f"[SEFAZ-AM] Erro autorizacao: {e}")
            return ResultadoAutorizacao(
                sucesso=False,
                codigo="999",
                mensagem=str(e),
            )

    def _parse_autorizacao(self, xml_response: str) -> ResultadoAutorizacao:
        """Parse da resposta de autorizacao."""
        try:
            xml_clean = xml_response.replace('xmlns="http://www.portalfiscal.inf.br/nfe"', "")
            root = ET.fromstring(xml_clean)

            # Verificar se e resposta sincrona (retEnviNFe) ou assincrona (retEnviNFe com recibo)
            ret = root.find(".//retEnviNFe")
            if ret is None:
                return ResultadoAutorizacao(
                    sucesso=False,
                    codigo="999",
                    mensagem="Resposta invalida",
                    xml_protocolo=xml_response,
                )

            cstat = ret.findtext("cStat", "")
            xmotivo = ret.findtext("xMotivo", "")

            # Resposta sincrona - protocolo direto
            prot_nfe = ret.find(".//protNFe/infProt")
            if prot_nfe is not None:
                cstat_prot = prot_nfe.findtext("cStat", "")
                chave = prot_nfe.findtext("chNFe", "")
                protocolo = prot_nfe.findtext("nProt", "")
                dh_recbto = prot_nfe.findtext("dhRecbto", "")

                sucesso = cstat_prot in ["100", "150"]  # 100=Autorizado, 150=Autorizado fora prazo

                return ResultadoAutorizacao(
                    sucesso=sucesso,
                    codigo=cstat_prot,
                    mensagem=prot_nfe.findtext("xMotivo", ""),
                    protocolo=protocolo,
                    chave_acesso=chave,
                    data_autorizacao=self._parse_datetime(dh_recbto),
                    xml_protocolo=xml_response,
                )

            # Resposta assincrona - apenas recibo
            n_rec = ret.findtext("infRec/nRec", "")
            if n_rec:
                return ResultadoAutorizacao(
                    sucesso=True,
                    codigo=cstat,
                    mensagem=xmotivo,
                    numero_recibo=n_rec,
                    xml_protocolo=xml_response,
                )

            return ResultadoAutorizacao(
                sucesso=False,
                codigo=cstat,
                mensagem=xmotivo,
                xml_protocolo=xml_response,
            )

        except ET.ParseError as e:
            logger.error(f"[SEFAZ-AM] Erro parse autorizacao: {e}")
            return ResultadoAutorizacao(
                sucesso=False,
                codigo="999",
                mensagem=f"Erro parse: {e}",
                xml_protocolo=xml_response,
            )

    # =========================================================================
    # 3. CONSULTA RETORNO DE AUTORIZACAO (LOTE ASSINCRONO)
    # =========================================================================

    async def consultar_retorno_autorizacao(
        self,
        numero_recibo: str,
    ) -> ResultadoAutorizacao:
        """
        Consulta retorno de lote assincrono.

        Endpoint: NfeRetAutorizacao4
        Versao: 4.00

        Args:
            numero_recibo: Numero do recibo retornado na autorizacao

        Returns:
            ResultadoAutorizacao com protocolo
        """
        xml_body = f'''<nfeDadosMsg xmlns="{NS_NFE}">
            <consReciNFe xmlns="{NS_NFE}" versao="4.00">
                <tpAmb>{self.ambiente.value}</tpAmb>
                <nRec>{numero_recibo}</nRec>
            </consReciNFe>
        </nfeDadosMsg>'''

        try:
            status_code, response_text, tempo_ms = await self._enviar_requisicao("NfeRetAutorizacao", xml_body)

            if status_code == 200:
                return self._parse_retorno_autorizacao(response_text)
            else:
                return ResultadoAutorizacao(
                    sucesso=False,
                    codigo=str(status_code),
                    mensagem=f"Erro HTTP: {status_code}",
                )

        except Exception as e:
            logger.error(f"[SEFAZ-AM] Erro consulta retorno: {e}")
            return ResultadoAutorizacao(
                sucesso=False,
                codigo="999",
                mensagem=str(e),
            )

    def _parse_retorno_autorizacao(self, xml_response: str) -> ResultadoAutorizacao:
        """Parse da resposta de retorno de autorizacao."""
        try:
            xml_clean = xml_response.replace('xmlns="http://www.portalfiscal.inf.br/nfe"', "")
            root = ET.fromstring(xml_clean)

            ret = root.find(".//retConsReciNFe")
            if ret is None:
                return ResultadoAutorizacao(
                    sucesso=False,
                    codigo="999",
                    mensagem="Resposta invalida",
                    xml_protocolo=xml_response,
                )

            cstat = ret.findtext("cStat", "")

            # Lote ainda em processamento
            if cstat == "105":
                return ResultadoAutorizacao(
                    sucesso=False,
                    codigo=cstat,
                    mensagem="Lote em processamento",
                    xml_protocolo=xml_response,
                )

            # Protocolo disponivel
            prot_nfe = ret.find(".//protNFe/infProt")
            if prot_nfe is not None:
                cstat_prot = prot_nfe.findtext("cStat", "")
                chave = prot_nfe.findtext("chNFe", "")
                protocolo = prot_nfe.findtext("nProt", "")
                dh_recbto = prot_nfe.findtext("dhRecbto", "")

                sucesso = cstat_prot in ["100", "150"]

                return ResultadoAutorizacao(
                    sucesso=sucesso,
                    codigo=cstat_prot,
                    mensagem=prot_nfe.findtext("xMotivo", ""),
                    protocolo=protocolo,
                    chave_acesso=chave,
                    data_autorizacao=self._parse_datetime(dh_recbto),
                    xml_protocolo=xml_response,
                )

            return ResultadoAutorizacao(
                sucesso=False,
                codigo=cstat,
                mensagem=ret.findtext("xMotivo", ""),
                xml_protocolo=xml_response,
            )

        except ET.ParseError as e:
            return ResultadoAutorizacao(
                sucesso=False,
                codigo="999",
                mensagem=f"Erro parse: {e}",
                xml_protocolo=xml_response,
            )

    # =========================================================================
    # 4. CONSULTA NF-e POR CHAVE DE ACESSO
    # =========================================================================

    async def consultar_nfe(self, chave_acesso: str) -> ResultadoConsulta:
        """
        Consulta NF-e por chave de acesso.

        Endpoint: NfeConsulta4
        Versao: 4.00

        Args:
            chave_acesso: Chave de acesso da NF-e (44 digitos)

        Returns:
            ResultadoConsulta com dados da NF-e
        """
        if len(chave_acesso) != 44:
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem="Chave de acesso deve ter 44 digitos",
            )

        xml_body = f'''<nfeDadosMsg xmlns="{NS_NFE}">
            <consSitNFe xmlns="{NS_NFE}" versao="4.00">
                <tpAmb>{self.ambiente.value}</tpAmb>
                <xServ>CONSULTAR</xServ>
                <chNFe>{chave_acesso}</chNFe>
            </consSitNFe>
        </nfeDadosMsg>'''

        try:
            status_code, response_text, tempo_ms = await self._enviar_requisicao("NfeConsulta", xml_body)

            if status_code == 200:
                return self._parse_consulta_nfe(response_text, tempo_ms)
            else:
                return ResultadoConsulta(
                    sucesso=False,
                    codigo=str(status_code),
                    mensagem=f"Erro HTTP: {status_code}",
                    tempo_resposta_ms=tempo_ms,
                )

        except Exception as e:
            logger.error(f"[SEFAZ-AM] Erro consulta NF-e: {e}")
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem=str(e),
            )

    def _parse_consulta_nfe(self, xml_response: str, tempo_ms: float) -> ResultadoConsulta:
        """Parse da resposta de consulta NF-e."""
        try:
            xml_clean = xml_response.replace('xmlns="http://www.portalfiscal.inf.br/nfe"', "")
            root = ET.fromstring(xml_clean)

            ret = root.find(".//retConsSitNFe")
            if ret is None:
                return ResultadoConsulta(
                    sucesso=False,
                    codigo="999",
                    mensagem="Resposta invalida",
                    xml_retorno=xml_response,
                    tempo_resposta_ms=tempo_ms,
                )

            cstat = ret.findtext("cStat", "")
            xmotivo = ret.findtext("xMotivo", "")

            # Extrair dados do protocolo
            prot_nfe = ret.find(".//protNFe/infProt")
            dados = {}

            if prot_nfe is not None:
                dados = {
                    "chave_acesso": prot_nfe.findtext("chNFe", ""),
                    "protocolo": prot_nfe.findtext("nProt", ""),
                    "data_autorizacao": prot_nfe.findtext("dhRecbto", ""),
                    "digest_value": prot_nfe.findtext("digVal", ""),
                    "status_protocolo": prot_nfe.findtext("cStat", ""),
                }

            # Extrair eventos associados
            eventos = []
            for proc_evento in ret.findall(".//procEventoNFe"):
                inf_evento = proc_evento.find(".//infEvento")
                if inf_evento is not None:
                    eventos.append(
                        {
                            "tipo": inf_evento.findtext("tpEvento", ""),
                            "sequencia": inf_evento.findtext("nSeqEvento", ""),
                            "data": inf_evento.findtext("dhEvento", ""),
                            "descricao": inf_evento.findtext("xEvento", ""),
                        }
                    )

            dados["eventos"] = eventos

            sucesso = cstat == "100"

            return ResultadoConsulta(
                sucesso=sucesso,
                codigo=cstat,
                mensagem=xmotivo,
                dados=dados,
                xml_retorno=xml_response,
                tempo_resposta_ms=tempo_ms,
            )

        except ET.ParseError as e:
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem=f"Erro parse: {e}",
                xml_retorno=xml_response,
                tempo_resposta_ms=tempo_ms,
            )

    # =========================================================================
    # 5. INUTILIZACAO DE NUMERACAO
    # =========================================================================

    async def inutilizar_numeracao(
        self,
        cnpj: str,
        serie: int,
        numero_inicial: int,
        numero_final: int,
        justificativa: str,
        ano: int | None = None,
    ) -> ResultadoConsulta:
        """
        Inutiliza faixa de numeracao de NF-e.

        Endpoint: NfeInutilizacao4
        Versao: 4.00

        Args:
            cnpj: CNPJ do emitente
            serie: Serie da NF-e
            numero_inicial: Numero inicial da faixa
            numero_final: Numero final da faixa
            justificativa: Motivo da inutilizacao (min 15 caracteres)
            ano: Ano de referencia (default: ano atual)

        Returns:
            ResultadoConsulta com protocolo de inutilizacao
        """
        if len(justificativa) < 15:
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem="Justificativa deve ter no minimo 15 caracteres",
            )

        ano = ano or datetime.now().year
        ano_2d = str(ano)[2:]

        # Montar ID da inutilizacao
        # ID = "ID" + cUF + ano + CNPJ + mod + serie + nNFIni + nNFFin
        id_inut = f"ID{self.UF_CODIGO}{ano_2d}{cnpj:014}55{serie:03d}{numero_inicial:09d}{numero_final:09d}"

        xml_inut = f'''<inutNFe xmlns="{NS_NFE}" versao="4.00">
            <infInut Id="{id_inut}">
                <tpAmb>{self.ambiente.value}</tpAmb>
                <xServ>INUTILIZAR</xServ>
                <cUF>{self.UF_CODIGO}</cUF>
                <ano>{ano_2d}</ano>
                <CNPJ>{cnpj}</CNPJ>
                <mod>55</mod>
                <serie>{serie}</serie>
                <nNFIni>{numero_inicial}</nNFIni>
                <nNFFin>{numero_final}</nNFFin>
                <xJust>{justificativa}</xJust>
            </infInut>
        </inutNFe>'''

        # Assinar XML
        xml_assinado = await self.xml_signer.assinar_xml(
            xml_inut,
            SignatureType.INUTILIZACAO,
            id_inut,
        )

        xml_body = f'''<nfeDadosMsg xmlns="{NS_NFE}">
            {xml_assinado}
        </nfeDadosMsg>'''

        try:
            status_code, response_text, tempo_ms = await self._enviar_requisicao("NfeInutilizacao", xml_body)

            if status_code == 200:
                return self._parse_inutilizacao(response_text, tempo_ms)
            else:
                return ResultadoConsulta(
                    sucesso=False,
                    codigo=str(status_code),
                    mensagem=f"Erro HTTP: {status_code}",
                    tempo_resposta_ms=tempo_ms,
                )

        except Exception as e:
            logger.error(f"[SEFAZ-AM] Erro inutilizacao: {e}")
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem=str(e),
            )

    def _parse_inutilizacao(self, xml_response: str, tempo_ms: float) -> ResultadoConsulta:
        """Parse da resposta de inutilizacao."""
        try:
            xml_clean = xml_response.replace('xmlns="http://www.portalfiscal.inf.br/nfe"', "")
            root = ET.fromstring(xml_clean)

            ret = root.find(".//retInutNFe/infInut")
            if ret is None:
                return ResultadoConsulta(
                    sucesso=False,
                    codigo="999",
                    mensagem="Resposta invalida",
                    xml_retorno=xml_response,
                    tempo_resposta_ms=tempo_ms,
                )

            cstat = ret.findtext("cStat", "")
            xmotivo = ret.findtext("xMotivo", "")
            protocolo = ret.findtext("nProt", "")

            sucesso = cstat == "102"  # 102 = Inutilizacao homologada

            return ResultadoConsulta(
                sucesso=sucesso,
                codigo=cstat,
                mensagem=xmotivo,
                dados={
                    "protocolo": protocolo,
                    "data_inutilizacao": ret.findtext("dhRecbto", ""),
                },
                xml_retorno=xml_response,
                tempo_resposta_ms=tempo_ms,
            )

        except ET.ParseError as e:
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem=f"Erro parse: {e}",
                xml_retorno=xml_response,
                tempo_resposta_ms=tempo_ms,
            )

    # =========================================================================
    # 6. RECEPCAO DE EVENTOS (CANCELAMENTO / CARTA DE CORRECAO)
    # =========================================================================

    async def registrar_evento(
        self,
        chave_acesso: str,
        tipo_evento: TipoEvento,
        cnpj: str,
        sequencia: int = 1,
        justificativa: str | None = None,
        correcao: str | None = None,
    ) -> ResultadoEvento:
        """
        Registra evento na NF-e.

        Endpoint: RecepcaoEvento4
        Versao: 4.00

        Args:
            chave_acesso: Chave de acesso da NF-e
            tipo_evento: Tipo do evento
            cnpj: CNPJ do autor do evento
            sequencia: Sequencia do evento (default: 1)
            justificativa: Justificativa (obrigatoria para cancelamento)
            correcao: Texto de correcao (obrigatorio para carta de correcao)

        Returns:
            ResultadoEvento com protocolo
        """
        if tipo_evento == TipoEvento.CANCELAMENTO and not justificativa:
            return ResultadoEvento(
                sucesso=False,
                codigo="999",
                mensagem="Justificativa obrigatoria para cancelamento",
            )

        if tipo_evento == TipoEvento.CARTA_CORRECAO and not correcao:
            return ResultadoEvento(
                sucesso=False,
                codigo="999",
                mensagem="Texto de correcao obrigatorio",
            )

        # Montar ID do evento
        id_evento = f"ID{tipo_evento.value}{chave_acesso}{sequencia:02d}"
        dh_evento = datetime.now().strftime("%Y-%m-%dT%H:%M:%S-04:00")

        # Montar detalhamento conforme tipo
        if tipo_evento == TipoEvento.CANCELAMENTO:
            det_evento = f"""<detEvento versao="1.00">
                <descEvento>Cancelamento</descEvento>
                <nProt></nProt>
                <xJust>{justificativa}</xJust>
            </detEvento>"""
        elif tipo_evento == TipoEvento.CARTA_CORRECAO:
            det_evento = f"""<detEvento versao="1.00">
                <descEvento>Carta de Correcao</descEvento>
                <xCorrecao>{correcao}</xCorrecao>
                <xCondUso>A Carta de Correcao e disciplinada pelo paragrafo 1o-A do art. 7o do Convenio S/N, de 15 de dezembro de 1970 e pode ser utilizada para regularizacao de erro ocorrido na emissao de documento fiscal, desde que o erro nao esteja relacionado com: I - as variaveis que determinam o valor do imposto tais como: base de calculo, aliquota, diferenca de preco, quantidade, valor da operacao ou da prestacao; II - a correcao de dados cadastrais que implique mudanca do remetente ou do destinatario; III - a data de emissao ou de saida.</xCondUso>
            </detEvento>"""
        else:
            # Manifestacao do destinatario
            det_evento = f"""<detEvento versao="1.00">
                <descEvento>{self._get_descricao_evento(tipo_evento)}</descEvento>
            </detEvento>"""

        xml_evento = f'''<evento xmlns="{NS_NFE}" versao="1.00">
            <infEvento Id="{id_evento}">
                <cOrgao>{self.UF_CODIGO}</cOrgao>
                <tpAmb>{self.ambiente.value}</tpAmb>
                <CNPJ>{cnpj}</CNPJ>
                <chNFe>{chave_acesso}</chNFe>
                <dhEvento>{dh_evento}</dhEvento>
                <tpEvento>{tipo_evento.value}</tpEvento>
                <nSeqEvento>{sequencia}</nSeqEvento>
                <verEvento>1.00</verEvento>
                {det_evento}
            </infEvento>
        </evento>'''

        # Assinar evento
        xml_assinado = await self.xml_signer.assinar_xml(
            xml_evento,
            SignatureType.EVENTO,
            id_evento,
        )

        xml_body = f'''<nfeDadosMsg xmlns="{NS_NFE}">
            <envEvento xmlns="{NS_NFE}" versao="1.00">
                <idLote>{datetime.now().strftime("%Y%m%d%H%M%S")}</idLote>
                {xml_assinado}
            </envEvento>
        </nfeDadosMsg>'''

        try:
            status_code, response_text, tempo_ms = await self._enviar_requisicao("RecepcaoEvento", xml_body)

            if status_code == 200:
                return self._parse_evento(response_text, tipo_evento)
            else:
                return ResultadoEvento(
                    sucesso=False,
                    codigo=str(status_code),
                    mensagem=f"Erro HTTP: {status_code}",
                )

        except Exception as e:
            logger.error(f"[SEFAZ-AM] Erro evento: {e}")
            return ResultadoEvento(
                sucesso=False,
                codigo="999",
                mensagem=str(e),
            )

    def _get_descricao_evento(self, tipo: TipoEvento) -> str:
        """Retorna descricao do tipo de evento."""
        descricoes = {
            TipoEvento.CANCELAMENTO: "Cancelamento",
            TipoEvento.CARTA_CORRECAO: "Carta de Correcao",
            TipoEvento.CIENCIA_OPERACAO: "Ciencia da Operacao",
            TipoEvento.CONFIRMACAO_OPERACAO: "Confirmacao da Operacao",
            TipoEvento.DESCONHECIMENTO_OPERACAO: "Desconhecimento da Operacao",
            TipoEvento.OPERACAO_NAO_REALIZADA: "Operacao nao Realizada",
        }
        return descricoes.get(tipo, tipo.value)

    def _parse_evento(self, xml_response: str, tipo_evento: TipoEvento) -> ResultadoEvento:
        """Parse da resposta de evento."""
        try:
            xml_clean = xml_response.replace('xmlns="http://www.portalfiscal.inf.br/nfe"', "")
            root = ET.fromstring(xml_clean)

            ret = root.find(".//retEvento/infEvento")
            if ret is None:
                return ResultadoEvento(
                    sucesso=False,
                    codigo="999",
                    mensagem="Resposta invalida",
                    xml_evento=xml_response,
                )

            cstat = ret.findtext("cStat", "")
            xmotivo = ret.findtext("xMotivo", "")
            protocolo = ret.findtext("nProt", "")
            sequencia = ret.findtext("nSeqEvento", "")
            dh_reg = ret.findtext("dhRegEvento", "")

            # Codigos de sucesso para eventos
            sucesso = cstat in ["135", "136"]  # 135=Evento registrado, 136=Evento ja registrado

            return ResultadoEvento(
                sucesso=sucesso,
                codigo=cstat,
                mensagem=xmotivo,
                protocolo=protocolo,
                tipo_evento=tipo_evento.value,
                sequencia=int(sequencia) if sequencia else None,
                data_registro=self._parse_datetime(dh_reg),
                xml_evento=xml_response,
            )

        except ET.ParseError as e:
            return ResultadoEvento(
                sucesso=False,
                codigo="999",
                mensagem=f"Erro parse: {e}",
                xml_evento=xml_response,
            )

    # =========================================================================
    # 7. CONSULTA CADASTRO DE CONTRIBUINTE
    # =========================================================================

    async def consultar_cadastro(
        self,
        inscricao_estadual: str | None = None,
        cnpj: str | None = None,
        cpf: str | None = None,
    ) -> ResultadoConsulta:
        """
        Consulta cadastro de contribuinte.

        Endpoint: CadConsultaCadastro4
        Versao: 4.00

        Args:
            inscricao_estadual: IE do contribuinte
            cnpj: CNPJ do contribuinte
            cpf: CPF do contribuinte

        Returns:
            ResultadoConsulta com dados cadastrais
        """
        if not any([inscricao_estadual, cnpj, cpf]):
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem="Informe IE, CNPJ ou CPF",
            )

        # Montar filtro
        if inscricao_estadual:
            filtro = f"<IE>{inscricao_estadual}</IE>"
        elif cnpj:
            filtro = f"<CNPJ>{cnpj}</CNPJ>"
        else:
            filtro = f"<CPF>{cpf}</CPF>"

        xml_body = f'''<nfeDadosMsg xmlns="{NS_NFE}">
            <ConsCad xmlns="{NS_NFE}" versao="2.00">
                <infCons>
                    <xServ>CONS-CAD</xServ>
                    <UF>{self.UF_SIGLA}</UF>
                    {filtro}
                </infCons>
            </ConsCad>
        </nfeDadosMsg>'''

        try:
            status_code, response_text, tempo_ms = await self._enviar_requisicao("CadConsultaCadastro", xml_body)

            if status_code == 200:
                return self._parse_cadastro(response_text, tempo_ms)
            else:
                return ResultadoConsulta(
                    sucesso=False,
                    codigo=str(status_code),
                    mensagem=f"Erro HTTP: {status_code}",
                    tempo_resposta_ms=tempo_ms,
                )

        except Exception as e:
            logger.error(f"[SEFAZ-AM] Erro consulta cadastro: {e}")
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem=str(e),
            )

    def _parse_cadastro(self, xml_response: str, tempo_ms: float) -> ResultadoConsulta:
        """Parse da resposta de consulta cadastral."""
        try:
            xml_clean = xml_response.replace('xmlns="http://www.portalfiscal.inf.br/nfe"', "")
            root = ET.fromstring(xml_clean)

            ret = root.find(".//retConsCad/infCons")
            if ret is None:
                return ResultadoConsulta(
                    sucesso=False,
                    codigo="999",
                    mensagem="Resposta invalida",
                    xml_retorno=xml_response,
                    tempo_resposta_ms=tempo_ms,
                )

            cstat = ret.findtext("cStat", "")
            xmotivo = ret.findtext("xMotivo", "")

            # Extrair dados do cadastro
            contribuintes = []
            for inf_cad in ret.findall(".//infCad"):
                contribuinte = InformacaoCadastral(
                    cnpj=inf_cad.findtext("CNPJ"),
                    cpf=inf_cad.findtext("CPF"),
                    inscricao_estadual=inf_cad.findtext("IE", ""),
                    razao_social=inf_cad.findtext("xNome", ""),
                    nome_fantasia=inf_cad.findtext("xFant"),
                    situacao=inf_cad.findtext("cSit", ""),
                    regime_tributario=inf_cad.findtext("xRegApur"),
                    cnae_principal=inf_cad.findtext("CNAE"),
                )

                # Endereco
                ender = inf_cad.find(".//ender")
                if ender is not None:
                    contribuinte.endereco = {
                        "logradouro": ender.findtext("xLgr", ""),
                        "numero": ender.findtext("nro", ""),
                        "complemento": ender.findtext("xCpl"),
                        "bairro": ender.findtext("xBairro", ""),
                        "codigo_municipio": ender.findtext("cMun", ""),
                        "municipio": ender.findtext("xMun", ""),
                        "cep": ender.findtext("CEP", ""),
                    }

                contribuintes.append(contribuinte)

            sucesso = cstat in ["111", "112"]  # 111=Um cadastro, 112=Multiplos

            return ResultadoConsulta(
                sucesso=sucesso,
                codigo=cstat,
                mensagem=xmotivo,
                dados={
                    "contribuintes": [
                        {
                            "cnpj": c.cnpj,
                            "cpf": c.cpf,
                            "inscricao_estadual": c.inscricao_estadual,
                            "razao_social": c.razao_social,
                            "nome_fantasia": c.nome_fantasia,
                            "situacao": c.situacao,
                            "regime_tributario": c.regime_tributario,
                            "cnae_principal": c.cnae_principal,
                            "endereco": c.endereco,
                        }
                        for c in contribuintes
                    ],
                },
                xml_retorno=xml_response,
                tempo_resposta_ms=tempo_ms,
            )

        except ET.ParseError as e:
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem=f"Erro parse: {e}",
                xml_retorno=xml_response,
                tempo_resposta_ms=tempo_ms,
            )

    # =========================================================================
    # 8. DF-E DISTRIBUICAO (NOTAS DESTINADAS) - VIA SEFAZ NACIONAL
    # =========================================================================

    async def consultar_dfe_destinadas(
        self,
        cnpj: str,
        ultimo_nsu: str = "0",
        nsu_especifico: str | None = None,
        chave_acesso: str | None = None,
    ) -> ResultadoConsulta:
        """
        Consulta DF-e destinados ao CNPJ (Distribuicao Nacional).

        Endpoint: NFeDistribuicaoDFe (Nacional)
        Versao: 1.01

        Args:
            cnpj: CNPJ do interessado
            ultimo_nsu: Ultimo NSU recebido (para paginacao)
            nsu_especifico: NSU especifico para consulta
            chave_acesso: Chave de acesso para consulta direta

        Returns:
            ResultadoConsulta com documentos destinados
        """
        url = (
            ENDPOINT_DFE_NACIONAL.producao
            if self.ambiente == AmbienteSEFAZ.PRODUCAO
            else ENDPOINT_DFE_NACIONAL.homologacao
        )

        # Montar consulta conforme tipo
        if chave_acesso:
            consulta = f"<consChNFe><chNFe>{chave_acesso}</chNFe></consChNFe>"
        elif nsu_especifico:
            consulta = f"<consNSU><NSU>{nsu_especifico:015}</NSU></consNSU>"
        else:
            consulta = f"<distNSU><ultNSU>{ultimo_nsu:015}</ultNSU></distNSU>"

        xml_body = f'''<nfeDadosMsg xmlns="{NS_NFE}">
            <distDFeInt xmlns="{NS_NFE}" versao="1.01">
                <tpAmb>{self.ambiente.value}</tpAmb>
                <cUFAutor>{self.UF_CODIGO}</cUFAutor>
                <CNPJ>{cnpj}</CNPJ>
                {consulta}
            </distDFeInt>
        </nfeDadosMsg>'''

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": ENDPOINT_DFE_NACIONAL.soap_action,
        }

        envelope = self._criar_envelope_soap(xml_body)

        inicio = datetime.now()
        try:
            client = await self._get_client()
            response = await client.post(url, content=envelope, headers=headers)
            tempo_ms = (datetime.now() - inicio).total_seconds() * 1000

            if response.status_code == 200:
                return self._parse_dfe_distribuicao(response.text, tempo_ms)
            else:
                return ResultadoConsulta(
                    sucesso=False,
                    codigo=str(response.status_code),
                    mensagem=f"Erro HTTP: {response.status_code}",
                    tempo_resposta_ms=tempo_ms,
                )

        except Exception as e:
            logger.error(f"[SEFAZ-AM] Erro DF-e distribuicao: {e}")
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem=str(e),
            )

    def _parse_dfe_distribuicao(self, xml_response: str, tempo_ms: float) -> ResultadoConsulta:
        """Parse da resposta de distribuicao DF-e."""
        try:
            xml_clean = xml_response.replace('xmlns="http://www.portalfiscal.inf.br/nfe"', "")
            root = ET.fromstring(xml_clean)

            ret = root.find(".//retDistDFeInt")
            if ret is None:
                return ResultadoConsulta(
                    sucesso=False,
                    codigo="999",
                    mensagem="Resposta invalida",
                    xml_retorno=xml_response,
                    tempo_resposta_ms=tempo_ms,
                )

            cstat = ret.findtext("cStat", "")
            xmotivo = ret.findtext("xMotivo", "")
            ultimo_nsu = ret.findtext("ultNSU", "")
            max_nsu = ret.findtext("maxNSU", "")

            # Extrair documentos
            documentos = []
            for doc in ret.findall(".//docZip"):
                nsu = doc.get("NSU", "")
                schema = doc.get("schema", "")
                # Conteudo esta em base64 gzip
                conteudo_b64 = doc.text

                documentos.append(
                    {
                        "nsu": nsu,
                        "schema": schema,
                        "conteudo_compactado": conteudo_b64,
                    }
                )

            sucesso = cstat in ["137", "138"]  # 137=Nenhum doc, 138=Documentos localizados

            return ResultadoConsulta(
                sucesso=sucesso,
                codigo=cstat,
                mensagem=xmotivo,
                dados={
                    "ultimo_nsu": ultimo_nsu,
                    "max_nsu": max_nsu,
                    "quantidade_documentos": len(documentos),
                    "documentos": documentos,
                },
                xml_retorno=xml_response,
                tempo_resposta_ms=tempo_ms,
            )

        except ET.ParseError as e:
            return ResultadoConsulta(
                sucesso=False,
                codigo="999",
                mensagem=f"Erro parse: {e}",
                xml_retorno=xml_response,
                tempo_resposta_ms=tempo_ms,
            )

    # =========================================================================
    # METODOS AUXILIARES
    # =========================================================================

    def _parse_datetime(self, dt_str: str | None) -> datetime | None:
        """Converte string de data/hora para datetime."""
        if not dt_str:
            return None
        try:
            # Formato ISO com timezone
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except ValueError:
            try:
                # Formato sem timezone
                return datetime.strptime(dt_str[:19], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return None


# =========================================================================
# SERVICO PARA USO NO CONECTA PRO
# =========================================================================


class SefazAMService:
    """Servico de integracao SEFAZ-AM para o Conecta PRO."""

    def __init__(self, db_session, certificate_manager: CertificateManager):
        """Inicializa o servico."""
        self.db = db_session
        self.certificate_manager = certificate_manager
        self._client: SefazAMClient | None = None

    async def _get_client(self, ambiente: AmbienteSEFAZ = AmbienteSEFAZ.PRODUCAO) -> SefazAMClient:
        """Obtem cliente SEFAZ-AM."""
        if self._client is None:
            self._client = SefazAMClient(
                certificate_manager=self.certificate_manager,
                ambiente=ambiente,
            )
        return self._client

    async def verificar_status(self) -> dict[str, Any]:
        """Verifica status do servico SEFAZ-AM."""
        client = await self._get_client()
        resultado = await client.consultar_status_servico()

        return {
            "disponivel": resultado.sucesso,
            "codigo": resultado.codigo,
            "mensagem": resultado.mensagem,
            "tempo_resposta_ms": resultado.tempo_resposta_ms,
            "dados": resultado.dados,
        }

    async def consultar_nfe(self, chave_acesso: str) -> dict[str, Any]:
        """Consulta NF-e por chave de acesso."""
        client = await self._get_client()
        resultado = await client.consultar_nfe(chave_acesso)

        return {
            "sucesso": resultado.sucesso,
            "codigo": resultado.codigo,
            "mensagem": resultado.mensagem,
            "dados": resultado.dados,
            "xml": resultado.xml_retorno,
        }

    async def consultar_cadastro_ie(self, inscricao_estadual: str) -> dict[str, Any]:
        """Consulta cadastro por IE."""
        client = await self._get_client()
        resultado = await client.consultar_cadastro(inscricao_estadual=inscricao_estadual)

        return {
            "sucesso": resultado.sucesso,
            "codigo": resultado.codigo,
            "mensagem": resultado.mensagem,
            "contribuintes": resultado.dados.get("contribuintes", []) if resultado.dados else [],
        }

    async def consultar_cadastro_cnpj(self, cnpj: str) -> dict[str, Any]:
        """Consulta cadastro por CNPJ."""
        client = await self._get_client()
        resultado = await client.consultar_cadastro(cnpj=cnpj)

        return {
            "sucesso": resultado.sucesso,
            "codigo": resultado.codigo,
            "mensagem": resultado.mensagem,
            "contribuintes": resultado.dados.get("contribuintes", []) if resultado.dados else [],
        }

    async def consultar_notas_destinadas(
        self,
        cnpj: str,
        ultimo_nsu: str = "0",
    ) -> dict[str, Any]:
        """Consulta notas destinadas ao CNPJ."""
        client = await self._get_client()
        resultado = await client.consultar_dfe_destinadas(cnpj, ultimo_nsu)

        return {
            "sucesso": resultado.sucesso,
            "codigo": resultado.codigo,
            "mensagem": resultado.mensagem,
            "ultimo_nsu": resultado.dados.get("ultimo_nsu") if resultado.dados else None,
            "documentos": resultado.dados.get("documentos", []) if resultado.dados else [],
        }

    async def cancelar_nfe(
        self,
        chave_acesso: str,
        cnpj: str,
        justificativa: str,
    ) -> dict[str, Any]:
        """Cancela NF-e."""
        client = await self._get_client()
        resultado = await client.registrar_evento(
            chave_acesso=chave_acesso,
            tipo_evento=TipoEvento.CANCELAMENTO,
            cnpj=cnpj,
            justificativa=justificativa,
        )

        return {
            "sucesso": resultado.sucesso,
            "codigo": resultado.codigo,
            "mensagem": resultado.mensagem,
            "protocolo": resultado.protocolo,
            "data_registro": resultado.data_registro.isoformat() if resultado.data_registro else None,
        }

    async def carta_correcao(
        self,
        chave_acesso: str,
        cnpj: str,
        correcao: str,
        sequencia: int = 1,
    ) -> dict[str, Any]:
        """Registra carta de correcao."""
        client = await self._get_client()
        resultado = await client.registrar_evento(
            chave_acesso=chave_acesso,
            tipo_evento=TipoEvento.CARTA_CORRECAO,
            cnpj=cnpj,
            sequencia=sequencia,
            correcao=correcao,
        )

        return {
            "sucesso": resultado.sucesso,
            "codigo": resultado.codigo,
            "mensagem": resultado.mensagem,
            "protocolo": resultado.protocolo,
            "sequencia": resultado.sequencia,
        }

    async def inutilizar_numeracao(
        self,
        cnpj: str,
        serie: int,
        numero_inicial: int,
        numero_final: int,
        justificativa: str,
    ) -> dict[str, Any]:
        """Inutiliza faixa de numeracao."""
        client = await self._get_client()
        resultado = await client.inutilizar_numeracao(
            cnpj=cnpj,
            serie=serie,
            numero_inicial=numero_inicial,
            numero_final=numero_final,
            justificativa=justificativa,
        )

        return {
            "sucesso": resultado.sucesso,
            "codigo": resultado.codigo,
            "mensagem": resultado.mensagem,
            "protocolo": resultado.dados.get("protocolo") if resultado.dados else None,
        }

    async def close(self):
        """Fecha conexoes."""
        if self._client:
            await self._client.close()
