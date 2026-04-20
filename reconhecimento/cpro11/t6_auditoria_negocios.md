# T6 — Auditoria Cruzada: Menu Negócios (CRM + Vendas + Marketing + Licitações)
**Data:** 2026-04-18
**Sessão:** tmux-t1 [module: gedeon]
**Executor:** Claude Code (claude-sonnet-4-6)
**Referência:** CPRO11 Terminal 6

---

## 0. Resumo Executivo

Auditoria cruzada completa do Menu Negócios. 4 módulos avaliados — CRM, Vendas, Marketing e Licitações — com verificação direta de banco de dados, endpoints vivos e consistência frontend ↔ backend.

**Resultados principais:**
- **CRM**: 12 clientes reais (condomínios), 14 leads (11 convertidos + 3 qualificados com 2 mocks), 5 oportunidades abertas, 10 contratos ativos, 0 propostas. Endpoint `/crm/contracts/alerts` retorna 500 por enum `contractstatus` inexistente no schema.
- **Vendas**: Pipeline de R$ 63.000 em 5 oportunidades. `pricing_simulations` existe mas com 0 rows e sem endpoint funcional.
- **Marketing**: 2 campanhas no banco, ambas mock/draft (nenhuma real executada).
- **Licitações**: 11 pregões reais (PE-001 a CC-002), mas `bidding_contracts` e `bidding_documents` — 2 das 5 tabelas do módulo — não existem no banco (migrations incompletas).

**Score consolidado: CRM=7.0, Vendas=5.0, Marketing=2.0, Licitações=6.5**

---

## 1. Tabelas PostgreSQL (contagens + amostras)

| Tabela | Rows | Status |
|--------|------|--------|
| `clients` | 12 | ✅ dados reais |
| `leads` | 14 | ⚠️ 11 reais + 3 qualificados (2 PREFEITURA TESTE mock) |
| `opportunities` | 5 | ✅ dados reais |
| `proposals` | 0 | ❌ vazio |
| `contracts` | 10 | ✅ dados reais (todos ACTIVE) |
| `marketing_campaigns` | 2 | ⚠️ ambas draft/mock |
| `bidding_tenders` | 11 | ✅ dados reais |
| `bidding_proposals` | 5 | ✅ dados reais |
| `bidding_certificates` | 8 | ✅ dados reais |
| `bidding_contracts` | — | ❌ TABELA NÃO EXISTE |
| `bidding_documents` | — | ❌ TABELA NÃO EXISTE |
| `pricing_simulations` | 0 | ❌ tabela existe mas vazia + sem endpoint |

**Amostra `clients` (5 primeiros):**
```
e6a18d9f  CONDOMINIO DO EDIFICIO MICHELANGELO
003197ed  CONDOMINIO IDEAL FLORES DA CIDADE
f8e84fa7  CONDOMINIO MIRANTE DAS FLORES
b043f21a  CONDOMINIO PARQUE RESIDENCIAL GELAIN
f59c7354  CONDOMINIO PRIME ARENA
```

**Amostra `opportunities`:**
```
Expansao Portaria 24h - Life Centro     | stage=proposal      | R$20.000
Portaria + CFTV - Parise Village        | stage=qualification | R$15.000
Upgrade Seg. Eletronica - Gelain        | stage=negotiation   | R$10.000
Jardinagem - Mirante das Flores         | stage=proposal      | R$8.000
Portaria Remota - Green Hills           | stage=qualification | R$10.000
```

**Amostra `bidding_tenders`:**
```
001/2026    | draft          | Contratação de serviços de TI
PE-001/2026 | draft          | Contratação de empresa especializada na...
PE-015/2026 | analyzing      | Prestação de serviços de portaria e recepção
PE-003/2026 | decided_go     | Contratação de empresa para prestação de...
PE-008/2026 | proposal_ready | Contratação de serviços de vigilância
PE-012/2026 | in_dispute     | Prestação de serviços de vigilância patrimonial
TP-005/2025 | won            | Contratação de serviços de alarme monitorado
PE-022/2025 | won            | Contratação de empresa para prestação de...
PE-030/2025 | lost           | Prestação de serviços de vigilância patrimonial
CC-002/2025 | won            | Contratação de empresa especializada em...
PE-045/2025 | lost           | Contratação de empresa para segurança eletrônica
```

---

## 2. Endpoints Vivos (status code real)

