"""
Modelo AccessLog para logs de acesso do Guardian.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class AccessLogType(str, Enum):
    """Tipo de log de acesso."""

    ENTRY = "entry"  # Entrada
    EXIT = "exit"  # Saída
    DENIED = "denied"  # Acesso negado
    VISITOR = "visitor"  # Visitante
    DELIVERY = "delivery"  # Entrega
    SERVICE = "service"  # Prestador de serviço
    EMERGENCY = "emergency"  # Emergência
    PATROL = "patrol"  # Ronda
    INTERCOM = "intercom"  # Chamada de interfone


class AccessLog(Base):
    """
    Modelo de Log de Acesso.

    Armazena todos os registros de acesso recebidos do Conecta Guardian,
    incluindo entradas, saídas, negações e eventos especiais.

    Attributes:
        id: Identificador único
        guardian_id: ID original no Guardian
        log_type: Tipo de acesso
        client_id: ID do cliente/condomínio
        post_id: ID do posto de acesso
        person_name: Nome da pessoa
        person_document: Documento (CPF/RG)
        person_type: Tipo (morador, visitante, prestador)
        unit_code: Código da unidade
        access_point: Ponto de acesso
        method: Método de acesso (facial, tag, senha, interfone)
        device_id: ID do dispositivo
        photos: URLs das fotos
        operator_id: Operador que liberou
        notes: Observações
        event_timestamp: Data/hora do evento
    """

    __tablename__ = "access_logs"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    guardian_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    # Tipo e Status
    log_type: Mapped[str] = mapped_column(
        String(30),
        default=AccessLogType.ENTRY.value,
        nullable=False,
        index=True,
    )

    # Referências
    client_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )
    contract_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    post_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )

    # Pessoa
    person_name: Mapped[str] = mapped_column(String(255), nullable=False)
    person_document: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )
    person_type: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )  # morador, visitante, prestador, funcionario
    person_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )

    # Localização
    unit_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    unit_block: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    access_point: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )  # Portaria, Garagem, Social, etc.
    access_point_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    # Método de Acesso
    access_method: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )  # facial, tag_rfid, senha, biometria, interfone, remoto
    device_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    device_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Veículo (se aplicável)
    vehicle_plate: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    vehicle_model: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    vehicle_color: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Operador
    operator_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    operator_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    authorization_type: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )  # automatico, manual, morador

    # Mídia
    photos: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    video_clip_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    denial_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    # Geolocalização
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    # Metadados
    guardian_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    sync_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    def __repr__(self) -> str:
        """Representação textual."""
        return f"<AccessLog {self.log_type} {self.person_name} {self.event_timestamp}>"

    @property
    def is_entry(self) -> bool:
        """Verifica se é entrada."""
        return self.log_type == AccessLogType.ENTRY.value

    @property
    def is_exit(self) -> bool:
        """Verifica se é saída."""
        return self.log_type == AccessLogType.EXIT.value

    @property
    def is_denied(self) -> bool:
        """Verifica se foi negado."""
        return self.log_type == AccessLogType.DENIED.value

    @property
    def is_visitor(self) -> bool:
        """Verifica se é visitante."""
        return self.person_type == "visitante"

    @property
    def has_vehicle(self) -> bool:
        """Verifica se tem veículo."""
        return self.vehicle_plate is not None

    @property
    def was_authorized_manually(self) -> bool:
        """Verifica se foi autorizado manualmente."""
        return self.authorization_type == "manual"

    @property
    def has_media(self) -> bool:
        """Verifica se tem mídia anexada."""
        return bool(self.photos) or bool(self.video_clip_url)
