"""
NFS-e Manaus - Integração com Prefeitura de Manaus.

Portal: https://nfse.manaus.am.gov.br/
WebService: ABRASF 2.04

Funções:
- Emissão de NFS-e
- Consulta de NFS-e
- Cancelamento de NFS-e
- Substituição de NFS-e
"""

import logging
import hashlib
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import xml.etree.ElementTree as ET

from .certificate_manager import CertificateManager
from .xml_signer import XMLSigner

logger = logging.getLogger(__name__)


class NFSeStatus(str, Enum):
    """Status da NFS-e."""
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    AUTORIZADA = "autorizada"
    CANCELADA = "cancelada"
    SUBSTITUIDA = "substituida"
    ERRO = "erro"


class TipoTributacao(str, Enum):
    """Tipo de tributação do ISS."""
    NORMAL = "1"  # Tributação no município
    RETIDO = "2"  # ISS retido pelo tomador
    IMUNE = "3"   # Imune
    ISENTO = "4"  # Isento
    EXIGIBILIDADE_SUSPENSA = "5"  # Exigibilidade suspensa por decisão judicial
    EXIGIBILIDADE_SUSPENSA_ADM = "6"  # Exigibilidade suspensa por processo administrativo


class NaturezaOperacao(str, Enum):
    """Natureza da operação."""
    TRIBUTACAO_MUNICIPIO = "1"
    TRIBUTACAO_FORA_MUNICIPIO = "2"
    ISENCAO = "3"
    IMUNE = "4"
    EXIGIBILIDADE_SUSPENSA_JUDICIAL = "5"
    EXIGIBILIDADE_SUSPENSA_ADM = "6"
    EXPORTACAO = "7"


@dataclass
class Tomador:
    """Dados do tomador do serviço."""
    cpf_cnpj: str
    razao_social: str
    endereco: str
    numero: str
    bairro: str
    cidade: str
    uf: str
    cep: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    inscricao_municipal: Optional[str] = None
    complemento: Optional[str] = None


@dataclass
class Servico:
    """Dados do serviço prestado."""
    codigo_servico: str  # Código do serviço (Lista de Serviços LC 116)
    discriminacao: str   # Descrição do serviço
    valor_servicos: Decimal
    valor_deducoes: Decimal = Decimal("0")
    valor_pis: Decimal = Decimal("0")
    valor_cofins: Decimal = Decimal("0")
    valor_inss: Decimal = Decimal("0")
    valor_ir: Decimal = Decimal("0")
    valor_csll: Decimal = Decimal("0")
    valor_iss: Decimal = Decimal("0")
    aliquota_iss: Decimal = Decimal("0.05")  # 5% padrão Manaus
    iss_retido: bool = False
    codigo_cnae: Optional[str] = None
    codigo_tributacao_municipio: Optional[str] = None

    @property
    def base_calculo(self) -> Decimal:
        """Calcula base de cálculo do ISS."""
        return self.valor_servicos - self.valor_deducoes

    @property
    def valor_liquido(self) -> Decimal:
        """Calcula valor líquido da nota."""
        return (self.valor_servicos - self.valor_deducoes -
                self.valor_pis - self.valor_cofins -
                self.valor_inss - self.valor_ir -
                self.valor_csll - (self.valor_iss if self.iss_retido else Decimal("0")))


@dataclass
class NFSeManaus:
    """Representação de uma NFS-e de Manaus."""
    # Identificação
    numero: Optional[str] = None
    codigo_verificacao: Optional[str] = None

    # Prestador (dados da empresa)
    prestador_cnpj: str = ""
    prestador_inscricao_municipal: str = ""

    # Tomador
    tomador: Optional[Tomador] = None

    # Serviço
    servico: Optional[Servico] = None

    # Datas
    data_emissao: datetime = field(default_factory=datetime.now)
    competencia: date = field(default_factory=date.today)

    # Tributação
    natureza_operacao: NaturezaOperacao = NaturezaOperacao.TRIBUTACAO_MUNICIPIO
    regime_especial_tributacao: Optional[str] = None
    optante_simples: bool = True
    incentivador_cultural: bool = False

    # Status
    status: NFSeStatus = NFSeStatus.PENDENTE
    mensagem_retorno: Optional[str] = None

    # XML
    xml_envio: Optional[str] = None
    xml_retorno: Optional[str] = None


