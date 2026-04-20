# CONTRATO CRM / VENDAS — Conecta PRO
**Versão:** v1.3
**Data:** 2026-04-20
**Mantenedor:** Opus CPRO 11
**Escopo:** Menu "Negócios" → CRM / Vendas (tudo que vive em `modules/crm/` no backend e `frontend/src/app/modulos/crm/`)
**Fora de escopo:** Marketing, Licitações (sprints futuras)

---

## §0 Referências Externas Obrigatórias

- `/opt/conecta-pro/PADRAO_PROMPTS_CONECTA_PRO.md` — metodologia CPRO 9 (§13 universal)
- `/opt/conecta-pro/CONTRACTS_GEDEON.md` — contrato irmão (CPRO 10) — **NÃO MODIFICAR**
- `/opt/conecta-pro/reconhecimento/cpro11/t4_backend_negocios.md` — baseline backend
- `/opt/conecta-pro/reconhecimento/cpro11/t5_frontend_negocios.md` — baseline frontend
- `/opt/conecta-pro/reconhecimento/cpro11/t6_auditoria_negocios.md` — baseline dados

---

## §1 Invariantes Universais (herdadas do CPRO 9)

### §1.1 Infraestrutura
- **VPS:** srv1134814.hstgr.cloud (82.25.75.74), Hostinger KV4
- **Backend:** FastAPI + PostgreSQL + Redis + Celery, porta 8080, path `/opt/conecta-pro/backend/`
- **Frontend:** Next.js 16 + React 19 + TypeScript + Tailwind, porta 3001 via Docker
- **Branch ativa:** `feature/people-management-reorganization`
- **Produção:** `erp.conectamais.pro` (login: `jjesus@conectamais.pro`)
- **tmux:** sessões t1–t6 (t1–t3 = CPRO 10 GEDEON, t4–t6 = CPRO 11 CRM). Nunca abrir terminal fora de tmux.

### §1.2 Zonas Proibidas (NUNCA MODIFICAR)
```
backend/modules/financial/           ← produção bancária (Inter)
backend/modules/government_integrations/  ← certificados A1 em uso
backend/modules/gedeon/              ← CPRO 10 em continuidade
backend/modules/bidding/             ← CPRO 11 sprint futura
backend/modules/crm/controllers/marketing_controller.py  ← sprint futura
backend/alembic/versions/*.py        ← migrations já commitadas (criar NOVAS)
backend/main_production.py           ← registro de rotas (apenas adicionar se indispensável)
backend/docker-compose*.yml
backend/.env*
backend/credentials/

frontend/src/app/modulos/gedeon/     ← CPRO 10
frontend/src/app/modulos/licitacoes/ ← sprint futura
frontend/src/app/modulos/marketing/  ← sprint futura
frontend/src/app/modulos/fiscal/     ← fora de escopo
frontend/src/app/modulos/dp/         ← fora de escopo
frontend/src/app/modulos/operacional/ ← fora de escopo
```

### §1.3 Convenções de Código
- **Backend:** Pylint ≥ 99/100, type hints obrigatórios, zero `print()` (usar logger)
- **Frontend:** TypeScript estrito, **zero `any`** novos (os 38 existentes no CRM entram no backlog P2), `useQuery + staleTime` (nunca `useState([])` para dados remotos)
- **Migrations:** Alembic, sempre com `down_revision` correto e `downgrade()` reversível
- **Endpoints novos:** obrigatoriamente com `Depends(get_current_user)` (lição §13-Bug 7)
- **Commits:** 2 separados conforme §13.3 — primeiro docs (atualização deste contrato), depois code
- **Nunca dados mock.** Qualquer linha "Teste", "lorem", "Prefeitura Teste", "Cliente Exemplo" = defeito a remover.

### §1.4 Validação de Qualidade
- Backend: endpoint retorna 200 com **dados reais** — array vazio `[]` ou erro silencioso = falha
- Frontend: **não basta HTML 200.** Validação em 4 camadas (lição §13-Bug 6):
  1. HTML referencia chunk-hash correto
  2. Chunk existe no filesystem
  3. Chunk contém strings preservadas do componente
  4. Network trace no DevTools mostra requisições esperadas
