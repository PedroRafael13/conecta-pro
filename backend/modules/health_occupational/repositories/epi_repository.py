"""
Repository EPI - Acesso a Dados de Equipamentos de Protecao
=============================================================

Camada de acesso a dados para entidades de EPI.
"""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from modules.health_occupational.models.epi import (
    EPI,
    EPIDelivery,
    EPIInventory,
)


class EPIRepository:
    """Repository para entidades de EPI."""

    def __init__(self, db: Session):
        self.db = db

    # ==========================================================================
    # EPI Catalog Repository
    # ==========================================================================

    def create_epi(self, epi: EPI) -> EPI:
        """Cria novo EPI."""
        self.db.add(epi)
        self.db.commit()
        self.db.refresh(epi)
        return epi

    def get_epi_by_id(self, epi_id: UUID) -> Optional[EPI]:
        """Busca EPI por ID."""
        return self.db.query(EPI).filter(EPI.id == epi_id).first()

    def get_epi_by_ca(self, ca_number: str) -> Optional[EPI]:
        """Busca EPI pelo CA."""
        return self.db.query(EPI).filter(EPI.ca_number == ca_number).first()

    def get_epi_by_codigo(self, codigo: str) -> Optional[EPI]:
        """Busca EPI pelo codigo interno."""
        return self.db.query(EPI).filter(EPI.codigo_interno == codigo).first()

    def list_epis(
        self,
        categoria: Optional[str] = None,
        ativo: Optional[bool] = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EPI]:
        """Lista EPIs com filtros."""
        query = self.db.query(EPI)

        if categoria:
            query = query.filter(EPI.categoria == categoria)
        if ativo is not None:
            query = query.filter(EPI.ativo == ativo)

        return query.order_by(EPI.nome).offset(offset).limit(limit).all()

    def count_epis(
        self,
        categoria: Optional[str] = None,
        ativo: Optional[bool] = True,
    ) -> int:
        """Conta EPIs."""
        query = self.db.query(EPI)

        if categoria:
            query = query.filter(EPI.categoria == categoria)
        if ativo is not None:
            query = query.filter(EPI.ativo == ativo)

        return query.count()

    def search_epis(self, termo: str, limit: int = 20) -> List[EPI]:
        """Busca EPIs por termo."""
        return self.db.query(EPI).filter(
            or_(
                EPI.nome.ilike(f"%{termo}%"),
                EPI.ca_number.ilike(f"%{termo}%"),
                EPI.fabricante.ilike(f"%{termo}%"),
            ),
            EPI.ativo == True,
        ).limit(limit).all()

    def update_epi(self, epi: EPI) -> EPI:
        """Atualiza EPI."""
        self.db.commit()
        self.db.refresh(epi)
        return epi

    def deactivate_epi(self, epi_id: UUID) -> Optional[EPI]:
        """Desativa EPI."""
        epi = self.get_epi_by_id(epi_id)
        if epi:
            epi.ativo = False
            self.db.commit()
            self.db.refresh(epi)
        return epi

    # ==========================================================================
    # EPI Delivery Repository
    # ==========================================================================

    def create_delivery(self, delivery: EPIDelivery) -> EPIDelivery:
        """Cria nova entrega."""
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def get_delivery_by_id(self, delivery_id: UUID) -> Optional[EPIDelivery]:
        """Busca entrega por ID."""
        return self.db.query(EPIDelivery).filter(
            EPIDelivery.id == delivery_id
        ).first()

    def get_deliveries_by_funcionario(
        self,
        funcionario_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EPIDelivery]:
        """Lista entregas de um funcionario."""
        return self.db.query(EPIDelivery).filter(
            EPIDelivery.funcionario_id == funcionario_id
        ).order_by(EPIDelivery.data_entrega.desc()).offset(offset).limit(limit).all()

    def count_deliveries_by_funcionario(self, funcionario_id: UUID) -> int:
        """Conta entregas de um funcionario."""
        return self.db.query(EPIDelivery).filter(
            EPIDelivery.funcionario_id == funcionario_id
        ).count()

    def get_active_deliveries_by_funcionario(
        self,
        funcionario_id: UUID,
    ) -> List[EPIDelivery]:
        """Lista entregas ativas (nao devolvidas e nao vencidas) de um funcionario."""
        today = date.today()
        return self.db.query(EPIDelivery).filter(
            EPIDelivery.funcionario_id == funcionario_id,
            EPIDelivery.devolvido == False,
            or_(
                EPIDelivery.data_validade == None,
                EPIDelivery.data_validade >= today,
            ),
        ).all()

    def get_expired_deliveries_by_funcionario(
        self,
        funcionario_id: UUID,
    ) -> List[EPIDelivery]:
        """Lista entregas vencidas de um funcionario."""
        today = date.today()
        return self.db.query(EPIDelivery).filter(
            EPIDelivery.funcionario_id == funcionario_id,
            EPIDelivery.devolvido == False,
            EPIDelivery.data_validade < today,
        ).all()

    def get_deliveries_by_epi(
        self,
        epi_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EPIDelivery]:
        """Lista entregas de um EPI."""
        return self.db.query(EPIDelivery).filter(
            EPIDelivery.epi_id == epi_id
        ).order_by(EPIDelivery.data_entrega.desc()).offset(offset).limit(limit).all()

    def get_unsigned_deliveries(self) -> List[EPIDelivery]:
        """Lista entregas sem assinatura."""
        return self.db.query(EPIDelivery).filter(
            EPIDelivery.assinatura_funcionario == False,
            EPIDelivery.devolvido == False,
        ).order_by(EPIDelivery.data_entrega).all()

    def update_delivery(self, delivery: EPIDelivery) -> EPIDelivery:
        """Atualiza entrega."""
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    # ==========================================================================
    # EPI Inventory Repository
    # ==========================================================================

    def create_inventory(self, inventory: EPIInventory) -> EPIInventory:
        """Cria registro de estoque."""
        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)
        return inventory

    def get_inventory_by_epi(self, epi_id: UUID) -> Optional[EPIInventory]:
        """Busca estoque de um EPI."""
        return self.db.query(EPIInventory).filter(
            EPIInventory.epi_id == epi_id
        ).first()

    def list_inventory(
        self,
        low_stock_only: bool = False,
    ) -> List[EPIInventory]:
        """Lista estoque."""
        query = self.db.query(EPIInventory)

        if low_stock_only:
            query = query.filter(
                EPIInventory.quantidade_atual < EPIInventory.quantidade_minima
            )

        return query.all()

    def get_low_stock_items(self) -> List[EPIInventory]:
        """Lista itens com estoque baixo."""
        return self.db.query(EPIInventory).filter(
            EPIInventory.quantidade_atual < EPIInventory.quantidade_minima
        ).all()

    def update_inventory(self, inventory: EPIInventory) -> EPIInventory:
        """Atualiza estoque."""
        self.db.commit()
        self.db.refresh(inventory)
        return inventory

    def adjust_inventory(
        self,
        epi_id: UUID,
        quantidade: int,
        operacao: str = "saida",
    ) -> Optional[EPIInventory]:
        """Ajusta quantidade no estoque."""
        inventory = self.get_inventory_by_epi(epi_id)
        if not inventory:
            return None

        if operacao == "entrada":
            inventory.quantidade_atual += quantidade
            inventory.ultima_entrada = datetime.utcnow()
        else:
            inventory.quantidade_atual -= quantidade
            inventory.ultima_saida = datetime.utcnow()

        self.db.commit()
        self.db.refresh(inventory)
        return inventory

    # ==========================================================================
    # Statistics
    # ==========================================================================

    def get_delivery_statistics(
        self,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """Retorna estatisticas de entregas em um periodo."""
        total = self.db.query(EPIDelivery).filter(
            EPIDelivery.data_entrega >= datetime.combine(start_date, datetime.min.time()),
            EPIDelivery.data_entrega <= datetime.combine(end_date, datetime.max.time()),
        ).count()

        by_motivo = {}
        for motivo in ["admissao", "substituicao", "desgaste", "perda", "troca_funcao"]:
            by_motivo[motivo] = self.db.query(EPIDelivery).filter(
                EPIDelivery.data_entrega >= datetime.combine(start_date, datetime.min.time()),
                EPIDelivery.data_entrega <= datetime.combine(end_date, datetime.max.time()),
                EPIDelivery.motivo == motivo,
            ).count()

        pending_signatures = self.db.query(EPIDelivery).filter(
            EPIDelivery.assinatura_funcionario == False,
            EPIDelivery.devolvido == False,
        ).count()

        low_stock = len(self.get_low_stock_items())

        return {
            "total_entregas": total,
            "entregas_por_motivo": by_motivo,
            "assinaturas_pendentes": pending_signatures,
            "itens_baixo_estoque": low_stock,
            "periodo": {
                "inicio": start_date.isoformat(),
                "fim": end_date.isoformat(),
            },
        }

    def get_epi_usage_ranking(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna ranking de EPIs mais utilizados."""
        results = self.db.query(
            EPIDelivery.epi_id,
            func.count(EPIDelivery.id).label("total_entregas"),
            func.sum(EPIDelivery.quantidade).label("total_quantidade"),
        ).group_by(
            EPIDelivery.epi_id
        ).order_by(
            func.count(EPIDelivery.id).desc()
        ).limit(limit).all()

        ranking = []
        for row in results:
            epi = self.get_epi_by_id(row.epi_id)
            ranking.append({
                "epi_id": str(row.epi_id),
                "epi_nome": epi.nome if epi else None,
                "total_entregas": row.total_entregas,
                "total_quantidade": row.total_quantidade or 0,
            })

        return ranking
