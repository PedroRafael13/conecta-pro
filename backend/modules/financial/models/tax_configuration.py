"""Modelo de Configuracao de Impostos - Regimes tributarios e configuracoes fiscais."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID

from core.models.base import Base


class TaxRegime(str, Enum):
    """Regime tributario da empresa."""

    SIMPLES_NACIONAL = "simples_nacional"
    SIMPLES_MEI = "simples_mei"
    LUCRO_PRESUMIDO = "lucro_presumido"
    LUCRO_REAL = "lucro_real"
    LUCRO_ARBITRADO = "lucro_arbitrado"
    IMUNE = "imune"
    ISENTO = "isento"


class TaxType(str, Enum):
    """Tipo de imposto."""

    # Federais
    IRPJ = "irpj"  # Imposto de Renda Pessoa Juridica
    CSLL = "csll"  # Contribuicao Social sobre Lucro Liquido
    PIS = "pis"  # Programa de Integracao Social
    COFINS = "cofins"  # Contribuicao para Financiamento da Seguridade Social
    IPI = "ipi"  # Imposto sobre Produtos Industrializados
    IOF = "iof"  # Imposto sobre Operacoes Financeiras
    II = "ii"  # Imposto de Importacao
    IE = "ie"  # Imposto de Exportacao
    IRRF = "irrf"  # Imposto de Renda Retido na Fonte
    INSS = "inss"  # Contribuicao Previdenciaria
    CPRB = "cprb"  # Contribuicao Previdenciaria sobre Receita Bruta

    # Estaduais
    ICMS = "icms"  # Imposto sobre Circulacao de Mercadorias e Servicos
    ICMS_ST = "icms_st"  # ICMS Substituicao Tributaria
    ICMS_DIFAL = "icms_difal"  # Diferencial de Aliquota
    FECP = "fecp"  # Fundo de Combate a Pobreza

    # Municipais
    ISS = "iss"  # Imposto sobre Servicos
    ISS_RETIDO = "iss_retido"  # ISS Retido na Fonte

    # Simples Nacional
    SIMPLES = "simples"  # DAS Simples Nacional

    # Outros
    FUNRURAL = "funrural"  # Fundo de Assistencia ao Trabalhador Rural
    SENAR = "senar"  # Servico Nacional de Aprendizagem Rural


class TaxCalculationType(str, Enum):
    """Tipo de calculo do imposto."""

    PERCENTUAL = "percentual"
    VALOR_FIXO = "valor_fixo"
    TABELA_PROGRESSIVA = "tabela_progressiva"
    SUBSTITUICAO_TRIBUTARIA = "substituicao_tributaria"
    DIFERIMENTO = "diferimento"
    ISENTO = "isento"
    NAO_TRIBUTADO = "nao_tributado"
    SUSPENSAO = "suspensao"


class TaxConfigurationStatus(str, Enum):
    """Status da configuracao de imposto."""

    ATIVA = "ativa"
    INATIVA = "inativa"
    PENDENTE = "pendente"
    EXPIRADA = "expirada"


class PISCOFINSRegime(str, Enum):
    """Regime de apuracao de PIS/COFINS."""

    CUMULATIVO = "cumulativo"  # Lucro Presumido
    NAO_CUMULATIVO = "nao_cumulativo"  # Lucro Real
    MISTO = "misto"


class ICMSOrigin(str, Enum):
    """Origem da mercadoria para ICMS."""

    NACIONAL = "0"  # Nacional
    ESTRANGEIRA_IMPORTACAO_DIRETA = "1"  # Estrangeira - Importacao direta
    ESTRANGEIRA_ADQUIRIDA_MERCADO_INTERNO = "2"  # Estrangeira - Adquirida no mercado interno
    NACIONAL_CONTEUDO_IMPORTADO_40_70 = "3"  # Nacional com conteudo importado 40-70%
    NACIONAL_PROCESSOS_BASICOS = "4"  # Nacional com processos produtivos basicos
    NACIONAL_CONTEUDO_IMPORTADO_ATE_40 = "5"  # Nacional com conteudo importado ate 40%
    ESTRANGEIRA_IMPORTACAO_DIRETA_SIMILAR = "6"  # Estrangeira sem similar nacional
    ESTRANGEIRA_MERCADO_INTERNO_SIMILAR = "7"  # Estrangeira adquirida sem similar nacional
    NACIONAL_CONTEUDO_IMPORTADO_ACIMA_70 = "8"  # Nacional com conteudo importado acima de 70%


class ICMSModalidadeBC(str, Enum):
    """Modalidade de base de calculo do ICMS."""

    MARGEM_VALOR_AGREGADO = "0"  # Margem Valor Agregado (%)
    PAUTA = "1"  # Pauta (Valor)
    PRECO_TABELADO_MAX = "2"  # Preco Tabelado Max (valor)
    VALOR_OPERACAO = "3"  # Valor da operacao


class ICMSModalidadeBCST(str, Enum):
    """Modalidade de base de calculo do ICMS ST."""

    PRECO_TABELADO = "0"
    LISTA_NEGATIVA = "1"
    LISTA_POSITIVA = "2"
    LISTA_NEUTRA = "3"
    MARGEM_VALOR_AGREGADO = "4"
    PAUTA = "5"
    VALOR_OPERACAO = "6"


class ICMSCST(str, Enum):
    """Codigo de Situacao Tributaria do ICMS."""

    TRIBUTADA_INTEGRALMENTE = "00"
    TRIBUTADA_COM_CREDITO = "20"
    ISENTA_OU_NAO_TRIBUTADA = "40"
    SUSPENSAO = "50"
    DIFERIMENTO = "51"
    ICMS_COBRADO_ANTERIORMENTE = "60"
    REDUCAO_BASE_CALCULO = "70"
    OUTRAS = "90"


class ICMSCSOSN(str, Enum):
    """Codigo de Situacao da Operacao no Simples Nacional."""

    TRIBUTADA_PELO_SIMPLES = "101"
    TRIBUTADA_COM_CREDITO = "102"
    ISENTA = "103"
    NAO_TRIBUTADA = "300"
    IMUNE = "400"
    ICMS_COBRADO_ANTERIORMENTE = "500"
    OUTRAS = "900"


class TaxConfiguration(Base):
    """Configuracao de impostos por empresa/condominio."""

    __tablename__ = "tax_configurations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    tax_type = Column(String(30), nullable=False, index=True)
    tax_regime = Column(String(30), nullable=False, index=True)

    # Configuracao
    calculation_type = Column(
        String(30), nullable=False, default=TaxCalculationType.PERCENTUAL.value
    )
    rate = Column(Numeric(8, 4), nullable=True)  # Aliquota em %
    fixed_value = Column(Numeric(15, 2), nullable=True)  # Valor fixo
    base_reduction = Column(Numeric(8, 4), nullable=True)  # Reducao de base (%)
    credit_rate = Column(Numeric(8, 4), nullable=True)  # Aliquota de credito (%)

    # ICMS Especifico
    icms_origin = Column(String(1), nullable=True)
    icms_cst = Column(String(3), nullable=True)
    icms_csosn = Column(String(3), nullable=True)  # Simples Nacional
    icms_modbc = Column(String(1), nullable=True)
    icms_mva = Column(Numeric(8, 4), nullable=True)  # Margem Valor Agregado

    # PIS/COFINS
    pis_cofins_regime = Column(String(20), nullable=True)
    pis_cst = Column(String(2), nullable=True)
    cofins_cst = Column(String(2), nullable=True)

    # IPI
    ipi_cst = Column(String(2), nullable=True)
    ipi_classe_enquadramento = Column(String(5), nullable=True)

    # ISS
    iss_codigo_servico = Column(String(20), nullable=True)
    iss_local_prestacao = Column(String(20), nullable=True)  # prestador, tomador

    # Retencoes
    has_retention = Column(Boolean, default=False)
    retention_rate = Column(Numeric(8, 4), nullable=True)
    retention_minimum = Column(Numeric(15, 2), nullable=True)  # Valor minimo para retencao

    # Vigencia
    valid_from = Column(Date, nullable=False, default=date.today)
    valid_until = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default=TaxConfigurationStatus.ATIVA.value)

    # Regras especiais (JSON)
    special_rules = Column(JSONB, nullable=True)  # Regras especificas por CFOP, NCM, etc.

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<TaxConfiguration {self.name} ({self.tax_type})>"

    @property
    def is_active(self) -> bool:
        """Verifica se configuracao esta ativa."""
        if self.status != TaxConfigurationStatus.ATIVA.value:
            return False
        if self.valid_until and self.valid_until < date.today():
            return False
        return self.active

    @property
    def is_expired(self) -> bool:
        """Verifica se configuracao expirou."""
        if self.valid_until:
            return self.valid_until < date.today()
        return False

    def calculate_tax(
        self,
        base_value: Decimal,
        quantity: Decimal = Decimal("1"),
    ) -> dict[str, Decimal]:
        """Calcula imposto baseado na configuracao."""
        result = {
            "base": base_value,
            "rate": self.rate or Decimal("0"),
            "value": Decimal("0"),
            "credit": Decimal("0"),
        }

        # Aplica reducao de base se houver
        if self.base_reduction:
            base_value = base_value * (Decimal("1") - self.base_reduction / 100)
            result["base_reduced"] = base_value

        if self.calculation_type == TaxCalculationType.PERCENTUAL.value:
            if self.rate:
                result["value"] = base_value * self.rate / 100
        elif self.calculation_type == TaxCalculationType.VALOR_FIXO.value:
            if self.fixed_value:
                result["value"] = self.fixed_value * quantity
        elif self.calculation_type == TaxCalculationType.ISENTO.value:
            result["value"] = Decimal("0")
            result["isento"] = True
        elif self.calculation_type == TaxCalculationType.NAO_TRIBUTADO.value:
            result["value"] = Decimal("0")
            result["nao_tributado"] = True

        # Calcula credito se aplicavel
        if self.credit_rate and result["value"] > 0:
            result["credit"] = base_value * self.credit_rate / 100

        return result


class TaxTable(Base):
    """Tabela progressiva de impostos (IRPJ, INSS, etc.)."""

    __tablename__ = "tax_tables"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    name = Column(String(100), nullable=False)
    tax_type = Column(String(30), nullable=False, index=True)
    year = Column(String(4), nullable=False)  # Ano de vigencia

    # Vigencia
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)

    # Faixas (JSONB array)
    # Formato: [{"min": 0, "max": 1412.00, "rate": 7.5, "deduction": 0}, ...]
    brackets = Column(JSONB, nullable=False, default=list)

    # Constantes
    dependent_deduction = Column(Numeric(15, 2), nullable=True)  # Deducao por dependente
    ceiling = Column(Numeric(15, 2), nullable=True)  # Teto de contribuicao
    floor = Column(Numeric(15, 2), nullable=True)  # Piso

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<TaxTable {self.name} ({self.year})>"

    def calculate(
        self,
        base_value: Decimal,
        dependents: int = 0,
    ) -> dict[str, Decimal]:
        """Calcula imposto usando tabela progressiva."""
        result = {
            "base": base_value,
            "taxable_base": base_value,
            "rate": Decimal("0"),
            "value": Decimal("0"),
            "deduction": Decimal("0"),
        }

        # Deduz dependentes
        if dependents > 0 and self.dependent_deduction:
            deduction = self.dependent_deduction * dependents
            result["dependent_deduction"] = deduction
            result["taxable_base"] = base_value - deduction

        taxable = result["taxable_base"]

        # Aplica teto se houver
        if self.ceiling and taxable > self.ceiling:
            taxable = self.ceiling
            result["taxable_base"] = taxable

        # Encontra faixa aplicavel
        for bracket in self.brackets:
            min_val = Decimal(str(bracket.get("min", 0)))
            max_val = Decimal(str(bracket.get("max", 999999999)))
            rate = Decimal(str(bracket.get("rate", 0)))
            deduction = Decimal(str(bracket.get("deduction", 0)))

            if min_val <= taxable <= max_val:
                result["rate"] = rate
                result["deduction"] = deduction
                result["value"] = (taxable * rate / 100) - deduction
                if result["value"] < 0:
                    result["value"] = Decimal("0")
                break

        return result


class SimplesNacionalConfig(Base):
    """Configuracao especifica do Simples Nacional."""

    __tablename__ = "simples_nacional_configs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Anexo do Simples
    anexo = Column(String(10), nullable=False)  # I, II, III, IV, V, VI
    faixa = Column(String(10), nullable=True)  # 1a, 2a, 3a, 4a, 5a, 6a

    # Faturamento
    faturamento_12_meses = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    limite_sublimite = Column(Numeric(15, 2), nullable=True)  # Sublimite estadual

    # Aliquotas
    aliquota_nominal = Column(Numeric(8, 4), nullable=False)
    aliquota_efetiva = Column(Numeric(8, 4), nullable=True)
    parcela_deduzir = Column(Numeric(15, 2), nullable=True)

    # Reparticao (JSONB)
    # {"irpj": 5.5, "csll": 3.5, "pis": 1.65, "cofins": 7.6, "cpp": 28.27, "icms": 34.0, "iss": 0}
    reparticao = Column(JSONB, nullable=True)

    # Fator R (para Anexo V)
    folha_pagamento_12_meses = Column(Numeric(15, 2), nullable=True)
    fator_r = Column(Numeric(8, 4), nullable=True)

    # Vigencia
    competencia = Column(String(7), nullable=False)  # YYYY-MM
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<SimplesNacionalConfig Anexo {self.anexo} ({self.competencia})>"

    def calculate_das(self, receita_bruta: Decimal) -> dict[str, Any]:
        """Calcula DAS do Simples Nacional."""
        # Formula: (RBT12 x Aliquota - Parcela a Deduzir) / RBT12
        if self.faturamento_12_meses <= 0:
            return {"value": Decimal("0"), "effective_rate": Decimal("0")}

        aliquota_efetiva = (
            (self.faturamento_12_meses * self.aliquota_nominal / 100)
            - (self.parcela_deduzir or Decimal("0"))
        ) / self.faturamento_12_meses * 100

        das = receita_bruta * aliquota_efetiva / 100

        result = {
            "receita_bruta": receita_bruta,
            "rbt12": self.faturamento_12_meses,
            "anexo": self.anexo,
            "faixa": self.faixa,
            "aliquota_nominal": self.aliquota_nominal,
            "aliquota_efetiva": aliquota_efetiva,
            "value": das,
        }

        # Reparticao por tributo
        if self.reparticao:
            result["reparticao"] = {}
            for tributo, percentual in self.reparticao.items():
                result["reparticao"][tributo] = das * Decimal(str(percentual)) / 100

        return result

    @property
    def is_anexo_v(self) -> bool:
        """Verifica se e Anexo V (depende do Fator R)."""
        return self.anexo == "V"

    def calculate_fator_r(self) -> Optional[Decimal]:
        """Calcula Fator R."""
        if not self.folha_pagamento_12_meses or not self.faturamento_12_meses:
            return None
        if self.faturamento_12_meses <= 0:
            return None
        return self.folha_pagamento_12_meses / self.faturamento_12_meses