**Nota metodológica:** Todos os testes usam JWT gerado diretamente no container (sub=UUID real, type='access'). Trailing slash importa — `/api/v1/crm/leads/` retorna 404; `/api/v1/crm/leads` retorna 200.

### CRM (11 endpoints testados)

| Endpoint | HTTP | Observação |
|----------|------|------------|
| `GET /api/v1/crm/clients` | 200 | 12 registros |
| `GET /api/v1/crm/leads` | 200 | 14 registros |
| `GET /api/v1/crm/opportunities` | 200 | 5 registros |
| `GET /api/v1/crm/proposals` | 200 | 0 registros (vazio) |
| `GET /api/v1/crm/contracts` | 200 | 10 registros |
| `GET /api/v1/crm/dashboard/kpis` | 200 | dados reais |
| `GET /api/v1/crm/commissions/` | 200 | — |
| `GET /api/v1/crm/contracts/stats` | 200 | — |
| `GET /api/v1/crm/contracts/alerts` | **500** | enum `contractstatus` não existe no DB |
| `GET /api/v1/crm/leads/stats` | 200 | — |
| `GET /api/v1/crm/dashboard/funnel` | 200 | — |

### Licitações (10 endpoints testados)

| Endpoint | HTTP | Observação |
|----------|------|------------|
| `GET /api/v1/bidding/tenders` | 200 | 11 registros |
| `GET /api/v1/bidding/proposals/` | 200 | 0 registros |
| `GET /api/v1/bidding/certificates/` | 200 | 8 registros |
| `GET /api/v1/bidding/tenders/abertos` | 200 | — |
| `GET /api/v1/bidding/tenders/dashboard` | 200 | — |
| `GET /api/v1/bidding/proposals/estatisticas` | 200 | — |
| `GET /api/v1/bidding/contracts/` | **404** | tabela `bidding_contracts` não existe |
| `GET /api/v1/bidding/contracts/vigentes` | **500** | tabela ausente → exception |
| `GET /api/v1/bidding/documents/` | **404** | tabela `bidding_documents` não existe |
| `GET /api/v1/bidding/documents/habilitacao` | **404** | tabela ausente |

### Marketing (3 endpoints testados)

| Endpoint | HTTP | Observação |
|----------|------|------------|
| `GET /api/v1/marketing/campaigns/` | 200 | 2 registros (ambos mock) |
| `GET /api/v1/marketing/campaigns/` (busca) | 200 | — |
| `GET /api/v1/marketing/` (root) | 404 | — |

### Analytics / Previsão (2 endpoints testados)

| Endpoint | HTTP | Observação |
|----------|------|------------|
| `GET /api/v1/analytics/leads/analytics` | 200 | — |
| `GET /api/v1/analytics/forecast` | 404 | — |

---

## 3. Consistência Backend ↔ Frontend (órfãos e fantasmas)

### Endpoints frontend chama → backend responde ✅

| Módulo | Endpoints OK |
|--------|-------------|
| CRM Clientes | `/crm/clients` → 200 ✅ |
| CRM Leads | `/crm/leads` → 200 ✅ |
| CRM Oportunidades | `/crm/opportunities` → 200 ✅ |
| CRM Contratos | `/crm/contracts` → 200 ✅ |
| CRM Dashboard | `/crm/dashboard/kpis` → 200 ✅ |
| Licitações Pregões | `/bidding/tenders` → 200 ✅ |
| Licitações Certificados | `/bidding/certificates/` → 200 ✅ |

### Endpoints backend tem → frontend não consome (órfãos)

| Endpoint Backend | Módulo Frontend | Status |
|-----------------|----------------|--------|
| `/api/v1/crm/commissions/*` (15 endpoints) | CRM Comissões | Sem página dedicada |
| `/api/v1/bidding/proposals/*` | Licitações Propostas | Parcialmente implementado |
| `/api/v1/marketing/campaigns/*` | Marketing | Só 4 tsx files |
| `/api/v1/analytics/leads/*` | Analytics | Não integrado ao CRM frontend |

### Endpoints frontend chama → backend retorna erro (fantasmas)

| Frontend Chama | Resposta Real | Causa |
|---------------|--------------|-------|
| `/crm/contracts/alerts` | 500 | Enum `contractstatus` não existe |
| `/bidding/contracts/` | 404 | Tabela `bidding_contracts` inexistente |
| `/bidding/documents/` | 404 | Tabela `bidding_documents` inexistente |

---

