"""Modelo de CFOP e NCM - Codigos fiscais e classificacao de mercadorias."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from core.models.base import Base

if TYPE_CHECKING:
    pass


class CFOPTipo(str, Enum):
    """Tipo de operacao do CFOP."""

    ENTRADA = "entrada"
    SAIDA = "saida"


class CFOPGrupo(str, Enum):
    """Grupo do CFOP (primeiro digito)."""

    # Entradas
    ENTRADA_ESTADO = "1"  # Entradas do estado
    ENTRADA_OUTRO_ESTADO = "2"  # Entradas de outro estado
    ENTRADA_EXTERIOR = "3"  # Entradas do exterior

    # Saidas
    SAIDA_ESTADO = "5"  # Saidas para o estado
    SAIDA_OUTRO_ESTADO = "6"  # Saidas para outro estado
    SAIDA_EXTERIOR = "7"  # Saidas para o exterior


class CFOPNatureza(str, Enum):
    """Natureza da operacao do CFOP."""

    COMPRA = "compra"
    VENDA = "venda"
    TRANSFERENCIA = "transferencia"
    DEVOLUCAO = "devolucao"
    REMESSA = "remessa"
    RETORNO = "retorno"
    BONIFICACAO = "bonificacao"
    DEMONSTRACAO = "demonstracao"
    CONSIGNACAO = "consignacao"
    SIMPLES_REMESSA = "simples_remessa"
    OUTRAS = "outras"


class CFOP(Base):
    """Codigo Fiscal de Operacoes e Prestacoes."""

    __tablename__ = "cfops"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identificacao
    codigo = Column(String(4), nullable=False, unique=True, index=True)
    descricao = Column(Text, nullable=False)
    descricao_resumida = Column(String(100), nullable=True)

    # Classificacao
    tipo = Column(String(10), nullable=False)  # entrada, saida
    grupo = Column(String(1), nullable=False)  # 1,2,3 ou 5,6,7
    natureza = Column(String(30), nullable=True)

    # Tributacao
    gera_credito_icms = Column(Boolean, default=False)
    gera_debito_icms = Column(Boolean, default=False)
    gera_credito_ipi = Column(Boolean, default=False)
    gera_debito_ipi = Column(Boolean, default=False)
    gera_pis_cofins = Column(Boolean, default=True)

    # Movimentacao
    movimenta_estoque = Column(Boolean, default=True)
    movimenta_financeiro = Column(Boolean, default=True)
    movimenta_contabilidade = Column(Boolean, default=True)

    # Zona Franca
    zfm_aplicavel = Column(Boolean, default=False)  # CFOP especifico para ZFM
    zfm_isenta_icms = Column(Boolean, default=False)
    zfm_isenta_ipi = Column(Boolean, default=False)
    zfm_suspende_pis_cofins = Column(Boolean, default=False)

    # CFOP correspondente (entrada <-> saida)
    cfop_correspondente = Column(String(4), nullable=True)

    # Conta contabil sugerida
    conta_contabil_debito = Column(String(20), nullable=True)
    conta_contabil_credito = Column(String(20), nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<CFOP {self.codigo}: {self.descricao_resumida or self.descricao[:50]}>"

    @property
    def is_entrada(self) -> bool:
        """Verifica se e operacao de entrada."""
        return self.grupo in ["1", "2", "3"]

    @property
    def is_saida(self) -> bool:
        """Verifica se e operacao de saida."""
        return self.grupo in ["5", "6", "7"]

    @property
    def is_interestadual(self) -> bool:
        """Verifica se e operacao interestadual."""
        return self.grupo in ["2", "6"]

    @property
    def is_exterior(self) -> bool:
        """Verifica se e operacao com exterior."""
        return self.grupo in ["3", "7"]


class NCM(Base):
    """Nomenclatura Comum do Mercosul."""

    __tablename__ = "ncms"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identificacao
    codigo = Column(String(8), nullable=False, unique=True, index=True)
    descricao = Column(Text, nullable=False)
    descricao_resumida = Column(String(200), nullable=True)

    # Classificacao
    capitulo = Column(String(2), nullable=True)  # Primeiros 2 digitos
    posicao = Column(String(4), nullable=True)  # Primeiros 4 digitos
    subposicao = Column(String(6), nullable=True)  # Primeiros 6 digitos

    # IPI
    ipi_aliquota = Column(Numeric(8, 4), nullable=True)
    ipi_codigo_enquadramento = Column(String(5), nullable=True)
    ipi_unidade_tributavel = Column(String(6), nullable=True)

    # PIS/COFINS
    pis_aliquota = Column(Numeric(8, 4), nullable=True, default=Decimal("1.65"))
    cofins_aliquota = Column(Numeric(8, 4), nullable=True, default=Decimal("7.6"))
    pis_cofins_cst_entrada = Column(String(2), nullable=True, default="50")
    pis_cofins_cst_saida = Column(String(2), nullable=True, default="01")

    # ICMS
    icms_cest = Column(String(7), nullable=True)  # Codigo CEST para ST
    icms_st_mva = Column(Numeric(8, 4), nullable=True)  # MVA padrao

    # II (Imposto de Importacao)
    ii_aliquota = Column(Numeric(8, 4), nullable=True)

    # Tributacao Monofasica
    tributacao_monofasica = Column(Boolean, default=False)
    aliquota_monofasica = Column(Numeric(8, 4), nullable=True)

    # Zona Franca
    zfm_isento_ipi = Column(Boolean, default=False)
    zfm_reduz_ii = Column(Boolean, default=False)
    zfm_percentual_reducao_ii = Column(Numeric(8, 4), nullable=True)

    # TIPI (Tabela de Incidencia do IPI)
    tipi_unidade = Column(String(10), nullable=True)
    tipi_nota = Column(String(500), nullable=True)

    # Vigencia
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<NCM {self.codigo}: {self.descricao_resumida or self.descricao[:50]}>"

    @property
    def is_vigente(self) -> bool:
        """Verifica se NCM esta vigente."""
        hoje = date.today()
        if self.valid_from and hoje < self.valid_from:
            return False
        if self.valid_until and hoje > self.valid_until:
            return False
        return self.active


class RetencaoFederal(Base):
    """Configuracao de retencoes federais por servico/cliente."""

    __tablename__ = "retencoes_federais"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    nome = Column(String(100), nullable=False)
    codigo_servico = Column(String(20), nullable=True)  # LC 116
    descricao = Column(Text, nullable=True)

    # Tipo de servico
    servico_vigilancia = Column(Boolean, default=False)
    servico_limpeza = Column(Boolean, default=False)
    servico_locacao_mao_obra = Column(Boolean, default=False)
    servico_construcao_civil = Column(Boolean, default=False)

    # INSS (Contribuicao Previdenciaria - 11%)
    inss_retido = Column(Boolean, default=True)
    inss_aliquota = Column(Numeric(8, 4), nullable=False, default=Decimal("11.00"))
    inss_base_minima = Column(Numeric(15, 2), nullable=True)  # Valor minimo para reter

    # Liminar INSS (caso especifico Conecta Mais)
    inss_liminar_ativa = Column(Boolean, default=False)
    inss_liminar_numero = Column(String(50), nullable=True)
    inss_liminar_vara = Column(String(100), nullable=True)
    inss_liminar_data = Column(Date, nullable=True)
    inss_liminar_validade = Column(Date, nullable=True)
    inss_liminar_texto = Column(Text, nullable=True)  # Texto para incluir na nota

    # IR (Imposto de Renda Retido na Fonte)
    ir_retido = Column(Boolean, default=True)
    ir_aliquota = Column(Numeric(8, 4), nullable=False, default=Decimal("1.50"))
    ir_base_minima = Column(Numeric(15, 2), nullable=True, default=Decimal("666.66"))

    # CSLL
    csll_retido = Column(Boolean, default=True)
    csll_aliquota = Column(Numeric(8, 4), nullable=False, default=Decimal("1.00"))

    # PIS
    pis_retido = Column(Boolean, default=True)
    pis_aliquota = Column(Numeric(8, 4), nullable=False, default=Decimal("0.65"))

    # COFINS
    cofins_retido = Column(Boolean, default=True)
    cofins_aliquota = Column(Numeric(8, 4), nullable=False, default=Decimal("3.00"))

    # Total PCC (PIS + COFINS + CSLL)
    # Aliquota total: 4.65%
    # Base minima: R$ 215,05 (5.000 * 4,3%)

    # ISS (quando aplicavel)
    iss_retido = Column(Boolean, default=False)
    iss_aliquota = Column(Numeric(8, 4), nullable=True)

    # Valores calculados
    pcc_base_minima = Column(Numeric(15, 2), nullable=True, default=Decimal("215.05"))

    # Cliente especifico (opcional)
    cliente_id = Column(PGUUID(as_uuid=True), nullable=True)
    cliente_aceita_liminar = Column(Boolean, nullable=True)  # Se cliente aceita liminar INSS

    # Vigencia
    valid_from = Column(Date, nullable=False, default=date.today)
    valid_until = Column(Date, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<RetencaoFederal {self.nome}>"

    @property
    def aliquota_pcc(self) -> Decimal:
        """Retorna aliquota total de PCC (PIS + COFINS + CSLL)."""
        total = Decimal("0")
        if self.pis_retido:
            total += self.pis_aliquota or Decimal("0")
        if self.cofins_retido:
            total += self.cofins_aliquota or Decimal("0")
        if self.csll_retido:
            total += self.csll_aliquota or Decimal("0")
        return total

    def calcular_retencoes(
        self,
        valor_servico: Decimal,
        cliente_aceita_liminar: bool = False,
    ) -> dict:
        """Calcula retencoes para um valor de servico.

        Args:
            valor_servico: Valor bruto do servico
            cliente_aceita_liminar: Se o cliente aceita a liminar de INSS

        Returns:
            Dict com valores de retencao
        """
        retencoes = {
            "valor_servico": valor_servico,
            "inss": Decimal("0"),
            "ir": Decimal("0"),
            "csll": Decimal("0"),
            "pis": Decimal("0"),
            "cofins": Decimal("0"),
            "iss": Decimal("0"),
            "total": Decimal("0"),
            "liminar_aplicada": False,
        }

        # INSS (11%)
        if self.inss_retido:
            if self.inss_liminar_ativa and cliente_aceita_liminar:
                retencoes["inss"] = Decimal("0")
                retencoes["liminar_aplicada"] = True
                retencoes["liminar_numero"] = self.inss_liminar_numero
            else:
                if not self.inss_base_minima or valor_servico >= self.inss_base_minima:
                    retencoes["inss"] = valor_servico * self.inss_aliquota / 100

        # IR (1.5%) - Base minima R$ 666,66
        if self.ir_retido:
            if not self.ir_base_minima or valor_servico >= self.ir_base_minima:
                retencoes["ir"] = valor_servico * self.ir_aliquota / 100

        # PCC (PIS + COFINS + CSLL = 4.65%) - Base minima R$ 215,05
        valor_pcc = valor_servico * self.aliquota_pcc / 100
        if valor_pcc >= (self.pcc_base_minima or Decimal("0")):
            if self.pis_retido:
                retencoes["pis"] = valor_servico * self.pis_aliquota / 100
            if self.cofins_retido:
                retencoes["cofins"] = valor_servico * self.cofins_aliquota / 100
            if self.csll_retido:
                retencoes["csll"] = valor_servico * self.csll_aliquota / 100

        # ISS
        if self.iss_retido and self.iss_aliquota:
            retencoes["iss"] = valor_servico * self.iss_aliquota / 100

        # Total
        retencoes["total"] = (
            retencoes["inss"]
            + retencoes["ir"]
            + retencoes["csll"]
            + retencoes["pis"]
            + retencoes["cofins"]
            + retencoes["iss"]
        )

        retencoes["valor_liquido"] = valor_servico - retencoes["total"]

        return retencoes


# CFOPs comuns para servicos de vigilancia em Manaus/ZFM
CFOPS_VIGILANCIA_ZFM = {
    # Prestacao de servico (saida)
    "5933": "Prestacao de servico tributado pelo ISSQN",
    "6933": "Prestacao de servico tributado pelo ISSQN para outro estado",
    # Entradas (aquisicao de materiais para uso)
    "1556": "Compra de material para uso/consumo - dentro do estado",
    "2556": "Compra de material para uso/consumo - fora do estado",
    "1407": "Compra para uso/consumo em operacao com ZFM",
    "2407": "Compra para uso/consumo com incentivo de ICMS ZFM",
    # Ativo imobilizado
    "1551": "Compra de ativo imobilizado",
    "2551": "Compra de ativo imobilizado de outro estado",
    # Devolucao
    "5202": "Devolucao de compra para comercializacao",
    "6202": "Devolucao de compra para comercializacao - outro estado",
}
