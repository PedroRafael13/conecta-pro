-- =============================================================================
-- Migration: 001_initial_schema
-- Descrição: Schema inicial para módulo de integrações governamentais
-- Data: 2026-01-16
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Extensões necessárias
-- -----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -----------------------------------------------------------------------------
-- Enum Types
-- -----------------------------------------------------------------------------

-- Status de documentos fiscais
CREATE TYPE status_documento AS ENUM (
    'rascunho',
    'validado',
    'enviado',
    'autorizado',
    'rejeitado',
    'cancelado',
    'inutilizado',
    'denegado'
);

-- Tipos de documento fiscal
CREATE TYPE tipo_documento_fiscal AS ENUM (
    'nfe',
    'nfce',
    'cte',
    'cte_os',
    'mdfe',
    'nfse'
);

-- Status de eventos eSocial
CREATE TYPE status_esocial AS ENUM (
    'pendente',
    'enviado',
    'processado',
    'rejeitado',
    'retificado'
);

-- Status de sincronização
CREATE TYPE status_sync AS ENUM (
    'pendente',
    'em_andamento',
    'concluido',
    'falha',
    'parcial'
);

-- Status de reprocessamento
CREATE TYPE status_reprocessamento AS ENUM (
    'pendente',
    'em_andamento',
    'concluido',
    'falha',
    'cancelado'
);

-- -----------------------------------------------------------------------------
-- Tabela: documentos_fiscais
-- Armazena documentos fiscais (NF-e, CT-e, MDF-e, NFS-e)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documentos_fiscais (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    tipo tipo_documento_fiscal NOT NULL,

    -- Identificação
    chave_acesso VARCHAR(44) UNIQUE,
    numero INTEGER NOT NULL,
    serie VARCHAR(3) NOT NULL,

    -- Emitente
    emitente_cnpj VARCHAR(14) NOT NULL,
    emitente_nome VARCHAR(200),
    emitente_uf VARCHAR(2),

    -- Destinatário
    destinatario_cnpj_cpf VARCHAR(14),
    destinatario_nome VARCHAR(200),
    destinatario_uf VARCHAR(2),

    -- Valores
    valor_produtos DECIMAL(15,2) DEFAULT 0,
    valor_servicos DECIMAL(15,2) DEFAULT 0,
    valor_frete DECIMAL(15,2) DEFAULT 0,
    valor_seguro DECIMAL(15,2) DEFAULT 0,
    valor_desconto DECIMAL(15,2) DEFAULT 0,
    valor_outras DECIMAL(15,2) DEFAULT 0,
    valor_total DECIMAL(15,2) DEFAULT 0,

    -- Impostos
    valor_icms DECIMAL(15,2) DEFAULT 0,
    valor_icms_st DECIMAL(15,2) DEFAULT 0,
    valor_ipi DECIMAL(15,2) DEFAULT 0,
    valor_pis DECIMAL(15,2) DEFAULT 0,
    valor_cofins DECIMAL(15,2) DEFAULT 0,
    valor_iss DECIMAL(15,2) DEFAULT 0,

    -- Status
    status status_documento DEFAULT 'rascunho',
    ambiente VARCHAR(1) DEFAULT '1', -- 1=Produção, 2=Homologação

    -- SEFAZ
    protocolo_autorizacao VARCHAR(50),
    data_autorizacao TIMESTAMP,
    motivo_rejeicao TEXT,
    codigo_status_sefaz VARCHAR(10),

    -- XMLs (armazenados comprimidos ou em storage externo)
    xml_envio TEXT,
    xml_retorno TEXT,
    xml_proc TEXT,

    -- Eventos (cancelamento, carta correção)
    eventos JSONB DEFAULT '[]'::jsonb,

    -- Contingência
    em_contingencia BOOLEAN DEFAULT FALSE,
    tipo_contingencia VARCHAR(20),
    justificativa_contingencia TEXT,

    -- Metadados
    versao INTEGER DEFAULT 1,
    dados_adicionais JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    data_emissao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Índices compostos
    UNIQUE(tenant_id, tipo, numero, serie, emitente_cnpj)
);

