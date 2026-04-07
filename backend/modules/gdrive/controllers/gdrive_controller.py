"""
GDrive Controller — Operação Conecta-Drive
Endpoints para status, autorização OAuth2 e envio de kits ao Google Drive.
"""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gdrive", tags=["GDrive - Operação Conecta-Drive"])


# ── HELPERS ────────────────────────────────────────────────────────────────────


def _drive_service(db: AsyncSession):
    """Instancia o GoogleDriveService com sessão assíncrona."""
    from modules.people_management.ged.services.google_drive_service import (
        GoogleDriveService,
    )

    return GoogleDriveService(db)


# ── STATUS ─────────────────────────────────────────────────────────────────────


@router.get("/status")
async def gdrive_status(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verifica se o Google Drive está conectado e retorna o status da integração."""
    svc = _drive_service(db)
    creds = await svc.check_credentials()
    return {
        "conectado": creds.get("configured", False),
        "email": None,
        "nome": None,
        "tipo": "service_account",
        "credenciais_configuradas": creds.get("credentials_file_exists", False),
        "mensagem": creds.get("message", ""),
        "acao": None if creds.get("configured") else "autorizar",
    }


# ── AUTORIZAR ──────────────────────────────────────────────────────────────────


@router.post("/autorizar")
async def gdrive_autorizar(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna URL de autorização do Google Drive (OAuth2 / service account).
    Se já conectado, confirma o status.
    """
    svc = _drive_service(db)
    creds = await svc.check_credentials()

    if creds.get("configured"):
        return {
            "ja_autorizado": True,
            "mensagem": "Google Drive já está conectado.",
            "url_autorizacao": None,
        }

    # Sem credenciais: retornar guia de configuração
    return {
        "ja_autorizado": False,
        "mensagem": (
            "Para conectar o Google Drive, faça upload do arquivo "
            "de service account (JSON) em: "
            "/opt/conecta-pro/config/google_drive_credentials.json"
        ),
        "url_autorizacao": "/modulos/gestao-pessoas/ged/configuracoes",
        "instrucoes": [
            "1. Acesse Google Cloud Console → IAM → Service Accounts",
            "2. Crie uma conta de serviço com permissão ao Drive",
            "3. Baixe a chave JSON",
            "4. Faça upload via: POST /api/v1/gdrive/credenciais",
        ],
    }


# ── LISTA DE KITS NO DRIVE ─────────────────────────────────────────────────────


@router.get("/kits")
async def gdrive_listar_kits(
    cliente_id: str | None = Query(None),
    competencia: str | None = Query(None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista kits que já foram enviados ao Google Drive."""
    from sqlalchemy import text as sa_text

    filtros = ["gdk.google_drive_link IS NOT NULL"]
    params: dict = {}

    if cliente_id:
        filtros.append("gdk.client_id::text = :client_id")
        params["client_id"] = cliente_id
    if competencia:
        # competencia = YYYY-MM
        try:
            ano, mes = competencia.split("-")
            filtros.append(
                "EXTRACT(YEAR FROM gdk.reference_month) = :ano AND EXTRACT(MONTH FROM gdk.reference_month) = :mes"
            )
            params["ano"] = int(ano)
            params["mes"] = int(mes)
        except ValueError:
            pass

    where = " AND ".join(filtros)
    rows = await db.execute(
        sa_text(
            f"SELECT gdk.id::text, gdk.reference_month::text, "
            f"gdk.google_drive_link, gdk.status, "
            f"c.name AS cliente_nome "
            f"FROM ged_document_kits gdk "
            f"JOIN ged_clients c ON c.id = gdk.client_id "
            f"WHERE {where} "
            f"ORDER BY gdk.reference_month DESC "
            f"LIMIT 50"
        ),
        params,
    )
    kits = [dict(r) for r in rows.mappings()]
    return {
        "total": len(kits),
        "kits": kits,
    }


# ── STATUS DE INGESTÃO ─────────────────────────────────────────────────────────


@router.get("/ingestao/status")
async def gdrive_ingestao_status(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Status da última sincronização/ingestão de kits para o Drive."""
    from sqlalchemy import text as sa_text

    rows = await db.execute(
        sa_text(
            "SELECT "
            "  COUNT(*) FILTER (WHERE google_drive_link IS NOT NULL) AS enviados, "
            "  COUNT(*) FILTER (WHERE google_drive_link IS NULL) AS pendentes, "
            "  COUNT(*) AS total, "
            "  MAX(updated_at)::text AS ultima_atualizacao "
            "FROM ged_document_kits"
        )
    )
    row = dict(rows.mappings().one())

    svc = _drive_service(db)
    creds = await svc.check_credentials()

    return {
        "drive_conectado": creds.get("configured", False),
        "kits_enviados": row.get("enviados", 0),
        "kits_pendentes": row.get("pendentes", 0),
        "total_kits": row.get("total", 0),
        "ultima_atualizacao": row.get("ultima_atualizacao"),
        "status": "ativo" if creds.get("configured") else "aguardando_autorizacao",
    }


# ── MONTAR E ENVIAR ────────────────────────────────────────────────────────────


@router.post("/kits/{cliente_id}/{competencia}/montar-e-enviar")
async def montar_e_enviar(
    cliente_id: str,
    competencia: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Monta o kit do cliente para a competência e envia ao Google Drive.
    Se o kit não existir, retorna erro orientando a criá-lo antes.
    competencia: YYYY-MM
    """
    from modules.people_management.ged.models.document_kit import GedDocumentKit

    # Verificar drive conectado
    svc = _drive_service(db)
    creds = await svc.check_credentials()

    if not creds.get("configured"):
        return {
            "drive": {
                "sucesso": False,
                "erro": "Google Drive não conectado",
                "acao": "autorizar — acesse Configurações GED",
            },
            "share_link": None,
            "email": {"sucesso": False},
        }

    # Encontrar kit pelo client_id + competencia (reference_month)
    try:
        ano, mes = competencia.split("-")
        ref_month = date(int(ano), int(mes), 1)
    except (ValueError, TypeError):
        raise HTTPException(status_code=422, detail="Competência inválida. Use YYYY-MM.")

    result = await db.execute(
        select(GedDocumentKit).where(
            GedDocumentKit.client_id == cliente_id,
            GedDocumentKit.reference_month == ref_month,
        )
    )
    kit = result.scalar_one_or_none()

    if not kit:
        raise HTTPException(
            status_code=404,
            detail=f"Kit não encontrado para cliente {cliente_id} em {competencia}. "
            "Monte o kit primeiro usando o botão 'Montar com GEDEON'.",
        )

    # Sincronizar com Drive
    try:
        sync = await svc.sync_kit_to_drive(str(kit.id))
        await db.commit()
    except Exception as exc:
        logger.error("Erro sync Drive: %s", exc)
        return {
            "drive": {
                "sucesso": False,
                "erro": str(exc),
            },
            "share_link": None,
            "email": {"sucesso": False},
        }

    share_link = sync.get("drive_link") or kit.google_drive_link
    uploaded = sync.get("uploaded", 0)
    errors = sync.get("errors", 0)

    return {
        "drive": {
            "sucesso": sync.get("configured", False),
            "kit_id": str(kit.id),
            "documentos_enviados": uploaded,
            "erros": errors,
        },
        "share_link": share_link,
        "email": {"sucesso": False, "motivo": "e-mail não configurado nesta operação"},
        "mensagem": (
            f"✅ {uploaded} documentos enviados ao Drive"
            if uploaded > 0
            else "⚠️ Drive conectado mas nenhum documento local encontrado para enviar"
        ),
    }


# ── ENDPOINTS DE E-MAIL ───────────────────────────────


@router.post("/kits/{client_id}/{competencia}/enviar-email")
async def enviar_kit_email(
    client_id: str,
    competencia: str,
    destinatario: str | None = None,
    current_user=Depends(get_current_user),
):
    """
    Enviar kit por e-mail.
    Link para kits > 10MB, anexos para menores.
    """
    from modules.gdrive.services.email_kit_service import email_kit_service

    resultado = email_kit_service.enviar_kit_por_email(
        client_id=client_id,
        competencia=competencia,
        destinatario_override=destinatario,
    )
    return resultado


@router.post("/kits/{client_id}/{competencia}/montar")
async def montar_kit_drive(
    client_id: str,
    competencia: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Montar kit completo no Google Drive.
    Cria pastas, faz upload de cada documento, gera link compartilhável.
    """
    from sqlalchemy import text as sa_text

    from modules.gdrive.services.kit_drive_service import kit_drive_service

    row = (
        (
            await db.execute(
                sa_text("SELECT tipo_kit FROM gedeon_kit_config WHERE client_id::text = :cid LIMIT 1"),
                {"cid": client_id},
            )
        )
        .mappings()
        .first()
    )
    tipo_kit = row["tipo_kit"] if row else "maos_de_obra"
    resultado = await kit_drive_service.montar_kit_no_drive(client_id, competencia, tipo_kit)
    return resultado


@router.get("/kits/{client_id}/{competencia}/link")
async def obter_link_kit(
    client_id: str,
    competencia: str,
    current_user=Depends(get_current_user),
):
    """Obter link do kit já montado no Drive."""
    from modules.gdrive.services.kit_drive_service import kit_drive_service

    link = kit_drive_service.obter_link_kit(client_id, competencia)
    if not link:
        raise HTTPException(status_code=404, detail="Kit não encontrado no Drive")
    return {"share_link": link, "client_id": client_id, "competencia": competencia}
