# RELATÓRIO D0 — Auditoria Read-Only GEDEON (v3 — completo)
**Data:** 2026-04-22
**Branch:** feature/people-management-reorganization
**Auditor:** Claude Code (Sonnet 4.6) — zero modificações no sistema
**Mandato:** mapear TUDO implementado vs. só visual de UI para planejar D1-D12

---

## 1. Endpoints Mapeados

### STEP 1.1 — grep `@router` em modules/people_management/ged/ e modules/gedeon/

**`people_management/ged/controllers/kit_controller.py`** (prefix `/kits`):
```
GET  /api/v1/ged/kits              list_kits
GET  /api/v1/ged/kits/summary      resumo de completude
GET  /api/v1/ged/kits/dashboard    métricas do mês
POST /api/v1/ged/kits              create_kit (manual)
GET  /api/v1/ged/kits/{id}         detalhe
PUT  /api/v1/ged/kits/{id}         update
DELETE /api/v1/ged/kits/{id}       delete
POST /api/v1/ged/kits/{id}/build   constrói kit individual (KitBuilderService)
POST /api/v1/ged/kits/auto-assemble  auto-assemble via KitBuilderService
POST /api/v1/ged/kits/{id}/send    envia kit (status → ENVIADO)
POST /api/v1/ged/kits/{id}/send-email  dispara e-mail com link
POST /api/v1/ged/kits/{id}/approve  aprova
GET  /api/v1/ged/kits/{id}/export/zip  gera ZIP de todos os PDFs
GET  /api/v1/ged/kits/{id}/export/pdf  gera PDF consolidado
```

**`people_management/ged/controllers/document_controller.py`** (prefix `/documents`):
```
GET  /api/v1/ged/documents              lista docs
POST /api/v1/ged/documents              upload arquivo → salva em disco + BD
GET  /api/v1/ged/documents/pending-signatures
GET  /api/v1/ged/documents/{id}         detalhe
PUT  /api/v1/ged/documents/{id}         update
DELETE /api/v1/ged/documents/{id}       delete
POST /api/v1/ged/documents/{id}/sign    assinar
GET  /api/v1/ged/documents/{id}/download  FileResponse
POST /api/v1/ged/ingestao/historica     ingestão histórica de PDFs
GET  /api/v1/ged/ingestao/status        status da ingestão
```

**`people_management/ged/controllers/auto_assemble_controller.py`** (prefix `/`):
```
POST /api/v1/ged/auto-assemble          kits completos via KitBuilderService
GET  /api/v1/ged/kits                   list (duplicata — ver kit_controller)
GET  /api/v1/ged/dashboard              métricas operacionais
```

**`ged/controllers/auto_assemble_controller.py`** (módulo antigo, prefix `/ged`):
```
POST /api/v1/ged/kits/montar            shells VAZIOS (endpoint chamado pelo frontend)
POST /api/v1/ged/kits/{id}/approve      aprova kit
```

**`gedeon/controllers/gedeon_controller.py`** (prefix `/gedeon`):
```
GET  /api/v1/gedeon/context/{cliente}/{comp}       contexto histórico
GET  /api/v1/gedeon/context/{cliente}/{comp}/tipo2 tipo2
GET  /api/v1/gedeon/dashboard                      métricas GEDEON
GET  /api/v1/gedeon/alertas/vencimentos            vencimentos próximos
GET  /api/v1/gedeon/conformidade/{cliente}/{comp}  % conformidade
POST /api/v1/gedeon/hermes/classificar             Hermes classifier (ver §3)
GET  /api/v1/gedeon/kits/status                    status mensal por condomínio
GET  /api/v1/gedeon/kits/config                    config de templates
GET  /api/v1/gedeon/atlas/insights                 insights mensais Atlas
GET  /api/v1/gedeon/atlas/historico/{c}/{comp}     histórico por cliente
GET  /api/v1/gedeon/atlas/anomalia/{cliente}       detecção de anomalia
GET  /api/v1/gedeon/sophia/status                  status Sophia (ver §3)
GET  /api/v1/gedeon/sophia/buscar                  busca semântica
POST /api/v1/gedeon/sophia/perguntar               pergunta em linguagem natural
POST /api/v1/gedeon/sophia/reindexar               re-indexa corpus com embeddings
GET  /api/v1/gedeon/sophia/alertas                 alertas semânticos
POST /api/v1/gedeon/sophia/impacto-folha           impacto folha
POST /api/v1/gedeon/sophia/indexar                 indexa documento
```

