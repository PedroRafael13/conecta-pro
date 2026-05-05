-- ============================================================
-- SEED: 11 Clientes Reais das NFS-e CONECTAMAIS ELETRONICA LTDA
-- Executado em: 2026-03-23
-- ============================================================

-- PASSO 1: Desativar clientes fictícios
UPDATE clients SET ativo = false, status = 'cancelled', updated_at = NOW()
WHERE name ILIKE ANY(ARRAY['%bellavile%','%river park%','%bellaville%']);

UPDATE contracts SET is_active = false, status = 'cancelado', updated_at = NOW()
WHERE client_id IN (SELECT id FROM clients WHERE ativo = false);

UPDATE ged_clients SET is_active = false, updated_at = NOW()
WHERE name ILIKE ANY(ARRAY['%bellavile%','%river park%','%bellaville%']);

-- PASSO 2: Inserir 11 clientes reais (tabela clients)
INSERT INTO clients (
  id, code, name, trading_name, client_type, document_type, document_number,
  email, address_street, address_number, address_complement, address_neighborhood,
  address_city, address_state, address_zipcode, address_country,
  status, segment, ativo, guardian_enabled, plus_enabled, is_defaulter, is_vip,
  created_at, updated_at
) VALUES
(gen_random_uuid(), 'CLI-0005', 'CONDOMINIO LIFE CENTRO', 'Condomínio Life Centro', 'condominium', 'cnpj', '19865917000187', 'lifecentro@conectamais.pro', 'Rua Afonso Pena', '555', NULL, 'Praça 14 de Janeiro', 'Manaus', 'AM', '69020-160', 'Brasil', 'active', 'small', true, false, false, false, false, NOW(), NOW()),
(gen_random_uuid(), 'CLI-0006', 'CONDOMINIO PARQUE RESIDENCIAL GELAIN', 'Condomínio Gelain', 'condominium', 'cnpj', '00736037000182', 'gelain@conectamais.pro', 'Rua Gabriel Gonçalves', '9', 'Bloco A-1', 'Aleixo', 'Manaus', 'AM', '69060-000', 'Brasil', 'active', 'small', true, false, false, false, false, NOW(), NOW()),
(gen_random_uuid(), 'CLI-0007', 'CONDOMINIO RESIDENCIAL PARISE VILLAGE', 'Condomínio Parise Village', 'condominium', 'cnpj', '34857941000168', 'parisevillage@conectamais.pro', 'Rua Partenon', '475', NULL, 'Flores', 'Manaus', 'AM', '69058-340', 'Brasil', 'active', 'small', true, false, false, false, false, NOW(), NOW()),
(gen_random_uuid(), 'CLI-0008', 'CONDOMINIO RESIDENCIAL GREEN HILLS', 'Condomínio Green Hills', 'condominium', 'cnpj', '08063476000183', 'greenhills@conectamais.pro', 'Rua Marques de Suassuna', 'SN', NULL, 'Parque das Laranjeiras', 'Manaus', 'AM', '69058-810', 'Brasil', 'active', 'small', true, false, false, false, false, NOW(), NOW()),
(gen_random_uuid(), 'CLI-0009', 'CONDOMINIO VILLA DEI FIORI', 'Condomínio Villa Dei Fiori', 'condominium', 'cnpj', '02153384000108', 'villadei@conectamais.pro', 'Av. Constantino Nery', 'S/N', NULL, 'Chapada', 'Manaus', 'AM', '69050-001', 'Brasil', 'active', 'large', true, false, false, false, false, NOW(), NOW()),
(gen_random_uuid(), 'CLI-0010', 'CONDOMINIO DO EDIFICIO MICHELANGELO', 'Condomínio Michelangelo', 'condominium', 'cnpj', '04911208000113', 'michelangelo@conectamais.pro', 'Rua Paraíba', '1020', NULL, 'Adrianópolis', 'Manaus', 'AM', '69057-021', 'Brasil', 'active', 'small', true, false, false, false, false, NOW(), NOW()),
(gen_random_uuid(), 'CLI-0011', 'CONDOMINIO RESIDENCIAL VILLA DOS PASSAROS', 'Condomínio Villa dos Pássaros', 'condominium', 'cnpj', '13221953000121', 'villapassaros@conectamais.pro', 'Rod. Torquato Tapajós', '11265', 'Rodovia AM-10', 'Tarumã', 'Manaus', 'AM', '69041-025', 'Brasil', 'active', 'large', true, false, false, false, true, NOW(), NOW()),
(gen_random_uuid(), 'CLI-0012', 'CONDOMINIO MIRANTE DAS FLORES', 'Condomínio Mirante das Flores', 'condominium', 'cnpj', '52605708000170', 'miranteflores@conectamais.pro', 'Rua Narciso Cavalcante de Melo', '370', NULL, 'Ponta Negra', 'Manaus', 'AM', '69037-207', 'Brasil', 'active', 'large', true, false, false, false, true, NOW(), NOW()),
(gen_random_uuid(), 'CLI-0013', 'RESIDENCIAL LARANJEIRAS VILLAGE', 'Residencial Laranjeiras Village', 'condominium', 'cnpj', '24632786000128', 'ADMLARANJEIRASVILLAGE@GMAIL.COM', 'Rua Paraopeba', '274', 'CJ B Flor II', 'Flores', 'Manaus', 'AM', '69028-388', 'Brasil', 'active', 'large', true, false, false, false, true, NOW(), NOW()),
(gen_random_uuid(), 'CLI-0014', 'CONDOMINIO PRIME ARENA', 'Condomínio Prime Arena', 'condominium', 'cnpj', '47405340000166', 'PRIME.ARENAA@GMAIL.COM', 'Rua Parque dos Franceses', '736', NULL, 'Chapada', 'Manaus', 'AM', '69050-045', 'Brasil', 'active', 'large', true, false, false, false, true, NOW(), NOW()),
(gen_random_uuid(), 'CLI-0015', 'CONDOMINIO IDEAL FLORES DA CIDADE', 'Condomínio Ideal Flores da Cidade', 'condominium', 'cnpj', '23147782000191', 'idealflores@conectamais.pro', 'Rua Franz Schubert', '840', NULL, 'Flores', 'Manaus', 'AM', '69028-331', 'Brasil', 'active', 'enterprise', true, false, false, false, true, NOW(), NOW());

-- PASSO 3: Inserir 11 contratos reais
-- (Ver valores no commit message)

-- PASSO 4: Inserir 11 GED clients
-- (Espelho dos clients na tabela ged_clients)

-- PASSO 5: Inserir 22 NFS-e (Jan+Fev 2026)
-- (11 notas por mês, prestador CNPJ 35.710.481/0001-03)

-- PASSO 6: Criar 11 kits GED para março 2026
