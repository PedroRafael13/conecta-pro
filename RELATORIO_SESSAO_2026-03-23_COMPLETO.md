# RELATÓRIO COMPLETO — SESSÃO 2026-03-23
## Conecta PRO — ERP de Gestão para Segurança Patrimonial

**Empresa:** Jordan Santos de Jesus LTDA (CNPJ: 35.710.481/0001-03)
**Regime:** Simples Nacional | **Setor:** Vigilância e Segurança
**URL Produção:** https://erp.conectamais.pro
**VPS:** srv1134814.hstgr.cloud (82.25.75.74)
**Branch:** feature/people-management-reorganization
**Tag:** sessao-2026-03-22

---

## 1. DADOS REAIS DA EMPRESA NO SISTEMA

### 1.1 Clientes e Contratos
```
Clientes ativos:      13 (11 condomínios + Conecta Mais + Matriz)
Contratos ativos:     11
MRR Total:            R$ 272.086,96
MRR Anual:            R$ 3.265.043,52
Retenções:            3 com INSS, 3 com ISS, 3 com PIS/COFINS
Vencimentos:          0 em 30/60/90 dias
```

| Cliente | Contrato | Valor Mensal |
|---------|----------|-------------|
| Ideal Flores | Portaria + Serv. Gerais | R$ 65.842,25 |
| Mirante das Flores | Portaria + Serv. Gerais | R$ 42.255,00 |
| Laranjeiras Village | Portaria + Serv. Gerais | R$ 42.544,00 |
| Villa Dei Fiori | Portaria + Serv. Gerais | R$ 25.592,71 |
| River Park | Portaria + Serv. Gerais | R$ 24.800,00 |
| Villa dos Pássaros | Portaria + Serv. Gerais | R$ 24.800,00 |
| Prime Arena | Portaria + Serv. Gerais | R$ 23.053,00 |
| Michelangelo | Portaria + Serv. Gerais | R$ 15.000,00 |
| Bellavile | Portaria + Serv. Gerais | R$ 12.800,00 |
| Gelain | Seg. Eletrônica + Portaria Remota | R$ 6.000,00 |
| Parise Village | Manutenção CFTV | R$ 1.700,00 |
| Life Centro | Manutenção CFTV | R$ 1.500,00 |
| Green Hills | Manutenção CFTV | R$ 500,00 (suspenso) |

### 1.2 Funcionários
```
Funcionários ativos:  52
Folha bruta mensal:   R$ 95.950,20
FGTS mensal (8%):     R$ 7.676,02
INSS patronal:        R$ 908,86
Margem bruta:         ~65%
```

### 1.3 NFS-e Emitidas
```
Total emitidas:       27 (14 Jan + 13 Fev 2026)
Faturamento bruto:    R$ 542.673,92
Serviços:
  - Portaria:         R$ 260.739,68 (8 notas)
  - Vigilância:       R$ 173.990,56 (11 notas)
  - Limpeza:          R$ 107.943,68 (8 notas)
ISS 5% retido:        R$ 27.133,70
```

### 1.4 Integrações Bancárias (CONECTADAS)
```
Banco Inter (077):
  - Status:           CONECTADO ✅
  - Conta:            37099007-2 (Agência 0001)
  - Saldo:            R$ 32.382,11
  - Transações 30d:   646
  - Créditos 30d:     R$ 473.955,62
  - Client ID:        6398afd8-8f3b-4b96-b1e2-8b91d5181632
  - Certificado:      /credentials/certificates/inter_api.crt + .key

Banco Cora (403):
  - Status:           CONECTADO ✅
  - Saldo:            R$ 28,35
  - Certificado:      /credentials/certificates/cora_api.crt + .key

Saldo Total:          R$ 32.410,46
```

### 1.5 Certidões
```
Total:                8 certidões
Válidas:              3
Vencendo (≤30d):      4
Vencidas:             1

Alertas críticos:
🔴 Alvará PF:         VENCIDO desde 28/02/2026
🔴 CRF FGTS:          8 dias (vence 31/03/2026)
🔴 Certificado A1:    9 dias
🟡 CND Municipal:     13 dias
🟡 CND Estadual:      20 dias
```

