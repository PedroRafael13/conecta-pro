"""
Repository PPRA - Acesso a Dados de Riscos Ocupacionais
========================================================

Camada de acesso a dados para entidades do PPRA.
"""

from datetime import date
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from modules.health_occupational.models.ppra import (
    RiskMapping,
    OccupationalRisk,
    ControlMeasure,
    RiskLevel,
)


class PPRARepository:
    """Repository para entidades do PPRA."""

    def __init__(self, db: Session):
        self.db = db

    # ==========================================================================
    # Risk Mapping Repository
    # ==========================================================================

    def create_mapping(self, mapping: RiskMapping) -> RiskMapping:
        """Cria novo mapeamento."""
        self.db.add(mapping)
        self.db.commit()
        self.db.refresh(mapping)
        return mapping

    def get_mapping_by_id(self, mapping_id: UUID) -> Optional[RiskMapping]:
        """Busca mapeamento por ID."""
        return self.db.query(RiskMapping).filter(RiskMapping.id == mapping_id).first()

    def get_mappings_by_setor(
        self,
        setor: str,
        ativo: Optional[bool] = True,
    ) -> List[RiskMapping]:
        """Lista mapeamentos de um setor."""
        query = self.db.query(RiskMapping).filter(
            RiskMapping.setor == setor
        )

        if ativo is not None:
            query = query.filter(RiskMapping.ativo == ativo)

        return query.order_by(RiskMapping.data_avaliacao.desc()).all()

    def get_latest_mapping_by_setor(self, setor: str) -> Optional[RiskMapping]:
        """Busca mapeamento mais recente de um setor."""
        return self.db.query(RiskMapping).filter(
            RiskMapping.setor == setor,
            RiskMapping.ativo == True,
        ).order_by(RiskMapping.data_avaliacao.desc()).first()

    def list_mappings(
        self,
        setor: Optional[str] = None,
        ativo: Optional[bool] = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[RiskMapping]:
        """Lista mapeamentos com filtros."""
        query = self.db.query(RiskMapping)

        if setor:
            query = query.filter(RiskMapping.setor.ilike(f"%{setor}%"))
        if ativo is not None:
            query = query.filter(RiskMapping.ativo == ativo)

        return query.order_by(RiskMapping.data_avaliacao.desc()).offset(offset).limit(limit).all()

    def count_mappings(
        self,
        setor: Optional[str] = None,
        ativo: Optional[bool] = True,
    ) -> int:
        """Conta mapeamentos."""
        query = self.db.query(RiskMapping)

        if setor:
            query = query.filter(RiskMapping.setor.ilike(f"%{setor}%"))
        if ativo is not None:
            query = query.filter(RiskMapping.ativo == ativo)

        return query.count()

    def update_mapping(self, mapping: RiskMapping) -> RiskMapping:
        """Atualiza mapeamento."""
        self.db.commit()
        self.db.refresh(mapping)
        return mapping

    def deactivate_mapping(self, mapping_id: UUID) -> Optional[RiskMapping]:
        """Desativa mapeamento."""
        mapping = self.get_mapping_by_id(mapping_id)
        if mapping:
            mapping.ativo = False
            self.db.commit()
            self.db.refresh(mapping)
        return mapping

    # ==========================================================================
    # Occupational Risk Repository
    # ==========================================================================

    def create_risk(self, risk: OccupationalRisk) -> OccupationalRisk:
        """Cria novo risco."""
        self.db.add(risk)
        self.db.commit()
        self.db.refresh(risk)
        return risk

    def get_risk_by_id(self, risk_id: UUID) -> Optional[OccupationalRisk]:
        """Busca risco por ID."""
        return self.db.query(OccupationalRisk).filter(
            OccupationalRisk.id == risk_id
        ).first()

    def get_risks_by_mapping(self, mapping_id: UUID) -> List[OccupationalRisk]:
        """Lista riscos de um mapeamento."""
        return self.db.query(OccupationalRisk).filter(
            OccupationalRisk.mapeamento_id == mapping_id
        ).all()

    def get_risks_by_categoria(self, categoria: str) -> List[OccupationalRisk]:
        """Lista riscos por categoria."""
        return self.db.query(OccupationalRisk).filter(
            OccupationalRisk.categoria == categoria
        ).all()

    def get_risks_by_funcao(self, funcao: str) -> List[OccupationalRisk]:
        """Lista riscos associados a uma funcao."""
        # Usa contains para buscar em array JSONB
        return self.db.query(OccupationalRisk).filter(
            OccupationalRisk.funcoes_expostas.contains([funcao])
        ).all()

    def get_high_priority_risks(self) -> List[OccupationalRisk]:
        """Lista riscos de alta prioridade (substancial ou intoleravel)."""
        return self.db.query(OccupationalRisk).filter(
            OccupationalRisk.nivel_risco.in_([
                RiskLevel.SUBSTANCIAL.value,
                RiskLevel.INTOLERAVEL.value,
            ])
        ).order_by(OccupationalRisk.prioridade).all()

    def update_risk(self, risk: OccupationalRisk) -> OccupationalRisk:
        """Atualiza risco."""
        self.db.commit()
        self.db.refresh(risk)
        return risk

    def delete_risk(self, risk_id: UUID) -> bool:
        """Remove risco."""
        risk = self.get_risk_by_id(risk_id)
        if risk:
            self.db.delete(risk)
            self.db.commit()
            return True
        return False

    # ==========================================================================
    # Control Measure Repository
    # ==========================================================================

    def create_measure(self, measure: ControlMeasure) -> ControlMeasure:
        """Cria nova medida de controle."""
        self.db.add(measure)
        self.db.commit()
        self.db.refresh(measure)
        return measure

    def get_measure_by_id(self, measure_id: UUID) -> Optional[ControlMeasure]:
        """Busca medida por ID."""
        return self.db.query(ControlMeasure).filter(
            ControlMeasure.id == measure_id
        ).first()

    def get_measures_by_mapping(
        self,
        mapping_id: UUID,
        status: Optional[str] = None,
    ) -> List[ControlMeasure]:
        """Lista medidas de um mapeamento."""
        query = self.db.query(ControlMeasure).filter(
            ControlMeasure.mapeamento_id == mapping_id
        )

        if status:
            query = query.filter(ControlMeasure.status == status)

        return query.all()

    def get_pending_measures(self) -> List[ControlMeasure]:
        """Lista medidas pendentes."""
        return self.db.query(ControlMeasure).filter(
            ControlMeasure.status == "pendente"
        ).order_by(ControlMeasure.data_prevista).all()

    def update_measure(self, measure: ControlMeasure) -> ControlMeasure:
        """Atualiza medida."""
        self.db.commit()
        self.db.refresh(measure)
        return measure

    # ==========================================================================
    # Statistics
    # ==========================================================================

    def get_risk_statistics(self) -> Dict[str, Any]:
        """Retorna estatisticas de riscos."""
        total_mappings = self.db.query(RiskMapping).filter(
            RiskMapping.ativo == True
        ).count()

        total_risks = self.db.query(OccupationalRisk).count()

        risks_by_category = {}
        for cat in ["fisico", "quimico", "biologico", "ergonomico", "acidente"]:
            risks_by_category[cat] = self.db.query(OccupationalRisk).filter(
                OccupationalRisk.categoria == cat
            ).count()

        risks_by_level = {}
        for level in ["trivial", "toleravel", "moderado", "substancial", "intoleravel"]:
            risks_by_level[level] = self.db.query(OccupationalRisk).filter(
                OccupationalRisk.nivel_risco == level
            ).count()

        pending_measures = self.db.query(ControlMeasure).filter(
            ControlMeasure.status == "pendente"
        ).count()

        return {
            "total_mapeamentos": total_mappings,
            "total_riscos": total_risks,
            "riscos_por_categoria": risks_by_category,
            "riscos_por_nivel": risks_by_level,
            "medidas_pendentes": pending_measures,
        }

    def get_sectors_summary(self) -> List[Dict[str, Any]]:
        """Retorna resumo de riscos por setor."""
        mappings = self.db.query(RiskMapping).filter(
            RiskMapping.ativo == True
        ).all()

        summary = []
        for mapping in mappings:
            summary.append({
                "setor": mapping.setor,
                "total_riscos": len(mapping.riscos),
                "nivel_geral": mapping.nivel_risco_geral,
                "data_avaliacao": mapping.data_avaliacao.isoformat(),
                "data_proxima_revisao": mapping.data_proxima_revisao.isoformat() if mapping.data_proxima_revisao else None,
            })

        return summary
