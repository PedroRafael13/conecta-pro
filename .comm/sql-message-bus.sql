-- Message Bus via PostgreSQL
-- Kimi e Opus podem ler/escrever mensagens

CREATE TABLE IF NOT EXISTS ia_communication (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_agent VARCHAR(50) NOT NULL CHECK (from_agent IN ('kimi', 'opus')),
    to_agent VARCHAR(50) NOT NULL CHECK (to_agent IN ('kimi', 'opus', 'broadcast')),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    type VARCHAR(50) CHECK (type IN ('request', 'response', 'notification', 'handoff', 'heartbeat')),
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'critical')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    subject TEXT NOT NULL,
    payload JSONB,
    files TEXT[],
    in_reply_to UUID REFERENCES ia_communication(id),
    processed_at TIMESTAMPTZ,
    result JSONB
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_comm_to_status ON ia_communication(to_agent, status);
CREATE INDEX IF NOT EXISTS idx_comm_timestamp ON ia_communication(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_comm_type ON ia_communication(type);

-- View para mensagens pendentes do Kimi
CREATE OR REPLACE VIEW kimi_inbox AS
SELECT * FROM ia_communication
WHERE to_agent IN ('kimi', 'broadcast')
  AND status = 'pending'
ORDER BY priority DESC, timestamp ASC;

-- View para mensagens pendentes do Opus
CREATE OR REPLACE VIEW opus_inbox AS
SELECT * FROM ia_communication
WHERE to_agent IN ('opus', 'broadcast')
  AND status = 'pending'
ORDER BY priority DESC, timestamp ASC;

-- Exemplo de uso:
-- Opus envia mensagem:
-- INSERT INTO ia_communication (from_agent, to_agent, type, subject, payload)
-- VALUES ('opus', 'kimi', 'request', 'Analisar módulo X', '{"module": "financial", "action": "audit"}');

-- Kimi lê mensagens:
-- SELECT * FROM kimi_inbox;

-- Kimi marca como processada:
-- UPDATE ia_communication SET status = 'completed', processed_at = NOW() WHERE id = '...';