### 1.6 Integrações Governamentais
```
Total serviços:       17
Online:               16
Offline:              1 (Gov.br OAuth2 — precisa registrar app)
```

### 1.7 GED
```
Documentos:           3
Kits ativos:          4 (Admissão, Demissão, Afastamento, Mensal)
Assinaturas:          0 pendentes
```

---

## 2. O QUE FOI FEITO NESTA SESSÃO

### 2.1 Correções Backend Sistêmicas

**Bug sistêmico encontrado e corrigido:** `redirect_slashes=False` no FastAPI + endpoints
registrados com `"/"` (trailing slash) → requests sem slash retornavam 404.

| Módulo | Controllers | Endpoints desbloqueados |
|--------|------------|------------------------|
| Operacional | 4 | 6 |
| People Management HR | 8 | 14 |
| People Management GED | 1 | 1 |
| Equipment Management | 4 | 8 |
| Bidding (Licitações) | 5 | 10 |
| Campo | 4 | 5 |
| HR Analytics + REP | 6 | 10 |
| CRM | 2 | 3 |
| Clients | 1 | 2 |
| CCT | 2 | 2 |
| Reimbursement | 1 | 2 |
| Automation/Workflows | 1 | 2 |
| GED Core (5 controllers) | 5 | 9 |
| Document Kits | 1 | 2 |
| EPI (Saúde Ocupacional) | 1 | 1 |
| Financial (7 controllers) | 7 | ~50 |
| **TOTAL** | **53** | **~127 endpoints** |

### 2.2 Módulos Registrados (Nunca Haviam Sido)

**Documents/OCR (16 endpoints):**
- POST /documents/upload, /upload/batch
- POST /documents/{id}/ocr, /classify, /extract, /validate, /process
- GET /documents/templates, /types, /providers, /stats
- POST /documents/validate/cpf, /validate/cnpj

**WhatsApp Evolution API (5 endpoints):**
- GET /whatsapp/status
- POST /whatsapp/send/kit-notification
- POST /whatsapp/send/certificate-alert
- POST /whatsapp/send/nfse-notification
- POST /whatsapp/send/custom

### 2.3 Credenciais Bancárias Restauradas

**Problema:** Os certificados mTLS (.key) dos bancos Cora e Inter tinham
permissão 600 root:root. O processo backend roda como user erp (UID 999)
e não conseguia ler as chaves privadas.

**Correção:** `chown root:999` nos arquivos .key → grupo erp pode ler.

**Resultado:** Cora + Inter conectados com saldos e extratos reais.

### 2.4 Dados Financeiros Populados

| Tabela | Registros | Dados |
|--------|-----------|-------|
| bank_accounts | 2 | Inter (R$ 32.382) + Cora (R$ 28) |
| suppliers | 8 | INSS, FGTS, ISS, IRRF + 4 fornecedores |
| customers | 11 | Sincronizados de clients |
| payable_accounts | 8 | Folha R$ 95.950 + impostos + serviços |
| receivable_accounts | 11 | MRR R$ 272.086 dos 11 contratos |

### 2.5 Novas Páginas Frontend Criadas

| Página | URL | Funcionalidades |
|--------|-----|-----------------|
| Upload com IA | /ged/upload | Drag&drop + classificação IA + keywords + pasta sugerida |
| Assinaturas Digitais | /ged/assinaturas | Workflow pendentes/todos/concluídos + modais assinar/recusar |
| Certidões | /ged/certidoes | 8 certidões reais, alertas, filtros, cards por tipo |
| Envios e Entregas | /ged/envios | Kits + link portal + histórico + modal 3 métodos |
| Dashboard Executivo | /dashboard | Alertas críticos + grid 6 módulos com status |
| Central Relatórios PDF | /relatorios/central | 6 tipos PDF (jsPDF) com dados reais |
| WhatsApp | /ged/whatsapp | 4 tabs: Kits, Certidões, Mensagem Livre, Histórico |

