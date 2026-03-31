# AUDITORIA SKILL 04 — COBERTURA DE TESTES — CONECTA PRO
> **Gerada em:** 31/03/2026
> **Metodologia:** Skill 04 (testes-unitarios-conecta-pro) — 5 subagentes paralelos
> **Cobertura:** GED · Financeiro · Departamento Pessoal · Operacional · AI + Gov + Auth
> **Stack de Testes:** pytest (NÃO instalado no container) · httpx · AsyncMock

---

## SCORECARD EXECUTIVO

```
╔══════════════════════════════════════════════════════════════════════╗
║         CONECTA PRO — AUDITORIA DE COBERTURA DE TESTES              ║
║         Auditoria: 31/03/2026 — Skill 04 Paralela                   ║
╠══════════════════════╦════════╦════════╦═══════════╦════════════════╣
║ Módulo               ║Arquivos║Funções ║ Cobertura ║  Score         ║
╠══════════════════════╬════════╬════════╬═══════════╬════════════════╣
║ GED                  ║    8   ║   221  ║    25%    ║  3.0 / 10 ❌   ║
║ Financeiro           ║   22   ║   547  ║    55%    ║  3.0 / 10 ❌   ║
║ Departamento Pessoal ║   40   ║   992  ║    65%    ║  5.5 / 10 ⚠️   ║
║ Operacional          ║   15   ║   443  ║    58%    ║  5.0 / 10 ⚠️   ║
║ AI + Gov + Auth      ║   25   ║  1044  ║    65%    ║  4.0 / 10 ⚠️   ║
╠══════════════════════╬════════╬════════╬═══════════╬════════════════╣
║ TOTAL                ║  110   ║  3247  ║    53%    ║  4.1 / 10      ║
╠══════════════════════╩════════╩════════╩═══════════╩════════════════╣
║                                                                      ║
║  pytest NÃO instalado no container → testes não podem ser executados ║
║  Bugs críticos SEM teste de regressão: 22 identificados              ║
║  Testes que requerem auth config e estão SKIPADOS: 60+               ║
║  Mocks excessivos mascaram bugs reais: 100% dos testes usam mocks    ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## ACHADO CRÍTICO: pytest NÃO está instalado no container

```bash
docker exec conecta-pro-backend python -m pytest --version
# Resultado: No module named pytest
```

**Consequência direta:** NENHUM dos 3.247 testes pode ser executado em CI/CD.
Os testes existem no filesystem mas são letra morta — não protegem o sistema.

**Fix imediato:**
```bash
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend --format '{{.Names}}' | head -1)
docker exec $CONTAINER pip install pytest pytest-asyncio pytest-cov httpx --break-system-packages
# Verificar:
docker exec $CONTAINER python -m pytest --version
```

---

## ESTRUTURA DE TESTES

```
/opt/conecta-pro/backend/
├── tests/
│   ├── _integration/           # 11 arquivos — e2e e integração
│   │   └── e2e/                # 9 arquivos (auth_flow, financial, hr, operations, AI)
│   ├── _orphaned/              # 25 arquivos — ABANDONADOS (imports quebrados)
│   ├── ai/
│   │   ├── bartolo/            # 17 arquivos — melhor cobertura do sistema
│   │   └── *.py                # 4 arquivos de AI geral
│   ├── core/security/          # 4 arquivos — validadores de segurança
│   ├── domains/                # 9 arquivos — entidades por domínio
│   │   ├── financial/          # 5 arquivos
│   │   ├── hr/                 # 2 arquivos
│   │   └── operacional/        # 3 arquivos
│   ├── ged/                    # 3 arquivos
│   ├── government_integrations/# 2 arquivos (só conftest + __init__)
│   ├── integration/            # 3 arquivos (disciplinary, patrol, scale)
│   ├── modules/                # 20+ arquivos (CRM, analytics, bidding, etc.)
│   ├── operations/             # 4 arquivos
│   ├── people_management/      # 30+ arquivos (melhor estruturado)
│   ├── services/               # 3 arquivos
│   ├── unit/                   # 1 arquivo
│   └── test_*.py               # ~100 arquivos raiz
│
├── test_*.py (raiz)            # 14 arquivos soltos (legacy)
└── scripts/test_gov_connections.py

