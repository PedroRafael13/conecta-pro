"""Modelo de Dependente do Morador."""

import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.residents.models.resident import Resident


class RelationshipType(str, Enum):
    """Tipo de relacionamento/parentesco."""

    CONJUGE = "conjuge"
    FILHO = "filho"
    FILHA = "filha"
    PAI = "pai"
    MAE = "mae"
    IRMAO = "irmao"
    IRMA = "irma"
    AVO = "avo"
    NETO = "neto"
    TIO = "tio"
    SOBRINHO = "sobrinho"
    PRIMO = "primo"
    ENTEADO = "enteado"
    SOGRO = "sogro"
    GENRO = "genro"
    NORA = "nora"
    CUNHADO = "cunhado"
    EMPREGADO_DOMESTICO = "empregado_domestico"
    CUIDADOR = "cuidador"
    AGREGADO = "agregado"
    OUTRO = "outro"


class DependentStatus(str, Enum):
    """Status do dependente."""

    ATIVO = "ativo"
    INATIVO = "inativo"
    BLOQUEADO = "bloqueado"
    TEMPORARIO = "temporario"


class DependentDocumentType(str, Enum):
    """Tipo de documento do dependente."""

    CPF = "cpf"
    RG = "rg"
    CERTIDAO_NASCIMENTO = "certidao_nascimento"
    PASSAPORTE = "passaporte"
    RNE = "rne"
    CTPS = "ctps"
    OUTRO = "outro"


