# INSPEÇÃO CIRÚRGICA — CONECTA PRO
## Data: 15/03/2026 | Executado por: Claude Code Opus

---

## ALVO 1 — CCT (deprecated/fase5)

### Localização exata:
`/opt/conecta-pro/backend/modules/fase5/cct_compliance/`

### Arquivos encontrados (7):
| Arquivo | Função |
|---------|--------|
| `__init__.py` | Exports do módulo |
| `enums.py` | 6 enums: TipoCargo (35 cargos), TipoJornada (6), TipoBeneficio (14), StatusValidacao, GrauInsalubridade, GrauPericulosidade |
| `models.py` | 4 Pydantic models + 2 tabelas hardcoded (TABELA_PISOS_SINDCOND_2026, BENEFICIOS_CCT_2026) |
| `service.py` | CCTComplianceService: 7 métodos (validar_salario, validar_jornada, validar_beneficios, validar_completo, calcular_custo, gerar_proposta, listar_cargos) |
| `agents/cct_agent.py` | CCTComplianceAgent (async multi-agent wrapping service) |
| `agents/base.py` | BaseAgent abstract class |
| `tests/test_cct_compliance.py` | 25+ testes |

### Dados hardcoded:
- **35 cargos** com piso salarial SINDCOND 2026 (reajuste 7.1%)
- **4 benefícios obrigatórios**: VA R$22/dia, Cesta R$18/mês, VT, Seguro Vida
- **Encargos**: INSS 20%, FGTS 8%, RAT 2%, Sistema S 3.3%, Férias 11.11%, 13o 8.33% = ~52.44%
- **ATENÇÃO**: `pricing_engine.py` (CRM) tem OUTRA tabela com 10 componentes = ~73.11%. DIVERGÊNCIA!

### Tabelas no banco de dados:
**NENHUMA.** Zero tabelas CCT existem. Todos os dados são Pydantic in-memory.

### Regras já implementadas:

| Regra | Status | Detalhe |
|-------|--------|---------|
| Piso salarial (35 cargos) | COMPLETO | Valores 2026 hardcoded |
| Validação salário vs piso | COMPLETO | Compara e retorna conforme/nao_conforme |
| Escalas permitidas por cargo | COMPLETO | 12x36, 44h, 6x1, 5x2 mapeados |
| Validação jornada | COMPLETO | Verifica escala permitida para cargo |
| Benefícios obrigatórios | PARCIAL | Só 4 de 14 tipos têm valores monetários |
| Adicional noturno 20% | DEFINIDO | No modelo, NÃO no cálculo de custo |
| Periculosidade 30% | ENUM | Definido, NÃO calculado |
| Insalubridade 10/20/40% | ENUM | Definido, NÃO calculado |
| HE 50%/100% | DEFINIDO | No modelo, NÃO no cálculo |
| Cálculo custo funcionário | COMPLETO | Salário + benefícios + encargos |
| Proposta comercial | COMPLETO | Custo + margem |
| Score compliance (0-100) | COMPLETO | 40pts salário + 30pts jornada + 30pts benefícios |

### Regras FALTANDO:
1. Adicionais (noturno, periculosidade, insalubridade) no cálculo de custo
2. Benefícios plano saúde, odonto sem valores
3. Sindicato hardcoded como SINDCOND/SP — Conecta PRO opera em Manaus/AM (SINDECOMPRESTS)
4. Versionamento por vigência (CCT 2026 → 2027)
5. Persistência em banco (zero tabelas)
6. Endpoints REST (nenhum controller)
7. Frontend (nenhuma página)

### Diagnóstico:
- **Por que orphaned?** Módulo fase5 foi marcado como experimental/deprecated na sessão 19. Nunca foi migrado.
- **Vale reaproveitar?** SIM. A lógica de validação (service.py) e os enums são sólidos. Precisa: (1) converter Pydantic → SQLAlchemy, (2) reconciliar encargos com pricing_engine, (3) adicionar dados Manaus/AM, (4) criar controller + frontend.

---

## ALVO 2 — CONECTOR SÓLIDES

### Localização exata:
`/opt/conecta-pro/backend/modules/integrations/connectors/solides/`

### Arquivos (12):
connector.py, models.py (15 tabelas), schemas.py (30+ schemas), sync_service.py, integration_service.py, mappers.py (1103 linhas), conflict_resolver.py, webhook_handler.py, tasks.py (10 Celery tasks), solides_controller.py (15+ endpoints), __init__.py

