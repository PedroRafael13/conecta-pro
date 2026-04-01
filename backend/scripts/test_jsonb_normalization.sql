-- ===============================================================================
-- CONECTA PRO - TESTE DE NORMALIZAÇÃO JSONB
-- ===============================================================================
-- Script para testar e verificar a normalização dos campos JSONB
-- Este script cria dados de teste, executa a normalização e verifica os resultados
--
-- ⚠️ EXECUTE APENAS EM AMBIENTE DE DESENVOLVIMENTO
-- ===============================================================================

-- ===============================================================================
-- PREPARAÇÃO: Criar tabelas de teste (simulando estrutura real)
-- ===============================================================================

-- Criar schema de teste
DROP SCHEMA IF EXISTS test_jsonb CASCADE;
CREATE SCHEMA test_jsonb;

-- Tabela employees de teste
CREATE TABLE test_jsonb.employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255),
    dados_adicionais JSONB,
    competencias JSONB,
    certificacoes JSONB,
    perfil_disc JSONB,
    dependentes JSONB
);

-- Tabela audit_logs de teste
CREATE TABLE test_jsonb.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    details JSONB,
    metadata JSONB,
    tags JSONB
);

-- Tabela occurrences de teste
CREATE TABLE test_jsonb.occurrences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attachments JSONB
);

-- ===============================================================================
-- INSERIR DADOS DE TESTE (com problemas conhecidos)
-- ===============================================================================

-- Inserir registros com NULL
INSERT INTO test_jsonb.employees (nome, dados_adicionais, competencias, certificacoes, perfil_disc, dependentes) VALUES
('Funcionario NULL', NULL, NULL, NULL, NULL, NULL);

-- Inserir registros com objetos vazios
INSERT INTO test_jsonb.employees (nome, dados_adicionais, competencias, certificacoes, perfil_disc, dependentes) VALUES
('Funcionario Vazio', '{}', '[]', '[]', '{}', '[]');

-- Inserir registros com strings "null"
INSERT INTO test_jsonb.employees (nome, dados_adicionais, competencias, certificacoes, perfil_disc, dependentes) VALUES
('Funcionario Null String', '"null"', '"null"', '"null"', '"null"', '"null"');

-- Inserir registros com strings vazias
INSERT INTO test_jsonb.employees (nome, dados_adicionais, competencias) VALUES
('Funcionario String Vazia', '""', '""');

-- Inserir registros com dados válidos (não devem ser alterados)
INSERT INTO test_jsonb.employees (nome, dados_adicionais, competencias, certificacoes, perfil_disc, dependentes) VALUES
('Funcionario OK',
 '{"curso": "vigilancia", "validade": "2026-12-01"}'::jsonb,
 '["lideranca", "comunicacao"]'::jsonb,
 '[{"nome": "curso1", "ano": 2025}]'::jsonb,
 '{"D": 80, "I": 60}'::jsonb,
 '[{"nome": "Filho 1", "idade": 10}]'::jsonb
);

-- Inserir registros com chaves duplicadas (simulado)
INSERT INTO test_jsonb.employees (nome, dados_adicionais) VALUES
('Funcionario Chaves Dup', '{"a": 1, "a": 2, "b": 3}'::jsonb);

-- Inserir dados em audit_logs
INSERT INTO test_jsonb.audit_logs (details, metadata, tags) VALUES
(NULL, NULL, NULL),
('{}', '{}', '[]'),
('{"user": "admin", "action": "create"}'::jsonb, '{"ip": "192.168.1.1"}'::jsonb, '["importante"]'::jsonb);

-- Inserir dados em occurrences
INSERT INTO test_jsonb.occurrences (attachments) VALUES
(NULL),
('[]'),
('[{"url": "http://exemplo.com/foto.jpg", "tipo": "imagem"}]'::jsonb);

-- ===============================================================================
-- VERIFICAR DADOS ANTES DA NORMALIZAÇÃO
-- ===============================================================================

SELECT 'ANTES DA NORMALIZAÇÃO' AS status;