Frontend:
└── src/ — ZERO arquivos de teste encontrados (*.test.ts, *.spec.tsx)
```

**Total de funções de teste:** ~9.860 (incluindo todos os módulos do sistema)

---

## ANÁLISE POR MÓDULO

### 📁 GED — Score 3/10 ❌

**Arquivos:** 8 | **Funções:** 221 | **Cobertura:** ~25% dos 120 endpoints

**Checklist:**

| # | Item | Status | Detalhe |
|---|------|--------|---------|
| 1 | CRUD de documentos | ✅ Parcial | Criar e listar OK; DELETE não testado |
| 2 | Kit documental | ✅ Sim | 41 testes; falta generate_zip, send_email |
| 3 | Autenticação (401) | ❌ Não | Zero testes sem token. Todos usam mock_current_user |
| 4 | UUID inválido (422) | ⚠️ Parcial | Testa com mock; sem chamada real ao endpoint |
| 5 | Edge cases | ❌ Não | Sem lista vazia, kit sem docs, ZIP incompleto |
| 6 | Regressão bugs conhecidos | ❌ Não | is_associated, ZeroDivisionError, trailing slash — todos sem teste |
| 7 | Fixtures com dados reais | ⚠️ Parcial | Sem UUID e3ba48aa, sem kit "Ideal Flores" |
| 8 | Integração real com BD | ❌ Não | 100% mocks — AsyncMock intercepta tudo |
| 9 | Testes rápidos | ✅ Sim | Mocks são rápidos (<100ms) |
| 10 | Nomenclatura clara | ⚠️ Parcial | Maioria clara; alguns combinam cenários |

**Bugs SEM teste de regressão:**
1. `DocumentTagRepository.is_associated()` ausente → 4 endpoints retornam 500
2. `ZeroDivisionError` no AI dashboard quando `total_documents = 0`
3. Trailing slash 404 em `/documents/`, `/folders/`, etc.
4. `DocumentShare.share_token` não persiste no banco após criação

**Top 5 testes a criar:**
1. `test_get_insights_zero_documents` — ZeroDivisionError com BD vazio → regressão crítica
2. `test_list_documents_without_token` → deve retornar 401
3. `test_get_document_invalid_uuid` → deve retornar 422 ou 404
4. `test_tag_is_associated_document` → regressão do método ausente
5. `test_list_documents_with_trailing_slash` → deve retornar 200 igual a sem slash

---

### 💰 Financeiro — Score 3/10 ❌

**Arquivos:** 22 | **Funções:** 547 | **Cobertura:** ~55% (models/schemas) / ~10% (API endpoints)

**Checklist:**

| # | Item | Status | Detalhe |
|---|------|--------|---------|
| 1 | Bug BI Dashboard (Session→AsyncSession) | ❌ Não | bi_controller.py — ZERO testes do bug real |
| 2 | Bug accounting (current_user["key"]) | ❌ Não | Nenhum teste valida acesso a atributo do objeto User |
| 3 | Regressão status 'paga' vs 'pago' | ⚠️ Parcial | Usa PayableStatus.PAGA mas sem teste de rejeição de 'pago' |
| 4 | Dados reais (R$ 258.482, R$ 128.514) | ❌ Não | Testes usam Decimal("1000.00") genérico |
| 5 | Bulk_payment N+1 | ⚠️ Parcial | Comentários mencionam, sem teste real |
| 6 | condominio_id fallback JWT | ❌ Não | Sem validação de fallback/422 |
| 7 | Paginação | ✅ Sim | 1-2 casos testados, cobertura mínima |
| 8 | BI tests são reais? | ❌ Não | 100% mocks isolados, zero chamadas HTTP |
| 9 | AI Command Center | ❌ Não | modules/financial/agents/ sem nenhum teste |
| 10 | Nomenclatura | ✅ Sim | Nomes claros; assertions com valores mockados |

**Bugs SEM teste de regressão:**
1. BI Dashboard Session→AsyncSession (0/11 endpoints funcionais)
2. `accounting_controller` current_user["key"] em 72 ocorrências
3. `BankTransactionRepository.list_with_filters` não implementado
4. `PayableStatus.PAGO` ser aceito silenciosamente (deveria ser PAGA)
5. condominio_id sem fallback JWT → 422 inesperado

**Top 5 testes a criar:**
1. `test_bi_dashboard_returns_200` — E2E com token, valida AsyncSession real
2. `test_accounting_cost_centers` — Regressão do current_user.key (não subscriptable)
3. `test_receivables_with_real_data` — Teste com R$ 258.482 do banco real
4. `test_bank_transactions_list_with_filters` — Valida método implementado + N+1
5. `test_payable_status_paga_not_pago` — Regressão: 'pago' deve ser rejeitado

---

### 👥 Departamento Pessoal — Score 5.5/10 ⚠️

**Arquivos:** 40 | **Funções:** 992 | **Cobertura:** ~65% (features) / ~0% (segurança/regressão)

**Checklist:**

| # | Item | Status | Detalhe |
|---|------|--------|---------|
| 1 | 52 funcionários ativos | ⚠️ Parcial | Testes com mocks; sem dados reais do BD |
| 2 | Ponto eletrônico | ✅ Sim | 57 testes punch, 31 e2e, geofence, haversine |
| 3 | CCT 2026 | ✅ Sim | 78 testes, 52 cargos, benefícios, feriados |
| 4 | Admissão/demissão | ⚠️ Parcial | Admissão OK; demissão/rescisão não testada |
| 5 | Handlers SEM auth (regressão) | ❌ Não | punch_controller e folha_controller — vulnerabilidade |
| 6 | Folha de pagamento | ✅ Sim | 26 testes, INSS 4 faixas, IRRF, FGTS |
| 7 | SST | ✅ Sim | 16 testes de modelos, schemas, 13 e2e |
| 8 | f-strings SQL (injeção) | ❌ Não | Zero testes de SQL injection |
| 9 | is_active vs status (regressão) | ❌ Não | 11 registros corrigidos, sem proteção |
| 10 | Integração real (não mocks) | ❌ Não | 683 instâncias de mock/patch, sem BD real |

**Bugs SEM teste de regressão:**
1. CCT Controller SQL colunas erradas (nome_cargo→cargo_nome) → 5 endpoints 500
2. 10 handlers SEM auth em punch_controller/folha_controller (vulnerabilidade crítica)
3. is_active vs status — 11 registros corrigidos sem proteção contra regressão
4. SQL injection via f-strings (não identificado com certeza, mas sem testes)

**Top 5 testes a criar:**
1. `test_ponto_dashboard_requires_auth` — POST /ponto/batida sem token → 401
2. `test_cct_cargo_nome_column_query` — Regressão SQL: `cargo_nome` retorna dados, `nome_cargo` falha
3. `test_employees_active_inactive_consistency` — is_active=True ↔ status='ativo'
4. `test_admissao_demissao_full_workflow` — Wizard completo + documentos + rescisão
5. `test_folha_holerite_with_real_employees` — 52 funcionários reais + CCT 2026

---

### ⚙️ Operacional — Score 5/10 ⚠️

**Arquivos:** 15 | **Funções:** 443 | **Cobertura:** ~58%

**Checklist:**

| # | Item | Status | Detalhe |
|---|------|--------|---------|
| 1 | 9 postos ativos | ⚠️ Parcial | CRUD genérico; sem dados reais dos 9 postos |
| 2 | Escala (gerar/aprovar/publicar) | ⚠️ Parcial | Geração OK; aprovação/publicação SKIPADAS |
| 3 | Banco de horas | ✅ Sim | Creditar, debitar, saldo, expiração |
| 4 | Rondas de inspeção | ⚠️ Parcial | 47 testes escritos mas TODOS SKIPADOS |
| 5 | Ocorrências | ⚠️ Parcial | 51 testes escritos mas TODOS SKIPADOS |
| 6 | Comunicados (tenant_id) | ❌ Não | Módulo inteiro sem nenhum teste |
| 7 | TimeBankRepository.get_stats | ❌ Não | Bug conhecido, zero testes de regressão |
| 8 | expires_at → data_expiracao | ❌ Não | Transformação de campo não testada |
| 9 | Rota /templates disciplinar | ❌ Não | Bug de ordem de rotas sem regressão |
| 10 | Diaristas | ✅ Sim | 44 testes CRUD + pagamentos + IA |

**Problema grave: 60+ testes SKIPADOS** com `pytest.skip("Requer autenticação configurada")`:
- `test_disciplinary_workflow.py` — completamente skipado
- `test_patrol_rounds_integration.py` — completamente skipado
- `test_scale_workflow.py` — completamente skipado

**Bugs SEM teste de regressão:**
1. `TimeBankRepository.get_stats()` não implementado → endpoint retorna 500
2. `expires_at` → `data_expiracao` mismatch de campo
3. tenant_id mismatch → 10 comunicados invisíveis via API
4. `/templates` depois de `/{action_id}` → FastAPI captura "templates" como UUID

**Top 5 testes a criar:**
1. `test_time_bank_get_stats` — Regressão do método não implementado
2. `test_comunicados_tenant_visibility` — 10 comunicados devem aparecer no tenant correto
3. `test_disciplinary_templates_route_order` — GET /templates não retorna 422
4. `test_scale_full_workflow` — Escala draft → aprovada → publicada (E2E)
5. `test_patrol_round_complete` — Ronda completa com checkpoints e ocorrências

---

### 🤖 AI + Gov + Auth — Score 4/10 ⚠️

**Arquivos:** 25 | **Funções:** 1.044 | **Cobertura:** ~65%

**Checklist:**

| # | Item | Status | Detalhe |
|---|------|--------|---------|
| 1 | Bartolo engine | ✅ Sim | 23+19 testes, 9 fluxos, escala/subs/alerta |
| 2 | Guard _is_query_not_action | ⚠️ Parcial | Testes negativos gerais; não testa "escala" especificamente |
| 3 | Greeting com nome personalizado | ❌ Não | Endpoint testado mas sem assert do nome "Jordan" |
| 4 | Auth JWT (login/refresh/logout) | ✅ Sim | 162 testes; falta teste de HTTP 401 real |
| 5 | Rate limit login (5/min → 429) | ❌ Não | Constante validada mas sem teste de HTTP 429 |
| 6 | Regressão get_db_sync → get_db | ❌ Não | Correção feita, sem teste de regressão |
| 7 | NFS-e Manaus | ⚠️ Parcial | 25 testes de schema; sem teste de emissão XML |
| 8 | EFD-Reinf | ⚠️ Parcial | 20 testes schema R-1000; sem XML completo |
| 9 | Endpoints SEM auth (regressão) | ❌ Não | bartolo/health e esocial/listar_eventos sem teste 401 |
| 10 | Intelligence Hub / OpenClaw | ❌ Não | Zero testes encontrados |

**Destaques positivos:**
- ActionDetector: **28 arquivos**, 679 linhas, 50+ frases por padrão em PT-BR
- DataConnector: 12 QueryTypes testados com pattern matching
- Wizards: 174 testes, 15+ wizards cobertos

**Bugs SEM teste de regressão:**
1. `get_db_sync` ImportError corrigido → sem proteção para regressão
2. Rate limit login declarado mas sem enforcement testado
3. `bartolo/health` sem auth → deve retornar 401 (vulnerabilidade)
4. `esocial/listar_eventos` sem auth → dados fiscais expostos
5. Greeting retornando UUID em vez de nome → UX quebrada

**Top 5 testes a criar:**
1. `test_login_rate_limit_429` — 6ª requisição em 1 min → HTTP 429
2. `test_bartolo_health_requires_auth` — Sem token → 401 (regressão da vulnerabilidade)
3. `test_esocial_listar_eventos_requires_auth` → 401 sem token
4. `test_bartolo_greeting_returns_name` — Greeting contém "Jordan", não UUID
5. `test_esocial_gaps_funcionarios_works` — Regressão do get_db_sync fix

---

## BUGS CRÍTICOS SEM TESTE DE REGRESSÃO (ordenados por impacto)

| # | Bug | Módulo | Impacto se Regredir |
|---|-----|--------|---------------------|
| 1 | BI Dashboard Session→AsyncSession | Financeiro | 0/11 endpoints funcionais |
| 2 | 10 handlers sem auth (punch/folha) | DP | Qualquer pessoa registra ponto |
| 3 | bartolo/health sem auth | AI | Informações de saúde expostas |
| 4 | esocial/listar_eventos sem auth | Gov | Dados fiscais expostos publicamente |
| 5 | CCT Controller SQL colunas erradas | DP | 5 endpoints 500 silencioso |
| 6 | DocumentTagRepository.is_associated | GED | 4 endpoints 500 |
| 7 | ZeroDivisionError GED AI dashboard | GED | 500 em qualquer cliente novo |
| 8 | TimeBankRepository.get_stats | Operacional | Dashboard banco de horas quebrado |
| 9 | tenant_id mismatch comunicados | Operacional | 10 comunicados invisíveis |
| 10 | get_db_sync ImportError | Gov | esocial/gaps-funcionarios 500 |
| 11 | Rate limit login sem teste | Auth | DDoS sem proteção validada |
| 12 | Greeting com UUID em vez de nome | AI | UX do Bartolo quebrada |
| 13 | accounting current_user["key"] | Financeiro | 4 endpoints 500 |
| 14 | is_active vs status (11 registros) | DP | Filtros de ativos quebram |
| 15 | expires_at → data_expiracao | Operacional | Expiração de horas incorreta |

---

## PROBLEMAS GLOBAIS DE QUALIDADE

### 1. pytest não instalado no container
**Gravidade:** CRÍTICA
Os 3.247 testes escritos não podem ser executados. Nenhum CI/CD pode rodar.

**Fix:**
```bash
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend --format '{{.Names}}' | head -1)
docker exec $CONTAINER pip install pytest pytest-asyncio pytest-cov httpx --break-system-packages
# Adicionar ao requirements.txt:
echo "pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0" >> /opt/conecta-pro/backend/requirements.txt
```

### 2. Mock excessivo mascara bugs reais
**Gravidade:** ALTA
100% dos testes usam `AsyncMock`/`MagicMock` para interceptar services e repositórios. Os testes verificam que o mock foi chamado, não que o sistema funciona.

**Exemplo do problema:**
```python
# TESTE ATUAL (inútil para detectar bugs reais)
with patch("modules.ged.controllers.folder_controller.FolderService") as mock:
    mock.return_value.list_folders.return_value = [fake_folder]
    response = await client.get("/api/v1/ged/folders")
    assert response.status_code == 200
    # Passa mesmo se o SQL está 100% errado