-- Índices para documentos_fiscais
CREATE INDEX idx_docs_tenant_tipo ON documentos_fiscais(tenant_id, tipo);
CREATE INDEX idx_docs_chave ON documentos_fiscais(chave_acesso);
CREATE INDEX idx_docs_emitente ON documentos_fiscais(emitente_cnpj);
CREATE INDEX idx_docs_destinatario ON documentos_fiscais(destinatario_cnpj_cpf);
CREATE INDEX idx_docs_status ON documentos_fiscais(status);
CREATE INDEX idx_docs_data_emissao ON documentos_fiscais(data_emissao);

-- -----------------------------------------------------------------------------
-- Tabela: documentos_historico
-- Histórico de versões de documentos (versionamento)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documentos_historico (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    documento_id UUID NOT NULL REFERENCES documentos_fiscais(id) ON DELETE CASCADE,
    tipo_documento VARCHAR(20) NOT NULL,
    versao INTEGER NOT NULL,
    dados_anteriores JSONB NOT NULL,
    motivo_alteracao VARCHAR(50) NOT NULL,
    usuario_id UUID,
    observacao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(documento_id, versao)
);

CREATE INDEX idx_doc_hist_documento ON documentos_historico(documento_id);
CREATE INDEX idx_doc_hist_versao ON documentos_historico(documento_id, versao DESC);

