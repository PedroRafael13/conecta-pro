"""Repository de Kits Documentais - Versão Async."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from modules.document_kits.models.document_kit import (
    AssignmentStatus,
    DocumentKit,
    DocumentKitAssignment,
    DocumentKitItem,
    DocumentKitItemStatus,
    EntityType,
    ItemStatusEnum,
    KitStatus,
    KitType,
)


class DocumentKitRepository:
    """Repository para operacoes de Kits Documentais."""

    def __init__(self, db: AsyncSession):
        """Inicializa repository."""
        self.db = db

    # === DocumentKit CRUD ===

    async def create_kit(self, kit: DocumentKit) -> DocumentKit:
        """Cria um kit."""
        self.db.add(kit)
        await self.db.commit()
        await self.db.refresh(kit)
        return kit

    async def get_kit_by_id(
        self,
        kit_id: UUID,
        condominio_id: UUID,
    ) -> DocumentKit | None:
        """Busca kit por ID."""
        query = (
            select(DocumentKit)
            .where(
                and_(
                    DocumentKit.id == kit_id,
                    DocumentKit.condominio_id == condominio_id,
                )
            )
            .options(joinedload(DocumentKit.itens))
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_kit_by_codigo(
        self,
        codigo: str,
        condominio_id: UUID,
    ) -> DocumentKit | None:
        """Busca kit por codigo."""
        query = select(DocumentKit).where(
            and_(
                DocumentKit.codigo == codigo,
                DocumentKit.condominio_id == condominio_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_kits(
        self,
        condominio_id: UUID,
        tipo: KitType | None = None,
        status: KitStatus | None = None,
        is_template: bool | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DocumentKit]:
        """Lista kits com filtros."""
        conditions = [DocumentKit.condominio_id == condominio_id]

        if tipo:
            conditions.append(DocumentKit.tipo == tipo)
        if status:
            conditions.append(DocumentKit.status == status)
        if is_template is not None:
            conditions.append(DocumentKit.is_template == is_template)
        if search:
            search_filter = f"%{search}%"
            conditions.append(
                or_(
                    DocumentKit.nome.ilike(search_filter),
                    DocumentKit.codigo.ilike(search_filter),
                    DocumentKit.descricao.ilike(search_filter),
                )
            )

        query = select(DocumentKit).where(and_(*conditions)).order_by(DocumentKit.nome).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_kits(
        self,
        condominio_id: UUID,
        tipo: KitType | None = None,
        status: KitStatus | None = None,
    ) -> int:
        """Conta kits."""
        conditions = [DocumentKit.condominio_id == condominio_id]

        if tipo:
            conditions.append(DocumentKit.tipo == tipo)
        if status:
            conditions.append(DocumentKit.status == status)

        query = select(func.count(DocumentKit.id)).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update_kit(self, kit: DocumentKit) -> DocumentKit:
        """Atualiza kit."""
        await self.db.commit()
        await self.db.refresh(kit)
        return kit

    async def delete_kit(self, kit: DocumentKit) -> None:
        """Remove kit."""
        await self.db.delete(kit)
        await self.db.commit()

    # === DocumentKitItem CRUD ===

    async def create_item(self, item: DocumentKitItem) -> DocumentKitItem:
        """Cria item de kit."""
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_item_by_id(
        self,
        item_id: UUID,
        condominio_id: UUID,
    ) -> DocumentKitItem | None:
        """Busca item por ID."""
        query = select(DocumentKitItem).where(
            and_(
                DocumentKitItem.id == item_id,
                DocumentKitItem.condominio_id == condominio_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_items_by_kit(
        self,
        kit_id: UUID,
        condominio_id: UUID,
        only_active: bool = True,
    ) -> list[DocumentKitItem]:
        """Lista itens de um kit."""
        conditions = [
            DocumentKitItem.kit_id == kit_id,
            DocumentKitItem.condominio_id == condominio_id,
        ]

        if only_active:
            conditions.append(DocumentKitItem.is_ativo.is_(True))

        query = select(DocumentKitItem).where(and_(*conditions)).order_by(DocumentKitItem.ordem)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_item(self, item: DocumentKitItem) -> DocumentKitItem:
        """Atualiza item."""
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete_item(self, item: DocumentKitItem) -> None:
        """Remove item."""
        await self.db.delete(item)
        await self.db.commit()

    async def reorder_items(
        self,
        kit_id: UUID,
        condominio_id: UUID,
        item_orders: list[dict],
    ) -> None:
        """Reordena itens do kit."""
        for order_data in item_orders:
            item_id = order_data.get("item_id")
            ordem = order_data.get("ordem")
            stmt = (
                update(DocumentKitItem)
                .where(
                    and_(
                        DocumentKitItem.id == item_id,
                        DocumentKitItem.kit_id == kit_id,
                        DocumentKitItem.condominio_id == condominio_id,
                    )
                )
                .values(ordem=ordem)
            )
            await self.db.execute(stmt)
        await self.db.commit()

    # === DocumentKitAssignment CRUD ===

    async def create_assignment(
        self,
        assignment: DocumentKitAssignment,
    ) -> DocumentKitAssignment:
        """Cria atribuicao de kit."""
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def get_assignment_by_id(
        self,
        assignment_id: UUID,
        condominio_id: UUID,
    ) -> DocumentKitAssignment | None:
        """Busca atribuicao por ID."""
        query = (
            select(DocumentKitAssignment)
            .where(
                and_(
                    DocumentKitAssignment.id == assignment_id,
                    DocumentKitAssignment.condominio_id == condominio_id,
                )
            )
            .options(
                joinedload(DocumentKitAssignment.kit),
                joinedload(DocumentKitAssignment.item_statuses),
            )
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_assignments(
        self,
        condominio_id: UUID,
        kit_id: UUID | None = None,
        entity_type: EntityType | None = None,
        entity_id: UUID | None = None,
        status: AssignmentStatus | None = None,
        vencidos: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DocumentKitAssignment]:
        """Lista atribuicoes com filtros."""
        conditions = [DocumentKitAssignment.condominio_id == condominio_id]

        if kit_id:
            conditions.append(DocumentKitAssignment.kit_id == kit_id)
        if entity_type:
            conditions.append(DocumentKitAssignment.entity_type == entity_type)
        if entity_id:
            conditions.append(DocumentKitAssignment.entity_id == entity_id)
        if status:
            conditions.append(DocumentKitAssignment.status == status)
        if vencidos is True:
            conditions.append(
                and_(
                    DocumentKitAssignment.data_limite < datetime.utcnow(),
                    DocumentKitAssignment.status.notin_(
                        [
                            AssignmentStatus.COMPLETO,
                            AssignmentStatus.CANCELADO,
                        ]
                    ),
                )
            )

        query = (
            select(DocumentKitAssignment)
            .where(and_(*conditions))
            .order_by(DocumentKitAssignment.data_limite.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_assignments(
        self,
        condominio_id: UUID,
        status: AssignmentStatus | None = None,
    ) -> int:
        """Conta atribuicoes."""
        conditions = [DocumentKitAssignment.condominio_id == condominio_id]

        if status:
            conditions.append(DocumentKitAssignment.status == status)

        query = select(func.count(DocumentKitAssignment.id)).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def count_vencidos(self, condominio_id: UUID) -> int:
        """Conta atribuicoes vencidas."""
        query = select(func.count(DocumentKitAssignment.id)).where(
            and_(
                DocumentKitAssignment.condominio_id == condominio_id,
                DocumentKitAssignment.data_limite < datetime.utcnow(),
                DocumentKitAssignment.status.notin_(
                    [
                        AssignmentStatus.COMPLETO,
                        AssignmentStatus.CANCELADO,
                    ]
                ),
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update_assignment(
        self,
        assignment: DocumentKitAssignment,
    ) -> DocumentKitAssignment:
        """Atualiza atribuicao."""
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def delete_assignment(self, assignment: DocumentKitAssignment) -> None:
        """Remove atribuicao."""
        await self.db.delete(assignment)
        await self.db.commit()

    # === DocumentKitItemStatus CRUD ===

    async def create_item_status(
        self,
        item_status: DocumentKitItemStatus,
    ) -> DocumentKitItemStatus:
        """Cria status de item."""
        self.db.add(item_status)
        await self.db.commit()
        await self.db.refresh(item_status)
        return item_status

    async def create_item_statuses_bulk(
        self,
        item_statuses: list[DocumentKitItemStatus],
    ) -> list[DocumentKitItemStatus]:
        """Cria multiplos status de item."""
        self.db.add_all(item_statuses)
        await self.db.commit()
        for status in item_statuses:
            await self.db.refresh(status)
        return item_statuses

    async def get_item_status_by_id(
        self,
        status_id: UUID,
        condominio_id: UUID,
    ) -> DocumentKitItemStatus | None:
        """Busca status por ID."""
        query = select(DocumentKitItemStatus).where(
            and_(
                DocumentKitItemStatus.id == status_id,
                DocumentKitItemStatus.condominio_id == condominio_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_item_statuses_by_assignment(
        self,
        assignment_id: UUID,
        condominio_id: UUID,
        status: ItemStatusEnum | None = None,
    ) -> list[DocumentKitItemStatus]:
        """Lista status de itens de uma atribuicao."""
        conditions = [
            DocumentKitItemStatus.assignment_id == assignment_id,
            DocumentKitItemStatus.condominio_id == condominio_id,
        ]

        if status:
            conditions.append(DocumentKitItemStatus.status == status)

        query = select(DocumentKitItemStatus).where(and_(*conditions))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_item_status(
        self,
        item_status: DocumentKitItemStatus,
    ) -> DocumentKitItemStatus:
        """Atualiza status de item."""
        await self.db.commit()
        await self.db.refresh(item_status)
        return item_status

    # === Estatisticas ===

    async def get_stats(self, condominio_id: UUID) -> dict:
        """Retorna estatisticas de kits."""
        total_kits = await self.count_kits(condominio_id)
        kits_ativos = await self.count_kits(condominio_id, status=KitStatus.ATIVO)
        kits_inativos = await self.count_kits(condominio_id, status=KitStatus.INATIVO)

        total_assignments = await self.count_assignments(condominio_id)
        assignments_pendentes = await self.count_assignments(condominio_id, status=AssignmentStatus.PENDENTE)
        assignments_completos = await self.count_assignments(condominio_id, status=AssignmentStatus.COMPLETO)
        assignments_vencidos = await self.count_vencidos(condominio_id)

        taxa_conclusao = 0.0
        if total_assignments > 0:
            taxa_conclusao = (assignments_completos / total_assignments) * 100

        # Por tipo
        por_tipo = {}
        for kit_type in KitType:
            count = await self.count_kits(condominio_id, tipo=kit_type)
            if count > 0:
                por_tipo[kit_type.value] = count

        # Por status
        por_status = {}
        for status in KitStatus:
            count = await self.count_kits(condominio_id, status=status)
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

    async def get_entity_compliance(
        self,
        condominio_id: UUID,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> dict:
        """Retorna conformidade de uma entidade."""
        assignments = await self.list_assignments(
            condominio_id=condominio_id,
            entity_type=entity_type,
            entity_id=entity_id,
        )

        total = len(assignments)
        completos = sum(1 for a in assignments if a.status == AssignmentStatus.COMPLETO)
        pendentes = sum(
            1
            for a in assignments
            if a.status
            in (
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