class NFSeManausManager:
    """
    Gerenciador de NFS-e para Prefeitura de Manaus.

    Implementa padrão ABRASF 2.04.
    Provider: Abaco/GIF
    Testado em: Janeiro 2026

    Endpoints testados e funcionais:
    - RecepcionarLoteRps
    - ConsultarSituacaoLoteRps
    - ConsultarNfsePorRps
    - ConsultarLoteRps
    """

    # URLs dos WebServices (Abaco/GIF - Testado Janeiro 2026)
    URL_BASE_PRODUCAO = "https://nfse-prd.manaus.am.gov.br/nfse/servlet"
    URL_BASE_HOMOLOGACAO = "https://nfse-hml.manaus.am.gov.br/nfse/servlet"

    # Endpoints específicos
    ENDPOINTS = {
        "RecepcionarLoteRps": "/arecepcionarloterps",
        "ConsultarSituacaoLoteRps": "/aconsultarsituacaoloterps",
        "ConsultarNfsePorRps": "/aconsultarnfseporrps",
        "ConsultarLoteRps": "/aconsultarloterps",
        "CancelarNfse": "/acancelarnfse",
        "SubstituirNfse": "/asubstituirnfse",
        "ConsultarNfseServicoPrestado": "/aconsultarnfseservicoprestado",
        "ConsultarNfseServicoTomado": "/aconsultarnfseservicotomado",
    }

    # WSDLs para Zeep (se necessário)
    WSDL_PRODUCAO = "https://nfse-prd.manaus.am.gov.br/nfse/servlet/arecepcionarloterps?wsdl"
    WSDL_HOMOLOGACAO = "https://nfse-hml.manaus.am.gov.br/nfse/servlet/arecepcionarloterps?wsdl"

    # Código do município de Manaus (IBGE)
    CODIGO_MUNICIPIO = "1302603"

    # Namespace ABRASF
    NS_TIPOS = "http://www.abrasf.org.br/nfse.xsd"

    # Namespace do WebService (Abaco/GIF)
    NS_WS = "http://www.e-nfs.com.br"

    def __init__(
        self,
        certificate_manager: CertificateManager,
        ambiente: str = "producao",
        inscricao_municipal: str = "",
        cnpj: str = "",
        usuario: str = "",
        senha: str = "",
    ):
        """
        Inicializa o gerenciador.

        Args:
            certificate_manager: Gerenciador de certificados
            ambiente: 'producao' ou 'homologacao'
            inscricao_municipal: Inscrição municipal do prestador
            cnpj: CNPJ do prestador
            usuario: Usuário para autenticação (geralmente o CNPJ)
            senha: Senha para autenticação
        """
        self.cert_manager = certificate_manager
        self.ambiente = ambiente
        self.inscricao_municipal = inscricao_municipal
        self.cnpj = cnpj
        self.usuario = usuario or cnpj
        self.senha = senha
        self.xml_signer = XMLSigner(certificate_manager)

        # URLs
        self.url_base = (
            self.URL_BASE_PRODUCAO if ambiente == "producao"
            else self.URL_BASE_HOMOLOGACAO
        )
        self.wsdl_url = (
            self.WSDL_PRODUCAO if ambiente == "producao"
            else self.WSDL_HOMOLOGACAO
        )

    def gerar_rps(self, nfse: NFSeManaus) -> str:
        """
        Gera XML do RPS (Recibo Provisório de Serviço).

        Args:
            nfse: Dados da NFS-e

        Returns:
            XML do RPS
        """
        # Namespace
        ns = {"ns": self.NS_TIPOS}

        # Root
        rps = ET.Element("Rps")

        # InfDeclaracaoPrestacaoServico
        inf_rps = ET.SubElement(rps, "InfDeclaracaoPrestacaoServico")

        # Rps (identificação)
        rps_id = ET.SubElement(inf_rps, "Rps")
        ident_rps = ET.SubElement(rps_id, "IdentificacaoRps")
        ET.SubElement(ident_rps, "Numero").text = str(int(datetime.now().timestamp()))
        ET.SubElement(ident_rps, "Serie").text = "RPS"
        ET.SubElement(ident_rps, "Tipo").text = "1"  # RPS
        ET.SubElement(rps_id, "DataEmissao").text = nfse.data_emissao.strftime("%Y-%m-%d")
        ET.SubElement(rps_id, "Status").text = "1"  # Normal

        # Competência
        ET.SubElement(inf_rps, "Competencia").text = nfse.competencia.strftime("%Y-%m-%d")

        # Serviço
        servico = ET.SubElement(inf_rps, "Servico")
        valores = ET.SubElement(servico, "Valores")
        ET.SubElement(valores, "ValorServicos").text = str(nfse.servico.valor_servicos)
        ET.SubElement(valores, "ValorDeducoes").text = str(nfse.servico.valor_deducoes)
        ET.SubElement(valores, "ValorPis").text = str(nfse.servico.valor_pis)
        ET.SubElement(valores, "ValorCofins").text = str(nfse.servico.valor_cofins)
        ET.SubElement(valores, "ValorInss").text = str(nfse.servico.valor_inss)
        ET.SubElement(valores, "ValorIr").text = str(nfse.servico.valor_ir)
        ET.SubElement(valores, "ValorCsll").text = str(nfse.servico.valor_csll)
        ET.SubElement(valores, "IssRetido").text = "1" if nfse.servico.iss_retido else "2"
        ET.SubElement(valores, "ValorIss").text = str(nfse.servico.valor_iss)
        ET.SubElement(valores, "BaseCalculo").text = str(nfse.servico.base_calculo)
        ET.SubElement(valores, "Aliquota").text = str(nfse.servico.aliquota_iss)
        ET.SubElement(valores, "ValorLiquidoNfse").text = str(nfse.servico.valor_liquido)

        ET.SubElement(servico, "ItemListaServico").text = nfse.servico.codigo_servico
        if nfse.servico.codigo_cnae:
            ET.SubElement(servico, "CodigoCnae").text = nfse.servico.codigo_cnae
        ET.SubElement(servico, "Discriminacao").text = nfse.servico.discriminacao
        ET.SubElement(servico, "CodigoMunicipio").text = self.CODIGO_MUNICIPIO

        # Prestador
        prestador = ET.SubElement(inf_rps, "Prestador")
        cpf_cnpj_prest = ET.SubElement(prestador, "CpfCnpj")
        ET.SubElement(cpf_cnpj_prest, "Cnpj").text = self.cnpj
        ET.SubElement(prestador, "InscricaoMunicipal").text = self.inscricao_municipal

        # Tomador
        if nfse.tomador:
            tomador = ET.SubElement(inf_rps, "Tomador")
            ident_tomador = ET.SubElement(tomador, "IdentificacaoTomador")
            cpf_cnpj_tom = ET.SubElement(ident_tomador, "CpfCnpj")

            doc = nfse.tomador.cpf_cnpj.replace(".", "").replace("-", "").replace("/", "")
            if len(doc) == 11:
                ET.SubElement(cpf_cnpj_tom, "Cpf").text = doc
            else:
                ET.SubElement(cpf_cnpj_tom, "Cnpj").text = doc

            if nfse.tomador.inscricao_municipal:
                ET.SubElement(ident_tomador, "InscricaoMunicipal").text = nfse.tomador.inscricao_municipal

            ET.SubElement(tomador, "RazaoSocial").text = nfse.tomador.razao_social

            endereco = ET.SubElement(tomador, "Endereco")
            ET.SubElement(endereco, "Endereco").text = nfse.tomador.endereco
            ET.SubElement(endereco, "Numero").text = nfse.tomador.numero
            if nfse.tomador.complemento:
                ET.SubElement(endereco, "Complemento").text = nfse.tomador.complemento
            ET.SubElement(endereco, "Bairro").text = nfse.tomador.bairro
            ET.SubElement(endereco, "CodigoMunicipio").text = self.CODIGO_MUNICIPIO
            ET.SubElement(endereco, "Uf").text = nfse.tomador.uf
            ET.SubElement(endereco, "Cep").text = nfse.tomador.cep.replace("-", "")

            if nfse.tomador.email or nfse.tomador.telefone:
                contato = ET.SubElement(tomador, "Contato")
                if nfse.tomador.telefone:
                    ET.SubElement(contato, "Telefone").text = nfse.tomador.telefone
                if nfse.tomador.email:
                    ET.SubElement(contato, "Email").text = nfse.tomador.email

        # Regime especial
        ET.SubElement(inf_rps, "OptanteSimplesNacional").text = "1" if nfse.optante_simples else "2"
        ET.SubElement(inf_rps, "IncentivoFiscal").text = "1" if nfse.incentivador_cultural else "2"

        return ET.tostring(rps, encoding="unicode")

    def enviar_lote_rps(self, lista_nfse: List[NFSeManaus]) -> Dict[str, Any]:
        """
        Envia lote de RPS para geração de NFS-e.

        Args:
            lista_nfse: Lista de NFS-e a serem enviadas

        Returns:
            Resultado do envio
        """
        # Monta lote
        lote = ET.Element("EnviarLoteRpsSincronoEnvio", xmlns=self.NS_TIPOS)

        lote_rps = ET.SubElement(lote, "LoteRps")
        ET.SubElement(lote_rps, "NumeroLote").text = str(int(datetime.now().timestamp()))

        cpf_cnpj = ET.SubElement(lote_rps, "CpfCnpj")
        ET.SubElement(cpf_cnpj, "Cnpj").text = self.cnpj
        ET.SubElement(lote_rps, "InscricaoMunicipal").text = self.inscricao_municipal
        ET.SubElement(lote_rps, "QuantidadeRps").text = str(len(lista_nfse))

        lista_rps = ET.SubElement(lote_rps, "ListaRps")

        for nfse in lista_nfse:
            rps_xml = self.gerar_rps(nfse)
            rps_element = ET.fromstring(rps_xml)
            lista_rps.append(rps_element)

        # Assina o lote
        xml_str = ET.tostring(lote, encoding="unicode")
        xml_assinado = self.xml_signer.assinar_xml(xml_str, "LoteRps")

        logger.info(f"Enviando lote com {len(lista_nfse)} RPS")

        return {
            "xml_envio": xml_assinado,
            "quantidade": len(lista_nfse),
            "status": "pendente"
        }

    def consultar_nfse_por_rps(
        self,
        numero_rps: str,
        serie: str = "RPS",
        tipo: str = "1"
    ) -> Dict[str, Any]:
        """
        Consulta NFS-e pelo número do RPS.

        Args:
            numero_rps: Número do RPS
            serie: Série do RPS
            tipo: Tipo do RPS

        Returns:
            Dados da NFS-e
        """
        consulta = ET.Element("ConsultarNfseRpsEnvio", xmlns=self.NS_TIPOS)

        ident_rps = ET.SubElement(consulta, "IdentificacaoRps")
        ET.SubElement(ident_rps, "Numero").text = numero_rps
        ET.SubElement(ident_rps, "Serie").text = serie
        ET.SubElement(ident_rps, "Tipo").text = tipo

        prestador = ET.SubElement(consulta, "Prestador")
        cpf_cnpj = ET.SubElement(prestador, "CpfCnpj")
        ET.SubElement(cpf_cnpj, "Cnpj").text = self.cnpj
        ET.SubElement(prestador, "InscricaoMunicipal").text = self.inscricao_municipal

        xml_str = ET.tostring(consulta, encoding="unicode")

        return {
            "xml_consulta": xml_str,
            "numero_rps": numero_rps
        }

    def consultar_nfse_por_numero(self, numero_nfse: str) -> Dict[str, Any]:
        """
        Consulta NFS-e pelo número da nota.

        Args:
            numero_nfse: Número da NFS-e

        Returns:
            Dados da NFS-e
        """
        consulta = ET.Element("ConsultarNfseEnvio", xmlns=self.NS_TIPOS)

        prestador = ET.SubElement(consulta, "Prestador")
        cpf_cnpj = ET.SubElement(prestador, "CpfCnpj")
        ET.SubElement(cpf_cnpj, "Cnpj").text = self.cnpj
        ET.SubElement(prestador, "InscricaoMunicipal").text = self.inscricao_municipal

        ET.SubElement(consulta, "NumeroNfse").text = numero_nfse

        xml_str = ET.tostring(consulta, encoding="unicode")

        return {
            "xml_consulta": xml_str,
            "numero_nfse": numero_nfse
        }

    def cancelar_nfse(
        self,
        numero_nfse: str,
        codigo_cancelamento: str = "1"
    ) -> Dict[str, Any]:
        """
        Cancela uma NFS-e.

        Args:
            numero_nfse: Número da NFS-e
            codigo_cancelamento: Código do motivo (1=Erro emissão, 2=Serviço não prestado, etc.)

        Returns:
            Resultado do cancelamento
        """
        cancelamento = ET.Element("CancelarNfseEnvio", xmlns=self.NS_TIPOS)

        pedido = ET.SubElement(cancelamento, "Pedido")
        inf_pedido = ET.SubElement(pedido, "InfPedidoCancelamento")

        ident_nfse = ET.SubElement(inf_pedido, "IdentificacaoNfse")
        ET.SubElement(ident_nfse, "Numero").text = numero_nfse
        cpf_cnpj = ET.SubElement(ident_nfse, "CpfCnpj")
        ET.SubElement(cpf_cnpj, "Cnpj").text = self.cnpj
        ET.SubElement(ident_nfse, "InscricaoMunicipal").text = self.inscricao_municipal
        ET.SubElement(ident_nfse, "CodigoMunicipio").text = self.CODIGO_MUNICIPIO

        ET.SubElement(inf_pedido, "CodigoCancelamento").text = codigo_cancelamento

        xml_str = ET.tostring(cancelamento, encoding="unicode")
        xml_assinado = self.xml_signer.assinar_xml(xml_str, "InfPedidoCancelamento")

        logger.info(f"Cancelando NFS-e {numero_nfse}")

        return {
            "xml_cancelamento": xml_assinado,
            "numero_nfse": numero_nfse,
            "codigo_cancelamento": codigo_cancelamento
        }

    def substituir_nfse(
        self,
        numero_nfse_substituida: str,
        nova_nfse: NFSeManaus
    ) -> Dict[str, Any]:
        """
        Substitui uma NFS-e por outra.

        Args:
            numero_nfse_substituida: Número da NFS-e a ser substituída
            nova_nfse: Dados da nova NFS-e

        Returns:
            Resultado da substituição
        """
        substituicao = ET.Element("SubstituirNfseEnvio", xmlns=self.NS_TIPOS)

        # Pedido de substituição
        pedido = ET.SubElement(substituicao, "SubstituicaoNfse")

        # NFS-e a ser substituída
        ET.SubElement(pedido, "NfseSubstituida").text = numero_nfse_substituida

        # Nova NFS-e (RPS)
        rps_xml = self.gerar_rps(nova_nfse)
        rps_element = ET.fromstring(rps_xml)
        pedido.append(rps_element)

        xml_str = ET.tostring(substituicao, encoding="unicode")
        xml_assinado = self.xml_signer.assinar_xml(xml_str, "SubstituicaoNfse")

        logger.info(f"Substituindo NFS-e {numero_nfse_substituida}")

        return {
            "xml_substituicao": xml_assinado,
            "numero_substituida": numero_nfse_substituida
        }

    def _montar_envelope_soap(
        self,
        operacao: str,
        xml_cabecalho: str,
        xml_dados: str
    ) -> str:
        """
        Monta envelope SOAP para comunicação com WebService.

        Args:
            operacao: Nome da operação (ex: RecepcionarLoteRps)
            xml_cabecalho: XML do cabeçalho ABRASF
            xml_dados: XML dos dados da requisição

        Returns:
            Envelope SOAP completo
        """
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:enf="{self.NS_WS}">
  <soap:Body>
    <enf:{operacao}.Execute>
      <enf:Nfsecabecmsg><![CDATA[{xml_cabecalho}]]></enf:Nfsecabecmsg>
      <enf:Nfsedadosmsg><![CDATA[{xml_dados}]]></enf:Nfsedadosmsg>
    </enf:{operacao}.Execute>
  </soap:Body>
