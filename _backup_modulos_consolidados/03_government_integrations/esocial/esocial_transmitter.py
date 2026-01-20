"""
Module: eSocialTransmitter
Description: Sistema de transmissao de eventos para eSocial (Sistema de Escrituracao
             Digital das Obrigacoes Fiscais, Previdenciarias e Trabalhistas).
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: Decreto 8.373/2014 - eSocial
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, date
from uuid import UUID, uuid4
import xml.etree.ElementTree as ET
from xml.dom import minidom
import hashlib
import base64
import logging
import asyncio

from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Date, Text, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()


class EventType(str, Enum):
    """Tipos de eventos eSocial."""
    # Eventos de Tabelas (S-1000 a S-1080)
    S1000_EMPREGADOR = "S-1000"           # Informacoes do Empregador
    S1005_ESTABELECIMENTOS = "S-1005"     # Tabela de Estabelecimentos
    S1010_RUBRICAS = "S-1010"             # Tabela de Rubricas
    S1020_LOTACOES = "S-1020"             # Tabela de Lotacoes Tributarias
    S1030_CARGOS = "S-1030"               # Tabela de Cargos/Empregos
    S1035_CARREIRAS = "S-1035"            # Tabela de Carreiras Publicas
    S1040_FUNCOES = "S-1040"              # Tabela de Funcoes
    S1050_HORARIOS = "S-1050"             # Tabela de Horarios
    S1060_AMBIENTES = "S-1060"            # Tabela de Ambientes de Trabalho
    S1070_PROCESSOS = "S-1070"            # Tabela de Processos Administrativos

    # Eventos Nao Periodicos (S-2190 a S-2420)
    S2190_ADMISSAO_PRELIMINAR = "S-2190"  # Registro Preliminar de Admissao
    S2200_ADMISSAO = "S-2200"             # Cadastramento Inicial/Admissao
    S2205_ALTERACAO_DADOS = "S-2205"      # Alteracao de Dados Cadastrais
    S2206_ALTERACAO_CONTRATO = "S-2206"   # Alteracao de Contrato de Trabalho
    S2210_CAT = "S-2210"                  # Comunicacao de Acidente de Trabalho
    S2220_MONITORAMENTO_SAUDE = "S-2220"  # Monitoramento da Saude do Trabalhador
    S2230_AFASTAMENTO = "S-2230"          # Afastamento Temporario
    S2240_EXPOSICAO_RISCOS = "S-2240"     # Condicoes Ambientais do Trabalho
    S2299_DESLIGAMENTO = "S-2299"         # Desligamento
    S2300_TSV_INICIO = "S-2300"           # Trabalhador Sem Vinculo - Inicio
    S2306_TSV_ALTERACAO = "S-2306"        # TSV - Alteracao Contratual
    S2399_TSV_TERMINO = "S-2399"          # TSV - Termino

    # Eventos Periodicos (S-1200 a S-1299)
    S1200_REMUNERACAO = "S-1200"          # Remuneracao do Trabalhador
    S1202_REMUNERACAO_RPPS = "S-1202"     # Remuneracao Servidor RPPS
    S1207_BENEFICIOS_PREVIDENCIARIOS = "S-1207"  # Beneficios Previdenciarios
    S1210_PAGAMENTOS = "S-1210"           # Pagamentos de Rendimentos
    S1260_COMERCIALIZACAO = "S-1260"      # Comercializacao Producao Rural
    S1270_AQUISICAO = "S-1270"            # Contratacao de Trabalhadores Avulsos
    S1280_INFO_DESONERADA = "S-1280"      # Informacoes Complementares Desonerada
    S1298_REABERTURA = "S-1298"           # Reabertura dos Eventos Periodicos
    S1299_FECHAMENTO = "S-1299"           # Fechamento dos Eventos Periodicos

    # Eventos de SST (S-2210 a S-2240 - ja listados acima)
    # Eventos Totalizadores
    S5001_BASES_IRRF = "S-5001"           # Bases de Calculo IRRF
    S5002_BASES_CS = "S-5002"             # Imposto de Renda Retido na Fonte
    S5003_BASES_FGTS = "S-5003"           # Bases de Calculo FGTS
    S5011_TOTAL_CONTRIB = "S-5011"        # Consolidacao de Contribuicoes
    S5012_TOTAL_IRRF = "S-5012"           # Consolidacao IRRF

    # Exclusao
    S3000_EXCLUSAO = "S-3000"             # Exclusao de Eventos


class TransmissionStatus(str, Enum):
    """Status de transmissao de evento."""
    PENDING = "pending"               # Aguardando envio
    VALIDATING = "validating"         # Em validacao
    TRANSMITTED = "transmitted"       # Transmitido
    PROCESSING = "processing"         # Em processamento no governo
    ACCEPTED = "accepted"             # Aceito
    REJECTED = "rejected"             # Rejeitado
    ERROR = "error"                   # Erro na transmissao
    CANCELLED = "cancelled"           # Cancelado


class Environment(str, Enum):
    """Ambiente de transmissao."""
    PRODUCAO = "1"
    PRODUCAO_RESTRITA = "2"  # Homologacao


class ESocialError(Exception):
    """Erro em operacao eSocial."""

    def __init__(self, message: str, event_id: Optional[str] = None, code: Optional[str] = None):
        self.message = message
        self.event_id = event_id
        self.code = code
        super().__init__(self.message)


class ValidationError(ESocialError):
    """Erro de validacao de evento."""
    pass


class TransmissionError(ESocialError):
    """Erro de transmissao."""
    pass


@dataclass
class CertificateInfo:
    """Informacoes do certificado digital."""
    serial_number: str
    subject_cn: str
    issuer_cn: str
    valid_from: datetime
    valid_until: datetime
    type: str  # A1, A3

    def is_valid(self) -> bool:
        """Verifica se certificado esta valido."""
        now = datetime.utcnow()
        return self.valid_from <= now <= self.valid_until

    def days_until_expiry(self) -> int:
        """Dias ate vencimento."""
        return (self.valid_until - datetime.utcnow()).days


@dataclass
class ESocialEvent:
    """Evento eSocial."""
    id: UUID
    event_type: EventType
    status: TransmissionStatus
    employer_cnpj: str
    employee_cpf: Optional[str] = None
    xml_content: Optional[str] = None
    xml_signed: Optional[str] = None
    protocol: Optional[str] = None
    receipt_number: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    transmitted_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    reference_id: Optional[str] = None     # ID de referencia no sistema
    reference_date: Optional[date] = None  # Data de referencia do evento
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "event_type": self.event_type.value,
            "status": self.status.value,
            "employer_cnpj": self.employer_cnpj,
            "employee_cpf": self.employee_cpf,
            "protocol": self.protocol,
            "receipt_number": self.receipt_number,
            "created_at": self.created_at.isoformat(),
            "transmitted_at": self.transmitted_at.isoformat() if self.transmitted_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "errors": self.errors,
            "warnings": self.warnings,
        }


# SQLAlchemy Model
class ESocialEventModel(Base):
    """Modelo de banco para eventos eSocial."""
    __tablename__ = "gov_esocial_events"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    event_type = Column(String(20), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    employer_cnpj = Column(String(18), nullable=False, index=True)
    employee_cpf = Column(String(14), nullable=True, index=True)
    xml_content = Column(Text, nullable=True)
    xml_signed = Column(Text, nullable=True)
    protocol = Column(String(100), nullable=True, index=True)
    receipt_number = Column(String(100), nullable=True, unique=True)
    reference_id = Column(String(100), nullable=True, index=True)
    reference_date = Column(Date, nullable=True, index=True)
    errors = Column(JSONB, default=[])
    warnings = Column(JSONB, default=[])
    extra_metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    transmitted_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class XMLBuilder:
    """Construtor de XML para eventos eSocial."""

    NAMESPACE = "http://www.esocial.gov.br/schema/evt"
    VERSION = "S_1.1.0"  # Versao do layout

    def __init__(self, environment: Environment = Environment.PRODUCAO_RESTRITA):
        self.environment = environment

    def build_event_id(self, event_type: str, employer_cnpj: str) -> str:
        """Gera ID unico do evento."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        seq = uuid4().hex[:5].upper()
        # Formato: ID + CNPJ (14) + Tipo (6) + AAAAMMDDHHMMSS + SEQ (5)
        cnpj_clean = employer_cnpj.replace(".", "").replace("/", "").replace("-", "")
        type_code = event_type.replace("-", "").replace("S", "")
        return f"ID{cnpj_clean}{type_code}{timestamp}{seq}"

    def build_s2200_admissao(self, data: Dict[str, Any]) -> str:
        """Constroi XML do evento S-2200 (Admissao)."""
        event_id = self.build_event_id("S-2200", data["employer_cnpj"])

        root = ET.Element("eSocial", xmlns=self.NAMESPACE)
        evt = ET.SubElement(root, "evtAdmissao", Id=event_id)

        # ideEvento
        ide = ET.SubElement(evt, "ideEvento")
        ET.SubElement(ide, "indRetif").text = str(data.get("indRetif", 1))
        ET.SubElement(ide, "tpAmb").text = self.environment.value
        ET.SubElement(ide, "procEmi").text = "1"
        ET.SubElement(ide, "verProc").text = "CONECTA_PRO_1.0"

        # ideEmpregador
        emp = ET.SubElement(evt, "ideEmpregador")
        ET.SubElement(emp, "tpInsc").text = "1"
        ET.SubElement(emp, "nrInsc").text = data["employer_cnpj"][:8]

        # trabalhador
        trab = ET.SubElement(evt, "trabalhador")
        ET.SubElement(trab, "cpfTrab").text = data["cpf"]
        ET.SubElement(trab, "nmTrab").text = data["nome"]
        ET.SubElement(trab, "sexo").text = data["sexo"]
        ET.SubElement(trab, "racaCor").text = str(data.get("racaCor", 6))
        ET.SubElement(trab, "estCiv").text = str(data.get("estCiv", 1))
        ET.SubElement(trab, "grauInstr").text = str(data.get("grauInstr", "07"))

        # nascimento
        nasc = ET.SubElement(trab, "nascimento")
        ET.SubElement(nasc, "dtNascto").text = data["dtNascimento"]
        ET.SubElement(nasc, "paisNascto").text = data.get("paisNascto", "105")
        if data.get("paisNascto", "105") == "105":
            ET.SubElement(nasc, "paisNac").text = "105"

        # vinculo
        vinc = ET.SubElement(evt, "vinculo")
        ET.SubElement(vinc, "matricula").text = data["matricula"]
        ET.SubElement(vinc, "tpRegTrab").text = str(data.get("tpRegTrab", 1))
        ET.SubElement(vinc, "tpRegPrev").text = str(data.get("tpRegPrev", 1))
        ET.SubElement(vinc, "cadIni").text = "S" if data.get("cadIni", True) else "N"

        # infoRegimeTrab
        reg = ET.SubElement(vinc, "infoRegimeTrab")
        clt = ET.SubElement(reg, "infoCeletista")
        ET.SubElement(clt, "dtAdm").text = data["dtAdmissao"]
        ET.SubElement(clt, "tpAdmissao").text = str(data.get("tpAdmissao", 1))
        ET.SubElement(clt, "indAdmissao").text = str(data.get("indAdmissao", 1))
        ET.SubElement(clt, "tpRegJor").text = str(data.get("tpRegJor", 1))
        ET.SubElement(clt, "natAtividade").text = str(data.get("natAtividade", 1))
        ET.SubElement(clt, "dtBase").text = str(data.get("dtBase", 1))
        ET.SubElement(clt, "cnpjSindCategProf").text = data.get("cnpjSindicato", "")

        # infoContrato
        cont = ET.SubElement(vinc, "infoContrato")
        ET.SubElement(cont, "nmCargo").text = data.get("cargo", "")
        ET.SubElement(cont, "CBOCargo").text = data.get("cbo", "")

        # remuneracao
        rem = ET.SubElement(cont, "remuneracao")
        ET.SubElement(rem, "vrSalFx").text = str(data["salario"])
        ET.SubElement(rem, "undSalFixo").text = str(data.get("undSalFixo", 5))

        return self._prettify(root)

    def build_s2299_desligamento(self, data: Dict[str, Any]) -> str:
        """Constroi XML do evento S-2299 (Desligamento)."""
        event_id = self.build_event_id("S-2299", data["employer_cnpj"])

        root = ET.Element("eSocial", xmlns=self.NAMESPACE)
        evt = ET.SubElement(root, "evtDeslig", Id=event_id)

        # ideEvento
        ide = ET.SubElement(evt, "ideEvento")
        ET.SubElement(ide, "indRetif").text = str(data.get("indRetif", 1))
        ET.SubElement(ide, "tpAmb").text = self.environment.value
        ET.SubElement(ide, "procEmi").text = "1"
        ET.SubElement(ide, "verProc").text = "CONECTA_PRO_1.0"

        # ideEmpregador
        emp = ET.SubElement(evt, "ideEmpregador")
        ET.SubElement(emp, "tpInsc").text = "1"
        ET.SubElement(emp, "nrInsc").text = data["employer_cnpj"][:8]

        # ideVinculo
        vinc = ET.SubElement(evt, "ideVinculo")
        ET.SubElement(vinc, "cpfTrab").text = data["cpf"]
        ET.SubElement(vinc, "matricula").text = data["matricula"]

        # infoDeslig
        desl = ET.SubElement(evt, "infoDeslig")
        ET.SubElement(desl, "mtvDeslig").text = data["mtvDeslig"]
        ET.SubElement(desl, "dtDeslig").text = data["dtDesligamento"]
        ET.SubElement(desl, "indPagtoAPI").text = "S" if data.get("indPagtoAPI", True) else "N"
        ET.SubElement(desl, "dtProjFimAPI").text = data.get("dtProjFimAPI", data["dtDesligamento"])
        ET.SubElement(desl, "pensAlim").text = str(data.get("pensAlim", 0))
        ET.SubElement(desl, "percAliment").text = str(data.get("percAliment", 0))
        ET.SubElement(desl, "vrAlim").text = str(data.get("vrAlim", 0))

        return self._prettify(root)

    def build_s2220_monitoramento_saude(self, data: Dict[str, Any]) -> str:
        """Constroi XML do evento S-2220 (Monitoramento da Saude)."""
        event_id = self.build_event_id("S-2220", data["employer_cnpj"])

        root = ET.Element("eSocial", xmlns=self.NAMESPACE)
        evt = ET.SubElement(root, "evtMonit", Id=event_id)

        # ideEvento
        ide = ET.SubElement(evt, "ideEvento")
        ET.SubElement(ide, "indRetif").text = str(data.get("indRetif", 1))
        ET.SubElement(ide, "tpAmb").text = self.environment.value
        ET.SubElement(ide, "procEmi").text = "1"
        ET.SubElement(ide, "verProc").text = "CONECTA_PRO_1.0"

        # ideEmpregador
        emp = ET.SubElement(evt, "ideEmpregador")
        ET.SubElement(emp, "tpInsc").text = "1"
        ET.SubElement(emp, "nrInsc").text = data["employer_cnpj"][:8]

        # ideVinculo
        vinc = ET.SubElement(evt, "ideVinculo")
        ET.SubElement(vinc, "cpfTrab").text = data["cpf"]
        ET.SubElement(vinc, "matricula").text = data["matricula"]

        # exMedOcup
        exmed = ET.SubElement(evt, "exMedOcup")
        ET.SubElement(exmed, "tpExameOcup").text = str(data["tpExameOcup"])

        # aso
        aso = ET.SubElement(exmed, "aso")
        ET.SubElement(aso, "dtAso").text = data["dtAso"]
        ET.SubElement(aso, "resAso").text = str(data["resAso"])

        # exame
        for exame in data.get("exames", []):
            exam = ET.SubElement(aso, "exame")
            ET.SubElement(exam, "dtExm").text = exame["dtExm"]
            ET.SubElement(exam, "procRealizado").text = exame["procRealizado"]
            ET.SubElement(exam, "obsProc").text = exame.get("obsProc", "")

        # medico
        med = ET.SubElement(aso, "medico")
        ET.SubElement(med, "nmMed").text = data["nmMed"]
        ET.SubElement(med, "nrCRM").text = data["nrCRM"]
        ET.SubElement(med, "ufCRM").text = data["ufCRM"]

        return self._prettify(root)

    def _prettify(self, elem: ET.Element) -> str:
        """Formata XML com identacao."""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