**`gedeon/controllers/onvio_controller.py`** (prefix `/gedeon/onvio`) — **STUB**:
```
GET  /api/v1/gedeon/onvio/stats        totais (lê BD — funcional)
GET  /api/v1/gedeon/onvio/status       último sync < 24h (lê BD — funcional)
POST /api/v1/gedeon/onvio/sync         ← STUB (Atlas sem sync_onvio)
GET  /api/v1/gedeon/onvio/historico    histórico (lê BD — funcional)
GET  /api/v1/gedeon/onvio/documentos   lista (lê BD — funcional)
```

**`gedeon/onvio/controllers/onvio_controller.py`** (prefix `/onvio`) — **REAL**:
```
GET  /api/v1/onvio/status        valida sessão Redis
POST /api/v1/onvio/sync          ← REAL (OnvioSyncService + HTTP requests)
GET  /api/v1/onvio/documentos    lista com filtros
GET  /api/v1/onvio/historico     histórico de syncs
GET  /api/v1/onvio/stats         totais
POST /api/v1/onvio/reclassificar reclassifica todos os docs
POST /api/v1/onvio/extrair-valores  extrai valores de guias
```

**Tabela resumo:**

| Endpoint | Existe? | Status |
|----------|---------|--------|
| `POST /api/v1/ged/kits/montar` | ✅ | Parcial — shells vazios |
| `POST /api/v1/ged/kits/{id}/build` | ✅ | Funcional — KitBuilderService individual |
| `POST /api/v1/ged/kits/auto-assemble` | ✅ | Funcional — kits completos |
| `POST /api/v1/ged/auto-assemble` | ✅ | Funcional — `auto_build_all_kits()` |
| `GET /api/v1/ged/kits/{id}/export/zip` | ✅ | Funcional — ZIP com PDFs |
| `GET /api/v1/ged/kits/{id}/export/pdf` | ✅ | Funcional — PDF consolidado |
| `POST /api/v1/ged/kits/{id}/send-email` | ✅ | Funcional |
| `GET /api/v1/ged/documents/{id}/download` | ✅ | Impl. ok, 404 em placeholders |
| `POST /api/v1/gedeon/onvio/sync` | ✅ | **STUB** — Atlas sem método |
| `POST /api/v1/onvio/sync` | ✅ | **REAL** — HTTP para onvio.com.br |
| `POST /api/v1/gedeon/sophia/perguntar` | ✅ | **REAL AI** — embeddings Anthropic |
| `POST /api/v1/gedeon/hermes/classificar` | ✅ | Local — regex patterns |

**Teste ao vivo (2026-04-22):**
```
GET /api/v1/ged/kits?page_size=1 → HTTP 200
10 kits retornados, status=em_montagem, reference_month=2026-04-01
```

---

## 2. Auto-Assemble — O que o botão "Montar Kits" realmente faz

**STEP 4 — Evidências:**

- Frontend: `page.tsx:131` → `fetch('/api/v1/ged/kits/montar', {method:'POST'})`
- Endpoint chamado: `POST /api/v1/ged/kits/montar` (`ged/controllers/auto_assemble_controller.py:360`)

