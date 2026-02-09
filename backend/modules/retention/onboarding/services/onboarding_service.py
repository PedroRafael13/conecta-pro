"""
Service para lógica de negócio do módulo Onboarding.

Este módulo implementa toda a lógica de negócio relacionada ao
processo de onboarding de funcionários, incluindo criação de
checklists, gerenciamento de etapas e acompanhamento de progresso.

Classes:
    OnboardingService: Service principal com toda a lógica de negócio
    OnboardingError: Exceção customizada para erros de onboarding
"""

import logging
from datetime import date, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.retention.onboarding.models import (
    OnboardingChecklist,
    OnboardingProgress,
    OnboardingStep,
    ProgressStatus,
)
from modules.retention.onboarding.repositories import OnboardingRepository
from modules.retention.onboarding.schemas import (
    ChecklistCreate,
    ChecklistUpdate,
    FuncionarioOnboardingCreate,
    FuncionarioOnboardingResponse,
    OnboardingAlert,
    OnboardingDashboard,
    OnboardingFilter,
    OnboardingStats,
    ProgressComplete,
    ProgressCreate,
    ProgressDetailResponse,
    StepCreate,
    StepResponse,
    StepUpdate,
)

logger = logging.getLogger(__name__)


class OnboardingError(Exception):
    """
    Exceção customizada para erros de onboarding.

    Attributes:
        message: Mensagem de erro
        code: Código do erro
        details: Detalhes adicionais
    """

    def __init__(
        self,
        message: str,
        code: str = "ONBOARDING_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Inicializa a exceção.

        Args:
            message: Mensagem de erro
            code: Código do erro
            details: Detalhes adicionais
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class OnboardingService:
    """
    Service para operações de Onboarding.

    Implementa toda a lógica de negócio para gerenciamento do processo
    de integração de novos funcionários.

    Attributes:
        session: Sessão assíncrona do SQLAlchemy
        repository: Repository para operações de banco

    Example:
        >>> service = OnboardingService(session)
        >>> checklist = await service.create_checklist(data)
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Inicializa o service.

        Args:
            session: Sessão assíncrona do SQLAlchemy
        """
        self.session = session
        self.repository = OnboardingRepository(session)

    # =========================================================================
    # CHECKLIST OPERATIONS
    # =========================================================================

    async def create_checklist(
        self,
        data: ChecklistCreate,
    ) -> OnboardingChecklist:
        """
        Cria um novo checklist de onboarding.

        Args:
            data: Dados para criação do checklist

        Returns:
            Checklist criado

        Raises:
            OnboardingError: Se já existir checklist com mesmo nome
        """
        # Verifica duplicidade
        existing = await self.repository.get_checklist_by_nome(data.nome, data.condominium_id)
        if existing:
            raise OnboardingError(
                message=f"Já existe um checklist com o nome '{data.nome}'",
                code="CHECKLIST_DUPLICATE",
            )

        # Se marcado como padrão, remove padrão anterior
        if data.is_default:
            await self._remove_default_checklist(data.condominium_id)

        # Cria o checklist
        checklist = await self.repository.create_checklist(data)

        # Cria etapas se fornecidas
        if data.etapas:
            for idx, etapa_data in enumerate(data.etapas, start=1):
                etapa_data.checklist_id = checklist.id
                if etapa_data.ordem is None:
                    etapa_data.ordem = idx
                await self.repository.create_step(etapa_data)

        await self.session.commit()

        logger.info(
            f"Checklist criado: {checklist.id} - {checklist.nome}",
            extra={
                "checklist_id": str(checklist.id),
                "condominium_id": str(data.condominium_id),
            },
        )

        return checklist

    async def get_checklist(
        self,
        checklist_id: UUID,
        include_etapas: bool = True,
    ) -> OnboardingChecklist | None:
        """
        Busca checklist por ID.

        Args:
            checklist_id: ID do checklist
            include_etapas: Se deve incluir etapas

        Returns:
            Checklist encontrado ou None
        """
        return await self.repository.get_checklist_by_id(checklist_id, include_etapas)

    async def update_checklist(
        self,
        checklist_id: UUID,
        data: ChecklistUpdate,
    ) -> OnboardingChecklist | None:
        """
        Atualiza um checklist.

        Args:
            checklist_id: ID do checklist
            data: Dados para atualização

        Returns:
            Checklist atualizado ou None

        Raises:
            OnboardingError: Se houver conflito de nome
        """
        checklist = await self.repository.get_checklist_by_id(checklist_id)
        if not checklist:
            return None

        # Verifica duplicidade de nome
        if data.nome and data.nome != checklist.nome:
            existing = await self.repository.get_checklist_by_nome(data.nome, checklist.condominium_id)
            if existing:
                raise OnboardingError(
                    message=f"Já existe um checklist com o nome '{data.nome}'",
                    code="CHECKLIST_DUPLICATE",
                )

        # Se marcado como padrão, remove padrão anterior
        if data.is_default and not checklist.is_default:
            await self._remove_default_checklist(checklist.condominium_id)

        checklist = await self.repository.update_checklist(checklist_id, data)
        await self.session.commit()

        logger.info(
            f"Checklist atualizado: {checklist_id}",
            extra={"checklist_id": str(checklist_id)},
        )

        return checklist

    async def delete_checklist(self, checklist_id: UUID) -> bool:
        """
        Remove um checklist (soft delete).

        Args:
            checklist_id: ID do checklist

        Returns:
            True se removido com sucesso

        Raises:
            OnboardingError: Se houver progressos vinculados
        """
        # Verifica se há progressos ativos
        checklist = await self.repository.get_checklist_by_id(checklist_id, include_etapas=True)
        if not checklist:
            return False

        # Verifica progressos pendentes
        for etapa in checklist.etapas:
            if etapa.progressos:
                ativos = [
                    p for p in etapa.progressos if p.status not in [ProgressStatus.CONCLUIDO, ProgressStatus.CANCELADO]
                ]
                if ativos:
                    raise OnboardingError(
                        message="Não é possível excluir checklist com progressos ativos",
                        code="CHECKLIST_HAS_PROGRESS",
                        details={"progressos_ativos": len(ativos)},
                    )

        result = await self.repository.soft_delete_checklist(checklist_id)
        await self.session.commit()

        logger.info(
            f"Checklist removido: {checklist_id}",
            extra={"checklist_id": str(checklist_id)},
        )

        return result

    async def list_checklists(
        self,
        condominium_id: UUID,
        skip: int = 0,
        limit: int = 20,
        filters: OnboardingFilter | None = None,
    ) -> tuple[list[OnboardingChecklist], int]:
        """
        Lista checklists com filtros.

        Args:
            condominium_id: ID do condomínio
            skip: Offset para paginação
            limit: Limite de registros
            filters: Filtros opcionais

        Returns:
            Tuple com lista e total
        """
        is_active = None
        cargo_id = None
        departamento = None
        search = None

        if filters:
            departamento = filters.departamento
            search = filters.search

        return await self.repository.list_checklists(
            condominium_id=condominium_id,
            skip=skip,
            limit=limit,
            is_active=is_active,
            cargo_id=cargo_id,
            departamento=departamento,
            search=search,
        )

    async def duplicate_checklist(
        self,
        checklist_id: UUID,
        novo_nome: str,
    ) -> OnboardingChecklist:
        """
        Duplica um checklist existente.

        Args:
            checklist_id: ID do checklist original
            novo_nome: Nome do novo checklist

        Returns:
            Novo checklist criado

        Raises:
            OnboardingError: Se checklist não encontrado
        """
        original = await self.repository.get_checklist_by_id(checklist_id, include_etapas=True)
        if not original:
            raise OnboardingError(
                message="Checklist não encontrado",
                code="CHECKLIST_NOT_FOUND",
            )

        # Cria novo checklist
        data = ChecklistCreate(
            nome=novo_nome,
            descricao=original.descricao,
            condominium_id=original.condominium_id,
            cargo_id=original.cargo_id,
            departamento=original.departamento,
            dias_duracao_total=original.dias_duracao_total,
            is_default=False,
        )

        novo_checklist = await self.repository.create_checklist(data)

        # Duplica etapas
        for etapa in original.etapas:
            etapa_data = StepCreate(
                checklist_id=novo_checklist.id,
                nome=etapa.nome,
                descricao=etapa.descricao,
                dias_apos_admissao=etapa.dias_apos_admissao,
                tipo=etapa.tipo,
                obrigatorio=etapa.obrigatorio,
                ordem=etapa.ordem,
                responsavel_padrao_id=etapa.responsavel_padrao_id,
                recursos=etapa.recursos,
                instrucoes=etapa.instrucoes,
                link_material=etapa.link_material,
                tempo_estimado_minutos=etapa.tempo_estimado_minutos,
                permite_pular=etapa.permite_pular,
                notificar_supervisor=etapa.notificar_supervisor,
                notificar_rh=etapa.notificar_rh,
            )
            await self.repository.create_step(etapa_data)

        await self.session.commit()

        logger.info(
            f"Checklist duplicado: {checklist_id} -> {novo_checklist.id}",
            extra={
                "original_id": str(checklist_id),
                "novo_id": str(novo_checklist.id),
            },
        )

        return novo_checklist

    async def _remove_default_checklist(
        self,
        condominium_id: UUID,
    ) -> None:
        """Remove flag padrão de checklists existentes."""
        checklists, _ = await self.repository.list_checklists(
            condominium_id=condominium_id,
            limit=1000,
        )
        for checklist in checklists:
            if checklist.is_default:
                checklist.is_default = False
        await self.session.flush()

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

        Raises:
            OnboardingError: Se checklist não encontrado
        """
        checklist = await self.repository.get_checklist_by_id(data.checklist_id)
        if not checklist:
            raise OnboardingError(
                message="Checklist não encontrado",
                code="CHECKLIST_NOT_FOUND",
            )

        step = await self.repository.create_step(data)
        await self.session.commit()

        logger.info(
            f"Etapa criada: {step.id} - {step.nome}",
            extra={
                "step_id": str(step.id),
                "checklist_id": str(data.checklist_id),
            },
        )

        return step

    async def get_step(self, step_id: UUID) -> OnboardingStep | None:
        """
        Busca etapa por ID.

        Args:
            step_id: ID da etapa

        Returns:
            Etapa encontrada ou None
        """
        return await self.repository.get_step_by_id(step_id)

    async def update_step(
        self,
        step_id: UUID,
        data: StepUpdate,
    ) -> OnboardingStep | None:
        """
        Atualiza uma etapa.

        Args:
            step_id: ID da etapa
            data: Dados para atualização

        Returns:
            Etapa atualizada ou None
        """
        step = await self.repository.update_step(step_id, data)
        if step:
            await self.session.commit()

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

        Raises:
            OnboardingError: Se houver progressos vinculados
        """
        step = await self.repository.get_step_by_id(step_id)
        if not step:
            return False

        # Verifica progressos
        if step.progressos:
            ativos = [
                p for p in step.progressos if p.status not in [ProgressStatus.CONCLUIDO, ProgressStatus.CANCELADO]
            ]
            if ativos:
                raise OnboardingError(
                    message="Não é possível excluir etapa com progressos ativos",
                    code="STEP_HAS_PROGRESS",
                    details={"progressos_ativos": len(ativos)},
                )

        result = await self.repository.delete_step(step_id)
        await self.session.commit()

        logger.info(
            f"Etapa removida: {step_id}",
            extra={"step_id": str(step_id)},
        )

        return result

    async def reorder_steps(
        self,
        checklist_id: UUID,
        step_orders: list[dict[str, Any]],
    ) -> list[OnboardingStep]:
        """
        Reordena etapas de um checklist.

        Args:
            checklist_id: ID do checklist
            step_orders: Lista com {step_id, ordem}

        Returns:
            Lista de etapas reordenadas
        """
        steps = await self.repository.reorder_steps(checklist_id, step_orders)
        await self.session.commit()

        logger.info(
            f"Etapas reordenadas: checklist {checklist_id}",
            extra={"checklist_id": str(checklist_id)},
        )

        return steps

    # =========================================================================
    # ONBOARDING FUNCIONÁRIO
    # =========================================================================

    async def iniciar_onboarding(
        self,
        data: FuncionarioOnboardingCreate,
    ) -> FuncionarioOnboardingResponse:
        """
        Inicia o processo de onboarding de um funcionário.

        Cria registros de progresso para todas as etapas do checklist,
        calculando as datas previstas baseadas na data de admissão.

        Args:
            data: Dados para iniciar onboarding

        Returns:
            Resposta com resumo do onboarding criado

        Raises:
            OnboardingError: Se funcionário já possui onboarding ativo
        """
        # Verifica se já tem onboarding ativo
        existing = await self.repository.list_by_funcionario(data.funcionario_id)
        ativos = [p for p in existing if p.status not in [ProgressStatus.CONCLUIDO, ProgressStatus.CANCELADO]]
        if ativos:
            raise OnboardingError(
                message="Funcionário já possui onboarding em andamento",
                code="ONBOARDING_ALREADY_EXISTS",
                details={"progressos_ativos": len(ativos)},
            )

        # Obtém checklist
        checklist = None
        if data.checklist_id:
            checklist = await self.repository.get_checklist_by_id(data.checklist_id, include_etapas=True)
        else:
            # Busca checklist padrão
            # Precisaria do condominium_id do funcionário
            # Por enquanto, retorna erro
            raise OnboardingError(
                message="ID do checklist é obrigatório",
                code="CHECKLIST_REQUIRED",
            )

        if not checklist:
            raise OnboardingError(
                message="Checklist não encontrado",
                code="CHECKLIST_NOT_FOUND",
            )

        if not checklist.is_active:
            raise OnboardingError(
                message="Checklist não está ativo",
                code="CHECKLIST_INACTIVE",
            )

        if not checklist.etapas:
            raise OnboardingError(
                message="Checklist não possui etapas configuradas",
                code="CHECKLIST_EMPTY",
            )

        # Cria progressos para cada etapa
        progress_list = []
        for etapa in checklist.etapas:
            data_prevista = data.data_admissao + timedelta(days=etapa.dias_apos_admissao)

            progress_data = ProgressCreate(
                funcionario_id=data.funcionario_id,
                checklist_id=checklist.id,
                step_id=etapa.id,
                data_prevista=data_prevista,
                supervisor_id=data.supervisor_id,
                responsavel_id=etapa.responsavel_padrao_id,
            )
            progress_list.append(progress_data)

        progressos = await self.repository.create_progress_batch(progress_list)
        await self.session.commit()

        logger.info(
            f"Onboarding iniciado: funcionário {data.funcionario_id}",
            extra={
                "funcionario_id": str(data.funcionario_id),
                "checklist_id": str(checklist.id),
                "total_etapas": len(progressos),
            },
        )

        # Monta resposta
        return FuncionarioOnboardingResponse(
            funcionario_id=data.funcionario_id,
            checklist_id=checklist.id,
            checklist_nome=checklist.nome,
            data_admissao=data.data_admissao,
            supervisor_id=data.supervisor_id,
            total_etapas=len(progressos),
            etapas_concluidas=0,
            etapas_pendentes=len(progressos),
            etapas_atrasadas=0,
            progresso_percentual=0.0,
        )

    async def get_funcionario_onboarding(
        self,
        funcionario_id: UUID,
    ) -> FuncionarioOnboardingResponse | None:
        """
        Obtém o status do onboarding de um funcionário.

        Args:
            funcionario_id: ID do funcionário

        Returns:
            Resposta com status do onboarding ou None
        """
        summary = await self.repository.get_funcionario_onboarding_summary(funcionario_id)

        if not summary.get("tem_onboarding"):
            return None

        progressos = await self.repository.list_by_funcionario(funcionario_id)

        progress_responses = [
            ProgressDetailResponse(
                id=p.id,
                funcionario_id=p.funcionario_id,
                checklist_id=p.checklist_id,
                step_id=p.step_id,
                status=p.status,
                data_prevista=p.data_prevista,
                data_inicio=p.data_inicio,
                data_conclusao=p.data_conclusao,
                observacoes=p.observacoes,
                supervisor_id=p.supervisor_id,
                responsavel_id=p.responsavel_id,
                notificacoes_enviadas=p.notificacoes_enviadas,
                ultima_notificacao_at=p.ultima_notificacao_at,
                evidencia_url=p.evidencia_url,
                avaliacao_nota=p.avaliacao_nota,
                avaliacao_comentario=p.avaliacao_comentario,
                metadata_info=p.metadata_info,
                created_at=p.created_at,
                updated_at=p.updated_at,
                dias_restantes=p.dias_restantes,
                esta_atrasado=p.esta_atrasado,
                tempo_execucao_dias=p.tempo_execucao_dias,
                step=StepResponse.model_validate(p.step) if p.step else None,
            )
            for p in progressos
        ]

        return FuncionarioOnboardingResponse(
            funcionario_id=funcionario_id,
            checklist_id=summary.get("checklist_id"),
            checklist_nome=summary.get("checklist_nome"),
            data_admissao=date.today(),  # Seria ideal ter esta info
            supervisor_id=progressos[0].supervisor_id if progressos else None,
            total_etapas=summary.get("total_etapas", 0),
            etapas_concluidas=summary.get("etapas_concluidas", 0),
            etapas_pendentes=summary.get("etapas_pendentes", 0),
            etapas_atrasadas=summary.get("etapas_atrasadas", 0),
            progresso_percentual=summary.get("progresso_percentual", 0.0),
            progressos=progress_responses,
        )

    async def completar_etapa(
        self,
        progress_id: UUID,
        data: ProgressComplete,
    ) -> OnboardingProgress:
        """
        Marca uma etapa como concluída.

        Args:
            progress_id: ID do progresso
            data: Dados de conclusão

        Returns:
            Progresso atualizado

        Raises:
            OnboardingError: Se progresso não encontrado ou já concluído
        """
        progress = await self.repository.get_progress_by_id(progress_id, include_step=True)

        if not progress:
            raise OnboardingError(
                message="Progresso não encontrado",
                code="PROGRESS_NOT_FOUND",
            )

        if progress.status == ProgressStatus.CONCLUIDO:
            raise OnboardingError(
                message="Etapa já foi concluída",
                code="PROGRESS_ALREADY_COMPLETED",
            )

        if progress.status == ProgressStatus.CANCELADO:
            raise OnboardingError(
                message="Etapa foi cancelada",
                code="PROGRESS_CANCELLED",
            )

        # Verifica dependência
        if progress.step and progress.step.dependencia_step_id:
            dep_progress = await self.repository.get_progress_by_funcionario_step(
                progress.funcionario_id,
                progress.step.dependencia_step_id,
            )
            if dep_progress and dep_progress.status != ProgressStatus.CONCLUIDO:
                raise OnboardingError(
                    message="Etapa de dependência ainda não foi concluída",
                    code="DEPENDENCY_NOT_COMPLETED",
                    details={"dependencia_step_id": str(progress.step.dependencia_step_id)},
                )

        # Marca como concluída
        progress.concluir(data.observacoes)

        if data.evidencia_url:
            progress.evidencia_url = data.evidencia_url

        if data.avaliacao_nota is not None:
            progress.avaliar(data.avaliacao_nota, data.avaliacao_comentario)

        await self.session.commit()

        logger.info(
            f"Etapa concluída: {progress_id}",
            extra={
                "progress_id": str(progress_id),
                "funcionario_id": str(progress.funcionario_id),
            },
        )

        return progress

    async def iniciar_etapa(
        self,
        progress_id: UUID,
    ) -> OnboardingProgress:
        """
        Marca uma etapa como em andamento.

        Args:
            progress_id: ID do progresso

        Returns:
            Progresso atualizado

        Raises:
            OnboardingError: Se progresso não encontrado
        """
        progress = await self.repository.get_progress_by_id(progress_id)

        if not progress:
            raise OnboardingError(
                message="Progresso não encontrado",
                code="PROGRESS_NOT_FOUND",
            )

        if progress.status != ProgressStatus.PENDENTE:
            raise OnboardingError(
                message="Apenas etapas pendentes podem ser iniciadas",
                code="INVALID_STATUS_TRANSITION",
            )

        progress.iniciar()
        await self.session.commit()

        logger.info(
            f"Etapa iniciada: {progress_id}",
            extra={"progress_id": str(progress_id)},
        )

        return progress

    async def cancelar_etapa(
        self,
        progress_id: UUID,
        motivo: str,
    ) -> OnboardingProgress:
        """
        Cancela uma etapa.

        Args:
            progress_id: ID do progresso
            motivo: Motivo do cancelamento

        Returns:
            Progresso atualizado

        Raises:
            OnboardingError: Se progresso não encontrado ou já concluído
        """
        progress = await self.repository.get_progress_by_id(progress_id, include_step=True)

        if not progress:
            raise OnboardingError(
                message="Progresso não encontrado",
                code="PROGRESS_NOT_FOUND",
            )

        if progress.status == ProgressStatus.CONCLUIDO:
            raise OnboardingError(
                message="Etapa concluída não pode ser cancelada",
                code="CANNOT_CANCEL_COMPLETED",
            )

        # Verifica se etapa é obrigatória
        if progress.step and progress.step.obrigatorio:
            raise OnboardingError(
                message="Etapas obrigatórias não podem ser canceladas",
                code="CANNOT_CANCEL_MANDATORY",
            )

        progress.cancelar(motivo)
        await self.session.commit()

        logger.info(
            f"Etapa cancelada: {progress_id}",
            extra={
                "progress_id": str(progress_id),
                "motivo": motivo,
            },
        )

        return progress

    # =========================================================================
    # VERIFICAÇÃO DE ATRASOS
    # =========================================================================

    async def verificar_atrasos(
        self,
        condominium_id: UUID,
    ) -> dict[str, int]:
        """
        Verifica e marca etapas atrasadas.

        Este método deve ser executado periodicamente via job/scheduler.

        Args:
            condominium_id: ID do condomínio

        Returns:
            Dicionário com estatísticas de processamento
        """
        atrasados_marcados = await self.repository.marcar_atrasados(condominium_id)
        await self.session.commit()

        logger.info(
            f"Verificação de atrasos: {atrasados_marcados} marcados",
            extra={
                "condominium_id": str(condominium_id),
                "atrasados_marcados": atrasados_marcados,
            },
        )

        return {
            "atrasados_marcados": atrasados_marcados,
            "condominium_id": str(condominium_id),
            "verificado_em": datetime.utcnow().isoformat(),
        }

    # =========================================================================
    # DASHBOARD E MÉTRICAS
    # =========================================================================

    async def get_dashboard(
        self,
        condominium_id: UUID,
    ) -> OnboardingDashboard:
        """
        Obtém dados do dashboard de onboarding.

        Args:
            condominium_id: ID do condomínio

        Returns:
            Dashboard com estatísticas e alertas
        """
        stats_data = await self.repository.get_dashboard_stats(condominium_id)
        alerts_data = await self.repository.get_alerts(condominium_id)

        stats = OnboardingStats(
            total_funcionarios_em_onboarding=stats_data.get("total_funcionarios_em_onboarding", 0),
            total_funcionarios_concluidos=stats_data.get("total_funcionarios_concluidos", 0),
            total_etapas_pendentes=stats_data.get("total_etapas_pendentes", 0),
            total_etapas_em_andamento=stats_data.get("total_etapas_em_andamento", 0),
            total_etapas_concluidas=stats_data.get("total_etapas_concluidas", 0),
            total_etapas_atrasadas=stats_data.get("total_etapas_atrasadas", 0),
            tempo_medio_conclusao_dias=stats_data.get("tempo_medio_conclusao_dias", 0.0),
            taxa_conclusao_no_prazo=stats_data.get("taxa_conclusao_no_prazo", 0.0),
            nota_media_avaliacoes=stats_data.get("nota_media_avaliacoes", 0.0),
            por_status=stats_data.get("por_status", {}),
            por_tipo_etapa=stats_data.get("por_tipo_etapa", {}),
        )

        alerts = [
            OnboardingAlert(
                id=a["id"],
                tipo=a["tipo"],
                nivel=a["nivel"],
                funcionario_id=a["funcionario_id"],
                funcionario_nome=a.get("funcionario_nome"),
                step_id=a["step_id"],
                step_nome=a.get("step_nome"),
                checklist_nome=a.get("checklist_nome"),
                dias_atraso=a.get("dias_atraso", 0),
                supervisor_id=a.get("supervisor_id"),
                supervisor_nome=a.get("supervisor_nome"),
                mensagem=a["mensagem"],
                created_at=a["created_at"],
            )
            for a in alerts_data
        ]

        # Funcionários atrasados únicos
        func_atrasados = len({a["funcionario_id"] for a in alerts_data if a["tipo"] == "atrasado"})

        return OnboardingDashboard(
            stats=stats,
            alerts=alerts,
            funcionarios_ativos=stats.total_funcionarios_em_onboarding,
            funcionarios_atrasados=func_atrasados,
            checklists_ativos=stats_data.get("checklists_ativos", 0),
        )

    async def get_alertas(
        self,
        condominium_id: UUID,
        limit: int = 50,
    ) -> list[OnboardingAlert]:
        """
        Obtém alertas de onboarding.

        Args:
            condominium_id: ID do condomínio
            limit: Limite de alertas

        Returns:
            Lista de alertas
        """
        alerts_data = await self.repository.get_alerts(condominium_id, limit)

        return [
            OnboardingAlert(
                id=a["id"],
                tipo=a["tipo"],
                nivel=a["nivel"],
                funcionario_id=a["funcionario_id"],
                funcionario_nome=a.get("funcionario_nome"),
                step_id=a["step_id"],
                step_nome=a.get("step_nome"),
                checklist_nome=a.get("checklist_nome"),
                dias_atraso=a.get("dias_atraso", 0),
                supervisor_id=a.get("supervisor_id"),
                supervisor_nome=a.get("supervisor_nome"),
                mensagem=a["mensagem"],
                created_at=a["created_at"],
            )
            for a in alerts_data
        ]

    async def list_pendentes(
        self,
        condominium_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[OnboardingProgress], int]:
        """
        Lista progressos pendentes.

        Args:
            condominium_id: ID do condomínio
            skip: Offset
            limit: Limite

        Returns:
            Tuple com lista e total
        """
        return await self.repository.list_pendentes(condominium_id, skip, limit)

    async def list_atrasados(
        self,
        condominium_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[OnboardingProgress], int]:
        """
        Lista progressos atrasados.

        Args:
            condominium_id: ID do condomínio
            skip: Offset
            limit: Limite

        Returns:
            Tuple com lista e total
        """
        return await self.repository.list_atrasados(condominium_id, skip, limit)
