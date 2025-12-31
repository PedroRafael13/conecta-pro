"""Modelo de NF-e - Nota Fiscal Eletronica."""

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


class NFeTipo(str, Enum):
    """Tipo de NF-e."""

    ENTRADA = "0"  # Entrada
    SAIDA = "1"  # Saida


class NFeStatus(str, Enum):
    """Status da NF-e."""

    RASCUNHO = "rascunho"
    EM_DIGITACAO = "em_digitacao"
    PENDENTE_ENVIO = "pendente_envio"
    ENVIADA = "enviada"
    AUTORIZADA = "autorizada"
    DENEGADA = "denegada"
    REJEITADA = "rejeitada"
    CANCELADA = "cancelada"
    INUTILIZADA = "inutilizada"
    CONTINGENCIA = "contingencia"


class NFeFinalidade(str, Enum):
    """Finalidade da NF-e."""

    NORMAL = "1"  # NF-e normal
    COMPLEMENTAR = "2"  # NF-e complementar
    AJUSTE = "3"  # NF-e de ajuste
    DEVOLUCAO = "4"  # Devolucao de mercadoria


class NFeModalidadeFrete(str, Enum):
    """Modalidade do frete."""

    CIF = "0"  # Contratacao do Frete por conta do Remetente (CIF)
    FOB = "1"  # Contratacao do Frete por conta do Destinatario (FOB)
    TERCEIROS = "2"  # Contratacao do Frete por conta de Terceiros
    PROPRIO_REMETENTE = "3"  # Transporte Proprio por conta do Remetente
    PROPRIO_DESTINATARIO = "4"  # Transporte Proprio por conta do Destinatario
    SEM_FRETE = "9"  # Sem Ocorrencia de Transporte


class NFeFormaPagamento(str, Enum):
    """Forma de pagamento da NF-e."""

    DINHEIRO = "01"
    CHEQUE = "02"
    CARTAO_CREDITO = "03"
    CARTAO_DEBITO = "04"
    CREDITO_LOJA = "05"
    VALE_ALIMENTACAO = "10"
    VALE_REFEICAO = "11"
    VALE_PRESENTE = "12"
    VALE_COMBUSTIVEL = "13"
    DUPLICATA_MERCANTIL = "14"
    BOLETO_BANCARIO = "15"
    DEPOSITO_BANCARIO = "16"
    PIX = "17"
    TRANSFERENCIA = "18"
    PROGRAMA_FIDELIDADE = "19"
    SEM_PAGAMENTO = "90"
    OUTROS = "99"


class NFeAmbiente(str, Enum):
    """Ambiente de emissao."""

    PRODUCAO = "1"
    HOMOLOGACAO = "2"


class NFeProcessoEmissao(str, Enum):
    """Processo de emissao."""

    EMISSAO_NORMAL = "0"
    AVULSA_FISCO = "1"
    AVULSA_CONTRIBUINTE = "2"
    CONTRIBUINTE_SITE_FISCO = "3"


class NFeContingencia(str, Enum):
    """Tipo de contingencia."""

    NORMAL = "normal"
    SCAN = "scan"  # Sistema de Contingencia do Ambiente Nacional
    SVC_AN = "svc_an"  # SEFAZ Virtual de Contingencia - Ambiente Nacional
    SVC_RS = "svc_rs"  # SEFAZ Virtual de Contingencia - Rio Grande do Sul
    DPEC = "dpec"  # Declaracao Previa de Emissao em Contingencia
    FSDA = "fsda"  # Formulario de Seguranca para Impressao de DANFE
    OFFLINE = "offline"


