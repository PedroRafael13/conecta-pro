"""
Modelo AccessLog para logs de acesso do CAMPO.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class AccessLogType(StrEnum):
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

    Armazena todos os registros de acesso,
    incluindo entradas, saídas, negações e eventos especiais.

    Attributes:
        id: Identificador único
        external_id: ID externo de integração
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
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    external_id: Mapped[str] = mapped_column(
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
        String(36),
        nullable=False,
        index=True,
    )
    contract_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )
    post_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    # Pessoa
    person_name: Mapped[str] = mapped_column(String(255), nullable=False)
    person_document: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )
    person_type: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )  # morador, visitante, prestador, funcionario
    person_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    # Localização
    unit_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    unit_block: Mapped[str | None] = mapped_column(String(20), nullable=True)
    access_point: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )  # Portaria, Garagem, Social, etc.
    access_point_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Método de Acesso
    access_method: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )  # facial, tag_rfid, senha, biometria, interfone, remoto
    device_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    device_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Veículo (se aplicável)
    vehicle_plate: Mapped[str | None] = mapped_column(String(10), nullable=True)
    vehicle_model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vehicle_color: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Operador
    operator_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )
    operator_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    authorization_type: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )  # automatico, manual, morador

    # Mídia
    photos: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    video_clip_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Observações
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    denial_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    # Metadados
    external_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sync_id: Mapped[str | None] = mapped_column(
        String(36),
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
