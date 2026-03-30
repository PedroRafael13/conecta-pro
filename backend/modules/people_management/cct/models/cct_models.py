"""
Models SQLAlchemy para CCT (Convenção Coletiva de Trabalho).

Tabelas:
- cct_convencoes: Convenção coletiva vigente
- cct_cargos: Piso salarial e adicionais por cargo
- cct_feriados: Feriados do ano
- cct_beneficios: Benefícios obrigatórios pela CCT
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import BaseModel


class CCTConvencao(BaseModel):
    """Convenção Coletiva de Trabalho vigente."""

    __tablename__ = "cct_convencoes"

    sindicato_trabalhadores: Mapped[str] = mapped_column(String(200), nullable=False)
    sindicato_trabalhadores_cnpj: Mapped[str | None] = mapped_column(String(20))
    sindicato_patronal: Mapped[str] = mapped_column(String(200), nullable=False)
    sindicato_patronal_cnpj: Mapped[str | None] = mapped_column(String(20))
    registro_mte: Mapped[str | None] = mapped_column(String(50))
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date] = mapped_column(Date, nullable=False)
    data_base: Mapped[str | None] = mapped_column(String(5))  # ex: "01/01"
    municipio: Mapped[str | None] = mapped_column(String(100))
    uf: Mapped[str | None] = mapped_column(String(2))
    descricao: Mapped[str | None] = mapped_column(Text)
    is_vigente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relacionamentos
    cargos: Mapped[list["CCTCargo"]] = relationship(
        "CCTCargo", back_populates="convencao", cascade="all, delete-orphan"
    )
    feriados: Mapped[list["CCTFeriado"]] = relationship(
        "CCTFeriado", back_populates="convencao", cascade="all, delete-orphan"
    )
    beneficios: Mapped[list["CCTBeneficio"]] = relationship(
        "CCTBeneficio", back_populates="convencao", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CCTConvencao {self.sindicato_trabalhadores}/{self.sindicato_patronal} {self.data_inicio.year}>"


class CCTCargo(BaseModel):
    """Piso salarial e adicionais por cargo conforme CCT."""

    __tablename__ = "cct_cargos"

    convencao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cct_convencoes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cargo_nome: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    piso_salarial: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    adicional_tipo: Mapped[str | None] = mapped_column(
        String(50)
    )  # nenhum, insalubridade_10, periculosidade_30, adicional_10
    adicional_noturno_percentual: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("20.0"), nullable=False
    )
    adicional_periculosidade_percentual: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("30.0"), nullable=False
    )
    adicional_insalubridade_percentual: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("10.0"), nullable=False
    )
    horas_extras_percentual: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("50.0"), nullable=False)
    horas_extras_noturnas_percentual: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("100.0"), nullable=False
    )
    jornada_semanal_horas: Mapped[int] = mapped_column(default=44, nullable=False)

    convencao: Mapped["CCTConvencao"] = relationship("CCTConvencao", back_populates="cargos")

    def __repr__(self) -> str:
        return f"<CCTCargo {self.cargo_nome} piso={self.piso_salarial}>"


class CCTFeriado(BaseModel):
    """Feriados do ano conforme CCT."""

    __tablename__ = "cct_feriados"

    convencao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cct_convencoes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    data_feriado: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # nacional, estadual, municipal
    ano: Mapped[int] = mapped_column(nullable=False, index=True)

    convencao: Mapped["CCTConvencao"] = relationship("CCTConvencao", back_populates="feriados")

    def __repr__(self) -> str:
        return f"<CCTFeriado {self.data_feriado} {self.nome}>"


class CCTBeneficio(BaseModel):
    """Benefícios obrigatórios pela CCT."""

    __tablename__ = "cct_beneficios"

    convencao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cct_convencoes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo_beneficio: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # vale_transporte, vale_refeicao, plano_odontologico, seguro_vida, etc.
    valor_minimo: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    valor_empresa: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    desconto_maximo_percentual: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    desconto_percentual_sobre_salario: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    obrigatorio: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)

    convencao: Mapped["CCTConvencao"] = relationship("CCTConvencao", back_populates="beneficios")

    def __repr__(self) -> str:
        return f"<CCTBeneficio {self.tipo_beneficio} obrigatorio={self.obrigatorio}>"
