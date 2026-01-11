"""
Models PCMSO (NR-7) - Programa de Controle Medico de Saude Ocupacional
======================================================================

Modelos para gerenciamento de exames medicos ocupacionais e ASO.
"""

import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional, List

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Date,
    Integer, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from core.models import Base


class ExamType(str, Enum):
    """Tipos de exame medico ocupacional (NR-7)."""
    ADMISSIONAL = "admissional"
    PERIODICO = "periodico"
    RETORNO_TRABALHO = "retorno_trabalho"
    MUDANCA_FUNCAO = "mudanca_funcao"
    DEMISSIONAL = "demissional"


class ExamStatus(str, Enum):
    """Status do exame medico."""
    AGENDADO = "agendado"
    CONFIRMADO = "confirmado"
    REALIZADO = "realizado"
    CANCELADO = "cancelado"
    NAO_COMPARECEU = "nao_compareceu"


class FitnessResult(str, Enum):
    """Resultado de aptidao do ASO."""
    APTO = "apto"
    INAPTO = "inapto"
    APTO_COM_RESTRICOES = "apto_com_restricoes"


class MedicalExam(Base):
    """
    Exame Medico Ocupacional.

    Representa um exame medico agendado ou realizado para um funcionario,
    conforme exigencias da NR-7.
    """
    __tablename__ = "health_medical_exams"

    # Identificacao
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    funcionario_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Tipo e status
    tipo_exame = Column(String(30), nullable=False, index=True)
    status = Column(String(20), nullable=False, default=ExamStatus.AGENDADO.value)

    # Dados do funcionario no momento do exame
    funcao = Column(String(100), nullable=False)
    setor = Column(String(100), nullable=False)
    riscos = Column(JSONB, default=list)  # Riscos ocupacionais da funcao

    # Agendamento
    data_agendamento = Column(Date, nullable=False, index=True)
    hora_agendamento = Column(String(5), nullable=True)  # HH:MM

    # Realizacao
    data_realizacao = Column(DateTime, nullable=True)
    local_realizacao = Column(String(200), nullable=True)

    # Exames complementares solicitados
    exames_complementares = Column(JSONB, default=list)

    # Observacoes
    observacoes = Column(Text, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    aso = relationship("ASO", back_populates="exame", uselist=False)
    exames_realizados = relationship("ComplementaryExam", back_populates="exame_principal")

    # Indices
    __table_args__ = (
        Index('idx_exam_funcionario_tipo', 'funcionario_id', 'tipo_exame'),
        Index('idx_exam_data_status', 'data_agendamento', 'status'),
    )

    def __repr__(self) -> str:
        return f"<MedicalExam {self.tipo_exame} - {self.data_agendamento}>"

    @property
    def esta_pendente(self) -> bool:
        """Verifica se o exame esta pendente de realizacao."""
        return self.status in [ExamStatus.AGENDADO.value, ExamStatus.CONFIRMADO.value]


class ASO(Base):
    """
    Atestado de Saude Ocupacional (ASO).

    Documento emitido apos realizacao do exame medico,
    atestando a aptidao ou inaptidao do trabalhador.
    """
    __tablename__ = "health_asos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exame_id = Column(UUID(as_uuid=True), ForeignKey("health_medical_exams.id"), nullable=False, unique=True)

    # Resultado
    resultado = Column(String(30), nullable=False)  # apto, inapto, apto_com_restricoes
    restricoes = Column(JSONB, default=list)  # Lista de restricoes se aplicavel

    # Validade
    data_emissao = Column(DateTime, nullable=False, default=datetime.utcnow)
    validade_dias = Column(Integer, nullable=False, default=365)
    data_vencimento = Column(Date, nullable=False)

    # Medico responsavel
    medico_responsavel = Column(String(100), nullable=False)
    crm = Column(String(20), nullable=False)
    uf_crm = Column(String(2), nullable=True, default="AM")

    # Documento
    numero_aso = Column(String(50), nullable=True, unique=True)
    documento_url = Column(String(500), nullable=True)  # PDF gerado

    # Assinaturas
    assinatura_medico = Column(Boolean, default=False)
    assinatura_funcionario = Column(Boolean, default=False)
    data_assinatura_funcionario = Column(DateTime, nullable=True)

    # Status
    ativo = Column(Boolean, default=True)
    cancelado = Column(Boolean, default=False)
    motivo_cancelamento = Column(Text, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    exame = relationship("MedicalExam", back_populates="aso")

    # Indices
    __table_args__ = (
        Index('idx_aso_vencimento', 'data_vencimento'),
        Index('idx_aso_resultado', 'resultado'),
    )

    def __repr__(self) -> str:
        return f"<ASO {self.numero_aso} - {self.resultado}>"

    @property
    def esta_vencido(self) -> bool:
        """Verifica se o ASO esta vencido."""
        return date.today() > self.data_vencimento

    @property
    def dias_para_vencer(self) -> int:
        """Retorna dias restantes para vencimento."""
        delta = self.data_vencimento - date.today()
        return max(0, delta.days)


class ComplementaryExam(Base):
    """
    Exame Complementar.

    Exames adicionais solicitados (audiometria, espirometria, etc).
    """
    __tablename__ = "health_complementary_exams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exame_principal_id = Column(UUID(as_uuid=True), ForeignKey("health_medical_exams.id"), nullable=False)

    # Identificacao
    nome = Column(String(100), nullable=False)
    codigo = Column(String(20), nullable=True)  # Codigo TUSS se aplicavel

    # Realizacao
    data_solicitacao = Column(Date, nullable=False, default=date.today)
    data_realizacao = Column(DateTime, nullable=True)
    laboratorio = Column(String(200), nullable=True)

    # Resultado
    resultado = Column(Text, nullable=True)
    resultado_arquivo_url = Column(String(500), nullable=True)
    valores_referencia = Column(JSONB, default=dict)
    normal = Column(Boolean, nullable=True)

    # Status
    status = Column(String(20), nullable=False, default="solicitado")

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    exame_principal = relationship("MedicalExam", back_populates="exames_realizados")

    def __repr__(self) -> str:
        return f"<ComplementaryExam {self.nome}>"
