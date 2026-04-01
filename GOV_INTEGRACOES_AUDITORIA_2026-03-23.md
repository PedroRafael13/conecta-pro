# AUDITORIA COMPLETA — INTEGRAÇÕES GOVERNAMENTAIS CONECTA PRO

**Data:** 2026-03-23
**Auditor:** Claude Opus 4.6 (AI)
**Versão:** 1.0
**Escopo:** Todos os módulos de integração gov do sistema Conecta PRO

---

## RESUMO EXECUTIVO

| Métrica | Valor |
|---------|-------|
| **Arquivos Python gov** | 171 |
| **Linhas de código** | 64.296 |
| **Endpoints registrados** | 306 rotas `/api/v1/government/*` |
| **Tabelas no banco** | 13 |
| **Tabelas com dados** | 2 (nfses: 22 rows, digital_signatures: 3 rows) |
| **Integrações online** | 9 |
| **Integrações degradadas** | 8 (ambiente homologação) |
| **Bugs encontrados** | 6 (4 erros 500, 2 NFS-e sem transmissão) |
| **Páginas frontend** | 13 (todas funcionais) |
| **Celery tasks configuradas** | 14 jobs com cron |

### Status Geral por Integração

| Integração | Backend | Frontend | Banco | API Status | Avaliação |
|------------|---------|----------|-------|------------|-----------|
| **NFS-e Manaus** | ✅ Completo | ✅ Completo | ✅ 22 rows | 200 OK | 🟡 Funcional mas nunca transmitiu |
| **NFS-e Nacional** | ✅ Completo | ✅ Completo | ✅ Schema | 200 OK (homolog) | 🟡 Homologação |
| **eSocial** | 🟡 4 eventos reais | ✅ Completo | ✅ Schema vazio | 200 OK (homolog) | 🟡 Parcial |
| **SEFAZ-AM NF-e** | ✅ 7 webservices | ✅ Completo | ✅ Schema vazio | 200 OK (produção) | 🟡 Schema sem dados |
| **NFC-e** | ⚠️ 7 TODOs | - | - | 200 OK | 🔴 Placeholder |
| **CT-e** | ✅ Completo | ✅ Completo | - | 200 OK | 🟡 Sem uso |
| **MDF-e** | ✅ Completo | ✅ Completo | - | 200 OK | 🟡 Sem uso |
| **SPED Fiscal** | ✅ Completo | ✅ Completo | ✅ Schema vazio | 200 OK | 🟡 Online |
| **SPED Contábil** | ✅ Completo | ✅ Completo | ✅ Schema vazio | 200 OK | 🟡 Online |
| **EFD-Reinf** | ✅ 16 eventos | ✅ Completo | - | 200 OK | 🟡 Online |
| **DCTFWeb** | ✅ Completo | ✅ Completo | - | 200 OK | 🟡 Online |
| **FGTS Digital** | ✅ 1.814 linhas | ✅ Completo | - | Degradado | 🟡 Cálculos OK, API degradada |
| **FGTS/INSS cálculo** | ✅ Tabelas 2026 | ✅ Completo | ✅ Schema vazio | - | 🟢 Motor de cálculo funcional |
| **Simples Nacional** | ✅ PGDAS-D/DAS/Fator R | ✅ Completo | - | 200 OK | 🟡 Degradado |
| **e-CAC** | ✅ Completo | ✅ Completo | - | 200 OK | 🟡 Online |
| **CND Federal** | ✅ 234 linhas | ✅ Completo | - | - | 🟡 Via bidding |
| **CNDT Trabalhista** | ✅ 244 linhas | ✅ Redirects | - | - | 🟡 Via bidding |
| **Gov.br OAuth2** | ✅ PKCE completo | ✅ Completo | - | 200 OK | 🟡 Online, não configurado |
| **Certificado A1** | ✅ 607 linhas | ✅ Completo | ✅ 3 rows | Válido até 2027-01 | 🟢 Funcional |
| **Certificado A3** | ❌ Não implementado | - | - | - | 🔴 Não existe |
| **CAGED** | ❌ Substituído eSocial | - | - | - | ⬜ N/A |
| **RAIS** | ❌ Substituído eSocial | - | - | - | ⬜ N/A |
| **SERPRO** | ❌ Não existe | - | - | - | 🔴 Não existe |
| **Dataprev** | ❌ Não existe | - | - | - | 🔴 Não existe |

