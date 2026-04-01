"""Model para integração com sistemas de folha externos."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class IntegrationType(StrEnum):
    """Tipo de sistema de integração."""

    ESOCIAL = "esocial"  # eSocial (Governo)
    TOTVS = "totvs"  # TOTVS Protheus/RM
    SENIOR = "senior"  # Senior Sistemas
    SAP = "sap"  # SAP HR
    ADP = "adp"  # ADP
    DOMINIO = "dominio"  # Domínio Sistemas
    FORTES = "fortes"  # Fortes Tecnologia
    ALTERDATA = "alterdata"  # Alterdata
    QUESTOR = "questor"  # Questor
    METADADOS = "metadados"  # Metadados
    CUSTOM = "custom"  # Sistema customizado
    API = "api"  # API genérica
    FILE = "file"  # Importação/exportação por arquivo


class IntegrationStatus(StrEnum):
    """Status da integração."""

    ACTIVE = "active"  # Ativa
    INACTIVE = "inactive"  # Inativa
    ERROR = "error"  # Com erro
    CONFIGURING = "configuring"  # Em configuração
    TESTING = "testing"  # Em teste


class PayrollIntegration(Base):
    """Configuração de integração com sistema externo."""

    __tablename__ = "payroll_integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificação
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    integration_type = Column(
        String(30),
        nullable=False,
        default=IntegrationType.ESOCIAL.value,
    )

    # Configurações de conexão
    endpoint_url = Column(String(500), nullable=True)  # URL da API
    api_version = Column(String(20), nullable=True)
    auth_type = Column(String(30), nullable=True)  # oauth2, basic, certificate, apikey
    credentials = Column(JSONB, default=dict)  # Credenciais (criptografadas)
    # {
    #   "client_id": "...",
    #   "client_secret": "...",
    #   "certificate_path": "...",
    #   "api_key": "..."
    # }

    # Configurações eSocial específicas
    esocial_config = Column(JSONB, default=dict)
    # {
    #   "ambiente": "producao",  # producao, producao_restrita
    #   "tipo_inscricao": 1,  # 1-CNPJ, 2-CPF
    #   "nr_inscricao": "12345678000199",
    #   "transmissor_cnpj": "...",
    #   "certificado_tipo": "A1",  # A1 ou A3
    #   "certificado_senha": "...",
    #   "procurador_cnpj": null
    # }

    # Mapeamento de campos/rubricas
    field_mapping = Column(JSONB, default=dict)
    # {
    #   "employee_id": "CODCOLIGADA",
    #   "salary": "VALSALARIO",
    #   "overtime_50": "VALHREXTRA50",
    #   ...
    # }

    # Mapeamento de rubricas para códigos externos
    rubrica_mapping = Column(JSONB, default=dict)
    # {
    #   "1000": "0001",  # Salário
    #   "1050": "0050",  # HE 50%
    #   ...
    # }

    # Configurações de sincronização
    sync_config = Column(JSONB, default=dict)
    # {
    #   "auto_sync": true,
    #   "sync_interval_hours": 24,
    #   "sync_direction": "export",  # import, export, both
    #   "sync_events": ["S-1200", "S-1210"],
    #   "batch_size": 100
    # }

    # Status e monitoramento
    status = Column(String(20), nullable=False, default=IntegrationStatus.CONFIGURING.value)
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(20), nullable=True)
    last_sync_message = Column(Text, nullable=True)
    last_sync_records = Column(Integer, default=0)
    total_syncs = Column(Integer, default=0)
    successful_syncs = Column(Integer, default=0)
    failed_syncs = Column(Integer, default=0)

    # Webhook para notificações
    webhook_url = Column(String(500), nullable=True)
    webhook_secret = Column(String(200), nullable=True)
    webhook_events = Column(JSONB, default=list)  # ["sync_complete", "error", etc.]

    # Logs e histórico
    error_log = Column(JSONB, default=list)  # Últimos N erros
    # [{
    #   "timestamp": "...",
    #   "error_code": "...",
    #   "message": "...",
    #   "details": {...}
    # }]

    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_payroll_integrations_type", "integration_type"),
        Index("ix_payroll_integrations_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<PayrollIntegration {self.name} ({self.integration_type})>"

    @property
    def is_active(self) -> bool:
        """Verifica se integração está ativa."""
        return self.status == IntegrationStatus.ACTIVE.value and self.ativo

    @property
    def is_esocial(self) -> bool:
        """Verifica se é integração eSocial."""
        return self.integration_type == IntegrationType.ESOCIAL.value

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso das sincronizações."""
        if self.total_syncs == 0:
            return 0.0
        return (self.successful_syncs / self.total_syncs) * 100

    @property
    def needs_certificate(self) -> bool:
        """Verifica se precisa de certificado digital."""
        return (
            self.integration_type
            in [
                IntegrationType.ESOCIAL.value,
            ]
            or self.auth_type == "certificate"
        )

    def record_sync(
        self,
        success: bool,
        records: int = 0,
        message: str = None,
    ) -> None:
        """Registra resultado de sincronização."""
        self.last_sync_at = datetime.utcnow()
        self.last_sync_status = "success" if success else "error"
        self.last_sync_message = message
        self.last_sync_records = records
        self.total_syncs += 1
        if success:
            self.successful_syncs += 1
        else:
            self.failed_syncs += 1
            # Adicionar ao log de erros
            if not self.error_log:
                self.error_log = []
            self.error_log.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": message,
                    "records": records,
                }
            )
            # Manter apenas últimos 50 erros
            self.error_log = self.error_log[-50:]

    def get_rubrica_code(self, internal_code: str) -> str | None:
        """Obtém código externo de rubrica."""
        return self.rubrica_mapping.get(internal_code)

    def get_field_mapping(self, internal_field: str) -> str | None:
        """Obtém mapeamento de campo externo."""
        return self.field_mapping.get(internal_field)

    def to_dict(self) -> dict:
        """Converte para dicionário (sem credenciais)."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "integration_type": self.integration_type,
            "status": self.status,
            "last_sync_at": (self.last_sync_at.isoformat() if self.last_sync_at else None),
            "last_sync_status": self.last_sync_status,
            "success_rate": round(self.success_rate, 2),
            "total_syncs": self.total_syncs,
            "is_active": self.is_active,
        }
