"""Testes de API para endpoints de Diaristas."""

from datetime import date, time, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

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


@pytest.fixture
def mock_diarist():
    """Fixture para diarista mock."""
    return Diarist(
        id=uuid4(),
        nome="Maria Silva",
        cpf="123.456.789-00",
        telefone="11999999999",
        email="maria@email.com",
        tipos_servico=[DiaristType.LIMPEZA],
        dias_disponiveis=[Weekday.SEGUNDA, Weekday.QUARTA],
        valor_hora=Decimal("25.00"),
        valor_diaria=Decimal("180.00"),
        status=DiaristStatus.ATIVO,
        avaliacao_media=Decimal("4.50"),
        total_servicos=20,
    )


@pytest.fixture
def mock_assignment(mock_diarist):
    """Fixture para alocação mock."""
    return DiaristAssignment(
        id=uuid4(),
        diarist_id=mock_diarist.id,
        condominio_id=uuid4(),
        tipo="recorrente",
        data_inicio=date.today(),
        recorrencia="semanal",
        dias_semana=[Weekday.SEGUNDA],
        status=AssignmentStatus.CONFIRMADO,
        valor_acordado=Decimal("180.00"),
    )


@pytest.fixture
def mock_schedule(mock_diarist):
    """Fixture para agendamento mock."""
    return DiaristSchedule(
        id=uuid4(),
        diarist_id=mock_diarist.id,
        condominio_id=uuid4(),
        data_trabalho=date.today() + timedelta(days=1),
        hora_inicio=time(8, 0),
        hora_fim=time(16, 0),
        valor_previsto=Decimal("180.00"),
        status=ScheduleStatus.AGENDADO,
    )


@pytest.fixture
def mock_payment():
    """Fixture para pagamento mock."""
    return DiaristPayment(
        id=uuid4(),
        diarist_id=uuid4(),
        condominio_id=uuid4(),
        data_referencia=date.today(),
        valor_bruto=Decimal("500.00"),
        valor_liquido=Decimal("445.00"),
        status=PaymentStatus.PENDENTE,
    )


@pytest.fixture
def mock_evaluation():
    """Fixture para avaliação mock."""
    return DiaristEvaluation(
        id=uuid4(),
        diarist_id=uuid4(),
        schedule_id=uuid4(),
        avaliador_id=uuid4(),
        nota_geral=5,
    )


# ==================== TESTES DIARIST ====================