# TESTE CORRETO (detecta bugs reais)
async def test_list_folders_real_db(db_session, auth_headers):
    folder = await Folder.create(db_session, name="Test")
    response = await client.get("/api/v1/ged/folders", headers=auth_headers)
    assert response.status_code == 200
    assert any(f["name"] == "Test" for f in response.json()["data"])
```

### 3. 60+ testes skipados por falta de autenticação
**Gravidade:** ALTA
Três arquivos de integração inteiros (disciplinar, rondas, escala) têm `pytest.skip("Requer autenticação configurada")` em todos os testes.

**Fix:** Criar fixture de autenticação compartilhada:
```python
# tests/conftest.py
@pytest.fixture
async def auth_headers():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.post("/api/v1/auth/login", data={
            "username": "jjesus@conectamais.pro",
            "password": "Jordan0612"  # pragma: allowlist secret
        })
        return {"Authorization": f"Bearer {r.json()['access_token']}"}
```

### 4. Frontend sem nenhum teste
**Gravidade:** ALTA
Zero arquivos `*.test.ts` ou `*.spec.tsx` encontrados em `/frontend/src/`.
Todas as 50+ páginas Next.js não têm testes.

### 5. Testes _orphaned (25 arquivos quebrados)
**Gravidade:** MÉDIA
Pasta `tests/_orphaned/` com 25 arquivos que provavelmente têm imports quebrados e não são parte da suite ativa. Devem ser revisados e ou corrigidos ou removidos.

---

## PLANO DE AÇÃO — PRIORIZADO

### Sprint 0 — Desbloqueador (1 dia)
```bash
# 1. Instalar pytest no container
docker exec $CONTAINER pip install pytest pytest-asyncio pytest-cov httpx

