-- =============================================================================
-- SEED DATA: Bidding Module - Conecta PRO
-- Empresa: Jordan Santos de Jesus Ltda (CNPJ 35.710.481/0001-03)
-- Manaus-AM | Seguranca Patrimonial
-- Idempotente: usa ON CONFLICT ou verifica existencia
-- =============================================================================

BEGIN;

-- =====================================================
-- FIXED UUIDs for referential integrity
-- =====================================================
-- Tenders
-- t1: 11111111-aaaa-bbbb-cccc-000000000001  (DRAFT)
-- t2: 11111111-aaaa-bbbb-cccc-000000000002  (ANALYZING)
-- t3: 11111111-aaaa-bbbb-cccc-000000000003  (DECIDED_GO)
-- t4: 11111111-aaaa-bbbb-cccc-000000000004  (PROPOSAL_READY)
-- t5: 11111111-aaaa-bbbb-cccc-000000000005  (IN_DISPUTE)
-- t6: 11111111-aaaa-bbbb-cccc-000000000006  (WON)
-- t7: 11111111-aaaa-bbbb-cccc-000000000007  (WON)
-- t8: 11111111-aaaa-bbbb-cccc-000000000008  (WON)
-- t9: 11111111-aaaa-bbbb-cccc-000000000009  (LOST)
-- t10:11111111-aaaa-bbbb-cccc-000000000010  (LOST)

-- Proposals
-- p1: 22222222-aaaa-bbbb-cccc-000000000001
-- p2: 22222222-aaaa-bbbb-cccc-000000000002
-- p3: 22222222-aaaa-bbbb-cccc-000000000003
-- p4: 22222222-aaaa-bbbb-cccc-000000000004
-- p5: 22222222-aaaa-bbbb-cccc-000000000005

-- Contracts
-- c1: 33333333-aaaa-bbbb-cccc-000000000001
-- c2: 33333333-aaaa-bbbb-cccc-000000000002
-- c3: 33333333-aaaa-bbbb-cccc-000000000003

-- Analyses
-- a1-a5: 44444444-aaaa-bbbb-cccc-00000000000X

-- Assessments
-- as1-as5: 55555555-aaaa-bbbb-cccc-00000000000X

-- =====================================================
-- 1. bidding_tenders (10 records)
-- =====================================================
INSERT INTO bidding_tenders (id, numero, numero_processo, ano, orgao_cnpj, orgao_nome, orgao_uf, orgao_municipio, unidade_gestora, modalidade, criterio_julgamento, tipo_contratacao, objeto, objeto_resumido, valor_estimado, valor_homologado, data_publicacao, data_abertura, data_encerramento_propostas, status, ativo, participando, interesse, segmento, tags, fonte, created_at)
VALUES
-- T1: DRAFT - Prefeitura de Manaus
('11111111-aaaa-bbbb-cccc-000000000001', 'PE-001/2026', '2026.001.PMM', 2026,
 '04.312.401/0001-28', 'Prefeitura Municipal de Manaus', 'AM', 'Manaus',
 'Secretaria Municipal de Seguranca', 'pregao_eletronico', 'menor_preco', 'servico_continuado',
 'Contratacao de empresa especializada na prestacao de servicos de vigilancia patrimonial armada e desarmada para as unidades administrativas da Prefeitura Municipal de Manaus, com fornecimento de mao de obra, uniformes, equipamentos e materiais necessarios.',
 'Vigilancia patrimonial armada/desarmada - Prefeitura Manaus',
 2500000.00, NULL,
 '2026-03-01 10:00:00', '2026-03-20 09:00:00', '2026-03-19 18:00:00',
 'draft', true, false, true, 'vigilancia_patrimonial',
 '["vigilancia", "armada", "desarmada", "prefeitura"]', 'pncp', NOW()),

-- T2: ANALYZING - Governo do AM
('11111111-aaaa-bbbb-cccc-000000000002', 'PE-015/2026', '2026.015.SEAP', 2026,
 '04.312.401/0001-28', 'Governo do Estado do Amazonas - SEAP', 'AM', 'Manaus',
 'Secretaria de Estado de Administracao e Gestao', 'pregao_eletronico', 'menor_preco', 'servico_continuado',
 'Prestacao de servicos de portaria e recepcao para os predios do Governo do Estado do Amazonas, incluindo controle de acesso, monitoramento de CFTV e rondas perimetrais.',
 'Portaria e recepcao - Governo AM',
 1800000.00, NULL,
 '2026-02-25 08:00:00', '2026-03-15 09:00:00', '2026-03-14 18:00:00',
 'analyzing', true, true, true, 'portaria',
 '["portaria", "recepcao", "cftv", "governo"]', 'pncp', NOW()),

-- T3: DECIDED_GO - TRT-11
('11111111-aaaa-bbbb-cccc-000000000003', 'PE-003/2026', '2026.003.TRT11', 2026,
 '04.539.504/0001-07', 'Tribunal Regional do Trabalho da 11a Regiao', 'AM', 'Manaus',
 'Secao de Licitacoes e Contratos', 'pregao_eletronico', 'menor_preco', 'servico_continuado',
 'Contratacao de empresa para prestacao de servicos de seguranca eletronica, incluindo instalacao, manutencao e monitoramento 24h de sistemas de alarme, CFTV e controle de acesso para o Forum Trabalhista de Manaus.',
 'Seguranca eletronica e CFTV - TRT-11',
 450000.00, NULL,
 '2026-02-15 10:00:00', '2026-03-10 09:00:00', '2026-03-09 18:00:00',
 'decided_go', true, true, true, 'seguranca_eletronica',
 '["eletronica", "cftv", "alarme", "monitoramento", "tribunal"]', 'comprasnet', NOW()),

-- T4: PROPOSAL_READY - TRE-AM
('11111111-aaaa-bbbb-cccc-000000000004', 'PE-008/2026', '2026.008.TREAM', 2026,
 '04.284.951/0001-57', 'Tribunal Regional Eleitoral do Amazonas', 'AM', 'Manaus',
 'Coordenadoria de Material e Patrimonio', 'pregao_eletronico', 'menor_preco', 'servico_continuado',
 'Contratacao de servicos de vigilancia patrimonial armada para as sedes do TRE-AM em Manaus e interiorizacao para 10 zonas eleitorais no interior do Amazonas.',
 'Vigilancia armada TRE-AM capital e interior',
 3200000.00, NULL,
 '2026-02-10 10:00:00', '2026-03-05 09:00:00', '2026-03-04 18:00:00',
 'proposal_ready', true, true, true, 'vigilancia_patrimonial',
 '["vigilancia", "armada", "interior", "eleitoral"]', 'comprasnet', NOW()),

-- T5: IN_DISPUTE - INSS Manaus
('11111111-aaaa-bbbb-cccc-000000000005', 'PE-012/2026', '2026.012.INSS', 2026,
 '29.979.036/0057-45', 'Instituto Nacional do Seguro Social - GEX Manaus', 'AM', 'Manaus',
 'Servico de Administracao', 'pregao_eletronico', 'menor_preco', 'servico_continuado',
 'Prestacao de servicos de vigilancia patrimonial armada e servicos de portaria para as Agencias da Previdencia Social em Manaus e Regiao Metropolitana.',
 'Vigilancia e portaria - INSS Manaus',
 1200000.00, NULL,
 '2026-02-01 10:00:00', '2026-02-28 09:00:00', '2026-02-27 18:00:00',
 'in_dispute', true, true, true, 'vigilancia_patrimonial',
 '["vigilancia", "portaria", "inss", "previdencia"]', 'comprasnet', NOW()),

-- T6: WON - SUFRAMA
('11111111-aaaa-bbbb-cccc-000000000006', 'PE-022/2025', '2025.022.SUFRAMA', 2025,
 '04.407.029/0001-43', 'Superintendencia da Zona Franca de Manaus - SUFRAMA', 'AM', 'Manaus',
 'Coordenacao-Geral de Administracao', 'pregao_eletronico', 'menor_preco', 'servico_continuado',
 'Contratacao de empresa para prestacao de servicos de monitoramento eletronico 24h, manutencao preventiva e corretiva de sistemas de CFTV, alarme e controle de acesso nas dependencias da SUFRAMA.',
 'Monitoramento eletronico 24h - SUFRAMA',
 380000.00, 355000.00,
 '2025-10-15 10:00:00', '2025-11-10 09:00:00', '2025-11-09 18:00:00',
 'won', true, true, true, 'seguranca_eletronica',
 '["monitoramento", "cftv", "alarme", "suframa"]', 'comprasnet', NOW() - INTERVAL '120 days'),

-- T7: WON - Camara Municipal
('11111111-aaaa-bbbb-cccc-000000000007', 'CC-002/2025', '2025.002.CMM', 2025,
 '07.846.498/0001-90', 'Camara Municipal de Manaus', 'AM', 'Manaus',
 'Diretoria Administrativa', 'concorrencia', 'menor_preco', 'servico_continuado',
 'Contratacao de empresa especializada em vigilancia patrimonial armada e desarmada para a sede e anexos da Camara Municipal de Manaus, incluindo postos 24h e postos diurnos 12x36.',
 'Vigilancia patrimonial - Camara Municipal Manaus',
 1500000.00, 1420000.00,
 '2025-08-20 10:00:00', '2025-09-25 09:00:00', '2025-09-24 18:00:00',
 'won', true, true, true, 'vigilancia_patrimonial',
 '["vigilancia", "armada", "desarmada", "camara", "legislativo"]', 'pncp', NOW() - INTERVAL '180 days'),

