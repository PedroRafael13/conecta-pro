"""Testes de API para endpoints de Diaristas."""

from datetime import date, time, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from modules.operacional.diaristas.models.diarist import (
    Diarist,
    DiaristAssignment,
    DiaristSchedule,
    DiaristPayment,
    DiaristEvaluation,
    DiaristStatus,
    DiaristType,
    AssignmentStatus,
    ScheduleStatus,
    PaymentStatus,
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
        dias_disponiveis=[Weekday.MONDAY, Weekday.WEDNESDAY],
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
        tipo="CONDOMINIO",
        data_inicio=date.today(),
        recorrencia="SEMANAL",
        dias_semana=[Weekday.MONDAY],
        status=AssignmentStatus.ATIVO,
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


class TestDiaristEndpoints:
    """Testes para endpoints de Diaristas."""

    @pytest.mark.asyncio
    async def test_create_diarist_success(self, async_client: AsyncClient, admin_token):
        """Testa criação de diarista com sucesso."""
        payload = {
            "nome": "Ana Costa",
            "cpf": "111.222.333-44",
            "telefone": "11888888888",
            "email": "ana@email.com",
            "tipos_servico": ["LIMPEZA", "FAXINA"],
            "dias_disponiveis": ["MONDAY", "WEDNESDAY", "FRIDAY"],
            "hora_inicio_disponivel": "08:00:00",
            "hora_fim_disponivel": "17:00:00",
            "valor_hora": 25.00,
            "valor_diaria": 180.00,
        }

        with patch("modules.diarists.services.diarist_service.DiaristService.create_diarist") as mock:
            mock.return_value = MagicMock(
                id=uuid4(),
                **payload,
                status=DiaristStatus.PENDENTE,
            )

            response = await async_client.post(
                "/api/v1/diarists/",
                json=payload,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nome"] == "Ana Costa"

    @pytest.mark.asyncio
    async def test_create_diarist_duplicate_cpf(self, async_client: AsyncClient, admin_token):
        """Testa erro ao criar diarista com CPF duplicado."""
        payload = {
            "nome": "Ana Costa",
            "cpf": "123.456.789-00",
            "telefone": "11888888888",
        }

        with patch(
            "modules.diarists.services.diarist_service.DiaristService.create_diarist"
        ) as mock:
            mock.side_effect = ValueError("CPF 123.456.789-00 já cadastrado")

            response = await async_client.post(
                "/api/v1/diarists/",
                json=payload,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_list_diarists(self, async_client: AsyncClient, user_token, mock_diarist):
        """Testa listagem de diaristas."""
        with patch(
            "modules.diarists.services.diarist_service.DiaristService.list_diarists"
        ) as mock:
            mock.return_value = [mock_diarist]

            response = await async_client.get(
                "/api/v1/diarists/",
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 0

    @pytest.mark.asyncio
    async def test_list_diarists_with_filters(
        self, async_client: AsyncClient, user_token, mock_diarist
    ):
        """Testa listagem de diaristas com filtros."""
        with patch(
            "modules.diarists.services.diarist_service.DiaristService.list_diarists"
        ) as mock:
            mock.return_value = [mock_diarist]

            response = await async_client.get(
                "/api/v1/diarists/",
                params={
                    "status": "ATIVO",
                    "tipo": "LIMPEZA",
                    "search": "Maria",
                },
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_get_diarist_by_id(
        self, async_client: AsyncClient, user_token, mock_diarist
    ):
        """Testa busca de diarista por ID."""
        with patch(
            "modules.diarists.services.diarist_service.DiaristService.get_diarist"
        ) as mock:
            mock.return_value = mock_diarist

            response = await async_client.get(
                f"/api/v1/diarists/{mock_diarist.id}",
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nome"] == mock_diarist.nome

    @pytest.mark.asyncio
    async def test_get_diarist_not_found(self, async_client: AsyncClient, user_token):
        """Testa busca de diarista inexistente."""
        with patch(
            "modules.diarists.services.diarist_service.DiaristService.get_diarist"
        ) as mock:
            mock.return_value = None

            response = await async_client.get(
                f"/api/v1/diarists/{uuid4()}",
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_diarist(
        self, async_client: AsyncClient, admin_token, mock_diarist
    ):
        """Testa atualização de diarista."""
        update_data = {"telefone": "11777777777", "valor_hora": 30.00}

        with patch(
            "modules.diarists.services.diarist_service.DiaristService.update_diarist"
        ) as mock:
            mock_diarist.telefone = update_data["telefone"]
            mock_diarist.valor_hora = Decimal(str(update_data["valor_hora"]))
            mock.return_value = mock_diarist

            response = await async_client.put(
                f"/api/v1/diarists/{mock_diarist.id}",
                json=update_data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_activate_diarist(
        self, async_client: AsyncClient, admin_token, mock_diarist
    ):
        """Testa ativação de diarista."""
        with patch(
            "modules.diarists.services.diarist_service.DiaristService.activate_diarist"
        ) as mock:
            mock_diarist.status = DiaristStatus.ATIVO
            mock.return_value = mock_diarist

            response = await async_client.post(
                f"/api/v1/diarists/{mock_diarist.id}/activate",
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_delete_diarist(self, async_client: AsyncClient, admin_token):
        """Testa remoção de diarista."""
        diarist_id = uuid4()

        with patch(
            "modules.diarists.services.diarist_service.DiaristService.delete_diarist"
        ) as mock:
            mock.return_value = True

            response = await async_client.delete(
                f"/api/v1/diarists/{diarist_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestScheduleEndpoints:
    """Testes para endpoints de Agendamentos."""

    @pytest.mark.asyncio
    async def test_create_schedule(
        self, async_client: AsyncClient, admin_token, mock_schedule
    ):
        """Testa criação de agendamento."""
        payload = {
            "diarist_id": str(uuid4()),
            "condominio_id": str(uuid4()),
            "data_trabalho": str(date.today() + timedelta(days=1)),
            "hora_inicio": "08:00:00",
            "hora_fim": "16:00:00",
            "valor_previsto": 180.00,
        }

        with patch(
            "modules.diarists.services.diarist_service.DiaristService.create_schedule"
        ) as mock:
            mock.return_value = mock_schedule

            response = await async_client.post(
                "/api/v1/diarists/schedules",
                json=payload,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_list_schedules(
        self, async_client: AsyncClient, user_token, mock_schedule
    ):
        """Testa listagem de agendamentos."""
        with patch(
            "modules.diarists.services.diarist_service.DiaristService.list_schedules"
        ) as mock:
            mock.return_value = [mock_schedule]

            response = await async_client.get(
                "/api/v1/diarists/schedules",
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_get_today_schedules(
        self, async_client: AsyncClient, user_token, mock_schedule
    ):
        """Testa busca de agendamentos de hoje."""
        with patch(
            "modules.diarists.services.diarist_service.DiaristService.get_today_schedules"
        ) as mock:
            mock.return_value = [mock_schedule]

            response = await async_client.get(
                "/api/v1/diarists/schedules/today",
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_confirm_schedule(
        self, async_client: AsyncClient, admin_token, mock_schedule
    ):
        """Testa confirmação de agendamento."""
        with patch(
            "modules.diarists.services.diarist_service.DiaristService.confirm_schedule"
        ) as mock:
            mock_schedule.status = ScheduleStatus.CONFIRMADO
            mock.return_value = mock_schedule

            response = await async_client.post(
                f"/api/v1/diarists/schedules/{mock_schedule.id}/confirm",
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_register_checkin(self, async_client: AsyncClient, admin_token, mock_schedule):
        """Testa registro de check-in."""
        payload = {
            "schedule_id": str(mock_schedule.id),
            "hora_checkin": "2025-01-01T08:05:00",
            "latitude": -23.5505,
            "longitude": -46.6333,
        }

        with patch(
            "modules.diarists.services.diarist_service.DiaristService.register_checkin"
        ) as mock:
            mock_schedule.status = ScheduleStatus.EM_ANDAMENTO
            mock.return_value = mock_schedule

            response = await async_client.post(
                "/api/v1/diarists/schedules/checkin",
                json=payload,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_register_checkout(
        self, async_client: AsyncClient, admin_token, mock_schedule
    ):
        """Testa registro de check-out."""
        payload = {
            "schedule_id": str(mock_schedule.id),
            "hora_checkout": "2025-01-01T16:10:00",
        }

        with patch(
            "modules.diarists.services.diarist_service.DiaristService.register_checkout"
        ) as mock:
            mock_schedule.status = ScheduleStatus.CONCLUIDO
            mock.return_value = mock_schedule

            response = await async_client.post(
                "/api/v1/diarists/schedules/checkout",
                json=payload,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == status.HTTP_200_OK


class TestPaymentEndpoints:
    """Testes para endpoints de Pagamentos."""

    @pytest.mark.asyncio
    async def test_create_payment(self, async_client: AsyncClient, admin_token):
        """Testa criação de pagamento."""
        diarist_id = uuid4()
        condominio_id = uuid4()

        payload = {
            "diarist_id": str(diarist_id),
            "condominio_id": str(condominio_id),
            "data_referencia": str(date.today()),
            "data_vencimento": str(date.today() + timedelta(days=5)),
            "valor_bruto": 500.00,
            "retencao_inss": 55.00,
            "forma_pagamento": "PIX",
        }

        mock_payment = DiaristPayment(
            id=uuid4(),
            diarist_id=diarist_id,
            condominio_id=condominio_id,
            data_referencia=date.today(),
            valor_bruto=Decimal("500.00"),
            valor_liquido=Decimal("445.00"),
            status=PaymentStatus.PENDENTE,
        )

        with patch(
            "modules.diarists.services.diarist_service.DiaristService.create_payment"
        ) as mock:
            mock.return_value = mock_payment

            response = await async_client.post(
                "/api/v1/diarists/payments",
                json=payload,
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_list_pending_payments(self, async_client: AsyncClient, user_token):
        """Testa listagem de pagamentos pendentes."""
        with patch(
            "modules.diarists.services.diarist_service.DiaristService.get_pending_payments"
        ) as mock:
            mock.return_value = []

            response = await async_client.get(
                "/api/v1/diarists/payments/pending",
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_process_payment(self, async_client: AsyncClient, admin_token):
        """Testa processamento de pagamento."""
        payment_id = uuid4()

        mock_payment = DiaristPayment(
            id=payment_id,
            diarist_id=uuid4(),
            condominio_id=uuid4(),
            data_referencia=date.today(),
            valor_bruto=Decimal("500.00"),
            valor_liquido=Decimal("445.00"),
            status=PaymentStatus.PAGO,
            data_pagamento=date.today(),
        )

        with patch(
            "modules.diarists.services.diarist_service.DiaristService.process_payment"
        ) as mock:
            mock.return_value = mock_payment

            response = await async_client.post(
                f"/api/v1/diarists/payments/{payment_id}/process",
                params={"data_pagamento": str(date.today())},
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == status.HTTP_200_OK


class TestEvaluationEndpoints:
    """Testes para endpoints de Avaliações."""

    @pytest.mark.asyncio
    async def test_create_evaluation(self, async_client: AsyncClient, user_token):
        """Testa criação de avaliação."""
        schedule_id = uuid4()
        diarist_id = uuid4()

        payload = {
            "schedule_id": str(schedule_id),
            "avaliador_id": str(uuid4()),
            "nota_geral": 5,
            "nota_pontualidade": 5,
            "nota_qualidade": 4,
            "nota_comportamento": 5,
            "nota_comunicacao": 4,
            "comentario": "Excelente trabalho!",
            "recomendaria": True,
        }

        mock_evaluation = DiaristEvaluation(
            id=uuid4(),
            diarist_id=diarist_id,
            schedule_id=schedule_id,
            nota_geral=5,
        )

        with patch(
            "modules.diarists.services.diarist_service.DiaristService.create_evaluation"
        ) as mock:
            mock.return_value = mock_evaluation

            response = await async_client.post(
                "/api/v1/diarists/evaluations",
                json=payload,
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_list_evaluations(self, async_client: AsyncClient, user_token):
        """Testa listagem de avaliações."""
        with patch(
            "modules.diarists.services.diarist_service.DiaristService.list_evaluations"
        ) as mock:
            mock.return_value = []

            response = await async_client.get(
                "/api/v1/diarists/evaluations",
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK


class TestAIEndpoints:
    """Testes para endpoints de IA."""

    @pytest.mark.asyncio
    async def test_suggest_diarists(self, async_client: AsyncClient, user_token):
        """Testa sugestão de diaristas por IA."""
        with patch(
            "modules.diarists.services.diarist_ai_service.DiaristAIService.suggest_diarists"
        ) as mock:
            mock.return_value = MagicMock(
                data=date.today(),
                tipo_servico=None,
                sugestoes=[],
                total_disponiveis=0,
                mensagem="Nenhuma diarista disponível",
            )

            response = await async_client.get(
                "/api/v1/diarists/ai/suggest",
                params={
                    "condominio_id": str(uuid4()),
                    "data": str(date.today()),
                },
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_analyze_availability(self, async_client: AsyncClient, user_token):
        """Testa análise de disponibilidade por IA."""
        with patch(
            "modules.diarists.services.diarist_ai_service.DiaristAIService.analyze_availability"
        ) as mock:
            mock.return_value = MagicMock(
                periodo={"inicio": date.today(), "fim": date.today() + timedelta(days=7)},
                analise_diaria=[],
                estatisticas={},
                recomendacoes=[],
            )

            response = await async_client.get(
                "/api/v1/diarists/ai/availability",
                params={
                    "condominio_id": str(uuid4()),
                    "data_inicio": str(date.today()),
                    "data_fim": str(date.today() + timedelta(days=7)),
                },
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_analyze_performance(self, async_client: AsyncClient, user_token):
        """Testa análise de performance por IA."""
        diarist_id = uuid4()

        with patch(
            "modules.diarists.services.diarist_ai_service.DiaristAIService.analyze_performance"
        ) as mock:
            mock.return_value = MagicMock(
                diarist_id=str(diarist_id),
                nome="Maria Silva",
                score_geral=85.0,
                dimensoes={},
                metricas={},
                insights=[],
                tendencia="estavel",
                classificacao="Bom",
            )

            response = await async_client.get(
                f"/api/v1/diarists/ai/performance/{diarist_id}",
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_optimize_schedule(self, async_client: AsyncClient, user_token):
        """Testa otimização de agendamentos por IA."""
        with patch(
            "modules.diarists.services.diarist_ai_service.DiaristAIService.optimize_schedule"
        ) as mock:
            mock.return_value = MagicMock(
                periodo={},
                condominio_id=str(uuid4()),
                distribuicao_atual={},
                sugestoes=[],
                economia_potencial=0.0,
                impacto_qualidade="Baixo impacto",
            )

            response = await async_client.get(
                "/api/v1/diarists/ai/optimize",
                params={
                    "condominio_id": str(uuid4()),
                    "data_inicio": str(date.today()),
                    "data_fim": str(date.today() + timedelta(days=30)),
                },
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK


class TestStatisticsEndpoints:
    """Testes para endpoints de Estatísticas."""

    @pytest.mark.asyncio
    async def test_get_condominio_statistics(self, async_client: AsyncClient, user_token):
        """Testa estatísticas do condomínio."""
        condominio_id = uuid4()

        with patch(
            "modules.diarists.services.diarist_service.DiaristService.get_condominio_statistics"
        ) as mock:
            mock.return_value = {
                "total_diaristas": 5,
                "agendamentos": {"total": 50, "concluidos": 45},
                "gastos_total": 9000.00,
                "media_avaliacoes": 4.5,
            }

            response = await async_client.get(
                f"/api/v1/diarists/statistics/condominio/{condominio_id}",
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_get_top_diarists(self, async_client: AsyncClient, user_token):
        """Testa ranking de diaristas."""
        with patch(
            "modules.diarists.services.diarist_service.DiaristService.get_top_diarists"
        ) as mock:
            mock.return_value = []

            response = await async_client.get(
                "/api/v1/diarists/statistics/ranking",
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_get_available_diarists(self, async_client: AsyncClient, user_token):
        """Testa busca de diaristas disponíveis."""
        with patch(
            "modules.diarists.services.diarist_service.DiaristService.get_available_diarists"
        ) as mock:
            mock.return_value = []

            response = await async_client.get(
                "/api/v1/diarists/available",
                params={"data": str(date.today())},
                headers={"Authorization": f"Bearer {user_token}"},
            )

        assert response.status_code == status.HTTP_200_OK
