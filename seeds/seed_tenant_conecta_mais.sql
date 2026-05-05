-- Seed: Tenant Conecta Mais (CPRO 12 T3 - 2026-05-05)
-- CNPJ: 35.710.481/0001-03
-- Empresa: CONECTAMAIS ELETRONICA LTDA
-- Executar apenas se tenants estiver vazio
--
-- ATENÇÃO (Cenário D): O Python model usa TenantStatus.ATIVO = "ativo" mas
-- o DB enum tenant_status tem valores inglês: {active, inactive, ...}.
-- Inserimos status='active' (valor válido no DB). Para _get_active_tenants()
-- funcionar, o Python deve ser corrigido para TenantStatus.ATIVO = "active".

INSERT INTO tenants (
    id,
    codigo,
    nome,
    nome_fantasia,
    documento,
    cnpj,
    email,
    responsavel_nome,
    responsavel_email,
    status,
    plano,
    tipo,
    endereco_cidade,
    endereco_estado,
    ativo
) VALUES (
    gen_random_uuid(),
    'CPRO-001',
    'CONECTAMAIS ELETRONICA LTDA',
    'Conecta Mais',
    '35710481000103',
    '35.710.481/0001-03',
    'jjesus@conectamais.pro',
    'Jordan Jesus',
    'jjesus@conectamais.pro',
    'active',
    'free',
    'company',
    'Manaus',
    'AM',
    true
) ON CONFLICT DO NOTHING;
