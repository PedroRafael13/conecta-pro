"""Testes para Models de Diaristas."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.operacional.diaristas.models.diarist import (
    AssignmentStatus,
    AssignmentType,
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


class TestDiaristModel:
    """Testes para o model Diarist."""

    def test_create_diarist(self):
        """Testa criação de diarista."""
        diarist = Diarist(
            nome="Maria Silva",
            cpf="123.456.789-00",
            telefone="11999999999",
            tipos_servico=[DiaristType.LIMPEZA, DiaristType.FAXINA],
            status=DiaristStatus.ATIVO,
        )

        assert diarist.nome == "Maria Silva"
        assert diarist.cpf == "123.456.789-00"
        assert DiaristType.LIMPEZA in diarist.tipos_servico
        assert diarist.status == DiaristStatus.ATIVO

    def test_diarist_disponibilidade(self):
        """Testa disponibilidade da diarista."""
        diarist = Diarist(
            nome="Ana Santos",
            cpf="987.654.321-00",
            telefone="11888888888",
            dias_disponiveis=[Weekday.MONDAY, Weekday.WEDNESDAY, Weekday.FRIDAY],
            hora_inicio_disponivel=time(8, 0),
            hora_fim_disponivel=time(17, 0),
        )

        assert len(diarist.dias_disponiveis) == 3
        assert Weekday.MONDAY in diarist.dias_disponiveis
        assert diarist.hora_inicio_disponivel == time(8, 0)

    def test_diarist_financeiro(self):
        """Testa dados financeiros da diarista."""
        diarist = Diarist(
            nome="Joana Costa",
            cpf="111.222.333-44",
            telefone="11777777777",
            valor_hora=Decimal("25.00"),
            valor_diaria=Decimal("180.00"),
            valor_hora_extra=Decimal("35.00"),
            pix="11777777777",
        )

        assert diarist.valor_hora == Decimal("25.00")
        assert diarist.valor_diaria == Decimal("180.00")
        assert diarist.pix == "11777777777"

    def test_diarist_metricas(self):
        """Testa métricas da diarista."""
        diarist = Diarist(
            nome="Paula Lima",
            cpf="555.666.777-88",
            telefone="11666666666",
            avaliacao_media=Decimal("4.50"),
            total_avaliacoes=25,
            total_servicos=50,
            valor_total_recebido=Decimal("9000.00"),
        )

        assert diarist.avaliacao_media == Decimal("4.50")
        assert diarist.total_avaliacoes == 25
        assert diarist.total_servicos == 50

    def test_diarist_scores_ia(self):
        """Testa scores de IA da diarista."""
        diarist = Diarist(
            nome="Carla Mendes",
            cpf="999.888.777-66",
            telefone="11555555555",
            score_confiabilidade=Decimal("92.50"),
            score_qualidade=Decimal("88.00"),
            score_pontualidade=Decimal("95.00"),
            ultima_analise_ia=datetime.now(),
        )

        assert diarist.score_confiabilidade == Decimal("92.50")
        assert diarist.score_qualidade == Decimal("88.00")
        assert diarist.score_pontualidade == Decimal("95.00")


class TestDiaristAssignmentModel:
    """Testes para o model DiaristAssignment."""

    def test_create_assignment_avulso(self):
        """Testa criação de alocação avulsa."""
        assignment = DiaristAssignment(
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            tipo=AssignmentType.CONDOMINIO,
            data_inicio=date.today(),
            recorrencia=RecurrenceType.AVULSO,
            valor_acordado=Decimal("200.00"),
            status=AssignmentStatus.ATIVO,
        )

        assert assignment.tipo == AssignmentType.CONDOMINIO
        assert assignment.recorrencia == RecurrenceType.AVULSO
        assert assignment.valor_acordado == Decimal("200.00")

    def test_create_assignment_recorrente(self):
        """Testa criação de alocação recorrente."""
        assignment = DiaristAssignment(
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            unidade_id=uuid4(),
            tipo=AssignmentType.UNIDADE,
            data_inicio=date.today(),
            data_fim=date.today() + timedelta(days=90),
            recorrencia=RecurrenceType.SEMANAL,
            dias_semana=[Weekday.TUESDAY, Weekday.THURSDAY],
            hora_inicio=time(8, 0),
            hora_fim=time(16, 0),
            status=AssignmentStatus.ATIVO,
        )

        assert assignment.tipo == AssignmentType.UNIDADE
        assert assignment.recorrencia == RecurrenceType.SEMANAL
        assert len(assignment.dias_semana) == 2

    def test_assignment_status_transitions(self):
        """Testa transições de status."""
        assignment = DiaristAssignment(
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            tipo=AssignmentType.AREA_COMUM,
            data_inicio=date.today(),
            status=AssignmentStatus.ATIVO,
        )

        assert assignment.status == AssignmentStatus.ATIVO

        assignment.status = AssignmentStatus.PAUSADO
        assert assignment.status == AssignmentStatus.PAUSADO

        assignment.status = AssignmentStatus.ENCERRADO
        assert assignment.status == AssignmentStatus.ENCERRADO


class TestDiaristScheduleModel:
    """Testes para o model DiaristSchedule."""

    def test_create_schedule(self):
        """Testa criação de agendamento."""
        schedule = DiaristSchedule(
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            data_trabalho=date.today() + timedelta(days=1),
            hora_inicio=time(8, 0),
            hora_fim=time(16, 0),
            valor_previsto=Decimal("180.00"),
            status=ScheduleStatus.AGENDADO,
        )

        assert schedule.data_trabalho == date.today() + timedelta(days=1)
        assert schedule.hora_inicio == time(8, 0)
        assert schedule.valor_previsto == Decimal("180.00")
        assert schedule.status == ScheduleStatus.AGENDADO

    def test_schedule_checkin_checkout(self):
        """Testa check-in e check-out."""
        schedule = DiaristSchedule(
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            data_trabalho=date.today(),
            hora_inicio=time(8, 0),
            hora_fim=time(16, 0),
            status=ScheduleStatus.EM_ANDAMENTO,
        )

        # Registrar check-in
        checkin = datetime.now().replace(hour=8, minute=5)
        schedule.checkin_real = checkin
        schedule.checkin_latitude = Decimal("-23.5505")
        schedule.checkin_longitude = Decimal("-46.6333")

        assert schedule.checkin_real == checkin
        assert schedule.checkin_latitude == Decimal("-23.5505")

        # Registrar check-out
        checkout = datetime.now().replace(hour=16, minute=10)
        schedule.checkout_real = checkout
        schedule.status = ScheduleStatus.CONCLUIDO

        assert schedule.checkout_real == checkout
        assert schedule.status == ScheduleStatus.CONCLUIDO

    def test_calcular_horas_trabalhadas(self):
        """Testa cálculo de horas trabalhadas."""
        schedule = DiaristSchedule(
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            data_trabalho=date.today(),
            hora_inicio=time(8, 0),
            hora_fim=time(16, 0),
            checkin_real=datetime.now().replace(hour=8, minute=0),
            checkout_real=datetime.now().replace(hour=16, minute=30),
            status=ScheduleStatus.CONCLUIDO,
        )

        horas = schedule.calcular_horas_trabalhadas()
        assert horas is not None
        assert horas >= Decimal("8.0")

    def test_pontualidade_checkin(self):
        """Testa verificação de pontualidade."""
        schedule = DiaristSchedule(
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            data_trabalho=date.today(),
            hora_inicio=time(8, 0),
            hora_fim=time(16, 0),
            checkin_real=datetime.now().replace(hour=8, minute=5),
        )

        # Check-in dentro da tolerância (15 min)
        assert schedule.pontualidade_checkin() is True

        # Check-in atrasado
        schedule.checkin_real = datetime.now().replace(hour=8, minute=30)
        assert schedule.pontualidade_checkin() is False

    def test_schedule_tarefas(self):
        """Testa lista de tarefas."""
        schedule = DiaristSchedule(
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            data_trabalho=date.today(),
            tarefas=["Limpeza sala", "Limpeza quartos", "Passar roupa"],
            status=ScheduleStatus.AGENDADO,
        )

        assert len(schedule.tarefas) == 3
        assert "Limpeza sala" in schedule.tarefas


class TestDiaristPaymentModel:
    """Testes para o model DiaristPayment."""

    def test_create_payment(self):
        """Testa criação de pagamento."""
        payment = DiaristPayment(
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            data_referencia=date.today(),
            data_vencimento=date.today() + timedelta(days=5),
            valor_bruto=Decimal("500.00"),
            valor_liquido=Decimal("445.00"),
            forma_pagamento=PaymentMethod.PIX,
            status=PaymentStatus.PENDENTE,
        )

        assert payment.valor_bruto == Decimal("500.00")
        assert payment.valor_liquido == Decimal("445.00")
        assert payment.forma_pagamento == PaymentMethod.PIX
        assert payment.status == PaymentStatus.PENDENTE

    def test_payment_retencoes(self):
        """Testa retenções no pagamento."""
        valor_bruto = Decimal("1000.00")
        inss = Decimal("110.00")  # 11%
        iss = Decimal("50.00")  # 5%
        irrf = Decimal("0.00")
        outros = Decimal("0.00")
        valor_liquido = valor_bruto - inss - iss - irrf - outros

        payment = DiaristPayment(
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            data_referencia=date.today(),
            valor_bruto=valor_bruto,
            retencao_inss=inss,
            retencao_iss=iss,
            retencao_irrf=irrf,
            outros_descontos=outros,
            valor_liquido=valor_liquido,
            status=PaymentStatus.PENDENTE,
        )

        assert payment.valor_liquido == Decimal("840.00")
        assert payment.retencao_inss == Decimal("110.00")

    def test_payment_calculo_retencoes(self):
        """Testa método de cálculo de retenções."""
        payment = DiaristPayment(
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            data_referencia=date.today(),
            valor_bruto=Decimal("2000.00"),
            valor_liquido=Decimal("2000.00"),
            status=PaymentStatus.PENDENTE,
        )

        # Chamar método de cálculo (se existir no model)
        retencoes = payment.calcular_retencoes()

        assert "inss" in retencoes
        assert "iss" in retencoes
        assert "irrf" in retencoes

    def test_payment_status_transitions(self):
        """Testa transições de status do pagamento."""
        payment = DiaristPayment(
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            data_referencia=date.today(),
            valor_bruto=Decimal("500.00"),
            valor_liquido=Decimal("450.00"),
            status=PaymentStatus.PENDENTE,
        )

        # Aprovar
        payment.status = PaymentStatus.APROVADO
        assert payment.status == PaymentStatus.APROVADO

        # Pagar
        payment.status = PaymentStatus.PAGO
        payment.data_pagamento = date.today()
        assert payment.status == PaymentStatus.PAGO
        assert payment.data_pagamento == date.today()


class TestDiaristEvaluationModel:
    """Testes para o model DiaristEvaluation."""

    def test_create_evaluation(self):
        """Testa criação de avaliação."""
        evaluation = DiaristEvaluation(
            diarist_id=uuid4(),
            schedule_id=uuid4(),
            avaliador_id=uuid4(),
            nota_geral=5,
            nota_pontualidade=5,
            nota_qualidade=4,
            nota_comportamento=5,
            nota_comunicacao=4,
            comentario="Excelente trabalho!",
            recomendaria=True,
        )

        assert evaluation.nota_geral == 5
        assert evaluation.nota_qualidade == 4
        assert evaluation.recomendaria is True

    def test_evaluation_media(self):
        """Testa cálculo de média da avaliação."""
        evaluation = DiaristEvaluation(
            diarist_id=uuid4(),
            nota_geral=4,
            nota_pontualidade=5,
            nota_qualidade=4,
            nota_comportamento=3,
            nota_comunicacao=4,
        )

        media = evaluation.calcular_media()
        assert media is not None
        assert 3 <= media <= 5

    def test_evaluation_validacao_notas(self):
        """Testa validação de notas (1-5)."""
        # Nota válida
        evaluation = DiaristEvaluation(
            diarist_id=uuid4(),
            nota_geral=5,
        )
        assert evaluation.nota_geral == 5

        # Verificar se o model aceita apenas 1-5
        with pytest.raises((ValueError, Exception)):
            DiaristEvaluation(
                diarist_id=uuid4(),
                nota_geral=6,  # Inválido
            )


class TestEnums:
    """Testes para os Enums do módulo."""

    def test_diarist_type_values(self):
        """Testa valores do enum DiaristType."""
        assert DiaristType.LIMPEZA.value == "LIMPEZA"
        assert DiaristType.FAXINA.value == "FAXINA"
        assert DiaristType.COZINHEIRA.value == "COZINHEIRA"
        assert len(DiaristType) == 9

    def test_diarist_status_values(self):
        """Testa valores do enum DiaristStatus."""
        assert DiaristStatus.ATIVO.value == "ATIVO"
        assert DiaristStatus.INATIVO.value == "INATIVO"
        assert DiaristStatus.PENDENTE.value == "PENDENTE"
        assert len(DiaristStatus) == 5

    def test_weekday_values(self):
        """Testa valores do enum Weekday."""
        assert Weekday.MONDAY.value == "MONDAY"
        assert Weekday.FRIDAY.value == "FRIDAY"
        assert Weekday.SUNDAY.value == "SUNDAY"
        assert len(Weekday) == 7

    def test_schedule_status_values(self):
        """Testa valores do enum ScheduleStatus."""
        assert ScheduleStatus.AGENDADO.value == "AGENDADO"
        assert ScheduleStatus.CONCLUIDO.value == "CONCLUIDO"
        assert ScheduleStatus.NAO_COMPARECEU.value == "NAO_COMPARECEU"
        assert len(ScheduleStatus) == 6

    def test_payment_method_values(self):
        """Testa valores do enum PaymentMethod."""
        assert PaymentMethod.PIX.value == "PIX"
        assert PaymentMethod.TRANSFERENCIA.value == "TRANSFERENCIA"
        assert PaymentMethod.DINHEIRO.value == "DINHEIRO"
        assert len(PaymentMethod) == 5
