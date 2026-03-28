"""
GED Config & Reports Controller.

Endpoints:
- GET  /config/drive      → status Google Drive
- GET  /config/schedule   → agendamento de envios
- PUT  /config/schedule   → salvar agendamento
- GET  /reports/monthly   → relatório mensal GED
"""

import logging
import os
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["GED - Config & Reports"])


# ─── GED Clients (alias /ged/clients → proxy to people-management) ────────────


@router.get("/clients")
async def list_ged_clients(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Lista clientes GED. Alias para /people-management/ged/clients."""
    result = await db.execute(
        text("""
        SELECT id, name, type, cnpj, address, contact_name, contact_email,
            contact_phone, portal_access_enabled, is_active, created_at
        FROM ged_clients
        WHERE is_active = true
        ORDER BY name
        """)
    )
    rows = result.mappings().all()
    return {
        "items": [
            {
                "id": str(r["id"]),
                "name": r["name"],
                "type": r["type"],
                "cnpj": r["cnpj"],
                "address": r["address"],
                "contact_name": r["contact_name"],
                "contact_email": r["contact_email"],
                "contact_phone": r["contact_phone"],
                "portal_access_enabled": r["portal_access_enabled"],
                "is_active": r["is_active"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
            for r in rows
        ],
        "total": len(rows),
    }


# ─── Config Google Drive ──────────────────────────────────────────────────────


@router.get("/config/drive")
async def get_config_drive(
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Retorna configuração do Google Drive."""
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    drive_folder = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    drive_email = os.getenv("GOOGLE_DRIVE_EMAIL", "")

    configurado = bool(client_id and client_secret)
    token_path = "/opt/conecta-pro/credentials/google_token.json"
    tem_token = os.path.exists(token_path)

    if configurado and tem_token:
        status = "conectado"
    elif configurado:
        status = "configurado_sem_token"
    else:
        status = "nao_configurado"

    return {
        "conectado": configurado and tem_token,
        "email_conta": drive_email or None,
        "pasta_raiz": drive_folder or None,
        "pasta_kits": os.getenv("GOOGLE_DRIVE_KITS_FOLDER", None),
        "pasta_certidoes": os.getenv("GOOGLE_DRIVE_CERTS_FOLDER", None),
        "ultimo_sync": None,
        "status": status,
        "client_id_configurado": bool(client_id),
    }


# ─── Config Schedule ──────────────────────────────────────────────────────────

_schedule_config: dict[str, Any] = {
    "envio_automatico": False,
    "dia_envio": 25,
    "hora_envio": "09:00",
    "canal_envio": "whatsapp",
    "incluir_certidoes": True,
    "incluir_kits": True,
    "destinatarios": [],
    "ativo": False,
}


@router.get("/config/schedule")
async def get_config_schedule(
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Retorna configuração de agendamento de envios."""
    return _schedule_config


@router.put("/config/schedule")
async def update_config_schedule(
    config: dict[str, Any],
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Salva configuração de agendamento."""
    allowed_keys = {
        "envio_automatico",
        "dia_envio",
        "hora_envio",
        "canal_envio",
        "incluir_certidoes",
        "incluir_kits",
        "destinatarios",
        "ativo",
    }
    for key, value in config.items():
        if key in allowed_keys:
            _schedule_config[key] = value

    logger.info("GED schedule atualizado: %s", config)
    return _schedule_config


# ─── Config Email Templates ──────────────────────────────────────────────────


@router.get("/config/email-templates")
async def get_email_templates(
    current_user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Retorna templates de email configurados."""
    return {
        "templates": [
            {
                "id": "kit-envio",
                "nome": "Envio Kit Mensal",
                "assunto": "Kit Documental {mes}/{ano} - {cliente}",
                "ativo": True,
            },
            {
                "id": "cert-alerta",
                "nome": "Alerta Certidão Vencendo",
                "assunto": "Certidão {tipo} vence em {dias} dias",
                "ativo": True,
            },
        ],
    }


# ─── Config Document Types ───────────────────────────────────────────────────


@router.get("/config/document-types")
async def get_document_types(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retorna tipos de documentos configurados para kits."""
    result = await db.execute(
        text("""
        SELECT DISTINCT tipo, nome, is_obrigatorio
        FROM document_kits
        WHERE is_template = true
        ORDER BY nome
        """)
    )
    rows = result.mappings().all()
    if rows:
        tipos = [{"tipo": r["tipo"], "nome": r["nome"], "obrigatorio": r["is_obrigatorio"]} for r in rows]
    else:
        tipos = [
            {"tipo": "FOLHA", "nome": "Folha de Pagamento", "obrigatorio": True},
            {"tipo": "HOLERITE", "nome": "Holerite/Contracheque", "obrigatorio": True},
            {"tipo": "PONTO", "nome": "Espelho de Ponto", "obrigatorio": True},
            {"tipo": "FGTS", "nome": "Guia FGTS", "obrigatorio": True},
            {"tipo": "GPS", "nome": "Guia GPS/INSS", "obrigatorio": True},
            {"tipo": "IRRF", "nome": "Guia IRRF", "obrigatorio": True},
            {"tipo": "RAIS", "nome": "RAIS/CAGED", "obrigatorio": False},
            {"tipo": "ASO", "nome": "ASO - Atestado Saúde", "obrigatorio": True},
            {"tipo": "EPI", "nome": "Ficha EPI", "obrigatorio": True},
            {"tipo": "CERTIDAO", "nome": "Certidões Negativas", "obrigatorio": True},
        ]
    return {"tipos": tipos, "total": len(tipos)}


# ─── Reports Monthly ─────────────────────────────────────────────────────────


@router.get("/reports/monthly")
async def get_relatorio_mensal(
    mes: int | None = Query(None),
    ano: int | None = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Relatório mensal completo do módulo GED."""
    hoje = date.today()
    mes_ref = mes or hoje.month
    ano_ref = ano or hoje.year
    mes_date = date(ano_ref, mes_ref, 1)

    # Kits do mês
    kits_result = await db.execute(
        text("""
        SELECT
            gk.id,
            gc.name as cliente,
            gk.status,
            gk.total_documents,
            gk.documents_signed,
            gk.completion_percentage
        FROM ged_document_kits gk
        LEFT JOIN ged_clients gc ON gk.client_id = gc.id
        WHERE DATE_TRUNC('month', gk.reference_month) = DATE_TRUNC('month', CAST(:mes AS date))
        ORDER BY gc.name
        """),
        {"mes": mes_date},
    )
    kits_rows = kits_result.mappings().all()

    kits = []
    concluidos = 0
    pendentes = 0
    for r in kits_rows:
        status = r["status"] or "em_montagem"
        kits.append(
            {
                "kit_id": str(r["id"]),
                "cliente": r["cliente"] or "—",
                "status": status,
                "documentos_total": r["total_documents"] or 0,
                "documentos_assinados": r["documents_signed"] or 0,
                "percentual": float(r["completion_percentage"] or 0),
            }
        )
        if status in ("completo", "enviado", "aprovado"):
            concluidos += 1
        else:
            pendentes += 1

    # Certidões
    certs_result = await db.execute(
        text("""
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'valid') as validas,
            COUNT(*) FILTER (WHERE status = 'expired') as vencidas,
            COUNT(*) FILTER (WHERE data_validade <= CURRENT_TIMESTAMP + INTERVAL '30 days'
                AND status = 'valid') as vencendo_30d
        FROM bidding_certificates
        WHERE ativo = true
        """)
    )
    cr = certs_result.mappings().first()
    certidoes = {
        "total": cr["total"] if cr else 0,
        "validas": cr["validas"] if cr else 0,
        "vencidas": cr["vencidas"] if cr else 0,
        "vencendo_30d": cr["vencendo_30d"] if cr else 0,
    }

    # NFS-e do mês
    nfse_result = await db.execute(
        text("""
        SELECT COUNT(*) as total, COALESCE(SUM(valor_servicos), 0) as valor_total
        FROM nfses
        WHERE active = true
        AND DATE_TRUNC('month', data_competencia) = DATE_TRUNC('month', CAST(:mes AS date))
        """),
        {"mes": mes_date},
    )
    nr = nfse_result.mappings().first()
    documentos = {
        "nfse_emitidas": nr["total"] if nr else 0,
        "nfse_valor": float(nr["valor_total"]) if nr and nr["valor_total"] else 0,
    }

    # Ações recomendadas
    acoes = []
    if pendentes > 0:
        acoes.append(f"{pendentes} kit(s) em montagem — completar antes do envio")
    if certidoes.get("vencidas", 0) > 0:
        acoes.append(f"{certidoes['vencidas']} certidão(ões) vencida(s) — renovar urgente")
    if certidoes.get("vencendo_30d", 0) > 0:
        acoes.append(f"{certidoes['vencendo_30d']} certidão(ões) vencendo em 30 dias")
    if concluidos == len(kits) and len(kits) > 0:
        acoes.append(f"Todos os {concluidos} kits prontos — enviar para síndicos")
    if not acoes:
        acoes.append("Nenhuma ação pendente")

    nomes_mes = [
        "",
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]

    return {
        "mes_referencia": f"{nomes_mes[mes_ref]}/{ano_ref}",
        "gerado_em": datetime.now().isoformat(),
        "resumo": {
            "total_kits": len(kits),
            "kits_concluidos": concluidos,
            "kits_pendentes": pendentes,
            "percentual_conclusao": round(concluidos / len(kits) * 100) if kits else 0,
        },
        "kits": kits,
        "certidoes": certidoes,
        "documentos": documentos,
        "acoes_recomendadas": acoes,
    }
