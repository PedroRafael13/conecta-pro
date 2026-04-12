"""Model para categorias de produtos/serviços."""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.product import Product


class ProductCategoryType(StrEnum):
    """Tipo de categoria."""

    PRODUTO = "produto"
    SERVICO = "servico"
    MATERIAL = "material"
    EQUIPAMENTO = "equipamento"
    CONSUMIVEL = "consumivel"
    ATIVO_FIXO = "ativo_fixo"


class ProductCategoryStatus(StrEnum):
    """Status da categoria."""

    ATIVA = "ativa"
    INATIVA = "inativa"
    ARQUIVADA = "arquivada"


class ProductCategory(Base):
    """Categoria de produtos/serviços para compras."""

    __tablename__ = "product_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominiums.id"),
        nullable=False,
        index=True,
    )

    # Hierarquia
    parent_id = Column(UUID(as_uuid=True), ForeignKey("product_categories.id"), nullable=True)
    path = Column(String(500), nullable=True)  # /parent_id/child_id/...
    depth = Column(Integer, default=0)

    # Identificação
    code = Column(String(20), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category_type = Column(String(20), nullable=False, default=ProductCategoryType.PRODUTO.value)
    status = Column(String(20), nullable=False, default=ProductCategoryStatus.ATIVA.value)

    # Configurações
    requires_approval = Column(Boolean, default=False)
    approval_limit = Column(String(20), nullable=True)  # Valor acima do qual requer aprovação
    default_account_code = Column(String(20), nullable=True)  # Código contábil padrão
    default_cost_center = Column(String(50), nullable=True)  # Centro de custo padrão

    # Metadados
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    sort_order = Column(Integer, default=0)

    # Contadores
    product_count = Column(Integer, default=0)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    parent = relationship("ProductCategory", remote_side=[id], backref="children")  # noqa: A003
    products: list["Product"] = relationship("Product", back_populates="category")

    __table_args__ = (
        Index("ix_product_categories_code", "code"),
        Index("ix_product_categories_name", "name"),
        Index("ix_product_categories_type", "category_type"),
        Index("ix_product_categories_condominio_status", "condominio_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<ProductCategory {self.name}>"

    @property
    def is_active(self) -> bool:
        """Verifica se categoria está ativa."""
        return self.status == ProductCategoryStatus.ATIVA.value and self.ativo

    @property
    def full_path(self) -> str:
        """Retorna caminho completo da categoria."""
        return self.path or f"/{self.id}"

    @property
    def has_children(self) -> bool:
        """Verifica se tem subcategorias."""
        return bool(self.children) if hasattr(self, "children") else False

    def update_path(self, parent_path: str | None = None) -> None:
        """Atualiza o path baseado no parent."""
        if parent_path:
            self.path = f"{parent_path}/{self.id}"
            self.depth = parent_path.count("/")
        else:
            self.path = f"/{self.id}"
            self.depth = 0

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "category_type": self.category_type,
            "status": self.status,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "depth": self.depth,
            "product_count": self.product_count,
            "is_active": self.is_active,
        }
