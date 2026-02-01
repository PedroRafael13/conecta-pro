"""
tests/domains/operacional/test_substitution_service.py
Testes unitarios para SubstitutionService.
"""

import sys
from datetime import date, time

import pytest

sys.path.insert(0, "/opt/conecta-pro/backend")

from modules.operacional.services.substitution_service import SubstitutionService


@pytest.fixture
def service():
    """Instancia do SubstitutionService."""
    return SubstitutionService()


def _make_employee(
    emp_id="emp1",
    name="Joao Silva",
    posts_worked=None,
    preferred_shifts=None,
    hourly_rate=25.0,
    location=None,
    shifts_this_week=3,
    max_shifts_per_week=6,
    is_on_leave=False,
    post_types_worked=None,
    avg_market_rate=25.0,
):
    """Helper para criar dict de funcionario."""
    return {
        "id": emp_id,
        "name": name,
        "posts_worked": posts_worked or [],
        "post_types_worked": post_types_worked or [],
        "preferred_shifts": preferred_shifts or [],
        "hourly_rate": hourly_rate,
        "avg_market_rate": avg_market_rate,
        "location": location,
        "shifts_this_week": shifts_this_week,
        "max_shifts_per_week": max_shifts_per_week,
        "is_on_leave": is_on_leave,
    }


class TestSubstitutionServiceInit:
    """Testes de inicializacao."""

    def test_weights_sum_to_100(self):
        total = sum(SubstitutionService.WEIGHTS.values())
        assert total == 100

    def test_all_weight_categories_present(self):
        expected = {"same_post_experience", "same_shift_type", "availability", "distance", "cost"}
        assert set(SubstitutionService.WEIGHTS.keys()) == expected


class TestSubstitutionSuggest:
    """Testes para sugestao de substitutos."""

    def test_empty_employees_returns_empty(self, service):
        result = service.suggest_substitutes(
            shift_date=date(2026, 2, 1),
            post_id="post1",
            shift_start=time(8, 0),
            shift_end=time(16, 0),
            available_employees=[],
        )
        assert result == []

    def test_single_employee_returns_one(self, service):
        emp = _make_employee(posts_worked=["post1"])
        result = service.suggest_substitutes(
            shift_date=date(2026, 2, 1),
            post_id="post1",
            shift_start=time(8, 0),
            shift_end=time(16, 0),
            available_employees=[emp],
        )
        assert len(result) == 1
        assert result[0].employee_id == "emp1"

    def test_max_suggestions_respected(self, service):
        employees = [_make_employee(emp_id=f"emp{i}") for i in range(10)]
        result = service.suggest_substitutes(
            shift_date=date(2026, 2, 1),
            post_id="post1",
            shift_start=time(8, 0),
            shift_end=time(16, 0),
            available_employees=employees,
            max_suggestions=3,
        )
        assert len(result) <= 3

    def test_sorted_by_score_descending(self, service):
        employees = [
            _make_employee(emp_id="low", posts_worked=[]),
            _make_employee(emp_id="high", posts_worked=["post1"], preferred_shifts=["diurno"]),
        ]
        result = service.suggest_substitutes(
            shift_date=date(2026, 2, 1),
            post_id="post1",
            shift_start=time(8, 0),
            shift_end=time(16, 0),
            available_employees=employees,
        )
        if len(result) >= 2:
            assert result[0].score >= result[1].score

    def test_night_shift_detection(self, service):
        emp = _make_employee(preferred_shifts=["noturno"])
        result = service.suggest_substitutes(
            shift_date=date(2026, 2, 1),
            post_id="post1",
            shift_start=time(22, 0),
            shift_end=time(6, 0),
            available_employees=[emp],
        )
        assert len(result) == 1


class TestSubstitutionScoring:
    """Testes para calculo de score."""

    def test_post_experience_boosts_score(self, service):
        emp_with = _make_employee(emp_id="with", posts_worked=["post1"])
        emp_without = _make_employee(emp_id="without", posts_worked=["post99"])

        r1 = service.suggest_substitutes(
            date(2026, 2, 1),
            "post1",
            time(8, 0),
            time(16, 0),
            [emp_with],
        )
        r2 = service.suggest_substitutes(
            date(2026, 2, 1),
            "post1",
            time(8, 0),
            time(16, 0),
            [emp_without],
        )

        assert r1[0].score > r2[0].score

    def test_suggestion_has_required_fields(self, service):
        emp = _make_employee()
        result = service.suggest_substitutes(
            date(2026, 2, 1),
            "post1",
            time(8, 0),
            time(16, 0),
            [emp],
        )
        suggestion = result[0]
        assert hasattr(suggestion, "employee_id")
        assert hasattr(suggestion, "employee_name")
        assert hasattr(suggestion, "score")
        assert hasattr(suggestion, "reasons")
        assert hasattr(suggestion, "is_overtime")
        assert hasattr(suggestion, "estimated_cost")

    def test_score_between_0_and_100(self, service):
        emp = _make_employee(
            posts_worked=["post1"],
            preferred_shifts=["diurno"],
            location=(-3.1, -60.0),
        )
        result = service.suggest_substitutes(
            date(2026, 2, 1),
            "post1",
            time(8, 0),
            time(16, 0),
            [emp],
            post_location=(-3.1, -60.0),
        )
        assert 0 <= result[0].score <= 100

    def test_reasons_list_not_empty(self, service):
        emp = _make_employee(posts_worked=["post1"])
        result = service.suggest_substitutes(
            date(2026, 2, 1),
            "post1",
            time(8, 0),
            time(16, 0),
            [emp],
        )
        assert len(result[0].reasons) > 0
