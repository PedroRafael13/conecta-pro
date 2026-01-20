-- =============================================================================
-- Rollback: 001_initial_schema
-- Descrição: Remove schema do módulo de integrações governamentais
-- ATENÇÃO: Esta operação é destrutiva e remove todos os dados!
-- =============================================================================

-- Remover triggers
DROP TRIGGER IF EXISTS update_documentos_fiscais_updated_at ON documentos_fiscais;
DROP TRIGGER IF EXISTS update_fila_reprocessamento_updated_at ON fila_reprocessamento;
DROP TRIGGER IF EXISTS update_eventos_esocial_updated_at ON eventos_esocial;
DROP TRIGGER IF EXISTS update_guias_fgts_updated_at ON guias_fgts;
DROP TRIGGER IF EXISTS update_sync_status_updated_at ON sync_status;
DROP TRIGGER IF EXISTS update_consentimentos_updated_at ON consentimentos;
DROP TRIGGER IF EXISTS update_solicitacoes_lgpd_updated_at ON solicitacoes_lgpd;
DROP TRIGGER IF EXISTS update_endpoint_status_updated_at ON endpoint_status;

-- Remover função
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Remover tabelas (ordem inversa de dependência)
DROP TABLE IF EXISTS endpoint_status CASCADE;
DROP TABLE IF EXISTS event_outbox CASCADE;
DROP TABLE IF EXISTS solicitacoes_lgpd CASCADE;
DROP TABLE IF EXISTS consentimentos CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS sync_status CASCADE;
DROP TABLE IF EXISTS guias_fgts CASCADE;
DROP TABLE IF EXISTS eventos_esocial CASCADE;
DROP TABLE IF EXISTS fila_reprocessamento CASCADE;
DROP TABLE IF EXISTS documentos_historico CASCADE;
DROP TABLE IF EXISTS documentos_fiscais CASCADE;

-- Remover tipos enum
DROP TYPE IF EXISTS status_reprocessamento CASCADE;
DROP TYPE IF EXISTS status_sync CASCADE;
DROP TYPE IF EXISTS status_esocial CASCADE;
DROP TYPE IF EXISTS tipo_documento_fiscal CASCADE;
DROP TYPE IF EXISTS status_documento CASCADE;
