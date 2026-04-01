"""Modelo de custo mensal para contratos de portaria remota."""

import uuid
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID

from core.models import Base


class CustoContratoPortariaRemota(Base):
    """Custo mensal de um contrato de portaria remota/virtual."""

    __tablename__ = "custos_contratos_portaria_remota"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contrato_id = Column(Integer, nullable=True, index=True)
    mes_referencia = Column(Date, nullable=False, index=True)

    # Dimensões do contrato
    qtd_unidades = Column(Integer, default=1)  # Unidades/acessos monitorados
    qtd_acessos_mes = Column(Integer, default=0)  # Total de acionamentos no mês

    # Componentes de custo
    custo_central = Column(Numeric(12, 2), default=0)  # Central de operações (rateio)
    custo_operadores = Column(Numeric(12, 2), default=0)  # Operadores remotos (rateio)
    custo_equipamentos = Column(Numeric(12, 2), default=0)  # Equipamentos na portaria
    custo_conectividade = Column(Numeric(12, 2), default=0)  # Links de comunicação
    custo_manutencao = Column(Numeric(12, 2), default=0)  # Manutenção de equipamentos
    custo_backup_presencial = Column(Numeric(12, 2), default=0)  # Backup eventual presencial
    custo_overhead = Column(Numeric(12, 2), default=0)

    # Totais e indicadores
    custo_total = Column(Numeric(12, 2), default=0)
    custo_por_unidade = Column(Numeric(10, 4), nullable=True)  # Custo por unidade/mês
    margem_contratual = Column(Numeric(12, 2), default=0)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CustoContratoPortariaRemota contrato={self.contrato_id} mes={self.mes_referencia}>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "contrato_id": self.contrato_id,
            "mes_referencia": self.mes_referencia.isoformat() if self.mes_referencia else None,
            "qtd_unidades": self.qtd_unidades,
            "qtd_acessos_mes": self.qtd_acessos_mes,
            "custo_central": float(self.custo_central or 0),
            "custo_operadores": float(self.custo_operadores or 0),
            "custo_equipamentos": float(self.custo_equipamentos or 0),
            "custo_conectividade": float(self.custo_conectividade or 0),
            "custo_manutencao": float(self.custo_manutencao or 0),
            "custo_backup_presencial": float(self.custo_backup_presencial or 0),
            "custo_overhead": float(self.custo_overhead or 0),
            "custo_total": float(self.custo_total or 0),
            "custo_por_unidade": float(self.custo_por_unidade or 0),
            "margem_contratual": float(self.margem_contratual or 0),
        }