-- T8: WON - SEAD/AM
('11111111-aaaa-bbbb-cccc-000000000008', 'TP-005/2025', '2025.005.SEAD', 2025,
 '04.312.401/0001-28', 'Secretaria de Estado de Administracao - SEAD/AM', 'AM', 'Manaus',
 'Gerencia de Licitacoes', 'tomada_precos', 'menor_preco', 'servico_continuado',
 'Contratacao de servicos de alarme monitorado para 15 unidades da SEAD distribuidas em Manaus, com central de monitoramento 24h, resposta tatica e manutencao preventiva mensal.',
 'Alarme monitorado 15 unidades - SEAD/AM',
 280000.00, 265000.00,
 '2025-11-01 10:00:00', '2025-12-05 09:00:00', '2025-12-04 18:00:00',
 'won', true, true, true, 'alarme_monitorado',
 '["alarme", "monitoramento", "resposta_tatica", "sead"]', 'ecompras_am', NOW() - INTERVAL '100 days'),

-- T9: LOST - UEA
('11111111-aaaa-bbbb-cccc-000000000009', 'PE-030/2025', '2025.030.UEA', 2025,
 '04.280.196/0001-76', 'Universidade do Estado do Amazonas - UEA', 'AM', 'Manaus',
 'Diretoria de Licitacoes', 'pregao_eletronico', 'menor_preco', 'servico_continuado',
 'Prestacao de servicos de vigilancia patrimonial armada para os campi da Universidade do Estado do Amazonas em Manaus, com 20 postos 24h.',
 'Vigilancia armada 20 postos - UEA',
 4800000.00, 4200000.00,
 '2025-09-10 10:00:00', '2025-10-08 09:00:00', '2025-10-07 18:00:00',
 'lost', true, true, true, 'vigilancia_patrimonial',
 '["vigilancia", "armada", "universidade", "campus"]', 'pncp', NOW() - INTERVAL '150 days'),

-- T10: LOST - DETRAN/AM
('11111111-aaaa-bbbb-cccc-000000000010', 'PE-045/2025', '2025.045.DETRAN', 2025,
 '04.312.401/0003-90', 'Departamento Estadual de Transito do Amazonas - DETRAN/AM', 'AM', 'Manaus',
 'Gerencia de Administracao', 'pregao_eletronico', 'menor_preco', 'servico_continuado',
 'Contratacao de empresa para seguranca eletronica e patrimonial para sede e postos de atendimento do DETRAN/AM, incluindo CFTV, controle de acesso biometrico e portaria.',
 'Seguranca eletronica e patrimonial - DETRAN/AM',
 950000.00, 880000.00,
 '2025-07-20 10:00:00', '2025-08-18 09:00:00', '2025-08-17 18:00:00',
 'lost', true, true, true, 'seguranca_eletronica',
 '["eletronica", "cftv", "biometria", "portaria", "detran"]', 'ecompras_am', NOW() - INTERVAL '200 days')
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 2. bidding_opportunities (20 records)
-- =====================================================
INSERT INTO bidding_opportunities (id, portal, portal_id, objeto, valor_estimado, modalidade, orgao_nome, orgao_cnpj, uf, municipio, data_publicacao, data_abertura, data_encerramento, url_edital, url_portal, status, relevancia_score, keywords_matched, created_at)
VALUES
-- PNCP opportunities
('aaaaaaaa-0001-0001-0001-000000000001', 'PNCP', 'PNCP-2026-001',
 'Prestacao de servicos de vigilancia patrimonial armada para edificios publicos municipais',
 1200000.00, 'pregao_eletronico', 'Prefeitura de Manaus', '04312401000128', 'AM', 'Manaus',
 '2026-03-10 08:00:00', '2026-03-25 09:00:00', '2026-03-24 18:00:00',
 'https://pncp.gov.br/editais/PNCP-2026-001', 'https://pncp.gov.br/app/editais/PNCP-2026-001',
 'nova', 0.92, '["vigilancia", "patrimonial", "armada"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000002', 'PNCP', 'PNCP-2026-002',
 'Servicos de monitoramento eletronico e manutencao de CFTV para unidades de saude',
 450000.00, 'pregao_eletronico', 'Secretaria Municipal de Saude - SEMSA', '04312401000128', 'AM', 'Manaus',
 '2026-03-08 10:00:00', '2026-03-22 09:00:00', '2026-03-21 18:00:00',
 'https://pncp.gov.br/editais/PNCP-2026-002', 'https://pncp.gov.br/app/editais/PNCP-2026-002',
 'nova', 0.85, '["monitoramento", "eletronico", "cftv"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000003', 'PNCP', 'PNCP-2026-003',
 'Contratacao de servicos de portaria e controle de acesso para predios do Poder Judiciario',
 800000.00, 'pregao_eletronico', 'Tribunal de Justica do Amazonas', '04539504000107', 'AM', 'Manaus',
 '2026-03-05 10:00:00', '2026-03-20 09:00:00', '2026-03-19 18:00:00',
 'https://pncp.gov.br/editais/PNCP-2026-003', 'https://pncp.gov.br/app/editais/PNCP-2026-003',
 'analisando', 0.78, '["portaria", "controle_acesso"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000004', 'PNCP', 'PNCP-2026-004',
 'Aquisicao de material de limpeza e higiene para escolas municipais',
 320000.00, 'pregao_eletronico', 'Secretaria Municipal de Educacao - SEMED', '04312401000128', 'AM', 'Manaus',
 '2026-03-07 10:00:00', '2026-03-18 09:00:00', '2026-03-17 18:00:00',
 'https://pncp.gov.br/editais/PNCP-2026-004', 'https://pncp.gov.br/app/editais/PNCP-2026-004',
 'descartada', 0.15, '["limpeza", "material"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000005', 'PNCP', 'PNCP-2026-005',
 'Servicos de seguranca eletronica com instalacao de sistemas de alarme para postos de saude',
 280000.00, 'pregao_eletronico', 'Prefeitura de Parintins', '04312401000290', 'AM', 'Parintins',
 '2026-03-06 08:00:00', '2026-03-19 09:00:00', '2026-03-18 18:00:00',
 'https://pncp.gov.br/editais/PNCP-2026-005', 'https://pncp.gov.br/app/editais/PNCP-2026-005',
 'nova', 0.72, '["seguranca", "eletronica", "alarme"]', NOW()),

-- COMPRASNET opportunities
('aaaaaaaa-0001-0001-0001-000000000006', 'COMPRASNET', 'CG-2026-101',
 'Vigilancia patrimonial armada e desarmada para instalacoes militares do CMA',
 5000000.00, 'pregao_eletronico', 'Comando Militar da Amazonia', '00394452000136', 'AM', 'Manaus',
 '2026-03-09 10:00:00', '2026-03-28 09:00:00', '2026-03-27 18:00:00',
 'https://comprasnet.gov.br/editais/CG-2026-101', 'https://comprasnet.gov.br/pregao/CG-2026-101',
 'nova', 0.95, '["vigilancia", "patrimonial", "armada", "desarmada", "militar"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000007', 'COMPRASNET', 'CG-2026-102',
 'Servicos de portaria e recepcao para predios da Receita Federal em Manaus',
 650000.00, 'pregao_eletronico', 'Receita Federal do Brasil - DRF Manaus', '00394460035160', 'AM', 'Manaus',
 '2026-03-04 10:00:00', '2026-03-18 09:00:00', '2026-03-17 18:00:00',
 'https://comprasnet.gov.br/editais/CG-2026-102', 'https://comprasnet.gov.br/pregao/CG-2026-102',
 'analisando', 0.80, '["portaria", "recepcao", "receita_federal"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000008', 'COMPRASNET', 'CG-2026-103',
 'Contratacao de servicos de CFTV e monitoramento eletronico para INPA',
 180000.00, 'pregao_eletronico', 'Instituto Nacional de Pesquisas da Amazonia - INPA', '04280196000176', 'AM', 'Manaus',
 '2026-03-03 10:00:00', '2026-03-17 09:00:00', '2026-03-16 18:00:00',
 'https://comprasnet.gov.br/editais/CG-2026-103', 'https://comprasnet.gov.br/pregao/CG-2026-103',
 'convertida', 0.88, '["cftv", "monitoramento", "eletronico"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000009', 'COMPRASNET', 'CG-2026-104',
 'Fornecimento de refeicoes transportadas para hospitais federais',
 2100000.00, 'pregao_eletronico', 'Hospital Universitario Getulio Vargas', '04280196000176', 'AM', 'Manaus',
 '2026-03-02 10:00:00', '2026-03-15 09:00:00', '2026-03-14 18:00:00',
 'https://comprasnet.gov.br/editais/CG-2026-104', 'https://comprasnet.gov.br/pregao/CG-2026-104',
 'descartada', 0.10, '["refeicoes"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000010', 'COMPRASNET', 'CG-2026-105',
 'Vigilancia patrimonial desarmada com ronda motorizada para agencias do IBGE no Amazonas',
 720000.00, 'pregao_eletronico', 'Instituto Brasileiro de Geografia e Estatistica - IBGE', '33787094000140', 'AM', 'Manaus',
 '2026-03-11 10:00:00', '2026-03-26 09:00:00', '2026-03-25 18:00:00',
 'https://comprasnet.gov.br/editais/CG-2026-105', 'https://comprasnet.gov.br/pregao/CG-2026-105',
 'nova', 0.83, '["vigilancia", "desarmada", "ronda"]', NOW()),