- CIC (Claude in Chrome) é verdade final — terminal diz "10/10", CIC valida

### §1.5 Certificado A1
- Path: `/opt/conecta-pro/credentials/certificates/certificado.pfx`
- Senha: `Conecta123`
- Válido até: Janeiro/2027
- CN: JORDAN SANTOS DE JESUS LTDA:35710481000103
- Uso no CRM: nenhum (apenas Licitações)

---

## §13 Princípios de Engenharia (universais, §13.5)

> Os 6 princípios nasceram no CPRO 9. São **invioláveis**. Cada prompt do CPRO 11 cita explicitamente o §13 mais relevante no STEP 0.

### §13.1 — Chesterton (Não Derrubar Cercas)
Se você encontrar algo estranho (tabela vazia, função esquisita, rota 404 onde deveria 200), **NÃO corrija ainda**. Investigue, documente, pergunte. A cerca está lá por razão que você ainda não vê.

**Aplicação CPRO 11:** `modules/comercial/` com 9 pastas vazias. Decisão: **preservar, investigar depois**. `lead_scores` vazio apesar do ML existir. `pricing_simulations` vazio apesar dos controllers de 12K existirem. Todos são cercas de Chesterton. Investigar antes de "consertar".

### §13.2 — Falsificação Rigorosa em 3 Níveis
Todo prompt crítico deve ter ≥ 1 teste 🔴 (rigoroso) ao final.

| Nível | Exige | Exemplo CRM |
|---|---|---|
| 🟢 Básico | input inválido → erro | `create_opportunity(stage=None) → raises ValidationError` |
| 🟡 Médio | input de outro tipo não passa threshold | passar objeto `endereco` como string → rejeitar |
| 🔴 Rigoroso | regressão de bug conhecido, monkey-patch, ou property-based | "React Error #31 do endereco-objeto nunca mais deve aparecer em nenhum cliente (E2E CIC)" |

### §13.3 — Documentar ANTES de Corrigir
Ordem obrigatória:
1. Atualizar este contrato (incrementar versão: v1.0 → v1.1)
2. **Commit docs:** `docs: CONTRATO CRM v1.1 — <descoberta>`
3. Corrigir código
4. **Commit code:** `fix/feat: <o que>, respeitando CONTRATO CRM v1.1`

Ordem inversa é PROIBIDA. Docs primeiro força raciocínio estruturado.

### §13.4 — Escopo é Sagrado
Cada prompt tem UM escopo. Descobriu trabalho adicional? Lista em "Trabalho Adicional Identificado" no relatório — **não faz**. Jordan decide se vira prompt próprio.

**Aplicação CPRO 11:** T4 só mexe backend. T5 só mexe frontend. T6 só audita/limpa dados. Ninguém invade o terreno do outro, mesmo que pareça óbvio.

### §13.5 — Aplicação Universal
Todo terminal, toda instância, toda fase. Prompts pequenos também seguem.

### §13.6 — STEP 0 Referencia Princípio
Todo prompt começa com STEP 0:
```
STEP 0 — CONTRATO
Responda:
[ ] Versão atual do Contrato CRM/Vendas: ___
[ ] Princípio §13 mais relevante: ___ (2 linhas)
[ ] Em 3 linhas, o que VAI fazer: ___
```

---

## §20 Estado-Atual-Validado (2026-04-20)

Verdade base consolidada de T4 + T5 + T6 + CIC E2E. Qualquer divergência descoberta = §13.1 Chesterton (investigar, não "corrigir").

### §20.1 Backend (score t4 = 92/100)

