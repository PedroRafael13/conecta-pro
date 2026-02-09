"""
Controller para KPI Trends - Tendências de indicadores
"""

import logging
from datetime import datetime, timedelta
from typing import Literal, cast

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.database import get_db
from modules.operacional.models.employee import Employee
from modules.operacional.models.post import Post
from modules.operacional.models.scale import Scale
from modules.operacional.occurrences.models import Occurrence

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kpi-trends", tags=["Operacional - KPI Trends"])


class KPITrendsData(BaseModel):
    """Dados de tendências dos KPIs."""

    postos_ativos: list[int] = Field(default_factory=list)
    colaboradores_ativos: list[int] = Field(default_factory=list)
    escalas_em_andamento: list[int] = Field(default_factory=list)
    ocorrencias_mes: list[int] = Field(default_factory=list)
    cobertura_percentual: list[float] = Field(default_factory=list)


class KPITrendsResponse(BaseModel):
    """Resposta do endpoint de tendências."""

    period: str
    days: int
    data: KPITrendsData


@router.get("/", response_model=KPITrendsResponse)
async def get_kpi_trends(
    period: Literal["7d", "30d", "90d"] = Query("7d", description="Período de análise"),
    db: Session = Depends(get_db),
) -> KPITrendsResponse:
    """
    Retorna tendências de KPIs ao longo do tempo.

    Períodos:
    - 7d: últimos 7 dias
    - 30d: últimos 30 dias
    - 90d: últimos 90 dias
    """
    # Mapear período para dias
    period_days: dict[str, int] = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
    }

    days = period_days.get(period, 7)

    try:
        # Calcular data inicial
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Inicializar listas de dados
        postos_ativos: list[int] = []
        colaboradores_ativos: list[int] = []
        escalas_em_andamento: list[int] = []
        ocorrencias_mes: list[int] = []
        cobertura_percentual: list[float] = []

        # Gerar dados por dia
        for i in range(days):
            current_date = start_date + timedelta(days=i)

            # Postos ativos
            postos_count = cast(
                int,
                (
                    db.query(func.count(Post.id))
                    .filter(Post.status == "active")
                    .filter(Post.created_at <= current_date)
                    .scalar()
                )
                or 0,
            )
            postos_ativos.append(postos_count)

            # Colaboradores ativos
            colab_count = cast(
                int,
                (
                    db.query(func.count(Employee.id))
                    .filter(Employee.is_active)
                    .filter(Employee.created_at <= current_date)
                    .scalar()
                )
                or 0,
            )
            colaboradores_ativos.append(colab_count)

            # Escalas em andamento
            escalas_count = cast(
                int,
                (
                    db.query(func.count(Scale.id))
                    .filter(Scale.status == "active")
                    .filter(Scale.created_at <= current_date)
                    .scalar()
                )
                or 0,
            )
            escalas_em_andamento.append(escalas_count)

            # Ocorrências no dia
            occ_count = cast(
                int,
                (
                    db.query(func.count(Occurrence.id))
                    .filter(func.date(Occurrence.created_at) == current_date.date())
                    .scalar()
                )
                or 0,
            )
            ocorrencias_mes.append(occ_count)

            # Cobertura percentual (simples: colaboradores / postos * 100)
            if postos_count > 0:
                cobertura = (colab_count / postos_count) * 100
                cobertura_percentual.append(round(cobertura, 2))
            else:
                cobertura_percentual.append(0.0)

        logger.info("KPI trends calculados para período %s", period)

        return KPITrendsResponse(
            period=period,
            days=days,
            data=KPITrendsData(
                postos_ativos=postos_ativos,
                colaboradores_ativos=colaboradores_ativos,
                escalas_em_andamento=escalas_em_andamento,
                ocorrencias_mes=ocorrencias_mes,
                cobertura_percentual=cobertura_percentual,
            ),
        )

    except Exception as e:
        logger.error("Erro ao calcular KPI trends: %s", e)
        # Retornar dados vazios em caso de erro
        return KPITrendsResponse(
            period=period,
            days=days,
            data=KPITrendsData(),
        )
