"""Repository para gerenciamento de Diaristas."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from modules.operacional.diaristas.models.diarist import (
    AssignmentStatus,
    Diarist,
    DiaristAssignment,
    DiaristEvaluation,
    DiaristPayment,
    DiaristSchedule,
    DiaristStatus,
    DiaristType,
    PaymentStatus,
    ScheduleStatus,
    Weekday,
)


class DiaristRepository:
    """Repository para operações de Diarista."""

    def __init__(self, db: AsyncSession):
        """Inicializa o repository."""
        self.db = db

    # ==================== DIARIST CRUD ====================

    async def create(self, diarist: Diarist) -> Diarist:
        """Cria uma nova diarista."""
        self.db.add(diarist)
        await self.db.commit()
        await self.db.refresh(diarist)
        return diarist

    async def get_by_id(self, diarist_id: UUID) -> Diarist | None:
        """Busca diarista por ID."""
        result = await self.db.execute(
            select(Diarist)
            .options(
                joinedload(Diarist.assignments),
                joinedload(Diarist.schedules),
                joinedload(Diarist.payments),
                joinedload(Diarist.evaluations),
            )
            .where(Diarist.id == diarist_id)
        )
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> Diarist | None:
        """Busca diarista por CPF."""
        result = await self.db.execute(select(Diarist).where(Diarist.cpf == cpf))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Diarist | None:
        """Busca diarista por email."""
        result = await self.db.execute(select(Diarist).where(Diarist.email == email))
        return result.scalar_one_or_none()

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: DiaristStatus | None = None,
        tipo: DiaristType | None = None,
        search: str | None = None,
        condominio_id: UUID | None = None,
    ) -> list[Diarist]:
        """Lista diaristas com filtros."""
        query = select(Diarist)

        if status:
            query = query.where(Diarist.status == status)

        if tipo:
            query = query.where(Diarist.tipos_servico.contains([tipo]))

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Diarist.nome.ilike(search_term),
                    Diarist.cpf.ilike(search_term),
                    Diarist.email.ilike(search_term),
                )
            )

        if condominio_id:
            query = query.join(Diarist.assignments).where(
                DiaristAssignment.condominio_id == condominio_id,
                DiaristAssignment.status == AssignmentStatus.ATIVO,
            )

        query = query.order_by(Diarist.nome).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        status: DiaristStatus | None = None,
        tipo: DiaristType | None = None,
    ) -> int:
        """Conta diaristas com filtros."""
        query = select(func.count(Diarist.id))

        if status:
            query = query.where(Diarist.status == status)

        if tipo:
            query = query.where(Diarist.tipos_servico.contains([tipo]))

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update(self, diarist: Diarist) -> Diarist:
        """Atualiza diarista."""
        await self.db.commit()
        await self.db.refresh(diarist)
        return diarist

    async def delete(self, diarist_id: UUID) -> bool:
        """Remove diarista (soft delete)."""
        diarist = await self.get_by_id(diarist_id)
        if diarist:
            diarist.ativo = False
            diarist.status = DiaristStatus.INATIVO
            await self.db.commit()
            return True
        return False

    # ==================== DISPONIBILIDADE ====================

    def get_available_diarists(
        self,
        data: date,
        tipo: DiaristType | None = None,
        condominio_id: UUID | None = None,
    ) -> list[Diarist]:
        """Busca diaristas disponíveis em uma data."""
        weekday = Weekday(data.strftime("%A").upper())

        query = self.db.query(Diarist).filter(
            Diarist.status == DiaristStatus.ATIVO,
            Diarist.ativo.is_(True),
            Diarist.dias_disponiveis.contains([weekday]),
        )

        if tipo:
            query = query.filter(Diarist.tipos_servico.contains([tipo]))

        # Excluir diaristas já alocadas nesta data
        subquery = self.db.query(DiaristSchedule.diarist_id).filter(
            DiaristSchedule.data_trabalho == data,
            DiaristSchedule.status.in_(
                [
                    ScheduleStatus.AGENDADO,
                    ScheduleStatus.CONFIRMADO,
                    ScheduleStatus.EM_ANDAMENTO,
                ]
            ),
        )

        query = query.filter(~Diarist.id.in_(subquery))

        if condominio_id:
            # Priorizar diaristas que já trabalham no condomínio
            query = query.outerjoin(
                DiaristAssignment,
                and_(
                    DiaristAssignment.diarist_id == Diarist.id,
                    DiaristAssignment.condominio_id == condominio_id,
                    DiaristAssignment.status == AssignmentStatus.ATIVO,
                ),
            ).order_by(
                DiaristAssignment.id.desc().nullslast(),
                Diarist.avaliacao_media.desc(),
            )
        else:
            query = query.order_by(Diarist.avaliacao_media.desc())

        return query.all()

    def check_availability(
        self,
        diarist_id: UUID,
        data: date,
    ) -> bool:
        """Verifica se diarista está disponível em uma data."""
        diarist = self.get_by_id(diarist_id)
        if not diarist or diarist.status != DiaristStatus.ATIVO:
            return False

        weekday = Weekday(data.strftime("%A").upper())
        if weekday not in (diarist.dias_disponiveis or []):
            return False

        # Verificar se já tem agendamento
        existing = (
            self.db.query(DiaristSchedule)
            .filter(
                DiaristSchedule.diarist_id == diarist_id,
                DiaristSchedule.data_trabalho == data,
                DiaristSchedule.status.in_(
                    [
                        ScheduleStatus.AGENDADO,
                        ScheduleStatus.CONFIRMADO,
                        ScheduleStatus.EM_ANDAMENTO,
                    ]
                ),
            )
            .first()
        )

        return existing is None

    # ==================== ASSIGNMENT CRUD ====================

    def create_assignment(self, assignment: DiaristAssignment) -> DiaristAssignment:
        """Cria uma alocação."""
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def get_assignment_by_id(self, assignment_id: UUID) -> DiaristAssignment | None:
        """Busca alocação por ID."""
        return (
            self.db.query(DiaristAssignment)
            .options(joinedload(DiaristAssignment.diarist))
            .filter(DiaristAssignment.id == assignment_id)
            .first()
        )

    def list_assignments(
        self,
        diarist_id: UUID | None = None,
        condominio_id: UUID | None = None,
        status: AssignmentStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DiaristAssignment]:
        """Lista alocações com filtros."""
        query = self.db.query(DiaristAssignment).options(joinedload(DiaristAssignment.diarist))

        if diarist_id:
            query = query.filter(DiaristAssignment.diarist_id == diarist_id)

        if condominio_id:
            query = query.filter(DiaristAssignment.condominio_id == condominio_id)

        if status:
            query = query.filter(DiaristAssignment.status == status)

        return query.order_by(DiaristAssignment.created_at.desc()).offset(skip).limit(limit).all()

    def update_assignment(self, assignment: DiaristAssignment) -> DiaristAssignment:
        """Atualiza alocação."""
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def cancel_assignment(self, assignment_id: UUID) -> bool:
        """Cancela uma alocação."""
        assignment = self.get_assignment_by_id(assignment_id)
        if assignment:
            assignment.status = AssignmentStatus.CANCELADO
            self.db.commit()
            return True
        return False

    # ==================== SCHEDULE CRUD ====================

    def create_schedule(self, schedule: DiaristSchedule) -> DiaristSchedule:
        """Cria um agendamento."""
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def get_schedule_by_id(self, schedule_id: UUID) -> DiaristSchedule | None:
        """Busca agendamento por ID."""
        return (
            self.db.query(DiaristSchedule)
            .options(
                joinedload(DiaristSchedule.diarist),
                joinedload(DiaristSchedule.assignment),
            )
            .filter(DiaristSchedule.id == schedule_id)
            .first()
        )

    def list_schedules(
        self,
        diarist_id: UUID | None = None,
        condominio_id: UUID | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        status: ScheduleStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DiaristSchedule]:
        """Lista agendamentos com filtros."""
        query = self.db.query(DiaristSchedule).options(joinedload(DiaristSchedule.diarist))

        if diarist_id:
            query = query.filter(DiaristSchedule.diarist_id == diarist_id)

        if condominio_id:
            query = query.filter(DiaristSchedule.condominio_id == condominio_id)

        if data_inicio:
            query = query.filter(DiaristSchedule.data_trabalho >= data_inicio)

        if data_fim:
            query = query.filter(DiaristSchedule.data_trabalho <= data_fim)

        if status:
            query = query.filter(DiaristSchedule.status == status)

        return query.order_by(DiaristSchedule.data_trabalho.desc()).offset(skip).limit(limit).all()

    def get_schedules_by_date(
        self,
        data: date,
        condominio_id: UUID | None = None,
    ) -> list[DiaristSchedule]:
        """Busca agendamentos de uma data específica."""
        query = (
            self.db.query(DiaristSchedule)
            .options(joinedload(DiaristSchedule.diarist))
            .filter(DiaristSchedule.data_trabalho == data)
        )

        if condominio_id:
            query = query.filter(DiaristSchedule.condominio_id == condominio_id)

        return query.order_by(DiaristSchedule.hora_inicio).all()

    def update_schedule(self, schedule: DiaristSchedule) -> DiaristSchedule:
        """Atualiza agendamento."""
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def register_checkin(
        self,
        schedule_id: UUID,
        hora_checkin: datetime,
        latitude: Decimal | None = None,
        longitude: Decimal | None = None,
    ) -> DiaristSchedule | None:
        """Registra check-in."""
        schedule = self.get_schedule_by_id(schedule_id)
        if schedule and schedule.status in [
            ScheduleStatus.AGENDADO,
            ScheduleStatus.CONFIRMADO,
        ]:
            schedule.checkin_real = hora_checkin
            schedule.checkin_latitude = latitude
            schedule.checkin_longitude = longitude
            schedule.status = ScheduleStatus.EM_ANDAMENTO
            self.db.commit()
            self.db.refresh(schedule)
            return schedule
        return None

    def register_checkout(
        self,
        schedule_id: UUID,
        hora_checkout: datetime,
        latitude: Decimal | None = None,
        longitude: Decimal | None = None,
    ) -> DiaristSchedule | None:
        """Registra check-out."""
        schedule = self.get_schedule_by_id(schedule_id)
        if schedule and schedule.status == ScheduleStatus.EM_ANDAMENTO:
            schedule.checkout_real = hora_checkout
            schedule.checkout_latitude = latitude
            schedule.checkout_longitude = longitude
            schedule.status = ScheduleStatus.CONCLUIDO
            self.db.commit()
            self.db.refresh(schedule)
            return schedule
        return None

    # ==================== PAYMENT CRUD ====================

    def create_payment(self, payment: DiaristPayment) -> DiaristPayment:
        """Cria um pagamento."""
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payment_by_id(self, payment_id: UUID) -> DiaristPayment | None:
        """Busca pagamento por ID."""
        return (
            self.db.query(DiaristPayment)
            .options(joinedload(DiaristPayment.diarist))
            .filter(DiaristPayment.id == payment_id)
            .first()
        )

    def list_payments(
        self,
        diarist_id: UUID | None = None,
        condominio_id: UUID | None = None,
        status: PaymentStatus | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DiaristPayment]:
        """Lista pagamentos com filtros."""
        query = self.db.query(DiaristPayment).options(joinedload(DiaristPayment.diarist))

        if diarist_id:
            query = query.filter(DiaristPayment.diarist_id == diarist_id)

        if condominio_id:
            query = query.filter(DiaristPayment.condominio_id == condominio_id)

        if status:
            query = query.filter(DiaristPayment.status == status)

        if data_inicio:
            query = query.filter(DiaristPayment.data_referencia >= data_inicio)

        if data_fim:
            query = query.filter(DiaristPayment.data_referencia <= data_fim)

        return query.order_by(DiaristPayment.data_referencia.desc()).offset(skip).limit(limit).all()

    def get_pending_payments(
        self,
        condominio_id: UUID | None = None,
    ) -> list[DiaristPayment]:
        """Busca pagamentos pendentes."""
        query = (
            self.db.query(DiaristPayment)
            .options(joinedload(DiaristPayment.diarist))
            .filter(DiaristPayment.status == PaymentStatus.PENDENTE)
        )

        if condominio_id:
            query = query.filter(DiaristPayment.condominio_id == condominio_id)

        return query.order_by(DiaristPayment.data_vencimento).all()

    def update_payment(self, payment: DiaristPayment) -> DiaristPayment:
        """Atualiza pagamento."""
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def mark_payment_as_paid(
        self,
        payment_id: UUID,
        data_pagamento: date,
        comprovante: str | None = None,
    ) -> DiaristPayment | None:
        """Marca pagamento como pago."""
        payment = self.get_payment_by_id(payment_id)
        if payment and payment.status == PaymentStatus.PENDENTE:
            payment.status = PaymentStatus.PAGO
            payment.data_pagamento = data_pagamento
            payment.comprovante_url = comprovante
            self.db.commit()
            self.db.refresh(payment)
            return payment
        return None

    # ==================== EVALUATION CRUD ====================

    def create_evaluation(self, evaluation: DiaristEvaluation) -> DiaristEvaluation:
        """Cria uma avaliação."""
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)

        # Atualizar média da diarista
        self._update_diarist_rating(evaluation.diarist_id)

        return evaluation

    def get_evaluation_by_id(self, evaluation_id: UUID) -> DiaristEvaluation | None:
        """Busca avaliação por ID."""
        return self.db.query(DiaristEvaluation).filter(DiaristEvaluation.id == evaluation_id).first()

    def list_evaluations(
        self,
        diarist_id: UUID | None = None,
        schedule_id: UUID | None = None,
        nota_minima: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DiaristEvaluation]:
        """Lista avaliações com filtros."""
        query = self.db.query(DiaristEvaluation)

        if diarist_id:
            query = query.filter(DiaristEvaluation.diarist_id == diarist_id)

        if schedule_id:
            query = query.filter(DiaristEvaluation.schedule_id == schedule_id)

        if nota_minima:
            query = query.filter(DiaristEvaluation.nota_geral >= nota_minima)

        return query.order_by(DiaristEvaluation.created_at.desc()).offset(skip).limit(limit).all()

    def get_evaluation_by_schedule(self, schedule_id: UUID) -> DiaristEvaluation | None:
        """Busca avaliação de um agendamento."""
        return self.db.query(DiaristEvaluation).filter(DiaristEvaluation.schedule_id == schedule_id).first()

    def _update_diarist_rating(self, diarist_id: UUID) -> None:
        """Atualiza média de avaliação da diarista."""
        result = (
            self.db.query(
                func.avg(DiaristEvaluation.nota_geral).label("media"),
                func.count(DiaristEvaluation.id).label("total"),
            )
            .filter(DiaristEvaluation.diarist_id == diarist_id)
            .first()
        )

        if result and result.media:
            diarist = self.db.query(Diarist).filter(Diarist.id == diarist_id).first()
            if diarist:
                diarist.avaliacao_media = Decimal(str(result.media))
                diarist.total_avaliacoes = result.total
                self.db.commit()

    # ==================== MÉTRICAS E ESTATÍSTICAS ====================

    def get_diarist_metrics(
        self,
        diarist_id: UUID,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> dict:
        """Calcula métricas da diarista."""
        if not data_inicio:
            data_inicio = date.today() - timedelta(days=30)
        if not data_fim:
            data_fim = date.today()

        # Agendamentos no período
        schedules = (
            self.db.query(DiaristSchedule)
            .filter(
                DiaristSchedule.diarist_id == diarist_id,
                DiaristSchedule.data_trabalho >= data_inicio,
                DiaristSchedule.data_trabalho <= data_fim,
            )
            .all()
        )

        total_agendamentos = len(schedules)
        concluidos = sum(1 for s in schedules if s.status == ScheduleStatus.CONCLUIDO)
        cancelados = sum(1 for s in schedules if s.status == ScheduleStatus.CANCELADO)

        # Horas trabalhadas
        horas_trabalhadas = sum(
            s.calcular_horas_trabalhadas() or Decimal("0") for s in schedules if s.status == ScheduleStatus.CONCLUIDO
        )

        # Taxa de pontualidade
        pontuais = sum(1 for s in schedules if s.pontualidade_checkin())
        taxa_pontualidade = (pontuais / concluidos * 100) if concluidos > 0 else 0

        # Pagamentos
        pagamentos = self.db.query(func.sum(DiaristPayment.valor_liquido)).filter(
            DiaristPayment.diarist_id == diarist_id,
            DiaristPayment.data_referencia >= data_inicio,
            DiaristPayment.data_referencia <= data_fim,
            DiaristPayment.status == PaymentStatus.PAGO,
        ).scalar() or Decimal("0")

        return {
            "periodo": {"inicio": data_inicio, "fim": data_fim},
            "agendamentos": {
                "total": total_agendamentos,
                "concluidos": concluidos,
                "cancelados": cancelados,
                "taxa_conclusao": (concluidos / total_agendamentos * 100 if total_agendamentos > 0 else 0),
            },
            "horas_trabalhadas": float(horas_trabalhadas),
            "taxa_pontualidade": round(taxa_pontualidade, 1),
            "valor_recebido": float(pagamentos),
        }

    def get_condominio_statistics(
        self,
        condominio_id: UUID,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> dict:
        """Estatísticas de diaristas do condomínio."""
        if not data_inicio:
            data_inicio = date.today() - timedelta(days=30)
        if not data_fim:
            data_fim = date.today()

        # Total de diaristas ativas
        total_diaristas = (
            self.db.query(func.count(func.distinct(DiaristAssignment.diarist_id)))
            .filter(
                DiaristAssignment.condominio_id == condominio_id,
                DiaristAssignment.status == AssignmentStatus.ATIVO,
            )
            .scalar()
            or 0
        )

        # Agendamentos
        schedules_query = self.db.query(DiaristSchedule).filter(
            DiaristSchedule.condominio_id == condominio_id,
            DiaristSchedule.data_trabalho >= data_inicio,
            DiaristSchedule.data_trabalho <= data_fim,
        )

        total_agendamentos = schedules_query.count()
        concluidos = schedules_query.filter(DiaristSchedule.status == ScheduleStatus.CONCLUIDO).count()

        # Gastos
        gastos = self.db.query(func.sum(DiaristPayment.valor_liquido)).filter(
            DiaristPayment.condominio_id == condominio_id,
            DiaristPayment.data_referencia >= data_inicio,
            DiaristPayment.data_referencia <= data_fim,
        ).scalar() or Decimal("0")

        # Média de avaliações
        media_avaliacoes = (
            self.db.query(func.avg(DiaristEvaluation.nota_geral))
            .join(DiaristSchedule)
            .filter(
                DiaristSchedule.condominio_id == condominio_id,
                DiaristSchedule.data_trabalho >= data_inicio,
                DiaristSchedule.data_trabalho <= data_fim,
            )
            .scalar()
        )

        return {
            "periodo": {"inicio": data_inicio, "fim": data_fim},
            "total_diaristas": total_diaristas,
            "agendamentos": {
                "total": total_agendamentos,
                "concluidos": concluidos,
                "taxa_conclusao": (concluidos / total_agendamentos * 100 if total_agendamentos > 0 else 0),
            },
            "gastos_total": float(gastos),
            "media_avaliacoes": round(float(media_avaliacoes or 0), 2),
        }

    def get_top_diarists(
        self,
        condominio_id: UUID | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Retorna ranking das melhores diaristas."""
        query = (
            self.db.query(
                Diarist,
                func.count(DiaristSchedule.id).label("total_servicos"),
            )
            .join(DiaristSchedule)
            .filter(
                Diarist.status == DiaristStatus.ATIVO,
                DiaristSchedule.status == ScheduleStatus.CONCLUIDO,
            )
            .group_by(Diarist.id)
        )

        if condominio_id:
            query = query.filter(DiaristSchedule.condominio_id == condominio_id)

        query = query.order_by(
            Diarist.avaliacao_media.desc(),
            func.count(DiaristSchedule.id).desc(),
        ).limit(limit)

        results = query.all()

        return [
            {
                "diarist": diarist,
                "total_servicos": total,
                "avaliacao_media": float(diarist.avaliacao_media or 0),
            }
            for diarist, total in results
        ]