-- LICITACOES_E opportunities
('aaaaaaaa-0001-0001-0001-000000000011', 'LICITACOES_E', 'LE-2026-201',
 'Servicos de seguranca patrimonial armada para unidades do SENAI-AM',
 900000.00, 'pregao_eletronico', 'SENAI - Departamento Regional do Amazonas', '03774688000173', 'AM', 'Manaus',
 '2026-03-08 10:00:00', '2026-03-23 09:00:00', '2026-03-22 18:00:00',
 'https://licitacoes-e.com.br/editais/LE-2026-201', 'https://licitacoes-e.com.br/aop/LE-2026-201',
 'nova', 0.87, '["seguranca", "patrimonial", "armada"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000012', 'LICITACOES_E', 'LE-2026-202',
 'Instalacao e manutencao de sistemas de alarme monitorado para agencias bancarias',
 350000.00, 'pregao_eletronico', 'Banco da Amazonia S.A. - BASA', '04902979000144', 'AM', 'Manaus',
 '2026-03-07 10:00:00', '2026-03-21 09:00:00', '2026-03-20 18:00:00',
 'https://licitacoes-e.com.br/editais/LE-2026-202', 'https://licitacoes-e.com.br/aop/LE-2026-202',
 'analisando', 0.75, '["alarme", "monitorado", "banco"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000013', 'LICITACOES_E', 'LE-2026-203',
 'Contratacao de empresa de TI para desenvolvimento de sistema web',
 500000.00, 'pregao_eletronico', 'SESI - Departamento Regional do Amazonas', '03774688000173', 'AM', 'Manaus',
 '2026-03-06 10:00:00', '2026-03-20 09:00:00', '2026-03-19 18:00:00',
 'https://licitacoes-e.com.br/editais/LE-2026-203', 'https://licitacoes-e.com.br/aop/LE-2026-203',
 'descartada', 0.08, '["TI", "sistema"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000014', 'LICITACOES_E', 'LE-2026-204',
 'Portaria e controle de acesso para condominio empresarial do Distrito Industrial',
 420000.00, 'pregao_eletronico', 'Condominio Empresarial do PIM', '04407029000143', 'AM', 'Manaus',
 '2026-03-05 10:00:00', '2026-03-19 09:00:00', '2026-03-18 18:00:00',
 'https://licitacoes-e.com.br/editais/LE-2026-204', 'https://licitacoes-e.com.br/aop/LE-2026-204',
 'nova', 0.70, '["portaria", "controle_acesso", "industrial"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000015', 'LICITACOES_E', 'LE-2026-205',
 'Servicos de vigilancia patrimonial para shopping center',
 1100000.00, 'concorrencia', 'Manauara Shopping', '04312401000290', 'AM', 'Manaus',
 '2026-03-04 10:00:00', '2026-03-25 09:00:00', '2026-03-24 18:00:00',
 'https://licitacoes-e.com.br/editais/LE-2026-205', 'https://licitacoes-e.com.br/aop/LE-2026-205',
 'nova', 0.65, '["vigilancia", "patrimonial", "shopping"]', NOW()),

-- ECOMPRAS_AM opportunities
('aaaaaaaa-0001-0001-0001-000000000016', 'ECOMPRAS_AM', 'EAM-2026-301',
 'Seguranca eletronica com monitoramento remoto para escolas estaduais da SEDUC-AM',
 1500000.00, 'pregao_eletronico', 'Secretaria de Estado de Educacao - SEDUC/AM', '04312401000128', 'AM', 'Manaus',
 '2026-03-09 10:00:00', '2026-03-24 09:00:00', '2026-03-23 18:00:00',
 'https://ecompras.am.gov.br/editais/EAM-2026-301', 'https://ecompras.am.gov.br/pregao/EAM-2026-301',
 'nova', 0.90, '["seguranca", "eletronica", "monitoramento", "escolas"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000017', 'ECOMPRAS_AM', 'EAM-2026-302',
 'Servicos de vigilancia patrimonial armada para unidades da SSP-AM',
 2800000.00, 'pregao_eletronico', 'Secretaria de Seguranca Publica do Amazonas', '04312401000128', 'AM', 'Manaus',
 '2026-03-10 10:00:00', '2026-03-27 09:00:00', '2026-03-26 18:00:00',
 'https://ecompras.am.gov.br/editais/EAM-2026-302', 'https://ecompras.am.gov.br/pregao/EAM-2026-302',
 'analisando', 0.93, '["vigilancia", "armada", "seguranca_publica"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000018', 'ECOMPRAS_AM', 'EAM-2026-303',
 'Manutencao predial e servicos gerais para predios do Estado',
 680000.00, 'pregao_eletronico', 'SEAD - Secretaria de Administracao', '04312401000128', 'AM', 'Manaus',
 '2026-03-08 10:00:00', '2026-03-22 09:00:00', '2026-03-21 18:00:00',
 'https://ecompras.am.gov.br/editais/EAM-2026-303', 'https://ecompras.am.gov.br/pregao/EAM-2026-303',
 'descartada', 0.30, '["manutencao", "predial"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000019', 'ECOMPRAS_AM', 'EAM-2026-304',
 'Contratacao de empresa para portaria remota com tecnologia IP para unidades da SEPLAN',
 220000.00, 'pregao_eletronico', 'Secretaria de Estado de Planejamento - SEPLAN/AM', '04312401000128', 'AM', 'Manaus',
 '2026-03-11 10:00:00', '2026-03-26 09:00:00', '2026-03-25 18:00:00',
 'https://ecompras.am.gov.br/editais/EAM-2026-304', 'https://ecompras.am.gov.br/pregao/EAM-2026-304',
 'nova', 0.82, '["portaria", "remota", "tecnologia"]', NOW()),

('aaaaaaaa-0001-0001-0001-000000000020', 'ECOMPRAS_AM', 'EAM-2026-305',
 'Servicos de ronda motorizada e vigilancia noturna para conjuntos habitacionais da SUHAB',
 380000.00, 'pregao_eletronico', 'Superintendencia de Habitacao do Amazonas - SUHAB', '04312401000128', 'AM', 'Manaus',
 '2026-03-12 10:00:00', '2026-03-28 09:00:00', '2026-03-27 18:00:00',
 'https://ecompras.am.gov.br/editais/EAM-2026-305', 'https://ecompras.am.gov.br/pregao/EAM-2026-305',
 'nova', 0.77, '["ronda", "motorizada", "vigilancia", "noturna"]', NOW())
ON CONFLICT (portal, portal_id) DO NOTHING;


-- =====================================================
-- 3. bidding_proposals (5 records)
-- =====================================================
INSERT INTO bidding_proposals (id, tender_id, numero, versao, valor_total, valor_unitario, desconto_percentual, bdi_percentual, bdi_detalhamento, encargos_sociais, encargos_detalhamento, status, ativo, posicao_classificacao, valor_lance_final, data_envio, data_resultado, observacoes, justificativa_preco, created_at)
VALUES
-- Proposal for T4 (PROPOSAL_READY - TRE-AM)
('22222222-aaaa-bbbb-cccc-000000000001', '11111111-aaaa-bbbb-cccc-000000000004',
 'PROP-004/2026', 2, 2980000.00, NULL, 6.88, 22.50,
 '{"administracao_central": 5.0, "lucro": 7.5, "despesas_financeiras": 1.2, "seguros": 3.5, "tributos": 5.3}',
 68.50, '{"inss": 20.0, "fgts": 8.0, "13_salario": 8.33, "ferias": 11.11, "provisoes": 21.06}',
 'submitted', true, NULL, NULL,
 '2026-03-04 16:30:00', NULL,
 'Proposta revisada v2 com ajuste nos encargos sociais conforme CCT 2026.',
 'Precos baseados na CCT SINDESP/AM 2026 e painel de precos PNCP.',
 NOW()),

-- Proposal for T5 (IN_DISPUTE - INSS)
('22222222-aaaa-bbbb-cccc-000000000002', '11111111-aaaa-bbbb-cccc-000000000005',
 'PROP-005/2026', 1, 1150000.00, NULL, 4.17, 24.00,
 '{"administracao_central": 5.5, "lucro": 8.0, "despesas_financeiras": 1.0, "seguros": 3.8, "tributos": 5.7}',
 70.20, '{"inss": 20.0, "fgts": 8.0, "13_salario": 8.33, "ferias": 11.11, "provisoes": 22.76}',
 'in_dispute', true, 2, 1120000.00,
 '2026-02-27 15:00:00', NULL,
 'Em fase de lances. Posicao atual: 2o lugar.',
 'Composicao de custos conforme IN SEGES/ME n. 65/2021 e CCT SINDESP/AM.',
 NOW()),

-- Proposal for T6 (WON - SUFRAMA)
('22222222-aaaa-bbbb-cccc-000000000003', '11111111-aaaa-bbbb-cccc-000000000006',
 'PROP-022/2025', 1, 360000.00, 30000.00, 5.26, 20.00,
 '{"administracao_central": 4.5, "lucro": 6.0, "despesas_financeiras": 0.8, "seguros": 3.2, "tributos": 5.5}',
 65.80, '{"inss": 20.0, "fgts": 8.0, "13_salario": 8.33, "ferias": 11.11, "provisoes": 18.36}',
 'won', true, 1, 355000.00,
 '2025-11-09 14:00:00', '2025-11-15 10:00:00',
 'Vencedora apos fase de lances. Contrato em execucao.',
 'Preco referenciado no painel de precos e contratos similares no PNCP.',
 NOW() - INTERVAL '120 days'),

-- Proposal for T7 (WON - Camara)
('22222222-aaaa-bbbb-cccc-000000000004', '11111111-aaaa-bbbb-cccc-000000000007',
 'PROP-002/2025', 1, 1450000.00, NULL, 3.33, 23.00,
 '{"administracao_central": 5.2, "lucro": 7.0, "despesas_financeiras": 1.1, "seguros": 3.5, "tributos": 6.2}',
 69.00, '{"inss": 20.0, "fgts": 8.0, "13_salario": 8.33, "ferias": 11.11, "provisoes": 21.56}',
 'won', true, 1, 1420000.00,
 '2025-09-24 16:00:00', '2025-10-02 10:00:00',
 'Vencedora. Contrato assinado em 15/10/2025.',
 'Custos baseados na planilha de custos da IN 05/2017 e CCT regional.',
 NOW() - INTERVAL '180 days'),

