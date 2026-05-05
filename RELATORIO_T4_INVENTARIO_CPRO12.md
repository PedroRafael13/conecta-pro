# T4 CPRO12 — Inventário Módulos Containers
**Data:** 2026-05-05
**Executor:** Claude Sonnet 4.6 [session: t4] [module: operacional]
**Tipo:** READ-ONLY — diagnóstico de sincronização

---

## Total de módulos HOST: 48

```
ai, analytics, audit, automation, bidding, campo, cct, client_portal, clients,
comercial, config, crm, document_kits, documents, empresas, equipment_management,
fase5, financeiro, financial, fiscal, fiscal_contabil, gdrive, ged, gedeon,
gestao, government_integrations, health_occupational, hr, integrations,
inteligencia, juridico, lgpd, mobile, monitoring, notifications, operacional,
operacoes, people_management, pessoas, recruitment, reimbursement, reports,
retention, scheduler, search, security_lgpd, services, tecnico
```

---

## Módulos com tasks Celery (no include celery_app.py)

| Módulo | Arquivos de tasks | Include celery_app.py |
|--------|------------------|-----------------------|
| bidding | 3 (notification, dispute, sync) | `modules.bidding.tasks` |
| financial | 1 (tasks.py) | `modules.financial.tasks` |
| gedeon | 1 (kronos_tasks.py) | `modules.gedeon.tasks.kronos_tasks` |
| government_integrations | 2 (monitoring, sync) | `modules.government_integrations.jobs.*` |
| health_occupational | 1 (sst_alerts_tasks.py) | `modules.health_occupational.tasks` |
| integrations | 1 (solides/tasks.py) | `modules.integrations.connectors.solides.tasks` |
| operacional | 1 (tasks.py) | `modules.operacional.tasks` |
| people_management | 1 (afastamento_tasks.py) | `modules.people_management.sst.tasks` |

---

## Containers verificados (8 total)

| Container | Status | Módulos |
|-----------|--------|---------|
| conecta-pro-backend | Up 7h (healthy) | 49 (+1 extra: `modules`) |
| conecta-pro-celery-beat | Up 33min (unhealthy) | 47 |
| conecta-pro-celery-batch | Up 32min (healthy) | 47 |
| 297439d0453a_conecta-pro-celery-operacional | Up 2 weeks (healthy) | 46 |
| conecta-pro-celery-integrations | Up 2 weeks (healthy) | 44 |
| 34bbe0bcda76_conecta-pro-celery-priority | Up 2 weeks (healthy) | 46 |
| 8f30da3e29ad_conecta-pro-celery-nfse | Up 2 weeks (healthy) | 46 |
| a853a3056bf9_conecta-pro-celery-sefaz | Up 2 weeks (healthy) | 46 |

---

## Tabela Matricial: módulo × container

| Módulo | backend | beat | batch | operacional | integrations | priority | nfse | sefaz |
|--------|---------|------|-------|-------------|--------------|----------|------|-------|
| ai | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| analytics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| audit | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| automation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| bidding | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| campo | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| cct | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| client_portal | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| clients | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| comercial | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| config | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| crm | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| document_kits | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| documents | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| empresas | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| equipment_management | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| fase5 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| financeiro | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| financial | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| fiscal | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| fiscal_contabil | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **gdrive** | ✅ | **❌** | **❌** | **❌** | **❌** | **❌** | **❌** | **❌** |
| ged | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **gedeon** | ✅ | ✅ | ✅ | **❌** | **❌** | **❌** | **❌** | **❌** |
| gestao | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| government_integrations | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| health_occupational | ✅ | ✅ | ✅ | **❌** | ✅ | **❌** | **❌** | **❌** |
| hr | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| integrations | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| inteligencia | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **juridico** | ✅ | **❌** | **❌** | **❌** | **❌** | **❌** | **❌** | **❌** |
| lgpd | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| mobile | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| monitoring | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| notifications | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| operacional | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| operacoes | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| people_management | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| pessoas | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| recruitment | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| reimbursement | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| reports | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| retention | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| scheduler | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **search** | ✅ | **❌** | **❌** | **❌** | **❌** | **❌** | **❌** | **❌** |
| security_lgpd | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| services | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| tecnico | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Extras nos containers (não no HOST):**
- `cadastros` — presente em beat, batch, operacional, priority, nfse, sefaz (legado do build original)
- `core` — presente em beat, batch, operacional, priority, nfse, sefaz (legado do build original)
- `modules` — presente apenas em backend (leftover de docker cp)