- **41 arquivos** em `modules/crm/`
- **5 models ORM:** `leads`, `opportunities`, `proposals` (+items/templates/approvals), `contracts` (+items/addendums/templates/sla_reports), `commissions` (+rules/payments/summaries)
- **10 services:** LeadService, OpportunityService, ProposalService, ContractService, CommissionService, **PricingEngine**, PipelineService, **CRM360Service** (RFM: VIP/Premium/Standard/Bronze/Prospect/Churning/Inactive), DashboardService, SignatureIntegration (5 provedores: DocuSign/ClickSign/D4Sign/Autentique/Interno)
- **~55 endpoints** REST
- **225 funções de teste** — zero TODOs no código
- **Event Bus ativo:** publica `CRM_LEAD_CONVERTIDO`, `CRM_PROPOSTA_APROVADA`, `CRM_CONTRATO_ATIVO` → GEDEON
- **Zero agentes IA nativos** (heurísticas em `LeadService.get_recommended_action`, ML em `modules/analytics/`)

### §20.2 Frontend (score t5 estático = 7/10, pós-CIC = 5.5/10)

- **9 rotas** em `app/modulos/crm/`: Dashboard, Clientes, Clientes/[id], Leads, Oportunidades (Kanban), Propostas, Contratos, Contatos, Comissões, Precificação
- **95+ hooks** em `hooks/crm/useCRM.ts`
- **4 componentes** em `components/crm/` (modais)
- **38 `: any`** — débito técnico P2
- **Zero Server Components**, zero testes frontend
- **Precificação e Ver-360°** = joias do módulo

### §20.3 Dados reais no PostgreSQL (verdade confirmada por t6 + CIC)

> **Atualizado em v1.3** — após higiene T6 (2026-04-20, commit cpro11_t6_hygiene.sql 8/8 ✅)

| Tabela | Rows (pré-T6) | Rows (pós-T6) | Observação |
|---|---|---|---|
| `clients` | 12 | **11** | Removido "Matriz escritório" (CNPJ 00000000000000 duplicado) + condomínio TEST-COND-001 em cascata |
| `leads` | 14 | **11** | Removidos 2× PREFEITURA TESTE + PREFEITURA MANAUS (mocks). Life Centro preservado (tem opportunity FK) |
| `opportunities` | 5 | 5 | Pipeline R$ 63.000 — condomínios reais |
| `contracts` | 10 | 10 | Todos ACTIVE |
| `crm_activities` | 1 | **0** | Removido "Teste auditoria" (mock) |
| `crm_contacts` | 1 | **0** | Removido "Teste" (mock) |
| `lead_scores` | 0 | 0 | Chesterton §13.1 ✅ — ML existe mas nunca populou (intencional) |
| `proposals` + 7 tabelas relacionadas | 0 | 0 | Módulo completo vazio (intencional) |
| `commission_rules` + 4 tabelas | 0 | 0 | Chesterton §13.1 ✅ — 22 colunas, produto novo, nunca cadastrado |
| `pricing_simulations` | 0 | 0 | Chesterton §13.1 ✅ — Controllers existem (12K) — aguarda propostas |

### §20.4 Os 11 clientes pós-higiene T6 (verdade atualizada v1.3)

1. CONDOMINIO DO EDIFICIO MICHELANGELO (04911208000113)
2. CONDOMINIO IDEAL FLORES DA CIDADE (23147782000191)
3. CONDOMINIO MIRANTE DAS FLORES (52605708000170)
4. CONDOMINIO PARQUE RESIDENCIAL GELAIN (00736037000182)
5. CONDOMINIO PRIME ARENA (47405340000166)
6. CONDOMINIO RESIDENCIAL GREEN HILLS (08063476000183)
7. CONDOMINIO RESIDENCIAL PARISE VILLAGE (34857941000168)
8. CONDOMINIO RESIDENCIAL VILLA DOS PASSAROS (13221953000121)
9. CONDOMINIO VILLA DEI FIORI (02153384000108)
10. RESIDENCIAL LARANJEIRAS VILLAGE (24632786000128)
11. CONECTA MAIS - Segurança e Tecnologia (CNPJ `00000000000000`) — empresa proprietária

