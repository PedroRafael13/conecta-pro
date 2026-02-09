"""
EFD-Reinf - Escrituração Fiscal Digital de Retenções e Outras Informações Fiscais.

Portal: https://reinf.receita.fazenda.gov.br/
Versão: 2.1.2

Eventos:
- R-1000: Informações do Contribuinte
- R-1070: Tabela de Processos Administrativos/Judiciais
- R-2010: Retenção Contribuição Previdenciária - Serviços Tomados
- R-2020: Retenção Contribuição Previdenciária - Serviços Prestados
- R-2030: Recursos Recebidos por Associação Desportiva
- R-2040: Recursos Repassados para Associação Desportiva
- R-2050: Comercialização da Produção Rural PF
- R-2055: Aquisição de Produção Rural
- R-2060: Contribuição Previdenciária sobre Receita Bruta (CPRB)
- R-2098: Reabertura dos Eventos Periódicos
- R-2099: Fechamento dos Eventos Periódicos
- R-3010: Receita de Espetáculos Desportivos
- R-4010: Pagamentos/créditos a beneficiário PF
- R-4020: Pagamentos/créditos a beneficiário PJ
- R-4040: Pagamentos/créditos a beneficiários não identificados
- R-4080: Retenção no recebimento
- R-4099: Fechamento/reabertura dos eventos série R-4000
- R-9000: Exclusão de eventos
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from xml.etree.ElementTree import Element, SubElement  # noqa: S405

import defusedxml.ElementTree as ET  # noqa: N817

from .certificate_manager import CertificateManager
from .xml_signer import XMLSigner

logger = logging.getLogger(__name__)


class TipoAmbiente(StrEnum):
    """Tipo de ambiente EFD-Reinf."""

    PRODUCAO = "1"
    PRODUCAO_RESTRITA = "2"


class TipoInscricao(StrEnum):
    """Tipo de inscrição."""

    CNPJ = "1"
    CPF = "2"


class IndRetificacao(StrEnum):
    """Indicador de retificação."""

    ORIGINAL = "1"
    RETIFICADOR = "2"


class ClassificacaoTributaria(StrEnum):
    """Classificação tributária."""

    EMPRESA_GERAL = "01"
    EMPRESA_SIMPLES = "02"
    MEI = "03"
    PRODUTOR_RURAL_PJ = "04"
    AGROINDÚSTRIA = "06"
    PRODUTOR_RURAL_PF = "07"
    CONSORCIO = "08"
    ENTIDADE_IMUNE = "09"
    MISSAO_DIPLOMATICA = "10"
    ORGAO_PUBLICO = "11"


@dataclass
class InfoContribuinte:
    """Informações do contribuinte (R-1000)."""

    cnpj: str
    razao_social: str
    classificacao_tributaria: ClassificacaoTributaria
    inicio_validade: str  # YYYY-MM
    fim_validade: str | None = None
    natureza_juridica: str | None = None
    ind_coop: str = "0"  # 0=Não é cooperativa
    ind_constr: str = "0"  # 0=Não é construtora
    ind_desoneracao: str = "0"  # 0=Não é desonerado
    telefone: str | None = None
    email: str | None = None


@dataclass
class RetencaoServico:
    """Retenção de contribuição previdenciária sobre serviço."""

    cnpj_prestador: str
    valor_bruto: Decimal
    valor_base_retencao: Decimal
    valor_retencao: Decimal  # 11% ou 3.5% (simples)
    valor_retencao_adicional: Decimal = Decimal("0")
    valor_nf_retido: Decimal = Decimal("0")
    serie_nf: str = ""
    numero_nf: str = ""
    data_emissao_nf: date | None = None
    codigo_servico: str | None = None
    ind_cprb: str = "0"  # 0=Não é CPRB


@dataclass
class PagamentoBeneficiarioPF:
    """Pagamento a beneficiário pessoa física (R-4010)."""

    cpf_beneficiario: str
    nome_beneficiario: str
    natureza_rendimento: str  # Código da natureza
    valor_bruto: Decimal
    valor_irrf: Decimal = Decimal("0")
    valor_inss: Decimal = Decimal("0")
    data_pagamento: date = field(default_factory=date.today)
    descricao: str | None = None


@dataclass
class PagamentoBeneficiarioPJ:
    """Pagamento a beneficiário pessoa jurídica (R-4020)."""

    cnpj_beneficiario: str
    razao_social: str
    natureza_rendimento: str
    valor_bruto: Decimal
    valor_irrf: Decimal = Decimal("0")
    valor_csll: Decimal = Decimal("0")
    valor_cofins: Decimal = Decimal("0")
    valor_pis: Decimal = Decimal("0")
    data_pagamento: date = field(default_factory=date.today)
    numero_nf: str | None = None


class EFDReinfManager:
    """
    Gerenciador EFD-Reinf.

    Responsável por gerar e transmitir eventos da EFD-Reinf.
    """

    # URLs dos WebServices
    URL_PRODUCAO = "https://reinf.receita.fazenda.gov.br/WsREINF/RecepcaoLoteReinf.svc"
    URL_PRODUCAO_RESTRITA = "https://preproducao.reinf.receita.fazenda.gov.br/WsREINF/RecepcaoLoteReinf.svc"

    # Namespace
    NS_REINF = "http://www.reinf.esocial.gov.br/schemas/envioLoteEventos/v1_00_00"
    NS_EVENTOS = "http://www.reinf.esocial.gov.br/schemas"

    # Versão do layout
    VERSAO = "2_01_02"

    def __init__(
        self,
        certificate_manager: CertificateManager | None = None,
        ambiente: TipoAmbiente = TipoAmbiente.PRODUCAO_RESTRITA,
        cnpj: str = "",
    ):
        """
        Inicializa o gerenciador.

        Args:
            certificate_manager: Gerenciador de certificados (opcional)
            ambiente: Ambiente (produção ou produção restrita)
            cnpj: CNPJ do contribuinte
        """
        self.cert_manager = certificate_manager
        self.ambiente = ambiente
        self.cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
        self.xml_signer = XMLSigner(certificate_manager) if certificate_manager else None

        self.url = self.URL_PRODUCAO if ambiente == TipoAmbiente.PRODUCAO else self.URL_PRODUCAO_RESTRITA

    def _gerar_id_evento(self, tipo_evento: str) -> str:
        """Gera ID único do evento."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        sequencial = hashlib.sha256(f"{self.cnpj}{timestamp}".encode()).hexdigest()[:5]
        return f"ID{tipo_evento}{self.cnpj}{timestamp}{sequencial}"

    def gerar_r1000(
        self,
        info: InfoContribuinte,
        ind_retificacao: IndRetificacao = IndRetificacao.ORIGINAL,
        _nr_recibo: str | None = None,
    ) -> str:
        """
        Gera evento R-1000 - Informações do Contribuinte.

        Args:
            info: Informações do contribuinte
            ind_retificacao: Original ou retificador
            nr_recibo: Número do recibo (para retificação)

        Returns:
            XML do evento
        """
        id_evento = self._gerar_id_evento("1000")

        reinf = Element("Reinf", xmlns=f"{self.NS_EVENTOS}/evtInfoContribuinte/v{self.VERSAO}")

        evt = SubElement(reinf, "evtInfoContri", id=id_evento)

        # ideEvento
        ide_evento = SubElement(evt, "ideEvento")
        SubElement(ide_evento, "tpAmb").text = self.ambiente.value
        SubElement(ide_evento, "procEmi").text = "1"  # Aplicativo do contribuinte
        SubElement(ide_evento, "verProc").text = "CONECTA_PRO_1.0"

        # ideContri
        ide_contri = SubElement(evt, "ideContri")
        SubElement(ide_contri, "tpInsc").text = TipoInscricao.CNPJ.value
        SubElement(ide_contri, "nrInsc").text = self.cnpj[:8]  # Raiz CNPJ

        # infoContri
        info_contri = SubElement(evt, "infoContri")

        # Inclusão
        inclusao = SubElement(info_contri, "inclusao")
        ide_periodo = SubElement(inclusao, "idePeriodo")
        SubElement(ide_periodo, "iniValid").text = info.inicio_validade
        if info.fim_validade:
            SubElement(ide_periodo, "fimValid").text = info.fim_validade

        info_cadastro = SubElement(inclusao, "infoCadastro")
        SubElement(info_cadastro, "classTrib").text = info.classificacao_tributaria.value
        SubElement(info_cadastro, "indEscrituracao").text = "1"
        SubElement(info_cadastro, "indDesoneracao").text = info.ind_desoneracao
        SubElement(info_cadastro, "indAcordoIsenMulta").text = "0"

        contato = SubElement(info_cadastro, "contato")
        SubElement(contato, "nmCtt").text = info.razao_social[:70]
        SubElement(contato, "cpfCtt").text = "00000000000"  # CPF do contato
        if info.telefone:
            SubElement(contato, "foneFixo").text = info.telefone
        if info.email:
            SubElement(contato, "email").text = info.email

        xml_str = ET.tostring(reinf, encoding="unicode")
        if self.xml_signer:
            return self.xml_signer.sign(xml_str, "evtInfoContri")
        return xml_str

    def gerar_r2010(
        self,
        periodo_apuracao: str,
        retencoes: list[RetencaoServico],
        ind_retificacao: IndRetificacao = IndRetificacao.ORIGINAL,
    ) -> str:
        """
        Gera evento R-2010 - Retenção Contribuição Previdenciária - Serviços Tomados.

        Args:
            periodo_apuracao: Período no formato YYYY-MM
            retencoes: Lista de retenções
            ind_retificacao: Original ou retificador

        Returns:
            XML do evento
        """
        id_evento = self._gerar_id_evento("2010")

        reinf = Element("Reinf", xmlns=f"{self.NS_EVENTOS}/evtServTom/v{self.VERSAO}")

        evt = SubElement(reinf, "evtServTom", id=id_evento)

        # ideEvento
        ide_evento = SubElement(evt, "ideEvento")
        SubElement(ide_evento, "indRetif").text = ind_retificacao.value
        SubElement(ide_evento, "perApur").text = periodo_apuracao
        SubElement(ide_evento, "tpAmb").text = self.ambiente.value
        SubElement(ide_evento, "procEmi").text = "1"
        SubElement(ide_evento, "verProc").text = "CONECTA_PRO_1.0"

        # ideContri
        ide_contri = SubElement(evt, "ideContri")
        SubElement(ide_contri, "tpInsc").text = TipoInscricao.CNPJ.value
        SubElement(ide_contri, "nrInsc").text = self.cnpj[:8]

        # infoServTom
        info_serv = SubElement(evt, "infoServTom")

        # Agrupa por prestador
        prestadores = {}
        for ret in retencoes:
            if ret.cnpj_prestador not in prestadores:
                prestadores[ret.cnpj_prestador] = []
            prestadores[ret.cnpj_prestador].append(ret)

        for cnpj_prest, lista_ret in prestadores.items():
            ide_estab = SubElement(info_serv, "ideEstabObra")
            SubElement(ide_estab, "tpInscEstab").text = "1"
            SubElement(ide_estab, "nrInscEstab").text = self.cnpj

            ide_prest = SubElement(ide_estab, "idePrestServ")
            SubElement(ide_prest, "cnpjPrestador").text = cnpj_prest

            for ret in lista_ret:
                nfs = SubElement(ide_prest, "nfs")
                SubElement(nfs, "serie").text = ret.serie_nf or "1"
                SubElement(nfs, "numDocto").text = ret.numero_nf
                if ret.data_emissao_nf:
                    SubElement(nfs, "dtEmissaoNF").text = ret.data_emissao_nf.strftime("%Y-%m-%d")
                SubElement(nfs, "vlrBruto").text = str(ret.valor_bruto)
                SubElement(nfs, "indCPRB").text = ret.ind_cprb

                info_tpserv = SubElement(nfs, "infoTpServ")
                SubElement(info_tpserv, "tpServico").text = ret.codigo_servico or "100000001"
                SubElement(info_tpserv, "vlrBaseRet").text = str(ret.valor_base_retencao)
                SubElement(info_tpserv, "vlrRetencao").text = str(ret.valor_retencao)
                if ret.valor_retencao_adicional > 0:
                    SubElement(info_tpserv, "vlrRetSub").text = str(ret.valor_retencao_adicional)

        xml_str = ET.tostring(reinf, encoding="unicode")
        if self.xml_signer:
            return self.xml_signer.sign(xml_str, "evtServTom")
        return xml_str

    def gerar_r4010(
        self,
        periodo_apuracao: str,
        pagamentos: list[PagamentoBeneficiarioPF],
        ind_retificacao: IndRetificacao = IndRetificacao.ORIGINAL,
    ) -> str:
        """
        Gera evento R-4010 - Pagamentos/créditos a beneficiário pessoa física.

        Args:
            periodo_apuracao: Período no formato YYYY-MM
            pagamentos: Lista de pagamentos
            ind_retificacao: Original ou retificador

        Returns:
            XML do evento
        """
        id_evento = self._gerar_id_evento("4010")

        reinf = Element("Reinf", xmlns=f"{self.NS_EVENTOS}/evt4010PagtoBeneficiarioPF/v{self.VERSAO}")

        evt = SubElement(reinf, "evt4010", id=id_evento)

        # ideEvento
        ide_evento = SubElement(evt, "ideEvento")
        SubElement(ide_evento, "indRetif").text = ind_retificacao.value
        SubElement(ide_evento, "perApur").text = periodo_apuracao
        SubElement(ide_evento, "tpAmb").text = self.ambiente.value
        SubElement(ide_evento, "procEmi").text = "1"
        SubElement(ide_evento, "verProc").text = "CONECTA_PRO_1.0"

        # ideContri
        ide_contri = SubElement(evt, "ideContri")
        SubElement(ide_contri, "tpInsc").text = TipoInscricao.CNPJ.value
        SubElement(ide_contri, "nrInsc").text = self.cnpj[:8]

        # ideBenef
        for pag in pagamentos:
            ide_benef = SubElement(evt, "ideBenef")
            SubElement(ide_benef, "cpfBenef").text = pag.cpf_beneficiario
            SubElement(ide_benef, "nmBenef").text = pag.nome_beneficiario

            ide_pgto = SubElement(ide_benef, "idePgto")
            SubElement(ide_pgto, "natRend").text = pag.natureza_rendimento
            SubElement(ide_pgto, "dtPgto").text = pag.data_pagamento.strftime("%Y-%m-%d")

            info_pgto = SubElement(ide_pgto, "infoPgto")
            SubElement(info_pgto, "vlrRendBruto").text = str(pag.valor_bruto)
            if pag.valor_irrf > 0:
                SubElement(info_pgto, "vlrIR").text = str(pag.valor_irrf)

        xml_str = ET.tostring(reinf, encoding="unicode")
        if self.xml_signer:
            return self.xml_signer.sign(xml_str, "evt4010")
        return xml_str

    def gerar_r4020(
        self,
        periodo_apuracao: str,
        pagamentos: list[PagamentoBeneficiarioPJ],
        ind_retificacao: IndRetificacao = IndRetificacao.ORIGINAL,
    ) -> str:
        """
        Gera evento R-4020 - Pagamentos/créditos a beneficiário pessoa jurídica.

        Args:
            periodo_apuracao: Período no formato YYYY-MM
            pagamentos: Lista de pagamentos
            ind_retificacao: Original ou retificador

        Returns:
            XML do evento
        """
        id_evento = self._gerar_id_evento("4020")

        reinf = Element("Reinf", xmlns=f"{self.NS_EVENTOS}/evt4020PagtoBeneficiarioPJ/v{self.VERSAO}")

        evt = SubElement(reinf, "evt4020", id=id_evento)

        # ideEvento
        ide_evento = SubElement(evt, "ideEvento")
        SubElement(ide_evento, "indRetif").text = ind_retificacao.value
        SubElement(ide_evento, "perApur").text = periodo_apuracao
        SubElement(ide_evento, "tpAmb").text = self.ambiente.value
        SubElement(ide_evento, "procEmi").text = "1"
        SubElement(ide_evento, "verProc").text = "CONECTA_PRO_1.0"

        # ideContri
        ide_contri = SubElement(evt, "ideContri")
        SubElement(ide_contri, "tpInsc").text = TipoInscricao.CNPJ.value
        SubElement(ide_contri, "nrInsc").text = self.cnpj[:8]

        # ideBenef
        for pag in pagamentos:
            ide_benef = SubElement(evt, "ideBenef")
            SubElement(ide_benef, "cnpjBenef").text = pag.cnpj_beneficiario
            SubElement(ide_benef, "nmBenef").text = pag.razao_social

            ide_pgto = SubElement(ide_benef, "idePgto")
            SubElement(ide_pgto, "natRend").text = pag.natureza_rendimento
            SubElement(ide_pgto, "dtPgto").text = pag.data_pagamento.strftime("%Y-%m-%d")

            info_pgto = SubElement(ide_pgto, "infoPgto")
            SubElement(info_pgto, "vlrRendBruto").text = str(pag.valor_bruto)

            # Retenções
            retencoes = SubElement(info_pgto, "retencoes")
            SubElement(retencoes, "vlrIR").text = str(pag.valor_irrf)
            SubElement(retencoes, "vlrCSLL").text = str(pag.valor_csll)
            SubElement(retencoes, "vlrCofins").text = str(pag.valor_cofins)
            SubElement(retencoes, "vlrPP").text = str(pag.valor_pis)

        xml_str = ET.tostring(reinf, encoding="unicode")
        if self.xml_signer:
            return self.xml_signer.sign(xml_str, "evt4020")
        return xml_str

    def gerar_r2099(
        self,
        periodo_apuracao: str,
        ind_retificacao: IndRetificacao = IndRetificacao.ORIGINAL,
    ) -> str:
        """
        Gera evento R-2099 - Fechamento dos Eventos Periódicos.

        Args:
            periodo_apuracao: Período no formato YYYY-MM
            ind_retificacao: Original ou retificador

        Returns:
            XML do evento
        """
        id_evento = self._gerar_id_evento("2099")

        reinf = Element("Reinf", xmlns=f"{self.NS_EVENTOS}/evtFechamento/v{self.VERSAO}")

        evt = SubElement(reinf, "evtFechaEvPer", id=id_evento)

        # ideEvento
        ide_evento = SubElement(evt, "ideEvento")
        SubElement(ide_evento, "perApur").text = periodo_apuracao
        SubElement(ide_evento, "tpAmb").text = self.ambiente.value
        SubElement(ide_evento, "procEmi").text = "1"
        SubElement(ide_evento, "verProc").text = "CONECTA_PRO_1.0"

        # ideContri
        ide_contri = SubElement(evt, "ideContri")
        SubElement(ide_contri, "tpInsc").text = TipoInscricao.CNPJ.value
        SubElement(ide_contri, "nrInsc").text = self.cnpj[:8]

        # ideRespInf
        ide_resp = SubElement(evt, "ideRespInf")
        SubElement(ide_resp, "nmResp").text = "SISTEMA CONECTA PRO"
        SubElement(ide_resp, "cpfResp").text = "00000000000"
        SubElement(ide_resp, "telefone").text = "0000000000"
        SubElement(ide_resp, "email").text = "sistema@conectapro.com.br"

        # infoFech
        info_fech = SubElement(evt, "infoFech")
        SubElement(info_fech, "evtServTm").text = "N"  # Sem eventos R-2010
        SubElement(info_fech, "evtServPr").text = "N"  # Sem eventos R-2020
        SubElement(info_fech, "evtAssDespRec").text = "N"
        SubElement(info_fech, "evtAssDespRep").text = "N"
        SubElement(info_fech, "evtComProd").text = "N"
        SubElement(info_fech, "evtCPRB").text = "N"
        SubElement(info_fech, "evtPgtos").text = "N"

        xml_str = ET.tostring(reinf, encoding="unicode")
        if self.xml_signer:
            return self.xml_signer.sign(xml_str, "evtFechaEvPer")
        return xml_str

    def enviar_lote(self, eventos: list[str]) -> dict[str, Any]:
        """
        Envia lote de eventos para a Receita Federal.

        Args:
            eventos: Lista de XMLs de eventos assinados

        Returns:
            Resultado do envio
        """
        # Monta envelope SOAP
        lote = Element("envioLoteEventos", xmlns=self.NS_REINF)
        SubElement(lote, "ideContribuinte")

        eventos_element = SubElement(lote, "eventos")
        for i, evt_xml in enumerate(eventos):
            evento = SubElement(eventos_element, "evento", Id=f"ID{i + 1}")
            evt_element = ET.fromstring(evt_xml)
            evento.append(evt_element)

        xml_str = ET.tostring(lote, encoding="unicode")

        logger.info(f"Enviando lote EFD-Reinf com {len(eventos)} eventos")

        return {
            "xml_envio": xml_str,
            "quantidade_eventos": len(eventos),
            "ambiente": self.ambiente.value,
            "status": "pendente",
        }


# Naturezas de rendimento comuns
NATUREZAS_RENDIMENTO = {
    # Pessoa Física
    "10001": "Aluguéis e royalties pagos à PF",
    "10002": "Serviços de transporte de cargas",
    "10003": "Serviços de transporte de passageiros",
    "10004": "Serviços prestados por associados de cooperativas de trabalho",
    "10005": "Honorários de profissões regulamentadas",
    "10006": "Serviços de publicidade e propaganda",
    "10007": "Comissões e corretagens",
    "10008": "Serviços pessoais prestados por autônomos",
    # Pessoa Jurídica
    "15001": "Aluguéis e royalties pagos à PJ",
    "15002": "Juros e indenizações por lucros cessantes",
    "15003": "Importâncias pagas/creditadas a cooperativas de trabalho",
    "15004": "Serviços de limpeza, conservação, segurança e vigilância",
    "15005": "Assessoria creditícia, mercadológica, gestão de crédito",
    "15006": "Serviços profissionais",
}
