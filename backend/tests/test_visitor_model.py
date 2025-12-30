"""Testes unitários para models do módulo Visitors."""

import pytest
from datetime import datetime, timedelta, date, time
from uuid import uuid4

from modules.visitors.models.visitor import (
    Visitor,
    VisitorType,
    VisitorStatus,
    DocumentType,
)
from modules.visitors.models.authorization import (
    VisitorAuthorization,
    AuthorizationType,
    AuthorizationStatus,
    RecurrenceType,
)
from modules.visitors.models.log import (
    VisitorLog,
    AccessType,
    AccessMethod,
    AccessPoint,
    DenialReason,
)
from modules.visitors.models.schedule import (
    VisitorSchedule,
    ScheduleStatus,
    SchedulePriority,
)


class TestVisitorModel:
    """Testes para o model Visitor."""

    def test_create_visitor(self):
        """Testa criação de visitante."""
        visitor = Visitor(
            name="João Silva",
            document_type=DocumentType.CPF,
            document_number="12345678901",
            phone="11999999999",
            visitor_type=VisitorType.VISITANTE,
        )

        assert visitor.name == "João Silva"
        assert visitor.document_type == DocumentType.CPF
        assert visitor.visitor_type == VisitorType.VISITANTE
        assert visitor.status == VisitorStatus.ATIVO

    def test_visitor_block(self):
        """Testa bloqueio de visitante."""
        visitor = Visitor(
            name="Maria Santos",
            document_type=DocumentType.CPF,
            document_number="98765432100",
            visitor_type=VisitorType.VISITANTE,
        )

        visitor.block("Comportamento inadequado", "admin_001")

        assert visitor.is_blocked is True
        assert visitor.status == VisitorStatus.BLOQUEADO
        assert visitor.block_reason == "Comportamento inadequado"
        assert visitor.blocked_by is not None

    def test_visitor_unblock(self):
        """Testa desbloqueio de visitante."""
        visitor = Visitor(
            name="Pedro Costa",
            document_type=DocumentType.RG,
            document_number="123456789",
            visitor_type=VisitorType.PRESTADOR,
            is_blocked=True,
            status=VisitorStatus.BLOQUEADO,
        )

        visitor.unblock()

        assert visitor.is_blocked is False
        assert visitor.status == VisitorStatus.ATIVO
        assert visitor.block_reason is None

    def test_visitor_set_vip(self):
        """Testa definição de VIP."""
        visitor = Visitor(
            name="Ana Souza",
            document_type=DocumentType.CPF,
            document_number="11122233344",
            visitor_type=VisitorType.VISITANTE,
        )

        visitor.set_vip()

        assert visitor.is_vip is True

    def test_visitor_register_visit(self):
        """Testa registro de visita."""
        visitor = Visitor(
            name="Carlos Lima",
            document_type=DocumentType.CPF,
            document_number="55566677788",
            visitor_type=VisitorType.VISITANTE,
            total_visits=5,
        )

        visitor.register_visit()

        assert visitor.total_visits == 6
        assert visitor.last_visit is not None

    def test_visitor_generate_qr_code(self):
        """Testa geração de QR code."""
        visitor = Visitor(
            id=uuid4(),
            name="Fernanda Alves",
            document_type=DocumentType.CPF,
            document_number="99988877766",
            visitor_type=VisitorType.VISITANTE,
        )

        qr_code = visitor.generate_qr_code()

        assert qr_code is not None
        assert visitor.qr_code == qr_code
        assert visitor.qr_code_generated_at is not None

    def test_visitor_is_valid_active(self):
        """Testa validação de visitante ativo."""
        visitor = Visitor(
            name="Roberto Dias",
            document_type=DocumentType.CPF,
            document_number="44433322211",
            visitor_type=VisitorType.VISITANTE,
            status=VisitorStatus.ATIVO,
            is_blocked=False,
        )

        assert visitor.is_valid is True

    def test_visitor_is_valid_blocked(self):
        """Testa validação de visitante bloqueado."""
        visitor = Visitor(
            name="Lucia Mendes",
            document_type=DocumentType.CPF,
            document_number="77766655544",
            visitor_type=VisitorType.VISITANTE,
            is_blocked=True,
        )

        assert visitor.is_valid is False

    def test_visitor_frequency_category(self):
        """Testa categoria de frequência."""
        visitor_rare = Visitor(
            name="Visitante Raro",
            document_type=DocumentType.CPF,
            document_number="11111111111",
            visitor_type=VisitorType.VISITANTE,
            total_visits=2,
        )

        visitor_occasional = Visitor(
            name="Visitante Ocasional",
            document_type=DocumentType.CPF,
            document_number="22222222222",
            visitor_type=VisitorType.VISITANTE,
            total_visits=7,
        )

        visitor_frequent = Visitor(
            name="Visitante Frequente",
            document_type=DocumentType.CPF,
            document_number="33333333333",
            visitor_type=VisitorType.VISITANTE,
            total_visits=30,
        )

        visitor_vip = Visitor(
            name="Visitante VIP",
            document_type=DocumentType.CPF,
            document_number="44444444444",
            visitor_type=VisitorType.VISITANTE,
            total_visits=60,
        )

        assert visitor_rare.frequency_category == "raro"
        assert visitor_occasional.frequency_category == "ocasional"
        assert visitor_frequent.frequency_category == "frequente"
        assert visitor_vip.frequency_category == "muito_frequente"


