"""
Modelos de banco de dados para dados sincronizados dos portais governamentais.

Este modulo define as tabelas para armazenar:
- Notas Fiscais (NF-e, NFC-e, NFS-e, CT-e, MDF-e)
- Eventos eSocial
- Guias de impostos (FGTS, INSS, DARF)
- Certidoes e comprovantes
- Dados cadastrais da Receita Federal
- Logs de sincronizacao
"""

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# =============================================================================
# ENUMS
# =============================================================================


class TipoDocumentoFiscal(StrEnum):
    """Tipos de documentos fiscais."""

    NFE = "nfe"
    NFCE = "nfce"
    NFSE = "nfse"
    CTE = "cte"
    MDFE = "mdfe"


class StatusDocumentoFiscal(StrEnum):
    """Status de documentos fiscais."""

    AUTORIZADO = "autorizado"
    AUTORIZADA = "autorizada"
    CANCELADO = "cancelado"
    CANCELADA = "cancelada"
    DENEGADO = "denegado"
    INUTILIZADO = "inutilizado"
    REJEITADO = "rejeitado"
    PENDENTE = "pendente"
    SUBSTITUIDA = "substituida"
    ENCERRADO = "encerrado"


class StatusEventoReinf(StrEnum):
    """Status de eventos EFD-Reinf."""

    PENDENTE = "pendente"
    ENVIADO = "enviado"
    ACEITO = "aceito"
    REJEITADO = "rejeitado"


class TipoParticipacao(StrEnum):
    """Tipo de participacao em documento fiscal."""

    EMITENTE = "emitente"
    DESTINATARIO = "destinatario"
    TRANSPORTADOR = "transportador"


class TipoEventoESocial(StrEnum):
    """Tipos de eventos eSocial."""

    S1000 = "S-1000"  # Empregador
    S1200 = "S-1200"  # Remuneracao
    S1210 = "S-1210"  # Pagamentos
    S2200 = "S-2200"  # Admissao
    S2205 = "S-2205"  # Alteracao Cadastral
    S2206 = "S-2206"  # Alteracao Contrato
    S2210 = "S-2210"  # CAT
    S2220 = "S-2220"  # Monitoramento Saude
    S2230 = "S-2230"  # Afastamento
    S2240 = "S-2240"  # Condicoes Ambientais
    S2299 = "S-2299"  # Desligamento
    S2300 = "S-2300"  # TSV Inicio
    S2399 = "S-2399"  # TSV Termino
    S3000 = "S-3000"  # Exclusao


class StatusEventoESocial(StrEnum):
    """Status de eventos eSocial."""

    PENDENTE = "pendente"
    ENVIADO = "enviado"
    PROCESSANDO = "processando"
    ACEITO = "aceito"
    REJEITADO = "rejeitado"
    ERRO = "erro"


class TipoGuia(StrEnum):
    """Tipos de guias de recolhimento."""

    FGTS = "fgts"
    FGTS_RESCISORIO = "fgts_rescisorio"
    INSS = "inss"
    IRRF = "irrf"
    DARF = "darf"
    DAS = "das"
    GPS = "gps"
    GFIP = "gfip"


class StatusGuia(StrEnum):
    """Status de guias."""

    GERADA = "gerada"
    PAGA = "paga"
    VENCIDA = "vencida"
    CANCELADA = "cancelada"


class StatusSincronizacao(StrEnum):
    """Status de sincronizacao."""

    SUCESSO = "sucesso"
    ERRO = "erro"
    PARCIAL = "parcial"
    PENDENTE = "pendente"
    EXECUTANDO = "executando"


class TipoSincronizacao(StrEnum):
    """Tipos de sincronizacao."""

    COMPLETA = "completa"
    INCREMENTAL = "incremental"
    MANUAL = "manual"
    AGENDADA = "agendada"


# =============================================================================
# MODELO BASE
# =============================================================================


