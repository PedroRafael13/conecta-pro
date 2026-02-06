"""
Service EPI (NR-6) - Equipamentos de Protecao Individual
=========================================================

Logica de negocio para gestao de EPIs.
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session

from modules.health_occupational.models.epi import (
    EPI,
    EPIDelivery,
    EPIInventory,
    EPICategory,
    EPIStatus,
    DeliveryReason,
)
from modules.health_occupational.schemas.epi import (
    EPICreateRequest,
    EPIUpdateRequest,
    EPIDeliveryRequest,
    EPIDeliveryUpdateRequest,
    EPIInventoryUpdateRequest,
)

logger = logging.getLogger(__name__)


class EPIService:
    """Service para gerenciamento de EPIs (NR-6)."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    # ==========================================================================
    # EPI Catalog Operations
    # ==========================================================================

    def create_epi(self, request: EPICreateRequest, created_by: Optional[UUID] = None) -> EPI:
        """
        Cadastra novo EPI.

        Args:
            request: Dados do EPI.
            created_by: UUID do usuario que criou.

        Returns:
            EPI cadastrado.
        """
        # Verificar se CA ja existe
        existing = self.db.query(EPI).filter(EPI.ca_number == request.ca_number).first()
        if existing:
            raise ValueError(f"EPI com CA {request.ca_number} ja cadastrado")

        epi = EPI(
            nome=request.nome,
            descricao=request.descricao,
            codigo_interno=request.codigo_interno,
            categoria=request.categoria,
            ca_number=request.ca_number,
            ca_validade=request.ca_validade,
            fabricante=request.fabricante,
            modelo=request.modelo,
            validade_dias=request.validade_dias,
            especificacoes=request.especificacoes,
            riscos_protegidos=request.riscos_protegidos,
            instrucoes_uso=request.instrucoes_uso,
            instrucoes_higienizacao=request.instrucoes_higienizacao,
            instrucoes_armazenamento=request.instrucoes_armazenamento,
            imagem_url=request.imagem_url,
            created_by=created_by,
        )

        self.db.add(epi)
        self.db.flush()

        # Criar registro de estoque
        inventory = EPIInventory(
            epi_id=epi.id,
            quantidade_atual=0,
            quantidade_minima=10,
        )
        self.db.add(inventory)

        self.db.commit()
        self.db.refresh(epi)

        logger.info("EPI cadastrado: nome=%s, CA=%s", request.nome, request.ca_number)
        return epi

    def get_epi(self, epi_id: UUID) -> Optional[EPI]:
        """Busca EPI por ID."""
        return self.db.query(EPI).filter(EPI.id == epi_id).first()

    def get_epi_by_ca(self, ca_number: str) -> Optional[EPI]:
        """Busca EPI pelo numero do CA."""
        return self.db.query(EPI).filter(EPI.ca_number == ca_number).first()

    def update_epi(self, epi_id: UUID, request: EPIUpdateRequest) -> Optional[EPI]:
        """Atualiza EPI."""
        epi = self.get_epi(epi_id)
        if not epi:
            return None

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(epi, field, value)

        self.db.commit()
        self.db.refresh(epi)
        return epi

    def list_epis(
        self,
        categoria: Optional[str] = None,
        ativo: Optional[bool] = True,
        page: int = 1,
        size: int = 20,
    ) -> Dict[str, Any]:
        """Lista EPIs cadastrados."""
        query = self.db.query(EPI)

        if categoria:
            query = query.filter(EPI.categoria == categoria)

        if ativo is not None:
            query = query.filter(EPI.ativo == ativo)

        total = query.count()
        epis = query.order_by(EPI.nome).offset((page - 1) * size).limit(size).all()

        return {
            "items": epis,
            "total": total,
            "page": page,
            "size": size,
        }

    def deactivate_epi(self, epi_id: UUID) -> Optional[EPI]:
        """Desativa EPI."""
        epi = self.get_epi(epi_id)
        if not epi:
            return None

        epi.ativo = False
        self.db.commit()
        self.db.refresh(epi)
        return epi

    # ==========================================================================
    # EPI Delivery Operations
    # ==========================================================================

    def register_delivery(
        self,
        request: EPIDeliveryRequest,
        entregue_por: Optional[UUID] = None,
    ) -> EPIDelivery:
        """
        Registra entrega de EPI para funcionario.

        Args:
            request: Dados da entrega.
            entregue_por: UUID de quem entregou.

        Returns:
            EPIDelivery registrada.
        """
        epi = self.get_epi(request.epi_id)
        if not epi:
            raise ValueError(f"EPI {request.epi_id} nao encontrado")

        if not epi.ativo:
            raise ValueError("EPI inativo, nao pode ser entregue")

        # Verificar estoque
        inventory = self.get_inventory(request.epi_id)
        if inventory and inventory.quantidade_atual < request.quantidade:
            raise ValueError(
                f"Estoque insuficiente: disponivel={inventory.quantidade_atual}, "
                f"solicitado={request.quantidade}"
            )

        # Calcular validade
        data_validade = date.today() + timedelta(days=epi.validade_dias)

        delivery = EPIDelivery(
            epi_id=request.epi_id,
            funcionario_id=request.funcionario_id,
            quantidade=request.quantidade,
            motivo=request.motivo,
            ca_number=request.ca_number,
            data_validade=data_validade,
            observacoes=request.observacoes,
            treinamento_realizado=request.treinamento_realizado,
            data_treinamento=datetime.utcnow() if request.treinamento_realizado else None,
            entregue_por=entregue_por,
        )

        self.db.add(delivery)

        # Atualizar estoque
        if inventory:
            inventory.quantidade_atual -= request.quantidade
            inventory.ultima_saida = datetime.utcnow()

        self.db.commit()
        self.db.refresh(delivery)

        logger.info(
            "Entrega de EPI registrada: funcionario=%s, epi=%s, qtd=%d",
            request.funcionario_id,
            request.epi_id,
            request.quantidade,
        )

        return delivery

    def get_delivery(self, delivery_id: UUID) -> Optional[EPIDelivery]:
        """Busca entrega por ID."""
        return self.db.query(EPIDelivery).filter(EPIDelivery.id == delivery_id).first()

    def update_delivery(
        self,
        delivery_id: UUID,
        request: EPIDeliveryUpdateRequest,
    ) -> Optional[EPIDelivery]:
        """Atualiza registro de entrega."""
        delivery = self.get_delivery(delivery_id)
        if not delivery:
            return None

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(delivery, field, value)

        if request.assinatura_funcionario:
            delivery.data_assinatura = datetime.utcnow()

        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def register_return(
        self,
        delivery_id: UUID,
        motivo: str,
        condicao: str,
    ) -> Optional[EPIDelivery]:
        """Registra devolucao de EPI."""
        delivery = self.get_delivery(delivery_id)
        if not delivery:
            return None

        delivery.devolvido = True
        delivery.data_devolucao = datetime.utcnow()
        delivery.motivo_devolucao = motivo
        delivery.condicao_devolucao = condicao

        # Se em boa condicao, devolver ao estoque
        if condicao == "bom":
            inventory = self.get_inventory(delivery.epi_id)
            if inventory:
                inventory.quantidade_atual += delivery.quantidade
                inventory.ultima_entrada = datetime.utcnow()

        self.db.commit()
        self.db.refresh(delivery)

        logger.info(
            "Devolucao de EPI registrada: delivery=%s, condicao=%s",
            delivery_id,
            condicao,
        )

        return delivery

    def get_employee_record(self, funcionario_id: UUID) -> Dict[str, Any]:
        """
        Retorna ficha de EPI do funcionario.

        Args:
            funcionario_id: UUID do funcionario.

        Returns:
            Dict com historico de EPIs.
        """
        deliveries = self.db.query(EPIDelivery).filter(
            EPIDelivery.funcionario_id == funcionario_id
        ).order_by(EPIDelivery.data_entrega.desc()).all()

        active_epis = [d for d in deliveries if not d.devolvido and not d.esta_vencido]
        expired_epis = [d for d in deliveries if not d.devolvido and d.esta_vencido]
        returned_epis = [d for d in deliveries if d.devolvido]

        return {
            "funcionario_id": str(funcionario_id),
            "entregas": deliveries,
            "total_entregas": len(deliveries),
            "epis_ativos": active_epis,
            "epis_vencidos": expired_epis,
            "epis_devolvidos": returned_epis,
        }

    def list_employee_deliveries(
        self,
        funcionario_id: UUID,
        page: int = 1,
        size: int = 20,
    ) -> Dict[str, Any]:
        """Lista entregas de um funcionario."""
        query = self.db.query(EPIDelivery).filter(
            EPIDelivery.funcionario_id == funcionario_id
        )

        total = query.count()
        deliveries = query.order_by(EPIDelivery.data_entrega.desc()).offset(
            (page - 1) * size
        ).limit(size).all()

        return {
            "items": deliveries,
            "total": total,
            "page": page,
            "size": size,
        }

    # ==========================================================================
    # Inventory Operations
    # ==========================================================================

    def get_inventory(self, epi_id: UUID) -> Optional[EPIInventory]:
        """Busca estoque de um EPI."""
        return self.db.query(EPIInventory).filter(EPIInventory.epi_id == epi_id).first()

    def update_inventory(
        self,
        epi_id: UUID,
        request: EPIInventoryUpdateRequest,
    ) -> Optional[EPIInventory]:
        """Atualiza estoque de EPI."""
        inventory = self.get_inventory(epi_id)
        if not inventory:
            return None

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(inventory, field, value)

        self.db.commit()
        self.db.refresh(inventory)
        return inventory

    def add_to_inventory(
        self,
        epi_id: UUID,
        quantidade: int,
        lote: Optional[str] = None,
        validade_lote: Optional[date] = None,
    ) -> EPIInventory:
        """Adiciona itens ao estoque."""
        inventory = self.get_inventory(epi_id)
        if not inventory:
            raise ValueError(f"Estoque para EPI {epi_id} nao encontrado")

        inventory.quantidade_atual += quantidade
        inventory.ultima_entrada = datetime.utcnow()

        if lote:
            inventory.lote_atual = lote
        if validade_lote:
            inventory.data_validade_lote = validade_lote

        self.db.commit()
        self.db.refresh(inventory)

        logger.info("Estoque atualizado: epi=%s, +%d unidades", epi_id, quantidade)
        return inventory

    def list_inventory(
        self,
        categoria: Optional[str] = None,
        low_stock_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Lista estoque de EPIs.

        Args:
            categoria: Filtrar por categoria.
            low_stock_only: Apenas com estoque baixo.

        Returns:
            Lista de itens de estoque.
        """
        query = self.db.query(EPIInventory).join(EPI)

        if categoria:
            query = query.filter(EPI.categoria == categoria)

        if low_stock_only:
            query = query.filter(
                EPIInventory.quantidade_atual < EPIInventory.quantidade_minima
            )

        inventories = query.all()

        result = []
        for inv in inventories:
            epi = self.get_epi(inv.epi_id)
            result.append({
                "epi_id": str(inv.epi_id),
                "epi_nome": epi.nome if epi else None,
                "categoria": epi.categoria if epi else None,
                "ca_number": epi.ca_number if epi else None,
                "quantidade_atual": inv.quantidade_atual,
                "quantidade_minima": inv.quantidade_minima,
                "estoque_baixo": inv.estoque_baixo,
                "local_armazenamento": inv.local_armazenamento,
                "lote_atual": inv.lote_atual,
            })

        return result

    # ==========================================================================
    # EPI Categories Info
    # ==========================================================================

    def get_epi_categories(self) -> Dict[str, Any]:
        """Retorna informacoes sobre categorias de EPI."""
        return {
            "categorias": [
                {"id": "cabeca", "nome": "Protecao da Cabeca", "exemplos": ["capacete", "capuz"]},
                {"id": "olhos", "nome": "Protecao dos Olhos", "exemplos": ["oculos", "mascara_solda"]},
                {"id": "face", "nome": "Protecao da Face", "exemplos": ["protetor_facial", "mascara"]},
                {"id": "auditivo", "nome": "Protecao Auditiva", "exemplos": ["protetor_auricular", "abafador"]},
                {"id": "respiratorio", "nome": "Protecao Respiratoria", "exemplos": ["respirador", "mascara_pff2"]},
                {"id": "tronco", "nome": "Protecao do Tronco", "exemplos": ["avental", "colete"]},
                {"id": "membros_superiores", "nome": "Protecao Membros Superiores", "exemplos": ["luvas", "mangotes"]},
                {"id": "membros_inferiores", "nome": "Protecao Membros Inferiores", "exemplos": ["calcado_seguranca", "perneira"]},
                {"id": "corpo_inteiro", "nome": "Protecao Corpo Inteiro", "exemplos": ["macacao", "conjunto"]},
                {"id": "quedas", "nome": "Protecao Contra Quedas", "exemplos": ["cinturao", "trava_quedas"]},
            ],
        }

    # ==========================================================================
    # Statistics
    # ==========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatisticas de EPI."""
        total_epis = self.db.query(EPI).filter(EPI.ativo == True).count()

        total_deliveries = self.db.query(EPIDelivery).filter(
            EPIDelivery.data_entrega >= datetime(date.today().year, 1, 1)
        ).count()

        low_stock = self.db.query(EPIInventory).filter(
            EPIInventory.quantidade_atual < EPIInventory.quantidade_minima
        ).count()

        pending_signatures = self.db.query(EPIDelivery).filter(
            EPIDelivery.assinatura_funcionario == False,
            EPIDelivery.devolvido == False,
        ).count()

        return {
            "total_epis_ativos": total_epis,
            "entregas_ano": total_deliveries,
            "itens_baixo_estoque": low_stock,
            "assinaturas_pendentes": pending_signatures,
        }
