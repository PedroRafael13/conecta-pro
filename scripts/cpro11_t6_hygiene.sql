-- =============================================================================
-- CPRO11 T6 — Higiene de Dados: CRM / Vendas
-- Criado: 2026-04-20
-- Script IDEMPOTENTE: executar 2x produz mesmo resultado (DELETE WHERE EXISTS)
-- Backup obrigatório ANTES de executar (INV-3): t6_backups/tables_backup_*.sql
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- BLOCO 0 — Verificação de pré-condições (🔴 testa antes de mutar)
-- ---------------------------------------------------------------------------
DO $$
DECLARE
  v_life_centro_opps INTEGER;
  v_matriz_contratos  INTEGER;
BEGIN
  -- Life Centro: confirmar que tem opportunity (não deve ser deletado)
  SELECT COUNT(*) INTO v_life_centro_opps
    FROM opportunities WHERE lead_id = '5839bcd2-3d1b-4b68-943a-3170db2d896a';
  IF v_life_centro_opps = 0 THEN
    RAISE EXCEPTION '🔴 FALHA PRE-COND: Life Centro deveria ter 1 opportunity, encontrou 0';
  END IF;
  RAISE NOTICE '✅ PRE-COND: Life Centro tem % opportunity(ies) — será preservado', v_life_centro_opps;

  -- Matriz escritório: confirmar que tem 0 contratos (seguro deletar)
  SELECT COUNT(*) INTO v_matriz_contratos
    FROM contracts WHERE client_id = '69c83c78-1599-4fd6-b1ca-68efeadfdc9d';
  IF v_matriz_contratos > 0 THEN
    RAISE EXCEPTION '🔴 FALHA PRE-COND: Matriz escritório tem % contratos — NÃO deletar sem revisão', v_matriz_contratos;
  END IF;
  RAISE NOTICE '✅ PRE-COND: Matriz escritório tem 0 contratos — seguro deletar';
END $$;

-- ---------------------------------------------------------------------------
-- BLOCO 1 — P0.10: Deletar cliente duplicado "Matriz escritório"
-- Motivo: CNPJ 00000000000000 duplicado, 0 contratos/atividades/contatos
-- O cliente real é "Conecta Mais - Segurança e Tecnologia" (9bac5ff5)
-- Cadeia FK (§13.1 Chesterton confirmada em execução):
--   document_kit_items(29) → document_kits(4) → condominiums(1) → clients
-- Ordem obrigatória: kit_items → kits → condominiums → clients
-- ---------------------------------------------------------------------------
DO $$
DECLARE
  v_deleted   INTEGER;
  v_condo_id  CONSTANT UUID := 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
  v_client_id CONSTANT UUID := '69c83c78-1599-4fd6-b1ca-68efeadfdc9d';
BEGIN
  IF NOT EXISTS (SELECT 1 FROM clients WHERE id=v_client_id) THEN
    RAISE NOTICE 'SKIP: Matriz escritório já foi removido (idempotente)';
    RETURN;
  END IF;

  -- 1a: document_kit_items (self-ref OK pois deleta todos do condominio de uma vez)
  DELETE FROM document_kit_items WHERE condominio_id = v_condo_id;
  GET DIAGNOSTICS v_deleted = ROW_COUNT;
  RAISE NOTICE 'DELETED: document_kit_items(%) para Condomínio Teste', v_deleted;

  -- 1b: document_kits
  DELETE FROM document_kits WHERE condominio_id = v_condo_id;
  GET DIAGNOSTICS v_deleted = ROW_COUNT;
  RAISE NOTICE 'DELETED: document_kits(%) para Condomínio Teste', v_deleted;

  -- 1c: condominium TEST-COND-001
  DELETE FROM condominiums WHERE id = v_condo_id;
  GET DIAGNOSTICS v_deleted = ROW_COUNT;
  RAISE NOTICE 'DELETED: condominiums(%) Condomínio Teste Integração', v_deleted;

  -- 1d: client Matriz escritório
  DELETE FROM clients WHERE id = v_client_id AND name = 'Matriz escritório';
  GET DIAGNOSTICS v_deleted = ROW_COUNT;
  RAISE NOTICE 'DELETED: clients(%) Matriz escritório', v_deleted;
