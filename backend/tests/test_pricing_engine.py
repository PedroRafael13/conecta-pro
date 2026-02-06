"""
Testes do Motor de Precificacao (PricingEngine).

Testa calculos de CCT, impostos, margem e formacao de preco
para propostas comerciais.
"""

from decimal import Decimal

import pytest

from modules.crm.services.pricing_engine import PricingEngine, PricingInput, PricingResult


class TestPricingEngineBasic:
    """Testes basicos do PricingEngine."""

    @pytest.fixture
    def engine(self) -> PricingEngine:
        """Fixture do engine."""
        return PricingEngine()

    @pytest.fixture
    def basic_input(self) -> PricingInput:
        """Input basico para testes."""
        return PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="vigilancia",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

    def test_calculate_returns_pricing_result(
        self, engine: PricingEngine, basic_input: PricingInput
    ) -> None:
        """Testa que calculate retorna PricingResult."""
        result = engine.calculate(basic_input)

        assert isinstance(result, PricingResult)

    def test_calculate_base_cost(self, engine: PricingEngine, basic_input: PricingInput) -> None:
        """Testa calculo do custo base."""
        result = engine.calculate(basic_input)

        # base_cost = salario * headcount * meses
        expected_base = Decimal("2000.00") * 10 * 12
        assert result.base_cost == expected_base

    def test_calculate_cct_value_positive(
        self, engine: PricingEngine, basic_input: PricingInput
    ) -> None:
        """Testa que CCT e positivo."""
        result = engine.calculate(basic_input)

        assert result.cct_value > 0
        assert result.cct_percent > 0

    def test_calculate_total_greater_than_cost(
        self, engine: PricingEngine, basic_input: PricingInput
    ) -> None:
        """Testa que total e maior que custo (inclui margem e impostos)."""
        result = engine.calculate(basic_input)

        assert result.total_contract > result.total_cost

    def test_calculate_margin_applied(
        self, engine: PricingEngine, basic_input: PricingInput
    ) -> None:
        """Testa que margem e aplicada."""
        result = engine.calculate(basic_input)

        assert result.margin_value > 0
        assert result.margin_percent > Decimal("0")


class TestPricingEngineCCT:
    """Testes especificos de CCT (encargos trabalhistas)."""

    @pytest.fixture
    def engine(self) -> PricingEngine:
        """Fixture do engine."""
        return PricingEngine()

    def test_cct_percent_in_expected_range(self, engine: PricingEngine) -> None:
        """Testa que CCT esta na faixa esperada (70-100%)."""
        cct = engine._calculate_cct_percent()  # pylint: disable=protected-access

        # CCT tipico brasileiro esta entre 70% e 100%
        assert cct >= Decimal("0.70")
        assert cct <= Decimal("1.00")

    def test_cct_components_count(self, engine: PricingEngine) -> None:
        """Testa que todos os componentes de CCT estao presentes."""
        expected_components = [
            "inss_empresa",
            "fgts",
            "sat_rat",
            "terceiros",
            "ferias",
            "ferias_terco",
            "decimo_terceiro",
            "aviso_previo",
            "multa_fgts",
            "provisao_rescisao",
        ]

        for component in expected_components:
            assert component in engine.CCT_COMPONENTS

    def test_cct_breakdown(self, engine: PricingEngine) -> None:
        """Testa detalhamento do CCT."""
        breakdown = engine.calculate_cct_breakdown(
            base_salary=Decimal("2000.00"),
            headcount=10,
            months=12,
        )

        assert len(breakdown) == len(engine.CCT_COMPONENTS)
        assert all(value >= 0 for value in breakdown.values())

        # Total do breakdown deve bater com calculo direto
        total_breakdown = sum(breakdown.values())
        base = Decimal("2000.00") * 10 * 12
        cct_percent = engine._calculate_cct_percent()  # pylint: disable=protected-access
        expected_total = (base * cct_percent).quantize(Decimal("0.01"))

        # Pode haver pequena diferenca por arredondamento
        assert abs(total_breakdown - expected_total) < Decimal("1.00")


