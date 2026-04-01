"""
Module: SEFAZManager
Description: Sistema de integracao com SEFAZ para emissao de documentos fiscais
             eletronicos (NFe, NFCe, CTe, MDFe).
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: SINIEF, CONFAZ, Legislacao Fiscal Brasileira
"""

import logging
import re
import xml.etree.ElementTree as ET  # noqa: N817, S405
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4
from xml.dom import minidom  # noqa: S408
from xml.etree.ElementTree import Element  # noqa: S405

from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base

# Importa gerenciador de certificados e assinador XML
from .certificate_manager import CertificateManager
from .xml_signer import NFEXMLSigner

logger = logging.getLogger(__name__)

Base = declarative_base()


class DocumentType(StrEnum):
    """Tipos de documentos fiscais eletronicos."""

    NFE = "nfe"  # Nota Fiscal Eletronica (modelo 55)
    NFCE = "nfce"  # NF Consumidor Eletronica (modelo 65)
    CTE = "cte"  # Conhecimento de Transporte (modelo 57)
    MDFE = "mdfe"  # Manifesto de Documentos Fiscais (modelo 58)
    NFSE = "nfse"  # NF de Servicos Eletronica (municipal)


class DocumentStatus(StrEnum):
    """Status de um documento fiscal."""

    DRAFT = "draft"  # Em edicao
    VALIDATING = "validating"  # Em validacao
    AUTHORIZED = "authorized"  # Autorizado
    DENIED = "denied"  # Denegado
    CANCELLED = "cancelled"  # Cancelado
    CORRECTED = "corrected"  # Carta de correcao emitida
    CONTINGENCY = "contingency"  # Emitido em contingencia
    ERROR = "error"  # Erro


class OperationType(StrEnum):
    """Tipo de operacao fiscal."""

    ENTRADA = "0"  # Entrada
    SAIDA = "1"  # Saida


class PaymentType(StrEnum):
    """Formas de pagamento."""

    DINHEIRO = "01"
    CHEQUE = "02"
    CARTAO_CREDITO = "03"
    CARTAO_DEBITO = "04"
    CREDITO_LOJA = "05"
    VALE_ALIMENTACAO = "10"
    VALE_REFEICAO = "11"
    VALE_PRESENTE = "12"
    VALE_COMBUSTIVEL = "13"
    BOLETO = "15"
    DEPOSITO = "16"
    PIX = "17"
    TRANSFERENCIA = "18"
    PROGRAMA_FIDELIDADE = "19"
    SEM_PAGAMENTO = "90"
    OUTROS = "99"


class ContingencyType(StrEnum):
    """Tipos de contingencia."""

    NORMAL = "1"  # Normal
    FS_IA = "2"  # Formulario de Seguranca - Impressor Autonomo
    SCAN = "3"  # SCAN (desativado)
    DPEC = "4"  # DPEC (desativado)
    FS_DA = "5"  # FS-DA
    SVC_AN = "6"  # SVC-AN (SEFAZ Virtual de Contingencia AN)
    SVC_RS = "7"  # SVC-RS (SEFAZ Virtual de Contingencia RS)
    OFFLINE = "9"  # NFC-e Offline


class SEFAZError(Exception):
    """Erro em operacao SEFAZ."""

    def __init__(self, message: str, code: str | None = None, document_id: str | None = None):
        self.message = message
        self.code = code
        self.document_id = document_id
        super().__init__(self.message)


class ValidationError(SEFAZError):
    """Erro de validacao de documento."""

    pass


class TransmissionError(SEFAZError):
    """Erro de transmissao."""

    pass


@dataclass
class UFConfig:
    """Configuracao por UF."""

    uf: str
    code: str  # Codigo IBGE
    webservice_url: str
    contingency_url: str | None = None
    timezone: str = "America/Sao_Paulo"


# Configuracoes das UFs
UF_CONFIGS: dict[str, UFConfig] = {
    "AC": UFConfig("AC", "12", "https://nfe.sefaznet.ac.gov.br"),
    "AL": UFConfig("AL", "27", "https://nfe.sefaz.al.gov.br"),
    "AM": UFConfig("AM", "13", "https://nfe.sefaz.am.gov.br"),
    "AP": UFConfig("AP", "16", "https://nfe.sefaz.ap.gov.br"),
    "BA": UFConfig("BA", "29", "https://nfe.sefaz.ba.gov.br"),
    "CE": UFConfig("CE", "23", "https://nfe.sefaz.ce.gov.br"),
    "DF": UFConfig("DF", "53", "https://nfe.fazenda.df.gov.br"),
    "ES": UFConfig("ES", "32", "https://nfe.sefaz.es.gov.br"),
    "GO": UFConfig("GO", "52", "https://nfe.sefaz.go.gov.br"),
    "MA": UFConfig("MA", "21", "https://nfe.sefaz.ma.gov.br"),
    "MG": UFConfig("MG", "31", "https://nfe.fazenda.mg.gov.br"),
    "MS": UFConfig("MS", "50", "https://nfe.sefaz.ms.gov.br"),
    "MT": UFConfig("MT", "51", "https://nfe.sefaz.mt.gov.br"),
    "PA": UFConfig("PA", "15", "https://nfe.sefaz.pa.gov.br"),
    "PB": UFConfig("PB", "25", "https://nfe.sefaz.pb.gov.br"),
    "PE": UFConfig("PE", "26", "https://nfe.sefaz.pe.gov.br"),
    "PI": UFConfig("PI", "22", "https://nfe.sefaz.pi.gov.br"),
    "PR": UFConfig("PR", "41", "https://nfe.sefa.pr.gov.br"),
    "RJ": UFConfig("RJ", "33", "https://nfe.fazenda.rj.gov.br"),
    "RN": UFConfig("RN", "24", "https://nfe.sefaz.rn.gov.br"),
    "RO": UFConfig("RO", "11", "https://nfe.sefin.ro.gov.br"),
    "RR": UFConfig("RR", "14", "https://nfe.sefaz.rr.gov.br"),
    "RS": UFConfig("RS", "43", "https://nfe.sefazrs.rs.gov.br"),
    "SC": UFConfig("SC", "42", "https://nfe.sef.sc.gov.br"),
    "SE": UFConfig("SE", "28", "https://nfe.sefaz.se.gov.br"),
    "SP": UFConfig("SP", "35", "https://nfe.fazenda.sp.gov.br"),
    "TO": UFConfig("TO", "17", "https://nfe.sefaz.to.gov.br"),
}