END $$;

-- ---------------------------------------------------------------------------
-- BLOCO 2 — P1.10: Deletar 2x leads "PREFEITURA TESTE" (mock idênticos)
-- Motivo: dados fictícios, email=licitacao.novo@lead.conecta, 0 FK refs
-- ---------------------------------------------------------------------------
DO $$
DECLARE v_deleted INTEGER;
BEGIN
  DELETE FROM leads
  WHERE id IN (
    '9e951d62-b9fd-4560-a353-9696fc5aba5c',
    '598dec5d-e9c4-4e7a-b603-b7e5251d246a'
  )
  AND name = 'PREFEITURA TESTE';
  GET DIAGNOSTICS v_deleted = ROW_COUNT;
  IF v_deleted = 0 THEN
    RAISE NOTICE 'SKIP: PREFEITURA TESTE leads já foram removidos (idempotente)';
  ELSE
    RAISE NOTICE 'DELETED: % leads PREFEITURA TESTE', v_deleted;
  END IF;
END $$;

-- ---------------------------------------------------------------------------
-- BLOCO 3 — P1.10: Deletar lead "PREFEITURA MANAUS" (mock de licitação)
-- Motivo: email sintético licitacao.PE-001-2026@lead.conecta, 0 FK refs
-- ---------------------------------------------------------------------------
DO $$
DECLARE v_deleted INTEGER;
BEGIN
  DELETE FROM leads
  WHERE id = '4eff5a48-2c0d-4b3e-b9c3-d29c19d5956a'
    AND name = 'PREFEITURA MANAUS';
  GET DIAGNOSTICS v_deleted = ROW_COUNT;
  IF v_deleted = 0 THEN
    RAISE NOTICE 'SKIP: PREFEITURA MANAUS lead já foi removido (idempotente)';
  ELSE
    RAISE NOTICE 'DELETED: lead PREFEITURA MANAUS (mock licitacao)';
  END IF;
END $$;

-- ---------------------------------------------------------------------------
-- BLOCO 4 — P1.11: Deletar crm_activities "Teste auditoria"
-- Motivo: mock criado em teste de auditoria, subject='Teste auditoria', 0 FK refs
-- ---------------------------------------------------------------------------
DO $$
DECLARE v_deleted INTEGER;
BEGIN
  DELETE FROM crm_activities
  WHERE id = 'e1cf3bf6-a069-47f5-a21e-385e0ffa9fdd'
    AND subject = 'Teste auditoria';
  GET DIAGNOSTICS v_deleted = ROW_COUNT;
  IF v_deleted = 0 THEN
    RAISE NOTICE 'SKIP: crm_activity "Teste auditoria" já foi removido (idempotente)';
  ELSE
    RAISE NOTICE 'DELETED: crm_activity "Teste auditoria"';
  END IF;
END $$;

-- ---------------------------------------------------------------------------
-- BLOCO 5 — P1.12: Deletar crm_contacts "Teste"
-- Motivo: mock sem role/email, name='Teste', 0 FK refs
-- ---------------------------------------------------------------------------
DO $$
DECLARE v_deleted INTEGER;
BEGIN
  DELETE FROM crm_contacts
  WHERE id = '36653983-d72e-4a95-a26e-1d047a5cf4bd'
    AND name = 'Teste';
  GET DIAGNOSTICS v_deleted = ROW_COUNT;
  IF v_deleted = 0 THEN
    RAISE NOTICE 'SKIP: crm_contact "Teste" já foi removido (idempotente)';
  ELSE
    RAISE NOTICE 'DELETED: crm_contact "Teste"';
  END IF;
END $$;

-- ---------------------------------------------------------------------------
-- BLOCO 6 — 🔴 Testes pós-mutação (INV-6)
-- ---------------------------------------------------------------------------
DO $$
DECLARE
  v_count INTEGER;
