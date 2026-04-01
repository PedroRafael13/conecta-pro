"""
CT-e - Conhecimento de Transporte Eletrônico.

Portal: https://www.cte.fazenda.gov.br/
Documentação: Manual de Orientação do Contribuinte CT-e

O CT-e documenta prestação de serviço de transporte:
- Rodoviário de Cargas
- Aéreo
- Aquaviário
- Ferroviário
- Dutoviário

Eventos:
- Cancelamento
- Carta de Correção
- EPEC (Evento Prévio de Emissão em Contingência)
- Prestação em Desacordo
- GTV (Guia de Transporte de Valores)
"""

import logging
import xml.etree.ElementTree as ET  # noqa: S405
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class ModalTransporte(StrEnum):
    """Modal de transporte."""

    RODOVIARIO = "01"
    AEREO = "02"
    AQUAVIARIO = "03"
    FERROVIARIO = "04"
    DUTOVIARIO = "05"
    MULTIMODAL = "06"


class TipoServico(StrEnum):
    """Tipo de serviço de transporte."""

    NORMAL = "0"
    SUBCONTRATACAO = "1"
    REDESPACHO = "2"
    REDESPACHO_INTERMEDIARIO = "3"
    SERVICO_VINCULADO_MULTIMODAL = "4"


class TomadorServico(StrEnum):
    """Indicador do tomador do serviço."""

    REMETENTE = "0"
    EXPEDIDOR = "1"
    RECEBEDOR = "2"
    DESTINATARIO = "3"
    OUTROS = "4"


class SituacaoCTe(StrEnum):
    """Situação do CT-e."""

    EM_DIGITACAO = "em_digitacao"
    ASSINADO = "assinado"
    AUTORIZADO = "autorizado"
    CANCELADO = "cancelado"
    DENEGADO = "denegado"
    REJEITADO = "rejeitado"


@dataclass
class Participante:
    """Participante do CT-e."""

    tipo: str  # remetente, destinatario, expedidor, recebedor
    cnpj_cpf: str
    nome: str
    inscricao_estadual: str | None = None
    endereco: str | None = None
    numero: str | None = None
    bairro: str | None = None
    codigo_municipio: str | None = None
    municipio: str | None = None
    uf: str | None = None
    cep: str | None = None
    telefone: str | None = None
    email: str | None = None


@dataclass
class NFReferenciada:
    """NF-e referenciada no CT-e."""

    chave: str
    pin: str | None = None  # PIN SUFRAMA se aplicável


@dataclass
class Carga:
    """Informações da carga."""

    valor_total_carga: Decimal
    produto_predominante: str
    peso_bruto: Decimal = Decimal("0")
    peso_cubado: Decimal = Decimal("0")
    peso_aferido: Decimal = Decimal("0")
    quantidade_volumes: int = 0
    unidade_medida: str = "KG"


@dataclass
class ComponenteValor:
    """Componente de valor do frete."""

    nome: str
    valor: Decimal


@dataclass
class CTe:
    """Conhecimento de Transporte Eletrônico."""

    # Identificação
    chave: str | None = None
    numero: int = 0
    serie: int = 1
    modelo: str = "57"
    data_emissao: datetime = field(default_factory=datetime.now)

    # Tipo
    modal: ModalTransporte = ModalTransporte.RODOVIARIO
    tipo_servico: TipoServico = TipoServico.NORMAL
    tomador: TomadorServico = TomadorServico.REMETENTE

    # Municípios
    municipio_inicio: str = ""
    uf_inicio: str = ""
    municipio_fim: str = ""
    uf_fim: str = ""

    # Participantes
    remetente: Participante | None = None
    destinatario: Participante | None = None
    expedidor: Participante | None = None
    recebedor: Participante | None = None

    # Documentos
    nf_referenciadas: list[NFReferenciada] = field(default_factory=list)

    # Carga
    carga: Carga | None = None

    # Valores
    valor_total_servico: Decimal = Decimal("0")
    valor_receber: Decimal = Decimal("0")
    componentes_valor: list[ComponenteValor] = field(default_factory=list)

    # Tributos
    icms_base_calculo: Decimal = Decimal("0")
    icms_aliquota: Decimal = Decimal("0")
    icms_valor: Decimal = Decimal("0")
    icms_cst: str = "00"

    # Situação
    situacao: SituacaoCTe = SituacaoCTe.EM_DIGITACAO
    protocolo_autorizacao: str | None = None
    data_autorizacao: datetime | None = None

    # XML
    xml_assinado: str | None = None
    xml_protocolo: str | None = None