**Legenda:** 🟢 Funcional | 🟡 Parcial/Homologação | 🔴 Não implementado | ⬜ N/A

---

## 1. eSocial

### 1.1 Arquivos

| Arquivo | Linhas | Localização |
|---------|--------|-------------|
| `esocial_manager.py` | ~800 | `government_integrations/core/` |
| `esocial_transmitter.py` | 827 | `government_integrations/core/` |
| `esocial_controller.py` | ~400 | `government_integrations/controllers/` |
| `esocial_service.py` | ~300 | `government_integrations/services/` |
| `esocial_extractor.py` | ~350 | `government_integrations/extractors/` |
| `esocial_sync.py` | ~400 | `government_integrations/sync/` |
| `esocial_controller.py` (HR) | 377 | `hr/payroll_integration/controllers/` |
| `esocial_service.py` (HR) | 459 | `hr/payroll_integration/services/` |
| `esocial_controller.py` (PM) | 146 | `people_management/hr/controllers/` |
| `esocial_service.py` (PM) | 126 | `people_management/hr/services/` |

### 1.2 Eventos Implementados

| Evento | Descrição | Status |
|--------|-----------|--------|
| **S-1000** | Informações do Empregador | ✅ XML builder completo |
| **S-2200** | Admissão de Trabalhador | ✅ XML builder completo |
| **S-2299** | Desligamento | ✅ XML builder completo |
| **S-1200** | Remuneração | ✅ XML builder completo |
| S-1005 a S-1070 | Tabelas | ⚠️ Generic builder |
| S-2190 a S-2399 | Não Periódicos | ⚠️ Generic builder |
| S-1202 a S-1299 | Periódicos | ⚠️ Generic builder |
| S-5001 a S-5012 | Totalizadores | ⚠️ Generic builder |
| S-3000 | Exclusão | ⚠️ Generic builder |

### 1.3 Transmissão

- **Protocolo:** SOAP + mTLS via certificado A1
- **Ambiente atual:** Homologação
- **Eventos no banco:** 0 (tabela `eventos_esocial` vazia)
- **Pendências:** 8 eventos pendentes (S-2200 a S-2299) listados na API

### 1.4 O Que Falta Para Ativar

1. Implementar XML builders específicos para todos os eventos além de S-1000/S-2200/S-2299/S-1200
2. Enviar eventos de tabelas (S-1000 a S-1070) como pré-requisito
3. Configurar ambiente para **produção** (variável `ESOCIAL_ENVIRONMENT`)
4. Validar certificado A1 com e-CAC
5. Testar transmissão em homologação com dados reais dos 44 empregados

---

## 2. SEFAZ / NF-e / NFC-e

### 2.1 NF-e (Nota Fiscal Eletrônica)

| Arquivo | Linhas | Propósito |
|---------|--------|-----------|
| `sefaz_manager.py` | 1.183 | Manager principal (NFE/NFCE/CTE/MDFE/NFSE) |
| `sefaz_am.py` | 1.519 | SEFAZ-AM: 7 webservices (prod + homolog) |
| `nfe_transmitter.py` | 555 | SOAP 1.2 + mTLS via aiohttp |
| `nfce_controller.py` | 637 | ⚠️ 7 TODOs — retorna placeholders |
| `nfe_provider.py` | 529 | Financial integration |

**Webservices SEFAZ-AM implementados:**
1. NfeStatusServico
2. NfeAutorizacao
3. NfeRetAutorizacao
4. NfeConsulta
5. NfeInutilizacao
6. RecepcaoEvento
7. CadConsultaCadastro