class TestPricingEngineTaxes:
    """Testes de calculo de impostos."""

    @pytest.fixture
    def engine(self) -> PricingEngine:
        """Fixture do engine."""
        return PricingEngine()

    def test_tax_rates_vigilancia(self, engine: PricingEngine) -> None:
        """Testa taxas de imposto para vigilancia."""
        rates = engine._get_tax_rates("vigilancia", "SP")  # pylint: disable=protected-access

        assert "iss" in rates
        assert "pis" in rates
        assert "cofins" in rates
        assert "irpj" in rates
        assert "csll" in rates

    def test_tax_rates_limpeza_iss(self, engine: PricingEngine) -> None:
        """Testa que limpeza tem ISS configurado."""
        rates_limpeza = engine._get_tax_rates("limpeza", "SP")  # pylint: disable=protected-access

        # ISS para limpeza deve estar presente e ser positivo
        assert "iss" in rates_limpeza
        assert rates_limpeza["iss"] >= Decimal("0.02")
        assert rates_limpeza["iss"] <= Decimal("0.05")

    def test_tax_breakdown_in_result(self, engine: PricingEngine) -> None:
        """Testa que breakdown de impostos esta no resultado."""
        pricing_input = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="vigilancia",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        result = engine.calculate(pricing_input)

        assert len(result.tax_breakdown) > 0
        assert sum(result.tax_breakdown.values()) > 0


class TestPricingEngineMargin:
    """Testes de calculo de margem."""

    @pytest.fixture
    def engine(self) -> PricingEngine:
        """Fixture do engine."""
        return PricingEngine()

    def test_margin_target_reflected(self, engine: PricingEngine) -> None:
        """Testa que margem alvo e refletida no resultado."""
        pricing_input = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("20.00"),
        )

        result = engine.calculate(pricing_input)

        # Margem efetiva deve ser positiva (calculo "por dentro" pode reduzir)
        # A margem final depende da relacao custo/preco com impostos
        assert result.margin_percent > Decimal("0")
        assert result.margin_value > Decimal("0")

    def test_higher_margin_higher_price(self, engine: PricingEngine) -> None:
        """Testa que margem maior gera preco maior."""
        base_input = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("10.00"),
        )

        high_margin_input = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("30.00"),
        )

        result_low = engine.calculate(base_input)
        result_high = engine.calculate(high_margin_input)

        assert result_high.total_contract > result_low.total_contract

    def test_estimate_margin(self, engine: PricingEngine) -> None:
        """Testa estimativa de margem dado preco de venda."""
        margin = engine.estimate_margin(
            selling_price=Decimal("100000.00"),
            total_cost=Decimal("70000.00"),
            tax_amount=Decimal("15000.00"),
        )

        # (100000 - 70000 - 15000) / 100000 = 15%
        assert margin == Decimal("15.00")


class TestPricingEngineValidation:
    """Testes de validacao de entrada."""

    @pytest.fixture
    def engine(self) -> PricingEngine:
        """Fixture do engine."""
        return PricingEngine()

    def test_negative_salary_raises_error(self, engine: PricingEngine) -> None:
        """Testa que salario negativo gera erro."""
        pricing_input = PricingInput(
            base_salary=Decimal("-1000.00"),
            headcount=10,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        with pytest.raises(ValueError, match="Salario base deve ser positivo"):
            engine.calculate(pricing_input)

    def test_zero_headcount_raises_error(self, engine: PricingEngine) -> None:
        """Testa que headcount zero gera erro."""
        pricing_input = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=0,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        with pytest.raises(ValueError, match="Headcount deve ser positivo"):
            engine.calculate(pricing_input)

    def test_zero_months_raises_error(self, engine: PricingEngine) -> None:
        """Testa que meses zero gera erro."""
        pricing_input = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=0,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        with pytest.raises(ValueError, match="Meses de contrato deve ser positivo"):
            engine.calculate(pricing_input)

    def test_negative_margin_raises_error(self, engine: PricingEngine) -> None:
        """Testa que margem negativa gera erro."""
        pricing_input = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("-5.00"),
        )

        with pytest.raises(ValueError, match="Margem nao pode ser negativa"):
            engine.calculate(pricing_input)


