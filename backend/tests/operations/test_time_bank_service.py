"""
Testes para o serviço TimeBankService (Banco de Horas).
"""

from datetime import date, timedelta

import pytest

from modules.operacional.services.time_bank_service import TimeBankService, time_bank_service


class TestTimeBankService:
    """Testes para o serviço de banco de horas."""

    @pytest.fixture
    def service(self):
        """Retorna instância do serviço."""
        return TimeBankService()

    def test_service_singleton(self):
        """Verifica que time_bank_service é singleton."""
        assert time_bank_service is not None
        assert isinstance(time_bank_service, TimeBankService)

    def test_constants(self, service):
        """Verifica constantes CLT."""
        assert service.MAX_DAILY_OVERTIME_HOURS == 2.0
        assert service.DEFAULT_EXPIRATION_DAYS == 180
        assert service.COLLECTIVE_AGREEMENT_EXPIRATION_DAYS == 365
        assert service.WARN_EXPIRATION_DAYS == 30


class TestOvertimeCalculation:
    """Testes para cálculo de horas extras."""

    @pytest.fixture
    def service(self):
        return TimeBankService()

    def test_no_overtime(self, service):
        """Testa turno sem hora extra."""
        result = service.calculate_overtime_hours(
            actual_hours=8.0,
            planned_hours=8.0,
            is_night_shift=False,
            break_minutes=0,
        )

        assert result["worked_hours"] == 8.0
        assert result["normal_hours"] == 8.0
        assert result["overtime_hours"] == 0.0
        assert result["negative_hours"] == 0.0

    def test_with_overtime(self, service):
        """Testa turno com hora extra."""
        result = service.calculate_overtime_hours(
            actual_hours=10.0,
            planned_hours=8.0,
            is_night_shift=False,
            break_minutes=0,
        )

        assert result["worked_hours"] == 10.0
        assert result["normal_hours"] == 8.0
        assert result["overtime_hours"] == 2.0  # Limite CLT
        assert result["negative_hours"] == 0.0

    def test_overtime_exceeds_limit(self, service):
        """Testa hora extra excedendo limite CLT (2h)."""
        result = service.calculate_overtime_hours(
            actual_hours=12.0,
            planned_hours=8.0,
            is_night_shift=False,
            break_minutes=0,
        )

        # Limite de 2h de hora extra por dia
        assert result["overtime_hours"] == 2.0
        # Total trabalhado continua sendo 12h
        assert result["worked_hours"] == 12.0

    def test_negative_hours(self, service):
        """Testa horas negativas (falta parcial)."""
        result = service.calculate_overtime_hours(
            actual_hours=6.0,
            planned_hours=8.0,
            is_night_shift=False,
            break_minutes=0,
        )

        assert result["worked_hours"] == 6.0
        assert result["normal_hours"] == 6.0
        assert result["overtime_hours"] == 0.0
        assert result["negative_hours"] == 2.0

    def test_night_shift(self, service):
        """Testa turno noturno."""
        result = service.calculate_overtime_hours(
            actual_hours=8.0,
            planned_hours=8.0,
            is_night_shift=True,
            break_minutes=0,
        )

        assert result["night_hours"] == 8.0

    def test_with_break(self, service):
        """Testa desconto de intervalo."""
        result = service.calculate_overtime_hours(
            actual_hours=9.0,
            planned_hours=8.0,
            is_night_shift=False,
            break_minutes=60,
        )

        # 9h - 1h intervalo = 8h trabalhadas
        assert result["worked_hours"] == 8.0
        assert result["overtime_hours"] == 0.0


