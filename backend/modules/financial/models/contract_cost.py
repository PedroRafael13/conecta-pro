"""Modelo de custo por contrato/posto por tipo de serviço."""

import uuid
from datetime import date
from enum import StrEnum

from sqlalchemy import Column, Date, Integer, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from core.models import Base


class ServiceType(StrEnum):
    PORTARIA = "portaria"
    LIMPEZA = "limpeza"
    JARDINAGEM = "jardinagem"
    SEGURANCA_ELETRONICA = "seguranca_eletronica"
    PORTARIA_REMOTA = "portaria_remota"


class ContractCost(Base):
    """Custo mensal por contrato, detalhado por tipo de serviço."""

    __tablename__ = "financial_contract_costs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(String(255), nullable=False, index=True)  # ID externo do contrato
    contract_name = Column(String(255), nullable=False)
    service_type = Column(SAEnum(ServiceType, name="servicetype"), nullable=False)
    reference_month = Column(Date, nullable=False, index=True)

    # Mão de obra
    labor_base = Column(Numeric(12, 2), default=0)  # Salários base
    labor_overtime_50 = Column(Numeric(12, 2), default=0)  # HE 50%
    labor_overtime_100 = Column(Numeric(12, 2), default=0)  # HE 100%
    labor_night_add = Column(Numeric(12, 2), default=0)  # Adicional noturno
    labor_charges = Column(Numeric(12, 2), default=0)  # Encargos INSS/FGTS
    labor_provisions = Column(Numeric(12, 2), default=0)  # Férias + 13º

    # Benefícios
    benefit_vt = Column(Numeric(12, 2), default=0)  # Vale transporte
    benefit_vr = Column(Numeric(12, 2), default=0)  # Vale refeição
    benefit_va = Column(Numeric(12, 2), default=0)  # Vale alimentação
    benefit_health = Column(Numeric(12, 2), default=0)  # Plano saúde
    benefit_other = Column(Numeric(12, 2), default=0)  # Outros benefícios

    # Materiais/Insumos (varia por tipo)
    materials_uniforms = Column(Numeric(12, 2), default=0)  # Uniformes/EPIs
    materials_supplies = Column(Numeric(12, 2), default=0)  # Produtos/Materiais
    materials_equipment = Column(Numeric(12, 2), default=0)  # Equipamentos
    materials_maintenance = Column(Numeric(12, 2), default=0)  # Manutenção

    # Conectividade/Tecnologia (seg. eletrônica, portaria remota)
    tech_connectivity = Column(Numeric(12, 2), default=0)  # Internet/links
    tech_monitoring = Column(Numeric(12, 2), default=0)  # Monitoramento central
    tech_software = Column(Numeric(12, 2), default=0)  # Licenças software

    # Rateios administrativos
    overhead_supervision = Column(Numeric(12, 2), default=0)  # Supervisão rateada
    overhead_admin = Column(Numeric(12, 2), default=0)  # Administrativo rateado
    overhead_commercial = Column(Numeric(12, 2), default=0)  # Comercial rateado

    # Métricas calculadas
    total_cost = Column(Numeric(12, 2), default=0)  # Custo total
    contract_revenue = Column(Numeric(12, 2), default=0)  # Receita do contrato
    gross_margin = Column(Numeric(5, 2), default=0)  # Margem % = (receita-custo)/receita*100

    # Métricas específicas por tipo
    qty_workers = Column(Integer, default=0)  # Qtd funcionários
    area_m2 = Column(Numeric(10, 2), default=0)  # Área (limpeza/jardinagem)
    qty_units = Column(Integer, default=0)  # Unidades (portaria remota)
    qty_cameras = Column(Integer, default=0)  # Câmeras (seg. eletrônica)

    # Observações
    notes = Column(String(500), nullable=True)
    created_at = Column(Date, default=date.today)
