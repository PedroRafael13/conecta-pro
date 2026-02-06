"""OCR Controller - Endpoints REST para processamento OCR.

Sprint 39 - Document OCR.

Endpoints:
- POST /upload - Upload de documento
- POST /process/{scan_id} - Processa documento
- GET /scans - Lista scans
- GET /scans/{scan_id} - Detalhes do scan
- GET /scans/{scan_id}/fields - Campos extraidos
- POST /scans/{scan_id}/fields/{field_id}/correct - Corrige campo
- GET /scans/{scan_id}/validation - Resultado de validacao
- POST /templates - Cria template
- GET /templates - Lista templates
"""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from core.security.file_validator import ocr_file_validator
from modules.ai.ocr.models.document_scan import DocumentScanStatus, DocumentScanType
from modules.ai.ocr.schemas.ocr_schemas import (
    BatchProcessRequest,
    DocumentScanList,
    DocumentScanResponse,
    DocumentScanUpdate,
    DocumentTemplateCreate,
    DocumentTemplateResponse,
    ExtractedFieldCorrection,
    ExtractedFieldResponse,
    ProcessDocumentRequest,
    ProcessDocumentResponse,
    ValidationResultResponse,
)
from modules.ai.ocr.services.extraction_service import ExtractionService
from modules.ai.ocr.services.ocr_service import OCRService
from modules.ai.ocr.services.validation_service import ValidationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ocr", tags=["OCR"])

# Servicos (em producao seriam injetados via DI)
ocr_service = OCRService()
extraction_service = ExtractionService()
validation_service = ValidationService()

# Storage em memoria para demo (em producao usaria banco de dados)
_scans: dict = {}
_results: dict = {}
_fields: dict = {}
_templates: dict = {}
_validations: dict = {}


# ============================================================
# Upload e Processamento
# ============================================================


@router.post(
    "/upload",
    response_model=DocumentScanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload de documento",
)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentScanType | None = None,
    template_id: str | None = None,
    tags: str | None = Query(None, description="Tags separadas por virgula"),
    priority: str | None = "normal",
):
    """Faz upload de documento para processamento OCR.

    Args:
        file: Arquivo para upload
        document_type: Tipo de documento (opcional)
        template_id: Template a usar (opcional)
        tags: Tags separadas por virgula
        priority: Prioridade do processamento

    Returns:
        Dados do scan criado
    """
    # Validar arquivo (tamanho, tipo MIME, magic number)
    content = await ocr_file_validator.validate_file(file)

    # Gera IDs
    scan_id = f"scan_{uuid.uuid4().hex[:12]}"
    scan_uuid = str(uuid.uuid4())

    file_size = len(content)

    # Cria registro do scan
    scan = {
        "id": scan_uuid,
        "scan_id": scan_id,
        "file_name": file.filename,
        "file_size": file_size,
        "mime_type": file.content_type,
        "document_type": document_type.value if document_type else None,
        "template_id": template_id,
        "status": DocumentScanStatus.UPLOADED.value,
        "page_count": 1,
        "tags": tags.split(",") if tags else [],
        "priority": priority,
        "requires_review": False,
        "fields_extracted": 0,
        "fields_validated": 0,
        "fields_with_errors": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "_content": content,  # Armazena conteudo para processamento
    }

    _scans[scan_id] = scan

    logger.info(f"Documento uploaded: {scan_id} - {file.filename}")

    return DocumentScanResponse(**{k: v for k, v in scan.items() if not k.startswith("_")})