Removido: "Matriz escritório" (CNPJ `00000000000000` duplicado, tinha condomínio TEST-COND-001 em cascata com 29 kit_items + 4 document_kits — todos removidos).
**Pendente:** CONDOMINIO LIFE CENTRO — não existe em clients. Lead `5839bcd2` status=converted com client_id=NULL + 1 opportunity. Requer criação manual do registro de cliente.

### §20.5 Integrações Externas

| Integração | Disponível no VPS | Usada pelo CRM? |
|---|---|---|
| Banco Inter | ✅ `modules/financial/` | ❌ Só financeiro |
| WhatsApp Evolution API | ✅ `main_production.py:929` | ❌ Sprint Marketing |
| SMTP `core/mailer.py` | ✅ Global | ❌ Não usa |
| SendGrid/Mailgun | ⚠️ Schema sem impl | ❌ Sprint Marketing |
| Solides | ✅ RH/DP | ❌ Não aplicável |
| Certificado A1 | ✅ | ❌ Só Licitações |
| Claude API (`ANTHROPIC_API_KEY`) | ✅ `bidding/agents/analyst_agent.py` | ❌ Só Licitações |
| DocuSign/ClickSign/D4Sign/Autentique | ✅ `crm/services/signature_integration.py` | ✅ **CRM usa** (5 provedores) |

---

## §21 Backlog CPRO 11 Consolidado (T4 + T5 + T6 + CIC)

### P0 — Bloqueiam uso ou corrompem dados (sprint atual)

| # | Bug | Dono | Evidência |
|---|---|---|---|
| P0.1 | Enum PG `contractstatus` não existe → 3 endpoints 500 (`/crm/contracts/alerts`, `/crm/contracts/templates`, `/crm/proposals/templates`) | **T4** | 87 erros em 24h nos logs |
| P0.2 | `/crm/clients/{id}` retorna `endereco` como objeto estruturado → **React Error #31** quebra a tela inteira de detalhe de cliente | **T4+T5** | CIC reproduziu 100% |
| P0.3 | Coluna Nome vazia em Clientes (12/12), Leads (14/14), Contratos (10/10) — mismatch schema `name` vs `trade_name`/`legal_name` | **T5** (dedução do contrato API) | CIC confirmou |
| P0.4 | **Todos os 14 leads** exibidos com status "Novo" (ignora `converted`/`qualified`/`new` do DB) | **T5** | CIC confirmou |
| P0.5 | KPI Dashboard `Clientes=3` enquanto lista mostra 12 (endpoints divergentes) | **T4+T5** | CIC confirmou |
| P0.6 | Contratos: **MRR = "R$ NaN"** (cálculo quebrado, provável soma com null) | **T4+T5** | CIC confirmou |
| P0.7 | Modal "Nova Oportunidade": Status "Novo" não existe no enum backend (valores reais: QUALIFICATION, NEEDS_ANALYSIS, PROPOSAL, NEGOTIATION, CLOSED_WON, CLOSED_LOST) | **T5** | CIC confirmou |
| P0.8 | Modal "Nova Oportunidade": Cliente e Responsável são inputs de texto livre (sem FK para `clients.id` e `users.id`) | **T5** | CIC confirmou |
| P0.9 | Life Centro: `leads.client_id IS NULL` apesar de status `converted` | **T6** | t6 flagou |
| P0.10 | Duplicata Conecta Mais (CNPJ `00000000000000` × 2 em `clients`) | **T6** | CIC confirmou |
| P0.11 | `leads_conversion_rate = 0.0` no KPI (real é 78,5%) | **T4** | t6 + CIC |
| P0.12 | `bidding_proposals` API retorna 0, DB tem 5 rows (fora de escopo desta sprint — registrar) | — | t6 flagou |

### P1 — Qualidade / UX (sprint atual, após P0 fechado)

