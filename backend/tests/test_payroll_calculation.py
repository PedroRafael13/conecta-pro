"""Testes para cálculos de folha de pagamento."""

import pytest
from decimal import Decimal

from modules.hr.payroll_integration.models.employee_payroll_config import (
    calculate_inss,
    calculate_irrf,
    INSS_TABLE_2024,
    IRRF_TABLE_2024,
)


class TestINSSCalculation:
    """Testes para cálculo de INSS."""

    def test_inss_primeira_faixa(self):
        """Testa INSS para salário até R$ 1.412,00."""
        # Primeira faixa: 7.5%
        inss = calculate_inss(Decimal("1412.00"))
        expected = Decimal("1412.00") * Decimal("0.075")
        assert inss == expected.quantize(Decimal("0.01"))

    def test_inss_segunda_faixa(self):
        """Testa INSS para salário até R$ 2.666,68."""
        # Salário: R$ 2.000,00
        # Faixa 1: 1.412,00 * 7.5% = 105.90
        # Faixa 2: (2.000 - 1.412) * 9% = 52.92
        # Total: 158.82
        inss = calculate_inss(Decimal("2000.00"))
        expected = Decimal("158.82")
        assert inss == expected

    def test_inss_terceira_faixa(self):
        """Testa INSS para salário até R$ 4.000,03."""
        # Salário: R$ 3.500,00
        # Faixa 1: 1.412,00 * 7.5% = 105.90
        # Faixa 2: (2.666,68 - 1.412) * 9% = 112.92
        # Faixa 3: (3.500 - 2.666,68) * 12% = 100.00
        # Total: 318.82
        inss = calculate_inss(Decimal("3500.00"))
        expected = Decimal("318.82")
        assert inss == expected

    def test_inss_quarta_faixa(self):
        """Testa INSS para salário até R$ 7.786,02."""
        # Salário: R$ 5.000,00
        # Faixa 1: 1.412,00 * 7.5% = 105.90
        # Faixa 2: (2.666,68 - 1.412) * 9% = 112.92
        # Faixa 3: (4.000,03 - 2.666,68) * 12% = 160.00
        # Faixa 4: (5.000 - 4.000,03) * 14% = 139.99
        # Total: 518.81
        inss = calculate_inss(Decimal("5000.00"))
        expected = Decimal("518.81")
        assert inss == expected

    def test_inss_teto(self):
        """Testa INSS para salário acima do teto."""
        # Teto INSS: R$ 7.786,02
        # Desconto máximo: R$ 908,85
        inss_teto = calculate_inss(Decimal("7786.02"))
        inss_acima = calculate_inss(Decimal("15000.00"))

        # Ambos devem ser iguais (teto)
        assert inss_teto == inss_acima
        assert inss_acima == Decimal("908.85")

    def test_inss_salario_zero(self):
        """Testa INSS para salário zero."""
        inss = calculate_inss(Decimal("0"))
        assert inss == Decimal("0")

    def test_inss_salario_minimo(self):
        """Testa INSS para salário mínimo 2024."""
        # Salário mínimo 2024: R$ 1.412,00
        inss = calculate_inss(Decimal("1412.00"))
        expected = Decimal("1412.00") * Decimal("0.075")
        assert inss == expected.quantize(Decimal("0.01"))


class TestIRRFCalculation:
    """Testes para cálculo de IRRF."""

    def test_irrf_isento(self):
        """Testa IRRF para base até R$ 2.259,20 (isento)."""
        irrf = calculate_irrf(Decimal("2000.00"), 0)
        assert irrf == Decimal("0")

    def test_irrf_primeira_faixa(self):
        """Testa IRRF para base até R$ 2.826,65 (7.5%)."""
        # Base: R$ 2.500,00
        # Acima do isento: 2.500 - 2.259,20 = 240,80
        # IRRF: 240,80 * 7.5% = 18,06
        irrf = calculate_irrf(Decimal("2500.00"), 0)
        expected = Decimal("18.06")
        assert irrf == expected

    def test_irrf_segunda_faixa(self):
        """Testa IRRF para base até R$ 3.751,05 (15%)."""
        # Base: R$ 3.500,00
        # Faixa 1: (2.826,65 - 2.259,20) * 7.5% = 42.56
        # Faixa 2: (3.500 - 2.826,65) * 15% = 101.00
        # Total: 143.56
        irrf = calculate_irrf(Decimal("3500.00"), 0)
        expected = Decimal("143.56")
        assert irrf == expected

    def test_irrf_terceira_faixa(self):
        """Testa IRRF para base até R$ 4.664,68 (22.5%)."""
        # Base: R$ 4.500,00
        irrf = calculate_irrf(Decimal("4500.00"), 0)
        # Valor aproximado
        assert irrf > Decimal("0")
        assert irrf < Decimal("500")

    def test_irrf_quarta_faixa(self):
        """Testa IRRF para base acima de R$ 4.664,68 (27.5%)."""
        # Base: R$ 10.000,00
        irrf = calculate_irrf(Decimal("10000.00"), 0)
        # Valor alto
        assert irrf > Decimal("500")

    def test_irrf_com_dependentes(self):
        """Testa IRRF com dedução de dependentes."""
        # Dedução por dependente: R$ 189,59
        # Base: R$ 3.500,00
        # Com 2 dependentes: 3.500 - (2 * 189.59) = 3.120,82
        irrf_sem_dep = calculate_irrf(Decimal("3500.00"), 0)
        irrf_com_dep = calculate_irrf(Decimal("3500.00"), 2)

        assert irrf_com_dep < irrf_sem_dep

    def test_irrf_muitos_dependentes_resulta_isento(self):
        """Testa IRRF quando dependentes tornam isento."""
        # Base: R$ 2.500,00
        # Com 5 dependentes: 2.500 - (5 * 189.59) = 1.552,05 (abaixo do isento)
        irrf = calculate_irrf(Decimal("2500.00"), 5)
        assert irrf == Decimal("0")

    def test_irrf_base_zero(self):
        """Testa IRRF para base zero."""
        irrf = calculate_irrf(Decimal("0"), 0)
        assert irrf == Decimal("0")