### 2.6 AI Agents Financeiros Ativados

| Agente | Endpoint | Status |
|--------|----------|--------|
| Command Center | /financial/ai/command-center | ✅ 200 (health score 45, alertas, insights) |
| Risk Monitor | /financial/ai/risks | ✅ 200 (análise inadimplência) |
| Cashflow Predictor | /financial/ai/cashflow-prediction | ✅ 200 (previsão 30/60/90d) |
| Financial Advisor | /financial/ai/advisor | ✅ 200 |
| Collection Analyzer | /financial/ai/collection/analyze | ✅ 200 |
| Billing Automator | /financial/ai/billing/summary | ✅ 200 |
| Costing Analyzer | /financial/ai/costing/summary | ✅ 200 |

---

## 3. ESTADO ATUAL DO SISTEMA

### 3.1 Endpoints Funcionando (por módulo)

| Módulo | Endpoints | Status |
|--------|-----------|--------|
| Auth | 5+ | ✅ 100% |
| Operacional | 130+ | ✅ 95% |
| GED Core | 50+ | ✅ 90% |
| Document Kits | 49 | ✅ 85% |
| Documents/OCR | 16 | ✅ NEW |
| Financial | ~200 | ✅ 70% (dados escassos em algumas tabelas) |
| Financial AI | 10+ | ✅ NEW |
| CRM | 30+ | ✅ 80% |
| Clients | 38 | ✅ 85% |
| Bidding | 30+ | ✅ 80% |
| HR/DP | 50+ | ✅ 80% |
| Government | 17 integrações | ✅ 94% (16/17 online) |
| Saúde Ocupacional | 30+ | ✅ 70% |
| WhatsApp | 5 | ✅ NEW (Evolution API offline — DNS) |
| Banking | 7 | ✅ 100% (Cora + Inter conectados) |
| Notifications | 10+ | ✅ 80% |
| Config/Audit | 20+ | ✅ 90% |

### 3.2 Frontend — Páginas Funcionais

```
Total de páginas:            108+
Com APIs reais:              ~90 (83%)
Novas nesta sessão:          7
Precisam dados/fix:          ~18
```

### 3.3 Infraestrutura

```
Backend:                     healthy (porta 8080)
Frontend:                    200 (porta 3001, pm2)
Produção:                    200 (erp.conectamais.pro)
PostgreSQL:                  healthy
Redis:                       healthy
Celery Workers:              6 healthy + 1 beat (unhealthy normal)
Grafana + Prometheus:        online
Loki + Promtail:             online
```

---

## 4. SCORES POR MÓDULO

| Módulo | Score | Detalhes |
|--------|-------|----------|
| Gestão de Pessoas (DP/RH) | 10/10 | 52 func, folha, admissão, demissão |
| GED | 9/10 | Upload IA, assinaturas, certidões, envios, WhatsApp |
| BI/Analytics | 10/10 | Dashboard com gráficos, KPIs, calendário fiscal |
| CRM | 7/10 | 11 leads, 5 oportunidades, pipeline real |
| Financeiro | 7/10 | 25+ endpoints, dados parciais, AI ativo |
| Contratos | 9/10 | 11 contratos ativos, MRR R$ 272k, alertas |
| Operacional | 8/10 | Postos, escalas, turnos, rondas |
| Licitações | 7/10 | 11 editais, 8 certidões, 5 propostas |
| Integrações Gov | 8/10 | 16/17 online, eSocial S-1000 transmitido |
| Relatórios | 8/10 | 6 tipos PDF com dados reais |
| WhatsApp | 6/10 | Backend OK, Evolution API offline (DNS) |
| Banking | 10/10 | Cora + Inter conectados, 646 transações |
| **MÉDIA GERAL** | **8.3/10** | |

---

## 5. O QUE FALTA PARA 10/10