class TestCompensationValue:
    """Testes para cálculo de valor de horas."""

    @pytest.fixture
    def service(self):
        return TimeBankService()

    def test_base_value(self, service):
        """Testa cálculo do valor base."""
        result = service.calculate_compensation_value(
            hours=8.0,
            hourly_rate=25.0,
            is_overtime=False,
            is_night=False,
            is_sunday=False,
            is_holiday=False,
        )

        assert result["base_value"] == 200.0  # 8h * R$25
        assert result["total_value"] == 200.0

    def test_overtime_bonus(self, service):
        """Testa adicional de hora extra (50% CLT)."""
        result = service.calculate_compensation_value(
            hours=2.0,
            hourly_rate=25.0,
            is_overtime=True,
            is_night=False,
            is_sunday=False,
            is_holiday=False,
        )

        base = 50.0  # 2h * R$25
        overtime_bonus = 25.0  # 50% de R$50
        assert result["base_value"] == base
        assert result["overtime_bonus"] == overtime_bonus
        assert result["total_value"] == 75.0

    def test_night_bonus(self, service):
        """Testa adicional noturno (20% CLT)."""
        result = service.calculate_compensation_value(
            hours=8.0,
            hourly_rate=25.0,
            is_overtime=False,
            is_night=True,
            is_sunday=False,
            is_holiday=False,
        )

        base = 200.0
        night_bonus = 40.0  # 20% de R$200
        assert result["night_bonus"] == night_bonus
        assert result["total_value"] == 240.0

    def test_sunday_bonus(self, service):
        """Testa adicional de domingo (100% CLT)."""
        result = service.calculate_compensation_value(
            hours=8.0,
            hourly_rate=25.0,
            is_overtime=False,
            is_night=False,
            is_sunday=True,
            is_holiday=False,
        )

        base = 200.0
        sunday_bonus = 200.0  # 100% de R$200
        assert result["sunday_bonus"] == sunday_bonus
        assert result["total_value"] == 400.0

    def test_holiday_bonus(self, service):
        """Testa adicional de feriado (100% CLT)."""
        result = service.calculate_compensation_value(
            hours=8.0,
            hourly_rate=25.0,
            is_overtime=False,
            is_night=False,
            is_sunday=False,
            is_holiday=True,
        )

        base = 200.0
        holiday_bonus = 200.0
        assert result["holiday_bonus"] == holiday_bonus
        assert result["total_value"] == 400.0

    def test_combined_bonuses(self, service):
        """Testa combinação de adicionais."""
        result = service.calculate_compensation_value(
            hours=2.0,
            hourly_rate=25.0,
            is_overtime=True,
            is_night=True,
            is_sunday=False,
            is_holiday=True,
        )

        base = 50.0  # 2h * R$25
        night_bonus = 10.0  # 20% de 50
        overtime_bonus = 25.0  # 50% de 50
        holiday_bonus = 50.0  # 100% de 50
        total = base + night_bonus + overtime_bonus + holiday_bonus
        assert result["total_value"] == total


class TestExpiration:
    """Testes para expiração de horas."""

    @pytest.fixture
    def service(self):
        return TimeBankService()

    def test_default_expiration(self, service):
        """Testa expiração padrão (6 meses)."""
        ref_date = date(2025, 1, 15)
        exp_date = service.get_expiration_date(ref_date)

        expected = ref_date + timedelta(days=180)
        assert exp_date == expected

    def test_collective_agreement_expiration(self, service):
        """Testa expiração com acordo coletivo (1 ano)."""
        ref_date = date(2025, 1, 15)
        exp_date = service.get_expiration_date(ref_date, has_collective_agreement=True)

        expected = ref_date + timedelta(days=365)
        assert exp_date == expected

    def test_expiration_alerts_expired(self, service):
        """Testa alerta de horas expiradas."""
        entries = [
            {
                "id": "1",
                "employee_id": "emp-1",
                "hours": 10.0,
                "expiration_date": date.today() - timedelta(days=1),
            }
        ]

        alerts = service.check_expiration_alerts(entries)

        assert len(alerts) == 1
        assert alerts[0]["status"] == "expired"
        assert alerts[0]["severity"] == "critical"

    def test_expiration_alerts_expiring_soon(self, service):
        """Testa alerta de horas expirando em breve."""
        entries = [
            {
                "id": "1",
                "employee_id": "emp-1",
                "hours": 10.0,
                "expiration_date": date.today() + timedelta(days=15),
            }
        ]

        alerts = service.check_expiration_alerts(entries)

        assert len(alerts) == 1
        assert alerts[0]["status"] == "expiring_soon"
        assert alerts[0]["days_left"] == 15

    def test_no_alerts_for_valid_entries(self, service):
        """Testa que não há alertas para entradas válidas."""
        entries = [
            {
                "id": "1",
                "employee_id": "emp-1",
                "hours": 10.0,
                "expiration_date": date.today() + timedelta(days=90),
            }
        ]

        alerts = service.check_expiration_alerts(entries)

        assert len(alerts) == 0


