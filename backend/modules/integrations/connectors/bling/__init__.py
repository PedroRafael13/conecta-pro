"""
Conector Bling ERP
Sprint 33: Integration Framework
"""

from modules.integrations.connectors.bling.connector import BlingConnector
from modules.integrations.connectors.bling.schemas import (
    BlingContato,
    BlingContatoCreate,
    BlingProduto,
    BlingProdutoCreate,
    BlingEstoqueSaldo,
    BlingPedido,
    BlingPedidoItem,
    BlingNFe,
    BlingEndereco,
    BlingPaginatedResponse,
    BlingSingleResponse,
    BlingErrorResponse,
)
from modules.integrations.connectors.bling.mappers import (
    bling_contato_to_customer,
    bling_contato_to_supplier,
    customer_to_bling_contato,
    supplier_to_bling_contato,
    bling_produto_to_product,
    product_to_bling_produto,
    bling_nfe_to_nfe,
    bling_pedido_to_order,
    compute_bling_entity_hash,
)

__all__ = [
    # Connector
    "BlingConnector",
    # Schemas
    "BlingContato",
    "BlingContatoCreate",
    "BlingProduto",
    "BlingProdutoCreate",
    "BlingEstoqueSaldo",
    "BlingPedido",
    "BlingPedidoItem",
    "BlingNFe",
    "BlingEndereco",
    "BlingPaginatedResponse",
    "BlingSingleResponse",
    "BlingErrorResponse",
    # Mappers
    "bling_contato_to_customer",
    "bling_contato_to_supplier",
    "customer_to_bling_contato",
    "supplier_to_bling_contato",
    "bling_produto_to_product",
    "product_to_bling_produto",
    "bling_nfe_to_nfe",
    "bling_pedido_to_order",
    "compute_bling_entity_hash",
]