@router.post(
    "/process/{scan_id}",
    response_model=ProcessDocumentResponse,
    summary="Processa documento",
)
async def process_document(
    scan_id: str,
    request: ProcessDocumentRequest | None = None,
):
    """Processa documento com OCR.

    Args:
        scan_id: ID do scan
        request: Opcoes de processamento

    Returns:
        Resultado do processamento
    """
    if scan_id not in _scans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan nao encontrado: {scan_id}",
        )

    scan = _scans[scan_id]
    request = request or ProcessDocumentRequest()

    start_time = datetime.utcnow()

    # Atualiza status
    scan["status"] = DocumentScanStatus.PROCESSING.value

    try:
        # Processa OCR
        content = scan.get("_content", b"dummy content")
        ocr_result = ocr_service.process_image(
            content,
            provider=request.provider,
            language=request.language,
        )

        # Armazena resultado OCR
        result_id = f"result_{uuid.uuid4().hex[:12]}"
        ocr_record = {
            "id": str(uuid.uuid4()),
            "result_id": result_id,
            "scan_id": scan_id,
            "provider": ocr_result.get("provider", "tesseract"),
            "page_number": 1,
            "raw_text": ocr_result.get("raw_text", ""),
            "text_length": len(ocr_result.get("raw_text", "")),
            "overall_confidence": ocr_result.get("overall_confidence"),
            "processing_time_ms": ocr_result.get("processing_time_ms", 0),
            "tables": ocr_result.get("tables", []),
            "key_value_pairs": ocr_result.get("key_value_pairs", []),
            "has_errors": False,
            "errors": [],
            "warnings": [],
            "created_at": datetime.utcnow(),
        }
        _results[scan_id] = ocr_record

        # Atualiza scan com dados OCR
        scan["ocr_provider"] = ocr_record["provider"]
        scan["ocr_confidence"] = ocr_record["overall_confidence"]
        scan["status"] = DocumentScanStatus.EXTRACTING.value

        # Detecta tipo de documento se necessario
        if request.auto_detect_type and not scan.get("document_type"):
            detected_type, confidence = ocr_service.detect_document_type(ocr_result)
            scan["detected_type"] = detected_type
            scan["type_confidence"] = confidence

        # Extrai campos
        template = _templates.get(request.template_id) if request.template_id else None
        extracted_fields = extraction_service.extract_fields(ocr_result, template)

        # Armazena campos
        _fields[scan_id] = []
        for field in extracted_fields:
            field["id"] = str(uuid.uuid4())
            field["scan_id"] = scan_id
            field["validation_status"] = "pending"
            field["was_corrected"] = False
            field["is_required"] = False
            field["is_key_field"] = False
            field["created_at"] = datetime.utcnow()
            _fields[scan_id].append(field)

        scan["fields_extracted"] = len(extracted_fields)
        scan["status"] = DocumentScanStatus.VALIDATING.value

        # Valida campos (se nao pulado)
        validation_result = None
        if not request.skip_validation:
            validation_result = validation_service.validate_fields(
                extracted_fields,
                document_type=scan.get("document_type"),
            )

            # Armazena validacao
            validation_result["id"] = str(uuid.uuid4())
            validation_result["scan_id"] = scan_id
            validation_result["created_at"] = datetime.utcnow()
            _validations[scan_id] = validation_result

            scan["fields_validated"] = validation_result.get("valid_fields", 0)
            scan["fields_with_errors"] = validation_result.get("invalid_fields", 0)
            scan["validation_score"] = validation_result.get("overall_score")
            scan["requires_review"] = validation_result.get("needs_review", False)

        # Finaliza processamento
        end_time = datetime.utcnow()
        processing_time_ms = int((end_time - start_time).total_seconds() * 1000)

        scan["status"] = DocumentScanStatus.COMPLETED.value
        scan["updated_at"] = end_time

        logger.info(f"Documento processado: {scan_id} em {processing_time_ms}ms")

        # Prepara resposta
        field_responses = [
            ExtractedFieldResponse(**{k: v for k, v in f.items() if not k.startswith("_")})
            for f in _fields.get(scan_id, [])
        ]

        return ProcessDocumentResponse(
            scan_id=scan_id,
            status=scan["status"],
            document_type=scan.get("detected_type") or scan.get("document_type"),
            ocr_confidence=scan.get("ocr_confidence"),
            fields_extracted=scan.get("fields_extracted", 0),
            validation_status=validation_result.get("status") if validation_result else None,
            validation_score=scan.get("validation_score"),
            requires_review=scan.get("requires_review", False),
            processing_time_ms=processing_time_ms,
            fields=field_responses,
            errors=validation_result.get("errors", []) if validation_result else [],
            warnings=validation_result.get("warnings", []) if validation_result else [],
        )

    except Exception as e:
        logger.error(f"Erro ao processar documento {scan_id}: {e}")
        scan["status"] = DocumentScanStatus.FAILED.value
        scan["last_error"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no processamento: {str(e)}",
        )