class TestVisitorAuthorizationModel:
    """Testes para o model VisitorAuthorization."""

    def test_create_authorization(self):
        """Testa criação de autorização."""
        auth = VisitorAuthorization(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            unit_id="unit_101",
            resident_id="resident_001",
            authorization_type=AuthorizationType.UNICA,
        )

        assert auth.authorization_type == AuthorizationType.UNICA
        assert auth.status == AuthorizationStatus.PENDENTE

    def test_authorization_approve(self):
        """Testa aprovação de autorização."""
        auth = VisitorAuthorization(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            unit_id="unit_101",
            authorization_type=AuthorizationType.PERIODO,
            status=AuthorizationStatus.PENDENTE,
        )

        auth.approve("admin_001", "Administrador")

        assert auth.status == AuthorizationStatus.APROVADA
        assert auth.approved_by_id == "admin_001"
        assert auth.approved_at is not None

    def test_authorization_reject(self):
        """Testa rejeição de autorização."""
        auth = VisitorAuthorization(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            authorization_type=AuthorizationType.UNICA,
            status=AuthorizationStatus.PENDENTE,
        )

        auth.reject("admin_001", "Administrador", "Documentação incompleta")

        assert auth.status == AuthorizationStatus.REJEITADA
        assert auth.rejection_reason == "Documentação incompleta"

    def test_authorization_cancel(self):
        """Testa cancelamento de autorização."""
        auth = VisitorAuthorization(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            authorization_type=AuthorizationType.PERIODO,
            status=AuthorizationStatus.APROVADA,
        )

        auth.cancel("Mudança de planos")

        assert auth.status == AuthorizationStatus.CANCELADA
        assert auth.cancelled_at is not None

    def test_authorization_use(self):
        """Testa uso de autorização."""
        auth = VisitorAuthorization(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            authorization_type=AuthorizationType.UNICA,
            status=AuthorizationStatus.APROVADA,
            max_uses=1,
            uses_count=0,
        )

        result = auth.use()

        assert result is True
        assert auth.uses_count == 1
        assert auth.status == AuthorizationStatus.UTILIZADA

    def test_authorization_extend_validity(self):
        """Testa extensão de validade."""
        original_expiry = datetime.utcnow() + timedelta(days=5)
        auth = VisitorAuthorization(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            authorization_type=AuthorizationType.PERIODO,
            valid_until=original_expiry,
        )

        auth.extend_validity(10)

        assert auth.valid_until > original_expiry

    def test_authorization_is_valid(self):
        """Testa validação de autorização."""
        auth = VisitorAuthorization(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            authorization_type=AuthorizationType.PERIODO,
            status=AuthorizationStatus.APROVADA,
            valid_from=datetime.utcnow() - timedelta(days=1),
            valid_until=datetime.utcnow() + timedelta(days=5),
            max_uses=10,
            uses_count=5,
        )

        assert auth.is_valid is True

    def test_authorization_expired(self):
        """Testa autorização expirada."""
        auth = VisitorAuthorization(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            authorization_type=AuthorizationType.PERIODO,
            status=AuthorizationStatus.APROVADA,
            valid_until=datetime.utcnow() - timedelta(days=1),
        )

        assert auth.is_valid is False

    def test_authorization_remaining_uses(self):
        """Testa usos restantes."""
        auth = VisitorAuthorization(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            authorization_type=AuthorizationType.PERIODO,
            max_uses=10,
            uses_count=3,
        )

        assert auth.remaining_uses == 7


