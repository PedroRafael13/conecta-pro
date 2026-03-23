-- ================================================================
-- SEED: Propagacao de dados reais para 11 clientes condomínios
-- Data: 2026-03-23
-- Faturamento total: R$ 272.086,96/mes
-- ================================================================

-- 1. CONTRATOS (client_contracts)
INSERT INTO client_contracts (id, client_id, contract_number, service_type, status, description, start_date, end_date, monthly_value, billing_day, auto_renewal, ativo)
VALUES
(gen_random_uuid(), '003197ed-2e49-45aa-80a8-3e837c9d1404', 'CT-2025-001', 'portaria_remota', 'active', 'Portaria 24h + Servicos Gerais', '2025-01-01', '2026-12-31', 65842.42, 10, true, true),
(gen_random_uuid(), '37f35647-bf2b-488f-9146-a653d205cc77', 'CT-2025-002', 'portaria_remota', 'active', 'Portaria 24h', '2025-01-01', '2026-12-31', 42544.50, 10, true, true),
(gen_random_uuid(), 'f8e84fa7-0fcc-43d5-8ee3-f3734b410d07', 'CT-2025-003', 'portaria_remota', 'active', 'Portaria 24h + Limpeza', '2025-01-01', '2026-12-31', 42255.80, 10, true, true),
(gen_random_uuid(), 'f59c7354-1541-4f47-a18b-c25f581bb5eb', 'CT-2025-004', 'portaria_remota', 'active', 'Portaria + Limpeza + Piscina', '2025-01-01', '2026-12-31', 40466.50, 10, true, true),
(gen_random_uuid(), '2b17d0f2-06de-4f09-9024-44849263bfe0', 'CT-2025-005', 'portaria_remota', 'active', 'Portaria 24h + CFTV', '2025-01-01', '2026-12-31', 37338.33, 10, true, true),
(gen_random_uuid(), '806c4970-ab5a-491a-aa6a-a1aad705234a', 'CT-2025-006', 'portaria_remota', 'active', 'Portaria + Servicos Gerais', '2025-01-01', '2026-12-31', 25592.71, 10, true, true),
(gen_random_uuid(), 'e6a18d9f-497d-4d85-922b-3feb153a8af3', 'CT-2025-007', 'limpeza', 'active', 'Limpeza', '2025-01-01', '2026-12-31', 8346.70, 10, true, true),
(gen_random_uuid(), 'b043f21a-97ea-4e53-b78a-2eb0cead9383', 'CT-2025-008', 'monitoramento_24h', 'active', 'Seg Eletronica + Portaria Remota', '2025-01-01', '2026-12-31', 6000.00, 10, true, true),
(gen_random_uuid(), 'a26984e9-a412-4e7e-b4a0-e0d4352856fc', 'CT-2025-009', 'manutencao', 'active', 'Manutencao CFTV', '2025-01-01', '2026-12-31', 1700.00, 10, true, true),
(gen_random_uuid(), 'f19c2275-c4d0-4842-a174-dc64a221c15a', 'CT-2025-010', 'manutencao', 'active', 'Manutencao CFTV', '2025-01-01', '2026-12-31', 1500.00, 10, true, true),
(gen_random_uuid(), 'c0750f70-7e60-4898-9ed2-d303e361c41e', 'CT-2025-011', 'manutencao', 'active', 'Manutencao CFTV', '2025-01-01', '2026-12-31', 500.00, 10, true, true)
ON CONFLICT DO NOTHING;

