"""
MDF-e - Manifesto Eletrônico de Documentos Fiscais.

Portal: https://mdfe-portal.sefaz.rs.gov.br/
Documentação: Manual de Orientação do Contribuinte MDF-e

O MDF-e é o documento que vincula os documentos fiscais transportados
(NF-e, CT-e) em um único manifesto, facilitando a fiscalização.

Obrigatório para:
- Transportadores de carga (CT-e)
- Emitentes de NF-e no transporte de bens/mercadorias

Eventos:
- Encerramento
- Cancelamento
- Inclusão de Condutor
- Inclusão de DFe
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class ModalTransporteMDFe(str, Enum):
    """Modal de transporte."""
    RODOVIARIO = "1"
    AEREO = "2"
    AQUAVIARIO = "3"
    FERROVIARIO = "4"


class TipoEmitente(str, Enum):
    """Tipo de emitente do MDF-e."""
    TRANSPORTADORA = "1"  # Prestador de serviço de transporte
    CARGA_PROPRIA = "2"   # Transportador de carga própria
    CTC = "3"             # Correios


class TipoCarroceria(str, Enum):
    """Tipo de carroceria."""
    NAO_APLICAVEL = "00"
    ABERTA = "01"
    FECHADA_BAU = "02"
    GRANELEIRA = "03"
    PORTA_CONTAINER = "04"
    SIDER = "05"


class TipoRodado(str, Enum):
    """Tipo de rodado do veículo."""
    TRUCK = "01"
    TOCO = "02"
    CAVALO_MECANICO = "03"
    VAN = "04"
    UTILITARIO = "05"
    OUTROS = "06"


class SituacaoMDFe(str, Enum):
    """Situação do MDF-e."""
    EM_DIGITACAO = "em_digitacao"
    ASSINADO = "assinado"
    AUTORIZADO = "autorizado"
    CANCELADO = "cancelado"
    ENCERRADO = "encerrado"
    REJEITADO = "rejeitado"


@dataclass
class Condutor:
    """Condutor do veículo."""
    cpf: str
    nome: str


@dataclass
class Veiculo:
    """Veículo de transporte."""
    placa: str
    renavam: Optional[str] = None
    uf: str = ""
    tara: Decimal = Decimal("0")  # Peso do veículo vazio
    capacidade_kg: Decimal = Decimal("0")
    capacidade_m3: Decimal = Decimal("0")
    tipo_rodado: TipoRodado = TipoRodado.TRUCK
    tipo_carroceria: TipoCarroceria = TipoCarroceria.FECHADA_BAU
    proprietario_cnpj_cpf: Optional[str] = None
    proprietario_nome: Optional[str] = None
    proprietario_ie: Optional[str] = None
    proprietario_uf: Optional[str] = None


@dataclass
class Reboque:
    """Reboque/Semi-reboque."""
    placa: str
    renavam: Optional[str] = None
    uf: str = ""
    tara: Decimal = Decimal("0")
    capacidade_kg: Decimal = Decimal("0")
    capacidade_m3: Decimal = Decimal("0")
    tipo_carroceria: TipoCarroceria = TipoCarroceria.FECHADA_BAU


@dataclass
class DocumentoVinculado:
    """Documento fiscal vinculado ao MDF-e."""
    tipo: str  # "NFe" ou "CTe"
    chave: str
    segundo_codigo_barras: Optional[str] = None  # Para NF-e de carga lotação


@dataclass
class Municipio:
    """Município de carregamento/descarregamento."""
    codigo_ibge: str
    nome: str
    documentos: List[DocumentoVinculado] = field(default_factory=list)


@dataclass
class Percurso:
    """Percurso do MDF-e (UFs de passagem)."""
    uf: str


@dataclass
class MDFe:
    """Manifesto Eletrônico de Documentos Fiscais."""
    # Identificação
    chave: Optional[str] = None
    numero: int = 0
    serie: int = 1
    modelo: str = "58"
    data_emissao: datetime = field(default_factory=datetime.now)

    # Tipo
    modal: ModalTransporteMDFe = ModalTransporteMDFe.RODOVIARIO
    tipo_emitente: TipoEmitente = TipoEmitente.TRANSPORTADORA

    # UF
    uf_inicio: str = ""
    uf_fim: str = ""
    percurso: List[Percurso] = field(default_factory=list)

    # Data/hora
    data_inicio_viagem: Optional[datetime] = None

    # Municípios de carregamento
    municipios_carregamento: List[Municipio] = field(default_factory=list)

    # Municípios de descarregamento
    municipios_descarregamento: List[Municipio] = field(default_factory=list)

    # Totais
    quantidade_cte: int = 0
    quantidade_nfe: int = 0
    valor_total_carga: Decimal = Decimal("0")
    peso_bruto_total: Decimal = Decimal("0")
    unidade_peso: str = "KG"

    # Veículo e condutores
    veiculo_tracao: Optional[Veiculo] = None
    reboques: List[Reboque] = field(default_factory=list)
    condutores: List[Condutor] = field(default_factory=list)

    # CIOT (Código Identificador da Operação de Transporte)
    ciot: Optional[str] = None
    ciot_cnpj_cpf: Optional[str] = None

    # Vale pedágio
    vale_pedagio: List[Dict[str, Any]] = field(default_factory=list)

    # Seguro
    seguradora_cnpj: Optional[str] = None
    seguradora_nome: Optional[str] = None
    numero_apolice: Optional[str] = None
    numero_averbacao: Optional[str] = None

    # Situação
    situacao: SituacaoMDFe = SituacaoMDFe.EM_DIGITACAO
    protocolo_autorizacao: Optional[str] = None
    data_autorizacao: Optional[datetime] = None
    protocolo_encerramento: Optional[str] = None
    data_encerramento: Optional[datetime] = None

    # XML
    xml_assinado: Optional[str] = None
    xml_protocolo: Optional[str] = None


class MDFeManager:
    """
    Gerenciador de MDF-e.

    Emite, consulta e gerencia MDF-e.
    """

    # URLs SEFAZ - SVRS é o autorizador nacional do MDF-e
    URL_PRODUCAO = "https://mdfe.svrs.rs.gov.br/ws/MDFeRecepcaoSinc/MDFeRecepcaoSinc.asmx"
    URL_HOMOLOGACAO = "https://mdfe-homologacao.svrs.rs.gov.br/ws/MDFeRecepcaoSinc/MDFeRecepcaoSinc.asmx"

    # Namespace
    NS_MDFE = "http://www.portalfiscal.inf.br/mdfe"

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

    def criar_mdfe(
        self,
        numero: int,
        serie: int = 1,
        modal: ModalTransporteMDFe = ModalTransporteMDFe.RODOVIARIO
    ) -> MDFe:
        """
        Cria um novo MDF-e.

        Args:
            numero: Número do MDF-e
            serie: Série
            modal: Modal de transporte

        Returns:
            MDF-e criado
        """
        mdfe = MDFe(
            numero=numero,
            serie=serie,
            modal=modal,
            uf_inicio=self.uf,
        )

        logger.info(f"Criado MDF-e nº {numero}")
        return mdfe

    def gerar_xml(self, mdfe: MDFe) -> str:
        """
        Gera XML do MDF-e.

        Args:
            mdfe: MDF-e a ser gerado

        Returns:
            XML gerado
        """
        # Cria elemento raiz
        mdfe_xml = ET.Element("MDFe", xmlns=self.NS_MDFE)

        # infMDFe
        inf_mdfe = ET.SubElement(mdfe_xml, "infMDFe", versao="3.00")

        # Identificação
        ide = ET.SubElement(inf_mdfe, "ide")
        ET.SubElement(ide, "cUF").text = self._codigo_uf(self.uf)
        ET.SubElement(ide, "tpAmb").text = self.tipo_ambiente
        ET.SubElement(ide, "tpEmit").text = mdfe.tipo_emitente.value
        ET.SubElement(ide, "tpTransp").text = "1"  # ETC
        ET.SubElement(ide, "mod").text = mdfe.modelo
        ET.SubElement(ide, "serie").text = str(mdfe.serie)
        ET.SubElement(ide, "nMDF").text = str(mdfe.numero)
        ET.SubElement(ide, "cMDF").text = str(mdfe.numero).zfill(8)
        ET.SubElement(ide, "cDV").text = "0"  # Dígito verificador
        ET.SubElement(ide, "modal").text = mdfe.modal.value
        ET.SubElement(ide, "dhEmi").text = mdfe.data_emissao.strftime("%Y-%m-%dT%H:%M:%S-04:00")
        ET.SubElement(ide, "tpEmis").text = "1"  # Normal
        ET.SubElement(ide, "procEmi").text = "0"  # Aplicativo do contribuinte
        ET.SubElement(ide, "verProc").text = "ConectaPRO 1.0"
        ET.SubElement(ide, "UFIni").text = mdfe.uf_inicio
        ET.SubElement(ide, "UFFim").text = mdfe.uf_fim or self.uf

        # Percurso (UFs intermediárias)
        for perc in mdfe.percurso:
            inf_perc = ET.SubElement(ide, "infPercurso")
            ET.SubElement(inf_perc, "UFPer").text = perc.uf

        # Data/hora viagem
        if mdfe.data_inicio_viagem:
            ET.SubElement(ide, "dhIniViagem").text = mdfe.data_inicio_viagem.strftime("%Y-%m-%dT%H:%M:%S-04:00")

        # Emitente
        emit = ET.SubElement(inf_mdfe, "emit")
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
        ET.SubElement(emit_ender, "email").text = "contato@empresa.com.br"

        # Info Modal Rodoviário
        if mdfe.modal == ModalTransporteMDFe.RODOVIARIO:
            inf_modal = ET.SubElement(inf_mdfe, "infModal", versaoModal="3.00")
            rodo = ET.SubElement(inf_modal, "rodo")

            # RNTRC
            inf_antt = ET.SubElement(rodo, "infANTT")
            ET.SubElement(inf_antt, "RNTRC").text = "00000000"

            # CIOT
            if mdfe.ciot:
                inf_ciot = ET.SubElement(inf_antt, "infCIOT")
                ET.SubElement(inf_ciot, "CIOT").text = mdfe.ciot
                if mdfe.ciot_cnpj_cpf:
                    if len(mdfe.ciot_cnpj_cpf) == 14:
                        ET.SubElement(inf_ciot, "CNPJ").text = mdfe.ciot_cnpj_cpf
                    else:
                        ET.SubElement(inf_ciot, "CPF").text = mdfe.ciot_cnpj_cpf

            # Veículo de tração
            if mdfe.veiculo_tracao:
                vei_trac = ET.SubElement(rodo, "veicTracao")
                ET.SubElement(vei_trac, "placa").text = mdfe.veiculo_tracao.placa
                if mdfe.veiculo_tracao.renavam:
                    ET.SubElement(vei_trac, "RENAVAM").text = mdfe.veiculo_tracao.renavam
                ET.SubElement(vei_trac, "tara").text = str(int(mdfe.veiculo_tracao.tara))
                ET.SubElement(vei_trac, "capKG").text = str(int(mdfe.veiculo_tracao.capacidade_kg))
                ET.SubElement(vei_trac, "capM3").text = str(int(mdfe.veiculo_tracao.capacidade_m3))
                ET.SubElement(vei_trac, "tpRod").text = mdfe.veiculo_tracao.tipo_rodado.value
                ET.SubElement(vei_trac, "tpCar").text = mdfe.veiculo_tracao.tipo_carroceria.value
                ET.SubElement(vei_trac, "UF").text = mdfe.veiculo_tracao.uf or self.uf

                # Proprietário do veículo (se diferente do emitente)
                if mdfe.veiculo_tracao.proprietario_cnpj_cpf:
                    prop = ET.SubElement(vei_trac, "prop")
                    if len(mdfe.veiculo_tracao.proprietario_cnpj_cpf) == 14:
                        ET.SubElement(prop, "CNPJ").text = mdfe.veiculo_tracao.proprietario_cnpj_cpf
                    else:
                        ET.SubElement(prop, "CPF").text = mdfe.veiculo_tracao.proprietario_cnpj_cpf
                    ET.SubElement(prop, "RNTRC").text = "00000000"
                    ET.SubElement(prop, "xNome").text = mdfe.veiculo_tracao.proprietario_nome or ""
                    if mdfe.veiculo_tracao.proprietario_ie:
                        ET.SubElement(prop, "IE").text = mdfe.veiculo_tracao.proprietario_ie
                    ET.SubElement(prop, "UF").text = mdfe.veiculo_tracao.proprietario_uf or self.uf
                    ET.SubElement(prop, "tpProp").text = "0"  # TAC Agregado

                # Condutores
                for condutor in mdfe.condutores:
                    cond = ET.SubElement(vei_trac, "condutor")
                    ET.SubElement(cond, "xNome").text = condutor.nome
                    ET.SubElement(cond, "CPF").text = condutor.cpf

            # Reboques
            for reboque in mdfe.reboques:
                vei_reb = ET.SubElement(rodo, "veicReboque")
                ET.SubElement(vei_reb, "placa").text = reboque.placa
                if reboque.renavam:
                    ET.SubElement(vei_reb, "RENAVAM").text = reboque.renavam
                ET.SubElement(vei_reb, "tara").text = str(int(reboque.tara))
                ET.SubElement(vei_reb, "capKG").text = str(int(reboque.capacidade_kg))
                ET.SubElement(vei_reb, "capM3").text = str(int(reboque.capacidade_m3))
                ET.SubElement(vei_reb, "tpCar").text = reboque.tipo_carroceria.value
                ET.SubElement(vei_reb, "UF").text = reboque.uf or self.uf

        # Info Documentos
        inf_doc = ET.SubElement(inf_mdfe, "infDoc")

        # Municípios de descarregamento com documentos
        for mun in mdfe.municipios_descarregamento:
            inf_mun_descarga = ET.SubElement(inf_doc, "infMunDescarga")
            ET.SubElement(inf_mun_descarga, "cMunDescarga").text = mun.codigo_ibge
            ET.SubElement(inf_mun_descarga, "xMunDescarga").text = mun.nome

            for doc in mun.documentos:
                if doc.tipo == "CTe":
                    inf_cte = ET.SubElement(inf_mun_descarga, "infCTe")
                    ET.SubElement(inf_cte, "chCTe").text = doc.chave
                elif doc.tipo == "NFe":
                    inf_nfe = ET.SubElement(inf_mun_descarga, "infNFe")
                    ET.SubElement(inf_nfe, "chNFe").text = doc.chave
                    if doc.segundo_codigo_barras:
                        ET.SubElement(inf_nfe, "SegCodBarra").text = doc.segundo_codigo_barras

        # Seguro
        if mdfe.seguradora_cnpj or mdfe.numero_apolice:
            seg = ET.SubElement(inf_mdfe, "seg")
            inf_resp = ET.SubElement(seg, "infResp")
            ET.SubElement(inf_resp, "respSeg").text = "1"  # Emitente
            ET.SubElement(inf_resp, "CNPJ").text = self.cnpj

            if mdfe.seguradora_cnpj:
                inf_seg = ET.SubElement(seg, "infSeg")
                ET.SubElement(inf_seg, "xSeg").text = mdfe.seguradora_nome or "SEGURADORA"
                ET.SubElement(inf_seg, "CNPJ").text = mdfe.seguradora_cnpj

            if mdfe.numero_apolice:
                ET.SubElement(seg, "nApol").text = mdfe.numero_apolice
            if mdfe.numero_averbacao:
                ET.SubElement(seg, "nAver").text = mdfe.numero_averbacao

        # Produção Rural (ProdPred) - obrigatório
        prod_pred = ET.SubElement(inf_mdfe, "prodPred")
        ET.SubElement(prod_pred, "tpCarga").text = "05"  # Carga geral
        ET.SubElement(prod_pred, "xProd").text = "MERCADORIAS DIVERSAS"

        # Totais
        tot = ET.SubElement(inf_mdfe, "tot")
        ET.SubElement(tot, "qCTe").text = str(mdfe.quantidade_cte)
        ET.SubElement(tot, "qNFe").text = str(mdfe.quantidade_nfe)
        ET.SubElement(tot, "vCarga").text = f"{mdfe.valor_total_carga:.2f}"
        ET.SubElement(tot, "cUnid").text = "01"  # KG
        ET.SubElement(tot, "qCarga").text = f"{mdfe.peso_bruto_total:.4f}"

        # Informações adicionais
        inf_adic = ET.SubElement(inf_mdfe, "infAdic")
        ET.SubElement(inf_adic, "infCpl").text = "MDF-e emitido pelo sistema ConectaPRO"

        # Responsável técnico
        inf_resp_tec = ET.SubElement(inf_mdfe, "infRespTec")
        ET.SubElement(inf_resp_tec, "CNPJ").text = self.cnpj
        ET.SubElement(inf_resp_tec, "xContato").text = "SUPORTE TECNICO"
        ET.SubElement(inf_resp_tec, "email").text = "suporte@empresa.com.br"
        ET.SubElement(inf_resp_tec, "fone").text = "9200000000"

        # Converte para string
        xml_str = ET.tostring(mdfe_xml, encoding="unicode")
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>' + xml_str

        logger.info(f"Gerado XML MDF-e nº {mdfe.numero}")
        return xml_str

    def encerrar(self, mdfe: MDFe, data_encerramento: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Gera evento de encerramento do MDF-e.

        Args:
            mdfe: MDF-e a ser encerrado
            data_encerramento: Data/hora do encerramento

        Returns:
            Resultado do encerramento
        """
        if not mdfe.chave:
            raise ValueError("MDF-e não possui chave de acesso")

        data_enc = data_encerramento or datetime.now()

        # XML do evento de encerramento
        evento = {
            "tipo_evento": "110112",
            "descricao": "Encerramento",
            "chave_mdfe": mdfe.chave,
            "data_evento": data_enc.isoformat(),
            "protocolo": mdfe.protocolo_autorizacao,
            "uf_encerramento": self.uf,
            "codigo_municipio": "1302603",  # Manaus
        }

        logger.info(f"Gerado evento de encerramento MDF-e {mdfe.numero}")

        return {
            "evento": evento,
            "status": "pendente",
            "mensagem": "Implementar envio do evento via WebService"
        }

    def incluir_condutor(self, mdfe: MDFe, condutor: Condutor) -> Dict[str, Any]:
        """
        Gera evento de inclusão de condutor.

        Args:
            mdfe: MDF-e
            condutor: Condutor a incluir

        Returns:
            Resultado da inclusão
        """
        if not mdfe.chave:
            raise ValueError("MDF-e não possui chave de acesso")

        evento = {
            "tipo_evento": "110114",
            "descricao": "Inclusão de Condutor",
            "chave_mdfe": mdfe.chave,
            "condutor_cpf": condutor.cpf,
            "condutor_nome": condutor.nome,
        }

        logger.info(f"Gerado evento de inclusão de condutor MDF-e {mdfe.numero}")

        return {
            "evento": evento,
            "status": "pendente",
            "mensagem": "Implementar envio do evento via WebService"
        }

    def consultar_status_servico(self) -> Dict[str, Any]:
        """
        Consulta status do serviço MDF-e na SEFAZ.

        Returns:
            Status do serviço
        """
        url = self.URL_PRODUCAO if self.ambiente == "producao" else self.URL_HOMOLOGACAO

        return {
            "servico": "MDFeStatusServico",
            "url": url,
            "status": "pendente",
            "mensagem": "Implementar consulta via WebService"
        }

    def consultar_nao_encerrados(self) -> List[Dict[str, Any]]:
        """
        Consulta MDF-e não encerrados do emitente.

        Returns:
            Lista de MDF-e não encerrados
        """
        return []

    def _codigo_uf(self, uf: str) -> str:
        """Retorna código IBGE da UF."""
        codigos = {
            "AC": "12", "AL": "27", "AP": "16", "AM": "13", "BA": "29",
            "CE": "23", "DF": "53", "ES": "32", "GO": "52", "MA": "21",
            "MT": "51", "MS": "50", "MG": "31", "PA": "15", "PB": "25",
            "PR": "41", "PE": "26", "PI": "22", "RJ": "33", "RN": "24",
            "RS": "43", "RO": "11", "RR": "14", "SC": "42", "SP": "35",
            "SE": "28", "TO": "17"
        }
        return codigos.get(uf, "13")
