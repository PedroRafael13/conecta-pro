# RELATÓRIO D0 — Auditoria Read-Only GEDEON
**Data:** 2026-04-22
**Branch:** feature/people-management-reorganization
**Auditor:** Claude Code (Sonnet 4.6) — sessão read-only, zero modificações no sistema
**Mandato:** mapear o que está implementado de verdade vs. só visual de UI para planejar D1-D12

---

## 1. Endpoints Mapeados

**STEP 1.1 — Endpoints de kit/document/upload/download:**

```
modules/people_management/ged/controllers/auto_assemble_controller.py
  POST /auto-assemble       → KitBuilderService.auto_build_all_kits()
  GET  /kits                → lista kits com filtros
  GET  /dashboard           → métricas operacionais

modules/people_management/ged/controllers/document_controller.py
  GET  /documents           → lista documentos
  POST /documents/upload    → UploadFile → salva em disco + BD
  GET  /documents/{id}      → detalhe
  PUT  /documents/{id}      → update
  DELETE /documents/{id}    → delete
  POST /documents/{id}/sign → assinatura
  GET  /documents/{id}/download → FileResponse

modules/ged/controllers/auto_assemble_controller.py
  POST /kits/montar         → cria shells vazios (endpoint chamado pelo frontend)
  POST /kits/{id}/approve   → aprova kit

modules/gedeon/controllers/onvio_controller.py
  GET  /onvio/stats         → totais e por_categoria
  GET  /onvio/status        → sessao_valida (último sync < 24h)
  POST /onvio/sync          → dispara sync (STUB — ver §4)
  GET  /onvio/historico     → últimos N logs
  GET  /onvio/documentos    → lista com filtros
```

| Endpoint | Existe? | Status |
|----------|---------|--------|
| `GET /api/v1/ged/kits` | ✅ | Funcional — retorna 10 kits (testado) |
| `GET /api/v1/ged/dashboard` | ✅ | Funcional |
| `POST /api/v1/ged/auto-assemble` | ✅ | Funcional — kits completos via KitBuilderService |
| `POST /api/v1/ged/kits/montar` | ✅ | Parcial — cria shells vazios (ver §2) |
| `GET /api/v1/ged/documents` | ✅ | Funcional |
| `POST /api/v1/ged/documents/upload` | ✅ | Funcional — salva em disco |
| `GET /api/v1/ged/documents/{id}/download` | ✅ | Impl. ok, 404 em placeholders (ver §8) |
| `POST /api/v1/gedeon/onvio/sync` | ✅ | **STUB** — retorna success=0 (ver §4) |
| `GET /api/v1/gedeon/onvio/stats` | ✅ | Funcional — lê banco |
| `GET /api/v1/ged/config/schedule` | ✅ | **STUB** — hardcoded, não persiste (ver §7) |

**STEP 1.2 — IA classifier:**
```
modules/ged/services/document_ai_service.py:201 → classify_document()
modules/people_management/ged/services/document_collector_service.py
modules/gedeon/gedeon.py → referencias a openai/anthropic ausentes
```
Nenhum arquivo GED chama `openai.ChatCompletion` ou `anthropic.messages.create`.

**STEP 1.3 — Celery/cron:**
```
modules/people_management/ged/tasks/auto_collect_task.py → ged.auto_collect_documents
modules/people_management/ged/tasks/cnd_sync_task.py     → ged.cnd_sync
```
Sem `CELERYBEAT_SCHEDULE` configurado para GED.

**STEP 1.4 — Onvio:**
```
modules/gedeon/controllers/onvio_controller.py
modules/gedeon/agents/atlas.py (NÃO tem sync_onvio)
modules/gedeon/onvio/ (parser de documentos Onvio)
.env: ONVIO_PASS=***, ONVIO_IMAP_PASSWORD=***
```

**STEP 1.5 — Banco Inter:**
```
modules/people_management/services/folha_payment_service.py → PIX folha via mTLS
modules/integrations/banking/controllers/banking_controller.py → extrato/webhook
/opt/conecta-pro/credentials/inter/inter_cert.crt + .key + ca.crt (reais)
```