class NFe(Base):
    """Nota Fiscal Eletronica."""

    __tablename__ = "nfe"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Identificacao da NF-e
    chave_acesso = Column(String(44), nullable=True, unique=True, index=True)
    numero = Column(Integer, nullable=True, index=True)
    serie = Column(String(3), nullable=False, default="1")
    tipo = Column(String(1), nullable=False, default=NFeTipo.SAIDA.value)
    modelo = Column(String(2), nullable=False, default="55")  # 55 = NF-e, 65 = NFC-e

    # Status
    status = Column(String(20), nullable=False, default=NFeStatus.RASCUNHO.value, index=True)
    ambiente = Column(String(1), nullable=False, default=NFeAmbiente.HOMOLOGACAO.value)
    finalidade = Column(String(1), nullable=False, default=NFeFinalidade.NORMAL.value)

    # Datas
    data_emissao = Column(DateTime, nullable=True)
    data_saida_entrada = Column(DateTime, nullable=True)
    data_autorizacao = Column(DateTime, nullable=True)
    data_cancelamento = Column(DateTime, nullable=True)

    # Emitente
    emitente_cnpj = Column(String(14), nullable=False)
    emitente_ie = Column(String(14), nullable=True)
    emitente_razao_social = Column(String(150), nullable=False)
    emitente_nome_fantasia = Column(String(60), nullable=True)
    emitente_endereco = Column(
        JSONB, nullable=True
    )  # {logradouro, numero, bairro, cidade, uf, cep, pais}

    # Destinatario
    destinatario_tipo = Column(String(1), nullable=True)  # 1=PF, 2=PJ
    destinatario_cpf_cnpj = Column(String(14), nullable=True, index=True)
    destinatario_ie = Column(String(14), nullable=True)
    destinatario_razao_social = Column(String(150), nullable=True)
    destinatario_email = Column(String(200), nullable=True)
    destinatario_endereco = Column(JSONB, nullable=True)
    destinatario_indicador_ie = Column(
        String(1), nullable=True
    )  # 1=Contribuinte, 2=Isento, 9=Nao contribuinte

    # Valores Totais
    valor_produtos = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_frete = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_seguro = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_desconto = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_outras_despesas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # Impostos Totais
    valor_icms = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_icms_st = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_ipi = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_pis = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_cofins = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_ii = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_fcpufdest = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_icmsufdest = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_icmsufremet = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_total_tributos = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # Valor Total da Nota
    valor_total = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # Frete
    modalidade_frete = Column(String(1), nullable=False, default=NFeModalidadeFrete.SEM_FRETE.value)
    transportadora_cnpj = Column(String(14), nullable=True)
    transportadora_razao_social = Column(String(150), nullable=True)
    transportadora_ie = Column(String(14), nullable=True)
    transportadora_endereco = Column(String(200), nullable=True)
    transportadora_uf = Column(String(2), nullable=True)
    veiculo_placa = Column(String(7), nullable=True)
    veiculo_uf = Column(String(2), nullable=True)

    # Volumes
    volumes = Column(
        JSONB, nullable=True
    )  # [{qtde, especie, marca, numeracao, peso_liq, peso_brut}]

    # Pagamento
    forma_pagamento = Column(String(2), nullable=True)
    pagamentos = Column(JSONB, nullable=True)  # [{forma, valor, vencimento}]

    # Informacoes Adicionais
    natureza_operacao = Column(String(60), nullable=False, default="VENDA")
    informacoes_adicionais_fisco = Column(Text, nullable=True)
    informacoes_adicionais_contribuinte = Column(Text, nullable=True)

    # SEFAZ / Retorno
    protocolo = Column(String(20), nullable=True)
    protocolo_data = Column(DateTime, nullable=True)
    codigo_status = Column(String(5), nullable=True)
    motivo_status = Column(String(300), nullable=True)
    digval = Column(String(30), nullable=True)

    # Cancelamento
    protocolo_cancelamento = Column(String(20), nullable=True)
    justificativa_cancelamento = Column(String(255), nullable=True)

    # Contingencia
    contingencia_tipo = Column(String(20), nullable=True)
    contingencia_motivo = Column(String(255), nullable=True)
    contingencia_data = Column(DateTime, nullable=True)

    # XML
    xml_envio = Column(Text, nullable=True)
    xml_retorno = Column(Text, nullable=True)
    xml_cancelamento = Column(Text, nullable=True)

    # Referencias
    nfe_referenciada = Column(String(44), nullable=True)  # Chave de NF-e referenciada
    pedido_id = Column(PGUUID(as_uuid=True), nullable=True)  # Pedido de venda origem
    nf_entrada_id = Column(PGUUID(as_uuid=True), nullable=True)  # NF de entrada (devolucao)

    # Relacionamentos
    itens = relationship("NFeItem", back_populates="nfe", cascade="all, delete-orphan")

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<NFe {self.numero}/{self.serie} - {self.status}>"

    @property
    def is_autorizada(self) -> bool:
        """Verifica se NF-e esta autorizada."""
        return self.status == NFeStatus.AUTORIZADA.value

    @property
    def is_cancelada(self) -> bool:
        """Verifica se NF-e esta cancelada."""
        return self.status == NFeStatus.CANCELADA.value

    @property
    def pode_cancelar(self) -> bool:
        """Verifica se NF-e pode ser cancelada."""
        if not self.is_autorizada:
            return False
        if not self.data_autorizacao:
            return False
        # Prazo de 24 horas para cancelamento
        from datetime import timedelta

        return datetime.utcnow() <= self.data_autorizacao + timedelta(hours=24)

    @property
    def pode_editar(self) -> bool:
        """Verifica se NF-e pode ser editada."""
        return self.status in [
            NFeStatus.RASCUNHO.value,
            NFeStatus.EM_DIGITACAO.value,
            NFeStatus.REJEITADA.value,
        ]

    def gerar_chave_acesso(
        self,
        codigo_uf: str,
        ano_mes: str,
        cnpj: str,
        modelo: str,
        serie: str,
        numero: str,
        tipo_emissao: str,
        codigo_numerico: str,
    ) -> str:
        """Gera chave de acesso da NF-e (sem digito verificador)."""
        chave = f"{codigo_uf}{ano_mes}{cnpj}{modelo}{serie.zfill(3)}{numero.zfill(9)}{tipo_emissao}{codigo_numerico}"
        # Calcula digito verificador
        peso = 2
        soma = 0
        for digito in reversed(chave):
            soma += int(digito) * peso
            peso = peso + 1 if peso < 9 else 2
        resto = soma % 11
        dv = 0 if resto < 2 else 11 - resto
        return chave + str(dv)

    def calcular_totais(self) -> None:
        """Recalcula totais da NF-e."""
        self.valor_produtos = (
            sum(item.valor_total for item in self.itens) if self.itens else Decimal("0")
        )
        self.valor_icms = (
            sum(item.valor_icms for item in self.itens) if self.itens else Decimal("0")
        )
        self.valor_icms_st = (
            sum(item.valor_icms_st or Decimal("0") for item in self.itens)
            if self.itens
            else Decimal("0")
        )
        self.valor_ipi = (
            sum(item.valor_ipi or Decimal("0") for item in self.itens)
            if self.itens
            else Decimal("0")
        )
        self.valor_pis = sum(item.valor_pis for item in self.itens) if self.itens else Decimal("0")
        self.valor_cofins = (
            sum(item.valor_cofins for item in self.itens) if self.itens else Decimal("0")
        )
        self.valor_total_tributos = (
            self.valor_icms
            + self.valor_icms_st
            + self.valor_ipi
            + self.valor_pis
            + self.valor_cofins
            + self.valor_ii
        )
        self.valor_total = (
            self.valor_produtos
            + self.valor_frete
            + self.valor_seguro
            + self.valor_outras_despesas
            + self.valor_icms_st
            + self.valor_ipi
            - self.valor_desconto
        )


