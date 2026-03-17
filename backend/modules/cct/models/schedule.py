"""
Jornadas e Adicionais CCT 2026 — SINDECOMPRESTS/SINDICOND-AM.

Jornadas permitidas, divisores, hora noturna reduzida, adicionais.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class TipoJornadaCCT(StrEnum):
    """Tipos de jornada previstos na CCT."""

    PADRAO_44H = "44h_semanais"
    CORRIDA_36H = "36h_corridas"
    ESCALA_12X36 = "12x36"


@dataclass(frozen=True)
class JornadaCCT:
    """Configuracao de jornada conforme CCT."""

    tipo: TipoJornadaCCT
    carga_semanal: int
    divisor_mensal: int
    descricao: str


JORNADAS_PERMITIDAS: tuple[JornadaCCT, ...] = (
    JornadaCCT(
        tipo=TipoJornadaCCT.PADRAO_44H,
        carga_semanal=44,
        divisor_mensal=220,
        descricao="Jornada padrao 44h semanais — divisor 220h",
    ),
    JornadaCCT(
        tipo=TipoJornadaCCT.CORRIDA_36H,
        carga_semanal=36,
        divisor_mensal=180,
        descricao="Jornada 36h corridas — divisor 180h",
    ),
    JornadaCCT(
        tipo=TipoJornadaCCT.ESCALA_12X36,
        carga_semanal=36,
        divisor_mensal=180,
        descricao="Escala 12x36 — divisor 180h — PREDOMINANTE na Conecta Mais",
    ),
)


# Escala proibida
ESCALA_PROIBIDA_2X1 = "2x1"
ESCALA_PROIBIDA_FUNDAMENTACAO = "TAC MPT 11a Regiao"


@dataclass(frozen=True)
class AdicionaisCCT:
    """Percentuais de adicionais conforme CCT."""

    # Hora noturna
    hora_noturna_minutos: Decimal = Decimal("52.5")
    adicional_noturno_percentual: Decimal = Decimal("20.0")

    # Hora extra
    hora_extra_normal_percentual: Decimal = Decimal("50.0")
    hora_extra_feriado_percentual: Decimal = Decimal("100.0")

    # Intrajornada nao concedida
    intrajornada_nao_concedida_horas: Decimal = Decimal("1.0")
    intrajornada_nao_concedida_percentual: Decimal = Decimal("50.0")

    # Ronda permanente
    ronda_permanente_percentual: Decimal = Decimal("15.0")
    ronda_permanente_pre_2020_percentual: Decimal = Decimal("30.0")

    # Acumulo de funcao
    acumulo_funcao_percentual: Decimal = Decimal("30.0")

    # Servicos jardinagem/piscina (servicos gerais)
    servicos_jardinagem_piscina_percentual: Decimal = Decimal("10.0")

    # Insalubridade e periculosidade
    insalubridade_minimo_percentual: Decimal = Decimal("10.0")
    periculosidade_percentual: Decimal = Decimal("30.0")


ADICIONAIS = AdicionaisCCT()


def get_jornada_by_tipo(tipo: TipoJornadaCCT) -> JornadaCCT | None:
    """Busca configuracao de jornada pelo tipo."""
    for jornada in JORNADAS_PERMITIDAS:
        if jornada.tipo == tipo:
            return jornada
    return None


def get_divisor_mensal(tipo: TipoJornadaCCT) -> int:
    """Retorna o divisor mensal para calculo de hora normal."""
    jornada = get_jornada_by_tipo(tipo)
    if jornada:
        return jornada.divisor_mensal
    return 220
