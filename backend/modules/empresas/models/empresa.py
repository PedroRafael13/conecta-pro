"""Modelos SQLAlchemy para o módulo de Empresas (Multi-CNPJ)."""

import enum
import uuid
from datetime import date

from sqlalchemy import Boolean, Column, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class RegimeTributarioEnum(enum.StrEnum):
    SIMPLES_NACIONAL = "simples_nacional"
    LUCRO_PRESUMIDO = "lucro_presumido"
    LUCRO_REAL = "lucro_real"
    MEI = "mei"


class AnexoSimplesEnum(enum.StrEnum):
    ANEXO_I = "I"  # Comércio
    ANEXO_II = "II"  # Indústria
    ANEXO_III = "III"  # Serviços (vigilância)
    ANEXO_IV = "IV"  # Construção civil
    ANEXO_V = "V"  # Serviços (outros)


class EmpresaStatusEnum(enum.StrEnum):
    ATIVA = "ativa"
    EM_ABERTURA = "em_abertura"
    INATIVA = "inativa"
    EM_ENCERRAMENTO = "em_encerramento"


class LiminarTipoEnum(enum.StrEnum):
    PIS_COFINS_ZERO = "pis_cofins_zero"
    INSS_NAO_RETIDO = "inss_nao_retido"
    ISS_ISENTO = "iss_isento"
    OUTROS = "outros"


class LiminarStatusEnum(enum.StrEnum):
    A_SOLICITAR = "a_solicitar"
    AGUARDANDO = "aguardando"
    CONCEDIDA = "concedida"
    CASSADA = "cassada"
    EXPIRADA = "expirada"


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(UUID(as_uuid=True), ForeignKey("condominios.id"), nullable=False, index=True)

    # Identificação
    slug = Column(String(50), nullable=False)
    razao_social = Column(String(200), nullable=False)
    nome_fantasia = Column(String(200))
    cnpj = Column(String(18), unique=True, nullable=True)

    # Inscrições
    inscricao_municipal = Column(String(30))
    inscricao_estadual = Column(String(30))
    inscricao_suframa = Column(String(20))
    codigo_municipio_ibge = Column(String(10), default="1302603")  # Manaus padrão

    # Regime tributário
    regime_tributario = Column(String(30), nullable=False)
    anexo_simples = Column(String(5))  # Apenas Simples Nacional
    data_opcao_simples = Column(Date)
    data_desenquadramento_simples = Column(Date)

    # Regime futuro (planejamento)
    regime_futuro = Column(String(30))
    data_prevista_mudanca_regime = Column(Date)

    # Certificado digital
    certificado_a1_path = Column(String(500))
    certificado_a1_senha = Column(String(200))  # Criptografada
    certificado_validade = Column(Date)

    # Contador
    contador_software = Column(String(100))
    contador_email = Column(String(200))
    contador_nome = Column(String(200))

    # Tipos de serviços desta empresa
    tipos_servicos = Column(JSON, default=list)

    # Configurações NFS-e
    nfse_ambiente = Column(String(20), default="homologacao")
    nfse_serie_rps = Column(String(5), default="1")
    nfse_numero_inicial = Column(String(10), default="1")

    # Status
    status = Column(String(20), default=EmpresaStatusEnum.ATIVA.value)
    is_principal = Column(Boolean, default=False)

    # Metadados
    observacoes = Column(Text)
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    # Relationships
    liminares = relationship("Liminar", back_populates="empresa", cascade="all, delete-orphan")


class Liminar(Base):
    __tablename__ = "liminares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)

    tipo = Column(String(30), nullable=False)
    descricao = Column(String(500), nullable=False)

    # Processo judicial
    numero_processo = Column(String(100))
    vara = Column(String(200))
    tribunal = Column(String(100))
    advogado = Column(String(200))

    # Datas
    data_solicitacao = Column(Date)
    data_concessao = Column(Date)
    data_validade = Column(Date)

    status = Column(String(20), default=LiminarStatusEnum.A_SOLICITAR.value)

    # Efeitos fiscais (JSON)
    efeitos = Column(JSON, default=dict)

    fundamento_legal = Column(Text)
    observacoes = Column(Text)

    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    empresa = relationship("Empresa", back_populates="liminares")
