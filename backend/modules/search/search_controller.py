"""
Controller para Busca Global do Sistema
"""

import time
from typing import List, Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from core.database import get_db
from modules.operacional.models.employee import Employee
from modules.operacional.models.post import Post
from modules.operacional.models.scale import Scale
from modules.operacional.occurrences.models import Occurrence
from modules.operacional.inspection_rounds.models import InspectionRound

router = APIRouter(prefix="/search", tags=["Search - Busca Global"])


class SearchResult(BaseModel):
    """Schema de resultado individual de busca."""

    type: Literal["colaborador", "posto", "escala", "ocorrencia", "ronda"]
    id: str
    title: str
    description: str
    url: str


class SearchResponse(BaseModel):
    """Schema de resposta da busca global."""

    results: List[SearchResult] = Field(default_factory=list)
    total: int = 0
    took_ms: int = 0


@router.get("/", response_model=SearchResponse)
async def global_search(
    q: str = Query(..., min_length=1, description="Query de busca"),
    limit: int = Query(20, ge=1, le=100, description="Limite de resultados"),
    db: Session = Depends(get_db),
) -> SearchResponse:
    """
    Busca global no sistema.

    Busca em:
    - Colaboradores (nome, CPF, matrícula)
    - Postos (nome, código)
    - Escalas (período, código)
    - Ocorrências (descrição, responsável)
    - Rondas (código, inspetor)

    Retorna no máximo 20 resultados ordenados por relevância.
    """
    start_time = time.time()
    results: List[SearchResult] = []

    query_lower = q.lower().strip()

    try:
        # ========================================
        # BUSCAR COLABORADORES
        # ========================================
        employees = (
            db.query(Employee)
            .filter(
                or_(
                    Employee.nome.ilike(f"%{query_lower}%"),
                    Employee.cpf.ilike(f"%{query_lower}%"),
                    Employee.matricula.ilike(f"%{query_lower}%"),
                )
            )
            .filter(Employee.is_active == True)
            .limit(5)
            .all()
        )

        for emp in employees:
            description_parts = []
            if emp.cargo:
                description_parts.append(emp.cargo)
            if emp.departamento:
                description_parts.append(emp.departamento)

            results.append(
                SearchResult(
                    type="colaborador",
                    id=str(emp.id),
                    title=emp.nome,
                    description=" - ".join(description_parts) or "Colaborador",
                    url=f"/modulos/operacional/colaboradores/{emp.id}",
                )
            )

        # ========================================
        # BUSCAR POSTOS
        # ========================================
        posts = (
            db.query(Post)
            .filter(
                or_(
                    Post.name.ilike(f"%{query_lower}%"),
                    Post.code.ilike(f"%{query_lower}%"),
                )
            )
            .filter(Post.status == "active")
            .limit(5)
            .all()
        )

        for post in posts:
            description_parts = []
            if post.client_name:
                description_parts.append(post.client_name)
            if post.location:
                description_parts.append(post.location)

            results.append(
                SearchResult(
                    type="posto",
                    id=str(post.id),
                    title=post.name,
                    description=" - ".join(description_parts) or "Posto",
                    url=f"/modulos/operacional/postos/{post.id}",
                )
            )

        # ========================================
        # BUSCAR ESCALAS
        # ========================================
        scales = (
            db.query(Scale)
            .filter(
                or_(
                    Scale.name.ilike(f"%{query_lower}%"),
                    Scale.code.ilike(f"%{query_lower}%"),
                )
            )
            .filter(Scale.status == "active")
            .limit(5)
            .all()
        )

        for scale in scales:
            description_parts = []
            if scale.period:
                description_parts.append(f"Período: {scale.period}")
            if scale.description:
                description_parts.append(scale.description[:50])

            results.append(
                SearchResult(
                    type="escala",
                    id=str(scale.id),
                    title=scale.name,
                    description=" - ".join(description_parts) or "Escala",
                    url=f"/modulos/operacional/escalas/{scale.id}",
                )
            )

        # ========================================
        # BUSCAR OCORRÊNCIAS
        # ========================================
        occurrences = (
            db.query(Occurrence)
            .filter(
                or_(
                    Occurrence.title.ilike(f"%{query_lower}%"),
                    Occurrence.description.ilike(f"%{query_lower}%"),
                )
            )
            .order_by(Occurrence.created_at.desc())
            .limit(5)
            .all()
        )

        for occ in occurrences:
            description_parts = []
            if occ.severity:
                description_parts.append(f"Gravidade: {occ.severity}")
            if occ.description:
                description_parts.append(occ.description[:50])

            results.append(
                SearchResult(
                    type="ocorrencia",
                    id=str(occ.id),
                    title=occ.title,
                    description=" - ".join(description_parts) or "Ocorrência",
                    url=f"/modulos/operacional/ocorrencias/{occ.id}",
                )
            )

        # ========================================
        # BUSCAR RONDAS
        # ========================================
        rounds = (
            db.query(InspectionRound)
            .filter(
                or_(
                    InspectionRound.code.ilike(f"%{query_lower}%"),
                    InspectionRound.inspector_name.ilike(f"%{query_lower}%"),
                )
            )
            .order_by(InspectionRound.created_at.desc())
            .limit(5)
            .all()
        )

        for round_item in rounds:
            description_parts = []
            if round_item.inspector_name:
                description_parts.append(f"Inspetor: {round_item.inspector_name}")
            if round_item.status:
                description_parts.append(f"Status: {round_item.status}")

            results.append(
                SearchResult(
                    type="ronda",
                    id=str(round_item.id),
                    title=round_item.code,
                    description=" - ".join(description_parts) or "Ronda",
                    url=f"/modulos/operacional/rondas/{round_item.id}",
                )
            )

    except Exception as e:
        # Log error mas retorna lista vazia
        print(f"Erro na busca global: {e}")

    # Limitar ao máximo configurado
    results = results[:limit]

    # Calcular tempo de execução
    took_ms = int((time.time() - start_time) * 1000)

    return SearchResponse(
        results=results,
        total=len(results),
        took_ms=took_ms,
    )
