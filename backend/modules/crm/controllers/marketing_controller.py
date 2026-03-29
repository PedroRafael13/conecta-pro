"""
Marketing Controller — Campanhas, leads de marketing e conversão para CRM.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/marketing", tags=["Marketing"])


class CampaignCreate(BaseModel):
    name: str
    type: str = "organic"
    budget: float = 0
    description: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None


class MktLeadCreate(BaseModel):
    campaign_id: str | None = None
    name: str
    email: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    source: str | None = None


# === CAMPAIGNS ===


@router.get("/campaigns/")
async def listar_campanhas(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        text("""
        SELECT mc.*, (SELECT COUNT(*) FROM marketing_leads ml WHERE ml.campaign_id = mc.id) as total_leads,
               (SELECT COUNT(*) FROM marketing_leads ml WHERE ml.campaign_id = mc.id AND ml.status = 'converted') as converted
        FROM marketing_campaigns mc ORDER BY mc.created_at DESC
    """)
    )
    rows = result.fetchall()
    return {
        "items": [
            {
                "id": str(r.id),
                "name": r.name,
                "type": r.type,
                "status": r.status,
                "budget": float(r.budget) if r.budget else 0,
                "spent": float(r.spent) if r.spent else 0,
                "start_date": str(r.start_date) if r.start_date else None,
                "end_date": str(r.end_date) if r.end_date else None,
                "description": r.description,
                "total_leads": r.total_leads,
                "converted": r.converted,
                "roi": round((r.converted / max(r.total_leads, 1)) * 100, 1),
            }
            for r in rows
        ],
        "total": len(rows),
    }


@router.post("/campaigns/")
async def criar_campanha(data: CampaignCreate, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        text("""
        INSERT INTO marketing_campaigns (name, type, budget, description, start_date, end_date, utm_source, utm_medium, utm_campaign)
        VALUES (:name, :type, :budget, :desc, :start, :end, :utm_s, :utm_m, :utm_c) RETURNING id
    """),
        {
            "name": data.name,
            "type": data.type,
            "budget": data.budget,
            "desc": data.description,
            "start": data.start_date,
            "end": data.end_date,
            "utm_s": data.utm_source,
            "utm_m": data.utm_medium,
            "utm_c": data.utm_campaign,
        },
    )
    await db.commit()
    return {"id": str(result.fetchone()[0]), "message": "Campanha criada"}


# === MARKETING LEADS ===


@router.get("/leads/")
async def listar_mkt_leads(
    campaign_id: str | None = Query(None),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_async_session),
):
    where_clauses = []
    if campaign_id:
        where_clauses.append(f"ml.campaign_id = '{campaign_id}'")
    if status:
        where_clauses.append(f"ml.status = '{status}'")
    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    result = await db.execute(
        text(f"""
        SELECT ml.*, mc.name as campaign_name
        FROM marketing_leads ml
        LEFT JOIN marketing_campaigns mc ON ml.campaign_id = mc.id
        {where}
        ORDER BY ml.created_at DESC
    """)
    )
    rows = result.fetchall()
    return {
        "items": [
            {
                "id": str(r.id),
                "name": r.name,
                "email": r.email,
                "phone": r.phone,
                "whatsapp": r.whatsapp,
                "source": r.source,
                "status": r.status,
                "campaign_name": r.campaign_name,
                "crm_lead_id": str(r.crm_lead_id) if r.crm_lead_id else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
        "total": len(rows),
    }


@router.post("/leads/")
async def criar_mkt_lead(data: MktLeadCreate, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        text("""
        INSERT INTO marketing_leads (campaign_id, name, email, phone, whatsapp, source)
        VALUES (:cid, :name, :email, :phone, :whatsapp, :source) RETURNING id
    """),
        {
            "cid": data.campaign_id,
            "name": data.name,
            "email": data.email,
            "phone": data.phone,
            "whatsapp": data.whatsapp,
            "source": data.source,
        },
    )
    await db.commit()
    return {"id": str(result.fetchone()[0]), "message": "Lead marketing criado"}


@router.post("/leads/{lead_id}/convert")
async def converter_lead_para_crm(lead_id: str, db: AsyncSession = Depends(get_async_session)):
    """Converte lead de marketing em lead CRM — fecha o ciclo campanha→CRM."""
    # Buscar lead marketing
    ml = await db.execute(text("SELECT * FROM marketing_leads WHERE id = :id"), {"id": lead_id})
    mkt_lead = ml.fetchone()
    if not mkt_lead:
        raise HTTPException(status_code=404, detail="Lead marketing nao encontrado")

    if mkt_lead.status == "converted":
        return {"message": "Lead ja convertido", "crm_lead_id": str(mkt_lead.crm_lead_id)}

    # Buscar campanha para source
    campaign_name = "marketing"
    if mkt_lead.campaign_id:
        camp = await db.execute(
            text("SELECT name FROM marketing_campaigns WHERE id = :id"), {"id": str(mkt_lead.campaign_id)}
        )
        cr = camp.fetchone()
        if cr:
            campaign_name = cr[0]

    # Criar lead no CRM
    crm_result = await db.execute(
        text("""
        INSERT INTO leads (name, email, phone, company, source, status, score, probability, expected_value, is_active)
        VALUES (:name, :email, :phone, :name, :source, 'new', 50, 0.3, 0, true) RETURNING id
    """),
        {
            "name": mkt_lead.name,
            "email": mkt_lead.email or f"{mkt_lead.name.lower().replace(' ', '.')}@lead.conecta",
            "phone": mkt_lead.phone,
            "source": f"campanha_{campaign_name}",
        },
    )
    crm_lead_id = str(crm_result.fetchone()[0])

    # Atualizar marketing lead
    await db.execute(
        text("""
        UPDATE marketing_leads SET status = 'converted', crm_lead_id = :crm_id, updated_at = NOW()
        WHERE id = :id
    """),
        {"crm_id": crm_lead_id, "id": lead_id},
    )

    await db.commit()

    return {
        "message": "Lead convertido para CRM",
        "crm_lead_id": crm_lead_id,
        "campanha": campaign_name,
    }


@router.get("/leads/stats")
async def stats_mkt_leads(db: AsyncSession = Depends(get_async_session)):
    """Estatísticas de leads por campanha."""
    result = await db.execute(
        text("""
        SELECT
            mc.name as campanha,
            COUNT(ml.id) as total,
            COUNT(*) FILTER (WHERE ml.status = 'new') as novos,
            COUNT(*) FILTER (WHERE ml.status = 'contacted') as contactados,
            COUNT(*) FILTER (WHERE ml.status = 'qualified') as qualificados,
            COUNT(*) FILTER (WHERE ml.status = 'converted') as convertidos,
            COUNT(*) FILTER (WHERE ml.status = 'lost') as perdidos,
            ROUND(COUNT(*) FILTER (WHERE ml.status = 'converted')::numeric / NULLIF(COUNT(ml.id), 0) * 100, 1) as taxa_conversao
        FROM marketing_campaigns mc
        LEFT JOIN marketing_leads ml ON ml.campaign_id = mc.id
        GROUP BY mc.id, mc.name
        ORDER BY total DESC
    """)
    )
    rows = result.fetchall()
    return {
        "campanhas": [
            {
                "campanha": r[0],
                "total": r[1],
                "novos": r[2],
                "contactados": r[3],
                "qualificados": r[4],
                "convertidos": r[5],
                "perdidos": r[6],
                "taxa_conversao": float(r[7]) if r[7] else 0,
            }
            for r in rows
        ],
        "gerado_em": datetime.now().isoformat(),
    }
