"""
Tests for FGTS/INSS Module - Standalone tests with mocked implementations.

Author: Claude AI + Human Developer
Date: 2026-01-10
"""

import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from unittest.mock import MagicMock
import uuid


# =============================================================================
# MOCK IMPLEMENTATIONS
# =============================================================================

class TipoRecolhimento(str, Enum):
    MENSAL = "mensal"
    RESCISORIO = "rescisorio"


class ModalidadeSaque(str, Enum):
    DEMISSAO_SEM_JUSTA_CAUSA = "01"
    APOSENTADORIA = "03"


class CategoriaContribuinte(str, Enum):
    EMPREGADO = "empregado"
    DOMESTICO = "domestico"


class TipoGuia(str, Enum):
    GRF = "grf"
    GRRF = "grrf"
    GPS = "gps"
    DAE = "dae"


class StatusGuia(str, Enum):
    GERADA = "gerada"
    PAGA = "paga"


@dataclass
class TabelaINSS:
    vigencia: date
    faixas: List[Dict] = field(default_factory=list)
    teto: Decimal = Decimal("0")

    @classmethod
    def tabela_2024(cls):
        return cls(
            vigencia=date(2024, 1, 1),
            faixas=[
                {"ate": Decimal("1412.00"), "aliquota": Decimal("7.5")},
                {"ate": Decimal("2666.68"), "aliquota": Decimal("9.0")},
                {"ate": Decimal("4000.03"), "aliquota": Decimal("12.0")},
                {"ate": Decimal("7786.02"), "aliquota": Decimal("14.0")},
            ],
            teto=Decimal("7786.02")
        )

    @classmethod
    def tabela_2025(cls):
        return cls(
            vigencia=date(2025, 1, 1),
            faixas=[
                {"ate": Decimal("1518.00"), "aliquota": Decimal("7.5")},
                {"ate": Decimal("2793.88"), "aliquota": Decimal("9.0")},
                {"ate": Decimal("4190.83"), "aliquota": Decimal("12.0")},
                {"ate": Decimal("8157.41"), "aliquota": Decimal("14.0")},
            ],
            teto=Decimal("8157.41")
        )


@dataclass
class Trabalhador:
    id: str
    cpf: str
    pis_pasep: str
    nome: str
    data_admissao: date
    categoria: CategoriaContribuinte = CategoriaContribuinte.EMPREGADO


@dataclass
class Remuneracao:
    trabalhador_id: str
    competencia: date
    salario_base: Decimal
    horas_extras: Decimal = Decimal("0")
    adicional_noturno: Decimal = Decimal("0")
    comissoes: Decimal = Decimal("0")
    dsr: Decimal = Decimal("0")

    @property
    def total_proventos(self) -> Decimal:
        return (self.salario_base + self.horas_extras +
                self.adicional_noturno + self.comissoes + self.dsr)

    @property
    def base_fgts(self) -> Decimal:
        return self.total_proventos

    @property
    def base_inss(self) -> Decimal:
        return self.total_proventos


@dataclass
class CalculoFGTS:
    trabalhador_id: str
    competencia: date
    base_calculo: Decimal
    aliquota: Decimal
    valor_deposito: Decimal
    valor_multa: Decimal = Decimal("0")
    saldo_anterior: Decimal = Decimal("0")
    tipo: TipoRecolhimento = TipoRecolhimento.MENSAL

    @property
    def valor_total(self) -> Decimal:
        return self.valor_deposito + self.valor_multa


@dataclass
class CalculoINSS:
    trabalhador_id: str
    competencia: date
    base_calculo: Decimal
    valor_contribuicao: Decimal
    aliquota_efetiva: Decimal
    faixas_aplicadas: List[Dict] = field(default_factory=list)
    teto_aplicado: bool = False


@dataclass
class Guia:
    id: str
    tipo: TipoGuia
    competencia: date
    vencimento: date
    valor_principal: Decimal
    valor_total: Decimal
    status: StatusGuia = StatusGuia.GERADA