**Status API:** `disponivel=true`, ambiente produção, 476ms response

**Banco:** Tabela `nfes` (55 colunas) + `nfe_itens` (35 colunas) — ambas vazias

**NFC-e:** 1 registro de teste. Controller com 7 TODOs (consulta SEFAZ, cancelamento, DANFE — todos placeholder)

### 2.2 O Que Falta Para Ativar NF-e

1. Popular tabela `cfops` (referência — atualmente vazia)
2. Implementar os 7 TODOs do NFC-e controller
3. Gerar DANFE real (atualmente placeholder)
4. Testar emissão completa em homologação
5. Configurar sequência numérica (série + número)
6. Cadastrar CSC (Código de Segurança do Contribuinte) para NFC-e

---

## 3. NFS-e (Nota Fiscal de Serviço)

### 3.1 NFS-e Manaus (ABRASF 2.04)

| Arquivo | Linhas |
|---------|--------|
| `nfse_manaus.py` | 606 |
| `nfse_manaus_sync.py` | 606 |
| Controller + Service | ~1.000 |

**Status API:** Produção, CNPJ 35710481000103, certificado válido até 2027-01-13

**Banco:** 22 NFS-e autorizadas na tabela `nfses`, porém **`numero_nfse` é NULL em todas** — indica que nunca foram transmitidas ao portal da prefeitura

### 3.2 NFS-e Nacional (REST API)

| Arquivo | Linhas |
|---------|--------|
| `nfse_nacional.py` | 704 |
| `nfse_nacional_sync.py` | 513 |
| Controller + Service | ~1.000 |

**Status API:** Homologação. Mensagem: "Padrão Nacional em preparação. Migração prevista para 2026"

**Frontend:** Página NFS-e Multi-Empresa funcional com detecção automática CNPJ (Patrimonial vs Eletrônica) e suporte a liminares. Botão "Emitir" **desabilitado** (homologação).

### 3.3 O Que Falta Para Ativar

1. Popular tabela `codigos_servico` (referência ISS — atualmente vazia)
2. Verificar se as 22 NFS-e existentes precisam ser transmitidas ou são de teste
3. Configurar credenciais NFS-e Manaus (`NFSE_MANAUS_USUARIO`, `NFSE_MANAUS_SENHA`)
4. Testar transmissão real de NFS-e para a Prefeitura de Manaus
5. Aguardar migração NFS-e Nacional (prevista 2026)

---

## 4. SPED (Fiscal + Contábil + Reinf)

### 4.1 Arquivos

| Arquivo | Linhas | Propósito |
|---------|--------|-----------|
| `sped_manager.py` | 862 | EFD-ICMS/IPI — blocos 0,C,D,E,G,H,K,1,9 |
| `sped_contabil.py` | 831 | ECD (Escrituração Contábil Digital) |
| `sped_fiscal.py` | 657 | EFD-ICMS/IPI |
| `efd_reinf.py` | 550 | 16 tipos de eventos (R-1000 a R-9000) |

### 4.2 Status

- **API:** Online para todos (SPED Fiscal, Contábil, EFD-Reinf)
- **Banco:** Tabela `sped_files` (24 colunas) — vazia
- **Frontend:** Páginas completas com geração e validação

### 4.3 O Que Falta

1. Integrar com dados contábeis reais (balanço, DRE, lançamentos)
2. Gerar primeiro arquivo SPED de teste
3. Validar com PVA (Programa Validador e Assinador)
4. Configurar periodicidade de envio

---

## 5. FGTS / INSS

### 5.1 Arquivos

| Arquivo | Linhas | Propósito |
|---------|--------|-----------|
| `fgts_inss_manager.py` | 1.814 | GRF, GPS, DARF, tabelas cálculo |
| `fgts_digital.py` | 486 | FGTS Digital (PIX, guias, rescisões) |
| `fgts_digital_sync.py` | 492 | Sync |
| `fgts_extractor.py` | 231 | Extração dados |

### 5.2 Status