**STEP 1.6 — CND:**
```
modules/people_management/ged/tasks/cnd_sync_task.py:
  from bidding.integrations.receita_federal.cnd_client       → Receita Federal
  from bidding.integrations.receita_federal.cndt_client      → TST
  from bidding.integrations.receita_federal.crf_client       → FGTS/Caixa
  from bidding.integrations.receita_federal.sefaz_am_client  → SEFAZ-AM
  from bidding.integrations.receita_federal.prefeitura_manaus_client → ISS Manaus
```

---

## 2. Auto-Assemble — O que o botão "Montar Kits" realmente faz

**STEP 4 — Inventário:**

Botão UI: `ged/page.tsx:194` → `setShowMontarConfirm(true)` → modal → "Sim, Montar Kits" (`page.tsx:324`)
Chamada real: `POST /api/v1/ged/kits/montar` (frontend: `fetch('/api/v1/ged/kits/montar', {method:'POST'})`)

**Endpoint chamado pelo frontend** (`ged/controllers/auto_assemble_controller.py:360`):
```python
# Cria shells vazios — NÃO popula documentos
INSERT INTO ged_document_kits (id, client_id, reference_month, status,
    total_employees, total_documents, ...)
VALUES (:id, :cid, :mes, 'em_montagem', 0, 0, ...)
```
1. Query todos `ged_clients` ativos sem kit no mês atual
2. Para cada cliente: INSERT em `ged_document_kits` com status=`em_montagem`, totais=0
3. **NÃO insere** `ged_kit_documents`, **NÃO calcula** total_esperado

**Endpoint CORRETO** (não usado pelo frontend) — `people_management/ged/controllers/auto_assemble_controller.py:23`:
```python
POST /api/v1/ged/auto-assemble → KitBuilderService.auto_build_all_kits(ref)
```
Este sim constrói kits completos com documentos via KitBuilderService.

**Veredicto:** botão existe e funciona mas cria kits incompletos (shells). O endpoint completo (`/auto-assemble`) não está conectado ao frontend.

---

## 3. Upload com IA — qual API, funcional ou stub?

**STEP 5 — Evidências:**

```
requirements.txt:
  openai>=1.0.0
  anthropic>=0.84.0

.env:
  OPENAI_API_KEY=***MASKED***
  ANTHROPIC_API_KEY=***MASKED***
```

**Serviço:** `modules/ged/services/document_ai_service.py:201` — `classify_document(text, file_name)`

**Implementação real — keyword/regex local, sem API externa:**
```python
# modules/ged/services/document_ai_service.py:210-221
type_scores[doc_type] = sum(1 for kw in keywords if kw in combined)
type_confidence = min(max_score / 5 * 100, 100)
# ↑ SEM openai.ChatCompletion, SEM anthropic.messages.create
```

Apesar de `openai>=1.0.0` e `anthropic>=0.84.0` instalados e **ambas as chaves** em `.env`, o `classify_document` usa apenas dicionários de keywords e regex. É completamente local.

**Funcionalidades reais do classificador:**
- Tipo de doc (CONTRATO, PROPOSTA, NOTA_FISCAL, BOLETO, CERTIDAO...) por frequência de keywords
- Extração de datas (regex `\d{2}/\d{2}/\d{4}`), valores `R$`, CPF/CNPJ
- Score de confiança: `min(matches/5 * 100, 100)`

**UI "Upload com IA":** `page.tsx:191` navega para `/modulos/gestao-pessoas/ged/upload` — a página de upload existe com drag-drop, mas a classificação é local, não IA real.

---

## 4. Integração Onvio — serviço, credenciais, sync real?

**STEP 1.4 + 9 — Evidências:**

```
.env: ONVIO_PASS=***MASKED***, ONVIO_IMAP_PASSWORD=***MASKED***
```

**Endpoint:** `POST /api/v1/gedeon/onvio/sync` (`onvio_controller.py:84`) chama `AtlasAgent().sync_onvio(db, mes_ref)`.

