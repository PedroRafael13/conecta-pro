"""
Repository para operações de banco de dados do módulo Onboarding.

Este módulo implementa o padrão Repository para abstrair as operações
de persistência relacionadas ao onboarding de funcionários.

Classes:
    OnboardingRepository: Repository principal com todas as operações
"""

import logging
from datetime import date, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import and_, case, distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.retention.onboarding.models import (
    OnboardingChecklist,
    OnboardingProgress,
    OnboardingStep,
    ProgressStatus,
)
from modules.retention.onboarding.schemas import (
    ChecklistCreate,
    ChecklistUpdate,
    ProgressCreate,
    ProgressUpdate,
    StepCreate,
    StepUpdate,
)

logger = logging.getLogger(__name__)


class OnboardingRepository:
    """
    Repository para operações de Onboarding.

    Implementa todas as operações de CRUD e consultas especializadas
    para checklists, etapas e progresso de onboarding.

    Attributes:
        session: Sessão assíncrona do SQLAlchemy

    Example:
        >>> repo = OnboardingRepository(session)
        >>> checklist = await repo.create_checklist(data)
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Inicializa o repository.

        Args:
            session: Sessão assíncrona do SQLAlchemy
        """
        self.session = session

    # =========================================================================
    # CHECKLIST OPERATIONS
    # =========================================================================

    async def create_checklist(self, data: ChecklistCreate) -> OnboardingChecklist:
        """
        Cria um novo checklist de onboarding.

        Args:
            data: Dados para criação do checklist

        Returns:
            Checklist criado

        Raises:
            Exception: Em caso de erro de banco de dados
        """
        checklist = OnboardingChecklist(
            nome=data.nome,
            descricao=data.descricao,
            condominium_id=data.condominium_id,
            cargo_id=data.cargo_id,
            departamento=data.departamento,
            dias_duracao_total=data.dias_duracao_total,
            is_default=data.is_default,
        )
        self.session.add(checklist)
        await self.session.flush()

        logger.info(
            f"Checklist criado: {checklist.id} - {checklist.nome}",
            extra={"checklist_id": str(checklist.id)},
        )

        return checklist

    async def get_checklist_by_id(
        self,
        checklist_id: UUID,
        include_etapas: bool = False,
    ) -> OnboardingChecklist | None:
        """
        Busca checklist por ID.

        Args:
            checklist_id: ID do checklist
            include_etapas: Se deve incluir as etapas

        Returns:
            Checklist encontrado ou None
        """
        query = select(OnboardingChecklist).where(
            and_(
                OnboardingChecklist.id == checklist_id,
                OnboardingChecklist.deleted_at.is_(None),
            )
        )

        if include_etapas:
            query = query.options(selectinload(OnboardingChecklist.etapas))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_checklist_by_nome(
        self,
        nome: str,
        condominium_id: UUID,
    ) -> OnboardingChecklist | None:
        """
        Busca checklist por nome dentro de um condomínio.

        Args:
            nome: Nome do checklist
            condominium_id: ID do condomínio

        Returns:
            Checklist encontrado ou None
        """
        result = await self.session.execute(
            select(OnboardingChecklist).where(
                and_(
                    OnboardingChecklist.nome == nome,
                    OnboardingChecklist.condominium_id == condominium_id,
                    OnboardingChecklist.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_default_checklist(
        self,
        condominium_id: UUID,
        cargo_id: UUID | None = None,
    ) -> OnboardingChecklist | None:
        """
        Busca o checklist padrão para um condomínio/cargo.

        Args:
            condominium_id: ID do condomínio
            cargo_id: ID do cargo (opcional)

        Returns:
            Checklist padrão ou None
        """
        # Primeiro tenta por cargo
        if cargo_id:
            result = await self.session.execute(
                select(OnboardingChecklist).where(
                    and_(
                        OnboardingChecklist.condominium_id == condominium_id,
                        OnboardingChecklist.cargo_id == cargo_id,
                        OnboardingChecklist.is_active.is_(True),
                        OnboardingChecklist.deleted_at.is_(None),
                    )
                )
            )
            checklist = result.scalar_one_or_none()
            if checklist:
                return checklist

        # Fallback para checklist padrão geral
        result = await self.session.execute(
            select(OnboardingChecklist).where(
                and_(
                    OnboardingChecklist.condominium_id == condominium_id,
                    OnboardingChecklist.is_default.is_(True),
                    OnboardingChecklist.is_active.is_(True),
                    OnboardingChecklist.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_checklist(
        self,
        checklist_id: UUID,
        data: ChecklistUpdate,
    ) -> OnboardingChecklist | None:
        """
        Atualiza um checklist existente.

        Args:
            checklist_id: ID do checklist
            data: Dados para atualização

        Returns:
            Checklist atualizado ou None
        """
        checklist = await self.get_checklist_by_id(checklist_id)
        if not checklist:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(checklist, field, value)

        await self.session.flush()

        logger.info(
            f"Checklist atualizado: {checklist_id}",
            extra={"checklist_id": str(checklist_id)},
        )

        return checklist

    async def soft_delete_checklist(self, checklist_id: UUID) -> bool:
        """
        Realiza soft delete de um checklist.

        Args:
            checklist_id: ID do checklist

        Returns:
            True se excluído com sucesso
        """
        checklist = await self.get_checklist_by_id(checklist_id)
        if not checklist:
            return False

        checklist.soft_delete()
        await self.session.flush()

        logger.info(
            f"Checklist excluído (soft): {checklist_id}",
            extra={"checklist_id": str(checklist_id)},
        )

        return True

    async def list_checklists(
        self,
        condominium_id: UUID,
        skip: int = 0,
        limit: int = 20,
        is_active: bool | None = None,
        cargo_id: UUID | None = None,
        departamento: str | None = None,
        search: str | None = None,
    ) -> tuple[list[OnboardingChecklist], int]:
        """
        Lista checklists com filtros e paginação.

        Args:
            condominium_id: ID do condomínio
            skip: Offset para paginação
            limit: Limite de registros
            is_active: Filtro por status ativo
            cargo_id: Filtro por cargo
            departamento: Filtro por departamento
            search: Termo de busca

        Returns:
            Tuple com lista de checklists e total
        """
        query = select(OnboardingChecklist).where(
            and_(
                OnboardingChecklist.condominium_id == condominium_id,
                OnboardingChecklist.deleted_at.is_(None),
            )
        )

        if is_active is not None:
            query = query.where(OnboardingChecklist.is_active == is_active)
        if cargo_id:
            query = query.where(OnboardingChecklist.cargo_id == cargo_id)
        if departamento:
            query = query.where(OnboardingChecklist.departamento == departamento)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    OnboardingChecklist.nome.ilike(search_term),
                    OnboardingChecklist.descricao.ilike(search_term),
                )
            )

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Ordenação e paginação
        query = query.order_by(OnboardingChecklist.created_at.desc())
        query = query.offset(skip).limit(limit)
        query = query.options(selectinload(OnboardingChecklist.etapas))

        result = await self.session.execute(query)
        checklists = result.scalars().all()

        return list(checklists), total

    # =========================================================================
    # STEP OPERATIONS
    # =========================================================================

    async def create_step(self, data: StepCreate) -> OnboardingStep:
        """
        Cria uma nova etapa de onboarding.

        Args:
            data: Dados para criação da etapa

        Returns:
            Etapa criada
        """
        step = OnboardingStep(
            checklist_id=data.checklist_id,
            nome=data.nome,
            descricao=data.descricao,
            dias_apos_admissao=data.dias_apos_admissao,
            tipo=data.tipo,
            obrigatorio=data.obrigatorio,
            ordem=data.ordem,
            responsavel_padrao_id=data.responsavel_padrao_id,
            recursos=data.recursos,
            instrucoes=data.instrucoes,
            link_material=data.link_material,
            tempo_estimado_minutos=data.tempo_estimado_minutos,
            permite_pular=data.permite_pular,
            notificar_supervisor=data.notificar_supervisor,
            notificar_rh=data.notificar_rh,
            dependencia_step_id=data.dependencia_step_id,
        )
        self.session.add(step)
        await self.session.flush()

        logger.info(
            f"Etapa criada: {step.id} - {step.nome}",
            extra={
                "step_id": str(step.id),
                "checklist_id": str(data.checklist_id),
            },
        )

        return step

    async def get_step_by_id(self, step_id: UUID) -> OnboardingStep | None:
        """
        Busca etapa por ID.

        Args:
            step_id: ID da etapa

        Returns:
            Etapa encontrada ou None
        """
        result = await self.session.execute(select(OnboardingStep).where(OnboardingStep.id == step_id))
        return result.scalar_one_or_none()

    async def update_step(
        self,
        step_id: UUID,
        data: StepUpdate,
    ) -> OnboardingStep | None:
        """
        Atualiza uma etapa existente.

        Args:
            step_id: ID da etapa
            data: Dados para atualização

        Returns:
            Etapa atualizada ou None
        """
        step = await self.get_step_by_id(step_id)
        if not step:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(step, field, value)

        await self.session.flush()

        logger.info(
            f"Etapa atualizada: {step_id}",
            extra={"step_id": str(step_id)},
        )

        return step

    async def delete_step(self, step_id: UUID) -> bool:
        """
        Remove uma etapa.

        Args:
            step_id: ID da etapa

        Returns:
            True se removida com sucesso
        """
        step = await self.get_step_by_id(step_id)
        if not step:
            return False

        await self.session.delete(step)
        await self.session.flush()

        logger.info(
            f"Etapa removida: {step_id}",
            extra={"step_id": str(step_id)},
        )

        return True

    async def list_steps_by_checklist(
        self,
        checklist_id: UUID,
    ) -> list[OnboardingStep]:
        """
        Lista etapas de um checklist ordenadas.

        Args:
            checklist_id: ID do checklist

        Returns:
            Lista de etapas ordenadas
        """
        result = await self.session.execute(
            select(OnboardingStep).where(OnboardingStep.checklist_id == checklist_id).order_by(OnboardingStep.ordem)
        )
        return list(result.scalars().all())

    async def reorder_steps(
        self,
        checklist_id: UUID,
        step_orders: list[dict[str, Any]],
    ) -> list[OnboardingStep]:
        """
        Reordena as etapas de um checklist.

        Args:
            checklist_id: ID do checklist
            step_orders: Lista com {step_id, ordem}

        Returns:
            Lista de etapas reordenadas
        """
        for order_info in step_orders:
            step = await self.get_step_by_id(order_info["step_id"])
            if step and step.checklist_id == checklist_id:
                step.ordem = order_info["ordem"]

        await self.session.flush()
        return await self.list_steps_by_checklist(checklist_id)

    # =========================================================================
    # PROGRESS OPERATIONS
    # =========================================================================

    async def create_progress(self, data: ProgressCreate) -> OnboardingProgress:
        """
        Cria um registro de progresso.

        Args:
            data: Dados para criação do progresso

        Returns:
            Progresso criado
        """
        progress = OnboardingProgress(
            funcionario_id=data.funcionario_id,
            checklist_id=data.checklist_id,
            step_id=data.step_id,
            data_prevista=data.data_prevista,
            supervisor_id=data.supervisor_id,
            responsavel_id=data.responsavel_id,
            status=ProgressStatus.PENDENTE,
        )
        self.session.add(progress)
        await self.session.flush()

        logger.info(
            f"Progresso criado: {progress.id}",
            extra={
                "progress_id": str(progress.id),
                "funcionario_id": str(data.funcionario_id),
            },
        )

        return progress

    async def create_progress_batch(
        self,
        progress_list: list[ProgressCreate],
    ) -> list[OnboardingProgress]:
        """
        Cria múltiplos registros de progresso em lote.

        Args:
            progress_list: Lista de dados para criação

        Returns:
            Lista de progressos criados
        """
        progressos = []
        for data in progress_list:
            progress = OnboardingProgress(
                funcionario_id=data.funcionario_id,
                checklist_id=data.checklist_id,
                step_id=data.step_id,
                data_prevista=data.data_prevista,
                supervisor_id=data.supervisor_id,
                responsavel_id=data.responsavel_id,
                status=ProgressStatus.PENDENTE,
            )
            self.session.add(progress)
            progressos.append(progress)

        await self.session.flush()

        logger.info(
            f"Criados {len(progressos)} registros de progresso em lote",
        )

        return progressos

    async def get_progress_by_id(
        self,
        progress_id: UUID,
        include_step: bool = False,
    ) -> OnboardingProgress | None:
        """
        Busca progresso por ID.

        Args:
            progress_id: ID do progresso
            include_step: Se deve incluir a etapa

        Returns:
            Progresso encontrado ou None
        """
        query = select(OnboardingProgress).where(OnboardingProgress.id == progress_id)

        if include_step:
            query = query.options(selectinload(OnboardingProgress.step))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_progress_by_funcionario_step(
        self,
        funcionario_id: UUID,
        step_id: UUID,
    ) -> OnboardingProgress | None:
        """
        Busca progresso por funcionário e etapa.

        Args:
            funcionario_id: ID do funcionário
            step_id: ID da etapa

        Returns:
            Progresso encontrado ou None
        """
        result = await self.session.execute(
            select(OnboardingProgress).where(
                and_(
                    OnboardingProgress.funcionario_id == funcionario_id,
                    OnboardingProgress.step_id == step_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_progress(
        self,
        progress_id: UUID,
        data: ProgressUpdate,
    ) -> OnboardingProgress | None:
        """
        Atualiza um progresso existente.

        Args:
            progress_id: ID do progresso
            data: Dados para atualização

        Returns:
            Progresso atualizado ou None
        """
        progress = await self.get_progress_by_id(progress_id)
        if not progress:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(progress, field, value)

        await self.session.flush()

        logger.info(
            f"Progresso atualizado: {progress_id}",
            extra={"progress_id": str(progress_id)},
        )

        return progress

    async def list_by_funcionario(
        self,
        funcionario_id: UUID,
        checklist_id: UUID | None = None,
        status: ProgressStatus | None = None,
    ) -> list[OnboardingProgress]:
        """
        Lista progressos de um funcionário.

        Args:
            funcionario_id: ID do funcionário
            checklist_id: Filtro por checklist
            status: Filtro por status

        Returns:
            Lista de progressos
        """
        query = select(OnboardingProgress).where(OnboardingProgress.funcionario_id == funcionario_id)

        if checklist_id:
            query = query.where(OnboardingProgress.checklist_id == checklist_id)
        if status:
            query = query.where(OnboardingProgress.status == status)

        query = query.options(selectinload(OnboardingProgress.step))
        query = query.order_by(OnboardingProgress.data_prevista)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_pendentes(
        self,
        condominium_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[OnboardingProgress], int]:
        """
        Lista progressos pendentes de um condomínio.

        Args:
            condominium_id: ID do condomínio
            skip: Offset para paginação
            limit: Limite de registros

        Returns:
            Tuple com lista e total
        """
        query = (
            select(OnboardingProgress)
            .join(OnboardingChecklist)
            .where(
                and_(
                    OnboardingChecklist.condominium_id == condominium_id,
                    OnboardingProgress.status.in_(
                        [
                            ProgressStatus.PENDENTE,
                            ProgressStatus.EM_ANDAMENTO,
                        ]
                    ),
                )
            )
            .options(
                selectinload(OnboardingProgress.step),
                selectinload(OnboardingProgress.checklist),
            )
        )

        # Contagem
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        query = query.order_by(OnboardingProgress.data_prevista)
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def list_atrasados(
        self,
        condominium_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[OnboardingProgress], int]:
        """
        Lista progressos atrasados de um condomínio.

        Args:
            condominium_id: ID do condomínio
            skip: Offset para paginação
            limit: Limite de registros

        Returns:
            Tuple com lista e total
        """
        today = date.today()

        query = (
            select(OnboardingProgress)
            .join(OnboardingChecklist)
            .where(
                and_(
                    OnboardingChecklist.condominium_id == condominium_id,
                    OnboardingProgress.status.in_(
                        [
                            ProgressStatus.PENDENTE,
                            ProgressStatus.EM_ANDAMENTO,
                            ProgressStatus.ATRASADO,
                        ]
                    ),
                    OnboardingProgress.data_prevista < today,
                )
            )
            .options(
                selectinload(OnboardingProgress.step),
                selectinload(OnboardingProgress.checklist),
            )
        )

        # Contagem
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Ordenação por dias de atraso (mais atrasados primeiro)
        query = query.order_by(OnboardingProgress.data_prevista.asc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def marcar_atrasados(self, condominium_id: UUID) -> int:
        """
        Marca progressos atrasados de um condomínio.

        Args:
            condominium_id: ID do condomínio

        Returns:
            Quantidade de registros atualizados
        """
        today = date.today()

        query = (
            select(OnboardingProgress)
            .join(OnboardingChecklist)
            .where(
                and_(
                    OnboardingChecklist.condominium_id == condominium_id,
                    OnboardingProgress.status.in_(
                        [
                            ProgressStatus.PENDENTE,
                            ProgressStatus.EM_ANDAMENTO,
                        ]
                    ),
                    OnboardingProgress.data_prevista < today,
                )
            )
        )

        result = await self.session.execute(query)
        progressos = result.scalars().all()

        count = 0
        for progress in progressos:
            progress.marcar_atrasado()
            count += 1

        await self.session.flush()

        logger.info(
            f"Marcados {count} progressos como atrasados",
            extra={"condominium_id": str(condominium_id)},
        )

        return count

    # =========================================================================
    # DASHBOARD AND STATS
    # =========================================================================

    async def get_dashboard_stats(
        self,
        condominium_id: UUID,
    ) -> dict[str, Any]:
        """
        Obtém estatísticas para o dashboard.

        Args:
            condominium_id: ID do condomínio

        Returns:
            Dicionário com estatísticas
        """
        # Funcionários em onboarding ativo
        func_ativos_query = (
            select(func.count(distinct(OnboardingProgress.funcionario_id)))
            .join(OnboardingChecklist)
            .where(
                and_(
                    OnboardingChecklist.condominium_id == condominium_id,
                    OnboardingProgress.status.in_(
                        [
                            ProgressStatus.PENDENTE,
                            ProgressStatus.EM_ANDAMENTO,
                            ProgressStatus.ATRASADO,
                        ]
                    ),
                )
            )
        )
        func_ativos_result = await self.session.execute(func_ativos_query)
        func_ativos = func_ativos_result.scalar() or 0

        # Funcionários que concluíram
        func_concluidos_subq = (
            select(OnboardingProgress.funcionario_id)
            .join(OnboardingChecklist)
            .where(
                and_(
                    OnboardingChecklist.condominium_id == condominium_id,
                    OnboardingProgress.status == ProgressStatus.CONCLUIDO,
                )
            )
            .group_by(OnboardingProgress.funcionario_id)
            .having(
                func.count(OnboardingProgress.id)
                == func.count(
                    case(
                        (
                            OnboardingProgress.status == ProgressStatus.CONCLUIDO,
                            1,
                        ),
                    )
                )
            )
        )
        func_concluidos_result = await self.session.execute(
            select(func.count()).select_from(func_concluidos_subq.subquery())
        )
        func_concluidos = func_concluidos_result.scalar() or 0

        # Contagem por status
        status_query = (
            select(
                OnboardingProgress.status,
                func.count(OnboardingProgress.id).label("count"),
            )
            .join(OnboardingChecklist)
            .where(OnboardingChecklist.condominium_id == condominium_id)
            .group_by(OnboardingProgress.status)
        )
        status_result = await self.session.execute(status_query)
        por_status = {row.status.value: row.count for row in status_result}

        # Contagem por tipo de etapa
        tipo_query = (
            select(
                OnboardingStep.tipo,
                func.count(OnboardingProgress.id).label("count"),
            )
            .join(OnboardingProgress)
            .join(OnboardingChecklist)
            .where(OnboardingChecklist.condominium_id == condominium_id)
            .group_by(OnboardingStep.tipo)
        )
        tipo_result = await self.session.execute(tipo_query)
        por_tipo = {row.tipo.value: row.count for row in tipo_result}

        # Tempo médio de conclusão
        tempo_query = (
            select(
                func.avg(
                    func.extract("day", OnboardingProgress.data_conclusao)
                    - func.extract("day", OnboardingProgress.created_at)
                )
            )
            .join(OnboardingChecklist)
            .where(
                and_(
                    OnboardingChecklist.condominium_id == condominium_id,
                    OnboardingProgress.status == ProgressStatus.CONCLUIDO,
                    OnboardingProgress.data_conclusao.isnot(None),
                )
            )
        )
        tempo_result = await self.session.execute(tempo_query)
        tempo_medio = tempo_result.scalar() or 0

        # Taxa de conclusão no prazo
        total_concluidos = por_status.get(ProgressStatus.CONCLUIDO.value, 0)
        if total_concluidos > 0:
            no_prazo_query = (
                select(func.count(OnboardingProgress.id))
                .join(OnboardingChecklist)
                .where(
                    and_(
                        OnboardingChecklist.condominium_id == condominium_id,
                        OnboardingProgress.status == ProgressStatus.CONCLUIDO,
                        OnboardingProgress.data_conclusao <= OnboardingProgress.data_prevista,
                    )
                )
            )
            no_prazo_result = await self.session.execute(no_prazo_query)
            no_prazo = no_prazo_result.scalar() or 0
            taxa_no_prazo = (no_prazo / total_concluidos) * 100
        else:
            taxa_no_prazo = 0.0

        # Nota média das avaliações
        nota_query = (
            select(func.avg(OnboardingProgress.avaliacao_nota))
            .join(OnboardingChecklist)
            .where(
                and_(
                    OnboardingChecklist.condominium_id == condominium_id,
                    OnboardingProgress.avaliacao_nota.isnot(None),
                )
            )
        )
        nota_result = await self.session.execute(nota_query)
        nota_media = nota_result.scalar() or 0

        # Checklists ativos
        checklists_query = select(func.count(OnboardingChecklist.id)).where(
            and_(
                OnboardingChecklist.condominium_id == condominium_id,
                OnboardingChecklist.is_active.is_(True),
                OnboardingChecklist.deleted_at.is_(None),
            )
        )
        checklists_result = await self.session.execute(checklists_query)
        checklists_ativos = checklists_result.scalar() or 0

        return {
            "total_funcionarios_em_onboarding": func_ativos,
            "total_funcionarios_concluidos": func_concluidos,
            "total_etapas_pendentes": por_status.get(ProgressStatus.PENDENTE.value, 0),
            "total_etapas_em_andamento": por_status.get(ProgressStatus.EM_ANDAMENTO.value, 0),
            "total_etapas_concluidas": por_status.get(ProgressStatus.CONCLUIDO.value, 0),
            "total_etapas_atrasadas": por_status.get(ProgressStatus.ATRASADO.value, 0),
            "tempo_medio_conclusao_dias": float(tempo_medio),
            "taxa_conclusao_no_prazo": float(taxa_no_prazo),
            "nota_media_avaliacoes": float(nota_media),
            "por_status": por_status,
            "por_tipo_etapa": por_tipo,
            "checklists_ativos": checklists_ativos,
        }

    async def get_alerts(
        self,
        condominium_id: UUID,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Obtém alertas de onboarding.

        Args:
            condominium_id: ID do condomínio
            limit: Limite de alertas

        Returns:
            Lista de alertas formatados
        """
        today = date.today()
        alerts = []

        # Atrasados
        atrasados_query = (
            select(OnboardingProgress)
            .join(OnboardingChecklist)
            .join(OnboardingStep)
            .where(
                and_(
                    OnboardingChecklist.condominium_id == condominium_id,
                    OnboardingProgress.status.in_(
                        [
                            ProgressStatus.PENDENTE,
                            ProgressStatus.EM_ANDAMENTO,
                            ProgressStatus.ATRASADO,
                        ]
                    ),
                    OnboardingProgress.data_prevista < today,
                )
            )
            .options(
                selectinload(OnboardingProgress.step),
                selectinload(OnboardingProgress.checklist),
            )
            .order_by(OnboardingProgress.data_prevista.asc())
            .limit(limit)
        )

        atrasados_result = await self.session.execute(atrasados_query)
        atrasados = atrasados_result.scalars().all()

        for progress in atrasados:
            dias_atraso = (today - progress.data_prevista).days
            nivel = "critico" if dias_atraso > 7 else "alto" if dias_atraso > 3 else "medio"

            alerts.append(
                {
                    "id": progress.id,
                    "tipo": "atrasado",
                    "nivel": nivel,
                    "funcionario_id": progress.funcionario_id,
                    "step_id": progress.step_id,
                    "step_nome": progress.step.nome if progress.step else None,
                    "checklist_nome": progress.checklist.nome if progress.checklist else None,
                    "dias_atraso": dias_atraso,
                    "supervisor_id": progress.supervisor_id,
                    "mensagem": f"Etapa '{progress.step.nome}' atrasada há {dias_atraso} dia(s)",
                    "created_at": datetime.utcnow(),
                }
            )

        # Próximos a vencer (próximos 3 dias)
        proximo_vencer_query = (
            select(OnboardingProgress)
            .join(OnboardingChecklist)
            .join(OnboardingStep)
            .where(
                and_(
                    OnboardingChecklist.condominium_id == condominium_id,
                    OnboardingProgress.status == ProgressStatus.PENDENTE,
                    OnboardingProgress.data_prevista >= today,
                    OnboardingProgress.data_prevista <= today + timedelta(days=3),
                )
            )
            .options(
                selectinload(OnboardingProgress.step),
                selectinload(OnboardingProgress.checklist),
            )
            .order_by(OnboardingProgress.data_prevista.asc())
            .limit(limit - len(alerts))
        )

        proximos_result = await self.session.execute(proximo_vencer_query)
        proximos = proximos_result.scalars().all()

        for progress in proximos:
            dias_restantes = (progress.data_prevista - today).days

            alerts.append(
                {
                    "id": progress.id,
                    "tipo": "proximo_vencer",
                    "nivel": "baixo",
                    "funcionario_id": progress.funcionario_id,
                    "step_id": progress.step_id,
                    "step_nome": progress.step.nome if progress.step else None,
                    "checklist_nome": progress.checklist.nome if progress.checklist else None,
                    "dias_atraso": -dias_restantes,
                    "supervisor_id": progress.supervisor_id,
                    "mensagem": f"Etapa '{progress.step.nome}' vence em {dias_restantes} dia(s)",
                    "created_at": datetime.utcnow(),
                }
            )

        return alerts

    async def get_funcionario_onboarding_summary(
        self,
        funcionario_id: UUID,
    ) -> dict[str, Any]:
        """
        Obtém resumo do onboarding de um funcionário.

        Args:
            funcionario_id: ID do funcionário

        Returns:
            Dicionário com resumo do onboarding
        """
        progressos = await self.list_by_funcionario(funcionario_id)

        if not progressos:
            return {
                "funcionario_id": funcionario_id,
                "tem_onboarding": False,
            }

        checklist = progressos[0].checklist if progressos else None
        total = len(progressos)
        concluidos = sum(1 for p in progressos if p.status == ProgressStatus.CONCLUIDO)
        atrasados = sum(1 for p in progressos if p.esta_atrasado)
        pendentes = total - concluidos

        # Próxima etapa
        proxima = next(
            (
                p
                for p in progressos
                if p.status
                in [
                    ProgressStatus.PENDENTE,
                    ProgressStatus.EM_ANDAMENTO,
                ]
            ),
            None,
        )

        return {
            "funcionario_id": funcionario_id,
            "tem_onboarding": True,
            "checklist_id": checklist.id if checklist else None,
            "checklist_nome": checklist.nome if checklist else None,
            "total_etapas": total,
            "etapas_concluidas": concluidos,
            "etapas_pendentes": pendentes,
            "etapas_atrasadas": atrasados,
            "progresso_percentual": (concluidos / total * 100) if total > 0 else 0,
            "proxima_etapa": {
                "id": proxima.id,
                "step_id": proxima.step_id,
                "nome": proxima.step.nome if proxima.step else None,
                "data_prevista": proxima.data_prevista,
                "status": proxima.status.value,
            }
            if proxima
            else None,
        }