class TestCompensationValidation:
    """Testes para validação de compensação."""

    @pytest.fixture
    def service(self):
        return TimeBankService()

    def test_valid_compensation(self, service):
        """Testa compensação válida."""
        result = service.validate_compensation_request(
            employee_balance=20.0,
            requested_hours=8.0,
            compensation_date=date.today() + timedelta(days=7),
        )

        assert result["is_valid"]
        assert len(result["errors"]) == 0
        assert result["balance_after"] == 12.0

    def test_insufficient_balance(self, service):
        """Testa compensação com saldo insuficiente."""
        result = service.validate_compensation_request(
            employee_balance=5.0,
            requested_hours=8.0,
            compensation_date=date.today() + timedelta(days=7),
        )

        assert not result["is_valid"]
        assert any("insuficiente" in e.lower() for e in result["errors"])

    def test_past_date(self, service):
        """Testa compensação com data no passado."""
        result = service.validate_compensation_request(
            employee_balance=20.0,
            requested_hours=8.0,
            compensation_date=date.today() - timedelta(days=1),
        )

        assert not result["is_valid"]
        assert any("passado" in e.lower() for e in result["errors"])

    def test_weekend_warning(self, service):
        """Testa aviso para compensação no fim de semana."""
        # Encontrar próximo sábado
        today = date.today()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        saturday = today + timedelta(days=days_until_saturday)

        result = service.validate_compensation_request(
            employee_balance=20.0,
            requested_hours=8.0,
            compensation_date=saturday,
        )

        assert result["is_valid"]  # Válido, mas com aviso
        assert any("fim de semana" in w.lower() for w in result["warnings"])


class TestMonthlySummary:
    """Testes para resumo mensal."""

    @pytest.fixture
    def service(self):
        return TimeBankService()

    def test_monthly_summary(self, service):
        """Testa cálculo de resumo mensal."""
        entries = [
            {"id": "1", "entry_type": "credit", "hours": 10.0, "reference_date": "2025-01-05"},
            {"id": "2", "entry_type": "credit", "hours": 5.0, "reference_date": "2025-01-10"},
            {"id": "3", "entry_type": "debit", "hours": 3.0, "reference_date": "2025-01-15"},
            {"id": "4", "entry_type": "compensation", "hours": 4.0, "reference_date": "2025-01-20"},
            {"id": "5", "entry_type": "credit", "hours": 8.0, "reference_date": "2025-02-01"},  # Outro mês
        ]

        summary = service.calculate_monthly_summary(entries, month=1, year=2025)

        assert summary["month"] == 1
        assert summary["year"] == 2025
        assert summary["entries_count"] == 4
        assert summary["total_credits"] == 15.0
        assert summary["total_debits"] == 3.0
        assert summary["total_compensations"] == 4.0
        assert summary["net_balance"] == 8.0  # 15 - 3 - 4


class TestRecommendations:
    """Testes para recomendações."""

    @pytest.fixture
    def service(self):
        return TimeBankService()

    def test_expiring_soon_recommendation(self, service):
        """Testa recomendação para horas expirando."""
        recommendations = service.get_recommendations(
            employee_balance=20.0,
            expiring_soon=10.0,
            monthly_avg_overtime=15.0,
        )

        assert any("expiram" in r.lower() for r in recommendations)

    def test_high_balance_recommendation(self, service):
        """Testa recomendação para saldo alto."""
        recommendations = service.get_recommendations(
            employee_balance=50.0,
            expiring_soon=0.0,
            monthly_avg_overtime=15.0,
        )

        assert any("elevado" in r.lower() for r in recommendations)

    def test_negative_balance_recommendation(self, service):
        """Testa recomendação para saldo negativo."""
        recommendations = service.get_recommendations(
            employee_balance=-15.0,
            expiring_soon=0.0,
            monthly_avg_overtime=15.0,
        )

        assert any("negativo" in r.lower() for r in recommendations)

    def test_high_overtime_recommendation(self, service):
        """Testa recomendação para média alta de horas extras."""
        recommendations = service.get_recommendations(
            employee_balance=10.0,
            expiring_soon=0.0,
            monthly_avg_overtime=35.0,
        )

        assert any("contratação" in r.lower() for r in recommendations)

    def test_no_recommendations(self, service):
        """Testa cenário sem recomendações."""
        recommendations = service.get_recommendations(
            employee_balance=10.0,
            expiring_soon=0.0,
            monthly_avg_overtime=15.0,
        )

        # Saldo normal, sem expiração, média normal
        assert len(recommendations) == 0