BEGIN
  -- T1: "Matriz escritório" não existe mais
  SELECT COUNT(*) INTO v_count FROM clients WHERE id = '69c83c78-1599-4fd6-b1ca-68efeadfdc9d';
  IF v_count > 0 THEN RAISE EXCEPTION '🔴 T1 FAIL: Matriz escritório ainda existe'; END IF;
  RAISE NOTICE '✅ T1: Matriz escritório removido';

  -- T2: "Conecta Mais" (real) preservado
  SELECT COUNT(*) INTO v_count FROM clients WHERE id = '9bac5ff5-7614-4498-809c-b88c6841672e';
  IF v_count = 0 THEN RAISE EXCEPTION '🔴 T2 FAIL: Conecta Mais foi deletado indevidamente'; END IF;
  RAISE NOTICE '✅ T2: Conecta Mais preservado';

  -- T3: PREFEITURA TESTE leads removidos
  SELECT COUNT(*) INTO v_count FROM leads WHERE name = 'PREFEITURA TESTE';
  IF v_count > 0 THEN RAISE EXCEPTION '🔴 T3 FAIL: Ainda existem % leads PREFEITURA TESTE', v_count; END IF;
  RAISE NOTICE '✅ T3: 0 leads PREFEITURA TESTE';

  -- T4: Life Centro lead preservado (tem opportunity)
  SELECT COUNT(*) INTO v_count FROM leads WHERE id = '5839bcd2-3d1b-4b68-943a-3170db2d896a';
  IF v_count = 0 THEN RAISE EXCEPTION '🔴 T4 FAIL: Life Centro lead foi deletado (tinha opportunity!)'; END IF;
  RAISE NOTICE '✅ T4: Life Centro lead preservado';

  -- T5: crm_activities limpo
  SELECT COUNT(*) INTO v_count FROM crm_activities WHERE subject = 'Teste auditoria';
  IF v_count > 0 THEN RAISE EXCEPTION '🔴 T5 FAIL: crm_activity Teste auditoria ainda existe'; END IF;
  RAISE NOTICE '✅ T5: crm_activities mock removido';

  -- T6: crm_contacts limpo
  SELECT COUNT(*) INTO v_count FROM crm_contacts WHERE name = 'Teste' AND role IS NULL;
  IF v_count > 0 THEN RAISE EXCEPTION '🔴 T6 FAIL: crm_contact Teste ainda existe'; END IF;
  RAISE NOTICE '✅ T6: crm_contacts mock removido';

  -- T7: Total de clients = 11 (era 12: Conecta Mais + 10 condominios + Matriz; agora 11)
  SELECT COUNT(*) INTO v_count FROM clients;
  IF v_count <> 11 THEN RAISE EXCEPTION '🔴 T7 FAIL: clients esperado=11, encontrado=%', v_count; END IF;
  RAISE NOTICE '✅ T7: clients count = 11';

  -- T8: Total de leads = 11 (era 14: 11 reais + 2 PREF.TESTE + PREF.MANAUS; agora 11)
  SELECT COUNT(*) INTO v_count FROM leads;
  IF v_count <> 11 THEN RAISE EXCEPTION '🔴 T8 FAIL: leads esperado=11, encontrado=%', v_count; END IF;
  RAISE NOTICE '✅ T8: leads count = 11';

  RAISE NOTICE '';
  RAISE NOTICE '=== HIGIENE CONCLUÍDA — 6/6 mutações + 8/8 testes ✅ ===';
END $$;

COMMIT;

-- ---------------------------------------------------------------------------
-- BLOCO 7 — Chesterton: tabelas vazias intencionais (NÃO tocar)
-- commission_rules: 0 rows — schema completo (22 cols), produto novo sem dados
-- lead_scores: 0 rows — gerado por IA quando leads são qualificados
-- pricing_simulations: 0 rows — gerado quando propostas são criadas
-- modules/comercial/ stubs: código stub aguardando implementação futura
-- CONCLUSÃO: nenhum dos 3 é bug — são módulos em implantação gradual
-- ---------------------------------------------------------------------------