-- 2. CONDOMINIUMS
INSERT INTO condominiums (id, client_id, code, name, cnpj, condominium_type, status, has_pool, has_gym, has_party_room, has_playground, has_sports_court, has_sauna, has_barbecue, has_garden, has_cctv, has_access_control, has_intercom, has_24h_security, has_electric_fence, has_alarm, ativo)
VALUES
(gen_random_uuid(), '003197ed-2e49-45aa-80a8-3e837c9d1404', 'COND-001', 'Ideal Flores da Cidade', '23147782000191', 'residential', 'active', true, true, true, true, true, false, true, true, true, true, true, true, true, true, true),
(gen_random_uuid(), '37f35647-bf2b-488f-9146-a653d205cc77', 'COND-002', 'Laranjeiras Village', '24632786000128', 'residential', 'active', true, true, true, true, false, false, true, true, true, true, true, true, true, true, true),
(gen_random_uuid(), 'f8e84fa7-0fcc-43d5-8ee3-f3734b410d07', 'COND-003', 'Mirante das Flores', '52605708000170', 'residential', 'active', true, true, true, true, true, false, true, true, true, true, true, true, true, true, true),
(gen_random_uuid(), 'f59c7354-1541-4f47-a18b-c25f581bb5eb', 'COND-004', 'Prime Arena', '47405340000166', 'residential', 'active', true, true, true, true, true, false, true, true, true, true, true, true, true, true, true),
(gen_random_uuid(), '2b17d0f2-06de-4f09-9024-44849263bfe0', 'COND-005', 'Villa dos Passaros', '13221953000121', 'residential', 'active', false, false, true, true, false, false, true, true, true, true, true, true, true, true, true),
(gen_random_uuid(), '806c4970-ab5a-491a-aa6a-a1aad705234a', 'COND-006', 'Villa Dei Fiori', '02153384000108', 'residential', 'active', false, false, true, true, false, false, true, true, true, true, true, true, true, true, true),
(gen_random_uuid(), 'e6a18d9f-497d-4d85-922b-3feb153a8af3', 'COND-007', 'Michelangelo', '04911208000113', 'residential', 'active', false, false, true, false, false, false, false, false, false, false, false, false, false, false, true),
(gen_random_uuid(), 'b043f21a-97ea-4e53-b78a-2eb0cead9383', 'COND-008', 'Parque Residencial Gelain', '00736037000182', 'residential', 'active', false, false, true, true, false, false, true, false, true, true, true, false, true, false, true),
(gen_random_uuid(), 'a26984e9-a412-4e7e-b4a0-e0d4352856fc', 'COND-009', 'Parise Village', '34857941000168', 'residential', 'active', false, false, true, false, false, false, false, false, true, true, false, false, true, false, true),
(gen_random_uuid(), 'f19c2275-c4d0-4842-a174-dc64a221c15a', 'COND-010', 'Life Centro', '19865917000187', 'commercial', 'active', false, false, false, false, false, false, false, false, true, true, true, false, false, false, true),
(gen_random_uuid(), 'c0750f70-7e60-4898-9ed2-d303e361c41e', 'COND-011', 'Green Hills', '08063476000183', 'residential', 'active', false, false, true, true, false, false, true, true, true, true, true, false, false, false, true)
ON CONFLICT DO NOTHING;

-- 3. VINCULAR POSTOS AOS CLIENTES
UPDATE posts SET client_id = '003197ed-2e49-45aa-80a8-3e837c9d1404' WHERE name ILIKE '%Ideal Flores%';
UPDATE posts SET client_id = '37f35647-bf2b-488f-9146-a653d205cc77' WHERE name ILIKE '%Laranjeiras%';
UPDATE posts SET client_id = 'f8e84fa7-0fcc-43d5-8ee3-f3734b410d07' WHERE name ILIKE '%Mirante%';
UPDATE posts SET client_id = 'f59c7354-1541-4f47-a18b-c25f581bb5eb' WHERE name ILIKE '%Prime Arena%';
UPDATE posts SET client_id = '2b17d0f2-06de-4f09-9024-44849263bfe0' WHERE name ILIKE '%Villa dos P%';
UPDATE posts SET client_id = '806c4970-ab5a-491a-aa6a-a1aad705234a' WHERE name ILIKE '%Villa Dei%';
UPDATE posts SET client_id = 'e6a18d9f-497d-4d85-922b-3feb153a8af3' WHERE name ILIKE '%Michelangelo%' AND status = 'active';
UPDATE posts SET client_id = 'b043f21a-97ea-4e53-b78a-2eb0cead9383' WHERE name ILIKE '%Gelain%';
UPDATE posts SET client_id = 'a26984e9-a412-4e7e-b4a0-e0d4352856fc' WHERE name ILIKE '%Parise%';
UPDATE posts SET client_id = 'f19c2275-c4d0-4842-a174-dc64a221c15a' WHERE name ILIKE '%Life Centro%';
UPDATE posts SET client_id = 'c0750f70-7e60-4898-9ed2-d303e361c41e' WHERE name ILIKE '%Green Hills%';