- **Motor de cálculo:** ✅ Funcional (tabela 2026, alíquotas atualizadas)
- **FGTS Digital API:** Degradado
- **Banco:** Tabela `tabela_inss` (10 colunas) — vazia (deveria ter faixas)
- **Simples Nacional:** Optante, Anexo III, desde 2020-01-01

### 5.3 O Que Falta

1. Popular tabela `tabela_inss` com faixas vigentes
2. Investigar por que FGTS Digital está degradado
3. Validar cálculos com folha real dos 44 empregados
4. Integrar com geração de guias DARF/GPS

---

## 6. DCTFWeb

### 6.1 Status

- **Backend:** Implementado
- **Frontend:** Página completa (cálculo FGTS/INSS, emissão DPS, guia mensal)
- **API:** Online
- **Celery:** Job diário às 08:00

### 6.2 O Que Falta

1. Gerar primeira declaração com dados reais
2. Transmitir em homologação
3. Frontend usa estado local (dados perdidos ao recarregar página)

---

## 7. CND / Certidões Negativas

### 7.1 Implementação

| Tipo | Arquivo | Linhas |
|------|---------|--------|
| CND Federal (RFB+PGFN) | `bidding/.../cnd_client.py` | 234 |
| CNDT Trabalhista | `bidding/.../cndt_client.py` | 244 |
| CND Sync (5 tipos) | `ged/tasks/cnd_sync_task.py` | 146 |
| e-CAC | `core/ecac.py` | 497 |

### 7.2 Tipos Monitorados (Celery task)

1. CND Federal (RFB + PGFN)
2. CND Estadual
3. CND Municipal
4. CRF FGTS — ⚠️ **EXPIRA EM 8 DIAS** (2026-03-31)
5. CNDT Trabalhista

### 7.3 Frontend

- Página principal de certidões com filtros por tipo
- 5 sub-rotas (federal, estadual, municipal, fgts, trabalhista) redirecionam para a principal
- Alertas de vencimento integrados

### 7.4 Alertas Críticos

| Certidão | Status | Vencimento |
|----------|--------|------------|
| CRF FGTS | ⚠️ Expirando | 2026-03-31 (8 dias) |
| Alvará PF | 🔴 EXPIRADO | 2026-02-28 |

---

## 8. Gov.br / e-CAC

### 8.1 Gov.br OAuth2

| Arquivo | Linhas |
|---------|--------|
| `core/govbr.py` | 358 |
| `extractors/govbr/govbr_extractor.py` | 413 |
| Controller + Service | ~700 |

- **Protocolo:** OAuth2 Authorization Code + PKCE (S256)
- **Níveis:** Bronze / Prata / Ouro
- **Status:** Online, mas **NÃO CONFIGURADO** (faltam `GOVBR_CLIENT_ID` e `GOVBR_CLIENT_SECRET`)
- **URL de autorização:** Gera corretamente com code_challenge

### 8.2 e-CAC

- **Implementação:** Situação fiscal, certidões, débitos, parcelamentos, declarações
- **Status:** Online

### 8.3 O Que Falta

1. Registrar aplicação no Gov.br para obter CLIENT_ID e CLIENT_SECRET
2. Configurar REDIRECT_URI
3. Testar fluxo completo de autenticação

---

## 9. Certificado Digital

### 9.1 Status Atual

| Item | Valor |
|------|-------|
| **Tipo** | A1 (.pfx) |
| **Caminho** | `/opt/conecta-pro/credentials/certificates/certificado.pfx` |
| **Validade** | Até 2027-01-13 |
| **Status** | ✅ Válido |
| **CNPJ** | 35.710.481/0001-03 |
| **A3 (Token)** | ❌ Não implementado |

### 9.2 Arquivos Encontrados

| Arquivo | Localização |
|---------|-------------|
| `certificado.pfx` | `/opt/conecta-pro/credentials/certificates/` |
| `conecta_certificado.p12` | `/opt/conecta-pro/certs/` |
| `a1_cert.pem` + `a1_key.pem` | `/opt/conecta-pro/credentials/certificates/` |
| `inter_cert.pem` + `inter_key.pem` | `/opt/conecta-pro/credentials/certificates/` |