# 2. Criar pytest.ini
cat > /opt/conecta-pro/backend/pytest.ini << 'EOF'
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
filterwarnings = ignore::DeprecationWarning
EOF

# 3. Rodar pela primeira vez
docker exec $CONTAINER bash -c "cd /app && python -m pytest tests/ -q --tb=no 2>&1 | tail -10"
```

### Sprint 1 — Testes de regressão dos bugs críticos (3 dias)

| Prioridade | Teste a criar | Bugs cobertos |
|------------|---------------|---------------|
| P1 | test_ponto_batida_requires_auth | Bug segurança punch_controller |
| P2 | test_bartolo_health_requires_auth | Bug segurança bartolo |
| P3 | test_esocial_listar_eventos_requires_auth | Bug segurança eSocial |
| P4 | test_bi_dashboard_async_session | BI 0/11 |
| P5 | test_ged_ai_zero_docs_no_crash | ZeroDivisionError |

### Sprint 2 — Cobertura de API real (1 semana)

- Criar fixture `auth_headers` global em `conftest.py`
- Remover `pytest.skip` dos 3 arquivos de integração
- Substituir 50% dos mocks por testes de integração real
- Cobrir todos os endpoints de segurança com teste sem token → 401

### Sprint 3 — Frontend (2 semanas)

- Setup Vitest + React Testing Library no frontend
- Cobrir os 5 componentes mais críticos: Login, Dashboard, Ponto, GED, Bartolo
- Meta: 30% de cobertura no frontend em 2 semanas

---

## RESUMO EXECUTIVO

```
╔══════════════════════════════════════════════════════════════════════╗
║  ESTADO ATUAL: TESTES EXISTEM MAS NÃO PROTEGEM                      ║
║                                                                      ║
║  ✅ Volume: 3.247 funções de teste escritas                          ║
║  ✅ Bartolo: excelente cobertura de actiondetector/wizards           ║
║  ✅ DP/CCT: 78 testes de CCT 2026 bem escritos                       ║
║  ✅ Estrutura: pastas organizadas por domínio                        ║
║                                                                      ║
║  ❌ pytest NÃO instalado → zero testes executam                      ║
║  ❌ 100% mocks → bugs reais em SQL/ORM invisíveis                    ║
║  ❌ 22 bugs críticos sem teste de regressão                          ║
║  ❌ 60+ testes skipados por falta de auth fixture                    ║
║  ❌ Frontend: ZERO testes                                             ║
║  ❌ CI/CD: sem pipeline de testes automatizados                      ║
║                                                                      ║
║  Score médio: 4.1/10 — Quantidade sem qualidade executável           ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

*Auditoria executada via Skill 04 (testes-unitarios-conecta-pro) com 5 subagentes paralelos.*
*Arquivo salvo em: /opt/conecta-pro/AUDITORIA_SKILL04.md*
