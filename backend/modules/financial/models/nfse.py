"""Modelo de NFS-e - Nota Fiscal de Servicos Eletronica."""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from core.models.base import Base


class NFSeStatus(StrEnum):
    """Status da NFS-e."""

    RASCUNHO = "rascunho"
    EM_DIGITACAO = "em_digitacao"
    PENDENTE_ENVIO = "pendente_envio"
    ENVIADA = "enviada"
    PROCESSANDO = "processando"
    AUTORIZADA = "autorizada"
    REJEITADA = "rejeitada"
    CANCELADA = "cancelada"
    SUBSTITUIDA = "substituida"
    ERRO = "erro"


class NFSeNaturezaOperacao(StrEnum):
    """Natureza da operacao da NFS-e."""

    TRIBUTACAO_MUNICIPIO = "1"  # Tributacao no municipio
    TRIBUTACAO_FORA_MUNICIPIO = "2"  # Tributacao fora do municipio
    ISENCAO = "3"  # Isencao
    IMUNE = "4"  # Imune
    EXIGIBILIDADE_SUSPENSA_DECISAO_JUDICIAL = "5"
    EXIGIBILIDADE_SUSPENSA_PROCESSO_ADM = "6"


class NFSeRegimeEspecial(StrEnum):
    """Regime especial de tributacao."""

    NENHUM = "0"
    MICROEMPRESA = "1"
    ESTIMATIVA = "2"
    SOCIEDADE_PROFISSIONAIS = "3"
    COOPERATIVA = "4"
    MEI = "5"
    ME_EPP_SIMPLES = "6"


class NFSeSimNao(StrEnum):
    """Opcao Sim/Nao."""

    SIM = "1"
    NAO = "2"


class NFSeLocalServico(StrEnum):
    """Local de prestacao do servico."""

    PRESTADOR = "prestador"
    TOMADOR = "tomador"
    OUTRO = "outro"


class NFSeTipoRPS(StrEnum):
    """Tipo de RPS."""

    RPS = "1"  # Recibo Provisorio de Servicos
    NFSE_CONJUGADA = "2"  # NFS-e Conjugada
    CUPOM = "3"  # Cupom


class NFSeResponsavelRetencao(StrEnum):
    """Responsavel pela retencao do ISS."""

    TOMADOR = "1"
    INTERMEDIARIO = "2"


class NFSeLayoutPadrao(StrEnum):
    """Layout padrao de NFS-e (varia por municipio)."""

    ABRASF_1_0 = "abrasf_1_0"
    ABRASF_2_0 = "abrasf_2_0"
    ABRASF_2_03 = "abrasf_2_03"
    GINFES = "ginfes"
    BETHA = "betha"
    WEBISS = "webiss"
    ISSNET = "issnet"
    DSF = "dsf"
    ELOTECH = "elotech"
    IPM = "ipm"
    SIMPLISS = "simpliss"
    SMARAPD = "smarapd"
    THEMA = "thema"
    SIGISS = "sigiss"
    GOVDIGITAL = "govdigital"
    PUBLICA = "publica"
    NACIONAL = "nacional"  # Padrao Nacional (novo)


