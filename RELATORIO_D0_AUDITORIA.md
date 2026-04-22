# RELATÓRIO D0 — Auditoria Read-Only GEDEON
**Data:** 2026-04-22
**Branch:** feature/people-management-reorganization
**Auditor:** Claude Code (Sonnet 4.6) — sessão read-only, sem modificações
**Mandato:** mapear o que está implementado de verdade vs. visual de UI

---

## 1. Endpoints Mapeados

| Endpoint | Existe? | Arquivo | Status |
|----------|---------|---------|--------|
| `GET /api/v1/ged/kits` | ✅ | `people_management/ged/controllers/auto_assemble_controller.py:47` | Funcional — retorna 10 kits |
| `GET /api/v1/ged/dashboard` | ✅ | `people_management/ged/controllers/auto_assemble_controller.py:101` | Funcional |
| `POST /api/v1/ged/auto-assemble` | ✅ | `people_management/ged/controllers/auto_assemble_controller.py:23` | Funcional — chama `KitBuilderService.auto_build_all_kits()` |
| `POST /api/v1/ged/kits/montar` | ✅ | `ged/controllers/auto_assemble_controller.py:360` | Funcional — cria shells vazios (ver §2) |
| `GET /api/v1/ged/documents` | ✅ | `people_management/ged/controllers/document_controller.py:39` | Funcional |
| `POST /api/v1/ged/documents/upload` | ✅ | `people_management/ged/controllers/document_controller.py:101` | Funcional — salva arquivo em disco |
| `GET /api/v1/ged/documents/{id}` | ✅ | `people_management/ged/controllers/document_controller.py:173` | Funcional |
| `PUT /api/v1/ged/documents/{id}` | ✅ | `people_management/ged/controllers/document_controller.py:187` | Funcional |
| `DELETE /api/v1/ged/documents/{id}` | ✅ | `people_management/ged/controllers/document_controller.py:212` | Funcional |
| `POST /api/v1/ged/documents/{id}/sign` | ✅ | `people_management/ged/controllers/document_controller.py:228` | Funcional |
| `GET /api/v1/ged/documents/{id}/download` | ✅ | `people_management/ged/controllers/document_controller.py:257` | Funcional — FileResponse (ver §8) |
| `POST /api/v1/ged/historico` | ✅ | `people_management/ged/controllers/document_controller.py:344` | Funcional |
| `GET /api/v1/ged/historico/status` | ✅ | `people_management/ged/controllers/document_controller.py:368` | Funcional |
| `GET /api/v1/gedeon/onvio/stats` | ✅ | `gedeon/controllers/onvio_controller.py:33` | Funcional — lê banco |
| `GET /api/v1/gedeon/onvio/status` | ✅ | `gedeon/controllers/onvio_controller.py:55` | Funcional — lê banco |
| `POST /api/v1/gedeon/onvio/sync` | ✅ | `gedeon/controllers/onvio_controller.py:84` | **STUB** (ver §4) |
| `GET /api/v1/gedeon/onvio/historico` | ✅ | `gedeon/controllers/onvio_controller.py:138` | Funcional |
| `GET /api/v1/gedeon/onvio/documentos` | ✅ | `gedeon/controllers/onvio_controller.py:164` | Funcional |

**Teste ao vivo (2026-04-22):**
```
GET /api/v1/ged/kits?page_size=1 → HTTP 200
10 kits retornados, todos status=em_montagem, reference_month=2026-04-01
```

---

## 2. Auto-Assemble — O que o botão realmente faz

**Botão UI:** "Montar Kits" (`ged/page.tsx:194`) → `setShowMontarConfirm(true)` → modal → "Sim, Montar Kits" (`page.tsx:324`).

**Chamada real:** `POST /api/v1/ged/kits/montar` (`ged/controllers/auto_assemble_controller.py:360`)

**O que acontece:**
1. Query: todos os `ged_clients` ativos sem kit no mês atual
2. Para cada cliente: `INSERT INTO ged_document_kits` com `status='em_montagem'`, `total_employees=0`, `total_documents=0`
3. Retorna lista de kits criados

