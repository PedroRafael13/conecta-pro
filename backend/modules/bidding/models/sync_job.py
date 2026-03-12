"""
Model de Job de Sincronizacao - Bidding AI Agents
===================================================
Controle de jobs de sincronizacao com portais publicos.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class BiddingSyncJob(Base):
    """
    Job de Sincronizacao com Portal.

    Registra execucoes de sincronizacao de dados com portais
    publicos (PNCP, ComprasNet, etc.), incluindo status e metricas.
    """

    __tablename__ = "bidding_sync_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portal = Column(String(50), nullable=False)
    tipo = Column(String(30), nullable=True)

    # Status e execucao
    status = Column(String(20), nullable=False, default="pendente")
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    # Metricas
    registros_processados = Column(Integer, default=0)
    registros_novos = Column(Integer, default=0)
    registros_atualizados = Column(Integer, default=0)
    erros = Column(JSONB, default=list)

    # Parametros/filtros utilizados
    filtros_utilizados = Column(JSONB, default=dict)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<BiddingSyncJob {self.portal}:{self.tipo} - {self.status}>"