### 9.3 Funcionalidades

- Upload de certificado A1
- Parse e validação automática
- Extração de CPF/CNPJ
- Verificação de expiração
- Assinatura XML (XMLDSig) para eSocial, NF-e, NFC-e, CT-e, MDF-e
- Gerenciamento multi-tenant

---

## 10. Variáveis de Ambiente Necessárias

### 10.1 Certificado Digital

| Variável | Status | Propósito |
|----------|--------|-----------|
| `CERTIFICATE_PATH` | ✅ Configurada | Caminho do .pfx |
| `CERTIFICATE_PASSWORD` | ✅ Configurada | Senha do certificado |
| `CERTIFICATE_PATH_STAGING` | - | Certificado staging |

### 10.2 eSocial

| Variável | Status | Propósito |
|----------|--------|-----------|
| `ESOCIAL_ENVIRONMENT` | ✅ Homologação | Ambiente (producao/homologacao) |

### 10.3 SEFAZ / NF-e

| Variável | Status | Propósito |
|----------|--------|-----------|
| `SEFAZ_ENVIRONMENT` | ✅ Produção | Ambiente SEFAZ |
| `NFE_CERT_PATH` | ✅ Configurada | Certificado NF-e |
| `NFE_CERT_PASSWORD` | ✅ Configurada | Senha certificado |
| `NFE_AMBIENTE` | ✅ Configurada | Ambiente NF-e |
| `NFE_UF` | ✅ Configurada | UF (AM) |
| `NFE_TIMEOUT_SECONDS` | ✅ Configurada | Timeout |

### 10.4 NFS-e

| Variável | Status | Propósito |
|----------|--------|-----------|
| `NFSE_MANAUS_CNPJ` | ✅ Configurada | CNPJ Manaus |
| `NFSE_MANAUS_USUARIO` | ⚠️ Verificar | Usuário portal Manaus |
| `NFSE_MANAUS_SENHA` | ⚠️ Verificar | Senha portal Manaus |
| `NFSE_MANAUS_IM` | ✅ Configurada | Inscrição Municipal |
| `NFSE_MANAUS_ENVIRONMENT` | ✅ Configurada | Ambiente |
| `NFSE_NACIONAL_CNPJ` | ✅ Configurada | CNPJ Nacional |
| `NFSE_NACIONAL_IM` | ✅ Configurada | IM Nacional |
| `NFSE_NACIONAL_COD_MUNICIPIO` | ✅ Configurada | Cód. município |
| `NFSE_NACIONAL_RAZAO_SOCIAL` | ✅ Configurada | Razão social |
| `NFSE_NACIONAL_ENVIRONMENT` | ✅ Homologação | Ambiente |

### 10.5 Gov.br

| Variável | Status | Propósito |
|----------|--------|-----------|
| `GOVBR_CLIENT_ID` | ❌ Não configurada | OAuth2 Client ID |
| `GOVBR_CLIENT_SECRET` | ❌ Não configurada | OAuth2 Secret |
| `GOVBR_REDIRECT_URI` | ❌ Não configurada | Redirect URI |
| `GOVBR_AMBIENTE` | - | Ambiente |

### 10.6 Vault (Cofre de Credenciais)

| Variável | Status | Propósito |
|----------|--------|-----------|
| `VAULT_ADDR` | - | Endereço HashiCorp Vault |
| `VAULT_TOKEN` | - | Token Vault |
| `VAULT_ROLE_ID` | - | Role ID AppRole |
| `VAULT_SECRET_ID` | - | Secret ID AppRole |

---

## 11. Banco de Dados — Tabelas Gov

### 11.1 Inventário

