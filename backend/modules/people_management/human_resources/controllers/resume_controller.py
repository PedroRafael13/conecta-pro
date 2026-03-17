"""
Controller de Parsing de Currículos — PDF/DOCX + IA.

Endpoints para upload e análise de currículos usando ResumeParserService.
"""

import logging
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from core.auth.dependencies import CurrentActiveUser
from modules.people_management.human_resources.services.resume_parser_service import (
    ResumeParserService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recruitment/resume", tags=["RH - Currículos"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/parse")
async def parse_resume(
    file: UploadFile = File(..., description="Currículo em PDF, DOCX ou TXT"),
    current_user: CurrentActiveUser = None,
) -> Any:
    """Faz parsing de currículo PDF/DOCX usando IA.

    Extrai dados estruturados: dados pessoais, experiência,
    formação, habilidades, idiomas e certificações.

    Se a API Claude estiver configurada, usa IA para análise profunda.
    Caso contrário, usa fallback via regex.
    """
    if not file.filename:
        raise HTTPException(400, "Nome do arquivo é obrigatório.")

    filename = file.filename.lower()
    if not any(filename.endswith(ext) for ext in (".pdf", ".docx", ".doc", ".txt")):
        raise HTTPException(400, "Formato não suportado. Use PDF, DOCX ou TXT.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"Arquivo muito grande. Máximo {MAX_FILE_SIZE // (1024 * 1024)}MB.")

    if len(content) == 0:
        raise HTTPException(400, "Arquivo vazio.")

    try:
        result = ResumeParserService.parse_resume(content, file.filename)
    except ImportError as e:
        raise HTTPException(422, f"Dependência não disponível: {e}")
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error("Erro ao parsear currículo %s: %s", file.filename, e)
        raise HTTPException(500, "Erro ao processar currículo.")

    return {
        "filename": file.filename,
        "file_size": len(content),
        "parsed_data": result,
    }


@router.post("/parse-text")
async def parse_resume_text(
    text: str,
    current_user: CurrentActiveUser = None,
) -> Any:
    """Analisa texto de currículo já extraído (sem upload de arquivo).

    Útil quando o texto já foi extraído previamente.
    """
    if not text or len(text.strip()) < 50:
        raise HTTPException(400, "Texto do currículo muito curto (mínimo 50 caracteres).")

    result = ResumeParserService.analyze_with_claude(text)
    return {"parsed_data": result}
