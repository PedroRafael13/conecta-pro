"""
Modelos SQLAlchemy para persistencia do modulo CCT.

Tabelas:
- cct_salary_audits: Auditorias de validacao salarial
- cct_compliance_checks: Verificacoes de conformidade CCT
- cct_benefit_configs: Configuracoes de beneficios por empresa
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class CCTSalaryAudit(Base):
    """Registro de auditoria de validacao salarial contra piso CCT."""

    __tablename__ = "cct_salary_audits"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    employee_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, index=True)
    cargo_cct: Mapped[str] = mapped_column(String(200), nullable=False)
    piso_cct: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    salario_atual: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    conforme: Mapped[bool] = mapped_column(Boolean, nullable=False)
    diferenca: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    adicional_tipo: Mapped[str | None] = mapped_column(String(50))
    adicional_valor: Mapped[float | None] = mapped_column(Numeric(12, 2))
    observacoes: Mapped[str | None] = mapped_column(Text)
    auditado_por: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<CCTSalaryAudit employee={self.employee_id} conforme={self.conforme}>"


class CCTComplianceCheck(Base):
    """Registro de verificacao de conformidade geral CCT."""

    __tablename__ = "cct_compliance_checks"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    empresa_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), index=True)
    tipo_verificacao: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    periodo_referencia: Mapped[str] = mapped_column(String(7), nullable=False)
    total_funcionarios: Mapped[int] = mapped_column(Integer, default=0)
    conformes: Mapped[int] = mapped_column(Integer, default=0)
    nao_conformes: Mapped[int] = mapped_column(Integer, default=0)
    percentual_conformidade: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    detalhes: Mapped[dict | None] = mapped_column(JSONB)
    executado_por: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<CCTComplianceCheck tipo={self.tipo_verificacao} periodo={self.periodo_referencia}>"


class CCTBenefitConfig(Base):
    """Configuracao de beneficios CCT por empresa."""

    __tablename__ = "cct_benefit_configs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    empresa_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), index=True)
    tipo_beneficio: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    valor_empresa: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    desconto_empregado: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    operadora: Mapped[str | None] = mapped_column(String(200))
    vigencia_inicio: Mapped[datetime | None] = mapped_column(Date)
    vigencia_fim: Mapped[datetime | None] = mapped_column(Date)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    observacoes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<CCTBenefitConfig tipo={self.tipo_beneficio} ativo={self.ativo}>"
