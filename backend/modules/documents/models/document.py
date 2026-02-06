"""
Modelo de Documento.

Define o modelo principal para documentos processados pelo sistema,
incluindo metadados, status de processamento e resultados de OCR.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class DocumentType(str, Enum):
    """Tipos de documentos suportados."""

    # Financeiros
    BOLETO = "boleto"
    NFE = "nfe"  # Nota Fiscal Eletronica
    NFSE = "nfse"  # Nota Fiscal de Servico
    FATURA = "fatura"
    RECIBO = "recibo"
    EXTRATO = "extrato"
    COMPROVANTE_PAGAMENTO = "comprovante_pagamento"

    # Pessoais
    RG = "rg"
    CPF = "cpf"
    CNH = "cnh"
    PASSAPORTE = "passaporte"
    CTPS = "ctps"  # Carteira de Trabalho
    TITULO_ELEITOR = "titulo_eleitor"
    CERTIDAO_NASCIMENTO = "certidao_nascimento"
    CERTIDAO_CASAMENTO = "certidao_casamento"

    # Endereco
    COMPROVANTE_ENDERECO = "comprovante_endereco"
    CONTA_LUZ = "conta_luz"
    CONTA_AGUA = "conta_agua"
    CONTA_GAS = "conta_gas"
    CONTA_TELEFONE = "conta_telefone"

    # Trabalhistas
    HOLERITE = "holerite"
    CONTRATO_TRABALHO = "contrato_trabalho"
    RESCISAO = "rescisao"
    FERIAS = "ferias"
    ASO = "aso"  # Atestado de Saude Ocupacional

    # Empresariais
    CONTRATO = "contrato"
    PROPOSTA = "proposta"
    CNPJ = "cnpj"
    CONTRATO_SOCIAL = "contrato_social"
    PROCURACAO = "procuracao"
    ATA_ASSEMBLEIA = "ata_assembleia"

    # Outros
    FORMULARIO = "formulario"
    DECLARACAO = "declaracao"
    ATESTADO = "atestado"
    LAUDO = "laudo"
    OUTRO = "outro"
    DESCONHECIDO = "desconhecido"


class DocumentStatus(str, Enum):
    """Status do documento no sistema."""

    UPLOADED = "uploaded"  # Arquivo enviado
    QUEUED = "queued"  # Na fila de processamento
    PREPROCESSING = "preprocessing"  # Pre-processamento de imagem
    OCR_PROCESSING = "ocr_processing"  # OCR em andamento
    CLASSIFYING = "classifying"  # Classificando tipo
    EXTRACTING = "extracting"  # Extraindo dados
    VALIDATING = "validating"  # Validando dados
    REVIEW_NEEDED = "review_needed"  # Precisa revisao manual
    COMPLETED = "completed"  # Processamento concluido
    FAILED = "failed"  # Falha no processamento
    ARCHIVED = "archived"  # Arquivado


class DocumentSource(str, Enum):
    """Origem do documento."""

    UPLOAD = "upload"  # Upload manual
    EMAIL = "email"  # Recebido por email
    API = "api"  # Via API
    SCAN = "scan"  # Escaneado
    MOBILE = "mobile"  # App mobile
    INTEGRATION = "integration"  # Integracao externa
    WEBHOOK = "webhook"  # Via webhook


class ProcessingStatus(str, Enum):
    """Status de cada etapa de processamento."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ProcessingStep:
    """Representa uma etapa de processamento."""

    name: str
    status: ProcessingStatus = ProcessingStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def start(self) -> None:
        """Marca inicio da etapa."""
        self.status = ProcessingStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()

    def complete(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Marca conclusao da etapa."""
        self.status = ProcessingStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_ms = int(
                (self.completed_at - self.started_at).total_seconds() * 1000
            )
        if metadata:
            self.metadata.update(metadata)

    def fail(self, error: str) -> None:
        """Marca falha da etapa."""
        self.status = ProcessingStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error = error
        if self.started_at:
            self.duration_ms = int(
                (self.completed_at - self.started_at).total_seconds() * 1000
            )


@dataclass
class ImageMetadata:
    """Metadados da imagem do documento."""

    width: int
    height: int
    format: str  # PNG, JPEG, PDF, TIFF
    size_bytes: int
    dpi: Optional[int] = None
    color_mode: Optional[str] = None  # RGB, GRAYSCALE, BINARY
    pages: int = 1
    orientation: Optional[str] = None  # PORTRAIT, LANDSCAPE
    quality_score: Optional[float] = None  # 0-100
    is_skewed: bool = False
    skew_angle: Optional[float] = None
    has_noise: bool = False
    is_blurry: bool = False


@dataclass
class Document:
    """
    Representa um documento no sistema.

    Attributes:
        id: Identificador unico
        tenant_id: ID do tenant
        name: Nome do arquivo
        document_type: Tipo do documento
        status: Status atual
        source: Origem do documento
        file_path: Caminho do arquivo original
        file_hash: Hash SHA-256 do arquivo
        image_metadata: Metadados da imagem
        processing_steps: Etapas de processamento
        confidence_score: Confianca geral (0-100)
        needs_review: Se precisa revisao manual
        review_notes: Notas de revisao
        reviewed_by: Usuario que revisou
        reviewed_at: Data da revisao
        tags: Tags do documento
        metadata: Metadados adicionais
        created_at: Data de criacao
        updated_at: Data de atualizacao
        processed_at: Data de processamento
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    name: str = ""
    original_name: str = ""
    document_type: DocumentType = DocumentType.DESCONHECIDO
    predicted_type: Optional[DocumentType] = None
    type_confidence: float = 0.0
    status: DocumentStatus = DocumentStatus.UPLOADED
    source: DocumentSource = DocumentSource.UPLOAD

    # Arquivo
    file_path: str = ""
    file_url: Optional[str] = None
    file_hash: str = ""
    mime_type: str = ""
    file_size: int = 0

    # Imagem
    image_metadata: Optional[ImageMetadata] = None
    preprocessed_path: Optional[str] = None
    thumbnail_path: Optional[str] = None

    # Processamento
    processing_steps: List[ProcessingStep] = field(default_factory=list)
    current_step: Optional[str] = None
    total_processing_time_ms: int = 0

    # Resultados
    ocr_result_id: Optional[str] = None
    extracted_fields_count: int = 0
    validation_passed: bool = False
    confidence_score: float = 0.0

    # Revisao
    needs_review: bool = False
    review_reason: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    # Organizacao
    folder_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    reference_id: Optional[str] = None  # ID de referencia externa
    reference_type: Optional[str] = None  # Tipo de referencia (lead, contract, etc)

    # Metadados
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_data: Dict[str, Any] = field(default_factory=dict)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    # Controle
    is_active: bool = True
    is_archived: bool = False
    version: int = 1
    parent_id: Optional[str] = None  # Para versoes de documento

    def __post_init__(self) -> None:
        """Inicializa etapas de processamento padrao."""
        if not self.processing_steps:
            self.processing_steps = [
                ProcessingStep(name="upload"),
                ProcessingStep(name="preprocessing"),
                ProcessingStep(name="ocr"),
                ProcessingStep(name="classification"),
                ProcessingStep(name="extraction"),
                ProcessingStep(name="validation"),
            ]

    def get_step(self, name: str) -> Optional[ProcessingStep]:
        """Obtem etapa por nome."""
        for step in self.processing_steps:
            if step.name == name:
                return step
        return None

    def start_step(self, name: str) -> bool:
        """Inicia uma etapa de processamento."""
        step = self.get_step(name)
        if step:
            step.start()
            self.current_step = name
            self.updated_at = datetime.utcnow()
            return True
        return False

    def complete_step(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Completa uma etapa de processamento."""
        step = self.get_step(name)
        if step:
            step.complete(metadata)
            self.updated_at = datetime.utcnow()
            self._update_total_time()
            return True
        return False

    def fail_step(self, name: str, error: str) -> bool:
        """Marca falha em uma etapa."""
        step = self.get_step(name)
        if step:
            step.fail(error)
            self.status = DocumentStatus.FAILED
            self.updated_at = datetime.utcnow()
            return True
        return False

    def _update_total_time(self) -> None:
        """Atualiza tempo total de processamento."""
        self.total_processing_time_ms = sum(
            step.duration_ms or 0
            for step in self.processing_steps
            if step.duration_ms
        )

    def mark_for_review(self, reason: str) -> None:
        """Marca documento para revisao manual."""
        self.needs_review = True
        self.review_reason = reason
        self.status = DocumentStatus.REVIEW_NEEDED
        self.updated_at = datetime.utcnow()

    def complete_review(self, reviewed_by: str, notes: Optional[str] = None) -> None:
        """Completa revisao do documento."""
        self.needs_review = False
        self.reviewed_by = reviewed_by
        self.reviewed_at = datetime.utcnow()
        self.review_notes = notes
        self.status = DocumentStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def complete_processing(self) -> None:
        """Marca processamento como concluido."""
        self.status = DocumentStatus.COMPLETED
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Arquiva o documento."""
        self.is_archived = True
        self.status = DocumentStatus.ARCHIVED
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Adiciona tag ao documento."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove tag do documento."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def set_extracted_data(self, data: Dict[str, Any]) -> None:
        """Define dados extraidos."""
        self.extracted_data = data
        self.extracted_fields_count = len(data)
        self.updated_at = datetime.utcnow()

    def get_processing_summary(self) -> Dict[str, Any]:
        """Retorna resumo do processamento."""
        return {
            "status": self.status.value,
            "document_type": self.document_type.value,
            "confidence_score": self.confidence_score,
            "total_time_ms": self.total_processing_time_ms,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status.value,
                    "duration_ms": step.duration_ms,
                    "error": step.error,
                }
                for step in self.processing_steps
            ],
            "needs_review": self.needs_review,
            "extracted_fields": self.extracted_fields_count,
            "validation_passed": self.validation_passed,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "original_name": self.original_name,
            "document_type": self.document_type.value,
            "predicted_type": (
                self.predicted_type.value if self.predicted_type else None
            ),
            "type_confidence": self.type_confidence,
            "status": self.status.value,
            "source": self.source.value,
            "file_path": self.file_path,
            "file_url": self.file_url,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
            "confidence_score": self.confidence_score,
            "needs_review": self.needs_review,
            "review_reason": self.review_reason,
            "tags": self.tags,
            "extracted_data": self.extracted_data,
            "processing_summary": self.get_processing_summary(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }
