-- ===============================================================================
-- CONECTA PRO - JSONB NORMALIZATION SCRIPT
-- ===============================================================================
-- Script para normalizar campos JSONB críticos no banco de dados PostgreSQL
--
-- Características:
-- - Idempotente: pode ser executado múltiplas vezes sem problemas
-- - Seguro: utiliza transações para garantir consistência
-- - Eficiente: atualiza apenas registros com dados inconsistentes
--
-- Tabelas afetadas:
-- - employees (dados_adicionais, competencias, certificacoes, perfil_disc, dependentes)
-- - audit_logs (details, old_values, new_values, changed_fields, compliance_frameworks,
--               triggered_alerts, metadata, tags)
-- - access_history (context, headers, risk_factors, metadata, tags, alert_ids)
-- - scales (config)
-- - occurrences (attachments)
-- - scale_templates (config, template_data)
-- - posts (required_certifications, metadata)
-- - allocations (qualifications)
-- - solides_occurrences (anexos, dados_adicionais)
-- - solides_employees (endereco, dependentes, perfil_disc, perfil_profiler, dados_adicionais)
-- - disciplinary_actions (ai_recommendation, extra_data)
--
-- Versão: 1.0.0
-- Data: 2026-02-06
-- ===============================================================================

-- ===============================================================================
-- INÍCIO DA TRANSAÇÃO
-- ===============================================================================
BEGIN;

-- ===============================================================================
-- FUNÇÕES AUXILIARES
-- ===============================================================================

-- Função para verificar se uma tabela existe
CREATE OR REPLACE FUNCTION _tmp_table_exists(p_table_name TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = p_table_name
    );
END;
$$ LANGUAGE plpgsql;

-- Função para verificar se uma coluna existe em uma tabela
CREATE OR REPLACE FUNCTION _tmp_column_exists(p_table_name TEXT, p_column_name TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = p_table_name
        AND column_name = p_column_name
    );
END;
$$ LANGUAGE plpgsql;

-- Função para normalizar campo JSONB objeto (NULL ou '{}' -> '{}')
CREATE OR REPLACE FUNCTION _tmp_normalize_jsonb_object(p_table_name TEXT, p_column_name TEXT)
RETURNS VOID AS $$
DECLARE
    v_count INTEGER;