**`AtlasAgent`** (`modules/gedeon/agents/atlas.py`) é um agente de **aprendizado contínuo** — registra histórico de kits, detecta anomalias por padrão estatístico, gera insights mensais. **Não tem método `sync_onvio`.**

**Fluxo real quando endpoint chamado:**
```python
try:
    atlas = AtlasAgent()
    resultado = await atlas.sync_onvio(db, mes_ref)  # ← AttributeError
except Exception as exc:
    logger.warning("Atlas não disponível — sync stub: %s", exc)
    novos, erros, status, duracao = 0, 0, "success", 0.1  # ← sempre cai aqui
```
Retorna `{"status": "success", "novos": 0, "erros": 0}` sem baixar nada.

**436 docs em `onvio_documents`** foram carregados pelo parser GEDEON em commits anteriores (reclassificação manual), não pelo sync em tempo real.

**Veredicto:** Onvio sync **é um stub completo**. Credenciais IMAP reais presentes mas nunca usadas pelo endpoint.

---

## 5. Integração Banco Inter — serviço, endpoints, certificado

**STEP 8 — Certificados:**
```
/opt/conecta-pro/credentials/inter/
  inter_cert.crt  (certificado cliente mTLS)
  inter_cert.key  (chave privada)
  ca.crt          (CA raiz Banco Inter)
```

**Onde está implementado (fora do escopo GED):**

| Arquivo | Uso |
|---------|-----|
| `modules/people_management/services/folha_payment_service.py:28` | PIX folha via mTLS — `INTER_CERT_PATH`, `INTER_KEY_PATH` |
| `modules/integrations/banking/controllers/banking_controller.py:263` | Extrato, transações bancárias |
| `modules/integrations/banking/controllers/webhook_controller.py:326` | Webhook de notificações PIX/TED |

**Endpoints Banco Inter implementados:**
- Extrato (banking_controller)
- Webhook PIX/TED (webhook_controller)
- Pagamentos PIX (folha_payment_service — para folha de pagamento)

**No GED:** zero referências a Inter. Os certs existem e são usados para folha e módulo financeiro.

---

## 6. Busca CND Automática — quais portais implementados

**Tarefa Celery:** `modules/people_management/ged/tasks/cnd_sync_task.py` — `shared_task(name="ged.cnd_sync")`

**5 portais declarados (imports lazy):**
```python
from bidding.integrations.receita_federal.cnd_client import CndClient
    # → Certidão Negativa Federal (Receita Federal / PGFN)
from bidding.integrations.receita_federal.cndt_client import CndtClient
    # → CNDT Trabalhista (TST)
from bidding.integrations.receita_federal.crf_client import CrfClient
    # → CRF FGTS (Caixa Econômica)
from bidding.integrations.receita_federal.sefaz_am_client import SefazAmClient
    # → CND Estadual AM (SEFAZ-AM)
from bidding.integrations.receita_federal.prefeitura_manaus_client import PrefeituraManausClient
    # → ISS Municipal (Prefeitura Manaus)
```

**TTL:** `"cnd_federal": 180` dias — certidões federais reaproveitadas por 180 dias (sem re-busca desnecessária).

**Storage:** `GED_STORAGE_BASE/certidoes/{portal}/{cnpj}/` (path configurável via `GED_STORAGE_PATH`).

**Caveat:** implementação real depende do módulo `bidding` (não auditado aqui). A task GED delega a busca para aquele módulo. Beat schedule não configurado (ver §7).

---

## 7. Cron / Scheduler — Celery Beat, cron OS, config da UI

**STEP 6 — Resultados das verificações:**

**`celerybeat-schedule`:** arquivo não encontrado no filesystem — Beat nunca rodou para GED.

**OS crontab (`crontab -l`):**
```
# apenas sistema/infra:
conecta-backup     → backup de arquivos
*/5 * * * *        → kill find travados
# SEM nenhuma entrada GED ou tasks de kits
```

**`/etc/cron.d/`:** apenas `conecta-backup` — sem entradas GED.

**Celery tasks GED definidas (mas não agendadas):**