class TestTaxTables:
    """Testes para tabelas de impostos."""

    def test_inss_table_structure(self):
        """Testa estrutura da tabela INSS."""
        assert len(INSS_TABLE_2024) == 4

        for faixa in INSS_TABLE_2024:
            assert "min" in faixa
            assert "max" in faixa
            assert "rate" in faixa
            assert isinstance(faixa["min"], Decimal)
            assert isinstance(faixa["max"], Decimal)
            assert isinstance(faixa["rate"], Decimal)

    def test_inss_table_order(self):
        """Testa ordem das faixas INSS."""
        for i in range(len(INSS_TABLE_2024) - 1):
            assert INSS_TABLE_2024[i]["max"] <= INSS_TABLE_2024[i + 1]["min"]

    def test_irrf_table_structure(self):
        """Testa estrutura da tabela IRRF."""
        assert len(IRRF_TABLE_2024) == 5

        for faixa in IRRF_TABLE_2024:
            assert "min" in faixa
            assert "max" in faixa
            assert "rate" in faixa
            assert isinstance(faixa["min"], Decimal)
            assert isinstance(faixa["rate"], Decimal)

    def test_irrf_table_order(self):
        """Testa ordem das faixas IRRF."""
        for i in range(len(IRRF_TABLE_2024) - 1):
            if IRRF_TABLE_2024[i]["max"] < Decimal("999999"):
                assert IRRF_TABLE_2024[i]["max"] <= IRRF_TABLE_2024[i + 1]["min"]


class TestOvertimeCalculation:
    """Testes para cálculo de hora extra."""

    def test_hourly_rate_calculation(self):
        """Testa cálculo de valor hora."""
        base_salary = Decimal("3000.00")
        monthly_hours = Decimal("220")

        hourly_rate = base_salary / monthly_hours
        assert hourly_rate == Decimal("13.636363636363636363636363636")

    def test_overtime_50_calculation(self):
        """Testa cálculo de hora extra 50%."""
        hourly_rate = Decimal("13.64")
        overtime_rate = Decimal("1.50")
        hours = Decimal("10")

        overtime_value = hourly_rate * overtime_rate * hours
        expected = Decimal("204.60")
        assert overtime_value == expected

    def test_overtime_100_calculation(self):
        """Testa cálculo de hora extra 100%."""
        hourly_rate = Decimal("13.64")
        overtime_rate = Decimal("2.00")
        hours = Decimal("5")

        overtime_value = hourly_rate * overtime_rate * hours
        expected = Decimal("136.40")
        assert overtime_value == expected

    def test_night_shift_calculation(self):
        """Testa cálculo de adicional noturno."""
        hourly_rate = Decimal("13.64")
        night_rate = Decimal("1.20")
        hours = Decimal("8")

        night_value = hourly_rate * night_rate * hours
        expected = Decimal("130.944")
        assert night_value == expected.quantize(Decimal("0.01"))


class TestProportionalCalculation:
    """Testes para cálculo proporcional."""

    def test_proportional_salary(self):
        """Testa salário proporcional."""
        base_salary = Decimal("3000.00")
        worked_days = 15
        month_days = 30

        proportional = base_salary * Decimal(worked_days) / Decimal(month_days)
        assert proportional == Decimal("1500.00")

    def test_proportional_vacation(self):
        """Testa férias proporcionais."""
        base_salary = Decimal("3000.00")
        months_worked = 6

        # 1/12 avos por mês trabalhado
        vacation_proportional = (base_salary / 12) * months_worked
        assert vacation_proportional == Decimal("1500.00")

    def test_proportional_thirteenth(self):
        """Testa 13º proporcional."""
        base_salary = Decimal("3000.00")
        months_worked = 8

        # 1/12 avos por mês trabalhado
        thirteenth_proportional = (base_salary / 12) * months_worked
        assert thirteenth_proportional == Decimal("2000.00")