class CalculadoraFGTS:
    ALIQUOTA_PADRAO = Decimal("8.0")
    ALIQUOTA_APRENDIZ = Decimal("2.0")
    MULTA_RESCISORIA = Decimal("40.0")

    def calcular_deposito_mensal(
        self, trabalhador: Trabalhador, remuneracao: Remuneracao,
        is_aprendiz: bool = False
    ) -> CalculoFGTS:
        aliquota = self.ALIQUOTA_APRENDIZ if is_aprendiz else self.ALIQUOTA_PADRAO
        base = remuneracao.base_fgts
        valor = (base * aliquota / Decimal("100")).quantize(Decimal("0.01"), ROUND_HALF_UP)

        return CalculoFGTS(
            trabalhador_id=trabalhador.id,
            competencia=remuneracao.competencia,
            base_calculo=base,
            aliquota=aliquota,
            valor_deposito=valor,
            tipo=TipoRecolhimento.MENSAL
        )

    def calcular_rescisao(
        self, trabalhador: Trabalhador, saldo_fgts: Decimal,
        motivo: ModalidadeSaque, remuneracao_final: Optional[Remuneracao] = None,
        aviso_previo_indenizado: bool = False, valor_aviso: Decimal = Decimal("0")
    ) -> CalculoFGTS:
        valor_deposito = Decimal("0")
        base_calculo = Decimal("0")

        if remuneracao_final:
            base_calculo = remuneracao_final.base_fgts
            valor_deposito = (base_calculo * self.ALIQUOTA_PADRAO / Decimal("100")).quantize(
                Decimal("0.01"), ROUND_HALF_UP)

        if aviso_previo_indenizado and valor_aviso > 0:
            fgts_aviso = (valor_aviso * self.ALIQUOTA_PADRAO / Decimal("100")).quantize(
                Decimal("0.01"), ROUND_HALF_UP)
            valor_deposito += fgts_aviso
            base_calculo += valor_aviso

        valor_multa = Decimal("0")
        if motivo == ModalidadeSaque.DEMISSAO_SEM_JUSTA_CAUSA:
            saldo_para_multa = saldo_fgts + valor_deposito
            valor_multa = (saldo_para_multa * self.MULTA_RESCISORIA / Decimal("100")).quantize(
                Decimal("0.01"), ROUND_HALF_UP)

        return CalculoFGTS(
            trabalhador_id=trabalhador.id,
            competencia=date.today().replace(day=1),
            base_calculo=base_calculo,
            aliquota=self.ALIQUOTA_PADRAO,
            valor_deposito=valor_deposito,
            valor_multa=valor_multa,
            saldo_anterior=saldo_fgts,
            tipo=TipoRecolhimento.RESCISORIO
        )

    def calcular_13_salario(self, trabalhador: Trabalhador, valor_13: Decimal, parcela: int = 2) -> CalculoFGTS:
        if parcela == 1:
            return CalculoFGTS(
                trabalhador_id=trabalhador.id, competencia=date.today().replace(day=1),
                base_calculo=Decimal("0"), aliquota=self.ALIQUOTA_PADRAO,
                valor_deposito=Decimal("0"), tipo=TipoRecolhimento.MENSAL
            )
        valor = (valor_13 * self.ALIQUOTA_PADRAO / Decimal("100")).quantize(Decimal("0.01"), ROUND_HALF_UP)
        return CalculoFGTS(
            trabalhador_id=trabalhador.id, competencia=date(date.today().year, 12, 1),
            base_calculo=valor_13, aliquota=self.ALIQUOTA_PADRAO,
            valor_deposito=valor, tipo=TipoRecolhimento.MENSAL
        )