**Limitação crítica:** cria apenas shells vazios sem documentos. NÃO calcula total_esperado, NÃO insere `ged_kit_documents`, NÃO aciona `KitBuilderService`.

**Contraste:** `POST /api/v1/ged/auto-assemble` (`people_management/ged/controllers/auto_assemble_controller.py:23`) chama `KitBuilderService.auto_build_all_kits()` que constrói kits completos com documentos — mas NÃO é o endpoint chamado pelo frontend.

**Veredicto:** botão funciona mas cria kits incompletos. O endpoint certo (`/auto-assemble`) existe mas não está conectado ao frontend.

---

## 3. Upload com IA — qual API, funcional ou stub?

**Botão UI:** "Upload com IA" (`ged/page.tsx:191`) → navega para `/modulos/gestao-pessoas/ged/upload`.

**Serviço IA:** `modules/ged/services/document_ai_service.py:201` — método `classify_document(text, file_name)`

**Implementação real:**
```python
# NÃO chama OpenAI nem Anthropic
# É classificação por contagem de keywords em dicionários
type_scores[doc_type] = sum(1 for kw in keywords if kw in combined)
type_confidence = min(max_score / 5 * 100, 100)
```

**Conclusão:** `classify_document` é **regex/keyword local** — sem chamada de API externa. Apesar de `openai` e `anthropic` estarem instalados e as chaves em `.env`, este serviço não os usa. A IA de classificação de documentos GED é local e determinística.

**Funcionalidades reais:**
- Classificação por tipo (CONTRATO, PROPOSTA, NOTA_FISCAL, etc.) via keywords
- Extração de datas, valores monetários (R$), CPF/CNPJ via regex
- Score de confiança calculado por contagem de matches

---

## 4. Integração Onvio — serviço, credenciais, sync real?

**Credenciais:** `.env` contém `ONVIO_PASS` e `ONVIO_IMAP_PASSWORD` — credenciais reais presentes.

**Endpoint sync:** `POST /api/v1/gedeon/onvio/sync` → chama `AtlasAgent().sync_onvio(db, mes_ref)`.

**Problema:** `AtlasAgent` (arquivo `modules/gedeon/agents/atlas.py`) é um agente de **aprendizado contínuo** — registra histórico de kits, detecta anomalias, gera insights. Ele **NÃO tem método `sync_onvio`**.

**Fluxo real quando o endpoint é chamado:**
```python
try:
    atlas = AtlasAgent()
    resultado = await atlas.sync_onvio(db, mes_ref)  # ← AttributeError aqui
except Exception as exc:
    logger.warning("Atlas não disponível — sync stub: %s", exc)
    novos, erros, status, duracao = 0, 0, "success", 0.1  # ← cai aqui
```

**Resultado:** o sync retorna `{"status": "success", "novos": 0}` sem fazer nada. Registra um log de "success" no banco, mas zero documentos são baixados.

**436 docs existentes** em `onvio_documents` foram carregados pelo parser GEDEON (commits anteriores), NÃO pelo sync em tempo real.

**Veredicto:** Onvio sync **é um stub**. IMAP e Playwright para baixar documentos não estão implementados no fluxo do endpoint.

---

## 5. Integração Banco Inter — serviço, endpoints, certificado

**Certificados:** arquivos reais presentes em `/opt/conecta-pro/credentials/inter/`:
- `inter_cert.crt` — certificado cliente
- `inter_cert.key` — chave privada
- `ca.crt` — CA raiz

**Uso no GED:** nenhum. O módulo `people_management/ged/` não faz referência a `inter`, `BancoInter` ou pagamentos.

**Onde está implementado:** `modules/financial/` (fora do escopo GED). Os certs existem para o módulo financeiro (PIX lote, boletos), não para o GED.

**Veredicto:** certificados reais presentes mas não utilizados pelo GED. Fora do escopo desta auditoria.

