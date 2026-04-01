"""
Controller de Busca Global — Conecta PRO.

GET /search?q=<termo>&limit=<n>
Busca em: Colaboradores (nome, CPF, matrícula), Postos (nome, código),
Escalas (código, nome) e Ocorrências (descrição).
"""

import logging
import time
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_active_user
from core.database import get_db
from modules.operacional.models.employee import Employee
from modules.operacional.models.post import Post
from modules.operacional.models.scale import Scale

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/search",
    tags=["Search - Busca Global"],
    dependencies=[Depends(get_current_active_user)],
)


def _result(rtype: str, rid: str, title: str, description: str, url: str) -> dict[str, Any]:
    return {"type": rtype, "id": rid, "title": title, "description": description, "url": url}


@router.get("")
async def global_search(
    q: str = Query(..., min_length=2, description="Termo de busca"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Busca global em colaboradores, postos e escalas."""
    t0 = time.monotonic()
    results: list[dict[str, Any]] = []
    term = f"%{q}%"

    # Colaboradores
    try:
        emp_q = (
            select(Employee)
            .where(
                Employee.is_active.is_(True),
                or_(
                    Employee.nome.ilike(term),
                    Employee.cpf.ilike(term),
                    Employee.matricula.ilike(term),
                ),
            )
            .limit(limit)
        )
        emp_rows = (await db.execute(emp_q)).scalars().all()
        for e in emp_rows:
            results.append(
                _result(
                    "colaborador",
                    str(e.id),
                    e.nome,
                    f"CPF: {e.cpf or '-'} | Matrícula: {e.matricula or '-'}",
                    f"/modulos/dp/funcionarios/{e.id}",
                )
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Busca colaboradores falhou: %s", exc)

    # Postos
    try:
        post_q = (
            select(Post)
            .where(
                Post.is_active.is_(True),
                or_(Post.name.ilike(term), Post.code.ilike(term)),
            )
            .limit(limit)
        )
        post_rows = (await db.execute(post_q)).scalars().all()
        for p in post_rows:
            results.append(
                _result(
                    "posto",
                    str(p.id),
                    p.name,
                    f"Código: {p.code}",
                    f"/modulos/operacional/postos/{p.id}",
                )
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Busca postos falhou: %s", exc)

    # Escalas
    try:
        scale_q = (
            select(Scale)
            .where(
                Scale.is_active.is_(True),
                or_(Scale.code.ilike(term), Scale.name.ilike(term)),
            )
            .limit(limit)
        )
        scale_rows = (await db.execute(scale_q)).scalars().all()
        for s in scale_rows:
            results.append(
                _result(
                    "escala",
                    str(s.id),
                    s.name or s.code,
                    f"Período: {s.month:02d}/{s.year}",
                    f"/modulos/operacional/escalas/{s.id}",
                )
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Busca escalas falhou: %s", exc)

    took_ms = round((time.monotonic() - t0) * 1000, 1)
    total = len(results)

    # Trim to limit across all types
    results = results[:limit]

    return {"results": results, "total": total, "took_ms": took_ms}
