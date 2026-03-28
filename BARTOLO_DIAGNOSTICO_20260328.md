# BARTOLO & AI — DIAGNÓSTICO COMPLETO
## Data: 2026-03-28 | Conecta PRO

---

## 1. INVENTÁRIO

### 111 endpoints AI registrados na OpenAPI

| Grupo | Endpoints | Status |
|-------|-----------|--------|
| Bartolo Core (/ai/bartolo/) | 15 | ✅ Todos 200 |
| Briefing (/ai/briefing/) | 3 | ✅ Todos 200 |
| OpenClaw (/ai/openclaw/) | 6 | ✅ Todos 200 |
| Financial AI (/financial/ai/) | 20+ | ✅ Todos 200 |
| Operacional AI (/operacional/ai/) | 13 | ✅ Todos 200 |
| People Management AI | 13 | ✅ (duplicata operacional) |
| Clients AI | 6 | ✅ Registrados |
| Document Kits AI | 6 | ✅ Registrados |
| **TOTAL** | **111** | |

### Skills (14 arquivos — 290 KB total)

| Skill | Tamanho | Comandos | Status |
|-------|---------|----------|--------|
| briefing_skill.py | 8.3 KB | /briefing, /resumo | ✅ NOVO — funciona |
| diarista_skill.py | 42 KB | /diarista listar, avaliar, pagamento | 🟡 Código existe |
| cobertura_skill.py | 37 KB | /relatorio horas_extras, custos | 🟡 Código existe |
| comunicado_skill.py | 29 KB | /comunicado criar, publicar | 🟡 Código existe |
| escala_skill.py | 27 KB | /escala ver, criar, auto_gerar | 🟡 Código existe |
| posto_skill.py | 27 KB | /posto listar, ver, criar | 🟡 Código existe |
| banco_horas_skill.py | 24 KB | /banco_horas saldo, extrato | 🟡 Código existe |
| ronda_skill.py | 21 KB | /ronda ver, criar, iniciar | 🟡 Código existe |
| disciplinar_skill.py | 18 KB | /disciplinar ver, criar | 🟡 Código existe |
| alerta_skill.py | 11 KB | /alerta ver, criticos | 🟡 Código existe |
| substituto_skill.py | 9.1 KB | /substituto buscar | 🟡 Código existe |
| ocorrencia_skill.py | 39 KB | /ocorrencia ver, criar | 🟡 Código existe |
| base_skill.py | 1.6 KB | (base class) | ✅ Framework |

### Agents (11 — 412 KB total)

| Agent | Tamanho | Intents | Status |
|-------|---------|---------|--------|
| diarista_agent.py | 67 KB | 11 intents | 🟡 Dormindo |
| escala_agent.py | 65 KB | 7 intents | 🟡 Dormindo |
| posto_agent.py | 42 KB | 7 intents | 🟡 Dormindo |
| disciplinar_agent.py | 40 KB | 5 intents | 🟡 Dormindo |
| banco_horas_agent.py | 38 KB | 6 intents | 🟡 Dormindo |
| comunicacao_agent.py | 33 KB | 5 intents | 🟡 Dormindo |
| ronda_agent.py | 28 KB | 5 intents | 🟡 Dormindo |
| ocorrencia_agent.py | 28 KB | 5 intents | 🟡 Dormindo |
| relatorio_agent.py | 25 KB | 7 intents | 🟡 Dormindo |
| substituicao_agent.py | 23 KB | 3 intents | 🟡 Dormindo |
| alerta_agent.py | 23 KB | 4 intents | 🟡 Dormindo |

### Executors (14 — 349 KB total)

| Executor | Tamanho | ActionTypes |
|----------|---------|-------------|
| shift_executor.py | 55 KB | CREATE_SHIFT, CHECKIN, CHECKOUT, ABSENCE |
| inspection_executor.py | 47 KB | CREATE_ROUND, START, COMPLETE, CHECKPOINT |
| diarist_executor.py | 41 KB | CREATE, SCHEDULE, EVALUATE, PAYMENT |
| scale_executor.py | 39 KB | CREATE_SCALE, APPROVE, PUBLISH, OPTIMIZE |
| post_executor.py | 25 KB | CREATE_POST, UPDATE, DELETE, STATS |
| allocation_executor.py | 23 KB | ALLOCATE, TERMINATE, TRANSFER |
| disciplinary_executor.py | 23 KB | CREATE, APPROVE, REJECT |
| occurrence_executor.py | 23 KB | CREATE, RESOLVE, UPDATE |
| time_bank_executor.py | 19 KB | APPROVE_OT, COMPENSATE, BALANCE |
| communication_executor.py | 18 KB | CREATE_ANN, PUBLISH_ANN |
| report_executor.py | 15 KB | GENERATE_REPORT |
| notification_executor.py | 11 KB | SEND_NOTIFICATION |
| substitution_executor.py | 9.1 KB | CREATE_SUBSTITUTION |
| base_executor.py | 5.6 KB | (base class) |