@router.post(
    "/batch",
    summary="Processamento em lote",
)
async def batch_process(request: BatchProcessRequest):
    """Processa multiplos documentos em lote.

    Args:
        request: Configuracao do lote

    Returns:
        Status do processamento
    """
    results = []

    for scan_id in request.scan_ids:
        try:
            result = await process_document(
                scan_id,
                ProcessDocumentRequest(
                    provider=request.provider,
                    language=request.language,
                    template_id=request.template_id,
                ),
            )
            results.append(
                {
                    "scan_id": scan_id,
                    "status": "success",
                    "fields_extracted": result.fields_extracted,
                }
            )
        except HTTPException as e:
            results.append(
                {
                    "scan_id": scan_id,
                    "status": "error",
                    "error": e.detail,
                }
            )

    return {
        "total": len(request.scan_ids),
        "processed": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results,
    }


# ============================================================
# Scans
# ============================================================


@router.get(
    "/scans",
    response_model=DocumentScanList,
    summary="Lista scans",
)
async def list_scans(
    status: DocumentScanStatus | None = None,
    document_type: DocumentScanType | None = None,
    requires_review: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Lista documentos escaneados.

    Args:
        status: Filtro por status
        document_type: Filtro por tipo
        requires_review: Filtro por revisao
        page: Pagina
        page_size: Itens por pagina

    Returns:
        Lista paginada de scans
    """
    # Filtra scans
    items = list(_scans.values())

    if status:
        items = [s for s in items if s.get("status") == status.value]

    if document_type:
        items = [s for s in items if s.get("document_type") == document_type.value]

    if requires_review is not None:
        items = [s for s in items if s.get("requires_review") == requires_review]

    # Ordena por data (mais recente primeiro)
    items.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)

    # Pagina
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    items = items[start:end]

    # Remove campos internos
    clean_items = [{k: v for k, v in s.items() if not k.startswith("_")} for s in items]

    return DocumentScanList(
        items=[DocumentScanResponse(**s) for s in clean_items],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get(
    "/scans/{scan_id}",
    response_model=DocumentScanResponse,
    summary="Detalhes do scan",
)
async def get_scan(scan_id: str):
    """Obtem detalhes de um scan.

    Args:
        scan_id: ID do scan

    Returns:
        Dados do scan
    """
    if scan_id not in _scans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan nao encontrado: {scan_id}",
        )

    scan = _scans[scan_id]
    clean_scan = {k: v for k, v in scan.items() if not k.startswith("_")}
    return DocumentScanResponse(**clean_scan)


@router.patch(
    "/scans/{scan_id}",
    response_model=DocumentScanResponse,
    summary="Atualiza scan",
)
async def update_scan(scan_id: str, update: DocumentScanUpdate):
    """Atualiza dados de um scan.

    Args:
        scan_id: ID do scan
        update: Dados para atualizar

    Returns:
        Scan atualizado
    """
    if scan_id not in _scans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan nao encontrado: {scan_id}",
        )

    scan = _scans[scan_id]

    # Atualiza campos
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            scan[key] = value.value if hasattr(value, "value") else value

    scan["updated_at"] = datetime.utcnow()

    clean_scan = {k: v for k, v in scan.items() if not k.startswith("_")}
    return DocumentScanResponse(**clean_scan)


@router.delete(
    "/scans/{scan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove scan",
)
async def delete_scan(scan_id: str):
    """Remove um scan.

    Args:
        scan_id: ID do scan
    """
    if scan_id not in _scans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan nao encontrado: {scan_id}",
        )

    del _scans[scan_id]
    _results.pop(scan_id, None)
    _fields.pop(scan_id, None)
    _validations.pop(scan_id, None)


# ============================================================
# Campos Extraidos
# ============================================================


@router.get(
    "/scans/{scan_id}/fields",
    response_model=list[ExtractedFieldResponse],
    summary="Lista campos extraidos",
)
async def get_extracted_fields(scan_id: str):
    """Lista campos extraidos de um scan.

    Args:
        scan_id: ID do scan

    Returns:
        Lista de campos
    """
    if scan_id not in _scans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan nao encontrado: {scan_id}",
        )

    fields = _fields.get(scan_id, [])
    return [ExtractedFieldResponse(**f) for f in fields]


@router.post(
    "/scans/{scan_id}/fields/{field_id}/correct",
    response_model=ExtractedFieldResponse,
    summary="Corrige campo",
)
async def correct_field(
    scan_id: str,
    field_id: str,
    correction: ExtractedFieldCorrection,
):
    """Corrige valor de um campo extraido.

    Args:
        scan_id: ID do scan
        field_id: ID do campo
        correction: Dados da correcao

    Returns:
        Campo atualizado
    """
    if scan_id not in _scans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan nao encontrado: {scan_id}",
        )

    fields = _fields.get(scan_id, [])
    field = next((f for f in fields if f.get("field_id") == field_id), None)

    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campo nao encontrado: {field_id}",
        )

    # Aplica correcao
    field["original_value"] = field.get("extracted_value")
    field["extracted_value"] = correction.corrected_value
    field["normalized_value"] = correction.corrected_value
    field["was_corrected"] = True
    field["correction_reason"] = correction.correction_reason
    field["validation_status"] = "corrected"

    return ExtractedFieldResponse(**field)


# ============================================================
# Validacao
# ============================================================


@router.get(
    "/scans/{scan_id}/validation",
    response_model=ValidationResultResponse,
    summary="Resultado de validacao",
)
async def get_validation_result(scan_id: str):
    """Obtem resultado de validacao de um scan.

    Args:
        scan_id: ID do scan

    Returns:
        Resultado da validacao
    """
    if scan_id not in _scans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan nao encontrado: {scan_id}",
        )

    validation = _validations.get(scan_id)
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validacao nao encontrada (documento pode nao ter sido processado)",
        )

    return ValidationResultResponse(**validation)


@router.post(
    "/scans/{scan_id}/revalidate",
    response_model=ValidationResultResponse,
    summary="Revalida documento",
)
async def revalidate_document(scan_id: str):
    """Revalida campos de um documento (apos correcoes).

    Args:
        scan_id: ID do scan

    Returns:
        Novo resultado de validacao
    """
    if scan_id not in _scans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan nao encontrado: {scan_id}",
        )

    fields = _fields.get(scan_id, [])
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo extraido para validar",
        )

    # Revalida
    validation_result = validation_service.validate_fields(
        fields,
        document_type=_scans[scan_id].get("document_type"),
    )

    validation_result["id"] = str(uuid.uuid4())
    validation_result["scan_id"] = scan_id
    validation_result["created_at"] = datetime.utcnow()

    _validations[scan_id] = validation_result

    # Atualiza scan
    scan = _scans[scan_id]
    scan["fields_validated"] = validation_result.get("valid_fields", 0)
    scan["fields_with_errors"] = validation_result.get("invalid_fields", 0)
    scan["validation_score"] = validation_result.get("overall_score")
    scan["requires_review"] = validation_result.get("needs_review", False)
    scan["updated_at"] = datetime.utcnow()

    return ValidationResultResponse(**validation_result)


# ============================================================
# Templates
# ============================================================


@router.post(
    "/templates",
    response_model=DocumentTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria template",
)
async def create_template(template: DocumentTemplateCreate):
    """Cria template de documento.

    Args:
        template: Dados do template

    Returns:
        Template criado
    """
    template_id = f"template_{uuid.uuid4().hex[:12]}"

    template_data = {
        "id": str(uuid.uuid4()),
        "template_id": template_id,
        "name": template.name,
        "description": template.description,
        "document_type": template.document_type.value,
        "document_subtype": template.document_subtype,
        "version": "1.0.0",
        "detection_keywords": template.detection_keywords,
        "detection_threshold": template.detection_threshold,
        "times_used": 0,
        "success_rate": None,
        "avg_confidence": None,
        "is_latest": True,
        "tags": template.tags,
        "category": template.category,
        "active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "_fields": [f.model_dump() for f in template.fields],
        "_validation_rules": template.validation_rules,
        "_field_mapping": template.field_mapping,
    }

    _templates[template_id] = template_data

    logger.info(f"Template criado: {template_id} - {template.name}")

    clean_template = {k: v for k, v in template_data.items() if not k.startswith("_")}
    return DocumentTemplateResponse(**clean_template)


@router.get(
    "/templates",
    response_model=list[DocumentTemplateResponse],
    summary="Lista templates",
)
async def list_templates(
    document_type: DocumentScanType | None = None,
    active: bool | None = True,
):
    """Lista templates de documento.

    Args:
        document_type: Filtro por tipo
        active: Filtro por status

    Returns:
        Lista de templates
    """
    templates = list(_templates.values())

    if document_type:
        templates = [t for t in templates if t.get("document_type") == document_type.value]

    if active is not None:
        templates = [t for t in templates if t.get("active") == active]

    clean_templates = [{k: v for k, v in t.items() if not k.startswith("_")} for t in templates]

    return [DocumentTemplateResponse(**t) for t in clean_templates]


@router.get(
    "/templates/{template_id}",
    response_model=DocumentTemplateResponse,
    summary="Detalhes do template",
)
async def get_template(template_id: str):
    """Obtem detalhes de um template.

    Args:
        template_id: ID do template

    Returns:
        Dados do template
    """
    if template_id not in _templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template nao encontrado: {template_id}",
        )

    template = _templates[template_id]
    clean_template = {k: v for k, v in template.items() if not k.startswith("_")}
    return DocumentTemplateResponse(**clean_template)


# ============================================================
# Estatisticas
# ============================================================


@router.get(
    "/stats",
    summary="Estatisticas OCR",
)
async def get_stats():
    """Retorna estatisticas do servico OCR.

    Returns:
        Estatisticas
    """
    scans = list(_scans.values())

    # Conta por status
    by_status = {}
    for scan in scans:
        status = scan.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1

    # Conta por tipo
    by_type = {}
    for scan in scans:
        doc_type = scan.get("document_type") or scan.get("detected_type") or "unknown"
        by_type[doc_type] = by_type.get(doc_type, 0) + 1

    # Metricas de qualidade
    confidences = [s.get("ocr_confidence", 0) for s in scans if s.get("ocr_confidence")]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0

    validation_scores = [s.get("validation_score", 0) for s in scans if s.get("validation_score")]
    avg_validation = sum(validation_scores) / len(validation_scores) if validation_scores else 0

    return {
        "total_scans": len(scans),
        "by_status": by_status,
        "by_type": by_type,
        "requires_review": len([s for s in scans if s.get("requires_review")]),
        "avg_ocr_confidence": round(avg_confidence, 3),
        "avg_validation_score": round(avg_validation, 3),
        "total_templates": len(_templates),
    }
