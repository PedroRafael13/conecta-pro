"""
Model de Certidao - Licitacoes
==============================
Gestao de certidoes para habilitacao em licitacoes.
"""

import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Date,
    Integer, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from core.models import Base


class CertificateType(str, Enum):
    """Tipo de certidao."""
    # Certidoes Federais
    CND_FEDERAL = "cnd_federal"                        # Certidao Unificada Federal (RFB + PGFN)
    CND_TRABALHISTA = "cnd_trabalhista"                # CNDT - Certidao Negativa Debitos Trabalhistas
    CRF_FGTS = "crf_fgts"                              # CRF - Certificado Regularidade FGTS

    # Certidoes Estaduais
    CND_ESTADUAL = "cnd_estadual"                      # Certidao Negativa Debitos Estaduais (ICMS)
    CND_DIVIDA_ATIVA_ESTADUAL = "cnd_divida_ativa_estadual"  # Divida Ativa Estadual

    # Certidoes Municipais
    CND_MUNICIPAL = "cnd_municipal"                    # Certidao Negativa Debitos Municipais (ISS/IPTU)
    CND_DIVIDA_ATIVA_MUNICIPAL = "cnd_divida_ativa_municipal"  # Divida Ativa Municipal

    # Outras Certidoes
    CERTIDAO_FALENCIA = "certidao_falencia"            # Certidao Negativa Falencia/Recuperacao
    CERTIDAO_CIVEL = "certidao_civel"                  # Certidao Distribuicao Civel
    CERTIDAO_CRIMINAL = "certidao_criminal"            # Certidao Antecedentes Criminais
    CERTIDAO_PROTESTO = "certidao_protesto"            # Certidao Negativa Protestos


class CertificateStatus(str, Enum):
    """Status da certidao."""
    VALID = "valid"                    # Valida (emitida e dentro da validade)
    EXPIRING = "expiring"              # Vencendo em breve (< 15 dias)
    EXPIRED = "expired"                # Vencida
    PENDING = "pending"                # Pendente (nao obtida)
    POSITIVE = "positive"              # Positiva (com debitos)
    POSITIVE_EFFECT_NEGATIVE = "positive_effect_negative"  # Positiva com efeito de negativa
    RENEWING = "renewing"              # Em renovacao automatica
    ERROR = "error"                    # Erro na obtencao


class CertificateSource(str, Enum):
    """Fonte de obtencao da certidao."""
    MANUAL = "manual"                  # Upload manual
    API_RECEITA = "api_receita"        # API Receita Federal
    API_FGTS = "api_fgts"              # API Caixa FGTS
    API_TST = "api_tst"                # API TST (CNDT)
    WEB_SCRAPING = "web_scraping"      # Web scraping
    SISTEMA = "sistema"                # Gerado pelo sistema


