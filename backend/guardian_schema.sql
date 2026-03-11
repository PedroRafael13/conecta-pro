-- DEPRECATED: Guardian integration — scheduled for extraction to separate microservice.
-- Deprecation date: 2026-03-11
-- ===============================================================================
-- GUARDIAN UNIFIED v3.0.0 - DATABASE INSTALLATION SCRIPT
-- ===============================================================================
-- Sistema Guardian Unificado: Física + Cibernética + CAMPO + ERP
-- Módulo 9 - ERP Conecta Mais
-- Database: PostgreSQL
-- ===============================================================================

-- Criar schema para Guardian se não existir
CREATE SCHEMA IF NOT EXISTS guardian;

-- ===============================================================================
-- TABELAS EXISTENTES (Portaria Remota) - Verificar e atualizar
-- ===============================================================================

-- Moradores (já existe da portaria remota)
CREATE TABLE IF NOT EXISTS guardian.portaria_moradores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    apartamento VARCHAR(50) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(255),
    documento VARCHAR(50),
    status VARCHAR(20) DEFAULT 'ativo',
    foto_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sync table (continuidade do remote_gatehouse)
CREATE TABLE IF NOT EXISTS guardian.guardian_syncs (
    id SERIAL PRIMARY KEY,
    sync_code VARCHAR(100) UNIQUE NOT NULL,
    direction VARCHAR(20) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100),
    external_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    client_id VARCHAR(50),
    contract_id VARCHAR(50),
    post_id VARCHAR(50),
    payload JSONB,
    response JSONB,
    error_message TEXT,
    error_details JSONB,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    last_retry_at TIMESTAMP,
    next_retry_at TIMESTAMP,
    synced_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    metadata_extra JSONB
);

-- Visitantes (já existe da portaria remota)
CREATE TABLE IF NOT EXISTS guardian.portaria_visitantes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    documento VARCHAR(50) NOT NULL,
    telefone VARCHAR(20),
    morador_id INTEGER REFERENCES guardian.portaria_moradores(id),
    motivo_visita TEXT,
    hora_entrada TIMESTAMP,
    hora_saida TIMESTAMP,
    autorizado_por VARCHAR(255),
    observacoes TEXT,
    foto_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'aguardando',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================================================
-- NOVAS TABELAS (Segurança Cibernética)
-- ===============================================================================

-- Auditorias de Segurança
CREATE TABLE IF NOT EXISTS guardian.security_audits (
    id SERIAL PRIMARY KEY,
    audit_id VARCHAR(100) UNIQUE NOT NULL,
    target_host VARCHAR(255) NOT NULL,
    audit_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running',
    vulnerabilities_found INTEGER DEFAULT 0,
    severity_breakdown JSONB,
    scan_results JSONB,
    recommendations TEXT,
    auditor VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permissões
GRANT USAGE ON SCHEMA guardian TO conecta_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA guardian TO conecta_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA guardian TO conecta_user;

-- Dados iniciais
INSERT INTO guardian.guardian_syncs (sync_code, direction, entity_type, status) VALUES
('GUARDIAN_INIT', 'outbound', 'system', 'completed') ON CONFLICT DO NOTHING;