-- Proposal for T9 (LOST - UEA)
('22222222-aaaa-bbbb-cccc-000000000005', '11111111-aaaa-bbbb-cccc-000000000009',
 'PROP-030/2025', 1, 4650000.00, NULL, 3.13, 25.00,
 '{"administracao_central": 5.8, "lucro": 8.5, "despesas_financeiras": 1.3, "seguros": 3.7, "tributos": 5.7}',
 71.00, '{"inss": 20.0, "fgts": 8.0, "13_salario": 8.33, "ferias": 11.11, "provisoes": 23.56}',
 'lost', true, 3, 4500000.00,
 '2025-10-07 15:30:00', '2025-10-15 10:00:00',
 'Classificada em 3o lugar. Diferenca de R$300k para o 1o colocado.',
 'Preco acima do mercado devido ao custo de interiorizacao (deslocamento para campi do interior).',
 NOW() - INTERVAL '150 days')
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 4. bidding_proposal_items (10 records for proposals p1, p3)
-- =====================================================
INSERT INTO bidding_proposal_items (id, proposal_id, numero_item, codigo, descricao, unidade, quantidade, valor_unitario, valor_total, custo_direto, custo_indireto, margem, composicao, created_at)
VALUES
-- Items for P1 (TRE-AM)
('66666666-aaaa-bbbb-cccc-000000000001', '22222222-aaaa-bbbb-cccc-000000000001',
 1, 'VIG-ARM-24H', 'Posto de vigilancia armada 24h (escala 12x36) - Capital', 'posto/mes', 8.0000, 18500.0000, 148000.00, 12800.00, 2960.00, 2740.00,
 '{"salario_base": 2200.00, "adicional_noturno": 440.00, "periculosidade": 660.00, "uniformes": 180.00, "equipamentos": 320.00}',
 NOW()),
('66666666-aaaa-bbbb-cccc-000000000002', '22222222-aaaa-bbbb-cccc-000000000001',
 2, 'VIG-ARM-12H', 'Posto de vigilancia armada diurno 12h - Capital', 'posto/mes', 4.0000, 10200.0000, 40800.00, 7100.00, 1640.00, 1460.00,
 '{"salario_base": 2200.00, "periculosidade": 660.00, "uniformes": 180.00, "equipamentos": 320.00}',
 NOW()),
('66666666-aaaa-bbbb-cccc-000000000003', '22222222-aaaa-bbbb-cccc-000000000001',
 3, 'VIG-ARM-INT', 'Posto de vigilancia armada 24h - Interior (zonas eleitorais)', 'posto/mes', 10.0000, 22800.0000, 228000.00, 15600.00, 3600.00, 3600.00,
 '{"salario_base": 2200.00, "adicional_noturno": 440.00, "periculosidade": 660.00, "adicional_interio": 550.00, "deslocamento": 1200.00}',
 NOW()),
('66666666-aaaa-bbbb-cccc-000000000004', '22222222-aaaa-bbbb-cccc-000000000001',
 4, 'SUP-FIELD', 'Supervisor de campo', 'profissional/mes', 2.0000, 8500.0000, 17000.00, 5800.00, 1350.00, 1350.00,
 '{"salario_base": 3200.00, "periculosidade": 960.00, "uniformes": 180.00, "veiculo": 1200.00}',
 NOW()),
('66666666-aaaa-bbbb-cccc-000000000005', '22222222-aaaa-bbbb-cccc-000000000001',
 5, 'COORD', 'Coordenador de contrato', 'profissional/mes', 1.0000, 12500.0000, 12500.00, 8500.00, 2000.00, 2000.00,
 '{"salario_base": 5000.00, "beneficios": 1500.00, "veiculo": 1500.00}',
 NOW()),

-- Items for P3 (SUFRAMA - seguranca eletronica)
('66666666-aaaa-bbbb-cccc-000000000006', '22222222-aaaa-bbbb-cccc-000000000003',
 1, 'MON-24H', 'Monitoramento eletronico 24h por unidade', 'unidade/mes', 5.0000, 2800.0000, 14000.00, 1800.00, 500.00, 500.00,
 '{"operador_cftv": 1200.00, "software": 300.00, "internet": 200.00, "energia": 100.00}',
 NOW()),
('66666666-aaaa-bbbb-cccc-000000000007', '22222222-aaaa-bbbb-cccc-000000000003',
 2, 'MANUT-PREV', 'Manutencao preventiva mensal de CFTV', 'visita/mes', 5.0000, 1500.0000, 7500.00, 900.00, 300.00, 300.00,
 '{"tecnico": 600.00, "deslocamento": 150.00, "materiais": 150.00}',
 NOW()),
('66666666-aaaa-bbbb-cccc-000000000008', '22222222-aaaa-bbbb-cccc-000000000003',
 3, 'MANUT-CORR', 'Manutencao corretiva de equipamentos (sob demanda)', 'chamado', 12.0000, 450.0000, 5400.00, 280.00, 85.00, 85.00,
 '{"tecnico": 150.00, "pecas_media": 80.00, "deslocamento": 50.00}',
 NOW()),
('66666666-aaaa-bbbb-cccc-000000000009', '22222222-aaaa-bbbb-cccc-000000000003',
 4, 'CTRL-ACESSO', 'Sistema de controle de acesso biometrico por ponto', 'ponto/mes', 8.0000, 350.0000, 2800.00, 220.00, 65.00, 65.00,
 '{"equipamento_locacao": 120.00, "software": 60.00, "suporte": 40.00}',
 NOW()),
('66666666-aaaa-bbbb-cccc-000000000010', '22222222-aaaa-bbbb-cccc-000000000003',
 5, 'RESP-TAT', 'Servico de resposta tatica (pronta resposta a alarmes)', 'mes', 1.0000, 3500.0000, 3500.00, 2200.00, 650.00, 650.00,
 '{"equipe": 1500.00, "veiculo": 400.00, "comunicacao": 200.00, "seguro": 100.00}',
 NOW())
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 5. bidding_public_contracts (3 records)
-- =====================================================
INSERT INTO bidding_public_contracts (id, tender_id, numero_contrato, ano_contrato, objeto, objeto_resumido, orgao_cnpj, orgao_nome, orgao_uf, unidade_gestora, gestor_contrato, fiscal_contrato, valor_contrato, valor_empenhado, valor_executado, valor_pago, saldo_contrato, data_assinatura, data_publicacao, data_vigencia_inicio, data_vigencia_fim, prazo_meses, indice_reajuste, garantia_tipo, garantia_valor, garantia_percentual, garantia_vencimento, status, ativo, created_at)
VALUES
-- Contract from T6 (SUFRAMA)
('33333333-aaaa-bbbb-cccc-000000000001', '11111111-aaaa-bbbb-cccc-000000000006',
 'CT-001/2026', 2026,
 'Prestacao de servicos de monitoramento eletronico 24h, manutencao preventiva e corretiva de CFTV, alarme e controle de acesso - SUFRAMA.',
 'Monitoramento eletronico 24h - SUFRAMA',
 '04.407.029/0001-43', 'Superintendencia da Zona Franca de Manaus - SUFRAMA', 'AM',
 'Coordenacao-Geral de Administracao',
 'Carlos Eduardo Souza Ribeiro', 'Ana Paula Mendes Ferreira',
 355000.00, 355000.00, 88750.00, 59166.67, 266250.00,
 '2025-12-01', '2025-12-05', '2026-01-01', '2026-12-31',
 12, 'igpm', 'caucao', 17750.00, 5.00, '2027-01-31',
 'active', true, NOW() - INTERVAL '100 days'),

-- Contract from T7 (Camara Municipal)
('33333333-aaaa-bbbb-cccc-000000000002', '11111111-aaaa-bbbb-cccc-000000000007',
 'CT-045/2025', 2025,
 'Vigilancia patrimonial armada e desarmada para sede e anexos da Camara Municipal de Manaus, incluindo postos 24h e postos diurnos 12x36.',
 'Vigilancia patrimonial - Camara Municipal Manaus',
 '07.846.498/0001-90', 'Camara Municipal de Manaus', 'AM',
 'Diretoria Administrativa',
 'Roberto Augusto Fonseca Lima', 'Marcia Helena Costa Braga',
 1420000.00, 1420000.00, 591666.67, 473333.34, 828333.33,
 '2025-10-15', '2025-10-20', '2025-11-01', '2026-10-31',
 12, 'ipca', 'seguro_garantia', 71000.00, 5.00, '2026-11-30',
 'active', true, NOW() - INTERVAL '150 days'),

-- Contract from T8 (SEAD - Alarme)
('33333333-aaaa-bbbb-cccc-000000000003', '11111111-aaaa-bbbb-cccc-000000000008',
 'CT-088/2025', 2025,
 'Servicos de alarme monitorado para 15 unidades da SEAD, com central de monitoramento 24h, resposta tatica e manutencao preventiva mensal.',
 'Alarme monitorado 15 unidades - SEAD/AM',
 '04.312.401/0001-28', 'Secretaria de Estado de Administracao - SEAD/AM', 'AM',
 'Gerencia de Licitacoes',
 'Fernando Jose Cavalcante', 'Lucia Maria dos Santos',
 265000.00, 265000.00, 66250.00, 44166.67, 198750.00,
 '2025-12-20', '2025-12-23', '2026-01-01', '2026-12-31',
 12, 'igpm', 'caucao', 13250.00, 5.00, '2027-01-31',
 'active', true, NOW() - INTERVAL '80 days')
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 6. bidding_measurements (6 records - 2 per contract)
-- =====================================================
INSERT INTO bidding_measurements (id, contrato_id, numero_medicao, competencia, tipo, periodo_inicio, periodo_fim, valor_bruto, valor_retencoes, valor_glosas, valor_liquido, retencao_iss, retencao_inss, retencao_irrf, retencao_pis_cofins_csll, status, ativo, data_envio, data_ateste, data_aprovacao, data_pagamento, aprovador_nome, nota_fiscal_numero, nota_fiscal_data, descricao_servicos, created_at)
VALUES
-- Contract 1 (SUFRAMA) - Medicoes
('77777777-aaaa-bbbb-cccc-000000000001', '33333333-aaaa-bbbb-cccc-000000000001',
 1, '2026-01', 'mensal', '2026-01-01', '2026-01-31',
 29583.33, 4290.58, 0.00, 25292.75,
 1479.17, 1183.33, 443.75, 1184.33,
 'paid', true, '2026-02-03', '2026-02-05', '2026-02-07', '2026-02-15',
 'Carlos Eduardo Souza Ribeiro', 'NFS-000152', '2026-02-03',
 'Monitoramento eletronico 24h, 5 unidades; manutencao preventiva realizada; 3 chamados corretivos atendidos.',
 NOW() - INTERVAL '40 days'),