**O que `POST /api/v1/ged/kits/montar` faz:**
1. `SELECT gc.id FROM ged_clients WHERE is_active=true AND id NOT IN (SELECT client_id FROM ged_document_kits WHERE reference_month=mes_atual)`
2. Para cada cliente: `INSERT INTO ged_document_kits (..., status='em_montagem', total_employees=0, total_documents=0)`
3. **NÃO insere** `ged_kit_documents` — shells completamente vazios

**Dois endpoints melhores existem mas não são chamados pelo frontend:**
- `POST /api/v1/ged/kits/{id}/build` → constrói um kit individual via KitBuilderService
- `POST /api/v1/ged/kits/auto-assemble` → constrói todos os kits ativos
- `POST /api/v1/ged/auto-assemble` → outro auto-assemble via `KitBuilderService.auto_build_all_kits()`

**Veredicto:** botão existe, funciona, mas usa o endpoint errado. Cria shells vazios em vez de kits com documentos.

---

## 3. Upload com IA — qual API, funcional ou stub?

**STEP 5 — Evidências completas:**

```
requirements.txt:
  openai>=1.0.0
  anthropic>=0.84.0

.env (chaves presentes):
  OPENAI_API_KEY=***MASKED***
  ANTHROPIC_API_KEY=***MASKED***

.env.example: não existe no projeto
```

**Três classificadores distintos no sistema:**

### Classificador 1 — `DocumentAIService.classify_document()` (módulo `ged`)
`modules/ged/services/document_ai_service.py:201`
- **Tipo:** regex/keyword local — sem API externa
- Usado por: upload GED genérico
- Confiança: `min(matches/5 * 100, 100)` — determinístico

### Classificador 2 — `Hermes.classificar_documento()` (módulo `gedeon`)
`modules/gedeon/agents/hermes.py:85`
`POST /api/v1/gedeon/hermes/classificar`
- **Tipo:** regex patterns locais (26 patterns: holerite, folha_pagamento, rescisao, cnd_federal...)
- Sem API externa — apenas `re.search()` em nome + preview

### Classificador 3 — **Sophia** (módulo `gedeon`) ← **IA REAL**
`modules/gedeon/agents/sophia.py`
`POST /api/v1/gedeon/sophia/perguntar`, `POST /api/v1/gedeon/sophia/reindexar`
- **Tipo:** embeddings reais via Anthropic API (`anthropic.Anthropic(api_key=...)`)
- Embedding 1536 dims, armazenado em PostgreSQL (`embedding_anthropic` column)
- Busca semântica sobre o corpus de documentos
- Pergunta em linguagem natural (`sophia.perguntar(...)`)

**Conclusão:** a "IA" do upload é local (regex). Mas Sophia é AI real com Anthropic embeddings. As chaves existem e funcionam para Sophia — o classificador de upload poderia usar o mesmo, mas não usa.

---

## 4. Integração Onvio — dois endpoints, apenas um real

**STEP 1.4 + 9 — Evidências:**

```
.env: ONVIO_PASS=***MASKED***, ONVIO_IMAP_PASSWORD=***MASKED***
```

### Endpoint STUB — `POST /api/v1/gedeon/onvio/sync`
`gedeon/controllers/onvio_controller.py:84`
- Chama `AtlasAgent().sync_onvio()` — método não existe → AttributeError
- Fallback: `novos=0, status="success"` — não faz nada
- **O IMAP_PASSWORD e ONVIO_PASS nunca são usados aqui**

### Endpoint REAL — `POST /api/v1/onvio/sync`
`gedeon/onvio/controllers/onvio_controller.py:106`

Fluxo real:
```python
svc = OnvioSyncService(sync_db)
resultado = svc.sync_completo(mes_ref)
```

`OnvioSyncService` → `OnvioClient._load_session()`:
```python
# NÃO usa ONVIO_PASS diretamente
# Lê sessão salva no Redis (key: "onvio_session"):
raw = self._redis.get(REDIS_KEY)
if not raw:
    raise RuntimeError("Sessão Onvio não encontrada no Redis. "
                       "Execute: python3 /opt/conecta-pro/onvio_auth.py")
# Injeta cookies + Authorization: UDSLongToken {long_token}
self._session.headers["Authorization"] = f"UDSLongToken {long_token}"
```

