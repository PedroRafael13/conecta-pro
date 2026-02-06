"""Service de Kits Documentais - Versão Async."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

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
from modules.document_kits.repositories.kit_repository import DocumentKitRepository
from modules.document_kits.schemas.kit_schemas import (
    DocumentKitCreate,
    DocumentKitUpdate,
    DocumentKitItemCreate,
    DocumentKitItemUpdate,
    DocumentKitAssignmentCreate,
    DocumentKitAssignmentUpdate,
)


class DocumentKitService:
    """Service para operacoes de Kits Documentais."""

    def __init__(self, db: AsyncSession):
        """Inicializa service."""
        self.db = db
        self.repository = DocumentKitRepository(db)

    # === DocumentKit Operations ===

    async def create_kit(
        self,
        data: DocumentKitCreate,
        created_by: UUID,
    ) -> DocumentKit:
        """Cria um novo kit."""
        kit = DocumentKit(
            id=uuid4(),
            condominio_id=data.condominio_id,
            codigo=data.codigo,
            nome=data.nome,
            descricao=data.descricao,
            tipo=data.tipo,
            is_template=data.is_template,
            is_obrigatorio=data.is_obrigatorio,
            prazo_dias=data.prazo_dias,
            permite_parcial=data.permite_parcial,
            requer_aprovacao=data.requer_aprovacao,
            entity_types=data.entity_types,
            departamentos=data.departamentos,
            cargos=data.cargos,
            tags=data.tags,
            status=KitStatus.RASCUNHO,
            created_by=created_by,
        )
        return await self.repository.create_kit(kit)

    async def get_kit(
        self,
        kit_id: UUID,
        condominio_id: UUID,
    ) -> Optional[DocumentKit]:
        """Busca kit por ID."""
        return await self.repository.get_kit_by_id(kit_id, condominio_id)

    async def list_kits(
        self,
        condominio_id: UUID,
        tipo: Optional[KitType] = None,
        status: Optional[KitStatus] = None,
        is_template: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DocumentKit]:
        """Lista kits."""
        return await self.repository.list_kits(
            condominio_id=condominio_id,
            tipo=tipo,
            status=status,
            is_template=is_template,
            search=search,
            skip=skip,
            limit=limit,
        )

    async def count_kits(
        self,
        condominio_id: UUID,
        tipo: Optional[KitType] = None,
        status: Optional[KitStatus] = None,
    ) -> int:
        """Conta kits."""
        return await self.repository.count_kits(
            condominio_id=condominio_id,
            tipo=tipo,
            status=status,
        )

    async def update_kit(
        self,
        kit: DocumentKit,
        data: DocumentKitUpdate,
        updated_by: UUID,
    ) -> DocumentKit:
        """Atualiza kit."""
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(kit, field, value)

        kit.updated_by = updated_by
        return await self.repository.update_kit(kit)

    async def activate_kit(self, kit: DocumentKit) -> DocumentKit:
        """Ativa kit."""
        kit.ativar()
        return await self.repository.update_kit(kit)

    async def deactivate_kit(self, kit: DocumentKit) -> DocumentKit:
        """Desativa kit."""
        kit.desativar()
        return await self.repository.update_kit(kit)

    async def archive_kit(self, kit: DocumentKit) -> DocumentKit:
        """Arquiva kit."""
        kit.arquivar()
        return await self.repository.update_kit(kit)

    async def duplicate_kit(
        self,
        kit: DocumentKit,
        new_codigo: str,
        new_nome: str,
        created_by: UUID,
    ) -> DocumentKit:
        """Duplica kit com itens."""
        new_kit = DocumentKit(
            id=uuid4(),
            condominio_id=kit.condominio_id,
            codigo=new_codigo,
            nome=new_nome,
            descricao=kit.descricao,
            tipo=kit.tipo,
            is_template=kit.is_template,
            is_obrigatorio=kit.is_obrigatorio,
            prazo_dias=kit.prazo_dias,
            permite_parcial=kit.permite_parcial,
            requer_aprovacao=kit.requer_aprovacao,
            entity_types=kit.entity_types,
            departamentos=kit.departamentos,
            cargos=kit.cargos,
            tags=kit.tags,
            status=KitStatus.RASCUNHO,
            created_by=created_by,
        )
        new_kit = await self.repository.create_kit(new_kit)

        for item in kit.itens:
            new_item = DocumentKitItem(
                id=uuid4(),
                kit_id=new_kit.id,
                condominio_id=kit.condominio_id,
                codigo=item.codigo,
                nome=item.nome,
                descricao=item.descricao,
                instrucoes=item.instrucoes,
                tipo=item.tipo,
                prioridade=item.prioridade,
                ordem=item.ordem,
                formatos_aceitos=item.formatos_aceitos,
                tamanho_max_mb=item.tamanho_max_mb,
                requer_validade=item.requer_validade,
                validade_minima_dias=item.validade_minima_dias,
                requer_autenticacao=item.requer_autenticacao,
                template_url=item.template_url,
                exemplo_url=item.exemplo_url,
                tags=item.tags,
            )
            await self.repository.create_item(new_item)

        new_kit.atualizar_contadores()
        return await self.repository.update_kit(new_kit)

    async def delete_kit(self, kit: DocumentKit) -> None:
        """Remove kit."""
        await self.repository.delete_kit(kit)

    # === DocumentKitItem Operations ===

    async def add_item(
        self,
        kit: DocumentKit,
        data: DocumentKitItemCreate,
    ) -> DocumentKitItem:
        """Adiciona item ao kit."""
        item = DocumentKitItem(
            id=uuid4(),
            kit_id=kit.id,
            condominio_id=data.condominio_id,
            codigo=data.codigo,
            nome=data.nome,
            descricao=data.descricao,
            instrucoes=data.instrucoes,
            tipo=data.tipo,
            prioridade=data.prioridade,
            ordem=data.ordem,
            formatos_aceitos=data.formatos_aceitos,
            tamanho_max_mb=data.tamanho_max_mb,
            requer_validade=data.requer_validade,
            validade_minima_dias=data.validade_minima_dias,
            requer_autenticacao=data.requer_autenticacao,
            template_url=data.template_url,
            exemplo_url=data.exemplo_url,
            depende_de=data.depende_de,
            tags=data.tags,
        )
        item = await self.repository.create_item(item)

        kit.atualizar_contadores()
        await self.repository.update_kit(kit)

        return item

    async def get_item(
        self,
        item_id: UUID,
        condominio_id: UUID,
    ) -> Optional[DocumentKitItem]:
        """Busca item por ID."""
        return await self.repository.get_item_by_id(item_id, condominio_id)

    async def list_kit_items(
        self,
        kit_id: UUID,
        condominio_id: UUID,
        only_active: bool = True,
    ) -> List[DocumentKitItem]:
        """Lista itens de um kit."""
        return await self.repository.list_items_by_kit(
            kit_id=kit_id,
            condominio_id=condominio_id,
            only_active=only_active,
        )

    async def update_item(
        self,
        item: DocumentKitItem,
        data: DocumentKitItemUpdate,
    ) -> DocumentKitItem:
        """Atualiza item."""
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(item, field, value)

        return await self.repository.update_item(item)

    async def delete_item(self, item: DocumentKitItem) -> None:
        """Remove item."""
        kit = await self.repository.get_kit_by_id(
            item.kit_id, item.condominio_id
        )
        await self.repository.delete_item(item)

        if kit:
            kit.atualizar_contadores()
            await self.repository.update_kit(kit)

    async def reorder_items(
        self,
        kit_id: UUID,
        condominio_id: UUID,
        item_orders: List[dict],
    ) -> None:
        """Reordena itens."""
        await self.repository.reorder_items(kit_id, condominio_id, item_orders)

    # === DocumentKitAssignment Operations ===

    async def assign_kit(
        self,
        data: DocumentKitAssignmentCreate,
        created_by: UUID,
    ) -> DocumentKitAssignment:
        """Atribui kit a uma entidade."""
        kit = await self.repository.get_kit_by_id(data.kit_id, data.condominio_id)
        if not kit:
            raise ValueError("Kit nao encontrado")

        data_limite = None
        if kit.prazo_dias:
            data_limite = datetime.utcnow() + timedelta(days=kit.prazo_dias)
        if data.data_limite:
            data_limite = data.data_limite

        assignment = DocumentKitAssignment(
            id=uuid4(),
            kit_id=data.kit_id,
            condominio_id=data.condominio_id,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            entity_nome=data.entity_nome,
            data_limite=data_limite,
            responsavel_id=data.responsavel_id,
            observacoes=data.observacoes,
            status=AssignmentStatus.PENDENTE,
            created_by=created_by,
        )
        assignment = await self.repository.create_assignment(assignment)

        items = await self.repository.list_items_by_kit(
            kit_id=kit.id,
            condominio_id=data.condominio_id,
            only_active=True,
        )

        item_statuses = []
        for item in items:
            status = DocumentKitItemStatus(
                id=uuid4(),
                assignment_id=assignment.id,
                item_id=item.id,
                condominio_id=data.condominio_id,
                status=ItemStatusEnum.PENDENTE,
            )
            item_statuses.append(status)

        if item_statuses:
            await self.repository.create_item_statuses_bulk(item_statuses)

        assignment.total_itens = len(items)
        assignment.itens_pendentes = len(items)
        await self.repository.update_assignment(assignment)

        kit.incrementar_uso()
        await self.repository.update_kit(kit)

        return assignment

    async def get_assignment(
        self,
        assignment_id: UUID,
        condominio_id: UUID,
    ) -> Optional[DocumentKitAssignment]:
        """Busca atribuicao por ID."""
        return await self.repository.get_assignment_by_id(assignment_id, condominio_id)

    async def list_assignments(
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
        """Lista atribuicoes."""
        return await self.repository.list_assignments(
            condominio_id=condominio_id,
            kit_id=kit_id,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            vencidos=vencidos,
            skip=skip,
            limit=limit,
        )

    async def count_assignments(
        self,
        condominio_id: UUID,
        status: Optional[AssignmentStatus] = None,
    ) -> int:
        """Conta atribuicoes."""
        return await self.repository.count_assignments(
            condominio_id=condominio_id,
            status=status,
        )

    async def update_assignment(
        self,
        assignment: DocumentKitAssignment,
        data: DocumentKitAssignmentUpdate,
    ) -> DocumentKitAssignment:
        """Atualiza atribuicao."""
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(assignment, field, value)

        return await self.repository.update_assignment(assignment)

    async def start_assignment(
        self,
        assignment: DocumentKitAssignment,
    ) -> DocumentKitAssignment:
        """Inicia atribuicao."""
        assignment.iniciar()
        return await self.repository.update_assignment(assignment)

    async def approve_assignment(
        self,
        assignment: DocumentKitAssignment,
        approved_by: UUID,
    ) -> DocumentKitAssignment:
        """Aprova atribuicao."""
        assignment.aprovar(str(approved_by))
        return await self.repository.update_assignment(assignment)

    async def reject_assignment(
        self,
        assignment: DocumentKitAssignment,
        motivo: str,
    ) -> DocumentKitAssignment:
        """Reprova atribuicao."""
        assignment.reprovar(motivo)
        return await self.repository.update_assignment(assignment)

    async def complete_assignment(
        self,
        assignment: DocumentKitAssignment,
    ) -> DocumentKitAssignment:
        """Completa atribuicao."""
        assignment.completar()
        return await self.repository.update_assignment(assignment)

    async def cancel_assignment(
        self,
        assignment: DocumentKitAssignment,
    ) -> DocumentKitAssignment:
        """Cancela atribuicao."""
        assignment.cancelar()
        return await self.repository.update_assignment(assignment)

    async def send_notification(
        self,
        assignment: DocumentKitAssignment,
    ) -> DocumentKitAssignment:
        """Registra notificacao enviada."""
        assignment.registrar_notificacao()
        return await self.repository.update_assignment(assignment)

    async def recalculate_progress(
        self,
        assignment: DocumentKitAssignment,
    ) -> DocumentKitAssignment:
        """Recalcula progresso da atribuicao."""
        statuses = await self.repository.list_item_statuses_by_assignment(
            assignment_id=assignment.id,
            condominio_id=assignment.condominio_id,
        )

        assignment.total_itens = len(statuses)
        assignment.itens_pendentes = sum(
            1 for s in statuses if s.status == ItemStatusEnum.PENDENTE
        )
        assignment.itens_aprovados = sum(
            1 for s in statuses if s.status == ItemStatusEnum.APROVADO
        )
        assignment.itens_reprovados = sum(
            1 for s in statuses if s.status == ItemStatusEnum.REPROVADO
        )
        assignment.calcular_progresso()

        if assignment.itens_aprovados == assignment.total_itens:
            assignment.status = AssignmentStatus.COMPLETO
            assignment.data_conclusao = datetime.utcnow()

        return await self.repository.update_assignment(assignment)

    # === DocumentKitItemStatus Operations ===

    async def get_item_status(
        self,
        status_id: UUID,
        condominio_id: UUID,
    ) -> Optional[DocumentKitItemStatus]:
        """Busca status de item."""
        return await self.repository.get_item_status_by_id(status_id, condominio_id)

    async def list_assignment_statuses(
        self,
        assignment_id: UUID,
        condominio_id: UUID,
        status: Optional[ItemStatusEnum] = None,
    ) -> List[DocumentKitItemStatus]:
        """Lista status de itens de uma atribuicao."""
        return await self.repository.list_item_statuses_by_assignment(
            assignment_id=assignment_id,
            condominio_id=condominio_id,
            status=status,
        )

    async def submit_document(
        self,
        item_status: DocumentKitItemStatus,
        arquivo_url: str,
        arquivo_nome: str,
        arquivo_tamanho: int,
        arquivo_tipo: str,
        enviado_por: UUID,
        data_validade: Optional[datetime] = None,
    ) -> DocumentKitItemStatus:
        """Submete documento para um item."""
        item_status.enviar(arquivo_url, arquivo_nome, str(enviado_por))
        item_status.arquivo_tamanho = arquivo_tamanho
        item_status.arquivo_tipo = arquivo_tipo

        if data_validade:
            item_status.data_validade = data_validade

        return await self.repository.update_item_status(item_status)

    async def approve_document(
        self,
        item_status: DocumentKitItemStatus,
        approved_by: UUID,
        observacoes: Optional[str] = None,
    ) -> DocumentKitItemStatus:
        """Aprova documento."""
        item_status.aprovar(str(approved_by), observacoes)
        return await self.repository.update_item_status(item_status)

    async def reject_document(
        self,
        item_status: DocumentKitItemStatus,
        motivo: str,
    ) -> DocumentKitItemStatus:
        """Reprova documento."""
        item_status.reprovar(motivo)
        return await self.repository.update_item_status(item_status)

    async def mark_not_applicable(
        self,
        item_status: DocumentKitItemStatus,
        motivo: str,
    ) -> DocumentKitItemStatus:
        """Marca item como nao aplicavel."""
        item_status.marcar_nao_aplicavel(motivo)
        return await self.repository.update_item_status(item_status)

    # === Stats Operations ===

    async def get_stats(self, condominio_id: UUID) -> dict:
        """Retorna estatisticas."""
        return await self.repository.get_stats(condominio_id)

    async def get_entity_compliance(
        self,
        condominio_id: UUID,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> dict:
        """Retorna conformidade de entidade."""
        return await self.repository.get_entity_compliance(
            condominio_id=condominio_id,
            entity_type=entity_type,
            entity_id=entity_id,
        )
