# RELATORIO INTEGRACAO SOLIDES/TANGERINO — CONECTA PRO
## Sessao 2026-03-23

> **Empresa:** Jordan Santos de Jesus LTDA (CNPJ: 35.710.481/0001-03)
> **Sistema:** Conecta PRO v2.0.0 | **API:** Solides Tangerino
> **Data:** 23 de Marco de 2026
> **Autor:** Claude Opus 4.6

---

## 1. DIAGNOSTICO DA INTEGRACAO

### O que ja existia ANTES desta sessao
A integracao Solides/Tangerino ja estava implementada com **15 tabelas de staging**
e **11 arquivos Python**:

```
backend/modules/integrations/connectors/solides/
├── __init__.py
├── connector.py          → Cliente HTTP para API Tangerino
├── sync_service.py       → Servico de sync bidirecional
├── mappers.py            → Mapeamento Solides ↔ Conecta PRO
├── models.py             → Models SQLAlchemy (15 tabelas solides_*)
├── schemas.py            → Pydantic schemas
├── tasks.py              → Celery tasks (full_sync, incremental, webhook)
├── conflict_resolver.py  → Resolucao de conflitos bidirecional
├── webhook_handler.py    → Handler de webhooks do Solides
└── integration_service.py → Servico de integracao
```

### Credenciais
- **API Token:** Configurado (`SOLIDES_API_TOKEN` no container)
- **Webhook Secret:** Configurado (`SOLIDES_WEBHOOK_SECRET`)
- **Endpoint real:** `https://employer.tangerino.com.br`
- **Autenticacao:** Basic Auth (token base64)

### Estado ANTES do sync
| Metrica | Valor |
|---------|-------|
| Funcionarios no banco | 52 |
| Funcionarios no Solides | 44 |
| Divergencia | 8 cadastros locais (sem Solides) |
| Ultimo sync | **NUNCA** (`last_full_sync_at: null`) |
| data_nascimento preenchidos | **0/52** |
| sexo preenchidos | **0/52** |
| PIS preenchidos | 37/52 |

---

## 2. SYNC EXECUTADO — RESULTADOS

### Full Sync via API Tangerino
```
Endpoint: https://employer.tangerino.com.br/employee/find-all
Metodo: GET com paginacao (?size=100&page=0)
Auth: Basic [SOLIDES_API_TOKEN]
Tempo: 3.6 segundos
```

**Entidades sincronizadas:**
| Entidade | Registros | Endpoint API |
|----------|-----------|-------------|
| employees | 44 | /employee/find-all |
| job_roles | 5 | /job-role/find-all |
| workplaces | 4 | /workplace/find-all |
| work_schedules | 29 | /work-schedule |
| **Total** | **82** | |

### Propagacao para tabela `employees`
| Campo | Antes | Depois | Fonte |
|-------|-------|--------|-------|
| data_nascimento | 0 | **42** | API `birthDate` (ms timestamp) |
| sexo | 0 | **27** | API `gender` (MASCULINO/FEMININO) |
| PIS | 37 | **43** | API `pis` |
| data_admissao | 52 | 52 | Ja existia |
| cargo | 52 | 52 | **Mantido** (nao tocado) |
| salario_base | 52 | 52 | **Mantido** (nao tocado) |
| solides_id | 44 | 52 | API `id` |

### 10 Funcionarios sem data_nascimento
A API Tangerino retorna `birthDate: null` para estes funcionarios.
**Precisam ser corrigidos no cadastro do Solides:**

| Funcionario | CPF | Tem Sexo | Tem PIS |
|------------|-----|----------|---------|
| ANDREW COSTA VASCONCELOS | 701...254 | Nao | Sim |
| CARLOS ALBERTO ASSIS DE LIMA | 456...291 | Nao | Sim |
| GELSON BERNARDO LIMA | 641...272 | Nao | Sim |
| JEFFERSON DA SILVA BATISTA | 026...296 | Nao | Sim |
| JORDANA BACRY PIRES | 034...282 | Nao | Sim |
| JOSIANE DE SOUSA SILVA | 006...212 | Nao | Nao |
| JULIO CESAR ASSIS SANTOS | 014...261 | Nao | Nao |
| ORLAILSON PAIVA PEREIRA | 027...214 | Nao | Sim |
| ROBERTO PEREIRA MENEZES | 862...272 | Nao | Sim |
| WANDERSON MATOS DIAS | 013...260 | Nao | Sim |