class TestVisitorLogModel:
    """Testes para o model VisitorLog."""

    def test_create_entry_log(self):
        """Testa criação de log de entrada."""
        log = VisitorLog(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            access_type=AccessType.ENTRADA,
            access_method=AccessMethod.PORTARIA,
            access_point=AccessPoint.PORTARIA_PRINCIPAL,
        )

        assert log.access_type == AccessType.ENTRADA
        assert log.is_entry is True
        assert log.is_exit is False

    def test_create_exit_log(self):
        """Testa criação de log de saída."""
        log = VisitorLog(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            access_type=AccessType.SAIDA,
            access_method=AccessMethod.PORTARIA,
            access_point=AccessPoint.PORTARIA_PRINCIPAL,
        )

        assert log.access_type == AccessType.SAIDA
        assert log.is_exit is True

    def test_log_register_entry(self):
        """Testa registro de entrada."""
        log = VisitorLog(
            visitor_id=uuid4(),
            condominium_id="condo_001",
        )

        log.register_entry(
            access_method=AccessMethod.QR_CODE,
            access_point=AccessPoint.GARAGEM,
            operator_id="op_001",
        )

        assert log.access_type == AccessType.ENTRADA
        assert log.access_method == AccessMethod.QR_CODE
        assert log.access_point == AccessPoint.GARAGEM
        assert log.entry_timestamp is not None

    def test_log_register_exit(self):
        """Testa registro de saída."""
        entry_time = datetime.utcnow() - timedelta(hours=2)
        log = VisitorLog(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            access_type=AccessType.ENTRADA,
            entry_timestamp=entry_time,
        )

        log.register_exit()

        assert log.exit_timestamp is not None
        assert log.duration_minutes > 0

    def test_log_deny_access(self):
        """Testa negativa de acesso."""
        log = VisitorLog(
            visitor_id=uuid4(),
            condominium_id="condo_001",
        )

        log.deny_access(
            reason=DenialReason.SEM_AUTORIZACAO,
            operator_id="op_001",
        )

        assert log.denied is True
        assert log.denial_reason == DenialReason.SEM_AUTORIZACAO
        assert log.is_denied is True

    def test_log_duration(self):
        """Testa cálculo de duração."""
        entry = datetime.utcnow() - timedelta(hours=3, minutes=30)
        exit = datetime.utcnow()
        log = VisitorLog(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            entry_timestamp=entry,
            exit_timestamp=exit,
            duration_minutes=210,
        )

        assert log.formatted_duration == "3h 30min"

    def test_log_is_still_inside(self):
        """Testa se visitante ainda está dentro."""
        log = VisitorLog(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            access_type=AccessType.ENTRADA,
            entry_timestamp=datetime.utcnow(),
            exit_timestamp=None,
            denied=False,
        )

        assert log.is_still_inside is True