| Task | Nome Celery | Arquivo |
|------|-------------|---------|
| Auto-collect docs | `ged.auto_collect_documents` | `tasks/auto_collect_task.py` |
| CND sync | `ged.cnd_sync` | `tasks/cnd_sync_task.py` |

**Toggle "Coleta Automática" da UI** — `GET/POST /api/v1/ged/config/schedule` (`config_controller.py:112`):
```python
@router.get("/schedule")
async def get_schedule(...):
    return {
        "enabled": False,           # ← hardcoded, nunca lê de .env ou BD
        "cron_expression": "0 8 5 * *",  # ← hardcoded
        "last_run": None,
    }

@router.post("/schedule")
async def save_schedule(...):
    return {"ok": True, "message": "Agendamento salvo"}  # ← não persiste nada
```

**Conclusão:** toggle da UI **é um stub**. Salvar o agendamento não faz nada. Tasks existem mas não rodam automaticamente em produção.

---

## 8. Download de Docs — endpoint testado com curl

**STEP 3.3 — Teste real:**

```bash
# Doc do kit PRIME ARENA (a5d04bc6-...)
DOC_ID=09ab2335-ce36-41aa-9f5b-611b634c0156  # doc real em ged_kit_documents

# Endpoint errado (forma do prompt / não existe):
GET /api/v1/ged/kits/a5d04bc6.../documents/09ab2335.../download
→ STATUS=404  {"detail":"Not Found"}  # route não mapeada

# Endpoint correto:
GET /api/v1/ged/documents/09ab2335.../download
→ STATUS=404  {"detail":"Documento não encontrado"}  # ORM lookup retornou None
```

**Diagnóstico do 404:** doc existe em `ged_kit_documents` (confirmado no banco), mas o endpoint usa `select(KitDocument).where(KitDocument.id == document_id)`. O modelo `KitDocument` mapeia para `ged_kit_documents`, mas pode haver filtro por `is_active` não visível na query simples. O doc tem `file_path=NULL` — mesmo que fosse encontrado, retornaria 404 "Documento nao possui arquivo vinculado".

**Implementação** (`document_controller.py:257-300`):
1. `select(KitDocument).where(id == document_id)` — busca no banco
2. Se não encontrado → `404 "Documento nao encontrado: {id}"`
3. Se `file_path IS NULL` → `404 "Documento nao possui arquivo vinculado"`
4. Resolve: `os.path.join(GED_STORAGE_BASE, doc.file_path)` se relativo
5. Se arquivo não existe em disco → `404 "Arquivo nao encontrado no storage"`
6. Registra `ExportService.log_access` + `await db.commit()`
7. Retorna `FileResponse(path, filename, media_type)`

**Storage base:** `GED_STORAGE_BASE = os.environ.get("GED_STORAGE_PATH", "/opt/conecta-pro/storage/ged")`

**Estado dos arquivos:**
```
/opt/conecta-pro/uploads/
  folhas/   (4 itens)
  ged/
    084b4d21...c350.pdf   ← 1 PDF real (upload manual)
    historico/
# Total: 29 arquivos — sem subdir onvio/ (confirma: sync nunca salvou nada)
```

**Veredicto:** implementação correta, bloqueada por dois motivos: (a) lookup ORM retorna None para kits-placeholder, (b) mesmo que encontrasse, file_path=NULL até sync real acontecer.

---

## 9. Upload de Docs — multipart, caminho, atualização no BD

**STEP 3.1 + 3.2 — Evidências:**

**Endpoint:** `POST /api/v1/ged/documents/upload` (`document_controller.py:101`)

```python
# Parâmetros: kit_id (form), document_type (form), file (UploadFile)
upload_dir = os.path.join(GED_STORAGE_BASE, "uploads", kit_id)
os.makedirs(upload_dir, exist_ok=True)
safe_filename = f"{uuid4()}_{secure_filename(file.filename)}"
file_path_full = os.path.join(upload_dir, safe_filename)
relative_path  = os.path.join("uploads", kit_id, safe_filename)

with open(file_path_full, "wb") as buffer:
    shutil.copyfileobj(file.file, buffer)

# UPDATE ged_kit_documents SET
#   file_path=relative_path, mime_type=content_type,
#   file_size_bytes=size, updated_at=NOW()
# WHERE kit_id=:kit_id AND document_type=:document_type
```