('77777777-aaaa-bbbb-cccc-000000000002', '33333333-aaaa-bbbb-cccc-000000000001',
 2, '2026-02', 'mensal', '2026-02-01', '2026-02-28',
 29583.33, 4290.58, 0.00, 25292.75,
 1479.17, 1183.33, 443.75, 1184.33,
 'approved', true, '2026-03-03', '2026-03-05', '2026-03-07', NULL,
 'Carlos Eduardo Souza Ribeiro', 'NFS-000168', '2026-03-03',
 'Monitoramento eletronico 24h, 5 unidades; manutencao preventiva OK; 2 chamados corretivos.',
 NOW() - INTERVAL '10 days'),

-- Contract 2 (Camara) - Medicoes
('77777777-aaaa-bbbb-cccc-000000000003', '33333333-aaaa-bbbb-cccc-000000000002',
 1, '2025-11', 'mensal', '2025-11-01', '2025-11-30',
 118333.33, 17158.33, 0.00, 101175.00,
 5916.67, 4733.33, 1775.00, 4733.33,
 'paid', true, '2025-12-03', '2025-12-05', '2025-12-08', '2025-12-18',
 'Roberto Augusto Fonseca Lima', 'NFS-000098', '2025-12-03',
 'Vigilancia patrimonial armada e desarmada - 12 postos 24h e 6 postos diurnos. Sem ocorrencias graves.',
 NOW() - INTERVAL '100 days'),

('77777777-aaaa-bbbb-cccc-000000000004', '33333333-aaaa-bbbb-cccc-000000000002',
 2, '2025-12', 'mensal', '2025-12-01', '2025-12-31',
 118333.33, 17158.33, 1500.00, 99675.00,
 5916.67, 4733.33, 1775.00, 4733.33,
 'paid', true, '2026-01-03', '2026-01-06', '2026-01-08', '2026-01-20',
 'Roberto Augusto Fonseca Lima', 'NFS-000112', '2026-01-03',
 'Vigilancia patrimonial - Glosa de R$1.500 por atraso em 2 postos no dia 24/12.',
 NOW() - INTERVAL '70 days'),

-- Contract 3 (SEAD) - Medicoes
('77777777-aaaa-bbbb-cccc-000000000005', '33333333-aaaa-bbbb-cccc-000000000003',
 1, '2026-01', 'mensal', '2026-01-01', '2026-01-31',
 22083.33, 3202.08, 0.00, 18881.25,
 1104.17, 883.33, 331.25, 883.33,
 'paid', true, '2026-02-03', '2026-02-04', '2026-02-06', '2026-02-14',
 'Fernando Jose Cavalcante', 'NFS-000155', '2026-02-03',
 'Alarme monitorado 15 unidades; 100% uptime; resposta tatica: 4 acionamentos, tempo medio 12min.',
 NOW() - INTERVAL '40 days'),

('77777777-aaaa-bbbb-cccc-000000000006', '33333333-aaaa-bbbb-cccc-000000000003',
 2, '2026-02', 'mensal', '2026-02-01', '2026-02-28',
 22083.33, 3202.08, 0.00, 18881.25,
 1104.17, 883.33, 331.25, 883.33,
 'submitted', true, '2026-03-03', NULL, NULL, NULL,
 NULL, 'NFS-000170', '2026-03-03',
 'Alarme monitorado 15 unidades; 99.8% uptime (1 falha sensor U07 corrigida em 4h); resposta tatica: 6 acionamentos.',
 NOW() - INTERVAL '10 days')
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 7. bidding_certificates (8 records)
-- =====================================================
INSERT INTO bidding_certificates (id, tipo, nome, codigo_verificacao, cnpj, razao_social, data_emissao, data_validade, situacao, status, ativo, fonte, orgao_emissor, orgao_uf, orgao_url, created_at)
VALUES
-- Valid (future expiry)
('88888888-aaaa-bbbb-cccc-000000000001', 'CND_FEDERAL',
 'Certidao Negativa de Debitos Relativos aos Tributos Federais e a Divida Ativa da Uniao',
 'CNDF-2026-8A3B-C4D5', '35710481000103', 'Jordan Santos de Jesus Ltda',
 '2026-02-15 10:30:00', '2026-08-14 23:59:59',
 'NEGATIVA', 'valid', true, 'manual',
 'Receita Federal do Brasil / PGFN', 'AM', 'https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PJ/Emitir',
 NOW()),

('88888888-aaaa-bbbb-cccc-000000000002', 'FGTS',
 'Certificado de Regularidade do FGTS - CRF',
 'CRF-2026-1234567890', '35710481000103', 'Jordan Santos de Jesus Ltda',
 '2026-03-01 08:00:00', '2026-03-31 23:59:59',
 'REGULAR', 'valid', true, 'manual',
 'Caixa Economica Federal', NULL, 'https://consulta-crf.caixa.gov.br',
 NOW()),

('88888888-aaaa-bbbb-cccc-000000000003', 'CNDT',
 'Certidao Negativa de Debitos Trabalhistas',
 'CNDT-2026-9876543210', '35710481000103', 'Jordan Santos de Jesus Ltda',
 '2026-02-20 14:00:00', '2026-08-19 23:59:59',
 'NEGATIVA', 'valid', true, 'manual',
 'Tribunal Superior do Trabalho', NULL, 'https://www.tst.jus.br/certidao',
 NOW()),

('88888888-aaaa-bbbb-cccc-000000000004', 'SICAF',
 'Registro no SICAF - Nivel VI (completo)',
 'SICAF-2026-UAS-001', '35710481000103', 'Jordan Santos de Jesus Ltda',
 '2026-01-10 09:00:00', '2027-01-10 23:59:59',
 'CREDENCIADO', 'valid', true, 'manual',
 'Ministerio da Gestao e Inovacao', NULL, 'https://sicaf.gov.br',
 NOW()),

-- Expiring soon (15-30 days)
('88888888-aaaa-bbbb-cccc-000000000005', 'CND_ESTADUAL',
 'Certidao Negativa de Debitos Estaduais - SEFAZ/AM',
 'CNDE-2026-AM-5678', '35710481000103', 'Jordan Santos de Jesus Ltda',
 '2025-10-15 10:00:00', '2026-04-12 23:59:59',
 'NEGATIVA', 'expiring', true, 'manual',
 'Secretaria de Estado da Fazenda do Amazonas - SEFAZ/AM', 'AM', 'https://sefaz.am.gov.br',
 NOW()),

('88888888-aaaa-bbbb-cccc-000000000006', 'CND_MUNICIPAL',
 'Certidao Negativa de Tributos Municipais - SEMEF Manaus',
 'CNDM-2026-MNS-3456', '35710481000103', 'Jordan Santos de Jesus Ltda',
 '2025-10-20 11:00:00', '2026-04-05 23:59:59',
 'NEGATIVA', 'expiring', true, 'manual',
 'Secretaria Municipal de Financas e Tecnologia da Informacao - SEMEF', 'AM', 'https://semef.manaus.am.gov.br',
 NOW()),

-- Expired
('88888888-aaaa-bbbb-cccc-000000000007', 'ALVARA',
 'Alvara de Funcionamento - Seguranca Privada',
 'ALV-2025-PF-1234', '35710481000103', 'Jordan Santos de Jesus Ltda',
 '2024-06-01 09:00:00', '2026-02-28 23:59:59',
 'VENCIDA', 'expired', true, 'manual',
 'Policia Federal - Delegacia de Controle de Seguranca Privada', 'AM', 'https://www.gov.br/pf/seguranca-privada',
 NOW()),

('88888888-aaaa-bbbb-cccc-000000000008', 'CERTIFICADO_DIGITAL',
 'Certificado Digital A1 - e-CNPJ',
 'CD-A1-2025-JSJ', '35710481000103', 'Jordan Santos de Jesus Ltda',
 '2025-04-01 10:00:00', '2026-04-01 23:59:59',
 'VALIDO', 'expiring', true, 'manual',
 'Certisign Certificadora Digital S.A.', NULL, 'https://www.certisign.com.br',
 NOW())
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 8. bidding_company_documents (6 records)
-- =====================================================
INSERT INTO bidding_company_documents (id, tipo, nome, descricao, numero, data_emissao, data_validade, status, ativo, orgao_emissor, metadados, created_at)
VALUES
('99999999-aaaa-bbbb-cccc-000000000001', 'CONTRATO_SOCIAL',
 'Contrato Social Consolidado', 'Contrato social com ultima alteracao',
 'JUCEMA-2024-001234', '2024-03-15', NULL,
 'valid', true, 'JUCEMA - Junta Comercial do Estado do Amazonas',
 '{"capital_social": 500000.00, "socios": ["Jordan Santos de Jesus"]}',
 NOW()),

('99999999-aaaa-bbbb-cccc-000000000002', 'AUTORIZACAO_PF',
 'Autorizacao de Funcionamento - Seguranca Privada',
 'Autorizacao da PF para prestacao de servicos de vigilancia patrimonial',
 'DG/DPF-2024-5678', '2024-06-01', '2026-05-31',
 'valid', true, 'Policia Federal - DELESP',
 '{"atividades": ["vigilancia_patrimonial", "seguranca_eletronica", "escolta_armada"]}',
 NOW()),

('99999999-aaaa-bbbb-cccc-000000000003', 'REGISTRO_CREA',
 'Registro CREA-AM (Responsavel Tecnico)',
 'Registro de pessoa juridica no CREA para servicos de engenharia eletrica/eletronica',
 'CREA-AM-2025-PJ-0456', '2025-01-15', '2026-01-14',
 'expired', true, 'CREA-AM',
 '{"responsavel_tecnico": "Eng. Marcos Oliveira", "registro_rt": "CREA-AM-123456"}',
 NOW()),