---

## 6. Busca CND Automática — quais portais implementados

**Tarefa Celery:** `modules/people_management/ged/tasks/cnd_sync_task.py` — `shared_task(name="ged.cnd_sync")`

**Clientes implementados (imports lazy):**
```python
from bidding.integrations.receita_federal.cnd_client import CndClient        # CND Federal (Receita)
from bidding.integrations.receita_federal.cndt_client import CndtClient       # CNDT Trabalhista (TST)
from bidding.integrations.receita_federal.crf_client import CrfClient         # CRF (FGTS/Caixa)
from bidding.integrations.receita_federal.sefaz_am_client import SefazAmClient # CND Estadual AM
from bidding.integrations.receita_federal.prefeitura_manaus_client import PrefeituraManausClient # ISS Manaus
```

**5 portais declarados:** Receita Federal, TST, FGTS/Caixa, SEFAZ-AM, Prefeitura Manaus.

**TTL configurado:** `"cnd_federal": 180` dias — certidões federais são reaproveitadas por 180 dias.

**Storage:** `GED_STORAGE_BASE/certidoes/{portal}/{cnpj}/` via raw SQL na task.

**Caveat:** os clientes são importados lazy do módulo `bidding` — a qualidade da implementação depende daquele módulo (não auditado aqui). A task GED encapsula a chamada mas não a implementa do zero.

---

## 7. Cron/Scheduler — Celery Beat, cron OS, onde está a config

**Celery tasks GED definidas:**

| Task | Nome | Arquivo |
|------|------|---------|
| Auto-collect docs | `ged.auto_collect_documents` | `people_management/ged/tasks/auto_collect_task.py` |
| CND sync | `ged.cnd_sync` | `people_management/ged/tasks/cnd_sync_task.py` |

**Celery Beat:** não foi encontrada configuração de schedule para as tasks GED em `CELERYBEAT_SCHEDULE` ou `beat_schedule`. Workers Celery existem (7 workers definidos em `docker-compose`) mas o Beat schedule para GED não está configurado.

**OS crontab:** nenhuma entrada para GED ou tasks de kits.

**Conclusão:** tasks existem e podem ser disparadas manualmente via `celery call ged.auto_collect_documents`, mas não rodam automaticamente em produção. O scheduler mensal documentado em CONTRACTS_GEDEON.md §37.x não está ativo.

---

## 8. Download de Docs — endpoint testado

**Endpoint:** `GET /api/v1/ged/documents/{document_id}/download`

**Implementação** (`document_controller.py:257`):
1. Busca `KitDocument` por `document_id`
2. Se `file_path IS NULL` → 404 "Documento nao possui arquivo vinculado"
3. Resolve path: `os.path.join(GED_STORAGE_BASE, doc.file_path)` se relativo
4. Se arquivo não existe em disco → 404
5. Registra log de acesso (`ExportService.log_access`)
6. Retorna `FileResponse(path, filename, media_type)`

**Storage base:** `GED_STORAGE_BASE = os.environ.get("GED_STORAGE_PATH", "/opt/conecta-pro/storage/ged")`

**Estado atual:** todos os 552 docs do BLOCO C têm `file_path=NULL` — qualquer download tentado retornará 404. Isso é esperado: kits 04/2026 são placeholders aguardando sync Onvio.

**Funciona quando há PDF:** a implementação está correta — quando `file_path` for preenchido (após sync real), o download funcionará.

---

## 9. Upload de Docs — multipart, caminho, atualização no BD

**Endpoint:** `POST /api/v1/ged/documents/upload` (`document_controller.py:101`)

**Parâmetros:** `kit_id` (form), `document_type` (form), `file` (UploadFile)