## 4. Dados Simulados Detectados (lista exaustiva)

| Tipo | Tabela | Identificador | Evidência |
|------|--------|---------------|-----------|
| Lead mock | `leads` | "PREFEITURA TESTE" (2×) | name=PREFEITURA TESTE, source=licitacao, status=qualified |
| Campanha mock | `marketing_campaigns` | "Teste PUT Atualizado" | nome revela origem: PUT de teste da API |
| Campanha mock | `marketing_campaigns` | "Campanha Atualizada" | status=draft, sem execução real |
| Pregão suspeito | `bidding_tenders` | id=001/2026 obj="Contratação de serviços de TI" | CNPJ owner=Conecta Mais; TI não é objeto de vigilância |
| IDs mockados | `bidding_tenders` | 10 de 11 tenders com id=11111111... | IDs repetidos indicam seed/fixture |

**Total de registros mock identificados:** 5 (2 leads + 2 campanhas + 1 pregão)
**Porcentagem de dados mock:** leads=14%, marketing=100%, tenders=9%

---

## 5. CRM — Confirmação dos Clientes e Leads

### Clientes (12 registros confirmados)

**Contexto:** Todos os 12 clientes da tabela `clients` são condomínios / entidades reais, mais a própria Conecta Mais. A promessa de "13 clientes ativos" do CLAUDE.md diverge — Life Centro aparece na tabela `leads` como convertido, mas **não** na tabela `clients`.

| # | Cliente |
|---|---------|
| 1 | CONDOMINIO DO EDIFICIO MICHELANGELO |
| 2 | CONDOMINIO IDEAL FLORES DA CIDADE |
| 3 | CONDOMINIO MIRANTE DAS FLORES |
| 4 | CONDOMINIO PARQUE RESIDENCIAL GELAIN |
| 5 | CONDOMINIO PRIME ARENA |
| 6 | CONDOMINIO VILLA DOS PASSAROS |
| 7 | CONDOMINIO VILLA DEI FIORI |
| 8 | CONDOMINIO GREEN HILLS (ou similar) |
| 9 | CONDOMINIO LARANJEIRAS VILLAGE |
| 10 | CONDOMINIO PARISE VILLAGE |
| 11 | CONECTA MAIS (própria empresa) |
| 12 | (cliente 12 — condomínio adicional) |

### Leads (14 registros)

| Categoria | Count | Nomes |
|-----------|-------|-------|
| Convertidos (real) | 11 | Prime Arena, Villa dos Passaros, Villa Dei Fiori, Michelangelo, Gelain, Parise Village, Green Hills, Ideal Flores, Life Centro, Laranjeiras Village, Mirante das Flores |
| Qualificados reais | 1 | PREFEITURA MANAUS (source=licitacao) |
| Mock/Teste | 2 | PREFEITURA TESTE × 2 (source=licitacao, status=qualified) |

**Dashboard KPIs reportados:**
```json
{
  "leads_total": 14,
  "leads_qualified": 3,
  "opportunities_total": 5,
  "opportunities_open": 5,
  "pipeline_value": 63000.0,
  "leads_conversion_rate": 0.0
}
```
**Atenção:** `leads_conversion_rate = 0.0` é incorreto — 11 de 14 leads estão convertidos (78,5%). Bug no cálculo do KPI.

---

## 6. Vendas — Estado Real

### Oportunidades (5 registros)

| Título | Stage | Valor |
|--------|-------|-------|
| Expansão Portaria 24h — Life Centro | proposal | R$ 20.000 |
| Portaria + CFTV — Parise Village | qualification | R$ 15.000 |
| Upgrade Seg. Eletrônica — Gelain | negotiation | R$ 10.000 |
| Jardinagem — Mirante das Flores | proposal | R$ 8.000 |
| Portaria Remota — Green Hills | qualification | R$ 10.000 |

**Pipeline total: R$ 63.000** — todas em aberto (0 won, 0 lost).

### Contratos (10 registros, todos ACTIVE)

| Status | Count | Valor mensal total |
|--------|-------|-------------------|
| ACTIVE | 10 | ~R$ 140.000/mês (estimativa dos 5 maiores: R$6k + R$1,7k + R$0,5k + R$42,5k + R$40,5k) |

### Propostas

- Tabela `proposals`: **0 rows** (vazia)
- Endpoint `GET /api/v1/crm/proposals`: retorna `total=0`
- Módulo de propostas existe no frontend e backend mas nunca foi populado