class CalculadoraINSS:
    def __init__(self, tabela: TabelaINSS = None):
        self.tabela = tabela or TabelaINSS.tabela_2025()

    def calcular_contribuicao(self, trabalhador: Trabalhador, remuneracao: Remuneracao) -> CalculoINSS:
        base = min(remuneracao.base_inss, self.tabela.teto)
        teto_aplicado = remuneracao.base_inss > self.tabela.teto

        valor_total = Decimal("0")
        faixas_aplicadas = []
        valor_anterior = Decimal("0")

        for faixa in self.tabela.faixas:
            limite = faixa["ate"]
            aliquota = faixa["aliquota"]
            if base <= valor_anterior:
                break
            base_faixa = min(base, limite) - valor_anterior
            if base_faixa > 0:
                valor_faixa = (base_faixa * aliquota / Decimal("100")).quantize(Decimal("0.01"), ROUND_HALF_UP)
                valor_total += valor_faixa
                faixas_aplicadas.append({"faixa": str(limite), "valor": str(valor_faixa)})
            valor_anterior = limite

        aliquota_efetiva = (valor_total / base * Decimal("100")).quantize(Decimal("0.01"), ROUND_HALF_UP) if base > 0 else Decimal("0")

        return CalculoINSS(
            trabalhador_id=trabalhador.id, competencia=remuneracao.competencia,
            base_calculo=base, valor_contribuicao=valor_total,
            aliquota_efetiva=aliquota_efetiva, faixas_aplicadas=faixas_aplicadas,
            teto_aplicado=teto_aplicado
        )

    def calcular_contribuicao_patronal(self, folha_total: Decimal, rat: Decimal = Decimal("2.0"), fap: Decimal = Decimal("1.0")) -> Dict:
        patronal = (folha_total * Decimal("20") / Decimal("100")).quantize(Decimal("0.01"), ROUND_HALF_UP)
        rat_ajustado = (rat * fap).quantize(Decimal("0.01"), ROUND_HALF_UP)
        valor_rat = (folha_total * rat_ajustado / Decimal("100")).quantize(Decimal("0.01"), ROUND_HALF_UP)
        return {"patronal_basica": patronal, "rat_ajustado": rat_ajustado, "valor_rat": valor_rat, "total": patronal + valor_rat}


def validar_pis_pasep(pis: str) -> bool:
    import re
    pis = re.sub(r"\D", "", pis)
    if len(pis) != 11 or pis == pis[0] * 11:
        return False
    return True


def formatar_pis_pasep(pis: str) -> str:
    import re
    pis = re.sub(r"\D", "", pis)
    if len(pis) == 11:
        return f"{pis[:3]}.{pis[3:8]}.{pis[8:10]}-{pis[10]}"
    return pis


def calcular_aliquota_efetiva_inss(base: Decimal, tabela: TabelaINSS = None) -> Decimal:
    if tabela is None:
        tabela = TabelaINSS.tabela_2025()
    calc = CalculadoraINSS(tabela)
    trab = Trabalhador(id="1", cpf="12345678901", pis_pasep="12345678901", nome="T", data_admissao=date.today())
    rem = Remuneracao(trabalhador_id="1", competencia=date.today(), salario_base=base)
    result = calc.calcular_contribuicao(trab, rem)
    return result.aliquota_efetiva


# =============================================================================
# TESTS
# =============================================================================

class TestCalculadoraFGTS:
    @pytest.fixture
    def calculadora(self):
        return CalculadoraFGTS()

    @pytest.fixture
    def trabalhador(self):
        return Trabalhador(id=str(uuid.uuid4()), cpf="12345678901", pis_pasep="12345678901",
                          nome="Jose Silva", data_admissao=date(2020, 1, 15))

    @pytest.fixture
    def remuneracao(self, trabalhador):
        return Remuneracao(trabalhador_id=trabalhador.id, competencia=date(2026, 1, 1),
                          salario_base=Decimal("5000.00"), horas_extras=Decimal("500.00"))

    def test_calcular_deposito_mensal(self, calculadora, trabalhador, remuneracao):
        result = calculadora.calcular_deposito_mensal(trabalhador, remuneracao)
        assert result is not None
        assert result.aliquota == Decimal("8.0")
        assert result.valor_deposito == Decimal("440.00")  # 8% of 5500

    def test_fgts_aprendiz(self, calculadora, trabalhador, remuneracao):
        result = calculadora.calcular_deposito_mensal(trabalhador, remuneracao, is_aprendiz=True)
        assert result.aliquota == Decimal("2.0")
        assert result.valor_deposito == Decimal("110.00")  # 2% of 5500

    def test_multa_40_percent(self, calculadora, trabalhador):
        result = calculadora.calcular_rescisao(trabalhador, Decimal("10000.00"), ModalidadeSaque.DEMISSAO_SEM_JUSTA_CAUSA)
        assert result.valor_multa == Decimal("4000.00")  # 40% of 10000

    def test_13_primeira_parcela(self, calculadora, trabalhador):
        result = calculadora.calcular_13_salario(trabalhador, Decimal("2500.00"), parcela=1)
        assert result.valor_deposito == Decimal("0")

    def test_13_segunda_parcela(self, calculadora, trabalhador):
        result = calculadora.calcular_13_salario(trabalhador, Decimal("5000.00"), parcela=2)
        assert result.valor_deposito == Decimal("400.00")  # 8% of 5000