class TestVisitorScheduleModel:
    """Testes para o model VisitorSchedule."""

    def test_create_schedule(self):
        """Testa criação de agendamento."""
        schedule = VisitorSchedule(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            unit_id="unit_101",
            scheduled_date=date.today() + timedelta(days=1),
            scheduled_time_from=time(14, 0),
        )

        assert schedule.status == ScheduleStatus.PENDENTE
        assert schedule.is_future is True

    def test_schedule_confirm(self):
        """Testa confirmação de agendamento."""
        schedule = VisitorSchedule(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            scheduled_date=date.today() + timedelta(days=1),
            scheduled_time_from=time(10, 0),
            status=ScheduleStatus.PENDENTE,
        )

        schedule.confirm("admin_001", "Administrador")

        assert schedule.status == ScheduleStatus.CONFIRMADO
        assert schedule.confirmed_by_id == "admin_001"
        assert schedule.confirmed_at is not None

    def test_schedule_cancel(self):
        """Testa cancelamento de agendamento."""
        schedule = VisitorSchedule(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            scheduled_date=date.today() + timedelta(days=1),
            scheduled_time_from=time(15, 0),
            status=ScheduleStatus.CONFIRMADO,
        )

        schedule.cancel("Visitante cancelou", "op_001", "Operador")

        assert schedule.status == ScheduleStatus.CANCELADO
        assert schedule.cancellation_reason == "Visitante cancelou"

    def test_schedule_reschedule(self):
        """Testa reagendamento."""
        original_date = date.today() + timedelta(days=1)
        new_date = date.today() + timedelta(days=3)
        new_time = time(16, 0)

        schedule = VisitorSchedule(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            scheduled_date=original_date,
            scheduled_time_from=time(10, 0),
        )

        schedule.reschedule(new_date, new_time)

        assert schedule.scheduled_date == new_date
        assert schedule.scheduled_time_from == new_time
        assert schedule.reschedule_count == 1

    def test_schedule_check_in(self):
        """Testa check-in."""
        schedule = VisitorSchedule(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            scheduled_date=date.today(),
            scheduled_time_from=time(14, 0),
            status=ScheduleStatus.CONFIRMADO,
        )

        schedule.check_in()

        assert schedule.status == ScheduleStatus.REALIZADO
        assert schedule.actual_arrival is not None

    def test_schedule_check_out(self):
        """Testa check-out."""
        schedule = VisitorSchedule(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            scheduled_date=date.today(),
            scheduled_time_from=time(14, 0),
            status=ScheduleStatus.REALIZADO,
            actual_arrival=datetime.utcnow() - timedelta(hours=1),
        )

        schedule.check_out()

        assert schedule.actual_departure is not None

    def test_schedule_no_show(self):
        """Testa não comparecimento."""
        schedule = VisitorSchedule(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            scheduled_date=date.today() - timedelta(days=1),
            scheduled_time_from=time(10, 0),
            status=ScheduleStatus.CONFIRMADO,
        )

        schedule.no_show()

        assert schedule.status == ScheduleStatus.NAO_COMPARECEU

    def test_schedule_is_today(self):
        """Testa se agendamento é hoje."""
        schedule = VisitorSchedule(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            scheduled_date=date.today(),
            scheduled_time_from=time(10, 0),
        )

        assert schedule.is_today is True
        assert schedule.is_past is False
        assert schedule.is_future is False

    def test_schedule_can_check_in(self):
        """Testa se pode fazer check-in."""
        schedule = VisitorSchedule(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            scheduled_date=date.today(),
            scheduled_time_from=time(0, 0),
            status=ScheduleStatus.CONFIRMADO,
        )

        assert schedule.can_check_in is True

    def test_schedule_days_until(self):
        """Testa dias até o agendamento."""
        future_date = date.today() + timedelta(days=5)
        schedule = VisitorSchedule(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            scheduled_date=future_date,
            scheduled_time_from=time(10, 0),
        )

        assert schedule.days_until == 5

    def test_schedule_send_reminder(self):
        """Testa envio de lembrete."""
        schedule = VisitorSchedule(
            visitor_id=uuid4(),
            condominium_id="condo_001",
            scheduled_date=date.today() + timedelta(days=1),
            scheduled_time_from=time(10, 0),
        )

        schedule.send_reminder()

        assert schedule.reminder_sent is True
        assert schedule.reminder_sent_at is not None


class TestEnums:
    """Testes para os enums do módulo."""

    def test_visitor_type_values(self):
        """Testa valores de VisitorType."""
        assert VisitorType.VISITANTE.value == "visitante"
        assert VisitorType.PRESTADOR.value == "prestador"
        assert VisitorType.ENTREGADOR.value == "entregador"
        assert VisitorType.MOTORISTA.value == "motorista"
        assert len(VisitorType) == 13

    def test_authorization_status_values(self):
        """Testa valores de AuthorizationStatus."""
        assert AuthorizationStatus.PENDENTE.value == "pendente"
        assert AuthorizationStatus.APROVADA.value == "aprovada"
        assert AuthorizationStatus.REJEITADA.value == "rejeitada"
        assert len(AuthorizationStatus) == 7

    def test_access_type_values(self):
        """Testa valores de AccessType."""
        assert AccessType.ENTRADA.value == "entrada"
        assert AccessType.SAIDA.value == "saida"
        assert len(AccessType) == 5

    def test_denial_reason_values(self):
        """Testa valores de DenialReason."""
        assert DenialReason.SEM_AUTORIZACAO.value == "sem_autorizacao"
        assert DenialReason.VISITANTE_BLOQUEADO.value == "visitante_bloqueado"
        assert len(DenialReason) == 11