| # | Bug | Dono |
|---|---|---|
| P1.1 | Frontend silencia 500 → hooks retornam 0/vazio (ex: `Alertas=0` oculta erro real em Contratos) | T5 |
| P1.2 | "Ver detalhes" de Contrato é botão morto (não navega) | T5 |
| P1.3 | Coluna Origem "-" em todos os leads (enum `source` não mapeado) | T5 |
| P1.4 | Coluna Tipo "-" em todos os clientes (`client_type` não mapeado) | T5 |
| P1.5 | KPI Condomínios=0 em Clientes (todos são condomínios — filtro errado) | T4+T5 |
| P1.6 | KPIs de Oportunidades (Em Negociação=0, Propostas=0) divergem do Kanban visual | T4+T5 |
| P1.7 | Propostas exibe "Erro ao carregar" mesmo em módulo vazio (provável 500 de templates) | T4+T5 |
| P1.8 | Tipo "Limpeza" existe em contratos reais mas não no catálogo do Simulador de Precificação | T5 |
| P1.9 | WebSocket 404 tentando conectar no CRM (17 tentativas registradas) — WS só existe em Licitações | T5 |
| P1.10 | 2 mocks "PREFEITURA TESTE" em `leads` | T6 |
| P1.11 | 1 mock "Teste auditoria" em `crm_activities` | T6 |
| P1.12 | 1 mock "Teste" em `crm_contacts` | T6 |
| P1.13 | Unificar precificação: duplicata entre `modules/financial/` e `modules/crm/` | T4 |
| P1.14 | `commission_rules` com 0 rows — vazio intencional? (§13.1 investigar) | T6 |

### P2 — Higiene técnica (sprints futuras)

- 38 `: any` no CRM frontend
- Cor de acento divergente do brand (usar `#0A2540`, `#1E3A5F`, `#2E5984`, `#FF6B35`)
- Sem breadcrumbs
- Zero Server Components
- Zero testes frontend em CRM (Licitações tem 6)
- `lead_scores` vazio apesar do ML (§13.1 Chesterton)
- `pricing_simulations` vazio apesar dos controllers (§13.1 Chesterton)
- `modules/comercial/` stub vazio (§13.1 Chesterton — preservar, reavaliar em 30 dias)

### P3 — Futuro

- Módulo "Vendas" separado de "CRM" (apenas se §13.1 investigar revelar que comercial/ tinha intenção arquitetural)
- Agentes IA nativos no CRM (hoje só ML em `analytics/`)
- Integração WhatsApp Evolution API → CRM (atualmente só em router separado)

---

## §22 Protocolo de Execução dos 3 Terminais Paralelos

### §22.1 Distribuição
- **T4 (Backend owner):** P0.1, P0.2 backend-side, P0.5 backend-side, P0.6 backend-side, P0.11, P1.5 backend, P1.6 backend, P1.13
- **T5 (Frontend owner):** P0.2 frontend-side, P0.3, P0.4, P0.5 frontend, P0.6 frontend, P0.7, P0.8, P1.1–P1.9 frontend
- **T6 (Cross-audit + Data hygiene):** P0.9, P0.10, P1.10, P1.11, P1.12, P1.14, e auditoria cruzada pós-correção (valida que T4 e T5 não quebraram nada)

### §22.2 Zero Conflito Git
- T4 mexe apenas em `backend/modules/crm/`, `backend/alembic/versions/NOVAS_*`
- T5 mexe apenas em `frontend/src/app/modulos/crm/**`, `frontend/src/hooks/crm/**`, `frontend/src/components/crm/**`, `frontend/src/types/` (apenas arquivos CRM)
- T6 executa SQL de limpeza em PostgreSQL + usa `psycopg2` — zero edição de código

### §22.3 Sincronização
- Cada terminal tem seu próprio relatório: `/opt/conecta-pro/RELATORIO_CPRO11_T[4|5|6].md`
- Cada terminal atualiza este contrato INDEPENDENTEMENTE (cada um incrementa versão quando descobre algo, commits atômicos):
  - T4 descobre algo → v1.0 → v1.1 → commit
  - T5 descobre em paralelo → faz rebase com v1.1, incrementa → v1.2 → commit
  - T6 idem