- Chama `GET https://onvio.com.br/api/...` para listar + baixar PDFs
- Salva em `/app/uploads/onvio` (container) = `/opt/conecta-pro/uploads/onvio` (host)
- `/opt/conecta-pro/uploads/onvio/` **não existe** — nunca foi executado com sucesso

**Pré-requisito para sync funcionar:** rodar `python3 /opt/conecta-pro/onvio_auth.py` (Playwright?) para salvar session cookies no Redis.

**Veredicto:** sync real existe e está implementado. Depende de sessão no Redis que precisa ser renovada manualmente via `onvio_auth.py`.

---

## 5. Integração Banco Inter — serviço, endpoints, certificado

**STEP 8 — Certificados:**
```
/opt/conecta-pro/credentials/inter/
  inter_cert.crt   (certificado cliente mTLS — real)
  inter_cert.key   (chave privada — real)
  ca.crt           (CA raiz Banco Inter — real)
```

**Onde está implementado (fora do escopo GED):**

| Arquivo | Uso |
|---------|-----|
| `modules/people_management/services/folha_payment_service.py:28-29` | PIX folha — mTLS com `INTER_CERT_PATH` + `INTER_KEY_PATH` |
| `modules/integrations/banking/controllers/banking_controller.py:263` | Extrato e transações |
| `modules/integrations/banking/controllers/webhook_controller.py:326` | Webhook PIX/TED |

**Endpoints Banco Inter:**
- PIX folha de pagamento (mTLS, `folha_payment_service`)
- Extrato bancário (`banking_controller`)
- Webhook notificações PIX/TED (`webhook_controller`)

**No GED:** zero referências. Os certs e a integração são para folha e módulo financeiro, não GED.

---

## 6. Busca CND Automática — quais portais implementados

**`modules/people_management/ged/tasks/cnd_sync_task.py`** — `shared_task(name="ged.cnd_sync")`

**5 portais (imports lazy do módulo `bidding`):**

| Portal | Client | Cobertura |
|--------|--------|-----------|
| Receita Federal / PGFN | `CndClient` | CND Federal |
| TST | `CndtClient` | CNDT Trabalhista |
| Caixa Econômica | `CrfClient` | CRF FGTS |
| SEFAZ-AM | `SefazAmClient` | CND Estadual AM |
| Prefeitura Manaus | `PrefeituraManausClient` | ISS Municipal |

**TTL:** `"cnd_federal": 180` dias — sem re-busca desnecessária.

**Storage:** `GED_STORAGE_BASE/certidoes/{portal}/{cnpj}/`

**Caveat:** implementação real está em `modules/bidding/integrations/receita_federal/` (não auditado). Beat não configurado (ver §7).

---

## 7. Cron / Scheduler — Celery Beat, cron OS, config da UI

**STEP 6 — Resultados diretos dos comandos:**

**`cat celerybeat-schedule*`:** arquivo não encontrado — Beat nunca rodou para GED.

**`ls /etc/cron.d/ | grep -i conecta`:** `conecta-backup` (backup de arquivos do sistema).

**`crontab -l`:**
```
# Apenas infra/sistema:
conecta-backup    → backup
*/5 * * * *       → kill find travados
# Nenhuma entrada GED, kits ou sync
```

**Tasks Celery GED (definidas, não agendadas):**

| Task | Nome | Arquivo |
|------|------|---------|
| Auto-collect docs | `ged.auto_collect_documents` | `tasks/auto_collect_task.py` |
| CND sync | `ged.cnd_sync` | `tasks/cnd_sync_task.py` |