class NFeItem(Base):
    """Item da NF-e."""

    __tablename__ = "nfe_itens"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    nfe_id = Column(PGUUID(as_uuid=True), ForeignKey("nfe.id", ondelete="CASCADE"), nullable=False)

    # Identificacao
    numero_item = Column(Integer, nullable=False)
    produto_id = Column(PGUUID(as_uuid=True), nullable=True)

    # Produto
    codigo_produto = Column(String(60), nullable=False)
    codigo_barras = Column(String(14), nullable=True)  # GTIN/EAN
    descricao = Column(String(120), nullable=False)
    ncm = Column(String(8), nullable=False)
    cest = Column(String(7), nullable=True)  # Codigo Especificador ST
    cfop = Column(String(4), nullable=False)
    unidade = Column(String(6), nullable=False)
    quantidade = Column(Numeric(15, 4), nullable=False)
    valor_unitario = Column(Numeric(21, 10), nullable=False)
    valor_total = Column(Numeric(15, 2), nullable=False)

    # Desconto/Frete/Seguro/Outras
    valor_desconto = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_frete = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_seguro = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_outras_despesas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # ICMS
    icms_origem = Column(String(1), nullable=False, default="0")
    icms_cst = Column(String(3), nullable=True)
    icms_csosn = Column(String(3), nullable=True)  # Simples Nacional
    icms_modbc = Column(String(1), nullable=True)
    icms_reducao_bc = Column(Numeric(8, 4), nullable=True)
    icms_base = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_aliquota = Column(Numeric(8, 4), nullable=False, default=Decimal("0"))
    valor_icms = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # ICMS ST
    icms_st_modbc = Column(String(1), nullable=True)
    icms_st_mva = Column(Numeric(8, 4), nullable=True)
    icms_st_reducao_bc = Column(Numeric(8, 4), nullable=True)
    icms_st_base = Column(Numeric(15, 2), nullable=True)
    icms_st_aliquota = Column(Numeric(8, 4), nullable=True)
    valor_icms_st = Column(Numeric(15, 2), nullable=True)

    # IPI
    ipi_cst = Column(String(2), nullable=True)
    ipi_classe = Column(String(5), nullable=True)
    ipi_codigo = Column(String(10), nullable=True)
    ipi_base = Column(Numeric(15, 2), nullable=True)
    ipi_aliquota = Column(Numeric(8, 4), nullable=True)
    valor_ipi = Column(Numeric(15, 2), nullable=True)

    # PIS
    pis_cst = Column(String(2), nullable=False, default="01")
    pis_base = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    pis_aliquota = Column(Numeric(8, 4), nullable=False, default=Decimal("0"))
    valor_pis = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # COFINS
    cofins_cst = Column(String(2), nullable=False, default="01")
    cofins_base = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    cofins_aliquota = Column(Numeric(8, 4), nullable=False, default=Decimal("0"))
    valor_cofins = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # II (Imposto de Importacao)
    ii_base = Column(Numeric(15, 2), nullable=True)
    ii_despesas_aduaneiras = Column(Numeric(15, 2), nullable=True)
    ii_iof = Column(Numeric(15, 2), nullable=True)
    valor_ii = Column(Numeric(15, 2), nullable=True)

    # Valor aproximado tributos (Lei Transparencia)
    valor_tributos_aproximado = Column(Numeric(15, 2), nullable=True)
    percentual_tributos_federais = Column(Numeric(8, 4), nullable=True)
    percentual_tributos_estaduais = Column(Numeric(8, 4), nullable=True)
    percentual_tributos_municipais = Column(Numeric(8, 4), nullable=True)

    # Informacoes adicionais
    informacoes_adicionais = Column(String(500), nullable=True)
    pedido_compra = Column(String(15), nullable=True)
    item_pedido_compra = Column(Integer, nullable=True)

    # Relacionamentos
    nfe = relationship("NFe", back_populates="itens")

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<NFeItem {self.numero_item}: {self.descricao}>"

    def calcular_impostos(self, config: Optional[Any] = None) -> None:
        """Calcula impostos do item."""
        # Valor base para calculo
        base = self.valor_total - self.valor_desconto + self.valor_frete + self.valor_seguro

        # ICMS
        if self.icms_reducao_bc and self.icms_reducao_bc > 0:
            self.icms_base = base * (1 - self.icms_reducao_bc / 100)
        else:
            self.icms_base = base
        self.valor_icms = self.icms_base * self.icms_aliquota / 100

        # PIS
        self.pis_base = base
        self.valor_pis = self.pis_base * self.pis_aliquota / 100

        # COFINS
        self.cofins_base = base
        self.valor_cofins = self.cofins_base * self.cofins_aliquota / 100

        # IPI (sobre valor produto + frete + seguro + outras)
        if self.ipi_aliquota and self.ipi_aliquota > 0:
            self.ipi_base = base
            self.valor_ipi = self.ipi_base * self.ipi_aliquota / 100

        # Valor aproximado de tributos
        self.valor_tributos_aproximado = (
            self.valor_icms + (self.valor_ipi or Decimal("0")) + self.valor_pis + self.valor_cofins
        )