### 8 Funcionarios sem Solides (cadastro local)
Estes 8 estao no Conecta PRO mas NAO estao no Solides:

**Acao necessaria:** Verificar se sao ativos reais ou cadastros de teste.
Se ativos: cadastrar no Solides. Se teste: inativar no Conecta PRO.

---

## 3. ESTADO ATUAL DA SINCRONIZACAO 24/7

### A integracao esta em tempo real? NAO — AINDA NAO.

**O que FUNCIONA hoje:**

| Componente | Status | Frequencia |
|-----------|--------|-----------|
| Full sync manual | ✅ Funciona | Sob demanda (POST /sync/full) |
| Incremental sync manual | ✅ Funciona | Sob demanda (POST /sync/incremental) |
| Celery task full_sync | ✅ Registrada | Queue: integrations |
| Celery worker integrations | ✅ Rodando | 24/7 |
| Endpoint /solides/status | ✅ 200 | Real-time |
| Endpoint /solides/employees | ✅ 200 | Paginado |
| Endpoint /solides/health | ✅ 200 | Health check |
| Webhook handler | ✅ Codigo existe | Endpoint POST /webhook |

**O que FALTA para ser 24/7 full duplex:**

| Componente | Status | Acao Necessaria |
|-----------|--------|-----------------|
| Celery Beat schedule | ⚠️ Parcial | Adicionar sync a cada 15min |
| Webhook ativo no Solides | ❌ Desabilitado | Configurar URL no painel Solides |
| Propagacao staging → employees | ⚠️ Manual | Automatizar no sync_service |
| Inativacao automatica | ❌ Nao implementado | Marcar inativos quando Solides remove |
| Sync de ponto/batidas | ❌ Nao implementado | API Tangerino tem endpoint de ponto |
| Sync de ausencias/faltas | ❌ Nao implementado | Endpoint /absence no Tangerino |

### Celery Beat — Tarefas Solides EXISTENTES
```python
# Ja registradas no celery_app.py:
"solides-incremental-sync-all": {
    "task": "solides.sync_all_condominios_incremental",
    "schedule": 900.0,  # 15 minutos
    "options": {"queue": "integrations"},
},
"solides-health-check-all": {
    "task": "solides.health_check_all",
    "schedule": 300.0,  # 5 minutos
    "options": {"queue": "integrations"},
},
"solides-process-webhooks": {
    "task": "solides.process_webhook_queue",
    "schedule": 30.0,  # 30 segundos
    "options": {"queue": "webhooks"},
},
```

O **incremental sync roda a cada 15 minutos** e o **health check a cada 5 minutos**.
Porem, o sync atualiza as tabelas `solides_*` (staging) mas **NAO propaga
automaticamente para `employees`**.

---

## 4. PLANO PARA 24/7 FULL DUPLEX

### PRIORIDADE 1 — Propagacao automatica (2-4h)
O sync ja roda a cada 15min mas salva em `solides_employees`.
Precisa de um step que compara `solides_employees` com `employees`
e propaga diferencas.

**Implementar:**
```python
# No sync_service.py, apos _sync_from_solides():
async def _propagate_to_employees(self):
    """Propaga dados do staging solides_employees para employees."""
    # Para cada solides_employee com mapping:
    #   Se employee.data_nascimento is None e solides tem: atualizar
    #   Se employee.sexo is None e solides tem: atualizar
    #   Se employee.pis is None e solides tem: atualizar
    #   Se solides.situacao == 'demitido': marcar employee como inativo
```

### PRIORIDADE 2 — Webhook do Solides (1h)
O webhook handler ja existe no codigo. Falta:
1. Configurar URL no painel Solides: `https://erp.conectamais.pro/api/v1/integrations/solides/webhook`
2. Ativar no Solides os eventos: admissao, rescisao, alteracao_cadastral, ponto
3. Testar com `curl -X POST` simulando um evento

### PRIORIDADE 3 — Sync de ponto (4-8h)
A API Tangerino tem endpoints de ponto:
```
GET /clock-in/find-by-employee?employeeId={id}&startDate={}&endDate={}
GET /clock-in/find-all?startDate={}&endDate={}
```
Implementar task que busca batidas das ultimas 2h a cada 5min.

