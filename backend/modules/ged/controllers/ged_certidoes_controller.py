"""
GED Certidões Controller.

Endpoints:
- GET    /certidoes          → listar certidões da empresa com status calculado
- POST   /certidoes          → adicionar nova certidão
- PUT    /certidoes/{id}     → renovar/atualizar certidão
- DELETE /certidoes/{id}     → remover certidão
"""

import logging
from datetime import date, datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["GED - Certidões"])


# ─── Schemas ─────────────────────────────────────────────────────────────────


class CertidaoCreate(BaseModel):
    name: str
    document_type: str
    issuing_body: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    file_path: str | None = None
    file_url: str | None = None
    notes: str | None = None


class CertidaoUpdate(BaseModel):
    name: str | None = None
    document_type: str | None = None
    issuing_body: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    file_path: str | None = None
    file_url: str | None = None
    notes: str | None = None


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _calcular_status(expiry_date: date | None) -> str:
    if expiry_date is None:
        return "sem_vencimento"
    hoje = date.today()
    if expiry_date < hoje:
        return "vencida"
    if expiry_date < hoje + timedelta(days=30):
        return "a_vencer"
    return "valida"


def _row_to_dict(row: Any) -> dict:
    expiry = row["expiry_date"]
    issue = row["issue_date"]
    return {
        "id": str(row["id"]),
        "name": row["name"],
        "document_type": row["document_type"],
        "issuing_body": row["issuing_body"],
        "issue_date": issue.isoformat() if issue else None,
        "expiry_date": expiry.isoformat() if expiry else None,
        "status": _calcular_status(expiry),
        "file_path": row["file_path"],
        "file_url": row["file_url"],
        "notes": row["notes"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


# ─── Endpoints ───────────────────────────────────────────────────────────────


@router.get("/certidoes")
async def listar_certidoes(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Lista todas as certidões da empresa com status calculado automaticamente."""
    result = await db.execute(
        text("""
        SELECT id, name, document_type, issuing_body,
               issue_date, expiry_date, file_path, file_url, notes,
               created_at, updated_at
        FROM ged_certidoes
        ORDER BY expiry_date ASC NULLS LAST
        """)
    )
    rows = result.mappings().all()
    certidoes = [_row_to_dict(r) for r in rows]

    validas = sum(1 for c in certidoes if c["status"] == "valida")
    vencidas = sum(1 for c in certidoes if c["status"] == "vencida")
    a_vencer = sum(1 for c in certidoes if c["status"] == "a_vencer")

    return {
        "certidoes": certidoes,
        "total": len(certidoes),
        "resumo": {
            "validas": validas,
            "vencidas": vencidas,
            "a_vencer_30d": a_vencer,
        },
        "gerado_em": datetime.now().isoformat(),
    }


@router.post("/certidoes", status_code=201)
async def criar_certidao(
    payload: CertidaoCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Adiciona nova certidão."""
    new_id = uuid4()
    await db.execute(
        text("""
        INSERT INTO ged_certidoes
          (id, name, document_type, issuing_body, issue_date, expiry_date,
           file_path, file_url, notes, created_at, updated_at)
        VALUES
          (:id, :name, :document_type, :issuing_body, :issue_date, :expiry_date,
           :file_path, :file_url, :notes, NOW(), NOW())
        """),
        {
            "id": str(new_id),
            "name": payload.name,
            "document_type": payload.document_type,
            "issuing_body": payload.issuing_body,
            "issue_date": payload.issue_date,
            "expiry_date": payload.expiry_date,
            "file_path": payload.file_path,
            "file_url": payload.file_url,
            "notes": payload.notes,
        },
    )
    await db.commit()
    return {"id": str(new_id), "message": "Certidão criada com sucesso."}


@router.put("/certidoes/{certidao_id}")
async def atualizar_certidao(
    certidao_id: str,
    payload: CertidaoUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Renova ou atualiza uma certidão existente."""
    # Verificar existência
    check = await db.execute(
        text("SELECT id FROM ged_certidoes WHERE id = :id"),
        {"id": certidao_id},
    )
    if not check.fetchone():
        raise HTTPException(
            status_code=404,
            detail={"code": "CERTIDAO_NOT_FOUND", "message": f"Certidão '{certidao_id}' não encontrada."},
        )

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=422, detail={"code": "NO_FIELDS", "message": "Nenhum campo para atualizar."})

    set_clause = ", ".join(f"{k} = :{k}" for k in updates)
    updates["certidao_id"] = certidao_id
    await db.execute(
        text(f"UPDATE ged_certidoes SET {set_clause}, updated_at = NOW() WHERE id = :certidao_id"),
        updates,
    )
    await db.commit()
    return {"id": certidao_id, "message": "Certidão atualizada com sucesso."}


@router.post("/certidoes/sync", status_code=200)
async def sincronizar_certidoes(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Dispara busca imediata de certidoes nos portais governamentais.

    Consulta CND Federal (RFB/PGFN), CNDT Trabalhista (TST) e CRF/FGTS (Caixa)
    para o CNPJ da empresa. Certidoes validas por 10+ dias sao puladas.
    """
    try:
        from modules.people_management.ged.tasks.cnd_sync_task import buscar_todas_certidoes

        resultado = await buscar_todas_certidoes(db)
        return resultado
    except Exception as exc:
        logger.error("Erro em POST /certidoes/sync: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/certidoes/sync/{cnpj}", status_code=200)
async def sincronizar_certidoes_cnpj(
    cnpj: str,
    tipo: str | None = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Dispara busca de certidoes para um CNPJ especifico.

    Args:
        cnpj: CNPJ da empresa (com ou sem formatacao)
        tipo: Tipo de certidao (cnd_federal | cndt_trabalhista | crf_fgts).
              Se omitido, busca todos os tipos.
    """
    import re

    cnpj_limpo = re.sub(r"\D", "", cnpj)
    if len(cnpj_limpo) != 14:
        raise HTTPException(status_code=422, detail=f"CNPJ invalido: {cnpj}")

    from modules.people_management.ged.tasks.cnd_sync_task import (
        CERTIDAO_CONFIG,
        _buscar_e_salvar_certidao,
    )

    tipos_validos = list(CERTIDAO_CONFIG.keys())

    if tipo and tipo not in tipos_validos:
        raise HTTPException(
            status_code=422,
            detail=f"Tipo invalido: {tipo}. Validos: {tipos_validos}",
        )

    try:
        tipos = [tipo] if tipo else tipos_validos
        resultados = []
        for t in tipos:
            r = await _buscar_e_salvar_certidao(db, cnpj_limpo, t)
            r["tipo"] = t
            resultados.append(r)

        if any(r.get("status") in ("criada", "atualizada") for r in resultados):
            await db.commit()

        return {
            "cnpj": cnpj_limpo,
            "total": len(tipos),
            "detalhes": resultados,
            "executado_em": datetime.now().isoformat(),
        }
    except Exception as exc:
        logger.error("Erro em POST /certidoes/sync/%s: %s", cnpj, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/certidoes/{certidao_id}", status_code=200)
async def remover_certidao(
    certidao_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Remove uma certidão."""
    check = await db.execute(
        text("SELECT id FROM ged_certidoes WHERE id = :id"),
        {"id": certidao_id},
    )
    if not check.fetchone():
        raise HTTPException(
            status_code=404,
            detail={"code": "CERTIDAO_NOT_FOUND", "message": f"Certidão '{certidao_id}' não encontrada."},
        )

    await db.execute(
        text("DELETE FROM ged_certidoes WHERE id = :id"),
        {"id": certidao_id},
    )
    await db.commit()
    return {"message": "Certidão removida com sucesso."}
