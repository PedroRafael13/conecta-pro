"""
Testes do PricingEngine.

Testes para calculo de CCT, impostos e formacao de preco.
"""

from decimal import Decimal

import pytest

from modules.crm.services.pricing_engine import (
    PricingEngine,
    PricingInput,
    PricingResult,
)


class TestPricingEngine:
    """Testes do motor de precificacao."""

    @pytest.fixture
    def engine(self):
        """Cria instancia do engine."""
        return PricingEngine()

    @pytest.fixture
    def basic_input(self):
        """Dados de entrada basicos."""
        return PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="vigilancia",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

    def test_calculate_basic(self, engine, basic_input):
        """Testa calculo basico."""
        result = engine.calculate(basic_input)

        assert isinstance(result, PricingResult)
        assert result.base_cost > 0
        assert result.cct_value > 0
        assert result.labor_cost > 0
        assert result.total_cost > 0
        assert result.total_contract > result.total_cost

    def test_calculate_cct_components(self, engine):
        """Testa componentes do CCT."""
        cct_percent = engine._calculate_cct_percent()

        # Soma dos componentes
        expected = sum(engine.CCT_COMPONENTS.values())
        assert cct_percent == expected

        # CCT total deve ser aproximadamente 73%
        assert Decimal("0.70") < cct_percent < Decimal("0.80")

    def test_calculate_cct_breakdown(self, engine):
        """Testa detalhamento do CCT."""
        breakdown = engine.calculate_cct_breakdown(
            base_salary=Decimal("2000.00"),
            headcount=5,
            months=6,
        )

        # Base = 2000 * 5 * 6 = 60000
        Decimal("60000.00")

        assert "inss_empresa" in breakdown
        assert "fgts" in breakdown
        assert "ferias" in breakdown
        assert "decimo_terceiro" in breakdown

        # INSS = 60000 * 0.20 = 12000
        assert breakdown["inss_empresa"] == Decimal("12000.00")

        # FGTS = 60000 * 0.08 = 4800
        assert breakdown["fgts"] == Decimal("4800.00")

    def test_calculate_with_benefits(self, engine):
        """Testa calculo com beneficios."""
        input_data = PricingInput(
            base_salary=Decimal("2500.00"),
            headcount=8,
            contract_months=12,
            service_type="limpeza",
            client_state="RJ",
            margin_target=Decimal("20.00"),
            benefits_value=Decimal("500.00"),  # VT, VR, etc
        )

        result = engine.calculate(input_data)

        # Benefits cost = 500 * 8 * 12 = 48000
        assert result.benefits_cost == Decimal("48000.00")
        assert result.total_cost > result.labor_cost

    def test_calculate_with_equipment(self, engine):
        """Testa calculo com equipamentos."""
        input_data = PricingInput(
            base_salary=Decimal("3000.00"),
            headcount=5,
            contract_months=12,
            service_type="facilities",
            client_state="MG",
            margin_target=Decimal("18.00"),
            equipment_value=Decimal("15000.00"),
        )

        result = engine.calculate(input_data)

        assert result.equipment_cost == Decimal("15000.00")

    def test_tax_rates_by_service(self, engine):
        """Testa taxas de impostos por tipo de servico."""
        # Vigilancia - ISS 5%
        rates_vigilancia = engine._get_tax_rates("vigilancia", "SP")
        assert rates_vigilancia["iss"] == Decimal("0.05")

        # Limpeza - ISS 2%
        rates_limpeza = engine._get_tax_rates("limpeza", "SP")
        assert rates_limpeza["iss"] == Decimal("0.02")

        # Facilities - ISS 3%
        rates_facilities = engine._get_tax_rates("facilities", "SP")
        assert rates_facilities["iss"] == Decimal("0.03")

    def test_tax_rates_by_state(self, engine):
        """Testa ISS por estado."""
        # SP - 5%
        rates_sp = engine._get_tax_rates("default", "SP")
        assert rates_sp["iss"] == Decimal("0.05")

        # SC - 3%
        rates_sc = engine._get_tax_rates("default", "SC")
        assert rates_sc["iss"] == Decimal("0.03")

        # MG - 4%
        rates_mg = engine._get_tax_rates("default", "MG")
        assert rates_mg["iss"] == Decimal("0.04")

    def test_tax_breakdown(self, engine, basic_input):
        """Testa detalhamento de impostos."""
        result = engine.calculate(basic_input)

        assert "iss" in result.tax_breakdown
        assert "pis" in result.tax_breakdown
        assert "cofins" in result.tax_breakdown
        assert "irpj" in result.tax_breakdown
        assert "csll" in result.tax_breakdown

        # Soma dos impostos = tax_amount
        sum_taxes = sum(result.tax_breakdown.values())
        assert abs(sum_taxes - result.tax_amount) < Decimal("1.00")

    def test_margin_calculation(self, engine, basic_input):
        """Testa calculo de margem."""
        result = engine.calculate(basic_input)

        # Margem efetiva deve ser proxima da alvo
        # (pode variar um pouco devido aos impostos)
        assert Decimal("10.00") < result.margin_percent < Decimal("20.00")

    def test_unit_price_calculation(self, engine, basic_input):
        """Testa calculo de preco unitario."""
        result = engine.calculate(basic_input)

        # unit_price = total_monthly / headcount
        expected_unit = result.total_monthly / basic_input.headcount
        assert abs(result.unit_price - expected_unit) < Decimal("0.01")

    def test_estimate_margin(self, engine):
        """Testa estimativa de margem."""
        selling_price = Decimal("100000.00")
        total_cost = Decimal("70000.00")
        tax_amount = Decimal("15000.00")

        margin = engine.estimate_margin(selling_price, total_cost, tax_amount)

        # Margem = (100000 - 70000 - 15000) / 100000 * 100 = 15%
        assert margin == Decimal("15.00")

    def test_estimate_margin_zero_price(self, engine):
        """Testa margem com preco zero."""
        margin = engine.estimate_margin(
            Decimal("0.00"),
            Decimal("50000.00"),
            Decimal("5000.00"),
        )

        assert margin == Decimal("0.00")

    def test_simulate_price(self, engine, basic_input):
        """Testa simulacao de precos."""
        results = engine.simulate_price(basic_input)

        # Deve ter pelo menos o cenario base + 5 margens padrao
        assert len(results) >= 6

        # Todos devem ser PricingResult
        for result in results:
            assert isinstance(result, PricingResult)

    def test_simulate_price_with_target(self, engine, basic_input):
        """Testa simulacao com preco alvo."""
        # Calcula preco base primeiro
        base_result = engine.calculate(basic_input)
        target_price = base_result.total_contract * Decimal("1.1")  # 10% acima

        results = engine.simulate_price(
            basic_input,
            target_price=target_price,
        )

        # Deve incluir cenario com margem calculada para atingir preco alvo
        assert len(results) > 1

    def test_simulate_price_custom_margins(self, engine, basic_input):
        """Testa simulacao com margens customizadas."""
        custom_margins = [
            Decimal("5.00"),
            Decimal("8.00"),
            Decimal("12.00"),
        ]

        results = engine.simulate_price(
            basic_input,
            custom_margins=custom_margins,
        )

        # Base + 3 customizadas
        assert len(results) >= 4

    def test_validation_negative_salary(self, engine):
        """Testa validacao de salario negativo."""
        input_data = PricingInput(
            base_salary=Decimal("-1000.00"),
            headcount=5,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        with pytest.raises(ValueError, match="Salario"):
            engine.calculate(input_data)

    def test_validation_zero_headcount(self, engine):
        """Testa validacao de headcount zero."""
        input_data = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=0,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        with pytest.raises(ValueError, match="Headcount"):
            engine.calculate(input_data)

    def test_validation_negative_margin(self, engine):
        """Testa validacao de margem negativa."""
        input_data = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("-5.00"),
        )

        with pytest.raises(ValueError, match="Margem"):
            engine.calculate(input_data)

    def test_rounding(self, engine):
        """Testa arredondamento para 2 casas."""
        value = Decimal("123.456789")
        rounded = engine._round(value)

        assert rounded == Decimal("123.46")

    def test_real_scenario_vigilancia(self, engine):
        """Testa cenario real de vigilancia."""
        # Contrato de 20 vigilantes por 12 meses
        input_data = PricingInput(
            base_salary=Decimal("2500.00"),
            headcount=20,
            contract_months=12,
            service_type="vigilancia",
            client_state="SP",
            margin_target=Decimal("18.00"),
            benefits_value=Decimal("800.00"),
            equipment_value=Decimal("50000.00"),
        )

        result = engine.calculate(input_data)

        # Verificacoes de sanidade
        assert result.base_cost == Decimal("600000.00")  # 2500 * 20 * 12
        assert result.benefits_cost == Decimal("192000.00")  # 800 * 20 * 12
        assert result.equipment_cost == Decimal("50000.00")

        # CCT deve adicionar ~73% sobre base
        assert result.cct_value > Decimal("400000.00")

        # Preco mensal por vigilante
        price_per_vigilante = result.unit_price
        assert price_per_vigilante > Decimal("4000.00")  # Minimo realista

        # Log para verificacao manual
        print("\nCenario Vigilancia:")
        print(f"  Base: R$ {result.base_cost:,.2f}")
        print(f"  CCT: R$ {result.cct_value:,.2f} ({result.cct_percent}%)")
        print(f"  Benefits: R$ {result.benefits_cost:,.2f}")
        print(f"  Equipment: R$ {result.equipment_cost:,.2f}")
        print(f"  Total Cost: R$ {result.total_cost:,.2f}")
        print(f"  Taxes: R$ {result.tax_amount:,.2f}")
        print(f"  Margin: R$ {result.margin_value:,.2f} ({result.margin_percent}%)")
        print(f"  Monthly: R$ {result.total_monthly:,.2f}")
        print(f"  Per Head: R$ {result.unit_price:,.2f}")
        print(f"  Contract: R$ {result.total_contract:,.2f}")
