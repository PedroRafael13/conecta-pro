"""Modelo de custo mensal para postos de limpeza."""
import uuid
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from core.models import Base


class CustoPostoLimpeza(Base):
    """Custo mensal de um posto de limpeza e conservação."""

    __tablename__ = "custos_postos_limpeza"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    posto_id = Column(Integer, nullable=True, index=True)
    contrato_id = Column(Integer, nullable=True, index=True)
    mes_referencia = Column(Date, nullable=False, index=True)

    # Dimensões
    area_m2 = Column(Numeric(10, 2), nullable=True)          # Área atendida em m²
    tipo_limpeza = Column(String(30), nullable=True)         # diaria, semanal, quinzenal

    # Componentes de custo
    custo_mao_obra = Column(Numeric(12, 2), default=0)       # Salários base
    custo_encargos = Column(Numeric(12, 2), default=0)
    custo_beneficios = Column(Numeric(12, 2), default=0)
    custo_materiais = Column(Numeric(12, 2), default=0)      # Produtos de limpeza
    custo_equipamentos = Column(Numeric(12, 2), default=0)   # Máquinas, aspiradores
    custo_supervisao = Column(Numeric(12, 2), default=0)
    custo_overhead = Column(Numeric(12, 2), default=0)

    # Totais e indicadores
    custo_total = Column(Numeric(12, 2), default=0)
    custo_m2 = Column(Numeric(10, 4), nullable=True)         # Custo por m² (calculado)
    margem_contratual = Column(Numeric(12, 2), default=0)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CustoPostoLimpeza posto={self.posto_id} mes={self.mes_referencia}>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "posto_id": self.posto_id,
            "contrato_id": self.contrato_id,
            "mes_referencia": self.mes_referencia.isoformat() if self.mes_referencia else None,
            "area_m2": float(self.area_m2 or 0),
            "tipo_limpeza": self.tipo_limpeza,
            "custo_mao_obra": float(self.custo_mao_obra or 0),
            "custo_encargos": float(self.custo_encargos or 0),
            "custo_beneficios": float(self.custo_beneficios or 0),
            "custo_materiais": float(self.custo_materiais or 0),
            "custo_equipamentos": float(self.custo_equipamentos or 0),
            "custo_supervisao": float(self.custo_supervisao or 0),
            "custo_overhead": float(self.custo_overhead or 0),
            "custo_total": float(self.custo_total or 0),
            "custo_m2": float(self.custo_m2 or 0),
            "margem_contratual": float(self.margem_contratual or 0),
        }
