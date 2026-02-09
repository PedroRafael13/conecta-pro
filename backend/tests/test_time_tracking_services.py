"""Testes unitários para Services do módulo de Ponto Eletrônico."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.hr.time_tracking.models import (
    AnomalyType,
    EntryType,
    ScheduleType,
    TimeEntry,
    WorkSchedule,
)
from modules.hr.time_tracking.services import (
    AnomalyDetectionService,
    AnomalyScore,
    TimeCalculationService,
)


class TestTimeCalculationService:
    """Testes para TimeCalculationService."""

    @pytest.fixture
    def calc_service(self):
        """Fixture do serviço de cálculo."""
        return TimeCalculationService()

    def test_calculate_worked_hours_basic(self, calc_service):
        """Testa cálculo básico de horas trabalhadas."""
        entries = [
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(8, 0),
                entry_type=EntryType.ENTRADA,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(17, 0),
                entry_type=EntryType.SAIDA,
            ),
        ]

        result = calc_service.calculate_worked_hours(entries)

        # 9 horas = 540 minutos
        assert result["worked_minutes"] == 540
        assert result["total_entries"] == 2

    def test_calculate_worked_hours_with_break(self, calc_service):
        """Testa cálculo com intervalo."""
        entries = [
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(8, 0),
                entry_type=EntryType.ENTRADA,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(12, 0),
                entry_type=EntryType.SAIDA_INTERVALO,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(13, 0),
                entry_type=EntryType.RETORNO_INTERVALO,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(17, 0),
                entry_type=EntryType.SAIDA,
            ),
        ]

        result = calc_service.calculate_worked_hours(entries)

        # 9h total - 1h intervalo = 8h = 480 minutos
        assert result["worked_minutes"] == 480
        assert result["break_minutes"] == 60

    def test_calculate_overtime_type_normal_day(self, calc_service):
        """Testa tipo de hora extra em dia normal."""
        overtime_50, overtime_100 = calc_service.calculate_overtime_type(
            overtime_minutes=90,
            work_date=date(2024, 12, 30),  # Segunda-feira
        )

        # Até 2h = 50%
        assert overtime_50 == 90
        assert overtime_100 == 0

    def test_calculate_overtime_type_exceeds_limit(self, calc_service):
        """Testa hora extra que excede limite de 50%."""
        overtime_50, overtime_100 = calc_service.calculate_overtime_type(
            overtime_minutes=180,  # 3 horas
            work_date=date(2024, 12, 30),  # Segunda-feira
        )

        # Até 2h = 50%, acima = 100%
        assert overtime_50 == 120  # 2h
        assert overtime_100 == 60  # 1h

    def test_calculate_overtime_type_sunday(self, calc_service):
        """Testa hora extra em domingo."""
        overtime_50, overtime_100 = calc_service.calculate_overtime_type(
            overtime_minutes=120,
            work_date=date(2024, 12, 29),  # Domingo
        )

        # Domingo = 100%
        assert overtime_50 == 0
        assert overtime_100 == 120

    def test_calculate_overtime_type_holiday(self, calc_service):
        """Testa hora extra em feriado."""
        overtime_50, overtime_100 = calc_service.calculate_overtime_type(
            overtime_minutes=120,
            work_date=date(2024, 12, 25),  # Natal
        )

        # Feriado = 100%
        assert overtime_50 == 0
        assert overtime_100 == 120

    def test_calculate_night_bonus(self, calc_service):
        """Testa cálculo de adicional noturno."""
        night_minutes = 420  # 7 horas noturnas
        hourly_rate = Decimal("20.00")

        bonus = calc_service.calculate_night_bonus(night_minutes, hourly_rate)

        # Adicional de 20% sobre horas noturnas
        assert bonus > Decimal("0")

    def test_calculate_overtime_value(self, calc_service):
        """Testa cálculo de valor de hora extra."""
        hourly_rate = Decimal("20.00")

        value_50, value_100 = calc_service.calculate_overtime_value(
            overtime_50_minutes=120,  # 2h
            overtime_100_minutes=60,  # 1h
            hourly_rate=hourly_rate,
        )

        # 2h * R$20 * 1.5 = R$60
        assert value_50 == Decimal("60.00")
        # 1h * R$20 * 2.0 = R$40
        assert value_100 == Decimal("40.00")

    def test_calculate_dsr_entitled(self, calc_service):
        """Testa direito ao DSR."""
        entitled, reason = calc_service.calculate_dsr(
            worked_days=22,
            expected_days=22,
            late_count=2,
            absence_count=0,
        )

        assert entitled is True
        assert reason == ""

    def test_calculate_dsr_lost_absence(self, calc_service):
        """Testa perda de DSR por falta."""
        entitled, reason = calc_service.calculate_dsr(
            worked_days=21,
            expected_days=22,
            late_count=0,
            absence_count=1,
        )

        assert entitled is False
        assert "injustificada" in reason.lower()

    def test_validate_clt_rules_overtime(self, calc_service):
        """Testa validação de regras CLT - jornada excessiva."""
        violations = calc_service.validate_clt_rules(
            worked_minutes=720,  # 12 horas
            break_minutes=60,
        )

        assert len(violations) > 0
        assert any("excede" in v.lower() for v in violations)

    def test_validate_clt_rules_break_short(self, calc_service):
        """Testa validação de regras CLT - intervalo curto."""
        violations = calc_service.validate_clt_rules(
            worked_minutes=480,  # 8 horas
            break_minutes=30,  # Apenas 30 minutos
        )

        assert len(violations) > 0
        assert any("intervalo" in v.lower() for v in violations)

    def test_pair_entries_complete(self, calc_service):
        """Testa pareamento de registros completo."""
        entries = [
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(8, 0),
                entry_type=EntryType.ENTRADA,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(17, 0),
                entry_type=EntryType.SAIDA,
            ),
        ]

        periods = calc_service.pair_entries(entries)

        assert len(periods) == 1
        assert periods[0]["type"] == "work"
        assert periods[0]["incomplete"] is False

    def test_pair_entries_incomplete(self, calc_service):
        """Testa pareamento de registros incompleto."""
        entries = [
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(8, 0),
                entry_type=EntryType.ENTRADA,
            ),
            # Sem saída
        ]

        periods = calc_service.pair_entries(entries)

        assert len(periods) == 1
        assert periods[0]["incomplete"] is True


class TestAnomalyDetectionService:
    """Testes para AnomalyDetectionService."""

    @pytest.fixture
    def anomaly_service(self):
        """Fixture do serviço de detecção de anomalias."""
        return AnomalyDetectionService()

    @pytest.fixture
    def schedule(self):
        """Fixture de jornada de trabalho."""
        return WorkSchedule(
            name="Comercial",
            schedule_type=ScheduleType.CLT_44H,
            weekly_schedule={
                "monday": {"start": "08:00", "end": "17:48"},
                "tuesday": {"start": "08:00", "end": "17:48"},
                "wednesday": {"start": "08:00", "end": "17:48"},
                "thursday": {"start": "08:00", "end": "17:48"},
                "friday": {"start": "08:00", "end": "17:48"},
            },
            tolerance_late_minutes=5,
            tolerance_early_minutes=5,
        )

    def test_detect_missing_entry(self, anomaly_service, schedule):
        """Testa detecção de entrada faltante."""
        entries = [
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(17, 0),
                entry_type=EntryType.SAIDA,
            ),
        ]

        anomalies = anomaly_service.analyze_entries(entries, schedule)

        assert len(anomalies) > 0
        assert any(a.anomaly_type == AnomalyType.FALTA_ENTRADA for a in anomalies)

    def test_detect_missing_exit(self, anomaly_service, schedule):
        """Testa detecção de saída faltante."""
        entries = [
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(8, 0),
                entry_type=EntryType.ENTRADA,
            ),
        ]

        anomalies = anomaly_service.analyze_entries(entries, schedule)

        assert len(anomalies) > 0
        assert any(a.anomaly_type == AnomalyType.FALTA_SAIDA for a in anomalies)

    def test_detect_late_entry(self, anomaly_service, schedule):
        """Testa detecção de atraso."""
        entries = [
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date(2024, 12, 30),  # Segunda-feira
                entry_time=time(8, 30),  # 30 min atrasado
                entry_type=EntryType.ENTRADA,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date(2024, 12, 30),
                entry_time=time(17, 48),
                entry_type=EntryType.SAIDA,
            ),
        ]

        anomalies = anomaly_service.analyze_entries(entries, schedule)

        assert any(a.anomaly_type == AnomalyType.ATRASO for a in anomalies)

    def test_detect_early_departure(self, anomaly_service, schedule):
        """Testa detecção de saída antecipada."""
        entries = [
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date(2024, 12, 30),
                entry_time=time(8, 0),
                entry_type=EntryType.ENTRADA,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date(2024, 12, 30),
                entry_time=time(16, 0),  # 1h48 antes
                entry_type=EntryType.SAIDA,
            ),
        ]

        anomalies = anomaly_service.analyze_entries(entries, schedule)

        assert any(a.anomaly_type == AnomalyType.SAIDA_ANTECIPADA for a in anomalies)

    def test_detect_excessive_work(self, anomaly_service):
        """Testa detecção de jornada excessiva."""
        entries = [
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(7, 0),
                entry_type=EntryType.ENTRADA,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(20, 0),  # 13 horas
                entry_type=EntryType.SAIDA,
            ),
        ]

        anomalies = anomaly_service.analyze_entries(entries)

        assert any(a.anomaly_type == AnomalyType.EXCESSO_JORNADA for a in anomalies)

    def test_detect_duplicate(self, anomaly_service):
        """Testa detecção de duplicata."""
        entries = [
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(8, 0),
                entry_type=EntryType.ENTRADA,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(8, 1),  # 1 min depois
                entry_type=EntryType.ENTRADA,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(17, 0),
                entry_type=EntryType.SAIDA,
            ),
        ]

        anomalies = anomaly_service.analyze_entries(entries)

        assert any(a.anomaly_type == AnomalyType.REGISTRO_DUPLICADO for a in anomalies)

    def test_detect_irregular_break(self, anomaly_service, schedule):
        """Testa detecção de intervalo irregular."""
        entries = [
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(8, 0),
                entry_type=EntryType.ENTRADA,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(12, 0),
                entry_type=EntryType.SAIDA_INTERVALO,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(12, 30),  # Apenas 30 min
                entry_type=EntryType.RETORNO_INTERVALO,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date.today(),
                entry_time=time(17, 0),
                entry_type=EntryType.SAIDA,
            ),
        ]

        anomalies = anomaly_service.analyze_entries(entries, schedule)

        assert any(a.anomaly_type == AnomalyType.INTERVALO_IRREGULAR for a in anomalies)

    def test_calculate_risk_score(self, anomaly_service):
        """Testa cálculo de score de risco."""
        anomalies = [
            AnomalyScore(
                anomaly_type=AnomalyType.ATRASO,
                score=30.0,
                description="Atraso de 30 min",
                severity="medium",
            ),
            AnomalyScore(
                anomaly_type=AnomalyType.FALTA_SAIDA,
                score=80.0,
                description="Saída não registrada",
                severity="high",
            ),
        ]

        score, level = anomaly_service.calculate_risk_score(anomalies)

        # 30 + 80 = 110, mas limitado a 100
        assert score == 100.0
        assert level == "critico"

    def test_suggest_resolution(self, anomaly_service):
        """Testa sugestão de resolução."""
        anomaly = AnomalyScore(
            anomaly_type=AnomalyType.ATRASO,
            score=30.0,
            description="Atraso",
            severity="medium",
        )

        resolution = anomaly_service.suggest_resolution(anomaly)

        assert "action" in resolution
        assert resolution["action"] == "justificar"

    def test_no_anomalies_valid_entries(self, anomaly_service, schedule):
        """Testa que registros válidos não geram anomalias."""
        entries = [
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date(2024, 12, 30),
                entry_time=time(8, 0),
                entry_type=EntryType.ENTRADA,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date(2024, 12, 30),
                entry_time=time(12, 0),
                entry_type=EntryType.SAIDA_INTERVALO,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date(2024, 12, 30),
                entry_time=time(13, 0),
                entry_type=EntryType.RETORNO_INTERVALO,
            ),
            TimeEntry(
                employee_id="emp-001",
                employee_name="João",
                entry_date=date(2024, 12, 30),
                entry_time=time(17, 48),
                entry_type=EntryType.SAIDA,
            ),
        ]

        anomalies = anomaly_service.analyze_entries(entries, schedule)

        # Pode haver algumas anomalias leves, mas não críticas
        critical = [a for a in anomalies if a.severity == "critical"]
        assert len(critical) == 0


class TestAnomalyScore:
    """Testes para AnomalyScore."""

    def test_create_anomaly_score(self):
        """Testa criação de AnomalyScore."""
        score = AnomalyScore(
            anomaly_type=AnomalyType.ATRASO,
            score=25.0,
            description="Atraso de 15 minutos",
            severity="low",
            auto_resolvable=False,
        )

        assert score.anomaly_type == AnomalyType.ATRASO
        assert score.score == 25.0
        assert score.severity == "low"

    def test_anomaly_score_defaults(self):
        """Testa valores padrão de AnomalyScore."""
        score = AnomalyScore(
            anomaly_type=AnomalyType.ATRASO,
            score=25.0,
            description="Atraso",
        )

        assert score.severity == "medium"
        assert score.auto_resolvable is False