BEGIN
    IF NOT _tmp_table_exists(p_table_name) THEN
        RAISE NOTICE 'Tabela % não existe. Pulando...', p_table_name;
        RETURN;
    END IF;

    IF NOT _tmp_column_exists(p_table_name, p_column_name) THEN
        RAISE NOTICE 'Coluna %.% não existe. Pulando...', p_table_name, p_column_name;
        RETURN;
    END IF;

    EXECUTE format('
        UPDATE %I
        SET %I = ''{}''::jsonb
        WHERE %I IS NULL OR %I = ''{}''::jsonb OR %I = ''null''::jsonb
    ', p_table_name, p_column_name, p_column_name, p_column_name, p_column_name);

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RAISE NOTICE 'Normalizados % registros em %.% (objeto vazio)', v_count, p_table_name, p_column_name;
END;
$$ LANGUAGE plpgsql;

-- Função para normalizar campo JSONB array (NULL ou '[]' -> '[]')
CREATE OR REPLACE FUNCTION _tmp_normalize_jsonb_array(p_table_name TEXT, p_column_name TEXT)
RETURNS VOID AS $$
DECLARE
    v_count INTEGER;
BEGIN
    IF NOT _tmp_table_exists(p_table_name) THEN
        RAISE NOTICE 'Tabela % não existe. Pulando...', p_table_name;
        RETURN;
    END IF;

    IF NOT _tmp_column_exists(p_table_name, p_column_name) THEN
        RAISE NOTICE 'Coluna %.% não existe. Pulando...', p_table_name, p_column_name;
        RETURN;
    END IF;

    EXECUTE format('
        UPDATE %I
        SET %I = ''[]''::jsonb
        WHERE %I IS NULL OR %I = ''null''::jsonb
    ', p_table_name, p_column_name, p_column_name, p_column_name);

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RAISE NOTICE 'Normalizados % registros em %.% (array vazio)', v_count, p_table_name, p_column_name;
END;
$$ LANGUAGE plpgsql;

-- Função para remover chaves duplicadas (mantém a última ocorrência)
CREATE OR REPLACE FUNCTION _tmp_remove_duplicate_keys(p_table_name TEXT, p_column_name TEXT)
RETURNS VOID AS $$
DECLARE
    v_count INTEGER;
BEGIN
    IF NOT _tmp_table_exists(p_table_name) THEN
        RETURN;
    END IF;

    IF NOT _tmp_column_exists(p_table_name, p_column_name) THEN
        RETURN;
    END IF;

    -- Esta função utiliza jsonb_each para expandir e reagrupar, eliminando duplicatas
    EXECUTE format('
        UPDATE %I
        SET %I = (
            SELECT jsonb_object_agg(key, value)
            FROM jsonb_each(%I)
        )
        WHERE %I IS NOT NULL AND jsonb_typeof(%I) = ''object''
    ', p_table_name, p_column_name, p_column_name, p_column_name, p_column_name);

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RAISE NOTICE 'Removidas chaves duplicadas de % registros em %.%', v_count, p_table_name, p_column_name;
END;
$$ LANGUAGE plpgsql;

-- ===============================================================================
-- SEÇÃO 1: TABELA EMPLOYEES
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Processando tabela: employees';
    RAISE NOTICE '========================================';

    -- dados_adicionais: objeto JSONB -> padronizar para '{}'
    PERFORM _tmp_normalize_jsonb_object('employees', 'dados_adicionais');
    PERFORM _tmp_remove_duplicate_keys('employees', 'dados_adicionais');

    -- competencias: array JSONB -> padronizar para '[]'
    PERFORM _tmp_normalize_jsonb_array('employees', 'competencias');

    -- certificacoes: array JSONB -> padronizar para '[]'
    PERFORM _tmp_normalize_jsonb_array('employees', 'certificacoes');

    -- perfil_disc: objeto JSONB -> padronizar para '{}'
    PERFORM _tmp_normalize_jsonb_object('employees', 'perfil_disc');

    -- dependentes: array JSONB -> padronizar para '[]'
    PERFORM _tmp_normalize_jsonb_array('employees', 'dependentes');

    -- Padronizar estrutura de dados_adicionais com campos padrão
    IF _tmp_table_exists('employees') AND _tmp_column_exists('employees', 'dados_adicionais') THEN
        UPDATE employees
        SET dados_adicionais = dados_adicionais || '{
            "_normalized": true,
            "_normalized_at": "' || NOW()::text || '"
        }'::jsonb
        WHERE dados_adicionais IS NOT NULL
        AND dados_adicionais <> '{}'::jsonb
        AND NOT (dados_adicionais ? '_normalized');
    END IF;
END $$;

-- ===============================================================================
-- SEÇÃO 2: TABELA AUDIT_LOGS
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Processando tabela: audit_logs';
    RAISE NOTICE '========================================';

    -- details: objeto JSONB
    PERFORM _tmp_normalize_jsonb_object('audit_logs', 'details');
    PERFORM _tmp_remove_duplicate_keys('audit_logs', 'details');

    -- old_values: objeto JSONB
    PERFORM _tmp_normalize_jsonb_object('audit_logs', 'old_values');

    -- new_values: objeto JSONB
    PERFORM _tmp_normalize_jsonb_object('audit_logs', 'new_values');

    -- changed_fields: array JSONB
    PERFORM _tmp_normalize_jsonb_array('audit_logs', 'changed_fields');

    -- compliance_frameworks: array JSONB
    PERFORM _tmp_normalize_jsonb_array('audit_logs', 'compliance_frameworks');

    -- triggered_alerts: array JSONB
    PERFORM _tmp_normalize_jsonb_array('audit_logs', 'triggered_alerts');

    -- metadata: objeto JSONB
    PERFORM _tmp_normalize_jsonb_object('audit_logs', 'metadata');

    -- tags: array JSONB
    PERFORM _tmp_normalize_jsonb_array('audit_logs', 'tags');
END $$;

-- ===============================================================================
-- SEÇÃO 3: TABELA ACCESS_HISTORY
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Processando tabela: access_history';
    RAISE NOTICE '========================================';

    -- context: objeto JSONB
    PERFORM _tmp_normalize_jsonb_object('access_history', 'context');
    PERFORM _tmp_remove_duplicate_keys('access_history', 'context');

    -- headers: objeto JSONB
    PERFORM _tmp_normalize_jsonb_object('access_history', 'headers');
    PERFORM _tmp_remove_duplicate_keys('access_history', 'headers');

    -- risk_factors: array JSONB
    PERFORM _tmp_normalize_jsonb_array('access_history', 'risk_factors');

    -- metadata: objeto JSONB
    PERFORM _tmp_normalize_jsonb_object('access_history', 'metadata');

    -- tags: array JSONB
    PERFORM _tmp_normalize_jsonb_array('access_history', 'tags');

    -- alert_ids: array JSONB
    PERFORM _tmp_normalize_jsonb_array('access_history', 'alert_ids');
END $$;

-- ===============================================================================
-- SEÇÃO 4: TABELA SCALES
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Processando tabela: scales';
    RAISE NOTICE '========================================';

    -- config: objeto JSONB
    PERFORM _tmp_normalize_jsonb_object('scales', 'config');
    PERFORM _tmp_remove_duplicate_keys('scales', 'config');

    -- Padronizar estrutura de config com campos padrão para escalas
    IF _tmp_table_exists('scales') AND _tmp_column_exists('scales', 'config') THEN
        UPDATE scales
        SET config = COALESCE(config, '{}'::jsonb) || '{
            "_normalized": true,
            "_normalized_at": "' || NOW()::text || '"
        }'::jsonb
        WHERE config IS NOT NULL
        AND config <> '{}'::jsonb
        AND NOT (config ? '_normalized');
    END IF;
END $$;

-- ===============================================================================
-- SEÇÃO 5: TABELA OCCURRENCES
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Processando tabela: occurrences';
    RAISE NOTICE '========================================';

    -- attachments: array JSONB
    PERFORM _tmp_normalize_jsonb_array('occurrences', 'attachments');
END $$;

-- ===============================================================================
-- SEÇÃO 6: TABELA SCALE_TEMPLATES (was SEÇÃO 7)
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Processando tabela: scale_templates';
    RAISE NOTICE '========================================';

    -- config: objeto JSONB (tabela antiga)
    PERFORM _tmp_normalize_jsonb_object('scale_templates', 'config');

    -- template_data: objeto JSONB (tabela nova)
    PERFORM _tmp_normalize_jsonb_object('scale_templates', 'template_data');
END $$;

-- ===============================================================================
-- SEÇÃO 8: TABELA POSTS
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Processando tabela: posts';
    RAISE NOTICE '========================================';

    -- required_certifications: array JSONB
    PERFORM _tmp_normalize_jsonb_array('posts', 'required_certifications');

    -- metadata: objeto JSONB
    PERFORM _tmp_normalize_jsonb_object('posts', 'metadata');
END $$;

-- ===============================================================================
-- SEÇÃO 9: TABELA ALLOCATIONS
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Processando tabela: allocations';
    RAISE NOTICE '========================================';

    -- qualifications: array JSONB
    PERFORM _tmp_normalize_jsonb_array('allocations', 'qualifications');
END $$;

-- ===============================================================================
-- SEÇÃO 10: TABELAS SOLIDES (Integração)
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Processando tabelas Solides';
    RAISE NOTICE '========================================';

    -- solides_occurrences
    PERFORM _tmp_normalize_jsonb_array('solides_occurrences', 'anexos');
    PERFORM _tmp_normalize_jsonb_object('solides_occurrences', 'dados_adicionais');

    -- solides_employees
    PERFORM _tmp_normalize_jsonb_object('solides_employees', 'endereco');
    PERFORM _tmp_normalize_jsonb_array('solides_employees', 'dependentes');
    PERFORM _tmp_normalize_jsonb_object('solides_employees', 'perfil_disc');
    PERFORM _tmp_normalize_jsonb_object('solides_employees', 'perfil_profiler');
    PERFORM _tmp_normalize_jsonb_object('solides_employees', 'dados_adicionais');

    -- solides_absences
    PERFORM _tmp_normalize_jsonb_object('solides_absences', 'dados_adicionais');

    -- solides_workplaces
    PERFORM _tmp_normalize_jsonb_object('solides_workplaces', 'endereco');

    -- solides_work_schedules
    PERFORM _tmp_normalize_jsonb_object('solides_work_schedules', 'horarios');
END $$;

-- ===============================================================================
-- SEÇÃO 11: TABELA DISCIPLINARY_ACTIONS
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Processando tabela: disciplinary_actions';
    RAISE NOTICE '========================================';

    -- ai_recommendation: objeto JSONB
    PERFORM _tmp_normalize_jsonb_object('disciplinary_actions', 'ai_recommendation');

    -- extra_data: objeto JSONB
    PERFORM _tmp_normalize_jsonb_object('disciplinary_actions', 'extra_data');
END $$;

-- ===============================================================================
-- SEÇÃO 12: OUTRAS TABELAS COM CAMPOS JSONB
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Processando outras tabelas';
    RAISE NOTICE '========================================';

    -- compliance_rules
    PERFORM _tmp_normalize_jsonb_array('compliance_rules', 'evidence_required');
    PERFORM _tmp_normalize_jsonb_array('compliance_rules', 'controls_required');
    PERFORM _tmp_normalize_jsonb_array('compliance_rules', 'applies_to_entities');
    PERFORM _tmp_normalize_jsonb_array('compliance_rules', 'applies_to_roles');
    PERFORM _tmp_normalize_jsonb_array('compliance_rules', 'applies_to_modules');
    PERFORM _tmp_normalize_jsonb_array('compliance_rules', 'excluded_entities');
    PERFORM _tmp_normalize_jsonb_array('compliance_rules', 'notification_recipients');
    PERFORM _tmp_normalize_jsonb_array('compliance_rules', 'escalation_path');
    PERFORM _tmp_normalize_jsonb_array('compliance_rules', 'remediation_steps');
    PERFORM _tmp_normalize_jsonb_array('compliance_rules', 'related_policies');
    PERFORM _tmp_normalize_jsonb_object('compliance_rules', 'metadata');
    PERFORM _tmp_normalize_jsonb_array('compliance_rules', 'tags');

    -- compliance_checks
    PERFORM _tmp_normalize_jsonb_array('compliance_checks', 'evidence_collected');
    PERFORM _tmp_normalize_jsonb_array('compliance_checks', 'evidence_files');
    PERFORM _tmp_normalize_jsonb_array('compliance_checks', 'screenshots');
    PERFORM _tmp_normalize_jsonb_object('compliance_checks', 'query_results');
    PERFORM _tmp_normalize_jsonb_array('compliance_checks', 'violations');
    PERFORM _tmp_normalize_jsonb_object('compliance_checks', 'remediation_plan');
    PERFORM _tmp_normalize_jsonb_array('compliance_checks', 'notifications_sent');
    PERFORM _tmp_normalize_jsonb_object('compliance_checks', 'escalated_to');
    PERFORM _tmp_normalize_jsonb_object('compliance_checks', 'error_details');
    PERFORM _tmp_normalize_jsonb_object('compliance_checks', 'metadata');
    PERFORM _tmp_normalize_jsonb_array('compliance_checks', 'tags');

    -- data_retention_policies
    PERFORM _tmp_normalize_jsonb_array('data_retention_policies', 'entity_types');
    PERFORM _tmp_normalize_jsonb_array('data_retention_policies', 'table_names');
    PERFORM _tmp_normalize_jsonb_array('data_retention_policies', 'field_patterns');
    PERFORM _tmp_normalize_jsonb_array('data_retention_policies', 'excluded_entities');
    PERFORM _tmp_normalize_jsonb_array('data_retention_policies', 'anonymize_fields');
    PERFORM _tmp_normalize_jsonb_array('data_retention_policies', 'notify_recipients');
    PERFORM _tmp_normalize_jsonb_object('data_retention_policies', 'metadata');
    PERFORM _tmp_normalize_jsonb_array('data_retention_policies', 'tags');

    -- security_audits
    IF _tmp_table_exists('security_audits') THEN
        PERFORM _tmp_normalize_jsonb_object('security_audits', 'severity_breakdown');
        PERFORM _tmp_normalize_jsonb_object('security_audits', 'scan_results');
    END IF;
END $$;

-- ===============================================================================
-- SEÇÃO 13: LIMPEZA DE VALORES INVÁLIDOS
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Limpando valores inválidos';
    RAISE NOTICE '========================================';

    -- Corrigir strings vazias em campos JSONB (converter para valores padrão apropriados)
    IF _tmp_table_exists('employees') AND _tmp_column_exists('employees', 'dados_adicionais') THEN
        UPDATE employees
        SET dados_adicionais = '{}'::jsonb
        WHERE dados_adicionais = '""'::jsonb;
    END IF;

    IF _tmp_table_exists('employees') AND _tmp_column_exists('employees', 'competencias') THEN
        UPDATE employees
        SET competencias = '[]'::jsonb
        WHERE competencias = '""'::jsonb;
    END IF;

    -- Remover chaves com valores NULL desnecessários em objetos JSONB
    IF _tmp_table_exists('audit_logs') AND _tmp_column_exists('audit_logs', 'details') THEN
        UPDATE audit_logs
        SET details = (
            SELECT jsonb_object_agg(key, value)
            FROM jsonb_each(details)
            WHERE value IS NOT NULL AND value <> 'null'::jsonb
        )
        WHERE details IS NOT NULL AND jsonb_typeof(details) = 'object';
    END IF;
END $$;

-- ===============================================================================
-- SEÇÃO 14: ATUALIZAR TIMESTAMPS DE NORMALIZAÇÃO
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Registrando normalização';
    RAISE NOTICE '========================================';

    -- Criar ou atualizar tabela de controle de normalizações
    CREATE TABLE IF NOT EXISTS _jsonb_normalization_log (
        id SERIAL PRIMARY KEY,
        executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        script_version VARCHAR(20) NOT NULL,
        tables_affected INTEGER DEFAULT 0,
        records_updated INTEGER DEFAULT 0,
        execution_time_ms INTEGER
    );

    -- Inserir registro desta execução
    INSERT INTO _jsonb_normalization_log (script_version, tables_affected)
    VALUES ('1.0.0', 15);

    RAISE NOTICE 'Normalização registrada na tabela _jsonb_normalization_log';
END $$;

-- ===============================================================================
-- LIMPEZA DAS FUNÇÕES AUXILIARES TEMPORÁRIAS
-- ===============================================================================
DROP FUNCTION IF EXISTS _tmp_table_exists(TEXT);
DROP FUNCTION IF EXISTS _tmp_column_exists(TEXT, TEXT);
DROP FUNCTION IF EXISTS _tmp_normalize_jsonb_object(TEXT, TEXT);
DROP FUNCTION IF EXISTS _tmp_normalize_jsonb_array(TEXT, TEXT);
DROP FUNCTION IF EXISTS _tmp_remove_duplicate_keys(TEXT, TEXT);

-- ===============================================================================
-- COMMIT DA TRANSAÇÃO
-- ===============================================================================
COMMIT;

-- ===============================================================================
-- MENSAGEM FINAL
-- ===============================================================================
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'NORMALIZAÇÃO CONCLUÍDA COM SUCESSO!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Resumo das operações realizadas:';
    RAISE NOTICE '- Campos JSONB NULL convertidos para {} ou []';
    RAISE NOTICE '- Chaves duplicadas removidas (mantendo última ocorrência)';
    RAISE NOTICE '- Valores "null" como string normalizados';
    RAISE NOTICE '- Estrutura padronizada nos campos críticos';
    RAISE NOTICE '';
    RAISE NOTICE 'Verifique a tabela _jsonb_normalization_log';
    RAISE NOTICE 'para histórico de execuções.';
    RAISE NOTICE '========================================';
END $$;
