"""
tests/domains/operacional/test_time_bank_service.py
Testes unitarios para TimeBankService.
"""

import sys
from datetime import date, timedelta

import pytest

sys.path.insert(0, "/opt/conecta-pro/backend")

from modules.operacional.services.time_bank_service import TimeBankService


@pytest.fixture
def service():
    """Instancia do TimeBankService."""
    return TimeBankService()


class TestTimeBankOvertimeCalculation:
    """Testes para calculo de horas extras."""

    def test_no_overtime_exact_hours(self, service):
        result = service.calculate_overtime_hours(8.0, 8.0)
        assert result["overtime_hours"] == 0.0
        assert result["normal_hours"] == 8.0
        assert result["negative_hours"] == 0.0

    def test_overtime_one_hour(self, service):
        result = service.calculate_overtime_hours(9.0, 8.0)
        assert result["overtime_hours"] == 1.0
        assert result["normal_hours"] == 8.0

    def test_overtime_capped_at_two_hours(self, service):
        """CLT limita a 2h extras por dia."""
        result = service.calculate_overtime_hours(12.0, 8.0)
        assert result["overtime_hours"] == 2.0

    def test_negative_hours_when_underworked(self, service):
        result = service.calculate_overtime_hours(6.0, 8.0)
        assert result["negative_hours"] == 2.0
        assert result["overtime_hours"] == 0.0
        assert result["normal_hours"] == 6.0

    def test_break_deducted(self, service):
        result = service.calculate_overtime_hours(9.0, 8.0, break_minutes=60)
        assert result["worked_hours"] == 8.0
        assert result["overtime_hours"] == 0.0

    def test_night_shift_all_hours_nocturnal(self, service):
        result = service.calculate_overtime_hours(8.0, 8.0, is_night_shift=True)
        assert result["night_hours"] == 8.0

    def test_day_shift_no_nocturnal(self, service):
        result = service.calculate_overtime_hours(8.0, 8.0, is_night_shift=False)
        assert result["night_hours"] == 0.0

    def test_zero_hours_worked(self, service):
        result = service.calculate_overtime_hours(0.0, 8.0)
        assert result["normal_hours"] == 0.0
        assert result["negative_hours"] == 8.0

    def test_rounding(self, service):
        result = service.calculate_overtime_hours(8.333, 8.0)
        assert result["overtime_hours"] == 0.33


class TestTimeBankCompensationValue:
    """Testes para calculo de valor monetario."""

    def test_base_value(self, service):
        result = service.calculate_compensation_value(8.0, 25.0)
        assert result["base_value"] == 200.0
        assert result["total_value"] == 200.0

    def test_night_bonus_20_percent(self, service):
        result = service.calculate_compensation_value(8.0, 25.0, is_night=True)
        assert result["night_bonus"] == 40.0  # 200 * 0.20
        assert result["total_value"] == 240.0

    def test_overtime_bonus_50_percent(self, service):
        result = service.calculate_compensation_value(2.0, 25.0, is_overtime=True)
        assert result["overtime_bonus"] == 25.0  # 50 * 0.50
        assert result["total_value"] == 75.0

    def test_sunday_bonus_100_percent(self, service):
        result = service.calculate_compensation_value(8.0, 25.0, is_sunday=True)
        assert result["sunday_bonus"] == 200.0  # 200 * 1.00
        assert result["total_value"] == 400.0

    def test_holiday_bonus_100_percent(self, service):
        result = service.calculate_compensation_value(8.0, 25.0, is_holiday=True)
        assert result["holiday_bonus"] == 200.0
        assert result["total_value"] == 400.0

    def test_all_bonuses_combined(self, service):
        result = service.calculate_compensation_value(
            8.0,
            25.0,
            is_overtime=True,
            is_night=True,
            is_sunday=True,
            is_holiday=True,
        )
        base = 200.0
        expected = base + (base * 0.20) + (base * 0.50) + (base * 1.0) + (base * 1.0)
        assert result["total_value"] == expected

    def test_zero_hours(self, service):
        result = service.calculate_compensation_value(0.0, 25.0)
        assert result["base_value"] == 0.0
        assert result["total_value"] == 0.0

    def test_zero_rate(self, service):
        result = service.calculate_compensation_value(8.0, 0.0)
        assert result["total_value"] == 0.0


class TestTimeBankExpiration:
    """Testes para calculo de data de expiracao."""

    def test_individual_agreement_180_days(self, service):
        ref = date(2026, 1, 1)
        exp = service.get_expiration_date(ref)
        assert exp == date(2026, 1, 1) + timedelta(days=180)

    def test_collective_agreement_365_days(self, service):
        ref = date(2026, 1, 1)
        exp = service.get_expiration_date(ref, has_collective_agreement=True)
        assert exp == date(2026, 1, 1) + timedelta(days=365)


class TestTimeBankExpirationAlerts:
    """Testes para alertas de expiracao."""

    def test_expired_entry_critical(self, service):
        yesterday = date.today() - timedelta(days=1)
        entries = [{"id": "1", "employee_id": "emp1", "hours": 4, "expiration_date": yesterday}]
        alerts = service.check_expiration_alerts(entries)
        assert len(alerts) == 1
        assert alerts[0]["status"] == "expired"
        assert alerts[0]["severity"] == "critical"

    def test_expiring_soon_warning(self, service):
        soon = date.today() + timedelta(days=15)
        entries = [{"id": "2", "employee_id": "emp2", "hours": 8, "expiration_date": soon}]
        alerts = service.check_expiration_alerts(entries)
        assert len(alerts) == 1
        assert alerts[0]["status"] == "expiring_soon"
        assert alerts[0]["severity"] == "medium"

    def test_no_alert_for_far_future(self, service):
        far = date.today() + timedelta(days=90)
        entries = [{"id": "3", "employee_id": "emp3", "hours": 6, "expiration_date": far}]
        alerts = service.check_expiration_alerts(entries)
        assert len(alerts) == 0

    def test_no_alert_without_expiration(self, service):
        entries = [{"id": "4", "employee_id": "emp4", "hours": 2}]
        alerts = service.check_expiration_alerts(entries)
        assert len(alerts) == 0

    def test_string_date_parsing(self, service):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        entries = [{"id": "5", "employee_id": "emp5", "hours": 3, "expiration_date": yesterday}]
        alerts = service.check_expiration_alerts(entries)
        assert len(alerts) == 1

    def test_multiple_entries_mixed(self, service):
        entries = [
            {"id": "1", "hours": 4, "expiration_date": date.today() - timedelta(days=5)},
            {"id": "2", "hours": 8, "expiration_date": date.today() + timedelta(days=10)},
            {"id": "3", "hours": 6, "expiration_date": date.today() + timedelta(days=60)},
            {"id": "4", "hours": 2},
        ]
        alerts = service.check_expiration_alerts(entries)
        assert len(alerts) == 2  # 1 expired, 1 expiring_soon


class TestTimeBankConstants:
    """Testes para constantes CLT."""

    def test_max_daily_overtime(self):
        assert TimeBankService.MAX_DAILY_OVERTIME_HOURS == 2.0

    def test_default_expiration(self):
        assert TimeBankService.DEFAULT_EXPIRATION_DAYS == 180

    def test_collective_expiration(self):
        assert TimeBankService.COLLECTIVE_AGREEMENT_EXPIRATION_DAYS == 365

    def test_warn_days(self):
        assert TimeBankService.WARN_EXPIRATION_DAYS == 30