| Tabela | Colunas | Registros | Categoria |
|--------|---------|-----------|-----------|
| `nfses` | 58 | **22** | NFS-e |
| `digital_signatures` | 24 | **3** | Assinaturas |
| `nfes` | 55 | 0 | NF-e |
| `nfe_itens` | 35 | 0 | Itens NF-e |
| `retencoes_federais` | 37 | 0 | Retenções tribut. |
| `sped_files` | 24 | 0 | Arquivos SPED |
| `fiscal_obligations` | 17 | 0 | Obrigações fiscais |
| `eventos_esocial` | 20 | 0 | eSocial |
| `tabela_inss` | 10 | 0 | Faixas INSS |
| `documentos_fiscais` | 18 | 0 | Docs fiscais |
| `cfops` | 25 | 0 | CFOPs |
| `codigos_servico` | 6 | 0 | Códigos ISS |
| `portal_digital_signatures` | 14 | 0 | Assinaturas portal |

### 11.2 Problemas Críticos

1. **Migration `sprint56_create_gov_sync_tables.py` NÃO foi aplicada** — tabelas `gov_sync_*` não existem no banco
2. **Tabelas de referência vazias:** `cfops`, `codigos_servico`, `tabela_inss` precisam de seed data
3. **22 NFS-e sem `numero_nfse`** — nunca transmitidas
4. **Sem tabelas para:** CND, PGFN, CAGED, RAIS, DCTF, DARF, EFD, SEFAZ config

---

## 12. Celery Tasks Governamentais

### 12.1 Jobs Configurados

| Job | Frequência | Horário |
|-----|------------|---------|
| NF-e/NFC-e Sync | A cada 30 min | - |
| CT-e/MDF-e Sync | A cada 30 min | - |
| eSocial Sync | Diário | 06:00 |
| FGTS Digital Sync | Diário | 07:00 |
| DCTFWeb Sync | Diário | 08:00 |
| EFD-Reinf Sync | Diário | 08:30 |
| SPED Fiscal | Semanal | Segunda 03:00 |
| SPED Contábil | Mensal | Dia 5 às 03:00 |
| NFS-e Manaus Sync | A cada 60 min | - |
| NFS-e Nacional Sync | A cada 60 min | - |
| Receita Federal | Semanal | - |
| Simples Nacional | Mensal | - |
| CND Sync (5 tipos) | Diário | - |
| Monit. Certificados | Diário | - |

### 12.2 Monitoring Tasks

- Verificador de disponibilidade das integrações
- Verificador de expiração de certificados
- Reprocessamento de falhas

---

## 13. Frontend — Páginas Governamentais

### 13.1 Módulo Fiscal (`/modulos/fiscal/`)

| Página | Rota | Funcionalidade |
|--------|------|---------------|
| Dashboard Fiscal | `/modulos/fiscal` | 4 cards (NFS-e, eSocial, Certidões, Sync) |
| NFS-e | `/modulos/fiscal/nfse` | Listar, emitir, cancelar NFS-e |
| NFS-e Multi-Empresa | `/modulos/fiscal/nfse-multi` | Emissão inteligente (detecção CNPJ + liminares) |
| eSocial | `/modulos/fiscal/esocial` | Gestão de eventos (S-1000 a S-2399) |
| SPED | `/modulos/fiscal/sped` | 3 tabs (Fiscal, Contábil, Reinf) |
| DCTFWeb | `/modulos/fiscal/dctfweb` | Declarações + guias FGTS/INSS |
| EFD-Reinf | `/modulos/fiscal/reinf` | 5 tipos de eventos (R-1000 a R-4020) |
| Certidões | `/modulos/fiscal/certidoes` | Painel com 5 sub-rotas (redirect) |

### 13.2 Outras Páginas Gov

| Página | Rota | Funcionalidade |
|--------|------|---------------|
| eSocial (DP) | `/modulos/dp/esocial` | Admissões/Desligamentos → eSocial |
| Integrações | `/modulos/integracoes` | Dashboard status (17 integrações) |
| Obrigações | `/modulos/empresas/obrigacoes` | Calendário fiscal multi-empresa |