class ResidentDependent(Base):
    """Modelo de Dependente do Morador."""

    __tablename__ = "resident_dependents"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Relacionamento com morador
    resident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("residents.id"), nullable=False, index=True
    )

    # Tipo de relacionamento
    relationship_type: Mapped[RelationshipType] = mapped_column(
        String(30), nullable=False
    )
    relationship_description: Mapped[Optional[str]] = mapped_column(String(100))

    # Dados pessoais
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    social_name: Mapped[Optional[str]] = mapped_column(String(200))
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(30))

    # Documento
    document_type: Mapped[Optional[DependentDocumentType]] = mapped_column(String(30))
    document_number: Mapped[Optional[str]] = mapped_column(String(50))
    cpf: Mapped[Optional[str]] = mapped_column(String(14))

    # Contato
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(200))

    # Status
    status: Mapped[DependentStatus] = mapped_column(
        String(20), default=DependentStatus.ATIVO
    )

    # Foto e biometria
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    facial_id: Mapped[Optional[str]] = mapped_column(String(100))
    fingerprint_id: Mapped[Optional[str]] = mapped_column(String(100))

    # Controle de acesso
    has_access: Mapped[bool] = mapped_column(Boolean, default=True)
    access_card_number: Mapped[Optional[str]] = mapped_column(String(50))
    access_tag_rfid: Mapped[Optional[str]] = mapped_column(String(50))

    # Permissões
    can_authorize_visitors: Mapped[bool] = mapped_column(Boolean, default=False)
    can_receive_deliveries: Mapped[bool] = mapped_column(Boolean, default=True)
    can_use_common_areas: Mapped[bool] = mapped_column(Boolean, default=True)

    # Para menores de idade
    is_minor: Mapped[bool] = mapped_column(Boolean, default=False)
    school_name: Mapped[Optional[str]] = mapped_column(String(200))
    school_phone: Mapped[Optional[str]] = mapped_column(String(20))
    authorized_pickup_persons: Mapped[Optional[list]] = mapped_column(
        JSONB, default=list
    )

    # Para funcionários domésticos
    is_employee: Mapped[bool] = mapped_column(Boolean, default=False)
    work_schedule: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    employment_start_date: Mapped[Optional[date]] = mapped_column(Date)
    employment_end_date: Mapped[Optional[date]] = mapped_column(Date)

    # Datas de validade
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_until: Mapped[Optional[date]] = mapped_column(Date)

    # Bloqueio
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    block_reason: Mapped[Optional[str]] = mapped_column(Text)
    blocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Necessidades especiais
    has_special_needs: Mapped[bool] = mapped_column(Boolean, default=False)
    special_needs_description: Mapped[Optional[str]] = mapped_column(Text)

    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Metadados
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relacionamentos
    resident: Mapped["Resident"] = relationship("Resident", back_populates="dependents")

    def __init__(self, **kwargs):
        """Inicializa o dependente."""
        super().__init__(**kwargs)
        # Auto-detecta se é menor de idade
        if self.birth_date:
            self._update_minor_status()

    def _update_minor_status(self) -> None:
        """Atualiza status de menor de idade."""
        if self.birth_date:
            age = self.age
            if age is not None:
                self.is_minor = age < 18

    def block(self, reason: str) -> None:
        """Bloqueia o dependente."""
        self.is_blocked = True
        self.status = DependentStatus.BLOQUEADO
        self.block_reason = reason
        self.blocked_at = datetime.utcnow()
        self.has_access = False

    def unblock(self) -> None:
        """Desbloqueia o dependente."""
        self.is_blocked = False
        self.status = DependentStatus.ATIVO
        self.block_reason = None
        self.blocked_at = None
        self.has_access = True

    def deactivate(self) -> None:
        """Desativa o dependente."""
        self.status = DependentStatus.INATIVO
        self.has_access = False

    def activate(self) -> None:
        """Ativa o dependente."""
        self.status = DependentStatus.ATIVO
        self.has_access = True

    def set_temporary(self, valid_from: date, valid_until: date) -> None:
        """Define como temporário com período de validade."""
        self.status = DependentStatus.TEMPORARIO
        self.valid_from = valid_from
        self.valid_until = valid_until

    def add_authorized_pickup(self, name: str, phone: str, document: str = None) -> None:
        """Adiciona pessoa autorizada a buscar (para menores)."""
        if not self.authorized_pickup_persons:
            self.authorized_pickup_persons = []
        self.authorized_pickup_persons.append({
            "name": name,
            "phone": phone,
            "document": document,
            "added_at": datetime.utcnow().isoformat(),
        })

    def remove_authorized_pickup(self, name: str) -> None:
        """Remove pessoa autorizada a buscar."""
        if self.authorized_pickup_persons:
            self.authorized_pickup_persons = [
                p for p in self.authorized_pickup_persons if p.get("name") != name
            ]

    def set_work_schedule(self, schedule: dict) -> None:
        """Define horário de trabalho (funcionários domésticos)."""
        self.is_employee = True
        self.work_schedule = schedule

    @property
    def is_active(self) -> bool:
        """Verifica se está ativo."""
        if self.status != DependentStatus.ATIVO and self.status != DependentStatus.TEMPORARIO:
            return False
        if self.is_blocked:
            return False
        return True

    @property
    def is_valid(self) -> bool:
        """Verifica se é válido para acesso."""
        if not self.is_active:
            return False
        if not self.has_access:
            return False
        if self.status == DependentStatus.TEMPORARIO:
            today = date.today()
            if self.valid_from and self.valid_from > today:
                return False
            if self.valid_until and self.valid_until < today:
                return False
        return True

    @property
    def age(self) -> Optional[int]:
        """Calcula idade."""
        if not self.birth_date:
            return None
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @property
    def has_biometric(self) -> bool:
        """Verifica se tem biometria cadastrada."""
        return bool(self.facial_id or self.fingerprint_id)

    @property
    def display_name(self) -> str:
        """Nome para exibição."""
        return self.social_name or self.name

    @property
    def relationship_display(self) -> str:
        """Exibição do tipo de relacionamento."""
        relationship_map = {
            RelationshipType.CONJUGE: "Cônjuge",
            RelationshipType.FILHO: "Filho",
            RelationshipType.FILHA: "Filha",
            RelationshipType.PAI: "Pai",
            RelationshipType.MAE: "Mãe",
            RelationshipType.IRMAO: "Irmão",
            RelationshipType.IRMA: "Irmã",
            RelationshipType.AVO: "Avô/Avó",
            RelationshipType.NETO: "Neto/Neta",
            RelationshipType.TIO: "Tio/Tia",
            RelationshipType.SOBRINHO: "Sobrinho/Sobrinha",
            RelationshipType.PRIMO: "Primo/Prima",
            RelationshipType.ENTEADO: "Enteado/Enteada",
            RelationshipType.SOGRO: "Sogro/Sogra",
            RelationshipType.GENRO: "Genro",
            RelationshipType.NORA: "Nora",
            RelationshipType.CUNHADO: "Cunhado/Cunhada",
            RelationshipType.EMPREGADO_DOMESTICO: "Empregado(a) Doméstico(a)",
            RelationshipType.CUIDADOR: "Cuidador(a)",
            RelationshipType.AGREGADO: "Agregado",
            RelationshipType.OUTRO: "Outro",
        }
        return relationship_map.get(self.relationship_type, "Outro")