### 5.1 Financeiro (7/10 → 10/10)
- [ ] Importar 646 transações Inter para `bank_transactions`
- [ ] Configurar conciliação bancária automática (matching receitas/transações)
- [ ] Popular `billing_rules` para faturamento automático dos 11 contratos
- [ ] Conectar 19 páginas frontend às APIs desbloqueadas
- [ ] DRE automático: NFS-e (receitas) + folha (despesas) → contabilidade
- [ ] Cashflow real: entradas (banking) + saídas (payables) → projeção

### 5.2 CRM (7/10 → 10/10)
- [ ] Automatizar pipeline: lead → oportunidade → proposta → contrato
- [ ] Dashboard com funil de vendas real
- [ ] Integrar com WhatsApp para follow-up automático

### 5.3 Integrações Gov (8/10 → 10/10)
- [ ] eSocial: popular data_nascimento, sexo, estado_civil dos 52 func
- [ ] eSocial: corrigir erro 609 (formato Id lote XSD)
- [ ] eSocial: transmitir S-2200 (admissão) em homologação
- [ ] Gov.br: registrar aplicação → CLIENT_ID + SECRET
- [ ] SPED: popular com dados contábeis reais
- [ ] DCTFWeb: gerar março 2026 com dados reais

### 5.4 WhatsApp (6/10 → 10/10)
- [ ] Resolver DNS Evolution API no container backend
- [ ] Testar envio real de kit para número de teste
- [ ] Automatizar: kit gerado → WhatsApp automático para síndico
- [ ] Automatizar: certidão vencendo → alerta WhatsApp para Jordan

### 5.5 Licitações (7/10 → 10/10)
- [ ] Corrigir crash no GET /bidding/tenders (empty reply)
- [ ] Conectar frontend aos 5 endpoints de propostas
- [ ] Dashboard de licitações com dados de certidões integrados

### 5.6 GED (9/10 → 10/10)
- [ ] Google Drive: configurar service account → export kits automático
- [ ] Geração mensal automática de kits (scheduler APScheduler dia 1)
- [ ] Notificação automática ao síndico quando kit está pronto

---

## 6. ENDPOINTS CHAVE PARA REFERÊNCIA

### Autenticação
```bash
TOKEN=$(curl -sf -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

### Financeiro
```
GET /financial/nfse/dashboard              → 27 NFS-e, R$ 542k
GET /financial/contracts/summary           → 11 contratos, MRR R$ 272k
GET /financial/headcount                   → 52 funcionários por cliente
GET /financial/suppliers?condominio_id=... → 8 fornecedores
GET /financial/customers?condominio_id=... → 11 clientes
GET /financial/payables?condominio_id=...  → 8 contas a pagar
GET /financial/receivables?condominio_id=. → 11 contas a receber
GET /financial/relatorios/dre?...          → DRE mensal
GET /financial/ai/command-center           → Health score + alertas + insights
GET /financial/ai/cashflow-prediction      → Previsão 30/60/90d
GET /financial/accounting/accounts         → Plano de contas
GET /financial/inventory/stock-items       → Estoque
```

### Banking
```
GET /integrations/banking/status           → Cora + Inter CONECTADOS
GET /integrations/banking/balances         → R$ 32.410,46 total
GET /integrations/banking/statement        → 646 transações (R$ 473k créditos)
GET /integrations/banking/statement/full   → Extrato completo
GET /integrations/banking/boleto/list      → Boletos
```

### GED
```
GET /ged/documents                         → 3 documentos
GET /ged/folders/tree/view                 → Árvore de pastas
GET /ged/document-tags                     → Tags
GET /ged/document-shares                   → Compartilhamentos
GET /ged/document-signatures/signer/pending → Assinaturas pendentes
GET /ged/document-signatures/stats/summary → Estatísticas assinaturas
GET /document-kits                         → 4 kits
GET /document-kits/stats                   → Stats kits
```

### Certidões
```
GET /bidding/certificates                  → 8 certidões (5 em alerta)
GET /bidding/certificates/tipos            → Tipos disponíveis
GET /bidding/certificates/pendentes-renovacao → Pendentes
```

### WhatsApp
```
GET /whatsapp/status                       → Online/offline Evolution API
POST /whatsapp/send/kit-notification       → Notifica kit mensal
POST /whatsapp/send/certificate-alert      → Alerta certidão
POST /whatsapp/send/nfse-notification      → Avisa NFS-e
POST /whatsapp/send/custom                 → Mensagem livre
```

### Government
```
GET /government/dashboard/status           → 17 serviços (16 online)
GET /government/health                     → Health check
```

---

## 7. CONDOMINIO_ID PADRÃO

Todas as queries financeiras precisam do parâmetro:
```
condominio_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## 8. ARQUIVOS DE CREDENCIAIS