- **Resolução de conflito:** se dois terminais tentarem incrementar ao mesmo tempo, o segundo faz `git pull --rebase` e renumera sua versão
- **Ponto de sincronização obrigatório:** T4 deve commitar a migration do enum `contractstatus` ANTES de T5 começar P0.6. Comunicação via contrato: T4 atualiza §23 "Status de Execução" quando completa P0.1.

### §22.4 Critério de Sucesso (por terminal)
- **Backend:** todos endpoints P0 retornam 200 com dados reais (sem erro silencioso), pytest passa, Pylint ≥ 99
- **Frontend:** CIC valida visualmente todas as 10 telas sem React Error, zero colunas vazias, zero "NaN"
- **Dados:** `SELECT COUNT(*) FROM clients WHERE cnpj='00000000000000'` = 1 (ou 0 se Conecta Mais não for cliente), zero mocks nos 14 leads, `lead_scores` com política definida

### §22.5 T7 Auditoria de Fechamento
Após T4+T5+T6 reportarem OK, disparar **T7** em terminal novo com INV-1: "ZERO alteração de código — T7 audita, não implementa". T7 valida:
1. Cada relatório vs código commitado
2. Todos os testes 🔴 executaram
3. CIC E2E em 10 telas do CRM sem erro
4. Este contrato está coerente (v final reflete estado real)
5. Veredito binário: **LIBERAR** ou **RETER**

---

## §23 Status de Execução (atualizado pelos terminais)

> Cada terminal escreve SEU status aqui e nenhum outro. T4 escreve em §23.1, T5 em §23.2, T6 em §23.3. Evita conflito de merge.

### §23.1 — Status T4 (Backend)
*(a ser preenchido pelo T4 ao concluir cada passo)*

- [ ] STEP 0 executado
- [ ] H1-H10 validadas
- [ ] P0.1 Migration `contractstatus` — status: ___
- [ ] P0.2 backend — schema `ClientResponse` com `endereco` estruturado — status: ___
- [ ] P0.5 backend — `/crm/dashboard/kpis` corrigido — status: ___
- [ ] P0.6 backend — cálculo MRR — status: ___
- [ ] P0.11 — `leads_conversion_rate` — status: ___
- [ ] Testes 🔴 executados: ___
- [ ] Commits: docs=<hash> code=<hash>

### §23.2 — Status T5 (Frontend)
*(a ser preenchido pelo T5 ao concluir cada passo)*

- [ ] STEP 0 executado
- [ ] H1-H10 validadas
- [ ] Aguardando T4 sincronizar P0.1 antes de P0.6? SIM / NÃO
- [ ] P0.2 frontend — componente endereco lida com objeto — status: ___
- [ ] P0.3 — colunas Nome mapeadas para `trade_name`/`legal_name` — status: ___
- [ ] P0.4 — status de leads mapeado corretamente — status: ___
- [ ] P0.7 — modal Oportunidade com enum backend — status: ___
- [ ] P0.8 — modal Oportunidade com FK (dropdowns) — status: ___
- [ ] CIC E2E pós-correção: ___/10 telas OK
- [ ] Commits: docs=<hash> code=<hash>

### §23.3 — Status T6 (Dados)

- [x] STEP 0 executado — CONTRATO v1.0 lido, §13.1 + §13.3 aplicados
- [x] H1-H8 validadas — backup (32KB) + queries executadas
- [x] P0.9 — Life Centro: lead preservado (tem opportunity), cliente NÃO criado — **PENDENTE dados manuais** (CNPJ desconhecido)
- [x] P0.10 — duplicata Conecta Mais resolvida — "Matriz escritório" + TEST-COND-001 + 29 kit_items + 4 kits removidos em cascata ✅
- [x] P1.10 — 2× PREFEITURA TESTE + PREFEITURA MANAUS removidos ✅
- [x] P1.11 — mock crm_activities "Teste auditoria" removido ✅
- [x] P1.12 — mock crm_contacts "Teste" removido ✅
- [x] P1.14 — `commission_rules` investigado (§13.1) — **CONCLUSÃO: tabela vazia intencional**, 22 colunas OK, produto novo. Idem `lead_scores` e `pricing_simulations`. NÃO tocar.
- [ ] Auditoria cruzada pós-T4-T5 — veredito: **AGUARDANDO §23.1 + §23.2**
- [x] Commits: docs=`<pendente commit>` data=`<pendente commit>`
- [x] Backup: `reconhecimento/cpro11/t6_backups/tables_backup_20260420_2014.sql` (32KB)
- [x] Script: `scripts/cpro11_t6_hygiene.sql` — 6 blocos, 8/8 testes ✅

