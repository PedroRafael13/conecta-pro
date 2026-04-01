"""Model para exportação de folha de pagamento."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class ExportFormat(StrEnum):
    """Formato de exportação."""

    # Formatos de arquivo
    TXT = "txt"  # Texto posicional (layout fixo)
    CSV = "csv"  # CSV padrão
    XLSX = "xlsx"  # Excel
    XML = "xml"  # XML genérico
    JSON = "json"  # JSON

    # Formatos específicos de sistemas
    ESOCIAL_XML = "esocial_xml"  # XML eSocial
    SEFIP = "sefip"  # SEFIP/GFIP
    CAGED = "caged"  # CAGED
    RAIS = "rais"  # RAIS
    DIRF = "dirf"  # DIRF

    # Layouts bancários
    CNAB240 = "cnab240"  # CNAB 240
    CNAB400 = "cnab400"  # CNAB 400
    FEBRABAN = "febraban"  # Padrão Febraban

    # Layouts de sistemas específicos
    TOTVS_TXT = "totvs_txt"  # Layout TOTVS
    SENIOR_TXT = "senior_txt"  # Layout Senior
    ADP_TXT = "adp_txt"  # Layout ADP


class ExportStatus(StrEnum):
    """Status da exportação."""

    PENDING = "pending"  # Aguardando
    PROCESSING = "processing"  # Processando
    COMPLETED = "completed"  # Concluído
    FAILED = "failed"  # Falhou
    PARTIAL = "partial"  # Parcialmente concluído
    CANCELLED = "cancelled"  # Cancelado
    TRANSMITTED = "transmitted"  # Transmitido (eSocial)
    ACCEPTED = "accepted"  # Aceito pelo destino
    REJECTED = "rejected"  # Rejeitado pelo destino


class PayrollExport(Base):
    """Exportação de dados de folha."""

    __tablename__ = "payroll_exports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )
    period_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payroll_periods.id"),
        nullable=True,
        index=True,
    )
    integration_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payroll_integrations.id"),
        nullable=True,
        index=True,
    )

    # Identificação
    export_code = Column(String(50), nullable=False)  # Código único
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Tipo e formato
    export_format = Column(String(30), nullable=False)
    export_type = Column(String(50), nullable=True)  # S-1200, pagamento, etc.

    # Escopo da exportação
    scope = Column(JSONB, default=dict)
    # {
    #   "employees": ["all"] ou ["uuid1", "uuid2"],
    #   "departments": ["all"] ou ["uuid1"],
    #   "event_types": ["earning", "deduction"],
    #   "event_categories": ["salary", "overtime_50"],
    #   "date_range": {"start": "...", "end": "..."}
    # }

    # Configurações do arquivo
    file_config = Column(JSONB, default=dict)
    # {
    #   "encoding": "utf-8",
    #   "delimiter": ";",
    #   "line_ending": "\r\n",
    #   "include_header": true,
    #   "decimal_separator": ",",
    #   "date_format": "dd/mm/yyyy"
    # }

    # Arquivo gerado
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # bytes
    file_hash = Column(String(64), nullable=True)  # SHA256

    # Status e processamento
    status = Column(String(20), nullable=False, default=ExportStatus.PENDING.value)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    # Estatísticas
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    success_records = Column(Integer, default=0)
    error_records = Column(Integer, default=0)
    warning_records = Column(Integer, default=0)

    # Transmissão (para eSocial, etc.)
    transmission_id = Column(String(100), nullable=True)  # Protocolo
    transmission_date = Column(DateTime, nullable=True)
    receipt_number = Column(String(100), nullable=True)  # Recibo
    receipt_date = Column(DateTime, nullable=True)

    # Erros e validações
    errors = Column(JSONB, default=list)
    # [{
    #   "record": 1,
    #   "field": "cpf",
    #   "code": "E001",
    #   "message": "CPF inválido",
    #   "employee_id": "..."
    # }]

    warnings = Column(JSONB, default=list)
    validation_results = Column(JSONB, default=dict)

    # Download
    download_url = Column(String(500), nullable=True)
    download_expires_at = Column(DateTime, nullable=True)
    download_count = Column(Integer, default=0)

    # Retry
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_error = Column(Text, nullable=True)

    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_payroll_exports_format", "export_format"),
        Index("ix_payroll_exports_status", "status"),
        Index("ix_payroll_exports_code", "export_code"),
        Index("ix_payroll_exports_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<PayrollExport {self.export_code} ({self.status})>"

    @property
    def is_completed(self) -> bool:
        """Verifica se exportação foi concluída."""
        return self.status in [
            ExportStatus.COMPLETED.value,
            ExportStatus.TRANSMITTED.value,
            ExportStatus.ACCEPTED.value,
        ]

    @property
    def is_failed(self) -> bool:
        """Verifica se exportação falhou."""
        return self.status in [
            ExportStatus.FAILED.value,
            ExportStatus.REJECTED.value,
        ]

    @property
    def can_retry(self) -> bool:
        """Verifica se pode tentar novamente."""
        return self.is_failed and self.retry_count < self.max_retries

    @property
    def progress_percentage(self) -> float:
        """Percentual de progresso."""
        if self.total_records == 0:
            return 0.0
        return (self.processed_records / self.total_records) * 100

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso."""
        if self.processed_records == 0:
            return 0.0
        return (self.success_records / self.processed_records) * 100

    @property
    def is_esocial_export(self) -> bool:
        """Verifica se é exportação eSocial."""
        return self.export_format == ExportFormat.ESOCIAL_XML.value

    @property
    def is_bank_export(self) -> bool:
        """Verifica se é exportação bancária."""
        return self.export_format in [
            ExportFormat.CNAB240.value,
            ExportFormat.CNAB400.value,
            ExportFormat.FEBRABAN.value,
        ]

    def start_processing(self) -> None:
        """Inicia processamento."""
        self.status = ExportStatus.PROCESSING.value
        self.started_at = datetime.utcnow()

    def complete(
        self,
        file_path: str,
        file_name: str,
        file_size: int,
        file_hash: str = None,
    ) -> None:
        """Marca como concluído."""
        self.status = ExportStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        self.file_path = file_path
        self.file_name = file_name
        self.file_size = file_size
        self.file_hash = file_hash
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.processing_time_ms = int(delta.total_seconds() * 1000)

    def fail(self, error: str) -> None:
        """Marca como falha."""
        self.status = ExportStatus.FAILED.value
        self.completed_at = datetime.utcnow()
        self.last_error = error
        self.retry_count += 1
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.processing_time_ms = int(delta.total_seconds() * 1000)

    def add_error(
        self,
        record: int,
        field: str,
        code: str,
        message: str,
        employee_id: str = None,
    ) -> None:
        """Adiciona erro."""
        if not self.errors:
            self.errors = []
        self.errors.append(
            {
                "record": record,
                "field": field,
                "code": code,
                "message": message,
                "employee_id": employee_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self.error_records += 1

    def add_warning(
        self,
        record: int,
        field: str,
        code: str,
        message: str,
    ) -> None:
        """Adiciona aviso."""
        if not self.warnings:
            self.warnings = []
        self.warnings.append(
            {
                "record": record,
                "field": field,
                "code": code,
                "message": message,
            }
        )
        self.warning_records += 1

    def record_transmission(
        self,
        transmission_id: str,
        receipt_number: str = None,
    ) -> None:
        """Registra transmissão."""
        self.status = ExportStatus.TRANSMITTED.value
        self.transmission_id = transmission_id
        self.transmission_date = datetime.utcnow()
        if receipt_number:
            self.receipt_number = receipt_number
            self.receipt_date = datetime.utcnow()
            self.status = ExportStatus.ACCEPTED.value

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "export_code": self.export_code,
            "name": self.name,
            "export_format": self.export_format,
            "status": self.status,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "total_records": self.total_records,
            "success_records": self.success_records,
            "error_records": self.error_records,
            "progress_percentage": round(self.progress_percentage, 2),
            "success_rate": round(self.success_rate, 2),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": (self.completed_at.isoformat() if self.completed_at else None),
        }
