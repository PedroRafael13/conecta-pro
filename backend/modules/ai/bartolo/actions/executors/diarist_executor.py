"""
Executor de acoes relacionadas a diaristas.

Acoes suportadas:
- CREATE_DIARIST: registrar nova diarista
- SCHEDULE_DIARIST: escalar diarista para trabalho
- EVALUATE_DIARIST: registrar avaliacao com notas
- APPROVE_DIARIST_PAYMENT: aprovar pagamento pendente
- GENERATE_DIARIST_PAYMENT: gerar pagamento para periodo

Nota: Os ActionTypes CREATE_DIARIST e SCHEDULE_DIARIST devem ser adicionados
ao enum ActionType em action_types.py para integracao completa.
Enquanto isso, este executor usa comparacao por string value.
"""
import logging
import re
from datetime import datetime, date, time
from decimal import Decimal
from uuid import uuid4, UUID
from typing import Optional

from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository
from modules.operacional.diaristas.models.diarist import (
    Diarist,
    DiaristSchedule,
    DiaristEvaluation,
    DiaristPayment,
    DiaristStatus,
    ScheduleStatus,
    PaymentStatus,
)
from ..action_schemas import ActionRequest, ActionPreview, ActionResult
from ..action_types import ActionStatus
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)

# Constantes locais para action types de diaristas.
# Compativel com o enum ActionType quando os valores forem adicionados.
DIARIST_ACTION_CREATE = "create_diarist"
DIARIST_ACTION_SCHEDULE = "schedule_diarist"
DIARIST_ACTION_EVALUATE = "evaluate_diarist"
DIARIST_ACTION_APPROVE_PAYMENT = "approve_diarist_payment"
DIARIST_ACTION_GENERATE_PAYMENT = "generate_diarist_payment"


def _get_action_value(action_type) -> str:
    """Extrai o valor string de um ActionType (enum ou string)."""
    return action_type.value if hasattr(action_type, "value") else str(action_type)