### 13.3 Services e Hooks

- **8 serviços** em `/frontend/src/services/government/`
- **8 hooks** em `/frontend/src/hooks/government/`
- Todos apontam para `/api/v1/government/*`

---

## 14. BUGS ENCONTRADOS

### 14.1 Erros 500 (Backend)

| # | Endpoint | Erro | Causa |
|---|----------|------|-------|
| 1 | `/government/dashboard/` | "Erro ao carregar dashboard" | Erro genérico no handler |
| 2 | `/government/dashboard/endpoints` | "Erro ao verificar endpoints" | Erro genérico |
| 3 | `/government/sync/jobs` | `'SyncManager' object has no attribute '_active_jobs'` | Atributo faltando na classe |
| 4 | `/government/sync/status/{cnpj}` | `'SyncManager' object has no attribute '_active_jobs'` | Mesmo bug |
| 5 | `/government/sync/configuracao/{cnpj}` | `'AsyncSession' object has no attribute 'query'` | SQLAlchemy 1.x em sessão async |
| 6 | `/government/sync/dados/certidoes/{cnpj}` | `'AsyncSession' object has no attribute 'query'` | Mesmo bug SQLAlchemy |

### 14.2 Outros Problemas

| # | Problema | Impacto |
|---|----------|---------|
| 7 | NFC-e controller com 7 TODOs | Retorna dados placeholder |
| 8 | 22 NFS-e com `numero_nfse` NULL | Nunca transmitidas |
| 9 | Migration gov_sync não aplicada | Sem infraestrutura de sync no banco |
| 10 | Tabelas referência vazias (cfops, codigos_servico, tabela_inss) | Cálculos sem dados base |
| 11 | DCTFWeb/Reinf frontend usa estado local | Dados perdidos ao recarregar |
| 12 | CRF FGTS expira 2026-03-31 | ⚠️ 8 DIAS |
| 13 | Alvará PF expirado 2026-02-28 | 🔴 VENCIDO |

---

## 15. Credenciais e Documentos Necessários

### 15.1 Já Disponíveis

| Item | Status |
|------|--------|
| Certificado Digital A1 (.pfx) | ✅ Válido até 2027-01-13 |
| CNPJ 35.710.481/0001-03 | ✅ |
| Inscrição Municipal (ISS) 45177801 | ✅ |
| Inscrição SUFRAMA 210140500 | ✅ |

### 15.2 Necessários para Ativação

| Item | Para | Prioridade |
|------|------|-----------|
| Credenciais portal NFS-e Manaus (usuário/senha) | NFS-e Manaus | ALTA |
| Registro no Gov.br (Client ID + Secret) | Gov.br OAuth2 | MÉDIA |
| CSC (Código de Segurança do Contribuinte) | NFC-e | MÉDIA |
| Certificado A1 do CNPJ 2 (Conecta Mais Patrimonial) | Multi-empresa | ALTA (quando aberto) |
| Credenciais e-CAC (procuração eletrônica) | e-CAC completo | MÉDIA |
| Cadastro FGTS Digital (gov.br prata/ouro) | FGTS Digital | ALTA |

---

## 16. ROADMAP DE ATIVAÇÃO

### Fase 1 — Correções Imediatas (1-2 dias) 🔴

1. **Corrigir 6 bugs 500** (SyncManager._active_jobs + AsyncSession.query)
2. **Renovar CRF FGTS** antes de 2026-03-31
3. **Renovar Alvará PF** (já expirado)
4. **Aplicar migration sprint56** (gov_sync tables)
5. **Popular tabelas referência:** cfops, codigos_servico, tabela_inss

### Fase 2 — NFS-e Manaus em Produção (3-5 dias) 🟡

1. Obter credenciais portal NFS-e Manaus
2. Testar emissão em homologação com dados reais
3. Verificar as 22 NFS-e existentes (teste ou válidas?)
4. Emitir primeira NFS-e real
5. Ativar sync automático (Celery job a cada 60min)