('99999999-aaaa-bbbb-cccc-000000000004', 'ATESTADO_CAPACIDADE',
 'Atestado de Capacidade Tecnica - Prefeitura Manaus',
 'Atestado referente ao contrato de vigilancia para secretarias municipais (2023-2024)',
 'ACT-PMM-2024-089', '2024-12-20', NULL,
 'valid', true, 'Prefeitura Municipal de Manaus',
 '{"valor_contrato": 1800000.00, "postos": 15, "tipo_servico": "vigilancia_patrimonial_armada", "periodo": "2023-2024"}',
 NOW()),

('99999999-aaaa-bbbb-cccc-000000000005', 'ATESTADO_CAPACIDADE',
 'Atestado de Capacidade Tecnica - TRT-11',
 'Atestado referente a prestacao de servicos de seguranca eletronica',
 'ACT-TRT11-2025-012', '2025-06-15', NULL,
 'valid', true, 'Tribunal Regional do Trabalho da 11a Regiao',
 '{"valor_contrato": 320000.00, "unidades": 3, "tipo_servico": "seguranca_eletronica_cftv", "periodo": "2024-2025"}',
 NOW()),

('99999999-aaaa-bbbb-cccc-000000000006', 'BALANCO_PATRIMONIAL',
 'Balanco Patrimonial e DRE 2025',
 'Demonstracoes contabeis do exercicio 2025 registradas na JUCEMA',
 'BP-2025-JSJ', '2026-02-28', NULL,
 'valid', true, 'JUCEMA / Dominio Sistemas (TOTVS)',
 '{"ativo_total": 2800000.00, "patrimonio_liquido": 1500000.00, "receita_bruta": 4200000.00, "lucro_liquido": 380000.00, "indice_liquidez_geral": 1.85}',
 NOW())
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 9. bidding_tender_documents (8 records)
-- =====================================================
INSERT INTO bidding_tender_documents (id, tender_id, nome, descricao, tipo, arquivo_nome, arquivo_tamanho, ordem, obrigatorio, created_at)
VALUES
-- Documents for T3 (TRT-11)
('aabbccdd-0001-0001-0001-000000000001', '11111111-aaaa-bbbb-cccc-000000000003',
 'Edital PE-003/2026', 'Edital completo do Pregao Eletronico', 'edital', 'edital_pe003_2026_trt11.pdf', 2450000, 1, true, NOW()),
('aabbccdd-0001-0001-0001-000000000002', '11111111-aaaa-bbbb-cccc-000000000003',
 'Termo de Referencia', 'Termo de referencia com especificacoes tecnicas detalhadas', 'termo_referencia', 'tr_pe003_2026_trt11.pdf', 1800000, 2, true, NOW()),
('aabbccdd-0001-0001-0001-000000000003', '11111111-aaaa-bbbb-cccc-000000000003',
 'Planilha de Custos Estimados', 'Planilha referencial de formacao de precos', 'planilha', 'planilha_custos_pe003_2026.xlsx', 350000, 3, false, NOW()),

-- Documents for T4 (TRE-AM)
('aabbccdd-0001-0001-0001-000000000004', '11111111-aaaa-bbbb-cccc-000000000004',
 'Edital PE-008/2026', 'Edital do pregao para vigilancia armada', 'edital', 'edital_pe008_2026_tream.pdf', 3100000, 1, true, NOW()),
('aabbccdd-0001-0001-0001-000000000005', '11111111-aaaa-bbbb-cccc-000000000004',
 'Termo de Referencia', 'TR com descricao dos postos e escalas', 'termo_referencia', 'tr_pe008_2026_tream.pdf', 2200000, 2, true, NOW()),
('aabbccdd-0001-0001-0001-000000000006', '11111111-aaaa-bbbb-cccc-000000000004',
 'Modelo de Planilha de Custos', 'Modelo obrigatorio de planilha IN 05/2017', 'planilha', 'modelo_planilha_pe008_2026.xlsx', 280000, 3, true, NOW()),

-- Documents for T5 (INSS)
('aabbccdd-0001-0001-0001-000000000007', '11111111-aaaa-bbbb-cccc-000000000005',
 'Edital PE-012/2026', 'Edital com todas as condicoes de participacao', 'edital', 'edital_pe012_2026_inss.pdf', 2800000, 1, true, NOW()),
('aabbccdd-0001-0001-0001-000000000008', '11111111-aaaa-bbbb-cccc-000000000005',
 'Ata de Esclarecimentos', 'Respostas aos pedidos de esclarecimento das licitantes', 'esclarecimento', 'ata_esclarecimentos_pe012.pdf', 420000, 4, false, NOW())
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 10. bidding_analyses (5 records)
-- =====================================================
INSERT INTO bidding_analyses (id, tender_id, objeto_resumido, modalidade_identificada, criterio_julgamento, valor_estimado, requisitos_habilitacao, prazos, red_flags, documentos_necessarios, itens_extraidos, estimativa_esforco_horas, recomendacao_participacao, justificativa_recomendacao, modelo_ia, created_at)
VALUES
-- Analysis for T2 (Governo AM - Portaria)
('44444444-aaaa-bbbb-cccc-000000000001', '11111111-aaaa-bbbb-cccc-000000000002',
 'Portaria e recepcao para predios do Governo do AM',
 'pregao_eletronico', 'menor_preco', 'R$ 1.800.000,00',
 '{"juridica": ["contrato_social", "certidao_jucema"], "fiscal": ["cnd_federal", "cnd_estadual", "cnd_municipal", "fgts", "cndt"], "tecnica": ["atestado_capacidade_tecnica_portaria", "registro_crea"], "economica": ["balanco_patrimonial", "indice_liquidez_1_0"]}',
 '{"abertura": "2026-03-15", "impugnacao": "2026-03-12", "esclarecimentos": "2026-03-13", "prazo_contrato": "12 meses"}',
 '["Exigencia de indice de liquidez >= 1.5 (acima do usual)", "Prazo curto para mobilizacao (15 dias)"]',
 '["CND Federal", "CND Estadual", "CND Municipal", "CRF/FGTS", "CNDT", "Balanco Patrimonial 2025", "Atestado Capacidade Tecnica (min 50% do objeto)", "Autorizacao PF"]',
 '[{"item": 1, "descricao": "Posto de portaria 24h", "quantidade": 10, "unidade": "posto/mes"}, {"item": 2, "descricao": "Posto de recepcao diurno", "quantidade": 8, "unidade": "posto/mes"}]',
 40, 'go',
 'Objeto alinhado com nossas competencias. Valor atrativo com boa margem. Red flags gerenciaveis: liquidez OK (1.85) e capacidade de mobilizacao existente.',
 'claude-sonnet-4-20250514', NOW()),

-- Analysis for T3 (TRT-11 - Seg Eletronica)
('44444444-aaaa-bbbb-cccc-000000000002', '11111111-aaaa-bbbb-cccc-000000000003',
 'Seguranca eletronica e CFTV - Forum Trabalhista Manaus',
 'pregao_eletronico', 'menor_preco', 'R$ 450.000,00',
 '{"juridica": ["contrato_social"], "fiscal": ["cnd_federal", "fgts", "cndt", "sicaf"], "tecnica": ["atestado_capacidade_eletronica", "registro_crea_eletrica"], "economica": ["balanco_patrimonial"]}',
 '{"abertura": "2026-03-10", "impugnacao": "2026-03-07", "vigencia": "12 meses renovaveis ate 5 anos"}',
 '[]',
 '["SICAF nivel VI", "CND Federal", "CRF/FGTS", "CNDT", "Atestado de capacidade tecnica em seg. eletronica", "Registro CREA com RT em engenharia eletrica"]',
 '[{"item": 1, "descricao": "Monitoramento 24h", "quantidade": 1, "unidade": "servico/mes"}, {"item": 2, "descricao": "Manutencao preventiva", "quantidade": 12, "unidade": "visita/ano"}, {"item": 3, "descricao": "Manutencao corretiva", "quantidade": 24, "unidade": "chamado/ano"}]',
 24, 'go',
 'Segmento estrategico (seguranca eletronica). Baixa concorrencia esperada. Temos atestado tecnico do proprio TRT-11. Sem red flags.',
 'claude-sonnet-4-20250514', NOW()),

-- Analysis for T4 (TRE-AM - Vigilancia)
('44444444-aaaa-bbbb-cccc-000000000003', '11111111-aaaa-bbbb-cccc-000000000004',
 'Vigilancia armada TRE-AM capital e interior',
 'pregao_eletronico', 'menor_preco', 'R$ 3.200.000,00',
 '{"juridica": ["contrato_social", "autorizacao_pf"], "fiscal": ["cnd_federal", "cnd_estadual", "cnd_municipal", "fgts", "cndt"], "tecnica": ["atestado_vigilancia_armada_50pct", "autorizacao_pf_armada"], "economica": ["balanco_patrimonial", "capital_social_10pct"]}',
 '{"abertura": "2026-03-05", "impugnacao": "2026-03-02", "mobilizacao": "30 dias", "vigencia": "12 meses"}',
 '["Exigencia de interiorizacao para 10 cidades do AM (custo logistico alto)", "Capital social minimo de 10% do valor estimado (R$320k)", "Necessidade de escritorio regional no interior"]',
 '["Autorizacao PF para vigilancia armada", "CND Federal", "CND Estadual/Municipal", "CRF/FGTS", "CNDT", "Atestados capacidade (min 10 postos armados)", "Balanco Patrimonial", "Capital social >= R$320.000"]',
 '[{"item": 1, "descricao": "Posto vigilancia armada 24h capital", "quantidade": 8, "unidade": "posto/mes"}, {"item": 2, "descricao": "Posto vigilancia armada diurno capital", "quantidade": 4, "unidade": "posto/mes"}, {"item": 3, "descricao": "Posto vigilancia armada 24h interior", "quantidade": 10, "unidade": "posto/mes"}, {"item": 4, "descricao": "Supervisor de campo", "quantidade": 2, "unidade": "profissional/mes"}]',
 60, 'go',
 'Maior licitacao do trimestre. Apesar dos custos com interiorizacao, volume compensa. Capital social OK (PL R$1.5M > R$320k). Interiorizacao e diferencial competitivo.',
 'claude-sonnet-4-20250514', NOW()),