### PRIORIDADE 4 — Sync de ausencias (2-4h)
```
GET /absence/find-by-employee?employeeId={id}
GET /absence/find-all
```

---

## 5. FOLHA DE PAGAMENTO — INALTERADA

A folha NAO mudou com o sync porque cargos e salarios foram mantidos:

```
Colaboradores:  52
Proventos:      R$ 118.658,60
Descontos:      R$  13.829,51
Liquido:        R$ 104.829,09
FGTS:           R$   7.935,00
INSS:           R$   7.742,98

Por cargo:
  34 Agentes de Portaria     → R$ 69.811,38 liq
  12 Agentes Serv. Gerais    → R$ 22.919,64 liq
   3 Lideres de Portaria     → R$  6.181,08 liq
   3 Artifices               → R$  5.916,99 liq
```

---

## 6. IMPACTO NO eSocial (S-2200)

Para transmitir o evento S-2200 (Cadastramento Inicial) precisa:

| Campo | Preenchidos | Meta | Gap |
|-------|------------|------|-----|
| CPF | 52/52 (100%) | 52 | 0 |
| data_nascimento | 42/52 (81%) | 52 | **10** |
| sexo | 27/52 (52%) | 52 | **25** |
| PIS | 43/52 (83%) | 52 | **9** |
| data_admissao | 52/52 (100%) | 52 | 0 |
| estado_civil | 0/52 (0%) | 52 | **52** |

**Acao:** Corrigir no Solides os cadastros incompletos.
O Tangerino nao retorna `estado_civil` nem `maritalStatus` — pode ser
que esse campo precise vir de outro endpoint ou ser preenchido manualmente.

---

## 7. COMANDOS UTEIS

```bash
# Token de acesso
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Status da integracao
curl -sf "http://127.0.0.1:8080/api/v1/integrations/solides/status" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Disparar full sync
curl -X POST "http://127.0.0.1:8080/api/v1/integrations/solides/sync/full" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'

# Disparar incremental sync
curl -X POST "http://127.0.0.1:8080/api/v1/integrations/solides/sync/incremental" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}'

# Ver funcionarios do Solides
curl -sf "http://127.0.0.1:8080/api/v1/integrations/solides/employees" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Propagar dados Tangerino para employees (script manual)
docker exec conecta-pro-backend python3 scripts/sync_solides_to_employees.py

# Ver campos faltantes
docker exec conecta-pro-postgres psql -U postgres -d conecta_pro -c "
SELECT nome, data_nascimento IS NOT NULL as nasc, sexo, pis IS NOT NULL as pis
FROM employees WHERE status = 'ativo' AND (data_nascimento IS NULL OR sexo IS NULL)
ORDER BY nome;"

# Ver logs do worker Celery integrations
docker logs conecta-pro-celery-integrations --since 5m | grep -i solides
```

---

## 8. RESPOSTA: A INTEGRACAO E 24/7 FULL DUPLEX?

### PARCIALMENTE — veja o quadro:

| Funcionalidade | Status | Detalhe |
|---------------|--------|---------|
| Conexao com Solides | ✅ Ativa | API token funcionando |
| Busca de funcionarios | ✅ Automatica | Celery a cada 15min |
| Health check | ✅ Automatico | Celery a cada 5min |
| Webhook queue | ✅ Ativo | Processa a cada 30s |
| Webhook do Solides | ❌ Desabilitado | Precisa configurar URL no painel |
| Propagacao staging→employees | ⚠️ Manual | Script existe, precisa automatizar |
| Sync de ponto | ❌ Nao implementado | API existe, falta codigo |
| Sync de ausencias | ❌ Nao implementado | API existe, falta codigo |
| Inativacao automatica | ❌ Nao implementado | Quando demitido no Solides |

### Para ficar 100% full duplex:
1. **Configurar webhook no painel Solides** (15min)
   → Admissao, rescisao, alteracao = atualiza imediato
2. **Automatizar propagacao** (2-4h de dev)
   → staging → employees automatico no sync
3. **Sync de ponto** (4-8h de dev)
   → Batidas em tempo real
4. **Sync de ausencias** (2-4h de dev)
   → Faltas, ferias, afastamentos

**Estimativa total: 8-16h de desenvolvimento para 100% full duplex.**

---

**Relatorio gerado por:** Claude Opus 4.6 (1M context)
**Data:** 23 de Marco de 2026