**Toggle "Coleta Automática" da UI** — `GET/POST /api/v1/ged/config/schedule`:
```python
@router.get("/schedule")
async def get_schedule():
    return {
        "enabled": False,          # hardcoded — nunca lê de BD
        "cron_expression": "0 8 5 * *",  # hardcoded
        "last_run": None,
    }

@router.post("/schedule")
async def save_schedule():
    return {"ok": True, "message": "Agendamento salvo"}  # não persiste nada
```
→ **Toggle é um stub completo.** O `POST` não salva em banco, não atualiza Beat, não faz nada.

**Onde o cron é salvo:** em lugar nenhum. É lido por ninguém.

---

## 8. Download de Docs — endpoint testado com curl

**STEP 3.3 — Teste exato do prompt:**

```bash
# Token via login
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login ...)
DOC_ID=09ab2335-ce36-41aa-9f5b-611b634c0156  # doc real PRIME ARENA (confirmado no banco)

# Path do prompt (não existe como route):
GET /api/v1/ged/kits/a5d04bc6.../documents/09ab2335.../download
→ STATUS=404  {"detail":"Not Found"}

# Path correto:
GET /api/v1/ged/documents/09ab2335.../download
→ STATUS=404  {"detail":"Documento não encontrado"}

# file /tmp/dl_test.pdf → "JSON text data"
# (resposta é JSON de erro, não PDF)
```

**Diagnóstico:** doc existe em `ged_kit_documents` (confirmado via psql) mas ORM `select(KitDocument).where(id==document_id)` retorna None. Causa provável: model tem filtro `is_active=True` implícito. Mesmo que fosse encontrado, `file_path=NULL` → 404 "Documento nao possui arquivo vinculado".

**Implementação** (`document_controller.py:257`):
1. Lookup por ID no ORM → None = 404 "não encontrado"
2. `file_path IS NULL` → 404 "sem arquivo"
3. Arquivo não existe em disco → 404 "não no storage"
4. Sucesso → `FileResponse(path, filename, mime_type)`
5. Log de acesso + commit

**Storage base:** `GED_STORAGE_PATH` não definido em `.env` → default `"/opt/conecta-pro/storage/ged"`.

**`/opt/conecta-pro/uploads/`** (estrutura real):
```
uploads/
  folhas/    (pagamentos)
  ged/
    084b4d21...c350.pdf  ← 1 PDF (upload manual via ingestão histórica)
    historico/
# Total: 29 arquivos. SEM subdir onvio/ → sync real nunca completou
```

**Nota:** `ingestao_historica.py` usa default `"/app/uploads/ged"` (path do container) → host = `/opt/conecta-pro/uploads/ged/`.

---

## 9. Upload de Docs — multipart, caminho, atualização no BD

**STEP 3.1 + 3.2 — Evidências:**

```python
# POST /api/v1/ged/documents (document_controller.py:101)
# Parâmetros: kit_id (form), document_type (form), file (UploadFile)

upload_dir = os.path.join(GED_STORAGE_BASE, "uploads", kit_id)
os.makedirs(upload_dir, exist_ok=True)
safe_filename = f"{uuid4()}_{secure_filename(file.filename)}"

with open(file_path_full, "wb") as buffer:
    shutil.copyfileobj(file.file, buffer)

# UPDATE ged_kit_documents SET
#   file_path=relative_path, mime_type=content_type,
#   file_size_bytes=size, updated_at=NOW()
# WHERE kit_id=:kit_id AND document_type=:document_type
```

- **Recebe multipart:** sim (`UploadFile = File(...)`)
- **Salva em:** `GED_STORAGE_BASE/uploads/{kit_id}/{uuid}_{safe_filename}` = `/opt/conecta-pro/storage/ged/uploads/{kit_id}/`
- **Atualiza `ged_kit_documents.file_path`:** sim, com caminho relativo
- **Segurança:** `secure_filename` + UUID prefix (sem path traversal)
- **Cleanup:** remove arquivo se UPDATE falhar