-- Analysis for T5 (INSS - Vigilancia+Portaria)
('44444444-aaaa-bbbb-cccc-000000000004', '11111111-aaaa-bbbb-cccc-000000000005',
 'Vigilancia e portaria INSS Manaus e regiao metropolitana',
 'pregao_eletronico', 'menor_preco', 'R$ 1.200.000,00',
 '{"juridica": ["contrato_social"], "fiscal": ["sicaf_nivel_vi"], "tecnica": ["atestado_vigilancia", "atestado_portaria"], "economica": ["balanco_patrimonial"]}',
 '{"abertura": "2026-02-28", "sessao_publica": "2026-02-28 09:00", "vigencia": "12 meses"}',
 '["SICAF obrigatorio - verificar se todos os niveis estao atualizados"]',
 '["SICAF atualizado (todos os niveis)", "Atestado capacidade vigilancia", "Atestado capacidade portaria", "Autorizacao PF"]',
 '[{"item": 1, "descricao": "Posto vigilancia armada 24h", "quantidade": 4, "unidade": "posto/mes"}, {"item": 2, "descricao": "Posto portaria 12h", "quantidade": 6, "unidade": "posto/mes"}]',
 32, 'go',
 'Objeto combinado (vigilancia + portaria) e nosso forte. INSS e bom pagador. SICAF ja esta atualizado nivel VI.',
 'claude-sonnet-4-20250514', NOW()),

-- Analysis for T1 (Prefeitura - DRAFT, preliminary)
('44444444-aaaa-bbbb-cccc-000000000005', '11111111-aaaa-bbbb-cccc-000000000001',
 'Vigilancia patrimonial armada/desarmada - Prefeitura Manaus',
 'pregao_eletronico', 'menor_preco', 'R$ 2.500.000,00',
 '{"juridica": ["contrato_social"], "fiscal": ["cnd_federal", "cnd_estadual", "cnd_municipal", "fgts", "cndt"], "tecnica": ["atestado_vigilancia_50pct"], "economica": ["balanco_patrimonial", "capital_social_10pct"]}',
 '{"abertura": "2026-03-20", "impugnacao": "2026-03-17"}',
 '["Edital ainda em fase de publicacao - possivel alteracao", "Historico de atrasos no pagamento pela Prefeitura"]',
 '["CND Federal", "CND Estadual", "CND Municipal", "CRF/FGTS", "CNDT", "Balanco 2025", "Atestados", "Autorizacao PF"]',
 '[]',
 20, 'analyze',
 'Valor atrativo mas historico de inadimplencia da Prefeitura preocupa. Aguardar publicacao definitiva do edital para analise completa.',
 'claude-sonnet-4-20250514', NOW())
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 11. bidding_assessments (5 records)
-- =====================================================
INSERT INTO bidding_assessments (id, tender_id, analysis_id, score, scores_detalhados, recomendacao, justificativa, requisitos_nao_atendidos, acoes_necessarias, created_at)
VALUES
('55555555-aaaa-bbbb-cccc-000000000001', '11111111-aaaa-bbbb-cccc-000000000002', '44444444-aaaa-bbbb-cccc-000000000001',
 82.5,
 '{"alinhamento_objeto": 90, "capacidade_tecnica": 85, "capacidade_financeira": 80, "documentacao": 75, "risco": 70, "competitividade": 85}',
 'go',
 'Alta aderencia ao nosso portfolio. Capacidade tecnica comprovada por atestados similares. Documentacao quase completa, faltando apenas renovar CND estadual.',
 '["CND Estadual vencendo em 30 dias - renovar antes da abertura"]',
 '["Renovar CND Estadual SEFAZ/AM", "Preparar planilha de custos conforme IN 05/2017", "Designar equipe de apoio para elaboracao da proposta"]',
 NOW()),

('55555555-aaaa-bbbb-cccc-000000000002', '11111111-aaaa-bbbb-cccc-000000000003', '44444444-aaaa-bbbb-cccc-000000000002',
 91.0,
 '{"alinhamento_objeto": 95, "capacidade_tecnica": 95, "capacidade_financeira": 90, "documentacao": 90, "risco": 80, "competitividade": 95}',
 'go',
 'Excelente oportunidade. Segmento core (seguranca eletronica), atestado do proprio orgao, baixa concorrencia no segmento em Manaus. Score mais alto do trimestre.',
 '[]',
 '["Atualizar proposta tecnica com novas cameras PTZ", "Incluir SLA de 99.9% uptime no termo de referencia"]',
 NOW()),

('55555555-aaaa-bbbb-cccc-000000000003', '11111111-aaaa-bbbb-cccc-000000000004', '44444444-aaaa-bbbb-cccc-000000000003',
 76.0,
 '{"alinhamento_objeto": 85, "capacidade_tecnica": 80, "capacidade_financeira": 75, "documentacao": 80, "risco": 55, "competitividade": 70}',
 'go',
 'Valor expressivo mas interiorizacao encarece operacao. Competitividade pode ser menor que concorrentes locais do interior. Recomenda-se ir com margem agressiva.',
 '["Sem estrutura fisica nas cidades do interior (necessario montar)"]',
 '["Levantar custos de deslocamento e hospedagem para 10 cidades", "Verificar disponibilidade de vigilantes armados no interior", "Preparar plano de interiorizacao com cronograma de mobilizacao"]',
 NOW()),

('55555555-aaaa-bbbb-cccc-000000000004', '11111111-aaaa-bbbb-cccc-000000000005', '44444444-aaaa-bbbb-cccc-000000000004',
 84.0,
 '{"alinhamento_objeto": 90, "capacidade_tecnica": 88, "capacidade_financeira": 82, "documentacao": 85, "risco": 75, "competitividade": 80}',
 'go',
 'Combinacao vigilancia + portaria e nosso diferencial. INSS pagador pontual. SICAF atualizado. Boa margem prevista.',
 '[]',
 '["Verificar escala de pessoal para postos INSS", "Preparar proposta com composicao de BDI detalhada"]',
 NOW()),

('55555555-aaaa-bbbb-cccc-000000000005', '11111111-aaaa-bbbb-cccc-000000000001', '44444444-aaaa-bbbb-cccc-000000000005',
 58.0,
 '{"alinhamento_objeto": 80, "capacidade_tecnica": 75, "capacidade_financeira": 70, "documentacao": 60, "risco": 25, "competitividade": 50}',
 'analyze',
 'Objeto interessante mas risco alto de inadimplencia. Historico de atrasos > 90 dias nos pagamentos da Prefeitura. Aguardar edital definitivo.',
 '["Edital nao publicado definitivamente", "Historico ruim de pagamentos do orgao"]',
 '["Monitorar publicacao definitiva do edital", "Consultar empresas que ja prestaram servico a Prefeitura sobre pagamentos", "Calcular impacto financeiro de atraso de 90+ dias no fluxo de caixa"]',
 NOW())
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 12. bidding_pricing (3 records)
-- =====================================================
INSERT INTO bidding_pricing (id, tender_id, proposal_id, itens, custos_diretos, custos_indiretos, impostos, margem_lucro, valor_total, cenario, cenarios_completos, comparativo_mercado, regime_tributario, bdi_percentual, created_at)
VALUES
('bbbbbbbb-aaaa-bbbb-cccc-000000000001', '11111111-aaaa-bbbb-cccc-000000000004', '22222222-aaaa-bbbb-cccc-000000000001',
 '[{"item": "Vigilante armado 24h capital", "custo_mensal": 7800.00, "quantidade": 8, "subtotal": 62400.00}, {"item": "Vigilante armado diurno capital", "custo_mensal": 4200.00, "quantidade": 4, "subtotal": 16800.00}, {"item": "Vigilante armado 24h interior", "custo_mensal": 9500.00, "quantidade": 10, "subtotal": 95000.00}, {"item": "Supervisor", "custo_mensal": 5800.00, "quantidade": 2, "subtotal": 11600.00}, {"item": "Coordenador", "custo_mensal": 8500.00, "quantidade": 1, "subtotal": 8500.00}]',
 2330400.00, 291300.00, 175824.00, 7.5,
 2980000.00, 'moderado',
 '{"conservador": {"valor": 3150000.00, "margem": 10.0, "bdi": 25.0}, "moderado": {"valor": 2980000.00, "margem": 7.5, "bdi": 22.5}, "agressivo": {"valor": 2780000.00, "margem": 4.0, "bdi": 18.5}}',
 '{"media_pncp": 3100000.00, "menor_pncp": 2650000.00, "maior_pncp": 3800000.00, "posicao_estimada": "abaixo_media", "fonte": "Painel de Precos PNCP - ultimos 12 meses - AM"}',
 'lucro_real', 22.5, NOW()),

('bbbbbbbb-aaaa-bbbb-cccc-000000000002', '11111111-aaaa-bbbb-cccc-000000000005', '22222222-aaaa-bbbb-cccc-000000000002',
 '[{"item": "Vigilante armado 24h", "custo_mensal": 7800.00, "quantidade": 4, "subtotal": 31200.00}, {"item": "Porteiro 12h", "custo_mensal": 3800.00, "quantidade": 6, "subtotal": 22800.00}]',
 648000.00, 97200.00, 56700.00, 8.0,
 1150000.00, 'moderado',
 '{"conservador": {"valor": 1200000.00, "margem": 10.5, "bdi": 26.0}, "moderado": {"valor": 1150000.00, "margem": 8.0, "bdi": 24.0}, "agressivo": {"valor": 1050000.00, "margem": 4.5, "bdi": 19.0}}',
 '{"media_pncp": 1180000.00, "menor_pncp": 980000.00, "maior_pncp": 1400000.00, "posicao_estimada": "na_media", "fonte": "Painel de Precos PNCP - INSS nacional"}',
 'lucro_real', 24.0, NOW()),

