"""
Controller de Documentos — Departamento Pessoal.

Endpoint de listagem de documentos de funcionários.
Proxy para o módulo GED quando disponível.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["DP - Documentos"])


@router.get("/")
async def list_documents(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
) -> Any:
    """Lista documentos de funcionários."""
    try:
        from sqlalchemy import func, select

        from modules.people_management.ged.models.document import Document

        count_q = select(func.count()).select_from(Document)
        total = (await db.execute(count_q)).scalar() or 0
        query = select(Document).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        return {
            "items": [
                {
                    "id": str(getattr(d, "id", "")),
                    "title": getattr(d, "title", getattr(d, "nome", "")),
                    "type": getattr(d, "document_type", getattr(d, "tipo", "")),
                    "status": getattr(d, "status", "active"),
                }
                for d in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        }
    except Exception:
        return {"items": [], "total": 0, "page": 1, "page_size": 20, "total_pages": 1}