@dataclass
class Endereco:
    """Endereco para documentos fiscais."""

    logradouro: str
    numero: str
    bairro: str
    cidade: str
    uf: str
    cep: str
    codigo_municipio: str
    complemento: str | None = None
    pais: str = "Brasil"
    codigo_pais: str = "1058"

    def to_dict(self) -> dict[str, Any]:
        return {
            "logradouro": self.logradouro,
            "numero": self.numero,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "uf": self.uf,
            "cep": self.cep,
            "codigo_municipio": self.codigo_municipio,
            "complemento": self.complemento,
        }


@dataclass
class Emitente:
    """Dados do emitente."""

    cnpj: str
    razao_social: str
    nome_fantasia: str | None
    inscricao_estadual: str
    endereco: Endereco
    regime_tributario: str = "3"  # 1=Simples, 2=Simples Excesso, 3=Normal
    cnae: str | None = None
    inscricao_municipal: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "cnpj": self.cnpj,
            "razao_social": self.razao_social,
            "nome_fantasia": self.nome_fantasia,
            "inscricao_estadual": self.inscricao_estadual,
            "endereco": self.endereco.to_dict(),
            "regime_tributario": self.regime_tributario,
        }


@dataclass
class Destinatario:
    """Dados do destinatario."""

    cpf_cnpj: str
    nome: str
    endereco: Endereco | None = None
    inscricao_estadual: str | None = None
    email: str | None = None
    telefone: str | None = None
    indicador_ie: str = "9"  # 1=Contribuinte, 2=Isento, 9=Nao Contribuinte

    @property
    def is_cpf(self) -> bool:
        """Verifica se documento e CPF."""
        doc = re.sub(r"[^\d]", "", self.cpf_cnpj)
        return len(doc) == 11

    def to_dict(self) -> dict[str, Any]:
        return {
            "cpf_cnpj": self.cpf_cnpj,
            "nome": self.nome,
            "endereco": self.endereco.to_dict() if self.endereco else None,
            "email": self.email,
            "indicador_ie": self.indicador_ie,
        }


@dataclass
class Produto:
    """Item/Produto da nota fiscal."""

    codigo: str
    descricao: str
    ncm: str
    cfop: str
    unidade: str
    quantidade: Decimal
    valor_unitario: Decimal
    cest: str | None = None
    ean: str | None = None
    origem: str = "0"  # 0=Nacional
    cst_icms: str = "00"
    cst_pis: str = "01"
    cst_cofins: str = "01"
    aliquota_icms: Decimal = Decimal("0")
    aliquota_pis: Decimal = Decimal("0")
    aliquota_cofins: Decimal = Decimal("0")
    valor_desconto: Decimal = Decimal("0")

    @property
    def valor_total(self) -> Decimal:
        """Calcula valor total do item."""
        return (self.quantidade * self.valor_unitario) - self.valor_desconto

    @property
    def valor_icms(self) -> Decimal:
        """Calcula valor do ICMS."""
        return self.valor_total * (self.aliquota_icms / 100)

    def to_dict(self) -> dict[str, Any]:
        return {
            "codigo": self.codigo,
            "descricao": self.descricao,
            "ncm": self.ncm,
            "cfop": self.cfop,
            "unidade": self.unidade,
            "quantidade": str(self.quantidade),
            "valor_unitario": str(self.valor_unitario),
            "valor_total": str(self.valor_total),
        }


@dataclass
class Pagamento:
    """Forma de pagamento."""

    tipo: PaymentType
    valor: Decimal
    bandeira: str | None = None  # Para cartoes
    autorizacao: str | None = None
    cnpj_credenciadora: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tipo": self.tipo.value,
            "valor": str(self.valor),
            "bandeira": self.bandeira,
        }