('bbbbbbbb-aaaa-bbbb-cccc-000000000003', '11111111-aaaa-bbbb-cccc-000000000006', '22222222-aaaa-bbbb-cccc-000000000003',
 '[{"item": "Monitoramento 24h", "custo_mensal": 1800.00, "quantidade": 5, "subtotal": 9000.00}, {"item": "Manutencao preventiva", "custo_mensal": 900.00, "quantidade": 5, "subtotal": 4500.00}, {"item": "Manutencao corretiva", "custo_chamado": 280.00, "quantidade": 12, "subtotal": 3360.00}, {"item": "Controle acesso", "custo_mensal": 220.00, "quantidade": 8, "subtotal": 1760.00}, {"item": "Resposta tatica", "custo_mensal": 2200.00, "quantidade": 1, "subtotal": 2200.00}]',
 249840.00, 37476.00, 22486.00, 6.0,
 360000.00, 'moderado',
 '{"conservador": {"valor": 385000.00, "margem": 9.0, "bdi": 24.0}, "moderado": {"valor": 360000.00, "margem": 6.0, "bdi": 20.0}, "agressivo": {"valor": 330000.00, "margem": 2.5, "bdi": 15.0}}',
 '{"media_pncp": 400000.00, "menor_pncp": 310000.00, "maior_pncp": 520000.00, "posicao_estimada": "abaixo_media", "fonte": "Painel de Precos PNCP - seg eletronica AM"}',
 'lucro_real', 20.0, NOW() - INTERVAL '120 days')
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 13. bidding_disputes (2 records)
-- =====================================================
INSERT INTO bidding_disputes (id, tender_id, portal, sessao_id, status, estrategia, lances, posicao_final, resultado, valor_final, started_at, finished_at, created_at)
VALUES
('dddddddd-aaaa-bbbb-cccc-000000000001', '11111111-aaaa-bbbb-cccc-000000000005',
 'COMPRASNET', 'SESSAO-PE012-2026',
 'em_andamento',
 '{"tipo": "decremental", "valor_minimo": 1050000.00, "decremento_inicial": 15000.00, "decremento_minimo": 5000.00, "tempo_resposta_seg": 15, "observacoes": "Acompanhar lances dos concorrentes e manter posicao entre top 3"}',
 '[{"lance": 1, "valor": 1150000.00, "posicao": 3, "timestamp": "2026-02-28 09:15:00"}, {"lance": 2, "valor": 1130000.00, "posicao": 2, "timestamp": "2026-02-28 09:22:00"}, {"lance": 3, "valor": 1120000.00, "posicao": 2, "timestamp": "2026-02-28 09:28:00"}]',
 NULL, NULL, NULL,
 '2026-02-28 09:00:00', NULL, NOW()),

('dddddddd-aaaa-bbbb-cccc-000000000002', '11111111-aaaa-bbbb-cccc-000000000006',
 'COMPRASNET', 'SESSAO-PE022-2025',
 'finalizado',
 '{"tipo": "decremental", "valor_minimo": 340000.00, "decremento_inicial": 5000.00, "decremento_minimo": 1000.00, "tempo_resposta_seg": 10}',
 '[{"lance": 1, "valor": 370000.00, "posicao": 2, "timestamp": "2025-11-10 09:12:00"}, {"lance": 2, "valor": 362000.00, "posicao": 1, "timestamp": "2025-11-10 09:18:00"}, {"lance": 3, "valor": 358000.00, "posicao": 1, "timestamp": "2025-11-10 09:25:00"}, {"lance": 4, "valor": 355000.00, "posicao": 1, "timestamp": "2025-11-10 09:32:00"}]',
 1, 'vencedor', '355000.00',
 '2025-11-10 09:00:00', '2025-11-10 09:45:00', NOW() - INTERVAL '120 days')
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 14. bidding_price_history (10 records)
-- =====================================================
INSERT INTO bidding_price_history (id, item_descricao, item_catmat, preco, unidade, quantidade, orgao_nome, orgao_cnpj, orgao_uf, data_homologacao, fonte, fonte_id, created_at)
VALUES
('eeeeeeee-aaaa-bbbb-cccc-000000000001',
 'Posto de vigilancia patrimonial armada 24h (escala 12x36)',
 '27502', 8200.00, 'posto/mes', 12.0000,
 'Tribunal de Justica do Amazonas', '04539504000107', 'AM',
 '2025-08-15', 'pncp', 'PNCP-2025-TJAM-001', NOW()),

('eeeeeeee-aaaa-bbbb-cccc-000000000002',
 'Posto de vigilancia patrimonial armada 24h (escala 12x36)',
 '27502', 7950.00, 'posto/mes', 20.0000,
 'Universidade Federal do Amazonas - UFAM', '04280196000176', 'AM',
 '2025-06-20', 'pncp', 'PNCP-2025-UFAM-001', NOW()),

('eeeeeeee-aaaa-bbbb-cccc-000000000003',
 'Posto de vigilancia patrimonial desarmada 24h',
 '27502', 6800.00, 'posto/mes', 8.0000,
 'Prefeitura Municipal de Manaus', '04312401000128', 'AM',
 '2025-09-10', 'pncp', 'PNCP-2025-PMM-001', NOW()),

('eeeeeeee-aaaa-bbbb-cccc-000000000004',
 'Posto de portaria/recepcao 12h diurno',
 '27502', 4100.00, 'posto/mes', 15.0000,
 'Governo do Estado do Amazonas - SEAD', '04312401000128', 'AM',
 '2025-07-05', 'pncp', 'PNCP-2025-SEAD-001', NOW()),

('eeeeeeee-aaaa-bbbb-cccc-000000000005',
 'Posto de portaria 24h',
 '27502', 6200.00, 'posto/mes', 10.0000,
 'INSS - Gerencia Executiva Manaus', '29979036005745', 'AM',
 '2025-05-12', 'pncp', 'PNCP-2025-INSS-001', NOW()),

('eeeeeeee-aaaa-bbbb-cccc-000000000006',
 'Servico de monitoramento eletronico 24h (CFTV + alarme)',
 '150215', 2950.00, 'unidade/mes', 5.0000,
 'SUFRAMA', '04407029000143', 'AM',
 '2025-10-20', 'pncp', 'PNCP-2025-SUFRAMA-001', NOW()),

('eeeeeeee-aaaa-bbbb-cccc-000000000007',
 'Manutencao preventiva de sistema de CFTV (por camera)',
 '150215', 85.00, 'camera/mes', 50.0000,
 'Tribunal Regional Eleitoral do Amazonas', '04284951000157', 'AM',
 '2025-04-18', 'pncp', 'PNCP-2025-TREAM-001', NOW()),

('eeeeeeee-aaaa-bbbb-cccc-000000000008',
 'Sistema de alarme monitorado (por ponto monitorado)',
 '150215', 320.00, 'ponto/mes', 30.0000,
 'Secretaria de Seguranca Publica - SSP/AM', '04312401000128', 'AM',
 '2025-11-05', 'ecompras_am', 'EAM-2025-SSP-001', NOW()),

('eeeeeeee-aaaa-bbbb-cccc-000000000009',
 'Supervisor de campo - seguranca patrimonial',
 '27502', 5800.00, 'profissional/mes', 3.0000,
 'Assembleia Legislativa do Amazonas - ALEAM', '04545876000150', 'AM',
 '2025-08-22', 'pncp', 'PNCP-2025-ALEAM-001', NOW()),

('eeeeeeee-aaaa-bbbb-cccc-000000000010',
 'Servico de resposta tatica / pronta resposta a alarmes',
 '150215', 3800.00, 'servico/mes', 1.0000,
 'Companhia de Gas do Amazonas - CIGÁS', '04312401000290', 'AM',
 '2025-12-10', 'licitacoes_e', 'LE-2025-CIGAS-001', NOW())
ON CONFLICT (id) DO NOTHING;


-- =====================================================
-- 15. bidding_sync_jobs (4 records)
-- =====================================================
INSERT INTO bidding_sync_jobs (id, portal, tipo, status, registros_processados, registros_novos, registros_atualizados, erros, filtros_utilizados, started_at, finished_at, created_at)
VALUES
('ffffffff-aaaa-bbbb-cccc-000000000001',
 'PNCP', 'opportunities', 'concluido',
 150, 12, 5, '[]',
 '{"uf": "AM", "data_inicio": "2026-03-01", "data_fim": "2026-03-12", "palavras_chave": ["vigilancia", "seguranca", "portaria", "cftv", "alarme", "monitoramento"]}',
 '2026-03-12 06:00:00', '2026-03-12 06:12:35', NOW()),

('ffffffff-aaaa-bbbb-cccc-000000000002',
 'COMPRASNET', 'opportunities', 'concluido',
 230, 8, 3, '[]',
 '{"uf": "AM", "data_inicio": "2026-03-01", "data_fim": "2026-03-12", "linha_fornecimento": "servicos_continuados"}',
 '2026-03-12 06:15:00', '2026-03-12 06:28:42', NOW()),

('ffffffff-aaaa-bbbb-cccc-000000000003',
 'ECOMPRAS_AM', 'opportunities', 'concluido',
 85, 5, 2, '[]',
 '{"data_inicio": "2026-03-01", "data_fim": "2026-03-12", "segmento": "seguranca"}',
 '2026-03-12 06:30:00', '2026-03-12 06:38:10', NOW()),

('ffffffff-aaaa-bbbb-cccc-000000000004',
 'PNCP', 'price_history', 'concluido',
 500, 45, 0, '[]',
 '{"uf": "AM", "catmat": ["27502", "150215"], "periodo_meses": 12}',
 '2026-03-12 07:00:00', '2026-03-12 07:15:22', NOW())
ON CONFLICT (id) DO NOTHING;


COMMIT;