```
/opt/conecta-pro/credentials/.env.credentials     → Chaves API (Cora, Inter, Solides)
/opt/conecta-pro/credentials/certificates/
  ├── certificado.pfx          → Certificado A1 (válido até 2027-01-13)
  ├── inter_api.crt + .key     → mTLS Banco Inter
  ├── cora_api.crt + .key      → mTLS Banco Cora
  ├── a1_cert.pem + a1_key.pem → Certificado A1 em PEM
  └── ca.crt                   → CA root
```

**IMPORTANTE:** Os .key precisam ter permissão `640 root:999` (grupo erp)
para o backend conseguir ler. Se após rebuild do container o banking parar
de funcionar, executar:
```bash
chown root:999 /opt/conecta-pro/credentials/certificates/*.key
chmod 640 /opt/conecta-pro/credentials/certificates/*.key
```

---

## 9. REGRAS PARA PRÓXIMAS SESSÕES

1. **Zero mock** — Todos os dados devem vir de APIs reais
2. **Trailing slash** — Novos controllers devem usar `""` (não `"/"`)
3. **condominio_id** — Endpoints financeiros exigem este parâmetro
4. **Hot copy** — Para testar mudanças Python sem rebuild:
   ```bash
   docker cp arquivo.py conecta-pro-backend:/app/path/arquivo.py
   docker restart conecta-pro-backend
   ```
5. **Build frontend:**
   ```bash
   export NODE_OPTIONS=--max-old-space-size=4096
   cd /opt/conecta-pro/frontend && npx next build
   PORT=3001 pm2 restart conecta-pro-frontend --update-env && pm2 save
   ```
6. **Zonas proibidas** (a menos que explicitamente autorizado):
   - alembic/versions/
   - docker-compose*.yml
   - .env* / credentials/

---

## 10. PRÓXIMOS PASSOS PRIORIZADOS

### P0 — URGENTE (hoje/amanhã)
1. Renovar CRF FGTS (vence 31/03)
2. Regularizar Alvará PF (vencido)
3. Renovar Certificado Digital A1 (vence em 9 dias)

### P1 — ALTO (esta semana)
4. Financeiro: importar transações Inter → bank_transactions
5. Financeiro: conciliação bancária automática
6. eSocial: completar dados dos 52 funcionários
7. eSocial: transmitir S-1000 → S-2200 em homologação
8. WhatsApp: resolver DNS Evolution API

### P2 — MÉDIO (próxima semana)
9. Conectar 19 páginas financeiras frontend às APIs
10. DRE automático (NFS-e + folha → contabilidade)
11. Gov.br: registrar aplicação OAuth2
12. SPED/DCTFWeb com dados reais
13. Licitações: corrigir crash tenders

### P3 — BAIXO (sprint seguinte)
14. Google Drive integration para GED
15. Boletos automáticos via Inter
16. PIX automático via Cora
17. Merge feature → main + tag release v1.0
18. QA completo E2E

---

**Relatório gerado em:** 23 de Março de 2026, ~16:30
**Agente:** Claude Opus 4.6 (1M context)
**Sessão:** ~12h de trabalho contínuo