class Certificate(Base):
    """
    Certidao para Habilitacao em Licitacoes.

    Gerencia certidoes necessarias para comprovacao de regularidade
    fiscal, trabalhista e juridica em processos licitatorios.
    """
    __tablename__ = "bidding_certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao
    tipo = Column(String(50), nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    codigo_verificacao = Column(String(100), nullable=True)  # Codigo para validacao

    # Empresa
    cnpj = Column(String(18), nullable=False, index=True)
    razao_social = Column(String(255), nullable=True)

    # Datas
    data_emissao = Column(DateTime, nullable=True)
    data_validade = Column(DateTime, nullable=True, index=True)
    hora_emissao = Column(String(8), nullable=True)  # Algumas certidoes tem hora

    # Conteudo
    situacao = Column(String(100), nullable=True)  # Texto da situacao (NEGATIVA, POSITIVA, etc)
    texto_certidao = Column(Text, nullable=True)   # Conteudo textual da certidao
    observacoes_orgao = Column(Text, nullable=True)  # Observacoes do orgao emissor

    # Arquivo
    arquivo_url = Column(String(500), nullable=True)
    arquivo_nome = Column(String(255), nullable=True)
    arquivo_hash = Column(String(64), nullable=True)  # SHA256 do arquivo

    # Status e controle
    status = Column(String(30), nullable=False, default=CertificateStatus.PENDING.value, index=True)
    ativo = Column(Boolean, default=True, nullable=False, index=True)

    # Obtencao automatica
    fonte = Column(String(30), nullable=False, default=CertificateSource.MANUAL.value)
    obtencao_automatica = Column(Boolean, default=False)
    ultima_tentativa = Column(DateTime, nullable=True)
    proxima_tentativa = Column(DateTime, nullable=True)
    tentativas_falha = Column(Integer, default=0)
    erro_obtencao = Column(Text, nullable=True)

    # Alertas
    alerta_enviado_30d = Column(Boolean, default=False)
    alerta_enviado_15d = Column(Boolean, default=False)
    alerta_enviado_7d = Column(Boolean, default=False)

    # Orgao emissor
    orgao_emissor = Column(String(255), nullable=True)
    orgao_uf = Column(String(2), nullable=True)
    orgao_url = Column(String(500), nullable=True)  # URL para consulta/emissao

    # Metadados
    metadados = Column(JSONB, default=dict)  # Dados extras da API

    # Observacoes internas
    observacoes = Column(Text, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Indices compostos
    __table_args__ = (
        Index('idx_certificate_cnpj_tipo', 'cnpj', 'tipo'),
        Index('idx_certificate_validade', 'data_validade'),
        Index('idx_certificate_status', 'status'),
        Index('idx_certificate_obtencao', 'obtencao_automatica', 'proxima_tentativa'),
    )

    def __repr__(self) -> str:
        return f"<Certificate {self.tipo} - {self.cnpj}>"

    @property
    def esta_valida(self) -> bool:
        """Verifica se a certidao esta valida."""
        if self.status == CertificateStatus.POSITIVE.value:
            return False
        if not self.data_validade:
            return self.status == CertificateStatus.VALID.value
        return datetime.utcnow() <= self.data_validade

    @property
    def dias_para_vencer(self) -> Optional[int]:
        """Dias restantes ate o vencimento."""
        if not self.data_validade:
            return None
        delta = self.data_validade - datetime.utcnow()
        return max(0, delta.days)

    @property
    def horas_para_vencer(self) -> Optional[int]:
        """Horas restantes ate o vencimento (util para certidoes de curta validade)."""
        if not self.data_validade:
            return None
        delta = self.data_validade - datetime.utcnow()
        return max(0, int(delta.total_seconds() / 3600))

    @property
    def esta_vencendo(self) -> bool:
        """Verifica se esta vencendo em menos de 15 dias."""
        dias = self.dias_para_vencer
        if dias is None:
            return False
        return 0 < dias <= 15

    @property
    def precisa_renovar(self) -> bool:
        """Verifica se a certidao precisa ser renovada."""
        if self.status in [CertificateStatus.EXPIRED.value, CertificateStatus.PENDING.value]:
            return True
        return self.esta_vencendo

    @property
    def pode_usar_licitacao(self) -> bool:
        """Verifica se pode ser usada em licitacao."""
        return self.status in [
            CertificateStatus.VALID.value,
            CertificateStatus.POSITIVE_EFFECT_NEGATIVE.value
        ]

    def atualizar_status(self) -> None:
        """Atualiza o status baseado na validade."""
        if not self.data_validade:
            return

        agora = datetime.utcnow()
        dias = self.dias_para_vencer

        if agora > self.data_validade:
            self.status = CertificateStatus.EXPIRED.value
        elif dias <= 15:
            self.status = CertificateStatus.EXPIRING.value
        elif self.situacao and "POSITIVA" in self.situacao.upper():
            if "EFEITO" in self.situacao.upper() and "NEGATIVA" in self.situacao.upper():
                self.status = CertificateStatus.POSITIVE_EFFECT_NEGATIVE.value
            else:
                self.status = CertificateStatus.POSITIVE.value
        else:
            self.status = CertificateStatus.VALID.value

    def registrar_tentativa_falha(self, erro: str) -> None:
        """Registra uma tentativa de obtencao que falhou."""
        self.tentativas_falha += 1
        self.ultima_tentativa = datetime.utcnow()
        self.erro_obtencao = erro

        # Proxima tentativa com backoff exponencial (max 24h)
        from datetime import timedelta
        minutos_espera = min(2 ** self.tentativas_falha * 5, 1440)
        self.proxima_tentativa = datetime.utcnow() + timedelta(minutes=minutos_espera)

        if self.tentativas_falha >= 5:
            self.status = CertificateStatus.ERROR.value

    def registrar_sucesso_obtencao(
        self,
        data_emissao: datetime,
        data_validade: datetime,
        situacao: str,
        arquivo_url: str = None,
        codigo_verificacao: str = None
    ) -> None:
        """Registra sucesso na obtencao automatica."""
        self.data_emissao = data_emissao
        self.data_validade = data_validade
        self.situacao = situacao
        self.arquivo_url = arquivo_url
        self.codigo_verificacao = codigo_verificacao
        self.ultima_tentativa = datetime.utcnow()
        self.tentativas_falha = 0
        self.erro_obtencao = None

        # Proxima verificacao em 80% da validade
        from datetime import timedelta
        validade_dias = (data_validade - datetime.utcnow()).days
        dias_proxima = max(1, int(validade_dias * 0.8))
        self.proxima_tentativa = datetime.utcnow() + timedelta(days=dias_proxima)

        self.atualizar_status()
