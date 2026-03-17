"""Model de CIPA (Comissao Interna de Prevencao de Acidentes) — NR-5."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base as _declarative_base

try:
    from core.database import Base
except ImportError:
    Base = _declarative_base()


class CIPAMembro(Base):
    """Membro da CIPA."""

    __tablename__ = "sst_cipa_membros"

    id = Column(Integer, primary_key=True, autoincrement=True)
    membro_id = Column(String(36), unique=True, nullable=False, index=True)
    employee_id = Column(String(36), nullable=False, index=True)
    employee_nome = Column(String(200))
    funcao = Column(String(50), nullable=False)
    representacao = Column(String(20), nullable=False)
    data_eleicao = Column(Date)
    data_posse = Column(Date)
    data_fim_mandato = Column(Date)
    status = Column(String(20), default="ativo")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "membro_id": self.membro_id,
            "employee_id": self.employee_id,
            "nome": self.employee_nome,
            "funcao": self.funcao,
            "representacao": self.representacao,
            "data_posse": str(self.data_posse) if self.data_posse else None,
            "data_fim_mandato": (str(self.data_fim_mandato) if self.data_fim_mandato else None),
            "status": self.status,
        }


class CIPAReuniao(Base):
    """Reuniao da CIPA."""

    __tablename__ = "sst_cipa_reunioes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reuniao_id = Column(String(36), unique=True, nullable=False, index=True)
    data_reuniao = Column(Date, nullable=False)
    tipo = Column(String(50), default="ordinaria")
    pauta = Column(Text)
    ata = Column(Text)
    participantes = Column(JSON, default=list)
    status = Column(String(20), default="agendada")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "reuniao_id": self.reuniao_id,
            "data": str(self.data_reuniao),
            "tipo": self.tipo,
            "pauta": self.pauta,
            "status": self.status,
        }
