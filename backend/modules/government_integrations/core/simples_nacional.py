"""
Simples Nacional - Regime Especial Unificado de Arrecadação.

Portal: https://www8.receita.fazenda.gov.br/SimplesNacional/
Documentação: Manual do PGDAS-D

O Simples Nacional unifica 8 tributos em uma única guia (DAS):
- IRPJ, CSLL, PIS, COFINS (Federal)
- ICMS (Estadual)
- ISS (Municipal)
- CPP (Contribuição Patronal Previdenciária)

Funcionalidades:
- PGDAS-D (Programa Gerador do DAS Declaratório)
- Geração de DAS
- DEFIS (Declaração de Informações Socioeconômicas e Fiscais)
- Consulta de pendências
- Parcelamentos
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class AnexoSimples(StrEnum):
    """Anexos do Simples Nacional."""

    ANEXO_I = "I"  # Comércio
    ANEXO_II = "II"  # Indústria
    ANEXO_III = "III"  # Serviços (ex: vigilância, limpeza, locação de mão de obra)
    ANEXO_IV = "IV"  # Serviços (construção, vigilância, advocacia)
    ANEXO_V = "V"  # Serviços (TI, engenharia, publicidade)


class SituacaoOpcao(StrEnum):
    """Situação da opção pelo Simples Nacional."""

    OPTANTE = "optante"
    NAO_OPTANTE = "nao_optante"
    EXCLUIDO = "excluido"
    IMPEDIDO = "impedido"


class TipoReceita(StrEnum):
    """Tipo de receita."""

    REVENDA_MERCADORIAS = "revenda"
    VENDA_PRODUCAO = "producao"
    SERVICOS = "servicos"
    LOCACAO_BENS = "locacao"


@dataclass
class FaixaAliquota:
    """Faixa de alíquota do Simples Nacional."""

    faixa: int
    receita_bruta_inicio: Decimal
    receita_bruta_fim: Decimal
    aliquota_nominal: Decimal
    valor_deduzir: Decimal

    def calcular_aliquota_efetiva(self, rbt12: Decimal) -> Decimal:
        """
        Calcula alíquota efetiva.

        Fórmula: (RBT12 x Aliq - PD) / RBT12

        Args:
            rbt12: Receita Bruta dos últimos 12 meses

        Returns:
            Alíquota efetiva
        """
        if rbt12 <= 0:
            return Decimal("0")

        aliquota_efetiva = (rbt12 * self.aliquota_nominal - self.valor_deduzir) / rbt12
        return aliquota_efetiva.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


@dataclass
class ReceitaCompetencia:
    """Receita de uma competência."""

    competencia: str  # YYYY-MM
    tipo_receita: TipoReceita
    anexo: AnexoSimples
    valor_bruto: Decimal
    deducoes: Decimal = Decimal("0")
    valor_liquido: Decimal = Decimal("0")

    def __post_init__(self):
        if self.valor_liquido == Decimal("0"):
            self.valor_liquido = self.valor_bruto - self.deducoes


@dataclass
class DAS:
    """Documento de Arrecadação do Simples Nacional."""

    numero_documento: str
    competencia: str
    data_vencimento: date
    valor_principal: Decimal
    valor_multa: Decimal = Decimal("0")
    valor_juros: Decimal = Decimal("0")
    valor_total: Decimal = Decimal("0")

    # Código de barras
    codigo_barras: str | None = None
    linha_digitavel: str | None = None

    # Composição do DAS
    irpj: Decimal = Decimal("0")
    csll: Decimal = Decimal("0")
    cofins: Decimal = Decimal("0")
    pis: Decimal = Decimal("0")
    cpp: Decimal = Decimal("0")
    icms: Decimal = Decimal("0")
    iss: Decimal = Decimal("0")

    # Situação
    situacao: str = "gerado"
    data_pagamento: datetime | None = None

    def __post_init__(self):
        if self.valor_total == Decimal("0"):
            self.valor_total = self.valor_principal + self.valor_multa + self.valor_juros


@dataclass
class PGDASD:
    """PGDAS-D - Declaração mensal do Simples Nacional."""

    competencia: str
    cnpj: str
    razao_social: str
    data_apuracao: datetime = field(default_factory=datetime.now)

    # Receitas
    receitas: list[ReceitaCompetencia] = field(default_factory=list)

    # Cálculos
    rbt12: Decimal = Decimal("0")  # Receita Bruta dos últimos 12 meses
    receita_mes: Decimal = Decimal("0")
    aliquota_efetiva: Decimal = Decimal("0")
    valor_devido: Decimal = Decimal("0")

    # DAS gerado
    das: DAS | None = None

    # Situação
    transmitida: bool = False
    numero_recibo: str | None = None
    data_transmissao: datetime | None = None


@dataclass
class DEFIS:
    """DEFIS - Declaração de Informações Socioeconômicas e Fiscais."""

    ano_calendario: int
    cnpj: str
    razao_social: str

    # Receitas anuais
    receita_bruta_total: Decimal = Decimal("0")
    receita_mercado_interno: Decimal = Decimal("0")
    receita_exportacao: Decimal = Decimal("0")

    # Folha de pagamento
    folha_salarios: Decimal = Decimal("0")
    quantidade_empregados_inicio: int = 0
    quantidade_empregados_fim: int = 0

    # Informações adicionais
    ganho_capital: Decimal = Decimal("0")
    rendimentos_exterior: Decimal = Decimal("0")
    doacao_campanha: Decimal = Decimal("0")

    # Sócios
    socios: list[dict[str, Any]] = field(default_factory=list)

    # Situação
    transmitida: bool = False
    numero_recibo: str | None = None
    data_transmissao: datetime | None = None


class SimplesNacionalManager:
    """
    Gerenciador do Simples Nacional.

    Calcula tributos e gera declarações do Simples Nacional.
    """

    # URLs
    URL_PORTAL = "https://www8.receita.fazenda.gov.br/SimplesNacional/"

    # Tabelas de alíquotas (LC 123/2006 atualizada)

    # Anexo III - Serviços (ex: vigilância, limpeza - Fator R >= 28%)
    ANEXO_III = [
        FaixaAliquota(1, Decimal("0"), Decimal("180000"), Decimal("0.06"), Decimal("0")),
        FaixaAliquota(2, Decimal("180000.01"), Decimal("360000"), Decimal("0.112"), Decimal("9360")),
        FaixaAliquota(3, Decimal("360000.01"), Decimal("720000"), Decimal("0.135"), Decimal("17640")),
        FaixaAliquota(4, Decimal("720000.01"), Decimal("1800000"), Decimal("0.16"), Decimal("35640")),
        FaixaAliquota(5, Decimal("1800000.01"), Decimal("3600000"), Decimal("0.21"), Decimal("125640")),
        FaixaAliquota(6, Decimal("3600000.01"), Decimal("4800000"), Decimal("0.33"), Decimal("648000")),
    ]

    # Anexo IV - Serviços (construção, vigilância sem cessão de mão de obra)
    ANEXO_IV = [
        FaixaAliquota(1, Decimal("0"), Decimal("180000"), Decimal("0.045"), Decimal("0")),
        FaixaAliquota(2, Decimal("180000.01"), Decimal("360000"), Decimal("0.09"), Decimal("8100")),
        FaixaAliquota(3, Decimal("360000.01"), Decimal("720000"), Decimal("0.102"), Decimal("12420")),
        FaixaAliquota(4, Decimal("720000.01"), Decimal("1800000"), Decimal("0.14"), Decimal("39780")),
        FaixaAliquota(5, Decimal("1800000.01"), Decimal("3600000"), Decimal("0.22"), Decimal("183780")),
        FaixaAliquota(6, Decimal("3600000.01"), Decimal("4800000"), Decimal("0.33"), Decimal("828000")),
    ]

    # Anexo V - Serviços (TI, engenharia - Fator R < 28%)
    ANEXO_V = [
        FaixaAliquota(1, Decimal("0"), Decimal("180000"), Decimal("0.155"), Decimal("0")),
        FaixaAliquota(2, Decimal("180000.01"), Decimal("360000"), Decimal("0.18"), Decimal("4500")),
        FaixaAliquota(3, Decimal("360000.01"), Decimal("720000"), Decimal("0.195"), Decimal("9900")),
        FaixaAliquota(4, Decimal("720000.01"), Decimal("1800000"), Decimal("0.205"), Decimal("17100")),
        FaixaAliquota(5, Decimal("1800000.01"), Decimal("3600000"), Decimal("0.23"), Decimal("62100")),
        FaixaAliquota(6, Decimal("3600000.01"), Decimal("4800000"), Decimal("0.305"), Decimal("540000")),
    ]

    # Partilha do Simples (percentual de cada tributo por anexo)
    PARTILHA = {
        AnexoSimples.ANEXO_III: {
            "irpj": Decimal("0.04"),
            "csll": Decimal("0.035"),
            "cofins": Decimal("0.1282"),
            "pis": Decimal("0.0278"),
            "cpp": Decimal("0.434"),
            "iss": Decimal("0.335"),
        },
        AnexoSimples.ANEXO_IV: {
            "irpj": Decimal("0.04"),
            "csll": Decimal("0.035"),
            "cofins": Decimal("0.1282"),
            "pis": Decimal("0.0278"),
            "cpp": Decimal("0"),  # CPP paga separadamente no Anexo IV
            "iss": Decimal("0.769"),
        },
        AnexoSimples.ANEXO_V: {
            "irpj": Decimal("0.04"),
            "csll": Decimal("0.035"),
            "cofins": Decimal("0.1282"),
            "pis": Decimal("0.0278"),
            "cpp": Decimal("0.434"),
            "iss": Decimal("0.335"),
        },
    }

    def __init__(
        self,
        cnpj: str,
        razao_social: str,
        anexo_principal: AnexoSimples = AnexoSimples.ANEXO_III,
    ):
        """
        Inicializa o gerenciador.

        Args:
            cnpj: CNPJ da empresa
            razao_social: Razão social
            anexo_principal: Anexo principal do Simples
        """
        self.cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
        self.razao_social = razao_social
        self.anexo_principal = anexo_principal

    def consultar_opcao(self) -> dict[str, Any]:
        """
        Consulta situação da opção pelo Simples Nacional.

        Returns:
            Dados da situação
        """
        # Na implementação real, consultaria o portal
        return {
            "cnpj": self.cnpj,
            "razao_social": self.razao_social,
            "situacao": SituacaoOpcao.OPTANTE.value,
            "data_opcao": "2020-01-01",
            "enquadramento": self.anexo_principal.value,
            "simei": False,  # Não é MEI
        }

    def obter_faixa(self, rbt12: Decimal, anexo: AnexoSimples) -> FaixaAliquota:
        """
        Obtém a faixa de alíquota para a RBT12.

        Args:
            rbt12: Receita Bruta dos últimos 12 meses
            anexo: Anexo do Simples

        Returns:
            Faixa de alíquota
        """
        tabela = {
            AnexoSimples.ANEXO_III: self.ANEXO_III,
            AnexoSimples.ANEXO_IV: self.ANEXO_IV,
            AnexoSimples.ANEXO_V: self.ANEXO_V,
        }.get(anexo, self.ANEXO_III)

        for faixa in tabela:
            if faixa.receita_bruta_inicio <= rbt12 <= faixa.receita_bruta_fim:
                return faixa

        # Se excedeu o limite, retorna última faixa
        return tabela[-1]

    def calcular_fator_r(self, folha_12_meses: Decimal, rbt12: Decimal) -> tuple[Decimal, AnexoSimples]:
        """
        Calcula o Fator R para determinar o anexo.

        Fator R = Folha de Salários 12 meses / RBT12

        Se Fator R >= 28%, usa Anexo III
        Se Fator R < 28%, usa Anexo V

        Args:
            folha_12_meses: Folha de salários dos últimos 12 meses
            rbt12: Receita Bruta dos últimos 12 meses

        Returns:
            Tuple com (Fator R, Anexo aplicável)
        """
        if rbt12 <= 0:
            return Decimal("0"), AnexoSimples.ANEXO_V

        fator_r = folha_12_meses / rbt12

        # Atividades do Anexo III com cessão de mão de obra
        # Vigilância com cessão: Anexo IV (CPP separado)
        # Vigilância sem cessão: Fator R determina III ou V

        if fator_r >= Decimal("0.28"):
            anexo = AnexoSimples.ANEXO_III
        else:
            anexo = AnexoSimples.ANEXO_V

        logger.info(f"Fator R: {fator_r:.4f} -> Anexo {anexo.value}")
        return fator_r.quantize(Decimal("0.0001")), anexo

    def calcular_pgdasd(
        self,
        competencia: str,
        receitas: list[ReceitaCompetencia],
        rbt12: Decimal,
        folha_12_meses: Decimal | None = None,
    ) -> PGDASD:
        """
        Calcula o PGDAS-D (declaração mensal).

        Args:
            competencia: Competência YYYY-MM
            receitas: Receitas do mês
            rbt12: Receita Bruta dos últimos 12 meses
            folha_12_meses: Folha de salários 12 meses (para Fator R)

        Returns:
            PGDAS-D calculado
        """
        pgdasd = PGDASD(
            competencia=competencia,
            cnpj=self.cnpj,
            razao_social=self.razao_social,
            rbt12=rbt12,
            receitas=receitas,
        )

        # Calcula receita do mês
        pgdasd.receita_mes = sum(r.valor_liquido for r in receitas)

        if pgdasd.receita_mes <= 0:
            logger.info(f"PGDAS-D {competencia}: Sem receita")
            return pgdasd

        # Determina anexo pelo Fator R se aplicável
        anexo = self.anexo_principal
        if folha_12_meses and self.anexo_principal in [AnexoSimples.ANEXO_III, AnexoSimples.ANEXO_V]:
            _, anexo = self.calcular_fator_r(folha_12_meses, rbt12)

        # Obtém faixa de alíquota
        faixa = self.obter_faixa(rbt12, anexo)

        # Calcula alíquota efetiva
        pgdasd.aliquota_efetiva = faixa.calcular_aliquota_efetiva(rbt12)

        # Calcula valor devido
        pgdasd.valor_devido = (pgdasd.receita_mes * pgdasd.aliquota_efetiva).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        logger.info(
            f"PGDAS-D {competencia}: RBT12={rbt12}, Receita={pgdasd.receita_mes}, "
            f"Alíq={pgdasd.aliquota_efetiva:.4f}, Devido={pgdasd.valor_devido}"
        )

        return pgdasd

    def gerar_das(self, pgdasd: PGDASD, data_vencimento: date | None = None) -> DAS:
        """
        Gera o DAS (guia de pagamento) a partir do PGDAS-D.

        Args:
            pgdasd: PGDAS-D calculado
            data_vencimento: Data de vencimento (default: dia 20 do mês seguinte)

        Returns:
            DAS gerado
        """
        if data_vencimento is None:
            ano, mes = map(int, pgdasd.competencia.split("-"))
            if mes == 12:
                ano += 1
                mes = 1
            else:
                mes += 1
            data_vencimento = date(ano, mes, 20)

        # Calcula partilha dos tributos
        partilha = self.PARTILHA.get(self.anexo_principal, self.PARTILHA[AnexoSimples.ANEXO_III])

        das = DAS(
            numero_documento=f"DAS{pgdasd.competencia.replace('-', '')}{datetime.now().strftime('%H%M%S')}",
            competencia=pgdasd.competencia,
            data_vencimento=data_vencimento,
            valor_principal=pgdasd.valor_devido,
            irpj=(pgdasd.valor_devido * partilha["irpj"]).quantize(Decimal("0.01")),
            csll=(pgdasd.valor_devido * partilha["csll"]).quantize(Decimal("0.01")),
            cofins=(pgdasd.valor_devido * partilha["cofins"]).quantize(Decimal("0.01")),
            pis=(pgdasd.valor_devido * partilha["pis"]).quantize(Decimal("0.01")),
            cpp=(pgdasd.valor_devido * partilha["cpp"]).quantize(Decimal("0.01")),
            iss=(pgdasd.valor_devido * partilha["iss"]).quantize(Decimal("0.01")),
        )

        # Gerar código de barras (simulado)
        das.codigo_barras = self._gerar_codigo_barras(das)
        das.linha_digitavel = self._gerar_linha_digitavel(das)

        pgdasd.das = das

        logger.info(f"Gerado DAS {das.numero_documento}: R$ {das.valor_total}")

        return das

    def calcular_defis(
        self, ano_calendario: int, pgdasd_mensal: list[PGDASD], dados_adicionais: dict[str, Any] | None = None
    ) -> DEFIS:
        """
        Calcula a DEFIS (declaração anual).

        Args:
            ano_calendario: Ano-calendário
            pgdasd_mensal: Lista de PGDAS-D do ano
            dados_adicionais: Dados adicionais (sócios, empregados, etc.)

        Returns:
            DEFIS calculada
        """
        dados = dados_adicionais or {}

        defis = DEFIS(
            ano_calendario=ano_calendario,
            cnpj=self.cnpj,
            razao_social=self.razao_social,
            receita_bruta_total=sum(p.receita_mes for p in pgdasd_mensal),
            receita_mercado_interno=sum(p.receita_mes for p in pgdasd_mensal),
            folha_salarios=Decimal(str(dados.get("folha_salarios_anual", 0))),
            quantidade_empregados_inicio=dados.get("empregados_janeiro", 0),
            quantidade_empregados_fim=dados.get("empregados_dezembro", 0),
            socios=dados.get("socios", []),
        )

        logger.info(f"DEFIS {ano_calendario}: Receita Total = R$ {defis.receita_bruta_total}")

        return defis

    def consultar_pendencias(self) -> dict[str, Any]:
        """
        Consulta pendências no Simples Nacional.

        Returns:
            Lista de pendências
        """
        return {"cnpj": self.cnpj, "pendencias": [], "mensagem": "Implementar consulta via portal Simples Nacional"}

    def consultar_das_emitidos(self, competencia_inicio: str, competencia_fim: str) -> list[dict[str, Any]]:
        """
        Consulta DAS emitidos em um período.

        Args:
            competencia_inicio: Competência inicial YYYY-MM
            competencia_fim: Competência final YYYY-MM

        Returns:
            Lista de DAS
        """
        return []

    def _gerar_codigo_barras(self, das: DAS) -> str:
        """Gera código de barras do DAS (simulado)."""
        # Código de barras do DAS tem 44 posições
        return f"8584000000{int(das.valor_total * 100):011d}0001{das.competencia.replace('-', '')}0000"

    def _gerar_linha_digitavel(self, das: DAS) -> str:
        """Gera linha digitável do DAS (simulada)."""
        return f"85840000000 {int(das.valor_total * 100):011d} 00010 {das.competencia.replace('-', '')}0 00000"

    def simular_calculo(
        self, receita_mensal: Decimal, rbt12: Decimal, folha_12_meses: Decimal | None = None
    ) -> dict[str, Any]:
        """
        Simula cálculo do Simples Nacional.

        Args:
            receita_mensal: Receita do mês
            rbt12: Receita Bruta 12 meses
            folha_12_meses: Folha de salários 12 meses

        Returns:
            Simulação detalhada
        """
        # Determina anexo
        fator_r = None
        anexo = self.anexo_principal

        if folha_12_meses and self.anexo_principal in [AnexoSimples.ANEXO_III, AnexoSimples.ANEXO_V]:
            fator_r, anexo = self.calcular_fator_r(folha_12_meses, rbt12)

        # Obtém faixa
        faixa = self.obter_faixa(rbt12, anexo)

        # Calcula alíquota efetiva
        aliquota_efetiva = faixa.calcular_aliquota_efetiva(rbt12)

        # Calcula valor devido
        valor_devido = (receita_mensal * aliquota_efetiva).quantize(Decimal("0.01"))

        # Partilha
        partilha = self.PARTILHA.get(anexo, self.PARTILHA[AnexoSimples.ANEXO_III])

        return {
            "receita_mensal": str(receita_mensal),
            "rbt12": str(rbt12),
            "fator_r": str(fator_r) if fator_r else None,
            "anexo": anexo.value,
            "faixa": faixa.faixa,
            "aliquota_nominal": str(faixa.aliquota_nominal),
            "valor_deduzir": str(faixa.valor_deduzir),
            "aliquota_efetiva": str(aliquota_efetiva),
            "valor_devido": str(valor_devido),
            "composicao": {
                "irpj": str((valor_devido * partilha["irpj"]).quantize(Decimal("0.01"))),
                "csll": str((valor_devido * partilha["csll"]).quantize(Decimal("0.01"))),
                "cofins": str((valor_devido * partilha["cofins"]).quantize(Decimal("0.01"))),
                "pis": str((valor_devido * partilha["pis"]).quantize(Decimal("0.01"))),
                "cpp": str((valor_devido * partilha["cpp"]).quantize(Decimal("0.01"))),
                "iss": str((valor_devido * partilha["iss"]).quantize(Decimal("0.01"))),
            },
        }
