"""Model para categorias de contas a pagar."""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.payable_account import PayableAccount


class CategoryType(StrEnum):
    """Tipo de categoria."""

    DESPESA = "despesa"  # Despesas operacionais
    CUSTO = "custo"  # Custos diretos
    INVESTIMENTO = "investimento"  # Investimentos/CAPEX
    IMPOSTO = "imposto"  # Impostos e taxas
    FOLHA = "folha"  # Folha de pagamento
    FINANCEIRO = "financeiro"  # Juros, multas, tarifas
    OUTRO = "outro"


class CategoryNature(StrEnum):
    """Natureza da categoria (plano de contas)."""

    # Despesas Operacionais
    PESSOAL = "pessoal"  # Salários, encargos, benefícios
    ADMINISTRATIVO = "administrativo"  # Material de escritório, etc
    OCUPACAO = "ocupacao"  # Aluguel, condomínio, IPTU
    UTILIDADES = "utilidades"  # Água, luz, gás, telefone, internet
    MANUTENCAO = "manutencao"  # Manutenção predial e equipamentos
    SEGURANCA = "seguranca"  # Vigilância, monitoramento
    LIMPEZA = "limpeza"  # Limpeza e conservação
    TRANSPORTE = "transporte"  # Combustível, manutenção veículos
    SERVICOS = "servicos"  # Serviços terceirizados
    MARKETING = "marketing"  # Publicidade, eventos
    TECNOLOGIA = "tecnologia"  # Software, hardware, suporte
    JURIDICO = "juridico"  # Honorários advocatícios
    CONTABIL = "contabil"  # Honorários contábeis
    CONSULTORIA = "consultoria"  # Consultorias diversas
    SEGUROS = "seguros"  # Seguros em geral

    # Tributos
    TRIBUTOS_FEDERAIS = "tributos_federais"
    TRIBUTOS_ESTADUAIS = "tributos_estaduais"
    TRIBUTOS_MUNICIPAIS = "tributos_municipais"

    # Financeiro
    JUROS_MULTAS = "juros_multas"
    TARIFAS_BANCARIAS = "tarifas_bancarias"

    # Outros
    OUTROS = "outros"


class PayableCategory(Base):
    """Categoria de conta a pagar (plano de contas)."""

    __tablename__ = "payable_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Hierarquia
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payable_categories.id"),
        nullable=True,
        index=True,
    )
    path = Column(String(500), nullable=True)  # /1/2/3 para busca hierárquica
    depth = Column(Integer, default=0)

    # Identificação
    code = Column(String(20), nullable=True)  # Código contábil (ex: 3.1.01)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category_type = Column(String(20), nullable=False, default=CategoryType.DESPESA.value)
    nature = Column(String(30), nullable=True)

    # Configurações
    is_system = Column(Boolean, default=False)  # Categoria do sistema (não editável)
    allows_children = Column(Boolean, default=True)  # Permite subcategorias
    requires_cost_center = Column(Boolean, default=False)  # Requer centro de custo
    requires_project = Column(Boolean, default=False)  # Requer projeto

    # Contabilidade
    accounting_code = Column(String(20), nullable=True)  # Código conta contábil
    cost_center_default = Column(String(50), nullable=True)  # Centro de custo padrão

    # Orçamento
    budget_monthly = Column(String(20), nullable=True)  # Orçamento mensal
    budget_yearly = Column(String(20), nullable=True)  # Orçamento anual
    alert_percentage = Column(Integer, default=80)  # % para alerta de orçamento

    # Exibição
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    display_order = Column(Integer, default=0)

    # Controle
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    children: list["PayableCategory"] = relationship(
        "PayableCategory",
        backref="parent",
        remote_side=[id],  # noqa: A003
        foreign_keys=[parent_id],
    )
    payable_accounts: list["PayableAccount"] = relationship("PayableAccount", back_populates="category")

    __table_args__ = (
        Index("ix_payable_categories_code", "code"),
        Index("ix_payable_categories_type", "category_type"),
        Index("ix_payable_categories_parent", "parent_id"),
        Index("ix_payable_categories_path", "path"),
    )

    def __repr__(self) -> str:
        return f"<PayableCategory {self.code} - {self.name}>"

    @property
    def full_name(self) -> str:
        """Retorna nome completo com código."""
        if self.code:
            return f"{self.code} - {self.name}"
        return self.name

    @property
    def is_leaf(self) -> bool:
        """Verifica se é categoria folha (sem filhos)."""
        return not self.allows_children or len(self.children) == 0

    def get_full_path_name(self) -> str:
        """Retorna caminho completo de nomes."""
        names = [self.name]
        current = self
        while current.parent:
            current = current.parent
            names.insert(0, current.name)
        return " > ".join(names)

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "code": self.code,
            "name": self.name,
            "full_name": self.full_name,
            "category_type": self.category_type,
            "nature": self.nature,
            "depth": self.depth,
            "is_leaf": self.is_leaf,
            "is_active": self.is_active,
            "icon": self.icon,
            "color": self.color,
        }