### 15 tabelas no banco:

| # | Tabela | Cols | Função | Registros |
|---|--------|:---:|--------|:---:|
| 1 | solides_sync_state | 20 | Cursor de sync por entidade | 0 |
| 2 | solides_sync_log | 24 | Log de operações de sync | 0 |
| 3 | solides_sync_conflict | 18 | Conflitos detectados | 0 |
| 4 | solides_entity_mapping | 17 | Mapeamento solides_id ↔ conecta_id | 0 |
| 5 | solides_webhook_log | 16 | Log de webhooks recebidos | 0 |
| 6 | solides_integration_config | 27 | Config por condomínio | 1 |
| 7 | solides_credential | 15 | Tokens API (encrypted) | 0 |
| 8 | **solides_employees** | 48 | **Staging — dados importados** | **44** |
| 9 | solides_departments | 15 | Staging — departamentos | 0 |
| 10 | solides_positions | 19 | Staging — cargos | 0 |
| 11 | solides_occurrences | 25 | Staging — ocorrências | 0 |
| 12 | solides_absences | 29 | Staging — afastamentos | 0 |
| 13 | solides_workplaces | 16 | Staging — locais de trabalho | 0 |
| 14 | solides_work_schedules | 15 | Staging — escalas | 0 |
| 15 | solides_cost_centers | 13 | Staging — centros de custo | 0 |

**IMPORTANTE:** `solides_employees` tem **44 registros** — os mesmos 44 colaboradores ativos do sistema. Dados JÁ foram importados do Sólides.

### Mapeamento de campos (34 campos):
nome→nome_completo, email→email, cpf→cpf, rg→rg, data_nascimento→data_nascimento, sexo→genero, estado_civil→estado_civil, telefone→telefone, celular→celular, endereco.*→endereco_*, matricula→matricula, cargo.nome→cargo_nome, departamento.nome→departamento_nome, data_admissao→data_admissao, salario→salario_base, ctps_*→ctps_*, pis→pis, situacao→status (ativo→active, etc.)

Mappers reversos também existem (Conecta→Sólides) para: employees, occurrences, absences, departments, positions, candidates.

### Fluxos de sync:
- **Full sync**: Busca todas entidades do Sólides em ordem de dependência
- **Incremental sync**: Usa `updated_since` para buscar apenas mudanças
- **Webhook**: 9 eventos suportados (novo/edição/demissão colaborador, ocorrência, absenteísmo, pesquisa, currículo, inscrição, mudança etapa) — **STUBS, não processam**
- **Conecta→Sólides**: Mappers existem mas sync reverso tem `# TODO`
- **Conflitos**: 4 estratégias (SOLIDES_WINS, CONECTA_WINS, MOST_RECENT, MANUAL)

### Por que NÃO está conectado ao GP:
1. **Zero imports** de `solides` em `people_management/`
2. `integration_service.py` tenta importar `from modules.hr.models import Funcionario` — modelo que NÃO existe nesse path
3. Dados vão Sólides API → `solides_employees` staging → **PARAM** (nunca chega em `employees`)
4. `solides_entity_mapping` tem 0 rows = nenhum link ID estabelecido

### Variáveis de ambiente (TODAS configuradas):
- `SOLIDES_API_TOKEN` = configurado (Base64 Basic Auth)
- `SOLIDES_WEBHOOK_SECRET` = configurado (HMAC SHA256)
- `SOLIDES_SYNC_INTERVAL_MINUTES` = 15
- `SOLIDES_CONFLICT_STRATEGY` = most_recent
- `SOLIDES_AUTO_CREATE_DEPARTMENTS` = true
- `SOLIDES_AUTO_CREATE_POSITIONS` = true
- `SOLIDES_RATE_LIMIT_PER_MINUTE` = 60

### Passos para conectar ao GP:
1. Corrigir import path: `from modules.hr.models import Funcionario` → `from modules.operacional.models.employee import Employee`
2. Wiring staging→employees: mapear `solides_employees` → tabela `employees`
3. Popular `solides_entity_mapping` com CPF-based matching
4. Ativar webhook handlers (atualmente stubs)
5. Registrar tasks no Celery beat schedule
6. Integrar com event bus Redis PubSub (sessão 23)

---

## ALVO 3 — BUG RH

### Route Prefix Bug:

