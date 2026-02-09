"""
Motor de Precificacao para Propostas.

Calcula custos trabalhistas (CCT), impostos e margem
para formacao de preco de venda em contratos de servicos.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from core.logging import logger


@dataclass
class PricingInput:
    """
    Dados de entrada para precificacao.

    Attributes:
        base_salary: Salario base mensal
        headcount: Numero de funcionarios
        contract_months: Duracao do contrato em meses
        service_type: Tipo de servico (vigilancia, limpeza, etc)
        client_state: Estado do cliente (para ISS)
        margin_target: Margem alvo em percentual
        benefits_value: Valor de beneficios por funcionario/mes
        equipment_value: Valor total de equipamentos
    """

    base_salary: Decimal
    headcount: int
    contract_months: int
    service_type: str
    client_state: str
    margin_target: Decimal
    benefits_value: Decimal = Decimal("0.00")
    equipment_value: Decimal = Decimal("0.00")


@dataclass
class PricingResult:
    """
    Resultado do calculo de preco.

    Attributes:
        base_cost: Custo base de salarios
        cct_value: Valor total de encargos trabalhistas
        cct_percent: Percentual de CCT aplicado
        labor_cost: Custo total de mao de obra
        benefits_cost: Custo total de beneficios
        equipment_cost: Custo de equipamentos
        total_cost: Custo total
        tax_amount: Valor total de impostos
        tax_breakdown: Detalhamento por imposto
        margin_value: Valor da margem
        margin_percent: Percentual efetivo de margem
        unit_price: Preco unitario por funcionario/mes
        total_monthly: Valor mensal total
        total_contract: Valor total do contrato
    """

    base_cost: Decimal
    cct_value: Decimal
    cct_percent: Decimal
    labor_cost: Decimal
    benefits_cost: Decimal
    equipment_cost: Decimal
    total_cost: Decimal
    tax_amount: Decimal
    tax_breakdown: dict[str, Decimal]
    margin_value: Decimal
    margin_percent: Decimal
    unit_price: Decimal
    total_monthly: Decimal
    total_contract: Decimal


class PricingEngine:
    """
    Motor de precificacao com calculo de CCT.

    Calcula custos trabalhistas, impostos e margem
    para formacao de preco de venda.

    Encargos trabalhistas (CCT) incluidos:
    - INSS Empresa: 20%
    - FGTS: 8%
    - SAT/RAT: 3%
    - Terceiros (Sistema S): 5.8%
    - Ferias: 11.11%
    - 1/3 Ferias: 3.70%
    - 13o Salario: 8.33%
    - Aviso Previo: 4.17%
    - Multa FGTS: 4%
    - Provisao Rescisao: 5%

    Impostos calculados "por dentro":
    - ISS: variavel por tipo/municipio
    - PIS: 0.65%
    - COFINS: 3%
    - IRPJ: 4.8% (Lucro Presumido)
    - CSLL: 2.88% (Lucro Presumido)
    """

    # Encargos trabalhistas (CCT)
    CCT_COMPONENTS: dict[str, Decimal] = {
        "inss_empresa": Decimal("0.20"),
        "fgts": Decimal("0.08"),
        "sat_rat": Decimal("0.03"),
        "terceiros": Decimal("0.058"),
        "ferias": Decimal("0.1111"),
        "ferias_terco": Decimal("0.0370"),
        "decimo_terceiro": Decimal("0.0833"),
        "aviso_previo": Decimal("0.0417"),
        "multa_fgts": Decimal("0.04"),
        "provisao_rescisao": Decimal("0.05"),
    }

    # Impostos por tipo de servico
    TAX_RATES: dict[str, dict[str, Decimal]] = {
        "default": {
            "iss": Decimal("0.05"),
            "pis": Decimal("0.0065"),
            "cofins": Decimal("0.03"),
            "irpj": Decimal("0.048"),
            "csll": Decimal("0.0288"),
        },
        "vigilancia": {
            "iss": Decimal("0.05"),
            "pis": Decimal("0.0065"),
            "cofins": Decimal("0.03"),
            "irpj": Decimal("0.048"),
            "csll": Decimal("0.0288"),
        },
        "limpeza": {
            "iss": Decimal("0.02"),
            "pis": Decimal("0.0065"),
            "cofins": Decimal("0.03"),
            "irpj": Decimal("0.048"),
            "csll": Decimal("0.0288"),
        },
        "portaria": {
            "iss": Decimal("0.05"),
            "pis": Decimal("0.0065"),
            "cofins": Decimal("0.03"),
            "irpj": Decimal("0.048"),
            "csll": Decimal("0.0288"),
        },
        "facilities": {
            "iss": Decimal("0.03"),
            "pis": Decimal("0.0065"),
            "cofins": Decimal("0.03"),
            "irpj": Decimal("0.048"),
            "csll": Decimal("0.0288"),
        },
    }

    # ISS por estado (quando diferente do padrao)
    ISS_BY_STATE: dict[str, Decimal] = {
        "SP": Decimal("0.05"),
        "RJ": Decimal("0.05"),
        "MG": Decimal("0.04"),
        "RS": Decimal("0.04"),
        "PR": Decimal("0.05"),
        "SC": Decimal("0.03"),
        "BA": Decimal("0.05"),
        "PE": Decimal("0.05"),
        "CE": Decimal("0.05"),
        "DF": Decimal("0.05"),
    }

    def calculate(  # pylint: disable=too-many-locals
        self, pricing_input: PricingInput
    ) -> PricingResult:
        """
        Calcula preco completo com todos os componentes.

        Args:
            pricing_input: Dados de entrada para precificacao

        Returns:
            PricingResult com todos os valores calculados

        Raises:
            ValueError: Se dados de entrada invalidos
        """
        self._validate_input(pricing_input)

        # Calcular custos base
        costs = self._calculate_costs(pricing_input)

        # Calcular impostos e preco final
        pricing = self._calculate_final_price(pricing_input, costs)

        logger.info(
            "Precificacao calculada",
            extra={
                "headcount": pricing_input.headcount,
                "months": pricing_input.contract_months,
                "total": str(pricing["total_contract"]),
                "margin": str(pricing["effective_margin"]),
            },
        )

        return PricingResult(
            base_cost=costs["base_cost"],
            cct_value=costs["cct_value"],
            cct_percent=costs["cct_percent"],
            labor_cost=costs["labor_cost"],
            benefits_cost=costs["benefits_cost"],
            equipment_cost=costs["equipment_cost"],
            total_cost=costs["total_cost"],
            tax_amount=pricing["tax_amount"],
            tax_breakdown=pricing["tax_breakdown"],
            margin_value=pricing["margin_value"],
            margin_percent=pricing["effective_margin"],
            unit_price=pricing["unit_price"],
            total_monthly=pricing["total_monthly"],
            total_contract=pricing["total_contract"],
        )

    def _calculate_costs(self, pricing_input: PricingInput) -> dict[str, Decimal]:
        """Calcula custos base, CCT, mao de obra e adicionais."""
        base_cost = pricing_input.base_salary * pricing_input.headcount * pricing_input.contract_months

        cct_percent = self._calculate_cct_percent()
        cct_value = base_cost * cct_percent
        labor_cost = base_cost + cct_value

        benefits_cost = pricing_input.benefits_value * pricing_input.headcount * pricing_input.contract_months
        equipment_cost = pricing_input.equipment_value
        total_cost = labor_cost + benefits_cost + equipment_cost

        return {
            "base_cost": self._round(base_cost),
            "cct_percent": self._round(cct_percent * Decimal("100")),
            "cct_value": self._round(cct_value),
            "labor_cost": self._round(labor_cost),
            "benefits_cost": self._round(benefits_cost),
            "equipment_cost": self._round(equipment_cost),
            "total_cost": self._round(total_cost),
        }

    def _calculate_final_price(self, pricing_input: PricingInput, costs: dict[str, Decimal]) -> dict[str, Decimal]:
        """Calcula preco final com impostos e margem."""
        total_cost = costs["total_cost"]
        margin_value = total_cost * (pricing_input.margin_target / Decimal("100"))
        price_before_tax = total_cost + margin_value

        taxes = self._get_tax_rates(pricing_input.service_type, pricing_input.client_state)
        total_tax_rate = sum(taxes.values())

        total_contract = price_before_tax / (Decimal("1") - total_tax_rate)
        tax_amount = total_contract - price_before_tax

        tax_breakdown = {name: self._round(total_contract * rate) for name, rate in taxes.items()}

        total_monthly = total_contract / pricing_input.contract_months
        unit_price = total_monthly / pricing_input.headcount
        effective_margin = (total_contract - total_cost - tax_amount) / total_contract * Decimal("100")

        return {
            "margin_value": self._round(margin_value),
            "tax_amount": self._round(tax_amount),
            "tax_breakdown": tax_breakdown,
            "effective_margin": self._round(effective_margin),
            "unit_price": self._round(unit_price),
            "total_monthly": self._round(total_monthly),
            "total_contract": self._round(total_contract),
        }

    def calculate_cct_breakdown(self, base_salary: Decimal, headcount: int, months: int) -> dict[str, Decimal]:
        """
        Calcula detalhamento de cada componente do CCT.

        Args:
            base_salary: Salario base mensal
            headcount: Numero de funcionarios
            months: Duracao em meses

        Returns:
            Dicionario com valor de cada encargo
        """
        base = base_salary * headcount * months
        return {name: self._round(base * rate) for name, rate in self.CCT_COMPONENTS.items()}

    def estimate_margin(self, selling_price: Decimal, total_cost: Decimal, tax_amount: Decimal) -> Decimal:
        """
        Estima margem dado um preco de venda.

        Args:
            selling_price: Preco de venda
            total_cost: Custo total
            tax_amount: Valor de impostos

        Returns:
            Margem efetiva em percentual
        """
        if selling_price <= 0:
            return Decimal("0.00")

        margin = (selling_price - total_cost - tax_amount) / selling_price * Decimal("100")
        return self._round(margin)

    def simulate_price(
        self,
        pricing_input: PricingInput,
        target_price: Decimal | None = None,
        custom_margins: list[Decimal] | None = None,
    ) -> list[PricingResult]:
        """
        Simula diferentes cenarios de precificacao.

        Args:
            pricing_input: Dados base
            target_price: Preco alvo para calculo reverso de margem
            custom_margins: Lista de margens customizadas para simular

        Returns:
            Lista de resultados simulados
        """
        results = []

        # Cenario base
        base_result = self.calculate(pricing_input)
        results.append(base_result)

        # Se preco alvo fornecido, calcular margem necessaria
        if target_price is not None:
            reverse_margin = self._reverse_margin_from_price(pricing_input, target_price)
            if reverse_margin is not None:
                modified_input = PricingInput(
                    base_salary=pricing_input.base_salary,
                    headcount=pricing_input.headcount,
                    contract_months=pricing_input.contract_months,
                    service_type=pricing_input.service_type,
                    client_state=pricing_input.client_state,
                    margin_target=reverse_margin,
                    benefits_value=pricing_input.benefits_value,
                    equipment_value=pricing_input.equipment_value,
                )
                results.append(self.calculate(modified_input))

        # Simulacao com margens diferentes
        margins = custom_margins or [
            Decimal("10"),
            Decimal("15"),
            Decimal("20"),
            Decimal("25"),
            Decimal("30"),
        ]
        for margin in margins:
            if margin != pricing_input.margin_target:
                modified_input = PricingInput(
                    base_salary=pricing_input.base_salary,
                    headcount=pricing_input.headcount,
                    contract_months=pricing_input.contract_months,
                    service_type=pricing_input.service_type,
                    client_state=pricing_input.client_state,
                    margin_target=margin,
                    benefits_value=pricing_input.benefits_value,
                    equipment_value=pricing_input.equipment_value,
                )
                results.append(self.calculate(modified_input))

        return results

    def _reverse_margin_from_price(self, pricing_input: PricingInput, target_price: Decimal) -> Decimal | None:
        """Calcula margem necessaria para atingir preco alvo."""
        costs = self._calculate_costs(pricing_input)
        total_cost = costs["total_cost"]

        taxes = self._get_tax_rates(pricing_input.service_type, pricing_input.client_state)
        total_tax_rate = sum(taxes.values())

        # preco = (custo + margem) / (1 - taxa)
        # custo + margem = preco * (1 - taxa)
        # margem = preco * (1 - taxa) - custo
        margin_value = target_price * (Decimal("1") - total_tax_rate) - total_cost

        if margin_value < 0 or total_cost == 0:
            return None

        margin_percent = margin_value / total_cost * Decimal("100")
        return self._round(margin_percent)

    def _validate_input(self, data: PricingInput) -> None:
        """Valida dados de entrada."""
        if data.base_salary <= 0:
            raise ValueError("Salario base deve ser positivo")
        if data.headcount <= 0:
            raise ValueError("Headcount deve ser positivo")
        if data.contract_months <= 0:
            raise ValueError("Meses de contrato deve ser positivo")
        if data.margin_target < 0:
            raise ValueError("Margem nao pode ser negativa")

    def _calculate_cct_percent(self) -> Decimal:
        """Calcula percentual total de CCT."""
        return sum(self.CCT_COMPONENTS.values())

    def _get_tax_rates(self, service_type: str, client_state: str) -> dict[str, Decimal]:
        """
        Retorna taxas de impostos do servico.

        Args:
            service_type: Tipo de servico
            client_state: Estado do cliente

        Returns:
            Dicionario com taxas por imposto
        """
        rates = self.TAX_RATES.get(service_type, self.TAX_RATES["default"]).copy()

        # Ajustar ISS pelo estado se necessario
        if client_state in self.ISS_BY_STATE:
            rates["iss"] = self.ISS_BY_STATE[client_state]

        return rates

    def _round(self, value: Decimal) -> Decimal:
        """Arredonda para 2 casas decimais."""
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# Instancia global
pricing_engine = PricingEngine()