---

## Módulos CRÍTICOS ausentes (com tasks no include celery_app.py)

| Módulo | Task ausente | Containers afetados | Impacto |
|--------|-------------|--------------------|---------|
| **gedeon** | `kronos_tasks.py` | operacional, integrations, priority, nfse, sefaz | KRONOS/THEMIS nunca executa nos 5 workers |
| **financial** | `tasks.py` | operacional, integrations, priority, nfse, sefaz | Tasks financeiras não carregadas nos 5 workers |
| **health_occupational** | `sst_alerts_tasks.py` | operacional, priority, nfse, sefaz | Verificações SST não carregadas em 4 workers |

---

## celery_app.py: TODOS os containers desatualizados

| Container | Diferença vs HOST |
|-----------|------------------|
| beat, batch | Agendamento D4: dia `1 às 02:00` → HOST tem `dia 21 às 07:00` |
| operacional, priority, nfse, sefaz | Faltam includes: gedeon, financial, health_occupational; faltam rotas SST |
| integrations | Faltam includes: gedeon, financial; faltam rotas GEDEON |

Consequência: mesmo com os módulos copiados, as tasks não serão descobertas pelos
workers que têm celery_app.py antigo sem os `include` corretos.

---

## Profundidade de tasks (STEP 4)

| Módulo | beat | batch | operacional | integrations | priority | nfse | sefaz |
|--------|------|-------|-------------|--------------|----------|------|-------|
| bidding | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| financial | ✅ 1/1 | ✅ 1/1 | ⚠️ 0/1 | ⚠️ 0/1 | ⚠️ 0/1 | ⚠️ 0/1 | ⚠️ 0/1 |
| gedeon | ✅ 1/1 | ✅ 1/1 | ⚠️ 0/1 | ⚠️ 0/1 | ⚠️ 0/1 | ⚠️ 0/1 | ⚠️ 0/1 |
| government_integrations | ✅ 2/2 | ✅ 2/2 | ✅ 2/2 | ✅ 2/2 | ✅ 2/2 | ✅ 2/2 | ✅ 2/2 |
| health_occupational | ⚠️ 2/1* | ✅ 1/1 | ⚠️ 0/1 | ✅ 1/1 | ⚠️ 0/1 | ⚠️ 0/1 | ⚠️ 0/1 |
| integrations | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 |
| operacional | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 |
| people_management | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 | ✅ 1/1 |

*beat tem 2 arquivos para health_occupational por causa de diretório duplicado aninhado.

---

## Módulos adicionados pós 2026-03-01 (mais provavelmente ausentes)

Módulos que tiveram `__init__.py` adicionado ou surgimento significativo pós março/2026:
- `gedeon` (múltiplos commits: 2026-03 em diante — onvio, fiscal, kronos)
- `gdrive` (feat: envio automático por e-mail — 2026-04)
- `juridico` (feat: skills controller — 2026-03)
- `financial/tasks.py` (feat: auto-sync cashflow — commit recente)
- `health_occupational/tasks/` (feat: SST integrações — 2026-03)

---

## Total .py files (apenas modules/)

| Localização | Arquivos .py |
|-------------|-------------|
| HOST (backend/modules/) | 2.278 |
| celery-beat (/app/modules/) | 2.287 |
| celery-batch (/app/modules/) | 2.251 |
| celery-operacional (/app/modules/) | 2.209 |
| celery-integrations (/app/modules/) | 2.247 |

beat tem ~9 arquivos extras (cadastros + core extras + nested health_occupational).
Diferença operacional vs HOST: ~69 arquivos.

---

## Lista priorizada de syncs

### CRÍTICO (tasks não carregadas — afeta execução de cronjobs)

1. **celery_app.py → TODOS os 7 workers**
   - Desbloqueia includes gedeon/financial/health_occupational e rotas SST/GEDEON
   - Sem isso, copiar os módulos não resolve: tasks não são descobertas

2. **gedeon/ → operacional, integrations, priority, nfse, sefaz**
   - 5 containers sem o módulo
   - KRONOS/THEMIS completamente inativo nesses workers

