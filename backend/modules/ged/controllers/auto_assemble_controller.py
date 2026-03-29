"""
Controller standalone para auto-assemble de kits documentais.

Isolado do aggregator para evitar import circular via people_management.__init__.
Registrado diretamente no main_production.py.
"""

import logging
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["GED - Auto-Assemble"])


@router.post("/auto-assemble")
async def auto_assemble_kits(
    reference_month: date | None = Query(None, description="Mes de referencia (default: mes atual)"),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Monta kits automaticamente para todos os clientes ativos.

    Coleta documentos de DP, Fiscal e Operacoes automaticamente
    para cada cliente que tem funcionarios alocados.
    """
    from modules.people_management.ged.services.kit_builder_service import KitBuilderService

    ref = reference_month or date.today().replace(day=1)
    builder = KitBuilderService(db)
    try:
        result = await builder.auto_build_all_kits(ref)
        await db.commit()
        return result
    except Exception as e:
        logger.error("Erro no auto-assemble: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kits")
async def list_kits(
    client_id: str | None = Query(None),
    status: str | None = Query(None),
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=2020),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Lista kits documentais com filtros."""
    from sqlalchemy import text

    conditions = []
    params: dict[str, Any] = {}

    if client_id:
        conditions.append("client_id = :client_id")
        params["client_id"] = client_id
    if status:
        conditions.append("status = :status")
        params["status"] = status
    if month and year:
        conditions.append("EXTRACT(MONTH FROM reference_month) = :month")
        conditions.append("EXTRACT(YEAR FROM reference_month) = :year")
        params["month"] = month
        params["year"] = year

    where = " AND ".join(conditions) if conditions else "1=1"
    query = text(
        f"SELECT gk.*, gc.name as client_name FROM ged_document_kits gk "
        f"LEFT JOIN ged_clients gc ON gk.client_id = gc.id "
        f"WHERE {where} ORDER BY gk.reference_month DESC, gk.created_at DESC LIMIT 50"
    )
    result = await db.execute(query, params)
    rows = result.mappings().all()
    return {
        "total": len(rows),
        "items": [
            {
                "id": str(r["id"]),
                "client_id": str(r["client_id"]) if r["client_id"] else None,
                "client_name": r.get("client_name") or None,
                "reference_month": r["reference_month"].isoformat() if r["reference_month"] else None,
                "status": r["status"],
                "total_employees": r["total_employees"],
                "total_documents": r["total_documents"],
                "documents_signed": r["documents_signed"],
                "completion_percentage": float(r["completion_percentage"]) if r["completion_percentage"] else 0,
                "sent_at": r["sent_at"].isoformat() if r["sent_at"] else None,
                "sent_method": r["sent_method"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in rows
        ],
    }


@router.get("/kits/{kit_id}")
async def get_kit_detail(
    kit_id: str,
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna detalhes de um kit documental."""
    from sqlalchemy import text

    result = await db.execute(
        text("""
        SELECT gk.*, gc.name as client_name
        FROM ged_document_kits gk
        LEFT JOIN ged_clients gc ON gk.client_id = gc.id
        WHERE gk.id = :kit_id
        """),
        {"kit_id": kit_id},
    )
    r = result.mappings().first()
    if not r:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")

    # Buscar documentos do kit
    docs_result = await db.execute(
        text("""
        SELECT id, document_type, document_name, file_path, is_signed, source_module, created_at
        FROM ged_kit_documents
        WHERE kit_id = :kit_id
        ORDER BY document_type, created_at
        """),
        {"kit_id": kit_id},
    )
    docs = docs_result.mappings().all()

    return {
        "id": str(r["id"]),
        "client_id": str(r["client_id"]) if r["client_id"] else None,
        "client_name": r.get("client_name"),
        "reference_month": r["reference_month"].isoformat() if r["reference_month"] else None,
        "status": r["status"],
        "total_employees": r["total_employees"],
        "total_documents": r["total_documents"],
        "documents_signed": r["documents_signed"],
        "completion_percentage": float(r["completion_percentage"]) if r["completion_percentage"] else 0,
        "sent_at": r["sent_at"].isoformat() if r["sent_at"] else None,
        "created_at": r["created_at"].isoformat() if r["created_at"] else None,
        "documents": [
            {
                "id": str(d["id"]),
                "document_type": d["document_type"],
                "name": d["document_name"],
                "file_path": d["file_path"],
                "signed": d["is_signed"],
                "origin": d["source_module"],
                "category": "employee" if d["source_module"] in ("dp", "rh", "operacional") else "company",
                "created_at": d["created_at"].isoformat() if d["created_at"] else None,
            }
            for d in docs
        ],
    }


@router.post("/kits")
async def create_kit(
    data: dict[str, Any],
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria um novo kit documental."""
    import uuid

    from sqlalchemy import text

    client_id = data.get("client_id")
    reference_month_str = data.get("reference_month")

    if not client_id:
        raise HTTPException(status_code=422, detail="client_id obrigatorio")
    if not reference_month_str:
        raise HTTPException(status_code=422, detail="reference_month obrigatorio (YYYY-MM-DD)")

    # Converter string para date
    try:
        ref_date = date.fromisoformat(reference_month_str[:10])
    except (ValueError, TypeError):
        raise HTTPException(status_code=422, detail="reference_month formato invalido (YYYY-MM-DD)")

    # Verificar duplicata
    existing = await db.execute(
        text("SELECT id FROM ged_document_kits WHERE client_id = :cid AND reference_month = :rm"),
        {"cid": client_id, "rm": ref_date},
    )
    if existing.first():
        raise HTTPException(status_code=409, detail="Kit ja existe para este cliente/mes")

    kit_id = str(uuid.uuid4())
    await db.execute(
        text("""
        INSERT INTO ged_document_kits (id, client_id, reference_month, status,
            total_employees, total_documents, documents_signed, completion_percentage,
            created_at, updated_at)
        VALUES (:id, :cid, :rm, 'em_montagem', 0, 0, 0, 0, NOW(), NOW())
        """),
        {"id": kit_id, "cid": client_id, "rm": ref_date},
    )
    await db.commit()

    return {"id": kit_id, "client_id": client_id, "reference_month": ref_date.isoformat(), "status": "em_montagem"}


@router.post("/kits/{kit_id}/send")
async def send_kit(
    kit_id: str,
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Envia kit ao cliente (muda status para 'enviado')."""
    from sqlalchemy import text

    result = await db.execute(
        text("SELECT id, status FROM ged_document_kits WHERE id = :id"),
        {"id": kit_id},
    )
    kit = result.mappings().first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")

    await db.execute(
        text("UPDATE ged_document_kits SET status = 'enviado', sent_at = NOW(), updated_at = NOW() WHERE id = :id"),
        {"id": kit_id},
    )
    await db.commit()
    return {"success": True, "kit_id": kit_id, "novo_status": "enviado"}


@router.post("/kits/{kit_id}/approve")
async def approve_kit(
    kit_id: str,
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Aprova kit (muda status para 'aprovado')."""
    from sqlalchemy import text

    result = await db.execute(
        text("SELECT id, status FROM ged_document_kits WHERE id = :id"),
        {"id": kit_id},
    )
    kit = result.mappings().first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit nao encontrado")

    await db.execute(
        text(
            "UPDATE ged_document_kits SET status = 'aprovado', approved_at = NOW(), updated_at = NOW() WHERE id = :id"
        ),
        {"id": kit_id},
    )
    await db.commit()
    return {"success": True, "kit_id": kit_id, "novo_status": "aprovado"}


@router.post("/kits/montar")
async def montar_kits(
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Monta kits para todos os clientes ativos que nao tem kit no mes atual."""
    import uuid

    from sqlalchemy import text

    hoje = date.today()
    mes_ref = hoje.replace(day=1)

    result = await db.execute(
        text("""
        SELECT gc.id, gc.name
        FROM ged_clients gc
        WHERE gc.is_active = true
        AND gc.id NOT IN (
            SELECT client_id FROM ged_document_kits
            WHERE reference_month = :mes
        )
        """),
        {"mes": mes_ref},
    )
    clientes = result.mappings().all()

    criados = 0
    detalhes = []
    for c in clientes:
        kit_id = str(uuid.uuid4())
        await db.execute(
            text("""
            INSERT INTO ged_document_kits (id, client_id, reference_month, status,
                total_employees, total_documents, documents_signed, completion_percentage,
                created_at, updated_at)
            VALUES (:id, :cid, :mes, 'em_montagem', 0, 0, 0, 0, NOW(), NOW())
            """),
            {"id": kit_id, "cid": str(c["id"]), "mes": mes_ref},
        )
        criados += 1
        detalhes.append({"kit_id": kit_id, "client": c["name"]})

    await db.commit()
    return {"kits_criados": criados, "detalhes": detalhes}


@router.get("/dashboard")
async def ged_dashboard(
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Dashboard consolidado do GED com metricas operacionais."""
    from sqlalchemy import text

    # Total de documentos por status
    docs_result = await db.execute(
        text("""
        SELECT
            count(*) as total,
            count(*) FILTER (WHERE status = 'ativo' OR status = 'rascunho') as ativos,
            count(*) FILTER (WHERE status = 'assinado') as assinados,
            count(*) FILTER (WHERE status = 'expirado') as expirados
        FROM ged_documents
    """)
    )
    docs = docs_result.mappings().first()

    # Kits do mes atual
    kits_result = await db.execute(
        text("""
        SELECT
            count(*) as total,
            count(*) FILTER (WHERE status = 'EM_MONTAGEM') as em_montagem,
            count(*) FILTER (WHERE status = 'COMPLETO') as completos,
            count(*) FILTER (WHERE status = 'ENVIADO') as enviados,
            count(*) FILTER (WHERE status = 'APROVADO') as aprovados,
            COALESCE(AVG(completion_percentage), 0) as media_completude
        FROM ged_document_kits
        WHERE EXTRACT(MONTH FROM reference_month) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(YEAR FROM reference_month) = EXTRACT(YEAR FROM CURRENT_DATE)
    """)
    )
    kits = kits_result.mappings().first()

    # Pastas
    folders_result = await db.execute(
        text("""
        SELECT count(*) as total FROM ged_folders WHERE status = 'ativa'
    """)
    )
    folders = folders_result.mappings().first()

    # Tags
    tags_result = await db.execute(
        text("""
        SELECT count(*) as total FROM ged_document_tags WHERE is_active = true
    """)
    )
    tags = tags_result.mappings().first()

    # Clientes GED
    clients_result = await db.execute(
        text("""
        SELECT
            count(*) as total,
            count(*) FILTER (WHERE portal_access_enabled = true) as com_portal
        FROM ged_clients
    """)
    )
    clients = clients_result.mappings().first()

    return {
        "documentos": {
            "total": docs["total"] if docs else 0,
            "ativos": docs["ativos"] if docs else 0,
            "assinados": docs["assinados"] if docs else 0,
            "expirados": docs["expirados"] if docs else 0,
        },
        "kits_mes_atual": {
            "total": kits["total"] if kits else 0,
            "em_montagem": kits["em_montagem"] if kits else 0,
            "completos": kits["completos"] if kits else 0,
            "enviados": kits["enviados"] if kits else 0,
            "aprovados": kits["aprovados"] if kits else 0,
            "media_completude": round(float(kits["media_completude"]), 1) if kits else 0,
        },
        "pastas": folders["total"] if folders else 0,
        "tags": tags["total"] if tags else 0,
        "clientes": {
            "total": clients["total"] if clients else 0,
            "com_portal": clients["com_portal"] if clients else 0,
        },
    }
