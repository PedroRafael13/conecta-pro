"""
GDrive Controller — Operação Conecta-Drive
Endpoints para status, autorização OAuth2 e envio de kits ao Google Drive.
"""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
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
async def listar_kits_drive(
    client_id: str | None = None,
    current_user=Depends(get_current_user),
):
    """Listar todos os kits montados no Drive."""
    from modules.gdrive.services.kit_drive_service import kit_drive_service

    kits = kit_drive_service.listar_kits_drive(client_id)
    return {"total": len(kits), "kits": kits}


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

    # Enviar e-mail automaticamente após montar no Drive
    from modules.gdrive.services.email_kit_service import email_kit_service as _email_svc

    resultado_email = _email_svc.enviar_kit_por_email(
        client_id=cliente_id,
        competencia=competencia,
        share_link=share_link,
    )

    return {
        "drive": {
            "sucesso": sync.get("configured", False),
            "kit_id": str(kit.id),
            "documentos_enviados": uploaded,
            "erros": errors,
        },
        "share_link": share_link,
        "email": resultado_email,
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


@router.get("/portal/{client_id}/kits")
async def portal_kits_cliente(
    client_id: str,
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Kits do cliente para exibir no portal.
    Autenticacao por token de sessao do portal (client_portal_sessions).
    Retorna historico dos ultimos 24 meses com share_link do Drive.
    """

    # Validar token do portal
    try:
        r_token = await db.execute(
            text(
                "SELECT client_id FROM client_portal_sessions "
                "WHERE token = :token "
                "AND expires_at > NOW() "
                "AND client_id::text = :client_id "
                "LIMIT 1"
            ),
            {"token": token, "client_id": client_id},
        )
        valid = r_token.scalar_one_or_none()
    except Exception:
        valid = None
    if not valid:
        raise HTTPException(status_code=401, detail="Token invalido ou expirado")

    rows = await db.execute(
        text(
            "SELECT competencia, total_docs, share_link, status, created_at::text "
            "FROM gdrive_kits "
            "WHERE client_id = :client_id "
            "AND status = 'concluido' "
            "ORDER BY competencia DESC "
            "LIMIT 24"
        ),
        {"client_id": client_id},
    )

    kits = []
    for row in rows.fetchall():
        competencia, total_docs, share_link, status, criado_em = row
        if share_link:
            kits.append(
                {
                    "competencia": competencia,
                    "total_docs": int(total_docs or 0),
                    "share_link": share_link,
                    "status": status or "concluido",
                    "criado_em": criado_em or "",
                }
            )

    return {"total": len(kits), "kits": kits}


# ── OAUTH2 ─────────────────────────────────────────────────────────────────────


import json as _json  # noqa: E402

from fastapi.responses import RedirectResponse as _Redirect  # noqa: E402
from sqlalchemy import text as _text  # noqa: E402

from core.database import get_session as _get_session  # noqa: E402
from modules.gdrive.services.gdrive_service import gdrive_service as _gdrive  # noqa: E402


@router.get("/oauth/callback")
async def gdrive_oauth_callback(
    code: str | None = None,
    db: AsyncSession = Depends(_get_session),
    state: str | None = None,
    error: str | None = None,
) -> _Redirect:
    """Callback OAuth2 — recebe código, troca por tokens e salva no banco."""
    base = "https://erp.conectamais.pro/modulos/gestao-pessoas/ged/configuracoes"
    if error or not code:
        logger.error("GDrive OAuth erro: %s", error)
        return _Redirect(url=f"{base}?gdrive=erro")
    try:
        tokens = _gdrive.trocar_codigo_por_token(code)
        at = tokens["access_token"]
        rt = tokens.get("refresh_token") or ""
        exp = tokens.get("expiry")
        import os as _os

        await db.execute(_text("DELETE FROM gdrive_config"))
        await db.execute(
            _text(
                "INSERT INTO gdrive_config "
                "(owner_email, access_token, refresh_token, token_expiry, "
                "is_connected, scopes, root_folder_id, kits_folder_id) "
                "VALUES (:email, :at, :rt, :exp, TRUE, :scopes, :root, :kits)"
            ),
            {
                "email": _os.environ.get("GDRIVE_OWNER_EMAIL", "jordansjesus@gmail.com"),
                "at": at,
                "rt": rt,
                "exp": exp,
                "scopes": _json.dumps(tokens.get("scopes", [])),
                "root": _os.environ.get("GDRIVE_ROOT_FOLDER_ID", ""),
                "kits": _os.environ.get("GDRIVE_KITS_FOLDER_ID", ""),
            },
        )
        await db.commit()
        _gdrive.conectar_com_tokens(at, rt, exp)
        logger.info("GDrive: OAuth2 concluído — tokens salvos")
        return _Redirect(url=f"{base}?gdrive=conectado")
    except Exception as exc:
        logger.error("GDrive callback erro: %s", exc)
        return _Redirect(url=f"{base}?gdrive=erro")


@router.post("/desconectar")
async def gdrive_desconectar(
    db: AsyncSession = Depends(_get_session),
    _user: dict = Depends(get_current_user),
) -> dict:
    """Desconectar o Google Drive e limpar tokens do banco."""
    try:
        await db.execute(
            _text(
                "UPDATE gdrive_config SET is_connected = FALSE, "
                "access_token = NULL, refresh_token = NULL, updated_at = NOW()"
            )
        )
        await db.commit()
        _gdrive._service = None
        _gdrive._initialized = False
        return {"status": "desconectado"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/autorizar")
async def gdrive_autorizar_get(
    _user: dict = Depends(get_current_user),
) -> dict:
    """GET — gerar URL OAuth2 para autorizar o Google Drive via navegador."""
    from modules.gdrive.services.gdrive_service import gdrive_service as _gds

    try:
        url = _gds.gerar_url_autorizacao()
        return {"url_autorizacao": url, "instrucao": "Acesse a URL para autorizar"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar URL: {exc}")