---

## §24 Glossário do Domínio

| Termo | Definição no Conecta PRO |
|---|---|
| Lead | Contato inicial, ainda não cliente. Status: new, contacted, qualified, proposal, negotiation, converted, lost |
| Oportunidade | Negócio em andamento com valor estimado. Stage: qualification, needs_analysis, proposal, negotiation, closed_won, closed_lost |
| Proposta | Documento comercial formal, gerado a partir de oportunidade. Status: draft, sent, viewed, approved, accepted, rejected, expired, cancelled, revision_requested, under_revision (10 status) |
| Contrato | Acordo formal pós-proposta aceita. Types: RECURRING, ONE_TIME. Status afeta o enum `contractstatus` (P0.1) |
| Comissão | Valor devido ao vendedor por venda concluída |
| Pipeline | Soma ponderada: `expected_value × probability` por stage |
| RFM | Recency-Frequency-Monetary — segmentação em `CRM360Service` |
| Health Score | Indicador de saúde do cliente (visto em CIC Ver-360°, origem a investigar — §13.1) |
| MRR | Monthly Recurring Revenue — soma dos `value` dos contratos `RECURRING` ativos |
| MC % | Margem de Contribuição (%) — usada no Simulador de Precificação |
| CCT SINDECOMPRESTS 2026 | Convenção Coletiva que rege salário base + encargos (42%) + VR + VT |
| Cliente 360° | Tela que agrega MRR + Health + Contratos + Contatos + NFS-e + Timeline (fiscal cross-module) |

---

## §25 Bugs do CPRO 9 Aplicáveis ao CRM/Vendas

Dos 8 bugs documentados no PADRAO_PROMPTS, os seguintes são relevantes aqui:

- **Bug 3 (Supor paths)** — não supor, sempre consultar DB para caminhos
- **Bug 6 (HTTP 200 ≠ renderiza)** — validar em 4 camadas, não só status code
- **Bug 7 (Endpoint sem auth)** — todo endpoint novo com `Depends(get_current_user)` e comparar com vizinhos no mesmo controller

Os demais (Bug 1/2/4/5/8) valem mas têm aplicação indireta.

---

## §26 Próximas Versões Esperadas

- **v1.1** — após T4 commitar migration do enum `contractstatus`
- **v1.2** — após T5 commitar correção de mismatches de schema
- **v1.3** ✅ — T6 limpeza de mocks + higiene FKs concluída (2026-04-20)
- **v1.4** — pós-T7 auditoria LIBERA
- **v2.0** — início de sprint Marketing/Licitações (novo ciclo)

---

### §20.6 — Conclusões Chesterton T6 (§13.1 aplicado em 2026-04-20)

| Tabela | Rows | Conclusão |
|---|---|---|
| `commission_rules` | 0 | Schema completo (22 cols). Produto novo — dados nunca cadastrados. **NÃO é bug.** |
| `lead_scores` | 0 | ML de scoring existe mas nunca executou (nenhum lead qualificado passou pelo pipeline). **NÃO é bug.** |
| `pricing_simulations` | 0 | Controllers existem (12K bytes). Aguarda criação de propostas. **NÃO é bug.** |
| `modules/comercial/` stubs | — | Código stub. Aguarda implementação futura. **NÃO deletar** — preservar cerca. |

---

**FIM DO CONTRATO v1.3**

> "Não se acomode. Sempre eleve. Quando errar, admita rápido. Quando descobrir
> algo novo, documente ANTES de corrigir. Escopo é sagrado. Chesterton não
> se desrespeita." — Opus 4.7 CPRO 9
