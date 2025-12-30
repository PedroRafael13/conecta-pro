"""Modelo de Log de Visitante."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from core.database import Base

if TYPE_CHECKING:
    from modules.visitors.models.visitor import Visitor


class AccessType(str, Enum):
    """Tipos de acesso."""

    ENTRADA = "entrada"
    SAIDA = "saida"
    TENTATIVA_NEGADA = "tentativa_negada"
    ENTRADA_FORCADA = "entrada_forcada"
    SAIDA_FORCADA = "saida_forcada"


class AccessMethod(str, Enum):
    """Métodos de acesso."""

    PORTARIA = "portaria"
    BIOMETRIA = "biometria"
    FACIAL = "facial"
    CARTAO = "cartao"
    QR_CODE = "qr_code"
    CODIGO = "codigo"
    TAG = "tag"
    INTERFONE = "interfone"
    REMOTO = "remoto"
    MANUAL = "manual"


class AccessPoint(str, Enum):
    """Pontos de acesso."""

    PORTARIA_PRINCIPAL = "portaria_principal"
    PORTARIA_SERVICO = "portaria_servico"
    PORTARIA_SOCIAL = "portaria_social"
    GARAGEM_ENTRADA = "garagem_entrada"
    GARAGEM_SAIDA = "garagem_saida"
    PEDESTRES = "pedestres"
    LATERAL = "lateral"
    EMERGENCIA = "emergencia"
    ESTACIONAMENTO = "estacionamento"
    AREA_COMUM = "area_comum"


class DenialReason(str, Enum):
    """Motivos de negativa."""

    NAO_AUTORIZADO = "nao_autorizado"
    VISITANTE_BLOQUEADO = "visitante_bloqueado"
    AUTORIZACAO_EXPIRADA = "autorizacao_expirada"
    AUTORIZACAO_INVALIDA = "autorizacao_invalida"
    FORA_HORARIO = "fora_horario"
    DOCUMENTO_INVALIDO = "documento_invalido"
    MORADOR_AUSENTE = "morador_ausente"
    MORADOR_NAO_AUTORIZA = "morador_nao_autoriza"
    LIMITE_EXCEDIDO = "limite_excedido"
    SISTEMA_INDISPONIVEL = "sistema_indisponivel"
    OUTRO = "outro"


class VisitorLog(Base):
    """Modelo de Log de Visitante."""

    __tablename__ = "visitor_logs"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Visitante
    visitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("visitors.id"), nullable=False, index=True
    )

    # Autorização usada
    authorization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("visitor_authorizations.id")
    )

    # Tipo e método
    access_type: Mapped[AccessType] = mapped_column(
        String(20), nullable=False, index=True
    )
    access_method: Mapped[AccessMethod] = mapped_column(
        String(20), default=AccessMethod.PORTARIA
    )
    access_point: Mapped[AccessPoint] = mapped_column(
        String(30), default=AccessPoint.PORTARIA_PRINCIPAL
    )

    # Condomínio e Unidade
    condominium_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    condominium_name: Mapped[Optional[str]] = mapped_column(String(200))
    unit_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    unit_number: Mapped[Optional[str]] = mapped_column(String(20))
    block: Mapped[Optional[str]] = mapped_column(String(20))

    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )
    entry_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    exit_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)

    # Morador visitado
    resident_id: Mapped[Optional[str]] = mapped_column(String(50))
    resident_name: Mapped[Optional[str]] = mapped_column(String(200))
    resident_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    resident_notified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Porteiro/Operador
    operator_id: Mapped[Optional[str]] = mapped_column(String(50))
    operator_name: Mapped[Optional[str]] = mapped_column(String(200))

    # Veículo
    vehicle_plate: Mapped[Optional[str]] = mapped_column(String(10), index=True)
    vehicle_model: Mapped[Optional[str]] = mapped_column(String(100))
    vehicle_color: Mapped[Optional[str]] = mapped_column(String(50))
    parking_spot: Mapped[Optional[str]] = mapped_column(String(20))

    # Documentos verificados
    document_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    document_type: Mapped[Optional[str]] = mapped_column(String(20))
    document_number: Mapped[Optional[str]] = mapped_column(String(50))

    # Negativas
    denied: Mapped[bool] = mapped_column(Boolean, default=False)
    denial_reason: Mapped[Optional[DenialReason]] = mapped_column(String(30))
    denial_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Fotos e evidências
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    photo_vehicle_url: Mapped[Optional[str]] = mapped_column(String(500))
    photo_document_url: Mapped[Optional[str]] = mapped_column(String(500))
    signature_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Acompanhantes
    companions_count: Mapped[int] = mapped_column(Integer, default=0)
    companions_names: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Items/Volumes
    items_description: Mapped[Optional[str]] = mapped_column(Text)
    items_count: Mapped[int] = mapped_column(Integer, default=0)
    items_photo_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Observações
    purpose: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Equipamento
    device_id: Mapped[Optional[str]] = mapped_column(String(50))
    device_name: Mapped[Optional[str]] = mapped_column(String(100))

    # Sincronização Guardian
    guardian_sync_id: Mapped[Optional[str]] = mapped_column(String(50))
    guardian_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Temperatura (COVID/protocolo sanitário)
    temperature: Mapped[Optional[float]] = mapped_column(Integer)
    health_check_passed: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Controle
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Metadados
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Relacionamentos
    visitor: Mapped["Visitor"] = relationship("Visitor", back_populates="logs")

    def register_entry(
        self,
        method: AccessMethod = AccessMethod.PORTARIA,
        point: AccessPoint = AccessPoint.PORTARIA_PRINCIPAL,
        operator_id: str = None,
        operator_name: str = None,
    ) -> None:
        """Registra entrada."""
        self.access_type = AccessType.ENTRADA
        self.access_method = method
        self.access_point = point
        self.entry_at = datetime.utcnow()
        self.timestamp = self.entry_at
        self.operator_id = operator_id
        self.operator_name = operator_name

    def register_exit(
        self,
        method: AccessMethod = AccessMethod.PORTARIA,
        point: AccessPoint = AccessPoint.PORTARIA_PRINCIPAL,
        operator_id: str = None,
        operator_name: str = None,
    ) -> None:
        """Registra saída."""
        self.access_type = AccessType.SAIDA
        self.access_method = method
        self.access_point = point
        self.exit_at = datetime.utcnow()
        self.timestamp = self.exit_at
        self.operator_id = operator_id
        self.operator_name = operator_name

        if self.entry_at:
            delta = self.exit_at - self.entry_at
            self.duration_minutes = int(delta.total_seconds() / 60)

    def deny_access(
        self, reason: DenialReason, notes: str = None, operator_id: str = None
    ) -> None:
        """Registra negativa de acesso."""
        self.access_type = AccessType.TENTATIVA_NEGADA
        self.denied = True
        self.denial_reason = reason
        self.denial_notes = notes
        self.timestamp = datetime.utcnow()
        self.operator_id = operator_id

    def notify_resident(self) -> None:
        """Marca morador como notificado."""
        self.resident_notified = True
        self.resident_notified_at = datetime.utcnow()

    def verify_document(
        self, document_type: str, document_number: str, photo_url: str = None
    ) -> None:
        """Verifica documento."""
        self.document_verified = True
        self.document_type = document_type
        self.document_number = document_number
        if photo_url:
            self.photo_document_url = photo_url

    def add_companions(self, count: int, names: list = None) -> None:
        """Adiciona acompanhantes."""
        self.companions_count = count
        if names:
            self.companions_names = names

    def add_items(self, description: str, count: int = 1, photo_url: str = None) -> None:
        """Adiciona itens/volumes."""
        self.items_description = description
        self.items_count = count
        if photo_url:
            self.items_photo_url = photo_url

    def add_vehicle(
        self, plate: str, model: str = None, color: str = None, spot: str = None
    ) -> None:
        """Adiciona veículo."""
        self.vehicle_plate = plate
        self.vehicle_model = model
        self.vehicle_color = color
        self.parking_spot = spot

    def soft_delete(self) -> None:
        """Soft delete."""
        self.is_deleted = True

    @property
    def is_entry(self) -> bool:
        """Verifica se é entrada."""
        return self.access_type == AccessType.ENTRADA

    @property
    def is_exit(self) -> bool:
        """Verifica se é saída."""
        return self.access_type == AccessType.SAIDA

    @property
    def is_denied(self) -> bool:
        """Verifica se foi negado."""
        return self.denied or self.access_type == AccessType.TENTATIVA_NEGADA

    @property
    def is_still_inside(self) -> bool:
        """Verifica se ainda está dentro."""
        return self.is_entry and not self.exit_at

    @property
    def has_companions(self) -> bool:
        """Verifica se tem acompanhantes."""
        return self.companions_count > 0

    @property
    def has_items(self) -> bool:
        """Verifica se tem itens."""
        return self.items_count > 0

    @property
    def has_vehicle(self) -> bool:
        """Verifica se tem veículo."""
        return bool(self.vehicle_plate)

    @property
    def formatted_duration(self) -> str:
        """Duração formatada."""
        if not self.duration_minutes:
            return "N/A"
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}min"
        return f"{minutes}min"

    @property
    def access_type_display(self) -> str:
        """Tipo de acesso para exibição."""
        type_map = {
            AccessType.ENTRADA: "Entrada",
            AccessType.SAIDA: "Saída",
            AccessType.TENTATIVA_NEGADA: "Acesso Negado",
            AccessType.ENTRADA_FORCADA: "Entrada Forçada",
            AccessType.SAIDA_FORCADA: "Saída Forçada",
        }
        return type_map.get(self.access_type, self.access_type.value)
