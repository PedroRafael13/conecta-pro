"""Modelo de Arquivos SPED - Sistema Publico de Escrituracao Digital."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from core.models.base import Base

if TYPE_CHECKING:
    pass


class SPEDTipo(StrEnum):
    """Tipo de arquivo SPED."""

    EFD_ICMS_IPI = "efd_icms_ipi"  # EFD ICMS/IPI (Estadual)
    EFD_CONTRIBUICOES = "efd_contribuicoes"  # EFD Contribuicoes (PIS/COFINS)
    ECD = "ecd"  # Escrituracao Contabil Digital
    ECF = "ecf"  # Escrituracao Contabil Fiscal
    REINF = "reinf"  # Escrituracao das Retencoes (EFD-Reinf)
    ESOCIAL = "esocial"  # eSocial (Eventos trabalhistas)
    SPED_FISCAL = "sped_fiscal"  # Alias para EFD ICMS/IPI


class SPEDStatus(StrEnum):
    """Status do arquivo SPED."""

    RASCUNHO = "rascunho"
    EM_GERACAO = "em_geracao"
    GERADO = "gerado"
    VALIDANDO = "validando"
    VALIDADO = "validado"
    ERRO_VALIDACAO = "erro_validacao"
    TRANSMITINDO = "transmitindo"
    TRANSMITIDO = "transmitido"
    ERRO_TRANSMISSAO = "erro_transmissao"
    PROCESSANDO = "processando"
    ACEITO = "aceito"
    REJEITADO = "rejeitado"
    RETIFICADO = "retificado"


class SPEDFinalidade(StrEnum):
    """Finalidade do arquivo SPED."""

    ORIGINAL = "0"
    RETIFICADOR = "1"


class SPEDPerfil(StrEnum):
    """Perfil de apresentacao do SPED Fiscal."""

    A = "A"  # Maior detalhamento
    B = "B"  # Detalhamento mediano
    C = "C"  # Menor detalhamento


class ECDTipoECD(StrEnum):
    """Tipo de ECD."""

    LIVRO_DIARIO = "G"  # Livro Diario (completo sem escrituracao auxiliar)
    LIVRO_DIARIO_RESUMIDO = "R"  # Livro Diario com Escrituracao Resumida
    LIVRO_DIARIO_AUXILIAR = "A"  # Livro Diario Auxiliar
    LIVRO_RAZAO_AUXILIAR = "Z"  # Razao Auxiliar
    LIVRO_BALANCETES = "B"  # Balancetes Diarios e Balancos


class ECFFormaApuracao(StrEnum):
    """Forma de apuracao do IRPJ/CSLL."""

    LUCRO_REAL_ANUAL = "A"
    LUCRO_REAL_TRIMESTRAL = "T"


class SPEDFile(Base):
    """Arquivo SPED gerado."""

    __tablename__ = "sped_files"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    tipo = Column(String(30), nullable=False, index=True)
    versao_layout = Column(String(10), nullable=False)  # Versao do layout SPED
    finalidade = Column(String(1), nullable=False, default=SPEDFinalidade.ORIGINAL.value)
    perfil = Column(String(1), nullable=True)  # Para EFD ICMS/IPI

    # Periodo
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=True)  # Null para arquivos anuais

    # Status
    status = Column(String(20), nullable=False, default=SPEDStatus.RASCUNHO.value, index=True)
    data_geracao = Column(DateTime, nullable=True)
    data_validacao = Column(DateTime, nullable=True)
    data_transmissao = Column(DateTime, nullable=True)

    # Empresa
    cnpj = Column(String(14), nullable=False)
    razao_social = Column(String(150), nullable=False)
    inscricao_estadual = Column(String(14), nullable=True)
    uf = Column(String(2), nullable=True)

    # Arquivo
    nome_arquivo = Column(String(255), nullable=True)
    caminho_arquivo = Column(String(500), nullable=True)
    tamanho_bytes = Column(Integer, nullable=True)
    hash_arquivo = Column(String(64), nullable=True)  # SHA-256

    # Validacao (PVA)
    pva_versao = Column(String(20), nullable=True)
    pva_resultado = Column(String(20), nullable=True)
    pva_erros = Column(Integer, nullable=True, default=0)
    pva_avisos = Column(Integer, nullable=True, default=0)
    pva_log = Column(Text, nullable=True)

    # Transmissao
    protocolo = Column(String(50), nullable=True)
    recibo = Column(String(50), nullable=True)
    codigo_retorno = Column(String(10), nullable=True)
    mensagem_retorno = Column(Text, nullable=True)

    # Retificacao
    sped_retificado_id = Column(PGUUID(as_uuid=True), nullable=True)  # SPED que esta sendo retificado
    nire = Column(String(20), nullable=True)  # Para ECD retificadora

    # Estatisticas (JSONB)
    # Qtde de registros por bloco: {"0": 100, "C": 500, "D": 0, ...}
    estatisticas = Column(JSONB, nullable=True)

    # Valores resumo (JSONB)
    # {"total_entradas": 1000000, "total_saidas": 800000, "icms_debito": 50000, ...}
    valores_resumo = Column(JSONB, nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<SPEDFile {self.tipo} {self.periodo_inicio:%Y-%m} - {self.status}>"

    @property
    def is_transmitido(self) -> bool:
        """Verifica se foi transmitido."""
        return self.status in [SPEDStatus.TRANSMITIDO.value, SPEDStatus.ACEITO.value]

    @property
    def is_aceito(self) -> bool:
        """Verifica se foi aceito."""
        return self.status == SPEDStatus.ACEITO.value

    @property
    def pode_retificar(self) -> bool:
        """Verifica se pode ser retificado."""
        return self.status in [SPEDStatus.ACEITO.value, SPEDStatus.TRANSMITIDO.value]

    @property
    def nome_periodo(self) -> str:
        """Retorna nome do periodo."""
        if self.mes:
            return f"{self.ano:04d}-{self.mes:02d}"
        return str(self.ano)


class SPEDRegistro(Base):  # pylint: disable=too-few-public-methods
    """Registro individual do SPED (para rastreabilidade)."""

    __tablename__ = "sped_registros"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    sped_file_id = Column(PGUUID(as_uuid=True), ForeignKey("sped_files.id", ondelete="CASCADE"), nullable=False)

    # Identificacao
    bloco = Column(String(1), nullable=False)  # 0, C, D, E, etc.
    registro = Column(String(10), nullable=False)  # C100, C170, etc.
    linha = Column(Integer, nullable=False)

    # Conteudo
    conteudo = Column(Text, nullable=False)  # Linha completa
    campos = Column(JSONB, nullable=True)  # Campos parseados

    # Referencia
    documento_tipo = Column(String(20), nullable=True)  # nfe, nfse, lancamento, etc.
    documento_id = Column(PGUUID(as_uuid=True), nullable=True)  # ID do documento fonte

    # Validacao
    valido = Column(Boolean, default=True)
    erro = Column(String(255), nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<SPEDRegistro {self.bloco}{self.registro} L{self.linha}>"


class EFDICMSIPIResumo(Base):  # pylint: disable=too-few-public-methods
    """Resumo do EFD ICMS/IPI por periodo."""

    __tablename__ = "efd_icms_ipi_resumos"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    sped_file_id = Column(PGUUID(as_uuid=True), ForeignKey("sped_files.id", ondelete="CASCADE"), nullable=False)
    condominio_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Periodo
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)

    # Entradas
    valor_contabil_entradas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    base_icms_entradas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_entradas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    ipi_entradas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # Saidas
    valor_contabil_saidas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    base_icms_saidas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_saidas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    ipi_saidas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # ICMS ST
    icms_st_entradas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_st_saidas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # Apuracao ICMS
    icms_debito = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_credito = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_saldo_credor_anterior = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_outros_debitos = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_outros_creditos = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_estorno_debito = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_estorno_credito = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_saldo_devedor = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_saldo_credor = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    icms_a_recolher = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # Apuracao IPI
    ipi_debito = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    ipi_credito = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    ipi_saldo_credor_anterior = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    ipi_a_recolher = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    ipi_saldo_credor = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # Quantidades
    qtd_documentos_entradas = Column(Integer, nullable=False, default=0)
    qtd_documentos_saidas = Column(Integer, nullable=False, default=0)
    qtd_itens = Column(Integer, nullable=False, default=0)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<EFDICMSIPIResumo {self.ano:04d}-{self.mes:02d}>"


class EFDContribuicoesResumo(Base):  # pylint: disable=too-few-public-methods
    """Resumo do EFD Contribuicoes (PIS/COFINS)."""

    __tablename__ = "efd_contribuicoes_resumos"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    sped_file_id = Column(PGUUID(as_uuid=True), ForeignKey("sped_files.id", ondelete="CASCADE"), nullable=False)
    condominio_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Periodo
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)

    # Receitas
    receita_bruta_cumulativo = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    receita_bruta_nao_cumulativo = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    receita_bruta_total = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # PIS
    pis_base_calculo = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    pis_debito = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    pis_credito = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    pis_saldo_credor_anterior = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    pis_a_recolher = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    pis_saldo_credor = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # COFINS
    cofins_base_calculo = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    cofins_debito = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    cofins_credito = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    cofins_saldo_credor_anterior = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    cofins_a_recolher = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    cofins_saldo_credor = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # Retencoes na Fonte
    pis_retido = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    cofins_retido = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # Quantidades
    qtd_documentos_receitas = Column(Integer, nullable=False, default=0)
    qtd_documentos_creditos = Column(Integer, nullable=False, default=0)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<EFDContribuicoesResumo {self.ano:04d}-{self.mes:02d}>"


class ECDResumo(Base):  # pylint: disable=too-few-public-methods
    """Resumo da ECD (Escrituracao Contabil Digital)."""

    __tablename__ = "ecd_resumos"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    sped_file_id = Column(PGUUID(as_uuid=True), ForeignKey("sped_files.id", ondelete="CASCADE"), nullable=False)
    condominio_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Periodo
    ano = Column(Integer, nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)

    # Tipo
    tipo_ecd = Column(String(1), nullable=False, default=ECDTipoECD.LIVRO_DIARIO.value)

    # Saldos
    total_ativo = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    total_passivo = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    patrimonio_liquido = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # Resultado
    total_receitas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    total_despesas = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    resultado_exercicio = Column(Numeric(15, 2), nullable=False, default=Decimal("0"))

    # Quantidades
    qtd_lancamentos = Column(Integer, nullable=False, default=0)
    qtd_contas = Column(Integer, nullable=False, default=0)
    qtd_centros_custo = Column(Integer, nullable=False, default=0)

    # Termos
    termo_abertura = Column(Text, nullable=True)
    termo_encerramento = Column(Text, nullable=True)

    # Hash de validacao
    hash_abertura = Column(String(64), nullable=True)
    hash_encerramento = Column(String(64), nullable=True)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<ECDResumo {self.ano}>"