**Problema:** 3 wrapper controllers criam router com prefix E incluem sub-router que JÁ tem prefix. Prefixos se empilham.

**Exemplo (turnover):**
```
aggregator.py prefix="/human-resources"
  + wrapper turnover_controller.py prefix="/turnover"
    + retention/turnover/controllers prefix="/retention/turnover"
= /human-resources/turnover/retention/turnover/{endpoint}  ← DUPLICADO
```

**3 arquivos afetados:**

| Arquivo | Linha | Prefix wrapper | Prefix child | Path resultante |
|---------|:---:|---|---|---|
| `human_resources/controllers/turnover_controller.py` | 13+20 | `/turnover` | `/retention/turnover` | `/human-resources/turnover/retention/turnover/` |
| `human_resources/controllers/climate_controller.py` | 13+20 | `/climate` | `/retention/climate` | `/human-resources/climate/retention/climate/` |
| `human_resources/controllers/onboarding_controller.py` | 13+20 | `/onboarding` | `/retention/onboarding` | `/human-resources/onboarding/retention/onboarding/` |

**Teste confirmou:**
- `/human-resources/turnover/dashboard` → 404 (path correto não existe)
- `/human-resources/turnover/retention/turnover/dashboard` → 422 (rota encontrada no path duplicado)

**Correção:** Em cada wrapper, passar `prefix=""` no `include_router()` para sobrescrever o prefix do child.

### Recruitment 500:

**Causa raiz:** Mismatch massivo entre SQLAlchemy models e schema real do banco.

**Tabela `candidates` — 30+ colunas divergentes:**

| Modelo Python | Banco Real |
|---|---|
| `neighborhood` | NÃO EXISTE |
| `salary_expectation_pj` | NÃO EXISTE |
| `available_immediately` | `availability` |
| `profile_score` | `ai_score` |
| `resume_file_path` | `resume_url` |
| `condominium_id` | `tenant_id` |
| `created_by` | NÃO EXISTE |
| + 25 colunas extras no modelo | NÃO EXISTEM no banco |

**Tabela `job_positions` — 14+ colunas divergentes:**

| Modelo Python | Banco Real |
|---|---|
| `salary_display` | `show_salary` |
| `filled_vacancies` | `filled_count` |
| `opening_date` | `published_at` |
| `deadline_date` | `deadline` |
| `recruiter_id` | `responsible_id` |
| `condominium_id` | `condominio_id` |
| + 8 colunas extras no modelo | NÃO EXISTEM no banco |

**Erro nos logs:**
```
asyncpg.exceptions.UndefinedColumnError: column candidates.neighborhood does not exist
asyncpg.exceptions.UndefinedColumnError: column job_positions.salary_display does not exist
```

**Tabelas que EXISTEM no banco:** candidates, job_positions, applications, interviews, candidate_educations, candidate_experiences, candidate_skills — todas 7 presentes.

**Correção:** 2 opções:
1. **Alembic migration** para adicionar/renomear ~44 colunas — arriscado e trabalhoso
2. **Reescrever models** para refletir o schema real do banco — mais seguro, menos trabalho

---

## SÍNTESE EXECUTIVA

### Prioridade 1 — RH Bug (Recruitment 500):
- **Impacto:** Recrutamento 100% inacessível
- **Correção:** Reescrever models `candidate.py` e `job_position.py` para refletir DB real
- **Esforço:** 2-3 horas
- **Também:** Corrigir 3 wrappers de prefix (15 min)

### Prioridade 2 — Sólides → GP:
- **Impacto:** 44 colaboradores importados mas parados em staging
- **Correção:** Corrigir import path + wiring staging→employees + popular entity_mapping
- **Esforço:** 4-6 horas
- **Pré-requisito:** Dados do Sólides via Chrome prompt (para validar mapeamento)

### Prioridade 3 — CCT:
- **Impacto:** Compliance trabalhista, cálculo de custos
- **Correção:** Extrair de fase5 → people_management/cct/, converter para SQLAlchemy, adicionar dados Manaus/AM
- **Esforço:** 8-12 horas (inclui frontend)
- **Pré-requisito:** Dados da CCT SINDECOMPRESTS 2026 (tabela salarial real)

### Sequência ideal:
1. Fix RH prefix + recruitment models (3h) → desbloqueia RH
2. Conectar Sólides ao GP (6h) → dados reais fluindo
3. Migrar CCT (12h) → compliance ativo