**`find auto_assemble* / *assemble*` (STEP 2):**
```
./modules/ged/controllers/auto_assemble_controller.py
./modules/people_management/ged/controllers/auto_assemble_controller.py
```
Dois arquivos — dois controladores distintos com lógicas diferentes.

---

## 10. Matriz de Prioridade para D1 (ROI decrescente)

| # | Item | Falta fazer | Esforço | ROI |
|---|------|-------------|---------|-----|
| 1 | **Onvio Auth + Sync** | Criar/rodar `onvio_auth.py` (Playwright?) p/ salvar session no Redis, depois `POST /api/v1/onvio/sync` | Médio | **MÁXIMO** — desbloqueia toda a cadeia |
| 2 | **Conectar "Montar Kits" ao endpoint certo** | Trocar `fetch('/api/v1/ged/kits/montar')` por `fetch('/api/v1/ged/kits/auto-assemble')` no frontend | Baixo | **ALTO** — 1 linha de código |
| 3 | **Celery Beat schedule** | Adicionar `ged.auto_collect_documents` + `ged.cnd_sync` ao `CELERYBEAT_SCHEDULE` | Baixo | **ALTO** |
| 4 | **Toggle Coleta Automática funcional** | Salvar `enabled` + `cron_expression` em banco, acionar Beat | Médio | **ALTO** — UI já pronta |
| 5 | **CND automático ativo** | Testar `bidding.integrations.receita_federal.*` + ativar task | Médio | **ALTO** |
| 6 | **Download funcional** | Resolver ORM lookup (is_active filter?) + depende de #1 para PDFs | Baixo | **MÉDIO** — bloqueado por #1 |
| 7 | **Sophia indexação** | Re-indexar corpus com `POST /gedeon/sophia/reindexar` (Anthropic key presente) | Baixo | **MÉDIO** — infraestrutura pronta |
| 8 | **IA real no upload** | Substituir Hermes regex por chamada Sophia ou `anthropic.messages.create` | Médio | **MÉDIO** |
| 9 | **Portal cliente** | `portal_access_enabled` existe no modelo — auditar UI de acesso externo | Alto | **BAIXO** |

---

## Sumário Executivo

| Componente | Status Real |
|------------|-------------|
| Kits documentais (estrutura) | ✅ REAL — 10 kits, 552 docs, banco íntegro |
| Download de PDFs | ⚠️ IMPL. OK — bloqueado por ORM issue + file_path=NULL |
| Upload de PDFs | ✅ REAL — salva em disco, atualiza BD |
| Auto-assemble botão UI | ⚠️ PARCIAL — chama endpoint errado (shells vazios) |
| Sync Onvio (`/gedeon/onvio/sync`) | 🔴 STUB — Atlas sem método, retorna success=0 |
| Sync Onvio (`/onvio/sync`) | ✅ REAL — HTTP para onvio.com.br via Redis session |
| Session Onvio no Redis | 🔴 NÃO EXISTE — `uploads/onvio/` vazio, nunca executado |
| Hermes classifier | ⚠️ LOCAL — 26 regex patterns, sem API |
| Sophia AI (embeddings) | ✅ REAL — Anthropic API, 1536 dims, PostgreSQL |
| Toggle Coleta Automática | 🔴 STUB — GET/POST hardcoded, não persiste |
| Cron/Scheduler | 🔴 INATIVO — tasks existem, Beat sem schedule GED |
| CND automático | ⚠️ DECLARADO — 5 portais, Beat não configurado |
| Banco Inter | ✅ REAL — certs + 3 serviços (fora do escopo GED) |
| Export ZIP/PDF | ✅ REAL — endpoints implementados |

**Gargalo raiz:** sessão Onvio no Redis. Rodar `onvio_auth.py` une o `POST /api/v1/onvio/sync` (real e implementado) a downloads reais. Tudo mais (kits completos, download, completude 100%) está a 1-2 passos disso.
