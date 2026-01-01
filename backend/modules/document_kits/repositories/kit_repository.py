"""Repository de Kits Documentais."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from modules.document_kits.models.document_kit import (
    DocumentKit,
    DocumentKitItem,
    DocumentKitAssignment,
    DocumentKitItemStatus,
    KitType,
    KitStatus,
    AssignmentStatus,
    ItemStatusEnum,
    EntityType,
)


class DocumentKitRepository:
    """Repository para operacoes de Kits Documentais."""

    def __init__(self, db: Session):
        """Inicializa repository."""
        self.db = db

    # === DocumentKit CRUD ===

    def create_kit(self, kit: DocumentKit) -> DocumentKit:
        """Cria um kit."""
        self.db.add(kit)
        self.db.commit()
        self.db.refresh(kit)
        return kit

    def get_kit_by_id(
        self,
        kit_id: UUID,
        condominio_id: UUID,
    ) -> Optional[DocumentKit]:
        """Busca kit por ID."""
        return self.db.query(DocumentKit).filter(
            and_(
                DocumentKit.id == kit_id,
                DocumentKit.condominio_id == condominio_id,
            )
        ).options(joinedload(DocumentKit.itens)).first()

    def get_kit_by_codigo(
        self,
        codigo: str,
        condominio_id: UUID,
    ) -> Optional[DocumentKit]:
        """Busca kit por codigo."""
        return self.db.query(DocumentKit).filter(
            and_(
                DocumentKit.codigo == codigo,
                DocumentKit.condominio_id == condominio_id,
            )
        ).first()

    def list_kits(
        self,
        condominio_id: UUID,
        tipo: Optional[KitType] = None,
        status: Optional[KitStatus] = None,
        is_template: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DocumentKit]:
        """Lista kits com filtros."""
        query = self.db.query(DocumentKit).filter(
            DocumentKit.condominio_id == condominio_id
        )

        if tipo:
            query = query.filter(DocumentKit.tipo == tipo)
        if status:
            query = query.filter(DocumentKit.status == status)
        if is_template is not None:
            query = query.filter(DocumentKit.is_template == is_template)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    DocumentKit.nome.ilike(search_filter),
                    DocumentKit.codigo.ilike(search_filter),
                    DocumentKit.descricao.ilike(search_filter),
                )
            )

        return query.order_by(DocumentKit.nome).offset(skip).limit(limit).all()

    def count_kits(
        self,
        condominio_id: UUID,
        tipo: Optional[KitType] = None,
        status: Optional[KitStatus] = None,
    ) -> int:
        """Conta kits."""
        query = self.db.query(func.count(DocumentKit.id)).filter(
            DocumentKit.condominio_id == condominio_id
        )

        if tipo:
            query = query.filter(DocumentKit.tipo == tipo)
        if status:
            query = query.filter(DocumentKit.status == status)

        return query.scalar() or 0

    def update_kit(self, kit: DocumentKit) -> DocumentKit:
        """Atualiza kit."""
        self.db.commit()
        self.db.refresh(kit)
        return kit

    def delete_kit(self, kit: DocumentKit) -> None:
        """Remove kit."""
        self.db.delete(kit)
        self.db.commit()

    # === DocumentKitItem CRUD ===

    def create_item(self, item: DocumentKitItem) -> DocumentKitItem:
        """Cria item de kit."""
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_item_by_id(
        self,
        item_id: UUID,
        condominio_id: UUID,
    ) -> Optional[DocumentKitItem]:
        """Busca item por ID."""
        return self.db.query(DocumentKitItem).filter(
            and_(
                DocumentKitItem.id == item_id,
                DocumentKitItem.condominio_id == condominio_id,
            )
        ).first()

    def list_items_by_kit(
        self,
        kit_id: UUID,
        condominio_id: UUID,
        only_active: bool = True,
    ) -> List[DocumentKitItem]:
        """Lista itens de um kit."""
        query = self.db.query(DocumentKitItem).filter(
            and_(
                DocumentKitItem.kit_id == kit_id,
                DocumentKitItem.condominio_id == condominio_id,
            )
        )

        if only_active:
            query = query.filter(DocumentKitItem.is_ativo.is_(True))

        return query.order_by(DocumentKitItem.ordem).all()

    def update_item(self, item: DocumentKitItem) -> DocumentKitItem:
        """Atualiza item."""
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item: DocumentKitItem) -> None:
        """Remove item."""
        self.db.delete(item)
        self.db.commit()

    def reorder_items(
        self,
        kit_id: UUID,
        condominio_id: UUID,
        item_orders: List[dict],
    ) -> None:
        """Reordena itens do kit."""
        for order_data in item_orders:
            item_id = order_data.get("item_id")
            ordem = order_data.get("ordem")
            self.db.query(DocumentKitItem).filter(
                and_(
                    DocumentKitItem.id == item_id,
                    DocumentKitItem.kit_id == kit_id,
                    DocumentKitItem.condominio_id == condominio_id,
                )
            ).update({"ordem": ordem})
        self.db.commit()

    # === DocumentKitAssignment CRUD ===

    def create_assignment(
        self,
        assignment: DocumentKitAssignment,
    ) -> DocumentKitAssignment:
        """Cria atribuicao de kit."""
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def get_assignment_by_id(
        self,
        assignment_id: UUID,
        condominio_id: UUID,
    ) -> Optional[DocumentKitAssignment]:
        """Busca atribuicao por ID."""
        return self.db.query(DocumentKitAssignment).filter(
            and_(
                DocumentKitAssignment.id == assignment_id,
                DocumentKitAssignment.condominio_id == condominio_id,
            )
        ).options(
            joinedload(DocumentKitAssignment.kit),
            joinedload(DocumentKitAssignment.item_statuses),
        ).first()

    def list_assignments(
        self,
        condominio_id: UUID,
        kit_id: Optional[UUID] = None,
        entity_type: Optional[EntityType] = None,
        entity_id: Optional[UUID] = None,
        status: Optional[AssignmentStatus] = None,
        vencidos: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DocumentKitAssignment]:
        """Lista atribuicoes com filtros."""
        query = self.db.query(DocumentKitAssignment).filter(
            DocumentKitAssignment.condominio_id == condominio_id
        )

        if kit_id:
            query = query.filter(DocumentKitAssignment.kit_id == kit_id)
        if entity_type:
            query = query.filter(DocumentKitAssignment.entity_type == entity_type)
        if entity_id:
            query = query.filter(DocumentKitAssignment.entity_id == entity_id)
        if status:
            query = query.filter(DocumentKitAssignment.status == status)
        if vencidos is True:
            query = query.filter(
                and_(
                    DocumentKitAssignment.data_limite < datetime.utcnow(),
                    DocumentKitAssignment.status.notin_([
                        AssignmentStatus.COMPLETO,
                        AssignmentStatus.CANCELADO,
                    ]),
                )
            )

        return query.order_by(
            DocumentKitAssignment.data_limite.asc()
        ).offset(skip).limit(limit).all()

    def count_assignments(
        self,
        condominio_id: UUID,
        status: Optional[AssignmentStatus] = None,
    ) -> int:
        """Conta atribuicoes."""
        query = self.db.query(func.count(DocumentKitAssignment.id)).filter(
            DocumentKitAssignment.condominio_id == condominio_id
        )

        if status:
            query = query.filter(DocumentKitAssignment.status == status)

        return query.scalar() or 0

    def count_vencidos(self, condominio_id: UUID) -> int:
        """Conta atribuicoes vencidas."""
        return self.db.query(func.count(DocumentKitAssignment.id)).filter(
            and_(
                DocumentKitAssignment.condominio_id == condominio_id,
                DocumentKitAssignment.data_limite < datetime.utcnow(),
                DocumentKitAssignment.status.notin_([
                    AssignmentStatus.COMPLETO,
                    AssignmentStatus.CANCELADO,
                ]),
            )
        ).scalar() or 0

    def update_assignment(
        self,
        assignment: DocumentKitAssignment,
    ) -> DocumentKitAssignment:
        """Atualiza atribuicao."""
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def delete_assignment(self, assignment: DocumentKitAssignment) -> None:
        """Remove atribuicao."""
        self.db.delete(assignment)
        self.db.commit()

    # === DocumentKitItemStatus CRUD ===

    def create_item_status(
        self,
        item_status: DocumentKitItemStatus,
    ) -> DocumentKitItemStatus:
        """Cria status de item."""
        self.db.add(item_status)
        self.db.commit()
        self.db.refresh(item_status)
        return item_status

    def create_item_statuses_bulk(
        self,
        item_statuses: List[DocumentKitItemStatus],
    ) -> List[DocumentKitItemStatus]:
        """Cria multiplos status de item."""
        self.db.add_all(item_statuses)
        self.db.commit()
        for status in item_statuses:
            self.db.refresh(status)
        return item_statuses

    def get_item_status_by_id(
        self,
        status_id: UUID,
        condominio_id: UUID,
    ) -> Optional[DocumentKitItemStatus]:
        """Busca status por ID."""
        return self.db.query(DocumentKitItemStatus).filter(
            and_(
                DocumentKitItemStatus.id == status_id,
                DocumentKitItemStatus.condominio_id == condominio_id,
            )
        ).first()

    def list_item_statuses_by_assignment(
        self,
        assignment_id: UUID,
        condominio_id: UUID,
        status: Optional[ItemStatusEnum] = None,
    ) -> List[DocumentKitItemStatus]:
        """Lista status de itens de uma atribuicao."""
        query = self.db.query(DocumentKitItemStatus).filter(
            and_(
                DocumentKitItemStatus.assignment_id == assignment_id,
                DocumentKitItemStatus.condominio_id == condominio_id,
            )
        )

        if status:
            query = query.filter(DocumentKitItemStatus.status == status)

        return query.all()

    def update_item_status(
        self,
        item_status: DocumentKitItemStatus,
    ) -> DocumentKitItemStatus:
        """Atualiza status de item."""
        self.db.commit()
        self.db.refresh(item_status)
        return item_status

    # === Estatisticas ===

    def get_stats(self, condominio_id: UUID) -> dict:
        """Retorna estatisticas de kits."""
        total_kits = self.count_kits(condominio_id)
        kits_ativos = self.count_kits(condominio_id, status=KitStatus.ATIVO)
        kits_inativos = self.count_kits(condominio_id, status=KitStatus.INATIVO)

        total_assignments = self.count_assignments(condominio_id)
        assignments_pendentes = self.count_assignments(
            condominio_id, status=AssignmentStatus.PENDENTE
        )
        assignments_completos = self.count_assignments(
            condominio_id, status=AssignmentStatus.COMPLETO
        )
        assignments_vencidos = self.count_vencidos(condominio_id)

        taxa_conclusao = 0.0
        if total_assignments > 0:
            taxa_conclusao = (assignments_completos / total_assignments) * 100

        # Por tipo
        por_tipo = {}
        for kit_type in KitType:
            count = self.count_kits(condominio_id, tipo=kit_type)
            if count > 0:
                por_tipo[kit_type.value] = count

        # Por status
        por_status = {}
        for status in KitStatus:
            count = self.count_kits(condominio_id, status=status)
            if count > 0:
                por_status[status.value] = count

        return {
            "total_kits": total_kits,
            "kits_ativos": kits_ativos,
            "kits_inativos": kits_inativos,
            "total_assignments": total_assignments,
            "assignments_pendentes": assignments_pendentes,
            "assignments_completos": assignments_completos,
            "assignments_vencidos": assignments_vencidos,
            "taxa_conclusao": round(taxa_conclusao, 2),
            "tempo_medio_conclusao_dias": 0.0,
            "por_tipo": por_tipo,
            "por_status": por_status,
        }

    def get_entity_compliance(
        self,
        condominio_id: UUID,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> dict:
        """Retorna conformidade de uma entidade."""
        assignments = self.list_assignments(
            condominio_id=condominio_id,
            entity_type=entity_type,
            entity_id=entity_id,
        )

        total = len(assignments)
        completos = sum(
            1 for a in assignments if a.status == AssignmentStatus.COMPLETO
        )
        pendentes = sum(
            1 for a in assignments if a.status in (
                AssignmentStatus.PENDENTE,
                AssignmentStatus.EM_ANDAMENTO,
                AssignmentStatus.AGUARDANDO_DOCUMENTOS,
            )
        )
        vencidos = sum(1 for a in assignments if a.is_vencido)

        taxa = (completos / total * 100) if total > 0 else 0.0

        return {
            "total_kits_atribuidos": total,
            "kits_completos": completos,
            "kits_pendentes": pendentes,
            "kits_vencidos": vencidos,
            "taxa_conformidade": round(taxa, 2),
        }