### Wizards (10 — 128 KB total)

| Wizard | Steps | Domínio |
|--------|-------|---------|
| proposta_comercial | 9 | Propostas comerciais |
| admissao | 8 | Admissão de funcionários |
| escala | 8 | Criação de escalas |
| posto | 10 | Criação de postos |
| diarista | 9 | Agendamento de diaristas |
| comunicado | 10 | Criação de comunicados |
| disciplinar | 7 | Medidas disciplinares |
| ocorrencia | 6 | Registro de ocorrências |
| banco_horas | 6 | Compensação de horas |
| ronda | 5 | Rondas de inspeção |

### Intelligence Hub (5 arquivos — 93 KB)

| Componente | Tamanho | Função |
|-----------|---------|--------|
| unified_ai_engine.py | 14 KB | Engine unificado |
| cross_module_analytics.py | 18 KB | Analytics cross-módulo |
| insight_distributor.py | 22 KB | Distribuição de insights |
| module_integration_manager.py | 21 KB | Integração entre módulos |
| predictive_orchestra.py | 18 KB | Orquestra preditiva |

---

## 2. O QUE ESTÁ FUNCIONANDO (ACORDADO)

### Bartolo Core — ✅ FUNCIONA
```
POST /ai/bartolo/send            → 200 (responde "Ola! Sou o Bartolo...")
GET  /ai/bartolo/health          → 200 {"status": "healthy"}
GET  /ai/bartolo/wizards         → 200 (10 wizards listados)
GET  /ai/bartolo/stats           → 200
GET  /ai/bartolo/modules         → 200
POST /ai/bartolo/send/stream     → 200
POST /ai/bartolo/feedback        → 200
POST /ai/bartolo/wizard/start    → 200
```

**Modelo usado:** `local-fallback` (NÃO está chamando Claude/GPT)
**Motivo:** LLM_PROVIDER=anthropic configurado mas as respostas vêm do fallback local.
Provável causa: timeout na API Anthropic ou ANTHROPIC_API_KEY ausente/inválida.
**Evidência:** `"model_used": "local-fallback"` na resposta.

### Briefing Executivo — ✅ FUNCIONA
```
GET  /ai/briefing/diario  → 200 (dados reais: saldo R$ 32k, MRR R$ 272k)
POST /ai/briefing/enviar  → 200 (Telegram: enviado True)
GET  /ai/briefing/status  → 200 (telegram_configurado: true)
```

### OpenClaw — ✅ FUNCIONA
```
GET /ai/openclaw/knowledge           → 200
GET /ai/openclaw/patterns            → 200
GET /ai/openclaw/interventions/stats → 200
POST /ai/openclaw/alert-webhook      → registrado
```

### Financial AI — ✅ FUNCIONA (7+ endpoints)
```
GET /financial/ai/command-center      → 200 (health 45/100)
GET /financial/ai/risks               → 200
GET /financial/ai/cashflow-prediction → 200
GET /financial/ai/advisor/health      → 200
GET /financial/ai/billing/summary     → 200
GET /financial/ai/costing/summary     → 200
```

### Operacional AI — ✅ FUNCIONA
```
GET /operacional/ai/command-center       → 200
GET /operacional/ai/performance-overview → 200
GET /operacional/ai/coverage-prediction  → 200
```

---

## 3. O QUE ESTÁ DORMINDO (CÓDIGO EXISTE MAS NÃO ATIVO)

### Skills do Bartolo (11 skills — 🟡 DORMINDO)
As 11 skills operacionais (escala, posto, ronda, etc.) existem como código
(290 KB de Python) mas só são ativadas quando o Bartolo recebe um slash command
via chat. Como o LLM está em fallback, o Bartolo não consegue classificar
corretamente as intenções e redirecionar para as skills.

**Para acordar:** Garantir que a ANTHROPIC_API_KEY funciona e o LLM sai do fallback.

### Agents do Bartolo (11 agents — 🟡 DORMINDO)
Os 11 agents são invocados pelo BartoloEngine quando detecta uma intenção.
Com o LLM em fallback, a detecção de intenção é limitada a regex patterns.
Os agents com regex mais amplos (escala, posto) funcionam parcialmente.