**Fluxo:**
```python
upload_dir = os.path.join(GED_STORAGE_BASE, "uploads", kit_id)
os.makedirs(upload_dir, exist_ok=True)
safe_filename = f"{uuid4()}_{secure_filename(file.filename)}"
file_path_full = os.path.join(upload_dir, safe_filename)
relative_path = os.path.join("uploads", kit_id, safe_filename)

with open(file_path_full, "wb") as buffer:
    shutil.copyfileobj(file.file, buffer)

# UPDATE ged_kit_documents SET file_path=relative_path, mime_type=..., file_size_bytes=...
```

**Segurança:** `secure_filename` aplicado + UUID prefixado — sem path traversal.

**Cleanup:** se UPDATE falhar, o arquivo em disco é removido (bloco try/except).

**Estado do storage:** `/opt/conecta-pro/storage/ged/` contém 29 arquivos. Subdir `ged/` presente. Nenhum `onvio/` (confirma que sync Onvio nunca salvou nada).

**Veredicto:** upload funcional e seguro.

---

## 10. Matriz de Prioridade (ROI decrescente)

| # | Item | O que está faltando | Impacto | Esforço | ROI |
|---|------|---------------------|---------|---------|-----|
| 1 | **Onvio Sync real** | Implementar `AtlasAgent.sync_onvio` com IMAP/Playwright para baixar PDFs mensais | Desbloqueia 436+ docs existentes + futuros meses | Alto | **MÁXIMO** |
| 2 | **Conectar `/kits/montar` ao KitBuilderService** | Frontend chama endpoint errado; trocar para `/auto-assemble` ou equiparar lógica | Kits completos com 1 clique em vez de shells vazios | Baixo | **ALTO** |
| 3 | **Celery Beat schedule** | Adicionar `ged.auto_collect_documents` e `ged.cnd_sync` ao `CELERYBEAT_SCHEDULE` | Automação mensal sem intervenção humana | Baixo | **ALTO** |
| 4 | **CND automático ativo** | Validar que `bidding.integrations.receita_federal.*` está funcional e disparar task | Certidões nos kits sem trabalho manual | Médio | **ALTO** |
| 5 | **Download desbloqueado** | Após item #1, os 552 placeholders terão `file_path` preenchido | Clientes poderão baixar documentos | Depende de #1 | **MÉDIO** |
| 6 | **IA real no upload** | Substituir keyword matcher por chamada `anthropic.messages.create` para classificar PDF | Classificação mais precisa | Médio | **MÉDIO** |
| 7 | **Auto-collect task funcional** | Verificar se `auto_collect_task.py` consegue coletar docs de DP/Fiscal/Operações | Popula kits automaticamente pós-sync | Médio | **MÉDIO** |
| 8 | **Portal cliente** | `portal_access_enabled` existe no modelo mas UI de portal não foi auditada | Acesso externo para condomínios | Alto | **BAIXO** |
| 9 | **Banco Inter no GED** | Não aplicável ao GED — integração existe no financeiro | Sem impacto direto no GED | — | **N/A** |

---

## Sumário Executivo

| Componente | Status Real |
|------------|-------------|
| Kits documentais (estrutura) | ✅ REAL — 10 kits, 552 docs, banco íntegro |
| Download de PDFs | ⚠️ REAL mas bloqueado — impl. ok, file_path=NULL |
| Upload de PDFs | ✅ REAL — salva em disco, atualiza BD |
| Auto-assemble (botão UI) | ⚠️ PARCIAL — cria shells vazios, não popula docs |
| Sync Onvio | 🔴 STUB — `sync_onvio` não existe no Atlas, retorna 0 |
| IA de classificação | ⚠️ LOCAL — keyword/regex, sem OpenAI/Anthropic |
| CND automático | ⚠️ DECLARADO — task existe, Beat não configurado |
| Cron/Scheduler | 🔴 INATIVO — tasks existem, sem Beat schedule |
| Banco Inter | ✅ CERTS REAIS — fora do escopo GED |

**Gargalo principal:** Onvio Sync. Toda a cadeia (download, completude de kits, relatórios) depende de PDFs que só chegam via sync real. Implementar `AtlasAgent.sync_onvio` com IMAP desbloquearia o módulo inteiro.