SELECT
    nome,
    dados_adicionais IS NULL AS dados_null,
    competencias IS NULL AS comp_null,
    dados_adicionais = '{}' AS dados_vazio,
    competencias = '[]'::jsonb AS comp_vazio
FROM test_jsonb.employees;

-- ===============================================================================
-- FUNÇÕES DE NORMALIZAÇÃO (cópia adaptada do script principal)
-- ===============================================================================

CREATE OR REPLACE FUNCTION test_jsonb._normalize_jsonb_object(p_table_name TEXT, p_column_name TEXT)
RETURNS VOID AS $$
DECLARE
    v_count INTEGER;
BEGIN
    EXECUTE format('
        UPDATE test_jsonb.%I
        SET %I = ''{}''::jsonb
        WHERE %I IS NULL OR %I = ''null''::jsonb OR %I = '""''::jsonb
    ', p_table_name, p_column_name, p_column_name, p_column_name, p_column_name);

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RAISE NOTICE 'Normalizados % registros em %.%', v_count, p_table_name, p_column_name;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION test_jsonb._normalize_jsonb_array(p_table_name TEXT, p_column_name TEXT)
RETURNS VOID AS $$
DECLARE
    v_count INTEGER;
BEGIN
    EXECUTE format('
        UPDATE test_jsonb.%I
        SET %I = ''[]''::jsonb
        WHERE %I IS NULL OR %I = ''null''::jsonb OR %I = '""''::jsonb
    ', p_table_name, p_column_name, p_column_name, p_column_name, p_column_name);

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RAISE NOTICE 'Normalizados % registros em %.%', v_count, p_table_name, p_column_name;
END;
$$ LANGUAGE plpgsql;

-- ===============================================================================
-- EXECUTAR NORMALIZAÇÃO
-- ===============================================================================

SELECT 'EXECUTANDO NORMALIZAÇÃO...' AS status;

-- Normalizar employees
SELECT test_jsonb._normalize_jsonb_object('employees', 'dados_adicionais');
SELECT test_jsonb._normalize_jsonb_array('employees', 'competencias');
SELECT test_jsonb._normalize_jsonb_array('employees', 'certificacoes');
SELECT test_jsonb._normalize_jsonb_object('employees', 'perfil_disc');
SELECT test_jsonb._normalize_jsonb_array('employees', 'dependentes');

-- Normalizar audit_logs
SELECT test_jsonb._normalize_jsonb_object('audit_logs', 'details');
SELECT test_jsonb._normalize_jsonb_object('audit_logs', 'metadata');
SELECT test_jsonb._normalize_jsonb_array('audit_logs', 'tags');

-- Normalizar occurrences
SELECT test_jsonb._normalize_jsonb_array('occurrences', 'attachments');

-- ===============================================================================
-- VERIFICAR DADOS APÓS A NORMALIZAÇÃO
-- ===============================================================================

SELECT 'APÓS A NORMALIZAÇÃO' AS status;

SELECT
    nome,
    dados_adicionais,
    competencias,
    dados_adicionais IS NULL AS dados_null,
    competencias IS NULL AS comp_null
FROM test_jsonb.employees;

-- ===============================================================================
-- VERIFICAÇÕES DE TESTE
-- ===============================================================================

SELECT 'VERIFICAÇÕES DE TESTE' AS status;

-- Teste 1: Verificar se campos NULL foram convertidos
SELECT
    'Teste 1: Campos NULL convertidos' AS teste,
    CASE
        WHEN COUNT(*) = 0 THEN 'PASSOU ✓'
        ELSE 'FALHOU ✗'
    END AS resultado
FROM test_jsonb.employees
WHERE dados_adicionais IS NULL OR competencias IS NULL;

-- Teste 2: Verificar se strings "null" foram convertidas
SELECT
    'Teste 2: Strings "null" convertidas' AS teste,
    CASE
        WHEN COUNT(*) = 0 THEN 'PASSOU ✓'
        ELSE 'FALHOU ✗'
    END AS resultado
FROM test_jsonb.employees
WHERE dados_adicionais = '"null"'::jsonb OR competencias = '"null"'::jsonb;

-- Teste 3: Verificar se dados válidos não foram alterados
SELECT
    'Teste 3: Dados válidos preservados' AS teste,
    CASE
        WHEN dados_adicionais = '{"curso": "vigilancia", "validade": "2026-12-01"}'::jsonb
        THEN 'PASSOU ✓'
        ELSE 'FALHOU ✗'
    END AS resultado
FROM test_jsonb.employees
WHERE nome = 'Funcionario OK';

-- Teste 4: Verificar valores padrão aplicados
SELECT
    'Teste 4: Valores padrão ({})' AS teste,
    CASE
        WHEN COUNT(*) >= 3 THEN 'PASSOU ✓'
        ELSE 'FALHOU ✗'
    END AS resultado
FROM test_jsonb.employees
WHERE dados_adicionais = '{}'::jsonb AND nome LIKE 'Funcionario%';

-- Teste 5: Verificar valores padrão aplicados (arrays)
SELECT
    'Teste 5: Valores padrão ([])' AS teste,
    CASE
        WHEN COUNT(*) >= 3 THEN 'PASSOU ✓'
        ELSE 'FALHOU ✗'
    END AS resultado
FROM test_jsonb.employees
WHERE competencias = '[]'::jsonb AND nome LIKE 'Funcionario%';

-- Teste 6: Verificar audit_logs
SELECT
    'Teste 6: Audit logs normalizados' AS teste,
    CASE
        WHEN COUNT(*) = 0 THEN 'PASSOU ✓'
        ELSE 'FALHOU ✗'
    END AS resultado
FROM test_jsonb.audit_logs
WHERE details IS NULL OR metadata IS NULL OR tags IS NULL;

-- Teste 7: Verificar occurrences
SELECT
    'Teste 7: Occurrences normalizadas' AS teste,
    CASE
        WHEN COUNT(*) = 0 THEN 'PASSOU ✓'
        ELSE 'FALHOU ✗'
    END AS resultado
FROM test_jsonb.occurrences
WHERE attachments IS NULL;

-- ===============================================================================
-- RELATÓRIO FINAL
-- ===============================================================================

SELECT 'RELATÓRIO FINAL' AS status;

SELECT
    'Employees' AS tabela,
    COUNT(*) AS total_registros,
    COUNT(*) FILTER (WHERE dados_adicionais = '{}') AS dados_adicionais_vazios,
    COUNT(*) FILTER (WHERE competencias = '[]') AS competencias_vazias,
    COUNT(*) FILTER (WHERE dados_adicionais IS NULL) AS dados_null,
    COUNT(*) FILTER (WHERE dados_adicionais IS NOT NULL AND dados_adicionais <> '{}') AS dados_preenchidos
FROM test_jsonb.employees;

SELECT
    'Audit Logs' AS tabela,
    COUNT(*) AS total_registros,
    COUNT(*) FILTER (WHERE details = '{}') AS details_vazios,
    COUNT(*) FILTER (WHERE tags = '[]') AS tags_vazias,
    COUNT(*) FILTER (WHERE details IS NULL) AS details_null
FROM test_jsonb.audit_logs;

SELECT
    'Occurrences' AS tabela,
    COUNT(*) AS total_registros,
    COUNT(*) FILTER (WHERE attachments = '[]') AS attachments_vazios,
    COUNT(*) FILTER (WHERE attachments IS NULL) AS attachments_null,
    COUNT(*) FILTER (WHERE attachments IS NOT NULL AND attachments <> '[]') AS attachments_preenchidos
FROM test_jsonb.occurrences;

-- ===============================================================================
-- LIMPEZA
-- ===============================================================================

-- Remover funções temporárias
DROP FUNCTION IF EXISTS test_jsonb._normalize_jsonb_object(TEXT, TEXT);
DROP FUNCTION IF EXISTS test_jsonb._normalize_jsonb_array(TEXT, TEXT);

-- Manter tabelas de teste para inspeção manual (opcional)
-- Para remover: DROP SCHEMA test_jsonb CASCADE;

SELECT 'TESTE CONCLUÍDO!' AS status;
SELECT 'Execute "DROP SCHEMA test_jsonb CASCADE;" para limpar os dados de teste.' AS instrucao;
