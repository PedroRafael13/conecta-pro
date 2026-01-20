"""
Modelo EquipmentStatus para status de equipamentos do Guardian.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class EquipmentStatusType(str, Enum):
    """Status do equipamento."""

    ONLINE = "online"  # Online e funcionando
    OFFLINE = "offline"  # Offline
    WARNING = "warning"  # Alerta (funcionando com problemas)
    ERROR = "error"  # Erro
    MAINTENANCE = "maintenance"  # Em manutenção
    DISABLED = "disabled"  # Desativado


class EquipmentStatus(Base):
    """
    Modelo de Status de Equipamento.

    Armazena status em tempo real de equipamentos monitorados pelo Guardian,
    incluindo câmeras, alarmes, controle de acesso, etc.

    Attributes:
        id: Identificador único
        guardian_id: ID original no Guardian
        equipment_id: ID do equipamento
        equipment_type: Tipo do equipamento
        equipment_name: Nome do equipamento
        status: Status atual
        client_id: ID do cliente
        post_id: ID do posto
        ip_address: Endereço IP
        last_ping: Último ping
        uptime_percentage: Percentual de uptime
        last_event: Último evento
        metrics: Métricas do equipamento
    """

    __tablename__ = "equipment_status"

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
    equipment_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Equipamento
    equipment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # camera, alarm, access_control, sensor, dvr, nvr, intercom
    equipment_name: Mapped[str] = mapped_column(String(100), nullable=False)
    equipment_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    equipment_brand: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    firmware_version: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=EquipmentStatusType.OFFLINE.value,
        nullable=False,
        index=True,
    )
    status_message: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

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

    # Localização
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Rede
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(17), nullable=True)
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Conectividade
    last_ping_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ping_latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_online_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_offline_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Métricas
    uptime_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    uptime_hours_24h: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    uptime_hours_7d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    uptime_hours_30d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    incidents_count_30d: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Último evento
    last_event_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_event_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_event_description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Métricas específicas (JSONB para flexibilidade)
    metrics: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Ex para câmera: {"fps": 30, "resolution": "1080p", "storage_days": 15}
    # Ex para alarme: {"zones": 8, "armed_zones": 6, "battery_level": 95}

    # Alertas
    has_alerts: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    active_alerts: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    alert_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Manutenção
    next_maintenance_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    maintenance_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    received_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
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
        return f"<EquipmentStatus {self.equipment_name} {self.status}>"

    @property
    def is_online(self) -> bool:
        """Verifica se está online."""
        return self.status == EquipmentStatusType.ONLINE.value

    @property
    def is_offline(self) -> bool:
        """Verifica se está offline."""
        return self.status == EquipmentStatusType.OFFLINE.value

    @property
    def has_issues(self) -> bool:
        """Verifica se tem problemas."""
        return self.status in (
            EquipmentStatusType.WARNING.value,
            EquipmentStatusType.ERROR.value,
        )

    @property
    def is_camera(self) -> bool:
        """Verifica se é câmera."""
        return self.equipment_type in ("camera", "dvr", "nvr")

    @property
    def is_access_control(self) -> bool:
        """Verifica se é controle de acesso."""
        return self.equipment_type in ("access_control", "intercom", "gate")

    @property
    def is_alarm(self) -> bool:
        """Verifica se é alarme."""
        return self.equipment_type in ("alarm", "sensor")

    @property
    def needs_attention(self) -> bool:
        """Verifica se precisa de atenção."""
        return self.has_issues or self.has_alerts

    def set_online(self, latency_ms: int | None = None) -> None:
        """Marca como online."""
        self.status = EquipmentStatusType.ONLINE.value
        self.last_ping_at = datetime.utcnow()
        self.last_online_at = datetime.utcnow()
        if latency_ms:
            self.ping_latency_ms = latency_ms

    def set_offline(self, reason: str | None = None) -> None:
        """Marca como offline."""
        self.status = EquipmentStatusType.OFFLINE.value
        self.last_offline_at = datetime.utcnow()
        if reason:
            self.status_message = reason

    def add_alert(self, alert: dict) -> None:
        """Adiciona um alerta."""
        if not self.active_alerts:
            self.active_alerts = []
        self.active_alerts.append(alert)
        self.alert_count = len(self.active_alerts)
        self.has_alerts = True

    def clear_alerts(self) -> None:
        """Limpa os alertas."""
        self.active_alerts = []
        self.alert_count = 0
        self.has_alerts = False

    def update_metrics(self, metrics: dict) -> None:
        """Atualiza métricas."""
        if not self.metrics:
            self.metrics = {}
        self.metrics.update(metrics)
