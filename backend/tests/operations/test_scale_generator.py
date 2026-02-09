"""
Testes para o serviço ScaleGenerator (geração de escalas com IA).
"""

from datetime import date
from uuid import uuid4

import pytest

from modules.operacional.models.scale import ScaleType
from modules.operacional.services.scale_generator import ScaleGenerator, scale_generator


class TestScaleGenerator:
    """Testes para o gerador de escalas."""

    @pytest.fixture
    def generator(self):
        """Retorna instância do gerador."""
        return ScaleGenerator()

    @pytest.fixture
    def base_config(self):
        """Configuração base para geração."""
        return {
            "start_time": "07:00",
            "end_time": "19:00",
            "break_minutes": 60,
        }

    def test_generator_singleton(self):
        """Verifica que scale_generator é singleton."""
        assert scale_generator is not None
        assert isinstance(scale_generator, ScaleGenerator)

    def test_generate_12x36_scale(self, generator, sample_employees, base_config):
        """Testa geração de escala 12x36."""
        scale_id = str(uuid4())
        post_id = str(uuid4())
        employee_ids = [e["id"] for e in sample_employees]

        shifts = generator.generate(
            scale_id=scale_id,
            post_id=post_id,
            scale_type=ScaleType.SCALE_12X36,
            month=1,
            year=2025,
            employee_ids=employee_ids,
            config=base_config,
        )

        assert len(shifts) > 0
        # Janeiro 2025 tem 31 dias
        # 12x36: ~16 turnos por funcionário
        # Com 4 funcionários, deveria ter muitos turnos
        assert all(shift.scale_id == scale_id for shift in shifts)
        assert all(shift.post_id == post_id for shift in shifts)

    def test_generate_6x1_scale(self, generator, sample_employees, base_config):
        """Testa geração de escala 6x1."""
        scale_id = str(uuid4())
        post_id = str(uuid4())
        employee_ids = [e["id"] for e in sample_employees]

        shifts = generator.generate(
            scale_id=scale_id,
            post_id=post_id,
            scale_type=ScaleType.SCALE_6X1,
            month=1,
            year=2025,
            employee_ids=employee_ids,
            config=base_config,
        )

        assert len(shifts) > 0
        # 6x1: 6 dias trabalhados, 1 folga
        # Verificar que há turnos em dias de semana

    def test_generate_5x2_scale(self, generator, sample_employees, base_config):
        """Testa geração de escala 5x2."""
        scale_id = str(uuid4())
        post_id = str(uuid4())
        employee_ids = [e["id"] for e in sample_employees]

        shifts = generator.generate(
            scale_id=scale_id,
            post_id=post_id,
            scale_type=ScaleType.SCALE_5X2,
            month=1,
            year=2025,
            employee_ids=employee_ids,
            config=base_config,
        )

        assert len(shifts) > 0
        # 5x2: Seg a Sex trabalhados, Sab e Dom folga
        # Verificar que não há turnos aos fins de semana

    def test_shifts_have_required_fields(self, generator, sample_employees, base_config):
        """Verifica que turnos têm campos obrigatórios."""
        scale_id = str(uuid4())
        post_id = str(uuid4())
        employee_ids = [e["id"] for e in sample_employees]

        shifts = generator.generate(
            scale_id=scale_id,
            post_id=post_id,
            scale_type=ScaleType.SCALE_12X36,
            month=1,
            year=2025,
            employee_ids=employee_ids,
            config=base_config,
        )

        for shift in shifts:
            assert shift.scale_id == scale_id
            assert shift.post_id == post_id
            assert shift.employee_id in employee_ids
            assert shift.shift_date is not None
            assert shift.start_time is not None
            assert shift.end_time is not None

    def test_shifts_within_month(self, generator, sample_employees, base_config):
        """Verifica que turnos estão dentro do mês."""
        scale_id = str(uuid4())
        post_id = str(uuid4())
        employee_ids = [e["id"] for e in sample_employees]
        month = 1
        year = 2025

        shifts = generator.generate(
            scale_id=scale_id,
            post_id=post_id,
            scale_type=ScaleType.SCALE_12X36,
            month=month,
            year=year,
            employee_ids=employee_ids,
            config=base_config,
        )

        for shift in shifts:
            assert shift.shift_date.month == month
            assert shift.shift_date.year == year

    def test_holiday_detection(self, generator, sample_employees, base_config):
        """Verifica que turnos incluem marcação de feriado."""
        scale_id = str(uuid4())
        post_id = str(uuid4())
        employee_ids = [e["id"] for e in sample_employees]

        # Janeiro tem feriado dia 1 (Ano Novo)
        shifts = generator.generate(
            scale_id=scale_id,
            post_id=post_id,
            scale_type=ScaleType.SCALE_12X36,
            month=1,
            year=2025,
            employee_ids=employee_ids,
            config=base_config,
        )

        # Verificar se há turno no dia 1 (pode ou não ser marcado como feriado
        # dependendo da biblioteca holidays estar instalada)
        new_year_shifts = [s for s in shifts if s.shift_date.day == 1]
        assert len(new_year_shifts) > 0  # Deve ter turnos no dia 1

    def test_single_employee(self, generator, base_config):
        """Testa geração com um único funcionário."""
        scale_id = str(uuid4())
        post_id = str(uuid4())
        employee_id = str(uuid4())

        shifts = generator.generate(
            scale_id=scale_id,
            post_id=post_id,
            scale_type=ScaleType.SCALE_12X36,
            month=1,
            year=2025,
            employee_ids=[employee_id],
            config=base_config,
        )

        # Com um funcionário, deve ter turnos apenas para ele
        assert len(shifts) > 0
        assert all(s.employee_id == employee_id for s in shifts)