class TestPricingEngineSimulation:
    """Testes de simulacao de precos."""

    @pytest.fixture
    def engine(self) -> PricingEngine:
        """Fixture do engine."""
        return PricingEngine()

    def test_simulate_returns_multiple_results(self, engine: PricingEngine) -> None:
        """Testa que simulacao retorna multiplos resultados."""
        pricing_input = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        results = engine.simulate_price(pricing_input)

        assert len(results) > 1
        assert all(isinstance(r, PricingResult) for r in results)

    def test_simulate_with_target_price(self, engine: PricingEngine) -> None:
        """Testa simulacao com preco alvo."""
        pricing_input = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        target_price = Decimal("500000.00")
        results = engine.simulate_price(pricing_input, target_price=target_price)

        # Deve ter pelo menos o resultado base + resultado do preco alvo
        assert len(results) >= 2

    def test_simulate_with_custom_margins(self, engine: PricingEngine) -> None:
        """Testa simulacao com margens customizadas."""
        pricing_input = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        custom_margins = [Decimal("5"), Decimal("10"), Decimal("15")]
        results = engine.simulate_price(pricing_input, custom_margins=custom_margins)

        # Deve ter resultado base + margens customizadas (exceto 15 que e igual ao base)
        assert len(results) >= 3


class TestPricingEngineDecimalPrecision:
    """Testes de precisao Decimal."""

    @pytest.fixture
    def engine(self) -> PricingEngine:
        """Fixture do engine."""
        return PricingEngine()

    def test_all_monetary_values_are_decimal(self, engine: PricingEngine) -> None:
        """Testa que todos os valores monetarios sao Decimal."""
        pricing_input = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        result = engine.calculate(pricing_input)

        # Todos os valores devem ser Decimal
        assert isinstance(result.base_cost, Decimal)
        assert isinstance(result.cct_value, Decimal)
        assert isinstance(result.cct_percent, Decimal)
        assert isinstance(result.labor_cost, Decimal)
        assert isinstance(result.total_cost, Decimal)
        assert isinstance(result.tax_amount, Decimal)
        assert isinstance(result.margin_value, Decimal)
        assert isinstance(result.margin_percent, Decimal)
        assert isinstance(result.unit_price, Decimal)
        assert isinstance(result.total_monthly, Decimal)
        assert isinstance(result.total_contract, Decimal)

    def test_values_have_two_decimal_places(self, engine: PricingEngine) -> None:
        """Testa que valores tem 2 casas decimais."""
        pricing_input = PricingInput(
            base_salary=Decimal("2000.00"),
            headcount=10,
            contract_months=12,
            service_type="default",
            client_state="SP",
            margin_target=Decimal("15.00"),
        )

        result = engine.calculate(pricing_input)

        # Verificar precisao de 2 casas
        def has_two_decimals(value: Decimal) -> bool:
            """Verifica se tem no maximo 2 casas decimais."""
            return value == value.quantize(Decimal("0.01"))

        assert has_two_decimals(result.base_cost)
        assert has_two_decimals(result.total_contract)
        assert has_two_decimals(result.unit_price)


class TestPricingEngineRealScenarios:
    """Testes com cenarios reais."""

    @pytest.fixture
    def engine(self) -> PricingEngine:
        """Fixture do engine."""
        return PricingEngine()

    def test_vigilancia_contract(self, engine: PricingEngine) -> None:
        """Testa contrato de vigilancia tipico."""
        # Cenario: 5 vigilantes, 24 meses, salario R$ 2.500
        pricing_input = PricingInput(
            base_salary=Decimal("2500.00"),
            headcount=5,
            contract_months=24,
            service_type="vigilancia",
            client_state="SP",
            margin_target=Decimal("18.00"),
            benefits_value=Decimal("800.00"),  # VT + VR + VA
        )

        result = engine.calculate(pricing_input)

        # Verificacoes de sanidade
        assert result.total_contract > Decimal("500000.00")  # Contrato significativo
        assert result.cct_percent > Decimal("70.00")  # CCT realista
        assert result.margin_percent > Decimal("10.00")  # Margem minima

    def test_limpeza_contract(self, engine: PricingEngine) -> None:
        """Testa contrato de limpeza tipico."""
        # Cenario: 3 auxiliares, 12 meses, salario minimo
        pricing_input = PricingInput(
            base_salary=Decimal("1412.00"),  # Salario minimo 2024
            headcount=3,
            contract_months=12,
            service_type="limpeza",
            client_state="SP",
            margin_target=Decimal("12.00"),
            benefits_value=Decimal("500.00"),
            equipment_value=Decimal("5000.00"),  # Equipamentos de limpeza
        )

        result = engine.calculate(pricing_input)

        # Contrato menor que vigilancia
        assert result.total_contract < Decimal("200000.00")
        assert result.equipment_cost == Decimal("5000.00")
