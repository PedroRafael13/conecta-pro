-- DEPRECATED: Guardian integration — scheduled for extraction to separate microservice.
-- Deprecation date: 2026-03-11
-- Corrigir schema Guardian - Criar tabelas ausentes
-- Executar como: psql -U postgres -d erp_conecta_mais -f fix_guardian_schema.sql

SET search_path TO guardian, public;

-- Criar tabela access_logs se não existir
CREATE TABLE IF NOT EXISTS access_logs (
    id VARCHAR(36) PRIMARY KEY DEFAULT (gen_random_uuid()::text),
    guardian_id VARCHAR(100) NOT NULL,
    client_id VARCHAR(50) NOT NULL,
    log_type VARCHAR(20) NOT NULL,
    post_id VARCHAR(50),
    person_name VARCHAR(255) NOT NULL,
    person_document VARCHAR(50) NOT NULL,
    person_type VARCHAR(50),
    unit_code VARCHAR(50),
    access_point VARCHAR(100),
    access_method VARCHAR(50),
    device_id VARCHAR(50),
    is_authorized BOOLEAN DEFAULT true,
    event_timestamp TIMESTAMP NOT NULL,
    photos JSONB,
    additional_data JSONB,
    location VARCHAR(255),
    temperature DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela equipment_status se não existir
CREATE TABLE IF NOT EXISTS equipment_status (
    id VARCHAR(36) PRIMARY KEY DEFAULT (gen_random_uuid()::text),
    equipment_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'online',
    last_ping TIMESTAMP,
    firmware_version VARCHAR(50),
    configuration JSONB,
    alerts JSONB,
    maintenance_schedule JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_access_logs_client_id ON access_logs(client_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_person_document ON access_logs(person_document);
CREATE INDEX IF NOT EXISTS idx_access_logs_event_timestamp ON access_logs(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_access_logs_log_type ON access_logs(log_type);

CREATE INDEX IF NOT EXISTS idx_equipment_status_equipment_id ON equipment_status(equipment_id);
CREATE INDEX IF NOT EXISTS idx_equipment_status_status ON equipment_status(status);
CREATE INDEX IF NOT EXISTS idx_equipment_status_type ON equipment_status(type);

-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
DROP TRIGGER IF EXISTS update_access_logs_updated_at ON access_logs;
CREATE TRIGGER update_access_logs_updated_at
    BEFORE UPDATE ON access_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_equipment_status_updated_at ON equipment_status;
CREATE TRIGGER update_equipment_status_updated_at
    BEFORE UPDATE ON equipment_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Dados iniciais para equipment_status
INSERT INTO equipment_status (equipment_id, name, type, location, status) VALUES
('camera-001', 'Câmera Portaria Principal', 'camera', 'Portaria Principal', 'online'),
('camera-002', 'Câmera Garagem', 'camera', 'Garagem', 'online'),
('control-001', 'Controladora Principal', 'access_control', 'Portaria', 'online'),
('sensor-001', 'Sensor Temperatura', 'sensor', 'Portaria', 'online'),
('intercom-001', 'Interfone Principal', 'intercom', 'Portaria Principal', 'online')
ON CONFLICT (equipment_id) DO NOTHING;

\echo 'Schema Guardian corrigido com sucesso!'
\echo 'Tabelas criadas: access_logs, equipment_status'
\echo 'Índices e triggers configurados'
\echo 'Dados iniciais inseridos'