class NFSe(Base):
    """Nota Fiscal de Servicos Eletronica."""

    __tablename__ = "nfse"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Identificacao NFS-e
    numero = Column(String(20), nullable=True, index=True)
    codigo_verificacao = Column(String(50), nullable=True, index=True)
    status = Column(String(20), nullable=False, default=NFSeStatus.RASCUNHO.value, index=True)

    # RPS (Recibo Provisorio de Servicos)
    rps_numero = Column(Integer, nullable=True, index=True)
    rps_serie = Column(String(5), nullable=True)
    rps_tipo = Column(String(1), nullable=False, default=NFSeTipoRPS.RPS.value)
    rps_data_emissao = Column(Date, nullable=True)

    # Layout do municipio
    layout = Column(String(20), nullable=False, default=NFSeLayoutPadrao.ABRASF_2_03.value)
    codigo_municipio = Column(String(7), nullable=False)  # Codigo IBGE
    municipio_nome = Column(String(100), nullable=True)

    # Datas
    data_emissao = Column(DateTime, nullable=True)
    data_competencia = Column(Date, nullable=False, default=date.today)
    data_cancelamento = Column(DateTime, nullable=True)

    # Prestador (Emitente)
    prestador_cnpj = Column(String(14), nullable=False)
    prestador_inscricao_municipal = Column(String(20), nullable=True)
    prestador_razao_social = Column(String(150), nullable=False)
    prestador_nome_fantasia = Column(String(60), nullable=True)
    prestador_endereco = Column(JSONB, nullable=True)
    prestador_email = Column(String(200), nullable=True)
    prestador_telefone = Column(String(20), nullable=True)
    prestador_regime_tributacao = Column(String(1), nullable=True)
    prestador_simples_nacional = Column(Boolean, default=False)
    prestador_incentivo_fiscal = Column(Boolean, default=False)

    # Tomador (Destinatario)
    tomador_tipo = Column(String(1), nullable=True)  # 1=PF, 2=PJ
    tomador_cpf_cnpj = Column(String(14), nullable=True, index=True)
    tomador_inscricao_municipal = Column(String(20), nullable=True)
    tomador_inscricao_estadual = Column(String(20), nullable=True)
    tomador_razao_social = Column(String(150), nullable=True)
    tomador_email = Column(String(200), nullable=True)
    tomador_telefone = Column(String(20), nullable=True)
    tomador_endereco = Column(JSONB, nullable=True)

    # Intermediario (opcional)
    intermediario_cpf_cnpj = Column(String(14), nullable=True)
    intermediario_razao_social = Column(String(150), nullable=True)
    intermediario_inscricao_municipal = Column(String(20), nullable=True)

    # Servico
    codigo_servico = Column(String(20), nullable=False)  # Codigo do servico na LC 116/2003
    codigo_servico_municipal = Column(String(20), nullable=True)  # Codigo do servico no municipio
    codigo_cnae = Column(String(10), nullable=True)  # CNAE
    discriminacao = Column(Text, nullable=False)  # Descricao do servico
    natureza_operacao = Column(String(1), nullable=False, default=NFSeNaturezaOperacao.TRIBUTACAO_MUNICIPIO.value)
    regime_especial = Column(String(1), nullable=True)

    # Local de prestacao
    local_prestacao = Column(String(20), nullable=False, default=NFSeLocalServico.PRESTADOR.value)
    municipio_prestacao = Column(String(7), nullable=True)  # Codigo IBGE
    municipio_prestacao_nome = Column(String(100), nullable=True)
    uf_prestacao = Column(String(2), nullable=True)

    # Valores
    valor_servicos = Column(Numeric(15, 2), nullable=False)
    valor_deducoes = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_desconto_incondicionado = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_desconto_condicionado = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_outras_retencoes = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_base_calculo = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    valor_liquido = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # ISS
    aliquota_iss = Column(Numeric(8, 4), nullable=False, default=Decimal("0"))
    valor_iss = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    iss_retido = Column(Boolean, default=False)
    valor_iss_retido = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    responsavel_retencao = Column(String(1), nullable=True)

    # Retencoes Federais
    valor_pis = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    aliquota_pis = Column(Numeric(8, 4), nullable=True)
    valor_cofins = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    aliquota_cofins = Column(Numeric(8, 4), nullable=True)
    valor_inss = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    aliquota_inss = Column(Numeric(8, 4), nullable=True)
    valor_ir = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    aliquota_ir = Column(Numeric(8, 4), nullable=True)
    valor_csll = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    aliquota_csll = Column(Numeric(8, 4), nullable=True)
    valor_total_retencoes = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # Construcao Civil
    obra_codigo = Column(String(20), nullable=True)
    obra_art = Column(String(20), nullable=True)  # ART do CREA

    # Substituicao
    nfse_substituida_numero = Column(String(20), nullable=True)
    nfse_substituida_codigo = Column(String(50), nullable=True)
    motivo_substituicao = Column(String(255), nullable=True)

    # Cancelamento
    codigo_cancelamento = Column(String(10), nullable=True)
    motivo_cancelamento = Column(String(255), nullable=True)

    # Retorno Prefeitura
    protocolo = Column(String(50), nullable=True)
    codigo_retorno = Column(String(10), nullable=True)
    mensagem_retorno = Column(Text, nullable=True)
    link_nfse = Column(String(500), nullable=True)  # URL para visualizacao

    # XML
    xml_envio = Column(Text, nullable=True)
    xml_retorno = Column(Text, nullable=True)
    xml_cancelamento = Column(Text, nullable=True)

    # Lote (para envio em lote)
    lote_numero = Column(String(20), nullable=True)
    lote_id = Column(PGUUID(as_uuid=True), nullable=True)

    # Referencias
    contrato_id = Column(PGUUID(as_uuid=True), nullable=True)  # Contrato de servico
    ordem_servico_id = Column(PGUUID(as_uuid=True), nullable=True)  # Ordem de servico

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<NFSe {self.numero or self.rps_numero} - {self.status}>"

    @property
    def is_autorizada(self) -> bool:
        """Verifica se NFS-e esta autorizada."""
        return self.status == NFSeStatus.AUTORIZADA.value

    @property
    def is_cancelada(self) -> bool:
        """Verifica se NFS-e esta cancelada."""
        return self.status == NFSeStatus.CANCELADA.value

    @property
    def is_rps(self) -> bool:
        """Verifica se ainda e RPS (nao convertida em NFS-e)."""
        return self.numero is None and self.rps_numero is not None

    @property
    def pode_cancelar(self) -> bool:
        """Verifica se NFS-e pode ser cancelada."""
        return self.status == NFSeStatus.AUTORIZADA.value

    @property
    def pode_substituir(self) -> bool:
        """Verifica se NFS-e pode ser substituida."""
        return self.status == NFSeStatus.AUTORIZADA.value

    @property
    def pode_editar(self) -> bool:
        """Verifica se NFS-e pode ser editada."""
        return self.status in [
            NFSeStatus.RASCUNHO.value,
            NFSeStatus.EM_DIGITACAO.value,
            NFSeStatus.REJEITADA.value,
            NFSeStatus.ERRO.value,
        ]

    def calcular_valores(self) -> None:
        """Recalcula valores da NFS-e."""
        # Base de calculo = Servicos - Deducoes - Descontos
        self.valor_base_calculo = self.valor_servicos - self.valor_deducoes - self.valor_desconto_incondicionado

        self.valor_base_calculo = max(self.valor_base_calculo, Decimal("0"))

        # ISS
        self.valor_iss = self.valor_base_calculo * self.aliquota_iss / 100

        if self.iss_retido:
            self.valor_iss_retido = self.valor_iss

        # Retencoes
        if self.aliquota_pis:
            self.valor_pis = self.valor_servicos * self.aliquota_pis / 100
        if self.aliquota_cofins:
            self.valor_cofins = self.valor_servicos * self.aliquota_cofins / 100
        if self.aliquota_inss:
            self.valor_inss = self.valor_servicos * self.aliquota_inss / 100
        if self.aliquota_ir:
            self.valor_ir = self.valor_servicos * self.aliquota_ir / 100
        if self.aliquota_csll:
            self.valor_csll = self.valor_servicos * self.aliquota_csll / 100

        # Total de retencoes
        self.valor_total_retencoes = (
            self.valor_iss_retido
            + self.valor_pis
            + self.valor_cofins
            + self.valor_inss
            + self.valor_ir
            + self.valor_csll
            + self.valor_outras_retencoes
        )

        # Valor liquido
        self.valor_liquido = (
            self.valor_servicos
            - self.valor_desconto_incondicionado
            - self.valor_desconto_condicionado
            - self.valor_total_retencoes
        )


