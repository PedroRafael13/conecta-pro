"""
Schemas para cálculos de FGTS e INSS.
"""

from decimal import Decimal

from pydantic import BaseModel, Field


class CalculoFGTSRequest(BaseModel):
    """Request para cálculo de FGTS.

    Attributes:
        salario_base: Salário base mensal.
        mes_referencia: Mês de referência (YYYY-MM).
        tipo_recolhimento: Tipo de recolhimento.
        rescisao: Se é cálculo de rescisão.
    """

    salario_base: Decimal = Field(
        ...,
        gt=0,
        description="Salario base mensal",
    )
    mes_referencia: str = Field(
        ...,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
        description="Mes de referencia (YYYY-MM)",
    )
    tipo_recolhimento: str = Field(
        default="mensal",
        description="Tipo de recolhimento",
        pattern=r"^(mensal|rescisorio|complementar)$",
    )
    rescisao: bool = Field(
        default=False,
        description="Se e calculo de rescisao (inclui multa 40%)",
    )


class CalculoINSSRequest(BaseModel):
    """Request para cálculo de INSS.

    Attributes:
        salario_bruto: Salário bruto mensal.
        categoria: Categoria do contribuinte.
        mes_referencia: Mês de referência.
    """

    salario_bruto: Decimal = Field(
        ...,
        gt=0,
        description="Salario bruto mensal",
    )
    categoria: str = Field(
        default="empregado",
        description="Categoria do contribuinte",
        pattern=r"^(empregado|domestico|contribuinte_individual|facultativo|mei)$",
    )
    mes_referencia: str = Field(
        ...,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
        description="Mes de referencia (YYYY-MM)",
    )