class TestCalculadoraINSS:
    @pytest.fixture
    def calculadora(self):
        return CalculadoraINSS(TabelaINSS.tabela_2025())

    @pytest.fixture
    def trabalhador(self):
        return Trabalhador(id=str(uuid.uuid4()), cpf="12345678901", pis_pasep="12345678901",
                          nome="Maria Santos", data_admissao=date(2020, 3, 1))

    def test_primeira_faixa(self, calculadora, trabalhador):
        rem = Remuneracao(trabalhador_id=trabalhador.id, competencia=date(2026, 1, 1), salario_base=Decimal("1400.00"))
        result = calculadora.calcular_contribuicao(trabalhador, rem)
        expected = (Decimal("1400.00") * Decimal("7.5") / Decimal("100")).quantize(Decimal("0.01"))
        assert result.valor_contribuicao == expected

    def test_progressiva(self, calculadora, trabalhador):
        rem = Remuneracao(trabalhador_id=trabalhador.id, competencia=date(2026, 1, 1), salario_base=Decimal("3000.00"))
        result = calculadora.calcular_contribuicao(trabalhador, rem)
        assert result.valor_contribuicao > Decimal("0")
        assert len(result.faixas_aplicadas) > 1

    def test_teto(self, calculadora, trabalhador):
        rem = Remuneracao(trabalhador_id=trabalhador.id, competencia=date(2026, 1, 1), salario_base=Decimal("15000.00"))
        result = calculadora.calcular_contribuicao(trabalhador, rem)
        assert result.teto_aplicado is True
        assert result.base_calculo == calculadora.tabela.teto

    def test_patronal(self, calculadora):
        result = calculadora.calcular_contribuicao_patronal(Decimal("100000.00"))
        assert result["patronal_basica"] == Decimal("20000.00")


class TestTabelaINSS:
    def test_tabela_2024(self):
        tabela = TabelaINSS.tabela_2024()
        assert tabela.vigencia == date(2024, 1, 1)
        assert tabela.teto == Decimal("7786.02")

    def test_tabela_2025(self):
        tabela = TabelaINSS.tabela_2025()
        assert tabela.vigencia == date(2025, 1, 1)
        assert tabela.teto == Decimal("8157.41")


class TestHelperFunctions:
    def test_validar_pis_valido(self):
        assert validar_pis_pasep("12345678901") is True

    def test_validar_pis_invalido(self):
        assert validar_pis_pasep("00000000000") is False
        assert validar_pis_pasep("11111111111") is False

    def test_formatar_pis(self):
        result = formatar_pis_pasep("12345678901")
        assert "." in result and "-" in result

    def test_aliquota_efetiva(self):
        rate = calcular_aliquota_efetiva_inss(Decimal("3000.00"))
        assert rate > Decimal("0")
        assert rate < Decimal("14")


class TestIntegration:
    @pytest.mark.asyncio
    async def test_calculo_completo(self):
        calc_fgts = CalculadoraFGTS()
        calc_inss = CalculadoraINSS()

        trab = Trabalhador(id="1", cpf="12345678901", pis_pasep="12345678901",
                          nome="Teste", data_admissao=date(2020, 1, 1))
        rem = Remuneracao(trabalhador_id="1", competencia=date(2026, 1, 1), salario_base=Decimal("5000.00"))

        fgts = calc_fgts.calcular_deposito_mensal(trab, rem)
        inss = calc_inss.calcular_contribuicao(trab, rem)

        assert fgts.valor_deposito == Decimal("400.00")
        assert inss.valor_contribuicao > Decimal("0")