class ESocialTransmitter:
    """
    Transmissor de eventos eSocial.

    Coordena geracao, validacao, assinatura e transmissao
    de eventos para o eSocial.

    Example:
        >>> transmitter = ESocialTransmitter(config)
        >>> event = await transmitter.create_event(
        ...     EventType.S2200_ADMISSAO,
        ...     employer_cnpj="12.345.678/0001-90",
        ...     data=admissao_data
        ... )
        >>> result = await transmitter.transmit(event.id)
    """

    WEBSERVICE_URLS = {
        Environment.PRODUCAO: "https://webservices.producao.esocial.gov.br",
        Environment.PRODUCAO_RESTRITA: "https://webservices.producaorestrita.esocial.gov.br",
    }

    def __init__(
        self,
        environment: Environment = Environment.PRODUCAO_RESTRITA,
        certificate_path: Optional[str] = None,
        certificate_password: Optional[str] = None
    ):
        """
        Inicializa o transmissor.

        Args:
            environment: Ambiente de transmissao.
            certificate_path: Caminho do certificado.
            certificate_password: Senha do certificado.
        """
        self.environment = environment
        self.certificate_path = certificate_path
        self.certificate_password = certificate_password
        self._events: Dict[UUID, ESocialEvent] = {}
        self._xml_builder = XMLBuilder(environment)
        self._certificate_info: Optional[CertificateInfo] = None
        logger.info("ESocialTransmitter inicializado (ambiente: %s)", environment.value)

    async def load_certificate(self) -> CertificateInfo:
        """
        Carrega e valida certificado digital.

        Returns:
            CertificateInfo: Informacoes do certificado.
        """
        # Simulacao - em producao usaria biblioteca de certificados
        self._certificate_info = CertificateInfo(
            serial_number="123456789",
            subject_cn="EMPRESA TESTE LTDA",
            issuer_cn="AC VALID",
            valid_from=datetime(2024, 1, 1),
            valid_until=datetime(2027, 1, 1),
            type="A1"
        )

        if not self._certificate_info.is_valid():
            raise ESocialError("Certificado digital vencido ou invalido")

        logger.info(
            "Certificado carregado: %s (valido ate %s)",
            self._certificate_info.subject_cn,
            self._certificate_info.valid_until.date()
        )

        return self._certificate_info

    async def create_event(
        self,
        event_type: EventType,
        employer_cnpj: str,
        data: Dict[str, Any],
        employee_cpf: Optional[str] = None,
        reference_id: Optional[str] = None,
        reference_date: Optional[date] = None
    ) -> ESocialEvent:
        """
        Cria evento eSocial.

        Args:
            event_type: Tipo do evento.
            employer_cnpj: CNPJ do empregador.
            data: Dados do evento.
            employee_cpf: CPF do trabalhador (se aplicavel).
            reference_id: ID de referencia no sistema.
            reference_date: Data de referencia.

        Returns:
            ESocialEvent: Evento criado.
        """
        # Gera XML baseado no tipo
        xml_content = await self._build_xml(event_type, employer_cnpj, data)

        event = ESocialEvent(
            id=uuid4(),
            event_type=event_type,
            status=TransmissionStatus.PENDING,
            employer_cnpj=employer_cnpj,
            employee_cpf=employee_cpf,
            xml_content=xml_content,
            reference_id=reference_id,
            reference_date=reference_date,
            metadata={"original_data": data},
        )

        self._events[event.id] = event

        logger.info(
            "Evento criado: id=%s, type=%s, cnpj=%s",
            event.id, event_type.value, employer_cnpj
        )

        return event

    async def _build_xml(
        self,
        event_type: EventType,
        employer_cnpj: str,
        data: Dict[str, Any]
    ) -> str:
        """Constroi XML do evento."""
        data["employer_cnpj"] = employer_cnpj

        if event_type == EventType.S2200_ADMISSAO:
            return self._xml_builder.build_s2200_admissao(data)
        elif event_type == EventType.S2299_DESLIGAMENTO:
            return self._xml_builder.build_s2299_desligamento(data)
        elif event_type == EventType.S2220_MONITORAMENTO_SAUDE:
            return self._xml_builder.build_s2220_monitoramento_saude(data)
        else:
            raise ESocialError(f"Tipo de evento nao implementado: {event_type.value}")

    async def validate_event(self, event_id: UUID) -> Dict[str, Any]:
        """
        Valida evento antes da transmissao.

        Args:
            event_id: ID do evento.

        Returns:
            Dict: Resultado da validacao.
        """
        event = self._events.get(event_id)
        if not event:
            raise ESocialError("Evento nao encontrado", str(event_id))

        event.status = TransmissionStatus.VALIDATING
        errors = []
        warnings = []

        # Valida XML
        try:
            ET.fromstring(event.xml_content)
        except ET.ParseError as e:
            errors.append({"code": "XML_INVALID", "message": str(e)})

        # Valida campos obrigatorios
        if not event.employer_cnpj:
            errors.append({"code": "CNPJ_REQUIRED", "message": "CNPJ do empregador obrigatorio"})

        # Valida certificado
        if self._certificate_info:
            days_until = self._certificate_info.days_until_expiry()
            if days_until < 30:
                warnings.append({
                    "code": "CERTIFICATE_EXPIRING",
                    "message": f"Certificado vence em {days_until} dias"
                })

        event.errors = errors
        event.warnings = warnings

        if errors:
            event.status = TransmissionStatus.ERROR
            raise ValidationError(f"Validacao falhou: {len(errors)} erro(s)")

        event.status = TransmissionStatus.PENDING

        return {
            "valid": True,
            "errors": errors,
            "warnings": warnings,
        }

    async def sign_event(self, event_id: UUID) -> str:
        """
        Assina evento com certificado digital.

        Args:
            event_id: ID do evento.

        Returns:
            str: XML assinado.
        """
        event = self._events.get(event_id)
        if not event:
            raise ESocialError("Evento nao encontrado", str(event_id))

        if not self._certificate_info:
            await self.load_certificate()

        # Simulacao de assinatura - em producao usaria XMLSec
        signature_value = base64.b64encode(
            hashlib.sha256(event.xml_content.encode()).digest()
        ).decode()

        # Adiciona elemento Signature ao XML
        signed_xml = event.xml_content.replace(
            "</eSocial>",
            f"""<Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignatureValue>{signature_value}</SignatureValue>
    <KeyInfo>
      <X509Data>
        <X509Certificate>{self._certificate_info.serial_number}</X509Certificate>
      </X509Data>
    </KeyInfo>
  </Signature>
</eSocial>"""
        )

        event.xml_signed = signed_xml

        logger.info("Evento assinado: %s", event_id)

        return signed_xml

    async def transmit(self, event_id: UUID) -> ESocialEvent:
        """
        Transmite evento para o eSocial.

        Args:
            event_id: ID do evento.

        Returns:
            ESocialEvent: Evento atualizado com resultado.
        """
        event = self._events.get(event_id)
        if not event:
            raise ESocialError("Evento nao encontrado", str(event_id))

        # Valida
        await self.validate_event(event_id)

        # Assina
        if not event.xml_signed:
            await self.sign_event(event_id)

        event.status = TransmissionStatus.TRANSMITTED
        event.transmitted_at = datetime.utcnow()

        # Simulacao de transmissao - em producao usaria zeep/requests
        protocol = f"PROT{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{uuid4().hex[:6].upper()}"
        event.protocol = protocol

        logger.info(
            "Evento transmitido: id=%s, protocol=%s",
            event_id, protocol
        )

        # Simula processamento
        event.status = TransmissionStatus.PROCESSING

        return event

    async def check_status(self, event_id: UUID) -> ESocialEvent:
        """
        Consulta status de processamento do evento.

        Args:
            event_id: ID do evento.

        Returns:
            ESocialEvent: Evento com status atualizado.
        """
        event = self._events.get(event_id)
        if not event:
            raise ESocialError("Evento nao encontrado", str(event_id))

        if event.status not in [TransmissionStatus.TRANSMITTED, TransmissionStatus.PROCESSING]:
            return event

        # Simulacao - em producao consultaria webservice
        event.status = TransmissionStatus.ACCEPTED
        event.processed_at = datetime.utcnow()
        event.receipt_number = f"REC{uuid4().hex[:12].upper()}"

        logger.info(
            "Evento aceito: id=%s, receipt=%s",
            event_id, event.receipt_number
        )

        return event

    async def get_event(self, event_id: UUID) -> Optional[ESocialEvent]:
        """Recupera evento por ID."""
        return self._events.get(event_id)

    async def list_events(
        self,
        status: Optional[TransmissionStatus] = None,
        event_type: Optional[EventType] = None,
        employer_cnpj: Optional[str] = None
    ) -> List[ESocialEvent]:
        """Lista eventos com filtros."""
        events = list(self._events.values())

        if status:
            events = [e for e in events if e.status == status]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if employer_cnpj:
            events = [e for e in events if e.employer_cnpj == employer_cnpj]

        return sorted(events, key=lambda x: x.created_at, reverse=True)

    async def get_pending_events(self) -> List[ESocialEvent]:
        """Lista eventos pendentes de transmissao."""
        return await self.list_events(status=TransmissionStatus.PENDING)

    async def batch_transmit(self, event_ids: List[UUID]) -> Dict[str, Any]:
        """
        Transmite lote de eventos.

        Args:
            event_ids: Lista de IDs de eventos.

        Returns:
            Dict: Resultado do lote.
        """
        results = {
            "total": len(event_ids),
            "success": 0,
            "failed": 0,
            "events": [],
        }

        for event_id in event_ids:
            try:
                event = await self.transmit(event_id)
                results["success"] += 1
                results["events"].append({
                    "id": str(event_id),
                    "status": event.status.value,
                    "protocol": event.protocol,
                })
            except ESocialError as e:
                results["failed"] += 1
                results["events"].append({
                    "id": str(event_id),
                    "status": "error",
                    "error": str(e),
                })

        logger.info(
            "Lote transmitido: %d/%d sucesso",
            results["success"], results["total"]
        )

        return results

    async def get_transmission_summary(self) -> Dict[str, Any]:
        """Gera resumo de transmissoes."""
        events = list(self._events.values())

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "total_events": len(events),
            "by_status": {
                status.value: sum(1 for e in events if e.status == status)
                for status in TransmissionStatus
            },
            "by_type": {},
            "pending_count": len(await self.get_pending_events()),
        }


# Singleton
_esocial_transmitter: Optional[ESocialTransmitter] = None


def get_esocial_transmitter() -> ESocialTransmitter:
    """Retorna instancia singleton do ESocialTransmitter."""
    global _esocial_transmitter
    if _esocial_transmitter is None:
        _esocial_transmitter = ESocialTransmitter()
    return _esocial_transmitter


def init_esocial_transmitter(
    environment: Environment = Environment.PRODUCAO_RESTRITA,
    certificate_path: Optional[str] = None,
    certificate_password: Optional[str] = None
) -> ESocialTransmitter:
    """Inicializa o ESocialTransmitter singleton."""
    global _esocial_transmitter
    _esocial_transmitter = ESocialTransmitter(environment, certificate_path, certificate_password)
    return _esocial_transmitter
