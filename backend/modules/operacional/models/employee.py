"""
Model SQLAlchemy para tabela employees (funcionarios principais).
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Column, Date, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class Employee(Base):
    """Model para funcionarios."""

    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True)
    solides_id = Column(String(50), nullable=True)
    matricula = Column(String(50), nullable=True)
    codigo = Column(String(20), nullable=True)
    nome = Column(String(255), nullable=False)
    nome_social = Column(String(255), nullable=True)
    cpf = Column(String(14), nullable=True)
    email = Column(String(255), nullable=True)
    telefone = Column(String(20), nullable=True)
    celular = Column(String(20), nullable=True)
    cargo = Column(String(100), nullable=True)
    departamento = Column(String(100), nullable=True)
    data_admissao = Column(Date, nullable=True)
    data_demissao = Column(Date, nullable=True)
    status = Column(String(20), default="ativo")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
