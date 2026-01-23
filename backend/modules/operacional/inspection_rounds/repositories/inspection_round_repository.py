"""
Repository de Rondas de Inspecao.

Author: Conecta PRO Team
Date: 2026-01-23
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from ..models import InspectionRound, InspectionRoundStatus, InspectionCheckpoint
from ..schemas import InspectionRoundFilter


class InspectionRoundRepository:
    """Repository para operacoes de banco de dados de Rondas de Inspecao."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, round_data: dict) -> InspectionRound:
        """Cria uma nova ronda."""
        inspection_round = InspectionRound(**round_data)
        self.db.add(inspection_round)
        self.db.commit()
        self.db.refresh(inspection_round)
        return inspection_round

    def get_by_id(self, round_id: str) -> Optional[InspectionRound]:
        """Busca ronda por ID."""
        return self.db.query(InspectionRound).filter(
            InspectionRound.id == round_id,
            InspectionRound.is_active == True,
        ).first()

    def get_by_code(self, code: str) -> Optional[InspectionRound]:
        """Busca ronda por codigo."""
        return self.db.query(InspectionRound).filter(
            InspectionRound.code == code,
            InspectionRound.is_active == True,
        ).first()

    def list(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[InspectionRoundFilter] = None,
    ) -> Tuple[List[InspectionRound], int]:
        """Lista rondas com filtros e paginacao."""
        query = self.db.query(InspectionRound).filter(
            InspectionRound.tenant_id == tenant_id,
            InspectionRound.is_active == True,
        )

        if filters:
            if filters.inspector_id:
                query = query.filter(InspectionRound.inspector_id == str(filters.inspector_id))
            if filters.inspector_role:
                query = query.filter(InspectionRound.inspector_role == filters.inspector_role)
            if filters.status:
                query = query.filter(InspectionRound.status == filters.status)
            if filters.start_date:
                query = query.filter(InspectionRound.created_at >= filters.start_date)
            if filters.end_date:
                query = query.filter(InspectionRound.created_at <= filters.end_date)
            if filters.has_occurrences is not None:
                if filters.has_occurrences:
                    query = query.filter(InspectionRound.total_occurrences > 0)
                else:
                    query = query.filter(InspectionRound.total_occurrences == 0)
            if filters.has_disciplinary_actions is not None:
                if filters.has_disciplinary_actions:
                    query = query.filter(InspectionRound.total_disciplinary_actions > 0)
                else:
                    query = query.filter(InspectionRound.total_disciplinary_actions == 0)
            if filters.post_id:
                # Busca rondas que visitaram determinado posto
                query = query.filter(
                    InspectionRound.posts_visited.contains([str(filters.post_id)])
                )

        total = query.count()
        rounds = query.order_by(InspectionRound.created_at.desc()).offset(skip).limit(limit).all()

        return rounds, total

    def update(self, inspection_round: InspectionRound) -> InspectionRound:
        """Atualiza uma ronda."""
        self.db.commit()
        self.db.refresh(inspection_round)
        return inspection_round

    def delete(self, inspection_round: InspectionRound) -> None:
        """Soft delete de uma ronda."""
        inspection_round.is_active = False
        self.db.commit()

    def get_next_sequence(self, tenant_id: str, year: int) -> int:
        """Retorna proximo numero sequencial para codigo."""
        result = self.db.query(func.count(InspectionRound.id)).filter(
            InspectionRound.tenant_id == tenant_id,
            func.extract('year', InspectionRound.created_at) == year,
        ).scalar()
        return (result or 0) + 1

    def get_rounds_by_inspector(
        self,
        inspector_id: str,
        tenant_id: str,
        limit: int = 50,
    ) -> List[InspectionRound]:
        """Busca rondas de um inspetor."""
        return self.db.query(InspectionRound).filter(
            InspectionRound.inspector_id == inspector_id,
            InspectionRound.tenant_id == tenant_id,
            InspectionRound.is_active == True,
        ).order_by(InspectionRound.created_at.desc()).limit(limit).all()

    def get_rounds_in_progress(self, tenant_id: str) -> List[InspectionRound]:
        """Retorna rondas em andamento."""
        return self.db.query(InspectionRound).filter(
            InspectionRound.tenant_id == tenant_id,
            InspectionRound.status == InspectionRoundStatus.EM_ANDAMENTO.value,
            InspectionRound.is_active == True,
        ).all()

    def get_rounds_scheduled_today(self, tenant_id: str) -> List[InspectionRound]:
        """Retorna rondas agendadas para hoje."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)

        return self.db.query(InspectionRound).filter(
            InspectionRound.tenant_id == tenant_id,
            InspectionRound.status == InspectionRoundStatus.AGENDADA.value,
            InspectionRound.scheduled_date >= today_start,
            InspectionRound.scheduled_date <= today_end,
            InspectionRound.is_active == True,
        ).all()

    def count_by_status(self, tenant_id: str) -> dict:
        """Conta rondas por status."""
        result = self.db.query(
            InspectionRound.status,
            func.count(InspectionRound.id)
        ).filter(
            InspectionRound.tenant_id == tenant_id,
            InspectionRound.is_active == True,
        ).group_by(InspectionRound.status).all()

        return {status: count for status, count in result}

    def get_stats_by_inspector(self, tenant_id: str, limit: int = 10) -> List[dict]:
        """Retorna estatisticas por inspetor."""
        result = self.db.query(
            InspectionRound.inspector_id,
            InspectionRound.inspector_name,
            InspectionRound.inspector_role,
            func.count(InspectionRound.id).label('total_rounds'),
            func.sum(InspectionRound.total_occurrences).label('total_occurrences'),
            func.sum(InspectionRound.total_disciplinary_actions).label('total_disciplinary_actions'),
            func.avg(InspectionRound.duration_minutes).label('avg_duration'),
            func.max(InspectionRound.created_at).label('last_round'),
        ).filter(
            InspectionRound.tenant_id == tenant_id,
            InspectionRound.is_active == True,
        ).group_by(
            InspectionRound.inspector_id,
            InspectionRound.inspector_name,
            InspectionRound.inspector_role,
        ).order_by(func.count(InspectionRound.id).desc()).limit(limit).all()

        return [
            {
                'inspector_id': r.inspector_id,
                'inspector_name': r.inspector_name,
                'inspector_role': r.inspector_role,
                'total_rounds': r.total_rounds,
                'total_occurrences': r.total_occurrences or 0,
                'total_disciplinary_actions': r.total_disciplinary_actions or 0,
                'avg_duration_minutes': float(r.avg_duration) if r.avg_duration else 0,
                'last_round_date': r.last_round,
            }
            for r in result
        ]

    # ==========================================================================
    # CHECKPOINT OPERATIONS
    # ==========================================================================

    def create_checkpoint(self, checkpoint_data: dict) -> InspectionCheckpoint:
        """Cria um novo checkpoint."""
        checkpoint = InspectionCheckpoint(**checkpoint_data)
        self.db.add(checkpoint)
        self.db.commit()
        self.db.refresh(checkpoint)
        return checkpoint

    def get_checkpoint_by_id(self, checkpoint_id: str) -> Optional[InspectionCheckpoint]:
        """Busca checkpoint por ID."""
        return self.db.query(InspectionCheckpoint).filter(
            InspectionCheckpoint.id == checkpoint_id,
            InspectionCheckpoint.is_active == True,
        ).first()

    def get_checkpoints_by_round(self, round_id: str) -> List[InspectionCheckpoint]:
        """Lista checkpoints de uma ronda."""
        return self.db.query(InspectionCheckpoint).filter(
            InspectionCheckpoint.inspection_round_id == round_id,
            InspectionCheckpoint.is_active == True,
        ).order_by(InspectionCheckpoint.sequence).all()

    def update_checkpoint(self, checkpoint: InspectionCheckpoint) -> InspectionCheckpoint:
        """Atualiza um checkpoint."""
        self.db.commit()
        self.db.refresh(checkpoint)
        return checkpoint

    def get_next_checkpoint_sequence(self, round_id: str) -> int:
        """Retorna proximo numero sequencial para checkpoint."""
        result = self.db.query(func.max(InspectionCheckpoint.sequence)).filter(
            InspectionCheckpoint.inspection_round_id == round_id,
        ).scalar()
        return (result or 0) + 1

    def count_checkpoints_by_status(self, round_id: str) -> dict:
        """Conta checkpoints por status."""
        result = self.db.query(
            InspectionCheckpoint.status,
            func.count(InspectionCheckpoint.id)
        ).filter(
            InspectionCheckpoint.inspection_round_id == round_id,
            InspectionCheckpoint.is_active == True,
        ).group_by(InspectionCheckpoint.status).all()

        return {status: count for status, count in result}
