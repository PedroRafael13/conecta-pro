-- ==========================================================================
-- ERP Conecta Mais - Database Initialization Script
-- ==========================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS erp;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS ai;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA erp TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA audit TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA ai TO postgres;

-- Set default search path
ALTER DATABASE erp_conecta_mais SET search_path TO erp, public;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'ERP Conecta Mais database initialized successfully';
END $$;