</soap:Envelope>'''

    def _gerar_cabecalho(self) -> str:
        """Gera cabeçalho ABRASF 2.04."""
        return f'''<cabecalho xmlns="{self.NS_TIPOS}" versao="2.04"><versaoDados>2.04</versaoDados></cabecalho>'''

    def _get_url(self, operacao: str) -> str:
        """Retorna URL completa para operação."""
        endpoint = self.ENDPOINTS.get(operacao, "")
        return f"{self.url_base}{endpoint}"

    def _get_soap_action(self, operacao: str) -> str:
        """Retorna SOAPAction para operação."""
        endpoint = self.ENDPOINTS.get(operacao, "").upper()
        return f"http://www.e-nfs.com.braction{endpoint}.Execute"

    def enviar_requisicao(
        self,
        operacao: str,
        xml_dados: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Envia requisição SOAP para o WebService.

        Args:
            operacao: Nome da operação
            xml_dados: XML dos dados
            timeout: Timeout em segundos

        Returns:
            Resultado da requisição
        """
        import requests

        url = self._get_url(operacao)
        cabecalho = self._gerar_cabecalho()
        envelope = self._montar_envelope_soap(operacao, cabecalho, xml_dados)

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": self._get_soap_action(operacao),
        }

        logger.info(f"Enviando requisição {operacao} para {url}")

        try:
            response = requests.post(
                url,
                data=envelope.encode('utf-8'),
                headers=headers,
                timeout=timeout,
                cert=(self.cert_manager.get_cert_path(), self.cert_manager.get_key_path())
                if self.cert_manager else None
            )

            resultado = {
                "status_code": response.status_code,
                "operacao": operacao,
                "url": url,
                "resposta_raw": response.text,
            }

            # Parseia resposta
            if response.status_code == 200:
                if "Outputxml" in response.text:
                    import re
                    match = re.search(r'<Outputxml>(.*?)</Outputxml>', response.text, re.DOTALL)
                    if match:
                        resultado["outputxml"] = match.group(1)
                        resultado["sucesso"] = True
                elif "Fault" in response.text:
                    match = re.search(r'<faultstring>(.*?)</faultstring>', response.text, re.DOTALL)
                    if match:
                        resultado["erro"] = match.group(1)
                        resultado["sucesso"] = False

            return resultado

        except requests.RequestException as e:
            logger.error(f"Erro na requisição {operacao}: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "operacao": operacao
            }


# Códigos de serviço comuns para vigilância/segurança
CODIGOS_SERVICO_VIGILANCIA = {
    "11.02": "Vigilância, segurança ou monitoramento de bens, pessoas e semoventes",
    "11.03": "Escolta, inclusive de veículos e cargas",
    "11.04": "Armazenamento, depósito, carga, descarga, arrumação e guarda de bens",
    "11.05": "Serviços de transporte de valores",
}