class NFSeLote(Base):  # pylint: disable=too-few-public-methods
    """Lote de NFS-e para envio em lote."""

    __tablename__ = "nfse_lotes"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    numero_lote = Column(String(20), nullable=False, index=True)
    quantidade_rps = Column(Integer, nullable=False, default=0)
    versao = Column(String(10), nullable=True)

    # Status
    status = Column(String(20), nullable=False, default="pendente")  # pendente, enviado, processado, erro
    data_envio = Column(DateTime, nullable=True)
    data_processamento = Column(DateTime, nullable=True)

    # Retorno
    protocolo = Column(String(50), nullable=True)
    codigo_retorno = Column(String(10), nullable=True)
    mensagem_retorno = Column(Text, nullable=True)

    # XML
    xml_envio = Column(Text, nullable=True)
    xml_retorno = Column(Text, nullable=True)

    # Notas do lote (JSONB array)
    # [{nfse_id, rps_numero, status, codigo_retorno, mensagem}]
    notas = Column(JSONB, nullable=True, default=list)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<NFSeLote {self.numero_lote} ({self.quantidade_rps} RPS)>"


class CodigoServico(Base):  # pylint: disable=too-few-public-methods
    """Codigo de servico conforme LC 116/2003."""

    __tablename__ = "codigos_servico"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identificacao
    codigo = Column(String(20), nullable=False, unique=True, index=True)
    descricao = Column(Text, nullable=False)
    subitem = Column(String(10), nullable=True)  # Subitem da LC 116

    # Aliquotas padrao
    aliquota_minima = Column(Numeric(8, 4), nullable=True, default=Decimal("2"))
    aliquota_maxima = Column(Numeric(8, 4), nullable=True, default=Decimal("5"))

    # ISS
    iss_retido_obrigatorio = Column(Boolean, default=False)
    local_tributacao = Column(String(20), nullable=True)  # prestador, tomador

    # Regras
    permite_deducao = Column(Boolean, default=False)
    exige_obra = Column(Boolean, default=False)  # Construcao civil
    exige_retencoes_federais = Column(Boolean, default=False)

    # CNAE relacionados (JSONB array)
    cnaes_relacionados = Column(JSONB, nullable=True, default=list)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<CodigoServico {self.codigo}: {self.descricao[:50]}>"
