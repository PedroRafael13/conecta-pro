"""Modelo de custo mensal para contratos de segurança eletrônica."""
import uuid
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from core.models import Base


class CustoContratoSegEletronica(Base):
    """Custo mensal de um contrato de segurança eletrônica (CFTV, monitoramento)."""

    __tablename__ = "custos_contratos_seg_eletronica"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contrato_id = Column(Integer, nullable=True, index=True)
    mes_referencia = Column(Date, nullable=False, index=True)

    # Dimensões do contrato
    qtd_cameras = Column(Integer, default=0)
    qtd_pontos_monitorados = Column(Integer, default=0)

    # Componentes de custo
    custo_monitoramento = Column(Numeric(12, 2), default=0)  # Central de monitoramento
    custo_operadores = Column(Numeric(12, 2), default=0)     # Operadores de CFTV
    custo_manutencao = Column(Numeric(12, 2), default=0)     # Manutenção preventiva/corretiva
    custo_conectividade = Column(Numeric(12, 2), default=0)  # Links, internet, VPN
    custo_software = Column(Numeric(12, 2), default=0)       # Licenças de software/VMS
    custo_depreciacao = Column(Numeric(12, 2), default=0)    # Depreciação de equipamentos
    custo_overhead = Column(Numeric(12, 2), default=0)

    # Totais e indicadores
    custo_total = Column(Numeric(12, 2), default=0)
    custo_por_camera = Column(Numeric(10, 4), nullable=True) # Custo por câmera/mês
    margem_contratual = Column(Numeric(12, 2), default=0)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CustoContratoSegEletronica contrato={self.contrato_id} mes={self.mes_referencia}>"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "contrato_id": self.contrato_id,
            "mes_referencia": self.mes_referencia.isoformat() if self.mes_referencia else None,
            "qtd_cameras": self.qtd_cameras,
            "qtd_pontos_monitorados": self.qtd_pontos_monitorados,
            "custo_monitoramento": float(self.custo_monitoramento or 0),
            "custo_operadores": float(self.custo_operadores or 0),
            "custo_manutencao": float(self.custo_manutencao or 0),
            "custo_conectividade": float(self.custo_conectividade or 0),
            "custo_software": float(self.custo_software or 0),
            "custo_depreciacao": float(self.custo_depreciacao or 0),
            "custo_overhead": float(self.custo_overhead or 0),
            "custo_total": float(self.custo_total or 0),
            "custo_por_camera": float(self.custo_por_camera or 0),
            "margem_contratual": float(self.margem_contratual or 0),
        }
