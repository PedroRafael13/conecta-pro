# SKILL: COMPLIANCE E AUDITORIA
## ERP Conecta Mais - Fase 2

**Versao:** 1.0
**Modulo:** Compliance
**Sprints:** 35-38 (Q1 2027)
**Executor:** Claude Opus 4.5

---

## INDICE

1. [Visao Geral](#1-visao-geral)
2. [LGPD - Lei Geral de Protecao de Dados](#2-lgpd)
3. [ISO 27001 - Seguranca da Informacao](#3-iso-27001)
4. [SOC 2 - Service Organization Control](#4-soc-2)
5. [Trilha de Auditoria](#5-trilha-de-auditoria)
6. [Gestao de Consentimento](#6-gestao-de-consentimento)
7. [Anonimizacao e Pseudonimizacao](#7-anonimizacao)
8. [Retencao de Dados](#8-retencao-de-dados)
9. [Relatorios de Conformidade](#9-relatorios-de-conformidade)
10. [Portal do Titular](#10-portal-do-titular)

---

## 1. VISAO GERAL

### 1.1 Escopo de Compliance

```
CONFORMIDADES IMPLEMENTADAS
===========================

1. LGPD (Lei 13.709/2018)
   - Gestao de consentimento
   - Direitos do titular
   - Anonimizacao de dados
   - Retencao e eliminacao
   - DPIA (Avaliacao de Impacto)
   - Registro de tratamento

2. ISO 27001:2022
   - SGSI (Sistema de Gestao de Seguranca)
   - Gestao de riscos
   - Controles de acesso
   - Criptografia
   - Continuidade de negocios
   - Auditoria interna

3. SOC 2 Type II
   - Seguranca
   - Disponibilidade
   - Integridade de processamento
   - Confidencialidade
   - Privacidade

4. AUDITORIA INTERNA
   - Trilha de auditoria completa
   - Logs imutaveis
   - Relatorios automatizados
   - Deteccao de anomalias
```

### 1.2 Estrutura do Modulo

```
modules/compliance/
├── models/
│   ├── consent.py              # Consentimentos LGPD
│   ├── data_subject.py         # Titular de dados
│   ├── data_processing.py      # Registro de tratamento
│   ├── audit_log.py            # Logs de auditoria
│   ├── retention_policy.py     # Politicas de retencao
│   ├── risk_assessment.py      # Avaliacao de riscos
│   └── compliance_control.py   # Controles ISO/SOC
├── schemas/
│   ├── consent_schemas.py
│   ├── audit_schemas.py
│   ├── dsar_schemas.py         # Data Subject Access Request
│   └── report_schemas.py
├── repositories/
│   ├── consent_repository.py
│   ├── audit_repository.py
│   └── retention_repository.py
├── services/
│   ├── consent_service.py
│   ├── anonymization_service.py
│   ├── audit_service.py
│   ├── retention_service.py
│   ├── dsar_service.py
│   └── compliance_report_service.py
├── controllers/
│   ├── consent_controller.py
│   ├── dsar_controller.py
│   ├── audit_controller.py
│   └── compliance_controller.py
└── tests/
    ├── test_consent.py
    ├── test_anonymization.py
    ├── test_audit.py
    └── test_retention.py
```

---

## 2. LGPD - LEI GERAL DE PROTECAO DE DADOS

### 2.1 Models LGPD

```python
# modules/compliance/models/consent.py
"""
Model de consentimento LGPD.

Registra consentimentos dos titulares para tratamento de dados.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class ConsentPurpose(str, Enum):
    """Finalidades de tratamento de dados."""

    CONTRATO = "contrato"
    OBRIGACAO_LEGAL = "obrigacao_legal"
    CONSENTIMENTO = "consentimento"
    INTERESSE_LEGITIMO = "interesse_legitimo"
    PROTECAO_VIDA = "protecao_vida"
    TUTELA_SAUDE = "tutela_saude"
    CREDITO = "protecao_credito"
    PESQUISA = "pesquisa"


class ConsentStatus(str, Enum):
    """Status do consentimento."""

    ATIVO = "ativo"
    REVOGADO = "revogado"
    EXPIRADO = "expirado"


class Consent(Base):
    """
    Representa um consentimento LGPD.

    Attributes:
        id: Identificador UUID
        data_subject_id: ID do titular
        purpose: Finalidade do tratamento
        legal_basis: Base legal
        description: Descricao do tratamento
        status: Status do consentimento
        granted_at: Data de concessao
        revoked_at: Data de revogacao (se aplicavel)
        expires_at: Data de expiracao
        ip_address: IP do dispositivo
        user_agent: User agent do navegador
        metadata: Metadados adicionais
    """

    __tablename__ = "lgpd_consents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    data_subject_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lgpd_data_subjects.id"),
        nullable=False,
    )
    purpose = Column(SQLEnum(ConsentPurpose), nullable=False)
    legal_basis = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(
        SQLEnum(ConsentStatus),
        default=ConsentStatus.ATIVO,
        nullable=False,
    )
    version = Column(String(20), default="1.0", nullable=False)

    # Timestamps
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Contexto da coleta
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    collection_point = Column(String(200), nullable=True)

    # Metadados
    metadata = Column(JSONB, default=dict)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relacionamentos
    data_subject = relationship("DataSubject", back_populates="consents")

    __table_args__ = (
        Index("ix_consents_subject_purpose", "data_subject_id", "purpose"),
        Index("ix_consents_status", "status"),
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return (
            f"<Consent(id={self.id}, "
            f"purpose='{self.purpose.value}', "
            f"status='{self.status.value}')>"
        )

    def revoke(self, reason: Optional[str] = None) -> None:
        """
        Revoga o consentimento.

        Args:
            reason: Motivo da revogacao
        """
        self.status = ConsentStatus.REVOGADO
        self.revoked_at = datetime.utcnow()
        if reason:
            self.metadata["revocation_reason"] = reason

    def is_valid(self) -> bool:
        """
        Verifica se consentimento esta valido.

        Returns:
            True se valido
        """
        if self.status != ConsentStatus.ATIVO:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
```

```python
# modules/compliance/models/data_subject.py
"""
Model de titular de dados.

Representa uma pessoa fisica cujos dados sao tratados.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class DataSubjectType(str, Enum):
    """Tipos de titular."""

    COLABORADOR = "colaborador"
    CLIENTE = "cliente"
    FORNECEDOR = "fornecedor"
    CANDIDATO = "candidato"
    VISITANTE = "visitante"
    OUTRO = "outro"


class DataSubject(Base):
    """
    Representa um titular de dados LGPD.

    Attributes:
        id: Identificador UUID
        external_id: ID externo (CPF hash)
        type: Tipo de titular
        email_hash: Hash do email
        phone_hash: Hash do telefone
        is_anonymized: Se foi anonimizado
        anonymized_at: Data de anonimizacao
    """

    __tablename__ = "lgpd_data_subjects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    external_id = Column(String(64), unique=True, nullable=False)  # SHA256 do CPF
    type = Column(SQLEnum(DataSubjectType), nullable=False)

    # Dados hashados para lookup
    email_hash = Column(String(64), nullable=True)
    phone_hash = Column(String(64), nullable=True)

    # Status
    is_anonymized = Column(Boolean, default=False, nullable=False)
    anonymized_at = Column(DateTime, nullable=True)
    deletion_requested_at = Column(DateTime, nullable=True)
    deletion_executed_at = Column(DateTime, nullable=True)

    # Metadados
    first_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSONB, default=dict)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relacionamentos
    consents = relationship("Consent", back_populates="data_subject")
    processing_records = relationship("DataProcessingRecord", back_populates="data_subject")
    dsar_requests = relationship("DSARRequest", back_populates="data_subject")

    __table_args__ = (
        Index("ix_data_subjects_email_hash", "email_hash"),
        Index("ix_data_subjects_type", "type"),
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return (
            f"<DataSubject(id={self.id}, "
            f"type='{self.type.value}', "
            f"anonymized={self.is_anonymized})>"
        )
```

```python
# modules/compliance/models/data_processing.py
"""
Model de registro de atividades de tratamento.

Conforme Art. 37 da LGPD - Registro de Operacoes.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class ProcessingOperation(str, Enum):
    """Tipos de operacao de tratamento."""

    COLETA = "coleta"
    PRODUCAO = "producao"
    RECEPCAO = "recepcao"
    CLASSIFICACAO = "classificacao"
    UTILIZACAO = "utilizacao"
    ACESSO = "acesso"
    REPRODUCAO = "reproducao"
    TRANSMISSAO = "transmissao"
    DISTRIBUICAO = "distribuicao"
    ARQUIVAMENTO = "arquivamento"
    ARMAZENAMENTO = "armazenamento"
    ELIMINACAO = "eliminacao"
    AVALIACAO = "avaliacao"
    CONTROLE = "controle"
    MODIFICACAO = "modificacao"
    COMUNICACAO = "comunicacao"
    TRANSFERENCIA = "transferencia"
    DIFUSAO = "difusao"
    EXTRACAO = "extracao"


class DataCategory(str, Enum):
    """Categorias de dados pessoais."""

    IDENTIFICACAO = "identificacao"
    CONTATO = "contato"
    FINANCEIRO = "financeiro"
    PROFISSIONAL = "profissional"
    BIOMETRICO = "biometrico"
    SAUDE = "saude"
    LOCALIZACAO = "localizacao"
    COMPORTAMENTAL = "comportamental"
    SENSIVEL = "sensivel"


class DataProcessingRecord(Base):
    """
    Registro de atividade de tratamento LGPD.

    Conforme Art. 37 - Obrigacao do controlador.

    Attributes:
        id: Identificador UUID
        name: Nome da atividade
        description: Descricao detalhada
        purpose: Finalidade
        legal_basis: Base legal
        data_categories: Categorias de dados
        operations: Operacoes realizadas
        retention_period_days: Periodo de retencao
    """

    __tablename__ = "lgpd_processing_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    data_subject_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lgpd_data_subjects.id"),
        nullable=True,
    )

    # Identificacao
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    department = Column(String(100), nullable=False)
    responsible_id = Column(UUID(as_uuid=True), nullable=False)

    # Tratamento
    purpose = Column(Text, nullable=False)
    legal_basis = Column(String(100), nullable=False)
    data_categories = Column(ARRAY(String), nullable=False)
    operations = Column(ARRAY(String), nullable=False)

    # Retencao
    retention_period_days = Column(Integer, nullable=False)
    retention_justification = Column(Text, nullable=True)

    # Compartilhamento
    shared_with = Column(JSONB, default=list)  # Lista de operadores/terceiros
    international_transfer = Column(Boolean, default=False)
    transfer_country = Column(String(100), nullable=True)
    transfer_safeguards = Column(Text, nullable=True)

    # Seguranca
    security_measures = Column(JSONB, default=list)
    dpia_required = Column(Boolean, default=False)
    dpia_id = Column(UUID(as_uuid=True), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    created_by = Column(UUID(as_uuid=True), nullable=False)

    # Relacionamentos
    data_subject = relationship("DataSubject", back_populates="processing_records")

    __table_args__ = (
        Index("ix_processing_records_department", "department"),
        Index("ix_processing_records_legal_basis", "legal_basis"),
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<DataProcessingRecord(id={self.id}, name='{self.name}')>"
```

### 2.2 Servico de Consentimento

```python
# modules/compliance/services/consent_service.py
"""
Servico de gestao de consentimentos LGPD.

Implementa coleta, validacao e revogacao de consentimentos.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
import hashlib

from sqlalchemy.orm import Session

from core.logging import logger
from modules.compliance.models.consent import (
    Consent,
    ConsentPurpose,
    ConsentStatus,
)
from modules.compliance.models.data_subject import DataSubject, DataSubjectType
from modules.compliance.repositories.consent_repository import ConsentRepository
from modules.compliance.schemas.consent_schemas import (
    ConsentCreate,
    ConsentResponse,
    ConsentValidation,
)


class ConsentService:
    """
    Servico de consentimentos.

    Gerencia ciclo de vida de consentimentos LGPD.
    """

    def __init__(self, db: Session) -> None:
        """
        Inicializa servico.

        Args:
            db: Sessao do banco
        """
        self.db = db
        self.repository = ConsentRepository(db)

    def grant_consent(
        self,
        cpf: str,
        email: str,
        purpose: ConsentPurpose,
        legal_basis: str,
        description: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        collection_point: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        subject_type: DataSubjectType = DataSubjectType.CLIENTE,
    ) -> Consent:
        """
        Registra consentimento do titular.

        Args:
            cpf: CPF do titular
            email: Email do titular
            purpose: Finalidade do tratamento
            legal_basis: Base legal aplicavel
            description: Descricao do tratamento
            ip_address: IP do dispositivo
            user_agent: User agent do navegador
            collection_point: Ponto de coleta (formulario, app, etc)
            expires_in_days: Dias ate expiracao
            subject_type: Tipo de titular

        Returns:
            Consentimento criado
        """
        # Obter ou criar titular
        data_subject = self._get_or_create_subject(cpf, email, subject_type)

        # Verificar se ja existe consentimento ativo para mesma finalidade
        existing = self.repository.get_active_by_subject_and_purpose(
            data_subject.id,
            purpose,
        )
        if existing:
            logger.info(
                "Consentimento ja existe para finalidade",
                subject_id=str(data_subject.id),
                purpose=purpose.value,
            )
            return existing

        # Calcular expiracao
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Criar consentimento
        consent = Consent(
            data_subject_id=data_subject.id,
            purpose=purpose,
            legal_basis=legal_basis,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            collection_point=collection_point,
            expires_at=expires_at,
        )

        self.db.add(consent)
        self.db.commit()
        self.db.refresh(consent)

        logger.info(
            "Consentimento registrado",
            consent_id=str(consent.id),
            purpose=purpose.value,
            subject_id=str(data_subject.id),
        )

        return consent

    def revoke_consent(
        self,
        consent_id: UUID,
        reason: Optional[str] = None,
        revoked_by: Optional[UUID] = None,
    ) -> Consent:
        """
        Revoga consentimento.

        Args:
            consent_id: ID do consentimento
            reason: Motivo da revogacao
            revoked_by: ID de quem revogou

        Returns:
            Consentimento atualizado

        Raises:
            ValueError: Se consentimento nao encontrado
        """
        consent = self.repository.get_by_id(consent_id)
        if not consent:
            raise ValueError(f"Consentimento {consent_id} nao encontrado")

        consent.revoke(reason)
        if revoked_by:
            consent.metadata["revoked_by"] = str(revoked_by)

        self.db.commit()
        self.db.refresh(consent)

        logger.info(
            "Consentimento revogado",
            consent_id=str(consent_id),
            reason=reason,
        )

        return consent

    def validate_consent(
        self,
        cpf: str,
        purpose: ConsentPurpose,
    ) -> ConsentValidation:
        """
        Valida se existe consentimento ativo.

        Args:
            cpf: CPF do titular
            purpose: Finalidade a validar

        Returns:
            Resultado da validacao
        """
        cpf_hash = self._hash_identifier(cpf)
        subject = self.db.query(DataSubject).filter(
            DataSubject.external_id == cpf_hash
        ).first()

        if not subject:
            return ConsentValidation(
                is_valid=False,
                reason="Titular nao encontrado",
            )

        consent = self.repository.get_active_by_subject_and_purpose(
            subject.id,
            purpose,
        )

        if not consent:
            return ConsentValidation(
                is_valid=False,
                reason="Consentimento nao encontrado para finalidade",
            )

        if not consent.is_valid():
            return ConsentValidation(
                is_valid=False,
                reason="Consentimento expirado ou revogado",
                consent_id=consent.id,
            )

        return ConsentValidation(
            is_valid=True,
            consent_id=consent.id,
            granted_at=consent.granted_at,
            expires_at=consent.expires_at,
        )

    def get_subject_consents(
        self,
        cpf: str,
    ) -> List[ConsentResponse]:
        """
        Lista consentimentos de um titular.

        Args:
            cpf: CPF do titular

        Returns:
            Lista de consentimentos
        """
        cpf_hash = self._hash_identifier(cpf)
        subject = self.db.query(DataSubject).filter(
            DataSubject.external_id == cpf_hash
        ).first()

        if not subject:
            return []

        consents = self.repository.get_all_by_subject(subject.id)
        return [ConsentResponse.from_orm(c) for c in consents]

    def _get_or_create_subject(
        self,
        cpf: str,
        email: str,
        subject_type: DataSubjectType,
    ) -> DataSubject:
        """
        Obtem ou cria titular de dados.

        Args:
            cpf: CPF do titular
            email: Email do titular
            subject_type: Tipo de titular

        Returns:
            Titular encontrado ou criado
        """
        cpf_hash = self._hash_identifier(cpf)
        email_hash = self._hash_identifier(email.lower())

        subject = self.db.query(DataSubject).filter(
            DataSubject.external_id == cpf_hash
        ).first()

        if not subject:
            subject = DataSubject(
                external_id=cpf_hash,
                type=subject_type,
                email_hash=email_hash,
            )
            self.db.add(subject)
            self.db.commit()
            self.db.refresh(subject)

            logger.info(
                "Titular criado",
                subject_id=str(subject.id),
                type=subject_type.value,
            )

        return subject

    def _hash_identifier(self, value: str) -> str:
        """
        Gera hash SHA256 de identificador.

        Args:
            value: Valor a hashar

        Returns:
            Hash em hexadecimal
        """
        # Remover caracteres nao numericos do CPF
        cleaned = "".join(c for c in value if c.isalnum())
        return hashlib.sha256(cleaned.encode()).hexdigest()
```

---

## 3. ISO 27001 - SEGURANCA DA INFORMACAO

### 3.1 Modelo de Controles

```python
# modules/compliance/models/compliance_control.py
"""
Model de controles de conformidade.

Implementa controles ISO 27001 e SOC 2.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class ControlFramework(str, Enum):
    """Frameworks de conformidade."""

    ISO_27001 = "iso_27001"
    SOC2 = "soc2"
    LGPD = "lgpd"
    PCI_DSS = "pci_dss"
    CUSTOM = "custom"


class ControlStatus(str, Enum):
    """Status de implementacao."""

    NAO_IMPLEMENTADO = "nao_implementado"
    PARCIALMENTE_IMPLEMENTADO = "parcialmente_implementado"
    IMPLEMENTADO = "implementado"
    NAO_APLICAVEL = "nao_aplicavel"


class ControlEffectiveness(str, Enum):
    """Efetividade do controle."""

    NAO_AVALIADO = "nao_avaliado"
    INEFICAZ = "ineficaz"
    PARCIALMENTE_EFICAZ = "parcialmente_eficaz"
    EFICAZ = "eficaz"
    ALTAMENTE_EFICAZ = "altamente_eficaz"


class ComplianceControl(Base):
    """
    Representa um controle de conformidade.

    Attributes:
        id: Identificador UUID
        framework: Framework de origem
        control_id: ID do controle no framework
        name: Nome do controle
        description: Descricao
        status: Status de implementacao
        effectiveness: Efetividade
    """

    __tablename__ = "compliance_controls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    framework = Column(SQLEnum(ControlFramework), nullable=False)
    control_id = Column(String(50), nullable=False)  # Ex: A.5.1.1, CC1.1
    category = Column(String(200), nullable=False)
    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)

    # Implementacao
    status = Column(
        SQLEnum(ControlStatus),
        default=ControlStatus.NAO_IMPLEMENTADO,
        nullable=False,
    )
    implementation_notes = Column(Text, nullable=True)
    evidence_location = Column(String(500), nullable=True)

    # Avaliacao
    effectiveness = Column(
        SQLEnum(ControlEffectiveness),
        default=ControlEffectiveness.NAO_AVALIADO,
        nullable=False,
    )
    last_assessment_date = Column(DateTime, nullable=True)
    next_assessment_date = Column(DateTime, nullable=True)
    assessment_frequency_days = Column(Integer, default=365)

    # Responsabilidade
    owner_id = Column(UUID(as_uuid=True), nullable=True)
    department = Column(String(100), nullable=True)

    # Risco associado
    risk_level = Column(Integer, default=1)  # 1-5
    compensating_controls = Column(JSONB, default=list)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relacionamentos
    assessments = relationship("ControlAssessment", back_populates="control")
    findings = relationship("AuditFinding", back_populates="control")

    __table_args__ = (
        Index("ix_controls_framework", "framework"),
        Index("ix_controls_status", "status"),
        Index("ix_controls_framework_control", "framework", "control_id", unique=True),
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return (
            f"<ComplianceControl(framework='{self.framework.value}', "
            f"control_id='{self.control_id}', "
            f"status='{self.status.value}')>"
        )
```

### 3.2 Avaliacao de Riscos

```python
# modules/compliance/models/risk_assessment.py
"""
Model de avaliacao de riscos.

Implementa gestao de riscos conforme ISO 27005.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class RiskCategory(str, Enum):
    """Categorias de risco."""

    SEGURANCA = "seguranca"
    PRIVACIDADE = "privacidade"
    OPERACIONAL = "operacional"
    FINANCEIRO = "financeiro"
    REPUTACIONAL = "reputacional"
    LEGAL = "legal"
    ESTRATEGICO = "estrategico"


class RiskStatus(str, Enum):
    """Status do risco."""

    IDENTIFICADO = "identificado"
    EM_ANALISE = "em_analise"
    TRATADO = "tratado"
    ACEITO = "aceito"
    TRANSFERIDO = "transferido"
    ELIMINADO = "eliminado"
    MONITORANDO = "monitorando"


class TreatmentType(str, Enum):
    """Tipos de tratamento de risco."""

    MITIGAR = "mitigar"
    TRANSFERIR = "transferir"
    ACEITAR = "aceitar"
    EVITAR = "evitar"


class RiskAssessment(Base):
    """
    Avaliacao de risco de seguranca.

    Attributes:
        id: Identificador UUID
        title: Titulo do risco
        description: Descricao detalhada
        category: Categoria
        probability: Probabilidade (1-5)
        impact: Impacto (1-5)
        inherent_risk: Risco inerente calculado
        residual_risk: Risco residual apos controles
    """

    __tablename__ = "risk_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(RiskCategory), nullable=False)
    status = Column(
        SQLEnum(RiskStatus),
        default=RiskStatus.IDENTIFICADO,
        nullable=False,
    )

    # Ativos afetados
    affected_assets = Column(JSONB, default=list)
    affected_processes = Column(JSONB, default=list)

    # Avaliacao
    probability = Column(Integer, nullable=False)  # 1-5
    impact = Column(Integer, nullable=False)  # 1-5
    inherent_risk = Column(Integer, nullable=False)  # probability * impact
    control_effectiveness = Column(Float, default=0.0)  # 0.0 - 1.0
    residual_risk = Column(Integer, nullable=False)

    # Tratamento
    treatment_type = Column(SQLEnum(TreatmentType), nullable=True)
    treatment_plan = Column(Text, nullable=True)
    treatment_deadline = Column(DateTime, nullable=True)
    treatment_cost = Column(Numeric(15, 2), nullable=True)

    # Responsabilidade
    risk_owner_id = Column(UUID(as_uuid=True), nullable=False)
    department = Column(String(100), nullable=False)

    # Aceitacao
    accepted_by_id = Column(UUID(as_uuid=True), nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    acceptance_justification = Column(Text, nullable=True)

    # Monitoramento
    review_frequency_days = Column(Integer, default=90)
    last_review_date = Column(DateTime, nullable=True)
    next_review_date = Column(DateTime, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    created_by = Column(UUID(as_uuid=True), nullable=False)

    __table_args__ = (
        Index("ix_risks_category", "category"),
        Index("ix_risks_status", "status"),
        Index("ix_risks_inherent", "inherent_risk"),
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return (
            f"<RiskAssessment(id={self.id}, "
            f"title='{self.title[:50]}', "
            f"inherent_risk={self.inherent_risk})>"
        )

    def calculate_residual_risk(self) -> int:
        """
        Calcula risco residual.

        Returns:
            Risco residual (1-25)
        """
        effectiveness_factor = 1 - self.control_effectiveness
        residual = int(self.inherent_risk * effectiveness_factor)
        return max(1, min(25, residual))

    @property
    def risk_level(self) -> str:
        """
        Retorna nivel de risco textual.

        Returns:
            Nivel (Baixo, Medio, Alto, Critico)
        """
        if self.residual_risk <= 4:
            return "Baixo"
        if self.residual_risk <= 9:
            return "Medio"
        if self.residual_risk <= 16:
            return "Alto"
        return "Critico"
```

### 3.3 Servico de Avaliacao de Riscos

```python
# modules/compliance/services/risk_service.py
"""
Servico de gestao de riscos.

Implementa identificacao, avaliacao e tratamento de riscos.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from core.logging import logger
from modules.compliance.models.risk_assessment import (
    RiskAssessment,
    RiskCategory,
    RiskStatus,
    TreatmentType,
)
from modules.compliance.schemas.risk_schemas import (
    RiskCreate,
    RiskDashboard,
    RiskMatrix,
    RiskResponse,
    RiskTreatment,
)


class RiskService:
    """
    Servico de gestao de riscos.

    Implementa ciclo completo de gestao de riscos.
    """

    # Matriz de risco (probabilidade x impacto)
    RISK_MATRIX: Dict[Tuple[int, int], str] = {
        (1, 1): "Baixo", (1, 2): "Baixo", (1, 3): "Medio",
        (1, 4): "Medio", (1, 5): "Alto",
        (2, 1): "Baixo", (2, 2): "Baixo", (2, 3): "Medio",
        (2, 4): "Alto", (2, 5): "Alto",
        (3, 1): "Baixo", (3, 2): "Medio", (3, 3): "Medio",
        (3, 4): "Alto", (3, 5): "Critico",
        (4, 1): "Medio", (4, 2): "Medio", (4, 3): "Alto",
        (4, 4): "Alto", (4, 5): "Critico",
        (5, 1): "Medio", (5, 2): "Alto", (5, 3): "Alto",
        (5, 4): "Critico", (5, 5): "Critico",
    }

    def __init__(self, db: Session) -> None:
        """
        Inicializa servico.

        Args:
            db: Sessao do banco
        """
        self.db = db

    def create_risk(
        self,
        data: RiskCreate,
        created_by: UUID,
    ) -> RiskAssessment:
        """
        Cria nova avaliacao de risco.

        Args:
            data: Dados do risco
            created_by: ID do criador

        Returns:
            Risco criado
        """
        # Calcular risco inerente
        inherent_risk = data.probability * data.impact

        # Calcular risco residual inicial (sem controles)
        residual_risk = inherent_risk

        risk = RiskAssessment(
            title=data.title,
            description=data.description,
            category=data.category,
            affected_assets=data.affected_assets,
            affected_processes=data.affected_processes,
            probability=data.probability,
            impact=data.impact,
            inherent_risk=inherent_risk,
            residual_risk=residual_risk,
            risk_owner_id=data.risk_owner_id,
            department=data.department,
            review_frequency_days=data.review_frequency_days or 90,
            next_review_date=datetime.utcnow() + timedelta(days=90),
            created_by=created_by,
        )

        self.db.add(risk)
        self.db.commit()
        self.db.refresh(risk)

        logger.info(
            "Risco criado",
            risk_id=str(risk.id),
            title=risk.title,
            inherent_risk=inherent_risk,
        )

        return risk

    def apply_treatment(
        self,
        risk_id: UUID,
        treatment: RiskTreatment,
        applied_by: UUID,
    ) -> RiskAssessment:
        """
        Aplica tratamento ao risco.

        Args:
            risk_id: ID do risco
            treatment: Dados do tratamento
            applied_by: ID de quem aplicou

        Returns:
            Risco atualizado

        Raises:
            ValueError: Se risco nao encontrado
        """
        risk = self.db.query(RiskAssessment).filter(
            RiskAssessment.id == risk_id
        ).first()

        if not risk:
            raise ValueError(f"Risco {risk_id} nao encontrado")

        risk.treatment_type = treatment.treatment_type
        risk.treatment_plan = treatment.treatment_plan
        risk.treatment_deadline = treatment.deadline
        risk.treatment_cost = treatment.cost
        risk.control_effectiveness = treatment.expected_effectiveness
        risk.status = RiskStatus.TRATADO

        # Recalcular risco residual
        risk.residual_risk = risk.calculate_residual_risk()

        self.db.commit()
        self.db.refresh(risk)

        logger.info(
            "Tratamento aplicado",
            risk_id=str(risk_id),
            treatment=treatment.treatment_type.value,
            residual_risk=risk.residual_risk,
        )

        return risk

    def accept_risk(
        self,
        risk_id: UUID,
        accepted_by: UUID,
        justification: str,
    ) -> RiskAssessment:
        """
        Aceita risco residual.

        Args:
            risk_id: ID do risco
            accepted_by: ID de quem aceitou
            justification: Justificativa

        Returns:
            Risco atualizado

        Raises:
            ValueError: Se risco nao encontrado ou nivel alto
        """
        risk = self.db.query(RiskAssessment).filter(
            RiskAssessment.id == risk_id
        ).first()

        if not risk:
            raise ValueError(f"Risco {risk_id} nao encontrado")

        # Validar nivel do risco
        if risk.residual_risk > 16:
            raise ValueError(
                "Riscos criticos nao podem ser aceitos. "
                "Aplique tratamento adicional."
            )

        risk.status = RiskStatus.ACEITO
        risk.accepted_by_id = accepted_by
        risk.accepted_at = datetime.utcnow()
        risk.acceptance_justification = justification

        self.db.commit()
        self.db.refresh(risk)

        logger.info(
            "Risco aceito",
            risk_id=str(risk_id),
            accepted_by=str(accepted_by),
        )

        return risk

    def get_risk_matrix(self) -> RiskMatrix:
        """
        Gera matriz de riscos.

        Returns:
            Matriz de riscos com distribuicao
        """
        risks = self.db.query(RiskAssessment).filter(
            RiskAssessment.status.notin_([
                RiskStatus.ELIMINADO,
            ])
        ).all()

        matrix = {}
        for prob in range(1, 6):
            for imp in range(1, 6):
                matrix[(prob, imp)] = []

        for risk in risks:
            key = (risk.probability, risk.impact)
            matrix[key].append({
                "id": str(risk.id),
                "title": risk.title,
                "residual_risk": risk.residual_risk,
            })

        return RiskMatrix(
            matrix=matrix,
            total_risks=len(risks),
            by_level={
                "baixo": sum(1 for r in risks if r.residual_risk <= 4),
                "medio": sum(1 for r in risks if 4 < r.residual_risk <= 9),
                "alto": sum(1 for r in risks if 9 < r.residual_risk <= 16),
                "critico": sum(1 for r in risks if r.residual_risk > 16),
            },
        )

    def get_dashboard(self) -> RiskDashboard:
        """
        Gera dashboard de riscos.

        Returns:
            Metricas de riscos
        """
        risks = self.db.query(RiskAssessment).all()

        by_category = self.db.query(
            RiskAssessment.category,
            func.count(RiskAssessment.id),
        ).group_by(RiskAssessment.category).all()

        by_status = self.db.query(
            RiskAssessment.status,
            func.count(RiskAssessment.id),
        ).group_by(RiskAssessment.status).all()

        overdue = self.db.query(RiskAssessment).filter(
            and_(
                RiskAssessment.treatment_deadline < datetime.utcnow(),
                RiskAssessment.status == RiskStatus.TRATADO,
            )
        ).count()

        pending_review = self.db.query(RiskAssessment).filter(
            RiskAssessment.next_review_date < datetime.utcnow()
        ).count()

        return RiskDashboard(
            total_risks=len(risks),
            critical_risks=sum(1 for r in risks if r.residual_risk > 16),
            high_risks=sum(1 for r in risks if 9 < r.residual_risk <= 16),
            medium_risks=sum(1 for r in risks if 4 < r.residual_risk <= 9),
            low_risks=sum(1 for r in risks if r.residual_risk <= 4),
            by_category={cat.value: count for cat, count in by_category},
            by_status={status.value: count for status, count in by_status},
            overdue_treatments=overdue,
            pending_reviews=pending_review,
            average_residual_risk=(
                sum(r.residual_risk for r in risks) / len(risks)
                if risks else 0
            ),
        )
```

---

## 4. SOC 2 - SERVICE ORGANIZATION CONTROL

### 4.1 Trust Service Criteria

```python
# modules/compliance/services/soc2_service.py
"""
Servico de conformidade SOC 2.

Implementa Trust Service Criteria (TSC).
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from core.logging import logger
from modules.compliance.models.compliance_control import (
    ComplianceControl,
    ControlEffectiveness,
    ControlFramework,
    ControlStatus,
)


class SOC2Service:
    """
    Servico de conformidade SOC 2.

    Gerencia controles dos Trust Service Criteria.
    """

    # Trust Service Criteria Categories
    TSC_CATEGORIES = {
        "CC": "Common Criteria",
        "A": "Availability",
        "PI": "Processing Integrity",
        "C": "Confidentiality",
        "P": "Privacy",
    }

    # Controles principais por categoria
    CONTROLS = {
        # Common Criteria - Control Environment
        "CC1.1": {
            "name": "COSO Principle 1 - Integrity and Ethical Values",
            "description": (
                "The entity demonstrates a commitment to integrity "
                "and ethical values."
            ),
            "category": "CC",
        },
        "CC1.2": {
            "name": "COSO Principle 2 - Board Independence",
            "description": (
                "The board of directors demonstrates independence from "
                "management and exercises oversight."
            ),
            "category": "CC",
        },
        # ... mais controles CC

        # Availability
        "A1.1": {
            "name": "Capacity Management",
            "description": (
                "Current processing capacity and usage are maintained, "
                "monitored, and evaluated."
            ),
            "category": "A",
        },
        "A1.2": {
            "name": "Environmental Controls",
            "description": (
                "Environmental protections, software, data backup, "
                "and recovery infrastructure are designed and implemented."
            ),
            "category": "A",
        },

        # Confidentiality
        "C1.1": {
            "name": "Confidential Information Identification",
            "description": (
                "Confidential information is identified and protected "
                "during collection, processing, and storage."
            ),
            "category": "C",
        },
        "C1.2": {
            "name": "Confidential Information Disposal",
            "description": (
                "Confidential information is disposed of "
                "in accordance with policy."
            ),
            "category": "C",
        },

        # Privacy
        "P1.1": {
            "name": "Privacy Notice",
            "description": (
                "The entity provides notice to data subjects about "
                "its privacy practices."
            ),
            "category": "P",
        },
        "P2.1": {
            "name": "Consent",
            "description": (
                "The entity communicates choices available regarding "
                "collection, use, and disclosure of personal information."
            ),
            "category": "P",
        },
    }

    def __init__(self, db: Session) -> None:
        """
        Inicializa servico.

        Args:
            db: Sessao do banco
        """
        self.db = db

    def initialize_controls(self) -> List[ComplianceControl]:
        """
        Inicializa controles SOC 2.

        Returns:
            Lista de controles criados
        """
        created = []

        for control_id, details in self.CONTROLS.items():
            existing = self.db.query(ComplianceControl).filter(
                ComplianceControl.framework == ControlFramework.SOC2,
                ComplianceControl.control_id == control_id,
            ).first()

            if not existing:
                control = ComplianceControl(
                    framework=ControlFramework.SOC2,
                    control_id=control_id,
                    category=self.TSC_CATEGORIES[details["category"]],
                    name=details["name"],
                    description=details["description"],
                )
                self.db.add(control)
                created.append(control)

        self.db.commit()

        logger.info(
            "Controles SOC 2 inicializados",
            created=len(created),
        )

        return created

    def get_compliance_status(self) -> Dict:
        """
        Retorna status de conformidade SOC 2.

        Returns:
            Status por categoria e geral
        """
        controls = self.db.query(ComplianceControl).filter(
            ComplianceControl.framework == ControlFramework.SOC2
        ).all()

        by_category = {}
        for cat_code, cat_name in self.TSC_CATEGORIES.items():
            cat_controls = [
                c for c in controls
                if c.control_id.startswith(cat_code)
            ]
            if cat_controls:
                implemented = sum(
                    1 for c in cat_controls
                    if c.status == ControlStatus.IMPLEMENTADO
                )
                by_category[cat_name] = {
                    "total": len(cat_controls),
                    "implemented": implemented,
                    "percentage": round(
                        implemented / len(cat_controls) * 100, 1
                    ),
                }

        total = len(controls)
        implemented = sum(
            1 for c in controls
            if c.status == ControlStatus.IMPLEMENTADO
        )

        return {
            "framework": "SOC 2 Type II",
            "overall_compliance": round(implemented / total * 100, 1) if total else 0,
            "total_controls": total,
            "implemented_controls": implemented,
            "by_category": by_category,
            "last_assessment": self._get_last_assessment_date(),
            "next_audit": self._get_next_audit_date(),
        }

    def assess_control(
        self,
        control_id: str,
        effectiveness: ControlEffectiveness,
        evidence: str,
        assessed_by: UUID,
        notes: Optional[str] = None,
    ) -> ComplianceControl:
        """
        Avalia efetividade de controle.

        Args:
            control_id: ID do controle
            effectiveness: Nivel de efetividade
            evidence: Localizacao das evidencias
            assessed_by: ID do avaliador
            notes: Notas adicionais

        Returns:
            Controle atualizado

        Raises:
            ValueError: Se controle nao encontrado
        """
        control = self.db.query(ComplianceControl).filter(
            ComplianceControl.framework == ControlFramework.SOC2,
            ComplianceControl.control_id == control_id,
        ).first()

        if not control:
            raise ValueError(f"Controle SOC 2 {control_id} nao encontrado")

        control.effectiveness = effectiveness
        control.evidence_location = evidence
        control.last_assessment_date = datetime.utcnow()
        control.next_assessment_date = (
            datetime.utcnow() +
            timedelta(days=control.assessment_frequency_days)
        )

        if notes:
            control.implementation_notes = notes

        # Atualizar status baseado na efetividade
        if effectiveness in [
            ControlEffectiveness.EFICAZ,
            ControlEffectiveness.ALTAMENTE_EFICAZ,
        ]:
            control.status = ControlStatus.IMPLEMENTADO
        elif effectiveness == ControlEffectiveness.PARCIALMENTE_EFICAZ:
            control.status = ControlStatus.PARCIALMENTE_IMPLEMENTADO
        else:
            control.status = ControlStatus.NAO_IMPLEMENTADO

        self.db.commit()
        self.db.refresh(control)

        logger.info(
            "Controle SOC 2 avaliado",
            control_id=control_id,
            effectiveness=effectiveness.value,
        )

        return control

    def _get_last_assessment_date(self) -> Optional[datetime]:
        """Retorna data da ultima avaliacao."""
        result = self.db.query(
            func.max(ComplianceControl.last_assessment_date)
        ).filter(
            ComplianceControl.framework == ControlFramework.SOC2
        ).scalar()
        return result

    def _get_next_audit_date(self) -> Optional[datetime]:
        """Retorna data do proximo audit."""
        # Logica de calculo baseada no ciclo de auditoria
        last = self._get_last_assessment_date()
        if last:
            return last + timedelta(days=365)
        return None
```

---

## 5. TRILHA DE AUDITORIA

### 5.1 Model de Audit Log

```python
# modules/compliance/models/audit_log.py
"""
Model de log de auditoria.

Registra todas as acoes do sistema de forma imutavel.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID

from core.database import Base


class AuditAction(str, Enum):
    """Tipos de acao auditada."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_CHANGE = "permission_change"
    EXPORT = "export"
    IMPORT = "import"
    PRINT = "print"
    CONSENT_GRANTED = "consent_granted"
    CONSENT_REVOKED = "consent_revoked"
    DATA_ACCESS = "data_access"
    ANONYMIZE = "anonymize"
    PURGE = "purge"


class AuditSeverity(str, Enum):
    """Severidade do evento."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(Base):
    """
    Registro de auditoria imutavel.

    Attributes:
        id: Identificador UUID
        timestamp: Data/hora do evento
        action: Tipo de acao
        entity_type: Tipo de entidade
        entity_id: ID da entidade
        user_id: ID do usuario
        changes: Alteracoes realizadas (before/after)
        ip_address: IP do cliente
    """

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Acao
    action = Column(SQLEnum(AuditAction), nullable=False)
    severity = Column(
        SQLEnum(AuditSeverity),
        default=AuditSeverity.INFO,
        nullable=False,
    )

    # Entidade
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)

    # Usuario
    user_id = Column(UUID(as_uuid=True), nullable=True)
    user_email = Column(String(255), nullable=True)
    user_role = Column(String(50), nullable=True)

    # Detalhes
    description = Column(Text, nullable=True)
    changes = Column(JSONB, nullable=True)  # {"before": {...}, "after": {...}}
    metadata = Column(JSONB, default=dict)

    # Contexto
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(100), nullable=True)
    session_id = Column(String(100), nullable=True)

    # Origem
    service_name = Column(String(100), default="erp-conecta-mais")
    endpoint = Column(String(500), nullable=True)
    http_method = Column(String(10), nullable=True)

    __table_args__ = (
        Index("ix_audit_timestamp", "timestamp"),
        Index("ix_audit_action", "action"),
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_user", "user_id"),
        Index("ix_audit_severity", "severity"),
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return (
            f"<AuditLog(id={self.id}, "
            f"action='{self.action.value}', "
            f"entity='{self.entity_type}')>"
        )
```

### 5.2 Servico de Auditoria

```python
# modules/compliance/services/audit_service.py
"""
Servico de auditoria.

Registra e consulta logs de auditoria.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID
import json

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from core.logging import logger
from modules.compliance.models.audit_log import (
    AuditAction,
    AuditLog,
    AuditSeverity,
)
from modules.compliance.schemas.audit_schemas import (
    AuditLogCreate,
    AuditLogResponse,
    AuditSearch,
    AuditStatistics,
)


class AuditService:
    """
    Servico de auditoria.

    Registra todas as acoes de forma imutavel.
    """

    def __init__(self, db: Session) -> None:
        """
        Inicializa servico.

        Args:
            db: Sessao do banco
        """
        self.db = db

    def log(
        self,
        action: AuditAction,
        entity_type: str,
        entity_id: Optional[str] = None,
        user_id: Optional[UUID] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        description: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Registra evento de auditoria.

        Args:
            action: Tipo de acao
            entity_type: Tipo de entidade
            entity_id: ID da entidade
            user_id: ID do usuario
            user_email: Email do usuario
            user_role: Role do usuario
            description: Descricao do evento
            changes: Alteracoes (before/after)
            ip_address: IP do cliente
            user_agent: User agent
            request_id: ID da requisicao
            session_id: ID da sessao
            endpoint: Endpoint acessado
            http_method: Metodo HTTP
            severity: Severidade
            metadata: Metadados adicionais

        Returns:
            Log criado
        """
        log_entry = AuditLog(
            action=action,
            severity=severity,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            description=description,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            session_id=session_id,
            endpoint=endpoint,
            http_method=http_method,
            metadata=metadata or {},
        )

        self.db.add(log_entry)
        self.db.commit()

        # Log em arquivo tambem
        logger.info(
            "Audit log",
            action=action.value,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=str(user_id) if user_id else None,
            severity=severity.value,
        )

        return log_entry

    def log_data_change(
        self,
        entity_type: str,
        entity_id: str,
        before: Optional[Dict[str, Any]],
        after: Optional[Dict[str, Any]],
        user_id: UUID,
        user_email: str,
        **kwargs,
    ) -> AuditLog:
        """
        Registra alteracao de dados com diff.

        Args:
            entity_type: Tipo de entidade
            entity_id: ID da entidade
            before: Estado anterior
            after: Estado posterior
            user_id: ID do usuario
            user_email: Email do usuario
            **kwargs: Argumentos adicionais

        Returns:
            Log criado
        """
        # Determinar acao
        if before is None and after is not None:
            action = AuditAction.CREATE
        elif before is not None and after is None:
            action = AuditAction.DELETE
        else:
            action = AuditAction.UPDATE

        # Calcular diff se for update
        changes = None
        if action == AuditAction.UPDATE and before and after:
            changes = self._calculate_diff(before, after)

        elif action == AuditAction.CREATE:
            changes = {"after": self._sanitize_data(after)}

        elif action == AuditAction.DELETE:
            changes = {"before": self._sanitize_data(before)}

        return self.log(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            user_email=user_email,
            changes=changes,
            **kwargs,
        )

    def search(
        self,
        search: AuditSearch,
    ) -> tuple[List[AuditLog], int]:
        """
        Busca logs de auditoria.

        Args:
            search: Criterios de busca

        Returns:
            Tuple (logs, total)
        """
        query = self.db.query(AuditLog)

        # Filtros
        if search.action:
            query = query.filter(AuditLog.action == search.action)

        if search.entity_type:
            query = query.filter(AuditLog.entity_type == search.entity_type)

        if search.entity_id:
            query = query.filter(AuditLog.entity_id == search.entity_id)

        if search.user_id:
            query = query.filter(AuditLog.user_id == search.user_id)

        if search.severity:
            query = query.filter(AuditLog.severity == search.severity)

        if search.start_date:
            query = query.filter(AuditLog.timestamp >= search.start_date)

        if search.end_date:
            query = query.filter(AuditLog.timestamp <= search.end_date)

        if search.ip_address:
            query = query.filter(AuditLog.ip_address == search.ip_address)

        # Total
        total = query.count()

        # Ordenacao e paginacao
        query = query.order_by(desc(AuditLog.timestamp))
        query = query.offset(search.skip).limit(search.limit)

        return query.all(), total

    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> AuditStatistics:
        """
        Gera estatisticas de auditoria.

        Args:
            start_date: Data inicial
            end_date: Data final

        Returns:
            Estatisticas
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        base_query = self.db.query(AuditLog).filter(
            and_(
                AuditLog.timestamp >= start_date,
                AuditLog.timestamp <= end_date,
            )
        )

        # Total de eventos
        total_events = base_query.count()

        # Por acao
        by_action = dict(
            self.db.query(
                AuditLog.action,
                func.count(AuditLog.id),
            ).filter(
                and_(
                    AuditLog.timestamp >= start_date,
                    AuditLog.timestamp <= end_date,
                )
            ).group_by(AuditLog.action).all()
        )

        # Por severidade
        by_severity = dict(
            self.db.query(
                AuditLog.severity,
                func.count(AuditLog.id),
            ).filter(
                and_(
                    AuditLog.timestamp >= start_date,
                    AuditLog.timestamp <= end_date,
                )
            ).group_by(AuditLog.severity).all()
        )

        # Por entidade
        by_entity = dict(
            self.db.query(
                AuditLog.entity_type,
                func.count(AuditLog.id),
            ).filter(
                and_(
                    AuditLog.timestamp >= start_date,
                    AuditLog.timestamp <= end_date,
                )
            ).group_by(AuditLog.entity_type).all()
        )

        # Top usuarios
        top_users = self.db.query(
            AuditLog.user_email,
            func.count(AuditLog.id).label("count"),
        ).filter(
            and_(
                AuditLog.timestamp >= start_date,
                AuditLog.timestamp <= end_date,
                AuditLog.user_email.isnot(None),
            )
        ).group_by(AuditLog.user_email).order_by(
            desc("count")
        ).limit(10).all()

        # Eventos criticos
        critical_events = base_query.filter(
            AuditLog.severity == AuditSeverity.CRITICAL
        ).count()

        return AuditStatistics(
            period_start=start_date,
            period_end=end_date,
            total_events=total_events,
            by_action={a.value: c for a, c in by_action.items()},
            by_severity={s.value: c for s, c in by_severity.items()},
            by_entity=dict(by_entity),
            top_users=[{"email": e, "count": c} for e, c in top_users],
            critical_events=critical_events,
            events_per_day=total_events / max(1, (end_date - start_date).days),
        )

    def _calculate_diff(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calcula diferenca entre estados.

        Args:
            before: Estado anterior
            after: Estado posterior

        Returns:
            Diff com campos alterados
        """
        before_clean = self._sanitize_data(before)
        after_clean = self._sanitize_data(after)

        changes = {"before": {}, "after": {}}

        all_keys = set(before_clean.keys()) | set(after_clean.keys())

        for key in all_keys:
            old_value = before_clean.get(key)
            new_value = after_clean.get(key)

            if old_value != new_value:
                changes["before"][key] = old_value
                changes["after"][key] = new_value

        return changes

    def _sanitize_data(
        self,
        data: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Remove dados sensiveis do log.

        Args:
            data: Dados a sanitizar

        Returns:
            Dados sanitizados
        """
        if not data:
            return {}

        sensitive_fields = {
            "password",
            "senha",
            "token",
            "secret",
            "api_key",
            "credit_card",
            "cpf",
            "cnpj",
        }

        sanitized = {}
        for key, value in data.items():
            if any(sf in key.lower() for sf in sensitive_fields):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            else:
                sanitized[key] = value

        return sanitized
```

---

## 6. GESTAO DE CONSENTIMENTO

### 6.1 Controller de Consentimento

```python
# modules/compliance/controllers/consent_controller.py
"""
Controller de consentimentos LGPD.

Endpoints para gestao de consentimentos.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.compliance.models.consent import ConsentPurpose
from modules.compliance.schemas.consent_schemas import (
    ConsentCreate,
    ConsentList,
    ConsentResponse,
    ConsentValidation,
)
from modules.compliance.services.consent_service import ConsentService

router = APIRouter(prefix="/lgpd/consents", tags=["LGPD - Consentimentos"])


@router.post("/", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
async def grant_consent(
    data: ConsentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> ConsentResponse:
    """
    Registra consentimento do titular.

    Args:
        data: Dados do consentimento
        request: Request HTTP
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Consentimento criado
    """
    service = ConsentService(db)

    consent = service.grant_consent(
        cpf=data.cpf,
        email=data.email,
        purpose=data.purpose,
        legal_basis=data.legal_basis,
        description=data.description,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        collection_point=data.collection_point,
        expires_in_days=data.expires_in_days,
        subject_type=data.subject_type,
    )

    return ConsentResponse.from_orm(consent)


@router.post("/{consent_id}/revoke", response_model=ConsentResponse)
async def revoke_consent(
    consent_id: UUID,
    reason: str = Query(None, description="Motivo da revogacao"),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),
) -> ConsentResponse:
    """
    Revoga consentimento.

    Args:
        consent_id: ID do consentimento
        reason: Motivo da revogacao
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Consentimento revogado

    Raises:
        HTTPException: Se consentimento nao encontrado
    """
    service = ConsentService(db)

    try:
        consent = service.revoke_consent(
            consent_id=consent_id,
            reason=reason,
            revoked_by=current_user.id,
        )
        return ConsentResponse.from_orm(consent)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/validate", response_model=ConsentValidation)
async def validate_consent(
    cpf: str = Query(..., description="CPF do titular"),
    purpose: ConsentPurpose = Query(..., description="Finalidade"),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> ConsentValidation:
    """
    Valida consentimento para finalidade.

    Args:
        cpf: CPF do titular
        purpose: Finalidade a validar
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Resultado da validacao
    """
    service = ConsentService(db)
    return service.validate_consent(cpf, purpose)


@router.get("/subject/{cpf}", response_model=List[ConsentResponse])
async def list_subject_consents(
    cpf: str,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> List[ConsentResponse]:
    """
    Lista consentimentos de um titular.

    Args:
        cpf: CPF do titular
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Lista de consentimentos
    """
    service = ConsentService(db)
    return service.get_subject_consents(cpf)
```

---

## 7. ANONIMIZACAO E PSEUDONIMIZACAO

### 7.1 Servico de Anonimizacao

```python
# modules/compliance/services/anonymization_service.py
"""
Servico de anonimizacao LGPD.

Implementa anonimizacao e pseudonimizacao de dados.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from uuid import UUID
import hashlib
import secrets

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from core.database import Base
from core.logging import logger
from modules.compliance.models.data_subject import DataSubject


class AnonymizationService:
    """
    Servico de anonimizacao de dados.

    Implementa tecnicas de anonimizacao e pseudonimizacao.
    """

    # Campos a anonimizar por tipo
    ANONYMIZATION_RULES = {
        "nome": lambda _: "***ANONIMIZADO***",
        "email": lambda v: f"anon_{hashlib.md5(v.encode()).hexdigest()[:8]}@anonimizado.com",
        "telefone": lambda _: "(**) *****-****",
        "cpf": lambda _: "***.***.***-**",
        "cnpj": lambda _: "**.***.***/****.−**",
        "endereco": lambda _: "Endereco anonimizado",
        "cep": lambda _: "*****-***",
        "data_nascimento": lambda _: None,
        "rg": lambda _: "*******-*",
        "foto": lambda _: None,
        "ip_address": lambda _: "0.0.0.0",
        "biometric_data": lambda _: None,
    }

    def __init__(self, db: Session) -> None:
        """
        Inicializa servico.

        Args:
            db: Sessao do banco
        """
        self.db = db

    def anonymize_subject(
        self,
        subject_id: UUID,
        reason: str,
        executed_by: UUID,
    ) -> DataSubject:
        """
        Anonimiza todos os dados de um titular.

        Args:
            subject_id: ID do titular
            reason: Motivo da anonimizacao
            executed_by: ID de quem executou

        Returns:
            Titular atualizado

        Raises:
            ValueError: Se titular nao encontrado
        """
        subject = self.db.query(DataSubject).filter(
            DataSubject.id == subject_id
        ).first()

        if not subject:
            raise ValueError(f"Titular {subject_id} nao encontrado")

        if subject.is_anonymized:
            logger.warning(
                "Titular ja anonimizado",
                subject_id=str(subject_id),
            )
            return subject

        # Anonimizar em todas as tabelas relacionadas
        self._anonymize_collaborators(subject.external_id)
        self._anonymize_clients(subject.external_id)
        self._anonymize_leads(subject.external_id)

        # Marcar titular como anonimizado
        subject.is_anonymized = True
        subject.anonymized_at = datetime.utcnow()
        subject.metadata["anonymization_reason"] = reason
        subject.metadata["anonymized_by"] = str(executed_by)

        self.db.commit()
        self.db.refresh(subject)

        logger.info(
            "Titular anonimizado",
            subject_id=str(subject_id),
            reason=reason,
        )

        return subject

    def pseudonymize_field(
        self,
        value: str,
        salt: Optional[str] = None,
    ) -> str:
        """
        Pseudonimiza valor mantendo consistencia.

        Args:
            value: Valor original
            salt: Salt para hash

        Returns:
            Valor pseudonimizado
        """
        if not salt:
            salt = secrets.token_hex(16)

        combined = f"{value}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def anonymize_record(
        self,
        record: Base,
        fields_to_anonymize: List[str],
    ) -> Base:
        """
        Anonimiza campos especificos de um registro.

        Args:
            record: Registro a anonimizar
            fields_to_anonymize: Lista de campos

        Returns:
            Registro anonimizado
        """
        for field in fields_to_anonymize:
            if hasattr(record, field):
                current_value = getattr(record, field)
                if current_value is not None:
                    # Encontrar regra de anonimizacao
                    rule = self._find_anonymization_rule(field)
                    anonymized = rule(current_value)
                    setattr(record, field, anonymized)

        return record

    def bulk_anonymize(
        self,
        model_class: Type[Base],
        record_ids: List[UUID],
        fields: List[str],
    ) -> int:
        """
        Anonimiza multiplos registros.

        Args:
            model_class: Classe do model
            record_ids: IDs dos registros
            fields: Campos a anonimizar

        Returns:
            Quantidade de registros anonimizados
        """
        records = self.db.query(model_class).filter(
            model_class.id.in_(record_ids)
        ).all()

        for record in records:
            self.anonymize_record(record, fields)

        self.db.commit()

        logger.info(
            "Bulk anonymization completed",
            model=model_class.__tablename__,
            count=len(records),
        )

        return len(records)

    def _find_anonymization_rule(self, field_name: str) -> callable:
        """
        Encontra regra de anonimizacao para campo.

        Args:
            field_name: Nome do campo

        Returns:
            Funcao de anonimizacao
        """
        field_lower = field_name.lower()

        for key, rule in self.ANONYMIZATION_RULES.items():
            if key in field_lower:
                return rule

        # Regra padrao: substituir por string generica
        return lambda _: "***"

    def _anonymize_collaborators(self, external_id: str) -> int:
        """Anonimiza dados de colaboradores."""
        # Implementar anonimizacao especifica
        return 0

    def _anonymize_clients(self, external_id: str) -> int:
        """Anonimiza dados de clientes."""
        # Implementar anonimizacao especifica
        return 0

    def _anonymize_leads(self, external_id: str) -> int:
        """Anonimiza dados de leads."""
        # Implementar anonimizacao especifica
        return 0
```

---

## 8. RETENCAO DE DADOS

### 8.1 Servico de Retencao

```python
# modules/compliance/services/retention_service.py
"""
Servico de retencao de dados.

Implementa politicas de retencao e eliminacao automatica.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Type
from uuid import UUID

from sqlalchemy import and_, delete
from sqlalchemy.orm import Session

from core.database import Base
from core.logging import logger
from modules.compliance.models.retention_policy import (
    RetentionPolicy,
    RetentionStatus,
)


class RetentionService:
    """
    Servico de retencao de dados.

    Gerencia ciclo de vida de dados conforme politicas.
    """

    # Politicas padrao por tipo de dado
    DEFAULT_POLICIES = {
        "audit_logs": {
            "retention_days": 365 * 5,  # 5 anos
            "legal_basis": "Obrigacao Legal - Audit Trail",
            "can_delete": False,
        },
        "financial_records": {
            "retention_days": 365 * 10,  # 10 anos
            "legal_basis": "Obrigacao Legal - Registros Fiscais",
            "can_delete": False,
        },
        "employment_records": {
            "retention_days": 365 * 30,  # 30 anos
            "legal_basis": "Obrigacao Legal - CLT",
            "can_delete": False,
        },
        "leads": {
            "retention_days": 365 * 2,  # 2 anos
            "legal_basis": "Interesse Legitimo",
            "can_delete": True,
        },
        "session_logs": {
            "retention_days": 90,  # 90 dias
            "legal_basis": "Seguranca",
            "can_delete": True,
        },
        "temp_files": {
            "retention_days": 7,  # 7 dias
            "legal_basis": "Operacional",
            "can_delete": True,
        },
    }

    def __init__(self, db: Session) -> None:
        """
        Inicializa servico.

        Args:
            db: Sessao do banco
        """
        self.db = db

    def execute_retention_policies(self) -> Dict[str, int]:
        """
        Executa todas as politicas de retencao.

        Returns:
            Dicionario com contagem de registros processados
        """
        results = {}

        policies = self.db.query(RetentionPolicy).filter(
            RetentionPolicy.is_active == True,
            RetentionPolicy.can_auto_delete == True,
        ).all()

        for policy in policies:
            try:
                count = self._execute_policy(policy)
                results[policy.entity_type] = count

                # Atualizar ultima execucao
                policy.last_execution = datetime.utcnow()
                policy.next_execution = (
                    datetime.utcnow() +
                    timedelta(days=policy.execution_frequency_days)
                )

                logger.info(
                    "Politica de retencao executada",
                    entity=policy.entity_type,
                    deleted=count,
                )

            except Exception as e:
                logger.error(
                    "Erro ao executar politica",
                    entity=policy.entity_type,
                    error=str(e),
                )
                results[policy.entity_type] = -1

        self.db.commit()
        return results

    def _execute_policy(self, policy: RetentionPolicy) -> int:
        """
        Executa uma politica especifica.

        Args:
            policy: Politica a executar

        Returns:
            Quantidade de registros deletados
        """
        cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_days)

        # Mapear entity_type para model
        model_class = self._get_model_class(policy.entity_type)
        if not model_class:
            logger.warning(
                "Model nao encontrado para politica",
                entity=policy.entity_type,
            )
            return 0

        # Encontrar campo de data
        date_field = getattr(model_class, policy.date_field, None)
        if not date_field:
            date_field = getattr(model_class, "created_at", None)

        if not date_field:
            logger.warning(
                "Campo de data nao encontrado",
                entity=policy.entity_type,
            )
            return 0

        # Deletar registros expirados
        if policy.delete_method == "hard":
            result = self.db.execute(
                delete(model_class).where(date_field < cutoff_date)
            )
            count = result.rowcount
        else:
            # Soft delete
            records = self.db.query(model_class).filter(
                date_field < cutoff_date
            ).all()

            for record in records:
                if hasattr(record, "is_deleted"):
                    record.is_deleted = True
                if hasattr(record, "deleted_at"):
                    record.deleted_at = datetime.utcnow()

            count = len(records)

        return count

    def get_retention_report(self) -> List[Dict]:
        """
        Gera relatorio de retencao.

        Returns:
            Lista com status de cada politica
        """
        policies = self.db.query(RetentionPolicy).all()

        report = []
        for policy in policies:
            model_class = self._get_model_class(policy.entity_type)
            if not model_class:
                continue

            cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_days)
            date_field = getattr(model_class, policy.date_field, None)
            if not date_field:
                date_field = getattr(model_class, "created_at", None)

            if date_field:
                expired_count = self.db.query(model_class).filter(
                    date_field < cutoff_date
                ).count()
            else:
                expired_count = 0

            total_count = self.db.query(model_class).count()

            report.append({
                "entity_type": policy.entity_type,
                "retention_days": policy.retention_days,
                "legal_basis": policy.legal_basis,
                "total_records": total_count,
                "expired_records": expired_count,
                "can_auto_delete": policy.can_auto_delete,
                "last_execution": policy.last_execution,
                "next_execution": policy.next_execution,
            })

        return report

    def _get_model_class(self, entity_type: str) -> Optional[Type[Base]]:
        """
        Mapeia entity_type para classe do model.

        Args:
            entity_type: Tipo de entidade

        Returns:
            Classe do model ou None
        """
        # Mapeamento de entidades para models
        mapping = {
            "audit_logs": "AuditLog",
            "leads": "Lead",
            "opportunities": "Opportunity",
            "proposals": "Proposal",
            # Adicionar mais mapeamentos
        }

        model_name = mapping.get(entity_type)
        if not model_name:
            return None

        # Importar dinamicamente
        # Implementar import dinamico baseado no model_name
        return None
```

---

## 9. RELATORIOS DE CONFORMIDADE

### 9.1 Servico de Relatorios

```python
# modules/compliance/services/compliance_report_service.py
"""
Servico de relatorios de conformidade.

Gera relatorios para auditorias e reguladores.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID
import io

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from core.logging import logger
from modules.compliance.services.audit_service import AuditService
from modules.compliance.services.consent_service import ConsentService
from modules.compliance.services.risk_service import RiskService
from modules.compliance.services.soc2_service import SOC2Service


class ComplianceReportService:
    """
    Servico de relatorios de conformidade.

    Gera relatorios PDF e Excel para auditorias.
    """

    def __init__(self, db: Session) -> None:
        """
        Inicializa servico.

        Args:
            db: Sessao do banco
        """
        self.db = db
        self.audit_service = AuditService(db)
        self.consent_service = ConsentService(db)
        self.risk_service = RiskService(db)
        self.soc2_service = SOC2Service(db)

    def generate_lgpd_report(
        self,
        start_date: datetime,
        end_date: datetime,
        format: str = "pdf",
    ) -> bytes:
        """
        Gera relatorio LGPD.

        Args:
            start_date: Data inicial
            end_date: Data final
            format: Formato (pdf ou xlsx)

        Returns:
            Arquivo em bytes
        """
        data = self._collect_lgpd_data(start_date, end_date)

        if format == "pdf":
            return self._generate_pdf_report(
                title="Relatorio de Conformidade LGPD",
                data=data,
            )
        return self._generate_excel_report(data)

    def generate_iso27001_report(
        self,
        format: str = "pdf",
    ) -> bytes:
        """
        Gera relatorio ISO 27001.

        Args:
            format: Formato (pdf ou xlsx)

        Returns:
            Arquivo em bytes
        """
        data = self._collect_iso27001_data()

        if format == "pdf":
            return self._generate_pdf_report(
                title="Relatorio ISO 27001 - Sistema de Gestao de Seguranca",
                data=data,
            )
        return self._generate_excel_report(data)

    def generate_soc2_report(
        self,
        format: str = "pdf",
    ) -> bytes:
        """
        Gera relatorio SOC 2.

        Args:
            format: Formato (pdf ou xlsx)

        Returns:
            Arquivo em bytes
        """
        status = self.soc2_service.get_compliance_status()

        data = {
            "summary": {
                "Framework": "SOC 2 Type II",
                "Conformidade Geral": f"{status['overall_compliance']}%",
                "Total de Controles": status["total_controls"],
                "Controles Implementados": status["implemented_controls"],
            },
            "by_category": status["by_category"],
            "generated_at": datetime.utcnow().isoformat(),
        }

        if format == "pdf":
            return self._generate_pdf_report(
                title="Relatorio SOC 2 Type II",
                data=data,
            )
        return self._generate_excel_report(data)

    def generate_risk_report(
        self,
        format: str = "pdf",
    ) -> bytes:
        """
        Gera relatorio de riscos.

        Args:
            format: Formato (pdf ou xlsx)

        Returns:
            Arquivo em bytes
        """
        dashboard = self.risk_service.get_dashboard()
        matrix = self.risk_service.get_risk_matrix()

        data = {
            "summary": {
                "Total de Riscos": dashboard.total_risks,
                "Riscos Criticos": dashboard.critical_risks,
                "Riscos Altos": dashboard.high_risks,
                "Riscos Medios": dashboard.medium_risks,
                "Riscos Baixos": dashboard.low_risks,
                "Media de Risco Residual": f"{dashboard.average_residual_risk:.1f}",
            },
            "by_category": dashboard.by_category,
            "by_status": dashboard.by_status,
            "overdue_treatments": dashboard.overdue_treatments,
            "pending_reviews": dashboard.pending_reviews,
        }

        if format == "pdf":
            return self._generate_pdf_report(
                title="Relatorio de Gestao de Riscos",
                data=data,
            )
        return self._generate_excel_report(data)

    def _collect_lgpd_data(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Coleta dados para relatorio LGPD."""
        # Implementar coleta de dados
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "consents": {
                "total_granted": 0,
                "total_revoked": 0,
                "by_purpose": {},
            },
            "data_subjects": {
                "total": 0,
                "anonymized": 0,
            },
            "dsar_requests": {
                "total": 0,
                "completed": 0,
                "pending": 0,
                "average_response_days": 0,
            },
            "data_breaches": {
                "total": 0,
                "notified_to_anpd": 0,
            },
        }

    def _collect_iso27001_data(self) -> Dict[str, Any]:
        """Coleta dados para relatorio ISO 27001."""
        # Implementar coleta de dados
        return {
            "sgsi_status": "Operacional",
            "controls": {
                "total": 0,
                "implemented": 0,
                "in_progress": 0,
                "not_applicable": 0,
            },
            "risks": {
                "identified": 0,
                "treated": 0,
                "accepted": 0,
            },
            "incidents": {
                "total": 0,
                "resolved": 0,
            },
            "last_audit": None,
            "next_audit": None,
        }

    def _generate_pdf_report(
        self,
        title: str,
        data: Dict[str, Any],
    ) -> bytes:
        """
        Gera PDF do relatorio.

        Args:
            title: Titulo do relatorio
            data: Dados do relatorio

        Returns:
            PDF em bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        styles = getSampleStyleSheet()
        story = []

        # Titulo
        story.append(Paragraph(title, styles["Title"]))
        story.append(Spacer(1, 20))

        # Data de geracao
        story.append(
            Paragraph(
                f"Gerado em: {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 20))

        # Conteudo
        self._add_data_to_pdf(story, data, styles)

        doc.build(story)
        return buffer.getvalue()

    def _add_data_to_pdf(
        self,
        story: List,
        data: Dict[str, Any],
        styles,
        level: int = 0,
    ) -> None:
        """Adiciona dados ao PDF recursivamente."""
        for key, value in data.items():
            if isinstance(value, dict):
                story.append(
                    Paragraph(
                        key.replace("_", " ").title(),
                        styles["Heading2" if level == 0 else "Heading3"],
                    )
                )
                story.append(Spacer(1, 10))
                self._add_data_to_pdf(story, value, styles, level + 1)
            else:
                story.append(
                    Paragraph(
                        f"<b>{key.replace('_', ' ').title()}:</b> {value}",
                        styles["Normal"],
                    )
                )
                story.append(Spacer(1, 5))

    def _generate_excel_report(self, data: Dict[str, Any]) -> bytes:
        """
        Gera Excel do relatorio.

        Args:
            data: Dados do relatorio

        Returns:
            Excel em bytes
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Relatorio"

        row = 1
        for key, value in data.items():
            if isinstance(value, dict):
                ws.cell(row=row, column=1, value=key.upper())
                row += 1
                for k, v in value.items():
                    ws.cell(row=row, column=1, value=k)
                    ws.cell(row=row, column=2, value=str(v))
                    row += 1
                row += 1
            else:
                ws.cell(row=row, column=1, value=key)
                ws.cell(row=row, column=2, value=str(value))
                row += 1

        buffer = io.BytesIO()
        wb.save(buffer)
        return buffer.getvalue()
```

---

## 10. PORTAL DO TITULAR

### 10.1 Controller DSAR

```python
# modules/compliance/controllers/dsar_controller.py
"""
Controller de requisicoes do titular (DSAR).

Data Subject Access Request - Direitos do titular LGPD.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.compliance.schemas.dsar_schemas import (
    DSARCreate,
    DSARResponse,
    DSARStatus,
    DSARType,
)
from modules.compliance.services.dsar_service import DSARService

router = APIRouter(prefix="/lgpd/dsar", tags=["LGPD - Direitos do Titular"])


@router.post("/", response_model=DSARResponse, status_code=status.HTTP_201_CREATED)
async def create_dsar_request(
    data: DSARCreate,
    db: Session = Depends(get_db),
) -> DSARResponse:
    """
    Cria requisicao do titular.

    Tipos disponiveis:
    - ACCESS: Direito de acesso aos dados
    - RECTIFICATION: Correcao de dados
    - ERASURE: Eliminacao de dados
    - PORTABILITY: Portabilidade
    - RESTRICTION: Restricao de tratamento
    - OBJECTION: Oposicao ao tratamento

    Args:
        data: Dados da requisicao
        db: Sessao do banco

    Returns:
        Requisicao criada
    """
    service = DSARService(db)

    request = service.create_request(
        cpf=data.cpf,
        email=data.email,
        request_type=data.request_type,
        description=data.description,
        contact_phone=data.contact_phone,
    )

    return DSARResponse.from_orm(request)


@router.get("/{request_id}", response_model=DSARResponse)
async def get_dsar_request(
    request_id: UUID,
    db: Session = Depends(get_db),
) -> DSARResponse:
    """
    Consulta status de requisicao.

    Args:
        request_id: ID da requisicao
        db: Sessao do banco

    Returns:
        Dados da requisicao

    Raises:
        HTTPException: Se nao encontrada
    """
    service = DSARService(db)
    request = service.get_request(request_id)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requisicao nao encontrada",
        )

    return DSARResponse.from_orm(request)


@router.get("/", response_model=List[DSARResponse])
async def list_dsar_requests(
    status: DSARStatus = Query(None),
    request_type: DSARType = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),  # pylint: disable=unused-argument
) -> List[DSARResponse]:
    """
    Lista requisicoes (uso interno).

    Args:
        status: Filtro por status
        request_type: Filtro por tipo
        page: Numero da pagina
        page_size: Itens por pagina
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Lista de requisicoes
    """
    service = DSARService(db)

    requests, _ = service.list_requests(
        status=status,
        request_type=request_type,
        skip=(page - 1) * page_size,
        limit=page_size,
    )

    return [DSARResponse.from_orm(r) for r in requests]


@router.post("/{request_id}/process")
async def process_dsar_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentActiveUser = Depends(),
) -> DSARResponse:
    """
    Processa requisicao do titular.

    Args:
        request_id: ID da requisicao
        db: Sessao do banco
        current_user: Usuario autenticado

    Returns:
        Requisicao processada
    """
    service = DSARService(db)

    try:
        request = service.process_request(
            request_id=request_id,
            processed_by=current_user.id,
        )
        return DSARResponse.from_orm(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
```

---

## CHECKLIST DO SPRINT

```
SPRINT 35-38 - COMPLIANCE
=========================

[ ] Modulo LGPD
    [ ] Gestao de consentimentos
    [ ] Registro de tratamento (ROPA)
    [ ] Direitos do titular (DSAR)
    [ ] Anonimizacao de dados
    [ ] Portal do titular

[ ] ISO 27001
    [ ] Controles implementados
    [ ] Gestao de riscos
    [ ] Avaliacao de efetividade
    [ ] Documentacao SGSI

[ ] SOC 2
    [ ] Trust Service Criteria
    [ ] Controles por categoria
    [ ] Evidencias e avaliacao

[ ] Auditoria
    [ ] Trilha de auditoria completa
    [ ] Logs imutaveis
    [ ] Relatorios automatizados
    [ ] Deteccao de anomalias

[ ] Retencao de Dados
    [ ] Politicas por tipo de dado
    [ ] Eliminacao automatica
    [ ] Relatorios de retencao

[ ] Relatorios
    [ ] Relatorio LGPD
    [ ] Relatorio ISO 27001
    [ ] Relatorio SOC 2
    [ ] Relatorio de Riscos
    [ ] Exportacao PDF/Excel

[ ] Testes >= 85% cobertura
[ ] Documentacao completa
[ ] Aprovacao DPO
```

---

*Skill Compliance - ERP Conecta Mais Fase 2*
*"Conformidade nao e opcional"*