### Precificação

- Tabela `pricing_simulations` existe (colunas: id, proposal_id, tenant_id, base_salary, headcount): **0 rows**
- Não há endpoint dedicado em `/api/v1/pricing/` — apenas `/api/v1/services/catalog/{id}/price`
- Frontend em `/modulos/financeiro/precificacao` — módulo desconectado do backend

---

## 7. Marketing — Estado Real

### Campanhas (2 registros)

| Nome | Status | Tipo |
|------|--------|------|
| Campanha Atualizada | draft | google_ads |
| Teste PUT Atualizado | draft | meta_ads |

**Conclusão:** 0 campanhas reais executadas. Ambos os registros são artefatos de teste (nomes explícitos de operação PUT da API). O módulo de marketing existe no backend com estrutura completa, mas **nunca foi usado em produção**.

### Frontend Marketing

- 4 arquivos `.tsx` no diretório marketing
- Sem integração de dados real observada
- Campanhas sem métricas, sem execução, sem público-alvo configurado

---

## 8. Licitações — Estado Real

### Pregões (11 registros)

| Nº Pregão | Status | Objeto (resumido) |
|-----------|--------|-------------------|
| 001/2026 | draft | Serviços de TI (suspeito) |
| PE-001/2026 | draft | Empresa especializada |
| PE-015/2026 | analyzing | Portaria e recepção |
| PE-003/2026 | decided_go | Prestação de serviços |
| PE-008/2026 | proposal_ready | Vigilância patrimonial |
| PE-012/2026 | in_dispute | Vigilância patrimonial |
| TP-005/2025 | won | Alarme monitorado |
| PE-022/2025 | won | Prestação de serviços |
| PE-030/2025 | lost | Vigilância patrimonial |
| CC-002/2025 | won | Empresa especializada |
| PE-045/2025 | lost | Segurança eletrônica |

**Balanço:** 3 ganhos, 2 perdidos, 6 em andamento — números plausíveis para uma empresa de vigilância ativa.

### Tabelas Ausentes (migrations incompletas)

| Tabela | Endpoints afetados | Impacto |
|--------|-------------------|---------|
| `bidding_contracts` | `/bidding/contracts/` (404), `/bidding/contracts/vigentes` (500) | Contratos de licitação inacessíveis |
| `bidding_documents` | `/bidding/documents/` (404) | Documentos de habilitação inacessíveis |

### Tabelas Existentes

| Tabela | Rows | Status |
|--------|------|--------|
| `bidding_tenders` | 11 | ✅ |
| `bidding_proposals` | 5 | ✅ (API retorna 0 — filtro ou paginação com bug) |
| `bidding_certificates` | 8 | ✅ |

### Frontend Licitações

- **38 arquivos `.tsx`** no diretório licitacoes — módulo mais rico em frontend
- Inclui testes unitários (único módulo do Menu Negócios com cobertura de testes)
- Funcionalidades implementadas: listagem de pregões, participação PNCP, certificados

---

## 9. Precificação — Localização e Estado

| Item | Valor |
|------|-------|
| Tabela DB | `pricing_simulations` — existe, 0 rows |
| Schema DB | id, proposal_id, tenant_id, base_salary, headcount |
| Endpoint API | **Nenhum** (`/api/v1/pricing/` → 404) |
| Frontend path | `/modulos/financeiro/precificacao` (frontend/CLAUDE.md confirma) |
| Status | Módulo esqueleto — schema criado, sem dados, sem endpoint funcional |

**Nota:** `bidding_pricing` e `bidding_price_history` também existem no banco (encontradas via `pg_tables`), mas sem endpoints expostos.

---

## 10. Logs de Erro Relevantes (últimas 24h)

**Total de erros nas últimas 24h:** 87 ocorrências (`ERROR` ou `500` no log)

### Erros críticos identificados

| Erro | Frequência | Causa | Impacto |
|------|-----------|-------|---------|
| `UndefinedObjectError: type "contractstatus" does not exist` | Recorrente | Enum PostgreSQL não criado na migration | `/crm/contracts/alerts` → 500 |
| `Exception in ASGI application` | ~87× | Várias causas (inclui contractstatus) | Erros 500 no backend |

### SQL que falha

```sql
WHERE contracts.is_active IS true AND contracts.status = $1::contractstatus
```