class DiaristActionExecutor(BaseActionExecutor):
    """Executor para acoes de diaristas."""

    # Action types suportados por este executor
    SUPPORTED_ACTIONS = {
        DIARIST_ACTION_CREATE,
        DIARIST_ACTION_SCHEDULE,
        DIARIST_ACTION_EVALUATE,
        DIARIST_ACTION_APPROVE_PAYMENT,
        DIARIST_ACTION_GENERATE_PAYMENT,
    }

    def supports(self, action_type) -> bool:
        """Verifica se este executor suporta o tipo de acao."""
        return _get_action_value(action_type) in self.SUPPORTED_ACTIONS

    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para acao de diarista."""
        action_value = _get_action_value(request.action_type)

        if action_value == DIARIST_ACTION_CREATE:
            return await self._create_diarist_preview(request)
        elif action_value == DIARIST_ACTION_SCHEDULE:
            return await self._schedule_diarist_preview(request)
        elif action_value == DIARIST_ACTION_EVALUATE:
            return await self._evaluate_diarist_preview(request)
        elif action_value == DIARIST_ACTION_APPROVE_PAYMENT:
            return await self._approve_payment_preview(request)
        elif action_value == DIARIST_ACTION_GENERATE_PAYMENT:
            return await self._generate_payment_preview(request)
        else:
            raise ValueError(f"Acao nao suportada: {action_value}")

    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """Executa acao de diarista."""
        action_value = _get_action_value(request.action_type)
        started_at = datetime.utcnow()

        try:
            if action_value == DIARIST_ACTION_CREATE:
                result = await self._execute_create_diarist(request, action_id, started_at)
            elif action_value == DIARIST_ACTION_SCHEDULE:
                result = await self._execute_schedule_diarist(request, action_id, started_at)
            elif action_value == DIARIST_ACTION_EVALUATE:
                result = await self._execute_evaluate_diarist(request, action_id, started_at)
            elif action_value == DIARIST_ACTION_APPROVE_PAYMENT:
                result = await self._execute_approve_payment(request, action_id, started_at)
            elif action_value == DIARIST_ACTION_GENERATE_PAYMENT:
                result = await self._execute_generate_payment(request, action_id, started_at)
            else:
                raise ValueError(f"Acao nao suportada: {action_value}")

            return result

        except Exception as e:
            logger.error(f"Erro ao executar acao {action_value}: {e}")
            return ActionResult(
                action_id=action_id,
                action_type=request.action_type,
                status=ActionStatus.FAILED,
                success=False,
                message=f"Erro ao executar acao: {action_value}",
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
            )

    # ==================== PREVIEW METHODS ====================

    async def _create_diarist_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para registro de diarista."""
        params = request.parameters
        nome = params.get("nome")
        cpf = params.get("cpf")
        valor_diaria = params.get("valor_diaria")

        changes_summary = []
        warnings = []
        affected_entities = []

        # Validar parametros minimos
        if not nome:
            warnings.append("Nome nao informado")
        else:
            changes_summary.append(f"Nome: {nome}")

        if not cpf:
            warnings.append("CPF nao informado")
        else:
            changes_summary.append(f"CPF: {cpf}")

        if not valor_diaria:
            warnings.append("Valor da diaria nao informado (sera usado R$ 150,00 padrao)")
            valor_diaria = 150.00
        changes_summary.append(f"Valor diaria: R$ {float(valor_diaria):,.2f}")

        # Verificar se CPF ja existe
        if cpf:
            try:
                repo = DiaristRepository(self.db)
                cpf_limpo = re.sub(r"\D", "", cpf)
                existing = await repo.get_by_cpf(cpf_limpo)
                if existing:
                    warnings.append(f"CPF {cpf} ja cadastrado para: {existing.nome}")
            except Exception as e:
                logger.warning(f"Erro ao verificar CPF duplicado: {e}")

        # Dados opcionais no preview
        tipos = params.get("tipos_servico", [])
        if tipos:
            changes_summary.append(f"Tipos: {', '.join(tipos)}")

        telefone = params.get("telefone")
        if telefone:
            changes_summary.append(f"Telefone: {telefone}")

        email = params.get("email")
        if email:
            changes_summary.append(f"Email: {email}")

        title = f"Cadastrar Diarista - {nome or 'Nova'}"
        description = "Registrar nova diarista no sistema"

        # Permissao - usar ALLOCATIONS_CREATE como proxy para diaristas
        required_perm = "allocations:create"
        user_role = getattr(self, "user_role", None)
        user_has_perm = False
        if user_role:
            try:
                from modules.operacional.permissions import has_permission, Permission
                user_has_perm = has_permission(user_role, Permission.ALLOCATIONS_CREATE)
            except Exception:
                pass
        logger.info(f"Permissao {required_perm}: role={user_role}, has_perm={user_has_perm}")

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    async def _schedule_diarist_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para escalar diarista."""
        params = request.parameters
        diarist_id = params.get("diarist_id")
        data_trabalho = params.get("data_trabalho")
        condominio_id = params.get("condominio_id")

        changes_summary = []
        warnings = []
        affected_entities = []

        repo = DiaristRepository(self.db)

        # Buscar diarista
        diarista = None
        if diarist_id:
            try:
                diarista = await repo.get_by_id(UUID(diarist_id))
            except (ValueError, Exception) as e:
                logger.warning(f"Erro ao buscar diarista {diarist_id}: {e}")

        if not diarista:
            warnings.append("Diarista nao encontrada")
            title = "Escalar Diarista"
            description = "Diarista nao encontrada"
        else:
            affected_entities.append({
                "type": "diarist",
                "id": str(diarista.id),
                "name": diarista.nome,
            })
            changes_summary.append(f"Diarista: {diarista.nome}")
            changes_summary.append(f"CPF: {diarista.cpf}")
            changes_summary.append(f"Valor diaria: R$ {float(diarista.valor_diaria or 0):,.2f}")

            if diarista.status != DiaristStatus.ATIVO.value:
                warnings.append(f"Diarista nao esta ativa (status: {diarista.status})")

            title = f"Escalar Diarista - {diarista.nome}"
            description = f"Agendar trabalho para {diarista.nome}"

        # Data
        if not data_trabalho:
            warnings.append("Data de trabalho nao informada")
        else:
            changes_summary.append(f"Data: {data_trabalho}")

            # Verificar disponibilidade
            if diarista and diarist_id:
                try:
                    data_obj = date.fromisoformat(data_trabalho) if isinstance(data_trabalho, str) else data_trabalho
                    disponivel = await repo.check_availability(UUID(diarist_id), data_obj)
                    if not disponivel:
                        warnings.append("Diarista nao disponivel nesta data (ja possui agendamento ou dia indisponivel)")
                except Exception as e:
                    logger.warning(f"Erro ao verificar disponibilidade: {e}")

        # Condominio
        if not condominio_id:
            warnings.append("Condominio nao informado")

        # Horarios
        hora_inicio = params.get("hora_inicio", "08:00")
        hora_fim = params.get("hora_fim", "17:00")
        changes_summary.append(f"Horario: {hora_inicio} - {hora_fim}")

        # Permissao
        required_perm = "allocations:create"
        user_role = getattr(self, "user_role", None)
        user_has_perm = False
        if user_role:
            try:
                from modules.operacional.permissions import has_permission, Permission
                user_has_perm = has_permission(user_role, Permission.ALLOCATIONS_CREATE)
            except Exception:
                pass
        logger.info(f"Permissao {required_perm}: role={user_role}, has_perm={user_has_perm}")

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title if diarista else "Escalar Diarista",
            description=description if diarista else "Diarista nao encontrada",
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    # ==================== EXECUTE METHODS ====================

    async def _execute_create_diarist(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa criacao de diarista."""
        params = request.parameters
        nome = params.get("nome")
        cpf = params.get("cpf")
        valor_diaria = params.get("valor_diaria", 150.00)

        if not nome or not cpf:
            raise ValueError("Nome e CPF sao obrigatorios")

        cpf_limpo = re.sub(r"\D", "", cpf)

        repo = DiaristRepository(self.db)

        # Verificar duplicidade
        existing = await repo.get_by_cpf(cpf_limpo)
        if existing:
            raise ValueError(f"CPF {cpf} ja cadastrado para: {existing.nome}")

        # Criar diarista
        diarista = Diarist(
            nome=nome,
            cpf=cpf_limpo,
            rg=params.get("rg"),
            telefone=params.get("telefone"),
            telefone_emergencia=params.get("telefone_emergencia"),
            email=params.get("email"),
            endereco=params.get("endereco"),
            cidade=params.get("cidade"),
            estado=params.get("estado"),
            cep=params.get("cep"),
            tipos_servico=params.get("tipos_servico", []),
            especialidades=params.get("especialidades", []),
            experiencia_anos=params.get("experiencia_anos", 0),
            dias_disponiveis=params.get("dias_disponiveis", []),
            hora_inicio_disponivel=time(8, 0),
            hora_fim_disponivel=time(17, 0),
            aceita_hora_extra=params.get("aceita_hora_extra", True),
            valor_diaria=Decimal(str(valor_diaria)),
            valor_hora=Decimal(str(params.get("valor_hora", 0))) if params.get("valor_hora") else None,
            valor_hora_extra=Decimal(str(params.get("valor_hora_extra", 25.00))),
            banco=params.get("banco"),
            agencia=params.get("agencia"),
            conta=params.get("conta"),
            tipo_conta=params.get("tipo_conta"),
            pix=params.get("pix"),
            status=DiaristStatus.ATIVO.value,
        )

        created = await repo.create(diarista)
        logger.info(f"Diarista criada via Bartolo: {created.id} - {created.nome}")

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Diarista '{nome}' cadastrada com sucesso",
            details={
                "diarist_id": str(created.id),
                "nome": created.nome,
                "cpf": created.cpf,
                "valor_diaria": float(created.valor_diaria or 0),
                "status": created.status,
            },
            affected_entities=[
                {"type": "diarist", "id": str(created.id)},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    async def _execute_schedule_diarist(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa escalacao de diarista."""
        params = request.parameters
        diarist_id = params.get("diarist_id")
        data_trabalho = params.get("data_trabalho")
        condominio_id = params.get("condominio_id")

        if not diarist_id:
            raise ValueError("ID da diarista e obrigatorio")
        if not data_trabalho:
            raise ValueError("Data de trabalho e obrigatoria")
        if not condominio_id:
            raise ValueError("ID do condominio e obrigatorio")

        repo = DiaristRepository(self.db)

        # Buscar diarista
        diarista = await repo.get_by_id(UUID(diarist_id))
        if not diarista:
            raise ValueError(f"Diarista {diarist_id} nao encontrada")

        if diarista.status != DiaristStatus.ATIVO.value:
            raise ValueError(f"Diarista nao esta ativa (status: {diarista.status})")

        # Parsear data
        data_obj = date.fromisoformat(data_trabalho) if isinstance(data_trabalho, str) else data_trabalho

        # Verificar disponibilidade
        disponivel = await repo.check_availability(UUID(diarist_id), data_obj)
        if not disponivel:
            raise ValueError("Diarista nao disponivel nesta data")

        # Parsear horarios
        hora_inicio_str = params.get("hora_inicio", "08:00")
        hora_fim_str = params.get("hora_fim", "17:00")

        hora_inicio_parts = hora_inicio_str.split(":")
        hora_fim_parts = hora_fim_str.split(":")
        hora_inicio = time(int(hora_inicio_parts[0]), int(hora_inicio_parts[1]))
        hora_fim = time(int(hora_fim_parts[0]), int(hora_fim_parts[1]))

        # Criar schedule
        schedule = DiaristSchedule(
            diarist_id=UUID(diarist_id),
            condominio_id=UUID(condominio_id),
            unidade_id=UUID(params["unidade_id"]) if params.get("unidade_id") else None,
            data_trabalho=data_obj,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            valor_previsto=diarista.valor_diaria,
            tarefas=params.get("tarefas", []),
            observacoes=params.get("observacoes"),
            status="AGENDADO",
        )

        created = await repo.create_schedule(schedule)
        logger.info(
            f"Diarista escalada via Bartolo: {diarista.nome} em {data_trabalho} - schedule {created.id}"
        )

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Diarista '{diarista.nome}' escalada para {data_obj.strftime('%d/%m/%Y')}",
            details={
                "schedule_id": str(created.id),
                "diarist_id": str(diarista.id),
                "diarist_nome": diarista.nome,
                "data_trabalho": data_obj.isoformat(),
                "horario": f"{hora_inicio_str} - {hora_fim_str}",
                "valor_previsto": float(diarista.valor_diaria or 0),
                "status": "AGENDADO",
            },
            affected_entities=[
                {"type": "diarist_schedule", "id": str(created.id)},
                {"type": "diarist", "id": str(diarista.id)},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    # ==================== EVALUATE PREVIEW & EXECUTE ====================

    async def _evaluate_diarist_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para avaliacao de diarista."""
        params = request.parameters
        diarist_id = params.get("diarist_id")
        schedule_id = params.get("schedule_id")
        nota_geral = params.get("nota_geral")

        changes_summary = []
        warnings = []
        affected_entities = []

        repo = DiaristRepository(self.db)

        # Buscar diarista
        diarista = None
        if diarist_id:
            try:
                diarista = await repo.get_by_id(UUID(diarist_id))
            except (ValueError, Exception) as e:
                logger.warning(f"Erro ao buscar diarista {diarist_id}: {e}")

        if not diarista:
            warnings.append("Diarista nao encontrada")
            title = "Avaliar Diarista"
            description = "Diarista nao encontrada"
        else:
            affected_entities.append({
                "type": "diarist",
                "id": str(diarista.id),
                "name": diarista.nome,
            })
            changes_summary.append(f"Diarista: {diarista.nome}")
            title = f"Avaliar Diarista - {diarista.nome}"
            description = f"Registrar avaliacao para {diarista.nome}"

        # Verificar avaliacao duplicada
        if schedule_id:
            try:
                existente = await repo.get_evaluation_by_schedule(UUID(schedule_id))
                if existente:
                    warnings.append(f"Ja existe avaliacao para este agendamento (nota: {existente.nota_geral}/5)")
            except Exception:
                pass
            changes_summary.append(f"Agendamento: {schedule_id}")

        # Notas
        if not nota_geral:
            warnings.append("Nota geral nao informada (obrigatoria, 1-5)")
        else:
            nota_geral = int(nota_geral)
            if nota_geral < 1 or nota_geral > 5:
                warnings.append("Nota geral deve ser entre 1 e 5")
            changes_summary.append(f"Nota geral: {nota_geral}/5")

        for campo, label in [
            ("nota_pontualidade", "Pontualidade"),
            ("nota_qualidade", "Qualidade"),
            ("nota_comportamento", "Comportamento"),
            ("nota_comunicacao", "Comunicacao"),
        ]:
            valor = params.get(campo)
            if valor:
                changes_summary.append(f"{label}: {valor}/5")

        comentario = params.get("comentario")
        if comentario:
            changes_summary.append(f"Comentario: {comentario[:50]}...")

        recomendaria = params.get("recomendaria", True)
        changes_summary.append(f"Recomendaria: {'Sim' if recomendaria else 'Nao'}")

        # Permissao
        required_perm = "allocations:create"
        user_role = getattr(self, "user_role", None)
        user_has_perm = False
        if user_role:
            try:
                from modules.operacional.permissions import has_permission, Permission
                user_has_perm = has_permission(user_role, Permission.ALLOCATIONS_CREATE)
            except Exception:
                pass

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=False,
            requires_confirmation=True,
        )

    async def _execute_evaluate_diarist(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa registro de avaliacao de diarista."""
        params = request.parameters
        diarist_id = params.get("diarist_id")
        schedule_id = params.get("schedule_id")
        nota_geral = params.get("nota_geral")
        user_id = params.get("user_id") or params.get("avaliador_id")

        if not diarist_id:
            raise ValueError("ID da diarista e obrigatorio")
        if not nota_geral:
            raise ValueError("Nota geral e obrigatoria")

        nota_geral = int(nota_geral)
        if nota_geral < 1 or nota_geral > 5:
            raise ValueError("Nota geral deve ser entre 1 e 5")

        repo = DiaristRepository(self.db)

        # Buscar diarista
        diarista = await repo.get_by_id(UUID(diarist_id))
        if not diarista:
            raise ValueError(f"Diarista {diarist_id} nao encontrada")

        # Verificar avaliacao duplicada
        if schedule_id:
            try:
                existente = await repo.get_evaluation_by_schedule(UUID(schedule_id))
                if existente:
                    raise ValueError(f"Ja existe avaliacao para o agendamento {schedule_id}")
            except ValueError:
                raise
            except Exception:
                pass

        # Validar notas opcionais
        def _parse_nota(valor):
            if valor is None:
                return None
            v = int(valor)
            if v < 1 or v > 5:
                return None
            return v

        # Criar avaliacao
        evaluation = DiaristEvaluation(
            diarist_id=UUID(diarist_id),
            schedule_id=UUID(schedule_id) if schedule_id else None,
            avaliador_id=UUID(user_id) if user_id else UUID("00000000-0000-0000-0000-000000000000"),
            nota_geral=nota_geral,
            nota_pontualidade=_parse_nota(params.get("nota_pontualidade")),
            nota_qualidade=_parse_nota(params.get("nota_qualidade")),
            nota_comportamento=_parse_nota(params.get("nota_comportamento")),
            nota_comunicacao=_parse_nota(params.get("nota_comunicacao")),
            comentario=params.get("comentario"),
            recomendaria=params.get("recomendaria", True),
        )

        created = await repo.create_evaluation(evaluation)
        logger.info(
            f"Avaliacao registrada via Bartolo: diarista {diarista.nome} - nota {nota_geral}/5 - evaluation {created.id}"
        )

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Avaliacao registrada para '{diarista.nome}' - Nota geral: {nota_geral}/5",
            details={
                "evaluation_id": str(created.id),
                "diarist_id": str(diarista.id),
                "diarist_nome": diarista.nome,
                "nota_geral": nota_geral,
                "nota_pontualidade": params.get("nota_pontualidade"),
                "nota_qualidade": params.get("nota_qualidade"),
                "nota_comportamento": params.get("nota_comportamento"),
                "nota_comunicacao": params.get("nota_comunicacao"),
                "recomendaria": params.get("recomendaria", True),
                "nova_media": float(diarista.avaliacao_media or 0),
            },
            affected_entities=[
                {"type": "diarist_evaluation", "id": str(created.id)},
                {"type": "diarist", "id": str(diarista.id)},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    # ==================== APPROVE PAYMENT PREVIEW & EXECUTE ====================

    async def _approve_payment_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para aprovacao de pagamento de diarista."""
        params = request.parameters
        pagamento_id = params.get("pagamento_id")

        changes_summary = []
        warnings = []
        affected_entities = []

        repo = DiaristRepository(self.db)

        pagamento = None
        if pagamento_id:
            try:
                pagamento = await repo.get_payment_by_id(UUID(pagamento_id))
            except (ValueError, Exception) as e:
                logger.warning(f"Erro ao buscar pagamento {pagamento_id}: {e}")

        if not pagamento:
            warnings.append("Pagamento nao encontrado")
            title = "Aprovar Pagamento"
            description = "Pagamento nao encontrado"
        else:
            nome = pagamento.diarist.nome if pagamento.diarist else "N/A"
            status_str = pagamento.status if isinstance(pagamento.status, str) else (pagamento.status.value if hasattr(pagamento.status, 'value') else str(pagamento.status))

            if status_str != "PENDENTE":
                warnings.append(f"Pagamento nao esta PENDENTE (status: {status_str})")

            affected_entities.append({
                "type": "diarist_payment",
                "id": str(pagamento.id),
                "name": f"Pagamento {nome}",
            })
            changes_summary.append(f"Diarista: {nome}")
            changes_summary.append(f"Valor bruto: R$ {float(pagamento.valor_bruto or 0):,.2f}")
            changes_summary.append(f"Valor liquido: R$ {float(pagamento.valor_liquido or 0):,.2f}")
            changes_summary.append(f"Referencia: {pagamento.data_referencia.strftime('%m/%Y') if pagamento.data_referencia else 'N/A'}")
            changes_summary.append(f"Status atual: {status_str} -> APROVADO")

            if pagamento.data_vencimento:
                changes_summary.append(f"Vencimento: {pagamento.data_vencimento.strftime('%d/%m/%Y')}")

            title = f"Aprovar Pagamento - {nome}"
            description = f"Aprovar pagamento de R$ {float(pagamento.valor_liquido or 0):,.2f} para {nome}"

        # Permissao
        required_perm = "allocations:create"
        user_role = getattr(self, "user_role", None)
        user_has_perm = False
        if user_role:
            try:
                from modules.operacional.permissions import has_permission, Permission
                user_has_perm = has_permission(user_role, Permission.ALLOCATIONS_CREATE)
            except Exception:
                pass

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    async def _execute_approve_payment(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa aprovacao de pagamento de diarista."""
        params = request.parameters
        pagamento_id = params.get("pagamento_id")

        if not pagamento_id:
            raise ValueError("ID do pagamento e obrigatorio")

        repo = DiaristRepository(self.db)

        pagamento = await repo.get_payment_by_id(UUID(pagamento_id))
        if not pagamento:
            raise ValueError(f"Pagamento {pagamento_id} nao encontrado")

        status_str = pagamento.status if isinstance(pagamento.status, str) else (pagamento.status.value if hasattr(pagamento.status, 'value') else str(pagamento.status))
        if status_str != "PENDENTE":
            raise ValueError(f"Pagamento nao esta PENDENTE (status: {status_str})")

        nome = pagamento.diarist.nome if pagamento.diarist else "N/A"

        # Aprovar pagamento
        pagamento.status = PaymentStatus.APROVADO.value
        await repo.update_payment(pagamento)

        logger.info(
            f"Pagamento aprovado via Bartolo: {pagamento_id} - diarista {nome} - R$ {float(pagamento.valor_liquido or 0):,.2f}"
        )

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Pagamento aprovado para '{nome}' - R$ {float(pagamento.valor_liquido or 0):,.2f}",
            details={
                "pagamento_id": str(pagamento.id),
                "diarist_id": str(pagamento.diarist_id),
                "diarist_nome": nome,
                "valor_bruto": float(pagamento.valor_bruto or 0),
                "valor_liquido": float(pagamento.valor_liquido or 0),
                "status": "APROVADO",
                "referencia": pagamento.data_referencia.strftime('%m/%Y') if pagamento.data_referencia else None,
            },
            affected_entities=[
                {"type": "diarist_payment", "id": str(pagamento.id)},
                {"type": "diarist", "id": str(pagamento.diarist_id)},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )

    # ==================== GENERATE PAYMENT PREVIEW & EXECUTE ====================

    async def _generate_payment_preview(self, request: ActionRequest) -> ActionPreview:
        """Cria preview para geracao de pagamento de diarista."""
        params = request.parameters
        diarist_id = params.get("diarist_id")
        periodo = params.get("periodo")
        condominio_id = params.get("condominio_id")

        changes_summary = []
        warnings = []
        affected_entities = []

        repo = DiaristRepository(self.db)

        # Buscar diarista
        diarista = None
        if diarist_id:
            try:
                diarista = await repo.get_by_id(UUID(diarist_id))
            except (ValueError, Exception) as e:
                logger.warning(f"Erro ao buscar diarista {diarist_id}: {e}")

        if not diarista:
            warnings.append("Diarista nao encontrada")
            title = "Gerar Pagamento"
            description = "Diarista nao encontrada"
        else:
            affected_entities.append({
                "type": "diarist",
                "id": str(diarista.id),
                "name": diarista.nome,
            })
            changes_summary.append(f"Diarista: {diarista.nome}")
            changes_summary.append(f"CPF: {diarista.cpf}")
            title = f"Gerar Pagamento - {diarista.nome}"
            description = f"Gerar pagamento para {diarista.nome} - periodo {periodo or 'atual'}"

        if not periodo:
            periodo = datetime.utcnow().strftime("%Y-%m")
            warnings.append(f"Periodo nao informado, usando mes atual: {periodo}")
        changes_summary.append(f"Periodo: {periodo}")

        if not condominio_id:
            warnings.append("Condominio nao informado")

        # Calcular valores estimados se tiver diarista
        if diarista and periodo:
            try:
                ano, mes = periodo.split("-")
                data_inicio = date(int(ano), int(mes), 1)
                if int(mes) == 12:
                    data_fim = date(int(ano) + 1, 1, 1) - timedelta(days=1)
                else:
                    data_fim = date(int(ano), int(mes) + 1, 1) - timedelta(days=1)

                schedules = await repo.list_schedules(
                    diarist_id=diarista.id,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                )
                concluidos = [
                    s for s in schedules
                    if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == "CONCLUIDO"
                ]

                qtd = len(concluidos)
                valor_diaria = float(diarista.valor_diaria or 0)
                valor_bruto = qtd * valor_diaria

                # Retencoes
                inss = round(valor_bruto * 0.11, 2) if valor_bruto > 0 else 0
                iss = round(valor_bruto * 0.05, 2) if valor_bruto > 0 else 0
                irrf = round(valor_bruto * 0.075, 2) if valor_bruto > 1903.98 else 0
                total_retencoes = inss + iss + irrf
                valor_liquido = valor_bruto - total_retencoes

                changes_summary.append(f"Diarias concluidas: {qtd}")
                changes_summary.append(f"Valor diaria: R$ {valor_diaria:,.2f}")
                changes_summary.append(f"Valor bruto: R$ {valor_bruto:,.2f}")
                changes_summary.append(f"INSS (11%): R$ {inss:,.2f}")
                changes_summary.append(f"ISS (5%): R$ {iss:,.2f}")
                changes_summary.append(f"IRRF (7.5%): R$ {irrf:,.2f}")
                changes_summary.append(f"Valor liquido: R$ {valor_liquido:,.2f}")

                if qtd == 0:
                    warnings.append("Nenhuma diaria concluida no periodo")
            except Exception as e:
                logger.warning(f"Erro ao calcular preview de pagamento: {e}")
                warnings.append("Nao foi possivel calcular valores estimados")

        # Permissao
        required_perm = "allocations:create"
        user_role = getattr(self, "user_role", None)
        user_has_perm = False
        if user_role:
            try:
                from modules.operacional.permissions import has_permission, Permission
                user_has_perm = has_permission(user_role, Permission.ALLOCATIONS_CREATE)
            except Exception:
                pass

        return ActionPreview(
            action_id=str(uuid4()),
            action_type=request.action_type,
            title=title,
            description=description,
            affected_entities=affected_entities,
            changes_summary=changes_summary,
            warnings=warnings,
            required_permission=required_perm,
            user_has_permission=user_has_perm,
            parameters=params,
            can_be_undone=True,
            requires_confirmation=True,
        )

    async def _execute_generate_payment(
        self,
        request: ActionRequest,
        action_id: str,
        started_at: datetime,
    ) -> ActionResult:
        """Executa geracao de pagamento para diarista em periodo."""
        params = request.parameters
        diarist_id = params.get("diarist_id")
        periodo = params.get("periodo")
        condominio_id = params.get("condominio_id")

        if not diarist_id:
            raise ValueError("ID da diarista e obrigatorio")
        if not periodo:
            raise ValueError("Periodo e obrigatorio (formato: YYYY-MM)")

        repo = DiaristRepository(self.db)

        # Buscar diarista
        diarista = await repo.get_by_id(UUID(diarist_id))
        if not diarista:
            raise ValueError(f"Diarista {diarist_id} nao encontrada")

        # Parsear periodo
        try:
            ano, mes = periodo.split("-")
            data_inicio = date(int(ano), int(mes), 1)
            if int(mes) == 12:
                data_fim = date(int(ano) + 1, 1, 1) - timedelta(days=1)
            else:
                data_fim = date(int(ano), int(mes) + 1, 1) - timedelta(days=1)
        except (ValueError, IndexError):
            raise ValueError(f"Periodo invalido: {periodo}. Use formato YYYY-MM")

        # Buscar schedules concluidos no periodo
        schedules = await repo.list_schedules(
            diarist_id=diarista.id,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )
        concluidos = [
            s for s in schedules
            if (s.status.value if hasattr(s.status, 'value') else str(s.status)) == "CONCLUIDO"
        ]

        qtd = len(concluidos)
        if qtd == 0:
            raise ValueError(f"Nenhuma diaria concluida no periodo {periodo} para {diarista.nome}")

        valor_diaria = float(diarista.valor_diaria or 0)
        valor_bruto = qtd * valor_diaria

        # Calculo de retencoes fiscais
        # INSS: 11% sobre valor bruto
        inss = round(valor_bruto * 0.11, 2) if valor_bruto > 0 else 0
        # ISS: 5% sobre valor bruto
        iss = round(valor_bruto * 0.05, 2) if valor_bruto > 0 else 0
        # IRRF: 7.5% se acima da faixa de isencao (R$ 1.903,98)
        irrf = round(valor_bruto * 0.075, 2) if valor_bruto > 1903.98 else 0
        total_retencoes = inss + iss + irrf
        valor_liquido = valor_bruto - total_retencoes

        # Criar pagamento
        payment = DiaristPayment(
            diarist_id=UUID(diarist_id),
            condominio_id=UUID(condominio_id) if condominio_id else UUID("00000000-0000-0000-0000-000000000000"),
            data_referencia=data_inicio,
            data_vencimento=data_fim + timedelta(days=5),
            valor_bruto=Decimal(str(valor_bruto)),
            retencao_inss=Decimal(str(inss)),
            retencao_iss=Decimal(str(iss)),
            retencao_irrf=Decimal(str(irrf)),
            outros_descontos=Decimal("0"),
            valor_liquido=Decimal(str(valor_liquido)),
            forma_pagamento=params.get("forma_pagamento"),
            status=PaymentStatus.PENDENTE.value,
            schedules_ids=[str(s.id) for s in concluidos],
            descricao=f"Pagamento {periodo} - {qtd} diaria(s) - {diarista.nome}",
        )

        created = await repo.create_payment(payment)
        logger.info(
            f"Pagamento gerado via Bartolo: {created.id} - diarista {diarista.nome} - "
            f"R$ {valor_bruto:,.2f} bruto / R$ {valor_liquido:,.2f} liquido - periodo {periodo}"
        )

        return ActionResult(
            action_id=action_id,
            action_type=request.action_type,
            status=ActionStatus.COMPLETED,
            success=True,
            message=f"Pagamento gerado para '{diarista.nome}' - Periodo {periodo} - R$ {valor_liquido:,.2f} liquido",
            details={
                "payment_id": str(created.id),
                "diarist_id": str(diarista.id),
                "diarist_nome": diarista.nome,
                "periodo": periodo,
                "quantidade_diarias": qtd,
                "valor_bruto": valor_bruto,
                "retencao_inss": inss,
                "retencao_iss": iss,
                "retencao_irrf": irrf,
                "total_retencoes": total_retencoes,
                "valor_liquido": valor_liquido,
                "data_vencimento": (data_fim + timedelta(days=5)).isoformat(),
                "status": "PENDENTE",
                "schedules_ids": [str(s.id) for s in concluidos],
            },
            affected_entities=[
                {"type": "diarist_payment", "id": str(created.id)},
                {"type": "diarist", "id": str(diarista.id)},
            ],
            started_at=started_at,
            completed_at=datetime.utcnow(),
            duration_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