class CTeManager:
    """
    Gerenciador de CT-e.

    Emite, consulta e gerencia CT-e.
    """

    # URLs SEFAZ
    URLS_PRODUCAO = {
        "AM": "https://cte.sefaz.am.gov.br/cte/services/CTeRecepcaoSinc",
        "MT": "https://cte.sefaz.mt.gov.br/ctews2/services/CTeRecepcaoSinc",
        "RS": "https://cte.sefaz.rs.gov.br/ws/CTeRecepcaoSinc/CTeRecepcaoSinc.asmx",
        "SP": "https://nfe.fazenda.sp.gov.br/cteWEB/services/CTeRecepcaoSinc.asmx",
        "SVRS": "https://cte.svrs.rs.gov.br/ws/CTeRecepcaoSinc/CTeRecepcaoSinc.asmx",
    }

    URLS_HOMOLOGACAO = {
        "AM": "https://cte.sefaz.am.gov.br/cte-hom/services/CTeRecepcaoSinc",
        "SVRS": "https://cte-homologacao.svrs.rs.gov.br/ws/CTeRecepcaoSinc/CTeRecepcaoSinc.asmx",
    }

    # Namespace
    NS_CTE = "http://www.portalfiscal.inf.br/cte"

    def __init__(
        self,
        cnpj: str,
        razao_social: str,
        inscricao_estadual: str,
        uf: str,
        ambiente: str = "producao",
    ):
        """
        Inicializa o gerenciador.

        Args:
            cnpj: CNPJ do emitente
            razao_social: Razão social
            inscricao_estadual: Inscrição Estadual
            uf: UF do emitente
            ambiente: 'producao' ou 'homologacao'
        """
        self.cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
        self.razao_social = razao_social
        self.ie = inscricao_estadual.replace(".", "").replace("-", "")
        self.uf = uf
        self.ambiente = ambiente
        self.tipo_ambiente = "1" if ambiente == "producao" else "2"

    def criar_cte(self, numero: int, serie: int = 1, modal: ModalTransporte = ModalTransporte.RODOVIARIO) -> CTe:
        """
        Cria um novo CT-e.

        Args:
            numero: Número do CT-e
            serie: Série
            modal: Modal de transporte

        Returns:
            CT-e criado
        """
        cte = CTe(
            numero=numero,
            serie=serie,
            modal=modal,
            uf_inicio=self.uf,
        )

        logger.info(f"Criado CT-e nº {numero}")
        return cte

    def gerar_xml(self, cte: CTe) -> str:
        """
        Gera XML do CT-e.

        Args:
            cte: CT-e a ser gerado

        Returns:
            XML gerado
        """
        # Cria elemento raiz
        cte_xml = ET.Element("CTe", xmlns=self.NS_CTE)

        # infCte
        inf_cte = ET.SubElement(cte_xml, "infCte", versao="4.00")

        # Identificação
        ide = ET.SubElement(inf_cte, "ide")
        ET.SubElement(ide, "cUF").text = self._codigo_uf(self.uf)
        ET.SubElement(ide, "cCT").text = str(cte.numero).zfill(8)
        ET.SubElement(ide, "CFOP").text = "6353"  # Prestação serviço transporte interestadual
        ET.SubElement(ide, "natOp").text = "PRESTACAO DE SERVICO DE TRANSPORTE"
        ET.SubElement(ide, "mod").text = cte.modelo
        ET.SubElement(ide, "serie").text = str(cte.serie)
        ET.SubElement(ide, "nCT").text = str(cte.numero)
        ET.SubElement(ide, "dhEmi").text = cte.data_emissao.strftime("%Y-%m-%dT%H:%M:%S-04:00")
        ET.SubElement(ide, "tpImp").text = "1"  # DACTE retrato
        ET.SubElement(ide, "tpEmis").text = "1"  # Normal
        ET.SubElement(ide, "cDV").text = "0"  # Dígito verificador (calculado depois)
        ET.SubElement(ide, "tpAmb").text = self.tipo_ambiente
        ET.SubElement(ide, "tpCTe").text = "0"  # CT-e Normal
        ET.SubElement(ide, "procEmi").text = "0"  # Aplicativo do contribuinte
        ET.SubElement(ide, "verProc").text = "ConectaPRO 1.0"
        ET.SubElement(ide, "cMunEnv").text = cte.municipio_inicio or "1302603"
        ET.SubElement(ide, "xMunEnv").text = "MANAUS"
        ET.SubElement(ide, "UFEnv").text = self.uf
        ET.SubElement(ide, "modal").text = cte.modal.value
        ET.SubElement(ide, "tpServ").text = cte.tipo_servico.value
        ET.SubElement(ide, "cMunIni").text = cte.municipio_inicio or "1302603"
        ET.SubElement(ide, "xMunIni").text = "MANAUS"
        ET.SubElement(ide, "UFIni").text = cte.uf_inicio
        ET.SubElement(ide, "cMunFim").text = cte.municipio_fim or "1302603"
        ET.SubElement(ide, "xMunFim").text = "MANAUS"
        ET.SubElement(ide, "UFFim").text = cte.uf_fim or self.uf
        ET.SubElement(ide, "retira").text = "0"  # Sem retira
        ET.SubElement(ide, "indIEToma").text = "1"  # Contribuinte ICMS

        # Tomador
        toma3 = ET.SubElement(ide, "toma3")
        ET.SubElement(toma3, "toma").text = cte.tomador.value

        # Emitente
        emit = ET.SubElement(inf_cte, "emit")
        ET.SubElement(emit, "CNPJ").text = self.cnpj
        ET.SubElement(emit, "IE").text = self.ie
        ET.SubElement(emit, "xNome").text = self.razao_social
        ET.SubElement(emit, "xFant").text = self.razao_social

        emit_ender = ET.SubElement(emit, "enderEmit")
        ET.SubElement(emit_ender, "xLgr").text = "RUA EXEMPLO"
        ET.SubElement(emit_ender, "nro").text = "100"
        ET.SubElement(emit_ender, "xBairro").text = "CENTRO"
        ET.SubElement(emit_ender, "cMun").text = "1302603"
        ET.SubElement(emit_ender, "xMun").text = "MANAUS"
        ET.SubElement(emit_ender, "CEP").text = "69000000"
        ET.SubElement(emit_ender, "UF").text = self.uf
        ET.SubElement(emit_ender, "fone").text = "9200000000"

        # Remetente
        if cte.remetente:
            rem = ET.SubElement(inf_cte, "rem")
            if len(cte.remetente.cnpj_cpf) == 14:
                ET.SubElement(rem, "CNPJ").text = cte.remetente.cnpj_cpf
            else:
                ET.SubElement(rem, "CPF").text = cte.remetente.cnpj_cpf
            if cte.remetente.inscricao_estadual:
                ET.SubElement(rem, "IE").text = cte.remetente.inscricao_estadual
            ET.SubElement(rem, "xNome").text = cte.remetente.nome

            rem_ender = ET.SubElement(rem, "enderReme")
            ET.SubElement(rem_ender, "xLgr").text = cte.remetente.endereco or "RUA"
            ET.SubElement(rem_ender, "nro").text = cte.remetente.numero or "S/N"
            ET.SubElement(rem_ender, "xBairro").text = cte.remetente.bairro or "CENTRO"
            ET.SubElement(rem_ender, "cMun").text = cte.remetente.codigo_municipio or "1302603"
            ET.SubElement(rem_ender, "xMun").text = cte.remetente.municipio or "MANAUS"
            ET.SubElement(rem_ender, "CEP").text = cte.remetente.cep or "69000000"
            ET.SubElement(rem_ender, "UF").text = cte.remetente.uf or self.uf

        # Destinatário
        if cte.destinatario:
            dest = ET.SubElement(inf_cte, "dest")
            if len(cte.destinatario.cnpj_cpf) == 14:
                ET.SubElement(dest, "CNPJ").text = cte.destinatario.cnpj_cpf
            else:
                ET.SubElement(dest, "CPF").text = cte.destinatario.cnpj_cpf
            if cte.destinatario.inscricao_estadual:
                ET.SubElement(dest, "IE").text = cte.destinatario.inscricao_estadual
            ET.SubElement(dest, "xNome").text = cte.destinatario.nome

            dest_ender = ET.SubElement(dest, "enderDest")
            ET.SubElement(dest_ender, "xLgr").text = cte.destinatario.endereco or "RUA"
            ET.SubElement(dest_ender, "nro").text = cte.destinatario.numero or "S/N"
            ET.SubElement(dest_ender, "xBairro").text = cte.destinatario.bairro or "CENTRO"
            ET.SubElement(dest_ender, "cMun").text = cte.destinatario.codigo_municipio or "1302603"
            ET.SubElement(dest_ender, "xMun").text = cte.destinatario.municipio or "MANAUS"
            ET.SubElement(dest_ender, "CEP").text = cte.destinatario.cep or "69000000"
            ET.SubElement(dest_ender, "UF").text = cte.destinatario.uf or self.uf

        # Valores
        v_prest = ET.SubElement(inf_cte, "vPrest")
        ET.SubElement(v_prest, "vTPrest").text = f"{cte.valor_total_servico:.2f}"
        ET.SubElement(v_prest, "vRec").text = f"{cte.valor_receber:.2f}"

        for comp in cte.componentes_valor:
            comp_elem = ET.SubElement(v_prest, "Comp")
            ET.SubElement(comp_elem, "xNome").text = comp.nome
            ET.SubElement(comp_elem, "vComp").text = f"{comp.valor:.2f}"

        # ICMS
        imp = ET.SubElement(inf_cte, "imp")
        icms = ET.SubElement(imp, "ICMS")
        icms00 = ET.SubElement(icms, f"ICMS{cte.icms_cst}")
        ET.SubElement(icms00, "CST").text = cte.icms_cst
        ET.SubElement(icms00, "vBC").text = f"{cte.icms_base_calculo:.2f}"
        ET.SubElement(icms00, "pICMS").text = f"{cte.icms_aliquota:.2f}"
        ET.SubElement(icms00, "vICMS").text = f"{cte.icms_valor:.2f}"

        # Info CTe Normal
        inf_cte_norm = ET.SubElement(inf_cte, "infCTeNorm")

        # Info Carga
        if cte.carga:
            inf_carga = ET.SubElement(inf_cte_norm, "infCarga")
            ET.SubElement(inf_carga, "vCarga").text = f"{cte.carga.valor_total_carga:.2f}"
            ET.SubElement(inf_carga, "proPred").text = cte.carga.produto_predominante

            inf_q = ET.SubElement(inf_carga, "infQ")
            ET.SubElement(inf_q, "cUnid").text = "01"  # KG
            ET.SubElement(inf_q, "tpMed").text = "PESO BRUTO"
            ET.SubElement(inf_q, "qCarga").text = f"{cte.carga.peso_bruto:.4f}"

        # Info documentos (NF-e)
        if cte.nf_referenciadas:
            inf_doc = ET.SubElement(inf_cte_norm, "infDoc")
            for nf in cte.nf_referenciadas:
                inf_nfe = ET.SubElement(inf_doc, "infNFe")
                ET.SubElement(inf_nfe, "chave").text = nf.chave

        # Info Modal (rodoviário)
        if cte.modal == ModalTransporte.RODOVIARIO:
            inf_modal = ET.SubElement(inf_cte_norm, "infModal", versaoModal="4.00")
            rodo = ET.SubElement(inf_modal, "rodo")
            ET.SubElement(rodo, "RNTRC").text = "00000000"  # RNTRC

        # Converte para string
        xml_str = ET.tostring(cte_xml, encoding="unicode")
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>' + xml_str

        logger.info(f"Gerado XML CT-e nº {cte.numero}")
        return xml_str

    def consultar_status_servico(self) -> dict[str, Any]:
        """
        Consulta status do serviço CT-e na SEFAZ.

        Returns:
            Status do serviço
        """
        url = self.URLS_PRODUCAO.get(self.uf, self.URLS_PRODUCAO["SVRS"])
        if self.ambiente == "homologacao":
            url = self.URLS_HOMOLOGACAO.get(self.uf, self.URLS_HOMOLOGACAO["SVRS"])

        return {
            "servico": "CTeStatusServico",
            "url": url,
            "status": "pendente",
            "mensagem": "Implementar consulta via WebService",
        }

    def _codigo_uf(self, uf: str) -> str:
        """Retorna código IBGE da UF."""
        codigos = {
            "AC": "12",
            "AL": "27",
            "AP": "16",
            "AM": "13",
            "BA": "29",
            "CE": "23",
            "DF": "53",
            "ES": "32",
            "GO": "52",
            "MA": "21",
            "MT": "51",
            "MS": "50",
            "MG": "31",
            "PA": "15",
            "PB": "25",
            "PR": "41",
            "PE": "26",
            "PI": "22",
            "RJ": "33",
            "RN": "24",
            "RS": "43",
            "RO": "11",
            "RR": "14",
            "SC": "42",
            "SP": "35",
            "SE": "28",
            "TO": "17",
        }
        return codigos.get(uf, "13")