class BaseModel:
    """Modelo base com campos comuns."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = Column(Boolean, default=True, nullable=False)


# =============================================================================
# DOCUMENTOS FISCAIS
# =============================================================================


class DocumentoFiscal(Base, BaseModel):
    """Documento fiscal (NF-e, NFC-e, NFS-e, CT-e, MDF-e)."""

    __tablename__ = "gov_documentos_fiscais"

    # Identificacao
    tipo = Column(SQLEnum(TipoDocumentoFiscal), nullable=False, index=True)
    chave_acesso = Column(String(44), unique=True, index=True)
    numero = Column(Integer, nullable=False)
    serie = Column(Integer, default=1)

    # Empresa
    cnpj_empresa = Column(String(14), nullable=False, index=True)
    tipo_participacao = Column(SQLEnum(TipoParticipacao), nullable=False)

    # Emitente
    cnpj_emitente = Column(String(14), index=True)
    razao_social_emitente = Column(String(200))
    uf_emitente = Column(String(2))

    # Destinatario
    cnpj_cpf_destinatario = Column(String(14), index=True)
    razao_social_destinatario = Column(String(200))
    uf_destinatario = Column(String(2))

    # Datas
    data_emissao = Column(DateTime, nullable=False, index=True)
    data_autorizacao = Column(DateTime)
    data_cancelamento = Column(DateTime)

    # Valores
    valor_total = Column(Numeric(15, 2), nullable=False)
    valor_produtos = Column(Numeric(15, 2))
    valor_servicos = Column(Numeric(15, 2))
    valor_desconto = Column(Numeric(15, 2), default=0)
    valor_frete = Column(Numeric(15, 2), default=0)

    # Impostos
    valor_icms = Column(Numeric(15, 2), default=0)
    valor_icms_st = Column(Numeric(15, 2), default=0)
    valor_ipi = Column(Numeric(15, 2), default=0)
    valor_pis = Column(Numeric(15, 2), default=0)
    valor_cofins = Column(Numeric(15, 2), default=0)
    valor_iss = Column(Numeric(15, 2), default=0)
    valor_irrf = Column(Numeric(15, 2), default=0)
    valor_csll = Column(Numeric(15, 2), default=0)

    # Status
    status = Column(SQLEnum(StatusDocumentoFiscal), default=StatusDocumentoFiscal.AUTORIZADO)
    protocolo_autorizacao = Column(String(50))
    motivo_cancelamento = Column(Text)

    # XML
    xml_original = Column(LargeBinary)
    xml_cancelamento = Column(LargeBinary)
    xml_carta_correcao = Column(LargeBinary)

    # Dados extras (JSON)
    itens = Column(JSONB)
    transportadora = Column(JSONB)
    pagamentos = Column(JSONB)
    informacoes_adicionais = Column(Text)
    dados_adicionais = Column(JSONB)

    # Campos adicionais para NFS-e
    tipo_documento = Column(SQLEnum(TipoDocumentoFiscal))
    nome_emitente = Column(String(200))
    nome_destinatario = Column(String(200))
    cnpj_emitente = Column(String(14), index=True)
    cnpj_destinatario = Column(String(14))
    direcao = Column(String(20))  # emitido, tomado, emitida, tomada
    codigo_servico = Column(String(20))
    xml_documento = Column(LargeBinary)

    # Sincronizacao
    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))
    data_sincronizacao = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_doc_fiscal_cnpj_data", "cnpj_empresa", "data_emissao"),
        Index("ix_doc_fiscal_tipo_status", "tipo", "status"),
    )


class EventoDocumentoFiscal(Base, BaseModel):
    """Eventos de documentos fiscais (carta correcao, cancelamento, etc)."""

    __tablename__ = "gov_eventos_documentos_fiscais"

    documento_id = Column(UUID(as_uuid=True), ForeignKey("gov_documentos_fiscais.id"), nullable=False)
    tipo_evento = Column(String(50), nullable=False)  # carta_correcao, cancelamento, etc
    sequencia = Column(Integer, default=1)
    data_evento = Column(DateTime, nullable=False)
    protocolo = Column(String(50))
    descricao = Column(Text)
    xml_evento = Column(LargeBinary)
    dados_adicionais = Column(JSONB)

    documento = relationship("DocumentoFiscal", backref="eventos")


# =============================================================================
# eSocial
# =============================================================================


class EventoESocial(Base, BaseModel):
    """Evento eSocial enviado/recebido."""

    __tablename__ = "gov_eventos_esocial"

    # Identificacao
    cnpj_empresa = Column(String(14), nullable=False, index=True)
    tipo_evento = Column(SQLEnum(TipoEventoESocial), nullable=False, index=True)
    id_evento = Column(String(50), unique=True, index=True)

    # Funcionario (quando aplicavel)
    cpf_funcionario = Column(String(11), index=True)
    matricula = Column(String(30))
    nome_funcionario = Column(String(200))

    # Periodo
    periodo_apuracao = Column(String(7))  # YYYY-MM
    data_evento = Column(Date, nullable=False)

    # Transmissao
    status = Column(SQLEnum(StatusEventoESocial), default=StatusEventoESocial.PENDENTE)
    protocolo_envio = Column(String(50))
    recibo = Column(String(50))
    data_envio = Column(DateTime)
    data_processamento = Column(DateTime)

    # Conteudo
    dados_evento = Column(JSONB, nullable=False)
    xml_envio = Column(LargeBinary)
    xml_retorno = Column(LargeBinary)

    # Erros
    codigo_erro = Column(String(10))
    mensagem_erro = Column(Text)

    # Retificacao
    evento_retificado_id = Column(UUID(as_uuid=True), ForeignKey("gov_eventos_esocial.id"))

    # Sincronizacao
    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (
        Index("ix_esocial_cnpj_periodo", "cnpj_empresa", "periodo_apuracao"),
        Index("ix_esocial_cpf_tipo", "cpf_funcionario", "tipo_evento"),
    )


# =============================================================================
# GUIAS DE RECOLHIMENTO
# =============================================================================


class GuiaRecolhimento(Base, BaseModel):
    """Guias de recolhimento (FGTS, INSS, DARF, DAS, etc)."""

    __tablename__ = "gov_guias_recolhimento"

    # Identificacao
    cnpj_empresa = Column(String(14), nullable=False, index=True)
    tipo_guia = Column(SQLEnum(TipoGuia), nullable=False, index=True)
    codigo_receita = Column(String(10))
    numero_guia = Column(String(50), index=True)

    # Periodo
    competencia = Column(String(7), nullable=False)  # YYYY-MM
    data_vencimento = Column(Date, nullable=False, index=True)
    data_pagamento = Column(Date)

    # Valores
    valor_principal = Column(Numeric(15, 2), nullable=False)
    valor_juros = Column(Numeric(15, 2), default=0)
    valor_multa = Column(Numeric(15, 2), default=0)
    valor_total = Column(Numeric(15, 2), nullable=False)

    # Status
    status = Column(SQLEnum(StatusGuia), default=StatusGuia.GERADA)

    # Codigo de barras
    linha_digitavel = Column(String(100))
    codigo_barras = Column(String(50))

    # Documento
    pdf_guia = Column(LargeBinary)

    # Dados extras
    dados_extras = Column(JSONB)
    dados_adicionais = Column(JSONB)

    # Sincronizacao
    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (
        Index("ix_guia_cnpj_competencia", "cnpj_empresa", "competencia"),
        Index("ix_guia_vencimento", "data_vencimento", "status"),
    )


# =============================================================================
# CERTIDOES
# =============================================================================


class Certidao(Base, BaseModel):
    """Certidoes obtidas (CND, CNDT, etc)."""

    __tablename__ = "gov_certidoes"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    tipo_certidao = Column(String(50), nullable=False)  # cnd_federal, cndt, crf_fgts, etc
    orgao_emissor = Column(String(100))

    # Validade
    data_emissao = Column(DateTime, nullable=False)
    data_validade = Column(Date, nullable=False, index=True)

    # Status
    situacao = Column(String(50))  # regular, irregular, positiva_com_efeito_negativa
    codigo_controle = Column(String(100))

    # Documento
    pdf_certidao = Column(LargeBinary)

    # Sincronizacao
    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (Index("ix_certidao_validade", "cnpj_empresa", "data_validade"),)


# =============================================================================
# DADOS CADASTRAIS
# =============================================================================


class DadosCadastraisEmpresa(Base, BaseModel):
    """Dados cadastrais da empresa na Receita Federal."""

    __tablename__ = "gov_dados_cadastrais_empresa"

    cnpj = Column(String(14), unique=True, nullable=False, index=True)

    # Dados basicos
    razao_social = Column(String(200), nullable=False)
    nome_fantasia = Column(String(200))
    situacao_cadastral = Column(String(50))
    data_situacao_cadastral = Column(Date)
    motivo_situacao = Column(String(100))

    # Natureza juridica
    codigo_natureza_juridica = Column(String(10))
    natureza_juridica = Column(String(200))

    # Atividades
    cnae_principal = Column(String(10))
    cnae_principal_descricao = Column(String(200))
    cnaes_secundarios = Column(JSONB)

    # Endereco
    logradouro = Column(String(200))
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cep = Column(String(8))
    municipio = Column(String(100))
    uf = Column(String(2))

    # Contato
    telefone = Column(String(20))
    email = Column(String(200))

    # Capital
    capital_social = Column(Numeric(15, 2))
    porte = Column(String(50))

    # Simples Nacional
    optante_simples = Column(Boolean)
    data_opcao_simples = Column(Date)
    data_exclusao_simples = Column(Date)
    optante_mei = Column(Boolean)

    # Socios
    quadro_societario = Column(JSONB)

    # Datas
    data_abertura = Column(Date)
    data_ultima_atualizacao = Column(DateTime)

    # Sincronizacao
    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))


class DadosCadastraisPessoa(Base, BaseModel):
    """Dados cadastrais de pessoa fisica."""

    __tablename__ = "gov_dados_cadastrais_pessoa"

    cpf = Column(String(11), unique=True, nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    data_nascimento = Column(Date)
    situacao_cadastral = Column(String(50))

    # Sincronizacao
    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))


# =============================================================================
# SIMPLES NACIONAL
# =============================================================================


class ApuracaoSimplesNacional(Base, BaseModel):
    """Apuracoes do Simples Nacional (PGDAS-D)."""

    __tablename__ = "gov_apuracoes_simples"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    competencia = Column(String(7), nullable=False)  # YYYY-MM

    # Valores
    receita_bruta_mes = Column(Numeric(15, 2))
    receita_bruta_12_meses = Column(Numeric(15, 2))
    valor_devido = Column(Numeric(15, 2))

    # Detalhamento por anexo
    anexo = Column(String(10))
    aliquota_efetiva = Column(Numeric(5, 4))
    detalhamento_tributos = Column(JSONB)

    # DAS
    numero_das = Column(String(50))
    data_vencimento_das = Column(Date)
    valor_das = Column(Numeric(15, 2))
    status_das = Column(String(20))

    # Sincronizacao
    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (UniqueConstraint("cnpj_empresa", "competencia", name="uq_apuracao_simples"),)


# =============================================================================
# SPED
# =============================================================================


class ArquivoSPED(Base, BaseModel):
    """Arquivos SPED enviados/recebidos."""

    __tablename__ = "gov_arquivos_sped"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    tipo_sped = Column(String(20), nullable=False)  # fiscal, contabil, contribuicoes

    # Periodo
    ano = Column(Integer, nullable=False)
    mes_inicial = Column(Integer)
    mes_final = Column(Integer)

    # Arquivo
    nome_arquivo = Column(String(200))
    hash_arquivo = Column(String(64))
    arquivo_txt = Column(LargeBinary)

    # Transmissao
    data_geracao = Column(DateTime)
    data_transmissao = Column(DateTime)
    protocolo = Column(String(50))
    recibo = Column(String(100))
    status = Column(String(20))

    # Sincronizacao
    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (Index("ix_sped_cnpj_ano", "cnpj_empresa", "ano"),)


# =============================================================================
# LOGS DE SINCRONIZACAO
# =============================================================================


class SyncLog(Base, BaseModel):
    """Log de sincronizacao com portais governamentais."""

    __tablename__ = "gov_sync_logs"

    # Identificacao
    cnpj_empresa = Column(String(14), nullable=False, index=True)
    servico = Column(String(50), nullable=False, index=True)  # esocial, sefaz, ecac, etc
    tipo_sync = Column(SQLEnum(TipoSincronizacao), nullable=False)

    # Execucao
    inicio_execucao = Column(DateTime, nullable=False, default=datetime.utcnow)
    fim_execucao = Column(DateTime)
    duracao_segundos = Column(Integer)

    # Status
    status = Column(SQLEnum(StatusSincronizacao), default=StatusSincronizacao.EXECUTANDO)

    # Resultados
    registros_processados = Column(Integer, default=0)
    registros_novos = Column(Integer, default=0)
    registros_atualizados = Column(Integer, default=0)
    registros_erro = Column(Integer, default=0)

    # Parametros
    data_inicial = Column(Date)
    data_final = Column(Date)
    parametros = Column(JSONB)

    # Erros
    mensagem_erro = Column(Text)
    detalhes_erro = Column(JSONB)

    # Marcador para sincronizacao incremental
    ultimo_id_processado = Column(String(100))
    ultima_data_processada = Column(DateTime)

    __table_args__ = (
        Index("ix_sync_log_cnpj_servico", "cnpj_empresa", "servico"),
        Index("ix_sync_log_status", "status", "inicio_execucao"),
    )


class SyncAgendamento(Base, BaseModel):
    """Agendamentos de sincronizacao."""

    __tablename__ = "gov_sync_agendamentos"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    servico = Column(String(50), nullable=False)

    # Agendamento
    ativo = Column(Boolean, default=True)
    intervalo_minutos = Column(Integer, default=60)
    horario_preferencial = Column(String(5))  # HH:MM
    dias_semana = Column(JSONB)  # [0,1,2,3,4,5,6]

    # Ultima execucao
    ultima_execucao = Column(DateTime)
    proxima_execucao = Column(DateTime)

    # Configuracoes
    tipo_sync = Column(SQLEnum(TipoSincronizacao), default=TipoSincronizacao.INCREMENTAL)
    dias_retroativos = Column(Integer, default=30)

    __table_args__ = (UniqueConstraint("cnpj_empresa", "servico", name="uq_sync_agendamento"),)


# =============================================================================
# CONFIGURACOES
# =============================================================================


class ConfiguracaoIntegracao(Base, BaseModel):
    """Configuracoes de integracao por empresa."""

    __tablename__ = "gov_configuracoes_integracao"

    cnpj_empresa = Column(String(14), unique=True, nullable=False, index=True)

    # Certificado
    certificado_id = Column(String(100))
    certificado_validade = Column(Date)

    # Gov.br
    govbr_access_token = Column(Text)  # Criptografado
    govbr_refresh_token = Column(Text)  # Criptografado
    govbr_token_expira = Column(DateTime)

    # SEFAZ
    uf_principal = Column(String(2))
    ambiente_nfe = Column(String(20), default="producao")

    # eSocial
    ambiente_esocial = Column(String(20), default="producao")

    # Configuracoes gerais
    notificar_erros = Column(Boolean, default=True)
    email_notificacao = Column(String(200))

    # Servicos habilitados
    servicos_habilitados = Column(JSONB, default=list)


# =============================================================================
# FGTS DIGITAL
# =============================================================================


class ExtratoFGTS(Base, BaseModel):
    """Extrato de conta vinculada FGTS."""

    __tablename__ = "gov_extratos_fgts"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    cpf_funcionario = Column(String(11), nullable=False, index=True)
    nome_funcionario = Column(String(200))
    pis = Column(String(11))
    numero_conta = Column(String(30))
    data_abertura = Column(Date)

    # Saldos
    saldo_anterior = Column(Numeric(15, 2), default=0)
    depositos = Column(Numeric(15, 2), default=0)
    saques = Column(Numeric(15, 2), default=0)
    juros_jam = Column(Numeric(15, 2), default=0)
    saldo_atual = Column(Numeric(15, 2), default=0)

    # Movimentacoes detalhadas
    movimentacoes = Column(JSONB)

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (Index("ix_extrato_fgts_cnpj_cpf", "cnpj_empresa", "cpf_funcionario"),)


class DebitoFGTS(Base, BaseModel):
    """Debitos pendentes de FGTS."""

    __tablename__ = "gov_debitos_fgts"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    numero_debito = Column(String(50), index=True)
    competencia = Column(String(7))
    origem = Column(String(100))

    valor_original = Column(Numeric(15, 2), nullable=False)
    valor_atualizado = Column(Numeric(15, 2))
    data_vencimento = Column(Date)
    situacao = Column(String(50))
    parcelado = Column(Boolean, default=False)
    numero_parcelamento = Column(String(50))

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))


class MovimentacaoFGTS(Base, BaseModel):
    """Movimentacoes de funcionarios no FGTS."""

    __tablename__ = "gov_movimentacoes_fgts"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    cpf_funcionario = Column(String(11), nullable=False, index=True)
    nome_funcionario = Column(String(200))
    tipo_movimentacao = Column(String(50))
    codigo_movimentacao = Column(String(10))
    descricao = Column(String(200))
    data_movimentacao = Column(Date)

    valor_base = Column(Numeric(15, 2), default=0)
    valor_deposito = Column(Numeric(15, 2), default=0)
    processado = Column(Boolean, default=False)

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))


# =============================================================================
# EFD-REINF
# =============================================================================


class EventoReinf(Base, BaseModel):
    """Eventos EFD-Reinf enviados."""

    __tablename__ = "gov_eventos_reinf"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    id_evento = Column(String(50), unique=True, index=True)
    tipo_evento = Column(String(20), nullable=False, index=True)
    descricao_evento = Column(String(200))
    periodo_apuracao = Column(String(7))  # YYYY-MM

    data_envio = Column(DateTime)
    status = Column(SQLEnum(StatusEventoReinf), default=StatusEventoReinf.PENDENTE)
    protocolo = Column(String(50))
    recibo = Column(String(50))

    dados_evento = Column(JSONB)
    xml_envio = Column(LargeBinary)

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (Index("ix_reinf_cnpj_periodo", "cnpj_empresa", "periodo_apuracao"),)


class TotalizadorReinf(Base, BaseModel):
    """Totalizadores EFD-Reinf (R-9001, R-9005, etc)."""

    __tablename__ = "gov_totalizadores_reinf"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    tipo_evento = Column(String(20), nullable=False)
    periodo_apuracao = Column(String(7), nullable=False)

    # Contribuicao previdenciaria
    base_calculo_cp = Column(Numeric(15, 2), default=0)
    valor_cp_patronal = Column(Numeric(15, 2), default=0)
    valor_cp_descontada = Column(Numeric(15, 2), default=0)
    valor_cprb = Column(Numeric(15, 2), default=0)

    # Retencoes na fonte
    base_calculo_ir = Column(Numeric(15, 2), default=0)
    valor_ir_retido = Column(Numeric(15, 2), default=0)
    valor_csll_retido = Column(Numeric(15, 2), default=0)
    valor_cofins_retido = Column(Numeric(15, 2), default=0)
    valor_pis_retido = Column(Numeric(15, 2), default=0)

    dados_completos = Column(JSONB)

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (UniqueConstraint("cnpj_empresa", "tipo_evento", "periodo_apuracao", name="uq_totalizador_reinf"),)


class RetencaoReinf(Base, BaseModel):
    """Retencoes na fonte EFD-Reinf."""

    __tablename__ = "gov_retencoes_reinf"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    tipo_retencao = Column(String(20))
    cnpj_prestador = Column(String(14), index=True)
    cnpj_tomador = Column(String(14))
    periodo_apuracao = Column(String(7))
    data_pagamento = Column(Date)

    valor_bruto = Column(Numeric(15, 2), default=0)
    base_retencao = Column(Numeric(15, 2), default=0)
    valor_retencao_cp = Column(Numeric(15, 2), default=0)
    valor_retencao_ir = Column(Numeric(15, 2), default=0)
    valor_retencao_csll = Column(Numeric(15, 2), default=0)
    valor_retencao_cofins = Column(Numeric(15, 2), default=0)
    valor_retencao_pis = Column(Numeric(15, 2), default=0)

    numero_nf = Column(String(20))
    serie_nf = Column(String(5))

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))


# =============================================================================
# DCTFWeb
# =============================================================================


class DeclaracaoDCTFWeb(Base, BaseModel):
    """Declaracoes DCTFWeb transmitidas."""

    __tablename__ = "gov_declaracoes_dctfweb"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    numero_recibo = Column(String(50), unique=True, index=True)
    tipo_declaracao = Column(String(10))
    descricao_tipo = Column(String(50))
    periodo_apuracao = Column(String(7), nullable=False)

    data_transmissao = Column(DateTime)
    situacao = Column(String(50))
    retificadora = Column(Boolean, default=False)
    numero_recibo_retificada = Column(String(50))

    valor_total_debitos = Column(Numeric(15, 2), default=0)
    valor_total_creditos = Column(Numeric(15, 2), default=0)
    valor_total_pagar = Column(Numeric(15, 2), default=0)

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (Index("ix_dctfweb_cnpj_periodo", "cnpj_empresa", "periodo_apuracao"),)


class DebitoDCTFWeb(Base, BaseModel):
    """Debitos apurados na DCTFWeb."""

    __tablename__ = "gov_debitos_dctfweb"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    periodo_apuracao = Column(String(7), nullable=False)
    codigo_receita = Column(String(10), nullable=False)
    descricao_receita = Column(String(200))

    valor_principal = Column(Numeric(15, 2), default=0)
    valor_multa = Column(Numeric(15, 2), default=0)
    valor_juros = Column(Numeric(15, 2), default=0)
    valor_total = Column(Numeric(15, 2), default=0)

    data_vencimento = Column(Date)
    situacao = Column(String(50))
    suspenso = Column(Boolean, default=False)
    processo_suspensao = Column(String(50))

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (Index("ix_debito_dctfweb_periodo", "cnpj_empresa", "periodo_apuracao"),)


class CreditoDCTFWeb(Base, BaseModel):
    """Creditos vinculados na DCTFWeb."""

    __tablename__ = "gov_creditos_dctfweb"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    tipo_credito = Column(String(50))
    origem = Column(String(100))
    periodo_apuracao = Column(String(7))

    valor_original = Column(Numeric(15, 2), default=0)
    valor_utilizado = Column(Numeric(15, 2), default=0)
    valor_disponivel = Column(Numeric(15, 2), default=0)

    data_vinculacao = Column(Date)
    debito_vinculado = Column(String(100))

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))


# =============================================================================
# SPED FISCAL E CONTABIL
# =============================================================================


class EscrituracaoSPED(Base, BaseModel):
    """Escrituracoes SPED Fiscal e Contabil."""

    __tablename__ = "gov_escrituracoes_sped"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    tipo_sped = Column(String(10), nullable=False)  # EFD, ECD
    numero_recibo = Column(String(50), unique=True, index=True)

    ano_calendario = Column(Integer)
    periodo_apuracao = Column(String(7))
    data_inicial = Column(Date)
    data_final = Column(Date)

    # EFD Fiscal
    perfil = Column(String(5))
    descricao_perfil = Column(String(100))
    finalidade = Column(String(50))

    # ECD Contabil
    tipo_livro = Column(String(5))
    descricao_livro = Column(String(100))

    data_transmissao = Column(DateTime)
    situacao = Column(String(50))
    hash_arquivo = Column(String(64))
    retificadora = Column(Boolean, default=False)
    recibo_substituido = Column(String(50))
    recibo_retificado = Column(String(50))

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (Index("ix_escrituracao_sped_cnpj", "cnpj_empresa", "tipo_sped"),)


class ContaContabil(Base, BaseModel):
    """Plano de contas SPED Contabil."""

    __tablename__ = "gov_contas_contabeis"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    codigo_conta = Column(String(50), nullable=False)
    descricao = Column(String(200))
    tipo_conta = Column(String(20))
    natureza = Column(String(20))
    nivel = Column(Integer)
    codigo_superior = Column(String(50))
    codigo_referencial = Column(String(50))
    ano_referencia = Column(Integer)

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (Index("ix_conta_contabil_cnpj", "cnpj_empresa", "codigo_conta"),)


class SaldoContabil(Base, BaseModel):
    """Saldos contabeis por periodo."""

    __tablename__ = "gov_saldos_contabeis"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    codigo_conta = Column(String(50), nullable=False)
    periodo = Column(String(7), nullable=False)  # YYYY-MM

    saldo_inicial_debito = Column(Numeric(15, 2), default=0)
    saldo_inicial_credito = Column(Numeric(15, 2), default=0)
    movimento_debito = Column(Numeric(15, 2), default=0)
    movimento_credito = Column(Numeric(15, 2), default=0)
    saldo_final_debito = Column(Numeric(15, 2), default=0)
    saldo_final_credito = Column(Numeric(15, 2), default=0)

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (UniqueConstraint("cnpj_empresa", "codigo_conta", "periodo", name="uq_saldo_contabil"),)


class ApuracaoICMS(Base, BaseModel):
    """Apuracao ICMS do SPED Fiscal."""

    __tablename__ = "gov_apuracoes_icms"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    periodo_apuracao = Column(String(7), nullable=False)

    valor_total_debitos = Column(Numeric(15, 2), default=0)
    valor_ajustes_debitos = Column(Numeric(15, 2), default=0)
    valor_total_creditos = Column(Numeric(15, 2), default=0)
    valor_ajustes_creditos = Column(Numeric(15, 2), default=0)
    saldo_credor_anterior = Column(Numeric(15, 2), default=0)
    valor_total_deducoes = Column(Numeric(15, 2), default=0)
    icms_recolher = Column(Numeric(15, 2), default=0)
    saldo_credor_transportar = Column(Numeric(15, 2), default=0)
    icms_st_recolher = Column(Numeric(15, 2), default=0)
    difal_recolher = Column(Numeric(15, 2), default=0)
    fcp_recolher = Column(Numeric(15, 2), default=0)

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (UniqueConstraint("cnpj_empresa", "periodo_apuracao", name="uq_apuracao_icms"),)


class ApuracaoIPI(Base, BaseModel):
    """Apuracao IPI do SPED Fiscal."""

    __tablename__ = "gov_apuracoes_ipi"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    periodo_apuracao = Column(String(7), nullable=False)

    valor_total_debitos = Column(Numeric(15, 2), default=0)
    valor_total_creditos = Column(Numeric(15, 2), default=0)
    saldo_credor_anterior = Column(Numeric(15, 2), default=0)
    ipi_recolher = Column(Numeric(15, 2), default=0)
    saldo_credor_transportar = Column(Numeric(15, 2), default=0)

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))

    __table_args__ = (UniqueConstraint("cnpj_empresa", "periodo_apuracao", name="uq_apuracao_ipi"),)


# =============================================================================
# NFS-E NACIONAL
# =============================================================================


class DPSPendente(Base, BaseModel):
    """DPS (Declaracao Prestacao Servicos) pendentes."""

    __tablename__ = "gov_dps_pendentes"

    cnpj_empresa = Column(String(14), nullable=False, index=True)
    id_dps = Column(String(50), unique=True, index=True)
    data_emissao = Column(Date)
    competencia = Column(String(7))

    valor_servicos = Column(Numeric(15, 2), default=0)
    situacao = Column(String(50))
    motivo_pendencia = Column(Text)
    xml_dps = Column(LargeBinary)

    sync_id = Column(UUID(as_uuid=True), ForeignKey("gov_sync_logs.id"))


# =============================================================================
# FUNCOES AUXILIARES
# =============================================================================


def criar_todas_tabelas(engine):
    """Cria todas as tabelas no banco de dados."""
    Base.metadata.create_all(engine)


def dropar_todas_tabelas(engine):
    """Remove todas as tabelas do banco de dados."""
    Base.metadata.drop_all(engine)
