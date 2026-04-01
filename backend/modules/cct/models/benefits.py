"""
Beneficios Obrigatorios CCT 2026 — SINDECOMPRESTS/SINDICOND-AM.

Define valores minimos, descontos maximos e regras de cada beneficio.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class TipoBeneficioCCT(StrEnum):
    """Tipos de beneficio previstos na CCT."""

    VALE_TRANSPORTE = "vale_transporte"
    VALE_REFEICAO = "vale_refeicao"
    PLANO_ODONTOLOGICO = "plano_odontologico"
    SEGURO_VIDA = "seguro_vida"
    AUXILIO_FUNERAL = "auxilio_funeral"
    AJUDA_MEDICAMENTO = "ajuda_medicamento"
    CESTA_BASICA = "cesta_basica"
    EMPRESTIMO_CONSIGNADO = "emprestimo_consignado"


@dataclass(frozen=True)
class BeneficioCCT:
    """Configuracao de um beneficio conforme CCT."""

    tipo: TipoBeneficioCCT
    obrigatorio: bool
    valor_total: Decimal | None = None
    valor_empresa: Decimal | None = None
    desconto_maximo_empregado: Decimal | None = None
    desconto_percentual: Decimal | None = None
    observacao: str = ""


BENEFICIOS_OBRIGATORIOS_CCT: tuple[BeneficioCCT, ...] = (
    BeneficioCCT(
        tipo=TipoBeneficioCCT.VALE_TRANSPORTE,
        obrigatorio=True,
        desconto_percentual=Decimal("4.0"),
        observacao="Desconto 4% salario base. Pode ser substituido por auxilio-combustivel mesmo desconto.",
    ),
    BeneficioCCT(
        tipo=TipoBeneficioCCT.VALE_REFEICAO,
        obrigatorio=True,
        valor_total=Decimal("22.00"),
        desconto_percentual=Decimal("1.0"),
        observacao="R$ 22,00/dia minimo. Desconto 1% salario base.",
    ),
    BeneficioCCT(
        tipo=TipoBeneficioCCT.PLANO_ODONTOLOGICO,
        obrigatorio=True,
        valor_total=Decimal("18.00"),
        valor_empresa=Decimal("9.00"),
        desconto_maximo_empregado=Decimal("9.00"),
        observacao="R$ 18,00/trabalhador. Empresa paga minimo R$ 9,00. Desconto max R$ 9,00.",
    ),
    BeneficioCCT(
        tipo=TipoBeneficioCCT.SEGURO_VIDA,
        obrigatorio=True,
        valor_total=Decimal("6.00"),
        valor_empresa=Decimal("4.00"),
        desconto_maximo_empregado=Decimal("2.00"),
        observacao="R$ 6,00 total. Empresa R$ 4,00. Desconto trabalhador ate R$ 2,00.",
    ),
    BeneficioCCT(
        tipo=TipoBeneficioCCT.AUXILIO_FUNERAL,
        obrigatorio=True,
        valor_total=Decimal("400.00"),
        observacao="R$ 400,00 (trabalhador, conjuge, dependentes).",
    ),
    BeneficioCCT(
        tipo=TipoBeneficioCCT.AJUDA_MEDICAMENTO,
        obrigatorio=True,
        valor_total=Decimal("300.00"),
        observacao="Ate R$ 300,00/mes em caso de acidente de trabalho.",
    ),
    BeneficioCCT(
        tipo=TipoBeneficioCCT.CESTA_BASICA,
        obrigatorio=False,
        valor_total=Decimal("170.00"),
        observacao="R$ 120,00 a R$ 170,00 (nao incorpora salario). Opcional.",
    ),
    BeneficioCCT(
        tipo=TipoBeneficioCCT.EMPRESTIMO_CONSIGNADO,
        obrigatorio=False,
        desconto_percentual=Decimal("30.0"),
        observacao="Teto 30% dos ganhos mensais. Opcional.",
    ),
)


@dataclass(frozen=True)
class TaxaNegocial:
    """Taxa negocial sindical 2026."""

    valor: Decimal
    meses: tuple[int, ...]
    prazo_oposicao_dia: int
    observacao: str


TAXA_NEGOCIAL_2026 = TaxaNegocial(
    valor=Decimal("22.00"),
    meses=(1, 3, 5, 7, 9, 11),
    prazo_oposicao_dia=20,
    observacao="R$ 22,00 nos meses jan, mar, mai, jul, set, nov. Trabalhador pode se opor via carta ate dia 20.",
)


def get_beneficio_by_tipo(tipo: TipoBeneficioCCT) -> BeneficioCCT | None:
    """Busca configuracao de beneficio pelo tipo."""
    for beneficio in BENEFICIOS_OBRIGATORIOS_CCT:
        if beneficio.tipo == tipo:
            return beneficio
    return None


def get_beneficios_obrigatorios() -> list[BeneficioCCT]:
    """Retorna apenas beneficios obrigatorios."""
    return [b for b in BENEFICIOS_OBRIGATORIOS_CCT if b.obrigatorio]