-- 4. LEADS CRM
INSERT INTO leads (id, name, email, phone, company, source, status, score, probability, expected_value, is_active, notes, created_at, updated_at)
VALUES
(gen_random_uuid(), 'Ideal Flores da Cidade', 'idealflores@conectamais.pro', '92999000001', 'CONDOMINIO IDEAL FLORES DA CIDADE', 'indicacao', 'converted', 100, 1.0, 65842.42, true, 'Portaria 24h + Servicos Gerais', NOW(), NOW()),
(gen_random_uuid(), 'Laranjeiras Village', 'ADMLARANJEIRASVILLAGE@GMAIL.COM', '92999000002', 'RESIDENCIAL LARANJEIRAS VILLAGE', 'indicacao', 'converted', 100, 1.0, 42544.50, true, 'Portaria 24h', NOW(), NOW()),
(gen_random_uuid(), 'Mirante das Flores', 'miranteflores@conectamais.pro', '92999000003', 'CONDOMINIO MIRANTE DAS FLORES', 'indicacao', 'converted', 100, 1.0, 42255.80, true, 'Portaria + Limpeza', NOW(), NOW()),
(gen_random_uuid(), 'Prime Arena', 'PRIME.ARENAA@GMAIL.COM', '92999000004', 'CONDOMINIO PRIME ARENA', 'indicacao', 'converted', 100, 1.0, 40466.50, true, 'Portaria + Limpeza + Piscina', NOW(), NOW()),
(gen_random_uuid(), 'Villa dos Passaros', 'villapassaros@conectamais.pro', '92999000005', 'CONDOMINIO RESIDENCIAL VILLA DOS PASSAROS', 'indicacao', 'converted', 100, 1.0, 37338.33, true, 'Portaria 24h + CFTV', NOW(), NOW()),
(gen_random_uuid(), 'Villa Dei Fiori', 'villadei@conectamais.pro', '92999000006', 'CONDOMINIO VILLA DEI FIORI', 'indicacao', 'converted', 100, 1.0, 25592.71, true, 'Portaria + Servicos Gerais', NOW(), NOW()),
(gen_random_uuid(), 'Michelangelo', 'michelangelo@conectamais.pro', '92999000007', 'CONDOMINIO DO EDIFICIO MICHELANGELO', 'indicacao', 'converted', 100, 1.0, 8346.70, true, 'Limpeza', NOW(), NOW()),
(gen_random_uuid(), 'Gelain', 'gelain@conectamais.pro', '92999000008', 'CONDOMINIO PARQUE RESIDENCIAL GELAIN', 'indicacao', 'converted', 100, 1.0, 6000.00, true, 'Seg Eletronica + Portaria Remota', NOW(), NOW()),
(gen_random_uuid(), 'Parise Village', 'parisevillage@conectamais.pro', '92999000009', 'CONDOMINIO RESIDENCIAL PARISE VILLAGE', 'indicacao', 'converted', 100, 1.0, 1700.00, true, 'Manutencao CFTV', NOW(), NOW()),
(gen_random_uuid(), 'Life Centro', 'lifecentro@conectamais.pro', '92999000010', 'CONDOMINIO LIFE CENTRO', 'indicacao', 'converted', 100, 1.0, 1500.00, true, 'Manutencao CFTV', NOW(), NOW()),
(gen_random_uuid(), 'Green Hills', 'greenhills@conectamais.pro', '92999000011', 'CONDOMINIO RESIDENCIAL GREEN HILLS', 'indicacao', 'converted', 100, 1.0, 500.00, true, 'Manutencao CFTV', NOW(), NOW())
ON CONFLICT DO NOTHING;

-- 5. OPORTUNIDADES CRM (pipeline de expansao)
INSERT INTO opportunities (id, title, contact_name, contact_email, company_name, stage, priority, value, probability, is_active, description, lead_id, expected_close_date, created_at, updated_at)
VALUES
(gen_random_uuid(), 'Expansao Portaria 24h - Life Centro', 'Sindico Life Centro', 'lifecentro@conectamais.pro', 'CONDOMINIO LIFE CENTRO', 'proposal', 'high', 20000.00, 60, true, 'Cliente atual CFTV R$1.500. Potencial expansao para portaria 24h.', (SELECT id FROM leads WHERE name = 'Life Centro' LIMIT 1), '2026-05-01', NOW(), NOW()),
(gen_random_uuid(), 'Portaria + CFTV - Parise Village', 'Sindico Parise Village', 'parisevillage@conectamais.pro', 'CONDOMINIO RESIDENCIAL PARISE VILLAGE', 'qualification', 'medium', 15000.00, 50, true, 'Cliente atual CFTV R$1.700. Interesse em portaria.', (SELECT id FROM leads WHERE name = 'Parise Village' LIMIT 1), '2026-06-01', NOW(), NOW()),
(gen_random_uuid(), 'Portaria Remota - Green Hills', 'Sindico Green Hills', 'greenhills@conectamais.pro', 'CONDOMINIO RESIDENCIAL GREEN HILLS', 'qualification', 'medium', 10000.00, 40, true, 'Cliente atual CFTV R$500. Potencial portaria remota.', (SELECT id FROM leads WHERE name = 'Green Hills' LIMIT 1), '2026-07-01', NOW(), NOW()),
(gen_random_uuid(), 'Upgrade Seg. Eletronica - Gelain', 'Sindico Gelain', 'gelain@conectamais.pro', 'CONDOMINIO PARQUE RESIDENCIAL GELAIN', 'negotiation', 'high', 10000.00, 70, true, 'Cliente atual R$6.000 seg eletronica. Interesse em portaria remota integrada.', (SELECT id FROM leads WHERE name = 'Gelain' LIMIT 1), '2026-04-15', NOW(), NOW()),
(gen_random_uuid(), 'Jardinagem - Mirante das Flores', 'Sindico Mirante', 'miranteflores@conectamais.pro', 'CONDOMINIO MIRANTE DAS FLORES', 'proposal', 'low', 8000.00, 45, true, 'Orcamento jardinagem solicitado pelo sindico.', (SELECT id FROM leads WHERE name = 'Mirante das Flores' LIMIT 1), '2026-05-15', NOW(), NOW())
ON CONFLICT DO NOTHING;
