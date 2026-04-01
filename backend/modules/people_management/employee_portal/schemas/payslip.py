"""
Schemas para consulta de contracheques do funcionario.
"""

from pydantic import BaseModel, ConfigDict


class PayslipItem(BaseModel):
    """Item individual do contracheque (provento ou desconto).

    Attributes:
        description: Descricao do item (ex: Salario Base, INSS, IRRF).
        type: Tipo (provento ou desconto).
        reference: Referencia (horas, percentual, etc.).
        value: Valor em reais.
    """

    description: str
    type: str = "provento"  # provento | desconto
    reference: str | None = None
    value: float

    model_config = ConfigDict(from_attributes=True)


class MyPayslipResponse(BaseModel):
    """Resposta com dados do contracheque do funcionario.

    Attributes:
        month: Mes de referencia (1-12).
        year: Ano de referencia.
        gross_salary: Salario bruto total.
        deductions: Total de descontos.
        net_salary: Salario liquido (bruto - descontos).
        items: Lista detalhada de proventos e descontos.
    """

    month: int
    year: int
    gross_salary: float
    deductions: float
    net_salary: float
    items: list[PayslipItem] = []

    model_config = ConfigDict(from_attributes=True)
