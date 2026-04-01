"""Modelo de custo mensal para postos de portaria."""

import uuid
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from core.models import Base


class CustoPostoPortaria(Base):
    """Custo mensal de um posto de portaria."""

    __tablename__ = "custos_postos_portaria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    posto_id = Column(Integer, nullable=True, index=True)
    contrato_id = Column(Integer, nullable=True, index=True)
    mes_referencia = Column(Date, nullable=False, index=True)

    # Dimensões do posto
    tipo_escala = Column(String(20), nullable=True)  # 12x36, 44h, 24h, etc.
    qtd_funcionarios = Column(Integer, default=1)

    # Componentes de custo
    custo_salarios = Column(Numeric(12, 2), default=0)
    custo_encargos = Column(Numeric(12, 2), default=0)  # INSS, FGTS, férias, 13º
    custo_beneficios = Column(Numeric(12, 2), default=0)  # VT, VR, VA, plano saúde
    custo_adicional_noturno = Column(Numeric(12, 2), default=0)
    custo_horas_extras = Column(Numeric(12, 2), default=0)
    custo_uniformes = Column(Numeric(12, 2), default=0)  # Uniformes e EPIs
    custo_equipamentos = Column(Numeric(12, 2), default=0)  # Rádio, lanterna, colete
    custo_supervisao = Column(Numeric(12, 2), default=0)  # Supervisão rateada
    custo_overhead = Column(Numeric(12, 2), default=0)  # Administrativo rateado

    # Totais
    custo_total = Column(Numeric(12, 2), default=0)
    margem_contratual = Column(Numeric(12, 2), default=0)  # Valor faturado - custo total

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CustoPostoPortaria posto={self.posto_id} mes={self.mes_referencia}>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "posto_id": self.posto_id,
            "contrato_id": self.contrato_id,
            "mes_referencia": self.mes_referencia.isoformat() if self.mes_referencia else None,
            "tipo_escala": self.tipo_escala,
            "qtd_funcionarios": self.qtd_funcionarios,
            "custo_salarios": float(self.custo_salarios or 0),
            "custo_encargos": float(self.custo_encargos or 0),
            "custo_beneficios": float(self.custo_beneficios or 0),
            "custo_adicional_noturno": float(self.custo_adicional_noturno or 0),
            "custo_horas_extras": float(self.custo_horas_extras or 0),
            "custo_uniformes": float(self.custo_uniformes or 0),
            "custo_equipamentos": float(self.custo_equipamentos or 0),
            "custo_supervisao": float(self.custo_supervisao or 0),
            "custo_overhead": float(self.custo_overhead or 0),
            "custo_total": float(self.custo_total or 0),
            "margem_contratual": float(self.margem_contratual or 0),
        }