### Fase 3 — eSocial Completo (1-2 semanas) 🟡

1. Implementar XML builders para eventos faltantes
2. Enviar eventos de tabelas (S-1000 a S-1070) em homologação
3. Enviar admissões (S-2200) dos 44 empregados ativos
4. Enviar folha (S-1200/S-1210)
5. Migrar para produção

### Fase 4 — NF-e / SEFAZ-AM (1 semana) 🟡

1. Popular tabela CFOPs
2. Configurar sequência numérica e série
3. Obter CSC para NFC-e
4. Implementar os 7 TODOs do NFC-e controller
5. Testar emissão em homologação
6. Migrar para produção

### Fase 5 — SPED + DCTFWeb + Reinf (2 semanas) 🟡

1. Integrar dados contábeis reais
2. Gerar primeiro SPED Fiscal de teste
3. Validar com PVA
4. Gerar DCTFWeb com dados reais
5. Enviar EFD-Reinf em homologação

### Fase 6 — Gov.br + Integrações Avançadas (2-4 semanas) 🔵

1. Registrar aplicação no Gov.br
2. Implementar fluxo completo de autenticação
3. Integrar FGTS Digital via Gov.br
4. Certificado A3 (se necessário)
5. SERPRO/Dataprev (se necessário)

---

## 17. ARQUITETURA TÉCNICA

```
/opt/conecta-pro/backend/modules/government_integrations/
├── __init__.py
├── controllers/          # 23 controllers (REST endpoints)
│   ├── esocial_controller.py
│   ├── sefaz_controller.py
│   ├── nfse_manaus_controller.py
│   ├── nfse_nacional_controller.py
│   ├── nfce_controller.py
│   ├── cte_controller.py
│   ├── mdfe_controller.py
│   ├── sped_controller.py
│   ├── reinf_controller.py
│   ├── dctfweb_controller.py
│   ├── fgts_controller.py
│   ├── simples_controller.py
│   ├── certificate_controller.py
│   ├── govbr_controller.py
│   ├── ecac_controller.py
│   ├── sync_controller.py
│   ├── dashboard_controller.py
│   └── ...
├── core/                 # Business logic (~19.000 linhas)
│   ├── esocial_manager.py
│   ├── esocial_transmitter.py
│   ├── sefaz_manager.py
│   ├── sefaz_am.py
│   ├── nfe_transmitter.py
│   ├── fgts_inss_manager.py
│   ├── fgts_digital.py
│   ├── sped_manager.py
│   ├── sped_contabil.py
│   ├── sped_fiscal.py
│   ├── efd_reinf.py
│   ├── certificate_manager.py
│   ├── xml_signer.py
│   ├── govbr.py
│   ├── ecac.py
│   ├── contingency.py
│   ├── rate_limiter.py
│   └── credentials/
├── extractors/           # 21 extractors (data extraction)
├── sync/                 # 17 sync modules
├── services/             # 13 services
├── schemas/              # 17 Pydantic schemas
├── models/               # 2 SQLAlchemy models
├── jobs/                 # 4 Celery task files
└── migrations/           # SQL migrations
```

**Dependências externas:** `anthropic`, `PyMuPDF`, `python-docx`, `xlsxwriter`, `reportlab`, `aiohttp`, `lxml`, `signxml`, `cryptography`

---

## 18. CONCLUSÃO

O módulo `government_integrations` é **massivo** (64K linhas) e **surpreendentemente completo** em termos de estrutura. A maioria das integrações tem código real (não apenas stubs), mas nenhuma está em **produção efetiva** — todas estão em homologação ou degradadas.

**Prioridade máxima:** Corrigir os 6 bugs 500, renovar CRF FGTS (8 dias), e ativar NFS-e Manaus (já tem 22 notas prontas).

**Risco principal:** A migration `sprint56` não foi aplicada, então toda a infraestrutura de sync do banco está ausente. Os Celery jobs rodam mas não persistem resultados.

---

*Gerado automaticamente por auditoria técnica — 2026-03-23*