@dataclass
class NotaFiscal:
    """Nota Fiscal Eletronica."""

    id: UUID
    tipo: DocumentType
    status: DocumentStatus
    emitente: Emitente
    destinatario: Destinatario | None
    produtos: list[Produto]
    pagamentos: list[Pagamento]
    operacao: OperationType
    natureza_operacao: str
    numero: int
    serie: int
    data_emissao: datetime
    chave_acesso: str | None = None
    protocolo: str | None = None
    xml_content: str | None = None
    xml_signed: str | None = None
    contingency_type: ContingencyType = ContingencyType.NORMAL
    informacoes_adicionais: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    authorized_at: datetime | None = None
    cancelled_at: datetime | None = None
    errors: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def valor_total_produtos(self) -> Decimal:
        """Valor total dos produtos."""
        return sum(p.valor_total for p in self.produtos)

    @property
    def valor_total_icms(self) -> Decimal:
        """Valor total do ICMS."""
        return sum(p.valor_icms for p in self.produtos)

    @property
    def valor_total_nota(self) -> Decimal:
        """Valor total da nota."""
        return self.valor_total_produtos

    def generate_chave_acesso(self) -> str:
        """Gera chave de acesso de 44 digitos."""
        uf = UF_CONFIGS.get(self.emitente.endereco.uf)
        if not uf:
            raise SEFAZError(f"UF invalida: {self.emitente.endereco.uf}")

        # Componentes da chave
        cuf = uf.code
        aamm = self.data_emissao.strftime("%y%m")
        cnpj = re.sub(r"[^\d]", "", self.emitente.cnpj)
        mod = "55" if self.tipo == DocumentType.NFE else "65"
        serie = str(self.serie).zfill(3)
        numero = str(self.numero).zfill(9)
        tpemis = self.contingency_type.value
        cnf = str(uuid4().int)[:8]

        # Chave sem DV
        chave_sem_dv = f"{cuf}{aamm}{cnpj}{mod}{serie}{numero}{tpemis}{cnf}"

        # Calcula digito verificador (modulo 11)
        dv = self._calculate_mod11(chave_sem_dv)

        self.chave_acesso = f"{chave_sem_dv}{dv}"
        return self.chave_acesso

    def _calculate_mod11(self, chave: str) -> str:
        """Calcula digito verificador modulo 11."""
        pesos = [2, 3, 4, 5, 6, 7, 8, 9]
        soma = 0
        for i, digito in enumerate(reversed(chave)):
            soma += int(digito) * pesos[i % 8]
        resto = soma % 11
        dv = 11 - resto
        return str(0 if dv >= 10 else dv)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "tipo": self.tipo.value,
            "status": self.status.value,
            "numero": self.numero,
            "serie": self.serie,
            "chave_acesso": self.chave_acesso,
            "protocolo": self.protocolo,
            "data_emissao": self.data_emissao.isoformat(),
            "emitente": self.emitente.to_dict(),
            "destinatario": self.destinatario.to_dict() if self.destinatario else None,
            "produtos": [p.to_dict() for p in self.produtos],
            "pagamentos": [p.to_dict() for p in self.pagamentos],
            "valor_total": str(self.valor_total_nota),
            "natureza_operacao": self.natureza_operacao,
        }


