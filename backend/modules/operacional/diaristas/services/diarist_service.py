"""Service para operações de Diaristas."""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.diaristas.models.diarist import (
    AssignmentStatus,
    Diarist,
    DiaristAssignment,
    DiaristEvaluation,
    DiaristPayment,
    DiaristSchedule,
    DiaristStatus,
    DiaristType,
    PaymentMethod,
    PaymentStatus,
    RecurrenceType,
    ScheduleStatus,
    Weekday,
)
from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository
from modules.operacional.diaristas.schemas.diarist_schemas import (
    BatchScheduleCreate,
    CheckinRequest,
    CheckoutRequest,
    DiaristAssignmentCreate,
    DiaristCreate,
    DiaristEvaluationCreate,
    DiaristPaymentCreate,
    DiaristScheduleCreate,
    DiaristUpdate,
    PayrollGenerateRequest,
)

logger = logging.getLogger(__name__)


class DiaristService:
    """Service para gerenciamento de diaristas."""

    def __init__(self, db: AsyncSession):
        """Inicializa o service."""
        self.db = db
        self.repository = DiaristRepository(db)

    # ==================== DIARIST OPERATIONS ====================

    async def create_diarist(self, data: DiaristCreate) -> Diarist:
        """Cria uma nova diarista."""
        # Verificar duplicidade
        if await self.repository.get_by_cpf(data.cpf):
            raise ValueError(f"CPF {data.cpf} já cadastrado")

        if data.email and await self.repository.get_by_email(data.email):
            raise ValueError(f"Email {data.email} já cadastrado")

        diarist = Diarist(
            nome=data.nome,
            cpf=data.cpf,
            rg=data.rg,
            data_nascimento=data.data_nascimento,
            telefone=data.telefone,
            telefone_emergencia=data.telefone_emergencia,
            email=data.email,
            endereco=data.endereco,
            cidade=data.cidade,
            estado=data.estado,
            cep=data.cep,
            tipos_servico=data.tipos_servico,
            especialidades=data.especialidades,
            experiencia_anos=data.experiencia_anos,
            referencias=data.referencias,
            documentos=data.documentos,
            dias_disponiveis=data.dias_disponiveis,
            hora_inicio_disponivel=data.hora_inicio_disponivel,
            hora_fim_disponivel=data.hora_fim_disponivel,
            aceita_hora_extra=data.aceita_hora_extra,
            valor_hora=data.valor_hora,
            valor_diaria=data.valor_diaria,
            valor_hora_extra=data.valor_hora_extra,
            banco=data.banco,
            agencia=data.agencia,
            conta=data.conta,
            tipo_conta=data.tipo_conta,
            pix=data.pix,
            status=DiaristStatus.ATIVO.value,
        )

        created = await self.repository.create(diarist)
        logger.info(f"Diarista criada: {created.id} - {created.nome}")
        return created

    async def get_diarist(self, diarist_id: UUID) -> Diarist | None:
        """Busca diarista por ID."""
        return await self.repository.get_by_id(diarist_id)

    async def list_diarists(
        self,
        skip: int = 0,
        limit: int = 100,
        status: DiaristStatus | None = None,
        tipo: DiaristType | None = None,
        search: str | None = None,
    ) -> list[Diarist]:
        """Lista diaristas com filtros."""
        return await self.repository.list_all(
            skip=skip,
            limit=limit,
            status=status,
            tipo=tipo,
            search=search,
        )

    async def update_diarist(self, diarist_id: UUID, data: DiaristUpdate) -> Diarist | None:
        """Atualiza diarista."""
        diarist = await self.repository.get_by_id(diarist_id)
        if not diarist:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(diarist, field, value)

        updated = await self.repository.update(diarist)
        logger.info(f"Diarista atualizada: {diarist_id}")
        return updated

    async def activate_diarist(self, diarist_id: UUID) -> Diarist | None:
        """Ativa uma diarista."""
        diarist = await self.repository.get_by_id(diarist_id)
        if not diarist:
            return None

        diarist.status = DiaristStatus.ATIVO
        diarist.ativo = True
        updated = await self.repository.update(diarist)
        logger.info(f"Diarista ativada: {diarist_id}")
        return updated

    async def deactivate_diarist(self, diarist_id: UUID) -> Diarist | None:
        """Desativa uma diarista."""
        diarist = await self.repository.get_by_id(diarist_id)
        if not diarist:
            return None

        diarist.status = DiaristStatus.INATIVO
        diarist.ativo = False
        updated = await self.repository.update(diarist)
        logger.info(f"Diarista desativada: {diarist_id}")
        return updated

    async def delete_diarist(self, diarist_id: UUID) -> bool:
        """Remove diarista (soft delete)."""
        return await self.repository.delete(diarist_id)

    # ==================== ASSIGNMENT OPERATIONS ====================

    async def create_assignment(self, data: DiaristAssignmentCreate) -> DiaristAssignment:
        """Cria uma alocação de diarista."""
        diarist = await self.repository.get_by_id(data.diarist_id)
        if not diarist:
            raise ValueError("Diarista não encontrada")

        if diarist.status != DiaristStatus.ATIVO:
            raise ValueError("Diarista não está ativa")

        assignment = DiaristAssignment(
            diarist_id=data.diarist_id,
            unidade_id=data.unidade_id,
            tipo=data.tipo,
            descricao=data.descricao,
            data_inicio=data.data_inicio,
            data_fim=data.data_fim,
            recorrencia=data.recorrencia,
            dias_semana=data.dias_semana,
            hora_inicio=data.hora_inicio,
            hora_fim=data.hora_fim,
            valor_acordado=data.valor_acordado,
            observacoes=data.observacoes,
            status=AssignmentStatus.ATIVO,
        )

        created = await self.repository.create_assignment(assignment)

        # Gerar agendamentos se for recorrente
        if data.recorrencia != RecurrenceType.AVULSO:
            await self._generate_schedules_from_assignment(created)

        logger.info(f"Alocação criada: {created.id}")
        return created

    async def _generate_schedules_from_assignment(
        self,
        assignment: DiaristAssignment,
        until_date: date | None = None,
    ) -> list[DiaristSchedule]:
        """Gera agendamentos a partir de uma alocação recorrente."""
        if not until_date:
            until_date = assignment.data_fim or (date.today() + timedelta(days=90))

        schedules = []
        current_date = assignment.data_inicio

        while current_date <= until_date:
            weekday = Weekday(current_date.strftime("%A").upper())

            if weekday in (assignment.dias_semana or []):
                # Verificar se já não existe agendamento
                existing = [
                    s
                    for s in await self.repository.list_schedules(
                        diarist_id=assignment.diarist_id,
                        data_inicio=current_date,
                        data_fim=current_date,
                    )
                    if s.assignment_id == assignment.id
                ]

                if not existing:
                    schedule = DiaristSchedule(
                        diarist_id=assignment.diarist_id,
                        assignment_id=assignment.id,
                        unidade_id=assignment.unidade_id,
                        data=current_date,
                        hora_inicio=assignment.hora_inicio,
                        hora_fim=assignment.hora_fim,
                        valor_previsto=assignment.valor_acordado,
                        status=ScheduleStatus.AGENDADO,
                    )
                    created = await self.repository.create_schedule(schedule)
                    schedules.append(created)

            # Próxima data baseada na recorrência
            if assignment.recorrencia == RecurrenceType.SEMANAL:
                current_date += timedelta(days=1)
            elif assignment.recorrencia == RecurrenceType.QUINZENAL:
                current_date += timedelta(days=1)
                if len(schedules) > 0 and len(schedules) % len(assignment.dias_semana or [1]) == 0:
                    current_date += timedelta(days=7)
            elif assignment.recorrencia == RecurrenceType.MENSAL:
                current_date += timedelta(days=1)
                if len(schedules) > 0 and len(schedules) % len(assignment.dias_semana or [1]) == 0:
                    current_date += timedelta(days=21)
            else:
                current_date += timedelta(days=1)

        logger.info(f"Gerados {len(schedules)} agendamentos para alocação {assignment.id}")
        return schedules

    async def get_assignment(self, assignment_id: UUID) -> DiaristAssignment | None:
        """Busca alocação por ID."""
        return await self.repository.get_assignment_by_id(assignment_id)

    async def list_assignments(
        self,
        diarist_id: UUID | None = None,
        status: AssignmentStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DiaristAssignment]:
        """Lista alocações."""
        return await self.repository.list_assignments(
            diarist_id=diarist_id,
            status=status,
            skip=skip,
            limit=limit,
        )

    async def cancel_assignment(self, assignment_id: UUID) -> bool:
        """Cancela uma alocação."""
        result = await self.repository.cancel_assignment(assignment_id)
        if result:
            logger.info(f"Alocação cancelada: {assignment_id}")
        return result

    # ==================== SCHEDULE OPERATIONS ====================

    async def create_schedule(self, data: DiaristScheduleCreate) -> DiaristSchedule:
        """Cria um agendamento avulso."""
        # Verificar disponibilidade
        if not await self.repository.check_availability(data.diarist_id, data.data_trabalho):
            raise ValueError("Diarista não disponível nesta data")

        schedule = DiaristSchedule(
            diarist_id=data.diarist_id,
            assignment_id=data.assignment_id,
            condominio_id=data.condominio_id,
            unidade_id=data.unidade_id,
            data_trabalho=data.data_trabalho,
            hora_inicio=data.hora_inicio,
            hora_fim=data.hora_fim,
            valor_previsto=data.valor_previsto,
            tarefas=data.tarefas,
            observacoes=data.observacoes,
            status=ScheduleStatus.AGENDADO,
        )

        created = await self.repository.create_schedule(schedule)
        logger.info(f"Agendamento criado: {created.id}")
        return created

    async def get_schedule(self, schedule_id: UUID) -> DiaristSchedule | None:
        """Busca agendamento por ID."""
        return await self.repository.get_schedule_by_id(schedule_id)

    async def list_schedules(
        self,
        diarist_id: UUID | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        status: ScheduleStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DiaristSchedule]:
        """Lista agendamentos."""
        return await self.repository.list_schedules(
            diarist_id=diarist_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
            skip=skip,
            limit=limit,
        )

    async def get_today_schedules(self) -> list[DiaristSchedule]:
        """Busca agendamentos de hoje."""
        return await self.repository.get_schedules_by_date(date.today(), None)

    async def confirm_schedule(self, schedule_id: UUID) -> DiaristSchedule | None:
        """Confirma um agendamento."""
        schedule = await self.repository.get_schedule_by_id(schedule_id)
        if not schedule or schedule.status != ScheduleStatus.AGENDADO:
            return None

        schedule.status = ScheduleStatus.CONFIRMADO
        updated = await self.repository.update_schedule(schedule)
        logger.info(f"Agendamento confirmado: {schedule_id}")
        return updated

    async def cancel_schedule(self, schedule_id: UUID, motivo: str | None = None) -> DiaristSchedule | None:
        """Cancela um agendamento."""
        schedule = await self.repository.get_schedule_by_id(schedule_id)
        if not schedule:
            return None

        if schedule.status in [
            ScheduleStatus.CONCLUIDO,
            ScheduleStatus.CANCELADO,
        ]:
            raise ValueError("Agendamento não pode ser cancelado")

        schedule.status = ScheduleStatus.CANCELADO
        schedule.observacoes = f"{schedule.observacoes or ''}\nCancelado: {motivo or 'Sem motivo'}"
        updated = await self.repository.update_schedule(schedule)
        logger.info(f"Agendamento cancelado: {schedule_id}")
        return updated

    async def register_checkin(self, data: CheckinRequest) -> DiaristSchedule | None:
        """Registra check-in."""
        schedule = await self.repository.register_checkin(
            schedule_id=data.schedule_id,
            hora_checkin=datetime.utcnow(),
            latitude=data.latitude,
            longitude=data.longitude,
        )

        if schedule:
            logger.info(f"Check-in registrado: {data.schedule_id}")

        return schedule

    async def register_checkout(self, data: CheckoutRequest) -> DiaristSchedule | None:
        """Registra check-out."""
        schedule = await self.repository.register_checkout(
            schedule_id=data.schedule_id,
            hora_checkout=datetime.utcnow(),
            latitude=data.latitude,
            longitude=data.longitude,
        )

        if schedule:
            # Calcular valor final
            horas = schedule.calcular_horas_trabalhadas()
            if horas and schedule.diarist:
                schedule.valor_final = horas * schedule.diarist.valor_hora
                await self.repository.update_schedule(schedule)

            logger.info(f"Check-out registrado: {data.schedule_id}")

        return schedule

    # ==================== PAYMENT OPERATIONS ====================

    async def create_payment(self, data: DiaristPaymentCreate) -> DiaristPayment:
        """Cria um pagamento."""
        diarist = await self.repository.get_by_id(data.diarist_id)
        if not diarist:
            raise ValueError("Diarista não encontrada")

        # Calcular retenções
        valor_bruto = data.valor_bruto
        inss = data.retencao_inss or Decimal("0")
        iss = data.retencao_iss or Decimal("0")
        irrf = data.retencao_irrf or Decimal("0")
        outros = data.outros_descontos or Decimal("0")
        valor_liquido = valor_bruto - inss - iss - irrf - outros

        payment = DiaristPayment(
            diarist_id=data.diarist_id,
            data_referencia=data.data_referencia,
            data_vencimento=data.data_vencimento,
            valor_bruto=valor_bruto,
            retencao_inss=inss,
            retencao_iss=iss,
            retencao_irrf=irrf,
            outros_descontos=outros,
            valor_liquido=valor_liquido,
            forma_pagamento=data.forma_pagamento,
            descricao=data.descricao,
            schedules_ids=data.schedules_ids,
            status=PaymentStatus.PENDENTE,
        )

        created = await self.repository.create_payment(payment)
        logger.info(f"Pagamento criado: {created.id}")
        return created

    async def get_payment(self, payment_id: UUID) -> DiaristPayment | None:
        """Busca pagamento por ID."""
        return await self.repository.get_payment_by_id(payment_id)

    async def list_payments(
        self,
        diarist_id: UUID | None = None,
        status: PaymentStatus | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DiaristPayment]:
        """Lista pagamentos."""
        return await self.repository.list_payments(
            diarist_id=diarist_id,
            status=status,
            data_inicio=data_inicio,
            data_fim=data_fim,
            skip=skip,
            limit=limit,
        )

    async def get_pending_payments(self) -> list[DiaristPayment]:
        """Lista pagamentos pendentes."""
        return await self.repository.get_pending_payments()

    async def process_payment(
        self,
        payment_id: UUID,
        data_pagamento: date,
        comprovante: str | None = None,
    ) -> DiaristPayment | None:
        """Processa pagamento."""
        payment = await self.repository.mark_payment_as_paid(
            payment_id=payment_id,
            data_pagamento=data_pagamento,
            comprovante=comprovante,
        )

        if payment:
            # Atualizar valor total recebido pela diarista
            diarist = await self.repository.get_by_id(payment.diarist_id)
            if diarist:
                diarist.valor_total_recebido = (diarist.valor_total_recebido or Decimal("0")) + payment.valor_liquido
                await self.repository.update(diarist)

            logger.info(f"Pagamento processado: {payment_id}")

        return payment

    async def generate_payment_from_schedules(
        self,
        diarist_id: UUID,
        data_inicio: date,
        data_fim: date,
        forma_pagamento: PaymentMethod = PaymentMethod.PIX,
    ) -> DiaristPayment | None:
        """Gera pagamento a partir de agendamentos concluídos."""
        schedules = await self.repository.list_schedules(
            diarist_id=diarist_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=ScheduleStatus.CONCLUIDO,
        )

        if not schedules:
            return None

        # Calcular valor total
        valor_bruto = sum(s.valor_final or s.valor_previsto or Decimal("0") for s in schedules)

        # Calcular retenções padrão (11% INSS para autônomo)
        inss = valor_bruto * Decimal("0.11")

        payment_data = DiaristPaymentCreate(
            diarist_id=diarist_id,
            data_referencia=data_fim,
            data_vencimento=data_fim + timedelta(days=5),
            valor_bruto=valor_bruto,
            retencao_inss=inss,
            forma_pagamento=forma_pagamento,
            descricao=f"Serviços de {data_inicio} a {data_fim}",
            schedules_ids=[str(s.id) for s in schedules],
        )

        return await self.create_payment(payment_data)

    # ==================== EVALUATION OPERATIONS ====================

    async def create_evaluation(self, data: DiaristEvaluationCreate) -> DiaristEvaluation:
        """Cria uma avaliação."""
        schedule = await self.repository.get_schedule_by_id(data.schedule_id)
        if not schedule:
            raise ValueError("Agendamento não encontrado")

        if schedule.status != ScheduleStatus.CONCLUIDO:
            raise ValueError("Agendamento ainda não foi concluído")

        # Verificar se já existe avaliação
        existing = await self.repository.get_evaluation_by_schedule(data.schedule_id)
        if existing:
            raise ValueError("Agendamento já foi avaliado")

        evaluation = DiaristEvaluation(
            diarist_id=schedule.diarist_id,
            schedule_id=data.schedule_id,
            avaliador_id=data.avaliador_id,
            nota_geral=data.nota_geral,
            nota_pontualidade=data.nota_pontualidade,
            nota_qualidade=data.nota_qualidade,
            nota_comportamento=data.nota_comportamento,
            nota_comunicacao=data.nota_comunicacao,
            comentario=data.comentario,
            recomendaria=data.recomendaria,
        )

        created = await self.repository.create_evaluation(evaluation)
        logger.info(f"Avaliação criada: {created.id}")
        return created

    async def get_evaluation(self, evaluation_id: UUID) -> DiaristEvaluation | None:
        """Busca avaliação por ID."""
        return await self.repository.get_evaluation_by_id(evaluation_id)

    async def list_evaluations(
        self,
        diarist_id: UUID | None = None,
        nota_minima: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DiaristEvaluation]:
        """Lista avaliações."""
        return await self.repository.list_evaluations(
            diarist_id=diarist_id,
            nota_minima=nota_minima,
            skip=skip,
            limit=limit,
        )

    # ==================== METRICS ====================

    async def get_diarist_metrics(
        self,
        diarist_id: UUID,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> dict:
        """Retorna métricas da diarista."""
        return await self.repository.get_diarist_metrics(
            diarist_id=diarist_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

    async def get_condominio_statistics(
        self,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> dict:
        """Retorna estatísticas do condomínio."""
        return await self.repository.get_condominio_statistics(
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

    async def get_top_diarists(
        self,
        limit: int = 10,
    ) -> list[dict]:
        """Retorna ranking das melhores diaristas."""
        return await self.repository.get_top_diarists(
            limit=limit,
        )

    async def get_available_diarists(
        self,
        data: date,
        tipo: DiaristType | None = None,
    ) -> list[Diarist]:
        """Busca diaristas disponíveis."""
        return await self.repository.get_available_diarists(
            data=data,
            tipo=tipo,
        )

    # ==================== BATCH SCHEDULE ====================

    async def create_batch_schedules(self, data: BatchScheduleCreate) -> dict:
        """Cria agendamentos em lote para uma data (escala diaria)."""
        from datetime import time as dt_time

        created = []
        errors = []

        for item in data.items:
            try:
                diarist = await self.repository.get_by_id(item.diarist_id)
                if not diarist:
                    errors.append(f"Diarista {item.diarist_id} nao encontrada")
                    continue

                if diarist.status != DiaristStatus.ATIVO.value:
                    errors.append(f"{diarist.nome}: nao esta ativa")
                    continue

                # Verificar disponibilidade
                available = await self.repository.check_availability(item.diarist_id, data.data)
                if not available:
                    errors.append(f"{diarist.nome}: indisponivel na data {data.data}")
                    continue

                # Parsear horarios
                h_ini_parts = item.horario_inicio.split(":")
                h_fim_parts = item.horario_fim.split(":")
                horario_inicio = dt_time(int(h_ini_parts[0]), int(h_ini_parts[1]))
                horario_fim = dt_time(int(h_fim_parts[0]), int(h_fim_parts[1]))

                schedule = DiaristSchedule(
                    condominio_id=data.condominio_id,
                    diarist_id=item.diarist_id,
                    data_trabalho=data.data,
                    hora_inicio=horario_inicio,
                    hora_fim=horario_fim,
                    valor_previsto=diarist.valor_diaria,
                    observacoes=item.observacoes,
                    status="AGENDADO",
                )

                created_schedule = await self.repository.create_schedule(schedule)
                created.append(created_schedule)
                logger.info(f"Escala criada: {diarist.nome} em {data.data}")

            except Exception as e:
                errors.append(f"Erro ao criar escala para {item.diarist_id}: {str(e)}")
                logger.error(f"Erro batch schedule: {e}")

        return {
            "total_criados": len(created),
            "total_erros": len(errors),
            "erros": errors,
            "schedules": created,
        }

    # ==================== PAYROLL (FECHAMENTO DE FOLHA) ====================

    async def generate_payroll_report(self, competencia: str, condominio_id: UUID | None = None) -> dict:
        """Gera relatorio de fechamento de folha para uma competencia (YYYY-MM)."""
        from calendar import monthrange

        year, month = int(competencia[:4]), int(competencia[5:7])
        periodo_inicio = date(year, month, 1)
        ultimo_dia = monthrange(year, month)[1]
        periodo_fim = date(year, month, ultimo_dia)

        # Buscar todos os schedules CONCLUIDOS no periodo
        # Nota: banco usa ENUM PostgreSQL com valores uppercase
        schedules = await self.repository.list_schedules(
            condominio_id=condominio_id,
            data_inicio=periodo_inicio,
            data_fim=periodo_fim,
            status="CONCLUIDO",
            limit=5000,
        )

        # Agrupar por diarista
        diarist_map: dict[UUID, dict] = {}
        for s in schedules:
            did = s.diarist_id
            if did not in diarist_map:
                diarist = await self.repository.get_by_id(did)
                if not diarist:
                    continue
                diarist_map[did] = {
                    "diarist_id": str(did),
                    "diarist_nome": diarist.nome,
                    "cpf": diarist.cpf,
                    "valor_diaria": diarist.valor_diaria or Decimal("0"),
                    "pix": diarist.pix,
                    "banco": diarist.banco,
                    "agencia": diarist.agencia,
                    "conta": diarist.conta,
                    "quantidade_diarias": 0,
                    "total_horas": Decimal("0"),
                    "valor_bruto": Decimal("0"),
                }

            entry = diarist_map[did]
            entry["quantidade_diarias"] += 1
            entry["total_horas"] += Decimal("8")  # carga padrao
            valor = s.valor_final or s.valor_previsto or entry["valor_diaria"]
            entry["valor_bruto"] += valor

        # Calcular retencoes e montar items
        items = []
        total_bruto = Decimal("0")
        total_inss = Decimal("0")
        total_liquido = Decimal("0")
        total_diarias = 0

        for entry in diarist_map.values():
            bruto = entry["valor_bruto"]
            inss = bruto * Decimal("0.11")  # 11% INSS autonomo
            liquido = bruto - inss

            total_bruto += bruto
            total_inss += inss
            total_liquido += liquido
            total_diarias += entry["quantidade_diarias"]

            items.append(
                {
                    "diarist_id": entry["diarist_id"],
                    "diarist_nome": entry["diarist_nome"],
                    "cpf": entry["cpf"],
                    "quantidade_diarias": entry["quantidade_diarias"],
                    "total_horas": entry["total_horas"],
                    "valor_diaria": entry["valor_diaria"],
                    "valor_bruto": bruto,
                    "inss_retido": round(inss, 2),
                    "valor_liquido": round(liquido, 2),
                    "pix": entry["pix"],
                    "banco": entry["banco"],
                    "agencia": entry["agencia"],
                    "conta": entry["conta"],
                }
            )

        # Ordenar por nome
        items.sort(key=lambda x: x["diarist_nome"])

        return {
            "competencia": competencia,
            "periodo_inicio": periodo_inicio,
            "periodo_fim": periodo_fim,
            "total_diaristas": len(items),
            "total_diarias": total_diarias,
            "valor_bruto_total": round(total_bruto, 2),
            "inss_total": round(total_inss, 2),
            "valor_liquido_total": round(total_liquido, 2),
            "items": items,
        }

    async def generate_payroll_payments(self, data: PayrollGenerateRequest) -> dict:
        """Gera pagamentos em lote a partir do relatorio de folha."""
        report = await self.generate_payroll_report(
            competencia=data.competencia,
            condominio_id=data.condominio_id,
        )

        created = []
        errors = []

        for item in report["items"]:
            # Filtro opcional por diarist_ids
            if data.diarist_ids and UUID(item["diarist_id"]) not in data.diarist_ids:
                continue

            try:
                payment = DiaristPayment(
                    condominio_id=data.condominio_id,
                    diarist_id=UUID(item["diarist_id"]),
                    data_referencia=report["periodo_fim"],
                    data_vencimento=report["periodo_fim"] + timedelta(days=5),
                    valor_bruto=item["valor_bruto"],
                    retencao_inss=item["inss_retido"],
                    valor_liquido=item["valor_liquido"],
                    forma_pagamento=data.forma_pagamento or "pix",
                    descricao=f"Folha {data.competencia} - {item['quantidade_diarias']} diarias",
                    status=PaymentStatus.PENDENTE.value,
                )

                created_payment = await self.repository.create_payment(payment)
                created.append(created_payment)
                logger.info(f"Pagamento gerado: {item['diarist_nome']} - R$ {item['valor_liquido']}")

            except Exception as e:
                errors.append(f"Erro ao gerar pagamento para {item['diarist_nome']}: {str(e)}")
                logger.error(f"Erro payroll payment: {e}")

        return {
            "competencia": data.competencia,
            "total_gerados": len(created),
            "total_erros": len(errors),
            "erros": errors,
            "payments": created,
        }