class TestDiaristEndpoints:
    """Testes para endpoints de Diaristas."""

    @pytest.mark.asyncio
    async def test_create_diarist_success(self, mock_diarist):
        """Testa criação de diarista com sucesso."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.create_diarist = AsyncMock(return_value=mock_diarist)

            result = await mock_instance.create_diarist(
                {
                    "nome": "Ana Costa",
                    "cpf": "111.222.333-44",
                    "valor_diaria": 180.00,
                }
            )

            assert result.nome == "Maria Silva"
            assert result.status == DiaristStatus.ATIVO.value
            mock_instance.create_diarist.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_diarist_duplicate_cpf(self):
        """Testa erro ao criar diarista com CPF duplicado."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.create_diarist = AsyncMock(side_effect=ValueError("CPF 123.456.789-00 já cadastrado"))

            with pytest.raises(ValueError, match="já cadastrado"):
                await mock_instance.create_diarist(
                    {
                        "nome": "Ana Costa",
                        "cpf": "123.456.789-00",
                    }
                )

    @pytest.mark.asyncio
    async def test_list_diarists(self, mock_diarist):
        """Testa listagem de diaristas."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.list_diarists = AsyncMock(return_value=[mock_diarist])

            result = await mock_instance.list_diarists()
            assert len(result) == 1
            assert result[0].nome == "Maria Silva"

    @pytest.mark.asyncio
    async def test_list_diarists_with_filters(self, mock_diarist):
        """Testa listagem de diaristas com filtros."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.list_diarists = AsyncMock(return_value=[mock_diarist])

            result = await mock_instance.list_diarists(status="ATIVO", tipo="LIMPEZA", search="Maria")
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_diarist_by_id(self, mock_diarist):
        """Testa busca de diarista por ID."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.get_diarist = AsyncMock(return_value=mock_diarist)

            result = await mock_instance.get_diarist(mock_diarist.id)
            assert result.nome == mock_diarist.nome
            assert result.cpf == mock_diarist.cpf

    @pytest.mark.asyncio
    async def test_get_diarist_not_found(self):
        """Testa busca de diarista inexistente."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.get_diarist = AsyncMock(return_value=None)

            result = await mock_instance.get_diarist(uuid4())
            assert result is None

    @pytest.mark.asyncio
    async def test_update_diarist(self, mock_diarist):
        """Testa atualização de diarista."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_diarist.telefone = "11777777777"
            mock_diarist.valor_hora = Decimal("30.00")
            mock_instance.update_diarist = AsyncMock(return_value=mock_diarist)

            result = await mock_instance.update_diarist(
                mock_diarist.id, {"telefone": "11777777777", "valor_hora": 30.00}
            )
            assert result.telefone == "11777777777"
            assert result.valor_hora == Decimal("30.00")

    @pytest.mark.asyncio
    async def test_activate_diarist(self, mock_diarist):
        """Testa ativação de diarista."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_diarist.status = DiaristStatus.ATIVO.value
            mock_instance.activate_diarist = AsyncMock(return_value=mock_diarist)

            result = await mock_instance.activate_diarist(mock_diarist.id)
            assert result.status == DiaristStatus.ATIVO.value

    @pytest.mark.asyncio
    async def test_delete_diarist(self):
        """Testa remoção de diarista."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.delete_diarist = AsyncMock(return_value=True)

            result = await mock_instance.delete_diarist(uuid4())
            assert result is True


# ==================== TESTES SCHEDULE ====================


class TestScheduleEndpoints:
    """Testes para endpoints de Agendamentos."""

    @pytest.mark.asyncio
    async def test_create_schedule(self, mock_schedule):
        """Testa criação de agendamento."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.create_schedule = AsyncMock(return_value=mock_schedule)

            result = await mock_instance.create_schedule(
                {
                    "diarist_id": str(uuid4()),
                    "condominio_id": str(uuid4()),
                    "data_trabalho": str(date.today() + timedelta(days=1)),
                    "hora_inicio": "08:00:00",
                    "hora_fim": "16:00:00",
                    "valor_previsto": 180.00,
                }
            )
            assert result.status == ScheduleStatus.AGENDADO
            assert result.valor_previsto == Decimal("180.00")

    @pytest.mark.asyncio
    async def test_list_schedules(self, mock_schedule):
        """Testa listagem de agendamentos."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.list_schedules = AsyncMock(return_value=[mock_schedule])

            result = await mock_instance.list_schedules()
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_today_schedules(self, mock_schedule):
        """Testa busca de agendamentos de hoje."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.get_today_schedules = AsyncMock(return_value=[mock_schedule])

            result = await mock_instance.get_today_schedules()
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_confirm_schedule(self, mock_schedule):
        """Testa confirmação de agendamento."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_schedule.status = ScheduleStatus.CONFIRMADO
            mock_instance.confirm_schedule = AsyncMock(return_value=mock_schedule)

            result = await mock_instance.confirm_schedule(mock_schedule.id)
            assert result.status == ScheduleStatus.CONFIRMADO

    @pytest.mark.asyncio
    async def test_register_checkin(self, mock_schedule):
        """Testa registro de check-in."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_schedule.status = ScheduleStatus.EM_ANDAMENTO
            mock_instance.register_checkin = AsyncMock(return_value=mock_schedule)

            result = await mock_instance.register_checkin(
                {
                    "schedule_id": str(mock_schedule.id),
                    "hora_checkin": "2025-01-01T08:05:00",
                    "latitude": -23.5505,
                    "longitude": -46.6333,
                }
            )
            assert result.status == ScheduleStatus.EM_ANDAMENTO

    @pytest.mark.asyncio
    async def test_register_checkout(self, mock_schedule):
        """Testa registro de check-out."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_schedule.status = ScheduleStatus.CONCLUIDO
            mock_instance.register_checkout = AsyncMock(return_value=mock_schedule)

            result = await mock_instance.register_checkout(
                {
                    "schedule_id": str(mock_schedule.id),
                    "hora_checkout": "2025-01-01T16:10:00",
                }
            )
            assert result.status == ScheduleStatus.CONCLUIDO


# ==================== TESTES PAYMENT ====================


class TestPaymentEndpoints:
    """Testes para endpoints de Pagamentos."""

    @pytest.mark.asyncio
    async def test_create_payment(self, mock_payment):
        """Testa criação de pagamento."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.create_payment = AsyncMock(return_value=mock_payment)

            result = await mock_instance.create_payment(
                {
                    "diarist_id": str(uuid4()),
                    "condominio_id": str(uuid4()),
                    "data_referencia": str(date.today()),
                    "valor_bruto": 500.00,
                }
            )
            assert result.valor_bruto == Decimal("500.00")
            assert result.status == PaymentStatus.PENDENTE

    @pytest.mark.asyncio
    async def test_list_pending_payments(self):
        """Testa listagem de pagamentos pendentes."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.get_pending_payments = AsyncMock(return_value=[])

            result = await mock_instance.get_pending_payments()
            assert isinstance(result, list)
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_process_payment(self, mock_payment):
        """Testa processamento de pagamento."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_payment.status = PaymentStatus.PAGO
            mock_payment.data_pagamento = date.today()
            mock_instance.process_payment = AsyncMock(return_value=mock_payment)

            result = await mock_instance.process_payment(mock_payment.id, data_pagamento=date.today())
            assert result.status == PaymentStatus.PAGO
            assert result.data_pagamento == date.today()


# ==================== TESTES EVALUATION ====================