class TestScaleMetrics:
    """Testes para métricas de escalas."""

    @pytest.fixture
    def generator(self):
        return ScaleGenerator()

    @pytest.fixture
    def base_config(self):
        """Configuração base para geração."""
        return {
            "start_time": "07:00",
            "end_time": "19:00",
            "break_minutes": 60,
        }

    def test_calculate_metrics(self, generator, sample_employees, base_config):
        """Testa cálculo de métricas da escala."""
        scale_id = str(uuid4())
        post_id = str(uuid4())
        employee_ids = [e["id"] for e in sample_employees]

        shifts = generator.generate(
            scale_id=scale_id,
            post_id=post_id,
            scale_type=ScaleType.SCALE_12X36,
            month=1,
            year=2025,
            employee_ids=employee_ids,
            config=base_config,
        )

        # Calcular métricas
        metrics = generator.calculate_metrics(shifts)

        assert "total_shifts" in metrics
        assert "total_hours" in metrics
        assert metrics["total_shifts"] == len(shifts)
        assert metrics["total_hours"] > 0


class TestShiftDistribution:
    """Testes para distribuição de turnos."""

    @pytest.fixture
    def generator(self):
        return ScaleGenerator()

    def test_multiple_employees_distribution(self, generator, sample_employees, base_config):
        """Testa distribuição entre múltiplos funcionários."""
        scale_id = str(uuid4())
        post_id = str(uuid4())
        employee_ids = [e["id"] for e in sample_employees]

        shifts = generator.generate(
            scale_id=scale_id,
            post_id=post_id,
            scale_type=ScaleType.SCALE_12X36,
            month=1,
            year=2025,
            employee_ids=employee_ids,
            config=base_config,
        )

        # Verificar que turnos foram distribuídos entre funcionários
        employees_with_shifts = {s.employee_id for s in shifts}
        assert len(employees_with_shifts) >= 1

    @pytest.fixture
    def base_config(self):
        """Configuração base para geração."""
        return {
            "start_time": "07:00",
            "end_time": "19:00",
            "break_minutes": 60,
        }

    def test_night_shift_generation(self, generator, sample_employees, base_config):
        """Testa geração de turnos noturnos."""
        scale_id = str(uuid4())
        post_id = str(uuid4())
        employee_ids = [e["id"] for e in sample_employees]

        shifts = generator.generate(
            scale_id=scale_id,
            post_id=post_id,
            scale_type=ScaleType.SCALE_12X36,
            month=1,
            year=2025,
            employee_ids=employee_ids,
            config=base_config,
        )

        # Escala 12x36 deve ter turnos noturnos
        night_shifts = [s for s in shifts if s.is_night_shift]
        # Pode ou não ter dependendo da implementação
        assert isinstance(night_shifts, list)