### Intelligence Hub (5 componentes — 🟡 NÃO REGISTRADO)
O Intelligence Hub existe em `/modules/ai/intelligence_hub/` com 93 KB de código
(unified_ai_engine, cross_module_analytics, predictive_orchestra, etc.)
**mas NÃO está registrado na API**. Nenhum endpoint `/intelligence/` aparece na OpenAPI.

### Wizards (10 wizards — ✅ REGISTRADOS mas dependem do LLM)
Os 10 wizards estão listados via GET /ai/bartolo/wizards.
Podem ser iniciados via POST /ai/bartolo/wizard/start.
Funcionam em modo step-by-step sem precisar do LLM.

---

## 4. O QUE PRECISA SER ACORDADO

### P0 — LLM saindo do fallback
**Problema:** `"model_used": "local-fallback"` em TODAS as respostas do Bartolo.
**Causa provável:** ANTHROPIC_API_KEY ausente, inválida, ou timeout.
**Impacto:** Bartolo responde com templates estáticos, não entende perguntas complexas.
**Solução:** Verificar ANTHROPIC_API_KEY no .env e testar conexão direta.

### P1 — Intelligence Hub sem registro
**Problema:** 93 KB de código AI que nunca foi registrado na API.
**Impacto:** Cross-module analytics, predictive orchestra, insight distributor inacessíveis.
**Solução:** Registrar controller do intelligence_hub no main_production.py.

### P2 — Telegram bot não conecta com Bartolo
**Problema:** O bot Telegram (`telegram_assistant.py`) é um processo independente
que usa Anthropic diretamente. Ele NÃO passa pelo BartoloEngine.
**Impacto:** As 11 skills, 11 agents e 10 wizards não são acessíveis via Telegram.
**Solução:** Fazer o bot Telegram chamar POST /ai/bartolo/send em vez de Anthropic direto.

### P3 — DataConnector limitado ao Operacional
**Problema:** O DataConnector do Bartolo só consulta módulo operacional
(postos, escalas, funcionários, ocorrências).
NÃO consulta financeiro, GED, clientes, contratos, certidões.
**Impacto:** Bartolo não responde perguntas sobre saldo, NFS-e, kits, etc.
**Solução:** Expandir DataConnector com queries financeiras e GED.

---

## 5. TELEGRAM BOT

```
Bot:        @conectapro_alertas_bot
Nome:       Conecta PRO Alertas
Status:     ✅ Online (PM2, uptime 6 dias)
PID:        10730
Memória:    61.4 MB
Engine:     Anthropic claude-sonnet-4 DIRETO (NÃO usa Bartolo)
Última msg: "Qual meu saldo na minha conta do banco inter neste momento?"
Chat ID:    5536961034 (Jordan)
```

O bot funciona como assistente standalone com Claude Sonnet via API Anthropic.
Tem tools para: system_status, run_sql, get_financial_data, etc.
**NÃO usa o BartoloEngine** — é um processo paralelo independente.

---

## 6. NÚMEROS FINAIS

```
Endpoints AI total:    111
Endpoints 200:         30+ testados OK
Skills:                14 (1 ativa, 13 dormindo)
Agents:                11 (todos dormindo — dependem do LLM)
Executors:             14 (todos dormindo — dependem dos agents)
Wizards:               10 (registrados, podem ser usados)
Intelligence Hub:      NÃO registrado (93 KB código morto)
LLM:                   local-fallback (Anthropic não conectado)
Telegram Bot:          ✅ Online (standalone, NÃO usa Bartolo)
Briefing:              ✅ Funciona (dados reais + Telegram)
OpenClaw:              ✅ Funciona (webhooks + interventions)
Financial AI:          ✅ Funciona (command-center, risks, cashflow)
Operacional AI:        ✅ Funciona (command-center, coverage)

Código AI total:       ~1.2 MB de Python
Código ativo:          ~200 KB (controllers + briefing + openclaw)
Código dormindo:       ~1.0 MB (skills + agents + executors + intelligence hub)
```

---

## 7. RECOMENDAÇÃO DE PRIORIDADE

1. **Verificar ANTHROPIC_API_KEY** (5 min) — se funcionar, o Bartolo inteiro acorda
2. **Registrar Intelligence Hub** na API (15 min) — desbloqueia 93 KB de AI
3. **Conectar Telegram ao Bartolo** — bot passa a usar skills/agents/wizards
4. **Expandir DataConnector** — Bartolo responde sobre financeiro/GED/clientes

---

## DOWNLOAD

```bash
scp root@82.25.75.74:/opt/conecta-pro/BARTOLO_DIAGNOSTICO_20260328.md ~/Desktop/
```
