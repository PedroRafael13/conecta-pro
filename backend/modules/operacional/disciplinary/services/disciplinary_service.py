"""
DisciplinaryService - Servico principal de Medidas Administrativas.

Implementa toda a logica de negocio para:
- CRUD de medidas disciplinares
- Workflow de aprovacao
- Validacao de regras CLT
- Integracao com outros modulos

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

import builtins
from datetime import date, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.operacional.disciplinary.models import (
    DisciplinaryAction,
    DisciplinaryActionStatus,
    DisciplinaryActionType,
)
from modules.operacional.disciplinary.repositories import (
    DisciplinaryRepository,
    SignatureRepository,
    TemplateRepository,
)
from modules.operacional.disciplinary.schemas import (
    ApproveRequest,
    DisciplinaryActionCreate,
    DisciplinaryActionListResponse,
    DisciplinaryActionResponse,
    DisciplinaryActionUpdate,
    DisciplinaryFilter,
    DisciplinaryStats,
    GenerateDocumentRequest,
    GenerateDocumentResponse,
    RejectRequest,
)


class DisciplinaryServiceError(Exception):
    """Excecao base para erros do servico disciplinar."""

    pass


class DisciplinaryValidationError(DisciplinaryServiceError):
    """Erro de validacao de regras de negocio."""

    pass


class DisciplinaryWorkflowError(DisciplinaryServiceError):
    """Erro no fluxo de workflow."""

    pass


class DisciplinaryNotFoundError(DisciplinaryServiceError):
    """Medida disciplinar nao encontrada."""

    pass


class DisciplinaryService:
    """
    Servico principal para gestao de medidas disciplinares.

    Implementa toda a logica de negocio, validacoes e workflow
    para medidas administrativas conforme CLT.
    """

    # Constantes CLT
    MAX_SUSPENSION_DAYS = 30
    IMMEDIATE_PRINCIPLES_DAYS = 30  # Imediaticidade: medida deve ser aplicada em ate 30 dias

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa o servico.

        Args:
            db: Sessao async do SQLAlchemy
        """
        self.db = db
        self.repo = DisciplinaryRepository(db)
        self.template_repo = TemplateRepository(db)
        self.signature_repo = SignatureRepository(db)

    async def create(
        self,
        data: DisciplinaryActionCreate,
        tenant_id: str,
        created_by: str,
    ) -> DisciplinaryAction:
        """
        Cria uma nova medida disciplinar.

        Args:
            data: Dados da medida
            tenant_id: ID do tenant
            created_by: ID do usuario criador

        Returns:
            Medida disciplinar criada

        Raises:
            DisciplinaryValidationError: Se validacao falhar
        """
        # Validar regras de negocio
        await self._validate_creation(data, tenant_id)

        # Criar medida
        action = await self.repo.create(data, tenant_id, created_by)

        logger.info(
            f"Medida disciplinar criada: {action.code}",
            extra={
                "action_id": action.id,
                "action_type": action.action_type,
                "employee_id": action.employee_id,
                "created_by": created_by,
            },
        )

        return action

    async def _validate_creation(self, data: DisciplinaryActionCreate, tenant_id: str) -> None:
        """
        Valida regras de negocio para criacao.

        Args:
            data: Dados da medida
            tenant_id: ID do tenant

        Raises:
            DisciplinaryValidationError: Se validacao falhar
        """
        errors = []

        # 1. Validar principio da imediaticidade (ate 30 dias do fato)
        days_since_incident = (date.today() - data.incident_date).days
        if days_since_incident > self.IMMEDIATE_PRINCIPLES_DAYS:
            errors.append(
                f"Principio da imediaticidade: medida deve ser aplicada em ate "
                f"{self.IMMEDIATE_PRINCIPLES_DAYS} dias do incidente. "
                f"Passaram {days_since_incident} dias."
            )

        # 2. Validar limite de suspensao
        if data.action_type == DisciplinaryActionType.SUSPENSAO:
            if data.suspension_days and data.suspension_days > self.MAX_SUSPENSION_DAYS:
                errors.append(f"CLT Art. 474: Suspensao nao pode exceder {self.MAX_SUSPENSION_DAYS} dias.")

        # 3. Validar progressao disciplinar
        await self._validate_progression(data, tenant_id, errors)

        if errors:
            raise DisciplinaryValidationError("; ".join(errors))

    async def _validate_progression(
        self,
        data: DisciplinaryActionCreate,
        tenant_id: str,
        errors: list[str],
    ) -> None:
        """
        Valida progressao disciplinar (advertencia -> suspensao -> justa causa).

        A progressao nao e obrigatoria por lei, mas e recomendada para
        evitar reversao em processo trabalhista.

        Args:
            data: Dados da medida
            tenant_id: ID do tenant
            errors: Lista de erros para adicionar
        """
        # Busca historico
        history = await self.repo.get_by_employee(data.employee_id, tenant_id)
        applied_history = [h for h in history if h.status == DisciplinaryActionStatus.APLICADA.value]

        warnings = [
            h
            for h in applied_history
            if h.action_type
            in [
                DisciplinaryActionType.ADVERTENCIA_VERBAL.value,
                DisciplinaryActionType.ADVERTENCIA_ESCRITA.value,
            ]
        ]
        suspensions = [h for h in applied_history if h.action_type == DisciplinaryActionType.SUSPENSAO.value]

        # Aviso se suspensao sem advertencia previa
        if data.action_type == DisciplinaryActionType.SUSPENSAO and len(warnings) == 0:
            # Nao e erro, mas registra aviso no log
            logger.warning(
                f"Suspensao sem advertencia previa para funcionario {data.employee_id}",
                extra={"tenant_id": tenant_id},
            )

        # Aviso se justa causa sem medidas previas
        if data.action_type == DisciplinaryActionType.DEMISSAO_JUSTA_CAUSA:
            if len(warnings) == 0 and len(suspensions) == 0:
                logger.warning(
                    f"Demissao por justa causa sem medidas previas para funcionario {data.employee_id}",
                    extra={"tenant_id": tenant_id},
                )

    async def get_by_id(self, action_id: str, tenant_id: str) -> DisciplinaryAction:
        """
        Busca medida por ID.

        Args:
            action_id: ID da medida
            tenant_id: ID do tenant

        Returns:
            Medida disciplinar

        Raises:
            DisciplinaryNotFoundError: Se nao encontrada
        """
        action = await self.repo.get_by_id(action_id, tenant_id)
        if not action:
            raise DisciplinaryNotFoundError(f"Medida disciplinar {action_id} nao encontrada")
        return action

    async def get_by_code(self, code: str, tenant_id: str) -> DisciplinaryAction:
        """
        Busca medida por codigo.

        Args:
            code: Codigo da medida
            tenant_id: ID do tenant

        Returns:
            Medida disciplinar

        Raises:
            DisciplinaryNotFoundError: Se nao encontrada
        """
        action = await self.repo.get_by_code(code, tenant_id)
        if not action:
            raise DisciplinaryNotFoundError(f"Medida disciplinar {code} nao encontrada")
        return action

    async def list(
        self,
        tenant_id: str,
        filters: DisciplinaryFilter | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> DisciplinaryActionListResponse:
        """
        Lista medidas com filtros e paginacao.

        Args:
            tenant_id: ID do tenant
            filters: Filtros de busca
            page: Pagina atual
            page_size: Itens por pagina

        Returns:
            Resposta paginada
        """
        actions, total = await self.repo.list(tenant_id, filters, page, page_size)
        total_pages = (total + page_size - 1) // page_size

        return DisciplinaryActionListResponse(
            items=[DisciplinaryActionResponse.model_validate(a) for a in actions],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def update(
        self,
        action_id: str,
        tenant_id: str,
        data: DisciplinaryActionUpdate,
    ) -> DisciplinaryAction:
        """
        Atualiza uma medida disciplinar.

        Args:
            action_id: ID da medida
            tenant_id: ID do tenant
            data: Dados para atualizacao

        Returns:
            Medida atualizada

        Raises:
            DisciplinaryNotFoundError: Se nao encontrada
            DisciplinaryWorkflowError: Se status nao permite edicao
        """
        action = await self.get_by_id(action_id, tenant_id)

        if not action.can_be_edited:
            raise DisciplinaryWorkflowError(f"Medida {action.code} nao pode ser editada no status {action.status}")

        updated = await self.repo.update(action_id, tenant_id, data)
        if not updated:
            raise DisciplinaryNotFoundError(f"Medida {action_id} nao encontrada")

        return updated

    async def delete(self, action_id: str, tenant_id: str) -> bool:
        """
        Remove uma medida disciplinar (soft delete).

        Args:
            action_id: ID da medida
            tenant_id: ID do tenant

        Returns:
            True se deletada

        Raises:
            DisciplinaryNotFoundError: Se nao encontrada
        """
        action = await self.get_by_id(action_id, tenant_id)

        if not action.can_be_edited:
            raise DisciplinaryWorkflowError(f"Medida {action.code} nao pode ser removida no status {action.status}")

        return await self.repo.delete(action_id, tenant_id)

    # ==========================================================================
    # WORKFLOW
    # ==========================================================================

    async def submit_for_approval(
        self,
        action_id: str,
        tenant_id: str,
        submitted_by: str,
        notes: str | None = None,
    ) -> DisciplinaryAction:
        """
        Submete medida para aprovacao.

        Args:
            action_id: ID da medida
            tenant_id: ID do tenant
            submitted_by: ID de quem submeteu
            notes: Notas adicionais

        Returns:
            Medida atualizada

        Raises:
            DisciplinaryWorkflowError: Se nao pode ser submetida
        """
        action = await self.get_by_id(action_id, tenant_id)

        if not action.can_be_submitted:
            raise DisciplinaryWorkflowError(f"Medida {action.code} nao pode ser submetida no status {action.status}")

        # Gerar documento se ainda nao gerado
        if not action.document_text:
            await self._generate_document(action, tenant_id)

        updated = await self.repo.update_status(
            action_id,
            tenant_id,
            DisciplinaryActionStatus.PENDENTE_APROVACAO,
        )

        logger.info(
            f"Medida {action.code} submetida para aprovacao",
            extra={"action_id": action_id, "submitted_by": submitted_by},
        )

        return updated  # type: ignore

    async def approve(
        self,
        action_id: str,
        tenant_id: str,
        approved_by: str,
        request: ApproveRequest,
    ) -> DisciplinaryAction:
        """
        Aprova uma medida disciplinar.

        Args:
            action_id: ID da medida
            tenant_id: ID do tenant
            approved_by: ID de quem aprovou
            request: Dados da aprovacao

        Returns:
            Medida aprovada

        Raises:
            DisciplinaryWorkflowError: Se nao pode ser aprovada
        """
        action = await self.get_by_id(action_id, tenant_id)

        if not action.can_be_approved:
            raise DisciplinaryWorkflowError(f"Medida {action.code} nao pode ser aprovada no status {action.status}")

        application_date = request.application_date or date.today()

        updated = await self.repo.update_status(
            action_id,
            tenant_id,
            DisciplinaryActionStatus.PENDENTE_ASSINATURA,
            approved_by_id=approved_by,
            approved_at=datetime.utcnow(),
            approval_notes=request.notes,
            application_date=application_date,
        )

        logger.info(
            f"Medida {action.code} aprovada",
            extra={"action_id": action_id, "approved_by": approved_by},
        )

        return updated  # type: ignore

    async def reject(
        self,
        action_id: str,
        tenant_id: str,
        rejected_by: str,
        request: RejectRequest,
    ) -> DisciplinaryAction:
        """
        Rejeita uma medida disciplinar.

        Args:
            action_id: ID da medida
            tenant_id: ID do tenant
            rejected_by: ID de quem rejeitou
            request: Dados da rejeicao

        Returns:
            Medida rejeitada

        Raises:
            DisciplinaryWorkflowError: Se nao pode ser rejeitada
        """
        action = await self.get_by_id(action_id, tenant_id)

        if not action.can_be_approved:  # Mesma verificacao
            raise DisciplinaryWorkflowError(f"Medida {action.code} nao pode ser rejeitada no status {action.status}")

        updated = await self.repo.update_status(
            action_id,
            tenant_id,
            DisciplinaryActionStatus.REJEITADA,
            rejected_by_id=rejected_by,
            rejected_at=datetime.utcnow(),
            rejection_reason=request.reason,
        )

        logger.info(
            f"Medida {action.code} rejeitada",
            extra={
                "action_id": action_id,
                "rejected_by": rejected_by,
                "reason": request.reason,
            },
        )

        return updated  # type: ignore

    async def apply(
        self,
        action_id: str,
        tenant_id: str,
    ) -> DisciplinaryAction:
        """
        Aplica a medida disciplinar (apos todas assinaturas).

        Args:
            action_id: ID da medida
            tenant_id: ID do tenant

        Returns:
            Medida aplicada

        Raises:
            DisciplinaryWorkflowError: Se nao pode ser aplicada
        """
        action = await self.get_by_id(action_id, tenant_id)

        # Verificar se tem as assinaturas necessarias ou recusa registrada
        if action.status not in [
            DisciplinaryActionStatus.ASSINADA.value,
            DisciplinaryActionStatus.RECUSADA_ASSINATURA.value,
        ]:
            raise DisciplinaryWorkflowError(f"Medida {action.code} precisa de assinaturas antes de ser aplicada")

        updated = await self.repo.update_status(
            action_id,
            tenant_id,
            DisciplinaryActionStatus.APLICADA,
        )

        logger.info(
            f"Medida {action.code} aplicada",
            extra={"action_id": action_id},
        )

        # Se suspensao, criar evento de afastamento no DP
        if action.is_suspension:
            await self._notify_hr_suspension(action)

        return updated  # type: ignore

    async def cancel(
        self,
        action_id: str,
        tenant_id: str,
        cancelled_by: str,
        reason: str,
    ) -> DisciplinaryAction:
        """
        Cancela uma medida disciplinar.

        Args:
            action_id: ID da medida
            tenant_id: ID do tenant
            cancelled_by: ID de quem cancelou
            reason: Motivo do cancelamento

        Returns:
            Medida cancelada
        """
        action = await self.get_by_id(action_id, tenant_id)

        # Nao pode cancelar se ja aplicada
        if action.status == DisciplinaryActionStatus.APLICADA.value:
            raise DisciplinaryWorkflowError(f"Medida {action.code} ja foi aplicada e nao pode ser cancelada")

        updated = await self.repo.update_status(
            action_id,
            tenant_id,
            DisciplinaryActionStatus.CANCELADA,
            metadata={
                **(action.metadata or {}),
                "cancelled_by": cancelled_by,
                "cancelled_at": datetime.utcnow().isoformat(),
                "cancellation_reason": reason,
            },
        )

        logger.info(
            f"Medida {action.code} cancelada",
            extra={
                "action_id": action_id,
                "cancelled_by": cancelled_by,
                "reason": reason,
            },
        )

        return updated  # type: ignore

    # ==========================================================================
    # DOCUMENTO
    # ==========================================================================

    async def generate_document(
        self,
        action_id: str,
        tenant_id: str,
        request: GenerateDocumentRequest | None = None,
    ) -> GenerateDocumentResponse:
        """
        Gera documento a partir de template.

        Args:
            action_id: ID da medida
            tenant_id: ID do tenant
            request: Dados opcionais

        Returns:
            Documento gerado
        """
        action = await self.get_by_id(action_id, tenant_id)
        return await self._generate_document(action, tenant_id, request)

    async def _generate_document(
        self,
        action: DisciplinaryAction,
        tenant_id: str,
        request: GenerateDocumentRequest | None = None,
    ) -> GenerateDocumentResponse:
        """
        Gera documento internamente.

        Args:
            action: Medida disciplinar
            tenant_id: ID do tenant
            request: Dados opcionais

        Returns:
            Documento gerado
        """
        import hashlib

        # Buscar template
        template_id = request.template_id if request else action.document_template_id
        template = None

        if template_id:
            template = await self.template_repo.get_by_id(template_id, tenant_id)

        if not template:
            template = await self.template_repo.get_default(tenant_id, action.action_type)

        if not template:
            raise DisciplinaryValidationError(f"Nenhum template encontrado para {action.action_type}")

        # Montar contexto
        context = self._build_document_context(action)
        if request and request.extra_context:
            context.update(request.extra_context)

        # Renderizar
        document_text = template.render(context)

        # Calcular hash
        document_hash = hashlib.sha256(document_text.encode("utf-8")).hexdigest()

        # Atualizar medida
        action.document_text = document_text
        action.document_hash = document_hash
        action.document_template_id = template.id
        action.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(
            f"Documento gerado para medida {action.code}",
            extra={"action_id": action.id, "template_id": template.id},
        )

        return GenerateDocumentResponse(
            document_text=document_text,
            document_hash=document_hash,
            template_id=template.id,
            generated_at=datetime.utcnow(),
            placeholders_used=template.placeholder_list,
        )

    def _build_document_context(self, action: DisciplinaryAction) -> dict[str, Any]:
        """
        Constroi contexto para renderizacao do documento.

        Args:
            action: Medida disciplinar

        Returns:
            Dicionario de contexto
        """

        # Formatar datas
        def format_date(d: date | None) -> str:
            return d.strftime("%d/%m/%Y") if d else ""

        # Categorias de motivo em portugues
        reason_display = {
            "falta": "Falta Injustificada",
            "atraso": "Atrasos Recorrentes",
            "insubordinacao": "Insubordinacao",
            "indisciplina": "Ato de Indisciplina",
            "dano_patrimonio": "Dano ao Patrimonio",
            "negligencia": "Negligencia no Desempenho",
            "embriaguez": "Embriaguez Habitual ou em Servico",
            "abandono_emprego": "Abandono de Emprego",
            "ato_improbidade": "Ato de Improbidade",
            "violacao_segredo": "Violacao de Segredo",
            "desistencia_habitual": "Desistencia Habitual",
            "ofensa_fisica": "Ofensas Fisicas",
            "ofensa_moral": "Ofensas Morais",
            "jogos_azar": "Pratica de Jogos de Azar",
            "perda_habilitacao": "Perda de Habilitacao Profissional",
            "outros": "Outros",
        }

        return {
            # Funcionario
            "employee_name": action.employee_name,
            "employee_cpf": action.employee_cpf,
            "employee_position": action.employee_position or "",
            "employee_admission_date": format_date(action.employee_admission_date),
            # Incidente
            "incident_date": format_date(action.incident_date),
            "application_date": format_date(action.application_date or date.today()),
            "reason_description": action.reason_description,
            "reason_category": action.reason_category,
            "reason_category_display": reason_display.get(action.reason_category, action.reason_category),
            # Suspensao
            "suspension_days": str(action.suspension_days or ""),
            "suspension_start_date": format_date(action.suspension_start_date),
            "suspension_end_date": format_date(action.suspension_end_date),
            # Testemunhas
            "witness_1_name": action.witness_1_name or "",
            "witness_1_cpf": action.witness_1_cpf or "",
            "witness_2_name": action.witness_2_name or "",
            "witness_2_cpf": action.witness_2_cpf or "",
            # Historico
            "previous_warnings": str(action.previous_warnings_count),
            "previous_suspensions": str(action.previous_suspensions_count),
            # Empresa
            "company_name": "JORDAN SANTOS DE JESUS LTDA",
            "company_cnpj": "35.710.481/0001-03",
            # Localizacao
            "city": "Manaus",
            "state": "AM",
            # Data atual
            "current_date": date.today().strftime("%d/%m/%Y"),
            "current_datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            # Local de trabalho
            "post_name": "",
            "client_name": "",
        }

    # ==========================================================================
    # OUTROS
    # ==========================================================================

    async def get_employee_history(
        self,
        employee_id: str,
        tenant_id: str,
    ) -> builtins.list[DisciplinaryAction]:
        """
        Busca historico disciplinar de um funcionario.

        Args:
            employee_id: ID do funcionario
            tenant_id: ID do tenant

        Returns:
            Lista de medidas
        """
        return await self.repo.get_by_employee(employee_id, tenant_id)

    async def get_pending_approval(
        self,
        tenant_id: str,
    ) -> builtins.list[DisciplinaryAction]:
        """
        Lista medidas pendentes de aprovacao.

        Args:
            tenant_id: ID do tenant

        Returns:
            Lista de medidas pendentes
        """
        return await self.repo.get_pending_approval(tenant_id)

    async def get_stats(self, tenant_id: str) -> DisciplinaryStats:
        """
        Obtem estatisticas.

        Args:
            tenant_id: ID do tenant

        Returns:
            Estatisticas
        """
        return await self.repo.get_stats(tenant_id)

    async def _notify_hr_suspension(self, action: DisciplinaryAction) -> None:
        """
        Notifica RH sobre suspensao para criar afastamento.

        Args:
            action: Medida de suspensao
        """
        # TODO: Integrar com modulo de DP para criar evento de afastamento
        logger.info(
            f"Notificando RH sobre suspensao do funcionario {action.employee_id}",
            extra={
                "action_id": action.id,
                "suspension_start": str(action.suspension_start_date),
                "suspension_end": str(action.suspension_end_date),
                "days": action.suspension_days,
            },
        )


def get_disciplinary_service(db: AsyncSession) -> DisciplinaryService:
    """
    Factory para criar instancia do servico.

    Args:
        db: Sessao do banco de dados

    Returns:
        Instancia do DisciplinaryService
    """
    return DisciplinaryService(db)
