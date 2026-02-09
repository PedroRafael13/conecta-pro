-- Script para criar índices GIN nas colunas JSONB prioritárias
-- Executar este script no PostgreSQL

-- Verificar quais colunas existem antes de criar índices
DO $$
DECLARE
    rec RECORD;
BEGIN
    -- Lista de tabelas.colunas para criar índices GIN
    FOR rec IN
        SELECT * FROM (VALUES
            ('audit_logs', 'details'),
            ('audit_logs', 'changes'),
            ('access_history', 'context'),
            ('integration_logs', 'request_data'),
            ('integration_logs', 'response_data'),
            ('report_templates', 'config'),
            ('workflows', 'config'),
            ('integration_sync_queue', 'payload'),
            ('ai_predictions', 'input_data'),
            ('employees', 'dados_adicionais')
        ) AS t(table_name, column_name)
    LOOP
        -- Verificar se tabela e coluna existem
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = rec.table_name
            AND column_name = rec.column_name
        ) THEN
            -- Criar índice GIN se não existir
            EXECUTE format(
                'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_%s_%s_gin ON %s USING GIN (%s)',
                rec.table_name, rec.column_name, rec.table_name, rec.column_name
            );
            RAISE NOTICE 'Índice criado: idx_%_%_gin', rec.table_name, rec.column_name;
        ELSE
            RAISE NOTICE 'Coluna %.% não existe, pulando...', rec.table_name, rec.column_name;
        END IF;
    END LOOP;
END $$;

-- Verificar índices criados
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE indexname LIKE '%gin%'
ORDER BY tablename;
