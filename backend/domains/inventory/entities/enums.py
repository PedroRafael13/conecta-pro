"""
domains/inventory/entities/enums.py - INVENTORY ENUMS
=====================================================
Enterprise inventory management enumerations
"""

from enum import Enum
from typing import List


class ProductType(str, Enum):
    """Tipo de produto."""

    RAW_MATERIAL = "raw_material"       # Materia prima
    FINISHED_GOODS = "finished_goods"   # Produto acabado
    SEMI_FINISHED = "semi_finished"     # Semi-acabado
    CONSUMABLE = "consumable"           # Material de consumo
    PACKAGING = "packaging"             # Embalagem
    SPARE_PARTS = "spare_parts"         # Pecas de reposicao
    SERVICE = "service"                 # Servico
    FIXED_ASSET = "fixed_asset"         # Ativo imobilizado

    def is_stockable(self) -> bool:
        """Verifica se pode ser estocado."""
        return self != self.SERVICE

    def requires_batch(self) -> bool:
        """Verifica se requer controle de lote."""
        return self in [self.RAW_MATERIAL, self.FINISHED_GOODS, self.SEMI_FINISHED]


class ProductStatus(str, Enum):
    """Status do produto."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    PENDING_APPROVAL = "pending"
    BLOCKED = "blocked"


class StockMovementType(str, Enum):
    """Tipo de movimentacao de estoque."""

    # Entradas
    PURCHASE = "purchase"               # Compra
    PRODUCTION = "production"           # Producao
    RETURN_CUSTOMER = "return_customer" # Devolucao de cliente
    TRANSFER_IN = "transfer_in"         # Transferencia entrada
    ADJUSTMENT_IN = "adjustment_in"     # Ajuste entrada
    INITIAL = "initial"                 # Saldo inicial

    # Saidas
    SALE = "sale"                       # Venda
    CONSUMPTION = "consumption"         # Consumo interno
    RETURN_SUPPLIER = "return_supplier" # Devolucao a fornecedor
    TRANSFER_OUT = "transfer_out"       # Transferencia saida
    ADJUSTMENT_OUT = "adjustment_out"   # Ajuste saida
    LOSS = "loss"                       # Perda/Quebra
    WRITE_OFF = "write_off"             # Baixa

    def is_entry(self) -> bool:
        """Verifica se e movimento de entrada."""
        return self in [
            self.PURCHASE, self.PRODUCTION, self.RETURN_CUSTOMER,
            self.TRANSFER_IN, self.ADJUSTMENT_IN, self.INITIAL
        ]

    def is_exit(self) -> bool:
        """Verifica se e movimento de saida."""
        return not self.is_entry()

    def affects_cost(self) -> bool:
        """Verifica se afeta custo medio."""
        return self in [self.PURCHASE, self.PRODUCTION, self.INITIAL]

    def requires_document(self) -> bool:
        """Verifica se requer documento fiscal."""
        return self in [
            self.PURCHASE, self.SALE, self.RETURN_CUSTOMER, self.RETURN_SUPPLIER
        ]


class WarehouseType(str, Enum):
    """Tipo de almoxarifado."""

    MAIN = "main"                   # Principal
    TRANSIT = "transit"             # Em transito
    PRODUCTION = "production"       # Producao
    QUARANTINE = "quarantine"       # Quarentena
    REJECTED = "rejected"           # Rejeitados
    CONSIGNMENT = "consignment"     # Consignacao
    EXTERNAL = "external"           # Externo (terceiros)


class StockStatus(str, Enum):
    """Status do estoque."""

    AVAILABLE = "available"         # Disponivel
    RESERVED = "reserved"           # Reservado
    IN_TRANSIT = "in_transit"       # Em transito
    QUARANTINE = "quarantine"       # Em quarentena
    BLOCKED = "blocked"             # Bloqueado
    EXPIRED = "expired"             # Vencido

    def can_be_sold(self) -> bool:
        """Verifica se pode ser vendido."""
        return self == self.AVAILABLE


class UnitOfMeasure(str, Enum):
    """Unidade de medida."""

    # Unidades
    UNIT = "UN"
    PIECE = "PC"
    PAIR = "PAR"
    DOZEN = "DZ"
    HUNDRED = "CENT"
    THOUSAND = "MIL"

    # Peso
    GRAM = "G"
    KILOGRAM = "KG"
    TON = "TON"

    # Volume
    MILLILITER = "ML"
    LITER = "L"
    CUBIC_METER = "M3"

    # Comprimento
    METER = "M"
    CENTIMETER = "CM"
    SQUARE_METER = "M2"

    # Tempo
    HOUR = "HR"
    DAY = "DIA"
    MONTH = "MES"

    # Outros
    KIT = "KIT"
    BOX = "CX"
    PACK = "PCT"


class InventoryValuationMethod(str, Enum):
    """Metodo de valorizacao do estoque."""

    AVERAGE_COST = "average"        # Custo medio ponderado
    FIFO = "fifo"                   # Primeiro a entrar, primeiro a sair
    LIFO = "lifo"                   # Ultimo a entrar, primeiro a sair
    SPECIFIC = "specific"           # Identificacao especifica
    STANDARD = "standard"           # Custo padrao


class ReorderPointStatus(str, Enum):
    """Status do ponto de reposicao."""

    NORMAL = "normal"               # Nivel normal
    WARNING = "warning"             # Alerta (proximo do minimo)
    CRITICAL = "critical"           # Critico (abaixo do minimo)
    STOCKOUT = "stockout"           # Ruptura (zerado)
    OVERSTOCK = "overstock"         # Excesso de estoque


class BatchStatus(str, Enum):
    """Status do lote."""

    ACTIVE = "active"
    QUARANTINE = "quarantine"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONSUMED = "consumed"


class InventoryCountStatus(str, Enum):
    """Status da contagem de inventario."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    ADJUSTED = "adjusted"
    CANCELLED = "cancelled"
