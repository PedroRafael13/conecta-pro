"""Service para operações de Diaristas."""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from modules.operacional.diaristas.models.diarist import (
    Diarist,
    DiaristAssignment,
    DiaristEvaluation,
    DiaristPayment,
    DiaristSchedule,
    DiaristStatus,
    DiaristType,
    AssignmentStatus,
    RecurrenceType,
    ScheduleStatus,
    PaymentStatus,
    PaymentMethod,
    Weekday,
)
from modules.operacional.diaristas.repositories.diarist_repository import DiaristRepository
from modules.operacional.diaristas.schemas.diarist_schemas import (
    DiaristCreate,
    DiaristUpdate,
    DiaristAssignmentCreate,
    DiaristScheduleCreate,
    DiaristPaymentCreate,
    DiaristEvaluationCreate,
    CheckinRequest,
    CheckoutRequest,
)

logger = logging.getLogger(__name__)


class DiaristService:
    """Service para gerenciamento de diaristas."""

    def __init__(self, db: Session):
        """Inicializa o service."""
        self.db = db
        self.repository = DiaristRepository(db)

    # ==================== DIARIST OPERATIONS ====================

    def create_diarist(self, data: DiaristCreate) -> Diarist:
        """Cria uma nova diarista."""
        # Verificar duplicidade
        if self.repository.get_by_cpf(data.cpf):
            raise ValueError(f"CPF {data.cpf} já cadastrado")

        if data.email and self.repository.get_by_email(data.email):
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
            status=DiaristStatus.PENDENTE,
        )

        created = self.repository.create(diarist)
        logger.info(f"Diarista criada: {created.id} - {created.nome}")
        return created

    def get_diarist(self, diarist_id: UUID) -> Optional[Diarist]:
        """Busca diarista por ID."""
        return self.repository.get_by_id(diarist_id)

    def list_diarists(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[DiaristStatus] = None,
        tipo: Optional[DiaristType] = None,
        search: Optional[str] = None,
        condominio_id: Optional[UUID] = None,
    ) -> list[Diarist]:
        """Lista diaristas com filtros."""
        return self.repository.list_all(
            skip=skip,
            limit=limit,
            status=status,
            tipo=tipo,
            search=search,
            condominio_id=condominio_id,
        )

    def update_diarist(
        self, diarist_id: UUID, data: DiaristUpdate
    ) -> Optional[Diarist]:
        """Atualiza diarista."""
        diarist = self.repository.get_by_id(diarist_id)
        if not diarist:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(diarist, field, value)

        updated = self.repository.update(diarist)
        logger.info(f"Diarista atualizada: {diarist_id}")
        return updated

    def activate_diarist(self, diarist_id: UUID) -> Optional[Diarist]:
        """Ativa uma diarista."""
        diarist = self.repository.get_by_id(diarist_id)
        if not diarist:
            return None

        diarist.status = DiaristStatus.ATIVO
        diarist.ativo = True
        updated = self.repository.update(diarist)
        logger.info(f"Diarista ativada: {diarist_id}")
        return updated

    def deactivate_diarist(self, diarist_id: UUID) -> Optional[Diarist]:
        """Desativa uma diarista."""
        diarist = self.repository.get_by_id(diarist_id)
        if not diarist:
            return None

        diarist.status = DiaristStatus.INATIVO
        diarist.ativo = False
        updated = self.repository.update(diarist)
        logger.info(f"Diarista desativada: {diarist_id}")
        return updated

    def delete_diarist(self, diarist_id: UUID) -> bool:
        """Remove diarista (soft delete)."""
        return self.repository.delete(diarist_id)

    # ==================== ASSIGNMENT OPERATIONS ====================

    def create_assignment(
        self, data: DiaristAssignmentCreate
    ) -> DiaristAssignment:
        """Cria uma alocação de diarista."""
        diarist = self.repository.get_by_id(data.diarist_id)
        if not diarist:
            raise ValueError("Diarista não encontrada")

        if diarist.status != DiaristStatus.ATIVO:
            raise ValueError("Diarista não está ativa")

        assignment = DiaristAssignment(
            diarist_id=data.diarist_id,
            condominio_id=data.condominio_id,
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

        created = self.repository.create_assignment(assignment)

        # Gerar agendamentos se for recorrente
        if data.recorrencia != RecurrenceType.AVULSO:
            self._generate_schedules_from_assignment(created)

        logger.info(f"Alocação criada: {created.id}")
        return created

    def _generate_schedules_from_assignment(
        self,
        assignment: DiaristAssignment,
        until_date: Optional[date] = None,
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
                    s for s in self.repository.list_schedules(
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
                        condominio_id=assignment.condominio_id,
                        unidade_id=assignment.unidade_id,
                        data_trabalho=current_date,
                        hora_inicio=assignment.hora_inicio,
                        hora_fim=assignment.hora_fim,
                        valor_previsto=assignment.valor_acordado,
                        status=ScheduleStatus.AGENDADO,
                    )
                    created = self.repository.create_schedule(schedule)
                    schedules.append(created)

            # Próxima data baseada na recorrência
            if assignment.recorrencia == RecurrenceType.SEMANAL:
                current_date += timedelta(days=1)
            elif assignment.recorrencia == RecurrenceType.QUINZENAL:
                current_date += timedelta(days=1)
                if len(schedules) > 0 and len(schedules) % len(
                    assignment.dias_semana or [1]
                ) == 0:
                    current_date += timedelta(days=7)
            elif assignment.recorrencia == RecurrenceType.MENSAL:
                current_date += timedelta(days=1)
                if len(schedules) > 0 and len(schedules) % len(
                    assignment.dias_semana or [1]
                ) == 0:
                    current_date += timedelta(days=21)
            else:
                current_date += timedelta(days=1)

        logger.info(
            f"Gerados {len(schedules)} agendamentos para alocação {assignment.id}"
        )
        return schedules

    def get_assignment(self, assignment_id: UUID) -> Optional[DiaristAssignment]:
        """Busca alocação por ID."""
        return self.repository.get_assignment_by_id(assignment_id)

    def list_assignments(
        self,
        diarist_id: Optional[UUID] = None,
        condominio_id: Optional[UUID] = None,
        status: Optional[AssignmentStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DiaristAssignment]:
        """Lista alocações."""
        return self.repository.list_assignments(
            diarist_id=diarist_id,
            condominio_id=condominio_id,
            status=status,
            skip=skip,
            limit=limit,
        )

    def cancel_assignment(self, assignment_id: UUID) -> bool:
        """Cancela uma alocação."""
        result = self.repository.cancel_assignment(assignment_id)
        if result:
            logger.info(f"Alocação cancelada: {assignment_id}")
        return result

    # ==================== SCHEDULE OPERATIONS ====================

    def create_schedule(self, data: DiaristScheduleCreate) -> DiaristSchedule:
        """Cria um agendamento avulso."""
        # Verificar disponibilidade
        if not self.repository.check_availability(data.diarist_id, data.data_trabalho):
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

        created = self.repository.create_schedule(schedule)
        logger.info(f"Agendamento criado: {created.id}")
        return created

    def get_schedule(self, schedule_id: UUID) -> Optional[DiaristSchedule]:
        """Busca agendamento por ID."""
        return self.repository.get_schedule_by_id(schedule_id)

    def list_schedules(
        self,
        diarist_id: Optional[UUID] = None,
        condominio_id: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        status: Optional[ScheduleStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DiaristSchedule]:
        """Lista agendamentos."""
        return self.repository.list_schedules(
            diarist_id=diarist_id,
            condominio_id=condominio_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
            skip=skip,
            limit=limit,
        )

    def get_today_schedules(
        self, condominio_id: Optional[UUID] = None
    ) -> list[DiaristSchedule]:
        """Busca agendamentos de hoje."""
        return self.repository.get_schedules_by_date(date.today(), condominio_id)

    def confirm_schedule(self, schedule_id: UUID) -> Optional[DiaristSchedule]:
        """Confirma um agendamento."""
        schedule = self.repository.get_schedule_by_id(schedule_id)
        if not schedule or schedule.status != ScheduleStatus.AGENDADO:
            return None

        schedule.status = ScheduleStatus.CONFIRMADO
        updated = self.repository.update_schedule(schedule)
        logger.info(f"Agendamento confirmado: {schedule_id}")
        return updated

    def cancel_schedule(
        self, schedule_id: UUID, motivo: Optional[str] = None
    ) -> Optional[DiaristSchedule]:
        """Cancela um agendamento."""
        schedule = self.repository.get_schedule_by_id(schedule_id)
        if not schedule:
            return None

        if schedule.status in [
            ScheduleStatus.CONCLUIDO,
            ScheduleStatus.CANCELADO,
        ]:
            raise ValueError("Agendamento não pode ser cancelado")

        schedule.status = ScheduleStatus.CANCELADO
        schedule.observacoes = f"{schedule.observacoes or ''}\nCancelado: {motivo or 'Sem motivo'}"
        updated = self.repository.update_schedule(schedule)
        logger.info(f"Agendamento cancelado: {schedule_id}")
        return updated

    def register_checkin(self, data: CheckinRequest) -> Optional[DiaristSchedule]:
        """Registra check-in."""
        schedule = self.repository.register_checkin(
            schedule_id=data.schedule_id,
            hora_checkin=data.hora_checkin,
            latitude=data.latitude,
            longitude=data.longitude,
        )

        if schedule:
            logger.info(f"Check-in registrado: {data.schedule_id}")

        return schedule

    def register_checkout(self, data: CheckoutRequest) -> Optional[DiaristSchedule]:
        """Registra check-out."""
        schedule = self.repository.register_checkout(
            schedule_id=data.schedule_id,
            hora_checkout=data.hora_checkout,
            latitude=data.latitude,
            longitude=data.longitude,
        )

        if schedule:
            # Calcular valor final
            horas = schedule.calcular_horas_trabalhadas()
            if horas and schedule.diarist:
                schedule.valor_final = horas * schedule.diarist.valor_hora
                self.repository.update_schedule(schedule)

            logger.info(f"Check-out registrado: {data.schedule_id}")

        return schedule

    # ==================== PAYMENT OPERATIONS ====================

    def create_payment(self, data: DiaristPaymentCreate) -> DiaristPayment:
        """Cria um pagamento."""
        diarist = self.repository.get_by_id(data.diarist_id)
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
            condominio_id=data.condominio_id,
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

        created = self.repository.create_payment(payment)
        logger.info(f"Pagamento criado: {created.id}")
        return created

    def get_payment(self, payment_id: UUID) -> Optional[DiaristPayment]:
        """Busca pagamento por ID."""
        return self.repository.get_payment_by_id(payment_id)

    def list_payments(
        self,
        diarist_id: Optional[UUID] = None,
        condominio_id: Optional[UUID] = None,
        status: Optional[PaymentStatus] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DiaristPayment]:
        """Lista pagamentos."""
        return self.repository.list_payments(
            diarist_id=diarist_id,
            condominio_id=condominio_id,
            status=status,
            data_inicio=data_inicio,
            data_fim=data_fim,
            skip=skip,
            limit=limit,
        )

    def get_pending_payments(
        self, condominio_id: Optional[UUID] = None
    ) -> list[DiaristPayment]:
        """Lista pagamentos pendentes."""
        return self.repository.get_pending_payments(condominio_id)

    def process_payment(
        self,
        payment_id: UUID,
        data_pagamento: date,
        comprovante: Optional[str] = None,
    ) -> Optional[DiaristPayment]:
        """Processa pagamento."""
        payment = self.repository.mark_payment_as_paid(
            payment_id=payment_id,
            data_pagamento=data_pagamento,
            comprovante=comprovante,
        )

        if payment:
            # Atualizar valor total recebido pela diarista
            diarist = self.repository.get_by_id(payment.diarist_id)
            if diarist:
                diarist.valor_total_recebido = (
                    diarist.valor_total_recebido or Decimal("0")
                ) + payment.valor_liquido
                self.repository.update(diarist)

            logger.info(f"Pagamento processado: {payment_id}")

        return payment

    def generate_payment_from_schedules(
        self,
        diarist_id: UUID,
        condominio_id: UUID,
        data_inicio: date,
        data_fim: date,
        forma_pagamento: PaymentMethod = PaymentMethod.PIX,
    ) -> Optional[DiaristPayment]:
        """Gera pagamento a partir de agendamentos concluídos."""
        schedules = self.repository.list_schedules(
            diarist_id=diarist_id,
            condominio_id=condominio_id,
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
            condominio_id=condominio_id,
            data_referencia=data_fim,
            data_vencimento=data_fim + timedelta(days=5),
            valor_bruto=valor_bruto,
            retencao_inss=inss,
            forma_pagamento=forma_pagamento,
            descricao=f"Serviços de {data_inicio} a {data_fim}",
            schedules_ids=[str(s.id) for s in schedules],
        )

        return self.create_payment(payment_data)

    # ==================== EVALUATION OPERATIONS ====================

    def create_evaluation(
        self, data: DiaristEvaluationCreate
    ) -> DiaristEvaluation:
        """Cria uma avaliação."""
        schedule = self.repository.get_schedule_by_id(data.schedule_id)
        if not schedule:
            raise ValueError("Agendamento não encontrado")

        if schedule.status != ScheduleStatus.CONCLUIDO:
            raise ValueError("Agendamento ainda não foi concluído")

        # Verificar se já existe avaliação
        existing = self.repository.get_evaluation_by_schedule(data.schedule_id)
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

        created = self.repository.create_evaluation(evaluation)
        logger.info(f"Avaliação criada: {created.id}")
        return created

    def get_evaluation(self, evaluation_id: UUID) -> Optional[DiaristEvaluation]:
        """Busca avaliação por ID."""
        return self.repository.get_evaluation_by_id(evaluation_id)

    def list_evaluations(
        self,
        diarist_id: Optional[UUID] = None,
        nota_minima: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DiaristEvaluation]:
        """Lista avaliações."""
        return self.repository.list_evaluations(
            diarist_id=diarist_id,
            nota_minima=nota_minima,
            skip=skip,
            limit=limit,
        )

    # ==================== METRICS ====================

    def get_diarist_metrics(
        self,
        diarist_id: UUID,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> dict:
        """Retorna métricas da diarista."""
        return self.repository.get_diarist_metrics(
            diarist_id=diarist_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

    def get_condominio_statistics(
        self,
        condominio_id: UUID,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> dict:
        """Retorna estatísticas do condomínio."""
        return self.repository.get_condominio_statistics(
            condominio_id=condominio_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

    def get_top_diarists(
        self,
        condominio_id: Optional[UUID] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Retorna ranking das melhores diaristas."""
        return self.repository.get_top_diarists(
            condominio_id=condominio_id,
            limit=limit,
        )

    def get_available_diarists(
        self,
        data: date,
        tipo: Optional[DiaristType] = None,
        condominio_id: Optional[UUID] = None,
    ) -> list[Diarist]:
        """Busca diaristas disponíveis."""
        return self.repository.get_available_diarists(
            data=data,
            tipo=tipo,
            condominio_id=condominio_id,
        )
