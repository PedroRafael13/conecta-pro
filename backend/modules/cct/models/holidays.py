"""
Feriados Manaus/AM 2026 — CCT SINDECOMPRESTS/SINDICOND-AM.

16 feriados oficiais (nacionais + estaduais AM + municipais Manaus).
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FeriadoCCT:
    """Feriado previsto na CCT."""

    data: date
    nome: str
    tipo: str  # nacional, estadual, municipal


FERIADOS_MANAUS_2026: tuple[FeriadoCCT, ...] = (
    FeriadoCCT(date(2026, 1, 1), "Confraternizacao Universal", "nacional"),
    FeriadoCCT(date(2026, 2, 17), "Carnaval (terca-feira)", "nacional"),
    FeriadoCCT(date(2026, 2, 18), "Carnaval (quarta ate 12h)", "nacional"),
    FeriadoCCT(date(2026, 4, 3), "Sexta-feira Santa", "nacional"),
    FeriadoCCT(date(2026, 4, 21), "Tiradentes", "nacional"),
    FeriadoCCT(date(2026, 5, 1), "Dia do Trabalho", "nacional"),
    FeriadoCCT(date(2026, 6, 4), "Corpus Christi", "nacional"),
    FeriadoCCT(date(2026, 9, 5), "Elevacao do Amazonas a Categoria de Provincia", "estadual"),
    FeriadoCCT(date(2026, 9, 7), "Independencia do Brasil", "nacional"),
    FeriadoCCT(date(2026, 10, 12), "Nossa Senhora Aparecida", "nacional"),
    FeriadoCCT(date(2026, 10, 24), "Aniversario de Manaus", "municipal"),
    FeriadoCCT(date(2026, 11, 2), "Finados", "nacional"),
    FeriadoCCT(date(2026, 11, 15), "Proclamacao da Republica", "nacional"),
    FeriadoCCT(date(2026, 11, 20), "Consciencia Negra", "municipal"),
    FeriadoCCT(date(2026, 12, 8), "Nossa Senhora da Conceicao", "estadual"),
    FeriadoCCT(date(2026, 12, 25), "Natal", "nacional"),
)


def is_feriado(dt: date) -> FeriadoCCT | None:
    """Verifica se uma data e feriado em Manaus/AM."""
    for feriado in FERIADOS_MANAUS_2026:
        if feriado.data == dt:
            return feriado
    return None


def get_feriados_mes(mes: int) -> list[FeriadoCCT]:
    """Retorna feriados de um mes especifico."""
    return [f for f in FERIADOS_MANAUS_2026 if f.data.month == mes]


def get_feriados_periodo(inicio: date, fim: date) -> list[FeriadoCCT]:
    """Retorna feriados dentro de um periodo."""
    return [f for f in FERIADOS_MANAUS_2026 if inicio <= f.data <= fim]
