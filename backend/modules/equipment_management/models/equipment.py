"""
Model Equipment - Cadastro de Equipamentos de Segurança Eletrônica.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class EquipmentType(str, Enum):
    """Tipos de equipamento."""

    CAMERA_IP = "camera_ip"
    CAMERA_ANALOGICA = "camera_analogica"
    DVR = "dvr"
    NVR = "nvr"
    ALARME_CENTRAL = "alarme_central"
    SENSOR_MOVIMENTO = "sensor_movimento"
    SENSOR_ABERTURA = "sensor_abertura"
    SENSOR_FUMACA = "sensor_fumaca"
    SENSOR_PRESENCA = "sensor_presenca"
    CONTROLE_ACESSO = "controle_acesso"
    CATRACA = "catraca"
    PORTAO_AUTOMATICO = "portao_automatico"
    CANCELA = "cancela"
    INTERFONE = "interfone"
    VIDEOPORTEIRO = "videoporteiro"
    CERCA_ELETRICA = "cerca_eletrica"
    CONCERTINA = "concertina"
    LEITOR_BIOMETRICO = "leitor_biometrico"
    LEITOR_RFID = "leitor_rfid"
    NOBREAK = "nobreak"
    SWITCH_REDE = "switch_rede"
    ROTEADOR = "roteador"
    OUTRO = "outro"


class EquipmentCategory(str, Enum):
    """Categorias de equipamento."""

    CFTV = "cftv"  # Câmeras, DVR, NVR
    ALARME = "alarme"  # Alarmes, sensores
    CONTROLE_ACESSO = "controle_acesso"  # Catracas, leitores, portões
    REDE = "rede"  # Switches, roteadores, nobreaks
    PERIMETRAL = "perimetral"  # Cercas, concertinas
    COMUNICACAO = "comunicacao"  # Interfones, videoporteiros
    OUTRO = "outro"


class EquipmentStatus(str, Enum):
    """Status do equipamento."""

    ESTOQUE = "estoque"  # Em estoque, aguardando instalação
    INSTALADO = "instalado"  # Instalado e funcionando
    MANUTENCAO = "manutencao"  # Em manutenção
    DEFEITO = "defeito"  # Com defeito, aguardando reparo
    COMODATO = "comodato"  # Em comodato com cliente
    BAIXA = "baixa"  # Baixado do patrimônio
    RESERVADO = "reservado"  # Reservado para instalação


class Equipment(Base):
    """
    Model para equipamentos de segurança eletrônica.

    Gerencia o cadastro completo de equipamentos:
    câmeras, alarmes, sensores, controle de acesso, etc.
    """

    __tablename__ = "equipments"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    equipment_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    # Classificação
    equipment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=EquipmentStatus.ESTOQUE.value,
        nullable=False,
        index=True,
    )

    # Informações do produto
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )
    part_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    firmware_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Descrição
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Aquisição
    supplier_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    supplier_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    purchase_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    purchase_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Garantia
    warranty_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    warranty_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    warranty_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    has_extended_warranty: Mapped[bool] = mapped_column(Boolean, default=False)

    # Localização atual (estoque ou cliente)
    location_type: Mapped[str] = mapped_column(
        String(20),
        default="estoque",
    )  # estoque, cliente
    location_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )  # warehouse_id ou client_id
    location_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    location_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Cliente/Contrato (quando instalado)
    client_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    client_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contract_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    post_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), nullable=True)

    # Instalação
    installation_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    installed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    installed_location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    gps_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gps_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Configuração técnica
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    http_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rtsp_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    technical_config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Status operacional (para equipamentos instalados)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    last_online_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_offline_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    uptime_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Manutenção
    last_maintenance_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    next_maintenance_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    maintenance_interval_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    total_maintenances: Mapped[int] = mapped_column(Integer, default=0)

    # Depreciação
    depreciation_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )  # % ao ano
    current_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    useful_life_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Imagens
    images: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    qr_code_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Metadados
    tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_extra: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Auditoria
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Properties
    @property
    def is_installed(self) -> bool:
        """Verifica se o equipamento está instalado."""
        return self.status == EquipmentStatus.INSTALADO.value

    @property
    def is_in_warranty(self) -> bool:
        """Verifica se está na garantia."""
        if not self.warranty_end:
            return False
        return datetime.utcnow() < self.warranty_end

    @property
    def days_until_warranty_end(self) -> Optional[int]:
        """Dias até o fim da garantia."""
        if not self.warranty_end:
            return None
        delta = self.warranty_end - datetime.utcnow()
        return max(0, delta.days)

    @property
    def needs_maintenance(self) -> bool:
        """Verifica se precisa de manutenção."""
        if not self.next_maintenance_at:
            return False
        return datetime.utcnow() >= self.next_maintenance_at

    @property
    def days_until_maintenance(self) -> Optional[int]:
        """Dias até a próxima manutenção."""
        if not self.next_maintenance_at:
            return None
        delta = self.next_maintenance_at - datetime.utcnow()
        return delta.days

    # Methods
    def install(
        self,
        client_id: str,
        client_name: str,
        installation_id: str,
        location: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> None:
        """Marca equipamento como instalado."""
        self.status = EquipmentStatus.INSTALADO.value
        self.location_type = "cliente"
        self.client_id = client_id
        self.client_name = client_name
        self.location_id = client_id
        self.location_name = client_name
        self.installation_id = installation_id
        self.installed_at = datetime.utcnow()
        self.installed_location = location
        self.gps_latitude = latitude
        self.gps_longitude = longitude

    def uninstall(self, reason: Optional[str] = None) -> None:
        """Remove equipamento de instalação."""
        self.status = EquipmentStatus.ESTOQUE.value
        self.location_type = "estoque"
        self.client_id = None
        self.client_name = None
        self.contract_id = None
        self.post_id = None
        self.installation_id = None
        self.installed_at = None
        self.installed_location = None
        self.gps_latitude = None
        self.gps_longitude = None
        self.is_online = False
        if reason:
            self.notes = f"Desinstalado: {reason}"

    def set_online(self) -> None:
        """Marca equipamento como online."""
        self.is_online = True
        self.last_online_at = datetime.utcnow()

    def set_offline(self) -> None:
        """Marca equipamento como offline."""
        self.is_online = False
        self.last_offline_at = datetime.utcnow()

    def send_to_maintenance(self, reason: Optional[str] = None) -> None:
        """Envia para manutenção."""
        self.status = EquipmentStatus.MANUTENCAO.value
        if reason:
            self.notes = f"Manutenção: {reason}"

    def return_from_maintenance(self) -> None:
        """Retorna da manutenção."""
        if self.client_id:
            self.status = EquipmentStatus.INSTALADO.value
        else:
            self.status = EquipmentStatus.ESTOQUE.value
        self.last_maintenance_at = datetime.utcnow()
        self.total_maintenances += 1

    def mark_defective(self, reason: str) -> None:
        """Marca como defeituoso."""
        self.status = EquipmentStatus.DEFEITO.value
        self.is_online = False
        self.notes = f"Defeito: {reason}"

    def decommission(self, reason: str) -> None:
        """Baixa do patrimônio."""
        self.status = EquipmentStatus.BAIXA.value
        self.is_online = False
        self.is_active = False
        self.notes = f"Baixa: {reason}"

    def calculate_depreciation(self) -> Optional[float]:
        """Calcula valor depreciado atual."""
        if not all([self.purchase_value, self.purchase_date, self.depreciation_rate]):
            return None

        years_owned = (datetime.utcnow() - self.purchase_date).days / 365
        depreciated = self.purchase_value * (1 - (self.depreciation_rate / 100)) ** years_owned
        self.current_value = max(0, depreciated)
        return self.current_value