3. **financial/tasks.py → operacional, integrations, priority, nfse, sefaz**
   - Arquivo único — trivial de copiar
   - tasks financeiras (auto-sync cashflow) não carregadas

### ALTO (módulo presente mas subdiretório tasks ausente)

4. **health_occupational/ → operacional, priority, nfse, sefaz**
   - SST alerts (ASO, EPI, exames) não verificados em 4 workers

### MÉDIO (módulos sem tasks, impacto indireto)

5. **gdrive/ → todos os 7 workers**
   - Envio automático de kits por e-mail não disponível nos workers
6. **juridico/ → todos os 7 workers**
7. **search/ → todos os 7 workers**

### BAIXO (anomalias/limpeza)

8. **Remover diretório duplicado aninhado** em celery-beat:
   `/app/modules/health_occupational/health_occupational/` (leftover de docker cp mal feito)

---

## Hipóteses

| H | Validada? | Detalhe |
|---|-----------|---------|
| H1 — mais módulos ausentes além de gedeon/health_occupational | ✅ SIM | gdrive, juridico, search ausentes em TODOS os workers; financial/tasks ausente em 5 |
| H2 — integrations/priority mais atualizados que beat/batch | ❌ NÃO | beat e batch têm gedeon presente; integrations/priority não têm gedeon |
| H3 — módulos com tasks todos presentes | ❌ NÃO | gedeon (5 workers), financial (5), health_occupational (4) ausentes |
| H4 — backend completo vs HOST | ✅ SIM | backend tem todos os 48 módulos + 1 extra (`modules`) |
| H5 — subdiretórios desatualizados | ✅ SIM | health_occupational beat tem dir aninhado; financial/tasks.py ausente em 5 |
| H6 — celery_app.py idêntico | ❌ NÃO | TODOS os 7 workers têm versão desatualizada |
| H7 — total .py HOST vs containers | ✅ | HOST 2278, beat 2287, batch 2251, operacional 2209, integrations 2247 |
| H8 — módulos pós março/2026 mais provavelmente ausentes | ✅ SIM | gedeon, gdrive, juridico, financial/tasks, health_occupational/tasks — todos pós março |

---

## Achado crítico transversal

**O problema raiz é o celery_app.py desatualizado, não apenas módulos faltando.**

Mesmo que todos os módulos fossem copiados para todos os containers, os workers
de operacional/priority/nfse/sefaz ainda não executariam as tasks de gedeon,
financial e health_occupational porque seus celery_app.py não têm os `include`
correspondentes. O sync de celery_app.py é pré-requisito para os demais syncs.

---

## Commits

| Commit | Tipo | Hash |
|--------|------|------|
| docs: §66 no CONTRACTS_GEDEON.md | docs | `55b2bf6a` |
| docs: RELATORIO_T4_INVENTARIO_CPRO12.md | docs | (próximo) |

---

## Self-check (12 itens)

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §65 confirmado, §13.1 + INV-3 citados | ✅ |
| STEP 1 — inventário HOST: 48 módulos + tasks identificadas | ✅ |
| STEP 2 — todos os 8 containers verificados (não apenas 6) | ✅ |
| STEP 3 — tabela matricial módulo × container gerada | ✅ |
| STEP 4 — profundidade tasks verificada em todos os workers | ✅ |
| STEP 5 — celery_app.py diff executado em todos os workers | ✅ |
| STEP 6 — módulos pós março/2026 identificados | ✅ |
| STEP 7 — lista priorizada CRÍTICO/ALTO/MÉDIO/BAIXO gerada | ✅ |
| STEP 8 — §66 no CONTRACTS_GEDEON + commit de docs | ✅ |
| STEP 9 — relatório gerado em /opt/conecta-pro/ | ✅ |
| INV-3 — ZERO alterações em containers ou código | ✅ |
| INV-10 — resultado em formato tabela legível | ✅ |

---

**T4 CPRO12 INVENTÁRIO OK — 4 módulos ausentes identificados (gdrive, gedeon, juridico, search ausentes em todos os workers; financial/tasks e health_occupational/tasks em 5/4 workers). celery_app.py desatualizado em TODOS os 7 workers é o bloqueador raiz. Syncs críticos necessários: celery_app.py primeiro, depois gedeon + financial/tasks + health_occupational.**

[session: t4] [module: operacional]