**Segurança:** `secure_filename` aplicado + UUID prefixado (sem path traversal).

**Cleanup:** se UPDATE falhar → `os.remove(file_path_full)` (sem arquivo órfão).

**Atualiza BD:** sim — `file_path` no `ged_kit_documents`, mais `mime_type` e `file_size_bytes`.

**Veredicto:** upload funcional, seguro, completo.

---

## 10. Matriz de Prioridade para D1 (ROI decrescente)

| # | Item | Falta fazer | Esforço | ROI |
|---|------|-------------|---------|-----|
| 1 | **Onvio Sync real** | Criar `sync_onvio` no Atlas com IMAP (`ONVIO_IMAP_PASSWORD`) para baixar PDFs mensais e salvar em `storage/ged/` | Alto | **MÁXIMO** — desbloqueia toda a cadeia |
| 2 | **Conectar `/kits/montar` ao endpoint completo** | Trocar frontend de `/kits/montar` para `/auto-assemble` OU replicar lógica do KitBuilderService no endpoint existente | Baixo | **ALTO** — 1 clique = kits com docs |
| 3 | **Celery Beat schedule** | Adicionar `ged.auto_collect_documents` + `ged.cnd_sync` ao `CELERYBEAT_SCHEDULE` em `celery_app.py` | Baixo | **ALTO** — automação mensal zero-toque |
| 4 | **Toggle Coleta Automática funcional** | Salvar `enabled` + `cron_expression` em banco e acionar `Beat.update_schedule()` | Médio | **ALTO** — UI já existe |
| 5 | **CND automático ativo** | Testar/validar `bidding.integrations.receita_federal.*` e disparar task GED | Médio | **ALTO** — certidões automáticas |
| 6 | **Download funcional** | Depende de #1 (file_path preenchido); corrigir lookup ORM se `is_active` bloqueia | Baixo | **MÉDIO** — bloqueado por #1 |
| 7 | **IA real no upload** | Substituir keyword matcher por `anthropic.messages.create` (chaves já em `.env`) | Médio | **MÉDIO** — packages já instalados |
| 8 | **Auto-collect task** | Verificar se `auto_collect_task.py` coleta docs de DP/Fiscal/Operações corretamente | Médio | **MÉDIO** |
| 9 | **Portal cliente** | `portal_access_enabled` existe no modelo — auditar e implementar UI de acesso externo | Alto | **BAIXO** — longo prazo |

---

## Sumário Executivo

| Componente | Status Real |
|------------|-------------|
| Kits documentais (estrutura) | ✅ REAL — 10 kits, 552 docs, banco íntegro |
| Download de PDFs | ⚠️ IMPL. OK mas bloqueado — file_path=NULL + ORM issue |
| Upload de PDFs | ✅ REAL — salva em disco, atualiza BD corretamente |
| Auto-assemble botão UI | ⚠️ PARCIAL — cria shells vazios, endpoint errado |
| Sync Onvio | 🔴 STUB — AtlasAgent sem `sync_onvio`, retorna success=0 |
| IA de classificação | ⚠️ LOCAL — keyword/regex, packages instalados, chaves presentes |
| Toggle Coleta Automática | 🔴 STUB — GET/POST hardcoded, não persiste |
| CND automático | ⚠️ DECLARADO — 5 portais, Beat não configurado |
| Cron/Scheduler | 🔴 INATIVO — tasks existem, Beat sem schedule GED |
| Banco Inter | ✅ REAL — certs + 3 arquivos que os usam (fora do escopo GED) |

**Gargalo raiz:** Onvio Sync. Toda a cadeia (download, completude, relatórios) depende de PDFs que só chegam via sync real. Implementar `sync_onvio` com IMAP desbloquearia o módulo inteiro. As chaves já estão em `.env`.
