"""Modelo de custo mensal para postos de jardinagem."""
import uuid
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from core.models import Base


class CustoPostoJardinagem(Base):
    """Custo mensal de um posto de jardinagem e manutenção de áreas verdes."""

    __tablename__ = "custos_postos_jardinagem"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    posto_id = Column(Integer, nullable=True, index=True)
    contrato_id = Column(Integer, nullable=True, index=True)
    mes_referencia = Column(Date, nullable=False, index=True)

    # Dimensões
    area_verde_m2 = Column(Numeric(10, 2), nullable=True)    # Área verde total em m²
    frequencia_visitas = Column(Integer, default=4)          # Visitas por mês

    # Componentes de custo
    custo_mao_obra = Column(Numeric(12, 2), default=0)
    custo_encargos = Column(Numeric(12, 2), default=0)
    custo_beneficios = Column(Numeric(12, 2), default=0)
    custo_insumos = Column(Numeric(12, 2), default=0)        # Adubo, mudas, sementes
    custo_equipamentos = Column(Numeric(12, 2), default=0)   # Roçadeira, soprador, etc.
    custo_combustivel = Column(Numeric(12, 2), default=0)    # Combustível para máquinas
    custo_supervisao = Column(Numeric(12, 2), default=0)
    custo_overhead = Column(Numeric(12, 2), default=0)

    # Totais e indicadores
    custo_total = Column(Numeric(12, 2), default=0)
    custo_m2 = Column(Numeric(10, 4), nullable=True)         # Custo por m² de área verde
    margem_contratual = Column(Numeric(12, 2), default=0)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CustoPostoJardinagem posto={self.posto_id} mes={self.mes_referencia}>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "posto_id": self.posto_id,
            "contrato_id": self.contrato_id,
            "mes_referencia": self.mes_referencia.isoformat() if self.mes_referencia else None,
            "area_verde_m2": float(self.area_verde_m2 or 0),
            "frequencia_visitas": self.frequencia_visitas,
            "custo_mao_obra": float(self.custo_mao_obra or 0),
            "custo_encargos": float(self.custo_encargos or 0),
            "custo_beneficios": float(self.custo_beneficios or 0),
            "custo_insumos": float(self.custo_insumos or 0),
            "custo_equipamentos": float(self.custo_equipamentos or 0),
            "custo_combustivel": float(self.custo_combustivel or 0),
            "custo_supervisao": float(self.custo_supervisao or 0),
            "custo_overhead": float(self.custo_overhead or 0),
            "custo_total": float(self.custo_total or 0),
            "custo_m2": float(self.custo_m2 or 0),
            "margem_contratual": float(self.margem_contratual or 0),
        }
