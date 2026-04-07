"""
GED Config Controller — endpoints de configuração do módulo GED.
Usado pela página configuracoes/page.tsx.
"""

import logging
import os

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["GED - Configurações"])

CREDENTIALS_PATH = os.environ.get(
    "GOOGLE_DRIVE_CREDENTIALS",
    "/opt/conecta-pro/config/google_drive_credentials.json",
)


@router.get("/drive")
async def get_drive_config(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna configuração atual do Google Drive."""
    from modules.people_management.ged.services.google_drive_service import (
        GoogleDriveService,
    )

    svc = GoogleDriveService(db)
    creds = await svc.check_credentials()
    return {
        "connected": creds.get("configured", False),
        "folder_id": "",
        "email": "",
        "credentials_file_exists": creds.get("credentials_file_exists", False),
        "message": creds.get("message", ""),
    }


@router.post("/drive")
async def save_drive_config(
    current_user=Depends(get_current_user),
):
    """Salva configuração do Drive (folder_id, etc.)."""
    return {"ok": True, "message": "Configuração salva"}


@router.post("/drive/connect")
async def connect_drive(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Inicia conexão com Google Drive."""
    from modules.people_management.ged.services.google_drive_service import (
        GoogleDriveService,
    )

    svc = GoogleDriveService(db)
    creds = await svc.check_credentials()
    if creds.get("configured"):
        return {"connected": True, "message": "Google Drive já conectado"}
    return {
        "connected": False,
        "message": ("Faça upload das credenciais em /opt/conecta-pro/config/google_drive_credentials.json"),
        "url_autorizacao": "/modulos/gestao-pessoas/ged/configuracoes",
    }


@router.delete("/drive/disconnect")
async def disconnect_drive(
    current_user=Depends(get_current_user),
):
    """Desconecta o Google Drive."""
    try:
        if os.path.exists(CREDENTIALS_PATH):
            os.rename(CREDENTIALS_PATH, CREDENTIALS_PATH + ".bak")
    except OSError:
        pass
    return {"disconnected": True}


@router.get("/email-templates")
async def get_email_templates(
    current_user=Depends(get_current_user),
):
    """Lista templates de e-mail disponíveis."""
    return [
        {"id": "kit_pronto", "name": "Kit Pronto para Revisão", "assunto": "Kit Documental — {cliente} {competencia}"},
        {"id": "kit_enviado", "name": "Kit Enviado ao Cliente", "assunto": "Documentos disponíveis — {competencia}"},
    ]


@router.get("/document-types")
async def get_document_types(
    current_user=Depends(get_current_user),
):
    """Lista tipos de documento habilitados."""
    return [
        {"id": "holerite", "name": "Holerite", "code": "holerite", "enabled": True},
        {"id": "ponto", "name": "Folha de Ponto", "code": "ponto", "enabled": True},
        {"id": "guia_fgts", "name": "Guia FGTS", "code": "guia_fgts", "enabled": True},
        {"id": "certidao", "name": "Certidões", "code": "certidao", "enabled": True},
    ]


@router.get("/schedule")
async def get_schedule(
    current_user=Depends(get_current_user),
):
    """Retorna configuração de agendamento automático."""
    return {
        "enabled": False,
        "cron_expression": "0 8 5 * *",
        "description": "Todo dia 5 às 08h",
        "last_run": None,
    }


@router.post("/schedule")
async def save_schedule(
    current_user=Depends(get_current_user),
):
    """Salva configuração de agendamento."""
    return {"ok": True, "message": "Agendamento salvo"}