-- -----------------------------------------------------------------------------
-- Tabela: fila_reprocessamento
-- Fila de documentos para reprocessamento
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fila_reprocessamento (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    documento_id UUID,
    tipo_documento VARCHAR(20) NOT NULL,
    operacao VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    status status_reprocessamento DEFAULT 'pendente',
    prioridade INTEGER DEFAULT 5,
    tentativas INTEGER DEFAULT 0,
    max_tentativas INTEGER DEFAULT 5,
    ultimo_erro TEXT,
    proxima_tentativa TIMESTAMP,
    processado_em TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fila_status ON fila_reprocessamento(status, proxima_tentativa);
CREATE INDEX idx_fila_tenant ON fila_reprocessamento(tenant_id, status);

-- -----------------------------------------------------------------------------
-- Tabela: eventos_esocial
-- Eventos do eSocial
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS eventos_esocial (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    funcionario_id UUID,

    -- Identificação do evento
    tipo_evento VARCHAR(10) NOT NULL, -- S-1000, S-2200, etc
    id_evento VARCHAR(50) UNIQUE NOT NULL,
    numero_recibo VARCHAR(50),

    -- Período
    competencia VARCHAR(7), -- AAAA-MM
    periodo_apuracao VARCHAR(7),

    -- Status
    status status_esocial DEFAULT 'pendente',
    ambiente VARCHAR(1) DEFAULT '1',

    -- XMLs
    xml_envio TEXT,
    xml_retorno TEXT,

    -- Erros
    erros JSONB DEFAULT '[]'::jsonb,

    -- Metadados
    dados_evento JSONB NOT NULL,

    -- Timestamps
    data_envio TIMESTAMP,
    data_processamento TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_esocial_tenant ON eventos_esocial(tenant_id);
CREATE INDEX idx_esocial_funcionario ON eventos_esocial(funcionario_id);
CREATE INDEX idx_esocial_tipo ON eventos_esocial(tipo_evento);
CREATE INDEX idx_esocial_competencia ON eventos_esocial(competencia);
CREATE INDEX idx_esocial_status ON eventos_esocial(status);

-- -----------------------------------------------------------------------------
-- Tabela: guias_fgts
-- Guias do FGTS Digital
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS guias_fgts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,

    -- Identificação
    competencia VARCHAR(7) NOT NULL, -- AAAA-MM
    tipo_guia VARCHAR(20) NOT NULL, -- mensal, rescisorio, parcelamento

    -- Valores
    valor_principal DECIMAL(15,2) NOT NULL,
    valor_multa DECIMAL(15,2) DEFAULT 0,
    valor_juros DECIMAL(15,2) DEFAULT 0,
    valor_total DECIMAL(15,2) NOT NULL,

    -- Pagamento
    codigo_barras VARCHAR(60),
    linha_digitavel VARCHAR(60),
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,

    -- Status
    status VARCHAR(20) DEFAULT 'gerada',

    -- Dados
    funcionarios_incluidos JSONB DEFAULT '[]'::jsonb,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fgts_tenant ON guias_fgts(tenant_id);
CREATE INDEX idx_fgts_competencia ON guias_fgts(tenant_id, competencia);

-- -----------------------------------------------------------------------------
-- Tabela: sync_status
-- Status de sincronização por serviço
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sync_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    servico VARCHAR(50) NOT NULL, -- sefaz_nfe, esocial, fgts, etc

    -- Status
    status status_sync DEFAULT 'pendente',
    ultimo_sync TIMESTAMP,
    proximo_sync TIMESTAMP,

    -- Estatísticas
    registros_processados INTEGER DEFAULT 0,
    registros_novos INTEGER DEFAULT 0,
    registros_atualizados INTEGER DEFAULT 0,
    registros_erro INTEGER DEFAULT 0,

    -- Cursor para sync incremental
    cursor_sync JSONB DEFAULT '{}'::jsonb,

    -- Erros
    ultimo_erro TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(tenant_id, servico)
);

CREATE INDEX idx_sync_tenant_servico ON sync_status(tenant_id, servico);

-- -----------------------------------------------------------------------------
-- Tabela: audit_log
-- Log de auditoria
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tenant_id UUID,
    usuario_id UUID,

    -- Evento
    tipo VARCHAR(50) NOT NULL,
    recurso VARCHAR(100) NOT NULL,
    recurso_id VARCHAR(100),
    acao TEXT NOT NULL,

    -- Origem
    ip_origem INET,
    user_agent TEXT,

    -- Dados
    dados_antes JSONB,
    dados_depois JSONB,
    metadata JSONB,

    -- Resultado
    sucesso BOOLEAN DEFAULT TRUE,
    erro TEXT,

    -- Rastreabilidade
    request_id VARCHAR(50),
    session_id VARCHAR(50),
    hash_integridade VARCHAR(64),

    -- Particionamento por mês
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Criar partições para os próximos 12 meses
CREATE TABLE audit_log_2026_01 PARTITION OF audit_log
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE audit_log_2026_02 PARTITION OF audit_log
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE TABLE audit_log_2026_03 PARTITION OF audit_log
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
-- ... adicionar mais partições conforme necessário

CREATE INDEX idx_audit_tenant ON audit_log(tenant_id, created_at);
CREATE INDEX idx_audit_tipo ON audit_log(tipo, created_at);
CREATE INDEX idx_audit_recurso ON audit_log(recurso, recurso_id);

-- -----------------------------------------------------------------------------
-- Tabela: consentimentos
-- Consentimentos LGPD
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS consentimentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    titular_id UUID NOT NULL,

    -- Consentimento
    finalidade VARCHAR(100) NOT NULL,
    dados_autorizados JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pendente',

    -- Datas
    data_consentimento TIMESTAMP,
    data_revogacao TIMESTAMP,
    data_expiracao TIMESTAMP,

    -- Evidência
    ip_origem INET,
    evidencia VARCHAR(100), -- Hash ou referência

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_consentimentos_tenant ON consentimentos(tenant_id);
CREATE INDEX idx_consentimentos_titular ON consentimentos(titular_id);
CREATE INDEX idx_consentimentos_finalidade ON consentimentos(tenant_id, finalidade);

-- -----------------------------------------------------------------------------
-- Tabela: solicitacoes_lgpd
-- Solicitações de titulares LGPD
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS solicitacoes_lgpd (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    titular_id UUID NOT NULL,

    -- Solicitação
    tipo VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'aberta',
    descricao TEXT,
    dados_solicitados JSONB,

    -- Resposta
    resposta TEXT,
    dados_resposta JSONB,

    -- Prazos
    prazo TIMESTAMP NOT NULL,
    responsavel_id UUID,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    concluida_em TIMESTAMP
);

CREATE INDEX idx_lgpd_tenant ON solicitacoes_lgpd(tenant_id);
CREATE INDEX idx_lgpd_titular ON solicitacoes_lgpd(titular_id);
CREATE INDEX idx_lgpd_status ON solicitacoes_lgpd(status, prazo);

-- -----------------------------------------------------------------------------
-- Tabela: event_outbox
-- Outbox para garantia de entrega de eventos
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS event_outbox (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID,

    -- Evento
    evento_tipo VARCHAR(100) NOT NULL,
    evento_payload JSONB NOT NULL,

    -- Status
    status VARCHAR(20) DEFAULT 'pendente',
    tentativas INTEGER DEFAULT 0,
    max_tentativas INTEGER DEFAULT 5,
    erro TEXT,

    -- Agendamento
    agendado_para TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processado_em TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_outbox_status ON event_outbox(status, agendado_para);
CREATE INDEX idx_outbox_tenant ON event_outbox(tenant_id);

-- -----------------------------------------------------------------------------
-- Tabela: endpoint_status
-- Status de endpoints governamentais
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS endpoint_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Identificação
    servico VARCHAR(50) NOT NULL,
    uf VARCHAR(2),
    ambiente VARCHAR(1) DEFAULT '1',

    -- Status
    status VARCHAR(20) DEFAULT 'desconhecido',
    disponivel BOOLEAN DEFAULT TRUE,
    usando_contingencia BOOLEAN DEFAULT FALSE,

    -- Métricas
    tempo_resposta_ms DECIMAL(10,2),
    falhas_consecutivas INTEGER DEFAULT 0,

    -- Última verificação
    ultima_verificacao TIMESTAMP,
    ultimo_erro TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(servico, uf, ambiente)
);

CREATE INDEX idx_endpoint_servico ON endpoint_status(servico);
CREATE INDEX idx_endpoint_status ON endpoint_status(status);

-- -----------------------------------------------------------------------------
-- Funções auxiliares
-- -----------------------------------------------------------------------------

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger em todas as tabelas com updated_at
CREATE TRIGGER update_documentos_fiscais_updated_at
    BEFORE UPDATE ON documentos_fiscais
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fila_reprocessamento_updated_at
    BEFORE UPDATE ON fila_reprocessamento
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_eventos_esocial_updated_at
    BEFORE UPDATE ON eventos_esocial
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_guias_fgts_updated_at
    BEFORE UPDATE ON guias_fgts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sync_status_updated_at
    BEFORE UPDATE ON sync_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_consentimentos_updated_at
    BEFORE UPDATE ON consentimentos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_solicitacoes_lgpd_updated_at
    BEFORE UPDATE ON solicitacoes_lgpd
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_endpoint_status_updated_at
    BEFORE UPDATE ON endpoint_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- -----------------------------------------------------------------------------
-- Comentários nas tabelas
-- -----------------------------------------------------------------------------
COMMENT ON TABLE documentos_fiscais IS 'Documentos fiscais eletrônicos (NF-e, CT-e, MDF-e, NFS-e)';
COMMENT ON TABLE documentos_historico IS 'Histórico de versões de documentos fiscais';
COMMENT ON TABLE fila_reprocessamento IS 'Fila de documentos para reprocessamento em caso de falha';
COMMENT ON TABLE eventos_esocial IS 'Eventos do eSocial enviados e processados';
COMMENT ON TABLE guias_fgts IS 'Guias do FGTS Digital';
COMMENT ON TABLE sync_status IS 'Status de sincronização com serviços governamentais';
COMMENT ON TABLE audit_log IS 'Log de auditoria para compliance (particionado por mês)';
COMMENT ON TABLE consentimentos IS 'Registros de consentimento LGPD';
COMMENT ON TABLE solicitacoes_lgpd IS 'Solicitações de titulares conforme LGPD';
COMMENT ON TABLE event_outbox IS 'Outbox pattern para garantia de entrega de eventos';
COMMENT ON TABLE endpoint_status IS 'Status de disponibilidade de endpoints governamentais';
