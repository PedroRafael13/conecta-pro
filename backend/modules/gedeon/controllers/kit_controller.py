"""Controller FastAPI — FASE 4 BLOCO 3 / T2 (§27, §28).

Expõe KitBuilderService via 2 endpoints:
- GET /kits/completude/{condominio_id}?mes_ref=MM.YYYY
- GET /kits/lote?mes_ref=MM.YYYY

§27: contrato de API (fonte única da verdade)
§28: documentação desta implementação

§13.1 Chesterton: KitBuilderService usado como está, sem alteração.
BUG 7 (CPRO 9): auth via Depends(get_current_user) OBRIGATÓRIA em ambos endpoints.
§28.6: usa get_sync_db_dependency (sync) pois KitBuilderService usa Session síncrona.
"""

from __future__ import annotations

from datetime import UTC
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user
from core.database.session import get_sync_db_dependency
from modules.gedeon.schemas.kit_completude import CompletudeKitResponse
from modules.gedeon.services.kit_builder_service import KitBuilderService

router = APIRouter(prefix="/gedeon", tags=["GEDEON — Kits"])

MES_REF_QUERY = Query(
    ...,
    description="Mês de referência no formato MM.YYYY (ex: 03.2026)",
    regex=r"^(0[1-9]|1[0-2])\.\d{4}$",
    examples=["03.2026"],
)


@router.get(
    "/kits/completude/{condominio_id}",
    response_model=CompletudeKitResponse,
    summary="Completude do kit documental de 1 condomínio",
    description="Retorna docs presentes, faltantes e métricas conforme §27.4.",
)
def get_completude_kit(
    condominio_id: UUID,
    mes_ref: str = MES_REF_QUERY,
    db: Session = Depends(get_sync_db_dependency),
    current_user=Depends(get_current_user),
) -> CompletudeKitResponse:
    """GET /api/v1/gedeon/kits/completude/{condominio_id}?mes_ref=MM.YYYY"""
    service = KitBuilderService(db)
    try:
        kit = service.build_completude(condominio_id, mes_ref)
    except ValueError as exc:
        msg = str(exc)
        if "mes_ref" in msg.lower():
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=404, detail=msg)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao montar completude do kit",
        )
    return CompletudeKitResponse.from_dataclass(kit)


@router.get(
    "/kits/lote",
    response_model=list[CompletudeKitResponse],
    summary="Completude em lote de todos os condomínios ativos",
    description="Retorna array de CompletudeKit (1 por condomínio ativo).",
)
def get_completude_lote(
    mes_ref: str = MES_REF_QUERY,
    db: Session = Depends(get_sync_db_dependency),
    current_user=Depends(get_current_user),
) -> list[CompletudeKitResponse]:
    """GET /api/v1/gedeon/kits/lote?mes_ref=MM.YYYY"""
    service = KitBuilderService(db)
    try:
        kits = service.build_lote_condominios(mes_ref)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao montar completude em lote",
        )
    return [CompletudeKitResponse.from_dataclass(k) for k in kits]


@router.post(
    "/kits/{condominio_id}/enviar",
    summary="Enviar kit via GDrive + Email",
    description="Convenience endpoint: recebe condominio_id + mes_ref (MM.YYYY). "
    "Valida completion_percentage=100, sincroniza Drive, envia email.",
)
async def enviar_kit_gedeon(
    condominio_id: UUID,
    mes_ref: str = MES_REF_QUERY,
    current_user=Depends(get_current_user),
) -> dict:
    """POST /api/v1/gedeon/kits/{condominio_id}/enviar?mes_ref=MM.YYYY"""
    from datetime import date, datetime

    from sqlalchemy import select as sa_select

    from core.database.session import async_session_factory
    from modules.gdrive.services.email_kit_service import email_kit_service as _email_svc
    from modules.people_management.ged.models.client import GedClient
    from modules.people_management.ged.models.document_kit import GedDocumentKit
    from modules.people_management.ged.services.google_drive_service import GoogleDriveService

    # Converter MM.YYYY → date
    try:
        mm, yyyy = mes_ref.split(".")
        ref_month = date(int(yyyy), int(mm), 1)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="mes_ref inválido. Use MM.YYYY.")

    async with async_session_factory() as async_db:
        # Buscar GedDocumentKit pelo client_id + reference_month
        kit_result = await async_db.execute(
            sa_select(GedDocumentKit).where(
                GedDocumentKit.client_id == str(condominio_id),
                GedDocumentKit.reference_month == ref_month,
            )
        )
        kit = kit_result.scalar_one_or_none()

        if not kit:
            raise HTTPException(
                status_code=404,
                detail=f"Kit não encontrado para condomínio {condominio_id} em {mes_ref}. Monte o kit primeiro.",
            )

        # Validar completude
        pct = float(kit.completion_percentage or 0)
        if pct < 100:
            raise HTTPException(
                status_code=400,
                detail=f"Kit incompleto. Completude atual: {pct:.1f}%. Só é possível enviar kits com 100%.",
            )

        # Buscar cliente e validar email
        client_result = await async_db.execute(sa_select(GedClient).where(GedClient.id == kit.client_id))
        client = client_result.scalar_one_or_none()
        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        if not client.contact_email:
            raise HTTPException(status_code=422, detail="Cliente não possui email cadastrado em ged_clients")

        # GDrive (atômico: se falhar, não envia email)
        drive_svc = GoogleDriveService(async_db)
        try:
            sync = await drive_svc.sync_kit_to_drive(str(kit.id))
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Falha GDrive: {str(exc)}")

        if not sync.get("configured"):
            raise HTTPException(
                status_code=502,
                detail=f"GDrive não configurado: {sync.get('message', 'Google Drive não conectado')}",
            )

        drive_link = sync.get("drive_link") or getattr(kit, "google_drive_link", None)

        # Email (só se GDrive OK)
        competencia = ref_month.strftime("%Y-%m")
        resultado_email = _email_svc.enviar_kit_por_email(
            client_id=str(kit.client_id),
            competencia=competencia,
            share_link=drive_link,
            destinatario_override=client.contact_email,
        )

        if not resultado_email.get("sucesso"):
            raise HTTPException(
                status_code=502,
                detail=f"Drive OK mas email falhou: {resultado_email.get('erro', 'Falha no envio')}",
            )

        # Gravar sent_at
        now_utc = datetime.now(UTC)
        kit.sent_at = now_utc
        kit.sent_method = "email+gdrive"
        kit.sent_to = client.contact_email
        kit.status = "enviado"
        await async_db.commit()

    return {
        "sucesso": True,
        "email_enviado": client.contact_email,
        "drive_link": drive_link,
        "sent_at": now_utc.isoformat(),
        "kit_id": str(kit.id),
        "documentos_drive": sync.get("uploaded", 0),
    }