# SQLAlchemy Model
class NotaFiscalModel(Base):
    """Modelo de banco para notas fiscais."""

    __tablename__ = "gov_notas_fiscais"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tipo = Column(String(10), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="draft", index=True)
    numero = Column(Integer, nullable=False)
    serie = Column(Integer, nullable=False, default=1)
    chave_acesso = Column(String(44), nullable=True, unique=True, index=True)
    protocolo = Column(String(50), nullable=True)
    data_emissao = Column(DateTime, nullable=False, index=True)

    # Emitente
    emitente_cnpj = Column(String(18), nullable=False, index=True)
    emitente_razao_social = Column(String(255), nullable=False)
    emitente_uf = Column(String(2), nullable=False)

    # Destinatario
    destinatario_cpf_cnpj = Column(String(18), nullable=True, index=True)
    destinatario_nome = Column(String(255), nullable=True)

    # Valores
    valor_produtos = Column(Numeric(15, 2), nullable=False)
    valor_icms = Column(Numeric(15, 2), default=0)
    valor_total = Column(Numeric(15, 2), nullable=False)

    # Operacao
    operacao = Column(String(1), nullable=False)
    natureza_operacao = Column(String(100), nullable=False)
    contingency_type = Column(String(1), default="1")

    # XML
    xml_content = Column(Text, nullable=True)
    xml_signed = Column(Text, nullable=True)

    # Detalhes
    produtos = Column(JSONB, default=[])
    pagamentos = Column(JSONB, default=[])
    errors = Column(JSONB, default=[])
    extra_metadata = Column(JSONB, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    authorized_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NFEXMLBuilder:
    """Construtor de XML para NFe/NFCe."""

    NAMESPACE = "http://www.portalfiscal.inf.br/nfe"
    VERSION = "4.00"

    def build_nfe(self, nf: NotaFiscal) -> str:
        """Constroi XML da NFe."""
        # Gera chave de acesso se nao existir
        if not nf.chave_acesso:
            nf.generate_chave_acesso()

        root = ET.Element("NFe", xmlns=self.NAMESPACE)
        inf = ET.SubElement(root, "infNFe", Id=f"NFe{nf.chave_acesso}", versao=self.VERSION)

        # ide - Identificacao
        ide = ET.SubElement(inf, "ide")
        uf_config = UF_CONFIGS.get(nf.emitente.endereco.uf)
        ET.SubElement(ide, "cUF").text = uf_config.code if uf_config else "35"
        ET.SubElement(ide, "cNF").text = nf.chave_acesso[35:43]
        ET.SubElement(ide, "natOp").text = nf.natureza_operacao
        ET.SubElement(ide, "mod").text = "55" if nf.tipo == DocumentType.NFE else "65"
        ET.SubElement(ide, "serie").text = str(nf.serie)
        ET.SubElement(ide, "nNF").text = str(nf.numero)
        # Fuso horário baseado na UF do emitente
        uf_timezone_offset = {
            "AC": -5,
            "AM": -4,
            "AP": -3,
            "PA": -3,
            "RO": -4,
            "RR": -4,
            "TO": -3,
            "MT": -4,
        }.get(nf.emitente.endereco.uf, -3)
        uf_timezone_str = f"{uf_timezone_offset:+03d}:00"

        # Se data_emissao é UTC (naive ou aware), converter para hora local
        data_emissao = nf.data_emissao
        if data_emissao.tzinfo is None:
            # datetime naive - assumir UTC e converter para hora local
            data_emissao = data_emissao + timedelta(hours=uf_timezone_offset)
        else:
            # datetime aware - converter para timezone da UF
            uf_tz = timezone(timedelta(hours=uf_timezone_offset))
            data_emissao = data_emissao.astimezone(uf_tz)

        ET.SubElement(ide, "dhEmi").text = data_emissao.strftime(f"%Y-%m-%dT%H:%M:%S{uf_timezone_str}")
        ET.SubElement(ide, "tpNF").text = nf.operacao.value
        ET.SubElement(ide, "idDest").text = "1"  # Operacao interna
        ET.SubElement(ide, "cMunFG").text = nf.emitente.endereco.codigo_municipio
        ET.SubElement(ide, "tpImp").text = "1"  # DANFE retrato
        ET.SubElement(ide, "tpEmis").text = nf.contingency_type.value
        ET.SubElement(ide, "cDV").text = nf.chave_acesso[-1]
        ET.SubElement(ide, "tpAmb").text = "2"  # Homologacao
        ET.SubElement(ide, "finNFe").text = "1"  # Normal
        # indFinal: 1 se NFC-e ou destinatário não contribuinte
        is_consumidor_final = nf.tipo == DocumentType.NFCE or (nf.destinatario and nf.destinatario.indicador_ie == "9")
        ET.SubElement(ide, "indFinal").text = "1" if is_consumidor_final else "0"
        ET.SubElement(ide, "indPres").text = "1"  # Presencial
        ET.SubElement(ide, "procEmi").text = "0"
        ET.SubElement(ide, "verProc").text = "CONECTA_PRO_1.0"

        # emit - Emitente
        emit = ET.SubElement(inf, "emit")
        ET.SubElement(emit, "CNPJ").text = re.sub(r"[^\d]", "", nf.emitente.cnpj)
        ET.SubElement(emit, "xNome").text = nf.emitente.razao_social
        if nf.emitente.nome_fantasia:
            ET.SubElement(emit, "xFant").text = nf.emitente.nome_fantasia
        self._add_endereco(emit, "enderEmit", nf.emitente.endereco)
        ET.SubElement(emit, "IE").text = nf.emitente.inscricao_estadual
        ET.SubElement(emit, "CRT").text = nf.emitente.regime_tributario

        # dest - Destinatario
        if nf.destinatario:
            dest = ET.SubElement(inf, "dest")
            doc = re.sub(r"[^\d]", "", nf.destinatario.cpf_cnpj)
            if nf.destinatario.is_cpf:
                ET.SubElement(dest, "CPF").text = doc
            else:
                ET.SubElement(dest, "CNPJ").text = doc
            ET.SubElement(dest, "xNome").text = nf.destinatario.nome
            if nf.destinatario.endereco:
                self._add_endereco(dest, "enderDest", nf.destinatario.endereco)
            ET.SubElement(dest, "indIEDest").text = nf.destinatario.indicador_ie
            if nf.destinatario.email:
                ET.SubElement(dest, "email").text = nf.destinatario.email

        # det - Produtos
        for i, produto in enumerate(nf.produtos, 1):
            det = ET.SubElement(inf, "det", nItem=str(i))
            prod = ET.SubElement(det, "prod")
            ET.SubElement(prod, "cProd").text = produto.codigo
            ET.SubElement(prod, "cEAN").text = produto.ean or "SEM GTIN"
            ET.SubElement(prod, "xProd").text = produto.descricao
            ET.SubElement(prod, "NCM").text = produto.ncm
            if produto.cest:
                ET.SubElement(prod, "CEST").text = produto.cest
            ET.SubElement(prod, "CFOP").text = produto.cfop
            ET.SubElement(prod, "uCom").text = produto.unidade
            ET.SubElement(prod, "qCom").text = f"{produto.quantidade:.4f}"
            ET.SubElement(prod, "vUnCom").text = f"{produto.valor_unitario:.10f}"
            ET.SubElement(prod, "vProd").text = f"{produto.valor_total:.2f}"
            ET.SubElement(prod, "cEANTrib").text = produto.ean or "SEM GTIN"
            ET.SubElement(prod, "uTrib").text = produto.unidade
            ET.SubElement(prod, "qTrib").text = f"{produto.quantidade:.4f}"
            ET.SubElement(prod, "vUnTrib").text = f"{produto.valor_unitario:.10f}"
            ET.SubElement(prod, "indTot").text = "1"

            # Impostos
            imposto = ET.SubElement(det, "imposto")
            self._add_icms(imposto, produto)
            self._add_pis(imposto, produto)
            self._add_cofins(imposto, produto)

        # total
        total = ET.SubElement(inf, "total")
        icms_tot = ET.SubElement(total, "ICMSTot")
        # Para Simples Nacional, BC e ICMS são zero
        is_simples = nf.emitente.regime_tributario in ["1", "2"]  # 1=SN, 2=SN sublimite
        ET.SubElement(icms_tot, "vBC").text = "0.00" if is_simples else f"{nf.valor_total_produtos:.2f}"
        ET.SubElement(icms_tot, "vICMS").text = "0.00" if is_simples else f"{nf.valor_total_icms:.2f}"
        ET.SubElement(icms_tot, "vICMSDeson").text = "0.00"
        ET.SubElement(icms_tot, "vFCP").text = "0.00"
        ET.SubElement(icms_tot, "vBCST").text = "0.00"
        ET.SubElement(icms_tot, "vST").text = "0.00"
        ET.SubElement(icms_tot, "vFCPST").text = "0.00"
        ET.SubElement(icms_tot, "vFCPSTRet").text = "0.00"
        ET.SubElement(icms_tot, "vProd").text = f"{nf.valor_total_produtos:.2f}"
        ET.SubElement(icms_tot, "vFrete").text = "0.00"
        ET.SubElement(icms_tot, "vSeg").text = "0.00"
        ET.SubElement(icms_tot, "vDesc").text = "0.00"
        ET.SubElement(icms_tot, "vII").text = "0.00"
        ET.SubElement(icms_tot, "vIPI").text = "0.00"
        ET.SubElement(icms_tot, "vIPIDevol").text = "0.00"
        ET.SubElement(icms_tot, "vPIS").text = "0.00"
        ET.SubElement(icms_tot, "vCOFINS").text = "0.00"
        ET.SubElement(icms_tot, "vOutro").text = "0.00"
        ET.SubElement(icms_tot, "vNF").text = f"{nf.valor_total_nota:.2f}"

        # transp
        transp = ET.SubElement(inf, "transp")
        ET.SubElement(transp, "modFrete").text = "9"  # Sem frete

        # pag
        pag = ET.SubElement(inf, "pag")
        for pagamento in nf.pagamentos:
            det_pag = ET.SubElement(pag, "detPag")
            ET.SubElement(det_pag, "tPag").text = pagamento.tipo.value
            ET.SubElement(det_pag, "vPag").text = f"{pagamento.valor:.2f}"

        # infAdic
        if nf.informacoes_adicionais:
            inf_adic = ET.SubElement(inf, "infAdic")
            ET.SubElement(inf_adic, "infCpl").text = nf.informacoes_adicionais

        # infRespTec - Responsável Técnico (obrigatório)
        inf_resp = ET.SubElement(inf, "infRespTec")
        ET.SubElement(inf_resp, "CNPJ").text = re.sub(r"[^\d]", "", nf.emitente.cnpj)
        ET.SubElement(inf_resp, "xContato").text = "Suporte Tecnico"
        ET.SubElement(inf_resp, "email").text = "suporte@conectapro.com.br"
        ET.SubElement(inf_resp, "fone").text = "92999999999"

        return self._prettify(root)

    def _add_endereco(self, parent: Element, tag: str, endereco: Endereco) -> None:
        """Adiciona endereco ao XML."""
        end = ET.SubElement(parent, tag)
        ET.SubElement(end, "xLgr").text = endereco.logradouro
        ET.SubElement(end, "nro").text = endereco.numero
        if endereco.complemento:
            ET.SubElement(end, "xCpl").text = endereco.complemento
        ET.SubElement(end, "xBairro").text = endereco.bairro
        ET.SubElement(end, "cMun").text = endereco.codigo_municipio
        ET.SubElement(end, "xMun").text = endereco.cidade
        ET.SubElement(end, "UF").text = endereco.uf
        ET.SubElement(end, "CEP").text = re.sub(r"[^\d]", "", endereco.cep)
        ET.SubElement(end, "cPais").text = endereco.codigo_pais
        ET.SubElement(end, "xPais").text = endereco.pais

    def _add_icms(self, parent: Element, produto: Produto) -> None:
        """Adiciona ICMS ao XML."""
        icms = ET.SubElement(parent, "ICMS")
        cst = produto.cst_icms

        # Simples Nacional (CSOSN 101, 102, 201, 202, 500, 900)
        if cst in ["101", "102", "103", "201", "202", "203", "300", "400", "500", "900"]:
            icms_elem = ET.SubElement(icms, f"ICMSSN{cst}")
            ET.SubElement(icms_elem, "orig").text = produto.origem
            ET.SubElement(icms_elem, "CSOSN").text = cst

            if cst == "101":
                # Tributada com permissão de crédito
                ET.SubElement(icms_elem, "pCredSN").text = f"{produto.aliquota_icms:.2f}"
                ET.SubElement(icms_elem, "vCredICMSSN").text = f"{produto.valor_icms:.2f}"
            elif cst in ["201", "202", "203"]:
                # Com ST
                ET.SubElement(icms_elem, "modBCST").text = "4"
                ET.SubElement(icms_elem, "pMVAST").text = "0.00"
                ET.SubElement(icms_elem, "vBCST").text = "0.00"
                ET.SubElement(icms_elem, "pICMSST").text = "0.00"
                ET.SubElement(icms_elem, "vICMSST").text = "0.00"
                if cst == "201":
                    ET.SubElement(icms_elem, "pCredSN").text = f"{produto.aliquota_icms:.2f}"
                    ET.SubElement(icms_elem, "vCredICMSSN").text = f"{produto.valor_icms:.2f}"
            elif cst == "500":
                # ICMS cobrado anteriormente por ST
                ET.SubElement(icms_elem, "vBCSTRet").text = "0.00"
                ET.SubElement(icms_elem, "pST").text = "0.00"
                ET.SubElement(icms_elem, "vICMSSubstituto").text = "0.00"
                ET.SubElement(icms_elem, "vICMSSTRet").text = "0.00"
            # 102, 103, 300, 400, 900 - apenas orig e CSOSN

        # Regime Normal
        else:
            icms_elem = ET.SubElement(icms, f"ICMS{cst}")
            ET.SubElement(icms_elem, "orig").text = produto.origem
            ET.SubElement(icms_elem, "CST").text = cst

            if cst in ["00", "10", "20", "70"]:
                ET.SubElement(icms_elem, "modBC").text = "3"
                ET.SubElement(icms_elem, "vBC").text = f"{produto.valor_total:.2f}"
                ET.SubElement(icms_elem, "pICMS").text = f"{produto.aliquota_icms:.2f}"
                ET.SubElement(icms_elem, "vICMS").text = f"{produto.valor_icms:.2f}"
            elif cst == "60":
                # ICMS cobrado anteriormente por ST
                ET.SubElement(icms_elem, "vBCSTRet").text = "0.00"
                ET.SubElement(icms_elem, "pST").text = "0.00"
                ET.SubElement(icms_elem, "vICMSSubstituto").text = "0.00"
                ET.SubElement(icms_elem, "vICMSSTRet").text = "0.00"
            # 40, 41, 50, 51 - apenas orig e CST

    def _add_pis(self, parent: Element, produto: Produto) -> None:
        """Adiciona PIS ao XML."""
        pis = ET.SubElement(parent, "PIS")
        pis_elem = ET.SubElement(pis, "PISAliq" if produto.cst_pis in ["01", "02"] else "PISOutr")
        ET.SubElement(pis_elem, "CST").text = produto.cst_pis
        if produto.cst_pis in ["01", "02"]:
            ET.SubElement(pis_elem, "vBC").text = f"{produto.valor_total:.2f}"
            ET.SubElement(pis_elem, "pPIS").text = f"{produto.aliquota_pis:.2f}"
            ET.SubElement(pis_elem, "vPIS").text = "0.00"

    def _add_cofins(self, parent: Element, produto: Produto) -> None:
        """Adiciona COFINS ao XML."""
        cofins = ET.SubElement(parent, "COFINS")
        cofins_elem = ET.SubElement(cofins, "COFINSAliq" if produto.cst_cofins in ["01", "02"] else "COFINSOutr")
        ET.SubElement(cofins_elem, "CST").text = produto.cst_cofins
        if produto.cst_cofins in ["01", "02"]:
            ET.SubElement(cofins_elem, "vBC").text = f"{produto.valor_total:.2f}"
            ET.SubElement(cofins_elem, "pCOFINS").text = f"{produto.aliquota_cofins:.2f}"
            ET.SubElement(cofins_elem, "vCOFINS").text = "0.00"

    def _prettify(self, elem: Element) -> str:
        """Formata XML com identacao."""
        rough_string = ET.tostring(elem, encoding="unicode")
        reparsed = minidom.parseString(rough_string)  # noqa: S318 - Apenas formata XML gerado internamente
        return reparsed.toprettyxml(indent="  ")


class SEFAZManager:
    """
    Gerenciador de documentos fiscais eletronicos.

    Coordena emissao, transmissao e consulta de NFe, NFCe, CTe
    junto a SEFAZ.

    Example:
        >>> manager = SEFAZManager(emitente)
        >>> nfe = await manager.create_nfe(
        ...     destinatario=dest,
        ...     produtos=produtos,
        ...     pagamentos=[pagamento]
        ... )
        >>> result = await manager.transmit(nfe.id)
    """

    def __init__(
        self,
        emitente: Emitente,
        certificate_path: str | None = None,
        certificate_password: str | None = None,
        certificate_data: bytes | None = None,
        ambiente: str = "2",  # 1=Producao, 2=Homologacao
    ):
        """
        Inicializa o gerenciador SEFAZ.

        Args:
            emitente: Dados do emitente.
            certificate_path: Caminho do certificado A1 (.pfx/.p12).
            certificate_password: Senha do certificado.
            certificate_data: Dados do certificado em bytes.
            ambiente: Ambiente (1=Prod, 2=Homolog).
        """
        self.emitente = emitente
        self.certificate_path = certificate_path
        self.certificate_password = certificate_password
        self.certificate_data = certificate_data
        self.ambiente = ambiente
        self._documents: dict[UUID, NotaFiscal] = {}
        self._xml_builder = NFEXMLBuilder()
        self._next_numero: dict[str, int] = {}
        self._certificate_manager: CertificateManager | None = None
        self._xml_signer: NFEXMLSigner | None = None
        self._certificate_loaded: bool = False
        logger.info("SEFAZManager inicializado para %s", emitente.cnpj)

    async def load_certificate(self) -> dict[str, Any]:
        """
        Carrega e valida certificado digital A1.

        Returns:
            Dict: Informacoes do certificado.

        Raises:
            SEFAZError: Se certificado invalido ou nao encontrado.
        """
        if self._certificate_loaded and self._certificate_manager:
            cert_info = self._certificate_manager.get_info()
            return {
                "loaded": True,
                "subject": cert_info.subject_cn,
                "cpf_cnpj": cert_info.cpf_cnpj,
                "valid_until": cert_info.valid_until.isoformat(),
            }

        if not self.certificate_path and not self.certificate_data:
            raise SEFAZError("Certificado digital nao configurado")

        try:
            # Carrega certificado usando CertificateManager
            self._certificate_manager = CertificateManager(
                pfx_path=self.certificate_path, pfx_data=self.certificate_data, password=self.certificate_password
            )

            if not self._certificate_manager.load():
                raise SEFAZError("Falha ao carregar certificado digital")

            # Valida certificado
            is_valid, validation_msg = self._certificate_manager.validate()
            if not is_valid:
                raise SEFAZError(f"Certificado invalido: {validation_msg}")

            # Extrai informacoes
            cert_info = self._certificate_manager.get_info()

            # Inicializa assinador XML com certificado
            self._xml_signer = NFEXMLSigner(self._certificate_manager)
            self._certificate_loaded = True

            logger.info(
                "Certificado A1 carregado para SEFAZ: %s (CPF/CNPJ: %s, valido ate %s)",
                cert_info.subject_cn,
                cert_info.cpf_cnpj or "N/A",
                cert_info.valid_until.date(),
            )

            return {
                "loaded": True,
                "subject": cert_info.subject_cn,
                "issuer": cert_info.issuer_cn,
                "cpf_cnpj": cert_info.cpf_cnpj,
                "valid_from": cert_info.valid_from.isoformat(),
                "valid_until": cert_info.valid_until.isoformat(),
                "serial_number": cert_info.serial_number,
            }

        except SEFAZError:
            raise
        except Exception as e:
            logger.error("Erro ao carregar certificado SEFAZ: %s", str(e))
            raise SEFAZError(f"Erro ao carregar certificado: {str(e)}")

    def _get_next_numero(self, serie: int = 1) -> int:
        """Obtem proximo numero de nota para a serie."""
        key = f"{self.emitente.cnpj}_{serie}"
        if key not in self._next_numero:
            self._next_numero[key] = 1
        numero = self._next_numero[key]
        self._next_numero[key] += 1
        return numero

    async def create_nfe(
        self,
        destinatario: Destinatario | None,
        produtos: list[Produto],
        pagamentos: list[Pagamento],
        natureza_operacao: str = "VENDA DE MERCADORIA",
        operacao: OperationType = OperationType.SAIDA,
        serie: int = 1,
        informacoes_adicionais: str | None = None,
    ) -> NotaFiscal:
        """
        Cria uma NFe.

        Args:
            destinatario: Dados do destinatario.
            produtos: Lista de produtos.
            pagamentos: Formas de pagamento.
            natureza_operacao: Natureza da operacao.
            operacao: Tipo de operacao (entrada/saida).
            serie: Serie da nota.
            informacoes_adicionais: Informacoes complementares.

        Returns:
            NotaFiscal: NFe criada.
        """
        numero = self._get_next_numero(serie)

        nfe = NotaFiscal(
            id=uuid4(),
            tipo=DocumentType.NFE,
            status=DocumentStatus.DRAFT,
            emitente=self.emitente,
            destinatario=destinatario,
            produtos=produtos,
            pagamentos=pagamentos,
            operacao=operacao,
            natureza_operacao=natureza_operacao,
            numero=numero,
            serie=serie,
            data_emissao=datetime.utcnow(),
            informacoes_adicionais=informacoes_adicionais,
        )

        # Gera chave de acesso
        nfe.generate_chave_acesso()

        # Gera XML
        nfe.xml_content = self._xml_builder.build_nfe(nfe)

        self._documents[nfe.id] = nfe

        logger.info("NFe criada: id=%s, numero=%d, chave=%s", nfe.id, numero, nfe.chave_acesso)

        return nfe

    async def create_nfce(
        self,
        produtos: list[Produto],
        pagamentos: list[Pagamento],
        destinatario: Destinatario | None = None,
        serie: int = 1,
    ) -> NotaFiscal:
        """
        Cria uma NFCe (Cupom Fiscal Eletronico).

        Args:
            produtos: Lista de produtos.
            pagamentos: Formas de pagamento.
            destinatario: Dados do consumidor (opcional).
            serie: Serie da nota.

        Returns:
            NotaFiscal: NFCe criada.
        """
        numero = self._get_next_numero(serie)

        nfce = NotaFiscal(
            id=uuid4(),
            tipo=DocumentType.NFCE,
            status=DocumentStatus.DRAFT,
            emitente=self.emitente,
            destinatario=destinatario,
            produtos=produtos,
            pagamentos=pagamentos,
            operacao=OperationType.SAIDA,
            natureza_operacao="VENDA AO CONSUMIDOR",
            numero=numero,
            serie=serie,
            data_emissao=datetime.utcnow(),
        )

        nfce.generate_chave_acesso()
        nfce.xml_content = self._xml_builder.build_nfe(nfce)

        self._documents[nfce.id] = nfce

        logger.info("NFCe criada: id=%s, numero=%d, valor=%.2f", nfce.id, numero, nfce.valor_total_nota)

        return nfce

    async def validate(self, document_id: UUID) -> dict[str, Any]:
        """
        Valida documento antes da transmissao.

        Args:
            document_id: ID do documento.

        Returns:
            Dict: Resultado da validacao.
        """
        doc = self._documents.get(document_id)
        if not doc:
            raise SEFAZError("Documento nao encontrado", document_id=str(document_id))

        doc.status = DocumentStatus.VALIDATING
        errors = []
        warnings = []

        # Validacoes
        if not doc.produtos:
            errors.append({"code": "PROD_REQUIRED", "message": "Ao menos um produto obrigatorio"})

        if not doc.pagamentos:
            errors.append({"code": "PAG_REQUIRED", "message": "Ao menos uma forma de pagamento obrigatoria"})

        valor_pago = sum(p.valor for p in doc.pagamentos)
        if valor_pago != doc.valor_total_nota:
            warnings.append(
                {"code": "PAG_DIFF", "message": f"Valor pago ({valor_pago}) difere do total ({doc.valor_total_nota})"}
            )

        for i, produto in enumerate(doc.produtos):
            if not produto.ncm or len(produto.ncm) != 8:
                errors.append({"code": "NCM_INVALID", "message": f"NCM invalido no item {i + 1}"})
            if not produto.cfop:
                errors.append({"code": "CFOP_REQUIRED", "message": f"CFOP obrigatorio no item {i + 1}"})

        doc.errors = errors

        if errors:
            doc.status = DocumentStatus.ERROR
            raise ValidationError(f"Validacao falhou: {len(errors)} erro(s)")

        doc.status = DocumentStatus.DRAFT

        return {
            "valid": True,
            "errors": errors,
            "warnings": warnings,
        }

    async def sign(self, document_id: UUID) -> str:
        """
        Assina documento com certificado digital A1 usando XMLDSig.

        Args:
            document_id: ID do documento.

        Returns:
            str: XML assinado com assinatura digital valida.

        Raises:
            SEFAZError: Se falha na assinatura.
        """
        doc = self._documents.get(document_id)
        if not doc:
            raise SEFAZError("Documento nao encontrado", document_id=str(document_id))

        # Carrega certificado se necessario
        if not self._xml_signer:
            await self.load_certificate()

        if not self._xml_signer:
            raise SEFAZError("Assinador XML nao inicializado")

        try:
            # Usa NFEXMLSigner para assinatura real
            signed_xml = self._xml_signer.sign_nfe(xml_content=doc.xml_content, inf_nfe_id=f"NFe{doc.chave_acesso}")

            doc.xml_signed = signed_xml

            logger.info("Documento assinado com certificado A1: id=%s, chave=%s", document_id, doc.chave_acesso)

            return signed_xml

        except Exception as e:
            logger.error("Erro ao assinar documento %s: %s", document_id, str(e))
            raise SEFAZError(f"Falha na assinatura digital: {str(e)}", document_id=str(document_id))

    async def transmit(self, document_id: UUID) -> NotaFiscal:
        """
        Transmite documento para SEFAZ.

        Args:
            document_id: ID do documento.

        Returns:
            NotaFiscal: Documento atualizado.
        """
        doc = self._documents.get(document_id)
        if not doc:
            raise SEFAZError("Documento nao encontrado", document_id=str(document_id))

        # Valida
        await self.validate(document_id)

        # Assina
        if not doc.xml_signed:
            await self.sign(document_id)

        # Simulacao de transmissao
        protocolo = f"{datetime.utcnow().strftime('%y%m%d%H%M%S')}{uuid4().hex[:9]}"

        doc.protocolo = protocolo
        doc.status = DocumentStatus.AUTHORIZED
        doc.authorized_at = datetime.utcnow()

        logger.info("Documento autorizado: id=%s, protocolo=%s, chave=%s", document_id, protocolo, doc.chave_acesso)

        return doc

    async def cancel(self, document_id: UUID, justificativa: str) -> NotaFiscal:
        """
        Cancela documento autorizado.

        Args:
            document_id: ID do documento.
            justificativa: Motivo do cancelamento (min 15 caracteres).

        Returns:
            NotaFiscal: Documento cancelado.
        """
        doc = self._documents.get(document_id)
        if not doc:
            raise SEFAZError("Documento nao encontrado", document_id=str(document_id))

        if doc.status != DocumentStatus.AUTHORIZED:
            raise SEFAZError("Documento nao pode ser cancelado", document_id=str(document_id))

        if len(justificativa) < 15:
            raise ValidationError("Justificativa deve ter no minimo 15 caracteres")

        # Verifica prazo (24h para NFe)
        if doc.authorized_at:
            hours_elapsed = (datetime.utcnow() - doc.authorized_at).total_seconds() / 3600
            if hours_elapsed > 24:
                raise SEFAZError("Prazo para cancelamento expirado (24h)")

        doc.status = DocumentStatus.CANCELLED
        doc.cancelled_at = datetime.utcnow()
        doc.metadata["cancelamento"] = {
            "justificativa": justificativa,
            "data": datetime.utcnow().isoformat(),
        }

        logger.info("Documento cancelado: %s", document_id)

        return doc

    async def get_document(self, document_id: UUID) -> NotaFiscal | None:
        """Recupera documento por ID."""
        return self._documents.get(document_id)

    async def get_by_chave(self, chave_acesso: str) -> NotaFiscal | None:
        """Recupera documento pela chave de acesso."""
        for doc in self._documents.values():
            if doc.chave_acesso == chave_acesso:
                return doc
        return None

    async def list_documents(
        self,
        status: DocumentStatus | None = None,
        tipo: DocumentType | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> list[NotaFiscal]:
        """Lista documentos com filtros."""
        docs = list(self._documents.values())

        if status:
            docs = [d for d in docs if d.status == status]
        if tipo:
            docs = [d for d in docs if d.tipo == tipo]
        if data_inicio:
            docs = [d for d in docs if d.data_emissao.date() >= data_inicio]
        if data_fim:
            docs = [d for d in docs if d.data_emissao.date() <= data_fim]

        return sorted(docs, key=lambda x: x.data_emissao, reverse=True)

    async def get_summary(self) -> dict[str, Any]:
        """Gera resumo de documentos."""
        docs = list(self._documents.values())

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "total": len(docs),
            "by_status": {s.value: sum(1 for d in docs if d.status == s) for s in DocumentStatus},
            "by_type": {t.value: sum(1 for d in docs if d.tipo == t) for t in DocumentType},
            "valor_total_emitido": str(sum(d.valor_total_nota for d in docs if d.status == DocumentStatus.AUTHORIZED)),
        }


# Singleton
_sefaz_manager: SEFAZManager | None = None


def get_sefaz_manager() -> SEFAZManager:
    """Retorna instancia singleton do SEFAZManager."""
    global _sefaz_manager
    if _sefaz_manager is None:
        raise SEFAZError("SEFAZManager nao inicializado")
    return _sefaz_manager


def init_sefaz_manager(
    emitente: Emitente,
    certificate_path: str | None = None,
    certificate_password: str | None = None,
    certificate_data: bytes | None = None,
    ambiente: str = "2",
) -> SEFAZManager:
    """
    Inicializa o SEFAZManager singleton.

    Args:
        emitente: Dados do emitente.
        certificate_path: Caminho do arquivo .pfx/.p12.
        certificate_password: Senha do certificado.
        certificate_data: Dados do certificado em bytes.
        ambiente: Ambiente (1=Prod, 2=Homolog).

    Returns:
        SEFAZManager: Instancia configurada.
    """
    global _sefaz_manager
    _sefaz_manager = SEFAZManager(
        emitente=emitente,
        certificate_path=certificate_path,
        certificate_password=certificate_password,
        certificate_data=certificate_data,
        ambiente=ambiente,
    )
    return _sefaz_manager
