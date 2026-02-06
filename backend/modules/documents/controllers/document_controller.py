"""
Document Intelligence Controller.

Endpoints da API REST para processamento de documentos,
OCR, extracao e validacao de dados.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field

from ..models.document import Document, DocumentSource, DocumentStatus, DocumentType
from ..models.extraction_template import TemplateCategory, TemplateStatus
from ..services.data_extractor import DataExtractor
from ..services.document_classifier import ClassificationResult, DocumentClassifier
from ..services.document_scanner import DocumentScanner, ScanConfig, ScanResult
from ..services.ocr_engine import OCRConfig, OCREngine, OCRProvider
from ..services.template_manager import TemplateManager
from ..services.validation_engine import ValidationConfig, ValidationEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Document Intelligence"])


# ============ Schemas ============


class DocumentUploadResponse(BaseModel):
    """Resposta de upload de documento."""

    success: bool
    document_id: Optional[str] = None
    status: str
    message: str
    warnings: List[str] = []


class DocumentResponse(BaseModel):
    """Resposta com dados do documento."""

    id: str
    name: str
    document_type: str
    status: str
    confidence_score: float
    needs_review: bool
    extracted_data: Dict[str, Any] = {}
    processing_summary: Dict[str, Any] = {}
    created_at: str


class ClassificationResponse(BaseModel):
    """Resposta de classificacao."""

    document_type: str
    confidence: float
    matched_keywords: List[str]
    matched_patterns: List[str]
    alternatives: List[Dict[str, Any]]


class ExtractionResponse(BaseModel):
    """Resposta de extracao."""

    document_id: str
    fields_extracted: int
    fields: List[Dict[str, Any]]
    confidence: float


class ValidationResponse(BaseModel):
    """Resposta de validacao."""

    document_id: str
    is_valid: bool
    overall_score: float
    total_fields: int
    fields_passed: int
    fields_failed: int
    errors: List[str]
    warnings: List[str]


class TemplateRequest(BaseModel):
    """Request para criacao de template."""

    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    document_type: str
    category: str = "other"
    detection_keywords: List[str] = []
    fields: List[Dict[str, Any]] = []


class TemplateResponse(BaseModel):
    """Resposta com dados do template."""

    id: str
    name: str
    document_type: str
    category: str
    status: str
    fields_count: int
    usage_count: int
    success_rate: float
    is_official: bool


class OCRResponse(BaseModel):
    """Resposta de OCR."""

    document_id: str
    provider: str
    pages: int
    words: int
    confidence: float
    processing_time_ms: int
    text_preview: str


class ProcessingRequest(BaseModel):
    """Request para processamento completo."""

    classify: bool = True
    extract: bool = True
    validate: bool = True
    template_id: Optional[str] = None


# ============ Dependencies ============


def get_scanner() -> DocumentScanner:
    """Retorna instancia do scanner."""
    config = ScanConfig()
    ocr_engine = get_ocr_engine()
    return DocumentScanner(config=config, ocr_engine=ocr_engine)


def get_ocr_engine() -> OCREngine:
    """Retorna instancia do OCR engine."""
    config = OCRConfig(
        primary_provider=OCRProvider.TESSERACT,
        languages=["por", "eng"],
    )
    return OCREngine(config=config)


def get_classifier() -> DocumentClassifier:
    """Retorna instancia do classificador."""
    return DocumentClassifier()


def get_extractor() -> DataExtractor:
    """Retorna instancia do extrator."""
    return DataExtractor()


def get_validator() -> ValidationEngine:
    """Retorna instancia do validador."""
    return ValidationEngine()


def get_template_manager() -> TemplateManager:
    """Retorna instancia do gerenciador de templates."""
    return TemplateManager()


# ============ Endpoints - Upload ============


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload de documento",
)
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str = Query(..., description="ID do tenant"),
    source: str = Query("upload", description="Origem do documento"),
    auto_process: bool = Query(True, description="Processar automaticamente"),
    scanner: DocumentScanner = Depends(get_scanner),
) -> DocumentUploadResponse:
    """
    Realiza upload e processamento inicial de documento.

    - **file**: Arquivo do documento (PDF, PNG, JPG, TIFF)
    - **tenant_id**: Identificador do tenant
    - **source**: Origem do documento (upload, api, email, scan)
    - **auto_process**: Se deve processar automaticamente
    """
    try:
        # Validar extensao
        allowed = ["pdf", "png", "jpg", "jpeg", "tiff", "bmp"]
        ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""
        if ext not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato nao suportado: {ext}. Use: {allowed}",
            )

        # Processar upload
        doc_source = DocumentSource(source) if source in [s.value for s in DocumentSource] else DocumentSource.UPLOAD

        result = await scanner.scan_file(
            file=file.file,
            filename=file.filename or "documento",
            tenant_id=tenant_id,
            source=doc_source,
        )

        if not result.success:
            return DocumentUploadResponse(
                success=False,
                status="error",
                message=result.error or "Erro no processamento",
                warnings=result.warnings,
            )

        return DocumentUploadResponse(
            success=True,
            document_id=result.document.id,
            status=result.document.status.value,
            message="Documento processado com sucesso",
            warnings=result.warnings,
        )

    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/upload/batch",
    response_model=List[DocumentUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload de multiplos documentos",
)
async def upload_batch(
    files: List[UploadFile] = File(...),
    tenant_id: str = Query(...),
    scanner: DocumentScanner = Depends(get_scanner),
) -> List[DocumentUploadResponse]:
    """Upload de multiplos documentos em lote."""
    results = []

    for file in files:
        try:
            result = await scanner.scan_file(
                file=file.file,
                filename=file.filename or "documento",
                tenant_id=tenant_id,
            )

            results.append(
                DocumentUploadResponse(
                    success=result.success,
                    document_id=result.document.id if result.document else None,
                    status=result.document.status.value if result.document else "error",
                    message="OK" if result.success else (result.error or "Erro"),
                    warnings=result.warnings,
                )
            )

        except Exception as e:
            results.append(
                DocumentUploadResponse(
                    success=False,
                    status="error",
                    message=str(e),
                )
            )

    return results


# ============ Endpoints - OCR ============


@router.post(
    "/{document_id}/ocr",
    response_model=OCRResponse,
    summary="Executar OCR em documento",
)
async def run_ocr(
    document_id: str,
    provider: str = Query("tesseract", description="Provider de OCR"),
    languages: str = Query("por,eng", description="Idiomas (separados por virgula)"),
    ocr_engine: OCREngine = Depends(get_ocr_engine),
) -> OCRResponse:
    """
    Executa OCR em um documento.

    - **document_id**: ID do documento
    - **provider**: Provider de OCR (tesseract, easyocr, google_vision)
    - **languages**: Lista de idiomas para OCR
    """
    try:
        # TODO: Buscar documento do banco
        # Por enquanto, simular
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint em desenvolvimento - requer integracao com banco de dados",
        )

    except Exception as e:
        logger.error(f"Erro no OCR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============ Endpoints - Classificacao ============


@router.post(
    "/{document_id}/classify",
    response_model=ClassificationResponse,
    summary="Classificar tipo de documento",
)
async def classify_document(
    document_id: str,
    classifier: DocumentClassifier = Depends(get_classifier),
    template_manager: TemplateManager = Depends(get_template_manager),
) -> ClassificationResponse:
    """
    Classifica o tipo de um documento.

    Utiliza keywords, padroes e templates para identificar
    automaticamente o tipo do documento.
    """
    try:
        # TODO: Buscar documento e resultado OCR do banco
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint em desenvolvimento - requer integracao com banco de dados",
        )

    except Exception as e:
        logger.error(f"Erro na classificacao: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============ Endpoints - Extracao ============


@router.post(
    "/{document_id}/extract",
    response_model=ExtractionResponse,
    summary="Extrair dados do documento",
)
async def extract_data(
    document_id: str,
    template_id: Optional[str] = Query(None, description="ID do template"),
    extractor: DataExtractor = Depends(get_extractor),
    template_manager: TemplateManager = Depends(get_template_manager),
) -> ExtractionResponse:
    """
    Extrai dados estruturados de um documento.

    - **document_id**: ID do documento
    - **template_id**: Template especifico (opcional)
    """
    try:
        # TODO: Buscar documento e resultado OCR do banco
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint em desenvolvimento - requer integracao com banco de dados",
        )

    except Exception as e:
        logger.error(f"Erro na extracao: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============ Endpoints - Validacao ============


@router.post(
    "/{document_id}/validate",
    response_model=ValidationResponse,
    summary="Validar dados extraidos",
)
async def validate_data(
    document_id: str,
    validator: ValidationEngine = Depends(get_validator),
) -> ValidationResponse:
    """
    Valida dados extraidos de um documento.

    Aplica validadores de formato, regras de negocio
    e consistencia nos campos extraidos.
    """
    try:
        # TODO: Buscar documento e campos extraidos do banco
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint em desenvolvimento - requer integracao com banco de dados",
        )

    except Exception as e:
        logger.error(f"Erro na validacao: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============ Endpoints - Processamento Completo ============


@router.post(
    "/{document_id}/process",
    response_model=DocumentResponse,
    summary="Processar documento completo",
)
async def process_document(
    document_id: str,
    request: ProcessingRequest,
    scanner: DocumentScanner = Depends(get_scanner),
    classifier: DocumentClassifier = Depends(get_classifier),
    extractor: DataExtractor = Depends(get_extractor),
    validator: ValidationEngine = Depends(get_validator),
    template_manager: TemplateManager = Depends(get_template_manager),
) -> DocumentResponse:
    """
    Processa documento com pipeline completo.

    1. OCR (se necessario)
    2. Classificacao (opcional)
    3. Extracao de dados (opcional)
    4. Validacao (opcional)
    """
    try:
        # TODO: Implementar pipeline completo
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint em desenvolvimento - requer integracao com banco de dados",
        )

    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ============ Endpoints - Templates ============


@router.get(
    "/templates",
    response_model=List[TemplateResponse],
    summary="Listar templates",
)
async def list_templates(
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    document_type: Optional[str] = Query(None, description="Filtrar por tipo"),
    include_builtin: bool = Query(True, description="Incluir templates builtin"),
    template_manager: TemplateManager = Depends(get_template_manager),
) -> List[TemplateResponse]:
    """Lista templates de extracao disponiveis."""
    try:
        cat = TemplateCategory(category) if category else None
        templates = template_manager.list_templates(
            category=cat,
            include_builtin=include_builtin,
        )

        if document_type:
            templates = [t for t in templates if t.document_type == document_type]

        return [
            TemplateResponse(
                id=t.id,
                name=t.name,
                document_type=t.document_type,
                category=t.category.value,
                status=t.status.value,
                fields_count=len(t.fields),
                usage_count=t.usage_count,
                success_rate=t.success_rate,
                is_official=t.is_official,
            )
            for t in templates
        ]

    except Exception as e:
        logger.error(f"Erro ao listar templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/templates/{template_id}",
    response_model=Dict[str, Any],
    summary="Obter template",
)
async def get_template(
    template_id: str,
    template_manager: TemplateManager = Depends(get_template_manager),
) -> Dict[str, Any]:
    """Obtem detalhes de um template."""
    template = template_manager.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template nao encontrado",
        )

    return template.to_dict()


@router.post(
    "/templates",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar template",
)
async def create_template(
    request: TemplateRequest,
    tenant_id: str = Query(...),
    template_manager: TemplateManager = Depends(get_template_manager),
) -> TemplateResponse:
    """Cria novo template de extracao."""
    try:
        from ..models.extraction_template import ExtractionTemplate, TemplateField

        # Converter campos
        fields = []
        for f in request.fields:
            fields.append(
                TemplateField(
                    name=f.get("name", ""),
                    label=f.get("label"),
                    field_type=f.get("field_type", "text"),
                    required=f.get("required", False),
                )
            )

        template = ExtractionTemplate(
            tenant_id=tenant_id,
            name=request.name,
            description=request.description,
            document_type=request.document_type,
            category=TemplateCategory(request.category),
            detection_keywords=request.detection_keywords,
            fields=fields,
        )

        created = template_manager.create_template(template)

        return TemplateResponse(
            id=created.id,
            name=created.name,
            document_type=created.document_type,
            category=created.category.value,
            status=created.status.value,
            fields_count=len(created.fields),
            usage_count=0,
            success_rate=0.0,
            is_official=False,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Erro ao criar template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover template",
)
async def delete_template(
    template_id: str,
    template_manager: TemplateManager = Depends(get_template_manager),
) -> None:
    """Remove um template customizado."""
    try:
        deleted = template_manager.delete_template(template_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template nao encontrado",
            )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============ Endpoints - Utilitarios ============


@router.get(
    "/types",
    response_model=List[Dict[str, str]],
    summary="Listar tipos de documentos",
)
async def list_document_types() -> List[Dict[str, str]]:
    """Lista todos os tipos de documentos suportados."""
    return [{"type": t.value, "name": t.name} for t in DocumentType]


@router.get(
    "/providers",
    response_model=Dict[str, Any],
    summary="Listar providers OCR",
)
async def list_ocr_providers(
    ocr_engine: OCREngine = Depends(get_ocr_engine),
) -> Dict[str, Any]:
    """Lista providers de OCR disponiveis."""
    return ocr_engine.get_provider_info()


@router.get(
    "/stats",
    response_model=Dict[str, Any],
    summary="Estatisticas de armazenamento",
)
async def get_storage_stats(
    tenant_id: str = Query(...),
    scanner: DocumentScanner = Depends(get_scanner),
) -> Dict[str, Any]:
    """Obtem estatisticas de armazenamento do tenant."""
    return scanner.get_storage_stats(tenant_id)


@router.post(
    "/validate/cpf",
    response_model=Dict[str, bool],
    summary="Validar CPF",
)
async def validate_cpf(
    cpf: str = Query(..., description="CPF a validar"),
    validator: ValidationEngine = Depends(get_validator),
) -> Dict[str, bool]:
    """Valida um CPF."""
    from ..models.validation_result import ValidationType

    is_valid = validator.validate_single(cpf, ValidationType.CPF)
    return {"valid": is_valid, "cpf": cpf}


@router.post(
    "/validate/cnpj",
    response_model=Dict[str, bool],
    summary="Validar CNPJ",
)
async def validate_cnpj(
    cnpj: str = Query(..., description="CNPJ a validar"),
    validator: ValidationEngine = Depends(get_validator),
) -> Dict[str, bool]:
    """Valida um CNPJ."""
    from ..models.validation_result import ValidationType

    is_valid = validator.validate_single(cnpj, ValidationType.CNPJ)
    return {"valid": is_valid, "cnpj": cnpj}