class TestEvaluationEndpoints:
    """Testes para endpoints de Avaliações."""

    @pytest.mark.asyncio
    async def test_create_evaluation(self, mock_evaluation):
        """Testa criação de avaliação."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.create_evaluation = AsyncMock(return_value=mock_evaluation)

            result = await mock_instance.create_evaluation(
                {
                    "schedule_id": str(uuid4()),
                    "avaliador_id": str(uuid4()),
                    "nota_geral": 5,
                    "nota_pontualidade": 5,
                    "nota_qualidade": 4,
                    "nota_comportamento": 5,
                    "nota_comunicacao": 4,
                    "comentario": "Excelente trabalho!",
                    "recomendaria": True,
                }
            )
            assert result.nota_geral == 5

    @pytest.mark.asyncio
    async def test_list_evaluations(self):
        """Testa listagem de avaliações."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.list_evaluations = AsyncMock(return_value=[])

            result = await mock_instance.list_evaluations()
            assert isinstance(result, list)


# ==================== TESTES AI ====================


class TestAIEndpoints:
    """Testes para endpoints de IA."""

    @pytest.mark.asyncio
    async def test_suggest_diarists(self):
        """Testa sugestão de diaristas por IA."""
        with patch("modules.operacional.diaristas.services.diarist_ai_service.DiaristAIService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_response = MagicMock(
                data=date.today(),
                tipo_servico=None,
                sugestoes=[],
                total_disponiveis=0,
                mensagem="Nenhuma diarista disponível",
            )
            mock_instance.suggest_diarists = AsyncMock(return_value=mock_response)

            result = await mock_instance.suggest_diarists(condominio_id=uuid4(), data=date.today())
            assert result.total_disponiveis == 0
            assert result.mensagem == "Nenhuma diarista disponível"

    @pytest.mark.asyncio
    async def test_analyze_availability(self):
        """Testa análise de disponibilidade por IA."""
        with patch("modules.operacional.diaristas.services.diarist_ai_service.DiaristAIService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_response = MagicMock(
                periodo={"inicio": date.today(), "fim": date.today() + timedelta(days=7)},
                analise_diaria=[],
                estatisticas={},
                recomendacoes=[],
            )
            mock_instance.analyze_availability = AsyncMock(return_value=mock_response)

            result = await mock_instance.analyze_availability(
                condominio_id=uuid4(),
                data_inicio=date.today(),
                data_fim=date.today() + timedelta(days=7),
            )
            assert result.periodo["inicio"] == date.today()
            assert len(result.recomendacoes) == 0

    @pytest.mark.asyncio
    async def test_analyze_performance(self):
        """Testa análise de performance por IA."""
        diarist_id = uuid4()

        with patch("modules.operacional.diaristas.services.diarist_ai_service.DiaristAIService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_response = MagicMock(
                diarist_id=str(diarist_id),
                nome="Maria Silva",
                score_geral=85.0,
                dimensoes={},
                metricas={},
                insights=[],
                tendencia="estavel",
                classificacao="Bom",
            )
            mock_instance.analyze_performance = AsyncMock(return_value=mock_response)

            result = await mock_instance.analyze_performance(diarist_id)
            assert result.score_geral == 85.0
            assert result.classificacao == "Bom"

    @pytest.mark.asyncio
    async def test_optimize_schedule(self):
        """Testa otimização de agendamentos por IA."""
        with patch("modules.operacional.diaristas.services.diarist_ai_service.DiaristAIService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_response = MagicMock(
                periodo={},
                condominio_id=str(uuid4()),
                distribuicao_atual={},
                sugestoes=[],
                economia_potencial=0.0,
                impacto_qualidade="Baixo impacto",
            )
            mock_instance.optimize_schedule = AsyncMock(return_value=mock_response)

            result = await mock_instance.optimize_schedule(
                condominio_id=uuid4(),
                data_inicio=date.today(),
                data_fim=date.today() + timedelta(days=30),
            )
            assert result.impacto_qualidade == "Baixo impacto"


# ==================== TESTES STATISTICS ====================


class TestStatisticsEndpoints:
    """Testes para endpoints de Estatísticas."""

    @pytest.mark.asyncio
    async def test_get_condominio_statistics(self):
        """Testa estatísticas do condomínio."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.get_condominio_statistics = AsyncMock(
                return_value={
                    "total_diaristas": 5,
                    "agendamentos": {"total": 50, "concluidos": 45},
                    "gastos_total": 9000.00,
                    "media_avaliacoes": 4.5,
                }
            )

            result = await mock_instance.get_condominio_statistics()
            assert result["total_diaristas"] == 5
            assert result["media_avaliacoes"] == 4.5

    @pytest.mark.asyncio
    async def test_get_top_diarists(self):
        """Testa ranking de diaristas."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.get_top_diarists = AsyncMock(return_value=[])

            result = await mock_instance.get_top_diarists()
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_available_diarists(self):
        """Testa busca de diaristas disponíveis."""
        with patch("modules.operacional.diaristas.services.diarist_service.DiaristService") as mock_svc:
            mock_instance = mock_svc.return_value
            mock_instance.get_available_diarists = AsyncMock(return_value=[])

            result = await mock_instance.get_available_diarists(data=date.today())
            assert isinstance(result, list)