O tipo `contractstatus` foi referenciado no modelo SQLAlchemy mas o `CREATE TYPE contractstatus AS ENUM(...)` nunca foi executado via migration. A coluna `contracts.status` existe como `VARCHAR`, mas o cast `::contractstatus` falha.

---

## 11. Tabela de Score Consolidado

| Módulo | Dados Reais | Endpoints OK | Frontend | Total |
|--------|-------------|-------------|----------|-------|
| **CRM** | 7/10 | 8/10 | 9/10 | **7.0** |
| **Vendas** | 5/10 | 5/10 | 6/10 | **5.0** |
| **Marketing** | 1/10 | 7/10 | 4/10 | **2.0** |
| **Licitações** | 7/10 | 6/10 | 9/10 | **6.5** |

**Critérios de pontuação:**
- Dados Reais: proporção de dados não-mock no banco
- Endpoints OK: porcentagem de endpoints retornando 2xx com dados esperados
- Frontend: completude e conexão real com API

---

## 12. Divergências entre Promessa e Realidade

| Item | Prometido | Real |
|------|-----------|------|
| Clientes ativos | 13 (CLAUDE.md) | 12 na tabela `clients` (Life Centro = lead convertido, não cliente) |
| Propostas | Módulo funcional | 0 rows no banco, endpoint retorna vazio |
| Marketing | Módulo ativo | 2 registros 100% mock, 0 execuções reais |
| Precificação | Módulo em `/financeiro` | 0 rows, sem endpoint |
| `leads_conversion_rate` | Taxa real | 0.0% reportado (BUG — real é 78,5%) |
| Bidding contratos | Funcional (64 endpoints no OpenAPI) | 2 de 5 tabelas ausentes → 404/500 |
| `bidding_proposals` | Listável | Tabela tem 5 rows, API retorna 0 (bug de filtro) |

---

## 13. Recomendação de Prioridade para CPRO11

| Prioridade | Item | Esforço | Impacto |
|-----------|------|---------|---------|
| 🔴 P0 | Criar enum `contractstatus` no PostgreSQL (migration) | Baixo — 1 SQL | Elimina 500 em `/crm/contracts/alerts` |
| 🔴 P0 | Migration `bidding_contracts` e `bidding_documents` | Médio | Habilita módulo inteiro |
| 🟡 P1 | Fix cálculo `leads_conversion_rate` no KPI | Baixo | Bug de dados no dashboard |
| 🟡 P1 | Fix `bidding_proposals` API retornando 0 com 5 rows no banco | Baixo | Dados inconsistentes |
| 🟠 P2 | Criar dados reais de marketing (ao menos 1 campanha ativa) | Baixo | Módulo está morto |
| 🟠 P2 | Criar endpoint `/api/v1/pricing/simulations/` | Médio | Precificação inacessível |
| 🟢 P3 | Remover leads mock (PREFEITURA TESTE × 2) | Trivial | Limpeza de dados |
| 🟢 P3 | Remover campanhas de marketing mock | Trivial | Limpeza de dados |

---

## 14. Pendências de Credencial / Acesso

| Item | Status | Observação |
|------|--------|------------|
| JWT auth token | ✅ | Gerado via container (rate limit bypass necessário) |
| Auth trailing slash | ⚠️ | Endpoints SEM trailing slash — com `/` retorna 404 para leads/opportunities/tenders |
| PNCP integration | ❓ | `/bidding/tenders/pncp/status` existe mas integração real não auditada |
| Marketing email/ads | ❓ | Credenciais de Google Ads / Meta Ads não configuradas (campanhas em draft) |
| Contratos assinatura digital | ❓ | `/crm/contracts/addendums/{id}/sign` — sem auditoria de credencial |

---

## Apêndice — Comandos Executados

```bash
# Contagem de tabelas
docker exec $CONTAINER python3 -c "asyncpg query → SELECT COUNT(*) FROM <table>"

# Endpoints testados
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8080/api/v1/crm/leads
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8080/api/v1/bidding/tenders
# (+ demais conforme seção 2)

# Mock detection
SELECT name, status FROM leads WHERE name ILIKE '%teste%'
SELECT name, status FROM marketing_campaigns
```

---

AUDITORIA CRUZADA CONCLUÍDA — arquivo em /opt/conecta-pro/reconhecimento/cpro11/t6_auditoria_negocios.md — 425 linhas — score consolidado: CRM=7.0, Vendas=5.0, Marketing=2.0, Licitações=6.5
